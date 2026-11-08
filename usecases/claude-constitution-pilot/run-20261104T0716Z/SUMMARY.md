# Constitution pilot, SC-9 probe (run 20261104T0716Z): the translation under the soft form

**Status.** This is a probe, and the committed translation does not change. The translation adopts the soft form only after an audit accepts `changed_units.json`, and that decision is the pilot's.
**C10 NOT RUN**: this run makes no model calls (DRI decision `reviews/dri-decisions-20261104-sc-9.md` item 1; follow-up sc-9-comprehension).
**R14.** The four separations and C1 to C4's findings are about the pilot's translation, not the constitution's text. No conflict was reported. Any conflict or separation presented as a property of the source is a CANDIDATE until an independent source check has run.

## What ran
- **Translation.** Run 20261010T1800Z's `translation.ve.md` at `76922d6c` (blob `2d9f53e6…`, via `tests/ce4.py`'s pinned copy).
- **Scripts.** `migrate_soft.py` writes `probe-translation.probe.md`. `measure.py` runs every check and query, one at a time in the foreground, under `/usr/bin/time -v` with a 16 GB memory limit, with the host load read before each step (`answers/measurements.json`). Each answer is saved verbatim in `answers/{before,after,strict}/<step>.out|.err`. The C9 point-status steps used `RLIMIT_AS=16G` because this worker has no user systemd bus.
- **Commits.** The 26 check and query steps ran at `c4d6e79f4`. The `decided` step ran at `2d0b9d1a9`, which adds only that step and `--only` to `measure.py`; `ve/`, `lean/` and `rust/` are identical at both commits. After the run, `3edf7ab32` changed `migrate_soft.py` only to read the pinned copy without calling git. Rerun at that commit, it wrote a byte-identical probe; only the search time in `answers/search.json` changed.
- **C9 point statuses.** Two further foreground steps ran at `427f40684`, after the status measurement code was committed. Each asked Lean for `norm-defaults-status` on all 16 compatible choices under each sufficient condition and with none (`answers/{after,strict}/point-status-c9.out`). The `unsafe-required` and `unsafe-not-required` rows use the same situation because their conclusions ask opposite universal entailment questions about one point.
- **First pass.** The first measuring pass ended `CheckerUnavailable: missing Rust executable` on every check. The worktree had no Rust release binary. After `python3 tools/rust_build.py` (pinned sha `d55731df…`) the pass was rerun, and the rerun's answers are the ones recorded.
- **Migration.** `soft-norms@0` is added. The four `default` candidates are rewritten as in plan 5.2. u0073.s05 becomes one default rule with three sufficient exception conditions. Five open terms are dropped: the four `exception_to_*` and `general_exception_to_complying`.
- **Situations.** SC-8's search over Lean's filled frame re-proposed every set's situations and found all 8 ordered pairs, with no limits (`answers/search.json`, 5.9 s). Lean admitted them on load.
- **Identities.** Unit ids are Lean's. Candidate ids are the loader's binding (`s1_content_meaning_id`), because no Lean answer carries one (deviation D1, accepted by DRI item 2; both ids are in `answers/meaning-ids.json`).

## Before and after
| Measure | Before (translation as committed) | After (probe) |
|---|---|---|
| `ve document check` wall; CPU | 53.70 s; 53.65 s (54.6 s recorded at arch-AR-6) | 46.34 s; 46.02 s |
| Route; choices; conflict; premises | `superposed` (recorded: enumerated); 16; CONFLICT-FREE; `model` | `enumerated` (`ReadingsNotSuperposable`, the unspecified completion); 16; CONFLICT-FREE, 16 checked one at a time; `model` per choice |
| Lean-decided units, bytes, share | none (`decided_units` null on the superposed route): 0, 0, 0.00% | 19 units, 2,602 B, 1.41% (`answers/after/decided.out`) |
| Open terms | 33 | 28 |
| Gap sentences in the four separation lines | C2: 1; C4: 1; C1 and C3: no worded line ("These two readings differ in a checked situation that VE cannot yet show in words.") | the same: C2: 1, C4: 1; C1 and C3 unworded |
| Pairs separated; not separated | 4 (outcome 2, selects 2); findings 0 | 4 (outcome 2, selects 2); `SeparatedByDecisionOnly` 4; the search left no pair unseparated |
| Claimed covered; audit-verified | 2,951 B (1.60%); 764 B (0.41%) | 2,951 B (1.60%); no status changes, and all five changed units stay OPEN. If the probe were adopted, the five units (568 B), all audit-verified now, would wait for re-audit, leaving 196 B (0.11%) |

Peak RSS of the two new C9 status steps was 185,704 KB; earlier steps were ≤ 141 MB, as `/usr/bin/time` reports. No run was killed.

## Queries (verbatim answers in `answers/`)
| Query | Before | After | Plan's expectation (CE4) |
|---|---|---|---|
| C6, "∀c. ¬ denial_of_being_claude_permitted(c)" | UNKNOWN | UNKNOWN | SOME |
| C6 `--under force-u0125-s04-p2:0` | ALL | ALL (8 certificates) | ALL |
| C6 `--under …:1` | UNKNOWN | UNKNOWN | NONE |
| C7, "∀c ∀s. genuine_ambiguity(s) → clarification_required(c, s)" | UNKNOWN | UNKNOWN | SOME |
| C7 `--under force-u0036-s05:0` | ALL | **CheckerUnavailable**: `ReadingsConformance: Lean's English plan has an unknown frame unworded` | ALL |
| Claim to be human (`queries/claim-human.json`) | ALL | ALL (16 certificates) | ALL |

Every UNKNOWN reads "… VE could not check whether the conclusion follows." The generators found neither a certificate nor a countermodel on the whole translation. On CE4 (the four sets alone) the same queries give SOME, ALL and NONE (`tests/test_readings_sd_ce4.py`). The cause on the whole frame was not analysed (sc-9b).

## C9: u0073.s05 as a default rule with three sufficient conditions
- **`soft_premises` (found).** Every one of the 16 choice entries carries `soft:exception:comply-operator-prompt:sufficient:0`, `:1` and `:2` (`compliance_unsafe`, `compliance_unethical`, `compliance_against_guidelines` → `soft__excepted__comply_operator_prompt`), so X ≠ [] (`answers/after/load.out`). `ve document coverage` reports one default exception, decider unstated. There is no force-twin finding, since u0073.s05 is in no reading set.
- **Point statuses (found).** Lean answered `norm-defaults-status` on a concrete model for every choice, with the guard true and each sufficient condition true in turn. Where a condition holds, the exception table contains `(c,s)` as X requires; with no condition, it is empty. An UNDECIDED answer includes two fillings checked by Lean. The strict twin has no C9 exception table.

| Concrete situation (each of 16 choices) | Default probe | Strict twin |
|---|---|---|
| `compliance_unsafe(s)`; both unsafe query phrasings | UNDECIDED | SETTLED yes |
| `compliance_unethical(s)` | UNDECIDED | SETTLED yes |
| `compliance_against_guidelines(s)` | UNDECIDED | SETTLED yes |
| No sufficient condition | SETTLED yes | SETTLED yes |

Thus the expected point-status separation is measured on the full probe translation, for every compatible choice. The six older `readings-c9-*.out` **universal entailment** answers remain UNKNOWN; those questions quantify over all situations and do not answer the concrete point-status question.

## C10: the comprehension check, NOT RUN
`comprehension/questions.json` holds C1 to C4's rendered lines byte for byte, with spec 2.6's four questions, and no answers. On this translation only C2's and C4's lines contain the "Under (2) … is not required to" wording. C1's and C3's lines are unworded, so on the translation their questions test no separation sentence.

## Failed checks and open items (listed, not worked around)
1. C6 and C7 end UNKNOWN on both documents, where CE4 gives SOME, and C6 `:1` ends UNKNOWN where CE4 gives NONE.
2. C7 `--under force-u0036-s05:0` on the probe ends CheckerUnavailable.
3. C1's and C3's separation lines are unworded on the whole translation, in both documents. CE4 words them.
4. The six universal C9 entailment queries remain UNKNOWN, despite the measured concrete point statuses and separation.
5. C10 was not run.
6. Before, the route measured `superposed`, where `enumerated` was recorded, and Lean decided no units.
