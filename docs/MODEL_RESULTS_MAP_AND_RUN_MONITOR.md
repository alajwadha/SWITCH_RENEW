# Mapped model results and run monitoring

Date: 21 September 2026  
Status: documented product concept; implementation is future work.

## Core decision

Build a shared results explorer and run monitor for **Kenya first, then Somalia, Saudi Arabia and GCC models**. This applies to the **whole concept**: geographic results, regional and project drill-down, infrastructure layers, the complete results catalog, scenario comparison, exports and run timing. It is not limited to reusing map labels.

Use one common interface with model-specific geography, units, output mappings and available capabilities. A model must have prepared inputs, a validated adapter and genuine run outputs before it is presented as runnable or its results are displayed.

This document records the design requested by the user. It does not authorize starting a solve or implementing the interface. The interactive design previews used illustrative model values and timings; they are not Kenya solver results. Future Somalia, Saudi Arabia and GCC adapters are requirements, not a claim of present availability.

## Experience to build

A researcher should be able to select a saved run and answer:

- Where does the model build capacity, generate electricity, use storage or import power?
- What changes between investment periods or compatible scenarios?
- Which regional totals come from which modeled projects and connections?
- What can be located at an actual site, and what is known only at regional level?
- What other results exist beyond the headline map?
- Is the run waiting, constructing the model, solving or preparing outputs? How long has it taken, and is there a defensible estimate of time remaining?

The results screen combines a large map, a metric and period selector, a linked detail panel, charts/tables and an expandable results catalog. The run monitor remains available while navigating. Selecting an area updates the panel, charts and project list together; selecting a project or connection highlights its known geography.

The sourced country atlas remains an observational reference. Saved model inputs, model decisions, derived results and atlas observations must retain distinct identities and dates even when displayed together.

## Geography across models

| Model scope | Geographic presentation | Required adaptation |
| --- | --- | --- |
| Kenya | County boundaries, modeled county zones, projects and connections | Start with the existing 47-zone configuration; validate stable zone-to-boundary identifiers. |
| Somalia | Country, regions or districts where supported, modeled zones and assets | Use the adopted model's actual spatial resolution and documented boundary source. |
| Saudi Arabia | Country, administrative regions and any supported finer zones or assets | Map administrative areas to the model's electrical geography explicitly. |
| GCC | Regional overview, member-country drill-down, modeled zones, assets and cross-border connections | Support a multi-country model with consistent units, time periods and unique identifiers. |

Administrative boundaries and electrical zones are different concepts. If a model combines several regions into one zone, show that zone's result at its actual resolution. Do not copy it into each administrative area as though each had an independently modeled value. Finer boundaries may be shown for orientation, with the absence of finer results stated.

Store boundary source, version/date, license, geographic identifiers and the zone-to-boundary mapping. Keep countries, zones and assets uniquely identified across the GCC. Use model-specific geographic terms in the interface rather than hard-coding "county" everywhere.

### Labels and navigation

- Give every modeled area an identifiable label: the full name where it fits and a stable **2–3 letter abbreviation** inside small areas.
- Do not use leader or callout lines to connect labels to small counties. Electrical connections remain a separate, optional data layer.
- Show the full name on selection, hover and keyboard focus. Include a searchable area list and abbreviation key; avoid ambiguous codes within the displayed geography.
- Use zoom and detail views to resolve crowded areas. Keep areas accessible through the list at every screen size.
- Provide zoom, focus selected area, reset extent and layer controls. Keep numeric legends readable and avoid covering them with the detail panel.
- Plan for English and local-language names, including Arabic, without coupling labels to model identifiers. Keep units and numbers readable in either writing direction.

## Results coverage: more than the initial map

The catalog must inventory **all outputs produced by each active model/module**, not stop at the metrics in the preview. Every result needs a definition, units, spatial level, time basis, origin and availability status. Results without a meaningful location belong in system charts or tables and remain discoverable.

Use clear availability states: saved input, exported result, derived result, additional export needed, additional data/modeling needed, or not applicable. Only enable a quantitative map when the selected run supplies the necessary data.

| Result family | Geographic/detail level | Measures and interpretation |
| --- | --- | --- |
| Generation capacity | Project, zone, system | Existing and installed MW; new builds by investment period; suspension and retirement only where actually represented, kept distinct. |
| Generation and dispatch | Project, technology, zone | Timepoint dispatch in MW and time-weighted annual energy in MWh/GWh; generation mix and derived capacity factor. |
| Demand and energy balance | Zone and system | Saved demand inputs, weighted annual demand, peak among modeled samples and supply-demand balance. Demand inputs are not a new demand forecast produced by the solve. |
| Renewable availability | Project and zone | Available output and unused potential/curtailment where the required availability and dispatch data exist; state the calculation. |
| Storage | Project, zone, system | Power capacity in MW, energy capacity in MWh, builds, charging/discharging MW, annual charged/discharged energy, state of charge and modeled losses. |
| Transmission and trade | Connection, zone, country, system | Existing/new transfer capacity, directional flow, annual transfers, net imports/exports, losses, utilization and binding hours. |
| Fuel | Project, fuel, zone, system | Fuel consumption, saved prices and expenditure with native units and any explicit conversions. |
| Emissions | Project, zone, system | Model-accounted emissions, intensity and policy limits where supported; identify the emissions boundary and denominator. |
| Costs | Project, zone where attributable, system | Investment/capital recovery, fixed and variable operation/maintenance, fuel, storage and transmission components; annual and discounted-horizon costs kept separate. |
| Reserves and adequacy | Actual reserve region or system | Requirements, provision and headroom only at the region and times represented by the model; add exports where necessary. |
| Reliability | Supported model level | Unserved energy or related measures only if the model includes them. County energy balance alone cannot establish customer outage duration. |
| Constraints and economic detail | Relevant project, zone, connection or system | Binding limits, slack and shadow prices when valid and available for the formulation; explain any extra analysis needed. |
| Stochastic results | Scenario, supported geography, system | Scenario outcomes, probabilities, expected cost, risk measures, VSS and EVPI only for models that compute them; do not imply a stochastic Kenya adapter already exists. |
| Run and solution quality | Whole run | Termination condition, feasible solution availability, objective, solver bound/gap where available, validation checks and stage timings. |

For each implemented adapter, maintain an audit linking output files/columns to these views. Keep raw downloads available even when a specialized chart has not yet been built. New modules should extend the catalog through a result registry rather than requiring another country-specific screen.

### Numerical rules

- Convert power to energy using the model's represented-hour weights. Do not sum MW values and label the result MWh.
- Label sampled days and timepoints as samples. A sampled peak is not automatically the true annual peak.
- Keep storage power, storage energy capacity and timepoint state of charge separate. Avoid counting storage discharge as additional primary generation.
- Account consistently for transmission efficiency when calculating sent, received and net energy. Regional aggregation must not double-count internal transfers.
- Retain currency, price base year, annualization and discounting assumptions. System cost per MWh is not a retail tariff.
- Inspect the components of any reported generation-cost ratio before calling it a complete levelized cost measure; missing fuel costs must be visible.
- Sum additive quantities; recompute shares, intensities and ratios from their numerators and denominators. Do not average regional percentages indiscriminately.
- Distinguish a reported zero from missing, not applicable, unavailable and not modeled. Never turn a missing result into zero.
- Keep map scales consistent while comparing periods or scenarios, or clearly flag an intentional scale change. Show units and numeric bounds; center signed differences on zero.

## Plants and other local detail

Support optional layers for generation plants, storage, substations, model connections and sourced physical transmission routes where the data support them. Selecting a marker should expose its full name, technology, capacity, status, source date, location confidence and any explicitly linked model-project results.

For example, a verified plant in northern Turkana should appear at its sourced position, with the surrounding county visible. A county-only model project must not acquire a precise northern-Turkana location simply because its name or region suggests one.

Use three distinct location states:

1. **Verified site location:** sourced coordinates with a documented link to the modeled project, where such a link exists.
2. **Approximate or unverified location:** clearly differentiated marker and explanation of the uncertainty.
3. **Region only / unknown:** listed under its known zone without inventing a site pin.

A point's presence in the plant inventory does not prove that it is included in a run. Model-project and inventory identifiers need a reviewed crosswalk; name similarity alone is insufficient. Aggregate candidate projects may have no physical site yet.

Support clustered markers with a list of constituent units. Preserve unit/phase identities and avoid adding a whole-site capacity to its constituent units again. Retain unmatched, offshore and boundary-uncertain records in a searchable list; do not silently drop them or force them into the nearest county.

Distinguish schematic connections between model zones from surveyed line routes. A drawn straight connection does not establish the physical path of a power line. Keep observed infrastructure status and observation year separate from modeled future builds and the selected model year.

## Comparison, exploration and export

- Compare compatible saved runs using side-by-side maps or absolute/percentage differences, with the scenario revision and period always visible.
- Check geography, metric definition, time basis, units and currency basis before comparison. Require an explicit aggregation/mapping for differing zone systems.
- Where the baseline is zero or absent, show absolute change and explain why a percentage change is undefined.
- Link regional rankings, technology filters, time-series charts and project tables to the map selection.
- Offer regional fact sheets, selected-data CSV exports and map/chart exports with units, legend, period, run identity, source and solution status.
- Keep national/system totals alongside regional views so the researcher can reconcile the parts with the whole.
- Make a table/list alternative available for every map interaction, with keyboard access and distinguishable colors.

Additional layers such as resource potential, hydrology, land restrictions or sector-specific demand should be offered only when sourced data or an active model module justify them. These are optional extensions, not confirmed additions to the present modeling scope.

## Run monitor and time estimates

Show the user's elapsed time, current stage and a defensible estimate of remaining time without pretending optimization advances at a constant speed.

### Stage and timing display

Use explicit stages: queued, validating/preparing inputs, constructing the model, translating/loading the solver, solving, exporting/checking results and finished. Record the actual stage boundaries in the worker rather than guessing them from a timer.

Display:

- Submitted, started and finished timestamps as applicable.
- Queue wait separately from execution elapsed time; also show total wall-clock duration when useful.
- Current-stage elapsed time and the latest worker update.
- Estimated remaining time as a range, estimated finish window and confidence/explanation when enough comparable history exists.
- Configured solver time limit and its remaining budget, labeled separately from an estimate of completion.
- On completion, the actual total duration, stage breakdown and final solution status.

The solver budget begins when the solver's own timed operation begins. Model preparation and export can make total runtime exceed that budget. "Time limit remaining" must never be presented as "time until the result is ready."

### Honest estimates and solution status

- On a first run, after a major configuration change or without comparable history, show **"Not enough history to estimate"** while continuing to report elapsed time.
- Base estimates on comparable model sizes, active modules, time sampling, solver/version/options and hardware. Update a range as stages finish and explain major revisions.
- Treat time-limited, cancelled and interrupted runs separately from successfully completed runtime samples; they do not reveal the time that would have been needed for completion.
- Solver bounds, feasible objective and optimality gap may help explain progress when available. A gap is a solution-quality measure, not a percentage of work completed or a reliable countdown.
- Show "No feasible solution yet" when appropriate. Any deliberately exposed interim solution must be labeled provisional and traceable to a saved snapshot.
- Distinguish optimal, feasible but stopped, time limit without a feasible solution, infeasible, failed, cancelled and interrupted. A time limit is not success or proof of optimality.
- Use an indeterminate solving indicator unless a stage has a real measurable denominator. Do not invent an overall completion percentage.
- A lost browser/backend connection is a separate state from solver failure. Show last-known status and update time, mark it stale and reconcile after reconnection.
- Reloading or closing the browser must not control worker lifetime. Do not imply that an interrupted solver can resume unless checkpoint recovery is actually supported.

Detailed logs and solver diagnostics should be expandable beneath the plain-language status. A cancel action should preserve run provenance and report cancellation only when the worker confirms it.

## Implementation approach for later work

1. **Audit data and capability:** inventory the actual outputs of each model, define metrics/units/aggregation, identify missing exports, validate zone identifiers and review geographic sources.
2. **Build the shared result contract:** model/adapter version, run and scenario revision, period/timepoint, zone/project/connection identity, metric definition, value/unit, origin, quality and provenance. Add model geography configuration, location crosswalks and a capability registry.
3. **Build the Kenya explorer:** county boundaries and simple labels, region/project/connection inspectors, supported layers, catalog, charts, compatible-run comparison and exports.
4. **Add worker telemetry:** durable stage events, timestamps, heartbeat and solver diagnostics where supported; develop and check runtime ranges using genuine run history.
5. **Add geographic adapters:** bring Somalia, Saudi Arabia and GCC models into the same experience as their inputs, adapters, mappings and outputs are validated. No duplicate Kenya-specific application and no misleading enabled run controls.
6. **Verify end to end:** reconcile the map, detail panels, charts and exports against saved outputs; exercise missing data, uncertain locations and each run termination state.

The later implementation must preserve immutable input/output snapshots, model/source revisions, units and existing workspace data. Existing requirements continue to apply: see [Requirements review](REQUIREMENTS_REVIEW.md), [Atlas map](ATLAS_MAP.md), [Atlas data](ATLAS_DATA.md) and [Verification](VERIFICATION.md).

## Acceptance criteria

- [ ] The shared design explicitly covers Kenya, Somalia, Saudi Arabia and GCC results, local detail and run monitoring; actual availability follows validated adapters.
- [ ] Geographic labels use full names or short 2–3 letter codes without label leader lines, with full-name lookup and keyboard access.
- [ ] Modeled zones and administrative boundaries are mapped explicitly; no unsupported county/subcounty precision is implied.
- [ ] Every available output is accounted for in the catalog; unavailable results explain what data, export or module is missing.
- [ ] Regional, project, connection and system results reconcile, with correct time weights, units and aggregation.
- [ ] Real plant positions have sources and confidence; model-to-inventory links are explicit; unknown or unmatched sites remain accessible.
- [ ] The selected run, revision, period and solution status remain visible through maps, charts, comparison and export.
- [ ] Run timing distinguishes queue, construction, solving and output preparation; remaining-time estimates are qualified and may be unknown.
- [ ] Solver gap and configured time limit are not misrepresented as completion progress.
- [ ] Reload, disconnection, interruption, cancellation, time limit and infeasibility are represented accurately.
- [ ] Responsive layouts, small areas, missing values, zero values and color/keyboard accessibility are checked.
- [ ] Documentation and previews cannot be mistaken for completed model implementation or genuine solved results.
