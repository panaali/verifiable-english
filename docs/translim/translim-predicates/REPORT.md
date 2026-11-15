# translim-predicates: the limit of 64 regulated predicates per environment

Branch `feature/translim-predicates`, base main `a84c072d76`. Task: measure what raising the limit costs, then RAISE
(if the cost is bounded and the DRI says yes) or RESTRUCTURE (if a structure inside today's limits carries the use
cases). Labels: **MEASURED** (run here, data file named) and **ESTIMATE** (derived, the method given).

**Outcome: RESTRUCTURE recommended; RAISE is not bounded.**
- Above 64 the cost is not bounded. At 96 and 128 the norms route overruns its 6 s CPU deadline. The soft
  document's AST limit refuses at 96, and the 256-predicate vocabulary limit refuses at 128.
- Today's limit already carries the problem. At 64, one worst-case request shape overruns its deadline.
- A split into two frames, each within 64, leaves every RSP answer unchanged.

DRI question 1 was sent with these numbers (section 5). PART 2 waits for the answer.

## 1a. Why 64: the limit sites and what grows with the count (MEASURED by reading the code)

| site | file:line | per regulated predicate | grows with k |
|---|---|---|---|
| `decodeRegulatedAllIn` (the `environment`, `model`, `check` modes via `Standalone.checkRegulated`; `Family`) | lean/VE/Norms/Plain.lean:44 | decode one declaration; `actChecks` | linear decode; `actChecks` pairwise on (signature, act, role) |
| `decodeNormsEnvironment` (`norms`, `soft-norms`, `norm-defaults` decoders) | lean/VE/Norms/Wire.lean:246 | decode; `actChecks`; `joinedActs` (each act read under `acts@0`, one grammar for all acts) | linear plus one act read per act |
| `check` (the elaborated document after an act split) | lean/VE/Norms/Tree.lean:304 | `dupName` over names, declaration loop, `actChecks`, dual lookup by `find?` | quadratic at most |
| `checkSteps` (proved `= check` by `rfl`), `CheckOK` and `check_iff` | lean/VE/NormDefaults/Check.lean:138, 388, 402 | the same check, as a statement | (statement) |
| `checkW1` (soft tree after `soften`) | lean/VE/SoftNorms/Soften.lean:471 | as `Tree.check` | quadratic at most |
| `checkW1Steps` (proved `= checkW1` by `rfl`) and the proof `TRel.checkW1` | lean/VE/RightClauses/PlainWellFormed/W1Check.lean:26, 189 | the same check | (the proof's `by_cases h64 : r.length > 64` is a fifth Lean literal, found when the test-only build failed on it) |
| Rust mirror `regulation_pairs` | rust/ve-kernel/src/environment.rs:305 | act/role map, duals | linear |
| Python | none | Python keeps no mirror (grep of `ve/`); `tests/test_soft_request_economy.py:31` names `MAX_REGULATED = 64` as a test constant | |

- **No bitmask or table limits the count.** No `UInt64`, mask or `2^k` table is indexed by the regulated list in
  the norms, soft-norms, norm-defaults, acts or right-clauses code. The only `2^k` is NormDefaults' enumeration
  budget of `2^12` fillings (lean/VE/NormDefaults/Evidence.lean:785), which has its own budget.
- **The limit is a chosen resource bound.** It entered with the W1 norms spec (commit `d07544be25`, 2026-09-26,
  docs/spec/norms.md 11.5) with no stated derivation. No site needs exactly 64.
- **What the bound protects is downstream of the sites,** in the generators that run per regulated predicate and
  per guarded rule. These were measured in section 1b:
  - `Flagged.regenerated`, lean/VE/Norms/Flagged.lean:46: per target, `conflict D r`, `elabPremise`, and the
    obligation/permission `pairs`.
  - NormDefaults' elaboration.

Decomposition on `norms-elaborate` (MEASURED, one run each, frame of 55 predicates; script
`/tmp`-only, numbers here):

| 32 / 48 regulated | CPU s |
|---|---|
| declarations, no rules | 0.05 / 0.17 |
| one rule each, guard `top` | 0.04 / 0.20 |
| one rule each, guard one frame predicate | 0.58 / 3.55 |
| the same with the frame cut from 55 to 4 predicates | 0.54 / 3.54 |
| obligations' rules only (half) | 0.38 / 2.36 |

- The response grows linearly: 29 KB at 32 and 44 KB at 48.
- The cost is in rules with a real guard, about n^5 in the regulated count. Neither the decoders' limit checks
  nor the frame size drive it.
- `norms-conflict` decodes the same source without the regenerated wire. It takes 2.3 s at 64 where
  `norms-elaborate` overruns, so most of the cost is in `Flagged.regenerated`.

## 1b. Cost curve (MEASURED)

**Method.** Script `cost_curve.py` (this directory). Each request runs on a fresh `ve_service`, 3 runs per cell
unless marked. CPU is the service process's own (`/proc`), and the deadline is the client's
(`lean_service.deadline`, CPU seconds).

**Environments.** The RSP frame is `environment.d1.json` without its regulated predicates: 3 sorts and 55
predicates. N generated regulated predicates are added over `situation`, as obligation and permission pairs, each
with a legend and one rule.
- `flat`: each guard is one frame predicate.
- `cone`: rule i's guard reads regulated predicate i-1, so the last rule's guard cone holds every regulated
  predicate. This is the worst case.

**Binaries.**
- 32 to 64: the pinned `ve_service` of this tree, sha `068a6676…f4f9`.
- 96 and 128: a test-only build with the limit at 128, sha `3668e255…cb6`. That build edited the five literal
  sites plus `CheckOK`/`check_iff` and the W1Check proof, locally. It was never committed and was reverted, and the
  shared build was restored.

**Machine.** AMD EPYC 7B12, 32 cores, load average 54 to 67 during the runs. CPU numbers can be inflated by
contention, and the overruns are well past any such factor.

**Data.** `data/curve_32_64.json`, `data/curve_40_56_flat.json`, `data/norm_defaults_8_28.json`,
`data/curve_96_128_patched.json`.

Median CPU seconds. **DL** = stopped at the CPU deadline (`CheckerUnavailable`, never a verdict). "refused" = a
`ResourceLimit` answer.

| kind (mode, deadline) | 32 flat | 32 cone | 40 flat | 48 flat | 56 flat | 64 flat | 64 cone | 96 flat | 96 cone | 128 flat | 128 cone |
|---|---|---|---|---|---|---|---|---|---|---|---|
| norms-elaborate (norms, 5.7-6.5) | 0.40 | 0.09 | 1.48 | 3.47 | **DL** | **DL** | 1.41 | **DL** | 3.73 | **DL** | **DL** |
| norms-conflict (norms, 5.7-6.5) | 0.66 | 0.81 | 1.06 | 1.33 | 1.85 | 2.26 | 2.16 | 3.12 | 2.91 | 6.46, then **DL** x2 | **DL** |
| soft-rules (soft-norms, 123-127) | 0.01 | 0.01 | | | | 0.07 | 0.06 | 0.15 | 0.12 | 0.39 | 0.42 |
| soft-elaborate (soft-norms, 123-127) | 0.07 | 0.10 | | | | 0.57 | 0.57 | 1.12 | 1.31 | refused: extended vocabulary | refused: extended vocabulary |
| norm-defaults-elaborate, all `unspecified` (norm-defaults, 122-124) | 4.03 (1 run) | **DL** (from 24) | 13.50 | 32.42 | 73.30 | ESTIMATE about 143, **DL** | **DL** | ESTIMATE about 1,100 | **DL** | ESTIMATE about 4,600 | **DL** |
| acts parse: norms-elaborate under `acts@0`, every act joined (norms, 5.7-6.7) | 0.56 | 0.11 | 1.41 | 3.62 | **DL** | **DL** | 1.21 | **DL** | 6.26 (at the deadline) | **DL** | **DL** |
| document check, `ve check` of a soft document with one norm unit per predicate (document, 120; child CPU) | 0.68 | 0.66 | | | | 2.65 | 2.42 | refused: AST exceeds 10,000 | refused: AST exceeds 10,000 | refused: extended vocabulary | refused: extended vocabulary |

`norm-defaults-elaborate`, `cone` shape (MEASURED, one run each):

| regulated | 8 | 12 | 16 | 20 | 24 | 28 |
|---|---|---|---|---|---|---|
| CPU s | 0.06 | 0.61 | 5.23 | 36.35 | **DL** | **DL** |

Each 4 more predicates multiply the cost by about 8: it grows exponentially with the depth of the guard cone.

**Readings.**
- **Growth at the base.** `norms-elaborate` (flat) and `norm-defaults-elaborate` (flat) grow at about n^5. The fit
  is MEASURED from 32 to 56, and the 64 to 128 values in the ESTIMATE cells extrapolate it.
- **Overruns at today's limit.** At 64, `norms-elaborate` and the joined-acts read already overrun their 5.9 s
  deadline on the flat shape. The overrun comes from the regeneration, not from reading the acts: the
  joined-acts parse adds 0.15 s to `norms-elaborate` at 32 and at 48. NormDefaults overruns at 24 with a guard
  cone.
- **Other limits refuse first above 64.** At 96, the soft document's formula hits `AST exceeds 10,000`. At 128,
  `soft-elaborate` and the document check hit the 256-predicate vocabulary limit: 55 frame predicates plus 128
  regulated plus the soft layer's generated predicates. A higher regulated limit alone gives the soft routes no
  room past about 96 with a frame of RSP's size.
- **Worst case against the RAISE criterion.** At 96 and at 128 the worst-case request of every kind except
  soft-rules overruns its deadline or is refused by another limit. No value above 64 passes "the worst case stays
  within its deadline with 2x margin", and 64 itself does not pass it for the flat `norms-elaborate`.

## 1c. Need: regulated predicates per keyed document

| document | today | without its merges | with the Nov 23 path rows | source |
|---|---|---|---|---|
| RSP (anthropic-rsp D1) | 64 of 64 (MEASURED, environment.d1.json) | 67 (PLAN 12 item 4: `s35-publish` and `s363-public-comments` merged, 3.4 step 1 UNFORMALISED) | 68: s33-evidence "may need a new act", +1 ESTIMATE (reviews/ops-width-20261114.md line 42) | MEASURED counts; the +1 is an ESTIMATE |
| PF (openai-preparedness) | 61 of 64 in d1, plus 2 in d2's own environment (MEASURED) | 61 | 62 to 171. The 110 spans UNFORMALISED with `waits: AP` (`unmapped_duty`) are MEASURED in spans.json. How many acts they share is not measured: the range runs from one act to one act per span. Ops-width counts 7 answers touched by AP spans | ESTIMATE range |
| blind R2 | 64 of 64 (stopped there) | | 78: 64 plus the 14 clauses left out (reviews/blind-rsp-build-20261114.md, step 3). Blind R3 already runs as a partition: "the dependency-complete non-r2 part (31 regulated + the query-time act)" | MEASURED from the review |
| FSF (safety-framework) | 27 of 64 (MEASURED) | 27 | 27 | MEASURED |

- **RSP and blind R2** need 68 and 78: within 96, but past 64.
- **PF's upper bound** (171) is past 128. No single frame of any measured width carries it.
- **Only partitioning scales.** Each component can stay small, and section 1d shows the components are small.

## 1d. Restructure (MEASURED on a scratch copy of usecases/anthropic-rsp)

**Setup.**
- Scratch tree `/tmp/translim/repo`: every top-level entry is a symlink to this checkout, with a real copy of
  `usecases/anthropic-rsp`.
- No use-case file of the checkout was changed.
- Recipe script: `rsp_split.py` (this directory). If the DRI picks RESTRUCTURE, PART 2 writes it up as the
  design note `docs/usecases/safetyfw/regulated-limit.md`.

**Recipe.**
1. **Link** two regulated predicates when any of these holds:
   - a rule on one names the other in its guard or carve-outs;
   - one is the other's permission dual;
   - their rules stand in a precedence (`over`) pair;
   - their rules are checked in one document (a conflict cluster or an opposite-sign pair).
2. **Split.** Frame A keeps every unregulated predicate and the regulated predicates left. Frame B is the same
   frame plus the moved components. Only whole components move.
3. **Route.** Each document is built per frame from the rules on that frame's predicates. A question about
   predicate p is asked of p's frame, and a conflict pair of the frame holding both rules.

**Results** (single runs, `VE_RUST_JSONL` = the pinned Rust binary of `ve-share-main`, same tree):

| run | frames | `run.py --check` | answers | wall |
|---|---|---|---|---|
| baseline (no split) | 64 | pass | 110 / 126 | 6 min 14 s |
| split, 3 moved (`advance_recommendations`, `argument_required`, `board_approved`; 2 of them question targets) | 61 + 3 | **pass**, results.json byte-identical | 110 / 126 | 5 min 38 s |
| split, 32 moved | 32 + 32 | **pass**, results.json byte-identical | 110 / 126 | 6 min 13 s |
| seeded bug (c): `--leak` moves `assessed_in_report` without `in_scope`, the guard of `f11-assess` | 63 + 1 | **fail**: `UnknownSymbol: Unknown predicate 'in_scope'` | n/a | 24 s |

- **The graph.** RSP's 64 regulated predicates form 60 components under step 1: 56 single predicates and 4 pairs.
  A split has wide room.
- **Routes that accept it.**
  - `soft-norms@0` through `SoftNormDocument`/`SoftEnvironment` (the Lean `soft-norms` mode) for the questions.
  - `norms@0` `check_conflict` for the conflict pairs.
  - Each frame is a separate environment within 64. No route refuses the split.
- **What a split costs.**
  - No measurable time: within the run-to-run spread.
  - One more environment per frame.
  - A frame-routing step in the case's harness: `document()`, `selected()` and `completed()` are asked of the
    predicate's frame, and the gap probe's document carries only frame A's rules.
- **Two changes for a case that actually needs more than 64 (ESTIMATE, not run).**
  - **Rule parsing.** Each rule must be parsed in its frame's environment. Today `T.parsed_rule` parses on the
    whole vocabulary, which would be refused above 64.
  - **The document artifact.** The D1 `ve-document@1` (`build_document.py`) holds one environment, so the excess
    units go to a further document beside D1, as D2 and D3 already are. PF's d2 environment is the same pattern.
- **Who does the adoption.** It is each case's next fix round (the follow-up row below), not this item.

**Restructure answers DRI question 3:** no route refuses the split.

## 2. PART 2

Waiting for DRI question 1's answer (section 5). Until it is answered, PART 1 and the tests are the deliverable.
Nothing in Lean, the spec or a use case was changed.

## 3. Tests

`tests/test_regulated_limit.py` (new, 16 tests, all pass on main's code, 4.3 s):

- **Sites** (accept exactly 64, refuse 65 with `ResourceLimit: regulated predicates`), one test per site through
  the service route that reaches it:
  - `Plain.decodeRegulatedAllIn` via the `environment` mode;
  - `Wire.decodeNormsEnvironment` via `norms`;
  - the soft route's decoder;
  - `norm-defaults`;
  - `Tree.check` on the elaborated document: 33 declarations, 64 parts accepted and 65 refused;
  - the Rust mirror.
- **Shadowed site.** `SoftNorms.checkW1` is not reachable with 65: the soft route refuses `acts@0` vocabularies
  (`InvalidInput: invalid vocabulary`, MEASURED), so its decoder refuses first. The docstring says so.
- **The split recipe.**
  - It moves whole components: dual, guard and precedence links.
  - It refuses a split that breaks a guard, dual or precedence link, and one that separates a conflict pair.
- **Not added (RAISE only):** "the 65th is accepted" and the grep test for a literal 64.

Unchanged and still passing: `tests/test_rsp_fidelity_fix.py::test_regulated_predicates_stay_within_lean_limit`,
the b6 CPU-deadline test, and the RSP `run.py --check` (section 1d baseline).

## 4. Seeded bugs

All four are recorded in `seeded-bugs.json`. Each was planted, seen to fail, and restored. No product code is
changed by this item: PART 1 adds docs and tests only.

| id | file | bug | caught by |
|---|---|---|---|
| a | lean/VE/Norms/Plain.lean | `decodeRegulatedAllIn` refuses exactly 64 (`>= 64`, off by one) | `test_plain_decoder_takes_the_limit_and_refuses_one_more[64-None]` (1 failed) |
| b | lean/VE/Norms/Tree.lean (+ twin NormDefaults/Check.lean) | `check` accepts the 65th (`> 65`) | `test_elaborated_document_takes_the_limit_and_refuses_one_more[32-1-...]` (1 failed) |
| c1 | rsp_split.py `--leak` | a split moves `assessed_in_report` without its rule's guard predicate `in_scope` | RSP `run.py --check` on the scratch copy: exit 1, `UnknownSymbol: Unknown predicate 'in_scope'` |
| c2 | rsp_split.py `links()` | a guard no longer links its predicate | `test_split_recipe_refuses_a_split_that_breaks_a_link[moved0-...]` and `test_split_recipe_moves_whole_components_only` (2 failed) |

## 5. DRI question and answer

Sent once with `msg.sh dri translim-predicates`:

> RAISE or RESTRUCTURE: measured worst case at 96/128 = norms-elaborate DL (over 6.2/6.5 s CPU) on both shapes at
> 128, flat at 96; norms-conflict DL at 128; acts parse DL; norm-defaults-elaborate DL from 24 (cone) and ~143 s at
> 64 flat (ESTIMATE, 73 s MEASURED at 56) vs 122 s; soft document refused by AST 10,000 at 96 and by the 256-predicate
> vocabulary at 128; even at 64 the flat norms-elaborate overruns its 5.9 s deadline. Restructure WORKS on RSP with
> answers unchanged (3 and 32 predicates in a second frame; run.py --check byte-identical, no measurable cost). Need:
> RSP 68, PF 62-171 (ESTIMATE), blind R2 78, FSF 27. Recommendation: NO to a spec-limit addendum; RESTRUCTURE (design
> note + one follow-up row per case). Yes to a spec-limit addendum raising regulated predicates to <N>?

The answer is quoted here when it comes. It had not come when the report was written.

## 6. ap-parse-indexb

**Not needed (MEASURED).**
- Reading every regulated act (joined, under `acts@0`) adds about 0.15 s to a `norms-elaborate` request at 32 and
  at 48 acts. That compares 0.56 with 0.40 s, and 3.62 with 3.47 s.
- The 64-act overrun is the regeneration's: `norms-elaborate` without joined acts overruns the same way.
- With RESTRUCTURE no document holds more than 64 acts, so a per-document parse budget has nothing to bound that
  the per-act step budget does not already bound.

## Notes for the DRI

- **Overruns within today's limit.** Two request shapes overrun their CPU deadline: `norms-elaborate` with 56 to 64
  regulated predicates, each with a guarded rule, and `norm-defaults-elaborate` with a guard cone of 24 or more
  `unspecified` predicates. Each is answered `CheckerUnavailable`, never a verdict, so no answer is wrong and no
  FOLLOW-UP is filed (override 3). It is a speed note for whoever owns `Flagged.regenerated` and NormDefaults'
  elaboration. The keyed cases do not hit it: RSP's rules sit in 60 small components.
- **Where a RAISE constant would live.** `VE.Limits` (lean/VE/Limits.lean) is the established single home of the
  runtime limits, stated in the service handshake and read by Python (`ve/limits.py`). The task's proposed new
  `lean/VE/Norms/Limits.lean` would be a second owner. The regulated limit is not in `VE.Limits` today, so the five
  literal sites above are not covered by `tests/test_lean_limits.py`'s literal check.
- **Act splits.** The elaborated document (act split) counts parts against the same 64. A case with joined acts
  reaches the limit at half the declarations, and the recipe applies to it unchanged.

FOLLOW-UP: none filed by this item for defects. The restructure adoption is a backlog row (kind feature, owner
"feature planner"), filed after the DRI's answer if the answer is RESTRUCTURE.

SIZE: see the final section.
