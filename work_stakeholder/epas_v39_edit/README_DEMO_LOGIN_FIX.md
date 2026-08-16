# EPAS 4.1.1 Demo Login Fix

The public 8501 demo now supports **direct Streamlit launch** as well as the helper script.

## Recommended

```bash
./scripts/run_demo_8501.sh
```

## Direct launch

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

When no explicit `EPAS_RUNTIME_MODE` is set, the demo package reads `.env.demo` automatically. This is safe for the demo distribution because `strip_demo_for_production.py` removes `.env.demo` and all demo adapters when creating the production package.

Demo GM credentials:

- Email: `gm@classification.com`
- Password: `PSB-Demo-2026!`

All other published demo roles use the same password.

If `EPAS_RUNTIME_MODE=production` is explicitly set in the environment, production mode wins intentionally.
