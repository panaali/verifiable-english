"""Build a compact, deterministic index of source modules from the working tree.

The committed map is refreshed on merges. Branch checks are informational because
the map may intentionally lag source changes on a branch.
"""
from __future__ import annotations

import argparse
import ast
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path("docs/codemap")
SUFFIXES = {".py", ".lean", ".rs"}
SKIP_DIRECTORIES = {".git", ".lake", ".venv", "__pycache__", "target", "build", "dist", "node_modules"}
AREA_CAP = 12_000
INDEX_CAP = 16_000
MISSING = "(no module docstring)"


def first_sentence(value: str | None) -> str | None:
    if not value:
        return None
    value = " ".join(value.split())
    if not value:
        return None
    # Keep common abbreviation stops inside the sentence, including "e.g. item".
    for match in re.finditer(r"[.!?](?=\s|$)", value):
        if value[:match.end()].lower().endswith(("e.g.", "i.e.", "etc.", "mr.", "ms.", "dr.")):
            continue
        value = value[:match.end()]
        break
    return value[:159] + "…" if len(value) > 160 else value


def module_sentence(path: Path) -> str | None:
    try:
        source = path.read_text(encoding="utf-8")
        if path.suffix == ".py":
            return first_sentence(ast.get_docstring(ast.parse(source)))
        if path.suffix == ".lean":
            match = re.search(r"/-!(.*?)-/", source, re.DOTALL)
            return first_sentence(match.group(1)) if match else None
        lines = source.splitlines()
        docs: list[str] = []
        for line in lines:
            if line.lstrip().startswith("//!"):
                docs.append(line.lstrip()[3:])
            elif docs:
                break
        return first_sentence("\n".join(docs))
    except (OSError, UnicodeError, SyntaxError):
        return None


def source_files(root: Path) -> list[Path]:
    found: list[Path] = []
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted(name for name in dirs if name not in SKIP_DIRECTORIES and not name.startswith("."))
        current = Path(directory)
        if current == root:
            dirs[:] = [name for name in dirs if name not in {".git"}]
            continue  # top-level scripts are not package modules
        for name in sorted(files):
            path = current / name
            if path.suffix in SUFFIXES and not path.is_symlink():
                found.append(path.relative_to(root))
    return sorted(found)


def area_text(paths: list[Path], sentences: dict[Path, str | None]) -> str:
    return "".join(f"- `{path.as_posix()}` — {sentences[path] or MISSING}\n" for path in paths)


def area_groups(paths: list[Path], sentences: dict[Path, str | None]) -> list[tuple[str, list[Path]]]:
    groups: list[tuple[str, list[Path]]] = []

    def add(prefix: tuple[str, ...], subset: list[Path], *, force_split: bool = False) -> None:
        if not subset:
            return
        label = "/".join(prefix) + "/"
        if not force_split and len(area_text(subset, sentences).encode()) < AREA_CAP:
            groups.append((label, subset))
            return
        direct = [p for p in subset if len(p.parts) == len(prefix) + 1]
        children = sorted({p.parts[len(prefix)] for p in subset if len(p.parts) > len(prefix) + 1})
        if direct:
            chunk: list[Path] = []
            large = len(area_text(direct, sentences).encode()) >= AREA_CAP
            part = 1
            for path in direct:
                if chunk and len(area_text(chunk + [path], sentences).encode()) >= AREA_CAP:
                    groups.append((f"{label} part {part}" if large else label, chunk))
                    part += 1
                    chunk = []
                chunk.append(path)
            if chunk:
                groups.append((f"{label} part {part}" if large else label, chunk))
        for child in children:
            add((*prefix, child), [p for p in subset if p.parts[len(prefix)] == child])

    for top in sorted({p.parts[0] for p in paths}):
        subset = [p for p in paths if p.parts[0] == top]
        if top == "lean":
            direct = [p for p in subset if len(p.parts) == 2]
            add((top,), direct)
            for child in sorted({p.parts[1] for p in subset if len(p.parts) > 2}):
                add((top, child), [p for p in subset if len(p.parts) > 2 and p.parts[1] == child],
                    force_split=child == "VE")
        else:
            add((top,), subset)
    return groups


def area_description(root: Path, label: str) -> str:
    directory = root / label.split(" part ", 1)[0]
    for name in ("README.md", "__init__.py"):
        path = directory / name
        if path.is_file():
            if name.endswith(".py"):
                sentence = module_sentence(path)
            else:
                lines = [line.strip().lstrip("# ") for line in path.read_text(encoding="utf-8").splitlines()
                         if line.strip() and not line.startswith(("<!--", "[!"))]
                sentence = first_sentence(" ".join(lines[:2])) if lines else None
            if sentence:
                return sentence
    return "-"


def render(root: Path) -> tuple[dict[Path, str], list[Path]]:
    paths = source_files(root)
    sentences = {path: module_sentence(root / path) for path in paths}
    groups = area_groups(paths, sentences)
    result: dict[Path, str] = {}
    index = ["# Code map\n\n",
             "Service-mode routes: `tools/repo_map.py`. Regenerate with `python tools/code_map.py --write`.\n",
             "Regenerated on every merge to main; on a branch it may lag that branch's own changes.\n\n"]
    for label, members in groups:
        filename = label.rstrip("/").replace("/ part ", "--part-").replace("/", "__") + ".md"
        result[OUTPUT / filename] = area_text(members, sentences)
        index.append(f"- [{label}]({filename}) — {len(members)} modules — {area_description(root, label)}\n")
    result[OUTPUT / "INDEX.md"] = "".join(index)
    for path, content in result.items():
        cap = INDEX_CAP if path.name == "INDEX.md" else AREA_CAP
        if len(content.encode()) >= cap:
            raise ValueError(f"{path}: exceeds {cap} bytes")
    return result, [path for path in paths if sentences[path] is None]


def run(root: Path, mode: str) -> int:
    expected, missing = render(root)
    directory = root / OUTPUT
    if mode == "missing":
        for path in missing:
            print(path.as_posix())
        return 0
    actual = set(directory.glob("*.md")) if directory.is_dir() else set()
    names = {root / path for path in expected}
    if mode == "check":
        for path in sorted(actual | names):
            relative = path.relative_to(root)
            if path not in names or not path.is_file() or path.read_bytes() != expected[relative].encode():
                print(f"stale code map: {relative}")
                return 1
        return 0
    directory.mkdir(parents=True, exist_ok=True)
    for path in actual - names:
        path.unlink()
    for relative, content in expected.items():
        destination = root / relative
        if not destination.is_file() or destination.read_bytes() != content.encode():
            destination.write_text(content, encoding="utf-8", newline="\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    action.add_argument("--missing", action="store_true")
    args = parser.parse_args(argv)
    return run(ROOT, "write" if args.write else "check" if args.check else "missing")


if __name__ == "__main__":
    sys.exit(main())
