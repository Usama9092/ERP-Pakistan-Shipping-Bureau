# V18 Final Launch Testing + HR Accounting Update

This update adds the final pre-launch operational layer requested by Admin.

## Added in App
- V18 Live Pre-Launch Testing
- HR + Accounting System
- V18 Final Launch Gap Closure

## HR Accounting Process
Employee master -> role/department -> leave/availability -> assignment lock -> job -> quotation/invoice -> receipt/ledger -> certificate release control.

## Real-Time Testing
The system can test local runtime, database connection, role registry and required environment variable readiness. Real external API testing requires live provider credentials and deployed Render URL.

## Required Production Actions
1. Apply `database/v18_final_launch_hr_accounting.sql`.
2. Configure Render environment variables.
3. Run V18 Live Pre-Launch Testing page.
4. Run UAT role by role.
5. Verify Supabase RLS with separate test users.
