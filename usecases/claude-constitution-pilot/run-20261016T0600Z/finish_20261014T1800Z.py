#!/usr/bin/env python3
"""Run 20261014T1800Z: AT-0p (hard-constraint guards bound to the acting Claude instance), the repairs of the units the audit of run 20261013T0600Z rejected,
the scope tally (SC-M0) and the act-workaround tags (AP-0 item 3); then the measurement at ve-green-repo-map-untracked.

Order (repository root, PATH must contain ~/.elan/bin, VE_NATIVE_PREBUILT=1; `lake build` in lean/ and tools/rust_build.py done):
    uv run python .../repair_20261014T1800Z.py            # base/ -> translation-without-content.ve.md, readings/all-strict.ve.md, readings/all-strict-narrow.ve.md
    uv run python .../nd.py all                           # about 2 min; then: cp readings/nd-all.ve.md translation.ve.md
    uv run python -m ve document coverage .../translation.ve.md > .../readings/coverage-nd-all.json
    probes (README.md)
    uv run python .../finish_20261014T1800Z.py            # ledger (units.json), scope-tally.json, renderings, check, coverage, metrics.json

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
import finish_20261013T0600Z as p13  # noqa: E402  (the previous run's notes, to replace exactly)
import s03_scope as sc  # noqa: E402
import scope_tally  # noqa: E402
import spec_nd  # noqa: E402

RUN_ID = "20261014T1800Z"
PREV_RUN = "20261013T0600Z"
TAG = "ve-green-repo-map-untracked"
PREV_TAG = "ve-green-eff-20261011-1"
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
# changed units: the seven hard constraints (plan repair AT-0p, and u0165.s03 also an audit repair), u0123.s02.p1 (audit repair), u0173.s01 (note only)
PLAN_REPAIRS = [{"unit": u, "plan": "attitudes", "item": "AT-0p"} for u in HC_UNITS]
AUDIT_REPAIRS = [{"unit": S03, "audit": "20261013T0600Z", "what": "the two attachments of “that could cause significant damage if deployed” are now a reading set of two candidates"},
                 {"unit": U0123, "audit": "20261013T0600Z", "what": "the open term for the operator's own products now binds the operator (a pair of an operator and an input)"}]
CHANGED = [*HC_UNITS, U0123, U0173]

# the audit of run 20261013T0600Z (14/20 sampled faithful + 1/8 changed faithful), verdicts as received (AUDIT-20261013T0600Z-received.md)
AUDIT_1013_FAITHFUL = ["u0023", "u0036.s05", "u0042.heading", "u0055.heading", "u0108", "u0123.s01.p1", "u0125.s04.p2", "u0156.s03", "u0173.s01", "u0248",
                       "u0263.s04.p2", "u0265", "u0268.heading", "u0277", "u0282"]
AUDIT_1013_UNFAITHFUL = [*HC_UNITS, U0123]

import os  # noqa: E402
HARD_PROBE = Path(os.environ.get("VE_PILOT_HARD_PROBE", RUN / "probes/hard-conclusions-probe.json"))  # a debugging override only
KNOW = "knowingly_engages_"
THINK = "thinks_quite_likely_"

HC_NOTE_NEW = (
    " Epistemic condition (audit 20261012T0600Z, repaired again after audits 20261012T1800Z and 20261013T0600Z): u0173.s01 to s04 qualify the list. The hard "
    "constraints are “centrally meant to apply to cases where Claude would either be knowingly and intentionally engaging in an action of the relevant "
    "restricted category, or where Claude thinks it quite likely that a given action would fall into such a category” (u0173.s01): two alternatives, both "
    "about the Claude that acts. “For cases that are more unclear or uncertain” Claude is to be “guided by the more holistic and nuanced prioritization at "
    "stake in the rest of this document” (u0173.s02); the restriction is “the operative consideration only in a small number of flagrant cases” (u0173.s03); "
    "and Claude “could in principle end up contributing unknowingly to the sorts of outcomes the constraints aim to avoid … without actually violating one of "
    "the constraints” (u0173.s04). So the guard of the rule is ( C(s) and " + KNOW + "N(c, s) ) or " + THINK + "N(c, s), where c is the instance of Claude "
    "the rule regulates (variable 1) and s the situation (variable 0): C is the category's case atom, kept explicit because with untyped terms VE cannot know "
    "that knowingly and intentionally engaging in an action of the category implies the category; " + KNOW + "N is the first alternative and " + THINK +
    "N the second, each a pair of an instance and a situation (an open term). The second is that instance's belief, which need not be correct, so it does not "
    "need C. Because the terms bind the acting instance, one instance's knowledge or belief does not count against another: the source says Claude “can run as "
    "multiple instances simultaneously” (u0249). “Centrally” is a hedge: the cases outside the two alternatives are left to u0173.s02's holistic judgment, "
    "not decided here. Where the guard does not hold the rule says nothing (completion `unspecified`): an unclear, uncertain or unknowing case is neither "
    "forbidden nor permitted by it. u0173.s01 to s04 stay UNFORMALISED (modality/belief; “quite likely” is a quantity); they are used, not claimed.")
CASE_LABEL_OLD = p13.CASE_LABEL_NEW
CASE_LABEL_NEW = "is only a label for the case; the source’s own words for it are the case atom and the two open terms of the guard."
HC_REPAIR_PAST = (
    "Audit 20261012T1800Z (u0165.s01 to s07 all UNFAITHFUL: the repaired guard required actual category membership together with the epistemic condition, but "
    "u0173.s01 also covers actions Claude thinks quite likely to fall into the category, and that belief need not be correct). Repaired in run 20261013T0600Z as "
    "one flat “either … or …” of two open terms of the situation alone; the audit of that run rejected this form (next entry).")
HC_REPAIR_AT0P = (
    "Audit 20261013T0600Z (u0165.s01 to s07 all UNFAITHFUL: both guard terms took only the situation, so neither bound the regulated instance of Claude and one "
    "instance's knowledge or belief counted against every instance). Repaired as the plan-directed repair AT-0p (attitudes plan, DRI AT2): the guard is "
    "( C(s) and " + KNOW + "N(c, s) ) or " + THINK + "N(c, s), two binary open terms on (claude_instance, situation) per rule; the category's case atom is restored "
    "and the previous run's unary terms are removed with every trace (vocabulary, open terms, stored relations, notes). Not audited.")
HC_REPAIR_S03 = (
    " Audit 20261013T0600Z (u0165.s03 additionally): whether “that could cause significant damage if deployed” follows both nouns or only “malicious code” was "
    "only an open-term factor, so the single recorded reading did not represent the two attachments the English admits. Repaired: the category is three case atoms "
    "(a cyberweapon, malicious code, could cause significant damage if deployed) and the rule is a reading set scope-u0165-s03 of two candidates, wide "
    "((cyberweapon or malicious code) and damage) and narrow (cyberweapon or (malicious code and damage)), each a full rule (s03_scope.py); Lean separated them "
    "and checked all 16 choices of the four sets. Not audited.")
S03_NOTE = (
    " Scope of the relative clause (audit 20261013T0600Z): “Create cyberweapons or malicious code that could cause significant damage if deployed” admits two "
    "attachments of “that could cause significant damage if deployed”: to both nouns (wide: a cyberweapon too must be one that could cause significant damage) "
    "or to “malicious code” only (narrow: every cyberweapon is covered). Both are candidates of the reading set scope-u0165-s03; VE does not choose. "
    "The open term for the old single category is gone with every trace; its three parts are the open terms " + ", ".join(sc.ATOMS) + ".")
U0123_NOTE_ADD = (
    " Audit 20261013T0600Z (UNFAITHFUL): the open term for the promote-products instruction took only the input, so once an input qualified the permission "
    "applied to every operator and lost the binding of “the operator’s own products”. Repaired: instruction_promote_own_products is a pair of an operator and an "
    "input (the operator who gives the input promotes its own products and services rather than those of competitors), and the guard of the rule uses it with the "
    "operator the permission is about (variable 1) and the input (variable 0). The probe with two operators: SETTLED yes for the operator who gave the "
    "instruction, UNDECIDED for the other operator.")
U0123_REPAIR_ADD = (
    "Audit 20261013T0600Z (u0123.s02.p1 UNFAITHFUL: `instruction_promote_own_products(input)` omitted the operator argument and so granted the permission beyond the "
    "stated ownership condition). Repaired: the term is binary on (operator, operator_input); the wording is “{0} gives {1}, which is an instruction to promote its "
    "own products and services rather than those of competitors” (a wording that starts with {1} is refused by VE's English reader, which then fails on an "
    "unrelated sentence: a finding about the language). Not audited.")
U0173_NOTE = ("Not claimed. Its words are used by the guards of the seven hard-constraint rules (u0165.s01 to u0165.s07): for each category its first "
              "alternative is the open term " + KNOW + "N and its second the open term " + THINK + "N, each a pair of the acting instance of Claude and a situation; "
              "the unit itself stays UNFORMALISED because knowing, intending and thinking something quite likely are not typed (modality/belief) and “quite "
              "likely” is a quantity.")


def words_of(unit):
    return PER_UNIT[unit][1]


def category_of(unit):
    words = words_of(unit)
    return words[len("Claude "):]


def update_ledger(prev, eng, eng_narrow, silence, probe, scope_probe, binding):
    ledger = copy.deepcopy(prev)
    pts = {p["label"]: p["status"] for p in probe["points"]}
    sp = {p["label"]: p["status"] for p in scope_probe}
    bp = {p["label"]: p["status"] for p in binding}
    for e in ledger:
        i = e["id"]
        e["status_in_previous_run"] = next(x for x in prev if x["id"] == i)["status"]
        if i in HC_UNITS:
            n = int(i[-1])
            case, words, pred = PER_UNIT[i]
            assert e["status"] == "OPEN" and len(e["open_terms"]) == 2 and e["open_terms"][0].startswith("knowingly_"), i
            rule = e["rule"]
            x, b = f"{KNOW}{n}", f"{THINK}{n}"
            cat = category_of(i)
            if i == S03:
                parts = list(sc.ATOMS)
                e["open_terms"] = [*parts, x, b]
                e["case_atoms"] = {
                    sc.CYBERWEAPON: "the situation is a case of Claude creating a cyberweapon",
                    sc.MALICIOUS_CODE: "the situation is a case of Claude creating malicious code",
                    sc.DAMAGE: "in the situation, what Claude creates could cause significant damage if deployed"}
            else:
                e["open_terms"] = [case, x, b]
                e["case_atoms"] = {case: f"the situation is a case of {words}"}
            e["case_atoms"][x] = (f"the instance of Claude knowingly and intentionally engages in the action of the situation as an action of the category: {cat} "
                                  "(u0173.s01, first alternative; a pair of an instance and a situation)")
            e["case_atoms"][b] = (f"the instance of Claude thinks it quite likely that the action of the situation falls into the category: {cat} "
                                  "(u0173.s01, second alternative; that instance's belief, which need not be correct)")
            assert e["note"].endswith(p13.HC_ADD), i
            e["note"] = e["note"][:-len(p13.HC_ADD)] + HC_NOTE_NEW + (S03_NOTE if i == S03 else "")
            assert CASE_LABEL_OLD in e["note"], i
            e["note"] = e["note"].replace(CASE_LABEL_OLD, CASE_LABEL_NEW)
            assert p13.HC_REPAIR_NEW in e["audit_repair"], i
            e["audit_repair"] = e["audit_repair"].replace(p13.HC_REPAIR_NEW, HC_REPAIR_PAST) + " | " + HC_REPAIR_AT0P + (HC_REPAIR_S03 if i == S03 else "")
            e["repaired_in_run"] = RUN_ID
            e["audit_verified"] = False
            e["where_the_text_is_silent"] = silence[pred]
            lab = lambda s: f"{i}: {s}"
            e["check"] = {
                "the case does not hold, Claude thinks it quite likely that the action falls into the category":
                    pts[lab("the case does not hold, Claude thinks it quite likely that the action falls into the category")],
                "the case holds, Claude knowingly and intentionally engages in it": pts[lab("the case holds, Claude knowingly and intentionally engages in it")],
                "neither (an unclear, uncertain or unknowing case)": pts[lab("neither (an unclear, uncertain or unknowing case)")],
                "the case does not hold, Claude knowingly and intentionally engages in it": pts[lab("the case does not hold, Claude knowingly and intentionally engages in it")],
                "meaning": "SETTLED no = the text says Claude may not; UNDECIDED = the text does not say (nothing is permitted or forbidden by default)"}
            r0 = e["readings"][0]
            r0["meaning"] = ("a strict rule: Claude may not do the act in a situation if the case holds and this instance of Claude knowingly and intentionally engages in it, "
                             "or if this instance of Claude thinks it quite likely that the action falls into that category (u0173.s01's two alternatives; the second need not be correct)")
            if i == S03:
                e["status"] = "READINGS"
                e["reading_set"] = sc.SET_ID
                e["readings"] = []
                for rid, text, meaning in (("wide", eng["hc-cyberweapons"], "the clause follows both nouns: a cyberweapon too must be one that could cause significant damage if deployed"),
                                           ("narrow", eng_narrow["hc-cyberweapons"], "the clause follows only “malicious code”: every cyberweapon is covered")):
                    e["readings"].append({"id": rid, "elaborated_in": "translation.ve.md (content); " + ("readings/all-strict.ve.md" if rid == "wide" else "readings/all-strict-narrow.ve.md") + " (the rule alone)",
                                          "predicate": pred, "completion": "unspecified", "english": text["text"], "english_round_trip": text["round_trip"],
                                          "english_round_trip_error": text["error"], "meaning": meaning})
                e["document_status"] = ("READINGS: an open reading set whose two candidates (wide, narrow) carry content that Lean checked in translation.ve.md "
                                        "(norm-defaults@0, completion unspecified); VE does not choose between them")
                e["checked_content"] = {"set": sc.SET_ID, "document": "translation.ve.md", "record": "readings/nd-all-result.json, readings/nd-all-check.json"}
                e["scope_probe"] = {"meaning": "u0165.s03 probe points, on the wide companion (readings/all-strict.ve.md) and the narrow companion (readings/all-strict-narrow.ve.md)",
                                    "points": sp}
                e["check"]["note"] = "asked on the wide companion with the case = a cyberweapon that could cause significant damage (a case under both readings); the two readings differ at: " + \
                    "a cyberweapon that could not cause significant damage, knowingly created (wide " + sp["u0165.s03, wide reading: a cyberweapon that could not cause significant damage, knowingly created"] + \
                    ", narrow " + sp["u0165.s03, narrow reading: a cyberweapon that could not cause significant damage, knowingly created"] + ")"
            else:
                r0["english"] = eng[rule]["text"]
                r0["english_round_trip"] = eng[rule]["round_trip"]
                r0["english_round_trip_error"] = eng[rule]["error"]
                e["document_status"] = "OPEN (one strict reading; its category atom and its two alternatives, the knowing alternative and the belief alternative, are open terms)"
        elif i == U0123:
            assert "instruction_promote_own_products" in e["case_atoms"]
            e["case_atoms"]["instruction_promote_own_products"] = ("the operator gave the input and the input is an instruction to promote that operator’s own products "
                                                                    "and services rather than those of competitors (a pair of an operator and an input)")
            e["note"] = e["note"] + U0123_NOTE_ADD
            e["audit_repair"] = e["audit_repair"] + " | " + U0123_REPAIR_ADD
            e["repaired_in_run"] = RUN_ID
            e["audit_verified"] = False
            e["check"] = {"binding": {"the operator who gave the instruction to promote its own products": bp["u0123.s02.p1: the operator who gave the instruction to promote its own products"],
                                      "another operator, for the same input": bp["u0123.s02.p1: another operator, for the same input"],
                                      "meaning": "two operators, one input that the first gave: SETTLED yes = the text says the operator may; UNDECIDED = the text does not say"}}
        elif i == U0173:
            e["note"] = U0173_NOTE
    # no trace of the removed terms may remain anywhere in the ledger
    for e in ledger:
        for k, v in e.items():
            dumped = json.dumps(v, ensure_ascii=False)
            for w in ("thought_likely", "knowingly_<", "knowingly_mass", "knowingly_critical", "knowingly_damaging", "knowingly_clear", "knowingly_attempt",
                      "knowingly_illegitimate", "knowingly_child", "damaging_cyberweapon_or_malicious_code", "restricted_action_knowing_or_quite_likely"):
                assert w not in dumped, (e["id"], k, w)
    return ledger


def annotate(text, ledger):
    """Under each hard-constraint rule (the English is several lines: a first line and the alternatives), print its source words and VE's verdicts."""
    lines, out = text.split("\n"), []
    by_english = {}
    for e in ledger:
        if e["id"] in HC_UNITS and e["id"] != S03:
            by_english[e["readings"][0]["english"].split("\n")[0]] = e
    done, n = set(), 0
    while n < len(lines):
        line = lines[n]
        out.append(line)
        n += 1
        m = re.match(r"^(Open|Checked) reading: (.*)$", line)
        if m and m.group(2) in by_english:
            while n < len(lines) and lines[n].startswith("  ("):  # the alternatives of the rule
                out.append(lines[n])
                n += 1
            e = by_english[m.group(2)]
            done.add(e["id"])
            c = e["check"]
            out.append(f"  Source words of the case atom and the two alternatives of u0173.s01 (open terms): {'; '.join(f'“{k}”: {v}' for k, v in e['case_atoms'].items())}.")
            out.append(f"  VE: the case does not hold but Claude thinks it quite likely that the action falls into the category: "
                       f"{c['the case does not hold, Claude thinks it quite likely that the action falls into the category']}; the case holds and Claude knowingly and "
                       f"intentionally engages in it: {c['the case holds, Claude knowingly and intentionally engages in it']}; neither: "
                       f"{c['neither (an unclear, uncertain or unknowing case)']}; the case does not hold but Claude knowingly engages in it: "
                       f"{c['the case does not hold, Claude knowingly and intentionally engages in it']}. SETTLED no = the text says Claude may not; UNDECIDED = the text does not say.")
    assert done == set(HC_UNITS) - {S03}, done
    return "\n".join(out)


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
    tally["note"] = ("scope-tally for run 20261014T1800Z; the tags are ledger annotations only: other_blockers gains `other:scope`, governed units record governed_by "
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
        assert act_now == r["act"] == prev_vocab[e["predicate"]]["regulated"]["act"], (r["unit"], act_now, r["act"])
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

    # ---- audit-verified bytes: accepted by an audit of this lineage AND byte-identical here to the form that audit saw
    prev_verified = list(prev_metrics["audit_verified_covered_units"])
    dropped = [i for i in prev_verified if i in CHANGED or i in AUDIT_1013_UNFAITHFUL]
    kept = [i for i in prev_verified if i not in CHANGED and i not in AUDIT_1013_UNFAITHFUL]
    newly = [i for i in AUDIT_1013_FAITHFUL if status[i] in COVERED and status[i] != "LABELLED" and i not in CHANGED and i not in kept]
    assert not any(by_id[i].get("claimed") is False for i in [*kept, *newly])
    verified = kept + newly
    verified_bytes = width(verified)
    cand_lab = list(dict.fromkeys(old.AUDIT_PASSED_LABELLED + old.AUDIT_PASSED_1004_LABELLED + old.AUDIT_PASSED_1004B_LABELLED + ["u0212.heading"]
                                  + prevf.AUDIT_FAITHFUL_1800 + prevf.AUDIT_FAITHFUL_1811 + p18.AUDIT_0600_FAITHFUL + p13.AUDIT_1800_FAITHFUL + AUDIT_1013_FAITHFUL))
    verified_lab = [i for i in cand_lab if i in by_id and status[i] == "LABELLED"]
    verified_meta = width(verified_lab)
    assert verified_meta == prev_metrics["audit_verified_metadata_bytes"] == nb["LABELLED"], (verified_meta, nb["LABELLED"])
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
    hard_reading = (f"{n_all} of {len(hard_q)} queries are ALL with a certificate on the superposed route; the rest ({', '.join(unknown)}) are UNKNOWN: VE's search budget is "
                    "exhausted without a counterexample or a proof. 'neither' is UNKNOWN for every unit, which is the intended answer: the translation does not forbid an unclear, "
                    "uncertain or unknowing case. For u0165.s01 all three are UNKNOWN (several minutes each; the same shape of query on the earlier translations was also UNKNOWN), a limit "
                    "of the proof search; for s01 the checked answer is the settled-point answer of the unspecified probe. "
                    f"{len(reran) + 2} queries first failed with CheckerUnavailable (the Rust checker's default 5-second limit, three queries in parallel on a machine with load above 70) and were re-run "
                    f"one at a time; CheckerUnavailable is not a verdict and was not used. {len(capped)} of them were unavailable again at the default limit and were re-run under "
                    "`prlimit --as=6442450944` (6 GB address space) with VE_RUST_TIMEOUT=600 (DRI 2026-10-14 15:30Z, 3): " + ", ".join(capped) + "; the cap and the peak resident set are in `reruns`. "
                    f"The queries {', '.join(reask)} were asked again alone on the final document, which differs from the one the others ran on only in one predicate description "
                    "(`document_note`); they answered at the default limit.")
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
        "sorts_identical": main_meta["environment"]["vocabulary"]["sorts"] == prev_meta["environment"]["vocabulary"]["sorts"],
        "constants_identical": main_meta["environment"]["vocabulary"]["constants"] == prev_meta["environment"]["vocabulary"]["constants"],
        "predicates_added": sorted(set(pv_new) - set(pv_old)), "predicates_removed": sorted(set(pv_old) - set(pv_new)),
        "predicates_changed": sorted(k for k in pv_new if k in pv_old and pv_new[k] != pv_old[k]),
        "sort_entity": ("the sort `entity` (noun “entity”, plural “entities”) is carried from earlier runs; this run declares no new sort and changes none. DRI (1) says to declare it with the noun "
                        "“thing” when a plan declares it; renaming the carried noun would change every English line of the document and is left to a pass that re-measures, so the differences "
                        "against the previous run stay those of the language"),
    }
    assert vocab_check["body_text_identical"] and vocab_check["graph_identical"] and vocab_check["sorts_identical"] and vocab_check["constants_identical"]
    assert set(vocab_check["units_changed"]) == set(CHANGED) - {U0173} | {S03} | set(), vocab_check["units_changed"]
    hard_changed = {i: "plan repair AT-0p (attitudes plan, DRI AT2) after audit 20261013T0600Z: guard = ( C(s) and " + KNOW + "N(c, s) ) or " + THINK + "N(c, s), "
                       "two binary open terms on (claude_instance, situation); the category's case atom is restored, the previous run's unary terms are removed" for i in HC_UNITS}
    hard_changed[S03] += ("; also an audit repair: the category is three case atoms and the rule is the reading set " + sc.SET_ID + " of two candidates (wide, narrow)")
    new_terms = sorted(names - prev_names)
    removed_terms = sorted(prev_names - names)
    expected_added = {*[PER_UNIT[u][0] for u in HC_UNITS if u != S03], *sc.ATOMS, *[f"{KNOW}{n}" for n in range(1, 8)], *[f"{THINK}{n}" for n in range(1, 8)]}
    assert set(new_terms) == expected_added, set(new_terms) ^ expected_added
    prev_open = {t["name"]: t for t in prev_metrics["open_terms"]}
    changed_args = {t["name"]: {"arguments": [prev_open[t["name"]]["arguments"], t["arguments"]]} for t in open_terms
                    if t["name"] in prev_open and prev_open[t["name"]]["arguments"] != t["arguments"]}
    changed_factors = {t["name"]: {"factors": [prev_open[t["name"]]["factors"], t["factors"]]} for t in open_terms
                       if t["name"] in prev_open and prev_open[t["name"]]["factors"] != t["factors"]}
    assert set(changed_args) == {"instruction_promote_own_products"} and set(changed_factors) == set(), (changed_args, changed_factors)
    plan_repairs_changed = sorted({r["unit"] for r in PLAN_REPAIRS})
    m = {
        "run": RUN_ID, "baseline_tag": TAG, "previous_run": PREV_RUN, "previous_baseline_tag": PREV_TAG,
        "source_sha256": prev_metrics["source_sha256"], "source_bytes": len(SOURCE), "bytes_accounted": total, "bytes_accounted_percent": 100.0,
        "history_note": "this file records this run; the earlier runs' records (audit-verification history, the earlier probes' narrative) are in prev/metrics.json",
        "changed_units": sorted(CHANGED),
        "plan_repairs": PLAN_REPAIRS,
        "audit_repairs": AUDIT_REPAIRS,
        "changed_units_detail": {
            **hard_changed,
            U0123: "audit repair (audit 20261013T0600Z, rejected): instruction_promote_own_products is a pair of an operator and an input, and the rule's guard binds the permission's operator to it",
            U0173: "note only: UNFORMALISED, not claimed; says which open terms carry its two alternatives"},
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
        "audit_verified_newly_from_20261013T0600Z": newly,
        "audit_verified_basis": (
            "Audit-verified = accepted as faithful by an independent audit of this lineage AND byte-identical in this run to the form that audit saw. The audit of run "
            "20261013T0600Z (14/20 sampled faithful, 1/8 changed faithful; unfaithful: u0165.s01 to u0165.s07 and u0123.s02.p1; AUDIT-20261013T0600Z-received.md) is the latest. "
            "It accepted u0123.s01.p1, u0125.s04.p2, u0036.s05, u0156.s03, u0248 and u0263.s04.p2 (covered) and u0173.s01 (only as correctly UNFORMALISED), which this run leaves "
            "byte-identical, so their bytes stay audit-verified. The eight rejected units are repaired in this run and are claimed but not audit-verified until re-audited "
            "(u0123.s02.p1 was audit-verified before; the 20261013T0600Z audit withdrew that). Labels are unchanged: 349 of 349 label bytes stay verified."),
        "audit_verified_metadata_bytes": verified_meta, "audit_verified_metadata_percent": round(100 * verified_meta / len(SOURCE), 4),
        "audit_verified_metadata_bytes_previous_run": prev_metrics["audit_verified_metadata_bytes"],
        "claimed_but_not_audit_verified_bytes": claimed - verified_bytes - verified_meta,
        "repaired_bytes_not_audit_verified": repaired_bytes,
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20261013T0600Z_audit": AUDIT_1013_UNFAITHFUL,
            "repair_done_in_20261014T1800Z": ("u0165.s01 to s07: the plan repair AT-0p (guards bound to the acting instance of Claude); u0165.s03 also: the two attachments of the "
                                              "relative clause as a reading set; u0123.s02.p1: the operator argument. See AUDIT-REPAIR.md. Each keeps its covered status only because "
                                              "it is repaired; all eight are claimed but not audit-verified"),
            "kept_covered_status_without_repair": [],
            "earlier_audits": "the rejections and repairs of the earlier runs are recorded in prev/metrics.json and the AUDIT-*-received.md files"},
        "document_profiles": {"main": main_meta["environment"]["profiles"], "strict": front_matter(STRICT)["environment"]["profiles"]},
        "documents": {"translation": "translation.ve.md (four reading sets carry content: three 'should' sets and the scope set of u0165.s03; built by nd.py all from translation-without-content.ve.md, cmp-identical)",
                      "without_content": "translation-without-content.ve.md", "strict": "readings/all-strict.ve.md (the source of the strict content of the three sets, and of the wide candidate of the scope set)",
                      "strict_narrow": "readings/all-strict-narrow.ve.md (the strict companion with the narrow candidate of u0165.s03; used by the probes)",
                      "not_carried": "readings/all-default.ve.md, readings/s1.ve.md (soft-chain demonstrations of earlier runs; copied in for probes s1 and rights, then removed)"},
        "open_terms": open_terms, "open_terms_count": len(open_terms), "open_terms_count_previous_run": prev_metrics["open_terms_count"],
        "open_terms_added": new_terms, "open_terms_removed_this_run": removed_terms, "open_terms_with_changed_factors": [],
        "open_terms_with_changed_arguments": changed_args,
        "open_terms_count_note": "AT-0p alone gives 46 (the plan's expectation, measured at the first stage of this run: 7 case atoms back, 14 binary terms, 14 unary terms gone); the scope set of u0165.s03 replaces one case atom by three, so 48",
        "reading_sets": {"count": 4, "unresolved": 4, "count_previous_run": 3, "units": [*SETS_KEPT, S03],
                         "candidates": {**{i: ["strict", "default"] for i in SETS_KEPT}, S03: ["wide", "narrow"]},
                         "couplings": [], "narrowings": [],
                         "choices": nd["all"]["choice_count"], "choices_previous_run": 8, "removed_this_run": {},
                         "added_this_run": {S03: "the two attachments of “that could cause significant damage if deployed” (audit 20261013T0600Z); both are admitted by the English words alone"},
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
                               "build_note": "this worktree's `lake build` rebuilt the whole library (887 jobs, about 30 minutes); not a language measurement",
                               "order": "[this run, previous run]; this run has four sets (16 choices), the previous three (8 choices)"},
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
                                         "ask u0165.s03 on both companions: a cyberweapon that could not cause significant damage, knowingly created, is UNDECIDED under the wide reading and "
                                         "SETTLED no under the narrow one; the binding points ask u0123.s02.p1 with two operators. The non-hard-constraint points are the previous run's",
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
                                      "document_note": json.load(open(RUN / "evidence/hard-queries-document-diff.json")),
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
            "units_with_status_change": {S03: ["OPEN", "READINGS"]}, "units_changed_by_audit_repair": [S03, U0123, *HC_UNITS],
            "open_terms_added": new_terms, "open_terms_removed": removed_terms,
            "open_terms_count_before_after": [len(prev_names), len(names)],
            "reading_sets_before_after": [3, 4], "choices_before_after": [8, 16]},
        "language_changes_since_previous_tag": {
            "from": PREV_TAG, "to": TAG,
            "merged": {"readings-defaults/rd5 (RD-5)": "coupled and joint reading choices are planned and checked by Lean (`readings-choices` mode, lean/VE/Service/ReadingsChoices.lean); authored assertions stay fixed in joint checks. "
                                                         "The reading plan of `ve document check` for a document with several sets goes through it only when couplings are present; here it is the independent route",
                       "lean-first/b14d (lf-14d)": "Lean-first relay batch; no change to the grammar or the profiles",
                       "infra/runner-portability": "timing and deadline handling of the Rust and Lean clients; tooling",
                       "infra/arch-AR-3, fix/main-relay, fix/repo-map-untracked": "gate, quarantine, relay-gate fixtures and repo-map regression repairs; tooling and tests"},
            "checked_by": "git diff ve-green-eff-20261011-1..HEAD --stat -- ve lean rust conformance: 29 files, namely the new Lean `readings-choices` mode and its response shape/encoders, "
                          "its relay in ve/readings.py, ve/document.py and ve/backends, generated manifests, and conformance wrapper tweaks; none is in the grammar, profiles, lexicon, checkers or Rust",
            "newly_expressible_features": 0, "units_upgraded_by_new_features": 0, "reading_sets_upgraded_by_new_features": 0,
            "newly_measurable": "the 16 choices of the four sets are planned through the new Lean choice mode; nothing else a translator can state changed",
            "what_made_the_difference": "the plan-directed repair AT-0p and the audit's repairs, not the language"},
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
    for stale in ("force-u0125", "exception_to_never_denying", "thought_likely", "knowingly_<", "damaging_cyberweapon_or_malicious_code", "restricted_action_knowing_or_quite_likely",
                  "flat “either", "three 'should' reading sets carry content"):
        assert stale not in whole, stale
    dump("metrics.json", m)
    print(json.dumps({k: m[k] for k in ("claimed_covered_bytes", "claimed_covered_percent", "audit_verified_covered_bytes", "audit_verified_covered_percent",
                                         "audit_verified_metadata_bytes", "claimed_but_not_audit_verified_bytes", "changed_units")}))
    print(dict(u), dict(nb))
    print("probe_same:", probe_same, "profile probe same:", m["profile_combination_probe_same_as_previous_run"])
    print("ask read:", ask_read, "companion q:", {k: v["verdict"] for k, v in comp_q.items()}, "conclusions:", {k: v["verdict"] for k, v in concl.items()})


if __name__ == "__main__":
    main()
