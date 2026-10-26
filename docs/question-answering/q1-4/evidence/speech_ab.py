"""Q1.4's A/B over the speech-acts corpus (plan Q1.4, 6.4): `parse_speech`'s content, kind and lint, or refusal.

`write OUT` records the corpus (the polar, `Must` and `Can` wordings of tests/test_speech_acts*.py with case, spacing
and Unicode variants, the declared glosses, controls; each `Is <…>?` wording as F1 with `is` put back at every gap;
F1 at, below and over the question limits of bytes and tokens) in every environment; set `VE_AB_ROOT` to record it
with another checkout's parser (the merge base's, for the base); `write-f2 OUT` adds `Is ` to the routed
prefixes (Q1.4b's move). `compare BASE HEAD OUT` classes each difference `verdict`, `class`, `wording` or `lint`.
`check DELTA` exits 1 on a `lint` row, a `verdict` row other than V1's (`over_limit`), or a `class` or `wording`
row that is not I1's (`indefinite`), R2's rule O1 (`order_o1`) or L1 (`over_limit`), and does not keep R1's (a) and
(b): every name the base quoted, and a span wherever the base had one. V1 and I1 are reserved for the DRI (DELTA.md).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("VE_AB_ROOT") or Path(__file__).resolve().parents[4])
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]

from ve.environment import Environment  # noqa: E402
from ve.errors import VEError  # noqa: E402
from ve.speech_english import parse_speech  # noqa: E402

GLOSSES = [("contradictory", "{0} is reviewed and not reviewed"), ("atlas_linked", "{0} is linked to atlas"),
           ("desk_near", "{0} is near the desk"), ("yet_never", "{0} is reviewed yet never reviewed"),
           ("comma", "{0} is vetted, sadly"), ("twice", "{0} is vetted really vetted"),
           ("staffed", "{0} is reviewed by staff"), ("despite", "{0} is reviewed despite remaining unreviewed"),
           ("vetted", "{0} is vetted")]
SPACES = [" ", "\t", "\n", "\r", "\x0b", "\x0c", "\x1c", "\x1f", "\x85", "\xa0", " ", "　", "\x00", "\x7f"]


def environments() -> dict[str, dict]:
    from test_speech_acts import environment
    from test_speech_acts_lean import F0
    glossed = environment().to_dict()
    for name, gloss in GLOSSES:
        glossed["vocabulary"]["predicates"][name] = {"arguments": ["service"], "description": name,
                                                     "verbalisation": gloss}
    out = {"speech": environment().to_dict(), "glossed": glossed}
    for name, gloss in [("f0-reviewed", "{0} is reviewed"), ("f0-checked", "{0} is checked")]:
        env = F0()
        env["vocabulary"]["predicates"]["reviewed"]["verbalisation"] = gloss
        env["vocabulary"]["predicates"]["cat"]["verbalisation"] = "{0} is a cat"
        out[name] = env
    return out


def wordings() -> list[str]:
    polar = ["Is atlas reviewed?", "Is beacon reviewed?", "Is atlas checked?", "Is it the case that atlas is reviewed?",
             "Is it the case that atlas is checked?", "Is it the case that every service is reviewed?",
             "Is it the case that atlas is reviewed and beacon is reviewed?", "Is it the case that tom is a cat?",
             "Is tom a cat?", "Is every service reviewed?", "Is some service reviewed?", "Is atlas not reviewed?",
             "Is token1 reviewed?", "Is the token reviewed?", "Is atlas?", "Is ?", "Is atlas reviewed", "Is",
             "Is it the case that?", "Is it the case that atlas is reviewed", "Is atlas reviewed??",
             "Is atlas reviewed? Is beacon reviewed?", "Is it the case that atlas is reviewed. Beacon is reviewed?",
             "Is atlas vetted?", "Is atlas reviewed by staff?", "Is atlas reviewed and not reviewed?",
             "Is atlas linked to atlas?", "Is beacon near the desk?", "Is atlas reviewed yet never reviewed?",
             "Is atlas vetted, sadly?", "Is atlas vetted really vetted?",
             "Is atlas reviewed despite remaining unreviewed?", "Is it the case that atlas is vetted?",
             "Is it the case that atlas is reviewed despite remaining unreviewed?", "Is Atlas reviewed?",
             "Is ATLAS reviewed?", "Is atlas Reviewed?", "Is a service reviewed?", "Is alice reviewed?",
             "Is it the case that therefore atlas is reviewed?", "Is atlas reviewed, therefore?"]
    modal = ["Must alice open the desk?", "Can alice open the desk?", "Can check.", "Must check.", "Must", "Can",
             "Must ", "Can ?", "Must alice?", "Mustard is reviewed?", "Canned check.", "must alice open the desk?",
             "can check.", "MUST check.", "May alice open the desk?", "Must\talice open the desk?"]
    controls = ["Atlas is reviewed.", "Atlas is reviewed?", "Click check.", "Do not click check.", "Open the desk.",
                "Do not share the token.", "Which one of atlas and beacon is reviewed?",
                "Which of atlas and beacon are reviewed?", "Which services are reviewed?", "You may open the desk.",
                "Please click check.", "Prove that atlas is reviewed using these premises.",
                "Does it follow from these premises that atlas is reviewed?", "Which reading did you mean?",
                "In this task, you are alice.", "Does atlas click?"]
    variants = set(polar) | set(modal) | set(controls) | {f for w in polar for f in f1_forms(w)} | set(limits())
    for base in ["Is atlas reviewed?", "Is it the case that atlas is reviewed?", "Must alice open the desk?",
                 "Can check.", "Is atlas checked?"]:
        variants |= {base.upper(), base.lower(), base.swapcase()}
        for c in SPACES + ["ſ", "K"]:
            variants |= {c + base, base + c, base.replace(" ", c, 1), base.replace(" ", c + c),
                         base.replace("s", c, 1), base.replace("k", c, 1)}
    return sorted(variants)


def f1_forms(wording: str) -> list[str]:
    """`Is <…>?` as F1 with `is` put back at every gap between its words (the F1 counterparts of F2's candidates)."""
    if not wording.startswith("Is ") or not wording.endswith("?") or wording.startswith(F1):
        return []
    words = wording[3:-1].split(" ")
    if not all(words):
        return []
    return [F1 + " ".join(words[:i] + ["is"] + words[i:]) + "?" for i in range(1, len(words) + 1)]


def limits() -> list[str]:
    """F1 below, at and over the question limits (`VE.Question.maxTokens` 300, `maxQuestionBytes` 4096): nested
    negations (6 tokens each; 49 is the last that fits), and an unknown word or a run of spaces padding the
    question to 4095, 4096 and 4097 bytes."""
    bodies = ("atlas is reviewed", "atlas is checked", "a service is reviewed", "therefore atlas is reviewed")
    nested = [F1 + "it is not the case that " * n + body + "?" for n in (49, 50, 55) for body in bodies]
    padded = []
    for size in (4095, 4096, 4097):
        word = F1 + "atlas is "
        padded.append(word + "x" * (size - len(word) - 1) + "?")
        head, tail = F1 + "atlas is", "reviewed?"
        padded.append(head + " " * (size - len(head) - len(tail)) + tail)
    return nested + padded


def outcome(env, wording: str) -> dict:
    lint: list[str] = []
    try:
        content, kind = parse_speech(env, wording, env.speech_acts, warnings=lint)
    except VEError as exc:
        return {"error": type(exc).__name__, **exc.to_dict()}
    return {"kind": kind, "content": content, "warnings": lint}


def write_f2(out: str) -> None:
    import ve.speech_english
    ve.speech_english._LEAN_PREFIXES += ("Is ",)
    write(out)


def write(out: str) -> None:
    records = [{"env": name, "wording": w, "outcome": outcome(Environment(env), w)}
               for name, env in environments().items() for w in wordings()]
    Path(out).write_text(json.dumps(records, indent=1, sort_keys=True) + "\n")


def kind_of(base: dict, head: dict) -> str | None:
    if base == head:
        return None
    if ("error" in base) != ("error" in head) or "error" not in base and (
            base["kind"], base["content"]) != (head["kind"], head["content"]):
        return "verdict"
    if "error" not in base:
        return "lint"
    return "class" if (base["error"], base["code"]) != (head["error"], head["code"]) else "wording"


def compare(base_path: str, head_path: str, out: str) -> None:
    base, head = (json.loads(Path(p).read_text()) for p in (base_path, head_path))
    keys = [(r["env"], r["wording"]) for r in base]
    if keys != [(r["env"], r["wording"]) for r in head]:
        raise SystemExit("the two runs do not cover the same corpus")
    rows = [{"class": k, "env": b["env"], "wording": b["wording"], "base": b["outcome"], "head": h["outcome"]}
            for b, h in zip(base, head) if (k := kind_of(b["outcome"], h["outcome"])) is not None]
    counts = {k: sum(r["class"] == k for r in rows) for k in ("verdict", "class", "wording", "lint")}
    Path(out).write_text(json.dumps({"records": len(base), "counts": counts, "rows": rows}, indent=1,
                                    sort_keys=True) + "\n")
    print(json.dumps({"records": len(base), **counts}))


def quoted(text: str) -> set[str]:
    return {a or b for a, b in re.findall(r"'([^']+)'|\"([^\"]+)\"", text)}


NOT_ONE = "Write one question that ends with a question mark."
TOO_LONG = "The question is longer than VE reads. Ask a shorter question."
INDEFINITE = re.compile(r'VE cannot tell whether "an?" here means every or some\. Ask one of these instead:\n')
F1 = "Is it the case that "


def order_o1(r: dict) -> bool:
    """R2's rule O1: the head refuses a wording of more than one sentence, or with more than one `?`, as not one
    question (`NotOneQuestion`) before any of its sentences is lexed."""
    body = r["wording"].removeprefix("Is it the case that ")[:-1]
    return r["head"]["message"] == NOT_ONE and (re.search(r"[.?] ", body) is not None or r["wording"].count("?") > 1)


def over_limit(r: dict) -> bool:
    """V1 (a `verdict` row, reserved for the DRI) and R2's rule L1 (a `class` row): the head refuses an F1 question
    over the question limits of bytes or tokens as `QuestionTooLong` before its body is read."""
    return r["head"].get("message") == TOO_LONG and r["head"]["code"] == "ResourceLimit" and r["wording"] in limits()


def indefinite(r: dict) -> bool:
    """I1 (a `wording` row, reserved for the DRI): the head is the question reader's row 14 (`IndefiniteQuestion`,
    spec 4.1), which offers the every and the some rephrasings in place of E2's diagnosis; the base's nearest declared
    wordings are not in it."""
    return r["class"] == "wording" and INDEFINITE.match(r["head"]["message"]) is not None


def keeps(r: dict) -> bool:
    """R1 (a) and (b): every name the base quoted, and a span wherever the base had one."""
    shown = {w for q in quoted(r["head"]["message"]) for w in [q, *q.split()]} | set(r["head"]["message"].split())
    return quoted(r["base"]["message"]) <= shown and ("span" in r["base"]) <= ("span" in r["head"])


def check(delta_path: str) -> int:
    rows = json.loads(Path(delta_path).read_text())["rows"]
    bad = [r for r in rows if r["class"] == "lint" or not over_limit(r) and not indefinite(r) and (
        r["class"] == "verdict" or not order_o1(r) and not keeps(r))]
    for r in bad:
        print("fails:", r["class"], r["env"], repr(r["wording"]), r["base"].get("message"), "->",
              r["head"].get("message"))
    print(json.dumps({"rows": len(rows), "O1": sum(map(order_o1, rows)),
                      "V1": sum(over_limit(r) and r["class"] == "verdict" for r in rows),
                      "L1": sum(over_limit(r) and r["class"] != "verdict" for r in rows),
                      "I1": sum(map(indefinite, rows)), "failing": len(bad)}))
    return 1 if bad else 0


if __name__ == "__main__":
    command, *paths = sys.argv[1:]
    if command == "write":
        write(*paths)
    elif command == "write-f2":
        write_f2(*paths)
    elif command == "compare":
        compare(*paths)
    elif command == "check":
        raise SystemExit(check(*paths))
    else:
        raise SystemExit(__doc__)
