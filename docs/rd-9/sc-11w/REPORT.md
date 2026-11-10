# sc-11w: charge `routeSD`'s reads before its work limit (REPORT)

Item sc-11w (feature feed, rd-9 soft chain; a ruling row of sc-11). Decisions:
- manage-agents/reviews/dri-decisions-20261109-sc-11.md item 2, as amended by dri-decisions-20261109-sc-11-3.md items 1-2;
- dri-decisions-20261109-sc-11-2.md item 2 (the at-most-64 over-work `#guard`);
- dri-decisions-20261110-sc-11w.md item 1 (asked by this builder: the correction below, the signed edit of 14.8's
  `def sdSuperposable`, and the conditions (a) to (d)).

## The measurement correction (accepted by the DRI, sc-11w item 1)

sc-11-3 put the 10.98 s and 94-100 s of the 767- and 3,071-node guard documents on `sdSuperposable`. They were
`sdCheckWork N`'s own evaluation: w13_bench printed `sdCheckWork` in the same timed process as `routeSD`.
`sdCheckWork` reads `(softXL N (sup N.D).1).length`, which builds every coherence premise only to count it, and
`cohPremiseU`'s `fill`, `selects` and `subst` of a wide guard take 89.7 s on the 3,071-node document. On main,
`routeSD` alone takes 0.13-0.21 s on those two documents, because `&&` stops at `sdSuperposable` false. It takes
0.95-1.44 s on the 191-node one and 1.32 s on NSDheavy, because there `sdSuperposable` is true and `sdCheckWork` is
read. docs/rd-9/sc-11w/cpu.md has the figures.

## Plan rows delivered

1. **The size charge, read before `sdSuperposable`'s reads.** These are in lean/VE/Readings/SoftSupWire.lean:
   - `sdSizeCharge N` is the source document's rules times its AST nodes: the frame's rules, rights and limitations,
     every fixed content and every candidate's. It is read from `N.D` without building `sup N.D` or `supU N`.
     `sdRuleCharge` and `sdContentCharge` count one rule and one content.
   - `maxSdSizeCharge` = 16,384.
   - `sdSuperposable` reads `decide (sdSizeCharge N ≤ maxSdSizeCharge)` first. This is the one edit of 14.8's
     approved `def sdSuperposable` that the DRI signed. It is recorded in tools/check_rd9_sc1_statements.py's `SIGNED`
     table (`SC11W`), and the approved spec text is not edited, as with B4.
   - `routeSD`'s text and every 14.8 theorem text are unchanged. The checker passes: "SC-11 wire PASS: 15 exact", with
     the one signed edit.
   - Over the charge, `routeSD` is `.enumerated`, today's row. The `todayRow` byte-identity `#guard` pins
     `overCharge`'s row (`routeOf true`, the completion's finding, `choicesJson`), and `wideGuard3071`'s `routeSD`
     equals `routeOf true`.
2. **A cheaper `sdCheckWork`, with no statement change.** `sdCheckWorkFast` counts the exception labels and the
   colliding pairs and builds no premise. The `@[csimp]` theorem `sdCheckWork_eq_fast : @sdCheckWork = @sdCheckWorkFast`
   proves the two equal, so `sdCheckWork` (14.8's text) is evaluated through it. On the 3,071-node document it drops
   from 87-97 s to 0.09 s, including process start.
3. **The three wide-guard documents as fixtures** (lean/VE/Readings/SoftSupWireExamples.lean):
   - `wideGuard191`: within the charge, enumerated by work.
   - `wideGuard767`: within the charge, `superposable` false.
   - `wideGuard3071`: over the charge, so neither `superposable` nor `supU N` is read.

   Each `routeSD` value is pinned by `#guard`. Measured `routeSD` Lean CPU on the VM: 0.25-0.29 s, 0.24-0.25 s and
   0.07-0.08 s (cpu.md).
4. **Off by one, and the charge alone refusing.**
   - `atCharge` (16 rules × 1,024 nodes = 16,384) is superposed.
   - `overCharge` (29 × 565 = 16,385) is enumerated although its `superposable` and `WellFormedU (supU N)` hold.
   - A `#guard` pins each content kind's charge, and another pins a document with frame rules, rights, limitations and
     a bar (`framed`).
   - A `run_meta` check reads `sdSuperposable`'s compiled `&&` chain and fails unless its first operand is the charge.
     That is the order no value `#guard` can see.
5. **14.11 restated as measured** (docs/spec/rd-9-soft-chain.md 14.11 only). The `sup N.D`/`supU N` row now has the
   charge, and the closing paragraph gives the charge's definition, 16,384, the machine and load, the signed edit, and
   the corrected reading of the 10.98 s and 94-100 s. It cites sc-11-3 item 1 and sc-11w item 1.
6. **Unchanged and selected.** W-13's three route `#guard`s (`NSDbig 8` superposed, `NSDbig 10` enumerated by work,
   `NSDbig 11` over 1024) and sc-11-2 item 2's `NSDheavy` `#guard` ("enumerated true 64 34752 enumerated":
   `sdSuperposable` true, the work bound refuses) stay unchanged. NSDheavy's charge is 11,523.

Also changed: tests/test_rd9_sc11_charge_wording.py. The code comment and 14.11 must now state the charge (`CURRENT`)
and no longer say "not charged". sc-11's REPORT keeps the wording sc-11 merged with. tools/trust-classes.json classes
the new declarations.

`sdCheckWork` was not made stricter (the task allows that but does not need it).

## Seeded bugs (docs/rd-9/sc-11w/mutants.json)

All are Lean, in lean/VE/Readings/SoftSupWire.lean. Each was shown failing with `lake build
VE.Readings.SoftSupWireExamples` and then restored with `git checkout`.

| Id | Bug | Fails |
| --- | --- | --- |
| M1 | charge dropped from `sdSuperposable` | `SupReplaySD.parts`'s proof; with that proof order-free, the `overCharge` `#guard` |
| M2 | size charge read after `sdSuperposable` (task bug 1) | `SupReplaySD.parts`'s proof; with that proof order-free, the `run_meta` first-operand check |
| M3a / M3b | `maxSdSizeCharge` 16383 / 16385 (task bug 2) | the `atCharge` / `overCharge` `#guard` |
| M4 | `sdRuleCharge` drops exception conditions | the `wideGuard191` `#guard` |
| M5 | `sdContentCharge` drops a limitation's conditions | the content-kind `#guard` |
| M6 | `sdSizeCharge` drops the frame's limitations | the `framed` `#guard` |
| M7 | `sdCheckWorkFast` drops the colliding pairs | `sdCheckWork_eq_fast`'s proof; with it `sorry`ed, the `M8` route `#guard` (work 30) |
| M8 | over the charge `routeSD` answers abstention (task bug 3) | `routeSD_superposed_iff`'s proof; with it `sorry`ed, the `wideGuard3071`, `overCharge` and `todayRow` byte-identity `#guard`s |

The task's bug 1 in its timing form ("the 3,071-node fixture's timing check fails") cannot fail. `&&` gives the same
value in either order, and the document is cheap either way: `superposable` stops early on it. The DRI replaced that
condition with (a) and (b) of sc-11w item 1, which M1-M8 meet. Python and Rust product code are unchanged, so there
are no seeded bugs in those languages.

## Trust

TRUST-PENDING

## DELTA

None. A stricter route check only refuses more: over the charge the row is the enumerated row with today's cause.
sc-11-3 item 1 and sc-11w item 1 cover this with no DELTA row and no reserved signature. The dispatch is unchanged
(14.13), and nothing outside SoftSupWireExamples.lean evaluates `routeSD`.

## Pilot bytes

0 expected: `routeSD` is not dispatched before sc-11b.

## Size

SIZE-PENDING

## Not done, and next

- Per-choice texts within the work limit cost about 31-54 µs per `sdCheckWork` unit on the shapes tried (cpu.md). A
  heavy shape just within 32,768 units could therefore take about 1.8 s. That is `maxSdCheckWork`'s bound (sc-11
  item 1), outside this item's required scope: sc-11-3 item 1 dropped the cost-proportional work charge. It bears on
  sc-11b, which routes live documents.
- Next items: sc-11c (the soft runners), then sc-11b.

## Tests

TESTS-PENDING
