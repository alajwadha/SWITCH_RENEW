"""One-time, cross-platform setup. Run with Python 3.12 (or 3.11/3.13)."""
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[1]
def call(args, **kwargs):
    print("Running:", " ".join(map(str, args)), flush=True)
    subprocess.run([str(v) for v in args], cwd=ROOT, check=True, **kwargs)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-kenya", action="store_true", help="Install the small teaching/tutorial configurations first")
    args = parser.parse_args()
    if not (3, 11) <= sys.version_info[:2] < (3, 14):
        raise SystemExit("Use Python 3.11, 3.12, or 3.13; Python 3.12 is recommended.")
    for command in ("git", "node", "npm"):
        if not shutil.which(command):
            raise SystemExit(f"Install {command} first, then run setup again. See README.md.")
    if int(subprocess.check_output(["node", "--version"], text=True).lstrip("v").split(".")[0]) < 22:
        raise SystemExit("Node.js 22 or later is required by this project's tested setup.")
    environment = ROOT / ".venv"
    if not environment.exists():
        venv.EnvBuilder(with_pip=True).create(environment)
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    sources = json.loads((ROOT / "sources.lock.json").read_text())
    (ROOT / ".sources").mkdir(exist_ok=True)
    for name, meta in sources.items():
        if name == "kenya" and args.skip_kenya:
            continue
        path = ROOT / ".sources" / name
        if not path.exists():
            call(["git", "clone", "--filter=blob:none", "--no-checkout", meta["url"], path])
            call(["git", "-C", path, "checkout", "--detach", meta["commit"]])
        else:
            actual = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
            if actual != meta["commit"]:
                raise SystemExit(f"{name} checkout differs from the lockfile. Setup will not overwrite it.")
    call([python, "-m", "pip", "install", "-r", "requirements.lock.txt"])
    call([python, "-m", "pip", "install", "--no-deps", "-e", ".sources/switch"])
    npm = shutil.which("npm")
    # Use an explicit .cmd shell on Windows only for the trusted fixed npm command.
    if os.name == "nt":
        call(["cmd", "/c", "npm", "ci", "--no-audit", "--no-fund"])
        call(["cmd", "/c", "npm", "run", "build"])
    else:
        call([npm, "ci", "--no-audit", "--no-fund"])
        call([npm, "run", "build"])
    print("Setup complete. Double-click Start_Workbench.command (macOS), Start_Workbench.bat (Windows), or run python scripts/launch.py.")

if __name__ == "__main__":
    main()
