# Feature review: what `ve-green-readings-defaults` adds over `ve-green-senses`

Source: the pinned 184,893-byte constitution, unchanged (SHA-256 `fa10ed48…50dd`, `source/SOURCE.md`). Start point: the translation of run `20261006T1800Z` (`prev/`; run 20261007T0600Z left no files). The ledger (1,132 units), the main document and the three companions are byte-identical in this run.

## Merged since `ve-green-senses` (`git log --first-parent`, 315 files, 48 under `ve/`)

| Merged | What it is | Changes what a document can say? |
|---|---|---|
| `readings-defaults/integrate` | RD-0 statement spec; RD-1 in Lean: `fillDoc` (the unspecified-completion filling applied to a readings document), its four equalities (taking a reading, a choice or the superposed document commutes with filling) and separation under one shared filling; A4 wording (a reading is named by its own sentence); templates E30, E31, E32, R7 and filled-gap lines, registered but not wired into answers; `tools/lean_decided_share.py` | **No.** Admission, per-choice checks, the fold across choices, companions and components (RD-2a, RD-3, RD-4) are not built. `lean/VE/Readings/Wire.lean` `abstention` still refuses content beside `norm-defaults@0`; the merge report says its gate is evidence of the implemented surface, not that RD-2 to RD-5 exist |
| `lean-first` b5, b7, b8, b9, b11b, b13a | decision code for risk and alternatives, rights, reports (attribution), W6 quantity typing, speech acts and diagnostics moved from Python and Rust to Lean; A/B on 94,489 public records identical except 49 diagnostic wordings (listed) | No. Infrastructure; no new form of text |

Result: **zero units upgraded.** The feature the latest audit ranked first (executable reading sets with unspecified completion) is half built.

## Measured at this tag

* `ve document check` of the main, strict and default documents, `coverage`, and every rendering of them (and the pilot's expanded `rendered.md`): byte-identical to the previous run's (premises UNKNOWN, "non-assertion reading elaboration pending" for the main document).
* The s1 demonstration companion (soft chain, duties completed with `deny` by the companion, not by the translation): same verdicts, counts, identities and structure; **three wording leaves differ** (`readings.sets[3].pairs[0].text`, `readings.sets[4].pairs[5].text`, `readings.english[9]`) and 40 rendered lines. Cause: the A4 slot. Before: "Under reading 1, operator is permitted to. Under reading 2, operator is not permitted to." Now each reading is quoted as its own sentence ("Under *Every operator may give Claude each operator input, if at least one of the following holds: (a) …*"), which for the operator-permission rules runs to many lines. This is correct and unambiguous, but it is not short; the reader test the reviewers deferred (Fable C1) has not been run, and this run calls no model.
* All six carried probes (unspecified: 34 points, 21 SETTLED, 13 UNDECIDED, 0 CONFLICT; s1; risk; discourse; rights; senses) and the profile-combination probe: byte-identical. Probe case b of `probe_s1.py` (main plus one strict candidate with content) is still `UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented`.
* S2a on the demonstration companion: `ve document check` of `readings/s1.ve.md` 5 min 18 s (5 min 28 s before); the three conclusion queries (across readings, under *must*, under *should*) give the previous results exactly (85, 56, 88 s).
* `tools/lean_decided_share.py` on the main document and on the companion: no Lean answer across readings, so `decided_units` is empty and the Lean-decided share is 0.00% (the route that would emit `decided_units`, RD-3, is not built).

## What it shows about the language

* **F1 (still the top blocker).** Unchanged in kind, closer in substance: the Lean side (`fillDoc`, shared fillings for separation) now exists with its statements approved, so the remaining work is the route. Note the design's own limits (spec 0 and 1.1): the completion applies to the **norms chain** only, and every rule must be strict with no party, no exception and no `hard` flag. So when F1 lands, the force sets (strict vs *should* as a defeasible rule: u0036.s05, u0052.s01, u0125.s04.p2, u0156.s03, u0263.s04.p2) need their defeasible candidate on the soft chain, which the spec keeps out of scope (D2, RD-9); the operator-permission sets (u0062.s01, u0123.s01.p1, u0123.s02.p1, u0123.s03) fit better, with their limits written as guard conjuncts rather than exceptions. This is a prediction from the spec, not a measurement.
* **F22 to F26** (typed modals, `order@0`/`alternatives@0` beside norms, senses outside documents): unchanged.

## Missing features, in order of what they would unlock here (ledger tally `UNFORMALISED`)

norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50 (stale), counting 31, modality/belief 24, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1. Unchanged.

1. **The route for `readings@1` content beside `norm-defaults@0`** (RD-2a, RD-3): turns the nine READINGS units from "pending" into verdicts across readings without invented defaults, for the strict candidates; the defeasible candidates need the soft chain (outside the spec).
2. **A senses block in documents** (F25).
3. **Typed modals with action complements** (F22) and **graded normative force**; **graded quantities** (not integers) for the weighing factors.
