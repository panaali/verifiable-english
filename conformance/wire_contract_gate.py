"""Replay the soft-norms shadow gate (wire-contract.md 8.3 and 9) through Python, Lean and the legacy routes.

The oracle is the fault catalogue (`conformance/wire_contract_faults.py`): each fault's expected check and
path are written by hand, its table position is read from the contract, and a combination of faults with
disjoint footprints expects the record of the fault of least position. No expectation, and no masking
witness, is read from an engine's output. Tier 0 and tier A compare both engines' records with the expected
record: every field, with `text` rendered from the contract's template and the catalogue's hand-written
`args`; for an inherited check, whose text is each language's own (section 6), `text` is that language's
legacy text and `args` is `{"message": text}`. They also compare the engines with each other on the whole
record (but `text` and `args` of inherited checks), each engine's code with its legacy validator's, and
Lean's text with the Lean route's for the checks whose text is the contract's. Tier B and the replayed corpora check that the engines agree
and that each reports a fault exactly when its legacy validator rejects. Every engine record, in every tier, has
exactly the fault record's members (2.7), each of the schema's type. The gate exits non-zero unless every
required row of spec 9 holds (`gate_failures`), each judged from the data the report summarizes and not from
the report's own verdicts: coverage from the unmet lists, S3-pre from the legacy verdict differences, and
feasibility from `n1 + n2` against 45 of 67, the tier counts partitioning the 67.
"""

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import random
import re
import subprocess

from conformance.soft_norms import (RUST_FIXTURES, combined_invalid_soft_blocks, generated,
                                    generated_invalid_soft_blocks, generated_invalid_soft_rules, multi_fault_base,
                                    multi_fault_cases, rejected_sources, soft3_accepted, soft3_reproducers)
from conformance.wire_contract import choose_combinations
from conformance.wire_contract_faults import (UNREACHED, catalogue, expected_first, expected_record,
                                              footprint, legacy_codes, overlaps, position)
from tests.test_soft_norms_lean import env
from ve.errors import VEError
from ve.softnorms import load_soft_document
from ve.softnorms_contract import REGISTRY
from ve.wire_contract.engine import Deferred, Fault, load, run

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "lean/.lake/build/bin"
REPORT = ROOT / "conformance/wire-contract/soft-norms@0-gate.json"
EXAMPLES = ROOT / "ve/wire_contract/examples/soft-norms@0"
EXPECTED_FIELDS = ("contract", "revision", "check", "phase", "code", "class", "path")
# The fault record's members (2.7; `contract.schema.json`, `$defs/fault`, closed to others).
RECORD_FIELDS = frozenset(EXPECTED_FIELDS + ("text", "args"))
# Spec 9: feasibility is `n1 + n2` out of the 67 numbered checks of soft-norms.md 8, required at least 45.
FEASIBILITY_OF = 67
FEASIBILITY_THRESHOLD = 45
# The profiles that Python's registry has and the Lean route's does not (s3-pre.md). Both legacy validators
# reject a soft source that lists any of them; the codes differ on two.
PYTHON_ONLY_PROFILES = ("alternatives@0", "norm-defaults@0", "reports@0", "rights@0", "risk@0",
                        "speech-acts@0")


def inherited_checks(contract):
    """The checks and members whose text and args are the inherited decoder's (2.5, rule 5)."""
    found = set()
    def walk(entries):
        for entry in entries:
            if "each" in entry:
                walk(entry["checks"])
            elif entry.get("kind") == "classifier":
                found.update(m["id"] for m in entry["emits"] if m.get("inherited"))
            elif entry.get("inherited"):
                found.add(entry["id"])
    for phase in contract["phases"]:
        walk(phase["checks"])
    return found


def inherited_texts(contract):
    """The templates of the inherited checks and members."""
    found = []
    def walk(entries):
        for entry in entries:
            if "each" in entry:
                walk(entry["checks"])
            elif entry.get("kind") == "classifier":
                found.extend(m["text"] for m in entry["emits"] if m.get("inherited"))
            elif entry.get("inherited"):
                found.append(entry["text"])
    for phase in contract["phases"]:
        walk(phase["checks"])
    return found


def all_checks(contract):
    found = []
    def walk(entries):
        for entry in entries:
            if "each" in entry:
                walk(entry["checks"])
            elif entry.get("kind") == "classifier":
                found.extend(m["id"] for m in entry["emits"])
            elif entry.get("kind") != "include":
                found.append(entry["id"])
    for phase in contract["phases"]:
        walk(phase["checks"])
    return found


def feasibility(contract):
    """Spec 9: each numbered check of soft-norms.md 8 counts by its weakest sub-entry, in the order T3,
    inherited hook (or include under a view), T2, T1; `n1` counts the T1 ones and `n2` the T2 ones."""
    strength = {"T1": 0, "T2": 1, "coarse": 2, "T3": 3}
    tiers = {}
    def number(check):
        return re.match(r"\d+\.\d+", check)[0]
    def walk(entries, viewed=False):
        for entry in entries:
            if "each" in entry:
                walk(entry["checks"], viewed)
            elif entry.get("kind") == "classifier":
                for member in entry["emits"]:
                    tiers[number(member["id"])] = "T3"
            elif entry.get("kind") == "include":
                continue
            else:
                tier = ("coarse" if entry.get("inherited") or viewed else
                        "T2" if entry["kind"] == "hook" else "T1")
                key = number(entry["id"])
                tiers[key] = max(tiers.get(key, "T1"), tier, key=strength.get)
    for phase in contract["phases"]:
        walk(phase["checks"])
    counts = Counter(tiers.values())
    return {"n1": counts["T1"], "n2": counts["T2"], "coarse": counts["coarse"], "t3": counts["T3"],
            "total": counts["T1"] + counts["T2"], "of": len(tiers), "threshold": FEASIBILITY_THRESHOLD,
            "met": len(tiers) == FEASIBILITY_OF and counts["T1"] + counts["T2"] >= FEASIBILITY_THRESHOLD}


def tier_b(faults, prints, count=200, seed=19):
    """Seeded stacks of two to five faults with disjoint footprints, applied in shuffled order, with every
    object's members reversed. Engines must sort wildcard keys."""
    rng = random.Random(seed)
    def reverse(value):
        if type(value) is dict:
            return {key: reverse(item) for key, item in reversed(list(value.items()))}
        if type(value) is list:
            return [reverse(item) for item in value]
        return value
    for index in range(count):
        chosen = []
        for fault in rng.sample(faults, len(faults)):
            if all(not overlaps(prints[fault.name], prints[other.name]) for other in chosen):
                chosen.append(fault)
                if len(chosen) == 2 + index % 4:
                    break
        rng.shuffle(chosen)
        root = _applied(chosen)
        yield "B" + str(index), reverse(root["environment"]), reverse(root["norms"])


def _applied(faults):
    raw, rules = multi_fault_base()
    root = {"environment": raw, "norms": rules}
    for fault in faults:
        fault.apply(root)
    return root


def replay_sources():
    """The existing corpora (8.3): the contract's examples, the seeded soft sources, the soft conformance
    fixtures and reproducers. Each is replayed whatever its verdict."""
    sources = []
    for path in sorted(EXAMPLES.glob("*.json")):
        value = json.loads(path.read_text())
        sources.append(("example:" + path.stem, value["environment"], value["norms"]))
    sources += [(f"generated:{seed}", *generated(seed)) for seed in range(200)]
    sources += [("soft3-accepted:" + name, raw, rules) for name, raw, rules in soft3_accepted()]
    sources += [(f"rejected:{i}", raw, rules) for i, (raw, rules) in enumerate(rejected_sources())]
    sources += [(f"block:{i}", raw, rules) for i, (raw, rules) in enumerate(generated_invalid_soft_blocks())]
    sources += [(f"blocks:{i}", raw, rules) for i, (raw, rules) in enumerate(combined_invalid_soft_blocks())]
    sources += [(f"rules:{i}", raw, rules) for i, (raw, rules) in enumerate(generated_invalid_soft_rules())]
    sources += [("soft3:" + name, raw, rules) for name, raw, rules, _ in soft3_reproducers()]
    return sources


def test_and_fixture_sources():
    """The `soft-norms@0` inputs of the contract tests (`tests/test_*contract*`) and of the soft conformance
    fixtures, each built by the code that builds it for its test: the base and the pairs and triples of
    `multi_fault_cases()`, the fixtures P1 to P17 (8.3), the shadow cases, probes and admission sources of the
    contract tests, the acceptance fixtures of soft-norms.md 10, and the sources of the Rust fixtures.
    `tests/test_wire_gate_corpus.py` records the inputs the tests actually submit and fails if one is missing
    from the gate's corpus. Imported here, not at the top: the test modules import this one."""
    from tests.test_soft_norms_conformance import fixtures
    from tests.test_softnorms_contract import CASES, admission_case
    from tests.test_wire_contract_faults import SHARED_CODE_PAIR
    from tests.test_wire_contract_precondition import probe_sources
    from tests.test_wire_contract_soft_lean import fixture_sources, s3_pre_sources
    from tests.test_wire_contract_three_way import admission_sources
    from ve.softnorms_contract import soft_source
    by_name = {fault.name: fault for fault in catalogue()}
    pair = _applied([by_name[name] for name in SHARED_CODE_PAIR])
    sources = [("base", *multi_fault_base()), ("shared-code-pair", pair["environment"], pair["norms"])]
    sources += [("multi-fault:" + name, raw, rules) for name, raw, rules, _ in multi_fault_cases()]
    sources += [(f"fixture:{i}", raw, rules) for i, (raw, rules) in enumerate(fixture_sources())]
    sources += [("shadow:" + make.__name__, *make()[:2]) for make in CASES]
    admission = soft_source(admission_case())
    sources += [("admission", admission["environment"], admission["norms"])]
    sources += [(f"admission:{i}", raw, rules) for i, (raw, rules) in enumerate(admission_sources())]
    sources += [(f"probe:{i}", raw, rules) for i, (raw, rules) in enumerate(probe_sources())]
    sources += [(f"s3-pre:{i}", raw, rules) for i, (raw, rules) in enumerate(s3_pre_sources())]
    sources += [("acceptance:" + row[0], row[1], row[2]) for row in fixtures()]
    sources += [("rust:" + row["id"], row["source"]["environment"], row["source"]["norms"])
                for row in json.loads(RUST_FIXTURES.read_text())]
    return sources


def source_key(raw, norms):
    return json.dumps([raw, norms], sort_keys=True)


def legacy_difference_sources(contract):
    """Inputs on which the two legacy validators differed or differ (s3-pre.md), with the record both
    engines must report: every profile outside the Lean route's registry, on `env()` and on the base, the
    `rights@0` source with its `rights` block, and the `unspecified` default under `norm-defaults@0`."""
    cases = []
    for profile in PYTHON_ONLY_PROFILES:
        for label, (raw, rules) in (("env", (env(), [])), ("base", multi_fault_base())):
            raw["profiles"] = sorted(raw["profiles"] + [profile])
            index = raw["profiles"].index(profile)
            expected = {"contract": contract["contract"], "revision": contract["revision"], "check": "3.2",
                        "phase": "profiles", "code": "SOFT_UNSUPPORTED_PROFILE", "class": "UnsupportedProfile",
                        "path": f"/environment/profiles/{index}",
                        "text": f"UnsupportedProfile: Unsupported profile {profile}", "args": {"value": profile}}
            cases.append((f"L:{profile}:{label}", raw, rules, expected))
    # A whole rights source on the soft route: the `rights` block is refused first, at 1.5a, by both.
    raw = env(profiles=("norms@0", "rights@0", "soft-norms@0"))
    raw["vocabulary"]["rights"] = {"holders": ["assistant"], "bearers": ["assistant"], "protected": [],
                                   "alters": {}}
    cases.append(("L:rights@0:block", raw, [], {
        "contract": contract["contract"], "revision": contract["revision"], "check": "1.5a",
        "phase": "envelope", "code": "SOFT_INVALID_INPUT", "class": "InvalidInput",
        "path": "/environment/vocabulary", "text": "InvalidInput: invalid vocabulary", "args": {}}))
    raw = env(profiles=("norms@0", "norm-defaults@0", "soft-norms@0"))
    raw["vocabulary"]["predicates"]["x_required"]["regulated"]["default"] = "unspecified"
    cases.append(("L:norm-defaults@0:unspecified", raw, [], {
        "contract": contract["contract"], "revision": contract["revision"], "check": "2.3",
        "phase": "declarations", "code": "SOFT_INVALID_INPUT", "class": "InvalidInput", "path": "/environment"}))
    return cases


def _schema_types():
    """Each fault record member's JSON type, read from `contract.schema.json` (`$defs/fault`)."""
    schema = json.loads((ROOT / "ve/wire_contract/contract.schema.json").read_text())
    return {name: member["type"] for name, member in schema["$defs"]["fault"]["properties"].items()}


RECORD_TYPES = _schema_types()
# A JSON type's Python values; `bool` is not an integer in JSON, though it is an `int` in Python.
JSON_TYPES = {"string": lambda value: type(value) is str, "integer": lambda value: type(value) is int,
              "object": lambda value: type(value) is dict}


def shape_problems(record):
    """How an engine's fault record departs from the schema's closed shape (2.7): a missing or an extra
    member, or a member of the wrong type. Checked on every record of every tier, so a stray field or a
    non-string `text` that both engines produce is not hidden by their agreeing with each other."""
    if not isinstance(record, dict):
        return [f"record {record!r} is not an object"]
    problems = []
    if set(record) != RECORD_FIELDS:
        problems.append(f"record fields: missing {sorted(RECORD_FIELDS - set(record))}, "
                        f"extra {sorted(set(record) - RECORD_FIELDS)}")
    for name, kind in sorted(RECORD_TYPES.items()):
        if name in record and not JSON_TYPES[kind](record[name]):
            problems.append(f"{name} {record[name]!r} is not of type {kind}")
    return problems


def record_problems(record, expected, legacy):
    """How an engine's record differs from the expected record (8.3, tiers 0 and A): every field of
    `expected`, `text` and `args` included. An expected record without `text` is an inherited check's: its
    text is the language's own decoder text (section 6), which its legacy validator reports as `legacy`
    (code, text), with the one argument `message`; `legacy` None skips that comparison (tier L, whose inputs
    are those on which the two legacy validators differ)."""
    if record is None:
        return [f"expected {expected['check']} {expected['path']}, got clean"]
    if shape_problems(record):
        return shape_problems(record)
    if any(record[key] != expected[key] for key in EXPECTED_FIELDS):
        return [f"expected {expected['check']} {expected['path']}, got {record['check']} {record['path']}"]
    if "text" in expected:
        if (record["text"], record["args"]) != (expected["text"], expected["args"]):
            return [f"text {record['text']!r}, args {record['args']}; expected {expected['text']!r}, "
                    f"{expected['args']}"]
    elif legacy is not None and (record["text"], record["args"]) != (legacy[1], {"message": legacy[1]}):
        return [f"inherited text {record['text']!r}, args {record['args']}; legacy {legacy[1]!r}"]
    return []


def _lean_rows(binary, unit, cases):
    rows = []
    for start in range(0, len(cases), 100):
        batch = [{"id": str(start + i), "kind": "soft-elaborate", "environment": raw, "norms": norms}
                 for i, (raw, norms) in enumerate(cases[start:start + 100])]
        result = subprocess.run([str(BIN / binary), *([unit] if unit else []), "-"],
                                input=json.dumps(batch), text=True, capture_output=True, timeout=600)
        if result.returncode not in (0, 1):
            raise RuntimeError(f"{binary}: {result.stderr}")
        parsed = json.loads(result.stdout)
        if len(parsed) != len(batch):
            raise RuntimeError(f"{binary}: wrong row count")
        rows.extend(parsed)
    return rows


def _python(contract, raw, norms):
    try:
        load_soft_document(deepcopy(raw), deepcopy(norms))
        legacy = None
    except VEError as exc:
        legacy = (exc.code, str(exc))
    outcome = run(contract, {"environment": deepcopy(raw), "norms": deepcopy(norms)}, registry=REGISTRY)
    return legacy, outcome


def gate_cases(contract):
    """The gate's corpus. Each case: (tier, label, raw, norms, expected fields or None, the faults it
    combines, Lean reads it)."""
    faults = catalogue()
    prints = {fault.name: footprint(fault) for fault in faults}
    both = [fault for fault in faults if fault.readers == "both"]
    cases = []
    for fault in faults:
        raw, norms = fault.source()
        cases.append(("0", "0:" + fault.name, raw, norms, expected_record(contract, fault), (fault,),
                      fault.readers == "both"))
    phase_of = {fault.name: position(contract, fault)[0] for fault in faults}
    combos = list(choose_combinations(both, phase=lambda fault: phase_of[fault.name],
                                      footprint=lambda fault: prints[fault.name], overlaps=overlaps))
    for combo in combos:
        root = _applied(combo)
        first = expected_first(contract, combo)
        cases.append(("A", "A:" + "+".join(f.name for f in combo), root["environment"], root["norms"],
                      expected_record(contract, first), combo, True))
    # Masking pairs for the checks no sampled combination masks: the fault with the nearest earlier
    # position among those independent of it. A reproducer replaces the whole source, so the fault applied
    # after it is `language` (1.2), which any source can carry.
    covered = {f.check for combo in combos for f in combo if f is not expected_first(contract, combo)}
    by_name = {fault.name: fault for fault in faults}
    for fault in faults:
        if fault.check in covered and fault.readers == "both":
            continue
        if "whole-source" in fault.labels:
            pair = (fault, by_name["language"])
        else:
            earlier = [other for other in both
                       if position(contract, other) < position(contract, fault)
                       and not overlaps(prints[fault.name], prints[other.name])]
            if not earlier:
                continue
            pair = (fault, max(earlier, key=lambda other: position(contract, other)))
        covered.add(fault.check)
        root = _applied(pair)
        cases.append(("A", f"A-mask:{pair[0].name}+{pair[1].name}", root["environment"], root["norms"],
                      expected_record(contract, pair[1]), pair, fault.readers == "both"))
    cases += [("B", label, raw, norms, None, (), True) for label, raw, norms in tier_b(both, prints)]
    cases += [("R", "R:" + label, raw, norms, None, (), True) for label, raw, norms in replay_sources()]
    differences = legacy_difference_sources(contract)
    cases += [("L", label, raw, norms, expected, (), True) for label, raw, norms, expected in differences]
    # The tests' and fixtures' inputs that no other tier has, each once, replayed with the other corpora.
    seen = {source_key(case[2], case[3]) for case in cases}
    for label, raw, norms in test_and_fixture_sources():
        if source_key(raw, norms) not in seen:
            seen.add(source_key(raw, norms))
            cases.append(("R", "R:test:" + label, raw, norms, None, (), True))
    return cases


def report():
    contract = load("soft-norms@0")
    inherited = inherited_checks(contract)
    if any(text != "{message}" for text in inherited_texts(contract)):
        raise ValueError("an inherited check's text is not `{message}`: the oracle compares it with the legacy text")
    faults = catalogue()
    codes = legacy_codes()
    python_only = [fault for fault in faults if fault.readers == "python"]
    cases = gate_cases(contract)

    lean_cases = [case for case in cases if case[6]]
    lean_engine = iter(_lean_rows("ve_diagnose", "soft-norms@0", [(c[2], c[3]) for c in lean_cases]))
    lean_legacy = iter(_lean_rows("ve_soft_norms_route", None, [(c[2], c[3]) for c in lean_cases]))

    residual, deferred, sizes = Counter(), Counter(), Counter()
    first = {"python": set(), "lean": set()}
    masked = {"python": set(), "lean": set()}
    phase_pairs = set()
    mismatches, legacy_verdicts, legacy_code_deltas = [], [], []
    text_deltas = Counter()
    for tier, label, raw, norms, expected, combo, lean_reads in cases:
        sizes[tier] += 1
        python_legacy, python_outcome = _python(contract, raw, norms)
        py = python_outcome.record if isinstance(python_outcome, Fault) else None
        if isinstance(python_outcome, Deferred):
            deferred["python"] += 1
        if lean_reads:
            engine_row, legacy_row = next(lean_engine), next(lean_legacy)
            ln = engine_row.get("diagnostic") if engine_row.get("outcome") == "fault" else None
            lean_legacy_result = ((legacy_row["code"], legacy_row["error"]) if legacy_row["status"] == "error"
                                  else None)
        else:
            ln = lean_legacy_result = None
        problems = []
        languages = [("python", py, python_legacy)] + ([("lean", ln, lean_legacy_result)] if lean_reads else [])
        for language, record, legacy in languages:
            if legacy is not None and record is None:
                residual[language] += 1
            if record is not None and expected is None:
                problems += [f"{language}: {problem}" for problem in shape_problems(record)]
            if tier == "L":
                continue
            if (legacy is None) != (record is None):
                problems.append(f"{language}: legacy {'accepts' if legacy is None else 'rejects'}, engine "
                                f"{'clean' if record is None else record['check']}")
            elif record is not None and record["code"] != legacy[0]:
                problems.append(f"{language}: engine code {record['code']}, legacy {legacy[0]}")
        if lean_reads and (py is None) == (ln is None) and py is not None:
            left, right = dict(py), dict(ln)
            if left["check"] in inherited:
                for record in (left, right):
                    record.pop("text"), record.pop("args")
            if left != right:
                problems.append(f"engines differ: python {py['check']} {py['path']}, lean {ln['check']} {ln['path']}")
        elif lean_reads and (py is None) != (ln is None):
            problems.append("engines differ on fault or clean")
        if expected is not None:
            for language, record, legacy in languages:
                problems += [f"{language}: {problem}"
                             for problem in record_problems(record, expected, None if tier == "L" else legacy)]
            if (lean_reads and ln is not None and lean_legacy_result is not None
                    and expected["check"] not in inherited and ln["text"] != lean_legacy_result[1]):
                problems.append(f"lean: text {ln['text']!r}, route {lean_legacy_result[1]!r}")
            if tier == "0" and combo[0].name in codes and codes[combo[0].name] != expected["code"]:
                problems.append(f"catalogue: multi_faults code {codes[combo[0].name]}, contract {expected['code']}")
        if tier == "L":
            if (python_legacy is None) != (lean_legacy_result is None):
                legacy_verdicts.append({"case": label, "python": python_legacy, "lean": lean_legacy_result})
            elif python_legacy and lean_legacy_result and python_legacy[0] != lean_legacy_result[0]:
                legacy_code_deltas.append({"case": label, "python": python_legacy, "lean": lean_legacy_result})
        if py is not None and python_legacy is not None and py["check"] not in inherited \
                and py["text"] != python_legacy[1]:
            text_deltas[py["check"]] += 1
        if problems:
            mismatches.append({"case": label, "problems": problems})
            continue
        if tier == "0":
            for language, record, _ in languages:
                first[language].add(record["check"])
        if tier == "A":
            winner = combo[1] if label.startswith("A-mask:") else expected_first(contract, combo)
            for language, record, _ in languages:
                masked[language].update(f.check for f in combo if f is not winner)
            phases = sorted({position(contract, f)[0][1] for f in combo})
            phase_pairs.update((a, b) for a, b in zip(phases, phases[1:]) if b == a + 1)
    checks = all_checks(contract)
    table_first = checks[0]
    without_first = {language: sorted(set(checks) - first[language], key=checks.index) for language in first}
    without_masked = {language: sorted(set(checks) - masked[language], key=checks.index) for language in masked}
    adjacent = [(a, a + 1) for a in range(len(contract["phases"]) - 1)]
    python_only_checks = sorted({f.check for f in python_only})
    unmet = {
        "first": sorted(set(without_first["python"]) | (set(without_first["lean"]) - set(python_only_checks)),
                        key=checks.index),
        # 8.3: every check after the table's first instance is masked by an earlier one; the first has none.
        "masked": sorted((set(without_masked["python"]) | (set(without_masked["lean"]) - set(python_only_checks)))
                         - {table_first}, key=checks.index),
        "adjacent_phase_pairs": [list(pair) for pair in adjacent if pair not in phase_pairs],
    }
    reasons = {check: reason for check, reason in UNREACHED.items()}
    for check in python_only_checks:
        reasons[check] = ("Reached only by an explicit null, which the wire readers refuse before diagnosis: "
                          "Lean has no witness; Python has its first-fault and masking witnesses.")
    verdict_open = bool(legacy_verdicts)
    return {
        "contract": contract["contract"], "revision": contract["revision"],
        "oracle": ("fault catalogue: hand-written check, path and args per fault, text from the contract's "
                   "template, table position from the contract; inherited text from each legacy validator"),
        "tiers": {"0": sizes["0"], "A": sizes["A"], "B": sizes["B"], "replayed": sizes["R"],
                  "legacy_differences": sizes["L"]},
        "residual": {language: residual[language] for language in ("python", "lean")},
        "deferred": {language: deferred[language] for language in ("python", "lean")},
        "deferred_share": {language: deferred[language] / max(1, sum(sizes.values()))
                           for language in ("python", "lean")},
        "feasibility": feasibility(contract),
        "s3_pre": ("open: a reachable legacy verdict difference is not fixed (s3-pre.md)" if verdict_open
                   else "closed: no legacy verdict difference"),
        "legacy_verdict_differences": legacy_verdicts,
        "legacy_code_differences": legacy_code_deltas,
        "all_check_count": len(checks),
        "first_check_count": {language: len(first[language]) for language in first},
        "checks_without_first": without_first,
        "checks_without_masked": without_masked,
        "masking_not_required": {table_first: "the first instance of the table: no earlier check exists, and 8.3 "
                                              "requires a masking witness for every check after it"},
        "coverage_unmet": unmet,
        "coverage_unmet_reasons": {check: reasons[check] for check in checks if check in reasons},
        "coverage_met": not (unmet["first"] or unmet["masked"] or unmet["adjacent_phase_pairs"]),
        "text_delta_count": sum(text_deltas.values()),
        "mismatches": mismatches,
    }


def _count(value):
    return type(value) is int and value >= 0


def gate_failures(value):
    """Every requirement of spec 9 that the report `value` does not meet; empty when the gate passes. No
    summary the report states is trusted over the data it summarizes: coverage is judged from the unmet
    lists and the checks without witnesses, S3-pre from the recorded legacy verdict differences, and
    feasibility from `n1` and `n2` against the spec's own numbers, its four counts partitioning the 67
    numbered checks; each stated summary must also agree with its data."""
    failures = []
    if value["mismatches"]:
        failures.append(f"tier 0 and A: {len(value['mismatches'])} mismatches")
    # A required row over no case is vacuous: every tier, the legacy differences of S3-pre included, ran.
    for tier in ("0", "A", "B", "replayed", "legacy_differences"):
        if not _count(value["tiers"].get(tier)) or not value["tiers"][tier]:
            failures.append(f"tier {tier} ran {value['tiers'].get(tier)!r} cases")
    for language in ("python", "lean"):
        if value["residual"].get(language) != 0 or not _count(value["residual"].get(language)):
            failures.append(f"residual count {value['residual'].get(language)!r} in {language}")
    failures += _coverage_failures(value)
    failures += _feasibility_failures(value["feasibility"])
    differences = value["legacy_verdict_differences"]
    if not isinstance(differences, list) or differences:
        failures.append(f"S3-pre: legacy verdict differences {differences!r}")
    if not isinstance(value["s3_pre"], str) or not value["s3_pre"].startswith("closed"):
        failures.append(f"S3-pre {value['s3_pre']!r}")
    return failures


def _coverage_failures(value):
    """8.3's coverage row: met only when every unmet list is empty, the stated `coverage_met` agrees, and
    the unmet lists hold every check the report shows without a first or a masking witness (a Lean-only gap
    being one the reasons explain)."""
    failures = []
    unmet = value["coverage_unmet"]
    rows = ("first", "masked", "adjacent_phase_pairs")
    if not isinstance(unmet, dict) or set(unmet) != set(rows) or any(type(unmet[row]) is not list for row in rows):
        return [f"coverage unmet is malformed: {unmet!r}"]
    if any(unmet[row] for row in rows):
        failures.append(f"coverage unmet: {unmet}")
    if value["coverage_met"] is not True:
        failures.append(f"coverage_met {value['coverage_met']!r}")
    checks = all_checks(load("soft-norms@0"))
    if value["all_check_count"] != len(checks):
        failures.append(f"all_check_count {value['all_check_count']!r}, the table has {len(checks)}")
    if set(value["masking_not_required"]) - {checks[0]}:
        failures.append(f"masking not required of {sorted(value['masking_not_required'])}, only of {checks[0]}")
    reasons = value["coverage_unmet_reasons"]
    for row, without in (("first", value["checks_without_first"]), ("masked", value["checks_without_masked"])):
        if set(without) != {"python", "lean"}:
            failures.append(f"checks without {row} witness, languages {sorted(without)}")
            continue
        exempt = set(value["masking_not_required"]) if row == "masked" else set()
        for language in ("python", "lean"):
            hidden = set(without[language]) - set(unmet[row]) - exempt
            if language == "lean":
                hidden -= set(reasons)
            if hidden:
                failures.append(f"{language} has no {row} witness for {sorted(hidden)}, not in coverage_unmet")
            if row == "first" and value["first_check_count"].get(language) != len(checks) - len(without[language]):
                failures.append(f"first_check_count of {language} {value['first_check_count'].get(language)!r}, "
                                f"{len(without[language])} of {len(checks)} checks without one")
    return failures


def _feasibility_failures(feasible):
    """Spec 9's feasibility row, from `n1` and `n2` against 45 of 67: the four counts are non-negative
    integers that partition the 67 numbered checks, so no count can exceed the checks there are, and the
    report's `total`, `threshold` and `met` are what those counts give."""
    failures = []
    parts = ("n1", "n2", "coarse", "t3")
    if not all(_count(feasible.get(part)) for part in parts + ("of", "total", "threshold")) \
            or type(feasible.get("met")) is not bool:
        return [f"feasibility counts are not non-negative integers, or met is not Boolean: {feasible}"]
    total = feasible["n1"] + feasible["n2"]
    if feasible["of"] != FEASIBILITY_OF:
        failures.append(f"feasibility counts {feasible['of']} numbered checks, not {FEASIBILITY_OF}")
    if sum(feasible[part] for part in parts) != FEASIBILITY_OF:
        failures.append(f"feasibility counts {sum(feasible[part] for part in parts)} checks by tier, not the "
                        f"{FEASIBILITY_OF} numbered checks")
    if total < FEASIBILITY_THRESHOLD:
        failures.append(f"feasibility {total} of {feasible['of']}, below {FEASIBILITY_THRESHOLD}")
    met = (total >= FEASIBILITY_THRESHOLD and feasible["of"] == FEASIBILITY_OF
           and sum(feasible[part] for part in parts) == FEASIBILITY_OF)
    if (feasible.get("total"), feasible.get("threshold"), feasible.get("met")) != (total, FEASIBILITY_THRESHOLD, met):
        failures.append(f"feasibility report inconsistent: {feasible}")
    return failures


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
          f"coverage unmet: {value['coverage_unmet']}; feasibility {value['feasibility']['total']}; "
          f"S3-pre {value['s3_pre']}")
    failures = gate_failures(value)
    for failure in failures:
        print(f"gate fails: {failure}")
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
