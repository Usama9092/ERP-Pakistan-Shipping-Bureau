# PSB Training App - Performance and Uptime Improvements

## Changes applied in this ZIP

1. Added cached filtered database reads with `db_where()` so pages do not always load full database tables.
2. Added `clear_db_cache()` so cache is cleared only after insert/update/delete.
3. Cached `init_db()` so table-creation checks do not run on every Streamlit click.
4. Optimized trainee training page to load only the assigned user record, selected training, selected files, selected MCQs, and selected assessment history.
5. Optimized notification creation to fetch only the target user instead of all users.
6. Changed training progress updates so one click updates only the relevant training record, not the entire training_records table.
7. Limited large table display to the latest 300 rows to prevent slow UI rendering. Full data can still be exported from Backup/Export.
8. Added Streamlit config improvements: disabled file watcher and minimized client toolbar for deployed runtime.

## Why the app was still slow

Streamlit reruns the full Python script after every button click, selectbox change, radio selection, form submit, or page navigation. If the app loads many tables, renders large dataframes, checks database schema, extracts files, or updates many records during each rerun, every click becomes slow.

## Deployment settings recommended on Render

Render Free web services sleep after inactivity. This is a platform limitation. For a professional app that should not go down, use at least Render Starter/paid instance or another always-on host.

Use these environment variables:

```text
DATABASE_URL=postgresql://...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_BUCKET=psb-hrdm-files
PUBLIC_URL=https://your-domain.com
PYTHONUNBUFFERED=1
STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
```

## Further upgrades that will make it much faster

1. Move from SQLite/local DB to Supabase PostgreSQL.
2. Add database indexes on frequently used columns:

```sql
create index if not exists idx_training_records_user_training on training_records(user_id, training_id);
create index if not exists idx_training_records_training on training_records(training_id);
create index if not exists idx_question_bank_training on question_bank(training_id);
create index if not exists idx_files_linked on files(linked_table, linked_id);
create index if not exists idx_notifications_user on notifications(user_id);
create index if not exists idx_users_login on users(login_id, email, status);
```

3. Use forms for all data entry so the app does not rerun after every typed field.
4. Split the single large `app.py` into smaller page modules.
5. Avoid rendering full audit trails, notifications, files, and backup tables on normal pages.
6. Do not extract PDF/DOCX/PPTX text during normal page load; do extraction only after upload.
7. Use pagination/search filters for large tables instead of showing everything.
