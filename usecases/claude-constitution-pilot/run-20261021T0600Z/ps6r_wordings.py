#!/usr/bin/env python3
"""Run 20261019T1800Z, PS-6r (merged): do the four relational-noun wordings now parse and render in this run's environment, without changing an existing wording?

    uv run python usecases/claude-constitution-pilot/run-20261019T1800Z/ps6r_wordings.py
Writes evidence/ps6r/wording-lint.json (read only otherwise)."""
from __future__ import annotations
import copy, json, sys
from pathlib import Path
RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(RUN))
from ve.english import EnglishVocabulary, parse_english, render_english  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.ast import formula_to_data  # noqa: E402

raw = (RUN / "translation-without-content.ve.md").read_bytes()
meta = json.loads(raw.split(b"---\n", 2)[1])
base_env = Environment.from_dict(meta["environment"])
base_voc = EnglishVocabulary(base_env)
# (predicate, arguments, wording, sentence to parse)
CANDIDATES = [
    ("core_value_of", ["entity", "entity"], "{0} is a core value of {1}", "Some thing is a core value of claude."),
    ("guideline_of", ["entity", "principal_type"], "{0} is a guideline of {1}", "Some thing is a guideline of anthropic."),
    ("mission_of", ["entity", "principal_type"], "{0} is a mission of {1}", "Some thing is a mission of anthropic."),
    ("nature_of", ["entity", "entity"], "{0} is a nature of {1}", "Some thing is a nature of claude."),
    ("value_other", ["entity", "entity"], "{0} is a value of {1}", "Some thing is a value of claude."),
]
out = []
for name, args, wording, sentence in CANDIDATES:
    m = copy.deepcopy(meta)
    m["environment"]["vocabulary"]["predicates"][name] = {"arguments": args, "description": "PS-6r wording probe.", "verbalisation": wording}
    env = Environment.from_dict(m["environment"])
    v = EnglishVocabulary(env)
    changed = {k: [base_voc.predicates[k], v.predicates[k]] for k in base_voc.predicates if v.predicates.get(k) != base_voc.predicates[k]}
    row = {"predicate": name, "wording": wording, "selected": v.predicates[name], "accepted": v.predicates[name] == wording,
           "lint": sorted({i.code for i in v.issues if f"/predicates/{name}/" in i.path}), "existing_wordings_changed": changed}
    try:
        p = parse_english(env, sentence)
        row["parses_to"] = [formula_to_data(env, f) for f in p.formulas]
        row["rendered"] = render_english(p.formulas[0], env)
    except Exception as e:
        row["parse_error"] = f"{type(e).__name__}: {e}"
    out.append(row)
    print(json.dumps({k: row[k] for k in ("predicate", "accepted", "lint", "selected")} | {"changed": list(changed), "parse": row.get("parse_error") or row.get("rendered")}, ensure_ascii=False))
(RUN / "evidence/ps6r/wording-lint.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
