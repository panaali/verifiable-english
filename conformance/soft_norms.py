"""Deterministic Python/Lean regeneration comparison for 1,000 soft trees."""
from __future__ import annotations

import json
from copy import deepcopy
from itertools import combinations
from pathlib import Path
import random
import subprocess
import sys

from ve.ast import formula_to_data
from ve.ast import formula_from_data
from ve.environment import Environment
from ve.errors import VEError
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.softnorms import SoftEnvironment, SoftNormDocument
from tests.test_soft_norms_lean import env, norm, should, ranks

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_soft_norms_route"
RUST_FIXTURES = ROOT / "conformance/soft_norms_rust.json"


def generated(seed):
    rng = random.Random(seed)
    ranks = ["high", "middle", "low"][:rng.randrange(4)]
    parties = ["operator", "user"][:rng.randrange(3)]
    mode = rng.choice(["strict", "holistic"])
    block = {"parties": parties, "ranks": ranks,
             "outranks": [[a, b] for a, b in zip(ranks, ranks[1:])],
             "ties": [], "outranking": {"mode": mode}}
    if mode == "holistic":
        block["outranking"]["decided_by"] = "assistant"
    extra = {p: {"arguments": ["assistant"], "description": p} for p in ("q", "u")}
    raw = env(block, extra=extra)
    rules = []
    for i in range(rng.randrange(1, 5)):
        pred = rng.choice(["x_required", "x_permitted"])
        soft_mode = rng.choice(["strict", "default"])
        parents = [r["norm"]["name"] for r in rules if r["norm"]["predicate"] == pred
                   and (soft_mode == "strict" or r["norm"].get("mode") == "default")]
        fields = {}
        if soft_mode == "default":
            fields["mode"] = "default"
            fields["exception"] = {"decided_by": "assistant", "sufficient": [],
                                   "necessary": [], "factors": []}
            if rng.randrange(4) == 0:
                fields["exception"][rng.choice(["sufficient", "necessary"])] = [
                    ["unary", "q", ["var", 0]]]
        if ranks and rng.randrange(3):
            fields["rank"] = rng.choice(ranks)
        switches = sorted(p for p in parties if rng.randrange(3) == 0)
        if switches:
            fields["alterable"] = switches
        if soft_mode == "strict" and not switches and rng.randrange(5) == 0:
            fields["hard"] = True
        guard = (["unary", "q", ["var", 0]] if rng.randrange(4) == 0 else ["top"])
        unless = (["unary", "u", ["var", 0]] if rng.randrange(4) == 0 else None)
        rules.append(norm(f"n{i}", pred, rng.choice([True, False]), guard=guard,
                          unless=[unless] if unless else [],
                          over=[rng.choice(parents)] if parents and rng.randrange(3) == 0 else [],
                          **fields))
    return raw, rules


def rust_sources():
    """Identity-bound soft sources and decision assignments for Rust replay."""
    return [
        ("default-live", env(), [should("a", "x_required", True)], []),
        ("default-excepted", env(), [should("a", "x_required", True)], ["soft__excepted__a"]),
        ("hard", env(), [norm("h", "x_required", True, hard=True)], []),
        ("switch-live", env({"parties": ["user"], "outranking": {"mode": "strict"}}),
         [norm("h", "x_required", True, alterable=["user"])], []),
        ("switch-off", env({"parties": ["user"], "outranking": {"mode": "strict"}}),
         [norm("h", "x_required", True, alterable=["user"])], ["soft__off__h__user"]),
        ("three-switches", env({"parties": ["a", "b", "c"], "outranking": {"mode": "strict"}}),
         [norm("h", "x_required", True, alterable=["a", "b", "c"])], ["soft__off__h__c"]),
        ("holistic-high", env(ranks(["high", "low"], "holistic")),
         [should("h", "x_required", True, rank="high"),
          should("l", "x_required", False, rank="low")], []),
        ("holistic-low", env(ranks(["high", "low"], "holistic")),
         [should("h", "x_required", True, rank="high"),
          should("l", "x_required", False, rank="low")],
         ["soft__outweighs__low__high__x_permitted"]),
        ("open-pair", env(), [should("a", "x_required", True),
                               should("b", "x_permitted", False)], []),
    ]


def rejected_sources():
    """Wire inputs both regenerators must reject with identical diagnostics."""
    return [
        (env({"ranks": ["Bad!"], "outranking": {"mode": "strict"}}), []),
        (env({"ranks": ["a", "a"], "outranking": {"mode": "strict"}}), []),
        (env({"parties": ["a", "a"], "outranking": {"mode": "strict"}}), []),
        (env({"ranks": ["x", "y", "z"], "outranks": [["x", "y"], ["y", "z"], ["z", "y"]],
              "outranking": {"mode": "strict"}}), []),
        (env(), [norm("a", "x_required", True, alterable=["user"])]),
        (env(), [norm("a", "x_required", True, mode="default", exception={
            "decided_by": "", "sufficient": [], "necessary": [], "factors": []})]),
        (env({"outranking": {"mode": "strict", "decided_by": "assistant"}}), []),
        (env({"ranks": ["a", "b"], "ties": [["a", "b"], ["a", "b"]],
              "outranking": {"mode": "strict"}}), []),
        (env({"ranks": ["a", "b"], "outranks": [["a", "b"], ["a", "b"]],
              "outranking": {"mode": "strict"}}), []),
        (env(), [norm("a", "x_required", True, mode="default",
                      exception={"decided_by": "assistant"})]),
        (env({"parties": ["assistant", "user"], "outranking": {"mode": "strict"}}),
         [norm("a", "x_required", True, alterable=["user", "assistant"])]),
        # Diagnostic parity reproducers from the soft route review.
        (env(), [norm("a", "x_required", True, mode="default")]),
        (env({"ranks": ["a"], "ties": [["a"]],
              "outranking": {"mode": "strict"}}), []),
        (env(), [norm("a", "x_required", True, mode="default", hard=True)]),
        (env(), [norm("a", "x_required", True, mode="default", alterable=["z"])]),
        (env(), [norm("a", "x_required", True, mode="default", rank="z")]),
        (env(), [norm("a", "x_required", True, alterable=False)]),
    ]


def generated_invalid_soft_blocks():
    """Single-field mutations of a valid block, including every collection shape."""
    baseline = env({"parties": ["p"], "ranks": ["a", "b"],
                    "outranking": {"mode": "strict"}})
    mutations = {
        "parties": [False, {}, "p", [False], ["Bad!"], ["p", "p"]],
        "ranks": [False, {}, "a", [42], ["Bad!"], ["a", "a"]],
        "outranks": [False, {}, "a", [[]], [["a"]], [["a", "b", "a"]],
                     [[1, "b"]], [["a", "a"]], [["a", "b"], ["a", "b"]],
                     [["a", "unknown"]]],
        "ties": [False, {}, "a", [[]], [["a"]], [["a", "b", "a"]],
                 [[1, "b"]], [["a", "a"]], [["a", "b"], ["a", "b"]],
                 [["a", "b"], ["b", "a"]], [["a", "unknown"]]],
        "outranking": [False, {}, "strict", {"mode": "other"},
                       {"mode": "strict", "extra": 1},
                       {"mode": "strict", "decided_by": False},
                       {"mode": "holistic"},
                       {"mode": "holistic", "decided_by": False},
                       {"mode": "holistic", "decided_by": ""}],
        "exception_decider": [False, 3, ""],
        "unknown_field": [True],
    }
    for field, values in mutations.items():
        for value in values:
            raw = deepcopy(baseline)
            raw["vocabulary"]["soft"][field] = value
            yield raw, []
    for value in (False, True, 0, "strict", [], {}):
        raw = deepcopy(baseline)
        raw["vocabulary"]["soft"] = value
        yield raw, []
    for name in ("soft__reserved",):
        raw = deepcopy(baseline)
        raw["vocabulary"]["predicates"][name] = {
            "arguments": ["assistant"], "description": name}
        yield raw, []
    # Diagnostic strings supplied as names must not change the rejection class.
    for name in ("needs an exception", "invalid ties pair", "UnknownRank: x"):
        raw = deepcopy(baseline)
        raw["vocabulary"]["soft"]["ranks"] = [name]
        yield raw, []
    for value in (False, True, 0, 1, [], {}, ["p"], {"party": "p"}):
        raw = deepcopy(baseline)
        raw["vocabulary"]["predicates"]["q"] = {
            "arguments": ["assistant"], "description": "q", "instruction_of": value}
        yield raw, []


def combined_invalid_soft_blocks():
    """Independent block faults must have the same diagnostic precedence."""
    baseline = env({"parties": ["p"], "ranks": ["a", "b"],
                    "outranking": {"mode": "strict"}})
    original = baseline["vocabulary"]["soft"]
    mutations = []
    for raw, _ in generated_invalid_soft_blocks():
        block = raw["vocabulary"].get("soft")
        if type(block) is not dict:
            continue
        changed = {k: v for k, v in block.items() if k not in original or v != original[k]}
        if len(changed) == 1:
            mutations.append(changed)
    for left, right in combinations(mutations, 2):
        if left.keys() & right.keys():
            continue
        raw = deepcopy(baseline)
        raw["vocabulary"]["soft"].update(left)
        raw["vocabulary"]["soft"].update(right)
        yield raw, []


def generated_invalid_soft_rules():
    """Pairs of independent rule faults check diagnostic precedence."""
    raw = env()
    valid = norm("a", "x_required", True, mode="default", exception={
        "decided_by": "assistant", "sufficient": [], "necessary": [], "factors": []})
    faults = [
        {"rank": "z"}, {"alterable": ["z"]}, {"alterable": False},
        {"hard": True}, {"exception": False},
        {"exception": {"decided_by": "", "sufficient": [], "necessary": [], "factors": []}},
        {"exception": {"decided_by": "assistant", "sufficient": [],
                       "necessary": [], "factors": False}},
        {"mode": "other"}, {"hard": "yes"},
    ]
    for left, right in combinations(faults, 2):
        if left.keys() & right.keys():
            continue
        yield raw, [{"norm": {**valid["norm"], **left, **right}}]


def generated_invalid_exceptions():
    """Exception fields are checked in wire order, including combined faults."""
    valid = {"decided_by": "assistant", "sufficient": [],
             "necessary": [], "factors": []}
    faults = [
        {"decided_by": False}, {"decided_by": ""},
        {"sufficient": False}, {"sufficient": [False]},
        {"necessary": False}, {"necessary": [False]},
        {"factors": False}, {"factors": [False]},
    ]
    for left, right in combinations(faults, 2):
        if left.keys() & right.keys():
            continue
        exception = {**valid, **left, **right}
        yield env(), [norm("a", "x_required", True, mode="default", exception=exception)]


def compare_rejected():
    cases = (rejected_sources() + list(generated_invalid_soft_blocks()) +
             list(generated_invalid_soft_rules()) +
             list(combined_invalid_soft_blocks()) +
             list(generated_invalid_exceptions()))
    expected = []
    for raw, rules in cases:
        try:
            SoftNormDocument(SoftEnvironment(raw), rules)
        except VEError as exc:
            expected.append((str(exc), exc.code))
        else:
            raise AssertionError("Python unexpectedly accepted a rejected soft source")
    wire = [{"id": str(i), "kind": "soft-elaborate", "environment": raw, "norms": rules}
            for i, (raw, rules) in enumerate(cases)]
    run = subprocess.run([str(LEAN), "-"], input=json.dumps(wire), text=True,
                         capture_output=True, timeout=120, check=False)
    rows = json.loads(run.stdout)
    if len(rows) != len(cases):
        raise AssertionError("Lean returned the wrong rejected row count")
    for i, (row, (error, code)) in enumerate(zip(rows, expected)):
        if row.get("status") != "error" or row.get("code") != code:
            raise AssertionError((i, error, code, row))
        if i < len(rejected_sources()) and row.get("error") != error:
            raise AssertionError((i, error, row))
    return len(cases)


def rust_fixture_rows():
    result = []
    for name, raw, rules, present in rust_sources():
        soft = SoftNormDocument(SoftEnvironment(raw), rules)
        case = {"id": name, "kind": "soft-elaborate", "environment": raw, "norms": rules}
        run = subprocess.run([str(LEAN), "-"], input=json.dumps([case]), text=True,
                             capture_output=True, timeout=120, check=False)
        row = json.loads(run.stdout)[0]
        if row.get("status") != "ok":
            raise AssertionError((name, row))
        py_layers = [(label, formula_to_data(soft.extended_env, formula, _generated=True))
                     for label, formula in soft.elaborated.premises()]
        if py_layers != [(p["label"], p["ast"]) for p in row["premises"]]:
            raise AssertionError(f"Python/Lean layers differ: {name}")
        stripped = json.loads(json.dumps(row["environment_prime"]))
        stripped["profiles"] = [p for p in stripped["profiles"] if p != "soft-norms@0"]
        stripped["vocabulary"].pop("soft", None)
        for predicate in stripped["vocabulary"]["predicates"].values():
            predicate.pop("instruction_of", None)
        environment = Environment(stripped)
        formulas = [p["ast"] for p in row["premises"]] + [
            p["ast"] for p in row["background"] if p.get("generator") == "soft"]
        target_start = len(formulas)
        for target in row["conflict_targets"]:
            existential = target["ast"]
            for sort in reversed(target["sorts"]):
                existential = ["exists", sort, existential]
            formulas.append(existential)
        for required, permitted in ((False, False), (False, True), (True, True)):
            relations = {p: [] for p in environment.predicates}
            relations["x_required"] = [["a"]] if required else []
            relations["x_permitted"] = [["a"]] if permitted else []
            for decision in present:
                relations[decision] = [["a"]]
            model_data = {"complete": True, "domains": {"assistant": ["a"], "user": []},
                          "constants": {}, "relations": relations}
            model = FiniteModel.from_dict(environment, model_data)
            expected = [evaluate(environment, formula_from_data(environment, formula),
                                 model, trace=False).value for formula in formulas]
            result.append({"id": name + f"-{int(required)}{int(permitted)}",
                           "untrusted": True,
                           "source": {"environment": raw, "norms": rules},
                           "environment": stripped, "formulas": formulas,
                           "model": model_data, "expected": expected,
                           "target_start": target_start,
                           "conflict": any(expected[target_start:])})
    return result


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--write-rust-fixtures":
        rows = rust_fixture_rows()
        RUST_FIXTURES.write_text(json.dumps(rows, sort_keys=True, ensure_ascii=False,
                                            separators=(",", ":")) + "\n")
        print(json.dumps({"rust_cases": len(rows), "path": str(RUST_FIXTURES)}))
        return
    compared = 0
    seed = 0
    while compared < 1000:
        batch = []
        while len(batch) < min(25, 1000 - compared):
            raw, rules = generated(seed)
            seed += 1
            try:
                soft = SoftNormDocument(SoftEnvironment(raw), rules)
            except Exception:
                continue  # generate another accepted tree
            batch.append((raw, rules, soft))
        cases = [{"id": str(compared + i), "kind": "soft-elaborate",
                  "environment": raw, "norms": rules}
                 for i, (raw, rules, _) in enumerate(batch)]
        run = subprocess.run([str(LEAN), "-"], input=json.dumps(cases), text=True,
                             capture_output=True, timeout=120, check=False)
        rows = json.loads(run.stdout)
        if len(rows) != len(batch):
            raise AssertionError("Lean returned the wrong row count")
        for i, ((_, _, soft), row) in enumerate(zip(batch, rows)):
            if row.get("status") != "ok":
                raise AssertionError((compared + i, row))
            py_layers = [(l, formula_to_data(soft.extended_env, f, _generated=True))
                         for l, f in soft.elaborated.premises()]
            lean_layers = [(p["label"], p["ast"]) for p in row["premises"]]
            py_soft = [(l, formula_to_data(soft.extended_env, f, _generated=True))
                       for l, f in soft.extended_env.soft_premises]
            lean_soft = [(p["label"], p["ast"]) for p in row["background"]
                         if p["generator"] == "soft"]
            if (soft.extended_env.to_dict() != row["environment_prime"] or
                    py_layers != lean_layers or py_soft != lean_soft or
                    list(soft.warnings) != row["warnings"] or
                    set(soft.extended_env.decision_names) !=
                    {d["name"] for d in row["decisions"]}):
                raise AssertionError(f"regeneration mismatch at seed {seed - len(batch) + i}")
        compared += len(batch)
    print(json.dumps({"accepted_trees": compared, "seeds_examined": seed,
                      "environment_matches": compared, "layer_matches": compared,
                      "soft_background_matches": compared, "decision_matches": compared,
                      "rejected_inputs": compare_rejected()}))


if __name__ == "__main__":
    main()
