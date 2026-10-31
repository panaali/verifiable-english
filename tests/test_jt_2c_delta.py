"""jt-2c's saved delta (docs/judgment-terms/jt-2c/evidence, DELTA row 3, standing ruling R1): read from the saved
records, never from a live service.

Every head record refuses with the text the environment mode refuses the same environment with (reviews F1 and F5);
a record that differs from the merge base's keeps R1 against it; the F5 lists (`judgments@0` duplicated, first or last)
answer as at the merge base.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from test_judgments_compose import COMPOSING, UNORDERED

BATCH = Path(__file__).resolve().parents[1] / "docs/judgment-terms/jt-2c"
SORTED_AND_UNIQUE = "UnsupportedProfile: profiles must be sorted and unique"


def delta_module():
    spec = importlib.util.spec_from_file_location("jt_2c_delta", BATCH / "delta.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def saved(name):
    return json.loads((BATCH / "evidence" / name).read_text())


def test_the_saved_delta_is_the_comparison_of_the_saved_records(tmp_path):
    out = tmp_path / "delta.json"
    assert delta_module().compare(BATCH / "evidence/base.json", BATCH / "evidence/head.json", out) == 0
    assert out.read_text() == (BATCH / "evidence/delta.json").read_text()


def test_every_composing_mode_and_shape_is_probed():
    modes = [f"{m}/{f.get('kind', 'case')}" for m, f, _ in COMPOSING] + ["english.read/block"]
    names = {p["probe"] for p in saved("delta.json")["pairs"]}
    assert names == set(modes) | {f"{m}/{shape}" for m in modes for shape in UNORDERED}


def test_every_head_record_is_the_environment_mode_s_refusal_and_keeps_r1():
    delta = delta_module()
    for p in saved("delta.json")["pairs"]:
        assert p["faults"] == [], p
        assert delta.refuses_as_the_environment_mode(p["head"], p["authority"]) == [], p
        if p["base"] != p["head"]:
            assert delta.r1(p["base"], p["head"]) == [], p


def test_the_f5_lists_answer_as_at_the_merge_base():
    """Review F5: the head refused none of them before the fix; the merge base and the fixed head refuse them all."""
    pairs = [p for p in saved("delta.json")["pairs"] if p["probe"].rsplit("/", 1)[-1] in UNORDERED]
    assert len(pairs) == 3 * (len(COMPOSING) + 1)
    for p in pairs:
        assert p["base"] == p["head"] and p["head"]["error"] == SORTED_AND_UNIQUE, p
