# Reproduce and inspect the data

Python 3.8+ and `requests` are sufficient for the main acquisition and verification scripts. Run from this directory; the scripts resolve paths relative to themselves. The World Bank solar workbook is read as an OOXML archive and is never rewritten.

```text
python scripts/collect_data.py --only wdi
python scripts/collect_data.py --only hourly
python scripts/collect_data.py --only daily
python scripts/collect_data.py --only boundaries
python scripts/collect_energy_statistics.py
python scripts/build_crosswalk.py
python scripts/build_catalogue.py
python scripts/validate_data.py
python scripts/build_catalogue.py
```

For the optional schema comparison, supply an existing Kenya input checkout:

```text
python scripts/collect_data.py --only kenya --kenya-inputs PATH_TO_KENYA_INPUTS
```

The recorded Kenya reference is `NotEleven/Switch-Kenya-2025_public` commit `089834b8fee23239d61ffb6e7d68279f0a74efed`. The comparison script reads files only and does not run SWITCH.

Existing raw snapshots with sidecars are reused. The offline validation command does not require network access. To refresh to a new vintage, use a separate directory and compare releases; do not overwrite this frozen evidence silently. Mutable upstream URLs can return different bytes later, so the saved hashes and raw files, rather than a current URL alone, identify this collection.

The report-derived fact tables were manually extracted and visually checked against the exact pages listed in each row. Their source manifests preserve hashes and URLs. They require a human table check to refresh; the collection scripts do not claim to parse those reports automatically. Full report copies and rendered pages are not part of the published Git snapshot.

Large rasters, where downloaded, have explicit retrieval manifests and separate metadata/audit records. Refer to `research/resource_geospatial.md` for the exact source and reproduction route. Access-limited, registration-only and unresolved-license datasets remain catalogue records. A source URL being catalogued does not mean the underlying dataset was acquired.

The full release archive contains the wind TIFF; an ordinary Git checkout contains its manifest, audit and retrieval script. The saved validation report includes the TIFF hash and byte-count checks. Running validation without the TIFF records its absence under `optional_payloads` and performs two fewer checks. It does not download the raster or repeat pixel decoding.

Rebuild the fuel annotations from the frozen source ZIPs:

```text
python research/fuel_audit.py --archive raw/world_bank_fuel/SOM_RTEP_mkt_2007_2026-08-24.zip --metadata-archive raw/world_bank_fuel/SOM_RTP_details_mkt_2007_2026-08-24.zip --json-out validation/fuel_archive_audit.json --annotated-out processed/fuel_prices_annotated.csv
```

`python research/power_build_tables.py` reproduces the manually reviewed power transcriptions. It is not an automatic PDF extractor and retains the recorded PDF hashes if the unpublished local caches are absent. Review source pages manually before changing those transcriptions.

For optional full wind pixel validation, install `Pillow`, `numpy`, `tifffile` and `imagecodecs` in a separate environment, then run:

```text
python raw/global_wind_atlas/retrieve_gwa.py --audit-existing
```

Without `--audit-existing`, the same script downloads the provider's current raster. A mutable upstream download must be compared with the frozen provenance hash before treating it as this snapshot. Re-auditing updates the audit timestamp and source-file timestamp record; preserve the original manifest if making a new vintage.

To package a new archive without publishing it:

```text
python scripts/package_release.py --output ../somalia-data-2026-09-28.zip
```

The packager writes a per-file checksum inventory, verifies ZIP CRCs and records the archive checksum in `manifests/publication_archive.json`. The archive manifest is outside the ZIP to avoid a circular checksum. The inventory omits itself and that archive manifest. ZIP timestamps can change the archive hash on a later rebuild; individual file hashes identify unchanged content. The optional `--copy-git-to` argument copies publishable files to an empty repository data directory, omitting TIFFs from normal Git storage.
