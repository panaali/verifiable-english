"""Source prose for an assist session: sentences, roles, and frozen target slots.

A source is plain data: an ordered list of sentences, each with a stable id, a
role, and an ``asserting`` flag. Roles:

* ``given``   - the prose states it as a premise; an assumption may anchor here.
* ``claimed`` - the prose asserts it as a conclusion; it must be derived.
* ``context`` - neither (headings, commentary); never needs coverage.

Untagged prose defaults to ``claimed``, never ``given``: intermediate conclusions
must not become anchors for assumptions by default. Tag premise paragraphs
``[given]`` (or give each JSON sentence an explicit ``role``).

Nothing here interprets meaning. Sentence splitting is a deterministic regex.
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path
import re

from ..environment import RESERVED, valid_identifier
from ..errors import VEError

ROLES = ("given", "claimed", "context")
_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])")
_TAG = re.compile(r"\[(given|claimed|context)\]\s*", re.I)


def split_sentences(text):
    """Deterministic sentence split on terminal punctuation followed by a capital."""
    return [part.strip() for part in _SPLIT.split(" ".join(text.split())) if part.strip()]


def _sentence(sid, text, role, block, asserting=True):
    if role not in ROLES:
        raise VEError(f"Unknown sentence role: {role!r}")
    return {"id": sid, "text": text, "role": role, "block": block,
            "asserting": bool(asserting) and role != "context"}


def source_from_text(text, *, default_role="claimed"):
    """Paragraphs (blank-line separated) become blocks p1, p2, ...

    A paragraph may start with ``[given]``, ``[claimed]`` or ``[context]``; an
    untagged paragraph is ``claimed`` (it must be derived, and cannot anchor an
    assumption), so premises have to be tagged ``[given]`` explicitly.
    Sentence ids are ``p<paragraph>.<sentence>``, one-based.
    """
    sentences = []
    for number, paragraph in enumerate((p for p in re.split(r"\n\s*\n", text) if p.strip()), 1):
        role = default_role
        match = _TAG.match(paragraph.strip())
        body = paragraph.strip()
        if match:
            role, body = match[1].lower(), body[match.end():]
        for k, sentence in enumerate(split_sentences(body), 1):
            sentences.append(_sentence(f"p{number}.{k}", sentence, role, f"p{number}"))
    if not sentences:
        raise VEError("Source text contains no sentences")
    return {"sentences": sentences}


def load_source(data):
    """Validate a source dictionary ({"sentences": [...]}) and return a copy.

    A sentence without a ``role`` is ``claimed`` (see the module docstring).
    """
    if type(data) is not dict or type(data.get("sentences")) is not list or not data["sentences"]:
        raise VEError("A source needs a nonempty 'sentences' list")
    seen, result = set(), []
    for row in data["sentences"]:
        if type(row) is not dict or not isinstance(row.get("id"), str) or not isinstance(row.get("text"), str):
            raise VEError("Each sentence needs string 'id' and 'text'")
        if row["id"] in seen:
            raise VEError(f"Duplicate sentence id: {row['id']}")
        seen.add(row["id"])
        result.append(_sentence(row["id"], row["text"], row.get("role", "claimed"),
                                row.get("block", row["id"].split(".")[0]), row.get("asserting", True)))
    return {"sentences": result}


# ---------------------------------------------------------------------------
# P5 dossiers (experiments/P5-shifting-definitions in ve-codex)

def read_p5_items(path):
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        text = stream.read()
    text = text.strip()
    if text.startswith("{") and "\n" not in text:
        return [json.loads(text)]
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def select_p5_item(path, item=None):
    items = read_p5_items(path)
    if item is None:
        if len(items) != 1:
            raise VEError("The dossier file has several items; pass an item id or index")
        return items[0]
    for row in items:
        if row.get("id") == item or row.get("payload", row).get("id") == item:
            return row
    if str(item).isdigit() and int(item) < len(items):
        return items[int(item)]
    raise VEError(f"No P5 item {item!r} in {path}")


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def p5_environment(payload):
    """Public P5 vocabulary with readable symbols.

    One unary predicate per glossary SENSE (as in p5_json_authoring.vocabulary),
    named by the term when it has one sense and term_sense when it has several,
    so the deterministic paraphrase names the sense. Descriptions keep the
    public gloss verbatim. No facts or rules are generated.
    """
    senses = []
    for entry in payload["glossary"]:
        match = re.fullmatch(r"(.+): (.+) \((R\d+)\)", entry["sense"])
        if not match or match[1] != entry["term"]:
            raise VEError("Unrecognised P5 glossary entry")
        senses.append((match[1], match[2], match[3], entry["sense"]))
    counts = {}
    for term, *_ in senses:
        counts[term] = counts.get(term, 0) + 1
    predicates = {}
    for term, sense, record, description in sorted(senses, key=lambda s: (s[0], s[2])):
        name = _slug(term) if counts[term] == 1 else _slug(term) + "_" + _slug(sense)
        if not valid_identifier(name) or name in RESERVED or re.fullmatch(r"x[0-9]+", name):
            name = "p_" + name
        if name in predicates:
            name += "_" + record.lower()
        predicates[name] = {"arguments": ["entity"], "description": description}
    text = json.dumps({k: payload[k] for k in ("premises", "records", "nodes")})
    constants = sorted(set(re.findall(r"\bunit\d+\b", text)))
    if re.search(r"Lot unit\d+ supplied sample unit\d+\.", text):
        predicates["supplied"] = {"arguments": ["entity", "entity"], "description": "Lot supplied sample."}
    return {"language": "ve.core@0", "profile": "relational-fol@0",
            "spec_revision": "ve-v0-draft-2026-09-20", "vocabulary": {
                "sorts": {"entity": {"description": "A named dossier entity."}},
                "predicates": dict(sorted(predicates.items())),
                "constants": {c: {"sort": "entity", "description": c} for c in constants}}}


def source_from_p5(item, *, targets="root"):
    """Sentences, frozen-target slots and environment for one P5 dossier.

    Declared premises and authoritative records are ``given``; paragraph
    sentences are ``claimed``. The target is the first sentence of the root
    paragraph (its conclusion), or of every paragraph with ``targets='all'``.
    Target FORMULAS are not supplied: the author freezes them first.
    """
    payload = item.get("payload", item)
    sentences = []
    for block, role in (("premises", "given"), ("records", "given"), ("nodes", "claimed")):
        for row in payload[block]:
            for k, sentence in enumerate(split_sentences(row["text"]), 1):
                sentences.append(_sentence(f"{row['id']}.{k}", sentence, role, row["id"]))
    roots = [payload["root"]] if targets == "root" else [n["id"] for n in payload["nodes"]]
    target_rows = [{"id": "t_" + node, "sentence": f"{node}.1"} for node in roots]
    parents = {n["id"]: list(n["parents"]) for n in payload["nodes"]}
    return {"source": {"sentences": sentences}, "targets": target_rows,
            "environment": p5_environment(payload),
            "metadata": {"p5_item_id": payload["id"], "p5_root": payload["root"],
                         "p5_paragraph_parents": parents}}
