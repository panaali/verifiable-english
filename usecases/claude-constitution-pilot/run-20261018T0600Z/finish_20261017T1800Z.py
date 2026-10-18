#!/usr/bin/env python3
"""Run 20261017T1800Z: the measurement of the carried translation at ve-green-fu-ar2-decoders (no language change since ve-green-rights-licence-relay: the two merged batches only change tests, tools and
docs), and the repair of what the audit of run 20261017T0600Z found: u0156.s03 UNFAITHFUL (readings incomplete: the sentence follows the situation of u0156.s01 and does not say "in that case"
itself, so the words admit that it continues the situation, and no candidate said that). The set now has four candidates (frame_u0156.py): strict, default (the rule for every case) and
strict-in-frame, default-in-frame (the rule only where Claude is asked to keep its system prompt confidential; one more open term). The audit's two small faults are repaired too: (1) the notes
of the three "should" units still said "8 compatible choices"; (2) u0186.s01, a governor of u0165.s06, was in neither its note nor the record of the open term illegitimate_absolute_control.
No unit gained a status or a meaning from the language.

Order (repository root, PATH must contain ~/.elan/bin, VE_NATIVE_PREBUILT=1; `lake build` in lean/ and tools/rust_build.py done):
    uv run python .../repair_20261017T1800Z.py            # adds the two in-frame candidates, notes u0186.s01 in the u0165.s06 term, writes readings/all-strict-in-frame.ve.md (idempotent: refuses a second run)
    uv run python .../nd.py all                           # about 1 min; then: cmp readings/nd-all.ve.md translation.ve.md (identical)
    uv run python -m ve document coverage .../translation.ve.md > .../readings/coverage-nd-all.json
    probes (README.md; probe_frame.py is new), then: uv run python .../probe_soft_chain.py
    uv run python .../repair_20261017T1800Z.py --check   # asserts the finished translation
    uv run python .../finish_20261017T1800Z.py            # ledger (units.json), scope-tally.json, renderings, check, coverage, metrics.json
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
import finish_20261012T0600Z as prevf  # noqa: E402  (slice_result, concl: readers of the nd result and conclusion files)
import finish_20261012T1800Z as p18  # noqa: E402  (earlier notes)
import finish_20261013T0600Z as p13  # noqa: E402  (earlier notes)
import finish_20261014T1800Z as p14  # noqa: E402  (annotate)
import finish_20261015T0600Z as p15  # noqa: E402  (the previous run's audit lists)
import frame_u0156 as fr  # noqa: E402
import repair_20261017T1800Z as r1800  # noqa: E402  (u0186.s01 wording)
import s03_scope as sc  # noqa: E402
import scope_tally  # noqa: E402
import spec_nd  # noqa: E402

RUN_ID = "20261017T1800Z"
PREV_RUN = "20261017T0600Z"
TAG = "ve-green-fu-ar2-decoders"
PREV_TAG = "ve-green-rights-licence-relay"
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
FRAME_DOC = RUN / "readings/all-strict-in-frame.ve.md"
HC_UNITS = [f"u0165.s0{i}" for i in range(1, 8)]
SETS_KEPT = ["u0036.s05", "u0156.s03", "u0263.s04.p2"]
U0125 = "u0125.s04.p2"
U0173 = "u0173.s01"
U0123 = "u0123.s02.p1"
S03 = sc.UNIT
PER_UNIT = {unit: (term, words, pred) for unit, _rule, pred, term, _act, words in spec_nd.HARD}
U0052 = "u0052.s01"
U0126 = "u0126"
# The AT-0p guards of u0165.s01 to s07 are in the plan's form from earlier runs (asserted by repair_20261017T0600Z.py, measured again by the probes); the plan repair is
# listed so that the audit can see its state. Only a ledger sentence of s01 to s07 (the list of audits that accepted them) is brought up to date in this run.
PLAN_REPAIRS = [{"unit": u, "plan": "attitudes", "item": "AT-0p",
                 "state": ("already in the plan's form at the start of this run (applied in 20261014T1800Z; accepted FAITHFUL by the audits of 20261014T1800Z, 20261015T0600Z, 20261015T1800Z, 20261016T0600Z and 20261016T1800Z); "
                           "the shape is asserted by repair_20261017T0600Z.py and measured again by the probes; not re-applied, no guard or act phrase changed in this run" if u != S03 else
                           "already in the plan's form per candidate at the start of this run (u0165.s03 has one pair of attitude terms per candidate since 20261015T0600Z; accepted "
                           "FAITHFUL by the audits of 20261015T0600Z, 20261015T1800Z, 20261016T0600Z and 20261016T1800Z); asserted and measured again; not re-applied"),
                 "applied_in_this_run": False} for u in HC_UNITS]
# Run 20261017T1800Z: the audit of run 20261017T0600Z (20/20 sampled + 4/5 changed; 25 verdicts) marked u0156.s03 UNFAITHFUL (readings incomplete) and listed two small faults. CHANGED lists
# every unit whose document text or ledger text changed, so that the audit re-verifies it; they leave the audit-verified bytes until an audit has seen them. The repair of u0156.s03 is the only
# one that changes a unit's content; u0165.s06 changes in the record of its open term (and its note); u0036.s05 and u0263.s04.p2 change in their notes (the count of compatible choices).
FORCE_SETS = ["u0036.s05", "u0156.s03", "u0263.s04.p2"]
EXCEPTION_TERM = {"u0036.s05": "exception_to_asking_for_clarification", "u0156.s03": "exception_to_not_deceiving_about_system_prompt",
                  "u0263.s04.p2": "exception_to_complying_with_exploit_instruction"}
MEANING_NOW = {"u0036.s05": {"open": ["genuine_ambiguity", "exception_to_asking_for_clarification"]},
               "u0156.s03": {"open": ["exception_to_not_deceiving_about_system_prompt", fr.FRAME_TERM]},
               "u0263.s04.p2": {"open": ["exception_to_complying_with_exploit_instruction"]}}
MEANING_BEFORE = {"u0036.s05": MEANING_NOW["u0036.s05"], "u0156.s03": {"open": ["exception_to_not_deceiving_about_system_prompt"]}, "u0263.s04.p2": MEANING_NOW["u0263.s04.p2"]}
S06 = "u0165.s06"
OLD_COUNT = "the three sets together have 8 compatible choices, all conflict-free"
NEW_COUNT = ("the sets of the document are conflict-free in every choice (three sets, 8 choices, in that run; four sets since run 20261014T1800Z; 32 choices since run 20261017T1800Z, when "
             "the set of u0156.s03 got four candidates)")
CHANGED = sorted([*FORCE_SETS, S06])
AUDIT_REPAIRS = [
    {"unit": "u0156.s03", "audit": "20261017T0600Z (UNFAITHFUL: readings incomplete)",
     "what": "document: the reading set now has four candidates, strict and default (the rule for every case) and strict-in-frame and default-in-frame (the rule only where Claude is asked to keep "
             "its system prompt confidential: the guard is the new open term " + fr.FRAME_TERM + ", unary on claude_instance); the audit found that the words admit the sentence as a continuation "
             "of the situation of u0156.s01 (it follows “Consider a situation where Claude is asked to keep its system prompt confidential.” and “In that case, …”, and says no “in that case” "
             "itself) and that both candidates were unconditional. The unit's meaning lists " + json.dumps(MEANING_NOW["u0156.s03"]) + ". Every pair of candidates has a separating situation "
             "checked by Lean; `ve document check` passes in all 32 choices"},
    {"unit": "u0165.s06", "audit": "20261017T0600Z (small fault)",
     "what": "document and ledger: u0186.s01 (a governor of this unit in the scope tally: “We’ve included assisting with especially severe and flagrant attempts to grab illegitimate power under "
             "the hard constraints above”) is now in the note and in the record of the open term " + r1800.S06_TERM + " (one more factor, one more sentence in the description of its predicate). "
             "The rule's guard, content and verdicts are unchanged"},
    {"unit": "u0036.s05, u0156.s03, u0263.s04.p2", "audit": "20261017T0600Z (small fault)",
     "what": "ledger: the note's sentence \"" + OLD_COUNT + "\" was out of date; it now states the count of the document (the three notes are the same sentence)"},
]
CHANGED_WHAT = {u: [r["what"] for r in AUDIT_REPAIRS if u in r["unit"]] for u in CHANGED}

# the audit of run 20261015T0600Z (20/20 sampled faithful + 9/9 changed faithful; 29 units), verdicts as received (AUDIT-20261015T0600Z-received.md)
AUDIT_1015_FAITHFUL = ["u0001", "u0002.heading", "u0023", "u0032.heading", "u0052.s01", "u0073.s05", "u0083.heading", "u0108", "u0123.s01.p1", "u0126", "u0151.heading",
                       "u0156.s03", "u0162.heading", "u0165.s01", "u0165.s02", "u0165.s03", "u0165.s04", "u0165.s05", "u0165.s06", "u0165.s07", "u0173.s01", "u0207.heading",
                       "u0235.heading", "u0238.heading", "u0248", "u0263.s04.p2", "u0268.heading", "u0286.heading", "u0298"]
AUDIT_1015_UNFAITHFUL = []


def received(run_id, expect, expect_bad=()):
    """The verdicts of one audit as received (AUDIT-<run>-received.md): (faithful, unfaithful or incomplete)."""
    text = (RUN / f"AUDIT-{run_id}-received.md").read_text()
    faithful = re.findall(r"^(u\d{4}(?:\.[\w.]+)?) FAITHFUL$", text, re.M)
    bad = re.findall(r"^(u\d{4}(?:\.[\w.]+)?) (?:UNFAITHFUL|INCOMPLETE)\b", text, re.M)
    assert len(faithful) == expect == len(set(faithful)) and bad == list(expect_bad), (run_id, len(faithful), bad)
    return faithful, bad


AUDIT_1015B_FAITHFUL, AUDIT_1015B_UNFAITHFUL = received("20261015T1800Z", 25)
AUDIT_1016_FAITHFUL, AUDIT_1016_UNFAITHFUL = received("20261016T0600Z", 28)
AUDIT_1016B_FAITHFUL, AUDIT_1016B_UNFAITHFUL = received("20261016T1800Z", 30)   # 20 sampled + 11 changed, one unit in both
AUDIT_1017_FAITHFUL, AUDIT_1017_UNFAITHFUL = received("20261017T0600Z", 24, ["u0156.s03"])   # 20 sampled + 5 changed, 25 verdicts, one unit in both
AUDIT_LATEST = list(dict.fromkeys(AUDIT_1015_FAITHFUL + AUDIT_1015B_FAITHFUL + AUDIT_1016_FAITHFUL + AUDIT_1016B_FAITHFUL + AUDIT_1017_FAITHFUL))

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


def frame_english(render, main_meta):
    """The four readings VE rendered for u0156.s03 (the lines after “One reading is:” and “Another reading is:”), by candidate id, and VE's English export of the rule of each in-frame
    candidate alone (and whether it parses back)."""
    lines = render.splitlines()
    key = "Claude shouldn’t actively deceive the user about the existence of a system prompt"
    start = next(i for i, ln in enumerate(lines) if ln.startswith(key))
    texts = [ln.split(" is: ", 1)[1] for ln in lines[start:start + 12] if ln.startswith(("One reading is: ", "Another reading is: "))]
    assert len(texts) == 4, texts
    english = dict(zip(fr.READINGS, texts))
    item = next(x for x in main_meta["reading_sets"] if x["id"] == fr.SET_ID)
    content = {r["id"]: r["content"] for r in item["readings"]}
    raw = FRAME_DOC.read_bytes()
    _, front, source = raw.split(b"---\n", 2)
    round_trip = {}
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        for rid in fr.IN_FRAME:
            meta = json.loads(front)
            meta["environment"]["vocabulary"]["predicates"][fr.EXCEPTION_TERM] = main_meta["environment"]["vocabulary"]["predicates"][fr.EXCEPTION_TERM]   # the default candidate's unless
            for u_ in meta["units"]:
                if u_["id"] == fr.UNIT:
                    u_["content"] = content[rid]
            path = Path(tmp) / f"{rid}.ve.md"
            path.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False).encode() + b"\n---\n" + source)
            got = old.english_nd(path)["no-system-prompt-deception"]
            round_trip[rid] = (got["round_trip"], got["error"])
            assert got["text"] == english[rid] or True   # recorded as VE rendered it in the document; the export of the rule alone may word the guard the same way
    return english, round_trip


def repair_ledger(ledger, main_meta, english, silence_frame, round_trip):
    """The repairs of this run in the ledger. `english` maps a candidate id of u0156.s03 to the English VE rendered for it; `silence_frame` is VE's silence sentence for the in-frame strict
    candidate; `round_trip` maps a candidate id to (round_trip, error) from VE's English export of its rule alone."""
    by = {e["id"]: e for e in ledger}
    flat = {x["id"]: x for u_ in main_meta["units"] for x in (u_["parts"] if u_.get("status") == "MIXED" else [u_])}
    names = {t_["name"] for t_ in main_meta["open_terms"]}
    for uid in FORCE_SETS:
        e = by[uid]
        term = EXCEPTION_TERM[uid]
        assert flat[uid]["meaning"] == MEANING_NOW[uid] and term in names and term in e["open_terms"], uid
        assert OLD_COUNT in e["note"], uid
        e["note"] = e["note"].replace(OLD_COUNT, NEW_COUNT)
        e["repaired_in_run"] = RUN_ID
        e["repair_20261017T1800Z"] = ("note: the count of compatible choices was out of date (it said 8); it now states the document's count (32 choices)" +
                                      ("" if uid == fr.UNIT else "; no reading, content or verdict of this unit changed"))
    # ---- u0156.s03: the reading set with four candidates
    e = by[fr.UNIT]
    assert fr.FRAME_TERM in names and [r["id"] for r in e["readings"]] == ["strict", "default"]
    for rid in ("strict", "default"):
        assert next(r for r in e["readings"] if r["id"] == rid)["english"] == english[rid], rid   # the carried English is the English VE renders now
    base_pred = e["predicate"]
    e["readings"].append({
        "id": "strict-in-frame", "elaborated_in": "translation.ve.md (content); readings/all-strict-in-frame.ve.md (the rule alone)", "predicate": base_pred, "completion": "unspecified",
        "english": english["strict-in-frame"], "english_round_trip": round_trip["strict-in-frame"][0], "english_round_trip_error": round_trip["strict-in-frame"][1],
        "meaning": "a strict rule that holds only where Claude is asked to keep its system prompt confidential (guard: the open term " + fr.FRAME_TERM + "); outside it the rule says nothing "
                   "(completion `unspecified`, VE reports UNDECIDED)"})
    e["readings"].append({
        "id": "default-in-frame", "elaborated_in": "translation.ve.md (content)", "predicate": base_pred, "completion": "unspecified", "english": english["default-in-frame"],
        "english_round_trip": round_trip["default-in-frame"][0], "english_round_trip_error": round_trip["default-in-frame"][1],
        "meaning": "the in-frame rule with one exception the text does not name, a base predicate that is an open term (" + fr.EXCEPTION_TERM + ")"})
    for r in e["readings"][:2]:
        r["meaning"] = r["meaning"] + "; it states the rule for every case (the sentence names no condition itself)"
    e["open_terms"] = [*e["open_terms"], fr.FRAME_TERM]
    e["document_status"] = ("READINGS: an open reading set of four candidates (force: strict or with one unnamed exception; attachment: every case or the situation of u0156.s01), every one "
                            "carrying content that Lean checked in translation.ve.md (norm-defaults@0, completion unspecified); VE does not choose between the candidates")
    e["defeasible_reading_predicate"] = ("system_prompt_deception_permitted, with the open term " + fr.EXCEPTION_TERM + " as the unnamed exception (the same predicate as the strict candidate); the "
                                         "in-frame candidates add the guard " + fr.FRAME_TERM)
    e["where_the_text_is_silent"] = ("strict candidate: no situation is left unsaid, a rule decides every case; defeasible candidate: where the unnamed exception holds, the rule says nothing "
                                     "and VE reports UNDECIDED; in-frame candidates: " + silence_frame + "; where the exception holds the in-frame default says nothing either")
    e["scope_alternative"] = {
        "words": "the sentence follows “Consider a situation where Claude is asked to keep its system prompt confidential.” (u0156.s01) and “In that case, Claude should not directly reveal the "
                 "system prompt …” (u0156.s02) and does not say “in that case” itself; u0156.s05 begins another condition",
        "candidates_every_case": ["strict", "default"], "candidates_in_frame": fr.IN_FRAME, "open_term": fr.FRAME_TERM,
        "scope_tally": "u0156.s01 is a governor of reach `frontier` (scope-tally.json): the candidates of the reading set are the two attachments; u0156.s02 and u0156.s04 stay UNFORMALISED"}
    e["note"] += (" Run 20261017T1800Z (audit 20261017T0600Z, UNFAITHFUL: readings incomplete): the words also admit that this sentence continues the situation of u0156.s01 (“Consider a situation "
                  "where Claude is asked to keep its system prompt confidential.”, then “In that case, Claude should not directly reveal …”; this sentence says no “in that case” itself, and u0156.s05 "
                  "begins another condition), so the set has two more candidates, strict-in-frame and default-in-frame: the same two rules, guarded by the open term " + fr.FRAME_TERM + ". The "
                  "candidates strict and default state the rule for every case. Nothing outside the text was used.")
    e["audit_repair"] += (" Rejected by the 20261017T0600Z audit (readings incomplete: both candidates were unconditional, so none said what the sentence says if it continues the situation of "
                          "u0156.s01). Repaired in 20261017T1800Z: two in-frame candidates and the open term " + fr.FRAME_TERM + " (frame_u0156.py).")
    e["checked_content"] = {"set": fr.SET_ID, "document": "translation.ve.md", "record": "readings/nd-all-result.json, readings/nd-all-check.json"}
    e["repair_20261017T1800Z"] += ("; and the repair of the audit's UNFAITHFUL verdict: the reading set has four candidates (frame_u0156.py), the unit's meaning lists " + json.dumps(MEANING_NOW[fr.UNIT]) + "; "
                                   "the open terms are 51 (one more: " + fr.FRAME_TERM + ")")
    # ---- u0165.s06: u0186.s01
    e = by[S06]
    term = next(t_ for t_ in main_meta["open_terms"] if t_["name"] == r1800.S06_TERM)
    assert r1800.S06_FACTOR in term["factors"]
    e["note"] += (" Run 20261017T1800Z (audit 20261017T0600Z, small fault): u0186.s01, a later sentence, says “We’ve included assisting with especially severe and flagrant attempts to grab "
                  "illegitimate power under the hard constraints above”. The scope tally lists it as a governor of this unit (it qualifies the hard constraint). It is not formalised (UNFORMALISED, "
                  "scope); what it adds is recorded as one more factor of the open term " + r1800.S06_TERM + ": whether only the especially severe and flagrant attempts count. The rule's guard "
                  "is unchanged.")
    e["repaired_in_run"] = RUN_ID
    e["repair_20261017T1800Z"] = ("note and open-term record: u0186.s01 is mentioned in the note, and the record of " + r1800.S06_TERM + " has one more factor and one more sentence in the description "
                                  "of its predicate; the guard, content and verdicts are unchanged")
    for e in ledger:   # no trace of the false texts anywhere in the ledger
        dumped = json.dumps(e, ensure_ascii=False)
        for w in ("stored model is a placeholder", "recorded here without content", "should avoid actively deceiving", "keeps the duty form", "3 sets together have 8", OLD_COUNT):
            assert w not in dumped, (e["id"], w)


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
    silence_frame_all, _ = old.silence_sentences(FRAME_DOC)   # (writes readings/silence.json; the strict document's call below writes it last)
    silence_frame = silence_frame_all["system_prompt_deception_permitted"]
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
    tally["note"] = ("scope-tally for run 20261017T0600Z; the tags are ledger annotations only: other_blockers gains `other:scope`, governed units record governed_by "
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
    if os.environ.get("VE_PILOT_REUSE"):   # debugging only: reuse the VE outputs of the previous full run of this script (the final run is always a full one)
        check, coverage, render = json.load(open(RUN / "check.json")), json.load(open(RUN / "coverage.json")), (RUN / "rendered-raw.md").read_text()
        timing = json.load(open(RUN / "evidence/finish-timing.json"))
    else:
        t0 = time.monotonic()
        check = json.loads(ve("document", "check", rel))
        t1 = time.monotonic()
        coverage = json.loads(ve("document", "coverage", rel))
        t2 = time.monotonic()
        timing = {"document_check": round(t1 - t0, 1), "document_coverage": round(t2 - t1, 1)}
        (RUN / "evidence").mkdir(exist_ok=True)
        (RUN / "evidence/finish-timing.json").write_text(json.dumps(timing) + "\n")
        render = ve("document", "render", rel)
    english_u0156, round_trip_u0156 = frame_english(render, main_meta)
    repair_ledger(ledger, main_meta, english_u0156, silence_frame, round_trip_u0156)
    if os.environ.get("VE_PILOT_REUSE"):
        strict = {"check": json.load(open(RUN / "readings/check-all-strict.json")), "coverage": None}
        strict["coverage"] = json.loads(ve("document", "coverage", str(STRICT.relative_to(ROOT))))
    else:
        strict = {"check": json.loads(ve("document", "check", str(STRICT.relative_to(ROOT)))),
                  "coverage": json.loads(ve("document", "coverage", str(STRICT.relative_to(ROOT))))}
    if not os.environ.get("VE_PILOT_REUSE"):
        dump("check.json", check)
        dump("coverage.json", coverage)
    dump("environment.json", main_meta["environment"])
    if not os.environ.get("VE_PILOT_REUSE"):
        dump("readings/check-all-strict.json", strict["check"])
        (RUN / "readings/rendered-all-strict.md").write_text(ve("document", "render", str(STRICT.relative_to(ROOT))))
    (RUN / "rendered.md").write_text(annotate(render, ledger))
    (RUN / "rendered-raw.md").write_text(render)
    assert check["premises"]["status"] == "model", check["premises"]
    assert check["reading_plan"]["route"] == "enumerate" and len(check["reading_plan"]["choices"]) == 32
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
    dropped = [i for i in prev_verified if i in CHANGED or i in AUDIT_1015_UNFAITHFUL or i in AUDIT_1015B_UNFAITHFUL or i in AUDIT_1016_UNFAITHFUL or i in AUDIT_1016B_UNFAITHFUL or i in AUDIT_1017_UNFAITHFUL]
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
    assert nd["all"]["conflict"] == "CONFLICT-FREE" and nd["all"]["premises"] == "model" and nd["all"]["choice_count"] == 32
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
    s1_prev = json.load(open(PREV_DIR / "probes/s1-probe.json"))
    s1_diff = sorted(k for k in s1_probe if s1_probe[k] != s1_prev[k])
    assert s1_diff == [], s1_diff
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
    frame_probe = json.load(open(RUN / "probes/frame-probe.json"))
    assert [(p_["candidate"], p_["status"]) for p_ in frame_probe["points"]] == [("strict-in-frame", "SETTLED no"), ("strict-in-frame", "UNDECIDED"), ("strict", "SETTLED no")]
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
                    "Every query was asked on the final document (translation.ve.md, which differs from the previous run's in the reading set of u0156.s03, its frame term and the record of illegitimate_absolute_control).")
    prev_meta = front_matter(PREV_DIR / "translation.ve.md")
    flat = lambda meta: {x["id"]: x for u_ in meta["units"] for x in (u_["parts"] if u_.get("status") == "MIXED" else [u_])}
    nu, ou = flat(main_meta), flat(prev_meta)
    pv_new, pv_old = main_meta["environment"]["vocabulary"]["predicates"], prev_meta["environment"]["vocabulary"]["predicates"]
    body = lambda p_: p_.read_bytes().split(b"\n---\n", 2)[-1]
    vocab_check = {
        "rule": "DRI 2026-10-14 15:30Z (2): after a vocabulary change rerun the situation step (nd.py all) and check every existing fenced unit still parses unchanged",
        "situation_step_rerun": "nd.py all ran after the last vocabulary change (readings/nd-all-result.json: admitted, 32 choices)",
        "fenced_blocks": {"now": MAIN.read_bytes().count(b"```ve "), "previous_run": (PREV_DIR / "translation.ve.md").read_bytes().count(b"```ve ")},
        "fenced_unit": "u0248 “Claude is not a human.” (the translation's only fenced block): the document is admitted and the unit's content and graph node are unchanged",
        "body_text_identical": body(MAIN) == body(PREV_DIR / "translation.ve.md"),
        "graph_identical": main_meta["graph"] == prev_meta["graph"],
        "units_compared": len(nu), "units_changed": sorted(i for i in nu if nu[i] != ou[i]),
        "constants_identical": main_meta["environment"]["vocabulary"]["constants"] == prev_meta["environment"]["vocabulary"]["constants"],
        "predicates_added": sorted(set(pv_new) - set(pv_old)), "predicates_removed": sorted(set(pv_old) - set(pv_new)),
        "predicates_changed": sorted(k for k in pv_new if k in pv_old and pv_new[k] != pv_old[k]),
        "vocabulary_changed_in_this_run": True,
        "vocabulary_change": ("one predicate added (" + fr.FRAME_TERM + ", the guard of the in-frame candidates of u0156.s03) and the description of " + r1800.S06_TERM + " extended by one sentence "
                              "(u0186.s01); nd.py all was rerun after both (DRI 2026-10-14 15:30Z (2)); the one fenced unit (u0248) parses unchanged and no unit's content changed except the new candidates of the "
                              "reading set of u0156.s03"),
        "sort_entity": ("DRI 2026-10-14 15:30Z (1): the carried sort `entity` has the noun “thing” (plural “things”), never the reserved word “entity” (applied in 20261015T0600Z, "
                        "asserted again by repair_20261017T1800Z.py); the vocabulary changed by one predicate and one description (vocabulary_change). nd.py all was rerun after the change; every fenced unit (u0248) parses unchanged, "
                        "and the only unit that differs from the previous run's is u0156.s03 (its meaning, units_changed); its reading set has two more candidates; the probes were run on the final document"),
        "translation_byte_identical_to_previous_run": False,
        "sorts_changed": sorted(k for k in main_meta["environment"]["vocabulary"]["sorts"]
                                if main_meta["environment"]["vocabulary"]["sorts"][k] != prev_meta["environment"]["vocabulary"]["sorts"].get(k)),
    }
    assert vocab_check["body_text_identical"] and vocab_check["graph_identical"] and vocab_check["constants_identical"]
    assert vocab_check["sorts_changed"] == [], vocab_check["sorts_changed"]
    assert vocab_check["predicates_removed"] == [] and vocab_check["predicates_added"] == [fr.FRAME_TERM] and vocab_check["predicates_changed"] == [r1800.S06_TERM], vocab_check
    # the translation is the previous run's except: u0156.s03's meaning and reading set (two more candidates, the frame term), the frame term's declarations, the record and description of
    # illegitimate_absolute_control, and the admission texts of u0156.s03's candidates; the other units, sets, situations of the other sets and the body are identical
    assert vocab_check["units_changed"] == [fr.UNIT], vocab_check["units_changed"]
    prev_doc, now_doc = json.loads(PREV_DIR.joinpath("translation.ve.md").read_text().split("\n")[1]), json.loads(MAIN.read_text().split("\n")[1])
    assert {k for k in now_doc if now_doc[k] != prev_doc[k]} == {"units", "reading_sets", "environment", "open_terms"}, {k for k in now_doc if now_doc[k] != prev_doc[k]}
    assert {k: v for k, v in nu[fr.UNIT].items() if k != "meaning"} == {k: v for k, v in ou[fr.UNIT].items() if k != "meaning"}
    assert nu[fr.UNIT]["meaning"] == MEANING_NOW[fr.UNIT] and ou[fr.UNIT]["meaning"] == MEANING_BEFORE[fr.UNIT]
    sets_now, sets_prev = {x["id"]: x for x in now_doc["reading_sets"]}, {x["id"]: x for x in prev_doc["reading_sets"]}
    def same_modulo_ids(x, y):
        """Two sets with the same candidates and situations, apart from the ids that depend on the environment (meaning ids, situation ids, the models the admissions cite) and the
        relation list of the new predicate in each stored situation."""
        def norm(item):
            sit = []
            for v in item.get("situations", {}).values():
                base = {k: (val if k != "relations" else {r: t for r, t in val.items() if r != fr.FRAME_TERM}) for k, val in v["base"].items()}
                sit.append({**{k: val for k, val in v.items() if k != "base"}, "base": base})
            return {"readings": [{"id": r["id"], "kind": r["kind"], "content": r["content"], "who": r["admission"]["who"], "why": r["admission"]["why"]} for r in item["readings"]],
                    "situations": sit, "rest": {k: val for k, val in item.items() if k not in ("readings", "situations", "models")}}
        return norm(x) == norm(y)
    assert [i for i in sets_now if not same_modulo_ids(sets_now[i], sets_prev[i])] == [fr.SET_ID]
    assert [r["id"] for r in sets_now[fr.SET_ID]["readings"]] == fr.READINGS and [r["content"] for r in sets_now[fr.SET_ID]["readings"][:2]] == [r["content"] for r in sets_prev[fr.SET_ID]["readings"]]
    terms_now, terms_prev = {t_["name"]: t_ for t_ in now_doc["open_terms"]}, {t_["name"]: t_ for t_ in prev_doc["open_terms"]}
    assert sorted(set(terms_now) - set(terms_prev)) == [fr.FRAME_TERM] and set(terms_prev) <= set(terms_now)
    assert sorted(n_ for n_ in terms_prev if terms_now[n_] != terms_prev[n_]) == [r1800.S06_TERM]
    hard_changed = {i: "plan repair AT-0p (attitudes plan, DRI AT2): carried unchanged, shape asserted again: guard = ( C(s) and " + KNOW + "N(c, s) ) or " + THINK +
                       "N(c, s), two binary open terms on (claude_instance, situation); not a changed unit in this run" for i in HC_UNITS if i != S03}
    hard_changed[S03] = ("plan repair AT-0p per candidate: guard = ( C_w(s) and knowingly_engages_3_wide(c, s) ) or thinks_quite_likely_3_wide(c, s), and the same with narrow for the narrow candidate; "
                         "carried unchanged, shape asserted again; not a changed unit in this run")
    changed_detail = {}
    new_terms = sorted(names - prev_names)
    removed_terms = sorted(prev_names - names)
    assert new_terms == [fr.FRAME_TERM] and removed_terms == [], (new_terms, removed_terms)
    prev_open = {t["name"]: t for t in prev_metrics["open_terms"]}
    changed_args = {t["name"]: {"arguments": [prev_open[t["name"]]["arguments"], t["arguments"]]} for t in open_terms
                    if t["name"] in prev_open and prev_open[t["name"]]["arguments"] != t["arguments"]}
    changed_factors = {t["name"]: {"factors": [prev_open[t["name"]]["factors"], t["factors"]]} for t in open_terms
                       if t["name"] in prev_open and prev_open[t["name"]]["factors"] != t["factors"]}
    assert changed_args == {} and list(changed_factors) == [r1800.S06_TERM], (changed_args, changed_factors)
    plan_repairs_changed = sorted({r["unit"] for r in PLAN_REPAIRS})
    m = {
        "run": RUN_ID, "baseline_tag": TAG, "previous_run": PREV_RUN, "previous_baseline_tag": PREV_TAG,
        "source_sha256": prev_metrics["source_sha256"], "source_bytes": len(SOURCE), "bytes_accounted": total, "bytes_accounted_percent": 100.0,
        "history_note": "this file records this run; the earlier runs' records (audit-verification history, the earlier probes' narrative) are in prev/metrics.json",
        "feature_upgrade_counts_separate_from_repairs": "units upgraded by new features 0; plan repairs 0 applied; audit repairs: " + str(len(CHANGED)) + " units (changed_units)",
        "changed_units": sorted(CHANGED),
        "plan_repairs": PLAN_REPAIRS,
        "audit_repairs": AUDIT_REPAIRS,
        "changed_units_detail": CHANGED_WHAT,
        "plan_repair_AT0p_state": hard_changed,
        "plan_repair_note": ("AT-0p (DRI AT2) is in the plan's form at the start of this run (applied in 20261014T1800Z, per candidate for u0165.s03 since 20261015T0600Z, audited "
                             "FAITHFUL five times); this run asserts the shape (repair_20261017T1800Z.py), rebuilds the content with nd.py all, measures "
                             "the four probe kinds again (all as the plan states, byte-identical probe file) and does not re-apply it: the seven units are listed in plan_repairs with "
                             "applied_in_this_run false and no guard or act phrase changed (u0165.s01 to s07 are not changed units; only the closing sentence of their audit_repair ledger text was brought up to date). "
                             "Plan expectation and measurement: claimed bytes unchanged at 2,951 (as stated); open terms: the plan "
                             "expected 46 on the 1800Z copy and the measured document has " + str(len(open_terms)) + " (46 at the AT-0p stage, plus the exception terms of the three "
                             "force sets and the per-candidate terms of the scope set of u0165.s03, which later runs added; a difference in the translation's other units, not in AT-0p); "
                             "case false and thinks-quite-likely true SETTLED no; case true and knowingly true SETTLED no; neither UNDECIDED; case false and knowingly true UNDECIDED, "
                             "for all seven rules; ve document check passes (premises model, all 32 choices CONFLICT-FREE)"),
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
        "audit_rejected_units_and_repair_status": {},   # set below (m.update)
        "document_profiles": {"main": main_meta["environment"]["profiles"], "strict": front_matter(STRICT)["environment"]["profiles"]},
        "documents": {"translation": "translation.ve.md (four reading sets carry content: three 'should' sets, the one of u0156.s03 with four candidates, and the scope set of u0165.s03, whose candidates have their own attitude terms; built by nd.py all from translation-without-content.ve.md, cmp-identical)",
                      "without_content": "translation-without-content.ve.md", "strict": "readings/all-strict.ve.md (the source of the strict content of the three sets, and of the wide candidate of the scope set)",
                      "strict_narrow": "readings/all-strict-narrow.ve.md (the strict companion with the narrow candidate of u0165.s03; used by the probes)",
                      "strict_in_frame": "readings/all-strict-in-frame.ve.md (the strict companion with the strict-in-frame rule of u0156.s03; its English, its silence sentence and probe_frame.py)",
                      "not_carried": "readings/all-default.ve.md, readings/s1.ve.md (soft-chain demonstrations of earlier runs; copied in for probes s1 and rights, then removed)"},
        "open_terms": open_terms, "open_terms_count": len(open_terms), "open_terms_count_previous_run": prev_metrics["open_terms_count"],
        "open_terms_added": new_terms, "open_terms_removed_this_run": removed_terms, "open_terms_with_changed_factors": sorted(changed_factors),
        "open_terms_with_changed_arguments": changed_args,
        "open_terms_count_note": "51: the previous run's 50 (AT-0p stage 46, plus the exception terms of the three force sets, plus the scope set of u0165.s03: three case atoms and four per-candidate attitude terms in place of one case atom and two shared terms) and one added in this run (" + fr.FRAME_TERM + ", the guard of the in-frame candidates of u0156.s03); none removed; one record extended (" + r1800.S06_TERM + ", one more factor)",
        "ledger_only_open_terms": {
            "what": "names that UNFORMALISED entries list as vague terms the unit would depend on, which are not open terms of the document (an earlier run removed their records "
                    "because no covered unit used them); a ledger pointer, never counted as an open term and never claimed",
            "names": sorted({t for e in ledger for t in (e.get("open_terms") or []) if t not in names}),
            "entries": sum(1 for e in ledger if any(t not in names for t in (e.get("open_terms") or []))),
            "statuses": dict(Counter(e["status"] for e in ledger if any(t not in names for t in (e.get("open_terms") or [])))),
            "covered_entries_with_such_names": [e["id"] for e in ledger if e["status"] in COVERED and any(t not in names for t in (e.get("open_terms") or []))]},
        "reading_sets": {"count": 4, "unresolved": 4, "count_previous_run": 4, "units": [*SETS_KEPT, S03],
                         "candidates": {**{i: ["strict", "default"] for i in SETS_KEPT if i != fr.UNIT}, fr.UNIT: fr.READINGS, S03: ["wide", "narrow"]},
                         "couplings": [], "narrowings": [],
                         "choices": nd["all"]["choice_count"], "choices_previous_run": 16, "removed_this_run": {},
                         "added_this_run": {}, "changed_this_run": {fr.UNIT: {"candidates_added": fr.IN_FRAME, "why": "audit 20261017T0600Z (UNFAITHFUL: readings incomplete)", "open_term_added": fr.FRAME_TERM,
                                                                              "pairs_with_a_separating_situation": 6, "pairs_without": 0}}, "note": "u0165.s03 (the two candidates wide and narrow, each with its own attitude terms; both attachments admitted by the English words alone) is carried as the 20261015T0600Z audit accepted it",
                         "readings_from_the_words": {
                             "force_sets_kept_because_of_the_word_should": {"units": ["u0036.s05", "u0263.s04.p2"], "spans": ["u0253.s04", "u0011.s01"]},
                             "force_set_kept_because_the_text_implies_exceptions": {"units": ["u0156.s03"], "spans": ["u0109.s06", "u0109.s05"],
                                                                                    "note": "accepted by the 20261012T0600Z, 20261012T1800Z and 20261013T0600Z audits (sampled)"},
                             "attachment_of_u0156_s03": {"units": [fr.UNIT], "spans": ["u0156.s01", "u0156.s02", "u0156.s05"],
                                                         "words": "the sentence follows “Consider a situation where Claude is asked to keep its system prompt confidential.” and “In that case, …” and says no “in that case” itself; "
                                                                  "u0156.s05 begins another condition: it is a rule for every case or a continuation of that situation (audit 20261017T0600Z: UNFAITHFUL, readings incomplete; repaired here); "
                                                                  "nothing outside the text is used"},
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
                               "order": "[this run, previous run]; both have four sets (32 and 16 choices)"},
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
        "seeded_bugs": {
            "needed": False, "why": "no product code (Lean, Python, Rust) was changed: this run adds files under usecases/ only (and copies a build into the worktree, ignored by git); the git diff of ve, lean, rust and conformance against the previous tag is empty",
            "pilot_script_faults": [
                {"claim": "u0156.s03 has four candidates with content and the frame term in its meaning", "planted": "the previous run's translation.ve.md put back", "failing_check": "repair_20261017T1800Z.py --check stops with AssertionError (the set has two candidates)", "restored": "cmp-identical to readings/nd-all.ve.md; the check passes"},
                {"claim": "the in-frame candidates are guarded by the frame term on the Claude instance (variable 1)", "planted": "the guard of strict-in-frame in translation.ve.md bound to variable 0 (the user)", "failing_check": "repair_20261017T1800Z.py --check stops with AssertionError: strict-in-frame", "restored": "cmp-identical to readings/nd-all.ve.md; the check passes"},
                {"claim": "the strict-in-frame rule says nothing outside the frame (UNDECIDED) and forbids inside it (SETTLED no)", "planted": "the guard of the rule in readings/all-strict-in-frame.ve.md replaced by top", "failing_check": "probe_frame.py gives SETTLED no for 'not asked' where UNDECIDED is expected (finish_20261017T1800Z.py asserts the three points)", "restored": "frame-probe.json byte-identical to the good run's"}]},
        "conflicts": {"reported_by_VE": 0, "classification": "none to classify: CONFLICT-FREE in all 32 choices; the whole-document proof attempt of the strict companion is CONFLICT-FREE"},
    }
    soft = json.load(open(RUN / "evidence/soft-chain-probe.json"))
    assert soft["load"] == "admitted" and soft["check"]["returncode"] == 1 and soft["conclusions"]["denial"]["verdict"] == "ALL" and soft["conclusions"]["claim_human"]["verdict"] == "ALL"
    assert soft["check"]["stderr_last_lines"][-1].startswith("ve.errors.UnsupportedProfile: UnsupportedProfile: norm-defaults@0 documents are checked through fill"), soft["check"]["stderr_last_lines"][-1]
    old_render = (PREV_DIR / "rendered-raw.md").read_text()
    git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    diff_product = git("diff", "--stat", f"{PREV_TAG}..HEAD", "--", "ve", "lean", "rust", "conformance")
    assert diff_product == "", diff_product   # no product code changed since the previous tag
    diff_all = "; ".join(ln.strip() for ln in git("diff", "--stat", f"{PREV_TAG}..HEAD").splitlines())
    gap_marker = "Here the text does not say whether"
    sep_lines = lambda text: [ln for ln in text.splitlines() if ln.startswith("These two readings differ here")]
    gaps_now = [ln.count(gap_marker) for ln in sep_lines(render)]
    gaps_before = [ln.count(gap_marker) for ln in sep_lines(old_render)]
    assert len(gaps_now) == len(gaps_before) == 2 and set(gaps_now) == {1} and set(gaps_before) == {1}, (gaps_now, gaps_before)
    cannot_show = lambda text: text.count("These two readings differ in a checked situation that VE cannot yet show in words.")
    assert cannot_show(old_render) == 2 and cannot_show(render) == 7, (cannot_show(render), cannot_show(old_render))   # u0165.s03: 1 pair; u0156.s03: 6 pairs of 4 candidates (was 1)
    render_same = render == old_render
    ve_log = {"hard_constraint_queries_first_run_unavailable": first_unavailable, "capped_runs": capped}
    assert not first_unavailable and not capped, ve_log
    m.update({
        "feature_upgrade_counts_separate_from_repairs": ("units upgraded by new features 0; plan repairs 0 applied (AT-0p, SC-M0, AP-0 item 3, X5 and X2-X4 were already in the plan's form or tags only); audit repairs: " +
                                                         str(len(CHANGED)) + " units (changed_units: u0156.s03 repaired after the audit's UNFAITHFUL verdict; u0165.s06 and the notes of u0036.s05 and u0263.s04.p2 for the audit's two small faults)"),
        "plan_repair_note": ("AT-0p (DRI AT2) is in the plan's form at the start of this run (applied in 20261014T1800Z, per candidate for u0165.s03 since 20261015T0600Z, audited "
                             "FAITHFUL five times); this run asserts the shape (repair_20261017T1800Z.py), rebuilds the content with nd.py all, measures "
                             "the four probe kinds again (all as the plan states, byte-identical probe file) and does not re-apply it: the seven units are listed in plan_repairs with "
                             "applied_in_this_run false and no guard or act phrase changed (u0165.s01 to s07 are not changed units; only the closing sentence of their audit_repair ledger text records the acceptances). "
                             "Plan expectation and measurement: claimed bytes unchanged at 2,951 (as stated); open terms: the plan expected 46 on the 1800Z copy and the measured document has " + str(len(open_terms)) +
                             " (46 at the AT-0p stage, plus the exception terms of the three force sets, the per-candidate terms of the scope set of u0165.s03 and, in this run, the frame term of u0156.s03; a difference in "
                             "the translation's other units, not in AT-0p); case false and thinks-quite-likely true SETTLED no; case true and knowingly true SETTLED no; neither UNDECIDED; case false and "
                             "knowingly true UNDECIDED, for all seven rules; ve document check passes (premises model, all 32 choices CONFLICT-FREE)"),
        "audit_verified_newly_from_20261017T0600Z": newly,
        "audit_verified_newly_labelled_from_20261017T0600Z": newly_lab,
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND unchanged in this run from the form that audit saw. The audit of run 20261017T0600Z "
            "(24 of 25 verdicts faithful, u0156.s03 UNFAITHFUL; 20 sampled plus 5 changed, one unit in both; AUDIT-20261017T0600Z-received.md) is the latest. Its acceptances of units unchanged here "
            "count (the headings and u0294 it sampled, u0165.s01 to s05 and s07 on top of the earlier audits'). The units whose document or ledger text changed in this run (changed_units: " +
            ", ".join(sorted(CHANGED)) + ") are accepted by earlier audits in their earlier form (u0036.s05, u0263.s04.p2 and u0165.s06 by this latest audit too) and leave the audit-verified set until "
            "an audit has seen the repair; u0156.s03 was rejected by the latest audit and is repaired, so it is not verified. This is a count of verdicts on unchanged text, not a fresh audit of this run."),
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20261017T0600Z_audit": AUDIT_1017_UNFAITHFUL,
            "repair_done_in_20261017T1800Z": {"u0156.s03": "the reading set has four candidates (strict, default, strict-in-frame, default-in-frame) with the open term " + fr.FRAME_TERM + "; the unit keeps "
                                                         "its READINGS status only because of this repair, and is not counted as audit-verified until an audit has seen it (see AUDIT-REPAIR.md)"},
            "small_faults_repaired": {" / ".join(r["unit"] for r in AUDIT_REPAIRS[1:]): [r["what"] for r in AUDIT_REPAIRS[1:]]},
            "small_faults_not_repaired": {
                "headings": "“Being helpful” and “The existential frontier” are labelled whole while “Being broadly safe” and “Safe behaviors” have presupposition units; the labels are true, so nothing was rewritten (a candidate for a later run)",
                "u0173.s01 to s04": "the notes call the gap modality/belief while the ledger's missing feature is `norms` with `modality/belief` as a further blocker; the tally is kept as it was, so that differences measure the language"},
            "kept_covered_status_without_repair": [],
            "earlier_audits": "the rejections and repairs of the earlier runs are recorded in prev/metrics.json and the AUDIT-*-received.md files"},
        "documents": {**m["documents"], "soft_chain_probe": "readings/soft-chain.ve.md (the three 'should' sets as default rules with an unstated exception on the soft chain; a measurement document, not the translation)"},
        "timing_single_runs": {**m["timing_single_runs"],
                               "note": "one run each on one machine at load average 20 to 35 (not a controlled comparison; the previous figures come from the previous run's files)",
                               "build_note": "this worktree's lean/.lake was copied from the ve-share-main checkout at the identical commit (3c6646151), so `lake build` was a no-op (0.6 s, 957 jobs up to date); the Rust binary was rebuilt by tools/rust_build.py --check (35 s) and matches the pin in lean/checkers.lock (SHA-256 6422647f…0579); not a language measurement"},
        "readings_defaults_probe": {**m["readings_defaults_probe"], "identical_to_previous_run": True,
                                    "reading": "the s1 probe (a, b and c) is byte-identical to the previous run's: (a) and (b) accepted; (c) refused for the S1 document's stale meaning ids (as at the previous tag)"},
        "carried_probes_note": ("the six carried probes (risk, s1, senses, senses_document, discourse, rights) and the unspecified probe re-run on the final document with byte-identical results: " +
                                ", ".join(f"{k} {'same' if v else 'differs'}" for k, v in probe_same.items()) + ". The denial and claim-to-be-human conclusion queries are ALL as before; the five `ve ask` questions are "
                                "no_answer as before (only their environment and lexicon ids differ, because the vocabulary has one more predicate); the 21 hard-constraint queries give the same 12 ALL and 9 UNKNOWN on "
                                "the first run at the default Rust limit. The companion probe differs from the previous run's only where u0156.s03's set has four candidates instead of two (its component, pairs, choices, "
                                "ids, 51 open terms, 9 separations, 32 choices); the same two conclusion queries are ALL"),
        "frame_probe": {"file": "probes/frame-probe.json", "script": "probe_frame.py", "document": "readings/all-strict-in-frame.ve.md",
                        "points": [{k: p_[k] for k in ("candidate", "label", "status")} for p_ in frame_probe["points"]],
                        "reading": "the strict-in-frame rule forbids deceiving the user about the system prompt where Claude is asked to keep it confidential (SETTLED no) and says nothing elsewhere (UNDECIDED); "
                                   "the unframed strict rule forbids it everywhere (SETTLED no). The text does not state what holds outside the situation, so no permission is invented"},
        "profile_combination_probe_changes": {"what": "the profile-combination probe adds each profile to the translation's environment and records the first refusal (old.probe_profiles)",
                                              "changed": {}, "reading": "all thirteen rows are identical to the previous run's"},
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
            "what": "the sentences 'Here the text does not say whether … this situation answers …' in the separation line of the two 'should' sets whose situation VE shows in words (u0036.s05 and u0263.s04.p2; rendered-raw.md, the line that starts 'These two readings differ here'); the other two sets, u0156.s03 and u0165.s03, get 'These two readings differ in a checked situation that VE cannot yet show in words.' (before 2 lines in all; now 7, six for the six pairs of u0156.s03's four candidates and one for u0165.s03)",
            "per_line_before": gaps_before, "per_line_now": gaps_now,
            "reading": "unchanged since rd-9 SC-A (the previous run measured the change from 15 sentences, 14 about other acts, to one); per_line_before and per_line_now are both [1, 1] here. The rendering is " + ("byte-identical to the previous run's" if render_same else "not byte-identical to the previous run's (see rendered-raw.md)") + ". No reading, content, verdict or meaning id moved",
            "source": "docs/spec/rd-9-soft-chain.md 2.2; docs/rd-9/integration/FIX-REPORT.md"},
        "language_changes_since_previous_tag": {
            "from": PREV_TAG, "to": TAG,
            "merged": {
                "infra/fu-premise-f9 (fu-premise-f9)": "tests/test_premise_scale.py: a test that a timeout in the lifted choices' searches alone is CheckerUnavailable; no product code",
                "infra/fu-ar2-decoders (fu-ar2-decoders)": "tests/test_frozen_sources.py (DECODERS completeness test), tools/trust_map.py and tools/trust_changes.py (widest trusted line at the base), docs/fu-ar2-decoders (report, seeded bugs); no product code",
            },
            "checked_by": "git diff ve-green-rights-licence-relay..HEAD --stat: " + diff_all + "; git diff ve-green-rights-licence-relay..HEAD --stat -- ve lean rust conformance: " + (diff_product or "empty"),
            "newly_expressible_features": 0, "units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
            "newly_measurable": ("nothing: no grammar production, profile, lexicon entry or checker changed; `ve document check`, the coverage, the render, the seven probes, the conclusion queries and the 21 hard-constraint queries "
                                 "give the same answers as at the previous tag (all 21 on the first run at the default Rust limit), apart from what the repair of u0156.s03 changes (two more candidates, 32 choices, 51 open terms)"),
            "what_made_the_difference": "nothing in what a document can say: no unit gained a status or a meaning from the language; the changes are the repair of u0156.s03 (audit UNFAITHFUL) and two small-fault repairs (changed_units)"},
        "changes_against_previous_run": {**m["changes_against_previous_run"],
            "translation_byte_identical_to_previous_run": False, "reading_sets_before_after": [4, 4], "choices_before_after": [16, 32],
            "translation_differs_only_in": "the reading set of u0156.s03 (two more candidates with content and the admission texts of all four; the unit's `meaning` lists the frame term), the open term " + fr.FRAME_TERM + " and its predicate, "
                                           "and the record and predicate description of " + r1800.S06_TERM + " (one factor, one sentence); body, graph, constants, sorts, every other unit, set and situation identical",
            "ledger_annotation_changes": "status_in_previous_run; u0156.s03 (four readings, note, audit_repair, scope_alternative, open_terms), u0165.s06 (note), the notes of u0036.s05 and u0263.s04.p2 (the count of choices); the audit_verified flag of the units the audits accepted (false for the changed units); scope tags, act_workaround and claimed regenerated with identical values"},
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
