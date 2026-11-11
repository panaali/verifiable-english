"""ap-5: `VE.Acts.Specialise` sits in the layer of `VE.Acts.Readings` (tools/layer_policy.py, task deliverable 3).

Without its row the module would fall to its package's default layer and `tools/check_lean_imports.py` would still
pass, so this test pins the placement and that both new modules import nothing above their layer."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_lean_imports import imports  # noqa: E402
from layer_policy import lean_layer  # noqa: E402


def test_specialise_sits_in_the_layer_of_readings_and_imports_nothing_above_it():
    assert lean_layer("VE.Acts.Readings") is not None
    assert lean_layer("VE.Acts.Specialise") == lean_layer("VE.Acts.Readings")
    for name in ("Specialise", "SpecialiseExamples"):
        module = f"VE.Acts.{name}"
        layer = lean_layer(module)
        assert layer is not None, module
        for imported in imports((ROOT / f"lean/VE/Acts/{name}.lean").read_text()):
            assert lean_layer(imported) is not None and lean_layer(imported) <= layer, (module, imported)
