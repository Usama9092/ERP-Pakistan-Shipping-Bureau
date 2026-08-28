"""Streamlit Community Cloud entry point for EPAS."""
from pathlib import Path
import importlib
import os
import runpy
import sys

# Deployment revision: 2026-08-28-project-plan-appraisal-complete
APP_DIR = Path(__file__).resolve().parent / "work_stakeholder" / "epas_v39_edit"
os.chdir(APP_DIR)
sys.path.insert(0, str(APP_DIR))
importlib.invalidate_caches()
runpy.run_path(str(APP_DIR / "app.py"), run_name="__main__")
