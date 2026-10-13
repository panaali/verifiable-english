# RD-7 work in progress

This batch is not review-ready. The worktree started clean at d006b1f4 on readings-defaults/rd7.
No model calls or push were made.

The superposed readings-verdicts service, dependency replay, conditions, candidate premise statuses, dead readings,
English selection and request-bound Python relay are implemented. Existing approved theorem statements were not
edited. Python's superposed fold, dependency replay, mentions and English selection were removed. Rust remains an
untrusted model evaluator. The runtime and soundness modules compile without sorry; computed Lean guards check the
fold boundaries and joint replay. The response-encoder proof remains unfinished: the isolated result-shape proof hits its heartbeat limit.
The full encoder/default-library build has not passed.

The six new tests in tests/test_readings_sup_verdicts.py passed in the recorded foreground run. They cover global
ALL, SOME, NONE, English relay, zero budgets, field retyping, one- and two-fault mutations, missing scopes with
reindexed model references, and a locally colliding canonical base refused as a premise model. Typed nullable
English slots are refused by the renderer when the frame cannot display them. The query's nullable dead list is
non-identity: switching null to an empty list changes no displayed line (R8).

## Seeded bugs

All four were killed and restored. The definition and execution evidence are in evidence/mutants.json,
evidence/python-mutants.json and evidence/lean-mutants.json.

| ID | File | Failing check |
|---|---|---|
| P1 | ve/readings_verdicts.py | test_missing_proof_scope_cannot_hide_behind_a_reindexed_model |
| P2 | ve/readings_s2_wording.py | test_sup_service_all_some_none_and_english |
| L1 | lean/VE/Readings/SupDependencies.lean | supDependencies_replay, checked by lake env lean |
| L2 | lean/VE/Readings/SupVerdictsWire.lean | the computed SOME encoder guard in SupVerdictsExamples.lean |

## Required work remaining

- AGENT (builder): finish the encoder Fits proof, then run the selected regressions, the statement comparison,
  audit and inventory regeneration, request/response mutation gate, saved corpus A/B, and latency measurements.
- AGENT (builder): record the actual user-visible deltas and their standing rulings, the deletion ledger and the
  measured R6 trust allowance. Any uncovered delta requires a HUMAN DRI signature; none is being presumed signed.
- AGENT (builder): save the code scope and commit list, review git diff main...HEAD, and run the full release gate
  once on the clean committed final code HEAD, retaining gate-result.json. No full gate has been run.
- HUMAN (environment owner): make /home/seyran/code/verifiable-english/.git/worktrees/ve-rd-7 writable. Git could
  not create index.lock because that metadata directory is mounted read-only. No local commit was possible;
  the implementation remains uncommitted. A read-only metadata mount cannot support the required clean final HEAD.

The signed reading's-own-sentence wording from readings-defaults-dri-note.md is retained. Corpus conservativity
and complete build-checklist acceptance are not claimed until the remaining evidence and final gate pass.

## Checklist status (uncommitted worktree)

This is an incomplete build record, not a request for review. Items marked pending need builder work; no
HUMAN or EXTERNAL approval is inferred. Saved execution logs and deletion-ledger.json describe this working
tree and must be regenerated or bound to the final committed code before review.

| Build-checklist item | Owner | Current evidence / remaining work |
|---|---|---|
| 1 Single contract | AGENT | Typed Lean shape and generated schema; encoder proof pending. |
| 2 Differential faults | AGENT | New one/two-fault response tests pass; selected differential suite pending. |
| 3 Shared normalization | AGENT | Parser normalization unchanged; selected regressions pending. |
| 4 Untrusted output | AGENT | Typed and request-bound relay, field mutations pass; complete relay gate pending. |
| 5 Malformed input | AGENT | Retyping tests pass; selected malformed-input regressions pending. |
| 6 Three-valued budgets | AGENT | Zero-budget test and computed fold boundaries pass. |
| 7 Whole-operation budgets | AGENT | Existing deadline infrastructure retained; selected guard tests pending. |
| 8 Exhaustive folds | AGENT | Lean ChoiceResult folds retained; existing constructor suite pending. |
| 9 English parsing | AGENT | Native plan formatting tests pass; complete M1–M20 regression run pending. |
| 10 Entry points | AGENT | Existing document and wording paths exercised; complete selected suite pending. |
| 11 Compiler oracles | AGENT | Lean compiled guards and Python AST ownership check; declaration dump pending. |
| 12 State/ledgers | AGENT | No product state-machine change; selected existing tests pending. |
| 13 Failing tests | AGENT | Four recorded mutants killed and restored, covering Lean and Python. |
| 14 Hermeticity | AGENT | New fixtures use tmp_path; prebuilt iteration recorded; final rebuild pending. |
| 15 Identity | AGENT | Scope/model/choice/label binding tested; nullable display slots fail closed. |
| 16 Inventories | AGENT | Route-map check passes; remaining inventory regeneration pending. |
| 17 Approved statements | AGENT | Approved-statement comparison passes; signed delta evidence pending. |
| 18 Theorem fixtures | AGENT | Computed ALL/SOME/NONE/gate guards pass; final encoder compilation pending. |
| 19 Use cases | AGENT | No new source translation; saved corpus comparison pending. |
| 20 Report numbers | AGENT | No final gate or corpus numbers claimed; saved final evidence pending. |
| 21 Ownership | AGENT | Acceptance ownership recorded here; environment blocker owned by HUMAN. |
| 22 Final gate/commits | AGENT + HUMAN | 36 GiB free measured; commits blocked by metadata mount; final gate not run. |
| 23 Signed deltas | AGENT | Own-sentence signed delta retained; measured DELTA and R6 allowance pending. |

## Latest foreground checks and blocker

The service, response decoder and computed Lean guards built successfully (rd7-proposals-build.log). The
over-64 countermodel regression and the new response tests passed (rd7-proposals-tests.log). All defaults
English tests passed (rd7-defaults-regressions.log). The latest binding checks also pass with the M3 witness
and M6 dead-reading regressions (rd7-final-binding-tests.log). These are working-tree checks, not a final gate.
The response schema and test collection were regenerated with their owners; the remaining declaration, audit,
assurance, frozen and trust inventories are pending.

The earlier unavailable over-64 countermodel line was fixed before handoff: Lean now supplies the bounded
compatible choices for the untrusted model generator. Python's MAX_LIFTS and choice search/filter were deleted.
The relay now binds model proposals, mentions, sort names and selected rule names, requires every aggregate
proof/countermodel row and every sent dead-certificate note, and checks only the schema's reference objects
so a model predicate cannot be mistaken for a result field. No new availability delta is claimed signed.

A fresh staging attempt failed with a read-only-filesystem error at
/home/seyran/code/verifiable-english/.git/worktrees/ve-rd-7/index.lock (rd7-git-stage.log). HEAD is still
d006b1f4. `git diff main...HEAD` is empty because no commit is possible; the working-tree diff was reviewed
for the intended RD-7 scope, and `git diff --check` passes. The saved deletion ledger marks itself explicitly
uncommitted. No full release gate, saved corpus A/B, latency check or review-ready check has run; none is claimed
passing. Rebind or rerun seeded evidence on the final committed code, including any mutants made redundant
by additional binding checks. This report must be finished after the HUMAN environment owner restores Git
metadata write access and the AGENT builder completes the remaining checks.

## Final working-tree verification record

The final focused run passed 35 tests (rd7-focused-final-worktree.log). The broader S2 document run passed 95
tests before reaching the old Python-dependency-selection expectation. That test was replaced by a direct R8
non-identity check: removing result metadata preserves every native-plan line. It and the remaining power-right
and owner-discovery tests pass in the focused records; the complete S2 run was not repeated. The display's
conclusion must equal the cached answer's original request conclusion, covered by the new query test.

All four seeded mutants were rerun against the latest product files, killed and restored. Current execution
evidence is python-mutants-final-worktree.json and lean-mutants-final-worktree.json. P1 is now the constant-reject
variant of the scope guard: its named test requires a genuine answer before probing the forgery, so it cannot
pass by refusing all answers. The restored computed Lean guards build passes (rd7-restored-guards.log). The
test collection was regenerated after the metadata-test rename. No command remains running.

The branch remains at d006b1f4 with all RD-7 work uncommitted because the Git metadata mount is read-only. The
encoder proof, final default build, audit/inventory/trust work, measured and signed DELTA, saved corpus/latency
evidence, selected-test command, final committed-HEAD gate and review-ready check remain AGENT work. Git metadata
write access remains the HUMAN environment owner's blocker. This is a blocked, incomplete build, not a review
handoff; no final gate result exists because no full gate was run.
