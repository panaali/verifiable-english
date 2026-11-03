# me-8 report: consistency of printed numbers (ME-8)

- **Status:** ready for review after the fix of the review's F1 (a B: the limit did not bound the run). Evidence HEAD `61c128228` (trust mutants, the fix's selected tests; seeded bugs at `570c73cfd`, the same Lean but for one comment); later commits change only `docs/math-evidence/me-8/`.
- **What changed:** spec 8.1 in Lean: interval enclosures (`Interval.lean`), the one `Consistent` with its witness and both refutations, the granularity theorems and GRIM (`Consistency.lean`), a charged runner, fixtures as `#guard`s and a relaying test.
- **Open:** me-8b (the `consistent` wire form and its rows, R-5 and R-10b as complete requests, the sign-flip arm of `refuteByGrain` once me-7b adds `.stat`, the runner's node limit in the spec's limit table). The review's C items F2 to F5 are not fixed here; F6 is.
- **Signatures:** none reserved. DELTA row 2 is SIGNED by the DRI (reviews/dri-decisions-20261102-me-8.md item 1); trust S +8, K +0 under R16 (row 1).

Base `287d5dc60`; commits `git log --oneline --no-merges main..HEAD` (`eb7fd36a5` to `7e6733b8c`, then this report). Lean is the only product
language changed (`tests/test_calc_consistency.py` is test code). Plan: `docs/spec/math-evidence-PLAN.md` at `ed5d863fe`,
"ME-8" and 3.7; spec `docs/spec/math-evidence.md` 8.1, 13.2-13.6 (main's 8.1 and 2.7 equal `ed5d863fe`'s: `diff` of the sections empty).
Synthesis-2 edit 4 (budgets) holds for the runner: its limits are Lean work units (`Work.maxWork`, 3.2's unit) and
`maxWitnessPoints`, separate from the Rust 5 s wall limit and `VE.SearchBudget`.

**Statement gate.** ME-S passed (manage-agents math-evidence-p3ver2.final.md). Spec 8.1's 15 declarations appear verbatim,
whitespace and comments normalised (`python3 docs/math-evidence/me-8/evidence/check_statements.py`: "15 of 15", saved in
`evidence/check_statements.txt`; one changed character makes it exit 1, tried). `tools/lean_statements.py --check`: "PASS:
7656 statements ... unchanged" after the dump (0 removed, 0 changed). The one definition whose spec body cannot be written,
`refuteByGrain`, was asked and SIGNED (below).

## Plan rows and task deliverables

| Plan row or task line | Delivered | Where |
|---|---|---|
| New files `Interval.lean`, `Consistency.lean`, `tests/test_calc_consistency.py` | yes | `eb7fd36a5`, `e19affef8`, `981a414bc` |
| (1) enclosures over the lowering with the inputs kept (J4), each operation's enclosure proved | yes | `Printed.box_sound`, `Interval.mul_sound`, `inv_sound`, `pow_sound`, `enclose_sound`; `encloseC` charged, `encloseC_some` |
| (2) `Consistent`, the witness and both refutations against it, over one lowering | yes | `consistent_of_witness`, `inconsistent_of_refutation`, `refuteByEnclosure_sound`, `refuteByGrain_sound` |
| `mean_grain_refutes`; `signFlipP_grain` used as a granularity check | yes, as library theorems | `grain_sound`, `signFlip_grain_refutes` (reads `signFlipP_grain`), `mean_grain_refutes` |
| Granularity on the route (`refuteByGrain`'s `.stat .signFlip` arm) | **no: me-8b** (DRI item 1) | `Expr` has no `.stat` (me-7b); `refuteByGrain` is `false`, so its disjunct is vacuous until then |
| Evaluator rule (DRI 2026-10-27): each value read once, its size charged against a stated limit, a large well-formed request within it and the deadline | yes, at `maxWork` | `consistencyRun`: one `inlineTable`; the outputs' trees at most 10,000 nodes together (`outputNodes`) before either phase; `encloseC` one unit a visit plus each endpoint's size, each endpoint held to the digit limit (`chargeI`, `encloseC_small`); each pass (the enclosures and each point) charged by input and node (`passWork`); each point built when tried, its values once into a table (`valueTableC`), sides by `Expr.evalsC`; none past `limit`. Native times at `maxWork`: at most 26 s over eleven shapes, against 170 s and about 16 minutes before the fix (`evidence/limit-times.txt`) |
| (3) V-7, V-8 (granularity, tie rule) | yes | `:136-142`, `v8_tiesUp` (`:145`); 0.007812 refuted under ties up only |
| V-7b (six p values over 2¹²) | yes | `:138`, `:141`: multiples 1,888, 3,586, 4, 8, 896, 4,068; none refuted under either rule |
| V-6 from the printed per-template values (a witness) | yes | `:62`: the twelve printed values witness SD 0.108, SE 0.031, half-width 0.081 by squared bounds; V-6r refuted (`:64`) |
| C-1 and R-5: a stated value left out of the inputs, a witness at an endpoint, a free value refused | yes, in Lean | `:26-38`: k1 fails with enclosure [13/20, 3/4], k2 holds at a = 7/20, k3 `ConsistencyName: f` (also through a definition), `ConsistencyInput` for a free or twice-named input |
| GRIM as a `#guard` of `mean_grain_refutes` (S-3) | yes | `:149` (3.47 refuted, 3.40 and 3.4 not), `grim_347` (`:151`) |
| (4) R-10b (unknown and undefined) | in Lean only; the wire request is **me-8b** | `:40-41` over counted values (exhausted: "the budget of 6 evaluation steps ran out"; none: undefined). The request needs the `consistent` wire form, not built here |
| (5) the test relays Lean's answers, no Python copy of a check | yes | 21 fixtures compared with the spec's hand answers, and two service tests (DELTA) |
| Seeded bug: `sub` as [lo − lo, hi − hi] refutes V-6 | planted; **V-6 does not catch it** | S1 below: the bug's interval still brackets V-6's values; the complement fixture (`:33-34`) catches it |
| DELTA: new checks only; an existing request answers as before | yes | DELTA.md |

## Seeded bugs (Lean)

Each planted alone, built (`lake build VE.Calc.ConsistencyExamples`), restored (`evidence/seed.py`, rerun for S1 to S18 after the fix); `mutants.json` has the commands and lines.

| # | File, definition | Bug | Fails |
|---|---|---|---|
| S1 | `Interval.lean`, `Interval.sub` | [lo − lo, hi − hi] (plan's; `enclose_sound` cut to `sorry`) | `ConsistencyExamples.lean:33`, `:34` (`complement`) |
| S2 | `Interval.lean`, `Printed.box` | ties' upper end (2D + 3)/2u | `:27`, `:29`, `:31`, `:33`, `:121` (`r5-k1`) |
| S3 | `Consistency.lean`, `endpointPoint` | always the upper endpoint | `:30` (`r5-k2`) |
| S4 | `Consistency.lean`, `refuteC` | the output index not advanced | `:31` (`r5-order`) |
| S5 | `Interval.lean`, `chargeI` | endpoints' sizes not charged | `:75` (`chain-short`) |
| S6 | `Consistency.lean`, `grainRefutes` | half to even whatever the rule (`grain_sound` cut) | `:136`, `:146` (`v7-ties-up`) |
| S7 | `Consistency.lean`, `freeReadTable` | definitions not followed | `:36` (`c1-through-definition`) |
| S8 | `Consistency.lean`, `consistencyInputFault` | a twice-named input accepted (its lemma cut) | `:38` (`input-twice`) |
| S9 | `Consistency.lean`, `pointHoldsC` | a point's pass not charged | `:75`, `:79` (`chain-short`, `search-short`) |
| S10 | `Interval.lean`, `chargeI` | no digit hold (`chargeI_some` cut) | `:113`, `:115`, `:121`, `:123`, `:126`, `:128` (`hold-past-limit`) |
| S11 | `Interval.lean`, `chargeI` | the hold reads only the lower endpoint (`chargeI_some` cut) | `:121` (`hold-either-endpoint`) |
| S12 | `Interval.lean`, `chargeI` | the hold reads only the upper endpoint (`chargeI_some` cut) | `:121` (`hold-either-endpoint`) |
| S13 | `Consistency.lean`, `outputNodes` | no node limit (the two chain guards at `maxWork` dropped: under this bug they run past any timeout) | `:75`, `:88`, `:90`, `:91`, `:93` (`nodes-past-limit`) |
| S14 | `Consistency.lean`, `outputNodes` | the limit per expression, not together | `:75`, `:88`, `:90`, `:91`, `:93` (`nodes-together`) |
| S15 | `Consistency.lean`, `consistencyRun` | past the node limit answers `fails` | `consistencyRun_fails` does not compile (`Consistency.lean:547`) |
| S16 | `Consistency.lean`, `passWork` | a node charged 1 unit | `:75`, `:97` (`chain-short`) |
| S17 | `Consistency.lean`, `passWork` | a lookup step charged 1 unit | `:75`, `:97` (`chain-short`) |
| S18 | `Consistency.lean`, `consistencyRun` | the enclosure pass not charged | `:75` (`chain-short`) |

**Trust mutants** (`mac-pytest.sh --trustmut -- --max-mutants 1000 --allow ... --json docs/math-evidence/me-8/trust-mutants.json`,
exit 0, a full run at `61c128228`): 15 mutants of the two new trusted definitions, 15 ALLOWED: `InBox`'s body-true and body-false fail the guards at
`:23-24` but are UNKNOWN by instance drift (as me-7's `SqrtRoundsTo`); `Consistent`'s 13 break `consistent_of_witness` and
`inconsistent_of_refutation` (undecidable, as me-9b's `IsIdentity`). The first run (before `InBox`'s instance) had 14
SURVIVOR and 1 UNKNOWN. `refuteByGrain`'s mutant `true` fails `refuteByGrain_sound` (killed, DRI item 1).

## Tests

- `uv run pytest -q tests/test_calc_consistency.py`: 40 passed.
- Selected tests on the finished code: 102 of 531 units planned, 110 run units in 6 shards, exit 0, 0 failed, at
  `bd6cd04ee`; then for the fix (`--base bd6cd04ee`): 101 units planned, 109 run, exit 0, 0 failed
  (`evidence/selected-tests.txt`); then for F1's fix (`--base $(git merge-base HEAD main)`, at `36c1db95b`): 102 of 531
  units planned, 110 run in 5 shards, exit 0, 0 failed. Nothing from `main-known-red.txt` was hit.
- `lake build` (1,244 jobs) and `python3 lean/audit.py` ("PASS: 737 source files"), after the last Lean change.
- `uv run python tools/regen_generated.py --check`: "checked 35 entries". `tools/gate_collection.py --check --prebuilt`:
  24 added, 0 refused, 0 stale, 0 malformed. The full gate: not run here (the chain runs it).

## Trust, size, bytes

- `uv run python tools/trust_map.py --check`: K +0, S +8, untied V +0; PASS with the R16 allowance (DELTA row 1).
- Size (`git diff --numstat $(git merge-base HEAD main)`, generated files excluded): Lean 1,014 (`Consistency.lean` 560,
  of which about 300 are proofs; `Interval.lean` 299, about 165 proofs; `ConsistencyExamples.lean` 155), test 158,
  `tools/trust-classes.json` 93, statement check 28, seeded-bug runner and bench 154, baseline and import 8, DELTA and
  this report about 125: about 1,570, more than twice the ~600 guide (`mutants.json`, the allow file and the trust-mutant JSON are evidence data). Measured
  before the second half at 782 (Lean only); I kept the runner rather than cut it, since spec 8.1's search and limits
  and R-5's behaviours live there and it was already proved. No Mathlib: each interval bound is proved by hand.
- Pilot bytes expected: 0 (plan "Bytes: 0"). Nothing is claimed.

## Deviations

- `enclose` (an opaque definition) is a `match` on `e` under the spec's signature; `refuteByGrain` is `false` (SIGNED).
- The plan's seeded bug does not refute V-6 with any of three variance forms tried: its [lo_a − lo_b, hi_a − hi_b]
  still brackets V-6's value at every claim. The fixture that catches it is a share's complement 1 − a ≥ 0.56.
- **F1 (review of `98c053ba2`).** The limit did not bound the run: enclosure endpoints grew without a hold, and trees
  were walked at every point with no node limit. Now the outputs' trees are held to `maxPolyTerms` nodes together, not
  per expression as `Identity` holds a side, because a case may have 512 outputs (about 10 million visits a point
  otherwise). Past it the answer is `consistencyInconclusive`, the kind's own reason in the spec's list and true: neither
  phase ran. A refutation another output would have given is then not looked for; that is UNKNOWN, never a verdict.
  The limit is not in the spec's limit table: me-8b adds it with the wire form.
- **Refusals the charge adds.** `passWork` charges 8 units a lookup step and 512 a node, calibrated as `entryUnits` is
  (spec 3.2), so a search with no witness over many inputs or nodes can reach limit 10 before its 4,096 points: 512
  inputs reach it at the last point, and 12 inputs over 10,000 nodes after about 1,400 points. Both fail closed; a
  witness found earlier is unaffected (V-6, with 648 nodes, would afford all 4,096).
- `limit_bench.lean` is run by hand as a temporary `lean_exe`; it is not a test and no time is asserted. Its figures are
  one serial run on the VM. A tree 9,999 levels deep runs natively; the interpreter's stack ends near 2,200 levels, so
  the fixtures use a balanced tree. me-8b should check the depth on the service's own stack.
- Self-review (after the first selected run) found the search holding up to 4,096 points of n values at once and doing
  n lookups per point uncharged; `7e6733b8c` builds each point when tried and charges n × n units first (S9; `passWork` now holds that charge).
- The decoder-side checks (`consistencyInputFault`, `freeReadTable`, `consistencyNameFault`) run once per check by
  lookup, uncharged, like calc@0's decoder and `inlineTable`; they move into the wire's decoder with me-8b.
- `consistencyRun` returns none past its limit; the wire (me-8b) maps it to limit 10 (`Wire.workLimit`), as calc@0 does.
  A refusal is structured (`ConsistencyRefusal`); 13.1's texts come with the wire.

## Spec re-read

`InBox`, `Consistent`, `witnessCheck`, `enclose`, `refuteByEnclosure`, `refuteByGrain`, the five theorems, `grainRefutes`,
`grain_sound`, `signFlip_grain_refutes`, `mean_grain_refutes` against `docs/spec/math-evidence.md:1798-1855` (main); the name
and input rules against `:793-795`; the outcomes, the order (printed values, then endpoints) and the 4,096 points against
`:1790-1794` and `:3377`; C-1 against `:2878`, `:2955`; R-5 against `:3145-3166`; R-10b against `:3310-3331`; V-6, V-7,
V-7b, V-8 against `:2908-2912`; S-3 against `:2952`.

## Next item

ME-P3 (the math paper's statistics pilot), then me-8b after me-7b.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: N.A., no relayed answer (no mode, schema or relay changes; the service tests read existing rows).
2. Deliverables: PASS, plan rows above with commits and guards; the moved rows by DRI item 1 and the size cut (me-8b).
3. Tests can fail: PASS, S1-S18 each fail a named guard or proof (`mutants.json`); trust mutants exit 0 (`trust-mutants.json`).
4. Python, Lean, Rust agree: N.A., Lean only; `test_an_existing_request_answers_as_before` shows the wire unchanged.
5. R8 binding: N.A., no field read from a Lean answer by product code; input refusals tested (`input-free`, `input-twice`).
6. Gate evidence: PASS, selected tests at `bd6cd04ee` and for the fix at `7e6733b8c`, base from `git merge-base`; the gate runs on the final HEAD.
7. Unsigned items: PASS, DELTA rows cite R16 and the DRI's signature (decision file named).
8. DELTA: PASS, public output none (`test_a_consistency_claim_is_not_on_the_wire_yet`, `..._answers_as_before`).
9. Selection: PASS, 102 of 531 units, `test_calc_consistency.py` among them (`evidence/selected-tests.txt`).
10. Statements: PASS, `check_statements.py` 15 of 15 (fails on a changed character); `lean_statements.py --check` PASS.
11. Budgets fail closed: PASS, `limit-zero` (no units: none), `chain-short`, `search-short`, `witness-points`, `nodes-past-limit`, `hold-a12-no-enclosure` (UNKNOWN or the refusal, never false).
12. CPU and memory: PASS, measured at the runner's limit, not at 1,000,000 units: `add-chain-max-work` and `mul-chain-max-work` (the review's two chains), the hold (`encloseC_small`, `hold-*`), the node limit (`nodes-*`), the charge pinned in units (`chain-at-work`, `chain-short`), and at most 26 s natively over eleven shapes at `maxWork` (`evidence/limit-times.txt`); points are built one at a time (`7e6733b8c`, S9).
13. Removed tests: N.A., none removed (`gate_collection.py --check --prebuilt`: 0 refused, 0 stale).
14. Both directions: PASS, each refusal and verdict has its opposite (`r5-k1`/`r5-k2`, `input-free`/`r5-k2`, `v7-ties-up`/`v7-half-even`, `s3`, the InBox guards `:23-24`).
