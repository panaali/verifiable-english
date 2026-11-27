# refusal-number-build-1126: user-visible delta

Row plain-vocab-refusal-number-1126. Design reviews/refusal-number-design-1126.md (manage-agents; Codex design
challenge 0 SERIOUS, reviews/refusal-number-design-challenge-1126.md); orchestrator ruling 2026-11-26T21:02Z
(inbox/dri/done/20261126T210203Z-orchestrator-137562.md: Lean writes every sentence number, hard stop at 10 measured
trusted lines).

**What changes.** A document's English fence was read alone (`Service/Document.lean` `contentOf`, and Python's own
path `ve/document/load.py`), so a refused fence's text always said "Sentence 1", whichever fence it was. Now
`english.read` takes an optional `sentence_base` (a natural number, the sentences before the source; absent = 0), and
every per-sentence refusal text of authoring mode counts from it: NoDerivation, Ambiguous, every sentence rejection
(and a lexical `EmptySentence`), ConclusionWithoutPremise, IllTyped, Budget, and the `unproved` text of an obligation.
The `sentence` field, the spans, the diagnosis and the advice still index the source sent. With a base, the two
premise texts say the premises are the fence's own, because each fence is read alone: "Sentence 3 is marked as a
conclusion, and no earlier sentence in its fence is a premise." (without it, "no earlier sentence" would deny
sentences 1 and 2 above it; review B1). `contentOf` sends the fence's index in the body (the order of
the ```` ```ve ```` fences, `Loader.bodyScan`); Python's own path sends the same index from the same order
(`list(fences).index(unit id)`, only when it is not 0); Python never edits Lean's text.

| before (3-fence document, 2nd fence unreadable) | after |
| --- | --- |
| `SyntaxError: Sentence 1 has no reading with the current vocabulary. ...` | `SyntaxError: Sentence 2 has no reading with the current vocabulary. ...` |

Unchanged: the first fence's text, a single-fence document's text, every request without the field (`senses.read`,
the norm, question and command readers, every other caller), translation mode (one sentence, never a document fence:
the field is validated and the text numbers from 1 as before), the texts that name no sentence (UndeclaredEvaluative, the other lexical
texts). `english.grammar`, `english.check` and `english.question` refuse the field as an unknown field (it is
`english.read`'s alone, as `judgments` is; jt-3 review F1), so it is read in `readCase`, not `optionalFields`.
Known limit (design (a)): the number counts each earlier fence as one sentence, which the loader enforces for every
fence it accepts ("each VE fence must contain exactly one sentence"). A fence is read with a fresh discourse state,
so "uses a name before introducing it" and "it is not settled what "it" refers to" are about the fence alone, as
before this change; only the number moved. The senses route's numbering under
`senses.defaults` is not in this item (row senses-defaults-sentence-number).

Generated files that move: the grammar `actions_version` 50 -> 52 (`Fixed/Version.lean`, `ve/english_grammar/LOCK.json`:
`EnglishGrammar/Run.lean` is a hashed file), checker pins, lean/declarations.txt and the other outputs of
`tools/regen_generated.py --write`.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| 1 | `VE/EnglishGrammar/Run.lean`: **+6 V** (measured, `tools/trust_map.py --since main` on the final HEAD; two allowances in docs/trust-baseline.json, +6 and +1, total 7 with row 2): `readCase` +3 (reads `sentence_base`; the field list entry is a changed line), `authoring` +2 (the `EmptySentence` shift), `noPremiseText` +1 (the "in its fence" text, review B1); changed lines passing `base` (`budgetFields`, `unprovedText` +0). Diagnostic-only G[R] (not counted): `noReadingFields`, `rejectionText`. No new definition. K +0, S +0. | R16 | tests/test_refusal_sentence_number.py; `#guard`s in lean/VE/EnglishGrammar/JudgmentRunExamples.lean |
| 2 | `VE/Service/Document.lean`: **+1 V** (measured): `contentOf` sends the fence's index (`(fences.map Prod.fst).idxOf id`). | R16 | tests/test_refusal_sentence_number.py (Lean document mode) |

Seeded bugs (`mutants-run.json`, Python's path, 3 of 3 killed by tests/test_refusal_sentence_number.py): the loader
numbering by sorted unit ids instead of body order, the loader sending no base, the request dropping the field. The
Lean sites are each pinned by a test or `#guard` that asserts the text with a base (NoDerivation, Ambiguous, a
rejection, EmptySentence, ConclusionWithoutPremise, IllTyped, risk-every-cannot, `unproved`, `budgetFields`); Lean
mutants were not run (each needs a full rebuild). `authoring`'s own `Budget` branch is not reached by a cheap input,
so only `budgetFields` with a base is checked.

R16 ties pass: asked for in manage-agents FOLLOW-UPS.md ("## refusal-number-build-1126").
