"""Check workspace crate dependencies against the inward-only rule."""
from __future__ import annotations

from pathlib import Path
import sys
import tomllib

from layer_policy import ROOT

WORKSPACE = ROOT / "rust"
CRATE_LAYERS = {"ve-core": 1, "ve": 4}


def dependencies(table: dict) -> set[str]:
    result = set()
    for name in ("dependencies", "dev-dependencies", "build-dependencies"):
        result.update(table.get(name, {}))
    for target in table.get("target", {}).values():
        result.update(dependencies(target))
    return result


def main() -> int:
    workspace = tomllib.loads((WORKSPACE / "Cargo.toml").read_text())
    members = workspace["workspace"]["members"]
    names = {}
    manifests = {}
    for member in members:
        path = WORKSPACE / member / "Cargo.toml"
        data = tomllib.loads(path.read_text())
        name = data["package"]["name"]
        names[name] = member
        manifests[name] = data
    errors = []
    if set(names) != set(CRATE_LAYERS):
        errors.append(f"unmapped crates: {sorted(set(names) ^ set(CRATE_LAYERS))}")
    for name, manifest in manifests.items():
        for dependency in sorted(dependencies(manifest) & names.keys()):
            if CRATE_LAYERS.get(name, 0) < CRATE_LAYERS.get(dependency, 6):
                errors.append(f"outward crate dependency: {name} -> {dependency}")
        for section in ("dependencies", "dev-dependencies", "build-dependencies"):
            for dependency, spec in manifest.get(section, {}).items():
                if isinstance(spec, dict) and "path" in spec:
                    target = (WORKSPACE / names[name] / spec["path"]).resolve()
                    if target not in {(WORKSPACE / member).resolve() for member in members}:
                        errors.append(f"unmapped path dependency: {name} -> {dependency}")
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print(f"Rust crate graph kept ({len(names)} crates)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
