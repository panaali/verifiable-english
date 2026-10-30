# me-2nb: `calc@0`'s claims computed once and charged (spec 3.2 (a), (b), limit 10)

**Status:** built; ready for the chain's gate. **HEAD:** the commit that adds this report (branch `feature/me-2nb`).
**What changed:** each value is computed once into a table, each claim's sides once, every step charged (12.2's unit);
F1-28 now `holds` and G-1x512 gets 512 `unknown (limit .digits)` rows (DELTA B1, signed by the DRI). **Open:** me-2nbb
(bench row, `runC_complete`, AR-10 row). **DRI signature needed:** none (B1 signed, item 1; B2 R16, trusted −2).

## Plan rows (`docs/math-evidence/me-2n/REPORT.md` "me-2nb"), delivered

| # | Row | Where |
|---|---|---|
| 1 | `bits` has one owner, `lean/VE/Numbers/Bits.lean`; `Arith/Bounded.lean` imports it | the only Arith edit: its `bits` docstring and `def` lines become the import (3 lines) |
| 2 | `qbits`, `powTooLarge` and `powTooLarge_sound`, `Table`, `valueTable` and `valueTable_read` (the stub's proof), `Expr.evalC`, `Decl.valC`, `valueTableC`, `Claim.decideSides`, `Claim.ofSides` and `_eq`; `Small`'s `Decidable` instance through `digitCount_le_iff`, proved (me-2n review F4) | `lean/VE/Calc/Decls.lean`, namespace `VE.Calc.Work` (the stub's namespace: `VE.Calc.Table` is ME-4's data table). Every charged step has `_some` and `_mono` lemmas. `Val.check` is not needed: the instance is the comparison, so every `Val.guard` is |
| 3 | `runCaseReported` runs the charged rows: a claim's outcome, `sides`, `display` and `tie` read its values evaluated once; `outcome_sound` re-proved through `runC_sound` (`Run.rowOf_outcome`); limit 10's text beside the others | `Run.lean` (`Run.rowOf`, `Run.rowsC`, `runC`, `runC_sound`/`_mono`/`_work`); `Wire.lean` (`Check.sidesC`, `Case.sidesC`, `Wire.workLimit`; `decodeCase` checks limit 10, see Design) |
| 4 | Guards F1-24, F1-28, F1-511, G-1, G-1x512, V-11s, H-1 with their units; route cases F1-28 and G-1; the comment on `calc`'s deadline (no `DEADLINES` change) | `RunExamples.lean:1020-1084`; `tests/data/route-cases.jsonl` (last two lines), `tests/test_calc_service.py`; `ve/backends/lean_service.py:146` |
| 5 | Seeded bugs S1-S6 in `Decls.lean`, each failing a `RunExamples.lean` guard, and one per new definition | below; `mutants.json` |
| — | me-2d F1 and F4 (not done on main): "the sum offset" and "the square often" in the accepted-words guard; the comment at `:413` now says W6's 256-character rule refuses longer words | `RunExamples.lean:952`, `:413` |

**Not delivered (me-2nbb):** the bench row (F1-511, H-1 in `tools/bench/`): it does not fit the size rule.
`runC_complete` (spec 3.2; not one of the DRI's conditions) needs a totality lemma for each charged step. Synthesis-2
edit 1 (`edits-math-evidence.md`: "me-2nb adds `calc@0`'s AR-10 row with its `interface` value") cannot be built yet:
main has no `interface` field and no PC-3 (`grep -rn interface lean/VE/Compose` finds nothing). Edits 2 to 5 are plan
wording for other items. This item implements none of the edits.

## Design notes

- **Limit 10 is in `Wire.decodeCase`.** The approved `outcome_sound` has no hypothesis about work, so a decoded case must
  be one that `runC Work.maxWork` answers. `decodeCase` (used only in theorems and fixtures) refuses with
  `Wire.workLimit` when `Case.sidesC Work.maxWork` is `none`. `runCaseReported` runs `Run.rowsC Work.maxWork` once and
  refuses the same way. Spec 3.2 puts limit 10 after the decoder's checks. me-2nc's lowering charge goes in that place.
- `Run.rowsC` holds the rows; `runC` (the spec's signature) is its projection, so a derivation's search runs once.
  A derivation is charged nothing here (me-2nc).
- `charge` is `visitC`: `VE.Calc.charge` is `Poly.lean`'s budget function. `digitBound` is irreducible, so no proof
  unfolds 10^4,096. `display` and `tie` take the claim's sides in place of the values function.
- Encoder helper lemmas `rowJson_fits` and `_software` take the sides (`vs`); `runCaseReported_fits` is unchanged.

## Statement gate

The nine statements proved equal the stub's after whitespace normalisation: `digitCount_le_iff`, `powTooLarge_sound`,
`valueTable_read`, `Expr.evalC_agrees`, `valueTableC_eq`, `Claim.ofSides_eq`, `runC_sound`, `runC_mono` and
`runC_work`. No theorem of main's `Decls.lean`, `Wire.lean` or `Run.lean` changed. In
`ResponseShape/Encoders/Calc.lean` only the two helper lemmas above changed. A regex extraction script compared the
`theorem … :=` texts. Axioms: `python3 lean/audit.py`: "PASS: 671 source files; 7526 named theorem declarations
audited … only the declared standard axiom allowlist".

## Seeded bugs (`mutants.json`; 28 of 28 killed)

Each bug was planted alone in the checkout, followed by `lake build VE.Calc.RunExamples ResponseShape.Encoders.Calc
VE.Arith.BoundedExamples`, then the file was restored. Where only proofs failed, the failing theorems were proved by
`sorry` and the build was run again, so the guards are shown failing on the behaviour itself.

| Bug | Definition | Behaviour broken | Guards failing (RunExamples.lean) | Proofs failing |
|---|---|---|---|---|
| S1 | `valueTableC` | the table does not store a value | `:55`, `:56`, `:58` (R-1, R-2) | `valueTableC_some` |
| S2 | `chargeV` | a read is not charged its size | `:1042`, `:1043`, `:1045` (F1 units) | — |
| S3 | `chargeQ` | a computed value is not charged | `:1042`, `:1043`, `:1045` | — |
| S4 | `chargeQ` | refused at the limit, not past it | `:1047` (F1-24 at 1,124/1,125/1,126) | — |
| S5 | `Expr.evalC` | a ruled-out power is computed | `:1053`, `:1054` (G-1), `:1061` (V-11s) | `evalC_some` |
| S6 | `digitBound` | 10^4,096 passes 2.4's comparison | `:1025` | the instance, `pow_beyond` |
| M1-M3 | `qbits`, `visitC`, `powTooLarge` | numerator only; free visit; strict bound | `:1042`; `:1042`; `:1031` | — ; `visitC_some`; `pow_beyond` |
| M4-M10 | `binC`, `Expr.evalC` (div), `Decl.valC`, `Expr.evalsC`, `decideSides`, `ofSides`, `Table.read` | second-operand fault; zero divisor; exhausted count; side dropped; `within`'s upper bound; exhausted outcome; missing name | `:1076`; `:56`, `:850`; `:1079`; `:55`; `:1074`; `:1079`; `:1081` | each one's `_some`/`_eq` |
| M11, M15, M21 | `valueTable`, `Check.sides`, `bits` | proof-only definitions; one bit short | — (me-12nb's S8 covers `bits`' guards) | `valueTable_read`; `sidesC_some`; `bits_add_le` |
| M12-M14 | `Check.sidesC`, `Case.sidesC`, `workLimit` | sides charged from 0; empty table; text | `:1042`; `:55`; `:1084` | `sidesC_some` |
| M16-M20 | `Run.rowOf`, `Run.rowsC`, `display`, `tie`, `runCaseReported` | reproduction lost; rows shifted; places; undefined tie; refused within the limit | `:92`, `:384`; `:56`, `:640`; `:850`; `:850`; `:55` | `rowOf_reproduction`; `rowsC_rows`; —; —; `outcome_sound` |
| P1 | `ve/backends/lean_service.py` `case_texts` | a comma one level deep splits a case | `tests/test_calc_service.py::test_route_cases_answer_their_rows` (`CheckerUnavailable`) | — |

Python's product change is the comment. P1 is planted in that changed file. A second Python mutant survived: setting
`DEADLINES["calc"]` to 0 is not caught, because the test passes `HANG_TIMEOUT`. No behaviour of this item depends on it.

## Trust, tests, size

- **Trust:** `uv run python tools/trust_map.py --check`: "K +0, S +0, … trusted -2 … PASS". DELTA row B2 itemises it
  per file. No allowance is needed. The FOLLOW-UPS.md row "## me-2nb" asks for the ties pass, and its probe passes.
- **Tests:**
  - `uv run pytest -q tests/test_calc_service.py`: 22 passed, route cases F1-28 and G-1 included.
  - Selected run (`mac-pytest.sh --select`, GitHub Actions 6 shards, log `/tmp/me2nb/select-run.log`): 432 of 433
    units passed. The failure was `tests/test_assurance_manifest.py`: Wire.lean's and Run.lean's decoder pins. After
    review they were re-pinned (commit 60c45e4c3), and the three ids passed on rerun (`mac-pytest.sh -- <ids>`: "3
    passed").
  - `regen_generated.py --check`: 34 entries.
  - No test in `main-known-red.txt` was involved.
  - The full gate was not run here: the chain runs it on the final HEAD.
- **Size:** this report's figures are measured with `git diff --numstat $(git merge-base HEAD main)`, excluding
  generated files.
  - Lean product and proofs: +663 −78.
  - Fixtures and tests: +92.
  - Evidence and docs: about +190.
  - The total, about +940, is over the ~600 rule. The Lean core of rows 1 to 3 (definitions, the DRI's condition
    proofs and their step lemmas) is +663 by itself and cannot be cut without losing a condition. The rest of the
    plan goes to me-2nbb.
- **Bytes:** 0 (the use-case ceiling); no pilot movement is claimed.
- **Overlap:** no branch in flight changes these hand-written files, apart from the shared append files
  `route-cases.jsonl` and `trust-classes.json`. `foundation/me-1` touches `Decls.lean` but is a stale branch of
  2026-10-15. me-2d has merged.

**Next:** me-2nc (derivations: C1-C4; lowering charged in `decodeCase`'s place for limit 10), then me-3 and me-4.

## Self-review against BUILDER-CHECKLIST

1. PASS: no schema field changes; rows are typed by `runCaseReported_fits` (unchanged statement, re-proved), `tests/test_calc_service.py`.
2. PASS: rows 1-5 delivered; the cut is named (me-2nbb); DELTA rows signed.
3. PASS: 28 of 28 seeded bugs killed (`mutants.json`), S1-S6 each by a `RunExamples.lean` guard.
4. N.A.: no Python or Rust copy of the decision; the Python relay is unchanged.
5. PASS: route cases bound per case (`test_route_cases_answer_their_rows`; P1 breaks the binding and is caught).
6. PASS: no Lean changed after the mutant, trust and selected runs (later commits: the manifest pins and docs); the gate runs on the final HEAD.
7. PASS: no reserved signature; B1 cites DRI item 1, B2 R16 with its FOLLOW-UPS row.
8. PASS: DELTA B1 (answer changes) and B2 (trust); no other user-visible change (`outcome_sound`, H-1 `:1069`).
9. PASS: `tools/select_tests.py --base …` selects `test_calc_service.py` and `test_assurance_manifest.py`, not every unit.
10. PASS: the statement gate above (nine statements equal to the stub's); `lean/audit.py` PASS.
11. PASS: limit 10 refuses before passing (`runC_work`; S4 at `:1047`; F1-24 at 1,124 units is refused).
12. PASS: work is linear in the value table (F1-511 at 396,545 units, `:1045`, a step-count guard in place of 2^511 evaluations); UNVERIFIED for the UDHR and constitution pilots (not timed here; they send no `calc` case that I know of).
13. N.A.: no test was removed or renamed.
14. PASS: both sides of each check (F1-24 under/at/over; `powTooLarge` 13,606/13,607 on both the numerator and the denominator; digits 10^4,096 ± 1; `within` under/at/over, `:1074`); spec re-read: `qbits`, `maxWork`, `powTooLarge` and limit 10's text against `docs/spec/math-evidence.md:803-813` and `:882-887`; the bound against `:932-940`.
