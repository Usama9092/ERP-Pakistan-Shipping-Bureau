# EPAS v3.1 — Final Multi-User Performance & Security Hardening

This package is the cumulative EPAS release built on v3.0 with the remaining
production gaps closed from the backend, frontend, security and performance audit.

## Key changes

- Authenticated Supabase clients are now **Streamlit-session scoped**. No
  authenticated client is globally cached across users.
- Streamlit uses a short-lived **session-local read cache** for dashboard,
  schedule, task, project and workflow reads. State-changing RPCs invalidate the
  cache.
- Role dashboards use a compact `epas_role_dashboard_bundle_v31()` RPC, reducing
  repeated round trips and removing avoidable N+1 KPI reads.
- Project/user/status/date indexes were added for the high-frequency workflow
  queries.
- Survey-cycle completion is now v3.1 controlled and refuses a missing/implicit
  survey interval rather than silently assuming 12 months.
- v3.1 scheduler wrapper adds retry bookkeeping and is service-role-only.
- Storage access is reasserted with role/phase-aware read policy, project-member
  upload control, and no direct authenticated update/delete.
- Controlled uploads now use centralized signature/type/size validation and a
  storage cleanup path when authoritative registration fails.
- Assignment/scope/checklist/execution objects carry row-version information for
  concurrency visibility.
- Streamlit navigation now renders one heavy operational surface at a time,
  reducing unnecessary database reads on every rerun.
- GM, DM, Engineer, Surveyor, Designer, Owner, Ship Management and Shipyard remain
  role-native and aligned to the supplied workflow diagrams.

## Deployment

1. Apply all cumulative migrations through v3.0.
2. Apply `database/production_v3_1_performance_security_final.sql`.
3. Execute `deployment/supabase_cron_v31.sql` once in the deployed Supabase project.
4. Install Python dependencies from `requirements.txt`.
5. Run Streamlit with `run_streamlit.sh` or the supplied `Dockerfile`.
6. Execute the live eight-role RLS/Storage/Cron/browser acceptance cases in
   `deployment/live_acceptance_v30.py` plus the v3.1 acceptance cases recorded in
   `workflow_acceptance_cases_v29`.

## Validation in build environment

- 178 static/regression tests passed.
- 1 browser smoke test is skipped in the build environment because Streamlit is
  not installed there.
