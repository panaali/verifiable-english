"""Read-only contract check against another branch; no harness files or model calls.

The git objects are loaded directly into memory. This lets the two workers test
the actual Item/Condition/Experiment contract without vendoring ve_experiments.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import types


def load_harness(branch):
    root = Path(__file__).resolve().parents[2]
    package = types.ModuleType("ve_experiments")
    package.__path__ = []
    package.__package__ = "ve_experiments"
    sys.modules[package.__name__] = package
    for name in ("llm", "ve_iface", "runner", "stats"):
        path = f"ve_experiments/{name}.py"
        source = subprocess.check_output(["git", "show", f"{branch}:{path}"], cwd=root, text=True)
        module = types.ModuleType(f"ve_experiments.{name}")
        module.__package__ = "ve_experiments"
        module.__file__ = str(root / path)
        sys.modules[module.__name__] = module
        exec(compile(source, f"{branch}:{path}", "exec"), module.__dict__)
    return sys.modules["ve_experiments.runner"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch", default="claude/harness")
    parser.add_argument("--committed", action="store_true")
    args = parser.parse_args()
    runner = load_harness(args.branch)
    from experiments.E5 import materials as e5
    from experiments.E2E4 import materials as e2e4
    root = Path(__file__).resolve().parents[2]
    results = []
    for experiment in ("E5", "E2", "E4"):
        if experiment == "E5":
            rows = e5.build_items("dev") + e5.build_items("scored")
            conditions = e5.harness_conditions()
            exp_id, split_file = "E5", e5.HERE / "split.json"
        else:
            rows = e2e4.build_items("dev", experiment) + e2e4.build_items("scored", experiment)
            cells = e2e4.E2_CELLS if experiment == "E2" else e2e4.E4_CELLS
            conditions = [runner.Condition(c, lambda p, c=c: e2e4.render_cell(p, c)) for c in cells]
            exp_id, split_file = f"E2E4/{experiment}", root / "experiments/E2E4/splits.json"
        exp = runner.Experiment(id=exp_id, items=[runner.Item(**r) for r in rows], conditions=conditions,
                                judges=["offline-contract-only"], split_file=split_file, root=root)
        runner.check_design(exp)
        missing = runner.missing_prereg_sections((exp.dir / "PREREG.md").read_text())
        assert not missing, (experiment, missing)
        if args.committed:
            runner.require_prereg(exp.dir, root)
            runner.require_committed(split_file, root)
        for split in ("dev", "scored"):
            trials = runner.plan_trials(exp, split)
            prompts = runner.build_prompts(exp, trials)
            assert len(prompts) == len(trials)
            assert all('{"verdict":"approve"}' in p and '{"verdict":"reject"}' in p for p in prompts)
            results.append({"experiment": experiment, "split": split,
                            "items": sum(r["split"] == split for r in rows), "prompts": len(prompts)})
    print(json.dumps({"branch": args.branch,
        "commit": subprocess.check_output(["git", "rev-parse", args.branch], text=True).strip(),
        "committed_preregs_checked": args.committed, "model_calls": 0, "results": results}, indent=2))


if __name__ == "__main__":
    main()
