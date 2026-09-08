# SWITCH Workbench

A local research workbench for Ali: edit assumptions, run SWITCH, inspect results, compare experiments, explore a sourced country globe, and learn the equations.

This is the first working implementation milestone. It includes actual optimization; charts are generated from saved solver results. The broader v1 roadmap remains in `docs/REQUIREMENTS_REVIEW.md`.

## Start on your computer

Install **Python 3.12**, **Node.js 22 or later**, and **Git**. Keep this folder on a normal local disk, outside a continuously synced cloud-drive folder.

From this project folder, run the one-time setup:

```bash
python scripts/setup.py
```

On macOS/Linux, your Python command may be `python3`. On Windows, `py -3.12` can be used. The setup installs the pinned Python environment, clones the pinned model repositories, installs frontend dependencies and builds the local website. The Kenya repository is large; `--skip-kenya` installs the tutorial and stochastic lab first. Run setup again without the flag to add Kenya.

Then double-click:

- **Windows:** `Start_Workbench.bat`
- **macOS:** `Start_Workbench.command`
- **Linux:** `Start_Workbench.sh` (or run `.venv/bin/python scripts/launch.py`)

The browser opens at **http://127.0.0.1:8765**. Backend and worker are detached from the launcher; its terminal can be closed. Closing a browser tab does not cancel a run. The computer still needs to remain powered on and awake. macOS/Windows idle-sleep inhibition is best-effort and does not protect against shutdown or closing the lid.

The service log is `workspace/service.log`. If an operating system blocks an executable download, inspect the scripts and use the Python launch command. This build was exercised on Linux/Python 3.12; Windows/macOS launch paths have been authored but not tested on those operating systems.

## First experiment

1. Create a **Three-zone tutorial** scenario.
2. Keep the baseline multipliers at 1. Validate inputs and run.
3. The published baseline objective is approximately **126,750,492.1068** in the model's base-year dollars. The verification test compares the new solution to the pinned upstream reference.
4. Duplicate the scenario, increase the demand multiplier to 1.2, save its revision, and run again.
5. Open **Compare runs**. Use **Input snapshot** to trace exactly what changed.

## Editing assumptions

Use the number boxes for exact multipliers or the sliders for exploration. The input table previews the current draft immediately: the pinned baseline is scaled first, then absolute cell overrides replace individual values. Each editable column has a unit, definition and allowed range under **Variables, units and allowed values**. **Remove override** restores the baseline with the current multiplier; **Clear all overrides** applies to every input table.

Drafts remain available when switching views or scenarios while the page is open. The Scenarios badge counts unsaved drafts. **Save revision** writes a draft to disk; browser draft memory is not a backup. A browser close/reload warning is requested while drafts exist, but browser or device shutdown can still lose unsaved drafts.

If another window updates the same scenario, your draft keeps its original revision. Save the draft as a new copy or discard it to load the latest saved revision. Validation and run submission explicitly name the revision being used and reject stale requests. A run never silently substitutes a newer revision.

The **Kenya base** model uses its pinned county configuration and `gen_build_limits.py`. Storage and reserves are active. It constructs with 778,293 variables and 1,040,868 constraints. A 15-second integration check reached the solver but found no incumbent before the limit; a full optimal Kenya solve has not been verified. The limit covers solver time, not model construction/translation. See `docs/VERIFICATION.md`. Hydrogen variants and a Kenya stochastic adapter are not implemented in this milestone.

The **Two-stage learning lab** is a separate original Pyomo model with three demand outcomes, shared firm/solar investments and scenario-specific dispatch. It reports expected annual cost, CVaR, VSS and EVPI. It is explicitly illustrative and is not presented as a Kenya model or a native SWITCH stochastic extension.

## What is saved automatically

- Saved scenario configuration, numerical input overrides and revision number.
- A separate run directory with original input snapshot, SHA-256 hashes, solver options and source pins before it enters the queue.
- A separate effective input copy if the pinned SWITCH upgrader is required. The tutorial's 2.0.7 inputs need migration; the original inputs remain intact.
- Solver logs, termination status, runtime/dependency versions, workbench code hashes, CSV outputs, selected processed Parquet tables and a result summary.
- Cancelled, failed and interrupted run records.

**Saving is not solver checkpointing.** Logs and completed artifacts survive, but a partially solved optimization is not generally resumable. The worker labels unfinished runs interrupted and you can submit a fresh run. The UI requires Save revision for changes to become authoritative; queued runs never read an unsaved browser draft.

## Back up and move laptops

Use **Workspace & backups → Create & download backup** once active jobs have finished or been cancelled. A backup contains a consistent SQLite snapshot, run folders and atlas source downloads. Keep completed archives in your chosen backup service. Do not sync the live SQLite database with OneDrive/Dropbox/Google Drive.

On the next laptop, clone this repository, run setup, then restore to a **new** workspace directory before launching:

```bash
# macOS/Linux
.venv/bin/python scripts/workspace.py restore /path/to/switch-workspace.zip --destination workspace

# Windows
.venv\Scripts\python.exe scripts\workspace.py restore C:\path\switch-workspace.zip --destination workspace
```

Restore refuses to overwrite an existing directory, rejects traversal/symlink archive entries and verifies every checksum. `SWITCH_WORKSPACE` can select another workspace folder. A previously used default `workspace/` can be kept by restoring to a different directory and setting that environment variable; never delete your prior work just to satisfy restore.

The downloadable code package is separate from a workspace backup. Git contains code, source lockfiles, compressed global country snapshots, documentation, tests and CI. The live workspace, large model downloads, logs, database, solver licenses and dependencies are excluded.

## GitHub

Repository: https://github.com/alajwadha/SWITCH_RENEW

This repository is public. Git stores the application and setup; workspace databases, run outputs, licenses and large source downloads remain excluded by `.gitignore`.

Clone on any laptop:

```bash
git clone https://github.com/alajwadha/SWITCH_RENEW.git
cd SWITCH_RENEW
python scripts/setup.py
```

Then open the platform launcher. Restore a completed workspace backup to recover saved scenarios and results. If using a terminal coding assistant, give it this repository and ask it to follow this README, run setup, verify the tutorial test, and launch the app. No particular coding assistant is required to use the workbench.

For an existing source checkout, connect the remote if it is not already configured:

```bash
git remote add origin https://github.com/alajwadha/SWITCH_RENEW.git
```

Use regular commits and pushes for future updates. Never force-push over remote work or commit the live workspace.

## Country atlas

All **251 country and territory profiles** share 12 energy sections, plus country context: generation; capacity and projects; electricity demand; the whole energy system; fuels and security; emissions; trade and grids; storage and flexibility; prices and costs; access and reliability; renewable resources; policies and targets.

The expanded snapshot contains **278 indicators**, **253 with observations somewhere**, **37,124 latest country values** and **488,520 historical observations**. Sources include Ember, IRENA, EIA, World Bank, OWID, Eurostat, Solargis/ESMAP, Net Zero Tracker, RFF, Global Energy Monitor and DOE/NTESS Sandia. Source coverage differs by country. See [the full data dictionary and coverage audit](docs/ATLAS_DATA.md).

Use the searchable section controls, country overview, generation/capacity charts, historical comparisons and globe layers. Compare up to six countries in the same observation period or choose latest available with dates displayed. Compatible totals can be shown per person using population from the same year. Annual growth requires the immediately preceding year. CSV exports include units, sources and dates; chart exports are SVG. The infrastructure view filters plants and projects by technology, status and name, with source links and CSV downloads.

GEM's **February 2026** inventory supplies 143,109 original plant/unit/phase records. Country allocations of cross-border hydro give 143,172 displayed records. The separate historical DOE/NTESS **January 2022** inventory supplies 1,045 battery/chemical-storage projects. Neither inventory is a current, complete national installed-capacity total.

Annual observations stop at the latest completed calendar year, **2025**, with earlier years where necessary. Available monthly 2026 data and matched-month YTD comparisons are separately labeled. Policy snapshots retain their source dates; solar potential retains its long-term **2020 study** basis. Global 2025 technology cost benchmarks are separate from country prices. No country statistic automatically changes SWITCH inputs.

Missing observations remain null. Some requested national measures have no connected comparable dataset, including current battery MWh, utility SAIDI/SAIFI, bilateral interconnector capacities, LNG terminals and country wind summaries. Those fields explain the gap in **Data coverage**. There is no synthetic universal 2025/2026 dataset.

To fetch updated data, stop the local app and run while online, then rebuild and restart:

```bash
.venv/bin/python scripts/refresh_atlas.py --refresh
npm run build
```

Windows uses `.venv\Scripts\python.exe`. Omitting `--refresh` reuses cached source files; `--offline` requires a complete cache and makes no downloads. New source files are validated before publishing a replacement snapshot. The entry point refreshes the complete atlas, including the original country context. Updates to pinned IRENA/DOE/GEM releases should be reviewed before changing their declared vintage.

Provider responses and request/hash records are kept under ignored `workspace/atlas_raw/`. The bundled manifest points to compressed country indices, histories, infrastructure and provenance under `public/atlas/`; all are included in Git. Data is unpacked by modern browsers with the standard DecompressionStream API. Only the histories and inventories needed by the current view are loaded; global matched-period maps load the full history. Natural Earth geography is also bundled, so the globe does not need an online tile server. Country selection remains available when WebGL is unavailable.

## Architecture and development

- Next.js, React, TypeScript, Motion, MapLibre and Recharts.
- Static frontend production export served by FastAPI on loopback.
- SQLite with transactions and revision checks, plus immutable filesystem artifacts.
- A separate single-worker queue that spawns one solver process per run.
- Pinned SWITCH 2.0.9, Pyomo 6.9.1 and HiGHS. No commercial solver license is needed for this milestone.

To run services explicitly for development/troubleshooting:

```bash
.venv/bin/python -m uvicorn backend.api:app --host 127.0.0.1 --port 8765 --no-proxy-headers
# Separate terminal:
.venv/bin/python -m backend.worker
```

For frontend source changes, rebuild with `npm run build`; the Python server serves `out/`. The source also retains `npm run dev`, but the integrated same-origin workflow uses the production export. The service processes started by the launcher persist until OS shutdown or deliberate process termination; stopping them during a solve interrupts it.

```bash
npm run build
node --experimental-strip-types --test tests/*.test.mjs
.venv/bin/python -m pytest -q
```

Tests cover an actual tutorial solve versus its published reference; input migration and immutability; scenario revision conflicts; numerical input validation; queue claims/cancellation/interruption; restart persistence; backup/restore/tampering; two-stage benchmark inequalities and physical balances; sourced country dates; and serving the production UI with the real API. Browser rendering and interaction QA has not been performed in this environment.

The editor regression checks cover the actual save-request serializer, draft preservation across newer revisions, invalid cell edits, and multiplier/override preview order. API clients must include `{"revision": 1}` (using the selected saved revision) in POST bodies for `/api/scenarios/{id}/validate` and `/api/scenarios/{id}/run`. After updating application code, restart the local backend and worker and reload the page.

## Sources and permissions

- SWITCH core: https://github.com/switch-model/switch — Apache-2.0; pinned revision in `sources.lock.json`.
- Official tutorial: https://github.com/switch-model/switch_tutorial — preserve its upstream licensing.
- Kenya: https://github.com/NotEleven/Switch-Kenya-2025_public — **CC BY-NC 4.0**, noncommercial research/academic use. Dataset terms are retained upstream; do not treat public availability as permission for commercial reuse.
- World Bank: https://data.worldbank.org/indicator — source methodology and organization available in the atlas. Review indicator-specific third-party reuse conditions.
- Natural Earth: https://www.naturalearthdata.com/about/terms-of-use/ — public domain.
- Next.js static export: https://nextjs.org/docs/app/guides/static-exports
- MapLibre globe: https://www.maplibre.org/maplibre-gl-js/docs/examples/display-a-globe-with-a-vector-map/

Do not expose this local-only backend to the public internet. Authentication, remote job submission and cloud storage are separate future capabilities, not activated by putting the code on GitHub or hosting the frontend on Vercel.
