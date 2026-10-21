# et-3cb build report: `embeddable_complete` and `eventsPremises_satisfiable`

**No DELTA signature is reserved, and there is no DELTA row** (DELTA.md: no user-visible change, trust +0).
`embeddable_sound` stays et-3d's, waiting for the DRI's amendment (et-3b's counterexample,
`reviews/escalations-20261019.md`).

Item: feature item et-3cb (rank 42 of the feature feed, acting DRI dri-featurefeed, 2026-10-18), the last two theorems
of ET-3 apart from et-3d, as `docs/events-time-causation/et-3c/REPORT.md` ("Next items") names them. Plan and spec
on main (`docs/spec/events-time-causation-PLAN.md` section 5 "ET-3", 2.1 to 2.5, 2.9, 3.1, 3.2; spec 1.6, 6.1,
6.2), unchanged since the pinned commit c5197da78. DRI-DECISIONS-PHASE2 ET1 to ET4 were read, and none of them
changes this item. Branch `feature/et-3cb` from main 7c85297ea.

## Statement gate

The phase-2 check accepted the ET-3 statements (et-3's report). et-3b's script
(`docs/events-time-causation/et-3b/evidence/statements-diff.py.txt`, run with this root) compares every 6.1 and 6.2
declaration after whitespace normalisation. Its unedited output is `evidence/statements.json`: 72 exact, 0 differ,
1 not built. `embeddable_complete` and `eventsPremises_satisfiable` are among the 72. The one not built is
`embeddable_sound`. No statement and no `EventsTyped` changed. No hypothesis was added.

## Plan rows

| Row (ET-3, et-3cb's part) | Delivered | Where |
|---|---|---|
| `embeddable_complete` (6.2) | yes, proved as approved. It needs no year bound. The proof is a pigeonhole count over lists, without Mathlib | d89e7436a, `Calendar.lean` |
| `eventsPremises_satisfiable` (6.2) | yes, proved as approved. The situation is the named dates' days in date order (`datesSituation`, the finite form of `expansion`). `embeddable` comes from `embeddable_complete` | dad6318c2, `Conservative.lean` |
| fixtures | `#guard`s on `datesSituation` for T4's block, T7's, R1's dates and no date, plus an instance of `eventsPremises_satisfiable` on T7 | dad6318c2, `Examples.lean` |
| `lean/EVENTS.md` in plain words | yes | e799551b4 |
| a seeded bug per theorem | yes: six mutants, three per theorem, each breaking the proof and a `#guard` | `mutants.json` |
| R16 row "only if a new trusted definition is needed" | not needed: trust +0, and the new definitions are proof helpers (P) | DELTA.md |
| `embeddable_sound` | **no**: et-3d, after the DRI's amendment (task) | et-3b's counterexample |
| `python3 lean/audit.py`, `tools/regen_generated.py --check` | PASS. The audit covers 599 files. `regen_generated --check --skip route-cases` checks 31 entries; `route-cases` needs the Rust binary, so the gate runs it | Tests |

**How `embeddable_complete` goes.** Take a numbering `num` that embeds `M`. A day's `rank` is then the number of days
with a smaller number, because `before` on days is `<` on numbers. `countP_eq_le_one`: a number is taken by at most
one day, since `num` is one-to-one on a list with no repeat. Hence `countP_lt_le`: at most `k` days have a number in
`a..a+k-1`. That bounds every count of step 4 of 1.6 (before `D₁`, between consecutive dates, after `Dk`, no date).
`countP_lt_lt`: a named day is counted below every later named day, so step 3 passes. Steps 1 and 2 come directly
from `Embeds` and `hn`. `valid` is not used, and neither is any year bound.

## Size

`git diff --numstat 7c85297ea`, without generated files (`lean/{declarations,statements,axioms}.txt`,
`lean/VE/Audit.lean`):

- product code and fixtures: `Calendar.lean` +130, `Conservative.lean` +148/−2, `Examples.lean` +19/−1,
  `tools/trust-classes.json` +4/−1;
- docs: `lean/EVENTS.md` +26/−13;
- evidence: the harness +71;
- this report and DELTA.md: about +120.

That makes about 535 hand-written lines, against the size rule's ~600. The two script outputs are another 205
lines: `evidence/statements.json` (85) and `mutants.json` (120). They are printed by the saved scripts and committed
unedited; with them counted, the total is about 740. The work is one coherent unit: the second theorem uses the
first. No part is cut.

## Seeded bugs (Lean; `mutants.json`, harness `evidence/seeded-bugs-harness.py.txt`)

Each mutant was applied alone to the committed tree at dad6318c2, and `lake build VE.Events.Examples` failed for all
six. The six events files were then elaborated as one scratch file, so the fixtures also run past a broken proof.
Each mutant was restored after its run. `mutants.json` is the harness's output, unedited (`failing` and `test` are
computed from Lean's error lines).

| Mutant | File | Theorem | Fails |
|---|---|---|---|
| `calendarCheck-gap-bound-minus-two` | `Calendar.lean` | `embeddable_complete` | its proof; T3 `#guard calendarCheck vT3 (chain ["a", "x1", "b"] …) == none` |
| `calendarCheck-first-bound-strict` | `Calendar.lean` | `embeddable_complete` | its proof; T3e `#guard calendarCheck (base [d 1970 1 1]) (chain ["a", "x"] …) == none` |
| `rank-counts-the-day-itself` | `Calendar.lean` | `embeddable_complete` | its proof; the three T3e `#guard`s |
| `datesSituation-before-reflexive` | `Conservative.lean` | `eventsPremises_satisfiable` | its proof; four `#guard`s of the pack alone (T4's premises and its day order, T7, R1) |
| `datesSituation-day-constant-unnamed` | `Conservative.lean` | `eventsPremises_satisfiable` | its proof; `#guard (datesSituation envT7 vT7).constants "the_day" == some ("day", c12) && …` |
| `dayNames-no-day-without-dates` | `Conservative.lean` | `eventsPremises_satisfiable` | its proof; `#guard (datesSituation envDay (base [])).domains "day" == [("day", "")] && …` |

Python and Rust: no product code changed (`tools/trust-classes.json` is a data table), so there is no seeded bug in
either. R16's per-definition mutants: no new trusted definition (Trust), so none is required. The three new P
definitions each have mutants anyway (rows 4 to 6).

## Trust

`uv run python tools/trust_map.py --check` on the final tree, against merge base 7c85297ea: K +0, S +0, D +0, G +0,
tied +0, unclassified +0, trusted +0, PASS. `dayNames`, `firstName` and `datesSituation` are classed P in
`tools/trust-classes.json`, as `expansion` is, because a wrong witness only makes the existential proof fail. The
lemmas are theorems. No allowance, R16 row or FOLLOW-UPS row is needed. `tools/trust_mutants.py` (checklist 13a)
applies only to trusted growth, so it was not run.

## Pilot bytes

0 (infrastructure). Nothing is reachable from a route until ET-4. ET-6's estimate (UDHR 201 to 548 B) depends on
et-3d (the DRI's amendment), ET-4, ET-5 and `infra/oom-rootcause`. Nothing is claimed before a pilot audit.

## Next items

- **et-3d**: `embeddable_sound`, after the DRI amends it (`reviews/escalations-20261019.md`). `embeddable_complete`
  now gives the converse.
- **et-4**: after et-3d and ar-10a. Its answer theorems need `embeddable_sound` (et-3c's report).

## Overlap with branches in flight

Files touched by hand: `lean/VE/Events/{Calendar,Conservative,Examples}.lean`, `lean/EVENTS.md`,
`tools/trust-classes.json` and `docs/events-time-causation/et-3cb/*`. No branch in `lean-first/*`, `feature/*`,
`infra/*` or `foundation/*` touches `lean/VE/Events/` or `lean/EVENTS.md` against main. `lean/VE.lean`, which four
branches touch, is unchanged: `Conservative.lean` now imports `Calendar.lean` (it used to import `Premises.lean`, which
`Calendar.lean` imports). `tools/trust-classes.json` uses the `ve-generated` merge driver.

## Tests

- Selected tests on the Mac runner (`zsh manage-agents/mac-pytest.sh --select -- --base 7c85297ea --run`, HEAD
  e799551b, clean tree): 78 of 459 units, 0 failed, exit 0. The run includes `lake build`, `lean/audit.py`,
  `test_trust_budget.py`, `test_trust_ratchet.py`, `test_regen_generated.py`, `test_repo_map.py`,
  `test_wire_gate_corpus.py`, `test_p0_three_way.py` and `test_lean_audit_record.py`.
  `tests/test_readings_defaults_rd8_report.py` is in main-known-red. It was selected and passed, and this item does
  not touch it.
- Run locally: `python3 lean/audit.py` PASS (599 files). `uv run python tools/regen_generated.py --check --skip
  route-cases` passes 31 entries. `tools/repo_map.py --check` PASS. `uv run python tools/gate_collection.py --check
  --prebuilt` reports 18947 collected, 0 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- The full gate is the chain's, on the final HEAD, and was not run here, as the task directs. The only commit after
  the selected run adds DELTA.md and this report.

## Acceptance items

All AGENT; none HUMAN or EXTERNAL. The `embeddable_sound` amendment is the DRI's (FOLLOW-UPS "## et-3b", "## et-3c").

## Commits

`git log --oneline main..HEAD --no-merges` when this was written: d89e7436a, dad6318c2, e799551b4, and the report
commit that adds this file and DELTA.md.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no route, relay or service answer is added (nothing reachable before ET-4).
2. Every deliverable built, no rule broken: PASS, see the plan-row table. Both theorems are proved as approved
   (`evidence/statements.json`). Rule-break grep of `git diff main...HEAD`: no Python or Rust copy of a decision, no
   new report test, no hand-written file shared with an in-flight branch.
3. Tests can fail: PASS. Six mutants (`mutants.json`), three per theorem, each failing its proof and a named
   `#guard`. None fails only at a hash or build step: the scratch run names the failing declarations.
4. Py/Lean/Rust agree, valid inputs pass: N.A., no Python or Rust path. The fixtures hold accepted cases (T4, T7, R1,
   no date) beside T3's and T3e's refused ones.
5. R8 binding: N.A., no relayed field.
6. Gate evidence matches the final HEAD: PASS for the parts run here. The selected run was on e799551b, and the later
   commit adds only DELTA.md and this report. The full gate is the chain's, on the final HEAD. The evidence is saved
   files, not live git.
7. No unsigned item: PASS. DELTA.md has no row, and trust is +0 (`tools/trust_map.py --check`).
8. Every user-visible change in DELTA: PASS. Nothing reachable changes (`tests/test_wire_gate_corpus.py` and
   `tests/test_p0_three_way.py` pass in the selected run).
9. Test selection finds breaking tests: PASS. With `dayNames-no-day-without-dates` planted, `tools/select_tests.py
   --base 7c85297ea` selects 78 of 459 units, including `lake build`, which fails under that mutant.
10. Lean statements say what is claimed: PASS. `evidence/statements.json` shows 72 exact and 0 differing, and both
    theorems break under their mutants. No hypothesis was added.
11. Budgets fail closed: N.A., no budgeted operation is added.
12. No CPU or memory regression: N.A., nothing is on a route or pilot path. `lake build VE.Events.Examples` takes
    seconds.
13. Removed tests carry a trailer: PASS, no test was removed. `tools/gate_collection.py --check --prebuilt` reports 0
    removed, 0 stale and 0 malformed.
