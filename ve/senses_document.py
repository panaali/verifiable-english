"""Senses in `ve document` (readings-defaults plan, section 6; batch RD-8): transport and display only.

A document whose front matter has `senses` sends its `surface: english` fences, in unit order, in one Lean
`senses.read` request with the packs, the own senses and the front matter's defaults (`read_fences`). Lean
reads each fence as one sentence, renders the defaults as preamble lines, and answers with each fence's unit
or preamble line (`VE.Senses.Document`). Python reads the pack files, hands each fence's unit Lean's formula
under Lean's projected environment, and relays Lean's refusals verbatim. It never reads a fence itself: the
English reader of other documents is bypassed here, not copied (relay lint, `PARSE_FREE`).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .environment import Environment
from .errors import VEError


@dataclass(frozen=True)
class SensesReading:
    """Lean's answer for a document's English fences."""
    environment: Environment
    # The formula AST of each fence whose unit Lean resolved, under `environment`.
    formulas: dict
    # Lean's English for each fence whose sentence has candidates (an unresolved word).
    unresolved: dict
    # The fences that are preamble lines.
    lines: frozenset
    reading: dict


def _pack(entry, directory: Path) -> bytes:
    """A bundled pack by name, or a pack file by a path relative to the document (one with a `/` or ending
    in `.json`)."""
    from .senses import bundled_pack, load_pack
    if type(entry) is not str:
        raise VEError("InvalidInput: a sense pack is named by a string")
    if "/" in entry or entry.endswith(".json"):
        return load_pack(directory / entry)
    return bundled_pack(entry)


def read_senses(env: Environment, senses, fences: list[tuple[str, str]], directory: Path,
                reading_set_units=frozenset()) -> SensesReading:
    """Lean's reading of `fences` (unit id and text, in unit order) under the front matter's `senses`. A
    fence whose sentence has candidates is admitted only when Lean finds its unit in the reading-set units."""
    from .backends.senses import read_fences
    if type(senses) is not dict or not set(senses) <= {"packs", "own", "defaults"} \
            or type(senses.get("packs", [])) is not list:
        raise VEError("InvalidInput: senses has packs, own and defaults only")
    packs = [_pack(entry, directory) for entry in senses.get("packs", [])]
    result = read_fences(env, [text for _, text in fences], packs, own=senses.get("own"),
                         defaults=senses.get("defaults"), fence_ids=[uid for uid, _ in fences],
                         reading_set_units=sorted(reading_set_units & {uid for uid, _ in fences}))
    reading = result["reading"]
    if reading["status"] not in ("one", "open"):
        if reading.get("code") == "Unresolved":
            raise VEError(reading["text"], diagnostic={"unit": reading["unit"], "code": reading["code"]})
        raise VEError(reading.get("text", reading["code"]), diagnostic=reading)
    formulas, unresolved, lines = {}, {}, set()
    for (uid, _), entry in zip(fences, reading["fences"], strict=True):
        if entry == "line":
            lines.add(uid)
            continue
        unit = reading["units"][entry]
        if "formula" in unit:
            formulas[uid] = unit["formula"]
        else:
            unresolved[uid] = unit["text"]
    return SensesReading(Environment(reading["environment"]), formulas, unresolved, frozenset(lines), reading)
