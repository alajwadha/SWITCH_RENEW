"""Build the explicit Kenya schema-to-Somalia evidence mapping; never create model inputs."""
import csv
from pathlib import Path
from collect_data import ROOT, write_csv

MAPPING = {
    "financials.csv": ("finance", "partial", "statistics_facts.csv; power_facts.csv", "Choose price base year, real/nominal basis and Somalia-specific financing scenarios; national GDP or inflation is not WACC", "P1"),
    "fuel_cost.csv": ("fuel_prices", "partial", "World Bank RTEP diesel archive; statistics_facts.csv", "Delivered utility diesel cost; market currency/FX/density/heating-value and procurement adjustments needed", "P1"),
    "fuels.csv": ("fuel_properties", "gap", "IPCC stationary combustion guidelines; fuel quality certificates needed", "Fuel-specific net calorific value and combustion/upstream CO2 factors; do not inherit Kenya values", "P1"),
    "gen_build_costs.csv": ("technology_costs", "partial", "power_facts.csv; official optimized plan candidate costs", "Local installed cost and fixed O&M by technology/vintage; separate battery USD/kW and USD/kWh; currency/base year", "P1"),
    "gen_build_limits_by_tech.csv": ("build_limits", "partial", "resource_catalog.csv; project pipeline in power_facts.csv", "Developable area, permitting, siting and construction-rate constraints; resource raster is not a build limit", "P2"),
    "gen_build_predetermined.csv": ("existing_assets", "partial", "gem_somalia_assets.csv; power_facts.csv; IRENA national totals", "Deduplicate sites/units, verify commissioned capacity and year; reconcile MWac/MWp; exclude uncommissioned pipeline", "P1"),
    "gen_info.csv": ("asset_performance", "partial", "power_facts.csv; gem_somalia_assets.csv", "Heat rates, plant dates, variable O&M, outages, battery power/energy/efficiency/life and retirement assumptions", "P1"),
    "load_zones.csv": ("electrical_zones", "partial", "geoboundaries alternative layers; resource_catalog.csv; utility reports", "Choose service areas; define local grid loss and capacity; admin units are not electrical zones", "P1"),
    "loads.csv": ("load_chronology", "partial", "power_consumption_history.csv; world_bank_observations.csv", "Metered hourly MW by utility with date/timezone; distinguish billing, gross generation, own-use, unserved demand and forecasts", "P1"),
    "modules.txt": ("model_scope", "decision_pending", "Somalia AGENTS.md; ASSUMPTIONS_AND_DECISIONS.md", "Select minimum modules after baseline scope; hydrogen and other additional sectors not adopted", "P1"),
    "non_fuel_energy_sources.csv": ("technology_scope", "partial", "IRENA; power_facts.csv; resource_catalog.csv", "Confirm technology coverage and suitability; availability of resource does not prove a project is feasible", "P2"),
    "periods.csv": ("planning_horizon", "decision_pending", "2025 national optimized plan; dated project documents", "Set baseline year and investment horizon; source forecast years are not automatically model periods", "P1"),
    "planning_reserve_requirement_zones.csv": ("adequacy_zones", "decision_pending", "utility/network records still required", "Define which connected systems share capacity; do not pool isolated systems", "P1"),
    "planning_reserve_requirements.csv": ("adequacy_criteria", "gap", "utility reliability criteria still required", "Reserve standard and renewable/storage capacity credit; Kenya 9% margin is not a Somalia observation", "P1"),
    "switch_inputs_version.txt": ("software_contract", "schema_only", "sources.lock.json; kenya_input_schema_inventory.csv", "Pin SWITCH version when building eventual adapter; data pack is not a runnable adapter", "P2"),
    "timepoints.csv": ("time_sampling", "partial", "NASA hourly2025 and daily2001-2025", "Align load/weather in same timezone then choose representative periods; retain chronology for storage", "P1"),
    "timeseries.csv": ("time_weights", "decision_pending", "NASA complete-year chronology", "Design sampling weights with represented-hours checks; daily weather is not hourly dispatch", "P1"),
    "trans_county.csv": ("auxiliary_geography", "schema_only", "geoBoundaries; OCHA metadata; Kenya source file", "Kenya-specific auxiliary mapping appears headerless; do not transfer county topology", "P3"),
    "trans_params.csv": ("network_costs", "partial", "power_facts.csv; optimized plan assumptions", "Somalia corridor cost per MW-km, lifetime and fixed O&M need rating/voltage/currency basis", "P1"),
    "transmission_lines.csv": ("network_topology", "partial", "power_facts.csv; 2026 project restructuring; OSM catalogue", "Verify existing versus proposed lines, endpoints, ratings, lengths, losses and timing; OSM may omit assets", "P1"),
    "variable_capacity_factors.csv": ("generation_profiles", "resource_inputs_available", "NASA POWER; solar_country_workbook_cells.csv; GWA raster", "Build/validate PV and turbine performance transformations; wind speed/irradiance are not capacity factors", "P1"),
    "zone_balancing_areas.csv": ("operating_areas", "decision_pending", "utility operating and interconnection agreements needed", "Define reserve sharing and island operation; blank Kenya file is not evidence of Somalia design", "P2"),
    "zone_coincident_peak_demand.csv": ("peak_demand", "partial", "power_facts.csv; utility records needed", "Measure simultaneous served peak, distinguish suppressed demand and noncoincident peaks", "P1"),
    "electrolyzer_build_limits.csv": ("hydrogen", "outside_active_scope", "Kenya schema reference only", "Separate research proposal; no data parameter transfer or implementation", "excluded"),
    "hydrogen.csv": ("hydrogen", "outside_active_scope", "Kenya schema reference only", "Separate research proposal; no data parameter transfer or implementation", "excluded"),
    "hydrogen_flexible.csv": ("hydrogen", "outside_active_scope", "Kenya schema reference only", "Separate research proposal; no data parameter transfer or implementation", "excluded"),
}

rows = []
with (ROOT / "processed/kenya_input_schema_inventory.csv").open(encoding="utf-8-sig", newline="") as handle:
    for row in csv.DictReader(handle):
        category, status, source, gap, priority = MAPPING[row["filename"]]
        rows.append(dict(kenya_file=row["filename"], fields=row["columns"], category=category,
                         somalia_readiness=status, available_evidence=source, remaining_requirement=gap, priority=priority,
                         parameter_transfer="none", kenya_reference_commit=row["reference_commit"]))
write_csv(ROOT / "processed/kenya_to_somalia_crosswalk.csv", rows)
write_csv(ROOT / "processed/priority_data_requests.csv", [dict(request_id="G%02d" % (i+1), category=r["category"], priority=r["priority"], requested_data=r["remaining_requirement"], evidence_so_far=r["available_evidence"], switch_destination=r["kenya_file"]) for i,r in enumerate(rows) if r["priority"] in ["P1", "P2"]])
print("Mapped " + str(len(rows)) + " Kenya files; no numerical parameters transferred")
