from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import uuid
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator
from starlette.middleware.trustedhost import TrustedHostMiddleware
from backend.core import *
from backend.backup import create_backup

class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    demand_multiplier: float = Field(default=1, ge=0.05, le=5)
    fuel_multiplier: float = Field(default=1, ge=0, le=10)
    capital_multiplier: float = Field(default=1, ge=0.05, le=10)
    time_limit: int = Field(default=120, ge=5, le=86400)
    mip_gap: float = Field(default=0.001, ge=0, le=0.2)
    risk_weight: float = Field(default=0, ge=0, le=1)
    cvar_alpha: float = Field(default=0.95, ge=0.5, le=0.99)

class Edit(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    file: str
    column: str
    row: int = Field(ge=0)
    value: float

class RevisionBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    revision: int = Field(ge=1)

class ScenarioBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    model: str
    config: Settings = Field(default_factory=Settings)
    edits: list[Edit] = Field(default_factory=list, max_length=2000)
    revision: int | None = None

    @field_validator("name")
    @classmethod
    def nonempty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("model")
    @classmethod
    def supported(cls, v):
        if v not in MODELS:
            raise ValueError("Unsupported model")
        return v

@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app = FastAPI(title="SWITCH Workbench", version="0.1.0", lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "[::1]", "testserver"])

@app.middleware("http")
async def same_origin(request: Request, call_next):
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        origin = request.headers.get("origin")
        if origin and urlparse(origin).netloc != request.headers.get("host"):
            return JSONResponse({"detail": "Cross-origin write rejected"}, status_code=403)
        if request.headers.get("sec-fetch-site") == "cross-site":
            return JSONResponse({"detail": "Cross-site write rejected"}, status_code=403)
    return await call_next(request)

@app.exception_handler(KeyError)
async def missing(_, exc):
    return JSONResponse({"detail": str(exc)}, status_code=404)

@app.exception_handler(ValueError)
async def invalid(_, exc):
    return JSONResponse({"detail": str(exc)}, status_code=400)

@app.get("/api/health")
def health():
    with connect() as db:
        heartbeat = db.execute("SELECT value FROM metadata WHERE key='worker_heartbeat'").fetchone()
    healthy = heartbeat is not None and (datetime.now(timezone.utc) - datetime.fromisoformat(heartbeat[0])).total_seconds() < 10
    return {"status": "ok", "worker_online": healthy, "version": "0.1.0", "workspace": str(workspace()), "active_runs": sum(r["status"] in ACTIVE for r in list_runs())}

@app.get("/api/models")
def models():
    return catalog()

@app.get("/api/scenarios")
def scenarios():
    return list_scenarios()

def body_data(body):
    return {"name": body.name, "model": body.model, "config": body.config.model_dump(), "edits": [e.model_dump() for e in body.edits]}

def check_edits(data):
    if data["model"] == "stochastic" and data["edits"]:
        raise ValueError("The teaching model does not use SWITCH CSV inputs")
    seen = set()
    for edit in data["edits"]:
        key = (edit["file"], edit["row"], edit["column"])
        if key in seen:
            raise ValueError("Duplicate edit for the same cell")
        seen.add(key)
        if edit["file"] not in EDITABLE:
            raise ValueError("Unknown editable table")
        prepared_table(data, edit["file"])

@app.post("/api/scenarios", status_code=201)
def create_scenario(body: ScenarioBody):
    data = body_data(body)
    check_edits(data)
    sid, stamp = str(uuid.uuid4()), now()
    with connect() as db:
        db.execute("INSERT INTO scenarios VALUES (?,?,?,?,?,?,?,?)", (sid, body.name, body.model, json.dumps(data["config"]), json.dumps(data["edits"]), 1, stamp, stamp))
    return get_scenario(sid)

@app.put("/api/scenarios/{sid}")
def update_scenario(sid: str, body: ScenarioBody):
    existing = get_scenario(sid)
    if body.model != existing["model"]:
        raise ValueError("Duplicate into a new scenario to change the model")
    data = body_data(body)
    check_edits(data)
    with connect() as db:
        changed = db.execute("UPDATE scenarios SET name=?,config=?,edits=?,revision=revision+1,updated_at=? WHERE id=? AND revision=?", (body.name, json.dumps(data["config"]), json.dumps(data["edits"]), now(), sid, body.revision)).rowcount
    if not changed:
        raise HTTPException(409, "Scenario changed in another window. Reload before saving.")
    return get_scenario(sid)

@app.get("/api/scenarios/{sid}/tables")
def tables(sid: str):
    scenario = get_scenario(sid)
    if scenario["model"] == "stochastic":
        return []
    return [{"name": f, "columns": cols} for f, cols in EDITABLE.items() if (baseline(scenario["model"]) / f).exists()]

@app.get("/api/scenarios/{sid}/tables/{filename}")
def table(sid: str, filename: str, offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
    scenario = get_scenario(sid)
    if scenario["model"] == "stochastic":
        raise ValueError("No input CSV tables for this model")
    fields, rows = prepared_table(scenario, filename)
    _, original = read_csv(baseline(scenario["model"]) / filename)
    return {"columns": fields, "rows": rows[offset:offset + limit], "baseline_rows": original[offset:offset + limit], "offset": offset, "total": len(rows), "editable": EDITABLE[filename], "revision": scenario["revision"]}

def selected_revision(sid: str, body: RevisionBody):
    scenario = get_scenario(sid)
    if scenario["revision"] != body.revision:
        raise HTTPException(409, "The saved scenario changed in another window. Review the latest revision before validating or running.")
    return scenario

@app.post("/api/scenarios/{sid}/validate")
def validation(sid: str, body: RevisionBody):
    scenario = selected_revision(sid, body)
    return {**validate(scenario), "revision": scenario["revision"]}

@app.post("/api/scenarios/{sid}/run", status_code=202)
def run_scenario(sid: str, body: RevisionBody):
    return queue_run(selected_revision(sid, body))

@app.get("/api/runs")
def runs():
    return list_runs()

@app.get("/api/runs/{rid}")
def run_detail(rid: str):
    return {**get_run(rid), "manifest": json.loads((run_dir(rid) / "manifest.json").read_text())}

@app.post("/api/runs/{rid}/cancel")
def cancel(rid: str):
    get_run(rid)
    with connect() as db:
        db.execute("UPDATE runs SET status=CASE WHEN status='queued' THEN 'cancelled' ELSE 'cancelling' END,finished_at=CASE WHEN status='queued' THEN ? ELSE finished_at END WHERE id=? AND status IN ('queued','running')", (now(), rid))
    return get_run(rid)

@app.get("/api/runs/{rid}/log")
def log(rid: str):
    get_run(rid)
    path = run_dir(rid) / "solver.log"
    if not path.exists():
        return {"text": "Waiting for the local worker…"}
    with path.open("rb") as f:
        f.seek(max(0, path.stat().st_size - 100000))
        return {"text": f.read().decode("utf-8", errors="replace")}

@app.get("/api/runs/{rid}/files")
def run_files(rid: str):
    get_run(rid)
    return [{"path": str(p.relative_to(run_dir(rid))), "bytes": p.stat().st_size} for p in sorted(run_dir(rid).rglob("*")) if p.is_file() and not p.name.endswith(".tmp")]

@app.get("/api/runs/{rid}/download/{filename:path}")
def download(rid: str, filename: str):
    get_run(rid)
    root = run_dir(rid).resolve()
    path = (root / filename).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise HTTPException(404, "Artifact not found")
    return FileResponse(path, filename=path.name)

@app.post("/api/backup")
def backup():
    path = create_backup()
    return {"filename": path.name, "url": f"/api/backups/{path.name}"}

@app.get("/api/backups/{name}")
def backup_download(name: str):
    if not name.startswith("switch-workspace-") or Path(name).name != name:
        raise HTTPException(404)
    p = ROOT / "backups" / name
    if not p.is_file():
        raise HTTPException(404)
    return FileResponse(p, filename=name)

if (ROOT / "out").exists():
    app.mount("/", StaticFiles(directory=ROOT / "out", html=True), name="frontend")
