# ap-4bb report: `sourceCheck_complete` with item 8c's bound, `View`'s soft fields (ap-4b-f2), the R16 ties pass

No DRI signature is reserved. One question is open with the DRI decider (part D's scope, "Notes for the DRI" 1); it
does not block the item.

Base `97b3c7999a` (`git merge-base HEAD main`). Branch `feature/ap-4bb`. Task: backlog row ap-4bb (carries ap-4b-f2 by
reviews/dri-decisions-20261102-followup-triage.md item 8c); FOLLOW-UPS "## ap-4b (2026-10-31)" and "## ap-4b round 1".
Deltas: [DELTA.md](DELTA.md).

SIZE: 179 product (Lean: Sources.lean 18, SourcesProofs.lean 118, Situation.lean 43), 54 tests (ReadingsExamples.lean
`#guard`s and fixtures), 175 other hand-written lines (spec 7 19, tools/trust-classes.json 26, check_statements.py 17,
seed_bugs.py 100, this REPORT and DELTA.md) plus the written-by-script mutants.json (106) and trust-mutants.json; from
`git diff --numstat $(git merge-base HEAD main)`, generated files (lean/*.txt, VE/Audit.lean, docs/codemap) excluded.

## Deliverables

| Task line | Delivered | Commit | Check |
|---|---|---|---|
| (A) the 65-choice counterexample, committed on its own | `sourceCheck_complete_needs_bound` (`lean/VE/Acts/SourcesProofs.lean:40-52`): for any `D` whose cut part passes D-29 and whose choices exceed `maxChoices`, `SourceExact` holds and `sourceCheck` is the `ResourceLimit` error. Its decidable premises hold on S4 beside six sets of two (128 choices; `choices` cuts at 65) | `ffb34310b8` | `#guard` `ReadingsExamples.lean:287` (`cutExact`, `maxChoices < (choices D).length`, `sc … == choiceLimit`) |
| (B) `sourceCheck_complete` with `hn`, lemmas, spec 7 `hn` + one sentence, 11.4 unchanged, S4/S6/64 through the theorem's direction | `sourceCheck_complete` (`SourcesProofs.lean:106-116`), statement exactly as the task gives it; lemmas `sourceCheck_eq`, `sourceExact_of_compare`, `eq_of_perm_of_pairwise`, `forall₂_mem_left`, `pick_of_forall₂` (the greedy `pick` returns any matching drawn from pairwise non-permuting choices), `compareViews_complete` (the converse of `compareViews_ok`). No hypothesis beyond `hn`: pairwise non-permutation and distinct paraphrases come from `SourceExact` itself. Spec 7 (docs/spec/act-phrases.md:1403-1405, 1420-1423); 11.4's line (:1811) unchanged | `690f83a22a`, `fd60c8154f` | `python3 docs/act-phrases/ap-4bb/check_statements.py`: 14 EQUAL (spec 7 against the Lean, incl. `sourceCheck_complete`); `#guard`s `ReadingsExamples.lean:306-307` (`exactOn` and `sc == "ok"` on S4, S6 and S4 beside five sets = 64 choices) and `:309-310` (the premises fail on S5 and S7) |
| (C) ap-4b-f2's `View` extension, only if signed | Signed: reviews/dri-decisions-20261110-ap-4b-f2.md item 1, and reviews/dri-decisions-20261111-ap-4bb.md item 1 (`expected` reads the five fields from `VE.Readings.strictNodeOf s.template`). `View`, `ruleView`, `expected` compare `mode`, `rank`, `alterable`, `exception`, `hard`; spec 7's `View` (:1364) edited; (B) is proved over the new `View` | `690f83a22a` | failing-first `ReadingsExamples.lean:319` (strict to default on S4's document refused with D-29's third text); `:320` (rank, alterable, exception, hard each refused); `:324` (`expected`'s fields are `strictNodeOf`'s); S1-S8, 64-choice, choice limit, F11 guards unchanged (`lake build` passes) |
| (D) R16 ties pass: `atomSituation` tied to `separates`/`separates_separated`; before/after with `trust_map.py --check` | `rulePred_eq_some` (both directions), `atomSituation_probe` (the probe is i's act when j's rule has another predicate), `atomSituation_holds` (else `holds`), `atomSituation_valid` (the base is valid over every environment), `atomSituation_separated` (`separates … (atomSituation …) = true` gives `Separated` through `separates_separated` with no base premise) (`lean/VE/Acts/Situation.lean:30-68`). See Deviations 1 for the part not proved | `fd60c8154f` | `#guard`s `ReadingsExamples.lean:367-387` (`separates` true both ways on S1's u105b/u105c, u055, a two-argument act d076; false and `holds` when two candidates share one act); `trust_map.py --check`: before (merge base) `atomSituation`, `rulePred` untied G[V] (+15 trusted, ap-4b's row); after: Situation.lean trusted -15 |
| Seeded bugs: `hn` dropped; `pick` stops at the first partial match; `atomSituation` j's act for i; `ruleView` ignoring mode | all four planted, KILLED, restored (below) | `c82c6e5623` | `python3 docs/act-phrases/ap-4bb/seed_bugs.py` → [mutants.json](mutants.json) |
| DELTA row 1 (`hn`), row 2 (`View`), trust | [DELTA.md](DELTA.md) rows 1-3 | this commit | review-ready [delta] |
| R16: no K, ≤ 150, a mutant per new trusted definition, FOLLOW-UPS row "## ap-4bb" | K +0, S +5, tied +15, trusted -10; plants on `View`, `ruleView`, `expected`; FOLLOW-UPS row written | `15d466978a` | `uv run python tools/trust_map.py --check`: "against 97b3c7999add: K +0, S +5, D +0, G +0, tied +15, unclassified +0, trusted -10 … PASS" |

## Deviations

1. **(D) proves the tie, not a general "separates whenever".** FOLLOW-UPS' row words the tie as "a theorem that
   `atomSituation D s i j` separates whenever i's rule regulates an act j's does not, under the guard-free template".
   That sentence is false as stated: `separates` (`lean/VE/Readings/Separate.lean:276-283`) also requires
   `situationWF` and `cells D s j base ≤ maxCells` (12), so a candidate j owning more than 12 generated keys is refused
   whatever the probe. A true version needs those premises and a semantic proof over every assignment of j's owned
   keys; it is not built. What is built ties both trusted definitions (their outputs characterised both ways, and an
   accepting `separates` made sound with no premise on the base), with `#guard`s on four documents; trust_map counts
   both as tied. Asked the DRI decider (inbox/dri/20261111T013520Z-ap-4bb-2854848.md) whether this completes (D),
   recommending yes with the bounded completeness theorem as ap-4bc; FOLLOW-UP line below until it answers.
2. **Trust-mutant sweep selects 0 mutants.** `mac-pytest.sh --trustmut -- --max-mutants 1000 --json
   docs/act-phrases/ap-4bb/trust-mutants.json` exited 0 with "0 definitions, 0 mutants": the changed lines of `View`,
   `ruleView` and `expected` are tuple fields no operator mutates (the one candidate in `expected`, `==` → `!=` on
   `s.role == .plain`, is on an unchanged line). The hand plants in mutants.json cover the three definitions.
3. If `soft-norms@0` ever joins `acts@0` (spec 4.4), `expected`'s soft fields (`strictNodeOf` of the template) are
   the place that must change (DRI 2026-11-11 item 1).

## Seeded bugs (all Lean; no Python or Rust product code changed)

From `python3 docs/act-phrases/ap-4bb/seed_bugs.py` ([mutants.json](mutants.json), restored build return code 0):

| Plant | File | Fails |
|---|---|---|
| `hn-dropped`: `sourceCheck_complete` without `hn` | lean/VE/Acts/SourcesProofs.lean | B no longer elaborates (build errors at `SourcesProofs.lean:109` and `:114` of the planted file, in the proof's use of the bound); A's theorem shows why no proof can exist |
| `pick-first-partial`: `pick` takes the first choice sharing any view | lean/VE/Acts/Sources.lean | `pick_forall₂` (`Sources.lean:160`); with its proofs `sorry`ed (`+guard`), the S4, S6 and 64-choice `#guard`s through B's direction (`ReadingsExamples.lean:306`) and S1-S8 guards fail |
| `atom-j-for-i`: `atomSituation` probes j's act for i | lean/VE/Acts/Situation.lean | `atomSituation_probe`/`_holds` (`Situation.lean:50`, `:56`); `+guard` variant fails too |
| `rulePred-name`: `rulePred` reads the rule's name | lean/VE/Acts/Situation.lean | `rulePred_eq_some` (`Situation.lean:43`, `:45`) |
| `ruleView-no-mode`: `ruleView` ignores mode again | lean/VE/Acts/Sources.lean | failing-first fixture `ReadingsExamples.lean:319` |
| `ruleView-no-hard` | lean/VE/Acts/Sources.lean | `ReadingsExamples.lean:320` |
| `view-drops-alterable` | lean/VE/Acts/Sources.lean | `ReadingsExamples.lean:320` |
| `expected-constant-rank` | lean/VE/Acts/Sources.lean | `ReadingsExamples.lean:184-187, 214-240, 273-306, 324, 346` |
| `strictNodeOf-default` (DRI 11-11's condition) | lean/VE/Readings/Unspecified.lean (planted only) | its own guard `Unspecified.lean:503` and `ReadingsExamples.lean:324` |

## Trust

`uv run python tools/trust_map.py --check` on the final code: "against 97b3c7999add: K +0, S +5, D +0, G +0, tied +15,
unclassified +0, trusted -10; VE/Acts/Situation.lean: trusted -15; VE/Acts/Sources.lean: trusted +5 … PASS".
Recorded with `trust_map.py --allow` (S 5, `docs/trust-baseline.json`), "SIGNED by standing ruling R16
(DRI-RULINGS.md), ap-4bb, 2026-10-18". Tied now: `sourceCheck`, `compareViews`, `pick` both ways
(`sourceCheck_exact`/`sourceCheck_complete`, `compareViews_ok`/`compareViews_complete`,
`pick_forall₂`/`pick_of_forall₂`); `atomSituation`, `rulePred`. Left: ap-4b's S definitions (`Source`, `View`,
`ruleView`, `expected`, `choicesOn`, `choiceRules`, `choiceViews`, `readingViews`, `opOfSource`, `SourceExact`), now
pinned both ways by `sourceCheck_exact` and `sourceCheck_complete`; the general `separates` completeness of
Deviations 1. FOLLOW-UPS.md row under "## ap-4bb".

## Pilot bytes

None expected: no route reaches `sourceCheck` or `atomSituation` until ap-4's admission hook (DELTA, "Public output").

## Tests run

- `cd lean && lake build` (in seed_bugs.py's restore step, return code 0) and per-module builds while iterating.
- `python3 docs/act-phrases/ap-4bb/check_statements.py`: 14 EQUAL.
- `uv run python tools/trust_map.py --check`: PASS (above).
- trust-mutants sweep: [trust-mutants.json](trust-mutants.json), 0 mutants, exit 0 (Deviations 2).
- Selected tests: `MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on
  the committed final tree; result in the build report.

## Notes for the DRI

1. Part (D)'s scope (Deviations 1): question sent; recommended answer "complete; the bounded completeness theorem is
   ap-4bc".
2. The cloud trust-mutant runner logged "base 0d663e3c50e5" (a main object with the same message as `97b3c7999a`); the
   JSON records base `97b3c7999add…` and head `c82c6e5623`. No mutants either way.
3. Main has moved 59 commits; only `tools/trust-classes.json` overlaps (main's 469+/412- against this branch's ties
   entries); the merge train's sync regenerates it.

## Next item

None, unless the DRI keeps (D)'s general theorem open:

FOLLOW-UP: ap-4bc `atomSituation` separates whenever i's rule regulates an act j's does not (with `situationWF` and the `maxCells` premise)
