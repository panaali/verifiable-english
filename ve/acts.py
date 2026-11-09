"""Lean's readings of one act phrase under a rule's modal words (act-phrases 7, AP-4): the relay of the
`act-readings` service mode (`lean/VE/Acts/Run.lean`, `runActReadings`).

Lean lexes the phrase, lists its readings (`phraseReadings`) and paraphrases them, and writes each token's UTF-8 byte
span and each act's token indices. This module builds the request, relays the row and checks only what a relay checks
(DRI ruling R8): the row's schema (`act-readings.json`, which bounds the readings at Lean's 64) and its binding to the
request, exactly spec 7's list and R8's "no row empty": the readings are non-empty exactly when the verdict is
`LISTED`; every span lies within the phrase's UTF-8 bytes, in order and disjoint; every `from` index names a token,
none twice in one act; no two readings have the same acts (as JSON values) or the same paraphrase; no reading, act,
text or diagnostic is empty. Which acts a reading lists, an act twice included (spec E16 reads one act written twice),
is Lean's content. It lexes nothing, composes no text and coerces no request value: the CLI's `--acts` block is sent
as written, so Lean's decoder refuses a member of the wrong type. Binding cannot see a reading dropped with
its row (spec 7, "What binding cannot show"): that is Lean's content (`phraseReadings_exact`).
"""
from __future__ import annotations

import json

from .errors import CheckerUnavailable, ResourceLimit, VEError

MODE = "act-readings"


def _as_sent(value):
    """A request member as the caller wrote it: a tuple as the JSON list it stands for, anything else unchanged, so
    that Lean's decoder, not a coercion here, decides whether it is well typed (a string is never split into its
    letters, a number never iterated)."""
    return list(value) if type(value) is tuple else value


def request(phrase: str, *, fixed=(), frames=(), adverbs=(), role: str = "plain", sign: bool = True,
            form: str | None = None, case_id: str = MODE) -> dict:
    """The mode's request (spec 7): the phrase, the `acts` block's fixed phrases, frames and adverbs as data, and the
    rule's role, sign and (for a plain act) form, absent when `None`. No member is coerced (`_as_sent`)."""
    case = {"id": case_id, "phrase": phrase, "fixed": _as_sent(fixed), "frames": _as_sent(frames),
            "adverbs": _as_sent(adverbs), "role": role, "sign": sign}
    return case if form is None else {**case, "form": form}


def _value(value) -> str:
    """A JSON value's canonical text: equal values, whatever their keys' order, have one."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def answer_problem(row, case: dict) -> str | None:
    """Why Lean's `act-readings` row is not an answer to `case` (R8: its binding to the request), or None."""
    if (type(row) is not dict or row.get("status") != "ok" or row.get("id") != case["id"]
            or type(case.get("phrase")) is not str):
        return "the row is not an answer to this case"
    readings, tokens, verdict = row.get("readings"), row.get("tokens"), row.get("verdict")
    if type(readings) is not list or type(tokens) is not list:
        return "the readings or tokens are not lists"
    if (verdict == "LISTED") != bool(readings) or (verdict != "LISTED") and tokens:
        return "the readings are not non-empty exactly when the verdict is LISTED"
    end = 0
    for span in tokens:
        if (type(span) is not list or len(span) != 2 or any(type(x) is not int for x in span)
                or not end <= span[0] < span[1] <= len(case["phrase"].encode("utf-8"))):
            return "a token span is not within the phrase, in order and disjoint"
        end = span[1]
    for reading in readings:
        if not reading["acts"] or not reading["paraphrase"]:
            return "a reading has no acts or no paraphrase"
        for act in reading["acts"]:
            if not act["act"] or not act["text"] or not act["from"]:
                return "an act has no text or no tokens"
            if any(not 0 <= i < len(tokens) for i in act["from"]):
                return "a token index is out of range"
            if len(set(act["from"])) != len(act["from"]):
                return "a token index occurs twice in one act"
    if verdict != "LISTED" and not row.get("diagnostic"):
        return "a refusal has no diagnostic"
    if len({_value(r["acts"]) for r in readings}) != len(readings):
        return "two readings have the same acts"
    if len({r["paraphrase"] for r in readings}) != len(readings):
        return "two readings have the same paraphrase"
    return None


def read_answer(row, case: dict) -> dict:
    """Lean's answer `row` to `case` after the schema check (`act-readings.json`) and the binding check
    (`answer_problem`)."""
    from .backends.service_schema import Invalid, check_row
    try:
        check_row(MODE, row, case, 0)
    except Invalid as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: Lean's act-readings answer does not fit its schema: {exc}") from None
    problem = answer_problem(row, case)
    if problem is not None:
        raise CheckerUnavailable(f"CheckerUnavailable: Lean's act-readings answer is not bound to its request: {problem}")
    return {key: row[key] for key in ("verdict", "tokens", "readings", "diagnostic") if key in row}


def readings(phrase: str, **request_fields) -> dict:
    """Lean's readings of `phrase` (`request` names the fields): verdict, token spans, readings and diagnostic."""
    from .backends.relay import decide_once
    case = request(phrase, **request_fields)
    return read_answer(decide_once(MODE, case), case)


BLOCK_MEMBERS = ("fixed", "frames", "adverbs")


def read_block(path: str) -> dict:
    """The `--acts` file (`-` for standard input), read as `ve calc` reads its case (at most the package size cap,
    then `loads_json`): one JSON object whose members are among the acts block's `fixed`, `frames` and `adverbs`;
    their values are sent to Lean as written (`_as_sent`)."""
    import sys
    from pathlib import Path
    from .limits import MAX_PACKAGE_BYTES
    from .wire import loads_json
    if path == "-":
        data = sys.stdin.buffer.read(MAX_PACKAGE_BYTES + 1)
    else:
        with Path(path).open("rb") as stream:
            data = stream.read(MAX_PACKAGE_BYTES + 1)
    block = loads_json(data)  # over the package cap: `loads_json`'s ResourceLimit
    # A file that is no acts block cannot become a request (relay lint: file I/O, as `ve.ask` reads its evidence).
    if type(block) is not dict:
        raise VEError("the --acts file is not a JSON object with fixed, frames and adverbs")  # relay-lint: file I/O
    extra = ", ".join(sorted(set(block) - set(BLOCK_MEMBERS)))
    if extra:
        raise VEError(f"the --acts file has members other than fixed, frames and adverbs: {extra}")  # relay-lint: file I/O
    return block


def main(argv: list[str]) -> int:
    """`ve acts readings PHRASE [--acts FILE] [--role R] [--negated] [--form F]`: Lean's readings of an act phrase
    under the rule's modal, as JSON. Exit 0 when Lean listed them, 2 when it refused the phrase or the request is
    invalid (an unreadable, malformed or oversized `--acts` file, or a member Lean's decoder refuses), 4 at a limit;
    an unavailable checker is the caller's exit 5."""
    import argparse
    parser = argparse.ArgumentParser(prog="python -m ve acts")
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("readings", help="an act phrase's readings and paraphrases under a modal")
    listing.add_argument("phrase", help='the act phrase, "{0} ..."')
    listing.add_argument("--acts", help="JSON of the acts block: fixed, frames and adverbs")
    listing.add_argument("--role", default="plain", choices=["plain", "permission", "obligation"])
    listing.add_argument("--negated", action="store_true", help="the rule's sign is false (must not, need not)")
    listing.add_argument("--form", choices=["has the right", "is entitled"], help="a plain act's form")
    options = parser.parse_args(argv)
    try:
        block = read_block(options.acts) if options.acts else {}
        found = readings(options.phrase, **{k: block[k] for k in BLOCK_MEMBERS if k in block}, role=options.role,
                         sign=not options.negated, form=options.form)
    except CheckerUnavailable:
        raise
    except VEError as exc:
        limit = exc.code == ResourceLimit.code
        print(json.dumps({"status": "ResourceLimit" if limit else "InvalidInput", "error": exc.to_dict()},
                         ensure_ascii=False, indent=2))
        return 4 if limit else 2
    except (OSError, UnicodeError) as exc:
        print(json.dumps({"status": "InvalidInput", "error": {"code": "InvalidInput", "message": str(exc)}},
                         ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(found, ensure_ascii=False, indent=2))
    return {"LISTED": 0, "REFUSED": 2}.get(found["verdict"], 4)
