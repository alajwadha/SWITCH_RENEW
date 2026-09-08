import json
import sqlite3
import subprocess
import threading
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from backend.api import app
from backend.backup import create_backup, restore_backup
from backend.core import ROOT, baseline, connect, get_run, get_scenario, hashes, init_db, list_runs, run_dir, workspace
from backend.worker import claim, execute, recover

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SWITCH_WORKSPACE", str(tmp_path / "workspace"))
    with TestClient(app) as c:
        yield c

def scenario(client, **kw):
    response = client.post("/api/scenarios", json={"name": "Test scenario", "model": "tiny", **kw})
    assert response.status_code == 201, response.text
    return response.json()

def run_and_wait(client, s):
    response = client.post(f"/api/scenarios/{s['id']}/run", json={"revision": s["revision"]})
    assert response.status_code == 202, response.text
    run = response.json()
    assert claim("test-worker") == run["id"]
    execute(run["id"], threading.Event())
    return get_run(run["id"])

def test_real_switch_matches_published_reference_and_preserves_inputs(client):
    original = hashes(baseline("tiny"))
    s = scenario(client)
    r = run_and_wait(client, s)
    assert r["status"] == "succeeded", r["error"]
    assert r["summary"]["termination"] == "optimal"
    reference = float((ROOT / ".sources/tutorial/3_zone_tiny/outputs/total_cost.txt").read_text())
    assert r["summary"]["objective"] == pytest.approx(reference, rel=1e-7)
    assert r["summary"]["max_constraint_violation"] < 1e-5
    assert hashes(baseline("tiny")) == original
    manifest = client.get(f"/api/runs/{r['id']}").json()["manifest"]
    assert manifest["input_upgrade_applied"]
    assert manifest["input_hashes"] == hashes(run_dir(r["id"]) / "inputs")
    assert manifest["effective_input_hashes"] == hashes(run_dir(r["id"]) / "effective_inputs")
    assert (run_dir(r["id"]) / "processed/dispatch.parquet").exists()
    assert client.get(f"/api/runs/{r['id']}/download/outputs/total_cost.txt").status_code == 200
    # New API lifespan must see the completed run in SQLite, without browser state.
    with TestClient(app) as restarted:
        assert restarted.get(f"/api/runs/{r['id']}").json()["summary"]["objective"] == r["summary"]["objective"]

def test_revisions_conflicts_and_queued_snapshot(client):
    s = scenario(client)
    before = client.post(f"/api/scenarios/{s['id']}/run", json={"revision": s["revision"]}).json()
    snapshot = hashes(run_dir(before["id"]) / "inputs")
    # Exercise the same serializer as the actual React Save revision handler.
    serialized = subprocess.run(["node", "--experimental-strip-types", "--input-type=module", "-e", "import {scenarioBody} from './components/scenario-state.ts'; import fs from 'node:fs'; console.log(JSON.stringify(scenarioBody(JSON.parse(fs.readFileSync(0, 'utf8')))));"], input=json.dumps(s), text=True, capture_output=True, check=True, cwd=ROOT)
    body = json.loads(serialized.stdout)
    body["config"]["demand_multiplier"] = 1.2
    body["edits"] = [{"file": "loads.csv", "row": 0, "column": "zone_demand_mw", "value": 9}]
    updated = client.put(f"/api/scenarios/{s['id']}", json=body)
    assert updated.status_code == 200
    assert updated.json()["revision"] == 2
    assert client.put(f"/api/scenarios/{s['id']}", json=body).status_code == 409
    table = client.get(f"/api/scenarios/{s['id']}/tables/loads.csv").json()
    assert float(table["rows"][0]["zone_demand_mw"]) == 9
    assert float(table["rows"][1]["zone_demand_mw"]) == pytest.approx(4 * 1.2)
    assert hashes(run_dir(before["id"]) / "inputs") == snapshot
    assert client.post(f"/api/runs/{before['id']}/cancel").json()["status"] == "cancelled"
    assert claim("test-worker") is None

def test_rejects_invalid_inputs_and_cross_origin_writes(client):
    assert client.post("/api/scenarios", json={"name": "Bad", "model": "tiny", "config": {"demand_multiplier": -1}}).status_code == 422
    assert client.post("/api/scenarios", json={"name": "Bad", "model": "tiny", "edits": [{"file": "../x", "row": 0, "column": "x", "value": 1}]}).status_code == 400
    assert client.post("/api/scenarios", headers={"Origin": "https://other.example"}, json={"name": "Bad", "model": "tiny"}).status_code == 403
    assert client.get("/api/health", headers={"Host": "other.example"}).status_code == 400

def test_backup_restore_and_tamper_detection(client, tmp_path):
    s = scenario(client)
    queued = client.post(f"/api/scenarios/{s['id']}/run", json={"revision": s["revision"]}).json()
    assert client.post("/api/backup").status_code == 400
    client.post(f"/api/runs/{queued['id']}/cancel")
    path = create_backup()
    try:
        restored = restore_backup(path, tmp_path / "restored")
        db = sqlite3.connect(restored / "workbench.sqlite")
        assert db.execute("SELECT name FROM scenarios").fetchone()[0] == s["name"]
        assert db.execute("SELECT status FROM runs").fetchone()[0] == "cancelled"
        db.close()
        assert hashes(restored / "runs") == hashes(workspace() / "runs")
        with pytest.raises(ValueError, match="new destination"):
            restore_backup(path, restored)
        malicious = tmp_path / "tampered.zip"
        with zipfile.ZipFile(path) as original, zipfile.ZipFile(malicious, "w") as output:
            for name in original.namelist():
                data = original.read(name)
                output.writestr(name, b"bad-data" if name.endswith("manifest.json") and name != "backup_manifest.json" else data)
        with pytest.raises(ValueError, match="checksum"):
            restore_backup(malicious, tmp_path / "must-not-exist")
        assert not (tmp_path / "must-not-exist").exists()
    finally:
        path.unlink(missing_ok=True)

def test_archive_traversal_is_rejected(tmp_path):
    path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("../escape.txt", "bad")
    with pytest.raises(ValueError, match="Unsafe"):
        restore_backup(path, tmp_path / "target")
    assert not (tmp_path / "escape.txt").exists()

def test_claim_once_cancel_running_and_recover(client):
    s = scenario(client)
    r = client.post(f"/api/scenarios/{s['id']}/run", json={"revision": s["revision"]}).json()
    assert claim("one") == r["id"]
    assert claim("two") is None
    assert client.post(f"/api/runs/{r['id']}/cancel").json()["status"] == "cancelling"
    execute(r["id"], threading.Event())
    assert get_run(r["id"])["status"] == "cancelled"
    r2 = client.post(f"/api/scenarios/{s['id']}/run", json={"revision": s["revision"]}).json()
    claim("crashed-worker")
    recover()
    assert get_run(r2["id"])["status"] == "interrupted"
    assert (run_dir(r2["id"]) / "manifest.json").exists()

@pytest.mark.parametrize("risk", [0, 0.5])
def test_true_two_stage_benchmarks(client, risk):
    s = scenario(client, model="stochastic", config={"risk_weight": risk})
    r = run_and_wait(client, s)
    assert r["status"] == "succeeded", r["error"]
    out = r["summary"]
    assert out["ws"] <= out["rp"] + 1e-5 <= out["eev"] + 1e-5
    assert out["vss"] == pytest.approx(out["eev"] - out["rp"])
    assert out["evpi"] == pytest.approx(out["rp"] - out["ws"])
    assert out["vss"] > 0
    assert sum(s["probability"] for s in out["scenarios"]) == 1
    for outcome in out["scenarios"]:
        assert outcome["firm_mw"] + outcome["solar_mw"] + outcome["unserved_mw"] == pytest.approx(outcome["demand_mw"])
        assert outcome["firm_mw"] <= 40 + out["firm_build_mw"] + 1e-6
        assert outcome["solar_mw"] <= 0.3 * out["solar_build_mw"] + 1e-6
    assert out["cvar"] >= out["expected_cost"] - 1e-5

def test_country_snapshot_is_source_dated_and_no_fake_2026(client):
    atlas = json.loads((ROOT / "public/atlas.json").read_text())
    if atlas.get("index_file"):
        import gzip
        atlas = json.loads(gzip.decompress((ROOT / "public" / atlas["index_file"].lstrip("/")).read_bytes()))
    assert len(atlas["countries"]) >= 249
    for country in atlas["countries"]:
        assert set(country["indicators"]) == set(atlas["metadata"])
        for k, obs in country["indicators"].items():
            if obs["value"] is not None:
                if atlas["metadata"][k]["frequency"] == "annual":
                    assert 2010 <= obs["year"] <= atlas["latest_completed_year"]
                assert atlas["metadata"][k]["source_url"].startswith("https://")
                assert obs["year"] == max(h["year"] for h in obs["history"])
            else:
                assert obs["year"] is None

def test_production_page_and_real_api_available(client):
    page = client.get("/")
    assert page.status_code == 200
    assert "SWITCH Workbench" in page.text
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/world.geojson").status_code == 200


def test_selected_revision_required_and_stale_actions_create_no_run(client):
    s = scenario(client, model="stochastic")
    path = f"/api/scenarios/{s['id']}"
    body = {k: s[k] for k in ("name", "model", "config", "edits", "revision")}
    body["name"] = "Updated in another window"
    assert client.put(path, json=body).json()["revision"] == 2
    for action in ("validate", "run"):
        assert client.post(path + "/" + action).status_code == 422
        assert client.post(path + "/" + action, json={"revision": 1}).status_code == 409
    assert list_runs() == []
    report = client.post(path + "/validate", json={"revision": 2}).json()
    assert report["valid"] and report["revision"] == 2
    run = client.post(path + "/run", json={"revision": 2}).json()
    assert run["revision"] == 2
    manifest = client.get(f"/api/runs/{run['id']}").json()["manifest"]
    assert manifest["scenario"]["name"] == body["name"]


def test_table_exposes_unmodified_baseline_for_draft_preview(client):
    s = scenario(client, config={"demand_multiplier": 1.2}, edits=[{"file": "loads.csv", "row": 0, "column": "zone_demand_mw", "value": 9}])
    table = client.get(f"/api/scenarios/{s['id']}/tables/loads.csv?offset=0&limit=2").json()
    assert len(table["baseline_rows"]) == 2
    assert float(table["rows"][0]["zone_demand_mw"]) == 9
    assert float(table["baseline_rows"][1]["zone_demand_mw"]) == 4
    assert float(table["rows"][1]["zone_demand_mw"]) == pytest.approx(4.8)

def test_compressed_country_index_and_history_are_served(client):
    import gzip
    manifest = client.get('/atlas.json').json()
    index_response = client.get(manifest['index_file'])
    assert index_response.status_code == 200
    raw = index_response.content
    atlas = json.loads(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw)
    assert len(atlas['countries']) == 251
    history = client.get(atlas['history_files']['K'])
    assert history.status_code == 200
    raw = history.content
    data = json.loads(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw)
    assert len(data['KEN']['generation_total']) >= 10
