-- Pakistan Shipping Bureau HRDM Supabase RLS Template
-- App creates tables automatically. Use this template after linking Supabase Auth.
-- Enable row level security on all application tables before adding policies.

alter table users enable row level security;
alter table training_modules enable row level security;
alter table trainings enable row level security;
alter table files enable row level security;
alter table training_records enable row level security;
alter table question_bank enable row level security;
alter table assessment_history enable row level security;
alter table competency_matrix enable row level security;
alter table authorization_matrix enable row level security;
alter table development_plans enable row level security;
alter table field_exposure_matrix enable row level security;
alter table witness_surveys enable row level security;
alter table supervised_activities enable row level security;
alter table authorization_requests enable row level security;
alter table authorization_certificates enable row level security;
alter table crb_reviews enable row level security;
alter table annual_reviews enable row level security;
alter table revalidation_requests enable row level security;
alter table job_requests enable row level security;
alter table kpi_records enable row level security;
alter table cpd_records enable row level security;
alter table knowledge_library enable row level security;
alter table knowledge_acknowledgements enable row level security;
alter table rule_library enable row level security;
alter table document_versions enable row level security;
alter table capa_register enable row level security;
alter table notifications enable row level security;
alter table audit_trail enable row level security;
alter table technical_authorities enable row level security;
alter table survey_report_reviews enable row level security;
alter table plan_review_quality enable row level security;
alter table competency_ncrs enable row level security;
alter table authorization_restrictions enable row level security;
alter table client_feedback enable row level security;
alter table succession_plans enable row level security;
alter table workforce_forecasts enable row level security;
alter table accreditation_evidence enable row level security;
alter table technical_interpretations enable row level security;

-- Important:
-- Keep SUPABASE_SERVICE_ROLE_KEY only in Render environment variables.
-- Do not commit service role keys to GitHub.


-- PSB Enterprise extension RLS enablement (adjust policies to your production security model)
alter table if exists competency_requirements enable row level security;
alter table if exists enterprise_gap_analysis enable row level security;
alter table if exists course_versions enable row level security;
alter table if exists case_studies enable row level security;
alter table if exists practical_assignments enable row level security;
alter table if exists technical_interviews enable row level security;
alter table if exists mobile_survey_evidence enable row level security;
alter table if exists stage_acceptances enable row level security;
alter table if exists material_certifications enable row level security;
alter table if exists trial_requests enable row level security;
alter table if exists comment_resolutions enable row level security;
alter table if exists ai_competency_recommendations enable row level security;
alter table if exists audit_readiness_items enable row level security;
alter table if exists workforce_forecasts enable row level security;
alter table if exists role_permission_matrix enable row level security;

-- PSB V4 final world-class tables RLS placeholders
alter table if exists iacs_clause_mapping_v4 enable row level security;
alter table if exists authorization_scope_locks_v4 enable row level security;
alter table if exists technical_interview_scores_v4 enable row level security;
alter table if exists authorized_staff_monitoring_v4 enable row level security;
alter table if exists document_control_register_v4 enable row level security;
alter table if exists audit_evidence_packs_v4 enable row level security;
alter table if exists offline_mobile_sync_v4 enable row level security;
alter table if exists notification_channels_v4 enable row level security;
alter table if exists worldclass_status_v4 enable row level security;


-- V5 Final professional closure controls RLS placeholders
alter table if exists survey_type_authorization_matrix_v5 enable row level security;
alter table if exists plan_domain_authorization_matrix_v5 enable row level security;
alter table if exists authorization_restrictions_v5 enable row level security;
alter table if exists ship_construction_file_v5 enable row level security;
alter table if exists vendor_material_approval_v5 enable row level security;
alter table if exists clause_evidence_mapping_v5 enable row level security;
alter table if exists competency_assignment_locks_v5 enable row level security;
alter table if exists executive_risk_score_v5 enable row level security;
alter table if exists worldclass_activity_gap_closure_v5 enable row level security;


-- V8 Classification Society ERP Governance Layer
create table if not exists erp_role_permissions (permission_id text primary key, role_name text, module_name text, page_name text, can_view text, can_create text, can_review text, can_approve text, can_release text, can_archive text, data_scope text, accountability text, updated_on text);
create table if not exists governance_actions (action_id text primary key, governance_area text, source_module text, source_id text, responsible_role text, responsible_user_id text, responsible_name text, reviewer_role text, approver_role text, status text, due_date text, escalation_level text, decision text, evidence_link text, remarks text, created_on text, closed_on text);
create table if not exists document_control_register (document_id text primary key, document_type text, document_title text, document_number text, revision text, project_or_vessel text, domain text, prepared_by text, reviewed_by text, approved_by text, status text, effective_date text, release_date text, superseded_by text, controlled_copy_holder text, distribution_list text, storage_link text, qr_reference text, created_on text, archived_on text);
create table if not exists erp_tasks (task_id text primary key, task_type text, source_module text, source_id text, assigned_to_role text, assigned_to_user_id text, assigned_to_name text, task_title text, task_description text, priority text, due_date text, status text, reminder_count integer, escalation_level text, created_by text, created_on text, completed_on text);
create table if not exists technical_monitoring_reports (monitoring_id text primary key, monitored_user_id text, monitored_name text, monitored_role text, activity_type text, project_or_vessel text, domain text, observation_date text, monitor_user_id text, monitor_name text, technical_score real, reporting_score real, rule_interpretation_score real, safety_score real, independence_score real, finding_summary text, competency_finding text, improvement_action text, restriction_recommended text, status text, created_on text);
create table if not exists plan_approval_workload (workload_id text primary key, appraiser_id text, appraiser_name text, domain text, open_reviews integer, late_reviews integer, average_turnaround_days real, comments_open integer, comments_closed integer, quality_score real, workload_status text, manager_review text, updated_on text);
create table if not exists survey_assignment_controls (control_id text primary key, request_id text, survey_type text, vessel_project text, candidate_user_id text, candidate_name text, authorized_status text, competency_status text, certificate_valid text, restriction_status text, availability_status text, assignment_decision text, blocked_reason text, checked_by text, checked_on text);
create table if not exists client_owner_requests (request_id text primary key, client_name text, organization text, vessel_project text, request_type text, requested_service text, preferred_date text, location text, certificate_required text, open_ncrs text, status text, assigned_manager text, created_on text, last_update text);
create table if not exists technical_knowledge_repository (knowledge_id text primary key, knowledge_type text, title text, domain text, source_activity text, root_cause text, lesson_learned text, technical_interpretation text, approved_by text, approval_status text, searchable_tags text, visibility text, created_on text, revision text);
create table if not exists practical_development_tracks (track_id text primary key, user_id text, user_name text, pathway text, domain text, witness_1_status text, witness_2_status text, witness_3_status text, supervised_status text, independent_observation_status text, technical_interview_status text, peer_review_status text, monitoring_review_status text, final_readiness text, next_action text, updated_on text);
create table if not exists executive_risk_register (risk_id text primary key, risk_area text, risk_score real, risk_level text, source_summary text, mitigation_owner text, mitigation_plan text, due_date text, status text, created_on text, reviewed_on text);

-- V9 State-of-Art ERP Governance Tables
alter table if exists workflow_quality_gates enable row level security;
alter table if exists uiux_performance_checks enable row level security;
alter table if exists role_accountability_map enable row level security;
-- Service role policies are recommended for server-side Streamlit deployment.

-- V10 suggested RLS policies. Tailor project/client isolation columns to your production data model.
alter table if exists workflow_task_engine_v10 enable row level security;
alter table if exists controlled_transmittals_v10 enable row level security;
alter table if exists survey_logbook_v10 enable row level security;
alter table if exists plan_review_peer_quality_v10 enable row level security;
-- Internal users can see assigned workflow tasks; Admin/CEO/Management can be granted enterprise-wide access by role claims.
-- External Designer/Shipyard/Client Owner access must be restricted by project/client mapping in production.

-- V11 RLS notes: enable according to your Supabase auth mapping.
alter table if exists enterprise_search_index enable row level security;
alter table if exists knowledge_graph_links enable row level security;
alter table if exists ai_competency_advice enable row level security;
alter table if exists lessons_learned enable row level security;
alter table if exists notification_rules enable row level security;
alter table if exists notification_outbox enable row level security;
alter table if exists mobile_sync_register enable row level security;
alter table if exists client_self_service_requests enable row level security;
alter table if exists role_communication_matrix enable row level security;


-- V12 RLS NOTES / POLICY TEMPLATE
-- Apply tenant/project ownership policies before live external access.
-- Suggested tables for strict isolation: client_portal_services, enterprise_messages,
-- mobile_devices, offline_inspection_packages, document_acknowledgements, quotations, invoices.
-- Example pattern:
-- alter table client_portal_services enable row level security;
-- create policy client_own_services on client_portal_services
-- for select using (client_user_id = auth.uid()::text or current_setting('app.role', true) in ('Admin','Management','Survey Operations Manager'));


-- V13 Production-grade international ERP hardening tables
create table if not exists security_policy_controls (control_id text primary key, control_area text, control_name text, requirement text, current_status text, implementation_status text, owner_role text, evidence_record text, risk_level text, target_date text, last_review_on text, created_on text);
create table if not exists external_portal_access_rules (rule_id text primary key, portal_role text, entity_type text, visibility_rule text, allowed_actions text, forbidden_actions text, data_filter_field text, approval_required text, rls_policy_note text, status text, created_on text);
create table if not exists database_enforcement_rules (rule_id text primary key, rule_name text, object_type text, business_rule text, enforcement_layer text, trigger_condition text, block_message text, related_tables text, test_case text, status text, created_on text);
create table if not exists integration_connector_registry (connector_id text primary key, connector_name text, connector_type text, provider text, purpose text, environment_secret_names text, data_direction text, enabled_status text, health_status text, last_health_check text, failure_action text, owner_role text, created_on text);
create table if not exists field_mobile_app_specifications (spec_id text primary key, app_module text, user_role text, offline_capability text, captured_data text, device_permissions text, sync_rule text, validation_rule text, conflict_resolution text, pwa_status text, native_app_status text, created_on text);
create table if not exists production_test_cases (test_id text primary key, test_area text, role_name text, scenario text, expected_result text, actual_result text, priority text, status text, tested_by text, tested_on text, defect_ref text, release_blocker text, created_on text);
create table if not exists enterprise_workflow_sla_rules (sla_id text primary key, workflow_type text, task_type text, owner_role text, due_hours integer, reminder_hours integer, escalation_hours integer, escalation_to_role text, auto_block_rule text, closure_evidence_required text, status text, created_on text);
create table if not exists uiux_page_quality_register (page_id text primary key, page_name text, primary_roles text, purpose text, ux_status text, performance_status text, mobile_status text, accessibility_status text, improvement_action text, priority text, owner_role text, created_on text);
create table if not exists enterprise_release_readiness_checks (check_id text primary key, readiness_area text, check_item text, required_for_go_live text, current_status text, evidence text, risk_if_missing text, owner_role text, target_status text, created_on text);
create index if not exists idx_security_policy_area on security_policy_controls(control_area);
create index if not exists idx_portal_access_role on external_portal_access_rules(portal_role);
create index if not exists idx_db_enforcement_object on database_enforcement_rules(object_type);
create index if not exists idx_connector_type on integration_connector_registry(connector_type);
create index if not exists idx_mobile_spec_role on field_mobile_app_specifications(user_role);
create index if not exists idx_test_role_status on production_test_cases(role_name, status);
create index if not exists idx_sla_workflow on enterprise_workflow_sla_rules(workflow_type);
create index if not exists idx_uiux_page_name on uiux_page_quality_register(page_name);
create index if not exists idx_release_area on enterprise_release_readiness_checks(readiness_area);

-- V14 External portal isolation examples. Adapt tenant field names to your real project/client/designer tables.
-- Designer: own project/drawing records only
-- create policy designer_own_drawings on drawings for select using (designer_id = auth.uid()::text);
-- Shipyard: own shipyard/project records only
-- create policy shipyard_own_projects on inspection_requests for select using (shipyard_id = auth.uid()::text);
-- Client/Owner: own vessels/certificates/invoices only
-- create policy client_own_certificates on certificates for select using (client_id = auth.uid()::text);
-- Audit logs: append-only, no normal delete/update.
-- create policy audit_insert_only on audit_logs for insert with check (true);

-- V15 portal isolation examples. Replace auth.uid() mapping with your users table relationship.
ALTER TABLE IF EXISTS finance_commercial_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS customer_support_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS external_party_access_register ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS manufacturer_vendor_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS subcontracted_surveyor_records ENABLE ROW LEVEL SECURITY;

-- Admin/management policies should be added using your production role claim strategy.
-- External users must only see records where related_client_id / vendor_id / surveyor_id matches their mapped profile.

