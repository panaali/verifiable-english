#!/usr/bin/env python3
"""Run 20261017T1800Z: the repair of u0156.s03, which the audit of run 20261017T0600Z marked UNFAITHFUL (readings incomplete: no candidate says what the sentence says if it continues
the situation of u0156.s01). frame_u0156.py owns the four candidates; this script (a) adds the two in-frame candidates, still without content, to the set in
translation-without-content.ve.md and says in the two carried candidates that they state the rule for every case, (b) writes the companion readings/all-strict-in-frame.ve.md (the strict
companion with the in-frame strict rule; used for its English and its silence sentence), (c) asserts the carried shapes (AT-0p guards, noun "thing"). nd.py all then gives every candidate
its content, declares the frame term and the unit's meaning, and finds the separating situations.

    uv run python usecases/claude-constitution-pilot/run-20261017T1800Z/repair_20261017T1800Z.py          # idempotent: stops if the set already has four candidates
    uv run python usecases/claude-constitution-pilot/run-20261017T1800Z/repair_20261017T1800Z.py --check  # asserts the finished documents (after nd.py all)
"""
from __future__ import annotations

import copy
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
import frame_u0156 as fr  # noqa: E402
import s03_scope as sc  # noqa: E402
import spec_nd as nd  # noqa: E402
import repair_20261015T0600Z as r0600  # noqa: E402  (check_at0p_shape)

RUN_ID = "20261017T1800Z"


def declare_frame(meta):
    """The frame term as a predicate and an open term of a document (nd.py does the same for the main chain)."""
    meta["environment"]["vocabulary"]["predicates"][fr.FRAME_TERM] = nd.base([nd.CLAUDE], fr.ENGLISH, fr.DESCRIPTION)
    meta["open_terms"].append({"name": fr.FRAME_TERM, "arguments": [nd.CLAUDE], "decided_by": "unresolved_decider", "necessary": [], "sufficient": [],
                               "factors": list(fr.FACTORS), "precedents": [], "jurisdiction": "claude_constitution", "version": 1})


def add_candidates(meta):
    meta = copy.deepcopy(meta)
    item = next(s for s in meta["reading_sets"] if s["id"] == fr.SET_ID)
    assert [r["id"] for r in item["readings"]] == ["strict", "default"], [r["id"] for r in item["readings"]]
    models = item["models"]
    model_id = next(iter(models))
    base = {r["id"]: r for r in item["readings"]}
    for rid in ("strict", "default"):
        base[rid]["admission"]["why"] += fr.EVERY_CASE
    for rid, twin in (("strict-in-frame", "strict"), ("default-in-frame", "default")):
        why = base[twin]["admission"]["why"].replace(fr.EVERY_CASE, "") + fr.IN_FRAME_WHY
        item["readings"].append({"id": rid, "kind": "norm", "meaning_id": f"pending-{rid}-u0156-s03", "content": None,
                                 "admission": {"who": "translator", "why": why, "distinguishing_models": {}}})
    for r in item["readings"]:
        r["admission"]["distinguishing_models"] = {o["id"]: model_id for o in item["readings"] if o["id"] != r["id"]}
    return meta


def frame_companion(strict_meta):
    meta = copy.deepcopy(strict_meta)
    declare_frame(meta)
    for u in pilot._flat(meta["units"]):
        if u["id"] == fr.UNIT:
            u["content"] = fr.with_frame(u["content"])
            now = u["meaning"]
            u["meaning"] = {"open": [fr.FRAME_TERM]} if now == "specified" else {"open": [*now["open"], fr.FRAME_TERM]}
    return meta


S06_TERM = "illegitimate_absolute_control"
S06_FACTOR = "whether only the especially severe and flagrant attempts count (u0186.s01: “We’ve included assisting with especially severe and flagrant attempts to grab illegitimate power under the hard constraints above”)"
S06_DESCRIPTION_ADD = (" u0186.s01, a later sentence, says the hard constraints include “assisting with especially severe and flagrant attempts to grab illegitimate power”; whether that "
                       "limits this constraint to such attempts is one of the term's factors.")


def note_u0186(meta):
    """Audit 20261017T0600Z, small fault: u0186.s01 is a governor of u0165.s06 (scope tally) but neither the note nor the open term's record mentioned it."""
    pred = meta["environment"]["vocabulary"]["predicates"][S06_TERM]
    term = next(t for t in meta["open_terms"] if t["name"] == S06_TERM)
    if S06_FACTOR in term["factors"]:
        return False
    term["factors"].append(S06_FACTOR)
    pred["description"] += S06_DESCRIPTION_ADD
    return True


def check_carried(meta):
    n = r0600.check_at0p_shape(meta)
    assert n == 6, n
    assert meta["environment"]["vocabulary"]["sorts"]["entity"]["verbalisation"] == {"singular": "thing", "plural": "things"}
    text = str(meta)
    assert not re.search(r"thought_likely|knowingly_<", text)


def main(argv):
    if "--check" in argv:
        main_meta, _ = pilot.read(RUN / "translation.ve.md")
        item = next(s for s in main_meta["reading_sets"] if s["id"] == fr.SET_ID)
        assert [r["id"] for r in item["readings"]] == fr.READINGS and all(r["content"] is not None for r in item["readings"])
        flat = {u["id"]: u for u in pilot._flat(main_meta["units"])}
        terms = {t["name"] for t in main_meta["open_terms"]}
        assert flat[fr.UNIT]["meaning"] == {"open": [fr.EXCEPTION_TERM, fr.FRAME_TERM]} and fr.FRAME_TERM in terms, flat[fr.UNIT]["meaning"]
        for r in item["readings"]:
            c = r["content"]["norm"]
            assert c["predicate"] == "system_prompt_deception_permitted" and c["sign"] is False
            assert (c["guard"] == ["unary", fr.FRAME_TERM, ["var", 1]]) == (r["id"] in fr.IN_FRAME), r["id"]
            assert bool(c["unless"]) == r["id"].startswith("default"), r["id"]
            why = r["admission"]["why"]
            assert "stored model is a placeholder" not in why and "recorded here without content" not in why and "Both candidates carry content" not in why, r["id"]
            assert ("only for the situation in which Claude is asked" in why) == (r["id"] in fr.IN_FRAME)
        term = next(t for t in main_meta["open_terms"] if t["name"] == S06_TERM)
        assert S06_FACTOR in term["factors"] and S06_DESCRIPTION_ADD in main_meta["environment"]["vocabulary"]["predicates"][S06_TERM]["description"]
        print("translation.ve.md ok: u0156.s03 has four candidates with content and the frame term in its meaning")
        return
    meta, source = pilot.read(RUN / "translation-without-content.ve.md")
    assert [r["id"] for s_ in meta["reading_sets"] if s_["id"] == fr.SET_ID for r in s_["readings"]] == ["strict", "default"], "already repaired: the set has four candidates"
    strict, strict_source = pilot.read(RUN / "readings/all-strict.ve.md")
    check_carried(meta)
    check_carried(strict)
    meta = add_candidates(meta)
    note_u0186(meta)
    pilot.write(RUN / "translation-without-content.ve.md", meta, source)
    note_u0186(strict)
    pilot.write(RUN / "readings/all-strict.ve.md", strict, strict_source)
    narrow, narrow_source = pilot.read(RUN / "readings/all-strict-narrow.ve.md")
    note_u0186(narrow)
    pilot.write(RUN / "readings/all-strict-narrow.ve.md", narrow, narrow_source)
    companion = frame_companion(strict)
    pilot.write(RUN / "readings/all-strict-in-frame.ve.md", companion, strict_source)
    print("ok:", [r["id"] for s in meta["reading_sets"] if s["id"] == fr.SET_ID for r in s["readings"]], len(companion["open_terms"]), "open terms in the companion")


if __name__ == "__main__":
    main(sys.argv)
