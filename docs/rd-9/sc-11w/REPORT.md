# sc-11w: charge `routeSD`'s reads before its work limit (REPORT)

Item sc-11w (feature feed, rd-9 soft chain; a ruling row of sc-11). Decisions, all in manage-agents/reviews/:
- dri-decisions-20261109-sc-11.md item 2, as amended by dri-decisions-20261109-sc-11-3.md items 1-2;
- dri-decisions-20261109-sc-11-2.md item 2 (the at-most-64 over-work `#guard`);
- dri-decisions-20261110-sc-11w.md item 1, asked by this builder (the correction below, the signed edit of 14.8's
  `def sdSuperposable`, and conditions (a)-(d));
- dri-decisions-20261110-sc-11w-cpu.md item 1, asked by this builder (per-choice work, filed as row sc-11wc).

## The measurement correction (accepted by the DRI, sc-11w item 1)

sc-11-3 put the 10.98 s and 94-100 s of the 767- and 3,071-node guard documents on `sdSuperposable`. They were
`sdCheckWork N`'s own evaluation: w13_bench printed `sdCheckWork` in the same timed process as `routeSD`.
`sdCheckWork` reads `(softXL N (sup N.D).1).length`, which builds every coherence premise only to count it, and
`cohPremiseU`'s `fill`, `selects` and `subst` of a wide guard take 89.7 s on the 3,071-node document.

On main, `routeSD` alone takes 130-142 ms on those two documents, because `&&` stops at `sdSuperposable` false. It
takes 0.95-1.44 s on the 191-node document and 1.32 s on NSDheavy, because there `sdSuperposable` is true and
`sdCheckWork` is read. docs/rd-9/sc-11w/cpu.md has the figures.

## Plan rows delivered

1. **The size charge, read first.** These are in lean/VE/Readings/SoftSupWire.lean.
   - `sdSizeCharge N` is the source document's units times its AST nodes, read from `N.D` without building `sup N.D`
     or `supU N`. Units: each frame rule, right, limitation and definition, and each fixed content, bar, reading set,
     candidate, coupling and narrowing. Nodes: each unit's formulas, at least one per unit, plus each cite, label,
     `over` name, coupled set and kept candidate. `sdRuleCharge` and `sdContentCharge` count one rule and one content.
   - `maxSdSizeCharge` = 16,384.
   - `sdSuperposable` reads `decide (sdSizeCharge N ≤ maxSdSizeCharge)` first. This is the one edit of 14.8's approved
     `def sdSuperposable` that the DRI signed. It is recorded in tools/check_rd9_sc1_statements.py's `SIGNED` table
     (`SC11W`), and the approved spec text is not edited, as with B4.
   - `routeSD`'s text and every 14.8 theorem text are unchanged. After regen the checker gives "SC-11 wire PASS: 15
     exact" with "sdSuperposable: SIGNED by the DRI 2026-11-10 (...) approved text with its one signed edit".
   - Over the charge, `routeSD` is `.enumerated`, today's row. The `todayRow` `#guard` pins `overCharge`'s row bytes
     (`routeOf true`, the completion's finding, `choicesJson`).
2. **A cheaper `sdCheckWork`, with no statement change.** `sdCheckWorkFast` counts the exception labels and the
   colliding pairs, and builds no premise. The `@[csimp]` theorem `sdCheckWork_eq_fast` proves it equal to
   `sdCheckWork`, which is evaluated through it. On the 3,071-node document it drops from 87-97 s to 0.07 s.
3. **The three wide-guard documents as fixtures** (lean/VE/Readings/SoftSupWireExamples.lean), each `routeSD` value
   pinned by `#guard`:
   - `wideGuard191`: within the charge, enumerated by work, 0.21 s Lean CPU on the VM;
   - `wideGuard767`: over the charge, 0.06-0.07 s;
   - `wideGuard3071`: over the charge, 0.06-0.07 s.
4. **Off by one, and the charge alone refusing.**
   - `atCharge` (16 units × 1,024 nodes = 16,384) is superposed.
   - `overCharge` (29 × 565 = 16,385) is enumerated, although its `superposable` and `WellFormedU (supU N)` hold.
   - `NSDsets` (300 sets) and `NSDcands` (one set of 5,000 candidates) are refused by the charge. These are the
     self-review's shapes, which took 11 s and 23 s.
   - Two `#guard`s pin the charge: one per content kind, and one on a document with every counted kind (`framed`).
   - An `example … := rfl` pins `sdSuperposable`'s term with the charge as the left operand, which `&&` reduces on and
     compiled code reads first. That is the order, which no value `#guard` can see. A `run_meta` check was used first,
     but it makes the tree run code while it elaborates, which tests/test_lean_dump_cache.py refuses.
5. **14.11 restated as measured** (docs/spec/rd-9-soft-chain.md 14.11 only), citing sc-11-3 item 1 and sc-11w item 1.
   - The `sup N.D`/`supU N` row gains the charge.
   - The closing paragraph gives the charge's definition, 16,384, the machine and load, the signed edit, and the
     corrected reading of the 10.98 s and 94-100 s.
6. **Unchanged and selected.**
   - W-13's three route `#guard`s: `NSDbig 8` superposed, `NSDbig 10` enumerated by work, `NSDbig 11` over 1024.
   - sc-11-2 item 2's `NSDheavy` `#guard`: "enumerated true 64 34752 enumerated", with `sdSuperposable` true and the
     work bound refusing. NSDheavy's charge is 14,703.

Outside the task's file list, each needed by the above:
- tools/check_rd9_sc1_statements.py: the signed entry, added to the file list by sc-11w item 1.
- tests/test_rd9_sc11_charge_wording.py: the code comment and 14.11 must now state the charge and no longer say "not
  charged". sc-11's REPORT keeps its merged wording. Two test ids were removed and replaced, with `Test-removed:`
  trailers in 4559df88d0.
- tools/trust-classes.json: the new declarations' classes.
- Inside SoftSupWire.lean, beyond the named regions: `SupReplaySD.parts`'s proof (one projection, after the signed
  edit) and `sdCheckWorkFast` with its csimp theorem.
- The fixtures' helpers in SoftSupWireExamples.lean: `chargeFacts`, `sized`, `NSDsized`, `todayRow` and `framed*`.

`sdCheckWork` was not made stricter (allowed, not required).

## Seeded bugs (docs/rd-9/sc-11w/mutants.json)

All are Lean, in lean/VE/Readings/SoftSupWire.lean. Each was rerun on 195119a8e0, shown failing, and restored with
`git checkout`. M1, M2, M7 and M8 are first rejected by a proof; their second run patches only that proof and shows
the named `#guard` failing.

| Id | Bug | Fails |
| --- | --- | --- |
| M1 | charge dropped from `sdSuperposable` | `overCharge`, `NSDsets`/`NSDcands`, `todayRow` `#guard`s, the `rfl` order pin |
| M2 | charge read after `sdSuperposable` (task bug 1) | the `rfl` order pin |
| M3a / M3b | `maxSdSizeCharge` 16383 / 16385 (task bug 2) | `atCharge` / `overCharge` and `todayRow` |
| M4 / M4b | `sdRuleCharge` drops exception conditions / `over` names | `wideGuard191` and others / content-kind |
| M5 / M5b / M5c | `sdContentCharge` drops a limitation's conditions / counts one line rule / no assertion unit | content-kind, `framed`, `NSDsets` |
| M6 / M6b / M6c | `sdSizeCharge` drops frame limitations / a set's unit / couplings | `framed`, the wide-guard and at-limit `#guard`s |
| M7 | `sdCheckWorkFast` drops the colliding pairs | `sdCheckWork_eq_fast`; with it `sorry`ed, sc-11's route `#guard`s |
| M8 | over the charge `routeSD` answers abstention (task bug 3) | `todayRow` byte identity, `wideGuard3071`, `overCharge` |

The task's bug 1 in its timing form cannot fail: `&&` gives the same value in either order, and the 3,071-node
document is cheap either way. The DRI replaced it with conditions (a) and (b) of sc-11w item 1. Python and Rust product
code are unchanged, so there are no seeded bugs in those languages.

## Trust

`tools/trust_map.py --check` against a3454b6ba598 gives K +0, S +0, D +0, G +2, untied V +0, trusted +0: PASS.
- `sdRuleCharge`, `sdContentCharge`, `sdSizeCharge` and `sdCheckWorkFast` are class C, like sc-11's `sdCheckWork` and
  `routeSD`.
- `maxSdSizeCharge` is G[R], like `maxSdCheckWork`.
- The fixtures are T.
- `trust_mutants.py --plan` finds 0 trusted definitions and 0 mutants, so no sweep applies (checklist 13a). The
  light lane says NOT only because of tools/trust-classes.json.
- The FOLLOW-UPS.md row "## sc-11w" asks the ties pass to confirm the C class.

`lean/audit.py` passes (825 files, standard axioms only).

## DELTA

None. A stricter route check only refuses more: over the charge the row is the enumerated row with today's cause.
sc-11-3 item 1 and sc-11w item 1 cover this, with no DELTA row and no reserved signature. The dispatch is unchanged
(14.13).

## Pilot bytes

0 expected: `routeSD` is not dispatched before sc-11b.

## Size

`git diff --numstat` against the merge base, generated files excluded, is about 600 lines. Code, fixtures, the checker
and the test are 220. Evidence and docs (REPORT, cpu.md, cpu_bench.lean, mutants.json, 14.11) are the rest.

## Open: per-choice work over R4 inside the limits, row sc-11wc (dri-decisions-20261110-sc-11w-cpu.md)

`heavyIn` is `NSDbig 6` plus 9 fixed rules with 47-node guards. Its charge is 12,880 and its work 31,744, both within
their limits, and `routeSD` took 1.16, 0.85 and 1.01 s at load 43-67, and 0.67-0.74 s at load 36. The per-choice texts
within `maxSdCheckWork` cost about 31-54 µs per unit. Row sc-11wc bounds this before sc-11b (sc-11b is blocked by it).
Next items: sc-11wc, sc-11c (the soft runners), then sc-11b.

## Tests

TESTS-PENDING
