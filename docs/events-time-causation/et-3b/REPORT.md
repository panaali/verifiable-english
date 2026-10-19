# et-3b build report: the completion and the typing theorems

**Statement gate: `embeddable_sound` as approved does not hold.** It is not built, and its amendment needs the DRI
before et-3c builds it (FOLLOW-UPS "## et-3b"). The counterexample is mechanised in `lean/VE/Events/Examples.lean`.
No DELTA signature is reserved: the one delta (trust S +27) is SIGNED by standing ruling R16 (DELTA.md row 1).

Item: feature item et-3b (rank 30 of the feature feed, acting DRI dri-featurefeed, 2026-10-18), the second half of
ET-3 as `docs/events-time-causation/et-3/REPORT.md` ("et-3b (next item)") lists it. Plan and spec: on main at
e010fb6aa (`docs/spec/events-time-causation-PLAN.md` section 5 "ET-3", 2.1 to 2.5, 2.9, 3.1, 3.2, fixture T7; spec
1.2 to 1.8, 6.1, 6.2), unchanged. DRI-DECISIONS-PHASE2 ET1 to ET4 read: none changes this item (ET3 limits ET-T1 to
day and week offsets; nothing here states an offset). Branch `feature/et-3b` from main e010fb6aa.

## Statement gate

The phase-2 check accepted the ET-3 statements (et-3's report). Every declaration built here is the approved text,
whitespace aside: 68 of the 6.1 and 6.2 declarations built so far are exact, 0 differ, 5 are not built
(`evidence/statements.json`, script `evidence/statements-diff.py.txt`, the et-3 script with the root as argument).

**`embeddable_sound` is false as approved.** `EventsTyped` requires each named date to be proper but sets no year
bound (`WellFormedEvents` has `D.year ≤ 9999`; `EventsTyped` does not). Take one named date 10000-01-01 and a
situation whose one day `x` it names. Then `EventsTyped` holds and `calendarCheck` passes: there is no gap, and
after the last date the check allows `dateMax − Dk.num`, which is 0 in Nat. But `numbering` gives `x` the number
`dateMax + 1`, and `Embeds` needs at most `dateMax`. The fixtures at the end of `Examples.lean` check this: one
`#guard` (`EventsTyped`, `embeddable`, `numbering … == dateMax + 1`) and an `example` proving that **no** numbering
embeds the situation. So "embeddable exactly when some numbering embeds" (1.6) fails as well. Possible amendments,
for the DRI: add `decide (D.year ≤ 9999)` to `EventsTyped` (the decoder already parses only such dates), or give
`embeddable_sound` that hypothesis. The task says to stop and report on a statement that must change. I stopped on
that statement only: the other statements are independent of it and are built as approved.

## Plan rows

| Plan row (ET-3, et-3b's half) | Delivered | Where |
|---|---|---|
| `completion` (`numOf`, `oldTuple`, `addedDay`, `isDayC`), `CalendarReading` | yes | 7e1f46270 (`Completion.lean`, `Premises.lean`) |
| `completion_extension`, `completion_reading`, `completion_admissible` | yes | 7e1f46270 |
| `regen_typed`, `eventsPremises_wellFormed`, `conventions_exact` | yes | d9413cbd6 |
| `embeddable_sound` | **no**: false as approved (above); et-3c after the DRI's amendment | counterexample in ae3ed63dd |
| `embeddable_complete`, `eventsPremises_satisfiable` | **no**: et-3c (size) | — |
| `Conservative.lean` (`oldEnv`, `events_conservative`), fixture T7 | **proved, then moved to et-3c for size** (see Size) | 7b1fdb277 (with `dateName_inj`), T7 in ae3ed63dd; removed in de6b8eb57 |
| `lean/EVENTS.md` in plain words | yes | de6b8eb57, 1197a360a |
| seeded bugs for the new definitions | yes, 9 mutants (below) | `mutants.json` |
| R16 row | yes, DELTA.md row 1 (S +27) | DELTA.md |
| `python3 lean/audit.py`, `tools/regen_generated.py --check` | PASS (574 files; 30 entries, `route-cases` skipped locally: it needs the Rust binary, the gate runs it) | Tests |

Proof helpers (class P, not in 6.2): `oldTuple_map`, `oldTuple_eq`, `completion_before_new`, `completion_typed`,
`startRole_mem`, `boundRole_mem`. Fixtures added: the completion's pieces (`oldTuple`, `numOf`, `addedDay`, `isDayC`
on T3's situation), "a finite situation is never a calendar reading" (`¬ CalendarReading`), and the counterexample.

## Size

Measured with `git diff --numstat $(git merge-base HEAD main)` without the generated files: `Completion.lean` +199,
`Premises.lean` +105, `Examples.lean` +34, `lean/EVENTS.md` +35/−14, `tools/trust-classes.json` +14/−3, evidence
scripts +86, plus DELTA.md and this report. That is about 600 lines.

The proofs ran longer than et-3's estimate. With `Conservative.lean` (409 lines) and T7 included, the item measured
945 lines, so I cut them as the feed's size rule asks. The cut is a commit, not a rewrite, so the proofs stay in the
branch history. et-3c restores them with
`git show 7b1fdb277:lean/VE/Events/Conservative.lean` and the T7 block of `ae3ed63dd:lean/VE/Events/Examples.lean`.
Both built and passed then: `events_conservative` exact against 6.2, T7's guards and example, and the mutants
`oldEnv-keeps-links` and `oldEnv-keeps-day-constants`, each failing `events_conservative` and a T7 guard.

## Seeded bugs (Lean; `mutants.json`, harness `evidence/seeded-bugs-harness.py.txt`)

Each was applied alone to the committed tree. `lake build VE.Events.Examples` failed for all nine. The five events
files were then elaborated as one scratch file, so every fixture also runs past a broken proof. Each mutant was
restored after its run.

| Mutant | Definition | File | Fails |
|---|---|---|---|
| `numOf-shift` | `numOf` (new, S) | `lean/VE/Events/Completion.lean` | `completion_reading`; `#guard numOf …` |
| `oldTuple-added-old` | `oldTuple` (new, S) | same | `oldTuple_eq`, `completion_reading`; `#guard oldTuple ([.inl "a", .inr 3] …) == none …` |
| `addedDay-no-bound` | `addedDay` (new, S) | same | `completion_reading`; `example : ¬ addedDay vT3 mC numC (dateMax + 1)` |
| `isDayC-any-old` | `isDayC` (new, S) | same | `completion_reading`, `completion_admissible`; `example : isDayC … ∧ ¬ isDayC …` |
| `completion-added-any-sort` | `completion` (new, S) | same | `completion_extension`, `completion_reading`, `completion_admissible` |
| `completion-added-any-predicate` | `completion` (new, S) | same | `completion_extension`, `completion_admissible` |
| `calendarReading-not-onto` | `CalendarReading` (new, S) | `lean/VE/Events/Premises.lean` | `completion_reading`; `example : ¬ CalendarReading vT3 mC.asStructure numC` |
| `oneRole-before-guard` | `oneRoleF` (et-3's; claim `conventions_exact`, `eventsPremises_wellFormed`) | same | `eventsPremises_wellFormed`, `conventions_exact`; F1's and T4's guards |
| `regen-date-sort` | `regenEnv` (et-3's; claim `regen_typed`) | `lean/VE/Events/Decl.lean` | `regen_typed`; T1's `regenEnv` and `EventsTyped` guards |

Every new trusted definition has a mutant, and none survives. Python and Rust: no product code changed (only
`tools/trust-classes.json`, a data table), so no seeded bug there.

## Trust

`uv run python tools/trust_map.py --check` on the final tree, against merge base e010fb6aa:
- K +0, **S +27**, untied V +0.
- `VE/Events/Completion.lean` +23: numOf 3, oldTuple 4, addedDay 2, isDayC 3, completion 9, and 2 header lines.
- `VE/Events/Premises.lean` +4: CalendarReading.

SIGNED by standing ruling R16. The allowance is recorded in `docs/trust-baseline.json`, and the FOLLOW-UPS row
"## et-3b" asks for the ties pass and names et-3c.

## Pilot bytes

0 (infrastructure). Nothing is reachable from a route until ET-4. ET-6's estimate (UDHR 201 to 548 B) depends on
et-3c, ET-4, ET-5 and `infra/oom-rootcause`. Nothing is claimed before a pilot audit.

## Next item: et-3c

- `embeddable_sound` (after the DRI amends its statement) and `embeddable_complete`: these tie `calendarCheck`,
  `embeddable` and `numbering`.
- `eventsPremises_satisfiable`.
- `Conservative.lean` (`oldEnv`, `events_conservative`, `dateName_inj`) and T7, restored from this branch's history.

ET-4 waits for et-3c as well as ar-10a.

## Overlap with branches in flight

Files touched by hand: `lean/VE/Events/{Premises,Completion,Examples}.lean`, `lean/EVENTS.md` and
`docs/events-time-causation/et-3b/*`. No in-flight branch touches these. The shared files are `lean/VE.lean`
(append-only; this item's net change is none, because the Conservative import is gone) and `tools/trust-classes.json`
and `docs/trust-baseline.json` (JSON ledgers with the `ve-generated` merge driver). Several branches also touch
these shared files (`feature/me-5`, `feature/me-6`, `feature/sc-3a`, `foundation/me-1`, `lean-first/b18` and
others), and the merge drivers handle them.

## Tests

- Selected tests on the Mac runner (`zsh manage-agents/mac-pytest.sh --select -- --base e010fb6aa --run`, HEAD
  1197a360, clean tree): 67 of 447 units, 0 failed. The run includes `lake build`, `lean/audit.py`, the Rust build,
  `test_trust_budget.py`, `test_trust_ratchet.py`, `test_frozen_sources.py`, `test_wire_gate_corpus.py`,
  `test_p0_three_way.py`, `test_regen_generated.py`, `test_lean_audit_record.py` and `test_repo_map.py`.
- Run locally: `python3 lean/audit.py` PASS. `uv run python tools/regen_generated.py --check --skip route-cases`
  passes 30 entries. `tools/repo_map.py --check` PASS. `uv run python tools/gate_collection.py --check --prebuilt`
  reports 18189 collected, 0 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- The full gate is the chain's, on the final HEAD; it was not run here, as the task directs. No main-known-red test
  was selected.

## Acceptance items

All AGENT. None HUMAN or EXTERNAL. The `embeddable_sound` amendment is the DRI's (FOLLOW-UPS).

## Commits

`git log --oneline main..HEAD --no-merges` at the time of writing: 7e1f46270, d9413cbd6, 7b1fdb277, ae3ed63dd,
da3284245, 0bf6a9244, abf139686, de6b8eb57, 4a5cfe1ab, 1197a360a, and the report commit
that adds this file.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no route, relay or service answer is added (nothing reachable before ET-4).
2. Every deliverable built or moved: PASS, see the plan-row table. The moved rows go to et-3c under the feed's size
   rule, and `embeddable_sound` under the statement gate. Rule-break grep: no Python or Rust copy of a decision, no
   new report test, no hand-written file shared with an in-flight branch.
3. Tests can fail: PASS, 9 mutants (`mutants.json`), each failing named proofs and, for all but the two `completion`
   mutants, a named fixture. None fails only at a hash or build step: the scratch run names the failing declarations.
4. Py/Lean/Rust agree, valid inputs pass: N.A., no Python or Rust path. The Lean fixtures include accepted cases
   (`addedDay` of 13 October, `isDayC` of a day) and refused ones.
5. R8 binding: N.A., no relayed field.
6. Gate evidence matches final HEAD: PASS for the parts run here. The selected run was on 1197a360, and later
   commits change only this report. The full gate is the chain's on the final HEAD. Evidence is saved files, not
   live git.
7. No unsigned item: PASS. DELTA.md row 1 cites R16 with its mutants and FOLLOW-UPS row. No signature is reserved.
   The `embeddable_sound` statement change is reported in the first line and not built.
8. Every user-visible change in DELTA: PASS, nothing reachable changes (`tests/test_wire_gate_corpus.py`,
   `tests/test_p0_three_way.py` pass in the selected run). Trust growth is row 1.
9. Test selection finds breaking tests: PASS, 67 of 447 units selected (not all). The selection runs `lake build`,
   which fails under each seeded mutant.
10. Lean statements say what is claimed: PASS. `evidence/statements.json` shows 68 exact and 0 differing. Each new
    theorem breaks under a mutant (`completion_*`, `regen_typed`, `eventsPremises_wellFormed`, `conventions_exact`).
    No hypothesis is added. The one false statement is reported, not weakened.
11. Budgets fail closed: N.A., no budgeted operation is added.
12. No CPU or memory regression: N.A., nothing is on a route or pilot path. `lake build VE.Events.Examples` takes
    under a minute.
13. Removed tests carry a trailer: PASS, no pytest test removed. `tools/gate_collection.py --check --prebuilt`
    reports 0 removed, 0 stale and 0 malformed. The moved Lean fixture T7 is not a collected test.
