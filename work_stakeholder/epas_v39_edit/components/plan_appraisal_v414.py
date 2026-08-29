"""Versioned Plan Appraisal entrypoint for the production project workspace.

v4.2 intentionally uses the production-only real Plan Appraisal surface. The
legacy demo-capable component remains in the repository for archived migration
coverage but is not rendered by the active project workspace.
"""
from components.plan_appraisal_real import render

__all__ = ["render"]
