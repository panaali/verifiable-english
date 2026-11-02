# df-5a: the zone at one situation, in Lean (report)

**Status**: review round 1 fixed (F1, its one B finding); ready for recheck. No DRI signature is reserved.
**Fix**: `zoneCharge` counts the record, the open atoms (`openAtomsCount` = `openAtomsAll`'s length, proved) and the
typed atoms before anything is listed; the review's probe answers `budget 20000000 12` in 2 s (it timed out at 30 s).
**Open**: F2, F3 (C, follow-ups); df-5ab (`forcedAll`); the full gate (the chain runs it). Trust unchanged (+64, R16).

**What changed**: `lean/VE/Defaults/Zone.lean` holds the zone, `defaultZoneOf` (nd-atoms' enumeration over
`openAtomsAll`, no cone pruning) and seven theorems with no `sorry`. `ZoneExamples.lean` holds spec 8.6's fixtures as
`#guard`s.
**Recorded deviations**: `valid` added to four statements of spec 7.5 (signed:
`reviews/dri-decisions-20261102-df-5a.md`). The `forcedAll` group is cut to df-5ab. The item is about 1,190 hand-written
lines, against the 600-line rule; the DRI accepted it as it is (`reviews/dri-decisions-20261102-df-5a-size.md`, "Size").
**Not run here**: the full gate (the chain runs it), and the 28 selected files over 120 s that were deferred to the
chain gate (`evidence/selected-tests.txt`).
**Bytes 0. DELTA**: trust only (T1, R16).

## Plan rows (plan 3.6 and batch DF-5 at 174fbb62a; spec 7.5, 8.6, 8.9; task deliverables (1) to (4))

| Row | Delivered | Where | Evidence |
| --- | --- | --- | --- |
| Statement gate: 3.6's `open VE.Weighing (AdmissibleCompletion OutcomeIn decisionAtoms openNames SettledZ ZoneUnknown)` resolves on main after wg-6a | yes | `Zone.lean:17` (the line verbatim) | `lake build VE.Defaults.Zone` |
| No `def` of the six weighing names under `lean/VE/Defaults/` (DRI 2026-10-31 item 2) | yes | — | `git diff main...HEAD -- lean/VE/Defaults \| grep -nE '^\+def (decisionAtoms\|openNames\|AdmissibleCompletion\|OutcomeIn\|SettledZ\|ZoneUnknown)\b'`: no match (exit 1) |
| (1) `DecLe`, `Observed`, `switchesOffRecord`, `DefaultCompletion`, `ByDefaultZ`, `ByDefaultLeftTo`, `DefaultZone`, `maxDefaultAtoms` (12), `openAtomsAll` | yes, word for word | `Zone.lean:20-85` | `evidence/statements.out`: OK for each |
| (1) `defaultZoneOf`: nd-atoms' bounded enumeration over `openAtomsAll` (nd-atoms' `subsets`, valued by nd-atoms' `coneAtomVX` and `kleene`), no cone pruning, no second enumerator; full assignments that satisfy X and `Fill_T` and agree with the observations, then the decision-minimality filter; `unknown (budget)` beyond `maxDefaultAtoms` | yes (signature word for word; body is this item's) | `Zone.lean` (`zoneRow`, `decSub`, `zoneAtoms`, `zoneDeclOk`, `zoneRecordOk`, the charge `tupleCount` … `zoneCharge`, `zoneMin`, `defaultZoneOf`) | fixtures below |
| (1) Evaluator rule (DRI 2026-10-27): each value read once, size charged against the limit, a large well-formed situation that ends within it | yes (fixed in review round 1, F1: the first build charged the count only after listing every atom) | `zoneCharge`, first in `zoneMin` and `zoneFormOf`: the record's length against `maxZoneRecord` (1,024), the open atoms by `openAtomsCount` (sorts' sizes and the record's tuples, no atom listed; `openAtomsCount_eq` proves it is `openAtomsAll`'s length, so `budget n` keeps the exact `n` of `defaultZone_budget`), and the typed atoms against `maxZoneRecord + maxDefaultAtoms`. Only then are the switches record, the atom lists and the assignments built, each let-bound once per function (`zoneMin` and `defaultZoneOf` each build the record and the atom list once) | `ZoneExamples.lean` "The budget": the review's probe (ten binary predicates at 1,000 entities, 20,000,000 open atoms) is `budget 20000000 12`, and at 100,000 entities `budget 200000000000 12`; DF-λ at 13 operators is `budget 26 12`; DF-λ at 6 operators (12 atoms, 4,096 assignments) ends with `no`; the record at 1,024 and 1,025 entries, the typed atoms at 1,036 and 1,038; `evidence/F1.out` |
| (1) `noExceptionRecord`, `zoneForm` | yes, word for word | `Zone.lean:189-202` | `evidence/statements.out` |
| (1) `forcedAllOf` | **no: df-5ab** (size) | — | — |
| (2) `defaultZone_byDefault_sound`, `_leftTo_sound`, `_notSaid_sound` | yes, with `valid` (DRI-signed) | `Zone.lean` | `evidence/statements.out` OK against the amended 7.5; `lean/axioms.txt`: propext, Classical.choice, Quot.sound only |
| (2) `defaultZone_noCompletion_sound`, `defaultZone_budget` | yes, word for word | `Zone.lean` | same |
| (2) `decisionAtoms_none`, `defaultZone_eq_noException` | yes, word for word | `Zone.lean` | same |
| (2) `forcedAll_sound`, `defaultCompletion_below`, `forced_everywhere` | **no: df-5ab** (the task's own fallback) | — | — |
| `cone_minimal_iff` (and its helpers `Adm`, `Splice`, `AgreeOn`, `DecLeOn`, `ConeIndependent`, `QueryIn`) | not built, as the task says (D10: cone pruning stays off) | — | no `sorry` anywhere (`python3 lean/audit.py`: PASS) |
| (3) 8.6: DF-μ, DF-μ′, DF-μ″, DF-δz, DF-ξ, DF-ξ′, DF-π′, budget, each with an accepting and a refusing side | yes; every computed value matches 8.6 (the counts of default completions too: 2, 4, 2, 3, 2, 2) | `ZoneExamples.lean` | `lake build VE.Defaults.ZoneExamples` |
| (3) 8.6's `forcedAll` values (DF-μ `[g1 at o1]`, DF-μ′/DF-μ″ `[]`) | computed on the deleted `forcedAllOf` before the cut (`#eval`: `some [soft__excepted__g1 at o1]`, `some []`, `some []`); the guards move to df-5ab | — | — |
| (4) 8.9's seeded bugs: unsaid atoms compared (DF-μ′b), same filling only (DF-π′), the query's cone (DF-μ″), exception atoms only (DF-δz), `zoneForm` always short (DF-δz) | yes, S1-S5 | `mutants.json` | `evidence/mutants.out` |
| (4) "forcedAll read from one default completion" | **no: df-5ab** (moves with `forcedAllOf`) | — | — |
| (4) One mutant per new trusted definition | yes | `mutants.json` T1-T8 | `evidence/mutants.out`, `evidence/T8.out`, `trust-mutants-final.json` |
| Imports and entries only in `lean/VE.lean`, `lean/VE/Audit.lean`; `lean/statements.txt` | yes (Audit and statements through `tools/regen_generated.py`) | — | `uv run python tools/lean_statements.py --check`: PASS, 0 removed, 0 changed |

## Recorded deviations

1. **`valid` on four statements** (`defaultZone_byDefault_sound`, `_leftTo_sound`, `_notSaid_sound`, `forcedAll_sound`).
   Each concludes that a default completion exists, which needs `Structure.Admissible` of `M` over every relation
   name. No computable `defaultZoneOf` can decide that. Counterexample: DF-ξ's model plus one tuple of an undeclared
   predicate. The DRI signed the plan 3.6 wording `(valid : M.Valid (VE.Norms.envAt L.U.D 0))`
   (`manage-agents/reviews/dri-decisions-20261102-df-5a.md`). `hb` was not needed: `zoneMin` evaluates the background
   once and checks the record's true atoms and each enumerated atom against the filled base environment. The four lines
   of `docs/spec/defeasible.md` 7.5 carry the new wording and cite the decision (this restores plan 3.6). The decision
   records it as no user-visible delta.
2. **What `defaultZoneOf` does with values the statements leave free.** `proposed` is not read (`have _ := proposed`):
   every enumerated assignment sets every typed open atom, so no witness needs checking. Where a Kleene value stays
   unknown (an open name at an untyped tuple, which a well-typed premise never reaches), the answer is
   `unknown (branch …)`, never a guess. `noCompletion`'s labels are `["record"]` or `["background"]` when those
   checks fail. Otherwise they are the labels of the checks that refuted the assignments: the premise's own label,
   `fill`, `observed`, `typing`. No theorem constrains the labels. df-5 renders them.
3. **Budget count.** `defaultZone_budget` states `n = (openAtomsAll L M record).length`, so the charge counts the atoms
   before the switches-off record removes any. The enumeration then runs over `zoneAtoms`, which drops those atoms, so
   it is never larger than what was charged. The count is `openAtomsCount`, computed from the sorts' sizes and the
   record's tuples without listing an atom, and `openAtomsCount_eq` proves it equal to that length.
4. **The bounds the charge adds (review F1).** The statements leave these answers free; `zoneMin_error` allows
   `unknown (branch …)`. A record of more than `maxZoneRecord` = 1,024 entries is `unknown (branch [] "record size")`
   before the record is read (the record check is quadratic in its length). A situation with at most
   `maxDefaultAtoms` open atoms but more than `maxZoneRecord + maxDefaultAtoms` typed decision and unsaid atoms is
   `unknown (branch [] "size")`; with domains that list no element twice the record fixes at most one atom per entry,
   so only a repeated element or predicate gets there. Spec 7.5's sentence "`unknown (budget)` when more than
   `maxDefaultAtoms` = 12 open atoms remain" holds for every record within `maxZoneRecord`; a longer record is
   `unknown (branch)` even then, because its exact count is not computed. This follows the review's fix line ("above
   a stated cap answer `.unknown (.branch …)`"). No route reads the zone yet (df-5 adds it), so no user sees it.
   `zoneForm` (spec 7.5's body, word for word) lists the atoms with no charge; `zoneFormOf` is the same form behind
   `zoneCharge` (`zoneFormOf_eq`), the entry df-5's renderer calls. `noExceptionRecord` (word for word) is read only
   by `defaultZone_eq_noException`'s statement and by fixtures; no computation calls it.

## Seeded bugs (Lean, the only product language changed; each planted alone, the named test fails, then restored)

Runner `python3 docs/defeasible/df-1a/evidence/run_mutants.py docs/defeasible/df-5a/mutants.json` (the definitions
with every theorem removed, joined with the fixtures; Prop mutants keep the theorems). Saved run: `evidence/mutants.out`,
control 0 failures, "ALL MUTANTS FAIL THEIR GUARDS". All in `lean/VE/Defaults/Zone.lean`:

| Id | Definition | Bug | Fails |
| --- | --- | --- | --- |
| S1 | `zoneMin` | the filter compares unsaid atoms too | DF-μ′b guard (by default no instead of notSaid) |
| S2 | `zoneMin` | the filter compares only completions with the same filling | DF-π′ guard |
| S3 | `defaultZoneOf` | minimality over the query's cone only (`coneEvalO`'s atoms, {excepted_r2}) | DF-μ″ guard (by default no instead of leftTo) |
| S4 | `zoneMin` | the filter compares exception atoms only | DF-δz guard (leftTo instead of yes) |
| S5 | `zoneForm` | always short | DF-δz guard |
| T1 | `DecLe` | compares the wrong way round | theorem `decLe_iff` |
| T2 | `Observed` | observation negated | theorem `realized_admissible` |
| T3 | `switchesOffRecord` | switches on | DF-ε guard |
| T4 | `DefaultCompletion` | observations dropped | theorem `dc_of_min` |
| T5 | `ByDefaultZ` | value negated | theorem `defaultZone_byDefault_sound` |
| T6 | `ByDefaultLeftTo` | the two completions agree | theorem `defaultZone_leftTo_sound` |
| T7 | `noExceptionRecord` | exceptions set true | DF-ξ guards |
| T8 | `DefaultZone` | constructor `notSaid` dropped | `lake build VE.Defaults.Zone` (`evidence/T8.out`) |
| C1 | `maxDefaultAtoms` | 13 | budget guards |
| C2 | `openAtomsAll` | unsaid atoms left out | DF-μ and 11 more guards |
| C3 | `zoneRow` | a contradicting observation does not refute | DF-μ (o1) and observation guards |
| C4 | `zoneRecordOk` | first-entry check dropped | record guard (one atom both ways) |
| C5 | `zoneDeclOk` | an undeclared predicate counts as declared | record guard (`zzz` held by an invalid model) |
| C6 | `openAtomsCount` | the record ignored | typed-atom bound guard, count-equals-list guards |
| C7 | `tupleMult` | a tuple counted once however often the domains list it | typed-atom bound guard, count guards |
| C8 | `tuplesOutside` | a record tuple named twice subtracted twice | count-equals-list guard |
| C9 | `zoneCharge` | the record's length not charged | record bound guard (1,025 entries) |
| C10 | `zoneCharge` | the typed atoms not charged | typed-atom bound guard (2 × 519 copies) |
| C11 | `zoneFormOf` | the form computed past the charge | budget guard (13 operators), typed-atom bound guard |
| F1 | `zoneCharge` | the open atoms counted by listing them (equal by `openAtomsCount_eq`: only the cost changes) | by hand: the joined file does not finish in 300 s (control 15 s), `evidence/F1.out` |

## Review fixes (round 1: `manage-agents/df-5a-review.final.md`, reviewed f1935bfd9)

- **F1 (B)** -> `zoneCharge` (`Zone.lean`, "The charge"), called first by `zoneMin` and `zoneFormOf`: the record's
  length, the open atoms counted by `openAtomsCount` from the sorts' sizes and the record's tuples (`openAtomsCount_eq`:
  equal to `openAtomsAll`'s length, so `defaultZone_budget` and `budget 26 12` are unchanged) and the typed atoms, each
  against a stated bound before any atom, tuple, switches record or assignment is built. The class, not the example:
  every list the zone builds (`openAtomsAll`, `zoneAtoms`, `switchesOffRecord`, `decisionAtoms`, the record check,
  `zoneForm`'s list) is now built only when its length is within `maxZoneRecord + maxDefaultAtoms` (the switches and
  decision atoms are among the typed atoms counted) or, for the record, `maxZoneRecord`. The sweep: `zoneForm` is
  spec 7.5's body word for word, so the charged entry is `zoneFormOf` (`zoneFormOf_eq`); `noExceptionRecord` is never
  computed outside a statement and fixtures (deviation 4); the record is charged (`maxZoneRecord`, so `zoneRecordOk`'s
  quadratic check reads at most 2,060 entries); "computed once": `zoneAtoms` binds the switches record once (it was
  rebuilt per atom), `zoneMin` and `defaultZoneOf` bind `openNames L` once (it was rebuilt per row), and
  `zoneMin`/`defaultZoneOf` each build the record and the atom list once, after the charge (the module docstring and
  the plan row now say so). The overclaim (the over-limit fixture had 13 operators) is replaced by the review's own
  probe and a 100,000-entity situation. PROBE F1: exit 124 before, `budget 20000000 12` exit 0 in 2.14 s after
  (`evidence/F1.out`). Regression tests: `lean/VE/Defaults/ZoneExamples.lean` "The budget" (`dwide`, the record and
  typed-atom bounds at the limit and one past it, `openAtomsCount` against the list, `zoneFormOf`); seeded bugs C6-C11
  and F1. Commit 4e8075558.
- **F2 (C)**, **F3 (C)**: follow-ups, not changed here (the size decision keeps fix rounds inside their findings).
  F2: witnesses, `differ` and `noCompletion` labels are read by no check (`tag` drops them; `tag` now shows the
  `branch` reason only). F3: the worst in-budget case (eleven or twelve unsaid atoms) runs for minutes; "about 1.3 s"
  in the plan row is the 12-atom fixture's short path, not the worst case.

## Trust

`uv run python tools/trust_map.py --check`: K +0, S +56, G[V] +8 (trusted +64), all in `VE/Defaults/Zone.lean`; PASS
with the R16 allowance (`docs/trust-baseline.json`). Classes in `tools/trust-classes.json`: S for the meaning,
G[V] for `zoneForm`, C for the enumeration (checked by the zone soundness theorems, as nd-atoms' enumeration is C),
P for the proof abbreviations, T for the fixtures. `tools/trust_mutants.py` on the cloud pool:

- First run: `trust-mutants.json`, 70 survivors.
- New fixtures at two elements (DF-ε2, DF-γ's record, DF-δ and DF-δ3's forms), then `trust-mutants-rescored.json`.
- Final run with the allow file: `trust-mutants-final.json` (head 0a62408a1d08): 77 killed, 15 invalid, 45 allowed,
  0 survivor, 0 unknown, exit 0.
- After the F1 fix (full run, no `--rescore`, same allow file): `trust-mutants-f1.json` (head 4e8075558e7e): 77 killed,
  15 invalid, 45 allowed, 0 survivor, 0 unknown, 0 not run, exit 0.

The F1 charge adds no trusted line: `tupleCount`, `tupleMult`, `tuplesOutside`, `zoneGens`, `recTuples`,
`openAtomsCount`, `maxZoneRecord` and `zoneCharge` are C (checked by `openAtomsCount_eq`, `zoneCharge_some` and through
them `zoneMin_error` and `defaultZone_budget`), and `zoneFormOf` is G[V] tied by `zoneFormOf_eq`. `trust_map.py
--check` after the fix: K +0, S +56, G +16 (tied +8), unclassified +0, trusted +64, as before.

The allowances are: the Props, which no check can evaluate (each breaks named proofs); the constructor drops; the
ill-typed `[]` mutants; and one equivalent mutant, `zoneForm`'s `decisionNames.drop 1`, with its argument in the
allow file. The FOLLOW-UPS ties row is in `manage-agents/FOLLOW-UPS.md` "## df-5a".

## Size

Review round 1 (F1) adds about 190 lines to `Zone.lean` (about 50 of definitions and docstrings, about 140 of proofs:
the count's exactness, `zoneCharge_some`, `zoneFormOf_eq`) and about 55 to `ZoneExamples.lean`, all inside F1 and its
sweep, as the size decision's condition asks (no new deliverable).

Measured with `git diff --numstat $(git merge-base HEAD main)`: `Zone.lean` 926, `ZoneExamples.lean` 193,
`tools/trust-classes.json` 63, `docs/spec/defeasible.md` +8/−4, `lean/VE.lean` 2, `ve/assurance-manifest.json` 1, plus
this report and DELTA. That makes about 1,190 hand-written lines, against the ~600-line rule. Of `Zone.lean`, about 195
lines are spec 7.5's definitions and docstrings, and about 730 are the proofs of the seven theorems. The task's fallback
("deliver the zone theorems with their fixtures and name the rest df-5ab") is itself about 1,100 lines, so the whole
`forcedAll` group is cut to df-5ab. Moving the proofs out as well is the only cut that reaches 600. The DRI signed keeping
the item as it is, with the `forcedAll` group as df-5ab and no further growth in this item
(`manage-agents/reviews/dri-decisions-20261102-df-5a-size.md`). The same decision dated the R16 allowance
2026-11-02, the day it was recorded. Generated files (codemap, `Audit.lean`, `lean/*.txt`) and tool
output (`trust-mutants*.json`, `evidence/`) are excluded.

## Tests

- Lean: `lake build` (whole library) builds. `python3 lean/audit.py`: PASS (721 files, 8,004 theorems, only the
  standard axioms). `uv run python tools/lean_statements.py --check`: PASS. `uv run python tools/repo_map.py --check`:
  PASS.
- Generators: `uv run python tools/regen_generated.py --write --skip route-cases`. route-cases needs a Rust release
  binary this worktree lacks, and this item changes none of its inputs. The run also refreshed six stale codemap pages
  of main (tracked files that main's codemap had not caught up with).
- Selected tests: `evidence/selected-tests.txt`. 387 units in six cloud shards plus a fast stage. One failure,
  `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`: `ZoneExamples.lean` parses
  JSON. It is fixed in ba5a8c4c1 (an `other_json` entry), and the failed id rerun passes. Nothing in
  `main-known-red.txt` was hit.

## Spec re-read

Each statement was compared token for token by `compare_statements.py` (`evidence/statements.out`) and re-read
against `docs/spec/defeasible.md` at 174fbb62a:

- the definitions `DecLe` :1028, `Observed` :1031, `switchesOffRecord` :1035, `DefaultCompletion` :1040,
  `ByDefaultZ` :1048, `ByDefaultLeftTo` :1054, `DefaultZone` :1061, `maxDefaultAtoms` :1068, `openAtomsAll` :1070,
  `defaultZoneOf` :1079, `zoneForm` :1182, `noExceptionRecord` :1195;
- the theorems `defaultZone_byDefault_sound` :1113, `_leftTo_sound` :1121, `_notSaid_sound` :1130,
  `_noCompletion_sound` :1140, `defaultZone_budget` :1188, `decisionAtoms_none` :1201, `defaultZone_eq_noException`
  :1205.

The zone semantics were re-read against 3.8 :204-231 and plan 2.7 :260-287: minimality over decision atoms only, with
unsaid tables varied; leftTo only with the same filling; the enumeration never over the cone.

## Pilot bytes

0 (plan: none in bytes; df-5a is Lean only, with no route).

## Next items

- df-5: the kind `defaults-zone`, the English (DE10, DE10f, DE11, DE13) chosen by `zoneForm` through `zoneFormOf`, the relay in
  `ve/defaults.py` and the route cases. It discharges `valid` through `LayeredU.sitValid`.
- df-5ab: `forcedAllOf`, `forcedAll_sound`, `defaultCompletion_below`, `forced_everywhere`, the DF-μ/DF-μ′/DF-μ″
  `forcedAll` guards and the seeded bug "forcedAll read from one default completion".

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A. (no relayed answer; df-5 adds the kind and its schema).
2. Every deliverable built: PASS (the plan rows table above; cuts to df-5ab follow the task's fallback; the grep for the
   six names is empty; no Python copy, no permanent report test).
3. Tests can fail: PASS (`evidence/mutants.out`, every mutant fails its guard or theorem; `trust-mutants-final.json`
   exit 0).
4. Python/Lean/Rust agree: N.A. (Lean only; no Python or Rust path computes a zone).
5. R8 binding: N.A. (no relay in this item).
6. Gate evidence on the final HEAD: N.A. here (the chain runs the gate on the final HEAD; `evidence/selected-tests.txt`
   records the selected run).
7. No unsigned item: PASS (DELTA T1 cites R16 with its conditions; the `valid` change is SIGNED in
   `reviews/dri-decisions-20261102-df-5a.md`; the size overrun is SIGNED in `reviews/dri-decisions-20261102-df-5a-size.md`).
8. Every user-visible change in DELTA: PASS (no route, schema or answer changes: DELTA.md; bytes 0).
9. Test selection: PASS (the selection picked 387 of 526 units and included `tests/test_assurance_manifest.py`, which
   caught the unclassified JSON file).
10. Statements say what is claimed: PASS (`evidence/statements.out`; T1/T2/T4-T6 break the named proofs; the added
    hypothesis is DRI-signed with its counterexample).
11. Budgets fail closed: PASS after review round 1 (the first build's PASS was wrong: F1). `zoneCharge` charges the
    record, the open atoms and the typed atoms before listing any; the guards cover 20,000,000 and 2 × 10^11 open atoms
    and each bound at the limit and one past it; theorem `defaultZone_budget` keeps the exact count; an unknown Kleene
    value gives `unknown (branch)`, never false.
12. No CPU or memory regression: PASS for routes (no route reads the file). Within the budget the cost is F3's open
    follow-up: the 12-atom fixture's 1.3 s is a short path, not the worst in-budget case.
13. Test-removed trailers: N.A. (no test removed or renamed).
14. Both directions, cited evidence, spec re-read: PASS (each 8.6 guard has an accepting and a refusing side; the
    record, observation and typing checks are guarded both ways; "Spec re-read" above).
