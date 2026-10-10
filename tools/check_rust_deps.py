"""Check the Rust workspace's crate graph against the inward-only rule, as cargo reads it.

Since the crate split (plan R3) each library crate holds one layer, so the boundary is cargo's
crate graph and the check reads it from `cargo metadata --no-deps` instead of tokenizing Rust:
`ve-kernel` depends on no workspace crate, `ve-profile` only on `ve-kernel`, the `ve-core` facade
on both, and the `ve` binary may depend on all. Every dependency kind counts (normal, dev and
build, under any target), as cargo resolves it (workspace inheritance, renames, `package =`).
A path dependency must be a workspace member, and every member must have a layer.

The facade holds no module of its own beyond its re-exports: its library directory holds only
`lib.rs`. Code in that `lib.rs` sits above both library crates, so cargo bounds what it can reach.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from layer_policy import ROOT

WORKSPACE = ROOT / "rust"
# A crate may depend only on workspace crates of a lower layer.
CRATE_LAYERS = {"ve-kernel": 1, "ve-profile": 2, "ve-core": 3, "ve": 4}
FACADE = "ve-core"


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
            target = dependency["name"]
            if dependency.get("path") is not None:
                target = folders.get(Path(dependency["path"]).resolve())
                if target is None:
                    alias = dependency.get("rename") or dependency["name"]  # the manifest's key
                    found.append(f"path dependency outside the workspace: {name} -> {alias}")
                    continue
            if target in names and CRATE_LAYERS.get(name, 0) <= CRATE_LAYERS.get(target, len(CRATE_LAYERS) + 1):
                found.append(f"outward crate dependency: {name} -> {target}")
    for package in members:
        if package["name"] != FACADE:
            continue
        libraries = [target for target in package["targets"] if "lib" in target["kind"]]
        if not libraries:
            found.append(f"the {FACADE} facade has no library target")
        for library in libraries:
            entry = Path(library["src_path"])
            found += [f"module in the {FACADE} facade: {path.relative_to(entry.parent).as_posix()}; "
                      f"add it to ve-kernel or ve-profile and re-export it from {FACADE}"
                      for path in sorted(entry.parent.rglob("*.rs")) if path != entry]
    return list(dict.fromkeys(found))


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
