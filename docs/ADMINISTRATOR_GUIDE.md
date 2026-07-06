# Administrator Guide

## Initial Setup
1. Install dependencies with pip install -r requirements.txt.
2. Start the app with streamlit run app.py.
3. Configure DATABASE_URL and other secrets for production deployments.

## Maritime Modules
- Use Maritime Registry to manage ships and their core profile details.
- Use Maritime Surveys to manage dynamic digital checklists.
- Use the notification center for survey and certificate alerts.
- Use the project information section to view centralized system metadata.

## Operations
- Keep survey types and checklists updated through the survey center.
- Review overdue survey and certificate alerts regularly.
- Backup the SQLite database or use PostgreSQL/Supabase in production.
