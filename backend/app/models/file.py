import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from app.database.database import Base


def gen_id():
    return str(uuid.uuid4())


class FileRecord(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    detected_mime_type = Column(String, nullable=True)
    file_size = Column(Integer, nullable=False)
    sha256 = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
