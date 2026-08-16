"""
EPAS · GM Dashboard — Settings & Domain Constants
--------------------------------------------------
Every enum in this file corresponds directly to a node or decision
in the GM workflow chart. Keeping them centralised means the wizard,
the RFI queue, the certificate engine and the ship register all speak
the same vocabulary — a status string typed in one component will
never silently mismatch another.
"""

from __future__ import annotations

APP_NAME = "Pakistan Shipping Bureau"
APP_TAGLINE = "Classification, Survey & Maritime Safety Management System"
ORG_NAME = "Pakistan Shipping Bureau"
APP_VERSION = "4.1.1-PSB"

# --------------------------------------------------------------------------
# Project phases  (Project Creation Wizard → Step 5 selection)
# --------------------------------------------------------------------------
PHASE_PLAN_APPRAISAL = "plan_appraisal"
PHASE_NSC_SURVEY = "nsc_survey"
PHASE_IN_SERVICE = "in_service"

PHASE_LABELS = {
    PHASE_PLAN_APPRAISAL: "Plan Appraisal",
    PHASE_NSC_SURVEY: "NSC Survey",
    PHASE_IN_SERVICE: "In-Service Surveys",
}

PHASE_ICONS = {
    PHASE_PLAN_APPRAISAL: "📐",
    PHASE_NSC_SURVEY: "🏗️",
    PHASE_IN_SERVICE: "⚓",
}

# Ordered — governs left-to-right tab order in the Project Workspace
ALL_PHASES = [PHASE_PLAN_APPRAISAL, PHASE_NSC_SURVEY, PHASE_IN_SERVICE]

# --------------------------------------------------------------------------
# Project status (top of funnel, shown in Projects List View)
# --------------------------------------------------------------------------
PROJECT_STATUS_ACTIVE = "active"
PROJECT_STATUS_CLOSED = "closed"
PROJECT_STATUS_ON_HOLD = "on_hold"

PROJECT_STATUS_LABELS = {
    PROJECT_STATUS_ACTIVE: "Active",
    PROJECT_STATUS_CLOSED: "Closed",
    PROJECT_STATUS_ON_HOLD: "On Hold",
}

# --------------------------------------------------------------------------
# RFI lifecycle — this is the exact left-to-right spine of the flowchart:
#
#   Pending Allocation → Allocated to DM → Survey Execution →
#   Observations Logged → Pending GM Approval → (Send Back | Approved) →
#   Certificate Issued / Closed
# --------------------------------------------------------------------------
RFI_PENDING_ALLOCATION = "pending_allocation"
RFI_ALLOCATED = "allocated_to_dm"
RFI_SURVEY_IN_PROGRESS = "survey_in_progress"
RFI_OBSERVATIONS_LOGGED = "observations_logged"          # DM reviewing
RFI_PENDING_GM_APPROVAL = "pending_gm_approval"           # forwarded by DM
RFI_SENT_BACK = "sent_back_for_rework"                    # GM sent back
RFI_APPROVED_CLEAN = "approved_no_observations"           # GM approved, no obs
RFI_APPROVED_WITH_OBS = "approved_with_observations"      # GM approved, obs open
RFI_CERT_ISSUED = "certificate_issued"
RFI_CLOSED = "closed"

RFI_STAGE_ORDER = [
    RFI_PENDING_ALLOCATION,
    RFI_ALLOCATED,
    RFI_SURVEY_IN_PROGRESS,
    RFI_OBSERVATIONS_LOGGED,
    RFI_PENDING_GM_APPROVAL,
    RFI_APPROVED_CLEAN,          # branches merge back into the same track
    RFI_CERT_ISSUED,
]

RFI_STAGE_LABELS = {
    RFI_PENDING_ALLOCATION: "Pending Allocation",
    RFI_ALLOCATED: "Allocated to DM",
    RFI_SURVEY_IN_PROGRESS: "Survey in Progress",
    RFI_OBSERVATIONS_LOGGED: "Observations Logged",
    RFI_PENDING_GM_APPROVAL: "Pending GM Approval",
    RFI_SENT_BACK: "Returned for Rework",
    RFI_APPROVED_CLEAN: "Approved — Clean",
    RFI_APPROVED_WITH_OBS: "Approved — Open Observations",
    RFI_CERT_ISSUED: "Certificate Issued",
    RFI_CLOSED: "Closed",
}

# Which stages require GM action right now (drives the "Needs You" filter)
RFI_GM_ACTIONABLE = {RFI_PENDING_ALLOCATION, RFI_PENDING_GM_APPROVAL}

RFI_TYPES = {
    PHASE_NSC_SURVEY: ["HATS", "SATS", "FTP", "ITP", "Final NSC Survey"],
    PHASE_IN_SERVICE: ["Annual Survey", "Intermediate Survey", "Class Renewal", "Change of Class", "Docking Survey"],
}

# --------------------------------------------------------------------------
# Observations
# --------------------------------------------------------------------------
OBS_OPEN = "open"
OBS_CLEARED = "cleared"

OBS_SEVERITY = ["Minor", "Major", "Critical"]

# --------------------------------------------------------------------------
# Certificates
# --------------------------------------------------------------------------
CERT_TYPE_CLASS = "class_certificate"
CERT_TYPE_INTERIM = "interim_certificate"
CERT_TYPE_NSC = "nsc_certificate"

CERT_TYPE_LABELS = {
    CERT_TYPE_CLASS: "Class Certificate",
    CERT_TYPE_INTERIM: "Interim Certificate of Class",
    CERT_TYPE_NSC: "New Construction Certificate",
}

CERT_TYPE_PREFIX = {
    CERT_TYPE_CLASS: "CC",
    CERT_TYPE_INTERIM: "ICC",
    CERT_TYPE_NSC: "NCC",
}

CERT_STATUS_ACTIVE = "active"
CERT_STATUS_EXPIRED = "expired"
CERT_STATUS_SUPERSEDED = "superseded"

# Default full validity (months) offered when NO open observations exist
CERT_VALIDITY_DEFAULT_MONTHS = {
    "Annual Survey": 12,
    "Intermediate Survey": 24,
    "Class Renewal": 60,
    "Change of Class": 60,
    "Docking Survey": 12,
    "HATS": 60,
    "SATS": 60,
    "FTP": 60,
    "ITP": 60,
    "Final NSC Survey": 60,
}

# Interim validity choices — GM sets this manually (per flowchart)
INTERIM_VALIDITY_OPTIONS_MONTHS = [1, 3, 6, 9, 12]

# Certificate expiring-soon threshold (Certificates tab widget)
CERT_EXPIRING_SOON_DAYS = 60

# --------------------------------------------------------------------------
# Roles (internal team + external stakeholders, per wizard Steps 4 & 5)
# --------------------------------------------------------------------------
ROLE_GM = "gm"
ROLE_DM = "dm"
ROLE_ENGINEER = "engineer"
ROLE_SURVEYOR = "surveyor"
ROLE_DESIGNER = "designer"
ROLE_OWNER = "owner"
ROLE_SHIP_MANAGEMENT = "ship_management"
ROLE_SHIPYARD = "shipyard"

INTERNAL_TEAM_ROLES = [ROLE_GM, ROLE_DM, ROLE_ENGINEER, ROLE_SURVEYOR]
# External parties are stakeholder accounts. They are NOT internal classification
# personnel. Designer and Ship Management may execute only explicitly assigned
# workflow tasks; Owner and Shipyard are read-only stakeholder users unless a
# future controlled task type is introduced.
EXTERNAL_STAKEHOLDER_ROLES = [ROLE_OWNER, ROLE_DESIGNER, ROLE_SHIP_MANAGEMENT, ROLE_SHIPYARD]
STAKEHOLDER_EXECUTION_ROLES = [ROLE_DESIGNER, ROLE_SHIP_MANAGEMENT]
STAKEHOLDER_READONLY_ROLES = [ROLE_OWNER, ROLE_SHIPYARD]

ROLE_LABELS = {
    ROLE_GM: "GM Classification",
    ROLE_DM: "Department Manager",
    ROLE_ENGINEER: "Authorised Engineer",
    ROLE_SURVEYOR: "Authorised Surveyor",
    ROLE_DESIGNER: "Designer",
    ROLE_OWNER: "Owner",
    ROLE_SHIP_MANAGEMENT: "Ship Management Co.",
    ROLE_SHIPYARD: "Shipyard",
}

DISCIPLINES = ["Hull & Structure", "Machinery", "Electrical", "Stability", "Safety Equipment", "Fire & LSA"]

# --------------------------------------------------------------------------
# Documents (Step 3 of wizard + Document Detail Panel)
# --------------------------------------------------------------------------
DOC_CATEGORY_CONTRACT = "contract"
DOC_CATEGORY_RULES = "class_rules"
DOC_CATEGORY_TIMELINE = "timeline"
DOC_CATEGORY_DRAWING = "drawing"

DOC_CATEGORY_LABELS = {
    DOC_CATEGORY_CONTRACT: "Contract Documents",
    DOC_CATEGORY_RULES: "Class Rules",
    DOC_CATEGORY_TIMELINE: "Project Timeline",
    DOC_CATEGORY_DRAWING: "Design Drawing",
}

DOC_STATUS_LABELS = {
    "pending_review": "Pending Review",
    "approved": "Approved",
    "amendments_required": "Amendments Required",
    "rejected": "Rejected",
}

# --------------------------------------------------------------------------
# Wizard picklists (Steps 1 & 2)
# --------------------------------------------------------------------------
VESSEL_TYPES = [
    "Patrol Vessel", "Container Feeder", "General Cargo", "Bulk Carrier",
    "Oil / Chemical Tanker", "Offshore Support Vessel", "Passenger Ferry",
    "Tug / Workboat", "Other",
]

COMMON_FLAG_STATES = [
    "Pakistan", "Panama", "Marshall Islands", "Liberia", "Malta",
    "Singapore", "United Kingdom", "Bahamas", "Other",
]

# --------------------------------------------------------------------------
# UI
# --------------------------------------------------------------------------
DATE_FMT = "%d %b %Y"
DATETIME_FMT = "%d %b %Y · %H:%M"

NAV_ITEMS = [
    ("overview", "Overview", "🏛️"),
    ("projects", "Projects", "📁"),
    ("rfi_nsc", "NSC Survey RFIs", "🏗️"),
    ("rfi_in_service", "In-Service RFIs", "⚓"),
    ("certificates", "Certificates", "📜"),
    ("ship_register", "Ship Register", "🧭"),
    ("reports", "Survey Logs & Reports", "📊"),
    ("plan_appraisal", "Plan Appraisal Control", "📐"),
    ("resources", "Authorization & Resources", "🛡️"),
    ("dm_dashboard", "DM Dashboard / Inbox", "👔"),
    ("surveyor_dashboard", "Surveyor Dashboard", "⚓"),
    ("workflow_inbox", "Workflow Inbox", "📥"),
    ("notifications", "Notifications", "🔔"),
    ("governance", "Governance & Closure", "🛡️"),
]
