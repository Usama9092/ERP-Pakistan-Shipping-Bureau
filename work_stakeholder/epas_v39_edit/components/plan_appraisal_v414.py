"""Production Plan Appraisal entrypoint.

Exact controlled route:
Designer -> GM -> Plan Appraisal Manager -> Plan Appraisal Engineer ->
Plan Appraisal Manager -> GM -> Approved package delivered to Designer.
"""
from components.plan_appraisal_routed import render

__all__ = ["render"]
