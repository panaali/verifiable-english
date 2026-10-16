"""Plant every mutant a fixed set of operators makes in this batch's Python code, run
tests/test_answer_cutoff.py on each, and restore the source: a test must fail for each one, or the mutant is
listed in EXEMPT with why no behaviour changes.

  .venv/bin/python docs/test-architecture/cutoff/sweep.py [--only FILE] [--jobs N] run | check

mutants.py names the bugs a review asked for, one by one; this sweep makes the rest of their kind
mechanically, so no branch is left untested because nobody thought to plant a bug in it. The operators: a
comparison negated or relaxed (`a == [b]` to `b in a`), `and`/`or` swapped and each operand dropped, `not`
dropped, an augmented assignment made plain (`|=` to `=`), each condition forced true and false, each
operand of a `-`, `&`, `|` or `+` dropped, each keyword argument dropped, each statement removed, and
`True`/`False` flipped. The code is the batch's: tools/answer_cutoff.py and tools/answer_replay.py whole,
and the lines of tools/test_map_recorder.py and tools/select_tests.py added since the saved base.

`run` writes evidence/sweep.json; `check` (check_evidence.py) reads it: the run is of today's mutant list,
and the survivors are exactly EXEMPT's mutants, each with why it changes no behaviour.
"""
from __future__ import annotations

import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
import copy
import hashlib
import itertools
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "tools")]
import nested_pytest  # noqa: E402
from subprocesses import HANG_TIMEOUT  # noqa: E402

OUTPUT = HERE / "evidence/sweep.json"
TEST = "tests/test_answer_cutoff.py"
WHOLE = ("tools/answer_cutoff.py", "tools/answer_replay.py")
ADDED = ("tools/test_map_recorder.py", "tools/select_tests.py")
FLIPPED = {ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.In: ast.NotIn, ast.NotIn: ast.In, ast.Is: ast.IsNot,
           ast.IsNot: ast.Is, ast.Lt: ast.GtE, ast.GtE: ast.Lt, ast.Gt: ast.LtE, ast.LtE: ast.Gt}
DROPPED = (ast.Sub, ast.BitAnd, ast.BitOr, ast.Add)
# The unmutated file runs in well under a minute even on the first, uncached run.
MUTANT_TIMEOUT = 300

# Why each kind of survivor changes no behaviour.

ESCAPES = 'json writes non-ASCII text as escapes that reading the line restores: the same rows'
ASCII = "the text is json's ASCII (non-ASCII escaped), which any locale's codec writes and reads alike"
LAST_RETURN = "a function's last statement `return None`: falling off its end returns None too"
PATH_TYPE = 'read_json opens a str path as it opens a Path'
PROGRESS = 'a progress line every 50,000 answers: no answer depends on it'
NO_RECORDING = "without a request recording, `_request` raises KeyError into the audit hook's catch-all after the event's last record: nothing else is written or skipped"
FORK = "a forked child of a request recording writes through its parent's handle, opened for appending and flushed per record: the same lines in the unit's records"
WRITE_MAP = 'test_map.write_map, which writes first into the output, makes the directory'
WORK_EXISTS = 'the work directory exists when it is removed (mkdtemp made it, or record_units wrote in it)'
RANDOM_ONLY = 'of the modules in UNSEEDED only random has a `Random`'
GIT_CHECK = 'a failed `git show` prints nothing, which does not parse: pinned is False either way'
GIT_BYTES = 'json.loads reads the bytes of `git show` as it reads its text'
UNUSED = 'deletes a parameter the rule does not use'
INSTALLED = "the tools' environment installs the project (editable), so `ve` imports without the path entry, which serves a bare checkout"
INTEGER = "_json_integer is int() wherever int() parses; a longer integer never reaches a recording, since the client's _dumps could not have written it"
CASE_INDEX = 'a result rebuilt without `case_index` is the result itself when it has none'
NONE_KEY = "environments.get(None, '') finds nothing, as .get('', '') does"
EMPTY_BATCH = 'a batch whose cases were all lost, sent anyway, has no case to answer: ask returns no answer'
STARTUP = "the startup allowance of a loaded machine: the client's default lets an idle one start"
HANDLES = "inline texts name no handle, so the client's handle table is never used"
STRICT = "the count check after the threads raises on a short answer list too, and the client's binding check never returns more results than cases"
DAEMON = 'the threads are joined before replay returns: daemon matters only at interpreter exit'
COMPACT = 'whitespace between JSON tokens only: read_json reads either'
REOPEN = 'reopening the store file for appending writes the same lines, each flushed'

# Survivors that change no behaviour, by `key`: why. A key names the file, the function and the statement as far
# as the mutated code, before and after (whitespace collapsed), so it stays with its place when lines move.
EXEMPT: dict[str, str] = {
    'tools/answer_cutoff.py:write_store: handle.write(json.dumps(rows[name], ensure_ascii=False) + "\\n") -> handle.write(json.dumps(rows[name]) + "\\n")':
        ESCAPES,
    'tools/answer_cutoff.py:write_store: handle.write(json.dumps(rows[name], ensure_ascii=False) + "\\n") -> handle.write(json.dumps(rows[name], ensure_ascii=True) + "\\n")':
        ESCAPES,
    'tools/answer_cutoff.py:record: output.mkdir(parents=True, exist_ok=True) -> pass':
        WRITE_MAP,
    'tools/answer_cutoff.py:record: shutil.rmtree(work, ignore_errors=True) -> shutil.rmtree(work)':
        WORK_EXISTS,
    'tools/answer_cutoff.py:record: shutil.rmtree(work, ignore_errors=True) -> shutil.rmtree(work, ignore_errors=False)':
        WORK_EXISTS,
    'tools/answer_cutoff.py:randomised: if module == "random" and name == "Random" and (node.args or node.keywords): -> if name == \'Random\' and (node.args or node.keywords):':
        RANDOM_ONLY,
    'tools/answer_cutoff.py:randomised: return None -> pass':
        LAST_RETURN,
    'tools/answer_cutoff.py:pinned: text = (ROOT / PIN_FILE).read_text() if after is None else subprocess.run( ["git", "show", f"{after}:{PIN_FILE}"], cwd=ROOT, check=True, capture_output=True, text=True).stdout -> text = (ROOT / PIN_FILE).read_text() if after is None else subprocess.run([\'git\', \'show\', f\'{after}:{PIN_FILE}\'], cwd=ROOT, capture_output=True, text=True).stdout':
        GIT_CHECK,
    'tools/answer_cutoff.py:pinned: text = (ROOT / PIN_FILE).read_text() if after is None else subprocess.run( ["git", "show", f"{after}:{PIN_FILE}"], cwd=ROOT, check=True, capture_output=True, text=True).stdout -> text = (ROOT / PIN_FILE).read_text() if after is None else subprocess.run([\'git\', \'show\', f\'{after}:{PIN_FILE}\'], cwd=ROOT, check=True, capture_output=True).stdout':
        GIT_BYTES,
    'tools/answer_cutoff.py:pinned: text = (ROOT / PIN_FILE).read_text() if after is None else subprocess.run( ["git", "show", f"{after}:{PIN_FILE}"], cwd=ROOT, check=True, capture_output=True, text=True).stdout -> text = (ROOT / PIN_FILE).read_text() if after is None else subprocess.run( ["git", "show", f"{after}:{PIN_FILE}"], cwd=ROOT, check=False, capture_output=True, text=True).stdout':
        GIT_CHECK,
    'tools/answer_cutoff.py:pinned: text = (ROOT / PIN_FILE).read_text() if after is None else subprocess.run( ["git", "show", f"{after}:{PIN_FILE}"], cwd=ROOT, check=True, capture_output=True, text=True).stdout -> text = (ROOT / PIN_FILE).read_text() if after is None else subprocess.run( ["git", "show", f"{after}:{PIN_FILE}"], cwd=ROOT, check=True, capture_output=True, text=False).stdout':
        GIT_BYTES,
    'tools/answer_cutoff.py:answers_rule.rule: del graph -> pass':
        UNUSED,
    'tools/answer_cutoff.py:main: diff.add_argument("base", type=Path) -> diff.add_argument(\'base\')':
        PATH_TYPE,
    'tools/answer_cutoff.py:main: diff.add_argument("head", type=Path) -> diff.add_argument(\'head\')':
        PATH_TYPE,
    'tools/answer_cutoff.py:main: diff.add_argument("--recording-answers", type=Path, help="the recording replayed on its own build: needed when the base build is another") -> diff.add_argument(\'--recording-answers\', help=\'the recording replayed on its own build: needed when the base build is another\')':
        PATH_TYPE,
    'tools/answer_replay.py:<module>: sys.path.insert(0, str(ROOT)) -> pass':
        INSTALLED,
    'tools/answer_replay.py:inline: case = json.loads(text, parse_int=lean_service._json_integer) -> case = json.loads(text)':
        INTEGER,
    'tools/answer_replay.py:inline: case["environment"] = json.loads(environments[handle], parse_int=lean_service._json_integer) -> case["environment"] = json.loads(environments[handle])':
        INTEGER,
    'tools/answer_replay.py:unplaced: if isinstance(result, dict) and "case_index" in result: -> if isinstance(result, dict):':
        CASE_INDEX,
    'tools/answer_replay.py:batches: extra = len(text) + len(environments.get(handle_of(text) or "", "")) -> extra = len(text) + len(environments.get(handle_of(text), ""))':
        NONE_KEY,
    'tools/answer_replay.py:replay: if len(lost) < len(keys): -> if True:':
        EMPTY_BATCH,
    'tools/answer_replay.py:replay.work: with lean_service.LeanService(executable, expected_sha256=build, startup_timeout=REPLAY_TIMEOUT, handles=False) as service: -> with lean_service.LeanService(executable, expected_sha256=build, handles=False) as service:':
        STARTUP,
    'tools/answer_replay.py:replay.work: with lean_service.LeanService(executable, expected_sha256=build, startup_timeout=REPLAY_TIMEOUT, handles=False) as service: -> with lean_service.LeanService(executable, expected_sha256=build, startup_timeout=REPLAY_TIMEOUT) as service:':
        HANDLES,
    'tools/answer_replay.py:replay.work: with lean_service.LeanService(executable, expected_sha256=build, startup_timeout=REPLAY_TIMEOUT, handles=False) as service: -> with lean_service.LeanService(executable, expected_sha256=build, startup_timeout=REPLAY_TIMEOUT, handles=True) as service:':
        HANDLES,
    'tools/answer_replay.py:replay.work: before = len(answers) // 50000 -> pass':
        PROGRESS,
    'tools/answer_replay.py:replay.work: answers.update(zip(keys, found, strict=True)) -> answers.update(zip(keys, found))':
        STRICT,
    'tools/answer_replay.py:replay.work: answers.update(zip(keys, found, strict=True)) -> answers.update(zip(keys, found, strict=False))':
        STRICT,
    'tools/answer_replay.py:replay.work: if len(answers) // 50000 > before: -> if False:':
        PROGRESS,
    'tools/answer_replay.py:replay.work: if len(answers) // 50000 > before: -> if True:':
        PROGRESS,
    'tools/answer_replay.py:replay.work: if len(answers) // 50000 > before: -> if len(answers) // 50000 <= before:':
        PROGRESS,
    'tools/answer_replay.py:replay.work: progress(f"replayed {len(answers)} of {len(cases)} cases") -> pass':
        PROGRESS,
    'tools/answer_replay.py:replay: threads = [threading.Thread(target=work, daemon=True) for _ in range(max(1, jobs))] -> threads = [threading.Thread(target=work) for _ in range(max(1, jobs))]':
        DAEMON,
    'tools/answer_replay.py:replay: threads = [threading.Thread(target=work, daemon=True) for _ in range(max(1, jobs))] -> threads = [threading.Thread(target=work, daemon=False) for _ in range(max(1, jobs))]':
        DAEMON,
    'tools/answer_replay.py:write_json: with opener(path, "wt", encoding="utf-8") as handle: -> with opener(path, \'wt\') as handle:':
        ASCII,
    'tools/answer_replay.py:write_json: json.dump(data, handle, separators=(",", ":")) -> json.dump(data, handle)':
        COMPACT,
    'tools/answer_replay.py:read_json: with opener(path, "rt", encoding="utf-8") as handle: -> with opener(path, \'rt\') as handle:':
        ASCII,
    'tools/answer_replay.py:main: two.add_argument("base", type=Path) -> two.add_argument(\'base\')':
        PATH_TYPE,
    'tools/answer_replay.py:main: two.add_argument("head", type=Path) -> two.add_argument(\'head\')':
        PATH_TYPE,
    'tools/test_map_recorder.py:_audit: if "requests" in _state: -> if True:':
        NO_RECORDING,
    'tools/test_map_recorder.py:_caller: return None -> pass':
        LAST_RETURN,
    'tools/test_map_recorder.py:_store: if kind not in _state["stores"]: -> if True:':
        REOPEN,
    'tools/test_map_recorder.py:_store: _state["stores"][kind].write(json.dumps(record, ensure_ascii=False) + "\\n") -> _state["stores"][kind].write(json.dumps(record) + "\\n")':
        ESCAPES,
    'tools/test_map_recorder.py:_store: _state["stores"][kind].write(json.dumps(record, ensure_ascii=False) + "\\n") -> _state["stores"][kind].write(json.dumps(record, ensure_ascii=True) + "\\n")':
        ESCAPES,
    'tools/test_map_recorder.py:_open_requests: _state["requests"] = open(os.path.join(root, "units", unit, f"{os.getpid()}.jsonl"), "a", encoding="utf-8") -> _state["requests"] = open(os.path.join(root, \'units\', unit, f\'{os.getpid()}.jsonl\'), \'a\')':
        ASCII,
    'tools/test_map_recorder.py:_after_fork: if "requests" in _state: -> if False:':
        FORK,
    'tools/test_map_recorder.py:_after_fork: _open_requests() -> pass':
        FORK,
}


def base() -> str:
    return json.loads((HERE / "evidence/summary.json").read_text())["base"]


def added_lines(name: str) -> set[int]:
    """The lines of `name` added since the saved base (a fixed commit, so the scope does not move)."""
    diff = subprocess.run(["git", "diff", "-U0", base(), "--", name], cwd=ROOT, check=True, capture_output=True,
                          text=True).stdout
    found: set[int] = set()
    for line in diff.splitlines():
        if line.startswith("@@"):
            start, _, count = line.split()[2].lstrip("+").partition(",")
            found.update(range(int(start), int(start) + (int(count) if count else 1)))
    return found


def segment(source: str, node: ast.AST) -> tuple[int, int]:
    """The character offsets of `node` in `source`."""
    starts = [0]
    for line in source.splitlines(keepends=True):
        starts.append(starts[-1] + len(line))

    def offset(line: int, column: int) -> int:  # ast columns count UTF-8 bytes
        text = source[starts[line - 1]:starts[line]]
        return starts[line - 1] + len(text.encode()[:column].decode())

    return offset(node.lineno, node.col_offset), offset(node.end_lineno, node.end_col_offset)


def replaced(node: ast.AST, **fields) -> ast.AST:
    other = copy.deepcopy(node)
    for field, value in fields.items():
        setattr(other, field, value)
    return other


def variants(node: ast.AST) -> list[tuple[ast.AST, str]]:
    """(the node to replace, its replacement source) for each mutant of `node`."""
    found: list[tuple[ast.AST, str]] = []
    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        found.append((node, ast.unparse(replaced(node, ops=[FLIPPED.get(type(node.ops[0]), ast.Eq)()]))))
        right = node.comparators[0]
        if isinstance(node.ops[0], ast.Eq) and isinstance(right, ast.List | ast.Tuple) and len(right.elts) == 1:
            found.append((node, ast.unparse(ast.Compare(right.elts[0], [ast.In()], [node.left]))))
    elif isinstance(node, ast.BoolOp):
        other = ast.Or() if isinstance(node.op, ast.And) else ast.And()
        found.append((node, ast.unparse(replaced(node, op=other))))
        for i in range(len(node.values)):
            rest = node.values[:i] + node.values[i + 1:]
            found.append((node, ast.unparse(rest[0] if len(rest) == 1 else replaced(node, values=rest))))
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        found.append((node, ast.unparse(node.operand)))
    elif isinstance(node, ast.BinOp) and isinstance(node.op, DROPPED):
        found += [(node, ast.unparse(node.left)), (node, ast.unparse(node.right))]
    elif isinstance(node, ast.Constant) and isinstance(node.value, bool):
        found.append((node, repr(not node.value)))
    elif isinstance(node, ast.Call):
        for keyword in node.keywords:
            if keyword.arg is not None:
                found.append((node, ast.unparse(replaced(node, keywords=[k for k in node.keywords if k is not keyword]))))
    if isinstance(node, ast.If | ast.While | ast.IfExp):
        found += [(node.test, "True"), (node.test, "False")]
    elif isinstance(node, ast.comprehension):
        found += [(test, value) for test in node.ifs for value in ("True", "False")]
    if isinstance(node, ast.AugAssign):
        found.append((node, ast.unparse(ast.Assign([node.target], node.value, lineno=0))))
    if isinstance(node, ast.Expr | ast.Assign | ast.AugAssign | ast.AnnAssign | ast.Raise | ast.Return
                  | ast.Continue | ast.Delete) and not (
            isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)):  # a docstring
        found.append((node, "pass"))
    return found


def mutants(name: str) -> list[dict]:
    source = (ROOT / name).read_text(encoding="utf-8")
    scope = None if name in WHOLE else added_lines(name)
    tree = ast.parse(source)
    # A message's f-string is not behaviour, and a node inside one has no source segment of its own; nor is
    # an annotation, which `from __future__ import annotations` never evaluates.
    inert = [node for node in ast.walk(tree) if isinstance(node, ast.JoinedStr)] + [
        annotation for node in ast.walk(tree) for annotation in (
            [node.annotation] if isinstance(node, ast.arg | ast.AnnAssign) else
            [node.returns] if isinstance(node, ast.FunctionDef) else []) if annotation is not None]
    formatted = {id(inner) for node in inert for inner in ast.walk(node)}
    statement, enclosing = {}, {}  # each node's innermost statement, and the function or class it is in
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            statement[id(child)] = child if isinstance(child, ast.stmt) else statement.get(id(node), node)
            named = isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
            enclosing[id(child)] = ".".join(filter(None, (enclosing.get(id(node)), node.name if named else None)))
    starts = [0]
    for line in source.splitlines(keepends=True):
        starts.append(starts[-1] + len(line))
    found, seen = [], set()
    for node in ast.walk(tree):
        if id(node) in formatted:
            continue
        for target, text in variants(node):
            if scope is not None and not set(range(target.lineno, target.end_lineno + 1)) <= scope:
                continue
            start, end = segment(source, target)
            mutant = source[:start] + text + source[end:]
            original = source[start:end]
            if mutant == source or original == text or (start, end, text) in seen:
                continue
            try:
                ast.parse(mutant)
            except SyntaxError:
                continue
            seen.add((start, end, text))
            first = statement[id(target)].lineno
            before, after = source[starts[first - 1]:start], source[end:starts[target.end_lineno]]
            place = f"{name}:{enclosing.get(id(target)) or '<module>'}: {' '.join((before + original + after).split())}"
            found.append({"file": name, "line": target.lineno, "original": original, "mutant": text,
                          "key": f"{place} -> {' '.join((before + text + after).split())}", "start": start,
                          "end": end})
    found.sort(key=lambda row: (row["start"], row["end"], row["mutant"]))
    counted: dict[str, int] = {}
    for row in found:  # the same statement twice in one function: number the later ones
        counted[row["key"]] = counted.get(row["key"], 0) + 1
        if counted[row["key"]] > 1:
            row["key"] += f" #{counted[row['key']]}"
    return found


def all_mutants(only: str | None = None) -> list[dict]:
    return [row for name in (*WHOLE, *ADDED) if only in (None, name) for row in mutants(name)]


def pytest(root: Path, cache: Path, timeout: float = HANG_TIMEOUT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(nested_pytest.command(["-q", "-x", "-p", "no:cacheprovider", TEST],
                                                python=[str(ROOT / ".venv/bin/python")]),
                          cwd=root, text=True, capture_output=True, timeout=timeout,
                          env=nested_pytest.environment(os.environ, PYTHONPYCACHEPREFIX=str(cache),
                                                        VE_NATIVE_PREBUILT="1", VE_LEAN_PREBUILT="1"))


def drop_bytecode(root: Path, name: str) -> None:
    """A child process the tests start writes bytecode next to the source: never let a mutant's be read."""
    for path in (root / name).parent.glob(f"__pycache__/{Path(name).stem}.*.pyc"):
        path.unlink()


STAMPS = itertools.count(1_000_000_000)  # bytecode is valid for a source's (size, whole-second mtime)


def scratch(directory: Path) -> Path:
    """A copy of this checkout to plant mutants in, so several run at once: the files the tests read, and
    the built ve_service linked in under the copy's own path (the recorder resolves it against the root)."""
    subprocess.run(["rsync", "-a", "--exclude=/lean/.lake", "--exclude=/.venv", "--exclude=/rust",
                    "--exclude=/experiments", "--exclude=/.cargo-home", "--exclude=__pycache__",
                    f"{ROOT}/", f"{directory}/"], check=True)
    service = directory / "lean/.lake/build/bin/ve_service"
    service.parent.mkdir(parents=True)
    os.link(ROOT / "lean/.lake/build/bin/ve_service", service)
    return directory


def key(row: dict) -> str:
    return row["key"]


def digest(rows: list[dict]) -> str:
    return hashlib.sha256(json.dumps([key(row) for row in rows]).encode()).hexdigest()


def content(name: str) -> str:
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def caught(root: Path, cache: Path, row: dict) -> bool:
    path = root / row["file"]
    original, stamp = path.read_text(encoding="utf-8"), path.stat().st_mtime_ns
    try:
        path.write_text(original[:row["start"]] + row["mutant"] + original[row["end"]:], encoding="utf-8")
        mutant = next(STAMPS)  # a stamp no other text of the file has, so no other text's bytecode is read
        os.utime(path, (mutant, mutant))
        drop_bytecode(root, row["file"])
        try:
            return pytest(root, cache, MUTANT_TIMEOUT).returncode != 0
        except subprocess.TimeoutExpired:  # a mutant that hangs the tests (a loop that never ends) fails them
            return True
    finally:
        path.write_text(original, encoding="utf-8")
        os.utime(path, ns=(stamp, stamp))
        drop_bytecode(root, row["file"])


def run(only: str | None, jobs: int) -> int:
    rows = all_mutants(only)
    work = Path(tempfile.mkdtemp(prefix="ve-sweep-"))
    survivors = []
    try:
        roots = [scratch(work / f"copy{i}") for i in range(jobs)]
        caches = [work / f"cache{i}" for i in range(jobs)]
        with ThreadPoolExecutor(jobs) as pool:
            for root, result in zip(roots, pool.map(pytest, roots, caches)):
                if result.returncode:
                    raise RuntimeError(f"{TEST} fails on the unmutated source in {root}")
        free = queue.Queue()
        for slot in range(jobs):
            free.put(slot)

        def one(row: dict) -> bool:
            slot = free.get()
            try:
                return caught(roots[slot], caches[slot], row)
            finally:
                free.put(slot)

        with ThreadPoolExecutor(jobs) as pool:
            for i, (row, failed) in enumerate(zip(rows, pool.map(one, rows))):
                if not failed:
                    survivors.append(row)
                print(f"{i + 1}/{len(rows)} {row['file']}:{row['line']} {'caught' if failed else 'SURVIVED'}: "
                      f"{row['original'][:60]!r} -> {row['mutant'][:60]!r}", flush=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    if only is None:
        files = {name: {"sha256": content(name), "digest": digest([row for row in rows if row["file"] == name])}
                 for name in (*WHOLE, *ADDED)}
        OUTPUT.write_text(json.dumps({"batch": "tarch-cutoff", "test": TEST, "python": list(sys.version_info[:2]),
                                      "mutants": len(rows), "files": files, "survivors": [
                                          {k: row[k] for k in ("file", "line", "key")}
                                          for row in survivors]}, indent=1, ensure_ascii=False) + "\n")
    unexplained = [row for row in survivors if key(row) not in EXEMPT]
    print(f"{len(rows)} mutants, {len(survivors)} survived, {len(unexplained)} not in EXEMPT")
    return 1 if unexplained else 0


def check() -> int:
    saved = json.loads(OUTPUT.read_text())
    if list(sys.version_info[:2]) != saved["python"]:  # ast.unparse writes some code differently in each version
        return subprocess.run([str(ROOT / ".venv/bin/python"), __file__, "check"], cwd=ROOT).returncode
    for name, run_of in saved["files"].items():
        if content(name) == run_of["sha256"]:
            assert digest(mutants(name)) == run_of["digest"], f"{name}: the saved run is not of today's mutants"
        else:  # this batch's own files must be swept as they are; a shared file main changed since is noted
            assert name not in WHOLE, f"{name} changed since the sweep: run sweep.py run again"
            print(f"sweep: {name} changed since the sweep (main's edits after the batch)")
    unexplained = [row for row in saved["survivors"] if key(row) not in EXEMPT]
    assert not unexplained, f"survivors not in EXEMPT: {unexplained}"
    stale = set(EXEMPT) - {key(row) for row in saved["survivors"]}
    assert not stale, f"EXEMPT names mutants a test now catches, or that no longer exist: {sorted(stale)}"
    print(f"sweep: {saved['mutants']} mutants, {len(saved['survivors'])} survivors, each in EXEMPT")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", help="sweep one file (no evidence is written)")
    parser.add_argument("--jobs", type=int, default=8, help="scratch copies that run mutants at once")
    parser.add_argument("command", choices=("run", "check"))
    args = parser.parse_args()
    return run(args.only, args.jobs) if args.command == "run" else check()


if __name__ == "__main__":
    raise SystemExit(main())
