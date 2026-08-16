# EPAS v2.9 — Final Production Hardening

Electronic Plan Approval System — cumulative Streamlit + Supabase workflow application.

This package includes the cumulative EPAS workflow through v2.8 plus the v2.9 security, workflow enforcement, UI and deployment hardening release.

### Core business rules
- **Shipyard → NSC Survey RFI only**
- **Owner → In-Service Survey RFI only**
- **Ship Management → In-Service Survey RFI only**
- Plan Appraisal gates NSC where selected.
- NSC gates In-Service where selected.
- In-Service is a persistent phase and survey cycles recur.
- Surveyors receive only the relevant approved Plan Appraisal drawing revisions selected by DM.

### Runtime
Production is fail-closed. Supabase URL/key are required. Demo mode is disabled unless `EPAS_ENABLE_DEMO_MODE=1` is explicitly set for isolated non-production testing; the production `run_streamlit.sh` rejects that flag.

### Validation
Build-environment validation currently reports 154 passing regression/static tests and one browser smoke test skipped because Streamlit is not installed in the build environment. Live RLS, Storage, Cron and browser acceptance must be executed after deployment against the actual Supabase project.
