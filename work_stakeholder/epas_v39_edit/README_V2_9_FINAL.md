# EPAS v2.9 — Final Production Hardening

EPAS v2.9 is the cumulative release containing the complete application, database migrations, Streamlit UI, deployment material, tests, role diagrams and release documentation.

### Business rules
- Shipyard initiates **NSC Survey RFI only**.
- Owner initiates **In-Service Survey RFI only**.
- Ship Management initiates **In-Service Survey RFI only** and executes assigned corrective actions.
- Plan Appraisal gates NSC where Plan Appraisal is selected.
- NSC gates In-Service where NSC is selected.
- In-Service is a persistent phase; survey cycles recur indefinitely until a project/vessel is intentionally closed or suspended.
- Only relevant approved Plan Appraisal drawing revisions are handed to the assigned Surveyor.

### Production notes
- Runtime is fail-closed if Supabase configuration is missing.
- Demo mode is disabled by default and requires explicit opt-in for isolated development only.
- Scheduler is service-role-only and deployed through `deployment/supabase_cron_v29.sql`.
- Live RLS, Storage, Cron and browser acceptance must still be executed against the real Supabase project; the release does not fabricate those results.
