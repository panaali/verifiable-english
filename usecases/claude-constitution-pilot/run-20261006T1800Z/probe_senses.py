#!/usr/bin/env python3
"""Probe (not part of the counted translation): what the senses reader (merged before ve-green-senses) gives for constitution words.

    uv run python usecases/claude-constitution-pilot/run-20261006T1800Z/probe_senses.py

The constitution itself says that "corrigible" has a sense it means ("not undermining legitimate human oversight", line 588)
and one it does not mean ("blind obedience"), and uses "safe" in a technical sense ("broadly safe") and an everyday one.
`ve senses check` is admission only: it reads sentences under a sense pack and reports unit formulas or open candidates;
there is no document integration (senses-integration-report.md: B6/B7 open), so nothing here upgrades a ledger unit.
Writes probes/senses-probe.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))

from ve.backends import senses as route  # noqa: E402
from ve.environment import Environment  # noqa: E402

SORT = {"name": "being", "noun": "being", "plural": "beings", "description": "A being.", "letter": "B"}
PACK = {"format": "ve.sense-pack@1", "name": "constitution-probe@1", "sorts": [SORT], "senses": [
    {"word": "corrigible", "index": 1, "gloss": "oversight respecting", "description": "does not actively undermine legitimate human oversight",
     "kinds": ["being"], "wording": "{0} is corrigible"},
    {"word": "corrigible", "index": 2, "gloss": "blindly obedient", "description": "obeys any human without question",
     "kinds": ["being"], "wording": "{0} is corrigible"},
    {"word": "safe", "index": 1, "gloss": "broadly safe", "description": "the constitution's technical sense: supports appropriate human oversight",
     "kinds": ["being"], "wording": "{0} is safe"},
    {"word": "safe", "index": 2, "gloss": "harmless", "description": "not in danger of harm", "kinds": ["being"], "wording": "{0} is safe"}]}

TEXTS = {
    "bare": "Claude is corrigible.",
    "default_line": "In this document, corrigible means oversight respecting.\nClaude is corrigible.",
    "switch_parenthetical": "Claude is corrigible (meaning oversight respecting).",
    "switch_rejected_sense": "Claude is not corrigible (meaning blindly obedient).",
    "two_words_no_default": "Claude is corrigible and Claude is safe.",
    "unknown_gloss": "Claude is corrigible (meaning obedient).",
    "constitution_sentence_kept_open": "Claude is safe.",
}


def main():
    env = Environment({"language": "ve.core@0", "profile": "relational-fol@0", "spec_revision": "ve-v0-draft-2026-09-20",
                       "vocabulary": {"sorts": {"being": {"description": "A sort."}}, "predicates": {},
                                      "constants": {"claude": {"sort": "being", "description": "A constant."}}}})
    overlay = {"format": "ve.english-vocabulary@1", "environment_id": env.environment_id, "sorts": {}, "predicates": {}, "constants": {}}
    pack = json.dumps(PACK).encode()
    out = {}
    for name, text in TEXTS.items():
        try:
            answer = route.read(env, text, [pack], overlay=overlay, budget=route.WORK_BUDGET)
            r = answer["reading"]
            slim = {"status": r["status"]}
            for k in ("code", "sentence", "details", "failure"):
                if k in r:
                    slim[k] = r[k]
            if "units" in r:
                slim["units"] = [{k: u.get(k) for k in ("sentence", "state", "formula", "candidates", "unresolved", "senses") if k in u} for u in r["units"]]
            if "text" in r:
                slim["text"] = r["text"]
            out[name] = {"source": text, "reading": slim}
        except Exception as exc:  # a refusal is a result
            out[name] = {"source": text, "error": f"{type(exc).__name__}: {exc}"[:400]}
    (RUN / "probes").mkdir(exist_ok=True)
    (RUN / "probes/senses-probe.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(out, indent=1, ensure_ascii=False)[:6000])


if __name__ == "__main__":
    main()
