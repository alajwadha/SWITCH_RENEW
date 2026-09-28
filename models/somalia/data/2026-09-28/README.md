# Somalia energy evidence and data

**Research snapshot: 28 September 2026.** Data collection and source checks are complete for the files listed here. This is a research evidence pack; a calibrated, runnable Somalia SWITCH model still needs hourly utility loads, reconciled operational assets and network/financing decisions.

[Download the complete data archive, including the wind raster](https://github.com/alajwadha/SWITCH_RENEW/releases/tag/somalia-data-2026-09-28). Smaller raw datasets, CSVs, scripts and documentation are stored directly in this folder. Rights-unclear full reports are linked with provenance, not redistributed.

## Collected data

| Data | Coverage and size | Evidence and limitation | Files |
|---|---|---|---|
| Electricity access, economy, population, land and infrastructure | 1,764 nonmissing values across 44 available WDI indicators; histories span 1960–2025 where available | Source-reported/estimated; each indicator has its own latest year; 7 valid series empty and 4 exploratory API identifiers rejected | [Availability](processed/world_bank_availability.csv), [full time series](processed/world_bank_observations.csv), [definitions](processed/world_bank_indicator_metadata.csv) |
| Electricity capacity and generation | 378 nonmissing IRENA observations in 4,056 dimensional rows; 2000–2025 | Current 2026 H2 release; MW/GWh separated; grid classes and technology subtotals overlap | [IRENA series](processed/irena_somalia_electricity.csv) |
| Power sector, utility, tariff and project evidence | 100 source-located records | Existing, estimated, planned, contracted and commissioned capacity separated | [Facts](research/power_facts.csv), [analysis](research/power_evidence.md) |
| Utility consumption histories | 179 cells, including 143 numeric values and 36 missing entries | Reported histories and estimated service-area values retain their original classification; not verified hourly load | [Consumption](research/power_consumption_history.csv) |
| Somalia planning parameters | 190 source-located entries | Published candidate-technology assumptions, not measured costs/performance or adopted SWITCH inputs | [Plan assumptions](research/power_planning_assumptions.csv) |
| Diesel market prices | 10,856 location-month rows, Jan 2007–Aug 2026; 45 physical markets plus one aggregate | SOS/L publisher labels; 2,073 source-price fields versus 10,856 modeled close estimates | [Annotated prices](processed/fuel_prices_annotated.csv), [audit](validation/fuel_archive_audit.json) |
| Hourly solar and weather | 87,600 timestamps at 10 locations in 2025, six variables | UTC, 8,760 hours/site; gridded estimates, not plant output | [Site series](processed/nasa_power), [sites](processed/resource_sampling_sites.csv) |
| Long weather history | 91,310 daily timestamps at 10 locations, 2001–2025 | Six variables; useful for variability checks, not subhourly dispatch | [Daily summaries](processed/nasa_daily_summary.csv), [metadata](processed/nasa_daily_parameter_metadata.csv) |
| National solar resource | 31 long-term resource/seasonality/monthly/spatial statistics | World Bank/ESMAP/Solargis 2020 study, not a 2020 weather observation | [Summary](processed/solar_resource_summary.csv), [original cell extract](processed/solar_country_workbook_cells.csv) |
| National wind resource | 54.5 MB GWA4 raster, 100 m height; 19,053,180 finite cells | Approximately 250 m product; includes offshore; 2008–2017 reference climate; no national land mean inferred | [Audit](raw/global_wind_atlas/som_wind-speed_100m_gwa4_20260928.audit.json), [retrieve](raw/global_wind_atlas/retrieve_gwa.py), full TIFF in release |
| Power asset inventory | 9 GEM unit/phase records | February 2026 public distribution; small-generator coverage incomplete and statuses need current verification | [Assets](processed/gem_somalia_assets.csv) |
| Administrative geography | Country, 18 ADM1 and 118 ADM2 geometries and names | geoBoundaries version differs from OCHA 91-district metadata; these are not electricity zones | [Geometry and metadata](raw/geoboundaries), [discussion](research/resource_geospatial.md) |
| Wider energy/economy/policy evidence | 40 source-located records | SNBS, AFREC, World Bank, IFC, NDC; conflicting records retained and quarantined | [Facts](research/statistics_facts.csv), [analysis](research/statistics_fuels.md) |
| Further spatial and environmental sources | 30 catalogued products | Population, roads, land cover, floods, drought, hydrology and constraints; many are metadata-only or registration-limited | [Dataset catalogue](research/resource_catalog.csv) |
| Global technology/fuel references | 8 IRENA cost benchmarks and 2 IPCC defaults | Separate from Somalia evidence; no implicit proxy adoption | [Costs](research/global_cost_benchmarks.csv), [fuel defaults](research/fuel_reference_defaults.csv) |
| Kenya-to-Somalia input map | All 26 Kenya input files inventoried | File/field checklist only; no Kenya numerical parameters transferred | [Crosswalk](processed/kenya_to_somalia_crosswalk.csv), [remaining requests](processed/priority_data_requests.csv) |

## Selected findings

- WDI electricity access: **54.4% in 2024**, with urban 73.4% and rural 24.4%. These are access statistics, not electricity consumption or reliability measures.
- IRENA 2025 renewable capacity: **49.46 MW**, comprising 45.91 MW solar PV and 3.55 MW onshore wind. Non-renewable capacity is reported as 300 MW. These national series do not establish a complete operating-unit list.
- Long-term national GHI: **6.0283 kWh/m²/day**; practical PV output Level 1: **4.7617 kWh/kWp/day** in the 2020 ESMAP study. Both are modeled resource estimates.
- The March 2026 restructuring paper removes the earlier 132 kV scope from its proposal; subsequent approval was not established. A contract or national planning option is not proof of commissioning.

## Quality and remaining limits

The [validation report](validation/validation_report.json) records **544 passed checks and 0 failures** for its stated scope. The NASA tables contain 1,073,460 parameter values with no missing source values in the requested windows. Fuel structural validation found no errors, while its observation-count metadata disagreement remains explicit. The wind raster was decoded and its dimensions, CRS, missing pixels and finite range checked separately.

**Source contradictions remain unresolved and visible.** These include incompatible official generation mixes, energy-balance arithmetic, fuel units, emissions baselines, geographic versions and data vintages. See the [conflict register](CONFLICTS.md). Passing file checks does not validate those disputed quantities.

## Navigation and reproduction

- [Source register](manifests/source_register.csv) and [download requests/checksums](manifests/download_manifest.json)
- [Methods](METHODS.md), [data dictionary](DATA_DICTIONARY.md), [reproduction commands](REPRODUCE.md)
- [Assumptions and decisions](ASSUMPTIONS_AND_DECISIONS.md), [work log](WORK_LOG.md)
- [Prepared advisor checkpoint](ADVISOR_BRIEF.md); no advisor or data-provider message was sent

No model run, residential-demand extension or Kenya parameter transfer was performed. Existing project work was preserved. Dataset-specific licenses apply; this collection does not relicense third-party material.
