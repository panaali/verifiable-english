"""Regenerates environment.json, rules.json and wordings.json in this directory from
usecases/eligibility (read only; relb-f1f2-grammar, 2026-11-22). Run from the repository root:
    .venv/bin/python -B tests/fixtures/relb_f1f2/make_fixtures.py
The tests read only the files written here, so later changes to usecases/eligibility do not move them.
wordings.json holds render_w6_sentence's wording of each rule (the generated layout the tests read back)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "usecases/eligibility"))
import translation as T  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.surface.time import render_w6_sentence  # noqa: E402
from ve.units import elaborate_quantity  # noqa: E402

raw = T.environment()
env = Environment(raw)
rules = [{"id": r["id"], "source": r["source"], "formula": r["formula"]} for r in T.rules()]
wordings = {}
for r in rules:
    canonical, _ = elaborate_quantity(env, T.q(r["formula"]))
    wordings[r["id"]] = render_w6_sentence(env, canonical)


def dump(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")


dump("environment.json", raw)
dump("rules.json", rules)
dump("wordings.json", wordings)
print(len(rules), "rules")
