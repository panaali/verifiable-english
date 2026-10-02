"""The asimov-extended documents and the 51 decision records of PLAN.md section 5.

Every record is a `risk@0` decision of the robot `R` (`r` in a witness model,
whose elements must be lower-case). Each (action, harm) cell cites one
annotator statement: `leads`, `might` or `cannot`. The base facts of PLAN.md
section 3 are in every record; the scenario's own facts come after them.
"""
from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from conformance.alternatives import cases as spec_cases  # noqa: E402
from conformance.risk import Log, record, statement  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.norm_english import parse_english, render_english  # noqa: E402
from ve.norms import Norm, NormDocument  # noqa: E402

V2 = REPO / "usecases" / "asimov-laws"
ANNOTATOR = "the Asimov case annotator"

HUMAN = ("death_1", "death_2", "death_3", "injury_1")
HUMANITY = ("humanity_harm",)
SELF = ("robot_destroyed", "robot_damaged")
HARMS = ("humanity_harm", "death_1", "death_2", "death_3", "injury_1", "property_damage",
         "robot_destroyed", "robot_damaged")
FACT_PREDICATES = ("ordered", "injures_human", "injures_humanity", "protects_robot", "ordered_before", "outranks")

# Stable names of the rules: v2's for rules 1-13, and one per addition.
# The names fix the order of each inlined disjunction (norms.md 4.1), and so the nesting depth of the
# conflict targets; `tie-` sorts after v2's `law-` names and keeps them inside VE's 64-level limit.
ADDITION_NAMES = [
    "tie-lawful-action", "tie-candidate-lawful", "tie-candidate-no-lawful-competitor", "tie-possibly-harmful-human",
    "tie-precaution", "tie-least-severe-worst-case", "tie-valid-order", "tie-order-authority",
    "tie-order-earlier", "tie-overridden-order", "tie-overridden-not-required", "tie-possibly-harmful-robot",
    "tie-def-own-robot-harm", "tie-def-competes-with", "tie-def-less-severe-competitor",
    "tie-def-beaten-by-a-candidate",
]


def environment(raw=None):
    data = json.loads((HERE / "environment.json").read_text()) if raw is None else raw
    return data


def v2_document():
    env = Environment(json.loads((V2 / "environment.json").read_text()))
    source = (V2 / "rules.ve").read_text()
    return parse_english(env, source, json.loads((V2 / "rules.manifest.json").read_text()))


def source_text(extended=True):
    """rules.ve is base.ve (v2's bytes, no final newline) followed by the additions, rules 14-29."""
    return (HERE / ("rules.ve" if extended else "base.ve")).read_text()


def _named(env, doc, names):
    """Rename the parsed rules (`rule-N`) to their stable names, keeping every reference."""
    mapping = {rule.name: name for rule, name in zip(doc.rules, names)}
    rules = [Norm(mapping[r.name], r.predicate, r.sign, r.guard, r.unless, tuple(mapping[o] for o in r.over))
             for r in doc.rules]
    return NormDocument(env, rules)


def rule_names(extended=True):
    names = [block["name"] for block in json.loads((V2 / "rules.manifest.json").read_text())["blocks"]]
    return names + ADDITION_NAMES if extended else names


@lru_cache(maxsize=4)
def document(extended=True):
    """The parsed document, bound to the manifest when it is checked in (base + additions)."""
    env = Environment(environment())
    text = source_text(extended)
    manifest_path = HERE / ("rules.manifest.json" if extended else "base.manifest.json")
    if manifest_path.exists():
        return parse_english(env, text, json.loads(manifest_path.read_text()))
    return _named(env, parse_english(env, text), rule_names(extended))


def render_manifest(extended=True):
    env = Environment(environment())
    return render_english(_named(env, parse_english(env, source_text(extended)), rule_names(extended)))


def norms(extended=True, replace=None):
    """W1 norm objects of the document, with fields of named rules optionally replaced (mutants)."""
    rules = [rule.to_dict() for rule in document(extended).rules]
    for rule in rules:
        if replace and rule["norm"]["name"] in replace:
            rule["norm"].update(replace[rule["norm"]["name"]])
    return rules


# ---------------------------------------------------------------------------- scenarios

def scenario(actions, leads=(), might=(), **facts):
    """A record spec: every cell not listed as `leads` or `might` is `cannot`."""
    cells = {(a, h): "cannot" for a in actions for h in HARMS}
    for a, h in might:
        cells[(a, h)] = "might"
    for a, h in leads:
        cells[(a, h)] = "leads"
    rows = {name: [list(row) if isinstance(row, (list, tuple)) else [row] for row in facts.get(name, ())]
            for name in FACT_PREDICATES}
    return {"actions": list(actions), "cells": cells, "facts": rows}


def from_v2(model, mapping):
    """A v2 alternatives model as a record spec, with v2's harms renamed by the fixed mapping (PLAN.md 5)."""
    relations = model["relations"]
    actions = model["domains"]["action"]
    leads = [(a, mapping[h]) for a, h in relations["leads_to"]]
    facts = {name: [tuple(row) for row in relations.get(name, [])] for name in FACT_PREDICATES}
    for h in model["domains"]["harm"]:
        # The harm's class and facts come with its constant (PLAN.md 3); v2's facts must agree.
        human = [h] in relations["harms_human"]
        humanity = [h] in relations["harms_humanity"]
        self_harm = [h, "r"] in relations.get("harm_to", [])
        assert (human, humanity, self_harm) == (mapping[h] in HUMAN, mapping[h] in HUMANITY,
                                                mapping[h] in SELF), (h, mapping[h])
    return scenario(actions, leads=leads, **facts)


SPEC_GROUPS = ["a", "b-A0", "b-A1", "c-7", "o-7", "d-full", "e", "j", "l5"]
SPEC_MAPPING = {"a": {"h1": "death_1"}, "c-7": {"h": "death_1"}, "o-7": {"h": "death_1"}, "l5": {"h": "death_1"},
                "d-full": {"hs": "robot_destroyed"}, "e": {"hp": "injury_1", "hh": "humanity_harm"}, "j": {}}
VARIANTS = {"FI": ("death_1", "injury_1"), "FF": ("death_1", "death_2"), "IF": ("injury_1", "death_1")}
REGRESSION_MAPPING = {"hp": "death_1", "hh": "humanity_harm", "hs": "robot_destroyed", "hs2": "robot_damaged"}


def spec_records():
    models = {item["id"]: item["scenario"]["model"] for item in spec_cases()}
    out = {}
    for name in SPEC_GROUPS:
        if name in ("b-A0", "b-A1"):
            for variant, (h1, h2) in VARIANTS.items():
                out[f"{name} {variant}"] = from_v2(models[name], {"h1": h1, "h2": h2})
        else:
            out[name] = from_v2(models[name], SPEC_MAPPING[name])
    return out


def regression_records():
    sys.path.insert(0, str(REPO / "tests"))
    from test_asimov_laws import REGRESSIONS
    return {name: from_v2(situation["model"], REGRESSION_MAPPING) for name, (situation, _) in REGRESSIONS.items()}


J = ("a1", "a2", "nothing")
O_RECORDS = {
    "O1 j-earlier": scenario(J, ordered=["a1", "a2"], ordered_before=[("a1", "a2")]),
    "O2 j-later-more-authority": scenario(J, ordered=["a1", "a2"], ordered_before=[("a1", "a2")],
                                          outranks=[("a2", "a1")]),
    "O3 j-earlier-more-authority": scenario(J, ordered=["a1", "a2"], ordered_before=[("a1", "a2")],
                                            outranks=[("a1", "a2")]),
    "O4 j-simultaneous-more-authority": scenario(J, ordered=["a1", "a2"], outranks=[("a2", "a1")]),
    "O5 j-later-authority-risky": scenario(J, might=[("a2", "injury_1")], ordered=["a1", "a2"],
                                           ordered_before=[("a1", "a2")], outranks=[("a2", "a1")]),
    "O6 j-later-authority-unlawful": scenario(J, leads=[("a2", "death_1")], ordered=["a1", "a2"],
                                              ordered_before=[("a1", "a2")], outranks=[("a2", "a1")]),
}

P_RECORDS = {
    "P1 risky-rescues": scenario(("nothing", "rescue_a", "rescue_b"), leads=[("nothing", "death_1")],
                                 might=[("rescue_a", "death_1"), ("rescue_a", "robot_destroyed"),
                                        ("rescue_b", "injury_1")]),
    "P2 certain-injury-vs-possible-death": scenario(("nothing", "rescue"), leads=[("nothing", "injury_1")],
                                                    might=[("rescue", "death_1")]),
    "P3 ordered-possible-injury": scenario(("nothing", "obey"), might=[("obey", "injury_1")], ordered=["obey"]),
    "P4 ordered-possible-robot-loss": scenario(("nothing", "obey"), might=[("obey", "robot_destroyed")],
                                               ordered=["obey"]),
    "P5 unequal-necessary-injuries": scenario(("nothing", "act", "act2"),
                                              leads=[("nothing", "humanity_harm"), ("act", "death_1"),
                                                     ("act2", "injury_1")], injures_human=["act", "act2"]),
    "P6 two-deaths-vs-one": scenario(("nothing", "pull"), leads=[("nothing", "death_1"), ("nothing", "death_2"),
                                                                 ("pull", "death_3")]),
    "P7 injury-vs-property": scenario(("nothing", "swerve", "brake"), leads=[("nothing", "death_1")],
                                      might=[("swerve", "injury_1"), ("brake", "property_damage")]),
    "P8 all-break-zeroth": scenario(("nothing", "act"), leads=[("nothing", "humanity_harm")],
                                    injures_humanity=["act"]),
    "P9 unordered-possible-robot-loss": scenario(("nothing", "act"), might=[("act", "robot_destroyed")]),
    "P10 risky-rescue-only": scenario(("nothing", "rescue"), leads=[("nothing", "death_1")],
                                      might=[("rescue", "robot_destroyed")]),
}


@lru_cache(maxsize=1)
def all_records():
    """The 51 records of PLAN.md section 5, by group, in the plan's order."""
    groups = {"S": spec_records(), "R": regression_records(), "O": O_RECORDS, "P": P_RECORDS}
    return {f"{group}:{name}": spec for group, records in groups.items() for name, spec in records.items()}


# ---------------------------------------------------------------------------- wire form

def base_facts(chooser):
    return ([("harms_human", [h]) for h in HUMAN] + [("harms_humanity", [h]) for h in HUMANITY]
            + [("harm_to", [h, chooser]) for h in SELF])


def decision(spec, policy, chooser="R"):
    """The log and the decision entry of one record; the facts cite the first statement."""
    log = Log()
    order = [(a, h) for a in spec["actions"] for h in HARMS]
    for seq, (a, h) in enumerate(order, start=1):
        log.add(seq, f"T{seq}", "statement", statement(a, h, spec["cells"][(a, h)], author=ANNOTATOR))
    facts = base_facts(chooser) + [(name, row) for name in FACT_PREDICATES for row in spec["facts"][name]]
    facts = [{"predicate": p, "args": list(args), "entry": "T1"} for p, args in facts]
    alternatives = [{"name": a, "label": a.replace("_", " ")} | ({"inaction": True} if a == "nothing" else {})
                    for a in spec["actions"]]
    dx = log.add(len(order) + 1, "DX", "decision",
                 record("x", chooser, "the robot", policy, alternatives, [], log.cite(*[e["id"] for e in log.entries]),
                        facts))
    return log, dx


def decision_case(case_id, env, rules, spec, policy, chooser="R"):
    log, dx = decision(spec, policy, chooser)
    return {"id": case_id, "kind": "risk-decision", "environment": env, "document": {"norms": rules},
            "decision": dx, "entries": log.entries[:-1]}


def witness_model(env, spec, chooser="r"):
    """The decision model of a record (risk.md 4.4) as a finite structure over E_risk's base vocabulary."""
    from tests.test_risk_fixtures import closure
    vocab, risk = env["vocabulary"], env["risk"]
    actions = spec["actions"]
    relations = {p: [] for p, d in vocab["predicates"].items() if "regulated" not in d}
    relations.update({
        "available": [[a, chooser] for a in actions],
        "inaction": [["nothing"]] if "nothing" in actions else [],
        "leads_to": [[a, h] for (a, h), c in spec["cells"].items() if c == "leads"],
        "risk__might_lead_to": [[a, h] for (a, h), c in spec["cells"].items() if c in ("leads", "might")],
        "risk__class": [list(p) for p in risk["harm_classes"]],
        "risk__more_severe": [list(p) for p in closure(risk["severity"]["more_severe"])],
    })
    for p, args in base_facts(chooser):
        relations[p].append(list(args))
    for name in FACT_PREDICATES:
        relations[name] += [list(row) for row in spec["facts"][name]]
    classes = risk["severity"]["classes"]
    domains = {"robot": [chooser], "action": list(actions), "harm": list(HARMS), risk["severity"]["sort"]: classes}
    constants = {c: c for c in classes} | {h: h for h in HARMS}
    return {"complete": True, "domains": domains, "constants": constants, "relations": relations}
