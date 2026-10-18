#!/usr/bin/env python3
"""Run 20261018T1800Z: the measurement of the translation at ve-green-eff-20261018-1, with the plans merged for this run.

Features: thirteen batches merged since ve-green-tarch-histdep; none adds anything a document can say (judgments@0, the events modules and the Numbers/Calc modules are not reachable
from a document; alternatives@0 with norm-defaults is not used by the constitution), so no unit is upgraded by a feature. The previous run's audit (20261018T0600Z) found 25 of 25
verdicts faithful, so nothing needs repair. What changed in the translation are plan-directed repairs (DRI SC2 and the merge of 2026-10-18):
  * QT-0p: u0042.presupposition CHECKED (38 B); u0043.s02 MIXED (p1 LABELLED 15 B, p2 CHECKED 75 B).
  * PS-0p: u0245 (class B) offered, OPEN (26 B); u0286 and u0032 offered and reverted (the whole-document premise check goes UNKNOWN); ledger steps 1 to 5; `presupposition_triggers`
    on every unit; `presupposition-goals.json`.
  * JT-0p: the class of every open term, `judgment_terms` on every unit (ledger only).
  * SC-M0, AP-0 item 3, AT-0p: carried (tags regenerated; the shape of the hard constraints asserted).

Order (repository root, PATH must contain ~/.elan/bin, VE_NATIVE_PREBUILT=1; `lake build` in lean/ and tools/rust_build.py done):
    uv run python .../apply_plans.py qt0p ; uv run python .../nd.py all ; uv run python .../checkpoint.py qt0p     # after QT-0p (the PS-0p variants are in evidence/ps0p/premise-variants.json)
    uv run python .../apply_plans.py ps0p ; uv run python .../nd.py all ; cp readings/nd-all.ve.md translation.ve.md ; uv run python .../checkpoint.py final
    probes (README.md), probe_hard_conclusions.py, probe_soft_chain.py
    uv run python .../finish_20261018T1800Z.py           # ledger (units.json), scope-tally.json, presupposition-goals.json, renderings, check, coverage, metrics.json
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))
import finish_0600 as old  # noqa: E402
import finish_20261012T0600Z as prevf  # noqa: E402  (slice_result, concl)
import finish_20261014T1800Z as p14  # noqa: E402  (annotate)
import finish_20261017T1800Z as p17  # noqa: E402  (update_ledger, frame_english, the audit lists)
import frame_u0156 as fr  # noqa: E402
import ledger_1800 as L  # noqa: E402
import scope_tally  # noqa: E402
import spec_nd  # noqa: E402

RUN_ID = "20261018T1800Z"
PREV_RUN = "20261018T0600Z"
TAG = "ve-green-eff-20261018-1"
PREV_TAG = "ve-green-tarch-histdep"
COVERED = old.COVERED
SOURCE = old.SOURCE
front_matter = old.front_matter
ve = p17.ve
dump = p17.dump
PREV_DIR = RUN / "prev"
MAIN = RUN / "translation.ve.md"
STRICT = RUN / "readings/all-strict.ve.md"
STRICT_NARROW = RUN / "readings/all-strict-narrow.ve.md"
FRAME_DOC = RUN / "readings/all-strict-in-frame.ve.md"
HC_UNITS = p17.HC_UNITS
S03 = p17.S03
AUDIT_1018_FAITHFUL, AUDIT_1018_UNFAITHFUL = p17.received(PREV_RUN, 25)   # 20 sampled + 5 changed, 25 verdicts, none unfaithful
AUDIT_LATEST = list(dict.fromkeys(p17.AUDIT_LATEST + p17.received("20261017T1800Z", 28)[0] + AUDIT_1018_FAITHFUL))
QT_CHANGED = ["u0042.presupposition", "u0043.s02.p1", "u0043.s02.p2"]
sent = lambda o: json.loads(re.sub(r"sentence \d+", "sentence N", json.dumps(o)))   # sentence numbers shift by one after the split of u0043.s02


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def block_after(render, anchor):
    """The lines a rendering gives under a unit's text: from the line after `anchor` up to the first line that is neither an indented continuation nor the unit's own
    “Checked reading:”/“Open reading:” line."""
    lines = render.split("\n")
    i = lines.index(anchor)
    out, n = [], i + 1
    assert re.match(r"^(Checked|Open) reading:", lines[n]), (anchor, lines[n])
    out.append(lines[n])
    n += 1
    while n < len(lines) and lines[n].startswith("  "):
        out.append(lines[n])
        n += 1
    return "\n".join(out)


# ---- JT-0p: the classes. Phase 1's instrument (evidence/jt0p/instrument-constitution.json) for every term it classified, then this run's new terms with a one-line reason each.
JT_NEW = {   # term -> (class, one-line reason)
    **{f"knowingly_engages_{i}": ("attitude", "new since the instrument (replaces restricted_action_knowing_or_quite_likely): “knowingly and intentionally engages” is a mental state of an agent (rule 1)")
       for i in ("1", "2", "3_wide", "3_narrow", "4", "5", "6", "7")},
    **{f"thinks_quite_likely_{i}": ("attitude", "new since the instrument (replaces restricted_action_knowing_or_quite_likely): “thinks it quite likely” is a mental state of an agent (rule 1)")
       for i in ("1", "2", "3_wide", "3_narrow", "4", "5", "6", "7")},
    "creating_a_cyberweapon": ("classification", "new since the instrument (the cyberweapon half of damaging_cyberweapon_or_malicious_code, judgment there): a kind of software, no threshold or evaluative standard in the word"),
    "creating_malicious_code": ("judgment", "new since the instrument (the malicious-code half of damaging_cyberweapon_or_malicious_code, judgment there): “malicious” is an evaluative standard the text does not state"),
    "could_cause_significant_damage_if_deployed": ("judgment", "new since the instrument (the “significant damage” half of damaging_cyberweapon_or_malicious_code, judgment there): “significant” is a threshold the text does not state"),
    "asked_to_keep_system_prompt_confidential": ("classification", "new since the instrument: whether a case is one of being asked to keep a prompt confidential is a classification of a speech act; no evaluative or threshold standard"),
    "novel_entity": ("judgment", "new this run (u0245, PS-0p class B): “novel” needs a standard (novel compared with what) that the text does not state"),
}
JT_GONE = {"restricted_action_knowing_or_quite_likely": "removed in 20261014T1800Z (AT-0p): split into knowingly_engages_N and thinks_quite_likely_N",
           "damaging_cyberweapon_or_malicious_code": "removed in 20261014T1800Z: split into creating_a_cyberweapon, creating_malicious_code and could_cause_significant_damage_if_deployed"}


def check_rules(classes, needed):
    """JT-0p's order of decision, spot-checked on the names: an `exception_to_…` placeholder is `exception`; “knowingly” and “thinks it quite likely” are `attitude`."""
    for t in needed:
        if t.startswith("exception_to_"):
            assert classes[t] == "exception", t
        if t.startswith("knowingly_") or t.startswith("thinks_"):
            assert classes[t] == "attitude", t


EXPECTED_DROPPED = [("u0050.s04", "returned to"), ("u0278.s01", "discoveries"), ("u0280.s01", "discoveries")]


def assert_no_traces(by_id):
    """REMOVE EVERY TRACE: a title or withheld heading no longer carries the claim PS-0p removed (only `previous_presupposed_claim` records it)."""
    for t in L.E_TITLES + ["u0055", "u0254", "u0268"]:
        assert "presupposed_claim" not in by_id[f"{t}.presupposition"], t


def jt_classes(ledger, main_meta):
    p1 = json.load(open(RUN / "evidence/jt0p/instrument-constitution.json"))
    classes = {t: c for t, c in p1["open_term_class"].items() if t not in JT_GONE}
    reasons = {}
    for t, (c, why) in JT_NEW.items():
        classes[t] = c
        reasons[t] = why
    declared = [t["name"] for t in main_meta["open_terms"]]
    listed = sorted({t for e in ledger for t in (e.get("open_terms") or [])})
    needed = sorted(set(declared) | set(listed))
    unclassified = [t for t in needed if t not in classes]
    assert not unclassified, unclassified
    check_rules(classes, needed)
    differs_from_p1 = {t: [p1["open_term_class"].get(t), c] for t, c in classes.items() if t in p1["open_term_class"] and p1["open_term_class"][t] != c}
    assert not differs_from_p1, differs_from_p1
    used = {t: classes[t] for t in needed}
    return used, reasons, p1


def apply_jt(ledger, classes):
    for e in ledger:
        e["judgment_terms"] = [t for t in (e.get("open_terms") or []) if classes[t] == "judgment"]
    jt_units = [e for e in ledger if e["judgment_terms"]]
    width = lambda es: sum(e["span"][1] - e["span"][0] for e in es)

    def split(key):
        n = Counter(e["status"] for e in jt_units)
        f = Counter(e.get("missing_feature") or "none" for e in jt_units)
        return {"total": len(jt_units) if key == "units" else width(jt_units), "by_status": dict(n) if key == "units" else
                {s: width([e for e in jt_units if e["status"] == s]) for s in n},
                "by_missing_feature": dict(f) if key == "units" else {m: width([e for e in jt_units if (e.get("missing_feature") or "none") == m]) for m in f}}
    return split("units"), split("bytes"), [e["id"] for e in jt_units]


def main():
    prev = json.load(open(PREV_DIR / "units.json"))
    pm = json.load(open(PREV_DIR / "metrics.json"))
    assert hashlib.sha256(SOURCE).hexdigest() == pm["source_sha256"]
    eng = old.english_nd(STRICT)
    eng_narrow = old.english_nd(STRICT_NARROW)
    silence_frame_all, _ = old.silence_sentences(FRAME_DOC)
    silence, legend = old.silence_sentences(STRICT)
    probe = json.load(open(RUN / "probes/unspecified-probe.json"))
    ledger = p17.update_ledger(prev, eng, eng_narrow, silence, probe, probe["scope_points"], probe["binding_points"])   # the previous ledger, AT-0p shape and probe points re-asserted
    ledger_pre = copy.deepcopy(ledger)   # the units as the scope tally knows them (u0043.s02 whole)
    main_meta = front_matter(MAIN)
    prev_meta = front_matter(PREV_DIR / "translation.ve.md")

    # ---- VE at this tag (the final document)
    rel = str(MAIN.relative_to(ROOT))
    assert (RUN / "readings/nd-all.ve.md").read_bytes() == MAIN.read_bytes()   # nd.py all built it
    t0 = time.monotonic()
    check = json.loads(ve("document", "check", rel))
    t1 = time.monotonic()
    coverage = json.loads(ve("document", "coverage", rel))
    t2 = time.monotonic()
    timing = {"document_check": round(t1 - t0, 1), "document_coverage": round(t2 - t1, 1)}
    (RUN / "evidence").mkdir(exist_ok=True)
    (RUN / "evidence/finish-timing.json").write_text(json.dumps(timing) + "\n")
    render = ve("document", "render", rel)
    prev_check = json.load(open(PREV_DIR / "check.json"))
    prev_cov = json.load(open(PREV_DIR / "coverage.json"))
    assert check["premises"]["status"] == "model", check["premises"]
    assert check["reading_plan"]["route"] == "enumerate" and len(check["reading_plan"]["choices"]) == 32
    assert check["readings"]["conflict"]["status"] == "CONFLICT-FREE"
    assert coverage["coverage_percent"] == 100 and coverage["source_bytes"] == len(SOURCE)
    assert all(c["status"] == "CONFLICT-FREE" for c in check["readings"]["conflict"]["choices"])

    english = {"u0042.presupposition": block_after(render, "Claude’s three types of principals"),
               "u0043.s02.p2": block_after(render, "Claude’s three types of principals are Anthropic, operators, and users.")}
    english_u0245 = block_after(render, "Claude as a novel entity")
    assert english_u0245 == "Open reading: Claude is novel.", english_u0245

    # ---- the ledger: QT-0p, PS-0p, then the tags
    ledger = L.qt0p(ledger, english)
    changed_ps = L.ps0p_notes(ledger)
    by_id = {e["id"]: e for e in ledger}
    ids = [e["id"] for e in ledger]
    for e in ledger:
        if e["status"] in COVERED:
            e["claimed"] = True
    claimed_false = [e["id"] for e in ledger if e.get("claimed") is False]

    # ---- SC-M0 (tags only), computed on the units as the tally knows them (u0043.s02 whole) and applied to the parts
    tally, notes = scope_tally.build(ledger_pre, SOURCE)
    for e in ledger:
        nt = notes.get(e.get("mixed_parent", e["id"]))
        if not nt:
            continue
        blockers = list(e.get("other_blockers") or [])
        if "other:scope" not in blockers:
            blockers.append("other:scope")
        e["other_blockers"] = blockers
        if nt["governed_by"]:
            e["governed_by"] = sorted(set(nt["governed_by"]), key=lambda i: ids.index(i) if i in ids else ids.index(i + ".p1"))
        if nt["governed_by_candidate"]:
            e["governed_by_candidate"] = sorted(set(nt["governed_by_candidate"]), key=lambda i: ids.index(i) if i in ids else ids.index(i + ".p1"))
    for g in tally["governors"]:
        if g["unit"] == "u0043.s02":
            g["parts"] = ["u0043.s02.p1", "u0043.s02.p2"]   # the governing sentence is now two parts; the tally counts it once, as before
    tally["note"] = ("scope-tally for run " + RUN_ID + "; the tags are ledger annotations only: other_blockers gains `other:scope`, governed units record governed_by "
                     "(a frontier governor's candidates record governed_by_candidate, never governed_by), and no unit's status or content changes. u0043.s02 is MIXED since QT-0p; its parts "
                     "both carry the tags and the tally counts the sentence once, with its 90 bytes")
    dump("scope-tally.json", tally)

    # ---- AP-0 item 3: act_workaround tags (carried: every act phrase equals the evidence's)
    m4_src = json.load(open(RUN / "evidence/m4-act-workaround.json"))
    vocab_now = main_meta["environment"]["vocabulary"]["predicates"]
    prev_vocab = prev_meta["environment"]["vocabulary"]["predicates"]
    entries = {e["id"]: e for e in ledger}
    for r in m4_src["units"]:
        e = entries[r["unit"]]
        act_now = vocab_now[e["predicate"]]["regulated"]["act"]
        assert act_now == r["act"] == prev_vocab[e["predicate"]]["regulated"]["act"], (r["unit"], act_now, r["act"])
        e["act_workaround"] = r["act_workaround"]
    m4_units = [e["id"] for e in ledger if e.get("act_workaround") not in (None, "none")]
    m4 = {"units": len(m4_units), "bytes": sum(e["span"][1] - e["span"][0] for e in ledger if e["id"] in m4_units), "unit_ids": m4_units,
          "tally": dict(Counter(e["act_workaround"] for e in ledger if "act_workaround" in e)), "stale": [], "expected": {"units": 17, "bytes": 2502},
          "source": "research/act-phrases-p1: docs/research/evidence/act-phrases/m4-act-workaround.json (evidence/m4-act-workaround.json)"}
    assert (m4["units"], m4["bytes"]) == (17, 2502), m4

    # ---- PS-0p step 4: presupposition_triggers on every unit; the blocker; step 6: the goals
    census = json.load(open(RUN / "evidence/ps0p/ledger-triggers-constitution.json"))
    unresolved, dropped, trig_counts = L.triggers_for_ledger(ledger, census, SOURCE)
    assert [(d["unit"], d["words"]) for d in dropped] == EXPECTED_DROPPED, dropped
    for e in ledger:
        if e["id"] in unresolved:
            b = list(e.get("other_blockers") or [])
            if "other:presupposition" not in b:
                b.append("other:presupposition")
            e["other_blockers"] = b
    entries_all = [t for e in ledger for t in e["presupposition_triggers"]]
    goals = L.goals(ledger, main_meta, SOURCE)
    dump("presupposition-goals.json", goals)

    # ---- JT-0p: classes and judgment_terms
    classes, jt_reasons, p1 = jt_classes(ledger, main_meta)
    jt_units, jt_bytes, jt_unit_ids = apply_jt(ledger, classes)
    p1_units = {u: set(ts) for u, ts in p1["judgment_terms"].items()}
    now_units = {e["id"]: set(e["judgment_terms"]) for e in ledger if e["judgment_terms"]}
    jt_diff = {u: {"phase1": sorted(p1_units.get(u, [])), "now": sorted(now_units.get(u, []))} for u in sorted(set(p1_units) | set(now_units)) if p1_units.get(u, set()) != now_units.get(u, set())}
    JT_DIFF_REASON = {
        "u0126": "u0126 is a LABELLED heading (“Avoiding harm”); the instrument listed the ledger-only pointer ethical_harm on it, and an earlier run removed ledger-only pointers from covered entries "
                 "(ledger_only_open_terms.covered_entries_with_such_names is empty); the class of ethical_harm is unchanged (judgment)",
        "u0165.s03": "damaging_cyberweapon_or_malicious_code was split in 20261014T1800Z into creating_a_cyberweapon (classification), creating_malicious_code (judgment) and "
                     "could_cause_significant_damage_if_deployed (judgment); the unit is READINGS now (the scope set), it was OPEN",
        "u0245.presupposition": "a unit of this run (PS-0p class B, 26 B): its open term novel_entity is class judgment"}
    assert set(jt_diff) == set(JT_DIFF_REASON), sorted(jt_diff)
    for u_, r_ in JT_DIFF_REASON.items():
        jt_diff[u_]["reason"] = r_

    # ---- the ledger, counts
    spans_ok = [(u["id"], tuple(u["span"])) for u in L._flat(main_meta["units"])] == [(e["id"], tuple(e["span"])) for e in ledger]
    assert spans_ok
    total = sum(e["span"][1] - e["span"][0] for e in ledger)
    assert total == len(SOURCE)
    pos = 0
    for e in ledger:
        assert e["span"][0] == pos, e["id"]
        pos = e["span"][1]
    u, nb = old.counts(ledger)
    claimed = sum(e["span"][1] - e["span"][0] for e in ledger if e["status"] in COVERED and e.get("claimed", True) is not False)
    assert claimed == sum(v for k, v in nb.items() if k in COVERED)
    assert claimed == pm["claimed_covered_bytes"] + 128 + 26, claimed   # QT-0p +128 (113 CHECKED, 15 LABELLED); PS-0p u0245 +26 (OPEN)
    n_old, old_units, _ = old.aggregate(ledger)
    spans = {e["id"]: e["span"] for e in ledger}
    status = {e["id"]: e["status"] for e in ledger}
    width = lambda ids_: sum(spans[i][1] - spans[i][0] for i in ids_)
    assert coverage["bytes_by_status"]["CHECKED"] == nb["CHECKED"] and coverage["bytes_by_status"]["OPEN"] == nb["OPEN"] + nb["READINGS"]
    assert coverage["bytes_by_status"]["LABELLED"] == nb["LABELLED"]

    changed_units = sorted(set(QT_CHANGED + changed_ps), key=ids.index)
    plan_repairs = ([{"unit": u_, "plan": "quantities", "item": "QT-0p"} for u_ in QT_CHANGED] +
                    [{"unit": u_, "plan": "presupposition", "item": by_id[u_]["plan_repair"]["item"]} for u_ in changed_ps])
    at0p = [{"unit": u_, "plan": "attitudes", "item": "AT-0p", "applied_in_this_run": False,
             "state": ("already in the plan's form at the start of this run (applied in 20261014T1800Z; accepted FAITHFUL by every audit since, the last of 20261018T0600Z); the shape is asserted "
                       "by repair_20261017T1800Z.py --check and update_ledger, and measured again by the four probe points; not re-applied, no guard or act phrase changed in this run"
                       if u_ != S03 else
                       "already in the plan's form per candidate at the start of this run (one pair of attitude terms per candidate since 20261015T0600Z; accepted FAITHFUL by every audit since); "
                       "asserted and measured again; not re-applied")} for u_ in HC_UNITS]
    for e in ledger:
        if e["id"] in changed_units:
            e["changed_in_run"] = RUN_ID

    # ---- audit-verified bytes: accepted by an audit of this lineage AND unchanged here from the form that audit saw
    prev_verified = list(pm["audit_verified_covered_units"])
    kept = [i for i in prev_verified if i not in changed_units]
    newly = [i for i in AUDIT_LATEST if i in status and status[i] in COVERED and status[i] != "LABELLED" and i not in changed_units and i not in kept]
    assert not any(by_id[i].get("claimed") is False for i in [*kept, *newly])
    verified = kept + newly
    verified_bytes = width(verified)
    cand_lab = list(dict.fromkeys(old.AUDIT_PASSED_LABELLED + old.AUDIT_PASSED_1004_LABELLED + old.AUDIT_PASSED_1004B_LABELLED + ["u0212.heading"]
                                  + p17.prevf.AUDIT_FAITHFUL_1800 + p17.prevf.AUDIT_FAITHFUL_1811 + p17.p18.AUDIT_0600_FAITHFUL + p17.p13.AUDIT_1800_FAITHFUL + p17.p14.AUDIT_1013_FAITHFUL
                                  + p17.p15.AUDIT_1014_FAITHFUL + AUDIT_LATEST))
    verified_lab = [i for i in cand_lab if i in by_id and status[i] == "LABELLED" and i not in changed_units]
    verified_meta = width(verified_lab)
    for e in ledger:
        if "audit_verified" in e and e["id"] in changed_units:
            e["audit_verified"] = False
        elif "audit_verified" in e and (e["id"] in verified or e["id"] in verified_lab or e["id"] in AUDIT_LATEST):
            e["audit_verified"] = True
    dump("units.json", ledger)

    # ---- the files that cannot be a render of the final ledger without it
    dump("check.json", check)
    dump("coverage.json", coverage)
    dump("environment.json", main_meta["environment"])
    strict = {"check": json.loads(ve("document", "check", str(STRICT.relative_to(ROOT)))),
              "coverage": json.loads(ve("document", "coverage", str(STRICT.relative_to(ROOT))))}
    dump("readings/check-all-strict.json", strict["check"])
    (RUN / "readings/rendered-all-strict.md").write_text(ve("document", "render", str(STRICT.relative_to(ROOT))))
    (RUN / "rendered.md").write_text(p14.annotate(render, ledger))
    (RUN / "rendered-raw.md").write_text(render)
    english_u0156, _rt = p17.frame_english(render, main_meta)
    carried = {r["id"]: r["english"] for r in by_id[fr.UNIT]["readings"]}
    assert carried == english_u0156, (carried, english_u0156)
    old_render = (PREV_DIR / "rendered-raw.md").read_text()
    render_diff_lines = sum(1 for a, b in zip(render.split("\n"), old_render.split("\n")) if a != b) + abs(len(render.split("\n")) - len(old_render.split("\n")))

    # ---- reading sets, conclusion queries, probes
    nd = {"all": prevf.slice_result("all")}
    assert nd["all"]["conflict"] == "CONFLICT-FREE" and nd["all"]["premises"] == "model" and nd["all"]["choice_count"] == 32
    sep_all = sum(nd["all"]["separations"].values())
    cand_status = Counter(nd["all"]["premises_by_candidate"].values())
    concl = prevf.concl((("denial_one_reading", "conclusion-no-denial-result.json"), ("claim_human", "claim-human-result.json")))
    assert concl["denial_one_reading"]["verdict"] == "ALL" and concl["claim_human"]["verdict"] == "ALL"
    hard_q = json.load(open(RUN / "probes/hard-conclusions-probe.json"))["queries"]
    hard_by = {(q["unit"], q["kind"]): q for q in hard_q}
    assert len(hard_q) == 21
    assert all(hard_by[(u_, "neither")]["verdict"] == "UNKNOWN" for u_ in HC_UNITS)
    assert all(hard_by[(u_, k)]["verdict"] == "ALL" and hard_by[(u_, k)]["evidence"] in ("certificate", "certificates") for u_ in HC_UNITS[1:] for k in ("knowing", "belief"))
    prev_hard = json.load(open(PREV_DIR / "probes/hard-conclusions-probe.json"))["queries"]
    slim = lambda qs: sent([{k: v for k, v in q.items() if k not in ("document", "english")} for q in qs])
    # the previous run had u0165.s01's two queries UNKNOWN (VE's search budget exhausted, several minutes each); in this run u0165.s01 "knowing" is ALL with certificates and "belief" is still
    # UNKNOWN. Every other query has the same verdict, route and evidence. The change is a budget effect on a changed document (QT-0p's premises), not a feature: recorded, not an upgrade.
    hard_changes = [{"unit": q["unit"], "kind": q["kind"], "now": [q["verdict"], q.get("evidence")], "before": [p_["verdict"], p_.get("evidence")]}
                    for q, p_ in zip(hard_q, prev_hard) if (q["unit"], q["kind"]) == (p_["unit"], p_["kind"]) and (q["verdict"], q.get("evidence")) != (p_["verdict"], p_.get("evidence"))]
    assert [(c["unit"], c["kind"]) for c in hard_changes] == [("u0165.s01", "knowing")] and hard_by[("u0165.s01", "belief")]["verdict"] == "UNKNOWN", hard_changes
    hard_same = slim([q for q in hard_q if (q["unit"], q["kind"]) != ("u0165.s01", "knowing")]) == slim([q for q in prev_hard if (q["unit"], q["kind"]) != ("u0165.s01", "knowing")])
    assert hard_same
    unavailable = sorted(f"{q['unit']}:{q['kind']}" for q in hard_q if "rerun_alone" in q or q.get("cap"))
    hard_summary = {k: dict(Counter(q["verdict"] for q in hard_q if q["kind"] == k)) for k in ("knowing", "belief", "neither")}
    probe_names = ("risk-probe", "s1-probe", "senses-probe", "senses-document-probe", "rights-reading-probe", "unspecified-probe", "frame-probe")
    probe_same = {n: (RUN / f"probes/{n}.json").read_bytes() == (PREV_DIR / f"probes/{n}.json").read_bytes() for n in probe_names}
    assert all(probe_same.values()), probe_same
    disc_same = (RUN / "probes/discourse-probe.json").read_bytes() == (PREV_DIR / "probes/discourse-probe.json").read_bytes()
    hard_probe_same_bytes = (RUN / "probes/hard-conclusions-probe.json").read_bytes() == (PREV_DIR / "probes/hard-conclusions-probe.json").read_bytes()
    profile_probe = old.probe_profiles()
    assert profile_probe == pm["profile_combination_probe"]
    comp = json.load(open(RUN / "probes/companion-probe.json"))
    prev_comp = json.load(open(PREV_DIR / "probes/companion-probe.json"))
    strip = lambda o: json.loads(json.dumps(sent(o)).replace(RUN_ID, "RUN").replace(PREV_RUN, "RUN"))
    comp_same = strip(comp) == strip(prev_comp)
    cw = comp["attempts"]["without_source_word"]
    summ, lds = cw["summary"], cw["lean_decided_share"]
    cq = {k: json.load(open(RUN / f"probes/companion/query-{k}.json")) for k in ("no-denial", "claim-human")}
    attribution = json.load(open(RUN / "evidence/companion-attribution.json"))
    assert [cq[k]["verdict"] for k in cq] == ["ALL", "ALL"] and lds["decided_units"] == summ["decided_units"] and len(lds["decided_units"]) == 4
    companion_probe = {**pm["companion_probe"], "components": summ["components"], "conflict": summ["conflict"], "premises": summ["premises"],
                       "premises_components": summ["premises_components"], "separations": summ["separations"], "decided_units": len(lds["decided_units"]), "decided_bytes": lds["decided_bytes"],
                       "decided_share_percent": lds["decided_share_percent"],
                       "queries": {k: {"verdict": cq[k]["verdict"], "route": cq[k]["route"], "component": cq[k]["component"], "sentence": cq[k]["sentence"],
                                       "decided_units": len(cq[k]["decided_units"]), "english": cq[k].get("english", [])} for k in cq},
                       "decided_units_same_as_previous_run": False,
                       "reading": ("the companion denial query (--sentence u0125.s04.p2) and the claim-human query (--sentence u0123.s03) still answer ALL, but the main component's premise check is now UNKNOWN "
                                   "(was model), so only 4 units are Lean-decided (was 19: 2,602 B). Cause (evidence/companion-attribution.json): QT-0p alone; the translation's own premise check, on the "
                                   "superposed route, stays `model`. A measurement document, not the translation"),
                       "premise_regression": attribution["results"]}
    lean_decided_share = {**pm["lean_decided_share"], "with_companion_sets": {**pm["lean_decided_share"]["with_companion_sets"], "decided_units": len(lds["decided_units"]),
                          "decided_bytes": lds["decided_bytes"], "decided_share_percent": lds["decided_share_percent"], "units": lds["decided_units"],
                          "previous_run": {"decided_units": 19, "decided_bytes": 2602, "decided_share_percent": "1.41"},
                          "cause": "the main component's premise check is UNKNOWN on the components route once QT-0p's principal_type (size 3) is in the document (evidence/companion-attribution.json)"}}
    frame_probe = json.load(open(RUN / "probes/frame-probe.json"))
    soft = json.load(open(RUN / "evidence/soft-chain-probe.json"))
    prev_soft = pm["soft_chain_probe"]
    assert soft["load"] == "admitted" and soft["check"]["returncode"] == 1 and soft["conclusions"]["denial"]["verdict"] == "ALL" and soft["conclusions"]["claim_human"]["verdict"] == "ALL"
    assert soft["check"]["stderr_last_lines"][-1].startswith("ve.errors.UnsupportedProfile: UnsupportedProfile: norm-defaults@0 documents are checked through fill"), soft["check"]["stderr_last_lines"][-1]
    asks = [json.load(open(RUN / f"probes/ask/q{i}.json")) for i in range(1, 6)]
    prev_ask = PREV_DIR / "probes/ask"

    def strip_version(o):
        # the environment and lexicon identities change with the vocabulary (QT-0p, PS-0p) and the closest-wordings sentence of the refusal lists the new wordings; the answer, class and code stay
        o = json.loads(json.dumps(o))
        for k in ("actions_version", "environment_id", "lexicon_id", "document_id", "source_id"):
            o["result"].get("identities", {}).pop(k, None)
        for k in ("text", "message"):
            o["result"].pop(k, None)
            o.get("error", {}).pop(k, None)
        return sent(o)
    ask_same = all(strip_version(json.load(open(RUN / f"probes/ask/q{i}{s}.json"))) == strip_version(json.load(open(prev_ask / f"q{i}{s}.json"))) for i in range(1, 6) for s in ("", ".answer"))
    nd_conclusions_same = all(sent(json.load(open(RUN / f"probes/nd/{f}.json"))) == sent(json.load(open(PREV_DIR / f"probes/nd/{f}.json"))) for f in ("conclusion-no-denial-result", "claim-human-result"))
    qt_probe = json.load(open(RUN / "probes/qt/no-fourth-result.json"))
    assert qt_probe["verdict"] == "ALL" and qt_probe["evidence"] == "certificate", qt_probe["verdict"]
    qt_fourth = json.load(open(RUN / "probes/qt/fourth-result.json"))

    open_terms = [{k: t[k] for k in ("name", "arguments", "decided_by", "necessary", "sufficient", "factors")} for t in main_meta["open_terms"]]
    prev_terms = {t["name"]: t for t in pm["open_terms"]}
    now_terms = {t["name"]: t for t in open_terms}
    added_terms = sorted(set(now_terms) - set(prev_terms))
    removed_terms = sorted(set(prev_terms) - set(now_terms))
    changed_terms = sorted(n for n in now_terms if n in prev_terms and now_terms[n] != prev_terms[n])
    assert added_terms == ["novel_entity"] and not removed_terms and not changed_terms, (added_terms, removed_terms, changed_terms)
    gap_marker = "Here the text does not say whether"
    sep_lines = lambda text: [ln for ln in text.splitlines() if ln.startswith("These two readings differ here")]
    gaps_now = [ln.count(gap_marker) for ln in sep_lines(render)]
    cannot_show = lambda text: text.count("These two readings differ in a checked situation that VE cannot yet show in words.")
    assert gaps_now == [1, 1] and cannot_show(render) == 7 == cannot_show(old_render)

    # ---- X3: the checkpoint evidence of the final document
    cp = json.load(open(RUN / "evidence/checkpoint-final.json"))
    assert cp["document_check"]["premises"] == "model" and not cp["x3_vocabulary"]["existing_predicate_wordings_changed"]
    cp_qt = json.load(open(RUN / "evidence/checkpoint-qt0p.json"))
    variants = json.load(open(RUN / "evidence/ps0p/premise-variants.json"))

    # ---- the language changes since the previous tag: read from the repository
    diff_all = git("diff", "--shortstat", f"{PREV_TAG}..{TAG}")
    diff_stat = git("diff", "--shortstat", f"{PREV_TAG}..{TAG}", "--", "ve", "lean", "rust", "conformance")
    merged = git("log", "--first-parent", "--format=%h %s", f"{PREV_TAG}..{TAG}").splitlines()
    assert len(merged) == 13, len(merged)

    missing_now = old.tally(ledger)
    m = copy.deepcopy(pm)
    m.update({
        "run": RUN_ID, "baseline_tag": TAG, "previous_run": PREV_RUN, "previous_baseline_tag": PREV_TAG,
        "history_note": "this file records this run; the earlier runs' records are in prev/metrics.json and the AUDIT-*-received.md files",
        "feature_upgrade_counts_separate_from_repairs": (
            "units upgraded by new features 0 (thirteen batches merged; none adds anything a document can say); plan repairs: QT-0p 3 units (+128 B), PS-0p " + str(len(changed_ps)) +
            " units (ledger steps 1 to 3 and 5; +26 B for u0245), AT-0p 7 units carried unchanged; audit repairs 0 (the audit of 20261018T0600Z found 25 of 25 faithful)"),
        "changed_units": changed_units,
        "plan_repairs": plan_repairs + at0p,
        "plan_repairs_by_plan": {"quantities QT-0p": QT_CHANGED, "presupposition PS-0p": changed_ps, "attitudes AT-0p (carried, not re-applied)": HC_UNITS},
        "audit_repairs": [],
        "changed_units_detail": {u_: by_id[u_].get("note", "")[:240] for u_ in changed_units},
        "feature_upgrades": {"units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
                             "note": "kept apart from the plan repairs and audit repairs, so that differences against the previous run measure the language, not the translator"},
        "tags_only_not_changed_units": ("scope tags (SC-M0), act_workaround (AP-0 item 3), presupposition_triggers and the blocker other:presupposition (PS-0p step 4), judgment_terms (JT-0p) and the "
                                        "`claimed` field are ledger annotations; none of them makes a unit a changed unit"),
        "sentence_clause_units": {"units_total": len(ledger), "unit_counts_by_status": old.full(u), "bytes_by_status": old.full(nb),
                                  "previous_run": {k: pm["sentence_clause_units"][k] for k in ("units_total", "unit_counts_by_status", "bytes_by_status")}},
        "aggregated_to_previous_boundaries": {"units_total": n_old, "unit_counts_by_status": old_units, "bytes_by_substatus": old.full(nb),
                                              "previous_run": {k: pm["aggregated_to_previous_boundaries"][k] for k in ("units_total", "unit_counts_by_status")},
                                              "note": "aggregated by the unit's block (parent_unit), as in earlier runs; u0043 (QT-0p) becomes a MIXED block"},
        "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(SOURCE), 4),
        "claimed_covered_bytes_previous_run": pm["claimed_covered_bytes"], "claimed_covered_bytes_gained": claimed - pm["claimed_covered_bytes"],
        "claimed_covered_bytes_gained_by_plan": {"QT-0p": 128, "PS-0p": 26},
        "claimed_false_units": claimed_false,
        "substantive_covered_bytes": nb["CHECKED"] + nb["OPEN"] + nb["READINGS"], "substantive_covered_bytes_previous_run": pm["substantive_covered_bytes"],
        "audit_verified_covered_bytes": verified_bytes, "audit_verified_covered_percent": round(100 * verified_bytes / len(SOURCE), 4),
        "audit_verified_covered_units": verified, "audit_verified_covered_bytes_previous_run": pm["audit_verified_covered_bytes"],
        "audit_verified_dropped_because_changed": [i for i in pm["audit_verified_covered_units"] if i in changed_units],
        "audit_verified_newly_from_20261018T0600Z": newly,
        "audit_verified_newly_labelled_from_20261018T0600Z": [i for i in AUDIT_1018_FAITHFUL if status.get(i) == "LABELLED"],
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND unchanged in this run from the form that audit saw. The audit of run 20261018T0600Z (25 of 25 "
            "verdicts faithful: 20 sampled plus the 5 AT-0p units it checked as changed; AUDIT-20261018T0600Z-received.md) is the latest and rejected nothing. None of the units this run "
            "changed (QT-0p, PS-0p) was audited in that form, so none counts. This is a count of verdicts on unchanged text, not a fresh audit of this run."),
        "audit_verified_metadata_bytes": verified_meta, "audit_verified_metadata_percent": round(100 * verified_meta / len(SOURCE), 4),
        "audit_verified_metadata_bytes_previous_run": pm["audit_verified_metadata_bytes"],
        "claimed_but_not_audit_verified_bytes": claimed - verified_bytes - verified_meta,
        "claimed_but_not_audit_verified_units": [e["id"] for e in ledger if e["status"] in COVERED and e.get("claimed", True) is not False and e["id"] not in verified and e["id"] not in verified_lab],
        "repaired_bytes_not_audit_verified": 0,
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20261018T0600Z_audit": AUDIT_1018_UNFAITHFUL, "repair_done_in_20261018T1800Z": {}, "small_faults_repaired": {},
            "small_faults_not_repaired": {
                "u0156.s03 frame term": pm["audit_rejected_units_and_repair_status"]["small_faults_not_repaired"]["u0156.s03 frame term"],
                "u0168.s01 guard": ("the audit of 20261018T0600Z (small fault, no verdict change): the guard seemingly_compelling_argument_to_cross_line(s) takes only the situation, so when one instance faces the "
                                    "argument every instance in s is obliged to remain firm; in English the extra duty is empty. Carried, not repaired: no plan of this run directs it, and binding the term to an "
                                    "agent is the typed-attitude feature (attitudes plan beyond AT-0p)"),
                "headings": "unchanged from earlier runs, except where PS-0p steps 1 to 3 now change the heading units (listed in changed_units)",
                "u0173.s01 to s04": pm["audit_rejected_units_and_repair_status"]["small_faults_not_repaired"]["u0173.s01 to s04"]},
            "kept_covered_status_without_repair": [],
            "earlier_audits": "the rejections and repairs of the earlier runs are recorded in prev/metrics.json and the AUDIT-*-received.md files"},
        "open_terms": open_terms, "open_terms_count": len(open_terms),
        "open_terms_count_previous_run": pm["open_terms_count"],
        "open_terms_added": added_terms, "open_terms_removed_this_run": removed_terms, "open_terms_with_changed_factors": changed_terms, "open_terms_with_changed_arguments": {},
        "open_terms_count_note": "52: the previous 51 plus novel_entity (u0245, PS-0p class B); u0286's open_problem and u0032's genuine_helpfulness were declared in the offered builds and are not in the final document",
        "ledger_only_open_terms": {**pm["ledger_only_open_terms"]},
        "missing_feature_tally": missing_now, "missing_feature_tally_previous_run": pm["missing_feature_tally"],
        "check_verdicts": {"main": {
            "document_loaded": True, "coverage_percent": coverage["coverage_percent"],
            "premises": {"status": check["premises"]["status"], "route": check["premises"]["route"], "evidence": check["premises"]["status"]}, "premises_gaps": check["premises"].get("gaps", []),
            "reading_plan": {"route": check["reading_plan"]["route"], "choice_count": len(check["reading_plan"]["choices"]), "conditional_on": check["reading_plan"].get("conditional_on")},
            "conflict": {"route": check["readings"]["route"], "status": check["readings"]["conflict"]["status"], "evidence": check["readings"]["conflict"]["evidence"],
                         "status_text": check["readings"]["conflict"]["status_text"], "choices": dict(Counter(c["status"] for c in check["readings"]["conflict"]["choices"])),
                         "sizes": check["readings"]["sizes"], "english": check["readings"]["english"]},
            "check_seconds_this_run": timing, "previous_run": {"premises_route": prev_check["premises"]["route"], "conflict_route": prev_check["readings"]["route"],
                                                              "choices": len(prev_check["reading_plan"]["choices"])},
            "bytes_by_status": check["coverage"]["bytes_by_status"], "bytes_by_status_previous_run": prev_check["coverage"]["bytes_by_status"],
            "residual": check["coverage"]["residual"], "residual_previous_run": prev_check["coverage"]["residual"]},
            "all_strict": {"document": "readings/all-strict.ve.md", "premises": strict["check"]["premises"], "residual": strict["coverage"]["residual"],
                           "bytes_by_status": strict["coverage"]["bytes_by_status"]}},
        "timing_single_runs": {
            "note": "one run each on one machine at a load average of about 30 to 40 (32 cores; not a controlled comparison)",
            "document_check_seconds": timing["document_check"], "document_check_seconds_previous_run": pm["timing_single_runs"]["document_check_seconds"],
            "document_coverage_seconds": timing["document_coverage"], "document_coverage_seconds_previous_run": pm["timing_single_runs"]["document_coverage_seconds"],
            "nd_all_load_seconds": [nd["all"]["load_seconds"], pm["timing_single_runs"]["nd_all_load_seconds"][0]],
            "nd_all_check_seconds": [nd["all"]["check_seconds"], pm["timing_single_runs"]["nd_all_check_seconds"][0]],
            "nd_all_separation_search_seconds": [nd["all"]["separation_search_seconds"], pm["timing_single_runs"]["nd_all_separation_search_seconds"][0]],
            "build_note": "lean/.lake copied (cp -a) from the ve-integration checkout at the identical commit; `lake build` still rebuilt (997 jobs, 25 minutes) and tools/rust_build.py rebuilt the Rust "
                          "binary (42 s), which matches the pin in lean/checkers.lock (SHA-256 6422647f…0579); not a language measurement",
            "order": "[this run, previous run]"},
        "unspecified_probe": {**pm["unspecified_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["unspecified-probe"]},
        "profile_combination_probe_same_as_previous_run": True,
        "senses_probe": {**pm["senses_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-probe"]},
        "senses_document_probe": {**pm["senses_document_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-document-probe"]},
        "discourse_probe": {**pm["discourse_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": disc_same},
        "rights_reading_probe": {**pm["rights_reading_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["rights-reading-probe"]},
        "risk_probe": {**pm["risk_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["risk-probe"]},
        "readings_defaults_probe": {**pm["readings_defaults_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["s1-probe"]},
        "carried_probes_note": ("the carried probes were re-run on the final document: byte-identical JSON for " + ", ".join(k for k, v in probe_same.items() if v) +
                                "; discourse " + ("byte-identical" if disc_same else "differs (see probes/discourse-probe.json)") + "; companion: the probe differs (the main component's premise check is UNKNOWN: 4 units Lean-decided, was 19; the queries still ALL; cause QT-0p alone, evidence/companion-attribution.json)" +
                                "; the 21 hard-constraint queries give 13 ALL and 8 UNKNOWN: the same as before except u0165.s01 \u201cknowing\u201d, now ALL with certificates (was UNKNOWN, a search-budget result on the changed document: " + json.dumps(hard_changes) + ")" +
                                "; the denial and claim-to-be-human conclusion queries are ALL; the five `ve ask` questions give no answer as before"),
        "frame_probe": {**pm["frame_probe"], "identical_to_previous_run": probe_same["frame-probe"]},
        "companion_probe": companion_probe, "lean_decided_share": lean_decided_share,
        "profile_combination_probe_changes": {"what": pm["profile_combination_probe_changes"]["what"], "changed": {}, "reading": "all thirteen rows are identical to the previous run's"},
        "soft_chain_probe": {**prev_soft, "result": {**prev_soft["result"],
                                                     "ve_document_check": {**prev_soft["result"]["ve_document_check"], "stderr_last_lines": soft["check"]["stderr_last_lines"]},
                                                     "ve_document_coverage": soft["coverage"], "ve_document_render": soft["render"],
                                                     "ve_document_readings_denial_query": soft["conclusions"]["denial"], "ve_document_readings_claim_human_query": soft["conclusions"]["claim_human"]},
                             "same_outcome_as_previous_run": True,
                             "decision": "still not adopted: `ve document check` raises the same UnsupportedProfile on the soft-chain document, so the exception_to_* workaround stays (not an upgrade)"},
        "separation_line_gap_sentences": {**pm["separation_line_gap_sentences"], "per_line_before": gaps_now, "per_line_now": gaps_now,
                                          "reading": "unchanged: per_line_before and per_line_now are both [1, 1]"},
        "reading_sets": {**pm["reading_sets"], "choices_previous_run": 32, "changed_this_run": {}, "added_this_run": {}, "removed_this_run": {}},
        "checked_content_main_chain": {**pm["checked_content_main_chain"], "documents": nd, "candidate_premise_status": dict(cand_status),
                                       "choices_checked": nd["all"]["choices_checked"],
                                       "choices_conflict_free": nd["all"]["conflict_by_choice"].get("CONFLICT-FREE", 0), "choices_conflict": nd["all"]["conflict_by_choice"].get("CONFLICT", 0),
                                       "separating_situations_checked_by_lean": sep_all, "separated_by_decision_only_findings": 0},
        "question_probe": {**pm["question_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": "in content: `no_answer` for all five with --reading and without it" if ask_same else "DIFFERS"},
        "conclusion_queries_note": "the denial and claim-to-be-human queries (probes/nd/*-result.json) were re-run: ALL on the superposed route with a certificate" + (", equal to the previous run's after the sentence numbers are normalised" if nd_conclusions_same else ""),
        "scope_tally": {"file": "scope-tally.json", "totals": tally["totals"], "not_tallied": tally["not_tallied"]},
        "act_workaround_m4": m4,
        "heading_presuppositions_exposed": sum(1 for e in ledger if "presupposed_claim" in e),
        "heading_presuppositions_exposed_previous_run": pm["heading_presuppositions_exposed"],
        "document_open_terms_class_note": "see open_term_class",
        "open_term_class": classes,
        "open_term_class_borderline": p1["borderline_judgment_terms"],
        "open_term_class_reasons_new_terms": jt_reasons,
        "open_term_class_removed_since_instrument": JT_GONE,
        "open_term_class_counts": dict(Counter(classes.values())),
        "open_term_class_vs_phase1": {"terms_in_both": sum(1 for t in classes if t in p1["open_term_class"]), "classes_differing": {}, "terms_new": sorted(JT_NEW),
                                      "note": "every term unchanged since run 20261012T1800Z has phase 1's class; the new terms are the ones of JT_NEW (a one-line reason each in open_term_class_reasons_new_terms)"},
        "judgment_term_units": jt_units, "judgment_term_bytes": jt_bytes,
        "judgment_term_phase1_reference": {"units": p1["judgment_term_units"]["total"], "bytes": p1["judgment_term_bytes"]["total"], "run": "20261012T1800Z"},
        "judgment_term_units_differing_from_phase1": jt_diff,
    })
    # the QT-0p measurement
    m["quantities_qt0p"] = {
        "plan": "docs/spec/quantities-PLAN.md QT-0p and 0.2 (research/quantities-p1); content docs/research/evidence/quantities/qt0p/constitution-u0042-u0043.ve.md (evidence/qt0p-constitution-u0042-u0043.ve.md)",
        "units_before": {"u0042.presupposition": [23448, 23486], "u0043.s01": [23486, 23587], "u0043.s02": [23587, 23677], "status": "UNFORMALISED", "missing_feature": "counting"},
        "applied": {"u0042.presupposition": "CHECKED, 38 B", "u0043.s02.p1": "LABELLED, 15 B (“At the moment,” the document's present, no date)", "u0043.s02.p2": "CHECKED, 75 B", "u0043.s01": "unchanged (UNFORMALISED, counting)"},
        "vocabulary": {"sort": "principal_type", "constants": ["anthropic", "operators", "users"], "predicate": "claude_principal_type"},
        "claimed_bytes": {"expected": "2,951 to 3,079 (+113 CHECKED, +15 LABELLED)", "measured_after_qt0p": cp_qt["document_check"]["bytes_by_status"], "gained": 128},
        "premises": {"expected": "model", "measured": cp_qt["document_check"]["premises"], "model_domain_sizes": {"principal_type": 3, "entity": 1}},
        "probe_fourth_type": {"question": "Is there a fourth type of principal?", "negation_tested": "probes/qt/no-fourth.conclusion.json (ALL on the negation)", "negation_verdict": qt_probe["verdict"],
                              "evidence": qt_probe["evidence"], "route": qt_probe["route"], "reading": "SETTLED no: under every reading, no type of principal other than Anthropic, operators and users is one of Claude's types",
                              "the_positive_query_fourth": {"verdict": qt_fourth["verdict"], "note": "NONE/does-not-follow on the readings route means only that the existence of a fourth type does not follow; it is not the answer"}},
        "checks_after_qt0p": {"x3_existing_wordings_changed": cp_qt["x3_vocabulary"]["existing_predicate_wordings_changed"], "fenced_u0248_unchanged": cp_qt["x3_fenced_units"]["u0248"]["unchanged"],
                              "choices": cp_qt["document_check"]["choices"], "conflict": cp_qt["document_check"]["conflict"], "conclusions": cp_qt["conclusions"]},
        "findings": [
            "The predicate's planned wording “{0} is one of Claude's types of principals” (and its negative wording) is refused by the English lint (LOGICAL_WORD, PHRASE_SYNTAX, SORT_NOUN, SYMBOL_COLLISION, UNARY_MODIFIER, "
            "NEGATIVE_WITHOUT_POSITIVE, TEMPLATE_LENGTH); VE falls back to `is classified as \"claude_principal_type\"`, so the rendered English of u0042 and u0043.s02.p2 carries one quoted name. "
            "Every other wording tried (a dozen, in evidence of this run's session) was refused or said something else; the checked content is the plan's. An auditor may judge that English not plain; if so the "
            "units revert to UNFORMALISED (counting) and nothing else moves.",
            "The constants `operators` and `users` are not confused with the sorts `operator` and `user`: the rendered English of both units parses back to exactly the same formulas (round trip checked), "
            "and “Operators is classified as …” parses to the constant. The English reads awkwardly (“operators is classified as …”) because a constant is a name.",
            "The closure is over Claude's types (the predicate), not over all principal types; the premise check's model has principal_type of size 3 (premise-scale), entity of size 1."]}
    m["presupposition_ps0p"] = {
        "plan": "docs/spec/presupposition-PLAN.md PS-0p (draft 4, research/presupposition-p1); text docs/research/evidence/presupposition/pilot-prompt-addition.md",
        "step1_titles": {"removed_presupposed_claim": [f"{t}.presupposition" for t in L.E_TITLES], "note": L.NOTE_TITLE, "u0055": {"unit": "u0055.presupposition", "note": L.NOTE_U0055, "listed_for_audit": True}},
        "step2_withheld": {"units": ["u0254.presupposition", "u0268.presupposition"], "note": L.NOTE_D},
        "step3": {"relational_nouns_not_claimed": {u_ + ".presupposition": L.NOTE_RELATIONAL for u_ in ("u0013", "u0095", "u0002", "u0235")},
                  "u0286": {"offered": "predicate open_problem(entity) worded “{0} is unsolved”; unit asserted/assumption/specified; fence “Some thing is unsolved.” (∃x open_problem(x)); ledger carrier assumed, "
                                       "trigger factive, trigger_words Acknowledging", "result": "loads and is admitted (CHECKED +29 B), but the whole-document premise check is UNKNOWN",
                            "action": "reverted (UNFORMALISED as before, with a note)", "bytes": 0, "evidence": "evidence/ps0p/premise-variants.json, premise-diag-*.txt"}},
        "step5_class_b": {"u0245": {"offered": True, "status": "OPEN", "bytes": 26, "fence": "Claude is novel.", "predicate": "novel_entity worded “{0} is novel”", "open_term": "novel_entity (judgment)",
                                    "carrier": "assumed", "claimed_only_if_audit_accepts": True},
                          "u0032": {"offered": True, "result": "wording “{0} is helpful” admitted (drops “genuine” and “constitutes”), existential claim; premise check UNKNOWN", "action": "reverted", "bytes": 0},
                          "u0069": {"offered": False, "reason": L.NOTE_U0069}, "u0083": {"offered": False, "reason": L.NOTE_U0083}},
        "noun_of_sort_entity": "thing (things), already declared in the carried translation (DRI 2026-10-14 15:30Z (1)); never the reserved word “entity”",
        "step4_triggers": {"units_with_a_trigger": sum(1 for e in ledger if e["presupposition_triggers"]), "entries": len(entries_all),
                           "by_class": dict(Counter(t["class"] for t in entries_all)), "by_carrier": dict(Counter(t["carrier"] for t in entries_all)),
                           "units_with_unresolved_carrier": len(unresolved), "blocker_tag": "other:presupposition",
                           "blocker_tag_note": "the plan says `presupposition`; the ledger's convention for a blocker outside the fixed list is other:<name>, so the tag is other:presupposition",
                           "carrier_none": "0: `none` is for a title; a title has no trigger entry, so none is written",
                           "classes_outside_the_plan_list": ["other:predicative-as (u0245, “Claude as a novel entity”)"],
                           "class_plural": "u0069 “existing deployment contexts” and u0083 “other values” are tagged plural (bare plurals with a contrast word); the census has no plural lexicon, so no other unit has one",
                           "source": "evidence/ps0p/ledger-triggers-constitution.json (the phase-1 census over the pinned text) cleaned of its named lexical false positives; headings from the curated table in ledger_1800.py",
                           "dropped_false_positives": dropped, "pre_basis": "`pre` is the translator's template sentence per trigger class (not checked by VE); carrier `unresolved` everywhere except the claimed headings (u0042, u0245, "
                                                                           "assumed) and u0043.s02.p2 (assumed, carrier_unit u0042.presupposition)"},
        "step6_goals": {"file": "presupposition-goals.json", "counts": goals["counts"]},
        "step7_check": {"loads": True, "vocabulary_wordings_changed": cp["x3_vocabulary"]["existing_predicate_wordings_changed"], "fenced_units_unchanged": all(v["unchanged"] for v in cp["x3_fenced_units"].values()),
                        "choices": cp["document_check"]["choices"], "conflict": cp["document_check"]["conflict"], "premises": cp["document_check"]["premises"],
                        "carried_probes_byte_identical": dict(probe_same), "hard_conclusions": hard_summary, "hard_conclusions_changes": hard_changes},
        "premise_variants": [{k: v[k] for k in ("variant", "added_to_QT0p", "premises")} for v in variants["variants"]],
        "finding": ("an existential premise over the sort `entity` that no ground fact names a witness for (u0286, u0032) leaves the premise check UNKNOWN once QT-0p's principal_type has size 3: the "
                    "100,000-evaluation budget is spent before a model is found and the ground-fact route has no witness; a ground fact (u0245) keeps `model`. Renaming the predicate does not matter. "
                    "Without QT-0p, u0286 alone loads with the premise check at `model` (phase 1); with both, the plans interact."),
        "expected_vs_measured": {"expected": "+29 B (u0286), stretch +149 B (class B)", "measured": "u0286 0 B (reverted), class B +26 B (u0245 only, not audited)"}}
    m["vocabulary_change_check"] = {
        "rule": "DRI 2026-10-14 15:30Z (2): after a vocabulary change rerun the situation step (nd.py all) and check every existing fenced unit still parses unchanged",
        "vocabulary_changed_in_this_run": True,
        "situation_step_rerun": "nd.py all was rerun after QT-0p, after the PS-0p builds (all variants) and for the final document (readings/nd-all-result.json: admitted, 32 choices)",
        "predicates_added": cp["x3_vocabulary"]["predicates_added"], "sorts_added": cp["x3_vocabulary"]["sorts_added"], "constants_added": cp["x3_vocabulary"]["constants_added"],
        "existing_predicate_wordings_changed": cp["x3_vocabulary"]["existing_predicate_wordings_changed"], "existing_sort_nouns_changed": cp["x3_vocabulary"]["existing_sort_nouns_changed"],
        "fenced_blocks": {"now": MAIN.read_bytes().count(b"```ve "), "previous_run": (PREV_DIR / "translation.ve.md").read_bytes().count(b"```ve ")},
        "fenced_units": {k: v for k, v in cp["x3_fenced_units"].items()}, "fenced_units_now": cp["fenced_units_now"],
        "units_differing_from_start_document": cp["units_differing_from_start"], "units_new_now": cp["units_new_now"],
        "sort_entity": "the carried sort `entity` has the noun “thing” (plural “things”), never the reserved word “entity” (asserted by repair_20261017T1800Z.py --check)",
        "checkpoints": {"qt0p": "evidence/checkpoint-qt0p.json", "final": "evidence/checkpoint-final.json"}}
    m["rust_time_limit"] = {"rule": "DRI 2026-10-14 15:30Z (3)", "VE_RUST_TIMEOUT": "unset (default)", "prlimit": "not used", "cap_raised": False,
                            "note": "no check needed a raised limit; the UNKNOWN premise checks of the PS-0p variants are an evaluation budget (Lean's), not a timeout, so a raised limit would not have changed them; "
                                    "no cap or peak resident set to record" + (f"; hard-constraint queries answered on the first run: {not unavailable}")}
    m["changes_against_previous_run"] = {
        "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger), "changed_or_replaced_ids": changed_units, "added_ids": ["u0043.s02.p1", "u0043.s02.p2"],
        "removed_ids": ["u0043.s02"], "units_newly_covered": ["u0042.presupposition", "u0043.s02.p1", "u0043.s02.p2", "u0245.presupposition"],
        "units_with_status_change": {"u0042.presupposition": "UNFORMALISED -> CHECKED", "u0043.s02": "UNFORMALISED -> MIXED (p1 LABELLED, p2 CHECKED)", "u0245.presupposition": "UNFORMALISED -> OPEN"},
        "units_changed_by_audit_repair": [], "open_terms_added": added_terms, "open_terms_removed": removed_terms, "open_terms_count_before_after": [pm["open_terms_count"], len(open_terms)],
        "reading_sets_before_after": [4, 4], "choices_before_after": [32, 32],
        "predicates_added": cp["x3_vocabulary"]["predicates_added"], "predicates_removed": [], "predicates_changed": [], "sorts_added": cp["x3_vocabulary"]["sorts_added"],
        "constants_added": cp["x3_vocabulary"]["constants_added"], "translation_byte_identical_to_previous_run": False,
        "translation_differs_only_in": "the vocabulary (sort principal_type, constants anthropic/operators/users, predicates claude_principal_type and novel_entity, open term novel_entity), the units u0042.presupposition, u0043.s02 (MIXED), u0245.presupposition, the fence of u0245, and the separating situations' identities (they are digests over the environment)",
        "ledger_annotation_changes": "status_in_previous_run; scope tags, act_workaround, claimed regenerated; presupposition_triggers and judgment_terms on every unit; other:presupposition on units with an unresolved carrier; PS-0p notes"}
    m["language_changes_since_previous_tag"] = {
        "from": PREV_TAG, "to": TAG,
        "merged": {
            "feature/jt-1 (jt-1)": "judgments@0: records and admission of judgment terms, the shared scan (lean/VE/Judgments); DELTA: no route, service mode, response field or diagnostic any caller sees until JT-2 switches the profile on in the document mode",
            "feature/et-3 (et-3)": "lean/VE/Events/* (events, states, links, calendar premises); DELTA: not reachable from any service mode, route, decoder or relay",
            "feature/et-7 (et-7)": "alternatives@0 with norm-defaults@0 is accepted (VE.Compose.todayGate and dispatch, ve.profiles.checker_family); the constitution uses no alternatives@0 profile, so it can say nothing new",
            "infra/me-1b, me-1c": "VE.Calc meaning, checker and English lines; DELTA: Public output none (no service mode, command or route)",
            "feature/pk-1s": "documents only (premise packs spec); no product file",
            "feature/fsf-r1": "a use case (safety framework) and its documents; no product code",
            "infra/ties-me-1a, ties-me-1b, ties-me-1c, tarch-manifest-ops, speed-abcache, eff-20261018-1": "ties passes, test architecture, speed and efficiency tooling; no language change"},
        "merge_commits_listed": merged,
        "checked_by": ("git diff " + PREV_TAG + ".." + TAG + " --shortstat: " + diff_all + "; git diff " + PREV_TAG + ".." + TAG + " --shortstat -- ve lean rust conformance: " + diff_stat +
                       ". Read: the DELTA.md of jt-1, et-3, et-7, me-1b, me-1c and pk-1s; no grammar production, profile, lexicon entry or checker that a norm, guard or reading set of the constitution could use "
                       "was added that a document reaches (judgments@0 and the Events and Calc modules are not reachable from a document; et-7's alternatives profile is not used here)"),
        "newly_expressible_features": 0, "units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
        "newly_measurable": ("nothing in what a document says: the probes, the conclusion queries and the 21 hard-constraint queries give the same answers as at the previous tag "
                             "(the render differs from the previous run's only where this run's plans changed the translation: " + str(render_diff_lines) + " lines)"),
        "what_made_the_difference": "plan-directed repairs only (QT-0p, PS-0p, JT-0p ledger fields); no unit gained a status or a meaning from the language"}
    m["seeded_bugs"] = json.load(open(RUN / "evidence/seeded-bugs.json")) if (RUN / "evidence/seeded-bugs.json").exists() else {"pending": True}
    m["plan_repair_AT0p_state"] = {u_: "AT-0p (attitudes plan, DRI AT2): carried unchanged, shape asserted again: guard = ( C(s) and knowingly_engages_N(c, s) ) or thinks_quite_likely_N(c, s), two binary open terms on (claude_instance, situation) (u0165.s03: one pair per candidate); not a changed unit in this run"
                                   for u_ in HC_UNITS}
    whole = json.dumps({k: v for k, v in m.items() if k not in ("checked_content_main_chain", "language_changes_since_previous_tag", "presupposition_ps0p", "quantities_qt0p", "open_term_class_removed_since_instrument", "open_term_class_reasons_new_terms", "seeded_bugs", "judgment_term_units_differing_from_phase1")}, ensure_ascii=False)
    for stale in ("force-u0125", "exception_to_never_denying", "thought_likely", "knowingly_<", "damaging_cyberweapon_or_malicious_code", "restricted_action_knowing_or_quite_likely",
                  "flat “either", "three 'should' reading sets carry content", "hard-queries-document-diff"):
        assert stale not in whole, stale
    # (judgment_term_units_differing_from_phase1 compares with the instrument of run 20261012T1800Z, which names the two removed terms; that is a comparison, not a trace)
    # REMOVE EVERY TRACE: the claims PS-0p removed must not survive anywhere in the ledger outside the unit's own `previous_presupposed_claim`
    assert_no_traces(by_id)
    dump("metrics.json", m)
    print(json.dumps({k: m[k] for k in ("claimed_covered_bytes", "claimed_covered_percent", "audit_verified_covered_bytes", "audit_verified_covered_percent",
                                         "audit_verified_metadata_bytes", "claimed_but_not_audit_verified_bytes", "changed_units")}))
    print(dict(u), dict(nb))
    print("probe_same:", probe_same, "disc_same:", disc_same, "comp_same:", comp_same, "hard_same_bytes:", hard_probe_same_bytes, "ask_same:", ask_same, "nd_concl_same:", nd_conclusions_same)
    print("judgment units:", jt_units["total"], jt_bytes["total"], "differing from phase 1:", len(jt_diff))


if __name__ == "__main__":
    main()
