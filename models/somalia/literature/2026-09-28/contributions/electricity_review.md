# Electricity: study design and reuse appraisal

The electricity contribution contains 19 records, one of which is assigned to productive uses because it concerns a named water enterprise. Fourteen were inspected through selected full-text sections; five remain at abstract-level access. See [records](electricity_records.json) and [search/access log](electricity_search_log.json).

## Existing modelling work

| Approach | Existing Somalia application | Implication for proposed work |
|---|---|---|
| OnSSET | [E05](https://doi.org/10.3390/en16186489), with related official [E17 report](https://moewr.gov.so/wp-content/uploads/2023/10/Final-report-for-somalias-least-cost-electrification-.pdf) | Compare spatial allocation, timing and demand assumptions before proposing another least-cost access map. |
| OSeMOSYS | [E18 country note](https://doi.org/10.21203/rs.3.rs-480695/v1), linked by [E19 data article](https://doi.org/10.1016/j.dib.2022.108021) | Open starter inputs exist; they are intentionally preliminary and partly regional. |
| LEAP | Official [BUR 2022](https://unfccc.int/sites/default/files/resource/Somalia%20First%20BUR%20report%202022.pdf) and [E11 journal article](https://doi.org/10.1002/ese3.70371) | Compare sector coverage, temporal detail, validation and decision questions; avoid an unqualified first-model claim. |
| HOMER / MATLAB | E01, E02, E04, E08–E10, E13, E14 | Many local designs exist. Their economic results depend on different inputs and constraints. |
| SAM | [E16](https://doi.org/10.30574/wjarr.2024.22.2.1577) | A design study is not confirmation of a constructed plant. |

The national and local studies are complementary, not interchangeable. A geospatial allocation model, annual scenario model and hourly hybrid simulation solve different problems. The review did not execute any of them or establish an absence of SWITCH applications.

## Measurement and demand

Wind studies supply named stations and measurement periods; the solar review supplies a monitored telecom case. Their restricted locations do not validate every national resource cell. Reanalysis should preserve missing-data treatment and distinguish measured heights from extrapolated turbine heights. [E06](https://doi.org/10.1016/j.heliyon.2024.e32500), [E07](https://doi.org/10.1016/j.esd.2024.101514), [E03](https://doi.org/10.1016/j.esr.2023.101108).

Household feasibility loads are often appliance-based. A willingness-to-pay questionnaire measures attitudes, not a metered demand response. The best new load work would combine billing and time-series records with service needs and sampling coverage. [E01](https://doi.org/10.1016/j.rser.2014.07.150), [E13](https://doi.org/10.30880/ijie.2024.16.01.014), [E12](https://doi.org/10.1038/s41598-026-56231-z).

## Reuse decision

Use the papers to identify methods, data owners and assumptions. Reconcile the specific issues in [SOURCE_ISSUES](../SOURCE_ISSUES.md) before numerical reuse. Repository listings were inspected separately: the OnSSET reference resolves as a tree/tag, but a complete country input bundle was not established from its filenames; the two Zenodo concept identifiers resolve to later versions. These version distinctions are recorded in [DATA_LEADS](../DATA_LEADS.md).

The next methodological contribution should be judged by the new evidence or decision insight it provides, not simply by changing optimization software or adding more technologies.
