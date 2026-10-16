#!/usr/bin/env python3
"""Run 20261015T0600Z: the repairs of the units the audit of run 20261014T1800Z rejected or flagged (u0165.s03: one pair of attitude terms per candidate; the
record of good_judgment; the ledger entry of u0126), the AT-0p shape verified, the scope tally (SC-M0) and the act-workaround tags (AP-0 item 3) re-generated;
then the measurement at ve-green-lf-14b.

Order (repository root, PATH must contain ~/.elan/bin, VE_NATIVE_PREBUILT=1; `lake build` in lean/ and tools/rust_build.py done):
    uv run python .../repair_20261015T0600Z.py            # base/ -> translation-without-content.ve.md, readings/all-strict.ve.md, readings/all-strict-narrow.ve.md
    uv run python .../nd.py all                           # about 2-3 min; then: cp readings/nd-all.ve.md translation.ve.md
    uv run python -m ve document coverage .../translation.ve.md > .../readings/coverage-nd-all.json
    probes (README.md)
    uv run python .../finish_20261015T0600Z.py            # ledger (units.json), scope-tally.json, renderings, check, coverage, metrics.json

The previous run's translation is `prev/translation.ve.md`; the units this run changed are in CHANGED below, split into plan repairs and audit repairs.
"""
from __future__ import annotations

import copy
import hashlib
import json
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
import finish_20261012T0600Z as prevf  # noqa: E402  (slice_result, concl: readers of the nd result and conclusion files)
import finish_20261012T1800Z as p18  # noqa: E402  (earlier notes)
import finish_20261013T0600Z as p13  # noqa: E402  (earlier notes)
import finish_20261014T1800Z as p14  # noqa: E402  (the previous run's notes, to replace exactly; annotate)
import s03_scope as sc  # noqa: E402
import scope_tally  # noqa: E402
import spec_nd  # noqa: E402

RUN_ID = "20261015T0600Z"
PREV_RUN = "20261014T1800Z"
TAG = "ve-green-lf-14b"
PREV_TAG = "ve-green-repo-map-untracked"
COVERED = old.COVERED
SOURCE = old.SOURCE
front_matter = old.front_matter


def ve(*args):
    """`ve ...` run as the previous finish scripts did, with one addition: an exit code 5 (CheckerUnavailable: the Rust checker's default 5-second limit on a loaded machine) is
    never a verdict, so the identical call is repeated up to three times; any other failure stops the run."""
    for attempt in range(3):
        proc = subprocess.run([sys.executable, "-m", "ve", *args], cwd=ROOT, capture_output=True, text=True)
        if proc.returncode == 0:
            return proc.stdout
        if proc.returncode != 5:
            break
    raise SystemExit(f"ve {' '.join(args)} failed (rc {proc.returncode}):\n{proc.stderr[-1500:]}\n{proc.stdout[-800:]}")


dump = lambda p, o: (RUN / p).write_text(json.dumps(o, indent=2, ensure_ascii=False) + "\n")
PREV_DIR = RUN / "prev"
MAIN = RUN / "translation.ve.md"
STRICT = RUN / "readings/all-strict.ve.md"
STRICT_NARROW = RUN / "readings/all-strict-narrow.ve.md"
HC_UNITS = [f"u0165.s0{i}" for i in range(1, 8)]
SETS_KEPT = ["u0036.s05", "u0156.s03", "u0263.s04.p2"]
U0125 = "u0125.s04.p2"
U0173 = "u0173.s01"
U0123 = "u0123.s02.p1"
S03 = sc.UNIT
PER_UNIT = {unit: (term, words, pred) for unit, _rule, pred, term, _act, words in spec_nd.HARD}
# changed units: u0165.s03 (audit repair: one pair of attitude terms per candidate), u0052.s01 (audit repair: the record of good_judgment declares its sorts),
# u0126 (audit repair: the ledger entry no longer lists the removed open term ethical_harm), u0173.s01 (note only). The AT-0p guards of u0165.s01 to s07 are
# carried from the previous run (verified, not re-applied); the plan repair is listed so that the audit can see its state.
U0052 = "u0052.s01"
U0126 = "u0126"
PLAN_REPAIRS = [{"unit": u, "plan": "attitudes", "item": "AT-0p",
                 "state": ("already in the plan's form at the start of this run (applied in 20261014T1800Z, audited 20261014T1800Z: u0165.s01, s02, s04 to s07 FAITHFUL); "
                           "the shape is asserted by repair_20261015T0600Z.py and measured again by the probes; not re-applied" if u != S03 else
                           "already in the plan's form at the start of this run; this run additionally gives each candidate of the reading set its own pair of attitude "
                           "terms (audit repair, below); the guard shape per candidate is the plan's")} for u in HC_UNITS]
AUDIT_REPAIRS = [{"unit": S03, "audit": "20261014T1800Z", "what": "each candidate (wide, narrow) has its own pair of attitude terms, with its own wording and record; the pair both "
                                                               "candidates shared is removed with every trace"},
                 {"unit": U0052, "audit": "20261014T1800Z", "what": "the open-term record of good_judgment names the declared sorts claude_instance and situation "
                                                                    "(it named the undeclared `action` and `context`)"},
                 {"unit": U0126, "audit": "20261014T1800Z", "what": "the ledger entry no longer lists the open term ethical_harm, which an earlier run removed from the document"}]
CHANGED = [S03, U0052, U0126, U0173]

# the audit of run 20261014T1800Z (19/20 sampled faithful + 8/9 changed faithful; 25 units), verdicts as received (AUDIT-20261014T1800Z-received.md)
AUDIT_1014_FAITHFUL = ["u0001", "u0008.heading", "u0032.heading", "u0040.heading", "u0052.s01", "u0055.heading", "u0062.s01", "u0123.s01.p1", "u0123.s02.p1",
                       "u0126", "u0130.heading", "u0165.s01", "u0165.s02", "u0165.s04", "u0165.s05", "u0165.s06", "u0165.s07", "u0173.s01", "u0174.heading",
                       "u0212.heading", "u0235.heading", "u0248", "u0260.heading", "u0263.s04.p2"]
AUDIT_1014_UNFAITHFUL = [S03]

import os  # noqa: E402
HARD_PROBE = Path(os.environ.get("VE_PILOT_HARD_PROBE", RUN / "probes/hard-conclusions-probe.json"))  # a debugging override only
KNOW = "knowingly_engages_"
THINK = "thinks_quite_likely_"
OLD_S03_TERMS = (sc.OLD_KNOWING, sc.OLD_THINKING)
# a name of the removed shared terms, not followed by the candidate suffix (the new terms start with the same letters)
STALE_S03 = re.compile(r"(knowingly_engages_3|thinks_quite_likely_3)(?!_(wide|narrow))")

S03_NOTE_ATTITUDES = (
    " Attitude terms per candidate (audit 20261014T1800Z, repaired in run 20261015T0600Z): the two candidates differ in the attitude terms too, not only in the case "
    "atoms. The wide candidate uses " + sc.KNOWING["wide"] + " and " + sc.THINKING["wide"] + ", whose category is “creating something that is a cyberweapon or "
    "malicious code and that could cause significant damage if deployed”; the narrow candidate uses " + sc.KNOWING["narrow"] + " and " + sc.THINKING["narrow"] +
    ", whose category is “creating a cyberweapon or creating malicious code that could cause significant damage if deployed”. So the narrow candidate states that "
    "thinking it quite likely that one is creating any cyberweapon triggers the prohibition, which the wide candidate does not; each record describes its own category.")
HC_REPAIR_ATTITUDES = (
    "Audit 20261014T1800Z (u0165.s03 UNFAITHFUL: the reading set split the case atoms into wide and narrow but not the attitude terms, so the belief term was the "
    "same alternative in both candidates and its record, like that of the knowing term, still described the category with the unsplit phrase). Repaired in run "
    "20261015T0600Z: each candidate has its own pair of binary open terms on (claude_instance, situation), " + sc.KNOWING["wide"] + " and " + sc.THINKING["wide"] +
    " for wide, " + sc.KNOWING["narrow"] + " and " + sc.THINKING["narrow"] + " for narrow; the shared terms are removed with every trace (vocabulary, open terms, "
    "stored relations, notes, ledger, probes). The guard of each candidate is ( category(s) and knowing(c, s) ) or thinks(c, s), c = var 1, s = var 0. Not audited.")
U0052_REPAIR_ADD = (
    "Audit 20261014T1800Z (small fault, no verdict change): the open-term record of good_judgment gave the argument sorts `action` and `context`, which the document "
    "does not declare. Repaired in run 20261015T0600Z: it is a pair of an instance of Claude and a situation (both declared); the question stays what counts as good "
    "judgment. The rule and its guard are unchanged. Not re-audited.")
U0126_REPAIR_ADD = (
    "Audit 20261014T1800Z (small fault, no verdict change): the ledger entry listed the open term ethical_harm, which repair.py removed from the document in run "
    "20261008T0600Z. Repaired in run 20261015T0600Z: the entry lists no open term. The heading's presupposition is not formalised (the document keeps the heading label). Not re-audited.")
U0173_NOTE = ("Not claimed. Its words are used by the guards of the seven hard-constraint rules (u0165.s01 to u0165.s07): for each category its first "
              "alternative is the open term " + KNOW + "N and its second the open term " + THINK + "N, each a pair of the acting instance of Claude and a situation "
              "(for u0165.s03 one such pair per candidate of its reading set: " + ", ".join(sc.ATTITUDES) + "); the unit itself stays UNFORMALISED because knowing, "
              "intending and thinking something quite likely are not typed (modality/belief) and “quite likely” is a quantity.")


def category_of(unit):
    words = PER_UNIT[unit][1]
    return words[len("Claude "):]


def update_ledger(prev, eng, eng_narrow, silence, probe, scope_probe, binding):
    """The previous run's ledger with this run's repairs. The six other hard constraints keep their entries (their checks are re-read from this run's probe)."""
    ledger = copy.deepcopy(prev)
    pts = {p["label"]: p["status"] for p in probe["points"]}
    sp = {p["label"]: p["status"] for p in scope_probe}
    prev_status = {x["id"]: x["status"] for x in prev}
    for e in ledger:
        i = e["id"]
        e["status_in_previous_run"] = prev_status[i]
        if i in HC_UNITS:
            lab = lambda s: f"{i}: {s}"
            keys = ("the case does not hold, Claude thinks it quite likely that the action falls into the category",
                    "the case holds, Claude knowingly and intentionally engages in it",
                    "neither (an unclear, uncertain or unknowing case)",
                    "the case does not hold, Claude knowingly and intentionally engages in it")
            assert [pts[lab(k)] for k in keys] == [e["check"][k] for k in keys], i   # the four points are as the previous run recorded them
            e["where_the_text_is_silent"] = silence[PER_UNIT[i][2]]
            if i != S03:
                r0 = e["readings"][0]
                r0["english"], r0["english_round_trip"], r0["english_round_trip_error"] = eng[e["rule"]]["text"], eng[e["rule"]]["round_trip"], eng[e["rule"]]["error"]
        if i == S03:
            n = 3
            assert e["status"] == "READINGS" and e["open_terms"] == [*sc.ATOMS, sc.OLD_KNOWING, sc.OLD_THINKING], e["open_terms"]
            e["open_terms"] = [*sc.ATOMS, *sc.ATTITUDES]
            for t in OLD_S03_TERMS:
                assert t in e["case_atoms"]
                del e["case_atoms"][t]
            for r in sc.READINGS:
                cat = sc.CATEGORY_WORDS[r]
                e["case_atoms"][sc.KNOWING[r]] = (f"the instance of Claude knowingly and intentionally engages in the action of the situation as an action of the category "
                                                  f"of the {r} reading: {cat} (u0173.s01, first alternative; a pair of an instance and a situation)")
                e["case_atoms"][sc.THINKING[r]] = (f"the instance of Claude thinks it quite likely that the action of the situation falls into the category of the {r} "
                                                   f"reading: {cat} (u0173.s01, second alternative; that instance's belief, which need not be correct)")
            assert e["note"].count("The open term for the old single category is gone with every trace;") == 1
            e["note"] = e["note"] + S03_NOTE_ATTITUDES
            # the notes of the earlier designs name the shared terms in the words of the history; the history says "the shared terms" instead
            e["note"] = e["note"].replace("the two open terms of the guard", "the open terms of the guard")
            e["audit_repair"] = e["audit_repair"] + " | " + HC_REPAIR_ATTITUDES
            e["repaired_in_run"] = RUN_ID
            e["audit_verified"] = False
            for rid, text, meaning in (("wide", eng["hc-cyberweapons"], "the clause follows both nouns: a cyberweapon too must be one that could cause significant damage if deployed"),
                                       ("narrow", eng_narrow["hc-cyberweapons"], "the clause follows only “malicious code”: every cyberweapon is covered")):
                r = next(x for x in e["readings"] if x["id"] == rid)
                r["english"], r["english_round_trip"], r["english_round_trip_error"], r["meaning"] = text["text"], text["round_trip"], text["error"], meaning
                r["attitude_terms"] = [sc.KNOWING[rid], sc.THINKING[rid]]
            e["scope_probe"] = {"meaning": "u0165.s03 probe points, on the wide companion (readings/all-strict.ve.md) and the narrow companion (readings/all-strict-narrow.ve.md); "
                                           "each companion's rule uses only its own candidate's attitude terms, so the other candidate's terms must leave it UNDECIDED",
                                "points": sp}
            e["check"]["note"] = ("asked on the wide companion with the case = a cyberweapon that could cause significant damage (a case under both readings) and the wide "
                                  "candidate's attitude terms; the two readings differ at: a cyberweapon that could not cause significant damage, knowingly created (wide " +
                                  sp["u0165.s03, wide reading: a cyberweapon that could not cause significant damage, knowingly created"] + ", narrow " +
                                  sp["u0165.s03, narrow reading: a cyberweapon that could not cause significant damage, knowingly created"] + "); the other candidate's attitude "
                                  "terms alone settle nothing (UNDECIDED on both companions)")
        elif i == U0052:
            e["audit_repair"] = e["audit_repair"] + " | " + U0052_REPAIR_ADD
            e["repaired_in_run"] = RUN_ID
            e["audit_verified"] = False
        elif i == U0126:
            assert e["open_terms"] == ["ethical_harm"], e["open_terms"]
            e["open_terms"] = []
            e["audit_repair"] = U0126_REPAIR_ADD
            e["repaired_in_run"] = RUN_ID
            e["audit_verified"] = False
        elif i == U0173:
            e["note"] = U0173_NOTE
    # no trace of the removed shared terms may remain anywhere in the ledger (the new per-candidate terms start with the same letters, hence the pattern)
    for e in ledger:
        for k, v in e.items():
            dumped = json.dumps(v, ensure_ascii=False)
            for w in ("thought_likely", "knowingly_<", "damaging_cyberweapon_or_malicious_code", "restricted_action_knowing_or_quite_likely"):
                assert w not in dumped, (e["id"], k, w)
            assert not STALE_S03.search(dumped), (e["id"], k, STALE_S03.search(dumped).group(0))
    return ledger


annotate = p14.annotate


def main():
    prev = json.load(open(PREV_DIR / "units.json"))
    prev_metrics = json.load(open(PREV_DIR / "metrics.json"))
    assert hashlib.sha256(SOURCE).hexdigest() == prev_metrics["source_sha256"]
    eng = old.english_nd(STRICT)
    eng_narrow = old.english_nd(STRICT_NARROW)
    silence, legend = old.silence_sentences(STRICT)
    probe = json.load(open(RUN / "probes/unspecified-probe.json"))
    ledger = update_ledger(prev, eng, eng_narrow, silence, probe, probe["scope_points"], probe["binding_points"])
    main_meta = front_matter(MAIN)
    ids = [e["id"] for e in ledger]

    # ---- DRI X5: a covered unit is claimed unless its entry says `claimed: false` (an OPEN unit with part of its meaning missing); none is marked here
    for e in ledger:
        if e["status"] in COVERED:
            e["claimed"] = True
    claimed_false = [e["id"] for e in ledger if e.get("claimed") is False]

    # ---- SC-M0: the scope tally (no status or content changes)
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
    tally["note"] = ("scope-tally for run 20261015T0600Z; the tags are ledger annotations only: other_blockers gains `other:scope`, governed units record governed_by "
                     "(a frontier governor's candidates record governed_by_candidate, never governed_by), and no unit's status or content changes")
    dump("scope-tally.json", tally)

    # ---- AP-0 item 3: act_workaround tags, copied from the act-phrases evidence for every unit whose act phrase is unchanged since run 20261012T1800Z
    m4_src = json.load(open(RUN / "evidence/m4-act-workaround.json"))
    vocab_now = main_meta["environment"]["vocabulary"]["predicates"]
    prev_vocab = front_matter(PREV_DIR / "translation.ve.md")["environment"]["vocabulary"]["predicates"]
    entries = {e["id"]: e for e in ledger}
    stale = []
    for r in m4_src["units"]:
        e = entries[r["unit"]]
        act_now = vocab_now[e["predicate"]]["regulated"]["act"]
        assert act_now == r["act"] == prev_vocab[e["predicate"]]["regulated"]["act"], (r["unit"], act_now, r["act"])   # no act phrase changed since 20261012T1800Z
        e["act_workaround"] = r["act_workaround"]
    m4_units = [e["id"] for e in ledger if e.get("act_workaround") not in (None, "none")]
    m4 = {"units": len(m4_units), "bytes": sum(e["span"][1] - e["span"][0] for e in ledger if e["id"] in m4_units), "unit_ids": m4_units,
          "tally": dict(Counter(e["act_workaround"] for e in ledger if "act_workaround" in e)),
          "stale": stale, "expected": {"units": 17, "bytes": 2502}, "source": "research/act-phrases-p1: docs/research/evidence/act-phrases/m4-act-workaround.json (evidence/m4-act-workaround.json)"}
    assert (m4["units"], m4["bytes"]) == (17, 2502), m4

    dump("units.json", ledger)
    by_id = {e["id"]: e for e in ledger}
    assert [(u["id"], tuple(u["span"])) for u in main_meta["units"]] == [(e["id"], tuple(e["span"])) for e in ledger]
    assert [(e["id"], tuple(e["span"])) for e in prev] == [(e["id"], tuple(e["span"])) for e in ledger]

    # ---- VE runs at this tag
    rel = str(MAIN.relative_to(ROOT))
    t0 = time.monotonic()
    check = json.loads(ve("document", "check", rel))
    t1 = time.monotonic()
    coverage = json.loads(ve("document", "coverage", rel))
    t2 = time.monotonic()
    timing = {"document_check": round(t1 - t0, 1), "document_coverage": round(t2 - t1, 1)}
    render = ve("document", "render", rel)
    strict = {"check": json.loads(ve("document", "check", str(STRICT.relative_to(ROOT)))),
              "coverage": json.loads(ve("document", "coverage", str(STRICT.relative_to(ROOT))))}
    dump("check.json", check)
    dump("coverage.json", coverage)
    dump("environment.json", main_meta["environment"])
    dump("readings/check-all-strict.json", strict["check"])
    (RUN / "readings/rendered-all-strict.md").write_text(ve("document", "render", str(STRICT.relative_to(ROOT))))
    (RUN / "rendered.md").write_text(annotate(render, ledger))
    (RUN / "rendered-raw.md").write_text(render)
    assert check["premises"]["status"] == "model", check["premises"]
    assert check["reading_plan"]["route"] == "enumerate" and len(check["reading_plan"]["choices"]) == 16
    assert check["readings"]["conflict"]["status"] == "CONFLICT-FREE"
    assert coverage["coverage_percent"] == 100 and coverage["source_bytes"] == len(SOURCE)
    prev_check = json.load(open(PREV_DIR / "check.json"))
    prev_cov = json.load(open(PREV_DIR / "coverage.json"))

    # ---- ledger and counts
    total = sum(e["span"][1] - e["span"][0] for e in ledger)
    assert total == len(SOURCE)
    pos = 0
    for e in ledger:
        assert e["span"][0] == pos, e["id"]
        pos = e["span"][1]
    u, nb = old.counts(ledger)
    claimed = sum(e["span"][1] - e["span"][0] for e in ledger if e["status"] in COVERED and e.get("claimed", True) is not False)
    assert claimed == sum(v for k, v in nb.items() if k in COVERED) and claimed == prev_metrics["claimed_covered_bytes"], claimed
    n_old, old_units, _ = old.aggregate(ledger)
    spans = {e["id"]: e["span"] for e in ledger}
    status = {e["id"]: e["status"] for e in ledger}
    width = lambda ids: sum(spans[i][1] - spans[i][0] for i in ids)
    # VE's own coverage: CHECKED + OPEN(+READINGS) bytes
    assert coverage["bytes_by_status"]["CHECKED"] == nb["CHECKED"] and coverage["bytes_by_status"]["OPEN"] == nb["OPEN"] + nb["READINGS"]

    # ---- audit-verified bytes: accepted by an audit of this lineage AND byte-identical here to the form that audit saw (a changed unit is dropped until re-audited)
    prev_verified = list(prev_metrics["audit_verified_covered_units"])
    dropped = [i for i in prev_verified if i in CHANGED or i in AUDIT_1014_UNFAITHFUL]
    kept = [i for i in prev_verified if i not in CHANGED and i not in AUDIT_1014_UNFAITHFUL]
    newly = [i for i in AUDIT_1014_FAITHFUL if status[i] in COVERED and status[i] != "LABELLED" and i not in CHANGED and i not in kept]
    assert not any(by_id[i].get("claimed") is False for i in [*kept, *newly])
    verified = kept + newly
    verified_bytes = width(verified)
    cand_lab = list(dict.fromkeys(old.AUDIT_PASSED_LABELLED + old.AUDIT_PASSED_1004_LABELLED + old.AUDIT_PASSED_1004B_LABELLED + ["u0212.heading"]
                                  + prevf.AUDIT_FAITHFUL_1800 + prevf.AUDIT_FAITHFUL_1811 + p18.AUDIT_0600_FAITHFUL + p13.AUDIT_1800_FAITHFUL + p14.AUDIT_1013_FAITHFUL
                                  + AUDIT_1014_FAITHFUL))
    verified_lab = [i for i in cand_lab if i in by_id and status[i] == "LABELLED" and i not in CHANGED]
    verified_meta = width(verified_lab)
    label_bytes_dropped = nb["LABELLED"] - verified_meta
    assert verified_meta == prev_metrics["audit_verified_metadata_bytes"] - width([i for i in CHANGED if status[i] == "LABELLED"]), (verified_meta, nb["LABELLED"])
    repaired_bytes = width([i for i in CHANGED if status[i] in COVERED])

    # ---- reading sets, conclusion queries, probes
    nd = {"all": prevf.slice_result("all")}
    assert nd["all"]["conflict"] == "CONFLICT-FREE" and nd["all"]["premises"] == "model" and nd["all"]["choice_count"] == 16
    sep_all = sum(nd["all"]["separations"].values())
    cand_status = Counter(nd["all"]["premises_by_candidate"].values())
    concl = prevf.concl((("denial_one_reading", "conclusion-no-denial-result.json"), ("claim_human", "claim-human-result.json")))
    assert concl["denial_one_reading"]["verdict"] == "ALL" and concl["claim_human"]["verdict"] == "ALL"
    prev_cc = prev_metrics["checked_content_main_chain"]
    prev_concl = prev_cc["conclusion_probes"]["results"]
    hard_q = json.load(open(HARD_PROBE))["queries"]
    hard_by = {(q["unit"], q["kind"]): q for q in hard_q}
    assert len(hard_q) == 21
    assert all(hard_by[(u_, "neither")]["verdict"] == "UNKNOWN" for u_ in HC_UNITS), "the 'neither' queries are meant not to be entailed"
    assert all(hard_by[(u_, k)]["verdict"] == "ALL" and hard_by[(u_, k)]["evidence"] in ("certificate", "certificates") for u_ in HC_UNITS[1:] for k in ("knowing", "belief"))
    assert all(hard_by[("u0165.s01", k)]["verdict"] == "UNKNOWN" for k in ("knowing", "belief"))
    hard_summary = {k: dict(Counter(q["verdict"] for q in hard_q if q["kind"] == k)) for k in ("knowing", "belief", "neither")}
    points = probe["points"]
    probe_names = ("risk-probe", "s1-probe", "senses-probe", "senses-document-probe", "discourse-probe", "rights-reading-probe")
    probe_same = {n: (RUN / f"probes/{n}.json").read_bytes() == (PREV_DIR / f"probes/{n}.json").read_bytes() for n in probe_names}
    assert all(probe_same.values()), probe_same
    s1_probe = json.load(open(RUN / "probes/s1-probe.json"))
    rights = json.load(open(RUN / "probes/rights-reading-probe.json"))
    profile_probe = old.probe_profiles()
    comp = json.load(open(RUN / "probes/companion-probe.json"))
    comp_ok, comp_bad = comp["attempts"]["without_source_word"], comp["attempts"]["with_source_word"]
    assert comp_ok["check"]["returncode"] == 0 and comp_bad["check"]["returncode"] == 5
    comp_share = comp_ok["lean_decided_share"]
    comp_q = {}
    for name in ("no-denial", "claim-human"):
        d = json.load(open(RUN / f"probes/companion/query-{name}.json"))
        comp_q[name] = {"verdict": d["verdict"], "route": d["route"], "component": d["component"], "sentence": d.get("sentence"),
                        "decided_units": len(d["decided_units"]), "english": d["english"]}
    asks = [json.load(open(RUN / f"probes/ask/q{i}.json")) for i in range(1, 6)]
    ask_questions = [(RUN / f"probes/ask/q{i}.question.txt").read_text().strip() for i in range(1, 6)]
    ask_read = sum(1 for a in asks if a["result"].get("status") != "none")

    open_terms = [{k: t[k] for k in ("name", "arguments", "decided_by", "necessary", "sufficient", "factors")} for t in main_meta["open_terms"]]
    names = {t["name"] for t in open_terms}
    prev_names = {t["name"] for t in prev_metrics["open_terms"]}
    cv_main = {"document_loaded": True, "coverage_percent": coverage["coverage_percent"],
               "premises": {k: check["premises"][k] for k in ("status", "route", "evidence")}, "premises_gaps": check["premises"].get("gaps"),
               "reading_plan": {"route": check["reading_plan"]["route"], "choice_count": len(check["reading_plan"]["choices"]),
                                "conditional_on": check["reading_plan"].get("conditional_on")},
               "conflict": {"route": check["readings"]["route"], "status": check["readings"]["conflict"]["status"],
                            "evidence": check["readings"]["conflict"].get("evidence"), "status_text": check["readings"]["status"],
                            "choices": dict(Counter(c["status"] for c in check["readings"]["conflict"]["choices"])),
                            "sizes": check["readings"].get("sizes"), "english": check["readings"]["english"]},
               "previous_run": {"premises_route": prev_check["premises"]["route"], "conflict_route": prev_check["readings"]["route"],
                                "conflict_status_text": prev_check["readings"]["status"], "choices": len(prev_check["reading_plan"]["choices"]),
                                "open_sentences": 3},
               "residual": coverage["residual"], "residual_previous_run": prev_cov["residual"], "norm_defaults": check["norm_defaults"],
               "check_seconds_this_run": timing}
    cv_strict = {"document": "readings/all-strict.ve.md", "premises": strict["check"]["premises"], "residual": strict["coverage"]["residual"],
                 "bytes_by_status": strict["coverage"]["bytes_by_status"]}
    HC_NAMES = {unit: rule for unit, rule, _p, _t, _a, _w in spec_nd.HARD}
    assert all(q.get("verdict") for q in hard_q), [(q["unit"], q["kind"]) for q in hard_q if not q.get("verdict")]
    n_all = sum(1 for q in hard_q if q["verdict"] == "ALL")
    unknown = [f"{q['unit']}:{q['kind']}" for q in hard_q if q["verdict"] == "UNKNOWN"]
    reask = [f"{q['unit']}:{q['kind']}" for q in hard_q if q.get("asked_on_final_document")]
    reran = [f"{q['unit']}:{q['kind']}" for q in hard_q if "rerun_alone" in q and not q.get("asked_on_final_document")]
    capped = [f"{q['unit']}:{q['kind']}" for q in hard_q if q.get("cap")]
    first_unavailable = sorted(f"{q['unit']}:{q['kind']}" for q in hard_q if "rerun_alone" in q)
    hard_reading = (f"{n_all} of {len(hard_q)} queries are ALL with a certificate on the superposed route; the rest ({', '.join(unknown)}) are UNKNOWN: VE's search budget is "
                    "exhausted without a counterexample or a proof. 'neither' is UNKNOWN for every unit, which is the intended answer: the translation does not forbid an unclear, "
                    "uncertain or unknowing case. For u0165.s01 all three are UNKNOWN (several minutes each; the same shape of query on the earlier translations was also UNKNOWN), a limit "
                    "of the proof search; for s01 the checked answer is the settled-point answer of the unspecified probe. For u0165.s03 the knowing and belief premises name the attitude "
                    "terms of both candidates, so that each candidate's rule fires; the answers are ALL with a certificate for each candidate. "
                    f"{len(first_unavailable)} queries first failed with CheckerUnavailable (the Rust checker's default 5-second limit, three queries in parallel on a machine with load "
                    f"above 60) and were re-run one at a time at the default limit; CheckerUnavailable is not a verdict and was not used. {len(capped)} of them were unavailable again at "
                    "the default limit and were re-run under `prlimit --as=6442450944` (6 GB address space) with VE_RUST_TIMEOUT=600 (DRI 2026-10-14 15:30Z, 3): " +
                    (", ".join(capped) if capped else "none") + "; the cap and the peak resident set are in `reruns`. Every query was asked on the final document (nothing was edited after the "
                    "queries ran).")
    prev_meta = front_matter(PREV_DIR / "translation.ve.md")
    flat = lambda meta: {x["id"]: x for u_ in meta["units"] for x in (u_["parts"] if u_.get("status") == "MIXED" else [u_])}
    nu, ou = flat(main_meta), flat(prev_meta)
    pv_new, pv_old = main_meta["environment"]["vocabulary"]["predicates"], prev_meta["environment"]["vocabulary"]["predicates"]
    body = lambda p_: p_.read_bytes().split(b"\n---\n", 2)[-1]
    vocab_check = {
        "rule": "DRI 2026-10-14 15:30Z (2): after a vocabulary change rerun the situation step (nd.py all) and check every existing fenced unit still parses unchanged",
        "situation_step_rerun": "nd.py all ran after the last vocabulary change (readings/nd-all-result.json: admitted, 16 choices)",
        "fenced_blocks": {"now": MAIN.read_bytes().count(b"```ve "), "previous_run": (PREV_DIR / "translation.ve.md").read_bytes().count(b"```ve ")},
        "fenced_unit": "u0248 “Claude is not a human.” (the translation's only fenced block): the document is admitted and the unit's content and graph node are unchanged",
        "body_text_identical": body(MAIN) == body(PREV_DIR / "translation.ve.md"),
        "graph_identical": main_meta["graph"] == prev_meta["graph"],
        "units_compared": len(nu), "units_changed": sorted(i for i in nu if nu[i] != ou[i]),
        "constants_identical": main_meta["environment"]["vocabulary"]["constants"] == prev_meta["environment"]["vocabulary"]["constants"],
        "predicates_added": sorted(set(pv_new) - set(pv_old)), "predicates_removed": sorted(set(pv_old) - set(pv_new)),
        "predicates_changed": sorted(k for k in pv_new if k in pv_old and pv_new[k] != pv_old[k]),
        "sort_entity": ("DRI 2026-10-14 15:30Z (1): the carried sort `entity` now has the noun “thing” (plural “things”) instead of the reserved word “entity” (it was “entity”, "
                        "“entities”). Only the noun changed (the sort's id, constants and formulas are as before); the noun appears only in VE's own model descriptions "
                        "(“e is a thing of sort ...”), in no unit's text. nd.py all was rerun after the change; the probes were run on the final document"),
        "sorts_changed": sorted(k for k in main_meta["environment"]["vocabulary"]["sorts"]
                                if main_meta["environment"]["vocabulary"]["sorts"][k] != prev_meta["environment"]["vocabulary"]["sorts"].get(k)),
    }
    assert vocab_check["body_text_identical"] and vocab_check["graph_identical"] and vocab_check["constants_identical"]
    assert vocab_check["sorts_changed"] == ["entity"], vocab_check["sorts_changed"]
    _s_new = copy.deepcopy(main_meta["environment"]["vocabulary"]["sorts"]); _s_old = copy.deepcopy(prev_meta["environment"]["vocabulary"]["sorts"])
    assert _s_new["entity"]["verbalisation"] == {"singular": "thing", "plural": "things"}
    _s_new["entity"]["verbalisation"] = _s_old["entity"]["verbalisation"]
    assert _s_new == _s_old, "only the noun of `entity` changed"
    assert set(vocab_check["units_changed"]) == {S03}, vocab_check["units_changed"]
    hard_changed = {i: "plan repair AT-0p (attitudes plan, DRI AT2): carried unchanged from run 20261014T1800Z, shape verified: guard = ( C(s) and " + KNOW + "N(c, s) ) or " + THINK +
                       "N(c, s), two binary open terms on (claude_instance, situation); not a changed unit in this run" for i in HC_UNITS if i != S03}
    changed_detail = {
        S03: ("audit repair (audit 20261014T1800Z, UNFAITHFUL): each candidate of the reading set has its own pair of binary attitude terms on (claude_instance, situation): " +
              ", ".join(sc.ATTITUDES) + "; the pair both candidates shared in the previous run is removed with every trace. The guards keep the AT-0p shape per candidate."),
        U0052: "audit repair (small fault): the open-term record of good_judgment names the declared sorts claude_instance and situation (it named `action` and `context`); the rule is unchanged",
        U0126: "audit repair (small fault): the ledger entry lists no open term (it listed the removed ethical_harm); the heading label is unchanged",
        U0173: "note only: UNFORMALISED, not claimed; says which open terms carry its two alternatives (for u0165.s03 one pair per candidate)"}
    new_terms = sorted(names - prev_names)
    removed_terms = sorted(prev_names - names)
    expected_added = set(sc.ATTITUDES)
    assert set(new_terms) == expected_added, set(new_terms) ^ expected_added
    assert set(removed_terms) == set(OLD_S03_TERMS), removed_terms
    prev_open = {t["name"]: t for t in prev_metrics["open_terms"]}
    changed_args = {t["name"]: {"arguments": [prev_open[t["name"]]["arguments"], t["arguments"]]} for t in open_terms
                    if t["name"] in prev_open and prev_open[t["name"]]["arguments"] != t["arguments"]}
    changed_factors = {t["name"]: {"factors": [prev_open[t["name"]]["factors"], t["factors"]]} for t in open_terms
                       if t["name"] in prev_open and prev_open[t["name"]]["factors"] != t["factors"]}
    assert set(changed_args) == {"good_judgment"} and set(changed_factors) == set(), (changed_args, changed_factors)
    plan_repairs_changed = sorted({r["unit"] for r in PLAN_REPAIRS})
    m = {
        "run": RUN_ID, "baseline_tag": TAG, "previous_run": PREV_RUN, "previous_baseline_tag": PREV_TAG,
        "source_sha256": prev_metrics["source_sha256"], "source_bytes": len(SOURCE), "bytes_accounted": total, "bytes_accounted_percent": 100.0,
        "history_note": "this file records this run; the earlier runs' records (audit-verification history, the earlier probes' narrative) are in prev/metrics.json",
        "changed_units": sorted(CHANGED),
        "plan_repairs": PLAN_REPAIRS,
        "audit_repairs": AUDIT_REPAIRS,
        "changed_units_detail": changed_detail,
        "plan_repair_AT0p_state": hard_changed,
        "plan_repair_note": ("AT-0p (DRI AT2) was applied in run 20261014T1800Z and is in the plan's form at the start of this run; this run asserts the shape (repair_20261015T0600Z.py), "
                             "measures the four probe kinds again (all as the plan states) and does not re-apply it, so the seven units are listed in plan_repairs with their state "
                             "but only u0165.s03 (an audit repair) is a changed unit. Expected by the plan and measured: claimed bytes unchanged at 2,951; open terms 46 at the AT-0p "
                             "stage of the previous run (now " + str(len(open_terms)) + " with the scope set and the per-candidate attitude terms); case false and thinks-quite-likely "
                             "true SETTLED no; case true and knowingly true SETTLED no; neither UNDECIDED; case false and knowingly true UNDECIDED, for all seven rules"),
        "feature_upgrades": {"units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
                             "note": "kept apart from the plan repairs and audit repairs, so that differences against the previous run measure the language, not the translator"},
        "tags_only_not_changed_units": ("scope tags (SC-M0), act_workaround (AP-0 item 3) and the `claimed` field are ledger annotations: " + str(tally["totals"]["units_tagged"]) +
                                        " units carry other:scope; none of them is a changed unit by this alone"),
        "sentence_clause_units": {"units_total": len(ledger), "unit_counts_by_status": old.full(u), "bytes_by_status": old.full(nb),
                                  "previous_run": {k: prev_metrics["sentence_clause_units"][k] for k in ("units_total", "unit_counts_by_status", "bytes_by_status")}},
        "aggregated_to_previous_boundaries": {"units_total": n_old, "unit_counts_by_status": old_units, "bytes_by_substatus": old.full(nb),
                                              "previous_run": {k: prev_metrics["aggregated_to_previous_boundaries"][k] for k in ("units_total", "unit_counts_by_status")}},
        "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(SOURCE), 4),
        "claimed_covered_bytes_previous_run": prev_metrics["claimed_covered_bytes"], "claimed_covered_bytes_gained": claimed - prev_metrics["claimed_covered_bytes"],
        "claimed_false_units": claimed_false,
        "claimed_rule": "DRI X5: a unit whose ledger entry says `claimed: false` (an OPEN unit with part of its meaning missing) is never counted as claimed or audit-verified bytes; "
                        "every covered unit here is `claimed: true`, none is marked false (u0165.s03's missing scope alternative is now represented by the reading set)",
        "substantive_covered_bytes": nb["CHECKED"] + nb["OPEN"] + nb["READINGS"], "substantive_covered_bytes_previous_run": prev_metrics["substantive_covered_bytes"],
        "audit_verified_covered_bytes": verified_bytes, "audit_verified_covered_percent": round(100 * verified_bytes / len(SOURCE), 4),
        "audit_verified_covered_units": verified, "audit_verified_covered_bytes_previous_run": prev_metrics["audit_verified_covered_bytes"],
        "audit_verified_dropped_because_changed": dropped,
        "audit_verified_newly_from_20261014T1800Z": newly,
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND byte-identical in this run to the form that audit saw. The audit of run "
            "20261014T1800Z (19/20 sampled faithful, 8/9 changed faithful, 25 units; unfaithful: u0165.s03; AUDIT-20261014T1800Z-received.md) is the latest. It accepted "
            "u0052.s01, u0062.s01, u0123.s02.p1, u0165.s01, s02 and s04 to s07 and u0248 (covered) and u0173.s01 (only as correctly UNFORMALISED); this run "
            "leaves them byte-identical except u0052.s01 (the open-term record of good_judgment, a small fault the audit named), which is dropped until re-audited, as are "
            "u0126 (its ledger entry) and u0165.s03 (rejected). u0173.s01 gets a note only (it is not covered). u0123.s02.p1 and the six hard constraints accepted for the first "
            "time become audit-verified."),
        "audit_verified_metadata_bytes": verified_meta, "audit_verified_metadata_percent": round(100 * verified_meta / len(SOURCE), 4),
        "audit_verified_metadata_bytes_previous_run": prev_metrics["audit_verified_metadata_bytes"],
        "claimed_but_not_audit_verified_bytes": claimed - verified_bytes - verified_meta,
        "repaired_bytes_not_audit_verified": repaired_bytes,
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20261014T1800Z_audit": AUDIT_1014_UNFAITHFUL,
            "repair_done_in_20261015T0600Z": ("u0165.s03: each candidate has its own pair of attitude terms (knowingly_engages_3_wide, thinks_quite_likely_3_wide, "
                                              "knowingly_engages_3_narrow, thinks_quite_likely_3_narrow), with wording and records stating that candidate's category; see AUDIT-REPAIR.md. "
                                              "It keeps its covered status (READINGS) only because it is repaired; it is claimed but not audit-verified"),
            "small_faults_repaired": {U0052: "open-term record of good_judgment: declared sorts", U0126: "ledger entry no longer lists the removed open term ethical_harm"},
            "kept_covered_status_without_repair": [],
            "earlier_audits": "the rejections and repairs of the earlier runs are recorded in prev/metrics.json and the AUDIT-*-received.md files"},
        "document_profiles": {"main": main_meta["environment"]["profiles"], "strict": front_matter(STRICT)["environment"]["profiles"]},
        "documents": {"translation": "translation.ve.md (four reading sets carry content: three 'should' sets and the scope set of u0165.s03, whose candidates have their own attitude terms; built by nd.py all from translation-without-content.ve.md, cmp-identical)",
                      "without_content": "translation-without-content.ve.md", "strict": "readings/all-strict.ve.md (the source of the strict content of the three sets, and of the wide candidate of the scope set)",
                      "strict_narrow": "readings/all-strict-narrow.ve.md (the strict companion with the narrow candidate of u0165.s03; used by the probes)",
                      "not_carried": "readings/all-default.ve.md, readings/s1.ve.md (soft-chain demonstrations of earlier runs; copied in for probes s1 and rights, then removed)"},
        "open_terms": open_terms, "open_terms_count": len(open_terms), "open_terms_count_previous_run": prev_metrics["open_terms_count"],
        "open_terms_added": new_terms, "open_terms_removed_this_run": removed_terms, "open_terms_with_changed_factors": [],
        "open_terms_with_changed_arguments": changed_args,
        "open_terms_count_note": "the previous run had 48 (AT-0p gave 46; the scope set of u0165.s03 replaced one case atom by three); this run replaces the two shared attitude terms of u0165.s03 by four (one pair per candidate), so 50",
        "ledger_only_open_terms": {
            "what": "names that UNFORMALISED entries list as vague terms the unit would depend on, which are not open terms of the document (an earlier run removed their records "
                    "because no covered unit used them); a ledger pointer, never counted as an open term and never claimed",
            "names": sorted({t for e in ledger for t in (e.get("open_terms") or []) if t not in names}),
            "entries": sum(1 for e in ledger if any(t not in names for t in (e.get("open_terms") or []))),
            "statuses": dict(Counter(e["status"] for e in ledger if any(t not in names for t in (e.get("open_terms") or [])))),
            "covered_entries_with_such_names": [e["id"] for e in ledger if e["status"] in COVERED and any(t not in names for t in (e.get("open_terms") or []))]},
        "reading_sets": {"count": 4, "unresolved": 4, "count_previous_run": 4, "units": [*SETS_KEPT, S03],
                         "candidates": {**{i: ["strict", "default"] for i in SETS_KEPT}, S03: ["wide", "narrow"]},
                         "couplings": [], "narrowings": [],
                         "choices": nd["all"]["choice_count"], "choices_previous_run": 16, "removed_this_run": {},
                         "added_this_run": {}, "changed_this_run": {S03: "the two candidates (wide, narrow) have their own attitude terms; both attachments are admitted by the English words alone (audit 20261014T1800Z)"},
                         "readings_from_the_words": {
                             "force_sets_kept_because_of_the_word_should": {"units": ["u0036.s05", "u0263.s04.p2"], "spans": ["u0253.s04", "u0011.s01"]},
                             "force_set_kept_because_the_text_implies_exceptions": {"units": ["u0156.s03"], "spans": ["u0109.s06", "u0109.s05"],
                                                                                    "note": "accepted by the 20261012T0600Z, 20261012T1800Z and 20261013T0600Z audits (sampled)"},
                             "scope_set": {"units": [S03], "words": "“Create cyberweapons or malicious code that could cause significant damage if deployed”: the relative clause follows both nouns or only the last; nothing outside the sentence is used"},
                             "removed": {"u0052.s01": "“should always”: the word “always” excludes exceptions in the sentence itself and no span of the text implies one",
                                         U0125: "“should never directly deny that it is Claude”: the spans cited for a defeasible reading are about honesty in general and u0170.s01 says the hard-constraint list does not exhaust what Claude should never do; the audit found no exception stated or implied"},
                             "removed_by_audit_20261008T1800Z": {"u0062.s01": ["ability"], "u0123.s01.p1": ["permission-no-limits"], "u0123.s02.p1": ["conditional-permission", "ability"],
                                                                 "u0123.s03": ["narrow-ability", "wide-ability"]}}},
        "missing_feature_tally": old.tally(ledger), "missing_feature_tally_previous_run": prev_metrics["missing_feature_tally"],
        "check_verdicts": {"main": cv_main, "all_strict": cv_strict},
        "timing_single_runs": {"note": "one run each on one machine under heavy load (load average above 70 for most of the run), not a controlled comparison (the previous figures come from the previous run's files)",
                               "document_check_seconds": timing["document_check"], "document_check_seconds_previous_run": prev_metrics["timing_single_runs"]["document_check_seconds"],
                               "document_coverage_seconds": timing["document_coverage"], "document_coverage_seconds_previous_run": prev_metrics["timing_single_runs"]["document_coverage_seconds"],
                               "nd_all_load_seconds": [nd["all"]["load_seconds"], prev_metrics["timing_single_runs"]["nd_all_load_seconds"][0]],
                               "nd_all_check_seconds": [nd["all"]["check_seconds"], prev_metrics["timing_single_runs"]["nd_all_check_seconds"][0]],
                               "nd_all_separation_search_seconds": [nd["all"]["separation_search_seconds"], prev_metrics["timing_single_runs"]["nd_all_separation_search_seconds"][0]],
                               "build_note": "this worktree's lean/.lake and rust/target were copied from an identical-commit build (b96f04a5a); `lake build` was a no-op and tools/rust_build.py --check matched the pin; not a language measurement",
                               "order": "[this run, previous run]; both have four sets (16 choices)"},
        "unspecified_probe": {"file": "probes/unspecified-probe.json", "document": "readings/all-strict.ve.md", "points_asked": len(points),
                              "undecided": sum(1 for p in points if p["status"] == "UNDECIDED"),
                              "settled": sum(1 for p in points if p["status"].startswith("SETTLED")),
                              "conflict": sum(1 for p in points if p["status"].startswith("CONFLICT")), "conflict_reports": probe["conflict"],
                              "gaps": {p: g["reached"] for p, g in probe["gaps"].items()},
                              "hard_constraint_points": {p["label"]: p["status"] for p in points if p["label"].startswith("u0165")},
                              "scope_points": {p["label"]: p["status"] for p in probe["scope_points"]},
                              "binding_points": {p["label"]: p["status"] for p in probe["binding_points"]},
                              "reading": "each hard constraint, four points (AT-0p): the case does not hold but this Claude thinks it quite likely that the action falls into the category: "
                                         "SETTLED no (no membership needed); the case holds and this Claude knowingly and intentionally engages in it: SETTLED no; neither: UNDECIDED; "
                                         "the case does not hold but this Claude knowingly engages in it: UNDECIDED (the untyped term cannot refuse that point). The scope points "
                                         "ask u0165.s03 on both companions, each with its own candidate's attitude terms: a cyberweapon that could not cause significant damage, knowingly created, is UNDECIDED under the wide reading and "
                                         "SETTLED no under the narrow one; the other candidate's attitude terms alone leave a companion UNDECIDED; the binding points ask u0123.s02.p1 with two operators. "
                                         "The non-hard-constraint points are the previous run's",
                              "non_hard_constraint_points_same_as_previous_run": {p["label"]: p["status"] for p in points if not p["label"].startswith("u0165")} ==
                              {p["label"]: p["status"] for p in json.load(open(PREV_DIR / "probes/unspecified-probe.json"))["points"] if not p["label"].startswith("u0165")},
                              "conflict_checks_same_as_previous_run": probe["conflict"] == json.load(open(PREV_DIR / "probes/unspecified-probe.json"))["conflict"]},
        "profile_combination_probe": profile_probe, "profile_combination_probe_same_as_previous_run": profile_probe == prev_metrics["profile_combination_probe"],
        "silence_sentences_as_used_in_ledger": {k: v for k, v in silence.items()}, "legend_sentences": legend,
        "senses_probe": {**prev_metrics["senses_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-probe"]},
        "senses_document_probe": {**prev_metrics["senses_document_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-document-probe"]},
        "discourse_probe": {**prev_metrics["discourse_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["discourse-probe"]},
        "rights_reading_probe": {**rights, "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["rights-reading-probe"]},
        "risk_probe": {**prev_metrics["risk_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["risk-probe"]},
        "readings_defaults_probe": {"re_run_at_this_tag": True, "identical_to_previous_run": probe_same["s1-probe"],
                                    "outcome": {"a_main_with_readings@1": "accepted; premises UNKNOWN (no set carries content)",
                                                "b_main_with_one_strict_norm_candidate": "accepted (premises UNKNOWN: the other sets are pending)",
                                                "c_s1_document_with_norm_defaults@0": s1_probe["c_s1_document_with_norm_defaults@0"]["rejection"]}},
        "lean_decided_share": {"decided_bytes": 0, "decided_share_percent": "0.00", "script": "tools/lean_decided_share.py",
                               "meaning": "units whose every verdict is a Lean answer that is not UNKNOWN across readings. For the translation itself (no companion set) it is still 0.00% "
                                          "(`ve document check` reports no `decided_units`, basis 'no Lean answer across readings')",
                               "with_companion_sets": {"document": "probes/companion/translation-companions-without_source_word.ve.md", "decided_units": len(comp_share["decided_units"]),
                                                       "decided_bytes": comp_share["decided_bytes"], "decided_share_percent": comp_share["decided_share_percent"],
                                                       "units": comp_share["decided_units"],
                                                       "caveat": "a probe document, not the translation; each of the four sets is checked by itself as a component, and a rule checked by itself is CONFLICT-FREE by construction"}},
        "companion_probe": {"what": "the four reading sets re-written as companion sets (readings-defaults RD-4b): each candidate carries the main environment (without readings@1) and the open terms its content names",
                            "accepted_with_source_word": False, "refusal_with_source_word": comp_bad["check"]["stdout_error"], "defect_still_present_at_repo_map_untracked": True,
                            "route": comp_ok["summary"]["route"], "components": comp_ok["summary"]["components"], "conflict": comp_ok["summary"]["conflict"],
                            "premises": comp_ok["summary"]["premises"], "premises_components": comp_ok["summary"]["premises_components"],
                            "separations": comp_ok["summary"]["separations"], "decided_units": len(comp_share["decided_units"]), "decided_bytes": comp_share["decided_bytes"],
                            "decided_share_percent": comp_share["decided_share_percent"], "queries": comp_q,
                            "decided_units_same_as_previous_run": comp_share["decided_units"] == prev_metrics["lean_decided_share"]["with_companion_sets"]["units"],
                            "reading": "the companion denial query (--sentence u0125.s04.p2) and the claim-human query (--sentence u0123.s03) answer ALL as before"},
        "checked_content_main_chain": {
            "documents": nd, "candidate_premise_status": dict(cand_status), "choices_checked": nd["all"]["choices_checked"],
            "choices_conflict_free": nd["all"]["conflict_by_choice"].get("CONFLICT-FREE", 0), "choices_conflict": nd["all"]["conflict_by_choice"].get("CONFLICT", 0),
            "separating_situations_checked_by_lean": sep_all, "separated_by_decision_only_findings": 0,
            "all_four_in_one_document": {"admitted": nd["all"]["admitted"], "choices": nd["all"]["choice_count"], "verdict": nd["all"]["conflict_text"],
                                         "separations": nd["all"]["separations"], "route": nd["all"]["route"], "sizes": nd["all"]["sizes"]},
            "conclusion_probes": {"query_denial": "every instance of Claude: not denial_of_being_claude_permitted (probes/nd/conclusion-no-denial.json)",
                                  "query_claim_human": "no operator may give Claude an instruction to claim to be human when asked (probes/nd/conclusion-no-claim-human.json)",
                                  "results": concl, "previous_run_verdicts": {k: v["verdict"] for k, v in prev_concl.items()},
                                  "hard_constraint_queries": {
                                      "file": "probes/hard-conclusions-probe.json (probe_hard_conclusions.py; queries and answers in probes/nd/hard/)",
                                      "what": "for every instance of Claude c and every situation s: (knowing) if the case holds and c knowingly and intentionally engages in it, the act is not permitted; "
                                              "(belief) if c thinks it quite likely that the action falls into the category, not permitted; (neither) if the guard does not hold, not permitted "
                                              "(NOT meant to be entailed: unclear, uncertain or unknowing cases). For u0165.s03 the case is a cyberweapon that could cause significant damage, a case under both candidates",
                                      "verdicts": hard_summary,
                                      "per_unit": {f"{q['unit']}:{q['kind']}": q["verdict"] for q in hard_q},
                                      "document_note": "every query was asked on the final translation.ve.md; nothing was edited after the queries ran",
                                      "reruns": {f"{q['unit']}:{q['kind']}": {k: q[k] for k in ("rerun_alone", "cap", "peak_resident_set_kb") if k in q} for q in hard_q if "rerun_alone" in q},
                                      "reading": hard_reading},
                                  "reading": "the denial and claim-human queries are ALL as before (same verdicts as the previous run); this run's repairs do not move them"},
            "not_representable": [
                "defeasibility beside norm-defaults@0 as VE's own mode: probe c still refuses norm-defaults@0 with soft-norms@0 ('await the Lean route')",
                "decided units for a document without companion sets: `decided_units` is reported only by the companion (product) route; the translation itself stays 0.00%",
                "companion sets together with `source_word`: refused with CheckerUnavailable (a Python defect, still present)",
                "English for a gated UNKNOWN conclusion on the superposed route",
                "typed knowledge, intention and likelihood (u0173.s01): carried only as binary open terms on (instance, situation)",
                "English round trip of a nested guard: the seven hard-constraint rules render in English but do not read back (IdentityMetadataMismatch: block count)",
                "an authored wording that starts with the second argument of a binary term ({1} ...): VE's reader then fails on an unrelated sentence"]},
        "english_round_trip": {"hard_constraint_rules": {HC_NAMES[i]: {"round_trip": eng[HC_NAMES[i]]["round_trip"], "error": eng[HC_NAMES[i]]["error"]} for i in HC_UNITS},
                               "other_rules_round_trip": sorted(k for k, v in eng.items() if v["round_trip"]),
                               "reading": "the nested guard ( C and knowing ) or thinking is rendered as English but VE does not read it back; the flat form of the previous run did. "
                                          "Per the plan the repair is kept because `ve document check` passes. The difference is a finding about the language, not the source."},
        "changes_against_previous_run": {
            "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger), "changed_or_replaced_ids": sorted(CHANGED), "added_ids": [], "units_newly_covered": [],
            "units_with_status_change": {}, "units_changed_by_audit_repair": [S03, U0052, U0126],
            "open_terms_added": new_terms, "open_terms_removed": removed_terms,
            "open_terms_count_before_after": [len(prev_names), len(names)],
            "reading_sets_before_after": [4, 4], "choices_before_after": [16, 16],
            "predicates_added": vocab_check["predicates_added"], "predicates_removed": vocab_check["predicates_removed"], "predicates_changed": vocab_check["predicates_changed"],
            "sort_noun_changed": {"entity": [["entity", "entities"], ["thing", "things"]]}},
        "language_changes_since_previous_tag": {
            "from": PREV_TAG, "to": TAG,
            "merged": {"lean-first/b14b (lf-14b)": "non-first-order norm guards on closure, core and order families are decided in Lean (`VE.Norms.Family`, the `family-norms` service); ve/norms.py "
                                                   "relays them. Results are identical to the retained Python route on 1,350 corpus records; n-ary core definitions stay for batch 14c",
                       "infra/ts-B2": "test-speed and gate shadow evidence; tooling and tests",
                       "infra/english-run-root": "the English runner gets a distinct executable root; tooling",
                       "fix/subtick": "sub-tick deadline probe and gate/relay evidence repairs; tooling and tests"},
            "checked_by": "git diff ve-green-repo-map-untracked..ve-green-lf-14b --stat -- ve lean rust conformance: 20 files, namely the Lean family-norms decider (lean/VE/Norms/Family.lean, "
                          "lean/VE/Service/FamilyNorms.lean, wire and response shapes), its relay in ve/norms.py, the English runner's root and generated manifests; none is in the grammar, "
                          "profiles, lexicon or Rust",
            "newly_expressible_features": 0, "units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
            "newly_measurable": "nothing a translator can state changed; where a closure/core/order norm check runs moved from Python to Lean with identical outcomes",
            "what_made_the_difference": "the audit's repairs (u0165.s03, two small faults), not the language"},
        "question_probe": {
            "what": "`ve ask --reading --json` on the translation: five yes-or-no questions about the denial, clarification and claim-to-be-human units (probes/ask/)",
            "questions": ask_questions, "read": ask_read, "no_reading": [a["result"]["text"] for a in asks],
            "reading": "none of the five is read (the reader does not know 'must not', 'must seek clarification in each situation'); the answers differ from the previous run's only in the environment and lexicon ids"},
        "reading_set_gaps": [
            {"gap": "a defeasible rule beside norm-defaults@0 (soft-norms@0 with norm-defaults@0 is refused, probe c)", "feature": "defaults", "workaround": "one named exception predicate per set, used as an `unless` (an open term)"},
            {"gap": "“cannot be unlocked by any operator or user”: who has authority to change what a norm requires; the language has no typed authority/modal", "feature": "modality/belief", "workaround": "the clause is UNFORMALISED; its effect is carried by the hard constraints' exception-free rules"},
            {"gap": "knowing, intending and thinking something quite likely (u0173.s01): no typed epistemic modal", "feature": "modality/belief", "workaround": "two binary open terms on (instance, situation) per category in the guard of each hard constraint (AT-0p); the category's case atom stays explicit because untyped terms do not imply it"},
            {"gap": "an exception the text does not name is an open term the translator names (exception_to_*), three open terms", "feature": "other:graded-force", "workaround": "recorded as open terms with 'the source names no exception' as their only factor"},
            {"gap": "decided units are reported only for a document with companion sets; a set with `source_word` fails there", "feature": "other:RD-4b-report", "workaround": "a probe document without `source_word`"},
            {"gap": "the superposed route gives no English for a gated UNKNOWN conclusion", "feature": "other:superposed-unknown-english", "workaround": "none needed here"},
            {"gap": "a nested guard (A and B) or C does not read back through the English export", "feature": "other:english-nested-guard", "workaround": "none: the rule is kept, its English is shown and flagged as not read back"},
            {"gap": "cross-sentence scope (lead-ins, bold labels, narrowing and ordering sentences) is not a construct", "feature": "other:scope", "workaround": "the scope tally (scope-tally.json) records the governors and what they govern; no unit changes"}],
        "scope_tally": {"file": "scope-tally.json", "totals": tally["totals"], "not_tallied": tally["not_tallied"]},
        "act_workaround_m4": m4,
        "heading_presuppositions_exposed": prev_metrics["heading_presuppositions_exposed"],
        "regulated_predicates": prev_metrics["regulated_predicates"], "no_invented_permissions": prev_metrics["no_invented_permissions"],
        "vocabulary_change_check": vocab_check,
        "carried_probes_note": "the six carried probes (risk, s1, senses, senses_document, discourse, rights) re-run at this tag; byte-identical JSON: " + ", ".join(probe_same),
        "seeded_bugs": {"needed": False, "why": "no product code (Lean, Python, Rust) was changed: this run adds files under usecases/ only"},
        "conflicts": {"reported_by_VE": 0, "classification": "none to classify: CONFLICT-FREE in all 16 choices; the whole-document proof attempt of the strict companion is CONFLICT-FREE"},
    }
    # no trace of the removed terms in this run's metrics (the lists of removed terms in changes_against_previous_run and open_terms_removed_this_run name them by design)
    skip = ("changes_against_previous_run", "open_terms_removed_this_run", "audit_verified_dropped_because_changed", "checked_content_main_chain", "vocabulary_change_check")
    whole = json.dumps({k: v for k, v in m.items() if k not in skip}, ensure_ascii=False)
    assert not STALE_S03.search(whole), STALE_S03.search(whole).group(0)
    assert ledger[[e["id"] for e in ledger].index(U0126)]["open_terms"] == []
    for stale in ("force-u0125", "exception_to_never_denying", "thought_likely", "knowingly_<", "damaging_cyberweapon_or_malicious_code", "restricted_action_knowing_or_quite_likely",
                  "flat “either", "three 'should' reading sets carry content", "hard-queries-document-diff"):
        assert stale not in whole, stale
    dump("metrics.json", m)
    print(json.dumps({k: m[k] for k in ("claimed_covered_bytes", "claimed_covered_percent", "audit_verified_covered_bytes", "audit_verified_covered_percent",
                                         "audit_verified_metadata_bytes", "claimed_but_not_audit_verified_bytes", "changed_units")}))
    print(dict(u), dict(nb))
    print("probe_same:", probe_same, "profile probe same:", m["profile_combination_probe_same_as_previous_run"])
    print("ask read:", ask_read, "companion q:", {k: v["verdict"] for k, v in comp_q.items()}, "conclusions:", {k: v["verdict"] for k, v in concl.items()})


if __name__ == "__main__":
    main()
