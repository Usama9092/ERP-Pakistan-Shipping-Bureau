"""Streamlit Community Cloud entry point for EPAS."""
from pathlib import Path
import os
import runpy
import sys

# Deployment revision: 2026-08-28-plan-appraisal-users-api
# Kept at the Cloud entry point so plan-appraisal source changes trigger a
# complete application rebuild instead of reusing a stale worker image.
APP_DIR = Path(__file__).resolve().parent / "work_stakeholder" / "epas_v39_edit"
os.chdir(APP_DIR)
sys.path.insert(0, str(APP_DIR))
runpy.run_path(str(APP_DIR / "app.py"), run_name="__main__")
