# sa-no-exception report (DF-U): `dfltUniform_sound` proved

**Summary.** Status: built. The selected tests pass (exit 0, 0 failed). The chain runs the full gate on the final
HEAD. Branch feature/sa-no-exception (HEAD: the commit that writes this report). `dfltUniform_sound` is now a theorem,
proved in spec 1.9's binders and conclusion with no `sorry`. The proof rests on the hypothesis that
reviews/dri-decisions-20261102-pc9-decide-check.md item 2 places inside `ConditionsExact`. `DfltUniformSound` and
`dfltUniformSound_iff` are deleted. Trust: S −7, K +0. No DELTA row. No DRI signature is needed.

Ruling read at the start: reviews/dri-decisions-20261102-pc9-decide-check.md (items 1-6), plus the row note
(`backlog.sh show sa-no-exception`). Plan and spec at 3dfadd302, as on main: PLAN :547, :1509, :1534, :1716, :1722;
spec 1.9 (:1106-1190) and 3.8 (:2531).

## Deliverables, as the ruling rules

| Task / ruling line | Delivered | Evidence |
|---|---|---|
| (1) `dfltUniform_sound` in the ruled form, proved, no `sorry` | b5899d175, `lean/VE/Defaults/Uniform.lean` | `lake build` passes (1261 jobs). `python3 lean/audit.py`: PASS, 748 files, 8295 theorems. `#print axioms`: `propext, Classical.choice, Quot.sound` |
| Ruling 2: the conjunct goes inside `ConditionsExact`, and the theorem's binders and conclusion stay spec 1.9's | `ConditionsExact` = the old conjunct ∧ `∀ p vs, leastUniform D qs B p vs → B.relation p vs` | `tests/test_pc9_statements.py::test_pc9_statements_equal_the_approved_text` (Lean against the amended spec block; `dfltUniform_sound` is compared as a theorem, with no held form) |
| Ruling 2: `conditionsExact_legacy` takes the same conjunct | b5899d175 | proved by `simp only [ConditionsExact, leastUniform_legacy D h]` |
| Ruling 2: the spec change goes in one docs commit | 9ab97c26d (spec 1.9 `ConditionsExact` and its comment, citing this item and the ruling). Plan lines unchanged | `git show 9ab97c26d --stat` |
| (2) delete `DfltUniformSound` and `dfltUniformSound_iff` | b5899d175; their side-table entry goes in d413b84fa | `grep -rn DfltUniformSound lean/VE tools` finds nothing |
| (2) keep F9.3, F9.6 and F9.7 selected | unchanged `#guard`s in UniformExamples.lean | they build. `select_tests` selects UniformExamples through the lake build |
| (3) a fixture of the counterexample's shape that the ruled hypothesis refuses | `Exact.exact_refuses`, plus `Exact.defaultBase_c` (a default base where `dfltUniform` fails) | UniformExamples.lean, section `Exact` |
| (3) a pack shaped like F9.3's `wPack` (premise `C → d`) where it holds | `Exact.exact_holds : ConditionsExact.{u} Uc Dc [wImp]`; `Exact.sound_holds` applies the theorem | same section. `#guard WellFormedSoft Dc && WellFormedU Uc` |
| (4) no `native_decide` | ruling 3 keeps the refutation out of the tree, so (4) is empty. The fixtures use none | `#print axioms` (above) |
| (5) statements.txt and the audit lists through their generators | d413b84fa | `uv run python tools/regen_generated.py --write` (rc 0, 35 entries) |
| Ruling 4: the `.off` limit in one sentence | below | |

`exact_refuses` proves two things on `wEx` (premises `∃x d(x)` and `∃x c(x)`). First, the old conjunct holds on every
admissible base. Second, `ConditionsExact` is false, refuted at `Bc`, the base on {a, b} with `c = {a}` and `d = {b}`.
So the bound alone does the refusing. `defaultBase_c` shows that `Bc` is a default base where `dfltUniform` fails, so
the bound is needed. The ruling's "for each decision name and tuple" is written `∀ p vs`, in the candidate's form;
`leastUniform` holds only at decision names, so the two say the same.

**Limit of the theorem (ruling 4):** on a `.off` condition that ever fires, `ConditionsExact` fails through
`SwitchesOff`, so `dfltUniform_sound` says nothing there. E1d's refusal covers that case, and lifting it is
EXP-D3's.

## How the proof goes

From `hex B hB.1` we get the competitor's admissibility, its `SwitchesOff`, and the bound. `DefaultBase`'s minimality
then forces `B`'s decision tables below `leastUniform`. `sat_dfltUniform` reads each uniform premise from there:
exception, switch (`noneOr_denote`) and `outweighs`. Decision names are distinct (`excepted_inj`, `excepted_only`,
`off_names` via `key_inj`), so each table matches its own key. `h` and `hU` are spec binders the proof does not use,
which gives two linter warnings.

## Seeded bugs (docs/profile-composition/sa-no-exception/mutants.json)

Each was applied alone, shown to fail at the named check, and restored (`git status` clean after each).

| # | Language, file | Mutation | Fails |
|---|---|---|---|
| 1 | Lean, lean/VE/Defaults/Uniform.lean | the ruled conjunct dropped | `dfltUniform_sound` (:219) and `conditionsExact_legacy` (:106) no longer close |
| 2 | Lean, same | the conjunct reads `leastDecisions` (pack conditions ignored); the theorem's proof admitted | `exact_refuses` (UniformExamples.lean:389), `exact_holds` (:408) |
| 3 | Lean, same | the conjunct made an iff (too strong); the proof patched to `.mp` | `exact_holds` (:397, :408); Uniform.lean itself builds |
| 4 | Python, tools/check_pc9_statements.py | `dfltUniform_sound` skipped by the comparison | `tests/test_pc9_statements.py::test_a_changed_statement_fails` |

No Rust product file changed.

## Trust (R16)

`uv run python tools/trust_map.py --since 90807e7f7`: K +0, S −7, D +0, G +0, unclassified +0, trusted −7, PASS.
`ConditionsExact` grows from 7 to 9 source lines, and `DfltUniformSound` (8 lines) is gone. This is no growth, so
there is no `--allow` entry. The FOLLOW-UPS.md row under "## sa-no-exception" asks for the ties pass. The 13 new
fixture definitions are class T in tools/trust-classes.json.

Trust mutants: `mac-pytest.sh --trustmut -- --max-mutants 1000` gave 3 mutants of `ConditionsExact`: 1 SURVIVOR
(`∧ → ∨`) and 2 UNKNOWN (body True/False; "too many explicit universe levels"). A Prop of the spec can only be
exercised by proofs, which the tool does not count, as in pc-9. So all three are allowed in trust-mutants-allow.json,
and the reasons name the proofs and the statement test that break. The rescore with `--allow` ran in full: exit 0,
3 ALLOWED, 0 SURVIVOR, 0 UNKNOWN (trust-mutants.json). Hand mutants 1-3 above kill each of the three operators'
intent through a fixture or a proof.

## Tests run

- While iterating: `lake build VE.Defaults.Uniform`, `lake build VE.Defaults.UniformExamples`, and
  `uv run pytest -q tests/test_pc9_statements.py` (2 passed after the regen).
- Once: `regen_generated.py --write` (rc 0), the full `lake build` and `lean/audit.py` (rc 0).
- Once: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on 6d502193d gave exit 0, 227 units,
  "0 failed" (/tmp/sa-sel.log, final summary line).
- Not run here: the full gate (the chain runs it). No test from main-known-red.txt was among the failures (there
  were none).

## Size, overlap, pilot

Hand-written lines: +422 −38 by `git diff --numstat $(git merge-base HEAD main)`, generated files and
trust-mutants.json excluded, plus this report and DELTA.md. Overlap: in-flight branches touch only
lean/statements.txt among these files, a generated inventory (R12). Pilot bytes: none move now. Soft × weighing,
23 units, ~3.1 kB, is an ESTIMATE for after EXP-D3 lifts the refusal.

## Spec re-read

- `ConditionsExact` against docs/spec/profile-composition.md:1174-1182 (as amended) and ruling item 2: the old conjunct
  kept word for word, the bound added, comment cites the item.
- `dfltUniform_sound` against :1184-1187: binders and conclusion unchanged (test_pc9_statements).
- Ruling items 3 and 5: no `native_decide`, no refutation in the tree, PC-9's guard and comment text otherwise untouched.

## Next item

EXP-D3 (it lifts E1d's refusal using this theorem), then weighing's WG-3, which builds on `ConditionsExact` in the
amended form (ruling item 6).

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A., no route or response changes.
2. Deliverables: PASS, the table above, each row with its commit and check.
3. Tests can fail: PASS, seeded bugs 1-4 (mutants.json), and the trust mutants at exit 0 (trust-mutants.json).
4. Py/Lean/Rust agree: N.A., no answer changes (DELTA.md); the F9.4/F9.7 `#guard`s are unchanged and pass.
5. R8 binding: N.A., no field is relayed.
6. Gate evidence: PASS as far as it goes here. The gate is the chain's, on the final HEAD; no batch evidence lists
   commits.
7. No unsigned item: PASS, no DELTA row, trust S −7 (no growth), no reserved signature.
8. DELTA: PASS, "no user-visible delta" with the reason (DELTA.md).
9. Test selection: PASS, `select_tests --base` chose 227 units including tests/test_pc9_statements.py and the lake
   build of UniformExamples. Seeded bug 4 fails in a selected test.
10. Lean statements say what is claimed: PASS, seeded bugs 1-3 break the build; `check_pc9_statements.py` passes;
    the added hypothesis has the ruling and the mechanised counterexample (reviews/pc9-decide-check-20261102.lean).
11. Budgets: N.A., no evaluator or limit.
12. CPU/memory: N.A., no runtime path changes.
13. Test-removed trailers: PASS, `gate_collection.py --check --prebuilt`: 31869 collected, 0 refused, 0 stale, 0 malformed (the deleted `dfltUniformSound_iff` is a theorem, not a
    collected test).
14. Both directions: PASS, `exact_refuses` (refuses) and `exact_holds` (holds); every claim above names its command.
