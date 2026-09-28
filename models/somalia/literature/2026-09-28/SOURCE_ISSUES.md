# Source issues and reuse decisions

These are specific checks, not a blanket judgment on an author or institution. **Retain the original statement and resolve the affected quantity before reuse.** A verified publication can still contain an unverified or inconsistent number. Additional limitations are recorded per item.

| Record | Check and source locator | Decision |
|---|---|---|
| [E11](https://doi.org/10.1002/ese3.70371) | Abstract / section 5.1: 133.2 GWh in 2020 to 1,814.2 in 2050 implies **9.0953%** compound annual growth over 30 years, rather than 1.88%. Table 4 diesel rows sum to **346.25 MW**, versus printed 302.35. Section 5.2.2 uses GW where earlier capacity discussion uses MW. | Quarantine these quantities. Arithmetic identifies inconsistencies; it does not reveal which model input is correct. |
| [E02](https://doi.org/10.3390/pr10040667) | PDF p.7 says approximately 26 and later 2.6 kWh/household/day, with 2,612 kWh/day for 100 households. Page visually inspected. | Reconcile load and units; do not treat the assumed grid tariff as a measured contract. |
| [E01](https://doi.org/10.1016/j.rser.2014.07.150) | Section 2.1 states 1,283 kWh/day; Table 1 totals 1,301. | Preserve the discrepancy and synthetic-load status. |
| [E06](https://doi.org/10.1016/j.heliyon.2024.e32500) | Tables 5–10 captions specify W/m²; header/prose use kW/m². Table2 rates WT7 at1,500kW; Table11 reports6.04GWh and CF0.29 at Xumbo Weyne. Eq33 gives1,500 ×8,760 ×0.29 /1,000,000 = **3.8106GWh**. Rounding cannot explain the discrepancy. | Resolve power-density units and turbine-output calculations; do not adopt the disputed AEP or derived economic results. Original station data remain a useful request lead. |
| [E07](https://doi.org/10.1016/j.esd.2024.101514) | Abstract p1 prints4494/6203m/s; Table1 p5 reports4.49/6.20m/s. Visual inspection confirms this is in the PDF. Table2 p6 labels rotor diameter cm for values90–172. | Quarantine the printed abstract magnitudes; obtain raw observations and verify turbine dimensions independently. Do not silently repair the source or infer that its underlying measurements are false. |
| TF014 | The September2025 NDC had already been inspected in the earlier data package: baseline54.3 versus53.4MtCO2e and BAU/base-year wording conflicts, printed pp8,17,40. | Catalogue access status reconciled with that selected full-text review; preserve [C05](../../data/2026-09-28/CONFLICTS.md). Policy targets remain distinct from validated baseline inputs. |
| [E16](https://doi.org/10.30574/wjarr.2024.22.2.1577) | Section 1.1 labels Mogadishu latitude 2.05S. | Check the actual SAM weather/location input; the text alone cannot show whether the simulation used the same sign. |
| [COOK05](https://doi.org/10.1007/s43621-026-03673-0) | Section 2.2 includes paraffin in “modern” fuel; section 3.3/Table 3 reports urban OR 5.211 with CI 1.410–1.891. | Modern is not synonymous with SDG clean cooking. Check whether intervals were left on the log-odds scale; do not silently repair. |
| [COOK02](https://doi.org/10.1177/11786302251315893) | Fuel coding puts kerosene in the “solid” category. | Reconcile definitions, denominators and weights with the original survey. |
| [COOK12](https://doi.org/10.5772/intechopen.99365) | Abstract baseline forest area 87,294 ha versus section 3.1 area 8,729,400 ha: **100×** difference. | Quarantine area benchmarks; forest loss is not itself attribution to charcoal. |
| [PU02](https://doi.org/10.1007/s10098-024-02741-1) | Publisher and Crossref link [correction 10.1007/s10098-024-02797-z](https://doi.org/10.1007/s10098-024-02797-z). Its body was inaccessible. | Correction existence is verified; effect on results remains unknown. Obtain corrected text before numerical use. |
| PU04 | BAARIS report pp.27/30: farm-area units change between square metres and hectares; Bari chart total 103 differs from 43 men plus 15 women. | Resolve unit and denominator conflicts. Original source and locator in the catalogue. |
| PU07 | Fish-price baseline, Table 4 versus accompanying gender narrative. | Do not adopt the disputed gender distribution without source clarification. |
| PU08 | Healthcare brief has inconsistent multi-country facility totals. | Keep Somalia row and standardized load assumptions distinct; do not aggregate disputed totals. |
| TF016 | Logistics Cluster report p4: identical price pairs are associated with differing displayed percentage increases. | Recalculate only as a labeled derived check; do not relabel the table as a national fuel-price series. |

The calculations for E11 and COOK12 are independently repeated in [validation.json](validation.json); formulas are in the validation script. Links and precise original-file URLs for institutional records are in [PUBLICATIONS](PUBLICATIONS.md).

## Bibliographic and independence checks

- E13's Crossref author array includes institutional affiliations as authors. The six-person list on the publisher PDF is used instead. Its PDF and Crossref differ on the April 2024 day of online publication; year is unambiguous.
- E02/E10/E16 discovery-service author lists were incomplete or inconsistent. Publisher/DOI registration metadata replaced them.
- E09 is online 2024 with a 2025 issue; E11 is online 2025 with a 2026 issue; COOK01 is in a 2026 issue with a December 2025 landing date. Those differences are explicitly retained.
- COOK12's publisher page gives 15 October 2021, while Crossref registers 16 February 2022. The catalogue uses the primary page's date and records the discrepancy.
- TF012's cover dates the CPSD June 2024; its 2025 hosting path does not change the publication year. E17 is dated 2021 in the subsequent authors' bibliography, despite a 2023 hosting path.
- E05/E17 share the SEAP foundation. E18/E19 are related starter-kit outputs. SIHBS/SHDS derivative articles reuse surveys. These are multiple publications, not independent replications of the underlying observations.
- E16's Zenodo copy was deduplicated against its journal DOI. Preprints remain explicitly labeled.
- DOI registry errors for PU01 and PU15 are preserved; a Crossref404 is not proof that an identified publication is nonexistent. Their primary document/author-deposit checks are retained.
- PU16's PDF cover orders authors Kassa, Elema, Redding; EarthArXiv/Crossref order Kassa, Redding, Elema. The catalogue retains the inspected PDF order and records the metadata conflict.
- PU01's raw load series was not obtained and a public download was not identified. The earlier word “unavailable” was too strong. E06 explicitly offers data on request. Exact request routes and restrictions are in [author/data requests](AUTHOR_DATA_REQUESTS.md).

## Novelty claims

The official 2022 BUR predates E11 and explicitly uses LEAP. E11's claim is qualified as a comprehensive electricity-sector application; the earlier report does not automatically disprove every part of that narrower claim. A new proposal should compare the actual scope and validation of both, alongside OnSSET/OSeMOSYS, rather than claim a first national model.

## Boundary of verification

This review checked source identity, inspected accessible content and tested selected contradictions. It did not audit every calculation, underlying dataset, legal provision or correction/retraction service. “No problem detected” is not a certification of numerical correctness.
