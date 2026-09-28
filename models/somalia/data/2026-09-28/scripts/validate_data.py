"""Offline, substantive integrity checks on the downloaded Somalia evidence pack."""
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS = []


def check(name, condition, detail=""):
    CHECKS.append(dict(check=name, passed=bool(condition), detail=detail))


def read_csv(relative):
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main():
    sidecars = sorted((ROOT / "raw").rglob("*.meta.json"))
    entries = [json.loads(p.read_text(encoding="utf-8-sig")) for p in sidecars]
    for entry in entries:
        if entry["status"] != "downloaded":
            continue
        path = ROOT / entry["local_path"]
        exists = path.exists()
        check("file_present:" + entry["source_id"], exists)
        if exists:
            content = path.read_bytes()
            check("sha256:" + entry["source_id"], hashlib.sha256(content).hexdigest() == entry["sha256"])
            check("bytecount:" + entry["source_id"], len(content) == entry["bytes"])
    wdi = read_csv("processed/world_bank_observations.csv")
    keys = [(r["indicator_code"], r["year"]) for r in wdi]
    check("wdi_unique_indicator_year", len(keys) == len(set(keys)))
    check("wdi_country", all(r["country_iso3"] == "SOM" for r in wdi))
    check("wdi_missing_not_zero", all((r["value"] == "") == (r["data_status"] == "missing") for r in wdi))
    raw_wdi = {}
    for path in (ROOT / "raw/world_bank").glob("*.json"):
        if path.name.endswith(".meta.json"):
            continue
        response = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(response, list) and len(response) > 1 and response[1]:
            for row in response[1]:
                raw_wdi[(row["indicator"]["id"], row["date"])] = row["value"]
    check("wdi_all_rows_match_source", all((None if r["value"] == "" else float(r["value"])) == raw_wdi[(r["indicator_code"], r["year"])] for r in wdi))
    check("business_loss_unit", all(r["unit"] == "% of sales for affected firms" for r in wdi if r["indicator_code"] == "IC.FRM.OUTG.ZS"))
    nasa_count = {}
    nasa_missing = 0
    for temporal, start, end, delta in [
        ("hourly", datetime(2025, 1, 1), datetime(2026, 1, 1), timedelta(hours=1)),
        ("daily", datetime(2001, 1, 1), datetime(2026, 1, 1), timedelta(days=1))]:
        pattern = "%Y%m%d%H" if temporal == "hourly" else "%Y%m%d"
        expected, date = [], start
        while date < end:
            expected.append(date.strftime(pattern)); date += delta
        paths = sorted((ROOT / "processed/nasa_power").glob(temporal + "_*.csv"))
        check("nasa_" + temporal + "_site_count", len(paths) == 10)
        nasa_count[temporal] = 0
        for path in paths:
            rows = read_csv(path.relative_to(ROOT))
            site_id = path.stem[len(temporal)+1:]
            raw_path = next((ROOT / "raw/nasa_power").glob(temporal + "_" + site_id + "_*.json"))
            raw = json.loads(raw_path.read_text(encoding="utf-8-sig"))
            check("nasa_utc:" + path.name, raw["header"]["time_standard"] == "UTC")
            check("nasa_complete_timestamps:" + path.name, [r["time_utc"] for r in rows] == expected)
            match, physically_plausible = True, True
            fill = raw["header"].get("fill_value", -999)
            for row in rows:
                for parameter in ["ALLSKY_SFC_SW_DWN", "T2M", "WS10M", "WS50M", "RH2M", "PRECTOTCORR"]:
                    source = raw["properties"]["parameter"][parameter].get(row["time_utc"])
                    value = None if row[parameter] == "" else float(row[parameter])
                    source = None if source == fill else source
                    match = match and source == value
                    if value is None:
                        nasa_missing += 1
                        continue
                    physically_plausible = physically_plausible and math.isfinite(value)
                    if parameter in ["ALLSKY_SFC_SW_DWN", "WS10M", "WS50M", "PRECTOTCORR"]:
                        physically_plausible = physically_plausible and value >= 0
                    if parameter == "RH2M":
                        physically_plausible = physically_plausible and 0 <= value <= 100
                    if parameter == "T2M":
                        physically_plausible = physically_plausible and -60 < value < 65
            check("nasa_all_values_match_source:" + path.name, match)
            check("nasa_basic_physical_ranges:" + path.name, physically_plausible)
            nasa_count[temporal] += len(rows)
    irena = read_csv("processed/irena_somalia_electricity.csv")
    dimensions = ["Country/area", "Technology", "Data Type", "Grid connection", "Year"]
    keys = [tuple(row[x] for x in dimensions) for row in irena]
    check("irena_unique_dimension_tuple", len(keys) == len(set(keys)))
    check("irena_country", all(row["Country/area"] == "Somalia" for row in irena))
    vals = {(r["Technology"], r["Data Type"], r["Grid connection"], r["Year"]): float(r["value"]) for r in irena if r["value"] != ""}
    grid_disagreements = []
    for tech, kind, grid, year in vals:
        if grid == "All" and (tech,kind,"On-grid",year) in vals and (tech,kind,"Off-grid",year) in vals:
            residual = vals[(tech,kind,"All",year)] - vals[(tech,kind,"On-grid",year)] - vals[(tech,kind,"Off-grid",year)]
            if abs(residual) > 0.02:
                grid_disagreements.append(dict(technology=tech, data_type=kind, year=year, residual=residual))
    check("irena_grid_parts_reconcile", not grid_disagreements, grid_disagreements)
    capacity = {r["Technology"]: float(r["value"]) for r in irena if r["value"] != "" and r["Year"] == "2025" and r["Grid connection"] == "All" and r["Data Type"] == "Electrical Installed Capacity (MW)"}
    check("irena_2025_renewable_components", abs(capacity["Total Renewable"] - capacity["Solar photovoltaic"] - capacity["Onshore wind energy"]) < 0.011)
    gem = read_csv("processed/gem_somalia_assets.csv")
    count = json.loads((ROOT / "raw/gem/count.json").read_text())["count"]
    check("gem_count_matches_api", len(gem) == count)
    check("gem_unique_unit_ids", len({r["GEM_unit_phase_ID"] for r in gem}) == len(gem))
    for level, count in [("ADM0",1),("ADM1",18),("ADM2",118)]:
        geo = json.loads((ROOT / ("raw/geoboundaries/" + level + ".geojson")).read_text(encoding="utf-8"))
        check("geoboundaries_count_" + level, len(geo["features"]) == count)
    solar_cells = {(r["sheet"], r["cell"]): r["value"] for r in read_csv("processed/solar_country_workbook_cells.csv")}
    solar_summary = read_csv("processed/solar_resource_summary.csv")
    check("solar_summary_matches_source_cells", all(float(r["value"]) == float(solar_cells[(r["source_sheet"], r["source_cell"])]) for r in solar_summary))
    check("solar_unique_statistic_ids", len({r["indicator_id"] for r in solar_summary}) == len(solar_summary))
    power_audit = json.loads((ROOT / "research/power_validation.json").read_text())
    for name, checksum in power_audit["output_sha256"].items():
        check("reviewed_power_transcription_hash:" + name, hashlib.sha256((ROOT / "research" / name).read_bytes()).hexdigest() == checksum)
    wind_meta = json.loads((ROOT / "raw/global_wind_atlas/som_wind-speed_100m_gwa4_20260928.provenance.json").read_text())
    wind_audit = json.loads((ROOT / "raw/global_wind_atlas/som_wind-speed_100m_gwa4_20260928.audit.json").read_text())
    check("wind_saved_audit_complete", wind_audit["pixels_decoded"] and wind_audit["header_validated"])
    check("wind_audit_pixel_accounting", wind_audit["valid_pixel_count"] + wind_audit["missing_or_nonfinite_pixel_count"] == wind_audit["width"] * wind_audit["height"])
    wind_path = ROOT / "raw/global_wind_atlas" / wind_meta["filename"]
    if wind_path.exists():
        check("wind_release_payload_sha256", hashlib.sha256(wind_path.read_bytes()).hexdigest() == wind_meta["sha256"])
        check("wind_release_payload_bytes", wind_path.stat().st_size == wind_meta["byte_count"])
    manual = []
    for filename in ["power_facts.csv", "statistics_facts.csv"]:
        path = ROOT / "research" / filename
        check("research_file_present:" + filename, path.exists())
        if path.exists():
            rows = read_csv(path.relative_to(ROOT)); manual.extend(rows)
            check("fact_ids_unique:" + filename, len({r["fact_id"] for r in rows}) == len(rows))
            required = ["fact_id", "indicator", "source_url", "locator", "evidence_type", "caveat"]
            check("fact_provenance_complete:" + filename, all(all(r.get(k) for k in required) for r in rows))
    available = read_csv("processed/world_bank_availability.csv")
    report = dict(generated_at_utc=datetime.now(timezone.utc).isoformat(), checks=CHECKS,
                  passed=sum(c["passed"] for c in CHECKS), failed=sum(not c["passed"] for c in CHECKS),
                  counts=dict(source_downloads=len(entries), world_bank_indicators_requested=len(available),
                              world_bank_indicators_available=sum(r["status"] == "available" for r in available),
                              world_bank_non_missing_values=sum(r["value"] != "" for r in wdi),
                              nasa_hourly_timestamps=nasa_count["hourly"], nasa_daily_timestamps=nasa_count["daily"],
                              nasa_parameter_values=(nasa_count["hourly"]+nasa_count["daily"])*6,
                              nasa_missing_parameter_values=nasa_missing, irena_rows=len(irena),
                              irena_non_missing_values=sum(r["value"] != "" for r in irena), gem_asset_records=len(gem),
                              manual_fact_rows=len(manual)),
                  optional_payloads={"wind_tiff_present": wind_path.exists(), "wind_tiff_distribution": "Complete release archive; intentionally omitted from ordinary Git"},
                  scope="File integrity, source-to-table fidelity, completeness, identities and elementary physical checks. Wind pixel decoding is recorded in a separate saved audit; this script checks its accounting and the payload hash when present. Not independent field validation, operating-asset confirmation or validation of a runnable SWITCH model.")
    (ROOT / "validation").mkdir(exist_ok=True)
    (ROOT / "validation/validation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (ROOT / "manifests/download_manifest.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k != "checks"}, indent=2))
    for row in CHECKS:
        if not row["passed"]: print("FAILED " + row["check"] + " " + str(row["detail"]))
    return 1 if report["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
