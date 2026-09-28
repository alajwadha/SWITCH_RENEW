# Collection and verification methods

Research cutoff: 28 September 2026. This is a source-preserving evidence collection, not a runnable Somalia SWITCH case or a solved model.

## What verification means here

1. Locate the source that owns the observation or dataset. Search snippets are discovery aids only.
2. Inspect the full source, including table headings, units, footnotes, publication date and observation period. The report research records include page/table locators; selected complex tables were also checked visually.
3. Save downloaded bytes unchanged with the exact request, retrieval time, byte count and SHA-256 digest. Report PDFs with uncertain redistribution rights stay in a local cache; publish citations and factual extracts.
4. Transform through the versioned scripts, retaining source identifiers and missing values. Check duplicates, country codes, timestamp coverage, units, source-to-CSV equality, elementary physical ranges and relevant component totals.
5. Record unresolved contradictions. A value being present in an official source does not establish that it is appropriate for calibration.

These checks verify provenance and transformation fidelity. They do not independently verify a utility meter, plant commissioning, site coordinates or the truth of every national estimate.

## Geographic and temporal scope

National API queries use the publisher's `SOM`/Somalia definition. Reports retain the source's own labels for federal Somalia, Somaliland, Puntland, regions and service areas. This collection takes no position on borders or political status. Administrative units are not electrical load zones.

geoBoundaries versions are retained as alternative mapping data: ADM1 has 18 features; ADM2 has 118. OCHA's separately catalogued 2025 metadata has 91 districts. Do not combine these without a documented crosswalk. No baseline model boundary, planning horizon or time-sampling design is chosen by acquiring these files.

## World Bank

`scripts/collect_data.py --only wdi` queries source 2, 1960–2025, and retains the full data and indicator-definition responses. The API's source update date differs from the observation year. `processed/world_bank_availability.csv` reports the latest **available** year; a latest value from 1982 or 2017 is not a current estimate.

The data table includes explicit missing rows; an empty value is missing, never zero. Availability distinguishes valid but empty series from API errors such as retired or invalid indicator identifiers. Four exploratory identifiers returned API errors and are preserved as failed discovery attempts, not evidence that Somalia lacks the quantity. Definitions are in `world_bank_indicator_metadata.csv`. Most API unit fields are blank, so documented title-based units are supplied. In particular, `IC.FRM.OUTG.ZS` is percentage of sales for affected firms, not percentage of firms. A reported zero in an enterprise survey is not evidence of zero outages or unmet demand.

## IRENA

The live API catalogue resolved to `Country_ELECSTAT_2026_H2_PXready.px`. The old H1 endpoint returned 404. The saved catalogue, dimension definitions, POST body and JSON-stat2 response identify this new vintage explicitly.

JSON-stat dimension order and category indices are used to decode the Cartesian product. Blank/null values remain missing. The 4,056-row table contains only 378 non-missing values: dimensional combinations are not all observations. Capacity is MW and generation GWh, as identified by `Data Type`. `All`, `On-grid` and `Off-grid` overlap; use one boundary consistently. Technology totals overlap their components. Do not sum a renewable subtotal again with solar and wind.

## NASA POWER

Ten analyst-selected, rounded city sampling coordinates are in `resource_sampling_sites.csv`. These are reproducible query points, not surveyed locations, national spatial averages or proposed generation sites. Each API result preserves the grid geometry, parameter metadata and underlying data-source information.

- Hourly: 2025-01-01 through 2025-12-31, UTC, exactly 8,760 timestamps per site.
- Daily: 2001-01-01 through 2025-12-31, UTC, exactly 9,131 dates per site, including leap days.
- Parameters: surface solar radiation, air temperature at 2 m, wind speed at 10 m and 50 m, relative humidity at 2 m and corrected precipitation.
- Missing sentinel `-999` is converted to a blank only in processed CSVs; raw bytes remain unchanged.

Solar radiation is `Wh/m^2` in the hourly response and `kW-hr/m^2/day` in the daily response. Summing hourly radiation and dividing by 1,000 gives kWh/m² over the selected hours. Daily solar values are already daily energy per area. Precipitation is mm/hour in hourly data and mm/day in daily data. Neither wind speed nor irradiance is an electrical capacity factor. Converting them requires a specified turbine/power curve or PV performance model, losses and validation. A wind-speed mean cannot be passed through a nonlinear turbine curve to recover mean generation.

POWER radiation and meteorology have different spatial resolutions and are satellite/reanalysis-based estimates. This collection does not turn them into measurements or high-resolution siting evidence. See the [NASA methodology](https://power.larc.nasa.gov/docs/methodology/) and [hourly API](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/).

## National solar workbook

The World Bank/ESMAP/Solargis 2020 workbook is downloaded unchanged. A read-only OOXML parser extracts the Somalia row and original column headings from all three relevant worksheets, retaining cell addresses. The statistics represent long-term modeled resource; the publication year is not the weather observation year. The workbook's older population, tariff and capacity context is not promoted to current evidence. Spatial percentiles describe variation across land, not interannual uncertainty or P90 project finance probabilities.

## Asset and fuel inventories

GEM's public Esri distribution explicitly states **February 2026**, although GEM's main website describes a newer September 2026 release. The downloaded nine-record subset retains that older vintage, project status, unit IDs and location accuracy. API count reconciliation checks download completeness within that distribution, not coverage of Somalia's many small generators. Do not sum it with the report inventories before resolving duplicate sites, phases and AC/DC ratings.

The World Bank diesel archive contains price-field, modeled, uncertainty/trust and interpolation information. Its market aggregate must not be counted as an additional physical market. See the dedicated fuel audit and research note for currency, unit and coverage. Retail diesel prices are not delivered generator fuel costs; a currency conversion, heating value, density, taxes/transport and procurement basis are needed before populating `fuel_cost.csv`.

## Kenya reference

All 26 local Kenya input files were inventoried with hashes, row counts and column names. This is a schema inspection. The `trans_county.csv` first line appears data-like and is recorded mechanically; the inventory does not certify that it has a normal header. Empty Kenya peak-demand and balancing-area files are not evidence that these parameters are unnecessary in Somalia.

No Kenya numerical assumptions were copied into Somalia. No residential-demand model, hydrogen, desalination, cross-border trade module or large solve was introduced. Their existence in a Kenya file or a source report does not authorize a Somalia extension.
