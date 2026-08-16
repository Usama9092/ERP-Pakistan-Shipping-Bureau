from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "app.py").read_text()
PW = (ROOT / "components/project_workspace_v40.py").read_text()
AUTH = (ROOT / "components/auth_gate.py").read_text()


def _sidebar_block() -> str:
    start = PW.index("with st.sidebar:")
    end = PW.index("st.markdown(\n        f\"<div class='psb-project-breadcrumb", start)
    return PW[start:end]


def test_global_navigation_is_vertical_sidebar():
    assert "with st.sidebar:" in APP
    assert "horizontal=True" not in APP
    assert "GLOBAL NAVIGATION" in APP


def test_global_signout_is_last_sidebar_action():
    nav_pos = APP.index("GLOBAL NAVIGATION")
    signout_pos = APP.index("Sign out", nav_pos)
    assert signout_pos > nav_pos


def test_project_sidebar_contains_only_navigation_controls():
    sidebar = _sidebar_block()
    assert "psb-project-sidebar-project" not in sidebar
    assert "PROJECT SUMMARY" not in sidebar
    assert "Project ID" not in sidebar
    assert "PROJECT NAVIGATION" in sidebar


def test_project_sidebar_has_change_project_then_signout():
    block = _sidebar_block()
    assert block.index("Change Project") < block.index("Sign out")


def test_auth_gate_does_not_render_duplicate_sidebar_signout():
    assert "with st.sidebar" not in AUTH
    assert "Sign out" not in AUTH


def test_project_nav_is_phase_aware():
    assert "plan_appraisal" in PW and "nsc_survey" in PW and "in_service" in PW
    assert 'if value == "plan_appraisal" and "plan_appraisal" not in phases' in PW
    assert 'if value == "nsc_survey" and "nsc_survey" not in phases' in PW
    assert 'if value == "in_service" and "in_service" not in phases' in PW


def test_hidden_legacy_project_info_cannot_reappear_as_project_nav():
    assert 'if current not in values.values()' in PW
    assert 'current = "overview"' in PW
