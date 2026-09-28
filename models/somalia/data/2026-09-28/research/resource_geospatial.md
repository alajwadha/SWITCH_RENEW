# Somalia renewable-resource, climate and geospatial evidence

**Research checked: 28 September 2026.** This package catalogs 30 primary-source datasets for resource assessment, geographical reporting, infrastructure screening and environmental constraints. It records access and licensing limits rather than treating every public map as reusable data.

**One raw dataset was acquired and numerically audited in this research branch:** the Global Wind Atlas Somalia 100 m wind-speed raster. The other 29 entries are source/metadata research, with download links where confirmed. Downloads by other branches of the Somalia project must be reconciled with their own manifests before changing this count. No hydropower potential, national renewable energy potential, electricity demand or plant capacity factors were inferred here.

Machine-readable metadata, units, periods, licenses and caveats are in [resource_catalog.csv](resource_catalog.csv). Source IDs below match that file.

## Evidence and acquisition table

| ID | Dataset / first-party reference | Resolution / period | Verified acquisition state | Main role |
|---|---|---|---|---|
| GEO-001 | [Somalia solar GIS / Solargis](https://solargis.com/resources/free-maps-and-gis-data?locality=somalia) | Irradiation ~250 m; PVOUT ~1 km; long-term monthly/annual | Direct country ZIP links found; package not downloaded here | Solar resource screening |
| GEO-002 | [Global Wind Atlas 4](https://globalwindatlas.info/en/about/method) | ~250 m; 2008–2017; 100 m height acquired | Raster downloaded, hashed and numerically decoded | Wind resource screening |
| GEO-003 | [ERA5 single levels](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels) | 0.25° hourly; 1940–present | Metadata verified; CDS account/request needed | Multiyear weather profiles |
| GEO-004 | [ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land) | 0.1° hourly; 1950–present | Metadata verified; CDS account/request needed | Land climate and water balance |
| GEO-005 | [CHIRPS v3](https://chc.ucsb.edu/data/chirps3) | 0.05°; 1981–present | Public archive directory verified | Rainfall and drought variability |
| GEO-006 | [NASA IMERG Final V07B](https://gpm.nasa.gov/data/directory) | 0.1°; half-hourly; January 1998–present | Product/archive verified; access registration may apply | Rainfall extremes |
| GEO-007 | [OCHA COD / SODMA mirror](https://sodma-dev.okfn.org/dataset/cod-ab-som) | 18 regions, 91 districts; January 2025 | Metadata verified; direct file link failed in web retrieval | Preferred current reporting reference |
| GEO-008 | [geoBoundaries Somalia API](https://www.geoboundaries.org/api/current/gbOpen/SOM/ALL/) | Level-specific 2015/2021/2022 sources | API metadata verified; parent handles geometry download | Explicit alternate boundary set |
| GEO-009 | [OSM / Geofabrik Somalia](https://download.geofabrik.de/africa/somalia.html) | Vector; 26 September 2026 snapshot | Dated PBF link verified | Roads and mapped infrastructure |
| GEO-010 | [WorldPop Global 2](https://hub.worldpop.org/project/categories?id=3) | 100 m; annual 2015–2030 | Exact Somalia 2025 TIFF link verified | Population distribution context |
| GEO-011 | [GHS-POP R2023A](https://data.jrc.ec.europa.eu/dataset/2ff68a52-5b5b-4a22-8f40-c41da8332cfe) | 100 m / 1 km; 1975–2030 | Metadata/download portal verified | Alternative spatial allocation |
| GEO-012 | [GHS-BUILT-S R2023A](https://data.jrc.ec.europa.eu/dataset/9f06f36f-4b11-47ec-abb0-4f8b7b1d72ea) | 2018 anchor 10 m; modeled time series | Metadata/download portal verified | Built and non-residential geography |
| GEO-013 | [ESA WorldCover 2021 v200](https://esa-worldcover.org/en/data-access) | 10 m; 2021 | DOI and anonymous S3 path verified | Land-cover screening |
| GEO-014 | [Dynamic World V1](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1) | 10 m; 2015–present | Earth Engine metadata verified; export not performed | Recent land-cover sensitivity |
| GEO-015 | [Copernicus GLO-30](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM) | ~30 m DSM; pin release | Provider and [public host](https://registry.opendata.aws/copernicus-dem/) verified | Terrain/slope screening |
| GEO-016 | [HydroRIVERS v1](https://www.hydrosheds.org/products/hydrorivers) | Vector from 15-arcsecond hydrography | Africa ZIP link verified | River network topology |
| GEO-017 | [HydroBASINS v1c](https://www.hydrosheds.org/products/hydrobasins) | 12 nested basin levels | Africa ZIP link verified | Upstream drainage areas |
| GEO-018 | [SWALIM river archive](https://snrfa.faoswalim.org/stations/) | Stations; daily where available | Portal verified; export/license/quality unresolved | Observed hydrology |
| GEO-019 | [SWALIM climate stations](https://climseries.faoswalim.org/station/) | Stations; variable coverage | Station groups verified; export/license unresolved | Local weather/groundwater evidence |
| GEO-020 | [SWIMS water sources](https://swims.faoswalim.org/dashboard/view) | Point inventory; record-specific dates | Portal categories verified; export unresolved | Water-source context |
| GEO-021 | [SWALIM drought index](https://cdi.faoswalim.org/index/cdi) | District time series; method changes in 2021 | Method notice and CSV interface verified | Regional drought stress |
| GEO-022 | [SWALIM flood monitoring](https://frrims.faoswalim.org/) | Station, reach and forecast layers | Live portal verified; underlying files not acquired | Flood events and bank failures |
| GEO-023 | [JRC Surface Water v1.5](https://global-surface-water.appspot.com/download) | 30 m; summary 1984–2024 | Updated version notes verified | Water masks and variability |
| GEO-024 | [Protected Planet Somalia](https://www.protectedplanet.net/en/country/SOM) | September 2026; point records | Summary/terms verified; no restricted data copied | Conservation evidence gaps |
| GEO-025 | [JRC/CEMS river flood hazard](https://data.jrc.ec.europa.eu/dataset/jrc-floods-floodmapgl_rp50y-tif) | ~90 m; v2.1.2 January 2026 files | Public directory/README verified | Return-period flood exposure |
| GEO-026 | [Aqueduct Floods v2](https://www.wri.org/data/aqueduct-floods-hazard-maps) | Baseline 2010; 2030/2050/2080 scenarios | Research/catalog pages verified | Future river/coastal sensitivity |
| GEO-027 | [NASA Black Marble VNP46A2](https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP46A2) | ~500 m daily; 2012–present | Collection 2 archive verified | Nighttime activity cross-check |
| GEO-028 | [SoilGrids 2.0](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs.html) | 250 m; six depth intervals | Documentation/WebDAV verified | Soil and land sensitivity |
| GEO-029 | [GEBCO 2026](https://www.gebco.net/data-products/gridded-bathymetry-data) | 15 arcseconds; 2026 release | Release/subset archive verified | Coastal terrain context |
| GEO-030 | [UNOSAT November 2023 floods](https://sodma-dev.okfn.org/dataset/floods-in-somalia-november-2023) | Event polygons; sensor-dependent | UNOSAT ZIP link verified; file not retrieved | Observed flood-event validation |

## Acquired wind raster: auditable facts

The [provider download interface](https://globalwindatlas.info/en/download/gis-files) exposed this exact link after selecting Somalia, WIND-SPEED and 100 m:

[Somalia wind speed at 100 m](https://globalwindatlas.info/api/gis/country/SOM/wind-speed/100)

| Check | Observed result |
|---|---|
| File | `som_wind-speed_100m_gwa4_20260928.tif` |
| Retrieval completion | 2026-09-28 16:34:15 UTC; based on local completed-file timestamp |
| Byte count | 54,469,571 |
| SHA-256 | `9d2dd6013ab0e2da38d420f861b83ca8b26a34150b86bbb6193c011766fc98de` |
| Source response | HTTP 200; image/tiff; last-modified 12 June 2025 |
| Raster dimensions | 5,399 columns × 6,668 rows; float32 |
| CRS / spacing | EPSG:4326; 0.0025° × 0.0025° |
| Extent, west/south/east/north | 40.96875°, −3.12375°, 54.46625°, 13.54625° |
| Finite / NaN / infinite pixels | 19,053,180 / 16,947,352 / 0 |
| All finite product values | Minimum 2.255723953 m/s; maximum 16.345039368 m/s |
| Geographic limit | Delivered country product includes offshore cells; no national-land clipping performed |
| Not computed | Area-weighted mean, turbine output, capacity factor or developable potential |

These extrema describe the **delivered resource product**, including offshore coverage. They are not an onshore Somalia range or a measure of electricity generation. The reference wind climatology is 2008–2017; a 2025 file timestamp is not a new measurement period. The [GWA method](https://globalwindatlas.info/en/about/method) describes ERA5 forcing, WRF downscaling to 3 km, and finer microscale output. The [terms](https://globalwindatlas.info/en/about/TermsOfUse) identify CC BY 4.0 except specified exceptions and request attribution to DTU, World Bank, Vortex and ESMAP.

The raster is retained locally under `raw/global_wind_atlas/`. Small provenance and audit JSON files plus `retrieve_gwa.py` document retrieval and repeatable verification. TIFF metadata was inspected using Pillow, and pixels independently decoded using tifffile 2026.9.20, imagecodecs and NumPy 2.3.5. Pillow's own TIFF decoder lacked ZSTD support; the isolated additional decoder resolved that limitation. No changes were made to the bundled Python environment.

## Decisions needed before combining sources

**Boundary vintages must remain separate.** Current COD metadata lists 91 districts; geoBoundaries ADM2 lists 118. The latter has a 2022 GPEI source, while its ADM1 source is 2015 OpenStreetMap. Operational zones must not be relabeled administrative districts. Record source-native IDs and develop an explicit crosswalk; administrative reporting regions do not establish electrical load zones. [COD metadata](https://sodma-dev.okfn.org/dataset/cod-ab-som), [geoBoundaries metadata](https://www.geoboundaries.org/api/current/gbOpen/SOM/ALL/).

**Some observed hydrology needs source correction before ingestion.** The river archive table appears to reverse latitude and longitude labels, and its maximum-flow column has a questionable unit label. Gauge failures and missing records are visible. Confirm coordinate order against station maps and obtain discharge units/rating-curve information; never convert stage in metres directly into flow or hydropower. [River archive](https://snrfa.faoswalim.org/stations/).

**Conservation data are a substantive gap.** The September 2026 country page reports 21 protected areas, all represented as points and none as polygons. Do not manufacture exclusion footprints from these points or reported areas. [Country profile](https://www.protectedplanet.net/en/country/SOM). Protected Planet's [legal terms](https://www.protectedplanet.net/en/legal) restrict redistribution, including derivative data. This repository should retain the citation and evidence-gap description unless separate permission supports publishing the data.

**Climate series are not interchangeable observations.** ERA5/ERA5-Land share forcing, and CHIRPS v3 daily variants use ERA5 or IMERG timing. These dependencies matter when comparing products. [CHIRPS documentation](https://chc.ucsb.edu/data/chirps3), [ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land). SWALIM stopped using NDVI in its drought-index calculation from early 2021; account for that structural change when comparing drought severity across years. [CDI notice](https://cdi.faoswalim.org/index/cdi).

**Population, built area and radiance are proxies.** They can help locate activity and check spatial allocation, but they do not provide MW demand, hourly demand, customer connection counts or reliable utility boundaries. Preserve each provider's population estimate versus projection distinction, quality masks and gap-filling flags. [WorldPop](https://hub.worldpop.org/project/categories?id=3), [Black Marble](https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP46A2).

## Exact acquisition leads

1. **Solar:** the source page exposes [average daily totals ZIP](https://cms.solargis.com/file?url=download/Somalia/Somalia_GISdata_LTAym_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF.zip&bucket=globalsolaratlas.info) and [yearly/monthly totals ZIP](https://cms.solargis.com/file?url=download/Somalia/Somalia_GISdata_LTAym_YearlyMonthlyTotals_GlobalSolarAtlas-v2_GEOTIFF.zip&bucket=globalsolaratlas.info). Select the unit convention once and preserve package metadata. The Solargis page labels these downloads CC BY-SA 4.0, while the [GSA FAQ](https://globalsolaratlas.info/support/faq) describes CC BY 4.0; keep the package-specific notice and resolve that discrepancy before relicensing derivatives.
2. **Current boundaries:** the mirror links [COD shapefile ZIP](https://data.humdata.org/dataset/ec140a63-5330-4376-a3df-c7ebf73cfc3c/resource/cc9ada4b-aee2-4745-ab59-98e7ef4ce037/download/som_adm_ocha_20250108_ab_shp.zip) and [gazetteer](https://data.humdata.org/dataset/ec140a63-5330-4376-a3df-c7ebf73cfc3c/resource/2bb93a9e-bb50-42e3-bd30-5b0f86b16ee5/download/som_admgz_ocha_20250108.xlsx). These failed in this branch's web retrieval; parent acquisition may use another verified path. Do not mark the file validated from the metadata alone.
3. **Population:** [2025 constrained Somalia WorldPop TIFF](https://data.worldpop.org/GIS/Population/Global_2015_2030/R2025A/2025/SOM/v1/100m/constrained/som_pop_2025_CN_100m_R2025A_v1.tif). Inspect raster units, missing cells, extent and country-total consistency.
4. **Land and terrain:** acquire only tiles intersecting the chosen country geometry and buffer. WorldCover anonymous prefix is `s3://esa-worldcover/v200/2021/map`; terrain access is described in the [GLO-30 public-host readme](https://copernicus-dem-30m.s3.amazonaws.com/readme.html). Record tile IDs and vertical datum; derive slope in a suitable metric coordinate system.
5. **Flood hazard:** begin with the [JRC/CEMS tile index](https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-GLOFAS/flood_hazard/tile_extents.geojson), then retrieve relevant return periods and masks from the [public directory](https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-GLOFAS/flood_hazard/). The [README](https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/CEMS-GLOFAS/flood_hazard/README.txt) documents v2.1.2 and artifact handling. Simulated depths and satellite-observed event extents must remain separate evidence types.
6. **Station data:** pursue authorized exports from SNRFA, ClimSeries, SWIMS and CDI. Capture station metadata, units, instrument dates, quality flags and applicable reuse permission before public redistribution.
7. **Recent/version-sensitive products:** use the documented v1.5 water corrections and [known issues](https://global-surface-water.appspot.com/download); use [SoilGrids WebDAV](https://files.isric.org/soilgrids/latest/data/) or WCS while its REST service is paused. Check the [Copernicus 10 m land-cover successor](https://land.copernicus.eu/en/products/global-dynamic-land-cover/land-cover-2020-raster-10-m-global-annual) when choosing a final land-cover vintage; do not assume announced future years are already downloadable.

Large global files should be retained in appropriate data storage with checksums and exact retrieval scripts. Publishing a catalog is not equivalent to publishing the raw data or confirming that a model input is ready.

## Required processing record

For every acquired file, retain source URL, resolved URL if redirected, retrieval UTC, source release/reference period, SHA-256, bytes, license notice and an immutable source identifier. Raw bytes remain unchanged. Derived artifacts need a reproducible transformation, software versions, units, input checksums, coordinate reference system, aggregation rule and a clear observation/proxy/scenario label.

Before model ingestion, verify raster dimensions/CRS/nodata or vector validity/IDs, country intersection, unit conversions and timestamps. Use area weights for geographic-grid averages, preserve categorical class resampling, avoid adding overlapping inventory totals, and distinguish no-data from zero. A national estimate should describe whether it includes Somaliland, disputed boundaries, islands and offshore areas according to the actual source geometry.

The data gathered here support the approved Somalia research phase. They do not authorize a solved model, residential-demand construction, hydrogen/desalination modules or new offshore projects.

## Numbered work log

1. Read approved research and Somalia repository rules; confined outputs to research staging and subsequently authorized raw wind retrieval.
2. Checked 30 primary datasets and their exact provider pages, versions, coverage and reuse conditions. Cataloged links separately from downloads.
3. Recorded COD/geoBoundaries administrative conflicts, SWALIM coordinate/unit issues, drought-index changes, restricted point-only conservation evidence and version-specific climate/water caveats.
4. Verified the Somalia GWA 100 m endpoint through the provider's rendered download UI; downloaded the 54.5 MB TIFF; saved source/hash/time/license sidecar.
5. Audited georeferencing and all numeric pixels; resolved missing ZSTD decoder using dependencies installed in a temporary workspace target. Produced reproducible acquisition/audit script and JSON.
6. Prepared the 30-row CSV and this report. No GitHub changes, capacity-factor calculation, demand estimate or model solve were performed by this research branch.

