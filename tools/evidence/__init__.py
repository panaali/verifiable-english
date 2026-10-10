"""The evidence toolkit (docs/ARCHITECTURE-REVIEW-2026-10.md, T6 and AR-5a): one implementation of each batch
measurement, so a batch writes `docs/<track>/<batch>/evidence.toml` and runs these instead of copying scripts.

    python -m tools.evidence scope   --base main --out DIR/evidence/scope.json
    python -m tools.evidence latency ...      (tools/evidence/latency.py: paired CPU samples, the 20% rule)
    python -m tools.evidence ab      ...      (tools/evidence/ab.py: tools/lean_first_diff.py compare)
    python -m tools.evidence fuzz_ab ...      (tools/evidence/fuzz_ab.py: tools/difffuzz.py on both checkouts)
    python -m tools.evidence report  DIR      (tools/evidence/report.py: numbers rendered from the evidence)

`tools/batch_evidence.py --check DIR` reads the toml and the evidence; a batch's evidence is checked there, at
its gate and in the merge train, not by a permanent test (DRI decision D4). Every reader here goes through
`load`, which refuses what cannot show anything: a missing or empty file and a JSON object with a key twice
(two rows of one key collapse to the last in `json.loads`, the class of `docs/lean-first/b1/latency.py:57`).
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]


class EvidenceError(ValueError):
    """Evidence that cannot be read as the toolkit writes it."""


def _unique(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise EvidenceError(f"the key {key!r} occurs twice in one object")
        seen[key] = value
    return seen


def loads(text: str, name: str = "evidence"):
    """`text` as JSON, refusing an empty text and a duplicated key."""
    if not text.strip():
        raise EvidenceError(f"{name} is empty")
    try:
        return json.loads(text, object_pairs_hook=_unique)
    except EvidenceError as exc:
        raise EvidenceError(f"{name}: {exc}") from None
    except ValueError as exc:
        raise EvidenceError(f"{name} is not JSON: {exc}") from None


def load(path: Path):
    """The JSON file at `path` (gzip-compressed when it ends in `.gz`), read by `loads`."""
    path = Path(path)
    if not path.is_file():
        raise EvidenceError(f"{path}: no such evidence file")
    data = path.read_bytes()
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    return loads(data.decode(), str(path))


def killed(record) -> bool:
    """Whether a seeded-mutant record shows its named test failing: `killed` true with the tests that failed
    (`tools/mutants.py --evidence`), or a non-zero exit with a failure excerpt (the records batches kept before)."""
    if not isinstance(record, dict) or not isinstance(record.get("file"), str) or not record["file"]:
        return False
    if "killed" in record:
        return record["killed"] is True and bool(record.get("killed_by") or record.get("command"))
    return (type(record.get("exit_code")) is int and record["exit_code"] != 0
            and bool(record.get("test") or record.get("tests")) and bool(record.get("failure_excerpt")))


def dump(path: Path, value) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=1, sort_keys=True, ensure_ascii=False) + "\n")


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", "--no-optional-locks", "-c", "core.quotePath=false", *args], cwd=cwd,
                          check=True, capture_output=True, text=True).stdout


def scope(base: str, head: str = "HEAD", cwd: Path = ROOT) -> dict:
    """The saved scope of a batch: `base..head --no-merges` (merge base with `base`), its commits newest first
    and the lines each changed path adds and deletes, so a report reads numbers that later syncs cannot move."""
    head_sha = git("rev-parse", head, cwd=cwd).strip()
    base_sha = git("merge-base", base, head_sha, cwd=cwd).strip()
    if base_sha == head_sha:
        raise EvidenceError(f"{head} has no commit that {base} lacks")
    commits = [dict(zip(("hash", "subject"), line.split("\0", 1)))
               for line in git("log", "--no-merges", "--format=%H%x00%s", f"{base_sha}..{head_sha}",
                               cwd=cwd).splitlines()]
    changes = []
    for line in git("diff", "--numstat", "--no-renames", base_sha, head_sha, cwd=cwd).splitlines():
        added, deleted, path = line.split("\t", 2)
        changes.append({"path": path, "added": int(added) if added != "-" else 0,
                        "deleted": int(deleted) if deleted != "-" else 0})
    return {"base": base_sha, "head": head_sha, "commits": commits, "changes": changes}
