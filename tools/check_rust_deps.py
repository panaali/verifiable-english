"""Check the Rust workspace's crate graph against the inward-only rule, as cargo reads it.

Since the crate split (plan R3) each library crate holds one layer, so the boundary is cargo's
crate graph and the check reads it from `cargo metadata --no-deps` instead of tokenizing Rust:
`ve-kernel` depends on no workspace crate, `ve-profile` only on `ve-kernel`, the `ve-core` facade
on both, and the `ve` binary may depend on all. Every dependency kind counts (normal, dev and
build, under any target), as cargo resolves it (workspace inheritance, renames, `package =`).
A path dependency must be a workspace member whose name is the declared one (`--no-deps` reports
both without resolving them; cargo's resolver rejects a mismatch), and every member must have a layer.

The facade holds no module of its own beyond its re-exports: its library directory holds only
`lib.rs`, and that file is in the plain layout of a re-export facade, read line by line and failing
closed on anything else: comments, lint attributes and inner doc comments, then `pub use` items
rooted at the facade's own dependencies (one name, or a braced list of names, as rustfmt writes it),
each optionally under `cfg(feature = "...")` and `doc(hidden)`. No Rust is tokenized: every line must
match one of these whole-line forms, ASCII outside comments, so no item, module, macro or `#[path]`
can be written in the facade.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from layer_policy import ROOT

WORKSPACE = ROOT / "rust"
# A crate may depend only on workspace crates of a lower layer.
CRATE_LAYERS = {"ve-kernel": 1, "ve-profile": 2, "ve-core": 3, "ve": 4}
FACADE = "ve-core"
# The whole-line forms of the facade's plain layout (see the module docstring).
IDENT = r"[A-Za-z_][A-Za-z0-9_]*"
NAMES = rf"{IDENT}(?:, {IDENT})*"
COMMENT = re.compile(r" *//[^\x00-\x08\x0a-\x1f\x7f]*")  # a line comment runs to the newline
INNER = re.compile(rf"#!\[(?:allow|deny|forbid|warn)\({IDENT}(?:, {IDENT})*\)\]|//![^\x00-\x08\x0a-\x1f\x7f]*")
OUTER = re.compile(r'#\[(?:cfg\(feature = "[A-Za-z0-9_-]+"\)|doc\(hidden\))\]')
USE = re.compile(rf"pub use (?P<root>{IDENT})(?:::{IDENT})*::(?:{IDENT}|\{{{NAMES}\}}|(?P<open>\{{))(?(open)|;)")
USE_NAMES = re.compile(rf"    {NAMES},")


def metadata(workspace: Path) -> dict:
    """The workspace's own packages as cargo reads them (no registry access)."""
    result = subprocess.run(["cargo", "metadata", "--format-version", "1", "--no-deps", "--offline",
                             "--manifest-path", str(workspace / "Cargo.toml")],
                            cwd=workspace, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise ValueError(f"cargo metadata failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def errors(data: dict) -> list[str]:
    """Outward crate edges, unmapped members and path dependencies, and modules in the facade."""
    ids = set(data["workspace_members"])
    members = [package for package in data["packages"] if package["id"] in ids]
    names = {package["name"] for package in members}
    found = []
    if names != set(CRATE_LAYERS):
        found.append(f"unmapped crates: {sorted(names ^ set(CRATE_LAYERS))}")
    folders = {Path(package["manifest_path"]).parent.resolve(): package["name"] for package in members}
    for package in members:
        name = package["name"]
        for dependency in package["dependencies"]:
            targets = [dependency["name"]]  # the package cargo looks for, after any `package =`
            if dependency.get("path") is not None:
                alias = dependency.get("rename") or dependency["name"]  # the manifest's key
                reached = folders.get(Path(dependency["path"]).resolve())
                if reached is None:
                    found.append(f"path dependency outside the workspace: {name} -> {alias}")
                    continue
                if reached != dependency["name"]:
                    found.append(f"mismatched path dependency: {name} -> {alias}")
                    targets.insert(0, reached)
            for target in targets:
                if target in names and CRATE_LAYERS.get(name, 0) <= CRATE_LAYERS.get(target, len(CRATE_LAYERS) + 1):
                    found.append(f"outward crate dependency: {name} -> {target}")
    for package in members:
        if package["name"] != FACADE:
            continue
        libraries = [target for target in package["targets"] if "lib" in target["kind"]]
        if not libraries:
            found.append(f"the {FACADE} facade has no library target")
        roots = {(dependency.get("rename") or dependency["name"]).replace("-", "_")
                 for dependency in package["dependencies"] if dependency["kind"] is None}
        for library in libraries:
            entry = Path(library["src_path"])
            found += [f"module in the {FACADE} facade: {path.relative_to(entry.parent).as_posix()}; "
                      f"add it to ve-kernel or ve-profile and re-export it from {FACADE}"
                      for path in sorted(entry.parent.rglob("*.rs")) if path != entry]
            found += facade_errors(entry.read_bytes(), roots)
    return list(dict.fromkeys(found))


def facade_errors(source: bytes, roots: set[str]) -> list[str]:
    """The first line of the facade's `lib.rs` outside its plain layout, if any (see the module docstring)."""
    lines = source.decode("utf-8", errors="replace").split("\n")
    items = False  # inner attributes come before the first item
    attributes = block = False  # inside an item: after its attributes, or in its braced list of names
    for number, line in enumerate(lines, 1):
        use = USE.fullmatch(line)
        if block:
            kept = USE_NAMES.fullmatch(line) or COMMENT.fullmatch(line) or line == "};"
            block = line != "};"
        elif use:
            kept, items, attributes, block = use["root"] in roots, True, False, bool(use["open"])
        elif OUTER.fullmatch(line):
            kept = items = attributes = True
        else:
            kept = not attributes and (line == "" or COMMENT.fullmatch(line) or (not items and INNER.fullmatch(line)))
        if not kept or "\r" in line or "\ufffd" in line:
            return [f"line {number} of the {FACADE} facade is not part of a re-export: {line!r}; the facade holds "
                    f"only `pub use` items of {', '.join(sorted(roots)) or 'its dependencies'} (one name or a "
                    "braced list, under `cfg(feature)` and `doc(hidden)` attributes), lint attributes and comments"]
    return [f"line {len(lines)} of the {FACADE} facade is not part of a re-export: the file ends inside an item"] \
        if block or attributes else []


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv or [])
    try:
        found = errors(metadata(WORKSPACE))
    except (OSError, ValueError) as error:
        found = [f"cannot read the Rust workspace: {error}"]
    for error in found:
        print(error, file=sys.stderr)
    if found:
        return 1
    print(f"Rust crate graph kept ({len(CRATE_LAYERS)} crates; {FACADE} re-exports only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
