import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from app.database.database import Base


def gen_id():
    return "ANL-" + uuid.uuid4().hex[:12].upper()


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=gen_id)
    file_id = Column(String, ForeignKey("files.id"), nullable=False)
    analysis_type = Column(String, nullable=False)  # image/video/audio/pdf/docx/unsupported
    status = Column(String, default="QUEUED")  # QUEUED, PROCESSING, COMPLETED, FAILED
    final_label = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
