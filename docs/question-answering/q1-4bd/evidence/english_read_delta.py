"""q1-4bd: the `english.read` relay's refusals before and after it stopped adding a code to Lean's text.

    uv run python docs/question-answering/q1-4bd/evidence/english_read_delta.py record base.json   # at the base
    uv run python docs/question-answering/q1-4bd/evidence/english_read_delta.py record head.json   # at the head
    uv run python docs/question-answering/q1-4bd/evidence/english_read_delta.py delta              # delta.json
    uv run python docs/question-answering/q1-4bd/evidence/english_read_delta.py check              # exit 1 on a problem

The corpus is the S3 fixtures (`conformance/english_lean_s3_python._fixtures`, spec 8 of english-lean) and, in each
S3 environment, `ILL_TYPED`'s documents, which put a reach sentence (a formula outside a family without `closure@0`)
at several places. Each record is the public outcome of `ve.english.parse_english`: the class and `to_dict()` of the
refusal, or the canonical text of the reading. `check` reads the saved files only.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[3]
PREFIX = "TypeMismatch: "
REACH = ("Starting from legacy, legacy is reachable by zero or more steps, where a step from a service to a second "
         "service satisfies this condition: that service is deployed.")
ILL_TYPED = (REACH, f"Legacy is deployed. {REACH}", f"Legacy is deployed.\n{REACH}",
             f"Legacy is deployed.\n\n{REACH} Legacy is deployed.", f"{REACH} {REACH}",
             f"Legacy is deployed. Legacy is deployed. {REACH}")


def cases() -> list[tuple[str, str, str]]:
    """(id, environment, text) of every recorded document."""
    sys.path.insert(0, str(ROOT))
    from conformance.english_lean_s3_fixtures import BUILDERS
    from conformance.english_lean_s3_python import _fixtures
    return ([(fid, env, text) for fid, env, text, _ in _fixtures()]
            + [(f"it{i}-{env}", env, text) for env in BUILDERS for i, text in enumerate(ILL_TYPED, 1)])


def outcome(env_name: str, text: str) -> dict:
    """The public outcome of one document."""
    import warnings
    from conformance.english_lean_s3_python import environment_json
    from ve import Environment, english
    from ve.errors import CheckerUnavailable, VEError
    from ve.printer import print_document
    env = Environment(environment_json(env_name))
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", english.UnreviewedVocabularyWarning)
            document = english.parse_english(env, text)
    except (VEError, CheckerUnavailable) as error:
        return {"class": type(error).__name__, **error.to_dict()}
    return {"class": "accepted", "canonical": print_document(env, document)}


def record() -> list[dict]:
    return [{"id": fid, "env": env, "text": text, "outcome": outcome(env, text)} for fid, env, text in cases()]


def delta_rows(base: list[dict], head: list[dict]) -> list[dict]:
    """Every record whose outcome moved, with both outcomes."""
    return [{"id": b["id"], "env": b["env"], "base": b["outcome"], "head": h["outcome"]}
            for b, h in zip(base, head) if b["outcome"] != h["outcome"]]


def quoted(text: str) -> list[str]:
    return re.findall(r"'([^']*)'", text)


def problems(base: list[dict], head: list[dict], delta: dict) -> list[str]:
    """Why the saved records are not this item's delta: each moved record lost only the code Python added to
    Lean's `TypeMismatch` text (R1: same class, span and quoted names), and nothing else moved."""
    out = []
    if [(r["id"], r["env"], r["text"]) for r in base] != [(r["id"], r["env"], r["text"]) for r in head]:
        out.append("base and head record different documents")
    if delta.get("rows") != delta_rows(base, head):
        out.append("delta.json is not the difference of base and head")
    if not delta.get("rows"):
        out.append("the delta is empty")
    for row in delta.get("rows", ()):
        b, h = row["base"], row["head"]
        if not (b["class"] == "TypeMismatch" and b["message"].startswith(PREFIX)
                and h == {**b, "message": b["message"].removeprefix(PREFIX)}):
            out.append(f"{row['id']}: moved by more than the dropped prefix")
        if "span" not in h or not all(name in h["message"] for name in quoted(b["message"])):
            out.append(f"{row['id']}: the head lost the base's span or a quoted name")
    for r in head:
        if r["outcome"]["class"] != "accepted" and r["outcome"]["message"].startswith(PREFIX):
            out.append(f"{r['id']}: the head still adds the code")
    return out


def _load(name: str):
    return json.loads((EVIDENCE / name).read_text())


def main(argv: list[str]) -> int:
    if argv[:1] == ["record"] and len(argv) == 2:
        (EVIDENCE / argv[1]).write_text(json.dumps(record(), indent=1, ensure_ascii=False) + "\n")
        return 0
    if argv == ["delta"]:
        rows = delta_rows(_load("base.json"), _load("head.json"))
        (EVIDENCE / "delta.json").write_text(json.dumps({"rows": rows}, indent=1, ensure_ascii=False) + "\n")
        return 0
    if argv == ["check"]:
        found = problems(_load("base.json"), _load("head.json"), _load("delta.json"))
        print("\n".join(found) or "OK")
        return 1 if found else 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
