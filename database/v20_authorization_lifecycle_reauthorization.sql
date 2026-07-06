
-- V20 Authorization Lifecycle & Reauthorization Management
-- Apply after previous schema files.
create table if not exists authorization_lifecycle_v20 (
  lifecycle_id text primary key, user_id text, person_name text, role_name text,
  authorization_scope text, authorization_domain text, state text, issue_date text, expiry_date text,
  days_remaining integer, refresher_due_date text, monitoring_due_date text,
  cpd_required_hours numeric, cpd_completed_hours numeric, last_activity_date text, activity_count integer,
  risk_color text, next_action text, owner_role text, created_on text, updated_on text
);
create index if not exists idx_auth_lifecycle_v20_user on authorization_lifecycle_v20(user_id);
create index if not exists idx_auth_lifecycle_v20_state on authorization_lifecycle_v20(state);

create table if not exists refresher_requirements_v20 (
  requirement_id text primary key, target_role text, authorization_scope text, trigger_type text,
  trigger_days_before_expiry integer, mandatory_courses text, mandatory_mcq text,
  minimum_score numeric, cpd_hours_required numeric, rule_update_training_required text,
  technical_interview_required text, practical_monitoring_required text, created_by text, created_on text
);

create table if not exists cpd_records_v20 (
  cpd_id text primary key, user_id text, person_name text, activity_type text, title text,
  provider text, date_completed text, hours numeric, linked_scope text, evidence_link text,
  approved_by text, status text, created_on text
);
create index if not exists idx_cpd_v20_user on cpd_records_v20(user_id);

create table if not exists monitoring_schedule_v20 (
  monitoring_id text primary key, user_id text, person_name text, role_name text,
  authorization_scope text, monitoring_type text, due_date text, monitor_id text, monitor_name text,
  status text, score numeric, finding_summary text, corrective_action text, closure_status text,
  created_on text, updated_on text
);
create index if not exists idx_monitoring_v20_user on monitoring_schedule_v20(user_id);

create table if not exists competency_board_reviews_v20 (
  review_id text primary key, board_period text, user_id text, person_name text, role_name text,
  scope_reviewed text, evidence_pack_status text, refresher_status text, cpd_status text,
  monitoring_status text, performance_status text, board_decision text, restriction_action text,
  suspension_action text, remarks text, reviewed_by text, created_on text
);

create table if not exists rule_update_training_impact_v20 (
  impact_id text primary key, source_type text, rule_reference text, change_summary text,
  affected_roles text, affected_scopes text, required_training text, required_mcq text,
  due_date text, notification_status text, completion_status text, created_by text, created_on text
);

create table if not exists authorization_lifecycle_policy_v20 (
  policy_id text primary key, policy_name text, applies_to_roles text, rule_statement text,
  trigger_condition text, system_action text, escalation_to text, status text, created_on text
);
