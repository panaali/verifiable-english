#!/usr/bin/env python3
"""Probe (not part of the counted translation): what the senses block of `ve document` (RD-8, merged in ve-green-rd-6a) gives for
words the constitution itself discusses.

    uv run python usecases/claude-constitution-pilot/run-20261008T0600Z/probe_senses_doc.py

Last run's probe (probe_senses.py) could only use `ve senses check` (admission, no document). A document may now carry
`"senses": {"packs": [...], "own": [...], "defaults": {word: index}}`; its English fences are read by Lean's sense reader and each
unit is checked in the projected environment. The probe writes small documents under probes/senses-documents/ and records, for each,
the unit status or Lean's refusal text. The constitution's words: "corrigible" (the text says it means not undermining legitimate
human oversight and does not mean blind obedience, line 588) and "safe" (everyday sense, and "broadly safe" in the technical sense).
Writes probes/senses-document-probe.json. Nothing here upgrades a ledger unit (see FEATURE-REVIEW.md).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))

from ve.document import load_document  # noqa: E402
from ve.errors import VEError  # noqa: E402

OUT = RUN / "probes/senses-documents"
SORT = {"name": "being", "noun": "being", "plural": "beings", "description": "A being.", "letter": "B"}
PACK = {"format": "ve.sense-pack@1", "name": "constitution-probe@1", "sorts": [SORT], "senses": [
    {"word": "corrigible", "index": 1, "gloss": "oversight respecting", "description": "does not actively undermine legitimate human oversight",
     "kinds": ["being"], "wording": "{0} is corrigible"},
    {"word": "corrigible", "index": 2, "gloss": "blindly obedient", "description": "obeys any human without question",
     "kinds": ["being"], "wording": "{0} is corrigible"},
    {"word": "safe", "index": 1, "gloss": "broadly safe", "description": "the constitution's technical sense: supports appropriate human oversight",
     "kinds": ["being"], "wording": "{0} is safe"},
    {"word": "safe", "index": 2, "gloss": "harmless", "description": "not in danger of harm", "kinds": ["being"], "wording": "{0} is safe"}]}
ENV = {"language": "ve.core@0", "profile": "relational-fol@0", "spec_revision": "ve-v0-draft-2026-09-20",
       "vocabulary": {"sorts": {"being": {"description": "A sort."}}, "predicates": {},
                      "constants": {"claude": {"sort": "being", "description": "A constant."}}}}
LINE_1 = "In this document, corrigible means oversight respecting."
CASES = {
    "a_front_matter_default": (["Claude is corrigible."], {"packs": ["pack.json"], "defaults": {"corrigible": 1}}),
    "b_no_choice_made": (["Claude is corrigible."], {"packs": ["pack.json"]}),
    "c_written_definition_line": ([LINE_1, "Claude is corrigible."], {"packs": ["pack.json"]}),
    "d_parenthetical_switch": (["Claude is corrigible (meaning oversight respecting)."], {"packs": ["pack.json"]}),
    "e_the_rejected_sense_negated": (["Claude is not corrigible (meaning blindly obedient)."], {"packs": ["pack.json"]}),
    "f_two_words_one_default": (["Claude is corrigible and Claude is safe."], {"packs": ["pack.json"], "defaults": {"corrigible": 1}}),
    "g_bad_default": (["Claude is corrigible."], {"packs": ["pack.json"], "defaults": {"corrigible": 3}}),
}


def write(name, texts, senses):
    body, units, cursor = b"", [], 0
    for i, text in enumerate(texts, 1):
        prose = f"Sentence {i}.\n".encode()
        body += prose + f"```ve u{i}\n{text}\n```\n".encode()
        units.append({"id": f"u{i}", "span": [cursor, cursor + len(prose)], "kind": "definition" if text.startswith("In this document,") else "asserted",
                      "meaning": "specified", "support": "assumption", "surface": "english", "content": {"fence": f"u{i}"}})
        cursor += len(prose)
    front = {"format": "ve-document@1", "environment": ENV, "units": units, "senses": senses}
    path = OUT / f"{name}.ve.md"
    path.write_bytes(b"---\n" + json.dumps(front).encode() + b"\n---\n" + body)
    return path


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "pack.json").write_text(json.dumps(PACK, indent=1) + "\n")
    out = {}
    for name, (texts, senses) in CASES.items():
        path = write(name, texts, senses)
        try:
            doc = load_document(path)
            units = {u["id"]: {k: u.get(k) for k in ("kind", "status")} for u in doc["units"]}
            out[name] = {"texts": texts, "senses": senses, "loaded": True, "units": units,
                         "lines": sorted(doc["senses"].lines)}
        except VEError as exc:
            out[name] = {"texts": texts, "senses": senses, "loaded": False, "refusal": str(exc.message)[:600]}
        except Exception as exc:  # a refusal of another shape is a result
            out[name] = {"texts": texts, "senses": senses, "loaded": False, "error": f"{type(exc).__name__}: {exc}"[:600]}
    (RUN / "probes/senses-document-probe.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(out, indent=1, ensure_ascii=False)[:6000])


if __name__ == "__main__":
    main()
