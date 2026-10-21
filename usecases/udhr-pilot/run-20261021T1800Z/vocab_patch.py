"""Extend a document's models and situation bases by new vocabulary and recompute every reading-set id (shared by the JT-0p and ET-0 steps).

Why not `tools/readings_s1_pilot.py --rebuild-reading-ids`: it extends every model and base by EVERY declared sort and by every
non-definition predicate (the regulated ones too).  A situation base of this pilot's content-bearing sets (u025, u027, u037) must not hold the
regulated predicates' relations (Lean's decode of the base refuses them), so the committed command is not a no-op on the unchanged parts 1, 2 and 4
and its output for them does not load (evidence/rebuild-command.json).  The rule here is the reference build's (research/judgment-terms/jt0p.py):
extend by the new vocabulary only, then recompute the ids with VE's own identity functions.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))


def extended(data, domains, constants, relations):
    data = copy.deepcopy(data)
    data["domains"] = dict(sorted({**{s: list(e) for s, e in domains.items() if s not in data["domains"]}, **data["domains"]}.items()))
    data["constants"] = dict(sorted({**data["constants"], **constants}.items()))
    data["relations"] = dict(sorted({**{p: [] for p in relations if p not in data["relations"]}, **data["relations"]}.items()))
    return data


def reidentified(environment, sets, domains, constants, model_relations, base_relations):
    """`domains`: new sort -> its elements; `constants`: new constant -> element; `model_relations`: new predicate names for a formula-set model;
    `base_relations`: new relation names for a situation base (non-regulated predicates and `unsaid__` of the regulated ones)."""
    from ve.ast import formula_from_data
    from ve.document import _environment
    from ve.identity import meaning_id
    from ve.model import FiniteModel
    from ve.readings import _reading_evaluation, s1_content_meaning_id
    from ve.wire import digest

    env = _environment(environment)
    model_env, _ = _reading_evaluation(env)
    out = []
    for item in sets:
        if any("companion" in r for r in item["readings"]):
            out.append(item)
            continue
        item = copy.deepcopy(item)
        renamed = {}
        if "models" in item:
            models = {}
            for old, data in item["models"].items():
                data = extended(data, domains, constants, model_relations)
                new = FiniteModel.from_dict(model_env, data).model_id
                renamed[old], models[new] = new, data
            item["models"] = models
        if "situations" in item:
            situations = {}
            for old, entry in item["situations"].items():
                entry = {**entry, "base": extended(entry["base"], domains, constants, base_relations)}
                new = digest(f"ve-situation-{env.identity_version}\n", {"environment_id": env.environment_id, "situation": entry})
                renamed[old], situations[new] = new, entry
            item["situations"] = situations
        for reading in item["readings"]:
            content = reading["content"]
            if type(content) is list:
                reading["meaning_id"] = meaning_id(env, formula_from_data(env, content))
            elif content is not None:
                reading["meaning_id"] = s1_content_meaning_id(env, item["id"], reading)
            reading["admission"]["distinguishing_models"] = {
                other: renamed.get(mid, mid) for other, mid in reading["admission"]["distinguishing_models"].items()}
        out.append(item)
    return out


def dropped(data, sorts=(), relations=()):
    """The inverse of `extended`: a model or situation base without the named sorts' domains and the named relations (20261021T0600Z repair)."""
    data = copy.deepcopy(data)
    for s in sorts:
        data["domains"].pop(s, None)
    for r in relations:
        data["relations"].pop(r, None)
    return data


def reidentified_by(environment, sets, transform):
    """Like `reidentified`, but `transform(data)` rewrites every model and every situation base; ids are recomputed over `environment`."""
    from ve.ast import formula_from_data
    from ve.document import _environment
    from ve.identity import meaning_id
    from ve.model import FiniteModel
    from ve.readings import _reading_evaluation, s1_content_meaning_id
    from ve.wire import digest

    env = _environment(environment)
    model_env, _ = _reading_evaluation(env)
    out = []
    for item in sets:
        if any("companion" in r for r in item["readings"]):
            out.append(item)
            continue
        item = copy.deepcopy(item)
        renamed = {}
        if "models" in item:
            models = {}
            for old, data in item["models"].items():
                data = transform(data)
                new = FiniteModel.from_dict(model_env, data).model_id
                renamed[old], models[new] = new, data
            item["models"] = models
        if "situations" in item:
            situations = {}
            for old, entry in item["situations"].items():
                entry = {**entry, "base": transform(entry["base"])}
                new = digest(f"ve-situation-{env.identity_version}\n", {"environment_id": env.environment_id, "situation": entry})
                renamed[old], situations[new] = new, entry
            item["situations"] = situations
        for reading in item["readings"]:
            content = reading["content"]
            if type(content) is list:
                reading["meaning_id"] = meaning_id(env, formula_from_data(env, content))
            elif content is not None:
                reading["meaning_id"] = s1_content_meaning_id(env, item["id"], reading)
            reading["admission"]["distinguishing_models"] = {
                other: renamed.get(mid, mid) for other, mid in reading["admission"]["distinguishing_models"].items()}
        out.append(item)
    return out
