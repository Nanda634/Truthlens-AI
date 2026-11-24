"""
Error Level Analysis - spec section 10.
Recompresses the image at a controlled JPEG quality and measures pixel-level
differences. Explicitly labeled as a supporting signal, not standalone proof.
"""
import io
import numpy as np
from PIL import Image, ImageChops


def error_level_analysis(path: str, quality: int = 90) -> dict:
    try:
        original = Image.open(path).convert("RGB")
        buffer = io.BytesIO()
        original.save(buffer, "JPEG", quality=quality)
        buffer.seek(0)
        recompressed = Image.open(buffer)

        diff = ImageChops.difference(original, recompressed)
        diff_arr = np.asarray(diff).astype(np.float32)

        max_diff = float(diff_arr.max()) if diff_arr.size else 0.0
        mean_diff = float(diff_arr.mean()) if diff_arr.size else 0.0

        # Anomaly percentage: fraction of pixels whose error level is far above the mean
        threshold = mean_diff + 2 * diff_arr.std() if diff_arr.size else 0
        anomaly_mask = diff_arr.mean(axis=2) > threshold if diff_arr.ndim == 3 else np.zeros((1, 1))
        anomaly_pct = float(anomaly_mask.mean() * 100) if anomaly_mask.size else 0.0

        # Normalize into a 0..1 suspicion score. High mean error + high anomaly
        # concentration suggests localized re-editing rather than uniform re-save.
        score = min(1.0, (anomaly_pct / 15.0) * 0.6 + (min(mean_diff, 25) / 25.0) * 0.4)

        return {
            "available": True,
            "mean_error_level": round(mean_diff, 3),
            "max_error_level": round(max_diff, 3),
            "anomaly_percentage": round(anomaly_pct, 2),
            "score": round(score, 3),
            "note": "Supporting forensic signal — not standalone proof.",
        }
    except Exception as e:
        return {"available": False, "error": str(e), "score": None,
                "note": "Supporting forensic signal — not standalone proof."}
