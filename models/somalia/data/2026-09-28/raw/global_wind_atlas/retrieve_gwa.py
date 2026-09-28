"""Retrieve the public GWA Somalia wind-speed layer and audit a local GeoTIFF.

Requires Python 3. For raster inspection install rasterio, or Pillow + NumPy.
The source URL is mutable: this script records a fresh checksum on every run.
No area mean is calculated. The country product can include offshore cells.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

URL = "https://globalwindatlas.info/api/gis/country/SOM/wind-speed/100"
FILENAME = "som_wind-speed_100m_gwa4_20260928.tif"
MAX_BYTES = 100_000_000
LICENSE_URL = "https://globalwindatlas.info/en/about/TermsOfUse"
METHOD_URL = "https://globalwindatlas.info/en/about/method"

def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def audit_raster(path):
    result = {
        "audit_utc": utc_now(),
        "units": "m/s (provider wind-speed layer)",
        "scope": "All finite cells in delivered Somalia country raster, including offshore cells",
        "area_mean_computed": False,
        "geographic_validation": "Header inspection; national land clipping and boundary reconciliation not performed",
    }
    if importlib.util.find_spec("rasterio"):
        import numpy as np
        import rasterio
        with rasterio.open(path) as ds:
            valid_count = 0
            total_count = ds.width * ds.height
            low, high = float("inf"), float("-inf")
            for _, window in ds.block_windows(1):
                values = ds.read(1, window=window, masked=True).compressed()
                values = values[np.isfinite(values)]
                if values.size:
                    valid_count += int(values.size)
                    low = min(low, float(values.min()))
                    high = max(high, float(values.max()))
            result.update({
                "decoder": "rasterio/GDAL",
                "decoder_version": rasterio.__version__,
                "width": ds.width,
                "height": ds.height,
                "bands": ds.count,
                "dtype": ds.dtypes[0],
                "crs": str(ds.crs),
                "bounds_west_south_east_north": list(ds.bounds),
                "pixel_size_degrees": list(ds.res),
                "nodata": str(ds.nodata),
                "header_validated": True,
                "pixels_decoded": True,
                "valid_pixel_count": valid_count,
                "missing_or_nonfinite_pixel_count": total_count-valid_count,
                "minimum_m_per_s": low if valid_count else None,
                "maximum_m_per_s": high if valid_count else None,
            })
        return result
    if not importlib.util.find_spec("PIL"):
        result.update(header_validated=False, pixels_decoded=False,
                      limitation="Neither rasterio nor Pillow is installed.")
        return result
    from PIL import Image, __version__ as pillow_version
    with Image.open(path) as im:
        tags = dict(im.tag_v2)
        scale = tags.get(33550)
        tie = tags.get(33922)
        key_list = tags.get(34735, ())
        geo_keys = {}
        if len(key_list) >= 4:
            for i in range(key_list[3]):
                key, location, count, value = key_list[4+i*4:8+i*4]
                geo_keys[str(key)] = {"location":location,"count":count,"value":value}
        epsg = geo_keys.get("2048", {}).get("value")
        result.update({
            "decoder": "Pillow",
            "decoder_version": pillow_version,
            "width": im.width,
            "height": im.height,
            "mode": im.mode,
            "bits_per_sample": list(tags.get(258, ())),
            "sample_format": list(tags.get(339, ())),
            "compression_code": tags.get(259),
            "pixel_size_degrees": list(scale[:2]) if scale else None,
            "model_tiepoint": list(tie) if tie else None,
            "crs": "EPSG:" + str(epsg) if epsg else "not resolved",
            "geokeys": geo_keys,
            "nodata": tags.get(42113),
            "header_validated": True,
            "pixels_decoded": False,
        })
        if scale and tie:
            west, north = tie[3] - tie[0]*scale[0], tie[4] + tie[1]*scale[1]
            result["bounds_west_south_east_north"] = [
                west, north-im.height*scale[1], west+im.width*scale[0], north]
        try:
            import numpy as np
            if importlib.util.find_spec("tifffile"):
                import tifffile
                data = tifffile.imread(path)
                result["pixel_decoder"] = "tifffile + imagecodecs"
                result["pixel_decoder_version"] = tifffile.__version__
            else:
                data = np.asarray(im)
            finite = np.isfinite(data)
            values = data[finite]
            result.update({
                "pixels_decoded": True,
                "dtype": str(data.dtype),
                "numpy_version": np.__version__,
                "valid_pixel_count": int(finite.sum()),
                "nan_pixel_count": int(np.isnan(data).sum()),
                "infinite_pixel_count": int(np.isinf(data).sum()),
                "missing_or_nonfinite_pixel_count": int(data.size-finite.sum()),
                "minimum_m_per_s": float(values.min()) if values.size else None,
                "maximum_m_per_s": float(values.max()) if values.size else None,
            })
        except Exception as exc:
            result["pixel_decode_limitation"] = str(exc)
            result["minimum_m_per_s"] = None
            result["maximum_m_per_s"] = None
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--audit-existing", action="store_true")
    parser.add_argument("--dependency-directory", type=Path, help="Optional isolated Python dependency directory")
    parser.add_argument("--force", action="store_true", help="Explicitly permit replacing an existing local file")
    args = parser.parse_args()
    if args.dependency_directory:
        sys.path.insert(0, str(args.dependency_directory.resolve()))
    args.directory.mkdir(parents=True, exist_ok=True)
    path = args.directory / FILENAME
    response_metadata = {}
    if not args.audit_existing:
        if path.exists() and not args.force:
            raise SystemExit("File exists. Use --audit-existing to inspect, or --force to re-download.")
        with urlopen(Request(URL, method="HEAD"), timeout=60) as response:
            declared_size = int(response.headers.get("Content-Length", "0"))
            if declared_size <= 0 or declared_size > MAX_BYTES:
                raise SystemExit("Missing or oversized Content-Length; inspect source manually.")
        with urlopen(URL, timeout=120) as response:
            response_metadata = {
                "resolved_url": response.url,
                "content_type": response.headers.get("Content-Type"),
                "content_length": response.headers.get("Content-Length"),
                "last_modified": response.headers.get("Last-Modified"),
                "etag": response.headers.get("ETag"),
            }
            size = 0
            with path.open("wb") as target:
                while block := response.read(1024*1024):
                    size += len(block)
                    if size > MAX_BYTES:
                        raise SystemExit("Download exceeded size limit; partial file retained for inspection.")
                    target.write(block)
            if size != declared_size:
                raise SystemExit("Downloaded length differs from HEAD response; inspect before use.")
    if not path.is_file():
        raise SystemExit("No raster available to audit.")
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024*1024), b""):
            checksum.update(block)
    metadata = {
        "source_id": "GEO-002",
        "title": "Global Wind Atlas 4.0 Somalia wind speed at 100 m",
        "source_url": URL,
        "landing_url": "https://globalwindatlas.info/en/download/gis-files",
        "method_url": METHOD_URL,
        "license": "CC BY 4.0 except explicitly identified third-party layers",
        "license_url": LICENSE_URL,
        "attribution": "Global Wind Atlas 4.0; Technical University of Denmark; World Bank Group; Vortex; ESMAP",
        "retrieval_completed_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat().replace("+00:00","Z"),
        "retrieval_timestamp_basis": "Local downloaded file final-write timestamp; audit time recorded separately",
        "sha256": checksum.hexdigest(),
        "byte_count": path.stat().st_size,
        "filename": path.name,
        "source_url_mutable": True,
        "reference_period": "2008-2017",
        "source_last_modified_header_observed_20260928": "Thu, 12 Jun 2025 14:27:33 GMT",
        "etag_header_observed_20260928": '"a05ee6697800e31456daff7e0335bb4b-2"',
        "status": "downloaded; raster validation status in separate audit JSON",
        "not_claimed": "No resource area mean, power generation, turbine capacity factor, asset coordinate, or national energy potential computed.",
        **response_metadata,
    }
    audit = audit_raster(path)
    for suffix, value in [("provenance", metadata), ("audit", audit)]:
        (path.with_suffix("." + suffix + ".json")).write_text(json.dumps(value, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({"provenance": metadata, "audit": audit}, indent=2, allow_nan=False))

if __name__ == "__main__":
    main()
