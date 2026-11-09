# gate-mutant-id-renumber: pair renumbered mutant ids by their text

Status: built, ready for the chain's gate. Option (A). Python only (tools/gate_collection.py, tools/gate.py, two
mutant test modules' hooks). Nothing reserved, no DELTA row (tooling). Open: other position-numbered mutant
modules opt in by adding the hook; this item adds it to the two named in the task.

## Why (A), not (B)

- (A) handles every module that adds a hook, and every later insertion, with no renaming commit. (B) needs a
  renaming commit with one `Test-removed:` trailer, plus a pairing table, for every existing mutant id (73 + 41
  in the two named files alone). The `EQUIVALENT` keys of tests/test_events_wire_mutants.py would also become
  opaque hashes.
- (A) keeps the `Test-removed:` rule for real removals: a lost id whose text is gone pairs with nothing, so it
  is refused unless its own trailer records it, while its renumbered siblings still pair. Matching is one to
  one, so every gone base text leaves a lost id that is refused or recorded. That makes it never weaker than
  the id check it refines. The one exception is a kept id (same id at both sides) whose base text is gone or
  unknown: no lost id shows that loss, so its function pairs nothing and every lost id there stays refused.
- The adv0845 rule (match mutants by definition, operator and text, never by id) becomes the tool's own check.

## What it does

- A test module may define `mutant_cases()`: {case parameter id: its definition, operator and text}
  (`CASES_HOOK`). tests/test_packs_guard_mutants.py returns `[definition, find, replace]` per id.
  tests/test_events_wire_mutants.py returns `[operator, definition, replaced lines, replacing lines]` per name
  (the lines are the diff against Wire.lean, so they do not depend on position).
- `missing()` passes each lost id that no trailer records to `Changes.renumbered`. That runs the hook in a
  scratch worktree of the base and in the head's tree (`root` for the worktree side). `pair_cases` then
  matches cases one to one by text, kept ids first, and a trailer-recorded id takes no head case. A lost id
  whose text is gone stays unpaired. A kept id whose text is gone or unknown makes its function pair nothing.
  A side with no tree, or no hook, or a hook that fails, has no texts, and a case with no text never pairs.
- `Verdict.paired` (base id -> head id) is in the gate result's `collection` record. The gate log prints
  `[gate] renumbered: <base id> -> <head id>`, and `gate_collection.py --check` prints the same table.

## Evidence

- Probe on the real module (`uv run python /tmp/gmr-probe/probe.py $PWD`, script not kept): two `eventsArray`
  mutants inserted at position 28 of tests/test_packs_guard_mutants.py's list, as in et-4b. Result:
  `41 43 lost 12 refused 0` and 12 `renumbered:` rows (coherenceLabels-28 -> coherenceLabels-30, ...,
  kindCase-40 -> kindCase-42).
- Hook texts are unique: 73 of 73 (events wire) and 41 of 41 (packs) (`uv run python -c` over both
  `mutant_cases()`).
- Collection of the changed test files, base b8266ee19 vs HEAD: 222 -> 234 ids, 0 lost, 12 added (the new
  test's cases; `pytest --collect-only` in a scratch worktree of the base).
- Tests: `uv run pytest tests/test_gate_collection_renumber.py tests/test_gate_collection.py`: 112 passed.
  The selected tests on the Mac runner are listed in the build report.
- Seeded bugs: docs/gate-mutant-id-renumber/seeded-mutants.json (S1-S11, all Python). Each one fails its test.
  S1 is the task's "pairing by id only". S7-S11 are the review fix's (below).

## Size

`git diff --numstat $(git merge-base HEAD main)`, generated files (docs/codemap, tests/history-dependent.json)
and this directory excluded: 199 lines added (task limit: under 200).

## Review fix (F1, B)

- F1: a deleted or edited mutant refused every renumbered sibling in its function, even with its own
  `Test-removed:` trailer. Fix in `pair_cases` (one place): the kept ids match first, and only a kept id whose
  text is gone or unknown blocks the function (the `[kept-id-reused]` hole, and now `[no-text]`). A lost id whose
  text is gone stays unpaired: refused, or recorded by its trailer. A trailer-recorded id takes no head case
  (`[trailer-on-a-twin]`), and a head case with no text is never claimed.
- PROBE F1 (the review's command): before, `AssertionError: ({}, [c-2, d-3])`; after, it passes. Regression
  row `[deleted-with-trailer]`. Changed rows: `[text-changed]` and `[case-deleted]` now pair their siblings.
  New rows: `[kept-first]`, `[no-text]`, `[trailer-on-a-twin]`.
- F2-F4 (C) and the follow-ups are not in this fix.
