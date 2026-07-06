-- V16 FINAL LIVE PRODUCTION HARDENING
-- Apply after the base schema in Supabase/PostgreSQL.
-- These tables and rules support live integrations, immutable audit, external portal isolation,
-- database-level enforcement, field PWA/offline operations, digital-signature trust, and UAT.

create table if not exists integration_connectors (
  connector_id text primary key,
  connector_name text not null,
  connector_type text not null,
  provider text,
  env_keys text,
  status text default 'Not Configured',
  last_tested_at timestamp,
  last_test_result text,
  created_at timestamp default now()
);

insert into integration_connectors (connector_id, connector_name, connector_type, provider, env_keys, status)
values
('email', 'Email SMTP/API', 'communication', 'SMTP/SendGrid/Mailgun', 'SMTP_HOST,SMTP_USER,SMTP_PASS,SENDGRID_API_KEY', 'Not Configured'),
('whatsapp', 'WhatsApp Business', 'communication', 'Meta WhatsApp Cloud API', 'WHATSAPP_TOKEN,WHATSAPP_PHONE_ID', 'Not Configured'),
('sms', 'SMS Gateway', 'communication', 'Local SMS Provider', 'SMS_API_KEY,SMS_SENDER_ID', 'Not Configured'),
('payment', 'Payment Gateway', 'finance', 'Bank/Stripe/PayFast/JazzCash', 'PAYMENT_SECRET_KEY,PAYMENT_WEBHOOK_SECRET', 'Not Configured'),
('hr', 'HR/Payroll Integration', 'hr', 'HRIS/Payroll API', 'HR_API_URL,HR_API_KEY', 'Not Configured'),
('digital_sign', 'Digital Signature Provider', 'certificate', 'PKI/eSign Provider', 'SIGNING_API_KEY,SIGNING_CERT_ID', 'Not Configured')
on conflict (connector_id) do nothing;

create table if not exists integration_events (
  event_id uuid primary key default gen_random_uuid(),
  connector_id text references integration_connectors(connector_id),
  event_type text not null,
  payload jsonb default '{}'::jsonb,
  status text default 'Queued',
  retry_count int default 0,
  error_message text,
  created_at timestamp default now(),
  processed_at timestamp
);
create index if not exists idx_integration_events_status on integration_events(status, created_at);

create table if not exists portal_tenants (
  tenant_id uuid primary key default gen_random_uuid(),
  tenant_type text not null check (tenant_type in ('Client','Designer','Shipyard','Vendor','Flag','PSC','Insurance','Subcontractor')),
  tenant_name text not null,
  external_ref text,
  status text default 'Active',
  created_at timestamp default now()
);

create table if not exists portal_user_access (
  access_id uuid primary key default gen_random_uuid(),
  user_id text not null,
  tenant_id uuid references portal_tenants(tenant_id),
  access_role text not null,
  can_view boolean default true,
  can_create boolean default false,
  can_update boolean default false,
  can_approve boolean default false,
  status text default 'Active',
  created_at timestamp default now()
);
create index if not exists idx_portal_access_user on portal_user_access(user_id, tenant_id, status);

create table if not exists external_records_scope (
  record_scope_id uuid primary key default gen_random_uuid(),
  record_table text not null,
  record_id text not null,
  tenant_id uuid references portal_tenants(tenant_id),
  sensitivity text default 'External Restricted',
  created_at timestamp default now(),
  unique(record_table, record_id, tenant_id)
);
create index if not exists idx_external_scope_record on external_records_scope(record_table, record_id);

create table if not exists immutable_audit_log (
  audit_id uuid primary key default gen_random_uuid(),
  event_time timestamp default now(),
  actor_user_id text,
  actor_role text,
  event_type text not null,
  record_table text,
  record_id text,
  before_hash text,
  after_hash text,
  details jsonb default '{}'::jsonb,
  ip_address text,
  user_agent text
);

create or replace function prevent_audit_mutation()
returns trigger as $$
begin
  raise exception 'immutable_audit_log is append-only';
end;
$$ language plpgsql;

drop trigger if exists trg_prevent_audit_update on immutable_audit_log;
create trigger trg_prevent_audit_update
before update or delete on immutable_audit_log
for each row execute function prevent_audit_mutation();

create table if not exists security_events (
  security_event_id uuid primary key default gen_random_uuid(),
  user_id text,
  event_type text not null,
  severity text default 'Normal',
  details jsonb default '{}'::jsonb,
  resolved text default 'No',
  created_at timestamp default now()
);
create index if not exists idx_security_events_user on security_events(user_id, created_at desc);

create table if not exists mfa_status (
  user_id text primary key,
  mfa_enabled boolean default false,
  mfa_method text,
  last_verified_at timestamp,
  backup_codes_hash text,
  updated_at timestamp default now()
);

create table if not exists login_lockouts (
  user_id text primary key,
  failed_attempts int default 0,
  locked_until timestamp,
  last_failed_at timestamp,
  updated_at timestamp default now()
);

create table if not exists field_offline_queue (
  offline_id uuid primary key default gen_random_uuid(),
  user_id text not null,
  device_id text,
  assignment_id text,
  evidence_type text,
  local_payload jsonb default '{}'::jsonb,
  gps_lat numeric,
  gps_lon numeric,
  captured_at timestamp,
  sync_status text default 'Pending',
  server_record_id text,
  created_at timestamp default now(),
  synced_at timestamp
);
create index if not exists idx_field_queue_user on field_offline_queue(user_id, sync_status, created_at);

create table if not exists certificate_trust_records (
  trust_id uuid primary key default gen_random_uuid(),
  certificate_id text not null,
  certificate_hash text not null,
  signer_user_id text,
  signer_role text,
  signing_provider text,
  signature_ref text,
  qr_verification_url text,
  status text default 'Valid',
  revoked_reason text,
  issued_at timestamp default now(),
  revoked_at timestamp
);
create unique index if not exists idx_certificate_trust_cert on certificate_trust_records(certificate_id);

create table if not exists production_uat_results (
  uat_id uuid primary key default gen_random_uuid(),
  role_name text not null,
  test_case text not null,
  expected_result text not null,
  actual_result text,
  status text default 'Not Tested',
  tested_by text,
  tested_at timestamp,
  evidence_link text,
  remarks text
);
create index if not exists idx_uat_role_status on production_uat_results(role_name, status);

create table if not exists workflow_enforcement_rules (
  rule_id text primary key,
  rule_name text not null,
  applies_to text not null,
  rule_condition text not null,
  blocking_level text default 'Hard Block',
  status text default 'Active',
  created_at timestamp default now()
);

insert into workflow_enforcement_rules (rule_id, rule_name, applies_to, rule_condition, blocking_level)
values
('no_assignment_without_authorization', 'No survey assignment without valid authorization', 'Survey Assignment', 'authorized=true and certificate_valid=true and no_restriction=true and available=true', 'Hard Block'),
('no_superseded_drawing_use', 'No superseded drawing use', 'Document Control', 'document_status=Released and latest_revision=true', 'Hard Block'),
('no_certificate_without_approval', 'No certificate without approval', 'Certificate Issuance', 'technical_approved=true and qmr_cleared=true and signer_present=true', 'Hard Block'),
('no_authorization_without_evidence', 'No authorization without evidence', 'Authorization', 'training_passed=true and practical_evidence=true and tutor_recommended=true and technical_interview=true', 'Hard Block'),
('external_records_rls', 'External portal data isolation', 'External Portals', 'tenant_id=current_user_tenant_id', 'Hard Block')
on conflict (rule_id) do nothing;

-- OPTIONAL RLS EXAMPLE: adapt auth.uid() mapping to your Supabase auth model before enabling in production.
-- alter table portal_user_access enable row level security;
-- create policy portal_user_own_access on portal_user_access
--   for select using (user_id = auth.uid()::text);
-- alter table external_records_scope enable row level security;
-- create policy external_records_by_tenant on external_records_scope
--   for select using (tenant_id in (select tenant_id from portal_user_access where user_id = auth.uid()::text and status='Active'));

-- Production notes:
-- 1) Run this SQL after the main schema.
-- 2) Enable RLS only after mapping app users to Supabase auth users.
-- 3) Test all policies using the Role UAT Matrix.
