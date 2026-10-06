"""E2's Lean-authoritative English reader and its untrusted response boundary.

Requests carry the submitted environment, optional overlay, Python's proposed lexicon,
source, mode and cap. The persistent `ve_service` answers `english.read`; this module
checks the answer's schema, formulas, spans, obligations and request identities before
`ve.english` uses it. `TRANSPORT` is a test override. The optional Python comparator
records a shadow outcome but never decides admission (docs/spec/english-lean-e2.md).
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Callable

from .. import ast
from ..english_grammar import actions_version, export, grammar_id, lexicon_id
from ..errors import (AmbiguousDerivation, CheckerUnavailable, ResourceLimit, SyntaxError, TypeMismatch,
                      UnknownSymbol, UnsupportedProfile, VEError, Span)
from . import dispatch
from . import relay

ROOT = Path(__file__).resolve().parents[2]
MODE = "english.read"
CAP = 2
IDENTITIES = ("source_sha256", "environment_id", "overlay_digest", "lexicon_id", "grammar_id", "actions_version")
STATUSES = ("one", "none", "many", "rejected", "budget", "invalidGrammar")
FAULTS = ("lexicon", "notWellFormed", "notTyped")
ILL_TYPED = ("UnknownSymbol", "TypeMismatch", "UnsupportedProfile")
# The Python classes each Lean rejection code maps onto: base 4.2 with this stage's four codes and its
# amended `IllTyped` row (spec 4.2). `RelativeForm` maps onto two classes by the text (2.8): either agrees.
# `CoefficientNotNumeral` is `order@0`'s (S3 2.8; Python's `SyntaxError`, `english.py:1213–1214`).
CLASSES = {
    "SourceTooLong": ("ResourceLimit",), "TextTooLong": ("ResourceLimit",),
    "BadCharacter": ("SyntaxError",), "OpenQuote": ("SyntaxError",), "BadNumeral": ("SyntaxError",),
    "EmptyDocument": ("SyntaxError",), "EmptySentence": ("SyntaxError",), "Unterminated": ("SyntaxError",),
    "BadSpacing": ("SyntaxError",),
    "UnboundReference": ("SyntaxError",), "ShadowedName": ("SyntaxError",), "SortMismatch": ("SyntaxError",),
    "MarkerDepth": ("SyntaxError",), "NestingLimit": ("ResourceLimit",), "NumeralBound": ("ResourceLimit",),
    "CoefficientNotNumeral": ("SyntaxError",),
    "PronounUnresolved": ("SyntaxError",), "BlockedWording": ("SyntaxError",), "IllTyped": ILL_TYPED,
    "CoordinationRepeated": ("SyntaxError",), "CoordinationForm": ("SyntaxError",),
    "NaturalScoped": ("SyntaxError",), "RelativeForm": ("SyntaxError", *ILL_TYPED),
    "ConclusionWithoutPremise": ("SyntaxError",), "ConclusionNotDerived": ("SyntaxError",),
    "NotOneSentence": ("SyntaxError",), "Internal": ("CheckerUnavailable",),
}
# The Python class of each status other than `rejected` (base 4.1), and the code Lean gives it.
STATUS_CLASSES = {"one": ("accepted",), "none": ("SyntaxError",), "many": ("AmbiguousDerivation",),
                  "budget": ("ResourceLimit",), "invalidGrammar": ("CheckerUnavailable",)}
STATUS_CODES = {"none": "NoDerivation", "many": "Ambiguous", "budget": "Budget", "invalidGrammar": "InvalidGrammar"}
ERRORS = {cls.__name__: cls for cls in (SyntaxError, AmbiguousDerivation, ResourceLimit, UnknownSymbol,
                                        TypeMismatch, UnsupportedProfile)}
# Python's one wall-clock limit on this path (`ve/surface/unambiguity.py`): excluded from G2 and listed.
WALL_CLOCK = "English Earley time budget exhausted"

TRANSPORT: Callable[[dict], dict] | None = None


def request(env, source: str, words, options: dict) -> dict:
    case = {"id": MODE, "environment": env.to_dict(), "lexicon": export(words), "source": source,
            "mode": "authoring", "cap": CAP}
    if options.get("vocabulary") is not None:
        case["overlay"] = options["vocabulary"]
    return case


def identities(env, source: str, words, lexicon: dict) -> dict:
    """The six identities of base 2.12 for this request, as the service must compute them."""
    out = {"source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
           "environment_id": env.environment_id, "lexicon_id": lexicon_id(lexicon),
           "grammar_id": grammar_id(env.profiles), "actions_version": actions_version()}
    if words.overlay_digest is not None:
        out["overlay_digest"] = words.overlay_digest
    return out


def _nat(value) -> bool:
    return type(value) is int and value >= 0


def _tree(value) -> bool:
    """A tree of spec 4.3: `[tag, start, end]` nodes in pre-order, the root first and starting at 0, every
    other node inside the span of an earlier node that is still open (its parent)."""
    if type(value) is not list or not value:
        return False
    open_spans: list[tuple[int, int]] = []
    for k, node in enumerate(value):
        # A rule covers at least one token (W2), so every span is non-empty.
        if not (type(node) is list and len(node) == 3 and type(node[0]) is str and node[0]
                and _nat(node[1]) and _nat(node[2]) and node[1] < node[2]):
            return False
        start, end = node[1], node[2]
        while open_spans and start >= open_spans[-1][1]:
            open_spans.pop()
        if k == 0:
            if start != 0:
                return False
        elif not open_spans or not (open_spans[-1][0] <= start and end <= open_spans[-1][1]):
            return False
        open_spans.append((start, end))
    return True


def _trees(value, count: int | None = None) -> bool:
    return (type(value) is list and (count is None or len(value) == count) and all(_tree(t) for t in value))


def _has_null(value) -> bool:
    if value is None:
        return True
    if type(value) is dict:
        return any(_has_null(item) for item in value.values())
    if type(value) is list:
        return any(_has_null(item) for item in value)
    return False


def response_problem(response, expected: dict, env) -> str | None:
    """Why `response` is not a well-formed `english.read` answer to the request over `env` whose identities
    are `expected`, or None (base 4.1, 4.3; spec 4.5). Every formula must decode under `env`."""
    if type(response) is not dict:
        return "the response is not an object"
    if _has_null(response):
        return "the response has a null"
    status = response.get("status")
    if type(status) is not str or status not in STATUSES:
        return f"unknown status {status!r}"
    fields = {"one": ({"ast", "conclusions", "derivation"}, set()),
              "none": ({"code", "text", "sentence"}, set()),
              "many": ({"code", "text", "sentence", "witnesses"}, set()),
              "budget": ({"code", "text", "sentence"}, set()),
              "rejected": ({"code", "text"}, {"sentence"}),
              "invalidGrammar": ({"code", "text", "fault"}, {"failure"})}
    required, optional = fields[status]
    required = required | {"status", "identities"}
    missing, extra = required - response.keys(), response.keys() - required - optional
    if missing or extra:
        return f"a {status} response with fields missing {sorted(missing)}, unknown {sorted(extra)}"
    found = response["identities"]
    if type(found) is not dict or found.keys() != expected.keys() or \
            not all(type(value) is str for value in found.values()):
        return f"identities {sorted(found) if type(found) is dict else found!r}, expected {sorted(expected)}"
    for name in IDENTITIES:
        if found.get(name) != expected.get(name):
            return f"{name} {found.get(name)!r} is not the request's {expected.get(name)!r}"
    for name in ("code", "text"):
        if name in response and (type(response[name]) is not str or not response[name]):
            return f"{name} is not a non-empty string"
    if status in STATUS_CODES and response["code"] != STATUS_CODES[status]:
        return f"a {status} response with the code {response['code']!r}"
    if "sentence" in response and not _nat(response["sentence"]):
        return "sentence is not a natural number"
    if status == "rejected" and (response["code"] not in CLASSES or response["code"] in STATUS_CODES.values()):
        return f"rejection code {response['code']!r} is not one of base 4.2 or spec 4.2"
    if status == "many" and not _trees(response["witnesses"], 2):
        return "a many response does not carry two witness trees"
    if status == "invalidGrammar":
        if response["fault"] not in FAULTS:
            return f"invalidGrammar fault {response['fault']!r}"
        failure = response.get("failure")
        if failure is not None and not (response["fault"] == "lexicon" and type(failure) is list
                                        and len(failure) == 3 and all(type(x) is str for x in failure)):
            return "invalidGrammar failure is not the first (condition, kind, name) of a lexicon fault"
    if status == "one":
        formulas, conclusions = response["ast"], response["conclusions"]
        if type(formulas) is not list or not formulas:
            return "ast is not a non-empty list of formulas"
        for formula in formulas:
            try:
                ast.formula_from_data(env, formula)
            except VEError as exc:
                return f"a formula does not decode under the environment: {exc}"
        if type(conclusions) is not list or not all(_nat(i) and i < len(formulas) for i in conclusions) \
                or conclusions != sorted(set(conclusions)):
            return "conclusions are not increasing indices of the formulas"
        if not _trees(response["derivation"], len(formulas)):
            return "derivation does not give one tree per sentence"
    return None


def e2_response_problem(response: dict, expected: dict, env, source: str) -> str | None:
    """Validate the full E2 answer before any formula or diagnostic is used."""
    if type(response) is not dict or _has_null(response):
        return "the response is not an object or contains null"
    status = response.get("status")
    if status not in STATUSES:
        return "unknown status"
    additions = {"one": {"obligations", "spans"}, "none": {"class", "span"},
                 "many": {"class", "span"}, "budget": {"class", "span"},
                 "rejected": {"class", "span"}, "invalidGrammar": {"class"}}[status]
    if status == "none" and "advice" in response:
        additions.add("advice")
    base = {k: v for k, v in response.items() if k not in additions}
    if status == "invalidGrammar" and base.get("code") == "InvalidOverlay":
        base = {k: v for k, v in base.items() if k != "failure"}
        base.update(code="InvalidGrammar", fault="lexicon")
    problem = response_problem(base, expected, env)
    if problem:
        return problem
    if not additions <= response.keys():
        return f"missing E2 fields {sorted(additions - response.keys())}"
    def span_ok(value):
        return (type(value) is list and len(value) == 2 and all(_nat(x) for x in value)
                and value[0] <= value[1] <= len(source))
    if "span" in response and not span_ok(response["span"]):
        return "invalid source span"
    if status == "one":
        n = len(response["ast"])
        spans = response["spans"]
        if type(spans) is not list or len(spans) != n or not all(span_ok(s) for s in spans):
            return "spans do not match the sentences"
        if any(spans[i][1] > spans[i + 1][0] for i in range(n - 1)):
            return "sentence spans overlap"
        obligations = response["obligations"]
        if type(obligations) is not list or len(obligations) != len(response["conclusions"]):
            return "obligations do not match conclusions"
        for marked, item in zip(response["conclusions"], obligations):
            if type(item) is not dict or item.keys() != {"conclusion", "premises", "unproved"}:
                return "malformed obligation"
            premises = item["premises"]
            if (type(item["conclusion"]) is not int or item["conclusion"] != marked
                    or type(premises) is not list or not premises
                    or not all(_nat(j) and j < marked for j in premises)
                    or premises != sorted(set(premises))
                    or type(item["unproved"]) is not str or item["unproved"].count("{status}") != 1):
                return "invalid obligation premises or text"
    else:
        if type(response.get("class")) is not str or not response["class"]:
            return "missing diagnostic class"
        if status == "invalidGrammar":
            expected_class = "VEError" if response.get("code") == "InvalidOverlay" else "CheckerUnavailable"
        elif status == "rejected":
            expected_class = ("TypeMismatch" if response.get("code") == "IllTyped" else
                              CLASSES.get(response.get("code"), (None,))[0])
        else:
            expected_class = {"none": "SyntaxError", "many": "AmbiguousDerivation",
                              "budget": "ResourceLimit"}[status]
        if response["class"] != expected_class:
            return "diagnostic class does not match the code"
        if status == "invalidGrammar" and response["code"] == "InvalidOverlay":
            failure = response.get("failure")
            if (type(failure) is not list or len(failure) != 3
                    or not all(type(x) is str and x for x in failure)
                    or failure[0] not in {"O1", "O2", "O3"}
                    or failure[1] not in {"sort", "predicate"} or "fault" in response):
                return "invalid overlay failure"
        if "advice" in response:
            advice = response["advice"]
            if status != "none" or type(advice) is not dict or advice.keys() != {"id", "text"} or not all(
                    type(x) is str and x for x in advice.values()):
                return "malformed advice"
    return None


def _transport(case: dict) -> dict:
    if TRANSPORT is not None:
        return TRANSPORT(case)
    row = relay.decide_once(MODE, case)
    if row.get("status") != "ok" or row.keys() != {"id", "status", "result"}:
        raise CheckerUnavailable(f"CheckerUnavailable: the Lean English reader did not read the case: "
                                 f"{row.get('error', row)!r}")
    return row["result"]


class LeanReading:
    """A checked `english.read` answer."""

    def __init__(self, response: dict, env, source: str = ""):
        self.response, self.env, self.source = response, env, source
        self.status = response["status"]

    def classes(self) -> tuple[str, ...]:
        """The Python classes this outcome maps onto (base 4.1, spec 4.2)."""
        if "class" in self.response:
            code = self.response.get("code")
            if code in ("RelativeForm", "IllTyped"):
                return CLASSES[code]
            return (self.response["class"],)
        if self.status == "rejected":
            return CLASSES[self.response["code"]]
        return STATUS_CLASSES[self.status]

    def document(self) -> ast.Document:
        """The formulas, which `response_problem` decoded once already."""
        return ast.Document(tuple(ast.formula_from_data(self.env, f) for f in self.response["ast"]))

    def canonical(self) -> str:
        """The canonical strict text of the formulas, by Python's printer (the owner of the printer)."""
        from ..printer import print_document
        return print_document(self.env, self.document())

    def rejection(self) -> Exception:
        """Lean's outcome other than `one` as the exception of its (first) Python class, with Lean's text;
        the answer rides along as `lean_reading` for the shadow record."""
        if self.status == "invalidGrammar" and self.response["code"] == "InvalidGrammar":
            failure = self.response.get("failure")
            error = CheckerUnavailable(f"CheckerUnavailable: invalidGrammar {self.response['fault']}"
                                       + (f": {' '.join(failure)}" if failure else ""))
        else:
            cls = self.response.get("class", self.classes()[0])
            span = self.response.get("span")
            where = None if span is None else Span(span[0], span[1],
                                                   self.source.count("\n", 0, span[0]) + 1,
                                                   span[0] - self.source.rfind("\n", 0, span[0]))
            error = ERRORS.get(cls, VEError)(self.response["text"], span=where)
        error.lean_reading = self
        return error

    def comparison(self, python_class: str) -> dict:
        """The comparison form of 2.11, with Lean's class read as Python's when the map allows it."""
        allowed = self.classes()
        out = {"code": python_class if python_class in allowed else allowed[0]}
        out["verdict"] = _verdict(out["code"])
        if self.status == "one":
            out.update(formulas=self.response["ast"], canonical=self.canonical(),
                       conclusions=self.response["conclusions"], witnesses=1)
        elif self.status == "many":
            out["witnesses"] = len(self.response["witnesses"])
        return out

    def record(self) -> dict:
        out = {key: self.response[key] for key in ("status", "code", "conclusions", "sentence")
               if key in self.response}
        if "ast" in self.response:
            out["formulas"] = self.response["ast"]
            out["canonical"] = self.canonical()
        if self.status in ("one", "many"):
            out["witnesses"] = 1 if self.status == "one" else len(self.response["witnesses"])
        return out


def read(env, source: str, words, options: dict) -> LeanReading:
    """Lean's checked answer for `source`; `CheckerUnavailable` when there is none."""
    case = request(env, source, words, options)
    expected = identities(env, source, words, case["lexicon"])
    response = _transport(case)
    try:
        problem = (response_problem(response, expected, env) if TRANSPORT is not None else
                   e2_response_problem(response, expected, env, source))
    except RecursionError:
        problem = "the response is nested too deeply"
    if problem:
        raise CheckerUnavailable(f"CheckerUnavailable: the Lean English reader's answer is malformed: {problem}")
    return LeanReading(response, env, source)


def check(env, words, options: dict, formulas: list, marks: list[bool], candidates: list[str]) -> int | None:
    """Ask Lean which candidate has the submitted formulas and marks."""
    case = {"id": "english.check", "environment": env.to_dict(), "lexicon": export(words),
            "formulas": formulas, "marks": marks, "candidates": candidates}
    if options.get("vocabulary") is not None:
        case["overlay"] = options["vocabulary"]
    row = relay.decide_once("english.check", case)
    if type(row) is not dict or row.get("id") != case["id"] or row.get("status") != "ok" or row.keys() != {
            "id", "status", "result"} or type(row["result"]) is not dict:
        raise CheckerUnavailable("CheckerUnavailable: malformed English check row")
    result = row["result"]
    expected = identities(env, "", words, case["lexicon"])
    del expected["source_sha256"]
    if result.get("identities") != expected:
        raise CheckerUnavailable("CheckerUnavailable: English check identities differ from the request")
    if "status" in result:
        if result.get("status") != "invalidGrammar" or result.get("class") not in ("CheckerUnavailable", "VEError"):
            raise CheckerUnavailable("CheckerUnavailable: malformed English check refusal")
        if type(result.get("text")) is not str or not result["text"]:
            raise CheckerUnavailable("CheckerUnavailable: English check refusal has no text")
        if result["class"] == "CheckerUnavailable":
            raise CheckerUnavailable(result["text"])
        raise VEError(result["text"])
    if result.keys() == {"identities"}:
        return None
    index = result.get("index")
    if result.keys() != {"identities", "index"} or not _nat(index) or index >= len(candidates):
        raise CheckerUnavailable("CheckerUnavailable: malformed English check index")
    return index


def _verdict(python_class: str) -> str:
    return {"accepted": "accepted", "ResourceLimit": "budget", "CheckerUnavailable": "unavailable"}.get(
        python_class, "rejected")


def python_class(exc: BaseException) -> str:
    return type(exc).__name__ if isinstance(exc, (VEError, CheckerUnavailable)) else f"internal:{type(exc).__name__}"


def shadow_record(env, source: str, words, python, lean) -> dict:
    """The shadow record of one call (spec 4.5): `python` is Python's grammatical reading (`ve.english`'s
    `_Reading`) or the exception it raised, `lean` the Lean side's reading or exception."""
    record: dict = {"identities": identities(env, source, words, export(words))}
    if isinstance(python, BaseException):
        cls = python_class(python)
        left = {"verdict": _verdict(cls), "code": cls}
        record["python"] = {"class": cls, "message": str(python)}
        if isinstance(python, AmbiguousDerivation):
            left["witnesses"] = record["python"]["witnesses"] = 2
        if isinstance(python, ResourceLimit) and str(python) == WALL_CLOCK:
            record["excluded"] = "wall-clock ResourceLimit"
    else:
        left = {"verdict": "accepted", "code": "accepted", **python.comparison()}
        record["python"] = {"class": "accepted", **python.comparison()}
        refused = python.conclusion_error()
        if refused is not None:
            record["conclusion_rejected"] = True
    reading = getattr(lean, "lean_reading", None) if isinstance(lean, BaseException) else lean.lean
    if reading is None:
        right = {"verdict": "unavailable", "code": python_class(lean)}
        record["lean"] = {"status": "unavailable", "code": right["code"], "message": str(lean)}
    else:
        right = reading.comparison(left["code"])
        record["lean"] = reading.record()
        record["identities"] = reading.response["identities"]
    record["classes"] = [] if "excluded" in record else dispatch._classes(left, right)
    return record
