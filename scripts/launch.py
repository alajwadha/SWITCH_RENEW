"""Launch detached services and open the browser; no terminal needed afterwards."""
from pathlib import Path
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
PORT = 8765

def health():
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/health", timeout=2) as r:
            return json.loads(r.read())
    except (OSError, ValueError):
        return None

def main():
    python = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.is_file() or not (ROOT / "out/index.html").is_file():
        raise SystemExit("Run python scripts/setup.py once before opening the workbench.")
    workspace = Path(os.environ.get("SWITCH_WORKSPACE", ROOT / "workspace")).resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    existing = health()
    if existing:
        if Path(existing["workspace"]).resolve() != workspace:
            raise SystemExit("A different workspace is running on port 8765. Stop it before opening this one.")
        if existing.get("worker_online"):
            webbrowser.open(f"http://127.0.0.1:{PORT}")
            return
    flags = {"creationflags": subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    processes = []
    with (workspace / "service.log").open("a") as log:
        if not existing:
            p = subprocess.Popen([str(python), "-m", "uvicorn", "backend.api:app", "--host", "127.0.0.1", "--port", str(PORT), "--no-proxy-headers"], cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log, stderr=log, **flags)
            processes.append(p)
        p = subprocess.Popen([str(python), "-u", "-m", "backend.worker"], cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log, stderr=log, **flags)
        processes.append(p)
    for _ in range(60):
        status = health()
        if status and status.get("worker_online"):
            webbrowser.open(f"http://127.0.0.1:{PORT}")
            print("Workbench is running. This window may be closed.")
            return
        if any(p.poll() is not None for p in processes):
            raise SystemExit(f"A service stopped while starting. See {workspace / 'service.log'}.")
        time.sleep(0.5)
    raise SystemExit(f"Startup took too long. See {workspace / 'service.log'}.")

if __name__ == "__main__":
    main()
