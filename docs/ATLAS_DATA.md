# Global energy atlas: data and coverage

This atlas expands every one of the 251 ISO/World Bank country and territory profiles at once. Every profile shares the same schema. A profile is not a claim of complete statistical coverage or a geopolitical boundary determination. All twelve energy sections have observations; individual countries and individual metrics may have gaps.

## Snapshot scope

The 8 September 2026 build includes 278 indicators: 253 with at least one country observation and 25 without connected usable observations. It contains 37,124 latest values and 488,520 historical observations. The original population, GDP, access and geography indicators are retained. Machine-readable counts and exclusions are in [atlas-coverage.json](atlas-coverage.json).

| Section | Indicators, including explicit gaps | Profiles with at least one observation |
|---|---:|---:|
| Electricity generation | 49 | 224 |
| Capacity and projects | 62 | 234 |
| Electricity demand | 14 | 217 |
| Whole energy system | 52 | 226 |
| Fuels and security | 26 | 219 |
| Emissions | 3 | 219 |
| Trade and grids | 8 | 217 |
| Storage and flexibility | 10 | 80 |
| Prices and costs | 5 | 39 |
| Access and reliability | 13 | 216 |
| Renewable resources | 21 | 208 |
| Policies and targets | 7 | 203 |
| Additional country context | 8 | 217 |

These counts mean a country has *some* data in a section. They do not imply every field, historical year or latest period is populated. Global cost benchmarks are available as references for every profile but are not counted as country tariff observations.

## Source register and boundaries

| Provider | Data used | Period and boundary |
|---|---|---|
| [Ember yearly and monthly electricity](https://ember-energy.org/data/yearly-electricity-data/) | Fuel generation, shares, changes, demand, net imports, power emissions and intensity | Annual 2010–2025 where reported; monthly 2020 onward including available completed 2026 months. Electricity demand is generation plus net imports. Emissions estimate full lifecycle CO₂e; not combustion-only CO₂. |
| [IRENASTAT](https://pxweb.irena.org/) | 26 technology categories, net capacity additions and selected off-grid categories | Renewable Capacity Statistics 2026 H1 table, annual 2010–2025. Main capacity series use **on-grid** ratings consistently. Off-grid renewables/PV/hydro/bioenergy are separate. MW are divided by 1,000 for GW. |
| [OWID energy data](https://github.com/owid/energy-data) | Primary energy totals, fuel mix, production and intensity | The accompanying codebook preserves Energy Institute and other original-provider methods, including the current primary-energy accounting basis. Do not assume all energy series share Ember's electricity boundary. |
| [EIA international statistics](https://www.eia.gov/international/data/world) | Coal/gas/petroleum production, consumption, imports/exports where reported; coal reserves; electricity imports/exports/losses; geothermal/oil generation; energy-related CO₂ | Native physical units are retained. Billion kWh = TWh. Carbon data are energy-related combustion CO₂; not total economy GHG or land-use emissions. Geography uses source ISO codes. |
| [EIA end-use release](https://www.eia.gov/todayinenergy/detail.php?id=67384) | Residential, commercial, industrial, transport, agriculture, direct-use fuel mix and electrification | Annual direct-use rows through 2023. Excludes transformation, separately classified purchased heat and non-energy feedstocks. Industry includes agriculture; do not add agriculture to industry. Regional residuals are never allocated to individual countries. |
| [World Bank](https://data.worldbank.org/) | Population/economy, energy access, rural/urban cooking, final-energy renewable share, energy imports, resource rents, business survey outage exposure/losses | Actual observation years. Survey data are firms' experience, not utility SAIDI/SAIFI. Losses refer to sales of *affected firms*. Legacy monthly outage counts are archived and not imputed. |
| [Eurostat electricity prices](https://ec.europa.eu/eurostat/databrowser/view/nrg_pc_204/default/table) | Household and non-household tariff bands | Semester prices in EUR/kWh from 2023 onward. Household: 2,500–4,999 kWh/year, all taxes included. Non-household: 500–1,999 MWh/year, VAT and other recoverable taxes excluded. European reporting coverage; no worldwide tariff imputation. |
| [IRENA 2025 generation costs](https://www.irena.org/Publications/2026/Jul/Renewable-Power-Generation-Costs-in-2025) | Seven global technology LCOE/CAPEX/capacity-factor references; four-hour battery reference | Executive summary Figure S1, published July 2026, values in 2025 USD. Global weighted averages for newly commissioned projects; not national tariffs or automatically chosen SWITCH assumptions. |
| [World Bank / ESMAP / Solargis](https://energydata.info/dataset/global-photovoltaic-power-potential-by-country) | GHI, practical PV yield, seasonality, monthly climatology and spatial percentiles | **2020 study, long-term modeled resource**. Underlying climatic reference periods vary by location. PVOUT Level 1 excludes physically unsuitable land. Spatial percentiles are not stochastic P10/P90 forecast probabilities. |
| [Net Zero Tracker via OWID](https://ourworldindata.org/grapher/net-zero-targets) | Target status and target year | July 2026 extract includes other emissions-reduction targets, not strictly net-zero. Gas scope, percentage reduction, conditionality and sector scope are not present. Labelled “emissions target,” never an inferred universal net-zero commitment. |
| [Resources for the Future via OWID](https://ourworldindata.org/grapher/carbon-tax-instruments) | National/subnational carbon-tax status | Annual categorical record through 2025. At least one covered sector does not imply the entire economy is priced. |
| [Global Energy Monitor](https://globalenergymonitor.org/projects/global-integrated-power-tracker/) | Plant/unit/phase coordinates, technology, fuel, status, dates and capacity | Public Esri FeatureServer distribution explicitly identifies **February 2026** vintage. It is not relabeled as GEM's newer August release. 143,109 source records, all fetched with verified pagination. |
| [DOE / NTESS Sandia](https://sandia.gov/ess-ssl/gesdb/public/projects.html) | Historical battery/chemical-storage projects and reported power/energy | **January 2022 inventory**, 1,045 mapped projects. Data remain under validation and are provided as-is. Missing/zero ratings are not usable duration measurements. This older inventory is distinct from current national storage capacity. |
| [Natural Earth](https://www.naturalearthdata.com/about/terms-of-use/) | Bundled globe country geometry | 1:50m, public domain; 242 features. Some small territories require the country picker. |

Provider licenses and required attribution are retained in the app. Numerical transformations do not transfer ownership of the source data. DOE content credits NTESS; GEM data credits Global Energy Monitor and its public Esri distribution. No personal DOE contact details or narrative descriptions are republished. Raw downloads stay in the ignored workspace, not in Git.

## Transformations

- **Per person:** total × unit scale / World Bank population, requiring identical calendar years. TWh × 10⁹ / people gives kWh/person. GW × 10⁹ / people gives W/person. PJ × 10⁶ / people gives GJ/person. Missing or zero population leaves a gap.
- **Annual growth:** 100 × (current / immediately preceding year − 1), only with a positive prior value. Gaps and zero denominators are not interpolated.
- **People without access:** population × (1 − access percentage / 100), same year for both inputs.
- **YTD demand:** January through the last contiguous available month. YTD growth requires the identical months in the previous year. An incomplete annual series is never labeled as a full annual observation.
- **Net capacity additions:** end-year on-grid capacity minus the previous year; may include retirements or source revisions. Not gross construction.
- **End-use conversion:** 1 trillion Btu = 1.05505585262 PJ. Electrical PJ / 3.6 = TWh. Direct-use electrification uses matching selected-sector electricity PJ and total PJ.
- **GEM capacity:** status-specific sums of reported capacities. Cross-border hydro uses country-allocated MW where supplied. This creates 143,172 country records from 143,109 original records without assigning the full shared plant capacity to both countries. Different inventories/technologies have different inclusion thresholds and status rules.
- **Storage:** only operational projects classified entirely as electro-chemical battery and chemical storage contribute to historical subtotals. Power and energy may have different reporting populations. Duration = summed MWh / summed MW for the subset reporting both positive values. Missing/nonpositive ratings are excluded, not treated as installed zero.

The generation mix chart requires a common year across its mutually exclusive Ember categories. The capacity chart shows reported technologies in one year and explicitly counts omitted unreported categories. It does not sum parent and child technology groups or claim a complete national total.

## Explicit remaining data gaps

All profiles include fields explaining these gaps rather than invented observations:

- Harmonized national peak demand, present-day battery MW/MWh/duration, curtailment and accredited demand-response capacity.
- Bilateral electricity partners, individual interconnector ratings/routes/status and a complete LNG terminal inventory.
- Comparable national delivered fuel prices, wholesale prices, subsidy definitions, and household/non-household tariffs outside the Eurostat coverage.
- Proved oil/gas reserves are absent from the connected EIA bulk extract; coal reserves are retained where provided.
- Utility SAIDI/SAIFI and backup-generator electricity shares; firm survey results are separate.
- Area-weighted national wind speed/density at a specified height. The public GWA summary API returned HTTP 400 in this session; the app links to Global Wind Atlas for site assessment. Capital-city weather is not substituted for country resource potential.
- Verified target percentages with capacity/generation/final-energy bases, conditionality, coal phase-out scope and ETS coverage. The carbon-price extract had inconsistent currency-base metadata and was withheld.
- One EIA crude-oil-production mass-unit series has no usable in-range observations; related production metrics in reported native units remain available.

These are source-coverage limits, not a staged country rollout. All 251 profiles can be explored and compared now, including countries whose observations are older or missing.

## Reproduction and files

`scripts/refresh_atlas.py` is the complete refresh entry point; `refresh_energy_atlas.py` builds the index, histories, inventories and data audit, and `energy_sources.py` declares the public sources and acquisition requests. `country_context.py` maintains the original World Bank/geography adapter and runs during `--refresh` into a staging location.

`public/atlas.json` is a small manifest pointing to a gzip-compressed index. The index references alphabetic compressed history and asset shards plus `provenance.json.gz`. The provenance register records exact request URLs/bodies, source SHA-256 digests and retrieval timestamps. The main index also retains per-indicator methods, units, observation periods, source dates, status, coverage and SWITCH relevance. Compressed files use deterministic gzip timestamps.

Run a refresh while the app is stopped, then rebuild. New files are staged before the manifest is replaced; a failed provider request or validation does not publish a partial atlas. Old generated folders are cleaned after publication, so existing open pages should be reloaded after a refresh. For reproducibility of an old version, retain its Git commit and the corresponding raw workspace backup; upstream public URLs can change their data.

The application never writes these contextual statistics into model inputs. Residential demand remains an optional future modeling extension.
