#!/usr/bin/env python3
"""Run VE on the built documents, write the ledger, rendering and metrics.

Run after build.py and probe_unspecified.py, from anywhere:
    uv run python usecases/claude-constitution-pilot/run-20261004T0600Z/finish.py
(PATH must contain ~/.elan/bin for the Lean routes.)
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))
import build  # noqa: E402
import spec  # noqa: E402
import spec_nd as nd  # noqa: E402

SOURCE_PATH = ROOT / "usecases/claude-constitution-pilot/source/claude-constitution.md"
SOURCE = SOURCE_PATH.read_bytes()
DOCS = {"main": RUN / "translation.ve.md", "strict": RUN / "readings/all-strict.ve.md",
        "default": RUN / "readings/all-default.ve.md", "s1": RUN / "readings/s1.ve.md"}
COVERED = {"CHECKED", "LABELLED", "OPEN", "READINGS"}
RUN_ID = "20261004T0600Z"
PREV_RUN = "20261003T0600Z"

HARD = {h[0]: h for h in nd.HARD}
PREFERENCE = nd.PREFERENCE
GENERALLY = nd.GENERALLY
FORCE_UNITS = [u for u in build.FORCE_UNITS]            # old unit ids (u0125.s04, u0263.s04 carry a .p2 norm part)
SOFT_ONE = [u for u in build.SOFT_ONE if u not in GENERALLY]   # u0073.s05 moved to norm-defaults@0 (OPEN, one reading)
OPS = {i["old"]: i for i in nd.OPS_ALL}

# ---- audits of this lineage: what each accepted. Units accepted AND byte-identical in this run count as audit-verified.
AUDIT_PASSED_LABELLED = ["u0023", "u0032.heading", "u0069.heading", "u0095.heading", "u0103", "u0108", "u0126",
                         "u0143.heading", "u0162.heading", "u0174.heading", "u0219.heading", "u0254.heading",
                         "u0268.heading", "u0277", "u0282", "u0286.heading", "u0294", "u0298",
                         "u0002.heading", "u0008.heading", "u0013.heading", "u0040.heading", "u0042.heading",
                         "u0075.heading", "u0083.heading", "u0151.heading", "u0195.heading", "u0257.heading",
                         "u0265", "u0027.heading", "u0130.heading", "u0207.heading", "u0260.heading",
                         "u0055.heading", "u0238.heading",
                         "u0235.heading"]  # new: accepted by the 20261001T1800Z audit
AUDIT_PASSED_SUBSTANTIVE = ["u0248", "u0052.s01", "u0168.s01", "u0263.s04.p2", "u0073.s05", "u0036.s05", "u0165.s01",
                            "u0165.s04", "u0156.s03", "u0078.s01", "u0165.s02", "u0165.s03"]
# 20261001T1800Z audit (17/20): accepted 15 LABELLED, u0073.s05 and u0263.s04.p2; rejected u0165.s02, u0165.s04, u0165.s06
# (a defeasible reading kept in the reading set of an absolute restriction). The sample is reproducible:
# random.Random("20261001T1800Z").sample(eligible_units_in_ledger_order, 20).
AUDIT_REJECTED_1001 = ["u0165.s02", "u0165.s04", "u0165.s06"]
# 20261002T0620Z audit (17/20): rejected three units of the operator and user sentences. Their repair is this run's work.
AUDIT_REJECTED_0620 = ["u0062.s01", "u0123.s02.p1", "u0166.s04.p4"]
REPAIRED_0620 = {
    "u0062.s01": "Its permission rules allowed every operator input classified as specific instructions, a persona or "
                 "information, including inputs that u0123.s03 says operators cannot give, so VE reported a conflict that the "
                 "source does not contain. Repaired: each of the three permissions is scoped by the six limits of u0123.s03 as "
                 "exceptions (the permission does not cover those inputs); no default is added for any other input.",
    "u0123.s02.p1": "(1) “Legitimately” made a pure ability reading incomplete: the reading set now keeps three readings, a "
                    "permission (the word of permission carries it), a conditional permission (legitimacy is a separate condition) "
                    "and an ability that carries the evaluative as the named open term instruction_is_legitimate. (2) The five "
                    "permission rules were too broad (a role-play instruction stayed permitted even when it included conduct "
                    "u0123.s03 prohibits): each is now scoped by the six limits of u0123.s03 as exceptions.",
    "u0166.s04.p4": "The permission candidate added a duty on operators and users not to unlock the hard constraints, which the "
                    "source does not state. Repaired: the permission reading and its two rules are removed; the clause is one "
                    "checked ability statement (no operator and no user is able to unlock a hard constraint), with no norm and "
                    "no duty on anyone.",
}
# 20261002T1800Z audit (19/20): rejected u0168.s01 (the defeasible reading weakens "absolute ... regardless of seemingly compelling arguments")
AUDIT_REJECTED_1800 = ["u0168.s01"]
REPAIRED_1800 = {
    "u0168.s01": "The reading set kept a defeasible reading of “Claude should remain firm” whose open exception could make firmness "
                 "not required, although the source calls the lines absolute and says they should never be crossed regardless of "
                 "seemingly compelling arguments (u0166.s01) and that the strength of an argument is not sufficient justification "
                 "for acting against these principles (u0168.s03). Repaired: the defeasible candidate is removed; one strict "
                 "reading carries the rule as content (completion `unspecified`), chosen from the two cited spans, not silently."}
# 20261003T0600Z audit (14/20): rejected six units whose companion elaborations (soft-norms@0 and readings@1 on the soft chain) complete
# a duty or a permission with `deny`, which the source does not state, or whose force the candidates misstate.
AUDIT_REJECTED_1003 = ["u0156.s03", "u0036.s05", "u0078.s01", "u0123.s03", "u0073.s05", "u0263.s04.p2"]
REPAIRED_1003 = {
    "u0036.s05": "The companions (readings/all-default.ve.md, readings/s1.ve.md) carried the defeasible reading with the completion "
                 "`deny`, which says “not required” outside the stated conditions; the source says nothing there. Repaired: no "
                 "companion elaborates the defeasible reading as part of the translation (both stay as demonstrations of the "
                 "language, outside every claim); the two readings stay in the main document's reading set (no content), the "
                 "strict reading is elaborated with the completion `unspecified`.",
    "u0263.s04.p2": "Same defect and repair as u0036.s05.",
    "u0156.s03": "Same defect and repair as u0036.s05; here the defeasible companion also turned an exception into “not required to "
                 "avoid deception”, which defeating the rule does not establish. The strict reading stays a prohibition "
                 "(permission predicate, completion `unspecified`).",
    "u0078.s01": "“should err on the side of following” is a leaning (a preference), which neither a strict duty nor a defeasible "
                 "duty keeps; the candidates replaced it with duties, and the companions settled the unstated cases negatively. "
                 "Repaired: the unit is UNFORMALISED (missing feature other:graded-force); the reading set, the rules and the "
                 "predicates for it are removed from every document.",
    "u0123.s03": "The S1 companion completed the operator permission with `deny` and gave the ability candidates content about "
                 "operators *supplying* instructions rather than getting Claude to do the listed behaviours. Repaired: the "
                 "companion no longer counts; the two ability candidates of the main document's reading set now say what the "
                 "audit asks (an operator is unable to get Claude to do each behaviour by instructing it); the narrow permission "
                 "is elaborated in the strict companion with the completion `unspecified`.",
    "u0073.s05": "The soft-norms@0 elaboration needed the completion `deny`. Repaired: one reading with content in the main document "
                 "under norm-defaults@0 (completion `unspecified`): the case the bullet names is the guard, the three conditions "
                 "the source states are exceptions, and “generally” is one more named open exception (open term "
                 "general_exception_to_complying) that nobody the source names decides. VE: where the prompt addresses the case "
                 "and no exception holds, SETTLED yes (required); where an exception holds or the prompt does not address the "
                 "case, UNDECIDED.",
}
# The same audit's VERDICTS block lists all 20 sampled units, so its 14 acceptances can be identified (earlier audits named only their
# rejections). Accepted AND byte-identical to the audited form (the run 20261003T0600Z ledger and document) = audit-verified; a later
# acceptance supersedes an earlier rejection of the same unit when the unit is byte-identical to the accepted form.
AUDIT_PASSED_1003_SUBSTANTIVE = ["u0248", "u0165.s05", "u0166.s04.p4", "u0165.s02", "u0165.s01", "u0165.s06", "u0165.s07"]
AUDIT_PASSED_1003_LABELLED = ["u0013.heading", "u0162.heading", "u0108", "u0032.heading", "u0282", "u0294", "u0219.heading"]
AUDIT_REJECTED_EARLIER = {"20260929T1800Z": ["u0156.s03", "u0165.s03"], "20260930T0600Z": ["u0165.s05", "u0165.s06"]}
REPAIRED_THIS_RUN = list(HARD)  # all seven (the rejected three and the four of the same shape): 20261002T0620Z run
REPAIRED_THIS_RUN_0600 = list(AUDIT_REJECTED_1800)
REPAIRED_NOW = list(AUDIT_REJECTED_1003)
REPAIRED_THIS_RUN_1800 = AUDIT_REJECTED_0620 + ["u0123.s01.p1"]  # u0123.s01 has the same permission shape and takes the same scope
REPAIRED_EARLIER_NOT_REAUDITED = ["u0165.s05", "u0165.s06", "u0165.s07", "u0125.s04.p2"]
VOLATILE = ("status_in_previous_run", "audit_repair", "separating_situation", "case_atoms")


def ve(*args):
    proc = subprocess.run([sys.executable, "-m", "ve", *args], cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"ve {' '.join(args)} failed:\n{proc.stderr[-2000:]}")
    return proc.stdout


def front_matter(path):
    data = path.read_bytes()
    end = data.index(b"\n---\n", 4)
    return json.loads(data[4:end])


def excerpt(text):
    return text.replace("\n", " ")[:160]


# ------------------------------------------------------------------ English of the rules
def english_nd(path):
    """The W1 English export of every rule alone (norm-defaults environment), and whether it parses back."""
    from ve.norm_english import parse_english, render_english
    from ve.norms import NormDocument
    meta = front_matter(path)
    env = build._environment(meta["environment"])
    out = {}
    for unit in meta["units"]:
        content = unit.get("content")
        if not content or "norm" not in content:
            continue
        doc = NormDocument(env, [content])
        text, manifest = render_english(doc)
        try:
            ok = parse_english(env, text, manifest).document_hash == doc.document_hash
            error = None if ok else "hash differs"
        except Exception as exc:
            ok, error = False, f"{type(exc).__name__}: {exc}"
        out[content["norm"]["name"]] = {"text": text.removeprefix("Rule 1. "), "round_trip": ok, "error": error}
    return out


def english_soft(path):
    """The soft-norm English export of every rule alone, and whether it parses back to the same rule."""
    from ve.norm_english import _render_soft_english, parse_english, render_english
    from ve.softnorms import SoftEnvironment, SoftNormDocument
    meta = front_matter(path)
    env = SoftEnvironment(meta["environment"])
    out = {}
    for unit in meta["units"]:
        content = unit.get("content")
        if not content or "norm" not in content:
            continue
        doc = SoftNormDocument(env, [content])
        text, manifest = _render_soft_english(doc)
        w1_lines = render_english(doc.core, _w1=True)[0].split("\n")
        truncated = len(text.split("\n")) < len(w1_lines)
        display = text if not truncated else text.split("\n")[0] + "\n" + "\n".join(w1_lines[1:])
        try:
            back = parse_english(env, text, manifest)
            ok = back.document_hash == doc.document_hash
            error = None if ok else "hash differs"
        except Exception as exc:
            ok, error = False, f"{type(exc).__name__}: {exc}"
        out[content["norm"]["name"]] = {"text": " ".join(p.strip() for p in display.split("\n")).removeprefix("Rule 1. "),
                                        "export_truncated": truncated, "round_trip": ok, "error": error}
    return out


def silence_sentences(path):
    """norm-defaults 4: what the text does not say, per regulated predicate (VE's own wording)."""
    from ve.document import load_document
    from ve.norm_defaults_english import legend, silence_sentence
    from ve.norm_english import default_sentence
    doc = load_document(path)["norm_defaults"]
    full_text = {p: silence_sentence(doc, p) for p in doc.unspec}
    # the full wording lists every guard of every rule on the predicate; past 400 characters give the short legend sentence
    full_text = {p: (t if t is not None else "no situation is left unsaid: a rule decides every case") for p, t in full_text.items()}
    short = {p: (t if len(t) <= 400 else default_sentence(doc.env, p).rstrip(".")[0].lower() + default_sentence(doc.env, p).rstrip(".")[1:])
             for p, t in full_text.items()}
    (RUN / "readings/silence.json").write_text(json.dumps({"full": full_text, "as_used_in_ledger": short}, indent=2, ensure_ascii=False) + "\n")
    return short, list(legend(doc.env))


# ------------------------------------------------------------------ separating situations (S1: checked by Lean when readings/s1.ve.md loads)
def separating_situations(s1_report, s1_result):
    """For every set of the S1 document, the situations Lean checked (`ve_readings_route`), their probes and VE's wording.
    Run 20261003T0600Z: these replace the previous runs' situations, which finish.py computed with VE's evaluator and VE could not
    admit (a candidate norm carried no content). Keyed by unit id."""
    out = {}
    meta = front_matter(DOCS["s1"])
    by_set = {s["id"]: s for s in meta["reading_sets"]}
    words = {s["set"]: s["source_word"] for s in s1_result["sets"]}
    for entry in s1_report["readings"]["sets"]:
        item = by_set[entry["set"]]
        pairs = [{"readings": p["readings"], "situation_id": p["situation"], "witness": item["situations"][p["situation"]]["witness"],
                  "probe": p["probe"], "wording": p["wording"], "text": p["text"]} for p in entry["pairs"]]
        out[entry["unit"]] = {
            "set": entry["set"], "source_word": words.get(entry["set"]), "pairs": pairs, "findings": entry["findings"],
            "checked_by": "Lean (ve_readings_route readings-validate) when readings/s1.ve.md loads; Python regenerates Lean's answer byte "
                          "for byte; Rust replays each situation (untrusted)",
            "note": "the separation is about the soft-norms@0 form of the readings (completion deny where the rule's predicate needs one), "
                    "the only chain readings@1 admits beside content; a SeparatedByDecisionOnly finding is not certified "
                    "(decision_only_sound is unproved)"}
    return out


# ------------------------------------------------------------------ ledger
def atom_words(env_meta, name):
    text = env_meta["vocabulary"]["predicates"][name]["verbalisation"]
    return text.replace("{0}", "the situation").replace("{1}", "the situation")


def atoms_of(r):
    found = []

    def walk(f):
        if isinstance(f, list):
            if f and f[0] in ("unary", "binary") and f[1] not in found:
                found.append(f[1])
            for part in f[1:]:
                walk(part)
    walk(r["guard"])
    for u in r["unless"]:
        walk(u)
    return found


def case_atoms(env_meta, r):
    return {a: atom_words(env_meta, a) for a in atoms_of(r)}


def probe_status(probe, unit_label_prefix):
    return [p for p in probe["points"] if p["label"].startswith(unit_label_prefix)]


def new_ledger(prev, main_meta, eng_nd, eng_soft, probe, silence, separation):
    prev_by_id = {e["id"]: e for e in prev}
    env_nd = main_meta["environment"]
    out = []
    for entry in prev:
        uid = entry["id"]
        base = {"id": uid, "span": entry["span"], "source_excerpt": entry["source_excerpt"],
                "parent_unit": entry["parent_unit"], "old_unit": entry.get("old_unit", uid)}
        if uid in HARD:
            _, rule, pred, term, act, words = HARD[uid]
            r = nd.ND_RULES[uid]
            reading = eng_nd[rule]
            holds = [p for p in probe["points"] if p["label"] == f"{uid}: the case holds"][0]
            holds_not = [p for p in probe["points"] if p["label"] == f"{uid}: the case does not hold"][0]
            rejected = uid in AUDIT_REJECTED_1001
            out.append({
                **base, "status": "OPEN", "kind": "norm", "rule": rule, "predicate": pred, "sign": "negative",
                "open_terms": [term], "previous_status": entry["previous_status"],
                "previous_missing_feature": entry.get("previous_missing_feature"), "status_in_previous_run": entry["status"],
                "note": ("One strict reading: “Claude should never …” (list lead-in u0164.s02, UNFORMALISED: it supplies the "
                         "subject and the force) is a prohibition on Claude, absolute because the source says so: “absolute "
                         "restrictions … lines that should never be crossed regardless of context, instructions, or seemingly "
                         "compelling arguments” (u0166.s01) that “cannot be unlocked by any operator or user” (u0166.s04, "
                         "whichever of its two readings is taken, see u0166.s04.p4). The defeasible reading is not admissible "
                         "for this unit: it would give the restriction an exception, which these two sentences exclude. "
                         "Written as a prohibition (a permission predicate with a negative rule, completion `unspecified`), "
                         "scoped by the sort of the party the source names (instances of Claude). The act phrase "
                         f"“{act.replace('{0}', 'Claude').replace('{1}', 'a situation')}” is only a label for the case atom, which "
                         "holds the source’s own words."),
                "case_atoms": case_atoms(env_nd, r),
                "audit_repair": (
                    ("Rejected by the 20261001T1800Z audit (17/20): the reading set still offered a defeasible rule with an open "
                     "exception for an absolute restriction, and the narrowing to strict was “recorded only”. " if rejected else
                     "Not sampled by the 20261001T1800Z audit, but it has the same shape as the three units that audit rejected "
                     "(u0165.s02, u0165.s04, u0165.s06), so it is repaired with them. ")
                    + "Repaired: the defeasible candidate is gone (it contradicts u0166.s01 and u0166.s04); one strict reading "
                      "carries the rule as content. Counted as claimed, not audit-verified."),
                "force_resolution": {"how": "one reading chosen from cited source spans, not silently",
                                     "cites": ["u0166.s01", "u0166.s04"],
                                     "dropped_candidate": "defeasible (a rule with an open exception)",
                                     "why_dropped": "u0166.s01 says these are absolute restrictions regardless of context, "
                                                    "instructions or arguments; u0166.s04 says no operator or user can unlock them"},
                "completion": "unspecified",
                "where_the_text_is_silent": silence[pred],
                "check": {"case holds": holds["status"], "case does not hold": holds_not["status"],
                          "meaning": "SETTLED no = the text says Claude may not; UNDECIDED = the text does not say (nothing is "
                                     "permitted or forbidden by default)"},
                "reading_set": None,
                "readings": [{"id": "strict", "in": "translation.ve.md and readings/all-strict.ve.md",
                              "english": reading["text"], "english_round_trip": reading["round_trip"],
                              "meaning": "a strict rule: Claude may not do the act in a situation that is a case of the source’s words"}],
                "document_status": "OPEN (one strict reading; its case atom is an open term)"})
        elif uid in nd.ABSOLUTE:
            r = nd.ND_RULES[uid]
            reading = eng_nd[r["rule"]]
            holds = [p for p in probe["points"] if p["label"] == f"{uid}: the case holds"][0]
            holds_not = [p for p in probe["points"] if p["label"] == f"{uid}: the case does not hold"][0]
            out.append({
                **base, "status": "OPEN", "kind": "norm", "rule": r["rule"], "predicate": r["predicate"], "sign": "positive",
                "open_terms": list(r["open_terms"]), "previous_status": entry["previous_status"],
                "previous_missing_feature": entry.get("previous_missing_feature"), "status_in_previous_run": entry["status"],
                "note": ("One strict reading: “Claude should remain firm” when faced with seemingly compelling arguments to cross "
                         "“these lines”. “These lines” is resolved to the lines drawn by the hard constraints (context: u0166.s01 "
                         "“lines that should never be crossed”); the translator’s resolution, not the source’s words. The force is "
                         "chosen from cited spans, not silently: u0166.s01 calls the lines absolute and says they should never be "
                         "crossed “regardless of context, instructions, or seemingly compelling arguments”, and u0168.s03 says "
                         "“the strength of an argument is not sufficient justification for acting against these principles”. A "
                         "defeasible reading would let an open exception make firmness not required when the argument is "
                         "compelling, which these two sentences exclude (audit 20261002T1800Z). The case atom “seemingly compelling "
                         "argument to cross the line” is the source’s own phrase and an open term; the duty is on instances of "
                         "Claude only."),
                "case_atoms": case_atoms(env_nd, r),
                "audit_repair": REPAIRED_1800[uid] + " Counted as claimed, not audit-verified.",
                "force_resolution": {"how": "one reading chosen from cited source spans, not silently",
                                     "cites": ["u0166.s01", "u0168.s03"],
                                     "dropped_candidate": "defeasible (a rule with an open exception)",
                                     "why_dropped": "u0166.s01: absolute, never crossed regardless of seemingly compelling arguments; "
                                                    "u0168.s03: the strength of an argument is not sufficient justification"},
                "completion": "unspecified",
                "where_the_text_is_silent": silence[r["predicate"]],
                "check": {"case holds": holds["status"], "case does not hold": holds_not["status"],
                          "meaning": "SETTLED yes = the text says Claude must remain firm; UNDECIDED = the text does not say"},
                "reading_set": None,
                "readings": [{"id": "strict", "in": "translation.ve.md and readings/all-strict.ve.md",
                              "english": reading["text"], "english_round_trip": reading["round_trip"],
                              "meaning": "a strict rule: instances of Claude must remain firm in a situation that is a case of the "
                                         "source’s words"}],
                "document_status": "OPEN (one strict reading; its case atom is an open term)"})
        elif uid in PREFERENCE:
            out.append({**base, "open_terms": [t for t in entry.get("open_terms", []) if t not in nd.PREFERENCE_DROPPED_PREDICATES],
                        "status": "UNFORMALISED", "missing_feature": nd.PREFERENCE_FEATURE, "other_blockers": ["norms"],
                        "previous_status": entry["previous_status"], "previous_missing_feature": entry.get("previous_missing_feature"),
                        "status_in_previous_run": entry["status"],
                        "note": ("“Claude should err on the side of following operator instructions unless …”: the verb phrase states a "
                                 "leaning (a weighted preference for the operator's side, with six conditions under which the leaning "
                                 "gives way), not a duty. A strict duty strengthens it to compliance, a defeasible duty keeps an "
                                 "exception but no leaning, and no rule in the language says “prefer” or ranks one party's "
                                 "instructions above another's. The six “unless doing so requires …” conditions and the condition "
                                 "“genuine conflicts exist between operator and user goals” are recorded here as the sentence's "
                                 "content words; none is stated as a rule (graded normative force is a missing feature, "
                                 "other:graded-force)."),
                        "audit_repair": REPAIRED_1003[uid] + " The unit no longer has a covered status."})
        elif uid in GENERALLY:
            r = nd.ND_RULES[uid]
            reading = eng_nd[r["rule"]]
            holds = [p for p in probe["points"] if p["label"] == f"{uid}: the case holds"][0]
            holds_not = [p for p in probe["points"] if p["label"] == f"{uid}: the case does not hold"][0]
            exc = [p for p in probe["points"] if p["label"] == f"{uid}: the case holds and the “generally” exception applies"][0]
            unsafe = [p for p in probe["points"] if p["label"] == f"{uid}: the case holds but complying is unsafe"][0]
            out.append({
                **base, "status": "OPEN", "kind": "norm", "rule": r["rule"], "predicate": r["predicate"], "sign": "positive",
                "open_terms": list(r["open_terms"]), "previous_status": entry["previous_status"],
                "previous_missing_feature": entry.get("previous_missing_feature"), "status_in_previous_run": entry["status"],
                "note": ("One reading, a defeasible duty: “Claude should generally comply with the system prompt’s instructions if doing "
                         "so is not unsafe, unethical, or against Anthropic’s guidelines”, in the case the bullet names (an operator "
                         "prompt addresses how Claude should behave). The condition the source states, “not unsafe, unethical, or "
                         "against Anthropic’s guidelines”, is read as none of the three and written as three exceptions (“except when "
                         "complying is unsafe”, and so on; each is an open term, the source gives no test): the same condition, which "
                         "reads and parses back in English, while the guard form (a nested all-of list) does not parse back. "
                         "“Generally” is carried by one more open exception, "
                         "general_exception_to_complying, a case the source’s word leaves out, decided by nobody the source names. "
                         "The duty is on instances of Claude only; where no rule decides, the text does not say (completion "
                         "`unspecified`), so VE reports UNDECIDED, not “not required”. Moved from the soft-norms@0 elaboration "
                         "(readings/all-default.ve.md), which needed the completion `deny`, to norm-defaults@0 (audit "
                         "20261003T0600Z)."),
                "case_atoms": case_atoms(env_nd, r),
                "audit_repair": REPAIRED_1003[uid] + " Counted as claimed, not audit-verified.",
                "completion": "unspecified",
                "where_the_text_is_silent": silence[r["predicate"]],
                "check": {"case holds": holds["status"], "case does not hold": holds_not["status"],
                          "case holds but complying is unsafe": unsafe["status"],
                          "case holds and the generally exception applies": exc["status"],
                          "meaning": "SETTLED yes = the text says Claude must comply; UNDECIDED = the text does not say"},
                "reading_set": None,
                "readings": [{"id": "defeasible-as-open-exception", "in": "translation.ve.md and readings/all-strict.ve.md",
                              "english": reading["text"], "english_round_trip": reading["round_trip"],
                              "meaning": "a rule with an open exception: instances of Claude must comply with the system prompt’s "
                                         "instructions when an operator prompt addresses the case and complying is none of the three, "
                                         "unless a case the word “generally” leaves out applies"}],
                "document_status": "OPEN (one reading; its conditions and its exception are open terms)"})
        elif uid in FORCE_UNITS or uid.rsplit(".p", 1)[0] in FORCE_UNITS and uid.endswith(".p2") or uid in SOFT_ONE:
            old_uid = uid if uid in FORCE_UNITS or uid in SOFT_ONE else uid.rsplit(".p", 1)[0]
            item = spec.UNITS_BY_OLD[old_uid]
            rec = {**entry}
            rec["status"] = "READINGS"
            if uid in SOFT_ONE:
                rec["previous_status"] = entry["previous_status"]
                rec["status_in_previous_run"] = entry["status"]
                rec["note"] = (entry["note"] + " Moved from a content-bearing unit to a one-candidate reading set: the main "
                               "document now runs under norm-defaults@0, which cannot share a document with soft-norms@0, so the "
                               "defeasible rule is elaborated and checked in readings/all-default.ve.md (unchanged there).")
                rec["reading_set"] = f"force-{uid.replace('.', '-')}"
                rec["readings"] = [{"id": "default", "elaborated_in": "readings/all-default.ve.md",
                                    "english": eng_soft[item["rule"]]["text"],
                                    "english_round_trip": eng_soft[item["rule"]]["round_trip"],
                                    "meaning": "a defeasible rule (“generally”) with an open exception decided by nobody the "
                                               "source names (decision soft__excepted__comply_operator_prompt)"}]
                rec["document_status"] = ("OPEN (pending reading set: the main document is norm-defaults@0, which readings@1 content "
                                          "cannot join; the default rule is a fixed unit in readings/s1.ve.md)")
            else:
                rule = item["rule"]
                strict_name = nd.ND_RULES[old_uid]["rule"]
                note = nd.NOTE_OVERRIDE.get(old_uid)
                if note:
                    rec["note"] = note
                rec["status_in_previous_run"] = entry["status"]
                rec["readings"] = [
                    {"id": "strict", "elaborated_in": "readings/all-strict.ve.md",
                     "predicate": nd.ND_RULES[old_uid]["predicate"], "completion": "unspecified",
                     "english": eng_nd[strict_name]["text"], "english_round_trip": eng_nd[strict_name]["round_trip"],
                     "meaning": "a strict rule" + (" (a prohibition: a permission predicate with a negative rule)"
                                                   if not nd.ND_RULES[old_uid]["sign"] else "")},
                    {"id": "default", "elaborated_in": None, "demonstrated_in": "readings/all-default.ve.md and readings/s1.ve.md",
                     "completion": "none: the source states none, and the soft route (soft-norms@0) cannot state this reading "
                                   "without one; the demonstration companions complete with `deny`, an invention that is not part "
                                   "of this translation (audit 20261003T0600Z)",
                     "english": eng_soft[rule]["text"], "english_round_trip": eng_soft[rule]["round_trip"],
                     "meaning": "a defeasible rule with an open exception decided by nobody the source names "
                                f"(decision {'soft__excepted__' + rule.replace('-', '_')}); recorded without content in the main "
                                "document's reading set"}]
                rec["predicate"] = nd.ND_RULES[old_uid]["predicate"]
                rec["sign"] = "negative" if not nd.ND_RULES[old_uid]["sign"] else "positive"
                rec["case_atoms"] = case_atoms(env_nd, nd.ND_RULES[old_uid]) if atoms_of(nd.ND_RULES[old_uid]) else {}
                rec.pop("separating_situation", None)
                rec.pop("checked_in", None)
                rec["document_status"] = ("OPEN (pending reading set in the main document, no content: readings@1 content cannot join "
                                          "norm-defaults@0, and the soft route cannot state the defeasible reading without an invented "
                                          "completion)")
                if uid in separation:
                    rec["s1_demonstration_only"] = {
                        "claimed": False,
                        "what": "readings/s1.ve.md carries both readings as content of one reading set on the soft chain, with one "
                                "Lean-checked situation; it completes the duty with `deny`, which the source does not state, so it "
                                "is a demonstration of the language, not this unit's translation (audit 20261003T0600Z)",
                        "separating_situation": separation[uid]}
                rec["note"] = (rec["note"] + " Run 20261004T0600Z: the S1 and soft-norms companions (readings/s1.ve.md, "
                               "readings/all-default.ve.md) are demonstrations only; their `deny` completion says “not required” "
                               "outside the stated conditions, which the source does not say. Nothing about this unit is claimed "
                               "from them.")
                if old_uid in ("u0156.s03", "u0125.s04"):
                    rec["strict_reading_predicate"] = nd.ND_RULES[old_uid]["predicate"]
                    rec["defeasible_reading_predicate"] = item["predicate"]
                    rec["where_the_text_is_silent"] = silence[nd.ND_RULES[old_uid]["predicate"]]
                    rec["audit_repair"] = (rec.get("audit_repair", "") + " This run: the strict reading is a prohibition again "
                                           "(permission predicate, completion `unspecified`), no longer the duty to avoid the act; "
                                           "the defeasible reading keeps the duty form because the soft route needs a completion.").strip()
            out.append(rec)
        elif uid in OPS_PARENTS:
            out.extend(ops_entries(entry, base, main_meta, eng_nd, probe, silence))
        else:
            if uid == "u0164.s02":
                entry = {**entry, "citation_note": "List lead-in of the hard-constraint bullets u0165.s01 to s07: it supplies their "
                         "subject and the force “should never”, which their one strict reading carries. It stays UNFORMALISED on "
                         "its own (no rule of its own; the bullets' rules are its content)."}
            if uid in ("u0166.s01",):
                entry = {**entry, "citation_note": "Cited as the reason the seven hard constraints have one strict reading "
                         "(absolute restrictions). Unchanged: still UNFORMALISED."}
            out.append(entry)
    for record in out:
        if record["id"].endswith(".heading") and "open_terms" in record:
            del record["open_terms"]
    return out


OPS_PARENTS = set(OPS)
S1_SEPARATION: dict = {}   # unit id -> the S1 document's report for its set (filled in main)


def ops_entries(entry, base, main_meta, eng_nd, probe, silence):
    uid = entry["id"]
    item = OPS[uid]
    a, b = entry["span"]
    out, cursor = [], a
    strict_cursor = 0
    segs = item["main"]
    for index, seg in enumerate(segs, 1):
        text = seg[1]
        width = len(text.encode("utf-8"))
        pid = uid if len(segs) == 1 else f"{uid}.p{index}"
        span = [cursor, cursor + width]
        cursor += width
        assert SOURCE[span[0]:span[1]].decode("utf-8") == text, (pid, text)
        rec = {"id": pid, "span": span, "source_excerpt": excerpt(text), "parent_unit": entry["parent_unit"], "old_unit": uid}
        if seg[0] == "unf":
            out.append({**rec, "status": "UNFORMALISED", "missing_feature": seg[2], "other_blockers": [], "note": seg[3]})
            if item["kind"] != "ops-fact":
                strict_cursor = skip(item["strict"], strict_cursor, text)
            continue
        if seg[0] == "fact":
            out.append({
                **rec, "status": "OPEN", "kind": "asserted", "open_terms": list(seg[2]),
                "previous_status": entry["status"], "previous_missing_feature": entry.get("missing_feature"),
                "status_in_previous_run": entry["status"], "note": item["note"],
                "case_atoms": {},
                "reading_set": None,
                "readings": [{"id": "ability", "in": "translation.ve.md and readings/all-strict.ve.md",
                              "kind": "asserted", "english": seg[3],
                              "meaning": "no operator and no user is able to unlock a hard constraint (a statement; no norm, no "
                                         "duty on operators or users)"}],
                "audit_repair": REPAIRED_0620[pid],
                "document_status": "OPEN (one reading, an ability statement; the relations are open terms)"})
            continue
        rules, strict_cursor = take(item["strict"], strict_cursor, text)
        out.append({
            **rec, "status": "READINGS", "kind": "norm", "rules": [r["rule"] for r in rules],
            "predicate": "operator_input_permitted",
            "sign": "negative" if not rules[0]["sign"] else "positive",
            "open_terms": list(dict.fromkeys([t for r in rules for t in r["open_terms"]] + item.get("extra_terms", []))),
            "previous_status": entry["status"], "previous_missing_feature": entry.get("missing_feature"),
            "status_in_previous_run": entry["status"], "note": item["note"],
            "case_atoms": {a_: atom_words(main_meta["environment"], a_) for r in rules for a_ in atoms_of(r)},
            "completion": "unspecified",
            "where_the_text_is_silent": silence[rules[0]["predicate"]],
            "reading_set": [rs["id"] for rs in main_meta["reading_sets"] if rs["unit"] == pid][0],
            "readings": [{"id": cid, "kind": kind, "elaborated_in": "readings/all-strict.ve.md" if cid in ("permission", "narrow-permission") else None,
                          "meaning": text_} for cid, kind, text_ in item["candidates"]]
            + [{"id": "permission-rules-english", "elaborated_in": "readings/all-strict.ve.md",
                "english": [eng_nd[r["rule"]]["text"] for r in rules],
                "english_round_trip": all(eng_nd[r["rule"]]["round_trip"] for r in rules)}],
            "document_status": ("OPEN (pending reading set in the main document, candidates without content: readings@1 content "
                                "cannot join norm-defaults@0; the permission candidate is elaborated in readings/all-strict.ve.md "
                                "with the completion `unspecified`)"),
            **({"s1_demonstration_only": {
                "claimed": False,
                "what": "readings/s1.ve.md restates this set with content on the soft chain; it completes the permission predicate "
                        "with `deny` (the source states none) and states ability candidates over an invented relation "
                        "operator_can_supply, so it is a demonstration of the language, not this unit's translation (audit "
                        "20261003T0600Z)",
                "s1": S1_SEPARATION[pid]}} if pid in S1_SEPARATION else {}),
            **({"scoped_by": nd.LIMIT_ATOMS, "scoped_by_source": "u0123.s03"} if rules[0]["sign"] else {}),
            **({"audit_repair": REPAIRED_0620[pid]} if pid in REPAIRED_0620 else
               {"audit_repair": "Not sampled by the 20261002T0620Z audit; it has the same permission shape as u0062.s01 and "
                                "u0123.s02.p1, so it takes the same scope (the limits of u0123.s03 as exceptions)."}
               if pid.startswith("u0123.s01") else {})})
    assert cursor == b, uid
    return out


def skip(segments, index, text):
    done = ""
    while done != text:
        done += segments[index][1]
        index += 1
    return index


def take(segments, index, text):
    done, rules = "", []
    while done != text:
        seg = segments[index]
        done += seg[1]
        index += 1
        if seg[0] == "norm":
            rules.append(seg[2])
    return rules, index


# ------------------------------------------------------------------ metrics helpers
def counts(ledger):
    units = Counter(e["status"] for e in ledger)
    nbytes = Counter()
    for e in ledger:
        nbytes[e["status"]] += e["span"][1] - e["span"][0]
    return units, nbytes


def aggregate(ledger):
    groups = defaultdict(list)
    for e in ledger:
        groups[e["parent_unit"]].append(e)
    units, nbytes = Counter(), Counter()
    for members in groups.values():
        statuses = {m["status"] for m in members}
        units["MIXED" if len(statuses) > 1 else next(iter(statuses))] += 1
        for m in members:
            nbytes[m["status"]] += m["span"][1] - m["span"][0]
    return len(groups), dict(units), dict(nbytes)


def full(counter):
    return {k: counter.get(k, 0) for k in ("CHECKED", "LABELLED", "OPEN", "READINGS", "UNFORMALISED")}


def tally(ledger):
    return dict(Counter(e["missing_feature"] for e in ledger if e["status"] == "UNFORMALISED"))


# ------------------------------------------------------------------ rendering
READING_LINE = re.compile(r"^(One|Another|A third|A fourth|A fifth) reading is: ")


def expand_main(main_text, main_meta, ledger):
    """Replace the renderer's generic reading-set block by what each reading says (companion English)."""
    lines, out = main_text.split("\n"), []
    by_pos = {e["id"]: e for e in ledger if e.get("reading_set")}
    set_units = sorted((u["span"][0], u["id"]) for u in main_meta["units"]
                       if u["id"] in {rs["unit"] for rs in main_meta.get("reading_sets", [])})
    index, i = 0, 0
    while i < len(lines):
        if (lines[i] == "Recorded meaning: The passage is recorded as a rule." and lines[i + 1:i + 2] == ["This sentence could mean:"]):
            j = i + 2
            while j < len(lines) and READING_LINE.match(lines[j]):
                j += 1
            entry = by_pos[set_units[index][1]]
            index += 1
            out.append("Open reading set (ambiguous: all readings kept; each is recorded without content because a candidate norm "
                       "carries none; the elaborated ones are in the companion documents):")
            for reading in entry["readings"]:
                if reading["id"] == "permission-rules-english":
                    for text in reading["english"]:
                        trip = "parses back" if reading["english_round_trip"] else "does not parse back"
                        out.append(f"  elaborated (strict companion, {trip}): {text}")
                    continue
                label = reading["id"]
                if "english" in reading:
                    trip = "parses back to the same rule" if reading["english_round_trip"] else "does not parse back"
                    out.append(f"Reading {label} — English: {reading['english']} [{trip}; completion "
                               f"{reading.get('completion', 'unspecified')}]")
                else:
                    out.append(f"Reading {label}: {reading.get('meaning', '')}")
            atoms = entry.get("case_atoms") or {}
            if atoms:
                out.append("Classifications named above, in the words the environment declares for them (the renderer prints only the "
                           "name; each is an open term whose test the source does not give):")
                for atom, words in atoms.items():
                    out.append(f"  “{atom}”: {words}.")
            if entry.get("where_the_text_is_silent"):
                out.append("Where the text is silent (VE's wording): " + entry['where_the_text_is_silent'][0].upper() + entry['where_the_text_is_silent'][1:] + ".")
            i = j
            continue
        out.append(lines[i])
        i += 1
    assert index == len(set_units), (index, len(set_units))
    return "\n".join(out)


def annotate_hard(text, ledger):
    """Under each one-reading prohibition of the hard constraints, print its source words and VE's two verdicts."""
    lines, out = text.split("\n"), []
    by_english = {e["readings"][0]["english"]: e for e in ledger if e["id"] in HARD}
    for line in lines:
        out.append(line)
        m = re.match(r"^(Open|Checked) reading: (.*)$", line)
        if m and m.group(2) in by_english:
            e = by_english[m.group(2)]
            out.append(f"  Source words of the case (open term “{e['open_terms'][0]}”): "
                       f"{list(e['case_atoms'].values())[0]}.")
            out.append(f"  VE: where the case holds, {e['check']['case holds']}; where it does not, {e['check']['case does not hold']}. "
                       f"{e['where_the_text_is_silent'][0].upper() + e['where_the_text_is_silent'][1:]}.")
    return "\n".join(out)


# ------------------------------------------------------------------ profile probe
def probe_profiles():
    """Add one more profile to the strict companion's environment and record what `ve document check` says."""
    import tempfile
    base = DOCS["strict"].read_bytes()
    end = base.index(b"\n---\n", 4)
    meta, tail = json.loads(base[4:end]), base[end + 5:]
    result = {}
    for extra in ("soft-norms@0", "closure@0", "order@0", "time@0", "reports@0", "alternatives@0", "speech-acts@0",
                  "definitions@0", "data@0", "rights@0", "risk@0", "ve.discourse@1", "readings@1"):
        m = json.loads(json.dumps(meta))
        m["environment"]["profiles"] = sorted(set(m["environment"]["profiles"]) | {extra})
        if extra == "rights@0":
            m["environment"]["vocabulary"]["rights"] = {"holders": ["user"], "bearers": ["claude_instance"], "protected": [], "alters": {}}
        if extra == "ve.discourse@1":
            m["format"] = "ve-document@2"
            m["discourse"] = {"version": "ve.discourse@1", "anchors": [{"id": "doc", "kind": "document", "label": "Claude's constitution", "span": [0, len(SOURCE)]}]}
        with tempfile.NamedTemporaryFile("wb", suffix=".ve.md", delete=False) as handle:
            handle.write(b"---\n" + json.dumps(m, ensure_ascii=False, separators=(",", ":")).encode() + b"\n---\n" + tail)
        proc = subprocess.run([sys.executable, "-m", "ve", "document", "check", handle.name], cwd=ROOT, capture_output=True, text=True)
        Path(handle.name).unlink()
        result[extra] = ("accepted at document-check level" if proc.returncode == 0
                         else (proc.stderr.strip().splitlines() or ["rejected"])[-1].split(": ", 1)[-1])
    return result


def main():
    # ---- VE runs
    results = {}
    for key, path in DOCS.items():
        rel = str(path.relative_to(ROOT))
        results[key] = {"check": json.loads(ve("document", "check", rel)),
                        "coverage": json.loads(ve("document", "coverage", rel)),
                        "render": ve("document", "render", rel)}
    main_meta = front_matter(DOCS["main"])
    soft_meta = front_matter(DOCS["default"])
    dump = lambda p, o: (RUN / p).write_text(json.dumps(o, indent=2, ensure_ascii=False) + "\n")
    dump("check.json", results["main"]["check"])
    dump("coverage.json", results["main"]["coverage"])
    dump("readings/check-all-strict.json", results["strict"]["check"])
    dump("readings/check-all-default.json", results["default"]["check"])
    dump("readings/check-s1.json", results["s1"]["check"])
    dump("readings/coverage-s1.json", results["s1"]["coverage"])
    dump("environment.json", main_meta["environment"])
    dump("readings/environment-all-default.json", soft_meta["environment"])
    for key, name in (("strict", "rendered-all-strict.md"), ("default", "rendered-all-default.md"), ("s1", "rendered-s1.md")):
        (RUN / "readings" / name).write_text(results[key]["render"])
    eng_nd = english_nd(DOCS["strict"])
    eng_soft = english_soft(DOCS["default"])
    dump("readings/english.json", {"strict_norm_defaults": eng_nd, "default_soft_norms": eng_soft})
    silence, legend = silence_sentences(DOCS["strict"])
    probe = json.loads((RUN / "probes/unspecified-probe.json").read_text())

    s1_check = results["s1"]["check"]
    s1_result = json.loads((RUN / "readings/s1-result.json").read_text())
    words_ = {x["set"]: x["source_word"] for x in s1_result["sets"]}

    # ---- ledger
    spec.UNITS_BY_OLD = {u["old"]: u for u in spec.UNITS}
    base_prev = json.load(open(RUN / "prev1001/units.json"))   # the ledger the build starts from (and the audited lineage)
    prev = json.load(open(RUN / "prev1003/units.json"))        # the previous run (20261003T0600Z): what this run is compared with
    separation = separating_situations(results["s1"]["check"], s1_result)
    S1_SEPARATION.update(separation)
    dump("readings/separating-situations.json", separation)
    ledger = new_ledger(base_prev, main_meta, eng_nd, eng_soft, probe, silence, separation)
    prev_by_id0 = {e["id"]: e for e in prev}
    for e in ledger:  # "the previous run" is the 20261003T0600Z run
        old = prev_by_id0.get(e["id"])
        if old is not None:
            e["status_in_previous_run"] = old["status"]
        elif e.get("old_unit") in prev_by_id0:
            e["status_in_previous_run"] = prev_by_id0[e["old_unit"]]["status"] + " (as part of " + e["old_unit"] + ")"
    dump("units.json", ledger)
    total = sum(e["span"][1] - e["span"][0] for e in ledger)
    assert total == len(SOURCE), (total, len(SOURCE))
    pos = 0
    for e in ledger:
        assert e["span"][0] == pos, e["id"]
        pos = e["span"][1]
    # the ledger and the main document tile the same spans, unit for unit
    doc_units = [(u["id"], tuple(u["span"])) for u in main_meta["units"]]
    led_units = [(e["id"], tuple(e["span"])) for e in ledger]
    assert [s for _, s in doc_units] == [s for _, s in led_units], "ledger and document spans differ"

    main_text = results["main"]["render"]
    rendered = annotate_hard(expand_main(main_text, main_meta, ledger), ledger)
    (RUN / "rendered.md").write_text(rendered)
    natural = next(l for l in rendered.split("\n") if l.startswith("Checked reading: Claude is not human"))
    (RUN / "checked-natural.md").write_text(natural.split(": ", 1)[1] + "\n")

    u, nb = counts(ledger)
    prev_u, prev_nb = counts(prev)
    n_old, old_units, old_bytes = aggregate(ledger)
    p_old, p_old_units, p_old_bytes = aggregate(prev)
    claimed = sum(v for k, v in nb.items() if k in COVERED)
    prev_claimed = sum(v for k, v in prev_nb.items() if k in COVERED)
    spans = {e["id"]: e["span"] for e in ledger}
    status = {e["id"]: e["status"] for e in ledger}
    width = lambda ids: sum(spans[i][1] - spans[i][0] for i in ids)
    doc_cov = results["main"]["coverage"]
    assert doc_cov["bytes_by_status"].get("OPEN", 0) == nb["OPEN"] + nb["READINGS"], (doc_cov["bytes_by_status"], dict(nb))
    assert doc_cov["bytes_by_status"].get("CHECKED", 0) == nb["CHECKED"]
    assert doc_cov["bytes_by_status"].get("UNFORMALISED", 0) == nb["UNFORMALISED"]
    assert doc_cov["bytes_by_status"].get("LABELLED", 0) == nb["LABELLED"]

    # ---- what changed against the previous ledger, entry by entry
    strip = lambda e: {k: v for k, v in e.items() if k not in VOLATILE}
    old_by_id = {e["id"]: e for e in prev}
    new_by_id = {e["id"]: e for e in ledger}
    unchanged = sorted(i for i in new_by_id if i in old_by_id and strip(new_by_id[i]) == strip(old_by_id[i]))
    changed = sorted(i for i in old_by_id if i not in new_by_id or strip(new_by_id[i]) != strip(old_by_id[i]))
    added = sorted(i for i in new_by_id if i not in old_by_id)
    upgraded = sorted(i for i in new_by_id if i in old_by_id and status[i] in COVERED and old_by_id[i]["status"] not in COVERED)
    new_covered_from_split = sorted(i for i in added if status[i] in COVERED)
    prev_status = {e["id"]: e["status"] for e in prev}
    prev_status_by_id = prev_status
    parent_prev_status = {}
    for i in added:
        parent_prev_status[i] = prev_status.get(new_by_id[i]["old_unit"])
    gained_bytes = (claimed - prev_claimed)

    # ---- audit-verified: accepted by an audit AND byte-identical (same ledger entry apart from volatile notes, same document unit)
    prev_main = front_matter(RUN / "prev1001/translation.ve.md")
    prev_units = {u["id"]: u for u in prev_main["units"]}
    new_units = {u["id"]: u for u in main_meta["units"]}
    prev_sets = {r["unit"]: r for r in prev_main.get("reading_sets", [])}
    new_sets = {r["unit"]: r for r in main_meta.get("reading_sets", [])}
    why_set = lambda s: [r["admission"]["why"] for r in s["readings"]]

    def core(e):
        """What an audit judges: status, span, rule, open terms and each reading's English; not added metadata."""
        if e["status"] == "LABELLED":
            return strip(e)
        return {"status": e["status"], "span": e["span"], "kind": e.get("kind"), "rule": e.get("rule"),
                "open_terms": e.get("open_terms"),
                "readings": {r["id"]: r.get("english") for r in e.get("readings", [])}}

    audit_by_id = {e["id"]: e for e in base_prev}   # the audited lineage (the ledger the build starts from)

    def same(i):
        if i not in audit_by_id or i not in new_by_id or core(new_by_id[i]) != core(audit_by_id[i]):
            return False
        if prev_units.get(i) != new_units.get(i):
            return False
        if (i in prev_sets) != (i in new_sets):
            return False
        return i not in prev_sets or why_set(prev_sets[i]) == why_set(new_sets[i])

    p1003_by_id = {e["id"]: e for e in prev}
    p1003_main = front_matter(RUN / "prev1003/translation.ve.md")
    p1003_units = {u["id"]: u for u in p1003_main["units"]}
    p1003_sets = {r["unit"]: r for r in p1003_main.get("reading_sets", [])}

    def same_1003(i):
        """Byte-identical to the form the 20261003T0600Z audit saw (ledger core, document unit, reading-set text)."""
        if i not in p1003_by_id or i not in new_by_id or core(new_by_id[i]) != core(p1003_by_id[i]):
            return False
        if p1003_units.get(i) != new_units.get(i) or (i in p1003_sets) != (i in new_sets):
            return False
        return i not in p1003_sets or why_set(p1003_sets[i]) == why_set(new_sets[i])

    rejected = set(AUDIT_REJECTED_1001) | set(AUDIT_REJECTED_0620) | set(AUDIT_REJECTED_1800) | set(AUDIT_REJECTED_1003)
    cand_sub = [i for i in AUDIT_PASSED_SUBSTANTIVE if i not in rejected]
    cand_lab = list(AUDIT_PASSED_LABELLED)
    verified_sub = [i for i in cand_sub if i in new_by_id and status[i] in COVERED and same(i)]
    verified_lab = [i for i in cand_lab if i in new_by_id and status[i] in COVERED and same(i)]
    newly_verified_sub = [i for i in AUDIT_PASSED_1003_SUBSTANTIVE if i in new_by_id and status[i] in COVERED and same_1003(i)
                          and i not in verified_sub]
    newly_verified_lab = [i for i in AUDIT_PASSED_1003_LABELLED if i in new_by_id and status[i] in COVERED and same_1003(i)
                          and i not in verified_lab]
    assert not newly_verified_lab, newly_verified_lab        # every accepted label unit was already in the lineage's list
    assert len(newly_verified_sub) == len(set(AUDIT_PASSED_1003_SUBSTANTIVE) - set(verified_sub)), "an accepted unit changed"
    verified_sub = verified_sub + newly_verified_sub
    rejected = rejected - set(newly_verified_sub)           # a later acceptance supersedes an earlier rejection
    dropped = sorted(set(cand_sub) - set(verified_sub))
    # the one the audit accepted before but this run's audit rejected
    rejected_now_unverified = sorted(set(AUDIT_PASSED_SUBSTANTIVE) & rejected)
    verified_sub_bytes, verified_lab_bytes = width(verified_sub), width(verified_lab)
    repaired_bytes = width(sorted(set(REPAIRED_THIS_RUN + REPAIRED_EARLIER_NOT_REAUDITED + REPAIRED_THIS_RUN_1800 + REPAIRED_THIS_RUN_0600 + REPAIRED_NOW) - set(verified_sub) - {i for i in status if status[i] not in COVERED}))
    prev_metrics = json.load(open(RUN / "prev1003/metrics.json"))
    # the units the 20261003T0600Z audit rejected that were verified before leave the verified list
    left_verified = [i for i in prev_metrics["audit_verified_covered_units"] if i in AUDIT_REJECTED_1003]
    assert verified_sub_bytes == prev_metrics["audit_verified_covered_bytes"] - width(left_verified) + width(newly_verified_sub), (
        verified_sub_bytes, prev_metrics["audit_verified_covered_bytes"], left_verified, newly_verified_sub)
    assert verified_lab_bytes == prev_metrics["audit_verified_metadata_bytes"], (verified_lab_bytes, prev_metrics["audit_verified_metadata_bytes"])
    repaired_1800_bytes = width(REPAIRED_THIS_RUN_1800)
    repaired_0600_bytes = width(REPAIRED_THIS_RUN_0600)

    # ---- probes of the unspecified route
    undecided_points = sum(1 for p in probe["points"] if p["status"] == "UNDECIDED")
    settled_points = sum(1 for p in probe["points"] if p["status"].startswith("SETTLED"))
    conflict_points = sum(1 for p in probe["points"] if p["status"].startswith("CONFLICT"))

    regulated = {name: {"role": p["regulated"]["role"], "default": p["regulated"]["default"], "arguments": p["arguments"]}
                 for name, p in main_meta["environment"]["vocabulary"]["predicates"].items() if "regulated" in p}
    assert all(r["default"] == "unspecified" for r in regulated.values()), "a completion other than unspecified in the main document"
    soft_regulated = {name: {"role": p["regulated"]["role"], "default": p["regulated"]["default"], "arguments": p["arguments"]}
                      for name, p in soft_meta["environment"]["vocabulary"]["predicates"].items() if "regulated" in p}
    nd_parties = sorted({r["arguments"][0] for r in regulated.values()})

    metrics = {
        "run": RUN_ID, "baseline_tag": "ve-green-env-profiles", "previous_run": PREV_RUN, "previous_baseline_tag": "ve-green-wire-s4",
        "source_sha256": hashlib.sha256(SOURCE).hexdigest(), "source_bytes": len(SOURCE),
        "bytes_accounted": total, "bytes_accounted_percent": round(100 * total / len(SOURCE), 4),
        "sentence_clause_units": {"units_total": len(ledger), "unit_counts_by_status": full(u), "bytes_by_status": full(nb),
                                  "previous_run": {"units_total": len(prev), "unit_counts_by_status": full(prev_u),
                                                   "bytes_by_status": full(prev_nb)}},
        "aggregated_to_previous_boundaries": {"units_total": n_old, "unit_counts_by_status": old_units,
                                              "bytes_by_substatus": full(nb),
                                              "previous_run": {"units_total": p_old, "unit_counts_by_status": p_old_units}},
        "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(SOURCE), 4),
        "claimed_covered_bytes_previous_run": prev_claimed,
        "claimed_covered_bytes_gained": gained_bytes,
        "substantive_covered_bytes": sum(v for k, v in nb.items() if k in ("CHECKED", "OPEN", "READINGS")),
        "substantive_covered_bytes_previous_run": sum(v for k, v in prev_nb.items() if k in ("CHECKED", "OPEN", "READINGS")),
        "audit_verified_covered_bytes": verified_sub_bytes,
        "audit_verified_covered_percent": round(100 * verified_sub_bytes / len(SOURCE), 4),
        "audit_verified_covered_units": verified_sub,
        "audit_verified_covered_bytes_previous_run": prev_metrics["audit_verified_covered_bytes"],
        "audit_verified_metadata_bytes": verified_lab_bytes,
        "audit_verified_metadata_percent": round(100 * verified_lab_bytes / len(SOURCE), 4),
        "audit_verified_metadata_bytes_previous_run": prev_metrics["audit_verified_metadata_bytes"],
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND byte-identical in this run (the same "
            "ledger entry apart from volatile notes, the same document unit, the same reading-set admission text). The latest "
            "audit (20261003T0600Z, 14/20) rejected six units; of those, u0036.s05, u0263.s04.p2 and u0078.s01 were verified before, "
            "so they leave the verified list. Unlike the earlier audits it lists a verdict for every sampled unit, so its 14 "
            "acceptances are identified: the six substantive ones not yet in the list (u0165.s01, s02, s05, s06, s07 and "
            "u0166.s04.p4, each byte-identical to the 20261003T0600Z form) join it, superseding their earlier rejections; its "
            "label units were already in the list. finish.py asserts: previous verified bytes, minus the three that left, plus "
            "the six that joined. The six rejected units are rewritten or demoted in this run (claimed, not verified, until the "
            "next audit)."),
        "audit_verified_newly_from_20261003T0600Z": newly_verified_sub,
        "audit_verified_dropped_because_changed_or_rejected": {"changed_since_acceptance": dropped,
                                                               "rejected_by_an_audit_and_not_re_accepted": rejected_now_unverified},
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20261003T0600Z_audit": AUDIT_REJECTED_1003,
            "repaired_in_20261004T0600Z": {i: {"status_before": prev_status_by_id.get(i), "status_now": status[i],
                                               "repair": REPAIRED_1003[i]} for i in REPAIRED_NOW},
            "repaired_in_20261004T0600Z_bytes": width(REPAIRED_NOW),
            "rejected_by_20261002T1800Z_audit": AUDIT_REJECTED_1800,
            "repaired_in_20261003T0600Z": {i: {"status_before": prev_status_by_id.get(i), "status_now": status[i],
                                               "repair": REPAIRED_1800[i]} for i in REPAIRED_THIS_RUN_0600},
            "repaired_in_20261003T0600Z_bytes": repaired_0600_bytes,
            "rejected_by_20261002T0620Z_audit": AUDIT_REJECTED_0620,
            "repaired_in_20261002T1800Z": {i: {"status_before": prev_status_by_id.get(i), "status_now": status[i],
                                               "repair": REPAIRED_0620.get(i, "same scope as the three rejected units")}
                                           for i in REPAIRED_THIS_RUN_1800},
            "repaired_in_20261002T1800Z_bytes": repaired_1800_bytes,
            "rejected_by_20261001T1800Z_audit": AUDIT_REJECTED_1001,
            "rejected_by_earlier_audits": AUDIT_REJECTED_EARLIER,
            "repaired_in_20261002T0620Z": REPAIRED_THIS_RUN,
            "repair": "the defeasible candidate is removed (it contradicts u0166.s01 and u0166.s04); one strict reading carries "
                      "the prohibition as content; the same shape in u0165.s01, s03, s05 and s07 is repaired with the three "
                      "the audit sampled",
            "repaired_earlier_not_re_audited": REPAIRED_EARLIER_NOT_REAUDITED,
            "status_now": {i: status[i] for i in REPAIRED_THIS_RUN + REPAIRED_EARLIER_NOT_REAUDITED + REPAIRED_THIS_RUN_1800
                           + REPAIRED_THIS_RUN_0600 + REPAIRED_NOW},
            "counted_as_audit_verified": False,
            "counted_as_audit_verified_20261002T0620Z_rejections": False,
            "any_unit_rejected_keeps_covered_status_without_repair": False},
        "claimed_but_not_audit_verified_bytes": claimed - verified_sub_bytes - verified_lab_bytes,
        "repaired_bytes_not_audit_verified": repaired_bytes,
        "documents": {k: str(v.relative_to(RUN)) for k, v in DOCS.items()},
        "document_profiles": {k: front_matter(v)["environment"]["profiles"] for k, v in DOCS.items()},
        "open_terms": [{k: t[k] for k in ("name", "arguments", "decided_by", "necessary", "sufficient", "factors")}
                       for t in main_meta["open_terms"]],
        "open_terms_count": len(main_meta["open_terms"]),
        "open_terms_count_previous_run": prev_metrics["open_terms_count"],
        "reading_sets": {
            "count": len(main_meta["reading_sets"]), "unresolved": len(main_meta["reading_sets"]),
            "candidates": {rs["unit"]: [r["id"] for r in rs["readings"]] for rs in main_meta["reading_sets"]},
            "units": [rs["unit"] for rs in main_meta["reading_sets"]],
            "narrowings": [], "narrowings_note": "none: the seven hard constraints and u0168.s01 are no longer reading sets (one strict "
                                                 "reading from cited spans), so no narrowing is left that is recorded but not binding",
            "count_previous_run": prev_metrics["reading_sets"]["count"]},
        "missing_feature_tally": tally(ledger), "missing_feature_tally_previous_run": tally(prev),
        "heading_presuppositions_exposed": sum(1 for e in ledger if e["id"].endswith(".presupposition")),
        "check_verdicts": {
            "main": {"document_loaded": True, "coverage_percent": doc_cov["coverage_percent"],
                     "premises": results["main"]["check"]["premises"], "reading_plan": results["main"]["check"]["reading_plan"],
                     "residual": doc_cov["residual"], "norm_defaults": doc_cov.get("norm_defaults")},
            "all_strict": {"premises": results["strict"]["check"]["premises"],
                           "residual": results["strict"]["coverage"]["residual"],
                           "bytes_by_status": results["strict"]["coverage"]["bytes_by_status"],
                           "norm_defaults": results["strict"]["coverage"].get("norm_defaults")},
            "s1": {"premises": results["s1"]["check"]["premises"], "readings": {
                       k: v for k, v in results["s1"]["check"]["readings"].items() if k in ("separations", "findings")},
                   "residual": results["s1"]["coverage"]["residual"],
                   "bytes_by_status": results["s1"]["coverage"]["bytes_by_status"]},
            "all_default": {"premises": results["default"]["check"]["premises"],
                            "residual": results["default"]["coverage"]["residual"],
                            "bytes_by_status": results["default"]["coverage"]["bytes_by_status"],
                            "default_exceptions_by_decider": results["default"]["coverage"].get("default_exceptions_by_decider")},
            "english_export": {"strict_rules": len(eng_nd), "strict_round_trip": sum(v["round_trip"] for v in eng_nd.values()),
                               "strict_not_round_tripping": sorted(n for n, x in eng_nd.items() if not x["round_trip"]),
                               "default_rules": len(eng_soft), "default_round_trip": sum(v["round_trip"] for v in eng_soft.values()),
                               "default_not_round_tripping": sorted(n for n, x in eng_soft.items() if not x["round_trip"])},
            "natural_render_checked_clause": (RUN / "checked-natural.md").read_text().strip()},
        "unspecified_probe": {
            "file": "probes/unspecified-probe.json", "document": probe["document"],
            "points_asked": len(probe["points"]), "undecided": undecided_points, "settled": settled_points,
            "conflict": conflict_points,
            "conflict_reports": probe["conflict"],
            "gaps": {p: g["reached"] for p, g in probe["gaps"].items()},
            "note": "VE's own verdicts on one-element situations chosen by probe_unspecified.py. Each of the seven hard constraints "
                    "is SETTLED no (Claude may not) where its case atom holds and UNDECIDED (the text does not say) where it does "
                    "not; no default permits or forbids anything the source does not state."},
        "regulated_predicates": regulated,
        "no_invented_permissions": {
            "regulated_predicates": len(regulated),
            "permission_predicates": sorted(n for n, r in regulated.items() if r["role"] == "permission"),
            "obligation_predicates": sorted(n for n, r in regulated.items() if r["role"] == "obligation"),
            "completions": sorted({r["default"] for r in regulated.values()}),
            "predicates_with_default_allow": 0, "predicates_with_default_deny": 0,
            "first_arguments_of_regulated_predicates": nd_parties,
            "every_party_is_one_the_source_names": True,
            "soft_companion_completions": sorted({r["default"] for r in soft_regulated.values()}),
            "s1_companion_completions": sorted({p["regulated"]["default"] for p in front_matter(DOCS["s1"])["environment"]["vocabulary"]["predicates"].values()
                                               if "regulated" in p}),
            "s1_companion_note": "readings/s1.ve.md completes the duties and the operator permission operator_input_permitted with deny: "
                                 "the soft route needs a completion and readings@1 content cannot join norm-defaults@0; the source "
                                 "states none. Since the 20261003T0600Z audit (companion `deny` completions say “not required” outside "
                                 "the stated conditions) this document is a demonstration of the language only: no unit's status, "
                                 "coverage or fidelity is claimed from it",
            "soft_companion_note": "readings/all-default.ve.md completes every duty with deny (“not required”), because "
                                   "norm-defaults@0 cannot share a document with soft-norms@0; demonstration only since the "
                                   "20261003T0600Z audit, nothing is claimed from it",
            "demonstration_documents_not_part_of_the_translation": ["readings/s1.ve.md", "readings/all-default.ve.md"],
            "note": "In the main document and the strict companion every completion is `unspecified`: where no rule decides, VE "
                    "reports UNDECIDED. A prohibition on Claude no longer makes anything permitted for another party, and no "
                    "duty is completed to “not required”. The party of every regulated predicate is a sort the source names "
                    "(instances of Claude, operators, users)."},
        "profile_combination_probe": probe_profiles(),
        "separating_situations": {"reading_sets": len(separation), "all_checked_by_lean": True,
                                  "file": "readings/separating-situations.json",
                                  "claimed": False,
                                  "note": "Lean-checked situations of readings/s1.ve.md (composition S1), a demonstration document: it completes "
                                          "duties and the operator permission with `deny`, which the source does not state (audit "
                                          "20261003T0600Z), so no unit's separation is claimed from it"},
        "s1": {
            "document": "readings/s1.ve.md", "profiles": front_matter(DOCS["s1"])["environment"]["profiles"],
            "demonstration_only": True,
            "demonstration_note": "Not part of the translation and not counted in any claim: its completion `deny` is an invention (audit "
                                  "20261003T0600Z rejected the units that relied on it). It stays to show what readings@1 does at this tag.",
            "what": "the force-ambiguous units as content-bearing reading sets: each set has two contents, the default rule and its "
                    "strict twin; one situation per pair, found by Python's search from the guard base, checked by Lean when the "
                    "document loads (Python regenerates Lean's answer, Rust replays the situation)",
            "content_bearing_sets": len(s1_check["readings"]["sets"]),
            "sets": {s["unit"]: {"set": s["set"], "source_word": words_.get(s["set"]),
                                 "candidates": [c["id"] for c in s["candidates"]],
                                 "pairs": [{"readings": p["readings"], "probe": p["probe"], "wording": p["wording"]}
                                           for p in s["pairs"]],
                                 "findings": s["findings"]} for s in s1_check["readings"]["sets"]},
            "separations": s1_check["readings"].get("separations"), "findings": s1_check["readings"].get("findings"),
            "wordings": dict(Counter(p["wording"] for s in s1_check["readings"]["sets"] for p in s["pairs"])),
            "not_certified": [f for s in s1_check["readings"]["sets"] for f in s["not_certified"]],
            "pairs_without_situation": s1_result["pairs_without_situation"], "search_limits": s1_result["search_limits"],
            "search_seconds": s1_result["search_seconds"], "load_seconds": s1_result["load_seconds"],
            "premises": s1_check["premises"],
            "bytes_by_status": results["s1"]["coverage"]["bytes_by_status"],
            "units_stated_in_duty_form_with_deny": ["u0125.s04.p2", "u0156.s03"],
            "operator_sets": {
                "units": ["u0062.s01", "u0123.s01.p1", "u0123.s02.p1", "u0123.s03"],
                "restated_as": "one rule per candidate (a candidate is one content): the several permission rules of the main document "
                               "become one rule with a disjunctive guard; ability candidates are assertions over operator_can_supply",
                "invented_completion": "operator_input_permitted completes with deny on the soft chain (not the source's); outcome "
                                       "probes between a permission and an ability candidate rest on it, `holds` and `selects` probes do not"},
            "main_document_keeps_the_sets_pending": True,
            "probe": json.loads((RUN / "probes/s1-probe.json").read_text()),
            "unchanged_by_s1": "S1 adds no status and no verdict: every unit keeps its status, the document premise is UNKNOWN "
                               "(superposition pending), and no reading set is resolved (verdicts across readings are S2's)"},
        "changes_against_previous_run": {
            "ledger_entries_previous": len(prev), "ledger_entries_now": len(ledger),
            "unchanged_entries": len(unchanged), "changed_or_replaced_ids": changed, "added_ids": added,
            "units_newly_covered": [i for i in added if status[i] in COVERED],
            "units_newly_covered_parent_previous_status": {i: parent_prev_status[i] for i in added if status[i] in COVERED},
            "units_with_status_change": sorted(i for i in new_by_id if i in old_by_id and status[i] != old_by_id[i]["status"]),
            "reason": ("no language change between the tags (below); the ledger changes only where the 20261003T0600Z audit rejected a "
                       "unit: u0078.s01 READINGS to UNFORMALISED (other:graded-force), u0073.s05 READINGS to OPEN (one reading in "
                       "norm-defaults@0, completion `unspecified`), and the notes of the other five units, which no longer cite the "
                       "demonstration companions as their elaboration")},
        "language_changes_since_previous_tag": {
            "from": "ve-green-wire-s4", "to": "ve-green-env-profiles",
            "git_diff_ve_files": "16 files in ve/ (281 insertions, 121 deletions): environment type checks and the read order of "
                                 "environment fields (ve/environment.py, ve/profiles.py, ve/rights.py, ve/speech_acts.py, ve/ast.py, "
                                 "ve/document.py and small ones); no change under lean/",
            "merged": {
                "fix/env-field-types (env-profiles)": "every top-level environment field is type-checked before use; wrong-typed fields "
                                                      "give the Lean route's diagnostic on every route; no new form of text",
                "infra/layers2-b1": "Rust module check, kernel wire tag tables replace registry reads; internal",
                "Lean": "unchanged"},
            "newly_expressible_features": 0,
            "newly_expressible": "nothing",
            "units_upgraded_by_new_features": 0,
            "why_no_unit_changed_status": "no merged feature adds a form of text, a status or a profile; the one status that rises "
                                          "(u0073.s05, READINGS to OPEN) uses norm-defaults@0 as merged at the previous tag, and the one "
                                          "that falls (u0078.s01) is the audit's repair",
            "profile_combination_result": "see profile_combination_probe and s1.probe (unchanged)"},
        "conflict_finding": {
            "previous_run_reported": "a checked CONFLICT between u0123.s02 and u0123.s03 on an input that is both a persona role-play "
                                     "instruction and an instruction to claim to be human",
            "status_now": "retracted as a finding: the 20261002T0620Z audit rejected the unscoped permission reading it came from "
                          "(u0062.s01, u0123.s02.p1), so no auditor accepted both readings",
            "after_scoping": "VE settles that input as `no` (not permitted), reports no conflict at the witness situations, and its "
                             "whole-document proof attempt returns CONFLICT-FREE (it was UNKNOWN before)"},
        "legend_sentences": legend,
    }
    assert set(changed) | set(added) | set(unchanged) == set(old_by_id) | set(new_by_id)
    metrics["risk_probe"] = json.loads((RUN / "probes/risk-probe.json").read_text())
    metrics["discourse_probe"] = json.loads((RUN / "probes/discourse-probe.json").read_text())
    metrics["rights_reading_probe"] = json.loads((RUN / "probes/rights-reading-probe.json").read_text())
    metrics["carried_probes_note"] = ("risk, discourse and rights probes re-run at ve-green-env-profiles (probe_risk.py, "
                                      "probe_discourse.py, probe_rights.py); the risk and S1 probes are byte-identical to the previous "
                                      "run's, the discourse probe differs only in the unit named in its message (the first unit with a "
                                      "slot is now u0123.s02.p1, u0078.s01 being UNFORMALISED), the rights probe only in model ids and "
                                      "in one predicate name; the findings are the same")
    (RUN / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: metrics[k] for k in ("sentence_clause_units", "aggregated_to_previous_boundaries", "claimed_covered_bytes",
                                                "claimed_covered_percent", "claimed_covered_bytes_gained",
                                                "audit_verified_covered_bytes", "audit_verified_metadata_bytes",
                                                "missing_feature_tally", "missing_feature_tally_previous_run")}, indent=1))
    print(json.dumps(metrics["changes_against_previous_run"], indent=1)[:3000])
    print(json.dumps(metrics["profile_combination_probe"], indent=1))
    print(dropped, rejected_now_unverified)


if __name__ == "__main__":
    main()
