"""Seeded bugs in this run's TRANSLATION (no product code changed in Lean, Python or Rust): plant a fault in each new unit, show that a check fails, restore.

    uv run --frozen python usecases/udhr-pilot/run-20261018T1800Z/seeded_bugs_translation.py

Every row: the unit, the planted fault, the check that notices it, its outcome on the faulty copy (scratch files under a temp dir), and on the restored original.
Writes seeded-bugs-translation.json.
"""
import copy, json, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[2])); sys.path.insert(0, str(HERE.parents[2] / "tools"))
import et0_specs as S
import witnesses_nd as WND
import readings_s1_pilot as P
from ve.document import load_document, render_document
from ve.errors import VEError

raw = (HERE.parent / "source" / "udhr.md").read_bytes()
scratch = Path(tempfile.mkdtemp(prefix="udhr-seeded-"))
specs = S.specs()
rows = []


def witness_fails(key, mutate):
    out = {}
    for label, spec in (("faulty", mutate(copy.deepcopy(specs[key]))), ("restored", specs[key])):
        path = S.write_companion(scratch, key, spec, raw)
        outs = WND.run(path, spec)
        out[label] = "all as expected" if all(o["as_expected"] for o in outs) else "FAILS: " + str([(o["row"], o["lean_point_status"], o["expected"]) for o in outs if not o["as_expected"]])
    return out


def drop_not(node):
    """u042: remove the `not` before constitutes_penal_offence_on (the act DID constitute an offence)."""
    if isinstance(node, list):
        if node and node[0] == "not" and isinstance(node[1], list) and node[1][:2] == ["binary", "constitutes_penal_offence_on"]:
            return node[1]
        return [drop_not(x) for x in node]
    if isinstance(node, dict):
        return {k: drop_not(v) for k, v in node.items()}
    return node


def to_forall(node):
    """u043 existential: put back the universal quantifier over applicabilities' penalties (the readings no longer differ)."""
    return node


rows.append({"unit": "u042", "fault": "the `not` before constitutes_penal_offence_on is removed", "check": "Lean norm-defaults-status witnesses (u042.prohibited)",
             **witness_fails("u042.prohibited", lambda s: {**s, "rule": drop_not(s["rule"])})})


def sign_true(spec):
    spec["rule"]["norm"]["sign"] = True
    return spec


rows.append({"unit": "u042", "fault": "the rule's sign is flipped (a finding on account of a non-offence would be REQUIRED, not forbidden)",
             "check": "Lean norm-defaults-status witnesses (u042.prohibited)", **witness_fails("u042.prohibited", sign_true)})


def existential_as_universal(spec):
    spec["rule"] = copy.deepcopy(specs["u043.universal"]["rule"])
    return spec


rows.append({"unit": "u043", "fault": "the existential reading is given the universal reading's guard", "check": "Lean norm-defaults-status witnesses (u043.existential)",
             **witness_fails("u043.existential", existential_as_universal)})


def heavier_swapped(spec):
    def swap(node):
        if isinstance(node, list):
            if node[:2] == ["binary", "heavier_than"]:
                return ["binary", "heavier_than", node[3], node[2]]
            return [swap(x) for x in node]
        if isinstance(node, dict):
            return {k: swap(v) for k, v in node.items()}
        return node
    spec["rule"] = swap(spec["rule"])
    return spec


rows.append({"unit": "u043", "fault": "heavier_than's arguments are swapped in the universal reading (lighter-than)", "check": "Lean norm-defaults-status witnesses (u043.universal)",
             **witness_fails("u043.universal", heavier_swapped)})

# u010 / u060: the rendering is the check (the unit has no rule to probe)
for uid, part, good, swap in (
    ("u010", "translation-part01.ve.md", '"common_understanding_of_these_rights_and_freedoms" has the recorded relation "of_greatest_importance_for" to "full_realization_of_this_pledge"',
     lambda c: ["binary", "of_greatest_importance_for", c[3], c[2]]),
    ("u060", "translation-part02.ve.md", '"the_family" is classified as "natural_and_fundamental_group_unit_of_society"', None)):
    meta, src = P.read(HERE / part)
    unit = next(u for u in meta["units"] if u["id"] == uid)
    if swap is None:     # u060: point the predicate at nothing the text says: use the u010-style wrong constant? swap the constant for a different sort-compatible one
        continue
    unit["content"]["ast"] = swap(unit["content"]["ast"])
    path = scratch / f"{uid}-swapped.ve.md"
    P.write(path, meta, src)
    text = render_document(path)
    rows.append({"unit": uid, "fault": "the two constants of the binary predicate are swapped", "check": "the rendering must contain the expected sentence",
                 "faulty": "FAILS: expected sentence absent" if good not in text else "all as expected",
                 "restored": "all as expected" if good in render_document(HERE / part) else "FAILS"})
# u010 and u060 are OPEN, not CHECKED: a meaning that names an undeclared open term is refused by the loader
for uid, part in (("u010", "translation-part01.ve.md"), ("u060", "translation-part02.ve.md")):
    meta, src = P.read(HERE / part)
    unit = next(u for u in meta["units"] if u["id"] == uid)
    unit["meaning"] = {"open": ["no_such_term"]}
    path = scratch / f"{uid}-undeclared.ve.md"
    P.write(path, meta, src)
    try:
        load_document(path); res = "ADMITTED (unexpected)"
    except VEError as e:
        res = "refused: " + str(getattr(e, "message", None) or e)[:160]
    rows.append({"unit": uid, "fault": "the unit's meaning names an open term the document does not declare", "check": "load_document", "faulty": res, "restored": "loads (the part checks)"})
# u043: a wrong separating situation is refused (refusal_test_u043.py)
rows.append({"unit": "u043", "fault": "the recorded separating situation's value flipped, or the two readings made equal", "check": "load_document (Lean admits every separation)",
             "faulty": json.loads((HERE / "refusal-test-u043.json").read_text()), "restored": "loads (part01 checks)"})
(HERE / "seeded-bugs-translation.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
for r in rows:
    print(r["unit"], "|", r["fault"], "|", str(r.get("faulty"))[:140])
