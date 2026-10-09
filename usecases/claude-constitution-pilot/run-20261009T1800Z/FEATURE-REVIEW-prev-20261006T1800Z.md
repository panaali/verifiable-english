# Feature review: what `ve-green-senses` adds over `ve-green-english-lean-s2`

Source: the pinned 184,893-byte constitution, unchanged (SHA-256 `fa10ed48…50dd`, `source/SOURCE.md`). Start point: the translation of run `20261005T1800Z` (`prev/`; run 20261006T0600Z left no files). The ledger (1,132 units), the main document and the three companions are byte-identical in this run.

## Merged since `ve-green-english-lean-s2` (`git log --first-parent`, 250 files, 27 under `ve/`)

| Merged | What it is | Changes what a document can say? |
|---|---|---|
| `senses/integrate` (senses) | word senses, read by the Lean reader: a pack gives a word numbered senses; one English line chooses a default (`In this document, corrigible means oversight respecting.`); a parenthetical gloss switches one occurrence; an unchosen ambiguous word makes the sentence an open reading set of named candidates. `ve senses check --env --pack source` is **admission only** (`conclusions: not_checked`) | **No.** No senses block in documents, no `--senses` in `ve check`, no render or glossary (B6/B7 open in `senses-integration-report.md`) |
| `english-lean-s3/integrate` | `order@0` (integer terms and comparisons) and `alternatives@0` (either/or, both/and) reader tables in Lean; risk wording ("more severe than") accepted | No: `ve document check` still refuses both beside norms (`norm document admission is FOL-only`, `InvalidInput: alternatives.block`) |
| `lean-first/b2`, `b10a`, `b11a`, `shapes` | environment handles in the service, shapes proved against encoders, difffuzz gates | No. Infrastructure |
| `infra/consolidate-b2` | one owner per piece of logic | No |

Result: **one genuinely new thing (lexical senses), zero units upgraded, because documents cannot carry it.**

## Measured at this tag

* `ve document check` of the main, strict, default and s1 documents, `coverage`, and every rendering: byte-identical to the previous run's (premises UNKNOWN, "non-assertion reading elaboration pending", for the main document). The pilot's expanded `rendered.md` is reproduced exactly.
* All five carried probes (unspecified: 34 points, 21 SETTLED, 13 UNDECIDED, 0 CONFLICT; s1; risk; discourse; rights) and the profile-combination probe (13 added profiles) are byte-identical.
* S2a (verdicts across readings) re-run on the demonstration companion `readings/s1.ve.md` (completes duties with `deny`, claims nothing): same verdicts, `ve document check` in 5 min 28 s (about 7 min before); conclusion queries 48 to 69 s. Still blocked from the main translation by **F1**: `readings@1` content beside `norm-defaults@0` is the named abstention.
* **Senses probe** (`probes/senses-probe.json`, `probe_senses.py`; outside any document, claims nothing). The constitution fixes one sense of "corrigible" (u0220.s01, "an AI that is broadly safe in this way") and rejects another ("blind obedience", u0220.s02, u0019.s02). With a two-sense pack: `Claude is corrigible.` is an **open** reading set of two named candidates (`sense__corrigible_1`, `sense__corrigible_2`, each with the English line that would choose it); the default line or `(meaning oversight respecting)` gives one reading; `Claude is not corrigible (meaning blindly obedient).` gives one reading (`not sense__corrigible_2(claude)`); `Claude is safe.` is open between "broadly safe" and "harmless". A gloss that is not a sense of the word, and a clause pair joined by a bare "and", are refused (`NoDerivation`). Pack rules the probe hit: a gloss is one to three lower-case words with no reserved word (the glosses "not undermining oversight" and "free from danger" were refused for that); a pack sort must use the document's noun and plural and an unused capital letter.

## What it shows about the language

* **F25 (new).** Lexical ambiguity now has a reading-set form (named senses, an English line that chooses each), but only outside documents. The constitution's `OPEN` vocabulary (36 open terms such as `broad_safety`, `ethical_harm`, `good_judgment`, `instruction_is_legitimate`) are open terms with a decider, not senses; senses would let a translation carry "which meaning of the word" as a checked reading set once documents accept a pack.
* **F26 (new).** `order@0` is integers only (`is less than`, `is at most`, sums, products): the constitution states no integer comparison, so the `quantities` blocker (119 units: probabilities, severity, breadth, "one in a million") is not touched; neither is `counting`.
* **F1, F14, F22, F23, F24** (as in `FEATURE-REVIEW-prev-20261005T1800Z.md`): unchanged.

## Missing features, in order of what they would unlock here (ledger tally `UNFORMALISED`)

norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50 (stale), counting 31, modality/belief 24, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1. Unchanged.

1. **`readings@1` content beside `norm-defaults@0`** (F1): lets S2a reach the main translation and moves the nine READINGS units from "pending" to verdicts.
2. **A senses block in documents** (F25): turns word-level polysemy into reading sets the document carries and checks.
3. **Typed modals with action complements** (F22) and **graded normative force**; **graded quantities** (not integers) for the weighing factors.
