# V15 Final Stakeholder, Role, Activity and Communication Closure

This update closes the remaining Classification Society ERP stakeholder gaps identified in the V14 evaluation.

## Added roles

- Finance Officer
- HR Officer
- IT/Security Admin
- Legal/Contract Officer
- Customer Support
- Flag Administration
- PSC Viewer
- Insurance/P&I Viewer
- Manufacturer/Vendor
- Subcontracted Surveyor

## Added role pages

- Finance & Commercial Control
- HR Availability & Leave Control
- IT Security Operations
- Legal Contract & Dispute Control
- Customer Support Ticket Center
- Flag Administration Portal
- PSC / Insurance Viewer
- Manufacturer Vendor Portal
- Subcontracted Surveyor Workspace
- Client Certificate Center
- Client Survey History
- Client Payment Center
- V15 Final Gap Closure Review

## Key professional controls

### 1. Finance / commercial workflow
Client request → quotation → acceptance → survey → invoice → payment → certificate release control.

### 2. HR assignment integration
Survey assignment checks active employment, leave, availability, conflict of interest, competence and authorization.

### 3. IT/security operations
Adds clear control owners for MFA, password reset, lockout, session timeout, backup monitoring, audit log and incident response.

### 4. Legal / contract governance
Supports client contracts, liability clauses, disputes and legal correspondence.

### 5. Customer support front door
Ticket routing for survey requests, certificate queries, NCR status, commercial queries and complaints.

### 6. External statutory / stakeholder views
Flag, PSC and Insurance/P&I see read-only restricted status information only.

### 7. Manufacturer/vendor portal
Supports material certificate submission, type approval, vendor audit, CAPA and service report communications.

### 8. Subcontracted surveyor workspace
Subcontracted surveyors see assigned work only, latest approved documents, evidence upload and report submission.

## Database additions

The schema now includes finance, HR availability, security incidents, legal contracts, support tickets, external party access, manufacturer/vendor, subcontracted surveyor and immutable audit events.

## Production reminder

For live use, configure Supabase RLS so external users only see data mapped to their `client_id`, `project_id`, `vendor_id` or `surveyor_id`.
