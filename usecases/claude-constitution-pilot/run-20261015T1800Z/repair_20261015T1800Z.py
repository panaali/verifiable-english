#!/usr/bin/env python3
"""Run 20261015T1800Z: no translation change. The 20261015T0600Z audit (AUDIT-20261015T0600Z-received.md: 20/20 sampled and 9/9 changed units faithful) rejected
nothing, and no feature merged between ve-green-lf-14b and ve-green-fix-abbrev lets a unit say more. This script asserts, on the carried documents, the shape the
plan additions of this run ask for (AT-0p guards bound to the acting Claude instance, per candidate for u0165.s03) and that the vocabulary is the carried one.
It writes nothing.

    uv run python usecases/claude-constitution-pilot/run-20261015T1800Z/repair_20261015T1800Z.py
    uv run python usecases/claude-constitution-pilot/run-20261015T1800Z/nd.py all
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))

_spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pilot)
import s03_scope as sc  # noqa: E402
import spec_nd as nd  # noqa: E402
import repair_20261015T0600Z as r0600  # noqa: E402  (check_at0p_shape)

RUN_ID = "20261015T1800Z"


def main():
    for name in ("translation-without-content.ve.md", "readings/all-strict.ve.md", "readings/all-strict-narrow.ve.md"):
        meta, _ = pilot.read(RUN / name)
        n = r0600.check_at0p_shape(meta)
        assert n == 6, (name, n)
        preds = meta["environment"]["vocabulary"]["predicates"]
        terms = {t["name"] for t in meta["open_terms"]}
        for i in range(1, 8):
            if i == 3:
                for r in ("wide", "narrow"):
                    assert sc.KNOWING[r] in preds and sc.THINKING[r] in preds and sc.KNOWING[r] in terms and sc.THINKING[r] in terms
                continue
            for pre in ("knowingly_engages_", "thinks_quite_likely_"):
                p = preds[f"{pre}{i}"]
                assert p["arguments"] == [nd.CLAUDE, nd.SITUATION], (pre, i, p["arguments"])
                assert f"{pre}{i}" in terms
        text = str(meta)
        assert not re.search(r"thought_likely|knowingly_<", text)
        assert not re.search(r"(knowingly_engages_3|thinks_quite_likely_3)(?!_(wide|narrow))", text)
        assert meta["environment"]["vocabulary"]["sorts"]["entity"]["verbalisation"] == {"singular": "thing", "plural": "things"}
        print(name, "ok:", len(meta["open_terms"]), "open terms")


if __name__ == "__main__":
    main()
