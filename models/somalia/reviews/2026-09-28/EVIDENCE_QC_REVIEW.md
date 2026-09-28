# Independent evidence and reproducibility review

Review date: 28 September 2026. Reviewer role: scientific-data and reproducibility auditor, independently delegated by the user. Baseline reviewed: commit `cf5da4ddf04082b6e1d6fb62ce269516d6a56a17`. Scope: the Somalia data snapshot, gap assessment, literature catalogue and the historical chat claims preserved in [CHAT_CLAIMS.md](CHAT_CLAIMS.md). A final spot-check also covered the newly drafted author/data-request register and corrected contribution records.

**Verdict:** the headline inventory counts and the tested raw-to-table transformations are supported. No numerical extraction error was found in the acquired API, solar-workbook, asset or fuel tables checked here. The literature needed a stronger warning about a newly identified internal calculation conflict in E06, a correction to PU01's availability wording, and an explicit PU16 author-order provenance note. These findings affect how published results and data-access leads should be reused; they do not justify changing raw source values or the research scope.

## Findings and required fixes

Severity describes the consequence of unqualified reuse: P1 = consequential numerical issue to resolve before adopting the affected result; P2 = material provenance or availability correction; P3 = documentation or verification-boundary clarification. A source inconsistency is not a finding that the repository transcription is wrong.

| ID / severity | File or record | Independent evidence | Required action and current disposition |
|---|---|---|---|
| QC-E01 / P1 before numerical reuse | Literature E06; `SOURCE_ISSUES.md`; electricity contribution | Batran et al., [primary article](https://doi.org/10.1016/j.heliyon.2024.e32500), Table 2 lists WT7 rated power as 1,500 kW. Table 11 lists Xumbo Weyne annual production 6.04 GWh and capacity factor 0.29. Equation 33 gives `1,500 kW × 8,760 h × 0.29 / 1,000,000 = 3.8106 GWh`. The discrepancy is far greater than rounding of a capacity factor to two decimals. The article's JATS table cells, rather than OCR, supplied these values. | Add the conflict and qualify turbine production/economic results pending author clarification and recomputation. Retain the original reported numbers and station-data provenance. The root agent has added this limitation and a corresponding-author request; the updated contribution was spot-checked. |
| QC-E02 / P2 | Literature PU01 `limitations` | The original catalogue said “raw series unavailable,” while its own availability field only established that no downloadable raw load series or HOMER project was identified. Neither unsuccessful discovery nor non-acquisition establishes nonavailability. | Use “raw series not obtained; public download not identified.” The updated contribution now does so. Contact row RQ01 correctly distinguishes a promising access lead from confirmed restricted data. |
| QC-E03 / P2 provenance | Literature PU16; bibliography provenance | The [author manuscript](https://eartharxiv.org/repository/object/14054/download/24632/) cover lists Kassa, Elema, Redding. The EarthArXiv landing metadata and saved Crossref metadata list Kassa, Redding, Elema. The catalogue follows the manuscript cover. This is a conflict between primary representations, not a demonstrated catalogue author-order error. | Preserve manuscript order and document both representations. Do not silently reorder the citation from Crossref. The conflict was reported to the root agent for the source-issues record. |
| QC-E04 / P3 | Validation claims; data/literature README and reproduction instructions | The ordinary Git checkout reproduced 542 data checks with zero failures. The saved 544 count includes two checks of the wind TIFF, intentionally supplied only in the release archive. The literature baseline reproduced 740 checks with zero failures, predominantly record-structure/bibliography checks plus selected arithmetic. | Preserve the documented optional-payload distinction and state the verification scope whenever reporting these counts. Do not describe 544/740 as independently validated scientific findings or paper-quality scores. Existing caveats substantially satisfy this requirement. |
| QC-E05 / P3 locator clarification; not a new error | Literature E06 power-density warning | Primary XML supports the caption `W/m²` versus heading/prose `kW/m²` discrepancy in Tables 5–7 **and** Tables 8–10. The original warning citing Tables 8–10 was therefore supported. | Broadening the locator to Tables 5–10 improves completeness. Do not characterize the original 8–10 locator as false. The updated E06 locator includes Tables 5–11. |

The E06 conflict is a transparent algebraic check on published quantities. It does not identify which source field or underlying model setting is wrong. No source value was “repaired” by the reviewer.

## Reproduction and transformation checks that passed

The following checks were executed against the baseline before integration edits. Validators wrote only to a temporary copy or to an in-memory capture; this reviewer did not regenerate the canonical source files.

| Check | Result | Boundary |
|---|---|---|
| Catalogue record counts | 73 records: electricity 18, cooking/biomass 19, transport/fuels/governance 17, productive uses 19 | Counts are publications/source records, not independent experiments or datasets. |
| Baseline inspection-depth counts | 4 complete short documents, 54 selected full-text inspections, 8 abstracts, 7 official summaries; one summary record is identity-only | Supports the historical chat's 58 full/selected, 14 other appraised, 1 identity-only split. Later access corrections may legitimately change the split. |
| Baseline literature hashes | All 80 files in `checksums.sha256` matched | Verifies byte integrity, not scientific accuracy. |
| Literature export rebuild | JSON, CSV, publication table, BibTeX, README and summary regenerated byte-for-byte in a temporary copy | Confirms the deterministic route from contribution records to these exports. |
| Literature validator | 740 passed, zero failed; 42 retrieved DOI-title matches and two documented Crossref exceptions | The two exceptions are PU01 and PU15. A Crossref 404 does not prove a publication or DOI is nonexistent. |
| Data validator | 542 passed, zero failed without the optional wind TIFF | Source/CSV equality for WDI and NASA, timestamps, missingness, hashes and elementary ranges; no field validation. |
| Data file inventory | 370 ordinary Git files present; all 368 locally present payloads covered by `publication_files.csv` matched their hashes and sizes | The 369-row inventory includes one release-only TIFF; inventory and archive-manifest files are deliberately outside the inventory's self-check. No unexplained missing payload or mismatch was found. |
| IRENA independent decoding | All 4,056 output rows' dimension labels and values matched the saved JSON-stat source using an independent stride/index calculation | 378 nonmissing values; overlapping grid/technology totals remain unsuitable for naive summation. |
| GEM attribute fidelity | Every original attribute in the nine output records matched the saved API response | Completeness within the queried distribution is not completeness of Somalia's operating assets. |
| Solar workbook extraction | All retained extracted cells matched the saved OOXML workbook; selected source headers supported the GHI and practical PV-output units | Long-term modeled resource and spatial statistics remain distinct from a weather-year observation or financial exceedance probability. |
| Fuel table fidelity and audit | All original source columns in 10,856 annotated rows matched the raw archive; market/aggregate and source-price annotations reconciled; zero fuel structural errors | Latest nonblank source-price field was June 2026, while modeled estimates extend through August. Existing labels preserve that difference; these are not 10,856 newly measured prices. |
| Utility-history classification | 179 cells comprise 143 numeric entries and 36 missing entries, years 2015–2024; numeric rows retain `reported_history_method_unresolved` | These are annual reported histories with unresolved measurement/estimation methods, not hourly metered demand. |

The acquired data headlines—1,764 nonmissing WDI values across 44 available indicators, 87,600 hourly NASA timestamps, 91,310 daily timestamps and 1,073,460 requested NASA parameter values—were reproduced by the offline validator. The saved unit mappings and selected resource headers were also inspected. No silent Kenya numerical-parameter transfer was found in the reviewed collection scripts.

## Contact-register sanity check

The draft [author/data-request register](../../literature/2026-09-28/author_data_requests.json) contained 13 request leads and 17 named or institutional contacts when inspected. Its purpose is to help the user obtain data for existing research. It does not alter the research question, implement a new sector or authorize outreach by an agent.

The availability taxonomy is appropriate and should remain visible in the readable export:

- **Explicitly confidential:** E03/Hormuud monitoring. Permission or a shareable aggregate must come from the authors/data owner.
- **Explicitly available on request:** E06. The primary XML states this; Mohamed Jama's correspondence address is printed in the same document.
- **Restricted request possible:** PU16. The manuscript explicitly allows possible anonymized access subject to ethics/confidentiality restrictions. Kassa's printed correspondence is a professional contact even though it uses a consumer email provider.
- **Not obtained or not located:** PU01/E07, PROSCAL and several operational inputs. These labels do not assert that no public file exists or that the authors must possess every requested variable.
- **Partly public:** OnSSET code is public; missing country-input/utility files remain a separate question. SIHBS has an official access route; the paper-specific recoding, sample decisions and code are the replication request.

Primary cached documents independently supported ten listed correspondence addresses across RQ02, RQ03, RQ04, RQ05, RQ07, RQ09 and RQ13. This was a bounded spot-check, not a second verification of all 17 contacts. Institution/project mailboxes, coauthor referral routes and publication-era addresses are correctly distinguished from confirmed data custodians. Deliverability, willingness to share and the quality of unseen raw data remain untested.

The requested variables are generally phrased appropriately as files or fields to ask for, with conditional wording where existence is uncertain. In particular, organizational fisheries questionnaires are not metered refrigeration demand, qualitative water-pumping interviews are not pump-efficiency measurements, and a hospital's historical load cannot stand in for national demand. Those limitations help the user make useful requests without changing the current research scope.

## Limits and final integration requirements

This audit independently reran the available integrity/rebuild checks and inspected selected primary-source content. It did not reproduce every paper, re-estimate surveys, inspect every unshared dataset, run an energy optimization, verify inbox delivery or contact any author. The wind raster was not re-downloaded or re-decoded, and the GitHub release binary was not re-fetched during this audit. Its absence from ordinary Git is expected and documented. Failed live opens of EarthArXiv/PMC produced access challenges; cached primary manuscript/JATS sources supplied the specific checks described above.

Existing E11, COOK12 and other source-conflict flags were treated as previously recorded limitations, not newly discovered findings. The historical gap response's hourly-load, asset, network and operating-cost priorities are consistent with the data inventory, but they remain priorities for the existing research, not instructions to redesign it.

Before publication of the integrated correction, the root agent should rebuild the changed catalogue/contact exports, rerun their scoped validators and update hashes. The baseline reproduction counts in this report are historical audit results and should not be substituted for the final post-edit verification. Raw datasets and existing model configuration should remain preserved because this audit found no verified extraction bug requiring their alteration.
