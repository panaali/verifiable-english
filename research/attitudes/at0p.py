#!/usr/bin/env python3
"""AT-0p (docs/spec/attitudes-PLAN.md section 4): the pilot repair of the seven hard constraints with the existing language.

    uv run python research/attitudes/at0p.py copy        # pilot run (read only) -> research/attitudes/run-baseline/, run-at0p/
    uv run python research/attitudes/at0p.py apply       # rewrites the guards in run-at0p/ (the two documents nd.py reads)

The pilot run is read from PILOT and never written. Its scripts find the repository as `RUN.parents[2]`, so the working
copies live at research/attitudes/run-*/, whose parents[2] is this checkout: they run against this checkout's VE.

For each hard constraint i (u0165.s0i), the guard `C_i(s) ∧ restricted_action_knowing_or_quite_likely(s)` becomes
`( C_i(s) ∧ knowingly_engages_<i>(c, s) ) ∨ thinks_quite_likely_<i>(c, s)`, with fourteen binary open terms on
(claude_instance, situation); `restricted_action_knowing_or_quite_likely` is deleted. Guards use de Bruijn variables
(docs/spec/norms.md: index 0 is the last argument), so `s` is `var 0` and `c` is `var 1`. No product code is changed.
"""
from __future__ import annotations

import copy
import importlib.util
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PILOT = Path("/home/seyran/code/manage-agents/pilots/claude-constitution/run-20261012T1800Z")
BASELINE = HERE / "run-baseline"
WORK = HERE / "run-at0p"

GONE = "restricted_action_knowing_or_quite_likely"
CLAUDE, SITUATION = "claude_instance", "situation"
# u0165.s0i -> (case atom C_i, the source's words for the category); the case atoms are the run's (spec.HARD)
UNITS = [f"u0165.s0{i}" for i in range(1, 8)]
SOURCE_U0173 = ("u0173.s01: the hard constraints are “centrally meant to apply to cases where Claude would either be knowingly "
                "and intentionally engaging in an action of the relevant restricted category, or where Claude thinks it quite "
                "likely that a given action would fall into such a category”.")


def knowing(i):
    return f"knowingly_engages_{i}"


def thinking(i):
    return f"thinks_quite_likely_{i}"


def un(pred, i):
    return ["unary", pred, ["var", i]]


def bi(pred, i, j):
    return ["binary", pred, ["var", i], ["var", j]]


def guard(case, i):
    """( C_i(s) ∧ knowingly_engages_i(c, s) ) ∨ thinks_quite_likely_i(c, s), with c = var 1 and s = var 0."""
    return ["or", ["and", case, bi(knowing(i), 1, 0)], bi(thinking(i), 1, 0)]


def terms(i, words):
    """The two open-term records and predicate entries of rule i (W2's record shape, as the run's own open terms)."""
    category = words[len("Claude "):] if words.startswith("Claude ") else words
    k_desc = (f"{SOURCE_U0173} Hard constraint u0165.s0{i}: the instance of Claude knowingly and intentionally engages, in the "
              f"situation, in an action of the restricted category of {category}. Which pairs these are is the open term "
              f"{knowing(i)} (AT-0p; not typed: VE does not know that knowing implies the category).")
    t_desc = (f"{SOURCE_U0173} Hard constraint u0165.s0{i}: the instance of Claude thinks it quite likely that the action of "
              f"the situation falls into the restricted category of {category}. Which pairs these are is the open term "
              f"{thinking(i)} (AT-0p; not typed).")
    preds = {
        knowing(i): {"arguments": [CLAUDE, SITUATION], "description": k_desc,
                     "verbalisation": "{0} knowingly and intentionally engages in {1} as a case of " + words},
        thinking(i): {"arguments": [CLAUDE, SITUATION], "description": t_desc,
                      "verbalisation": "{0} thinks it quite likely that {1} is a case of " + words},
    }
    record = lambda name, factors: {"name": name, "arguments": [CLAUDE, SITUATION], "decided_by": "unresolved_decider",
                                    "necessary": [], "sufficient": [], "factors": factors, "precedents": [],
                                    "jurisdiction": "claude_constitution", "version": 1}
    records = [record(knowing(i), ["what counts as knowingly and intentionally engaging in an action of the category"]),
               record(thinking(i), ["how likely counts as quite likely"])]
    return preds, records


def pilot_module():
    spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def drop_relation(x, name):
    """The run's own helper (repair_20261012T1800Z.py): drop a predicate from stored models' relations."""
    if isinstance(x, dict):
        if isinstance(x.get("relations"), dict):
            x["relations"].pop(name, None)
        for v in x.values():
            drop_relation(v, name)
    elif isinstance(x, list):
        for v in x:
            drop_relation(v, name)


def rewrite(meta, words_of):
    """AT-0p on one document's front matter. Returns the new front matter; asserts the starting shape."""
    meta = copy.deepcopy(meta)
    vocab = meta["environment"]["vocabulary"]["predicates"]
    assert GONE in vocab and [t["name"] for t in meta["open_terms"]].count(GONE) == 1
    del vocab[GONE]
    meta["open_terms"] = [t for t in meta["open_terms"] if t["name"] != GONE]
    drop_relation(meta.get("reading_sets", []), GONE)
    pilot = pilot_module()
    done = []
    for unit in pilot._flat(meta["units"]):
        if unit["id"] not in UNITS:
            continue
        i = int(unit["id"][-1])
        norm = unit["content"]["norm"]
        g = norm["guard"]
        assert g[0] == "and" and g[2] == ["unary", GONE, ["var", 0]] and g[1][0] == "unary" and g[1][2] == ["var", 0], unit["id"]
        assert norm["unless"] == [] and vocab[norm["predicate"]]["arguments"] == [CLAUDE, SITUATION], unit["id"]
        case = g[1]
        preds, records = terms(i, words_of[case[1]])
        for name in preds:
            assert name not in vocab
        vocab.update(preds)
        meta["open_terms"].extend(records)
        norm["guard"] = guard(case, i)
        opens = [x for x in unit["meaning"]["open"] if x != GONE]
        unit["meaning"]["open"] = [*opens, knowing(i), thinking(i)]
        done.append(unit["id"])
    assert done == UNITS, done
    return meta


def words_by_case():
    sys.path.insert(0, str(WORK))  # the working copy, never PILOT: an import there would write __pycache__ into it
    import spec  # the run's own table: case atom -> the source's words
    return {term: words for _u, _r, _p, term, _a, words in spec.HARD}


def cmd_copy():
    assert not (PILOT / "__pycache__").exists(), "the pilot run must stay as recorded"
    for target in (BASELINE, WORK):
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(PILOT, target, ignore=shutil.ignore_patterns("__pycache__"))
    print("copied", PILOT, "->", BASELINE.name, WORK.name)


def cmd_apply():
    sys.path.insert(0, str(ROOT))
    pilot = pilot_module()
    words = words_by_case()
    for rel in ("translation-without-content.ve.md", "readings/all-strict.ve.md"):
        meta, source = pilot.read(WORK / rel)
        pilot.write(WORK / rel, rewrite(meta, words), source)
        print("rewrote", rel)


EVIDENCE = ROOT / "docs/research/evidence/attitudes"


def dump(name, obj):
    import json
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def cmd_probe():
    """The plan's probe points on the AT-0p strict companion, asked as the run's probe_unspecified.py asks them (Lean's
    norm-defaults-status row at a one-element situation; UNKNOWN falls back to the run's "undecided" tables; at an
    `operator_input_permitted` point, the run's conflict check). Every point of the run's probe not about the seven
    rules is asked again and compared with the run's recorded status, and so are the run's conflict checks."""
    import json
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(WORK))
    from itertools import product
    from conformance import frozen_norm_defaults as fnd  # the run's evidence proposer; Lean replays every proposal
    from ve.document import load_document
    from ve.norm_defaults_route import run_case, source_case
    import probe_unspecified as run_probe  # the working copy's module: situation() only; its main() is not called
    import spec_nd

    doc = load_document(WORK / "readings/all-strict.ve.md")["norm_defaults"]
    env = doc.env
    fdoc = fnd.UnspecifiedDocument(doc.env, doc.author.rules)
    assert GONE not in env.predicates

    def status(predicate, atoms):
        text = point_status(predicate, atoms)
        if predicate == "operator_input_permitted":  # as the run: the point status does not show a rule conflict
            report = fnd.check_conflict(fdoc, model=run_probe.situation(doc, atoms).to_dict())
            if report.status == "CONFLICT" and report.target == predicate:
                text = f"CONFLICT ({report.kind}: permitted by one rule, forbidden by another)"
        return text

    def point_status(predicate, atoms):
        model = run_probe.situation(doc, atoms)
        values = [x + "0" for x in env.predicates[predicate].arguments]
        case = source_case(doc, "norm-defaults-status", model=model.to_dict(), predicate=predicate, tuple=values,
                           method="enumerate")
        row = run_case(case)
        if row["point_status"] == "UNKNOWN":  # as the run: every unsaid atom true, then every one false
            yes = {item["name"]: [list(v) for v in product(*(model.to_dict()["domains"][x] for x in item["sorts"]))]
                   for item in doc.elaboration["unsaid"]}
            no = {item["name"]: [] for item in doc.elaboration["unsaid"]}
            row = run_case({**case, "method": "undecided", "yes": yes, "no": no})
        return row["point_status"]

    # (bar, label, atoms(case, K, T), expected); A3 is asked at two points (case true / case false)
    points = [("A1", "case false, thinks-quite-likely true", lambda c, k, t: [t], "SETTLED no"),
              ("A2", "case true, knowingly true", lambda c, k, t: [c, k], "SETTLED no"),
              ("A3", "neither attitude; case true", lambda c, k, t: [c], "UNDECIDED"),
              ("A3", "neither attitude; case false", lambda c, k, t: [], "UNDECIDED"),
              ("A4", "case false, knowingly true", lambda c, k, t: [k], "UNDECIDED"),
              ("info", "case true, thinks-quite-likely true", lambda c, k, t: [c, t], None),
              ("info", "case false, knowingly and thinks-quite-likely true", lambda c, k, t: [k, t], None)]
    hard = []
    for unit, _rule, pred, term, _act, _words in spec_nd.HARD:
        i = int(unit[-1])
        for bar, label, atoms, expected in points:
            got = status(pred, atoms(term, knowing(i), thinking(i)))
            hard.append({"bar": bar, "unit": unit, "predicate": pred, "label": label,
                         "true_atoms": sorted(atoms(term, knowing(i), thinking(i))), "status": got, "expected": expected,
                         "as_expected": None if expected is None else got == expected})

    recorded = json.loads((PILOT / "probes/unspecified-probe.json").read_text())
    baseline_audit_case = {p["label"].split(":")[0]: p["status"] for p in recorded["points"]
                           if p["label"].endswith("the case does not hold (the knowledge atom does)")}
    others = []
    for p in recorded["points"]:
        if p["label"].startswith("u0165"):
            continue
        got = status(p["predicate"], p["true_atoms"])
        others.append({"label": p["label"], "predicate": p["predicate"], "true_atoms": p["true_atoms"], "status": got,
                       "recorded": p["status"], "same": got == p["status"],
                       "conflict_checked": p["predicate"] == "operator_input_permitted"})

    # the run's conflict section: the three witness situations, then the whole document (proof attempt, Lean's row)
    conflicts = {}
    for label, atoms in [("a role-play instruction that also claims to be human",
                          ["instruction_role_play_custom_persona", "instruction_claim_human_when_asked"]),
                         ("a persona that also is an instruction to claim to be human",
                          ["input_is_persona", "instruction_claim_human_when_asked"]),
                         ("no atom true", [])]:
        report = fnd.check_conflict(fdoc, model=run_probe.situation(doc, atoms).to_dict())
        conflicts[label] = {"status": report.status, "target": report.target, "kind": report.kind,
                            "tuple": list(report.tuple)}
    proof = fnd.check_conflict(fdoc, prove=True)
    lean = run_case(source_case(doc, "norm-defaults-conflict", packages=dict(proof.certificates)))
    conflicts["whole document, proof attempt"] = {"status": lean.get("verdict"), "detail": "", "oracle_status": proof.status,
                                                  "lean_row_keys": sorted(lean)}
    conflict_same = {k: conflicts[k] == recorded["conflict"][k] for k in conflicts}

    def bar(name):
        rows = [r for r in hard if r["bar"] == name]
        return {"points": len(rows), "as_expected": sum(r["as_expected"] for r in rows),
                "verdict": "PASS" if all(r["as_expected"] for r in rows) else "FAIL"}
    verdicts = {name: bar(name) for name in ("A1", "A2", "A3", "A4")}
    a5_baseline = sorted(baseline_audit_case.items())
    verdicts["A5"] = {"baseline_points": a5_baseline,
                      "baseline_all_undecided": len(a5_baseline) == 7 and all(s == "UNDECIDED" for _, s in a5_baseline),
                      "after": "A1",
                      "verdict": "PASS" if (len(a5_baseline) == 7 and all(s == "UNDECIDED" for _, s in a5_baseline)
                                            and verdicts["A1"]["verdict"] == "PASS") else "FAIL"}
    out = {"document": "research/attitudes/run-at0p/readings/all-strict.ve.md (AT-0p strict companion)",
           "pilot": str(PILOT), "method": ("probe_unspecified.py's point(): Lean norm-defaults-status, one-element situation; "
                                           "at operator_input_permitted points, the run's conflict check"),
           "verdicts": verdicts, "hard_constraint_points": hard,
           "other_points": {"asked": len(others), "same_as_recorded": sum(o["same"] for o in others),
                            "conflict_checked": sum(o["conflict_checked"] for o in others), "rows": others},
           "conflict": {"checks": conflicts, "same_as_recorded": conflict_same}}
    dump("at0p-probe.json", out)
    for r in hard:
        print(f"{r['bar']:5} {r['unit']} {r['status']:12} {r['label']}")
    print(json.dumps(verdicts, indent=1))
    print("other points same as recorded:", out["other_points"]["same_as_recorded"], "/", len(others),
          "(conflict-checked:", out["other_points"]["conflict_checked"], ")")
    print("conflict checks same as recorded:", conflict_same)


def cmd_measure():
    """A6, A7 and the regression checks on the rebuilt main translation and the strict companion (ve document check and
    coverage, the run's own assertions), against the run's recorded files."""
    import hashlib
    import json
    import subprocess
    main, strict = WORK / "translation.ve.md", WORK / "readings/all-strict.ve.md"

    def ve(*args):
        cmd = ["prlimit", "--as=6442450944", sys.executable, "-m", "ve", *args]
        return json.loads(subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True).stdout)

    sys.path.insert(0, str(ROOT))
    pilot = pilot_module()
    check, coverage = ve("document", "check", str(main)), ve("document", "coverage", str(main))
    s_check = ve("document", "check", str(strict))
    recorded_cov = json.loads((PILOT / "coverage.json").read_text())
    recorded_metrics = json.loads((PILOT / "metrics.json").read_text())
    meta, _ = pilot.read(main)
    smeta, _ = pilot.read(strict)
    names = [t["name"] for t in meta["open_terms"]]
    added = sorted(set(names) - {t["name"] for t in recorded_metrics["open_terms"]})
    removed = sorted({t["name"] for t in recorded_metrics["open_terms"]} - set(names))
    regress = {"premises_model": check["premises"]["status"] == "model",
               "plan_enumerate_8": check["reading_plan"]["route"] == "enumerate" and len(check["reading_plan"]["choices"]) == 8,
               "readings_conflict_free": check["readings"]["conflict"]["status"] == "CONFLICT-FREE",
               "coverage_100": coverage["coverage_percent"] == 100,
               "strict_premises": s_check["premises"]["status"]}
    out = {"A6": {"bytes_by_status": coverage["bytes_by_status"], "recorded": recorded_cov["bytes_by_status"],
                  "claimed_recorded": recorded_metrics["claimed_covered_bytes"],
                  "verdict": "PASS" if coverage["bytes_by_status"] == recorded_cov["bytes_by_status"] else "FAIL"},
           "A7": {"open_terms": len(names), "recorded": recorded_metrics["open_terms_count"], "expected": 46,
                  "added": added, "removed": removed, "strict_companion_open_terms": len(smeta["open_terms"]),
                  "verdict": "PASS" if len(names) == 46 else "FAIL"},
           "regressions": regress,
           "sha256": {p.relative_to(WORK).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (main, strict, WORK / "translation-without-content.ve.md")},
           "seven_units": {u["id"]: u["content"]["norm"] for u in pilot._flat(meta["units"]) if u["id"] in UNITS},
           "new_predicates": {n: meta["environment"]["vocabulary"]["predicates"][n]
                              for i in range(1, 8) for n in (knowing(i), thinking(i))}}
    dump("at0p-measure.json", out)
    print(json.dumps({k: out[k] for k in ("A6", "A7", "regressions")}, indent=1)[:4000])


def cmd_render():
    """`ve document render` of the AT-0p translation against this checkout's render of the unmodified run (which
    run_at0p.sh first checks is byte-identical to the run's recorded rendered-raw.md): every line that differs must be
    one of the seven rules' "Open reading" lines that name the deleted term, and each must be replaced."""
    import difflib
    import hashlib
    before = (BASELINE / "rendered-raw.md").read_text().splitlines()
    after = (WORK / "rendered-raw.md").read_text().splitlines()
    hunks = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, before, after, autojunk=False).get_opcodes():
        if tag != "equal":
            hunks.append({"tag": tag, "before_lines": [i1 + 1, i2], "after_lines": [j1 + 1, j2],
                          "before": before[i1:i2], "after": after[j1:j2]})
    changed = [line for h in hunks for line in h["before"]]
    only_seven = (len(hunks) == 7 and all(h["tag"] == "replace" and len(h["before"]) == 1 for h in hunks)
                  and all(line.startswith("Open reading:") and f'"{GONE}"' in line for line in changed)
                  and sum(f'"{GONE}"' in line for line in before) == 7 and not any(GONE in line for line in after))
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    out = {"before": "research/attitudes/run-baseline/rendered-raw.md (this checkout's render of the run's translation; "
                     "cmp-identical to the run's recorded rendered-raw.md)",
           "after": "research/attitudes/run-at0p/rendered-raw.md",
           "sha256": {"before": sha(BASELINE / "rendered-raw.md"), "recorded": sha(PILOT / "rendered-raw.md"),
                      "after": sha(WORK / "rendered-raw.md")},
           "lines": {"before": len(before), "after": len(after)}, "lines_changed_before": len(changed),
           "only_the_seven_rules_changed": only_seven, "hunks": hunks}
    dump("at0p-render-diff.json", out)
    print("hunks:", len(hunks), "lines changed:", len(changed), "only the seven rules:", only_seven)
    sys.exit(0 if only_seven else 1)


if __name__ == "__main__":
    {"copy": cmd_copy, "apply": cmd_apply, "probe": cmd_probe, "measure": cmd_measure,
     "render": cmd_render}[sys.argv[1]]()
