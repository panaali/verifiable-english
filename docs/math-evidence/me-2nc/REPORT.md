# me-2nc: `calc@0`'s derivations, first part: the charged lowering and the one-pass steps (spec 3.2 (b))

**Status:** built, cut at the decoder; ready for the chain's gate. **HEAD:** the commit that adds this report (branch `feature/me-2nc`).
**What changed:** deliverables (1) and (2): each side lowered once on the case's count, limit 10 in the decoder (P-2 at 73, N-1 at 122 refused in about 1.5 s; S-1 to S-10 keep 5's linearity); `normOnce`, `isConstOnce`, `pickOnce`, `checkOnce` proved equal to 5's.
**Open:** me-2ncb has (3) and the rest of (4): the runner reading the lowering, the search charged and held to the digit limit, DELTA C1, C2 and K-1's part of C3. **Not reached here:** L-2 to L-4, P-1's rows and K-1 behave as today.
**DRI signature needed:** none (C3 item 3; C5 R2; C4 R16).

## Why the cut, and where

The size rule is about 600 lines and says to cut rather than grow. Lower.lean alone is +554, and deliverables (1) and
(2) with their proofs are +1,283 −17 of Lean. Going on to (3) would have put the item past 2,000. So I stopped at the
first coherent part: the decoder is complete and tested, and nothing in the runner changed. The design that (3) needs
is below, so me-2ncb need not rediscover it.

The consequence is a partial answer to the item's "Why". N-1 and P-2's decoder cost are fixed. **L-2 to L-4, P-1's
rows and K-1 are not: they still run as on main, and L-4 still passes the deadline.** `lean/VE/Calc/Wire.lean:39`
("me-2nc charges them") and `ve/backends/lean_service.py:146` (me-2nb review F1) stay until me-2ncb, which replaces
that code. DELTA rows C1 and C2 of the task are not in DELTA.md, because neither delta happens in this item.

## Plan rows, delivered and not

| # | Row (task) | Where | Status |
|---|---|---|---|
| 1 | `Shape`, `Lowered`, `Expr.linearC` with its shape rules, `Expr.exactBound`, `exactC`, `Expr.linearC_form`, `_nonlinear`, `_tooLarge` | `lean/VE/Calc/Lower.lean:47-222`, `:655-663` | done |
| 1 | `QLin.isConst` becomes `isConstOnce` | `Lower.lean:39-43`; the lowering reads it, `QLin.isConst` stays as the meaning `Shape.Sound` states | done |
| 2 | `QLin.normOnce_eq`, `Farkas.checkOnce_eq` | `lean/VE/Calc/Linear.lean:192`, `:224` | done; **`checkOnce` is not wired yet**: `Step.derive` still calls `Farkas.check` (me-2ncb) |
| 2 | `pickOnce_eq` | `lean/VE/Calc/FourierMotzkin.lean:324` | done; **not wired yet**: `backSubstitute` still calls `pick` (me-2ncb) |
| 2 | `nonlinearAtC_eq`: each side lowered once, limit 10 in 3.2's order, only `.nonlinear` is `NonlinearPremise` | `lean/VE/Calc/Wire.lean:445`, `:677`, `derivations` `:689` | done; the count is the value table's and the sides', and **the lowering table is not kept**: nothing reads it until (3) |
| 3 | Run.lean: premise facts once per case, units threaded; FM and Derive: `rowCost`, `passCost`, rows and points held | — | **not delivered: me-2ncb** |
| 4 | Fixtures with exact **case** units | `lean/VE/Calc/WorkExamples.lean`, `tests/test_calc_service.py` | **part**: L-1 to L-5, one premise of P-1 and P-2, S-1 to S-10, N-1's side, the K-1 stages' `pickOnce`, P-2 at 72/73 and N-1 at 121/122 on the service. Case units and K-1's units need (3): me-2ncb |
| 4 | `tools/bench/` rows | — | **not delivered**: they do not fit (me-2ncb) |
| 5 | Seeded bugs S7-S16 plus one mutant per new trusted definition | `docs/math-evidence/me-2nc/mutants.json`, `trust-mutants.json` | done: 40 of 40 caught, 18 mechanical mutants allowed with reasons |

The DRI's conditions that this item meets: item 3's P-2 at 72/73 and H-1. Not met yet, and me-2ncb must meet them:
item 1's P-1 rows and L-4; item 2's L-1 `holds`, L-2 to L-4 `derivationInconclusive`, L-5 and a search row. Of item 2,
`Expr.linearC_form`, `_nonlinear` and `powTooLarge_sound` are proved, without `sorry`.

Synthesis-2 edits (`edits-math-evidence.md`): this item implements none; they are plan wording and other items' rows.

## What me-2ncb inherits

- `Check.run` needs the digit hold, and `outcome_sound`'s text must not change. `Node` separates units from result:
  `Expr.held : Expr → Lowered` is a five-line recursion over `stepNode`, and `linearC` returning `l` means `l = e.held`
  by `Node.run_some`. Then `Claim.lower` over held forms goes in `Check.runShown`.
- The search's `Search` monad should track remaining room as `Option Nat`, with `none` unlimited, so `Check.run` is
  the unlimited run and one lemma per search function covers both `runC_sound` and `runC_mono`.
- A row reads premises by `Claim` equality in a table with one entry per premise: a look-up visits at most the table,
  whose nodes are within limit 1. `Case` needs a `premises` field: `Wire.decode` drops them today.
- `decodeCase` needs the whole charged run, so it moves to `Run.lean`.

## Design notes

- **`Node`** replaces the stub's `chargeL limit L w` and `stepC limit e parts w`: a step gives its units and a thunk of
  its result, and `Node.run` refuses before the thunk runs. So the exact fallback's bound is charged before it is
  computed, and a result cannot depend on the limit. Units are the stub's: every 13.3 number reproduces.
- **`exactC`** has the spec's signature; `exactNode` is its `Node`. `stepNode` replaces `stepC`.
- `firstAppearance`, `unknowns` and `QLin.norm` moved from `FourierMotzkin.lean` to `Linear.lean`, so `normOnce_eq` can
  sit under `checkOnce_eq`. Their texts did not change.
- `Wire.derivations` skips the value table when a case has no premise or conclusion to lower, so a plain claim case
  does no new work.

## Statement gate

me-2n's review ended MERGE and me-2nb has merged (`git log`: "Merge feature/me-2nb"). The eight statements proved equal
the stub's after whitespace normalisation (a script over `theorem … :=`; `Expr.linearC_tooLarge`'s difference there
was the regex running past a line break, checked by eye): `QLin.normOnce_eq`, `QLin.isConstOnce_eq`,
`Farkas.checkOnce_eq`, `pickOnce_eq`, `Expr.linearC_form`, `Expr.linearC_nonlinear`, `Expr.linearC_tooLarge`,
`nonlinearAtC_eq`, and `Shape.Sound`'s body. No merged statement changed: the diff touches no existing theorem.
`python3 lean/audit.py`: "PASS: 676 source files; 7607 named theorem declarations audited … only the declared standard
axiom allowlist".

Spec re-read:
- `Shape`, `Lowered`, `Expr.linearC` and its theorems against `docs/spec/math-evidence.md:909-919`;
- `nonlinearAtC` against `:920-924`;
- the one-pass list against `:854-860`;
- what is held to the digit limit against `:861-868`;
- the shape rules against `:869-879`;
- limit 10's order and text against `:807-812`;
- P-2, N-1, L-1 to L-4 and S-1 to S-10 against 13.3 (`:2921-2926`).

## Seeded bugs (`mutants.json`; 40 of 40 caught)

Each bug was planted alone, with that file's theorems cut to `sorry` so the guards decide, then
`lake build VE.Calc.WorkExamples`, then restored (`git status` clean after the run). Every definition is also held by
its proof; the table lists the guards. All are Lean: no Python or Rust product code changed.

| Bug | Definition (file) | Behaviour broken | First guards failing (`WorkExamples.lean`) |
|---|---|---|---|
| S7 | `chargeL` (`Lower.lean`) | forms not held to the digit limit | `:28`, `:29`, `:32` |
| S8 | `stepNode` | a ruled-out power is computed | `:24`, `:75` |
| S9 | `binL` | an operand beyond the limit decides the node | `:73`, `:74` |
| S10 | `addS` | two sides not constant add to not constant | `:73`, `:74` |
| S11 | `FM.tightest` (`FourierMotzkin.lean`) | an equal bound's strictness is dropped | `:149`, `:151` |
| S12 | `QLin.normOnce` (`Linear.lean`) | names that cancel are kept | `:77`, `:125` |
| S13 | `Wire.judged` (`Wire.lean`) | a node past `maxPolyTerms` is judged | `:179`, `:198` |
| S14 | `chargeL` | no entry charge | `:46`, `:55` |
| S15 | `stepNode` | a ruled-out power loses its shape | `:24`, `:75` |
| S16 | `nonlinearAtC` | a power node is not judged | `:179`, `:188` |
| M1-M30 | one or more per new definition | listed in `mutants.json` with their guards | all caught |

Two survived at first, and each became a fixture: M11 (a first power charged again, now `WorkExamples.lean:61`) and
M12 (the right operand's path, now `:187`-`:188`). The trust mutants' first runs left `Shape.Sound` with no check, so
its truth table (`:117`) was added, both ways.

M3 ran with `hugeC` at `powChain 2`: unbounded, it would compute a value of 2.2 × 10⁹ bits and the build passes its
time limit.

## Trust, tests, size

- **Trust:** `uv run python tools/trust_map.py --check`: "K +0, S +6, D +4, G +4, tied +0, unclassified +0, trusted +6"
  and "PASS: K, S and untied [V] within 432763b06d8d and the allowances introduced since". Allowance recorded with
  `--allow`, signed by R16. The FOLLOW-UPS.md row "## me-2nc" asks for the ties pass.
- **Trust mutants:** `mac-pytest.sh --trustmut`: "0 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 INVALID, 18 ALLOWED", exit 0
  (`trust-mutants.json`). The 18 are all `Shape.Sound`. They are not equivalent, bar one (`≤ false` on Bool): the guard
  at `:117` does fail on them, but the tool cannot count it, since the check reads an instance that reads `Shape.Sound`
  (`allow` reasons). The wider `--classes all` run (523 mutants) was **not run**; the 40 hand bugs stand for the C code.
- **Selected tests:** `mac-pytest.sh --select`, GitHub Actions, 6 shards, run me-2nc-75dac3b2-t392237: exit 0, 400 of
  400 units passed (`/tmp/me2nc/select.log`). It ran at 75dac3b27; the commits after it add only this report and
  DELTA.md.
- **Others:** `uv run pytest -q tests/test_calc_service.py`: 26 passed. `tests/test_assurance_manifest.py`: 138 passed
  (Wire.lean re-pinned, 849 lines). `tools/gate_collection.py --check --prebuilt`: "4 added, 0 removed by a trailer, 0
  refused, 0 stale and 0 malformed". `repo_map.py --check`: PASS, 39 modes. No test in `main-known-red.txt` was touched.
- **Not run:** the full gate (the chain runs it), and `tools/bench/` (not delivered). No timing on the UDHR or
  constitution pilots: UNVERIFIED, and they send no `calc` case that I know of.
- **Size,** from `git diff --numstat $(git merge-base HEAD main)`, generated files out: Lean product and proofs +1,283
  −17; fixtures +232 (`WorkExamples.lean`) and +59 (`test_calc_service.py`); `trust-classes.json` +121 −6; evidence and
  docs about +250. About twice the ~600 rule. Most of the Lean is proof that (1) and (2)'s statements need; the cut
  kept (3) out, and nothing in (1) or (2) can go without losing a statement.
- **Bytes:** 0 (the use-case ceiling); no pilot movement is claimed.
- **Overlap:** a loop over `git diff --name-only main...<branch>` for every `feature/*`, `lean-first/*`, `infra/*` and
  `foundation/*` branch found none on `Linear.lean`, `FourierMotzkin.lean`, `Lower.lean`, `Wire.lean` or
  `test_calc_service.py`. `tools/trust-classes.json` is a shared append file; main has moved on it.

**Next:** me-2ncb, then me-3 (the Python relay), me-4, me-5e.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no schema, row field or relay changed; the only new answer is `Wire.limit`'s text, pinned by `test_limit_10_on_the_lowering`.
2. PASS: rows above, each with its commit's file and test; the cut is named (me-2ncb). `git diff` shows no Python copy of a Lean decision and no new report test.
3. PASS: 40 of 40 seeded bugs caught (`mutants.json`); trust mutants exit 0 (`trust-mutants.json`).
4. N.A.: no Python or Rust path changed; `nonlinearAtC_eq` and `WorkExamples.lean:179` compare with 5's check, and `test_limit_10_on_the_lowering` runs the service.
5. N.A.: no field Python reads changed.
6. PASS: no Lean changed after the selected run and the mutant runs; the gate runs on the final HEAD. Main has moved: not synced, the merge train does that.
7. PASS: no reserved signature; C3 item 3, C5 R2, C4 R16 with its FOLLOW-UPS row.
8. PASS: DELTA C3, C4, C5; `Run.rowsC` and `Check.run` are untouched, and S-1 to S-10 (`:73`) show nothing else moves.
9. PASS: `tools/select_tests.py --base …` selects `test_calc_service.py` and `test_assurance_manifest.py`; 400 units, not every unit.
10. PASS: statement gate above; `lean/audit.py` PASS; no `sorry` (`git grep -c sorry` on the four files: 0).
11. PASS: limit refusal at and one under the units, `:26`, `:76`, `:224`; M1 shows the boundary is tested.
12. PASS for this path: step-count guards `:55`, `:133` (units in place of time), N-1 at 122 in 1.3 s (`pytest --durations`); pilots UNVERIFIED.
13. N.A.: no test removed or renamed (`gate_collection --check`: 0 stale, 0 malformed).
14. PASS: both directions per check: digit limit `:32`-`:34`, shape rules `:89`-`:101`, `Shape.Sound` `:117`, equal bounds `:156`-`:158`, decoder paths `:179`-`:181`, fault order `:214`-`:215`, limit 10 `test_limit_10_on_the_lowering` (four sides); claims cite commands above; spec re-read listed above.
