#!/usr/bin/env python3
"""Run 20261016T1800Z: the measurement of the carried translation at ve-green-trust-ties-rd9, the repair of the small faults the audit of run 20261016T0600Z recorded
(28/28 units faithful, nothing unfaithful or incomplete), and the first probe of the soft chain (rd-9: soft-norms@0 beside norm-defaults@0). No unit gained a status or a meaning:
the batches merged since ve-green-premise-scale (rd-9 soft chain, b16e rights/readings documents in Lean, trust ties, test architecture, relay gate) do not let a unit say
more through `ve document check`. The translation (translation.ve.md) is byte-identical to the previous run's; what changed are ledger texts that were false (AUDIT-REPAIR.md).

Order (repository root, PATH must contain ~/.elan/bin, VE_NATIVE_PREBUILT=1; `lake build` in lean/ and tools/rust_build.py done):
    uv run python .../repair_20261016T1800Z.py            # asserts the documents (AT-0p shape, the true admission texts; writes nothing)
    uv run python .../nd.py all                           # about 2 min; then: cmp readings/nd-all.ve.md translation.ve.md (identical)
    uv run python -m ve document coverage .../translation.ve.md > .../readings/coverage-nd-all.json
    probes (README.md), then: uv run python .../probe_soft_chain.py
    uv run python .../finish_20261016T1800Z.py            # ledger (units.json), scope-tally.json, renderings, check, coverage, metrics.json
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
import finish_20261014T1800Z as p14  # noqa: E402  (annotate)
import finish_20261015T0600Z as p15  # noqa: E402  (the previous run's audit lists)
import s03_scope as sc  # noqa: E402
import scope_tally  # noqa: E402
import spec_nd  # noqa: E402

RUN_ID = "20261016T1800Z"
PREV_RUN = "20261016T0600Z"
TAG = "ve-green-trust-ties-rd9"
PREV_TAG = "ve-green-premise-scale"
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
U0052 = "u0052.s01"
U0126 = "u0126"
# The AT-0p guards of u0165.s01 to s07 are in the plan's form from earlier runs (asserted by repair_20261016T0600Z.py, measured again by the probes); the plan repair is
# listed so that the audit can see its state. Only a ledger sentence of s01 to s07 ("Not audited.") is brought up to date in this run.
PLAN_REPAIRS = [{"unit": u, "plan": "attitudes", "item": "AT-0p",
                 "state": ("already in the plan's form at the start of this run (applied in 20261014T1800Z; accepted FAITHFUL by the audits of 20261014T1800Z, 20261015T0600Z, 20261015T1800Z and 20261016T0600Z); "
                           "the shape is asserted by repair_20261016T1800Z.py and measured again by the probes; not re-applied, no guard or act phrase changed in this run" if u != S03 else
                           "already in the plan's form per candidate at the start of this run (u0165.s03 has one pair of attitude terms per candidate since 20261015T0600Z; accepted "
                           "FAITHFUL by the audits of 20261015T0600Z, 20261015T1800Z and 20261016T0600Z); asserted and measured again; not re-applied"),
                 "applied_in_this_run": False} for u in HC_UNITS]
# Run 20261016T1800Z: the small faults of the audit of 20261016T0600Z (28/28 units faithful; nothing unfaithful or incomplete). Each is a ledger text that said something false;
# none changes a verdict, a status or the translation. CHANGED lists the units whose ledger text was repaired, so that the audit re-verifies them; they leave the audit-verified
# bytes until that audit has seen them.
FORCE_SETS = ["u0036.s05", "u0156.s03", "u0263.s04.p2"]
OPERATOR_UNITS = ["u0062.s01", "u0123.s01.p1", "u0123.s02.p1"]
EXCEPTION_TERM = {"u0036.s05": "exception_to_asking_for_clarification", "u0156.s03": "exception_to_not_deceiving_about_system_prompt",
                  "u0263.s04.p2": "exception_to_complying_with_exploit_instruction"}
CHANGED = sorted([*FORCE_SETS, *OPERATOR_UNITS, "u0073.s05"])
AUDIT_REPAIRS = [
    {"unit": u, "audit": "20261016T0600Z (small fault)",
     "what": "ledger: the case atoms said “the situation is …” for terms whose argument is an operator input (operator_input); each now says “the operator input is …” (u0123.s03 was repaired the same way in "
             "20261016T0600Z). The terms, the document and the verdicts are unchanged"} for u in OPERATOR_UNITS] + [
    {"unit": u, "audit": "20261016T0600Z (small fault)",
     "what": "ledger: open_terms listed only " + ("genuine_ambiguity" if u == "u0036.s05" else "nothing") + ", but the default candidate of the set carries the open term " + EXCEPTION_TERM[u] +
             " as its unnamed exception; the ledger now lists it. The document, the contents and the verdicts are unchanged"} for u in FORCE_SETS] + [
    {"unit": "u0073.s05", "audit": "20261016T0600Z (small fault)",
     "what": "ledger: audit_repair ended “Counted as claimed, not audit-verified.” although the audits of 20261015T0600Z and 20261016T0600Z accepted the unit; it now records both (the text of the unit is unchanged)"},
    {"unit": "u0123.s03", "audit": "20261016T0600Z (small fault)",
     "what": "ledger: the audit_verified flag was true although the unit had been dropped as changed; the audit of 20261016T0600Z has since accepted the repaired form, so the flag is true and the unit is counted as audit-verified again (no change to the unit in this run, so it is not a changed unit)"},
    {"unit": "u0165.s01 to s07", "audit": "20261016T0600Z",
     "what": "ledger: the closing sentence of audit_repair now also records the acceptance by the audit of 20261016T0600Z (not a changed unit: no content moved)"},
]

# the audit of run 20261015T0600Z (20/20 sampled faithful + 9/9 changed faithful; 29 units), verdicts as received (AUDIT-20261015T0600Z-received.md)
AUDIT_1015_FAITHFUL = ["u0001", "u0002.heading", "u0023", "u0032.heading", "u0052.s01", "u0073.s05", "u0083.heading", "u0108", "u0123.s01.p1", "u0126", "u0151.heading",
                       "u0156.s03", "u0162.heading", "u0165.s01", "u0165.s02", "u0165.s03", "u0165.s04", "u0165.s05", "u0165.s06", "u0165.s07", "u0173.s01", "u0207.heading",
                       "u0235.heading", "u0238.heading", "u0248", "u0263.s04.p2", "u0268.heading", "u0286.heading", "u0298"]
AUDIT_1015_UNFAITHFUL = []
# the audit of run 20261015T1800Z (20/20 sampled + 5/5 changed faithful; 25 units), verdicts as received (AUDIT-20261015T1800Z-received.md)
_received = (RUN / "AUDIT-20261015T1800Z-received.md").read_text()
AUDIT_1015B_FAITHFUL = re.findall(r"^(u\d{4}(?:\.[\w.]+)?) FAITHFUL$", _received, re.M)
AUDIT_1015B_UNFAITHFUL = re.findall(r"^(u\d{4}(?:\.[\w.]+)?) (?:UNFAITHFUL|INCOMPLETE)\b", _received, re.M)
assert len(AUDIT_1015B_FAITHFUL) == 25 == len(set(AUDIT_1015B_FAITHFUL)) and AUDIT_1015B_UNFAITHFUL == []
# the audit of run 20261016T0600Z (20/20 sampled + 8/8 changed faithful; 28 units), verdicts as received (AUDIT-20261016T0600Z-received.md)
_received16 = (RUN / "AUDIT-20261016T0600Z-received.md").read_text()
AUDIT_1016_FAITHFUL = re.findall(r"^(u\d{4}(?:\.[\w.]+)?) FAITHFUL$", _received16, re.M)
AUDIT_1016_UNFAITHFUL = re.findall(r"^(u\d{4}(?:\.[\w.]+)?) (?:UNFAITHFUL|INCOMPLETE)\b", _received16, re.M)
assert len(AUDIT_1016_FAITHFUL) == 28 == len(set(AUDIT_1016_FAITHFUL)) and AUDIT_1016_UNFAITHFUL == []
AUDIT_LATEST = list(dict.fromkeys(AUDIT_1015_FAITHFUL + AUDIT_1015B_FAITHFUL + AUDIT_1016_FAITHFUL))

import os  # noqa: E402
HARD_PROBE = Path(os.environ.get("VE_PILOT_HARD_PROBE", RUN / "probes/hard-conclusions-probe.json"))  # a debugging override only
KNOW = "knowingly_engages_"
THINK = "thinks_quite_likely_"
OLD_S03_TERMS = (sc.OLD_KNOWING, sc.OLD_THINKING)
# a name of the removed shared terms, not followed by the candidate suffix (the new terms start with the same letters)
STALE_S03 = re.compile(r"(knowingly_engages_3|thinks_quite_likely_3)(?!_(wide|narrow))")

def category_of(unit):
    words = PER_UNIT[unit][1]
    return words[len("Claude "):]


def rendered_english(render, unit_text):
    """The two readings VE rendered for a reading set's sentence: (first, second), the English after “One reading is:” and “Another reading is:”."""
    lines = render.splitlines()
    key = unit_text.strip()[:45]
    start = next(i for i, ln in enumerate(lines) if key in ln)
    one = next(ln for ln in lines[start:start + 8] if ln.startswith("One reading is: "))
    other = next(ln for ln in lines[start:start + 8] if ln.startswith("Another reading is: "))
    return one[len("One reading is: "):], other[len("Another reading is: "):]


def repair_ledger(ledger, render, vocab):
    """The small faults of the audit of 20261016T0600Z: ledger texts that said something false. No status, content or verdict moves."""
    by = {e["id"]: e for e in ledger}
    for uid in OPERATOR_UNITS:
        e = by[uid]
        n = 0
        for term, text in e["case_atoms"].items():
            if vocab[term]["arguments"] == ["operator_input"]:
                assert text.startswith("the situation is "), (uid, term, text)
                e["case_atoms"][term] = "the operator input is " + text[len("the situation is "):]
                n += 1
            else:
                assert not text.startswith("the situation is "), (uid, term)
        assert n == {"u0062.s01": 9, "u0123.s01.p1": 7, "u0123.s02.p1": 10}[uid], (uid, n)   # u0123.s02.p1 has an eleventh atom, a pair of an operator and an input, already worded as such
        e["repaired_in_run"] = RUN_ID
        e["repair_20261016T1800Z"] = "ledger case atoms: the terms take an operator input, not a situation"
    for uid in FORCE_SETS:
        e = by[uid]
        term = EXCEPTION_TERM[uid]
        assert term not in e["open_terms"] and vocab[term]["arguments"], uid
        e["open_terms"] = [*e["open_terms"], term]
        # the rendering still shows what the ledger's english says (the strict and the default candidate)
        first, second = rendered_english(render, SOURCE[e["span"][0]:e["span"][1]].decode())
        assert (e["readings"][0]["english"], e["readings"][1]["english"]) == (first, second), uid
        e["repaired_in_run"] = RUN_ID
        e["repair_20261016T1800Z"] = "ledger open_terms now lists the open term of the default candidate's unnamed exception (" + term + ")"
    e = by["u0073.s05"]
    old = "Counted as claimed, not audit-verified."
    assert e["audit_repair"].rstrip().endswith(old)
    e["audit_repair"] = e["audit_repair"].rstrip()[: -len(old)].rstrip() + " Counted as claimed; accepted FAITHFUL by the audits of 20261015T0600Z and 20261016T0600Z."
    e["repaired_in_run"] = RUN_ID
    e["repair_20261016T1800Z"] = "ledger audit_repair now says the unit was audited and accepted"
    for uid in HC_UNITS:
        e = by[uid]
        old = " Accepted FAITHFUL by the audits of 20261015T0600Z and 20261015T1800Z."
        assert e["audit_repair"].rstrip().endswith(old), uid
        e["audit_repair"] = e["audit_repair"].rstrip()[: -len(old)] + " Accepted FAITHFUL by the audits of 20261015T0600Z, 20261015T1800Z and 20261016T0600Z."
    for e in ledger:   # no trace of the false texts anywhere in the ledger
        dumped = json.dumps(e, ensure_ascii=False)
        for w in ("stored model is a placeholder", "recorded here without content", "should avoid actively deceiving", "keeps the duty form"):
            assert w not in dumped, (e["id"], w)
    assert "not audit-verified" not in by["u0073.s05"]["audit_repair"]   # (the audit_repair of u0165.s01 to s07 keeps its dated history lines, which say it of an earlier state)
    for uid in OPERATOR_UNITS + ["u0123.s03"]:
        assert not any(t.startswith("the situation is ") and vocab[k]["arguments"] == ["operator_input"] for k, t in by[uid]["case_atoms"].items()), uid


def update_ledger(prev, eng, eng_narrow, silence, probe, scope_probe, binding):
    """The previous run's ledger, carried: no unit's status or content changes. Each hard constraint's four probe points are re-read from this run's probe and must equal
    what the ledger records; the English of each rule is re-read from this run's rendering."""
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
            assert e["where_the_text_is_silent"] == silence[PER_UNIT[i][2]], i
            if i != S03:
                r0 = e["readings"][0]
                assert (r0["english"], r0["english_round_trip"], r0["english_round_trip_error"]) == (eng[e["rule"]]["text"], eng[e["rule"]]["round_trip"], eng[e["rule"]]["error"]), i
        if i == S03:
            for rid, text in (("wide", eng["hc-cyberweapons"]), ("narrow", eng_narrow["hc-cyberweapons"])):
                r = next(x for x in e["readings"] if x["id"] == rid)
                assert (r["english"], r["english_round_trip"], r["english_round_trip_error"]) == (text["text"], text["round_trip"], text["error"]), rid
            assert e["scope_probe"]["points"] == sp
            assert e["open_terms"] == [*sc.ATOMS, *sc.ATTITUDES], e["open_terms"]
    # no trace of the removed terms may remain anywhere in the ledger (the per-candidate terms start with the same letters as the removed shared ones, hence the pattern)
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
    tally["note"] = ("scope-tally for run 20261016T0600Z; the tags are ledger annotations only: other_blockers gains `other:scope`, governed units record governed_by "
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
    repair_ledger(ledger, render, main_meta["environment"]["vocabulary"]["predicates"])
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

    # ---- audit-verified bytes: accepted by an audit of this lineage AND unchanged here from the form that audit saw. The units repaired in this run (CHANGED) leave the
    # audit-verified set until an audit has seen the repair; every other unit audited by 20261015T0600Z or 20261015T1800Z is identical here.
    assert len(AUDIT_1015_FAITHFUL) == 29 == len(set(AUDIT_1015_FAITHFUL))
    prev_verified = list(prev_metrics["audit_verified_covered_units"])
    dropped = [i for i in prev_verified if i in CHANGED or i in AUDIT_1015_UNFAITHFUL or i in AUDIT_1015B_UNFAITHFUL or i in AUDIT_1016_UNFAITHFUL]
    kept = [i for i in prev_verified if i not in dropped]
    newly = [i for i in AUDIT_LATEST if status[i] in COVERED and status[i] != "LABELLED" and i not in CHANGED and i not in kept]
    assert not any(by_id[i].get("claimed") is False for i in [*kept, *newly])
    verified = kept + newly
    verified_bytes = width(verified)
    cand_lab = list(dict.fromkeys(old.AUDIT_PASSED_LABELLED + old.AUDIT_PASSED_1004_LABELLED + old.AUDIT_PASSED_1004B_LABELLED + ["u0212.heading"]
                                  + prevf.AUDIT_FAITHFUL_1800 + prevf.AUDIT_FAITHFUL_1811 + p18.AUDIT_0600_FAITHFUL + p13.AUDIT_1800_FAITHFUL + p14.AUDIT_1013_FAITHFUL
                                  + p15.AUDIT_1014_FAITHFUL + AUDIT_LATEST))
    verified_lab = [i for i in cand_lab if i in by_id and status[i] == "LABELLED" and i not in CHANGED]
    verified_meta = width(verified_lab)
    newly_lab = [i for i in AUDIT_LATEST if status[i] == "LABELLED" and i in verified_lab]
    label_bytes_dropped = nb["LABELLED"] - verified_meta
    repaired_bytes = width([i for i in CHANGED if status[i] in COVERED])
    # the ledger's historical `audit_verified` flag follows the audits: true for every unit an audit accepted that is byte-identical here
    for e in ledger:
        if (e["id"] in verified or e["id"] in verified_lab or e["id"] in AUDIT_LATEST) and e["id"] not in CHANGED:
            if "audit_verified" in e:
                e["audit_verified"] = True
        if e["id"] in CHANGED and "audit_verified" in e:   # repaired in this run: not verified until an audit has seen the repair
            e["audit_verified"] = False
    dump("units.json", ledger)

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
    assert all(v for k, v in probe_same.items() if k != "s1-probe"), probe_same
    s1_probe = json.load(open(RUN / "probes/s1-probe.json"))
    s1_prev = json.load(open(PREV_DIR / "probes/s1-probe.json"))
    s1_diff = sorted(k for k in s1_probe if s1_probe[k] != s1_prev[k])
    assert s1_diff == ["c_s1_document_with_norm_defaults@0"], s1_diff
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
                    f"{len(first_unavailable)} queries first failed with CheckerUnavailable. As at the previous tag (premise-scale: the Rust limit grows with the case, ME1; eight queries had failed at the tag before) "
                    "every query answered on its first run at the default limit (VE_RUST_TIMEOUT unset), three queries in parallel, so no re-ask and no capped run was needed "
                    f"({len(capped)} capped runs, no peak resident set to record); CheckerUnavailable is not a verdict and none was used. The verdicts are identical to the previous run's. "
                    "Every query was asked on the final document (translation.ve.md, which is byte-identical to the previous run's).")
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
        "vocabulary_changed_in_this_run": False,
        "sort_entity": ("DRI 2026-10-14 15:30Z (1): the carried sort `entity` has the noun “thing” (plural “things”), never the reserved word “entity” (applied in 20261015T0600Z, "
                        "asserted again by repair_20261016T1800Z.py); no vocabulary changed in this run. nd.py all was rerun at this tag; its result is byte-identical to the previous run's translation, "
                        "so every fenced unit (u0248) parses unchanged and no unit differs; the probes were run on the final document"),
        "translation_byte_identical_to_previous_run": True,
        "sorts_changed": sorted(k for k in main_meta["environment"]["vocabulary"]["sorts"]
                                if main_meta["environment"]["vocabulary"]["sorts"][k] != prev_meta["environment"]["vocabulary"]["sorts"].get(k)),
    }
    assert vocab_check["body_text_identical"] and vocab_check["graph_identical"] and vocab_check["constants_identical"]
    assert vocab_check["sorts_changed"] == [], vocab_check["sorts_changed"]
    assert vocab_check["predicates_added"] == vocab_check["predicates_removed"] == vocab_check["predicates_changed"] == []
    # the translation is the previous run's, byte for byte: body, units, vocabulary, graph, contents, meaning ids, situations and admission texts
    assert MAIN.read_bytes() == (PREV_DIR / "translation.ve.md").read_bytes(), "translation.ve.md differs from the previous run's"
    assert vocab_check["units_changed"] == [], vocab_check["units_changed"]
    hard_changed = {i: "plan repair AT-0p (attitudes plan, DRI AT2): carried unchanged, shape asserted again: guard = ( C(s) and " + KNOW + "N(c, s) ) or " + THINK +
                       "N(c, s), two binary open terms on (claude_instance, situation); not a changed unit in this run" for i in HC_UNITS if i != S03}
    hard_changed[S03] = ("plan repair AT-0p per candidate: guard = ( C_w(s) and knowingly_engages_3_wide(c, s) ) or thinks_quite_likely_3_wide(c, s), and the same with narrow for the narrow candidate; "
                         "carried unchanged, shape asserted again; not a changed unit in this run")
    changed_detail = {}
    new_terms = sorted(names - prev_names)
    removed_terms = sorted(prev_names - names)
    assert new_terms == [] and removed_terms == [], (new_terms, removed_terms)
    prev_open = {t["name"]: t for t in prev_metrics["open_terms"]}
    changed_args = {t["name"]: {"arguments": [prev_open[t["name"]]["arguments"], t["arguments"]]} for t in open_terms
                    if t["name"] in prev_open and prev_open[t["name"]]["arguments"] != t["arguments"]}
    changed_factors = {t["name"]: {"factors": [prev_open[t["name"]]["factors"], t["factors"]]} for t in open_terms
                       if t["name"] in prev_open and prev_open[t["name"]]["factors"] != t["factors"]}
    assert changed_args == {} and changed_factors == {}, (changed_args, changed_factors)
    plan_repairs_changed = sorted({r["unit"] for r in PLAN_REPAIRS})
    m = {
        "run": RUN_ID, "baseline_tag": TAG, "previous_run": PREV_RUN, "previous_baseline_tag": PREV_TAG,
        "source_sha256": prev_metrics["source_sha256"], "source_bytes": len(SOURCE), "bytes_accounted": total, "bytes_accounted_percent": 100.0,
        "history_note": "this file records this run; the earlier runs' records (audit-verification history, the earlier probes' narrative) are in prev/metrics.json",
        "feature_upgrade_counts_separate_from_repairs": "units upgraded by new features 0; plan repairs 0 applied (AT-0p already in the plan's form); audit/small-fault repairs: " + str(len(CHANGED)) + " units (changed_units)",
        "changed_units": sorted(CHANGED),
        "plan_repairs": PLAN_REPAIRS,
        "audit_repairs": AUDIT_REPAIRS,
        "changed_units_detail": {u_: [r["what"] for r in AUDIT_REPAIRS if r["unit"] == u_] for u_ in sorted(CHANGED)},
        "plan_repair_AT0p_state": hard_changed,
        "plan_repair_note": ("AT-0p (DRI AT2) is in the plan's form at the start of this run (applied in 20261014T1800Z, per candidate for u0165.s03 since 20261015T0600Z, audited "
                             "FAITHFUL three times); this run asserts the shape (repair_20261016T0600Z.py), rebuilds the content with nd.py all, measures "
                             "the four probe kinds again (all as the plan states, byte-identical probe file) and does not re-apply it: the seven units are listed in plan_repairs with "
                             "applied_in_this_run false and no guard or act phrase changed (u0165.s01 to s07 are not changed units; only the closing sentence of their audit_repair ledger text was brought up to date). "
                             "Plan expectation and measurement: claimed bytes unchanged at 2,951 (as stated); open terms: the plan "
                             "expected 46 on the 1800Z copy and the measured document has " + str(len(open_terms)) + " (46 at the AT-0p stage, plus the exception terms of the three "
                             "force sets and the per-candidate terms of the scope set of u0165.s03, which later runs added; a difference in the translation's other units, not in AT-0p); "
                             "case false and thinks-quite-likely true SETTLED no; case true and knowingly true SETTLED no; neither UNDECIDED; case false and knowingly true UNDECIDED, "
                             "for all seven rules; ve document check passes (premises model, all 16 choices CONFLICT-FREE)"),
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
        
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND unchanged in this run from the form that audit saw. The audit of run 20261015T1800Z "
            "(20/20 sampled faithful plus 5/5 changed faithful, 25 units; AUDIT-20261015T1800Z-received.md) is the latest and rejected nothing; it recorded small faults, repaired here. "
            "Units repaired in this run (changed_units: " + ", ".join(sorted(CHANGED)) + ") are accepted by that audit in their earlier form and leave the audit-verified set until an audit "
            "has seen the repair; u0165.s01 to s07 keep theirs (their guards and acts are untouched). This is a count of verdicts on unchanged text, not a fresh audit of this run."),
        "audit_verified_metadata_bytes": verified_meta, "audit_verified_metadata_percent": round(100 * verified_meta / len(SOURCE), 4),
        "audit_verified_metadata_bytes_previous_run": prev_metrics["audit_verified_metadata_bytes"],
        "claimed_but_not_audit_verified_bytes": claimed - verified_bytes - verified_meta,
        "repaired_bytes_not_audit_verified": repaired_bytes,
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20261015T1800Z_audit": AUDIT_1015B_UNFAITHFUL,
            "repair_done_in_20261016T0600Z": "none needed for verdicts: the audit accepted all 25 units; the small faults it and the audit of 20261015T0600Z recorded are repaired (see AUDIT-REPAIR.md)",
            "small_faults_repaired": {r["unit"]: r["what"] for r in AUDIT_REPAIRS if r["unit"] not in FORCE_SETS} | {u_: next(r["what"] for r in AUDIT_REPAIRS if r["unit"] == u_) for u_ in FORCE_SETS},
            "small_faults_not_repaired": {
                "headings": "“Being helpful” and “The existential frontier” are labelled whole while “Being broadly safe” and “Safe behaviors” have presupposition units; the labels are true, so nothing was rewritten (a candidate for a later run)",
                "u0173.s01 to s04": "the notes call the gap modality/belief while the ledger's missing feature is `norms` with `modality/belief` as a further blocker; the tally is kept as it was, so that differences measure the language"},
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
        "open_terms_count_note": "unchanged from the previous run: 50 (AT-0p stage 46, plus the exception terms of the three force sets, plus the scope set of u0165.s03: three case atoms and four per-candidate attitude terms in place of one case atom and two shared terms); no term added or removed in this run",
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
                         "added_this_run": {}, "changed_this_run": {}, "note": "u0165.s03 (the two candidates wide and narrow, each with its own attitude terms; both attachments admitted by the English words alone) is carried as the 20261015T0600Z audit accepted it",
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
                               "build_note": "this worktree's lean/.lake, rust/target and .venv were copied from the ve-integration checkout at the identical commit (3160fb800); `lake build` still ran all 943 jobs (27 minutes under load) and tools/rust_build.py --check rebuilt the Rust binary, which matched the pin in lean/checkers.lock; not a language measurement",
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
                            "accepted_with_source_word": False, "refusal_with_source_word": comp_bad["check"]["stdout_error"], "defect_still_present_at_trust_ties_rd9": True,
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
            "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger), "changed_or_replaced_ids": [], "added_ids": [], "units_newly_covered": [],
            "units_with_status_change": {}, "units_changed_by_audit_repair": sorted(CHANGED),
            "open_terms_added": new_terms, "open_terms_removed": removed_terms,
            "open_terms_count_before_after": [len(prev_names), len(names)],
            "reading_sets_before_after": [4, 4], "choices_before_after": [16, 16],
            "predicates_added": vocab_check["predicates_added"], "predicates_removed": vocab_check["predicates_removed"], "predicates_changed": vocab_check["predicates_changed"],
            "translation_byte_identical_to_previous_run": False, "translation_differs_only_in": "the admission texts of the three 'should' reading sets (u0036.s05, u0156.s03, u0263.s04.p2): two false sentences replaced by true ones; body, units, vocabulary, graph, contents, meaning ids and situations identical",
            "ledger_annotation_changes": "status_in_previous_run, the audit_verified flag of the units the audits accepted; the ledger texts repaired (AUDIT-REPAIR.md); scope tags, act_workaround and claimed regenerated with identical values"},
        "language_changes_since_previous_tag": {
            "from": PREV_TAG, "to": TAG,
            "merged": {
                "infra/premise-scale (premise-scale)": "the premise-consistency check searches models with a per-sort domain budget (Lean's `search-budget` mode: a sort the premises force to hold 3 to 8 distinct things is searched at that size), "
                                                       "takes ground stated facts as their own model, reads a Rust timeout in the premise search as 'no witness' (Lean's replay then answers) and scales the Rust model-search limit "
                                                       "by the case's measured cost (at least 5 s). It decides more documents; it adds no construct a document can say",
                "lean-first/b14c (lf-14c)": "n-ary and mixed-arity `definitions@0` are elaborated by Lean (one definition order across arities); the translation uses no definitions sugar",
                "fix/x86-cpu-deadline": "a Lean service request is charged its user CPU only (deadline accounting); no language change",
                "infra/arch-AR-2, arch-AR-4, tarch-b8, test-tail": "relay typing of parse diagnostics and graph formulas, test architecture and tail tests; no language change"},
            "checked_by": "git diff ve-green-fix-abbrev..ve-green-premise-scale --stat -- ve lean rust conformance: 75 files, namely the Lean `SearchBudget` modules and their response shape "
                          "(search-budget.json), the Rust ground-fact route and scaled limit (rust/ve-profile, rust/ve), Layers/Preflight/Elaborate (lf-14c, relay typing), process limits and "
                          "generated manifests; no grammar production, profile or lexicon entry that a norm, guard or reading set of the constitution could use was added",
            "newly_expressible_features": 0, "units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
            "newly_measurable": "the Rust limit grows with the case: the 21 hard-constraint conclusion queries all answered on the first run at the default limit (eight needed re-asks, two a capped run, at the previous tag); the verdicts are identical. "
                                "The premise search reaches a Lean-checked model (it did before); the document's own constants stay one thing per sort, so the search budget raises no sort here",
            "what_made_the_difference": "nothing in what a document can say: no unit gained a status or a meaning; the only changes are the repaired texts (changed_units)"},
        "question_probe": {
            "what": "`ve ask --reading --json` on the translation: five yes-or-no questions about the denial, clarification and claim-to-be-human units (probes/ask/q*.json); and `ve ask --json` "
                    "without --reading (probes/ask/q*.answer.json)",
            "questions": ask_questions, "read": ask_read, "no_reading": [a["result"]["text"] for a in asks],
            "answers_without_reading": [json.load(open(RUN / f"probes/ask/q{i}.answer.json")).get("answer") for i in range(1, 6)],
            "reading": "none of the five is read (the reader does not know 'must not', 'must seek clarification in each situation'); the results are byte-identical to the previous run's "
                       "(with --reading and without it: `no_answer` for all five)"},
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
        "seeded_bugs": {"needed": False, "why": "no product code (Lean, Python, Rust) was changed: this run adds files under usecases/ only (and copies a build into the worktree, ignored by git)"},
        "conflicts": {"reported_by_VE": 0, "classification": "none to classify: CONFLICT-FREE in all 16 choices; the whole-document proof attempt of the strict companion is CONFLICT-FREE"},
    }
    soft = json.load(open(RUN / "evidence/soft-chain-probe.json"))
    assert soft["load"] == "admitted" and soft["check"]["returncode"] == 1 and soft["conclusions"]["denial"]["verdict"] == "ALL" and soft["conclusions"]["claim_human"]["verdict"] == "ALL"
    assert soft["check"]["stderr_last_lines"][-1].startswith("ve.errors.UnsupportedProfile: UnsupportedProfile: norm-defaults@0 documents are checked through fill"), soft["check"]["stderr_last_lines"][-1]
    old_render = (PREV_DIR / "rendered-raw.md").read_text()
    gap_marker = "Here the text does not say whether"
    sep_lines = lambda text: [ln for ln in text.splitlines() if ln.startswith("These two readings differ here")]
    gaps_now = [ln.count(gap_marker) for ln in sep_lines(render)]
    gaps_before = [ln.count(gap_marker) for ln in sep_lines(old_render)]
    assert len(gaps_now) == len(gaps_before) == 2 and set(gaps_now) == {1} and set(gaps_before) == {15}, (gaps_now, gaps_before)
    cannot_show = lambda text: text.count("These two readings differ in a checked situation that VE cannot yet show in words.")
    assert cannot_show(render) == cannot_show(old_render) == 2
    assert len(old_render) != len(render)
    ve_log = {"hard_constraint_queries_first_run_unavailable": first_unavailable, "capped_runs": capped}
    assert not first_unavailable and not capped, ve_log
    m.update({
        "feature_upgrade_counts_separate_from_repairs": "units upgraded by new features 0; plan repairs 0 applied (AT-0p already in the plan's form); audit/small-fault repairs: " + str(len(CHANGED)) + " units (changed_units, ledger texts only)",
        "plan_repair_note": ("AT-0p (DRI AT2) is in the plan's form at the start of this run (applied in 20261014T1800Z, per candidate for u0165.s03 since 20261015T0600Z, audited "
                             "FAITHFUL four times); this run asserts the shape (repair_20261016T1800Z.py), rebuilds the content with nd.py all (cmp-identical to the previous translation), measures "
                             "the four probe kinds again (all as the plan states, byte-identical probe file) and does not re-apply it: the seven units are listed in plan_repairs with "
                             "applied_in_this_run false and no guard or act phrase changed (u0165.s01 to s07 are not changed units; only the closing sentence of their audit_repair ledger text records the new acceptance). "
                             "Plan expectation and measurement: claimed bytes unchanged at 2,951 (as stated); open terms: the plan expected 46 on the 1800Z copy and the measured document has " + str(len(open_terms)) +
                             " (46 at the AT-0p stage, plus the exception terms of the three force sets and the per-candidate terms of the scope set of u0165.s03, which later runs added; a difference in "
                             "the translation's other units, not in AT-0p); case false and thinks-quite-likely true SETTLED no; case true and knowingly true SETTLED no; neither UNDECIDED; case false and "
                             "knowingly true UNDECIDED, for all seven rules; ve document check passes (premises model, all 16 choices CONFLICT-FREE)"),
        "audit_verified_newly_from_20261016T0600Z": newly,
        "audit_verified_newly_labelled_from_20261016T0600Z": newly_lab,
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND unchanged in this run from the form that audit saw. The audit of run 20261016T0600Z "
            "(20/20 sampled faithful plus 8/8 changed faithful, 28 units; AUDIT-20261016T0600Z-received.md) is the latest and rejected nothing; it recorded small faults, repaired here. "
            "Its acceptance of u0123.s03 (the repaired form, unchanged here) puts that unit back in the verified set. Units whose ledger text was repaired in this run (changed_units: "
            + ", ".join(sorted(CHANGED)) + ") are accepted by that audit (u0073.s05, u0036.s05, u0156.s03, u0263.s04.p2, u0062.s01, u0123.s01.p1) or earlier audits in their earlier form and leave the "
            "audit-verified set until an audit has seen the repair (u0123.s02.p1 was not in the 0600Z sample); u0165.s01 to s07 keep theirs (their guards and acts are untouched). "
            "This is a count of verdicts on unchanged text, not a fresh audit of this run."),
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20261016T0600Z_audit": AUDIT_1016_UNFAITHFUL,
            "repair_done_in_20261016T1800Z": "none needed for verdicts: the audit accepted all 28 units; the small faults it recorded are repaired (see AUDIT-REPAIR.md)",
            "small_faults_repaired": {r["unit"]: r["what"] for r in AUDIT_REPAIRS},
            "small_faults_not_repaired": {
                "headings": "“Being helpful” and “The existential frontier” are labelled whole while “Being broadly safe” and “Safe behaviors” have presupposition units; the labels are true, so nothing was rewritten (a candidate for a later run)",
                "u0173.s01 to s04": "the notes call the gap modality/belief while the ledger's missing feature is `norms` with `modality/belief` as a further blocker; the tally is kept as it was, so that differences measure the language"},
            "kept_covered_status_without_repair": [],
            "earlier_audits": "the rejections and repairs of the earlier runs are recorded in prev/metrics.json and the AUDIT-*-received.md files"},
        "documents": {**m["documents"], "soft_chain_probe": "readings/soft-chain.ve.md (the three 'should' sets as default rules with an unstated exception on the soft chain; a measurement document, not the translation)"},
        "timing_single_runs": {**m["timing_single_runs"],
                               "note": "one run each on one machine at load average 9 to 30 (not a controlled comparison; the previous figures come from the previous run's files)",
                               "build_note": "this worktree's lean/.lake, rust/target and .cargo-home were copied from the ve-integration checkout at the identical commit (171faae80); `lake build` still ran all 957 jobs (17 minutes 50 seconds) and tools/rust_build.py --check rebuilt the Rust binary, which matched the pin in lean/checkers.lock; not a language measurement"},
        "readings_defaults_probe": {**m["readings_defaults_probe"], "identical_to_previous_run": False,
                                    "differs_from_previous_run_in": s1_diff,
                                    "reading": ("probe (c) adds norm-defaults@0 to the S1 document, which carries soft-norms@0, without re-identifying its readings. Before, the loader refused it by profile "
                                                "(`UnsupportedProfile: norm-defaults@0 documents on the soft and rights routes await the Lean route`); at this tag the refusal is gone for the soft route (the text now names the rights route only) "
                                                "and the document is refused further on, for its stale meaning ids. The soft chain is therefore reachable (probes/soft-chain below); (a) and (b) are byte-identical to the previous run's")},
        "carried_probes_note": ("five of the six carried probes (risk, senses, senses_document, discourse, rights) re-run at this tag with byte-identical JSON; the s1 probe differs in its last point only "
                                "(readings_defaults_probe): " + ", ".join(f"{k} {'same' if v else 'differs'}" for k, v in probe_same.items())),
        "profile_combination_probe_changes": {
            "what": "the profile-combination probe adds each profile to the translation's environment and records the first refusal (old.probe_profiles); two rows differ from the previous run's, the other eleven are identical",
            "changed": {k: {"previous_run": prev_metrics["profile_combination_probe"][k], "now": profile_probe[k]} for k in profile_probe if profile_probe[k] != prev_metrics["profile_combination_probe"].get(k)},
            "reading": "soft-norms@0 beside norm-defaults@0 is no longer refused at load by the old 'await the Lean route' text: the document loads and the refusal comes later, in the claim-graph admission "
                       "(ve document check, see soft_chain_probe). rights@0 now reaches the rights route's own refusal for norm-defaults@0 (it said 'rights@0 requires soft-norms@0' before, because the "
                       "check order changed); the constitution uses neither rights@0 beside norm-defaults@0 nor needs it"},
        "soft_chain_probe": {
            "what": "the three 'should' sets with their defeasible candidate stated natively on the soft chain (rd-9: soft-norms@0 added beside norm-defaults@0; each default candidate is a default rule with "
                    "`exception: {decided_by: unstated}` and `unless: []`; the three invented exception_to_* open terms are not needed). Everything else is the translation. Not adopted (see result)",
            "file": "evidence/soft-chain-probe.json", "document": "readings/soft-chain.ve.md", "script": "probe_soft_chain.py",
            "open_terms_before_after": [soft["open_terms_before"], soft["open_terms_after"]],
            "result": {"document_load": soft["load"], "situation_search": "all pairs separated by a situation Lean checked (no pair without situation, no limit)",
                       "ve_document_coverage": soft["coverage"], "ve_document_render": soft["render"],
                       "ve_document_readings_denial_query": soft["conclusions"]["denial"], "ve_document_readings_claim_human_query": soft["conclusions"]["claim_human"],
                       "ve_document_check": {"returncode": 1, "outcome": "an uncaught `UnsupportedProfile: norm-defaults@0 documents are checked through fill (ve.norm_defaults)` with a Python traceback, raised from ve/document.py `_report` -> ve/soft_route.py `admit_soft_document(lower_env, ...)` -> the `soft-elaborate` service call",
                                             "cause_as_read_from_the_traceback": "the claim-graph admission is asked of the Lean soft route with the lower environment `_lower_route(doc)` returns, which still lists norm-defaults@0 (only readings@1 is stripped); the soft document beside it was rewritten with the unspecified placeholder. Not verified beyond the traceback",
                                             "stderr_last_lines": soft["check"]["stderr_last_lines"]}},
            "decision": "the translation keeps the exception_to_* workaround: the plan's rule keeps a repair only if `ve document check` passes, and it does not on the soft-chain document. Not an upgrade; no unit's status or content changes",
            "what_it_would_change_if_check_passed": "47 open terms instead of 50; the defeasible candidates become 'default rule, unstated exception' (the spec's C1 to C4) instead of 'strict rule unless an open term the translator invented'; the units would stay READINGS"},
        "separation_line_gap_sentences": {
            "what": "the sentences 'Here the text does not say whether … this situation answers …' in the separation line of the two 'should' sets whose situation VE shows in words (u0036.s05 and u0263.s04.p2; rendered-raw.md, the line that starts 'These two readings differ here'); the other two sets, u0156.s03 and u0165.s03, get 'These two readings differ in a checked situation that VE cannot yet show in words.' (before and now)",
            "per_line_before": gaps_before, "per_line_now": gaps_now,
            "reading": "rd-9 SC-A: Lean now names the gap atoms the separating pair's witness uses, and the renderer shows only those. Before, every point of every filled table was listed (15 sentences, 14 about other acts); now each line shows the one its value reads. A display change only: no reading, content, verdict or meaning id moved",
            "source": "docs/spec/rd-9-soft-chain.md 2.2; docs/rd-9/integration/FIX-REPORT.md"},
        "language_changes_since_previous_tag": {
            "from": PREV_TAG, "to": TAG,
            "merged": {
                "rd-9/integrate (rd-9)": "the soft chain (readings@1 x soft-norms@0 x norm-defaults@0): Lean admits such a document, separates its readings on filled sides and checks each choice (readings-validate, -elaborate, -choice, -verdicts, norm-defaults-certificate); "
                                         "per-pair `gaps` on separation lines and `decided_units` on enumerated verdict answers (SC-A); the R14 candidate wording. The public availability of the route is signed only once the full gate passes on the final head, and `ve document check` does not carry it yet (soft_chain_probe)",
                "lean-first/b16e (lf-16e)": "Lean's `document` mode decides rights@0 documents with and without readings@1, and readings@1 documents without norm-defaults@0 (it calls the existing rights and soft routes). The constitution uses neither rights@0 nor a soft document without norm-defaults@0, so nothing here applies to a unit",
                "infra/trust-ties-rd9, fix/relay-mutation-gate": "trust classification ties and a relay mutation gate over every route; no language change",
                "infra/tarch-contract, tarch-leanshare, tarch-split, tarch-select, fix/ci-run-timeout, infra/ts-B3": "test architecture, test speed and CI timeouts; no language change"},
            "checked_by": "git diff ve-green-premise-scale..HEAD --stat -- ve lean rust conformance: 68 files, namely rd-9's Lean (SoftWire, SoftSeparate, SoftVerdicts, LayeredAdmission, LayeredEntail, Readings Run/VerdictsWire) and its response shapes, "
                          "the readings and rights relays, softnorms/document.py, and one file under ve/surface (rights.py, 14 lines); no grammar production, profile or lexicon entry that a norm, guard or reading set of the constitution could use was added",
            "newly_expressible_features": 0, "units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
            "newly_measurable": ("the soft chain loads, renders, covers and answers `ve document readings` queries on the constitution (soft_chain_probe) but `ve document check` refuses it; the separation lines show one gap sentence "
                                 "instead of 15 (separation_line_gap_sentences); the 21 hard-constraint queries and the two conclusion queries answer as before, all on the first run at the default Rust limit"),
            "what_made_the_difference": "nothing in what a document can say: no unit gained a status or a meaning; the only changes are the repaired ledger texts (changed_units)"},
        "changes_against_previous_run": {**m["changes_against_previous_run"],
            "translation_byte_identical_to_previous_run": True,
            "translation_differs_only_in": "nothing: translation.ve.md is byte-identical to the previous run's (the ledger texts are what changed)",
            "ledger_annotation_changes": "status_in_previous_run; the audit_verified flag of the units the audits accepted (false for the changed units); the ledger texts repaired (AUDIT-REPAIR.md); scope tags, act_workaround and claimed regenerated with identical values"},
        "question_probe": {**m["question_probe"], "reading": "none of the five is read (the reader does not know 'must not', 'must seek clarification in each situation'); the results are byte-identical to the previous run's "
                                                              "(with --reading and without it: `no_answer` for all five)"},
        "reading_set_gaps": [dict(g) for g in m["reading_set_gaps"]],
    })
    m["reading_set_gaps"][0] = {"gap": "a defeasible rule beside norm-defaults@0 as the language's own mode: loads and answers queries (soft chain), but `ve document check` refuses the document", "feature": "defaults",
                                "workaround": "one named exception predicate per set, used as an `unless` (an open term); the native form was tried (soft_chain_probe) and not adopted"}
    m["checked_content_main_chain"]["not_representable"][0] = ("defeasibility beside norm-defaults@0 as VE's own mode: documents load and answer `ve document readings` queries (soft_chain_probe), "
                                                               "`ve document check` raises UnsupportedProfile (an uncaught error); probe c of the s1 probe no longer refuses the profile")
    m["checked_content_main_chain"]["conclusion_probes"]["hard_constraint_queries"]["reading"] = hard_reading
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
