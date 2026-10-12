"""The evidence toolkit (docs/ARCHITECTURE-REVIEW-2026-10.md, T6 and AR-5a): one implementation of each batch
measurement, so a batch writes `docs/<track>/<batch>/evidence.toml` and runs these instead of copying scripts.

    python -m tools.evidence scope   --base main --out DIR/evidence/scope.json
    python -m tools.evidence latency ...      (tools/evidence/latency.py: paired CPU samples, the 20% rule)
    python -m tools.evidence ab      ...      (tools/evidence/ab.py: tools/lean_first_diff.py compare)
    python -m tools.evidence fuzz_ab ...      (tools/evidence/fuzz_ab.py: tools/difffuzz.py on both checkouts)
    python -m tools.evidence mutants ...      (tools/mutants.py, the seeded-mutant harness, called as it is)
    python -m tools.evidence report  DIR      (tools/evidence/report.py: numbers rendered from the evidence)

`tools/batch_evidence.py --check DIR` reads the toml and the evidence; a batch's evidence is checked there, at
its gate and in the merge train, not by a permanent test (DRI decision D4). Every reader here goes through
`load`, which refuses what cannot show anything: a missing or empty file and a JSON object with a key twice
(two rows of one key collapse to the last in `json.loads`, the class of `docs/lean-first/b1/latency.py:57`).
Every file the toolkit opens goes through `read_bytes`, so `recording` lists each one for the check that it is
inside the repository and committed (arch-20261010-2 review F3).

Every A/B record names both commits it compared, taken from the two checkouts (`checkouts`), never typed:
`base_problems` refuses a record without its base, a head compared with itself (the lf-0 "compares nothing"
class) and, in a batch, a base other than the scope's merge base (review F2).
"""
from __future__ import annotations

from contextlib import contextmanager
import gzip
import json
from collections import defaultdict
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SHA = re.compile(r"[0-9a-f]{40}")
_RECORDINGS: list[list[Path]] = []


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


@contextmanager
def recording():
    """The resolved path of every file `read_bytes` opens inside the block, in order."""
    paths: list[Path] = []
    _RECORDINGS.append(paths)
    try:
        yield paths
    finally:
        _RECORDINGS.remove(paths)


def read_bytes(path: Path) -> bytes:
    """The bytes of the file at `path`, listed in every open `recording`; a missing file is an error."""
    path = Path(path)
    if not path.is_file():
        raise EvidenceError(f"{path}: no such evidence file")
    for paths in _RECORDINGS:
        paths.append(path.resolve())
    return path.read_bytes()


def load(path: Path):
    """The JSON file at `path` (gzip-compressed when it ends in `.gz`), read by `loads`."""
    path = Path(path)
    data = read_bytes(path)
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


def checkout_commit(root: Path) -> str:
    """The commit checked out at `root`; a tracked file changed since that commit is an error, because the
    measurement would then be of no commit."""
    try:
        if git("status", "--porcelain", "--untracked-files=no", cwd=root).strip():
            raise EvidenceError(f"{root} has uncommitted changes to tracked files")
        return git("rev-parse", "HEAD", cwd=root).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise EvidenceError(f"{root} is not a Git checkout: {exc}") from None


def checkouts(base_root: Path, head_root: Path) -> tuple[str, str]:
    """(base commit, head commit) of an A/B's two checkouts; one directory or one commit on both sides would
    compare the head with itself."""
    if Path(base_root).resolve() == Path(head_root).resolve():
        raise EvidenceError(f"the base and head checkouts are the same directory {base_root}")
    base, head = checkout_commit(base_root), checkout_commit(head_root)
    if base == head:
        raise EvidenceError(f"the base and head checkouts are both at {head}: the A/B would compare nothing")
    return base, head


def base_problems(record: dict, what: str, base: str | None = None) -> list[str]:
    """The errors of the base an A/B `record` names: its `base_commit` is a commit other than its
    `head_commit` and, when the batch's `base` is given (`batch_evidence --check`: the scope's merge base),
    that commit. Without `base` (the positional form, for records saved before the toolkit) a missing
    `base_commit` is not an error."""
    saved = record.get("base_commit")
    if base is None and saved is None:
        return []
    if not isinstance(saved, str) or not SHA.fullmatch(saved):
        return [f"{what} names no base commit"]
    if saved == record.get("head_commit"):
        return [f"{what} compared the head {saved} with itself"]
    if base is not None and saved != base:
        return [f"{what} ran on the base {saved}, not on the batch's merge base {base}"]
    return []


def scope_range(base_sha: str, head_sha: str, cwd: Path = ROOT) -> dict:
    """Commits and their added/deleted lines in a fixed `base..head --no-merges` range.

    Sum each non-merge commit's changes. A sync merge cannot add another batch's paths to these numbers.
    """
    if base_sha == head_sha:
        raise EvidenceError(f"{head_sha} has no commit that {base_sha} lacks")
    commits = [dict(zip(("hash", "subject"), line.split("\0", 1)))
               for line in git("log", "--no-merges", "--format=%H%x00%s", f"{base_sha}..{head_sha}",
                               cwd=cwd).splitlines()]
    totals = defaultdict(lambda: [0, 0])
    for commit in commits:
        for line in git("show", "--numstat", "--format=", "--no-renames", commit["hash"], cwd=cwd).splitlines():
            added, deleted, path = line.split("\t", 2)
            totals[path][0] += int(added) if added != "-" else 0
            totals[path][1] += int(deleted) if deleted != "-" else 0
    changes = [{"path": path, "added": values[0], "deleted": values[1]} for path, values in sorted(totals.items())]
    return {"base": base_sha, "head": head_sha, "commits": commits, "changes": changes}


def merge_base(head: str, main: str = "main", cwd: Path = ROOT) -> str:
    """The batch's merge base with `main`: the base its saved scope must start from.

    Before the batch is merged it is `git merge-base main head`. Once a merge commit on `main`'s first-parent
    history holds `head`, it is the merge base of that merge's first parent (`main` just before it) and
    `head`: the same commit, so a later merge to `main` does not move it.
    """
    try:
        head = git("rev-parse", "--verify", f"{head}^{{commit}}", cwd=cwd).strip()
        line = git("rev-list", "--first-parent", main, cwd=cwd).split()
    except subprocess.CalledProcessError as exc:
        raise EvidenceError(f"no merge base of {head} with {main}: {exc.stderr.strip()}") from None

    def holds(commit: str) -> bool:
        return subprocess.run(["git", "merge-base", "--is-ancestor", head, commit], cwd=cwd).returncode == 0

    if not line or not holds(line[0]):
        return git("merge-base", main, head, cwd=cwd).strip()
    low, high = 0, len(line) - 1  # line[low] holds head; find the oldest first-parent commit that does
    while low < high:
        middle = (low + high + 1) // 2
        low, high = (middle, high) if holds(line[middle]) else (low, middle - 1)
    if low + 1 == len(line) or line[low] == head or len(git("rev-list", "--parents", "-n1", line[low],
                                                            cwd=cwd).split()) < 3:
        raise EvidenceError(f"{head} reached {main} without a merge commit; name {main}'s commit before it "
                            "(--main) to find the batch's merge base")
    return git("merge-base", line[low + 1], head, cwd=cwd).strip()


def scope(base: str, head: str = "HEAD", cwd: Path = ROOT) -> dict:
    """The batch's scope from its merge base with `base`; save the fixed object IDs in the result."""
    head_sha = git("rev-parse", head, cwd=cwd).strip()
    base_sha = git("merge-base", base, head_sha, cwd=cwd).strip()
    return scope_range(base_sha, head_sha, cwd)
