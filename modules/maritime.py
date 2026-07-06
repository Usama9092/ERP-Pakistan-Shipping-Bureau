from __future__ import annotations

from typing import Any

import pandas as pd

MODULE_INFO = {
    "name": "Maritime",
    "description": "Maritime registry, survey, certificate, and notification services.",
    "version": "1.0.0",
    "pages": ["Maritime Registry", "Maritime Surveys"],
}

SURVEY_TYPES = [
    "Annual Survey",
    "Intermediate Survey",
    "Renewal Survey",
    "Load Line Survey",
    "Safety Equipment Survey",
    "Safety Radio Survey",
    "ISM Survey",
    "ISPS Survey",
    "MARPOL Survey",
    "Special Survey",
    "Dry Dock Survey",
    "Bottom Survey",
    "Electrical Survey",
    "Hull Survey",
    "Machinery Survey",
]


def build_dashboard_summary(ships: list[dict[str, Any]], surveys: list[dict[str, Any]], certificates: list[dict[str, Any]], notifications: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "ships": len(ships),
        "surveys": len(surveys),
        "certificates": len(certificates),
        "notifications": len(notifications),
    }


def sanitize_text_input(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    text = text.replace("<script", "&lt;script")
    text = text.replace("</script", "&lt;/script")
    text = text.strip()
    return text


def normalize_checklist_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "section": str(item.get("section", "")).strip(),
        "subsection": str(item.get("subsection", "")).strip(),
        "checklist_item": str(item.get("checklist_item", "")).strip(),
        "inspection_requirement": str(item.get("inspection_requirement", "")).strip(),
        "observation": str(item.get("observation", "")),
        "status": str(item.get("status", "Pending")) or "Pending",
        "remarks": str(item.get("remarks", "")),
        "photo_required": bool(item.get("photo_required", False)),
        "document_required": bool(item.get("document_required", False)),
        "gps_required": bool(item.get("gps_required", False)),
        "inspector_name": str(item.get("inspector_name", "")).strip(),
        "survey_date": str(item.get("survey_date", "")),
        "digital_signature": str(item.get("digital_signature", "")).strip(),
        "completion_pct": int(item.get("completion_pct", 0) or 0),
    }
