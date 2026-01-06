from typing import Any, Dict, Optional
from datetime import datetime

from sqlmodel import Session

from .models import ScanSession, AllergenFinding
from .database import engine


def save_detection_result(
    allergen_detection: Dict[str, Any],
    raw_text: str,
    cleaned_text: str,
    timings: Dict[str, float],
    source: str,
    user_label: Optional[str] = None,
) -> int:
    """
    Persist a detection result with its allergen findings.

    Args:
        allergen_detection: structured detection result (contains/may_contain/summary)
        raw_text: raw OCR or provided text
        cleaned_text: cleaned text used for detection
        timings: timing info (seconds)
        source: 'image' or 'text'
        user_label: optional user identifier

    Returns:
        session_id of the saved ScanSession
    """

    summary = allergen_detection.get("summary", {})
    contains = allergen_detection.get("contains", []) or []
    may_contain = allergen_detection.get("may_contain", []) or []

    # Convert timings to ms if available
    total_ms = None
    if timings:
        total_ms = sum(timings.values()) * 1000

    with Session(engine) as session:
        scan_session = ScanSession(
            created_at=datetime.utcnow(),
            source=source,
            raw_text=raw_text or "",
            cleaned_text=cleaned_text or "",
            safety_label=_infer_safety(contains, may_contain),
            contains_count=int(summary.get("contains_count", len(contains))),
            may_contain_count=int(summary.get("may_contain_count", len(may_contain))),
            total_detected=int(summary.get("total_detected", len(contains) + len(may_contain))),
            duration_ms=total_ms,
            user_label=user_label,
        )
        session.add(scan_session)
        session.commit()
        session.refresh(scan_session)

        def add_findings(items, category: str):
            for item in items:
                rec = item.get("health_recommendation", {}) or {}
                finding = AllergenFinding(
                    session_id=scan_session.id,
                    allergen=item.get("allergen", ""),
                    category=item.get("category", category),
                    confidence=float(item.get("confidence", 0) or 0),
                    evidence=item.get("evidence", ""),
                    cleaned_trigger_phrase=item.get("cleaned_trigger_phrase"),
                    keyword=item.get("keyword"),
                    severity=rec.get("severity"),
                    symptoms=rec.get("symptoms"),
                    immediate_actions=rec.get("immediate_actions"),
                    when_to_seek_help=rec.get("when_to_seek_help"),
                    alternatives=rec.get("alternatives"),
                    summary=rec.get("summary"),
                )
                session.add(finding)

        add_findings(contains, "CONTAINS")
        add_findings(may_contain, "MAY_CONTAIN")
        session.commit()

        return scan_session.id


def _infer_safety(contains, may_contain) -> str:
    if contains:
        return "UNSAFE"
    if may_contain:
        return "CAUTION"
    return "SAFE"
