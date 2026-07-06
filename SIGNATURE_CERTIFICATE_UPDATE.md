# Digital Signature & Authorization Certificate Update

## Added

- Admin-controlled digital signature management section inside **Admin Control Center**.
- Admin can upload signature images for:
  - CEO
  - Trainer
  - Tutor/Mentor
  - Principal Surveyor / Chief Plan Appraiser
  - QMR
  - Technical Manager
  - Management
- Signatures are saved in the database table `digital_signatures` as data URI image values.
- Each signature can be mapped to authorization levels:
  - All
  - Level 0 - Trainee
  - Level 1 - Witness Eligible
  - Level 2 - Supervised Eligible
  - Level 3 - Authorized
  - Level 4 - Senior Authorized
  - Level 5 - Principal / Lead
- Authorization certificate now automatically places stored signatures for Trainer, Tutor/Mentor, Principal/Chief Reviewer, QMR, Management, and CEO.
- CEO approval regenerates/updates the certificate so the CEO signature appears on the final certificate.
- Trainees cannot edit signatures or certificate signature placement.

## How to Use

1. Login as Admin.
2. Open **Admin Control Center**.
3. Go to **Authorized Digital Signatures for Certificates**.
4. Select signer role and person or choose role default signature.
5. Upload PNG/JPG/WebP signature image.
6. Select the levels where this signature applies.
7. Save signature.
8. When authorization certificate is issued or CEO approves, the certificate will use the active stored signatures.

## Supabase/PostgreSQL

The project now includes the `digital_signatures` table and related indexes in `database/postgres_schema.sql`. The app also performs safe runtime migrations using `ensure_schema_column()`.
