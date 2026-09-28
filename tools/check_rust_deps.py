"""Check workspace crate dependencies against the inward-only rule."""
from __future__ import annotations

from pathlib import Path
import sys
import tomllib

from layer_policy import ROOT

WORKSPACE = ROOT / "rust"
CRATE_LAYERS = {"ve-core": 1, "ve": 4}


def dependencies(table: dict) -> list[tuple[str, object]]:
    result = []
    for name in ("dependencies", "dev-dependencies", "build-dependencies"):
        result.extend(table.get(name, {}).items())
    for target in table.get("target", {}).values():
        result.extend(dependencies(target))
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
    member_paths = {(WORKSPACE / member).resolve(): crate for crate, member in names.items()}
    workspace_deps = dict(dependencies(workspace.get("workspace", {})))
    for name, manifest in manifests.items():
        for alias, raw_spec in dependencies(manifest):
            spec = raw_spec if isinstance(raw_spec, dict) else {}
            if spec.get("workspace"):
                inherited = workspace_deps.get(alias)
                if inherited is None:
                    errors.append(f"missing workspace dependency: {name} -> {alias}")
                    continue
                spec = {**(inherited if isinstance(inherited, dict) else {}), **spec}
            dependency = spec.get("package", alias)
            if "path" in spec:
                base = WORKSPACE if raw_spec is not spec and isinstance(raw_spec, dict) and raw_spec.get("workspace") else WORKSPACE / names[name]
                target = (base / spec["path"]).resolve()
                if target not in member_paths:
                    errors.append(f"unmapped path dependency: {name} -> {alias}")
                elif member_paths[target] != dependency:
                    errors.append(f"mismatched path dependency: {name} -> {alias}")
                else:
                    dependency = member_paths[target]
            if dependency in names and CRATE_LAYERS.get(name, 0) < CRATE_LAYERS.get(dependency, 6):
                errors.append(f"outward crate dependency: {name} -> {dependency}")
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print(f"Rust crate graph kept ({len(names)} crates)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
