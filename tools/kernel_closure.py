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

A subject is what the theorems are about only if some listed theorem states its answer (a hypothesis
`subject … = .ok answer` whose answer the theorem uses again, or `subject … = true`); the tool reports
a kernel subject with none, since the code under it would then be uncounted wrap.

It also lists the **verdict writers**: every definition whose body holds one of the registry's
`verdict_tokens` as a string literal, and whether it lies inside the kernel: in a kernel path's
spec or wrap, or in the code a kernel subject runs for a case kind a listed theorem covers (the
registry's `covered_writers` names each such writer with its kind and theorem; code for kinds no
theorem covers is `uncovered` and stays outside). A writer outside the kernel is a place where a
feature states a verdict on its own authority (section 3).

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


def uncovered_names(registry: dict) -> list[str]:
    """Code a kernel subject runs for case kinds no listed theorem covers (`uncovered`). It is outside
    the kernel whichever subject runs it, so every subject's body is cut there."""
    return [x["name"] for path in registry["paths"] if path.get("tier") == "kernel"
            for x in path.get("uncovered", [])]


def requests(registry: dict) -> list[dict]:
    """The closure requests of a registry: per path, `spec:<name>` and `wrap:<name>`; per kernel path
    also `body:<name>`, the code its subjects run for the case kinds its theorems cover."""
    out = []
    uncovered = uncovered_names(registry)
    for path in registry["paths"]:
        subject = path.get("subject", [])
        out.append({"name": "spec:" + path["name"], "roots": path["theorems"], "opaque": subject})
        cut = subject + path.get("delegates", []) + [x["name"] for x in path.get("nonverdict", [])]
        out.append({"name": "wrap:" + path["name"], "roots": path["entry"], "opaque": cut, "mode": "run"})
        if path.get("tier") == "kernel":
            out.append({"name": "body:" + path["name"], "roots": subject, "opaque": uncovered, "mode": "run"})
    for name, entry in registry.get("keys", {}).get("validators", {}).items():
        out.append({"name": "keys:" + name, "roots": entry, "opaque": [], "mode": "run"})
    return out


def keyed(registry: dict, ranges_of: dict, validator_ranges: dict, kernel_ranges: list) -> dict:
    """The frozen keys' figures: the distinct lines under their answers (spec and wrap of each keyed
    path, each validator's whole run closure) and how many of them lie in the kernel."""
    keys = registry.get("keys", {})
    if not keys:
        return {}
    under = [r for name in keys["paths"] for r in ranges_of[name]]
    under += [r for name in keys.get("validators", {}) for r in validator_ranges[name]]
    total, kernel = covered(under), covered(kernel_ranges)
    return {"keyed_lines": total, "keyed_kernel_lines": total + kernel - covered(under + kernel_ranges)}


def registry_problems(registry: dict) -> list[str]:
    """What the registry itself gets wrong, before any Lean is read: a `covered_writers` entry must name
    the case kinds it writes for and theorems of its own path; an `uncovered` entry its kinds and a
    reason; both belong to kernel paths only (a candidate path's subjects have no census body)."""
    problems = []
    for path in registry["paths"]:
        name, kernel = path["name"], path.get("tier") == "kernel"
        for entry in path.get("covered_writers", []):
            if not kernel:
                problems.append(f"{name}: covered_writers on a candidate path: {entry.get('name')}")
            if not entry.get("kinds") or not entry.get("theorems"):
                problems.append(f"{name}: covered writer {entry.get('name')} names no case kind or no theorem")
            for theorem in entry.get("theorems", []):
                if theorem not in path["theorems"]:
                    problems.append(f"{name}: covered writer {entry.get('name')} cites {theorem}, not a theorem of the path")
        for entry in path.get("uncovered", []):
            if not kernel:
                problems.append(f"{name}: uncovered on a candidate path: {entry.get('name')}")
            if not entry.get("kinds") or len(entry.get("why", "")) <= 20:
                problems.append(f"{name}: uncovered {entry.get('name')} names no case kind or no reason")
    names = {path["name"] for path in registry["paths"]}
    problems += [f"keys: {name} is not a path of the registry"
                 for name in registry.get("keys", {}).get("paths", []) if name not in names]
    return problems


def subject_problems(path: dict, stated: dict) -> list[str]:
    """Section 2: a kernel path's theorems say what its subject's answer means. `stated` maps each
    subject to the listed theorems whose statement uses its answer (the Lean half's `answersStated`).
    A subject that only gate theorems mention (`subject j = .ok r → P j`, `r` unused) is not a subject:
    the code under it is wrap, and the path is a candidate until a theorem states the answer."""
    if path.get("tier") != "kernel":
        return []
    return [f"{path['name']}: no listed theorem states what the answer of {subject} means"
            for subject in path.get("subject", []) if not stated.get(subject)]


def classify_writers(census: list[dict], spec_wrap: set, body: set, covered: set) -> tuple[list[dict], list[str]]:
    """Section 3's census. A writer is inside the kernel when its declaration is in a kernel path's spec
    or wrap (`inside: "spec-or-wrap"`), or in code a kernel subject runs for a case kind a listed theorem
    covers (`inside: "body"`). A body writer is inside only if the registry's `covered_writers` names it
    with its kind and theorem; one it does not name is reported, never counted inside silently."""
    rows, problems = [], []
    for w in census:
        if is_fixture(w["module"]):
            continue
        at = (w["module"], w["from"])
        inside = "spec-or-wrap" if at in spec_wrap else "body" if at in body else None
        if inside == "body" and w["name"] not in covered:
            problems.append(f"verdict writer {w['name']} runs under a kernel subject, but no covered_writers entry "
                            "names the case kind and theorem that cover it (list it there, or as uncovered)")
            inside = None
        rows.append({"name": w["name"], "module": w["module"], "tokens": w["tokens"],
                     "in_kernel": inside is not None, "inside": inside})
    named = {w["name"] for w in rows if w["inside"] == "body"}
    problems += [f"covered_writers names {n}, which is not a verdict writer reached only through a kernel subject"
                 for n in sorted(covered - named)]
    return sorted(rows, key=lambda w: (w["module"], w["name"])), problems


def check_total(result: dict, allowed: int) -> tuple[bool, str]:
    """Section 6: the kernel total may not exceed the saved one."""
    if result["kernel_lines"] > allowed:
        return False, (f"FAIL: the kernel grew from {allowed} to {result['kernel_lines']} lines "
                       "(docs/spec/kernel-boundary.md, section 6: shrink it, or have the architect sign the new total)")
    return True, f"PASS: kernel {result['kernel_lines']} <= {allowed}"


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
    rows, kernel_ranges, body_starts, ranges_of = [], [], set(), {}
    problems = registry_problems(registry)
    for path in registry["paths"]:
        spec, wrap = raw["spec:" + path["name"]], raw["wrap:" + path["name"]]
        parts = [spec, wrap] + ([raw["body:" + path["name"]]] if path.get("tier") == "kernel" else [])
        for part in parts:
            if part["missing"]:
                problems.append(f"{path['name']}: not in the environment: {', '.join(part['missing'])}")
            if part["flagged"]:
                problems.append(f"{path['name']}: replaced or opaque definitions on the path: "
                                + ", ".join(f"{x['name']} ({x['why']})" for x in part["flagged"]))
        for part in (spec, wrap):
            if part["unranged"]:
                problems.append(f"{path['name']}: reached constants with no source range (not counted): "
                                + ", ".join(part["unranged"]))
        problems += subject_problems(path, spec["stated"])
        ranges = [(d["module"], d["from"], d["to"]) for part in (spec, wrap) for d in part["decls"]]
        ranges_of[path["name"]] = ranges
        if path.get("tier") == "kernel":
            kernel_ranges += ranges
            body_starts |= {(d["module"], d["from"]) for d in raw["body:" + path["name"]]["decls"]}
        rows.append({"name": path["name"], "tier": path.get("tier", "candidate"), "modes": path.get("modes", []),
                     "theorems": len(path["theorems"]), "spec_lines": spec["lines"], "wrap_lines": wrap["lines"],
                     "lines": covered(ranges), "axioms": sorted(set(spec["axioms"]) | set(wrap["axioms"])),
                     "stated": spec["stated"], "spec_modules": spec["modules"], "wrap_modules": wrap["modules"]})
    covered_writers = {x["name"] for path in registry["paths"] if path.get("tier") == "kernel"
                       for x in path.get("covered_writers", [])}
    writers, census_problems = classify_writers(census, {(module, first) for module, first, _ in kernel_ranges},
                                                body_starts, covered_writers)
    validator_ranges = {}
    for name in registry.get("keys", {}).get("validators", {}):
        part = raw["keys:" + name]
        if part["missing"] or part["unranged"]:
            problems.append(f"keys: validator {name}: missing {part['missing']}, unranged {part['unranged']}")
        validator_ranges[name] = [(d["module"], d["from"], d["to"]) for d in part["decls"]]
    return {"kernel_lines": covered(kernel_ranges), "paths": rows, "problems": problems + census_problems,
            "verdict_writers": writers, **keyed(registry, ranges_of, validator_ranges, kernel_ranges)}


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
    if "keyed_lines" in result:
        lines.append(f"under the frozen keys' answers: {result['keyed_lines']}, "
                     f"of them in the kernel: {result['keyed_kernel_lines']}")
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
        ok, message = check_total(result, json.loads(args.check.read_text())["kernel_lines"])
        print(message)
        if not ok:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
