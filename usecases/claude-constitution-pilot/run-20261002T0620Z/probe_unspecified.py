#!/usr/bin/env python3
"""Ask VE what the unspecified-completion translation says, on small situations. Writes probes/unspecified-probe.json.

Reads readings/all-strict.ve.md (every norm of the main translation plus every force-ambiguous unit resolved to its strict
reading, under norm-defaults@0) and asks, with VE's own norm-defaults route (docs/spec/norm-defaults.md 2.5, 3.1):

* the status of each regulated predicate at a one-element situation where the case atom holds, and where it does not
  (SETTLED yes/no, or UNDECIDED: the text does not say);
* whether the operator rules conflict (a checked witness, or the failure to find one);
* which predicates have a reachable gap (the text is silent in some situation).

Nothing here reads the answer from the source: the situations are chosen by this script, the verdicts are VE's.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))

from ve import norm_defaults as nd  # noqa: E402
from ve.document import load_document  # noqa: E402
from ve.model import FiniteModel  # noqa: E402
import spec_nd  # noqa: E402


def status_text(s):
    return "SETTLED " + ("yes" if s.value else "no") if s.status == "SETTLED" else s.status


def situation(document, true_atoms=()):
    env = document.situation_environment()
    domains = {s: [s + "0"] for s in env.model_sorts}
    consts = {c: env.constants[c].sort + "0" for c in env.constants}
    relations = {p: [] for p in env.predicates}
    for atom in true_atoms:
        relations[atom] = [[s + "0" for s in env.predicates[atom].arguments]]
    return FiniteModel.from_dict(env, {"complete": True, "domains": domains, "constants": consts, "relations": relations})


def main():
    doc = load_document(RUN / "readings/all-strict.ve.md")["norm_defaults"]
    env = doc.env
    out = {"document": "readings/all-strict.ve.md", "points": [], "conflict": {}, "gaps": {}}

    def point(label, predicate, atoms):
        model = situation(doc, atoms)
        sorts = env.predicates[predicate].arguments
        s = doc.status(model, predicate, tuple(x + "0" for x in sorts))
        text = status_text(s)
        if predicate == "operator_input_permitted":  # the point status does not show a rule conflict; ask for one
            report = nd.check_conflict(doc, model=model.to_dict())
            if report.status == "CONFLICT" and report.target == predicate:
                text = f"CONFLICT ({report.kind}: permitted by one rule, forbidden by another)"
        out["points"].append({"label": label, "predicate": predicate, "true_atoms": sorted(atoms), "status": text,
                              "evidence": s.evidence})
        return s

    for unit, rule, pred, term, _act, _words in spec_nd.HARD:
        point(f"{unit}: the case holds", pred, [term])
        point(f"{unit}: the case does not hold", pred, [])
    for label, pred, atoms in [
        ("u0156.s03: any situation", "system_prompt_deception_permitted", []),
        ("u0125.s04.p2: any situation", "denial_of_being_claude_permitted", []),
        ("u0166.s04: operator unlocking", "operator_unlock_permitted", []),
        ("u0166.s04: user unlocking", "user_unlock_permitted", []),
        ("u0123.s01: a dishonest-looking instruction within the honesty principles", "operator_input_permitted",
         ["instruction_dishonest_looking_within_honesty"]),
        ("u0062.s01: input is a persona", "operator_input_permitted", ["input_is_persona"]),
        ("u0062.s01: input is none of the three", "operator_input_permitted", []),
        ("u0123.s02: persona role-play instruction", "operator_input_permitted", ["instruction_role_play_custom_persona"]),
        ("u0123.s03: instruction to claim to be human", "operator_input_permitted", ["instruction_claim_human_when_asked"]),
        ("u0123.s02 and u0123.s03: a role-play instruction that also claims to be human", "operator_input_permitted",
         ["instruction_role_play_custom_persona", "instruction_claim_human_when_asked"]),
        ("u0036.s05: genuine ambiguity", "clarification_required", ["genuine_ambiguity"]),
        ("u0036.s05: no genuine ambiguity", "clarification_required", []),
    ]:
        point(label, pred, atoms)

    # conflicts: a witness situation for the operator rules, then the whole document
    for label, atoms in [("a role-play instruction that also claims to be human",
                          ["instruction_role_play_custom_persona", "instruction_claim_human_when_asked"]),
                         ("no atom true", [])]:
        report = nd.check_conflict(doc, model=situation(doc, atoms).to_dict())
        out["conflict"][label] = {"status": report.status, "target": report.target, "kind": report.kind,
                                  "tuple": list(report.tuple)}
    proof = nd.check_conflict(doc, prove=True)
    out["conflict"]["whole document, proof attempt"] = {"status": proof.status, "detail": proof.detail}

    for line in nd.report(doc, prove=True, search_domain_size=2):
        out["gaps"][line.predicate] = {"completion": line.completion, "reached": line.reached,
                                       "inherits_from": list(line.inherits_from)}
    (RUN / "probes").mkdir(exist_ok=True)
    (RUN / "probes/unspecified-probe.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    for p in out["points"]:
        print(f"{p['status']:60} {p['label']}")
    print(json.dumps(out["conflict"], indent=1))
    print({k: v["reached"] for k, v in out["gaps"].items()})


if __name__ == "__main__":
    main()
