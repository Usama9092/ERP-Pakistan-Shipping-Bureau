# CEO, Person-Wise Training Compliance & Escalation Update

This build implements the coding-ready URD for CEO governance and person-wise training compliance.

## Added in Code

- Added `CEO` role to the role list and sidebar workflow.
- Added CEO Executive Governance Dashboard with tabs for:
  - Executive Overview
  - Role Compliance
  - Person Performance
  - Trainer/Tutor Performance
  - Training Performance
  - Overdue & Escalations
  - Authorization Approvals
  - Reports
- Added person-wise assignment generator.
  - Training can be assigned to selected persons.
  - Training can be assigned to all active persons in selected roles.
  - One individual `training_records` row is created per person.
- Added overdue reminder/escalation engine.
  - User popup notification after due/overdue training.
  - Trainer/Tutor reminder for incomplete trainee.
  - Management escalation after 3 overdue days for mandatory training.
  - CEO escalation after 7 overdue days for critical/mandatory training.
- Added popup notification panel after login.
- Added trainer/tutor performance table.
- Added role-wise and person-wise compliance tables.
- Added training-wise performance table.
- Added CEO authorization approval decision recording.
- Added audit trail entry for CEO decisions.
- Added default CEO login for upgraded/existing deployments if no CEO user exists.

## Default CEO Login

Login ID: `ceo`  
Password: `CEO@1234`

Change this password immediately after first deployment.

## Database Migration Fields Added

The app now auto-adds the following fields where missing:

### users
- `designation`
- `reports_to`
- `mandatory_training_exempt`

### trainings
- `mandatory_for_authorization`
- `ceo_visible`
- `created_by`

### training_records
- `trainer_id`
- `trainer_name`
- `department`
- `assigned_by`
- `assignment_type`
- `material_accessed`
- `recording_accessed`
- `is_overdue`
- `reminder_count`
- `escalation_level`
- `authorization_impact`

### notifications
- `recipient_role`
- `priority`
- `popup_required`
- `related_training_id`
- `related_record_id`
- `read_on`

### authorization_requests
- `ceo_decision`
- `ceo_comments`
- `ceo_signature`
- `ceo_decision_date`

### New table
- `escalation_logs`

## Supabase Notes

This build uses lightweight SQL migrations through SQLAlchemy. For Supabase/PostgreSQL, the migration uses `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`. For SQLite testing, it uses `PRAGMA table_info` before adding columns.

## Important Workflow

1. Admin/Trainer creates training.
2. Admin/Trainer assigns training by selected persons or by role.
3. System creates person-wise records.
4. Assigned users receive popup notifications.
5. Incomplete/overdue training triggers reminders and escalations.
6. CEO sees organization-wide compliance and escalation status.
7. CEO can approve/reject authorization requests in the CEO dashboard.
