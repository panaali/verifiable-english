"""Regenerate, check and merge every generated inventory, manifest and lock of the repository.

    uv run python tools/regen_generated.py --list              # the inventory: files, writers, checkers
    uv run python tools/regen_generated.py --write [--skip N]  # regenerate everything, in dependency order
    uv run python tools/regen_generated.py --check [--skip N]  # exit 1 if any generated file is stale
    uv run python tools/regen_generated.py --resolve           # finish a `git merge --no-commit` (below)
    python3 tools/regen_generated.py --merge-driver %O %A %B %P   # git's merge driver `ve-generated`
    python3 tools/regen_generated.py --install-driver              # configure that driver in this repository

`GENERATED` is the one list of these files. Each entry names the files it owns (git attribute patterns),
the command that rewrites them and the one that checks them, both owned by the file's own generator (this
script only runs them, in order), and how a merge combines two sides of the file before regeneration:

* `regenerate`: the file is derived from the tree; a merge takes either side and the writer rebuilds it;
* `union`: a hand-kept list of lines whose union is the merge (the Lean import roots); the build that
  follows (`lake build`) catches a wrong union;
* `json`: a hand-curated JSON ledger (the assurance manifest, trust tables, checker pins, layer ledgers);
  a structural three-way merge (`merge_json`) keeps both sides' additions and removals and fails on a
  value both sides changed differently, which is left to a person or the sync agent.

`.gitattributes` is generated from the same list (`merge=ve-generated` for every owned pattern). With the
driver installed, `git merge` resolves those files by their strategy and never stops on them. Without it,
`--resolve` does the same from the index stages of each conflicted path.

`--resolve` (merge-train, docs/merge-tooling.md): run after `git merge --no-commit`. If any conflicted path is
not a generated file it changes nothing and exits 2 (an agent sync is needed). Otherwise it resolves the
conflicted generated files, runs every writer and then every check, stages the generated files and exits 0,
so the caller only runs `git commit --no-edit`; a failed writer or check exits 1.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import fnmatch
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
DRIVER = "ve-generated"
ATTRIBUTES = ROOT / ".gitattributes"
LOCK = ROOT / "lean/checkers.lock"


@dataclass(frozen=True)
class Generated:
    name: str
    paths: tuple[str, ...]            # git attribute patterns, from the repository root
    write: tuple | None               # argv, or a function name of this module; None: merged, never rewritten
    check: tuple | None               # argv, or a function name; None: checked by rewriting and comparing
    merge: str = "regenerate"         # regenerate | union | json
    cwd: str = "."
    note: str = ""


# In dependency order: generated Lean before the build; the build before the statement dumps, the checker pins
# and the Lean-rendered tables; the declaration list before the audit manifests generated from it (AR-1); every
# generated Lean file before the frozen inventory that hashes it; the collection last.
GENERATED = (
    Generated("gitattributes", (".gitattributes",), ("write_attributes",), ("check_attributes",),
              note="the merge attributes of every pattern below"),
    Generated("wire-contract",
              ("lean/VE/WireContract/Limits.lean", "lean/VE/WireContract/Names.lean",
               "lean/VE/WireContract/Tables/*.lean", "ve/wire_contract/contracts.lock",
               "conformance/wire-contract/contracts/contracts.lock", "docs/spec/*-wire-table.md"),
              # Written without live validation: the examples go through the service, which is built and
              # pinned only later; the check (after every write) validates them live.
              ((PY, "-m", "tools.wire_contract", "--write", "--generated-only"),
               (PY, "-m", "tools.wire_contract", "--write", "--generated-only", "--directory",
                "conformance/wire-contract/contracts")),
              ((PY, "-m", "tools.wire_contract", "--check"),
               (PY, "-m", "tools.wire_contract", "--check", "--directory", "conformance/wire-contract/contracts")),
              note="a changed contract needs a higher `revision` in its source (WC10)"),
    Generated("english-grammar", ("lean/VE/EnglishGrammar/Fixed/*.lean", "ve/english_grammar/LOCK.json"),
              ((PY, "tools/english_grammar_gen.py", "--write"),), ((PY, "tools/english_grammar_gen.py", "--check"),),
              note="refuses when a hashed Lean file changed without a new --actions-version (a person decides)"),
    Generated("english-lexicon-fixtures", ("lean/VE/EnglishGrammar/LexiconFixtures.lean",),
              ((PY, "-m", "conformance.english_lean_lexicon", "--lean-fixtures"),), None),
    Generated("question-fixtures", ("lean/VE/Question/Fixtures.lean",),
              ((PY, "tools/question_fixtures.py", "--write"),), ((PY, "tools/question_fixtures.py", "--check"),)),
    Generated("english-run-copy", ("lean/VE/Service/EnglishRun.lean",),
              ((PY, "VE/Service/english_copy.py"),), ((PY, "VE/Service/english_copy.py", "--check"),), cwd="lean"),
    Generated("route-cases", ("lean/VE/Route/examples/route-cases.json",),
              ((PY, "lean/VE/Route/examples/generate.py"),), None),
    Generated("lean-roots", ("lean/VE.lean", "lean/ResponseShape.lean"), None, None, merge="union",
              note="import lists; `lake build` checks the union"),
    Generated("lake-build", (), (("lake", "build"),), (("lake", "build"),), cwd="lean",
              note="no file of its own: the build every later entry reads"),
    Generated("lean-mode-deps", ("tools/lean-mode-deps.json",),
              ((PY, "tools/lean_mode_deps.py", "--write"),),
              ((PY, "tools/lean_mode_deps.py", "--check"),),
              note="mode roots from the compiled runMode dispatch pins"),
    Generated("lean-statements", ("lean/statements.txt", "lean/predicates.txt", "lean/declarations.txt"),
              ((PY, "tools/lean_statements.py"),), ((PY, "tools/lean_statements.py", "--check"),)),
    Generated("lean-audit-manifests", ("lean/VE/Audit.lean", "lean/ResponseShape/Audit.lean", "lean/axioms.txt"),
              ((PY, "lean/audit.py", "--write"),), ((PY, "lean/audit.py", "--check"),),
              note="generated from lean/declarations.txt, then the axiom audit record"),
    Generated("frozen-inventory", ("lean/VE/Route/frozen-sources.sha256",),
              ((PY, "VE/Route/frozen.py", "--write"),), ((PY, "VE/Route/frozen.py"),), cwd="lean"),
    Generated("trust-tables", ("tools/trust-classes.json", "docs/trust-baseline.json"), None,
              ((PY, "tools/trust_map.py", "--check"),), merge="json",
              note="ledgers: growth over the base needs `trust_map.py --allow --reason ... --signed ...` "
                   "(the DRI's signature); `--write` is the merge train's, on main"),
    Generated("checker-pins", ("lean/checkers.lock",), ("pin_checkers",), ("check_pins",), merge="json",
              note="both sides' pins, plus the merged ve_service build and Rust release binary"),
    Generated("response-schemas", ("ve/backends/lean_service_schema/*.json",),
              ((PY, "tools/response_schemas.py", "--write"),), ((PY, "tools/response_schemas.py", "--check"),)),
    Generated("english-codes", ("ve/english_grammar/codes.json",),
              ((PY, "tools/english_codes.py", "--write"),), ((PY, "tools/english_codes.py", "--check"),)),
    Generated("question-codes", ("ve/question/codes.json",),
              ((PY, "tools/question_codes.py", "--write"),), ((PY, "tools/question_codes.py", "--check"),)),
    Generated("question-lock", ("ve/question/LOCK.json",),
              ((PY, "tools/question_lock.py", "--write"),), ((PY, "tools/question_lock.py"),),
              note="hashes lean/VE/Question/*.lean (after question-fixtures) with question-codes' version"),
    Generated("assurance-manifest", ("ve/assurance-manifest.json",), None, ("check_assurance_pins",),
              merge="json", note="decoder pins are reviewed by hand; a merge keeps each side's pins"),
    Generated("assurance-doc", ("docs/spec/assurance-manifest.md",),
              ((PY, "tools/assurance_manifest.py", "--write"),), ((PY, "tools/assurance_manifest.py", "--check"),)),
    Generated("layer-ledgers", ("tools/layer-exceptions.json", "tools/lean-layer-exceptions.json"), None,
              ((PY, "tools/check_lean_imports.py"),), merge="json"),
    Generated("import-contract", (".importlinter",), ((PY, "tools/check_python_layers.py", "--write"),),
              ((PY, "tools/check_python_layers.py"),)),
    Generated("uv-lock", ("uv.lock",), (("uv", "lock"),), (("uv", "lock", "--check"),)),
)


# Generated files that are deleted, each with the change that deleted it: `--resolve` settles a conflict on one
# (a branch that still edited it) by taking the deletion.
RETIRED = {
    "tools/gate-collection.json": "AR-3: the gate takes the expected collection from the merge base",
}


# Scripts with a writing mode whose output this script does not regenerate, each with the reason. Every script
# of the repository with such a mode is either a writer above or listed here (tests/test_regen_generated.py).
NOT_REGENERATED = {
    "tools/ask_fixtures.py": "Q2 use-case fixtures: replayed and reviewed with their source documents",
    "tools/question_answering_report.py": "Q2 batch report from saved measurement and comparison evidence",
    "tools/question_answering_agreement.py": "Q2.6 evidence: the agreement of ask with the existing route, run on corpora and saved",
    "tools/words_ab.py": "Q2.4 evidence: the A/B of Lean's wording against the pre-Q2.4 producers, run on corpora and saved",
    "docs/spec/question-answering-q2/mutants.py": "Q2 seeded-bug evidence: each mutant is run and restored, then its result is saved",
    "tools/difffuzz.py": "reviewed ledger: --update-baseline adds findings a person triages",
    "tools/stage2_parity.py": "report: docs/spec/stage2-parity.md, a migration record",
    "tools/lean_service_soak.py": "measurement report of the machine it runs on",
    "tools/lean_decided_share.py": "measurement report",
    "tools/lean_output_diff.py": "comparison report of two builds",
    "tools/select_tests_evidence.py": "recorded evidence of the test selector (replay and mutants)",
    "tools/coverage_dashboard.py": "report: the ROADMAP.md coverage table",
    "tools/architecture_numbers.py": "the map's numbers, measured on a committed head whose hash they record: "
                                     "rerun after the merge commit",
    "tools/lean_first_oracle.py": "batch 0 oracle, recorded once",
    "tools/semantic_inventory.py": "reads ~/code/ve-webapp and ~/code/ve-bench: not derived from this tree",
    "tools/relay_mutation_gate.py": "--record re-records gate fixtures from a test run; the gate reads answers live",
    "tests/probe_matrix.py": "frozen Stage 0 baseline with a pinned runtime hash",
    "conformance/wire_contract_golden.py": "unit conformance artifact, rewritten with its unit (--check in its tests)",
    "conformance/wire_contract_faults.py": "unit conformance artifact, rewritten with its unit (--check in its tests)",
    "conformance/wire_contract_delta.py": "unit conformance artifact, rewritten with its unit (--check in its tests)",
    "conformance/wire_contract_gate.py": "unit conformance artifact and recorded test inputs; needs the Lean gate run",
    "conformance/soft_norms_wire_report.py": "unit conformance report",
    "conformance/english_lean_e2_report.py": "batch report",
    "conformance/english_lean_e2_6_report.py": "batch report",
    "conformance/english_lean_e2_ab.py": "batch report",
    "conformance/english_lean_e2_readability_report.py": "batch report",
    "docs/lean-first/*/*.py": "batch evidence pinned at a commit",
    "docs/test-speed-b2/shadow.py": "fixed-merge shadow evidence, recorded once and checked at the batch gate",
    "docs/merge-tooling/*.py": "this tooling's evidence, recorded once (git merge-tree --write-tree is no writer)",
    "conformance/soft_norms.py": "--write-rust-fixtures: the Rust tests' fixture, rewritten with the soft-norms unit",
    "usecases/*/*.py": "use-case results, rerun by their harness",
}
# The flags that make a script write a committed file.
WRITE_FLAGS = ("--write", "--update-baseline", "--lean-fixtures", "--record")


def owner(path: str) -> Generated | None:
    """The entry that owns `path` (repository-relative), or None."""
    for entry in GENERATED:
        if any(fnmatch.fnmatchcase(path, pattern) and (pattern.count("/") == path.count("/"))
               for pattern in entry.paths):
            return entry
    return None


def owned_files(entry: Generated, root: Path = ROOT) -> list[Path]:
    return sorted({path for pattern in entry.paths for path in root.glob(pattern) if path.is_file()})


# .gitattributes


ATTRIBUTES_HEAD = ("# Generated by tools/regen_generated.py --write (the GENERATED list); do not edit.\n"
                   "# Generated files merge by their strategy, then tools/regen_generated.py rebuilds them\n"
                   "# (docs/merge-tooling.md). Install the driver once: python3 tools/regen_generated.py --install-driver\n")


def attributes_text() -> str:
    lines = [f"{pattern} merge={DRIVER}\n" for entry in GENERATED for pattern in entry.paths]
    return ATTRIBUTES_HEAD + "".join(lines)


def write_attributes() -> int:
    ATTRIBUTES.write_text(attributes_text())
    return 0


def check_attributes() -> int:
    if not ATTRIBUTES.is_file() or ATTRIBUTES.read_text() != attributes_text():
        print(".gitattributes differs from the GENERATED list; run tools/regen_generated.py --write",
              file=sys.stderr)
        return 1
    return 0


# Checker pins


def _lock() -> dict:
    return json.loads(LOCK.read_text())


def _write_lock(lock: dict) -> None:
    LOCK.write_text(json.dumps({key: sorted(set(values)) for key, values in lock.items()}, indent=2) + "\n")


def _service_digest() -> str:
    sys.path.insert(0, str(ROOT))
    from ve.backends.lean_service import DEFAULT_EXECUTABLE, executable_sha256
    return executable_sha256(DEFAULT_EXECUTABLE)


def _rust_digest(build: bool) -> str | None:
    sys.path.insert(0, str(ROOT / "tools"))
    import rust_build
    if build:
        done = subprocess.run([PY, "tools/rust_build.py"], cwd=ROOT)
        if done.returncode:
            return None
    return rust_build.digest(rust_build.RELEASE_BINARY) if rust_build.RELEASE_BINARY.is_file() else None


def pin_checkers() -> int:
    """Pin the built `ve_service` and (unless VE_REGEN_NO_RUST is set) the rebuilt Rust release binary."""
    lock = _lock()
    lock.setdefault("ve_service", []).append(_service_digest())
    if not os.environ.get("VE_REGEN_NO_RUST"):
        digest = _rust_digest(build=True)
        if digest is None:
            print("checker-pins: the Rust release build failed", file=sys.stderr)
            return 1
        lock.setdefault("rust_jsonl", []).append(digest)
    _write_lock(lock)
    return 0


def check_pins() -> int:
    lock, problems = _lock(), []
    if _service_digest() not in lock.get("ve_service", ()):
        problems.append("the built ve_service is not pinned")
    if not os.environ.get("VE_REGEN_NO_RUST"):
        digest = _rust_digest(build=False)
        if digest is None or digest not in lock.get("rust_jsonl", ()):
            problems.append("the Rust release binary is missing or not pinned (python3 tools/rust_build.py)")
    for problem in problems:
        print(f"checker-pins: {problem}", file=sys.stderr)
    return 1 if problems else 0


# The assurance manifest's decoder pins, checked by their tests.
ASSURANCE_PIN_TESTS = ("tests/test_assurance_manifest.py::test_decoder_files_are_pinned_whole",
                       "tests/test_assurance_manifest.py::test_trusted_decoder_line_ranges_are_pinned")


def check_assurance_pins() -> int:
    sys.path.insert(0, str(ROOT / "tools"))
    import nested_pytest
    return subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", *ASSURANCE_PIN_TESTS]),
                          cwd=ROOT, env=nested_pytest.environment(os.environ)).returncode


# Merging


class Conflict(Exception):
    """Both sides changed one JSON value differently."""


_MISSING = object()


def _key_field(*lists) -> str | None:
    """A field that names every element of every list uniquely (records such as operations or files)."""
    for field in ("id", "file", "name", "path"):
        if all(all(isinstance(item, dict) and isinstance(item.get(field), str) for item in items)
               and len({item[field] for item in items}) == len(items) for items in lists):
            return field
    return None


def _text(value) -> str:
    if value is _MISSING:
        return "<missing>"
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def merge_json(base, ours, theirs, path="$", trust_files=False):
    """Three-way merge of JSON values: a side's change wins over the base; objects merge per key; lists of
    records merge per record key; other lists keep both sides' additions and drop either side's removals;
    a value both sides changed differently raises Conflict."""
    # Trust-file counts are independent changes to a measured ledger. Apply both deltas even when
    # they happen to have the same value; a deletion versus a change still reaches Conflict below.
    if (trust_files and type(ours) is int and type(theirs) is int
            and (base is _MISSING or type(base) is int)):
        return ours + theirs - (0 if base is _MISSING else base)
    if ours is _MISSING or theirs is _MISSING:
        if ours is theirs:
            return ours
    elif _text(ours) == _text(theirs) and not (trust_files and isinstance(ours, dict)):
        return ours
    if base is not _MISSING and ours is not _MISSING and _text(base) == _text(ours):
        return theirs
    if base is not _MISSING and theirs is not _MISSING and _text(base) == _text(theirs):
        return ours
    if base is _MISSING and ours is _MISSING:
        return theirs
    if base is _MISSING and theirs is _MISSING:
        return ours
    if isinstance(ours, dict) and isinstance(theirs, dict) and isinstance(base, (dict, type(_MISSING))):
        base = base if isinstance(base, dict) else {}
        merged = {}
        for key in [*ours, *(k for k in theirs if k not in ours), *(k for k in base if k not in ours and k not in theirs)]:
            value = merge_json(base.get(key, _MISSING), ours.get(key, _MISSING), theirs.get(key, _MISSING),
                               f"{path}.{key}", trust_files and (path != "$" or key == "files"))
            if value is not _MISSING:
                merged[key] = value
        if list(ours) == sorted(ours) and list(theirs) == sorted(theirs):  # a sorted map stays sorted
            merged = dict(sorted(merged.items()))
        return merged
    if isinstance(ours, list) and isinstance(theirs, list) and isinstance(base, (list, type(_MISSING))):
        base = base if isinstance(base, list) else []
        field = _key_field(base, ours, theirs)
        if field is not None:
            merged = merge_json({b[field]: b for b in base}, {o[field]: o for o in ours},
                                {t[field]: t for t in theirs}, path, trust_files)
            return list(merged.values())  # in key order when both sides were (the map merge keeps it)
        before = {_text(item) for item in base}
        removed = (before - {_text(item) for item in ours}) | (before - {_text(item) for item in theirs})
        merged, keys = [], set()
        for item in [*ours, *theirs]:
            key = _text(item)
            if key not in removed and key not in keys:
                merged.append(item)
                keys.add(key)
        if all(type(item) is str for item in merged) and ours == sorted(ours) and theirs == sorted(theirs):
            merged.sort()
        return merged
    raise Conflict(f"{path}: both sides changed it ({_text(ours)[:80]} / {_text(theirs)[:80]})")


def _json_format(text: str) -> tuple:
    """(indent, ensure_ascii) that reproduce `text` from its value, else the indent of its second line and
    whether it escapes non-ASCII text."""
    value = json.loads(text)
    for indent in (2, 1, None, 4):
        for ascii_ in (False, True):
            if json.dumps(value, indent=indent, ensure_ascii=ascii_) + "\n" == text:
                return indent, ascii_
    lines = text.splitlines()
    second = lines[1] if len(lines) > 1 else ""
    return (len(second) - len(second.lstrip(" ")) or None), "\\u" in text


# Values derived from the rest of a JSON ledger: both sides of a merge change them, so the merge ignores them
# and recomputes them from the merged ledger. {path: ((keys to the value, its function), ...)}.
def _decoder_total(manifest: dict) -> int:
    # Importing assurance_manifest loads ve.assurance, which reads the still-conflicted manifest
    # during --resolve. Keep this arithmetic pure until every merged file has been written.
    return sum(end - start + 1 for entry in manifest["lean_decoders"]["files"]
               for start, end in entry["ranges"])


def _trust_totals(baseline: dict) -> dict:
    sys.path.insert(0, str(ROOT / "tools"))
    from trust_map import totals
    return totals(baseline["files"])


def _trust_budget(baseline: dict) -> dict:
    sys.path.insert(0, str(ROOT / "tools"))
    from trust_map import budget
    return budget(_trust_totals(baseline))


def _check_concurrent_trust_allowances(base: dict, ours: dict, theirs: dict) -> None:
    """A pending allowance may be folded into file counts on at most one side.

    `trust_map.py --write` removes each signed entry after measuring the tree. If both
    branches consume the same base entry, adding their file deltas counts that growth
    twice. No per-file merge can distinguish that shared growth from independent work.
    """
    if not all(isinstance(side, dict) for side in (base, ours, theirs)):
        return
    counts = [Counter(_text(entry) for entry in side.get("signed", []))
              for side in (base, ours, theirs)]
    for entry, n in counts[0].items():
        if counts[1][entry] < n and counts[2][entry] < n:
            raise Conflict(f"$.signed: both sides consumed base allowance {entry[:80]}")


DERIVED = {
    "ve/assurance-manifest.json": ((("lean_decoders", "total_lines"), _decoder_total),),
    "docs/trust-baseline.json": ((("totals",), _trust_totals), (("budget",), _trust_budget)),
}


# The key a ledger's derived values are computed from. AR-4's budget file has no per-file counts: its budget is
# the merge train's measurement (`trust_map.py --write`), merged as a value, not derived from the file.
DERIVED_FROM = {"docs/trust-baseline.json": "files"}


def _derived(path: str, value, new=None):
    """Set the derived value of `value` (a ledger) to `new`, or, with `new` None, to its recomputation."""
    source = DERIVED_FROM.get(path)
    if path not in DERIVED or not isinstance(value, dict) or (source is not None and source not in value):
        return value
    for keys, compute in DERIVED[path]:
        node = value
        for key in keys[:-1]:
            node = node.get(key) if isinstance(node, dict) else None
        if isinstance(node, dict) and keys[-1] in node:
            node[keys[-1]] = compute(value) if new is None else new
    return value


def merge_text(path: str, base: str, ours: str, theirs: str) -> tuple[str, bool]:
    """(merged text, clean) of a generated file by its entry's strategy."""
    entry = owner(path)
    if entry is None or entry.merge == "regenerate":
        return ours, True
    if entry.merge == "union":
        with tempfile.TemporaryDirectory(prefix="ve-merge-") as directory:
            files = []
            for name, text in (("ours", ours), ("base", base), ("theirs", theirs)):
                file = Path(directory) / name
                file.write_text(text)
                files.append(str(file))
            done = subprocess.run(["git", "merge-file", "--union", "-p", *files], capture_output=True, text=True)
            return done.stdout, done.returncode == 0
    sides = [_derived(path, json.loads(text), 0) if text.strip() else _MISSING for text in (base, ours, theirs)]
    try:
        if path == "docs/trust-baseline.json":
            _check_concurrent_trust_allowances(*sides)
        merged = _derived(path, merge_json(*sides, trust_files=path == "docs/trust-baseline.json"))
    except Conflict as exc:
        print(f"{path}: {exc}", file=sys.stderr)
        return ours, False
    indent, ascii_ = _json_format(ours)
    return json.dumps(merged, indent=indent, ensure_ascii=ascii_) + "\n", True


def merge_driver(base: str, ours: str, theirs: str, path: str) -> int:
    """git's `ve-generated` driver: write the merge of %O and %B into %A; exit 1 on a conflict."""
    read = lambda name: Path(name).read_text() if Path(name).is_file() else ""  # noqa: E731
    text, clean = merge_text(path, read(base), read(ours), read(theirs))
    Path(ours).write_text(text)
    return 0 if clean else 1


def install_driver() -> int:
    for key, value in ((f"merge.{DRIVER}.name", "VE generated files: merge by strategy, then regenerate"),
                       (f"merge.{DRIVER}.driver", "python3 tools/regen_generated.py --merge-driver %O %A %B %P")):
        subprocess.run(["git", "config", key, value], cwd=ROOT, check=True)
    print(f"installed merge driver {DRIVER}")
    return 0


# Running writers and checks


def _run(entry: Generated, steps, root: Path = ROOT) -> int:
    for step in steps:
        if isinstance(step, str):  # a function of this module
            code = globals()[step]()
        else:
            code = subprocess.run(list(step), cwd=root / entry.cwd).returncode
        if code:
            return code
    return 0


def _check_by_rewriting(entry: Generated, root: Path = ROOT) -> int:
    """Rewrite the entry's files, compare them with the committed ones, and put the committed ones back."""
    before = {path: path.read_bytes() for path in owned_files(entry, root)}
    try:
        code = _run(entry, entry.write, root)
        after = {path: path.read_bytes() for path in owned_files(entry, root)}
    finally:
        for path in set(owned_files(entry, root)) - set(before):
            path.unlink()
        for path, data in before.items():
            path.write_bytes(data)
    if code:
        return code
    stale = sorted(str(path.relative_to(root)) for path in before.keys() | after.keys()
                   if before.get(path) != after.get(path))
    for path in stale:
        print(f"{entry.name}: {path} is stale", file=sys.stderr)
    return 1 if stale else 0


def selected(only, skip) -> list[Generated]:
    names = {entry.name for entry in GENERATED}
    unknown = (set(only or ()) | set(skip or ())) - names
    if unknown:
        raise SystemExit(f"unknown entries: {sorted(unknown)} (see --list)")
    return [entry for entry in GENERATED if (not only or entry.name in only) and entry.name not in (skip or ())]


def write(entries) -> list[str]:
    failed = []
    for entry in entries:
        if entry.write is None:
            continue
        print(f"== write {entry.name}", flush=True)
        if _run(entry, entry.write):
            failed.append(entry.name)
            break  # later entries read this one's output
    return failed


def check(entries) -> list[str]:
    failed = []
    for entry in entries:
        print(f"== check {entry.name}", flush=True)
        if entry.check is not None:
            code = _run(entry, entry.check)
        elif entry.write is not None:
            code = _check_by_rewriting(entry)
        else:
            continue
        if code:
            failed.append(entry.name)
    return failed


# Finishing a merge


def _git(root: Path, *args) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout


def _stage(root: Path, path: str, number: int) -> str:
    done = subprocess.run(["git", "show", f":{number}:{path}"], cwd=root, capture_output=True, text=True)
    return done.stdout if done.returncode == 0 else ""


def resolve(entries, root: Path = ROOT) -> int:
    """Finish the merge in progress in `root` (see the module docstring); `entries` are the writers and checks
    to run after the conflicted generated files are merged."""
    if subprocess.run(["git", "rev-parse", "-q", "--verify", "MERGE_HEAD"], cwd=root,
                      capture_output=True).returncode:
        print("regen_generated --resolve: no merge in progress (run git merge --no-commit first)", file=sys.stderr)
        return 2
    unmerged = sorted(set(_git(root, "diff", "--name-only", "--diff-filter=U").split()))
    retired = [path for path in unmerged if path in RETIRED]
    unmerged = [path for path in unmerged if path not in RETIRED]
    others = [path for path in unmerged if owner(path) is None]
    if others:
        print("regen_generated --resolve: conflicts outside the generated files (agent sync needed):",
              *others, sep="\n  ", file=sys.stderr)
        return 2
    merged = {}
    for path in unmerged:
        text, clean = merge_text(path, _stage(root, path, 1), _stage(root, path, 2), _stage(root, path, 3))
        if not clean:
            print(f"regen_generated --resolve: {path} needs a person or the sync agent", file=sys.stderr)
            return 2
        merged[path] = text
    for path, text in merged.items():  # nothing is written unless every conflicted file merged
        (root / path).write_text(text)
        print(f"resolved {path} ({owner(path).merge})")
    for path in retired:
        _git(root, "rm", "-q", "-f", "--", path)
        print(f"resolved {path} (deleted: {RETIRED[path]})")
    failed = write(entries) or check(entries)
    if failed:
        print(f"regen_generated --resolve: failed: {', '.join(failed)}", file=sys.stderr)
        return 1
    tracked = set(_git(root, "ls-files").split())
    # Only patterns that name a file (git refuses a pathspec that matches nothing).
    patterns = [f":(glob){pattern}" for entry in GENERATED for pattern in entry.paths
                if any(root.glob(pattern)) or any(fnmatch.fnmatchcase(name, pattern) for name in tracked)]
    _git(root, "add", "-A", "--", *unmerged, *patterns)
    remaining = _git(root, "diff", "--name-only", "--diff-filter=U").split()
    if remaining:
        print("regen_generated --resolve: still unmerged:", *remaining, file=sys.stderr)
        return 1
    print("regen_generated --resolve: generated files merged, regenerated and checked; commit with "
          "git commit --no-edit")
    return 0


def listing() -> str:
    rows = []
    for entry in GENERATED:
        show = lambda steps: "; ".join(  # noqa: E731
            f"{step}() in this script" if isinstance(step, str) else
            " ".join("python" if part == PY else part for part in step) for step in steps) if steps else "-"
        rows.append(f"{entry.name} [{entry.merge}] {', '.join(entry.paths) or '(no files)'}\n"
                    f"    write: {show(entry.write)}{'  (cwd ' + entry.cwd + ')' if entry.cwd != '.' else ''}\n"
                    f"    check: {show(entry.check) if entry.check else 'rewrite and compare' if entry.write else '-'}"
                    + (f"\n    note: {entry.note}" if entry.note else ""))
    return "\n".join(rows)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--list", action="store_true")
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    action.add_argument("--resolve", action="store_true")
    action.add_argument("--merge-driver", nargs=4, metavar=("BASE", "OURS", "THEIRS", "PATH"))
    action.add_argument("--install-driver", action="store_true")
    action.add_argument("--owner", metavar="PATH", help="print the entry that owns PATH")
    parser.add_argument("--only", action="append", metavar="NAME")
    parser.add_argument("--skip", action="append", metavar="NAME")
    args = parser.parse_args(argv)
    if args.list:
        print(listing())
        return 0
    if args.owner:
        entry = owner(args.owner)
        print(entry.name if entry else "-")
        return 0 if entry else 1
    if args.merge_driver:
        return merge_driver(*args.merge_driver)
    if args.install_driver:
        return install_driver()
    entries = selected(args.only, args.skip)
    if args.resolve:
        return resolve(entries)
    failed = write(entries) if args.write else check(entries)
    if failed:
        print(f"regen_generated: failed: {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"regen_generated: {'wrote' if args.write else 'checked'} {len(entries)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
