
-- V18 FINAL LAUNCH + HR ACCOUNTING CLOSURE
create table if not exists hr_employee_master_v18 (
    employee_id text primary key,
    name text not null,
    department text,
    role_name text,
    grade text,
    employment_status text default 'Active',
    cost_center text,
    supervisor_id text,
    created_at text
);
create table if not exists hr_leave_availability_v18 (
    leave_id text primary key,
    employee_id text,
    start_date text,
    end_date text,
    leave_type text,
    status text,
    remarks text,
    created_at text
);
create table if not exists hr_payroll_v18 (
    payroll_id text primary key,
    employee_id text,
    period text,
    basic_salary numeric default 0,
    allowances numeric default 0,
    deductions numeric default 0,
    net_pay numeric default 0,
    status text default 'Draft',
    created_at text
);
create table if not exists accounting_ledger_v18 (
    entry_id text primary key,
    account_name text,
    reference_no text,
    debit numeric default 0,
    credit numeric default 0,
    remarks text,
    status text default 'Draft',
    created_at text
);
create table if not exists integration_health_v18 (
    integration_id text primary key,
    provider_name text,
    integration_type text,
    env_key_name text,
    status text default 'Not Tested',
    last_tested_at text,
    last_result text
);
create table if not exists launch_uat_results_v18 (
    uat_id text primary key,
    role_name text,
    test_case text,
    expected_result text,
    actual_result text,
    status text,
    tested_by text,
    tested_at text
);
create index if not exists hr_employee_master_v18_role_idx on hr_employee_master_v18(role_name, employment_status);
create index if not exists hr_leave_availability_v18_emp_idx on hr_leave_availability_v18(employee_id, status, start_date, end_date);
create index if not exists hr_payroll_v18_emp_period_idx on hr_payroll_v18(employee_id, period);
create index if not exists accounting_ledger_v18_ref_idx on accounting_ledger_v18(reference_no, account_name);

-- Assignment availability guard concept for PostgreSQL deployments:
-- Use this as a trigger/policy in production to block assignment of staff on approved leave.
-- The application also checks availability in the HR + Accounting System page.
