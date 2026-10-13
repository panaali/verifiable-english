"""QT-0p: pilot repair with the existing language (quantities plan, section 4, QT-0p).

No product code. Builds, from the pinned pilot runs (read only):

1. Constitution, u0042.presupposition (38 B) and u0043.s02 (90 B), in `relational-fol@0`:
   - the heading's presupposed claim "Claude has three types of principals" as "exactly three", with no names;
   - u0043.s02 as a MIXED unit: "At the moment, " LABELLED (the document's present, no date, no second
     indexical: edit 9), and the rest CHECKED: the three facts, pairwise distinctness and closure.
2. UDHR, u097 (76 B): a bearer-less duty (as u098) guarded by the stage, `norm-defaults@0` with completion
   `unspecified`, so stages other than elementary and fundamental are "the text does not say"; "free" is an
   open term, as "compulsory" is in u098.

Each repair is checked twice: as a small companion document over exactly the units' source bytes, and spliced
into a copy of the pilot's own translation (constitution `translation.ve.md`; UDHR `translation-part03.ve.md`),
with `ve document check` and `ve document coverage` on main. Probes: "Is there a fourth type of principal?"
(expected SETTLED no) and "Must higher education be free under this sentence?" (expected UNDECIDED).
Outputs go to docs/research/evidence/quantities/qt0p/; the spliced copies to research/quantities/out/ (not
committed; their SHA-256 is recorded).
"""
from __future__ import annotations

import copy
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (CONSTITUTION_RUN, EVIDENCE, MAIN, REPO, UDHR_RUN, main_head, run_ve, sha256, split_document,
                    ve_python, write_document, write_json)

OUT = EVIDENCE / "qt0p"
WORK = REPO / "research" / "quantities" / "out" / "qt0p"

# ---------------------------------------------------------------- constitution

C_SPAN = (23448, 23677)          # u0042.presupposition, u0043.s01, u0043.s02
C_LABEL = "At the moment, "     # the LABELLED part of u0043.s02

C_SORTS = {"principal_type": {
    "description": "A type of principal, in the source's sense (u0042, u0043): a kind of party whose instructions "
                   "Claude gives weight to.",
    "verbalisation": {"singular": "type of principal", "plural": "types of principals"}}}
C_CONSTANTS = {
    "anthropic": {"sort": "principal_type", "description": "Anthropic, as a type of principal (u0043.s02)."},
    "operators": {"sort": "principal_type", "description": "Operators, as a type of principal (u0043.s02)."},
    "users": {"sort": "principal_type", "description": "Users, as a type of principal (u0043.s02)."},
}
C_PREDICATES = {"claude_principal_type": {
    "arguments": ["principal_type"], "description": "The type of principal is one of Claude's types of principals.",
    "verbalisation": "{0} is one of Claude's types of principals",
    "negative_verbalisation": "{0} is not one of Claude's types of principals"}}


def v(i):
    return ["var", i]


def c(name):
    return ["const", name]


def cpt(term):
    return ["unary", "claude_principal_type", term]


def neq(a, b):
    return ["not", ["eq", a, b]]


def conj(*items):
    out = items[-1]
    for item in reversed(items[:-1]):
        out = ["and", item, out]
    return out


def disj(*items):
    out = items[-1]
    for item in reversed(items[:-1]):
        out = ["or", item, out]
    return out


# "Claude has three types of principals": there are x, y, z, pairwise different, each one of Claude's types, and
# every one of Claude's types is one of them. No names: the heading does not name them.
PRESUPPOSITION = ["exists", "principal_type", ["exists", "principal_type", ["exists", "principal_type", conj(
    cpt(v(2)), cpt(v(1)), cpt(v(0)), neq(v(2), v(1)), neq(v(2), v(0)), neq(v(1), v(0)),
    ["forall", "principal_type", ["implies", cpt(v(0)), disj(["eq", v(0), v(3)], ["eq", v(0), v(2)],
                                                              ["eq", v(0), v(1)])]])]]]

# "Claude's three types of principals are Anthropic, operators, and users."
NAMES = [c("anthropic"), c("operators"), c("users")]
THREE = conj(
    cpt(NAMES[0]), cpt(NAMES[1]), cpt(NAMES[2]),
    neq(NAMES[0], NAMES[1]), neq(NAMES[0], NAMES[2]), neq(NAMES[1], NAMES[2]),
    ["forall", "principal_type", ["implies", cpt(v(0)), disj(*(["eq", v(0), n] for n in NAMES))]])

# Probe "Is there a fourth type of principal?": SETTLED no means the negation follows (ALL) and the question's
# positive form is refuted (NONE).
FOURTH = ["exists", "principal_type", conj(cpt(v(0)), *(neq(v(0), n) for n in NAMES))]
NO_FOURTH = ["not", FOURTH]
# Control: "Anthropic is one of Claude's types of principals" follows from u0043.s02's facts.
ANTHROPIC_IS_ONE = cpt(c("anthropic"))


def constitution_units(base: int) -> list[dict]:
    """The three source units over [C_SPAN), spans relative to `base`."""
    a, b = C_SPAN
    pres = (23448, 23486)
    s01 = (23486, 23587)
    s02 = (23587, 23677)
    label_end = s02[0] + len(C_LABEL.encode())
    r = lambda lo, hi: [lo - base, hi - base]
    return [
        {"id": "u0042.presupposition", "span": r(*pres), "support": "assumption", "kind": "asserted",
         "meaning": "specified", "content": {"ast": PRESUPPOSITION}},
        {"id": "u0043.s01", "span": r(*s01), "support": "none", "kind": ["unformalised", "counting"],
         "meaning": {"unformalised": "counting"}},
        {"id": "u0043.s02", "span": r(*s02), "status": "MIXED", "parts": [
            {"id": "u0043.s02.p1", "span": r(s02[0], label_end), "status": "LABELLED", "support": "none",
             "kind": "meta", "meaning": "specified"},
            {"id": "u0043.s02.p2", "span": r(label_end, s02[1]), "status": "CHECKED", "support": "assumption",
             "kind": "asserted", "meaning": "specified", "content": {"ast": THREE}},
        ]},
    ]


def constitution_vocabulary(vocab: dict) -> dict:
    vocab = copy.deepcopy(vocab)
    for key, extra in (("sorts", C_SORTS), ("constants", C_CONSTANTS), ("predicates", C_PREDICATES)):
        clash = set(vocab.setdefault(key, {})) & set(extra)
        assert not clash, clash
        vocab[key].update(extra)
    return vocab


def constitution_companion() -> Path:
    meta, body = split_document(CONSTITUTION_RUN / "translation.ve.md")
    source = (CONSTITUTION_RUN.parent / "source" / "claude-constitution.md").read_bytes()
    assert body[C_SPAN[0]:C_SPAN[1]] == source[C_SPAN[0]:C_SPAN[1]]
    units = constitution_units(C_SPAN[0])
    env = {"language": meta["environment"]["language"], "spec_revision": meta["environment"]["spec_revision"],
           "profiles": ["documents@1", "norms@0", "readings@1", "relational-fol@0"],
           "vocabulary": constitution_vocabulary({"sorts": {}, "constants": {}, "predicates": {}})}
    doc = {"format": "ve-document@1", "environment": env, "units": units}
    path = OUT / "constitution-u0042-u0043.ve.md"
    write_document(path, doc, source[C_SPAN[0]:C_SPAN[1]])
    return path


def constitution_rebuild(repaired: bool) -> dict:
    """Re-run the pilot's own rebuild (`nd.py all`) on a work copy, with or without the repair.

    The repair adds vocabulary, so the environment id changes and every reading-set identity and situation must be
    recomputed: that is `nd.py`'s job in the pilot (it reads `translation-without-content.ve.md` and
    `readings/all-strict.ve.md`). The pilot's scripts and inputs are copied, never edited in place; `nd.py` imports
    `tools/readings_s1_pilot.py` from its repository root, which here is a copy of main's.
    """
    tag = "repaired" if repaired else "baseline"
    root = WORK / f"constitution-{tag}"
    run = root / "usecases" / "claude-constitution-pilot" / CONSTITUTION_RUN.name
    (run / "readings").mkdir(parents=True, exist_ok=True)
    (root / "tools").mkdir(parents=True, exist_ok=True)
    (root / "tools" / "readings_s1_pilot.py").write_bytes((MAIN / "tools" / "readings_s1_pilot.py").read_bytes())
    for name in ("nd.py", "spec_nd.py", "spec.py"):
        (run / name).write_bytes((CONSTITUTION_RUN / name).read_bytes())
    (run / "readings" / "all-strict.ve.md").write_bytes((CONSTITUTION_RUN / "readings" / "all-strict.ve.md").read_bytes())
    meta, body = split_document(CONSTITUTION_RUN / "translation-without-content.ve.md")
    if repaired:
        meta = copy.deepcopy(meta)
        meta["environment"]["vocabulary"] = constitution_vocabulary(meta["environment"]["vocabulary"])
        new = {u["id"]: u for u in constitution_units(0)}
        replaced = 0
        for i, unit in enumerate(meta["units"]):
            if unit["id"] in new:
                assert unit.get("kind") == ["unformalised", "counting"], unit
                meta["units"][i] = new[unit["id"]]
                replaced += 1
        assert replaced == 3, replaced
    write_document(run / "translation-without-content.ve.md", meta, body)
    proc = ve_python(["-B", str(run / "nd.py"), "all"])
    (OUT / f"c-{tag}-nd.out").write_text(proc.stdout)
    if proc.stderr:
        (OUT / f"c-{tag}-nd.err").write_text(proc.stderr[-20000:])
    result_path = run / "readings" / "nd-all-result.json"
    result = json.loads(result_path.read_text()) if result_path.exists() else None
    if result is not None:
        write_json(OUT / f"c-{tag}-nd-result.json", {k: v for k, v in result.items() if k != "readings"})
    return {"returncode": proc.returncode, "document": run / "readings" / "nd-all.ve.md", "result": result}


# ---------------------------------------------------------------- UDHR

U097_SPAN_PART03 = (2284, 2360)
U097_SOURCE = "Education shall be free, at least in the elementary and fundamental stages. "  # the unit's 76 B
U097_PREDICATES = {
    "education_free_required": {
        "arguments": ["education_kind"], "description": "The education is required to be free",
        "regulated": {"act": "{0} be free", "default": "unspecified", "role": "obligation"}},
    "is_fundamental": {"arguments": ["education_kind"], "description": "The education is fundamental",
                       "verbalisation": "{0} is fundamental"},
}
U097_OPEN = {"arguments": [], "decided_by": "unstated", "factors": ["what it is for education to be free"],
             "jurisdiction": "universal", "name": "free_education", "necessary": [], "precedents": [],
             "sufficient": [], "version": 1}
U097_NORM = {"norm": {"guard": ["or", ["unary", "is_elementary", ["var", 0]], ["unary", "is_fundamental", ["var", 0]]],
                      "name": "u097-free-at-least-elementary-and-fundamental", "over": [],
                      "predicate": "education_free_required", "sign": True, "unless": []}}


def u097_unit(span: list[int]) -> dict:
    return {"id": "u097", "kind": "norm", "meaning": {"open": ["free_education"]}, "span": span,
            "support": "none", "content": copy.deepcopy(U097_NORM)}


def udhr_companion() -> Path:
    part_meta, _ = split_document(UDHR_RUN / "translation-part03.ve.md")
    vocab = part_meta["environment"]["vocabulary"]
    predicates = {"is_elementary": vocab["predicates"]["is_elementary"], **U097_PREDICATES}
    env = {"language": "ve.core@0.2", "profiles": ["documents@1", "norm-defaults@0", "norms@0", "relational-fol@0"],
           "spec_revision": part_meta["environment"]["spec_revision"],
           "vocabulary": {"constants": {}, "predicates": predicates,
                          "sorts": {"education_kind": vocab["sorts"]["education_kind"]}}}
    doc = {"format": "ve-document@1", "environment": env, "open_terms": [U097_OPEN],
           "units": [u097_unit([0, len(U097_SOURCE.encode())])]}
    path = OUT / "udhr-u097.ve.md"
    write_document(path, doc, U097_SOURCE.encode())
    return path


# Re-identification of part03's two older reading sets (`models`, plain formula content) after the vocabulary
# grows: each content reading's meaning id and each model's id are recomputed by main's own functions, and every
# model gets an empty relation for each predicate it lacks (the two new ones). Lean then admits the whole document again.
REIDENTIFY_SCRIPT = r"""
import json, sys
from ve.document import _environment
from ve.identity import meaning_id
from ve.ast import formula_from_data
from ve.model import FiniteModel
meta = json.loads(sys.stdin.read())
env = _environment(meta["environment"])
new_preds = list(meta["environment"]["vocabulary"]["predicates"])
renamed = {}
for item in meta.get("reading_sets", []):
    models = item.get("models", {})
    fixed = {}
    for old, data in models.items():
        data = json.loads(json.dumps(data))
        for n in new_preds:
            data.setdefault("relations", {}).setdefault(n, [])
        mid = FiniteModel.from_dict(env, data).model_id
        renamed[old] = mid
        fixed[mid] = data
    if models:
        item["models"] = fixed
    for r in item["readings"]:
        if r["content"] is not None:
            r["meaning_id"] = meaning_id(env, formula_from_data(env, r["content"]))
        r["admission"]["distinguishing_models"] = {k: renamed.get(v, v)
                                                   for k, v in r["admission"]["distinguishing_models"].items()}
print(json.dumps(meta, ensure_ascii=False))
"""


def udhr_spliced() -> Path:
    meta, body = split_document(UDHR_RUN / "translation-part03.ve.md")
    assert body[U097_SPAN_PART03[0]:U097_SPAN_PART03[1]] == U097_SOURCE.encode()
    meta = copy.deepcopy(meta)
    vocab = meta["environment"]["vocabulary"]
    assert not set(vocab["predicates"]) & set(U097_PREDICATES)
    vocab["predicates"].update(U097_PREDICATES)
    assert U097_OPEN["name"] not in {t["name"] for t in meta["open_terms"]}
    meta["open_terms"].append(U097_OPEN)
    for i, unit in enumerate(meta["units"]):
        if unit["id"] == "u097":
            assert unit["kind"] == ["unformalised", "quantities"]
            meta["units"][i] = u097_unit(list(U097_SPAN_PART03))
    proc = ve_python(["-c", REIDENTIFY_SCRIPT], stdin=json.dumps(meta))
    if proc.returncode:
        raise SystemExit(proc.stderr[-4000:])
    meta = json.loads(proc.stdout)
    path = WORK / "udhr-translation-part03-qt0p.ve.md"
    write_document(path, meta, body)
    return path


# Status witnesses, as the UDHR pilot's witnesses_nd.py reads them (Lean's `norm-defaults-status` rows).
STATUS_SCRIPT = r"""
import json, sys
from itertools import product
from ve.document import load_document
from ve.norm_defaults_route import run_case, source_case
path, spec = sys.argv[1], json.loads(sys.stdin.read())
ud = load_document(path)["norm_defaults"]
out = []
for case in spec:
    model = {"complete": True, "constants": {}, "domains": case["domains"], "relations": case["relations"]}
    c = source_case(ud, "norm-defaults-status", model=model, predicate=case["predicate"], tuple=case["row"],
                    method="enumerate")
    res = run_case(c)
    if res["point_status"] == "UNKNOWN":
        yes = {i["name"]: [list(x) for x in product(*(model["domains"][s] for s in i["sorts"]))]
               for i in ud.elaboration["unsaid"]}
        no = {i["name"]: [] for i in ud.elaboration["unsaid"]}
        res = run_case({**c, "method": "undecided", "yes": yes, "no": no})
    out.append({"name": case["name"], "row": case["row"], "lean_point_status": res["point_status"],
                "rules": res.get("rules")})
print(json.dumps(out))
"""


def u097_relations(extra: dict, declared: dict) -> dict:
    relations = {n: [] for n, p in declared.items() if "regulated" not in p}
    relations.update(extra)
    return relations


def udhr_status_cases(path: Path) -> list[dict]:
    meta, _ = split_document(path)
    declared = meta["environment"]["vocabulary"]["predicates"]
    domains = {s: [] for s in meta["environment"]["vocabulary"]["sorts"]}
    # e0 elementary, e1 fundamental (not elementary), e2 higher (neither), e3 both
    domains["education_kind"] = ["e0", "e1", "e2", "e3"]
    rel = u097_relations({"is_elementary": [["e0"], ["e3"]], "is_fundamental": [["e1"], ["e3"]]}, declared)
    expected = {"e0": "SETTLED yes", "e1": "SETTLED yes", "e2": "UNDECIDED", "e3": "SETTLED yes"}
    return [{"name": f"education_free_required({e})", "predicate": "education_free_required", "row": [e],
             "domains": domains, "relations": rel, "expected": expected[e]} for e in domains["education_kind"]]


def run_status(path: Path) -> list[dict]:
    cases = udhr_status_cases(path)
    proc = ve_python(["-c", STATUS_SCRIPT, str(path)], stdin=json.dumps(cases))
    if proc.returncode:
        return [{"error": proc.stderr[-4000:]}]
    rows = json.loads(proc.stdout)
    for row, case in zip(rows, cases):
        row["expected"] = case["expected"]
        row["as_expected"] = row["lean_point_status"] == case["expected"]
    return rows


# A model of the repaired content at domain size 3, searched by the Rust enumerator and checked by Lean
# (`ve.search.find_countermodel` with conclusion "bottom": a countermodel to falsehood is a model of the premises);
# the same model refutes FOURTH. The document check's own premise search stops at domain size 2.
MODEL_SCRIPT = r"""
import json, sys
from ve.document import _environment
from ve.ast import formula_from_data
from ve.search import find_countermodel
spec = json.loads(sys.stdin.read())
env = _environment(spec["environment"])
premises = [formula_from_data(env, f) for f in spec["premises"]]
out = {}
for name, concl in spec["conclusions"].items():
    for size in (2, 3):
        r = find_countermodel(env, premises, formula_from_data(env, concl), max_domain_size=size)
        out[f"{name}@{size}"] = {"status": getattr(r, "status", None), "found": getattr(r, "model", None) is not None,
                                 "model": r.model.to_dict() if getattr(r, "model", None) is not None and
                                 hasattr(r.model, "to_dict") else None}
print(json.dumps(out, default=str))
"""


def constitution_model() -> dict:
    meta, _ = split_document(OUT / "constitution-u0042-u0043.ve.md")
    spec = {"environment": meta["environment"], "premises": [PRESUPPOSITION, THREE],
            "conclusions": {"bottom": ["bottom"], "fourth": FOURTH}}
    proc = ve_python(["-c", MODEL_SCRIPT], stdin=json.dumps(spec))
    if proc.returncode:
        return {"error": proc.stderr[-4000:]}
    return json.loads(proc.stdout)


# ---------------------------------------------------------------- driver

def record(name: str, args: list[str]) -> dict:
    proc = run_ve(args)
    (OUT / f"{name}.out").write_text(proc.stdout)
    if proc.stderr:
        (OUT / f"{name}.err").write_text(proc.stderr)
    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError:
        parsed = None
    return {"args": args, "returncode": proc.returncode, "json": parsed}


def readings_probe(name: str, doc: Path, formula, expected: str) -> dict:
    conclusion = OUT / f"{name}.conclusion.json"
    write_json(conclusion, formula)
    res = record(name, ["document", "readings", str(doc), "--conclusion", str(conclusion)])
    verdict = res["json"].get("verdict") if isinstance(res["json"], dict) else None
    return {"probe": name, "expected": expected, "verdict": verdict, "as_expected": verdict == expected,
            "returncode": res["returncode"]}


def check_summary(res: dict) -> dict:
    data = res["json"] if isinstance(res["json"], dict) else {}
    return {"returncode": res["returncode"], "status": data.get("status"),
            "premises": (data.get("premises") or {}).get("status"),
            "bytes_by_status": (data.get("coverage") or {}).get("bytes_by_status")}


def coverage_delta(before: dict, after: dict) -> dict:
    keys = sorted(set(before["bytes_by_status"]) | set(after["bytes_by_status"]))
    return {k: after["bytes_by_status"].get(k, 0) - before["bytes_by_status"].get(k, 0) for k in keys}


def main() -> None:
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.rmtree(WORK, ignore_errors=True)
    OUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    summary = {"main_head": main_head(), "inputs": {
        "constitution": {"path": str(CONSTITUTION_RUN / "translation.ve.md"),
                         "sha256": sha256(CONSTITUTION_RUN / "translation.ve.md")},
        "udhr_part03": {"path": str(UDHR_RUN / "translation-part03.ve.md"),
                        "sha256": sha256(UDHR_RUN / "translation-part03.ve.md")}}}

    comp = constitution_companion()
    base = constitution_rebuild(repaired=False)
    rep = constitution_rebuild(repaired=True)
    summary["constitution"] = {
        "companion": str(comp.relative_to(REPO)),
        "companion_check": check_summary(record("c-companion-check", ["document", "check", str(comp)])),
        "model_search": constitution_model(),
        "rebuild": {tag: {"returncode": r["returncode"],
                          "admitted": (r["result"] or {}).get("admitted"),
                          "premises": ((r["result"] or {}).get("premises") or {}).get("status"),
                          "bytes_by_status": (r["result"] or {}).get("bytes_by_status"),
                          "pairs_without_situation": (r["result"] or {}).get("pairs_without_situation"),
                          "document_sha256": sha256(r["document"]) if r["document"].exists() else None}
                    for tag, r in (("baseline", base), ("repaired", rep))},
    }
    if rep["document"].exists():
        doc = rep["document"]
        summary["constitution"]["repaired_coverage"] = record("c-repaired-coverage",
                                                              ["document", "coverage", str(doc)])["json"]
        # Lean's readings route refuses `readings@1` on a document with no reading set, so the probes run on the
        # rebuilt pilot translation, as the pilot's own conclusion probes do.
        summary["constitution"]["probes"] = [
            readings_probe("c-repaired-no-fourth", doc, NO_FOURTH, "ALL"),
            readings_probe("c-repaired-fourth", doc, FOURTH, "NONE"),
            readings_probe("c-repaired-anthropic-is-one", doc, ANTHROPIC_IS_ONE, "ALL")]
    if base["document"].exists():
        summary["constitution"]["baseline_coverage"] = record("c-baseline-coverage",
                                                              ["document", "coverage", str(base["document"])])["json"]
    bc, rc = summary["constitution"].get("baseline_coverage"), summary["constitution"].get("repaired_coverage")
    if isinstance(bc, dict) and isinstance(rc, dict):
        summary["constitution"]["coverage_delta_bytes_by_status"] = coverage_delta(bc, rc)

    ucomp = udhr_companion()
    uspliced = udhr_spliced()
    before_u = record("u-part03-original-coverage",
                      ["document", "coverage", str(UDHR_RUN / "translation-part03.ve.md")])["json"]
    summary["udhr"] = {
        "companion": str(ucomp.relative_to(REPO)), "spliced_sha256": sha256(uspliced),
        "companion_check": check_summary(record("u-companion-check", ["document", "check", str(ucomp)])),
        "companion_coverage": record("u-companion-coverage", ["document", "coverage", str(ucomp)])["json"],
        "companion_status": run_status(ucomp),
        "spliced_check": check_summary(record("u-spliced-check", ["document", "check", str(uspliced)])),
        "spliced_coverage": record("u-spliced-coverage", ["document", "coverage", str(uspliced)])["json"],
        "spliced_status": run_status(uspliced),
    }
    if isinstance(before_u, dict) and isinstance(summary["udhr"]["spliced_coverage"], dict):
        summary["udhr"]["coverage_delta_bytes_by_status"] = coverage_delta(before_u, summary["udhr"]["spliced_coverage"])
    write_json(OUT / "summary.json", summary)
    print(json.dumps(summary, indent=1)[:6000])


if __name__ == "__main__":
    main()
