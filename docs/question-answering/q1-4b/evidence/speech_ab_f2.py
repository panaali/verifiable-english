"""Q1.4b's check of its saved A/B (plan Q1.4; DRI 2026-10-27 item 4): `check DELTA` exits 1 unless every row is covered.

The corpus, its recording and its comparison are Q1.4's (`../../q1-4/evidence/speech_ab.py write` and `compare`):
base.json is `write` at the merge base, head.json is `write` at this item's head, and delta.json is `compare` of
the two. A `verdict` row must be in exactly one of the DRI's three classes: (a) `gloss`, a declared gloss the base
read as its one predicate and Lean's lexicon refuses; (b) `folded`, a name the base matched after folding its case
and Lean refuses; (c) `quantified`, `Is every/some <sort> <rest>?`, which the base refused as `UnknownAlternative` and
Lean reads with a quantifier. A `class` or `wording` row must keep R1's (a) and (b) or be R2's rule O1, as in Q1.4.
A `lint` row fails, and so does a class whose count is not the decision's (10, 3 and 6), so an empty delta or a
head-against-head comparison fails too.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "q1-4" / "evidence"))

import speech_ab  # noqa: E402

GLOSS_PREDICATES = {name for name, _ in speech_ab.GLOSSES} | {"cat"}


def _named(r: dict) -> tuple[str, str] | None:
    """The name as the wording writes it and the constant the base read, for a base polar reading of one constant."""
    body = r["base"].get("content", {}).get("body")
    if r["base"].get("kind") != "question" or type(body) is not list or body[0] != "unary":
        return None
    return r["wording"].split(" ")[1], body[2][1]


def gloss(r: dict) -> bool:
    named = _named(r)
    return (r["class"] == "verdict" and named is not None and named[0] == named[1]
            and r["base"]["content"]["body"][1] in GLOSS_PREDICATES and r["head"].get("code") == "SyntaxError")


def folded(r: dict) -> bool:
    named = _named(r)
    return (r["class"] == "verdict" and named is not None and named[0] != named[1]
            and named[0].casefold() == named[1] and named[0] != named[1].capitalize()
            and r["head"].get("code") == "SyntaxError")


def quantified(r: dict) -> bool:
    word = r["wording"].split(" ")[1]
    body = r["head"].get("content", {}).get("body")
    return (r["class"] == "verdict" and word in ("every", "some") and r["wording"].startswith("Is ")
            and r["base"].get("message") == f"UnknownAlternative: wording, {word}" and type(body) is list
            and body[0] == {"every": "forall", "some": "exists"}[word])


CLASSES = {"gloss": gloss, "folded": folded, "quantified": quantified}
DECIDED = {"gloss": 10, "folded": 3, "quantified": 6}  # reviews/dri-decisions-20261027-featureplan-gates.md item 4


def check(delta_path: str) -> int:
    rows = json.loads(Path(delta_path).read_text())["rows"]
    counts = {name: sum(map(test, rows)) for name, test in CLASSES.items()}
    refusals = [r for r in rows if r["class"] in ("class", "wording")]
    bad = [r for r in rows if r["class"] == "lint"
           or r["class"] == "verdict" and sum(test(r) for test in CLASSES.values()) != 1
           or r in refusals and not speech_ab.order_o1(r) and not speech_ab.keeps(r)]
    for r in bad:
        print("fails:", r["class"], r["env"], repr(r["wording"]), r["base"].get("message"), "->",
              r["head"].get("message"))
    o1 = [r for r in refusals if speech_ab.order_o1(r)]
    print(json.dumps({"rows": len(rows), **counts, "O1": len(o1), "R1": len(refusals) - len(o1),
                      "failing": len(bad)}))
    return 1 if bad or counts != DECIDED else 0


if __name__ == "__main__":
    if sys.argv[1:2] != ["check"] or len(sys.argv) != 3:
        raise SystemExit(__doc__)
    raise SystemExit(check(sys.argv[2]))
