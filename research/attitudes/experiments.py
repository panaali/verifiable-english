#!/usr/bin/env python3
"""E1 and E2 (docs/spec/attitudes-PLAN.md section 4): item sets, seeded orders and scoring, with the plan's bars written in.

No reader is called here: `run_readers.py` makes the calls (Sonnet 5.5 as human proxy, 40 independent readers per
item; authorised by the DRI's decision AT1, 2026-10-13). This script holds the items, the seeded orders and the bars, so
that the run is mechanical and its bars are fixed before any answer exists:

    uv run python research/attitudes/experiments.py items             # -> docs/research/evidence/attitudes/e{1,2}-items.json
    uv run python research/attitudes/experiments.py score-e1 ANSWERS  # -> e1-result.json   (ANSWERS: jsonl, one answer per line)
    uv run python research/attitudes/experiments.py score-e2 ANSWERS  # -> e2-result.json   (needs e1-result.json)
    uv run python research/attitudes/experiments.py table STUB        # -> e-table.lean: the frozen `table`, reviewed by Lean
    uv run python research/attitudes/experiments.py selfcheck STUB    # the bars at their boundaries; a synthetic outcome through Lean

An answer line is {"item": "<item id>", "session": <0..39>, "answer": "<the reader's raw text>"}. Every item needs exactly one
answer per session; anything else is refused, never scored in part.

The closure review is Lean's `Table.reviewed` (spec section 2.1), evaluated by `lake env lean` on a copy of the AT-0 stub
with the emitted table appended: this script never decides it. The only closure computed here is the PROPOSED resolution
(phase 1 report, section 5, G4) that removes a word before freezing; its output is still reviewed by Lean.
"""
from __future__ import annotations

import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EVIDENCE = ROOT / "docs/research/evidence/attitudes"
STUB = HERE / "stub/SpecStubs_attitudes.lean"
# The AT-0 stub, updated to spec draft 4's Lean with the frozen table written in (committed here; draft 1's copy was
# untracked in ve-design-attitudes, sha256 2178fb6e…), then with AT-0's re-review fixes RR-1 to RR-3 (was 0c73f880…).
# Its `Table` and `Table.reviewed` are unchanged from draft 1.
# Pinned so that a later edit to it cannot silently change the review: a stub with another hash is refused.
STUB_SHA256 = "dea412eb2654d245c12b48cc389c33d6292ad51c57421aa9640bec08d738f113"

# ---- quoted from the PLAN (E1, E2); the order is E1's list order, strongest first ----
WORDS = ["almost certain", "very likely", "quite likely", "likely", "more likely than not", "as likely as not",
         "unlikely", "very unlikely"]
SESSIONS = 40
READER = "claude-sonnet-5-5"
PAIR_YES, PAIR_MAX_NO = 36, 2          # E1: a pair enters iff at least 36 of 40 answer yes and at most 2 answer no
CERT_YES = 34                          # E1: lower bound confirmed iff at least 34 of 40 answer yes
E2_REACH = 36                          # E2: an item "reaches 36 of 40"

ANSWERS = ("yes", "no", "cannot tell")
PROMPT = ("Read the text and answer the question as an ordinary reader of English. Answer with exactly one of: yes, no, "
          "cannot tell.\n\n{text}")


def slug(word):
    return word.replace(" ", "-")


def e1_items():
    items = []
    for i, a in enumerate(WORDS):
        for b in WORDS[i + 1:]:  # 28 pairs, asked in E1's list order: "a" first (G1)
            items.append({"id": f"E1.pair.{slug(a)}.{slug(b)}", "kind": "pair", "a": a, "b": b,
                          "text": f"First sentence: Claude thinks it {a} that the file is safe.\n"
                                  f"Second sentence: Claude thinks it {b} that the file is safe.\n"
                                  f"Question: If the first sentence is true, must the second be true?"})
    for w in WORDS:
        items.append({"id": f"E1.cert.{slug(w)}", "kind": "cert", "word": w,
                      "text": f"Question: If Claude is certain that the file is safe, does Claude think it {w} that the file "
                              f"is safe?"})
    assert len(items) == 36
    return items


CONTENTS = [("the file is safe", "the file be safe"), ("the user is an adult", "the user be an adult"),
            ("the door is locked", "the door be locked")]


def e2_items():
    items = []
    for n, (p, p_be) in enumerate(CONTENTS, 1):
        items.append({"id": f"E2.factive.{n}", "kind": "factive", "group": "E2.factive", "expected": "yes",
                      "text": f"Claude knows that {p}. Question: Must {p_be}?"})
    for n, (p, _) in enumerate(CONTENTS, 1):
        items.append({"id": f"E2.knows-believes.{n}", "kind": "knows-believes", "group": "E2.knows-believes",
                      "expected": "yes", "text": f"Claude knows that {p}. Question: Must Claude believe that {p}?"})
    for w in WORDS:  # all eight, so that E2 can run beside E1 (G3); only E1's lower-bound words are scored
        items.append({"id": f"E2.knows-thinks.{slug(w)}", "kind": "knows-thinks", "word": w, "expected": "yes",
                      "group": f"E2.knows-thinks.{slug(w)}",
                      "text": f"Claude knows that the file is safe. Question: Must Claude think it {w} that the file is safe?"})
    for n, (p, p_be) in enumerate(CONTENTS, 1):
        items.append({"id": f"E2.negated-know.{n}", "kind": "negated-know", "group": "E2.negated-know", "expected": None,
                      "text": f"Claude does not know that {p}. Question: Must {p_be}?"})
    unless = [("Claude must not share the file unless Claude knows that the user is an adult. The user is not an adult.",
               "Must Claude not share the file?"),
              ("Claude must not open the door unless Claude knows that the visitor is the owner. The visitor is not the owner.",
               "Must Claude not open the door?"),
              ("Claude must not send the report unless Claude knows that the data is correct. The data is not correct.",
               "Must Claude not send the report?")]
    for n, (rule, q) in enumerate(unless, 1):
        items.append({"id": f"E2.unless.{n}", "kind": "unless", "group": "E2.unless", "expected": None,
                      "text": f"{rule} Question: {q}"})
    for n, (p, p_be) in enumerate(CONTENTS, 1):  # the question is this phase's proposal (G5)
        items.append({"id": f"E2.asserted-not-know.{n}", "kind": "asserted-not-know", "group": "E2.asserted-not-know",
                      "expected": "yes", "text": f"{p[0].upper()}{p[1:]}, and Claude does not know that {p}. Question: Must {p_be}?"})
    for n, (p, _) in enumerate(CONTENTS, 1):  # G5's three added items: is "does not know" read as not knowing?
        items.append({"id": f"E2.asserted-not-know-knows.{n}", "kind": "asserted-not-know-knows",
                      "group": "E2.asserted-not-know", "expected": "no",
                      "text": f"{p[0].upper()}{p[1:]}, and Claude does not know that {p}. Question: Does Claude know that {p}?"})
    assert len(items) == 26
    return items


def orders(items, seed):
    """One call order per session, from one seeded generator (the PLAN's seed). Every call is a fresh context (G2)."""
    rng = random.Random(seed)
    ids = [i["id"] for i in items]
    out = []
    for _ in range(SESSIONS):
        perm = ids[:]
        rng.shuffle(perm)
        out.append(perm)
    return out


def parse(text):
    """yes / no / cannot tell, from the first line; anything else is "invalid". An invalid answer is never a yes; for E1's
    no cap it counts as a no, and it is left out of the negated-"know" agreement count (G6, in the scorers)."""
    first = (text or "").strip().splitlines()[0].strip().lower() if (text or "").strip() else ""
    first = re.sub(r"[^a-z' ]", "", first).strip()
    if first.startswith("cannot tell") or first.startswith("can't tell") or first.startswith("cant tell"):
        return "cannot tell"
    for word in ("yes", "no"):
        if first == word or first.startswith(word + " "):
            return word
    return "invalid"


def tally(items, lines):
    """Counts per item; refuses an answer set that is not exactly one answer per (item, session)."""
    ids = {i["id"] for i in items}
    seen, counts = set(), {i: {"yes": 0, "no": 0, "cannot tell": 0, "invalid": 0} for i in ids}
    for row in lines:
        key = (row["item"], row["session"])
        if row["item"] not in ids or not (isinstance(row["session"], int) and 0 <= row["session"] < SESSIONS):
            raise SystemExit(f"refused: answer for an unknown item or session {key}")
        if key in seen:
            raise SystemExit(f"refused: two answers for {key}")
        seen.add(key)
        counts[row["item"]][parse(row["answer"])] += 1
    if len(seen) != len(ids) * SESSIONS:
        raise SystemExit(f"refused: {len(ids) * SESSIONS - len(seen)} answers missing")
    return counts


def score_e1(counts):
    """The PLAN's E1 bars, as quoted (phase 1 report 1.2). A word that fails its certainty item is named by no pair."""
    lower = [(w, f"E1.cert.{slug(w)}") for w in WORDS if counts[f"E1.cert.{slug(w)}"]["yes"] >= CERT_YES]
    words = [w for w, _ in lower]
    above = []
    for i, a in enumerate(WORDS):
        for b in WORDS[i + 1:]:
            c = counts[f"E1.pair.{slug(a)}.{slug(b)}"]
            if c["yes"] >= PAIR_YES and c["no"] + c["invalid"] <= PAIR_MAX_NO and a in words and b in words:  # G6
                above.append((a, b, f"E1.pair.{slug(a)}.{slug(b)}"))
    return {"lowerBound": lower, "above": above, "counts": counts}


def score_e2(counts, e1):
    expected = {i["id"]: i["expected"] for i in e2_items()}
    reach = lambda i: counts[i][expected[i]] >= E2_REACH  # 36 of 40 give the item's expected answer
    factive = "E2.factive" if all(reach(f"E2.factive.{n}") for n in (1, 2, 3)) else None
    believes = "E2.knows-believes" if factive and all(reach(f"E2.knows-believes.{n}") for n in (1, 2, 3)) else None
    words = [w for w, _ in e1["lowerBound"]]
    thinks = [(w, f"E2.knows-thinks.{slug(w)}") for w in words if factive and reach(f"E2.knows-thinks.{slug(w)}")]
    top = lambda i: max(ANSWERS, key=lambda k: counts[i][k])
    # agreement on one reading among yes, no and cannot tell; invalid answers are left out of the count (G6)
    negated = {f"E2.negated-know.{n}": {"counts": counts[f"E2.negated-know.{n}"],
                                         "agreed_36": max(counts[f"E2.negated-know.{n}"][k] for k in ANSWERS) >= E2_REACH,
                                         "top": top(f"E2.negated-know.{n}")} for n in (1, 2, 3)}
    # admitted only if all six items reach 36 of 40: three "Must P?" (yes: P is asserted) and three "Does Claude know
    # that P?" (no: "does not know" is read as not knowing) (A4, G5)
    six = [f"E2.asserted-not-know.{n}" for n in (1, 2, 3)] + [f"E2.asserted-not-know-knows.{n}" for n in (1, 2, 3)]
    admitted = all(reach(i) for i in six)
    return {"factive": factive, "knowsBelieves": believes, "knowsThinks": thinks,
            "negated_know": {"items": negated, "decision": "refused (D-A7), whatever the counts"},
            "unless": {"items": {f"E2.unless.{n}": counts[f"E2.unless.{n}"] for n in (1, 2, 3)},
                       "decision": "refused; evidence only"},
            "asserted_not_know": {"admitted": admitted, "reached": {i: reach(i) for i in six},
                                  "decision": "admitted" if admitted else "refused, with its rewrites",
                                  "items": {i: counts[i] for i in six}},
            "counts": counts}


def resolve(lower, above, thinks):
    """G4 (PLAN draft 5, section 4): while the closure of the frozen pairs reaches a pair without its own passing item,
    or a premise-3 word without its own item, the weaker word of one such entry leaves lowerBound (with every pair and
    premise naming it): of all offending words, the weakest (the last in E1's list) first, one per round. The order
    is part of the rule; with several violations another order can leave a different table that Lean also reviews."""
    lower, above, thinks = list(lower), list(above), list(thinks)
    removed = []
    while True:
        words = [w for w, _ in lower]
        edges = {(a, b) for a, b, _ in above}
        reach = {a: {a} for a in words}
        changed = True
        while changed:
            changed = False
            for a in words:
                for (x, y) in edges:
                    if x in reach[a] and y not in reach[a]:
                        reach[a].add(y)
                        changed = True
        weak = [b for a in words for b in sorted(reach[a], key=WORDS.index) if a != b and (a, b) not in edges]
        k = {w for w, _ in thinks}
        weak += [b for a in k for b in reach[a] if b not in k]
        if not weak:
            return lower, above, thinks, removed
        drop = max(weak, key=WORDS.index)
        removed.append(drop)
        lower = [p for p in lower if p[0] != drop]
        above = [p for p in above if drop not in p[:2]]
        thinks = [p for p in thinks if p[0] != drop]


def lean_str(s):
    return json.dumps(s, ensure_ascii=False)


def lean_table(name, lower, above, factive, believes, thinks):
    opt = lambda x: "none" if x is None else f"some {lean_str(x)}"
    pairs = lambda xs: "[" + ", ".join("(" + ", ".join(lean_str(v) for v in p) + ")" for p in xs) + "]"
    return (f"def {name} : VE.Attitudes.Table :=\n"
            f"  {{ candidates := VE.Attitudes.e1Words,\n    lowerBound := {pairs(lower)},\n    above := {pairs(above)},\n"
            f"    factive := {opt(factive)},\n    knowsBelieves := {opt(believes)},\n    knowsThinks := {pairs(thinks)} }}\n")


def lean_review(stub, tables):
    """Evaluates `Table.reviewed` (the stub's, i.e. the spec's) on each emitted table with `lake env lean`."""
    import hashlib
    digest = hashlib.sha256(Path(stub).read_bytes()).hexdigest()
    if digest != STUB_SHA256:
        raise SystemExit(f"refused: stub {stub} has sha256 {digest}, not the pinned {STUB_SHA256}")
    text = Path(stub).read_text()
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "ReviewTables.lean"
        body = "\n".join(src for _, src in tables)
        evals = "\n".join(f"#eval ({n}).reviewed" for n, _ in tables)
        f.write_text(text + "\n\nnamespace PhaseOne\n" + body + "\n" + evals + "\nend PhaseOne\n")
        lean = shutil.which("lake") or str(Path.home() / ".elan/bin/lake")
        run = subprocess.run([lean, "env", "lean", str(f)], cwd=ROOT / "lean", capture_output=True, text=True)
    outs = [ln.strip() for ln in run.stdout.splitlines() if ln.strip() in ("true", "false")]
    if run.returncode != 0 or len(outs) != len(tables):
        raise SystemExit(f"lean review failed ({run.returncode}):\n{run.stdout[-3000:]}\n{run.stderr[-2000:]}")
    return dict(zip([n for n, _ in tables], [o == "true" for o in outs]))


def dump(name, obj):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def cmd_items():
    protocol = {"reader": READER, "sessions": SESSIONS, "prompt": PROMPT, "answers": list(ANSWERS),
                "calls": "one fresh context per call: no system prompt beyond PROMPT, no earlier turns (G2)",
                "parse": "first line, lower case, letters only: 'yes' / 'no' / 'cannot tell' (also can't tell); else invalid"}
    e1, e2 = e1_items(), e2_items()
    dump("e1-items.json", {"seed": "attitudes-E1", "protocol": protocol, "items": e1, "orders": orders(e1, "attitudes-E1")})
    dump("e2-items.json", {"seed": "attitudes-E2", "protocol": protocol, "items": e2, "orders": orders(e2, "attitudes-E2")})
    print("E1", len(e1), "items,", len(e1) * SESSIONS, "calls; E2", len(e2), "items,", len(e2) * SESSIONS, "calls")


def read_answers(path):
    return [json.loads(ln) for ln in Path(path).read_text().splitlines() if ln.strip()]


def cmd_score_e1(path):
    r = score_e1(tally(e1_items(), read_answers(path)))
    dump("e1-result.json", r)
    print(json.dumps({k: r[k] for k in ("lowerBound", "above")}, indent=1))


def cmd_score_e2(path):
    e1 = json.loads((EVIDENCE / "e1-result.json").read_text())
    r = score_e2(tally(e2_items(), read_answers(path)), e1)
    dump("e2-result.json", r)
    print(json.dumps({k: r[k] for k in ("factive", "knowsBelieves", "knowsThinks", "asserted_not_know")}, indent=1)[:3000])


def frozen(e1, e2):
    lower, above, thinks, removed = resolve([tuple(p) for p in e1["lowerBound"]], [tuple(p) for p in e1["above"]],
                                           [tuple(p) for p in e2["knowsThinks"]])
    return lean_table("frozenTable", lower, above, e2["factive"], e2["knowsBelieves"], thinks), removed


def cmd_table(stub):
    e1 = json.loads((EVIDENCE / "e1-result.json").read_text())
    e2 = json.loads((EVIDENCE / "e2-result.json").read_text())
    src, removed = frozen(e1, e2)
    reviewed = lean_review(stub, [("frozenTable", src)])
    (EVIDENCE / "e-table.lean").write_text(f"-- removed before freezing (G4): {removed}\n-- Lean Table.reviewed: "
                                           f"{reviewed['frozenTable']}\n" + src)
    print(src, removed, reviewed)


def synthetic(item_ids, yes, no=None, cannot=None):
    """Answer lines with exact counts per item, for the self-check only (no reader is involved). The rest of the 40 is
    invalid ("Maybe.")."""
    no, cannot = no or {}, cannot or {}
    lines = []
    for i in item_ids:
        kinds = ["yes"] * yes.get(i, 0) + ["no"] * no.get(i, 0) + ["cannot tell"] * cannot.get(i, 0)
        kinds += ["maybe"] * (SESSIONS - len(kinds))
        lines += [{"item": i, "session": s, "answer": k.capitalize() + "."} for s, k in enumerate(kinds)]
    return lines


def cmd_selfcheck(stub):
    """The bars at their boundaries, and the refusals of a malformed answer set. Synthetic counts, no reader."""
    e1 = e1_items()
    ids = [i["id"] for i in e1]
    p = "E1.pair.very-likely.quite-likely"
    base = {i: 40 for i in ids}
    checks = {}
    # the rest of the 40 is "cannot tell" unless named; G6: an invalid answer counts as a no for the no cap
    for yes, no, inv, want in [(36, 2, 0, True), (35, 0, 0, False), (36, 3, 0, False), (40, 0, 0, True), (37, 3, 0, False),
                               (36, 2, 1, False), (36, 0, 4, False), (38, 0, 2, True), (36, 1, 1, True)]:
        cannot = SESSIONS - yes - no - inv
        r = score_e1(tally(e1, synthetic(ids, {**base, p: yes}, {p: no}, {p: cannot})))
        checks[f"pair yes={yes} no={no} invalid={inv}"] = (any(x[2] == p for x in r["above"]) == want)
    c = "E1.cert.likely"
    for yes, want in [(34, True), (33, False)]:
        r = score_e1(tally(e1, synthetic(ids, {**base, c: yes})))
        got = "likely" in [w for w, _ in r["lowerBound"]]
        names = any("likely" in x[:2] for x in r["above"])
        checks[f"cert yes={yes}"] = got == want and (names == want)
    for bad, what in [(synthetic(ids, base)[:-1], "missing"), (synthetic(ids, base) + synthetic(ids, base)[:1], "duplicate")]:
        try:
            tally(e1, bad)
            checks[f"refuses {what}"] = False
        except SystemExit:
            checks[f"refuses {what}"] = True
    for raw, want in [("Yes.", "yes"), ("no", "no"), ("Cannot tell.", "cannot tell"), ("I think yes", "invalid"), ("", "invalid"),
                      ("Not necessarily.", "invalid")]:  # the current rule (G6): a clear negative is not "no"
        checks[f"parse {raw!r}"] = parse(raw) == want
    # E2 at its boundary, and premise 2/3 only with premise 1
    e2 = e2_items()
    ids2 = [i["id"] for i in e2]
    r1 = score_e1(tally(e1, synthetic(ids, base)))
    full = {i: 40 for i in ids2}
    for yes, want in [(36, "E2.factive"), (35, None)]:
        r = score_e2(tally(e2, synthetic(ids2, {**full, "E2.factive.2": yes})), r1)
        checks[f"factive item yes={yes}"] = r["factive"] == want and (want is not None or (r["knowsBelieves"] is None and r["knowsThinks"] == []))
    # the asserted-not-know form: six items, the three "Does Claude know that P?" items reach on "no" (G5)
    knows = [f"E2.asserted-not-know-knows.{n}" for n in (1, 2, 3)]
    yes_full = {i: (0 if i in knows else 40) for i in ids2}
    for k_no, want in [(36, True), (35, False)]:
        r = score_e2(tally(e2, synthetic(ids2, yes_full, {**{k: 40 for k in knows}, knows[1]: k_no})), r1)
        checks[f"asserted-not-know: knows item no={k_no}"] = r["asserted_not_know"]["admitted"] is want
    r = score_e2(tally(e2, synthetic(ids2, full)), r1)
    checks["asserted-not-know: 'yes' to 'Does Claude know?' refuses the form"] = r["asserted_not_know"]["admitted"] is False
    # G6: the negated-"know" agreement count leaves invalid answers out (35 no + 5 invalid is not agreement)
    neg = "E2.negated-know.1"
    for no, cannot, want in [(36, 0, True), (35, 0, False), (35, 1, False), (0, 0, False)]:
        r = score_e2(tally(e2, synthetic(ids2, {**full, neg: 0}, {neg: no}, {neg: cannot})), r1)
        checks[f"negated-know agreement no={no} cannot={cannot} invalid={40 - no - cannot}"] = (
            r["negated_know"]["items"][neg]["agreed_36"] is want)
    # a synthetic outcome with a closure failure: (very likely, likely) fails while the chain through quite likely passes
    fail = "E1.pair.very-likely.likely"
    rf = score_e1(tally(e1, synthetic(ids, {**base, fail: 20}, {fail: 20})))
    r2 = score_e2(tally(e2, synthetic(ids2, full)), rf)
    raw = lean_table("rawTable", rf["lowerBound"], rf["above"], r2["factive"], r2["knowsBelieves"], r2["knowsThinks"])
    src, removed = frozen(rf, r2)
    allpass = lean_table("allPassTable", r1["lowerBound"], r1["above"], "E2.factive", "E2.knows-believes",
                         [(w, f"E2.knows-thinks.{slug(w)}") for w, _ in r1["lowerBound"]])
    # three violations at once: only the chain almost certain > very likely > quite likely > likely passes among these
    # four, so (almost certain, quite likely), (almost certain, likely) and (very likely, likely) are derived and failed.
    # Removing "quite likely" alone would also leave a reviewed table; the weakest-offending-word rule removes "likely"
    # first, then "quite likely" (G4: the order is the rule, Lean's review accepts both outcomes)
    fails = ["E1.pair.almost-certain.quite-likely", "E1.pair.almost-certain.likely", "E1.pair.very-likely.likely"]
    rm = score_e1(tally(e1, synthetic(ids, {**base, **{f: 20 for f in fails}}, {f: 20 for f in fails})))
    r2m = score_e2(tally(e2, synthetic(ids2, full)), rm)
    multi, removed_multi = frozen(rm, r2m)
    multi = multi.replace("def frozenTable", "def multiTable")
    keep = lambda p: "quite likely" not in p[:2]
    other = lean_table("otherOrderTable", [p for p in rm["lowerBound"] if keep(p)], [p for p in rm["above"] if keep(p)],
                       r2m["factive"], r2m["knowsBelieves"], [p for p in r2m["knowsThinks"] if keep(p)])
    reviewed = lean_review(stub, [("rawTable", raw), ("frozenTable", src), ("allPassTable", allpass),
                                  ("multiTable", multi), ("otherOrderTable", other)])
    checks["lean: raw table with a failed derived pair is not reviewed"] = reviewed["rawTable"] is False
    checks["lean: resolved table is reviewed"] = reviewed["frozenTable"] is True
    checks["lean: all-pass table is reviewed"] = reviewed["allPassTable"] is True
    checks["resolution removes the weaker word"] = removed[:1] == ["likely"]
    checks["three violations: weakest offending word first, then the next"] = removed_multi == ["likely", "quite likely"]
    checks["lean: three violations resolved is reviewed (and the other order too, so the order is pre-registered)"] = (
        reviewed["multiTable"] is True and reviewed["otherOrderTable"] is True)
    with tempfile.TemporaryDirectory() as tmp:
        edited = Path(tmp) / "SpecStubs_attitudes.lean"
        edited.write_bytes(Path(stub).read_bytes() + b"\n")
        try:
            lean_review(edited, [("allPassTable", allpass)])
            checks["refuses a stub with another hash"] = False
        except SystemExit:
            checks["refuses a stub with another hash"] = True
    out = {"synthetic": "counts made up by this self-check; no reader was called", "stub": str(stub),
           "stub_sha256": STUB_SHA256, "checks": checks, "removed": removed,
           "removed_three_violations": removed_multi, "all_pass": all(checks.values())}
    dump("e-selfcheck.json", out)
    print(json.dumps(out, indent=1))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    cmd, *args = sys.argv[1:]
    sys.exit({"items": lambda: cmd_items(), "score-e1": lambda: cmd_score_e1(*args), "score-e2": lambda: cmd_score_e2(*args),
              "table": lambda: cmd_table(*(args or [STUB])), "selfcheck": lambda: cmd_selfcheck(*(args or [STUB]))}[cmd]())
