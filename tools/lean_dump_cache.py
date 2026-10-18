"""A content-keyed cache of the two Lean dumps of `tools/regen_generated.py`: `cached`.

The entries `lean-statements` (`tools/lean_statements.py`, the statement, predicate and declaration dumps) and
`lean-audit-manifests` (`lean/audit.py --check` and `--write`, the `#print axioms` runs) each run Lean over the
whole tree for minutes. Their output is a function of what the run reads, so a run on inputs that a run on this
machine already dumped replays the bytes Lean wrote then instead of running Lean again. Lean owns the output;
this module only stores and replays it, and the callers' Python checks run on the replayed text as on a fresh
one. The key holds everything the output can depend on:

* every Lean source the dump reads (`sources`: every `*.lean` under `lean/` outside `.lake`, the generated
  audit manifests included), by path and SHA-256, so an edited, added or removed file is another key;
* the toolchain, lakefile and Lake manifest (`LEAN_INPUTS`), the installed toolchain's programs and libraries
  (`toolchain`), the `lake` program that runs, the Lean, Lake and elan settings of the environment, the platform
  and the Python version;
* the code that runs Lean and reads its output: `CODE_STARTS` and every repository Python module their imports
  reach (`tools/source_graph.py`), the embedded Lean scripts included, this module and the store;
* the caller's own inputs (the audit: `lean/declarations.txt` and the digest of the texts it elaborates);
* `FORMAT` and the step.

A stored entry records those inputs; it is replayed only when every recorded input equals the current one, and
any other entry (malformed, truncated, of another format, step or key) is a miss that runs the dump as without a
cache. Only a dump that finished is stored, and only when its inputs did not change while it ran. A tree with a
source that runs code while it elaborates (`EVALUATES`: `#eval`, `include_str`, ...) is never cached, since that
code could read a file the key does not name. `VE_RUN_CACHE` governs it as it governs `tools/run_cache.py`
(`off` turns it off; the nightlies set it); the entries are kept by `tools/cache_store.py` in a directory per
step. A replayed run prints `<step>: from cache <key8>` on stderr. `tests/test_lean_dump_cache.py` changes each
kind of keyed input and checks that the entry is not used.
"""
from __future__ import annotations

from collections.abc import Callable
import json
import os
from pathlib import Path
import platform
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # the store's HANG_TIMEOUT (tests/subprocesses.py), for a script run from tools/
    sys.path.append(str(ROOT))
import cache_store  # noqa: E402

# 1: the first format.
FORMAT = "ve-lean-dump-cache@1"
# Entries kept per step, newest first (a statement dump is about 0.8 MB compressed).
KEEP = 16
# The steps: the names of the tools/regen_generated.py entries they serve.
STATEMENTS = "lean-statements"
AUDIT = "lean-audit-manifests"
CODE_STARTS = ("tools/lean_statements.py", "lean/audit.py")
LEAN_INPUTS = ("lean/lean-toolchain", "lean/lakefile.toml", "lean/lakefile.lean", "lean/lake-manifest.json")
ENVIRONMENT = ("LEAN", "LAKE", "ELAN")
# Commands that run code while a file elaborates, which may read any file; and, in a file that defines
# elaboration code, a use of IO or the file system.
EVALUATES = re.compile(r"(?<![\w.'])(#eval|#exit|include_str|run_cmd|run_elab|run_meta|initialize|"
                       r"builtin_initialize)(?![\w'])")
ELABORATES = re.compile(r"(?<![\w.'])(elab|elab_rules|macro|macro_rules|syntax|TacticM|TermElabM|CommandElabM|"
                        r"MetaM|CoreM)(?![\w'])")
READS = re.compile(r"(?<![\w'])(IO|System|FilePath)\.")


def code_only(text: str) -> str:
    """The text with comments and string literals blanked (lean/audit.py's)."""
    if str(ROOT / "lean") not in sys.path:
        sys.path.insert(0, str(ROOT / "lean"))
    from audit import code_only as blank
    return blank(text)


def evaluates(root: Path, sources: list[Path]) -> str | None:
    """Why the dump of `sources` cannot be keyed by their content: the first source whose code runs code
    while it elaborates, or defines elaboration code that uses IO; None when none does."""
    for path in sources:
        text = path.read_text(encoding="utf-8", errors="replace")
        if not EVALUATES.search(text) and not (ELABORATES.search(text) and READS.search(text)):
            continue
        code = code_only(text)
        found = EVALUATES.search(code) or (ELABORATES.search(code) and READS.search(code))
        if found:
            return f"{path.relative_to(root).as_posix()} runs code while it elaborates ({found[0]})"
    return None


def code_files(code_root: Path) -> list[str]:
    """`CODE_STARTS` and every repository Python file their imports reach (`tools/source_graph.py`'s import edges,
    without the files their strings name: the dump runs no script), as paths under `code_root`."""
    tools = str(code_root / "tools")
    sys.path.insert(0, tools)
    try:
        import source_graph
    finally:
        sys.path.remove(tools)
    edges = source_graph.load(code_root).edges
    found, stack = set(CODE_STARTS), list(CODE_STARTS)
    while stack:
        for target in edges.get(stack.pop(), ()):
            if target not in found:
                found.add(target)
                stack.append(target)
    return sorted(found)


def toolchain(root: Path) -> str:
    """The installed toolchain that `lean/lean-toolchain` names, by the digests of its programs and shared libraries,
    in elan's directory for it (`<ELAN_HOME or ~/.elan>/toolchains/<name, "/" as "--" and ":" as "---">`, found
    without running elan, which could download one): a toolchain reinstalled under its name with other bytes is
    another key, and one not installed is keyed as absent."""
    name = (root / "lean/lean-toolchain").read_text().strip() if (root / "lean/lean-toolchain").is_file() else ""
    home = Path(os.environ.get("ELAN_HOME") or Path.home() / ".elan") / "toolchains" / \
        name.replace("/", "--").replace(":", "---")
    files = [home / "bin/lean", home / "bin/lake", *sorted((home / "lib/lean").glob("*.so")),
             *sorted((home / "lib/lean").glob("*.dylib"))]
    return json.dumps([str(home), {str(path.relative_to(home)): cache_store.file_digest(path) for path in files}])


def inputs(step: str, root: Path, sources: list[Path], files: tuple[str, ...] = (), values: dict | None = None,
           code_root: Path = ROOT) -> dict[str, str]:
    """{input: digest} of everything a dump of `step` over `sources` can depend on (the module docstring):
    `files` and `values` are the caller's own inputs, as paths under `root` and as named values."""
    found = {"step": step}
    found.update((f"lean:{path.relative_to(root).as_posix()}", cache_store.file_digest(path)) for path in sources)
    found.update((f"file:{name}", cache_store.file_digest(root / name)) for name in (*LEAN_INPUTS, *files))
    found.update((f"code:{name}", cache_store.file_digest(code_root / name)) for name in code_files(code_root))
    found["program:toolchain"] = toolchain(root)
    lake = shutil.which("lake")
    found["program:lake"] = json.dumps([lake, cache_store.file_digest(Path(os.path.realpath(lake))) if lake else None])
    found["environment"] = json.dumps({name: value.replace(str(root), "<root>") for name, value in
                                       sorted(os.environ.items()) if name.startswith(ENVIRONMENT)})
    found["platform"] = json.dumps([platform.platform(), platform.machine(), sys.version])
    found.update((f"value:{name}", value) for name, value in sorted((values or {}).items()))
    return found


def usable(entry: dict | None, step: str, key: str, current: dict[str, str], count: int) -> bool:
    """Whether a loaded entry is a finished dump of `step` under `key` whose every recorded input is the current
    one, with `count` texts."""
    return (entry is not None and entry.get("format") == FORMAT and entry.get("step") == step
            and entry.get("key") == key and entry.get("inputs") == current
            and isinstance(entry.get("outputs"), list) and len(entry["outputs"]) == count
            and all(isinstance(text, str) for text in entry["outputs"]))


def cached(step: str, root: Path, sources: Callable[[], list[Path]], run: Callable[[], list[str]], count: int,
           files: tuple[str, ...] = (), values: dict | None = None, code_root: Path = ROOT) -> list[str]:
    """The `count` texts that `run()` (the Lean dump of `step` over the files `sources()` lists) returns: replayed
    from an entry of the same inputs (`inputs`) when one is stored, else from `run()`, stored when its inputs
    did not change while it ran."""
    folder = cache_store.directory(root, step)
    if folder is None:
        return run()
    listed = sources()
    reason = evaluates(root, listed)
    if reason is not None:
        print(f"{step}: not cached: {reason}", file=sys.stderr)
        return run()
    current = inputs(step, root, listed, files, values, code_root)
    key = cache_store.key_of(FORMAT, current)
    path = cache_store.entry_path(folder, key)
    entry = cache_store.load(path)
    if usable(entry, step, key, current, count):
        cache_store.touch(path)
        print(f"{step}: from cache {key[:8]}", file=sys.stderr, flush=True)
        return list(entry["outputs"])
    texts = run()
    if len(texts) == count and inputs(step, root, sources(), files, values, code_root) == current:
        try:
            cache_store.store(path, {"format": FORMAT, "step": step, "key": key, "inputs": current,
                                     "outputs": list(texts)}, KEEP)
        except OSError as error:  # the dump stands; the next run dumps again
            print(f"{step}: not stored: {error}", file=sys.stderr)
    return texts
