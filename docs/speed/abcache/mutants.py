"""Seeded bugs for the base-record cache: one per rule it claims; each must make a test of
tests/test_lean_first_diff_cache.py fail. Each file is restored byte for byte afterwards.

    uv run python docs/speed/abcache/mutants.py > docs/speed/abcache/evidence/mutants.json
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools import nested_pytest  # noqa: E402
CACHE, DIFF = "tools/lean_first_cache.py", "tools/lean_first_diff.py"
TESTS = "tests/test_lean_first_diff_cache.py"
# (rule, file, text, replacement, the test that must fail)
MUTANTS = [
    ("a hit re-validates every line (record_problem)", CACHE, "records = diff.load_text(text, name)",
     "records = {tuple(r[k] for k in ('corpus', 'authority', 'case', 'op')): r for r in map(json.loads, text.splitlines())}",
     "test_a_damaged_entry_is_a_miss_and_is_replaced[retyped]"),
    ("the commit is keyed", CACHE, '"commit": git("rev-parse", "HEAD").strip()', '"commit": "any"',
     "test_each_key_part_changed_is_a_miss[change_commit]"),
    ("the Lean build key is keyed", CACHE, '"lean_build": lean,', '"lean_build": None,',
     "test_each_key_part_changed_is_a_miss[change_lean]"),
    ("the recorder is keyed", CACHE, '"recorder": recorder,', '"recorder": None,',
     "test_each_key_part_changed_is_a_miss[change_recorder]"),
    ("the corpus inputs are keyed", CACHE, '"corpus_sha256": corpus_sha256}', '"corpus_sha256": None}',
     "test_each_key_part_changed_is_a_miss[change_corpus]"),
    ("the authority is keyed", CACHE, '"authority": authority,\n', '"authority": "any",\n',
     "test_the_authority_is_part_of_the_key"),
    ("the environment is keyed", CACHE, 'if name.startswith("VE_") and', 'if name.startswith("XX_") and',
     "test_each_key_part_changed_is_a_miss[change_env]"),
    ("the Python version is keyed", CACHE, '"python": sys.version,', '"python": None,',
     "test_each_key_part_changed_is_a_miss[change_python]"),
    ("a dirty root is neither read nor stored", CACHE, 'if git("status", "--porcelain"):', "if False:",
     "test_a_dirty_root_is_neither_read_nor_stored"),
    ("the stored segment's digest is checked", CACHE, 'meta.get("sha256") != _sha256(data) or ', "",
     "test_a_damaged_entry_is_a_miss_and_is_replaced[flipped byte]"),
    ("a hit holds every case (completeness)", CACHE,
     "diff.completeness(name, records, diff.expected_cases(diff.ROOT, [corpus], [authority]))", "pass",
     "test_a_damaged_entry_is_a_miss_and_is_replaced[a whole record dropped]"),
    ("a hit is the recorder's canonical text", CACHE, "if diff.line(row) != line + \"\\n\":", "if False:",
     "test_a_damaged_entry_is_a_miss_and_is_replaced[not canonical]"),
    ("a hit's records read the corpus's sources", CACHE, 'if row["source_sha256"] != source_of(row["case"]):',
     "if False:", "test_a_damaged_entry_is_a_miss_and_is_replaced[another source]"),
    ("a damaged entry is set aside and replaced", CACHE, "        os.rename(entry, refused)\n", "",
     "test_a_damaged_entry_is_a_miss_and_is_replaced[flipped byte]"),
    ("only builds the root's lock pins are stored", CACHE, '            pinned_checkers(root, shared["checkers"])\n',
     "", "test_an_unpinned_build_is_not_stored"),
    ("the recording's scratch path is stored portable", CACHE,
     'data = text.replace(_stem(out), SCRATCH + ".").encode()', "data = text.encode()",
     "test_hit_returns_the_records_a_recording_writes"),
    ("entries are 0644 files", CACHE, "os.chmod(path, 0o644)", "os.chmod(path, 0o600)",
     "test_store_layout_names_every_key_part"),
    ("no cache: record runs as before", DIFF, 'cache = args.cache or os.environ.get("VE_AB_CACHE")',
     'cache = args.cache or os.environ.get("VE_AB_CACHE") or "/nonexistent"',
     "test_without_a_cache_record_runs_as_before"),
    ("a child recording is split at newlines only", CACHE, 'for line in text.split("\\n")[:-1]:  # not',
     "for line in text.splitlines():  # not", "test_hit_returns_the_records_a_recording_writes"),
    ("the key is the same after recording before anything is stored", CACHE, "if root_key(root) != shared:",
     "if False:", "test_a_key_that_changes_while_recording_stores_nothing"),
    ("a failed recording writes and stores nothing", CACHE, "        if code:\n            return code\n", "",
     "test_a_failed_recording_writes_and_stores_nothing"),
    ("prune keeps the entries used lately", CACHE, "os.utime(entry)  # used now", "pass  # used now",
     "test_prune_keeps_what_was_stored_or_used_lately"),
    # review F1: the checker builds a recording ran are keyed, not the lock's membership alone
    ("the checker builds are keyed (review F1)", CACHE, '"checkers": checker_builds(root)}', '"checkers": None}',
     "test_a_base_recorded_with_an_old_pinned_build_is_not_reused"),
    ("every Lean executable is keyed (review F1)", CACHE, 'found[f"lean/{path.name}"] = _file_sha256(path)',
     "pass", "test_each_key_part_changed_is_a_miss[change_route_build]"),
    ("an overridden checker is keyed by its contents (review F1)", CACHE,
     "found[name] = _file_sha256(Path(os.environ.get(variable) or root / default))",
     "found[name] = os.environ.get(variable) or default", "test_each_key_part_changed_is_a_miss[change_rust_override]"),
    # review F2: `sources` itself is tested, branch by branch
    ("a pilot's companion files are keyed (review F2)", CACHE, "_json_sha256([blobs, beside])", "_json_sha256([blobs])",
     "test_each_input_a_corpus_reads_changes_its_key[pilots]"),
    ("the discourse corpus file is keyed (review F2)", CACHE, "return diff.digest(diff.ROOT / path), by_case.get",
     'return "0" * 64, by_case.get', "test_each_input_a_corpus_reads_changes_its_key[discourse]"),
    ("a conformance file is keyed (review F2)", CACHE,
     'files = {name: diff.digest(root / f"conformance/{name}.json") for name in diff.CONFORMANCE}',
     'files = {name: "0" * 64 for name in diff.CONFORMANCE}',
     "test_each_input_a_corpus_reads_changes_its_key[conformance]"),
]


def main() -> int:
    rows = []
    for rule, name, text, replacement, test in MUTANTS:
        path = ROOT / name
        original = path.read_bytes()
        source = original.decode()
        assert source.count(text) == 1, (rule, text)
        path.write_text(source.replace(text, replacement))
        try:
            done = subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", "-x", f"{TESTS}::{test}"]),
                                  cwd=ROOT, env=nested_pytest.environment(os.environ), capture_output=True, text=True)
        finally:
            path.write_bytes(original)
        rows.append({"rule": rule, "file": name, "test": f"{TESTS}::{test}", "failed": done.returncode == 1,
                     "summary": (done.stdout.strip().splitlines() or [""])[-1]})
    print(json.dumps(rows, indent=1))
    return 0 if all(row["failed"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
