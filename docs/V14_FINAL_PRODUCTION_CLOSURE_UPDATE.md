# V14 Final Production Closure Update

This update adds the final items required to move the PSB platform from a feature-complete ERP prototype toward a serious live international Classification Society ERP platform.

## Added

1. **Live Integration Center**
   - Email, WhatsApp, SMS, payment, HR/payroll, finance and digital signature connector readiness.
   - Uses Render environment variables; no secrets are hard-coded.

2. **Mobile / PWA Field Operations**
   - Offline inspection work queue design.
   - GPS, photo, evidence, signature and sync rules.

3. **Database Hard Rules**
   - No survey assignment without valid authorization.
   - No certificate without approval evidence.
   - No superseded drawing in active inspection.
   - No authorization without evidence.

4. **External Portal Isolation**
   - Designer, shipyard and client data separation register.
   - Supabase RLS policy notes included.

5. **Production Security Operations**
   - 2FA, password reset, login lockout, session timeout and protected audit logs.

6. **Role Landing UX Builder**
   - Defines role-specific first screens: My Tasks, Alerts, Approvals, Deadlines and KPIs.

7. **Full UAT Test Suite**
   - Role-by-role launch testing register with release blocker tracking.

8. **Live ERP Launch Control**
   - Single launch readiness dashboard for final go-live review.

## Production Go-Live Remaining Actions

- Add real API keys in Render environment variables.
- Apply Supabase RLS policies to real tables.
- Convert hard-rule checks into PostgreSQL triggers/checks where appropriate.
- Complete UAT evidence for every role.
- Validate external portal isolation using test accounts.
- Configure real digital signature provider.
- Configure email/WhatsApp/SMS/payment/HR integrations.
