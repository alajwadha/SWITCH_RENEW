"""Fetch a reproducible country profile snapshot. Never invent missing observations."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from pathlib import Path
import hashlib
import json
import sys
import urllib.request
import pycountry

ROOT = Path(__file__).resolve().parents[1]
INDICATORS = {
    "population": ("SP.POP.TOTL", "Population", "people"),
    "gdp": ("NY.GDP.MKTP.CD", "GDP", "current US$"),
    "gdp_per_capita": ("NY.GDP.PCAP.CD", "GDP per person", "current US$/person"),
    "urban_population": ("SP.URB.TOTL.IN.ZS", "Urban population", "% of population"),
    "electricity_access": ("EG.ELC.ACCS.ZS", "Electricity access", "% of population"),
    "clean_cooking": ("EG.CFT.ACCS.ZS", "Clean cooking access", "% of population"),
    "electricity_per_capita": ("EG.USE.ELEC.KH.PC", "Electricity consumption per person", "kWh/person/year"),
    "renewable_electricity": ("EG.ELC.RNEW.ZS", "Renewable electricity generation", "% of generation"),
    "electricity_losses": ("EG.ELC.LOSS.ZS", "Transmission and distribution losses", "% of output"),
    "energy_intensity": ("EG.EGY.PRIM.PP.KD", "Primary energy intensity", "MJ per 2021 PPP US$ GDP"),
    "land_area": ("AG.LND.TOTL.K2", "Land area", "km²"),
}

def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "SWITCH-Workbench-research/0.1"}), timeout=45) as response:
        return response.read()

def main(output_dir=None):
    # Annual 2026 is unfinished in September 2026, so do not request it as a completed year.
    year = date.today().year - 1
    stamp = datetime.now(timezone.utc).isoformat()
    raw_dir = ROOT / "workspace" / "atlas_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    countries_url = "https://api.worldbank.org/v2/country?format=json&per_page=400"
    raw = fetch(countries_url)
    (raw_dir / "countries.json").write_bytes(raw)
    wb_countries = json.loads(raw)[1]
    countries = {c.alpha_3: {"iso3": c.alpha_3, "iso2": c.alpha_2, "name": c.name, "capital": None, "region": None, "income_group": None, "lat": None, "lon": None, "indicators": {}} for c in pycountry.countries}
    for c in wb_countries:
        if c["region"]["id"] == "NA":
            continue
        iso = c["id"]
        if iso not in countries:
            countries[iso] = {"iso3": iso, "iso2": c["iso2Code"], "indicators": {}}
        countries[iso].update(name=c["name"], capital=c["capitalCity"] or None, region=c["region"]["value"], income_group=c["incomeLevel"]["value"], lat=float(c["latitude"]) if c["latitude"] else None, lon=float(c["longitude"]) if c["longitude"] else None)
    errors = []
    metadata = {}

    def get_indicator(key, definition):
        code, label, unit = definition
        url = f"https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&date=2010:{year}&per_page=20000"
        cached_path = raw_dir / f"{code}.json"
        cached = json.loads(cached_path.read_bytes()) if cached_path.exists() else None
        try:
            b = fetch(url)
            payload = json.loads(b)
        except Exception:
            # Some indicator series reject full-range calls. Request the latest
            # non-empty observation; keep cached history instead of losing it.
            url = f"https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&per_page=1000&mrnev=1"
            b = fetch(url)
            payload = json.loads(b)
        if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
            raise ValueError(f"Invalid World Bank response for {code}")
        if payload[0].get("pages", 1) > 1:
            raise ValueError(f"Unfetched pagination for {code}; refusing a partial snapshot")
        try:
            detail = json.loads(fetch(f"https://api.worldbank.org/v2/indicator/{code}?format=json"))[1][0]
        except Exception:
            detail = {}
        # Store exact provider bytes, plus retained observations separately.
        (raw_dir / f"{code}_latest_response.json").write_bytes(b)
        combined = {(o["countryiso3code"], o["date"]): o for o in (cached[1] if cached else [])}
        combined.update({(o["countryiso3code"], o["date"]): o for o in payload[1]})
        payload[1] = list(combined.values())
        cached_path.write_text(json.dumps(payload))
        return key, definition, url, b, payload, detail

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(get_indicator, k, d): k for k, d in INDICATORS.items()}
        for future in as_completed(futures):
            key = futures[future]
            try:
                key, (code, label, unit), url, b, payload, detail = future.result()
                metadata[key] = {"code": code, "label": label, "unit": unit, "source": "World Bank · World Development Indicators", "source_url": f"https://data.worldbank.org/indicator/{code}", "retrieval_url": url, "retrieved_at": stamp, "publication_date": payload[0].get("lastupdated"), "sha256": hashlib.sha256(b).hexdigest(), "methodology": detail.get("sourceNote"), "source_organization": detail.get("sourceOrganization"), "license": "World Bank dataset terms; see source indicator for third-party conditions", "status": "source-reported; estimates may be included by the provider"}
                for obs in payload[1]:
                    iso = obs["countryiso3code"]
                    if iso not in countries or obs["value"] is None or int(obs["date"]) > year:
                        continue
                    entry = countries[iso]["indicators"].setdefault(key, {"value": None, "year": None, "history": []})
                    entry["history"].append({"year": int(obs["date"]), "value": obs["value"]})
                    if entry["year"] is None or int(obs["date"]) > entry["year"]:
                        entry.update(value=obs["value"], year=int(obs["date"]))
                print(key, "downloaded", flush=True)
            except Exception as exc:
                errors.append({"indicator": key, "error": str(exc)})
                print(key, str(exc), flush=True)
    for country in countries.values():
        for k, (code, label, unit) in INDICATORS.items():
            country["indicators"].setdefault(k, {"value": None, "year": None, "history": []})
            country["indicators"][k]["history"].sort(key=lambda o: o["year"])
            metadata.setdefault(k, {"code": code, "label": label, "unit": unit, "source": "World Bank · World Development Indicators", "source_url": f"https://data.worldbank.org/indicator/{code}", "retrieved_at": stamp, "status": "unavailable"})
    geo_url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson"
    geo_raw = fetch(geo_url)
    (raw_dir / "natural_earth_50m.geojson").write_bytes(geo_raw)
    geo = json.loads(geo_raw)
    for f in geo["features"]:
        p = f["properties"]
        iso = p.get("ISO_A3_EH") or p.get("ISO_A3")
        if iso in (None, "-99"):
            iso = p.get("ADM0_A3")
        f["properties"] = {"iso3": iso, "name": p.get("ADMIN"), "lat": p.get("LABEL_Y"), "lon": p.get("LABEL_X")}
        if iso in countries and countries[iso].get("lat") is None:
            countries[iso].update(lat=p.get("LABEL_Y"), lon=p.get("LABEL_X"))
    # Write complete new files atomically; keep the previous snapshot if the fetch fails.
    target = output_dir or ROOT / "public"
    target.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": 1, "retrieved_at": stamp, "latest_completed_year": year, "history_start": 2010, "geography": {"source": "Natural Earth, 1:50m", "license": "Public domain", "source_url": "https://www.naturalearthdata.com/about/terms-of-use/", "sha256": hashlib.sha256(geo_raw).hexdigest()}, "metadata": metadata, "countries": sorted(countries.values(), key=lambda c: c["name"]), "errors": errors}
    for name, value in [("atlas.json", payload), ("world.geojson", geo)]:
        tmp = target / (name + ".tmp")
        tmp.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False))
        tmp.replace(target / name)
    print("Saved", len(countries), "country/territory profiles;", len(errors), "source errors")

    return payload
