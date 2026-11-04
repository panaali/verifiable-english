# df-5ab: `forcedAll` at one situation, in Lean (report)

**Status**: built; ready for the chain's gate and review. No DRI signature is reserved.
**What changed**: `lean/VE/Defaults/Zone.lean` gains `forcedAllOf` and three theorems, all proved (`forcedAll_sound`
with its signed `valid`, `defaultCompletion_below`, `forced_everywhere`), no `sorry`, no new axiom.
`ZoneExamples.lean` gains 8.6's `forcedAll` checks as `#guard`s.
**Open**: the full gate (the chain runs it). **Bytes 0. DELTA**: none. **Trust**: +0 (K, S, V).
**Next item**: df-5 (the `defaults-zone` kind row, English DE10/DE10f/DE11/DE13, the relay and the route cases).

## Inputs

- Task: feature item df-5ab, rank 166, cut from df-5a by `manage-agents/reviews/dri-decisions-20261102-df-5a-size.md`
  item 1 (SIGNED: the cut, the four declarations, their fixtures and the seeded bug).
- `forcedAll_sound`'s wording, with `valid : M.Valid (envAt L.U.D 0)`, comes from `reviews/dri-decisions-20261102-df-5a.md`.
  That wording is already in spec 7.5 on main (`docs/spec/defeasible.md:1154-1160`, merged with df-5a). This item does
  not edit the spec.
- Plan and spec: `docs/spec/defeasible-PLAN.md` 3.6 and `docs/spec/defeasible.md` 7.5, 8.6 and 8.9. Both are already
  on main and identical to the pinned 174fbb62a for these sections, so nothing was copied.
- Base: main at 4e961f0ad, which already contains df-5a (`git merge-base --is-ancestor feature/df-5a main`: true).

## Plan rows

| Row | Delivered | Where | Evidence |
| --- | --- | --- | --- |
| Statement gate: DF-S accepted 7.5; `forcedAll_sound` at its signed wording, the other three word for word | yes | `Zone.lean:273`, `:1161`, `:1197`, `:1230` | `python3 docs/defeasible/df-5ab/evidence/check_statements.py`, output in `evidence/statements.out`: "ALL OK" (the four OK) |
| (1) `forcedAllOf`: the exception atoms true in every default completion, from `defaultZoneOf`'s complete enumeration (`zoneMin`); `none` if the enumeration is incomplete or finds no default completion | yes | `Zone.lean:268-284` | `forcedAll_sound`; the guards below |
| (1) `forcedAll_sound` (with `valid`) | yes, proved | `Zone.lean:1161` | `lake build`: "Build completed successfully (1236 jobs)"; `python3 lean/audit.py`: PASS (propext, Classical.choice, Quot.sound only) |
| (1) `defaultCompletion_below` | yes, proved (strong induction on the number of true decision atoms, using the existing `VE.NormDefaults.countP_lt_of`) | `Zone.lean:1197` | same |
| (1) `forced_everywhere` | yes, proved from `defaultCompletion_below` | `Zone.lean:1230` | same |
| (2) 8.6 DF-μ: `forcedAll` = [g1's exception at o1] (accepting side) | yes | `ZoneExamples.lean:249` | `lake build VE.Defaults.ZoneExamples` |
| (2) 8.6 DF-μ′, DF-μ″: `forcedAll` = [] although each default completion has an exception (refusing side) | yes | `ZoneExamples.lean:252`, `:254` | same |
| (2) DF-δz: `forcedAll` = []; an exception fixed by the record is forced when true and not when false; a decision that is not an exception is not listed; no list (`none`) over the budget, over the record bound, with no completion, and at 2 × 10⁷ open atoms | yes | `ZoneExamples.lean:256-266` | same |
| (3) 8.9 seeded bug "forcedAll read from one default completion" fails DF-μ′ and DF-μ″ | yes, S6 | `mutants.json` | `python3 docs/defeasible/df-1a/evidence/run_mutants.py docs/defeasible/df-5ab/mutants.json`, output in `evidence/mutants.out`: "S6 … FAILS 2 guards" (the dμ' and dγ guards) |
| (4) One mutant per new trusted definition; `tools/trust_mutants.py` exit 0 | yes: there is no new trusted definition (`forcedAllOf` is C, checked by `forcedAll_sound`), and F1-F8 mutate each part of `forcedAllOf` anyway | `mutants.json` F1-F8 | `mutants.out` "ALL MUTANTS FAIL THEIR GUARDS"; `mac-pytest.sh --trustmut`: "0 definitions … 0 SURVIVOR", exit 0 (`trust-mutants.json`) |
| (4) Evaluator rule (2026-10-27): each value read once, size charged, a large well-formed situation ends within the limit | yes. `forcedAllOf` reads `zoneMin`, which runs `zoneCharge` before it lists anything, and lists only `noExceptionRecord`, whose atoms that charge has counted (at most `maxZoneRecord + maxDefaultAtoms` typed atoms). `C`, `V₀` and `Min` are each computed once. Fixtures: 12 open atoms (4,096 assignments), 2 × 518 typed atoms listed, one past that is `none`, 2 × 10⁷ atoms are `none` at once. | `ZoneExamples.lean:263-272` | same build |
| df-5a's conditions stay selected: `lake build VE.Defaults.Zone VE.Defaults.ZoneExamples`; 8.6's fixtures; df-5a's mutants; the large situation; trust_mutants exit 0 | yes | — | `run_mutants.py docs/defeasible/df-5a/mutants.json` on this tree: "control: 0 failures … ALL MUTANTS FAIL THEIR GUARDS" (run once; the output was not saved here and df-5a's evidence was left as it is) |
| No `def` of `decisionAtoms`, `openNames`, `AdmissibleCompletion`, `OutcomeIn`, `SettledZ`, `ZoneUnknown` under `lean/VE/Defaults/` | yes | — | `git diff main...HEAD -- lean/VE/Defaults \| grep -nE '^\+def (decisionAtoms\|openNames\|AdmissibleCompletion\|OutcomeIn\|SettledZ\|ZoneUnknown)\b'`: no match |
| Not touched: `Uniform.lean`, `Route.lean`, `ve/defaults.py`, `lean/VE/Weighing/` | yes | — | `git diff --stat main...HEAD` |
| `lean/statements.txt` through its tool | yes (`uv run python tools/regen_generated.py --write`) | — | `regen_generated.py --check`: only trust-tables was stale, and it is clean after the classification (`trust_map.py --check` PASS) |

**Recorded deviations** (none needs a signature):
- `forcedAllOf` returns each atom once (`eraseDups`). The spec gives only its signature and docstring. Without this, a
  domain that lists an element twice would report the same atom twice (guard `ZoneExamples.lean:272`, mutant F7).
- Two helper lemmas are added (P, proof only): `mem_of_mem_eraseDups` (core has only the converse) and `coneAtomVX_off`.

## Seeded bugs (Lean, the only product language changed; each in `lean/VE/Defaults/Zone.lean`)

Run with `python3 docs/defeasible/df-1a/evidence/run_mutants.py docs/defeasible/df-5ab/mutants.json`. The saved output
is `evidence/mutants.out`: control 0 failures, then "ALL MUTANTS FAIL THEIR GUARDS". Each mutant was planted, shown to
fail and removed (the runner edits a temporary copy).

| Id | Definition | Bug | Failing test |
| --- | --- | --- | --- |
| S6 | `forcedAllOf` | 8.9: forced read from one default completion (`Min.take 1`) | dμ' and dγ forcedAll guards (DF-μ′, DF-μ″) |
| F1 | `forcedAllOf` | an exception fixed true by the record is never forced | dlam record-fixed guard |
| F2 | `forcedAllOf` | an atom off the enumeration is forced whatever its value | dlam record-fixed guard |
| F3 | `forcedAllOf` | forced when some minimal assignment holds it | dμ' and dγ guards |
| F4 | `forcedAllOf` | an incomplete enumeration answers `some []` | dlam and dα `none` guards |
| F5 | `forcedAllOf` | emptiness test inverted | DF-μ guard |
| F6 | `forcedAllOf` | every decision atom is a candidate | dδ outweighs guard |
| F7 | `forcedAllOf` | no deduplication | dlam large-situation guard |
| F8 | `forcedAllOf` | the two branches swapped | DF-μ guard |
| P1 | `forcedAllOf` (theorems kept) | as F2 | theorem `forcedAll_sound` |
| P2 | `DefaultCompletion` (theorems kept) | minimality ignores the observations | theorem `defaultCompletion_below` |
| P3 | `DecLe` (theorems kept) | compared the wrong way round | theorems `defaultCompletion_below`, `forced_everywhere` |

## Trust

`uv run python tools/trust_map.py --check` on the final tree reports "against 4e961f0ad503: K +0, S +0, D +0, G +0, tied
+0, unclassified +0, trusted +0" and "PASS". `tools/trust-classes.json` puts `VE.Defaults.forcedAllOf` in C, as
df-5a's `defaultZoneOf`: its meaning is checked by `forcedAll_sound` against `DefaultCompletion`, which is S. The
fixture helper `VE.Defaults.ZoneFixtures.forced` is T. With no growth, there is no R16 allowance and no FOLLOW-UPS row.

## Size

`git diff --numstat $(git merge-base HEAD main)`, excluding generated files and saved run outputs: Zone.lean +114,
ZoneExamples.lean +34, trust-classes.json +2, mutants.json +189, check_statements.py +25, REPORT.md +116 and DELTA.md
+14. That is 494 hand-written lines, under 600.

## Tests

- Selected tests, run once on the finished code at 177ce32f6:
  `zsh manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`. It ran on GitHub Actions in two
  shards: 47 + 51 units, all passed, exit 0 (`evidence/selected-tests.txt`).
- Commits after 177ce32f6 change docs and evidence only.
- Not run here: the full gate (the chain runs it on the final HEAD).
- No test was removed or renamed.

## Pilot bytes

0 expected: no route reads `forcedAllOf` yet. DE10f in df-5 is the first reader.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer. No mode, schema or relay was added.
2. PASS: each plan row and directive is in the table above with its evidence. `git diff main...HEAD` adds no Python
   copy, no report test and no shared file in flight. The only overlap is `lean/VE/Defaults/Zone.lean`, with df-5a,
   which is now merged.
3. PASS: `evidence/mutants.out` (S6, F1-F8 on guards, P1-P3 on theorems); trust_mutants exit 0 (`trust-mutants.json`).
4. N.A.: Lean only. No Python or Rust path computes `forcedAll`.
5. N.A.: Python reads no field (no relay).
6. PASS for the evidence: the selected tests ran at 177ce32f6. The chain runs the full gate on the final HEAD.
7. PASS: DELTA has no rows and trust is +0 (`trust_map.py --check` PASS). No signature is pending.
8. PASS: no user-visible change. No mode, executable or relay reads the new declarations (DELTA.md).
9. PASS: `tools/select_tests.py --base …` selected 98 units, not every unit (`evidence/selected-tests.txt`).
10. PASS: `evidence/statements.out` "ALL OK". P1-P3 show that a wrong `forcedAllOf`, `DefaultCompletion` or `DecLe`
    breaks `forcedAll_sound`, `defaultCompletion_below` and `forced_everywhere` (`mutants.out`).
11. PASS: an incomplete enumeration is `none`, never a list. Guards for the budget, the record bound, no completion and
    2 × 10⁷ atoms (`ZoneExamples.lean:263-266`; mutant F4).
12. PASS: no eager listing before the charge, and `C`, `V₀` and `Min` are each computed once. The cost is bounded by
    the charged counts; the large-situation guard ends within the build (`ZoneExamples.lean:268-272`).
13. N.A.: no test removed or renamed.
14. PASS: both directions are guarded (DF-μ forced and DF-μ′/DF-μ″ not; record true forced and false not; `some` and
    `none`). Every claim above cites its command. Spec re-read: the four statements against
    `docs/spec/defeasible.md:1146-1178` (`check_statements.py`), and 8.6 at `:1442-1446` and 8.9 at `:1498` against the
    guards.
