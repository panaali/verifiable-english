"""The gen-inv-design document covers every route the code gives it (gen-inv-design review F1, F2).

Design (a) makes the audit manifests and the checker pins train-only: a branch holds main's copies. So every default
build route that compiles a manifest must be one gi-1 removes, and every pin key of `lean/checkers.lock` must be one
the candidate prep writes. Both lists are read from the code, not from the review's examples: a new glob, import,
manifest or pin key the design does not name fails here. Once gi-1 lands, no route is left and the first test holds
trivially.
"""
from __future__ import annotations

import json
import ast
from pathlib import Path
import sys
import tomllib

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "lean"))
from audit import MANIFESTS  # noqa: E402
from check_lean_imports import imports, lake_globs  # noqa: E402
import lean_statements  # noqa: E402

DESIGN = ROOT / "docs/infra/gen-inv-design/DESIGN.md"
GLOB = {"andSubmodules": "{}.*", "submodules": "{}.+", "one": "{}"}
# The word the candidate prep's row uses for the checker each pin key pins.
CHECKER = {"ve_service": "ve_service", "rust_jsonl": "Rust"}


def module(path: str) -> str:
    return path.removesuffix(".lean").replace("/", ".")


def default_build_routes(manifest: str, root: Path = ROOT) -> list[str]:
    """What names `manifest` in the default build: the lakefile glob that matches it, or each Lean file that imports
    it."""
    lakefile = (root / "lean/lakefile.toml").read_text()
    globs, _ = lake_globs(tomllib.loads(lakefile))
    name = module(manifest)
    routes = [f"lean/lakefile.toml {GLOB[kind].format(root)}" for root, kind in globs
              if (kind != "submodules" and name == root) or (kind != "one" and name.startswith(root + "."))]
    return routes + sorted(f"{p.relative_to(root)} import" for p in (root / "lean").rglob("*.lean")
                           if ".lake" not in p.parts and name in imports(p.read_text()))


def test_gi1_names_every_default_build_route_of_every_manifest():
    """PROBE F1: the design named the `VE.Audit` import only, not the `ResponseShape.*` glob of the lakefile."""
    design = DESIGN.read_text()
    for manifest in MANIFESTS:
        assert f"lean/{manifest}" in design or module(manifest) in design, manifest
        assert default_build_routes(manifest) == [], manifest


def test_gi1_route_guard_accepts_exactly_nondefault_modules(tmp_path):
    lean = tmp_path / "lean"
    lean.mkdir()
    (lean / "lakefile.toml").write_text('defaultTargets = ["Shapes"]\n[[lean_lib]]\nname = "Shapes"\nglobs = ["Shapes.*"]\n')
    (lean / "Shapes.lean").write_text("-- root\n")
    (lean / "ShapesAudit.lean").write_text("-- audit\n")
    assert default_build_routes("ShapesAudit.lean", tmp_path) == []
    (lean / "Shapes.lean").write_text("import ShapesAudit\n")
    assert default_build_routes("ShapesAudit.lean", tmp_path) == ["lean/Shapes.lean import"]
    (lean / "Shapes.lean").write_text("-- root\n")
    (lean / "Shapes" ).mkdir()
    (lean / "Shapes/Audit.lean").write_text("-- audit\n")
    assert default_build_routes("Shapes/Audit.lean", tmp_path) == ["lean/lakefile.toml Shapes.*"]


def test_gi1_dump_build_omits_both_audit_modules(monkeypatch):
    modules = ["VE", "VE.Audit", "ResponseShape", "ResponseShapeAudit"]
    monkeypatch.setattr(lean_statements, "tree_modules", lambda root: modules)
    called = []

    class StopBuild(Exception):
        pass

    def build(argv, **kwargs):
        called.append(argv)
        raise StopBuild

    monkeypatch.setattr(lean_statements.subprocess, "run", build)
    with pytest.raises(StopBuild):
        lean_statements.dump_all(ROOT)
    assert called == [["lake", "build", "VE", "ResponseShape"]]


def audit_stage(source: str, *, selection, candidate: bool):
    """Execute the gate's actual audit branch with recording stubs, including its selection guard."""
    tree = ast.parse(source)
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    branches = [n for n in ast.walk(main) if isinstance(n, ast.If)
                and ast.unparse(n.test) == "selection is None"
                and "Lean audit" in ast.unparse(n)]
    assert len(branches) == 1
    branch = ast.fix_missing_locations(ast.Module(body=[branches[0]], type_ignores=[]))
    calls = []
    args = type("Args", (), {"workers": "auto", "base": "candidate-base" if candidate else None})()
    scope = {"selection": selection, "args": args, "env": {}, "result": {"stages": []},
             "os": type("OS", (), {"environ": {}})(),
             "command": lambda argv, **kw: calls.append((argv, kw))}
    exec(compile(branch, "gate-audit-branch", "exec"), scope)
    return calls, scope["result"]["stages"]


@pytest.mark.parametrize("candidate", [False, True])
def test_lean_audit_stage_runs_in_full_and_candidate_mode(candidate):
    source = (ROOT / "tools/gate.py").read_text()
    calls, stages = audit_stage(source, selection=None, candidate=candidate)
    assert len(calls) == 1
    assert calls[0][0][:5] == ["uv", "run", "--frozen", "--no-sync", "python"]
    assert "lean/audit.py" in calls[0][0]
    assert calls[0][1]["stage"] == "Lean audit"
    assert stages == ["lean_audit"]
    assert audit_stage(source, selection=[], candidate=candidate) == ([], [])


def test_lean_audit_stage_guard_refuses_missing_stage():
    source = (ROOT / "tools/gate.py").read_text()
    with pytest.raises(AssertionError):
        audit_stage(source.replace('stage="Lean audit"', 'stage="removed"'), selection=None, candidate=True)


def test_the_candidate_prep_writes_every_pin_key():
    """PROBE F2: the prep ran on the probe or an unpinned `ve_service` only, so a Rust-only change was never pinned."""
    design = DESIGN.read_text()
    prep = design[design.index("| merge train: mkcand"):design.index("| x86 essentials |")]
    for key in json.loads((ROOT / "lean/checkers.lock").read_text()):
        assert key in CHECKER, f"pin key {key}: the design's candidate prep must name its checker"
        assert CHECKER[key] in prep, key
