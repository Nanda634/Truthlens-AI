"""
VideoForensicsEngine - spec sections 16-18.
Real container metadata + frame-sampling heuristics via OpenCV. Deepfake
detection (face-swap/reenactment classifier) is wired as a pluggable slot
that reports model_status="unavailable" since no trained weights ship with
this project (spec section 59) — never fabricates a deepfake_probability.
"""
import cv2
import numpy as np
from app.services.evidence_aggregator import Signal
from app.config import settings


def _severity(score):
    if score is None:
        return None
    return "high" if score >= 0.7 else "medium" if score >= 0.4 else "low"


def run_video_forensics(path: str, sample_every_sec: float = 1.0, max_frames: int = 60) -> dict:
    signals = []
    limitations = []
    suspicious_frames = []

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return {"signals": [], "regions": [], "limitations": ["Unable to decode video file."],
                "ml_available": False, "raw": {}}

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps else 0.0

    step = max(1, int(fps * sample_every_sec))
    frames = []
    idx = 0
    while cap.isOpened() and len(frames) < max_frames:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            frames.append((idx / fps if fps else idx, frame))
        idx += 1
    cap.release()

    # Frame-to-frame consistency: large sudden histogram jumps between sampled
    # frames can indicate cuts/splices/frame insertion.
    hist_diffs = []
    prev_hist = None
    for t, frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [64], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        if prev_hist is not None:
            diff = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA)
            hist_diffs.append((t, diff))
        prev_hist = hist

    if hist_diffs:
        diffs_only = np.array([d for _, d in hist_diffs])
        mean_diff = float(diffs_only.mean())
        std_diff = float(diffs_only.std())
        threshold = mean_diff + 2.5 * std_diff
        for t, d in hist_diffs:
            if d > threshold and d > 0.3:
                suspicious_frames.append({"timestamp_sec": round(t, 2), "score": round(float(d), 3)})

        consistency_score = min(1.0, len(suspicious_frames) / max(1, len(hist_diffs)) * 4)
        signals.append(Signal(
            "consistency", "Frame-to-frame consistency analysis", round(consistency_score, 3),
            _severity(consistency_score),
            f"{len(suspicious_frames)} abrupt visual discontinuities detected across {len(frames)} sampled frames.",
            str(suspicious_frames[:10]),
        ))
    else:
        limitations.append("Insufficient frames sampled to assess frame-to-frame consistency.")

    signals.append(Signal("metadata", "Container/codec metadata analysis", 0.05, "low",
                           f"{width}x{height}, {round(fps, 2)}fps, {round(duration, 2)}s duration.",
                           f"frame_count={frame_count}"))

    model_configured = bool(settings.MODEL_VIDEO_PATH)
    ai_result = {
        "model_status": "unavailable",
        "deepfake_probability": None,
        "frames_analyzed": len(frames),
        "message": "Specialized deepfake-detection model is not configured.",
    }
    limitations.append("AI model unavailable — result based on forensic signals only.")
    limitations.append("This analysis cannot confirm face-swap or reenactment manipulation without a trained model.")

    return {
        "signals": signals,
        "regions": [{"frame_number": None, "timestamp_sec": f["timestamp_sec"], "confidence": f["score"]}
                     for f in suspicious_frames],
        "limitations": limitations,
        "ml_available": False,
        "ai_model_result": ai_result,
        "raw": {"fps": fps, "duration": duration, "width": width, "height": height,
                "frames_sampled": len(frames), "suspicious_frames": suspicious_frames},
    }
