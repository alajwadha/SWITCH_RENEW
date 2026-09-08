"""Local persistence, model registry, and immutable input preparation."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import sqlite3
import subprocess
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = ("queued", "running", "cancelling")
SOURCE_LOCK = json.loads((ROOT / "sources.lock.json").read_text())
MODELS = {
    "tiny": {"id": "tiny", "name": "Three-zone tutorial", "kind": "switch", "source": "tutorial", "folder": "3_zone_tiny/inputs", "country": None, "description": "The official SWITCH tutorial: three abstract zones, two investment periods, seven sampled timepoints.", "geography": "Abstract network", "license": "Upstream tutorial license"},
    "kenya": {"id": "kenya", "name": "Kenya · base model", "kind": "switch", "source": "kenya", "folder": "inputs", "country": "KEN", "description": "Xi Xi’s public base configuration, 2027–2050. Custom build limits, storage and planning reserves.", "geography": "47 county zones", "license": "CC BY-NC 4.0 · academic/noncommercial"},
    "stochastic": {"id": "stochastic", "name": "Two-stage learning lab", "kind": "teaching", "source": None, "country": None, "description": "A separate, illustrative Pyomo capacity-planning model. Shared investment and uncertain demand with operating recourse. Not the Kenya formulation.", "geography": "Single illustrative zone", "license": "Original teaching implementation"},
}

EDITABLE = {
    "loads.csv": {"zone_demand_mw": (0, None, "MW", "Demand at the zone and sampled timepoint")},
    "fuel_cost.csv": {"fuel_cost": (0, None, "model currency/MMBtu", "Fuel input price")},
    "gen_build_costs.csv": {"gen_overnight_cost": (0, None, "model currency/MW", "Overnight capital cost"), "gen_fixed_om": (0, None, "model currency/MW-year", "Annual fixed operating cost")},
    "variable_capacity_factors.csv": {"gen_max_capacity_factor": (0, 1, "fraction", "Available variable output divided by installed capacity")},
    "financials.csv": {"discount_rate": (0, 1, "fraction/year", "Present-value discount rate"), "interest_rate": (0, 1, "fraction/year", "Financing interest rate")},
    "gen_info.csv": {"gen_capacity_limit_mw": (0, None, "MW", "Maximum project capacity"), "gen_variable_om": (0, None, "model currency/MWh", "Variable operating cost")},
}

def now():
    return datetime.now(timezone.utc).isoformat()

def workspace() -> Path:
    return Path(os.environ.get("SWITCH_WORKSPACE", ROOT / "workspace")).resolve()

def atomic_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, allow_nan=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)

class ClosingConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()

def connect():
    w = workspace()
    w.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(w / "workbench.sqlite", timeout=30, factory=ClosingConnection)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=30000")
    return db

def init_db():
    with connect() as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.executescript("""
        CREATE TABLE IF NOT EXISTS scenarios (
          id TEXT PRIMARY KEY, name TEXT NOT NULL, model TEXT NOT NULL,
          config TEXT NOT NULL, edits TEXT NOT NULL DEFAULT '[]', revision INTEGER NOT NULL,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS runs (
          id TEXT PRIMARY KEY, scenario_id TEXT NOT NULL, scenario_name TEXT NOT NULL,
          model TEXT NOT NULL, revision INTEGER NOT NULL, status TEXT NOT NULL,
          created_at TEXT NOT NULL, started_at TEXT, finished_at TEXT,
          heartbeat TEXT, worker_id TEXT, error TEXT, summary TEXT,
          FOREIGN KEY(scenario_id) REFERENCES scenarios(id)
        );
        CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_runs_status_created ON runs(status,created_at);
        PRAGMA user_version=1;
        """)

def unpack(row):
    if row is None:
        return None
    d = dict(row)
    for k in ("config", "edits", "summary"):
        if k in d and d[k] is not None:
            d[k] = json.loads(d[k])
    return d

def list_scenarios():
    with connect() as db:
        return [unpack(r) for r in db.execute("SELECT * FROM scenarios ORDER BY updated_at DESC")]

def get_scenario(sid):
    with connect() as db:
        r = unpack(db.execute("SELECT * FROM scenarios WHERE id=?", (sid,)).fetchone())
    if r is None:
        raise KeyError("Scenario not found")
    return r

def list_runs():
    with connect() as db:
        return [unpack(r) for r in db.execute("SELECT * FROM runs ORDER BY created_at DESC")]

def get_run(rid):
    with connect() as db:
        r = unpack(db.execute("SELECT * FROM runs WHERE id=?", (rid,)).fetchone())
    if r is None:
        raise KeyError("Run not found")
    return r

def run_dir(rid):
    # UUIDs only, independent of HTTP routing or user-supplied filenames.
    uuid.UUID(rid)
    return workspace() / "runs" / rid

def source_dir(model):
    meta = MODELS[model]
    return ROOT / ".sources" / meta["source"]

def baseline(model):
    return source_dir(model) / MODELS[model]["folder"]

def source_versions(model):
    keys = ["switch", MODELS[model]["source"]] if model != "stochastic" else []
    out = {}
    for key in keys:
        folder = ROOT / ".sources" / key
        expected = SOURCE_LOCK[key]
        head = subprocess.run(["git", "-C", str(folder), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        if head.returncode or head.stdout.strip() != expected["commit"]:
            raise ValueError(f"{key} source is missing or is not at its pinned revision. Run setup.")
        scope = {"switch": ["switch_model"], "tutorial": ["3_zone_tiny/inputs"], "kenya": ["inputs", "gen_build_limits.py"]}[key]
        dirty = subprocess.run(["git", "-C", str(folder), "status", "--porcelain", "--untracked-files=no", "--", *scope], capture_output=True, text=True, timeout=30)
        if dirty.stdout.strip():
            raise ValueError(f"{key} pinned source has tracked modifications. Use a clean checkout.")
        out[key] = {**expected, "verified_paths": scope}
    return out

def catalog():
    items = []
    for key, meta in MODELS.items():
        d = dict(meta)
        d["available"] = key == "stochastic" or baseline(key).is_dir()
        if key != "stochastic" and d["available"]:
            d["modules"] = [line.strip() for line in (baseline(key) / "modules.txt").read_text().splitlines() if line.strip() and not line.startswith("#")]
            for f, field in [("load_zones.csv", "zones"), ("timepoints.csv", "timepoints"), ("periods.csv", "periods"), ("gen_info.csv", "projects")]:
                d[field] = len(read_csv(baseline(key) / f)[1])
        else:
            d.update(modules=[], zones=1, timepoints=3, periods=1, projects=2)
        items.append(d)
    return items

def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)

def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def prepared_table(scenario, filename):
    if filename not in EDITABLE:
        raise ValueError("This table is not editable in this milestone")
    path = baseline(scenario["model"]) / filename
    if not path.is_file():
        raise ValueError("Table not present in this model")
    fields, rows = read_csv(path)
    cfg = scenario["config"]
    scales = {"loads.csv": ("zone_demand_mw", cfg["demand_multiplier"]), "fuel_cost.csv": ("fuel_cost", cfg["fuel_multiplier"]), "gen_build_costs.csv": ("gen_overnight_cost", cfg["capital_multiplier"])}
    if filename in scales:
        col, multiplier = scales[filename]
        for r in rows:
            if col in r and r[col] not in (None, "", "."):
                r[col] = str(float(r[col]) * multiplier)
    for e in scenario["edits"]:
        if e["file"] == filename:
            col, idx, val = e["column"], e["row"], e["value"]
            if col not in EDITABLE[filename] or col not in fields or idx < 0 or idx >= len(rows):
                raise ValueError("Invalid input edit")
            low, high, *_ = EDITABLE[filename][col]
            if not math.isfinite(val) or val < low or (high is not None and val > high):
                raise ValueError(f"Invalid value for {col}")
            rows[idx][col] = str(val)
    return fields, rows

def prepare_inputs(scenario, target):
    shutil.copytree(baseline(scenario["model"]), target)
    for name in EDITABLE:
        if (target / name).is_file():
            fields, rows = prepared_table(scenario, name)
            write_csv(target / name, fields, rows)

def hashes(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.rglob("*")) if p.is_file()}

def validate(scenario):
    errors, warnings = [], []
    if scenario["model"] == "stochastic":
        return {"valid": True, "errors": [], "warnings": ["Illustrative assumptions; this is a teaching model, not a national forecast."]}
    try:
        source_versions(scenario["model"])
        _, loads = prepared_table(scenario, "loads.csv")
        zones = {r["LOAD_ZONE"] for r in read_csv(baseline(scenario["model"]) / "load_zones.csv")[1]}
        time_rows = read_csv(baseline(scenario["model"]) / "timepoints.csv")[1]
        tps = {r[next(iter(r))] for r in time_rows}
        keys = set()
        for r in loads:
            key = (r["LOAD_ZONE"], r["TIMEPOINT"])
            if key in keys:
                errors.append(f"Duplicate load key: {key}")
            keys.add(key)
            if key[0] not in zones or key[1] not in tps:
                errors.append(f"Unknown load index: {key}")
            if not math.isfinite(float(r["zone_demand_mw"])) or float(r["zone_demand_mw"]) < 0:
                errors.append(f"Invalid demand at {key}")
        if keys != {(z, t) for z in zones for t in tps}:
            errors.append("Load table must cover every zone/timepoint pair")
        for name in EDITABLE:
            if (baseline(scenario["model"]) / name).exists():
                prepared_table(scenario, name)
        warnings.append("Preflight checks cover input ranges and load coverage. Full module/domain checks occur when SWITCH constructs the model.")
        if scenario["model"] == "kenya":
            warnings.append("Kenya can need substantially more RAM and solve time than the tutorial. Time-limited feasible solutions are labelled explicitly.")
    except (ValueError, OSError, KeyError) as exc:
        errors.append(str(exc))
    return {"valid": not errors, "errors": errors[:50], "warnings": warnings}

def queue_run(scenario):
    report = validate(scenario)
    if not report["valid"]:
        raise ValueError("; ".join(report["errors"]))
    rid = str(uuid.uuid4())
    folder = run_dir(rid)
    folder.mkdir(parents=True)
    try:
        versions = source_versions(scenario["model"])
        if scenario["model"] != "stochastic":
            prepare_inputs(scenario, folder / "inputs")
            if scenario["model"] == "kenya":
                # Snapshot trusted custom implementation as well as its data.
                (folder / "custom").mkdir()
                shutil.copy2(source_dir("kenya") / "gen_build_limits.py", folder / "custom" / "gen_build_limits.py")
        stamp = now()
        atomic_json(folder / "manifest.json", {"schema_version": 1, "id": rid, "created_at": stamp, "scenario": scenario, "source_versions": versions, "input_hashes": hashes(folder / "inputs") if (folder / "inputs").exists() else {}, "custom_hashes": hashes(folder / "custom") if (folder / "custom").exists() else {}, "solver": {"name": "HiGHS", "interface": "appsi_highs", "time_limit_seconds": scenario["config"]["time_limit"], "mip_gap": scenario["config"]["mip_gap"]}, "validation": report})
        with connect() as db:
            # Reject a stale browser update before inserting the run snapshot.
            db.execute("BEGIN IMMEDIATE")
            current = db.execute("SELECT revision FROM scenarios WHERE id=?", (scenario["id"],)).fetchone()
            if current is None or current[0] != scenario["revision"]:
                raise ValueError("Scenario changed while preparing the run. Refresh and retry.")
            db.execute("INSERT INTO runs (id,scenario_id,scenario_name,model,revision,status,created_at) VALUES (?,?,?,?,?,'queued',?)", (rid, scenario["id"], scenario["name"], scenario["model"], scenario["revision"], stamp))
        return get_run(rid)
    except Exception:
        shutil.rmtree(folder)
        raise
