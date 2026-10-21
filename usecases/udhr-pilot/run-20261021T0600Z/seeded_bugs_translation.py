"""Seeded bugs in this run's TRANSLATION (no product code changed in Lean, Python or Rust): plant a fault in each unit this run touched or carries
from JT-0p, show that a check fails, restore.

    uv run --frozen python usecases/udhr-pilot/run-20261021T0600Z/seeded_bugs_translation.py

Every row: the unit, the planted fault, the check that notices it, its outcome on the faulty copy (scratch files under a temp dir), and on the restored original.
Writes seeded-bugs-translation.json.  (u042 and u043 are UNFORMALISED again, so their rows are gone.)
"""
import copy, json, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[2])); sys.path.insert(0, str(HERE.parents[2] / "tools"))
import u061_specs as S
import udhr_specs as U
import witnesses_nd as WND
import readings_s1_pilot as P
from ve.document import load_document, render_document
from ve.errors import VEError

raw = (HERE.parent / "source" / "udhr.md").read_bytes()
scratch = Path(tempfile.mkdtemp(prefix="udhr-seeded-"))
legacy, _ = P.read(HERE / "translation.ve.md")
a, b = next(u for u in legacy["units"] if u["id"] == "u061")["span"]
rows = []


def witness_fails(mutate):
    out = {}
    for label, spec in (("faulty", mutate(copy.deepcopy(S.SPEC))), ("restored", S.SPEC)):
        (scratch / label).mkdir(exist_ok=True)
        path = U.write_companion(scratch / label, "u061", "entitlement", spec, raw[a:b], legacy["open_terms"])
        outs = WND.run(path, spec)
        out[label] = "all as expected" if all(o["as_expected"] for o in outs) else "FAILS: " + str([(o["row"], o["lean_point_status"], o["expected"]) for o in outs if not o["as_expected"]])
    return out


def guard_top(spec):
    spec["rule"]["norm"]["guard"] = ["top"]      # every thing, not only the family, would be entitled
    return spec


def sign_off(spec):
    spec["rule"]["norm"]["sign"] = False         # the entitlement turned into its denial
    return spec


rows.append({"unit": "u061", "fault": "the rule's guard is dropped (every thing, not only the family, would be entitled)",
             "check": "Lean norm-defaults-status witnesses (u061.entitlement)", **witness_fails(guard_top)})
rows.append({"unit": "u061", "fault": "the rule's sign is flipped (the entitlement becomes its denial)",
             "check": "Lean norm-defaults-status witnesses (u061.entitlement)", **witness_fails(sign_off)})


def render_check(uid, part, good, mutate, fault):
    meta, src = P.read(HERE / part)
    unit = next(u for u in meta["units"] if u["id"] == uid)
    mutate(unit)
    path = scratch / f"{uid}-{abs(hash(fault)) % 1000}.ve.md"
    P.write(path, meta, src)
    try:
        text = render_document(path)
        faulty = "FAILS: expected sentence absent" if good not in text else "all as expected"
    except VEError as e:
        faulty = "refused by the loader: " + str(getattr(e, "message", None) or e)[:120]
    rows.append({"unit": uid, "fault": fault, "check": "the rendering must contain the expected sentence (or the loader must refuse)",
                 "faulty": faulty,
                 "restored": "all as expected" if good in render_document(HERE / part) else "FAILS"})


def swap_ast(unit):      # u010: the two constants swapped
    c = unit["content"]["ast"]
    unit["content"]["ast"] = ["binary", "of_greatest_importance_for", c[3], c[2]]


render_check("u010", "translation-part01.ve.md",
             '"common_understanding_of_these_rights_and_freedoms" has the recorded relation "of_greatest_importance_for" to "full_realization_of_this_pledge"',
             swap_ast, "the two constants of the binary predicate are swapped")


def drop_uniqueness(unit):      # u060: only the first conjunct
    unit["content"]["ast"] = unit["content"]["ast"][1]


render_check("u060", "translation-part02.ve.md", 'that thing is the same as "the_family"', drop_uniqueness,
             "the uniqueness conjunct is dropped (the unit says only that the family is a natural and fundamental group unit)")


def other_constant(unit):       # u060: the uniqueness names a different thing
    unit["content"]["ast"][2][2][2][2] = ["const", "common_understanding_of_these_rights_and_freedoms"]


render_check("u060", "translation-part02.ve.md", 'that thing is the same as "the_family"', other_constant,
             "the uniqueness conjunct names another constant than the family")


def other_subject(unit):        # u061: the entitlement of another thing
    unit["content"]["ast"][2] = ["const", "common_understanding_of_these_rights_and_freedoms"]


render_check("u061", "translation-part02.ve.md", '"the_family" is classified as "is_entitled_to_protection_by_society_and_the_state"', other_subject,
             "the entitlement is given to another thing than the family (the subject u060 names)")

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
(HERE / "seeded-bugs-translation.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
for r in rows:
    print(r["unit"], "|", r["fault"], "|", str(r.get("faulty"))[:140], "|", str(r.get("restored"))[:40])
