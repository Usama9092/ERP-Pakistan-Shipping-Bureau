-- PostgreSQL schema for Pakistan Shipping Bureau HRDM Training System
-- This schema reflects the application tables and recommended indexes.

set search_path = public;

-- Core user and training tables
create table if not exists users (
    user_id text primary key,
    name text,
    role text,
    trainee_path text,
    department text,
    assigned_duty text,
    email text unique,
    login_id text unique,
    password_hash text,
    temp_password text,
    status text,
    availability text,
    current_location text,
    mentor_id text,
    mentor_name text,
    competency_level text,
    created_on text,
    last_login text
);

create table if not exists training_modules (
    module_id text primary key,
    title text,
    module_group text,
    target_path text,
    mandatory text,
    refresher_required text,
    cpd_hours real,
    validity_months integer,
    added_by text,
    created_on text
);

create table if not exists trainings (
    training_id text primary key,
    module_id text,
    title text,
    category text,
    standards text,
    target_roles text,
    target_paths text,
    trainer_id text,
    trainer_name text,
    slides_link text,
    video_link text,
    reference_link text,
    scorm_package_link text,
    lms_course_id text,
    schedule_date text,
    schedule_time text,
    meeting_link text,
    recording_link text,
    passing_marks integer,
    validity_months integer,
    max_attempts integer,
    retest_wait_days integer,
    status text,
    created_on text,
    updated_on text,
    foreign key (module_id) references training_modules(module_id),
    foreign key (trainer_id) references users(user_id)
);

create table if not exists files (
    file_id text primary key,
    owner_user_id text,
    owner_name text,
    linked_table text,
    linked_id text,
    category text,
    file_name text,
    file_ext text,
    mime_type text,
    storage_provider text,
    storage_path text,
    public_url text,
    extracted_text text,
    ocr_status text,
    review_status text,
    created_on text,
    updated_on text,
    foreign key (owner_user_id) references users(user_id)
);

create table if not exists training_records (
    record_id text primary key,
    user_id text,
    name text,
    role text,
    trainee_path text,
    training_id text,
    training_title text,
    status text,
    slides_opened text,
    video_opened text,
    live_attendance text,
    recording_opened text,
    lms_completed text,
    test_status text,
    score real,
    passing_marks integer,
    certificate_status text,
    certificate_link text,
    due_date text,
    completed_on text,
    progress integer,
    remarks text,
    mandatory_training text,
    exam_started_on text,
    exam_submitted_on text,
    exam_violation text,
    exam_answers_json text,
    exam_autosaved_on text,
    exam_question_order_json text,
    updated_on text,
    foreign key (user_id) references users(user_id),
    foreign key (training_id) references trainings(training_id)
);

create table if not exists question_bank (
    question_id text primary key,
    training_id text,
    question text,
    option_a text,
    option_b text,
    option_c text,
    option_d text,
    correct_answer text,
    marks integer,
    difficulty_level text,
    question_category text,
    learning_objective text,
    explanation text,
    reference_source text,
    quality_score integer,
    quality_status text,
    mcq_generation_mode text,
    generated_on text,
    foreign key (training_id) references trainings(training_id)
);

create table if not exists assessment_history (
    assessment_id text primary key,
    user_id text,
    name text,
    training_id text,
    training_title text,
    attempt_no integer,
    score real,
    result text,
    attempted_on text,
    next_retest_allowed text,
    remarks text,
    duration_minutes integer,
    violation text,
    answers_json text,
    foreign key (user_id) references users(user_id),
    foreign key (training_id) references trainings(training_id)
);

create table if not exists competency_matrix (
    competency_id text primary key,
    user_id text,
    name text,
    role text,
    trainee_path text,
    area text,
    competency_level text,
    scope text,
    job_type text,
    required_training_ids text,
    required_witness_count integer,
    required_supervised_count integer,
    required_joint_plan_count integer,
    required_independent_plan_count integer,
    required_level_for_auth text,
    status text,
    expiry_date text,
    evidence text,
    created_on text,
    updated_on text,
    foreign key (user_id) references users(user_id)
);

create table if not exists authorization_matrix (
    matrix_id text primary key,
    scope text,
    job_type text,
    required_witness_count integer,
    required_supervised_count integer,
    required_joint_plan_count integer,
    required_independent_plan_count integer,
    required_level_for_auth text,
    minimum_job_level text,
    risk_category text,
    validity_months integer,
    active text
);

create table if not exists development_plans (
    plan_id text primary key,
    user_id text,
    name text,
    trainee_path text,
    mentor_id text,
    mentor_name text,
    competency_scope text,
    month_no integer,
    activity text,
    target_date text,
    status text,
    mentor_comments text,
    created_on text,
    updated_on text,
    foreign key (user_id) references users(user_id),
    foreign key (mentor_id) references users(user_id)
);

create table if not exists field_exposure_matrix (
    exposure_id text primary key,
    user_id text,
    name text,
    trainee_path text,
    scope text,
    activity_type text,
    required_count integer,
    completed_count integer,
    status text,
    updated_on text,
    foreign key (user_id) references users(user_id)
);

create table if not exists witness_surveys (
    witness_id text primary key,
    user_id text,
    name text,
    trainee_path text,
    tutor_id text,
    tutor_name text,
    vessel_or_project text,
    job_type text,
    scope text,
    witness_date text,
    location text,
    technical_knowledge integer,
    rule_application integer,
    safety_awareness integer,
    communication integer,
    report_quality integer,
    professional_conduct integer,
    outcome text,
    comments text,
    status text,
    created_on text,
    updated_on text,
    foreign key (user_id) references users(user_id),
    foreign key (tutor_id) references users(user_id)
);

create table if not exists supervised_activities (
    supervised_id text primary key,
    user_id text,
    name text,
    trainee_path text,
    tutor_id text,
    tutor_name text,
    activity_kind text,
    vessel_or_project text,
    job_type text,
    scope text,
    activity_date text,
    location text,
    preparation integer,
    execution_quality integer,
    findings_quality integer,
    reporting_quality integer,
    rule_compliance integer,
    outcome text,
    comments text,
    status text,
    created_on text,
    updated_on text,
    foreign key (user_id) references users(user_id),
    foreign key (tutor_id) references users(user_id)
);

create table if not exists authorization_requests (
    authorization_id text primary key,
    user_id text,
    name text,
    trainee_path text,
    job_type text,
    scope text,
    competency_id text,
    status text,
    tutor_remarks text,
    tutor_signature text,
    tutor_signed_on text,
    principal_remarks text,
    principal_signature text,
    principal_signed_on text,
    technical_remarks text,
    technical_signature text,
    technical_signed_on text,
    qms_remarks text,
    qms_signature text,
    qms_signed_on text,
    crb_decision text,
    crb_remarks text,
    management_remarks text,
    management_signature text,
    management_signed_on text,
    expiry_date text,
    certificate_id text,
    certificate_html text,
    certificate_storage_link text,
    qr_data_uri text,
    created_on text,
    updated_on text,
    foreign key (user_id) references users(user_id),
    foreign key (competency_id) references competency_matrix(competency_id)
);

create table if not exists authorization_certificates (
    certificate_id text primary key,
    authorization_id text,
    user_id text,
    name text,
    scope text,
    job_type text,
    issue_date text,
    expiry_date text,
    certificate_html text,
    qr_data_uri text,
    storage_link text,
    verification_url text,
    status text,
    certificate_level text,
    signature_snapshot_json text,
    created_on text,
    foreign key (authorization_id) references authorization_requests(authorization_id),
    foreign key (user_id) references users(user_id)
);

create table if not exists training_certificates (
    certificate_id text primary key,
    record_id text,
    training_id text,
    user_id text,
    name text,
    role text,
    training_title text,
    certificate_type text,
    issue_date text,
    completion_date text,
    refresher_due_date text,
    score real,
    result text,
    certificate_html text,
    qr_data_uri text,
    verification_url text,
    status text,
    created_on text,
    updated_on text,
    foreign key (record_id) references training_records(record_id),
    foreign key (training_id) references trainings(training_id),
    foreign key (user_id) references users(user_id)
);


create table if not exists digital_signatures (
    signature_id text primary key,
    user_id text,
    signer_name text,
    role text,
    title text,
    signature_data_uri text,
    stamp_data_uri text,
    applies_to_levels text,
    certificate_usage text,
    is_active text default 'Yes',
    uploaded_by text,
    uploaded_on text,
    remarks text,
    foreign key (user_id) references users(user_id)
);

create table if not exists crb_reviews (
    crb_id text primary key,
    authorization_id text,
    user_id text,
    name text,
    scope text,
    review_date text,
    tutor_decision text,
    technical_decision text,
    qmr_decision text,
    management_decision text,
    final_decision text,
    remarks text,
    signed_by text,
    created_on text,
    foreign key (authorization_id) references authorization_requests(authorization_id),
    foreign key (user_id) references users(user_id)
);

create table if not exists annual_reviews (
    review_id text primary key,
    user_id text,
    name text,
    scope text,
    review_year integer,
    training_status text,
    kpi_status text,
    complaint_status text,
    capa_status text,
    decision text,
    reviewer text,
    review_date text,
    remarks text,
    foreign key (user_id) references users(user_id)
);

create table if not exists revalidation_requests (
    revalidation_id text primary key,
    authorization_id text,
    user_id text,
    name text,
    scope text,
    refresher_training_status text,
    annual_review_status text,
    kpi_review_status text,
    tutor_confirmation text,
    crb_status text,
    final_status text,
    due_date text,
    created_on text,
    updated_on text,
    foreign key (authorization_id) references authorization_requests(authorization_id),
    foreign key (user_id) references users(user_id)
);

create table if not exists job_requests (
    job_id text primary key,
    job_title text,
    job_type text,
    required_scope text,
    vessel_name text,
    imo_number text,
    location text,
    planned_date text,
    priority text,
    risk_level text,
    minimum_level text,
    status text,
    created_by text,
    assigned_user_id text,
    assigned_user_name text,
    assignment_reason text,
    created_on text,
    updated_on text,
    foreign key (assigned_user_id) references users(user_id)
);

create table if not exists kpi_records (
    kpi_id text primary key,
    user_id text,
    name text,
    period text,
    surveys_done integer,
    plans_reviewed integer,
    audits_done integer,
    reports_overdue integer,
    ncr_count integer,
    client_feedback real,
    training_compliance real,
    utilization_percent real,
    kpi_score real,
    created_on text,
    remarks text,
    foreign key (user_id) references users(user_id)
);

create table if not exists cpd_records (
    cpd_id text primary key,
    user_id text,
    name text,
    title text,
    category text,
    hours real,
    provider text,
    completion_date text,
    evidence_file_id text,
    status text,
    created_on text,
    foreign key (user_id) references users(user_id)
);

create table if not exists knowledge_library (
    knowledge_id text primary key,
    title text,
    category text,
    standard text,
    revision text,
    issue_date text,
    file_id text,
    mandatory_ack text,
    uploaded_by text,
    created_on text
);

create table if not exists knowledge_acknowledgements (
    ack_id text primary key,
    knowledge_id text,
    user_id text,
    name text,
    acknowledged_on text,
    status text,
    foreign key (knowledge_id) references knowledge_library(knowledge_id),
    foreign key (user_id) references users(user_id)
);

create table if not exists rule_library (
    rule_id text primary key,
    title text,
    standard text,
    revision text,
    category text,
    link text,
    mandatory text,
    current_version_id text,
    created_on text,
    updated_on text
);

create table if not exists document_versions (
    version_id text primary key,
    rule_id text,
    version_no text,
    revision_date text,
    change_summary text,
    file_link text,
    uploaded_by text,
    approved_by text,
    status text,
    created_on text,
    foreign key (rule_id) references rule_library(rule_id)
);

create table if not exists capa_register (
    capa_id text primary key,
    source text,
    finding text,
    severity text,
    owner_id text,
    owner_name text,
    due_date text,
    status text,
    corrective_action text,
    created_on text,
    updated_on text,
    foreign key (owner_id) references users(user_id)
);

create table if not exists notifications (
    notification_id text primary key,
    user_id text,
    name text,
    email text,
    subject text,
    message text,
    type text,
    status text,
    created_on text,
    sent_on text,
    foreign key (user_id) references users(user_id)
);

create table if not exists audit_trail (
    audit_id text primary key,
    date_time text,
    actor_id text,
    actor_name text,
    actor_role text,
    action text,
    details text,
    result text,
    foreign key (actor_id) references users(user_id)
);

create table if not exists technical_authorities (
    authority_id text primary key,
    user_id text,
    name text,
    discipline text,
    authority_level text,
    approval_limit text,
    active text,
    appointed_by text,
    appointed_on text,
    remarks text,
    foreign key (user_id) references users(user_id)
);

create table if not exists survey_report_reviews (
    review_id text primary key,
    user_id text,
    name text,
    survey_scope text,
    vessel_name text,
    report_file_id text,
    reviewer_id text,
    reviewer_name text,
    technical_quality integer,
    deficiency_identification integer,
    rule_interpretation integer,
    report_writing integer,
    decision_quality integer,
    overall_score real,
    decision text,
    comments text,
    created_on text,
    foreign key (user_id) references users(user_id),
    foreign key (reviewer_id) references users(user_id)
);

create table if not exists plan_review_quality (
    planqa_id text primary key,
    user_id text,
    name text,
    plan_scope text,
    project_name text,
    plan_file_id text,
    reviewer_id text,
    reviewer_name text,
    comments_quality integer,
    missed_findings integer,
    turnaround_days integer,
    accuracy_score integer,
    overall_score real,
    result text,
    comments text,
    created_on text,
    foreign key (user_id) references users(user_id),
    foreign key (reviewer_id) references users(user_id)
);

create table if not exists competency_ncrs (
    ncr_id text primary key,
    user_id text,
    name text,
    source text,
    scope text,
    ncr_type text,
    description text,
    severity text,
    impact_on_authorization text,
    status text,
    corrective_action text,
    raised_by text,
    raised_on text,
    closed_on text,
    foreign key (user_id) references users(user_id)
);

create table if not exists authorization_restrictions (
    restriction_id text primary key,
    authorization_id text,
    user_id text,
    name text,
    scope text,
    restriction_type text,
    restriction_detail text,
    effective_date text,
    expiry_date text,
    status text,
    imposed_by text,
    created_on text,
    foreign key (authorization_id) references authorization_requests(authorization_id),
    foreign key (user_id) references users(user_id)
);

create table if not exists client_feedback (
    feedback_id text primary key,
    user_id text,
    name text,
    client_name text,
    project_or_vessel text,
    job_id text,
    rating integer,
    feedback_type text,
    comments text,
    impact_on_kpi text,
    received_on text,
    foreign key (user_id) references users(user_id)
);

create table if not exists succession_plans (
    succession_id text primary key,
    user_id text,
    name text,
    current_role_name text,
    target_role text,
    readiness_level text,
    successor_for text,
    development_actions text,
    expected_ready_date text,
    sponsor text,
    status text,
    created_on text,
    foreign key (user_id) references users(user_id)
);

create table if not exists workforce_forecasts (
    forecast_id text primary key,
    forecast_period text,
    discipline text,
    required_headcount integer,
    available_headcount integer,
    expiring_authorizations integer,
    leave_or_unavailable integer,
    gap integer,
    risk_status text,
    mitigation_plan text,
    created_on text
);

create table if not exists accreditation_evidence (
    evidence_id text primary key,
    standard text,
    clause text,
    requirement text,
    linked_table text,
    linked_id text,
    evidence_summary text,
    status text,
    owner text,
    last_reviewed text
);

create table if not exists technical_interpretations (
    interpretation_id text primary key,
    title text,
    discipline text,
    related_rule text,
    question text,
    interpretation text,
    approved_by text,
    approval_status text,
    revision text,
    issue_date text,
    created_on text
);

-- Recommended indexes for query performance
create index if not exists users_login_id_idx on users(login_id);
create index if not exists users_email_idx on users(email);
create index if not exists trainings_trainer_id_idx on trainings(trainer_id);
create index if not exists training_records_user_id_idx on training_records(user_id);
create index if not exists training_records_training_id_idx on training_records(training_id);
create index if not exists files_owner_user_id_idx on files(owner_user_id);
create index if not exists files_linked_idx on files(linked_table, linked_id);
create index if not exists competency_matrix_user_id_idx on competency_matrix(user_id);
create index if not exists authorization_requests_user_id_idx on authorization_requests(user_id);
create index if not exists authorization_requests_competency_id_idx on authorization_requests(competency_id);
create index if not exists authorization_certificates_user_id_idx on authorization_certificates(user_id);
create index if not exists training_certificates_user_id_idx on training_certificates(user_id);
create index if not exists training_certificates_training_id_idx on training_certificates(training_id);
create index if not exists digital_signatures_role_idx on digital_signatures(role);
create index if not exists digital_signatures_user_id_idx on digital_signatures(user_id);
create index if not exists revalidation_requests_authorization_id_idx on revalidation_requests(authorization_id);
create index if not exists job_requests_assigned_user_id_idx on job_requests(assigned_user_id);
create index if not exists kpi_records_user_id_idx on kpi_records(user_id);
create index if not exists cpd_records_user_id_idx on cpd_records(user_id);
create index if not exists knowledge_acknowledgements_user_id_idx on knowledge_acknowledgements(user_id);
create index if not exists knowledge_acknowledgements_knowledge_id_idx on knowledge_acknowledgements(knowledge_id);
create index if not exists document_versions_rule_id_idx on document_versions(rule_id);
create index if not exists survey_report_reviews_user_id_idx on survey_report_reviews(user_id);
create index if not exists plan_review_quality_user_id_idx on plan_review_quality(user_id);
create index if not exists competency_ncrs_user_id_idx on competency_ncrs(user_id);
create index if not exists authorization_restrictions_authorization_id_idx on authorization_restrictions(authorization_id);
create index if not exists client_feedback_user_id_idx on client_feedback(user_id);
create index if not exists succession_plans_user_id_idx on succession_plans(user_id);

-- Competency-based authorization pathway update
create table if not exists authorization_scope_tracks (
    track_id text primary key,
    user_id text,
    name text,
    role text,
    pathway text,
    discipline text,
    scope text,
    theory_training_required text,
    theory_training_status text,
    witness_required integer,
    assisted_required integer,
    independent_required integer,
    joint_plan_required integer,
    independent_plan_required integer,
    witness_completed integer,
    assisted_completed integer,
    independent_completed integer,
    joint_plan_completed integer,
    independent_plan_completed integer,
    authorization_status text,
    assigned_by text,
    created_on text,
    updated_on text
);

alter table competency_matrix add column if not exists pathway text;
alter table competency_matrix add column if not exists discipline text;
alter table witness_surveys add column if not exists activity_phase text;
alter table witness_surveys add column if not exists evidence_link text;
alter table supervised_activities add column if not exists evidence_link text;

create index if not exists auth_scope_tracks_user_idx on authorization_scope_tracks(user_id);
create index if not exists auth_scope_tracks_scope_idx on authorization_scope_tracks(scope);
create index if not exists competency_matrix_user_scope_idx on competency_matrix(user_id, scope);


-- Secure one-violation MCQ proctoring upgrade for existing Supabase/PostgreSQL deployments
alter table training_records add column if not exists exam_autosaved_on text;
alter table training_records add column if not exists exam_question_order_json text;
alter table training_records add column if not exists exam_answers_json text;
alter table training_records add column if not exists exam_violation text;
alter table training_records add column if not exists exam_started_on text;
alter table training_records add column if not exists exam_submitted_on text;
alter table assessment_history add column if not exists duration_minutes integer;
alter table assessment_history add column if not exists violation text;
alter table assessment_history add column if not exists answers_json text;

-- ================================================================
-- PSB VERSION 2.0 ADDITIONS
-- Competency Matrix, Class Society Operations, Designer/Shipyard Portals
-- ================================================================
create table if not exists competency_matrix (
    matrix_id text primary key, user_id text, user_name text, role text, pathway text,
    domain text, required_scope text, required_training text, training_status text,
    mcq_status text, witness_required integer, witness_completed integer,
    supervised_required integer, supervised_completed integer,
    plan_joint_required integer, plan_joint_completed integer,
    plan_independent_required integer, plan_independent_completed integer,
    tutor_rating real, technical_interview_status text, qmr_status text,
    crb_status text, authorization_status text, gap_summary text, risk_level text,
    expiry_date text, last_review_date text, updated_on text
);

create table if not exists inspection_requests (
    request_id text primary key, request_type text, requester_name text, requester_org text,
    vessel_project text, stage_or_survey text, domain text, location text, requested_date text,
    priority text, risk_level text, assigned_surveyor_id text, assigned_surveyor_name text,
    status text, hold_point text, witness_point text, notes text, created_by text, created_on text
);

create table if not exists survey_operations (
    operation_id text primary key, request_id text, vessel_project text, survey_type text,
    domain text, surveyor_id text, surveyor_name text, checklist_status text,
    evidence_status text, ncr_status text, report_status text, reviewer_status text,
    certificate_status text, safety_briefing text, start_date text, close_date text,
    remarks text, created_on text
);

create table if not exists plan_submissions (
    submission_id text primary key, designer_name text, designer_org text, project_name text,
    drawing_title text, drawing_number text, revision text, domain text, submitted_date text,
    assigned_appraiser_id text, assigned_appraiser_name text, status text, review_type text,
    comments_count integer, target_close_date text, approval_letter_status text, remarks text,
    created_on text
);

create table if not exists drawing_revisions (
    revision_id text primary key, submission_id text, revision text, received_date text,
    comments_issued text, designer_response text, appraiser_decision text, routed_to_surveyor text,
    status text, created_on text
);

create table if not exists ncr_closure_workflow (
    ncr_id text primary key, source_type text, source_id text, raised_against text, domain text,
    severity text, ncr_description text, corrective_action text, root_cause text,
    responsible_person text, due_date text, closure_evidence text, qmr_verification text,
    status text, created_on text, closed_on text
);

create table if not exists role_activity_improvements (
    activity_id text primary key, role_name text, activity_area text, current_activity text,
    recommended_improvement text, maturity_score real, target_score real, priority text,
    owner_role text, status text, created_on text
);

create table if not exists escalation_policy (
    policy_id text primary key, trigger_event text, target_roles text, escalation_timing text,
    severity text, message_template text, is_active text, created_on text
);


-- =========================================================
-- PSB Enterprise Priority 1-10 Extension
-- Safe additive schema: does not remove existing tables/data
-- =========================================================
create table if not exists competency_requirements (
    requirement_id text primary key, role_name text, pathway text, domain text,
    required_training text, required_mcq_categories text, witness_required integer,
    supervised_required integer, joint_reviews_required integer, independent_reviews_required integer,
    case_study_required integer, practical_assignment_required integer, technical_interview_required text,
    revalidation_months integer, risk_level text, created_on text
);
create table if not exists enterprise_gap_analysis (
    gap_id text primary key, priority integer, area text, current_status text,
    missing_gap text, action_required text, owner_role text, status text,
    target_date text, created_on text
);
create table if not exists course_versions (
    version_id text primary key, training_id text, course_title text, version_no text,
    change_summary text, approved_by text, effective_date text, status text, created_on text
);
create table if not exists case_studies (
    case_id text primary key, user_id text, training_id text, scope text,
    case_title text, case_response text, assessor_id text, score real, status text,
    feedback text, created_on text
);
create table if not exists practical_assignments (
    assignment_id text primary key, user_id text, scope text, assignment_title text,
    evidence_summary text, assessor_id text, score real, status text, created_on text
);
create table if not exists technical_interviews (
    interview_id text primary key, user_id text, scope text, interviewer_id text,
    technical_score real, rule_interpretation_score real, reporting_score real,
    safety_score real, decision text, remarks text, created_on text
);
create table if not exists mobile_survey_evidence (
    evidence_id text primary key, operation_id text, user_id text, vessel_project text,
    evidence_type text, gps_location text, captured_at text, file_reference text,
    offline_sync_status text, signature_status text, remarks text, created_on text
);
create table if not exists stage_acceptances (
    acceptance_id text primary key, request_id text, operation_id text, project_name text,
    stage_name text, domain text, hold_point_status text, witness_point_status text,
    ncr_status text, accepted_by text, acceptance_decision text, remarks text, created_on text
);
create table if not exists material_certifications (
    cert_id text primary key, project_name text, material_type text, certificate_no text,
    supplier text, domain text, verification_status text, verified_by text, remarks text, created_on text
);
create table if not exists trial_requests (
    trial_id text primary key, project_name text, trial_type text, requested_by text,
    requested_date text, assigned_surveyor_id text, status text, findings text, created_on text
);
create table if not exists comment_resolutions (
    comment_id text primary key, submission_id text, revision_id text, comment_text text,
    designer_response text, appraiser_closure text, status text, created_on text, closed_on text
);
create table if not exists ai_competency_recommendations (
    recommendation_id text primary key, user_id text, name text, scope text,
    gap_type text, recommendation text, priority text, status text, created_on text
);
create table if not exists audit_readiness_items (
    item_id text primary key, standard_name text, clause_ref text, requirement text,
    evidence_required text, evidence_status text, open_findings integer, overdue_actions integer,
    risk_level text, owner_role text, last_review_date text, created_on text
);
create table if not exists workforce_forecasts (
    forecast_id text primary key, department text, domain text, required_staff integer,
    authorized_staff integer, trainee_pipeline integer, retirement_risk integer,
    competency_shortage integer, authorization_shortage integer, recruitment_need integer,
    forecast_period text, risk_level text, created_on text
);
create table if not exists role_permission_matrix (
    permission_id text primary key, role_name text, module_name text, can_view text,
    can_create text, can_update text, can_approve text, can_export text, created_on text
);

create index if not exists idx_comp_req_path_domain on competency_requirements(pathway, domain);
create index if not exists idx_mobile_evidence_operation on mobile_survey_evidence(operation_id);
create index if not exists idx_audit_readiness_standard on audit_readiness_items(standard_name);
create index if not exists idx_workforce_domain on workforce_forecasts(domain);


-- PSB V3 Training Practical Certificate Reauthorization Update
create table if not exists training_pathway_rules (rule_id text primary key, pathway text, scope text, rule_name text, required_training_ids text, min_score real, min_attendance real, require_case_study text, require_practical_assignment text, required_witness_count integer, required_supervised_count integer, required_joint_review_count integer, required_independent_review_count integer, require_technical_interview text, validity_months integer, created_by text, created_on text, status text, remarks text);
create table if not exists practical_eligibility_records (eligibility_id text primary key, user_id text, name text, pathway text, scope text, rule_id text, training_status text, mcq_status text, attendance_status text, case_study_status text, practical_assignment_status text, witness_status text, supervised_status text, joint_review_status text, independent_review_status text, technical_interview_status text, overall_status text, readiness_percent real, missing_items text, calculated_on text, unlocked_by text, unlocked_on text, phase_unlocked text, remarks text);
create table if not exists digital_certificates_v3 (certificate_id text primary key, certificate_no text, certificate_type text, user_id text, name text, role text, pathway text, scope text, qualification_title text, module_details text, authorization_level text, authorized_activities text, restrictions text, issue_date text, expiry_date text, status text, qr_payload text, verification_url text, ceo_signer text, trainer_signer text, hod_signer text, technical_authority_signer text, admin_signature_snapshot text, certificate_html text, generated_by text, generated_on text, revoked_on text, revoke_reason text);
create table if not exists reauthorization_requirements_v3 (requirement_id text primary key, scope text, required_refresher_training_ids text, required_cpd_hours real, min_activity_count integer, max_major_ncr integer, max_client_complaints integer, require_qmr_clearance text, require_technical_interview text, validity_years integer, created_by text, created_on text, status text);
create table if not exists reauthorization_reviews_v3 (review_id text primary key, certificate_id text, user_id text, name text, scope text, current_expiry_date text, refresher_status text, cpd_status text, activity_status text, performance_status text, qmr_clearance text, technical_interview_status text, decision text, new_expiry_date text, reviewer text, review_date text, remarks text);
create table if not exists certificate_signature_settings_v3 (setting_id text primary key, role_name text, signer_name text, designation text, signature_image_ref text, stamp_image_ref text, certificate_usage text, active text, uploaded_by text, uploaded_on text, remarks text);
create table if not exists role_activity_gap_reviews_v3 (gap_id text primary key, role_name text, activity_name text, world_class_requirement text, current_status text, gap_detail text, improvement_action text, priority text, owner_role text, target_date text, status text, created_on text);
create index if not exists eligibility_user_scope_idx on practical_eligibility_records(user_id, scope);
create index if not exists certs_user_scope_idx on digital_certificates_v3(user_id, scope);
create index if not exists pathway_rules_scope_idx on training_pathway_rules(pathway, scope);

-- ============================================================
-- PSB V4 Final World-Class IACS/RO Control Layer
-- Added to close final 1-8 professional gaps and mark status Strong
-- ============================================================
create table if not exists iacs_clause_mapping_v4 (
    mapping_id text primary key, standard text, clause_ref text, clause_title text,
    workflow_area text, role_name text, required_evidence text, evidence_table text,
    owner_role text, review_frequency text, status text, strength_status text,
    created_by text, created_on text, remarks text
);
create table if not exists authorization_scope_locks_v4 (
    lock_id text primary key, user_id text, name text, role_name text, scope text,
    survey_type text, authorization_level text, certificate_id text, valid_from text,
    valid_until text, status text, restriction_detail text, last_verified_on text,
    verified_by text, lock_result text, remarks text
);
create table if not exists technical_interview_scores_v4 (
    interview_id text primary key, user_id text, name text, pathway text, scope text,
    interview_type text, interviewer text, technical_knowledge integer, rule_interpretation integer,
    practical_judgement integer, reporting_quality integer, ethics_independence integer,
    safety_awareness integer, total_score real, pass_mark real, decision text,
    corrective_action text, interview_date text, evidence_ref text, remarks text
);
create table if not exists authorized_staff_monitoring_v4 (
    monitoring_id text primary key, user_id text, name text, scope text, review_period text,
    jobs_completed integer, reports_reviewed integer, major_ncrs integer, minor_ncrs integer,
    client_complaints integer, audit_findings integer, technical_errors integer,
    performance_rating text, risk_level text, action_required text, reviewed_by text,
    review_date text, next_review_date text, remarks text
);
create table if not exists document_control_register_v4 (
    document_id text primary key, project_or_vessel text, document_type text, document_title text,
    discipline text, revision_no text, status text, owner_role text, submitted_by text,
    reviewed_by text, approval_status text, file_ref text, linked_record_id text,
    effective_date text, expiry_date text, created_on text, updated_on text, remarks text
);
create table if not exists audit_evidence_packs_v4 (
    pack_id text primary key, audit_standard text, audit_scope text, audit_period text,
    prepared_by text, evidence_summary text, included_tables text, open_findings integer,
    overdue_actions integer, risk_areas text, pack_status text, export_ref text,
    prepared_on text, reviewed_by text, review_status text, remarks text
);
create table if not exists offline_mobile_sync_v4 (
    sync_id text primary key, user_id text, name text, role_name text, operation_id text,
    evidence_type text, gps_location text, captured_timestamp text, offline_device_ref text,
    local_record_id text, sync_status text, synced_on text, reviewed_by text,
    review_status text, integrity_hash text, remarks text
);
create table if not exists notification_channels_v4 (
    channel_id text primary key, channel_name text, provider_name text, enabled text,
    sender_id text, config_summary text, escalation_types text, test_status text,
    last_tested_on text, created_by text, created_on text, remarks text
);
create table if not exists worldclass_status_v4 (
    item_id text primary key, priority_no text, item_name text, target_status text,
    implementation_status text, evidence_page text, owner_role text, last_reviewed_on text,
    remarks text
);
create index if not exists iacs_clause_area_idx on iacs_clause_mapping_v4(workflow_area, role_name);
create index if not exists auth_scope_lock_user_idx on authorization_scope_locks_v4(user_id, scope, survey_type);
create index if not exists tech_interview_user_idx on technical_interview_scores_v4(user_id, scope);
create index if not exists doc_control_project_idx on document_control_register_v4(project_or_vessel, document_type);
create index if not exists mobile_sync_user_idx on offline_mobile_sync_v4(user_id, sync_status);


-- V5 Final professional closure controls
create table if not exists survey_type_authorization_matrix_v5 (lock_id text primary key, user_id text, name text, survey_type text, scope text, authorization_status text, allowed_for_assignment text, restriction_status text, expiry_date text, last_activity_date text, risk_level_allowed text, verified_by text, verified_on text, remarks text);
create table if not exists plan_domain_authorization_matrix_v5 (domain_id text primary key, user_id text, name text, plan_domain text, theoretical_status text, joint_reviews_required integer, joint_reviews_completed integer, independent_reviews_required integer, independent_reviews_completed integer, technical_interview_status text, authorization_status text, expiry_date text, authorized_by text, remarks text, created_on text);
create table if not exists authorization_restrictions_v5 (restriction_id text primary key, user_id text, name text, scope text, action_type text, reason text, effective_from text, effective_until text, imposed_by text, review_required text, review_date text, status text, remarks text, created_on text);
create table if not exists ship_construction_file_v5 (scf_id text primary key, project_name text, vessel_name text, imo_number text, shipyard text, stage text, document_pack text, required_documents text, received_documents text, missing_documents text, approval_status text, stage_gate_status text, responsible_surveyor text, last_reviewed_on text, remarks text, created_on text);
create table if not exists vendor_material_approval_v5 (approval_id text primary key, vendor_name text, material_or_equipment text, certificate_no text, standard_reference text, project_name text, submitted_by text, review_status text, approved_by text, approval_date text, expiry_date text, linked_stage text, remarks text, created_on text);
create table if not exists clause_evidence_mapping_v5 (evidence_id text primary key, standard_name text, clause_reference text, clause_requirement text, evidence_source text, evidence_owner text, evidence_status text, risk_rating text, last_verified_on text, next_review_due text, gap_or_finding text, corrective_action text, remarks text, created_on text);
create table if not exists competency_assignment_locks_v5 (lock_check_id text primary key, job_id text, job_title text, required_scope text, required_survey_type text, candidate_user_id text, candidate_name text, authorization_valid text, restriction_clear text, expiry_clear text, competency_level_clear text, assignment_decision text, reason text, checked_by text, checked_on text);
create table if not exists executive_risk_score_v5 (risk_id text primary key, period text, revenue_risk integer, competency_risk integer, audit_risk integer, authorization_risk integer, resource_risk integer, overall_risk_score real, risk_band text, top_actions text, prepared_by text, prepared_on text, remarks text);
create table if not exists worldclass_activity_gap_closure_v5 (closure_id text primary key, role_name text, activity_name text, previous_gap text, control_added text, maturity_status text, residual_gap text, owner_role text, review_frequency text, created_on text);
create index if not exists idx_survey_lock_user_scope_v5 on survey_type_authorization_matrix_v5(user_id, scope);
create index if not exists idx_plan_domain_user_v5 on plan_domain_authorization_matrix_v5(user_id, plan_domain);
create index if not exists idx_clause_standard_v5 on clause_evidence_mapping_v5(standard_name, clause_reference);
create index if not exists idx_assignment_lock_job_v5 on competency_assignment_locks_v5(job_id);

-- V7 Appraised / Approved Drawing Distribution Upgrade
create table if not exists plan_appraised_drawings_v7 (
            appraised_id text primary key, appraised_no text unique, appraisal_id text, package_id text, project_no text,
            workflow_id text, drawing_no text, drawing_title text, discipline text, designer_name text,
            submitted_revision text, appraised_revision text, original_file_id text, markedup_file_id text,
            comment_summary text, appraisal_status text, response_required text, response_due_date text,
            appraised_by text, appraised_at text, created_on text
        );
create table if not exists drawing_comment_register_v7 (
            comment_id text primary key, appraised_id text, comment_no text unique, drawing_no text, revision_no text,
            page_no text, zone_location text, rule_reference text, priority text, comment_text text,
            status text, created_by text, created_on text, closed_at text
        );
create table if not exists designer_drawing_responses_v7 (
            response_id text primary key, appraised_id text, comment_id text, response_no text unique, designer_name text,
            response_text text, revised_drawing_no text, revised_revision_no text, response_file_id text,
            response_status text, submitted_by text, submitted_on text, reviewed_by text, reviewed_on text
        );
create table if not exists drawing_revision_chain_v7 (
            chain_id text primary key, drawing_no text, previous_revision text, appraised_revision text, new_revision text,
            change_summary text, superseded_revision text, current_revision_status text, created_on text
        );
create table if not exists approved_drawing_distribution_v7 (
            distribution_id text primary key, distribution_no text unique, appraised_id text, project_no text,
            workflow_id text, drawing_no text, drawing_title text, approved_revision text, approved_file_id text,
            approval_status text, distributed_to_role text, distributed_to_user text, distribution_purpose text,
            acknowledgement_required text, acknowledgement_status text, distributed_by text, distributed_on text, acknowledged_on text
        );
create table if not exists surveyor_drawing_dashboard_v7 (
            dashboard_id text primary key, surveyor_user text, project_no text, workflow_id text, drawing_no text,
            drawing_title text, discipline text, approved_revision text, applicable_survey_scope text,
            linked_itp_id text, linked_inspection_request_id text, latest_revision_status text,
            surveyor_acknowledged text, acknowledged_on text, created_on text
        );
create table if not exists latest_revision_checks_v7 (
            check_id text primary key, check_no text unique, project_no text, workflow_id text, drawing_no text,
            required_revision text, latest_approved_revision text, inspection_request_id text, check_result text,
            block_reason text, checked_by text, checked_on text
        );
create table if not exists superseded_drawing_control_v7 (
            superseded_id text primary key, drawing_no text, superseded_revision text, current_revision text,
            superseded_date text, blocked_for_survey text, reason text, created_by text, created_on text
        );
create table if not exists surveyor_drawing_acknowledgements_v7 (
            acknowledgement_id text primary key, dashboard_id text, surveyor_user text, drawing_no text,
            approved_revision text, acknowledgement_text text, acknowledgement_status text, acknowledged_on text
        );
create table if not exists drawing_distribution_thread_v7 (
            thread_id text primary key, thread_no text, drawing_no text, revision_no text, source_step text,
            target_step text, linked_record text, relationship_note text, created_on text
        );


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

-- V9 State-of-Art ERP Review, Role Accountability and UI/UX Performance Layer
create table if not exists workflow_quality_gates (
    gate_id text primary key, module_name text, activity_name text, current_status text,
    required_standard text, owner_role text, input_data text, output_data text,
    control_check text, risk_if_missing text, improvement_action text, maturity_score real,
    uiux_status text, performance_risk text, updated_on text
);
create table if not exists uiux_performance_checks (
    check_id text primary key, page_name text, role_name text, ui_clarity_score real,
    loading_risk text, data_volume_control text, error_handling_status text,
    mobile_readiness text, user_guidance text, improvement_action text, status text, updated_on text
);
create table if not exists role_accountability_map (
    map_id text primary key, role_name text, responsibility text, input_from text,
    data_received text, action_taken text, output_to text, data_transferred text,
    approval_authority text, escalation_rule text, missing_control text, final_status text,
    updated_on text
);
create index if not exists workflow_quality_module_idx on workflow_quality_gates(module_name, current_status);
create index if not exists uiux_performance_page_idx on uiux_performance_checks(page_name, status);
create index if not exists role_accountability_role_idx on role_accountability_map(role_name);

-- ============================================================
-- V10 STATE-OF-THE-ART ERP MATURITY LAYER
-- ============================================================
create table if not exists role_activity_maturity_v10 (
    maturity_id text primary key, role_name text, activity_name text, current_score real,
    target_score real, current_state text, world_class_standard text, gap text,
    improvement_action text, owner_role text, due_frequency text, kpi text,
    automation_control text, uiux_control text, performance_control text,
    status text, updated_on text
);
create table if not exists workflow_task_engine_v10 (
    task_id text primary key, workflow_name text, source_role text, target_role text,
    object_type text, object_id text, task_title text, task_description text,
    status text, priority text, due_date text, escalation_level text,
    reminder_count integer, created_by text, created_on text, closed_on text,
    data_payload text, remarks text
);
create table if not exists survey_logbook_v10 (
    log_id text primary key, user_id text, name text, survey_type text, vessel_project text,
    ship_type text, location text, survey_date text, role_performed text,
    findings_count integer, ncr_count integer, report_ref text, reviewed_by text,
    competency_credit text, remarks text, created_on text
);
create table if not exists competency_decay_v10 (
    decay_id text primary key, user_id text, name text, scope text, last_activity_date text,
    months_without_activity integer, decay_status text, required_action text,
    review_by text, next_review_date text, status text, created_on text
);
create table if not exists plan_review_peer_quality_v10 (
    review_id text primary key, appraiser_user_id text, appraiser_name text, domain text,
    drawing_ref text, review_type text, accuracy_score real, comment_quality_score real,
    timeliness_score real, rule_interpretation_score real, peer_reviewer text,
    decision text, improvement_required text, created_on text
);
create table if not exists controlled_transmittals_v10 (
    transmittal_id text primary key, project_name text, document_ref text, revision text,
    document_type text, issued_by text, issued_to_role text, issued_to_user text,
    issue_purpose text, issue_status text, acknowledgement_required text,
    acknowledged_on text, supersedes_revision text, due_date text, remarks text, created_on text
);
create table if not exists enterprise_health_metrics_v10 (
    metric_id text primary key, metric_area text, metric_name text, score real,
    risk_level text, source_module text, calculation_basis text, owner_role text,
    action_required text, updated_on text
);
create table if not exists workflow_sla_v10 (
    sla_id text primary key, workflow_name text, step_name text, owner_role text,
    standard_days integer, warning_days integer, escalation_role text,
    escalation_rule text, kpi_name text, status text, updated_on text
);
create table if not exists uiux_page_design_v10 (
    design_id text primary key, page_name text, role_name text, primary_user_goal text,
    key_cards text, required_filters text, next_action_prompt text,
    empty_state_message text, performance_rule text, mobile_rule text,
    status text, updated_on text
);
create index if not exists workflow_task_status_idx_v10 on workflow_task_engine_v10(status, priority, due_date);
create index if not exists survey_logbook_user_idx_v10 on survey_logbook_v10(user_id, survey_type, survey_date);
create index if not exists transmittal_doc_idx_v10 on controlled_transmittals_v10(document_ref, revision, issue_status);
create index if not exists role_activity_role_idx_v10 on role_activity_maturity_v10(role_name, status);
create index if not exists health_metric_area_idx_v10 on enterprise_health_metrics_v10(metric_area, risk_level);

-- V11 International Classification Society ERP Intelligence Layer
create table if not exists enterprise_search_index (
    search_id text primary key, object_type text, object_id text, title text, summary text,
    keywords text, owner_role text, owner_user_id text, confidentiality text, status text,
    source_table text, source_url text, updated_on text
);
create table if not exists knowledge_graph_links (
    link_id text primary key, source_type text, source_id text, source_title text,
    relation_type text, target_type text, target_id text, target_title text,
    strength integer, rationale text, created_by text, created_on text
);
create table if not exists ai_competency_advice (
    advice_id text primary key, user_id text, name text, role text, target_role text, scope text,
    readiness_score integer, readiness_status text, key_strengths text, critical_gaps text,
    recommended_training text, recommended_practical text, recommended_authorization_action text,
    risk_level text, generated_on text, reviewed_by text, review_status text
);
create table if not exists lessons_learned (
    lesson_id text primary key, source_type text, source_id text, title text, event_date text,
    discipline text, root_cause text, lesson text, preventive_action text, linked_standard text,
    severity text, mandatory_read text, owner_role text, approval_status text, approved_by text,
    created_by text, created_on text, closed_on text
);
create table if not exists notification_rules (
    rule_id text primary key, event_name text, trigger_condition text, recipient_roles text,
    channels text, reminder_days text, escalation_days text, escalation_roles text,
    active text, created_by text, created_on text
);
create table if not exists notification_outbox (
    outbox_id text primary key, event_name text, object_type text, object_id text, recipient_role text,
    recipient_user_id text, recipient_name text, channel text, subject text, message text,
    due_date text, escalation_level text, status text, created_on text, sent_on text, failure_reason text
);
create table if not exists mobile_sync_register (
    sync_id text primary key, user_id text, name text, role text, device_id text, workflow_type text,
    object_id text, offline_payload text, evidence_count integer, gps_lat text, gps_lng text,
    captured_on text, synced_on text, validation_status text, sync_status text, remarks text
);
create table if not exists client_self_service_requests (
    request_id text primary key, client_user_id text, client_name text, request_type text,
    vessel_or_project text, imo_number text, requested_date text, location text, priority text,
    request_details text, status text, assigned_to_role text, assigned_user_id text,
    last_client_update text, certificate_link text, created_on text, updated_on text
);
create table if not exists role_communication_matrix (
    comm_id text primary key, workflow_name text, from_role text, to_role text, data_shared text,
    format text, trigger_event text, due_time text, escalation_rule text, system_record text,
    criticality text, improvement_control text, created_on text
);
create index if not exists idx_search_keywords on enterprise_search_index (keywords);
create index if not exists idx_search_object on enterprise_search_index (object_type, object_id);
create index if not exists idx_graph_source on knowledge_graph_links (source_type, source_id);
create index if not exists idx_graph_target on knowledge_graph_links (target_type, target_id);
create index if not exists idx_advice_user on ai_competency_advice (user_id, scope);
create index if not exists idx_lessons_discipline on lessons_learned (discipline, severity);
create index if not exists idx_outbox_status on notification_outbox (status, due_date);
create index if not exists idx_client_status on client_self_service_requests (status, requested_date);


-- V12 COMPLETE ENTERPRISE ERP CLOSURE LAYER
-- Adds final 1–8 gaps: communication integrations, native mobile readiness,
-- strict document enforcement, expanded client self-service, commercial module,
-- HR integration, rule/circular change management and universal workflow engine.
create table if not exists communication_integrations (
    integration_id text primary key, channel text, provider text, sender_identity text,
    api_key_secret_name text, webhook_url text, enabled text, test_status text,
    last_test_on text, owner_role text, created_on text
);
create table if not exists enterprise_messages (
    message_id text primary key, workflow_name text, event_name text, object_type text, object_id text,
    recipient_role text, recipient_user_id text, channel text, subject text, body text,
    priority text, due_date text, status text, escalation_level text, created_on text, sent_on text, error_message text
);
create table if not exists mobile_devices (
    device_id text primary key, assigned_user_id text, assigned_user_name text, assigned_role text,
    device_type text, platform text, app_version text, offline_enabled text, last_sync_on text,
    gps_required text, signature_required text, photo_required text, status text, created_on text
);
create table if not exists offline_inspection_packages (
    package_id text primary key, workflow_type text, job_id text, assigned_user_id text, vessel_or_project text,
    required_checklist text, required_documents text, offline_payload text, sync_status text,
    evidence_count integer, gps_lat text, gps_lng text, captured_on text, uploaded_on text, validation_status text
);
create table if not exists document_usage_locks (
    lock_id text primary key, document_id text, revision_no text, document_title text,
    controlled_status text, allowed_for_use text, blocked_reason text, checked_by text, checked_on text
);
create table if not exists document_acknowledgements (
    ack_id text primary key, document_id text, revision_no text, recipient_role text, recipient_user_id text,
    recipient_name text, acknowledgement_status text, acknowledged_on text, remarks text
);
create table if not exists client_portal_services (
    service_id text primary key, client_user_id text, client_name text, service_type text,
    vessel_or_project text, request_reference text, current_status text, certificate_link text,
    open_ncr_count integer, invoice_status text, feedback_status text, created_on text, updated_on text
);
create table if not exists quotations (
    quotation_id text primary key, client_name text, vessel_or_project text, service_scope text,
    estimated_fee real, currency text, tax_amount real, total_amount real, status text,
    prepared_by text, approved_by text, valid_until text, created_on text
);
create table if not exists invoices (
    invoice_id text primary key, quotation_id text, client_name text, vessel_or_project text,
    invoice_amount real, currency text, payment_status text, due_date text, paid_on text,
    created_by text, created_on text
);
create table if not exists hr_integration_records (
    hr_id text primary key, user_id text, employee_no text, department text, designation text,
    employment_status text, leave_status text, leave_from text, leave_to text, availability_status text,
    last_hr_sync_on text, source_system text
);
create table if not exists rule_change_register (
    change_id text primary key, source_type text, reference_no text, title text, issue_date text,
    effective_date text, affected_domains text, impact_summary text, technical_owner text,
    training_required text, affected_staff_roles text, implementation_status text, approval_status text,
    created_on text, closed_on text
);
create table if not exists enterprise_workflows (
    workflow_id text primary key, workflow_name text, object_type text, object_id text,
    current_step text, owner_role text, owner_user_id text, reviewer_role text, approver_role text,
    required_evidence text, due_date text, priority text, status text, escalation_level text,
    audit_trail_summary text, created_on text, updated_on text
);
create table if not exists enterprise_workflow_tasks (
    task_id text primary key, workflow_id text, task_title text, task_description text,
    owner_role text, owner_user_id text, due_date text, evidence_required text,
    status text, reviewer text, approver text, completed_on text, escalation_status text, created_on text
);

create index if not exists idx_messages_status on enterprise_messages (status, due_date);
create index if not exists idx_mobile_user on mobile_devices (assigned_user_id, status);
create index if not exists idx_offline_job on offline_inspection_packages (job_id, sync_status);
create index if not exists idx_doc_lock on document_usage_locks (document_id, revision_no);
create index if not exists idx_client_services on client_portal_services (client_user_id, current_status);
create index if not exists idx_quotes_client on quotations (client_name, status);
create index if not exists idx_invoices_client on invoices (client_name, payment_status);
create index if not exists idx_hr_user on hr_integration_records (user_id, availability_status);
create index if not exists idx_rule_effective on rule_change_register (effective_date, implementation_status);
create index if not exists idx_workflows_status on enterprise_workflows (status, due_date, owner_role);
create index if not exists idx_workflow_tasks on enterprise_workflow_tasks (workflow_id, status, due_date);


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

-- V14 final production closure tables: live integrations, mobile/PWA, hard rules, isolation, security, role UX and UAT
create table if not exists live_integration_events (event_id text primary key, connector_name text, connector_type text, provider text, direction text, trigger_event text, payload_summary text, endpoint_secret_name text, retry_policy text, status text, last_attempt_on text, error_message text, owner_role text, created_on text);
create table if not exists production_security_operations (security_id text primary key, control_name text, control_type text, applies_to_roles text, required_status text, current_status text, enforcement_method text, test_case text, failure_action text, owner_role text, last_verified_on text, created_on text);
create table if not exists mobile_offline_work_queue (offline_id text primary key, app_module text, user_role text, task_type text, record_ref text, captured_fields text, evidence_required text, gps_required text, photo_required text, signature_required text, sync_status text, conflict_rule text, last_sync_on text, created_on text);
create table if not exists database_hard_rule_checks (rule_id text primary key, rule_name text, source_table text, blocking_condition text, database_enforcement text, ui_enforcement text, test_status text, block_message text, risk_if_missing text, owner_role text, created_on text);
create table if not exists portal_isolation_verification (isolation_id text primary key, portal_role text, tenant_field text, visibility_scope text, forbidden_visibility text, rls_policy_required text, test_user_a text, test_user_b text, expected_result text, current_status text, last_tested_on text, created_on text);
create table if not exists role_landing_page_config (config_id text primary key, role_name text, first_screen_title text, required_widgets text, primary_actions text, hidden_operational_pages text, task_filters text, alert_filters text, kpi_cards text, mobile_priority text, status text, created_on text);
create table if not exists production_uat_role_results (uat_id text primary key, role_name text, workflow_name text, test_scenario text, expected_result text, actual_result text, result_status text, severity text, release_blocker text, evidence_link text, tested_by text, tested_on text, created_on text);
create table if not exists live_payment_finance_controls (finance_id text primary key, module_name text, process_name text, client_visible text, integration_provider text, environment_secret_names text, approval_required text, posting_rule text, reconciliation_rule text, status text, owner_role text, created_on text);
create table if not exists digital_signature_validation_controls (sig_id text primary key, certificate_type text, signer_role text, validation_method text, certificate_hash_required text, qr_verification_required text, revocation_check_required text, audit_trail_required text, current_status text, owner_role text, created_on text);
create index if not exists idx_live_integration_status on live_integration_events(connector_type, status);
create index if not exists idx_security_ops_type on production_security_operations(control_type, current_status);
create index if not exists idx_mobile_queue_sync on mobile_offline_work_queue(user_role, sync_status);
create index if not exists idx_hard_rules_table on database_hard_rule_checks(source_table, test_status);
create index if not exists idx_portal_isolation_role on portal_isolation_verification(portal_role, current_status);
create index if not exists idx_role_landing_role on role_landing_page_config(role_name);
create index if not exists idx_uat_role_status on production_uat_role_results(role_name, result_status);
create index if not exists idx_finance_status on live_payment_finance_controls(module_name, status);
create index if not exists idx_signature_cert_type on digital_signature_validation_controls(certificate_type, current_status);

-- ================================================================
-- V15 FINAL STAKEHOLDER + EXTERNAL COMMUNICATION CLOSURE
-- ================================================================
CREATE TABLE IF NOT EXISTS finance_commercial_records (
    record_id TEXT PRIMARY KEY,
    client_id TEXT,
    vessel_id TEXT,
    commercial_stage TEXT,
    quote_no TEXT,
    invoice_no TEXT,
    amount NUMERIC DEFAULT 0,
    currency TEXT DEFAULT 'PKR',
    payment_status TEXT DEFAULT 'Pending',
    payment_reference TEXT,
    due_date DATE,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_finance_commercial_client ON finance_commercial_records(client_id);
CREATE INDEX IF NOT EXISTS idx_finance_commercial_status ON finance_commercial_records(payment_status);

CREATE TABLE IF NOT EXISTS hr_availability_records (
    record_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    department TEXT,
    position_title TEXT,
    availability_status TEXT NOT NULL,
    leave_from DATE,
    leave_to DATE,
    conflict_of_interest_flag BOOLEAN DEFAULT FALSE,
    assignment_block BOOLEAN DEFAULT FALSE,
    remarks TEXT,
    updated_by TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_hr_availability_employee ON hr_availability_records(employee_id);
CREATE INDEX IF NOT EXISTS idx_hr_availability_status ON hr_availability_records(availability_status);

CREATE TABLE IF NOT EXISTS security_incident_register (
    incident_id TEXT PRIMARY KEY,
    severity TEXT,
    incident_type TEXT,
    affected_user TEXT,
    description TEXT,
    containment_action TEXT,
    status TEXT DEFAULT 'Open',
    reported_by TEXT,
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_security_incident_status ON security_incident_register(status);

CREATE TABLE IF NOT EXISTS legal_contract_records (
    record_id TEXT PRIMARY KEY,
    client_id TEXT,
    contract_no TEXT,
    contract_status TEXT,
    liability_clause_status TEXT,
    dispute_status TEXT,
    legal_owner TEXT,
    document_reference TEXT,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customer_support_tickets (
    ticket_id TEXT PRIMARY KEY,
    client_id TEXT,
    ticket_type TEXT,
    priority TEXT,
    subject TEXT,
    description TEXT,
    routed_to_role TEXT,
    sla_due_at TIMESTAMP,
    status TEXT DEFAULT 'Open',
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_support_ticket_status ON customer_support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_support_ticket_client ON customer_support_tickets(client_id);

CREATE TABLE IF NOT EXISTS external_party_access_register (
    access_id TEXT PRIMARY KEY,
    party_type TEXT NOT NULL,
    party_name TEXT,
    related_client_id TEXT,
    related_project_id TEXT,
    allowed_view TEXT,
    prohibited_view TEXT,
    access_status TEXT DEFAULT 'Active',
    approved_by TEXT,
    approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_external_party_type ON external_party_access_register(party_type);

CREATE TABLE IF NOT EXISTS manufacturer_vendor_records (
    record_id TEXT PRIMARY KEY,
    vendor_id TEXT,
    vendor_name TEXT,
    approval_scope TEXT,
    approval_status TEXT,
    expiry_date DATE,
    ncr_status TEXT,
    evidence_reference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subcontracted_surveyor_records (
    record_id TEXT PRIMARY KEY,
    surveyor_id TEXT,
    assignment_id TEXT,
    authorization_scope TEXT,
    contract_valid_until DATE,
    evidence_status TEXT,
    report_status TEXT,
    review_status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS immutable_audit_events (
    audit_id TEXT PRIMARY KEY,
    actor_id TEXT,
    actor_role TEXT,
    action_name TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    before_hash TEXT,
    after_hash TEXT,
    event_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_immutable_audit_entity ON immutable_audit_events(entity_type, entity_id);

