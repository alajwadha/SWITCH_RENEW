# Somalia power-sector evidence

**Research snapshot: 28 September 2026.** This package contains **100 factual records, 143 historical utility consumption values, 36 preserved missing cells, and 190 planning-parameter records**. Source statements are classified as reported inventory, estimates, plans, tender designs, project results or conflicts. Verification means the cited primary document was opened and the relevant content inspected; it does not mean an independent engineering audit.

The strongest modelling evidence is utility-specific. A current, complete national asset register was not established. None of these research files changes a SWITCH input, chooses a demand baseline, or authorizes a Somalia solve.

## Contents and provenance

| File | Content | Use |
|---|---|---|
| `power_facts.csv` | 100 records with dates, units, geography, source URL, page locator and caveat | Evidence register |
| `power_consumption_history.csv` | 179 source cells, 2015–2024; 143 numeric and 36 missing | Utility consumption research |
| `power_planning_assumptions.csv` | 190 technology, cost and network parameters | Explicit planning assumptions, not observed prices |
| `source_doc_manifest.json` | 15 source documents/pages; 8 downloaded PDF hashes and sizes | Retrieval and version traceability |
| `power_validation.json` | Counts, checks, limitations and output hashes | Verification record |
| `power_build_tables.py` | Deterministic reconstruction from reviewed transcriptions | Reproduce tables; no network or model writes |

Primary-source links and document dates are retained in every data table. The manifest distinguishes document publication, report version and retrieval dates. A missing hash means no binary was retained; it does not indicate a fabricated hash or a successful download. The July 2025 World Bank mission PDF was readable through the web index, but direct download returned HTTP 404 on retrieval day.

## Selected verified records

| Evidence | Value | Date / meaning | Primary source and locator |
|---|---:|---|---|
| GECO installed capacity | 2.4 MW: 2 diesel + 0.4 PV | January 2025 draft baseline; South Galkacyo | [GECO ESIA](https://moewr.gov.so/wp-content/uploads/2025/02/GECO-ESIA.pdf), PDF p12 |
| NEPCO installed capacity | 5.4432 MW: 4.9432 diesel + 0.5 PV | January 2025 draft baseline; North Galkacyo | [NEPCO ESIA](https://moewr.gov.so/wp-content/uploads/2025/02/NEPCO-ESIA.pdf), PDF p13 |
| BEC-Baidoa installed capacity | 8.648 MW: 7.648 diesel + 1 PV | January 2025 draft baseline | [Baidoa ESIA](https://moewr.gov.so/wp-content/uploads/2025/02/BEC-BAIDOA-ESIA.pdf), PDF p12 |
| Indicative electricity tariff | About USD 0.60/kWh | 2025 narrative benchmark; not utility tariff schedule | [World Bank DPF2](https://documents1.worldbank.org/curated/en/099071725125534548/pdf/BOSIB-97a425a9-97c2-4c6a-9909-b8c80e38ad3d.pdf), printed p17 / PDF p24 |
| SESRP contracted solar and storage | 50 MWp + 130 MWh | Implementation stages in March 2026; commissioning not established | [Restructuring paper](https://documents1.worldbank.org/curated/en/099032626073010531/pdf/P173088-db056fb6-ff05-4619-bc8c-69938418e4de.pdf), printed p1 / PDF p6 |
| SESRP renewable capacity constructed | 8.10 MW | Actual project result dated 28 February 2026; not national stock | [Restructuring paper](https://documents1.worldbank.org/curated/en/099032626073010531/pdf/P173088-db056fb6-ff05-4619-bc8c-69938418e4de.pdf), printed p7 / PDF p12 |
| Public institutions commissioned | 120 health; 173 education | March 2026 project narrative | [Restructuring paper](https://documents1.worldbank.org/curated/en/099032626073010531/pdf/P173088-db056fb6-ff05-4619-bc8c-69938418e4de.pdf), printed p1 / PDF p6 |
| Proposed Bosaso increment | 7.15 MWp DC / 5.5 MW AC; BESS 3 MW / 11 MWh | March 2025 draft design; not operating stock | [Bosaso ESIA](https://moewr.gov.so/wp-content/uploads/2025/05/Final-Bosaso-ESIA-Report-20250324-Clean-ver-4-2.pdf), printed p44 / PDF p91 |

ESIA inventory statements are provisional utility aggregates. They lack unit commissioning dates, retirement schedules, audited availability and complete AC/DC definitions. Do not add a new project to its company total without checking overlap.

## Historical consumption

The [June 2025 government plan](https://moewr.gov.so/wp-content/uploads/2025/07/Somalia-Generation-and-Transmission-Plan-2025-MoEWR.pdf), pp36–37, Tables 3-7 through 3-10, supplies the extracted annual utility history. It describes field collection from ESPs during 2025. It does not identify, cell by cell, measured versus estimated values. The extraction therefore uses `reported_history_method_unresolved`.

All 179 cells remain: missing numeric values are empty, while original blanks, single dashes and double dashes are distinguished. No interpolation, extrapolation, loss adjustment or growth assumption was applied. Utility IDs distinguish Baidoa's BEC/BECO from Mogadishu's BECO. SOOL and Shebelle service areas remain unresolved. MPS area values must not be added to its Mogadishu aggregate until overlap is resolved.

These annual MWh values provide candidate utility energy totals; they do not provide hourly load profiles, peaks, unmet demand or a complete national demand total.

## Project designs and status

The [July 2025 World Bank mission](https://documents1.worldbank.org/curated/en/099110425105030846/pdf/P173088-fa99e7da-f0c3-4bcc-a248-69768f01f7c1.pdf), p8, reports five proposed solar/BESS packages. The facts file preserves their capacities and bid/package costs separately. Page15 distinguishes current technical-loss estimates from targets. Procurement-stage capacities are not labelled commissioned.

The [March 2026 restructuring paper](https://documents1.worldbank.org/curated/en/099032626073010531/pdf/P173088-db056fb6-ff05-4619-bc8c-69938418e4de.pdf), printed p3, explicitly removes the proposed 132 kV Mogadishu/Hargeisa subtransmission scope. Its June 2028 closing date and revised capacity target are proposals in this document; subsequent approval was not established. Project MWh indicators have no explicit annual denominator and must not be repurposed as annual national supply.

The [September 2026 World Bank feature](https://www.worldbank.org/en/news/feature/2026/09/09/reliable-electricity-is-helping-communities-across-somalia) provides narrative context. Its broad beneficiary and institution figures are not a plant commissioning register. Technical status relies on dated project documents.

## Conflicts and exclusions

| Issue | Research treatment |
|---|---|
| Government plan p27 diesel total | Reported 95,186 kW; visible regional entries sum **83,586 kW**, a difference of **11,600 kW**. Eastern entry is blank. Quarantined. |
| Government plan p27 LV total | Reported 2,225 km; entries sum 2,219 km. Quarantined. |
| BECO 175 MW | [Dayniile ESIA](https://moewr.gov.so/wp-content/uploads/2025/02/BECO-DAYNIILE-POWER-PLANT-ESIA.pdf), PDF p14, includes BESS in its total. Not generation-only MW or site-only capacity. |
| Loss definitions and vintage | Declaration tables do not consistently separate technical/commercial losses. Baidoa 70% conflicts with a later 33% technical estimate; definitions also differ. Neither silently replaces the other. |
| GECO tender design | [February addendum](https://moewr.gov.so/wp-content/uploads/2025/03/Addendum-No2-for-GECO-RFB.pdf), p1: 3.5 MWp + 7 MWh; July mission: 3.42 MWp + 5 MWh. Final contract scope unresolved. |
| Jazeera solar unit | [Tender addendum](https://moewr.gov.so/wp-content/uploads/2025/03/Jazeera-Addendum-001-Submission-Extension-Jazeera-Power-Plant-BECO-Mogadishu.pdf), p1, prints “MWp(AC)”. Kept as an ambiguous source unit. |
| Bosaso draft/final label | Ministry filename says Final; cover and revision sheet say draft, dated 23 March 2025. Design-stage evidence only. |
| Bosaso internal design changes | Printed p45 gives a 19.2 km ring; executive summary p xvi gives 21.2 km. Annual solar yield also differs between pp xv and44. These are not selected as defaults. |
| Cost-table ambiguities | LNG-labelled 300 MW CCGT row has LFO fuel; hydro row has 80% in the heat-input column. Preserved and flagged, not repaired. |
| Website counters | Zero-valued ministry counters and unrelated regulator template figures were excluded. Missing/placeholder content is not evidence of zero infrastructure. |
| AfDB appraisal | Official Bosaso appraisal could not be opened because of access protection. Search snippets and secondary copies were not promoted to verified facts. The accessible ministry ESIA is a different, earlier source. |

## Model-use boundaries

The planning-parameter file covers thermal technologies, PV, wind, four-hour BESS and network equipment. Cost base year is not specified; transmission estimates reference the Ethiopia–Somalia feasibility study. They are candidate sensitivities, not observed Somalia quotations. A battery's MW, MWh and USD/kW must remain separate.

For a reviewed SWITCH model, further evidence is needed for unit-level generation, delivered fuel prices, efficiencies and availability, commissioned battery usable energy, network endpoints/ratings, utility boundary geometry, interconnector operating status, hourly demand and consumption metering definitions. Kenya input structure can guide this checklist; Kenyan values were not substituted.

The [Electricity Act announcement](https://moewr.gov.so/ova_doc/somalia-electricity-act/) records signing on 8 March 2023, and the [tariff/licensing announcement](https://moewr.gov.so/ova_doc/tariff-and-licensing-regulations/) records cabinet approval on 13 July 2023. These establish policy events, not current utility tariff schedules.

## Verification and work log

1. Read the research/PDF skills and approved repository research workflow; retained evidence-only scope.
2. Opened primary ministry and World Bank sources; downloaded PDFs where accessible; retained hashes and versions.
3. Checked consumption and cost tables against rendered pages, plus key ESIA inventory and 2026 project-result pages.
4. Transcribed data with original units, missingness and explicit evidence classes. Kept plans separate from operating capacity.
5. Validated record counts, unique IDs/utility-years, required source locators, nonnegative consumption and conflicting inventory arithmetic. Checks do not certify source truth.

Raw PDF, full-text and PNG caches are **local review material**. Redistribution licenses were not established. Publish original factual tables, original analysis, the script and source manifest; link to the publisher's documents. Do not commit cached source PDFs, full extracted text or rendered pages by default. No Git operation or external message was performed by this research subtask.
