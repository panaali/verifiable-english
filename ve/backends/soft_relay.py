"""Lean's soft route at the Python boundary."""
from __future__ import annotations

from copy import deepcopy

from ..errors import VEError
from .relay import decide, decide_once


def wire(value):
    """The restricted Lean wire spells optional null fields by omission."""
    if type(value) is dict:
        return {key: wire(item) for key, item in value.items() if item is not None}
    if type(value) is list:
        return [wire(item) for item in value]
    return value


def run(case):
    """Return a Lean soft row, retaining its diagnostic on a rejection."""
    try:
        if case.get("kind") in ("soft-elaborate", "soft-rule", "soft-rules"):
            # Both are pure source checks. Repeated rights correlation sends the
            # same large source and rules many times; keep Lean's bound answer,
            # and give each caller an independent display row.
            return deepcopy(decide_once("soft-norms", case))
        return decide("soft-norms", [case])[0]
    except VEError as error:
        if case.get("kind") in ("soft-elaborate", "admission"):
            diagnosed = decide("diagnose", [{**case, "unit": "soft-norms@0"}])[0]
            if diagnosed.get("outcome") == "fault":
                error.diagnostic = diagnosed["diagnostic"]
        raise
