# ci-3 report: steps, `Then` steps and conditions written first on the `english.command` route

No DELTA row reserves a DRI signature: rows 1-7 cite a signed decision or R3/R16.

Spec: docs/spec/commands-imperatives.md section 7 (the statement gate passed in reviews/dri-decisions-20261102-ci-0.md
item 1). Plan: commands-imperatives-PLAN.md "CI-3. Steps and conditions written first". Branch `feature/ci-3`, merged
with main at d3bb8bfbc (ci-2b and ci-3b in).

## Plan rows delivered

1. **`readInstruction` returns `StepOutcome`** (`lean/VE/Commands/Run.lean`): a proof task's outcome is
   `lift (.core s) false`, else `readStep`. `readInstruction_step` replaces `readInstruction_command`;
   `readInstruction_refused_classed_step` and `readInstruction_typed_step` are proved (no `sorry`, standard axioms).
   Every caller of the old `Outcome` is updated: the mode's encoder (`Run.encode`, `caseReported`),
   `readInstruction_refused_classed_of` and `readInstruction_typed_of_facts` (Run.lean), and after the main merge
   ci-2b's `RunSplit.readInstruction_typed` and the source wrapper's A2 re-read (`Source/Run.lean`,
   `.one r _`). Read.lean and Examples.lean are not touched.
2. **The stated order** (Run.lean): `stepCommands`, `stepCommands_policy`, `StepUnit`, `stepNames`, `lastStep`,
   `firstStep`, `antecedentOf`, `stepOrder`, `thenWithoutStep`, `stepOrder_forward`, with section 7's fixtures as
   `#guard`s in RunExamples.lean: the seven units -> [(u2.1, u2.2), (u2.2, u3), (u3, u5)] and `thenWithoutStep`
   [u6, u7]; uweb.tour.552_0 -> no pair and `ThenWithoutStep` for b; "Then click Ask." with no earlier instruction;
   the counterexample [a, b (2 steps, after a)] -> [(a, b.1), (b.1, b.2)]. `ThenWithoutStep` is in Texts.lean, class
   `VEError`.
   Finding (d), the reader's part: the first refusal wins with the step's code and text ("Click Ask, then add an
   exception or precedence." is `InvalidInput`, a guard). **Left to the translation writer:** the MIXED unit with a
   demand part per read step and a GAP part per refused step (its code from reading the step alone), and the stated
   order kept between read steps only. These are document facts, not reader outcomes (`StepOutcome` gains no
   constructor). OPEN O4 (the GAP part's owner when the step's object kind is not in section 12's table) and OPEN O8
   (the refusal's text naming the step) stay open; this item does not decide either.
3. **`surfaceKind`'s `if `/`then ` cases** (Wire.lean): `If <c>, <act verb> …` (the clause after the first comma) and
   `Then <act verb> …` are `instruction`. SA's (ββ) "If Alice must click Check then Atlas is reviewed." stays
   `asserted`. A/B on the pinned corpus: AB.md (12 files, 0 literals starting `if `/`then `, 0 flips).
   `paraphraseSteps` is in speech-acts (`lean/VE/SpeechActs/Run.lean`, S10: no second paraphrase table); section 7's two
   English lines are guards. The derived order in `lean/VE/SpeechActs/Source/Run.lean`: `stepUnits` and
   `thenFault`, the `ThenWithoutStep` document check after the core check, by each unit's effective kind
   (attributed, hedged and signed-choice instructions included). No unit field names an antecedent (O3, ruled in
   reviews/dri-decisions-20261102-ci-0.md item 5), so every authored `Then` instruction unit is refused.
4. **The `english.command` response shape**: `one` gains `after_previous`; `many` gains `alternatives`; new
   outcomes `steps` (readings and `paraphraseSteps`) and `mixed` (CI-7b's, written by no reader yet). Schema
   `lean/ResponseShape/Schemas/Command.lean` and encoder theorem `ResponseShape.Encoders.Command.encode_fits`
   (ROUTE-RECIPE steps 2-3).
   **Not delivered: the Python binding of `steps` and of a `many` of sequences.** It is cut to ci-3c
   (reviews/dri-decisions-20261109-ci-3-size.md item 2). After the main merge, ci-2b's relay
   (`ve/backends/english_lean.py`) reads `english.command`. It now refuses `steps`, `mixed` and a `many` whose
   alternatives are not one reading each at its own position as CheckerUnavailable (R8: unbound means unavailable),
   instead of raising `KeyError`. This is DELTA row 7, signed in reviews/dri-decisions-20261110-ci-3-relay.md item 1.
   ci-3c removes that refusal. The binding inventory classifies the new members; its bound-field fuzz rebinds a
   genuine `many`'s `alternatives`.

## Statements (section 7, whitespace normalised)

Every ci-3 definition and theorem equals section 7's text, with these exceptions:

- `readInstruction_typed_step` has `(hw : VE.Scope.JsonWF j)` beside `hd`: SIGNED by the DRI 2026-11-09,
  reviews/dri-decisions-20261109-ci-3.md item 1 (the guard that every ci-3 fixture environment passes `jsonWF?` is in
  RunExamples.lean).
- `readInstruction_typed_of_facts`' `h` is in the step form: SIGNED by the DRI 2026-11-09,
  reviews/dri-decisions-20261109-ci-3-step.md item 1.
- `readInstruction_refused_classed_of`: `Outcome.refused` became `StepOutcome.refused`, the type only. SIGNED by the
  DRI 2026-11-09, reviews/dri-decisions-20261109-ci-3-codes.md item 3.
- After the merge, `RunSplit.readInstruction_typed` (ci-2b, section 6) has `h` in section 7's step form and is proved
  by `readInstruction_typed_step`: SIGNED by the DRI 2026-11-10, reviews/dri-decisions-20261110-ci-3-typed.md item 1.
  `tests/test_ci2b_statements.py` checks section 6's text with only the `hw` and `h` substitutions.
  `RunSplit.readInstruction_refused_classed` keeps its text.

The `hb` hypotheses of `readStep`'s lemmas are ci-3a's and ci-3b's (their own rulings).

## Seeded bugs (each failed its test, then was restored; mutants.json has the file and the failing guard)

| Language | File | Bug | Failing test |
|---|---|---|---|
| Lean | lean/VE/Commands/Run.lean | `stepOrder` reversed | `stepOrder_forward` (Run.lean:718); with proofs sorried, RunExamples.lean:277 and 282 |
| Lean | lean/VE/Commands/Run.lean | `stepOrder` pairs a `Then` unit with the nearest earlier instruction unit | Run.lean:724; sorried: RunExamples.lean:277, 279 (uweb.tour.552_0) |
| Lean | lean/VE/Commands/Run.lean | `readInstruction` skips `proofTask` | Run.lean:449, 452, 625, 630; sorried: ci-1's proof-task guards (RunExamples.lean:104, 117, …) |
| Lean | lean/VE/SpeechActs/Wire.lean | `surfaceKind` reads "If … then …" without a comma as an instruction | RunExamples.lean:297 (the `webKind` guard, (ββ) stays `asserted`), 301 |
| Python | ve/backends/english_lean.py | the `steps` outcome relayed unbound | `tests/test_commands_steps.py::test_the_relay_refuses_a_sequence_it_does_not_bind_yet` |
| Python | ve/backends/english_lean.py | a `many`'s alternatives not bound to its readings | `tests/test_commands_steps.py::test_a_many_answer_s_alternatives_are_bound_to_its_readings` |

The task's fifth seeded bug ("the relay accepting a step reading not in the answer") belongs to the binding of
`steps`, which is ci-3c's. Here a `steps` answer is refused whole, which the first Python seed shows.

mutants.json lists 37 entries: 28 hand mutants, at least one in every new trusted definition, plus the 9 seeds above
(the Lean seeds both with and without sorried proofs). Each records the guard, proof or test that fails. Its line
numbers are on the merged tree.

## Trust

`tools/trust_map.py --check` against d3bb8bfbc650: K +0, S +0, trusted +89. That is VE/Commands/Run.lean +84,
VE/SpeechActs/Wire.lean +4 and VE/SpeechActs/Source/Run.lean +1. The allowance is in docs/trust-baseline.json, SIGNED
by standing ruling R16, and FOLLOW-UPS.md "## ci-3" asks for the ties pass. Fixture definitions are classified `T`
(tools/trust-classes.json).

Trust-mutants sweep on the final Lean tree (HEAD db70c3c70, tree 538087148): `zsh mac-pytest.sh --trustmut --
--max-mutants 1000 --json docs/commands-imperatives/ci-3/trust-mutants.json --test lean/VE/Commands/RunExamples.lean
--test lean/VE/Commands/RunSplit.lean --allow docs/commands-imperatives/ci-3/trust-mutants-allow.json --rescore <the
first sweep's record>`. It ran on the VM and exited 0 in 11976 s. Over 14 definitions and 293 mutants: **218 KILLED,
0 SURVIVOR, 0 UNKNOWN, 60 INVALID, 15 ALLOWED, 0 NOT RUN**. By class, D[V] has 155 KILLED, 44 INVALID and 14 ALLOWED;
G[V] has 63 KILLED, 16 INVALID and 1 ALLOWED. The record is committed as trust-mutants.json, with its `head` and
`tree` equal to the commit it ran on. The `--rescore` did not reuse any verdicts. The main merge moved the plan from
292 to 293 mutants and added the RunSplit `--test`, so the tool did a full run ("its inputs differ (options)").

The first sweep ran at 0ff26e6f1, before the merge. It found 187 KILLED, 34 SURVIVOR and 11 UNKNOWN. Commit 496560675
handled those results:

- it added a fixture for each survivor that could be killed (RunExamples.lean and RunSplit.lean);
- it allowed the rest in trust-mutants-allow.json, each with its reason: equivalent mutants (`take 1` before `head?`),
  and mutants that do not elaborate (UNKNOWN only).

## Size

`git diff --numstat d3bb8bfbc` (the merge base), with generated files left out, measured with the DRI's exclusion list:

- at 496560675: +1610/-126. The DRI measured +1609/-126 there; the extra line is generated `ResponseShapeAudit.lean`.
- at HEAD: +1726/-126 before this report's last edits. The rise is REPORT.md (+116 once committed) and
  trust-mutants.json (generated by the tool).

This size is ACCEPTED in reviews/dri-decisions-20261110-ci-3-size2.md item 1 (product lines about 244: Lean Run.lean
145, Texts 8, SpeechActs/Run 7, Source/Run 18, Wire 5, Encoders/Command 27, Schemas/Command 24; Python english_lean.py
10). Its exempt groups, each with the ruling the DRI cites:

- R16 survivor fixtures (RunExamples 40, RunSplit 22) and trust-mutants-allow.json: R16 and the sweep;
- the relay guard, its tests and the inventory rows: ci-3-relay item 1;
- test_ci2b_statements: ci-3-typed item 1;
- the seeded bugs, the stated-order `#guard`s and mutants.json: ci-3-size item 1;
- ab.py: the A/B that 10-28 commands-imperatives item 2(b) requires;
- Run.lean's 377 proof lines (`readInstruction_step`, `_refused_classed_step`, `_typed_step`,
  `stepCommands_policy`, `stepOrder_forward` and their lemmas): statement-gate proofs, ci-3-size item 1 and
  adv1207 item 3;
- REPORT and DELTA: documentation.

No product line was added after that ruling.

## Tests

- `python3 lean/audit.py`: PASS. 819 source files and 9242 theorems, only the standard axioms (run once on this
  tree after `lake build` built 1353 jobs with no error and no `sorry`).
- `uv run python tools/regen_generated.py --check`: 38 entries checked, none stale.
- `tools/gate_collection.py --check --prebuilt`: 33425 collected, 14 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- Selected tests, run once on the committed tree 2f3694d6e (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base
  d3bb8bfbc --run`): TESTS_LINE

## Pilot bytes (an estimate; nothing is claimed before a pilot audit)

The plan's estimate is +2 segments / 46 B for CI-3. "Then click Ask." and "Then click Check rule conflict." (tour.js)
now read as `one` with `after_previous`, and "Click Check rule conflict, then click Ask." reads as `steps`. In a
document, an authored `Then` unit is still `ThenWithoutStep` until O3 names an antecedent field. Through the Python
fence route, a sequence is CheckerUnavailable until ci-3c.

## Next

ci-4 (after this item and ci-3b); then ci-3c.

FOLLOW-UP: ci-3c english.command steps/many relay binding, inventory rows, fuzz test

## Spec re-read (whitespace normalised, against docs/spec/commands-imperatives.md on this branch)

- `readInstruction_step`, `readInstruction_refused_classed_step`, `readInstruction_typed_step` (with `hw`, signed):
  :935-952.
- `stepCommands` :996, `stepCommands_policy` :1000, `StepUnit` :1005, `stepNames` :1014, `lastStep`/`firstStep`
  :1017-1018, `antecedentOf` :1021, `stepOrder` :1026, `thenWithoutStep` :1042, `stepOrder_forward` :1048.
- The two English lines: :1061-1065. `paraphraseSteps`: :1132-1145.
- `ThenWithoutStep` in `codeClasses`: :1437.
- `surfaceKind`'s `if `/`then ` cases: commands-imperatives-PLAN.md:588.
- The A/B classes: reviews/dri-decisions-20261028-commands-imperatives.md item 2(b).

## Not synced with main

main is 208 commits past the merge base d3bb8bfbc (`git rev-list --count HEAD..main`). `git merge-tree --write-tree
HEAD main` shows conflicts only in generated files: the codemap, binding-census, assurance-manifest.md and
declarations.txt. It also conflicts in `ve/assurance-manifest.json`, where the pins have to be re-applied on main's,
as ffc69bead did. No hand-written ci-3 file conflicts. `tests/test_relay_binding_inventory.py` merges cleanly.

A sync now would need another full build, sweep and selected run. So this branch is gated as it is, and the sync is
left to the merge train (R12 for the generated files).

## Self-review against BUILDER-CHECKLIST

1. PASS. A sequence, a mixed outcome and a `many` of sequences are refused whole as CheckerUnavailable, and a `many`'s
   alternatives are bound one per reading:
   - `tests/test_commands_steps.py::test_the_relay_refuses_a_sequence_it_does_not_bind_yet`,
     `::test_a_many_answer_s_alternatives_are_bound_to_its_readings`;
   - the inventory rows in `tests/test_relay_binding_inventory.py`.
   The binding of `steps` is ci-3c's (ci-3-size item 2).
2. PASS. Plan rows (1)-(4) are listed above with their commits. The cut of (4)'s Python binding has a ruling
   (ci-3-size item 2). No Python copy of a Lean decision is added: the relay only refuses or binds.
3. PASS:
   - seeded bugs: the table above and mutants.json (37 entries);
   - trust-mutants sweep: 0 SURVIVOR and 0 UNKNOWN, in trust-mutants.json;
   - the allow file names exact definitions and operators.
4. PASS. AB.md/AB.json give base against HEAD on the pinned corpus (0 flips) and the fixtures. Their tests:
   - `tests/test_commands_steps.py::test_saved_ab_has_no_stop_row_and_no_surface_kind_flip`;
   - `::test_each_b1_row_is_a_route_fixture_that_reads`.
   Rust is not changed.
5. PASS. The unbound new members are refused, not read
   (`::test_the_relay_refuses_a_sequence_it_does_not_bind_yet`, parametrised over steps, mixed and a `many` of
   sequences). A `many`'s alternatives are rebound by the inventory's bound-field fuzz.
6. PASS for evidence on this tree: the sweep record's `head` and `tree` are db70c3c70, and the selected run is on
   2f3694d6e. The gate is the chain's. Not synced with main (see above).
7. PASS. The DELTA rows cite R3, R16 or a signed decision file (rows 1-7). Trust growth is +89 under R16, with the
   allowance and the FOLLOW-UPS.md "## ci-3" row.
8. PASS. DELTA rows 1-7 cover:
   - the readings that change (b1);
   - the refusing direction (b2);
   - the codes (ci-3-codes);
   - `Then` in documents (ThenWithoutStep);
   - the relay refusal (row 7).
   AB.md recounts them.
9. PASS. `tools/select_tests.py --base d3bb8bfbc` selects 493 units, not every unit, including test_commands_steps,
   test_relay_binding_inventory and test_ci2b_statements.
10. PASS. Lean proof seeds break `stepOrder_forward`, `readInstruction_step` and `_typed_step` (mutants.json,
    Run.lean:718, :724, :449, :625). `tests/test_ci2b_statements.py` checks the statement text, and the added
    hypotheses are signed (ci-3, ci-3-step, ci-3-codes, ci-3-typed).
11. PASS. The budget is charged before work. Two RunExamples.lean guards show it:
    - "charges through the mode": 359 steps' bytes and 6 KB of `preposed` splits end as `limit` before any shape is
      built;
    - `readingsBound` alternatives are written in full.
    No test sleeps, times or uses a wall deadline (`tests/test_hang_guards.py` is selected).
12. N.A. for pilot timing (L70 forbids whole-UDHR runs). The eager pattern is guarded by the `limit` and
    `readingsBound` guards in item 11.
13. PASS. `tools/gate_collection.py --check --prebuilt`: 14 added, 0 removed, 0 refused, 0 stale, 0 malformed. No
    test is removed.
14. PASS. Each new check is tested in both directions:
    - `surfaceKind`: instruction for "If c, click …" and asserted for (ββ) (RunExamples webKind guards);
    - ThenWithoutStep: refused for an instruction `Then` unit (and an asserted one with a signed instruction choice);
      "ok" for an asserted `Then` unit with no such choice (RunSplit.lean guards);
    - the relay: refuses steps and accepts `one` with `after_previous` (`::test_a_then_step_is_relayed_with_its_flag`).
    Spec re-read: the section above.
15. PASS:
    - no overclaim: every count above names its command (sweep log, audit, gate_collection, numstat);
    - no silent cut: (4)'s Python part has a ruling;
    - every new check can fail: mutants.json and the sweep;
    - limits are charged first: item 11.

SELF-REVIEW: 3 A, 7 B, 6 C; fixed 10 (every A and B, commit da54d48c2 and its follow-ups 857d49cc4 and d920f468e;
the earlier session's record; the reviewer's own count of fixed C findings was not kept)
