#!/usr/bin/env python3
"""Run 20261008T1800Z: the one availability repair of the carried documents (wording only, no meaning change).

    uv run python usecases/claude-constitution-pilot/run-20261008T1800Z/reword.py

At `ve-green-lf-15b` Lean's English reader is authoritative for `ve document render` (lean-first E2/lf-15b). It refuses a
predicate wording that does not lex as ONE sentence (V3), and the act phrases of two regulated predicates held an apostrophe
("the system prompt's instructions", "a system prompt's existence-or-content"). `ve document render` of the previous run's
translation therefore answered `CheckerUnavailable: invalidGrammar lexicon: V3 predicate system_prompt_compliance_required`
(`check` still ran). The two act phrases lose the apostrophe; nothing else changes: units, spans, contents, open terms and
reading sets are byte-identical, and the identities that depend on the vocabulary (the placeholder models' ids) are recomputed.
"""
import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import readings_s1_pilot as pilot  # noqa: E402
from ve.document import _environment  # noqa: E402

ACTS = {"system_prompt_compliance_required": "{0} comply with the system prompt instructions in {1}",
        "system_prompt_deception_permitted": "{0} actively deceive {1} about system prompt existence-or-content"}


def reword(path):
    raw = Path(path).read_bytes()
    head, front, rest = raw.split(b"---\n", 2)
    meta = json.loads(front)
    preds = meta["environment"]["vocabulary"]["predicates"]
    changed = []
    for name, act in ACTS.items():
        if name in preds and preds[name]["regulated"]["act"] != act:
            changed.append((name, preds[name]["regulated"]["act"]))
            preds[name]["regulated"]["act"] = act
    if not changed:
        return changed
    env = _environment(meta["environment"])
    meta["reading_sets"] = [pilot._reidentified(env, item) if all(r.get("content") is None for r in item["readings"]) else item
                            for item in meta.get("reading_sets", [])]
    Path(path).write_bytes(head + b"---\n" + json.dumps(meta, ensure_ascii=False).encode() + b"\n---\n" + rest)
    return changed


if __name__ == "__main__":
    for rel in ("translation.ve.md", "readings/all-strict.ve.md", "readings/all-default.ve.md"):
        print(rel, reword(RUN / rel))
