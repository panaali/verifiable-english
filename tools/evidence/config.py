"""`docs/<track>/<batch>/evidence.toml`: what a batch claims and where its evidence is.

    batch = "AR-5a"                      # the batch's name
    evidence = "evidence"                # the evidence directory, relative to the batch directory

    [scope]    file = "scope.json"       # python -m tools.evidence scope: main..HEAD --no-merges, saved
    [gate]     file = "gate.json"        # the tools/gate.py result of the final code commit (scope.head)
    [mutants]  file = "mutants.json"     # the seeded mutants and the tests they failed;  min = 3
    [ab]       file = "ab.json"          # python -m tools.evidence ab;  corpora = [...] (default: the seven)
    [latency]  file = "latency.json"     # python -m tools.evidence latency;  workloads = [...];  allowance = 0.2
    [fuzz_ab]  file = "fuzz-ab.json"     # python -m tools.evidence fuzz_ab;  seeds = [...];  [[fuzz_ab.explained]]
    [report]   file = "REPORT.md"        # a block rendered from the evidence;  marker = "...";  lines = [...]
    [[claims]] kind = "tally" ...        # tools/batch_evidence.py, CLAIMS

`scope`, `gate` and `mutants` are required; `ab` is required when the saved scope changes `ve/` or `lean/`.
A key the toolkit does not read is an error, not ignored: a misspelt section would otherwise check nothing.
Every path is relative to the batch directory and must stay inside the repository.
"""
from __future__ import annotations

from pathlib import Path
import tomllib

from tools.evidence import ROOT, EvidenceError

SECTIONS = {
    "scope": ({"file"}, {"file"}),
    "gate": ({"file"}, {"file"}),
    "mutants": ({"file"}, {"file", "min"}),
    "ab": ({"file"}, {"file", "corpora"}),
    "latency": ({"file", "workloads"}, {"file", "workloads", "allowance"}),
    "fuzz_ab": ({"file"}, {"file", "seeds", "explained"}),
    "report": ({"file", "marker", "lines"}, {"file", "marker", "lines"}),
}
TOP = {"batch", "evidence", "claims"} | SECTIONS.keys()
REQUIRED = ("batch", "scope", "gate", "mutants")


def read(directory: Path) -> dict:
    """The parsed `evidence.toml` of the batch at `directory`, its schema checked."""
    path = Path(directory) / "evidence.toml"
    if not path.is_file():
        raise EvidenceError(f"{path}: no evidence.toml")
    try:
        config = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as exc:
        raise EvidenceError(f"{path}: {exc}") from None
    errors = [f"unknown key {key!r}" for key in sorted(config.keys() - TOP)]
    errors += [f"missing {key!r}" for key in REQUIRED if key not in config]
    if not isinstance(config.get("batch", ""), str) or not config.get("batch", "x").strip():
        errors.append("batch is not a name")
    for name, (required, allowed) in SECTIONS.items():
        section = config.get(name)
        if section is None:
            continue
        if not isinstance(section, dict):
            errors.append(f"[{name}] is not a table")
            continue
        errors += [f"[{name}] misses {key!r}" for key in sorted(required - section.keys())]
        errors += [f"[{name}] has unknown key {key!r}" for key in sorted(section.keys() - allowed)]
        if not isinstance(section.get("file", ""), str):
            errors.append(f"[{name}] file is not a path")
    for key, kind in (("workloads", "latency"), ("lines", "report"), ("corpora", "ab"), ("seeds", "fuzz_ab")):
        value = config.get(kind, {}).get(key) if isinstance(config.get(kind), dict) else None
        if value is not None and (not isinstance(value, list) or not value
                                  or not all(isinstance(item, (str, int)) and str(item).strip() for item in value)):
            errors.append(f"[{kind}] {key} is not a non-empty list of names")
    if not isinstance(config.get("claims", []), list):
        errors.append("claims is not an array of tables")
    if errors:
        raise EvidenceError(f"{path}: " + "; ".join(errors))
    return config


def inside(directory: Path, relative: str) -> Path:
    """`relative` (from the toml) resolved against the batch directory, refused outside the repository."""
    path = (Path(directory) / relative).resolve()
    if path != ROOT and ROOT not in path.parents:
        raise EvidenceError(f"{relative} is outside the repository")
    return path


def evidence_dir(directory: Path, config: dict) -> Path:
    return inside(directory, config.get("evidence", "evidence"))
