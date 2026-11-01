# qt-a3db REPORT: the `paraphrase` case (quantities QT-A3, last part)

Status: complete. All four deliverables are in: `Render.lean`, the `paraphrase` case and its shape, the route cases, and the seeded bugs.
Changed: Lean's English line for each canonical cardinality statement, plus one assumption per finite sort. The reply's text is charged against one 65,536-byte limit, and that limit is proved (`paraphrase_within`).
Open: the lines are display-only until QT-A6. Spec 7's paraphrase column, a W6a part's English and irregular plurals belong to QT-A6 ("Three choices", "Spec re-read").
Size: about 790 hand-written lines (771 added, 22 changed, the REPORT included) against ~600, accepted by the DRI (`reviews/dri-decisions-20261101-qt-a3db.md`). DELTA: none. DRI signature needed: none (trust growth is SIGNED by standing ruling R16). Next: qt-a4, then QT-A6.

## Plan rows (docs/spec/quantities-PLAN.md :174-181, :724; spec 4, 4.3)

| Row | Delivered by | Check |
|---|---|---|
| (1) `Render.lean`, a paraphrase of every canonical form the runner accepts | `lean/VE/Cardinality/Render.lean` (`formula` covers all ten `CFormula` constructors) | `RunExamples.lean` guards, one or more per form; route cases `paraphrase-quantity` … `paraphrase-implies` |
| The finite-sort declaration shown as an assumption | `Render.paraphrase` (one per `finite_sorts` entry, in order) | guard `RunExamples.lean:545` (word for word: "The document assumes there are finitely many FOMC policymakers.") |
| "the paraphrase says there is at least one user" on every proportion | `Render.formula` `.proportion` begins with `atLeastOne` | guards `:556`-`:565` ("There is at least one user, and of the users x, more than 1 in 2 …") |
| `.tiesUp` as "a value exactly halfway rounds up, to the larger number"; `.halfEven` as its own text | `Render.tie` | guards `:570`, `:573`, `:585`, `:588`; theorem `RenderTheorems.texts` |
| (2) the `paraphrase` case and its row in `cardinality.json`; `runCaseReported_fits` kept | `Run.runCase` (`kind == "paraphrase"`), `ResponseShape/Schemas/Cardinality.lean` `paraphrase` (generated `cardinality.json`), `Encoders/Cardinality.lean` (`certificate_kind` gains the kind) | `lake build ResponseShape.Encoders.Cardinality` (the encoder theorem builds unchanged in statement) |
| Each value read once, its size charged against a stated limit; a large well-formed request ends within it | The statement is decoded once (`decodeStatement`). The renderer charges every piece, vocabulary text included, before it is appended: `Render.emit`, one budget `maxBytes` = 65,536 for the line and all assumptions together (`piece`) | Proved: `RenderTheorems.paraphrase_within`. Guards `:635`/`:637` (65,536 bytes answered, 65,537 refused), `:639` (a 65,536-byte sort name refused) and `:643`/`:645` (one limit for the whole reply); tests `test_the_reply_text_is_charged_against_one_limit` and `test_a_large_statement_ends_within_the_limit` (4,099 nodes answered, 8,195 refused at the limit) |
| (3) route cases: one per form; hostile set with both sides | `tests/data/route-cases.jsonl` (15 rows); `tests/test_cardinality_service.py` `EXPECTED` | over-limit (`paraphrase-over-limit`, accepting side: the boundary test above); unknown form (`paraphrase-unknown-form`, accepting: every form row); non-canonical number (`paraphrase-non-canonical` "01", accepting: `paraphrase-count` "18"); not finite (`paraphrase-not-finite`, accepting: `paraphrase-half`); unknown kind (guard `RunExamples.lean:650`, "paraphrases") |
| R8: typed and bound, with fuzz | `test_paraphrase_rows_are_typed_and_bound`: every member dropped, retyped (`BAD`), duplicated or extra, and the assumptions cut, emptied or extended (`x-length` against `/environment/cardinality/finite_sorts`), all sent through the reply decoder `_decode_json` | 1 passed (`uv run pytest -q tests/test_cardinality_service.py`: 11 passed) |
| (4) seeded bugs and one mutant per new trusted definition | `docs/quantities/qt-a3db/mutants.json` (17 hand-planted), `trust-mutants.json` | below |

Synthesis round 2 (`debates/plan-synthesis-2/edits-quantities.md`): none of its seven edits concerns the paraphrase, so none is implemented here. The edited plan (`cf3f6fc49`) has the same paraphrase rows as main's (`diff` of the two plans, grepped for "paraphras": no line).

## Three choices (from qt-a3d's REPORT)

- **A sort's plural adds "s": kept.** The vocabulary has no plural field. Adding one would widen what W6a's environment decoder accepts, which needs the DRI. The pilot sorts ("FOMC policymaker", "user", "decision") all take "s". Irregular plurals belong to QT-A6's catalogue, and its parse-back check will refuse a wrong one. Recorded in FOLLOW-UPS.
- **W6a parts shown in canonical JSON: kept.** Lean has no English line for a W6a statement (`VE.Time` has no renderer), and writing one belongs to the time profile, not this item. The line marks the part as "the W6a statement … holds". QT-A6 must render it or refuse it before a line is shown as checked. Recorded in FOLLOW-UPS.
- **A line starting with a connective starts with "(the": changed.** `Render.initial` capitalises the first character after the opening parentheses: "(The W6a statement [\"top\"] holds) and (…)." (guard `RunExamples.lean:611`, route case `paraphrase-and`). Theorem `initial_size`: the capital changes no byte count.

## Spec re-read

- The declaration line against plan :174 and spec 7.1 (`docs/spec/quantities.md:1232`): equal, word for word.
- "at least one" against plan :177-178 and the review checklist :1309 ("Every proportion requires a nonempty population, and the paraphrase says so"): every proportion line starts "There is at least one <sort>", and every ratio says its denominator is positive.
- The tie-up text against plan :179, :181 and :1321 ("tie-up paraphrases say 'to the larger number'"): equal.
- **Deviation, recorded for QT-A6:** spec 7.1-7.2's paraphrase column (`quantities.md:1230-1300`) is the English that QT-A6's catalogue and parse-back produce. The spec calls those rows "QT-A6's fixtures" (`:1510`), and they read differently: "who expect …" against this item's "x such that x expects …", and half-even as "a value exactly halfway rounds to the one whose last digit is even" against this item's "… rounds to the even digit". The negative-half rendering fixture (E4, FA4e) is QT-A6's too. This item's lines are interim display text.
- `paraphrase` in spec 4.1 (`:768`, "Lean's English line for a canonical statement") and plan :724: delivered as a case kind with its row.
- "No symbol appears in any wording, paraphrase or diagnostic" (`:1302`): the W6a JSON part breaks this rule. It is display-only, disclosed above and recorded for QT-A6.

## Statement gate

The quantities statement review accepted QT-A3 (`docs/quantities/qt-a3/REPORT.md`, "Statement gate"). `uv run python tools/lean_statements.py --diff <statements.txt at the merge base 1d9ad881d> lean/statements.txt` reports added 26 (the `VE.Cardinality.Render.*` theorems), removed 0, changed 0. `python3 lean/audit.py` passes ("only the declared standard axiom allowlist"; `paraphrase_within` uses only `propext`, `Classical.choice` and `Quot.sound`, with no `sorry`).

## Trust (R16)

`uv run python tools/trust_map.py --check` against the merge base: K +0, S +6, unclassified 0, trusted +141.

| File | Class | Lines |
|---|---|---|
| `lean/VE/Cardinality/Render.lean` | D[V] (17 rendering functions), G[V] (`M`, `emit`, `piece`) | V +129 |
| `lean/VE/Cardinality/Run.lean` | G[V] `runCase`, the paraphrase case | V +6 |
| `lean/VE/Cardinality/RenderTheorems.lean` | S `Charges` | S +6 |

`maxBytes` and `tooLong` are G[R] (as `Wire.maxFiniteSorts`), the shape is G[R], and the guard helpers are T. These are recorded in `docs/trust-baseline.json` as "SIGNED by standing ruling R16 (DRI-RULINGS.md), qt-a3db, 2026-10-18". The ties-pass row is in manage-agents `FOLLOW-UPS.md` under "## qt-a3db". Every trusted definition is stated about by a theorem (`tests/test_cardinality_exercised.py`: 5 passed).

Trust mutants: `zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/quantities/qt-a3db/trust-mutants.json` (`trust-mutants-run1.json`: 18 survivors and 12 unknowns, at d79a060a). Two kinds of survivor got new guards: the paraphrase row's exact keys (`envIds` mutants) and a three-term count (`count`'s further terms). The rest are allowed in `trust-mutants-allow.json`: `Charges` is a proposition exercised by the proofs it breaks, and the other 8 do not compile. Rescored at 84930ae4, then at 2aa3ddb9 after the import fix (`--rescore trust-mutants-run1.json`): 49 KILLED, 0 SURVIVOR, 0 UNKNOWN, 22 ALLOWED, 4 INVALID, exit 0.

## Seeded bugs (Lean; no Python or Rust product code changed)

Each bug was planted alone in the file named, built with `lake build VE.Cardinality.RunExamples VE.Cardinality.RenderTheorems` (script `/tmp/qt-a3db-seed/plant.py`, results in `mutants.json`), then restored; `git status` was clean afterwards.

| Bug | File | Fails |
|---|---|---|
| "at least one" left out of a proportion | `lean/VE/Cardinality/Render.lean` (`formula`) | guards `RunExamples.lean:556`, `:558`, `:560`, `:563`, `:565`, `:643` |
| `ties_up` rendered as `half_even` | `Render.lean` (`tie`) | guards `:570`, `:576`, `:579`, `:585`, `:593`; theorem `RenderTheorems.lean:176` (`texts`) |
| finite-sort assumption dropped | `Render.lean` (`paraphrase`) | guards `:545`, `:548`, `:637`, `:639`, `:643` |
| a piece's bytes not carried on | `Render.lean` (`piece`) | guards `:637`, `:643`; proof `RenderTheorems.lean:97` |
| limit moved by one byte | `Render.lean` (`maxBytes`) | guard `:637` (65,537 answered); `texts` |
| assumptions not bound to the finite sorts | `lean/ResponseShape/Schemas/Cardinality.lean` (`.length` dropped, schema regenerated) | `tests/test_cardinality_service.py::test_paraphrase_rows_are_typed_and_bound` |

One more bug each in `describe`, `inParens`, `body`, `members`, `atLeastOne`, `term`, `operand`, `positive`, `relText`, `cmpText` and `initial`; each fails 3 to 26 guards (`mutants.json`). `emit`, `count`, `countTerm`, `formula`, `place`, `paraphrase` and `runCase` are covered by the tool's kills. `M` is a type abbreviation and has no well-typed mutant.

## Tests

- While iterating: `uv run pytest -q tests/test_cardinality_service.py` (11 passed), `tests/test_cardinality_exercised.py` (5 passed), and `tests/test_route_row_schemas.py` (32 passed, run with the exercised file before the trust classes were added).
- Selected run 1 (`mac-pytest.sh --select`, Claude cloud, b5b90ade, 412 units in 6 shards) had three failures, all from this item. Shard 1 stopped at `tools/check_lean_imports.py`: RenderTheorems imported `VE.Question.Strings` (layer 2 -> 3), and no default target built it. `test_precommit_hook.py::test_large_staged_change_passes` failed for the same import. `test_consolidation_tools.py::test_committed_ledger_names_real_declarations` failed because step 7 of `docs/CONSOLIDATION-PLAN.md` counts every `Run.runCase` and now measures 727 (`trust_map.py --ledger`). All three fixed in 2aa3ddb9b (import from `VE.Readings.Names`, a root in `lean/VE.lean`, the step-7 row re-measured).
- Selected run 2 (a8018ddf, 412 units): 5 of 6 shards passed (411 units). `test_assurance_manifest.py` failed three tests: Run.lean's pin and the two new files' classification. Fixed in 507a7c17d (Run.lean re-pinned, Render.lean pinned whole, RenderTheorems.lean under `other_json`). Rerun of that file alone: `uv run pytest -q tests/test_assurance_manifest.py`, 139 passed.
- Pre-existing red (main-known-red.txt): two `test_lean_service.py` sub-tick deadline tests and `test_readings_defaults_rd8_report.py::test_review_fix_commit_chain_and_final_gate_target` belong to lf-14d.
- Not run by me: the full gate (the chain runs it on the final HEAD).

## Pilot bytes

0 (estimate; nothing is claimed before a pilot audit): the case reaches documents only through QT-A4. This is the reader's line for Asimov P6, the constitution's 31 counting units and the 5,387 B research share, once QT-A4 relays it.

## Evidence

Commits (`git log --oneline --no-merges main..HEAD`): f0d020267, 7463e05be, 1f521a4ba, d79a060ac, 0fb6e8386, 84930ae45, da67568a4, 789a0ac03, b5b90adec, 2aa3ddb9b, a8018ddf4, 507a7c17d, and this report's update. Main was merged once (8abff0f63, at 1d9ad881d). Overlap: no in-flight branch (`feature/pc-3` included) touches these files; feature/qt-a4a has not started.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS. `test_paraphrase_rows_are_typed_and_bound` (each member set to 7, true, null, [], {}, 1.5, "\ud800" and a deep list, all through `_decode_json`); the request side is `paraphrase-unknown-form`, `paraphrase-non-canonical` and the unknown-kind guard.
2. Deliverables and rules: PASS. See "Plan rows". No Python copy of a Lean decision: under `ve/` the diff is only the hand-reviewed decoder pins (`ve/assurance-manifest.json`) and the generated `cardinality.json` (`git diff --stat <merge base> HEAD -- ve/ rust/`). No permanent report test.
3. Tests can fail: PASS. 17 seeded bugs (`mutants.json`); trust mutants exit 0 (`trust-mutants.json`).
4. Agreement, and valid input still passes: PASS. Every form row is answered (`test_route_cases_answer_as_recorded`); Rust has no paraphrase.
5. R8 binding: PASS. `assumptions` is bound by `x-length` to the request's finite sorts (seeded bug "assumptions-unbound"); the row's ids are W6a's environment identities, typed hex64.
6. Gate evidence: PASS. Synced with main at 1d9ad881d. Evidence: commits from `main..HEAD --no-merges`, trust and statement base from the merge base. The gate runs on the final HEAD in the chain.
7. Nothing unsigned: PASS. Trust growth cites R16 with its conditions met; there is no DELTA row.
8. DELTA: N.A. A new case kind; no existing answer changes (every pre-existing `EXPECTED` row is unchanged in `test_route_cases_answer_as_recorded`).
9. Test selection: PASS. `tools/select_tests.py --base $(git merge-base HEAD main)` picks 412 of 519 units, including the cardinality tests, the assurance manifest and the layer checks. Its failures in run 1 were the ones this item caused (see "Tests").
10. Statements say what is claimed: PASS. `paraphrase_within` is about `paraphrase`'s returned pair; the seeded bugs break `texts` and `piece_charges`; statement diff 26/0/0.
11. Budgets fail closed: PASS. Over the limit the answer is `ResourceLimit` (guards `:637`, `:643`; route case `paraphrase-over-limit`). The large request ends at the limit without a deadline (`test_a_large_statement_ends_within_the_limit`).
12. CPU and memory: PASS. Each byte is charged before it is appended, so work is bounded by 65,536 bytes plus the decoder's 10,000 nodes. The step check is `test_a_large_statement_ends_within_the_limit` (8,195 nodes refused, no timing).
13. Test-removed trailers: N.A. No test removed or renamed (`test_document_rows_are_typed_and_bound` and the others are kept).
14. Both directions, cited evidence, spec re-read: PASS. Each refusal has its accepting fixture ("Plan rows"); "Spec re-read" above.
