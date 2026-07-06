-- V19 Rule Development Automation Layer
-- Apply in Supabase/PostgreSQL after base schema.
create table if not exists rule_development_projects_v19 (
    project_id text primary key,
    source_type text,
    source_reference text,
    title text,
    reason_for_change text,
    affected_rules text,
    affected_domains text,
    risk_level text,
    technical_owner text,
    qmr_reviewer text,
    document_controller text,
    target_effective_date text,
    status text,
    created_by text,
    created_at text,
    updated_at text
);
create table if not exists rule_impact_assessments_v19 (
    impact_id text primary key,
    project_id text,
    impacted_area text,
    impact_summary text,
    affected_roles text,
    affected_documents text,
    training_required text,
    system_update_required text,
    client_notification_required text,
    flag_notification_required text,
    priority text,
    due_date text,
    owner_role text,
    status text,
    created_at text
);
create table if not exists rule_approval_workflow_v19 (
    approval_id text primary key,
    project_id text,
    step_name text,
    owner_role text,
    reviewer_role text,
    approver_role text,
    decision text,
    decision_date text,
    comments text,
    evidence_link text,
    created_at text
);
create table if not exists rule_training_actions_v19 (
    action_id text primary key,
    project_id text,
    training_title text,
    target_roles text,
    assessment_required text,
    due_date text,
    completion_status text,
    generated_by text,
    created_at text
);
create table if not exists rule_communication_log_v19 (
    log_id text primary key,
    project_id text,
    recipient_group text,
    channel text,
    subject text,
    message text,
    status text,
    sent_on text,
    acknowledgement_required text,
    created_at text
);
create table if not exists rule_release_register_v19 (
    release_id text primary key,
    project_id text,
    document_id text,
    revision_no text,
    release_status text,
    released_by text,
    release_date text,
    supersedes text,
    acknowledgement_status text,
    qr_or_link text,
    created_at text
);
create index if not exists idx_rule_project_status_v19 on rule_development_projects_v19(status, risk_level);
create index if not exists idx_rule_impact_project_v19 on rule_impact_assessments_v19(project_id, status);
create index if not exists idx_rule_approval_project_v19 on rule_approval_workflow_v19(project_id, decision);
create index if not exists idx_rule_training_project_v19 on rule_training_actions_v19(project_id, completion_status);
create index if not exists idx_rule_comm_project_v19 on rule_communication_log_v19(project_id, status);
create index if not exists idx_rule_release_project_v19 on rule_release_register_v19(project_id, release_status);
