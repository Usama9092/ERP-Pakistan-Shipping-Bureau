# Demo → Professional Production Switch

## Demo on port 8501

Use GitHub Codespaces (GitHub itself does not run Streamlit apps on port 8501):

```bash
./scripts/run_demo_8501.sh
```

This sets `EPAS_RUNTIME_MODE=demo` and uses the bundled sample data + demo credentials.

## Professional production

Create a clean production copy that removes demo-only files:

```bash
./scripts/promote_to_production.sh ../epas-production
```

Then configure only Supabase credentials:

```bash
export EPAS_RUNTIME_MODE=production
export SUPABASE_URL=https://YOUR_PROJECT.supabase.co
export SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
```

Start:

```bash
cd ../epas-production
./scripts/run_production_8501.sh
```

Production uses **Supabase Auth + Supabase database/RLS/Storage only**. Demo authentication and seed data are removed from the promoted copy.
