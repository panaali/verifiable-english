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
from .. import errors
from ..english_grammar import actions_version, codes, export, grammar_id, lexicon_id
from ..errors import AmbiguousDerivation, CheckerUnavailable, ResourceLimit, VEError, Span
from . import dispatch
from . import relay

ROOT = Path(__file__).resolve().parents[2]
EXECUTABLE = ROOT / "lean/.lake/build/bin/ve_english_route"  # S2/S3 conformance oracle
MODE = "english.read"
CAP = 2
IDENTITIES = ("source_sha256", "environment_id", "overlay_digest", "lexicon_id", "grammar_id", "actions_version")
# Lean's class of every code and the codes of every status (`Run.codeClasses`, `Run.statusCodes`): the
# `english.grammar` export, written to `ve/english_grammar/codes.json` by `tools/english_codes.py`. The relay
# holds no class or code table of its own (spec 2.6, D9).
CODE_CLASSES, STATUS_CODES, UNSENTENCED = codes()
STATUSES = ("one", *STATUS_CODES)
FAULTS = ("lexicon", "notWellFormed", "notTyped")
OVERLAY_SITES = {"O1": ("predicate",), "O2": ("predicate",), "O3": ("sort", "predicate")}
# Every class a response may name, by its Python name: the classes of `ve.errors`, never a list kept here.
ERROR_CLASSES = {name: cls for name, cls in vars(errors).items()
                 if isinstance(cls, type) and issubclass(cls, (VEError, CheckerUnavailable))}
# The comparator's tolerance (spec 2.9: kept by the comparator only): Python raised a typing class where Lean
# writes `IllTyped`, and for `RelativeForm` either Python's `SyntaxError` or a typing class.
TYPING = ("UnknownSymbol", "TypeMismatch", "UnsupportedProfile")
COMPARATOR_CLASSES = {"IllTyped": TYPING, "RelativeForm": ("SyntaxError", *TYPING)}
# Python's one wall-clock limit on this path (`ve/surface/unambiguity.py`): excluded from G2 and listed.
WALL_CLOCK = "English Earley time budget exhausted"
# Python's premise check (`english._check_conclusions`), owned by Lean as `ConclusionWithoutPremise`.
NO_PREMISE = "A conclusion needs an earlier premise."

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


def _text(value) -> bool:
    return type(value) is str and bool(value)


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


def _span(value, source: str) -> bool:
    return (type(value) is list and len(value) == 2 and all(_nat(x) for x in value)
            and value[0] <= value[1] <= len(source))


# The fields of each status of an `english.read` answer (spec 4.4), besides `status` and `identities`:
# required, then optional. `advice` is Lean's for a sentence without a reading or that it refused.
FIELDS = {"one": ({"ast", "conclusions", "derivation", "obligations", "spans"}, set()),
          "none": ({"code", "text", "class", "sentence", "span"}, {"advice"}),
          "many": ({"code", "text", "class", "sentence", "span", "witnesses"}, set()),
          "budget": ({"code", "text", "class", "sentence", "span"}, set()),
          "rejected": ({"code", "text", "class", "span"}, {"sentence", "advice"}),
          "invalidGrammar": ({"code", "text", "class"}, {"fault", "failure"})}


def refusal_problem(response: dict, source: str, *, unlocated: frozenset[str] = frozenset()) -> str | None:
    """Why a refusal (any status but `one`) is not Lean's, or None: its exact fields (spec 4.4), a code of its
    status, the class Lean gives the code, whether it names a sentence (Lean's `unsentenced` codes never do,
    and the codes of `unlocated` may not), a span inside the source, the advice, the witnesses and the
    invalid-grammar fields. The senses relay checks the outcomes it shares with this; its reader names no
    sentence for `IllTyped`."""
    status = response.get("status")
    if type(status) is not str or status not in FIELDS or status == "one":
        return f"unknown refusal status {status!r}"
    required, optional = FIELDS[status]
    required = required | {"status"}
    missing, extra = required - response.keys(), response.keys() - required - optional
    if missing or extra:
        return f"a {status} response with fields missing {sorted(missing)}, unknown {sorted(extra)}"
    if not _text(response["code"]) or not _text(response["text"]) or not _text(response["class"]):
        return "code, text and class are not non-empty strings"
    code = response["code"]
    if code not in STATUS_CODES[status]:
        return f"a {status} response with the code {code!r}"
    if response["class"] != CODE_CLASSES.get(code):
        return f"the class {response['class']!r} is not Lean's class of {code}"
    if response["class"] not in ERROR_CLASSES:
        return f"the class {response['class']!r} is not a class of ve.errors"
    if "sentence" in response and not _nat(response["sentence"]):
        return "sentence is not a natural number"
    if status == "rejected" and code not in unlocated and ("sentence" in response) == (code in UNSENTENCED):
        return f"a {code} rejection {'names' if code in UNSENTENCED else 'does not name'} a sentence"
    if "span" in response and not _span(response["span"], source):
        return "invalid source span"
    if "advice" in response:
        advice = response["advice"]
        if type(advice) is not dict or advice.keys() != {"id", "text"} or not all(_text(x) for x in advice.values()):
            return "malformed advice"
        if status == "rejected" and "sentence" not in response:
            return "advice for a rejection that names no sentence"
    if status == "many" and not _trees(response["witnesses"], 2):
        return "a many response does not carry two witness trees"
    if status == "invalidGrammar":
        failure = response.get("failure")
        if code == "InvalidOverlay":
            if "fault" in response or not (type(failure) is list and len(failure) == 3 and all(
                    _text(x) for x in failure) and failure[1] in OVERLAY_SITES.get(failure[0], ())):
                return "invalid overlay failure"
        else:
            if response.get("fault") not in FAULTS:
                return f"invalidGrammar fault {response.get('fault')!r}"
            # A refused vocabulary names its first failure (`lexiconFailure`); no other fault has one.
            if (failure is not None) != (response["fault"] == "lexicon") or failure is not None and not (
                    type(failure) is list and len(failure) == 3 and all(_text(x) for x in failure)):
                return "invalidGrammar failure is not the first (condition, kind, name) of a lexicon fault"
    return None


def response_problem(response, expected: dict, env, source: str) -> str | None:
    """Why `response` is not a well-formed `english.read` answer (spec 4.4) to the request over `env` whose
    identities are `expected`, or None. Every formula must decode under `env`; every transport, the test
    override included, is checked by this one function."""
    if type(response) is not dict:
        return "the response is not an object"
    if _has_null(response):
        return "the response has a null"
    found = response.get("identities")
    if type(found) is not dict or found.keys() != expected.keys() or \
            not all(type(value) is str for value in found.values()):
        return f"identities {sorted(found) if type(found) is dict else found!r}, expected {sorted(expected)}"
    for name in IDENTITIES:
        if found.get(name) != expected.get(name):
            return f"{name} {found.get(name)!r} is not the request's {expected.get(name)!r}"
    body = {k: v for k, v in response.items() if k != "identities"}
    if body.get("status") != "one":
        return refusal_problem(body, source)
    required = FIELDS["one"][0] | {"status"}
    if body.keys() != required:
        return f"a one response with fields missing {sorted(required - body.keys())}, " \
               f"unknown {sorted(body.keys() - required)}"
    formulas, conclusions = body["ast"], body["conclusions"]
    if type(formulas) is not list or not formulas:
        return "ast is not a non-empty list of formulas"
    try:
        ast.core_gate(env)
    except VEError:
        # The core checker refuses every formula under this environment, so its decoding cannot judge Lean's
        # answer; the reading's own decoding raises the gate's refusal, as Python's reader does (E2.5).
        gated = True
    else:
        gated = False
    for formula in [] if gated else formulas:
        try:
            ast.formula_from_data(env, formula)
        except VEError as exc:
            return f"a formula does not decode under the environment: {exc}"
    if type(conclusions) is not list or not all(_nat(i) and i < len(formulas) for i in conclusions) \
            or conclusions != sorted(set(conclusions)):
        return "conclusions are not increasing indices of the formulas"
    if not _trees(body["derivation"], len(formulas)):
        return "derivation does not give one tree per sentence"
    n = len(formulas)
    spans = body["spans"]
    if type(spans) is not list or len(spans) != n or not all(_span(s, source) for s in spans):
        return "spans do not match the sentences"
    if any(spans[i][1] > spans[i + 1][0] for i in range(n - 1)):
        return "sentence spans overlap"
    obligations = body["obligations"]
    if type(obligations) is not list or len(obligations) != len(conclusions):
        return "obligations do not match conclusions"
    for marked, item in zip(conclusions, obligations):
        if type(item) is not dict or item.keys() != {"conclusion", "premises", "unproved"}:
            return "malformed obligation"
        premises = item["premises"]
        if (not _nat(item["conclusion"]) or item["conclusion"] != marked
                or type(premises) is not list or not premises
                or not all(_nat(j) and j < marked and j not in conclusions for j in premises)
                or premises != sorted(set(premises))
                or type(item["unproved"]) is not str or item["unproved"].count("{status}") != 1):
            return "invalid obligation premises or text"
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

    def gate(self) -> VEError | None:
        """The core checker's refusal of the environment (`ast.core_gate`), which decoding a reading's formulas
        raises whatever they are; None when there is none."""
        try:
            ast.core_gate(self.env)
        except VEError as exc:
            return exc
        return None

    def classes(self) -> tuple[str, ...]:
        """The Python classes the comparator accepts for this outcome: Lean's class, with the tolerance the
        comparator keeps (spec 2.9). A reading under a gated environment is the gate's refusal."""
        if self.status == "one":
            gate = self.gate()
            return ("accepted",) if gate is None else (type(gate).__name__,)
        code = self.response["code"]
        return COMPARATOR_CLASSES.get(code, (self.response["class"],))

    def document(self) -> ast.Document:
        """The formulas, which `response_problem` decoded once already."""
        return ast.Document(tuple(ast.formula_from_data(self.env, f) for f in self.response["ast"]))

    def canonical(self) -> str:
        """The canonical strict text of the formulas, by Python's printer (the owner of the printer)."""
        from ..printer import print_document
        return print_document(self.env, self.document())

    def message(self, help_text: str | None = None) -> str:
        """Lean's text, then Lean's advice, then the relay's editor help (spec 2.8: the nearest wording)."""
        parts = [self.response["text"]]
        advice = self.response.get("advice")
        if advice is not None:
            parts.append(advice["text"])
        elif help_text:
            parts.append(help_text)
        return " ".join(parts)

    def rejection(self, help_text: str | None = None) -> Exception:
        """Lean's outcome other than `one` as the exception of the class Lean names, with Lean's text and span;
        the answer rides along as `lean_reading` for the shadow record."""
        cls = ERROR_CLASSES[self.response["class"]]
        if issubclass(cls, CheckerUnavailable):
            error = cls(self.message(), operation="english.admission", backend="lean")
        else:
            span = self.response.get("span")  # an overlay refusal reads no text, so it has none
            where = None if span is None else Span(span[0], span[1], self.source.count("\n", 0, span[0]) + 1,
                                                    span[0] - self.source.rfind("\n", 0, span[0]))
            error = cls(self.message(help_text), span=where)
        error.lean_reading = self
        return error

    def comparison(self, python_class: str) -> dict:
        """The comparison form of 2.11, with Lean's class read as Python's when the map allows it."""
        allowed = self.classes()
        out = {"code": python_class if python_class in allowed else allowed[0]}
        out["verdict"] = _verdict(out["code"])
        if self.status == "one" and out["code"] == "accepted":
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
            if self.gate() is None:
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
        problem = response_problem(response, expected, env, source)
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
        refusal = {k: v for k, v in result.items() if k != "identities"}
        try:
            problem = refusal_problem(refusal, "") if refusal.get("status") == "invalidGrammar" else \
                "an English check answers only invalidGrammar"
        except RecursionError:
            problem = "the refusal is nested too deeply"
        if problem:
            raise CheckerUnavailable(f"CheckerUnavailable: malformed English check refusal: {problem}")
        cls = ERROR_CLASSES[refusal["class"]]
        if issubclass(cls, CheckerUnavailable):
            raise cls(refusal["text"], operation="english.check", backend="lean")
        raise cls(refusal["text"])
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
            if str(refused) == NO_PREMISE:
                # Python's admission refused the document at its premise check, which Lean now owns as
                # `ConclusionWithoutPremise` (spec 2.9): compare the public outcome, not the reading alone.
                left = {"verdict": "rejected", "code": python_class(refused)}
                record["python"] = {"class": python_class(refused), "message": str(refused)}
    reading = getattr(lean, "lean_reading", None) if isinstance(lean, BaseException) else lean.lean
    if reading is None:
        right = {"verdict": "unavailable", "code": python_class(lean)}
        record["lean"] = {"status": "unavailable", "code": right["code"], "message": str(lean)}
    else:
        right = reading.comparison(left["code"])
        record["lean"] = reading.record()
        record["identities"] = reading.response["identities"]
    record["classes"] = [] if "excluded" in record else dispatch._classes(left, right)
    if TRANSPORT is not None:
        record["planted"] = "test transport"  # a test's answer, not Lean's: no evidence either way
    return record
