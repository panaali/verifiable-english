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
   colliding pairs, and builds no coherence premise; it still builds the exception premises (`excPremises`), one
   formula per exception condition, to count them. The `@[csimp]` theorem `sdCheckWork_eq_fast` proves it equal to
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

`git diff --numstat` against the merge base, with generated files (codemap, inventories) excluded: +625 -20 = 645.
- 225 of those lines are code, fixtures, the checker, trust classes and tests.
- 90 are SoftSupWireExamples.lean fixtures that are conditions of a DRI ruling (sc-11w item 1 (a)). Those are exempt
  from the ~600 count (adv1207 item 3), leaving about 555.
- The rest is evidence and docs: REPORT, cpu.md, cpu_bench.lean, mutants.json and 14.11.

## Open: per-choice work over R4 inside the limits, row sc-11wc (dri-decisions-20261110-sc-11w-cpu.md)

`heavyIn` is `NSDbig 6` plus 9 fixed rules with 47-node guards. Its charge is 12,880 and its work 31,744, both within
their limits, and `routeSD` took 1.16, 0.85 and 1.01 s at load 43-67, and 0.67-0.74 s at load 36. The per-choice texts
within `maxSdCheckWork` cost about 31-54 µs per unit. Row sc-11wc bounds this before sc-11b (sc-11b is blocked by it).
Next items: sc-11wc, sc-11c (the soft runners), then sc-11b.

## Tests

- Selected tests on 0754a04015 (`mac-pytest.sh --select`, log /tmp/sc11w-select2.log; ran on ve-cloud-2 after
  Actions shard 2 gave no result): 115 units recorded, 1 failed. That was `tests/test_lean_dump_cache.py`, three
  tests, because the `run_meta` order check made the tree run code while it elaborates. It was fixed in b9b9fdabe4
  (the `rfl` pin). The three ids rerun on a1d2e27dd6 (`mac-pytest.sh -- <ids>`, VM): 3 passed. Locally,
  `tests/test_rd9_statements.py`, `tests/test_rd9_sc11_charge_wording.py` and `tests/test_trust_budget.py`: 65 passed.
  No failure is in main-known-red.txt.
- `lake build` (1358 jobs) and `python3 lean/audit.py` ("PASS: 825 source files") on a1d2e27dd6, after
  `regen_generated.py --write` (rc 0).
- `tools/check_rd9_sc1_statements.py`: "SC-11 wire PASS: 15 exact", with sdSuperposable signed.
- `tools/gate_collection.py --check --prebuilt`: the two removed ids carry `Test-removed:` trailers in the final
  trailer block of the REPORT commit. The first trailers, in 4559df88d0's body, were not parsed as trailers.

SELF-REVIEW: 2 A, 5 B, 4 C; fixed 11 (A1 the charge counts every unit; A2 14.11 and cpu.md restated with set- and
candidate-heavy shapes; B1 asked the DRI, row sc-11wc; B2 mutant M5b; B3 trailers; B4 re-measured on the final Lean;
B5 FOLLOW-UPS row and REPORT sections; C1-C4).

## Review fix round (sc-11w-review.final.md on 89f139589f)

- F1 (A): `sdCheckWorkFast` builds no coherence premise but still builds the exception premises (`min` reads
  `excPremises X`'s length). Narrowed in SoftSupWire.lean's module docstring and `sdCheckWorkFast`'s comment, 14.11,
  this REPORT's row 2 and cpu.md's "after" paragraph.
- F2 (A): the charge bounds `sdSuperposable`'s reads, not the whole route. `sdSizeCharge`'s comment, the module
  docstring and 14.11 now name the accepted sc-11wc gap (`heavyIn`, up to 1.16 s). cpu.md's summary named 0.60 s
  as the slowest while its table has 0.74 s, and called the at-charge shapes the worst reads while `wideGuard191`'s
  are slower; both summaries now state the table's maxima, and item 12 below says 0.74 s.
- Class tests (tests/test_rd9_sc11_charge_wording.py): every sc-11w text is scanned for an unnarrowed premise claim
  and for "within the charge, `routeSD` ends within R4"; each fast-counter text must name `excPremises`; each charge
  measurement must name sc-11wc; cpu.md's summary figures are recomputed from its table. On the reviewed text 14 of
  them fail.
- F-ready1 (B): Python mutants P1 and P2 on tools/check_rd9_sc1_statements.py, each killed by
  tests/test_rd9_statements.py (mutants.json).

## Self-review against BUILDER-CHECKLIST

1. Typed and contained answers: N.A. (no relayed answer and no wire change; `routeSD` is not dispatched).
2. Deliverables: PASS (rows 1-6 above; `#guard`s in SoftSupWireExamples.lean; cpu.md; 14.11).
3. Tests can fail: PASS (mutants.json M1-M8, each with the failing `#guard` or proof; P1-P2 for the Python
   checker, each with its failing test).
4. Python, Lean and Rust agree: N.A. (Lean semantics only; the one Python change is the statement checker's
   `SIGNED` entry, seeded by P1-P2; no Rust).
5. R8 binding: N.A. (no relay).
6. Gate evidence on the final HEAD: PASS (selected run, the failed ids rerun, audit and build on a1d2e27dd6). The gate
   itself is the chain's.
7. No unsigned item: PASS (the 14.8 edit is signed in dri-decisions-20261110-sc-11w.md item 1, via the checker's
   `SC11W` entry).
8. DELTA: N.A. (refusal direction only; sc-11-3 item 1 and sc-11w item 1: no DELTA row).
9. Test selection: PASS (the selection picked `tests/test_rd9_statements.py`, `tests/test_rd9_sc11_charge_wording.py`
   and `tests/test_lean_dump_cache.py`; log /tmp/sc11w-select2.log).
10. Lean statements: PASS (`check_rd9_sc1_statements.py`; `sdCheckWork_eq_fast` proved; audit standard axioms only).
11. Limits fail closed: PASS (over the charge, enumerated: `overCharge`, `NSDsets`, `NSDcands`, `wideGuard767` and
    `wideGuard3071` `#guard`s).
12. CPU: PASS (cpu.md: every case at most 0.74 s at load 36, the slowest `heavyIn`, which took up to 1.16 s at
    load 43-67 and is the open row sc-11wc; the csimp takes `sdCheckWork` from 87-97 s to 0.07 s; the examples
    module builds in about 1m45 interpreted).
13. Test-removed trailers: PASS (`gate_collection.py --check --prebuilt` after the trailer commit).
14. Both directions: PASS (`atCharge` accepts and `overCharge` refuses; the wide-guard documents on each side;
    spec re-read: 14.8 `def sdSuperposable` against docs/spec/rd-9-soft-chain.md:2297 and its signed edit, 14.11's row
    and closing paragraph against dri-decisions-20261110-sc-11w.md item 1).
15. Four classes: PASS. No overclaim: 14.11's "at most 0.60 s" is for the listed documents, 14.11 and the code
    comment say the charge bounds the reads and not the whole route, and heavyIn is listed as
    open. No silent cut: per-choice work is ruled sc-11wc. Every check can fail: mutants.json. Limits charged before
    work: the `rfl` order pin.
