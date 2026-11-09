# ps-2aa: the presupposition wire layer (spec 4.7, Wire.lean) (build report)

No DRI signature is reserved in this item. There are no DELTA rows: the item adds only new Lean, which no route calls.
Trusted growth is +120 (K +0, S +79, V +41), covered by standing ruling R16 (see "Trust").
Status: built, with the cut that the task names (R16's 150 lines). The DRI accepted it as the named cut point
(reviews/dri-decisions-20261109-ps-2aa.md item 1). The readings block goes to ps-2a (see "Cut").
Checks: probe 22/22 declarations equal, audit PASS, trust_map --check PASS, trust_mutants exit 0, selected tests exit 0.
Open: the full gate runs in the chain on the final HEAD. Next item: ps-2a.

Feature item ps-2aa (PS-2a's first part; plan `docs/spec/presupposition-PLAN.md:496-518, :845-863`). Branch
`feature/ps-2aa`, merged with main at 64f06135d's parent 92c4f0417 (merge base ee1fb3efa). Command outputs: `evidence/tests.txt`.

## Preconditions

- **Statement gate.** PASSED, as the task states. I read the stub and did not commit it. Probe (`evidence/tests.txt`): I compared
  each Wire.lean declaration with the stub's 4.7 declaration of the same name, and the four in spec 4.7's definitions
  block (`presupposition.md:940-979`) with the spec too. Comments were stripped and the tokens whitespace-normalised.
  Result: 22 declarations, 0 differ (`cellOk`, `carrierAllowed`, `restrictionPaths`, `entersRestriction`: stub = spec).
- **Synthesis round 2.** Item 1 (no `presuppositions` mode; the report is a layer field): this part keeps it. It adds no
  mode, schema or relay (`git diff --name-only main...HEAD` lists no Python, Rust or Protocol.lean file). Item 5 (the RF
  census row) and DEC 10 (a heading presupposition is the heading unit's `.layer` assumption) belong to ps-2a's `admit`.
  Here only `Position.heading` exists, guarded at Examples.lean:489.
- **Layers.** `tools/check_lean_imports.py` passes ("Lean layer graph kept (799 modules)"). I made no `layer_policy` edit and
  added no exception. Wire.lean imports `VE.Presupposition.{Frame,Reading,Rows}`.
- **In-flight overlap.** Shared files only: `lean/VE.lean`, `tools/trust-classes.json` and `docs/trust-baseline.json`, also
  edited by ap-4, ci-5, et-4b, jt-3b, pe-1, qt-a4b, sc-10b, sc-7, me-1 and arch-20261105-1. My edits there are one import line and added
  entries. No branch touches `lean/VE/Presupposition/` (`git diff --name-only main...<b>` over `feature/*`, `infra/*`,
  `lean-first/*`, `foundation/*`). Audit.lean is generated (lean-audit-manifests), and regen left it unchanged: Wire.lean has no theorem.

## Plan rows delivered

| Row (task "Deliver") | Commit | Evidence |
|---|---|---|
| (1) `Carrier`, `Candidate`, `Carrier.root`, `Carrier.cand`, `Candidate.root`, `Candidate.core`, `Position`, `Args` (+ the stub's `Args.tuple`), `Obligation` | a40bc453a | Examples.lean:476-489 |
| (1) `CandidateTable`, `candidateTable` (empty), `cellOk`, `tableOk` (+ the stub's `rowNames`); the `table` row and 7.2's `tableOk` row, both sides | a40bc453a, 8e63b6621, c8571dd8f | Examples.lean:491-510, :589-597 |
| (1) `Checked`, `Report`, `unitModes`, `ruleConditions` (stub bodies) | a40bc453a | Examples.lean:538-569, :603 |
| (1) `carrierAllowed`; S12 (allowed at `not ·`), S25 and S27 (refused at non-shallow frames), A22/A23's sides | a40bc453a, 172d4140f | Examples.lean:512-536 |
| (1) `restrictionPaths`, `entersRestriction`; body paths `[0, 1, 1]`, `[1, 0, 1]` outside; generic has none | a40bc453a | Examples.lean:571-585, :598-602 |
| (2) size measured | this report | "Size" |
| (3) lemmas for ps-2a | none required (task) | — |
| (4) `lean/VE.lean`, trust classes, inventories through regen | a40bc453a, 9ed3e6e7e, d8f3a1b62, 92c4f0417 | `trust_map --check`, regen |

Guards in Examples.lean: 161 → 213 (`grep -c '^#guard'`).

## Cut (task rule; DRI decision 2026-11-09 ps-2aa item 1)

Wire.lean with every 4.7 definition measured 217 trusted lines (commit 9cdd78473). The kept set measures 120. Keeping
`RReading` and the readings would measure 167. I cut the dependency-closed readings set to ps-2a: `RContent`, `RReading`, `UContent`, `DocUnit`,
`PDoc`, `env`, `unitOf`, `unitContent`, `unitAsserted`, `unitReadings`, `nodeCertificate`, `premisesBefore`,
`claimReading`, `ruleReading`, `emitted`, `aliasesOf`, `expectedReadings`. Their 7.1 rows go with them: `expected`, S12's
and S26's reading shapes, S27's alias half, S17 and the rule-act readings. So does seeded bug 2. Their guards, written and passing, are in
9cdd78473 (Examples.lean). ps-2a's own R16 budget carries the ~47 lines (FOLLOW-UPS.md "## ps-2aa").

## Deviations

- **Seeded bug 2** (`expectedReadings` in place at a non-shallow frame) moved with its definition. Its replacement is
  `carrierAllowed` accepting in place at any frame, the same R-D1 rule. The DRI accepted it.
- **Seeded bug 3 catches at other guards.** `entersRestriction` with `isPrefixOf` reversed leaves the two body-path guards
  true: neither path is a prefix of a restriction path. It fails the inner-copy and the prefix guards (:579, :585).
- **Two stub helpers beyond the spec's list:** `Args.tuple` (the 4-tuple `buildReading` takes) and `rowNames` (`tableOk`'s
  rows, used by `candidates_ruleAct`). Both are the stub's text.
- **regen skipped `route-cases`** (`--skip route-cases`). Its writer needs the Rust release binary, which this worktree
  does not have, and it reads no presupposition file. The chain's gate builds Rust and checks it.

## Seeded bugs (Lean only; this item changes no Python or Rust product code)

`mutants.json` lists 34 hand mutants, at least one per new trusted definition, with `file`, `find`, `replace` and
`test`. I applied each alone, built `VE.Presupposition.Examples` and restored the file. All 34 fail. The claimed behaviours:

| Id | Behaviour | Mutant | Fails |
|---|---|---|---|
| M-cellOk-inPlace-alone | R-2: in place only beside conditioned | drops the clause | Examples.lean:501 (`[inPlace]` alone in the negated cell) |
| M-carrierAllowed-shallow | R-D1: in place needs a shallow frame | always allowed | :528 (S25), :532 (S27), :554 (S26's outer) |
| M-entersRestriction-prefix | R-D6: containment runs one way | `q.isPrefixOf (p ++ o)` | :579, :585 |

The type mutants (a dropped constructor or field) stop Wire.lean itself (e.g. L-Carrier at Wire.lean:38). L-Position
fails the R-10 guard (:489).

**R16 mechanical mutants** (`trust-mutants.json`, `trust-mutants-allow.json`). The first sweep gave 152 KILLED,
27 SURVIVOR and 21 UNKNOWN. The survivors were list edits my guards did not move: an element first or last in `cellOk`'s
`cs`, the first and middle rows and classes of `tableOk`, plural's `[0, 0]`, a two-step `p`, `R.checked.drop 1`.
c8571dd8f and d77575f50 add guards for each one (:587-603). The 21 UNKNOWN are constructor drops and bare `[]`s that do not elaborate.
Each is allowed with a reason that names the hand mutant covering it. Final sweep, head 24928091e, base ee1fb3efa: 179 KILLED, 0 SURVIVOR,
0 UNKNOWN, 21 ALLOWED, exit 0.

## Trust

`tools/trust_map.py --check` PASS against ee1fb3efa: Wire.lean trusted +120 (S +79, D[V] +26, G[V] +15), K +0;
Examples.lean is T (fixtures) and unclassified +0. Classes: S for `Carrier`, `Candidate`, their roots and `cand`/`core`,
`CandidateTable`, `candidateTable`, `cellOk`, `tableOk`, `rowNames`, `unitModes`, `carrierAllowed`, `restrictionPaths`,
`entersRestriction`, `ruleConditions`. D[V] for the wire shapes `Position`, `Args`, `Args.tuple`, `Obligation`. G[V] for
`Checked` and `Report`, as `VE.Norms.Tree` is. The allowance in `docs/trust-baseline.json` is "SIGNED by standing ruling R16
(DRI-RULINGS.md), ps-2aa, 2026-10-18". The "## ps-2aa" ties-pass row is in FOLLOW-UPS.md.

## Size, bytes, evaluators

- **Size.** `git diff --numstat $(git merge-base HEAD main)` (ee1fb3efa), without generated files (codemap,
  declarations, predicates, trust-baseline) and the sweep's output `trust-mutants.json`: Wire.lean 136, Examples.lean 132,
  VE.lean 1, trust-classes.json 44, mutants.json 39, trust-mutants-allow.json 39, evidence/tests.txt 43, REPORT.md (see the total).
- **Pilot bytes.** 0, as the task states: no route reads Wire.lean yet.
- **Evaluators.** None added. `tableOk` walks a constant table: 3 rows × 7 classes, each cell read once.
  `carrierAllowed` reads one cell. Neither is a runner or a mode.
- **Total: 568 added lines, 0 deleted** (REPORT.md 134/0, the rest as listed above), under the ~600 limit.

## Spec re-read

- 4.7 types against `presupposition.md:843-933`: names, constructor order, fields, `deriving`. Definitions against
  `:940-979`, by the probe. The paragraph after it (`:981-983`): body at `[0, 1, 1]` and `[1, 0, 1]`, generic without
  restriction (Examples.lean:571-583).
- 7.1 `table` `:1292` (T, T, F, F, F, T: :493-501), S12 `:1275` (`carrierAllowed` half), S25 `:1276`, S27 `:1278`;
  7.2 `tableOk` `:1310`, `carrierAllowed` `:1312` (A22 at `not ·` :520, A23 at `not (· and r)` :532).
  `expected` `:1291`, S26 `:1277` (readings) and `admit_inPlace_alias` `:1311` are ps-2a's (cut).

## Self-review against BUILDER-CHECKLIST

1. Typed Lean answers: N.A., no relay or service mode added (`git diff --name-only main...HEAD`).
2. Deliverables: PASS, the table above; the named cut is DRI-confirmed (dri-decisions-20261109-ps-2aa.md).
3. Tests can fail: PASS, `mutants.json` (34/34), `trust-mutants.json` exit 0 with `trust-mutants-allow.json`.
4. Three-way agreement: N.A., no Python or Rust path changed; selected tests (113 units) exit 0.
5. R8 binding: N.A., no Lean answer is read by Python.
6. Gate evidence: PASS, merged with main (92c4f0417); sweep and selection ran on the merged tree; the chain runs the gate.
7. Unsigned items: PASS, `trust_map --check` exit 0 with the R16 allowance; no DELTA rows.
8. User-visible changes: PASS, no answer path edited; no route imports VE.Presupposition.Wire (`grep -rl Presupposition.Wire lean/VE`).
9. Test selection: PASS, `select_tests` picked 113/554 units, not all. The seeded bugs fail at `lake build` of Examples.lean, which the gate builds.
10. Statements: N.A., no theorem added (Wire.lean has none; `lean/statements.txt` unchanged by this item's Lean).
11. Budgets: N.A., no operation with a budget.
12. CPU or memory: N.A., new code runs only in `#guard`s at build time.
13. Test-removed trailers: PASS, `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
14. Both directions: PASS, each check has an accepting and a refusing guard (`tableOk` :493-499, `cellOk` :505-508,
    :589-591, `carrierAllowed` :520-536, `entersRestriction` :579-602). Claims cite `evidence/tests.txt`; "Spec re-read" above.
15. Overclaim: PASS, I checked "no", "every", "none" and "all" here against `evidence/tests.txt` and the probe. Silent cut: PASS, the cut point is the
    task's, confirmed by the DRI. New checks can fail: PASS, `mutants.json`, `trust-mutants.json`. Limits: N.A., no evaluator.

FOLLOW-UP: ps-2a takes ps-2aa's cut readings block (RContent to PDoc, document accessors, premisesBefore, claimReading, ruleReading, emitted, aliasesOf, expectedReadings) with the 7.1 expected row, S12/S26 readings, S17 and seeded bug 2
