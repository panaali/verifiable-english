# et-3d build report: `embeddable_sound`, with `EventsTyped`'s year bound

**Status:** done, ready for the gate. No DELTA signature is reserved: row 1 is SIGNED by the DRI (2026-10-27, item 1; the
condition text was corrected on 2026-10-28), and row 2 cites R16.
**What changed:** `EventsTyped` requires `decide (D.year ≤ 9999)` of every named date (the DRI's amendment), and
`embeddable_sound` is proved as approved, with no extra hypothesis. Every ET-3 statement is now built.
**Open items:** none in ET-3 (no et-3e). Next: et-4. Python, Rust, routes and wire are unchanged. Bytes 0.

Item: feature item et-3d (rank 82 of the feature feed, acting DRI dri-featurefeed, 2026-10-18), amended by the DRI in
`manage-agents/reviews/dri-decisions-20261027-featureplan-gates.md` item 1. Branch `feature/et-3d` from main
b8eac7455. Plan and spec are on main (`docs/spec/events-time-causation-PLAN.md` 5 "ET-3", D5;
`docs/spec/events-time-causation.md` 1.3, 1.6, 6.1, 6.2), so nothing was copied.

## Statement gate

The DRI's decision is the amendment, so the gate is open. The plan's statement review accepted ET-3 (et-3's report).
et-3b's script (`docs/events-time-causation/et-3b/evidence/statements-diff.py.txt`, run with this root) gives
`evidence/statements.json`: **72 exact, 0 not built, 1 differs**. The one that differs is `def EventsTyped`. Its
Lean text is the approved text with `decide (D.year ≤ 9999) && ` inserted after `D.properB && `, and nothing else
(a probe replaces that string in the approved text and compares: equal). `theorem embeddable_sound` is among the
72 exact. The bound broke no other statement. The only re-proof needed was a one-line `simp` set in `regen_typed`;
every other proof that unfolds `EventsTyped` (`calendar_sat`, `datesOrder_iff`, `embeddable_complete`,
`completion_admissible`) builds unchanged. The approved 6.1 text stays as the approved draft. The spec gains
section 13, which records the amendment and its rulings, as rd-6a did for its own.

**The decoder condition.** Item 1 asked for a test that the decoder refuses 10000-01-01 with `DateRange`. On main,
`parseIso` reads a four-digit year only, so it refuses that date with `InvalidDate(10000-01-01)`. I asked the DRI
(`msg.sh dri`). The ruling, `reviews/dri-decisions-20261028-et-3d.md`, corrects the condition to the guards below.
`parseIso`'s texts are unchanged.

## Plan rows and directive lines

| Row | Delivered | Where |
|---|---|---|
| (1) the bound in `EventsTyped`; every touched proof re-checked | yes; `lake build` (all targets) passes, `python3 lean/audit.py` PASS on 647 files | 99b409d5d, `Decl.lean:100`, `Premises.lean:221` |
| (2) `embeddable_sound` as approved, no extra hypothesis | yes; axioms `propext`, `Classical.choice`, `Quot.sound` | 99b409d5d, `Calendar.lean:237` |
| (3a) 10000-01-01 fixture flipped to not `EventsTyped` | `#guard !EventsTyped envX vX && embeddable vX mX && numbering vX mX "x" == dateMax + 1`; the not-embeddable `example` kept | `Examples.lean:298` |
| (3b) the decoders refuse it (DRI 2026-10-28) | `#guard`s: `parseIso "10000-01-01"` is `InvalidDate(10000-01-01)`; civil day 2932897 is `DateRange(2932897)`; day 2932896 is `9999-12-31`; `parseIso "9999-12-31"` is accepted; an `example` from `parseIso_valid` that every date it returns meets the bound | `Examples.lean`, after `vL` |
| (4) seeded bugs: bound dropped, 9998, 10000, one per changed trusted definition | 7 mutants, each breaking a proof and a `#guard` | `mutants.json`, below |
| both sides of each boundary | typed: 9999-12-31, and 9998-12-31 with 9999-01-01; not typed: 10000-01-01 alone, after 9999-12-31, an earlier date without its constant, and an improper earlier date (2026-02-30). The check: one day named 9999-12-31 passes and is numbered `dateMax`, a day before it is numbered `dateMax - 1`, a day after it fails (`1 day after 9999-12-31, at most 0`). `WellFormedEvents` agrees on 9999-12-31, on 10000-01-01 and on the pair | `Examples.lean:305-324` |
| DELTA: amended statement SIGNED by the DRI, its condition tests named; trust under R16 | yes | `DELTA.md` rows 1, 2 |
| R16 FOLLOW-UPS row | yes, `manage-agents/FOLLOW-UPS.md` `## et-3d` | |
| no edit of `lean/VE/Events/Wire` or the events pack | none exists, and none was made | |
| `lean/EVENTS.md` in plain words | yes | 73bd26a36 |

**How `embeddable_sound` goes.** When the check passes, `before` is a strict linear order on the days, so a day's
`rank` is strictly increasing along the order (`countP_lt_of`), and `rank x < n`. Write `numbering x` as
`rank x + h (rank x)`. Here `h k` is the offset `D.num − rank D` of the last named day of rank at most `k`, or that
of the first named day when there is none. Steps 3 and 4 hold along consecutive dates. Through `pairwise_of_chain`
they hold for every pair of dates, as one transitive relation: rank grows, and the offset grows too, once the first
date's rank is at most its number. So `h` never decreases (`rel_getLast`: the last date of a filtered, sorted list
is the greatest). Hence the numbers rise strictly with the order, which gives clauses 1 and 3 of `Embeds`, and a
named day gets its date's number (clause 4). Clause 2 is the bound. The after-gap bound gives
`n − 1 − rank Dk ≤ dateMax − Dk.num`. This equals `n − 1 + Dk.num − rank Dk ≤ dateMax` only when `Dk.num ≤ dateMax`,
which is where the year bound comes in. Without it the subtraction truncates to 0, which is et-3b's counterexample.

## Seeded bugs (Lean; `mutants.json`, harness `evidence/seeded-bugs-harness.py.txt`)

The harness is et-3cb's, with this item's mutants. It applies one mutant at a time to the committed tree 31702358c,
runs `lake build VE.Events.Examples` (it failed for all seven), then elaborates the six events files as one scratch
file so that the guards run past a broken proof, and restores the file. `mutants.json` is its output, unedited. The
two earlier-date guards came later (01ce09bda) and only add checks.

| Mutant | File | Claim | Fails (a `#guard`, plus the proofs) |
|---|---|---|---|
| `EventsTyped-bound-dropped` | `lean/VE/Events/Decl.lean` | the bound | `#guard !EventsTyped envX vX …` (the flipped fixture), the `vX` and `vL2` boundary guards; `embeddable_sound` |
| `EventsTyped-bound-9998` | `lean/VE/Events/Decl.lean` | the bound, off by one below | `#guard EventsTyped (regenEnv envDay vL) vL && …` (9999-12-31), the 9998/9999 guard; `regen_typed`, `embeddable_sound` |
| `EventsTyped-bound-10000` | `lean/VE/Events/Decl.lean` | the bound, off by one above | the flipped fixture, the `vX` and `vL2` guards; `regen_typed`, `embeddable_sound` |
| `EventsTyped-bound-first-date-only` | `lean/VE/Events/Decl.lean` | every named date is bounded | `#guard !EventsTyped (regenEnv envDay vL2) vL2 && …`; five theorems |
| `WellFormedEvents-bound-dropped` | `lean/VE/Events/Decl.lean` | the decoder side (`regen_typed`) | the `vX` and `vL2` guards; `regen_typed`, `events_conservative`, `eventsPremises_satisfiable` |
| `calendarCheck-after-bound-plus-one` | `lean/VE/Events/Calendar.lean` | `embeddable_sound` | `#guard calendarCheck vL (chain ["x", "y"] …) == some "NotCalendar: 1 day after 9999-12-31, at most 0"`, T3e; `embeddable_sound` |
| `numbering-named-offset-plus-one` | `lean/VE/Events/Calendar.lean` | `embeddable_sound` | `#guard embeddable vL (chain ["x"] …) && numbering … == dateMax`, the flipped fixture, T3; `embeddable_sound` |

Python and Rust: no product code changed (`ve/assurance-manifest.json` and `tools/trust-classes.json` are data
tables), so neither has a seeded bug.

## Trust

`uv run python tools/trust_map.py --check` against merge base b8eac7455: **K +0, S +1, D +0, G +0, tied +0,
unclassified +0, trusted +1**, PASS with the allowance `--signed "SIGNED by standing ruling R16 (DRI-RULINGS.md),
et-3d, 2026-10-18"` (`docs/trust-baseline.json`). The +1 is `EventsTyped`'s docstring line, `Decl.lean`.
`vL` and `vL2` are classed T. The trust mutants (checklist 13a) ran via `mac-pytest.sh --trustmut -- --max-mutants
1000 --json docs/events-time-causation/et-3d/trust-mutants.json` on ve-mac-1. The first run had 15 KILLED and 1
SURVIVOR, `list-last` (`V.dates → V.dates.reverse.take 1`), which checks only the last date. The two earlier-date
guards kill it. The rescore (`--rescore` of the same JSON) gives **16 KILLED, 0 SURVIVOR, 0 UNKNOWN**.

## Tests

- `lake build VE.Events.Examples` while iterating; the full `lake build` once (rc 0); `python3 lean/audit.py` PASS.
- `uv run python tools/regen_generated.py --write --skip route-cases` (twice: after the proof and after the
  earlier-date fixtures). `route-cases` needs the Rust release binary, which this worktree lacks; the gate runs it.
  No route changed.
- Selected tests (`mac-pytest.sh --select -- --base b8eac7455 --run`, 87 units): 1 failed,
  `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`. `Examples.lean` now builds
  JSON for the `runConversion` guards. Fixed by an `other_json` entry in `ve/assurance-manifest.json`
  (`tools/assurance_manifest.py --check` passes). After the fix `tests/test_assurance_manifest.py` gives 137 passed.
- Not run, by the task's rules: the full gate (the chain runs it), whole-UDHR runs.

## Size

Hand-written lines (`git diff --numstat b8eac7455`, without generated files): `Calendar.lean` +211,
`Examples.lean` +52, `Decl.lean`, `Premises.lean`, `tools/trust-classes.json` and `ve/assurance-manifest.json` +12,
`lean/EVENTS.md` +38, the spec note +13, DELTA +13, the harness +73, and this report (about 150). That is about
560, under the ~600 rule. The script outputs `statements.json` (89), `mutants.json` (168) and `trust-mutants.json`
(18) are printed by their scripts and committed unedited.

## Pilot bytes

0 (infrastructure). Nothing is reachable from a route until ET-4. ET-5 and ET-6 then move the UDHR's time units
(M8, an estimate of +201 to 548 B). Nothing is claimed before a pilot audit.

## Next items

- **et-4** (the wire and the events pack). Its four answer-level theorems can use `embeddable_sound` as approved.
  The year bound reaches the decoded route through `parseIso_valid`; ET-4 states it on `eventsDecode`'s output.
- **ET-E1** (approved, item 7 of the same decision) before et-5.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No route, relay or response schema changes; Events is unreachable.
2. Deliverables: PASS. Every plan row and directive line is in the table above, with its commit or file. Rule grep of
   `git diff main...HEAD`: no Python or Rust copy of a decision, no report test, no file in flight elsewhere (checked
   against every `feature/*`, `infra/*`, `lean-first/*`, `foundation/*` branch).
3. Tests can fail: PASS. `mutants.json` (7 mutants, each failing a `#guard` and a proof) and `trust-mutants.json`
   (16 KILLED).
4. Py/Lean/Rust agree: N.A. Only Lean changed, and it reaches no route.
5. R8 binding: N.A. No Lean answer is read by Python.
6. Gate evidence on final HEAD: PASS for what I ran. Selected tests ran on 49aaf3606, and the fix
   `tests/test_assurance_manifest.py` (137 passed) on 8b8be806b. The chain runs the gate on the final HEAD.
7. No unsigned item: PASS. `L52_WIDE=1 review-ready.py --delta-dri-needed` gives "No DELTA row reserved for the DRI".
8. Every user-visible change in DELTA: PASS. There is none outside Lean's unreachable Events modules. The amended
   definition and the trust growth are rows 1 and 2.
9. Test selection: PASS. The selection (87 units) includes `lake build` and the audit, which every Lean mutant
   breaks.
10. Lean statements: PASS. `evidence/statements.json` (72 exact, 1 differing by exactly the signed edit). The
    mutants break `embeddable_sound`'s proof.
11. Budgets and deadlines: N.A. No budget, limit or deadline changes.
12. CPU or memory: N.A. No runtime path changes; Events is unreachable.
13. Removed tests: N.A. No test removed or renamed.

## FIXMAP
Files:
- lean/VE/Events/Decl.lean: `EventsTyped` (6.1, amended: year ≤ 9999 per named date), `WellFormedEvents` (unchanged)
- lean/VE/Events/Premises.lean: `regen_typed` (the one-line re-proof of the amended conjunct)
- lean/VE/Events/Calendar.lean: `pairwise_of_chain`, `rel_getLast`, `countP_lt_of`, `embeddable_sound` (6.2)
- lean/VE/Events/Examples.lean: the flipped 10000-01-01 fixture, the year boundary, the decoder guards (DRI conditions)
- lean/EVENTS.md: plain-words account; docs/spec/events-time-causation.md section 13: the amendment note
- ve/assurance-manifest.json: `other_json` entry for Examples.lean (JSON fixtures)
- tools/trust-classes.json: `vL`, `vL2` as T; docs/trust-baseline.json: the R16 allowance S +1
- docs/events-time-causation/et-3d/: DELTA, REPORT, mutants.json, trust-mutants.json, evidence/
Definitions by spec section:
- 6.1 EventsTyped -> lean/VE/Events/Decl.lean:100
- 6.2 embeddable_sound -> lean/VE/Events/Calendar.lean:237; regen_typed -> lean/VE/Events/Premises.lean:221
- helpers -> lean/VE/Events/Calendar.lean:202 (pairwise_of_chain), :211 (rel_getLast), :220 (countP_lt_of)
- fixtures -> lean/VE/Events/Examples.lean:289-342
Regression commands:
- cd lean && PATH=~/.elan/bin:$PATH lake build VE.Events.Examples
- python3 docs/events-time-causation/et-3d/evidence/seeded-bugs-harness.py.txt "$PWD" (prints mutants.json)
- uv run python docs/events-time-causation/et-3b/evidence/statements-diff.py.txt "$PWD" (prints statements.json)
- uv run pytest -q tests/test_assurance_manifest.py
- uv run python tools/trust_map.py --check
Generated files: lean/VE/Audit.lean, lean/{axioms,declarations,statements}.txt ->
  uv run python tools/regen_generated.py --write (route-cases needs the Rust release binary)
Trust mutants: zsh /home/seyran/code/manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --json
  docs/events-time-causation/et-3d/trust-mutants.json --rescore docs/events-time-causation/et-3d/trust-mutants.json
## END FIXMAP
