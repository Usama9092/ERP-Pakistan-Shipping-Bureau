# V13 Final International Classification Society ERP Hardening

This version adds the last production-readiness layer to transform the platform from a strong prototype into an international classification society ERP launch candidate.

## Added

1. Production Security Center: 2FA readiness, password reset/lockout, session timeout, RLS, tamper-protected audit log.
2. External Portal Isolation: designer, shipyard, client and vendor data separation rules.
3. Database Enforcement Center: hard business rules for assignment, drawing revision, certificates and authorization gates.
4. Real Integration Connectors: email, WhatsApp, SMS, payment gateway, HRMS and digital signature provider registry.
5. Field Mobile App Blueprint: offline survey, GPS, QR, photos, signatures and sync specifications.
6. Production Testing & UAT: release-blocker test suite by role and workflow.
7. Workflow SLA Rules: task due dates, reminders, escalations and closure evidence.
8. UI/UX Final Polish Register: page-level usability, performance, mobile and accessibility controls.
9. Final Release Readiness: go-live checklist for Render/Supabase.

## Go-live condition

Before real external users are added, configure production secrets, activate Supabase RLS, run all release-blocker tests, confirm backup/restore, and complete security review.
