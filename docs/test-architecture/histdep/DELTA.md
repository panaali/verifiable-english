# tarch-histdep: user-visible deltas

VE's own outputs: **none**. No Lean, `ve/` or Rust file changes, so no verdict, wording, code, field, fault order,
CPU or trust count of the checker changes (trusted lines: unchanged, no growth). What changes is the gate's record
and its rerun rule.

Not deltas, so not in the table: the new inventory `tests/history-dependent.json`, its saved map extract
`tests/history-map.json` and their lint (`tools/history_tests.py`, run by `tests/test_history_tests.py` in the gate),
which add a check and skip nothing; and the run cache's entry format 2 (`tools/run_cache.py`), a private cache in the
git common directory whose entries for runs that read history now also bind the commit, the runner and git's version.
No test's outcome changes because of either. Fix round 1 widens two private checks, again only toward listing or
binding more: the lint follows the source a unit can run, and the read recorder binds a run whose process names
git in any word of its arguments (`tools/git_words.py`). Fix round 2 widens the lint again, toward listing more: a
name bound to the git program in one module counts where another module uses it.

| # | Delta | Ruling | Test |
|---|-------|--------|------|
| 1 | The gate record (gate-result.json and its git note) gains `runner` (`system`, `machine`, `node` of the machine the gate ran on) and, under `toolchains`, `git` (the first line of `git --version`) and `paths.git`; gate.log gains the `[gate] git version: <git> --version` line. Nothing is removed or renamed; the record's readers take named members only (tools/since_pass.py, tools/gate_collection.py, tools/batch_evidence.py, manage-agents gaterec.py, mac-gate-post.py, chain-gate.sh, review-ready.py). | R3 (DRI-RULINGS.md): information added, nothing removed or renamed; each field equals the true value; it names no request id. | tests/test_gate_rerun.py::test_a_full_gate_records_its_tree_and_mode (the runner equals `platform`'s values), tests/test_gate_integrity.py::test_poisoned_toolchain_variables_do_not_reach_real_tools (git's version line and its path in the system directories), tests/test_gate_rerun.py::test_anything_but_test_failures_on_this_tree_runs_the_full_gate[another git] |
| 2 | `tools/gate.py --rerun-failed` refuses a previous gate of the same tree on another commit or another runner (or one whose record names no runner), and runs the full gate instead, saying why in `rerun_failed.refused`. Before, the tree and toolchains had to match but the commit and runner did not. | R13 (DRI-RULINGS.md): a rerun counts only for the SAME commit; the refusal enforces that, and runs more, never less. | tests/test_gate_rerun.py::test_the_same_tree_on_another_commit_or_runner_runs_the_full_gate |
