"""DOCXForensicsEngine - spec sections 25-26."""
import docx
from app.services.evidence_aggregator import Signal


def _severity(score):
    if score is None:
        return None
    return "high" if score >= 0.7 else "medium" if score >= 0.4 else "low"


def run_docx_forensics(path: str) -> dict:
    signals = []
    limitations = []

    try:
        d = docx.Document(path)
    except Exception as e:
        return {"signals": [], "regions": [], "limitations": [f"Unable to parse DOCX: {e}"],
                "ml_available": False, "raw": {}}

    props = d.core_properties
    meta = {
        "author": props.author, "last_modified_by": props.last_modified_by,
        "created": str(props.created) if props.created else None,
        "modified": str(props.modified) if props.modified else None,
        "revision": props.revision,
    }

    meta_score = 0.15
    findings = []
    if props.author and props.last_modified_by and props.author != props.last_modified_by:
        meta_score += 0.2
        findings.append(f"Document authored by '{props.author}' but last modified by '{props.last_modified_by}'.")
    if props.revision and props.revision > 20:
        meta_score += 0.15
        findings.append(f"High revision count ({props.revision}).")
    if not props.created:
        meta_score += 0.1
        findings.append("No creation date recorded.")

    meta_score = min(1.0, meta_score)
    signals.append(Signal("metadata", "DOCX core properties analysis", meta_score, _severity(meta_score),
                           "; ".join(findings) or "Metadata appears consistent.", str(meta)))

    embedded_images = 0
    try:
        for rel in d.part.rels.values():
            if "image" in rel.reltype:
                embedded_images += 1
    except Exception:
        pass

    # Font/style consistency: count distinct fonts used in runs
    fonts_used = set()
    for para in d.paragraphs:
        for run in para.runs:
            if run.font and run.font.name:
                fonts_used.add(run.font.name)

    struct_score = min(1.0, max(0.0, (len(fonts_used) - 2) * 0.15))
    signals.append(Signal(
        "structural", "Font/formatting consistency", struct_score, _severity(struct_score),
        f"{len(fonts_used)} distinct font(s) used across the document body." if fonts_used
        else "No explicit run-level fonts set (using style defaults).",
        str(list(fonts_used)),
    ))

    # Track changes / comments detection via XML
    xml = d.element.xml
    has_track_changes = "<w:ins " in xml or "<w:del " in xml
    has_comments = "w:commentRangeStart" in xml or "w:comment " in xml

    if has_track_changes:
        signals.append(Signal("structural", "Track changes detection", 0.3, "low",
                               "Document contains tracked insertions/deletions.", ""))

    if has_comments:
        signals.append(Signal("structural", "Comments detection", 0.15, "low",
                               "Document contains reviewer comments.", ""))

    signals.append(Signal("metadata", "Embedded object count", 0.0, "low",
                           f"{embedded_images} embedded image(s) found.", str(embedded_images)))

    limitations.append("AI model unavailable — result based on structural/metadata forensic signals only.")
    limitations.append("This analysis cannot establish authorship or intent behind detected changes.")

    return {
        "signals": signals,
        "regions": [],
        "limitations": limitations,
        "ml_available": False,
        "raw": {"metadata": meta, "embedded_images": embedded_images, "fonts_used": list(fonts_used),
                "has_track_changes": has_track_changes},
    }
