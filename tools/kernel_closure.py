#!/usr/bin/env python3
"""The kernel boundary, measured (docs/spec/kernel-boundary.md, section 2).

A *verdict path* is one way a service mode answers with a verdict. `tools/kernel-paths.json`
names each path of the kernel: the mode's entry (the right-hand side of its `runMode_*` pin in
`lean/VE/Service/Protocol.lean`), the theorems that state what an accepted answer means, and the
runner those theorems are about (the `subject`). For every path this tool measures, from the
compiled Lean environment (`tools/kernel_closure.lean`):

* **spec**: the lines a reviewer must read to know what the theorems say: the statements' own
  definitions, transitively, with the subject left unread (the theorems hold for whatever it
  computes) and no proof read;
* **wrap**: the lines that run between the service entry and the subject, which no listed theorem
  covers: every definition the entry reaches without passing through a subject, a path this path
  delegates to (`delegates`), or a reviewed non-verdict exit (`nonverdict`).

It also lists the **verdict writers**: every definition whose body holds one of the registry's
`verdict_tokens` as a string literal, and whether it lies inside the kernel: in a kernel path's
spec or wrap, or in the code a kernel subject runs (which that path's theorems are about). A writer
outside the kernel is a place where a feature states a verdict on its own authority (section 3).

The kernel's size is the number of distinct source lines in the spec and wrap of all paths of
tier `kernel`. Nothing here is a hand-kept classification: change the registry or the Lean and
the number moves.

    python3 tools/kernel_closure.py                    # table for every path, and the kernel total
    python3 tools/kernel_closure.py --out FILE         # also save the full measurement as JSON
    python3 tools/kernel_closure.py --check FILE       # exit 1 if the kernel total exceeds FILE's

Needs a built `lean/.lake` (`lake build VE`); runs `lake env lean` once (minutes on a loaded host).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "tools" / "kernel-paths.json"


def covered(ranges) -> int:
    """Distinct lines in a set of inclusive (module, first, last) ranges."""
    by_module: dict[str, list[tuple[int, int]]] = {}
    for module, first, last in ranges:
        by_module.setdefault(module, []).append((first, last))
    total = 0
    for spans in by_module.values():
        high = 0
        for first, last in sorted(spans):
            if last <= high:
                continue
            total += last - max(first, high + 1) + 1
            high = last
    return total


def requests(registry: dict) -> list[dict]:
    """The closure requests of a registry: per path, `spec:<name>` and `wrap:<name>`."""
    out = []
    for path in registry["paths"]:
        subject = path.get("subject", [])
        out.append({"name": "spec:" + path["name"], "roots": path["theorems"], "opaque": subject})
        cut = subject + path.get("delegates", []) + [x["name"] for x in path.get("nonverdict", [])]
        out.append({"name": "wrap:" + path["name"], "roots": path["entry"], "opaque": cut, "mode": "run"})
        if path.get("tier") == "kernel":
            out.append({"name": "body:" + path["name"], "roots": subject, "opaque": [], "mode": "run"})
    return out


def run_lean(paths: list[dict], tokens: list[str], imports: list[str], timeout: float) -> tuple[dict, list[dict]]:
    """Run the Lean half over `VE`, the service protocol and the registry's extra `imports` (modules that
    hold a listed theorem and that only `VE.Audit` imports)."""
    with tempfile.TemporaryDirectory() as tmp:
        cfg, out, program = Path(tmp) / "cfg.json", Path(tmp) / "out.json", Path(tmp) / "kernel_closure.lean"
        cfg.write_text(json.dumps({"out": str(out), "paths": paths, "census": tokens}))
        program.write_text("".join(f"import {module}\n" for module in imports)
                           + (ROOT / "tools/kernel_closure.lean").read_text())
        env = dict(os.environ, VE_KC_CFG=str(cfg))
        env["PATH"] = str(Path.home() / ".elan/bin") + os.pathsep + env.get("PATH", "")
        done = subprocess.run(("lake", "env", "lean", str(program)), cwd=ROOT / "lean", env=env,
                              capture_output=True, text=True, timeout=timeout)
        if done.returncode != 0 or not out.exists():
            raise SystemExit(f"kernel_closure.lean failed ({done.returncode}):\n{done.stdout[-2000:]}{done.stderr[-2000:]}")
        answer = json.loads(out.read_text())
        return {p["name"]: p for p in answer["paths"]}, answer["census"]


def measure(registry: dict, timeout: float = 3600) -> dict:
    """Per path: spec and wrap lines; and the kernel tier's distinct-line total."""
    raw, census = run_lean(requests(registry), registry.get("verdict_tokens", []), registry.get("imports", []), timeout)
    rows, kernel_ranges, problems, covered_starts = [], [], [], set()
    for path in registry["paths"]:
        spec, wrap = raw["spec:" + path["name"]], raw["wrap:" + path["name"]]
        for part in (spec, wrap):
            if part["missing"]:
                problems.append(f"{path['name']}: not in the environment: {', '.join(part['missing'])}")
            if part["flagged"]:
                problems.append(f"{path['name']}: replaced or opaque definitions on the path: "
                                + ", ".join(f"{x['name']} ({x['why']})" for x in part["flagged"]))
        ranges = [(d["module"], d["from"], d["to"]) for part in (spec, wrap) for d in part["decls"]]
        if path.get("tier") == "kernel":
            kernel_ranges += ranges
            covered_starts |= {(d["module"], d["from"]) for d in raw["body:" + path["name"]]["decls"]}
        rows.append({"name": path["name"], "tier": path.get("tier", "candidate"), "modes": path.get("modes", []),
                     "theorems": len(path["theorems"]), "spec_lines": spec["lines"], "wrap_lines": wrap["lines"],
                     "lines": covered(ranges), "axioms": sorted(set(spec["axioms"]) | set(wrap["axioms"])),
                     "spec_modules": spec["modules"], "wrap_modules": wrap["modules"]})
    inside = {(module, first) for module, first, _ in kernel_ranges} | covered_starts
    writers = sorted(({"name": w["name"], "module": w["module"], "tokens": w["tokens"],
                       "in_kernel": (w["module"], w["from"]) in inside}
                      for w in census if not is_fixture(w["module"])), key=lambda w: (w["module"], w["name"]))
    return {"kernel_lines": covered(kernel_ranges), "paths": rows, "problems": problems, "verdict_writers": writers}


def is_fixture(module: str) -> bool:
    """Example, check and fixture modules compute no service answer."""
    last = module.rsplit(".", 1)[-1]
    return last.endswith(("Examples", "Checks", "Fixtures")) or module.startswith("ResponseShape")


def table(result: dict) -> str:
    lines = [f"{'path':<14}{'tier':<11}{'theorems':>9}{'spec':>8}{'wrap':>8}{'lines':>8}  modes"]
    for row in result["paths"]:
        lines.append(f"{row['name']:<14}{row['tier']:<11}{row['theorems']:>9}{row['spec_lines']:>8}"
                     f"{row['wrap_lines']:>8}{row['lines']:>8}  {', '.join(row['modes'])}")
    lines.append(f"kernel (distinct lines of every path of tier kernel): {result['kernel_lines']}")
    outside = [w for w in result["verdict_writers"] if not w["in_kernel"]]
    lines.append(f"definitions that write a verdict token: {len(result['verdict_writers'])}, of them outside the kernel: "
                 f"{len(outside)} in {len({w['module'] for w in outside})} modules")
    lines += ["problem: " + p for p in result["problems"]]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path, help="a saved measurement; fail if the kernel total is above its")
    parser.add_argument("--timeout", type=float, default=3600)
    args = parser.parse_args(argv)
    result = measure(json.loads(args.registry.read_text()), args.timeout)
    print(table(result))
    if args.out:
        args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    if result["problems"]:
        return 1
    if args.check:
        allowed = json.loads(args.check.read_text())["kernel_lines"]
        if result["kernel_lines"] > allowed:
            print(f"FAIL: the kernel grew from {allowed} to {result['kernel_lines']} lines "
                  "(docs/spec/kernel-boundary.md, section 6: shrink it, or have the architect sign the new total)")
            return 1
        print(f"PASS: kernel {result['kernel_lines']} <= {allowed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
