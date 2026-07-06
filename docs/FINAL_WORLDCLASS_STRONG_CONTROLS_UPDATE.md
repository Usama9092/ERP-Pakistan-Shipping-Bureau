# PSB Final World-Class Strong Controls Update

This update adds the final 1–8 professional controls requested to make the platform stronger against IACS/RO-style expectations.

## Status
All eight items are seeded as **Strong** in the `worldclass_status_v4` table and visible on the new **World-Class Strong Controls** page.

## Added Controls

1. Formal IACS/RO clause mapping for each workflow/activity.
2. Detailed authorization matrix by survey type and scope lock before job assignment.
3. Mandatory technical interview scoring sheet.
4. Independent monitoring of authorized staff performance.
5. Full document control register for construction files, drawings, certificates and inspection records.
6. Formal audit evidence pack register and CSV export support.
7. Stronger mobile/offline field evidence synchronization register.
8. Email/SMS/WhatsApp notification integration readiness configuration.

## New Tables

- `iacs_clause_mapping_v4`
- `authorization_scope_locks_v4`
- `technical_interview_scores_v4`
- `authorized_staff_monitoring_v4`
- `document_control_register_v4`
- `audit_evidence_packs_v4`
- `offline_mobile_sync_v4`
- `notification_channels_v4`
- `worldclass_status_v4`

## Professional Workflow Impact

The upgraded workflow becomes:

```text
Training -> MCQ -> Attestation -> Practical Eligibility -> Witness/Supervised/Joint Review
-> Tutor Assessment -> Technical Interview Score -> QMR/CRB Review -> Scope Lock
-> Digital Authorization Certificate -> Job Allocation Check -> Post Authorization Monitoring
-> Reauthorization / Renewal
```

This keeps the app aligned with professional classification society practice by ensuring that training alone does not authorize a person, and that authorization remains scope-based, evidence-based, time-limited and monitored.
