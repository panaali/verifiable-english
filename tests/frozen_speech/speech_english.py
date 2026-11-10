"""The pre-switch speech parser of `ve/speech_english.py`, frozen at ci-2b's base (63b2b596f): its command branch
(`_command_candidates`, `parse_speech`'s `You may`, `Please`, coordination, proof-task and `text.endswith(".")`
blocks), which commands-imperatives CI-2 deleted from the product (Lean's `VE.Commands.readInstruction` reads
commands). Test data only: the frozen checkers here and the ci-2b A/B's base read commands with it; the question
forms and helpers are the live module's."""
from __future__ import annotations

from itertools import product
import re

from ve.ast import _to_data
from ve.errors import VEError
from ve.speech_acts import ascii_fold, wording_text
from ve.speech_english import (_LEAN_PREFIXES, _alternatives, _body, _formula, _name, _polar,  # noqa: F401
                               _sentence)
from tests.frozen_speech.speech_acts import PROOF_TASK_ACT, act_verb


def _command_candidates(env, scope):
    """Enumerate declared act phrases with bound names and definite synonyms."""
    for predicate, decl in env.predicates.items():
        reg = decl.regulated
        # An imperative begins with its act's verb (3.2): an act whose first word after `{0}` is a slot has none.
        if reg is None or reg.role not in ("obligation", "permission") or act_verb(reg.act) is None:
            continue
        names = []
        for sort in decl.arguments[1:]:
            choices = []
            for name, constant in env.constants.items():
                if constant.sort == sort:
                    choices.append((name, name))
                    choices.extend((phrase, name) for phrase, bound in scope.get("definites", {}).items()
                                   if bound == name)
            names.append(choices)
        for bindings in product(*names):
            display = [None, *(label for label, _ in bindings)]
            phrase = reg.act[4:].format(*display)
            yield phrase, predicate, tuple(value for _, value in bindings), reg.role



def parse_speech(env, source, scope, *, query=None, reading_set=None, warnings=None):
    """Return a typed wire content object and its kind; reject other wordings.

    Advisory lints (`OpaqueWording`) are appended to `warnings` when given.
    """
    if type(source) is not str:
        raise VEError("InvalidInput: speech wording")
    text = wording_text(source)
    if not text:
        raise VEError("InvalidInput: speech wording")
    if text == "Which reading did you mean?":
        if reading_set is None:
            raise VEError("InvalidInput: reading set required")
        return {"mode": "reading", "set": reading_set[0], "version": reading_set[1]}, "question"
    if text.startswith("Does it follow from these premises that ") and text.endswith("?"):
        if query is None:
            raise VEError("InvalidInput: query required")
        _sentence(env, text[len("Does it follow from these premises that "):-1] + ".", warnings)
        return {"mode": "follows", "query": query}, "question"
    if text.startswith(_LEAN_PREFIXES):
        return _polar(env, text)
    for mode, pattern in (("which_one", r"Which one of (.+) is (.+)\?"),
                          ("which_all", r"Which of (.+) are (.+)\?")):
        match = re.fullmatch(pattern, text)
        if match:
            domain = [_name(env, name) for name in _alternatives(match[1])]
            sort = env.constants[domain[0]].sort
            if any(env.constants[name].sort != sort for name in domain):
                raise VEError("AlternativeSort: wording")
            rest = "is " + match[2]
            return {"mode": mode, "sort": sort, "domain": domain,
                    "body": _body(env, domain[0], rest, warnings)}, "question"
    if text.startswith("Which "):
        raise VEError("OpenDomainWhich: list the named alternatives")
    if text.startswith("You may "):
        raise VEError("PermissionNotCommand: use an equality-guarded W1 rule")
    if text.startswith("Please "):
        raise VEError("InvalidInput: please needs author approval")
    if " and " in text and not text.startswith("Do not "):
        # A conjunction may be inside a declared act. Check matching phrases
        # before issuing this diagnostic.
        coordinated = True
    else:
        coordinated = False
    if text.startswith("Prove that ") and text.endswith(" using these premises."):
        if query is None:
            raise VEError("InvalidInput: query required")
        _sentence(env, text[len("Prove that "):-len(" using these premises.")] + ".", warnings)
        candidates = [(name, decl) for name, decl in env.predicates.items()
                      if decl.regulated is not None and decl.regulated.role == "obligation"
                      and decl.regulated.act == PROOF_TASK_ACT and decl.arguments[1:] == ("query",)]
        if len(candidates) != 1:
            raise VEError(f"MissingObligationRole: {PROOF_TASK_ACT}")
        return {"force": "require", "act": candidates[0][0], "args": [query], "guard": ["top"]}, "instruction"
    if text.endswith("."):
        plain = text[:-1]
        condition = None
        if ", if " in plain:
            plain, condition = plain.rsplit(", if ", 1)
        forbidden = plain.startswith("Do not ")
        if forbidden:
            plain = plain[len("Do not "):]
        matches = []
        wrong_role = []
        for phrase, predicate, args, role in _command_candidates(env, scope):
            if ascii_fold(plain) == ascii_fold(phrase):
                if role == ("permission" if forbidden else "obligation"):
                    matches.append((predicate, args, role))
                else:
                    wrong_role.append(predicate)
        matches = list(dict.fromkeys(matches))
        if len(matches) == 1:
            predicate, args, role = matches[0]
            if role != ("permission" if forbidden else "obligation"):
                raise VEError(f"Missing{'Permission' if forbidden else 'Obligation'}Role: {env.predicates[predicate].regulated.act}")
            guard = _to_data(_formula(env, condition + ".")) if condition else ["top"]
            return {"force": "forbid" if forbidden else "require", "act": predicate,
                    "args": list(args), "guard": guard}, "instruction"
        if len(matches) > 1:
            raise VEError("AmbiguousDerivation: multiple declared acts match")
        if wrong_role:
            raise VEError(f"Missing{'Permission' if forbidden else 'Obligation'}Role: {env.predicates[wrong_role[0]].regulated.act}")
    if coordinated:
        raise VEError("CoordinatedActs: split into two commands")
    raise VEError("InvalidInput: no single speech-act reading")
