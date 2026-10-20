"""Ledger repair (the 20261016T1800Z audit's open gap): u052 and u114 list a companion file for their ASSERTED candidate
(case_excluded, no_implied_right) that never existed. An asserted formula has no norm-defaults status point, so only the norm
candidate has a companion. Translation parts, readings and meanings are unchanged; only the ledger text and lists change."""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
doc = json.loads((HERE / "units.json").read_text())
units = doc if isinstance(doc, list) else doc["units"]
FIX = {"u052": ("case_excluded", "invocation_barred"), "u114": ("no_implied_right", "interpretive_ban")}
for u in units:
    if u["id"] not in FIX:
        continue
    gone, kept = FIX[u["id"]]
    for key in ("companions", "norm_defaults_companions"):
        u[key] = [c for c in u[key] if f".{gone}." not in c]
        assert u[key] == [f"readings/{u['id']}.{kept}.ve.md"], u[key]
    old = "each candidate also stands as a one-unit companion document with Lean status witnesses (a case inside the rule is SETTLED, a case outside it UNDECIDED, never 'not required' and never permitted)."
    new = (f"the norm candidate {kept} also stands as a one-unit companion document with Lean status witnesses (a case inside the rule is SETTLED, a case outside it UNDECIDED, "
           f"never 'not required' and never permitted); the asserted candidate {gone} is a formula and has no status point, so it has no companion document (repaired 20261017T0600Z: the ledger had listed one that never existed).")
    assert old in u["formal_depth"]
    u["formal_depth"] = u["formal_depth"].replace(old, new)
    u["ledger_repair_20261017T0600Z"] = f"removed the non-existent companion readings/{u['id']}.{gone}.ve.md from companions and norm_defaults_companions; no change to the translation"
(HERE / "units.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + ("\n" if True else ""))
print("ok")
