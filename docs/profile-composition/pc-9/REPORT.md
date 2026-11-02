# pc-9 report: typed priority checks and the "no exception" statements

**Summary.** Status: built; selected tests pass after one fix; the chain runs the full gate on the final HEAD. Branch
feature/pc-9 (HEAD: the last commit, which writes this report). New: `lean/VE/Defaults/Uniform.lean`, the guard line
in `defaultsRows`, F9.1-F9.7 in `UniformExamples.lean`, a statement check, a relay test. Trust +59 (S +56, V +3,
K +0) under R16. Open: `dfltUniform_sound` is stated and not proved (DF-U, DRI decision 2026-11-02 pc-9 items 1 and
3); E1d's display, asked of the DRI (below). The DELTA row is R16 (the DRI confirmed the citation, item 4).

Plan and spec at 3dfadd302: PLAN "PC-9" (:1494-1535), 4.1-4.2 (:514-574), order table (:1766); spec 1.8, 1.9, 3.8,
E1d (:1341), refusal row 11 (:3008), F9.1-F9.7 (:3230-3236). Statement gate: pc-d2's confirmation review passed
2026-10-30 (plan change log); row-level I2 applies (structure row, 0 B).

## Plan sync (pc-plan-sync 2(b))

No in-flight branch touches docs/spec/profile-composition-PLAN.md or profile-composition.md (`git diff --name-only
main...<b>` over every lean-first/, feature/, infra/ and foundation/ branch), so both files are 3dfadd302's bytes,
unchanged (commit c4045543f).

## Plan rows

| Row | Delivered | Where | Test |
|---|---|---|---|
| `packConditions`, `noneOr`, `dfltUniformOf` (by `decisionRule N`), `dfltUniformLabelled`, `dfltUniform` | yes, spec text | Uniform.lean | `tools/check_pc9_statements.py` (tests/test_pc9_statements.py), UniformExamples.lean:75, :91 |
| `dfltUniform_legacy` proved | yes | Uniform.lean:63 | F9.4 (:132), F9.5 (`decodeLayered_uniform`, :150) |
| `leastUniform`, `ConditionsExact` | yes (body of `leastUniform` signed: DRI 2026-11-02 item 2) | Uniform.lean | `leastUniform_legacy`, `conditionsExact_legacy`, per-branch `decide` checks :111, :118, :124 |
| `dfltUniform_sound` stated | as `DfltUniformSound` with the lock `dfltUniformSound_iff` (DRI 2026-11-02 item 1); not proved here (DF-U) | Uniform.lean | the lock; tests/test_pc9_statements.py |
| `precedence_apart` by `rfl` | yes | Uniform.lean:23 (its statement reads `SoftDoc`, so it cannot sit in Norms/Tree.lean, which SoftNorms imports) | `#guard` :32 |
| no `Compose/Priority.lean`, no `priorityCheck`, no mixed-cycle refusal | none added | - | F9.1 (:23) |
| guard `providerConditions` in `defaultsRows`, `providerRefusal`, E1d | yes; E1d is `providerE1d` | Route.lean:21, Uniform.lean | F9.3 (:64-66), F9.6 (:154-155), F9.7 (:160, :162) |
| F9.1-F9.7 | yes | UniformExamples.lean | F9.1 :23, :29, :32; F9.2 :36; F9.3 :64-68; F9.4 :130, :132; F9.5 :150, `decodeLayered_uniform`; F9.6 :154-155; F9.7 :160, :162 |
| relay side | Python relays Lean's text; no Python copy | tests/test_defaults_uniform.py | `test_the_refusal_is_relayed_verbatim`, `test_no_python_copy_of_the_guard_or_its_sentence` |
| F6.7 | left to PC-6 (PC-6 not launched; task) | - | - |

Deviations: (1) `DfltUniformSound` form (DRI item 1); (2) `leastUniform`'s body (DRI item 2); (3) E1d's text lives in
Lean as `providerE1d`; it is not carried to the CLI: no route on main renders a refusal sentence, every sentence
passes the all-derivations gate before registration (spec 2; E1, E1s and E2 are PC-4's), and no request reaches the
refusal. Asked of the DRI (inbox/dri/20261102T163244Z-pc-9-4172182.md); until it rules, this is open. (4) The
encoder proof `layeredKindCase_fits` (lean/ResponseShape/Encoders/NormDefaults.lean) gains the guard's case (3 lines).

## Evidence (commands)

- `lake build` (inside `uv run python tools/regen_generated.py --write`, rc 0 in /tmp/pc9scratch/regen3.log) and
  `python3 lean/audit.py`: "PASS: 726 source files; 8070 named theorem declarations audited".
- `uv run python tools/trust_map.py --check`: "against d8f58bf3be47: K +0, S +56, D +0, G +14, ... trusted +59" and
  "PASS: K, S and untied [V] within d8f58bf3be47 and the allowances introduced since"; allowance recorded with
  `--allow ... --signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), pc-9, 2026-11-02"`.
- `mac-pytest.sh --trustmut -- --max-mutants 1000 --allow ...` (a full run, no --rescore, after the F1 wording fix):
  exit 0, trust-mutants.json counts 91 KILLED, 52 ALLOWED, 12 INVALID, 0 SURVIVOR, 0 UNKNOWN, 0 NOT RUN (head
  4bf5b3ae0; the first full run is
  trust-mutants-run1.json: 41 SURVIVOR and 33 UNKNOWN, fixed by the multi-element fixtures of 0d333d2e4 or allowed
  with one reason each in trust-mutants-allow.json).
- `mac-pytest.sh --select -- --base d8f58bf3b --run` (HEAD 01d6e725, 426/530 units): 4 failures, all
  tests/test_assurance_manifest.py (Route.lean's whole-file pin, the decoder line total, UniformExamples.lean
  unclassified); fixed in 8f3b259a; `mac-pytest.sh --` on the 4 ids: "4 passed". Before that run,
  `tools/check_lean_imports.py` refused UniformExamples -> RouteExamples (layer 4); fixed in 49c2d94e3. None of the
  failures is in main-known-red.txt.
- `uv run pytest -q tests/test_defaults_uniform.py tests/test_pc9_statements.py`: 8 passed.
- Size: `git diff --numstat $(git merge-base HEAD main)` without generated and verbatim files: 677 added lines before
  this report (trust-mutants-allow.json 26 after compaction, Uniform.lean 130, UniformExamples.lean 164).

## Seeded bugs (Lean and Python; mutants.json, applied one at a time, restored, `git status` clean)

1-2. `providerConditions` ignores conditions / reads only id `weighing`: F9.3 (:64) and F9.6 (:154) / F9.6 (:154).
3-4. guard on every kind (`layeredKindCase`): F9.7 (:160, :162) with `layeredKindCase_other` set aside; as is,
`layeredKindCase_other` (Route.lean:36). 5. guard removed: F9.3, F9.6. 6. `packConditions` without the key filter:
:75, :91, :118. 7. `noneOr []` gives `d`: `dfltUniform_legacy`. 8-9. `dfltUniformOf` by `N.name` (exception, switch):
:91. 10. ranking ignores conditions: :68. 11. `dfltUniform` reversed: :150. 12-14. each `leastUniform` branch without
`packConditions`: :111, :118, :124. 15. `ConditionsExact` without `SwitchesOff`: `conditionsExact_legacy`.
16. `DfltUniformSound`'s conclusion: the lock. 17-18. `providerRefusal`, `providerE1d` texts: :65, :66.
19-24 (Python, review F-ready1). `tools/check_pc9_statements.py`: the held form drops the binders, `leastUniform`
compared with its body, the Lean text ignored, exit 0 on a difference, 1.8 read alone, theorems skipped: each fails
`tests/test_pc9_statements.py` (ids in mutants.json). No Rust product code changed, so no seed there.

## Spec re-read

`packConditions` ... `providerRefusal` against profile-composition.md 1.9 (:1121-1196) and `precedence_apart` against
1.8 (:1094-1099), by `tools/check_pc9_statements.py` (12 equal); E1d against :1341 (`#guard` :66); refusal row 11
against :3008; F9.1-F9.7 against :3230-3236; the guard's place against 3.8 (:2541-2542) and plan :1513-1514.

Pilot bytes: 0 expected (no answer on main changes). Next: pc-6, defeasible's DF-U (`dfltUniform_sound`, and item 3
of the DRI decision), weighing's WG-3.

## Self-review against BUILDER-CHECKLIST

1. PASS: no new relayed field; the refusal is an existing error row (`test_the_refusal_is_relayed_verbatim`).
2. PASS: rows above; no Python copy (`test_no_python_copy_of_the_guard_or_its_sentence`); overlaps: lean/VE.lean
   (union-merged import list) and generated files (R12) only; Compose/, Service/, Zone files untouched.
3. PASS: mutants.json (24: 18 Lean, 6 Python), trust-mutants.json exit 0.
4. N.A.: no Python or Rust path changes; Lean answers unchanged (F9.4, F9.7, `decodeLayered_uniform`).
5. N.A.: no field Python reads is added.
6. PASS for the evidence order: selected tests on the committed tree; the full gate is the chain's.
7. PASS: DELTA row 1 cites R16 (DRI item 4); trust growth itemised there.
8. PASS: DELTA.md; no reachable answer changes (`decodeLayered_uniform`).
9. PASS: `tools/select_tests.py --base d8f58bf3b` selects tests/test_defaults_uniform.py and test_assurance_manifest.py.
10. PASS: seeds 7, 15, 16 break `dfltUniform_legacy`, `conditionsExact_legacy`, the lock; `tools/check_pc9_statements.py`.
11. N.A.: no budget or deadline added; the guard is one Bool over the pack list.
12. N.A.: one `List.any` over the packs per defaults case; no pilot path reaches it.
13. N.A.: no test removed or renamed.
14. PASS: both directions: F9.3/F9.6 refuse, F9.4/F9.7 accept; every claim above names its command.
