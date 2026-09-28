"""Package the public research snapshot; never include local report caches."""
import argparse
import csv
import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "somalia-data-2026-09-28"
MANIFEST = Path("manifests/publication_archive.json")
INVENTORY = Path("manifests/publication_files.csv")


def public_files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if "__pycache__" in relative.parts or "references_cache" in relative.parts:
            continue
        if path.name.startswith(("power_source_", "power_verify_")):
            continue
        if relative.parts[:2] == ("raw", "global_solar_atlas") and path.suffix == ".zip":
            continue
        if relative == MANIFEST:
            continue  # Avoid a circular archive checksum.
        yield path, relative


def in_git(path):
    return path.suffix.lower() not in (".tif", ".tiff")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--copy-git-to", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise SystemExit("Place the release archive outside the source data directory.")
    if output.exists():
        raise SystemExit("Refusing to overwrite an existing archive; choose a new output path.")
    files = [(p, r) for p, r in public_files() if r != INVENTORY]
    allowed = {".py", ".md", ".csv", ".json", ".geojson", ".xlsx", ".zip", ".tif", ".tiff"}
    unexpected = [str(r) for p, r in files if p.suffix.lower() not in allowed and p.name != ".gitignore"]
    if unexpected:
        raise SystemExit("Review unexpected file types before publication: " + repr(unexpected))
    rows = [dict(path=r.as_posix(), bytes=p.stat().st_size,
                 sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                 distribution="git_and_release" if in_git(p) else "release_only") for p, r in files]
    with (ROOT / INVENTORY).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "bytes", "sha256", "distribution"])
        writer.writeheader()
        writer.writerows(rows)
    files.append((ROOT / INVENTORY, INVENTORY))
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path, relative in files:
            archive.write(path, VERSION + "/" + relative.as_posix())
    with zipfile.ZipFile(output) as archive:
        bad = archive.testzip()
        if bad:
            raise SystemExit("Archive CRC failed: " + bad)
    manifest = dict(version=VERSION, packaged_at_utc=datetime.now(timezone.utc).isoformat(),
                    filename=output.name, bytes=output.stat().st_size,
                    sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                    archive_members=len(files), inventory_rows=len(rows),
                    inventory_excludes=[INVENTORY.as_posix(), MANIFEST.as_posix()],
                    archive_excludes=[MANIFEST.as_posix(), "unpublished report caches, page renders and temporary dependencies"],
                    archive_crc_checked=True,
                    release_url="https://github.com/alajwadha/SWITCH_RENEW/releases/tag/" + VERSION,
                    asset_url="https://github.com/alajwadha/SWITCH_RENEW/releases/download/" + VERSION + "/" + output.name,
                    licensing="Dataset-specific terms in source register and sidecars; no blanket relicensing")
    (ROOT / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if args.copy_git_to:
        destination = args.copy_git_to.resolve()
        if destination.exists() and any(destination.iterdir()):
            raise SystemExit("Git publication destination must be empty; no existing research is overwritten.")
        for path, relative in files + [(ROOT / MANIFEST, MANIFEST)]:
            if not in_git(path):
                continue
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
