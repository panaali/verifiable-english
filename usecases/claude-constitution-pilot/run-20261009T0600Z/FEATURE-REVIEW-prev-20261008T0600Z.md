# Feature review: what `ve-green-rd-6a` adds over `ve-green-readings-defaults`

Source: the pinned 184,893-byte constitution, unchanged (`source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261007T1800Z` (`prev/`). 4 first-parent merges, 184 files, 25 under `ve/`.

| Merged | What it is | Changes what a document can say? |
|---|---|---|
| `lean-first/b6` (lf-6) | soft-norms decision code moved to Lean; the Python copy kept as a conformance oracle | No |
| `lean-first/b10b` (lf-10b) | norm-defaults decision code moved to Lean (`Explain`, layered report); the Python `UnspecifiedDocument.status`, `check_conflict` and report lines deleted | No for the language; **yes for the pilot's tooling**: `probe_unspecified.py` crashed (`'UnspecifiedDocument' object has no attribute 'status'`) and was ported to Lean's rows (`norm-defaults-status`, `-report`, `-conflict`; the frozen oracle only proposes evidence). Answers are the same |
| `readings-defaults/rd8` (rd-8) | **senses in `ve document`**: a `senses` front-matter key (packs, own, defaults); English fences read by Lean's sense reader; Lean's refusal texts relayed | **Yes**, in documents with English fences. The constitution translation has none (its units are structured), so no unit uses it |
| `readings-defaults/rd6a` (rd-6a) | Lean only: S2a with a carried base-premise family (`superpose_all_extra`, approved form refuted in Lean, an added hypothesis ruled in) | No: nothing calls it; `Wire.lean` `abstention` still refuses reading sets with content beside `norm-defaults@0` |

Result: **zero units upgraded by the language.** One unit changed status because of the lead's new rule (u0052.s01, READINGS to OPEN), not because of a feature.

## Senses probe (`probe_senses_doc.py`, `probes/senses-document-probe.json`)
Seven small documents with the constitution's words "corrigible" (means "not undermining legitimate human oversight", not "blind obedience", line 588) and "safe". A front-matter default, a written definition line and a parenthetical all give a CHECKED unit; no choice made is refused with Lean's text ("Sentence 1 uses corrigible, which has two senses here: … Add the line … or write corrigible (meaning blindly obedient)."); a default naming no sense is refused. What it cannot do: say that a word does **not** mean something (u0220.s02, "corrigibility does not mean blind obedience"); the nearest sentence ("Claude is not corrigible (meaning blindly obedient)") is a claim about Claude. A stipulation like u0220.s01 ("We call an AI that is broadly safe in this way 'corrigible'") also needs "in this way" (discourse) and is Anthropic's act (attribution), so it stays UNFORMALISED. A conjunction of two sentences, each with a word of the pack, was refused (case f).

## Measured at this tag
* `ve document check` of the main, strict and default documents: premises unchanged (UNKNOWN, "non-assertion reading elaboration pending" for the main document; a model for the companions). Differences from the previous run are only the repair's: 32 open terms, 8 reading sets, `judgment_use_required` gap now "none" (a rule without a guard), `choice_count` 144 (a running product when it first exceeds 64, order-dependent, not a count of choices).
* s1 demonstration companion: one set fewer (7, 17 candidates); still CONFLICT-FREE, route superposed, 4 SeparatedByDecisionOnly findings (not certified), check 2 min 21 s (5 min 18 s before). The three S2a conclusion queries give the previous verdicts and routes (UNKNOWN across readings, ALL under *must*, UNKNOWN under *should*).
* Probes: s1, risk, discourse, rights, senses byte-identical to the previous run's; unspecified: same 34 answers plus one new point (u0052.s01 SETTLED yes), gaps and conflict reports equal; profile combinations: the same accept/refuse outcomes (two refusal wordings changed). Lean-decided share 0.00% (no route emits `decided_units`).

## What it shows about the language
* **F1 (still the top blocker).** Reading sets with content beside `norm-defaults@0`: RD-1 and RD-6a add Lean statements only; the route (RD-2a, RD-3, RD-4) is not built. The seven reading sets that remain with a force or modal ambiguity stay without checked content.
* **Reading sets are now a small, auditable set.** Under the words-only rule the constitution keeps 8 sets: 4 for "should" (two of them resting on the document's own honesty wording), and the operator-permission block (u0062.s01, u0123.s01.p1, u0123.s02.p1, u0123.s03). Everything else the text could be read two ways stays a named open term, not a reading set.
* **New gap (senses):** a way to state what a word does not mean, and to carry the text's own definitions, would let u0220 (corrigibility) and similar passages move from UNFORMALISED.

## Missing features, in order of what they would unlock here (ledger tally `UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50 (stale), counting 31, modality/belief 24, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1. Unchanged.
1. The built route for `readings@1` content beside `norm-defaults@0` (RD-2a, RD-3).
2. Typed modals with action complements (F22) and graded quantities.
3. Statements about what a word means or does not mean, with the text's own stipulations (senses plus attribution plus discourse).
