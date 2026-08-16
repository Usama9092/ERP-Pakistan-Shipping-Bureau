from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQL = (ROOT / "database" / "production_v4_1_4_stakeholder_registry.sql").read_text()
PQ = (ROOT / "database" / "production_queries.py").read_text()
PW = (ROOT / "components" / "project_workspace_v40.py").read_text()
GM = (ROOT / "components" / "gm_production.py").read_text()
UI = (ROOT / "components" / "stakeholder_registry.py").read_text()
DEMO = (ROOT / "database" / "demo_queries_v40.py").read_text()

def test_registry_table_and_types_exist():
    assert "create table if not exists stakeholder_registry" in SQL
    for token in ["owner", "designer", "ship_management", "shipyard"]:
        assert token in SQL

def test_gm_only_create_and_list_rpc_exist():
    assert "epas_create_stakeholder" in SQL
    assert "Only GM Classification may create stakeholders" in SQL
    assert "epas_list_stakeholder_registry" in SQL

def test_project_links_registry_snapshot():
    assert "registry_id" in SQL
    assert "Selected stakeholder type does not match requested project role" in SQL
    assert "stakeholders(project_id,company_name" in SQL

def test_projects_tab_has_peer_create_stakeholder_action():
    assert "+ Create New Stakeholder" in PW
    assert "gm_create_stakeholder_open" in PW

def test_create_project_uses_registered_stakeholders():
    assert "stakeholder_registry_v414" in GM
    assert "registry_id" in GM
    assert "Select registered stakeholder organizations" in GM

def test_stakeholder_page_has_all_four_types():
    assert "Create New Stakeholder" in UI
    for label in ["Owner", "Designer", "Ship Management", "Shipyard"]:
        assert label in UI

def test_demo_supports_registry_and_project_selection():
    assert "stakeholder_registry_v414" in DEMO
    assert "create_stakeholder_v414" in DEMO
    assert "registry_id" in DEMO
