# arch-20261105-2: raising `actions_version` stops rewriting recorded test files

No DRI signature is reserved. DELTA.md has R7 rows only (A/B records unavailable on both sides with identical outputs).
`batch_evidence.py --check` stops only at the missing `[gate]`, which is saved after the chain's gate (see "After the
gate"). With a stub gate file it reported only the four gate errors, so scope, seeded mutants and A/B pass.

Debt batch (PIPELINE-LIMITS L175, backlog arch-actions-stamp), launched by the architecture pass of 2026-11-05. Not a
plan batch.

## Measured outcome

The measured raise (deliverable 5). Command on a scratch tree: `python tools/english_grammar_gen.py --write
--actions-version 46`, then what the tree needs to pass again, then `git diff --stat`.

| | Files in `git diff --stat` | Recorded test files among them | Evidence |
|---|---|---|---|
| Before (main `e9a6ec8d5`) | 23 | 18: 17 `tests/fixtures/ask/*.json`, 12 `#guard pin` lines of `lean/VE/Senses/RunExamples.lean` re-pinned by hand; plus the S3 comparison rewritten | `evidence/bump-before.txt` |
| After (this branch, `4a1c42e88`) | 5 | 0 | `evidence/bump-after.txt` |

The 5 after the raise are the generator's own 2 outputs (`lean/VE/EnglishGrammar/Fixed/Version.lean`,
`ve/english_grammar/LOCK.json`) and 3 generated files that `regen_generated.py --write` rewrites (exit 0). Afterwards,
`lake build VE.Senses.RunExamples` succeeds unchanged, `ask_fixtures.py --check` replays 18 of 18 and the five
fixture and report test files pass: 123 passed (`evidence/bump-after.txt`). What still changes, one row each. The
batch does not widen to chase them. Commit counts are `git log --oneline --no-merges --since=2026-10-31 <rev> -- <file>
| wc -l`:

| File | Why it changes | Owner | Commits since 2026-10-31 (at `e9a6ec8d5` / at main `e433588f5`) |
|---|---|---|---|
| `lean/VE/EnglishGrammar/Fixed/Version.lean` | the generator's output (the version itself) | `english_grammar_gen.py` | 10 / 10 |
| `ve/english_grammar/LOCK.json` | the generator's output (the lock) | `english_grammar_gen.py` | 12 / 12 |
| `conformance/english-lean/s3-fixture-comparison.json` | its records carry Lean's `actions_version`, which one test reads (deliverable 4) | generated entry `english-s3-comparison` (new) | 8 / 8 |
| `lean/checkers.lock` | pins the rebuilt `ve_service` | generated entry `checker-pins` | 121 / 127 |
| `lean/declarations.txt` | a line of `Fixed/Version.lean` | generated entry `lean-statements` | 109 / 128 |

The why-now figures were measured again first (`docs/infra/arch-20261105-2/measure.py --since 2026-10-31 --rev main`
at `e9a6ec8d5`, output `evidence/before.json`). They match the task:

- `Fixed/Version.lean` changed in **10** non-merge commits since 2026-10-31.
- **8** commits changed `tests/fixtures/ask/`: **136** file edits, no file added or deleted. Across the parsed JSON of
  every edit (commit against parent), only two JSON paths ever changed: `/result/identities/actions_version` (**136**)
  and `/seconds` (**95**). No edit changed an answer.
- `RunExamples.lean` pins: **131** `#guard pin` hash changes in 18 commits; 108 of them are in the 9 version commits
  that touch the file. **120** are explained by the version alone: the hash of the answer with the version removed is
  equal on both sides. That is 108 in version commits (76 computed directly against the built head answers; the other
  32, in 4 commits that also changed `JudgmentLines.lean` or `Run.lean`, computed in each commit's own built tree,
  `before.json` `pins.built`). The other 12 are in `aa6234fb6`, which re-pinned 12 pins that were stale under version
  35 (`evidence/stale-aa6234fb6.json`). The remaining **11** are real changes: two Senses B6b commits
  (`a5443602f`: 3, `1ea08edfd`: 8) with the version unchanged.

The corpus A/B against the merge base `e433588f`: **100,531** records the same and **22** unavailable on both sides
with identical outputs (listed, R7), **0** unlisted (`evidence/ab.json`, `python -m tools.evidence ab ... --delta
evidence/ab-delta.json`: "ab PASS"). The head recording first had 7 whole-UDHR `document_check` records at the
recorder's 600 s timeout. The machine's load average was 104 to 120 on 32 cores (`uptime`) and the base had been
recorded earlier. They timed out again when re-run 7 at once. Re-run one at a time with the recorder's own
`pilot_check` (`rerun_timeouts.py`), all 7 exit 0, and the re-run head recording is **byte-identical** to the base
recording (SHA-256 `466909e2...` both, `evidence/ab.json` `recordings`).

Trust (D3): `uv run python tools/trust_map.py --check` against `e433588f5109`: "K +0, S +0, D +0, G +0, tied +0,
unclassified +0, trusted +0", "PASS" (`evidence/trust-check.txt`). No allowance was added. The three new
`RunExamples` helpers are classed T in `tools/trust-classes.json`.

## Deliverables

| # | Directive | Commit | Test or evidence |
|---|---|---|---|
| 1 | `tests/fixtures/ask/`: store no `seconds` and no `actions_version`; print seconds while writing; every other field byte-compared in replay | `0f2bea593` | `tests/test_ask_fixtures.py::test_every_recorded_fixture_is_in_the_current_format`, `::test_the_replay_compares_every_field_of_the_answer`; `ask_fixtures.py --check` 18 of 18 |
| 1 | the conversion is mechanical | `0f2bea593` | `evidence/conversion.json` (`convert.py`): 21 fixture files parsed before and after; each differs by exactly `/seconds` and `/result/identities/actions_version` or by nothing (`A1d.json` and the conflict files had neither), `"mechanical": true`. Evidence, not a permanent test |
| 2 | one owner: the loader supplies `actions_version` from `ve/english_grammar/LOCK.json` | `0f2bea593` | `tools/ask_fixtures.py:279` `lock_version()` reads it through `ve.english_grammar.actions_version()`, the lock's one Python reader; `load()` (`:305`) puts it in. `::test_the_loader_takes_the_version_from_the_lock` (writes a lock with another version under `tmp_path`) |
| 2 | replay compares Lean's live answer with the whole recording, version included; another version FAILS | `0f2bea593` | `::test_an_answer_under_another_version_than_the_locks_fails_the_replay`, `::test_the_replay_compares_every_field_of_the_answer` (retypes and changes every leaf, `true` vs `1` included) |
| 2 | a record stores the version-free answer only under the lock's version | `0f2bea593` | `::test_a_record_stores_no_version_and_refuses_another_version_than_the_locks` |
| 2 | relay tests still see a fully typed row | `0f2bea593` | `tests/test_ask_relay.py` and `tests/test_ask_cli.py` load through `ask_fixtures.load`, so each answer has its version back. Both passed in the selected run (below) |
| 2 | other readers found by grep | none | `tests/test_ask_null_free.py:51` reads only `path`, `question` and `case`. `tests/test_question_answering_readability.py:14`, `tests/test_question_answering_measure_report.py:216` and `tools/question_answering_report.py` read neither field (`grep -n "seconds\|actions_version\|identities"`: no match) |
| — | an old-format fixture is refused, naming `tools/ask_fixtures.py --write` | `0f2bea593` | `::test_a_fixture_in_the_old_format_is_refused_by_name[seconds|actions_version|both]` |
| 3 | RunExamples: measure first; if the version explains the pin changes, pin without the version and add one version `#guard` per answer form | `829dabad1` | Measured: 120 of 131 explained (above). `pin` hashes `withoutVersion`. Two `#guard`s compare `versionOf "reading"` and `versionOf "projection"` with `.str VE.EnglishGrammar.Fixed.actionsVersion`. Two more `#guard`s check that `withoutVersion` removes that member and nothing else (put back, it is the answer). 4 `#guard`s added (two version guards, two round trips), 12 pin hashes changed (the 12 answers that carry the version), none removed. Test-class Lean only |
| 4 | S3 comparison: remove the version if nothing reads it, otherwise a generated entry | `3a0713254`, `6ed1cc56a` | Readers: `tests/test_english_lean_s3_compare.py:85` asserts every record's `actions_version` equals the lock's, so the field is read. `tests/test_english_e2_report.py:12` and `tools/difffuzz_corpus.py:39` (an inventory row) do not read it. So the file is the one new entry `english-s3-comparison` in `tools/regen_generated.py`. Its writer now runs under `PYTHONHASHSEED=0`: Lark lists expected terminals in set order, and the rewrite-and-compare check needs one output. `tests/test_english_lean_s3_compare.py::test_the_report_is_the_same_whatever_hash_seed_the_command_starts_under` |
| 5 | the measured raise | `59b5ed076` | `evidence/bump-before.txt` (23 files), `evidence/bump-after.txt` (5) |
| — | generated files only through `regen_generated.py --write` | `4a1c42e88`, `b7c0dbdd4` | the codemap, `.gitattributes`, `lean/declarations.txt` |
| — | `docs/merge-tooling.md` lists every generated entry | `4b63f08f4` | `tests/test_merge_tooling_evidence.py::test_the_generated_file_table_names_every_entry` (its name pattern now admits a digit, for `s3`) |

What is unchanged ("must not change"): `git diff --stat main...HEAD` lists no `ve/` file, no `rust/` file, no file
under `lean/ResponseShape/` and no Lean file except `lean/VE/Senses/RunExamples.lean` and the generated
`lean/declarations.txt`. `tools/trust_mutants.py`, `tests/data/route-cases.jsonl`, `relay-gate-cases.jsonl` and
`binding-answers.jsonl.gz` are not in it. `english_grammar_gen.py --check` is untouched. `tools/regen_generated.py`
gains exactly one entry (+4 lines). No test, fixture or `#guard` is removed:
`uv run python tools/gate_collection.py --check --prebuilt` printed "32497 collected, 32488 at e433588f...; 9 added, 0
removed by a trailer, 0 refused, 0 stale and 0 malformed trailers".

## Seeded bugs

`uv run python tools/mutants.py docs/infra/arch-20261105-2/mutants.json --evidence
docs/infra/arch-20261105-2/evidence/mutants-result.json` on `5058d2609` (after the merge of main): "mutants: 11/11
killed". Each baseline passed first, and each file was restored byte for byte.

| Id | File | Bug | Failing test |
|---|---|---|---|
| Pa (a) | `tools/ask_fixtures.py` | replay leaves `actions_version` out of the comparison | `tests/test_ask_fixtures.py::test_an_answer_under_another_version_than_the_locks_fails_the_replay`, `::test_the_replay_compares_every_field_of_the_answer` |
| Pb (b) | `tools/ask_fixtures.py` | replay leaves `lead` out of the comparison | `::test_the_replay_compares_every_field_of_the_answer` |
| Pc (c) | `tools/ask_fixtures.py` | loader supplies the constant `"45"`, not the lock's | `::test_the_loader_takes_the_version_from_the_lock` |
| Pd (d) | `tools/ask_fixtures.py` | reader accepts an old-format fixture | `::test_a_fixture_in_the_old_format_is_refused_by_name` |
| Pd2 (d) | `tools/ask_fixtures.py` | old-format check misses a recorded `actions_version` | `::test_a_fixture_in_the_old_format_is_refused_by_name` |
| Ps | `tools/ask_fixtures.py` | a record stores an answer under another version | `::test_a_record_stores_no_version_and_refuses_another_version_than_the_locks` |
| Pg | `conformance/english_lean_s3_compare.py` | the report command keeps the caller's hash seed | `tests/test_english_lean_s3_compare.py::test_the_report_is_the_same_whatever_hash_seed_the_command_starts_under` |
| Le (e) | `lean/VE/Senses/RunExamples.lean` | the pin also leaves out `environment_id` | `lake build VE.Senses.RunExamples` fails at the pins |
| Le2 (e) | `lean/VE/Senses/Run.lean` (product, restored) | a pinned answer field other than the version changes (`used` written twice) | `lake build VE.Senses.RunExamples` fails at the pins |
| Lh | `lean/VE/Senses/Run.lean` (product, restored) | the reading answer carries another version than `Fixed.actionsVersion` | `lake build VE.Senses.RunExamples` fails at the version `#guard` (the pins leave it out) |
| Lf (f) | `lean/VE/Senses/RunExamples.lean` | the version `#guard` compares the literal `"45"` | after `english_grammar_gen.py --write --actions-version <next>`, `lake build VE.Senses.RunExamples` fails (it builds unchanged without the bug, `bump-after.txt`) |

## Tests run

- While iterating: the named test files and `lake build VE.Senses.RunExamples` (earlier session).
- After the merge of main: `lake build` (1313 jobs, success), `regen_generated.py --write` (36 entries, exit 0, after
  `rust_build.py`), `python3 lean/audit.py` ("PASS: 782 source files; 8670 named theorem declarations").
- Selected tests, once, on `5058d2609`: `mac-pytest.sh --select -- --base e433588f5 --run` (cloud run
  `arch-20261105-2-5058d260-t127825`). Every shard passed except one test,
  `tests/test_merge_tooling_evidence.py::test_the_generated_file_table_names_every_entry`, which had no table row for
  the new entry. Fixed in `4b63f08f4`; `uv run pytest -q tests/test_merge_tooling_evidence.py`: 5 passed.
- None of the three tests in `main-known-red.txt` is in this batch's area.
- Not run by me: the full gate (`tools/gate.py`). The chain runs it on the final HEAD.

## Coordination

At the end (2026-11-08), I ran `git diff --name-only main...<branch>` for every branch the task names, against this
batch's files. ap-3dc, ci-5, jt-3b, qt-a4b and et-4b share only `tools/trust-classes.json`. df-5 shares
`tools/trust-classes.json`, `.gitattributes` and `tools/regen_generated.py`. at-1b, ps-1c, ps-e1, pc-1g and cmp-s4c are
merged. eff-20261104-1 shares nothing. `git merge-tree --write-tree HEAD <branch>` is clean for ap-3dc, ci-5 and df-5.
jt-3b, qt-a4b and et-4b conflict only in files this batch does not touch (`tests/data/*-cases.jsonl`,
`ve/assurance-manifest.json`, NormDefaults files), so there is no textual overlap. No in-flight branch touches the
fixtures, `RunExamples.lean` or the S3 comparison. The start-of-batch check was done in the earlier session and its
output was not saved. UNVERIFIED beyond the end check above.

## Spec re-read

- "store no `actions_version`", "print it while writing ... without storing it" against the task's deliverable 1:
  `tools/ask_fixtures.py` `stored()` and the `--write` print. Both hold.
- "Lean's answer carrying a different version than the lock must FAIL" against deliverable 2: the replay compares
  the whole answer with `load()`'s entry, which carries the lock's version (Pa).
- "one `#guard` per answer form that `actions_version` equals `Fixed.actionsVersion`" against deliverable 3:
  there are two answer forms (`reading`, `projection`), with one guard each, reading the generated constant (Lf).
- "refuse a fixture still carrying `seconds` or `actions_version` with a message naming `tools/ask_fixtures.py
  --write`" against "In-flight sync": `load()` (Pd, Pd2).
- "keep any edit there to one entry" against deliverable 4: `tools/regen_generated.py` +4 lines, one `Generated(...)`.

## FOLLOW-UP

- CLAUDE.md, "Testing rules that recur in reviews", or `docs/TESTING.md`, should gain one line: *Recorded fixtures
  hold no run-time values (times, versions owned elsewhere): the loader supplies an owned value from its owner, and
  the writer prints a time without storing it.* Not added here: the batch's scope is the fixtures and their readers.
- `lean/declarations.txt` and `lean/checkers.lock` still change on every raise (generated, `--resolve` handles them).
- The whole-UDHR pilot records reach the A/B recorder's fixed 600 s timeout under heavy machine load. A recorder
  option to re-run timeouts serially would replace `rerun_timeouts.py`.

## Self-review against BUILDER-CHECKLIST

1. Fully typed and contained: N.A. No route, schema or relay changed; relay rows keep their version
   (`tests/test_ask_relay.py` passed in the selected run).
2. Deliverables built, no rule broken: PASS (Deliverables table). No Python copy of a Lean decision: the version is
   read from the lock's one reader. No permanent report test. The overlaps are listed under Coordination.
3. Tests can fail: PASS. 11/11 seeded mutants killed (`evidence/mutants-result.json`). The comparator catches a
   changed value and `true` vs `1` (`test_the_replay_compares_every_field_of_the_answer`).
4. Python, Lean and Rust agree: PASS. Corpus A/B: 100,531 records the same, 0 unlisted, re-run head
   byte-identical to the base.
5. R8 binding: N.A. No field Python reads from a Lean answer changed.
6. Gate evidence matches the final HEAD: PASS for the merge and the scope (`evidence/scope.json`, base = merge base).
   The gate is saved after the chain's gate ("After the gate").
7. No unsigned item: PASS. DELTA rows cite R7; no trust growth.
8. Every user-visible change in DELTA: PASS. The A/B shows none; DELTA.md lists only the R7 rows.
9. Test selection: PASS. `tools/select_tests.py --base e433588f5` selects `tests/test_ask_fixtures.py`,
   `tests/test_english_lean_s3_compare.py`, `tests/test_merge_tooling_evidence.py` and `tests/test_senses_*.py`.
10. Lean statements: N.A. There are no theorems. The new `#guard`s are mutated (Le, Le2, Lh, Lf).
11. Budgets fail closed: N.A. There are no budgets. The tests have no sleeps or deadlines (`tmp_path` only).
12. CPU or memory: N.A. The loader adds one dictionary merge per fixture, and no product path changed.
13. Test-removed trailers: PASS. `gate_collection.py --check --prebuilt`: 0 removed, 0 refused, 0 stale, 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS. The loader accepts the current format
    (`test_every_recorded_fixture_is_in_the_current_format`) and refuses the old one. The replay passes under the
    lock's version (`ask_fixtures.py --check`) and fails under another. Spec re-read above.
15. Overclaim, silent cut, new check can fail, limits charged: PASS, PASS, PASS (11 mutants), N.A. (no limits).

## After the gate

The scope, the A/B and the gate must name the commit the chain gates (`<G>`). After that gate, make one report commit
that changes only `docs/infra/arch-20261105-2/`:

    cp gate-result.json docs/infra/arch-20261105-2/evidence/gate.json
    uv run python -m tools.evidence scope --base main --head <G> --out docs/infra/arch-20261105-2/evidence/scope.json
    uv run python -m tools.evidence ab /tmp/arch2-ab/base.jsonl /tmp/arch2-ab/head-rerun.jsonl \
        --base-commit e433588f51099f2a839b746a194c847491b8ecc5 --head-commit <G> \
        --out docs/infra/arch-20261105-2/evidence/ab.json --delta docs/infra/arch-20261105-2/evidence/ab-delta.json
    uv run python tools/batch_evidence.py --check docs/infra/arch-20261105-2 --report-commit HEAD

The recordings stay valid for `<G>`. The head was recorded at `4b63f08f4`. The one commit after it outside this
directory, `54625b35f`, adds `rerun_timeouts.py` and its two codemap lines (`docs/codemap/`) and changes no
recorded input. Every later commit changes only `docs/infra/arch-20261105-2/`. The saved `evidence/scope.json` and
`evidence/ab.json` name `54625b35f`.
