"""Durable single-machine queue with independent per-job child processes."""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import threading
import time
import uuid
from backend.core import ROOT, atomic_json, connect, init_db, now, run_dir, workspace

def claim(worker_id):
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT id FROM runs WHERE status='queued' ORDER BY created_at LIMIT 1").fetchone()
        if row is None:
            return None
        db.execute("UPDATE runs SET status='running',started_at=?,heartbeat=?,worker_id=? WHERE id=? AND status='queued'", (now(), now(), worker_id, row[0]))
        return row[0]

def finish(rid, status, summary=None, error=None):
    with connect() as db:
        # Cancellation wins a concurrent completion race.
        current = db.execute("SELECT status FROM runs WHERE id=?", (rid,)).fetchone()[0]
        if current == "cancelling":
            status, summary = "cancelled", None
        db.execute("UPDATE runs SET status=?,finished_at=?,heartbeat=?,summary=?,error=? WHERE id=?", (status, now(), now(), json.dumps(summary) if summary else None, error, rid))
    atomic_json(run_dir(rid) / "status.json", {"status": status, "finished_at": now(), "error": error})

def lock_worker():
    handle = (workspace() / "worker.lock").open("a+")
    try:
        if os.name == "nt":
            import msvcrt
            handle.seek(0)
            handle.write("0")
            handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        raise RuntimeError("A worker is already running for this workspace")
    return handle

def prevent_sleep():
    """Best effort, release when the solve finishes. Does not prevent shutdown."""
    if sys.platform == "darwin":
        return subprocess.Popen(["caffeinate", "-i", "-w", str(os.getpid())])
    if os.name == "nt":
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    return None

def execute(rid, stop):
    folder = run_dir(rid)
    with (folder / "solver.log").open("a", buffering=1) as log:
        # Run outside the browser/API process; record its PID for conservative recovery.
        child = subprocess.Popen([sys.executable, "-u", "-m", "backend.solve_job", rid], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, env={**os.environ, "PYTHONUNBUFFERED": "1"})
        sleep_guard = prevent_sleep()
        with connect() as db:
            db.execute("INSERT OR REPLACE INTO metadata VALUES ('active_child',?)", (json.dumps({"pid": child.pid, "run_id": rid}),))
        try:
            while child.poll() is None:
                with connect() as db:
                    db.execute("UPDATE runs SET heartbeat=? WHERE id=?", (now(), rid))
                    db.execute("INSERT OR REPLACE INTO metadata VALUES ('worker_heartbeat',?)", (now(),))
                    current = db.execute("SELECT status FROM runs WHERE id=?", (rid,)).fetchone()[0]
                if current == "cancelling" or stop.is_set():
                    child.terminate()
                    try:
                        child.wait(timeout=8)
                    except subprocess.TimeoutExpired:
                        child.kill()
                        child.wait()
                    finish(rid, "interrupted" if stop.is_set() else "cancelled")
                    return
                stop.wait(0.5)
            if (folder / "result.json").exists():
                summary = json.loads((folder / "result.json").read_text())
                finish(rid, summary["status"], summary, summary.get("error"))
            else:
                finish(rid, "failed", error=f"Solver exited with code {child.returncode}; see solver.log")
        finally:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=10)
            if sleep_guard:
                sleep_guard.terminate()
            if os.name == "nt":
                import ctypes
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
            with connect() as db:
                db.execute("DELETE FROM metadata WHERE key='active_child'")

def pid_exists(pid):
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False

def recover():
    with connect() as db:
        orphan = db.execute("SELECT value FROM metadata WHERE key='active_child'").fetchone()
    if orphan:
        data = json.loads(orphan[0])
        if pid_exists(data["pid"]):
            # Do not signal a stored PID: it could have been reused by another app.
            raise RuntimeError("A prior solver process may still be alive. Its run remains preserved; wait for that process to exit before restarting the worker.")
    with connect() as db:
        rows = db.execute("SELECT id,status FROM runs WHERE status IN ('running','cancelling')").fetchall()
    for row in rows:
        file = run_dir(row[0]) / "result.json"
        if file.exists() and row[1] != "cancelling":
            summary = json.loads(file.read_text())
            finish(row[0], summary["status"], summary, summary.get("error"))
        else:
            finish(row[0], "interrupted", error="Worker stopped before completion. Create a new run from the preserved scenario.")

def main():
    init_db()
    lock = lock_worker()
    stop = threading.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop.set())
    worker_id = str(uuid.uuid4())
    try:
        recover()
        while not stop.is_set():
            with connect() as db:
                db.execute("INSERT OR REPLACE INTO metadata VALUES ('worker_heartbeat',?)", (now(),))
            rid = claim(worker_id)
            if rid:
                try:
                    execute(rid, stop)
                except Exception as exc:
                    finish(rid, "failed", error=str(exc))
            else:
                stop.wait(1)
    finally:
        lock.close()

if __name__ == "__main__":
    main()
