# EPAS v2.5 — Complete Workflow Enforcement Release

This package is cumulative from v2.4 and is the full application baseline plus the v2.5 workflow-enforcement hardening migration.

## Migration order

Apply the existing migrations in order through `production_v2_4_state_of_art_lifecycle.sql`, then apply:

`database/production_v2_5_workflow_enforcement_hardening.sql`

## Core operational rule

- Shipyard initiates NSC Survey RFI only.
- Owner initiates In-Service RFI only.
- Ship Management initiates In-Service RFI only.

## v2.5 final workflow gates

1. Project scope / phase gate
2. RFI policy and project membership
3. Immutable survey scope version
4. DM assignment + resource eligibility snapshot
5. Surveyor assignment acceptance
6. Controlled approved-drawing package
7. Immutable drawing handover acknowledgement
8. Revision-impact decision when a new approved revision exists
9. Mandatory pre-survey checklist
10. Survey start gate
11. Frozen survey execution basis
12. Survey report submission gate
13. Exact observation/corrective-action evidence authorization
14. Frozen certificate decision package
15. Real DM certificate-package acknowledgement
16. Certificate issuance gate
17. Ship Register status projection
18. Recurring In-Service schedule
19. Role-filtered due notifications
20. Project-authorized timeline and control-tower reads

## Validation

- Static/non-browser pytest suite: 97 passed.
- Python compilation: passed.
- Live browser/Supabase/RLS/Storage acceptance requires the deployed environment and is not represented as passed here.
