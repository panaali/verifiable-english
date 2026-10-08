# RD-6a: S2a with a carried base-premise family (Lean)

Batch RD-6a of [readings-defaults-PLAN.md](../../spec/readings-defaults-PLAN.md), statements of
[readings-defaults.md](../../spec/readings-defaults.md) section 6.7, on branch `readings-defaults/rd6a` from `main`
at `167eb8ff`. Built by one Lean builder session on 2026-10-07 and fixed after review on 2026-10-07 and
2026-10-08; no model was called. Off the UDHR path: RD-6b needs it to run the superposed route under the completion.

**Status.** `superpose_all_extra` takes the added hypothesis `hQw`, accepted by the DRI ruling of 2026-10-07 20:30Z
on the condition that the approved form is refuted in Lean. That refutation is fixture X3 below
(`superpose_all_extra_refuted`, audited), and the statement checker reports the theorem as amended, not pending.
The gate below is the last full gate before the review fixes, on `03aeb667`. The report commit that follows the final code commit replaces it with that commit's gate. The gate result, the corpus A/B comparison and the latency measurement are the git note
`refs/notes/ve-rd6a-gate` on the gated commit and its committed copy [gate-note.json](gate-note.json), since a
merge or push does not carry a local note; `tools/batch_evidence.py` accepted them for that commit.

Every number, commit and seeded bug below is checked against [gate-note.json](gate-note.json) and
[gate-evidence.json](gate-evidence.json) by `tests/test_readings_defaults_rd6a_report.py`, which reads no git. The
commits are `git log main..<gated commit> --no-merges`.

## What changed

| Commit | Subject |
|---|---|
| `53bb8fbd` | readings-defaults RD-6a: S2a with a carried base-premise family |
| `053e8f50` | readings-defaults RD-6a: check the statements against the approved 6.7 text |
| `bc413880` | readings-defaults RD-6a: READINGS.md lists the 6.7 theorems in plain words |
| `d0021754` | readings-defaults RD-6a: batch report (gate evidence, the pending superpose_all_extra change, seeded bugs, checklist) |
| `ef3559e9` | readings-defaults RD-6a: bind batch evidence to final HEAD |
| `03aeb667` | readings-defaults RD-6a: normalize latency corpus requests |

- `lean/VE/Readings/SupExtra.lean` (new): `Transfers`, `supCertificateCheckExtra` and `supModelCheckExtra` word for
  word as 6.7 states them; the proofs of `superpose_conflict_free_extra`, `superpose_all_extra`,
  `superpose_countermodel_extra` and `transfers_nil`; the helper `sat_pull_up`; and the checks at `Q = []`
  (`supCertificateCheckExtra_nil`, `supModelCheckExtra_nil`, `baseAdmissibleR_nil`). Three `example`s derive S2a's
  `superpose_conflict_free`, `superpose_all` and `superpose_countermodel` from the `_extra` forms at
  `transfers_nil`. They restate no declaration and leave the S2a proofs unchanged, so every S2a fixture answers
  byte-identically: nothing calls the new file (class: none).
- `lean/VE/Readings/SupExtraExamples.lean` (new): fixtures on S2a's K1. X1 (rows X1.1 to X1.6, `#guard`s) is the
  counterexample below; X2 shows the `_extra` checks at `Q = []` are S2a's on M2's bases, and that the model check
  reads `Q` on the base; X3 is X1 in Lean, the refutation of the approved `superpose_all_extra`.
- Registered in `lean/VE.lean`, `lean/VE/Audit.lean`, `lean/VE/Route/frozen-sources.sha256`, `lean/axioms.txt`,
  `lean/statements.txt` (additions only), `lean/predicates.txt`, `lean/declarations.txt` and
  `tools/trust-classes.json`. Classes: S for `Transfers` (like `Encodes`); G[V] for the two checks (like
  `supCertificateCheck`); P for the theorems; T for the fixtures, X3's definitions included.
- `tools/check_readings_defaults_statements.py` compares `SupExtra.lean` with 6.7 the way it compares RD-1 with 6.2.
  An amended declaration (`AMENDED_6A`) passes only when the Lean text is the approved text with the ruled edit and
  nothing else, the refutations file states the approved statement as one proposition built from the spec text, a
  theorem there concludes its negation, and `Audit.lean` audits that theorem. RD-6b's three declarations are listed
  as not built, and each is compared once it is in the file. A Lean name is read whole, so a primed name such as
  `transfers_nil'` is not read as `transfers_nil`.
- `tools/batch_evidence.py` refuses a saved gate that is not on the given clean commit or lacks the complete suite,
  corpus A/B or latency evidence; with `--report-commit` it also refuses a later commit that changes anything outside
  the report directory, or that does not descend from the gated commit. `tools/readings_batch_latency.py` measures
  the readings route on the base and head builds with the public validator's requests.
- `lean/READINGS.md`: a section listing the 6.7 theorems in plain words.

Tests added (collected IDs in `tools/gate-collection.json` that `main` lacks):

| File | IDs |
|---|---|
| `tests/test_batch_evidence.py` | 11 |
| `tests/test_readings_defaults_rd6a.py` | 2 |
| `tests/test_readings_defaults_rd6a_report.py` | 83 |
| `tests/test_readings_defaults_statements.py` | 11 |

No frozen statement, wire function, Python module or answer changed. Python and Rust are untouched (the checker and
the evidence tools decide nothing about meaning).

## One statement amended by the DRI ruling of 2026-10-07

`superpose_all_extra` is **false as approved**. Built instead: the approved statement with the added hypothesis
`(hQw : VE.Compose.SlotWellFormed (correlate (sup D).1) Q)`, meaning `Q` is over `sup D`'s base vocabulary.
`slot_route_acceptance` requires the same of every slot premise. The DRI accepted it (option 1: keep the hypothesis
on this theorem, not in `Transfers`) on condition that the counterexample is mechanised. RD-6b's `nd_superpose_all`
derives `hQw` from the typing of `fillPremises (supU N)`.

Why it is needed: the certificate reads `Q` on an intended structure of `sup D`, where a layer symbol (a regulated
or defined predicate) means its expansion. `Transfers` and `BaseAdmissibleP` read `Q` on a base, where an admissible
base gives a layer symbol no tuple. Fixture X1 (`SupExtraExamples.lean`) uses S2a's K1 and
`Q = Q' c = [∀agent ∀user. ¬avoid_required]`:

- X1.1, X1.2: `φ = Q`'s sentence is over the shared vocabulary and over each choice's complete vocabulary, and the
  name map fixes `avoid_required`. Since `avoid_required` is a layer symbol, every admissible base satisfies `Q`, so
  `Transfers K1 Q (fun _ => Q)` holds.
- X1.3: `Q` fails `slotCheck` (the typing `hQw` asks for); the slot itself passes.
- X1.4: the one-step certificate `close` is accepted by `supCertificateCheckExtra K1 [] Q [] φ`, and not without `Q`.
- X1.5: the base `bare` (one agent, one user, no tuple) passes each reading's background with `Q' c`, satisfies `Q`
  as a base sentence, and K1's readings assert nothing.
- X1.6: on each reading's expansion of `bare`, `φ` is false (`circ`, which is the expansion by `circ_canon`).

**X3, the refutation in Lean.** `SuperposeAllExtraApproved` is 6.7's approved statement as one proposition, binder
for binder; the checker builds it from the spec text and compares, and an `example` applies it to the built
theorem's binders, so both are over the same constants. `superpose_all_extra_refuted : X1Checks →
¬ SuperposeAllExtraApproved` instantiates it at X1 (the reading `[("rs1", 0)]`) and derives `False`. Lean proves
each hypothesis that quantifies over structures: `Transfers` for every compatible choice and every admissible base
(`transfers_x1`); the conflict-freedom `hcf` of the slot over every base (`x1_conflict_free`, from the two conflict
certificates the route finds, by `slot_conflict_free`), which the Python route test only confirmed before; the
admissibility of `bare` (`bare_admissible`); and the failing conclusion (through `canon_subst`). The theorems use
only `propext`, `Classical.choice` and `Quot.sound`.

What Lean does not reduce: `X1Checks` is four checker runs on closed data, K1's `WellFormedDoc` and `superposable`,
X1.4's certificate check and the conflict certificates' check. They go through core's `List.mergeSort` and the
`String` functions behind generated names, which are well-founded recursion that the kernel does not unfold, and
the audit admits no decision by compiled code. Ground `simp` evaluation proved small parts but did not finish the
certificate check in 20 minutes. So `X1Checks` is the theorem's premise, and Lean's evaluator runs it at build
(`#guard X1Checks`), as it runs every other fixture of the file; seeded bug M10 shows the guard fails on a wrong
certificate.

On the gated commit, `tools/check_readings_defaults_statements.py` reports: RD-1: 31 exact, 0 pending; RD-6a: 7 checked, 6 exact (0 amended by a DRI ruling), 1 pending: `superpose_all_extra`, 3 not built (`fill_transfers`, `nd_superpose_all`, `nd_superpose_conflict_free`).

## Gate

Gated commit: `03aeb667172a10ec17f68ad10178f2fe09397e41`, run in this worktree with a clean status.

| Check | Result |
|---|---|
| `lake build` (`PATH=~/.elan/bin:$PATH`) | `Build completed successfully (788 jobs)` |
| `python3 lean/audit.py` | PASS: 433 source files, 4,680 theorems, only `propext`, `Classical.choice`, `Quot.sound` |
| `python3 VE/Route/frozen.py` | PASS |
| `python3 tools/lean_statements.py --check` | PASS (4,319 statements; RD-6a adds 8, removes 0 and changes none) |
| `tools/check_lean_imports.py` | layer graph kept (433 modules) |
| `tools/check_readings_defaults_statements.py` | PASS (above) |
| `tools/trust_map.py --check` | fails, as on `main` before this batch (the S budget; RD-1's DELTA explains it); RD-6a's own growth is `SupExtra.lean` S +7 (`Transfers`), and nothing unclassified |

The full gate (`--workers 16`): `tools/gate.py` passed on a clean worktree of the gated commit, stages `toolchains`, `lean_build`, `lean_audit`, `rust_build`, `cargo_test`, `pytest`. 11,911 Python tests passed, 7 skipped (each on the gate's allowed list), 1 deselected, 0 failed; 37 Rust tests passed.

Corpus A/B (`tools/lean_first_diff.py record` on both commits, then `compare`): 94,498 results identical, 0 different, 0 unlisted, base `167eb8ff`.

| Corpus/authority | Records |
|---|---|
| `conformance/lean` | 19,806 |
| `conformance/python` | 19,806 |
| `discourse/default` | 6,350 |
| `pilots/default` | 303 |
| `probe/lean` | 9,435 |
| `probe/python` | 9,435 |
| `quantity/lean` | 12,863 |
| `quantity/python` | 12,863 |
| `readings/default` | 1,137 |
| `rights/default` | 2,500 |

One base record was replaced by a retry, `pilot/cc-20261004T1800Z:usecases/claude-constitution-pilot/run-20261004T1800Z/readings/s1.ve.md`: The base run's recorder hit its 600 s per-document limit on this pilot (8 workers recording at once); recorded again alone on the same base checkout, it returned exit 0, and that result equals the head's. The original record and the retry are
bound by their SHA-256 in the note.

Latency (`tools/readings_batch_latency.py`: paired warm readings-route calls on the base and head builds, service
CPU time; the budget is 20% over the base):

| Case | Calls per side | Base CPU ms per call | Head CPU ms per call |
|---|---|---|---|
| `differential/c0` | 1000 | 2.937 | 2.934 |
| `differential/c568` | 1000 | 3.110 | 2.971 |
| `nulls/rights/vocabulary.predicates.arrest_permitted.instruction_of` | 1000 | 3.186 | 3.155 |

Not run: nothing else; `tools/gate.py` ran as one process.

## Seeded bugs (each planted in a scratch edit, shown failing, then removed)

| # | File | Bug | What failed |
|---|---|---|---|
| M1 | `lean/VE/Readings/SupExtra.lean` | Transfers carries Q one way only (→ for ↔) | lake build: 5 errors, in superpose_conflict_free_extra (both directions), superpose_all_extra, superpose_countermodel_extra and transfers_nil |
| M2 | `lean/VE/Readings/SupExtra.lean` | supCertificateCheckExtra drops Q from the slot | lake build: superpose_all_extra (the certificate no longer covers Q) |
| M3 | `lean/VE/Readings/SupExtra.lean` | supModelCheckExtra reads Q through the outcome substitution with the assertions, not on the base | lake build: superpose_countermodel_extra (Q no longer holds of the base) |
| M4 | `tools/check_readings_defaults_statements.py` | an amended declaration is not compared with the edit its ruling accepts | pytest: test_rd6a_checker_fails_on_every_changed_declaration[theorem-superpose_all_extra], test_rd6a_checker_fails_on_the_approved_all_statement |
| M5 | `tools/check_readings_defaults_statements.py` | an RD-6b declaration is skipped even when it is in the file | pytest: test_rd6a_checker_compares_an_rd6b_declaration_once_built |
| M6 | `tests/test_readings_defaults_rd6a_report.py` | the report check finds no mismatch, whatever the evidence | pytest: 4 of the 7 report tests (every changed evidence leaf, every changed note value, a changed corpus count or latency, the empty report) |
| M7 | `tools/check_readings_defaults_statements.py` | an amended declaration passes without its refutation being checked | pytest: 9 tests of test_readings_defaults_statements.py (every refuted-proposition mutant, the missing and wrong refutations, the unaudited refutation) |
| M8 | `lean/VE/Readings/SupExtraExamples.lean` | SuperposeAllExtraApproved drops the hypothesis hcf | lake build: the example tying it to superpose_all_extra and superpose_all_extra_refuted; the statement checker |
| M9 | `tools/batch_evidence.py` | a commit after the gate may change any path | pytest: test_a_report_commit_may_change_only_the_report_directory, test_report_commit_check_reads_git |
| M10 | `lean/VE/Readings/SupExtraExamples.lean` | the conflict certificate is a bare close | lake build: #guard X1Checks |
| M11 | `lean/VE/Readings/SupExtraExamples.lean` | Q is over the base predicate asks, not the layer symbol avoid_required | lake build: the X1 guards, noAvoid_of_empty and the failing conclusion of superpose_all_extra_refuted |
| M12 | `docs/readings-defaults/rd6a/gate-note.json` | the pilot retry's reason is empty | pytest: test_a_replaced_corpus_record_states_why |

Each of M1 to M3 changes an approved definition, so the statement checker fails on it as well. The report test
fails when any number, commit or seeded bug in the evidence or the note is changed, and on an empty report or
empty evidence.

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
| 11 no regex of a real language | partly: the statement checker compares Lean text with approved text by regex and reads binders by bracket depth, as for RD-1; elaboration is the compiler's (X3's `example` ties the refuted proposition to the built theorem), axioms the audit's; the report commit's paths come from `git diff --no-renames -z` |
| 12 state machines | not applicable |
| 13 tests can fail | done: M1 to M11; the checker's mutant tests; the report test's mutated evidence and note |
| 14 hermetic | done: the new tests write only to `tmp_path`, read no environment, no sleep; the report-commit test makes its own git repository |
| 15 identity | not applicable |
| 16 lists generated or covered | done: `Audit.lean` (audit), frozen inventory, statement, predicate and declaration lists, trust classes, gate collection |
| 17 statement diff | done: the checker; the one changed theorem is amended by the DRI ruling, its original refuted in Lean (X3) |
| 18 fixtures, both directions | done: X1 (each hypothesis and the failing conclusion), X1.3 both ways, X1.4 both ways, X2 on accepted and refused model checks; X3 in Lean, with M11 showing it fails for a `Q` over a base predicate |
| 19 use-case formalisation | not applicable |
| 20 reports | done: every number checked against the note's committed copy and the evidence by a test; what was not run is stated |
| 21 AGENT/HUMAN/EXTERNAL | done: everything AGENT; the external re-review was replaced by the DRI ruling. Pushing `refs/notes/ve-rd6a-gate` is the orchestrator's at merge (EXTERNAL to this worktree, which does not push); the committed copy carries the same content |
| 22 hand-off | done: all committed; the gate ran on the gated commit with a clean status; disk checked (66 GB free before the gate) |
