# RD-5: the UDHR migrated to readings with their own vocabulary, and measured

Batch RD-5 of [the plan](../../spec/readings-defaults-PLAN.md) (its RD-5 section, row and section 5), with the
statement spec [readings-defaults.md](../../spec/readings-defaults.md) 8.6, 9 and 10 and the DRI note
(`manage-agents/readings-defaults-dri-note.md`). No model was called. The pilot's scripts, data and report are in
[`usecases/udhr-pilot/run-20261010T1400Z/`](../../../usecases/udhr-pilot/run-20261010T1400Z/) and its
[`SUMMARY.md`](../../../usecases/udhr-pilot/run-20261010T1400Z/SUMMARY.md); this batch's evidence is in
[`evidence/`](evidence/). `check_delta.py` checks every number below against the saved evidence (DRI-RULINGS R11, D4:
batch evidence is checked at the gate and the merge, not by a permanent test).

## What was done

- **Migration** (`migrate.py`, `situations.py`): run 20261006T1800Z read at `bd6c7ab2` with `git show`. Each of the
  49 reading sets was offered to Lean by itself, its readings carrying their companions inline. Lean admitted 22,
  with every ordered pair separated by a situation the retained search proposed over Lean's filled document and
  Lean checked (30 situations, 0 unseparated pairs). Lean's split refused 27, each because two readings declare a
  name differently (E1). They stay on W2 as they were and are listed with Lean's text. `rs_u052` and `rs_u112` are
  among them, as the plan derived; `rs_u114`, with a companion copied from the main frame, migrated. No set
  declared an open term differently, so the migration did not stop (E4).
- **Checks** (`measure.py`, `witnesses.py`): the migrated document loads, checks and renders. Premises `model` and
  CONFLICT-FREE over 23 components. 152 of 152 status witnesses replayed in their components through
  `readings-choice` equal the recorded `witnesses.json`. All 156 companions re-checked alone give premises `model`,
  and 459 of 459 of their witnesses through the norm-defaults route equal the recorded ones.
- **Measurements**: the table of RD-5 step 4 is in `SUMMARY.md`, rendered from `metrics.json`. The Lean-decided
  share moves from 0 bytes (0.00%) to 2,111 of 10,916 bytes (19.34%) in 23 units. 1,886 of those bytes belong to
  units whose companions the run had already checked alone. The largest choice document holds 4 rules (1 written
  rule, 3 generated). Claimed covered (4,792, 43.90%) and audit-verified (2,543, 23.30%) bytes are unchanged.
- **Queries** (spec 8.6): `rs_u029` SOME; `rs_u081` SOME, then ALL under `--under rs_u081:2`; `rs_u081` NONE. Each
  answer is the derived one, and each is saved verbatim in `answers/`.
- **One product change** (`ve/readings_route.py`, 4 lines): S1's pair English raised `VEError` on a pair whose
  separating probe is a plain regulated predicate, because E19 words only duties and permissions. The whole report
  was then `CheckerUnavailable`. Such a pair now gets E24, the existing sentence for a checked separation VE cannot
  yet show in words. 15 of the migrated UDHR's 34 pair sentences are E24.

## Deviations from the plan's text, and why

1. **`norm-defaults@0` joins the main profiles beside `readings@1`.** The plan names only `readings@1`. RD-4b's Lean
   checks a document with companion readings as a product only under `norm-defaults@0` on the norms chain
   (`test_a_component_outside_the_completion_is_refused`). The main frame's one regulated predicate states its
   default (`allow`), so the profile adds no unspecified predicate.
2. **Meaning ids are checked by Lean, not taken from its answer.** `readings-validate` does not return meaning ids.
   It checks each recorded id (`companionMeaningId`) and refuses a mismatch. The companions' recorded ids are kept,
   and the three copied companions' ids are proposed with the W1 identity, as the pilot recorded them. Lean
   admitted every migrated one.
3. **Separations are checked by `readings-validate` on each set, not by `readings-separate` pair by pair.** The
   validation checks every recorded separation (S1 4.5) and answers per pair. The proposals come from the retained
   search (`ve.readings_s1.search`, RD-2b), seeded with the 3.3 pattern (`guard_base`) for each witness in turn. No
   new Python search was written.
4. **A set left on W2 keeps its models, re-identified.** W2's model and formula ids are over the environment's id,
   which the added profiles change. They are recomputed with the S1 pilot tool's `_reidentified`. The readings and
   contents are unchanged.
5. **`ve document load` does not exist.** Load is `load_document`, as the run's `verify_step.py` measured it. Each
   timed step runs in a child process of its own, and its CPU includes the Lean processes it waits for.
6. **The maximum rules per choice document is not in Lean's answer** (the share tool's `max_choice_rules` stays null).
   It is measured from Lean's `norm-defaults-elaborate` of every choice: its unspecified predicates, one generated
   rule each, plus one rule per chosen norm reading.
7. **No `pilot/udhr-readings-defaults` branch.** The run is committed on this batch's branch, under
   `usecases/udhr-pilot/`, so that the review sees it. A pilot branch would add the migrated document to the A/B
   `pilots` corpus of every later batch; that is the orchestrator's choice.
8. `witnesses.py` gained an `only` filter after the measuring commit `ae7fa229`, for the test. It changes nothing a
   full run computes.

## User-visible deltas

| # | Delta | Ruling | Evidence |
|---|---|---|---|
| U1 | A document whose S1 pair is separated on a plain regulated predicate gets a report, with E24 for that pair, where the base gave `CheckerUnavailable: ReadingsConstruction` | Not covered by a standing ruling (an availability change with an existing sentence): **DRI signature pending** | `tests/test_readings_rd5_plain_probe.py` (E24 on a plain probe; E19 kept on a duty probe); no record of the A/B corpora reaches it (below) |

The pilot's own outputs (the migrated document, its reports and answers) are new files, not changes to existing
outputs. The 27 sets left on W2 keep W2's UNKNOWN in the main component.

## A/B (base `cc534bfc`, the merge base; head this branch)

Both sides use the same Lean and Rust builds: no Lean or Rust file differs. The head side was recorded from this
checkout after `c3e40b7a`, the last commit that changes product code (`ve/readings_route.py`); later commits change
tests, the gate-collection pins, the pilot and docs only. The base is a worktree of `cc534bfc` with
this checkout's builds linked in.

- **probe and conformance**: 58,482 records (probe 9,435 per authority, conformance 19,806 per authority), all
  **same**, 0 unlisted (`ab-probe-conformance.json.gz`).
- **pilots and readings**: 1,606 records (469 pilot documents, 1,137 readings cases). 1,589 same. The 17 differences
  are 8 availability, 2 unavailable on both sides and 7 wording (`ab.json.gz`). Each comes from a wall-clock limit
  under host load (the Rust checker's 5 s, the recorder's 600 s), or from the absolute scratch path a sense-pack
  probe prints (as in RD-4b). Host load averages of 50 to 100 were seen while the sides were recorded. Rerun serially (`ab_rerun.py`), 13 are equal
  (`ab-rerun.json.gz`), and the last 4 are equal with the Rust checker's limit raised to 600 s
  (`ab-rerun-rust600.json.gz`, `VE_RUST_TIMEOUT=600`). All 17 are equal; `ab-summary.json` pairs each difference
  with its rerun.

No record differs in a verdict, a wording or an order once the load is removed.

## Seeded bugs (AGENT)

`mutants.py` planted each bug, ran its test (which failed), and restored the file (the SHA-256 is equal before and
after). The record is in [`evidence/mutants.json`](evidence/mutants.json).

| Bug | File | Failing test |
|---|---|---|
| `no-e24-for-plain-probe` | `ve/readings_route.py` | `tests/test_readings_rd5_plain_probe.py::test_a_pair_probed_on_a_plain_predicate_gets_e24` |
| `e24-for-every-probe` | `ve/readings_route.py` | `tests/test_readings_rd5_plain_probe.py::test_a_pair_probed_on_a_duty_keeps_e19` |
| `main-frame-without-norm-defaults` | `usecases/udhr-pilot/run-20261010T1400Z/migrate.py` | `tests/test_readings_rd5_udhr.py::test_the_migration_reproduces_the_committed_document` |
| `unknown-status-taken-as-an-answer` | `usecases/udhr-pilot/run-20261010T1400Z/witnesses.py` | `tests/test_readings_rd5_udhr.py::test_one_sets_witnesses_replay_equal_in_its_component_and_alone` |
| `summary-share-before-for-after` | `usecases/udhr-pilot/run-20261010T1400Z/summary.py` | `tests/test_readings_rd5_udhr.py::test_the_summary_is_rendered_from_the_saved_metrics` |

Python is the only language whose product code changed (no Lean or Rust file changed). Two earlier candidate bugs
were equivalent on the UDHR's data and were replaced:
- Dropping the copied environment's argument sorts changes nothing: every argument of a well-typed closed formula
  is a quantified variable or a constant.
- Taking an UNKNOWN status as the answer changes nothing on `rs_u029`: every one of its witnesses is SETTLED via
  `table3`. The witness test now replays `rs_u025`, which has SETTLED yes, SETTLED no and UNDECIDED witnesses.

## Scope

Saved `main..HEAD --no-merges` at the code head `6a80b9a3` ([`scope.json`](evidence/scope.json)): **10 commits**,
36 files, **23,709 lines added**, **1 deleted**. Of these, 4 lines are product code (`ve/readings_route.py`), 249
are tests, 4 are difffuzz corpus exclusions and 11 are gate-collection pins. The rest is the pilot's scripts, data,
evidence and this DELTA. Commits: `c3e40b7a`, `ae7fa229`, `a497cf56`, `98d8dbf0`, `8fed59c9`, `b6cf9fbb`,
`b90219bb`, `b52c22a4`, `5e5ac815`, `6a80b9a3`.

- `b52c22a4` is `main`'s `6b66f087`, cherry-picked (the one deleted line): the layer map's row 4 lists `ve.ask`,
  which `tools/test_layer_policy.py` needs and the merge base lacks.
- `6a80b9a3` registers the run in two corpora that read every file under `usecases/` (the cost of deviation 7):
  `tools/difffuzz_corpus.py` excludes the run's answers, reports, metrics and `unmigrated.json` as artifacts (none
  holds an environment, a request or a model; `test_every_fixture_is_read_or_excluded_with_a_reason` checks that
  for `no-input` and that every pattern matches), and `tests/test_lean_document_wrapper.py` lists the migrated
  document among the fail-closed seeds. Lean's document mode refuses it with "JSON reader: null in reading_sets"
  (the 27 sets left on W2 keep `content: null`), as it refuses `constitution-nd-readings`; Python answers ok.
- `5e5ac815` makes `mutants.py` build its pytest command with `tools/nested_pytest.py`
  (`test_every_pytest_command_is_built_by_the_builder`); the seeded bugs were rerun with it.

## Statements, manifests and limits

- RD-5 lists no Lean statement, and no Lean file changed: no proof, `sorry`, audit, statement, frozen-source,
  assurance or response-schema change, and no rehash.
- `tools/gate-collection.json` pins the 11 new test IDs (`tools/gate_collection.py --write`).
- `tools/trust_map.py --check` passes: K, S, D, G, tied and trusted lines are all +0 against the baseline (the trust
  check is not weakened; sibling finding B1).
- No limit is copied into product code. The pilot's test reads `MAX_DOCUMENT_BYTES` and `MAX_CHOICES` from their
  owners, and the per-frame limits are the frozen decoders', under which Lean admitted the document.
- The gate's Lean binaries come from a build from source in this worktree: its `lean/.lake` was empty on
  2026-10-11, and `lake build` built all 881 jobs (57 min) before the selected tests and the gate (sibling finding
  B2). The new `ve_service`'s SHA-256 (`e4e92788…`) is the one pinned in `lean/checkers.lock`.

## Sibling findings (rd-6b review), checked

- B1 (a disabled trust check): no report test touched; `trust_map.py --check` passes on HEAD.
- B2 (a stale binary): binaries relinked as above; no fuzz baseline entry added.
- B3 (answers changed and tests loosened): no expected output changed; the A/B shows no answer change.
- B4 (an untyped relayed field): no response schema or relayed field changed.
- B5 (a narrow differential): no differential is claimed; the migration is reproduced byte for byte by a test.
- C (Python recomputing Lean's values): nothing in `ve/` counts, searches or limits anything new. The pilot scripts
  count only to report Lean's answers (the share sums Lean's `decided_units`).

## Acceptance items

- AGENT: everything above, with the tests named (`tests/test_readings_rd5_udhr.py`, 9 tests;
  `tests/test_readings_rd5_plain_probe.py`, 2 tests).
- HUMAN, DRI: the signature for U1. Owner: the DRI.
- EXTERNAL, deferred: the next UDHR audit decides on the migrated units; the audit-verified share is unchanged until
  then. Owner: the UDHR pilot.
- HUMAN, deferred, pilot task: re-translating the 27 sets that need one vocabulary (most are `state` against
  `bearer`). Owner: the UDHR pilot.

## Full gate

Run once on the committed final HEAD; the result is in [`evidence/gate.json`](evidence/gate.json) (see below).
