#!/usr/bin/env python3
"""Score the risk wording probe mechanically against the sealed key and write RESULTS.md (risk-PLAN.md 2.6).

    python3 score.py

Reads items.json, sessions.json and runs/<session>/{response.txt,meta.json}. An answer is the first option letter
found in the reader's block for that text; an unparseable answer counts as wrong but not critical.
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROXY = "proxy; human readability unmeasured"
ORDER = ["c1", "c2", "c3a", "c3b", "c4", "c5", "c6", "c7", "c8", "c9", "c10", "c11", "c12", "c13", "c14",
         "control-prevents"]

# Where the reader's block for text n starts: "Text 1", "**Item 1:**", "## Question 1", or "1." / "1)" / "1:".
HEAD = (r"(?im)^[ \t>#*_\-]*(?:(?:text|item|question|q)\s*#?\s*{n}(?!\d)"
        r"|\**{n}\**\s*[.):])")
# The chosen option, earliest match in the block wins.
END = r"(?=\)|\.|:|\*|\s*[—–-]|\s*$)"
PICK = [
    r"(?i)\(([a-d])\)",                                                         # (b)
    r"(?im)^[ \t>*_\-]*\**([a-d])\**\s*[.):]\**(?=\s|$)",                       # b) ... / **b.**
    r"(?im)\b(?:answer|option|choice)\s*(?:is\s*)?[:\-]?\s*\**\s*([a-d])" + END,  # Answer: b
    r"(?i)\*\*([a-d])\*\*",                                                     # **b**
    r"(?im)(?:\b(?:text|item|question|q)\s*#?\s*\d+|^[ \t>#*_\-]*\d+)\**\s*[:.)\-—–]\s*\**\s*([a-d])" + END,
]


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", re.sub(r"\s+", " ", s.lower())).strip()


def blocks(response, count):
    """Split the response into one block per text; a block whose heading is not found is None."""
    starts, pos = [], 0
    for n in range(1, count + 1):
        m = re.compile(HEAD.format(n=n)).search(response, pos)
        if m:
            starts.append((n, m.start(), m.end()))
            pos = m.end()
        else:
            starts.append((n, None, None))
    found = [s for s in starts if s[1] is not None]
    out = {}
    for n, s, e in starts:
        if s is None:
            out[n] = None
            continue
        later = [f[1] for f in found if f[1] > s]
        out[n] = response[s:(min(later) if later else len(response))]
    return out


def pick(block, shown_texts):
    """Return (shown letter or None, how it was parsed)."""
    best = None
    for pat in PICK:
        for m in re.finditer(pat, block):
            if best is None or m.start(1) < best[0]:
                best = (m.start(1), m.group(1).lower())
            break
    if best:
        return best[1], "letter"
    hits = [l for l, t in shown_texts.items() if norm(t) and norm(t) in norm(block)]
    if len(hits) == 1:
        return hits[0], "option text"
    return None, "unparseable"


def main():
    items = {it["id"]: it for it in json.loads((HERE / "items.json").read_text())}
    sealed = json.loads((HERE / "sessions.json").read_text())
    answers, sessions_meta = [], []
    for sess in sealed["sessions"]:
        sid = sess["session"]
        rdir = HERE / "runs" / sid
        resp_path = rdir / "response.txt"
        meta = json.loads((rdir / "meta.json").read_text()) if (rdir / "meta.json").exists() else {}
        response = resp_path.read_text() if resp_path.exists() else None
        sessions_meta.append({"session": sid, "ran": response is not None, **meta})
        bl = blocks(response, len(sess["items"])) if response is not None else {}
        for e in sess["items"]:
            it = items[e["item"]]
            label_of = e["shown_to_label"]
            shown_texts = {s: next(o["text"] for o in it["options"] if o["label"] == l)
                           for s, l in label_of.items()}
            block = bl.get(e["position"])
            if response is None:
                shown, how = None, "not run"
            elif block is None:
                shown, how = None, "unparseable"
            else:
                shown, how = pick(block, shown_texts)
            label = label_of.get(shown) if shown else None
            answers.append({
                "session": sid, "family": sess["family"], "replicate": sess["replicate"],
                "condition": sess["condition"], "position": e["position"], "item": it["id"],
                "construct": it["construct"], "scored": it["scored"], "shown": shown, "label": label,
                "key": it["key"], "critical_labels": it["critical"], "parse": how,
                "correct": label == it["key"], "critical": label in it["critical"] if label else False,
                "reason": re.sub(r"\s+", " ", block or "").strip(),
            })
    (HERE / "scored.json").write_text(json.dumps(answers, indent=1) + "\n")
    write_results(items, sealed, answers, sessions_meta)


def tally(ans):
    return (sum(a["correct"] for a in ans), sum(a["critical"] for a in ans), len(ans),
            sum(a["parse"] in ("unparseable", "not run") for a in ans))


def write_results(items, sealed, answers, sessions_meta):
    by = {}
    for a in answers:
        by.setdefault((a["construct"], a["condition"]), []).append(a)
    L = []
    L.append("# Risk wording probe: results")
    L.append("")
    L.append(f"**Label: {PROXY}.** Readers are proxy models (Claude Haiku 4.5, GPT-6 Sol), not people. This is the "
             "2.6 wording probe of `docs/spec/risk-PLAN.md`, not the W8 fidelity gate.")
    L.append("")
    L.append(f"Sealed inputs: `MANIFEST.sha256` (seed {sealed['seed']}). Dropped before sealing: "
             + ", ".join(f"`{d}`" for d in sealed["dropped"]) + ". Generated by `score.py` from `runs/`; "
             "per-answer data in `scored.json`.")
    L.append("")

    # Per construct and condition.
    L.append("## Counts per construct and condition")
    L.append("")
    L.append("`correct / answers`, `critical`, `unparseable`; the gate uses L (2.6 rule 1).")
    L.append("")
    L.append("| Construct | Items | L correct | L critical | L unparseable | C correct | C critical | C unparseable |")
    L.append("|---|---|---|---|---|---|---|---|")
    for c in ORDER:
        n_items = sum(1 for it in items.values() if it["construct"] == c)
        row = [c, str(n_items)]
        for cond in ("L", "C"):
            ans = by.get((c, cond), [])
            if not ans:
                row += ["n/a", "n/a", "n/a"]
                continue
            cor, crit, n, unp = tally(ans)
            row += [f"{cor}/{n}", str(crit), str(unp)]
        L.append("| " + " | ".join(row) + " |")
    L.append("")
    L.append("Per family (L / C, correct and critical):")
    L.append("")
    L.append("| Construct | Haiku L | Haiku C | Sol L | Sol C |")
    L.append("|---|---|---|---|---|")
    for c in ORDER:
        row = [c]
        for fam in ("haiku", "sol"):
            for cond in ("L", "C"):
                ans = [a for a in by.get((c, cond), []) if a["family"] == fam]
                if not ans:
                    row.append("n/a")
                    continue
                cor, crit, n, _ = tally(ans)
                row.append(f"{cor}/{n}, {crit} crit")
        L.append("| " + " | ".join(row) + " |")
    L.append("")

    # Decisions.
    passes, verdict = {}, {}
    for c in ORDER[:-1]:
        ans = by.get((c, "L"), [])
        cor, crit, n, _ = tally(ans)
        passes[c] = n > 0 and crit == 0 and n - cor <= 1
        c_ans = by.get((c, "C"), [])
        legend_dep = passes[c] and any(a["critical"] for a in c_ans)
        strict = n > 0 and crit == 0 and cor * 16 >= 15 * n
        verdict[c] = (cor, crit, n, legend_dep, strict)
    L.append("## Decisions (2.6 rules 1 to 5)")
    L.append("")
    L.append("Rule 1 as sealed (README, Scoring): a construct passes when, in L, at most one of its answers is not "
             "correct and none is critical (the 15-of-16 allowance, applied to the answers that remain after the "
             "drops). The proportional reading (at least 15/16 of answers correct, none critical) is shown beside it "
             "and decides nothing.")
    L.append("")
    L.append("| Construct | L correct | L critical | Passes (rule 1) | Proportional | Legend-dependent | Decision |")
    L.append("|---|---|---|---|---|---|---|")
    for c in ORDER[:-1]:
        cor, crit, n, legend_dep, strict = verdict[c]
        if c in ("c3a", "c3b"):
            dec = "see rule 3"
        elif passes[c]:
            dec = "frozen as written (rule 2)" + ("; legend-dependent, re-test in W8" if legend_dep else "")
        else:
            dec = "pending wording (rule 4)"
        L.append(f"| {c} | {cor}/{n} | {crit} | {'yes' if passes[c] else 'no'} | {'yes' if strict else 'no'} | "
                 f"{'yes' if legend_dep else 'no'} | {dec} |")
    L.append("")
    a, b = passes["c3a"], passes["c3b"]
    if a:
        r3 = ("c3a passes: `leads to` stays, one word across `alternatives@0` and `risk@0`; c3a is frozen"
              + (" (legend-dependent, re-test in W8)" if verdict["c3a"][3] else "") + ".")
    elif b:
        r3 = ("c3a fails and c3b passes: risk environments render `certainly leads to`, and `leads to` is accepted "
              "as input and shown in that form" + (" (c3b legend-dependent, re-test in W8)" if verdict["c3b"][3]
                                                   else "") + ".")
    else:
        r3 = "c3a and c3b both fail: neither is frozen; `leads to` is pending wording (rule 4)."
    L.append(f"- **Rule 3 (`leads to` versus `certainly leads to`).** c3a {'passes' if a else 'fails'}, c3b "
             f"{'passes' if b else 'fails'}. {r3}")
    frozen = [c for c in ORDER[:-1] if passes[c] and c not in ("c3a", "c3b")]
    pending = [c for c in ORDER[:-1] if not passes[c] and c not in ("c3a", "c3b")]
    L.append("- **Rule 2 (frozen as written):** " + (", ".join(frozen) or "none") + ".")
    L.append("- **Rule 4 (pending wording):** " + (", ".join(pending) or "none") + "."
             + (" While " + ", ".join(p for p in pending if p in ("c10", "c11", "c12"))
                + " is pending, its profile word is not offered in risk environments; authors write its definition "
                "out in guards." if any(p in ("c10", "c11", "c12") for p in pending) else "")
             + (" The reviewers propose one replacement per failing construct, probed once with new sealed items."
                if pending or not (a or b) else ""))
    legend = [c for c in ORDER[:-1] if verdict[c][3]]
    L.append("- **Legend-dependent** (pass L with a critical answer in C): " + (", ".join(legend) or "none") + ".")
    ctl = by.get(("control-prevents", "L"), []) + by.get(("control-prevents", "C"), [])
    cor, crit, n, _ = tally(ctl)
    L.append(f"- **Rule 5 (`prevents` controls, informational):** {cor}/{n} answers chose the risk@0 reading, "
             f"{crit}/{n} the ordinary-English guarantee reading. The rejection of bare `prevents` stands.")
    L.append("")

    # Sessions.
    L.append("## Sessions")
    L.append("")
    L.append("| Session | CLI session id | Transport errors (retried) |")
    L.append("|---|---|---|")
    for m in sessions_meta:
        errs = m.get("transport_errors", [])
        L.append(f"| {m['session']} | {m.get('cli_session_id') or ('not run' if not m['ran'] else '?')} | "
                 f"{len(errs)}{': ' + '; '.join(e.get('summary', '') for e in errs) if errs else ''} |")
    L.append("")

    # Every answer.
    L.append("## Every answer")
    L.append("")
    L.append("`shown` is the letter the reader saw; `label` is the item's sealed option label. Verdict: correct, "
             "CRITICAL, wrong, or unparseable (wrong, not critical). The reason is the reader's block verbatim, "
             "whitespace collapsed.")
    L.append("")
    for c in ORDER:
        L.append(f"### {c}")
        L.append("")
        L.append("| Item | Cond | Reader | Session | Shown | Label | Key | Verdict | Reason |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        rows = sorted((a for a in answers if a["construct"] == c),
                      key=lambda a: (a["item"], a["condition"], a["family"], a["session"]))
        for a in rows:
            v = ("unparseable" if a["label"] is None else "correct" if a["correct"]
                 else "CRITICAL" if a["critical"] else "wrong")
            reason = a["reason"].replace("|", "\\|")
            L.append(f"| {a['item']} | {a['condition']} | {a['family']} | {a['session']} | {a['shown'] or '-'} | "
                     f"{a['label'] or '-'} | {a['key']} | {v} | {reason} |")
        L.append("")
    (HERE / "RESULTS.md").write_text("\n".join(L) + "\n")


def selftest():
    """Parser checks on hand-written response shapes (run before sealing)."""
    opts = {"a": "Data loss is not ruled out.", "b": "Data loss is more likely than not.",
            "c": "No data loss happens.", "d": "The text does not say."}
    cases = [
        ("**Text 1:** (b) Because it says so.\n\n**Text 2:** (a) Since (c) is wrong.", ["b", "a"]),
        ("1. **(c)** — reason one.\n2. a) reason two.", ["c", "a"]),
        ("Text 1\nAnswer: d — reason\n\nText 2\nAnswer: (A). reason", ["d", "a"]),
        ("## Text 1\n**b.** The text says so.\n## Text 2\n**Option c** — reason.", ["b", "c"]),
        ("Text 1: c\nText 2: a", ["c", "a"]),
        ("**1. (b)** reason\n**2. (d)** reason", ["b", "d"]),
        ("**Text 1**\n**b** — A lift failure is only possible.\n\n**Text 2**\nA server outage is likely.", ["b", None]),
        ("Text 1\nThe text does not say. Nothing gives a chance.\nText 2\n(c) reason", ["d", "c"]),
        ("Text 2: (a) reason", [None, "a"]),
    ]
    bad = 0
    for resp, want in cases:
        bl = blocks(resp, len(want))
        got = [pick(bl[n], opts)[0] if bl[n] is not None else None for n in range(1, len(want) + 1)]
        if got != want:
            bad += 1
            print("FAIL", repr(resp), got, want)
    print(f"selftest: {len(cases) - bad}/{len(cases)} passed")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    import sys
    selftest() if "--selftest" in sys.argv else main()
