"""Build the human entry point and flat source register from the frozen evidence."""
import csv
import hashlib
import json
from pathlib import Path
from collect_data import ROOT, write_csv


def csvrows(relative):
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def solar_summary():
    cells = csvrows("processed/solar_country_workbook_cells.csv")
    lookup = {(r["sheet"],r["cell"]):r["value"] for r in cells}
    mappings = [
        ("national_ghi", "Average GHI", "Country indicators", "K170", "kWh/m2/day", "long_term"),
        ("national_pvout", "Average practical PV output Level1", "Country indicators", "L170", "kWh/kWp/day", "long_term"),
        ("pv_seasonality", "PV seasonality index", "Country indicators", "N170", "ratio", "long_term"),
    ]
    months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    for i,month in enumerate(months):
        mappings.append(("pvout_"+month.lower(), "PVOUT Level1 " + month, "Monthly data", chr(ord("F")+i)+"170", "kWh/kWp/day", "long_term_monthly_climatology"))
    for statistic, ghi_col, pv_col in [("minimum","E","M"),("spatial_p10","F","N"),("spatial_p25","G","O"),("mean","H","P"),("median","I","Q"),("spatial_p75","J","R"),("spatial_p90","K","S"),("maximum","L","T")]:
        mappings.append(("ghi_"+statistic, "GHI " + statistic, "Summary statistics", ghi_col+"170", "kWh/m2/day", "long_term_spatial_statistic"))
        mappings.append(("pvout_"+statistic, "PVOUT Level1 " + statistic, "Summary statistics", pv_col+"170", "kWh/kWp/day", "long_term_spatial_statistic"))
    rows = [dict(indicator_id=i, indicator_name=n, value=float(lookup[(s,c)]), unit=u, geography="Somalia source country extent", temporal_basis=t, publication_year=2020,
                 source_id="ESMAP_SOLAR_WORKBOOK", source_sheet=s, source_cell=c, source_url="https://energydata.info/dataset/global-photovoltaic-power-potential-by-country",
                 caveat="Long-term modeled resource; not2020 weather. Spatial percentiles are not exceedance probabilities; PVOUT technology/design assumptions are source-specific.") for i,n,s,c,u,t in mappings]
    write_csv(ROOT / "processed/solar_resource_summary.csv", rows)


def source_register():
    rows = []
    for entry in json.loads((ROOT / "manifests/download_manifest.json").read_text(encoding="utf-8")):
        rows.append(dict(source_id=entry["source_id"], record_kind="download", title=entry["description"], publisher=entry["publisher"], source_url=entry["url"],
                         publication_date="", retrieved_at=entry["retrieved_at_utc"], access_status=entry["status"], license=entry["license"],
                         local_path=entry["local_path"], sha256=entry.get("sha256", ""), note="HTTP200 responses may contain API error messages; use availability table and metadata" if entry["source_id"].startswith("WDI") else "See dataset-specific interpretation and validation"))
    for entry in csvrows("research/resource_catalog.csv"):
        rows.append(dict(source_id=entry["source_id"], record_kind="dataset_catalogue", title=entry["title"], publisher=entry["publisher"], source_url=entry["landing_url"], publication_date="",
                         retrieved_at="2026-09-28", access_status=entry["access_status"], license=entry["license"], local_path="research/resource_catalog.csv", sha256="", note=entry["caveat"]))
    grouped = {}
    for filename in ["power_facts.csv","statistics_facts.csv","global_cost_benchmarks.csv"]:
        for row in csvrows("research/" + filename):
            grouped.setdefault(row["source_url"], row)
    for url,row in grouped.items():
        sid = "REPORT_" + hashlib.sha256(url.encode()).hexdigest()[:10]
        rows.append(dict(source_id=sid, record_kind="report_or_primary_page", title=row["source_title"], publisher=row["publisher"], source_url=url,
                         publication_date=row["publication_date"], retrieved_at="2026-09-28", access_status="source_opened; factual extracts retained", license="Report-specific; original PDF not redistributed in Git", local_path="research/", sha256="", note="Exact locator, evidence class and caveat recorded per fact; document hashes where retained are in report manifests"))
    for row in csvrows("research/fuel_reference_defaults.csv"):
        rows.append(dict(source_id=row["reference_id"],record_kind="global_reference",title=row["parameter"],publisher="IPCC",source_url=row["source_url"],publication_date=row["source_year"],retrieved_at="2026-09-28",access_status="original PDF table inspected",license="IPCC source retained as citation and factual extract",local_path="research/fuel_reference_defaults.csv",sha256="",note=row["caveat"]))
    wind = json.loads((ROOT / "raw/global_wind_atlas/som_wind-speed_100m_gwa4_20260928.provenance.json").read_text())
    rows.append(dict(source_id="GWA_SOMALIA_100M",record_kind="download_release_archive",title=wind["title"],publisher=wind["attribution"],source_url=wind["source_url"],publication_date="GWA4; climatology2008-2017",retrieved_at=wind["retrieval_completed_utc"],access_status="downloaded and decoded; TIFF included in GitHub Release archive",license=wind["license"],local_path="raw/global_wind_atlas/"+wind["filename"],sha256=wind["sha256"],note=wind["not_claimed"]))
    write_csv(ROOT / "manifests/source_register.csv", rows)


def readme():
    validation = json.loads((ROOT / "validation/validation_report.json").read_text())
    c = validation["counts"]
    fuel = json.loads((ROOT / "validation/fuel_archive_audit.json").read_text())
    power_history = csvrows("research/power_consumption_history.csv")
    planning = csvrows("research/power_planning_assumptions.csv")
    catalog = csvrows("research/resource_catalog.csv")
    text = f"""# Somalia energy evidence and data

**Research snapshot: 28 September 2026.** Data collection and source checks are complete for the files listed here. This is a research evidence pack; a calibrated, runnable Somalia SWITCH model still needs hourly utility loads, reconciled operational assets and network/financing decisions.

[Download the complete data archive, including the wind raster](https://github.com/alajwadha/SWITCH_RENEW/releases/tag/somalia-data-2026-09-28). Smaller raw datasets, CSVs, scripts and documentation are stored directly in this folder. Rights-unclear full reports are linked with provenance, not redistributed.

## Collected data

| Data | Coverage and size | Evidence and limitation | Files |
|---|---|---|---|
| Electricity access, economy, population, land and infrastructure | {c['world_bank_non_missing_values']:,} nonmissing values across {c['world_bank_indicators_available']} available WDI indicators; histories span1960–2025 where available | Source-reported/estimated; each indicator has its own latest year; 7 valid series empty and4 exploratory API identifiers rejected | [Availability](processed/world_bank_availability.csv), [full time series](processed/world_bank_observations.csv), [definitions](processed/world_bank_indicator_metadata.csv) |
| Electricity capacity and generation | {c['irena_non_missing_values']} nonmissing IRENA observations in {c['irena_rows']:,} dimensional rows; 2000–2025 | Current2026H2 release; MW/GWh separated; grid classes and technology subtotals overlap | [IRENA series](processed/irena_somalia_electricity.csv) |
| Power sector, utility, tariff and project evidence | 100 source-located records | Existing, estimated, planned, contracted and commissioned capacity separated | [Facts](research/power_facts.csv), [analysis](research/power_evidence.md) |
| Utility consumption histories | {len(power_history)} cells, including {sum(bool(r['value_mwh']) for r in power_history)} numeric values and {sum(not r['value_mwh'] for r in power_history)} missing entries | Reported histories and estimated service-area values retain their original classification; not verified hourly load | [Consumption](research/power_consumption_history.csv) |
| Somalia planning parameters | {len(planning)} source-located entries | Published candidate-technology assumptions, not measured costs/performance or adopted SWITCH inputs | [Plan assumptions](research/power_planning_assumptions.csv) |
| Diesel market prices | {fuel['rows']:,} location-month rows, Jan2007–Aug2026; {fuel['physical_market_locations']} physical markets plus one aggregate | SOS/L publisher labels; {fuel['source_price_field_nonblank']:,} source-price fields versus {fuel['modeled_close_nonblank']:,} modeled close estimates | [Annotated prices](processed/fuel_prices_annotated.csv), [audit](validation/fuel_archive_audit.json) |
| Hourly solar and weather | {c['nasa_hourly_timestamps']:,} timestamps at10 locations in2025, six variables | UTC,8,760 hours/site; gridded estimates, not plant output | [Site series](processed/nasa_power), [sites](processed/resource_sampling_sites.csv) |
| Long weather history | {c['nasa_daily_timestamps']:,} daily timestamps at10 locations,2001–2025 | Six variables; useful for variability checks, not subhourly dispatch | [Daily summaries](processed/nasa_daily_summary.csv), [metadata](processed/nasa_daily_parameter_metadata.csv) |
| National solar resource | 31 long-term resource/seasonality/monthly/spatial statistics | World Bank/ESMAP/Solargis2020 study, not a2020 weather observation | [Summary](processed/solar_resource_summary.csv), [original cell extract](processed/solar_country_workbook_cells.csv) |
| National wind resource | 54.5MB GWA4 raster,100m height;19,053,180 finite cells | Approximately250m product; includes offshore;2008–2017 reference climate; no national land mean inferred | [Audit](raw/global_wind_atlas/som_wind-speed_100m_gwa4_20260928.audit.json), [retrieve](raw/global_wind_atlas/retrieve_gwa.py), full TIFF in release |
| Power asset inventory | {c['gem_asset_records']} GEM unit/phase records | February2026 public distribution; small-generator coverage incomplete and statuses need current verification | [Assets](processed/gem_somalia_assets.csv) |
| Administrative geography | Country,18 ADM1 and118 ADM2 geometries and names | geoBoundaries version differs from OCHA91-district metadata; these are not electricity zones | [Geometry and metadata](raw/geoboundaries), [discussion](research/resource_geospatial.md) |
| Wider energy/economy/policy evidence | 40 source-located records | SNBS,AFREC,World Bank,IFC,NDC; conflicting records retained and quarantined | [Facts](research/statistics_facts.csv), [analysis](research/statistics_fuels.md) |
| Further spatial and environmental sources | {len(catalog)} catalogued products | Population,roads,land cover,floods,drought,hydrology and constraints; many are metadata-only or registration-limited | [Dataset catalogue](research/resource_catalog.csv) |
| Global technology/fuel references | 8 IRENA cost benchmarks and2 IPCC defaults | Separate from Somalia evidence; no implicit proxy adoption | [Costs](research/global_cost_benchmarks.csv), [fuel defaults](research/fuel_reference_defaults.csv) |
| Kenya-to-Somalia input map | All26 Kenya input files inventoried | File/field checklist only; no Kenya numerical parameters transferred | [Crosswalk](processed/kenya_to_somalia_crosswalk.csv), [remaining requests](processed/priority_data_requests.csv) |

## Selected findings

- WDI electricity access: **54.4% in2024**, with urban73.4% and rural24.4%. These are access statistics, not electricity consumption or reliability measures.
- IRENA2025 renewable capacity: **49.46MW**, comprising45.91MW solar PV and3.55MW onshore wind. Non-renewable capacity is reported as300MW. These national series do not establish a complete operating-unit list.
- Long-term national GHI: **6.0283kWh/m²/day**; practical PV output Level1: **4.7617kWh/kWp/day** in the2020 ESMAP study. Both are modeled resource estimates.
- The March2026 restructuring paper removes the earlier132kV scope from its proposal; subsequent approval was not established. A contract or national planning option is not proof of commissioning.

## Quality and remaining limits

The [validation report](validation/validation_report.json) records **{validation['passed']} passed checks and {validation['failed']} failures** for its stated scope. The NASA tables contain1,073,460 parameter values with no missing source values in the requested windows. Fuel structural validation found no errors, while its observation-count metadata disagreement remains explicit. The wind raster was decoded and its dimensions,CRS,missing pixels and finite range checked separately.

**Source contradictions remain unresolved and visible.** These include incompatible official generation mixes, energy-balance arithmetic, fuel units, emissions baselines, geographic versions and data vintages. See the [conflict register](CONFLICTS.md). Passing file checks does not validate those disputed quantities.

## Navigation and reproduction

- [Source register](manifests/source_register.csv) and [download requests/checksums](manifests/download_manifest.json)
- [Methods](METHODS.md), [data dictionary](DATA_DICTIONARY.md), [reproduction commands](REPRODUCE.md)
- [Assumptions and decisions](ASSUMPTIONS_AND_DECISIONS.md), [work log](WORK_LOG.md)
- [Prepared advisor checkpoint](ADVISOR_BRIEF.md); no advisor or data-provider message was sent

No model run, residential-demand extension or Kenya parameter transfer was performed. Existing project work was preserved. Dataset-specific licenses apply; this collection does not relicense third-party material.
"""
    # Add spacing in prose while preserving Markdown targets and code literals.
    import re
    chunks = re.split(r"(`[^`]*`|\]\([^)]*\))", text)
    for i in range(0, len(chunks), 2):
        chunks[i] = re.sub(r"(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])", " ", chunks[i])
        for token in ["ADM1", "ADM2", "GWA4", "H2"]:
            chunks[i] = chunks[i].replace(re.sub(r"(?<=[A-Za-z])(?=\d)", " ", token), token)
        chunks[i] = re.sub(r",(?=[A-Za-z])|(?<=[A-Za-z]),(?=\d)|;(?=\d)", lambda match: match.group(0) + " ", chunks[i])
    text = "".join(chunks)
    (ROOT / "README.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    solar_summary()
    source_register()
    readme()

