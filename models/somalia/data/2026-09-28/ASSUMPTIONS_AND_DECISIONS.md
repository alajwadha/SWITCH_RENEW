# Assumptions and decisions

| ID | Decision or assumption | Reason and consequence | Status |
|---|---|---|---|
| D01 | Treat this as evidence acquisition, not baseline model construction | The user requested verified data; sources do not yet establish a consistent hourly load and complete operational fleet | Applied |
| D02 | Use Kenya only to identify fields and file relationships | Kenya's costs, loss rates, reserve margin, financing and time design are not Somalia observations | Applied; no transfer |
| D03 | Preserve source geography labels and API `SOM` coverage | Different reports and boundary versions cover different populations or service areas | Applied; final model zones pending |
| D04 | Retain conflicting values separately | Arithmetic inconsistencies and definition changes cannot be fixed by silent averaging | Applied; see conflict register |
| D05 | Use 2025 hourly weather plus 2001–2025 daily history | A completed year supplies chronology; the longer record reveals resource variability | Research sampling choice only |
| D06 | Use ten rounded city query coordinates | Makes regional screening reproducible without inventing asset locations | Analyst-selected approximation; not approved siting |
| D07 | Keep official estimates, survey results and reanalysis distinct | Source authority does not turn estimation into field measurement | Applied in metadata and evidence types |
| D08 | Preserve market fuel price fields and modeled estimates separately | Sparse observations and publisher aggregate otherwise create false coverage | Applied; utility delivered prices pending |
| D09 | Do not convert tariff into generation cost or LCOE into overnight cost | They contain different cost boundaries and financing assumptions | Applied |
| D10 | Keep project announcements, contracts and commissioning distinct | Capacity under implementation cannot serve load in a historical baseline | Applied |
| D11 | Keep large/rights-unclear documents and rasters outside Git | Publish factual extracts, exact URLs, checksums and retrieval routes; licensed compact datasets are included | Applied |
| D12 | No national WACC, reserve margin, fuel heat rate, outage rate or load shape is imputed | These would materially control investment outcomes | Pending evidence/scenario decision |

No decision in this collection fixes a future planning horizon, simulation resolution, project inclusion or study contribution. Those remain choices for the initial research brief, supported by the evidence now gathered.
