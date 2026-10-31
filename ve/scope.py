"""Lean's explanation of a `scope@0` document (docs/spec/scope.md 1.6, 2.3 and 5.3, SC-1c): the relay of the `scope`
service mode (`lean/VE/Scope/Run.lean`).

Lean decides which units are governed, which governors contribute to each, their reaches and the provenance sentences
(`VE/Scope/English.lean`). This module sends the document's text, relays Lean's rows and checks only what a relay
checks (DRI ruling R8): the answer's schema (the service checks `scope.json`) and its binding to the document it asked
about (`answer_problem`). It decides nothing and words nothing itself; the display prints each governed unit's source
text and Lean's sentences, and the unit and governor ids only in the provenance view (`--ids`).
"""
from __future__ import annotations

import json
from pathlib import Path

from .errors import CheckerUnavailable, VEError

MODE = "scope"
_CASE_ID = "scope"


def request(text: str) -> dict:
    return {"id": _CASE_ID, "document": text}


def _declared(meta) -> tuple[dict, dict]:
    """The document's unit spans by id and its governors by id, as its front matter writes them (first of each id)."""
    units, governors = {}, {}
    for unit in meta.get("units") or []:
        if type(unit) is dict and type(unit.get("id")) is str:
            units.setdefault(unit["id"], unit.get("span"))
    block = meta.get("scope")
    for governor in (block.get("governors") if type(block) is dict else None) or []:
        if type(governor) is dict and type(governor.get("id")) is str:
            governors.setdefault(governor["id"], governor)
    return units, governors


def _effect_key(effect) -> str | None:
    """The wire name of a governor's effect as written: the member of `{"frame": …}`, or the word itself."""
    if type(effect) is dict and len(effect) == 1:
        return next(iter(effect))
    return effect if type(effect) is str else None


def answer_problem(row, meta, case_id: str = _CASE_ID) -> str | None:
    """Why Lean's `scope` row is not an answer about the document `meta` (R8: its binding), or None. Rows follow the
    document's unit order, each unit once. Every governor a row names is one of the document's, once, with its unit,
    its effect and its recorded reach, which holds the row's unit (or, for `precedes`, its unit is the row's).
    `governed` is the document's governors in order, each with exactly the units whose rows name it."""
    if type(row) is not dict or set(row) != {"id", "status", "rows", "governed"} or row["id"] != case_id \
            or row["status"] != "ok" or type(row["rows"]) is not list or type(row["governed"]) is not list:
        return "the row is not an answer to the case"
    units, governors = _declared(meta)
    order = {u: i for i, u in enumerate(units)}
    listed, last = {}, -1
    for entry in row["rows"]:
        if type(entry) is not dict or set(entry) != {"unit", "governors"} or type(entry["governors"]) is not list:
            return "a row's fields are not unit and governors"
        unit = entry["unit"]
        if type(unit) is not str or unit not in order or order[unit] <= last or not entry["governors"]:
            return "a row names a unit outside the document, out of its order or twice, or no governor"
        last = order[unit]
        for x in entry["governors"]:
            governor = governors.get(x.get("id")) if type(x) is dict else None
            if governor is None or set(x) != {"id", "unit", "effect", "reach", "provenance"}:
                return f"{unit}: a governor is not one of the document's"
            if x["unit"] != governor.get("unit") or x["reach"] != governor.get("units"):
                return f"{unit}: governor {x['id']} is answered with another unit or reach"
            if type(x["effect"]) is not str or x["effect"].replace("-", "_") != _effect_key(governor.get("effect")):
                return f"{unit}: governor {x['id']} is answered with another effect"
            if unit not in x["reach"] and not (x["effect"] == "precedes" and x["unit"] == unit):
                return f"{unit}: governor {x['id']} does not reach the unit"
            if type(x["provenance"]) is not str or not x["provenance"]:
                return f"{unit}: governor {x['id']} has no sentence"
            if unit in listed.setdefault(x["id"], []):
                return f"{unit}: governor {x['id']} is named twice"
            listed[x["id"]].append(unit)
    expected = [{"id": g, "units": listed.get(g, [])} for g in governors]
    if row["governed"] != expected:
        return "governed is not the document's governors with the units whose rows name them"
    return None


def read_answer(row, case: dict) -> tuple[list[dict], dict, bytes]:
    """Lean's rows of the `ok` row `row` answering `case`, after the binding check (`answer_problem`), with the front
    matter and the source they are bound to."""
    from .document.source import _split
    try:
        meta, source, _ = _split(case["document"].encode("utf-8"))
    except VEError:
        meta, source = None, b""
    problem = answer_problem(row, meta, case.get("id")) if type(meta) is dict else "Lean answered a document Python cannot read"
    if problem is not None:
        raise CheckerUnavailable(f"CheckerUnavailable: Lean's scope answer is not bound to its document: {problem}")
    return row["rows"], meta, source


def explain(raw: bytes) -> tuple[list[dict], dict, bytes]:
    """`read_answer` of Lean's answer to the document `raw`; a refusal raises Lean's diagnostic, whatever Python
    reads of the document."""
    from .backends.relay import answer
    try:
        case = request(raw.decode("utf-8"))
    except UnicodeError:
        raise VEError("InvalidInput: the document is not UTF-8 text") from None  # relay-lint: file I/O
    row, error = answer(MODE, case)
    if error is not None:
        raise error
    return read_answer(row, case)


def lines(rows: list[dict], meta, source: bytes, *, ids: bool = False) -> list[str]:
    """The reader's view: each governed unit's source text, then Lean's sentences under *Where the parts come from:*,
    in the block's order of its governors; with `ids`, the unit and each governor's id, effect and reach (the
    provenance view)."""
    units, governors = _declared(meta)
    rank = {g: i for i, g in enumerate(governors)}
    out = []
    for entry in rows:
        span = units[entry["unit"]]
        text = source[span[0]:span[1]].decode("utf-8", "replace").strip() if type(span) is list and len(span) == 2 else ""
        named = sorted(entry["governors"], key=lambda x: rank[x["id"]])
        out.append(f"[{entry['unit']}] {text}" if ids else text)
        out.append("  Where the parts come from: " + " ".join(x["provenance"] for x in named))
        if ids:
            out.extend(f"    {x['id']} ({x['effect']}, {x['unit']} -> {', '.join(x['reach'])})" for x in named)
    return out


def main(argv: list[str]) -> int:
    """`ve scope explain FILE [--ids]`: Lean's explanation of a `scope@0` document. Exit 0 when Lean answered, 2 when
    it refused the document (its diagnostic), 4 at a resource limit; an unavailable checker is the caller's exit 5."""
    import argparse
    from .errors import ResourceLimit
    parser = argparse.ArgumentParser(prog="python -m ve scope")
    commands = parser.add_subparsers(dest="command", required=True)
    explaining = commands.add_parser("explain", help="each governed unit's governors and where its parts come from")
    explaining.add_argument("file", help="a ve-document@1 file listing scope@0")
    explaining.add_argument("--ids", action="store_true", help="the provenance view: unit and governor ids, reaches")
    options = parser.parse_args(argv)
    try:
        found, meta, source = explain(Path(options.file).read_bytes())
    except CheckerUnavailable:
        raise
    except (VEError, OSError) as exc:
        error = exc.to_dict() if isinstance(exc, VEError) else {"code": "InvalidInput", "message": str(exc)}
        print(json.dumps({"status": error["code"], "error": error}, ensure_ascii=False, indent=2))
        return 4 if isinstance(exc, ResourceLimit) else 2
    print("\n".join(lines(found, meta, source, ids=options.ids)))
    return 0
