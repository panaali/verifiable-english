# tm-esc-sweep-1123: the 11 unallowed SURVIVORs of the 2026-11-23 nightly mutation sweep

Row tm-esc-sweep-1123 (rows tm-esc-kb-1-1, tm-esc-kb-7-1 .. tm-esc-kb-7-10). Nightly record
`test-skip/nightly/20261123T0939Z.json` (manage-agents; head fc84ed56a2c9, base 039d3dd5190e). Branch from local main
df25d3c3b3. Trusted (non-test) Lean is unchanged: this branch adds only files under `docs/kernel/`.

## Result

**Survivors open: before 11, after 0** (MEASURED: `tm-nightly.py classify` on the nightly record, see "Evidence").
11 allowed as Props no check can evaluate (the task's verdict (a): "a Prop whose body no trusted decision reads"),
0 gaps killed, 0 faults in trusted behaviour.

All 11 are mutants of a `Prop` definition. Each states a property of the route's answer by equality of `Json` values
(`Except String Json` or `Json`), under an existential. `Lean.Json` has no `DecidableEq` (lean-toolchain v4.24.0: `Lean/Data/Json/Basic.lean`
derives only `Inhabited` for it; its `==` is a `partial` `BEq`), so neither `decide` nor `native_decide` nor a `#guard` can evaluate
any of them. The tool kills a mutant only through a check that evaluates (`trust_mutants.py` docstring: KILLED only when a
check's own refutation fails), so no test file can kill them. Every one of them breaks at least one proof in trusted
code (the "proofs it breaks" column). So a real `lake build` would refuse each mutant and none could reach main unnoticed (INFERRED from the tool's cut list, not
measured by a separate build). The tool's rule (`R16`, the docstring's "a Prop no check can evaluate is exercised only by those proofs, so an
--allow reason for it cites one") is to allow them with a reason that names the proofs. The wording follows the precedents
kb-1 (`docs/kb-1/trust-mutants-allow.json`, Path.Ran) and kb-validators (`docs/kernel/kb-validators/trust-mutants-allow.json`:
the same `EvaluationAnswer and-or` pair at other lines).

Why the nightly counted them unallowed:
- **kb-7 (10):** kb-7's merge fd97f094f2 added `lean/VE/Route/MeteredWire.lean` and `lean/VE/SoftNorms/ElaborateSound.lean`
  but no trust-mutants record or allow file (only `docs/kernel/kb-7/seeded-bugs.json`). tm-nightly reads an allowance
  only from the blamed label's own files, so there was nothing to read. This branch adds `docs/kernel/kb-7/trust-mutants-allow.json`
  and the record `docs/kernel/kb-7/trust-mutants.json`.
- **kb-1 (1):** kb-1's record already has the row ALLOWED (`docs/kb-1/trust-mutants.json` M001). Its directory is
  `docs/kb-1/`, one level under docs/. tm-nightly's `label_files` reads `docs/*/<label>/` and `RECORD_DIR`
  `docs/<family>/<dir>/trust-mutants.json` only, so it never finds it (tool defect, below). This branch adds the same pair and
  reason, re-judged at main, under `docs/kernel/kb-1/`, with kb-1's three other Prop pairs (Ran body-false and eq-ne,
  Path eq-ne: M103, M401, M400) so that a later nightly does not flag them again (review finding 3). `docs/kb-1/` is untouched: its DELTA row is signed.

## Table

Lines are at main df25d3c3b3. The three files are byte-identical to the nightly head fc84ed56a2c9 (`git diff --stat`
is empty), so the ids and lines are the nightly's. "Breaks" lists the tool's detail. The tool names a theorem's docstring
line, so the theorem itself starts a few lines later.

| row | nightly id | file:line | definition, operator | verdict | reason (the allow file's, abridged) | proofs it breaks | evidence |
|---|---|---|---|---|---|---|---|
| tm-esc-kb-1-1 | M027 | VE/Kernel/Carry.lean:26 | Path.Ran, body-true | allowed (Prop, no check can evaluate) | `r.result = p.run r.case` is an equality of Except String Json. shell_provenance proves it of every row a shell builds; ran_meaning reads it. | Carry.lean:35 (shell_provenance), :52 (ran_meaning); nightly also CoreCheck.lean:393 (document_core_sound) | docs/kernel/kb-1/trust-mutants.json M027 (raw SURVIVOR) |
| tm-esc-kb-7-1 | M141 | VE/Route/MeteredWire.lean:23 | MeteredRun.EncodesEvaluation, body-false | allowed | ∃ explanation : Json, an equality of Json answers. Proved only by answer_evaluate (`⟨_, rfl⟩` on the encoder). It is a conjunct of EvaluationAnswer in all four families. | MeteredWire.lean:73 (answer_evaluate) | kb-7 record M141 |
| tm-esc-kb-7-2 | M144 | VE/Route/MeteredWire.lean:230 | MeteredRun.CaseModel, body-false | allowed | ∃ given, an equality of Except String Json (the model field; under layers, completeModel's result). A conjunct of runWith_sound's conclusion, so also of wire_sound_of and the four metered_wire_sound* (:321, :336, :350, :364). | MeteredWire.lean:249 (runWith_sound) | kb-7 record M144 |
| tm-esc-kb-7-3 | M156 | VE/SoftNorms/ElaborateSound.lean:41 | Run.BackgroundField, body-false | allowed | ∃ entries, an equality of Json arrays. Established only by regeneratedCore_fields (the runner's own background list). Read by ElaborationAnswer and its theorems. | ElaborateSound.lean:87 (not_elaborationAnswer_of_null_background), :112 (regeneratedCore_fields) | kb-7 record M156 |
| tm-esc-kb-7-4 | M157 | VE/SoftNorms/ElaborateSound.lean:48 | Run.PremisesField, body-false | allowed | ∃ entries, an equality of Json arrays. Established only by regeneratedCore_fields. | ElaborateSound.lean:112 | kb-7 record M157 |
| tm-esc-kb-7-5 | M158 | VE/SoftNorms/ElaborateSound.lean:74 | Run.ElaborationAnswer, body-false | allowed | Equalities of Except String Json read by key, plus two ∃ over Json fields. Conclusion of elaborationAnswer_ok and soft_wire_elaborate; premise of elaborationAnswer_reads and not_elaborationAnswer_of_null_background. | ElaborateSound.lean:78 (elaborationAnswer_reads), :96 (elaborationAnswer_ok) | kb-7 record M158 |
| tm-esc-kb-7-6 | M244 | VE/Route/MeteredWire.lean:189 | MeteredRun.EvaluationAnswer, and-or | allowed | Per family, ∃ vocabulary, formulas, model, result, with Except equalities over Json. Conclusion of run_evaluation_sound, runWith_sound and metered_wire_sound. kb-validators allows the same pair; its record has every and-or row of EvaluationAnswer ALLOWED (M008-M048 at :191-:213). | MeteredWire.lean:216 (run_evaluation_sound) | kb-7 record M244 |
| tm-esc-kb-7-7 | M245 | VE/Route/MeteredWire.lean:230 | MeteredRun.CaseModel, and-or | allowed | as tm-esc-kb-7-2 | MeteredWire.lean:249 | kb-7 record M245 |
| tm-esc-kb-7-8 | M262 | VE/SoftNorms/ElaborateSound.lean:42 | Run.BackgroundField, and-or | allowed | as tm-esc-kb-7-3 | ElaborateSound.lean:87, :112 | kb-7 record M262 |
| tm-esc-kb-7-9 | M263 | VE/SoftNorms/ElaborateSound.lean:49 | Run.PremisesField, and-or | allowed | as tm-esc-kb-7-4 | ElaborateSound.lean:112 | kb-7 record M263 |
| tm-esc-kb-7-10 | M264 | VE/SoftNorms/ElaborateSound.lean:74 | Run.ElaborationAnswer, and-or | allowed | as tm-esc-kb-7-5 | ElaborateSound.lean:78, :96 | kb-7 record M264 |

What the and-or mutants do: each turns one `∧` of the statement into `∨`. That weakens the stated property (for example
M264, one of the two `∧` on ElaborateSound.lean:74: the answer's `id` OR the rest is as stated). The proofs that build the statement with the anonymous constructor
then fail to elaborate, so main's build refuses the mutant. The body-false mutants make the property unprovable, and the
proofs that establish it fail the same way. The one body-true mutant (M027) makes `Ran` trivially true. Then
shell_provenance's `rfl` and ran_meaning's `h ▸ ha` fail. Not one of the 11 shows that trusted behaviour on main is wrong.
Each mutated statement is exactly what main's proofs refuse.

## Evidence (MEASURED)

- Plan mapping at main (`trust_mutants.plan`, base 039d3dd5190e, 8789 planned): every nightly id maps to the same id at
  main by text (file, definition, operator, before, after).
- Runs (VM, iso scope tmesc-1123 16G, worktree lean/ restored from the shared main build by lean-prep.sh):
  - `uv run python tools/trust_mutants.py --base 039d3dd5190e --max-mutants 10000 --jobs 4 --only M027,M103,M400,M401 --test
    lean/VE/Kernel/CarryChecks.lean --allow docs/kernel/kb-1/trust-mutants-allow.json --json docs/kernel/kb-1/trust-mutants.json`:
    exit 0, "4 ALLOWED" (raw: M027, M103, M401 SURVIVOR; M400 UNKNOWN, CarryChecks.lean:16 type mismatch, as kb-1's
    reason says), 99 s.
  - the same with `--only M141,M144,M156,M157,M158,M244,M245,M262,M263,M264 --test lean/VE/Route/MeteredProfileExamples.lean
    --allow docs/kernel/kb-7/trust-mutants-allow.json --json docs/kernel/kb-7/trust-mutants.json`: exit 0, "10 ALLOWED"
    (all raw SURVIVOR), 304 s. Logs: manage-agents reviews/tm-esc-sweep-1123/kb1.log, kb7.log.
- The number: `tm-nightly.py classify test-skip/nightly/20261123T0939Z.json <worktree> 039d3dd5190e`. It ran in a sandbox:
  `TEST_SKIP_DIR` a copy of test-skip, `TM_NIGHTLY_NO_SIDE=1`, a copied BACKLOG, `TM_TARGETED_ONLY_FLAG` a /tmp path.
  Nothing live was written.
  - before (`~/code/ve-integration`, main df25d3c3b3): unresolved `{"SURVIVOR": 11, "UNKNOWN": 1, "NOT RUN": 8548}`;
    allowed SURVIVOR 16 of 27. Per file: Carry.lean allowed 0 of 1, MeteredWire.lean 3 of 7, ElaborateSound.lean 0 of 6.
  - after (this branch, committed head d54d507df9 before this line was added; the same with the files uncommitted): unresolved `{"UNKNOWN": 1, "NOT RUN": 8548}`; allowed SURVIVOR 27 of 27. Per file:
    Carry.lean 1 of 1, MeteredWire.lean 7 of 7, ElaborateSound.lean 6 of 6.
  - The record stays incomplete: 8548 NOT RUN, because the sweep ran out of budget (nightly parts 2-4 had no record), and
    1 UNKNOWN that is not in this row. Neither changes here.

## Tool defect (one line; not fixed here, tm-nightly.py unchanged)

- tm-nightly.py `label_files`/`RECORD_DIR` read only `docs/<family>/<label>/`. A label whose record sits at
  `docs/<label>/` (kb-1, and any other one-level record dir) is never read, so its own ALLOWED rows never count. The fix
  is a glob for `docs/<label>/` too, plus `RECORD_DIR` `docs/(.+/)?<dir>/trust-mutants.json`.

## Trust and DELTA

No trusted Lean line changes and no DELTA row: the branch adds records and allow files only (docs/). No signature is
reserved.
