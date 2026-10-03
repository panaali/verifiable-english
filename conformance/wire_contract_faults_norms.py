"""The fault catalogue and the gate corpus of `norms@0` (wire-contract-s5.md 2.3, 8.1, 8.4).

Every fault is applied to the base B of 8 (the contract's first example) and records, by hand, the check
that must be the first diagnostic when it alone is applied, the record's `path` and, for a check that is not
inherited, the record's `args`. The oracle of `conformance/wire_contract_faults.py` computes the rest. The
faults are the fixtures N2 to N40 of 8.1 (N14 is struck), with one more fault for each check that no fixture
reaches alone (3.5, 3.6, 3.9a and a second 1.1).
"""

from copy import deepcopy
import json
from pathlib import Path
import random
import sys

from conformance.wire_contract_faults import Fault, _replacing, _set_at
from ve.errors import VEError
from ve.norms_contract import REGISTRY, in_domain, legacy_validation

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "ve/wire_contract/examples/norms@0"
UNIT = "norms@0"
LEAN_ROUTE = "ve_norms_route"
CASE_KIND = "norms-elaborate"
FEASIBILITY_OF = 24
RECORDED_TESTS = ("tests/test_norms_contract*", "tests/test_norm_admission.py", "tests/test_norms.py",
                  "tests/test_norms_three_way.py")
# 8.4's allowed coverage gaps for this unit: G1 as the pilot's; G2 applies to no check of this unit; G3 to
# 4.3, whose guard names `norm-defaults@0`, outside this unit's domain.
GAP_APPLIES = {"G1": lambda faults: {f.check for f in faults} - {f.check for f in faults if f.readers != "python"},
               "G2": lambda faults: set(), "G3": lambda faults: {"4.3"}}
# 4.3 has no fault here (gap G3): `norm-defaults@0`'s catalogue holds it, as `w1/4.3` (4.4).
UNREACHED = {}
WHOLE_SOURCE_PARTNER = "environment-defined"
N = ("norms",)
P = ("environment", "vocabulary", "predicates")
ATOM = ["unary", "c", ["var", 0]]


def norm(name, predicate, sign, guard, unless=(), over=()):
    return {"norm": {"name": name, "predicate": predicate, "sign": sign, "guard": deepcopy(guard),
                     "unless": deepcopy(list(unless)), "over": list(over)}}


def base():
    """The base B (8): the contract's first example."""
    value = json.loads((EXAMPLES / "base.json").read_text())
    return value["environment"], value["norms"]


def balanced(formulas):
    """A balanced conjunction (8): the formula itself, or `and` over the first ⌈n/2⌉ and the rest."""
    if len(formulas) == 1:
        return deepcopy(formulas[0])
    half = (len(formulas) + 1) // 2
    return ["and", balanced(formulas[:half]), balanced(formulas[half:])]


def nots(count, inner):
    for _ in range(count):
        inner = ["not", inner]
    return inner


def _env(change):
    return lambda root: change(root["environment"])


def _rules(change):
    return lambda root: change(root["norms"])


def _guard(i, formula):
    return _set_at(N + (i, "norm", "guard"), formula)


REACH = ["reach", "plus", ["named", "c"], ["var", 0], ["var", 0]]
BUDGET = frozenset({"rule-budget"})


def _n2(raw):
    raw["profiles"] = ["relational-fol@0"]
    for entry in raw["vocabulary"]["predicates"].values():
        entry.pop("regulated", None)


def _n21(root):
    for i in (0, 1):
        root["norms"][i]["norm"]["guard"] = balanced([ATOM] * 1667)
    root["norms"][1]["norm"]["unless"] = []


def _n39(root):
    _n21(root)
    root["norms"][2]["norm"]["guard"] = ["unary", "d", ["var", 0]]


def _n38(root):
    root["environment"]["profiles"] = ["data@0", "norms@0", "relational-fol@0"]
    root["norms"][0]["norm"]["guard"] = ["forall", "$string", ["top"]]


def _names(*indices):
    return tuple(N + (i, "norm", "name") for i in indices)


def _fields(*pairs):
    return tuple(N + (i, "norm", field) for i, field in pairs)


# (name, check, path, apply, args, labels, reads): `args` None for an inherited check.
def _faults():
    seventeen = [norm(f"r{i}", "x_required", True, ["top"], over=[f"r{i - 1}"] if i else []) for i in range(17)]
    return [
        ("environment-defined", "1.1", "/environment", _env(lambda r: r["vocabulary"]["predicates"]["c"].update(
            defined={"arguments": ["assistant"], "body": ["top"]})), None, (), ()),
        ("environment-language", "1.1", "/environment", _set_at(("environment", "language"), "ve.core@0.1"),
         None, (), ()),
        ("profile-missing", "2.1", "/environment/profiles", _env(_n2), {}, (), ()),
        ("rules-limit", "2.2", "/norms", _rules(lambda rules: rules.extend(
            deepcopy({"norm": {**rules[0]["norm"], "name": f"r{i}"}}) for i in range(3, 257))), {}, (), ()),
        ("unit-field", "3.1", "/norms/1", _rules(lambda rules: rules[1].update(extra=1)), {}, (), ()),
        ("norm-shape", "3.2", "/norms/0/norm", _set_at(N + (0, "norm"), []), {}, (), ()),
        ("norm-fields", "3.3", "/norms/2/norm", _rules(lambda rules: rules[2]["norm"].pop("over")), {}, (), ()),
        ("unless-shape", "3.4", "/norms/1/norm/unless", _set_at(N + (1, "norm", "unless"), {}), {}, (), ()),
        ("over-shape", "3.5", "/norms/2/norm/over", _set_at(N + (2, "norm", "over"), "a0"), {}, (), ()),
        ("predicate-type", "3.6", "/norms/0/norm/predicate", _set_at(N + (0, "norm", "predicate"), 7),
         {}, (), ()),
        ("over-item", "3.7", "/norms/2/norm/over/1", _set_at(N + (2, "norm", "over"), ["a0", 7]), {}, (), ()),
        ("guard-depth", "3.8a", "/norms/0/norm/guard", _guard(0, nots(65, ["top"])), None, BUDGET, ()),
        ("guard-shape", "3.8b", "/norms/0/norm/guard", _guard(0, 5), None, (), ()),
        ("carve-out-shape", "3.9b", "/norms/1/norm/unless/1",
         _set_at(N + (1, "norm", "unless"), [ATOM, 5]), None, (), ()),
        ("carve-out-depth", "3.9a", "/norms/1/norm/unless/0",
         _set_at(N + (1, "norm", "unless"), [nots(65, ["top"])]), None, BUDGET, ()),
        ("guard-index", "3.8b", "/norms/0/norm/guard", _guard(0, ["unary", "c", ["var", True]]), None, (), ()),
        ("guard-reach-first", "3.8b", "/norms/0/norm/guard", _guard(0, ["and", REACH, nots(65, ["top"])]),
         None, BUDGET, ()),
        ("guard-depth-first", "3.8a", "/norms/0/norm/guard", _guard(0, ["and", nots(65, ["top"]), REACH]),
         None, BUDGET, ()),
        ("name-class", "4.1", "/norms/0/norm/name", _set_at(N + (0, "norm", "name"), "A0"), {"value": "A0"},
         (), ()),
        ("name-repeat", "4.2", "/norms/2/norm/name", _set_at(N + (2, "norm", "name"), "a0"), {"value": "a0"},
         (), _names(0)),
        ("predicate-unregulated", "4.4", "/norms/0/norm/predicate", _set_at(N + (0, "norm", "predicate"), "c"),
         {"value": "c"}, (), ()),
        ("sign-type", "4.5", "/norms/1/norm/sign", _set_at(N + (1, "norm", "sign"), "no"), {}, (), ()),
        ("carve-out-limit", "4.6", "/norms/1/norm/unless", _set_at(N + (1, "norm", "unless"), [ATOM] * 9),
         {}, (), ()),
        ("guard-arity", "4.7a", "/norms/0", _guard(0, ["binary", "c", ["var", 0], ["var", 0]]), None, (),
         _fields((0, "predicate"))),
        ("guard-predicate", "4.7b", "/norms/0", _guard(0, ["unary", "d", ["var", 0]]), None, (), ()),
        ("guard-scope", "4.7c", "/norms/0", _guard(0, ["unary", "c", ["var", 1]]), None, (),
         _fields((0, "predicate"))),
        ("rules-nodes", "4.7d", "/norms/2", _replacing(_n21, N + (0, "norm", "guard"), N + (1, "norm", "guard"),
                                                         N + (1, "norm", "unless")),
         None, BUDGET, _fields((2, "guard"), (2, "unless"))),
        ("carve-out-predicate", "4.7b", "/norms/1",
         _set_at(N + (1, "norm", "unless"), [ATOM, ["unary", "d", ["var", 0]]]), None, (), ()),
        ("guard-predicate-name", "4.7b", "/norms/0", _guard(0, ["unary", 7, ["var", 0]]), None, (), ()),
        ("guard-constant", "4.7b", "/norms/0", _guard(0, ["eq", ["const", 5], ["var", 0]]), None, (), ()),
        ("guard-sort", "4.7b", "/norms/0", _guard(0, ["forall", 5, ["top"]]), None, (), ()),
        ("guard-string-binder", "4.7e", "/norms/0", _replacing(_n38, ("environment", "profiles"),
                                                                N + (0, "norm", "guard")), None, (), ()),
        ("nodes-before-type", "4.7d", "/norms/2",
         _replacing(_n39, N + (0, "norm", "guard"), N + (1, "norm", "guard"), N + (1, "norm", "unless"),
                    N + (2, "norm", "guard")), None, BUDGET, _fields((2, "unless"))),
        ("over-unknown", "5.1", "/norms/2/norm/over/0", _set_at(N + (2, "norm", "over"), ["zz"]),
         {"value": "zz"}, (), ()),
        ("over-predicate", "5.2", "/norms/2/norm/over/0", _set_at(N + (2, "norm", "over"), ["b1"]),
         {"rule": "c2", "predicate": "x_required", "value": "b1", "parent_predicate": "x_permitted"}, (),
         _names(1, 2) + _fields((1, "predicate"), (2, "predicate"))),
        ("precedence-cycle", "6.1", "/norms", _set_at(N + (0, "norm", "over"), ["c2"]), {"detail": "a0, c2"},
         frozenset({"precedence"}), _names(0, 1, 2) + _fields((1, "over"), (2, "over"))),
        ("precedence-depth", "6.2", "/norms", _replacing(lambda root: root.update(norms=deepcopy(seventeen)), N),
         {}, frozenset({"precedence"}), ()),
        ("layer-cycle", "6.3", "/norms", _replacing(lambda root: (
            root["norms"][0]["norm"].update(guard=["unary", "x_permitted", ["var", 0]]),
            root["norms"][1]["norm"].update(guard=["unary", "x_required", ["var", 0]])),
            N + (0, "norm", "guard"), N + (1, "norm", "guard")),
         {"detail": "x_permitted, x_required"}, frozenset({"layers"}),
         _fields((0, "predicate"), (1, "predicate"), (1, "unless"), (2, "guard"), (2, "unless"))),
    ]


def catalogue():
    faults = []
    for name, check, path, apply, args, labels, reads in _faults():
        faults.append(Fault(name, check, path, apply, frozenset({name}) | frozenset(labels), reads=tuple(reads),
                            base=base, args=args))
    return faults


# ## The gate's other corpora and its unit rules

def handler_reaching(raw, norms):
    """A rejected source on which the call of D(N) reaches the statement of 2.8 (2.11): its environment
    decodes and lists `norms@0`, and its norms are objects with a member `norm`."""
    from ve.environment import Environment
    try:
        env = Environment(deepcopy(raw))
    except VEError:
        return False
    return ("norms@0" in env.profiles and type(norms) is list
            and all(type(unit) is dict and "norm" in unit for unit in norms))


def class_exempt(check, legacy_code):
    """2.12: the checks exempt from the class rule."""
    tail = check.rsplit("/", 1)[-1]
    return tail == "1.1" or (tail in ("3.8b", "3.9b") and legacy_code != "SyntaxError")


def own_text(record):
    """J10: the text of 3.8b or 3.9b at a non-first-order tag is the hook's own, not the decoder's."""
    return record["check"].rsplit("/", 1)[-1] in ("3.8b", "3.9b") and record["text"] == "invalid indexed formula"


def call_problems(label, raw, norms, legacy_error, reported, reaching):
    """Tier P, the call (2.11; 8.4, G2 and G12), filled in by the switch commit."""
    return []


def _mutations(rng, raw, norms):
    """One seeded random change of a source: a member of a rule replaced by a value of another type or a
    neighbouring value, a rule repeated or dropped, or a predicate's declaration changed."""
    choice = rng.randrange(10)
    if norms and choice < 7:
        rule = rng.choice(norms)["norm"]
        field = rng.choice(["name", "predicate", "sign", "guard", "unless", "over"])
        values = {"name": ["A", "", "a" * 65, 1, "a0", "b1", "x-y", "unsaid--x", "a'b"],
                  "predicate": ["c", "zz", 1, "x_permitted", "x_required"],
                  "sign": [1, None, "true", True, False],
                  "guard": [["top"], ["bottom"], ["unary", "c", ["var", 0]], ["unary", "c", ["var", 3]],
                            ["unary", "x_permitted", ["var", 0]], ["lt", ["var", 0], ["var", 0]], [],
                            ["unary", "c"], nots(70, ["top"]), ["exists", "assistant", ["top"]]],
                  "unless": [[], [["top"]], [["unary", "zz", ["var", 0]]], [["top"]] * 9, "x"],
                  "over": [[], ["a0"], ["b1"], ["c2"], ["zz"], [1], "a0"]}[field]
        rule[field] = deepcopy(rng.choice(values))
    elif norms and choice == 7:
        norms.append(deepcopy(rng.choice(norms)))
    elif norms and choice == 8:
        norms.pop(rng.randrange(len(norms)))
    else:
        predicates = raw["vocabulary"]["predicates"]
        predicates["c"]["arguments"] = rng.choice([["assistant"], ["user"], ["assistant", "user"]])
    return raw, norms


def generated_sources(count=400, seed=5):
    """Seeded sources: B with one to three random changes each."""
    rng = random.Random(seed)
    for index in range(count):
        raw, norms = base()
        for _ in range(1 + index % 3):
            raw, norms = _mutations(rng, raw, norms)
        if in_domain(raw, norms, defaults=False):
            yield f"generated:{index}", raw, norms


def conformance_sources():
    """The sources the unit's conformance scripts build (8.7): the generated documents of the W1 three-way
    tests (`tests/test_norms_three_way.py`: `corpus()` and `pair_corpus()`)."""
    if str(ROOT / "tests") not in sys.path:
        sys.path.append(str(ROOT / "tests"))  # the three-way module imports the tests' `subprocesses`
    from tests.test_norms_three_way import corpus, pair_corpus
    sources = []
    for name, documents in (("three-way", corpus()), ("pairs", pair_corpus())):
        sources += [(f"{name}:{i}", doc.env.to_dict(), [rule.to_dict() for rule in doc.rules])
                    for i, doc in enumerate(documents)]
    return sources


def example_sources():
    sources = []
    for path in sorted(EXAMPLES.glob("*.json")):
        value = json.loads(path.read_text())
        sources.append(("example:" + path.stem, value["environment"], value["norms"]))
    return sources


def replay_sources():
    """The examples, the seeded mutations of B, and the sources of the unit's conformance scripts."""
    return example_sources() + list(generated_sources()) + conformance_sources()


def legacy_difference_sources(contract):
    """The candidates of S5-pre (2.12) that belong to this unit: a layer cycle through a defined predicate
    under `definitions@0` (the Lean route's stratum graph has defined nodes; Python's layer graph does
    not). Each with the record both engines must report: clean, if Python accepts."""
    raw, norms = base()
    raw["profiles"] = ["definitions@0", "norms@0", "relational-fol@0"]
    raw["vocabulary"]["predicates"]["d"] = {"arguments": ["assistant"], "description": "d",
                                            "defined": {"arguments": ["assistant"],
                                                        "body": ["unary", "x_required", ["var", 0]]}}
    norms[0]["norm"]["guard"] = ["unary", "d", ["var", 0]]
    return [("L:defined-layer", raw, norms, None)]


def test_and_fixture_sources():
    """The `norms@0` sources of the contract tests: the fixtures of 8.1 and 8.3 that the tests build."""
    from tests.test_norms_contract import fixture_sources
    return [(f"fixture:{label}", raw, norms) for label, raw, norms in fixture_sources()]
