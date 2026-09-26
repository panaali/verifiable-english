"""Gatekeeper image exemption on a finite, recorded input domain."""
from __future__ import annotations

from dataclasses import dataclass

from ..errors import VEError
from .records import _lookup_verified, run, verify


@dataclass(frozen=True, slots=True)
class Exemption:
    value: bool | None
    labels: tuple[str, ...]


def tables(patterns: list[str], images: list[str]) -> tuple[dict, ...]:
    """Build one complete glob table per exemption pattern."""
    return tuple(run("glob@1", {"pattern": pattern}, images) for pattern in patterns)


def is_exempt(image: str, patterns: list[str], records: tuple[dict | None, ...] | None) -> Exemption:
    """Return UNKNOWN if any required table is absent and no table matches."""
    if records is None:
        return Exemption(False if not patterns else None, ())
    if len(records) != len(patterns):
        raise VEError("Exemption table count does not match pattern count")
    found, missing, labels = False, False, []
    for pattern, record in zip(patterns, records, strict=True):
        if record is None:
            missing = True
            continue
        checked = verify(record)
        if checked["function"] != "glob@1" or checked["parameters"] != {"pattern": pattern}:
            raise VEError("Exemption table is bound to a different glob pattern")
        found |= _lookup_verified(checked, image)
        labels.append(checked["label"])
    return Exemption(True if found else None if missing else False, tuple(labels))
