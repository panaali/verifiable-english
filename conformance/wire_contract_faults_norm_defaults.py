"""The fault catalogue and the gate corpus of `norm-defaults@0` (wire-contract-s5.md 2.4, 8.2, 8.4).

Every fault is applied to the base U of 8 (the contract's first example). The faults of `norms@0` are
applied to U too, each expecting its check under the include that runs it (`w1-environment/1.1`,
`w1-shape/3.4`, `w1/4.2`); the fault of `w1/2.1` is not, because its source is outside this unit's domain
(gap G2 of 8.4). Then the fixtures D4 and D6 to D11 of 8.2, one fault for each own check and for `w1/4.3`.
"""

from copy import deepcopy
import json
from pathlib import Path
import random
import sys

from conformance import wire_contract_faults_norms as norms_faults
from conformance.wire_contract_faults import Fault, _replacing, _set_at
from conformance.wire_contract_faults_norms import (ATOM, BUDGET, balanced, call_problems, class_exempt,
                                                   own_text)
from ve.errors import VEError
from ve.norm_defaults_contract import REGISTRY, legacy_validation
from ve.norms_contract import in_domain

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "ve/wire_contract/examples/norm-defaults@0"
UNIT = "norm-defaults@0"
LEAN_ROUTE = "ve_norm_defaults_route"
CASE_KIND = "norm-defaults-elaborate"
FEASIBILITY_OF = 6
RECORDED_TESTS = ("tests/test_norm_defaults_contract*", "tests/test_norm_defaults.py",
                  "tests/test_norm_defaults_three_way.py", "tests/test_norm_defaults_differential.py")
# 8.4's allowed coverage gaps for this unit: G1 as the pilot's; G2 to `w1/2.1`, which the environment
# decoder masks under this unit's profile; G3 applies to no check of this unit.
GAP_APPLIES = {"G1": lambda faults: {f.check for f in faults} - {f.check for f in faults if f.readers != "python"},
               "G2": lambda faults: {"w1/2.1"}, "G3": lambda faults: set()}
UNREACHED = {}
WHOLE_SOURCE_PARTNER = "environment-defined"
N = ("norms",)
P = ("environment", "vocabulary", "predicates")
INCLUDES = {"environment": "w1-environment", "rule-shape": "w1-shape"}
# The `norms@0` faults that leave this unit's domain (their variants under U are below), and the label of
# the faults that read `x_permitted`'s name, which D8 changes.
OUTSIDE = {"profile-missing", "guard-string-binder"}
PERMITTED_NAME = frozenset({"x-permitted-name"})
LONG = "x_permitted_" + "p" * 45


def base():
    """The base U (8): the contract's first example."""
    value = json.loads((EXAMPLES / "base.json").read_text())
    return value["environment"], value["norms"]


def included(check):
    """A `norms@0` check under the include that runs it in this unit."""
    phase = {"1": "environment", "3": "rule-shape"}.get(check.split(".")[0], "norms")
    return INCLUDES.get(phase, "w1") + "/" + check


def _string_binder(root):
    root["environment"]["profiles"] = ["data@0", "norm-defaults@0", "norms@0", "relational-fol@0"]
    root["norms"][0]["norm"]["guard"] = ["forall", "$string", ["top"]]


def _rename_permitted(root):
    """D8: `x_permitted` renamed to a 57-byte name, in its declaration, in `x_required`'s `permission` and
    in unit 1, U's rule on it (the faults that change unit 1's predicate or read the name are not combined
    with this one: its footprint and the label `PERMITTED_NAME`)."""
    predicates = root["environment"]["vocabulary"]["predicates"]
    predicates[LONG] = predicates.pop("x_permitted")
    predicates["x_required"]["regulated"]["permission"] = LONG
    root["norms"][1]["norm"]["predicate"] = LONG


def _chain(predicate, count):
    return [{"norm": {"name": f"r{i}", "predicate": predicate, "sign": True, "guard": ["top"], "unless": [],
                      "over": [f"r{i - 1}"] if i else []}} for i in range(count)]


def _own():
    """(name, check, path, apply, args, labels, reads) of D4 and D6 to D11 (8.2)."""
    def vocabulary(root):
        root["environment"]["vocabulary"]["predicates"].update(
            {f"b{i}": {"arguments": ["assistant"], "description": "b"} for i in range(253)})
    def rules(root):
        root["norms"].extend({"norm": {"name": f"r{i}", "predicate": "x_required", "sign": True,
                                       "guard": ["top"], "unless": [], "over": []}} for i in range(3, 256))
    return [
        ("reserved-name", "w1/4.3", "/norms/1/norm/name", _set_at(N + (1, "norm", "name"), "unsaid--x"),
         {"value": "unsaid--x"}, (), ()),
        ("string-binder", "w1/4.7e", "/norms/0", _replacing(_string_binder, ("environment", "profiles"),
                                                             N + (0, "norm", "guard")), None, (), ()),
        ("filled-vocabulary", "5.1", "", vocabulary, {}, (), ()),
        ("filled-rules", "5.2", "", rules, {}, (), ()),
        ("unspecified-name", "5.3", "", _replacing(_rename_permitted, P + ("x_permitted",), P + (LONG,),
                                                    P + ("x_required", "regulated", "permission"),
                                                    N + (1, "norm", "predicate")),
         {}, PERMITTED_NAME, ()),
        ("filled-nodes", "6.1", "", _set_at(N + (0, "norm", "guard"), balanced([ATOM] * 3332)), {}, BUDGET,
         (N,)),
        ("filled-depth", "6.2", "", _replacing(lambda root: root.update(norms=_chain("x_permitted", 16)), N),
         {}, frozenset({"precedence"}) | PERMITTED_NAME, ()),
        ("fill-premise", "6.3", "", _set_at(N + (0, "norm", "guard"), balanced([ATOM] * 3320)),
         {"label": "unsaid:pair:x_required,x_permitted"}, BUDGET | PERMITTED_NAME, (N,)),
    ]


def catalogue():
    faults = []
    for name, check, path, apply, args, labels, reads in norms_faults._faults():
        if name in OUTSIDE:
            continue
        if name in ("layer-cycle", "over-predicate"):
            labels = frozenset(labels) | PERMITTED_NAME
        faults.append(Fault(name, included(check), path, apply, frozenset({name}) | frozenset(labels),
                            reads=tuple(reads), base=base, args=args))
    for name, check, path, apply, args, labels, reads in _own():
        faults.append(Fault(name, check, path, apply, frozenset({name}) | frozenset(labels), reads=tuple(reads),
                            base=base, args=args))
    return faults


# ## The gate's other corpora and its unit rules

def handler_reaching(raw, norms):
    """A rejected source on which the call of D(N) reaches the statement of 2.8 (2.11): its environment
    decodes and lists `norm-defaults@0`, and its norms are objects with a member `norm`."""
    from ve.environment import Environment
    try:
        env = Environment(deepcopy(raw))
    except VEError:
        return False
    return ("norm-defaults@0" in env.profiles and type(norms) is list
            and all(type(unit) is dict and "norm" in unit for unit in norms))


def _mutations(rng, raw, norms):
    raw, norms = norms_faults._mutations(rng, raw, norms)
    if rng.randrange(4) == 0:
        predicates = raw["vocabulary"]["predicates"]
        name = rng.choice(["x_required", "x_permitted"])
        if name in predicates and "regulated" in predicates[name]:
            predicates[name]["regulated"]["default"] = rng.choice(["deny", "allow", "unspecified"])
    return raw, norms


def generated_sources(count=400, seed=7):
    """Seeded sources: U with one to three random changes each."""
    rng = random.Random(seed)
    for index in range(count):
        raw, norms = base()
        for _ in range(1 + index % 3):
            raw, norms = _mutations(rng, raw, norms)
        if in_domain(raw, norms, defaults=True):
            yield f"generated:{index}", raw, norms


def conformance_sources():
    """The sources the unit's conformance scripts build (8.7), those in its domain: `sources()` of
    `conformance/norm_defaults.py` on the norms route, the fixtures of `conformance/norm_defaults_three_way.py`
    and the generated trees of `conformance/norm_defaults_differential.py`."""
    if str(ROOT / "tests") not in sys.path:
        sys.path.append(str(ROOT / "tests"))
    from conformance import norm_defaults, norm_defaults_differential, norm_defaults_three_way
    from ve.norm_defaults import UnspecifiedDocument
    found = []
    for name, document, _ in norm_defaults.sources():
        if type(document) is UnspecifiedDocument:
            found.append((f"sources:{name}", document.env.to_dict(),
                          [rule.to_dict() for rule in document.author.rules]))
    for name, env, units, _ in norm_defaults_three_way.fixtures():
        found.append((f"three-way:{name}", deepcopy(env), deepcopy(units)))
    for seed in range(1000):
        env, rules, _ = norm_defaults_differential.case(seed)
        found.append((f"differential:{seed}", env.to_dict(), [rule.to_dict() for rule in rules]))
    return [(label, raw, units) for label, raw, units in found if in_domain(raw, units, defaults=True)]


def example_sources():
    sources = []
    for path in sorted(EXAMPLES.glob("*.json")):
        value = json.loads(path.read_text())
        sources.append(("example:" + path.stem, value["environment"], value["norms"]))
    return sources


def replay_sources():
    """The examples, the seeded mutations of U, and the sources of the unit's conformance scripts."""
    return example_sources() + list(generated_sources()) + conformance_sources()


def legacy_difference_sources(contract):
    """The candidates of S5-pre (2.12) for this unit: a `data@0` predicate with a `functional` flag under
    `norm-defaults@0` (Lean's decoder runs without data flags; `UnspecifiedDocument` has no such check)."""
    raw, norms = base()
    raw["profiles"] = ["data@0", "norm-defaults@0", "norms@0", "relational-fol@0"]
    raw["vocabulary"]["predicates"]["c"] = {"arguments": ["assistant", "assistant"], "description": "c",
                                            "functional": True}
    norms[0]["norm"]["guard"] = ["exists", "assistant", ["binary", "c", ["var", 1], ["var", 0]]]
    norms[1]["norm"]["unless"] = []
    return [("L:data-flag", raw, norms, None),
            ("L:constant-verbalisation", *norms_faults.verbalised(base()), None)]


def test_and_fixture_sources():
    """The `norm-defaults@0` sources of the contract tests: the fixtures of 8.2 that the tests build."""
    from tests.test_norm_defaults_contract import fixture_sources
    return [(f"fixture:{label}", raw, norms) for label, raw, norms in fixture_sources()]


__all__ = ["call_problems", "class_exempt", "own_text", "legacy_validation", "REGISTRY"]
