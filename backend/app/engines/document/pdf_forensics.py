"""PDFForensicsEngine - spec sections 22-24."""
import fitz  # PyMuPDF
from app.services.evidence_aggregator import Signal


def _severity(score):
    if score is None:
        return None
    return "high" if score >= 0.7 else "medium" if score >= 0.4 else "low"


def run_pdf_forensics(path: str) -> dict:
    signals = []
    limitations = []
    regions = []

    try:
        doc = fitz.open(path)
    except Exception as e:
        return {"signals": [], "regions": [], "limitations": [f"Unable to parse PDF: {e}"],
                "ml_available": False, "raw": {}}

    meta = doc.metadata or {}
    producer = (meta.get("producer") or "").lower()
    creator = (meta.get("creator") or "").lower()

    suspicious_kw = ["screenshot", "canva", "unknown", ""]
    meta_score = 0.2
    findings = []
    if not meta.get("creationDate") and not meta.get("modDate"):
        meta_score += 0.15
        findings.append("No creation/modification timestamps present.")
    if meta.get("modDate") and meta.get("creationDate") and meta["modDate"] != meta["creationDate"]:
        meta_score += 0.15
        findings.append("Modification date differs from creation date.")
    if not producer and not creator:
        meta_score += 0.2
        findings.append("No producer/creator application recorded.")

    meta_score = min(1.0, meta_score)
    signals.append(Signal("metadata", "PDF metadata analysis", meta_score, _severity(meta_score),
                           "; ".join(findings) or "Metadata appears consistent.", str(meta)))

    # Incremental update / structural check: multiple %%EOF markers indicate
    # the file was saved more than once (incremental update), which is common
    # for legitimately annotated PDFs but also for post-hoc edits.
    try:
        with open(path, "rb") as f:
            raw = f.read()
        eof_count = raw.count(b"%%EOF")
        js_present = b"/JavaScript" in raw or b"/JS " in raw
    except Exception:
        eof_count = 1
        js_present = False

    struct_score = min(1.0, max(0.0, (eof_count - 1) * 0.25))
    signals.append(Signal("structural", "Incremental update analysis", struct_score, _severity(struct_score),
                           f"{eof_count} EOF marker(s) found (>1 indicates incremental saves/edits).",
                           f"eof_count={eof_count}"))

    if js_present:
        signals.append(Signal("structural", "Embedded JavaScript check", 0.6, "medium",
                               "Embedded JavaScript detected in PDF — unusual for standard documents.",
                               "js_present=True"))

    sig_present = False
    try:
        for xref in range(1, doc.xref_length()):
            if doc.xref_get_key(xref, "Type")[1] == "/Sig":
                sig_present = True
                break
    except Exception:
        pass

    signature_info = {"signature_present": sig_present, "signature_valid": None,
                       "document_modified_after_signature": None}
    if sig_present:
        limitations.append("Digital signature detected but cryptographic validation is not configured "
                            "in this deployment — signature validity was not verified.")

    # Per-page rendering consistency (spec 23): compare page image sizes/aspect
    # ratios and detect an outlier page.
    page_sizes = []
    for page in doc:
        rect = page.rect
        page_sizes.append((rect.width, rect.height))

    outlier_pages = []
    if len(page_sizes) > 2:
        widths = [p[0] for p in page_sizes]
        median_w = sorted(widths)[len(widths) // 2]
        for i, (w, h) in enumerate(page_sizes):
            if median_w > 0 and abs(w - median_w) / median_w > 0.05:
                outlier_pages.append(i + 1)

    if outlier_pages:
        consistency_score = min(1.0, 0.3 + 0.15 * len(outlier_pages))
        signals.append(Signal(
            "consistency", "Page dimension consistency", consistency_score, _severity(consistency_score),
            f"Page(s) {outlier_pages} differ significantly in dimensions from the rest of the document.",
            str(outlier_pages),
        ))
        for p in outlier_pages:
            regions.append({"page_number": p, "confidence": consistency_score})
    else:
        signals.append(Signal("consistency", "Page dimension consistency", 0.05, "low",
                               "All pages share consistent dimensions.", ""))

    limitations.append("AI model unavailable — result based on structural/metadata forensic signals only.")
    limitations.append("This analysis cannot establish authorship or intent behind detected changes.")

    doc.close()

    return {
        "signals": signals,
        "regions": regions,
        "limitations": limitations,
        "ml_available": False,
        "raw": {"metadata": meta, "eof_count": eof_count, "js_present": js_present,
                "signature": signature_info, "page_count": len(page_sizes)},
    }
