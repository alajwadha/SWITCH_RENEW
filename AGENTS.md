# SWITCH_RENEW — Research and Collaboration Instructions

**Status:** approved by the user on 27 September 2026.  
**Scope:** the shared SWITCH workbench, Kenya, Somalia work, and later Saudi Arabia/GCC models.

These are the repository-wide instructions. Before substantive work, also read and follow the [research workflow](docs/RESEARCH_WORKFLOW.md), which contains the required live explanations, continuous documentation and Dan Kammen consultation process. For Somalia work, also read [models/somalia/AGENTS.md](models/somalia/AGENTS.md).

Use the [documentation index](docs/DOCUMENTATION.md) to find the current records. The [research backlog](docs/RESEARCH_BACKLOG.md) contains proposals, not authorization to implement them or start model runs. The [map/results design](docs/MODEL_RESULTS_MAP_AND_RUN_MONITOR.md) remains planned work.

## Independent judgment and collaboration

- Give your own assessment before accommodating the user's position. Do not automatically agree, reject, defend or contradict.
- Evaluate ideas using evidence, scientific reasoning, practical consequences and the research objective.
- Say clearly whether you agree, partly agree, disagree or remain uncertain. Explain the main reason and recommend a next step.
- Distinguish facts, assumptions, interpretations and recommendations.
- If the user has already made a decision, evaluate it honestly. Prioritize correcting a fixable mistake over rationalizing it.
- Change your assessment when the evidence changes. Do not manufacture disagreement to appear independent.
- Treat reviewer comments, advisor suggestions and AI-generated findings as claims to investigate before changing the model.
- Preserve the user's project, existing changes and agreed scope. Follow the latest explicit user decisions and record changes to earlier agreements.

## ADHD-friendly explanations

- Put the immediate answer, action or recommendation first.
- Explain one main idea at a time. Use short paragraphs, numbered steps, selective bolding and useful examples.
- Introduce unfamiliar terms when needed. Connect technical details to their purpose.
- Show units with numbers. Distinguish concepts such as capacity versus generation, modeled demand versus observed consumption, and system cost versus customer tariff.
- Use diagrams, maps or tables when they clarify something that prose cannot explain as easily.
- Make the next step clear without presenting a long, unranked list of choices.
- Be concise in each explanation without omitting necessary steps, assumptions or limitations.
- When mixing Arabic and English, preserve readable RTL/LTR order. Keep equations, numbers and units together in an isolated LTR expression.

## Reliable sources and numerical evidence

- Prefer original official statistics, regulators, utilities/system operators, original datasets and peer-reviewed research.
- Evaluate a source's method, coverage, date, definitions and suitability. A reputable publisher does not automatically make a value appropriate for the study.
- Use search snippets, secondary summaries and AI-generated responses for discovery, not as final evidence for numerical claims.
- Open and inspect the supporting source. Verify the exact value or claim, not merely that the document exists.
- Record dataset identifiers, table/page references, extraction methods or code where available.
- Never invent citations, DOIs, quotations, data values or verification results.
- Distinguish the observation period, publication date, retrieval date and modeled future year.
- Prefer the most appropriate verified evidence. Explain why an older source is retained when newer information exists.
- Check geographic and sector coverage before transferring values between countries.
- Respect data licenses and redistribution restrictions.

### Conflicting evidence

When sources disagree:

1. Check whether their definitions, dates, coverage and units differ.
2. Preserve both source records.
3. Explain which source is selected and why.
4. Test alternatives if the disagreement could change the conclusions.
5. Escalate unresolved, consequential conflicts.

Do not silently average incompatible figures or select whichever supports the preferred result.

## Parameters, assumptions and missing data

Give each important parameter a stable identifier and record:

- Value and units.
- Geographic and sector scope.
- Reference year and currency/base year where relevant.
- Source and precise location within that source.
- Extraction, conversion or transformation.
- Implementation location.
- Uncertainty and known limitations.
- Status: verified for this use, provisional, pending, conflicting or superseded.

Distinguish observed data, derived data, proxies, expert assumptions, scenario choices and placeholders.

- Missing is not zero.
- A proxy needs a donor source, justification, adjustment method, limitations and sensitivity check.
- Do not describe a source-backed proxy as a direct observation for Somalia.
- Placeholders must be visibly identified and prevented from silently entering the production baseline.
- Separate uncertainty caused by missing knowledge from variability represented by the model.
- Scenario ranges are not automatically probabilities or statistical confidence intervals.
- Do not introduce precision that the evidence cannot support.
- Mark assumptions that materially control the conclusions and prioritize improving their evidence.

## Preserve data and make runs reproducible

- Preserve raw data unchanged. Perform transformations through reproducible scripts.
- Record source versions, retrieval dates, checksums and licenses.
- Keep substantial datasets, databases and run outputs in suitable storage, with tracked manifests and retrieval instructions.
- Keep live workspace databases on appropriate local storage rather than relying on a synchronized folder.
- Never commit credentials, private tokens or confidential data.
- Preserve previous run snapshots when assumptions change.

Each run must identify:

- Model and scenario revision.
- Input hashes and active modules.
- Workbench and upstream model versions.
- Dependency and solver versions.
- Solver settings and random seeds where relevant.
- Submission, start and finish times.
- Termination condition and available solution quality information.
- Output locations and validation results.

Use portable paths and document the execution order. Provide a reproducible route from source inputs to figures and reported results.

## Model correctness and validation

Check the scientific meaning of the implementation as well as whether the code runs.

- Verify energy balances, capacity limits, storage behavior, transmission losses and cost accounting.
- Use represented-hour weights when converting power into annual energy.
- Keep MW, MWh, annual costs and discounted planning-horizon totals distinct.
- Distinguish existing capacity, new construction, suspension and retirement.
- Separate calibration from validation. Record what was adjusted and why.
- Where possible, validate against evidence not used to tune the model.
- Define appropriate validation criteria and numerical tolerances before interpreting the results.
- Do not silently rescale outputs to match a benchmark or impose the conclusion the study is meant to test.
- Investigate surprising results before explaining them as scientific findings.
- Use small examples with understandable expected behavior to check important equations and constraints.
- Verify that scenario controls actually affect the intended equations and outputs.
- Recheck affected results after a correction.

Validation claims must state their scope. "These checks passed" does not mean that every model behavior has been validated.

## Scope, execution and resource use

- State the research question, baseline, system boundaries and scenario differences before substantial implementation.
- Keep a small, reproducible reference case.
- Progress from input checks to a representative small model, then to larger studies.
- Record expected runtime, memory/storage requirements and stopping conditions for substantial runs.
- Obtain authorization for large national solves, major batches or paid computation.
- Proceed autonomously within an already approved scope and budget; do not repeatedly request the same permission.
- Do not automatically launch a large Kenya optimization.
- Keep residential-demand modeling and other sector extensions outside active scope unless explicitly requested.
- Preserve failed and interrupted run evidence when useful for diagnosis.
- Never imply that a solver can resume unless the required checkpoint/recovery capability exists.

### Interrupted work and handovers

Before stopping or handing over substantial work, record:

- What is complete and where its outputs are.
- What remains unfinished.
- Current assumptions and unresolved decisions.
- Commands or processes still running.
- Validation performed and outstanding failures.
- The exact next useful step.

Do not leave the next session to reconstruct the project from chat history alone.

## Results, maps and scientific claims

Follow the documented shared map/results concept across Kenya, Somalia and later Saudi/GCC models.

- Inventory all outputs of the active model; do not limit the interface to a few headline metrics.
- Keep system-only results available in charts or tables.
- Distinguish saved inputs, solver outputs, derived results, external observations and illustrative examples.
- Display units, period, scenario revision and solution status.
- Keep administrative boundaries separate from electrical zones.
- Use full names or short 2–3 letter labels for small areas, with full-name lookup and no label leader lines.
- Plot precise asset locations only when justified by sourced coordinates.
- Show location confidence and preserve unmatched or region-only assets.
- Distinguish schematic model connections from surveyed transmission routes.
- Keep existing, planned and model-selected future assets distinct.

For comparisons and reporting:

- Compare compatible definitions, geographic coverage, periods and units.
- Recompute ratios and shares from their underlying quantities.
- Show absolute changes when percentage changes are undefined.
- Generate figures, tables and reported numbers from identified saved outputs.
- Independently recalculate important claims.
- Propagate corrections across the dashboard, documentation, figures and any manuscript.
- Mark older dependent outputs as stale when an input or method changes.
- Provide accessible tables/lists and readable map legends alongside visual displays.

## Honest run monitoring

Show:

- Queue wait and execution elapsed time separately.
- The actual current stage.
- Stage timings and last worker update.
- Configured solver time limit and remaining solver budget.
- An estimated finish window only when defensible.
- Actual completion time and final termination status.

Rules:

- Distinguish optimal, feasible, infeasible, time-limited, failed, cancelled and interrupted runs.
- An optimality gap is not completion percentage.
- Remaining solver budget is not time until results are ready.
- Preparation and export can extend total runtime beyond the solver limit.
- Say when there is insufficient history to estimate completion.
- Label stale status after a lost connection.
- Do not interpret a disconnected browser as proof that the solve failed.
- Describe interim solutions as provisional.
- Preserve worker independence from browser lifetime.

## Definition of completed work

Before marking a task complete, establish that:

- The requested outcome has been achieved.
- Inputs, methods, assumptions and outputs are traceable.
- Appropriate validation has been performed and reported.
- Affected documentation and downstream results are updated.
- Remaining uncertainty and limitations are visible.
- Existing relevant functionality and user work are preserved.
- Files and outputs are clearly located.
- The user has received a plain-language explanation of what changed, why it matters and what comes next.

If something remains incomplete, say exactly what and why. Distinguish implemented, tested, scientifically validated and ready for publication.
