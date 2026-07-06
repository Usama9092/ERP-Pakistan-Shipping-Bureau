# Plan Appraisal Domain-Based Duty Assignment Update

## What Was Added

This update adds a dedicated **Plan Appraisal Duty Assignment** workflow under the Job Allocation module.

Admin/Management/CEO/Chief Plan Appraiser/Technical Manager can now:

1. Create a Plan Appraisal duty.
2. Select the specific appraisal domain/discipline.
3. Specify document/plan type and revision.
4. Assign the duty only to a person authorized for that exact appraisal domain.
5. Track assignment basis, assigned by, and assigned date.
6. Notify the assigned plan appraiser through the app.

## Plan Appraisal Domains Supported

- Hull Structure and Naval Architecture
- Machinery and Piping Systems
- Electrical and Automation
- Statutory and Safety
- Environmental and Alternative Fuels
- Materials and Equipment Certification

## Authorization Logic

A person is eligible for a Plan Appraisal job only when:

- The person has an approved authorization request.
- The authorization status is `Management Approved`.
- The authorization scope matches `Plan Appraiser - <Selected Domain>`.
- The job type is `Plan Appraisal`.
- The authorization is not expired.
- The person is available.
- The person meets the minimum competency level.

## New Job Fields

The `job_requests` table now supports:

- `appraisal_domain`
- `plan_discipline`
- `plan_document_type`
- `plan_revision`
- `assignment_basis`
- `assigned_by`
- `assigned_on`

## Example

If Admin creates a job for:

- Domain: Electrical and Automation
- Document Type: Electrical Single Line Diagram

The system will only show candidates holding:

`Plan Appraiser - Electrical and Automation`

This prevents assigning Hull, Machinery, Statutory, Environmental, or Materials plan appraisal work to a person not authorized in that domain.

## Deployment

No manual database rebuild is required. Existing SQLite/PostgreSQL/Supabase databases are migrated automatically using `ensure_schema_column()` when the app starts.
