# Somalia statistics, fuels, productive uses and climate policy

Research date: **28 September 2026**. Scope: evidence discovery and verification for Somalia electricity planning. No residential-demand model, household microdata collection, water-demand extension or optimization was performed. Geographic labels follow each publisher; a national headline is not assumed to represent every region or electricity provider equally.

**The strongest immediately usable material is the frozen World Bank market fuel-price panel and current SNBS national accounts. Several official energy tables contain consequential inconsistencies and must remain outside a model baseline.** A number can be verified as printed without being validated for the proposed modeling use.

## Deliverables and status

| Material | Coverage | Verification | Appropriate use |
|---|---|---|---|
| `statistics_facts.csv` | 40 traceable records: macroeconomy, historical fuel imports, energy balances, NDC targets, prices, water technical ranges and statistical capacity | Opened original sources; exact source locators; important PDF tables rendered and inspected | Evidence inventory, with per-record caveats |
| World Bank RTEP archive, version 2026-08-24 | January 2007-August 2026; 45 named markets plus the publisher's aggregate; 10,856 rows | Frozen ZIP and SHA-256; matched metadata; unique keys and monthly panel checked | Spatial and historical fuel-price sensitivity, after distinguishing modeled and source fields |
| `fuel_audit.py` | Standard-library audit and optional annotated export | Executed successfully against both frozen archives | Reproducible structural validation; preserves raw values |
| `global_cost_benchmarks.csv` | Seven global generation technology benchmarks and one four-hour battery benchmark, 2025 USD | Figure S1 and battery narrative visually checked against IRENA original; reference manifest retained | International comparison/proxy evidence; no Somalia cost assumptions adopted |
| Restricted/unclear-license reports | AFREC, NDC, SNBS and IFC reports | Inspected locally; original URLs, dates and hashes below | Link and metadata retention; no full-report redistribution assumed |

## Selected evidence

| Indicator | Value | Observation / target period | Status and source |
|---|---:|---|---|
| GDP, current prices | USD 13,234.49 million | 2025 | SNBS national-accounts estimate, 2026 release; [official table](https://nbs.gov.so/somalia-gross-domestic-product-gdp-2025/) |
| Real GDP growth | 3.1% | 2025 | Same release; 2022 constant-price basis; [SNBS](https://nbs.gov.so/somalia-gross-domestic-product-gdp-2025/) |
| Imports of goods and services | USD 9,884.17 million | 2025 | Economy-wide import value, not fuel volume; [SNBS](https://nbs.gov.so/somalia-gross-domestic-product-gdp-2025/) |
| Gas/diesel oil imports | 134 ktoe | 2020 | Historical national figure, Table 4.6; [SNBS Abstract](https://nbs.gov.so/wp-content/uploads/2025/03/Statistical-Abstract-2024.pdf) |
| Petroleum products imported | 246 ktoe | 2020 | Sum of six listed product types; same table; [SNBS Abstract](https://nbs.gov.so/wp-content/uploads/2025/03/Statistical-Abstract-2024.pdf) |
| Oil-product imports | 248.64 ktoe | 2023 | AFREC reported value; energy-balance conflicts unresolved; [AFREC p104](https://au-afrec.org/sites/default/files/2026-03/Energy%20Balance%202025%20%28EN%29.pdf) |
| Modeled diesel close: Baidoa | 40,559.30 SOS/L | August 2026 | Modeled estimate; no source-price field for that month; [World Bank archive](https://microdata.worldbank.org/catalog/6130/download/359961) |
| Modeled diesel close: Bossaso | 46,717.90 SOS/L | August 2026 | Same distinction; [World Bank archive](https://microdata.worldbank.org/catalog/6130/download/359961) |
| Modeled diesel close: Kismayo | 52,974.64 SOS/L | August 2026 | Same distinction; [World Bank archive](https://microdata.worldbank.org/catalog/6130/download/359961) |
| Economy-wide NDC reduction | 34% below BAU | 2035 target | Official policy ambition; 5% unconditional and 29% conditional; numerical caveats below; [updated NDC](https://unfccc.int/sites/default/files/2025-09/Somalia%20NDC%203.0_Official_2025.pdf) |
| Energy-sector NDC reduction | 3.24 MtCO2e | 2035 target | Narrative target; includes uses beyond electric power; [NDC p20](https://unfccc.int/sites/default/files/2025-09/Somalia%20NDC%203.0_Official_2025.pdf) |
| Solar pumping system cost | USD 20,000-30,000/system | 2021 report | Generic assessment range, not a current quote or USD/kW; [World Bank p12](https://documents1.worldbank.org/curated/en/099615012012129914/pdf/P1749940c70d5d09008a3203ad9eeb97d1a.pdf) |

`ktoe` means thousand tonnes of oil equivalent: an **energy** unit, not physical kilotonnes of fuel. `SOS/L` is the publisher's Somali-shilling price label per litre; no exchange-rate conversion has been made.

## World Bank fuel archive: verified meaning and audit

Catalogue: [SOM_2023_RTEP_v01_M](https://microdata.worldbank.org/catalog/6130). Version: **2026-08-24**, catalogue modified 27 August 2026. The catalogue describes a mixture of source prices and machine-learning completion, with modeled open/high/low/close price paths. These ranges are not statistical confidence intervals. [Catalogue methods and coverage](https://microdata.worldbank.org/catalog/6130).

The [matching details archive](https://microdata.worldbank.org/catalog/6130/download/359963) identifies diesel as **1 L** and the currency as **SOS**. The data CSV uses the same currency throughout. This verifies the published unit, not the underlying conversion of each local market quote. In particular, check local-currency treatment before connecting Somaliland market rows to other price sources.

The audit found:

- 236 monthly dates, 10,856 unique location-month rows and 20 source columns.
- 45 physical market identifiers, plus `gid_som_national_average`, which is a publisher aggregate with no coordinates. Exclude that row from market counts and spatial analyses.
- 2,073 nonblank `fuel_diesel` cells, of which 2,054 belong to physical markets. The last such date is June 2026. These are labeled **source-price fields present**, not independently verified survey observations.
- 10,856 nonblank `c_fuel_diesel` modeled estimates. A zero `spatially_interpolated` flag does not establish that a row is free of temporal imputation.
- No duplicate keys, invalid monthly dates, non-positive price values or modeled closes outside their low/high range.
- Metadata reports **1,352 underlying diesel observations**, whereas the CSV and [variable metadata](https://microdata.worldbank.org/catalog/6130/variable/SOM_2023_RTEP_MKT/V013?name=fuel_diesel) have 2,073 valid source-price fields. Preserve both counts; do not interpret the number of nonblank cells as a count of independent primary observations.

Reproduce from the `somalia-data` root (or equivalent repository data directory):

```text
python research/fuel_audit.py --archive raw/world_bank_fuel/SOM_RTEP_mkt_2007_2026-08-24.zip --metadata-archive raw/world_bank_fuel/SOM_RTP_details_mkt_2007_2026-08-24.zip --json-out derived/fuel_archive_audit.json --annotated-out derived/fuel_prices_annotated.csv
```

The script does not average markets, change source currency labels, fill source-price gaps, or estimate generator fuel costs. Converting these market prices into SWITCH fuel costs requires a documented delivery boundary, verified exchange rate, physical fuel specifications and generator heat rate. None has been assumed.

## Quarantined figures and reconciliation decisions

| Issue | Verified source evidence | Decision |
|---|---|---|
| SNBS generation mix conflicts with Somalia's documented power system | Abstract 2024 Table 4.5, printed p43/PDF p56: geothermal 43.6%, hydro 36.4%, fossil fuels 6.5%; visually verified | Do not use. This resembles another country's mix, but its actual origin has not been established. Seek the originating AFREC country/table and SNBS correction. Adjacent export/production-share charts also need review. |
| Mogadishu import unit is unresolved | Table 4.7, p45/PDF p58 has no unit header; p44 calls the 2021-2023 gas-oil total of 449,456 `ktoe` while also referring to kilotons | Preserve the printed numbers only in this conflict note, not as model fuel volumes. Do not silently relabel them tonnes. Table 4.6's explicit ktoe series is a separate historical record. |
| AFREC electricity transformation is physically inconsistent | 2023 balance p104 lists oil input 37.43 ktoe and solar input 15.19 ktoe but electricity output 107.70 ktoe | Inputs sum to 52.62 ktoe; reported output/input is about 2.05. Do not use these electricity totals for calibration. The 26.23-ktoe final-consumption entry is retained only as a conflicting reported value. |
| AFREC consumption chart and table differ | p103 chart gives commercial/public and agriculture electricity shares 8.9%/2.1%; p104 table gives 1.72 and 0.43 out of 26.23 ktoe, about 6.6%/1.6% | Do not combine chart percentages with table totals. Do not repair or average them. |
| Updated NDC baseline and target definitions disagree | p8/PDF p10 gives 54.3 MtCO2e in 2024; p17/PDF p19 gives 53.4. Main target says BAU; annex p40/PDF p42 says base year | Retain the published 34% headline and conditional split as policy context. Do not derive a power-only carbon cap. The 29.5/84.9 reduction is about 34.75%, so the stated percentage is not exactly reproducible from those rounded values. |
| SNBS fuel shock percentage fails arithmetic | March 2026 brief pp2-3 reports approximately USD 0.60 to 1.50/L and also 108% | Those levels imply 150%, not 108%. Retain approximate source levels; quarantine the percentage. Fuel grade and import/retail boundary are insufficiently specified for generator costs. |
| Fuel metadata observation counts differ | 1,352 observations in details versus 2,073 nonblank source-price cells | Treat this as a metadata/definition issue, not missing data to fill. The reproducible audit records it. |

Sources: [SNBS Abstract](https://nbs.gov.so/wp-content/uploads/2025/03/Statistical-Abstract-2024.pdf), [AFREC balance](https://au-afrec.org/sites/default/files/2026-03/Energy%20Balance%202025%20%28EN%29.pdf), [NDC](https://unfccc.int/sites/default/files/2025-09/Somalia%20NDC%203.0_Official_2025.pdf), [SNBS inflation brief](https://nbs.gov.so/wp-content/uploads/2026/04/Somalias-Inflation-Outlook.pdf), [World Bank details](https://microdata.worldbank.org/catalog/6130/download/359963).

The 2026 SNBS GDP release is selected for the macroeconomic records because it is the more recent domestic expenditure-account release. It should be kept separate from IMF/WDI vintages. It uses a 2022 base year and a population path extrapolated from PESS 2014 at 2.8% annually. Therefore, its GDP-per-capita denominator is not automatically compatible with a UN/WDI population series. [SNBS methodology, report p1/PDF p6](https://nbs.gov.so/wp-content/uploads/2026/06/Somalia-GDP-2025.pdf).

## Productive-use leads and gaps

The groundwater assessment supplies generic borehole ranges of 50-400 m depth and 3-35 m3/hour output. Depth is not the total pumping head, and neither value establishes annual pumping electricity. Site-specific water volumes, dynamic head, efficiency, operating hours and seasonal availability remain necessary. Desalination and detailed water-demand modeling remain separate proposals. [World Bank assessment pp11-12](https://documents1.worldbank.org/curated/en/099615012012129914/pdf/P1749940c70d5d09008a3203ad9eeb97d1a.pdf).

The IFC diagnostic identifies insufficient cold-chain infrastructure and landing facilities as fisheries constraints (printed p19/PDF p41). This supports investigating productive-use loads, but supplies no verified hourly cold-storage load series for a Somalia baseline. Keep industry, fisheries refrigeration, public facilities and irrigation as data-request categories until measured loads and operating schedules are available. [IFC Country Private Sector Diagnostic, June 2024](https://www.ifc.org/content/dam/ifc/doc/2024/somalia-country-private-sector-diagnostic-en.pdf).

AFREC's July 2025 diagnostic reports a functioning electricity-focused NEIS since late 2024, four full-time MoEWR energy-data/planning staff, and assumption-based annual biomass growth between survey benchmarks. It also describes limited end-use information and incomplete public dissemination. These findings support direct requests for annual balances, fuel volume units and utility reporting coverage; they do not validate the inconsistent published tables. [AFREC diagnostic pp8,12,21-25](https://au-afrec.org/sites/default/files/2026-04/DiagActionPlan-somalia.pdf).

## IEA discovery and access limitation

The public [IEA Somalia overview](https://www.iea.org/countries/somalia), [electricity page](https://www.iea.org/countries/somalia/electricity) and [Energy Statistics Data Browser with Somalia selected](https://www.iea.org/data-and-statistics/data-tools/energy-statistics-data-browser?country=SOM) were inspected. The browser page marks its content CC BY 4.0, but the public reader returned no reproducible Somalia numerical table in this run. This is a retrieval limitation, not proof that IEA has no Somalia data. No IEA numerical estimate was added from snippets or inferred from empty charts.

The [IEA terms](https://www.iea.org/terms) distinguish open text/figures from standalone databases and other exceptions; full World Energy Balances and related products may have separate access and reuse conditions. No account purchase, paywall bypass or bulk restricted-data extraction was attempted. Obtain the specific product's license and underlying Somalia series before treating IEA bulk data as GitHub-redistributable.

## Global cost reference, kept separate from Somalia inputs

The eight rows in `global_cost_benchmarks.csv` are **global 2025 benchmarks**, visually verified in the [IRENA 2026 executive summary](https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2026/Jul/IRENA_TEC_RPGC_2025_Executive_summary_2026.pdf). Figure S1 on PDF p6 reports generation costs, total installed costs and capacity factors; p8 reports a four-hour utility-scale battery installed cost of USD140/kWh. `global_cost_benchmarks.source.json` records source metadata, checksum, license and inspected pages.

These figures are not Somalia vendor quotations or adopted SWITCH build costs. In particular, global capacity factors cannot replace Somalia hourly resource profiles, LCOE cannot replace capital costs, and the battery's system cost per kWh must not be added to a separately assumed full power-component cost. Any transfer requires a documented proxy decision, local scope/financing/logistics adjustments and sensitivity analysis.

## Source preservation and licenses

Full report PDFs below were downloaded to temporary local storage for verification. Repository preservation here is factual extraction, citation and checksums. These checksums identify the exact inspected bytes; they do not imply an open redistribution license. Retrieval date for all entries: **2026-09-28**.

| Source | Publication / vintage | Original URL | Bytes | SHA-256 | Redistribution decision |
|---|---|---|---:|---|---|
| SNBS GDP 2025 | June 2026 upload; PDF metadata June 2026; exact release day not independently established | [PDF](https://nbs.gov.so/wp-content/uploads/2026/06/Somalia-GDP-2025.pdf) | 13589609 | `d3ff43ae7fe878d2215fa612486ca5c518ac8754f3a995739231c3a2ce13a743` | Open whole-document license not verified; link and metadata only |
| SNBS Statistical Abstract 2024 | November 2024 on cover; March 2025 URL | [PDF](https://nbs.gov.so/wp-content/uploads/2025/03/Statistical-Abstract-2024.pdf) | 8625917 | `874035fcad83794d0567d7a94bedb41f91622323bf3d71b6f16d354bddb85cc6` | Open whole-document license not verified; link and metadata only |
| Updated Somalia NDC 3.0 | Submitted 8 September 2025; updated version | [PDF](https://unfccc.int/sites/default/files/2025-09/Somalia%20NDC%203.0_Official_2025.pdf) | 18679184 | `38f99173365cedfaa0d11ce0fd6d6561e27f35941d46dbf0b79cc5f9253679e7` | Public official submission; no explicit open license verified; link and metadata only |
| AFREC Africa Energy Balances 2025 | 2025 edition; March 2026 upload; 2023 balance | [PDF](https://au-afrec.org/sites/default/files/2026-03/Energy%20Balance%202025%20%28EN%29.pdf) | 2343066 | `89c0c5df12fe5c3d4e015104587f536c7febd3210dbfeb18b11091f8b29f9efd` | Copyright page requires written permission for reproduction/copy/transmission; quotes allowed with acknowledgment. No full PDF in GitHub |
| AFREC Somalia NEIS diagnostic | July 2025 report; April 2026 upload | [PDF](https://au-afrec.org/sites/default/files/2026-04/DiagActionPlan-somalia.pdf) | 13704178 | `07a28c797043b3a63af893229fc791a0f2003d8d39167fe76e70b6d5da6f94e9` | Copyright AFREC 2025, all rights reserved; link and metadata only |
| SNBS Inflation Outlook | March 2026 brief; April 2026 uploaded file | [PDF](https://nbs.gov.so/wp-content/uploads/2026/04/Somalias-Inflation-Outlook.pdf) | 506896 | `4b75b09366b6b2487c466e8c9854229312040b0fe518314255e0697d09e86727` | Open whole-document license not verified; link and metadata only |
| World Bank Groundwater Assessment | 2021 | [PDF](https://documents1.worldbank.org/curated/en/099615012012129914/pdf/P1749940c70d5d09008a3203ad9eeb97d1a.pdf) | 4529203 | `3c0bdd1be31fa2f19e8e90c47f51fc198b555ec9d199f4307b64cdf9bb38b56d` | p2 permits noncommercial reproduction with full attribution; retained as link/metadata here |
| IFC Somalia Private Sector Diagnostic | June 2024 | [PDF](https://www.ifc.org/content/dam/ifc/doc/2024/somalia-country-private-sector-diagnostic-en.pdf) | 2216099 | `6ca566d19218550ca2104e6826308fee0fd48acb9c9f2bd23ef5a048d95c7a3b` | IFC copyright/all rights reserved on p2; link and metadata only |
| IRENA Renewable Power Generation Costs 2025, executive summary | July 2026; 2025 benchmarks | [PDF](https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2026/Jul/IRENA_TEC_RPGC_2025_Executive_summary_2026.pdf) | 2737306 | `2046b4146b69197a6d62f769a50fd76b87c31f558fbc8b8c4f621339e8b46905` | p2 allows reuse with acknowledgment; third-party materials excepted. Link/metadata retained here |

The two World Bank RTEP ZIPs are retained under the catalogue's open-data attribution terms, with `.meta.json` provenance sidecars. The [terms page](https://microdata.worldbank.org/catalog/6130/get-microdata) requires attribution and forbids implying World Bank endorsement; third-party restrictions, if any, remain applicable. The source-price catalogue describes these estimates as open data.

## Work log and next evidence priorities

1. Read the approved repository research/scope instructions and research skill. Used Kenya only to identify input categories; transferred no Kenya parameter.
2. Searched official statistics, AFREC, UNFCCC, World Bank and IFC sources. Separated report dates from data years and targets.
3. Checked the PDF skills. Adobe tools were unavailable, so reports were read with local PDF extraction and their critical pages rendered for visual verification.
4. Downloaded public reports and fuel data; recorded original URLs, metadata, hashes and licenses. Public shell downloads needed approved network escalation. The obsolete SNBS January-2025 PDF URL returned 404; the live March-2025 URL was used.
5. Recomputed balance checks and selected ratios; retained conflicts rather than replacing them with guesses. Historical imports are separated from Mogadishu-only port figures with unresolved units.
6. Audited the entire frozen diesel panel and its matching metadata. Structural checks passed, while the metadata count discrepancy remains documented.
7. Wrote 40 source-located records and the reproducible audit script. No source total was promoted automatically into an active model baseline.
8. Visually verified the requested global IRENA 2025 generation/battery cost benchmarks and stored eight clearly separated comparison rows, without converting them into Somalia assumptions.

Highest priorities are corrected national energy balances, documented physical units and geographic coverage for port fuel imports, observed delivered-generator diesel prices, and annual/hourly commercial and public-service loads. Missing quantities remain missing. The research-question/advisor checkpoint can use these findings to choose a small transparent baseline; no external message was sent.
