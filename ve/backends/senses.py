"""Admission through the Lean senses reader.

Python transports pack bytes and checks the shape and identity of the answer.
It does not select a sense or turn an unavailable checker into a verdict.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import re
import time

from .. import ast
from ..backends import lean as lean_backend
from ..backends.english_lean import refusal_problem
from ..backends.lean import ROUTE_TIMEOUT, configured_timeout
from ..environment import Environment
from ..errors import CheckerUnavailable, VEError
from ..english import EnglishVocabulary
from ..english_grammar import actions_version, export, grammar_id, lexicon_id
from ..senses import senses_version
from ..wire import canonical_json, digest, loads_json

ROOT = Path(__file__).resolve().parents[2]
EXECUTABLE = ROOT / "lean/.lake/build/bin/ve_senses_route"
OPERATION = "senses.read"
PROJECT = "senses.project"
WORK_BUDGET = 2_100_000  # VE.EnglishGrammar.workBudget; checked against compiled Lean in tests.
CANDIDATE_CAP = 8  # VE.Senses.candidateCap; checked against compiled Lean in tests.
STATUSES = {"one", "open", "none", "many", "rejected", "budget", "invalidGrammar"}
HEX64 = re.compile("[0-9a-f]{64}")
# The identities of a projection (`VE.Senses.Run.projectionIds`); an answer adds S2's actions version.
PROJECTION_IDS = ("environment_id", "lexicon_id", "grammar_id")


def _nat(value) -> bool:
    return type(value) is int and value >= 0


def _word(value) -> bool:
    return type(value) is str and bool(value)


def _string(value) -> bool:
    return type(value) is str


def _words(value) -> bool:
    return type(value) is list and bool(value) and all(_word(word) for word in value) \
        and len(set(value)) == len(value)


def _why(value) -> bool:
    return value == "binder" or (type(value) is dict and value.keys() == {"referent"} and _word(value["referent"]))


# The arguments of each sense fault, by code: lean/VE/Senses/Run.lean `faultFields`, named as the fields of
# `SenseFault` (spec 5.2). InvalidDictionary carries `failure` instead.
FAULT_DETAILS = {
    "UnknownWord": {"line": _nat, "word": _word},
    "UnknownGloss": {"line": _nat, "word": _word, "gloss": _word},
    "MalformedPreamble": {"line": _nat},
    "PreambleBudget": {"line": _nat},
    "RepeatedDefault": {"line": _nat, "word": _word},
    "PreambleLate": {"sentence": _nat},
    # Project.pairFault and preCheck may leave a collision component empty; Run.faultFields
    # serializes each component as a string without a nonempty invariant.
    "Collision": {"kind": _string, "name": _string, "sense": _string},
    "VocabularyLimit": {"what": lambda value: value in ("sorts", "predicates")},
    "TooManyCandidates": {"sentence": _nat, "words": _words},
    "CandidatesDiverge": {"sentence": _nat, "words": _words, "why": _why},
    "QuotedSense": {"sentence": _nat, "word": _word},
}


def _text(raw: bytes) -> str:
    """A pack's text, sent unchanged: its bytes as UTF-8."""
    if type(raw) is not bytes:
        raise VEError("A sense pack must be bytes")
    try:
        return raw.decode("utf-8")
    except UnicodeError as exc:
        raise VEError("A sense pack is not UTF-8") from exc


# The same reading for the `document` mode's request (`ve.senses_document.pack_texts`).
pack_text = _text


def _refusal_problem(reading: dict, source: str | None, fence_ids: list[str] | None = None,
                     reading_set_units: list[str] | None = None) -> str | None:
    """A refused reading: a sense fault with its arguments, an uncovered fence, or one of S2's outcomes as
    `english.read` writes it (`english_lean.refusal_problem`, the one validator of those fields), over `source`
    (`_refusal_source`), or with no span when there is none."""
    code = reading.get("code")
    if type(code) is not str:
        return "a refused reading has no code"
    if code == "Unresolved":
        if (fence_ids is None or reading.keys() != {"status", "code", "unit", "text"}
                or reading["status"] != "rejected" or not _word(reading["text"])
                or reading["unit"] not in fence_ids
                or reading["unit"] in (reading_set_units or [])):
            return "an unresolved fence refusal is malformed or does not name an uncovered fence"
        return None
    if code == "InvalidDictionary":
        if reading.keys() != {"status", "code", "failure"} or reading["status"] != "rejected":
            return "a dictionary refusal has missing or unknown fields"
        if not (type(reading["failure"]) is list and len(reading["failure"]) == 3
                and all(type(part) is str for part in reading["failure"])):
            return "a dictionary failure is malformed"
        return None
    if code in FAULT_DETAILS:
        if reading.keys() != {"status", "code", "details"}:
            return "a sense fault has missing or unknown fields"
        if reading["status"] != ("budget" if code == "PreambleBudget" else "rejected"):
            return "a sense fault has the wrong status"
        details, spec = reading["details"], FAULT_DETAILS[code]
        if type(details) is not dict or details.keys() != spec.keys() \
                or not all(check(details[name]) for name, check in spec.items()):
            return "the arguments of a sense fault are malformed"
        return None
    if reading.get("status") in ("one", "open"):
        return "a refused reading has an admitting status"
    # S2's outcomes: the fields, codes, classes, spans and advice of `english.read`'s refusals (one validator
    # of those fields, reading Lean's table of codes and classes).
    problem = refusal_problem(reading, source, unlocated=frozenset({"IllTyped"}))
    if problem:
        return "a refused reading is not S2's: " + problem
    return None


def _refusal_source(source: str | None, fences: list[str] | None, defaults) -> str | None:
    """The text Lean's refusal spans are over (`refusalSource`), or one that contains it: the source, or the
    fences joined by line breaks (Lean drops each fence's closing line break first); none under front-matter
    defaults, whose lines the author did not write."""
    if defaults:
        return None
    return source if fences is None else "\n".join(fences)


def _identities_problem(ids: object, keys: tuple, binding: dict | None, projected=None) -> str | None:
    """Identities with exactly `keys`, each a digest but the actions version; bound, when the request is known
    (`binding`), to its environment's grammar, S2's actions version, its source and the returned environment."""
    if type(ids) is not dict or set(ids) != set(keys) or not all(type(ids[key]) is str for key in keys) \
            or not all(HEX64.fullmatch(ids[key]) for key in keys if key != "actions_version"):
        return "identities are missing, unknown or not digests"
    if binding is None:
        return None
    if ids["grammar_id"] != grammar_id(binding["env"].profiles) \
            or ids.get("actions_version", actions_version()) != actions_version():
        return "the grammar identities do not match the request"
    if "source_sha256" in ids and ids["source_sha256"] != hashlib.sha256(binding["source"].encode()).hexdigest():
        return "the source identity does not match the request"
    if projected is not None and ids["environment_id"] != projected.environment_id:
        return "the environment identity is not the returned environment's"
    return None


def _response_problem(response: object, expected_id: str, request_id: str,
                      fences: int | None = None, *, source: str | None = "", defaults_count: int = 0,
                      fence_ids: list[str] | None = None,
                      reading_set_units: list[str] | None = None, binding: dict | None = None) -> str | None:
    """`fences`: the number of fences a fence request sent (Lean's `fenceUnits` map is then required on an
    admitted reading), or None for a source. `source`: the text a refusal's span is over (`_refusal_source`).
    `binding`: the request's environment, source and dictionary words, which the identities and used words name."""
    if type(response) is not dict or response.keys() != {"request_id", "dictionary_id", "senses_version", "reading"}:
        return "the result does not have request and dictionary identities, the senses version and a reading"
    if response["senses_version"] != senses_version():
        return "the senses version is not the one this relay is built for"
    if type(response["request_id"]) is not str or response["request_id"] != request_id:
        return "the request identity does not match the submitted envelope"
    if type(response["dictionary_id"]) is not str or response["dictionary_id"] != expected_id:
        return "the dictionary identity does not match the request"
    reading = response["reading"]
    if type(reading) is not dict or type(reading.get("status")) is not str \
            or reading["status"] not in STATUSES:
        return "the reading has no known status"
    if reading["status"] in {"one", "open"}:
        admitted = {"status", "units", "sense_map", "mixed", "unused", "environment", "identities", "used"} | (
            set() if fences is None else {"fences"})
        if reading.keys() != admitted | {"code"} and reading.keys() != admitted:
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
        problem = _identities_problem(reading["identities"], (*PROJECTION_IDS, "actions_version") + (
            ("source_sha256",) if fences is None else ()), binding, projected)
        if problem:
            return "the reading's " + problem
        if not _words(reading["used"]) and reading["used"] != [] \
                or binding is not None and not set(reading["used"]) <= binding["words"]:
            return "the used words are malformed or not words of the request's dictionary"
        for unit in reading["units"]:
            state = {"sentence", "candidates", "unresolved", "referents", "binder_seen"}
            if type(unit) is not dict or unit.keys() not in (state, state | {"text"},
                                                               state | {"formula", "mark"}) \
                    or type(unit["candidates"]) is not list or type(unit["unresolved"]) is not list \
                    or len(unit["candidates"]) > CANDIDATE_CAP \
                    or not all(type(word) is str for word in unit["unresolved"]) \
                    or len(set(unit["unresolved"])) != len(unit["unresolved"]):
                return "a unit is malformed"
            if type(unit["referents"]) is not list \
                    or not all(type(name) is str and name in projected.constants for name in unit["referents"]) \
                    or len(set(unit["referents"])) != len(unit["referents"]) \
                    or type(unit["binder_seen"]) is not bool:
                return "the state after a unit is malformed"
            resolved = {"formula", "mark"} <= unit.keys()
            if resolved == bool(unit["candidates"]):
                return "a unit is neither resolved nor open, or both"
            # Only the document fence route carries Lean's unresolved English. Source-mode JSON is frozen.
            if ("text" in unit) != (fences is not None and not resolved) \
                    or ("text" in unit and not _word(unit["text"])):
                return "a unit has the wrong English fields"
            if resolved and type(unit["mark"]) is not bool:
                return "a unit mark is not Boolean"
            if resolved:
                try:
                    ast.formula_from_data(projected, unit["formula"])
                except VEError:
                    return "a resolved formula is invalid under the projected environment"
            choices = []
            for candidate in unit["candidates"]:
                if type(candidate) is not dict or candidate.keys() != {"choice", "lines", "formula", "mark", "identities"} \
                        or type(candidate["choice"]) is not list or not candidate["choice"] \
                        or type(candidate["lines"]) is not str or type(candidate["mark"]) is not bool:
                    return "a candidate is malformed"
                if not all(type(pair) is list and len(pair) == 2 and type(pair[0]) is str
                           and _nat(pair[1]) and pair[1] > 0 for pair in candidate["choice"]):
                    return "a candidate choice is malformed"
                if [pair[0] for pair in candidate["choice"]] != unit["unresolved"] \
                        or not set(unit["unresolved"]) <= set(reading["used"]):
                    return "a candidate choice does not name the unresolved words"
                problem = _identities_problem(candidate["identities"], PROJECTION_IDS, binding)
                if problem:
                    return "a candidate's " + problem
                choices.append(tuple(map(tuple, candidate["choice"])))
                try:
                    ast.formula_from_data(projected, candidate["formula"])
                except VEError:
                    return "a candidate formula is invalid under the projected environment"
            if len(choices) != len(set(choices)):
                return "candidate choices are duplicated"
        sentences = [unit["sentence"] for unit in reading["units"]]
        if not all(_nat(s) for s in sentences) \
                or sentences != list(range(sentences[0], sentences[0] + len(sentences))):
            return "the units are not the consecutive body sentences"
        units = dict(zip(sentences, reading["units"]))
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
            unit = units.get(occurrence["sentence"])
            if unit is None or ("candidate" in occurrence) != bool(unit["candidates"]) \
                    or occurrence.get("candidate", 0) >= max(1, len(unit["candidates"])):
                return "a sense-map occurrence names no unit or candidate of its sentence"
        if not all(type(pair) is list and len(pair) == 2 and type(pair[0]) is str
                   and type(pair[1]) is list and len(pair[1]) >= 2
                   and all(type(symbol) is str and symbol in projected.predicates for symbol in pair[1])
                   for pair in reading["mixed"]):
            return "mixed senses are malformed"
        if not all(type(word) is str for word in reading["unused"]):
            return "unused words are malformed"
        if fences is not None:
            # One entry per fence sent: "line" for a preamble line (they lead), else the next unit in order.
            mapped = reading["fences"]
            if type(mapped) is not list or len(mapped) != fences:
                return "the fence map does not have one entry per fence"
            lines = next((i for i, entry in enumerate(mapped) if entry != "line"), len(mapped))
            if mapped[lines:] != list(range(len(reading["units"]))) \
                    or not all(_nat(entry) for entry in mapped[lines:]):
                return "the fence map is not the preamble lines followed by the units in order"
            if sentences != list(range(defaults_count + lines, defaults_count + lines + len(sentences))):
                return "the unit sentences do not match the request's preamble and fence map"
            if fence_ids is not None and any(
                    reading["units"][entry]["candidates"] and fence_ids[index] not in (reading_set_units or [])
                    for index, entry in enumerate(mapped) if entry != "line"):
                return "an open fence has no reading set in the request"
    else:
        return _refusal_problem(reading, source, fence_ids, reading_set_units)
    return None


def request(env, source: str | None, texts: list[str], *, own: list[dict] = (), overlay: dict | None = None,
            budget: int = WORK_BUDGET, fences: list[str] | None = None, defaults=None,
            fence_ids: list[str] | None = None, reading_set_units: list[str] | None = None) -> dict:
    """The `ve_senses_route` case: the environment, the lexicon Python's vocabulary selects, the pack texts
    unchanged, the own senses, the source (or a document's English fences in unit order), the front
    matter's defaults as written, and the budget."""
    case = {"id": OPERATION, "environment": env.to_dict(),
            "lexicon": export(EnglishVocabulary(env, vocabulary=overlay)), "packs": list(texts),
            "own": list(own), "budget": budget}
    if fences is None:
        case["source"] = source
    else:
        case["fences"] = list(fences)
        case["fence_ids"] = list(fence_ids if fence_ids is not None else map(str, range(len(fences))))
        case["reading_set_units"] = list(reading_set_units if reading_set_units is not None else [])
    if overlay is not None:
        case["overlay"] = overlay
    if defaults is not None:
        case["defaults"] = defaults
    return case


def read(env, source: str, packs: list[bytes], *, own: list[dict] | None = None,
         overlay: dict | None = None,
         budget: int = WORK_BUDGET, executable: Path = EXECUTABLE) -> dict:
    """Return Lean's senses admission, including open readings, after validating its envelope."""
    if type(source) is not str:
        raise VEError("Invalid senses request")
    return _read(env, source, None, packs, own=own, overlay=overlay, defaults=None, budget=budget,
                 executable=executable)


def read_fences(env, fences: list[str], packs: list[bytes], *, own: list[dict] | None = None, defaults=None,
                budget: int = WORK_BUDGET, executable: Path = EXECUTABLE,
                fence_ids: list[str] | None = None,
                reading_set_units: list[str] | None = None) -> dict:
    """Lean's reading of a document's English fences in unit order, one sentence each, with the front
    matter's defaults (RD-8). The answer maps each fence to its unit or to a preamble line (`fences`)."""
    if type(fences) is not list or not all(type(text) is str for text in fences):
        raise VEError("Invalid senses request")
    return _read(env, None, fences, packs, own=own, overlay=None, defaults=defaults, budget=budget,
                 executable=executable, fence_ids=fence_ids, reading_set_units=reading_set_units)


def _dictionary(packs: list[bytes], own: list) -> tuple[str | None, set]:
    """The dictionary identity Lean must answer with, over the packs' canonical decoded content, and the words the
    packs and own senses name. The producer remains Lean: a malformed pack still goes to its restricted decoder,
    which owns the diagnostic, and has no expected identity here."""
    try:
        parsed = [loads_json(pack) for pack in packs]
        return (digest("ve-senses-dictionary-v1\n", {"packs": [[p["name"], p] for p in parsed], "own": own}),
                {sense["word"] for p in parsed for sense in p["senses"]} | {sense["word"] for sense in own})
    except (VEError, KeyError, TypeError, ValueError, RecursionError, OverflowError):
        return None, set()


def _projection_problem(row: object, case: dict, env, expected_id: str | None) -> str | None:
    """A `senses.project` row bound to its request: the case's id, the packs' dictionary identity, this relay's
    senses version, and a projection whose identities are those of the environment and lexicon it returns
    (Python's own over the returned JSON), or a sense fault with its arguments."""
    if type(row) is not dict or row.keys() != {"id", "status", "result"} or row["id"] != case["id"] \
            or row["status"] != "ok":
        return "the row is not the answer to the request"
    result = row["result"]
    if type(result) is not dict or result.keys() != {"dictionary_id", "senses_version", "projection"}:
        return "the result does not have the dictionary identity, the senses version and a projection"
    if result["dictionary_id"] != expected_id:
        return "the dictionary identity does not match the request"
    if result["senses_version"] != senses_version():
        return "the senses version is not the one this relay is built for"
    projection = result["projection"]
    if type(projection) is not dict or projection.get("status") != "ok":
        if type(projection) is not dict or projection.get("code") not in {"InvalidDictionary", *FAULT_DETAILS}:
            return "the projection is neither a projection nor a sense fault"
        return _refusal_problem(projection, None)
    if projection.keys() != {"status", "environment", "lexicon", "identities"}:
        return "the projection has missing or unknown fields"
    try:
        projected = Environment(projection["environment"])
    except VEError:
        return "the projected environment is invalid"
    lexicon = projection["lexicon"]
    if type(lexicon) is not dict or lexicon.get("environment_id") != projected.environment_id:
        return "the projected lexicon does not name the projected environment"
    problem = _identities_problem(projection["identities"], (*PROJECTION_IDS, "actions_version"),
                                  {"env": env, "source": None, "words": set()}, projected)
    if problem:
        return "the projection's " + problem
    if projection["identities"]["lexicon_id"] != lexicon_id(lexicon):
        return "the lexicon identity is not the returned lexicon's"
    return None


def project(env, packs: list[bytes], lines: str, used: list[str], *, own: list[dict] | None = None,
            overlay: dict | None = None, budget: int = WORK_BUDGET) -> dict:
    """Lean's projection (`senses.project`, plan 2.6): the packs and own senses under the preamble `lines` over the
    `used` words, as the environment and lexicon a candidate is rendered and re-read under, with their
    identities; or Lean's fault. A request Lean refuses raises Lean's text."""
    if type(lines) is not str or type(used) is not list or not all(type(word) is str for word in used) \
            or type(packs) is not list or type(budget) is not int or budget < 0 \
            or type(own) not in (list, type(None)):
        raise VEError("Invalid senses request")
    own = [] if own is None else own
    case = request(env, None, [_text(pack) for pack in packs], own=own, overlay=overlay, budget=budget)
    del case["source"]
    case.update(id=PROJECT, lines=lines, used=list(used))
    try:
        canonical_json([case])
    except (TypeError, ValueError, RecursionError, OverflowError) as exc:
        raise VEError("Invalid senses request JSON") from exc
    # The manifest's binding of `senses.project` fixes the service mode; an answer out of its schema is
    # CheckerUnavailable there, and Lean's refusal raises its own diagnostic.
    [row] = lean_backend.run(PROJECT, None, [case], runner="ve_service", mode=PROJECT)
    problem = _projection_problem(row, case, env, _dictionary(packs, own)[0])
    if problem:
        raise CheckerUnavailable("CheckerUnavailable: malformed senses projection: " + problem)
    return row["result"]


def _read(env, source, fences, packs, *, own, overlay, defaults, budget, executable,
          fence_ids=None, reading_set_units=None) -> dict:
    deadline = time.monotonic() + configured_timeout(ROUTE_TIMEOUT)
    # A dictionary of own senses alone is Lean's to judge: no pack is required here.
    if type(packs) is not list or \
            type(budget) is not int or budget < 0 or type(own) not in (list, type(None)):
        raise VEError("Invalid senses request")
    own = [] if own is None else own
    texts = [_text(pack) for pack in packs]
    expected_id, words = _dictionary(packs, own)
    case = request(env, source, texts, own=own, overlay=overlay, budget=budget, fences=fences, defaults=defaults,
                   fence_ids=fence_ids, reading_set_units=reading_set_units)
    try:
        request_id = digest("ve-senses-request-v1\n", case)
        canonical_json([case])
    except (TypeError, ValueError, RecursionError, OverflowError) as exc:
        raise VEError("Invalid senses request JSON") from exc
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise CheckerUnavailable("CheckerUnavailable: the Lean senses request exceeded its deadline")
    # The manifest's binding of `senses.read` (ve/assurance-manifest.json) fixes the runner, its mode and
    # the row's fields; a runner that cannot start, times out or answers out of shape is CheckerUnavailable.
    [row] = lean_backend.run("senses.read", executable, [case], runner="ve_senses_route", timeout=remaining)
    if row["status"] != "ok" or row.keys() != {"id", "status", "result"}:
        raise VEError(row.get("error", "Invalid senses request"))
    problem = _response_problem(row["result"], expected_id, request_id, None if fences is None else len(fences),
                                source=_refusal_source(source, fences, defaults),
                                defaults_count=len(defaults) if type(defaults) is dict else 0,
                                fence_ids=case.get("fence_ids"), reading_set_units=case.get("reading_set_units"),
                                binding={"env": env, "source": source, "words": words})
    if problem:
        raise CheckerUnavailable("CheckerUnavailable: malformed senses response: " + problem)
    if time.monotonic() > deadline:
        raise CheckerUnavailable("CheckerUnavailable: the Lean senses request exceeded its deadline")
    return row["result"]
