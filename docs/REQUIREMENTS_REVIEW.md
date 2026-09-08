# Requirements review · 7 September 2026

Basis: retained requirements from the latest master prompt and separate GitHub addendum. The two original writing blocks could not be retrieved verbatim; this is an implementation interpretation, not a claim of line-by-line verification.

The agreed direction is sound: a personal local SWITCH workbench with a Next.js/React/TypeScript interface, FastAPI, separate solver workers, SQLite metadata, immutable run directories, Parquet results, smooth transitions, a global country atlas and a genuine stochastic capability. It is not a PhD contribution in itself. Residential buildings demand remains only an optional extension example.

## Corrections applied
1. Browser lifetime must not control solver lifetime. A separate worker claims durable SQLite jobs. Interrupted jobs retain inputs/logs and become interrupted; no promise of resuming a solver without a supported checkpoint.
2. Saving is distinct from backing up. Runs are saved locally; a completed checksum-verified workspace archive is required when moving computers. GitHub holds code and setup, not live databases or all outputs.
3. Snapshot every input and options before queuing; store hashes, source revisions, dependency versions, status and termination condition. Never treat a time limit as optimal.
4. Display actual timepoint-weighted energy and discounted cost from SWITCH. Never sum MW values as annual MWh or substitute atlas national statistics for model inputs.
5. Stochastic is a real two-stage teaching formulation first, with common build decisions, scenario-specific dispatch, probabilities, explicit units, VSS/EVPI and optional CVaR. Kenya stochastic remains a later separately validated adapter.
6. Country data: latest completed 2026 where available, else 2025, else earlier; source and observation year on every value. Missing is null, never zero. YTD must not masquerade as annual. All country/territory profiles share a schema; source coverage varies.
7. Local runtime is served on loopback. A Next.js static production export can be served by FastAPI, simplifying daily launch to one local service plus a worker. It preserves the future Vercel frontend path.
8. Local sleep prevention is OS-dependent and best-effort, never a guarantee that a closed lid or shutdown will preserve a solve.
9. Kenya baseline is trusted pinned source, read-only from the application. Country boundaries carry their own attribution and are descriptive, not a claim about disputed borders.
10. Use the dedicated `alajwadha/SWITCH_RENEW` repository, created by the user. The user confirmed that the repository should remain public. Track the complete application, setup, source pins, country snapshot, documentation and tests; move saved scenarios and results through workspace backups.

## This implementation milestone
- Local launcher, pinned source bootstrap, reproducible dependency lockfiles, CI.
- Real official 3_zone_tiny and base Kenya adapter with validation, immutable inputs and robust job records.
- Scenario parameters plus numerical CSV editing with version conflict detection.
- Exact multiplier entry, live draft input previews, parameter definitions/units/ranges, draft retention across in-app navigation, and revision-specific validation/run requests.
- Results, manifests, raw exports, scenario comparisons and logs.
- Globe with bundled Natural Earth geography and 251 country/territory profiles. All 12 energy sections have sourced observations, historical and matched-period comparisons, CSV/SVG exports, global plant inventory and a separately dated historical storage inventory. Source gaps are explicitly audited in ATLAS_DATA.md.
- Learning view explaining equations, input versus decision variables, stochastic versus sensitivity.
- Genuine two-stage teaching model with expected cost, VSS, EVPI and CVaR.
- Consistent backup/restore with checksums and no overwrite of an existing workspace.

The final verification evidence and material limits are recorded in `VERIFICATION.md`.

## Remaining complete-v1 roadmap
Kenya custom variants and county layers; remaining atlas data-source gaps (see ATLAS_DATA.md), including current national battery ratings, bilateral interconnectors and utility reliability; batch experiments/sensitivity orchestration; SWITCH-based stochastic extensive form then Kenya scale study; advanced constraints/duals and infeasibility diagnosis; optional module authoring; authenticated remote workers/HPC and cloud storage. Preserve the broader prompt as the roadmap, and show only implemented capabilities as active.
