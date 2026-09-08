# Verification · 8 September 2026

## Passed
- Next.js production export compiles and TypeScript passes.
- Python test suite: **10 passed**. The suite includes real solver execution, input migration/checksums, revision conflicts, validation, queued and running cancellation, interrupted-job recovery, service-restart persistence, consistent backup/restore and tamper/path rejection, and stochastic benchmark/physical balance checks.
- Official `3_zone_tiny` baseline objective: **126,750,492.10678375**, matching the pinned upstream published reference within the test tolerance of 1e-7 relative.
- Tutorial demand multiplier 1.2: **152,435,913.2644603**. Both runs terminate optimal.
- Risk-neutral and risk-averse teaching lab runs terminate optimal. Risk-neutral benchmarks satisfy WS ≤ RP ≤ EEV, with VSS = EEV − RP and EVPI = RP − WS.
- Country snapshot: **251 country/territory profiles**, **11 indicators**, **2,192 nonmissing latest observations** and **242 geographic features**. Final refresh recorded zero provider request errors. Values retain actual observation years; e.g., demographic/economic data may be 2025 while some energy indicators are earlier.
- Production HTML and bundled geography are served by the actual FastAPI app in HTTP integration checks.

## Kenya integration result
The base model constructs successfully and reaches HiGHS: **778,293 Pyomo variables**, **1,040,868 constraints**, including discrete investment decisions. A 15-second solver time limit ends during presolve without an incumbent; this is stored as `no_solution`, termination `maxTimeLimit`. Total construction/translation/solve handling was approximately 165 seconds. The time limit applies to the solver phase, not full Python data loading/model construction. **A complete optimal Kenya solve has not been verified.**

## Practical limits
- Tests ran on Linux and Python 3.12. Windows/macOS launcher paths are authored but have not been exercised on those operating systems.
- Browser rendering, WebGL behavior, responsive interaction and animation QA have not been performed. Compilation and HTTP checks do not substitute for that.
- Local backend only: no authenticated remote/HPC worker, cloud database or Vercel deployment has been connected. The public `alajwadha/SWITCH_RENEW` repository stores code and setup; it does not run the models or automatically back up the live workspace.
- Stochastic lab is a separate teaching model; Kenya stochastic, hydrogen variants and detailed county-map layers remain on the roadmap.
- World Bank statistics are the first atlas data layer. 2025 electricity mix/capacity/emissions via Ember/IRENA and broader policy data require separate adapters.
- The optional example-workspace backup contains completed tutorial and teaching runs; it is not a national Kenya solution.
