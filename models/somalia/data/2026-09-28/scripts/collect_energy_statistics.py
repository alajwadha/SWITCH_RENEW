"""Somalia-only IRENA and GEM retrieval and World Bank/ESMAP solar workbook extraction."""
import itertools
import json
import urllib.parse
import zipfile
import xml.etree.ElementTree as ET
from collect_data import ROOT, fetch, write_csv


def irena():
    base = "https://pxweb.irena.org/api/v1/en/IRENASTAT/Power%20Capacity%20and%20Generation/"
    catalogue = fetch("IRENA_CATALOGUE", base, "raw/irena/catalogue.json", "IRENA", "IRENA noncommercial attribution terms; https://www.irena.org/terms-and-conditions", "Live table list; preserve release identifiers")
    tables = json.loads((ROOT / catalogue["local_path"]).read_text(encoding="utf-8-sig"))
    selected = [t for t in tables if t["id"].startswith("Country_ELECSTAT")]
    if len(selected) != 1:
        raise ValueError("Require one explicit country electricity table: " + str(selected))
    url = base + urllib.parse.quote(selected[0]["id"])
    meta = fetch("IRENA_DIMENSIONS", url, "raw/irena/dimensions.json", "IRENA", "IRENA noncommercial attribution terms; https://www.irena.org/terms-and-conditions", selected[0]["text"])
    dimensions = json.loads((ROOT / meta["local_path"]).read_text(encoding="utf-8-sig"))
    query = []
    for variable in dimensions["variables"]:
        values = variable["values"]
        if "Country" in variable["code"]:
            values = [v for v, label in zip(variable["values"], variable["valueTexts"]) if label == "Somalia"]
            assert len(values) == 1, "Somalia dimension missing or ambiguous"
        query.append(dict(code=variable["code"], selection=dict(filter="item", values=values)))
    request = dict(query=query, response=dict(format="json-stat2"))
    entry = fetch("IRENA_SOMALIA_ELECTRICITY", url, "raw/irena/somalia_electricity.json", "IRENA", "IRENA noncommercial attribution terms; https://www.irena.org/terms-and-conditions", "All available electricity capacity/generation categories for Somalia; overlapping technology hierarchies must not be summed", request)
    data = json.loads((ROOT / entry["local_path"]).read_text(encoding="utf-8-sig"))
    if data.get("class") != "dataset":
        raise ValueError("Unexpected JSON-stat response")
    dimensions_ordered = []
    for dimension_id in data["id"]:
        category = data["dimension"][dimension_id]["category"]
        idx = category["index"]
        codes = sorted(idx, key=idx.get) if isinstance(idx, dict) else idx
        dimensions_ordered.append([(code, category.get("label", {}).get(code, code)) for code in codes])
    rows = []
    values, flags = data["value"], data.get("status", {})
    for i, coordinate in enumerate(itertools.product(*dimensions_ordered)):
        value = values[i] if isinstance(values, list) else values.get(str(i))
        flag = flags[i] if isinstance(flags, list) else flags.get(str(i), "")
        row = {dimension_id: coordinate[j][1] for j, dimension_id in enumerate(data["id"])}
        row.update(value=value, source_flag=flag, source_id=entry["source_id"], release=selected[0]["id"], source_url=url,
                   data_status="missing" if value is None else "source_reported")
        rows.append(row)
    write_csv(ROOT / "processed/irena_somalia_electricity.csv", rows)
    print("IRENA: " + str(len(rows)) + " values including nulls; dimensions " + str(data["id"]) + "; labels " + str([[p[1] for p in d[:5]] for d in dimensions_ordered]), flush=True)


def gem():
    base = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/Global_Integrated_Power_v1/FeatureServer/0"
    fetch("GEM_LAYER", base + "?f=json", "raw/gem/layer.json", "Global Energy Monitor / Esri distribution", "CC BY 4.0; attribute GEM", "Layer metadata; API snapshot may be older than GEM latest release")
    fetch("GEM_DISTRIBUTION", "https://www.arcgis.com/sharing/rest/content/items/d48c087b6d8141599d4923e70e610fca?f=json", "raw/gem/distribution.json", "Global Energy Monitor / Esri distribution", "CC BY 4.0; attribute GEM", "Source distribution metadata, release and limitations")
    where = "Country_area LIKE '%Somal%'"
    count_url = base + "/query?" + urllib.parse.urlencode(dict(where=where, returnCountOnly="true", f="json"))
    count_entry = fetch("GEM_SOMALIA_COUNT", count_url, "raw/gem/count.json", "GEM", "CC BY 4.0", "Validate complete query result")
    count = json.loads((ROOT / count_entry["local_path"]).read_text(encoding="utf-8-sig"))["count"]
    query = dict(where=where, outFields="*", returnGeometry="false", orderByFields="OBJECTID", resultRecordCount=2000, f="json")
    url = base + "/query?" + urllib.parse.urlencode(query)
    entry = fetch("GEM_SOMALIA_ASSETS", url, "raw/gem/somalia_assets.json", "Global Energy Monitor / Esri distribution", "CC BY 4.0; attribute Global Energy Monitor", "Threshold-limited power asset inventory; not national installed total")
    data = json.loads((ROOT / entry["local_path"]).read_text(encoding="utf-8-sig"))
    assert len(data["features"]) == count and not data.get("exceededTransferLimit"), "Incomplete GEM download"
    rows = [dict(f["attributes"], source_id=entry["source_id"], coverage_note="technology_threshold_limited_not_national_total") for f in data["features"]]
    if rows:
        write_csv(ROOT / "processed/gem_somalia_assets.csv", rows)
    print("GEM asset records: " + str(len(rows)), flush=True)


def solar():
    url = "https://datacatalogfiles.worldbank.org/ddh-published/0038379/1/DR0046831/solargis_pvpotential_countryranking_2020_data.xlsx"
    entry = fetch("ESMAP_SOLAR_WORKBOOK", url, "raw/solar/solargis_pvpotential_countryranking_2020_data.xlsx", "World Bank / ESMAP / Solargis", "CC BY 4.0 per World Bank dataset; acknowledge Solargis", "Global Photovoltaic Power Potential by Country 2020; long-term modeled resources")
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rows = []
    # Read-only OOXML cell extraction. No spreadsheet authoring or recalculation.
    with zipfile.ZipFile(ROOT / entry["local_path"]) as archive:
        strings = ["".join(n.itertext()) for n in ET.fromstring(archive.read("xl/sharedStrings.xml")).findall("m:si", ns)]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheet_names = [s.attrib["name"] for s in workbook.findall("m:sheets/m:sheet", ns)]
        for index, sheet_name in enumerate(sheet_names, 1):
            cells = []
            for node in ET.fromstring(archive.read("xl/worksheets/sheet%d.xml" % index)).findall("m:sheetData/m:row", ns):
                row = {}
                for cell in node.findall("m:c", ns):
                    value_node = cell.find("m:v", ns)
                    value = value_node.text if value_node is not None else ""
                    if cell.attrib.get("t") == "s" and value:
                        value = strings[int(value)]
                    if cell.attrib.get("t") == "inlineStr":
                        value = "".join(cell.find("m:is", ns).itertext())
                    row[cell.attrib["r"]] = value
                cells.append(row)
            selected = [r for r in cells if any(v in ["SOM", "Somalia"] for v in r.values())]
            if not selected:
                continue
            for row in cells[:2] + selected:
                for cell, value in row.items():
                    rows.append(dict(sheet=sheet_name, cell=cell, value=value, source_id=entry["source_id"], role="source_header" if row in cells[:2] else "somalia_source_value"))
            print("Solar sheet " + sheet_name + ": " + str(selected), flush=True)
    write_csv(ROOT / "processed/solar_country_workbook_cells.csv", rows)


if __name__ == "__main__":
    irena()
    gem()
    solar()
    entries = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "raw").rglob("*.meta.json"))]
    (ROOT / "manifests/download_manifest.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")

