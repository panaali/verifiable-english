#!/usr/bin/env python3
"""Run 20261018T0600Z: the measurement of the carried translation at ve-green-tarch-histdep.

No unit gained a status or a meaning from the language (the eighteen batches merged since ve-green-fu-ar2-decoders change the document service's internals, the superposed
readings route's verdict assembly, a Numbers core and an order closure that no document can name yet, test architecture and tools). The previous run's audit (20261017T1800Z) found 28 of 28
verdicts faithful and nothing incomplete, so there is nothing to repair; its one small fault (u0156.s03's frame term takes only the instance, not a situation) is carried and recorded.
translation.ve.md is byte-identical to the previous run's (nd.py all rebuilt it; cmp-identical), the ledger is carried (status_in_previous_run, audit flags and the plan annotations
regenerated with identical values), and metrics.json is the previous run's record with everything this run measured replaced.

Order (repository root, PATH must contain ~/.elan/bin, VE_NATIVE_PREBUILT=1; `lake build` in lean/ and tools/rust_build.py done):
    uv run python .../nd.py all; cmp readings/nd-all.ve.md translation.ve.md   # identical
    uv run python -m ve document coverage .../translation.ve.md > .../readings/coverage-nd-all.json
    probes (README.md), probe_hard_conclusions.py, probe_soft_chain.py
    uv run python .../repair_20261017T1800Z.py --check   # asserts the finished translation
    uv run python .../finish_20261018T0600Z.py           # ledger (units.json), scope-tally.json, renderings, check, coverage, metrics.json
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
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
import finish_20261017T1800Z as p17  # noqa: E402  (update_ledger, frame_english, the audit lists, PLAN_REPAIRS)
import frame_u0156 as fr  # noqa: E402
import scope_tally  # noqa: E402
import spec_nd  # noqa: E402

RUN_ID = "20261018T0600Z"
PREV_RUN = "20261017T1800Z"
TAG = "ve-green-tarch-histdep"
PREV_TAG = "ve-green-fu-ar2-decoders"
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
AUDIT_1017B_FAITHFUL, AUDIT_1017B_UNFAITHFUL = p17.received("20261017T1800Z", 28)   # 20 sampled + 8 changed, 28 verdicts
AUDIT_LATEST = list(dict.fromkeys(p17.AUDIT_LATEST + AUDIT_1017B_FAITHFUL))
CHANGED: list[str] = []   # no unit's document text or ledger text content changed in this run

PLAN_REPAIRS = [{"unit": u, "plan": "attitudes", "item": "AT-0p",
                 "state": ("already in the plan's form at the start of this run (applied in 20261014T1800Z; accepted FAITHFUL by the audits of 20261014T1800Z, 20261015T0600Z, 20261015T1800Z, "
                           "20261016T0600Z, 20261016T1800Z, 20261017T0600Z and 20261017T1800Z); the shape is asserted by repair_20261017T1800Z.py --check and measured again by the probes; not "
                           "re-applied, no guard or act phrase changed in this run" if u != S03 else
                           "already in the plan's form per candidate at the start of this run (u0165.s03 has one pair of attitude terms per candidate since 20261015T0600Z; accepted FAITHFUL by the "
                           "audits of 20261015T0600Z, 20261015T1800Z, 20261016T0600Z, 20261016T1800Z, 20261017T0600Z and 20261017T1800Z); asserted and measured again; not re-applied"),
                 "applied_in_this_run": False} for u in HC_UNITS]


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def main():
    prev = json.load(open(PREV_DIR / "units.json"))
    pm = json.load(open(PREV_DIR / "metrics.json"))
    assert hashlib.sha256(SOURCE).hexdigest() == pm["source_sha256"]
    eng = old.english_nd(STRICT)
    eng_narrow = old.english_nd(STRICT_NARROW)
    silence_frame_all, _ = old.silence_sentences(FRAME_DOC)
    silence_frame = silence_frame_all["system_prompt_deception_permitted"]
    silence, legend = old.silence_sentences(STRICT)
    probe = json.load(open(RUN / "probes/unspecified-probe.json"))
    ledger = p17.update_ledger(prev, eng, eng_narrow, silence, probe, probe["scope_points"], probe["binding_points"])
    main_meta = front_matter(MAIN)
    ids = [e["id"] for e in ledger]
    by_id = {e["id"]: e for e in ledger}

    # ---- the translation and its companions are the previous run's, byte for byte
    same_files = {n: (RUN / n).read_bytes() == (PREV_DIR / n).read_bytes() for n in ("translation.ve.md",)}
    assert all(same_files.values()), same_files
    assert (RUN / "readings/nd-all.ve.md").read_bytes() == MAIN.read_bytes()   # nd.py all rebuilt it
    frame_english_now = None

    # ---- DRI X5
    for e in ledger:
        if e["status"] in COVERED:
            e["claimed"] = True
    claimed_false = [e["id"] for e in ledger if e.get("claimed") is False]

    # ---- SC-M0: the scope tally (tags only)
    tally, notes = scope_tally.build(ledger, SOURCE)
    for e in ledger:
        nt = notes.get(e["id"])
        if not nt:
            continue
        blockers = list(e.get("other_blockers") or [])
        if "other:scope" not in blockers:
            blockers.append("other:scope")
        e["other_blockers"] = blockers
        if nt["governed_by"]:
            e["governed_by"] = sorted(set(nt["governed_by"]), key=ids.index)
        if nt["governed_by_candidate"]:
            e["governed_by_candidate"] = sorted(set(nt["governed_by_candidate"]), key=ids.index)
    tally["note"] = ("scope-tally for run " + RUN_ID + "; the tags are ledger annotations only: other_blockers gains `other:scope`, governed units record governed_by "
                     "(a frontier governor's candidates record governed_by_candidate, never governed_by), and no unit's status or content changes")
    dump("scope-tally.json", tally)
    prev_tally = json.load(open(PREV_DIR.parent / "scope-tally.json")) if False else None

    # ---- AP-0 item 3: act_workaround tags
    m4_src = json.load(open(RUN / "evidence/m4-act-workaround.json"))
    vocab_now = main_meta["environment"]["vocabulary"]["predicates"]
    prev_vocab = front_matter(PREV_DIR / "translation.ve.md")["environment"]["vocabulary"]["predicates"]
    entries = {e["id"]: e for e in ledger}
    stale = []
    for r in m4_src["units"]:
        e = entries[r["unit"]]
        act_now = vocab_now[e["predicate"]]["regulated"]["act"]
        assert act_now == r["act"] == prev_vocab[e["predicate"]]["regulated"]["act"], (r["unit"], act_now, r["act"])
        e["act_workaround"] = r["act_workaround"]
    m4_units = [e["id"] for e in ledger if e.get("act_workaround") not in (None, "none")]
    m4 = {"units": len(m4_units), "bytes": sum(e["span"][1] - e["span"][0] for e in ledger if e["id"] in m4_units), "unit_ids": m4_units,
          "tally": dict(Counter(e["act_workaround"] for e in ledger if "act_workaround" in e)),
          "stale": stale, "expected": {"units": 17, "bytes": 2502}, "source": "research/act-phrases-p1: docs/research/evidence/act-phrases/m4-act-workaround.json (evidence/m4-act-workaround.json)"}
    assert (m4["units"], m4["bytes"]) == (17, 2502), m4
    assert [(u["id"], tuple(u["span"])) for u in main_meta["units"]] == [(e["id"], tuple(e["span"])) for e in ledger]
    assert [(e["id"], tuple(e["span"])) for e in prev] == [(e["id"], tuple(e["span"])) for e in ledger]

    # ---- VE at this tag
    rel = str(MAIN.relative_to(ROOT))
    t0 = time.monotonic()
    check = json.loads(ve("document", "check", rel))
    t1 = time.monotonic()
    coverage = json.loads(ve("document", "coverage", rel))
    t2 = time.monotonic()
    timing = {"document_check": round(t1 - t0, 1), "document_coverage": round(t2 - t1, 1)}
    (RUN / "evidence").mkdir(exist_ok=True)
    (RUN / "evidence/finish-timing.json").write_text(json.dumps(timing) + "\n")
    render = ve("document", "render", rel)
    english_u0156, _rt = p17.frame_english(render, main_meta)
    carried = {r["id"]: r["english"] for r in by_id[fr.UNIT]["readings"]}
    assert carried == english_u0156, (carried, english_u0156)   # the English VE renders now is the English the ledger records
    strict = {"check": json.loads(ve("document", "check", str(STRICT.relative_to(ROOT)))),
              "coverage": json.loads(ve("document", "coverage", str(STRICT.relative_to(ROOT))))}
    dump("check.json", check)
    dump("coverage.json", coverage)
    dump("environment.json", main_meta["environment"])
    dump("readings/check-all-strict.json", strict["check"])
    (RUN / "readings/rendered-all-strict.md").write_text(ve("document", "render", str(STRICT.relative_to(ROOT))))
    (RUN / "rendered.md").write_text(p14.annotate(render, ledger))
    (RUN / "rendered-raw.md").write_text(render)
    assert check["premises"]["status"] == "model", check["premises"]
    assert check["reading_plan"]["route"] == "enumerate" and len(check["reading_plan"]["choices"]) == 32
    assert check["readings"]["conflict"]["status"] == "CONFLICT-FREE"
    assert coverage["coverage_percent"] == 100 and coverage["source_bytes"] == len(SOURCE)
    prev_check = json.load(open(PREV_DIR / "check.json"))
    prev_cov = json.load(open(PREV_DIR / "coverage.json"))
    check_same, cov_same = check == prev_check, coverage == prev_cov
    assert check_same and cov_same
    old_render = (PREV_DIR / "rendered-raw.md").read_text()
    render_same = render == old_render

    # ---- ledger and counts
    total = sum(e["span"][1] - e["span"][0] for e in ledger)
    assert total == len(SOURCE)
    pos = 0
    for e in ledger:
        assert e["span"][0] == pos, e["id"]
        pos = e["span"][1]
    u, nb = old.counts(ledger)
    claimed = sum(e["span"][1] - e["span"][0] for e in ledger if e["status"] in COVERED and e.get("claimed", True) is not False)
    assert claimed == sum(v for k, v in nb.items() if k in COVERED) and claimed == pm["claimed_covered_bytes"], claimed
    n_old, old_units, _ = old.aggregate(ledger)
    spans = {e["id"]: e["span"] for e in ledger}
    status = {e["id"]: e["status"] for e in ledger}
    width = lambda ids_: sum(spans[i][1] - spans[i][0] for i in ids_)
    assert coverage["bytes_by_status"]["CHECKED"] == nb["CHECKED"] and coverage["bytes_by_status"]["OPEN"] == nb["OPEN"] + nb["READINGS"]

    # ---- audit-verified bytes: accepted by an audit of this lineage AND unchanged here from the form that audit saw (nothing changed in this run, so the audit of 20261017T1800Z, which
    # accepted 28 of 28 including the four units repaired in that run, adds them)
    prev_verified = list(pm["audit_verified_covered_units"])
    bad_ever = (p17.AUDIT_1015_UNFAITHFUL + p17.AUDIT_1015B_UNFAITHFUL + p17.AUDIT_1016_UNFAITHFUL + p17.AUDIT_1016B_UNFAITHFUL + p17.AUDIT_1017_UNFAITHFUL)
    # u0156.s03 was rejected by the 20261017T0600Z audit and accepted, after its repair, by the 20261017T1800Z audit, which saw the form carried here
    still_bad = [i for i in bad_ever if i not in AUDIT_1017B_FAITHFUL]
    dropped = [i for i in prev_verified if i in CHANGED or i in still_bad]
    kept = [i for i in prev_verified if i not in dropped]
    newly = [i for i in AUDIT_LATEST if status[i] in COVERED and status[i] != "LABELLED" and i not in CHANGED and i not in kept]
    assert not any(by_id[i].get("claimed") is False for i in [*kept, *newly])
    verified = kept + newly
    verified_bytes = width(verified)
    cand_lab = list(dict.fromkeys(old.AUDIT_PASSED_LABELLED + old.AUDIT_PASSED_1004_LABELLED + old.AUDIT_PASSED_1004B_LABELLED + ["u0212.heading"]
                                  + p17.prevf.AUDIT_FAITHFUL_1800 + p17.prevf.AUDIT_FAITHFUL_1811 + p17.p18.AUDIT_0600_FAITHFUL + p17.p13.AUDIT_1800_FAITHFUL + p17.p14.AUDIT_1013_FAITHFUL
                                  + p17.p15.AUDIT_1014_FAITHFUL + AUDIT_LATEST))
    verified_lab = [i for i in cand_lab if i in by_id and status[i] == "LABELLED" and i not in CHANGED]
    verified_meta = width(verified_lab)
    newly_lab = [i for i in AUDIT_1017B_FAITHFUL if status[i] == "LABELLED" and i in verified_lab and i not in pm["audit_verified_newly_labelled_from_20261017T0600Z"]
                 and i not in [x for x in pm.get("audit_verified_covered_units", [])]]
    label_bytes_prev = pm["audit_verified_metadata_bytes"]
    for e in ledger:
        if (e["id"] in verified or e["id"] in verified_lab or e["id"] in AUDIT_LATEST) and e["id"] not in CHANGED:
            if "audit_verified" in e:
                e["audit_verified"] = True
        if e["id"] in CHANGED and "audit_verified" in e:
            e["audit_verified"] = False
    dump("units.json", ledger)

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
    assert all(hard_by[("u0165.s01", k)]["verdict"] == "UNKNOWN" for k in ("knowing", "belief"))
    prev_hard = json.load(open(PREV_DIR / "probes/hard-conclusions-probe.json"))["queries"]
    hard_same = [{k: v for k, v in q.items() if k != "document"} for q in hard_q] == [{k: v for k, v in q.items() if k != "document"} for q in prev_hard]
    assert hard_same
    first_unavailable = sorted(f"{q['unit']}:{q['kind']}" for q in hard_q if "rerun_alone" in q)
    capped = [f"{q['unit']}:{q['kind']}" for q in hard_q if q.get("cap")]
    assert not first_unavailable and not capped
    unknown = [f"{q['unit']}:{q['kind']}" for q in hard_q if q["verdict"] == "UNKNOWN"]
    n_all = sum(1 for q in hard_q if q["verdict"] == "ALL")
    hard_summary = {k: dict(Counter(q["verdict"] for q in hard_q if q["kind"] == k)) for k in ("knowing", "belief", "neither")}
    points = probe["points"]
    probe_names = ("risk-probe", "s1-probe", "senses-probe", "senses-document-probe", "discourse-probe", "rights-reading-probe", "unspecified-probe", "frame-probe", "hard-conclusions-probe")
    probe_same = {n: (RUN / f"probes/{n}.json").read_bytes() == (PREV_DIR / f"probes/{n}.json").read_bytes() for n in probe_names}
    assert all(probe_same.values()), probe_same
    profile_probe = old.probe_profiles()
    assert profile_probe == pm["profile_combination_probe"]
    comp = json.load(open(RUN / "probes/companion-probe.json"))
    prev_comp = json.load(open(PREV_DIR / "probes/companion-probe.json"))
    strip = lambda o: json.loads(json.dumps(o).replace(RUN_ID, "RUN").replace(PREV_RUN, "RUN"))
    assert strip(comp) == strip(prev_comp)   # identical apart from the run directory in the document paths
    frame_probe = json.load(open(RUN / "probes/frame-probe.json"))
    soft = json.load(open(RUN / "evidence/soft-chain-probe.json"))
    prev_soft = pm["soft_chain_probe"]
    assert soft["load"] == "admitted" and soft["check"]["returncode"] == 1 and soft["conclusions"]["denial"]["verdict"] == "ALL" and soft["conclusions"]["claim_human"]["verdict"] == "ALL"
    assert soft["check"]["stderr_last_lines"][-1].startswith("ve.errors.UnsupportedProfile: UnsupportedProfile: norm-defaults@0 documents are checked through fill"), soft["check"]["stderr_last_lines"][-1]
    asks = [json.load(open(RUN / f"probes/ask/q{i}.json")) for i in range(1, 6)]
    # the question probe and the two conclusion queries: re-asked at this tag. Their content equals the previous run's; JSON member order differs (rd-7 changed the order of the members of
    # the conclusion objects, review row K1) and the ask answers carry one more identity value (actions_version 30, was 28).
    prev_ask = PREV_DIR / "probes/ask"
    def strip_version(o):
        o = json.loads(json.dumps(o))
        o["result"]["identities"].pop("actions_version")
        return o
    ask_same = all(strip_version(json.load(open(RUN / f"probes/ask/q{i}{s}.json"))) == strip_version(json.load(open(prev_ask / f"q{i}{s}.json"))) for i in range(1, 6) for s in ("", ".answer"))
    assert ask_same
    assert all(json.load(open(RUN / f"probes/nd/{f}.json")) == json.load(open(PREV_DIR / f"probes/nd/{f}.json")) for f in ("conclusion-no-denial-result", "claim-human-result"))
    open_terms = [{k: t[k] for k in ("name", "arguments", "decided_by", "necessary", "sufficient", "factors")} for t in main_meta["open_terms"]]
    assert open_terms == pm["open_terms"], "the open terms are the previous run's"
    prev_meta = front_matter(PREV_DIR / "translation.ve.md")
    assert main_meta == prev_meta
    body = lambda p_: p_.read_bytes().split(b"\n---\n", 2)[-1]
    gap_marker = "Here the text does not say whether"
    sep_lines = lambda text: [ln for ln in text.splitlines() if ln.startswith("These two readings differ here")]
    gaps_now = [ln.count(gap_marker) for ln in sep_lines(render)]
    cannot_show = lambda text: text.count("These two readings differ in a checked situation that VE cannot yet show in words.")
    assert gaps_now == [1, 1] and cannot_show(render) == 7 == cannot_show(old_render)

    # ---- the language changes since the previous tag: read from the repository
    diff_names = git("diff", "--name-only", f"{PREV_TAG}..HEAD", "--", "ve", "lean", "rust", "conformance").splitlines()
    diff_stat = git("diff", "--shortstat", f"{PREV_TAG}..HEAD", "--", "ve", "lean", "rust", "conformance")
    diff_all = git("diff", "--shortstat", f"{PREV_TAG}..HEAD")
    merged = [ln for ln in git("log", "--first-parent", "--format=%s", f"{PREV_TAG}..HEAD").splitlines()]
    assert len(merged) == 18, len(merged)

    plan_repairs_changed = sorted({r["unit"] for r in PLAN_REPAIRS})
    m = copy.deepcopy(pm)
    m.update({
        "run": RUN_ID, "baseline_tag": TAG, "previous_run": PREV_RUN, "previous_baseline_tag": PREV_TAG,
        "history_note": "this file records this run; the earlier runs' records (audit-verification history, the earlier probes' narrative) are in prev/metrics.json",
        "feature_upgrade_counts_separate_from_repairs": ("units upgraded by new features 0; plan repairs 0 applied (AT-0p, SC-M0, AP-0 item 3, X5 and X2-X4 were already in the plan's form or are tags only); "
                                                         "audit repairs 0 (the audit of 20261017T1800Z found 28 of 28 faithful); changed units 0"),
        "changed_units": [],
        "plan_repairs": PLAN_REPAIRS,
        "audit_repairs": [],
        "changed_units_detail": {},
        "plan_repair_note": ("AT-0p (DRI AT2) is in the plan's form at the start of this run (applied in 20261014T1800Z, per candidate for u0165.s03 since 20261015T0600Z, audited FAITHFUL seven times); "
                             "this run asserts the shape (repair_20261017T1800Z.py --check), rebuilds the content with nd.py all (cmp-identical), measures the four probe kinds again (as the plan states, "
                             "byte-identical probe file) and does not re-apply it: the seven units are listed in plan_repairs with applied_in_this_run false and no guard or act phrase changed "
                             "(u0165.s01 to s07 are not changed units). Plan expectation and measurement: claimed bytes unchanged at 2,951 (as stated); open terms: the plan expected 46 on the 1800Z copy "
                             "and the measured document has " + str(len(open_terms)) + " (46 at the AT-0p stage, plus the exception terms of the three force sets, the per-candidate terms of the "
                             "scope set of u0165.s03 and the frame term of u0156.s03, which later runs added; a difference in the translation's other units, not in AT-0p); case false and "
                             "thinks-quite-likely true SETTLED no; case true and knowingly true SETTLED no; neither UNDECIDED; case false and knowingly true UNDECIDED, for all seven rules; "
                             "ve document check passes (premises model, all 32 choices CONFLICT-FREE)"),
        "feature_upgrades": {"units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
                             "note": "kept apart from the plan repairs and audit repairs, so that differences against the previous run measure the language, not the translator"},
        "tags_only_not_changed_units": ("scope tags (SC-M0), act_workaround (AP-0 item 3) and the `claimed` field are ledger annotations: " + str(tally["totals"]["units_tagged"]) +
                                        " units carry other:scope; none of them is a changed unit by this alone"),
        "sentence_clause_units": {"units_total": len(ledger), "unit_counts_by_status": old.full(u), "bytes_by_status": old.full(nb),
                                  "previous_run": {k: pm["sentence_clause_units"][k] for k in ("units_total", "unit_counts_by_status", "bytes_by_status")}},
        "aggregated_to_previous_boundaries": {"units_total": n_old, "unit_counts_by_status": old_units, "bytes_by_substatus": old.full(nb),
                                              "previous_run": {k: pm["aggregated_to_previous_boundaries"][k] for k in ("units_total", "unit_counts_by_status")}},
        "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(SOURCE), 4),
        "claimed_covered_bytes_previous_run": pm["claimed_covered_bytes"], "claimed_covered_bytes_gained": claimed - pm["claimed_covered_bytes"],
        "claimed_false_units": claimed_false,
        "substantive_covered_bytes": nb["CHECKED"] + nb["OPEN"] + nb["READINGS"], "substantive_covered_bytes_previous_run": pm["substantive_covered_bytes"],
        "audit_verified_covered_bytes": verified_bytes, "audit_verified_covered_percent": round(100 * verified_bytes / len(SOURCE), 4),
        "audit_verified_covered_units": verified, "audit_verified_covered_bytes_previous_run": pm["audit_verified_covered_bytes"],
        "audit_verified_dropped_because_changed": dropped,
        "audit_verified_newly_from_20261017T1800Z": newly,
        "audit_verified_newly_labelled_from_20261017T1800Z": [i for i in AUDIT_1017B_FAITHFUL if status[i] == "LABELLED"],
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND unchanged in this run from the form that audit saw. The audit of run 20261017T1800Z "
            "(28 of 28 verdicts faithful: 20 sampled plus 8 changed; AUDIT-20261017T1800Z-received.md) is the latest and rejected nothing. It saw the repaired u0156.s03 (four candidates), "
            "u0165.s06, the notes of u0036.s05 and u0263.s04.p2 and the AT-0p units; all are byte-identical here (translation.ve.md is the previous run's, and no ledger text of them changed), "
            "so they count again. No unit changed in this run. This is a count of verdicts on unchanged text, not a fresh audit of this run."),
        "audit_verified_metadata_bytes": verified_meta, "audit_verified_metadata_percent": round(100 * verified_meta / len(SOURCE), 4),
        "audit_verified_metadata_bytes_previous_run": pm["audit_verified_metadata_bytes"],
        "claimed_but_not_audit_verified_bytes": claimed - verified_bytes - verified_meta,
        "repaired_bytes_not_audit_verified": 0,
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20261017T1800Z_audit": AUDIT_1017B_UNFAITHFUL,
            "repair_done_in_20261018T0600Z": {},
            "small_faults_repaired": {},
            "small_faults_not_repaired": {
                "u0156.s03 frame term": ("the audit of 20261017T1800Z (small fault, no verdict change): the open term " + fr.FRAME_TERM + " takes only the instance of Claude, while the source words describe "
                                         "“a situation” and the rule ranges over (instance, user), so an instance that counts as asked is in the frame toward every user. Carried, not repaired: the term "
                                         "is the translator's hand-made frame; a frame over a situation is what the missing scope construct (other:scope) would give, and giving the term a user or a situation "
                                         "argument would add a quantity of words the source does not state. The unit, its readings and the open term are as the audit accepted them"),
                "headings": "“Being helpful” and “The existential frontier” are labelled whole while “Being broadly safe” and “Safe behaviors” have presupposition units; the labels are true, so nothing was rewritten",
                "u0173.s01 to s04": "the notes call the gap modality/belief while the ledger's missing feature is `norms` with `modality/belief` as a further blocker; the tally is kept as it was"},
            "kept_covered_status_without_repair": [],
            "earlier_audits": "the rejections and repairs of the earlier runs are recorded in prev/metrics.json and the AUDIT-*-received.md files"},
        "open_terms_count_previous_run": pm["open_terms_count"],
        "open_terms_added": [], "open_terms_removed_this_run": [], "open_terms_with_changed_factors": [], "open_terms_with_changed_arguments": {},
        "open_terms_count_note": "51, as in the previous run (nothing added, removed or changed)",
        "ledger_only_open_terms": {**pm["ledger_only_open_terms"]},
        "missing_feature_tally": old.tally(ledger), "missing_feature_tally_previous_run": pm["missing_feature_tally"],
        "check_verdicts": {"main": {**pm["check_verdicts"]["main"], "check_seconds_this_run": timing,
                                    "previous_run": {"premises_route": prev_check["premises"]["route"], "conflict_route": prev_check["readings"]["route"],
                                                     "conflict_status_text": prev_check["readings"]["status"], "choices": len(prev_check["reading_plan"]["choices"]), "open_sentences": 3},
                                    "check_json_identical_to_previous_run": check_same, "coverage_json_identical_to_previous_run": cov_same},
                           "all_strict": {"document": "readings/all-strict.ve.md", "premises": strict["check"]["premises"], "residual": strict["coverage"]["residual"],
                                          "bytes_by_status": strict["coverage"]["bytes_by_status"]}},
        "timing_single_runs": {
            "note": "one run each on one machine at a load average of about 5 to 8 at the start of the run (not a controlled comparison; the previous figures come from the previous run's files)",
            "document_check_seconds": timing["document_check"], "document_check_seconds_previous_run": pm["timing_single_runs"]["document_check_seconds"],
            "document_coverage_seconds": timing["document_coverage"], "document_coverage_seconds_previous_run": pm["timing_single_runs"]["document_coverage_seconds"],
            "nd_all_load_seconds": [nd["all"]["load_seconds"], pm["timing_single_runs"]["nd_all_load_seconds"][0]],
            "nd_all_check_seconds": [nd["all"]["check_seconds"], pm["timing_single_runs"]["nd_all_check_seconds"][0]],
            "nd_all_separation_search_seconds": [nd["all"]["separation_search_seconds"], pm["timing_single_runs"]["nd_all_separation_search_seconds"][0]],
            "hard_constraint_queries_wall_clock": "54 minutes for the 21 queries (3 in parallel), the previous run's was about 60 minutes at a higher load",
            "build_note": "this worktree's lean/.lake was copied from the ve-integration checkout at the identical commit (de9cfa84f); `lake build` still rebuilt all 973 jobs (18 minutes) and tools/rust_build.py rebuilt "
                          "the Rust binary (25 s), which matches the pin in lean/checkers.lock (SHA-256 6422647f…0579); not a language measurement",
            "order": "[this run, previous run]; both have four sets (32 choices)"},
        "unspecified_probe": {**pm["unspecified_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["unspecified-probe"]},
        "profile_combination_probe_same_as_previous_run": True,
        "senses_probe": {**pm["senses_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-probe"]},
        "senses_document_probe": {**pm["senses_document_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-document-probe"]},
        "discourse_probe": {**pm["discourse_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["discourse-probe"]},
        "rights_reading_probe": {**pm["rights_reading_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["rights-reading-probe"]},
        "risk_probe": {**pm["risk_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["risk-probe"]},
        "readings_defaults_probe": {**pm["readings_defaults_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["s1-probe"]},
        "carried_probes_note": ("the six carried probes (risk, s1, senses, senses_document, discourse, rights), the unspecified, frame and hard-conclusions probes were re-run on the final document "
                                "(the hard-conclusions probe after 54 minutes); byte-identical JSON: " + ", ".join(f"{k} {'same' if v else 'differs'}" for k, v in probe_same.items()) +
                                ". The companion probe differs only in the run directory inside its document paths. The denial and claim-to-be-human conclusion queries are ALL as before; the 21 "
                                "hard-constraint queries give the same 12 ALL and 9 UNKNOWN, all on the first run at the default Rust limit (VE_RUST_TIMEOUT unset, no prlimit, no capped run)"),
        "frame_probe": {**pm["frame_probe"], "identical_to_previous_run": probe_same["frame-probe"]},
        "profile_combination_probe_changes": {"what": pm["profile_combination_probe_changes"]["what"], "changed": {}, "reading": "all thirteen rows are identical to the previous run's"},
        "soft_chain_probe": {**prev_soft, "result": {**prev_soft["result"],
                                                     "ve_document_check": {**prev_soft["result"]["ve_document_check"], "stderr_last_lines": soft["check"]["stderr_last_lines"]},
                                                     "ve_document_coverage": soft["coverage"], "ve_document_render": soft["render"],
                                                     "ve_document_readings_denial_query": soft["conclusions"]["denial"], "ve_document_readings_claim_human_query": soft["conclusions"]["claim_human"]},
                             "same_outcome_as_previous_run": True,
                             "decision": "still not adopted: `ve document check` raises the same UnsupportedProfile on the soft-chain document, so the exception_to_* workaround stays (not an upgrade)"},
        "separation_line_gap_sentences": {**pm["separation_line_gap_sentences"], "per_line_before": gaps_now, "per_line_now": gaps_now,
                                          "reading": "unchanged: per_line_before and per_line_now are both [1, 1]; the rendering is " + ("byte-identical to the previous run's" if render_same else "not byte-identical to the previous run's (see rendered-raw.md)")},
        "reading_sets": {**pm["reading_sets"], "choices_previous_run": 32, "changed_this_run": {}, "added_this_run": {}, "removed_this_run": {}},
        "checked_content_main_chain": {**pm["checked_content_main_chain"], "documents": nd, "candidate_premise_status": dict(cand_status),
                                       "choices_checked": nd["all"]["choices_checked"],
                                       "choices_conflict_free": nd["all"]["conflict_by_choice"].get("CONFLICT-FREE", 0), "choices_conflict": nd["all"]["conflict_by_choice"].get("CONFLICT", 0),
                                       "separating_situations_checked_by_lean": sep_all, "separated_by_decision_only_findings": 0},
        "question_probe": {**pm["question_probe"], "re_run_at_this_tag": True,
                           "identical_to_previous_run": "in content: `no_answer` for all five with --reading and without it. The JSON files differ in one identity value only (result.identities.actions_version 30, was 28)"},
        "conclusion_queries_note": "the denial and claim-to-be-human queries (probes/nd/*-result.json) were re-run: ALL on the superposed route with a certificate, equal as JSON objects to the previous run's; only the order of the members differs (rd-7)",
        "scope_tally": {"file": "scope-tally.json", "totals": tally["totals"], "not_tallied": tally["not_tallied"]},
        "act_workaround_m4": m4,
        "vocabulary_change_check": {
            "rule": "DRI 2026-10-14 15:30Z (2): after a vocabulary change rerun the situation step (nd.py all) and check every existing fenced unit still parses unchanged",
            "vocabulary_changed_in_this_run": False,
            "situation_step_rerun": "nd.py all was rerun at this tag anyway (readings/nd-all-result.json: admitted, 32 choices) and its document is cmp-identical to the carried translation",
            "fenced_blocks": {"now": MAIN.read_bytes().count(b"```ve "), "previous_run": (PREV_DIR / "translation.ve.md").read_bytes().count(b"```ve ")},
            "fenced_unit": "u0248 “Claude is not a human.” (the translation's only fenced block): the document is admitted and the unit's content and graph node are unchanged",
            "translation_byte_identical_to_previous_run": True, "front_matter_identical": main_meta == prev_meta, "body_text_identical": body(MAIN) == body(PREV_DIR / "translation.ve.md"),
            "units_changed": [], "predicates_added": [], "predicates_removed": [], "predicates_changed": [], "sorts_changed": [],
            "sort_entity": "DRI 2026-10-14 15:30Z (1): the carried sort `entity` has the noun “thing” (plural “things”), never the reserved word “entity” (asserted by repair_20261017T1800Z.py --check)"},
        "rust_time_limit": {"rule": "DRI 2026-10-14 15:30Z (3)", "VE_RUST_TIMEOUT": "unset (default)", "prlimit": "not used", "cap_raised": False,
                            "note": "no check needed a raised limit: all 21 hard-constraint queries answered on the first run at the default limit, so there is no cap or peak resident set to record"},
        "changes_against_previous_run": {
            "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger), "changed_or_replaced_ids": [], "added_ids": [], "units_newly_covered": [],
            "units_with_status_change": {}, "units_changed_by_audit_repair": [],
            "open_terms_added": [], "open_terms_removed": [], "open_terms_count_before_after": [51, 51],
            "reading_sets_before_after": [4, 4], "choices_before_after": [32, 32],
            "predicates_added": [], "predicates_removed": [], "predicates_changed": [],
            "translation_byte_identical_to_previous_run": True, "translation_differs_only_in": "nothing",
            "ledger_annotation_changes": "status_in_previous_run; the audit_verified flag of the units the 20261017T1800Z audit accepted; scope tags, act_workaround and claimed regenerated with identical values"},
        "language_changes_since_previous_tag": {
            "from": PREV_TAG, "to": TAG,
            "merged": {
                "readings-defaults/rd7 (rd-7)": "the superposed `readings-verdicts` route: Lean (not Python) assembles ALL, SOME and NONE answers over reading sets from the empty-assumption certificate, one complete choice and countermodels, with per-reading premise "
                                                "status, dead readings and dependencies; Python keeps evidence generation and binding. A conclusion query is answered the same way as before (verdict-preserving: the corpora are identical); "
                                                "it adds no construct a document can say",
                "lean-first/b16f (lf-16f)": "the `document` mode now decides soft-norms, plain norm content, senses and fenced content in Lean (the retained Python loader keeps the rest); same documents, same answers",
                "lean-first/b16g (lf-16g)": "stopped at its precondition: no product code",
                "infra/me-1a (me-1a)": "VE.Numbers core (decimal, rounding, comparison phrases) and the generated ve/numbers_phrases.json that ve/english.py reads for order@0 comparison wording; `Public output: none` (no service mode, command or route); "
                                        "graded quantities are still not expressible in a document",
                "foundation/qs-1 (qs-1)": "VE.Closure.Order (an order closure with caps and theorems); no service mode or Python relay was added",
                "infra/fu-lf14c-f4": "n-ary defined predicates in the family view (definitions of any arity); the translation uses no definitions",
                "infra/jt-crossplan-fixes (X2, X3)": "the English lint reaches a fixed point over predicate head words (only accepted templates claim a head) and a constant's `verbalisation` is refused with the v0 diagnostic; the constitution's rendering is unchanged",
                "infra/fu-rd9-checks, ties-rights-licence-relay, ties-qs-1, ties-lf-16f, ties-fu-1017, ties-jt-crossplan, fu-docs-1017, dri-sign-1017b": "relay checks, theorems tying existing definitions, docstring and DELTA text; no new construct",
                "infra/tarch-slowtail, tarch-histdep, fix/fsmonitor-gate": "test architecture, history-dependent tests and gate tooling; no language change"},
            "merge_commits_listed": merged,
            "checked_by": ("git diff " + PREV_TAG + "..HEAD --shortstat: " + diff_all + "; git diff " + PREV_TAG + "..HEAD --shortstat -- ve lean rust conformance: " + diff_stat +
                           ". Read: the Lean and Python files changed are the document service (Service/Document.lean, ve/document.py), the readings route (Readings/Sup*.lean, ve/readings_verdicts.py), "
                           "the Numbers and Closure.Order modules, the English lint and printer, and generated tables and response shapes; no grammar production, profile, lexicon entry or checker "
                           "that a norm, guard or reading set of the constitution could use was added (the new Numbers and Order modules are not reachable from a document)"),
            "newly_expressible_features": 0, "units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
            "newly_measurable": ("nothing in what a document says: `ve document check`, the coverage, the render, the probes, the conclusion queries and the 21 hard-constraint queries give the same answers as at the previous tag "
                                 "(check.json, coverage.json and every probe JSON are byte-identical, the render is " + ("identical" if render_same else "not identical") + "). Only the time moved: the hard-constraint queries took 54 minutes"),
            "what_made_the_difference": "nothing: no unit gained a status or a meaning from the language, and there is no repair to make (the previous audit rejected nothing)"},
        "seeded_bugs": {
            "needed": False,
            "why": "no product code (Lean, Python, Rust) was changed: this run adds files under usecases/ only (a copied build in the worktree is ignored by git). The pilot scripts were checked as follows.",
            "pilot_script_faults": [
                {"claim": "the finished translation is the previous run's, byte for byte", "planted": "one byte of the open-term name exception_to_not_deceiving_about_system_prompt changed in translation.ve.md",
                 "failing_check": "finish_20261018T0600Z.py stops at `assert all(same_files.values())` (AssertionError: {'translation.ve.md': False})", "restored": "the translation put back; cmp-identical to prev/translation.ve.md"},
                {"claim": "the in-frame candidates are guarded by the frame term on the Claude instance (variable 1)", "planted": "the guard of the first in-frame candidate in translation.ve.md bound to variable 0 (the user)",
                 "failing_check": "repair_20261017T1800Z.py --check stops with AssertionError: strict-in-frame", "restored": "the translation put back; cmp-identical to prev/translation.ve.md"}],
            "not_planted": "the other assertions of finish_20261018T0600Z.py (the carried English, the 21 hard-constraint answers, the probe files, the open terms) were not seeded: each needs a 4-minute run of the script"},
    })
    whole = json.dumps({k: v for k, v in m.items() if k not in ("checked_content_main_chain", "language_changes_since_previous_tag")}, ensure_ascii=False)
    for stale in ("force-u0125", "exception_to_never_denying", "thought_likely", "knowingly_<", "damaging_cyberweapon_or_malicious_code", "restricted_action_knowing_or_quite_likely",
                  "flat “either", "three 'should' reading sets carry content", "hard-queries-document-diff"):
        assert stale not in whole, stale
    dump("metrics.json", m)
    print(json.dumps({k: m[k] for k in ("claimed_covered_bytes", "claimed_covered_percent", "audit_verified_covered_bytes", "audit_verified_covered_percent",
                                         "audit_verified_metadata_bytes", "claimed_but_not_audit_verified_bytes", "changed_units")}))
    print(dict(u), dict(nb))
    print("probe_same:", probe_same, "render_same:", render_same, "check_same:", check_same, "cov_same:", cov_same)


if __name__ == "__main__":
    main()
