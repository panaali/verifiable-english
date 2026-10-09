# RD-1: `fillDoc` and separation under the completion (Lean)

Batch RD-1 of [readings-defaults-PLAN.md](../../spec/readings-defaults-PLAN.md), statements of
[readings-defaults.md](../../spec/readings-defaults.md) section 6.2 (draft 2), on branch `readings-defaults/lean`
from `1e15ef69`. Built by one Lean builder session on 2026-10-07; no model was called.

## What changed

- `lean/VE/Readings/Unspecified.lean` (new): the 6.2 definitions verbatim and the proofs of `fillDoc_one`,
  `fillDoc_free`, `fillDoc_choice`, `fillDoc_sup`, `compatible_fillDoc`, `attached_fillDoc`, `fillDoc_conservative`,
  `separates_soundU`, `separates_separatedU`, `achievesU_iff`, with 86 helper lemmas (among them
  `mem_attached_fillDoc`, `build_fillDoc`, `sup_fillDoc`, `soften_strict`, `choiceEnv_fill`).
- `lean/VE/Readings/UnspecifiedExamples.lean` (new): the fixtures of 8.1 as `#guard` (F-ND1 rows 1.1 to 1.10,
  F-ND5 rows 5.1 to 5.3, F-ND0) and F-ND11.
- Registered in `lean/VE.lean`, `lean/VE/Audit.lean`, `lean/VE/Route/frozen-sources.sha256` (new entries and the
  rehashed `Audit.lean`), `lean/axioms.txt`, `lean/statements.txt` (additions only: 96), `lean/predicates.txt`,
  `lean/declarations.txt`, `tools/trust-classes.json` (S: the meaning definitions; C: `fillDoc` and its parts,
  `fillHolds`; P: proof helpers; T: the fixtures).
- `tools/check_readings_defaults_statements.py` and `tests/test_readings_defaults_statements.py` (3 tests, pinned
  in `tools/gate-collection.json`); `lean/READINGS.md` (a section listing every theorem in plain words).

No frozen file, wire function, Python module or answer changed: nothing calls the new files (class: none).
`Norms`, `SoftNorms` and `Route` are untouched; `soften_hard_identity`'s core is restated locally
(`decisions_strict`, `soften_strict`) because its frozen statement carries an unused `WellFormedSoft` hypothesis.

## One statement changed: pending the statement re-review

`attached_fillDoc` is **false as approved** (hypothesis `fillNamesFree N` only). Fixture F-ND11 is a norms-shaped
document with free names and four fixed units over three sets whose rules name each other in `over`: unit `u0` is
attached to `[s2, s0, s1]` in `N.D` and to `[s0, s1, s2]` in `fillDoc N`. `attached` computes its table level by
level with fuel `D.items.length`; `fillDoc` adds one item per unspecified predicate, and for a unit attached to
several sets the level lists alternate in order (period 2 here), so the extra fuel changes the order. A brute-force
simulation of the level iteration found the same alternation in 14,417 of 200,000 random graphs.

Built instead, with the approved conclusion: `attached_fillDoc` with the added hypothesis
`(hs : singlyAttached N.D = true)` (a conjunct of `WellFormedDoc`, so every admitted document has it). Also proved:
`mem_attached_fillDoc` (under `fillNamesFree` only, the members agree), which is all the four equalities use, so
none of them needed a change. `tools/check_readings_defaults_statements.py` reports the 9 other statements exact and
`attached_fillDoc` as pending. **Owner: orchestrator; reviewers Astra + Fable (EXTERNAL, deferred):** accept the
added hypothesis, or prefer the membership form as the approved statement.

## Gate (run on HEAD `d3854ad6`, worktree clean)

| Check | Result |
|---|---|
| `lake build` (`PATH=~/.elan/bin:$PATH`) | `Build completed successfully (778 jobs)` |
| `python3 lean/audit.py` | PASS: 427 source files, 4,645 theorems, only `propext`, `Classical.choice`, `Quot.sound` |
| `python3 VE/Route/frozen.py` | PASS |
| `python3 tools/lean_statements.py --check` | PASS (4,291 statements; RD-1 adds 96, removes and changes none) |
| `tools/check_lean_imports.py` | layer graph kept (427 modules) |
| `tools/gate_collection.py --check` | 3 new IDs pinned (`--write`) |
| `tools/check_readings_defaults_statements.py` | PASS: 9 exact, 1 pending (above) |
| full pytest, 5 file chunks with `-n 16`, `VE_LEAN_PREBUILT=1`, 4 slow tests deselected | 1,912 + 3,904 + 1,765 + 2,289 + 1,535 passed, 6 skipped, 0 failed |
| the 4 slow tests alone (`-n 4`) | 28 passed |

`tools/trust_map.py --since 1e15ef69` still fails: the branch base's committed `declarations.txt` was stale for the
Senses modules, `ResponseShape/Schemas/Check.lean` and `Service/Standalone.lean` (S +917 before this batch). RD-1's
own growth is `VE/Readings/Unspecified.lean` trusted +45 (the S definitions: `NDoc`, `asU` and the four
documents, `normsShaped`, `fillNamesFree`, `WellFormedND`, `AchievesU`, `SeparatedU`). The baseline was not
rewritten, since that would sign the other modules' growth under this batch.

Not run: the corpus A/B and latency budget (nothing calls the new files, so no answer or timing can change).

## Seeded bugs (each planted in `Unspecified.lean` in a scratch copy, then removed)

| # | Bug | What failed |
|---|---|---|
| M1 | `fillSoftNode` ignores `over` (puts every rule on `p` under `F_p`) | proofs `fillSoftNode_toNode`, `copyContent_fill`, `gateContent_fill`, `uses_sub_fillContent` |
| M2 | `fillUnits` appends the `F_p` units in reverse order | `#guard` 1.1, 1.4 (four), 5.3; proofs `build_fillDoc`, `sup_fillDoc`, `mem_fillUnits` |
| M3 | `fillHolds` accepts every base | `#guard` 1.6; proof `fillHolds_sat` |
| M4 | `fillNamesFree` drops the reading sets' declared names | `#guard` 5.1; proof `namesFree` |
| M5 | `fillFrameEnv` declares `unsaid__p` with no arguments | `#guard` 1.3 and 1.4 (four); proofs `fillFrameEnv_eq`, `choiceEnv_fill` |

The statement checker's own tests also run it on a dropped hypothesis and on a stale pending entry; both fail.

## Build checklist (`manage-agents/prompts/build-checklist.txt`)

| # | Status |
|---|---|
| 1 one contract | not applicable: RD-1 adds no diagnostic, limit or JSON decoding |
| 2 differential fuzz | not applicable: no wire or decoder (RD-2a) |
| 3 text normalization | not applicable: no text input |
| 4 untrusted output | not applicable: no response is consumed |
| 5 malformed input | not applicable: no JSON input |
| 6 three-valued verdicts, budget 0 | not applicable: no verdict or public operation (the fold is RD-3) |
| 7 deadlines | not applicable |
| 8 exhaustive folds | not applicable: no kind or owner fold; `fillItem` matches every `Item` constructor, `fillContent` is the spec's |
| 9 English | not applicable: no sentence |
| 10 one admit() | not applicable: no entry point (admission is RD-2a) |
| 11 no regex of a real language | partly: the statement checker compares Lean text with approved text by regex, as `check_english_s3_statements.py` does; elaboration is the compiler's, axioms the audit's |
| 12 state machines | not applicable |
| 13 tests can fail | done: M1 to M5 above, and the checker's mutant tests |
| 14 hermetic | done: the new tests write only to `tmp_path`, read no environment, no sleep |
| 15 identity | not applicable: no schema field or identity |
| 16 lists generated or covered | done: `Audit.lean` (audit), frozen inventory (`frozen.py`), statement, predicate and declaration lists, gate collection, trust classes |
| 17 statement diff | done: `tools/check_readings_defaults_statements.py`; one change pending new approval (above); no DRI ruling in RD-1 |
| 18 fixtures, both directions of each iff | done: 8.1 as `#guard`; `compatible_fillDoc` both ways (1.9), `achievesU_iff` without `Fill_T` (1.6), `fillNamesFree` both ways (1.3, 5.1); F-ND11 for the changed statement |
| 19 use-case formalisation | not applicable |
| 20 reports | done: what was not run is stated; the numbers are copied from this run's logs |
| 21 AGENT/HUMAN/EXTERNAL | done: the statement re-review is EXTERNAL (Astra + Fable), deferred, owner the orchestrator; everything else AGENT |
| 22 hand-off | done: all committed, gate run on HEAD with a clean status in this worktree (not a fresh one), 57 GB free |
