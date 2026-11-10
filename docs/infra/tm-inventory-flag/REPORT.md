# tm-inventory-flag: `--only IDS` in tools/trust_mutants.py

Item tm-inventory-flag (infra p40; DRI adv0642 apply item 2, reviews/dri-decisions-20261105-adv0642-apply.md;
task file under LP-20261108T1600-2, reviews/dri-decisions-20261108-lp1600.md item 2). Nothing reserved; no DELTA
row (tooling only, no checker output changes); no Lean change.

## (a) The flag

`tools/trust_mutants.py --only IDS`: ids comma- or space-separated, or `@FILE` with one id per line (blank lines
and repeats ignored). Right after `plan(...)`, where the line tm-inventory.py injects filters today, the plan is cut
to those ids in plan order, before `--max-mutants`, `--shard`, `--rescore` and `--resume` read it. An id not in
the plan is a fatal plan error: exit 2, `--only: not in the plan: <ids>` on stderr, nothing built or written. An
empty list or an unreadable @FILE also exits 2. `--plan --only ...` prints the counts of the kept mutants plus
`"only": [the kept ids]`. Without `--only`, nothing changes (`test_plan_prints_the_counts_and_builds_nothing`
still expects the exact old line). The anchor line `found, tree, fatal = plan(root, base, classes)` is kept as it
was, so tm-inventory.py's MARK line still applies until the follow-up drops it.

## (b) Tests (tests/test_trust_mutants.py, on the stubbed `sharded` plan of 8 mutants, no Lean)

- `test_only_keeps_exactly_the_named_mutants[4 forms]`: comma, space, mixed with a repeat, @file; exactly M002 and
  M005 run and are recorded, both judged.
- `test_only_an_id_not_in_the_plan_stops_the_run[4]`: unknown ids (alone and next to a known one) and empty lists:
  exit 2, nothing run or built, no record, stderr names the unknown ids.
- `test_only_with_plan_prints_only_the_kept_mutants`: `--plan --only M007,M001,M004 --max-mutants 2` prints
  mutants 3, to_run 2, not_run 1, `only` = [M001, M004, M007] in plan order, and builds nothing.

`uv run pytest -q tests/test_trust_mutants.py -k "<the 3 names> or test_plan_prints_the_counts_and_builds_nothing"`:
10 passed.

Seeded bugs (Python, tools/trust_mutants.py; each planted, run against its test, then removed, `cmp` with the saved
copy before commit):

| # | Bug | Failing test |
|---|-----|--------------|
| S1 | the filter ignored (`found = found`) | test_only_keeps_exactly_the_named_mutants: 4 failed |
| S2 | an unknown id silently dropped (no fatal) | test_only_an_id_not_in_the_plan_stops_the_run: 2 failed (the 2 unknown-id cases) |
| S3 | `--plan` prints the requested ids, not the kept plan-order ones | test_only_with_plan_prints_only_the_kept_mutants: 1 failed |

## (c) Would mutants killed at a changed check line have joined the inventory?

Method: `python3 docs/infra/tm-inventory-flag/measure.py <sidecar>...` in this checkout, output saved in
`counts.json`. For each tm-inventory sidecar in /home/seyran/code/manage-agents/reviews/tm-targeted, it takes the
KILLED rows (raw status) of the record the inventory was built from, and finds those whose `killed_at` lines in
the check file named by `detail` overlap a line that the diff record_head..item_head under lean/ changes (on the
record's side). It then checks whether the inventory already holds each one (by definition, operator, before,
after). The inventory rule today adds mutants on changed *definition* lines, open verdicts, missing rows and
observed ones. A kill whose *check* changed is not among them.

| Inventory (sidecar) | record head → item head | inventory | record kills | killed at a changed check | already in | would join |
|---|---|---|---|---|---|---|
| et-4b-et-4b-c081844 (11-08, pending run) | a97072e601 → ee7646c4d3 | 8 | 326 | 0 | 0 | 0 |
| df-5-df-5-c050431 (run 11-08 05:33) | 66190bd0ce → 6f09a20879 | 81 | 389 | 0 | 0 | 0 |
| et-4b-et-4b-c050416 (run 11-05 09:36) | 01d9048bc2 → 6ece790384 | 41 | 316 | 1 | 0 | 1 |
| pc-1g-pc-1g-c050449 (run 11-05 07:29) | 85660f9155 → a38ebdf513 | 1 | 125 | 4 | 0 | 4 |
| pc-1g-pc-1g-f3 / f3b | a38ebdf513 → 17664656c9 | 0 / 0 | 1 / 0 | 0 | 0 | 0 |

The three most recent targeted runs with a record are df-5-c050431, et-4b-c050416 and pc-1g-c050449. Their
mac-pytest.jsonl rows: et-4b 2026-11-05T09:36:36Z vm rc 4 exec_s 5247 (partial, cloud deadline); pc-1g
2026-11-05T07:29:38Z ve-mac-1 rc 0 exec_s 981. The df-5 record has no ve-df-5 row since 11-05 (it ran under
another worktree name; not traced). Across them, 5 of 830 record kills sat at a changed check line, and none of
the 5 was in its inventory. So yes: all 5 would have joined under a changed-check-line rule, and none joined under
today's rule. None was a lost kill: each one has a KILLED verdict again in a later full record of the same branch,
both later than the item head (`git merge-base --is-ancestor`):
- et-4b M424 `VE.Events.routeView` list-drop-first, killed at RouteExamples.lean:315–319 (the hunk at old lines
  319–320 changed). In the full record et-4b-rebase-20261108 (head a97072e601) the same mutant is M441, KILLED at
  RouteExamples.lean:314.
- pc-1g M041, M090, M128, M209 `VE.Service.Document.environmentOf`, killed at ChainExamples.lean:203/214. In the
  record committed at main (head 8929d200ea) all four are KILLED again, at :203/:215.

The routeView case (et-4b's stopped sweep, et-4b-stopped-fullsweep-20261105.log lines 21–22, at HEAD 6ece7903):
append-left and append-right on Wire.lean:270 were UNKNOWN at RouteExamples.lean:91 ("could not elaborate it in
the probe"). `git diff -U0 01d9048bc2 6ece790384 -- lean/VE/Events/RouteExamples.lean lean/VE/Events/Wire.lean`
shows Wire.lean unchanged and RouteExamples.lean changed only at old 289–290 and 319–320, so line 91 is the same
line on both sides. In the record, those two mutants (M036, M041) were KILLED at WireExamples.lean:406 and :409,
which are unchanged. A changed-check-line rule would not have added them: they joined only through
et-4b-observed.json ("observed in the stopped sweep"), and the targeted run killed them again (M038, M043 at
WireExamples.lean:406/409). The one routeView mutant such a rule would add is a different one, M424 above. The
inventory rule is not changed in this item.

## FOLLOW-UP

Row **tm-inventory-flag-ma** (manage-agents, blocked by this item): tm-inventory.py passes `--only @<ids file>`
and drops the MARK line and `restore`; tm-shard.sh and mac-pytest.sh pass `--only` through to every pool. A
changed-check-line inventory rule, if wanted, is for the decider (5 extra mutants over the runs measured here).

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A., no relayed route touched.
2. Deliverables: (a) commit bbbcec955 (tools/trust_mutants.py); (b) the 3 tests above; (c) this section with
   counts.json; FOLLOW-UP named. PASS. No permanent report test added (D4).
3. Tests can fail: PASS, seeded bugs S1–S3 above.
4. Python/Lean/Rust agree: N.A., no checker code changed.
5. R8 binding: N.A., no relayed answer. The analogue for input binding is that an unknown id is refused:
   test_only_an_id_not_in_the_plan_stops_the_run.
6. Gate evidence: the chain runs tools/gate.py on the final HEAD (not run by the builder, per task).
7. Unsigned items: none; no DELTA row (tooling only, no product output changes).
8. DELTA: N.A., no user-visible checker output changes. Default `--plan` output unchanged:
   test_plan_prints_the_counts_and_builds_nothing.
9. Test selection: PASS. `tools/select_tests.py --base $(git merge-base HEAD main)` selects 173/553 units,
   including tests/test_trust_mutants.py.
10. Lean statements: N.A., no Lean change.
11. Budgets fail closed: N.A., `--only` adds no budget (deadline handling untouched).
12. CPU/memory: N.A. The filter is one pass over the plan, and the default path is unchanged.
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions: PASS. Kept ids vs unknown ids (both tests), and `--plan` with vs without `--only`. Spec
    re-read: task (a) "exit 2, listing the unknown ids" against the message `--only: not in the plan: <ids>`;
    "--plan --only prints only the kept mutants" against the counts and `only`.
15. No overclaim: "unchanged" (default plan) cites test_plan_prints_the_counts_and_builds_nothing; "none was a
    lost kill" cites the later records named above. No deliverable was cut.
