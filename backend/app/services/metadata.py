"""Generic + type-specific metadata extraction, spec sections 9/22/25."""
from PIL import Image
from PIL.ExifTags import TAGS

SUSPICIOUS_SOFTWARE_KEYWORDS = [
    "photoshop", "gimp", "canva", "midjourney", "dall-e", "dalle", "stable diffusion",
    "imagemagick", "affinity", "lightroom", "snapseed", "picsart", "facetune",
]


def extract_image_metadata(path: str) -> dict:
    result = {
        "width": None, "height": None, "format": None, "mode": None,
        "camera_make": None, "camera_model": None, "datetime": None,
        "software": None, "gps_present": False, "suspicious_software": False,
        "exif_present": False,
    }
    try:
        with Image.open(path) as img:
            result["width"], result["height"] = img.size
            result["format"] = img.format
            result["mode"] = img.mode
            exif = img.getexif()
            if exif:
                result["exif_present"] = True
                tagged = {TAGS.get(k, k): v for k, v in exif.items()}
                result["camera_make"] = tagged.get("Make")
                result["camera_model"] = tagged.get("Model")
                result["datetime"] = str(tagged.get("DateTime")) if tagged.get("DateTime") else None
                software = tagged.get("Software")
                result["software"] = software
                if software and any(k in str(software).lower() for k in SUSPICIOUS_SOFTWARE_KEYWORDS):
                    result["suspicious_software"] = True
                result["gps_present"] = "GPSInfo" in tagged
    except Exception as e:
        result["error"] = str(e)
    return result
