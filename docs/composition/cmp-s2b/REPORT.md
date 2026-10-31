# cmp-s2b: S2b, first part (superposed verdicts for rights documents)

Status: first coherent part delivered, cut at the size line; the switch is not in. HEAD: see `git log main..HEAD`.
Changed: `sup D` gates rights contents; owners and quiescence for `lim`, `cond` and `aimed` (edit 1); `qualifyKey`
over limitation names; F21's fixed-bar case at well-sorted tuples (`bar_dead`); the rights lifting lemma; the
signed hypothesis `ht` on `superpose_faithful`, with its counterexample. Open: the rest of the rights case, the
switch, the differential and shadow test, the load time (cmp-s2bb). DRI signature needed: none (item 1 of
reviews/dri-decisions-20261031-cmp-s2b.md signed the statement change).

## Plan rows (task "Deliver, in this order")

| Row | Delivered | Where | Evidence |
|---|---|---|---|
| (1) rights case of `superpose_faithful`, F21's fixed-bar case first | partly: the F21 bar step, the construction it needs, the statement fixed | `Choice.lean` (`gateContent`, `copyContent`, `owners`, `qualifyKey`), `BarQuiet.lean` (`quiet_holds`, `bar_dead`), `Faithful.lean` (`ht`) | `RightsExamples.f21_bar_dead`, `rules21`, `choicePremises21`, `f21_needs_typed` |
| (1) owner-based quiescence for `lim`, `cond`, `aimed` (edit 1) | yes | `limOwners`, `aimedOwners`, `jointOwner` | F7, F10 and F21 `#guard`s in `RightsExamples.lean` |
| (1) the other rights cases (line nodes, limitation carve-outs, the simulation) | no: cmp-s2bb | | |
| (2) lifting lemma for `superpose_all` on rights documents | the lemma: `adjoin_baseAdmissibleR`; `superpose_all` without `hch` needs (1): cmp-s2bb | `BarQuiet.lean` | builds; audit PASS |
| (3) the switch, fixtures F6 to F10 and F21, differential and shadow test | F7, F10 and F21 as Lean fixtures; F6, F8, F9, the switch and the differential: cmp-s2bb | `RightsExamples.lean` | `lake build` |
| (4) load time against 85 s on a part document | no: cmp-s2bb (nothing to time before the switch) | | |

Synthesis edits (debates/plan-synthesis-2/edits-composition.md): this item implements none of edits 1 to 8 (they edit
the plan's AR-10, G3, S4, sa-parts, family-adapter, D14, reading-set and cost rows); it builds composition-S2-PLAN.md
converged edit 1 (owner-based quiescence for `lim`, `cond`, `aimed`, the fixed bar kept, F21).

## Deviation (signed)

The rights case of `superpose_faithful` as approved is false at ill-sorted tuples: quiescence binds only sorted
tuples and the fixed bar's node is guarded by `aimed_m` alone (docs/composition/cmp-s2b/DRI-QUESTION.md). The DRI
signed option A (reviews/dri-decisions-20261031-cmp-s2b.md item 1): `(ht : VE.TupleTyped S r.sorts vs)`, in
`lean/VE/Readings/Faithful.lean` and in the plan's S2 block (docs/spec/composition-PLAN.md, one added hypothesis,
nothing else in the spec). Its conditions: (a) `RightsExamples.f21_needs_typed` (F21, the claim choice, `M21` with
`rights__bar__1(e)` for an `e` in no domain: `value21_sup` = `some false`, `value21_choice` = `some true`); (b)
`RightsExamples.f21_bar_dead` and the general `bar_dead`; (c) `base_down`, `base_up`, `superpose_conflict_free`,
`superpose_all` and `superpose_countermodel` keep their statements (`git diff main -- lean/VE/Readings/BaseDown.lean
lean/VE/Readings/BaseUp.lean lean/VE/Readings/SupFree.lean lean/VE/Readings/SupAll.lean
lean/VE/Readings/SupWitness.lean` is empty; the plan's S2 block differs from main only in the two `ht` lines); (d)
S2a's proofs build (`lake build`: "Build completed successfully (1172 jobs)"). No `sorry`, no new axiom
(`python3 lean/audit.py`: "PASS: 679 source files; 7647 named theorem declarations audited").

Other notes for cmp-s2bb, found while building: Python's `ve/readings_sup.superposed_contents` still refuses a
rights document ("rights superposition is S2b"); `pairOwner` reads `origin` on node names, so a candidate fan-out
line (`rights-fan-<k>`) has no outweighs owner yet; a candidate `right_lines` unit on another set's interface right
is not copied per candidate; S2a's proofs that `shared_outweighs` and `fixedGenerated_of_origin` use now state or
prove their rights cases (`shared_outweighs` takes `noRights`).

## Seeded bugs (Lean; no Python or Rust product code changed)

All in lean/VE/Readings/Choice.lean, each planted, `lake build VE.Readings.RightsExamples` run, file restored
(docs/composition/cmp-s2b/mutants.json):

| Definition | Bug | Caught by |
|---|---|---|
| `gateLine` | a candidate line's rule left ungated | `#guard (choiceLabelled F21)…`, `rules21`, `aimedOwners21`, `choicePremises21` |
| `aimedOwners` | every line on `m`, not only liberties | `#guard aimedOwners …rs48m…` |
| `limOwners` | the limitation's origin dropped | F10's lim-owners `#guard` |
| `qualifyKey` (`qLim`) | a lim key's limitation name not qualified | F10's `qualifyKey` and `nameMap` `#guard`s |
| `copyScope` | a fixed limitation's scope keeps the author name | `#guard (sup F7r).1.limits…` |

A first `aimedOwners` mutant (origins replaced by `[]`) broke a proof in `BarQuiet.lean` rather than a fixture and
was replaced. The trust mutants of every new trusted definition: docs/composition/cmp-s2b/trust-mutants.json
(`tools/trust_mutants.py`, 11 definitions, 248 mutants; see "Runs").

## Trust (R16)

`uv run python tools/trust_map.py --check`: "PASS: K, S and untied [V] within 327bf922a119 and the allowances
introduced since"; "against 327bf922a119: K +0, S +0, D +0, G +46"; lean/VE/Readings/Choice.lean +52,
lean/VE/Readings/ChoiceFacts.lean -6. Allowance recorded in docs/trust-baseline.json, SIGNED by standing ruling
R16; FOLLOW-UPS.md row "## cmp-s2b (2026-10-31)" asks for the ties pass.

## Size

`git diff --numstat $(git merge-base HEAD main)` without generated files: +703 -67 (Lean +505 -67, of which
`RightsExamples.lean` 208 and `BarQuiet.lean` 104; docs and evidence +163; `tools/trust-classes.json` +35). Over
the ~600 line by about 100 lines of report, evidence and the DRI question; no further feature was started after
the measurement.

## Pilot bytes

Expected to move: none. No answer changes before the switch (DELTA.md); the UDHR's main document stays UNKNOWN
until cmp-s2bb.

## Runs

- `lake build` (full): "Build completed successfully (1172 jobs)"; `python3 lean/audit.py`: PASS.
- `uv run python tools/regen_generated.py --write`: "wrote 34 entries" (after `python3 tools/rust_build.py`, which
  the route-cases generator needs); `tools/lean_statements.py` again after the `VE.lean` import edit.
- Selected tests (`mac-pytest.sh --select -- --base 327bf922a --run`, Actions then ve-mac-1): 394 of 397 units
  `exit 0`, none failed; the run was stopped by the session's time limit before
  `tests/test_safetyfw_usecases.py`, `tests/test_speech_polar_lean.py` and `tests/test_trust_mutants.py` reported.
  Their rerun: RERUN_RESULT.
- Trust mutants (`mac-pytest.sh --trustmut -- --max-mutants 1000 --json …`): TRUSTMUT_RESULT.
- Not run: the full gate (the chain runs it); no pilot or UDHR run (L70).

## Spec re-read

- `gateContent` rights cases against composition-PLAN.md 2.3 lines 171-184 (right: q(R), every line's norm gated,
  holder guard unchanged; right_lines: lines gated; limitation: q(L), scope naming every copy).
- `owners` for `lim`, `cond`, `aimed` against 2.3 lines 192-202 and composition-S2-PLAN.md edit 1 (a disjunct is a
  conjunction of atoms of candidates of different sets; `aimed_m` only through candidate liberties).
- `qualifyKey` against composition-s2.md 12 (`qualifyKey` for `lim`, `cond` and `aimed` keys over positional
  names; `aimed` keys name the author's predicate and stay).
- `superpose_faithful`'s `ht` against the DRI decision item 1 (one added hypothesis, both chains).
- F21 against composition-PLAN.md section 5, row F21 (the bar node by correlate unchanged; the quiescence premise
  labelled as the liberty's; the claim choice's document has no bar node and no `aimed_m`).

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A., no relayed answer or schema changed (no route reaches the new code).
2. Deliverables and rules: PASS, plan rows above; no Python copy of a Lean decision (`gateNorm` moved, its copy
   deleted); no new report test; no overlap with in-flight branches (checked at the start).
3. Tests can fail: PASS, mutants.json (5 seeded bugs, each a named fixture) and trust-mutants.json.
4. Python, Lean, Rust agree: N.A., no Python or Rust change and no answer change (DELTA.md).
5. R8 binding: N.A., no relayed field added.
6. Gate evidence: the chain runs the gate on the final HEAD; selected tests as in "Runs".
7. No unsigned item: PASS, DELTA.md's one row cites R16; the statement change is the DRI's decision.
8. Every user-visible change in DELTA: PASS, none besides the trust budget (`routeOf`, `notSuperposable`).
9. Test selection: PASS, `tools/select_tests.py` selected 397 of 504 units, including the readings and rights tests.
10. Lean statements: PASS, `f21_needs_typed` shows `ht` is needed; seeded bugs break the F21 theorems.
11. Budgets fail closed: N.A., no budget or limit changed.
12. CPU and memory: N.A., no route runs the new code before the switch (cmp-s2bb times it).
13. Removed tests: N.A., none removed.
14. Both directions: PASS, `f21_bar_dead` (dead at sorted tuples) and `f21_needs_typed` (live at an ill-sorted one);
    F10 shows each choice's own copy; `rs48m` shows a claim on `m` owns nothing.

Next item: cmp-s2bb (below), then cmp-s3.
