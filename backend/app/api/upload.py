import os
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.config import settings
from app.services.file_validation import validate_file, sanitize_filename
from app.services.hashing import sha256_of_file
from app.models.file import FileRecord
from app.api.deps import get_current_user
from app.models.user import User


router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dest_path = None

    try:
        # ---------------------------------------------------------
        # 1. Validate filename
        # ---------------------------------------------------------
        safe_name = sanitize_filename(file.filename or "unnamed_file")

        if not safe_name:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename."
            )

        # ---------------------------------------------------------
        # 2. Create upload directory if it doesn't exist
        # ---------------------------------------------------------
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        # ---------------------------------------------------------
        # 3. Generate unique stored filename
        # ---------------------------------------------------------
        stored_name = f"{uuid.uuid4().hex}_{safe_name}"
        dest_path = os.path.join(settings.UPLOAD_DIR, stored_name)

        # ---------------------------------------------------------
        # 4. Save uploaded file
        # ---------------------------------------------------------
        size = 0

        with open(dest_path, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                size += len(chunk)

                # Maximum file size check
                if size > settings.MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File exceeds the maximum allowed size."
                    )

                out.write(chunk)

        # ---------------------------------------------------------
        # 5. Validate actual file type / MIME
        # ---------------------------------------------------------
        result = validate_file(
            dest_path,
            file.content_type or "",
            settings.MAX_FILE_SIZE
        )

        if not result.ok:
            raise HTTPException(
                status_code=400,
                detail=result.message
            )

        # ---------------------------------------------------------
        # 6. Calculate SHA-256 hash
        # ---------------------------------------------------------
        file_hash = sha256_of_file(dest_path)

        # ---------------------------------------------------------
        # 7. Store file information in Neon PostgreSQL
        # ---------------------------------------------------------
        record = FileRecord(
            user_id=user.id,
            original_filename=safe_name,
            stored_filename=stored_name,
            mime_type=file.content_type or "",
            detected_mime_type=result.detected_mime,
            file_size=size,
            sha256=file_hash,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        # ---------------------------------------------------------
        # 8. Return upload result
        # ---------------------------------------------------------
        return {
            "success": True,
            "file_id": record.id,
            "filename": record.original_filename,
            "category": result.category,
            "detected_mime_type": result.detected_mime,
            "declared_mime_type": result.declared_mime,
            "mime_mismatch": result.mismatch,
            "size": size,
            "sha256": file_hash,
            "message": result.message,
        }

    except HTTPException:
        # Remove partially uploaded file
        if dest_path and os.path.exists(dest_path):
            try:
                os.remove(dest_path)
            except OSError:
                pass

        db.rollback()
        raise

    except Exception as e:
        # Remove uploaded file if database/validation/etc. fails
        if dest_path and os.path.exists(dest_path):
            try:
                os.remove(dest_path)
            except OSError:
                pass

        db.rollback()

        # Print actual error in backend terminal
        print(f"[UPLOAD ERROR] {type(e).__name__}: {e}")

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        )

    finally:
        await file.close()


@router.delete("/{file_id}")
def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    record = (
        db.query(FileRecord)
        .filter(
            FileRecord.id == file_id,
            FileRecord.user_id == user.id
        )
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    path = os.path.join(
        settings.UPLOAD_DIR,
        record.stored_filename
    )

    try:
        if os.path.exists(path):
            os.remove(path)

        db.delete(record)
        db.commit()

        return {
            "success": True,
            "message": "File deleted successfully."
        }

    except Exception as e:
        db.rollback()

        print(f"[DELETE ERROR] {type(e).__name__}: {e}")

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while deleting the file."
        )