#!/usr/bin/env python3
"""Run 20261020T0600Z: measurement of the audit's three small faults (AUDIT-20261019T1800Z-received.md) on the three unclaimed relational-noun headings.

  * u0095, u0002: the fences' owner was `anthropic`, a constant of the sort principal_type ("Anthropic, as a type of principal"); the guidelines and the mission belong to the company. Probe: a
    separate constant `anthropiccompany` of the sort `entity` (a thing), with the predicates over (thing, thing).
  * u0235: "Claude's nature" is a singular possessive: existence AND uniqueness (as u0002's "the mission of"). Probe: the enumerated uniqueness form.
  * u0013: "of claude" is lower case. Probe: a constant named `Claude`.

Parse and render only (no unit of the translation changes; the document is not touched). Writes evidence/owner-probe.json."""
from __future__ import annotations
import json, sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
from ve.ast import formula_to_data  # noqa: E402
from ve.english import parse_english, render_english  # noqa: E402
from ve.environment import Environment  # noqa: E402

meta = json.loads((RUN / "translation-without-content.ve.md").read_bytes().split(b"---\n", 2)[1])
voc = meta["environment"]["vocabulary"]
voc["constants"]["anthropiccompany"] = {"sort": "entity", "description": "The company Anthropic (probe)."}
voc["predicates"]["guideline_of_probe"] = {"arguments": ["entity", "entity"], "description": "probe", "verbalisation": "{0} is a guideline of {1}"}
voc["predicates"]["mission_of_probe"] = {"arguments": ["entity", "entity"], "description": "probe", "verbalisation": "{0} is a mission of {1}"}
voc["predicates"]["nature_of_probe"] = {"arguments": ["entity", "entity"], "description": "probe", "verbalisation": "{0} is a nature of {1}"}
voc["predicates"]["core_value_of_probe"] = {"arguments": ["entity", "entity"], "description": "probe", "verbalisation": "{0} is a core value of {1}"}
capital = json.loads(json.dumps(meta["environment"]))
capital["vocabulary"]["constants"]["Claude"] = {"sort": "entity", "description": "Claude (probe, capitalised)."}
try:
    Environment.from_dict(capital)
    CAPITAL = {"declared": True}
except Exception as exc:  # noqa: BLE001
    CAPITAL = {"declared": False, "error": f"{type(exc).__name__}: {str(exc)[:200]}"}
print("capitalised constant:", CAPITAL)
env = Environment.from_dict(meta["environment"])
FENCES = {
    "u0095.company": "Some thing is a guideline of anthropiccompany.",
    "u0002.company": ("There is a first thing such that both of the following hold:\n  (a) the first thing is a mission of anthropiccompany;\n"
                      "  (b) for every second thing that is a mission of anthropiccompany, the second thing is the same as the first thing."),
    "u0235.unique": ("There is a first thing such that both of the following hold:\n  (a) the first thing is a nature of claude;\n"
                     "  (b) for every second thing that is a nature of claude, the second thing is the same as the first thing."),
}
out = {}
for k, text in FENCES.items():
    try:
        parsed = parse_english(env, text)
        data = [formula_to_data(env, f) for f in parsed.formulas]
        back = [render_english(f, env) for f in parsed.formulas]
        again = [formula_to_data(env, f) for f in parse_english(env, back[0] + ".").formulas]
        out[k] = {"fence": text, "parses": True, "formulas": data, "rendered": back, "round_trip_same_formula": again == data}
    except Exception as exc:  # noqa: BLE001
        out[k] = {"fence": text, "parses": False, "error": f"{type(exc).__name__}: {str(exc)[:300]}"}
    print(k, json.dumps(out[k], ensure_ascii=False)[:400])
out["u0013.capital"] = {"fence": "Some thing is a core value of Claude.", **CAPITAL}
(RUN / "evidence").mkdir(exist_ok=True)
(RUN / "evidence/owner-probe.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
