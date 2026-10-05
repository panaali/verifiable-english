"""The differential of docs/spec/composition-s1.md 9.3, seeded, since lean-first batch 3.

Generated sets (strict and default twins with random exception conditions and fixed units beside them, mixed
kinds, two acts, renamed twins that must not separate, rights candidates under a fixed limitation, the norms
chain) and faulty sources (each check of 4.1 broken once, malformed and misattributed situations). For each
document Python's search, an untrusted generator (docs/LEAN-FIRST-PLAN.md rule 3), records a situation per pair,
and Lean's `readings-validate` is the only answer: every situation the search finds is accepted by Lean, a set for
which the search finds none is refused, each fault is refused with the text of the check it breaks, and the route
(`ve.readings_route.validate`) relays every row, Lean's answer or its diagnostic with Lean's text. Python's
regeneration of the answer and Rust's replay of the situations were deleted in batch 3, so nothing else is
compared. The count is 1,000 (9.3), in a nightly test; the default run checks the first 200;
`VE_S1_DIFFERENTIAL_COUNT` lowers both for a quick run.

`test_separation_conservative_shadow` is 9.3's shadow of `separation_conservative` on the search's own evaluation
(the rule-3 duplicate of Lean's `sideValid` and `sideValue`): on pairs in which neither side owns a key, some
probe separates exactly when the two observation lists differ.
"""
from __future__ import annotations

import copy
import json
import os
import random
from itertools import product

import pytest

from tests import lean_routes

from tests.test_readings_s1_lean import LEAN, SOFT_PROFILES, env_k, env_rights, norm_object
from ve.errors import CheckerUnavailable, VEError
from ve.readings_route import run_lean, validate as route_validate
from ve.readings_s1 import Decoded, record_situations, search

SEED = 20261002
COUNT = int(os.environ.get("VE_S1_DIFFERENTIAL_COUNT", "1000"))
# The default run's prefix of those documents, which still breaks every check and exercises every generator.
QUICK_COUNT = min(COUNT, 200)
ASKS = ["binary", "asks", ["var", 1], ["var", 0]]
ASKS_ALL = ["forall", "agent", ["forall", "user", ASKS]]
NOT_ASKS_ALL = ["forall", "agent", ["forall", "user", ["not", ASKS]]]


@pytest.fixture(scope="module")
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("ve_readings_route is not built")
    return LEAN


def norm(name, pred, sign, mode="strict", over=(), guard=("top",), sufficient=(), necessary=(),
         decider="unstated"):
    body = norm_object(name, pred, sign, mode, over, guard)
    if mode == "default":
        body["exception"].update({"sufficient": list(sufficient), "necessary": list(necessary),
                                  "decided_by": decider})
    return {"norm": body}


def nulled(rng, body):
    """A norm object with some optional fields written as null, which Lean reads as absent (finding B,
    looprecheck2): `hard`, `alterable` and `rank` at any mode, `mode` on a strict rule."""
    keys = ["hard", "alterable", "rank"] + (["mode"] if body.get("mode", "strict") == "strict" else [])
    for key in keys:
        if rng.random() < 0.15:
            body[key] = None
    return body


def null_cited(rng, content):
    """A norm content with `cites: null` beside it, sometimes."""
    if type(content) is dict and "norm" in content:
        nulled(rng, content["norm"])
        if rng.random() < 0.15:
            content["cites"] = None
    return content


def reading(rid, content, kind="norm"):
    return {"id": rid, "kind": kind, "content": content, "meaning_id": "m",
            "admission": {"who": "w", "why": "y", "distinguishing_models": {}}}


def reading_set(sid, unit, readings):
    for r in readings:
        r["admission"]["distinguishing_models"] = {o["id"]: "none" for o in readings if o["id"] != r["id"]}
    return {"id": sid, "unit": unit, "version": 1, "status": "open", "readings": readings}


def unit(uid, content=None, kind="norm"):
    return {"id": uid, **({"kind": kind, "content": content} if content is not None else {"kind": kind})}


# ---------------------------------------------------------------------------------------------------------------
# Generators: (environment, document, faulty)

def twins(rng):
    pred = rng.choice(["avoid_required", "help_required"])
    guard = rng.choice([["top"], ASKS])
    sufficient = rng.choice([[], [ASKS]])
    necessary = rng.choice([[], [ASKS], [["bottom"]]])
    decider = rng.choice(["unstated", "operator"])
    candidates = [reading("strict", norm("twin", pred, True, guard=guard)),
                  reading("default", norm("twin", pred, True, "default", guard=guard, sufficient=sufficient,
                                          necessary=necessary, decider=decider))]
    rng.shuffle(candidates)
    units = [unit("u1")]
    other = "help_required" if pred == "avoid_required" else "avoid_required"
    if rng.random() < 0.4:
        units.append(unit("u2", norm("be-kind", other, True, "default")))
    if rng.random() < 0.3:
        units.append(unit("u3", norm("never", pred, False, guard=rng.choice([["top"], ASKS]))))
    if rng.random() < 0.2:
        units.append(unit("u4", norm("except-x", pred, False, over=("twin",), guard=ASKS)))
    if rng.random() < 0.2:
        units.append(unit("u5", norm("lenient", pred, False, "default", guard=ASKS)))
    if rng.random() < 0.3:
        units.append(unit("u6", rng.choice([ASKS_ALL, NOT_ASKS_ALL]), "asserted"))
    for r in candidates:
        null_cited(rng, r["content"])
    for u in units:
        null_cited(rng, u.get("content"))
    rng.shuffle(units)
    return env_k(), {"units": units, "reading_sets": [reading_set("rs1", "u1", candidates)]}, None


def renamed(rng):
    mode = rng.choice(["strict", "default"])
    candidates = [reading("a", norm("twin-a", "avoid_required", True, mode)),
                  reading("b", norm("twin-b", "avoid_required", True, mode))]
    return env_k(), {"units": [unit("u1")], "reading_sets": [reading_set("rs1", "u1", candidates)]}, None


def mixed(rng):
    candidates = [reading("assert", rng.choice([ASKS_ALL, NOT_ASKS_ALL]), "asserted"),
                  reading("rule", norm("rule", rng.choice(["avoid_required", "help_required"]), True,
                                       rng.choice(["strict", "default"])))]
    if rng.random() < 0.5:
        candidates.append(reading("other", rng.choice([ASKS_ALL, NOT_ASKS_ALL, ["top"]]), "asserted"))
    return env_k(), {"units": [unit("u1")], "reading_sets": [reading_set("rs1", "u1", candidates)]}, None


def two_acts(rng):
    candidates = [reading("avoid", norm("avoid-x", "avoid_required", True, rng.choice(["strict", "default"]))),
                  reading("help", norm("help-x", "help_required", True, rng.choice(["strict", "default"])))]
    profiles = SOFT_PROFILES if rng.random() < 0.7 else ("norms@0", "readings@1", "relational-fol@0")
    if len(profiles) == 3:
        for c in candidates:
            c["content"]["norm"].pop("mode", None)
            c["content"]["norm"].pop("exception", None)
    for c in candidates:
        null_cited(rng, c["content"])
    return env_k(profiles), {"units": [unit("u1")], "reading_sets": [reading_set("rs1", "u1", candidates)]}, None


def decoded_variant(rng, line):
    """`line` as written differently, decoded the same by Lean (`decodeLine`): an empty or null `cites` or
    `fan_out`, a strict norm's soft fields at their defaults or null, the keys in another order. Lean's input has no
    null (`wire` omits it), so an explicit null is the field's default (review finding B, looprecheck2)."""
    line = copy.deepcopy(line)
    if rng.random() < 0.3:
        line["cites"] = rng.choice([{}, None])
    if rng.random() < 0.2:
        line["fan_out"] = rng.choice([{}, None])
    if rng.random() < 0.1:
        line[rng.choice(["holder_slot", "liberty", "recognition"])] = None
    if line["norm"].get("mode", "strict") == "strict":
        for key, value in (("mode", "strict"), ("alterable", []), ("hard", False), ("rank", None)):
            if rng.random() < 0.2:
                line["norm"][key] = rng.choice([value, None])
    else:
        nulled(rng, line["norm"])
    if rng.random() < 0.3:
        line = dict(reversed(list(line.items())))
    return line


def rights(rng):
    arbitrary = ["binary", "arbitrary_arrest", ["var", 1], ["var", 0]]

    def claim(mode):
        return {"right": {"name": "r9", "holder": "person", "guard": ["top"], "lines": [
            {"kind": "claim", "norm": norm_object("no-arbitrary-arrest", "arrest_permitted", False, mode,
                                                  guard=arbitrary)}]}}
    candidates = [reading("strict", claim("strict"), "right"), reading("default", claim("default"), "right")]
    for r in candidates:
        # Lean's decoder defaults, written or not (an absent guard is `top`, an empty `fan_out` none).
        right = r["content"]["right"]
        if rng.random() < 0.3:
            right["guard"] = None
            if rng.random() < 0.5:
                del right["guard"]
        right["lines"] = [decoded_variant(rng, line) for line in right["lines"]]
    units = [unit("u9", kind="right")]
    if rng.random() < 0.6:
        conditions = [{"name": "determined_by_law", "role": rng.choice(["necessary", "sufficient"]),
                       "decided_by": None, "verbalisation": "the limitation is determined by law"}]
        if rng.random() < 0.5:
            del conditions[0]["decided_by"]
        limitation = {"name": "l29", "scope": "all", "kinds": "all", "decided_by": "unstated", "factors": [],
                      "conditions": conditions}
        if rng.random() < 0.2:
            # MissingExceptionDecider, whether the decider is absent or null.
            limitation["decided_by"] = None
            if rng.random() < 0.5:
                del limitation["decided_by"]
        units.append(unit("u29", {"limitation": limitation}, "limitation"))
    if rng.random() < 0.3:
        bar = {"name": "b30", "reading": rng.choice(["rule", "query"])}
        if rng.random() < 0.5:
            bar["decided_by"] = rng.choice(["unstated", None])
        units.append(unit("u30", {"bar": bar}, "bar"))
    rng.shuffle(units)
    return env_rights(), {"units": units, "reading_sets": [reading_set("rs9", "u9", candidates)]}, None


def faulty(rng):
    """A valid twin document with one fault (4.1's checks in turn, and the situation's)."""
    raw, document, _ = twins(random.Random(rng.random()))
    fault = rng.choice(["duplicate", "reserved", "interface", "attached", "witness", "situation-id", "decides",
                        "arity", "soft-over-hard", "norm-defaults", "line-order"])
    rs1 = document["reading_sets"][0]
    if fault == "duplicate":
        document["units"].append(unit("u7"))
        document["reading_sets"].append(reading_set("rs2", "u7", [reading("x", norm("twin", "help_required", True))]))
    elif fault == "reserved":
        for r in rs1["readings"]:
            r["content"]["norm"]["name"] = "rd-twin"
    elif fault == "interface":
        rs1["readings"][0]["content"]["norm"]["name"] = "twin-only"
        document["units"].append(unit("u7", norm("needs", "avoid_required", False, over=("twin-only",), guard=ASKS)))
    elif fault == "attached":
        document["units"].append(unit("u7"))
        document["reading_sets"].append(reading_set("rs2", "u7", [
            reading("strict", norm("be-good", "help_required", True)),
            reading("default", norm("be-good", "help_required", True, "default"))]))
        document["units"].append(unit("u8", norm("both", "avoid_required", False, over=("twin", "be-good"),
                                                 guard=ASKS)))
    elif fault == "soft-over-hard":
        document["units"].append(unit("u7", norm("hard", rs1["readings"][0]["content"]["norm"]["predicate"], True)))
        for r in rs1["readings"]:
            if r["content"]["norm"].get("mode") == "default":
                r["content"]["norm"]["over"] = ["hard"]
    elif fault == "norm-defaults":
        raw = env_k(("norm-defaults@0", *SOFT_PROFILES))
    elif fault == "line-order":
        raw, document, _ = rights(random.Random(rng.random()))
        # The repeated line as written may differ from the first; Lean compares them decoded.
        line = document["reading_sets"][0]["readings"][0]["content"]["right"]["lines"][0]
        document["reading_sets"][0]["readings"][0]["content"]["right"]["lines"].append(
            decoded_variant(rng, copy.deepcopy(line)))
    return raw, document, fault


def environment_nulled(rng, raw):
    """`raw` with some optional environment fields written as null, which Lean reads as absent (review finding B,
    compose-s1-loop): a soft or rights block the environment leaves out, a base predicate's `regulated` and any
    predicate's `instruction_of`, and the rights block's `protected` and `alters` (optional to Lean's decoder: an
    absent one is empty, under the identity of the environment without it)."""
    raw = copy.deepcopy(raw)
    vocabulary = raw["vocabulary"]
    for key in ("soft", "rights"):
        if key not in vocabulary and rng.random() < 0.15:
            vocabulary[key] = None
    for declaration in vocabulary["predicates"].values():
        for key in ("regulated", "instruction_of"):
            if key not in declaration and rng.random() < 0.1:
                declaration[key] = None
    if type(vocabulary.get("rights")) is dict:
        for key in ("protected", "alters"):
            if rng.random() < 0.15:
                vocabulary["rights"][key] = None
    return raw


GENERATORS = [(twins, 5), (renamed, 1), (mixed, 2), (two_acts, 1), (rights, 2), (faulty, 3)]


def generate(rng):
    pick = rng.choices([g for g, _ in GENERATORS], weights=[w for _, w in GENERATORS])[0]
    return pick.__name__, *pick(rng)


def mutate_situation(raw, document, fault):
    """The faults that need a recorded situation: a third reading as witness, a wrong id, a decision on a key the
    witness does not own, a tuple of the wrong arity. All but the wrong id are recorded under their own id."""
    from ve.readings_s1 import S1Environment
    rs = document["reading_sets"][0]
    if not rs.get("situations"):
        return
    sid, entry = next(iter(rs["situations"].items()))
    if fault == "witness":
        rs["readings"].append(reading("third", norm("third", "help_required", True)))
        for r in rs["readings"][:-1]:
            r["admission"]["distinguishing_models"]["third"] = sid
        rs["readings"][-1]["admission"]["distinguishing_models"] = {r["id"]: sid for r in rs["readings"][:-1]}
        witness = entry["witness"]
        entry = {**entry, "witness": "third"}
    elif fault == "situation-id":
        entry["value"] = not entry["value"]
        return
    elif fault == "decides":
        entry = {**entry, "decisions": entry["decisions"] + [{"key": {"excepted": "be-kind"}, "tuples": []}]}
    elif fault == "arity":
        entry = {**entry, "decisions": [{"key": {"excepted": "twin"}, "tuples": [["a"]]}]}
    else:
        return
    new = S1Environment(raw).situation_id(entry)
    rs["situations"] = {(new if k == sid else k): (entry if k == sid else v) for k, v in rs["situations"].items()}
    for r in rs["readings"]:
        r["admission"]["distinguishing_models"] = {o: (new if m == sid else m)
                                                   for o, m in r["admission"]["distinguishing_models"].items()}
    if fault == "witness":
        # The twins' own pair keeps its situation; the third reading's situation is recorded for the twins.
        rs["situations"][sid] = {**entry, "witness": witness}
        for r in rs["readings"][:-1]:
            for o in list(r["admission"]["distinguishing_models"]):
                if o != "third":
                    r["admission"]["distinguishing_models"][o] = new


# The search proposes before Lean has seen the document: on a source Lean refuses it may fail in any way, and
# then proposes nothing (rule 3: a generator's failure is never a verdict).
SEARCH_FAILURES = (VEError, KeyError, TypeError, ValueError, AttributeError, IndexError, StopIteration)


def generated_cases(count=COUNT):
    """The seeded documents with the situations the search found recorded, as `readings-validate` cases, and per
    case (generator, fault, whether every pair has a situation, whether some pair has none)."""
    rng = random.Random(SEED)
    cases, expectations = [], []
    for n in range(count):
        name, raw, document, fault = generate(rng)
        # Its own generator, so that the documents are the ones generated without the nulls.
        raw = environment_nulled(random.Random(f"{SEED}-environment-{n}"), raw)
        rs = document["reading_sets"][0]
        found = {}
        try:
            found = search(raw, document, rs["id"])
        except SEARCH_FAILURES:
            pass
        document["reading_sets"][0] = record_situations(rs, {k: v for k, v in found.items() if v is not None})
        if fault in ("witness", "situation-id", "decides", "arity"):
            mutate_situation(raw, document, fault)
        complete = bool(found) and all(v is not None for v in found.values())
        cases.append({"id": f"c{n}", "kind": "readings-validate", "environment": raw, "document": document})
        expectations.append((name, fault, complete, bool(found) and not complete))
    return cases, expectations


def routed(case):
    """The route's outcome on a case: Lean's row without its id, its diagnostic, or `CheckerUnavailable`."""
    units = [{"id": u["id"], "kind": u.get("kind"), **({"content": u["content"]} if "content" in u else {})}
             for u in case["document"]["units"]]
    try:
        row = route_validate(case["environment"], units, case["document"]["reading_sets"])
    except CheckerUnavailable:
        return "CheckerUnavailable"
    except VEError as exc:
        return {"status": "error", "error": exc.message if hasattr(exc, "message") else str(exc)}
    return {k: v for k, v in row.items() if k != "id"}


def test_generated_sets_lean_answers(lean):
    """The first QUICK_COUNT documents of the nightly run (the same seeds, in order)."""
    generated_sets_lean_answers(QUICK_COUNT)


@pytest.mark.nightly
def test_all_generated_sets_lean_answers(lean):
    """9.3's 1,000 documents: runs with `-m nightly` and in tools/gate.py."""
    generated_sets_lean_answers(COUNT)


def generated_sets_lean_answers(count):
    cases, expectations = generated_cases(count)
    rows = []
    for start in range(0, len(cases), 50):
        rows.extend(run_lean(cases[start:start + 50]))
    kinds = {}
    texts = {}
    for n, (case, row, (name, fault, complete, missing)) in enumerate(zip(cases, rows, expectations)):
        if n % 20 == 0:
            # The route relays Lean's row (a sample: one route process per case).
            assert routed(case) == {key: value for key, value in row.items() if key != "id"}, (n, name, fault)
        if fault is None and complete:
            # Every situation the search finds is accepted by Lean.
            assert row["status"] == "ok", (n, name, row)
        if fault is None and missing:
            # A pair for which the search finds none is rejected.
            assert row["status"] == "error", (n, name, row)
        if fault is not None:
            assert row["status"] == "error" or fault in ("witness", "situation-id", "decides", "arity"), \
                (n, name, fault, row)
        kinds.setdefault((name, row["status"]), 0)
        kinds[(name, row["status"])] += 1
        if fault is not None:
            texts.setdefault(fault, set()).add(row.get("error", "ok"))
    # Each fault was rejected, at least once, by the check it breaks, with its text.
    expected = {"duplicate": "DuplicateDeclaration: twin in reading sets rs1 and rs2",
                "reserved": "InvalidInput: name rd-twin begins with rd-",
                "interface": "ReadingInterface: rs1: twin-only",
                "attached": "UnsupportedProfile: readings@1 fixed unit u8 depends on reading sets rs1 and rs2",
                "witness": "InvalidInput: invalid situation", "situation-id": "distinguishing model id does not match",
                "decides": "InvalidInput: situation", "arity": "InvalidInput: invalid situation",
                "soft-over-hard": "SoftOverHard: rule twin over hard",
                "norm-defaults": "UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented",
                "line-order": "InvalidInput: line order lists a line of right r9 twice"}
    for fault, prefix in expected.items():
        assert any(text.startswith(prefix) for text in texts.get(fault, ())), (fault, texts.get(fault))
    # Every generator was exercised, admitted and refused sets alike.
    assert {name for name, _ in kinds} == {g.__name__ for g, _ in GENERATORS}, kinds
    assert kinds.get(("twins", "ok")) and kinds.get(("renamed", "error")) and kinds.get(("faulty", "error")), kinds


def test_separation_conservative_shadow(lean):
    """9.3: where neither reading owns a key, some probe separates exactly when the observation lists differ."""
    rng = random.Random(SEED + 1)
    checked = 0
    for _ in range(60):
        pick = rng.choice([mixed, two_acts, renamed])
        raw, document, _ = pick(rng)
        if pick is renamed:
            for r in document["reading_sets"][0]["readings"]:
                r["content"]["norm"]["mode"] = "strict"
                r["content"]["norm"].pop("exception", None)
        admission = Decoded(raw, document)
        R = admission.doc.sets[0]
        pairs = [(i, j) for i in range(len(R.candidates)) for j in range(len(R.candidates)) if i < j]
        for i, j in pairs:
            if admission.owned_keys(R.id, i) or admission.owned_keys(R.id, j):
                continue
            for base in _bases(admission):
                if not (admission.side_valid(R.id, i, base, []) and admission.side_valid(R.id, j, base, [])):
                    continue
                probes = _probes_of(admission, base)
                left = [admission.side_value(R.id, i, base, [], q) for q in probes]
                right = [admission.side_value(R.id, j, base, [], q) for q in probes]
                separating = [(q, a) for q, a, b in zip(probes, left, right) if a is not None and a != b] + \
                    [(q, b) for q, a, b in zip(probes, left, right) if b is not None and a != b]
                assert bool(separating) == (left != right), (pick.__name__, i, j)
                checked += 1
    assert checked > 50


def _bases(admission):
    from ve.model import FiniteModel
    author = admission.senv.author_environment()
    for asks in ([], [["a", "u"]]):
        yield FiniteModel._decode(author, {"complete": True, "domains": {"agent": ["a"], "user": ["u"]},
                                           "constants": {}, "relations": {"asks": asks}}, _defer_model_id=True)


def _probes_of(admission, base):
    """`probesOf`: every outcome and selects probe on the frame's regulated predicates, typed tuples."""
    from ve.readings_s1 import PROBE_KINDS
    regulated = admission.senv.regulated
    probes = []
    for p in sorted(regulated):
        rows = list(product(*(base.domains[s] for s in regulated[p].arguments)))
        probes += [("outcome", p, row) for row in rows]
        probes += [(k, p, row) for k in PROBE_KINDS for row in rows]
    return probes
