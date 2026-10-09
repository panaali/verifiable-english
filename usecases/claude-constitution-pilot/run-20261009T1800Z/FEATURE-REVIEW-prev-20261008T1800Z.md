# Feature review: what `ve-green-lf-15b` adds over `ve-green-rd-6a`

Source: the pinned 184,893-byte constitution, unchanged (`source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261008T0600Z` (`prev/`). 6 first-parent merges since `ve-green-rd-6a`.

| Merged | What it is | Changes what a document can say? |
|---|---|---|
| `english-lean-e2` | Lean's English reader takes over admission and rendering | No; **availability regression** here: `render` answered `CheckerUnavailable: invalidGrammar lexicon: V3 predicate system_prompt_compliance_required` for the previous run's documents (an apostrophe in two act wordings). Repaired by wording (`reword.py`) |
| `lean-first/b15a`, `b16a`, `b15b` | search, evaluate and document steps move to Lean; Rust no longer reads source text | No |
| `readings-defaults/rd2a` (rd-2a) | Lean: admission, separation and choices of a `readings@1` set with content under `norm-defaults@0`; `fill_premises` and the filled document | **Yes** (Lean wire) |
| `readings-defaults/rd2b` (rd-2b) | relay and generators for the same: `ve document` loads, checks, renders and answers queries for such a document (enumerated route, at most 64 choices, evidence per choice) | **Yes**: the previous runs' top blocker F1 |

Result: **no unit changes status; all 8 reading sets can now carry Lean-checked content on the main chain.**

## What `nd.py` built (`readings/nd-*.ve.md`, `checked_content_main_chain` in `metrics.json`)
| Document | Sets | Choices | Conflict | Premises | Separating situations |
|---|---|---|---|---|---|
| `nd-force` | u0036.s05, u0125.s04.p2, u0156.s03, u0263.s04.p2 (strict, defeasible) | 16 | CONFLICT-FREE in all 16 | model in all 16 | 4 (2 outcome, 2 selects) |
| `nd-op` | u0062.s01 (2), u0123.s02.p1 (3), u0123.s03 (4) | 24 | CONFLICT-FREE in all 24 | model in 8, UNKNOWN in 16 (the two ability candidates, existence claims) | 10 |
| `nd-s01p1` | u0123.s01.p1 (3) | 3 | CONFLICT-FREE in all 3 | model in all 3 | 3 |
| `nd-all` | all 8 | 1,152 | `UNKNOWN: more than 64 compatible readings` | UNKNOWN | 17 (all admitted by Lean) |

Conclusion probe on `nd-force` ("no instance of Claude may directly deny being Claude"): UNKNOWN across readings, ALL under the strict reading (certificates), UNKNOWN under the defeasible one: the same verdicts the soft-chain companion gave, without its `deny` completion.

## What is still missing for these sets
* More than 64 choices per document: the companion split (RD-4a) is not merged; the fold across components (RD-4b) and Lean's fold (RD-3) neither. `lean_decided_share` stays 0.00%.
* A candidate whose content depends on another set's chosen reading (u0062.s01 and u0123.s02.p1 are limited by u0123.s03 "under its own reading"): couplings tie labels, not contents. These two carry the narrow-limits form, so pairing them with the wide reading of u0123.s03 is accepted and conflict-free but says nothing about the wide reading of the text.
* A defeasible rule beside `norm-defaults@0` (probe c: still refused). The defeasible candidates use one named exception predicate per set (an open term, as `exception: unstated` was).
* Findings for the language owners: Lean's English reader refuses an apostrophe in an act wording (V3) with a message that names the predicate but not the cause; the soft-chain `render` fails with `invalid soft name soft__excepted__clarify_ambiguity` for `readings/all-default.ve.md` (it was fine at rd-6a); filled-gap sentences list every point of every table (RD-2b deviation 2), so a separation sentence is very long.

## Missing features, ledger tally (`UNFORMALISED`), unchanged
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50, counting 31, modality/belief 24, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1.
Next, in order of unlock: the companion split and Lean fold (RD-4a, RD-3) so the sets are checked together; typed modals and graded quantities; statements about what a word does not mean.
