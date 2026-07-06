# PSB HRDM Training System — Render Deployment Guide

This guide ensures **all data is permanently stored** and persists across server restarts and redeployments.

## ⚠️ Critical: Data Persistence Requirements

**The application BLOCKS local SQLite on Render because data disappears after restart/redeploy.**

For production on Render, you **MUST** configure:
- ✅ **PostgreSQL database** (via `DATABASE_URL`)
- ✅ **Supabase Storage** (for file uploads)

## Deployment Options

### Option A: Render PostgreSQL + Supabase (Recommended)

#### 1. Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +" → PostgreSQL**
3. Configure:
   - **Name:** `psb-hrdm-db`
   - **Database:** `postgres`
   - **User:** `postgres`
   - **Region:** same as your web service
   - **PostgreSQL Version:** 15 or later
4. Click **Create Database**
5. Copy the **Internal Database URL** (this is your `DATABASE_URL`)

#### 2. Create Supabase Project

1. Go to [Supabase](https://supabase.com) and create a new project
2. Go to **Project Settings → API**
3. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **Service Role Key** → `SUPABASE_SERVICE_ROLE_KEY`
4. Create a storage bucket:
   - Go to **Storage** → **New Bucket**
   - Name: `psb-hrdm-files`
   - Make it **public**

#### 3. Create Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com) → **New +"** → **Web Service**
2. Connect your GitHub repository:
   - **Repository:** `Pakistan-Shipping-Bureau-Training`
   - **Branch:** `main`
3. Configure:
   - **Name:** `psb-hrdm-training`
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
4. Add **Environment Variables:**

```text
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/postgres
SUPABASE_URL=https://YOUR-PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=YOUR-SERVICE-ROLE-KEY
SUPABASE_BUCKET=psb-hrdm-files
PUBLIC_URL=https://YOUR-RENDER-APP.onrender.com
APP_ENV=production
```

5. Click **Create Web Service**
6. Wait 5-10 minutes for deployment
7. Access your app at the provided URL

### Option B: Render PostgreSQL + Supabase Storage (Alternative)

Same as Option A but using only Supabase for file storage instead of Render's file system.

### Option C: Supabase PostgreSQL + Supabase Storage (Full Supabase)

1. Create Supabase project
2. Get Supabase connection string from **Project Settings → Database**
3. Configure `DATABASE_URL` with Supabase PostgreSQL URL
4. Use same Supabase Storage setup as above

## Local Development

For local testing with SQLite (data DOES NOT persist but fine for development):

```bash
# Copy environment template
cp .env.example .env

# Set DATABASE_URL to local SQLite or PostgreSQL
DATABASE_URL=sqlite:///psb_hrdm_world_class.db

# Or use PostgreSQL locally:
DATABASE_URL=postgresql://postgres:password@localhost:5432/psb_hrdm

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

**Default demo logins:**
```text
admin / Admin@1234
trainer / Trainer@1234
tutor / Tutor@1234
```

## Data Persistence Verification

✅ **On Render:**
- All user data is stored in PostgreSQL
- All files are stored in Supabase Storage
- Data persists across restarts and redeployments
- You can scale/suspend/resume without data loss

❌ **Without PostgreSQL on Render:**
- App will show error: "Persistent database is not configured"
- App will not start

## Schema Migration

The PostgreSQL schema is automatically created on first run:

```bash
# Manual migration (if needed):
psql -h HOST -U postgres -d postgres < database/postgres_schema.sql
```

To enable Row Level Security (RLS) in Supabase after setup:

```bash
# In Supabase SQL Editor, run:
\i database/supabase_rls_template.sql
```

## Monitoring Data

### Check Database Size
```bash
# On Render PostgreSQL:
SELECT pg_size_pretty(pg_database_size('postgres'));
```

### Backup Data
1. Render: Use built-in backup feature in PostgreSQL settings
2. Supabase: Settings → Backups

## Environment Variables Explained

| Variable | Purpose | Example |
|----------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host:5432/db` |
| `SUPABASE_URL` | Supabase API endpoint | `https://project.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Server-side API key | (secret) |
| `SUPABASE_BUCKET` | Storage bucket name | `psb-hrdm-files` |
| `PUBLIC_URL` | App public URL | `https://app.onrender.com` |
| `APP_ENV` | Environment mode | `production` or `local` |

⚠️ **Never commit secrets to GitHub. Always use Render Environment Variables.**

## Troubleshooting

### "Persistent database is not configured"
- **Cause:** Running on Render without PostgreSQL
- **Fix:** Add `DATABASE_URL` environment variable to Render

### "Data disappeared after restart"
- **Cause:** Using SQLite on Render
- **Fix:** Switch to PostgreSQL via `DATABASE_URL`

### File uploads failing
- **Cause:** Supabase Storage not configured
- **Fix:** Set `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`

### Connection timeout
- **Cause:** PostgreSQL host/credentials wrong
- **Fix:** Check `DATABASE_URL` format and network access

## Support

For questions:
- Render docs: https://render.com/docs
- Supabase docs: https://supabase.com/docs
- PostgreSQL docs: https://www.postgresql.org/docs/
