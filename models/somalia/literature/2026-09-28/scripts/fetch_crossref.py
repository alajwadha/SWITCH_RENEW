"""Save compact primary DOI registration metadata; metadata is not a paper review."""
import argparse
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import time
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def fetch(doi, retry_errors=False):
    url = "https://api.crossref.org/works/" + quote(doi, safe="")
    name = hashlib.sha256(doi.lower().encode()).hexdigest()[:16] + ".json"
    target = ROOT / "raw_metadata/crossref" / name
    previous = None
    if target.exists():
        previous = json.loads(target.read_text(encoding="utf-8"))
        if previous.get("status") == "retrieved" or not retry_errors:
            return previous
    request = Request(url, headers={"User-Agent": "SomaliaEnergyScopingReview/1.0 (bibliographic verification)"})
    try:
        with urlopen(request, timeout=45) as response:
            data = json.loads(response.read())["message"]
        fields = ["DOI", "title", "author", "publisher", "container-title", "volume", "issue", "page", "article-number", "type", "published", "published-online", "published-print", "issued", "created", "license", "link", "resource", "URL", "relation", "update-to", "updated-by", "is-referenced-by-count"]
        result = dict(requested_doi=doi, source_url=url, retrieved_at_utc=datetime.now(timezone.utc).isoformat(),
                      status="retrieved", metadata={key: data[key] for key in fields if key in data},
                      scope="Primary DOI registration metadata; not an endorsement or independent validation of findings. Citation counts are not used as a quality score.")
    except Exception as exc:
        result = dict(requested_doi=doi, source_url=url, retrieved_at_utc=datetime.now(timezone.utc).isoformat(), status="error", error=str(exc))
    if previous:
        result["previous_attempts"] = previous.get("previous_attempts", []) + [{k: v for k, v in previous.items() if k != "previous_attempts"}]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--doi-file", type=Path, help="JSON list of DOIs; otherwise inspect contribution records")
    parser.add_argument("--retry-errors", action="store_true")
    args = parser.parse_args()
    if args.doi_file:
        dois = json.loads(args.doi_file.read_text(encoding="utf-8"))
    else:
        dois = [record["doi"] for path in (ROOT / "contributions").glob("*_records.json") for record in json.loads(path.read_text(encoding="utf-8-sig")) if record.get("doi")]
    dois = sorted(set(doi.lower().strip().removeprefix("https://doi.org/") for doi in dois))
    results = []
    for doi in dois:
        results.append(fetch(doi, args.retry_errors))
        time.sleep(0.5)
    for result in results:
        data = result.get("metadata", {})
        print(json.dumps(dict(doi=result["requested_doi"], status=result["status"], title=data.get("title"),
                              authors=[" ".join(filter(None,[a.get("given"),a.get("family")])) or a.get("name","") for a in data.get("author",[])],
                              published=data.get("published"), online=data.get("published-online"), printed=data.get("published-print"),
                              updates=data.get("update-to",[]), error=result.get("error")), ensure_ascii=False))


if __name__ == "__main__":
    main()
