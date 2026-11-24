import os
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.config import settings
from app.models.file import FileRecord
from app.models.analysis import Analysis
from app.models.forensic_signal import ForensicSignal, DetectedRegion, Report
from app.api.deps import get_current_user
from app.models.user import User
from app.services.file_validation import categorize
from app.services.evidence_aggregator import aggregate
from app.services.risk_scoring import risk_band, RISK_LABELS
from app.services.report_generator import generate_report

from app.engines.image.image_forensics import run_image_forensics
from app.engines.document.pdf_forensics import run_pdf_forensics
from app.engines.document.docx_forensics import run_docx_forensics
from app.engines.audio.audio_forensics import run_audio_forensics
from app.engines.video.video_forensics import run_video_forensics

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

ENGINE_MAP = {
    "image": run_image_forensics,
    "pdf": run_pdf_forensics,
    "docx": run_docx_forensics,
    "audio": run_audio_forensics,
    "video": run_video_forensics,
}


def _run_analysis_job(analysis_id: str, file_path: str, category: str):
    from app.database.database import SessionLocal
    db = SessionLocal()
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        analysis.status = "PROCESSING"
        db.commit()

        engine_fn = ENGINE_MAP.get(category)
        if not engine_fn:
            analysis.status = "COMPLETED"
            analysis.final_label = "UNSUPPORTED"
            analysis.confidence = 0.0
            analysis.risk_score = 0.0
            analysis.completed_at = datetime.utcnow()
            db.commit()
            return

        engine_result = engine_fn(file_path)
        signals = engine_result.get("signals", [])
        aggregated = aggregate(signals, engine_result.get("ml_available", False),
                                list(engine_result.get("limitations", [])))

        analysis.status = "COMPLETED"
        analysis.final_label = aggregated.label
        analysis.confidence = aggregated.confidence
        analysis.risk_score = aggregated.risk_score
        analysis.completed_at = datetime.utcnow()
        db.commit()

        for s in signals:
            db.add(ForensicSignal(
                analysis_id=analysis_id, signal_type=s.signal_type, signal_name=s.name,
                score=s.score, severity=s.severity, description=s.description, evidence=s.evidence,
            ))
        for r in engine_result.get("regions", []):
            db.add(DetectedRegion(
                analysis_id=analysis_id,
                page_number=str(r.get("page_number")) if r.get("page_number") is not None else None,
                frame_number=str(r.get("frame_number")) if r.get("frame_number") is not None else None,
                x=r.get("x"), y=r.get("y"), width=r.get("width"), height=r.get("height"),
                confidence=r.get("confidence"),
            ))
        db.commit()

        # persist full evidence blob for the /result and /evidence endpoints
        blob_path = os.path.join(settings.TEMP_DIR, f"{analysis_id}_evidence.json")
        with open(blob_path, "w") as f:
            json.dump({
                "limitations": aggregated.limitations,
                "category_scores": aggregated.category_scores,
                "raw": {k: (str(v) if not isinstance(v, (dict, list, str, int, float, bool, type(None))) else v)
                        for k, v in engine_result.get("raw", {}).items()},
            }, f, default=str)

    except Exception as e:
        analysis.status = "FAILED"
        analysis.error_message = str(e)
        analysis.completed_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()


@router.post("/{file_id}")
def start_analysis(file_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    record = db.query(FileRecord).filter(FileRecord.id == file_id, FileRecord.user_id == user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="File not found.")

    category = categorize(record.detected_mime_type)
    analysis = Analysis(file_id=file_id, analysis_type=category, status="QUEUED")
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    file_path = os.path.join(settings.UPLOAD_DIR, record.stored_filename)
    background_tasks.add_task(_run_analysis_job, analysis.id, file_path, category)

    return {"success": True, "analysis_id": analysis.id, "status": analysis.status}


@router.get("/{analysis_id}/status")
def get_status(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return {"analysis_id": analysis.id, "status": analysis.status, "error": analysis.error_message}


@router.get("/{analysis_id}/result")
def get_result(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    record = db.query(FileRecord).filter(FileRecord.id == analysis.file_id).first()

    result = {
        "success": True,
        "analysis_id": analysis.id,
        "status": analysis.status,
        "file": {
            "name": record.original_filename, "type": record.detected_mime_type,
            "size": record.file_size, "sha256": record.sha256,
        } if record else {},
        "result": {
            "label": analysis.final_label,
            "confidence": analysis.confidence,
            "risk_score": analysis.risk_score,
            "risk_band": risk_band(analysis.risk_score) if analysis.risk_score is not None else None,
            "risk_label": RISK_LABELS.get(risk_band(analysis.risk_score)) if analysis.risk_score is not None else None,
        },
        "disclaimer": (
            "Automated digital-authenticity analysis can identify signals associated with "
            "manipulation or synthetic generation, but no automated detector can guarantee "
            "authenticity or manipulation in every case. Results should be independently "
            "verified when used for legal, financial, employment, security, journalistic, "
            "or other high-stakes decisions."
        ),
    }
    return result


@router.get("/{analysis_id}/evidence")
def get_evidence(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    signals = db.query(ForensicSignal).filter(ForensicSignal.analysis_id == analysis_id).all()
    regions = db.query(DetectedRegion).filter(DetectedRegion.analysis_id == analysis_id).all()

    blob_path = os.path.join(settings.TEMP_DIR, f"{analysis_id}_evidence.json")
    extra = {}
    if os.path.exists(blob_path):
        with open(blob_path) as f:
            extra = json.load(f)

    return {
        "analysis_id": analysis_id,
        "signals": [{"type": s.signal_type, "name": s.signal_name, "score": s.score,
                     "severity": s.severity, "description": s.description} for s in signals],
        "regions": [{"page_number": r.page_number, "frame_number": r.frame_number,
                     "x": r.x, "y": r.y, "width": r.width, "height": r.height,
                     "confidence": r.confidence} for r in regions],
        "limitations": extra.get("limitations", []),
        "category_scores": extra.get("category_scores", {}),
    }


@router.get("/{analysis_id}/report")
def get_report(analysis_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis or analysis.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="Analysis not completed.")
    record = db.query(FileRecord).filter(FileRecord.id == analysis.file_id).first()
    signals = db.query(ForensicSignal).filter(ForensicSignal.analysis_id == analysis_id).all()

    blob_path = os.path.join(settings.TEMP_DIR, f"{analysis_id}_evidence.json")
    limitations = []
    if os.path.exists(blob_path):
        with open(blob_path) as f:
            limitations = json.load(f).get("limitations", [])

    class SignalObj:
        def __init__(self, s):
            self.signal_type, self.name, self.score = s.signal_type, s.signal_name, s.score
            self.severity, self.description = s.severity, s.description

    report_path = generate_report(
        analysis_id,
        {"name": record.original_filename, "type": record.detected_mime_type,
         "size": record.file_size, "sha256": record.sha256},
        {"label": analysis.final_label, "confidence": analysis.confidence, "risk_score": analysis.risk_score},
        [SignalObj(s) for s in signals],
        limitations,
    )

    existing = db.query(Report).filter(Report.analysis_id == analysis_id).first()
    if not existing:
        db.add(Report(analysis_id=analysis_id, report_path=report_path))
        db.commit()

    from fastapi.responses import FileResponse
    return FileResponse(report_path, media_type="application/pdf",
                         filename=f"truthlens_report_{analysis_id}.pdf")


@router.get("/history")
def get_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    files = db.query(FileRecord).filter(FileRecord.user_id == user.id).all()
    file_ids = [f.id for f in files]
    analyses = db.query(Analysis).filter(Analysis.file_id.in_(file_ids)).order_by(Analysis.started_at.desc()).all()
    file_map = {f.id: f for f in files}

    return {"history": [{
        "analysis_id": a.id,
        "filename": file_map[a.file_id].original_filename if a.file_id in file_map else None,
        "type": a.analysis_type,
        "status": a.status,
        "label": a.final_label,
        "confidence": a.confidence,
        "risk_score": a.risk_score,
        "started_at": a.started_at,
    } for a in analyses]}
