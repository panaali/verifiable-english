"""English surface of ``soft-norms@0``.

The W1 numbered-rule and completion prefixes are shared.  These records
describe the new continuations; :mod:`ve.norm_english` selects them only when
the soft profile is enabled.  No decision predicate is inferred from a word.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from ..norms import Norm, _to_data
from ..errors import SyntaxError
from .registry import SurfaceRecord, register


SOFT_PROFILE = "soft-norms@0"

# These are contextual productions under a W1 ``Rule`` block.  They have no
# statement-initial keyword, since registering ``Rule `` a second time would
# make dispatch ambiguous.
for tag, form, production in (
    ("soft-should", "should | should not", "default obligation | default prohibition"),
    ("soft-generally", "generally may | generally need not", "default permission | release"),
    ("soft-serves", "serves", "rule rank attribution"),
    ("soft-outranks", "outranks", "rank order edge"),
    ("soft-unranked", "are not ranked", "declared rank tie"),
    ("soft-excepted", "is excepted when | is excepted only when", "sufficient | necessary"),
    ("soft-factors", "takes account of", "exception factors"),
    ("soft-decider", "is decided by", "exception decider"),
    ("soft-header", "may turn off", "instruction switch in rule header"),
    ("soft-attribution", "records an instruction of", "legend party attribution"),
):
    register(SurfaceRecord(tag, form, (), form, production, profiles=(SOFT_PROFILE,)))

register(SurfaceRecord("soft-document-exceptions", "exception_decider",
                       ("Exceptions to rules in this document ",), "exception decider",
                       "document-level exception decider", profiles=(SOFT_PROFILE,)))
register(SurfaceRecord("soft-document-outranking", "outranking",
                       ("Outranking in this document ",), "outranking",
                       "strict | holistic flag", profiles=(SOFT_PROFILE,)))
register(SurfaceRecord("soft-rule-exception", "exception",
                       ("The exception to rule ",), "exception",
                       "decider | factors", profiles=(SOFT_PROFILE,)))


# Canonical deontic tokens, followed by the only input synonyms.  The latter
# are normalized to ``should`` on export.
DEFAULT_MODALS = {"should": ("obligation", True),
                  "should not": ("permission", False),
                  "generally may": ("permission", True),
                  "generally need not": ("obligation", False)}
SYNONYMS = {"generally must": "should", "generally must not": "should not"}
FREQUENCY_WORDS = ("normally", "typically", "usually", "as a rule")


def normalize_modal(modal: str) -> str:
    """Return one canonical default modal, rejecting unsupported permutations."""
    lowered = modal.casefold()
    if lowered in ("should generally", "should generally not"):
        raise SyntaxError("should generally has no authoring reading; use should or generally may")
    return SYNONYMS.get(lowered, lowered)


def modal_reading(modal: str):
    """Return ``(mode, role, sign)`` for a surface deontic token."""
    canonical = normalize_modal(modal)
    if canonical in DEFAULT_MODALS:
        role, sign = DEFAULT_MODALS[canonical]
        return "default", role, sign
    strict = {"must": ("obligation", True), "need not": ("obligation", False),
              "may": ("permission", True), "must not": ("permission", False)}
    if canonical in strict:
        role, sign = strict[canonical]
        return "strict", role, sign
    raise SyntaxError(f"No single deontic reading for {modal!r}")


def frequency_readings(word: str, act: str) -> tuple[str, str]:
    """Two English paraphrases for an unresolved frequency expression.

    These are shown to the author; the word is never silently accepted as a
    default-rule synonym.
    """
    if word.casefold() not in FREQUENCY_WORDS:
        raise SyntaxError(f"Unknown frequency expression {word!r}")
    return (f"A defeasible rule requires {act} unless its named exception applies.",
            f"{act.capitalize()} occurs in most relevant situations; this is a frequency claim.")


def rule_paraphrase(number: int | str, mode: str, *, role: str = "obligation",
                    sign: bool = True, decider: str | None = None,
                    alterable=(), rank: str | None = None) -> str:
    """The fixed, one-reading explanation displayed beside a rule."""
    if mode == "default":
        effect = ("required" if sign else "not required") if role == "obligation" else (
            "permitted" if sign else "not permitted")
        who = (f"{decider} decides whether it applies" if decider and decider != "unstated"
               else "the source names no decider")
        main = (f"Rule {number} makes the act {effect} unless its named exception applies here; "
                f"{who}.")
    elif mode == "strict":
        main = f"Rule {number} has no exception decision."
    else:
        raise SyntaxError(f"Unknown rule mode {mode!r}")
    if alterable:
        main += " " + ", ".join(alterable) + " may turn it off for this situation."
    elif mode == "strict":
        main += " No instruction switch exists; only a strict exception rule written in this document can override it."
    if rank:
        main += (f" It serves {rank} where default rules collide." if mode == "default" else
                 f" It records rank {rank}, but a strict rule is never weighed.")
    if mode == "default":
        main += (" It gives way to strict decisions and to higher-ranked effective opponents "
                 "unless holistically outweighed; a lower-ranked opponent that the decider "
                 "finds outweighs it need only be eligible.")
    return main


_PARTIES = re.compile(r"([a-z][a-z0-9_]*)(?: and ([a-z][a-z0-9_]*))? may turn off\Z")


def parse_header_options(source: str) -> tuple[tuple[int, ...], tuple[str, ...]]:
    """Decode author precedence and party switches from a header's parentheses.

    A caller checks the referenced rule numbers and declared party names.
    """
    if not source:
        return (), ()
    pieces = source.split("; ")
    if len(pieces) > 2:
        raise SyntaxError("Rule header has too many options")
    refs: tuple[int, ...] = ()
    parties: tuple[str, ...] = ()
    for piece in pieces:
        match = re.fullmatch(r"exception to rules? ([1-9][0-9]*(?:, [1-9][0-9]*)*(?: and [1-9][0-9]*)?)", piece)
        if match:
            if refs:
                raise SyntaxError("Duplicate precedence option")
            refs = tuple(int(n) for n in re.findall(r"[1-9][0-9]*", match[1]))
            continue
        match = _PARTIES.fullmatch(piece)
        if match:
            if parties:
                raise SyntaxError("Duplicate instruction switch option")
            parties = tuple(x for x in match.groups() if x)
            if len(set(parties)) != len(parties):
                raise SyntaxError("Duplicate instruction party")
            continue
        raise SyntaxError(f"Unknown rule header option {piece!r}")
    return refs, parties


def render_header_options(refs: tuple[int, ...], parties: tuple[str, ...]) -> str:
    parts = []
    if refs:
        parts.append("exception to rule" + ("s" if len(refs) > 1 else "") + " " +
                     (str(refs[0]) if len(refs) == 1 else
                      ", ".join(map(str, refs[:-1])) + " and " + str(refs[-1])))
    if parties:
        parts.append(" and ".join(parties) + " may turn off")
    return " (" + "; ".join(parts) + ")" if parts else ""


_IDENT = r"[a-z][a-z0-9_]*"


def parse_declaration(sentence: str) -> tuple[str, object]:
    """Read one environment legend or rank sentence without changing ``E``.

    The resulting value is compared with the identity-bound environment by
    the environment editor.  A rank name is lowercased only at the displayed
    initial capital; identifiers elsewhere retain their exact spelling.
    """
    m = re.fullmatch(rf"([A-Z][a-z0-9_]*) outranks ({_IDENT})\.", sentence)
    if m:
        return "outranks", (m[1].lower(), m[2])
    m = re.fullmatch(rf"([A-Z][a-z0-9_]*) and ({_IDENT}) are not ranked\.", sentence)
    if m:
        return "tie", (m[1].lower(), m[2])
    if sentence == "Outranking in this document is strict.":
        return "outranking", {"mode": "strict"}
    m = re.fullmatch(
        r"Outranking in this document is holistic; ([^.]+) decides when a "
        r"lower-ranked rule outweighs a higher-ranked one in a situation\.", sentence)
    if m:
        return "outranking", {"mode": "holistic", "decided_by": m[1]}
    m = re.fullmatch(
        r"Exceptions to rules in this document are decided by ([^.]+), "
        r"unless a rule says otherwise\.", sentence)
    if m:
        return "exception_decider", m[1]
    m = re.fullmatch(r'"(.+) records an instruction of (' + _IDENT + r')\."', sentence)
    if m:
        return "instruction_of", (m[1], m[2])
    raise SyntaxError(f"No single soft declaration reading for {sentence!r}")


def render_declaration(kind: str, value: object) -> str:
    if kind == "outranks":
        high, low = value
        return f"{high.capitalize()} outranks {low}."
    if kind == "tie":
        left, right = value
        return f"{left.capitalize()} and {right} are not ranked."
    if kind == "outranking":
        if value["mode"] == "strict":
            return "Outranking in this document is strict."
        if value["mode"] == "holistic":
            return ("Outranking in this document is holistic; " + value["decided_by"] +
                    " decides when a lower-ranked rule outweighs a higher-ranked one in a situation.")
    if kind == "exception_decider":
        return f"Exceptions to rules in this document are decided by {value}, unless a rule says otherwise."
    if kind == "instruction_of":
        verbalisation, party = value
        return f'"{verbalisation} records an instruction of {party}."'
    raise SyntaxError(f"Unknown soft declaration {kind!r}")


@dataclass(frozen=True, slots=True)
class SoftNorm(Norm):
    """Surface value for a norm with the item-2 extension fields.

    It remains a ``Norm`` so the existing numbered-rule constructor and
    manifest can carry it.  Item 2 owns validation and elaboration of these
    fields; this value only preserves the authored reading and identity.
    """
    mode: str = "strict"
    rank: str | None = None
    alterable: tuple[str, ...] = ()
    decided_by: str | None = None
    sufficient: tuple[object, ...] = ()
    necessary: tuple[object, ...] = ()
    factors: tuple[str, ...] = ()
    hard: bool = False

    def to_dict(self):
        data = Norm.to_dict(self)
        raw = data["norm"]
        if self.mode != "strict":
            raw["mode"] = self.mode
            raw["exception"] = {"sufficient": [_to_data(x) for x in self.sufficient],
                                "necessary": [_to_data(x) for x in self.necessary],
                                "factors": list(self.factors)}
            if self.decided_by is not None:
                raw["exception"]["decided_by"] = self.decided_by
        if self.rank is not None:
            raw["rank"] = self.rank
        if self.alterable:
            raw["alterable"] = list(self.alterable)
        if self.hard:
            raw["hard"] = True
        return data
