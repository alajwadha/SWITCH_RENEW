# How to read the files

| File or family | One row represents | Keys / units | Interpretation |
|---|---|---|---|
| `processed/world_bank_observations.csv` | Indicator in one year | `indicator_code,year`; units in each row | Source-reported national statistic; nulls retained |
| `processed/world_bank_availability.csv` | Requested indicator | Code, available years, latest value, status | Distinguishes availability and API errors; latest is not necessarily recent |
| `processed/world_bank_indicator_metadata.csv` | Indicator definition | Code, source note and original organization | Read before modeling use |
| `processed/irena_somalia_electricity.csv` | Technology, metric, connection class and year | Country/area, Technology, Data Type, Grid connection, Year | MW capacity or GWh generation; parent categories overlap |
| `processed/nasa_power/*.csv` | Site timestamp | Site and UTC date/hour; six parameter columns | Gridded estimated weather/resource, not asset output |
| `processed/nasa_*_parameter_metadata.csv` | Parameter in a source response | Source ID, units, long name, time standard | Hourly and daily solar/precipitation units differ |
| `processed/nasa_*_summary.csv` | Parameter/site over requested window | Min, max, arithmetic mean, nonmissing count | Descriptive query-point statistics, not national means |
| `processed/resource_sampling_sites.csv` | Rounded query point | Latitude and longitude in degrees | Analyst-selected city approximation, not plant location |
| `processed/solar_country_workbook_cells.csv` | Source workbook cell | Sheet and cell address | Original headers and Somalia values, including source missing/error cells |
| `processed/solar_resource_summary.csv` | Long-term national solar statistic/month | Source sheet/cell, units | 2020 study; spatial percentiles are not future probability quantiles |
| `processed/gem_somalia_assets.csv` | GEM unit or phase | GEM unit ID, status, capacity, location accuracy | February2026 public distribution; threshold-limited coverage |
| `processed/geoboundaries_*_units.csv` | Administrative feature | Publisher IDs and names | Alternative administrative version; not electrical topology |
| `processed/fuel_prices_annotated.csv` | Market or publisher aggregate in a month | Location/month; source price fields and modeled prices | Preserve annotation flags; SOS/L as publisher labels |
| `research/power_facts.csv` and `statistics_facts.csv` | Source-located factual claim | Stable fact ID, value, unit, geography, period, evidence type | Some rows intentionally preserve conflicts or planning assumptions |
| `research/power_consumption_history.csv` | Utility consumption entry by year | Utility, year, source status and locator | Distinguish supplied data from report estimates |
| `research/resource_catalog.csv` | Candidate dataset/product | Source ID, source/download URLs, resolution, access and license | Some are metadata-only or restricted; access status is explicit |
| `research/global_cost_benchmarks.csv` | Global technology reference | Observation year, cost units and source locator | Not Somalia supplier quotes or approved model parameters |
| `research/fuel_reference_defaults.csv` | Global fuel default | NCV or combustion emission factor, original units | Not a Somalia assay; no implicit adoption |
| `processed/kenya_to_somalia_crosswalk.csv` | Kenya input file | Fields, available Somalia evidence, remaining need and priority | Schema checklist only; no copied parameters |
| `processed/priority_data_requests.csv` | Remaining evidence requirement | ID, priority, destination | Requests to prepare; none were sent to external organizations |
| `manifests/download_manifest.json` | Download request/snapshot | Source ID, URL/body, retrieval time, bytes, SHA-256 | Audits raw file identity; an HTTP200 API error is not valid data |
| `validation/*.json` | Check or dataset audit | Pass/failure details and scope | File/source checks do not imply a scientifically validated model |

## Missingness and evidence types

Blank numeric cells mean missing or inapplicable as specified by the source. Explicit zeros are preserved. Original errors such as workbook `#N/A` remain visible in the cell extract and are excluded from numerical summaries.

`source_reported`, official estimate, measured/reported utility data, modeled resource, forecast, target, planning assumption, global benchmark and conflicting/quarantined record are different categories. Read the `caveat` and `model_use` fields before choosing an input. Verification of a transcription does not turn a planning assumption into an observed value.

## Licenses

Each dataset retains its own license; this repository does not relicense third-party data. World Bank products retain their dataset-specific terms and original-provider restrictions. IRENASTAT uses IRENA noncommercial attribution terms unless a specific product overrides them. geoBoundaries ADM1 carries ODbL source conditions; other boundaries may differ. GEM and the national solar workbook retain their stated attribution terms. See source metadata and `research/resource_geospatial.md` for precise licenses. Full rights-unclear reports remain linked, not redistributed.
