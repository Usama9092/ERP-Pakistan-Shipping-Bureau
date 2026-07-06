# Deploy PSB HRDM on Render with Supabase

## 1. Create Supabase project
Create a free Supabase project.

## 2. Get PostgreSQL DATABASE_URL
Supabase Dashboard → Project Settings → Database → Connection string.

Use this form in Render:

```text
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:5432/postgres
```

## 3. Get Supabase Storage keys
Supabase Dashboard → Project Settings → API:

```text
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
```

The app will create/use bucket:

```text
psb-hrdm-files
```

## 4. Push this package to GitHub
Upload all files.

## 5. Deploy on Render
New Web Service → GitHub repo.

Build:

```bash
pip install -r requirements.txt
```

Start:

```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

## 6. Add environment variables in Render
Add:

```text
DATABASE_URL
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
SUPABASE_BUCKET
PUBLIC_URL
```

## 7. Open app
The app creates database tables automatically on first run.
