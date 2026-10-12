#!/usr/bin/env python3
"""The gate's test collection, checked against the merge base's.

`tools/gate.py` collects the head's tests and compares them with the collection of the merge base: the
record a gate attached to the base as the git note NOTES_REF, or, when the base has none, a collection of
the base in a scratch worktree (whose record is then attached, so the next gate on that base reads it).
A test the head collects and the base did not is fine. A base ID the head no longer collects fails unless a
commit in base..head carries a removal record for it, the trailer

    Test-removed: <the test ID, or its function, class or file> — <why it goes>

so a reviewer reads every lost ID with the batch. A trailer that names a deleted function, class or file covers
all of its IDs, and fails as stale if the head still collects any of them, as does a trailer naming an ID
the head still collects. A trailer without a target and a reason fails too.

`git diff --no-renames base..head` only labels each removal (`Changes.label`), it never authorises one:

* the diff deletes its file;
* the diff deletes its test function, or a class the ID names, read from both sides with `ast`;
* the diff changes the function's parametrisation (`parametrisation`): the decorators of the function and
  of each class the ID names, the classes' bases, the module's `pytestmark` and `pytest_generate_tests`,
  the decorators of the module's fixtures the function takes, and every module-level statement those
  name, transitively;
* none of these: a `conftest.py` that deselects or ignores it, or a parameter list that shrinks while its
  source in the test module is unchanged (a data file, a glob, an imported list).

A module that no longer imports or is skipped at collection is a collection report, which fails on its own
as well. Every head collection is attached as the record of its commit.

Run from the checkout after `(cd lean && lake build)`, to see what the gate will say:
    uv run python tools/gate_collection.py --check [--base REV] [--prebuilt]
"""
from __future__ import annotations

import argparse
import ast
import base64
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import nested_pytest  # noqa: E402

# The gate record includes its collection, bound to the commit and its tree.
NOTES_REF = "refs/notes/ve-gate-result"
FORMAT = "ve-gate-result@1"
MAX_IDS_BYTES = 16 * 1024 * 1024
# The Rust release binary the tests load (ve/backends/rust_jsonl.py), relative to a checkout.
RUST_BINARY = "rust/target/release/ve"
# The branch whose merge base the gate compares with, unless it is given one.
MAIN = "main"
# Variables the collection inherits; pytest options and plugins never do.
INHERITED = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR")
# Every git command: no lock taken on a read, paths unquoted, and the note's author fixed (the gate's HOME
# has no git identity).
GIT = ("git", "--no-optional-locks", "-c", "core.quotePath=false", "-c", "user.name=ve gate",
       "-c", "user.email=ve-gate@localhost")
# The removal record: a commit trailer `TRAILER: <target>SEPARATOR<reason>`. pytest escapes non-ASCII in IDs,
# so an ID never holds the separator and the first one ends the target.
TRAILER = "Test-removed"
SEPARATOR = " — "
# The label of a removal the diff neither deletes nor re-parametrises.
UNLABELLED = "the diff neither deletes its file, function or class nor changes its parametrisation"


class CollectionError(RuntimeError):
    """The collection itself is incomplete, so no expectation may be taken from it."""


def collection_command(python: list[str], files: list[str] | None = None) -> list[str]:
    from tools import gate
    return gate.collection_command(python, files)


def collect(root: Path = ROOT, *, prebuilt: bool = False, python: list[str] | None = None,
            env: dict[str, str] | None = None) -> list[str]:
    """The IDs the gate's plugin records as collected in `root`, in collection order. `env` (default: INHERITED
    from this process) gets `root` as PYTHONPATH, so `root`'s own sources are imported."""
    with tempfile.TemporaryDirectory(prefix="ve-gate-collection-") as directory:
        output = Path(directory) / "events.json"
        base = {name: os.environ[name] for name in INHERITED if name in os.environ} if env is None else dict(env)
        # Bytecode is checked only against its source's size and whole-second
        # mtime, so a same-size edit within the second would load the earlier
        # source. An empty cache, never the tree's __pycache__, compiles it fresh.
        base.update(PYTHONPATH=str(root), PYTHONPYCACHEPREFIX=str(Path(directory) / "pycache"))
        if prebuilt:
            # Inside a running suite, whose session holds the shared build lock.
            base["VE_NATIVE_PREBUILT"] = "1"
        run = subprocess.run(collection_command(python or [sys.executable]), cwd=root,
                             env=nested_pytest.environment(base, VE_GATE_PYTEST_RESULT=str(output)),
                             text=True, capture_output=True)
        events = json.loads(output.read_text()) if output.exists() else None
    if events and events["collection_reports"]:
        # A module skipped or broken at collection drops its IDs without a trace.
        raise CollectionError("collection reports: " + json.dumps(events["collection_reports"])[:4000])
    if run.returncode not in (0, 5) or events is None:
        raise CollectionError(f"collection failed (exit {run.returncode}):\n"
                              f"{run.stdout[-4000:]}{run.stderr[-4000:]}")
    if len(events["collected"]) != len(set(events["collected"])):
        raise CollectionError("duplicate test ID in collection")
    return events["collected"]


def git(args: list[str], *, cwd: Path = ROOT, env: dict[str, str] | None = None, check: bool = True,
        stdin: bytes | None = None) -> subprocess.CompletedProcess:
    run = subprocess.run([*GIT, *args], cwd=cwd, env=env, input=stdin, capture_output=True)
    if check and run.returncode:
        raise RuntimeError(f"git {' '.join(args)}: exit {run.returncode}: {run.stderr.decode(errors='replace')}")
    return run


def rev(name: str, *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> str:
    return git(["rev-parse", "--verify", "--end-of-options", name], cwd=cwd, env=env).stdout.decode().strip()


def merge_base(head: str = "HEAD", *, main: str = MAIN, cwd: Path = ROOT,
               env: dict[str, str] | None = None) -> str:
    """The commit the head is compared with: its merge base with `main`, or, on `main` itself, its first
    parent."""
    head = rev(f"{head}^{{commit}}", cwd=cwd, env=env)
    base = git(["merge-base", head, main], cwd=cwd, env=env).stdout.decode().strip()
    return rev(f"{head}^1", cwd=cwd, env=env) if base == head else base


# --- the record -------------------------------------------------------------------------------------------

def encode_ids(ids: list[str]) -> str:
    """Compact, deterministic representation of the collected IDs in the gate record."""
    raw = json.dumps(sorted(ids), ensure_ascii=True, separators=(",", ":")).encode()
    return base64.b64encode(zlib.compress(raw, 9)).decode("ascii")


def decode_ids(encoded: str) -> list[str] | None:
    if type(encoded) is not str:
        return None
    try:
        compressed = base64.b64decode(encoded, validate=True)
        decoder = zlib.decompressobj()
        raw = decoder.decompress(compressed, MAX_IDS_BYTES + 1)
        if len(raw) > MAX_IDS_BYTES or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
            return None
        ids = json.loads(raw)
    except (ValueError, zlib.error, UnicodeDecodeError):
        return None
    if not isinstance(ids, list) or not ids or not all(type(nodeid) is str for nodeid in ids) \
            or ids != sorted(set(ids)):
        return None
    return ids


def record_text(commit: str, tree: str, ids: list[str], result: dict | None = None) -> str:
    record = dict(result or {})
    record.update(format=FORMAT, commit_sha=commit, tree_sha=tree)
    record["collection"] = {**record.get("collection", {}), "collected_zlib": encode_ids(ids)}
    return json.dumps(record, indent=1) + "\n"


def parse_record(text: str, commit: str, tree: str) -> list[str] | None:
    """The IDs of a gate record bound to `commit` and `tree`, or None if malformed."""
    try:
        record = json.loads(text)
    except ValueError:
        return None
    if not isinstance(record, dict) or record.get("format") != FORMAT \
            or record.get("commit_sha") != commit or record.get("tree_sha") != tree:
        return None
    collection = record.get("collection")
    if not isinstance(collection, dict) or "collected_zlib" not in collection:
        return None
    return decode_ids(collection["collected_zlib"])


def read_record(commit: str, *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> list[str] | None:
    """The collection recorded for `commit`, or None when it has no valid record."""
    shown = git(["notes", f"--ref={NOTES_REF}", "show", commit], cwd=cwd, env=env, check=False)
    if shown.returncode:
        return None
    return parse_record(shown.stdout.decode(errors="replace"), commit, rev(f"{commit}^{{tree}}", cwd=cwd, env=env))


def read_gate_result(commit: str, *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> dict | None:
    """A full gate result from its note, if one is present and its collection is valid."""
    shown = git(["notes", f"--ref={NOTES_REF}", "show", commit], cwd=cwd, env=env, check=False)
    if shown.returncode:
        return None
    text = shown.stdout.decode(errors="replace")
    if parse_record(text, commit, rev(f"{commit}^{{tree}}", cwd=cwd, env=env)) is None:
        return None
    record = json.loads(text)
    if "status" not in record:  # a base-only record, before that commit's gate
        return None
    return {key: value for key, value in record.items() if key != "format"}


def recorded(commit: str, *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> tuple[str, list[str]] | None:
    """(the commit whose record is used, its IDs): `commit`'s own record or that of a parent with the same
    tree (a merge commit and the gated branch head it merged), or None."""
    tree = rev(f"{commit}^{{tree}}", cwd=cwd, env=env)
    parents = git(["rev-list", "--parents", "-n", "1", commit], cwd=cwd, env=env).stdout.decode().split()[1:]
    for candidate in [commit, *parents]:
        if candidate == commit or rev(f"{candidate}^{{tree}}", cwd=cwd, env=env) == tree:
            ids = read_record(candidate, cwd=cwd, env=env)
            if ids is not None:
                return candidate, ids
    return None


def write_record(commit: str, ids: list[str], *, result: dict | None = None, cwd: Path = ROOT,
                 env: dict[str, str] | None = None) -> None:
    """Attach the gate result with its IDs as the record of `commit`."""
    text = record_text(commit, rev(f"{commit}^{{tree}}", cwd=cwd, env=env), ids, result)
    git(["notes", f"--ref={NOTES_REF}", "add", "-f", "-F", "-", commit], cwd=cwd, env=env, stdin=text.encode())


def build(args: list[str], *, cwd: Path, env: dict[str, str], what: str) -> None:
    done = subprocess.run(args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if done.returncode:
        raise CollectionError(f"{what}: exit {done.returncode}:\n{done.stdout[-4000:]}")


def build_rust(tree: Path, root: Path, build_env: dict[str, str]) -> None:
    """The release binary `tree`'s tests load: `root`'s when `tree`'s lock pins it, else built in `tree` from a
    copy of `root`'s target directory, offline, with the gate's path remapping (tools/rust_build.py)."""
    from tools import rust_build
    binary, lock = root / RUST_BINARY, tree / "lean/checkers.lock"
    (tree / RUST_BINARY).parent.mkdir(parents=True, exist_ok=True)
    if binary.is_file() and lock.is_file() and rust_build.digest(binary) in rust_build.pinned_digests(lock):
        shutil.copy2(binary, tree / RUST_BINARY)
        return
    if (root / "rust/target").is_dir():
        shutil.copytree(root / "rust/target", tree / "rust/target", symlinks=True, dirs_exist_ok=True)
    cargo_home = Path(build_env.get("CARGO_HOME") or root / ".cargo-home")
    env = {**build_env, "CARGO_HOME": str(cargo_home), "CARGO_NET_OFFLINE": "true",
           "CARGO_ENCODED_RUSTFLAGS": rust_build.encoded_rustflags(root=tree, cargo_home=cargo_home,
                                                                   target_dir=tree / "rust/target")}
    build(["cargo", "build", "--target-dir", str(tree / "rust/target"), "--locked", "--release",
           "--manifest-path", str(tree / "rust/Cargo.toml")], cwd=tree, env=env, what="cargo build of the base")


def collect_commit(commit: str, scratch: Path, *, build_env: dict[str, str], env: dict[str, str],
                   python: list[str], root: Path = ROOT) -> list[str]:
    """The collection of `commit`, in a scratch worktree of it under `scratch`: its Lean build is `root`'s
    copied and rebuilt there (`lake` from `build_env`), its Rust binary `build_rust`'s, and its tests collected
    by `python` in `env`."""
    tree = scratch / "base-worktree"
    git(["worktree", "add", "--detach", str(tree), commit], cwd=root, env=build_env)
    try:
        for name in ("lean/lean-toolchain", "rust-toolchain.toml"):
            pins = [(side / name).read_bytes() if (side / name).is_file() else None for side in (tree, root)]
            if pins[0] != pins[1]:
                raise CollectionError(f"the base {commit} pins another toolchain in {name}: collect it with its "
                                      "own toolchain")
        if (tree / "lean/lakefile.toml").is_file():
            # Lake rebuilds only what differs from the head's build: its traces are of content.
            if (root / "lean/.lake").is_dir():
                shutil.copytree(root / "lean/.lake", tree / "lean/.lake", symlinks=True)
            build(["lake", "build"], cwd=tree / "lean", env=build_env, what=f"lake build of the base {commit}")
        if (tree / "rust/Cargo.toml").is_file():
            build_rust(tree, root, build_env)
        return collect(tree, python=python, env=env)
    finally:
        git(["worktree", "remove", "--force", str(tree)], cwd=root, env=build_env, check=False)
        shutil.rmtree(tree, ignore_errors=True)
        git(["worktree", "prune"], cwd=root, env=build_env, check=False)


# --- the rule ---------------------------------------------------------------------------------------------

def _defined(statement: ast.stmt) -> set[str]:
    """The module-level names a statement binds."""
    if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {statement.name}
    if isinstance(statement, (ast.Import, ast.ImportFrom)):
        return {(alias.asname or alias.name).split(".")[0] for alias in statement.names}
    targets = (statement.targets if isinstance(statement, ast.Assign) else
               [statement.target] if isinstance(statement, (ast.AnnAssign, ast.AugAssign)) else [])
    return {node.id for target in targets for node in ast.walk(target) if isinstance(node, ast.Name)}


def _names(nodes) -> set[str]:
    return {node.id for root in nodes for node in ast.walk(root) if isinstance(node, ast.Name)}


def _locate(module: ast.Module, names: list[str]) -> list[ast.AST]:
    """The class and function definitions an ID names, outermost first, as far as they are found."""
    found, body = [], module.body
    for index, name in enumerate(names):
        kinds = (ast.FunctionDef, ast.AsyncFunctionDef) if index == len(names) - 1 else (ast.ClassDef,)
        matches = [node for node in body if isinstance(node, kinds) and node.name == name]
        if not matches:
            break
        found.append(matches[-1])  # a later definition replaces an earlier one
        body = matches[-1].body if isinstance(matches[-1], ast.ClassDef) else []
    return found


def parametrisation(module: ast.Module, path: list[ast.AST]) -> list[str]:
    """What fixes a test function's parameters within its module, as AST dumps in source order: the
    decorators of the function and of each class around it, those classes' bases and keywords, the module's
    `pytestmark` and `pytest_generate_tests`, the decorators of the module's fixtures the function takes, and
    every module-level statement those name, transitively."""
    statements = {}
    for statement in module.body:
        for name in _defined(statement):
            statements.setdefault(name, []).append(statement)
    roots: list[ast.AST] = []
    for node in path:
        roots += node.decorator_list
        if isinstance(node, ast.ClassDef):
            roots += [*node.bases, *node.keywords]
    function = path[-1]
    arguments = {argument.arg for argument in [*function.args.posonlyargs, *function.args.args,
                                              *function.args.kwonlyargs]}
    for name in arguments:
        for statement in statements.get(name, []):
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)) and statement.decorator_list:
                roots += statement.decorator_list
    included = {id(statement): statement for name in ("pytestmark", "pytest_generate_tests")
                for statement in statements.get(name, [])}
    pending = _names([*roots, *included.values()])
    seen = set()
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        for statement in statements.get(name, []):
            if id(statement) not in included:
                included[id(statement)] = statement
                pending |= _names([statement])
    order = {id(statement): index for index, statement in enumerate(module.body)}
    return ([ast.dump(root) for root in roots]
            + [ast.dump(statement) for statement in sorted(included.values(), key=lambda s: order[id(s)])])


@dataclass(frozen=True)
class Removal:
    """A `Test-removed:` trailer: the ID, or the function, class or file whose IDs it covers, and why."""
    target: str
    reason: str
    commit: str

    def covers(self, nodeid: str) -> bool:
        return nodeid == self.target or nodeid.startswith((self.target + "::", self.target + "["))


def parse_trailer(value: str, commit: str) -> Removal | None:
    """The removal a trailer's value records, or None unless it is `<target> — <reason>`, both non-empty."""
    target, separator, reason = value.partition(SEPARATOR)
    if not separator or not target.strip() or target != target.strip() or not reason.strip():
        return None
    return Removal(target, reason.strip(), commit)


def removal_records(base: str, head: str, *, root: Path = ROOT,
                    env: dict[str, str] | None = None) -> tuple[list[Removal], list[dict]]:
    """(the removals the `Test-removed:` trailers of base..head record, oldest first; each trailer that is not
    one, with its commit). Git parses the trailers."""
    # Each trailer as `<key>: <value>`, so a commit without one is the only empty item.
    out = git(["log", "--reverse", f"--format=%H%x1f%(trailers:key={TRAILER},unfold,separator=%x1f)%x1e",
               f"{base}..{head}", "--"], cwd=root, env=env).stdout.decode()
    removals, malformed = [], []
    for entry in out.split("\x1e"):
        commit, *trailers = entry.strip("\n").split("\x1f")
        for trailer in trailers if commit else []:
            if not trailer:
                continue
            value = trailer.partition(":")[2].strip()
            removal = parse_trailer(value, commit)
            if removal is None:
                malformed.append({"commit": commit, "trailer": value})
            else:
                removals.append(removal)
    return removals, malformed


@dataclass
class Changes:
    """What base..head does to the tests: the files `git diff --no-renames` changes (`head` None: the worktree
    at `root`), and the removal records of its commits (up to HEAD for the worktree)."""
    base: str
    head: str | None
    statuses: dict[str, str]
    root: Path = ROOT
    env: dict[str, str] | None = None
    removals: list[Removal] = field(default_factory=list)
    malformed: list[dict] = field(default_factory=list)
    _modules: dict = field(default_factory=dict)

    def module(self, side: str, path: str) -> ast.Module | None:
        key = (side, path)
        if key not in self._modules:
            if side == "head" and self.head is None:
                source = (self.root / path).read_bytes()
            else:
                source = git(["show", f"{self.base if side == 'base' else self.head}:{path}"],
                             cwd=self.root, env=self.env).stdout
            try:
                self._modules[key] = ast.parse(source, filename=path)
            except (SyntaxError, ValueError):
                self._modules[key] = None
        return self._modules[key]

    def _definitions(self, nodeid: str):
        """(path, names, base module, head module, the definitions the ID names on each side) for an ID in a
        changed, not deleted, test module that parses on both sides; else None."""
        path, _, rest = nodeid.partition("::")
        if self.statuses.get(path) in (None, "D") or not (path.endswith(".py") and rest):
            return None
        names = rest.split("[", 1)[0].split("::")
        base, head = self.module("base", path), self.module("head", path)
        if base is None or head is None:
            return None
        return path, names, base, head, _locate(base, names), _locate(head, names)

    def deleted(self, nodeid: str) -> str | None:
        """The ID's file, or its function or a class it names (as an ID prefix), when the diff deletes it."""
        path = nodeid.partition("::")[0]
        if self.statuses.get(path) == "D":
            return path
        found = self._definitions(nodeid)
        if found is None or len(found[5]) >= len(found[4]):
            return None
        return "::".join([path, *found[1][:len(found[5]) + 1]])

    def label(self, nodeid: str) -> str:
        """What the diff did to the base's `nodeid`, for the gate's report; it never authorises a removal."""
        if self.statuses.get(nodeid.partition("::")[0]) == "D":
            return "its file is deleted"
        found = self._definitions(nodeid)
        if found is None:
            return UNLABELLED
        _, names, base, head, before, after = found
        if len(after) < len(before):
            kind = "test function" if len(after) == len(names) - 1 else "class"
            return f"its {kind} {names[len(after)]} is deleted"
        if len(before) < len(names):
            return UNLABELLED  # not defined in its module at the base (inherited or generated): nothing to compare
        if parametrisation(base, before) != parametrisation(head, after):
            return f"the parametrisation of {names[-1]} changed"
        return UNLABELLED


def changes(base: str, head: str | None = "HEAD", *, root: Path = ROOT,
            env: dict[str, str] | None = None) -> Changes:
    """The changes `git diff --no-renames base..head` makes (a rename is a deletion and an addition), with the
    removal records of base..head (base..HEAD for the worktree, whose edits carry none)."""
    sides = [base] if head is None else [base, head]
    out = git(["diff", "--no-renames", "--name-status", "-z", *sides, "--"], cwd=root, env=env).stdout.decode()
    fields = out.split("\0")
    statuses = {fields[index + 1]: fields[index][0] for index in range(0, len(fields) - 1, 2)}
    tip = rev(f"{head or 'HEAD'}^{{commit}}", cwd=root, env=env)
    removals, malformed = removal_records(base, tip, root=root, env=env)
    return Changes(base, None if head is None else tip, statuses, root, env, removals, malformed)


@dataclass
class Verdict:
    """The head's collection against the base's."""
    removed: dict[str, dict]  # each base ID the head lacks that a trailer covers: its label, reason and commit
    refused: dict[str, str]  # each base ID the head lacks that no trailer covers: its label
    stale: list[dict]  # each trailer covering an ID the head still collects
    malformed: list[dict]  # each trailer that is not `<target> — <reason>`
    suggested: list[str]  # a trailer target for each refused ID: its deleted file, class or function, or itself

    def failed(self) -> bool:
        return bool(self.refused or self.stale or self.malformed)

    def record(self) -> dict:
        return {"removed": self.removed, "refused": self.refused, "stale": self.stale, "malformed": self.malformed}


def missing(expected: list[str], collected: list[str], diff: Changes | None) -> Verdict:
    """Each base ID the head lacks, removed by a trailer or refused, and each trailer that is stale or malformed.
    Without `diff`, every lost ID is refused unlabelled."""
    removals = diff.removals if diff else []
    head = set(collected)
    removed, refused, suggested = {}, {}, []
    for nodeid in sorted(set(expected) - head):
        label = diff.label(nodeid) if diff else UNLABELLED
        deleted = diff.deleted(nodeid) if diff else None
        # A prefix records its definition's deletion, not a changed parameter
        # list or collection rule on a definition that still exists.
        removal = next((removal for removal in removals if removal.covers(nodeid) and
                        (removal.target == nodeid or removal.target == deleted)), None)
        if removal is None:
            refused[nodeid] = label
            # A deleted file's or function's trailer, unless the head still collects an ID it would cover.
            if deleted in suggested or deleted and not any(Removal(deleted, "", "").covers(other) for other in head):
                nodeid = deleted
            if nodeid not in suggested:
                suggested.append(nodeid)
        else:
            removed[nodeid] = {"label": label, "reason": removal.reason, "commit": removal.commit}
    stale = []
    for removal in removals:
        still = next((nodeid for nodeid in collected if removal.covers(nodeid)), None)
        if still is not None:
            stale.append({"target": removal.target, "commit": removal.commit, "collected": still})
    return Verdict(removed, refused, stale, list(diff.malformed) if diff else [], suggested)


def difference_text(base: str, verdict: Verdict) -> str:
    """The gate's failure: every base ID the head lacks without a removal record, with the diff's label, and
    every stale or malformed trailer."""
    at = f"the merge base {base}" if base else "the merge base"
    lines = []
    if verdict.refused:
        lines.append(f"{len(verdict.refused)} tests collected at {at} are not collected here, and no "
                     f"`{TRAILER}:` trailer since it names them:")
        lines.extend(f"  {nodeid}  ({label})" for nodeid, label in verdict.refused.items())
        lines.append(f"Restore them, or record each removal in a commit message trailer (one per deleted file, "
                     f"class or function covers its IDs), saying why it goes:")
        lines.extend(f"  {TRAILER}: {target}{SEPARATOR}<why>" for target in verdict.suggested)
    if verdict.stale:
        lines.append(f"{len(verdict.stale)} `{TRAILER}:` trailers name tests still collected here:")
        lines.extend(f"  {row['target']} (commit {row['commit'][:12]}) covers {row['collected']}"
                     for row in verdict.stale)
    if verdict.malformed:
        lines.append(f"{len(verdict.malformed)} `{TRAILER}:` trailers are not `<test ID>{SEPARATOR}<reason>`:")
        lines.extend(f"  commit {row['commit'][:12]}: {row['trailer']}" for row in verdict.malformed)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", required=True,
                        help="compare the worktree's collection with the merge base's")
    parser.add_argument("--base", help=f"the commit to compare with (default: the merge base with {MAIN})")
    parser.add_argument("--prebuilt", action="store_true",
                        help="skip the suite's native build (run `(cd lean && lake build)` first)")
    args = parser.parse_args()
    try:
        base = rev(f"{args.base}^{{commit}}") if args.base else merge_base()
        collected = collect(prebuilt=args.prebuilt)
        found = recorded(base)
        if found is None:
            with tempfile.TemporaryDirectory(prefix="ve-gate-base-") as scratch:
                env = {name: os.environ[name] for name in INHERITED if name in os.environ}
                expected = collect_commit(base, Path(scratch), build_env=dict(os.environ), python=[sys.executable],
                                          env={**env, "VE_NATIVE_PREBUILT": "1"})
        else:
            expected = found[1]
        verdict = missing(expected, collected, changes(base, None))
    except (CollectionError, RuntimeError) as exc:
        print(f"gate collection: {exc}", file=sys.stderr)
        return 2
    for nodeid, row in verdict.removed.items():
        print(f"removed: {nodeid}: {row['reason']} (commit {row['commit'][:12]}; {row['label']})")
    print(f"{len(collected)} collected, {len(expected)} at {base}; {len(set(collected) - set(expected))} added, "
          f"{len(verdict.removed)} removed by a trailer, {len(verdict.refused)} refused, "
          f"{len(verdict.stale)} stale and {len(verdict.malformed)} malformed trailers")
    if verdict.failed():
        print(difference_text(base, verdict), file=sys.stderr)
    return 1 if verdict.failed() else 0


if __name__ == "__main__":
    raise SystemExit(main())
