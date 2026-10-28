"""Q1.4b's check of its saved A/B (plan Q1.4; DRI 2026-10-27 item 4).

The corpus, its recording and its comparison are Q1.4's (`../../q1-4/evidence/speech_ab.py write` and `compare`):
base.json is `write` at the merge base, head.json is `write` at this item's head, and delta.json is `compare` of
the two. An approved `verdict` row must be in exactly one of the DRI's three classes: (a) `gloss`, a declared gloss the base
read as its one predicate and Lean's lexicon refuses; (b) `folded`, a name the base matched after folding its case
and Lean refuses; (c) `quantified`, `Is every/some <sort> <rest>?`, which the base refused as `UnknownAlternative` and
Lean reads with a quantifier. A `class` or `wording` row must keep R1's (a) and (b) or be R2's rule O1, as in Q1.4.
A `lint` row fails, and so does a class whose count is not the decision's (10, 3 and 6), so an empty delta or a
head-against-head comparison fails too. `audit` checks the complete recorded corpus while allowing the ten new
verdicts to be marked pending; `check` fails until the DRI signs those verdicts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "q1-4" / "evidence"))

import speech_ab  # noqa: E402

NEGATIVE_SUBJECTS = ("atlas", "beacon")
SPECIAL_NAMES = ("atlas2", "atlas_two", "beacon2", "beacon_two")


def extra_cases() -> list[tuple[str, str, dict]]:
    """Environment/wording pairs missed by the original Cartesian corpus.

    Keep these outside Q1.4's corpus: that earlier batch's saved evidence is
    frozen.  Both spellings of service names and both subjects of a declared
    negative verbalisation exercise whole classes, not one reproducer.
    """
    from test_speech_acts import environment

    negative = environment().to_dict()
    negative["vocabulary"]["predicates"]["reviewed"]["negative_verbalisation"] = "{0} is not reviewed"
    named = environment().to_dict()
    for name in SPECIAL_NAMES:
        named["vocabulary"]["constants"][name] = {"sort": "service", "description": name}
    return ([("negative", f"Is {name} not reviewed?", negative) for name in NEGATIVE_SUBJECTS]
            + [("names", f"Is {spelling} reviewed?", named)
               for name in SPECIAL_NAMES
               for spelling in (name, f'"{name}"')])


def augment(source: str, out: str) -> None:
    """Append the new cases to a saved base/head corpus using this checkout's parser.

    VE_AB_ROOT selects the base parser when recording base answers; the corpus
    and this script always come from the current checkout.
    """
    from ve.environment import Environment

    rows = json.loads(Path(source).read_text())
    keys = {(row["env"], row["wording"]) for row in rows}
    for env_name, wording, raw in extra_cases():
        if (env_name, wording) in keys:
            raise ValueError(f"duplicate corpus case: {env_name}, {wording}")
        rows.append({"env": env_name, "wording": wording,
                     "outcome": speech_ab.outcome(Environment(raw), wording)})
    Path(out).write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n")

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


def pending(r: dict) -> str | None:
    """Verdict classes awaiting a DRI decision, named by the added corpus cases."""
    if r["class"] != "verdict":
        return None
    wording = r["wording"]
    base, head = r["base"], r["head"]
    body = head.get("content", {}).get("body")
    if r["env"] == "negative" and wording in {f"Is {name} not reviewed?" for name in NEGATIVE_SUBJECTS}:
        name = wording.split()[1]
        if base.get("code") == "SyntaxError" and body == ["not", ["unary", "reviewed", ["const", name]]]:
            return "negative"
    if r["env"] == "names":
        for name in SPECIAL_NAMES:
            atom = ["unary", "reviewed", ["const", name]]
            if wording == f"Is {name} reviewed?" and base.get("content", {}).get("body") == atom \
                    and head.get("code") == "SyntaxError":
                return "bare_name"
            if wording == f'Is "{name}" reviewed?' and base.get("code") == "InvalidInput" and body == atom:
                return "quoted_name"
    return None


PENDING_COUNTS = {"negative": len(NEGATIVE_SUBJECTS), "bare_name": len(SPECIAL_NAMES),
                  "quoted_name": len(SPECIAL_NAMES)}


def check(delta_path: str, *, allow_pending: bool = False) -> int:
    rows = json.loads(Path(delta_path).read_text())["rows"]
    counts = {name: sum(map(test, rows)) for name, test in CLASSES.items()}
    pending_counts = {name: sum(pending(r) == name for r in rows) for name in PENDING_COUNTS}
    refusals = [r for r in rows if r["class"] in ("class", "wording")]
    bad = [r for r in rows if r["class"] == "lint"
           or r["class"] == "verdict" and sum(test(r) for test in CLASSES.values()) + (pending(r) is not None) != 1
           or r in refusals and not speech_ab.order_o1(r) and not speech_ab.keeps(r)]
    for r in bad:
        print("fails:", r["class"], r["env"], repr(r["wording"]), r["base"].get("message"), "->",
              r["head"].get("message"))
    o1 = [r for r in refusals if speech_ab.order_o1(r)]
    print(json.dumps({"rows": len(rows), **counts, **pending_counts, "O1": len(o1),
                      "R1": len(refusals) - len(o1), "failing": len(bad),
                      "pending_signature": sum(pending_counts.values())}))
    return 1 if bad or counts != DECIDED or pending_counts != PENDING_COUNTS or (
        not allow_pending and sum(pending_counts.values()) > 0) else 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["augment"] and len(sys.argv) == 4:
        augment(sys.argv[2], sys.argv[3])
    elif sys.argv[1:2] not in (["check"], ["audit"]) or len(sys.argv) != 3:
        raise SystemExit(__doc__)
    else:
        raise SystemExit(check(sys.argv[2], allow_pending=sys.argv[1] == "audit"))
