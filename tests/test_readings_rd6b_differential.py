"""RD-6b: 200 generated norms-chain documents under the completion, the superposed route against the retained
enumerated oracle (plan RD-6b, fixtures; review B5 of rd-6b).

The documents are generated from a seed per index, not renamed copies of one: one or two pairs of regulated
predicates with an unspecified default, one or two open sentences on any pair, each with two or three readings drawn
from an unconditional duty, a duty under either of two conditions and a permission, and no fixed unit, a fixed
permission, a fixed duty under both conditions or a fixed prohibition unless a condition holds (which makes some choices
conflict and others not). Each pair of readings is separated by a situation chosen for the two templates.

Each document is answered on both routes and compared whole: the conflict status and every compatible choice's
status, the premise status and every candidate's, and a query (with or without `--under` a reading
of the first sentence). The generated answers cover CONFLICT and CONFLICT-FREE, and ALL, SOME, NONE and UNKNOWN.
"""
from __future__ import annotations

from collections import Counter
import random

import pytest

from tests.test_readings_nd_document import as_document
from tests.test_readings_nd_lean import environment, regulated
from tests.test_readings_s1_lean import entry, norm, reading, reading_set, situation_id

DOCUMENTS = 200
CHUNKS = 10
ACTS = {1: "{0} be done", 2: "{0} be tried"}
TEMPLATES = ("U", "C1", "C2", "P")
FIXED = ("none", "no-unless-c1", "may", "must-if-c1-c2")


def _condition(k):
    return ["unary", f"c{k}", ["var", 0]]


def _template(kind, i, name):
    """An unconditional duty (U), a duty under c1 or c2 (C1, C2) or a permission (P) on the i-th pair."""
    if kind == "U":
        return norm(name, f"p{i}_required", True)
    if kind in ("C1", "C2"):
        return norm(name, f"p{i}_required", True, guard=_condition(int(kind[1])))
    return norm(name, f"p{i}_permitted", True)


# For each pair of templates, the reading that the probe `p_i_required(a)` holds under, and whether c1 and c2 hold
# at `a` in the separating situation: the witness requires the act there, the other reading does not (no situation
# makes both conditions hold, so the fixed duty never decides the probe).
SEPARATING = {frozenset(("U", "C1")): ("U", (False, False)), frozenset(("U", "C2")): ("U", (False, False)),
              frozenset(("C1", "C2")): ("C1", (True, False)), frozenset(("U", "P")): ("U", (False, False)),
              frozenset(("C1", "P")): ("C1", (True, False)), frozenset(("C2", "P")): ("C2", (False, True))}


def generated(index):
    """The document of `index`: (environment, document, sentence texts, query, under, shape)."""
    rng = random.Random(f"rd6b-differential:{index}")
    pairs = rng.choice([1, 2])
    predicates = {"c1": {"arguments": ["act"], "description": "c1"},
                  "c2": {"arguments": ["act"], "description": "c2"}}
    for i in range(1, pairs + 1):
        predicates[f"p{i}_required"] = {"arguments": ["act"], "description": "obligation", "regulated": regulated(
            "obligation", "unspecified", ACTS[i], permission=f"p{i}_permitted")}
        predicates[f"p{i}_permitted"] = {"arguments": ["act"], "description": "permission",
                                         "regulated": regulated("permission", "unspecified", ACTS[i])}
    raw = environment(predicates, ("act",))

    def situation(witness, i, c1, c2):
        relations = {"c1": [["a"]] if c1 else [], "c2": [["a"]] if c2 else []}
        for j in range(1, pairs + 1):
            relations[f"unsaid__p{j}_permitted"] = [["a"]]
            relations[f"unsaid__p{j}_required"] = []
        return entry({"domains": {"act": ["a"]}, "constants": {}, "relations": relations}, witness,
                     {"outcome": {"predicate": f"p{i}_required", "tuple": ["a"]}}, True)

    units, sets, texts = [], [], {}
    fixed = rng.choice(FIXED)
    if fixed != "none":
        i = rng.randint(1, pairs)
        content = {"no-unless-c1": norm(f"no-p{i}", f"p{i}_permitted", False, guard=["not", _condition(1)]),
                   "may": norm(f"may-p{i}", f"p{i}_permitted", True),
                   "must-if-c1-c2": norm(f"must-p{i}-c1-c2", f"p{i}_required", True,
                                         guard=["and", _condition(1), _condition(2)])}[fixed]
        units.append({"id": "f0", "kind": "norm", "content": content})
        texts["f0"] = "A fixed sentence.\n"
    shape = [fixed]
    for k in range(rng.choice([1, 2])):
        i = rng.randint(1, pairs)
        kinds = rng.sample(TEMPLATES, rng.choice([2, 2, 3]))
        names = {kind: f"{kind.lower()}-{k}" for kind in kinds}
        situations, models = {}, {kind: {} for kind in kinds}
        for a, x in enumerate(kinds):
            for y in kinds[a + 1:]:
                witness, (c1, c2) = SEPARATING[frozenset((x, y))]
                sigma = situation(names[witness], i, c1, c2)
                sid = situation_id(raw, sigma)
                situations[sid] = sigma
                models[x][names[y]] = models[y][names[x]] = sid
        sets.append(reading_set(f"rs_{k}", f"u{k}", [
            reading(names[kind], _template(kind, i, f"r{k}-{kind.lower()}"), models[kind]) for kind in kinds],
            situations))
        units.append({"id": f"u{k}"})
        texts[f"u{k}"] = f"Open sentence {k}.\n"
        shape.append((i, tuple(kinds)))
    queries = [["forall", "act", ["unary", "p1_required", ["var", 0]]],
               ["forall", "act", ["implies", _condition(1), ["unary", "p1_required", ["var", 0]]]],
               ["forall", "act", ["implies", ["unary", "p1_required", ["var", 0]], ["unary", "p1_permitted", ["var", 0]]]]]
    choices = 1
    for reading_set_ in sets:
        choices *= len(reading_set_["readings"])
    # A countermodel per choice is the costly answer on both routes: the general queries run where the choices are
    # few, the implication (which follows from `Fill_T`) everywhere else.
    query = rng.choice(queries[:2]) if choices <= 4 else queries[2]
    under = rng.choice([None, [[sets[0]["id"], rng.randrange(len(sets[0]["readings"]))]]])
    return raw, {"units": units, "reading_sets": sets}, texts, query, under, tuple(shape)


def answers(route, query, under):
    """Everything compared: the conflict status and each choice's, the premise status and each candidate's, and
    the query's verdict."""
    conflict, premises = route.conflict(), route.premises()
    return {"conflict": (conflict["status"], [(c["choice"], c["status"]) for c in conflict["choices"]]),
            "premises": (premises["status"], [(c["set"], c["index"], c["status"]) for c in premises["candidates"]]),
            "query": route.entailment(query, assumed=under)["verdict"]}


def test_the_generated_documents_differ_in_shape():
    """Not one document renamed (review B5 of rd-6b): the shapes, fixed units, readings and choice counts vary."""
    shapes = Counter()
    sets, readings, fixed, choices, unders = Counter(), Counter(), Counter(), Counter(), 0
    for index in range(DOCUMENTS):
        _, document, _, _, under, shape = generated(index)
        shapes[shape] += 1
        sets[len(document["reading_sets"])] += 1
        fixed[shape[0]] += 1
        count = 1
        for reading_set_ in document["reading_sets"]:
            readings[len(reading_set_["readings"])] += 1
            count *= len(reading_set_["readings"])
        choices[count] += 1
        unders += under is not None
    assert len(shapes) >= 100 and max(shapes.values()) <= 6
    assert set(sets) == {1, 2} and set(readings) == {2, 3} and set(fixed) == set(FIXED)
    assert {2, 3, 4, 6, 9} <= set(choices)
    assert 60 <= unders <= 140


@pytest.mark.parametrize("chunk", range(CHUNKS))
def test_generated_documents_agree_on_both_routes(tmp_path, chunk):
    from ve.document import load_document
    from ve.readings_verdicts import Enumerated, Superposed
    seen = Counter()
    for index in range(chunk, DOCUMENTS, CHUNKS):
        raw, document, texts, query, under, _ = generated(index)
        (tmp_path / str(index)).mkdir()
        loaded = load_document(as_document(tmp_path / str(index), raw, document, texts))
        row = loaded["readings_s2"]
        count = 1
        for reading_set_ in document["reading_sets"]:
            count *= len(reading_set_["readings"])
        assert (row["route"], row["finding"], row["choices_checked"]) == ("superposed", None, count), index
        enumerated_row = {**row, "route": "enumerated", "finding": {
            "text": "ReadingsNotSuperposable: " + ", ".join(R["id"] for R in document["reading_sets"]),
            "cause": "the unspecified completion"}}
        superposed = answers(Superposed(loaded), query, under)
        enumerated = answers(Enumerated({**loaded, "readings_s2": enumerated_row}), query, under)
        assert superposed == enumerated, (index, superposed, enumerated)
        assert len(superposed["conflict"][1]) == count
        seen[superposed["conflict"][0]] += 1
        seen[superposed["query"]] += 1
    # Each chunk meets both conflict statuses and more than one verdict, so no chunk compares constants.
    assert seen["CONFLICT"] and seen["CONFLICT-FREE"], seen
    assert len({verdict for verdict in seen if verdict in ("ALL", "SOME", "NONE", "UNKNOWN")}) >= 2, seen
