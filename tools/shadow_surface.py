"""Source scans of Stage 3 shadow mode (docs/spec/mig3.md 2.12, fixtures L11 to L13).

All three read Python sources only, given as ``{path: text}`` for the files
under ``ve/``, so that ``tools/shadow_gate.py`` can scan any commit's tree:

* ``execute_calls``: the first argument of every call of ``execute`` (L11);
* ``handoff_functions`` and ``handoff_modules``: the functions of
  ``ve/backends/lean.py`` that hand cases to a statement-layer route
  (decorated ``_handoff``) and the modules outside ``ve/backends/`` that call
  them (L13);
* ``static_branches``: every ``if`` whose test calls ``authority_for`` and has a
  disjunct that does not, with the ``note_uncompared`` call its body starts
  with (L12).

``candidate_surface`` combines them with the glue, the lock file and the
manifest's decoders.
"""
from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF_MODULE = "ve/backends/lean.py"
GLUE = ("lean/VE/Service/", "lean/Serve.lean")
LOCK = "lean/checkers.lock"


def _trees(sources: dict[str, str]):
    for path, text in sorted(sources.items()):
        if path.startswith("ve/") and path.endswith(".py"):
            yield path, ast.parse(text, filename=path)


def _called(node, name: str) -> bool:
    function = node.func if isinstance(node, ast.Call) else None
    return (isinstance(function, ast.Name) and function.id == name) or (
        isinstance(function, ast.Attribute) and function.attr == name)


def execute_calls(sources: dict[str, str]) -> dict[str, list[str]]:
    """``{path: [dispatch names]}`` for the modules outside ``ve/backends/``
    that call ``execute``; a first argument that is not a literal is ``None``."""
    found: dict[str, list[str]] = {}
    for path, tree in _trees(sources):
        if path.startswith("ve/backends/"):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _called(node, "execute") and node.args:
                first = node.args[0]
                found.setdefault(path, []).append(
                    first.value if isinstance(first, ast.Constant) and type(first.value) is str else None)
    return found


def handoff_functions(sources: dict[str, str]) -> list[str]:
    """The functions of ``ve/backends/lean.py`` decorated with ``_handoff``."""
    text = sources.get(HANDOFF_MODULE)
    if text is None:
        return []
    names = []
    for node in ast.parse(text).body:
        if isinstance(node, ast.FunctionDef) and any(
                (isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == "_handoff")
                or (isinstance(d, ast.Name) and d.id == "_handoff") for d in node.decorator_list):
            names.append(node.name)
    return names


def unmarked_process_starters(sources: dict[str, str]) -> list[str]:
    """Functions of ``ve/backends/lean.py`` other than ``run`` that start a
    process and are not handoffs: a statement-layer route reached past the
    ``lean-only`` record."""
    text = sources.get(HANDOFF_MODULE)
    if text is None:
        return []
    handoffs = set(handoff_functions(sources))
    starters = []
    for node in ast.parse(text).body:
        if isinstance(node, ast.FunctionDef) and node.name not in handoffs and node.name != "run":
            if any(isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                   and isinstance(call.func.value, ast.Name) and call.func.value.id == "subprocess"
                   for call in ast.walk(node)):
                starters.append(node.name)
    return starters


def handoff_modules(sources: dict[str, str]) -> dict[str, list[str]]:
    """``{path: [handoff names]}`` for the modules outside ``ve/backends/`` that
    call a handoff function."""
    names = set(handoff_functions(sources))
    found: dict[str, list[str]] = {}
    for path, tree in _trees(sources):
        if path.startswith("ve/backends/"):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and any(_called(node, name) for name in names):
                function = node.func
                found.setdefault(path, []).append(function.id if isinstance(function, ast.Name)
                                                  else function.attr)
    return found


def _calls_authority(node) -> str | None:
    """The literal operation of the first ``authority_for`` call in ``node``, or
    ``""`` for a call without one; None when there is no call."""
    for item in ast.walk(node):
        if isinstance(item, ast.Call) and _called(item, "authority_for"):
            first = item.args[0] if item.args else None
            return first.value if isinstance(first, ast.Constant) and type(first.value) is str else ""
    return None


def _reasons(node) -> list[str] | None:
    """The reason literals of a ``note_uncompared`` reason argument: a string, or
    a lambda whose body is a conditional expression over strings."""
    if isinstance(node, ast.Constant) and type(node.value) is str:
        return [node.value]
    if isinstance(node, ast.Lambda) and not node.args.args:
        body, found = node.body, []
        while isinstance(body, ast.IfExp):
            if not (isinstance(body.body, ast.Constant) and type(body.body.value) is str):
                return None
            found.append(body.body.value)
            body = body.orelse
        if isinstance(body, ast.Constant) and type(body.value) is str:
            return found + [body.value]
    return None


def static_branches(sources: dict[str, str]) -> list[dict]:
    """Every ``if`` whose test is a disjunction with a disjunct that calls
    ``authority_for`` and one that does not, and what its body starts with."""
    branches = []
    for path, tree in _trees(sources):
        if path.startswith("ve/backends/"):
            continue
        for node in ast.walk(tree):
            if not (isinstance(node, ast.If) and isinstance(node.test, ast.BoolOp)
                    and isinstance(node.test.op, ast.Or)):
                continue
            ops = [_calls_authority(value) for value in node.test.values]
            if all(op is None for op in ops) or not any(op is None for op in ops):
                continue
            first = node.body[0] if node.body else None
            call = first.value if isinstance(first, ast.Expr) else None
            note = None
            if isinstance(call, ast.Call) and _called(call, "note_uncompared") and len(call.args) == 2:
                op = call.args[0]
                note = {"op": op.value if isinstance(op, ast.Constant) else None,
                        "reasons": _reasons(call.args[1])}
            branches.append({"path": path, "line": node.lineno,
                             "op": next(op for op in ops if op is not None), "note": note})
    return branches


def uncompared_reasons_used(sources: dict[str, str]) -> dict[str, list[str]]:
    """``{reason: [path:line]}`` over every ``note_uncompared`` call in ``ve/``."""
    used: dict[str, list[str]] = {}
    for path, tree in _trees(sources):
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _called(node, "note_uncompared") and len(node.args) == 2:
                for reason in _reasons(node.args[1]) or ["<not a literal>"]:
                    used.setdefault(reason, []).append(f"{path}:{node.lineno}")
    return used


def candidate_surface(sources: dict[str, str], manifest: dict) -> tuple[set[str], tuple[str, ...]]:
    """The candidate surface (mig3.md 2.12) as exact files and path prefixes:
    the ``ve/`` modules with an ``execute`` call or a Lean-only handoff, the lock
    file and the manifest's ``lean_decoders``; ``ve/backends/`` and the glue are
    prefixes."""
    files = set(execute_calls(sources)) | set(handoff_modules(sources)) | {LOCK, GLUE[1]}
    files |= {entry["file"] for entry in manifest.get("lean_decoders", {}).get("files", ())}
    return files, ("ve/backends/", GLUE[0])


def on_surface(path: str, surface: tuple[set[str], tuple[str, ...]]) -> bool:
    files, prefixes = surface
    return path in files or any(path.startswith(prefix) for prefix in prefixes)


def classed(path: str, surface: tuple[set[str], tuple[str, ...]]) -> bool:
    """Whether a changed path is a classed path: the surface or any file under ``ve/``."""
    return path.startswith("ve/") or on_surface(path, surface)


def tree_sources(commit: str, root: Path = ROOT) -> tuple[dict[str, str], dict]:
    """The Python sources under ``ve/`` and the assurance manifest at ``commit``."""
    names = subprocess.run(["git", "ls-tree", "-r", "--name-only", commit, "--", "ve"], cwd=root,
                           check=True, capture_output=True, text=True).stdout.split()
    wanted = [name for name in names if name.endswith(".py")] + ["ve/assurance-manifest.json"]
    request = "".join(f"{commit}:{name}\n" for name in wanted).encode()
    output = subprocess.run(["git", "cat-file", "--batch"], cwd=root, input=request, check=True,
                            capture_output=True).stdout
    texts, offset = {}, 0
    for name in wanted:
        header_end = output.index(b"\n", offset)
        header = output[offset:header_end].split()
        if header[-1] == b"missing":
            offset = header_end + 1
            continue
        size = int(header[2])
        texts[name] = output[header_end + 1:header_end + 1 + size].decode()
        offset = header_end + 2 + size
    manifest_text = texts.pop("ve/assurance-manifest.json", "{}")
    return texts, json.loads(manifest_text)


def worktree_sources(root: Path = ROOT) -> tuple[dict[str, str], dict]:
    sources = {path.relative_to(root).as_posix(): path.read_text()
               for path in sorted((root / "ve").rglob("*.py"))}
    return sources, json.loads((root / "ve/assurance-manifest.json").read_text())
