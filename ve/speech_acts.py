"""Speech wording helpers retained for the Python English parser until E3.

Speech document acceptance and semantic decisions are owned by the Lean route.
"""
from __future__ import annotations

import re

from .errors import ResourceLimit, VEError

_TOKEN = re.compile(r"[A-Za-z0-9_.-]{1,64}\Z", re.ASCII)

_PHRASE = re.compile(r"the [A-Za-z][A-Za-z'-]*(?: [A-Za-z][A-Za-z'-]*)*\Z", re.ASCII)

PROOF_TASK_ACT = "{0} submit a proof of {1}"

def parse_scope(raw):
    """The block's structure, as Lean's `parseScope`, which the speech route
    reads before the envelope: an object of `task`, `addressee` and
    `definites`, with string names and definite phrases in normal form."""
    block = VEError("InvalidInput: speech_acts block")
    if type(raw) is not dict or "task" not in raw or set(raw) - {"task", "addressee", "definites"}:
        raise block
    if type(raw["task"]) is not str:
        raise block
    addressee = raw.get("addressee")
    if "addressee" in raw and (type(addressee) is not dict or set(addressee) != {"sort", "constant"}
                               or any(type(v) is not str for v in addressee.values())):
        raise block
    definites = raw.get("definites", {})
    if type(definites) is not dict or any(type(c) is not str for c in definites.values()):
        raise block
    for phrase in definites:
        if type(phrase) is not str or len(phrase.encode()) > 80 or not _PHRASE.fullmatch(phrase):
            raise block

def validate_scope(raw, sorts, constants, predicates):
    """Validate the identity-bound task legend without changing old environments.

    Every reference is first a name (a string), with the block's structure and
    phrase checks, and only then resolved, in the order of Lean's `parseScope`,
    `checkPhrases` and `checkSpeech`: a mistyped sort or constant is a block
    error, never an `UnknownSymbol` or a crash.
    """
    block = VEError("InvalidInput: speech_acts block")
    parse_scope(raw)
    if not _TOKEN.fullmatch(raw["task"]):
        raise block
    result = {"task": raw["task"]}
    addressee = raw.get("addressee")
    definites = raw.get("definites", {})
    normalized = {}
    for phrase, constant in definites.items():
        key = " ".join(phrase.split())
        if key in normalized or key in constants or key in sorts or key.lower() in {
                "true", "false", "is", "equals", "not", "and", "or", "if", "then", "for",
                "every", "there", "exists", "believes", "must", "eventually"}:
            raise block
        normalized[key] = constant
    check_templates(predicates)
    if addressee is not None:
        sort, constant = addressee["sort"], addressee["constant"]
        if sort not in sorts:
            raise VEError(f"UnknownSymbol: sort {sort}")
        if constant not in constants or constants[constant].sort != sort:
            raise VEError(f"UnknownSymbol: {constant}")
        result["addressee"] = dict(addressee)
    if len(definites) > 64:
        raise ResourceLimit("definites")
    for constant in normalized.values():
        if constant not in constants:
            raise VEError(f"UnknownSymbol: {constant}")
    if normalized:  # canonical as Lean's `encodeScope`: an empty map is absent
        result["definites"] = normalized
    return result

ATTACHED_SLOT = "InvalidInput: speech template slot must stand apart"

_SLOT = re.compile(r"\{[0-9]+\}")

def _attached(c):
    """A character that joins a slot to its word: not ASCII whitespace, and a `{`, `}` or no `_WORD_BREAK`."""
    return c not in _SURFACE_SPACES and (c in "{}" or c not in _WORD_BREAK)

def check_templates(predicates):
    """3.1: every slot of an act or verbalisation template stands apart from its words, as Lean's `checkTemplates`.

    A slot `{n}` begins the template or follows ASCII whitespace or a word break
    (`_WORD_BREAK`, but not a brace), and ends it or precedes one, so "{0} click
    {1}" and "{0} is ({1})" pass and "{0} click{1}", "click-{1}", "click'{1}" and
    "pre{1}post" are `ATTACHED_SLOT`: a filled slot never makes a new word.
    Acts are W1's normalised phrases; verbalisations are read as declared.
    """
    for decl in predicates.values():
        templates = (decl.verbalisation, decl.negative_verbalisation,
                     decl.regulated.act if decl.regulated is not None else None)
        for template in templates:
            for slot in _SLOT.finditer(template or ""):
                start, end = slot.span()
                if ((start > 0 and _attached(template[start - 1]))
                        or (end < len(template) and _attached(template[end]))):
                    raise VEError(ATTACHED_SLOT)

_SURFACE_SPACES = " \t\n\r\x0b\x0c"

_SURFACE_SPACE = re.compile(f"[{_SURFACE_SPACES}]+")

_SURFACE_FOLD = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")

_WORD_BREAK = frozenset(" !\"#$%&()*+,./:;<=>?@[\\]^`{|}~")

def surface_words(text):
    """The one normalisation of a wording and an act phrase for `surface_kind` (3.2), as Lean's `surfaceWords`.

    ASCII only: the six ASCII whitespace characters of Python's `string.whitespace`
    separate words (runs collapse to one space, none leads or trails) and only
    `A`-`Z` fold to `a`-`z`.  Every other character, Unicode whitespace and
    control characters included, is an ordinary letter.
    """
    return " ".join(w for w in _SURFACE_SPACE.split(text) if w).translate(_SURFACE_FOLD)

NON_ASCII_WORDING = "InvalidInput: non-ASCII speech wording"

def ascii_wording(text):
    """3.2: a speech-act wording is ASCII only, as Lean's `asciiWording`; any other character is `NON_ASCII_WORDING`.

    Checked before a wording is classified or read, so no reader (the surface
    kind, the speech parser, P0's English for an embedded formula) sees a
    character another reader would normalise differently.
    """
    if not text.isascii():
        raise VEError(NON_ASCII_WORDING)
    return text

def wording_text(text):
    """A unit's ASCII wording (`ascii_wording`) without leading or trailing ASCII whitespace.

    Every reader of a wording (the source wrapper's span and fence, the speech
    parser) trims with this, so no path sees a different sentence.
    """
    return ascii_wording(text).strip(_SURFACE_SPACES)

def ascii_fold(text):
    """`A`-`Z` folded to `a`-`z` and nothing else, the case rule of `surface_words`."""
    return text.translate(_SURFACE_FOLD)

def act_verb(act):
    """The first word after `{0}` of an act phrase, normalised as `surface_words`, or None when it is a slot.

    An imperative wording begins with this word (3.2), so only an act with one is
    read as a command by the speech parser or classifies a wording, as Lean's `actVerb`.
    """
    words = surface_words(act).split(" ")
    return words[1] if len(words) > 1 and words[0] == "{0}" and not words[1].startswith("{") else None
