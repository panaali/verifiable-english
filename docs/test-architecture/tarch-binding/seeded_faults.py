"""Seeded faults at hand binders' boundaries, judged end to end (tarch-binding, part 3; evidence pinned at a commit).

    uv run python docs/test-architecture/tarch-binding/seeded_faults.py docs/test-architecture/tarch-binding/seeded-faults.json

For each binder below, the fault disables its check (a temporary edit of the product file, restored after the
run). Then:

* `tests_failing`: the consumer tests that fail with the fault in place (the hand tests that catch it);
* `mutants`: every mutant this binder refused in the recorded probe (`docs/test-architecture/binding-probes.jsonl.gz`),
  delivered again on the wire (`tools/binding_census.py --probe --wire`: the shape check first, as the service
  would), with the binder disabled. `wire` means the generic checker refuses it before any consumer sees it (the
  fault is caught by the generic layer); `hand` that another hand check still refuses it; anything else that the
  fault lets it through to the consumer (`passed`: accepted silently; `AssertionError`: the test saw a wrong answer;
another exception: a crash). `not reached` and `FileExistsError` are inconclusive (`INCONCLUSIVE`).

A binder is retirable later, on this evidence, only if every one of its mutants is `wire`.
"""
from __future__ import annotations

from collections import Counter
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import binding_census  # noqa: E402
import nested_pytest  # noqa: E402

# binder: (file, the check's text, its replacement, mode, consumer tests)
FAULTS = {
    "ve/discourse.py:_bind_joint": (
        "ve/discourse.py", '    product = 1\n    for rs in open_sets:\n        product *= len(rs["readings"])\n',
        '    return\n    product = 1\n    for rs in open_sets:\n        product *= len(rs["readings"])\n', "discourse",
        ("tests/test_discourse_answer.py", "tests/test_discourse_lean.py", "tests/test_discourse.py")),
    "ve/rights.py:__init__": (
        "ve/rights.py", '                    raise ValueError("rights line binding")',
        '                    pass  # seeded fault', "rights", ("tests/test_rights_lean.py", "tests/test_rights.py")),
    "ve/admission.py:bound_admission": (
        "ve/admission.py", '        raise CheckerUnavailable("CheckerUnavailable: the Lean admission answer is not bound to '
                           'the request")',
        '        pass  # seeded fault', "route",
        ("tests/test_stage2_norms.py", "tests/test_stage2_validation.py", "tests/test_alternatives_profile.py")),
    "ve/reports.py:_load_statuses": (
        "ve/reports.py", '                raise CheckerUnavailable(f"Lean returned report statuses for different {field}")',
        '                pass  # seeded fault', "reports", ("tests/test_reports_lean.py",)),
    "ve/backends/english_lean.py:check": (
        "ve/backends/english_lean.py", '        raise CheckerUnavailable("CheckerUnavailable: malformed English check row")',
        '        pass  # seeded fault', "english.check", ("tests/test_english_lean_route.py",)),
}


def _failing(tests) -> list[str]:
    done = subprocess.run(nested_pytest.command(["-q", "-rf", "-p", "no:cacheprovider", *tests], workers=8),
                          cwd=ROOT, env=nested_pytest.environment(os.environ), capture_output=True, text=True)
    return sorted(line.split()[1] for line in done.stdout.splitlines() if line.startswith("FAILED "))


def _refused_by(binder: str) -> set[tuple]:
    out = set()
    for probe in binding_census.load_probes():
        if probe["refused"] == "hand" and probe.get("site") and binding_census._site_key(probe["site"]) == binder:
            out.add((probe["mode"], probe["kind"], probe["path"], probe["generic"]))
    return out


def run(binder: str) -> dict:
    path, old, new, mode, tests = FAULTS[binder]
    target = ROOT / path
    source = target.read_text()
    assert source.count(old) == 1, f"{binder}: the check's text is not in {path} once"
    refused = _refused_by(binder)
    try:
        target.write_text(source.replace(old, new))
        failing = _failing(tests)
        with tempfile.TemporaryDirectory(prefix="seeded-wire-") as directory:
            os.environ["VE_BINDING_PROBE_MODES"] = ",".join(sorted({m for m, _, _, _ in refused} | {mode}))
            binding_census.probe(Path(directory), list(tests), 8, wire=True)
            lines = [json.loads(line) for file in Path(directory).glob("probe-*.jsonl")
                     for line in file.read_text().splitlines() if line.strip()]
    finally:
        target.write_text(source)
        os.environ.pop("VE_BINDING_PROBE_MODES", None)
    seeded: dict = {}
    for line in lines:
        if "genuine" in line or "error" in line:
            continue
        probe = binding_census._attributed(line)
        key = (probe["mode"], probe["kind"], probe["path"])
        outcome = probe["refused"] or probe["outcome"]
        if probe["refused"] == "hand":
            outcome = f"hand {binding_census._site_key(probe['site'])}"
        seeded.setdefault(key, set()).add(outcome)
    mutants = []
    for mode_, kind, mutant_path, generic in sorted(refused):
        outcomes = sorted(seeded.get((mode_, kind, mutant_path), {"not reached"}))
        mutants.append({"mode": mode_, "kind": kind, "path": mutant_path, "generic": generic, "seeded": outcomes})
    return summarise({"binder": binder, "fault": {"file": path, "check": old.strip(), "replaced_by": new.strip()},
                      "tests_failing": failing, "mutants": mutants})


# Outcomes that say nothing about the fault: the mutant was not delivered again, or the child failed on the
# directory an earlier child of the same test had created (children share the parent's tmp_path).
INCONCLUSIVE = ("not reached", "FileExistsError")


def summarise(fault: dict) -> dict:
    """The counts of one fault's outcomes, whether the generic checker caught every mutant the binder refused,
    and how many reached the consumer (accepted, observed by the test as a wrong answer, or a crash)."""
    mutants = fault["mutants"]
    stopped = lambda o: o == "wire" or o.startswith("hand ") or o == "transport" or o in INCONCLUSIVE  # noqa: E731
    return {**fault, "summary": dict(sorted(Counter(o for m in mutants for o in m["seeded"]).items())),
            "caught_by_the_generic_checker": all(m["seeded"] == ["wire"] for m in mutants),
            "reaches_the_consumer": sum(1 for m in mutants if not all(stopped(o) for o in m["seeded"])),
            "inconclusive": sum(1 for m in mutants if all(o in INCONCLUSIVE for o in m["seeded"]))}


def main(argv=None) -> int:
    """Run every fault and write the evidence to the path given (the nested test runs print to stdout)."""
    [out] = argv if argv is not None else sys.argv[1:]
    evidence = {"comment": __doc__.split("\n")[0], "faults": [run(binder) for binder in FAULTS]}
    Path(out).write_text(json.dumps(evidence, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
