# ps-1c: the rules and the agreement theorems (spec 4.5 Rules.lean, 4.6 Agree.lean) (build report)

No DRI signature is reserved in this item. There are no DELTA rows: the item adds only new Lean, and no existing file's logic changes.
Trusted growth is +8 (K +0, S +8, V +0), covered by standing ruling R16 (see "Trust").
Status: built, nothing cut. Every statement of 4.5 and 4.6 is proved, with S8, S14, S22's formula-level rows, P1-P4 and P13.
Checks: audit PASS, trust_map --check PASS, trust_mutants exit 0, selected tests exit 0, named tests 776 passed.
Open: the full gate runs in the chain on the final HEAD. Next item: PS-2a.

Feature item ps-1c (PS-1's third and last part; plan `docs/spec/presupposition-PLAN.md:731-751`). Branch `feature/ps-1c`,
merge base 9672601e3. Every command's output is in `evidence/tests.txt`.

## Preconditions

- **Statement gate.** PASSED, as the task states. The stub file was read, not committed.
- **Statements are the spec's text.** The probe in `evidence/tests.txt` found all 14 pieces of 4.5 and all 6 of 4.6 in the sources.
- **Synthesis round 2.** Items 1, 5, 7 and DEC 10 belong to others, as the task says. A grep of the plan finds items 2, 3, 4
  and 6 not yet applied; the plan is outside this item's file list, and none of them changes a 4.5 or 4.6 statement.
- **Layers.** `tools/check_lean_imports.py` passes with no `layer_policy` edit and no new exception.
- **In-flight overlap.** `lean/VE.lean`, `lean/VE/Audit.lean` and `tools/trust-classes.json` are shared with df-5, et-4b,
  pc-1g, pe-1, wg-2-siff, me-1 and AR-1. My hand edits are 2 import lines and added entries; Audit.lean is generated.
  No branch touches `lean/VE/Presupposition/`.

## Plan rows delivered

| Row (task "Deliver") | Commit | Evidence |
|---|---|---|
| (1) Rules.lean: `ruleGoal`, `conditionNode`, `conditionRule` and the 8 theorems named | fa82f43da | audit PASS; `rule_collapse_typed` goes through `bindAll_denote_nil` (Rules.lean:124) |
| (2) S14a, S14b, both directions of 7.2's `condition_applies` and `rule_collapse_decides` | fa82f43da | Examples.lean:344-358 |
| (2) S22's formula-level rows; `unsaid_iff` on the `unspecified` cell, both directions | fa82f43da, a21cf5da0 | Examples.lean:383-419 |
| (3) Agree.lean: `discourse_definite_is_row`, `data_attribute_proved`, `speech_question_top` | 9395f684a | audit PASS |
| (3) S8: flags T and `U` T; functional F and `U` F (plus total F and `U` F) | 9395f684a | Examples.lean:420-433 |
| (3) P1-P4 through `buildPre … 0`, P13 | 9395f684a | Examples.lean:438-470 |
| (4) `lean/VE.lean`, trust classes (S: the 3 definitions; T: fixtures; no K), inventories | fdfa8912b, 0cb4bda7c, cf7bdd3be | `regen_generated.py --check`: 35 entries |

Guards in Examples.lean: 110 → 161 (`grep -c '^#guard'`), plus 3 `decide` statements and 2 `example`s for `unsaid_iff`.

**Not in this item (PS-2a):** S22's `SatUnder` and `SameModels` row (spec 7.2:1318), which needs PS-2a's admission; P1-P4's
heading obligations (A24, A25); ps-1b's `expectedReadings` and `carrierAllowed` rows. **PS-2b:** the documents S7 and S7b of
7.2's `unsaid_iff` row. **PS-6r:** the English of P1, P2 and P4.

## Deviations

- **One import beyond the spec's block.** Rules.lean also imports `VE.Discourse.Descriptions`, for `denote_prefix` in
  `source_identity_entails`. Rows.lean's block already imports it, and the layer check passes.
- **Helper lemmas.** `exists_child_map`, `yieldsD_map` and `decidesD_map` in Rules.lean, all proved.
- **The `conditionNode` seeded bug.** The task expected S14b's `condition_applies` row to catch a dropped `N.guard`. It
  cannot: S14b's guard is implied by `pre`, so both of its rows keep their values. I added a row with a guard `pre` does
  not imply (`r14other`, Examples.lean:356), and that row catches it.
- **P13's form.** The use case declares no constants (`usecases/us-constitution-14th-s1/model-true.json`), and the
  Amendment says "the State wherein they reside". So P13 is S8's flags over `∀x:person`, with `definite 1`.
- **Fixtures beyond the spec:** the `hname` counterexample (:378-381), carve-outs (:357-358), exceptions (:367-370).

## Seeded bugs (Lean only; this item changes no Python or Rust product code)

`mutants.json` lists 15, with `file`, `find`, `replace` and `test`. Each was applied alone and restored. "Guards" fail once
the theorem bodies of Rules.lean are replaced by `sorry`; otherwise the broken proofs stop the build first.

| Id | Definition or statement | Mutant | Proofs | Guards (Examples.lean) |
|---|---|---|---|---|
| **M3** (spec 7.5) | `ruleGoal` | binds `N.over` | Rules:124, :148 | **S14's goal :349**, :375, :398 |
| L-ruleGoal-pre | `ruleGoal` | no `applies` antecedent | Rules:124, :148 | :345, :375, :380 |
| **L-conditionNode-guard** | `conditionNode` | drops `N.guard` | Rules:27 | **:356**, :366, :401, :405, :406, :408, :411 |
| L-conditionNode-cond | `conditionNode` | drops the condition | Rules:27 | :352, :355, :361, :366, :370, :372, :381 |
| L-conditionNode-carve | `conditionNode` | drops carve-outs | Rules:27 | :357 |
| **L-conditionRule-every** | `conditionRule` | conditions every node | Rules:38, :104 | **the other-rule row :360**, :362, :364, :370 |
| L-conditionRule-others | `conditionRule` | conditions the others | Rules:104 | :352, :360-362, :364, :370, :381 |
| L-P-plural, -generic, -definite | `buildPre` (Rows.lean, temporary) | wrong `pre` | none | P1, P2 :445-446; P3 :447; P4 :448 |
| L-S8-unique | S8's fixture | no uniqueness | none | :429 |
| L-P13-open | P13's fixture | `definite 0` | none | :468, :470 |
| S-definite-1, S-speech, S-unsaid | 3 statements | wrong statement | Agree:17; Agree:32; Rules:142 | none |

**R16 mechanical mutants.** The first run gave 9 KILLED and 2 UNKNOWN: a `decide` inside a term proof is no check. I moved
those values to `decide`-proved statements (a21cf5da0). The rescore gave 11 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 ALLOWED, exit 0,
head cf7bdd3be (`trust-mutants.json`). The tool generated mutants only for `conditionRule`; `ruleGoal` and `conditionNode`
are covered by the hand mutants above.

## Trust

`tools/trust_map.py --check` PASS: Rules.lean S +8 (`ruleGoal`, `conditionNode`, `conditionRule`); Agree.lean has no
definitions; K +0. The allowance in `docs/trust-baseline.json` is "SIGNED by standing ruling R16 (DRI-RULINGS.md), ps-1c,
2026-10-18". The "## ps-1c" ties-pass row is in FOLLOW-UPS.md.

## Size, bytes, evaluators

- **Size.** `git diff --numstat 9672601e3`, without generated files and `trust-mutants.json`/`trust-baseline.json`: see the
  last line of this section, swept over every hand-written file (ps-1b-review F1). About 50 lines of it are the pasted spec.
- **Pilot bytes.** 0, as the plan claims for PS-1. The RF census row (estimate) waits for PS-2a.
- **Evaluators.** None added: `conditionRule` is one `map` over nodes the caller holds. PS-2a's runner charges them.
- **Total: 560 additions, 1 deletions** (REPORT.md 113/0, tests.txt 39/0, mutants.json 20/0, VE.lean 2/0, Agree.lean 36/0, Examples.lean 155/1, Rules.lean 151/0, trust-classes.json 44/0).

## Spec re-read

- 4.5 against `presupposition.md:752-809`, 4.6 against `:811-833`, by the probe, and the note on `hname`.
- 7.1 S14 `:1282`, S8 `:1283`, S22 `:1288`; 7.2 `:1304`, `:1305`, `:1309`, `:1318`; 7.4 P1-P4 `:1365-1369`, plan P13
  `PLAN:585`; 7.5 M3; checklist 9 item 5 (`rule_collapse_typed`'s binders and `conditionRule` against S14 and M3: :349, :375).

## Self-review against BUILDER-CHECKLIST

1. Typed Lean answers: N.A., no relay or service mode added.
2. Deliverables: PASS, the table above; `git diff --name-only` shows no Python, Rust or read-only Lean file.
3. Tests can fail: PASS, `mutants.json`, `trust-mutants.json` (exit 0).
4. Three-way agreement: N.A. for new behaviour; `test_discourse_three_way.py`, `test_norms_three_way.py`, `test_norm_defaults_three_way.py` pass.
5. R8 binding: N.A., no Lean answer is read by Python.
6. Gate evidence: PASS for the checks in `evidence/tests.txt`; the chain runs the gate on the final HEAD.
7. Unsigned items: PASS, `trust_map --check`; no DELTA rows.
8. User-visible changes: PASS, no answer path edited (`git diff --name-only`); 776 named tests pass.
9. Test selection: PASS, `select_tests` picked 100/544 units rather than all.
10. Statements: PASS, the statement probe; S-definite-1, S-speech and S-unsaid break the build.
11. Budgets: N.A., no operation with a budget.
12. CPU or memory: N.A., only `#guard`s and proofs run new code, at build time.
13. Test-removed trailers: PASS, `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
14. Both directions: PASS, Examples.lean:344-358, :409-419, row8, row13; claims cite `evidence/tests.txt`; "Spec re-read" above.
15. Overclaim: PASS, universal words checked against `evidence/tests.txt`. Silent cut: PASS, deliverables (1)-(4) built, none cut. New checks can fail: PASS, `mutants.json`. Limits: N.A., no evaluator.
