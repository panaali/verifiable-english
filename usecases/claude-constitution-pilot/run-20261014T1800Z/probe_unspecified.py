#!/usr/bin/env python3
"""Ask VE what the unspecified-completion translation says, on small situations. Writes probes/unspecified-probe.json.

Reads readings/all-strict.ve.md (every norm of the main translation plus every force-ambiguous unit resolved to its strict
reading, under norm-defaults@0) and asks, with VE's own norm-defaults route (docs/spec/norm-defaults.md 2.5, 3.1):

* the status of each regulated predicate at a one-element situation where the case atom holds, and where it does not
  (SETTLED yes/no, or UNDECIDED: the text does not say);
* whether the operator rules conflict (a checked witness, or the failure to find one);
* which predicates have a reachable gap (the text is silent in some situation).

Nothing here reads the answer from the source: the situations are chosen by this script, the verdicts are VE's.

Run 20261008T0600Z: ported to the Lean-owned route. ve-green-lf-10b deleted the Python `UnspecifiedDocument.status`,
`check_conflict` and per-line `report`; a point status is now Lean's `norm-defaults-status` row (`point_status`), the gap lines are
the `report` of Lean's `norm-defaults-report` row, and a conflict verdict is Lean's `norm-defaults-conflict` row on evidence the
frozen Python oracle (conformance/frozen_norm_defaults.py) proposes, as conformance does. The output file keeps the previous shape.
"""
from __future__ import annotations

import json
import sys
from itertools import product
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))

from conformance import frozen_norm_defaults as fnd  # noqa: E402  (evidence PROPOSER only; Lean replays every proposal)
from ve import norm_defaults as nd  # noqa: E402
from ve.norm_defaults_route import run_case, source_case  # noqa: E402
from ve.document import load_document  # noqa: E402
from ve.model import FiniteModel  # noqa: E402
import s03_scope as sc  # noqa: E402
import spec_nd  # noqa: E402

# run 20261014T1800Z (AT-0p): the guard of hard constraint i is ( C_i(s) and knowingly_engages_i(c, s) ) or thinks_quite_likely_i(c, s),
# two binary open terms on (claude_instance, situation) per rule; u0173.s01's first and second alternatives


def situation(document, true_atoms=()):
    env = document.situation_environment()
    domains = {s: [s + "0"] for s in env.model_sorts}
    consts = {c: env.constants[c].sort + "0" for c in env.constants}
    relations = {p: [] for p in env.predicates}
    for atom in true_atoms:
        relations[atom] = [[s + "0" for s in env.predicates[atom].arguments]]
    return FiniteModel.from_dict(env, {"complete": True, "domains": domains, "constants": consts, "relations": relations})


def situation2(document, true_tuples, sizes):
    """A situation with `sizes[sort]` elements (sort0, sort1, ...) and the given true tuples {atom: [[element, ...], ...]}."""
    env = document.situation_environment()
    domains = {s: [f"{s}{k}" for k in range(sizes.get(s, 1))] for s in env.model_sorts}
    consts = {c: env.constants[c].sort + "0" for c in env.constants}
    relations = {p: [] for p in env.predicates}
    for atom, tuples in true_tuples.items():
        relations[atom] = [list(t) for t in tuples]
    return FiniteModel.from_dict(env, {"complete": True, "domains": domains, "constants": consts, "relations": relations})


def main():
    doc = load_document(RUN / "readings/all-strict.ve.md")["norm_defaults"]
    env = doc.env
    fdoc = fnd.UnspecifiedDocument(doc.env, doc.author.rules)
    out = {"document": "readings/all-strict.ve.md", "points": [], "conflict": {}, "gaps": {}}

    def point(label, predicate, atoms, model=None, values=None, doc=doc, env=env, fdoc=fdoc, key="points"):
        model = model or situation(doc, atoms)
        sorts = env.predicates[predicate].arguments
        values = values or [x + "0" for x in sorts]
        case = source_case(doc, "norm-defaults-status", model=model.to_dict(), predicate=predicate, tuple=values, method="enumerate")
        row = run_case(case)
        if row["point_status"] == "UNKNOWN":  # the tables of "the text does not say": every unsaid atom true, then every one false
            yes = {item["name"]: [list(v) for v in product(*(model.to_dict()["domains"][x] for x in item["sorts"]))]
                   for item in doc.elaboration["unsaid"]}
            no = {item["name"]: [] for item in doc.elaboration["unsaid"]}
            row = run_case({**case, "method": "undecided", "yes": yes, "no": no})
        text = row["point_status"]
        if predicate == "operator_input_permitted":  # the point status does not show a rule conflict; ask for one
            report = fnd.check_conflict(fdoc, model=model.to_dict())
            if report.status == "CONFLICT" and report.target == predicate:
                text = f"CONFLICT ({report.kind}: permitted by one rule, forbidden by another)"
        out.setdefault(key, []).append({"label": label, "predicate": predicate, "true_atoms": sorted(atoms), "status": text,
                                        "rules": row.get("rules"), "differs": row.get("differs")})
        return row

    for n, (unit, rule, pred, term, _act, _words) in enumerate(spec_nd.HARD):
        # four points per rule (AT-0p; the atoms are one-element situations, so c and s are the only instance and situation)
        i = n + 1
        c, k, t = term, f"knowingly_engages_{i}", f"thinks_quite_likely_{i}"
        if unit == sc.UNIT:  # the category is three atoms; the wide companion (readings/all-strict.ve.md) carries the wide reading
            c = [sc.CYBERWEAPON, sc.DAMAGE]  # a case under both readings
        point(f"{unit}: the case does not hold, Claude thinks it quite likely that the action falls into the category", pred, [t])
        point(f"{unit}: the case holds, Claude knowingly and intentionally engages in it", pred, [*([c] if isinstance(c, str) else c), k])
        point(f"{unit}: neither (an unclear, uncertain or unknowing case)", pred, [])
        point(f"{unit}: the case does not hold, Claude knowingly and intentionally engages in it", pred, [k])
    for label, pred, atoms in [
        ("u0156.s03: any situation", "system_prompt_deception_permitted", []),
        ("u0125.s04.p2: any situation", "denial_of_being_claude_permitted", []),
        ("u0052.s01: any situation (added in run 20261008T0600Z: the unit is now one strict reading)", "judgment_use_required", []),
        ("u0123.s01: a dishonest-looking instruction within the honesty principles", "operator_input_permitted",
         ["instruction_dishonest_looking_within_honesty"]),
        ("u0062.s01: input is a persona", "operator_input_permitted", ["input_is_persona"]),
        ("u0062.s01: input is none of the three", "operator_input_permitted", []),
        ("u0062.s01: input is specific instructions", "operator_input_permitted", ["input_is_specific_instructions"]),
        ("u0062.s01 and u0123.s03: a persona that also is an instruction to claim to be human", "operator_input_permitted",
         ["input_is_persona", "instruction_claim_human_when_asked"]),
        ("u0062.s01 and u0123.s03: specific instructions that also endanger health or safety", "operator_input_permitted",
         ["input_is_specific_instructions", "instruction_endanger_health_or_safety"]),
        ("u0123.s01 and u0123.s03: a dishonest-looking instruction that also acts against the guidelines", "operator_input_permitted",
         ["instruction_dishonest_looking_within_honesty", "instruction_act_against_guidelines"]),
        ("u0123.s02: persona role-play instruction", "operator_input_permitted", ["instruction_role_play_custom_persona"]),
        ("u0123.s03: instruction to claim to be human", "operator_input_permitted", ["instruction_claim_human_when_asked"]),
        ("u0123.s02 and u0123.s03: a role-play instruction that also claims to be human", "operator_input_permitted",
         ["instruction_role_play_custom_persona", "instruction_claim_human_when_asked"]),
        ("u0036.s05: genuine ambiguity", "clarification_required", ["genuine_ambiguity"]),
        ("u0036.s05: no genuine ambiguity", "clarification_required", []),
        ("u0073.s05: the case holds", "system_prompt_compliance_required", ["operator_prompt_addresses_case"]),
        ("u0073.s05: the case does not hold", "system_prompt_compliance_required", []),
        ("u0073.s05: the case holds but complying is unsafe", "system_prompt_compliance_required",
         ["operator_prompt_addresses_case", "compliance_unsafe"]),
        ("u0073.s05: the case holds and the “generally” exception applies", "system_prompt_compliance_required",
         ["operator_prompt_addresses_case", "general_exception_to_complying"]),
        ("u0168.s01: the case holds", "firmness_required", ["seemingly_compelling_argument_to_cross_line"]),
        ("u0168.s01: the case does not hold", "firmness_required", []),
    ]:
        point(label, pred, atoms)

    # u0165.s03: the two attachments of “that could cause significant damage if deployed”, each on its own companion (wide: readings/all-strict.ve.md)
    k3, t3 = sc.KNOWING, sc.THINKING
    for reading, path in (("wide", "readings/all-strict.ve.md"), ("narrow", "readings/all-strict-narrow.ve.md")):
        d2 = load_document(RUN / path)["norm_defaults"]
        f2 = fnd.UnspecifiedDocument(d2.env, d2.author.rules)
        for label, atoms in [("a cyberweapon that could not cause significant damage, knowingly created", [sc.CYBERWEAPON, k3]),
                             ("malicious code that could not cause significant damage, knowingly created", [sc.MALICIOUS_CODE, k3]),
                             ("malicious code that could cause significant damage, knowingly created", [sc.MALICIOUS_CODE, sc.DAMAGE, k3]),
                             ("a cyberweapon that could cause significant damage, knowingly created", [sc.CYBERWEAPON, sc.DAMAGE, k3]),
                             ("nothing holds", [])]:
            point(f"u0165.s03, {reading} reading: {label}", "cyberweapon_creation_permitted", atoms, doc=d2, env=d2.env, fdoc=f2, key="scope_points")
    # u0123.s02.p1: the operator's own products. Two operators; operator0 gave the input, which promotes its own products.
    sizes = {"operator": 2}
    for label, who in [("the operator who gave the instruction to promote its own products", "operator0"),
                       ("another operator, for the same input", "operator1")]:
        m = situation2(doc, {"instruction_promote_own_products": [["operator0", "operator_input0"]]}, sizes)
        point(f"u0123.s02.p1: {label}", "operator_input_permitted", ["instruction_promote_own_products(operator0, operator_input0)"],
              model=m, values=[who, "operator_input0"], key="binding_points")

    # conflicts: a witness situation for the operator rules, then the whole document
    for label, atoms in [("a role-play instruction that also claims to be human",
                          ["instruction_role_play_custom_persona", "instruction_claim_human_when_asked"]),
                         ("a persona that also is an instruction to claim to be human",
                          ["input_is_persona", "instruction_claim_human_when_asked"]),
                         ("no atom true", [])]:
        report = fnd.check_conflict(fdoc, model=situation(doc, atoms).to_dict())
        out["conflict"][label] = {"status": report.status, "target": report.target, "kind": report.kind,
                                  "tuple": list(report.tuple)}
    proof = fnd.check_conflict(fdoc, prove=True)
    lean = run_case(source_case(doc, "norm-defaults-conflict", packages=dict(proof.certificates)))
    out["conflict"]["whole document, proof attempt"] = {"status": lean.get("verdict"), "detail": "", "oracle_status": proof.status,
                                                         "lean_row_keys": sorted(lean)}

    for line in nd.report(doc, prove=True, search_domain_size=2)["report"]:
        out["gaps"][line["predicate"]] = {"completion": line["completion"], "reached": line["reached"],
                                          "inherits_from": list(line["inherits_from"])}
    (RUN / "probes").mkdir(exist_ok=True)
    (RUN / "probes/unspecified-probe.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    for p in out["points"]:
        print(f"{p['status']:60} {p['label']}")
    for key in ("scope_points", "binding_points"):
        for p in out[key]:
            print(f"{p['status']:60} {p['label']}")
    print(json.dumps(out["conflict"], indent=1))
    print({k: v["reached"] for k, v in out["gaps"].items()})


if __name__ == "__main__":
    main()
