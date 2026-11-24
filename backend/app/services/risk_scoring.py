"""Maps a 0-100 risk_score to a human-readable risk band - spec section 8."""


def risk_band(risk_score: float) -> str:
    if risk_score <= 20:
        return "VERY_LOW"
    if risk_score <= 40:
        return "LOW"
    if risk_score <= 60:
        return "MODERATE"
    if risk_score <= 80:
        return "HIGH"
    return "VERY_HIGH"


RISK_LABELS = {
    "VERY_LOW": "Very Low Manipulation Risk",
    "LOW": "Low Risk",
    "MODERATE": "Moderate Risk",
    "HIGH": "High Risk",
    "VERY_HIGH": "Very High Risk",
}
