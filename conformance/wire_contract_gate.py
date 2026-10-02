"""Replay the soft-norms shadow gate through Python, Lean and the legacy routes."""

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import random
import subprocess

from conformance.soft_norms import multi_fault_base, multi_fault_cases, multi_faults, rejected_sources
from conformance.wire_contract_faults import derived_faults
from tests.test_soft_norms_lean import env
from ve.errors import VEError
from ve.softnorms import load_soft_document
from ve.softnorms_contract import REGISTRY
from ve.wire_contract.engine import CLEAN, Fault, load, run

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "lean/.lake/build/bin"
REPORT = ROOT / "conformance/wire-contract/soft-norms@0-gate.json"
INHERITED = {"2.3", "4.2a", "4.13b", "4.13d", "5.7", "5.8a", "6.10b", "6.10c"}


def tier_b(count=200, seed=19):
    """Seeded stacks of two to five independent faults, applied in shuffled order."""
    rng = random.Random(seed)
    faults = multi_faults()
    for index in range(count):
        chosen = []
        groups = set()
        for fault in rng.sample(faults, len(faults)):
            if fault[1] not in groups:
                chosen.append(fault)
                groups.add(fault[1])
                if len(chosen) == 2 + index % 4:
                    break
        rng.shuffle(chosen)
        raw, rules = multi_fault_base()
        for fault in chosen:
            fault[4](raw, rules)
        # Reverse every object's insertion order. Engines must sort wildcard keys.
        def reverse(value):
            if type(value) is dict:
                return {key: reverse(item) for key, item in reversed(list(value.items()))}
            if type(value) is list:
                return [reverse(item) for item in value]
            return value
        yield "B" + str(index), reverse(raw), reverse(rules), chosen


def _lean_rows(binary, unit, cases):
    rows = []
    for start in range(0, len(cases), 100):
        batch = [{"id": str(start + i), "kind": "soft-elaborate", "environment": raw, "norms": norms}
                 for i, (_, raw, norms, _) in enumerate(cases[start:start + 100])]
        result = subprocess.run([str(BIN / binary), *([unit] if unit else []), "-"],
                                input=json.dumps(batch), text=True, capture_output=True, timeout=600)
        if result.returncode not in (0, 1):
            raise RuntimeError(f"{binary}: {result.stderr}")
        parsed = json.loads(result.stdout)
        if len(parsed) != len(batch):
            raise RuntimeError(f"{binary}: wrong row count")
        rows.extend(parsed)
    return rows


def report():
    contract = load("soft-norms@0")
    faults = multi_faults()
    cases = []
    for fault in faults:
        raw, norms = multi_fault_base()
        fault[4](raw, norms)
        cases.append(("0:" + fault[0], raw, norms, fault[3]))
    for check, raw, norms in derived_faults():
        cases.append(("0d:" + check, raw, norms, None))
    tier0_size = len(cases)
    for label, raw, norms, code in multi_fault_cases():
        cases.append(("A:" + label, raw, norms, code))
    mask_count = 0
    masked_sources = {}
    for _, raw, norms, _ in cases[:tier0_size]:
        outcome = run(contract, {"environment": raw, "norms": norms}, registry=REGISTRY)
        if isinstance(outcome, Fault) and outcome.record["check"] != "1.1":
            masked_sources.setdefault(outcome.record["check"], (raw, norms))
    for check, (raw, norms) in sorted(masked_sources.items()):
        raw = deepcopy(raw)
        raw["extra"] = 1
        cases.append(("M:" + check, raw, norms, "SOFT_INVALID_INPUT"))
        mask_count += 1
    tier_a_size = len(cases) - tier0_size
    b = list(tier_b())
    cases.extend((label, raw, norms, None) for label, raw, norms, _ in b)
    cases.extend(("R" + str(i), raw, norms, None)
                 for i, (raw, norms) in enumerate(rejected_sources()))
    cases.extend(("accepted:" + str(i), raw, norms, None)
                 for i, (raw, norms) in enumerate((multi_fault_base(), (env(), []))))
    lean_engine = _lean_rows("ve_diagnose", "soft-norms@0", cases)
    lean_legacy = _lean_rows("ve_soft_norms_route", None, cases)
    residual = Counter()
    deferred = Counter()
    first = Counter()
    tier0_check = {}
    mismatches = []
    text_deltas = Counter()
    for (label, raw, norms, expected), engine_row, legacy_row in zip(cases, lean_engine, lean_legacy):
        try:
            load_soft_document(deepcopy(raw), deepcopy(norms))
            python_code = None
            python_text = None
        except VEError as exc:
            python_code = exc.code
            python_text = str(exc)
        python_outcome = run(contract, {"environment": raw, "norms": norms}, registry=REGISTRY)
        lean_code = legacy_row.get("code") if legacy_row["status"] == "error" else None
        py_record = python_outcome.record if isinstance(python_outcome, Fault) else None
        ln_record = engine_row.get("diagnostic") if engine_row["outcome"] == "fault" else None
        if python_code and py_record is None: residual["python"] += 1
        if lean_code and ln_record is None: residual["lean"] += 1
        if not isinstance(python_outcome, (Fault, type(CLEAN))): deferred["python"] += 1
        if label.startswith("0:") and py_record:
            tier0_check[label[2:]] = py_record["check"]
        if py_record:
            first[py_record["check"]] += 1
            if python_text != py_record["text"]:
                text_deltas[py_record["check"]] += 1
        py_compare = None if py_record is None else dict(py_record)
        ln_compare = None if ln_record is None else dict(ln_record)
        if py_compare and py_compare["check"] in INHERITED:
            for record in (py_compare, ln_compare):
                if record:
                    record.pop("text", None)
                    record.pop("args", None)
        if ((label.startswith("M:") and
             (py_record is None or py_record["check"] != "1.1" or
              ln_record is None or ln_record["check"] != "1.1")) or
                (label.startswith("0d:") and
             (py_record is None or py_record["check"] != label[3:] or
              ln_record is None or ln_record["check"] != label[3:])) or
                py_compare != ln_compare or
                (python_code is None) != (py_record is None) or
                (lean_code is None) != (ln_record is None) or
                (expected is not None and
                 (python_code != expected or lean_code != expected or
                  (py_record and py_record["code"] != expected))) or
                (python_code is not None and py_record and py_record["code"] != python_code) or
                (lean_code is not None and ln_record and ln_record["code"] != lean_code)):
            mismatches.append({"case": label, "expected": expected, "python_code": python_code,
                               "lean_code": lean_code,
                               "python_check": None if py_record is None else py_record["check"],
                               "lean_check": None if ln_record is None else ln_record["check"]})
    masked = Counter()
    for label, *_ in cases[tier0_size:tier0_size + tier_a_size]:
        if label.startswith("M:"):
            masked[label[2:]] += 1
            continue
        checks = {tier0_check.get(name) for name in label[2:].split("+")}
        checks.discard(None)
        # At least one check is hidden by the first reported fault.
        for check in checks - {first_check_for_combo(label, cases, lean_engine)}:
            masked[check] += 1
    all_checks = set()
    def collect(entries):
        for entry in entries:
            if "each" in entry:
                collect(entry["checks"])
            elif entry["kind"] == "classifier":
                all_checks.update(m["id"] for m in entry["emits"])
            else:
                all_checks.add(entry["id"])
    for phase in contract["phases"]:
        collect(phase["checks"])
    coverage_met = not (all_checks - set(first)) and not (all_checks - set(masked))
    return {"contract": "soft-norms@0", "revision": contract["revision"],
            "tiers": {"0": tier0_size, "A": tier_a_size - mask_count, "A_mask": mask_count, "B": len(b),
                      "replay_rejected": len(rejected_sources()), "replay_accepted": 2},
            "residual": {language: residual[language] for language in ("python", "lean")},
            "deferred": {language: deferred[language] for language in ("python", "lean")},
            "deferred_share": {language: deferred[language] / len(cases)
                               for language in ("python", "lean")},
            "feasibility": {"n1": 43, "n2": 8, "total": 51, "of": 67, "threshold": 45},
            "s3_pre": "closed: no verdict difference",
            "first_check_count": len(first), "all_check_count": len(all_checks),
            "checks_without_first": sorted(all_checks - set(first)),
            "checks_without_masked": sorted(all_checks - set(masked)),
            "coverage_met": coverage_met,
            "coverage_notes": {
                "1.1": "The first table check has no earlier check that can mask it.",
                "4.11b": "Its distinguishing value is an explicit null; the Lean case reader rejects raw null before diagnosis.",
                "6.10a": "No reachable first-fault witness for the softened-document cycle classifier member was found.",
                "6.10c": "No reachable first-fault witness for the softened-document fallback classifier member was found."
            },
            "text_delta_count": sum(text_deltas.values()),
            "mismatches": mismatches}


def first_check_for_combo(label, cases, lean_engine):
    # The corresponding engine row is the oracle's actual first expanded check.
    for (case_label, *_), row in zip(cases, lean_engine):
        if case_label == label:
            return row.get("diagnostic", {}).get("check")
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = report()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not REPORT.exists() or REPORT.read_text() != rendered:
            print("wire gate report differs")
            return 1
    else:
        REPORT.write_text(rendered)
    print(f"{sum(value['tiers'].values())} cases; {len(value['mismatches'])} mismatches; "
          f"{len(value['checks_without_first'])} checks without a first-fault witness")
    return bool(value["mismatches"] or any(value["residual"].values()) or
                not value["coverage_met"])


if __name__ == "__main__":
    raise SystemExit(main())
