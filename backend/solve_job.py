"""One solver process per run. All outputs belong to that run's snapshot."""
from __future__ import annotations

import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import shutil
import sys
import time
import traceback

from backend.core import ROOT, atomic_json, hashes, now, run_dir, source_versions

def finite(v):
    try:
        n = float(v)
        return n if math.isfinite(n) else None
    except (ValueError, TypeError):
        return None

def solve_switch(folder, manifest):
    import pandas as pd
    import pyomo.environ as pyo
    from switch_model.solve import main
    from switch_model.upgrade import do_inputs_need_upgrade, upgrade_inputs

    # The queued snapshot is immutable. Upgrades operate on a separate effective copy.
    effective = folder / "effective_inputs"
    shutil.copytree(folder / "inputs", effective)
    needs_upgrade = do_inputs_need_upgrade(str(effective))
    if needs_upgrade:
        print("Migrating the effective input copy using the pinned SWITCH upgrader.", flush=True)
        upgrade_inputs(str(effective))
    manifest["effective_input_hashes"] = hashes(effective)
    manifest["input_upgrade_applied"] = needs_upgrade
    atomic_json(folder / "manifest.json", manifest)
    if (folder / "custom").exists():
        sys.path.insert(0, str(folder / "custom"))
    out = folder / "outputs"
    out.mkdir(exist_ok=True)
    model = main(args=["--inputs-dir", str(effective), "--outputs-dir", str(out), "--solver", "appsi_highs"], return_instance=True)
    solver = pyo.SolverFactory("appsi_highs")
    solver.options["time_limit"] = manifest["solver"]["time_limit_seconds"]
    solver.options["mip_rel_gap"] = manifest["solver"]["mip_gap"]
    solver.options["threads"] = 1
    print("Solving with HiGHS…", flush=True)
    result = solver.solve(model, tee=True, load_solutions=False)
    termination = str(result.solver.termination_condition)
    result.write(filename=str(folder / "solver_results.json"), format="json")
    base = {"termination": termination, "model_kind": "switch", "variables": model.nvariables(), "constraints": model.nconstraints(), "has_integer_variables": any(v.is_integer() or v.is_binary() for v in model.component_data_objects(pyo.Var)), "currency": f"model dollars, base year {pyo.value(model.base_financial_year)}", "objective": None, "solver_lower_bound": finite(result.problem.lower_bound), "solver_upper_bound": finite(result.problem.upper_bound)}
    if not len(result.solution):
        return {**base, "status": "infeasible" if termination == "infeasible" else "no_solution", "message": "No incumbent solution is available. Review the solver log and inputs."}
    # APPSI keeps a direct mapping to model variables; loading through this
    # interface also retains variables omitted from legacy serialized results.
    solver.load_vars()
    model.post_solve(str(out))
    maximum = 0.0
    worst = None
    for c in model.component_data_objects(pyo.Constraint, active=True):
        body = pyo.value(c.body)
        violation = max(0, (pyo.value(c.lower) - body) if c.has_lb() else 0, (body - pyo.value(c.upper)) if c.has_ub() else 0)
        if violation > maximum:
            maximum, worst = violation, c.name
    tables = {}
    processed = folder / "processed"
    processed.mkdir()
    for name in ["electricity_cost", "dispatch_annual_summary", "gen_cap", "gen_build", "costs_itemized", "transmission", "load_balance", "dispatch"]:
        path = out / f"{name}.csv"
        if path.exists():
            frame = pd.read_csv(path)
            frame.to_parquet(processed / f"{name}.parquet", index=False)
            if name not in ("load_balance", "dispatch"):
                tables[name] = json.loads(frame.to_json(orient="records"))
    return {**base, "status": "succeeded" if termination == "optimal" else "feasible", "objective": pyo.value(model.SystemCost), "max_constraint_violation": maximum, "worst_constraint": worst, "constraint_check_note": "Absolute residual across constraints with differing native units; inspect the named constraint when material.", "tables": tables, "periods": list(model.PERIODS), "zones": list(model.LOAD_ZONES), "input_upgrade_applied": needs_upgrade}

def main(rid):
    folder = run_dir(rid)
    manifest = json.loads((folder / "manifest.json").read_text())
    start = time.monotonic()
    try:
        source_versions(manifest["scenario"]["model"])
        if hashes(folder / "inputs") != manifest["input_hashes"] and manifest["scenario"]["model"] != "stochastic":
            raise ValueError("Input snapshot checksum mismatch")
        if hashes(folder / "custom") != manifest.get("custom_hashes", {}):
            raise ValueError("Custom module checksum mismatch")
        manifest["runtime"] = {"python": platform.python_version(), "platform": platform.platform(), "packages": {n: importlib.metadata.version(n) for n in ["pyomo", "highspy", "pandas", "pyarrow", "switch-model"]}}
        from subprocess import run
        revision = run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True)
        manifest["workbench_commit"] = revision.stdout.strip() if revision.returncode == 0 else "uncommitted-development"
        import hashlib
        manifest["workbench_python_hashes"] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / "backend").glob("*.py")}
        dirty = run(["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=normal", "--", "backend", "sources.lock.json"], capture_output=True, text=True)
        manifest["workbench_has_uncommitted_solver_changes"] = bool(dirty.stdout.strip())
        atomic_json(folder / "manifest.json", manifest)
        if manifest["scenario"]["model"] == "stochastic":
            from backend.stochastic import solve_teaching
            summary = solve_teaching(manifest["scenario"]["config"])
        else:
            summary = solve_switch(folder, manifest)
        summary["elapsed_seconds"] = time.monotonic() - start
        summary["finished_at"] = now()
        summary["output_hashes"] = hashes(folder / "outputs") if (folder / "outputs").exists() else {}
        atomic_json(folder / "result.json", summary)
        print(f"Completed: {summary['status']} · {summary.get('objective')}", flush=True)
    except BaseException as exc:
        traceback.print_exc()
        atomic_json(folder / "result.json", {"status": "failed", "error": str(exc), "elapsed_seconds": time.monotonic() - start, "finished_at": now()})
        raise

if __name__ == "__main__":
    main(sys.argv[1])
