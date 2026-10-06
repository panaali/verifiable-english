"""Admission through the Lean senses reader.

Python transports pack bytes and checks the shape and identity of the answer.
It does not select a sense or turn an unavailable checker into a verdict.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import time

from .. import ast
from ..backends.lean import NoAnswer, ROUTE_TIMEOUT, configured_timeout, read_rows
from ..environment import Environment
from ..errors import CheckerUnavailable, VEError
from ..english import EnglishVocabulary
from ..english_grammar import export
from ..wire import canonical_json, digest, loads_json

ROOT = Path(__file__).resolve().parents[2]
EXECUTABLE = ROOT / "lean/.lake/build/bin/ve_senses_route"
WORK_BUDGET = 2_100_000  # VE.EnglishGrammar.workBudget; checked against compiled Lean in tests.
STATUSES = {"one", "open", "none", "many", "rejected", "budget", "invalidGrammar"}


def _nat(value) -> bool:
    return type(value) is int and value >= 0


def _text(raw: bytes) -> str:
    if type(raw) is not bytes:
        raise VEError("A sense pack must be bytes")
    try:
        return raw.decode("utf-8")
    except UnicodeError as exc:
        raise VEError("A sense pack is not UTF-8") from exc


def _response_problem(response: object, expected_id: str, request_id: str) -> str | None:
    if type(response) is not dict or response.keys() != {"request_id", "dictionary_id", "reading"}:
        return "the result does not have request and dictionary identities and a reading"
    if type(response["request_id"]) is not str or response["request_id"] != request_id:
        return "the request identity does not match the submitted envelope"
    if type(response["dictionary_id"]) is not str or response["dictionary_id"] != expected_id:
        return "the dictionary identity does not match the request"
    reading = response["reading"]
    if type(reading) is not dict or type(reading.get("status")) is not str \
            or reading["status"] not in STATUSES:
        return "the reading has no known status"
    if reading["status"] in {"one", "open"}:
        if reading.keys() != {"status", "code", "units", "sense_map", "mixed", "unused", "environment"} \
                and reading.keys() != {"status", "units", "sense_map", "mixed", "unused", "environment"}:
            return "an admitted reading has missing or unknown fields"
        if (reading.get("code") != "Unresolved" if reading["status"] == "open" else "code" in reading):
            return "an admitted reading has the wrong code"
        if (type(reading["units"]) is not list or not reading["units"]
                or type(reading["sense_map"]) is not list or type(reading["mixed"]) is not list
                or type(reading["unused"]) is not list or type(reading["environment"]) is not dict):
            return "an admitted reading has malformed collections"
        try:
            projected = Environment(reading["environment"])
        except VEError:
            return "the projected environment is invalid"
        for unit in reading["units"]:
            if type(unit) is not dict or unit.keys() not in (
                    {"candidates", "unresolved"}, {"candidates", "unresolved", "formula", "mark"}) \
                    or type(unit["candidates"]) is not list or type(unit["unresolved"]) is not list \
                    or len(unit["candidates"]) > 8 \
                    or not all(type(word) is str for word in unit["unresolved"]) \
                    or len(set(unit["unresolved"])) != len(unit["unresolved"]):
                return "a unit is malformed"
            resolved = {"formula", "mark"} <= unit.keys()
            if resolved == bool(unit["candidates"]):
                return "a unit is neither resolved nor open, or both"
            if resolved and type(unit["mark"]) is not bool:
                return "a unit mark is not Boolean"
            if resolved:
                try:
                    ast.formula_from_data(projected, unit["formula"])
                except VEError:
                    return "a resolved formula is invalid under the projected environment"
            choices = []
            for candidate in unit["candidates"]:
                if type(candidate) is not dict or candidate.keys() != {"choice", "lines", "formula", "mark"} \
                        or type(candidate["choice"]) is not list or not candidate["choice"] \
                        or type(candidate["lines"]) is not str or type(candidate["mark"]) is not bool:
                    return "a candidate is malformed"
                if not all(type(pair) is list and len(pair) == 2 and type(pair[0]) is str
                           and _nat(pair[1]) and pair[1] > 0 for pair in candidate["choice"]):
                    return "a candidate choice is malformed"
                if [pair[0] for pair in candidate["choice"]] != unit["unresolved"]:
                    return "a candidate choice does not name the unresolved words"
                choices.append(tuple(map(tuple, candidate["choice"])))
                try:
                    ast.formula_from_data(projected, candidate["formula"])
                except VEError:
                    return "a candidate formula is invalid under the projected environment"
            if len(choices) != len(set(choices)):
                return "candidate choices are duplicated"
        if (reading["status"] == "one") != all(not u["candidates"] for u in reading["units"]):
            return "the status disagrees with the units"
        for occurrence in reading["sense_map"]:
            if type(occurrence) is not dict or occurrence.keys() not in (
                    {"sentence", "token_start", "token_stop", "symbol", "is_default"},
                    {"sentence", "token_start", "token_stop", "symbol", "is_default", "candidate"}) \
                    or not all(_nat(occurrence[key]) for key in ("sentence", "token_start", "token_stop")) \
                    or occurrence["token_stop"] <= occurrence["token_start"] \
                    or type(occurrence["symbol"]) is not str \
                    or occurrence["symbol"] not in projected.predicates \
                    or type(occurrence["is_default"]) is not bool \
                    or ("candidate" in occurrence and not _nat(occurrence["candidate"])):
                return "a sense-map occurrence is malformed"
        if not all(type(pair) is list and len(pair) == 2 and type(pair[0]) is str
                   and type(pair[1]) is list and len(pair[1]) >= 2
                   and all(type(symbol) is str and symbol in projected.predicates for symbol in pair[1])
                   for pair in reading["mixed"]):
            return "mixed senses are malformed"
        if not all(type(word) is str for word in reading["unused"]):
            return "unused words are malformed"
    else:
        if reading.keys() != {"status", "code"} and reading.keys() != {"status", "code", "failure"}:
            return "a refused reading has missing or unknown fields"
        if type(reading["code"]) is not str or not reading["code"]:
            return "a refused reading has no code"
        if "failure" in reading and not (type(reading["failure"]) is list and len(reading["failure"]) == 3
                                         and all(type(part) is str for part in reading["failure"])):
            return "a dictionary failure is malformed"
    return None


def read(env, source: str, packs: list[bytes], *, own: list[dict] | None = None,
         overlay: dict | None = None,
         budget: int = WORK_BUDGET, executable: Path = EXECUTABLE) -> dict:
    """Return Lean's senses admission, including open readings, after validating its envelope."""
    deadline = time.monotonic() + configured_timeout(ROUTE_TIMEOUT)
    if type(source) is not str or type(packs) is not list or not packs or \
            type(budget) is not int or budget < 0 or type(own) not in (list, type(None)):
        raise VEError("Invalid senses request")
    own = [] if own is None else own
    texts = [_text(pack) for pack in packs]
    # The expected identity is over canonical decoded content. The producer remains Lean:
    # malformed packs still go to its restricted decoder, which owns their diagnostic.
    try:
        parsed = [loads_json(pack) for pack in packs]
        expected_id = digest("ve-senses-dictionary-v1\n",
                             {"packs": [[p["name"], p] for p in parsed], "own": own})
    except (VEError, KeyError, TypeError, ValueError, RecursionError, OverflowError):
        expected_id = None
    case = {"id": "senses.read", "environment": env.to_dict(),
            "lexicon": export(EnglishVocabulary(env, vocabulary=overlay)), "packs": texts,
            "own": own, "source": source, "budget": budget}
    if overlay is not None:
        case["overlay"] = overlay
    try:
        request_id = digest("ve-senses-request-v1\n", case)
        payload = canonical_json([case])
    except (TypeError, ValueError, RecursionError, OverflowError) as exc:
        raise VEError("Invalid senses request JSON") from exc
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise CheckerUnavailable("CheckerUnavailable: the Lean senses request exceeded its deadline")
    try:
        proc = subprocess.run([str(executable)], input=payload, capture_output=True,
                              timeout=remaining, check=False,
                              env={"LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"})
        [row] = read_rows(proc.returncode, proc.stdout, [case], restricted=True)
    except (OSError, subprocess.TimeoutExpired, NoAnswer) as exc:
        raise CheckerUnavailable("CheckerUnavailable: the Lean senses reader gave no valid answer") from exc
    if row["status"] != "ok" or row.keys() != {"id", "status", "result"}:
        raise VEError(row.get("error", "Invalid senses request"))
    problem = _response_problem(row["result"], expected_id, request_id)
    if problem:
        raise CheckerUnavailable("CheckerUnavailable: malformed senses response: " + problem)
    if time.monotonic() > deadline:
        raise CheckerUnavailable("CheckerUnavailable: the Lean senses request exceeded its deadline")
    return row["result"]
