# PSB Training App — Supabase, UI/UX and Workflow Review

## Supabase/PostgreSQL readiness status

The app is now suitable for Supabase PostgreSQL deployment when these environment variables are configured on Render or the hosting server:

```text
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:5432/postgres
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVICE_ROLE_KEY
SUPABASE_BUCKET=psb-hrdm-files
PUBLIC_URL=https://training.psbureau.org
APP_ENV=production
```

### Important security note
This Streamlit app uses the Supabase service-role key only on the server side. Do not place the service-role key in frontend JavaScript, public GitHub files, screenshots, or client-side code.

## What was improved in this version

1. Fixed a cache-clearing recursion bug that could freeze the app after database inserts, updates, and deletes.
2. Improved SQLAlchemy connection handling for PostgreSQL/Supabase and SQLite test mode.
3. Added PostgreSQL indexes for frequently used dashboard, login, trainee, notification, file, and assessment queries.
4. Optimized login to query only the matching user instead of loading the full users table.
5. Fixed the succession planning database column mismatch from `current_role` to `current_role_name` for PostgreSQL compatibility.
6. Improved professional UI styling: cleaner sidebar, stronger dashboard header, cards, rounded sections, better buttons, tabs, tables, and metrics.
7. Kept trainee training material workflow read-only.
8. Preserved trainer/admin ability to upload links, schedule meetings, assign users, mark attendance, and upload recordings.

## Workflow check

### Admin workflow
Admin can create users, assign roles, define training matrix, manage files, check authorizations, manage CRB, monitor KPI, QMS, backup, and management dashboards. This is appropriate for system control.

### Trainer workflow
Trainer can create courses, attach slide/video/reference/LMS/meeting/recording links, generate MCQs, assign training, and update attendance. This is appropriate for training delivery.

### Trainee workflow
Trainee can access only assigned trainings. Training details and files are read-only. Trainee can open assigned materials, confirm completion, view recording when uploaded, and attempt assessments. This is appropriate and prevents editing.

### Tutor/Technical/QMR/Management workflow
Evidence review, competency, CRB, authorization, annual board, restrictions, and approval workflows are present. This aligns with classification-society competency governance.

## Remaining production recommendations

1. Use Render paid Starter or another always-on hosting plan. Render Free can sleep after inactivity, which cannot be fully solved in code.
2. Use Supabase PostgreSQL for all structured data and Supabase Storage for uploaded files.
3. Keep table sizes controlled by archiving old audit logs and old notifications periodically.
4. Do not enable Supabase RLS policies unless you are using Supabase Auth directly. This app uses server-side service-role access, so app-level role control is currently handled inside Streamlit.
5. Use a custom domain such as `training.psbureau.org` with HTTPS.
6. For large uploaded PDFs/PPTs, avoid extracting huge text on every upload or keep uploads below practical file-size limits.
7. Set `DB_POOL_SIZE=5` and `DB_MAX_OVERFLOW=10` on Render for normal usage; increase only if the database plan supports it.

## Why the app may still feel slow

Streamlit reruns the script on every button click. This is normal behavior. The app is now improved by caching, filtered queries, and indexes, but hosting plan, Supabase region, large tables, and uploaded file size can still affect response time.

