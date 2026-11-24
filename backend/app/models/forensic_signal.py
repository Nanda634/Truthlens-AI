import uuid
from sqlalchemy import Column, String, Float, ForeignKey, Text
from app.database.database import Base


def gen_id():
    return str(uuid.uuid4())


class ForensicSignal(Base):
    __tablename__ = "forensic_signals"

    id = Column(String, primary_key=True, default=gen_id)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    signal_type = Column(String, nullable=False)  # metadata/forensic/ml/structural/consistency
    signal_name = Column(String, nullable=False)
    score = Column(Float, nullable=True)
    severity = Column(String, nullable=True)  # low/medium/high
    description = Column(Text, nullable=True)
    evidence = Column(Text, nullable=True)


class DetectedRegion(Base):
    __tablename__ = "detected_regions"

    id = Column(String, primary_key=True, default=gen_id)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    page_number = Column(String, nullable=True)
    frame_number = Column(String, nullable=True)
    x = Column(Float, nullable=True)
    y = Column(Float, nullable=True)
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=gen_id)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    report_path = Column(String, nullable=False)
