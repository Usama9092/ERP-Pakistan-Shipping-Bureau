"""
EPAS · UI Helpers
------------------
Small, pure functions that turn domain data into the HTML fragments
used across components. Centralising these means a badge always looks
the same whether it's rendered in the KPI row, the RFI queue, or the
Ship Register.
"""

from __future__ import annotations

from datetime import date, datetime

import streamlit as st

from config import settings as cfg

# -----------------------------------------------------------------------
# Date helpers
# -----------------------------------------------------------------------

def to_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return datetime.fromisoformat(str(value)).date()
    except ValueError:
        return None


def days_between(target, base: date | None = None) -> int | None:
    d = to_date(target)
    if d is None:
        return None
    base = base or date.today()
    return (d - base).days


def fmt_date(value) -> str:
    d = to_date(value)
    return d.strftime(cfg.DATE_FMT) if d else "—"


def fmt_datetime(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime(cfg.DATETIME_FMT)


def relative_age(value) -> str:
    """'3 days ago' / 'today' / 'in 4 days' style label."""
    d = to_date(value)
    if d is None:
        return "—"
    delta = (date.today() - d).days
    if delta == 0:
        return "today"
    if delta > 0:
        return f"{delta} day{'s' if delta != 1 else ''} ago"
    return f"in {abs(delta)} day{'s' if abs(delta) != 1 else ''}"


# -----------------------------------------------------------------------
# Badge / pill renderers  → return raw HTML, caller wraps in st.markdown
# -----------------------------------------------------------------------

_BADGE_KIND_BY_RFI_STATUS = {
    cfg.RFI_PENDING_ALLOCATION: "warning",
    cfg.RFI_ALLOCATED: "info",
    cfg.RFI_SURVEY_IN_PROGRESS: "info",
    cfg.RFI_OBSERVATIONS_LOGGED: "warning",
    cfg.RFI_PENDING_GM_APPROVAL: "action",
    cfg.RFI_SENT_BACK: "danger",
    cfg.RFI_APPROVED_CLEAN: "success",
    cfg.RFI_APPROVED_WITH_OBS: "warning",
    cfg.RFI_CERT_ISSUED: "success",
    cfg.RFI_CLOSED: "neutral",
}

_BADGE_KIND_BY_CERT_STATUS = {
    cfg.CERT_STATUS_ACTIVE: "success",
    cfg.CERT_STATUS_EXPIRED: "danger",
    cfg.CERT_STATUS_SUPERSEDED: "neutral",
}

_BADGE_KIND_BY_DOC_STATUS = {
    "approved": "success",
    "pending_review": "info",
    "amendments_required": "warning",
    "rejected": "danger",
}


def badge(label: str, kind: str = "neutral") -> str:
    """kind ∈ success | warning | danger | info | action | neutral"""
    return f'<span class="badge badge--{kind}">{label}</span>'


def rfi_status_badge(status: str) -> str:
    kind = _BADGE_KIND_BY_RFI_STATUS.get(status, "neutral")
    label = cfg.RFI_STAGE_LABELS.get(status, status)
    return badge(label, kind)


def cert_status_badge(status: str) -> str:
    kind = _BADGE_KIND_BY_CERT_STATUS.get(status, "neutral")
    return badge(status.title(), kind)


def doc_status_badge(status: str) -> str:
    kind = _BADGE_KIND_BY_DOC_STATUS.get(status, "neutral")
    label = cfg.DOC_STATUS_LABELS.get(status, status)
    return badge(label, kind)


def priority_badge(priority: str) -> str:
    kind = {"high": "danger", "medium": "warning", "low": "neutral"}.get(priority, "neutral")
    return badge(priority.title(), kind)


def severity_badge(severity: str) -> str:
    kind = {"Critical": "danger", "Major": "warning", "Minor": "info"}.get(severity, "neutral")
    return badge(severity, kind)


def days_remaining_badge(expiry_value, warn_days: int = cfg.CERT_EXPIRING_SOON_DAYS) -> str:
    n = days_between(expiry_value)
    if n is None:
        return badge("—", "neutral")
    if n < 0:
        return badge(f"Expired {abs(n)}d ago", "danger")
    if n <= warn_days:
        return badge(f"{n} days left", "warning")
    return badge(f"{n} days left", "success")


# -----------------------------------------------------------------------
# Stage track — small horizontal stepper used on every RFI card,
# mirrors the exact left-to-right spine of the flowchart.
# -----------------------------------------------------------------------

def stage_track_html(current_status: str) -> str:
    stages = cfg.RFI_STAGE_ORDER
    terminal_variants = {cfg.RFI_APPROVED_WITH_OBS: cfg.RFI_APPROVED_CLEAN,
                          cfg.RFI_SENT_BACK: cfg.RFI_PENDING_GM_APPROVAL}
    effective = terminal_variants.get(current_status, current_status)

    try:
        current_idx = stages.index(effective)
    except ValueError:
        current_idx = -1

    dots = []
    for i, stage in enumerate(stages):
        label = cfg.RFI_STAGE_LABELS[stage]
        if i < current_idx:
            state = "done"
        elif i == current_idx:
            state = "current"
        else:
            state = "pending"

        # Special-case colouring for the two branch outcomes
        if stage == cfg.RFI_APPROVED_CLEAN and current_status == cfg.RFI_APPROVED_WITH_OBS and i == current_idx:
            state = "current-warn"
            label = "Approved — Open Obs."
        if stage == cfg.RFI_PENDING_GM_APPROVAL and current_status == cfg.RFI_SENT_BACK and i == current_idx:
            state = "current-danger"
            label = "Returned for Rework"

        dots.append(
            f'<div class="stage-step stage-step--{state}">'
            f'<span class="stage-dot"></span><span class="stage-step-label">{label}</span>'
            f"</div>"
        )
        if i < len(stages) - 1:
            connector_state = "done" if i < current_idx else "pending"
            dots.append(f'<div class="stage-connector stage-connector--{connector_state}"></div>')

    return f'<div class="stage-track">{"".join(dots)}</div>'


# -----------------------------------------------------------------------
# Misc
# -----------------------------------------------------------------------

def initials(full_name: str) -> str:
    parts = [p for p in full_name.split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def phase_icon_label(phase: str) -> str:
    return f"{cfg.PHASE_ICONS.get(phase, '•')} {cfg.PHASE_LABELS.get(phase, phase)}"


# -----------------------------------------------------------------------
# Modal compatibility shim
# -----------------------------------------------------------------------

def modal(title: str, width: str = "large"):
    """
    Drop-in replacement for `st.dialog` that degrades gracefully on
    Streamlit versions older than 1.31 (no native dialog support).
    Usage is identical to st.dialog:

        @modal("Document Detail")
        def show_document(doc_id):
            ...

        if st.button("View"):
            show_document(doc_id)
    """
    if hasattr(st, "dialog"):
        return st.dialog(title, width=width)

    def _decorator(func):
        def _wrapper(*args, **kwargs):
            st.markdown(f"#### {title}")
            with st.container(border=True):
                return func(*args, **kwargs)
        return _wrapper
    return _decorator
