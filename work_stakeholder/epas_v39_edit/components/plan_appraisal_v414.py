"""Versioned Plan Appraisal entrypoint for the production project workspace.

v4.2 uses the production-only professional Plan Appraisal surface. It keeps the
real Supabase workflow while presenting the controlled drawing register and
revision dossier with a classification-society-grade interface.
"""
from components.plan_appraisal_pro import render

__all__ = ["render"]
