# et-3c build report: conservativity and fixture T7

**No DELTA signature is reserved.** The one delta (trust S +10) is SIGNED by standing ruling R16 (DELTA.md row 1).
`embeddable_sound` stays the DRI's (et-3b's counterexample). **ET-4 uses it**, so ET-4 and M8 wait for the
DRI's amendment (below).

Item: feature item et-3c (rank 35 of the feature feed, acting DRI dri-featurefeed, 2026-10-18), the third part of
ET-3 as `docs/events-time-causation/et-3b/REPORT.md` ("Next item: et-3c") lists it. Plan and spec on main
(`docs/spec/events-time-causation-PLAN.md` section 5 "ET-3", 2.1 to 2.5, 2.9, 3.1, 3.2, fixture T7; spec 1.6, 6.1,
6.2), unchanged. DRI-DECISIONS-PHASE2 ET1 to ET4 were read, and none of them changes this item. Branch
`feature/et-3c` from main e14d56df9.

## Statement gate

The phase-2 check accepted the ET-3 statements (et-3's report). et-3b's script
(`docs/events-time-causation/et-3b/evidence/statements-diff.py.txt`, run with this root) compares every 6.1 and 6.2
declaration after whitespace normalisation. Result: 70 exact, 0 differ, 3 not built
(`evidence/statements.json`). The 70 include `oldEnv`, `DayExtension` and `events_conservative`. The 3 not built are
`embeddable_sound`, `embeddable_complete` and `eventsPremises_satisfiable`. No statement and no `EventsTyped` changed.

## Plan rows

| Row (ET-3, et-3c's part) | Delivered | Where |
|---|---|---|
| `Conservative.lean`: `oldEnv`, `events_conservative`, `dateName_inj` | yes, restored verbatim from 7b1fdb277 | 15fbd0087 |
| fixture T7 | yes, the T7 block of ae3ed63dd, verbatim | 15fbd0087 (`Examples.lean`) |
| `eventsPremises_satisfiable` | **no**: et-3cb (size) | — |
| `embeddable_complete` | **no**: et-3cb (size). It holds as approved without the amendment (below) | — |
| `embeddable_sound` | **no**: et-3d, after the DRI's amendment (task) | et-3b's counterexample |
| `lean/EVENTS.md` in plain words | yes | afaa0097b |
| seeded bugs for the new definitions | yes, 6 mutants | `mutants.json`, 7c67d5d46 |
| R16 row | yes, DELTA.md row 1 (S +10) | 07ad5efab |
| `python3 lean/audit.py`, `tools/regen_generated.py --check` | PASS (595 files; 31 entries, `route-cases` skipped locally because it needs the Rust binary; the gate runs it) | Tests |

`embeddable_complete` needs no year bound. Its hypothesis `Embeds` already numbers every day within `0..dateMax`,
and `EventsTyped` orders consecutive dates. So every count of step 4 of 1.6 is bounded by the numbers that injective
day numbers can take. That is a pigeonhole proof over lists, without Mathlib, and it does not fit in this item's size.

## Does ET-4 use `embeddable_sound`? Yes.

ET-4 has four answer-level theorems in spec 6.3: `events_model_calendar`, `events_witness_calendar`,
`events_settled_calendar` and `events_undecided_calendar`. Each assumes only `hT : EventsTyped …` and
`he : embeddable V M = true`. Each concludes `CalendarReading V (completion V M (numbering V M)) …`.
`completion_reading` gives that conclusion only from `Embeds V M.asStructure (numbering V M)`, and `embeddable_sound`
is the theorem that turns `he` into it. The 10000-01-01 situation of `Examples.lean` has `EventsTyped` and
`embeddable`. Its conclusion cannot hold: a calendar reading of the completion under `numOf (numbering V M)` would
restrict to an embedding of `M` by `numbering`, and the fixture proves that no numbering embeds it. So each of the
four is false as approved for any document whose other hypotheses this situation meets. That last step is not
mechanised here. **M8 (the ET-6 pilot) waits for the DRI's amendment.** An amendment
inside `EventsTyped` (adding `decide (D.year ≤ 9999)`) repairs all five statements at once. A hypothesis added to
`embeddable_sound` alone would leave the four ET-4 statements to amend separately. Both points are in FOLLOW-UPS
"## et-3c".

## Size

`git diff --numstat e14d56df9`, without generated files: `Conservative.lean` +409 (restored), `Examples.lean`
+38/−1, `lean/EVENTS.md` +23/−11, `tools/trust-classes.json` +16, the harness +52, and this report and DELTA.md
(+170). That makes about 720 hand-written lines, against the size rule's ~600; the code and fixtures alone are 447. Generated files are left out:
`lean/{declarations,statements,axioms,predicates}.txt`, `lean/VE/Audit.lean` and `docs/trust-baseline.json` (written
by `--allow`). The script outputs `evidence/statements.json` and `mutants.json` are also left out. The restored file
is one unit, because T7 and the proof need all of it. So the cut is everything else: `eventsPremises_satisfiable` and
`embeddable_complete` go to **et-3cb**.

## Seeded bugs (Lean; `mutants.json`, harness `evidence/seeded-bugs-harness.py.txt`)

Each mutant was applied alone to the committed tree at 15fbd0087. `lake build VE.Events.Examples` failed for all six.
The six events files were then elaborated as one scratch file, so every fixture also runs past a broken proof. Each
mutant was restored after its run.

| Mutant | Definition | Fails |
|---|---|---|
| `oldEnv-keeps-links` | `oldEnv` (new, S) | `events_conservative`; `#guard (oldEnv envT7 vT7).predicates "admires" == … && ["before", "committed_on", "contributed_to"].all …` |
| `oldEnv-keeps-day-predicates` | `oldEnv` | `events_conservative`; the same T7 `#guard` (`before`, `committed_on`) |
| `oldEnv-keeps-day-constants` | `oldEnv` | `events_conservative`; `#guard … constants "the_day" == none` |
| `oldEnv-keeps-day-sort` | `oldEnv` | `events_conservative`; `#guard (oldEnv envT7 vT7).sorts == ["person", "act"]` |
| `expansion-before-reflexive` | `expansion` (P helper) | `events_conservative` (the expansion embeds its days) |
| `firstDay-zero` | `firstDay` (P helper) | `events_conservative` (author day constants denote a day) |

The one new trusted definition (`oldEnv`) has four mutants, and none survives. Python and Rust: no product code
changed (`tools/trust-classes.json` is a data table), so there is no seeded bug in either.

## Trust

`uv run python tools/trust_map.py --check` on the final tree, against merge base e14d56df9: K +0, **S +10**, untied V
+0, unclassified +0. All of it is in `VE/Events/Conservative.lean`: `oldEnv` (lines 15 to 23 with its docstring; the
tool counts 10). This is SIGNED by standing ruling R16. The allowance is in `docs/trust-baseline.json`, and FOLLOW-UPS
"## et-3c" asks for the ties pass. `expDays`, `firstDay` and `expansion` are classed P, as in et-3b's ae3ed63dd.

## Pilot bytes

0 (infrastructure); nothing is reachable from a route until ET-4. ET-6's estimate (UDHR 201 to 548 B) depends on
et-3cb, et-3d (the DRI's amendment), ET-4, ET-5 and `infra/oom-rootcause`. Nothing is claimed before a pilot audit.

## Next items

- **et-3cb**: `embeddable_complete` and `eventsPremises_satisfiable`. The second's planned proof takes the named
  dates' days in date order as the situation (the finite form of `expansion`) and gets `embeddable` from the first.
- **et-3d**: `embeddable_sound`, after the DRI amends it (`reviews/escalations-20261019.md`).
- **et-4**: after et-3cb, et-3d and ar-10a. Its answer theorems need `embeddable_sound` (above).

## Overlap with branches in flight

Files touched by hand: `lean/VE/Events/{Conservative,Examples}.lean`, `lean/EVENTS.md`, `tools/trust-classes.json`
and `docs/events-time-causation/et-3c/*`. No branch in `lean-first/*`, `feature/*`, `infra/*` or `foundation/*`
touches `lean/VE/Events/` or `lean/EVENTS.md` against main. `tools/trust-classes.json` and `docs/trust-baseline.json`
are JSON ledgers with the `ve-generated` merge driver. `lean/VE.lean` is unchanged: `Examples.lean` imports the new
module.

## Tests

- Selected tests on the Mac runner (`zsh manage-agents/mac-pytest.sh --select -- --base e14d56df9 --run`, HEAD
  07ad5efa, clean tree): 80 of 457 units, 0 failed, exit 0. The run includes `lake build`, `lean/audit.py`,
  `test_trust_budget.py`, `test_trust_ratchet.py`, `test_regen_generated.py`, `test_repo_map.py`,
  `test_wire_gate_corpus.py`, `test_p0_three_way.py` and `test_lean_audit_record.py`.
  `tests/test_readings_defaults_rd8_report.py` is in main-known-red (lf-14d's). It was selected and passed. It is not
  touched here.
- Run locally: `python3 lean/audit.py` PASS (595 files). `uv run python tools/regen_generated.py --check --skip
  route-cases` passes 31 entries. `tools/repo_map.py --check` PASS. `uv run python tools/gate_collection.py --check
  --prebuilt` reports 18411 collected, 0 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- The full gate is the chain's, on the final HEAD, and was not run here, as the task directs. Commits after the
  selected run change only this report.

## Acceptance items

All AGENT. None HUMAN or EXTERNAL. The `embeddable_sound` amendment is the DRI's (FOLLOW-UPS "## et-3b", "## et-3c").

## Commits

`git log --oneline main..HEAD --no-merges` at the time of writing: 15fbd0087, 7c67d5d46, afaa0097b, 07ad5efab, and
the report commit that adds this file.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no route, relay or service answer is added (nothing reachable before ET-4).
2. Every deliverable built or moved: PASS, see the plan-row table. `eventsPremises_satisfiable` and
   `embeddable_complete` move to et-3cb under the feed's size rule, and `embeddable_sound` to et-3d under the task.
   Rule-break grep: no Python or Rust copy of a decision, no new report test, no hand-written file shared with an
   in-flight branch.
3. Tests can fail: PASS, 6 mutants (`mutants.json`), each failing `events_conservative`; the four on `oldEnv` also
   fail a named T7 `#guard`. None fails only at a hash or build step: the scratch run names the failing declarations.
4. Py/Lean/Rust agree, valid inputs pass: N.A., no Python or Rust path. T7 has accepted cases (`WellFormedEvents`, the
   typed claims, the entailment with the block) and refused ones (the claim that does not follow, both ways).
5. R8 binding: N.A., no relayed field.
6. Gate evidence matches final HEAD: PASS for the parts run here. The selected run was on 07ad5efa, and the later
   commit adds only this report. The full gate is the chain's on the final HEAD. Evidence is saved files, not live git.
7. No unsigned item: PASS. DELTA.md row 1 cites R16 with its mutants and FOLLOW-UPS row. No signature is reserved.
8. Every user-visible change in DELTA: PASS, nothing reachable changes (`tests/test_wire_gate_corpus.py`,
   `tests/test_p0_three_way.py` pass in the selected run). Trust growth is row 1.
9. Test selection finds breaking tests: PASS. With `oldEnv-keeps-links` planted, `tools/select_tests.py --base
   e14d56df9` selects 80 of 457 units, including `lake build`, which fails under that mutant.
10. Lean statements say what is claimed: PASS. `evidence/statements.json` shows 70 exact and 0 differing.
    `events_conservative` breaks under every mutant. No hypothesis is added.
11. Budgets fail closed: N.A., no budgeted operation is added.
12. No CPU or memory regression: N.A., nothing is on a route or pilot path. `lake build VE.Events.Examples` takes
    seconds.
13. Removed tests carry a trailer: PASS, no test removed. `tools/gate_collection.py --check --prebuilt` reports 0
    removed, 0 stale and 0 malformed.
