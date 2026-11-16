"""The document mode's core path (kb-2a-b): Lean's answer for a document it lowers to its core documents
(`VE.Service.CoreCheck`), bound to the document sent and rendered. Python decides nothing here: the statuses, the core
statements and the kernel's rows are Lean's; this module checks that the answer is about the document sent and shows it.
"""
from __future__ import annotations

import json

from ..backends.lean_service import CheckerUnavailable
from ..environment import listed_profiles
from ..readings import active_reading_sets

# The front matter members the lowering has no row for (`CoreCheck.inputs`): no core answer has one.
UNLOWERED = ("couplings", "narrowings", "graph", "completions")
# The profiles the cases' environment drops (`Document.decodedEnvironment`: the document layers, then `lowerReadings`).
LOWERED = ("judgments@0", "readings@1")


def is_core(row) -> bool:
    """Whether a `document` row is the core path's answer (`view` and the kernel's `rows`)."""
    return type(row) is dict and "view" in row and "rows" in row


def _same(a, b) -> bool:
    return (json.dumps(a, sort_keys=True, ensure_ascii=False, allow_nan=False) ==
            json.dumps(b, sort_keys=True, ensure_ascii=False, allow_nan=False))


def _statements(unit: dict, sets: list, choice: list, terms: set) -> list:
    """The core statements the request gives a unit under a choice (`CoreDocument.UnitPlan.statements`), each as
    `(statement, written)`: its judgment declarations (the terms its `open` meaning lists that are open terms, in its
    order), then the body of the reading the choice takes in its active set, or else of its own content: a formula as a
    premise, a reading's rule as a strict norm, its own rule as a soft norm. `written` is the authored soft rule a
    statement's rule is bound to (`_soft_bound`), or None when the statement is the request's exactly."""
    listed = unit["meaning"].get("open", []) if type(unit.get("meaning")) is dict else []
    out = [({"feature": "judgments@0", "judgment": t}, None) for t in listed if t in terms]
    unit_set = next((s for s in sets if s["unit"] == unit["id"]), None)
    origin = {}
    if unit_set is not None:
        index = next(e["reading"] for e in choice if e["set"] == unit_set["id"])
        content = unit_set["readings"][index].get("content")
        origin = {"reading": {"set": unit_set["id"], "index": index}}
    else:
        content = unit.get("content")
    if content is None:
        return out
    if type(content) is dict and "ast" in content:
        return out + [({"feature": "facts", **origin, "premise": content["ast"]}, None)]
    if origin:
        return out + [({"feature": "norms@0", **origin, "rule": content}, None)]
    return out + [({"feature": "soft-norms@0", "rule": content}, content)]


def bind_core_answer(meta: dict, body: str, declared: list, row: dict) -> None:
    """R8 for the core answer: every id, choice, statement and row it names is the request's, and nothing is empty,
    missing, repeated or extra. The view's answer fields are bound as the plain answer's are (`_bind_document_answer`);
    the choices are exactly every choice of one reading per active set, in order; each unit's statements per choice
    are exactly the ones the request gives it (`_statements`: its judgment declarations, then its chosen reading's or
    its own content), and a unit has an entry exactly when it has a statement; each row's case is the core document of
    its choice (the written environment without `judgments@0` and `readings@1`, that choice's rules and premises in
    order) and its answer the kernel's admission of exactly that case. A row that is not is `CheckerUnavailable`."""
    from .lean import _bind_document_answer, _soft_bound

    def require(condition):
        if not condition:
            raise CheckerUnavailable("CheckerUnavailable: the Lean core document answer is not bound to the document "
                                     "sent")

    require(set(row) == {"id", "status", "view", "rows"} and type(row["view"]) is dict and type(row["rows"]) is list)
    view, rows = row["view"], row["rows"]
    try:
        _bind_document_answer(body, meta, declared, {"id": row["id"], "status": row["status"],
                                                      **{k: v for k, v in view.items()
                                                         if k not in ("choices", "statements")}})
    except (ValueError, KeyError, TypeError) as exc:
        raise CheckerUnavailable("CheckerUnavailable: the Lean core document answer is not bound to the document "
                                 "sent") from exc
    # The lowering refuses these members (`CoreCheck.inputs`: no row), so a core answer never has them.
    require(not any(key in meta for key in UNLOWERED))
    units = {u["id"]: u for u, _ in declared}
    sets = active_reading_sets(meta.get("reading_sets", []))
    # Every choice of one reading per active set, in the order of the sets, the first set's index slowest
    # (`CoreDocument.allChoices`); no coupling filters it (refused above).
    expected = [[]]
    for reading_set in sets:
        expected = [c + [{"set": reading_set["id"], "reading": i}] for c in expected
                    for i in range(len(reading_set["readings"]))]
    choices = view["choices"]
    require(type(choices) is list and len(rows) >= 1 and _same(choices, expected) and len(rows) == len(choices))
    terms = {t.get("name") for t in meta.get("open_terms", [])}
    entries = view["statements"]
    require(type(entries) is list)
    plan = [(u["id"], [_statements(u, sets, choice, terms) for choice in choices]) for u, _ in declared]
    plan = [(uid, per) for uid, per in plan if any(per)]
    require([e.get("id") for e in entries] == [uid for uid, _ in plan])
    norms = [[] for _ in choices]
    facts = [[] for _ in choices]
    for entry, (uid, per) in zip(entries, plan, strict=True):
        require(set(entry) == {"id", "choices"} and type(entry["choices"]) is list and
                len(entry["choices"]) == len(per))
        for k, (statements, wanted) in enumerate(zip(entry["choices"], per, strict=True)):
            require(type(statements) is list and len(statements) == len(wanted))
            for st, (want, written) in zip(statements, wanted, strict=True):
                if written is None:
                    require(_same(st, want))
                else:
                    # A soft rule of the unit's own content: in the form Lean's soft route holds it, as the plain
                    # answer's soft units are bound (`_soft_bound`, `Service.Document.softCanonical`).
                    require(type(st) is dict and set(st) == set(want) and _same(st["feature"], want["feature"]) and
                            _soft_bound(st["rule"], written, _same))
                if "premise" in st:
                    facts[k].append(st["premise"])
                elif "rule" in st:
                    norms[k].append(st["rule"])
    profiles = listed_profiles(meta.get("environment"))
    environment = {**meta["environment"], "profiles": [p for p in profiles if p not in LOWERED]}
    for k, r in enumerate(rows):
        require(set(r) == {"case", "answer"})
        case, answer = r["case"], r["answer"]
        require(_same(case, {"id": f"choice-{k}", "kind": "slot-admission", "environment": environment,
                             "norms": norms[k], "facts": facts[k]}))
        require(_same(answer, {"id": case["id"], "status": "ok", "rules": len(norms[k]), "facts": len(facts[k])}))


def core_report(row: dict) -> dict:
    """What `ve document check` prints for a core answer: per unit its status and its core statements per choice,
    the choices and each choice's kernel row, as Lean answered them."""
    view = row["view"]
    statements = {e["id"]: e["choices"] for e in view["statements"]}
    return {"format": "ve-document@1", "answered_by": "lean core document path",
            "source_id": view["source_id"], "document_id": view["document_id"], "coverage": view["coverage"],
            "choices": view["choices"],
            "units": [{"id": u["id"], "status": u["status"], "statements": statements.get(u["id"], [])}
                      for u in view["units"]],
            "rows": [{"choice": k, "answer": r["answer"]} for k, r in enumerate(row["rows"])],
            **({"judgment_lines": view["judgment_lines"]} if "judgment_lines" in view else {})}
