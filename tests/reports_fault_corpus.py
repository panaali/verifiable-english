"""Malformed reports documents for the public `check_document` path (build checklist 2 and 5).

One rich, valid reports@0 document and its mutants: every JSON node of the reports front
matter (contexts, assessments, bridges, scoped) and of every report content tree replaced by
each of `7`, `true`, `null`, `[]`, `{}`, `"x"` and `""`; each object member deleted and an
extra member added; each list's first row duplicated; the limits at limit and limit + 1; and
two-fault pairs from different sections. The base recording
(`tests/data/reports_base_faults.json`, `docs/lean-first/b8/record_faults.py`) holds the
pre-batch Python's answer to each; `tests/test_reports_fault_order.py` compares Lean's.

This module imports nothing from `ve` at import time, so the recorder can run it against
another checkout's `ve`.
"""
from __future__ import annotations

import copy
import hashlib
import json
import random

SAFE = ["unary", "safe", ["const", "alice"]]
REVIEWED = ["unary", "reviewed", ["const", "service"]]
REPLACEMENTS = (("int", 7), ("true", True), ("null", None), ("list", []), ("object", {}), ("str", "x"),
                ("empty", ""))
SECTIONS = ("contexts", "assessments", "bridges", "scoped", "units")


def _report(inner, *, holder="article", act="says", context="c1", literal=None):
    node = {"holder": holder, "act": act, "context": context, "content": inner}
    if literal is not None:
        node["literal"] = literal
    return {"report": node}


def seed(language: str, revision: str) -> tuple[dict, str]:
    """The valid document (front matter, source text)."""
    environment = {
        "language": language, "profiles": ["documents@1", "relational-fol@0", "reports@0"],
        "spec_revision": revision,
        "vocabulary": {
            "reports": {"holders": ["person", "text"], "evidence": "evidence"},
            "sorts": {s: {"description": s} for s in ("person", "text", "evidence")},
            "predicates": {"safe": {"arguments": ["person"], "description": "safe"}},
            "constants": {"article": {"sort": "text", "description": "article"},
                          "alice": {"sort": "person", "description": "Alice"},
                          "e1": {"sort": "evidence", "description": "evidence"}},
        },
    }
    definitions = {
        "language": language, "profiles": ["definitions@0", "relational-fol@0"], "spec_revision": revision,
        "vocabulary": {"sorts": {"system": {"description": "system"}},
                       "predicates": {"reviewed": {"arguments": ["system"], "description": "reviewed"},
                                      "safe": {"arguments": ["system"], "description": "safe",
                                               "defined": {"arguments": ["system"],
                                                           "body": ["unary", "reviewed", ["var", 0]]}}},
                       "constants": {"service": {"sort": "system", "description": "service"}}}}
    norms = copy.deepcopy(environment)
    norms["profiles"] = ["norms@0", "relational-fol@0"]
    del norms["vocabulary"]["reports"]
    lines = [
        ("The article says that alice believes, \"Alice is safe\".\n",
         ["attributed", "article", "says", ["attributed", "alice", "believes", "asserted"]], "specified",
         _report(_report({"ast": SAFE}, holder="alice", act="believes", context="c2", literal="Alice is safe"))),
        ("According to the stated assessment, alice may be safe.\n", ["hedged", "could", "asserted"],
         {"open": ["reports__may__1"]},
         {"assessment": {"judgment": "may", "record": "a1", "content": {"ast": SAFE}}}),
        ("It is not the case that the article says that alice is safe.\n",
         ["attributed", "article", "says", "asserted"], "specified", {"negated": _report({"ast": SAFE})}),
        ("The article promised alice is safe.\n", ["attributed", "article", "promised", "asserted"],
         "specified", None),
        ("The article says the definition package.\n", ["attributed", "article", "says", "definition"],
         "specified", _report({"definition": {"environment": definitions, "content": {"ast": REVIEWED}}})),
        ("The article says the norms.\n", ["attributed", "article", "says", "norm"], "specified",
         _report({"norm": {"environment": norms, "norms": []}})),
    ]
    units, cursor = [], 0
    for index, (text, kind, meaning, content) in enumerate(lines, 1):
        size = len(text.encode())
        unit = {"id": f"u{index}", "span": [cursor, cursor + size], "kind": kind, "meaning": meaning,
                "support": "testimony"}
        if content is not None:
            unit["content"] = content
        units.append(unit)
        cursor += size
    meta = {
        "format": "ve-document@1", "environment": environment,
        "contexts": [{"id": "c1", "tense": "present", "reference_time": None, "description": "publication"},
                     {"id": "c2", "tense": "past", "reference_time": "t0", "description": "interview"}],
        "assessments": [{"id": "a1", "context": "e1", "decided_by": "unresolved_decider", "necessary": [SAFE],
                         "sufficient": [], "factors": ["review status"], "precedents": [],
                         "jurisdiction": "news_desk", "version": 1}],
        "units": units,
        "bridges": [{"id": "b1", "unit": "u1", "path": "1", "accepted_by": "reviewer", "reason": ["checked"]}],
        "scoped": [{"id": "s1", "payloads": [{"unit": "u1", "path": "1"}], "conclusion": {"ast": SAFE}},
                   {"id": "s2", "payloads": [{"unit": "u5", "path": "1"}],
                    "conclusion": {"ast": ["unary", "safe", ["const", "service"]]}}],
    }
    return meta, "".join(text for text, *_ in lines)


def _paths(value, path):
    yield path, value
    if type(value) is dict:
        for key, child in value.items():
            yield from _paths(child, path + (key,))
    elif type(value) is list:
        for index, child in enumerate(value):
            yield from _paths(child, path + (index,))


def _roots(meta):
    """The mutated subtrees: the front matter sections and each unit's content tree."""
    for key in ("contexts", "assessments", "bridges", "scoped"):
        yield (key,)
    for index, unit in enumerate(meta["units"]):
        if "content" in unit:
            yield ("units", index, "content")


def _get(meta, path):
    for step in path:
        meta = meta[step]
    return meta


def _set(meta, path, value):
    _get(meta, path[:-1])[path[-1]] = value


def _delete(meta, path):
    parent = _get(meta, path[:-1])
    if type(parent) is dict:
        del parent[path[-1]]
    else:
        parent.pop(path[-1])


def _label(path):
    return ".".join(str(step) for step in path) or "."


def single_faults(meta):
    """`(id, section, edit)` for every one-fault mutant; `edit(meta)` changes a copy in place."""
    faults = []
    for root in _roots(meta):
        for path, value in _paths(_get(meta, root), root):
            label = _label(path)
            for name, replacement in REPLACEMENTS:
                if value != replacement or type(value) is not type(replacement):
                    faults.append((f"{label}={name}", path[0],
                                   lambda m, p=path, r=replacement: _set(m, p, copy.deepcopy(r))))
            if len(path) > 1:
                faults.append((f"{label}=deleted", path[0], lambda m, p=path: _delete(m, p)))
            if type(value) is dict:
                faults.append((f"{label}+extra", path[0], lambda m, p=path: _get(m, p).update(extra=1)))
            if type(value) is list and value:
                faults.append((f"{label}+dup", path[0], lambda m, p=path: _get(m, p).append(_get(m, p)[0])))
    for key in ("contexts", "assessments", "bridges", "scoped"):
        faults.append((f"{key}=absent", key, lambda m, k=key: m.pop(k)))
    faults.extend(_limits(meta))
    return faults


def _renamed(rows, count):
    out = []
    for index in range(count):
        row = copy.deepcopy(rows[0])
        row["id"] = f"{row['id']}x{index}"
        out.append(row)
    return out


def _limits(meta):
    """Each count, byte and depth limit at the limit and one past it."""
    out = []
    for key, limit in (("contexts", 256), ("assessments", 256), ("bridges", 1000), ("scoped", 256)):
        for count in (limit, limit + 1):
            out.append((f"{key}*{count}", key,
                        lambda m, k=key, c=count: m[k].extend(_renamed(m[k], c - len(m[k])))))
    for count in (64, 65):
        out.append((f"scoped.0.payloads*{count}", "scoped",
                    lambda m, c=count: m["scoped"][0]["payloads"].extend(
                        [{"unit": "u1", "path": "1"}] * (c - 1))))
    for size in (200, 201):
        out.append((f"contexts.0.description bytes {size}", "contexts",
                    lambda m, s=size: m["contexts"][0].update(description="é" * (s // 2) + "a" * (s % 2))))
    for size in (4096, 4097):
        out.append((f"literal bytes {size}", "units",
                    lambda m, s=size: m["units"][0]["content"]["report"]["content"]["report"].update(
                        literal="é" * (s // 2) + "a" * (s % 2))))
    for depth in (16, 17):
        def deep(m, d=depth):
            node = {"ast": SAFE}
            for _ in range(d - 1):
                node = _report(node)
            m["units"][2]["content"] = {"negated": node}
            kind = "asserted"
            for _ in range(d - 1):
                kind = ["attributed", "article", "says", kind]
            m["units"][2]["kind"] = kind
        out.append((f"content depth {depth}", "units", deep))
    for depth in (64, 65):
        def nested(m, d=depth):
            formula = SAFE
            for _ in range(d - 1):
                formula = ["not", formula]
            m["assessments"][0]["necessary"] = [formula]
        out.append((f"formula depth {depth}", "assessments", nested))
    for name, value in (("unicode digit", "c١"), ("space", "c 1"), ("long", "c" * 65), ("nbsp", "c 1")):
        out.append((f"contexts.0.id {name}", "contexts",
                    lambda m, v=value: m["contexts"][0].update(id=v)))
    return out


def cases(language: str, revision: str, *, pairs: int = 400):
    """`(id, front matter, source)` for the seed, every single fault and `pairs` two-fault pairs."""
    meta, source = seed(language, revision)
    faults = single_faults(meta)
    out = [("seed", meta, source)]
    for fault_id, _section, edit in faults:
        changed = copy.deepcopy(meta)
        edit(changed)
        out.append((fault_id, changed, source))
    rng = random.Random(8)
    chosen = set()
    while len(chosen) < pairs:
        a, b = rng.sample(range(len(faults)), 2)
        if faults[a][1] != faults[b][1]:
            chosen.add((a, b))
    for a, b in sorted(chosen):
        changed = copy.deepcopy(meta)
        faults[a][2](changed)
        try:
            faults[b][2](changed)
        except (KeyError, IndexError, TypeError, AttributeError):
            continue  # the first fault removed the second's target
        out.append((f"{faults[a][0]} & {faults[b][0]}", changed, source))
    return out


def text(meta, source) -> str:
    return "---\n" + json.dumps(meta) + "\n---\n" + source


def digest(language: str, revision: str) -> str:
    """The corpus's identity: the recording is valid for exactly these documents."""
    h = hashlib.sha256()
    for case_id, meta, source in cases(language, revision):
        h.update(case_id.encode() + b"\0" + text(meta, source).encode() + b"\0")
    return h.hexdigest()


def outcome(check_document, path) -> str:
    """The public answer: `OK <status>`, or the exception's class and text."""
    try:
        return "OK " + str(check_document(path).get("status"))
    except Exception as exc:  # noqa: BLE001  (a crash is an answer too)
        return f"{type(exc).__name__}: {exc}"


# The public diagnostic classes (`ve/errors.py`); a base answer of any other class was a crash.
DIAGNOSTICS = frozenset(("VEError", "SyntaxError", "UnknownSymbol", "DuplicateDeclaration", "UnboundVariable",
                         "TypeMismatch", "UnsupportedProfile", "ResourceLimit"))
# The quoted packages' trees (units u5 and u6): their environments, norms and statements.
QUOTED = ("units.4.", "units.5.")
GROUPS = {
    "W8.1": "a Python AST decoder text carries its code: `SyntaxError: <text>`, `ResourceLimit: <text>`",
    "W8.2": "a quoted package's environment, norms or statement: the text of Lean's decoder",
    "O8.1": "`UnknownSymbol: evidence context <c>`: the same text, raised with its own code",
    "V8.1": "a pre-batch crash (`TypeError`) is now a diagnostic",
}


def _class(answer):
    return answer.split(":", 1)[0]


def _single_group(case_id, base, head):
    if _class(base) in ("SyntaxError", "ResourceLimit") and head == f"{_class(base)}: {base}":
        return "W8.1"
    if base.startswith("VEError: UnknownSymbol: evidence context ") and head == "UnknownSymbol: " + base[9:]:
        return "O8.1"
    if _class(base) not in DIAGNOSTICS and not base.startswith("OK") and _class(head) in DIAGNOSTICS:
        return "V8.1"
    if (case_id.startswith(QUOTED) and _class(base) in DIAGNOSTICS and _class(head) in DIAGNOSTICS
            and " & " not in case_id):
        return "W8.2"
    return None


def classify(base: dict, head: dict) -> dict:
    """Every difference between two recordings, by group; a pair whose answer is one of its
    faults' (on both sides) takes that fault's group, so order is checked too."""
    groups = {name: 0 for name in GROUPS}
    unlisted = []
    same = 0
    for case_id, before in base.items():
        after = head[case_id]
        if before == after:
            same += 1
            continue
        group = _single_group(case_id, before, after)
        if group is None and " & " in case_id:
            for part in case_id.split(" & "):
                if (base.get(part) == before and head.get(part) == after
                        and _single_group(part, before, after) == "W8.2"):
                    group = "W8.2"
        if group is None:
            unlisted.append(case_id)
        else:
            groups[group] += 1
    return {"documents": len(base), "same": same, "groups": groups, "unlisted": unlisted}
