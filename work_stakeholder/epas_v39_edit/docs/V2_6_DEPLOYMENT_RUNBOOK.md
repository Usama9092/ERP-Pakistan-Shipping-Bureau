# EPAS v2.6 Deployment Runbook

1. Deploy the existing cumulative migrations through v2.5.
2. Apply `database/production_v2_6_final_workflow_acceptance_hardening.sql`.
3. Restart the application after the schema is live.
4. Configure the service scheduler (Supabase Cron or equivalent) to call `public.epas_scheduler_tick()` using service-role execution.
5. Run the static regression suite (`pytest -q tests --ignore=tests/test_workflow_smoke.py`).
6. Run the live seven/eight-role acceptance matrix against the real Supabase environment.

Recommended scheduler cadence: hourly. The scheduler is designed to be idempotent for the same day/cycle and records each run in `scheduler_runs`.

Do not grant `epas_scheduler_tick()` to `authenticated`.
