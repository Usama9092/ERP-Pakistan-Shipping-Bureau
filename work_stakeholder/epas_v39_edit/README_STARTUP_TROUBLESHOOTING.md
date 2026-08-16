# EPAS startup troubleshooting

## GitHub Codespaces / port 8501

The app is now bootstrapped so the local `config` package is found even when Streamlit is launched from the parent workspace directory.

Preferred:

```bash
./scripts/run_demo_8501.sh
```

Direct launch is also supported:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

The runtime will load `.env.demo` automatically when no explicit `EPAS_RUNTIME_MODE` is set.

If you see `ModuleNotFoundError: No module named 'config'`, make sure you are launching the `app.py` located in the extracted EPAS project directory, or use the included launcher above. The application itself also inserts its project root into `sys.path` before importing `config`.
