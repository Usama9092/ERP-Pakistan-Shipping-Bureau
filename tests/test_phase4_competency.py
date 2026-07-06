import pandas as pd

from app import build_competency_matrix_snapshot, build_training_pathway_rule_record, evaluate_reauthorization_readiness


def test_build_training_pathway_rule_record_uses_review_count_schema():
    row = build_training_pathway_rule_record(
        pathway="In-Service Surveyor",
        scope="Annual Survey",
        rule_name="Annual Survey Eligibility",
        required_training_ids=["T1", "T2"],
        min_score=80,
        min_attendance=80,
        require_case_study="Yes",
        require_practical_assignment="Yes",
        required_witness_count=2,
        required_supervised_count=1,
        required_joint_review_count=0,
        required_independent_review_count=1,
        require_technical_interview="Yes",
        validity_months=36,
        created_by="Admin",
        created_on="2026-07-04",
        status="Active",
        remarks="",
    )

    assert row["required_independent_review_count"] == 1
    assert row["required_joint_review_count"] == 0
    assert row["required_training_ids"] == "T1, T2"


def test_evaluate_reauthorization_readiness_recommends_reauthorization_when_criteria_met():
    result = evaluate_reauthorization_readiness(
        cpd_hours=18,
        activity_count=3,
        open_ncr_count=0,
        complaint_count=0,
        requirement={
            "required_cpd_hours": 12,
            "min_activity_count": 2,
            "max_major_ncr": 0,
            "max_client_complaints": 1,
            "require_qmr_clearance": "Yes",
            "require_technical_interview": "Yes",
        },
        qmr_clearance="Cleared",
        technical_interview_status="Passed",
    )

    assert result["can_reauthorize"] is True
    assert result["suggested_decision"] == "Reauthorized"
    assert result["gaps"] == []


def test_build_competency_matrix_snapshot_uses_current_phase4_tables():
    training_records = pd.DataFrame(
        [{"user_id": "U1", "test_status": "Passed", "status": "Completed"}]
    )
    witness_surveys = pd.DataFrame(
        [
            {"user_id": "U1", "scope": "In-Service Surveyor - Hull", "outcome": "Pass"},
            {"user_id": "U1", "scope": "In-Service Surveyor - Hull", "outcome": "Pass"},
        ]
    )
    supervised_activities = pd.DataFrame(
        [{"user_id": "U1", "scope": "In-Service Surveyor - Hull", "activity_kind": "Independent Survey", "outcome": "Pass"}]
    )
    authorization_requests = pd.DataFrame(
        [{"user_id": "U1", "scope": "In-Service Surveyor - Hull", "status": "Management Approved"}]
    )

    result = build_competency_matrix_snapshot(
        user_id="U1",
        scope="In-Service Surveyor - Hull",
        pathway="In-Service Surveyor",
        training_records=training_records,
        witness_records=witness_surveys,
        supervised_records=supervised_activities,
        authorization_requests=authorization_requests,
        development_plans=pd.DataFrame(),
    )

    assert result["training_status"] == "Completed"
    assert result["mcq_status"] == "Passed"
    assert result["witness_completed"] == 2
    assert result["supervised_completed"] == 1
    assert result["authorization_status"] == "Authorized"
    assert result["risk_level"] == "Low"
    assert result["gap_summary"] == "No major gap"
