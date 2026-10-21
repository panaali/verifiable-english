#!/usr/bin/env python3
"""Run 20261021T0600Z: the measurement of the translation at ve-green-sc-1ad, starting from the translation of run 20261020T1800Z, with the repairs of the audit of that run.

Features: five batches merged since ve-green-sc-1ac (ap-1c, me-6b, et-3cb, df-1ac, sc-1ad). None lets a document say something new: every DELTA.md says "None" / "what users see does not change" / "public output: none"
and no ve/ rust/ conformance file changes behaviour (git diff ve-green-sc-1ac..ve-green-sc-1ad -- ve rust conformance: only ve/assurance-manifest.json). `scope@0`, `defaults@0`, `calc@0`, `acts@0`, `judgments@0` are still refused.
Audit repairs (the audit of 20261020T1800Z marked four units unfaithful; repair_20261021T0600Z.py, frame_u0156.py, nd.py own the document changes, this script the ledger):
  * u0168.s01: the guard is binary on (claude_instance, situation) (it took only the situation);
  * u0156.s03: the in-frame candidates' frame term is binary on (claude_instance, user) (it took only the instance);
  * u0036.s05 (and u0263.s04.p2, the same shape and the same rendering sentence): back to UNFORMALISED (other:silence-display), the rendering says “c is not required to” for silence and the translator cannot change that product wording;
  * u0013.presupposition: back to UNFORMALISED (PS-0p step 3: not claimed).

Order (repository root, PATH must contain ~/.elan/bin, VE_NATIVE_PREBUILT=1; `lake build` in lean/ and tools/rust_build.py done):
    uv run python .../nd.py all ; cmp readings/nd-all.ve.md prev/translation.ve.md ; uv run python .../checkpoint.py final ; owner_probe.py ; probes (README.md), rerun_queries.py, probe_hard_conclusions.py, probe_soft_chain.py
    uv run python .../finish_20261021T0600Z.py           # ledger (units.json), scope-tally.json, presupposition-goals.json, renderings, check, coverage, metrics.json
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

RUN_ID = "20261021T0600Z"
PREV_RUN = "20261020T1800Z"
AUDIT_RUN = "20261020T1800Z"   # the latest audit received: the audit of PREV_RUN (22 of 26 verdicts faithful, four unfaithful)
TAG = "ve-green-sc-1ad"
PREV_TAG = "ve-green-sc-1ac"
COVERED = old.COVERED
SOURCE = old.SOURCE
front_matter = old.front_matter
_ve_plain = p17.ve


def ve(*args):
    """`ve ...` through the previous run's helper; with FINISH_CACHE=1 the output is memoised in /tmp keyed by the arguments and the bytes of the files named (a development aid; the final run is without it)."""
    if os.environ.get("FINISH_CACHE") != "1":
        return _ve_plain(*args)
    key = hashlib.sha256(json.dumps([list(args), [hashlib.sha256((ROOT / a).read_bytes()).hexdigest() for a in args if a.endswith(".ve.md") and (ROOT / a).exists()]]).encode()).hexdigest()
    path = Path("/tmp/ve-finish-cache-" + key)
    if path.exists():
        return path.read_text()
    out = _ve_plain(*args)
    path.write_text(out)
    return out
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
AUDIT_1019B_FAITHFUL, AUDIT_1019B_UNFAITHFUL = p17.received("20261019T1800Z", 31)   # 20 sampled + 9 changed + 2 PS-0p class-B items, 31 verdicts, none unfaithful
assert AUDIT_1019B_UNFAITHFUL == []
AUDIT_REJECTED = ["u0013.presupposition", "u0036.s05", "u0156.s03", "u0168.s01"]
AUDIT_1020_FAITHFUL, AUDIT_1020_UNFAITHFUL = p17.received(AUDIT_RUN, 28, AUDIT_REJECTED)   # 17 of 20 sampled and 11 of 12 supplementary verdicts faithful (28), four unfaithful, four unfaithful (AUDIT-20261020T1800Z-received.md)
AUDIT_LATEST = list(dict.fromkeys(p17.AUDIT_LATEST + p17.received("20261017T1800Z", 28)[0] + AUDIT_1018_FAITHFUL + AUDIT_1018B_FAITHFUL + AUDIT_1019_FAITHFUL + AUDIT_1019B_FAITHFUL + AUDIT_1020_FAITHFUL))
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
    """scope@0, defaults@0, calc@0 (this tag) and acts@0, judgments@0 (the tag before) are Lean modules: add each to the strict companion's environment and record what `ve document check` says."""
    import tempfile
    base = STRICT.read_bytes()
    end = base.index(b"\n---\n", 4)
    meta, tail = json.loads(base[4:end]), base[end + 5:]
    result = {}
    for extra in ("scope@0", "defaults@0", "calc@0", "acts@0", "judgments@0"):
        m_ = json.loads(json.dumps(meta))
        m_["environment"]["profiles"] = sorted(set(m_["environment"]["profiles"]) | {extra})
        with tempfile.NamedTemporaryFile("wb", suffix=".ve.md", delete=False) as handle:
            handle.write(b"---\n" + json.dumps(m_, ensure_ascii=False, separators=(",", ":")).encode() + b"\n---\n" + tail)
        proc = subprocess.run([sys.executable, "-m", "ve", "document", "check", handle.name], cwd=ROOT, capture_output=True, text=True)
        Path(handle.name).unlink()
        result[extra] = "accepted at document-check level" if proc.returncode == 0 else (proc.stderr.strip().splitlines() or ["rejected"])[-1].split(": ", 1)[-1]
    return result


# ---- the audit repairs of this run (document changes: repair_20261021T0600Z.py, frame_u0156.py, nd.py)
REPAIR_KEYS_DROPPED = ("kind", "rule", "predicate", "sign", "open_terms", "case_atoms", "reading_set", "readings", "document_status", "checked_content", "repaired_in_run", "note_edited_in_run",
                       "claimed", "act_workaround", "audit_repair", "scope_alternative", "previous_status", "previous_missing_feature", "strict_reading_predicate", "defeasible_reading_predicate",
                       "where_the_text_is_silent", "audit_verified", "check", "completion", "force_resolution") + tuple(f"repair_{d}" for d in
                       ("20261016T0600Z", "20261016T1800Z", "20261017T0600Z", "20261017T1800Z"))
DEMOTED = {
    "u0036.s05": "Claude should ask for clarification in cases of genuine ambiguity.",
    "u0263.s04.p2": "in situations where Claude has explicitly been instructed not to engage in unintended exploits, it should comply.",
}
SILENCE_FEATURE = "other:silence-display"
SILENCE_WHY = ("`ve document render` shows the separating situation of a reading set whose candidates are a strict duty and the same duty with one exception as “Here the text does not say whether c must ... in s; this "
               "situation answers ‘no’. Under (1), c still must. Under (2), c is not required to.” (`ve/readings_english.py`, `outcome_sentence`: the probe value false of an obligation is worded “is not required to”). "
               "The separating situation is the only place where the two candidates differ, so every set of this shape shows that sentence. It is a product wording the translator does not own, so it cannot be repaired in the "
               "translation: the set, its candidates, its case predicate, its exception term and its stored situations are removed with every trace. The words “should” still admit a strict and a defeasible duty "
               "(u0253.s04, u0011.s01); nothing is claimed of either now. Missing feature: other:silence-display (the display of a defeasible candidate's silence as ‘the text does not say’ rather than ‘not required’). "
               "Restoring the set once that wording is fixed would give back ")
U13_NOTE = ("Back to UNFORMALISED (24 B not claimed). PS-0p step 3 of the prompt: u0013, u0095, u0002 and u0235 are not claimed, and the audit of 20261020T1800Z marked the claim UNFAITHFUL for exactly that reason: “The existence claim is "
            "intelligible, but claiming it violates this prompt’s explicit PS-0p exclusion. Earlier audit acceptance does not supersede that instruction.” The heading “Claude’s core values” takes for granted that Claude has core values "
            "(a possessive); that is the presupposed claim, and it is not formalised. The prompt's note for step 3 says “relational-noun wording not admitted in VE English (PS-0p phase 1)”; at this tag that is no longer measured "
            "(ps-6r admits “{0} is a core value of {1}”, evidence/ps6r/wording-lint.json), so the unit is left unclaimed because the instruction says so, not because the wording is refused. The predicate and the fence are "
            "removed from the document with every trace.")
U13_EXPRESSIBLE = {"feature": "ps-6r", "fence": "Some thing is a core value of claude.", "blocked_by": "PS-0p step 3 of the prompt (do not claim u0013) and, as for u0095, the premise-check budget and the lower-case constant (evidence/owner-probe.json)",
                   "owner": "the constant `claude`, lower case as the document's English writes a constant inside a sentence"}
U156_REPAIR = ("Repaired in 20261021T0600Z (audit 20261020T1800Z, UNFAITHFUL: “The two contextual readings bind confidentiality only to the Claude instance, losing the situation and associated user. A request in one context "
               "consequently governs every user for that instance; these candidates misrepresent the contextual reading.”). The frame term " + fr.FRAME_TERM + " was unary on the instance; it is now binary on "
               "(claude_instance, user), like the exception term and the regulated act, so a request made in the conversation of an instance with one user governs that instance toward that user and no other "
               "(probes/frame-probe.json, binding_points: SETTLED no for that pair, UNDECIDED for the same instance toward another user and for another instance toward the same user). The situation the source names "
               "is that conversation: a third argument is impossible (a predicate of the relational profile has at most two arguments, lean/VE/Route/Wire.lean), so the pair stands for it, and the term's third factor says so. "
               "The act phrase, the exception term and the candidates strict and default are unchanged; the guard of the in-frame candidates changed from asked(c) to asked(c, u). The reading set now has two sets in the document "
               "(this one and u0165.s03's) and 8 choices.")
U168_REPAIR = ("Repaired in 20261021T0600Z (audit 20261020T1800Z, UNFAITHFUL: “The guard depends only on the situation. One instance facing an argument therefore imposes firmness on every instance, strengthening the source’s "
               "condition.”). The open term seemingly_compelling_argument_to_cross_line is now binary on (claude_instance, situation) and the guard binds the acting instance (c is var 1, s is var 0): firmness is required of an "
               "instance that faces the argument, not of every instance in the situation (probes/unspecified-probe.json, binding_points: SETTLED yes for the instance that faces the argument, UNDECIDED for another instance in the "
               "same situation). The act phrase and the strict reading are unchanged.")


def apply_repairs(ledger, eng, silence, silence_frame, probe, frame_probe, frame_en, frame_rt):
    by = {e["id"]: e for e in ledger}
    # 1. u0013.presupposition: PS-0p step 3
    e = by["u0013.presupposition"]
    assert e["status"] == "CHECKED" and e["claimed"] is True
    for k in list(e):
        if k in ("kind", "support", "claimed", "checked_english", "carrier", "trigger", "trigger_words", "previous_status", "previous_missing_feature", "previous_presupposed_claim", "offered_to_audit",
                 "feature_upgrade", "audit_verified", "changed_in_run"):
            del e[k]
    e.update({"status": "UNFORMALISED", "missing_feature": "other:discourse", "presupposed_claim": "Claude has core values.", "note": U13_NOTE, "status_in_previous_run": "CHECKED",
              "expressible_with": U13_EXPRESSIBLE, "changed_in_run": RUN_ID,
              "audit_repair": {"audit": AUDIT_RUN, "verdict": "UNFAITHFUL", "cause": "the claim violates the PS-0p step 3 exclusion of the prompt (u0013 is not claimed)",
                               "repair": "back to UNFORMALISED (other.discourse); the predicate core_value_of and the fence are removed; 24 B not claimed"}})
    # 2. u0036.s05 and u0263.s04.p2: the display of silence
    for uid, text in DEMOTED.items():
        e = by[uid]
        assert e["status"] == "READINGS" and e["claimed"] is True and e["source_excerpt"].strip().endswith(text[-20:].strip())
        width = e["span"][1] - e["span"][0]
        for k in REPAIR_KEYS_DROPPED:
            e.pop(k, None)
        if uid == "u0036.s05":
            why = ("Back to UNFORMALISED (" + str(width) + " B not claimed). The audit of " + AUDIT_RUN + " marked this unit UNFAITHFUL: “The rendering converts silence under the defeasible reading into “c is not required to.” "
                   "Its formal completion is unspecified: absence of an obligation verdict does not establish exemption.” ")
            cause = "the rendering of the reading set words the defeasible candidate's silence as “c is not required to” (audit of " + AUDIT_RUN + ")"
        else:
            why = ("Back to UNFORMALISED (" + str(width) + " B not claimed). The audit of " + AUDIT_RUN + " did not sample this unit; it marked u0036.s05, whose reading set has the same shape (a strict duty and the same duty with one "
                   "unnamed exception) and whose rendering has the same sentence (the previous run's rendered-raw.md ends this unit's separating line with “c is not required to.”). The cause is the same, so the repair is the same "
                   "(as the repair of 12 October took the hard constraints the audit had not sampled together with the ones it had). ")
            cause = "same candidate shape and same rendering sentence as u0036.s05 (rejected by the audit of " + AUDIT_RUN + "); not itself sampled"
        e.update({"status": "UNFORMALISED", "missing_feature": SILENCE_FEATURE, "note": why + SILENCE_WHY + str(width) + " B.", "open_terms": [], "status_in_previous_run": "READINGS",
                  "changed_in_run": RUN_ID, "act_workaround_stale": True,
                  "audit_repair": {"audit": AUDIT_RUN, "verdict": "UNFAITHFUL" if uid == "u0036.s05" else "same cause, not sampled", "cause": cause,
                                   "repair": "back to UNFORMALISED (" + SILENCE_FEATURE + "); the reading set, its candidates, case predicate, exception term and stored situations are removed; " + str(width) + " B not claimed"}})
    # 3. u0156.s03: the frame term binds the instance and the user
    e = by[fr.UNIT]
    for rid in ("strict-in-frame", "default-in-frame"):
        r = next(x for x in e["readings"] if x["id"] == rid)
        r["english"], r["english_round_trip"], r["english_round_trip_error"] = frame_en[rid], frame_rt[rid][0], frame_rt[rid][1]
        r["meaning"] = r["meaning"].replace("guard: the open term " + fr.FRAME_TERM + ")", "guard: the open term " + fr.FRAME_TERM + ", on the instance and the user)")
    e["defeasible_reading_predicate"] = ("system_prompt_deception_permitted, with the open term " + fr.EXCEPTION_TERM + " as the unnamed exception (the same predicate as the strict candidate); the in-frame candidates "
                                         "add the guard " + fr.FRAME_TERM + " (c, u)")
    e["where_the_text_is_silent"] = ("strict candidate: no situation is left unsaid, a rule decides every case; defeasible candidate: where the unnamed exception holds, the rule says nothing and VE reports "
                                     "UNDECIDED; in-frame candidates: " + silence_frame + "; where the exception holds the in-frame default says nothing either")
    e["scope_alternative"]["open_term"] = fr.FRAME_TERM
    e["scope_alternative"]["binds"] = "the instance of Claude and the user it talks with (the conversation is the pair)"
    e["note"] += " " + U156_REPAIR
    e["audit_repair"] += (" Rejected by the " + AUDIT_RUN + " audit (UNFAITHFUL: the frame term bound only the instance, so a request governed every user). Repaired in 20261021T0600Z: the frame term is binary on (claude_instance, user).")
    e["repair_20261021T0600Z"] = ("audit repair: the frame term " + fr.FRAME_TERM + " is binary on (claude_instance, user); the in-frame candidates' English and silence sentence are re-read from this run's rendering; "
                                  "the document has 2 reading sets and 8 choices (it was 4 sets and 32)")
    e["changed_in_run"] = RUN_ID
    e["frame_binding_probe"] = {"file": "probes/frame-probe.json", "points": [{"label": p["label"], "tuple": p["tuple"], "status": p["status"]} for p in frame_probe["binding_points"]]}
    # 4. u0168.s01: the guard binds the instance
    e = by["u0168.s01"]
    r0 = e["readings"][0]
    en = eng["remain-firm-under-argument"]
    r0["english"], r0["english_round_trip"], r0["english_round_trip_error"] = en["text"], en["round_trip"], en["error"]
    r0["meaning"] = "a strict rule: an instance of Claude must remain firm in a situation in which that instance faces seemingly compelling arguments to cross the lines drawn by the hard constraints"
    e["case_atoms"] = {"seemingly_compelling_argument_to_cross_line": "the instance of Claude faces seemingly compelling arguments to cross the lines drawn by the hard constraints in the situation"}
    e["where_the_text_is_silent"] = silence["firmness_required"]
    pts = {p["label"]: p["status"] for p in probe["points"]}
    assert pts["u0168.s01: the case holds"] == "SETTLED yes" and pts["u0168.s01: the case does not hold"] == "UNDECIDED"
    bp = {p["label"]: p["status"] for p in probe["binding_points"] if p["label"].startswith("u0168.s01")}
    assert list(bp.values()) == ["SETTLED yes", "UNDECIDED"], bp
    e["check"]["binding"] = bp
    e["check"]["meaning"] += "; the case is a pair of an instance and a situation: another instance of Claude in the same situation is UNDECIDED"
    e["note"] = e["note"].replace("the duty is on instances of Claude only.", "the duty is on instances of Claude only, and the case atom is binary on (instance, situation).") + " " + U168_REPAIR
    e["audit_repair"] += (" Rejected by the " + AUDIT_RUN + " audit (UNFAITHFUL: the guard took only the situation, so one instance facing an argument made every instance firm). Repaired in 20261021T0600Z: the open term is binary "
                          "on (claude_instance, situation) and the guard binds the acting instance.")
    e["repair_20261021T0600Z"] = "audit repair: the guard is binary on (claude_instance, situation); the English, the case atom, the silence sentence and the probe points are re-read from this run's document"
    e["changed_in_run"] = RUN_ID
    return [fr.UNIT, "u0168.s01", "u0013.presupposition", *DEMOTED]


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
    assert check["reading_plan"]["route"] == "enumerate" and len(check["reading_plan"]["choices"]) == 8   # 2 sets (u0156.s03: 4 candidates, u0165.s03: 2) after the two demotions (was 32)
    assert check["readings"]["conflict"]["status"] == "CONFLICT-FREE"
    assert coverage["coverage_percent"] == 100 and coverage["source_bytes"] == len(SOURCE)
    assert all(c["status"] == "CONFLICT-FREE" for c in check["readings"]["conflict"]["choices"])

    english = {"u0042.presupposition": block_after(render, "Claude’s three types of principals"),
               "u0043.s02.p2": block_after(render, "Claude’s three types of principals are Anthropic, operators, and users."),
               "u0286.presupposition": block_after(render, "Acknowledging open problems")}
    assert english["u0286.presupposition"] == "Checked reading: There is a thing that is unsolved.", english["u0286.presupposition"]
    assert "core_value_of" not in render and "core value of claude" not in render   # u0013 is UNFORMALISED again
    lines_ = render.split("\n")
    assert lines_[lines_.index("Claude’s core values") + 1] == "Recorded meaning: The passage is recorded as a passage without a formal reading yet, for this reason: other.discourse."
    for sentence_ in ("Claude should ask for clarification in cases of genuine ambiguity.", "in situations where Claude has explicitly been instructed not to engage in unintended exploits, it should comply."):
        assert any(ln.endswith(sentence_) and lines_[i + 1] == "Recorded meaning: The passage is recorded as a passage without a formal reading yet, for this reason: other.silence-display."
                   for i, ln in enumerate(lines_)), sentence_
    assert "genuine_helpfulness" not in render and "Some thing is helpful" not in render and "There is a thing that is helpful" not in render   # u0032 is UNFORMALISED again
    assert "classified as" not in english["u0042.presupposition"] + english["u0043.s02.p2"] and "principal type of Claude" in english["u0042.presupposition"]   # the audit repair: no quoted name
    english_u0245 = block_after(render, "Claude as a novel entity")
    assert english_u0245 == "Open reading: Claude is novel.", english_u0245

    # ---- the ledger: the ps-6r upgrade (u0013), the not-claimed expressible headings, the audit repair of u0032
    L.HEADINGS["u0235"] = [("possessive", "Claude’s", L4.CLAIM_U0235)]   # the audit of 20261019T1800Z: a singular possessive takes for granted existence and uniqueness
    frame_en, frame_rt = p17.frame_english(render, main_meta)
    frame_probe = json.load(open(RUN / "probes/frame-probe.json"))
    changed_edit = apply_repairs(ledger, eng, silence, silence_frame_all["system_prompt_deception_permitted"], probe, frame_probe, frame_en, frame_rt)
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
    stale_m4 = []
    for r in m4_src["units"]:
        e = entries[r["unit"]]
        if r["unit"] in DEMOTED:   # the unit is UNFORMALISED now: no act phrase, so the tag is stale (AP-0: write act_workaround_stale and say so)
            assert e["status"] == "UNFORMALISED" and e["act_workaround_stale"] is True and "act_workaround" not in e
            stale_m4.append({"unit": r["unit"], "was": r["act_workaround"], "bytes": e["span"][1] - e["span"][0], "reason": "the unit has no norm in the document any more (" + SILENCE_FEATURE + ")"})
            continue
        act_now = vocab_now[e["predicate"]]["regulated"]["act"]
        assert act_now == r["act"] == prev_vocab[e["predicate"]]["regulated"]["act"], (r["unit"], act_now, r["act"])
        e["act_workaround"] = r["act_workaround"]
    m4_units = [e["id"] for e in ledger if e.get("act_workaround") not in (None, "none")]
    m4 = {"units": len(m4_units), "bytes": sum(e["span"][1] - e["span"][0] for e in ledger if e["id"] in m4_units), "unit_ids": m4_units,
          "tally": dict(Counter(e["act_workaround"] for e in ledger if "act_workaround" in e)), "stale": stale_m4, "expected": {"units": 17, "bytes": 2502},
          "source": "research/act-phrases-p1: docs/research/evidence/act-phrases/m4-act-workaround.json (evidence/m4-act-workaround.json)"}
    assert (m4["units"], m4["bytes"]) == (17 - 2, 2502 - 68 - 115) and len(stale_m4) == 2, m4   # measured 17 units, 2,502 B in 20261012T1800Z..20261020T1800Z; the two demoted units are stale now

    # ---- PS-0p step 4: presupposition_triggers on every unit; the blocker; step 6: the goals
    census = json.load(open(RUN / "evidence/ps0p/ledger-triggers-constitution.json"))
    L.HEADING_CARRIER.pop("u0013", None)
    L.HEADING_CARRIER.update({"u0286": "assumed"})   # the heading whose claim is the unit's content now, as u0042 and u0245 (u0032 and, since this run, u0013 are unresolved)
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
        "u0245.presupposition": "a unit of the 18:00Z run (PS-0p class B, 26 B): its open term novel_entity is class judgment",
        "u0036.s05": "the unit is UNFORMALISED again in this run (audit repair, " + SILENCE_FEATURE + "): its open term genuine_ambiguity (class judgment in phase 1) is removed from the document with the unit's reading set, so the unit has no judgment term now"}
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
    lost_bytes = {"u0013.presupposition": 24, "u0036.s05": 68, "u0263.s04.p2": 115}
    assert claimed == pm["claimed_covered_bytes"] - sum(lost_bytes.values()) == 2951, claimed   # three claimed units leave the covered statuses; nothing else changes status
    n_old, old_units, _ = old.aggregate(ledger)
    spans = {e["id"]: e["span"] for e in ledger}
    status = {e["id"]: e["status"] for e in ledger}
    width = lambda ids_: sum(spans[i][1] - spans[i][0] for i in ids_)
    assert coverage["bytes_by_status"]["CHECKED"] == nb["CHECKED"] and coverage["bytes_by_status"]["OPEN"] == nb["OPEN"] + nb["READINGS"]
    assert coverage["bytes_by_status"]["LABELLED"] == nb["LABELLED"]

    changed_units = sorted(set(changed_edit), key=ids.index)
    LEDGER_NOTES = []
    PREV_RUN_LEDGER_NOTES = []   # the 20261020T0600Z ledger notes (u0095, u0002, u0235) were audited FAITHFUL by the audit of 20261020T1800Z; the 20261020T1800Z run changed nothing
    assert changed_units == sorted(["u0013.presupposition", "u0036.s05", "u0156.s03", "u0168.s01", "u0263.s04.p2"], key=ids.index), changed_units
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
    assert nd["all"]["conflict"] == "CONFLICT-FREE" and nd["all"]["premises"] == "model" and nd["all"]["choice_count"] == 8
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
    # run 20261021T0600Z: u0165.s01 "knowing" and "belief" are ALL with a certificate again (they were ALL at 20261018T1800Z, UNKNOWN at both runs of 20261019 and at 20261020T0600Z/1800Z: a search-budget effect). The
    # document is smaller now (2 reading sets and 8 choices instead of 4 and 32); the other 19 queries have the previous verdict, route and evidence. Not a language change: nothing under ve/ lean/VE/Service rust/ changed.
    assert hard_changes == [{"unit": "u0165.s01", "kind": "knowing", "now": ["ALL", "certificate"], "before": ["UNKNOWN", None]},
                            {"unit": "u0165.s01", "kind": "belief", "now": ["ALL", "certificate"], "before": ["UNKNOWN", None]}], hard_changes
    hard_same = slim(hard_q) == slim(prev_hard)
    assert not hard_same and all(hard_by[(u_, k)]["verdict"] == "ALL" for u_ in HC_UNITS for k in ("knowing", "belief"))
    unavailable = sorted(f"{q['unit']}:{q['kind']}" for q in hard_q if "rerun_alone" in q or q.get("cap"))
    hard_summary = {k: dict(Counter(q["verdict"] for q in hard_q if q["kind"] == k)) for k in ("knowing", "belief", "neither")}
    probe_names = ("risk-probe", "s1-probe", "senses-probe", "senses-document-probe", "rights-reading-probe", "unspecified-probe", "frame-probe")
    probe_same = {n: (RUN / f"probes/{n}.json").read_bytes() == (PREV_DIR / f"probes/{n}.json").read_bytes() for n in probe_names}
    # risk-probe: probe_risk.py lost its Python gate mirror (ar-10a); the cases must be identical, only the profile-gate rows may differ
    risk_now, risk_prev = json.load(open(RUN / "probes/risk-probe.json")), json.load(open(PREV_DIR / "probes/risk-probe.json"))
    risk_cases_same = {k: v for k, v in risk_now.items() if k != "profile_gate"} == {k: v for k, v in risk_prev.items() if k != "profile_gate"}
    risk_gate_diff = {k: {"before": risk_prev["profile_gate"][k], "now": risk_now["profile_gate"][k]} for k in risk_now["profile_gate"] if risk_now["profile_gate"][k] != risk_prev["profile_gate"][k]}
    assert risk_cases_same and risk_gate_diff == {}, (risk_cases_same, risk_gate_diff)   # the previous run already read Lean's gate
    # the two probes the repairs change by design: unspecified-probe (the two u0036.s05 points and the two gap lines of the removed predicates go; two u0168.s01 binding points are added) and frame-probe (three binding points are added)
    assert {k for k, v in probe_same.items() if not v} == {"unspecified-probe", "frame-probe"}, probe_same
    up_now, up_prev = json.load(open(RUN / "probes/unspecified-probe.json")), json.load(open(PREV_DIR / "probes/unspecified-probe.json"))
    gone_labels = {"u0036.s05: genuine ambiguity", "u0036.s05: no genuine ambiguity"}
    removed_preds = {"clarification_required", "exploit_instruction_compliance_required"}   # the `differs` lists name every regulated predicate that the point leaves unsaid; the two removed ones drop out
    norm_pt = lambda p: {**p, "differs": [d for d in (p.get("differs") or []) if d["predicate"] not in removed_preds]}
    assert [norm_pt(p) for p in up_prev["points"] if p["label"] not in gone_labels] == [norm_pt(p) for p in up_now["points"]] and [norm_pt(p) for p in up_prev["scope_points"]] == [norm_pt(p) for p in up_now["scope_points"]]
    assert [norm_pt(p) for p in up_prev["binding_points"]] == [norm_pt(p) for p in up_now["binding_points"][:len(up_prev["binding_points"])]] and len(up_now["binding_points"]) == len(up_prev["binding_points"]) + 2
    assert up_prev["conflict"] == up_now["conflict"] and {k: v for k, v in up_prev["gaps"].items() if k not in ("clarification_required", "exploit_instruction_compliance_required")} == up_now["gaps"]
    fp_now, fp_prev = json.load(open(RUN / "probes/frame-probe.json")), json.load(open(PREV_DIR / "probes/frame-probe.json"))
    assert fp_now["points"] == fp_prev["points"] and [p["status"] for p in fp_now["binding_points"]] == ["SETTLED no", "UNDECIDED", "UNDECIDED"]
    unspecified_changes = {"points_removed": sorted(gone_labels), "gap_lines_removed": ["clarification_required", "exploit_instruction_compliance_required"],
                           "binding_points_added": [p["label"] + ": " + p["status"] for p in up_now["binding_points"][len(up_prev["binding_points"]):]]}
    frame_changes = {"binding_points_added": [p["label"] + ": " + p["status"] for p in fp_now["binding_points"]]}
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
    assert [cq[k]["verdict"] for k in cq] == ["ALL", "ALL"] and lds["decided_units"] == summ["decided_units"] and lds["decided_units"] == ["u0156.s03", "u0165.s03"] and lds["decided_bytes"] == 189
    companion_probe = {**pm["companion_probe"], "components": summ["components"], "conflict": summ["conflict"], "premises": summ["premises"],
                       "premises_components": summ["premises_components"], "separations": summ["separations"], "decided_units": len(lds["decided_units"]), "decided_bytes": lds["decided_bytes"],
                       "decided_share_percent": lds["decided_share_percent"],
                       "queries": {k: {"verdict": cq[k]["verdict"], "route": cq[k]["route"], "component": cq[k]["component"], "sentence": cq[k]["sentence"],
                                       "decided_units": len(cq[k]["decided_units"]), "english": cq[k].get("english", [])} for k in cq},
                       "decided_units_same_as_previous_run": False,
                       "reading": ("changed by the repairs of this run: the reading sets of u0036.s05 and u0263.s04.p2 are gone, so 2 units are Lean-decided (189 B, 0.10%) where 4 were (372 B, 0.20%). "
                                   "The main component's premise check is UNKNOWN on the components route, as in the three runs before (it has been UNKNOWN since QT-0p's principal_type of size 3 entered the document on "
                                   "20261018T1800Z; the repair of QT-0p's wording did not restore it); u0013.presupposition is no longer in that component. The translation's own premise check, on the superposed route, stays `model`. "
                                   "A measurement document, not the translation. The component also holds the claimed unit u0286 (it is not Lean-decided)"),
                       "premise_regression": {"measured_in": "20261018T1800Z, with QT-0p's predicate wording; not re-attributed in this run", "results": attribution["results"]},
                       "decided_units_ids": lds["decided_units"]}
    lean_decided_share = {**pm["lean_decided_share"], "with_companion_sets": {**pm["lean_decided_share"]["with_companion_sets"], "decided_units": len(lds["decided_units"]),
                          "decided_bytes": lds["decided_bytes"], "decided_share_percent": lds["decided_share_percent"], "units": lds["decided_units"],
                          "previous_run": {"decided_units": 4, "decided_bytes": 372, "decided_share_percent": "0.20"}, "same_as_previous_run": False, "earlier_run_20261018T0600Z": {"decided_units": 19, "decided_bytes": 2602, "decided_share_percent": "1.41"},
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
    ask_same = all(strip_version(json.load(open(RUN / f"probes/ask/q{i}{s}.json"))) == strip_version(json.load(open(prev_ask / f"q{i}{s}.json"))) for i in (1, 3) for s in ("", ".answer"))   # q1 and q3 are the previous run's questions
    asks_now = [json.load(open(RUN / f"probes/ask/q{i}.json")) for i in range(1, 6)]
    asks_ans = [json.load(open(RUN / f"probes/ask/q{i}.answer.json")) for i in range(1, 6)]
    ask_questions_now = [(RUN / f"probes/ask/q{i}.question.txt").read_text().strip() for i in range(1, 6)]
    assert all(a["answer"] == "no_answer" and a["result"]["code"] == "NoDerivation" for a in asks_now + asks_ans)
    assert not any(w in json.dumps(asks_now + asks_ans + ask_questions_now) for w in ("genuine_ambiguity", "seek clarification", "exploit"))
    nd_conclusions_same = all(sent(json.load(open(RUN / f"probes/nd/{f}.json"))) == sent(json.load(open(PREV_DIR / f"probes/nd/{f}.json"))) for f in ("conclusion-no-denial-result", "claim-human-result"))
    nd_verdicts_same = all({k: v for k, v in json.load(open(RUN / f"probes/nd/{f}.json")).items() if k != "english"} == {k: v for k, v in json.load(open(PREV_DIR / f"probes/nd/{f}.json")).items() if k != "english"}
                           for f in ("conclusion-no-denial-result", "claim-human-result")) if True else False
    assert nd_verdicts_same
    qt_probe = json.load(open(RUN / "probes/qt/no-fourth-result.json"))
    assert qt_probe["verdict"] == "ALL" and qt_probe["evidence"] == "certificate", qt_probe["verdict"]
    qt_fourth = json.load(open(RUN / "probes/qt/fourth-result.json"))

    open_terms = [{k: t[k] for k in ("name", "arguments", "decided_by", "necessary", "sufficient", "factors")} for t in main_meta["open_terms"]]
    prev_terms = {t["name"]: t for t in pm["open_terms"]}
    now_terms = {t["name"]: t for t in open_terms}
    added_terms = sorted(set(now_terms) - set(prev_terms))
    removed_terms = sorted(set(prev_terms) - set(now_terms))
    changed_terms = sorted(n for n in now_terms if n in prev_terms and now_terms[n] != prev_terms[n])
    assert (added_terms, removed_terms, changed_terms) == ([], ["exception_to_asking_for_clarification", "exception_to_complying_with_exploit_instruction", "genuine_ambiguity"],
                                                          ["asked_to_keep_system_prompt_confidential", "seemingly_compelling_argument_to_cross_line"]), (added_terms, removed_terms, changed_terms)
    changed_terms_detail = {"seemingly_compelling_argument_to_cross_line": {"arguments": [prev_terms["seemingly_compelling_argument_to_cross_line"]["arguments"], now_terms["seemingly_compelling_argument_to_cross_line"]["arguments"]]},
                            "asked_to_keep_system_prompt_confidential": {"arguments": [prev_terms["asked_to_keep_system_prompt_confidential"]["arguments"], now_terms["asked_to_keep_system_prompt_confidential"]["arguments"]],
                                                                        "factors_added": [f for f in now_terms["asked_to_keep_system_prompt_confidential"]["factors"] if f not in prev_terms["asked_to_keep_system_prompt_confidential"]["factors"]]}}
    gap_marker = "Here the text does not say whether"
    sep_lines = lambda text: [ln for ln in text.splitlines() if ln.startswith("These two readings differ here")]
    gaps_now = [ln.count(gap_marker) for ln in sep_lines(render)]
    cannot_show = lambda text: text.count("These two readings differ in a checked situation that VE cannot yet show in words.")
    assert gaps_now == [] and cannot_show(render) == 7 == cannot_show(old_render) and len(sep_lines(old_render)) == 2   # the two "differ here" lines of the previous run were the sets of u0036.s05 and u0263.s04.p2

    # ---- X3: the checkpoint evidence of the final document
    cp = json.load(open(RUN / "evidence/checkpoint-final.json"))
    assert cp["document_check"]["premises"] == "model" and not cp["x3_vocabulary"]["existing_predicate_wordings_changed"]

    # ---- the language changes since the previous tag: read from the repository
    diff_all = git("diff", "--shortstat", f"{PREV_TAG}..{TAG}")
    diff_stat = git("diff", "--shortstat", f"{PREV_TAG}..{TAG}", "--", "ve", "lean", "rust", "conformance")
    merged_all = git("log", "--first-parent", "--format=%h %s", f"{PREV_TAG}..{TAG}").splitlines()
    merged = [ln for ln in merged_all if "Merge feature/" in ln]
    assert [ln.split("Merge feature/")[1].split(" ")[0] for ln in merged] == ["sc-1ad", "df-1ac", "et-3cb", "me-6b", "ap-1c"], merged
    other_first_parent = [ln for ln in merged_all if ln not in merged]   # README and planning commits of main that came with the sync

    missing_now = old.tally(ledger)
    lo_names = list(pm["ledger_only_open_terms"]["names"])
    assert lo_names == ["appropriate_oversight", "broad_safety", "ethical_harm", "genuine_helpfulness"], lo_names
    lo_entries = [e for e in ledger if set(e.get("open_terms") or []) & set(lo_names)]
    ledger_only = {**pm["ledger_only_open_terms"], "names": lo_names, "entries": len(lo_entries), "statuses": dict(Counter(e["status"] for e in lo_entries)),
                   "covered_entries_with_such_names": [e["id"] for e in lo_entries if e["status"] in COVERED]}
    assert ledger_only["covered_entries_with_such_names"] == []

    # ---- new this tag: do the profiles whose Lean modules landed (scope@0: sc-1ab/sc-1ac, defaults@0: df-1ab, calc@0: me-9; acts@0: ap-1a, judgments@0: jt-1b earlier) reach a document?
    new_profiles = json.load(open(RUN / "evidence/new-profile-probe.json")) if os.environ.get("FINISH_CACHE") == "1" and (RUN / "evidence/new-profile-probe.json").exists() else probe_new_profiles()
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
    english_round_trip_same = all(rt_now.get(r) == v for r, v in rt_prev.items() if r not in ("clarify-ambiguity", "comply-no-exploit-instruction"))

    audit_note = ("The audit of run 20261020T1800Z (AUDIT-20261020T1800Z-received.md: 17 of 20 sampled and 11 of 12 supplementary verdicts faithful, four unfaithful: u0013.presupposition, u0036.s05, u0156.s03, u0168.s01) is the latest received; "
                  "the audits of 20261019T1800Z and earlier are in the AUDIT-*-received.md files. The four unfaithful units are repaired in this run (changed_units); none keeps a covered status without a repair")
    # ---- values recomputed from this run's documents (the regulated predicates, the probe, the rules' English)
    strict_now = front_matter(STRICT)
    reg_now = {n: {"role": p["regulated"]["role"], "default": p["regulated"]["default"], "arguments": p["arguments"]}
               for n, p in strict_now["environment"]["vocabulary"]["predicates"].items() if "regulated" in p}
    assert reg_now == {n: v for n, v in pm["regulated_predicates"].items() if n in reg_now} and set(pm["regulated_predicates"]) - set(reg_now) == {"clarification_required", "exploit_instruction_compliance_required"}
    nd_parties = sorted({r["arguments"][0] for r in reg_now.values()})
    assert nd_parties == pm["no_invented_permissions"]["first_arguments_of_regulated_predicates"]
    points_now = probe["points"]
    undecided_points = sum(1 for p in points_now if p["status"] == "UNDECIDED")
    settled_points = sum(1 for p in points_now if p["status"].startswith("SETTLED"))
    assert not any(p["status"].startswith("CONFLICT") for p in points_now)
    rt_hc = {r: {"round_trip": v["round_trip"], "error": v["error"]} for r, v in eng.items() if r.startswith("hc-")}
    rt_other = sorted(r for r, v in eng.items() if not r.startswith("hc-") and v["round_trip"])
    assert rt_hc == pm["english_round_trip"]["hard_constraint_rules"] and set(pm["english_round_trip"]["other_rules_round_trip"]) - set(rt_other) == {"clarify-ambiguity", "comply-no-exploit-instruction"} and not set(rt_other) - set(pm["english_round_trip"]["other_rules_round_trip"])
    reading_sets_now = front_matter(MAIN)["reading_sets"]
    m = copy.deepcopy(pm)
    for stale in ("feature_upgrade_counts_separate_from_repairs", "changed_units_by_role", "audit_repairs", "changed_units_detail", "feature_upgrades", "claimed_covered_bytes_gained_by_plan",
                  "claimed_covered_bytes_gained_by_feature", "claimed_covered_bytes_lost_by_audit_repair", "claimed_covered_bytes_gained_detail", "audit_rejected_units_and_repair_status",
                  "audit_verified_newly_from_20261017T0600Z", "audit_verified_newly_labelled_from_20261017T0600Z", "audit_verified_newly_from_20261017T1800Z", "audit_verified_newly_labelled_from_20261017T1800Z",
                  "audit_verified_newly_from_20261018T0600Z", "audit_verified_newly_labelled_from_20261018T0600Z", "audit_verified_newly_from_20261018T1800Z", "audit_verified_newly_labelled_from_20261018T1800Z",
                  "audit_verified_newly_from_20261019T0600Z", "audit_verified_newly_labelled_from_20261019T0600Z", "audit_verified_newly_from_20261019T1800Z", "audit_verified_newly_labelled_from_20261019T1800Z", "plan_repairs_carried_from_20261019T0600Z", "plan_repair_note", "open_terms_count_note",
                  "repaired_bytes_not_audit_verified", "claimed_but_not_audit_verified_units"):
        m.pop(stale, None)
    m.update({
        "run": RUN_ID, "baseline_tag": TAG, "previous_run": PREV_RUN, "previous_baseline_tag": PREV_TAG,
        "history_note": "this file records this run; the earlier runs' records are in prev/metrics.json and the AUDIT-*-received.md files",
        "feature_upgrade_counts_separate_from_repairs": (
            "units upgraded by new features 0 (+0 B), reading sets upgraded by new features 0: none of the five batches merged since ve-green-sc-1ac (ap-1c, me-6b, et-3cb, df-1ac, sc-1ad) lets a document say something new (FEATURE-REVIEW.md). "
            "Plan repairs of this run: 1 unit, 0 B gained and 24 B lost (u0013.presupposition: PS-0p step 3 says not to claim it). Audit repairs: 4 units rejected by the audit of 20261020T1800Z (u0013.presupposition, u0036.s05, u0156.s03, u0168.s01) and one more "
            "unit of the same cause (u0263.s04.p2): u0156.s03 and u0168.s01 are repaired in place (still READINGS and OPEN), u0013.presupposition, u0036.s05 and u0263.s04.p2 go back to UNFORMALISED (207 B no longer claimed). Ledger-note-only changes: 0. "
            "Changed units: 5. The translation document is not the previous run's: the differences are the audit repairs, none of them a feature of the language"),
        "changed_units": changed_units,
        "changed_units_by_role": {"feature_upgrade": [], "plan_repair": ["u0013.presupposition"], "audit_repair_of_a_covered_unit": ["u0156.s03", "u0168.s01", "u0036.s05", "u0013.presupposition"],
                                  "audit_repair_same_cause_not_sampled": ["u0263.s04.p2"], "ledger_note_only": []},
        "changed_units_previous_run_not_yet_audited": {"run": PREV_RUN, "units": PREV_RUN_LEDGER_NOTES, "what": "none: the previous run (20261020T1800Z) changed no unit and has been audited (AUDIT-20261020T1800Z-received.md); the 20261020T0600Z ledger notes (u0095, u0002, u0235) were audited FAITHFUL by it"},
        "plan_repairs": [{"unit": "u0013.presupposition", "plan": "presupposition", "item": "PS-0p"}],
        "plan_repairs_note": ("one plan repair this run: u0013.presupposition goes back to UNFORMALISED because the prompt's PS-0p step 3 says u0013, u0095, u0002 and u0235 are not claimed (the previous run kept u0013 CHECKED and reported the tension twice; the audit of 20261020T1800Z rejected the claim for exactly that reason, so the instruction is followed now). "
                              "The other sections (JT-0p, QT-0p, AT-0p, SC-M0, AP-0 item 3, DRI X2 to X5) are the ones already applied on 18 October and are re-verified, not re-applied; their state is in plan_repair_AT0p_state, quantities_qt0p, presupposition_ps0p, scope_tally, act_workaround_m4, open_term_class and vocabulary_change_check"),
        "plan_repairs_carried": {"AT-0p (attitudes)": HC_UNITS, "QT-0p (quantities)": ["u0042.presupposition", "u0043.s02.p1", "u0043.s02.p2"], "PS-0p (presupposition)": pm["plan_repairs_carried_from_20261019T0600Z"]["changed_units_of_the_previous_run"]
                                 if "plan_repairs_carried_from_20261019T0600Z" in pm else "see prev/metrics.json"},
        "audit_repairs": [
            {"unit": "u0168.s01", "audit": AUDIT_RUN, "verdict": "UNFAITHFUL", "cause": "the guard took only the situation", "repair": "the open term is binary on (claude_instance, situation); the guard binds the acting instance", "still": "OPEN", "bytes": 96, "audit_verified": False},
            {"unit": "u0156.s03", "audit": AUDIT_RUN, "verdict": "UNFAITHFUL", "cause": "the frame term took only the instance", "repair": "the frame term is binary on (claude_instance, user); the situation is the conversation of that pair (a third argument is impossible)", "still": "READINGS", "bytes": 100, "audit_verified": False},
            {"unit": "u0036.s05", "audit": AUDIT_RUN, "verdict": "UNFAITHFUL", "cause": "the rendering words the defeasible candidate's silence as “c is not required to” (ve/readings_english.py, not the translator's)", "repair": "back to UNFORMALISED (" + SILENCE_FEATURE + "); set, predicates, terms and situations removed", "still": "UNFORMALISED", "bytes": 68},
            {"unit": "u0013.presupposition", "audit": AUDIT_RUN, "verdict": "UNFAITHFUL", "cause": "the claim violates PS-0p step 3 of the prompt", "repair": "back to UNFORMALISED (other:discourse); predicate and fence removed", "still": "UNFORMALISED", "bytes": 24},
            {"unit": "u0263.s04.p2", "audit": AUDIT_RUN, "verdict": "same cause as u0036.s05, not sampled", "cause": "same candidate shape and same rendering sentence", "repair": "back to UNFORMALISED (" + SILENCE_FEATURE + ")", "still": "UNFORMALISED", "bytes": 115}],
        "audit_faults_listed_on_unclaimed_units": {
            "audit": AUDIT_RUN, "verdicts": "u0002.presupposition, u0095.presupposition, u0235.presupposition, u0286, u0245, u0055 and the other unclaimed units it sampled: FAITHFUL",
            "state": "the 20261020T0600Z repairs of u0235 (existence and uniqueness), u0002 and u0095 (the owner is the company constant, not the principal type) were audited FAITHFUL and are carried unchanged; u0013.presupposition is unclaimed now (its lower-case constant `claude` is moot until it is claimed again)",
            "evidence": "evidence/owner-probe.json (owner_probe.py), re-run in this run: the fences of u0095, u0002 and u0235 still parse, render and round-trip; they are not added to the document"},
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
        "claimed_covered_bytes_gained_by_feature": {}, "claimed_covered_bytes_gained_by_plan": {},
        "claimed_covered_bytes_lost_by_plan": {"u0013.presupposition": 24},
        "claimed_covered_bytes_lost_by_audit_repair": {"u0013.presupposition": 24, "u0036.s05": 68, "u0263.s04.p2": 115, "note": "u0013.presupposition's 24 B are counted under both the audit and the plan (PS-0p step 3); the total lost is 207 B"},
        "claimed_false_units": claimed_false,
        "substantive_covered_bytes": nb["CHECKED"] + nb["OPEN"] + nb["READINGS"], "substantive_covered_bytes_previous_run": pm["substantive_covered_bytes"],
        "audit_verified_covered_bytes": verified_bytes, "audit_verified_covered_percent": round(100 * verified_bytes / len(SOURCE), 4),
        "audit_verified_covered_units": verified, "audit_verified_covered_bytes_previous_run": pm["audit_verified_covered_bytes"],
        "audit_verified_dropped_because_changed": [i for i in pm["audit_verified_covered_units"] if i in changed_units],
        "audit_verified_newly_this_run": newly,
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND unchanged in this run from the form that audit saw. " + audit_note + ". The two repaired units that keep a covered status (u0156.s03, 100 B, and u0168.s01, 96 B) are changed units, "
            "so they are claimed but not audit-verified until the next audit; every other claimed byte is the form an audit saw. This is a count of verdicts on unchanged text, not a fresh audit of this run."),
        "audit_verified_metadata_bytes": verified_meta, "audit_verified_metadata_percent": round(100 * verified_meta / len(SOURCE), 4),
        "audit_verified_metadata_bytes_previous_run": pm["audit_verified_metadata_bytes"],
        "claimed_but_not_audit_verified_bytes": claimed - verified_bytes - verified_meta,
        "claimed_but_not_audit_verified_units": [e["id"] for e in ledger if e["status"] in COVERED and e.get("claimed", True) is not False and e["id"] not in verified and e["id"] not in verified_lab],
        "audit_rejected_units_and_repair_status": {
            "rejected_by_latest_audit": AUDIT_REJECTED, "latest_audit": AUDIT_RUN, "kept_covered_status_without_repair": [],
            "repair": {"u0168.s01": "repaired in place (binary term, guard binds the instance); OPEN, claimed, not audit-verified", "u0156.s03": "repaired in place (binary frame term); READINGS, claimed, not audit-verified",
                       "u0036.s05": "UNFORMALISED (" + SILENCE_FEATURE + "); not claimed", "u0013.presupposition": "UNFORMALISED (other:discourse); not claimed", "u0263.s04.p2": "same cause as u0036.s05, not sampled: UNFORMALISED (" + SILENCE_FEATURE + "); not claimed"},
            "earlier": {"rejected_by_20261019T0600Z_audit": ["u0032.presupposition"], "repair_done_in_20261019T1800Z": "reverted to UNFORMALISED (other:discourse), 38 B not claimed; confirmed by the 20261019T1800Z audit (u0032.presupposition FAITHFUL as unclaimed)"},
            "small_faults_not_repaired": {
                "principal type of Claude": "can also be read as “main type of Claude” (carried; the sort noun is what removed the quoted-name fallback)",
                "u0173.s01 to s04": pm["audit_rejected_units_and_repair_status"]["small_faults_not_repaired"]["u0173.s01 to s04"]}},
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
            "note": "one run each on a shared 32-core machine (other sessions were running; not a controlled comparison)",
            "document_check_seconds": timing["document_check"], "document_check_seconds_previous_run": pm["timing_single_runs"]["document_check_seconds"],
            "document_coverage_seconds": timing["document_coverage"], "document_coverage_seconds_previous_run": pm["timing_single_runs"]["document_coverage_seconds"],
            "nd_all_load_seconds": [nd["all"]["load_seconds"], pm["timing_single_runs"]["nd_all_load_seconds"][0]],
            "nd_all_check_seconds": [nd["all"]["check_seconds"], pm["timing_single_runs"]["nd_all_check_seconds"][0]],
            "nd_all_separation_search_seconds": [nd["all"]["separation_search_seconds"], pm["timing_single_runs"]["nd_all_separation_search_seconds"][0]],
            "build_note": "lean/.lake and rust/target copied (cp -a) from the ve-integration checkout at the identical commit (68f18dcdc); `lake build` completed (1058 jobs, about 25 minutes: the copy's paths differ, so it rebuilt) and the Rust binary "
                          "is the pin in lean/checkers.lock (SHA-256 6422647f…8579, `tools/rust_build.py --check`); not a language measurement",
            "order": "[this run, previous run]; this run has two reading sets (8 choices), the previous four (32)"},
        "unspecified_probe": {"file": "probes/unspecified-probe.json", "document": "readings/all-strict.ve.md", "points_asked": len(points_now), "undecided": undecided_points, "settled": settled_points,
                              "conflict": 0, "conflict_reports": probe["conflict"], "gaps": {p: g["reached"] for p, g in probe["gaps"].items()},
                              "hard_constraint_points": {p["label"]: p["status"] for p in points_now if p["label"].startswith("u0165")},
                              "scope_points": {p["label"]: p["status"] for p in probe["scope_points"]}, "binding_points": {p["label"]: p["status"] for p in probe["binding_points"]},
                              "reading": (pm["unspecified_probe"]["reading"] + " Run 20261021T0600Z (audit repairs): the two points of u0036.s05 and the two gap lines of the removed obligations are gone with the units; the binding points gain two for u0168.s01 "
                                          "(two instances of Claude in one situation: the instance that faces the seemingly compelling argument is SETTLED yes, the other is UNDECIDED), which is what the repaired guard says."),
                              "non_hard_constraint_points_same_as_previous_run": "yes, except the two removed points of u0036.s05 (every other point has the previous run's status)",
                              "conflict_checks_same_as_previous_run": probe["conflict"] == up_prev["conflict"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["unspecified-probe"],
                              "changes_against_previous_run": unspecified_changes},
        "profile_combination_probe_same_as_previous_run": True,
        "senses_probe": {**pm["senses_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-probe"]},
        "senses_document_probe": {**pm["senses_document_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["senses-document-probe"]},
        "discourse_probe": {**pm["discourse_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": disc_same},
        "rights_reading_probe": {**pm["rights_reading_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["rights-reading-probe"]},
        "risk_probe": {**pm["risk_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["risk-probe"], "cases_identical_to_previous_run": risk_cases_same,
                       "profile_gate_differences": risk_gate_diff,
                       "why_earlier": ("ar-10a deleted the Python gate mirror `checker_family` that probe_risk.py imported; the script now builds the environment and lets Lean's gate (VE.Compose.gateOf) answer, "
                               "so the one accepted row no longer names a “checker family”, and rows with `rights@0` are refused as an unregistered environment profile first (ar-10a DELTA item 1, fault order). "
                               "Every risk case (outcome of the 14 elaborations) is identical; in this run the whole file is byte-identical to the previous run's")},
        "readings_defaults_probe": {**pm["readings_defaults_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": probe_same["s1-probe"]},
        "carried_probes_note": ("the carried probes were re-run on the final document: byte-identical JSON for " + ", ".join(k for k, v in probe_same.items() if v) +
                                "; unspecified-probe and frame-probe differ by design (the audit repairs: " + json.dumps(unspecified_changes) + "; " + json.dumps(frame_changes) + "); discourse " + ("byte-identical" if disc_same else "differs (see probes/discourse-probe.json)") + "; companion: " +
                                ("identical to the previous run's after the run identifiers are normalised" if comp_same else "differs as expected (2 Lean-decided units, 189 B, where 4 were: the two removed sets)") + "; the 21 hard-constraint queries give " +
                                json.dumps(hard_summary) + (", every verdict equal to the previous run's" if not hard_changes else ", changes: " + json.dumps(hard_changes) + " (a search-budget effect on a smaller document, not a language change)") +
                                "; the denial, claim-to-be-human and no-fourth-type conclusion queries are ALL, the positive fourth-type query UNKNOWN as before; the five `ve ask` questions give no answer (questions 2, 4 and 5 are new: the old ones asked about the clarification unit); the probe_s1 and probe_rights inputs are documents of earlier runs (readings/s1.ve.md and all-default.ve.md of 20261008T1800Z, evidence/pre-qt0p-translation-without-content.ve.md), as in the previous run, so their results do not depend on this translation"),
        "frame_probe": {**{k: v for k, v in pm["frame_probe"].items() if k != "reading"}, "binding_points": frame_probe["binding_points"], "identical_to_previous_run": probe_same["frame-probe"], "points_identical_to_previous_run": True,
                        "changes_against_previous_run": frame_changes,
                        "reading": (pm["frame_probe"]["reading"] + ". Binding points (audit 20261020T1800Z): the frame term binds the instance and the user; with two instances and two users and the frame holding for (instance0, user0), the rule is SETTLED no for that pair and "
                                    "UNDECIDED for instance0 toward user1 and for instance1 toward user0")},
        "companion_probe": companion_probe, "lean_decided_share": lean_decided_share,
        "profile_combination_probe_changes": {"what": pm["profile_combination_probe_changes"]["what"], "changed": {}, "reading": "all thirteen rows are identical to the previous run's"},
        "new_profiles_probe": {"what": "the profiles whose Lean modules exist, `scope@0` (sc-1ab, sc-1ac, sc-1ad), `defaults@0` (df-1ab, df-1ac), `calc@0` (me-9, me-6b), `acts@0` (ap-1a, ap-1c), `judgments@0` (jt-1b), added to the strict companion's environment, then `ve document check`", "result": new_profiles,
                               "reading": "all five are refused as unsupported profiles, again at this tag: no document can use them yet (sc-1ad DELTA: the changed definitions reach no caller until the document mode SC-1b; df-1ac: the wire exists, the kind-table row is df-1ad's; me-6b: no service mode; ap-1c: theorems only, ap-1b opens acts; jt-1b: JT-2). So no unit of the constitution can use cross-sentence scope, defeasible defaults, algebra and units, lexical acts or judgment terms at this tag"},
        "soft_chain_probe": {**prev_soft, "result": {**prev_soft["result"],
                                                     "ve_document_check": {**prev_soft["result"]["ve_document_check"], "stderr_last_lines": soft["check"]["stderr_last_lines"]},
                                                     "ve_document_coverage": soft["coverage"], "ve_document_render": soft["render"],
                                                     "ve_document_readings_denial_query": soft["conclusions"]["denial"], "ve_document_readings_claim_human_query": soft["conclusions"]["claim_human"]},
                             "same_outcome_as_previous_run": soft_same,
                             "decision": "still not adopted: `ve document check` raises the same UnsupportedProfile on the soft-chain document, so the exception_to_* workaround stays (not an upgrade)"},
        "separation_line_gap_sentences": {"what": pm["separation_line_gap_sentences"]["what"], "per_line_before": [1, 1], "per_line_now": gaps_now,
                                          "reading": "the two 'differ here' lines of the previous run belonged to the sets of u0036.s05 and u0263.s04.p2; those sets are gone (" + SILENCE_FEATURE + "), so no set of the document shows a situation in words any more; the 7 'cannot yet show in words' lines are the same (six pairs of u0156.s03's four candidates, one for u0165.s03)",
                                          "source": pm["separation_line_gap_sentences"]["source"]},
        "reading_sets": {"count": len(reading_sets_now), "unresolved": len(reading_sets_now), "count_previous_run": 4, "units": [rs["unit"] for rs in reading_sets_now],
                         "candidates": {rs["unit"]: [r["id"] for r in rs["readings"]] for rs in reading_sets_now}, "couplings": [], "narrowings": [], "choices": len(check["reading_plan"]["choices"]), "choices_previous_run": 32,
                         "removed_this_run": {"u0036.s05": "force-u0036-s05 (strict, default): the unit is UNFORMALISED (" + SILENCE_FEATURE + ")", "u0263.s04.p2": "force-u0263-s04-p2 (strict, default): the unit is UNFORMALISED (" + SILENCE_FEATURE + ")"},
                         "added_this_run": {}, "changed_this_run": {"u0156.s03": "the frame term of the two in-frame candidates is binary on (claude_instance, user)"},
                         "note": pm["reading_sets"]["note"],
                         "readings_from_the_words": {**{k: v for k, v in pm["reading_sets"]["readings_from_the_words"].items() if k != "force_sets_kept_because_of_the_word_should"},
                                                     "force_sets_removed_in_20261021T0600Z": {"units": ["u0036.s05", "u0263.s04.p2"], "spans": ["u0253.s04", "u0011.s01"],
                                                                                             "note": "the words “should ask” and “it should comply” still admit a strict and a defeasible duty; no set is kept because the rendering of such a set words silence as “not required” (" + SILENCE_FEATURE + ")"}}},
        "checked_content_main_chain": {**pm["checked_content_main_chain"], "documents": nd, "candidate_premise_status": dict(cand_status),
                                       "choices_checked": nd["all"]["choices_checked"],
                                       "choices_conflict_free": nd["all"]["conflict_by_choice"].get("CONFLICT-FREE", 0), "choices_conflict": nd["all"]["conflict_by_choice"].get("CONFLICT", 0),
                                       "separating_situations_checked_by_lean": sep_all, "separated_by_decision_only_findings": 0},
        "question_probe": {**pm["question_probe"], "re_run_at_this_tag": True, "identical_to_previous_run": "in content: `no_answer` for all five with --reading and without it" if ask_same else "DIFFERS"},
        "conclusion_queries_note": "the denial and claim-to-be-human queries (probes/nd/*-result.json) were re-run: ALL on the superposed route with a certificate" + (", the same verdict, route and evidence as the previous run's; the English differs only in the number of open sentences (2 where there were 4: the reading sets of u0036.s05 and u0263.s04.p2 are gone)" if nd_verdicts_same else ""),
        "scope_tally": {"file": "scope-tally.json", "totals": tally["totals"], "not_tallied": tally["not_tallied"]},
        "act_workaround_m4": m4,
        "heading_presuppositions_exposed": sum(1 for e in ledger if "presupposed_claim" in e),
        "heading_presuppositions_exposed_previous_run": pm["heading_presuppositions_exposed"],
        "english_round_trip": {"hard_constraint_rules": rt_hc, "other_rules_round_trip": rt_other, "reading": pm["english_round_trip"]["reading"], "re_measured_this_run": True, "same_as_previous_run": english_round_trip_same,
                               "removed_with_the_demoted_units": ["clarify-ambiguity", "comply-no-exploit-instruction"]},
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
    # ---- carried fields recomputed for this run's documents
    m["regulated_predicates"] = reg_now
    m["no_invented_permissions"] = {**pm["no_invented_permissions"], "regulated_predicates": len(reg_now), "permission_predicates": sorted(n for n, r in reg_now.items() if r["role"] == "permission"),
                                    "obligation_predicates": sorted(n for n, r in reg_now.items() if r["role"] == "obligation"), "first_arguments_of_regulated_predicates": nd_parties}
    assert m["no_invented_permissions"]["predicates_with_default_allow"] == 0 and m["no_invented_permissions"]["completions"] == ["unspecified"]
    m["silence_sentences_as_used_in_ledger"] = dict(silence)
    m["legend_sentences"] = legend
    m["conflicts"] = {"reported_by_VE": 0, "classification": "none to classify: CONFLICT-FREE in all " + str(len(check["reading_plan"]["choices"])) + " choices; the whole-document proof attempt of the strict companion is CONFLICT-FREE"}
    m["documents"] = {**{k: v for k, v in pm["documents"].items() if k not in ("translation", "strict", "soft_chain_probe")},
                      "translation": "translation.ve.md (two reading sets carry content: the one of u0156.s03 with four candidates and the scope set of u0165.s03, whose candidates have their own attitude terms; built by nd.py all from translation-without-content.ve.md after repair_20261021T0600Z.py)",
                      "strict": "readings/all-strict.ve.md (the source of the strict content of the set of u0156.s03 and of the wide candidate of the scope set)",
                      "soft_chain_probe": "readings/soft-chain.ve.md (the u0156.s03 set as default rules with an unstated exception on the soft chain; a measurement document, not the translation)"}
    m["question_probe"] = {"what": "`ve ask --reading --json` on the translation: five yes-or-no questions about the denial, firmness, system-prompt-deception and claim-to-be-human units (probes/ask/q*.json); and `ve ask --json` without --reading (probes/ask/q*.answer.json). "
                                   "Questions 2, 4 and 5 are new in this run (the previous ones asked about the clarification unit, which is UNFORMALISED now)",
                           "questions": ask_questions_now, "read": 0, "no_reading": [a["result"]["text"] for a in asks_now], "answers_without_reading": [a["answer"] for a in asks_ans],
                           "reading": "none of the five is read (the reader does not know 'must not', 'must remain firm in each situation', 'may each instance ... deceive'); no answer for any of them, with --reading and without it",
                           "re_run_at_this_tag": True, "identical_to_previous_run": "questions 1 and 3 give the previous run's results; questions 2, 4 and 5 are different questions" if ask_same else "DIFFERS (questions 1 and 3)"}
    ccm = m["checked_content_main_chain"]
    ccm.pop("all_four_in_one_document")
    ccm["all_sets_in_one_document"] = {"admitted": nd["all"]["admitted"], "choices": nd["all"]["choice_count"], "verdict": nd["all"]["conflict_text"], "separations": nd["all"]["separations"], "route": nd["all"]["route"], "sizes": nd["all"]["sizes"],
                                      "sets": [x["unit"] for x in nd["all"]["sets"]]}
    m["lean_decided_share"] = json.loads(json.dumps(m["lean_decided_share"]).replace("each of the four sets", "each of the two sets"))
    assert "four sets" not in json.dumps(m["lean_decided_share"])
    m["companion_probe"]["attribution_records_note"] = ("premise_regression and its results are measurements of the documents of 20261018T1800Z and earlier (the control, the QT-0p-only and the final documents of that run); they name the reading sets those "
                                                        "documents had and are not re-measured in this run")
    m["rights_reading_probe"]["input_note"] = ("probe_rights.py reads readings/all-default.ve.md, the soft companion of run 20261008T1800Z (copied in and removed again), so its message lists that document's vocabulary; it is a probe of the language "
                                               "on an earlier document, not a measurement of this translation, and is byte-identical to the previous run's")
    m["quantities_qt0p"]["checks_after_repair"] = {**m["quantities_qt0p"]["checks_after_repair"], "measured_in": "20261018T1800Z (32 choices in the document then; this run's checks are in checks_this_run: 8)"}
    m["soft_chain_probe"].update({
        "what": ("the 'should' set of u0156.s03 (the only one left) with its defeasible candidates stated natively on the soft chain (rd-9: soft-norms@0 added beside norm-defaults@0; each default candidate is a default rule with `exception: {decided_by: unstated}` and `unless: []`; "
                 "the invented exception_to_* open term is not needed). Everything else is the translation. Not adopted (see result)"),
        "open_terms_before_after": [soft["open_terms_before"], soft["open_terms_after"]], "exception_terms_dropped": soft["exception_terms_dropped"],
        "what_it_would_change_if_check_passed": ("%d open terms instead of %d; the defeasible candidates become 'default rule, unstated exception' (the spec's C1 to C4) instead of 'strict rule unless an open term the translator invented'; the unit would stay READINGS"
                                                 % (soft["open_terms_after"], soft["open_terms_before"]))})
    m["companion_probe"]["what"] = m["companion_probe"]["what"].replace("the four reading sets", "the two reading sets")
    # the QT-0p and PS-0p records: carried (the units are unchanged and were audited FAITHFUL)
    m["quantities_qt0p"] = {
        **pm["quantities_qt0p"], "carried_in_this_run": True,
        "this_run": ("no unit, wording or formula of QT-0p changed in this run (the document's other repairs do not touch it): u0042.presupposition (CHECKED, 38 B), u0043.s02.p1 (LABELLED, 15 B) and u0043.s02.p2 (CHECKED, 75 B) stay as audited FAITHFUL; "
                     "u0043.s01 is still UNFORMALISED (counting). The fourth-type probe is re-run on the final document."),
        "claimed_bytes": {**pm["quantities_qt0p"]["claimed_bytes"], "gained_in_this_run": 0, "measured_this_run": cp["document_check"]["bytes_by_status"]},
        "premises": {**pm["quantities_qt0p"]["premises"], "measured": cp["document_check"]["premises"]},
        "probe_fourth_type": {**pm["quantities_qt0p"]["probe_fourth_type"], "negation_verdict": qt_probe["verdict"], "evidence": qt_probe["evidence"], "route": qt_probe["route"], "re_run_at_this_tag": True,
                              "the_positive_query_fourth": {"verdict": qt_fourth["verdict"], "note": pm["quantities_qt0p"]["probe_fourth_type"]["the_positive_query_fourth"]["note"]}},
        "checks_this_run": {"x3_existing_wordings_changed": cp["x3_vocabulary"]["existing_predicate_wordings_changed"], "choices": cp["document_check"]["choices"], "conflict": cp["document_check"]["conflict"],
                            "conclusions": cp["conclusions"]}}
    ps_prev = pm["presupposition_ps0p"]
    m["presupposition_ps0p"] = {
        **{k: v for k, v in ps_prev.items() if k not in ("this_run", "step4_triggers", "step6_goals", "step7_check", "prompt_tension", "expected_vs_measured", "finding")},
        "finding": ps_prev["finding"].replace("The translation keeps the natural identifiers and claims u0013.", "Until 20261020T1800Z the translation kept the natural identifiers and claimed u0013; since 20261021T0600Z it claims none of the four (PS-0p step 3)."),
        "superseded_in_20261021T0600Z": "the claim of u0013 recorded in carried_from_20261019T1800Z (step3_u0013: CHECKED, +24 B) is withdrawn: u0013.presupposition is UNFORMALISED again (PS-0p step 3 of the prompt; the audit of 20261020T1800Z rejected the claim for that reason); "
                                        "the other records of that section (u0095, u0002, u0235 expressible but unclaimed; u0032 reverted; the premise variants) stand",
        "carried_from_20261020T0600Z": ps_prev["this_run"],
        "this_run": {"document_changes": "u0013.presupposition: CHECKED -> UNFORMALISED (other.discourse); predicate core_value_of and the fence removed (PS-0p step 3; audit 20261020T1800Z)", "ledger_note_changes": {"u0013.presupposition": "note, expressible_with and audit_repair"},
                     "owner_probe": "evidence/owner-probe.json (owner_probe.py), re-run: the fences of u0095, u0002 and u0235 parse, render and round-trip; they are NOT added to the document (the premise-check budget still blocks claiming them)",
                     "u0013_lower_case_constant": owner["u0013.capital"]},
        "step4_triggers": {"units_with_a_trigger": sum(1 for e in ledger if e["presupposition_triggers"]), "entries": len(entries_all),
                           "by_class": dict(Counter(t["class"] for t in entries_all)), "by_carrier": dict(Counter(t["carrier"] for t in entries_all)),
                           "units_with_unresolved_carrier": len(unresolved), "blocker_tag": "other:presupposition",
                           "blocker_tag_note": ps_prev["step4_triggers"]["blocker_tag_note"],
                           "changed_in_this_run": {"u0013.presupposition": "carrier assumed -> unresolved (the unit is UNFORMALISED again), blocker other:presupposition added"},
                           "source": ps_prev["step4_triggers"]["source"], "dropped_false_positives": dropped},
        "step6_goals": {"file": "presupposition-goals.json", "counts": goals["counts"]},
        "step7_check": {"loads": True, "vocabulary_wordings_changed": cp["x3_vocabulary"]["existing_predicate_wordings_changed"], "fenced_units_unchanged": all(v.get("unchanged", True) for v in cp["x3_fences"].values()),
                        "choices": cp["document_check"]["choices"], "conflict": cp["document_check"]["conflict"], "premises": cp["document_check"]["premises"],
                        "carried_probes_byte_identical": dict(probe_same), "hard_conclusions": hard_summary, "hard_conclusions_changes": hard_changes},
        "prompt_tension": ("resolved by following the prompt: PS-0p step 3 says u0013, u0095, u0002 and u0235 are not claimed. The prompt's note for step 3 (“relational-noun wording not admitted in VE English”) is no longer true at this tag (ps-6r admits it; "
                           "evidence/ps6r/wording-lint.json), which the previous two runs reported; the audit of 20261020T1800Z rejected the claim of u0013 because it breaks the instruction, so u0013 is unclaimed and the ledger note says why. "
                           "If the orchestrator wants u0013 claimed, the step-3 sentence must be retired; the unit then returns as CHECKED, +24 B (evidence in prev/ and in the run of 20261020T1800Z)"),
        "expected_vs_measured": {"expected": "PS-0p's expectation (+29 B u0286, stretch +149 B class B) was met or superseded in earlier runs", "measured": "24 B lost in this run (u0013.presupposition, PS-0p step 3); nothing gained"}}
    m["vocabulary_change_check"] = {
        "rule": "DRI 2026-10-14 15:30Z (2): after a vocabulary change rerun the situation step (nd.py all) and check every existing fenced unit still parses unchanged",
        "vocabulary_changed_in_this_run": True,
        "situation_step_rerun": "nd.py all was rerun on the repaired start document (repair_20261021T0600Z.py): readings/nd-all.ve.md is the translation; checkpoint.py final (evidence/checkpoint-final.json): every fenced unit of the start document that is still fenced parses to the same formula; "
                                "the one fence that went (u0013.presupposition) went with its unit",
        "predicates_added": [], "predicates_removed": cp["x3_vocabulary"]["intended_removed"], "predicates_reworded_or_rebound": cp["x3_vocabulary"]["intended_reworded"], "sorts_added": [], "constants_added": [], "sort_noun_changed": {},
        "predicates_reworded_detail": {"seemingly_compelling_argument_to_cross_line": "arguments [situation] -> [claude_instance, situation]; wording “Claude faces seemingly compelling arguments ... in {0}” -> “{0} faces seemingly compelling arguments ... in {1}” (u0168.s01 audit repair)",
                                       "asked_to_keep_system_prompt_confidential": "arguments [claude_instance] -> [claude_instance, user]; wording “{0} is asked to keep its system prompt confidential” -> “... in a conversation with {1}” (u0156.s03 audit repair)"},
        "existing_predicate_wordings_changed_other_than_intended": cp["x3_vocabulary"]["existing_predicate_wordings_changed"], "existing_sort_nouns_changed": cp["x3_vocabulary"]["existing_sort_nouns_changed"],
        "fenced_blocks": {"now": MAIN.read_bytes().count(b"```ve "), "previous_run": (PREV_DIR / "translation.ve.md").read_bytes().count(b"```ve ")},
        "fenced_units": {k: v for k, v in cp["x3_fences"].items()}, "fenced_units_now": sorted(cp["fenced_units_now"]),
        "graph_nodes_unchanged": all(v["unchanged"] for v in cp["x3_fenced_units"].values() if v["now"] is not None),
        "units_differing_from_start_document": cp["units_differing_from_start"], "units_new_now": cp["units_new_now"],
        "existing_fenced_units_that_changed": [k for k, v in cp["x3_fences"].items() if v.get("unchanged") is False],
        "sort_entity": "the carried sort `entity` has the noun “thing” (plural “things”), never the reserved word “entity” (asserted by checkpoint.py)",
        "checkpoints": {"final": "evidence/checkpoint-final.json"}}
    m["rust_time_limit"] = {"rule": "DRI 2026-10-14 15:30Z (3)", "VE_RUST_TIMEOUT": "unset (default)", "prlimit": "not used", "cap_raised": False,
                            "note": "no check needed a raised limit; no cap or peak resident set to record" + (f"; hard-constraint queries answered on the first run: {not unavailable}")}
    m["changes_against_previous_run"] = {
        "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger), "changed_or_replaced_ids": changed_units, "added_ids": [], "removed_ids": [],
        "units_newly_covered": [], "units_with_status_change": {"u0013.presupposition": ["CHECKED", "UNFORMALISED"], "u0036.s05": ["READINGS", "UNFORMALISED"], "u0263.s04.p2": ["READINGS", "UNFORMALISED"]},
        "units_changed_by_audit_repair": ["u0013.presupposition", "u0036.s05", "u0156.s03", "u0168.s01", "u0263.s04.p2"], "units_changed_by_feature_upgrade": [], "units_changed_by_plan_repair": ["u0013.presupposition"],
        "units_changed_ledger_note_only": [],
        "open_terms_added": added_terms, "open_terms_removed": removed_terms, "open_terms_changed": changed_terms_detail, "open_terms_count_before_after": [pm["open_terms_count"], len(open_terms)],
        "reading_sets_before_after": [4, len(reading_sets_now)], "choices_before_after": [32, len(check["reading_plan"]["choices"])],
        "predicates_added": [], "predicates_removed": cp["x3_vocabulary"]["intended_removed"], "predicates_changed": cp["x3_vocabulary"]["intended_reworded"], "sorts_added": [], "sort_noun_changed": [], "constants_added": [],
        "translation_byte_identical_to_previous_run": MAIN.read_bytes() == (PREV_DIR / "translation.ve.md").read_bytes(),
        "ledger_annotation_changes": "status_in_previous_run regenerated; the five changed entries rewritten; everything else carried"}
    assert not m["changes_against_previous_run"]["translation_byte_identical_to_previous_run"]
    m["language_changes_since_previous_tag"] = {
        "from": PREV_TAG, "to": TAG,
        "merged": {
            "feature/ap-1c (ap-1c)": "lean/VE/Acts/LexicalProofs.lean (667 lines of theorems) and `check_extends` in lean/VE/Acts/Compat.lean; DELTA: None. No definition, diagnostic, limit, verdict, field or mode changes; the four new definitions are proof helpers",
            "feature/me-6b (me-6b)": "lean/VE/Calc/Units.lean (ve-units@2: UnitDef, UnitEnv, decodeV2); DELTA: public output none, no service mode, command or route; reached only by the Lean build and tests/test_calc_units.py",
            "feature/et-3cb (et-3cb)": "lean/VE/Events/{Calendar,Conservative}.lean (the last two theorems of ET-3: eventsPremises_satisfiable, embeddable_complete); DELTA: None. The Events modules are still reachable from no service mode, route, decoder or relay",
            "feature/df-1ac (df-1ac)": "lean/VE/Defaults/Wire.lean (the `defaults-elaborate` and `defaults-coherence` kinds, defaultsCase); DELTA: what users see does not change; no service mode, executable, response shape, schema, relay, Python or Rust file calls them (df-1ad's kind-table row would)",
            "feature/sc-1ad (sc-1ad)": "lean/VE/Scope/{Govern,Theorems}.lean: the graph step (edgesOf, edgesInto, addOver), governFast and four theorems; DELTA: the changed definitions reach no caller until the document mode (SC-1b); `govern` now answers a precedes or yields governor where sc-1ac refused it (`ScopeNoEffect` appears in no answer yet)"},
        "merge_commits_listed": merged, "other_first_parent_commits": other_first_parent,
        "checked_by": ("git diff " + PREV_TAG + ".." + TAG + " --shortstat: " + diff_all + "; git diff " + PREV_TAG + ".." + TAG + " --shortstat -- ve lean rust conformance: " + diff_stat +
                       "; git diff --stat -- ve rust conformance tests lean/VE/Service lean/ResponseShape names only ve/assurance-manifest.json under ve/ (bookkeeping), the tests and docs. Read: the DELTA.md of ap-1c, me-6b, et-3cb, df-1ac and sc-1ad. "
                       "None adds a wording, a construct or a profile a document can use (measured: scope@0, defaults@0 and calc@0 are still refused, evidence/new-profile-probe.json). The unchanged start document, rebuilt by nd.py all at this tag before any repair, "
                       "was cmp-identical to the previous run's translation (4 min 49 s)"),
        "newly_expressible_features": 0, "units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
        "newly_measurable": ("`scope@0` (govern, now with the graph step and governFast; the 352 units of the cross-sentence scope tally) and `defaults@0` (the wire kinds) have Lean modules but no document can name them yet (the document mode SC-1b, sc-3ab and df-1ad are the batches that open them); "
                             "`acts@0` and `judgments@0` wait for ap-1b and JT-2 as before; the render differs from the previous run's in " + str(render_diff_lines) + " lines, all from the audit repairs"),
        "what_made_the_difference": "nothing in the language: the differences against the previous run are the audit repairs of the translation (u0168.s01, u0156.s03, u0036.s05 with u0263.s04.p2, u0013.presupposition)"}
    m["seeded_bugs"] = json.load(open(RUN / "evidence/seeded-bugs.json")) if (RUN / "evidence/seeded-bugs.json").exists() else {"pending": True}
    m["plan_repair_AT0p_state"] = {u_: "AT-0p (attitudes plan, DRI AT2): carried unchanged, shape asserted again: guard = ( C(s) and knowingly_engages_N(c, s) ) or thinks_quite_likely_N(c, s), two binary open terms on (claude_instance, situation) (u0165.s03: one pair per candidate); not a changed unit in this run"
                                   for u_ in HC_UNITS}
    m["plan_repairs_by_plan"] = {"presupposition (PS-0p step 3)": ["u0013.presupposition"]}
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
