"""
EvidenceAggregator - spec section 48.
Combines normalized results from independent forensic engines into one
traceable final result. Never forces uncertain evidence into a hard "fake"
verdict - falls back to INCONCLUSIVE when signal strength is weak/conflicting.
"""
from dataclasses import dataclass, field
from app.config import settings

LABELS = [
    "AUTHENTIC", "LIKELY_AUTHENTIC", "SUSPICIOUS", "LIKELY_MANIPULATED",
    "AI_GENERATED", "LIKELY_AI_GENERATED", "TAMPERED", "INCONCLUSIVE", "UNSUPPORTED",
]


@dataclass
class Signal:
    signal_type: str  # metadata/forensic/ml/structural/consistency
    name: str
    score: float  # 0..1, higher = more suspicious
    severity: str  # low/medium/high
    description: str
    evidence: str = ""


@dataclass
class AggregatedResult:
    label: str
    confidence: float
    risk_score: float
    signals: list = field(default_factory=list)
    limitations: list = field(default_factory=list)
    category_scores: dict = field(default_factory=dict)


def _avg(signals, stype):
    matched = [s.score for s in signals if s.signal_type == stype and s.score is not None]
    if not matched:
        return None
    return sum(matched) / len(matched)


def aggregate(signals: list, ml_available: bool, limitations: list = None) -> AggregatedResult:
    limitations = limitations or []

    metadata_score = _avg(signals, "metadata")
    forensic_score = _avg(signals, "forensic")
    ml_score = _avg(signals, "ml")
    structural_score = _avg(signals, "structural")
    consistency_score = _avg(signals, "consistency")

    category_scores = {
        "metadata": metadata_score,
        "forensic": forensic_score,
        "ml": ml_score,
        "structural": structural_score,
        "consistency": consistency_score,
    }

    weights = {
        "metadata": settings.WEIGHT_METADATA,
        "forensic": settings.WEIGHT_FORENSIC,
        "ml": settings.WEIGHT_ML,
        "structural": settings.WEIGHT_STRUCTURAL,
        "consistency": settings.WEIGHT_CONSISTENCY,
    }

    if not ml_available:
        limitations.append(
            "No specialized AI-generation/deepfake model was configured for this analysis; "
            "the result below is based on forensic and structural heuristics only, which are "
            "weaker evidence than a trained classifier."
        )

    available = {k: v for k, v in category_scores.items() if v is not None}
    if not available:
        return AggregatedResult(
            label="INCONCLUSIVE", confidence=0.0, risk_score=0.0,
            signals=signals,
            limitations=limitations + ["Available forensic signals are insufficient to determine authenticity reliably."],
            category_scores=category_scores,
        )

    total_weight = sum(weights[k] for k in available)
    weighted_sum = sum(available[k] * weights[k] for k in available)
    final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
    risk_score = round(final_score * 100, 1)

    # Confidence reflects both the score's extremity and how much evidence backs it.
    evidence_coverage = len(available) / 5.0
    confidence = round(min(0.97, (0.5 + abs(final_score - 0.5)) * (0.6 + 0.4 * evidence_coverage)), 2)

    n_high_severity = sum(1 for s in signals if s.severity == "high")

    if len(available) <= 1 and n_high_severity == 0:
        label = "INCONCLUSIVE"
    elif final_score >= 0.80 and ml_score is not None and ml_score >= 0.75:
        label = "AI_GENERATED" if any("ai" in s.name.lower() or "synthetic" in s.name.lower()
                                       for s in signals if s.score and s.score > 0.7) else "TAMPERED"
    elif final_score >= 0.65:
        label = "LIKELY_MANIPULATED" if ml_score is None or ml_score < 0.6 else "LIKELY_AI_GENERATED"
    elif final_score >= 0.45:
        label = "SUSPICIOUS"
    elif final_score >= 0.25:
        label = "LIKELY_AUTHENTIC"
    else:
        label = "AUTHENTIC"

    return AggregatedResult(
        label=label,
        confidence=confidence,
        risk_score=risk_score,
        signals=signals,
        limitations=limitations,
        category_scores=category_scores,
    )
