"""
FileValidationService

Validates uploaded files without relying on libmagic.
Uses file signatures (magic bytes) and content inspection to determine
the actual file type instead of trusting the filename extension.
"""

import os
from dataclasses import dataclass
from pathlib import Path


MAX_FILENAME_LEN = 255


SUPPORTED_TYPES = {
    "image": {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/bmp",
        "image/tiff",
    },
    "video": {
        "video/mp4",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-matroska",
        "video/webm",
    },
    "audio": {
        "audio/wav",
        "audio/x-wav",
        "audio/mpeg",
        "audio/mp4",
        "audio/aac",
        "audio/flac",
        "audio/ogg",
    },
    "pdf": {
        "application/pdf",
    },
    "docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    },
    "text": {
        "text/plain",
        "text/rtf",
        "application/rtf",
    },
}


@dataclass
class ValidationResult:
    ok: bool
    category: str
    detected_mime: str
    declared_mime: str
    mismatch: bool
    message: str


def sanitize_filename(filename: str) -> str:
    """
    Remove path components and potentially dangerous characters.
    Prevents path traversal attacks.
    """

    if not filename:
        return "unnamed_file"

    # Normalize Windows/Unix path separators
    filename = filename.replace("\\", "/")

    # Remove directory components
    base = os.path.basename(filename)

    # Prevent path traversal
    base = base.replace("..", "_")

    # Keep only safe characters
    safe = "".join(
        c for c in base
        if c.isalnum() or c in "._- "
    )

    safe = safe.strip()

    return safe[:MAX_FILENAME_LEN] or "unnamed_file"


def categorize(detected_mime: str) -> str:
    """
    Convert MIME type into an application category.
    """

    for category, mimes in SUPPORTED_TYPES.items():
        if detected_mime in mimes:
            return category

    return "unsupported"


def _read_header(path: str, size: int = 64) -> bytes:
    """
    Read the first bytes of a file.
    """

    with open(path, "rb") as file:
        return file.read(size)


def _detect_mime_from_signature(path: str) -> str:
    """
    Detect MIME type using file signatures/magic bytes.

    This implementation does not require libmagic and therefore
    works properly on Windows.
    """

    try:
        header = _read_header(path, 128)
    except (OSError, IOError):
        return "application/octet-stream"

    # ---------------------------------------------------------
    # PDF
    # ---------------------------------------------------------

    if header.startswith(b"%PDF-"):
        return "application/pdf"

    # ---------------------------------------------------------
    # JPEG
    # ---------------------------------------------------------

    if header.startswith(b"\xFF\xD8\xFF"):
        return "image/jpeg"

    # ---------------------------------------------------------
    # PNG
    # ---------------------------------------------------------

    if header.startswith(
        b"\x89PNG\r\n\x1a\n"
    ):
        return "image/png"

    # ---------------------------------------------------------
    # GIF
    # Not currently supported, but correctly identified.
    # ---------------------------------------------------------

    if header.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"

    # ---------------------------------------------------------
    # WEBP
    # RIFF....WEBP
    # ---------------------------------------------------------

    if (
        len(header) >= 12
        and header[0:4] == b"RIFF"
        and header[8:12] == b"WEBP"
    ):
        return "image/webp"

    # ---------------------------------------------------------
    # BMP
    # ---------------------------------------------------------

    if header.startswith(b"BM"):
        return "image/bmp"

    # ---------------------------------------------------------
    # TIFF
    # ---------------------------------------------------------

    if header.startswith((b"II*\x00", b"MM\x00*")):
        return "image/tiff"

    # ---------------------------------------------------------
    # WAV
    # RIFF....WAVE
    # ---------------------------------------------------------

    if (
        len(header) >= 12
        and header[0:4] == b"RIFF"
        and header[8:12] == b"WAVE"
    ):
        return "audio/wav"

    # ---------------------------------------------------------
    # AVI
    # RIFF....AVI
    # ---------------------------------------------------------

    if (
        len(header) >= 12
        and header[0:4] == b"RIFF"
        and header[8:12] == b"AVI "
    ):
        return "video/x-msvideo"

    # ---------------------------------------------------------
    # MP4 / MOV
    #
    # ISO Base Media File Format uses an "ftyp" box.
    # ---------------------------------------------------------

    if len(header) >= 12 and header[4:8] == b"ftyp":

        brand = header[8:12]

        mp4_brands = {
            b"isom",
            b"iso2",
            b"iso3",
            b"iso4",
            b"iso5",
            b"iso6",
            b"mp41",
            b"mp42",
            b"avc1",
            b"M4V ",
            b"MSNV",
        }

        mov_brands = {
            b"qt  ",
        }

        if brand in mp4_brands:
            return "video/mp4"

        if brand in mov_brands:
            return "video/quicktime"

        # Many MP4-compatible files use other brands.
        return "video/mp4"

    # ---------------------------------------------------------
    # MKV / WebM
    # EBML signature
    # ---------------------------------------------------------

    if header.startswith(b"\x1A\x45\xDF\xA3"):

        # WebM normally contains "webm" later in the EBML data.
        if b"webm" in header.lower():
            return "video/webm"

        return "video/x-matroska"

    # ---------------------------------------------------------
    # FLAC
    # ---------------------------------------------------------

    if header.startswith(b"fLaC"):
        return "audio/flac"

    # ---------------------------------------------------------
    # OGG
    # ---------------------------------------------------------

    if header.startswith(b"OggS"):
        return "audio/ogg"

    # ---------------------------------------------------------
    # MP3
    # ---------------------------------------------------------

    if header.startswith(b"ID3"):
        return "audio/mpeg"

    # MP3 frames can begin with FF FB / FF F3 / FF F2
    if len(header) >= 2:
        if header[0] == 0xFF and header[1] in {
            0xFB,
            0xF3,
            0xF2,
        }:
            return "audio/mpeg"

    # ---------------------------------------------------------
    # DOCX
    #
    # DOCX is a ZIP archive containing:
    # [Content_Types].xml
    # word/document.xml
    # ---------------------------------------------------------

    if header.startswith(b"PK\x03\x04"):

        try:
            import zipfile

            with zipfile.ZipFile(path, "r") as archive:

                names = set(archive.namelist())

                if (
                    "[Content_Types].xml" in names
                    and any(
                        name.startswith("word/")
                        for name in names
                    )
                ):
                    return (
                        "application/"
                        "vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    )

        except (
            zipfile.BadZipFile,
            OSError,
            IOError,
        ):
            pass

    # ---------------------------------------------------------
    # Legacy DOC
    #
    # Microsoft Compound File Binary Format.
    # ---------------------------------------------------------

    if header.startswith(
        b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"
    ):
        return "application/msword"

    # ---------------------------------------------------------
    # Plain text / RTF
    # ---------------------------------------------------------

    if header.startswith(b"{\\rtf"):
        return "application/rtf"

    try:
        decoded = header.decode(
            "utf-8",
            errors="strict",
        )

        # If the beginning is valid UTF-8 and contains no
        # binary control characters, treat it as text.
        if decoded:

            has_binary_control = any(
                ord(char) < 9
                for char in decoded
            )

            if not has_binary_control:
                return "text/plain"

    except UnicodeDecodeError:
        pass

    return "application/octet-stream"


def validate_file(
    path: str,
    declared_mime: str,
    max_size: int,
) -> ValidationResult:

    # ---------------------------------------------------------
    # Check existence
    # ---------------------------------------------------------

    if not os.path.exists(path):
        return ValidationResult(
            False,
            "unsupported",
            "",
            declared_mime,
            False,
            "File does not exist.",
        )

    # ---------------------------------------------------------
    # Check file
    # ---------------------------------------------------------

    if not os.path.isfile(path):
        return ValidationResult(
            False,
            "unsupported",
            "",
            declared_mime,
            False,
            "Uploaded path is not a regular file.",
        )

    # ---------------------------------------------------------
    # Check size
    # ---------------------------------------------------------

    try:
        size = os.path.getsize(path)
    except OSError:
        return ValidationResult(
            False,
            "unsupported",
            "",
            declared_mime,
            False,
            "Unable to read file information.",
        )

    if size == 0:
        return ValidationResult(
            False,
            "unsupported",
            "",
            declared_mime,
            False,
            "File is empty.",
        )

    if size > max_size:
        return ValidationResult(
            False,
            "unsupported",
            "",
            declared_mime,
            False,
            "File exceeds the maximum allowed size.",
        )

    # ---------------------------------------------------------
    # Detect actual MIME type
    # ---------------------------------------------------------

    detected_mime = _detect_mime_from_signature(path)

    # ---------------------------------------------------------
    # Categorize
    # ---------------------------------------------------------

    category = categorize(detected_mime)

    # ---------------------------------------------------------
    # Compare browser-declared MIME with actual MIME
    # ---------------------------------------------------------

    mismatch = (
        bool(declared_mime)
        and declared_mime != detected_mime
        and category != "unsupported"
    )

    # ---------------------------------------------------------
    # Unsupported
    # ---------------------------------------------------------

    if category == "unsupported":
        return ValidationResult(
            False,
            "unsupported",
            detected_mime,
            declared_mime,
            mismatch,
            "File type currently unsupported.",
        )

    # ---------------------------------------------------------
    # Successful validation
    # ---------------------------------------------------------

    message = "File validated successfully."

    if mismatch:
        message = (
            "Declared file type does not match the file's "
            "actual signature. Proceeding with analysis "
            "based on detected content type."
        )

    return ValidationResult(
        True,
        category,
        detected_mime,
        declared_mime,
        mismatch,
        message,
    )