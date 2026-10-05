"""Python's outcome on every fixture of docs/spec/english-lean-s3.md 8.1 to 8.5 and 8.7 (spec ev5, S3.5).

The spec computed each fixture in Lean and read Python's outcome from the source (spec 12, plan question 1).
This harness runs Python at the dispatched boundary (the reading the unit `english.admission` dispatches,
`ve.english._python_reading`, with Python's own lexicon) and compares its outcome with the spec's under the
class map of spec 2.8 and base 4.1: `one` or `ok` is an accepted document with the same formulas and marks,
`zero` (and `none` under `stopped`) is `SyntaxError`, `many` is `AmbiguousDerivation`, a lexical refusal
is `SyntaxError`, and a rejection is the class of its code (`CLASSES` of the adapter). A difference is a
finding, not a failed fixture. The one agreed difference is or38's (spec 2.11, Q11): Python reports
`ResourceLimit` where Lean has no reading.

Formulas are compared in the notation of spec 8 (S2's): `pred p [t, u]`, `all s (...)`, `scale -1 (t)`.
`python_text` is a fixture's text rewritten to Python's selected wording where Python's producer selects
another wording than the spec's hand-written lexicon (the `FA` family: `safe`, see `FINDINGS`): the guard
structure is then still compared, and the exact text's outcome is reported beside it.

    python -m conformance.english_lean_s3_python [--output PATH]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import warnings

from conformance import english_lean_s3_fixtures as X

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "conformance/english-lean/s3-python-report.json"

# Spec 2.8 and base 4.1: the Python class of each Lean outcome.
REJECTION_CLASS = {"nestingLimit": "ResourceLimit", "numeralBound": "ResourceLimit",
                   "coefficientNotNumeral": "SyntaxError", "unboundReference": "SyntaxError",
                   "sortMismatch": "SyntaxError", "blockedWording": "SyntaxError",
                   "pronounUnresolved": "SyntaxError"}
STATUS_CLASS = {"zero": "SyntaxError", "none": "SyntaxError", "many": "AmbiguousDerivation",
                "lexical": "SyntaxError"}
# The agreed differences of spec 2.11 (Q11): Lean `none`, Python `ResourceLimit`.
AGREED = {"or38a": "ResourceLimit", "or38b": "ResourceLimit"}

SIGNS = "-" * 64


def costs(t: str) -> str:
    return f"pred costs [const legacy, {t}]"


def nested_scale(n: int, inner: str) -> str:
    out = inner
    for _ in range(n):
        out = f"scale -1 ({out})"
    return out


def A(o: str) -> str:
    return f"pred available [var 0, {o}]"


def D(i: int) -> str:
    return f"not (eq (var 0) (var {i}))"


S = "pred safe [var 0]"
LD = "pred leads_to [var 0, const injury]"
R = "const robot"


def M(a: str, h: str) -> str:
    return f"pred risk__might_lead_to [{a}, {h}]"


def one(*formulas: str) -> dict:
    return {"status": "one", "formulas": list(formulas)}


def ok(*formulas: str, marks=None) -> dict:
    return {"status": "ok", "formulas": list(formulas), **({"marks": marks} if marks is not None else {})}


def rejected(code: str, stopped: int | None = None) -> dict:
    return {"status": "rejected", "code": code, **({"stopped": stopped} if stopped is not None else {})}


ZERO = {"status": "zero"}
MANY = {"status": "many"}


def lexical(code: str) -> dict:
    return {"status": "lexical", "code": code}


def _fixtures() -> list[tuple[str, str, str, dict]]:
    """(id, environment, text, the spec's expected outcome), in the order of spec 8."""
    fo = [
        ("or1", "Legacy costs 5.", one(costs("num 5"))),
        ("or2", "Legacy costs -5.", one(costs("num -5"))),
        ("or3", "Legacy costs -0.", one(costs("num 0"))),
        ("or4", "Legacy costs [budget + 1].", one(costs("add (const budget) (num 1)"))),
        ("or5", "Legacy costs [budget - limit].", one(costs("add (const budget) (scale -1 (const limit))"))),
        ("or6a", "Legacy costs [3 * budget].", one(costs("scale 3 (const budget)"))),
        ("or6b", "Legacy costs [-3 * budget].", one(costs("scale -3 (const budget)"))),
        ("or7", "Legacy costs [budget * limit].", rejected("coefficientNotNumeral")),
        ("or8", "Legacy costs [[budget + 1] * limit].", rejected("coefficientNotNumeral")),
        ("or9", "Legacy costs twice the budget.", one(costs("scale 2 (const budget)"))),
        ("or10a", "Legacy costs -budget.", one(costs("scale -1 (const budget)"))),
        ("or10b", "Legacy costs --budget.", one(costs("scale -1 (scale -1 (const budget))"))),
        ("or11", "Legacy costs -[budget + 1].", one(costs("scale -1 (add (const budget) (num 1))"))),
        ("or12", "Legacy costs [budget - -5].", one(costs("add (const budget) (scale -1 (num -5))"))),
        ("or13", "Legacy costs [[budget + 1] + [2 * limit]].",
         one(costs("add (add (const budget) (num 1)) (scale 2 (const limit))"))),
        ("or14", "Legacy costs [[budget + 1] + [limit * 2]].", rejected("coefficientNotNumeral")),
        ("or15a", "Budget is at most 5.", one("le (const budget) (num 5)")),
        ("or15b", "Budget IS AT MOST 5.", one("le (const budget) (num 5)")),
        ("or16a", "Budget is less than limit.", one("lt (const budget) (const limit)")),
        ("or16b", "Budget is more than limit.", one("lt (const limit) (const budget)")),
        ("or17", "Budget is at least [limit + 1].", one("le (add (const limit) (num 1)) (const budget)")),
        ("or18a", "Budget is the same as limit.", one("eq (const budget) (const limit)")),
        ("or18b", "Budget exceeds limit.", one("pred exceeds [const budget, const limit]")),
        ("or19a", "Every service that costs 5 is reviewed.",
         one("all service (implies (pred costs [var 0, num 5]) (pred reviewed [var 0]))")),
        ("or19b", "Every service costs twice the budget.",
         one("all service (pred costs [var 0, scale 2 (const budget)])")),
        ("or20", "Legacy costs --5.", ZERO),
        ("or21", "Legacy costs -twice the budget.", ZERO),
        ("or22", "Legacy costs - budget.", ZERO),
        ("or23a", "Legacy costs [budget+1].", ZERO),
        ("or23b", "Legacy costs [budget +1].", ZERO),
        ("or24a", "Legacy costs [ budget + 1].", ZERO),
        ("or24b", "Legacy costs [budget + 1 ].", ZERO),
        ("or25", "Legacy costs 007.", lexical("badNumeral")),
        ("or26a", "Legacy costs legacy.", ZERO),
        ("or26b", "Legacy is the same as budget.", ZERO),
        ("or26c", "Budget is the same as legacy.", ZERO),
        ("or26d", "Legacy costs twice the 5.", ZERO),
        ("or27", "Legacy is deployed. It costs 5.", ok("pred deployed [const legacy]", costs("num 5"))),
        ("or28a", "It costs 5.", rejected("pronounUnresolved")),
        ("or28b", "That service costs 5.", rejected("unboundReference")),
        ("or29", "Legacy costs " + "-" * 63 + "budget.", one(costs(nested_scale(63, "const budget")))),
        ("or30", "Legacy costs " + SIGNS + "budget.", rejected("nestingLimit")),
        ("or31", "Legacy costs [[budget * limit] + " + SIGNS + "budget].", rejected("nestingLimit")),
        ("or32", "That service costs " + SIGNS + "budget.", rejected("unboundReference")),
        ("or33a", "Budget is at most " + SIGNS + "budget.", rejected("nestingLimit")),
        ("or33b", "[budget * limit] is at most " + SIGNS + "budget.", rejected("nestingLimit")),
        ("or34a", "Legacy costs " + "9" * 40 + ".", one(costs("num " + "9" * 40))),
        ("or34b", "Legacy costs " + "9" * 41 + ".", rejected("numeralBound")),
        ("or35a", "Legacy costs -" + "9" * 39 + ".", one(costs("num -" + "9" * 39))),
        ("or35b", "Legacy costs -" + "9" * 40 + ".", rejected("numeralBound")),
        ("or36a", "Every service is reviewed.", one("all service (pred reviewed [var 0])")),
        ("or36b", "For every service that is deployed, there is a person who owns that service.",
         one("all service (implies (pred deployed [var 0]) (ex person (pred owns [var 0, var 1])))")),
        ("or38a", SIGNS + "budget exceeds [ limit + 1].", ZERO),
        ("or38b", "Legacy costs " + SIGNS + "[ limit + 1].", ZERO),
    ]
    fo_cap = [
        ("or37a", '"budget_cap" is at most 5.', one("le (const budget_cap) (num 5)")),
        ("or37b", 'Legacy costs "budget_cap".', one(costs("const budget_cap"))),
        ("or37c", 'Legacy costs twice the "budget_cap".', ZERO),
    ]
    da_pairs = [(r, p) for r in ("owner_of", "backup_of") for p in ("senior", "deployed", "reviewed")]
    da_expected = {("owner_of", "senior"): "person", ("backup_of", "deployed"): "service",
                   ("backup_of", "reviewed"): "service"}
    fd = [
        ("da1", "The owner_of of legacy is alice.", one("pred owner_of [const legacy, const alice]")),
        ("da2", 'Legacy has the recorded relation "owner_of" to alice.',
         one("pred owner_of [const legacy, const alice]")),
        ("da3", "The owner_of of legacy is senior.",
         one("ex person (and (pred owner_of [const legacy, var 0]) (pred senior [var 0]))")),
        ("da4", "The owner_of of legacy is deployed.", ZERO),
        ("da5", "The backup_of of legacy is deployed.",
         one("ex service (and (pred backup_of [const legacy, var 0]) (pred deployed [var 0]))")),
        ("da6", "For every service, the owner_of of that service is senior.",
         one("all service (ex person (and (pred owner_of [var 1, var 0]) (pred senior [var 0])))")),
        ("da7", "The owns of alice is legacy.", ZERO),
        ("da8", "The Owner_of of legacy is alice.", ZERO),
        ("da9", "If legacy is deployed, then The owner_of of legacy is alice.", ZERO),
        ("da10", "Every service that the owner_of of that service is alice is reviewed.", ZERO),
        ("da11", "If legacy is deployed, then the owner_of of legacy is alice.",
         one("implies (pred deployed [const legacy]) (pred owner_of [const legacy, const alice])")),
        ("da12", "Legacy is deployed. The backup_of of it is legacy.",
         ok("pred deployed [const legacy]", "pred backup_of [const legacy, const legacy]")),
        ("da13", "Legacy is deployed. The backup_of of legacy is it.",
         ok("pred deployed [const legacy]", "pred backup_of [const legacy, const legacy]")),
        ("da14", "Legacy is deployed. The backup_of of it is deployed.",
         ok("pred deployed [const legacy]",
            "ex service (and (pred backup_of [const legacy, var 0]) (pred deployed [var 0]))")),
        ("da15", "Legacy is deployed. If legacy is deployed, then the backup_of of it is legacy.",
         rejected("pronounUnresolved", stopped=1)),
        ("da16", "The backup_of of it is legacy.", rejected("pronounUnresolved", stopped=0)),
    ] + [
        (f"da17.{r}.{p}", f"The {r} of legacy is {p}.",
         one(f"ex {da_expected[(r, p)]} (and (pred {r} [const legacy, var 0]) (pred {p} [var 0]))")
         if (r, p) in da_expected else ZERO)
        for r, p in da_pairs
    ]
    fa = [
        ("al1", "Every action available to robot is safe.", one(f"all action (implies {_p(A(R))} {_p(S)})")),
        ("al2", "For every action, every other action available to robot is safe.",
         one(f"all action (all action (implies (and {_p(A(R))} ({D(1)})) {_p(S)}))")),
        ("al3", "For every action, another action available to robot is safe.",
         one(f"all action (ex action (and (and {_p(A(R))} ({D(1)})) {_p(S)}))")),
        ("al4a", "Every other action available to robot is safe.", rejected("unboundReference")),
        ("al4b", "Another action available to robot is safe.", rejected("unboundReference")),
        ("al5", "For every action named A1, for every action named A2, every other action available to robot "
                "is safe.",
         one(f"all action (all action (all action (implies (and {_p(A(R))} ({D(1)})) {_p(S)})))")),
        ("al6", "For every action named A1, for every action named A2, every other action available to robot "
                "excluding A1 is safe.",
         one(f"all action (all action (all action (implies (and {_p(A(R))} ({D(2)})) {_p(S)})))")),
        ("al7", "For every action named A1, for every action named A2, another action available to robot "
                "excluding A1 is safe.",
         one(f"all action (all action (ex action (and (and {_p(A(R))} ({D(2)})) {_p(S)})))")),
        ("al8", "For every action, every other action available to robot excluding robot is safe.",
         rejected("sortMismatch")),
        ("al9", "For every agent, for every action, every other action available to robot excluding that agent "
                "is safe.", rejected("sortMismatch")),
        ("al10", "Every action available to robot excluding robot is safe.", ZERO),
        ("al11", "For every action, every other action available to robot that other action leads to injury.",
         one(f"all action (all action (implies (and {_p(A(R))} ({D(1)})) {_p(LD)}))")),
        ("al12", "For every action, another action available to robot either is safe or leads to injury.",
         one(f"all action (ex action (and (and {_p(A(R))} ({D(1)})) (or {_p(S)} {_p(LD)})))")),
        ("al13", "For every action, another action available to robot either is safe or leads to injury, or "
                 "both.",
         one(f"all action (ex action (and (and {_p(A(R))} ({D(1)})) (or {_p(S)} {_p(LD)})))")),
        ("al14", "For every action, another action available to robot both is safe and leads to injury.",
         one(f"all action (ex action (and (and {_p(A(R))} ({D(1)})) (and {_p(S)} {_p(LD)})))")),
        ("al15", "For every action, every other action available to robot either that other action is safe or "
                 "leads to injury.",
         one(f"all action (all action (implies (and {_p(A(R))} ({D(1)})) (or {_p(S)} {_p(LD)})))")),
        ("al16", "For every action, another action available to robot that other action is the same as wait.",
         one(f"all action (ex action (and (and {_p(A(R))} ({D(1)})) (eq (var 0) (const wait))))")),
        ("al17", "For every action, every other action available to robot is the same as wait.", ZERO),
        ("al18", "Every action available to robot that action is safe.",
         one(f"all action (implies {_p(A(R))} {_p(S)})")),
        ("al19", "Every action available to robot that other action is safe.", rejected("unboundReference")),
        ("al20", "For every action, every other action available to robot that action is safe.",
         rejected("unboundReference")),
        ("al21", "For every action, that other action is safe.", rejected("unboundReference")),
        ("al22a", "Every action available to it is safe.", rejected("pronounUnresolved")),
        ("al22b", "Every action available to that agent is safe.", rejected("unboundReference")),
        ("al23", "For every agent, every action available to that agent is safe.",
         one(f"all agent (all action (implies {_p(A('var 1'))} {_p(S)}))")),
        ("al24", "For every action, every other action available to robot That other action is safe.", ZERO),
        ("al25", "Every Action available to robot is safe.", ZERO),
        ("al26", "Every action Available to robot is safe.", ZERO),
        ("al27", "Every action available to robot wait is safe.", ZERO),
        ("al28", "Every action available to robot this holds in all cases.", ZERO),
        ("al29", "For every action, every other action available to robot is the same as that other action.",
         {"status": "none", "stopped": 0}),
        ("al30", "For every action, another action available to robot that other action is the same as That "
                 "Other Action.",
         one(f"all action (ex action (and (and {_p(A(R))} ({D(1)})) (eq (var 0) (var 0))))")),
        ("al31a", "Injury is preventable by robot.", one("pred avoidable [const injury, const robot]")),
        ("al31b", "Injury is avoidable by robot.", one("pred avoidable [const injury, const robot]")),
        ("al32a", "Wait lets injury happen.", one("pred allows [const wait, const injury]")),
        ("al32b", "Wait does not lead to injury.", one("not (pred leads_to [const wait, const injury])")),
        ("al32c", "Wait prevents injury.", one("pred prevents [const wait, const injury]")),
        ("al33", "Wait is safe. Therefore every action available to robot is safe.",
         ok("pred safe [const wait]", f"all action (implies {_p(A(R))} {_p(S)})", marks=[False, True])),
        ("al34", "For every action, every action available to robot is safe.",
         one(f"all action (all action (implies {_p(A(R))} {_p(S)}))")),
        ("al35", "Wait cannot lead to injury.", ZERO),
    ]
    fa2 = [
        ("al36", 'Every entity of sort "action" available to robot is safe.',
         one(f"all action (implies {_p(A(R))} {_p(S)})")),
        ("al37", 'For every entity of sort "action", every other entity of sort "action" available to robot that '
                 'other entity of sort "action" is safe.',
         one(f"all action (all action (implies (and {_p(A(R))} ({D(1)})) {_p(S)}))")),
        ("al38a", 'Every entity of sort "Action" available to robot is safe.', ZERO),
        ("al38b", 'Every Entity of sort "action" available to robot is safe.', ZERO),
    ]
    ci = "const injury"
    fr = [
        ("ri1", "Wait might lead to injury.", one(M("const wait", ci))),
        ("ri2", "Wait cannot lead to injury.", one(f"not ({M('const wait', ci)})")),
        ("ri3a", "Wait might not lead to injury.", one("not (pred leads_to [const wait, const injury])")),
        ("ri3b", "Wait leads to injury.", one("pred leads_to [const wait, const injury]")),
        ("ri4", "Injury is catastrophic.", one("pred risk__class [const injury, const catastrophic]")),
        ("ri5", "Injury is minor or worse.", one("pred risk__or_worse [const injury, const minor]")),
        ("ri6", "Wait has a less severe worst case than wait.", one("pred risk__less_worst [const wait, const wait]")),
        ("ri7", "Catastrophic is more severe than minor.",
         one("pred risk__more_severe [const catastrophic, const minor]")),
        ("ri8", "Wait might prevent injury.", one("pred prevents [const wait, const injury]")),
        ("ri9", "For every harm that is catastrophic, wait cannot lead to that harm.",
         one(f"all harm (implies (pred risk__class [var 0, const catastrophic]) (not ({M('const wait', 'var 0')})))")),
        ("ri10", "Every action available to robot cannot lead to injury.", rejected("blockedWording")),
        ("ri11a", "Every action available to robot either is safe or cannot lead to injury.",
         rejected("blockedWording")),
        ("ri11b", "Every action available to robot both cannot lead to injury and is safe.",
         rejected("blockedWording")),
        ("ri12", "For every action, every other action available to robot cannot lead to injury.",
         one(f"all action (all action (implies (and {_p(A(R))} ({D(1)})) (not ({M('var 0', ci)}))))")),
        ("ri13", "For every action, another action available to robot cannot lead to injury.",
         one(f"all action (ex action (and (and {_p(A(R))} ({D(1)})) (not ({M('var 0', ci)}))))")),
        ("ri14", "Every action available to robot might not lead to injury.",
         one(f"all action (implies {_p(A(R))} (not {_p(LD)}))")),
        ("ri15", "Every action available to robot might lead to injury.",
         one(f"all action (implies {_p(A(R))} {_p(M('var 0', ci))})")),
    ] + [(f"ri17.{k}", text, ZERO) for k, text in enumerate([
        "Wait may lead to injury.", "Wait does not lead to injury.", "Wait could lead to injury.",
        "Wait risks injury.", "Wait is likely to lead to injury.", "Wait increases the risk of injury.",
        "Wait certainly leads to injury.", "Wait prevents injury.", "Wait is safer than wait.",
        "Wait leads to injury unless wait is safe.", "Wait cannot lead to injury exactly when wait is safe.",
        "Wait causes injury.", "Wait results in injury."], 1)]
    fm = [
        ("mo1a", "Alice may access legacy.", one("pred access [const alice, const legacy]")),
        ("mo1b", "Alice must review legacy.", one("pred review [const alice, const legacy]")),
        ("mo2", "Every person who may access legacy owns legacy.",
         one("all person (implies (pred access [var 0, const legacy]) (pred owns [var 0, const legacy]))")),
        ("mo3a", "Alice may not access legacy.", ZERO),
        ("mo3b", "Alice access legacy.", ZERO),
    ]
    rg = [(f"rg{k}.{env}", text, ZERO) for k, text, envs in (
        (1, "Every service is deployed or reviewed, or both.", ("FO", "FD")),
        (2, "For every person, if that person is deployed and that person is reviewed, then that person is "
            "reviewed.", ("FO",)),
        (3, "No service that is deployed is not reviewed.", ("FO", "FD"))) for env in envs]
    out = [(i, "FO", t, e) for i, t, e in fo] + [(i, "FO+cap", t, e) for i, t, e in fo_cap]
    out += [(i, "FD", t, e) for i, t, e in fd] + [(i, "FA", t, e) for i, t, e in fa]
    out += [(i, "FA2", t, e) for i, t, e in fa2] + [(i, "FR", t, e) for i, t, e in fr]
    out += [(i, "FM", t, e) for i, t, e in fm]
    out += [(i, i.split(".")[1], t, e) for i, t, e in rg]
    return out


def _p(formula: str) -> str:
    return f"({formula})"


def environment_json(name: str) -> dict:
    if name == "FO+cap":
        raw = X.FO()
        raw["vocabulary"]["constants"]["budget_cap"] = {"sort": "$int", "description": "$int"}
        return raw
    if name == "FA2":
        # The action sort on its fallback noun: a declared noun that is a predicate's name is refused, and
        # Python selects `entity of sort "action"` (`english.py:233–248`).
        raw = X.FA()
        raw["vocabulary"]["sorts"]["action"]["verbalisation"] = {"singular": "safe", "plural": "safes"}
        return raw
    return X.BUILDERS[name]()


# ------------------------------------------------------------------ the notation of spec 8

def term(t) -> str:
    from ve import ast
    if isinstance(t, ast.Var):
        return f"var {t.index}"
    if isinstance(t, ast.Const):
        return f"const {t.name}"
    if isinstance(t, ast.Num):
        return f"num {t.value}"
    if isinstance(t, ast.Add):
        return f"add ({term(t.left)}) ({term(t.right)})"
    if isinstance(t, ast.Scale):
        return f"scale {t.coefficient} ({term(t.term)})"
    raise TypeError(type(t).__name__)


def formula(f) -> str:
    from ve import ast
    if isinstance(f, ast.Top):
        return "top"
    if isinstance(f, ast.Bottom):
        return "bottom"
    if isinstance(f, ast.Unary):
        return f"pred {f.predicate} [{term(f.term)}]"
    if isinstance(f, ast.Binary):
        return f"pred {f.predicate} [{term(f.left)}, {term(f.right)}]"
    if isinstance(f, ast.Atom):
        return f"pred {f.predicate} [{', '.join(term(t) for t in f.terms)}]"
    if isinstance(f, (ast.Eq, ast.Lt, ast.Le)):
        return f"{type(f).__name__.lower()} ({term(f.left)}) ({term(f.right)})"
    if isinstance(f, ast.Not):
        return f"not ({formula(f.body)})"
    if isinstance(f, (ast.And, ast.Or, ast.Implies)):
        return f"{type(f).__name__.lower()} ({formula(f.left)}) ({formula(f.right)})"
    if isinstance(f, ast.Forall):
        return f"all {f.sort} ({formula(f.body)})"
    if isinstance(f, ast.Exists):
        return f"ex {f.sort} ({formula(f.body)})"
    raise TypeError(type(f).__name__)


# ------------------------------------------------------------------ the run

def python_outcome(env, text: str) -> dict:
    """Python's outcome at the dispatched boundary: the reading `english.admission` dispatches (the hand
    parser, the Lark audit and the typed check, `_python_reading`), before the conclusion check, which runs
    after the dispatch for either backend (S2 2.10, D16): the formulas and marks, or the error's class."""
    from ve.english import EnglishVocabulary, UnreviewedVocabularyWarning, _python_reading
    from ve.errors import VEError
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UnreviewedVocabularyWarning)
        try:
            reading = _python_reading(env, text, EnglishVocabulary(env), {})
        except VEError as exc:
            # The first line only: Lark lists its expected terminals in no fixed order.
            return {"class": type(exc).__name__, "message": str(exc).split("\n", 1)[0]}
    marked = set(reading.conclusions)
    formulas = reading.document.formulas
    return {"class": "accepted", "formulas": [formula(f) for f in formulas],
            "marks": [i in marked for i in range(len(formulas))]}


def expected_class(expected: dict) -> str:
    status = expected["status"]
    if status in ("one", "ok"):
        return "accepted"
    if status == "rejected":
        return REJECTION_CLASS[expected["code"]]
    return STATUS_CLASS[status]


def agrees(fixture_id: str, expected: dict, got: dict) -> bool:
    if fixture_id in AGREED:
        return got["class"] == AGREED[fixture_id]
    if got["class"] != expected_class(expected):
        return False
    if got["class"] != "accepted":
        return True
    if got["formulas"] != expected["formulas"]:
        return False
    return expected.get("marks") is None or got["marks"] == expected["marks"]


def python_text(env_name: str, text: str, words) -> str | None:
    """The fixture's text in the selections Python makes where the spec's hand-written lexicon `LA` makes
    others (`FINDINGS`): `is safe` in Python's wording for `safe`, and the labels `A1`, `A2` with Python's
    letter for the action sort. None when Python selects what the spec does."""
    if not env_name.startswith(("FA", "FR")):
        return None
    out = text
    selected = words.predicates.get("safe")
    if selected and selected != "{0} is safe":
        out = out.replace(" is safe", " " + selected.removeprefix("{0} "))
    letter = words.letters.get("action")
    if letter and letter != "A":
        out = re.sub(r"\bA([12])\b", lambda m: letter + m[1], out)
    return None if out == text else out


# What the run shows about the spec's fixtures, for the S3 report: each a difference between the spec's
# hand-written lexicon and the one Python's producer selects for the same environment.
FINDINGS = {
    "safe-fallback": "Under `FA` and `FR` Python selects `{0} is classified as \"safe\"` for `safe`: the declared "
                     "`{0} is safe` carries SYMBOL_COLLISION, because `is` is the head of the fixed role wording "
                     "`{0} is available to {1}` (`printer.py:201-205`, `:245-246`). The spec's `LA` and `LR` select "
                     "`{0} is safe`, which V6 (E2.1) would refuse.",
    "action-letter": "Under `FA` Python's letter for the action sort is `C`, not the spec's `A` (al5 to al7).",
}


def report() -> dict:
    from ve import Environment
    from ve.english import EnglishVocabulary, UnreviewedVocabularyWarning
    envs, words = {}, {}
    rows = []
    for fixture_id, env_name, text, expected in _fixtures():
        if env_name not in envs:
            envs[env_name] = Environment(environment_json(env_name))
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UnreviewedVocabularyWarning)
                words[env_name] = EnglishVocabulary(envs[env_name])
        got = python_outcome(envs[env_name], text)
        row = {"id": fixture_id, "environment": env_name, "text": text, "expected": expected,
               "expected_class": AGREED.get(fixture_id, expected_class(expected)), "python": got,
               "agrees": agrees(fixture_id, expected, got)}
        alternative = python_text(env_name, text, words[env_name])
        if alternative is not None:
            again = python_outcome(envs[env_name], alternative)
            row["python_text"] = alternative
            row["python_on_python_text"] = again
            row["agrees_on_python_text"] = agrees(fixture_id, expected, again)
        rows.append(row)
    findings = [r["id"] for r in rows if not r["agrees"]]
    structural = [r["id"] for r in rows if not r["agrees"] and not r.get("agrees_on_python_text", False)]
    return {"format": "ve.english-lean-s3-python@1", "fixtures": len(rows),
            "agree": len(rows) - len(findings), "differ": len(findings), "differences": findings,
            "differences_on_python_text": structural, "agreed_differences": sorted(AGREED),
            "findings": FINDINGS,
            "selected": {name: {"safe": v.predicates.get("safe"), "action_letter": v.letters.get("action"),
                                "risk__more_severe": v.predicates.get("risk__more_severe")}
                         for name, v in words.items()},
            "rows": rows}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--output", type=Path, default=REPORT)
    args = parser.parse_args(argv)
    out = report()
    args.output.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: out[k] for k in ("fixtures", "agree", "differ", "differences")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
