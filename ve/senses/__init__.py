"""Sense pack transport and review provenance.

The Lean senses decoder owns the pack schema, dictionary identity and every
reading decision. Keep the source bytes intact on the way to that decoder.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

from ..errors import VEError
from ..wire import loads_json


def load_pack(path: str | Path) -> bytes:
    """Read a pack without interpreting or normalizing its JSON."""
    try:
        return Path(path).read_bytes()
    except (OSError, TypeError, ValueError) as exc:
        raise VEError(f"Cannot read sense pack: {exc}") from exc


def bundled_pack(name: str) -> bytes:
    """Read a bundled pack by its exact file name."""
    if (type(name) is not str or not name or name in {".", ".."}
            or any(char in name for char in ("/", "\\", "\x00"))):
        raise VEError("Invalid sense pack name")
    try:
        return files("ve.senses").joinpath("packs", name + ".json").read_bytes()
    except (OSError, UnicodeError, ValueError) as exc:
        raise VEError(f"Cannot read sense pack: {exc}") from exc


def review_status(name: str, dictionary_id: str) -> str:
    """Display metadata only; `dictionary_id` must come from Lean.

    A missing or malformed review file fails closed without changing admission.
    """
    try:
        records = loads_json(files("ve.senses").joinpath("reviewed-packs.json").read_bytes())
        if type(records) is not list:
            return "unreviewed"
        for record in records:
            if (type(record) is dict and record.get("name") == name
                    and record.get("dictionary_id") == dictionary_id
                    and all(type(record.get(key)) is str and record[key]
                            for key in ("reviewer", "date", "scope"))):
                return "reviewed"
    except (OSError, VEError):
        pass
    return "unreviewed"
