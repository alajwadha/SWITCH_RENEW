"""Rebuild reviewed Somalia power evidence tables. No network and no model adoption.

Numeric transcriptions were checked against cited primary documents on 2026-09-28.
Raw documents are local review caches; redistribution rights remain unestablished.
"""
from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parent
RETRIEVED = "2026-09-28"
SOURCES = {
    "plan": dict(title="Optimized Cost Electricity Generation and Transmission Development Plan for Somalia", publisher="Federal Ministry of Energy and Water Resources (MoEWR)", publication_date="2025-06", url="https://moewr.gov.so/wp-content/uploads/2025/07/Somalia-Generation-and-Transmission-Plan-2025-MoEWR.pdf", local_filename="power_source_moewr_ocedp_2025.pdf", version="June 2025 report; government landing page dated 2025-07-08"),
    "pid": dict(title="Somali Electricity Sector Recovery Project (P173088): Appraisal Project Information Document", publisher="World Bank", publication_date="2021-10-08", url="https://documents1.worldbank.org/curated/en/917771634027301072/pdf/Project-Information-Document-Somali-Electricity-Sector-Recovery-Project-P173088.pdf", local_filename=None, version="Prepared/updated 2021-10-08; public PDF inspected with web tool"),
    "dpf": dict(title="Somalia Second Inclusive Growth Development Policy Financing", publisher="World Bank", publication_date="2025-07-11", url="https://documents1.worldbank.org/curated/en/099071725125534548/pdf/BOSIB-97a425a9-97c2-4c6a-9909-b8c80e38ad3d.pdf", local_filename=None, version="2025-07-11 report; public PDF inspected with web tool"),
    "mtr": dict(title="SESRP Mid-Term Review and ASCENT Implementation Support Mission: Aide-Memoire, July 7-25 2025", publisher="World Bank", publication_date="2025-11-04", url="https://documents1.worldbank.org/curated/en/099110425105030846/pdf/P173088-fa99e7da-f0c3-4bcc-a248-69768f01f7c1.pdf", local_filename=None, version="Mission July 7-25 2025; disclosed November 4 2025; web cached PDF full text inspected; direct download returned 404 on retrieval date"),
    "restructure": dict(title="SESRP (P173088): Restructuring Paper RES01687", publisher="World Bank", publication_date="2026-03-26", url="https://documents1.worldbank.org/curated/en/099032626073010531/pdf/P173088-db056fb6-ff05-4619-bc8c-69938418e4de.pdf", local_filename="power_source_wb_sesrp_restructuring_2026.pdf", version="Public document catalog date 2026-03-26; proposed restructuring, not independent proof of its subsequent approval"),
    "geco": dict(title="Draft ESIA: Proposed Hybrid Power Plant for GECO, Gaalkacyo", publisher="MoEWR; Horizon Developments", publication_date="2025-01-30", url="https://moewr.gov.so/wp-content/uploads/2025/02/GECO-ESIA.pdf", local_filename="power_source_GECO-ESIA.pdf", version="Draft revision 04, submission 2025-01-30"),
    "nepco": dict(title="Draft ESIA: Proposed Hybrid Power Plant for NEPCO, Gaalkacyo", publisher="MoEWR; Horizon Developments", publication_date="2025-01-30", url="https://moewr.gov.so/wp-content/uploads/2025/02/NEPCO-ESIA.pdf", local_filename="power_source_NEPCO-ESIA.pdf", version="Draft revision 04, submission 2025-01-30; page headers retain 2024"),
    "bec": dict(title="Draft ESIA: Proposed Hybrid Power Plant for BEC-Baidoa", publisher="MoEWR; Horizon Developments", publication_date="2025-01-30", url="https://moewr.gov.so/wp-content/uploads/2025/02/BEC-BAIDOA-ESIA.pdf", local_filename="power_source_BEC-BAIDOA-ESIA.pdf", version="Draft revision 04, submission 2025-01-30"),
    "beco": dict(title="Draft ESIA: Proposed BECO Hybrid Power Plant, Dayniile", publisher="MoEWR; Horizon Developments", publication_date="2025-01-30", url="https://moewr.gov.so/wp-content/uploads/2025/02/BECO-DAYNIILE-POWER-PLANT-ESIA.pdf", local_filename="power_source_BECO-DAYNIILE-POWER-PLANT-ESIA.pdf", version="Draft revision 04, submission 2025-01-30"),
    "bosaso": dict(title="Draft ESIA: Proposed Repair and Expansion of Bosaso Power Grid", publisher="MoEWR; Horizon Developments", publication_date="2025-03-23", url="https://moewr.gov.so/wp-content/uploads/2025/05/Final-Bosaso-ESIA-Report-20250324-Clean-ver-4-2.pdf", local_filename="power_source_bosaso_esia_2025.pdf", version="Cover says DRAFT, revision 03 dated 2025-03-23; website calls it Final, posted 2025-05-07"),
    "geco_addendum": dict(title="GECO Solar PV+BESS tender addendum, SO-MOEWR-459178-CW-RFB", publisher="MoEWR", publication_date="2025-02-16", url="https://moewr.gov.so/wp-content/uploads/2025/03/Addendum-No2-for-GECO-RFB.pdf", local_filename="power_source_GECO_addendum_2025.pdf", version="Page 1 says Addendum No.1 while filename says No2"),
    "jazeera_addendum": dict(title="Jazeera Power Plant BECO: Addendum 001, submission extension", publisher="MoEWR", publication_date="2025-03", url="https://moewr.gov.so/wp-content/uploads/2025/03/Jazeera-Addendum-001-Submission-Extension-Jazeera-Power-Plant-BECO-Mogadishu.pdf", local_filename=None, version="Upload month only; no more precise document date established"),
    "act": dict(title="Somalia Electricity Act", publisher="MoEWR", publication_date="2023-03-08", url="https://moewr.gov.so/ova_doc/somalia-electricity-act/", local_filename=None, version="Government announcement of presidential signing"),
    "regulations": dict(title="Tariff and Licensing Regulations", publisher="MoEWR", publication_date="2023-07-13", url="https://moewr.gov.so/ova_doc/tariff-and-licensing-regulations/", local_filename=None, version="Government announcement of cabinet approval"),
    "feature": dict(title="Reliable Electricity Is Helping Communities Across Somalia", publisher="World Bank", publication_date="2026-09-09", url="https://www.worldbank.org/en/news/feature/2026/09/09/reliable-electricity-is-helping-communities-across-somalia", local_filename=None, version="Feature story; reviewed for context, not an asset commissioning register"),
}

def write_csv(name, rows, columns=None):
    assert rows
    with (ROOT / name).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns or list(rows[0]))
        w.writeheader()
        w.writerows(rows)

facts = []
def fact(category, indicator, value, unit, geography, period, source, locator, evidence, model_use, caveat=""):
    s = SOURCES[source]
    facts.append(dict(fact_id=f"PWR-{len(facts)+1:03d}", category=category, indicator=indicator,
                      value=value, unit=unit, geography=geography, observation_period=period,
                      source_title=s["title"], publisher=s["publisher"], publication_date=s["publication_date"],
                      source_url=s["url"], locator=locator, evidence_type=evidence, model_use=model_use, caveat=caveat))

# Historical national context: retain source coverage, not a current whole-country registry.
for indicator,value,unit in [
    ("Electricity service providers","about 55","providers"),
    ("ESPs share of electricity supply",">90","percent"),
    ("Installed generation in major load centers","about 138","MW"),
    ("High speed diesel generators",">=227","generators"),
    ("Median diesel generator size",315,"kW"),
    ("Technical losses range","25-40","percent")]:
    fact("sector_history",indicator,value,unit,"Somalia major load centers" if indicator.startswith("Installed") else "Somalia (PID sector coverage)","Reported 2021; underlying inventory vintage not fully established","pid","PDF p4, paragraphs7-8","reported_estimate","Historical cross-check only","Not a current complete plant census; technical losses exclude a complete commercial-loss estimate.")
fact("tariff_history","Weighted average electricity tariff",0.61,"USD/kWh","Somalia (source distinguishes Somaliland)","2018 PSMP estimate cited in 2021","pid","PDF p4, paragraph8 and footnote","reported_estimate","Historical tariff benchmark","Do not assign as 2026 utility tariff or generation marginal cost.")
fact("tariff_history","Weighted average electricity tariff",0.68,"USD/kWh","Somaliland (source reporting area)","2018 PSMP estimate cited in 2021","pid","PDF p4, paragraph8 and footnote","reported_estimate","Historical tariff benchmark","Distinct source geography; not to be added to Somalia tariff.")
fact("tariff","Indicative electricity tariff",0.60,"USD/kWh","Somalia","2025 report context","dpf","Printed p17 / PDF p24, paragraph48","reported_estimate","Sector affordability context","Approximate narrative benchmark; tariff class, weighting and tax treatment not specified.")
fact("sector_structure","Private sector share of urban/periurban electricity supply",">90","percent","Somalia urban and periurban","2025 report context","dpf","Printed p17 / PDF p24, paragraph48","reported_estimate","Utility boundary context","Not a rural electrification or national access percentage.")

# Geospatial proximity is not access.
for indicator,val in [("Population within5km of existing mini-grids",44),("Population within10km of existing mini-grids",50),("Population within5km of MV network",35),("Population within10km of MV network",38)]:
    fact("network_proximity",indicator,val,"percent","Somalia (plan analysis geography)","Plan baseline; network/population layer vintages unresolved","plan","p24 Table2-1","geospatial_estimate","Candidate spatial screening only","Distance proximity is not an observed connection or access rate.")

# Inventory totals have known conflicts; only record with quarantine labels.
for indicator,val,unit,caveat in [
    ("Table2-5 reported PV total",11808,"kW","Regional values sum correctly; age and geographic coverage unresolved; not current national PV."),
    ("Table2-5 reported wind total",750,"kW","Age and geographic coverage unresolved; not a current national wind census."),
    ("Table2-5 reported diesel total",95186,"kW","CONFLICT: visible regional values sum 83586 kW, 11600 kW below reported total. Eastern cell blank. Do not select or repair silently."),
    ("Table2-5 reported MV line total",430,"km","Regional values reconcile; no route geometry, rating or common inventory date."),
    ("Table2-5 reported LV line total",2225,"km","CONFLICT: visible regional values sum2219km,6km below reported total. Not a transmission-line model.")]:
    fact("inventory_quarantine",indicator,val,unit,"Plan Table2-5 regional coverage (not established as nationwide)","Historical inventory reproduced in June2025 plan; vintage unresolved","plan","p27 Table2-5","conflicting_reported_inventory" if "CONFLICT" in caveat else "reported_inventory_vintage_unresolved","Quarantine pending source clarification",caveat)

losses=[("BECO","Mogadishu",16), ("Blue Sky","Mogadishu",25), ("MPS","Mogadishu",32),
        ("ENEE","Bosaso",35), ("Golis","Bosaso",30), ("Sometel","Bosaso",30),
        ("BECO","Baidoa",70), ("NESCOM (source spelling)","Garowe",25), ("ENEE","Qardho",35),
        ("DAYAH and Altowba","Beledweyne",2.3), ("BECO","Balad",19.9),
        ("Telesom","Hargeisa; Somaliland reporting area",25), ("NEC","Hargeisa; Somaliland reporting area",25),
        ("Hargeisa Electric Company","Hargeisa; Somaliland reporting area",30),
        ("BECO","Burao; Somaliland reporting area",45), ("Telesom","Borama; Somaliland reporting area",40),
        ("ALOOG","Borama; Somaliland reporting area",40)]
for esp,city,loss in losses:
    caveat="ESP declarations; survey date unresolved; technical/commercial components not consistently separated; do not apply nationally."
    if esp=="MPS": caveat += " p41 separately gives32% technical and25% commercial;32% is not a total."
    if city=="Baidoa": caveat += " CONFLICT: July2025 WB MTR estimates33% technical;70% must not become default."
    fact("losses",esp+" distribution loss reported",loss,"percent",city,"Undated ESP declaration reproduced June2025","plan","pp24-25 Table2-2","reported_estimate" if city!="Baidoa" else "conflicting_reported_estimate","Utility-specific sensitivity candidate; review needed",caveat)

# Existing capacities as reported by utility ESIAs, kept separate from proposals.
for src,city,esp,total,diesel,pv,page in [
    ("geco","South Galkacyo; Galmudug","GECO",2.4,2,0.4,12),
    ("nepco","North Galkacyo; Puntland","NEPCO",5.4432,4.9432,0.5,13),
    ("bec","Baidoa; South West State","BEC-Baidoa",8.648,7.648,1,12)]:
    for label,val in [("Reported installed total",total),("Reported diesel capacity",diesel),("Reported solar PV capacity",pv)]:
        fact("existing_generation",esp+": "+label,val,"MW",city,"Draft ESIA baseline January2025; precise measurement date unstated",src,f"PDF p{page}, Executive Summary item(iii)","reported_inventory_draft","Candidate existing-plant evidence; validate operational status","Not a commissioning certificate or audited asset register; aggregate utility capacity only; AC/DC PV basis unspecified.")
fact("inventory_quarantine","BECO reported combined generation plus storage power",175,"MW","BECO system; Mogadishu","Draft ESIA baseline January2025","beco","PDF p14 / printed xiv, Executive Summary item(iii)","reported_inventory_mixed_generation_storage","Do not load as generation-only MW","Source shares62%diesel31%PV7%BESS. Storage is included; not175MW of generation. Companywide, not Dayniile-site-only.")

# Most recent detailed utility project design evidence located, not commissioned stock.
projects=[("NECSOM","Garowe; Puntland",10,20,18.51), ("NEPCO","North Galkacyo; Puntland",4.3,9,10.57),
          ("GECO","South Galkacyo; Galmudug",3.42,5,5.31), ("WESCO","Kismayo; Jubaland",6,9.8,8.10),
          ("BEC","Baidoa; South West State",5.3,8.3,9.31)]
for esp,city,pv,bess,cost in projects:
    for indicator,val,unit in [("Proposed solar PV",pv,"MWp"),("Proposed BESS energy",bess,"MWh"),("Estimated package cost",cost,"million USD")]:
        fact("project_pipeline",esp+": "+indicator,val,unit,city,"July7-25,2025 mission; proposed EPC packages","mtr","p8 Annex2 Table1 and footnote7","planned_capacity" if unit!="million USD" else "bid_or_project_cost_estimate","Pipeline scenario candidate; not existing capacity","Contracts were under procurement at mission date. Cost is whole package; best-evaluated bid for NECSOM/NEPCO/GECO/BEC, estimate for WESCO. Later contract specifications not verified.")
for esp,city,current,target in [("NECSOM","Garowe",20,15),("NEPCO","North Galkacyo",25,19),("GECO","South Galkacyo",32,15),("WESCO","Kismayo",32,20),("BEC","Baidoa",33,20)]:
    for kind,val in [("Current technical loss estimate",current),("Target technical losses",target)]:
        fact("losses",esp+": "+kind,val,"percent",city,"July2025 MTR" if kind.startswith("Current") else "Post-project target; timing not specified","mtr","p15 Annex4, Technical loss reduction row","reported_estimate" if kind.startswith("Current") else "project_target","Utility-level loss sensitivity, not national default","The table labels current estimates and targets; this is not a metered-loss audit. Source spelling NECOM mapped to NECSOM by project context.")

# 2026 project status with exact observation dates.
for indicator,val,unit,period,loc,status,caveat in [
    ("Solar PV in SPV+BESS contracts",50,"MWp","March2026","PDF p6 / printed p1, paragraph2(b)","contracted_under_implementation","Contracts at various implementation stages; not50MWp commissioned. Includes Somaliland project scope."),
    ("BESS energy in SPV+BESS contracts",130,"MWh","March2026","PDF p6 / printed p1, paragraph2(b)","contracted_under_implementation","Storage energy; do not treat as MW. Commissioning not established."),
    ("Health institutions commissioned",120,"institutions","March2026","PDF p6 / printed p1, paragraph2(c)","reported_commissioned","Project count, not a count of all electrified health facilities in Somalia."),
    ("Education institutions commissioned",173,"institutions","March2026","PDF p6 / printed p1, paragraph2(c)","reported_commissioned","Project count; March narrative is newer than some October2025 indicator rows."),
    ("Health institutions in revised component scope",196,"institutions","March2026 revised scope","PDF p6 / printed p1, paragraph2(c)","project_scope_target","Not all commissioned; differs from original205 target."),
    ("Education institutions in revised component scope",272,"institutions","March2026 revised scope","PDF p6 / printed p1, paragraph2(c)","project_scope_target","Not all commissioned; differs from original380 target."),
    ("Renewable generation capacity constructed under SESRP",8.10,"MW","2026-02-28","PDF p12 / printed p7, Results renewable generation row","reported_project_result","Project contribution only, not national renewable stock; table comments retain stale October2025 wording."),
    ("Additional electricity supply under SESRP",17739,"MWh","2025-10-15","PDF p12 / printed p7, Results electricity supply row","reported_project_result","Public-institution systems; accumulation interval not explicit. Do not reinterpret as annual national generation."),
    ("Proposed revised SESRP renewable generation target",55.21,"MW","Target June2028","PDF p8 / printed p3 Table1 and PDF p12 results","proposed_project_target","Proposed restructuring target, not observed capacity or national target; another generation row retains23MW."),
    ("Proposed revised project electricity supply target",241772,"MWh","Target June2028","PDF p8 / printed p3 Table1","proposed_project_target","Period basis not explicitly annual; do not use as Somalia consumption."),
    ("Project tariff-reduction target",30,"percent","Target June2028","PDF p8 / printed p3 Table1","proposed_project_target","Project-relative reduction, not an actual tariff or guaranteed change."),
    ("Mogadishu and Hargeisa132kV subtransmission scope","dropped","status","March2026 restructuring report","PDF p8 / printed p3, paragraph6","reported_scope_cancellation","Detailed assessment found unnecessary at current demand. Not an existing or committed132kV network."),
    ("Requested new project closing date","2028-06-30","date","Request March5,2026","PDF p7 / printed p2, paragraph4","proposed_restructuring","A proposal/request; not independently verified as approved closing date.")]:
    fact("project_status",indicator,val,unit,"SESRP project areas in Somalia and Somaliland",period,"restructure",loc,status,"Project-specific evidence; not a national baseline",caveat)

# Other primary project versions, kept as explicit conflicts rather than silently updated.
for indicator,val,unit in [("GECO tender solar PV",3.5,"MWp"),("GECO tender BESS energy",7,"MWh")]:
    fact("project_version_conflict",indicator,val,unit,"South Galkacyo; Galmudug","Tender addendum2025-02-16","geco_addendum","p1 contract SO-MOEWR-459178-CW-RFB","historical_tender_design","Track design changes only","July2025 MTR gives3.42MWp+5MWh. Final contract scope not established; filename and internal addendum number differ.")
for indicator,val,unit in [("Jazeera tender solar PV",55,"MWp(AC) as printed"),("Jazeera tender BESS energy",160,"MWh")]:
    fact("project_pipeline",indicator,val,unit,"Jazeera; BECO; Mogadishu","March2025 tender addendum","jazeera_addendum","p1, SO-MOEWR-464597-CW-RFB","tender_design","ASCENT pipeline only","MWp(AC) is nonstandard/ambiguous; retain original basis, do not convert to AC or DC. Bid extension is not award or commissioning evidence.")

# Bosaso primary document recovered from official ministry mirror after AfDB access blocked.
for indicator,val,unit,loc,caveat in [
    ("PEPCO merger year",2022,"year","PDF p14 / printed xiv, Project description(i)","Merger of ENEE/GOLIS/SEPCO/RAHMO/TOWHID; not proof all networks interconnected."),
    ("Electricity service providers in Bosaso",4,"providers","PDF p14 / printed xiv, Project description(i)","PEPCO/Tawfiq/Alfardaws/Somtel; report-era scope, not national ESP count."),
    ("Proposed new solar PV DC capacity",7.15,"MWp","PDF p91 / printed p44, section3.3.1.1","New project increment, not total existing+planned solar."),
    ("Proposed new solar PV AC capacity",5.5,"MW","PDF p91 / printed p44, section3.3.1.1","Explicit AC counterpart to7.15MWp; planned, not commissioned."),
    ("Proposed BESS power",3,"MW","PDF p91 / printed p44, section3.3.1.1","Power, distinct from energy11MWh."),
    ("Proposed BESS energy",11,"MWh","PDF p91 / printed p44, section3.3.1.1","Planned storage; usable energy and degradation basis unspecified."),
    ("Proposed11kV network extension",24.7,"km","PDF p92 / printed p45, section3.3.2.2","Planned distribution, not existing transmission asset."),
    ("New distribution transformers",40,"transformers","PDF p92 / printed p45, section3.3.2.2","Planned11/0.4kV pole-mounted units."),
    ("Combined new transformer rated capacity",10545,"kVA","PDF p92 / printed p45, section3.3.2.2","Apparent power, not electrical generation MW."),
    ("Estimated project investment cost",25401917,"USD","PDF p101 / printed p54, Table3-0-1","Excludes land, rights of way and taxes; feasibility cost, not later financing approval or unit capital cost.")]:
    fact("bosaso_project",indicator,val,unit,"Bosaso; Puntland","ESIA March2025; feasibility reference2024","bosaso",loc,"reported_sector_history" if indicator in ["PEPCO merger year","Electricity service providers in Bosaso"] else "planned_design_or_cost","Project pipeline or utility boundary evidence",caveat+" Cover says draft despite Final in filename.")

fact("policy","Electricity Act presidential signing","2023-03-08","date","Federal Republic of Somalia","2023-03-08","act","Government announcement","official_policy_event","Regulatory context","Signing event does not establish implementation of every provision.")
fact("policy","Tariff and licensing regulations cabinet approval","2023-07-13","date","Federal Republic of Somalia","2023-07-13","regulations","Government announcement","official_policy_event","Regulatory context","Approval does not establish current approved utility tariff schedules.")
write_csv("power_facts.csv",facts)

# Historical annual utility consumption: all cells retained, including blanks/dashes.
consumption=[]
def consumption_table(table, page, utilities, data):
    for line in data.strip().splitlines():
        cells=line.split()
        year=int(cells[0])
        assert len(cells)-1==len(utilities)
        for (uid,name,area),raw in zip(utilities,cells[1:]):
            missing=raw in ["-","--","BLANK"]
            caveat="Source calls series historical consumption collected from ESPs in2025. Metering/audit and estimation method not specified per year. Do not label every cell audited observed demand."
            if not area: caveat += " Service area unresolved in table header."
            if name in ["BECO","Shebelle"]: caveat += " Utility source spelling retained; geographic ID prevents conflating distinct BECO names."
            if table=="3-8": caveat += " Overlap with MPS Mogadishu aggregate unresolved; do not add automatically."
            consumption.append(dict(record_id=f"PWR-C-{len(consumption)+1:03d}",utility_id=uid,
                utility_name_source=name,service_area_source=area,year=year,value_mwh="" if missing else int(raw),
                value_source_raw="" if raw=="BLANK" else raw,missing_reason="source_blank" if raw=="BLANK" else "source_dash" if missing else "",
                series_type="historical_consumption",evidence_type="missing" if missing else "reported_history_method_unresolved",
                source_title=SOURCES["plan"]["title"],publisher=SOURCES["plan"]["publisher"],publication_date=SOURCES["plan"]["publication_date"],
                retrieval_date=RETRIEVED,source_url=SOURCES["plan"]["url"],locator=f"p{page} Table{table}; year{year}; {name} {area}".strip(),caveat=caveat))

consumption_table("3-7",36,[("altowba_beledweyne","Al-Towba","Beledweyne"),("dayah_beledweyne","Dayah","Beledweyne"),("bec_baidoa","BECO","Baidoa"),("bse_mogadishu","BSE","Mogadishu"),("mps_mogadishu","MPS","Mogadishu"),("beco_mogadishu","BECO","Mogadishu")],"""
2015 - - 1163 18500 31904 -
2016 - - 1453 24555 35094 -
2017 - - 1772 32000 38603 -
2018 1102 2325 1772 32305 42463 -
2019 1114 3540 2735 43040 46710 -
2020 1238 3950 3335 57000 51381 -
2021 1360 4565 4118 80070 56519 -
2022 1540 4655 5147 105180 62171 331755
2023 1811 5465 6113 112560 83923 385176
2024 2691 5584 6833 120018 127616 446804
""")
consumption_table("3-8",37,[(f"mps_area_{i}","MPS",f"Area{i} {name}") for i,name in enumerate(["Balcad","Jowhar","Marko","Baraawe","Buuhoolde","Qoryooley","Buulomareer","Shalembood","Ceelsha"],2)],"2024 693 2048 1616 931 710 542 722 399 2778")
consumption_table("3-9",37,[("geco_galkayo","GECO","Galkayo"),("nepco_galkayo","NEPCO","Galkayo"),("nepco_goldogob","NEPCO","Goldogob"),("necsom_garowe","NECSOM","Garowe"),("pepco_bosaso","PEPCO","Bosaso"),("wesco_kismayo","WESCO","Kismayo")],"""
2015 4868 1978 - - - 592
2016 5112 2347 - - - 657
2017 5367 2787 - - - 740
2018 5636 3310 - 9128 - 847
2019 5918 3931 - 10892 -- 1078
2020 6213 4290 656 11823 - 1286
2021 6524 5467 709 13109 12090 1678
2022 6850 6585 766 15694 16420 2104
2023 7193 8036 739 19209 22150 2341
2024 7552 9281 893 23269 23710 2640
""")
consumption_table("3-10",37,[("sool_unresolved","SOOL",""),("beco_barawe","BECO","Barawe"),("shebelle_unresolved","Shebelle",""),("enee_qardho","ENEE","Qardho"),("hilaac_dhusmareeb","Hilaac","Dhusmareeb")],"""
2015 BLANK 585 351 BLANK 4300
2016 BLANK 667 400 BLANK 4730
2017 BLANK 760 456 BLANK 5203
2018 1354 867 520 BLANK 5790
2019 3025 988 593 BLANK 6369
2020 3384 1126 676 BLANK 7395
2021 4290 1284 770 2108 8135
2022 4980 1464 878 2910 9570
2023 6464 1669 1001 3900 10527
2024 7948 1902 1141 4180 11580
""")
assert len(consumption)==179
assert len({(x["utility_id"],x["year"]) for x in consumption})==len(consumption)
write_csv("power_consumption_history.csv",consumption)

# Planning cost assumptions copied as data, not promoted to default model inputs.
costs=[]
def cost(technology,parameter,value,unit,year,locator,caveat=""):
    costs.append(dict(record_id=f"PWR-A-{len(costs)+1:03d}",technology=technology,parameter=parameter,value=value,unit=unit,assumption_year=year,
        currency_basis="Dollar symbol in table; report currency context USD; cost base year not specified",evidence_type="planning_assumption_not_observed_quote",
        source_title=SOURCES["plan"]["title"],source_url=SOURCES["plan"]["url"],publication_date="2025-06",retrieval_date=RETRIEVED,locator=locator,
        model_use="Sensitivity candidate only; not adopted into SWITCH",caveat=caveat))
thermal=[
 ("HSDG",1,"Diesel",1440,10,10,2.23,8),
 ("Diesel MSDG10MW",10,"Diesel",1500,10,5,2.05,10),
 ("HFO MSDG10MW",10,"HFO",1500,10,5,2.10,10),
 ("HFO MSDG20MW",20,"HFO",1400,10,5,2.00,10),
 ("Diesel OCGT30MW",30,"Diesel",1000,10,4,2.39,20),
 ("LNG OCGT40MW",40,"LNG",1200,10,2,2.26,20),
 ("LNG OCGT100MW",100,"LNG",1050,10,2,2.26,20),
 ("LFO OCGT40MW",40,"LFO",1200,10,2,2.26,20),
 ("LFO OCGT100MW",100,"LFO",1050,10,2,2.26,20),
 ("LNG CCGT1+1 60MW",60,"LNG",1350,15,2,2.10,30),
 ("LNG CCGT2+1 120MW",120,"LNG",1200,15,2,1.80,30),
 ("LNG CCGT1+1 150MW",150,"LNG",1150,15,2,1.95,30),
 ("LNG CCGT2+1 300MW",300,"LFO",1000,15,2,1.95,30),
 ("LFO CCGT1+1 60MW",60,"LFO",1350,15,2,2.10,30),
 ("LFO CCGT2+1 120MW",120,"LFO",1200,15,2,1.80,30),
 ("LFO CCGT1+1 150MW",150,"LFO",1150,15,2,1.95,30),
 ("LFO CCGT2+1 300MW",300,"LFO",1000,15,2,1.95,30),
 ("Coal",200,"Coal",5000,50,5,2.39,30),
 ("Nuclear",300,"Nuclear",10000,120,10,2.46,60),
 ("Existing Hydro (source label)",4.6,"-",100,10,1,"80%",40),
 ("New Hydro",150,"-",1000,10,1,"80%",40),
]
for tech,size,fuel,capex,fom,vom,heat,life in thermal:
    note="Technology option, not an existing plant or approved procurement."
    if tech=="LNG CCGT2+1 300MW": note+=" CONFLICT: source calls technology LNG but fuel cell LFO; retained without correction."
    if "Hydro" in tech: note+="80% appears in heat-rate column; stored as efficiency-labelled source value, not Gcal/MWh. Existing label does not verify operational hydro capacity."
    for param,val,unit in [("Unit size",size,"MW"),("Fuel",fuel,"source fuel label"),("CAPEX",capex,"USD/kW"),("Fixed O&M",fom,"USD/kW/year"),("Variable O&M",vom,"USD/MWh"),("Efficiency source value" if "Hydro" in tech else "Heat input",heat,"percent as printed" if "Hydro" in tech else "Gcal/MWh"),("Lifetime",life,"years")]:
        cost(tech,param,val,unit,"Unspecified planning basis","p209 Table5-15",note)
for tech,capex,fom,life in [("PV",[700,650,500],7,25),("Onshore wind",[1500,1400,1300],20,30),("Offshore wind",[2200,2100,2000],50,30),("BESS4h",[800,480,360],0,15)]:
    note="Four-hour BESS CAPEX is per kW of power, not per kWh of energy." if tech=="BESS4h" else "Planning cost trajectory; not Somalia vendor quotes."
    for year,value in zip([2030,2040,2050],capex): cost(tech,"CAPEX",value,"USD/kW",year,"p209 Table5-16",note)
    for p,v,u in [("Fixed O&M",fom,"USD/kW/year"),("Variable O&M",0,"USD/MWh"),("Lifetime",life,"years")]: cost(tech,p,v,u,"Unspecified planning basis","p209 Table5-16",note)
network=[
 ("500kV single circuit quad Condor",511,"thousand USD/km"), ("230kV single circuit twin Ash",313,"thousand USD/km"),("132kV single circuit Ash",237,"thousand USD/km"),
 ("500kV double circuit quad Condor",787,"thousand USD/km"),("230kV double circuit twin Ash",450,"thousand USD/km"),("132kV double circuit Ash",330,"thousand USD/km"),
 ("Transformer500/230kV 500MVA",6300,"thousand USD/unit"),("Transformer500/230kV 250MVA",5500,"thousand USD/unit"),("Transformer500/230kV 150MVA",4500,"thousand USD/unit"),
 ("Transformer230/132kV 250MVA",4300,"thousand USD/unit"),("Transformer230/132kV 150MVA",3200,"thousand USD/unit"),("Transformer230/33kV 100MVA",3000,"thousand USD/unit"),("Transformer230/33kV 50MVA",2580,"thousand USD/unit"),("Transformer132/33kV 100MVA",2500,"thousand USD/unit"),
 ("500kV switchgear",4190,"thousand USD/circuit"),("230kV switchgear",1500,"thousand USD/circuit"),("132kV switchgear",850,"thousand USD/circuit"),("Shunt reactor",15,"thousand USD/Mvar"),("Capacitor bank",25,"thousand USD/Mvar")]
for tech,val,unit in network: cost(tech,"Investment cost",val,unit,"Unspecified planning basis","p210 Table5-17","Report says Somalia-specific transmission cost observations unavailable; estimates follow Ethiopia-Somalia interconnection study. Do not treat as existing line cost or delivered quote.")
write_csv("power_planning_assumptions.csv",costs)

manifest=[]
# Public checkouts deliberately omit cached PDFs. Preserve the frozen source
# fingerprints when rebuilding reviewed transcriptions without those caches.
prior_path = ROOT / "source_doc_manifest.json"
prior_manifest = {entry["source_id"]: entry for entry in json.loads(prior_path.read_text(encoding="utf-8"))} if prior_path.exists() else {}
for sid,s in SOURCES.items():
    p=ROOT/s["local_filename"] if s["local_filename"] else None
    present=bool(p and p.is_file())
    prior = prior_manifest.get(sid, {})
    manifest.append(dict(source_id=sid,source_url=s["url"],title=s["title"],publisher=s["publisher"],publication_date=s["publication_date"],retrieval_date=RETRIEVED,version=s["version"],
        sha256=hashlib.sha256(p.read_bytes()).hexdigest() if present else prior.get("sha256"),bytes=p.stat().st_size if present else prior.get("bytes"),
        local_filename=s["local_filename"] if present else prior.get("local_filename"),
        verification="PDF downloaded and opened" if present else prior.get("verification", "Primary webpage/PDF text opened in web tool; no local binary retained"),
        redistribution_status="Link and original factual annotations only; raw redistribution license not established; do not publish cached PDF, full text or page renders by default"))
(ROOT/"source_doc_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert len({f["fact_id"] for f in facts})==len(facts)
assert all(f["source_url"].startswith("https://") and f["locator"] and f["evidence_type"] for f in facts)
assert all(x["value_mwh"]=="" or x["value_mwh"]>=0 for x in consumption)
assert sum([8100,15553,26230,17463,16240])==83586
assert sum([233,440,770,503,273])==2219
print(json.dumps({"facts":len(facts),"consumption_cells":len(consumption),"consumption_numeric":sum(r["value_mwh"]!="" for r in consumption),"consumption_missing":sum(r["value_mwh"]=="" for r in consumption),"planning_parameters":len(costs),"sources":len(manifest)},indent=2))
validation=dict(retrieval_date=RETRIEVED,facts=len(facts),consumption_cells=len(consumption),consumption_numeric=sum(r["value_mwh"]!="" for r in consumption),consumption_missing=sum(r["value_mwh"]=="" for r in consumption),planning_parameter_records=len(costs),sources=len(manifest),local_pdf_hashes=sum(x["sha256"] is not None for x in manifest),
    checks_passed=["unique fact IDs","unique utility-year consumption keys","all facts have HTTPS source and page/section locator","nonnegative consumption values","179 source cells retained including36 missing","plan Table2-5 diesel arithmetic conflict reproduced:83586 versus95186kW","plan Table2-5 LV arithmetic conflict reproduced:2219 versus2225km"],
    verification_limits=["Manual transcriptions, not independently audited utility records","No source license established for raw PDF redistribution","No current complete generation or transmission inventory established","No SWITCH inputs changed and no optimization run"],
    output_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ["power_facts.csv","power_consumption_history.csv","power_planning_assumptions.csv","source_doc_manifest.json"]})
(ROOT/"power_validation.json").write_text(json.dumps(validation,indent=2)+"\n",encoding="utf-8")
