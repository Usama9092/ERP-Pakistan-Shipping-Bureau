# V19 Rule Development Automation Update

This release adds an automated internal Classification Society Rule Development role and workflow.

## Rule Development Rep responsibilities
- Monitor IMO, IACS, flag, class, PSB procedure and technical interpretation updates.
- Open rule/circular development projects.
- Record affected rules, forms, checklists, certificates and training.
- Run impact assessment for survey, plan appraisal, statutory, document control and software workflows.
- Route to Technical Manager, QMR, Management and Document Controller.
- Trigger training/awareness/assessment actions for affected roles.
- Queue communication to internal staff and external stakeholders where required.
- Register controlled release and supersession of rule documents.

## Workflow
Source update → Rule project → Impact assessment → Technical review → QMR compliance review → Management approval → Controlled release → Training/acknowledgement → implementation monitoring → closure.

## Communication
- Rule Development Rep → Technical Authority: impact and technical draft.
- Technical Authority → QMR: technical decision and compliance effects.
- QMR → Management: risk and readiness.
- Document Controller → internal/external users: released current document only.
- Trainer → affected staff: training, MCQ and awareness.
- Client/Flag/Shipyard/Designer portals receive only released circulars.

## Added files
- `database/v19_rule_development_automation.sql`
- `docs/V19_RULE_DEVELOPMENT_AUTOMATION_UPDATE.md`

## Deployment note
The app creates V19 tables at startup, but production teams should also apply the SQL file in Supabase for full index creation and audit visibility.
