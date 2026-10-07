# RD-6a: S2a with a carried base-premise family (Lean)

Batch RD-6a of [readings-defaults-PLAN.md](../../spec/readings-defaults-PLAN.md), statements of
[readings-defaults.md](../../spec/readings-defaults.md) section 6.7, on branch `readings-defaults/rd6a` from `main`
at `167eb8ff`. Built by one Lean builder session on 2026-10-07; no model was called. Off the UDHR path: RD-6b needs
it to run the superposed route under the completion.

Every number, commit and seeded bug below is checked against the saved evidence
[gate-evidence.json](gate-evidence.json) by `tests/test_readings_defaults_rd6a_report.py`. That evidence was
written from the gate's logs and from `git log main..<gated commit> --no-merges`, and the test reads no git.

## What changed

| Commit | Subject |
|---|---|
| `53bb8fbd` | readings-defaults RD-6a: S2a with a carried base-premise family |
| `053e8f50` | readings-defaults RD-6a: check the statements against the approved 6.7 text |
| `bc413880` | readings-defaults RD-6a: READINGS.md lists the 6.7 theorems in plain words |

- `lean/VE/Readings/SupExtra.lean` (new): `Transfers`, `supCertificateCheckExtra` and `supModelCheckExtra` word for
  word as 6.7 states them; the proofs of `superpose_conflict_free_extra`, `superpose_all_extra`,
  `superpose_countermodel_extra` and `transfers_nil`; the helper `sat_pull_up`; and the checks at `Q = []`
  (`supCertificateCheckExtra_nil`, `supModelCheckExtra_nil`, `baseAdmissibleR_nil`). Three `example`s derive S2a's
  `superpose_conflict_free`, `superpose_all` and `superpose_countermodel` from the `_extra` forms at
  `transfers_nil`. They restate no declaration and leave the S2a proofs unchanged, so every S2a fixture answers
  byte-identically: nothing calls the new file (class: none).
- `lean/VE/Readings/SupExtraExamples.lean` (new): `#guard` fixtures on S2a's K1. X1 (rows X1.1 to X1.6) is the
  counterexample below. X2 shows the `_extra` checks at `Q = []` are S2a's on M2's bases, and that the model check
  reads `Q` on the base.
- Registered in `lean/VE.lean`, `lean/VE/Audit.lean`, `lean/VE/Route/frozen-sources.sha256` (the two new modules and
  the rehashed `Audit.lean`), `lean/axioms.txt`, `lean/statements.txt` (additions only), `lean/predicates.txt`,
  `lean/declarations.txt` and `tools/trust-classes.json`. Classes: S for `Transfers` (like `Encodes`); G[V] for the
  two checks (like `supCertificateCheck`); P for the theorems; T for the fixtures.
- `tools/check_readings_defaults_statements.py` compares `SupExtra.lean` with 6.7 the way it compares RD-1 with 6.2.
  A pending declaration carries its one exact edit, so any further change fails. RD-6b's three declarations are
  listed as not built, and each is compared once it is in the file. A Lean name is now read whole: before this, a
  primed name such as `transfers_nil'` was read as `transfers_nil`. Tests are in
  `tests/test_readings_defaults_statements.py` (11 new) and `tests/test_readings_defaults_rd6a.py` (2), all pinned in
  `tools/gate-collection.json`.
- `lean/READINGS.md`: a section listing the 6.7 theorems in plain words.

No frozen statement, wire function, Python module or answer changed. Python and Rust are untouched (the checker is
a tool, and it decides nothing about meaning).

## One statement changed: pending the statement re-review

`superpose_all_extra` is **false as approved**. Built instead: the approved statement with the added hypothesis
`(hQw : VE.Compose.SlotWellFormed (correlate (sup D).1) Q)`, meaning `Q` is over `sup D`'s base vocabulary.
`slot_route_acceptance` requires the same of every slot premise.

Why it is needed: the certificate reads `Q` on an intended structure of `sup D`, where a layer symbol (a regulated
or defined predicate) means its expansion. `Transfers` and `BaseAdmissibleP` read `Q` on a base, where an admissible
base gives a layer symbol no tuple. Fixture X1 (`SupExtraExamples.lean`, all `#guard`) uses S2a's K1 and
`Q = Q' c = [∀agent ∀user. ¬avoid_required]`:

- X1.1, X1.2: `φ = Q`'s sentence is over the shared vocabulary and over each choice's complete vocabulary, and the
  name map fixes `avoid_required`. Since `avoid_required` is a layer symbol, every admissible base satisfies `Q`, so
  `Transfers K1 Q (fun _ => Q)` holds.
- X1.3: `Q` fails `slotCheck` (the typing `hQw` asks for); the slot itself passes.
- X1.4: the one-step certificate `close` is accepted by `supCertificateCheckExtra K1 [] Q [] φ`, and not without `Q`.
- X1.5: the base `bare` (one agent, one user, no tuple) passes each reading's background with `Q' c`, satisfies `Q`
  as a base sentence, and K1's readings assert nothing.
- X1.6: on each reading's expansion of `bare`, `φ` is false (`circ`, which is the expansion by `circ_canon`).
- The hypothesis `hcf`: K1's slot is CONFLICT-FREE, certified by the Lean route
  (`tests/test_readings_defaults_rd6a.py::test_x1_k1_is_conflict_free_on_the_superposed_route`; its companion test
  fails on K1 plus K6's `never-avoid`). `Q` holds of every admissible base, so adding it excludes none.

So every hypothesis of the approved statement holds and its conclusion fails. `superpose_conflict_free_extra`,
`superpose_countermodel_extra`, `transfers_nil` and the three definitions are exact.
`tools/check_readings_defaults_statements.py` reports: RD-1: 31 exact, 0 pending; RD-6a: 7 checked, 6 exact, 1 pending (`superpose_all_extra`), 3 not built (`fill_transfers`, `nd_superpose_all`, `nd_superpose_conflict_free`).
**Owner: orchestrator; reviewers Astra + Fable (EXTERNAL, deferred):** accept the added hypothesis, or move the
typing of `Q` into `Transfers` as a third conjunct. The second option keeps the theorem's signature but adds a
needless hypothesis to the other two theorems. RD-6b's `nd_superpose_all` would then derive `hQw` from the typing
of `fillPremises (supU N)`.

## Gate

Gated commit: `bc413880ae7e88e436f88288eb6e8639708dbfc5`, run in a fresh worktree of it with a clean status. The
report commit adds only this file, the evidence, the report test and that test's IDs in `tools/gate-collection.json`
(83 added, none removed); those were run on the report commit, not in the chunks below.

| Check | Result |
|---|---|
| `lake build` (`PATH=~/.elan/bin:$PATH`) | `Build completed successfully (788 jobs)` |
| `python3 lean/audit.py` | PASS: 433 source files, 4,680 theorems, only `propext`, `Classical.choice`, `Quot.sound` |
| `python3 VE/Route/frozen.py` | PASS |
| `python3 tools/lean_statements.py --check` | PASS (4,319 statements; RD-6a adds 8, removes 0 and changes none) |
| `tools/check_lean_imports.py` | layer graph kept (433 modules) |
| `tools/check_python_layers.py`, `tools/test_layer_policy.py`, `tools/relay_lint.py` | PASS |
| `tools/gate_collection.py --check` | PASS (13 IDs added in `053e8f50`, 0 removed) |
| `tools/check_readings_defaults_statements.py` | PASS (above) |
| `tools/trust_map.py --check` | fails, as on `main` before this batch (the S budget; RD-1's DELTA explains it); RD-6a's own growth is `SupExtra.lean` S +7 (`Transfers`) |

Full pytest by file chunks, `-n 16`, `VE_LEAN_PREBUILT=1`, four slow tests deselected:

| Chunk | Files | Passed | Skipped | Failed |
|---|---|---|---|---|
| 1 | 60 | 2,022 | 1 | 0 |
| 2 | 54 | 3,929 | 2 | 0 |
| 3 | 59 | 1,799 | 3 | 0 |
| 4 | 56 | 2,453 | 0 | 0 |
| 5 | 55 | 1,578 | 0 | 0 |
| all | 284 | 11,781 | 6 | 0 |

Then the 4 slow tests alone (`-n 4`): 28 passed, 0 failed.

Not run: `tools/gate.py` as one process (the suite does not fit one 60-minute foreground call here; its stages
were run one by one as above), the cargo tests (no Rust changed), and the corpus A/B and latency budget (nothing
calls the new files, so no answer or timing can change).

## Seeded bugs (each planted in a scratch edit, shown failing, then removed)

| # | File | Bug | What failed |
|---|---|---|---|
| M1 | `lean/VE/Readings/SupExtra.lean` | Transfers carries Q one way only (→ for ↔) | lake build: 5 errors, in superpose_conflict_free_extra (both directions), superpose_all_extra, superpose_countermodel_extra and transfers_nil |
| M2 | `lean/VE/Readings/SupExtra.lean` | supCertificateCheckExtra drops Q from the slot | lake build: superpose_all_extra (the certificate no longer covers Q) |
| M3 | `lean/VE/Readings/SupExtra.lean` | supModelCheckExtra reads Q through the outcome substitution with the assertions, not on the base | lake build: superpose_countermodel_extra (Q no longer holds of the base) |
| M4 | `tools/check_readings_defaults_statements.py` | a pending declaration is not compared with its one approved edit | pytest: test_rd6a_checker_fails_on_every_changed_declaration[theorem-superpose_all_extra] |
| M5 | `tools/check_readings_defaults_statements.py` | an RD-6b declaration is skipped even when it is in the file | pytest: test_rd6a_checker_compares_an_rd6b_declaration_once_built |
| M6 | `tests/test_readings_defaults_rd6a_report.py` | the report check finds no mismatch, whatever the evidence | pytest: 81 of the report tests (every changed-leaf case and the empty report) |

Each of M1 to M3 changes an approved definition, so the statement checker fails on it as well. The report test
fails when any number, commit or seeded bug in the evidence is changed (one parametrized case per leaf), and on an
empty report or empty evidence.

## Build checklist (`manage-agents/prompts/build-checklist.txt`)

| # | Status |
|---|---|
| 1 one contract | not applicable: no diagnostic, limit or JSON decoding |
| 2 differential fuzz | not applicable: no wire or decoder (RD-6b) |
| 3 text normalization | not applicable: no text input |
| 4 untrusted output | not applicable: no response consumed |
| 5 malformed input | not applicable: no JSON input |
| 6 three-valued verdicts, budget 0 | not applicable: no verdict or public operation |
| 7 deadlines | not applicable |
| 8 exhaustive folds | not applicable: no kind or owner fold |
| 9 English | not applicable: no sentence |
| 10 one admit() | not applicable: no entry point (the route is RD-6b) |
| 11 no regex of a real language | partly: the statement checker compares Lean text with approved text by regex, as for RD-1; elaboration is the compiler's, axioms the audit's |
| 12 state machines | not applicable |
| 13 tests can fail | done: M1 to M5; the checker's mutant tests; the report test's mutated evidence |
| 14 hermetic | done: the new tests write only to `tmp_path`, read no environment or git, no sleep |
| 15 identity | not applicable |
| 16 lists generated or covered | done: `Audit.lean` (audit), frozen inventory, statement, predicate and declaration lists, trust classes, gate collection |
| 17 statement diff | done: the checker, with one change pending new approval (above) |
| 18 fixtures, both directions | done: X1 (each hypothesis and the failing conclusion), X1.3 both ways (`Q` fails the typing, the slot passes), X1.4 both ways (with and without `Q`), X2 on accepted and refused model checks |
| 19 use-case formalisation | not applicable |
| 20 reports | done: every number checked against the saved evidence by a test; what was not run is stated |
| 21 AGENT/HUMAN/EXTERNAL | done: the statement re-review is EXTERNAL (Astra + Fable), deferred, owner the orchestrator; everything else AGENT |
| 22 hand-off | done: all committed; the gate ran on the gated commit in a fresh worktree; disk checked (66 GB free before the gate) |
