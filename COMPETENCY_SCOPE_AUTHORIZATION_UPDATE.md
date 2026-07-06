# Competency-Based Authorization Scope Update

This update converts **New Building Surveyor**, **In-Service Surveyor**, and **Plan Appraiser** into authorization pathways/scopes instead of simple login roles.

## What was added

- `Qualification Scopes` module
- Scope assignment by person
- Multiple authorizations per person
- Work-specific disciplines:
  - Hull Structure and Naval Architecture
  - Machinery and Piping Systems
  - Electrical and Automation
  - Statutory and Safety
  - Environmental and Alternative Fuels
  - Materials and Equipment Certification
- New Building Surveyor pathway
- In-Service Surveyor pathway
- Plan Appraiser pathway
- Theory + witness + assisted + independent evidence readiness logic
- Plan appraisal witness/joint review and independent review logic
- Authorization readiness matrix
- CSV export of scope matrix
- Supabase/PostgreSQL compatible migration table
- Render/GitHub deployable syntax-checked `app.py`

## Workflow

1. Admin/Tutor/Management assigns a person an authorization pathway and discipline.
2. Person completes theoretical training/assessment.
3. Tutor/Trainer records witness evidence.
4. Tutor/Trainer records assisted/supervised and independent work evidence.
5. System checks readiness.
6. Authorization request is created only when theory + practical evidence are complete.
7. Approval workflow issues authorization certificate.

## Important design decision

Login roles remain operational access roles. Technical authorizations are now person-wise scopes. One person may have both:

- New Building Surveyor - Electrical and Automation
- In-Service Surveyor - Electrical and Automation
- Plan Appraiser - Electrical and Automation

This is closer to classification society competency management practice.
