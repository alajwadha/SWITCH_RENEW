# Learn SWITCH: from zero to a defensible application

The learning section is a full, source-linked course inside the existing workbench—not a replacement model or a set of generated solver results. It works in both the local application and the static Vercel edition. Open **Learn SWITCH** in the sidebar, or append `?learn=what-switch-does` to the website URL.

## What is included

- **44 lessons in 10 parts**, with more than **24,000 words** of searchable lesson material, including worked examples and practice explanations. The word count includes equation annotations, goals and answers; it is not a measure of mastery or an estimated completion time.
- **54 rendered equations**, each explained in context and indexed in the model reference.
- **111 variable, parameter, set, expression, constraint, objective and registry entries**. Each includes a code object, symbol, meaning, units, domain/indexing, example, effect, source and related lesson.
- **44 worked examples** and **132 open-ended practice questions** with separately revealable explanations. These are not scored quizzes.
- **24 glossary entries** and a traceable source map.
- **Five interactive illustrations**: merit-order dispatch, capital recovery, physical versus representative time, stored-energy accounting, and two-stage investment/CVaR/information benchmarks.
- Full-text lesson search, reference search and type filtering, lesson deep links, previous/next navigation, mobile contents, reduced-motion support and personal reading markers.

Reading markers and the last-read lesson are saved in this browser's local storage. They are **not** uploaded, synced across devices or included in model-workspace backups. Clearing site data removes them. A blocked-storage warning makes this limitation explicit; lessons and calculations remain usable without storage.

## Learning path

| Part | Lessons | What the reader learns |
|---|---:|---|
| Start from zero | 4 | Model boundaries; planning versus forecasting; MW/MWh; capacity and load factors; inputs versus decisions; indexed algebra and unit checks. |
| Think like the optimizer | 3 | Hand-solved dispatch, capacity-expansion trade-offs, feasibility, LP/MIP, solver termination, dual interpretation and scaling. |
| Understand time | 3 | Periods, timeseries, timepoints, annual/period weights, representative days, chronology and weather alignment. |
| Follow the money | 3 | Overnight/FOM/variable costs, currency bases, capital recovery, discounting and the actual objective registries. |
| Build the power system | 8 | Vintages/suspension, thermal fuels, renewables/curtailment, storage, transmission, planning reserves, hydro and unit commitment. |
| Ask better policy questions | 4 | Carbon policies, renewable targets, flexible demand, fairness and accounting boundaries. |
| Work with real SWITCH files | 6 | Module hooks, input tables, the tiny tutorial, results, debugging, validation and controlled experiments. |
| Understand Xi Xi's Kenya application | 5 | Framework/data/code separation, county/time mapping, custom build limits, hydrogen integration and replication limits. |
| Plan before the future is known | 4 | Sensitivity versus stochastic/robust/simulation methods, non-anticipativity, CVaR, RP/EEV/WS/VSS/EVPI, scenario trees and holdout tests. |
| Design your own extension | 4 | External-demand contracts, an educational module skeleton, a new-country workflow and an eight-task capstone. |

The residential bottom-up demand model is retained as an **optional interface example**, not an assumed PhD topic or an implemented coupling.

## Deliberate model boundaries

1. **Core framework:** the pinned SWITCH source controls the actual algebra. Short teaching notation does not imply identically named code objects. Optional hydro, commitment and policy discussions do not mean those modules are active in Kenya.
2. **Kenya application:** country inputs instantiate the framework, while custom Python changes constraints/subsystems. Source availability, module activation, successful construction and an optimal validated solve are distinct milestones.
3. **Workbench:** prepares runs and displays saved artifacts locally; the Vercel build does not execute a national optimization.
4. **Browser illustrations:** pure TypeScript calculations with explicit simplifications. No API calls, hidden backend solves, result writes or changes to saved scenarios.
5. **Annual stochastic Pyomo lab:** remains the existing separate backend model. It is not the browser's two-demand, one-hour example and is not a native SWITCH/Kenya stochastic adapter.

## Source audit

Content was checked on 9 September 2026 against:

- SWITCH: `239d62cbe9baeec3bb05e56487241bdea60740af`.
- Kenya: `089834b8fee23239d61ffb6e7d68279f0a74efed`.
- Official tutorial: `6b72f3006854a81ac74d008d0145da1919c54d49`.
- Workbench baseline: `8253ca90cc9abaebe239a27cea1609ac3515a2b1`, before this learning expansion.

The source map lives in `components/learn/sources.ts`. Core and Kenya links use immutable revisions. Workbench documentation/backend links follow `main` and should be reviewed when those interfaces change.

Important implementation distinctions retained in the course:

- `tp_duration_hrs` advances physical storage/service equations; `tp_weight_in_year` weights annual accounting. SWITCH validates against 8,766 hours/year with tolerance; Kenya's inspected base weights sum to 8,760.
- The actual pinned storage investment object is `BuildStorageEnergy`, in **MWh**. `BuildGen` is its separate power investment in **MW**. The basic state equation places round-trip efficiency on charging.
- `GenCapacity` includes vintage and suspension accounting. Predetermined `BuildGen` values already represent existing assets; capital recovery is not simply erased by suspension.
- `SystemCost` is an expression; `Minimize_System_Cost` is the objective. Hourly and annual registry contributions have different units.
- Kenya base data contains 47 zones, 133 corridors, 24 annual periods, 192 timeseries and 1,152 timepoints. Four normal and four peak representative days per year carry different weights.
- The optional project-level branch of Kenya's `gen_build_limits.py` refers to undefined `tech`/`p` names. The inspected base has no `gen_build_limits.csv`, so an empty project-limit set can hide the defect while technology limits still construct. The lesson separates intended algebra from this source defect; upstream code is not silently patched.
- Neither the inspected `inputs/modules.txt` nor `inputs_h2-inf/modules.txt` activates `hydrogen_electrolyzers`. Folder names do not prove activation. The course also flags hydrogen output-weighting/percentage conventions, installed-versus-new capacity limits and capital-cost vintage treatment for audit.
- The previously recorded tutorial optimum is a verification result. Successful Kenya construction and a time-limited solve with no incumbent are **not** a national optimal solution. No Kenya solve was started for this content change.

The course is broad but does not claim exhaustive coverage of every optional SWITCH module, complete electrical-engineering training, a proven stochastic country adapter, or reproduction of a paper's full results. Advanced directions and the evidence needed to pursue them are listed in the capstone.

## Teaching calculation contracts

| Illustration | Boundary | Checks |
|---|---|---|
| Dispatch | Two fixed generators, one operating condition, linear variable costs, explicitly penalized shortage. | Merit order, balance, capacity bounds, shortage and cost; no startup, network or ramp constraints. |
| Finance | Capital plus connection cost per MW, real rate, positive life, annual FOM. | Zero/near-zero rate, CRF and units. Multi-period discounting is taught separately. |
| Time weights | One sampled point, repetitions over the whole period. | Physical duration, period/annual scaling and weighted energy/cost. Not an annual sample by itself. |
| Storage | Prescribed charge then discharge; charging-side efficiency. | Energy ledger and bounds. Infeasible schedules remain visible; separate power limits and cyclic closure are not imposed. |
| Uncertainty | Demand of 50/100 MW for one hour, shared capacity, zero running cost and penalized shortage. | Exact breakpoints; fractional probability mass in CVaR; risk-neutral information benchmarks remain separate from risk aversion. |

## Maintenance and tests

The course content is split by subject in `components/learn/`; the reader is `components/learning.tsx`, and its namespaced style sheet is `app/learn.css`. Course and chart code are lazy-loaded on entering Learn, preserving the existing atlas/scenario paths. No frontend dependency was added.

Run:

```bash
npm run build
node --experimental-strip-types --test tests/*.test.mjs
```

The new learning suite checks curriculum structure, source/lesson references, every KaTeX expression with strict parsing, search, resilient progress-state parsing, numerical worked examples and stochastic inequalities/optimality across a parameter grid. Existing scenario and atlas state tests run alongside it. TypeScript content is transpiled into an isolated temporary test directory; the test removes only that directory afterward.

Production compilation and unit/content tests are not a substitute for browser interaction, mobile/touch or screen-reader testing. No browser visual/interaction QA or national solve was performed for this update.
