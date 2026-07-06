# Enterprise Deployment Guide

1. Push this repository to GitHub.
2. Create/confirm Supabase PostgreSQL database.
3. Run `database/postgres_schema.sql` in Supabase SQL editor.
4. Run `database/supabase_rls_template.sql` and then adjust policies for production.
5. Configure Render environment variables from `.env.example`.
6. Deploy on Render using `render.yaml`.
7. Login as Admin and open Enterprise Upgrade Center.
8. Open Audit Readiness Engine and seed/verify evidence items.
9. Open Workforce Forecasting and generate forecast from live data.
10. Validate external roles Designer and Shipyard Representative with limited access.

Important: RLS policies in this package are a template. For production, replace broad template policies with organization-specific least-privilege policies.
