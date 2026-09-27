# Research and collaboration workflow

**Status:** approved by the user on 27 September 2026.

This guide is a required companion to the [repository instructions](../AGENTS.md). It contains the detailed live-explanation, documentation and advisor-consultation rules. Somalia-specific requirements are in [models/somalia/AGENTS.md](../models/somalia/AGENTS.md); optional ideas are in the [research backlog](RESEARCH_BACKLOG.md).

## Explain the work while doing it

Explain every substantive research, data-processing, modeling and validation step during execution where possible—not only in the final response.

For each step, cover:

| Part | What to explain |
|---|---|
| **Action** | What I am about to do. |
| **Purpose** | Which question this answers and why it is needed. |
| **Inputs** | Which data, sources, units and assumptions it uses. |
| **Method** | The formula, transformation or procedure. |
| **Consequences** | What this affects later in the model or its interpretation. |
| **Outcome** | What actually happened, including unexpected findings. |
| **Check** | How the result was checked and what remains uncertain. |
| **Next step** | What follows and why. |

Use short explanations rather than eight long headings for every action.

For calculations, show the inputs, formula, relevant intermediate quantities, units, result and interpretation. Use a small numerical example when it improves understanding.

For example:

> "I'm estimating annual electricity demand from population and electricity use per person. This gives the energy requirement that generation must meet. It will affect capacity and storage decisions, but it does not establish peak demand or reliable access."

Additional rules:

- Do not compress unexplained transformations into statements such as "cleaned the data" or "processed the results."
- Keep a numbered work log preserving the full sequence of meaningful steps.
- Describe repeated operations once, then record the datasets or items covered, results and exceptions.
- The work log supplements live explanations; it does not replace them.
- Explain uninterrupted tool operations before starting, then describe their outcomes afterward.
- During long operations, report actual stages and useful progress. Do not invent completion percentages.
- Continue routine authorized work without asking for confirmation after every explanation.

## Continuous documentation

A meaningful change to data, assumptions, equations, methods or conclusions is incomplete until the relevant documentation is updated.

Maintain clear authoritative records for:

| Record | Purpose |
|---|---|
| Documentation index | Find the current explanation of each component. |
| Project status | Separate planned, implemented, tested and validated work. |
| Source register | Trace data and factual claims. |
| Assumption register | Explain values, proxies, uncertainty and status. |
| Decision log | Preserve consequential choices, alternatives and reasons. |
| Methodology notes | Explain equations and processing steps. |
| Work log | Preserve the sequence of meaningful actions and findings. |
| Reproduction guide | Rebuild inputs, outputs and figures. |
| Limitations and open questions | Prevent unresolved issues from disappearing. |

Further rules:

- Give each topic one authoritative location and link to it.
- Date and mark superseded material, with a link to its replacement.
- Keep historical evidence without presenting it as current guidance.
- Explain important scripts through purpose, inputs, outputs, decision rules, sources and limitations.
- Update documentation in the same change set as the corresponding work.
- Write commit messages explaining what changed and why.
- Check documentation links and important reported values for drift.
- Record failed approaches when they explain a methodological choice or prevent repeated mistakes.

## When to consult Dan Kammen

Prepare a focused consultation when his scientific judgment could materially change the study:

1. **Research framing:** the question, contribution and policy relevance.
2. **Model design:** consequential boundaries, resolution, technologies or scenario choices.
3. **Evidence gaps:** important proxies, conflicting sources or uncertain assumptions.
4. **Interpretation:** surprising findings that remain after technical checks.
5. **Milestones:** the validated baseline, major extensions and publication framing.

Before consulting him, prepare:

- The decision needed.
- Relevant evidence and unresolved uncertainty.
- Viable options and trade-offs.
- Your own recommendation.
- What changes depending on his answer.

Additional rules:

- Do the preparatory research first.
- Do not send routine coding, formatting or readily resolvable factual questions to Dan.
- Continue independent work while a decision is pending.
- Identify exactly which work depends on his answer.
- Prepare questions or draft messages for the user.
- Contact Dan only when explicitly instructed.
- Record his actual feedback, date and resulting decision. Do not infer his approval.

The first proposed checkpoint is a short Somalia research-question brief after the initial data review and before committing to a detailed model.

## Adoption record

On 27 September 2026, the user approved the combined research and collaboration instructions after reviewing the shared rules, Somalia additions, explanation requirements, advisor checkpoints and ideas backlog. This replaces the earlier separate chat drafts. It adopts working instructions and creates the Somalia documentation folder; it does not start a solve or authorize backlog implementation.

The documentation and research-integrity practices were adapted from the user's EU hydrogen repository, then revised through this SWITCH discussion. Source snapshot:

- [Documentation conventions](https://github.com/alajwadha/eu-hydrogen-buildings/blob/de08030b06cfa64e7c569b9881e76a35873687a1/DOCUMENTATION.md).
- [Assumptions and citation audit](https://github.com/alajwadha/eu-hydrogen-buildings/blob/de08030b06cfa64e7c569b9881e76a35873687a1/literature/assumptions_register.md).
- [Research integrity guidance](https://github.com/alajwadha/eu-hydrogen-buildings/blob/de08030b06cfa64e7c569b9881e76a35873687a1/.claude/skills/manuscript-integrity/SKILL.md).

These are provenance references, not additional automatically adopted instructions or EU modeling assumptions. The approved SWITCH rules and the latest explicit user decisions govern this project.
