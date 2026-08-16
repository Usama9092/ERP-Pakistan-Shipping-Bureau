from pathlib import Path
import subprocess
import sys


def test_demo_production_switch_files_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / 'scripts' / 'run_demo_8501.sh').exists()
    assert (root / 'scripts' / 'run_production_8501.sh').exists()
    assert (root / 'scripts' / 'promote_to_production.sh').exists()
    assert (root / 'config' / 'demo_runtime.py').exists()
    assert (root / 'database' / 'demo_queries_v40.py').exists()


def test_production_promotion_removes_demo_runtime(tmp_path):
    root = Path(__file__).resolve().parents[1]
    out = tmp_path / 'production'
    subprocess.run([
        sys.executable,
        str(root / 'scripts' / 'strip_demo_for_production.py'),
        '--output', str(out),
    ], check=True)
    forbidden = [
        out / 'config' / 'demo_runtime.py',
        out / 'database' / 'demo_queries_v40.py',
        out / 'database' / 'seed_data.py',
        out / 'DEMO_CREDENTIALS.md',
        out / 'scripts' / 'run_demo_8501.sh',
        out / '.env.demo',
        out / '.devcontainer',
    ]
    assert all(not p.exists() for p in forbidden)
    assert 'Demo runtime' in (out / 'PRODUCTION_MODE.txt').read_text(encoding='utf-8')


def test_run_script_is_port_8501_aware():
    root = Path(__file__).resolve().parents[1]
    demo = (root / 'scripts' / 'run_demo_8501.sh').read_text(encoding='utf-8')
    prod = (root / 'scripts' / 'run_production_8501.sh').read_text(encoding='utf-8')
    assert '--server.port 8501' in demo
    assert '--server.port 8501' in prod
    assert 'EPAS_RUNTIME_MODE=demo' in demo
    assert 'EPAS_RUNTIME_MODE=production' in prod


def test_demo_env_file_auto_load_is_supported_for_direct_streamlit_launch():
    root = Path(__file__).resolve().parents[1]
    client = (root / 'config' / 'supabase_client.py').read_text(encoding='utf-8')
    assert '_load_demo_env_file' in client
    assert 'EPAS_RUNTIME_MODE' in client
    assert '.env.demo' in client
    assert 'production promotion script removes `.env.demo`' in client
