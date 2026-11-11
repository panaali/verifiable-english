# ps-7-p9: P9 guards that a PS-7 definition mutant can fail (test-only)

Item ps-7-p9 (DRI 2026-11-11, reviews/dri-decisions-20261111-lp0000.md item 2). Branch feature/ps-7-p9.
Base: merge base 97b3c7999a.

## Problem

On main, the P9 guards (lean/VE/Presupposition/Events/Examples.lean:170 and :175 at main) compared `p9.pre` with
`p9F = .andR ipBefore .hole`, where `ipBefore = inProgressBefore V stay x t` is the definition `continues` builds
its pre from. Under any mutant of `inProgressBefore`, both sides move together:
- :170's goal `ipBefore → p9.pre` becomes `ipBefore' → ipBefore'`, which still holds.
- :175's entailment `ipBefore ∧ ip → p9.pre` becomes `ipBefore' ∧ ip → ipBefore'`, which also still holds.

So neither guard could fail. This is a reading of the guard terms, not a run on main.

## Delivered

| Task row | Delivered | Where |
|---|---|---|
| (1) Rewrite the P9 guards against a formula written out on the fixture's constants | yes | Events/Examples.lean:164-190 |
| (2) A PS-7 definition mutant per rewritten guard, killed with the phrase's input fixed, and replayed | yes | docs/presupposition/ps-7/mutants.json: M-p9-before-reversed, M-p9-ip-at-t |
| (3) Test-only: no definition change, no DELTA row, no trust growth, no signature reserved | yes | see Trust and DELTA |

(1) The P9 block now defines two formulas on the fixture constants `s` and `t`, written out from the events
wordings-table formula the same way lean/VE/Events/Examples.lean:109 (`inProgress`) is:
- `ongoing` (:169): ∃u. before(u,t) ∧ in progress on u.
- `onDay` (:174): in progress on t.

Neither formula goes through `inProgressBefore`, `inProgress`, `ip` or `ipBefore`. The phrase is
`p9 = continues V stay x t onDay`, and `p9F = .andR ongoing .hole`. The guards are:
- :181: the goal holds, and asserted, conditioned and in place all equal the weak plug.
- :183: the strong plug on the five situations. This line is unchanged.
- :187: `ongoing ∧ onDay` entails the pre.
- :188 (new): the pre equals `ongoing` on every situation. This is the opposite direction of :187: it checks the
  value the pre must keep, not just an implication.
- :189: read with `onDay`, the goal fails on onT, and asserted and conditioned differ there. This is the refusing
  direction.

Main's definitions pass all of them. The `lake build` and the replay below show this.

(2) The new mutants are in docs/presupposition/ps-7/mutants.json. Both change `VE.Presupposition.Events.inProgressBefore`
(lean/VE/Presupposition/Events.lean), and the phrase's input `onDay` stays fixed:

| Mutant | Change | Rewritten P9 guards that fail |
|---|---|---|
| M-p9-before-reversed | before(u,t) reversed to before(t,u) | :181, :183, :187, :188, :189 |
| M-p9-ip-at-t | in progress on t, not on the earlier day u | :181, :188, :189 |

Each rewritten guard (:181, :187, :188, :189) is failed by at least one of these mutants.

The rewritten guards also fail under these existing mutants (recorded test lists refreshed):
- M-stops-no-before, M-ip-no-begin-bound, M-ip-lift-t: :188, :189.
- M-ip-no-ends: no P9 line. On the shared five states, the ends clause does not change the pre. Adding a state
  would mean editing the shared `states` list outside the P9 block, which this item may not touch (see Notes).

Replay of all 28 mutants: 28/28 KILLED. Commit 9becaebe07 records this, and the `replay` field of mutants.json
gives the procedure. I replayed M-p9-ip-at-t again on the final Lean tree in this session:
`lake build VE.Presupposition.Events.Examples` reported errors at Examples.lean:46 49 50 51 54 58 148 154 181 188
189 196 205. That is exactly the recorded `test` list. After `git checkout` of Events.lean, the full `lake build`
printed "Build completed successfully (1382 jobs)".

## Seeded bugs (Lean; the only language changed)

The changed code is a test file, Events/Examples.lean (trust class T). The seeded bugs are planted in the definitions
those tests exercise, in lean/VE/Presupposition/Events.lean. Each fails a named rewritten `#guard`, and each is
restored afterwards:
1. M-p9-before-reversed (`inProgressBefore`, before(u,t) reversed): fails Events/Examples.lean:187 (entailment)
   and :181 (goal).
2. M-p9-ip-at-t (`inProgressBefore`, in progress on t rather than on u): fails :188 (pre = ongoing) and :181. I
   replayed this one this session (output above).
3. M-ip-no-begin-bound (`inProgress`, the begin day after t allowed): fails :189 (the onDay contrast) and :188.

## Trust, DELTA, generated files, checks

- Trust: `uv run python tools/trust_map.py --check` prints "against 97b3c7999add: K +0, S +0, D +0, G +0, tied +0,
  unclassified +0, trusted +0", then "PASS". There is no growth, so no allowance and no R16 row.
- trust_mutants: light-lane printed `NOT trusted core: tools/trust-classes.json`. That generated file gained the
  names `ongoing` and `onDay`, both class T. So I ran the sweep:
  `mac-pytest.sh --trustmut -- --test lean/VE/Presupposition/Events/Examples.lean --json docs/presupposition/ps-7-p9/trust-mutants.json`.
  It reported "0 definitions, 0 mutants … 0 SURVIVOR", exit 0. No trusted declaration changed, and `--plan` gave
  `"definitions": 0` too.
- DELTA: no rows: test-only. There is no user-visible change, and no DRI signature is reserved.
- Generated files: lean/declarations.txt (lean-statements) and tools/trust-classes.json (trust-tables) come from
  their generators. `uv run python tools/regen_generated.py --check` exited 0 ("checked 38 entries").
- `python3 lean/audit.py` printed "PASS: 843 source files; 9475 named theorem declarations audited".
- Test selection: `tools/select_tests.py --base 97b3c7999a` selects 104/586 units, including `lake build` (which
  runs these `#guard`s) and `python3 lean/audit.py`.
- Overlap: no local `lean-first/*`, `feature/*`, `infra/*` or `foundation/*` branch changes Events/Examples.lean
  or ps-7/mutants.json (`git diff --name-only main...<branch>`). The edit stays inside the P9 block; the (k)/(l)
  guards that the held item ps-7d edits are untouched.

SIZE: 0 product, 33 tests (Events/Examples.lean +23/-10), 16 other hand-written lines (mutants.json +9/-7), plus
this report. Measured with `git diff --numstat`.

Pilot bytes expected to move: none. This item is test-only and changes no verdict.

Next item: ps-4 (its P9 exposure hold lifts when this merges).

## Notes for the DRI

- `M-ip-no-ends` (the not-ended conjunct dropped, the task's second example) is not failed by any P9 guard. The
  shared five-state fixture has no situation where s begins and ends before t with no day between. A P9-only
  situation could kill it, but this item is limited to the P9 block and ps-7d is editing the same file. The task's
  rule of one killing mutant per rewritten guard is met without it.
- Tests already red on main (main-known-red.txt): I ran none of them. This item touches no Python.

## Self-review against BUILDER-CHECKLIST

1. Lean answer typed and contained: N.A., no relayed answer changes (test-only).
2. Deliverables built, no rule broken: PASS. Rows (1)-(3) are in the table above, with the `lake build` and
   `lean/audit.py` output cited.
3. Tests and gates can fail: PASS. M-p9-before-reversed and M-p9-ip-at-t fail Events/Examples.lean:181, :187,
   :188, :189 (replay above).
4. Python, Lean and Rust agree: N.A., no Python or Rust change.
5. R8 binding: N.A., no binding.
6. Gate evidence matches the final HEAD: PASS. The trust-mutants.json, `lake build`, audit and regen check all ran
   on 9becaebe07's tree. Only docs are added after it.
7. No unsigned item: PASS. There are no DELTA rows and no reserved signature, and `trust_map.py --check` PASSes
   with +0.
8. Every user-visible change is in DELTA: N.A., no user-visible change.
9. Test selection finds the tests: PASS. `select_tests.py` selects `lake build`, which compiles the changed
   `#guard`s, and a seeded mutant fails that build (replay above).
10. Lean statements say what is claimed: PASS. The `ongoing` and `onDay` comments (:168, :173) give the formula
    each one writes out, and :188 checks pre = `ongoing` on all five states.
11. Budgets fail closed: N.A., no limit or evaluator.
12. No CPU or memory regression: N.A., two small formulas in a test module.
13. Test-removed trailer: N.A., no test removed. The rewritten guards replace :170/:175 in place.
14. Both directions and cited evidence: PASS. The accepting direction is :181/:187/:188 (main's definitions pass,
    shown by `lake build`); the refusing direction is :189, plus the mutants. Spec re-read: `ongoing` and `onDay`
    against lean/VE/Events/Examples.lean:109 (`inProgress`, the events wordings-table formula).
15. Four FIX classes: PASS. No overclaim: the one mutant no P9 guard fails (M-ip-no-ends) is named in Notes. No
    deliverable cut. Every new check can fail (item 3). Limits: N.A.
