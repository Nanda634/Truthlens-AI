"""
AudioForensicsEngine - spec sections 19-21.
Real metadata + spectral heuristics via librosa. The AI-voice classifier slot
(HuBERT/WavLM-style) is wired but reports model_status="unavailable" since no
trained weights ship with this project (spec section 59).
"""
import librosa
import numpy as np
from app.services.evidence_aggregator import Signal
from app.config import settings


def _severity(score):
    if score is None:
        return None
    return "high" if score >= 0.7 else "medium" if score >= 0.4 else "low"


def run_audio_forensics(path: str) -> dict:
    signals = []
    limitations = []

    try:
        y, sr = librosa.load(path, sr=None, mono=True)
    except Exception as e:
        return {"signals": [], "regions": [], "limitations": [f"Unable to decode audio: {e}"],
                "ml_available": False, "raw": {}}

    duration = float(len(y) / sr) if sr else 0.0

    # Spectral flatness: synthetic/TTS voices often show unusually consistent
    # (flatter) spectral flatness across time compared to natural speech.
    flatness = librosa.feature.spectral_flatness(y=y)[0]
    flatness_std = float(np.std(flatness))
    flatness_mean = float(np.mean(flatness))

    # Silence pattern analysis
    intervals = librosa.effects.split(y, top_db=30)
    silence_ratio = 1 - (sum((e - s) for s, e in intervals) / len(y)) if len(y) else 0.0

    consistency_score = min(1.0, max(0.0, (0.02 - flatness_std) * 15)) if flatness_mean > 0 else 0.3
    signals.append(Signal(
        "consistency", "Spectral consistency analysis", round(consistency_score, 3),
        _severity(consistency_score),
        f"Spectral flatness variance: {round(flatness_std, 5)} (unusually low variance can indicate synthetic audio).",
        f"flatness_mean={flatness_mean}, flatness_std={flatness_std}",
    ))

    signals.append(Signal(
        "metadata", "Audio format/metadata analysis", 0.05, "low",
        f"Duration {round(duration, 2)}s, sample rate {sr}Hz, silence ratio {round(silence_ratio, 3)}.",
        f"sr={sr}, duration={duration}",
    ))

    model_configured = bool(settings.MODEL_AUDIO_PATH)
    ai_result = {
        "model_status": "unavailable",
        "synthetic_audio_probability": None,
        "human_audio_probability": None,
        "message": "Specialized AI-generation model is not configured.",
    }
    limitations.append("AI model unavailable — result based on forensic signals only.")
    limitations.append("This analysis cannot establish the original speaker's identity or intent.")

    return {
        "signals": signals,
        "regions": [],
        "limitations": limitations,
        "ml_available": False,
        "ai_model_result": ai_result,
        "raw": {"duration": duration, "sample_rate": sr, "silence_ratio": silence_ratio,
                "flatness_mean": flatness_mean, "flatness_std": flatness_std},
    }
