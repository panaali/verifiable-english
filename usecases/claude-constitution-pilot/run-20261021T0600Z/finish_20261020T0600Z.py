#!/usr/bin/env python3
"""Run 20261020T0600Z: the measurement of the translation at ve-green-ap-1a, starting from the translation of run 20261019T1800Z (byte-identical document).

Features: nine batches merged since ve-green-et-3b (eff-20261019-1, me-5, jt-1b, et-8, ar-10a, arch-20261019-1 = AR-17, pk-1b, arch-20261019-2 = AR-16a, ap-1a). None lets a document say something new:
`acts@0` (ap-1a) and `judgments@0` (jt-1b) are Lean modules whose profiles the envelope still refuses (evidence/new-profile-probe.json); the rest are refactors, tooling, trust and refusal-text changes. What changed in the ledger:
  * the three faults the audit of 20261019T1800Z listed on UNCLAIMED units (u0235 existence and uniqueness; u0002 and u0095 the owner is the company, not the principal type): ledger notes, claims and fences only (ledger_20261020.py,
    owner_probe.py); no status, no byte, no document change.
  * everything else is carried: ledger fields regenerated or kept, every probe re-run on the unchanged document.

Order (repository root, PATH must contain ~/.elan/bin, VE_NATIVE_PREBUILT=1; `lake build` in lean/ and tools/rust_build.py done):
    uv run python .../nd.py all ; cmp readings/nd-all.ve.md prev/translation.ve.md ; uv run python .../checkpoint.py final ; owner_probe.py ; probes (README.md), probe_hard_conclusions.py, probe_soft_chain.py
    uv run python .../finish_20261020T0600Z.py           # ledger (units.json), scope-tally.json, presupposition-goals.json, renderings, check, coverage, metrics.json
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
import ledger_0600 as L2  # noqa: E402  (EXTRA_TRIGGERS)
import ledger_1800z as L3  # noqa: E402
import ledger_20261020 as L4  # noqa: E402
import scope_tally  # noqa: E402
import spec_nd  # noqa: E402

RUN_ID = "20261020T0600Z"
PREV_RUN = "20261019T1800Z"
TAG = "ve-green-ap-1a"
PREV_TAG = "ve-green-et-3b"
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
AUDIT_1018_FAITHFUL, AUDIT_1018_UNFAITHFUL = p17.received("20261018T0600Z", 25)   # 20 sampled + 5 changed, 25 verdicts, none unfaithful
AUDIT_1018B_FAITHFUL, AUDIT_1018B_UNFAITHFUL = p17.received("20261018T1800Z", 47, ["u0042.presupposition"])   # 20 sampled + 28 changed, 48 verdicts, one unfaithful
AUDIT_1019_FAITHFUL, AUDIT_1019_UNFAITHFUL = p17.received("20261019T0600Z", 30, ["u0032.presupposition"])   # 20 sampled + 11 changed, 31 verdicts, one unfaithful
AUDIT_1019B_FAITHFUL, AUDIT_1019B_UNFAITHFUL = p17.received(PREV_RUN, 31)   # 20 sampled + 9 changed + 2 PS-0p class-B items, 31 verdicts, none unfaithful
assert AUDIT_1019B_UNFAITHFUL == []
AUDIT_LATEST = list(dict.fromkeys(p17.AUDIT_LATEST + p17.received("20261017T1800Z", 28)[0] + AUDIT_1018_FAITHFUL + AUDIT_1018B_FAITHFUL + AUDIT_1019_FAITHFUL + AUDIT_1019B_FAITHFUL))
QT_CHANGED = []   # QT-0p is carried: the units were audited FAITHFUL by 20261019T0600Z and are unchanged here
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


def probe_new_profiles():
    """acts@0 (ap-1a) and judgments@0 (jt-1b) are new Lean modules at this tag: add each to the strict companion's environment and record what `ve document check` says."""
    import tempfile
    base = STRICT.read_bytes()
    end = base.index(b"\n---\n", 4)
    meta, tail = json.loads(base[4:end]), base[end + 5:]
    result = {}
    for extra in ("acts@0", "judgments@0"):
        m_ = json.loads(json.dumps(meta))
        m_["environment"]["profiles"] = sorted(set(m_["environment"]["profiles"]) | {extra})
        with tempfile.NamedTemporaryFile("wb", suffix=".ve.md", delete=False) as handle:
            handle.write(b"---\n" + json.dumps(m_, ensure_ascii=False, separators=(",", ":")).encode() + b"\n---\n" + tail)
        proc = subprocess.run([sys.executable, "-m", "ve", "document", "check", handle.name], cwd=ROOT, capture_output=True, text=True)
        Path(handle.name).unlink()
        result[extra] = "accepted at document-check level" if proc.returncode == 0 else (proc.stderr.strip().splitlines() or ["rejected"])[-1].split(": ", 1)[-1]
    return result


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
               "u0043.s02.p2": block_after(render, "Claude’s three types of principals are Anthropic, operators, and users."),
               "u0286.presupposition": block_after(render, "Acknowledging open problems"),
               "u0013.presupposition": block_after(render, "Claude’s core values")}
    assert english["u0286.presupposition"] == "Checked reading: There is a thing that is unsolved.", english["u0286.presupposition"]
    assert english["u0013.presupposition"] == "Checked reading: There is a thing that is a core value of claude.", english["u0013.presupposition"]
    assert "genuine_helpfulness" not in render and "Some thing is helpful" not in render and "There is a thing that is helpful" not in render   # u0032 is UNFORMALISED again
    assert "classified as" not in english["u0042.presupposition"] + english["u0043.s02.p2"] and "principal type of Claude" in english["u0042.presupposition"]   # the audit repair: no quoted name
    english_u0245 = block_after(render, "Claude as a novel entity")
    assert english_u0245 == "Open reading: Claude is novel.", english_u0245

    # ---- the ledger: the ps-6r upgrade (u0013), the not-claimed expressible headings, the audit repair of u0032
    L.HEADINGS["u0235"] = [("possessive", "Claude’s", L4.CLAIM_U0235)]   # the audit of 20261019T1800Z: a singular possessive takes for granted existence and uniqueness
    changed_edit = L4.apply(ledger)
    by_id = {e["id"]: e for e in ledger}
    ids = [e["id"] for e in ledger]
    for e in ledger:
        if e["status"] in COVERED:
            e["claimed"] = True
    claimed_false = [e["id"] for e in ledger if e.get("claimed") is False]

    # ---- SC-M0 (tags only): carried. No unit's span, id or text changed in this run, so the governors, their reach and effect, and the tags in the carried ledger stand; checked against the tally file
    tally = json.load(open(PREV_DIR / "scope-tally.json"))
    assert tally["totals"] == pm["scope_tally"]["totals"] and (tally["totals"]["governors"], tally["totals"]["units_tagged"], tally["totals"]["bytes_tagged"]) == (150, 352, 55294)
    tagged = {e["id"] for e in ledger if "other:scope" in (e.get("other_blockers") or [])}
    assert sum(e["span"][1] - e["span"][0] for e in ledger if e["id"] in tagged) == 55294 and len(tagged) == 353, (len(tagged),)   # 352 units, u0043.s02 counted once and carried by both parts
    tally["note"] = ("scope-tally for run " + RUN_ID + ", carried from " + PREV_RUN + ": the tags are ledger annotations only (other_blockers gains `other:scope`, governed units record governed_by, "
                     "a frontier governor's candidates record governed_by_candidate), and no unit's status or content changes for them. No unit's span, id or text changed in this run, so governors, reach, effect "
                     "and totals are those of the previous run. u0043.s02 is MIXED; its parts both carry the tags and the tally counts the sentence once, with its 90 bytes")
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
    L.HEADING_CARRIER.update({"u0286": "assumed", "u0013": "assumed"})   # the headings whose claim is the unit's content now, as u0042 and u0245 (u0032 is unresolved again)
    L.HEADINGS["u0002"] = [("definite", "the mission of", "Anthropic has exactly one mission.")]   # unchanged text of the table; asserted so the claim and the trigger's `pre` stay equal
    assert by_id["u0002.presupposition"]["presupposed_claim"] == "Anthropic has exactly one mission."
    unresolved, dropped, trig_counts = L.triggers_for_ledger(ledger, census, SOURCE)
    assert [(d["unit"], d["words"]) for d in dropped] == EXPECTED_DROPPED, dropped
    for uid_, ent_ in L2.EXTRA_TRIGGERS.items():   # the audit's small fault: the definite triggers of two LABELLED headings
        assert by_id[uid_]["presupposition_triggers"] == [], uid_
        by_id[uid_]["presupposition_triggers"] = [dict(ent_)]
        unresolved.append(uid_)
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
        "u0245.presupposition": "a unit of the 18:00Z run (PS-0p class B, 26 B): its open term novel_entity is class judgment"}
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
    assert claimed == pm["claimed_covered_bytes"], claimed   # no unit changes status
    n_old, old_units, _ = old.aggregate(ledger)
    spans = {e["id"]: e["span"] for e in ledger}
    status = {e["id"]: e["status"] for e in ledger}
    width = lambda ids_: sum(spans[i][1] - spans[i][0] for i in ids_)
    assert coverage["bytes_by_status"]["CHECKED"] == nb["CHECKED"] and coverage["bytes_by_status"]["OPEN"] == nb["OPEN"] + nb["READINGS"]
    assert coverage["bytes_by_status"]["LABELLED"] == nb["LABELLED"]

    changed_units = sorted(set(changed_edit), key=ids.index)
    LEDGER_NOTES = ["u0095.presupposition", "u0002.presupposition", "u0235.presupposition"]
    assert sorted(changed_units) == sorted(LEDGER_NOTES)
    at0p = [{"unit": u_, "plan": "attitudes", "item": "AT-0p", "applied_in_this_run": False,
             "state": ("already in the plan's form at the start of this run (applied in 20261014T1800Z; accepted FAITHFUL by every audit since, the last of 20261019T0600Z); the shape is asserted "
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
    # u0165.s01 "knowing" was ALL at the 18:00Z run of 20261018 and UNKNOWN at both runs of 20261019 (a search-budget effect on a changed document): every query has the previous run's verdict, route and evidence
    hard_changes = [{"unit": q["unit"], "kind": q["kind"], "now": [q["verdict"], q.get("evidence")], "before": [p_["verdict"], p_.get("evidence")]}
                    for q, p_ in zip(hard_q, prev_hard) if (q["unit"], q["kind"]) == (p_["unit"], p_["kind"]) and (q["verdict"], q.get("evidence")) != (p_["verdict"], p_.get("evidence"))]
    assert hard_changes == [] and hard_by[("u0165.s01", "belief")]["verdict"] == "UNKNOWN" and hard_by[("u0165.s01", "knowing")]["verdict"] == "UNKNOWN", hard_changes
    hard_same = slim(hard_q) == slim(prev_hard)
    assert hard_same
    unavailable = sorted(f"{q['unit']}:{q['kind']}" for q in hard_q if "rerun_alone" in q or q.get("cap"))
    hard_summary = {k: dict(Counter(q["verdict"] for q in hard_q if q["kind"] == k)) for k in ("knowing", "belief", "neither")}
    probe_names = ("risk-probe", "s1-probe", "senses-probe", "senses-document-probe", "rights-reading-probe", "unspecified-probe", "frame-probe")
    probe_same = {n: (RUN / f"probes/{n}.json").read_bytes() == (PREV_DIR / f"probes/{n}.json").read_bytes() for n in probe_names}
    # risk-probe: probe_risk.py lost its Python gate mirror (ar-10a); the cases must be identical, only the profile-gate rows may differ
    risk_now, risk_prev = json.load(open(RUN / "probes/risk-probe.json")), json.load(open(PREV_DIR / "probes/risk-probe.json"))
    risk_cases_same = {k: v for k, v in risk_now.items() if k != "profile_gate"} == {k: v for k, v in risk_prev.items() if k != "profile_gate"}
    risk_gate_diff = {k: {"before": risk_prev["profile_gate"][k], "now": risk_now["profile_gate"][k]} for k in risk_now["profile_gate"] if risk_now["profile_gate"][k] != risk_prev["profile_gate"][k]}
    assert risk_cases_same and len(risk_gate_diff) == 2, (risk_cases_same, risk_gate_diff)
    assert all(v for n, v in probe_same.items() if n != "risk-probe"), probe_same
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
                       "decided_units_same_as_previous_run": True,
                       "reading": ("unchanged since the 06:00Z run of 20261019 (and the 18:00Z run before it) except that u0013.presupposition takes the place of u0032.presupposition in the main component: the companion denial query (--sentence u0125.s04.p2) and the claim-human query (--sentence u0123.s03) answer ALL, but the main component's "
                                   "premise check is UNKNOWN on the components route (was model at 06:00Z), so only 4 units are Lean-decided (372 B; 19 units, 2,602 B at 06:00Z). The repair of QT-0p's wording "
                                   "(a sort instead of a predicate) did not restore it; the translation's own premise check, on the superposed route, stays `model`. A measurement document, not the translation. "
                                   "The component also holds the claimed units u0286 and u0013 (they are not Lean-decided)"),
                       "premise_regression": {"measured_in": "20261018T1800Z, with QT-0p's predicate wording; not re-attributed in this run", "results": attribution["results"]},
                       "decided_units_ids": lds["decided_units"]}
    lean_decided_share = {**pm["lean_decided_share"], "with_companion_sets": {**pm["lean_decided_share"]["with_companion_sets"], "decided_units": len(lds["decided_units"]),
                          "decided_bytes": lds["decided_bytes"], "decided_share_percent": lds["decided_share_percent"], "units": lds["decided_units"],
                          "previous_run": {"decided_units": 4, "decided_bytes": 372, "decided_share_percent": "0.20"}, "same_as_previous_run": True, "earlier_run_20261018T0600Z": {"decided_units": 19, "decided_bytes": 2602, "decided_share_percent": "1.41"},
                          "cause": "the main component's premise check is UNKNOWN on the components route since QT-0p's principal_type (size 3) entered the document in 20261018T1800Z (evidence/companion-attribution.json); the sort-based wording of this run leaves it UNKNOWN"}}
    frame_probe = json.load(open(RUN / "probes/frame-probe.json"))
    soft = json.load(open(RUN / "evidence/soft-chain-probe.json"))
    prev_soft = pm["soft_chain_probe"]
    nosec = lambda d: {k: v for k, v in d.items() if k != "seconds"}
    soft_same = (soft["check"]["returncode"] == prev_soft["result"]["ve_document_check"]["returncode"] and
                 nosec(soft["conclusions"]["denial"]) == nosec(prev_soft["result"]["ve_document_readings_denial_query"]) and
                 nosec(soft["conclusions"]["claim_human"]) == nosec(prev_soft["result"]["ve_document_readings_claim_human_query"]))
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
    assert not removed_terms and not added_terms and not changed_terms, (added_terms, removed_terms, changed_terms)   # no vocabulary change
    gap_marker = "Here the text does not say whether"
    sep_lines = lambda text: [ln for ln in text.splitlines() if ln.startswith("These two readings differ here")]
    gaps_now = [ln.count(gap_marker) for ln in sep_lines(render)]
    cannot_show = lambda text: text.count("These two readings differ in a checked situation that VE cannot yet show in words.")
    assert gaps_now == [1, 1] and cannot_show(render) == 7 == cannot_show(old_render)

    # ---- X3: the checkpoint evidence of the final document
    cp = json.load(open(RUN / "evidence/checkpoint-final.json"))
    assert cp["document_check"]["premises"] == "model" and not cp["x3_vocabulary"]["existing_predicate_wordings_changed"]

    # ---- the language changes since the previous tag: read from the repository
    diff_all = git("diff", "--shortstat", f"{PREV_TAG}..{TAG}")
    diff_stat = git("diff", "--shortstat", f"{PREV_TAG}..{TAG}", "--", "ve", "lean", "rust", "conformance")
    merged = git("log", "--first-parent", "--format=%h %s", f"{PREV_TAG}..{TAG}").splitlines()
    assert len(merged) == 9, len(merged)

    missing_now = old.tally(ledger)
    lo_names = list(pm["ledger_only_open_terms"]["names"])
    assert lo_names == ["appropriate_oversight", "broad_safety", "ethical_harm", "genuine_helpfulness"], lo_names
    lo_entries = [e for e in ledger if set(e.get("open_terms") or []) & set(lo_names)]
    ledger_only = {**pm["ledger_only_open_terms"], "names": lo_names, "entries": len(lo_entries), "statuses": dict(Counter(e["status"] for e in lo_entries)),
                   "covered_entries_with_such_names": [e["id"] for e in lo_entries if e["status"] in COVERED]}
    assert ledger_only["covered_entries_with_such_names"] == []

    # ---- new this tag: do the two profiles that landed as Lean modules (acts@0 by ap-1a, judgments@0 by jt-1b) reach a document?
    new_profiles = probe_new_profiles()
    assert all(v.startswith("UnsupportedProfile") for v in new_profiles.values()), new_profiles
    dump("evidence/new-profile-probe.json", new_profiles)
    owner = json.load(open(RUN / "evidence/owner-probe.json"))
    assert owner["u0095.company"]["parses"] and owner["u0002.company"]["parses"] and owner["u0235.unique"]["parses"] and owner["u0013.capital"]["declared"] is False
    assert all(owner[k]["round_trip_same_formula"] for k in ("u0095.company", "u0002.company", "u0235.unique"))
    assert [owner[k]["fence"] for k in ("u0095.company", "u0002.company", "u0235.unique")] == [L4.FENCE["u0095"], L4.FENCE["u0002"], L4.FENCE["u0235"]]
    assert owner["u0235.unique"]["formulas"][0][0] == "exists" and "forall" in json.dumps(owner["u0235.unique"]["formulas"]), owner["u0235.unique"]   # existence AND uniqueness

    # ---- English round trip of the rules: carried record compared with this run's measurement (the nested guard of the hard constraints)
    rt_now = {r: v["round_trip"] for r, v in eng.items()}
    rt_prev = {**{r: False for r in pm["english_round_trip"]["hard_constraint_rules"]}, **{r: True for r in pm["english_round_trip"]["other_rules_round_trip"]}}
    english_round_trip_same = all(rt_now.get(r) == v for r, v in rt_prev.items())

    audit_note = ("The audit of run 20261019T1800Z (AUDIT-20261019T1800Z-received.md, 31 verdicts, all FAITHFUL; 20 sampled plus 9 changed plus the 2 PS-0p class-B items it also checked) is the latest. It marked no unit unfaithful "
                  "or incomplete, so there is nothing to repair for a covered status. It listed three faults to fix before claiming (no verdict change): u0235, u0002 and u0095, all unclaimed")
    m = copy.deepcopy(pm)
    for stale in ("feature_upgrade_counts_separate_from_repairs", "changed_units_by_role", "audit_repairs", "changed_units_detail", "feature_upgrades", "claimed_covered_bytes_gained_by_plan",
                  "claimed_covered_bytes_gained_by_feature", "claimed_covered_bytes_lost_by_audit_repair", "claimed_covered_bytes_gained_detail", "audit_rejected_units_and_repair_status",
                  "audit_verified_newly_from_20261017T0600Z", "audit_verified_newly_labelled_from_20261017T0600Z", "audit_verified_newly_from_20261017T1800Z", "audit_verified_newly_labelled_from_20261017T1800Z",
                  "audit_verified_newly_from_20261018T0600Z", "audit_verified_newly_labelled_from_20261018T0600Z", "audit_verified_newly_from_20261018T1800Z", "audit_verified_newly_labelled_from_20261018T1800Z",
                  "audit_verified_newly_from_20261019T0600Z", "audit_verified_newly_labelled_from_20261019T0600Z", "plan_repairs_carried_from_20261019T0600Z", "plan_repair_note", "open_terms_count_note",
                  "repaired_bytes_not_audit_verified", "claimed_but_not_audit_verified_units"):
        m.pop(stale, None)
    m.update({
        "run": RUN_ID, "baseline_tag": TAG, "previous_run": PREV_RUN, "previous_baseline_tag": PREV_TAG,
        "history_note": "this file records this run; the earlier runs' records are in prev/metrics.json and the AUDIT-*-received.md files",
        "feature_upgrade_counts_separate_from_repairs": (
            "units upgraded by new features 0 (+0 B), reading sets upgraded by new features 0: none of the nine batches merged since ve-green-et-3b lets a document say something new (FEATURE-REVIEW.md). "
            "Plan repairs of this run: 0 (the plans merged for the 18:00Z run of 20261018 are carried unchanged). Audit repairs of covered units: 0 (the latest audit marked none unfaithful). Ledger-note-only "
            "changes: 3 (u0095, u0002, u0235: the three faults the latest audit listed on unclaimed units), 0 B claimed or lost. The translation document is byte-identical to the previous run's"),
        "changed_units": changed_units,
        "changed_units_by_role": {"feature_upgrade": [], "plan_repair": [], "audit_repair_of_a_covered_unit": [], "ledger_note_only (status unchanged, 0 B claimed; audit faults on unclaimed units)": LEDGER_NOTES},
        "plan_repairs": [],
        "plan_repairs_note": "none in this run. AT-0p, QT-0p, PS-0p, SC-M0, AP-0 item 3, JT-0p and the DRI rulings X2 to X5 were applied in the 18:00Z run of 20261018 and carried since; their state is in plan_repair_AT0p_state, quantities_qt0p, presupposition_ps0p, scope_tally, act_workaround_m4 and open_term_class",
        "plan_repairs_carried": {"AT-0p (attitudes)": HC_UNITS, "QT-0p (quantities)": ["u0042.presupposition", "u0043.s02.p1", "u0043.s02.p2"], "PS-0p (presupposition)": pm["plan_repairs_carried_from_20261019T0600Z"]["changed_units_of_the_previous_run"]
                                 if "plan_repairs_carried_from_20261019T0600Z" in pm else "see prev/metrics.json"},
        "audit_repairs": [],
        "audit_faults_listed_on_unclaimed_units": {
            "audit": PREV_RUN, "verdicts": "31 of 31 FAITHFUL, none unfaithful or incomplete",
            "u0235.presupposition": {"fault": "“Claude’s nature” is a singular possessive: existence and uniqueness; the record and fence gave existence only", "repair": "claim, trigger `pre` and fence are the uniqueness form (ledger only; the unit stays UNFORMALISED)"},
            "u0002.presupposition": {"fault": "the fence's owner `anthropic` is the type of principal; the mission belongs to the company", "repair": f"fence names the constant `{L4.COMPANY}` (sort thing); ledger only"},
            "u0095.presupposition": {"fault": "the fence's owner `anthropic` is the type of principal; the guidelines belong to the company", "repair": f"fence names the constant `{L4.COMPANY}` (sort thing); ledger only"},
            "u0013.presupposition": {"fault": "“of claude” is written in lower case", "repair": "not repairable: a constant must be a lower-case ASCII identifier (`Invalid ASCII identifier: 'Claude'`, evidence/owner-probe.json); recorded as a finding; the entry is untouched so its audit verdict stands"},
            "evidence": "evidence/owner-probe.json (owner_probe.py): the three corrected fences parse, render and round-trip to the same formula"},
        "feature_upgrades": {"units_upgraded_by_new_features": 0, "bytes_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0, "unit_ids": [],
                             "note": "kept apart from the plan repairs and audit repairs, so that differences against the previous run measure the language, not the translator"},
        "tags_only_not_changed_units": ("scope tags (SC-M0), act_workaround (AP-0 item 3), presupposition_triggers and the blocker other:presupposition (PS-0p step 4), judgment_terms (JT-0p) and the "
                                        "`claimed` field are ledger annotations; none of them makes a unit a changed unit"),
        "sentence_clause_units": {"units_total": len(ledger), "unit_counts_by_status": old.full(u), "bytes_by_status": old.full(nb),
                                  "previous_run": {k: pm["sentence_clause_units"][k] for k in ("units_total", "unit_counts_by_status", "bytes_by_status")}},
        "aggregated_to_previous_boundaries": {"units_total": n_old, "unit_counts_by_status": old_units, "bytes_by_substatus": old.full(nb),
                                              "previous_run": {k: pm["aggregated_to_previous_boundaries"][k] for k in ("units_total", "unit_counts_by_status")},
                                              "note": "aggregated by the unit's block (parent_unit), as in earlier runs"},
        "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(SOURCE), 4),
        "claimed_covered_bytes_previous_run": pm["claimed_covered_bytes"], "claimed_covered_bytes_gained": claimed - pm["claimed_covered_bytes"],
        "claimed_covered_bytes_gained_by_feature": {}, "claimed_covered_bytes_gained_by_plan": {}, "claimed_covered_bytes_lost_by_audit_repair": {},
        "claimed_false_units": claimed_false,
        "substantive_covered_bytes": nb["CHECKED"] + nb["OPEN"] + nb["READINGS"], "substantive_covered_bytes_previous_run": pm["substantive_covered_bytes"],
        "audit_verified_covered_bytes": verified_bytes, "audit_verified_covered_percent": round(100 * verified_bytes / len(SOURCE), 4),
        "audit_verified_covered_units": verified, "audit_verified_covered_bytes_previous_run": pm["audit_verified_covered_bytes"],
        "audit_verified_dropped_because_changed": [i for i in pm["audit_verified_covered_units"] if i in changed_units],
        "audit_verified_newly_from_20261019T1800Z": newly,
        "audit_verified_newly_labelled_from_20261019T1800Z": [i for i in AUDIT_1019B_FAITHFUL if status.get(i) == "LABELLED" and i not in changed_units],
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND unchanged in this run from the form that audit saw. " + audit_note + ". The three units whose ledger notes changed are "
            "UNFORMALISED (no claimed byte); the 24 B of u0013.presupposition, the only claimed bytes the previous run's audit had not seen, were accepted by it and are unchanged here. This is a count of verdicts on "
            "unchanged text, not a fresh audit of this run."),
        "audit_verified_metadata_bytes": verified_meta, "audit_verified_metadata_percent": round(100 * verified_meta / len(SOURCE), 4),
        "audit_verified_metadata_bytes_previous_run": pm["audit_verified_metadata_bytes"],
        "claimed_but_not_audit_verified_bytes": claimed - verified_bytes - verified_meta,
        "claimed_but_not_audit_verified_units": [e["id"] for e in ledger if e["status"] in COVERED and e.get("claimed", True) is not False and e["id"] not in verified and e["id"] not in verified_lab],
        "audit_rejected_units_and_repair_status": {
            "rejected_by_latest_audit": [], "latest_audit": PREV_RUN, "kept_covered_status_without_repair": [],
            "earlier": {"rejected_by_20261019T0600Z_audit": ["u0032.presupposition"], "repair_done_in_20261019T1800Z": "reverted to UNFORMALISED (other:discourse), 38 B not claimed; confirmed by the 20261019T1800Z audit (u0032.presupposition FAITHFUL as unclaimed)"},
            "small_faults_not_repaired": {
                "principal type of Claude": "can also be read as “main type of Claude” (carried; the sort noun is what removed the quoted-name fallback)",
                "u0156.s03 frame term": pm["audit_rejected_units_and_repair_status"]["small_faults_not_repaired"]["u0156.s03 frame term"],
                "u0168.s01 guard": pm["audit_rejected_units_and_repair_status"]["small_faults_not_repaired"]["u0168.s01 guard"],
                "u0173.s01 to s04": pm["audit_rejected_units_and_repair_status"]["small_faults_not_repaired"]["u0173.s01 to s04"],
                "u0013 lower-case constant": "not repairable by a wording (owner-probe.json): the finding stays"}},
        "open_terms": open_terms, "open_terms_count": len(open_terms), "open_terms_count_previous_run": pm["open_terms_count"],
        "open_terms_added": added_terms, "open_terms_removed_this_run": removed_terms, "open_terms_with_changed_factors": changed_terms, "open_terms_with_changed_arguments": {},
        "ledger_only_open_terms": ledger_only,
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
            "build_note": "lean/.lake and rust/target copied (cp -a) from the ve-integration checkout at the identical commit (b1f7ca7ad); `lake build` completed (1045 jobs, 31 min 46 s: the copy's paths differ, so it rebuilt) and the Rust binary "
                          "is the pin in lean/checkers.lock (SHA-256 6422647f…8579, `tools/rust_build.py --check`); not a language measurement",
            "order": "[this run, previous run]"},
        "unspecified_probe": {**pm["unspecified_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["unspecified-probe"]},
        "profile_combination_probe_same_as_previous_run": True,
        "senses_probe": {**pm["senses_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-probe"]},
        "senses_document_probe": {**pm["senses_document_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-document-probe"]},
        "discourse_probe": {**pm["discourse_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": disc_same},
        "rights_reading_probe": {**pm["rights_reading_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["rights-reading-probe"]},
        "risk_probe": {**pm["risk_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["risk-probe"], "cases_identical_to_previous_run": risk_cases_same,
                       "profile_gate_differences": risk_gate_diff,
                       "why": ("ar-10a deleted the Python gate mirror `checker_family` that probe_risk.py imported; the script now builds the environment and lets Lean's gate (VE.Compose.gateOf) answer, "
                               "so the one accepted row no longer names a “checker family”, and rows with `rights@0` are refused as an unregistered environment profile first (ar-10a DELTA item 1, fault order). "
                               "Every risk case (outcome of the 14 elaborations) is identical")},
        "readings_defaults_probe": {**pm["readings_defaults_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["s1-probe"]},
        "carried_probes_note": ("the carried probes were re-run on the final document: byte-identical JSON for " + ", ".join(k for k, v in probe_same.items() if v) +
                                "; discourse " + ("byte-identical" if disc_same else "differs (see probes/discourse-probe.json)") + "; risk: every case identical, the profile-gate rows differ in two rows (see risk_probe); companion: " +
                                ("identical to the previous run's after the run identifiers are normalised" if comp_same else "DIFFERS") + "; the 21 hard-constraint queries give " +
                                json.dumps(hard_summary) + (", every verdict equal to the previous run's" if not hard_changes else ", changes: " + json.dumps(hard_changes)) +
                                "; the denial and claim-to-be-human conclusion queries are ALL; the five `ve ask` questions give no answer as before; the probe_s1 input is the 06:00Z document of 20261018 (evidence/pre-qt0p-translation-without-content.ve.md), as in the previous run"),
        "frame_probe": {**pm["frame_probe"], "identical_to_previous_run": probe_same["frame-probe"]},
        "companion_probe": companion_probe, "lean_decided_share": lean_decided_share,
        "profile_combination_probe_changes": {"what": pm["profile_combination_probe_changes"]["what"], "changed": {}, "reading": "all thirteen rows are identical to the previous run's"},
        "new_profiles_probe": {"what": "the two profiles that landed as Lean modules at this tag, `acts@0` (ap-1a) and `judgments@0` (jt-1b), added to the strict companion's environment, then `ve document check`", "result": new_profiles,
                               "reading": "both are refused: no document can use them yet (ap-1a: “acts@0 has no profile row (ap-1b)”; jt-1b: not reached by any route before JT-2). So no unit of the constitution can use lexical acts or judgment terms at this tag"},
        "soft_chain_probe": {**prev_soft, "result": {**prev_soft["result"],
                                                     "ve_document_check": {**prev_soft["result"]["ve_document_check"], "stderr_last_lines": soft["check"]["stderr_last_lines"]},
                                                     "ve_document_coverage": soft["coverage"], "ve_document_render": soft["render"],
                                                     "ve_document_readings_denial_query": soft["conclusions"]["denial"], "ve_document_readings_claim_human_query": soft["conclusions"]["claim_human"]},
                             "same_outcome_as_previous_run": soft_same,
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
        "english_round_trip": {**pm["english_round_trip"], "re_measured_this_run": True, "same_as_previous_run": english_round_trip_same},
        "document_open_terms_class_note": "see open_term_class",
        "open_term_class": classes,
        "open_term_class_borderline": p1["borderline_judgment_terms"],
        "open_term_class_reasons_new_terms": jt_reasons,
        "open_term_class_removed_since_instrument": JT_GONE,
        "open_term_class_counts": dict(Counter(classes.values())),
        "open_term_class_vs_phase1": {"terms_in_both": sum(1 for t in classes if t in p1["open_term_class"]), "classes_differing": {}, "terms_new": sorted(JT_NEW),
                                      "note": "every term unchanged since run 20261012T1800Z has phase 1's class; the new terms are the ones of JT_NEW (a one-line reason each in open_term_class_reasons_new_terms); no term is new or changed in this run"},
        "judgment_term_units": jt_units, "judgment_term_bytes": jt_bytes,
        "judgment_term_phase1_reference": {"units": p1["judgment_term_units"]["total"], "bytes": p1["judgment_term_bytes"]["total"], "run": "20261012T1800Z"},
        "judgment_term_units_differing_from_phase1": jt_diff,
    })
    # the QT-0p and PS-0p records: carried (the units are unchanged and were audited FAITHFUL)
    m["quantities_qt0p"] = {
        **pm["quantities_qt0p"], "carried_in_this_run": True,
        "this_run": ("no unit, wording or formula of QT-0p changed in this run: u0042.presupposition (CHECKED, 38 B), u0043.s02.p1 (LABELLED, 15 B) and u0043.s02.p2 (CHECKED, 75 B) stay as audited FAITHFUL; "
                     "u0043.s01 is still UNFORMALISED (counting). The fourth-type probe is re-run on the final document."),
        "claimed_bytes": {**pm["quantities_qt0p"]["claimed_bytes"], "gained_in_this_run": 0, "measured_this_run": cp["document_check"]["bytes_by_status"]},
        "premises": {**pm["quantities_qt0p"]["premises"], "measured": cp["document_check"]["premises"]},
        "probe_fourth_type": {**pm["quantities_qt0p"]["probe_fourth_type"], "negation_verdict": qt_probe["verdict"], "evidence": qt_probe["evidence"], "route": qt_probe["route"], "re_run_at_this_tag": True,
                              "the_positive_query_fourth": {"verdict": qt_fourth["verdict"], "note": pm["quantities_qt0p"]["probe_fourth_type"]["the_positive_query_fourth"]["note"]}},
        "checks_this_run": {"x3_existing_wordings_changed": cp["x3_vocabulary"]["existing_predicate_wordings_changed"], "choices": cp["document_check"]["choices"], "conflict": cp["document_check"]["conflict"],
                            "conclusions": cp["conclusions"]}}
    ps_prev = pm["presupposition_ps0p"]
    m["presupposition_ps0p"] = {
        **{k: v for k, v in ps_prev.items() if k in ("plan", "applied_in_20261018T1800Z_and_carried", "carried_from_20261019T0600Z", "noun_of_sort_entity", "finding")},
        "carried_from_20261019T1800Z": {"step3_u0013": ps_prev["this_run"]["step3_u0013"], "step3_expressible_not_claimed": ps_prev["this_run"]["step3_expressible_not_claimed"],
                                        "step5_u0032": ps_prev["this_run"]["step5_u0032"], "premise_variants": ps_prev["this_run"]["premise_variants"], "ps6r_wordings": ps_prev["this_run"]["ps6r_wordings"]},
        "this_run": {"document_changes": "none", "ledger_note_changes": {"u0235.presupposition": "claim, trigger `pre` and expressible fence: existence and uniqueness (singular possessive), from the audit of 20261019T1800Z",
                                                                         "u0002.presupposition": f"expressible fence names the company constant `{L4.COMPANY}`, not the principal type `anthropic`",
                                                                         "u0095.presupposition": f"expressible fence names the company constant `{L4.COMPANY}`, not the principal type `anthropic`"},
                     "owner_probe": "evidence/owner-probe.json (owner_probe.py): the corrected fences parse, render and round-trip; they are NOT added to the document (the premise-check budget still blocks claiming them)",
                     "u0013_lower_case_constant": owner["u0013.capital"]},
        "step4_triggers": {"units_with_a_trigger": sum(1 for e in ledger if e["presupposition_triggers"]), "entries": len(entries_all),
                           "by_class": dict(Counter(t["class"] for t in entries_all)), "by_carrier": dict(Counter(t["carrier"] for t in entries_all)),
                           "units_with_unresolved_carrier": len(unresolved), "blocker_tag": "other:presupposition",
                           "blocker_tag_note": ps_prev["step4_triggers"]["blocker_tag_note"],
                           "changed_in_this_run": {"u0235": "pre “Claude has exactly one nature.” (was “Claude has a nature.”)"},
                           "source": ps_prev["step4_triggers"]["source"], "dropped_false_positives": dropped},
        "step6_goals": {"file": "presupposition-goals.json", "counts": goals["counts"]},
        "step7_check": {"loads": True, "vocabulary_wordings_changed": cp["x3_vocabulary"]["existing_predicate_wordings_changed"], "fenced_units_unchanged": all(v.get("unchanged", True) for v in cp["x3_fences"].values()),
                        "choices": cp["document_check"]["choices"], "conflict": cp["document_check"]["conflict"], "premises": cp["document_check"]["premises"],
                        "carried_probes_byte_identical": dict(probe_same), "hard_conclusions": hard_summary, "hard_conclusions_changes": hard_changes},
        "prompt_tension": ("the standing PS-0p step 3 in this run's prompt still says to keep u0013, u0095, u0002 and u0235 UNFORMALISED because the relational-noun wording is 'not admitted'. ps-6r (merged before the "
                           "previous run) admits it, the audit of 20261019T1800Z accepted u0013 (“I accept u0013. You should retire that line, or overrule me and drop its 24 B”), so u0013 stays CHECKED as in the previous run; "
                           "u0095, u0002 and u0235 stay unclaimed for the premise-check budget, not for the wording. The orchestrator should retire the step-3 sentence or tell the next run to drop the 24 B"),
        "expected_vs_measured": {"expected": "PS-0p's expectation (+29 B u0286, stretch +149 B class B) was met or superseded in earlier runs", "measured": "no byte gained or lost in this run (3,158 B claimed, all audit-verified)"}}
    m["vocabulary_change_check"] = {
        "rule": "DRI 2026-10-14 15:30Z (2): after a vocabulary change rerun the situation step (nd.py all) and check every existing fenced unit still parses unchanged",
        "vocabulary_changed_in_this_run": False,
        "situation_step_rerun": "nd.py all was rerun on the unchanged start document: readings/nd-all.ve.md is cmp-identical to the previous run's translation.ve.md; checkpoint.py final (evidence/checkpoint-final.json): fenced units parse to the same formulas",
        "predicates_added": [], "predicates_removed": [], "sorts_added": [], "constants_added": [], "sort_noun_changed": {},
        "existing_predicate_wordings_changed": cp["x3_vocabulary"]["existing_predicate_wordings_changed"], "existing_sort_nouns_changed": cp["x3_vocabulary"]["existing_sort_nouns_changed"],
        "fenced_blocks": {"now": MAIN.read_bytes().count(b"```ve "), "previous_run": (PREV_DIR / "translation.ve.md").read_bytes().count(b"```ve ")},
        "fenced_units": {k: v for k, v in cp["x3_fences"].items()}, "fenced_units_now": sorted(cp["x3_fences"]),
        "graph_nodes_unchanged": all(v["unchanged"] for v in cp["x3_fenced_units"].values() if v["now"] is not None),
        "units_differing_from_start_document": cp["units_differing_from_start"], "units_new_now": cp["units_new_now"],
        "existing_fenced_units_that_changed": [k for k, v in cp["x3_fences"].items() if v.get("unchanged") is False],
        "sort_entity": "the carried sort `entity` has the noun “thing” (plural “things”), never the reserved word “entity” (asserted by repair_20261017T1800Z.py --check)",
        "checkpoints": {"final": "evidence/checkpoint-final.json"}}
    m["rust_time_limit"] = {"rule": "DRI 2026-10-14 15:30Z (3)", "VE_RUST_TIMEOUT": "unset (default)", "prlimit": "not used", "cap_raised": False,
                            "note": "no check needed a raised limit; no cap or peak resident set to record" + (f"; hard-constraint queries answered on the first run: {not unavailable}")}
    m["changes_against_previous_run"] = {
        "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger), "changed_or_replaced_ids": changed_units, "added_ids": [], "removed_ids": [],
        "units_newly_covered": [], "units_with_status_change": {}, "units_changed_by_audit_repair": [], "units_changed_by_feature_upgrade": [], "units_changed_ledger_note_only": LEDGER_NOTES,
        "open_terms_added": added_terms, "open_terms_removed": removed_terms, "open_terms_count_before_after": [pm["open_terms_count"], len(open_terms)],
        "reading_sets_before_after": [4, 4], "choices_before_after": [32, 32],
        "predicates_added": [], "predicates_removed": [], "predicates_changed": [], "sorts_added": [], "sort_noun_changed": [], "constants_added": [],
        "translation_byte_identical_to_previous_run": MAIN.read_bytes() == (PREV_DIR / "translation.ve.md").read_bytes(),
        "ledger_annotation_changes": "status_in_previous_run regenerated; the notes, expressible fences, audit_repair records and (u0235) recorded claim and trigger `pre` of u0095, u0002, u0235; everything else carried"}
    assert m["changes_against_previous_run"]["translation_byte_identical_to_previous_run"]
    m["language_changes_since_previous_tag"] = {
        "from": PREV_TAG, "to": TAG,
        "merged": {
            "infra/eff-20261019-1 (eff-20261019-1)": "tools/regen_generated.py builds and pins ve_service first (Python tooling only): no product change",
            "feature/me-5 (me-5)": "lean/VE/Calc/{Linear,FourierMotzkin,Derive,DeriveExamples}.lean: derivations over rational unknowns; DELTA: public output none (no service mode, command, route, schema, Python or Rust file)",
            "feature/jt-1b (jt-1b)": "lean/VE/Judgments/Status.lean (dependence, unit status, usage map of `judgments@0`); DELTA: reached by no service mode, route or document check before JT-2; diagnostics reached by no route",
            "feature/et-8 (et-8)": "two harnesses and README text; DELTA: no product code changed",
            "feature/ar-10a (ar-10a)": "the profile-gate table (VE.Compose.gateOf profileTable): a list with an unregistered profile is refused for that profile first (fault order, text only); Python reads ve/profile_table.json and its gate mirror (`checker_family`) is deleted. Verdicts do not move",
            "infra/arch-20261019-1 (AR-17)": "the readings route relays Lean's S2 row (checked for schema and binding) instead of recomputing it; one wording changes in the readings report's `checked_by.python` (45 records)",
            "feature/pk-1b (pk-1b)": "norm-defaults layered cases dispatch through a kind table (`kindCase`, proved equal to `layeredCase`); DELTA: output identical (445 invocations, 0 differences)",
            "infra/arch-20261019-2 (AR-16a)": "ve/document.py moved into the package ve/document/ verbatim; DELTA: none (63 of 63 definitions verbatim, 0 differences on nine corpora)",
            "feature/ap-1a (ap-1a)": "lean/VE/Acts/{LexicalBase,Lexical,Compat}.lean and the profile-aware decoder: lexical acts; DELTA: public output none, because `acts@0` has no profile row until ap-1b (the envelope refuses it as today)"},
        "merge_commits_listed": merged,
        "checked_by": ("git diff " + PREV_TAG + ".." + TAG + " --shortstat: " + diff_all + "; git diff " + PREV_TAG + ".." + TAG + " --shortstat -- ve lean rust conformance: " + diff_stat +
                       ". Read: the DELTA.md of ap-1a, AR-16a, AR-17, ar-10a, et-8, jt-1b, me-5, pk-1b and the report of eff-20261019-1. None adds a wording, a construct or a profile a document can use: "
                       "ap-1a and jt-1b add Lean modules behind profiles the envelope still refuses (measured: evidence/new-profile-probe.json), me-5 and pk-1b are unreachable from or identical on every recorded input, ar-10a and AR-17 change "
                       "the text of a refusal or a report only, AR-16a and eff-20261019-1 are refactors/tooling. The translation was rebuilt from the carried start document and is byte-identical to the previous run's"),
        "newly_expressible_features": 0, "units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
        "newly_measurable": ("`acts@0` and `judgments@0` exist in Lean but no document can name them yet (ap-1b and JT-2 are the batches that open them): the 17 units whose act phrase needs a workaround (act_workaround_m4) and the "
                             "judgment terms (507 units, 88,996 B) wait for them; the render differs from the previous run's in " + str(render_diff_lines) + " lines"),
        "what_made_the_difference": "nothing in the language: no unit gained or lost a status; the three ledger notes of unclaimed headings were corrected from the audit"}
    m["seeded_bugs"] = json.load(open(RUN / "evidence/seeded-bugs.json")) if (RUN / "evidence/seeded-bugs.json").exists() else {"pending": True}
    m["plan_repair_AT0p_state"] = {u_: "AT-0p (attitudes plan, DRI AT2): carried unchanged, shape asserted again: guard = ( C(s) and knowingly_engages_N(c, s) ) or thinks_quite_likely_N(c, s), two binary open terms on (claude_instance, situation) (u0165.s03: one pair per candidate); not a changed unit in this run"
                                   for u_ in HC_UNITS}
    m["plan_repairs_by_plan"] = {"none this run": []}
    whole = json.dumps({k: v for k, v in m.items() if k not in ("checked_content_main_chain", "language_changes_since_previous_tag", "presupposition_ps0p", "quantities_qt0p", "open_term_class_removed_since_instrument",
                                                                "open_term_class_reasons_new_terms", "seeded_bugs", "judgment_term_units_differing_from_phase1", "audit_faults_listed_on_unclaimed_units")}, ensure_ascii=False)
    for stale in ("wording not admitted", "not admitted in VE English", "waits for PS-6r", "force-u0125", "exception_to_never_denying", "thought_likely", "knowingly_<", "damaging_cyberweapon_or_malicious_code",
                  "restricted_action_knowing_or_quite_likely", "flat “either", "three 'should' reading sets carry content", "hard-queries-document-diff"):
        assert stale not in whole, stale
    assert_no_traces(by_id)
    dump("metrics.json", m)
    print(json.dumps({k: m[k] for k in ("claimed_covered_bytes", "claimed_covered_percent", "audit_verified_covered_bytes", "audit_verified_covered_percent",
                                         "audit_verified_metadata_bytes", "claimed_but_not_audit_verified_bytes", "changed_units")}))
    print(dict(u), dict(nb))
    print("probe_same:", probe_same, "disc_same:", disc_same, "comp_same:", comp_same, "hard_same_bytes:", hard_probe_same_bytes, "ask_same:", ask_same, "nd_concl_same:", nd_conclusions_same, "rt_same:", english_round_trip_same)
    print("judgment units:", jt_units["total"], jt_bytes["total"], "differing from phase 1:", len(jt_diff))


if __name__ == "__main__":
    main()
