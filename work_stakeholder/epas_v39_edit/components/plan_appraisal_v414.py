"""Versioned Plan Appraisal entrypoint for the v4.1.4 Cloud deployment.

The compatibility guard is deliberately applied before importing the main
component so a rolling Streamlit worker cannot fail on the historic
``list_users`` query name.
"""
from database import production_queries as _production_queries

if not hasattr(_production_queries, "list_users"):
    _production_queries.list_users = _production_queries.users

from components.plan_appraisal import render

__all__ = ["render"]

