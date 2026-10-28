No DRI signature is reserved: DELTA has no row and trust is +0. me-12nb builds spec 12.2's draft 5 charge in
`lean/VE/Arith/Bounded.lean`, re-proves `decideBounded_sound`, `_work`, `_mono`, `_complete` and `_covered`, proves
`Term.evalB_bits` and the three bit-length bounds, and pins 13.3's counts. N1's pin is flipped, and the chains B-2 to B-4
are UNKNOWN at 1,000,000 units within seconds. Open: definition-name lookup reaches UNKNOWN only after 37 s
(interpreted; 2.5 to 2.9 s compiled), so the DRI queued **me-12nc** before me-12b (`reviews/dri-decisions-20261027-me-12nb.md`).

# me-12nb report: the `arith@0` budget that charges term nodes, calls and value sizes

Base `d9cff5345` (`git merge-base HEAD main`); commits `git log --oneline --no-merges main..HEAD`. Lean is the only
product language changed. There is no Python, Rust, wire, mode, `Protocol.lean`, Registry or `ve/` change (me-12b).

**Statement gate.** me-12n's review (manage-agents `me-12n-review.final.md`, the ME-S re-check of 12.2 and 13.3) ended
MERGE with no A or B finding. A scratch script cuts each declaration of 12.2's code block at its `:=` and collapses
whitespace: every definition (`bits`, `charge`, `chargeBits`, `stepB`, the loops, `OpEnv`, the three evaluators,
`Defs.opEnv`, `maxSteps`, `decideBounded`, `arithOutcome`) and every theorem (`decideBounded_sound`, `_mono`, `_work`,
`_complete`, `Term.evalB_bits`, `bits_add_le`, `bits_sub_le`, `bits_mul_le` and `arithOutcome`'s three) equals
`Bounded.lean`. `decideBounded_covered` keeps me-12ab's text. `lean_statements.py --check`: 0 added, 0 removed, 0 changed.

## Delivered (task order)

| Task row | Delivered | Proof or test |
|---|---|---|
| (1) the new `charge`: term-node visits, calls, the size charge of `add`/`sub`/`mul` | `bits`, `chargeBits`, `stepB` and `Term.evalB` as 12.2 states them (every term clause starts with `charge` and ends in `chargeBits`; each range step charges its value) | `BoundedExamples.lean:15-24` (`0 = 0` = 5 units; `bits`, `chargeBits` and `stepB` under, at and over each boundary), `:27-29` (`prime 7` = 85, empty count = 9, `pos 3` = 10) |
| (2) `decideBounded_sound`, `_work`, `_mono`, `_complete` re-proved | yes, with `_covered`: `chargeBits_some`/`_eq`/`_mono` and `stepB_some`/`_sound`/`_mono`/`_total` carry each clause; the term work bound comes from `Term.evalB_bits`; `Total`'s W gains the bits | `lake build`, `lean/audit.py` PASS; `CompleteExamples.lean:19-25` (W − 1, W, W + 1 and the sweeps) |
| (3) the size bound (a theorem, as me-12n states it) | `Term.evalB_bits`, `bits_add_le`, `bits_sub_le`, `bits_mul_le`, proved without `sorry` (the DRI's condition) | `lean/axioms.txt`; S1, S3 and S11 break `Term.evalB_bits`, S8 breaks the bounds |
| (4) the N1 pin flipped; N1's and F1's chains UNKNOWN at 1,000,000 within seconds; 13.3's counts as guards | B-1 (`1024 = f10`) unknown at 1, 1,000 and 12,272, holds at 12,273 and 12,274 (`:148`); B-2 (`:150`), B-2p (`:152`), B-3 at 31 levels (`:158`) and B-4 (`:160`) unknown at `maxSteps`; M-1 337,735, M-2 7,420, M-5 33, M-4 holds through 87 and is unknown at 88 (`:68`), M-4b's bounds 87, 88, 89, 91 | `BoundedExamples.lean`; times below |
| (5) seeded bugs from me-12n's plan, plus one mutant per new trusted definition | 12 hand mutants, all KILLED ([`mutants.json`](mutants.json)) | below |
| DRI (me-12n item 1): restate the old units outside 12.2 | 12.5's `budget` and `units`, 13.4's M-1b rows (337,734 and 337,735), 13.6's R-7 (337,735 and 33), section 14's `arith` row, section 16's C6; plan D19, 2.13, 3.9, 4.3's M-4 reference (87) and ME-12 (me-12n review F1) | `docs/spec/math-evidence.md`, `docs/spec/math-evidence-PLAN.md` |
| me-12n review F2: `BoundedExamples.lean:136`'s `false 2` | now `false 33` (`:167`) | the `example` builds |
| me-12aa review F3: M-2 and `big 3` one unit over their boundaries | `:40` (7,419 / 7,420 / 7,421), `:122` (22 / 23 / 24) | — |

`CompleteExamples.lean` also carried draft-4 counts (not in me-12n's file list). Its sweeps, its `keeps` ranges and its
`tickEnv` counterexample are recomputed (`tickEnv` now compares with 20, because `5` no longer fits a budget of 5).

## Times (interpreted, `lake env lean` on the VM, beyond the 0.85 s load)

| Fixture | Draft 4 (me-12aa, me-12n) | This build |
|---|---|---|
| B-1, N1's pin at budget 1,000 | (true, 1) at budget 1 | under 0.1 s, unknown |
| B-2, `0 < f24` | 55.8 s, 1 unit | 1.4 s, unknown |
| B-2p, `0 < f24(1)` | — | 1.5 s, unknown |
| B-3, `0 < g31` | 40 s, 1.8 GB, 1 unit | under 0.1 s, unknown |
| B-4, reused 65,537-bit value | 107 s, holds in 999,001 | under 0.1 s, unknown |
| M-1 at `maxSteps` | — | 0.2 s, (true, 337,735) |
| M-4 `N = 200` at 10,000,000 | — | 6.2 s, (true, 9,694,873) |
| `BoundedExamples.lean` whole | — | 53 s (the stub: 50 s) |

**The uncharged costs** (DRI's me-12n item 1 asked me-12nb to record them; [`uncharged-costs.lean`](uncharged-costs.lean)):
- reading the last of 4,000 parameters twice per count step: 1.3 s to UNKNOWN;
- a range up to a 65,537-bit bound (its countdown is uncharged): under 0.3 s;
- **definition-name lookup: 37 s to UNKNOWN** (guard 3: 511 definitions with 64-byte names that differ only at the
  end, and a 512th whose body is a product tree of 1,024 calls of the first, about 6 units per call; each lookup walks
  511 closures with a full-name compare).

Compiled (a temporary `lean_exe` whose root imports only `VE.Arith.Bounded`, reverted after the run; three runs
each on the VM): parameter read 0.8 s, countdown 0.05 s, **name lookup 2.5 to 2.9 s**, B-2 0.05 s.

The DRI decided (`dri-decisions-20261027-me-12nb.md`): the charge does not change. The fix is **me-12nc**, a
name-to-definition table built once per case, proved to return what the list lookup returns, with no unit count
changed, queued before me-12b. After me-12nc, guard 3 must reach UNKNOWN within 2 s compiled. Spec 12.2's "Time" bullet
now states these measurements and names me-12nc.

## Seeded bugs and mutants (Lean; [`mutants.json`](mutants.json))

All are in `lean/VE/Arith/Bounded.lean`. Each was planted alone, in a copy joined with both fixture modules. One
`lake env lean` run lists the broken proofs and the failing guards; the control has no error. **12 of 12 are KILLED.**

| Id | Definition | Bug | Proofs broken; guards failing (`BoundedExamples.lean` unless named) |
|---|---|---|---|
| S1 | `Term.evalB` | a variable yields without `chargeBits` | `Term.evalB_bits`, `_sound`, `_mono`, `_total`; `:27`, `:33`, 26 more |
| S2 | `stepB` | a step does not charge its value | `stepB_some`, `_mono`, `_total`; `:24`, `:33`, `:49`, 16 more |
| S3 | `Term.evalB` | `mul` charged without its size | `Term.evalB_bits`, `_sound`, `_mono`, `_total`; `:33`, `:154-156`, 16 more |
| S4 | `chargeBits` | refused only when `limit < w` | `chargeBits_some`, `stepB_some`; `:15`, `:22`, `:148`, 14 more |
| S5 | `Term.evalB` | a function call costs no visit | `Term.evalB_sound`, `_mono`, `_total`; `:116`, `:148`, 15 more |
| S6 | `Term.evalB` | a term node charged 0 (a literal) | `Term.evalB_sound`, `_mono`, `_total`; `:15`, 36 more |
| S7 | `Term.evalB` | a call charged without its body | `Term.evalB_total`; `:73`, `:148`, `:150`, `:152`, 15 more |
| S8 | `bits` | one bit short (0 for 0 and 1) | `bits_add_le`, `bits_mul_le`; `:21`, 39 more |
| S9 | `chargeBits` | refused at the budget, not past it | `chargeBits_eq`, `stepB_mono`; `:22`, `:148`, 15 more |
| S10 | `stepB` | the condition sees the units before the charge | `stepB_some`, `_mono`, `_total`; `:24`, 18 more |
| S11 | `Term.evalB` | a count's result uncharged | `Term.evalB_bits`, `_sound`, `_mono`, `_total`; `:28`, 7 more |
| S12 | `Term.evalB`, `stepB` | draft 4's evaluator (N1's) | 7 proofs; `:148`, `:150`, `:152`, `:158`, `:160`, 39 more |

S1 to S5 are me-12n's build plan. S6, S7 and S3 are the task's three. S8 (`bits`), S4 and S9 (`chargeBits`), and S2 and
S10 (`stepB`) are the mutants per new definition. S12 shows that the UNKNOWN guards of B-2 to B-4 can fail.
`mac-pytest.sh --trustmut -- --jobs 6 --max-mutants 1000` ran on ve-mac-1 ([`trust-mutants.json`](trust-mutants.json)):
0 definitions, 0 mutants, exit 0. The new definitions are C, not trusted.

## Trust, tests, size and overlap

- **Trust.** `uv run python tools/trust_map.py --check`: K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0,
  PASS. `bits`, `chargeBits` and `stepB` are C (`tools/trust-classes.json`), as the evaluator is; the four new fixture
  definitions are T. There is no allowance, no R16 row and no FOLLOW-UPS row.
- **Tests.** `mac-pytest.sh --select -- --base d9cff5345 --run`, tree of 5f75f9893 (later commits: spec prose and this
  report): 87 of 474 units, 0 failed, exit 0, on the VM (no Mac slot; 7,164 s); the last commit's 7 units
  (`--base 5f75f9893`) also pass. Fix round 1 adds `tests/test_arith_uncharged_costs.py` (below).
- **Checks.** `lake build` (1,121 jobs), `lean/audit.py` (7,210 theorems), `lean_statements.py --check`,
  `repo_map.py --check`, `frozen.py` and `trust_map.py --check` pass. `regen_generated.py --write --skip route-cases`
  wrote 32 entries (`route-cases` needs the Rust release binary; no route changed). `gate_collection.py --check
  --prebuilt`: 0 added, removed, refused, stale or malformed. The full gate is the chain's, on the final HEAD.
- **Size.** 598 hand-written lines added or changed (`git diff --numstat` from the base; generated files excluded):
  `Bounded.lean` 235, `BoundedExamples.lean` 92, `CompleteExamples.lean` 14, `ARITH.md` 14, spec 24, plan 7, trust table
  8, evidence 62 (`uncharged-costs.lean`, `mutants.json`, DELTA) and this report 142. Nothing is cut.
- **Overlap.** No in-flight branch touches `lean/VE/Arith/` or `lean/ARITH.md`. `lean/VE/Audit.lean` (generated) and
  `tools/trust-classes.json` (union) are shared with ap-2b, ap-3c, df-2b, qt-a3b, me-1 and arch-AR-1; the stale
  `foundation/me-1` also touches the spec and plan.
- **Bytes.** 0 expected (use-case ceiling, ME-P4); nothing is claimed before a pilot audit.

## Fix round 1 (`me-12nb-review.final.md`)

- **F1 (B): the condition's fixtures were run by nothing.** `uncharged-costs.lean` is outside Lake's targets, so the
  DRI's "must stay selected" guards ran only by hand. `tests/test_arith_uncharged_costs.py` now runs the file with
  `lake env lean` (so every Lean change selects it, as `lake`/`lean` runners are, and an edit of the file selects it,
  as it names the file), checks that each of the four guards is still there (the three UNKNOWN at `maxSteps`, the count
  6,147), and shows the run can fail: a copy with the count off by one is refused. Seeded bug: `tree 10` → `tree 9`
  in `dense` fails `test_lean_accepts_every_guard` (`:22`); restored. About 50 s on the VM, interpreted.
- **Sweep.** The other `#guard` files under `docs/` are spec scratch stubs, not fixtures a decision keeps:
  `me-12n-budget-stub.lean` and `SpecStubs_pk1.lean` (type-checked against main when written) and
  `SpecStubs_sc5r.lean` (`tests/test_scope_sc5r_stub.py` reads it). Inside `lean/`, `BoundedExamples.lean` and
  `CompleteExamples.lean` are imported by `lean/VE.lean`.

## Next items

- **me-12nc** (DRI, before me-12b): the definition-name table described above, under R16. Its fixture is guard 3 of
  `uncharged-costs.lean`, which must reach UNKNOWN within 2 s compiled with its unit count unchanged.
- **me-12ac**: spec 12.5's `decidingValue` and M-6 (me-12ab's plan).
- **me-12b** (protocol queue after AP-4): the wire, the runner, the rows and the mode. It writes R-7's units 337,735
  and 33. me-12n's review F3 asks it to size `arith`'s `DEADLINES` row for a whole case (512 statements × 1,000,000
  units), or to add a total per case.

## Sibling lessons (me-12n review)

F1: every passage it and its sweep name is restated (`grep formula-node` finds only draft-4 history). F2: done, with
`CompleteExamples.lean`'s counts. F3 (no total per case): me-12b's, named above.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; no mode or schema (me-12b).
2. PASS: each task row is in the table above with its proof or guard. `git diff main...HEAD` adds no Python copy of
   a Lean decision and no report test. The shared registries are listed under Overlap.
3. PASS: 12 hand mutants, each KILLED by named proofs and guards (`mutants.json`), control clean; `trust_mutants`
   exits 0 with 0 definitions (`trust-mutants.json`).
4. N.A.: `arith@0` has no Python or Rust counterpart.
5. N.A.: no relayed field to bind.
6. PASS: base from `git merge-base`, commits from `main..HEAD --no-merges`; the chain gates the final HEAD.
7. PASS: DELTA has no row; trust +0 (`trust_map.py --check`); no allowance and no signature.
8. PASS: DELTA "Public output: none": no mode, command, route, or Python or Rust product file.
9. PASS: the selection ran 87 of 474 units, not every unit. Its plan runs `lake build`, which checks every guard that
   S1 to S12 break.
10. PASS: the statements equal spec 12.2 after whitespace normalisation (`lean_statements.py --check`); S1, S3, S4, S8
    and S11 break `Term.evalB_bits`, `chargeBits_some` and the bit-length bounds.
11. PASS: budget 0 is UNKNOWN (`BoundedExamples.lean:15-17`); every boundary is tested under, at and over (`:15`, `:22`,
    `:24`, `:33`, `:40`, `:49`, `:68`, `:122`, `:148`, `:156`).
12. PASS: B-2, B-2p, B-3 and B-4 are step-count fixtures for the CPU and memory class (UNKNOWN at 1,000,000;
    `:150-160`), and S7 and S12 show they fail when the charge is weakened. The name-lookup class is me-12nc's.
13. PASS: no test was removed. `gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and 0 malformed.
