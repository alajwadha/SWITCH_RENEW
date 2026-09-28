# Reproduction and verification

The manually appraised records under `contributions/` are the source for exports. Each of the four themes has a search/access log and a critical review. Original PDFs and extracted text remain outside this publication.

## Rebuild without network access

From this snapshot directory, using Python 3.10 or later:

```console
python scripts/build_catalogue.py
python scripts/build_data_requests.py
python scripts/validate_catalogue.py
```

All three scripts use the Python standard library. The catalogue builder regenerates the table, JSON, CSV, BibTeX, README and summary. The data-request builder regenerates its table and CSV from `author_data_requests.json`. Validation checks structure, duplicate IDs/DOIs, bibliography matches, links, request references, file hygiene and selected arithmetic; it then writes a SHA-256 manifest. It does **not** prove source claims, verify email delivery or rerun any energy model.

The sibling data-snapshot link is checked after copying into the repository. The checksum file excludes itself. Rebuilding or updating provenance may change hashes; preserve dated versions when making substantive revisions.

## Optional public metadata refresh

```console
python scripts/fetch_crossref.py --retry-errors
python scripts/check_linked_repositories.py
```

These commands require internet access. Crossref results contain compact identity/date/relationship metadata, excluding full abstracts. A cached successful result is preserved. Error retries preserve the previous response. Current linked-repository metadata is separate from the publication-era version; concept identifiers may resolve to later datasets.

Publication findings must still be checked at the original source and at the recorded location. Metadata is not full-text access. DOI registry404 responses for two records are retained as exceptions, with their document/author-deposit checks explicitly recorded.

## Verification boundaries

The primary-source content review and selected visual inspections were performed manually, with exact locators in each record. The scripts do not reconstruct search rankings or certify peer-review quality. No complete retraction check, source-data replication, survey reanalysis, model execution or legal audit was undertaken.

All outputs are original notes and bibliographic/provenance records. Do not infer rights to redistribute linked full texts or confidential data.
