"""The gen-inv-design document covers every route the code gives it (gen-inv-design review F1, F2).

Design (a) makes the audit manifests and the checker pins train-only: a branch holds main's copies. So every default
build route that compiles a manifest must be one gi-1 removes, and every pin key of `lean/checkers.lock` must be one
the candidate prep writes. Both lists are read from the code, not from the review's examples: a new glob, import,
manifest or pin key the design does not name fails here. Once gi-1 lands, no route is left and the first test holds
trivially.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "lean"))
from audit import MANIFESTS  # noqa: E402
from check_lean_imports import imports, lake_globs  # noqa: E402

DESIGN = ROOT / "docs/infra/gen-inv-design/DESIGN.md"
GLOB = {"andSubmodules": "{}.*", "submodules": "{}.+", "one": "{}"}
# The word the candidate prep's row uses for the checker each pin key pins.
CHECKER = {"ve_service": "ve_service", "rust_jsonl": "Rust"}


def module(path: str) -> str:
    return path.removesuffix(".lean").replace("/", ".")


def default_build_routes(manifest: str) -> list[str]:
    """What names `manifest` in the default build: the lakefile glob that matches it, or each Lean file that imports
    it."""
    lakefile = (ROOT / "lean/lakefile.toml").read_text()
    globs, _ = lake_globs(tomllib.loads(lakefile))
    name = module(manifest)
    routes = [f"lean/lakefile.toml {GLOB[kind].format(root)}" for root, kind in globs
              if (kind != "submodules" and name == root) or (kind != "one" and name.startswith(root + "."))]
    return routes + sorted(f"{p.relative_to(ROOT)} import" for p in (ROOT / "lean").rglob("*.lean")
                           if ".lake" not in p.parts and name in imports(p.read_text()))


def test_gi1_names_every_default_build_route_of_every_manifest():
    """PROBE F1: the design named the `VE.Audit` import only, not the `ResponseShape.*` glob of the lakefile."""
    design = DESIGN.read_text()
    for manifest in MANIFESTS:
        assert f"lean/{manifest}" in design or module(manifest) in design, manifest
        for route in default_build_routes(manifest):
            path, what = route.split(" ")
            assert path in design and (what == "import" or f"`{what}`" in design), (manifest, route)


def test_the_candidate_prep_writes_every_pin_key():
    """PROBE F2: the prep ran on the probe or an unpinned `ve_service` only, so a Rust-only change was never pinned."""
    design = DESIGN.read_text()
    prep = design[design.index("| merge train: mkcand"):design.index("| x86 essentials |")]
    for key in json.loads((ROOT / "lean/checkers.lock").read_text()):
        assert key in CHECKER, f"pin key {key}: the design's candidate prep must name its checker"
        assert CHECKER[key] in prep, key
