# Pakistan Shipping Bureau — World-Class HRDM / Classification Competency Platform

This is a Streamlit + Supabase/PostgreSQL + Render-ready system for PSB.

## What is included

- Role-based dashboards
- Admin control center
- Theoretical training matrix
- Trainer course creation
- File uploads for PDF/PPT/DOC/TXT/video/evidence
- MCQ generation from uploaded/extracted content
- Development plans for trainees/probationers
- Assigned mentor/tutor workflow
- Field exposure matrix
- Witness survey assessment
- Supervised survey assessment
- Plan appraisal joint/independent review workflow
- Scope-specific authorization matrix
- Competency levels
- Technical authority structure
- Competency Review Board (CRB)
- Digital approval/signature flow
- QR authorization certificate
- Risk-based job assignment engine
- KPI and utilization tracking
- CPD/seminar/refresher records
- Technical knowledge library
- QMS/CAPA/audit trail
- Revalidation / reauthorization workflow
- Backup/export system
- Supabase file storage support
- SQLite fallback for local testing
- Render deployment files

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Render

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

## PostgreSQL / Supabase migration files

- `database/postgres_schema.sql` contains the complete PostgreSQL schema, indexes, and references for all app tables.
- `database/supabase_rls_template.sql` enables row level security on all supported tables after the schema is created.
- `database/supabase_rls_and_storage.sql` provides a Supabase-ready RLS template and storage guidance.

## Environment variables for Render

```text
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_BUCKET=psb-hrdm-files
PUBLIC_URL=https://training.psbureau.org
```

## Default demo logins

```text
admin / Admin@1234
trainer / Trainer@1234
tutor / Tutor@1234
technical / Tech@1234
principal / Principal@1234
qmr / QMR@1234
coordinator / Coord@1234
surveyor / Surveyor@1234
appraiser / Appraiser@1234
management / Mgmt@1234
```

## International classification society workflow

The workflow follows:

```text
Admin assigns role/path/mentor
→ Trainer assigns theoretical training
→ Candidate passes training and assessment
→ Tutor records witness surveys
→ Tutor records supervised survey or plan review
→ Readiness engine checks evidence
→ Authorization request
→ Principal/Technical/QMR/CRB/Management approval
→ QR certificate
→ Risk-based job allocation
→ Annual review, CPD, refresher and reauthorization
```


## PLUS 12 Advanced Modules

1. Technical Authority Framework
2. Survey Report Review System
3. Plan Review Quality Monitoring
4. Competency NCR / Surveyor Performance NCR
5. AI Competency Gap Advisor
6. Annual Competency Review Board
7. Authorization Restriction Matrix
8. Client / Shipowner / Shipyard Feedback
9. Succession Planning / Talent Pipeline
10. Workforce Planning / Resource Forecasting
11. Accreditation Readiness Dashboard
12. Rule Interpretation / Technical Decision Portal

## IMPORTANT: Prevent Data Loss on Render

This version prevents accidental data loss by blocking temporary SQLite/local storage on Render.

Set these Render Environment Variables:

```text
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_BUCKET=psb-hrdm-files
PUBLIC_URL=https://training.psbureau.org
APP_ENV=production
```

Local SQLite is allowed only for local testing. On Render, the app will stop and show a configuration warning if `DATABASE_URL` is not PostgreSQL/Supabase.

Uploaded files also require Supabase Storage on Render, so training files, evidence, certificates and records do not disappear after restart/redeploy.


## Final Classification Society ERP Governance Layer

Added Competency Manager, Survey Operations Manager, Plan Approval Manager, Document Controller, Technical Monitor, Client Owner Portal, ERP Governance Hub, role permission matrix, document control register, technical monitoring, assignment lock checks, advanced practical development, technical knowledge repository, and CEO executive ERP analytics.

## V10 State-of-the-Art Final Layer

This package includes the final maturity improvements:

- Role Maturity Optimizer
- Workflow Task Center
- Survey Logbook & Competency Decay
- Plan Review Peer Quality
- Controlled Transmittals
- Enterprise Health Center
- State-of-Art UI/UX Design Guide
- Performance Safeguards

These features strengthen workflow maturity, role accountability, document control, competency governance, operational integration, UI/UX and performance safety for Render/Supabase deployment.


## V11 World-Class International ERP Intelligence Layer

This release adds the final state-of-the-art improvements requested for a modern Classification Society ERP:

- Enterprise Search across training, certificates, jobs, NCR/CAPA, knowledge and interpretations
- Knowledge Graph linking training, competency, surveys, plan appraisal, NCRs and certificates
- AI Competency Advisor for readiness, gaps, risk and authorization recommendations
- Lessons Learned Portal for major NCRs, surveys, projects, audits and technical decisions
- Enterprise Notification Engine with escalation and email/SMS/WhatsApp readiness
- Mobile App / Offline Sync Center with GPS, timestamp and evidence validation
- Client Self-Service Portal for survey requests, certificate status, NCR status and survey history
- World-Class Role, Activity and Information Flow matrix

The platform is now structured around governance, competency, authorization, survey operations, plan appraisal, new construction, QMS, workforce planning, technical knowledge, client/shipyard/designer portals, document control and executive analytics.


## V12 Complete Enterprise ERP Closure

Added final production ERP layers: communication integrations, native mobile operations readiness, strict document enforcement, expanded client self-service, commercial module, HR integration, rule/circular change management and enterprise workflow engine.


## V13 Final International ERP Hardening

Added production security, external portal isolation, database enforcement controls, real integration connector registry, field mobile app blueprint, production UAT tests, workflow SLA rules, UI/UX final polish register and release readiness checks.

## V14 Final Production Closure

The latest version includes final live production readiness improvements: live integration connectors, mobile/PWA offline work queues, database hard-rule registers, external portal isolation verification, production security operations, role-specific landing UX, full UAT testing and live ERP launch control.

Use the following new pages from Admin/Management/CEO workspaces:
- Final Live Integration Center
- Final Mobile PWA Operations
- Final Database Hard Rules
- Final Portal Isolation
- Final Security Operations
- Final Role Landing UX
- Final UAT Test Suite
- Final Live ERP Launch Control

Before true go-live, configure secrets in Render and apply Supabase RLS/database trigger rules using the included schema and RLS notes.


## V15 Final Stakeholder Closure

This build adds the remaining international Classification Society ERP stakeholders and controls: Finance Officer, HR Officer, IT/Security Admin, Legal/Contract Officer, Customer Support, Flag Administration, PSC Viewer, Insurance/P&I Viewer, Manufacturer/Vendor, and Subcontracted Surveyor. It also adds commercial workflow, HR availability checks, security incident control, legal contract/dispute control, customer support ticketing, external stakeholder read-only portals, and expanded client certificate/payment self-service.

## V16 Final Live Production Closure

This package includes the V16 final production hardening layer:

- Live Integration Operations
- Immutable Audit Control
- External Portal Data Isolation
- Internal Classification Society Portal
- External Stakeholder Portal
- Backend Communication Flow Validator
- Role UAT Matrix
- Digital Signature Trust Center
- Field PWA Operations
- Finance + HR Integration Verification
- Database Rules Verification
- Final V16 Gap Closure

Apply `database/v16_final_live_production_hardening.sql` after the main schema and complete role-based UAT before enabling production access.


## V17 Final Production Closure

Added final role registry consistency, immutable audit SQL, external isolation hardening, mandatory evidence policy, assignment/document hard-rule tables, integration readiness register and final role-gap review page. Apply `database/v17_final_production_role_security_hardening.sql` before live use.


## V18 Final Launch Testing + HR Accounting

Added live pre-launch readiness checks, HR master, leave/availability, payroll, accounting ledger, admin process flow, integration environment checks and V18 launch gap closure dashboard. Apply `database/v18_final_launch_hr_accounting.sql` before using the HR/accounting forms.

## V19 Rule Development Automation

V19 adds a dedicated Rule Development Automation portal for Rule Development Representatives and technical management. It supports source monitoring, impact assessment, approval workflow, training action generation, communication logging, and controlled release of rule/circular revisions.

New menu: **Rule Development Automation**

Primary role: **Rule Development Rep**

Supporting roles: Technical Manager, QMR, Document Controller, Trainer, Management, Admin.


## V20 Authorization Lifecycle & Reauthorization

Added full career-long authorization lifecycle for Surveyors, New Building Surveyors, Plan Appraisers, Auditors, Technical Authorities and Technical Monitors. Includes CPD, refresher training, annual monitoring, rule update training impact, Competency Board review, expiry triggers, restrictions/suspensions and personal reauthorization status center.
