"""The document mode's core path (kb-2a-b): Lean's answer for a document it lowers to its core documents
(`VE.Service.CoreCheck`), bound to the document sent and rendered. Python decides nothing here: the statuses, the core
statements and the kernel's rows are Lean's; this module checks that the answer is about the document sent and shows it.
"""
from __future__ import annotations

import json

from ..backends.lean_service import CheckerUnavailable
from ..environment import listed_profiles
from ..readings import active_reading_sets

# The features a core statement's origin names (`CoreDocument.lowerContent`, `declarations`).
FEATURES = ("facts", "soft-norms@0", "norms@0", "judgments@0")
# The profiles the cases' environment drops (`Document.decodedEnvironment`: the document layers, then `lowerReadings`).
LOWERED = ("judgments@0", "readings@1")


def is_core(row) -> bool:
    """Whether a `document` row is the core path's answer (`view` and the kernel's `rows`)."""
    return type(row) is dict and "view" in row and "rows" in row


def _same(a, b) -> bool:
    return (json.dumps(a, sort_keys=True, ensure_ascii=False, allow_nan=False) ==
            json.dumps(b, sort_keys=True, ensure_ascii=False, allow_nan=False))


def bind_core_answer(meta: dict, body: str, declared: list, row: dict) -> None:
    """R8 for the core answer: every id, choice, statement and row it names is the request's, and nothing is empty or
    extra. The view's answer fields are bound as the plain answer's are (`_bind_document_answer`); the choices name
    the active reading sets and an index inside each; each unit's statements are its own content, its reading's
    content, or a judgment term its meaning lists; each row's case is the core document of its choice (the written
    environment without `judgments@0` and `readings@1`, that choice's rules and premises in order) and its answer the
    kernel's admission of exactly that case. A row that is not is `CheckerUnavailable`."""
    from .lean import _bind_document_answer

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
    units = {u["id"]: u for u, _ in declared}
    sets = {s["id"]: s for s in active_reading_sets(meta.get("reading_sets", []))}
    choices = view["choices"]
    require(len(choices) == len(rows) >= 1 and len({json.dumps(c, sort_keys=True) for c in choices}) == len(choices))
    for choice in choices:
        require(sorted(e["set"] for e in choice) == sorted(sets) and
                all(e["reading"] < len(sets[e["set"]]["readings"]) for e in choice))
    terms = {t.get("name") for t in meta.get("open_terms", [])}
    order = [u["id"] for u, _ in declared]
    entries = view["statements"]
    ids = [e["id"] for e in entries]
    require(len(set(ids)) == len(ids) and all(i in units for i in ids) and
            ids == [i for i in order if i in ids] and
            all(i in ids for i, u in units.items() if u.get("content") is not None))
    norms = [[] for _ in choices]
    facts = [[] for _ in choices]
    for entry in entries:
        unit = units[entry["id"]]
        require(len(entry["choices"]) == len(choices))
        unit_set = next((s for s in sets.values() if s["unit"] == entry["id"]), None)
        listed = unit["meaning"].get("open", []) if type(unit["meaning"]) is dict else []
        for k, statements in enumerate(entry["choices"]):
            for st in statements:
                require(st["feature"] in FEATURES)
                reading = st.get("reading")
                if reading is not None:
                    require(unit_set is not None and reading["set"] == unit_set["id"] and
                            {"set": reading["set"], "reading": reading["index"]} in choices[k])
                    source = unit_set["readings"][reading["index"]].get("content")
                else:
                    source = unit.get("content")
                if "judgment" in st:
                    require(reading is None and st["feature"] == "judgments@0" and st["judgment"] in terms and
                            st["judgment"] in listed)
                elif "premise" in st:
                    require(st["feature"] == "facts" and type(source) is dict and _same(st["premise"], source.get("ast")))
                    facts[k].append(st["premise"])
                else:
                    require(st["feature"] != "facts" and _same(st["rule"], source))
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
