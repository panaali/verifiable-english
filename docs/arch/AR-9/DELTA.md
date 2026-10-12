# AR-9 delta: split the assist modules

## User-visible deltas

None. AR-9 moves code between files (plan 4.3: "Code moves, nothing else; public names
re-exported"). No verdict, diagnostic text, wire field, ledger format or CLI output changes, so no
standing ruling (R1 to R11) is invoked and no DRI signature is needed.

The evidence for "nothing else": `evidence/split.json` compares the syntax tree of every
definition in the base `ve/assist/recovery.py` and `ve/assist/session.py` (163 of them) with its
definition at head. 156 are identical. The other 7 are identical once their calls through a
service seam are read as the module names they forward to (`self._evaluate(...)` as
`evaluate(...)`; see below). Every assist test file (`tests/test_assist*.py`, 5 files) is
unchanged and passes.

## The picked readings-route relay fix

`fc30653f` is `c88e4012` from `infra/oom-rootcause`, picked unchanged (REPORT.md, "Relay gate").
It has one delta, and R8 covers it:

| # | Delta | Before | After | Test | Signature |
|---|---|---|---|---|---|
| 1 | A readings-route answer from Lean with an empty fill `label`, an empty conflict target, or a repeated `over` name is refused as CheckerUnavailable. No genuine answer has these: the relay gate's genuine fixtures all pass | relayed as given | CheckerUnavailable | `test_readings_route_refuses_empty_labels_targets_and_repeated_over_names`, `test_readings_route_shape_agrees_with_lean_on_empty_names_and_repeated_over`, `test_unique_string_lists_refuse_duplicate_rule_names`; relay gate 0 failures | SIGNED (R8: Python checks schema typing and binding, and refuses an empty row) |

## Changes that are not user-visible

1. **Seams.** Tests replace five names of the `ve.assist.recovery` module
   (`OPERATION_SECONDS`, `checked_wording`, `evaluate`, `formula_to_data`, `formula_from_data`),
   for example to inject a delay and prove a deadline covers a step. Code moved to another
   module would read that module's own names, so those replacements would no longer reach it.
   `RecoveryService` in `recovery.py` therefore has five forwarders (`_operation_seconds`,
   `_checked_wording`, `_evaluate`, `_formula_to_data`, `_formula_from_data`) that read the
   `recovery` names when called, and the 7 moved definitions that used those names call the
   forwarders. With no replacement in place each forwarder returns exactly what the direct call
   did. The session's equivalent names (`prove_entailment`, `ground_countermodel`,
   `find_countermodel`, used by `_decide`) need no seam: every method that reads them stays in
   `session.py`.
2. **Defining modules.** Classes and functions that moved report their new module in
   `__module__` (for example `ve.assist.session_state.AssistError`, `ve.assist.recovery_journal.Unit`).
   Every one stays importable from its old module and is the same object there. No ledger,
   record or output contains a class's module path. The assurance registry
   (`ve/assurance.py`, which records `fn.__module__`) has no assist entries.
3. **`checker_build`.** `ve/argument.py:_checker_build` digests every Python source under `ve/`,
   so it changes, as it does for any edit under `ve/`.

## Where the reviewed exception handlers are

`ve/assurance-manifest.json` reviews six broad handlers by `file:Class.method`. Four
in-flight branches change the manifest (lean-first/b16d, question-answering/integrate,
readings-defaults/rd4b, readings-defaults/rd6b), so AR-9 leaves it alone. Those six methods stay
on `RecoveryService` in `recovery.py` (`_command_uncached`, `_legacy_command`, `_replay_inner`,
`request_proposer`) and on `AssistSession` in `session.py` (`apply`, `paraphrase_formula`).
`tests/test_assist_split.py::test_reviewed_broad_handlers_stay_where_the_manifest_names_them`
reads the manifest and checks this.
