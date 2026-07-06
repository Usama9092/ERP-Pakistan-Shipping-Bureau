from __future__ import annotations

from typing import Any, Callable

import streamlit as st

from maritime_integration import (
    render_certificate_management,
    render_maritime_dashboard,
    render_notification_center,
    render_security_summary,
    render_ship_registry,
    render_survey_checklist_editor,
)
from modules.maritime import MODULE_INFO, SURVEY_TYPES
from modules.registry import ModuleRegistry


def register_module(
    registry: ModuleRegistry,
    page_handlers: dict[str, Callable[[dict], None]] | None = None,
    dependencies: dict[str, object] | None = None,
) -> None:
    """Register maritime module pages with the main app registry."""
    registry.register_module(MODULE_INFO)

    if dependencies is None or "db_all" not in dependencies:
        raise ValueError("Maritime module requires a 'db_all' dependency.")

    db_all = dependencies["db_all"]

    def maritime_registry_page(actor: dict) -> None:
        ships = []
        try:
            ships = db_all("ships").to_dict("records") if not db_all("ships").empty else []
        except Exception:
            ships = []

        render_maritime_dashboard(
            ships,
            db_all("ship_surveys").to_dict("records") if not db_all("ship_surveys").empty else [],
            db_all("ship_certificates").to_dict("records") if not db_all("ship_certificates").empty else [],
            db_all("maritime_notifications").to_dict("records") if not db_all("maritime_notifications").empty else [],
        )
        render_ship_registry(ships)
        render_security_summary()

    def maritime_survey_center_page(actor: dict) -> None:
        survey_type = st.selectbox("Survey Type", SURVEY_TYPES)
        render_survey_checklist_editor(survey_type)
        notifications = db_all("maritime_notifications").to_dict("records") if not db_all("maritime_notifications").empty else []
        certificates = db_all("ship_certificates").to_dict("records") if not db_all("ship_certificates").empty else []
        render_notification_center(notifications)
        render_certificate_management(certificates)

    handlers = page_handlers or {
        "maritime_registry": maritime_registry_page,
        "maritime_surveys": maritime_survey_center_page,
    }
    registry.register_page("Maritime Registry", handlers["maritime_registry"], module_name=MODULE_INFO["name"])
    registry.register_page("Maritime Surveys", handlers["maritime_surveys"], module_name=MODULE_INFO["name"])
