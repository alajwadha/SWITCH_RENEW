"""Build the user-facing author/data-request table from the reviewed register."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = {
    "not_obtained": "Raw files not obtained; public download not identified",
    "author_request": "Authors offer data on request",
    "confidential": "Explicitly confidential",
    "partial_public": "Partly public; complete study inputs not established",
    "not_located": "Underlying files not located; availability unconfirmed",
    "public_base_missing_replication": "Survey access exists; paper replication files not located",
    "restricted_author_request": "Restricted; anonymized access may be requested",
}

def main():
    package = json.loads((ROOT / "author_data_requests.json").read_text(encoding="utf-8"))
    papers = {p["id"]: p for p in json.loads((ROOT / "publications.json").read_text(encoding="utf-8"))}
    rows = package["requests"]
    lines = [
        "# Authors and data to request",
        "",
        f"Checked 28 September 2026. **{len(rows)} prioritized data-request leads with {sum(len(r['contacts']) for r in rows)} public professional contact entries.** These contacts are for the user to request data for the existing research. No author was contacted and no research scope or model setting was changed.",
        "",
        "Priority reflects the potential usefulness of the underlying data, not certification of data that we have not received. The distinction between confidential, offered-on-request, public, and not-located data is explicit. Corresponding authors may need to route requests to the actual data owner. Email addresses are publicly documented; deliverability has not been tested.",
        "",
        "| Lead / priority | Publication and authors to contact | Public professional contact | What to request | Why useful | Availability |",
        "|---|---|---|---|---|---|",
    ]
    exports = []
    def cell(v):
        return str(v).replace("|", " / ").replace("\n", " ")
    for r in rows:
        ps = [papers[i] for i in r["publication_ids"]]
        names = "; ".join(c["name"] for c in r["contacts"])
        emails = "<br>".join("[" + c["email"] + "](" + c["source_url"] + ")" for c in r["contacts"])
        labels = ", ".join("[" + p["id"] + "](" + p["primary_url"] + ")" for p in ps)
        lines.append("| [" + r["id"] + "](#" + r["id"].lower() + ") / " + r["priority"] + " | " + labels + "<br>" + cell(names) + " | " + emails + " | " + cell(r["data_to_request"]) + " | " + cell(r["why_useful"]) + " | " + STATUS[r["availability_status"]] + " |")
        exports.append({
            "request_id": r["id"], "priority": r["priority"], "topic": r["topic"],
            "publication_ids": "; ".join(r["publication_ids"]),
            "publication_titles": "; ".join(p["title"] for p in ps),
            "publication_authors": " || ".join("; ".join(p["authors"]) for p in ps),
            "publication_urls": "; ".join(p["primary_url"] for p in ps),
            "contact_names": names, "contact_emails": "; ".join(c["email"] for c in r["contacts"]),
            "contact_roles": "; ".join(c["role"] for c in r["contacts"]),
            "contact_sources": "; ".join(c["source_url"] for c in r["contacts"]),
            "contact_locators": "; ".join(c["locator"] for c in r["contacts"]),
            "availability_status": r["availability_status"], "availability_detail": r["availability_detail"],
            "data_to_request": r["data_to_request"], "why_useful": r["why_useful"],
            "reuse_limit": r["reuse_limit"], "availability_source_url": r["availability_source_url"],
            "availability_locator": r["availability_locator"], "contact_checked_on": r["contact_checked_on"],
            "outreach_status": r["outreach_status"],
        })
    lines += ["", "## Source and request details", ""]
    for r in rows:
        lines += ['<a id="' + r["id"].lower() + '"></a>', "", "### " + r["id"] + " — " + r["topic"], ""]
        for pid in r["publication_ids"]:
            p = papers[pid]
            lines += ["- **Publication:** [" + p["title"] + "](" + p["primary_url"] + ") (" + str(p["year"]) + "). **Authors:** " + "; ".join(p["authors"]) + "."]
        for c in r["contacts"]:
            lines += ["- **Contact:** " + c["name"] + " — " + c["email"] + ". " + c["role"] + ". [Public source](" + c["source_url"] + "), " + c["locator"] + "."]
        lines += ["", "**Access evidence:** " + r["availability_detail"] + " [Source](" + r["availability_source_url"] + "), " + r["availability_locator"] + ".",
                  "", "**Ask for:** " + r["data_to_request"], "", "**Value to the existing research:** " + r["why_useful"],
                  "", "**Reuse boundary:** " + r["reuse_limit"], ""]
    lines += [
        "## Include these details in a data request", "",
        "Name the paper and the exact files/variables requested. Ask for observation dates, units, time zone, sampling interval, missing-value/quality flags, anonymization, source version, code or data dictionary, and permitted research use/citation. Accept a link to an existing repository or an aggregate dataset if original records cannot be shared. Request only fields actually recorded; do not imply that a missing dataset already exists.",
        "",
        "Public starter-kit repositories, SIHBS/SHDS access routes and WBES are not classified as unavailable merely because their downloads were not exercised. See [data leads](DATA_LEADS.md).",
        "",
        "Machine-readable versions: [CSV](author_data_requests.csv) and [JSON](author_data_requests.json). [QC and disposition](../../reviews/2026-09-28/README.md).",
    ]
    (ROOT / "AUTHOR_DATA_REQUESTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    with (ROOT / "author_data_requests.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(exports[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(exports)
    print(json.dumps({"requests": len(rows), "contact_entries": sum(len(r["contacts"]) for r in rows)}))

if __name__ == "__main__":
    main()
