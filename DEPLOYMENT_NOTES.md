# Deployment Notes

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Production deployment
- Set DATABASE_URL to a persistent PostgreSQL/Supabase connection.
- Ensure the app runs behind HTTPS.
- Configure secrets for any future email/SMS/WhatsApp integrations.
- Keep the database backed up regularly.
