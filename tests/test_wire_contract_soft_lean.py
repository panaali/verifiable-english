"""The pilot contract soft-norms@0 in the Lean engine (`ve_diagnose soft-norms@0`), docs/spec/wire-contract.md
section 6 and 8.3, against the hand-derived records and against the legacy Lean route.

The legacy route `ve_soft_norms_route` decides accept or reject and reports a code; the engine only names the
first failing check. On every case here the engine reports a fault exactly when the route rejects, with the
route's code, and, for a check that is not inherited, the route's text (spec 6: Lean's texts). The cases are
the fixtures P1 to P17, every single fault of `conformance.soft_norms.multi_faults()` (tier 0) and the pairs
and triples of `multi_fault_cases()` (tier A, the oracle being the fault of least table position).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests import lean_routes
from conformance.soft_norms import multi_fault_base, multi_fault_cases, multi_faults
from tests.test_soft_norms_lean import env, norm
from ve.wire import canonical_json

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "lean/.lake/build/bin"
S = "/environment/vocabulary/soft"
# Checks and classifier members whose text is the inherited decoder's (spec 2.5, rule 5).
INHERITED = {"2.3", "4.2a", "4.13b", "4.13d", "5.7", "5.8a", "6.10b"}


@pytest.fixture(scope="module")
def built():
    if not (BIN / "ve_service").exists():
        pytest.skip("the Lean service has not been built")
    return BIN


def call(route, args, cases):
    """The rows of the service mode that replaced the one-shot `route` (`ve_diagnose` with its unit in
    `args`, or `ve_soft_norms_route`)."""
    rows = lean_routes.diagnose(args[0], cases) if route == "ve_diagnose" else lean_routes.rows(route, cases)
    assert len(rows) == len(cases)
    return rows


def cases(sources):
    return [{"id": f"c{n}", "kind": "soft-elaborate", "environment": raw, "norms": rules}
            for n, (raw, rules) in enumerate(sources)]


def both(bin_dir, sources, size=100):
    """(engine row, legacy row) per source, in batches within the runners' 16 MiB package limit."""
    rows = []
    for start in range(0, len(sources), size):
        batch = cases(sources[start:start + size])
        engine = call("ve_diagnose", ["soft-norms@0"], batch)
        legacy = call("ve_soft_norms_route", [], batch)
        assert all(row["status"] == "ok" for row in engine)
        rows += zip(engine, legacy)
    return rows


def with_faults(*names):
    raw, rules = multi_fault_base()
    table = {f[0]: f for f in multi_faults()}
    for name in names:
        table[name][4](raw, rules)
    return raw, rules


def record(check, phase, code, cls, path, text, args=None):
    return {"contract": "soft-norms@0", "revision": 4, "check": check, "phase": phase, "code": code,
            "class": cls, "path": path, "text": text, "args": args or {}}


def agree(engine, legacy):
    """The engine names a fault exactly when the route rejects, with the route's code and (unless inherited)
    its text."""
    if legacy["status"] != "error":
        assert engine["outcome"] == "clean", (engine, legacy)
        return
    assert engine["outcome"] == "fault", (engine, legacy)
    diagnostic = engine["diagnostic"]
    assert diagnostic["code"] == legacy["code"], (diagnostic, legacy)
    if diagnostic["check"] not in INHERITED:
        assert diagnostic["text"] == legacy["error"], (diagnostic, legacy)


FIXTURES = {
    "P2": (("party-name",), record("2.7a", "declarations", "SOFT_INVALID_NAME", "InvalidInput", S + "/parties/1",
                                   "InvalidInput: invalid soft name Q!", {"value": "Q!"})),
    "P3": (("party-repeat",), record("2.7b", "declarations", "SOFT_DUPLICATE_DECLARATION", "DuplicateDeclaration",
                                     S + "/parties/2", "DuplicateDeclaration: party p", {"value": "p"})),
    "P4": (("language",), record("1.2", "envelope", "SOFT_UNSUPPORTED_PROFILE", "UnsupportedProfile",
                                 "/environment/language", "UnsupportedProfile: Unsupported language")),
    "P5": (("parties-shape", "r3-rank-type"), record("2.5", "declarations", "SOFT_INVALID_ARRAY", "InvalidInput",
                                                     S + "/parties", "InvalidInput: parties must be an array")),
    "P6": (("r0-hard-type", "r1-mode"), record("4.6", "rule-fields", "SOFT_INVALID_RULE_FIELDS", "InvalidInput",
                                               "/norms/0/norm/hard", "InvalidInput: hard of rule a0 must be Boolean",
                                               {"name": "a0"})),
    "P8": (("outranks-pair",), record("2.16b", "declarations", "SOFT_INVALID_OUTRANKS_PAIR", "InvalidInput",
                                      S + "/outranks/1/1", "InvalidInput: invalid outranks pair")),
    "P9": (("ties-pair",), record("2.17d", "declarations", "SOFT_INVALID_TIES_PAIR", "InvalidInput",
                                  S + "/ties/1", "InvalidInput: invalid ties pair")),
    "P10": (("holistic-decider",), record("2.12", "declarations", "SOFT_MISSING_DECIDER", "InvalidInput",
                                          S + "/outranking", "MissingExceptionDecider: outranking")),
    "P11": (("inherited-decider",), record("4.11a", "rule-fields", "SOFT_MISSING_DECIDER", "InvalidInput",
                                           "/norms/2/norm/exception", "MissingExceptionDecider: rule c2",
                                           {"name": "c2"})),
    "P12": (("r1-strict-exception",), record("4.8", "rule-fields", "SOFT_STRICT_EXCEPTION", "InvalidInput",
                                             "/norms/1/norm/exception",
                                             "InvalidInput: rule b1 is strict and declares an exception",
                                             {"name": "b1"})),
    "P13": (("duplicate-rule",), record("5.3", "references", "SOFT_DUPLICATE_DECLARATION", "DuplicateDeclaration",
                                        "/norms/3/norm/name", "DuplicateDeclaration: rule b1", {"value": "b1"})),
    "P14": (("rank-cycle",), record("6.1", "semantic", "SOFT_DEPENDENCY_CYCLE", "InvalidInput", S + "/outranks",
                                    "DependencyCycle: a, b", {"detail": "a, b"})),
    "P15": (("soft-over-hard",), record("6.8", "semantic", "SOFT_OVER_HARD", "InvalidInput", "",
                                        "SoftOverHard: rule d3 over b1", {"detail": "rule d3 over b1"})),
    "P16": (("precedence-cycle", "soft-over-hard"), record("6.5b", "semantic", "SOFT_DEPENDENCY_CYCLE",
                                                           "InvalidInput", "", "DependencyCycle: a0, c2",
                                                           {"detail": "a0, c2"})),
}


def p7_source():
    """On `env()`: rule `a` default with a factor of 201 bytes, then rule `b` with rank `z`."""
    exception = {"decided_by": "assistant", "sufficient": [], "necessary": [], "factors": ["x" * 201]}
    return env(), [norm("a", "x_required", True, mode="default", exception=exception),
                   norm("b", "x_permitted", False, rank="z")]


def fixture_sources():
    """P1's two examples, P7, P17, then the named fixtures in the order of `sorted(FIXTURES)`."""
    return [multi_fault_base(), (env(), []), p7_source(), with_faults("malformed-predicate"),
            *[with_faults(*FIXTURES[name][0]) for name in sorted(FIXTURES)]]


def test_fixtures_p1_to_p17(built):
    names = sorted(FIXTURES)
    rows = both(built, fixture_sources())
    base, empty, p7, p17, *rest = rows
    for engine, legacy in (base, empty):  # P1: both examples are accepted, and the engine is clean
        assert legacy["status"] == "ok" and engine["outcome"] == "clean"
    assert canonical_json(p7[0]["diagnostic"]) == canonical_json(record(
        "4.14b", "rule-fields", "SOFT_INVALID_FACTORS", "InvalidInput", "/norms/0/norm/exception/factors/0",
        "InvalidInput: invalid factors of rule a", {"name": "a"}))
    agree(*p7)
    diagnostic = p17[0]["diagnostic"]
    assert (diagnostic["check"], diagnostic["path"], diagnostic["code"]) == ("2.3", "/environment",
                                                                             "SOFT_INVALID_INPUT")
    assert diagnostic["args"] == {"message": diagnostic["text"]}
    agree(*p17)
    for name, (engine, legacy) in zip(names, rest):
        assert canonical_json(engine["diagnostic"]) == canonical_json(FIXTURES[name][1]), name
        agree(engine, legacy)


def test_tier0_every_single_fault(built):
    """Each fault alone: the route rejects, and the engine names a check with the fault's code."""
    faults = multi_faults()
    rows = both(built, [with_faults(f[0]) for f in faults])
    for fault, (engine, legacy) in zip(faults, rows):
        assert legacy["status"] == "error", fault[0]
        assert legacy["code"] == fault[3], fault[0]
        agree(engine, legacy)


def test_tier_a_pairs_and_triples(built):
    """Two and three faults: the engine's code is the code of the fault of least table position, as the route's."""
    combos = list(multi_fault_cases())
    rows = both(built, [(raw, rules) for _, raw, rules, _ in combos])
    for (name, _, _, expected), (engine, legacy) in zip(combos, rows):
        assert legacy["code"] == expected, name
        agree(engine, legacy)


def test_adapter_rejects_other_case_kinds(built):
    rows = call("ve_diagnose", ["soft-norms@0"], [{"id": "x", "kind": "evaluation"}])
    assert rows == [{"id": "x", "status": "error",
                     "error": "UnsupportedProfile: case kind evaluation has no wire contract input"}]


def s3_pre_sources():
    """With `norm-defaults@0` among the profiles: the base, `env()`, `env()` without any `regulated`, and
    `env()` with the `unspecified` default."""
    def with_profile(raw):
        raw["profiles"] = sorted(raw["profiles"] + ["norm-defaults@0"])
        return raw

    plain = with_profile(env())
    bare = with_profile(env())
    for entry in bare["vocabulary"]["predicates"].values():
        entry.pop("regulated", None)
    unspecified = with_profile(env())
    unspecified["vocabulary"]["predicates"]["x_required"]["regulated"]["default"] = "unspecified"
    base_raw, base_rules = multi_fault_base()
    return [(with_profile(base_raw), base_rules), (plain, []), (bare, []), (unspecified, [])]


def test_s3_pre_norm_defaults_profile(built):
    """S4-pre: both legacy validators reject every source with the same code."""
    from ve.errors import VEError
    from ve.softnorms import load_soft_document

    sources = s3_pre_sources()
    expected = [("SOFT_UNSUPPORTED_PROFILE", "3.2")] * 3 + [("SOFT_INVALID_INPUT", "2.3")]
    rows = both(built, sources)
    for (raw, rules), (engine, legacy), (lean_code, check) in zip(sources, rows, expected):
        with pytest.raises(VEError) as caught:
            load_soft_document(json.loads(json.dumps(raw)), json.loads(json.dumps(rules)))
        assert caught.value.code == lean_code
        # The source lists `norm-defaults@0`, so no text may name that profile as missing (Fable B2).
        assert "checked through fill" in str(caught.value)
        assert "requires norm-defaults@0" not in str(caught.value)
        if check == "2.3":
            assert str(caught.value) == ("UnsupportedProfile: norm-defaults@0 documents are checked through "
                                         "fill (ve.norm_defaults)")
        assert legacy["status"] == "error" and legacy["code"] == lean_code
        assert engine["diagnostic"]["check"] == check
        agree(engine, legacy)
        python = python_record(raw, rules)
        if check in INHERITED:
            python.pop("text"), python.pop("args"), engine["diagnostic"].pop("text"), engine["diagnostic"].pop("args")
        assert canonical_json(python) == canonical_json(engine["diagnostic"])


# What Python's legacy validator does with each profile absent from the Lean soft route
# (s3-pre.md and s4-pre.md). The rights and speech-act differences are now closed.
PYTHON_ONLY_LEGACY = {
    "alternatives@0": ("SOFT_UNSUPPORTED_PROFILE", "UnsupportedProfile: alternatives@0 with soft-norms@0"),
    "norm-defaults@0": ("SOFT_UNSUPPORTED_PROFILE",
                        "UnsupportedProfile: norm-defaults@0 documents are checked through fill (ve.norm_defaults)"),
    "reports@0": ("SOFT_UNSUPPORTED_PROFILE", "UnsupportedProfile: reports@0 with norms@0 layers"),
    # S3-pre: the rights route strips `rights@0` before the soft table, as Lean's does, so the soft route
    # alone refuses it at 3.2 with the Lean route's text (it accepted before the fix).
    "rights@0": ("SOFT_UNSUPPORTED_PROFILE", "UnsupportedProfile: Unsupported profile rights@0"),
    "risk@0": ("SOFT_UNSUPPORTED_PROFILE", "UnsupportedProfile: risk@0 requires alternatives@0"),
    "speech-acts@0": ("SOFT_UNSUPPORTED_PROFILE", "UnsupportedProfile: Unsupported profile speech-acts@0"),
}


def python_record(raw, rules):
    from ve.softnorms_contract import REGISTRY
    from ve.wire_contract.engine import Fault, load, run
    outcome = run(load("soft-norms@0"), {"environment": raw, "norms": rules}, registry=REGISTRY)
    return outcome.record if isinstance(outcome, Fault) else "clean"


def test_profiles_outside_the_lean_route_three_way(built):
    """Wire review (Fable A1): both engines report check 3.2 on every profile outside the Lean route's
    registry; the legacy outcomes are pinned. No profile is a legacy verdict difference: both legacy
    validators reject every one (S3-pre; Python accepted `rights@0` before the fix)."""
    from ve.errors import VEError
    from ve.softnorms import load_soft_document
    names = sorted(PYTHON_ONLY_LEGACY)
    sources = []
    for name in names:
        for raw, rules in ((env(), []), multi_fault_base()):
            raw["profiles"] = sorted(raw["profiles"] + [name])
            sources.append((name, raw, rules))
    rows = both(built, [(raw, rules) for _, raw, rules in sources])
    for (name, raw, rules), (engine, legacy) in zip(sources, rows):
        assert legacy["status"] == "error" and legacy["code"] == "SOFT_UNSUPPORTED_PROFILE", name
        assert engine["diagnostic"]["check"] == "3.2", name
        agree(engine, legacy)
        assert canonical_json(python_record(raw, rules)) == canonical_json(engine["diagnostic"]), name
        try:
            load_soft_document(json.loads(json.dumps(raw)), json.loads(json.dumps(rules)))
            python_legacy = None
        except VEError as error:
            python_legacy = (error.code, str(error))
        expected = ("SOFT_UNSUPPORTED_PROFILE", "UnsupportedProfile: Unsupported profile soft-norms@0") \
            if name == "reports@0" else PYTHON_ONLY_LEGACY[name]
        assert python_legacy == expected, name
        assert python_legacy is not None, name


def test_decision_names_prefix_order_three_way(built):
    """Wire review (Fable B1): a strict rule's long `off` name before a default rule's long `excepted` name;
    both legacy validators and both engines name the `excepted` one."""
    raw, rules = multi_fault_base()
    rules[1]["norm"]["name"] = "b" * 52
    rules[3]["norm"]["name"] = "d" * 52
    [(engine, legacy)] = both(built, [(raw, rules)])
    name = "soft__excepted__" + "d" * 52
    expected = record("6.4a", "semantic", "SOFT_RESOURCE_LIMIT", "ResourceLimit", "",
                      f"ResourceLimit: decision predicate {name}", {"name": name})
    assert legacy["error"] == expected["text"]
    assert canonical_json(engine["diagnostic"]) == canonical_json(expected)
    assert canonical_json(python_record(raw, rules)) == canonical_json(expected)
