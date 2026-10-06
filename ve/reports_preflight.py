"""Frozen public diagnostics before the reports document reaches Lean.

These shallow checks ran before reading choices in the original Python view.
They preserve that fault order; Lean remains the authority for document meaning.
"""
from __future__ import annotations

from copy import deepcopy

from .admission import token
from .errors import DuplicateDeclaration, ResourceLimit, UnsupportedProfile, VEError


def _records(rows, label):
    if type(rows) is not list:
        raise VEError(f"InvalidInput: {label} must be a list")
    if len(rows) > 256:
        raise ResourceLimit(f"ResourceLimit: {label}")
    result = {}
    for row in rows:
        if type(row) is not dict or not token(row.get("id")):
            raise VEError(f"InvalidInput: {label} record")
        if row["id"] in result:
            raise DuplicateDeclaration(f"DuplicateDeclaration: {label[:-1]} {row['id']}")
        result[row["id"]] = deepcopy(row)
    return result


def prepare(environment, contexts, assessments, bridges, scoped):
    """Return accepted record maps and metadata lists in the frozen fault order."""
    if "reports@0" not in environment.profiles or environment.reports is None:
        raise UnsupportedProfile("reports@0 needs a reports block")
    context_rows = _records(contexts, "contexts")
    assessment_rows = _records(assessments, "assessments")
    bridges, scoped = list(bridges), list(scoped)
    for label, rows in (("bridge", bridges), ("scoped", scoped)):
        ids = [row.get("id") if type(row) is dict else None for row in rows]
        duplicate = next((i for n, i in enumerate(ids) if i in ids[:n]), None)
        if duplicate is not None:
            raise DuplicateDeclaration(f"DuplicateDeclaration: {label} {duplicate}")
    if len(bridges) > 1000 or len(scoped) > 256:
        raise ResourceLimit("ResourceLimit: bridges or scoped")
    return context_rows, assessment_rows, bridges, scoped
