"""ImageForensicsEngine - orchestrates all image-specific checks, spec section 9."""
from app.services.metadata import extract_image_metadata
from app.services.evidence_aggregator import Signal
from app.engines.image.ela import error_level_analysis
from app.engines.image.noise import noise_consistency_analysis
from app.engines.image.frequency import frequency_analysis
from app.engines.image.copy_move import copy_move_detection
from app.engines.image.splicing import splicing_analysis
from app.engines.image.ai_detector import AIImageDetector


def _severity(score):
    if score is None:
        return None
    if score >= 0.7:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


def run_image_forensics(path: str) -> dict:
    signals = []
    regions = []
    limitations = []

    meta = extract_image_metadata(path)
    meta_score = 0.55 if meta.get("suspicious_software") else (0.1 if meta.get("exif_present") else 0.3)
    signals.append(Signal(
        "metadata", "Metadata / EXIF analysis", meta_score, _severity(meta_score),
        f"Editing software detected: {meta.get('software')}" if meta.get("suspicious_software")
        else ("Camera EXIF present." if meta.get("exif_present") else "No EXIF metadata found (common after re-saving or messaging-app compression)."),
        str(meta),
    ))

    ela = error_level_analysis(path)
    if ela.get("available"):
        signals.append(Signal("forensic", "Error Level Analysis", ela["score"], _severity(ela["score"]),
                               f"Anomaly concentration: {ela['anomaly_percentage']}% of pixels.", str(ela)))
    else:
        limitations.append("Error Level Analysis could not be completed for this file.")

    noise = noise_consistency_analysis(path)
    if noise.get("available"):
        signals.append(Signal("forensic", "Noise consistency analysis", noise["score"], _severity(noise["score"]),
                               f"Outlier noise blocks: {noise['outlier_block_percentage']}%.", str(noise)))
    else:
        limitations.append("Noise consistency analysis could not be completed for this file.")

    freq = frequency_analysis(path)
    if freq.get("available"):
        signals.append(Signal("forensic", "Frequency-domain (FFT) analysis", freq["score"], _severity(freq["score"]),
                               f"High/low frequency energy ratio: {freq['high_low_freq_ratio']}.", str(freq)))
    else:
        limitations.append("Frequency-domain analysis could not be completed for this file.")

    cm = copy_move_detection(path)
    if cm.get("available"):
        signals.append(Signal("structural", "Copy-move detection", cm["score"], _severity(cm["score"]),
                               f"Matched keypoint clusters: {cm['matches_found']}.", str(cm)))
        regions.extend(cm.get("regions", []))
    else:
        limitations.append("Copy-move detection could not be completed for this file.")

    splice = splicing_analysis(path)
    if splice.get("available"):
        signals.append(Signal("structural", "Splicing indicator analysis", splice["splicing_probability"],
                               _severity(splice["splicing_probability"]),
                               "Edge/illumination inconsistency across image regions.", str(splice)))
    else:
        limitations.append("Splicing indicator analysis could not be completed for this file.")

    ai = AIImageDetector().predict(path)
    ml_available = ai.get("model_status") == "available"
    if ml_available:
        signals.append(Signal("ml", "AI-generated image classifier", ai["ai_generated_probability"], "high",
                               "Trained classifier output.", str(ai)))
    else:
        limitations.append("AI model unavailable — result based on forensic signals only.")

    limitations.append(
        "This analysis cannot establish the original creator or prove malicious intent."
    )

    return {
        "signals": signals,
        "regions": regions,
        "limitations": limitations,
        "ml_available": ml_available,
        "ai_model_result": ai,
        "raw": {"metadata": meta, "ela": ela, "noise": noise, "frequency": freq,
                "copy_move": cm, "splicing": splice},
    }
