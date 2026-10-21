"""Audit repair of run 20261021T1800Z (the 20261021T0600Z audit rejected u048).  Nothing here calls a model.

    uv run --frozen python usecases/udhr-pilot/run-20261021T1800Z/repair_20261021t1800.py [--dry-run]

u048 (Article 13(1)) "Everyone has the right to freedom of movement and residence within the borders of each state."  The audit: "within the
borders of each state" can qualify movement and residence together, or residence alone; one opaque predicate repeated the ambiguity.  The unit
becomes a reading set of two entitlements (one per scope), each ONE right (who holds it, nothing more; no duty reading), with a model that
separates them.  The old predicate `has_the_right_to_movement_and_residence` is removed everywhere (vocabulary, relations of every model and
situation base, the companion document, its witnesses); every reading-set id is recomputed over the new environment (vocab_patch.reidentified_by).
Part 2 and the whole declaration are changed; every other unit is left exactly as it was.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE.parents[2] / "tools"))
import vocab_patch as V  # noqa: E402

OLD = "has_the_right_to_movement_and_residence"
BOTH = "right_to_movement_and_residence_within_borders"
ONLY = "right_to_movement_and_residence_borders_on_residence"
SET = "rs_u048"
DOCS = {"part02": HERE / "translation-part02.ve.md", "whole": HERE / "experiment-whole" / "translation-whole.ve.md"}

PREDICATES = {
    BOTH: {"arguments": ["person"],
           "description": "The person has the right to freedom of movement within the borders of each state and to freedom of residence within "
                          "the borders of each state",
           "verbalisation": "{0} has the right to freedom of movement within the borders of each state as well as to freedom of residence "
                            "within the borders of each state"},
    ONLY: {"arguments": ["person"],
           "description": "The person has the right to freedom of movement (not said to be within the borders of each state) and to freedom of "
                          "residence within the borders of each state",
           "verbalisation": "{0} has the right to freedom of movement as well as to freedom of residence within the borders of each state"}}
UNSPEC = ("Completion 'unspecified' (norm-defaults@0): where the rule's guard fails, or the party is not one the rule names, the case is "
          "UNDECIDED, never 'not required' and never permitted; strict force, because the source states no exception.")
NOBEARER = "The words name no one who must act, so the candidate names no bearer (the responsibility stays unspecified)."
WHY = {
    "borders_over_both": ("Entitlement reading of Article 13(1) in which 'within the borders of each state' qualifies both 'movement' and "
                          "'residence': every person has the right to freedom of movement within the borders of each state and to freedom of "
                          f"residence within the borders of each state. {NOBEARER} {UNSPEC}"),
    "borders_residence_only": ("Entitlement reading of Article 13(1) in which 'within the borders of each state' qualifies 'residence' alone: "
                               "every person has the right to freedom of movement (the words then attach no borders to it) and to freedom of "
                               f"residence within the borders of each state. {NOBEARER} {UNSPEC}")}
CANDIDATES = [("borders_over_both", BOTH), ("borders_residence_only", ONLY)]


def read(path):
    raw = Path(path).read_bytes()
    _, front, source = raw.split(b"---\n", 2)
    return json.loads(front), source


def write(path, meta, source):
    Path(path).write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False).encode() + b"\n---\n" + source)


def separating_model(env, meta_constants):
    """Every relation empty except `BOTH` at the one person: the first reading holds, the second fails."""
    from ve.readings import _reading_evaluation
    model_env, _ = _reading_evaluation(env)
    domains = {s: [] for s in model_env.model_sorts}
    domains["person"] = ["p0"]
    constants = {}
    for name, entry in sorted(meta_constants.items()):
        domains[entry["sort"]] = [*domains[entry["sort"]], name]
        constants[name] = name
    relations = {p: [] for p in model_env.predicates if p not in model_env.definition_entries}
    relations[BOTH] = [["p0"]]
    return {"complete": True, "constants": constants, "domains": dict(sorted(domains.items())), "relations": dict(sorted(relations.items()))}


def repair(meta):
    from ve.ast import formula_from_data
    from ve.document import _environment
    from ve.identity import meaning_id
    from ve.model import FiniteModel
    from ve.readings import _reading_evaluation
    vocab = meta["environment"]["vocabulary"]
    assert OLD in vocab["predicates"] and BOTH not in vocab["predicates"]
    unit = next(u for u in meta["units"] if u["id"] == "u048")
    assert unit["kind"] == "asserted" and unit["content"]["ast"] == ["forall", "person", ["unary", OLD, ["var", 0]]], unit
    users = [u["id"] for u in meta["units"] if OLD in json.dumps(u)]
    assert users == ["u048"], users
    assert not any(s["unit"] == "u048" for s in meta["reading_sets"])
    del vocab["predicates"][OLD]
    vocab["predicates"] = dict(sorted({**vocab["predicates"], **copy.deepcopy(PREDICATES)}.items()))
    span = unit["span"]
    unit.clear()
    unit.update({"id": "u048", "kind": "norm", "meaning": "specified", "span": span, "support": "none"})

    def transform(data):
        data = V.dropped(data, relations=[OLD])
        data["relations"] = dict(sorted({**data["relations"], **{p: [] for p in PREDICATES if p not in data["relations"]}}.items()))
        return data
    sets = V.reidentified_by(meta["environment"], meta["reading_sets"], transform)
    # the new set (models, as u073's: the readings are plain formulas over the new predicates)
    env = _environment(meta["environment"])
    model_env, _ = _reading_evaluation(env)
    model = separating_model(env, vocab["constants"])
    model_id = FiniteModel.from_dict(model_env, model).model_id
    readings = []
    for cid, stem in CANDIDATES:
        content = ["forall", "person", ["unary", stem, ["var", 0]]]
        other = next(c for c, _ in CANDIDATES if c != cid)
        readings.append({"id": cid, "kind": "asserted", "meaning_id": meaning_id(env, formula_from_data(env, content)), "content": content,
                         "admission": {"who": "translator", "why": WHY[cid], "distinguishing_models": {other: model_id}}})
    new = {"id": SET, "unit": "u048", "version": 1, "status": "open", "readings": readings, "models": {model_id: model}}
    order = [u["id"] for u in meta["units"]]
    sets.append(new)
    meta["reading_sets"] = sorted(sets, key=lambda s: order.index(s["unit"]))
    return meta


def main():
    dry = "--dry-run" in sys.argv
    for label, path in DOCS.items():
        meta, src = read(path)
        new = repair(copy.deepcopy(meta))
        if not dry:
            write(path, new, src)
        print("repaired", label, "(dry run)" if dry else "", flush=True)


if __name__ == "__main__":
    main()
