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
from ..wire import canonical_json, digest, loads_json
from .service_schema import Invalid, check_projected_environment

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
# The codes whose refusal carries Lean's text of spec 3.2 (`VE.Senses.Run.textsJson`).
TEXTED = {"UnknownGloss", "TooManyCandidates", "CandidatesDiverge"}


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
                     reading_set_units: list[str] | None = None, texts: bool = True) -> str | None:
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
        if reading.keys() - {"text"} != {"status", "code", "details"}:
            return "a sense fault has missing or unknown fields"
        if reading["status"] != ("budget" if code == "PreambleBudget" else "rejected"):
            return "a sense fault has the wrong status"
        details, spec = reading["details"], FAULT_DETAILS[code]
        if type(details) is not dict or details.keys() != spec.keys() \
                or not all(check(details[name]) for name, check in spec.items()):
            return "the arguments of a sense fault are malformed"
        # Lean's 3.2 text (`VE.Senses.Run.textsJson`) on these codes, a CandidatesDiverge's for one word only.
        texted = texts and code in TEXTED and (code != "CandidatesDiverge" or len(details["words"]) == 1)
        if ("text" in reading) != texted or texted and not _word(reading["text"]):
            return "a sense fault's text is missing, unasked or not a string"
        return None
    if reading.get("status") in ("one", "open"):
        return "a refused reading has an admitting status"
    # S2's outcomes: the fields, codes, classes, spans and advice of `english.read`'s refusals (one validator
    # of those fields, reading Lean's table of codes and classes).
    if "hint" in reading:
        # NoSenseFits beside S2's `none` (spec 3.2), Lean's text.
        hint = reading["hint"]
        if not texts or reading.get("code") != "NoDerivation" or type(hint) is not dict \
                or hint.keys() != {"code", "text"} or hint["code"] != "NoSenseFits" or not _word(hint["text"]):
            return "a refused reading's hint is malformed"
        reading = {key: value for key, value in reading.items() if key != "hint"}
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
        return "grammar identities do not match the request"
    if "source_sha256" in ids and ids["source_sha256"] != hashlib.sha256(binding["source"].encode()).hexdigest():
        return "source identity does not match the request"
    if projected is not None and ids["environment_id"] != projected.environment_id:
        return "environment identity is not the returned environment's"
    return None


def _preamble_problem(lines: object, count: int, source: str | None) -> str | None:
    """A source answer's preamble lines (`VE.Senses.Run.writtenLines`), bound to the request: as many as the
    sentences before the body, each non-empty, and together the source's leading sentences, in order, with only
    white space before, between and after them."""
    if type(lines) is not list or not all(_word(line) for line in lines) or len(lines) != count:
        return "the preamble lines are malformed or not the sentences before the body"
    at = 0
    for line in lines:
        rest = source[at:] if type(source) is str else ""
        start = at + len(rest) - len(rest.lstrip())
        at = start + len(line)
        if not source.startswith(line, start) or not (source[at:at + 1].isspace() or at == len(source)):
            return "a preamble line is not the next sentence of the request's source"
    return None


# The members of a flip model by its status (`VE.Senses.Run.flipJson`), besides its unit and pair.
FLIP_FIELDS = {"distinguished": {"true", "values", "model"}, "undistinguished": set(), "unknown": set()}


def _model_problem(model: object, projected) -> str | None:
    """A flip model in the model wire form (`VE.Senses.FlipModel.json`), typed and bound to the projected
    environment: its sorts, constants and predicates are the environment's, each domain distinct entities, each
    constant an entity of its sort's domain and each tuple one of its predicate's sorts' entities. Which tuples
    hold, and that the model separates the pair, are Lean's (`VE.Senses.flipValues_sound`)."""
    if type(model) is not dict or model.keys() != {"complete", "domains", "constants", "relations"} \
            or model["complete"] is not True or not all(type(model[key]) is dict
                                                       for key in ("domains", "constants", "relations")):
        return "is not in the model wire form"
    domains, constants, relations = model["domains"], model["constants"], model["relations"]
    if not all(name in projected.sorts and _words(entities) and len(set(entities)) == len(entities)
               for name, entities in domains.items()):
        return "has a domain of no projected sort, or one that is empty or repeats an entity"
    if not all(name in projected.constants and type(entity) is str
               and entity in domains.get(projected.constants[name].sort, ()) for name, entity in constants.items()):
        return "has a constant of no projected constant, or one outside its sort's domain"
    if not all(name in projected.predicates and type(rows) is list and all(
            type(row) is list and len(row) == len(projected.predicates[name].arguments)
            and all(type(entity) is str and entity in domains.get(sort, ())
                    for entity, sort in zip(row, projected.predicates[name].arguments)) for row in rows)
               for name, rows in relations.items()):
        return "has a relation of no projected predicate, or a tuple outside its sorts' domains"
    return None


def _flips_problem(flips: object, units: list, projected) -> str | None:
    """The flip models (`VE.Senses.flipsOf`): one row per pair `first < second` of each open unit's candidates,
    in unit order, then pair order; a distinguishing model names predicates of the projection, gives the two
    candidates' values and writes the model (`_model_problem`)."""
    pairs = [(unit["sentence"], i, j) for unit in units
             for i in range(len(unit["candidates"])) for j in range(i + 1, len(unit["candidates"]))]
    if type(flips) is not list or len(flips) != len(pairs):
        return "the flip models are not one per pair of an open unit's candidates"
    for row, pair in zip(flips, pairs):
        if type(row) is not dict or type(row.get("status")) is not str or row["status"] not in FLIP_FIELDS \
                or row.keys() != {"sentence", "first", "second", "status"} | FLIP_FIELDS[row["status"]]:
            return "a flip model has missing or unknown fields"
        if not all(_nat(row[key]) for key in ("sentence", "first", "second")) \
                or (row["sentence"], row["first"], row["second"]) != pair:
            return "a flip model does not name the next pair of an open unit's candidates"
        if row["status"] == "distinguished" and (
                not _words(row["true"]) or not all(name in projected.predicates for name in row["true"])
                or type(row["values"]) is not list or len(row["values"]) != 2
                or not all(type(value) is bool for value in row["values"])):
            return "a flip model's senses or values are malformed or not the projection's"
        problem = row["status"] == "distinguished" and _model_problem(row["model"], projected)
        if problem:
            return "a flip model " + problem
    return None


def _response_problem(response: object, expected_id: str, request_id: str,
                      fences: int | None = None, *, source: str | None = "", defaults_count: int = 0,
                      fence_ids: list[str] | None = None,
                      reading_set_units: list[str] | None = None, binding: dict | None = None,
                      line: dict | None = None, reread: dict | None = None) -> str | None:
    """`fences`: the number of fences a fence request sent (Lean's `fenceUnits` map is then required on an
    admitted reading), or None for a source. `source`: the text a refusal's span is over (`_refusal_source`).
    `binding`: the request's environment, source and dictionary words, which the identities and used words name.
    `line` and `reread`: the request's members of those names (sn-b6d), whose answers must be there exactly when
    asked."""
    if type(response) is not dict or response.keys() != {"request_id", "dictionary_id", "senses_version", "reading"} | (
            {"line"} if line is not None else set()):
        return "the result does not have request and dictionary identities, the senses version and a reading"
    if line is not None:
        problem = _line_problem(response["line"], line, binding)
        if problem:
            return problem
    if not _word(response["senses_version"]):
        return "the senses version is not a string"
    if type(response["request_id"]) is not str or response["request_id"] != request_id:
        return "the request identity does not match the submitted envelope"
    if type(response["dictionary_id"]) is not str or response["dictionary_id"] != expected_id:
        return "the dictionary identity does not match the request"
    reading = response["reading"]
    if type(reading) is not dict or type(reading.get("status")) is not str \
            or reading["status"] not in STATUSES:
        return "the reading has no known status"
    if reading["status"] in {"one", "open"}:
        admitted = {"status", "units", "sense_map", "mixed", "unused", "environment", "identities", "used",
                    "flips", "warnings"} | ({"preamble"} if fences is None else {"fences"}) | (
                        {"reread"} if reread is not None else set())
        if reading.keys() != admitted | {"code"} and reading.keys() != admitted:
            return "an admitted reading has missing or unknown fields"
        if (reading.get("code") != "Unresolved" if reading["status"] == "open" else "code" in reading):
            return "an admitted reading has the wrong code"
        if (type(reading["units"]) is not list or not reading["units"]
                or type(reading["sense_map"]) is not list or type(reading["mixed"]) is not list
                or type(reading["unused"]) is not list or type(reading["environment"]) is not dict):
            return "an admitted reading has malformed collections"
        if binding is not None:
            try:
                check_projected_environment(reading["environment"], binding["case"])
            except Invalid as exc:
                return f"the projected environment is not the request's with the projection's added: {exc}"
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
            # Every open unit carries Lean's unresolved English (spec 3.2 `Unresolved`), a source's too (sn-b6c).
            if ("text" in unit) != (not resolved) \
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
        if fences is None:
            problem = _preamble_problem(reading["preamble"], sentences[0] - defaults_count,
                                        source if binding is None else binding["source"])
            if problem:
                return problem
        problem = _flips_problem(reading["flips"], reading["units"], projected)
        if problem:
            return problem
        units = dict(zip(sentences, reading["units"]))
        if (reading["status"] == "one") != all(not u["candidates"] for u in reading["units"]):
            return "the status disagrees with the units"
        entry = {"sentence", "token_start", "token_stop", "symbol", "is_default", "gloss"} | (
            {"byte_start", "byte_stop"} if fences is None else set())
        for occurrence in reading["sense_map"]:
            if type(occurrence) is not dict or occurrence.keys() not in (entry, entry | {"candidate"}) \
                    or not _word(occurrence["gloss"]) \
                    or binding is not None and "glosses" in binding \
                    and not any(occurrence["gloss"] == gloss for _, gloss in binding["glosses"]) \
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
        if fences is None:
            problem = _byte_spans_problem(reading["sense_map"], source if binding is None else binding["source"],
                                          reading["preamble"])
            if problem:
                return problem
        problem = _warnings_problem(reading["warnings"], reading["mixed"], binding)
        if problem:
            return problem
        if reread is not None:
            problem = _reread_problem(reading["reread"], reread, units)
            if problem:
                return problem
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


def _boundary(data: bytes, at: int) -> bool:
    """`at` starts a character of the UTF-8 bytes `data` (or is their end)."""
    return at == len(data) or not 0x80 <= data[at] < 0xC0


def _byte_spans_problem(entries: list, source: object, preamble: list) -> str | None:
    """A source answer's sense-map bytes (`VE.Senses.Run.byteSpan`), bound to the request's source: inside its body
    (after the preamble lines, which are bound already), on character boundaries, not empty, with no white space at
    either edge and no word cut at either edge; and in the order of the entries' token spans, equal token spans
    having equal bytes."""
    if type(source) is not str:
        return "a sense-map span has no source"
    data = source.encode()
    at = 0
    for line in preamble:
        at = source.index(line, at) + len(line)
    floor = len(source[:at].encode())
    order = []
    for entry in entries:
        start, stop = entry["byte_start"], entry["byte_stop"]
        if not (_nat(start) and _nat(stop) and floor <= start < stop <= len(data)
                and _boundary(data, start) and _boundary(data, stop)):
            return "a sense-map span is not inside the request's source body"
        text = data[start:stop].decode()
        before = data[:start].decode()[-1:]
        after = data[stop:stop + 4].decode(errors="ignore")[:1]
        if text != text.strip() or before.isalnum() and text[0].isalnum() or after.isalnum() and text[-1].isalnum():
            return "a sense-map span does not start and end at a word of the request's source"
        order.append(((entry["sentence"], entry["token_start"], entry["token_stop"]), (start, stop)))
    order.sort()
    for (tokens, span), (tokens2, span2) in zip(order, order[1:]):
        if (tokens == tokens2) != (span == span2) or span > span2:
            return "sense-map spans are not in the order of their tokens"
    return None


def _warnings_problem(warnings: object, mixed: list, binding: dict | None) -> str | None:
    """An admitted reading's warnings (`VE.Senses.Run.warningsJson`): one `Mixed` per entry of `mixed`, in its order
    and naming its word, then `Unneeded` for distinct words of the request's dictionary; each with Lean's text."""
    if type(warnings) is not list or not all(
            type(w) is dict and w.keys() == {"code", "word", "text"} and w["code"] in ("Mixed", "Unneeded")
            and _word(w["word"]) and _word(w["text"]) for w in warnings):
        return "the warnings are malformed"
    words = [pair[0] for pair in mixed]
    if [w["word"] for w in warnings[:len(words)] if w["code"] == "Mixed"] != words:
        return "the Mixed warnings are not one per mixed word"
    unneeded = warnings[len(words):]
    if any(w["code"] != "Unneeded" for w in unneeded) or len({w["word"] for w in unneeded}) != len(unneeded) \
            or binding is not None and not {w["word"] for w in unneeded} <= binding["words"]:
        return "the Unneeded warnings are not distinct words of the request's dictionary"
    return None



REREAD_OUTCOMES = {"same", "different", "unknown"}


def _reread_problem(reread: object, asked: dict, units: dict) -> str | None:
    """The re-read of one rendering (`VE.Senses.Run.rereadJson`): the unit and candidate the request named, one of
    the answer's units and one of its candidates, and Lean's outcome."""
    if type(reread) is not dict or reread.keys() != {"sentence", "candidate", "outcome"} \
            or type(reread["outcome"]) is not str or reread["outcome"] not in REREAD_OUTCOMES:
        return "the re-read is malformed"
    if not all(_nat(reread[key]) for key in ("sentence", "candidate")) \
            or [reread["sentence"], reread["candidate"]] != [asked["sentence"], asked["candidate"]] \
            or reread["sentence"] not in units \
            or reread["candidate"] >= len(units[reread["sentence"]]["candidates"]):
        return "the re-read does not name the request's unit and candidate"
    return None


def _line_problem(answer: object, asked: dict, binding: dict | None) -> str | None:
    """Lean's line for the requested word and gloss (`VE.Senses.Run.lineJson`): that word and gloss, with Lean's
    line (a sense of the request's dictionary) or with Lean's code (none is)."""
    if type(answer) is not dict or answer.keys() not in ({"word", "gloss", "text"}, {"word", "gloss", "code"}) \
            or not all(type(answer[key]) is str for key in answer) \
            or [answer["word"], answer["gloss"]] != [asked["word"], asked["gloss"]]:
        return "the line does not name the request's word and gloss"
    pair = (asked["word"], asked["gloss"])
    if "text" in answer and (not answer["text"] or binding is not None and pair not in binding["glosses"]) \
            or "code" in answer and (answer["code"] not in ("UnknownWord", "UnknownGloss")
                                     or binding is not None and pair in binding["glosses"]):
        return "the line is not one of a sense of the request's dictionary"
    return None


def request(env, source: str | None, texts: list[str], *, own: list[dict] = (), overlay: dict | None = None,
            budget: int = WORK_BUDGET, fences: list[str] | None = None, defaults=None,
            fence_ids: list[str] | None = None, reading_set_units: list[str] | None = None,
            line: dict | None = None, reread: dict | None = None) -> dict:
    """The `ve_senses_route` case: the environment, the lexicon Python's vocabulary selects, the pack texts
    unchanged, the own senses, the source (or a document's English fences in unit order), the front
    matter's defaults as written, and the budget."""
    case = {"id": OPERATION, "environment": env.to_dict(),
            "lexicon": export(EnglishVocabulary(env, vocabulary=overlay)), "packs": list(texts),
            "own": list(own), "budget": budget}
    if fences is None:
        case["source"] = source
        # sn-b6d: Lean's preamble line for a word and gloss, and the re-read of one candidate's rendering.
        if line is not None:
            case["line"] = line
        if reread is not None:
            case["reread"] = reread
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
         budget: int = WORK_BUDGET, executable: Path = EXECUTABLE,
         line: tuple[str, str] | None = None, reread: tuple[int, int, str] | None = None) -> dict:
    """Return Lean's senses admission, including open readings, after validating its envelope. `line`, a word and
    a gloss, asks for Lean's preamble line (`result["line"]`); `reread`, a unit's sentence, a candidate's index and
    a rendering, asks Lean to re-read the rendering under that candidate's projection (`reading["reread"]`, on an
    admitted reading; Lean refuses a rendering that is not one sentence)."""
    if type(source) is not str \
            or line is not None and not (type(line) is tuple and len(line) == 2 and all(type(x) is str for x in line)) \
            or reread is not None and not (type(reread) is tuple and len(reread) == 3 and _nat(reread[0])
                                           and _nat(reread[1]) and type(reread[2]) is str):
        raise VEError("Invalid senses request")
    return _read(env, source, None, packs, own=own, overlay=overlay, defaults=None, budget=budget,
                 executable=executable,
                 line=None if line is None else {"word": line[0], "gloss": line[1]},
                 reread=None if reread is None else dict(zip(("sentence", "candidate", "rendering"), reread)))


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


def _glosses(packs: list[bytes], own: list) -> set:
    """The (word, gloss) pairs of the request's senses, which a sense-map gloss must name."""
    try:
        return {(sense["word"], sense["gloss"]) for sense in
                [s for pack in packs for s in loads_json(pack)["senses"]] + list(own)}
    except (VEError, KeyError, TypeError, ValueError, RecursionError, OverflowError):
        return set()


def _projection_problem(row: object, case: dict, env, expected_id: str | None) -> str | None:
    """A `senses.project` row bound to its request: the case's id, the packs' dictionary identity, and a
    projection whose identities are those of the environment and lexicon it returns (Python's own over the
    returned JSON), or a sense fault with its arguments. The senses version is typed, not bound; sn-b6bb binds it."""
    if type(row) is not dict or row.keys() != {"id", "status", "result"} or row["id"] != case["id"] \
            or row["status"] != "ok":
        return "the row is not the answer to the request"
    result = row["result"]
    if type(result) is not dict or result.keys() != {"dictionary_id", "senses_version", "projection"}:
        return "the result does not have the dictionary identity, the senses version and a projection"
    if result["dictionary_id"] != expected_id:
        return "the dictionary identity does not match the request"
    if not _word(result["senses_version"]):
        return "the senses version is not a string"
    projection = result["projection"]
    if type(projection) is not dict or projection.get("status") != "ok":
        if type(projection) is not dict or projection.get("code") not in {"InvalidDictionary", *FAULT_DETAILS}:
            return "the projection is neither a projection nor a sense fault"
        return _refusal_problem(projection, None, texts=False)
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
    [row] = lean_backend.run("senses.project", None, [case], runner="ve_service", mode="senses.project")
    problem = _projection_problem(row, case, env, _dictionary(packs, own)[0])
    if problem:
        raise CheckerUnavailable("CheckerUnavailable: malformed senses projection: " + problem)
    return row["result"]


def _read(env, source, fences, packs, *, own, overlay, defaults, budget, executable,
          fence_ids=None, reading_set_units=None, line=None, reread=None) -> dict:
    deadline = time.monotonic() + configured_timeout(ROUTE_TIMEOUT)
    # A dictionary of own senses alone is Lean's to judge: no pack is required here.
    if type(packs) is not list or \
            type(budget) is not int or budget < 0 or type(own) not in (list, type(None)):
        raise VEError("Invalid senses request")
    own = [] if own is None else own
    texts = [_text(pack) for pack in packs]
    expected_id, words = _dictionary(packs, own)
    case = request(env, source, texts, own=own, overlay=overlay, budget=budget, fences=fences, defaults=defaults,
                   fence_ids=fence_ids, reading_set_units=reading_set_units, line=line, reread=reread)
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
                                binding={"env": env, "source": source, "words": words, "case": case,
                                         "glosses": _glosses(packs, own)},
                                line=line, reread=reread)
    if problem:
        raise CheckerUnavailable("CheckerUnavailable: malformed senses response: " + problem)
    if time.monotonic() > deadline:
        raise CheckerUnavailable("CheckerUnavailable: the Lean senses request exceeded its deadline")
    return row["result"]
