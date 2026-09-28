"""Download public Somalia data, preserve bytes, and create traceable CSV tables.

Python 3.8+, requests. Network access required; no credentials or paid services.
Existing source snapshots are reused. Use a new output directory for a new vintage.
"""
import argparse
import concurrent.futures
import csv
import hashlib
import io
import json
import math
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = []

INDICATORS = {
    "SP.POP.TOTL": ("demography", "people"),
    "SP.POP.GROW": ("demography", "% annual"),
    "SP.URB.TOTL": ("demography", "people"),
    "SP.URB.TOTL.IN.ZS": ("demography", "% of population"),
    "SP.RUR.TOTL": ("demography", "people"),
    "EN.POP.DNST": ("demography", "people/km2 land area"),
    "EG.ELC.ACCS.ZS": ("electricity_access", "% of population"),
    "EG.ELC.ACCS.UR.ZS": ("electricity_access", "% of urban population"),
    "EG.ELC.ACCS.RU.ZS": ("electricity_access", "% of rural population"),
    "EG.CFT.ACCS.ZS": ("energy_access", "% of population"),
    "EG.FEC.RNEW.ZS": ("energy_balance", "% of total final energy consumption"),
    "EG.ELC.RNEW.ZS": ("electricity_generation", "% of electricity output"),
    "EG.USE.PCAP.KG.OE": ("energy_balance", "kg oil equivalent/person"),
    "EG.USE.ELEC.KH.PC": ("electricity_consumption", "kWh/person"),
    "EG.ELC.LOSS.ZS": ("electricity_network", "% of output"),
    "EG.IMP.CONS.ZS": ("energy_balance", "% of energy use"),
    "EG.USE.COMM.FO.ZS": ("energy_balance", "% of total energy use"),
    "EG.ELC.PROD.KH": ("electricity_generation", "kWh"),
    "EG.ELC.FOSL.ZS": ("electricity_generation", "% of total output"),
    "EG.ELC.HYRO.ZS": ("electricity_generation", "% of total output"),
    "EG.ELC.RNWX.ZS": ("electricity_generation", "% of total output"),
    "EG.EGY.PRIM.PP.KD": ("energy_intensity", "MJ/$2021 PPP GDP"),
    "NY.GDP.MKTP.CD": ("economy", "current USD"),
    "NY.GDP.MKTP.KD": ("economy", "constant 2015 USD"),
    "NY.GDP.MKTP.KD.ZG": ("economy", "% annual"),
    "NY.GDP.PCAP.CD": ("economy", "current USD/person"),
    "NY.GDP.PCAP.KD": ("economy", "constant 2015 USD/person"),
    "FP.CPI.TOTL.ZG": ("finance", "% annual"),
    "PA.NUS.FCRF": ("finance", "LCU/USD period average"),
    "NE.IMP.GNFS.CD": ("trade", "current USD"),
    "NE.EXP.GNFS.CD": ("trade", "current USD"),
    "TX.VAL.FUEL.ZS.UN": ("trade", "% of merchandise exports"),
    "TM.VAL.FUEL.ZS.UN": ("trade", "% of merchandise imports"),
    "NV.AGR.TOTL.ZS": ("productive_sectors", "% of GDP"),
    "NV.IND.TOTL.ZS": ("productive_sectors", "% of GDP"),
    "NV.IND.MANF.ZS": ("productive_sectors", "% of GDP"),
    "NV.SRV.TOTL.ZS": ("productive_sectors", "% of GDP"),
    "NE.GDI.TOTL.ZS": ("finance", "% of GDP"),
    "BX.KLT.DINV.WD.GD.ZS": ("finance", "% of GDP"),
    "BX.TRF.PWKR.DT.GD.ZS": ("finance", "% of GDP"),
    "AG.LND.TOTL.K2": ("land", "km2"),
    "AG.LND.AGRI.ZS": ("land", "% of land area"),
    "AG.LND.FRST.ZS": ("land", "% of land area"),
    "AG.LND.ARBL.ZS": ("land", "% of land area"),
    "ER.H2O.INTR.PC": ("water", "m3/person/year"),
    "ER.H2O.FWTL.ZS": ("water", "% of internal resources"),
    "SH.H2O.BASW.ZS": ("water", "% of population"),
    "SH.STA.BASS.ZS": ("water", "% of population"),
    "IT.NET.USER.ZS": ("infrastructure", "% of population"),
    "IT.CEL.SETS.P2": ("infrastructure", "subscriptions/100 people"),
    "IC.ELC.OUTG": ("business_electricity", "outages/typical month"),
    "IC.ELC.LOSS.ZS": ("business_electricity", "% of annual sales"),
    "IC.ELC.OWNG.ZS": ("business_electricity", "% of firms"),
    "IC.FRM.OUTG.ZS": ("business_electricity", "% of sales for affected firms"),
    "IC.ELC.OUTG.ZS": ("business_electricity", "% of firms"),
}

# Deliberately approximate representative city sampling points, not asset locations.
# They are analyst-selected query coordinates and must not be used for plant siting.
SITES = [
    ("mogadishu", "Mogadishu", 2.04, 45.34),
    ("hargeisa", "Hargeisa", 9.56, 44.06),
    ("bosaso", "Bosaso", 11.28, 49.18),
    ("garowe", "Garowe", 8.40, 48.48),
    ("kismayo", "Kismayo", -0.36, 42.55),
    ("baidoa", "Baidoa", 3.12, 43.65),
    ("beledweyne", "Beledweyne", 4.74, 45.20),
    ("galkayo", "Galkayo", 6.77, 47.43),
    ("berbera", "Berbera", 10.44, 45.01),
    ("dhuusamareeb", "Dhuusamareeb", 5.53, 46.39),
]
PARAMETERS = ["ALLSKY_SFC_SW_DWN", "T2M", "WS10M", "WS50M", "RH2M", "PRECTOTCORR"]


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def write_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def fetch(source_id, url, relative, publisher, license_note, description, body=None):
    path = ROOT / relative
    meta_path = path.with_suffix(path.suffix + ".meta.json")
    if path.exists() and meta_path.exists():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = dict(source_id=source_id, url=url, publisher=publisher,
                 license=license_note, description=description, retrieved_at_utc=utcnow(),
                 local_path=relative, status="failed")
    if body is not None:
        entry["request_body"] = body
    for attempt in range(3):
        try:
            headers = {"User-Agent": "SomaliaResearch/1.0 (public academic data collection)"}
            response = requests.post(url, json=body, timeout=(20, 90), headers=headers) if body is not None else requests.get(url, timeout=(20, 90), headers=headers)
            entry.update(http_status=response.status_code, resolved_url=response.url,
                         content_type=response.headers.get("content-type", ""))
            response.raise_for_status()
            # Refuse to mis-save HTML error/challenge pages as JSON data.
            if relative.endswith(".json") or relative.endswith(".geojson"):
                response.json()
            path.write_bytes(response.content)
            entry.update(status="downloaded", bytes=len(response.content),
                         sha256=hashlib.sha256(response.content).hexdigest())
            break
        except Exception as error:
            entry["error"] = str(error)
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
    meta_path.write_text(json.dumps(entry, indent=2), encoding="utf-8")
    return entry


def collect_wdi():
    def one(code):
        url = "https://api.worldbank.org/v2/country/SOM/indicator/" + code + "?format=json&per_page=1000&date=1960:2025&source=2"
        data = fetch("WDI_" + code, url, "raw/world_bank/" + code + ".json", "World Bank WDI and named original providers", "CC BY 4.0 subject to indicator-specific third-party terms", "Somalia annual series including explicit nulls")
        meta_url = "https://api.worldbank.org/v2/indicator/" + code + "?format=json&source=2"
        metadata = fetch("WDI_META_" + code, meta_url, "raw/world_bank_metadata/" + code + ".json", "World Bank", "CC BY 4.0 subject to named original providers", "Indicator definition, original sources and method")
        return code, data, metadata
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(one, INDICATORS))
    observations, availability, metadata_rows = [], [], []
    for code, data, metadata in results:
        MANIFEST.extend([data, metadata])
        rows = []
        response_status = "request_failed"
        definition = {}
        if metadata["status"] == "downloaded":
            response = json.loads((ROOT / metadata["local_path"]).read_text(encoding="utf-8-sig"))
            if isinstance(response, list) and len(response) > 1 and response[1]:
                definition = response[1][0]
        if data["status"] == "downloaded":
            response = json.loads((ROOT / data["local_path"]).read_text(encoding="utf-8-sig"))
            response_status = "api_error" if isinstance(response, list) and response and isinstance(response[0], dict) and "message" in response[0] else "no_non_null_data"
            if isinstance(response, list) and len(response) > 1 and response[1]:
                for record in response[1]:
                    rows.append(dict(indicator_code=code, indicator_name=record["indicator"]["value"],
                                     category=INDICATORS[code][0], country_iso3=record["countryiso3code"],
                                     year=int(record["date"]), value=record["value"], unit=definition.get("unit") or INDICATORS[code][1],
                                     observation_status=record.get("obs_status", ""),
                                     data_status="missing" if record["value"] is None else "source_reported",
                                     source_id=data["source_id"], source_last_updated=response[0].get("lastupdated", ""),
                                     source_url=data["url"]))
        valid = sorted([r for r in rows if r["value"] is not None], key=lambda r: r["year"])
        availability.append(dict(indicator_code=code, indicator_name=definition.get("name", code), category=INDICATORS[code][0],
                                 status="available" if valid else response_status, observations=len(valid),
                                 first_year=valid[0]["year"] if valid else "", last_year=valid[-1]["year"] if valid else "",
                                 latest_value=valid[-1]["value"] if valid else "", unit=definition.get("unit") or INDICATORS[code][1], source_url=data["url"]))
        metadata_rows.append(dict(indicator_code=code, name=definition.get("name", ""), source_note=definition.get("sourceNote", ""),
                                  source_organization=definition.get("sourceOrganization", ""), api_unit=definition.get("unit", ""),
                                  displayed_unit=definition.get("unit") or INDICATORS[code][1], unit_note="API unit if supplied; otherwise indicator-title based unit mapping; verify metadata before conversion", source_url=metadata["url"]))
        observations.extend(rows)
    observations.sort(key=lambda r: (r["indicator_code"], r["year"]))
    write_csv(ROOT / "processed/world_bank_observations.csv", observations)
    write_csv(ROOT / "processed/world_bank_availability.csv", availability)
    write_csv(ROOT / "processed/world_bank_indicator_metadata.csv", metadata_rows)
    print(json.dumps({"wdi_indicators_requested": len(INDICATORS), "available": sum(a["status"] == "available" for a in availability),
                      "non_null_observations": sum(r["value"] is not None for r in observations), "rows_including_nulls": len(observations)}), flush=True)


def collect_power(temporal):
    start, end = ("20250101", "20251231") if temporal == "hourly" else ("20010101", "20251231")
    site_rows = [dict(site_id=s[0], city_label=s[1], latitude=s[2], longitude=s[3], coordinate_status="analyst_selected_approximate_city_sampling_point", not_for="asset_siting_or_electrical_zone_boundaries") for s in SITES]
    write_csv(ROOT / "processed/resource_sampling_sites.csv", site_rows)
    summary, parameter_metadata = [], []
    # Sequential site requests respect NASA guidance to limit simultaneous calls.
    for site_id, name, lat, lon in SITES:
        url = "https://power.larc.nasa.gov/api/temporal/" + temporal + "/point?" + requests.compat.urlencode(dict(parameters=",".join(PARAMETERS), community="RE", longitude=lon, latitude=lat, start=start, end=end, format="JSON", **{"time-standard": "UTC"}))
        relative = "raw/nasa_power/" + temporal + "_" + site_id + "_" + start + "_" + end + ".json"
        entry = fetch("NASA_" + temporal.upper() + "_" + site_id.upper(), url, relative, "NASA POWER", "NASA POWER freely available; acknowledge NASA POWER and underlying data providers", "Gridded resource estimates at approximate city point; not measured site data or generation capacity factors")
        MANIFEST.append(entry)
        if entry["status"] != "downloaded":
            print("NASA failed: " + temporal + " " + site_id, flush=True)
            continue
        data = json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))
        values = data.get("properties", {}).get("parameter", {})
        if not values:
            print("NASA returned no parameter values: " + site_id, flush=True)
            continue
        fill = data.get("header", {}).get("fill_value", -999)
        keys = sorted(set(k for p in values.values() for k in p))
        records = []
        for key in keys:
            row = dict(site_id=site_id, time_utc=key, latitude=lat, longitude=lon)
            for parameter in PARAMETERS:
                value = values.get(parameter, {}).get(key)
                row[parameter] = "" if value is None or value == fill else value
            records.append(row)
        write_csv(ROOT / ("processed/nasa_power/" + temporal + "_" + site_id + ".csv"), records)
        for parameter in PARAMETERS:
            valid = [r[parameter] for r in records if r[parameter] != ""]
            meta = data.get("parameters", {}).get(parameter, {})
            parameter_metadata.append(dict(source_id=entry["source_id"], parameter=parameter, unit=meta.get("units", ""), longname=meta.get("longname", ""),
                                           time_standard=data.get("header", {}).get("time_standard", "UTC_requested"), fill_value=fill))
            summary.append(dict(site_id=site_id, temporal=temporal, start=start, end=end, parameter=parameter, unit=meta.get("units", ""),
                                expected_timestamps=len(keys), non_missing=len(valid), missing=len(keys)-len(valid),
                                minimum=min(valid) if valid else "", maximum=max(valid) if valid else "", arithmetic_mean=sum(valid)/len(valid) if valid else "",
                                source_id=entry["source_id"]))
        print("NASA " + temporal + " " + site_id + ": " + str(len(records)) + " timestamps", flush=True)
    write_csv(ROOT / ("processed/nasa_" + temporal + "_summary.csv"), summary)
    write_csv(ROOT / ("processed/nasa_" + temporal + "_parameter_metadata.csv"), parameter_metadata)


def collect_boundaries():
    for level in ["ADM0", "ADM1", "ADM2"]:
        entry = fetch("GEOBOUNDARIES_META_" + level, "https://www.geoboundaries.org/api/current/gbOpen/SOM/" + level + "/", "raw/geoboundaries/" + level + "_metadata.json", "geoBoundaries; original provider in metadata", "See each returned boundaryLicense; not uniform", "Alternative administrative boundary version, not electrical zones")
        MANIFEST.append(entry)
        if entry["status"] == "downloaded":
            meta = json.loads((ROOT / entry["local_path"]).read_text())
            url = meta.get("simplifiedGeometryGeoJSON") or meta.get("gjDownloadURL")
            if url:
                geo = fetch("GEOBOUNDARIES_" + level, url, "raw/geoboundaries/" + level + ".geojson", "geoBoundaries / " + str(meta.get("boundarySource", "")), meta.get("boundaryLicense", "See metadata"), "Simplified administrative geometry; retain metadata and version")
                MANIFEST.append(geo)
                if geo["status"] == "downloaded":
                    data = json.loads((ROOT / geo["local_path"]).read_text())
                    rows = [f["properties"] for f in data["features"]]
                    fields = sorted(set(k for r in rows for k in r))
                    write_csv(ROOT / ("processed/geoboundaries_" + level + "_units.csv"), rows, fields)
                    print(level + " boundaries: " + str(len(rows)), flush=True)


def collect_kenya(input_path):
    rows = []
    for path in sorted(Path(input_path).glob("*")):
        if not path.is_file():
            continue
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024*1024), b""):
                digest.update(chunk)
        header, count = [], ""
        if path.suffix == ".csv":
            with path.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.reader(handle)
                header = next(reader)
                count = sum(1 for row in reader)
        rows.append(dict(filename=path.name, bytes=path.stat().st_size, sha256=digest.hexdigest(), data_rows=count, columns=" | ".join(header),
                         reference_commit="089834b8fee23239d61ffb6e7d68279f0a74efed", status="schema_reference_only_not_transferred_to_Somalia"))
    write_csv(ROOT / "processed/kenya_input_schema_inventory.csv", rows)
    print("Kenya input files inspected: " + str(len(rows)), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=["wdi", "hourly", "daily", "boundaries", "kenya", "all"], default="all")
    parser.add_argument("--kenya-inputs", default="D:/SWITCH_RENEW/.sources/kenya/inputs")
    args = parser.parse_args()
    if args.only in ["wdi", "all"]: collect_wdi()
    if args.only in ["hourly", "all"]: collect_power("hourly")
    if args.only in ["daily", "all"]: collect_power("daily")
    if args.only in ["boundaries", "all"]: collect_boundaries()
    if args.only in ["kenya", "all"]: collect_kenya(args.kenya_inputs)
    # Rebuild complete manifest from immutable per-download sidecars.
    entries = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "raw").rglob("*.meta.json"))]
    (ROOT / "manifests").mkdir(exist_ok=True)
    (ROOT / "manifests/download_manifest.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
