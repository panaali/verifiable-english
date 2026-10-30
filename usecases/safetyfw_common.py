"""Shared, source-free mechanics for the frontier-framework case studies.

The individual cases own their vocabulary, source anchors and feature decisions.
This module only loads the existing FSF helpers and aggregates saved measurements.
"""
from __future__ import annotations

import importlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def safety_framework(*module_names):
    """Load FSF modules without leaving their bare sibling names in sys.modules."""
    names = ("vocabulary", "translation", "build_document", "measure_r1")
    saved = {name: sys.modules.pop(name) for name in names if name in sys.modules}
    sys.path.insert(0, str(ROOT / "safety-framework"))
    try:
        return {name: importlib.import_module(name) for name in module_names}
    finally:
        sys.path.pop(0)
        for name in names:
            sys.modules.pop(name, None)
        sys.modules.update(saved)


FAMILIES = ("JT", "DF", "SC", "QT", "ET", "AP", "WG", "AT", "external reference", "readings",
            "no claim to check")


def measure_units(spans_path: Path, coverage_path: Path, blockers):
    """The common shape of units.json and gaps.json, with case-owned blockers."""
    spans = json.loads(spans_path.read_text())["units"]
    units = [{"id": r["id"], "bytes": r["span"][1] - r["span"][0], "status": r["status"],
              "kind": r["kind"], "blockers": blockers(r),
              **({"reason": r["reason"]} if "reason" in r else {}),
              **({"reading_set": r["reading_set"]} if "reading_set" in r else {})} for r in spans]
    statuses, features = {}, {}
    for unit in units:
        statuses[unit["status"]] = statuses.get(unit["status"], 0) + unit["bytes"]
        for family in unit["blockers"]:
            entry = features.setdefault(family, {"units": 0, "bytes": 0, "sole_units": 0, "sole_bytes": 0,
                                                 "statuses": {}})
            entry["units"] += 1
            entry["bytes"] += unit["bytes"]
            entry["statuses"][unit["status"]] = entry["statuses"].get(unit["status"], 0) + unit["bytes"]
            if len(unit["blockers"]) == 1:
                entry["sole_units"] += 1
                entry["sole_bytes"] += unit["bytes"]
    coverage = json.loads(coverage_path.read_text())
    gaps = {"source_bytes": coverage["source_bytes"], "master_bytes_by_status": coverage["master_bytes_by_status"],
            "d1_bytes_by_status": coverage["bytes_by_status"], "status_bytes_recomputed": statuses,
            "units": len(units), "features": dict(sorted(features.items(), key=lambda kv: (-kv[1]["bytes"], kv[0])))}
    return {"units": units}, gaps


def part_document(document: bytes, records, source: bytes, uids, profiles=None):
    """Retain chosen source units and rebase their spans for a stage-0 probe."""
    front = json.loads(document[4:document.index(b"\n---\n")])
    keep = {r["id"]: r for r in records if r["id"] in uids}
    units, body, cursor = [], b"", 0
    for unit in front["units"]:
        if unit["id"] in keep:
            a, b = unit["span"]
            units.append({**unit, "span": [cursor, cursor + b - a]})
            body += source[a:b]
            cursor += b - a
    terms = {t for r in keep.values() for t in r.get("open_terms", [])}
    env = front["environment"] if profiles is None else {**front["environment"], "profiles": profiles}
    trimmed = {"format": "ve-document@1", "environment": env, "units": units,
               "open_terms": [t for t in front["open_terms"] if t["name"] in terms],
               "reading_sets": [s for s in front["reading_sets"] if s["unit"] in keep]}
    return b"---\n" + json.dumps(trimmed, indent=1, ensure_ascii=False).encode() + b"\n---\n" + body


def ve_check(document: bytes):
    """Return VE's part-document result, including refusals as data for a probe."""
    from ve.document import check_document, load_document
    from ve.errors import VEError
    with tempfile.TemporaryDirectory() as scratch:
        path = Path(scratch) / "part.ve.md"
        path.write_bytes(document)
        try:
            units = load_document(path)["units"]
            report = check_document(path)
        except VEError as exc:
            return {"admitted": False, "diagnostic": f"{type(exc).__name__}: {exc}"}
    readings = report.get("readings") or {}
    return {"admitted": True, "units": {u["id"]: u["status"] for u in units},
            "route": readings.get("route"), "premises": report["premises"]["status"],
            "unresolved_reading_sets": report["coverage"]["residual"]["unresolved_reading_sets"]}


def lean_document(document: bytes):
    from ve.backends.relay import answer
    row, error = answer("document", {"id": "d", "document": document.decode(), "admit": True})
    if error is not None:
        return {"admitted": False, "diagnostic": str(error)}
    return {"admitted": True, "units": {u["id"]: u["status"] for u in row["units"]}}
