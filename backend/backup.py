"""Consistent portable backups: quiescent workspace, SQLite backup, file hashes."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
import uuid
import zipfile
from backend.core import ACTIVE, ROOT, connect, hashes, now, workspace

def create_backup():
    destination = ROOT / "backups"
    destination.mkdir(exist_ok=True)
    name = f"switch-workspace-{now()[:19].replace(':','-')}-{uuid.uuid4().hex[:6]}.zip"
    target = destination / name
    with tempfile.TemporaryDirectory(prefix="switch-backup-") as temp:
        staging = Path(temp)
        # Block new queue entries/claims during the snapshot; refuse active runs.
        with connect() as gate:
            gate.execute("BEGIN IMMEDIATE")
            if gate.execute("SELECT COUNT(*) FROM runs WHERE status IN ('queued','running','cancelling')").fetchone()[0]:
                raise ValueError("Finish or cancel active jobs before creating a consistent workspace backup")
            source = sqlite3.connect(workspace() / "workbench.sqlite")
            output = sqlite3.connect(staging / "workbench.sqlite")
            try:
                source.backup(output)
            finally:
                source.close()
                output.close()
            # Only copy committed terminal runs. Another request may be preparing
            # an as-yet-unqueued directory while this transaction holds the gate.
            for row in gate.execute("SELECT id FROM runs"):
                source_folder = workspace() / "runs" / row[0]
                if source_folder.exists():
                    shutil.copytree(source_folder, staging / "runs" / row[0])
            if (workspace() / "atlas_raw").exists():
                shutil.copytree(workspace() / "atlas_raw", staging / "atlas_raw")
        manifest = {"schema_version": 1, "created_at": now(), "files": hashes(staging), "note": "Consistent SQLite backup plus run artifacts. Source code and solvers are restored separately from Git and lockfiles."}
        (staging / "backup_manifest.json").write_text(json.dumps(manifest, indent=2))
        temporary = target.with_suffix(".zip.tmp")
        try:
            with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for file in sorted(staging.rglob("*")):
                    if file.is_file():
                        archive.write(file, str(file.relative_to(staging)))
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
    return target

def restore_backup(archive_path, destination):
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("Restore requires a new destination directory; existing workspaces are never overwritten")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.with_name(destination.name + ".restore-" + uuid.uuid4().hex)
    staging.mkdir()
    try:
        with zipfile.ZipFile(archive_path) as z:
            members = z.infolist()
            if sum(m.file_size for m in members) > 10 * 1024**3:
                raise ValueError("Archive exceeds the 10 GiB restore limit")
            names = set()
            for m in members:
                p = PurePosixPath(m.filename)
                if p.is_absolute() or ".." in p.parts or "\\" in m.filename or ":" in m.filename or m.filename in names:
                    raise ValueError("Unsafe archive entry")
                names.add(m.filename)
                if (m.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("Symlinks are not accepted in workspace backups")
                if p.parts[0] not in ("workbench.sqlite", "runs", "atlas_raw", "backup_manifest.json"):
                    raise ValueError("Unknown top-level backup entry")
            z.extractall(staging)
        manifest = json.loads((staging / "backup_manifest.json").read_text())
        (staging / "backup_manifest.json").unlink()
        if manifest["schema_version"] != 1 or hashes(staging) != manifest["files"]:
            raise ValueError("Backup checksum verification failed")
        db = sqlite3.connect(staging / "workbench.sqlite")
        try:
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok" or db.execute("PRAGMA user_version").fetchone()[0] != 1:
                raise ValueError("Database integrity/schema check failed")
            db.execute("DELETE FROM metadata")
            db.execute("UPDATE runs SET status='interrupted',error='Restored from backup' WHERE status IN ('queued','running','cancelling')")
            db.commit()
        finally:
            db.close()
        staging.rename(destination)
        return destination
    except Exception:
        shutil.rmtree(staging)
        raise
