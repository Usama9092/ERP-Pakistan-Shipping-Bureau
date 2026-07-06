# PSB Version 2.0 Class Society Update

This update adds the missing role and workflow items identified in the review:

## Added Modules

1. Competency Matrix Engine
2. New Building Survey Operations
3. In-Service Survey Operations
4. Shipyard Inspection Request Portal
5. Designer Plan Submission Portal
6. Drawing Revision and Comment Resolution
7. NCR Closure Workflow
8. Role Activity Evaluation and Improvement Plan
9. Training failure / overdue escalation helper
10. Supabase/PostgreSQL schema additions

## Target End-to-End Workflow

Training Assigned → Material Completed → Secure MCQ Passed → Case Study/Interview → Witness/Supervised/Plan Review Evidence → Tutor Rating → Technical Authority Review → QMR Compliance Check → CRB → Management/CEO Approval → QR Authorization → Risk-Based Job Assignment → Annual Revalidation

## Roles Strengthened

- Trainee: personal competency and gap tracking.
- Trainer: failure/overdue and retest visibility.
- Tutor/Mentor: evidence-based competency rating.
- Surveyor: in-service and new-building evidence tracking.
- New Building Surveyor: inspection request, ITP stage and NCR workflow.
- Plan Appraiser: domain-based plan submission and revision tracking.
- Technical Authority: technical readiness review support.
- QMR: NCR and compliance evidence workflow.
- Management/CEO: risk and gap dashboards.
- Job Coordinator: better input for risk-based assignment.

## Deployment

Render and Supabase deployment files are retained. The app automatically creates the V2 tables on startup using `ensure_v2_schema()`. The SQL is also appended in `database/postgres_schema.sql` for direct Supabase execution if required.
