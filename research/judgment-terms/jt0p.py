#!/usr/bin/env python3
"""JT-0p item 2 (docs/spec/judgment-terms-PLAN.md section 5): UDHR u010 and u060 as asserted judgments.

    uv run python research/judgment-terms/jt0p.py copy      # pinned run (read only) -> run-baseline/, run-jt0p/
    uv run python research/judgment-terms/jt0p.py apply     # the encoding of the phase-1 report, 1.3.2, in run-jt0p/
    uv run python research/judgment-terms/jt0p.py check run-baseline   # check, load, render the four parts
    uv run python research/judgment-terms/jt0p.py check run-jt0p
    uv run python research/judgment-terms/jt0p.py compare   # bar part A (A1-A5), reproduction P1, the render diff

The pilot run is read from PILOT and never written. `check` does what the run's own check_parts.py does
(check_document, load_document, render_document) against this checkout's VE. No product code is changed.
"""
from __future__ import annotations

import copy
import difflib
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PILOT = Path("/home/seyran/code/manage-agents/pilots/udhr/run-20261012T1800Z")
EVIDENCE = ROOT / "docs/research/evidence/judgment-terms"
PARTS = [f"translation-part0{i}.ve.md" for i in range(1, 5)]
BASELINE, WORK = HERE / "run-baseline", HERE / "run-jt0p"

U010_TERM, U060_TERM = "of_greatest_importance_for", "natural_and_fundamental_group_unit_of_society"
UNDERSTANDING = "common_understanding_of_these_rights_and_freedoms"
REALIZATION = "full_realization_of_this_pledge"
FAMILY = "the_family"

THING = {"description": "a thing the text names: an understanding, an aim or an institution",
         "verbalisation": {"plural": "things", "singular": "thing"}}


def record(name, arguments, factors):
    """A W2 open-term record (the nine keys), as the plan's JT-0p asks."""
    return {"arguments": arguments, "decided_by": "unresolved_decider", "factors": factors, "jurisdiction": "universal",
            "name": name, "necessary": [], "precedents": [], "sufficient": [], "version": 1}


# The two unused placeholders this batch replaces in place (report 1.3.2), and their replacements.
REPLACE = {
    "greatest_importance": record(U010_TERM, ["understanding", "realization"],
                                  ["comparison class", "measure of importance"]),
    "natural_group_unit": record(U060_TERM, ["thing"],
                                 ["meaning of natural", "meaning of fundamental",
                                  "what counts as a group unit of society"]),
}

PART1_CONSTANTS = {
    UNDERSTANDING: {"sort": "thing",
                    "description": "a common understanding of these rights and freedoms: the human rights and fundamental "
                                   "freedoms whose universal respect and observance the Member States have pledged "
                                   "themselves to promote (the preceding clause, u009)"},
    REALIZATION: {"sort": "thing",
                  "description": "the full realization of this pledge: the pledge of the Member States in the preceding "
                                 "clause (u009)"},
}
PART1_PREDICATE = {U010_TERM: {"arguments": ["thing", "thing"],
                               "description": "The first thing is of the greatest importance for the second; the open "
                                              f"term {U010_TERM} (a judgment; the text does not say who makes it)"}}
# No verbalisation for the binary predicate (report section 2, deviation D3): the wording lint rejects
# "{0} is of the greatest importance for {1}" (BINARY_AUXILIARY, BINARY_CONVERSE, LOGICAL_WORD), and its head "is" still
# collides with every one-word "{0} is X" template of the part (ve/printer.py, SYMBOL_COLLISION).
PART2_CONSTANTS = {FAMILY: {"sort": "thing",
                            "description": "the family, the institution the Article names, not any one family"}}
PART2_PREDICATE = {U060_TERM: {"arguments": ["thing"],
                               "description": "The thing is the natural and fundamental group unit of society; the open "
                                              f"term {U060_TERM} (a judgment; the text does not say who makes it)",
                               "verbalisation": "{0} is the natural and fundamental group unit of society"}}

UNITS = {
    "u010": {"kind": "asserted", "meaning": {"open": [U010_TERM]}, "support": "none",
             "content": {"ast": ["binary", U010_TERM, ["const", UNDERSTANDING], ["const", REALIZATION]]}},
    "u060": {"kind": "asserted", "meaning": {"open": [U060_TERM]}, "support": "none",
             "content": {"ast": ["unary", U060_TERM, ["const", FAMILY]]}},
}

LEDGER = {
    "u010": {"status": "OPEN", "open_terms": [U010_TERM], "semantic_kind": "asserted judgment",
             "jt0p_note": "JT-0p: an asserted judgment, OPEN. The ground atom says that a common understanding of these "
                          "rights and freedoms is of the greatest importance for the full realization of this pledge; "
                          "whether it is is a judgment the text leaves to no one it names (unresolved_decider). The "
                          "recital function of 'Whereas' (a reason given for the proclamation) is not represented. "
                          "Bytes claimed only if the targeted blind audit finds the unit FAITHFUL (plan JT-0p)."},
    "u060": {"status": "OPEN", "open_terms": [U060_TERM], "semantic_kind": "asserted judgment",
             "missing_feature": "presupposition", "claimed": False,
             "jt0p_note": "JT-0p: an asserted judgment, OPEN, written and audited but its bytes are not claimed. 'The' "
                          "(uniqueness: the one natural and fundamental group unit) is not represented; it is "
                          "presupposition's. 'The family' is read as the institution (one constant), not as every "
                          "family; u061 reads the same subject distributively for its entitlement."},
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_doc(path):
    text = Path(path).read_text()
    lines = text.split("\n")
    assert lines[0] == "---" and lines[2] == "---", path
    return lines, json.loads(lines[1])


def write_doc(path, lines, front):
    lines = list(lines)
    lines[1] = json.dumps(front, ensure_ascii=False)
    Path(path).write_text("\n".join(lines))


def extended(model, constants, predicates):
    """A model or situation base over the new vocabulary: one `thing`, every new constant on it, new relations empty.

    The readings the models and situations separate do not mention the new sort, constants or predicates, so their
    values are unchanged; Lean re-checks every situation and Python every model at load."""
    model = copy.deepcopy(model)
    model["domains"] = dict(sorted({**model["domains"], "thing": ["thing"]}.items()))
    model["constants"] = dict(sorted({**model["constants"], **{c: "thing" for c in constants}}.items()))
    model["relations"] = dict(sorted({**model["relations"], **{p: [] for p in predicates}}.items()))
    return model


def reidentified(environment, sets, constants, predicates):
    """Every id a reading set carries, recomputed over the new environment by VE's own identity functions.

    Meaning ids, distinguishing-model ids and S1 situation ids are digests over the environment id (ve/identity.py,
    ve/model.py, ve/readings_s1.py), so a new sort, constant or predicate changes them all; the pilot's own build
    recomputes them the same way (tools/readings_s1_pilot.py, `_reidentified`). Report section 2, deviation D1."""
    sys.path.insert(0, str(ROOT))
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
        item = copy.deepcopy(item)
        renamed = {}
        if "models" in item:
            models = {}
            for old, data in item["models"].items():
                data = extended(data, constants, predicates)
                new = FiniteModel.from_dict(model_env, data).model_id
                renamed[old], models[new] = new, data
            item["models"] = models
        if "situations" in item:
            situations = {}
            for old, entry in item["situations"].items():
                entry = {**entry, "base": extended(entry["base"], constants, predicates)}
                new = digest(f"ve-situation-{env.identity_version}\n",
                             {"environment_id": env.environment_id, "situation": entry})
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


def cmd_copy():
    for target in (BASELINE, WORK):
        target.mkdir(exist_ok=True)
        for name in PARTS + ["units.json"]:
            shutil.copyfile(PILOT / name, target / name)
    print("copied", PARTS, "units.json", "from", PILOT)


def cmd_apply():
    for name in PARTS:
        lines, front = read_doc(BASELINE / name)
        front = copy.deepcopy(front)
        terms = front["open_terms"]
        names = [t["name"] for t in terms]
        for old, new in REPLACE.items():
            terms[names.index(old)] = new
        vocab = front["environment"]["vocabulary"]
        if name.endswith("part01.ve.md"):
            vocab["sorts"]["thing"] = THING
            vocab["constants"].update(PART1_CONSTANTS)
            vocab["predicates"].update(PART1_PREDICATE)
        if name.endswith("part02.ve.md"):
            vocab["sorts"]["thing"] = THING
            vocab["constants"].update(PART2_CONSTANTS)
            vocab["predicates"].update(PART2_PREDICATE)
        for unit in front["units"]:
            if unit["id"] in UNITS:
                span = unit["span"]
                for key in ("kind", "meaning", "support", "content"):
                    unit.pop(key, None)
                unit.update(copy.deepcopy(UNITS[unit["id"]]))
                assert unit["span"] == span
        if name.endswith(("part01.ve.md", "part02.ve.md")):
            constants = PART1_CONSTANTS if name.endswith("part01.ve.md") else PART2_CONSTANTS
            predicates = PART1_PREDICATE if name.endswith("part01.ve.md") else PART2_PREDICATE
            front["reading_sets"] = reidentified(front["environment"], front["reading_sets"], constants, predicates)
        write_doc(WORK / name, lines, front)
    ledger = json.loads((BASELINE / "units.json").read_text())
    for unit in ledger["units"]:
        if unit["id"] in LEDGER:
            unit.pop("missing_feature", None)
            unit["status_in_previous_run"] = unit["status"]
            unit.update(LEDGER[unit["id"]])
    (WORK / "units.json").write_text(json.dumps(ledger, indent=1, ensure_ascii=False) + "\n")
    print("applied JT-0p to", WORK)


def cmd_check(label):
    sys.path.insert(0, str(ROOT))
    from ve.document import check_document, load_document, render_document

    run = HERE / label
    out = {}
    for name in PARTS:
        path = run / name
        started = time.monotonic()
        try:
            rep = check_document(path)
            doc = load_document(path)
            text = render_document(path)
            (run / "rendered-parts").mkdir(exist_ok=True)
            (run / "rendered-parts" / (name[:-len(".ve.md")] + ".md")).write_text(text)
            out[name] = {"seconds": round(time.monotonic() - started, 1), "coverage": rep["coverage"],
                         "premises": {k: v for k, v in rep["premises"].items() if k not in ("choices", "model", "candidates")},
                         "readings_status": (rep.get("readings") or {}).get("status"),
                         "conflict": ((rep.get("readings") or {}).get("conflict") or {}).get("status"),
                         "unit_status": {u["id"]: u["status"] for u in doc["units"]},
                         "document_id": rep["document_id"], "source_id": rep["source_id"], "sha256": sha(path)}
            print(name, "ok", out[name]["premises"].get("status"), out[name]["readings_status"], flush=True)
        except Exception as exc:  # recorded verbatim, never hidden
            message = getattr(exc, "message", None) or str(exc)
            out[name] = {"error": f"{type(exc).__name__}: {message}"[:2000], "sha256": sha(path)}
            print(name, "ERR", out[name]["error"], flush=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    label_out = "baseline" if label == "run-baseline" else "jt0p"
    (EVIDENCE / f"parts-check-{label_out}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")


MOVED = {"translation-part01.ve.md": ("u010", 132), "translation-part02.ve.md": ("u060", 66)}


def expected_coverage(base, name):
    """Baseline coverage with the moved unit's bytes moved (report 1.3.3, A5)."""
    cov = copy.deepcopy(base)
    if name in MOVED:
        _, size = MOVED[name]
        cov["bytes_by_status"]["UNFORMALISED"] -= size
        cov["bytes_by_status"]["OPEN"] = cov["bytes_by_status"].get("OPEN", 0) + size
        cov["bytes_by_kind"]["unformalised"] -= size
        cov["bytes_by_kind"]["asserted"] = cov["bytes_by_kind"].get("asserted", 0) + size
        reasons = cov["unformalised_reasons"]
        reasons["other_evaluative_open_claim"] -= 1
        if reasons["other_evaluative_open_claim"] == 0:
            del reasons["other_evaluative_open_claim"]
    return cov


def coverage_diff(a, b, prefix=""):
    """Every member path where two coverage objects differ."""
    diffs = []
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            diffs += coverage_diff(a.get(key), b.get(key), f"{prefix}.{key}" if prefix else key)
    elif a != b:
        diffs.append({"member": prefix, "left": a, "right": b})
    return diffs


def cmd_compare():
    recorded = json.loads((PILOT / "parts-check.json").read_text())
    base = json.loads((EVIDENCE / "parts-check-baseline.json").read_text())
    work = json.loads((EVIDENCE / "parts-check-jt0p.json").read_text())

    p1 = {}
    for name in PARTS:
        r, b = recorded[name], base[name]
        if "error" in b:
            p1[name] = {"pass": False, "error": b["error"]}
            continue
        status_diff = {u: [r["unit_status"].get(u), b["unit_status"].get(u)]
                       for u in sorted(set(r["unit_status"]) | set(b["unit_status"]))
                       if r["unit_status"].get(u) != b["unit_status"].get(u)}
        cov = coverage_diff(r["coverage"], b["coverage"])
        p1[name] = {"pass": not status_diff and not cov, "unit_status_differences": status_diff,
                    "coverage_differences": cov,
                    "premises_equal": r["premises"] == b["premises"],
                    "readings_status_equal": r["readings_status"] == b["readings_status"],
                    "conflict_equal": r["conflict"] == b["conflict"]}

    a1 = {name: "error" not in work[name] for name in PARTS}
    a2 = {}
    a3, a4, a5 = {}, {}, {}
    for name in PARTS:
        if "error" in work[name] or "error" in base[name]:
            a3[name] = a4[name] = a5[name] = {"pass": False, "reason": work[name].get("error") or base[name].get("error")}
            continue
        ws, bs = work[name]["unit_status"], base[name]["unit_status"]
        for unit in ("u010", "u060"):
            if unit in ws:
                a2[unit] = {"part": name, "baseline": bs.get(unit), "jt0p": ws[unit], "pass": ws[unit] == "OPEN"}
        others = {u: [bs.get(u), ws.get(u)] for u in sorted(set(bs) | set(ws))
                  if u not in ("u010", "u060") and bs.get(u) != ws.get(u)}
        a3[name] = {"pass": not others, "differences": others}
        same = {k: base[name][k] == work[name][k] for k in ("premises", "readings_status", "conflict")}
        a4[name] = {"pass": all(same.values()), "equal": same,
                    "baseline": {k: base[name][k] for k in ("premises", "readings_status", "conflict")},
                    "jt0p": {k: work[name][k] for k in ("premises", "readings_status", "conflict")}}
        diff = coverage_diff(expected_coverage(base[name]["coverage"], name), work[name]["coverage"])
        a5[name] = {"pass": not diff, "differences_from_expected": diff}
    bar = {"A1": {"pass": all(a1.values()), "parts": a1},
           "A2": {"pass": len(a2) == 2 and all(v["pass"] for v in a2.values()), "units": a2},
           "A3": {"pass": all(v["pass"] for v in a3.values()), "parts": a3},
           "A4": {"pass": all(v["pass"] for v in a4.values()), "parts": a4},
           "A5": {"pass": all(v["pass"] for v in a5.values()), "parts": a5}}
    bar["bar_part_A"] = "PASS" if all(bar[k]["pass"] for k in ("A1", "A2", "A3", "A4", "A5")) else "FAIL"
    (EVIDENCE / "bar-a.json").write_text(json.dumps(bar, indent=1, ensure_ascii=False) + "\n")
    (EVIDENCE / "reproduction-p1.json").write_text(json.dumps(
        {"P1": {"pass": all(v["pass"] for v in p1.values()), "parts": p1}}, indent=1, ensure_ascii=False) + "\n")

    diff_text = []
    for name in PARTS:
        stem = name[:-len(".ve.md")] + ".md"
        left = (BASELINE / "rendered-parts" / stem).read_text().splitlines(keepends=True)
        right = (WORK / "rendered-parts" / stem).read_text().splitlines(keepends=True)
        diff_text += difflib.unified_diff(left, right, f"baseline/{stem}", f"jt0p/{stem}", n=1)
    (EVIDENCE / "render.diff").write_text("".join(diff_text))
    inputs = {"pilot": str(PILOT), "pilot_sha256": {n: sha(PILOT / n) for n in PARTS + ["units.json", "parts-check.json"]},
              "jt0p_sha256": {n: sha(WORK / n) for n in PARTS + ["units.json"]},
              "ve_service_sha256": sha(ROOT / "lean/.lake/build/bin/ve_service"),
              "rust_sha256": sha(ROOT / "rust/target/release/ve")}
    (EVIDENCE / "jt0p-inputs.json").write_text(json.dumps(inputs, indent=1) + "\n")
    print("bar part A:", bar["bar_part_A"], {k: bar[k]["pass"] for k in ("A1", "A2", "A3", "A4", "A5")})
    print("P1:", all(v["pass"] for v in p1.values()), {n: v["pass"] for n, v in p1.items()})
    print("render diff lines:", len(diff_text))


if __name__ == "__main__":
    command = sys.argv[1]
    if command == "copy":
        cmd_copy()
    elif command == "apply":
        cmd_apply()
    elif command == "check":
        cmd_check(sys.argv[2])
    elif command == "compare":
        cmd_compare()
    else:
        raise SystemExit(__doc__)
