from __future__ import annotations

import html
import re
from datetime import datetime, date
from typing import Any

import pandas as pd

PROJECT_CONFIG = {
    "project_name": "Maritime Classification & Ship Registry Platform",
    "version": "2.1.0",
    "description": "Enterprise-grade maritime survey, ship registry, certificate, and notification management system.",
    "developers": ["PSB Engineering Team", "Maritime Systems Division"],
    "company": "Pakistan Shipping Bureau",
    "last_updated": "2026-07-04",
    "change_log": [
        "Added centralized project configuration",
        "Added maritime registry, survey checklist, and notification modules",
        "Added theme support, security hardening helpers, and audit logging",
    ],
    "license": "Internal Enterprise License",
    "modules": [
        "Project Information",
        "Ship Registry",
        "Survey Management",
        "Certificate Management",
        "Notifications",
        "Dashboards",
        "Reports",
    ],
    "system_status": "Production Ready",
    "dependencies": ["Streamlit", "SQLAlchemy", "Pandas", "Supabase", "PyPDF2", "python-docx"],
    "database_version": "v21 Maritime Core",
    "environment": "Production/Development",
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

CERTIFICATE_CATEGORIES = [
    "Class",
    "Load Line",
    "SOLAS",
    "ISM",
    "ISPS",
    "MARPOL",
    "IOPP",
    "Safety Construction",
    "Safety Equipment",
    "Safety Radio",
    "Cargo Ship Safety",
    "Minimum Safe Manning",
    "Tonnage",
    "International Sewage",
    "International Air Pollution",
]

NOTIFICATION_TYPES = [
    "Certificate Expiring",
    "Survey Due",
    "Survey Overdue",
    "Ship Status Changed",
    "Document Missing",
    "Approval Required",
    "Checklist Submitted",
    "Checklist Rejected",
    "Survey Assigned",
]


def get_project_config() -> dict[str, Any]:
    return PROJECT_CONFIG


def sanitize_text_input(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_checklist_item(item: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "section": sanitize_text_input(item.get("section", "")),
        "subsection": sanitize_text_input(item.get("subsection", "")),
        "checklist_item": sanitize_text_input(item.get("checklist_item", "")),
        "inspection_requirement": sanitize_text_input(item.get("inspection_requirement", "")),
        "observation": sanitize_text_input(item.get("observation", "")),
        "status": sanitize_text_input(item.get("status", "Pending")),
        "remarks": sanitize_text_input(item.get("remarks", "")),
        "photo_required": bool(item.get("photo_required", False)),
        "document_required": bool(item.get("document_required", False)),
        "gps_required": bool(item.get("gps_required", False)),
        "inspector_name": sanitize_text_input(item.get("inspector_name", "")),
        "survey_date": sanitize_text_input(item.get("survey_date", today_iso())),
        "digital_signature": sanitize_text_input(item.get("digital_signature", "")),
        "completion_pct": int(item.get("completion_pct", 0) or 0),
    }
    normalized["status"] = normalized["status"] or "Pending"
    normalized["completion_pct"] = max(0, min(100, normalized["completion_pct"]))
    return normalized


def calculate_completion_percentage(completed: int, total: int) -> int:
    if total <= 0:
        return 0
    value = int(round((completed / total) * 100))
    return max(0, min(100, value))


def build_theme_css(theme: str) -> str:
    if theme == "dark":
        return """
        :root { color-scheme: dark; }
        .theme-shell { background: #0f172a; color: #e2e8f0; }
        .theme-card { background: #111827; border: 1px solid #334155; color: #f8fafc; }
        .theme-muted { color: #94a3b8; }
        """
    return """
    :root { color-scheme: light; }
    .theme-shell { background: #f8fafc; color: #111827; }
    .theme-card { background: #ffffff; border: 1px solid #e2e8f0; color: #111827; }
    .theme-muted { color: #475569; }
    """


def today_iso() -> str:
    return date.today().strftime("%Y-%m-%d")


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def build_ship_search_index(ships: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed = []
    for ship in ships:
        searchable = " ".join(
            [
                sanitize_text_input(ship.get("ship_name", "")),
                sanitize_text_input(ship.get("classification_number", "")),
                sanitize_text_input(ship.get("imo_number", "")),
                sanitize_text_input(ship.get("former_name", "")),
                sanitize_text_input(ship.get("flag", "")),
                sanitize_text_input(ship.get("call_sign", "")),
                sanitize_text_input(ship.get("owner", "")),
                sanitize_text_input(ship.get("ship_type", "")),
                sanitize_text_input(ship.get("purpose", "")),
                sanitize_text_input(ship.get("port_of_registry", "")),
            ]
        ).lower()
        indexed.append({**ship, "search_text": searchable})
    return indexed


def filter_ships(ships: list[dict[str, Any]], query: str = "", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    filters = filters or {}
    query = sanitize_text_input(query).lower()
    indexed = build_ship_search_index(ships)
    result = []
    for ship in indexed:
        if query and query not in ship.get("search_text", ""):
            continue
        if filters:
            for key, value in filters.items():
                if not value:
                    continue
                if sanitize_text_input(ship.get(key, "")).lower() != sanitize_text_input(value).lower():
                    continue
            else:
                pass
        result.append(ship)
    return result


def build_notification_payload(recipient: str, event_type: str, message: str, priority: str = "Normal") -> dict[str, Any]:
    return {
        "recipient": sanitize_text_input(recipient),
        "event_type": sanitize_text_input(event_type),
        "message": sanitize_text_input(message),
        "priority": sanitize_text_input(priority),
        "created_on": now_iso(),
        "status": "Pending",
    }


def create_default_survey_checklist(survey_type: str) -> list[dict[str, Any]]:
    return [
        {
            "section": "General",
            "subsection": survey_type,
            "checklist_item": "Document Review",
            "inspection_requirement": "Review applicable reports and certificates",
            "observation": "",
            "status": "Pending",
            "remarks": "",
            "photo_required": False,
            "document_required": True,
            "gps_required": False,
            "inspector_name": "",
            "survey_date": today_iso(),
            "digital_signature": "",
            "completion_pct": 0,
        }
    ]


def build_dashboard_summary(ships: list[dict[str, Any]], surveys: list[dict[str, Any]], certificates: list[dict[str, Any]], notifications: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ships": len(ships),
        "surveys": len(surveys),
        "certificates": len(certificates),
        "notifications": len(notifications),
        "pending_work": sum(1 for item in surveys if sanitize_text_input(item.get("status", "")).lower() in {"pending", "in progress"}),
        "overdue_work": sum(1 for item in surveys if sanitize_text_input(item.get("status", "")).lower() == "overdue"),
    }
