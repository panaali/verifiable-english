#!/usr/bin/env python3
"""PS-0p step 3 and 5: which wordings the English vocabulary lint admits in this run's environment, without changing an existing one.

    uv run python usecases/claude-constitution-pilot/run-20261018T1800Z/ps0p_wordings.py
Writes evidence/ps0p/wording-lint.json (read only otherwise)."""
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
    ("open_problem", ["entity"], "{0} is unsolved", "Some thing is unsolved."),
    ("deployment_context", ["entity"], "{0} is a deployment context", "Some thing is a deployment context."),
    ("existing_deployment_context", ["entity"], "{0} is an existing deployment context", "Some thing is an existing deployment context."),
    ("in_use_deployment_context", ["entity"], "{0} is a deployment context in use", "Some thing is a deployment context in use."),
    ("deployment_context_in_use", ["entity"], "{0} is deployed", "Some thing is deployed."),
    ("novel_kind", ["entity"], "{0} is a novel kind of thing", "Some thing is a novel kind of thing."),
    ("novel_entity", ["entity"], "{0} is novel", "Some thing is novel."),
    ("genuine_helpfulness", ["entity"], "{0} constitutes genuine helpfulness", "Some thing constitutes genuine helpfulness."),
    ("is_genuinely_helpful", ["entity"], "{0} is genuinely helpful", "Some thing is genuinely helpful."),
    ("genuine_helpfulness_b", ["entity"], "{0} is helpful", "Some thing is helpful."),
    ("genuine_helpfulness_c", ["entity"], "{0} counts as genuine helpfulness", "Some thing counts as genuine helpfulness."),
    ("genuine_helpfulness_d", ["entity"], "{0} is part of genuine helpfulness", "Some thing is part of genuine helpfulness."),
    ("genuine_helpfulness_e", ["entity"], "{0} makes up genuine helpfulness", "Some thing makes up genuine helpfulness."),
    ("genuine_helpfulness_f", ["entity"], "{0} is truly helpful", "Some thing is truly helpful."),
    ("genuine_helpfulness_g", ["entity"], "{0} is genuine help", "Some thing is genuine help."),
    ("value_other_than_helpfulness", ["entity"], "{0} is a value other than helpfulness", "Some thing is a value other than helpfulness."),
]
out = []
for name, args, wording, sentence in CANDIDATES:
    m = copy.deepcopy(meta)
    m["environment"]["vocabulary"]["predicates"][name] = {"arguments": args, "description": "PS-0p wording probe.", "verbalisation": wording}
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
(RUN / "evidence/ps0p/wording-lint.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
