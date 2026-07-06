
-- V17 FINAL PRODUCTION HARDENING FOR PSB INTERNATIONAL CLASS SOCIETY ERP
-- Apply in Supabase/PostgreSQL after reviewing table names in your production schema.

-- 1) Immutable audit logs: append-only. Admins may view but must not update/delete.
CREATE TABLE IF NOT EXISTS immutable_audit_log (
    audit_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    event_time timestamptz NOT NULL DEFAULT now(),
    actor_id text,
    actor_role text,
    action text NOT NULL,
    entity_table text,
    entity_id text,
    before_json jsonb,
    after_json jsonb,
    ip_address text,
    user_agent text,
    hash text,
    previous_hash text
);

CREATE OR REPLACE FUNCTION prevent_immutable_audit_change()
RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'immutable_audit_log is append-only';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_prevent_audit_update ON immutable_audit_log;
CREATE TRIGGER trg_prevent_audit_update
BEFORE UPDATE OR DELETE ON immutable_audit_log
FOR EACH ROW EXECUTE FUNCTION prevent_immutable_audit_change();

-- 2) External portal isolation baseline. Add company/account fields to external-facing tables.
ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS company_id text;
ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS external_party_type text;
ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS portal_scope text DEFAULT 'internal';

-- Recommended RLS pattern (adapt to Supabase auth.uid mappings):
-- CREATE POLICY client_own_records ON client_requests FOR SELECT USING (client_id = current_setting('app.company_id', true));
-- CREATE POLICY designer_own_drawings ON drawing_submissions FOR SELECT USING (designer_company_id = current_setting('app.company_id', true));
-- CREATE POLICY shipyard_own_project ON inspection_requests FOR SELECT USING (shipyard_company_id = current_setting('app.company_id', true));

-- 3) Assignment hard rule: block assignment unless authorized, available, not restricted.
CREATE TABLE IF NOT EXISTS assignment_lock_events (
    lock_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    checked_on timestamptz DEFAULT now(),
    employee_id text,
    job_id text,
    job_type text,
    authorized boolean,
    competent boolean,
    certificate_valid boolean,
    available boolean,
    not_restricted boolean,
    result text,
    reason text
);

-- 4) Mandatory evidence checklist before approval/recommendation.
CREATE TABLE IF NOT EXISTS mandatory_evidence_policy (
    policy_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_name text NOT NULL,
    role_name text NOT NULL,
    required_evidence text NOT NULL,
    block_if_missing boolean DEFAULT true,
    active boolean DEFAULT true,
    created_on timestamptz DEFAULT now()
);

INSERT INTO mandatory_evidence_policy (workflow_name, role_name, required_evidence)
VALUES
('Tutor Recommendation','Tutor/Mentor','Witness report, observation notes, rubric score, evidence attachment'),
('Survey Report Approval','Surveyor','Checklist, photos/GPS/time where applicable, NCR decision, report draft'),
('New Building Stage Approval','New Building Surveyor','ITP stage evidence, material/NDT/test record as applicable'),
('Plan Approval','Plan Appraiser','Reviewed drawing, comment register, designer closure response, reviewer decision'),
('Authorization Certificate','Competency Manager','Training record, MCQ, practical evidence, tutor recommendation, technical interview, QMR clearance')
ON CONFLICT DO NOTHING;

-- 5) Document control hard rule helper table.
CREATE TABLE IF NOT EXISTS document_revision_control (
    document_id text PRIMARY KEY,
    document_type text,
    revision_no text,
    status text CHECK (status IN ('Draft','Reviewed','Approved','Released','Superseded','Archived')),
    supersedes_document_id text,
    released_on timestamptz,
    released_by text,
    acknowledgement_required boolean DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_document_revision_control_status ON document_revision_control(status);

-- 6) UAT role test evidence.
CREATE TABLE IF NOT EXISTS role_uat_execution (
    uat_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    role_name text NOT NULL,
    workflow_name text NOT NULL,
    test_step text NOT NULL,
    expected_result text NOT NULL,
    actual_result text,
    result_status text DEFAULT 'Not Tested',
    tester text,
    tested_on timestamptz,
    release_blocker boolean DEFAULT false
);

-- 7) Integration readiness register.
CREATE TABLE IF NOT EXISTS live_integration_register (
    integration_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_name text NOT NULL,
    provider text,
    env_var_required text,
    status text DEFAULT 'Not Connected',
    last_tested_on timestamptz,
    owner_role text DEFAULT 'IT/Security Admin'
);

INSERT INTO live_integration_register (integration_name, provider, env_var_required)
VALUES
('Email','SMTP/SendGrid/Mailgun','SMTP_HOST, SMTP_USER, SMTP_PASSWORD'),
('WhatsApp','Meta/Twilio','WHATSAPP_TOKEN, WHATSAPP_PHONE_ID'),
('SMS','Twilio/Local Gateway','SMS_API_KEY'),
('Payment Gateway','Stripe/PayFast/Bank','PAYMENT_API_KEY'),
('Digital Signature','PKI/eSign Provider','SIGNATURE_API_KEY'),
('HRIS/Payroll','HR System','HR_API_KEY'),
('Accounting','ERP/Accounting','FINANCE_API_KEY')
ON CONFLICT DO NOTHING;
