const core='https://github.com/switch-model/switch/blob/239d62cbe9baeec3bb05e56487241bdea60740af/';
const kenya='https://github.com/NotEleven/Switch-Kenya-2025_public/blob/089834b8fee23239d61ffb6e7d68279f0a74efed/';
const work='https://github.com/alajwadha/SWITCH_RENEW/blob/main/';
export const sources:Record<string,{title:string;url:string;note:string}>={
 core:{title:'SWITCH core · pinned source and module architecture',url:core+'README.md',note:'Core revision 239d62c; this course targets the workbench’s pinned SWITCH 2.0.9, not every historical SWITCH study.'},
 time:{title:'timescales.py · periods, timepoints and weights',url:core+'switch_model/timescales.py',note:'Defines physical durations, annual/period weights and circular predecessor links; uses 8,766 hours/year for weight validation.'},
 finance:{title:'financials.py · annualization, discounting and objective',url:core+'switch_model/financials.py',note:'Authoritative cost registries and annual-to-base-year factors.'},
 zones:{title:'balancing/load_zones.py · zonal power balance',url:core+'switch_model/balancing/load_zones.py',note:'Zone_Power_Injections and Zone_Power_Withdrawals assemble the active balance.'},
 build:{title:'generators/core/build.py · vintages, capacity and fixed costs',url:core+'switch_model/generators/core/build.py',note:'BuildGen, SuspendGen, surviving capacity, minimum builds and capital-recovery accounting.'},
 dispatch:{title:'generators/core/dispatch.py · dispatch and emissions',url:core+'switch_model/generators/core/dispatch.py',note:'DispatchGen, generator/timepoint mappings, fuel use, annual reporting and emissions expressions.'},
 noCommit:{title:'generators/core/no_commit.py · dispatch without unit commitment',url:core+'switch_model/generators/core/no_commit.py',note:'Availability ceilings, baseload treatment and full-load heat-rate fuel use.'},
 fuel:{title:'energy_sources/fuel_costs/simple.py · exogenous fuel prices',url:core+'switch_model/energy_sources/fuel_costs/simple.py',note:'Zone–fuel–period prices and their hourly cost contribution.'},
 storage:{title:'generators/extensions/storage.py · MW, MWh and state of charge',url:core+'switch_model/generators/extensions/storage.py',note:'This pinned implementation places round-trip efficiency on charging; DispatchGen is discharge.'},
 txBuild:{title:'transmission/transport/build.py · corridor investment',url:core+'switch_model/transmission/transport/build.py',note:'Transport capacity and cost model; does not enforce AC or DC power-flow physics.'},
 txDispatch:{title:'transmission/transport/dispatch.py · directional transfers',url:core+'switch_model/transmission/transport/dispatch.py',note:'Sending-end dispatch, receiving-end efficiency and zonal net power.'},
 reserves:{title:'balancing/planning_reserves.py · capacity adequacy',url:core+'switch_model/balancing/planning_reserves.py',note:'Planning reserve requirement, capacity contribution and enforcement times.'},
 hydro:{title:'generators/extensions/hydro_simple.py · hydro energy budgets',url:core+'switch_model/generators/extensions/hydro_simple.py',note:'Optional simple hydro module; a river-basin model needs more detailed water constraints.'},
 commit:{title:'generators/core/commit/operate.py · unit commitment',url:core+'switch_model/generators/core/commit/operate.py',note:'Optional commitment, startup/shutdown and operating restrictions; not the Kenya base no_commit module.'},
 carbon:{title:'policies/carbon_policies.py · emissions caps and prices',url:core+'switch_model/policies/carbon_policies.py',note:'Optional carbon-policy implementation; must be activated to affect a model.'},
 tutorial:{title:'Official three-zone tiny tutorial · pinned inputs and outputs',url:'https://github.com/switch-model/switch_tutorial/tree/6b72f3006854a81ac74d008d0145da1919c54d49/3_zone_tiny',note:'Small official example used for the workbench’s parity test.'},
 kenyaBase:{title:'Kenya base · active module list',url:kenya+'inputs/modules.txt',note:'County-level deterministic configuration. The inspected base list does not activate hydrogen_electrolyzers.'},
 kenyaData:{title:'Kenya dataset · pinned research repository',url:'https://github.com/NotEleven/Switch-Kenya-2025_public/tree/089834b8fee23239d61ffb6e7d68279f0a74efed',note:'Dataset and custom modules. Retain attribution and the CC BY-NC 4.0 noncommercial conditions.'},
 kenyaLimits:{title:'Kenya gen_build_limits.py · custom investment constraints',url:kenya+'gen_build_limits.py',note:'Includes a project-limit branch with undefined tech/p names; the course distinguishes intended algebra from this source defect.'},
 kenyaH2:{title:'Kenya hydrogen_electrolyzers.py · custom sector coupling',url:kenya+'hydrogen_electrolyzers.py',note:'Attributes the adaptation to Xi Xi, based partly on work by Tyler Lis and Aashika Nair. Source availability is not adapter activation.'},
 workbench:{title:'Workbench README · actual setup, runs and backups',url:work+'README.md',note:'What the current local and Vercel editions can actually do.'},
 verification:{title:'Workbench verification · tests and known limits',url:work+'docs/VERIFICATION.md',note:'A full optimal Kenya solve is not yet verified; do not interpret an unfinished solve as a research result.'},
 stochastic:{title:'backend/stochastic.py · original two-stage learning lab',url:work+'backend/stochastic.py',note:'Separate illustrative Pyomo model, not a native SWITCH stochastic or Kenya adapter.'},
 atlas:{title:'Atlas data dictionary · coverage and comparability',url:work+'docs/ATLAS_DATA.md',note:'Country statistics supply context; they do not automatically populate SWITCH inputs.'},
 pyomo:{title:'Pyomo documentation · modelling components',url:'https://pyomo.readthedocs.io/en/stable/explanation/modeling/math_programming/index.html',note:'General modelling reference. Workbench dependency versions are pinned separately.'}
};
