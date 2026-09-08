"""Explicit two-stage capacity expansion example; not a SWITCH adapter."""
import pyomo.environ as pyo

def solve_teaching(config):
    # One representative operating condition covering 8,760 hours per year.
    # Capital cost is already annualized, USD/MW-year. All costs USD/year.
    demands = [70.0, 100.0, 150.0]
    probabilities = [0.25, 0.5, 0.25]
    demands = [d * config["demand_multiplier"] for d in demands]
    alpha = config["cvar_alpha"]
    risk = config["risk_weight"]

    def solve(ds, ps, fixed=None, risk_weight=0.0):
        m = pyo.ConcreteModel()
        m.S = pyo.RangeSet(0, len(ds) - 1)
        # One shared variable per technology is non-anticipativity by construction.
        m.BuildFirm = pyo.Var(domain=pyo.NonNegativeReals)
        m.BuildSolar = pyo.Var(bounds=(0, 300), domain=pyo.NonNegativeReals)
        m.FirmDispatch = pyo.Var(m.S, domain=pyo.NonNegativeReals)
        m.SolarDispatch = pyo.Var(m.S, domain=pyo.NonNegativeReals)
        m.Unserved = pyo.Var(m.S, domain=pyo.NonNegativeReals)
        if fixed is not None:
            m.BuildFirm.fix(fixed[0])
            m.BuildSolar.fix(fixed[1])
        m.Balance = pyo.Constraint(m.S, rule=lambda m, s: m.FirmDispatch[s] + m.SolarDispatch[s] + m.Unserved[s] == ds[s])
        m.FirmLimit = pyo.Constraint(m.S, rule=lambda m, s: m.FirmDispatch[s] <= 40 + m.BuildFirm)
        m.SolarLimit = pyo.Constraint(m.S, rule=lambda m, s: m.SolarDispatch[s] <= 0.3 * m.BuildSolar)
        m.BuildCost = pyo.Expression(expr=config["capital_multiplier"] * (85000 * m.BuildFirm + 65000 * m.BuildSolar))
        m.Cost = pyo.Expression(m.S, rule=lambda m, s: m.BuildCost + 8760 * (70 * config["fuel_multiplier"] * m.FirmDispatch[s] + 10000 * m.Unserved[s]))
        m.ExpectedCost = pyo.Expression(expr=sum(ps[s] * m.Cost[s] for s in m.S))
        if risk_weight:
            m.Eta = pyo.Var(domain=pyo.Reals)
            m.Excess = pyo.Var(m.S, domain=pyo.NonNegativeReals)
            m.Tail = pyo.Constraint(m.S, rule=lambda m, s: m.Excess[s] >= m.Cost[s] - m.Eta)
            m.CVaR = pyo.Expression(expr=m.Eta + sum(ps[s] * m.Excess[s] for s in m.S) / (1 - alpha))
            m.Objective = pyo.Objective(expr=(1 - risk_weight) * m.ExpectedCost + risk_weight * m.CVaR)
        else:
            m.Objective = pyo.Objective(expr=m.ExpectedCost)
        solver = pyo.SolverFactory("appsi_highs")
        solver.options["time_limit"] = config["time_limit"]
        result = solver.solve(m, load_solutions=False)
        if str(result.solver.termination_condition) != "optimal":
            raise RuntimeError("Teaching benchmark did not solve to optimality: " + str(result.solver.termination_condition))
        solver.load_vars()
        costs = [pyo.value(m.Cost[s]) for s in m.S]
        eta = next(c for c, _ in sorted(zip(costs, ps)) if sum(p for v, p in zip(costs, ps) if v <= c) >= alpha - 1e-12)
        cvar = eta + sum(p * max(c - eta, 0) for c, p in zip(costs, ps)) / (1 - alpha)
        return {"expected_cost": pyo.value(m.ExpectedCost), "objective": pyo.value(m.Objective), "firm_build_mw": pyo.value(m.BuildFirm), "solar_build_mw": pyo.value(m.BuildSolar), "cvar": cvar, "var": eta, "scenarios": [{"name": ["Low", "Central", "High"][s] if len(ds) == 3 else "Benchmark", "probability": ps[s], "demand_mw": ds[s], "cost": costs[s], "firm_mw": pyo.value(m.FirmDispatch[s]), "solar_mw": pyo.value(m.SolarDispatch[s]), "unserved_mw": pyo.value(m.Unserved[s])} for s in m.S], "variables": m.nvariables(), "constraints": m.nconstraints()}

    neutral = solve(demands, probabilities)
    selected = neutral if risk == 0 else solve(demands, probabilities, risk_weight=risk)
    ev = solve([sum(d * p for d, p in zip(demands, probabilities))], [1.0])
    eev = solve(demands, probabilities, fixed=(ev["firm_build_mw"], ev["solar_build_mw"]))
    ws = sum(p * solve([d], [1.0])["expected_cost"] for d, p in zip(demands, probabilities))
    selected.update({"termination": "optimal", "status": "succeeded", "model_kind": "two_stage_teaching", "currency": "USD/year", "risk_weight": risk, "cvar_alpha": alpha, "rp": neutral["expected_cost"], "eev": eev["expected_cost"], "ws": ws, "vss": eev["expected_cost"] - neutral["expected_cost"], "evpi": neutral["expected_cost"] - ws, "nonanticipativity_residual": 0.0, "nonanticipativity_note": "Shared BuildFirm and BuildSolar variables, so scenario-specific build choices do not exist. VSS and EVPI use the risk-neutral benchmark even when a risk-averse plan is selected.", "assumptions": {"hours_per_year": 8760, "existing_firm_mw": 40, "solar_availability": 0.3, "firm_capex_usd_per_mw_year": 85000 * config["capital_multiplier"], "solar_capex_usd_per_mw_year": 65000 * config["capital_multiplier"], "firm_variable_usd_per_mwh": 70 * config["fuel_multiplier"], "unserved_usd_per_mwh": 10000, "solar_limit_mw": 300, "warning": "Single representative operating condition; no chronology, storage, network, or national calibration. Illustrative assumptions."}})
    return selected
