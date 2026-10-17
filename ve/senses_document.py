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


def names_file(entry) -> bool:
    """Whether a `senses.packs` entry names a pack file by a path relative to the document (one with a `/` or ending
    in `.json`), not a bundled pack. Every reader that moves a document reads its files by this rule."""
    return type(entry) is str and ("/" in entry or entry.endswith(".json"))


def pack_files(meta) -> list[str]:
    """The pack files a front matter's `senses` names, relative to the document, in order."""
    senses = meta.get("senses") if type(meta) is dict else None
    packs = senses.get("packs") if type(senses) is dict else None
    return [entry for entry in packs if names_file(entry)] if type(packs) is list else []


def _pack(entry, directory: Path) -> bytes:
    """A bundled pack by name, or a pack file by a path relative to the document (`names_file`)."""
    from .senses import bundled_pack, load_pack
    if type(entry) is not str:
        raise VEError("InvalidInput: a sense pack is named by a string")
    if names_file(entry):
        return load_pack(directory / entry)
    return bundled_pack(entry)


def pack_texts(senses, directory: Path) -> list[str] | None:
    """The texts of a document's packs, one per `senses.packs` entry, which Lean's `document` mode hands the senses
    route (`Service.Document.sensesLayer`, batch 16f): reading the files is Python's. None when `senses` or its
    packs are malformed or a pack cannot be read: the mode then answers `CheckerUnavailable`, and the loader reports
    that fault in its own order."""
    from .backends.senses import pack_text
    if type(senses) is not dict or type(senses.get("packs", [])) is not list:
        return None
    try:
        return [pack_text(_pack(entry, directory)) for entry in senses.get("packs", [])]
    except VEError:
        return None


def covered_units(reading_sets) -> set[str]:
    """The fence units the front matter's `reading_sets` name. The reading sets are untrusted and not yet
    checked: an entry or unit of any other shape names nothing here, and the readings checks refuse it."""
    if type(reading_sets) is not list:
        return set()
    return {r["unit"] for r in reading_sets if type(r) is dict and type(r.get("unit")) is str}


def read_senses(env: Environment, senses, fences: list[tuple[str, str]], directory: Path,
                reading_sets=()) -> SensesReading:
    """Lean's reading of `fences` (unit id and text, in unit order) under the front matter's `senses`. A
    fence whose sentence has candidates is admitted only when Lean finds its unit among the units of the
    front matter's `reading_sets` (`covered_units`)."""
    from .backends.senses import read_fences
    if type(senses) is not dict or not set(senses) <= {"packs", "own", "defaults"} \
            or type(senses.get("packs", [])) is not list:
        raise VEError("InvalidInput: senses has packs, own and defaults only")
    packs = [_pack(entry, directory) for entry in senses.get("packs", [])]
    ids = [uid for uid, _ in fences]
    result = read_fences(env, [text for _, text in fences], packs, own=senses.get("own"),
                         defaults=senses.get("defaults"), fence_ids=ids,
                         reading_set_units=sorted(covered_units(reading_sets) & set(ids)))
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
