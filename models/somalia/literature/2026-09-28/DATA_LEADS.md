# Data and reproducibility leads

Status as of 28 September 2026. **Metadata availability is not validation of data contents.** Public API file listings and checksums are saved in [linked_repositories.json](provenance/linked_repositories.json). No workbook macros or models were run.

## Existing model and transport repositories

| Source | Verified repository result | Reuse boundary |
|---|---|---|
| E05 OnSSET | [Somalia-1.0 reference](https://github.com/OnSSET/onsset/tree/Somalia-1.0) resolves through the Git tree API; 153 file entries, tree `bd5a27c267b231efb18b0eb964b7a3d17a80e4c7`. Branch-only lookup returned 404. | Code and generic/test inputs are visible. A complete identifiable Somalia scenario-input bundle was not established from the listing; inspect README, archives and dependencies before claiming reproducibility. |
| E18/E19 energy starter kit | Cited concept DOI [4725474](https://doi.org/10.5281/zenodo.4725474) resolves to [version 7540465](https://zenodo.org/records/7540465), dated 16 January 2023, 19 files, CC BY 4.0. | Includes parameter CSVs and scenario workbooks; later version must not be silently substituted for the 2021 paper’s inputs. Contents not audited. |
| TF018 transport starter kit | Cited concept DOI [7998431](https://doi.org/10.5281/zenodo.7998431) resolves to [version 10409827](https://zenodo.org/records/10409827), with `TSDK_Somalia.xlsx` and `Somalia.pdf`. | Country inclusion verified. Check cell provenance, missingness, extrapolation and regional proxies before use. |

## Measured, survey and operational leads

| Priority | Records | Data to locate | Why it matters / restriction |
|---|---|---|---|
| 1 | E17 / E05 | Original ESP billing, customer and collection files; SEAP/SDI metadata | Distinguish historical utility aggregates from household interviews and hourly demand. |
| 1 | PU01 / E07 | Hospital load series and station observations | Named historical measurements; request timestamps, units, quality flags and coverage before reuse. |
| 1 | COOK01/02/04/05/06/18 | SIHBS 2022 and SHDS 2020 questionnaires, codebooks, weights and analysis code | Reconcile common underlying observations rather than count repeated papers as replication. |
| 1 | PU10 | [Somalia WBES 2025 metadata/microdata](https://microdata.worldbank.org/catalog/8119) | Weighted firm analysis; formal-enterprise coverage and missingness matter. |
| 2 | E06 | Original [FAO-SWALIM](https://www.faoswalim.org/) station series and gap masks | Independent checks of resource estimates; reported gap filling affects uncertainty. |
| 2 | E03 | Hormuud telecom PV monitoring | Article explicitly identifies confidentiality; publication is not permission to redistribute data. |
| 2 | COOK14/15 | PROSCAL household, refill, subsidy and follow-up monitoring | Assess continued use after support ends. |
| 2 | PU04/07/08/09 | Corrected feasibility tables and facility/market assessment files | Resolve publication conflicts; distinguish installed systems from plans. |
| 2 | PU13/15 / E14 | Water-pump operations, dairy cold-chain records and enterprise loads | Link energy to useful output, maintenance and service continuity. |
| 2 | TF005/007/008/018 | Fuel-account assumptions and original transport observations | Reconcile sources and identify proxies before any calibration. |

Priorities describe the next evidence audit, not permission to contact data owners. No author, institution or advisor was contacted. Dataset ownership, access terms and geographic coverage remain part of each reuse decision.
