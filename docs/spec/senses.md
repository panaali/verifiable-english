# Vocabulary out of the box: senses (statement specification)

> Status: statement specification, draft 2 (2026-10-05), branch `design/senses`. Draft 2 applies the
> statement review's FIX (`manage-agents/debates/senses-spec/`, Astra and Fable, converged in round 3); section
> 0.1 lists every edit and where it lands, and section 13.3 the applier's choices, the two corrections from the
> verification of draft 2 and the plan's alignment. **Nothing was run for draft 2**: the rows it adds or
> changes are marked *hand-derived* or *computed by a reviewer*, and the statements it changes have not been
> re-elaborated; both are the remaining conditions of G-S0 (7). The rest of this note describes draft 1.
>
> Draft 1: statement specification (2026-10-05). This is the item-1 statement
> spec (batch B0) of [senses-PLAN.md](senses-PLAN.md) draft 2 (the **plan**), which the plan review converged
> on by DRI ruling (`manage-agents/debates/design-senses/`, 2026-10-04). It writes out plan sections 2 to 4 on
> top of the S2 spec ([english-lean-s2.md](english-lean-s2.md), draft 5 with its integration amendment) and the
> base spec ([english-lean.md](english-lean.md)); a section number written `S2 2.6` or `base 2.9` refers to
> those, `plan 2.8` to the plan. **Nothing is proved and nothing is built.** What was run for this draft: a
> scratch file `lean/SpecStubs_senses.lean` (a stub, never committed) against the **merged S2
> build** (`main` at `1e68d6d6`, merged into this branch at `7746f24a`; Lean 4.24.0). The file holds the
> signature of 5.2 with prototype bodies, every statement of 5.3 as a definition of type `Prop` (all thirteen
> elaborate against the real `VE.EnglishGrammar` modules, not against interim stubs), one of them proved as a
> check of the stub (`wf_iff_no_failure`), and every fixture of section 8 marked *computed*, evaluated by
> `#eval` or `#guard` through S2's own `lex`, `Lexicon.failures`, `grammar`, `verdict`, `meaning`,
> `typedDocument`, `checkRendering` and `Extends` (section 12). The prototype bodies are B0's reading of the
> plan and are obligations on B1 to B5, not an implementation. Not run: anything in Python, the service, the
> identities, the display, any proof. Every `file:line` was read on 2026-10-05.

## 0. Scope, and what the computation changed

The senses layer gives each word numbered senses, lets a document choose one default per word in one English
line and switch any occurrence with a gloss, and never guesses: a bare word with several senses and no default
makes its sentence an open reading set. Lean owns every decision; a sense is an ordinary predicate of a
*projected* environment, and one reading per sentence is S2's theorem applied to the projection (plan section
0). This specification fixes the definitions (2), the English (3), the diagnostics (4), the Lean signature and
the exact statements (5), the requests to S2 (6), gates (7), the acceptance fixtures (8), limits (9), the
statement review checklist (10), open points (11), how the figures were computed (12) and the edits carried
over from the plan review (13).

Computing the fixtures on the merged S2 build overturned parts of the plan's hand-derived text. The statement
review and the DRI should read these first.

| # | Finding | Evidence | What this draft does |
|---|---|---|---|
| F1 | **The plan's joke does not read under S2 as merged.** S2 lexes a wording with a terminator appended (`sentenceTokens`, `Lexicon.lean:232`), so a mark that ends a wording is always glued to what follows; in a sentence the same mark followed by a space has the other flag, and `exact` terminals compare flags. `funny (meaning strange) is …` and `… strange, is …` therefore have no derivation | c3 to c6, c9: zero; s1: `stopped 1 noDerivation` (8.5, 8.7) | request **R3** to S2 (6.2), required for the brief's two forms in mid-sentence; no statement of 5.3 depends on it; every affected fixture has both values, *as merged* and *with R3* (R3 simulated in the stub, 12) |
| F2 | **Label letters are capitals.** The S1 lexer reads a label as capital letters and a number (`S1`; `Lexer.lean:87–93`), and S2's producer picks capitals (`_fluent_variable_letters`, `ve/printer.py:138–163`; read, not run). A lower-case pack letter never matches a label and differs from the document's letter for a shared sort | d20, j12b | W4: one capital ASCII letter; the fixture pack uses `J`, `S`, `P`, `N`, `R`, `Q` |
| F3 | **A pack sort lacked what an environment sort needs**, and a sense's arity was unbounded. Python's `Environment` requires `description` and, with a noun, both `singular` and `plural` (`ve/environment.py:479–485`), and the base profile allows one or two arguments (`:508`) | read, not run; d21 | `PackSort` gains `plural` and `description`; W4: one or two kinds |
| F4 | **`project_valid` had idle premises, and they were not the by-construction claim.** The plan's premises hold for a pack whose noun equals the selected noun of a document sort, where the projection is invalid | j13 | `project` always runs S2's `Lexicon.failures` on its result; `project_valid` is stated without premises (true by that check); the by-construction content is the proposed `project_total`, with premises over every key the document declares or selects (5.3) |
| F5 | **`typedDocument E []` is false**, so a document whose units are all open would be `illTyped`, and a text of preamble lines only would have no outcome | `#eval typedDocument EJ [] = false`; s16, n7 | the typed check runs when there is a resolved formula; a text with no body sentence is S2's `emptyDocument` (2.6) |
| F6 | Fixture values that differ from the plan: d2 (detail text), d11 (confounded: the added word `strange` is a gloss of two senses, so W2 fires first), j12 (the shared sort's letter rule fires first), s3 (needs a default to reach `illTyped`), s14 (a byte-order mark is a word character: `stopped 0 noDerivation`, not `lexical`), the order of the mixed report | 8.1, 8.4, 8.7 | the computed values stand; d11, j12 and s3 are rewritten so that each isolates its condition |

Four refinements are B0's own and are marked **(B0)** where they appear: `SenseUnit.after` (the state after a
unit, so that "the state the earlier units leave" is data and not an unproved lemma about S2); the proposed
statement `senses_unit_sound` for a resolved unit of a document that also has open units; `unneeded` as a
function; and a text for the zero-candidate case (`NoSenseFits`). Draft 1's fifth, W6 as a condition on
different words only, was false and is withdrawn (0.1, R1). Section 13.2 lists every difference from the plan.

### 0.1 What the statement review changed (draft 2)

The review converged on **FIX** (round 3). The W1, soft and P0 contracts are untouched; R3 keeps its
approval, versioning and regression gate (6.2). Every edit below is applied in this draft.

| # | Finding | Edit | Where |
|---|---|---|---|
| R1 | **`project_total` was false: W6's same-word exemption is unsound.** `near` 1 (gloss `beside`, wording `{0} is near bob`) and `near` 2 (gloss `beside bob`, wording `{0} is near`) pass draft 1's W1 to W7, yet both have the comma form `{0} is near, in the sense of beside bob`, so V4 of the projection fails whenever `near` is used (Astra r1 1, Fable r1 1) | W6 compares every pair of forms of two different senses, by `wordingKey`, except two bare forms of one word; checked, not argued | 2.2, 4.2, d2, d26, j15, 8.10 |
| R2 | A gloss part had no upper bound, so a form could exceed Python's 256-character verbalisation limit (`ve/environment.py:81–86`) or S1's `maxTextChars` (Fable r1 2) | each gloss part has 3 to 50 characters; every form of a sense has at most 256 characters; a pack sort's noun and plural likewise | 2.2 (W2, W3, W4), 4.2 |
| R3 | F3 was half applied: Python's `Environment` also needs identifier names that are not reserved, and non-empty descriptions (`ve/environment.py:28–29`, `:63–78`, `:470–474`) (Fable r1 3, Astra r2 5) | W4: a pack sort's name is an identifier, not reserved, not beginning with `sense__`; sort and sense descriptions are not empty | 2.2, 4.2, 5.2 |
| R4 | Python caps an environment at 32 sorts and 256 predicates (`ve/environment.py:465`, `ve/limits.py:6–7`); the count is over the document's environment and the projection together, so no pack check can hold it (Astra r2 5, Fable r3 2) | a projection fault `limit`; `project_total` takes the bound as a premise | 2.5 (step 5), 3.2, 5.2, 5.3, j16 |
| R5 | `senses_resolved_one_reading` and `senses_unit_sound` never tied `P` to the preamble's assignment: `A` was bound and unused (Fable r1 4) | both conclude `project D A E L (usedWords D body) = .ok P` | 5.3, 3.3 |
| R6 | 2.6 said "exactly one of formula and candidates"; the statements gave only "not both" (Fable r1 7) | `senses_unit_sound` concludes that every unit has a formula or a candidate | 5.3 |
| R7 | **Candidate discovery treated explicit switches as unresolved.** `Both the riddle is odd and the riddle is funny (meaning strange).` gave two candidates with one formula, differing in an idle choice for `funny` (Astra r1 2, computed) | `unresolvedIn` keeps a word without a default only when one of its occurrences is not switched (a token rule); `usedWords` unchanged | 2.6, 5.2, s22, 9 (L11) |
| R8 | **R3 as written differed from its simulation.** The request tested the end of the wording; the stub twinned every lexical row that ends in a mark. The object relative of `{0} tells (meaning says aloud) {1}` ends in `)` once ` {1}` is cut (`Rules.lean:96–98`) (Astra r1 3, Fable r2 3) | R3 tests each row after its cut; the simulation twins rows of `clauseRows` only; the R3 column is recomputed; "always" holds for the clause position only | 2.3, 3.1, 6.2, 12, c17, L12 |
| R9 | **Q4 had no favourable answer.** `Every joke that is funny, in the sense of strange, and is odd, in the sense of strange, and is funny is not funny.` has two derivations with R3: `guard.three-left` with `funny`'s closing-comma alias, and `guard.three-right` with `odd`'s (`RelationalFol.lean:198–199`) (Fable r1 5, Astra r2 1: 0 as merged, 2 with R3) | c16; Q4's rule, stated once: drop the comma forms if any c fixture is `many` in the column that ships; the DRI may revise the rule only with a fixture showing `one` | 2.3, 8.5, 11 |
| R10 | j13's text said "one kind under different nouns" for two kinds under one noun; 3.2 had no total map from `collision` to a text (Fable r1 6) | the map from `collision kind name sense` to its text, with a text for a pack kind whose noun the document uses. After verification: step 6 names one colliding pair from `clashes`, so `{wording}` always exists, and a text covers step 6 with no pair | 2.5 (step 6), 3.2, 5.2, j13, j15, j17 |
| R11 | The one-candidate text claimed a typing reason: in s20 `near` loses a candidate by derivation, not by kind (Astra r1 4) | "only {gloss} gives a reading of this sentence" | 3.2 |
| R12 | The two hints had no Lean function (Fable r1 7) | `noSenseFitsText`, `glossedNaturalRewrite` | 5.2 |
| R13 | A same-sort binary sense gets S2's quoted `relation.` row (`Rules.lean:182–190`), which has no headword token, so the span of 2.6 cannot cover it and "every sense its formula uses" overclaimed (Fable r1 7, r3 3; Astra r2 5) | a reader fault `quotedSense`: a sentence whose derivation uses that row of a sense predicate is refused, so `senseOccurrences`, `mixed_exact` and `senseMap_ids` hold as stated on accepted documents | 2.6, 3.2, 5.2, 5.4, s23 |

Not changed by the review: the signature of `candidates_complete`, which already ranges over `u.unresolved`
(R7 changes the definition, the text and the fixtures, not the statement).

## 1. Decisions

Plan D1 to D19 stand as the plan states them, with these amendments.

| # | Amendment | Where |
|---|---|---|
| D1, D2 | A pack sort declares its noun, plural, description and label letter; a sense has one or two kinds (F3) | 2.2 |
| D4 | Which positions the two gloss forms read in depends on R3 (F1): 3.1 gives both columns. Whether the comma forms stay is decided by Q4's rule in the column that ships (R9) | 2.3, 3.1, 6.2, 11 |
| D6 | A unit with no candidate is `stopped i noDerivation` with the `NoSenseFits` hint; the unit record carries the state after it (B0) | 2.6 |
| D8 | "S2 is untouched" holds for every statement and definition here; R3 is one requested change to S2's lexical rules, with its own gate (F1) | 6.2 |
| D12 | W6 compares every pair of forms of two different senses, except two bare forms of one word, which no assignment selects together (R1; draft 1's "different words only" is withdrawn) | 2.2 |
| D19 | The S2 build is merged, so B0's stub elaborated every statement against it; no interim interface was needed. G-S0b becomes "re-elaborate when S2 changes" (R3 in particular) | 7 |
| D20 (B0) | Sentence numbers in outcomes, faults and the sense map are zero-based indices into the whole text, preamble included (body unit `i` is sentence `k + i`); texts show them as S2's texts show a sentence index | 2.6 |

## 2. Definitions

### 2.1 Terms

Plan 2.1 stands. Added: a **part** of a text is a piece between single spaces (`String.splitOn " "`); the
**words** of a text are its maximal runs of ASCII letters, folded (`wordsOf`); the **head** of a sense in one of
its forms is the part that carries the word: the word itself, or, in an automatic negative that inflects it,
the part at the word's distance from the end (`tell` in `{0} does not tell {1}`); a form is **bare** when it has
no gloss and **decorated** when its head carries one (parenthetical or comma).

### 2.2 The dictionary

A pack file (the fixture pack `F` of section 8 is this file plus the last entry's two sorts):

```json
{"format": "ve.sense-pack@1", "name": "fixtures@1",
 "sorts": [{"name": "joke", "noun": "joke", "plural": "jokes", "description": "A joke.", "letter": "J"},
           {"name": "service", "noun": "service", "plural": "services", "description": "A service.", "letter": "S"},
           {"name": "person", "noun": "person", "plural": "persons", "description": "A person.", "letter": "P"},
           {"name": "number", "noun": "number", "plural": "numbers", "description": "A number.", "letter": "N"}],
 "senses": [
  {"word": "funny", "index": 1, "gloss": "amusing", "description": "causes laughter", "kinds": ["joke"],
   "wording": "{0} is funny"},
  {"word": "funny", "index": 2, "gloss": "strange", "description": "odd, hard to explain", "kinds": ["joke"],
   "wording": "{0} is funny"},
  {"word": "odd", "index": 1, "gloss": "strange", "description": "odd, hard to explain", "kinds": ["joke"],
   "wording": "{0} is odd"},
  {"word": "odd", "index": 2, "gloss": "uneven", "description": "not divisible by two", "kinds": ["number"],
   "wording": "{0} is odd"},
  {"word": "tells", "index": 1, "gloss": "says aloud", "description": "says the joke to someone",
   "kinds": ["person", "joke"], "wording": "{0} tells {1}"},
  {"word": "deployed", "index": 1, "gloss": "live", "description": "running in production",
   "kinds": ["service"], "wording": "{0} is deployed"},
  {"word": "reviewed", "index": 1, "gloss": "checked", "description": "examined by a reviewer",
   "kinds": ["service"], "wording": "{0} is reviewed"},
  {"word": "reviewed", "index": 2, "gloss": "rated", "description": "given a public rating",
   "kinds": ["service"], "wording": "{0} is reviewed"},
  {"word": "access", "index": 1, "gloss": "read", "description": "may read the resource",
   "kinds": ["principal", "resource"], "wording": "{0} may access {1}", "negative": "{0} may not access {1}"}
 ]}
```

Hidden from people: `index`, the ids, the JSON, the label letters' role. Shown: the word, the gloss, the
description, the wordings.

**`Dictionary.wf D docSorts`** holds when `Dictionary.failures D docSorts` is empty (`wf_iff_no_failure`).
`failures` lists every failed condition as (condition, word or pack or kind, detail), in the order of the table
and, within a row, in the order written; `detail` is the English text of 4.2. `docSorts` are the sort names of
the document's environment.

| # | Condition, exactly |
|---|---|
| W1 | **Words.** Each sense's word has 2 to 50 characters, all `a` to `z`, and is not in `reservedWords`. Within one pack, and within the document's own senses, the indices of a word's senses, sorted, are `1` to `n`. No word has senses in two packs. No own sense has the word of a pack sense |
| W2 | **Glosses.** A gloss has one to three parts, each of 3 to 50 characters, all `a` to `z`, none in `reservedWords`; it is not the sense's word; it is not a word of the dictionary. No two senses of one word have glosses with one `wordingKey` |
| W3 | **Wording.** `shapeOk wording kinds.length` (S1); the first part is `{0}`; the word is exactly one of the parts and exactly one of the words of the text; the text has no `(`, `)` or `.`; none of its words is `means` or `meaning`; its words do not contain `in the sense of` in a row. Every form of the sense (`s.bareForms ++ s.decoratedForms`, 2.3) has at most 256 characters (`maxFormChars`) |
| W4 | **Kinds, sorts and descriptions.** A sense has one or two kinds, and a description that is not empty. A pack sense's kinds are sorts of its pack; an own sense's kinds are sorts of the document (`docSorts`) or of a pack. A pack sort's name matches `[a-z][a-z0-9_]*`, has at most 64 characters, is not a word of `schemaReserved`, does not match `x` followed by one or more digits, and does not begin with `sense__`. A pack sort's description is not empty. Its noun is not empty, has no hole, has at most 256 characters and lexes as one sentence (`sentenceTokens`); its plural is not empty, has no hole and has at most 256 characters; its letter is one character `A` to `Z`. A sort name declared by two packs is declared with the same noun, plural, description and letter. Two sorts of the dictionary with different names have different letters, and nouns with different `wordingKey`s |
| W5 | **Negative.** When `negativeTemplate wording arity` (S1) is `some`, the sense declares no negative. When it is `none`, a declared negative differs from the wording and passes every condition of W3 |
| W6 | **Distinctness of forms.** For every two different senses of the dictionary, no form of one has the `wordingKey` of a form of the other, where the forms of a sense are its bare forms (the wording and the bare negative) and its decorated forms (2.3), with one exception: two **bare** forms of two senses of the **same** word are not compared, since at most one of the two is the default under any assignment (d1). No form of a sense has the `wordingKey` of a pack sort's noun or plural. One failure is reported per pair of senses, in the order of `D.senses`, naming the first form of the earlier sense, in the order `bareForms ++ decoratedForms`, whose key a compared form of the later one has |
| W7 | **Reserved phrase.** The words of a wording, a declared negative, a gloss, a noun or a plural do not contain `in this document` in a row |

W6 is what makes V4 of the projected lexicon hold among the senses (D12): under one assignment the projection
selects, per sense, either its bare forms (the default) or decorated ones, and W6 has compared every pair that
two senses can select together. For two senses of one word the comparison is **checked, not argued**: different
glosses (W2) do not keep the decorated forms apart, because the comma form without its closing comma lets one
sense's gloss run on into what follows the other's word (d26: `near` with glosses `beside` and `beside bob`
and wordings `{0} is near bob` and `{0} is near` share `{0} is near, in the sense of beside bob`). A bare form
of one sense never equals a decorated form of another sense of the same word, because W3 keeps `(` and
`in the sense of` out of a wording; W6 compares them all the same. Nothing in W1 to W7 constrains the arity
or the literal words of two senses of one word against each other beyond W6: `{0} is near bob` (one kind) and
`{0} is near {1}` (two) are both legal senses of `near` (d18), which is why the state check of 2.6 exists.

The bounds of W2 to W4 make the projected JSON acceptable to Python's `Environment` (`ve/environment.py`:
identifiers `:29` and `:63–72`, reserved schema names `:28` and `:473`, non-empty descriptions `:75–78`,
verbalisations of at most 256 characters `:81–86`; read, not run). Python's caps on the number of sorts and
predicates (`:465`) are over the document and the projection together, so they are the projection's `limit`
check (2.5, step 5), not a condition of the dictionary.

`reservedWords` is one Lean list: the words of Python's `_RESERVED` (`ve/english.py:44–47` with
`_LOGICAL_WORDS`, `ve/printer.py:93`), plus `means`, `meaning` and `document` (D13). `schemaReserved` is the
Lean copy of Python's schema list `RESERVED` (`ve/environment.py:28`), which W4 needs for sort names; it is
data that E2 retires with the Python side, as `reservedWords` is.

### 2.3 The forms of a sense

All forms are computed from the sense's wording, by parts.

| Function | Value |
|---|---|
| `s.headIn t` | `some s.word` when the word is a part of `t`; otherwise, with `d` the word's distance from the end of `s.wording`'s parts, the part of `t` at distance `d` from its end, when there is one |
| `s.decorate t deco` | `t` with the **last** part equal to its head replaced by `deco head`; `t` when it has no head |
| `s.glossed t` | `s.decorate t` with `head (meaning gloss)` |
| `s.commaForms t` | `s.decorate t` with `head, in the sense of gloss,` and with `head, in the sense of gloss` |
| `s.selectedWording isDefault` | the wording for the default, `s.glossed s.wording` otherwise |
| `s.automaticNegative isDefault` | `negativeTemplate (s.selectedWording isDefault) s.arity` |
| `s.fixedNegative isDefault` | the declared negative, glossed when the sense is not the default |
| `s.selectedNegative isDefault` | the fixed negative when one is declared, else the automatic one |
| `s.bareNegative` | `s.selectedNegative true` |
| `s.aliases isDefault` | with polarity: the two comma forms of the wording (`false`); the two comma forms of the bare negative, when there is one (`true`); and, for the default only, `s.glossed s.wording` (`false`) and the glossed bare negative (`true`). Repeats dropped |
| `s.bareForms` | the wording and the bare negative |
| `s.decoratedForms` | the glossed wording, its comma forms, the glossed bare negative, its comma forms, and `s.selectedNegative false` |
| `s.headwordTokens` | the word and the head of the bare negative, folded, repeats dropped |

"Last part" matters for one statement only: `glossed_negative` holds for every sense, including a malformed one
whose word is `is` or `{0}`, because the last occurrence is the adjective's own position. Under W3 the word
occurs once and "last" is "the".

Computed on the fixture pack:

| Sense | Selected wording, not default | Selected negative, not default | Aliases as default | Headword tokens |
|---|---|---|---|---|
| `funny` 1 | `{0} is funny (meaning amusing)` | `{0} is not funny (meaning amusing)` | `{0} is funny, in the sense of amusing,`; `{0} is funny, in the sense of amusing`; `{0} is not funny, in the sense of amusing,` (negated); `{0} is not funny, in the sense of amusing` (negated); `{0} is funny (meaning amusing)`; `{0} is not funny (meaning amusing)` (negated) | `funny` |
| `tells` 1 | `{0} tells (meaning says aloud) {1}` | `{0} does not tell (meaning says aloud) {1}` | `{0} tells, in the sense of says aloud, {1}`; `{0} tells, in the sense of says aloud {1}`; the same two of `{0} does not tell …` (negated); `{0} tells (meaning says aloud) {1}`; `{0} does not tell (meaning says aloud) {1}` (negated) | `tells`, `tell` |
| `access` 1 | `{0} may access (meaning read) {1}` | `{0} may not access (meaning read) {1}` (the declared negative, glossed) | the comma forms of `{0} may access {1}` and of `{0} may not access {1}` (negated), and the two glossed forms | `access` |

**Negatives.** No pack writes a negative for a wording that `negativeTemplate` negates (W5): `{0} is funny`
gives `{0} is not funny`, `{0} tells {1}` gives `{0} does not tell {1}`, and the glossed wording gives the
glossed negative (`glossed_negative` for the simple adjectives; computed for `tells`). A declared negative
(`access`) enters the projection as a profile-fixed negative, V5's exception. One corner is a limit, not a
fault: an idiom in the past tense (`{0} voted for {1}`) has an automatic negative only in its bare form, because
`negativeTemplate` looks the wording up in S1's idiom list; such a sense, when it is not the default, has no
selected negative (L11).

**The simple-adjective families of S2.** A default sense whose wording is `{0} is w` with `w` one lower-case
word gets S2's adjective, natural-subject and copula rules (`adjectiveOf`, `Rules.lean:134`), so
`Every funny joke is odd.` reads as S2 reads it (s9). A glossed wording is not of that shape and has the
clause and relative forms only (L3, s10).

**Spacing, and F1.** S2 turns a wording into rule symbols by lexing it with `.` appended (`wordingTokens`,
`Lexicon.lean:256`); a word becomes a `content` terminal and every other token an `exact` terminal that
compares both glue flags (`Token.lean:77`). So inside a form the spacing is exact, as the plan says: `(` is not
glued before and is glued after, `)` is glued before, the comma is glued before and not after; `funny ( meaning
strange )` has no reading (c7). The same lexing makes the **last** token of a wording glued after, because the
appended terminator follows it. A sense whose word ends its wording (every adjective) therefore reads in a
glossed form only where a mark follows directly. The same holds for every row that S2 builds by cutting a
wording: the object relative of `{0} tells {1}` is lexed from `{0} tells` (`clauseRows`, `Rules.lean:96–98`),
so the object relative of the glossed `tells` ends in a glued `)` although its wording ends in a hole:

| Written | As merged | With R3 |
|---|---|---|
| `The riddle is funny (meaning strange).` | one | one |
| `Every joke that is funny (meaning strange) is not funny.` | **zero** | one |
| `The riddle is funny, in the sense of strange.` | one | one |
| `Every joke that is funny, in the sense of strange, is not funny.` | **zero** | one |
| `Every joke that is funny, in the sense of strange is not funny.` (no closing comma) | one | one |
| `Alice tells (meaning says aloud) the riddle.` and both comma forms of `tells` (clause position) | one | one |
| `Every joke that alice tells (meaning says aloud) is odd (meaning strange).` (object relative) | **zero** | one |
| `Every joke that is funny, in the sense of strange, and is odd, in the sense of strange, and is funny is not funny.` (c16) | zero | **two** |

R3 (6.2) asks S2 to give each lexical row of `clauseRows` that, after its cut, ends in a mark a twin whose
last mark is not glued after. Both columns are in 8.5; the R3 column is recomputed under that restricted
simulation (12). Q4 has no favourable answer: with R3, c16 has two derivations, one through `funny`'s
closing-comma alias under `guard.three-left` and one through `odd`'s under `guard.three-right`
(`RelationalFol.lean:198–199`). Q4's rule (11) is: **drop the comma forms if any c fixture is `many` in the
column that ships.** So if R3 ships, the comma forms are dropped and the parenthetical form alone remains,
unless the DRI revises the rule with a fixture showing `one`; as merged, no c fixture is `many`. Until R3 and
Q4 are decided, the definitions here keep the comma forms; dropping them removes `s.commaForms` from
`s.aliases` and `s.decoratedForms` and changes j1's alias count and the c rows that use a comma form.

### 2.4 Documents: preamble, defaults, body

**Shape.** A sentence is **preamble-shaped** (`preambleShaped`) when its first four tokens are three words that
fold to `in`, `this`, `document` and a comma glued before. The test reads no dictionary. Both directions are
fixtures (a1; a7, a13, a14).

**Lines.** `preambleGrammar D` has one rule per sense of `D.senses`, in order, rule `i` for sense `i`:
`kw in`, `kw this`, `kw document`, the comma glued before and not after, `content word`, `kw means`, then one
`content` terminal per part of the gloss; start symbol 0, one nonterminal of rank 0. It is well-formed and
terminator-free by construction (computed for `F`: 9 rules, both true). `readLine D b i w`, for a shaped
sentence `w` that is sentence `i` of the text, is `verdict (preambleGrammar D) b w`:

| Verdict | Result |
|---|---|
| `none` | `preambleBudget i` |
| `some (.one (node r _))` | the sense `D.senses[r]` |
| `some .zero`, and the fifth token is a word that is no word of `D` | `unknownWord i word` |
| `some .zero`, the fifth token is a word of `D`, the sixth folds to `means`, at least one token follows, all the tokens after it are words, and their folded texts joined by spaces are no gloss of that word | `unknownGloss i word gloss` |
| anything else (no `means`, no gloss, a capital in a fixed word, a comma glued after; and `many`, which W2 excludes) | `malformedPreamble i` |

**The preamble.** `readPreamble D b sents` reads the leading shaped sentences in order. A line whose word
already has a line is `repeatedDefault i word`. At the first sentence that is not shaped the body starts; a
shaped sentence anywhere after it is `preambleLate j`, with `j` that sentence's index, whatever the body
sentences before it are. The result is the assignment, in line order, and the number of lines `k`. The preamble
is the reader's one channel for defaults (D5): `readWithSenses` takes no assignment.

**Defaults.** `defaultOf D A w` is the assigned sense, else the only sense when `w` has exactly one, else none.
`unneeded D A` lists the assigned words that have one sense; their lines change nothing (j5) and are reported,
never refused. `Assignment.lines D A` is one line `In this document, <word> means <gloss>.` per default, in
the assignment's own order, joined by line breaks; reading it back gives the assignment (`lines_read`, a10).
`Assignment.wf D A` holds when no word is assigned twice and every assigned index is a sense of its word.

**Body.** The sentences after the preamble. A text with no body sentence is `lexical emptyDocument` (F5).

**`ve-document@1`.** Plan 2.4 stands: the Lean `document` mode renders front-matter defaults with
`Assignment.lines` and prepends them to the source (B11).

### 2.5 The projection onto S2's lexicon

**Used words.** `usedWords D sents` are the words of `D`, in `D`'s order, one of whose senses has a headword
token equal to the folded text of some word token of `sents` outside a gloss (D18; `unglossed`, 2.6, fix
round). A verb written only negatively is found through `tell` (j11); a gloss is no headword (`The riddle is
strange.` uses no word of `F`), and a word inside a gloss is no occurrence of that word.

**`project D A E L used`**, for the document's environment `E` and its own lexicon `L` (the request's, from
S2's one producer; `readWithSenses` checks `L.valid E {}` first). With `senses` the senses of the used words
of `D` in `D`'s order, `isDefault s` true when `defaultOf D A s.word` is `s`, a pack sort **shared** when `E`
has a sort of its name and **fresh** otherwise, the steps are, in order:

1. a shared sort whose noun's `wordingKey` is not that of `L`'s noun for it: `collision "sort" name ""`;
2. a shared sort whose letter is not `L`'s letter for it: `collision "letter" letter name`;
3. a fresh sort whose letter is a letter of `L`: `collision "letter" letter name`;
4. a fresh sort name or a sense symbol that is the name of a sort, predicate or constant of `E`:
   `collision "name" name ""`;
5. the projected environment would have more than `maxSorts` (32) sorts: `limit "sorts"`; else more than
   `maxPredicates` (256) predicates: `limit "predicates"`. The counts are `E.sorts.length` plus the fresh
   sorts, and `E.predicates.length` plus the senses of the used words; the bounds are Python's
   (`ve/limits.py:6–7`, checked at `ve/environment.py:465`);
6. the projection is built (below) and S2's `Lexicon.failures` is run on it. No failure: `ok`. Otherwise the
   fault names one **colliding pair**, taken from `clashes P.env P.lexicon` (5.2): for each selection of
   `P.lexicon` in S2's V4 order (wordings, negatives, aliases, nouns, spellings, each list sorted by symbol),
   each other symbol that declares or selects a text with the same `wordingKey`, as `(kind, name, kind₂,
   name₂, text)`, with `text` the selection's. The pair is the first in which one side is a symbol of the
   document and the other a sense symbol or a fresh sort, else the first: `collision kind name sense`, with
   `(kind, name)` the document's side (else the selection's) and `sense` the other side's name; the pair's
   `text` is the shared wording of 3.2. When `clashes` is empty, so that every failure is of V1, V2, V3 or V5
   (no fixture reaches this): `collision cond name ""`, with `(cond, kind, name)` the first failure. Whether
   the projection is refused is decided by S2's `Lexicon.failures` alone; `clashes` repeats V4's comparison
   (S2's `owners` and `selections` are local to `Lexicon.failures`) only to name the pair, and the symbol of
   every V4 failure is the selection side of some clash (tested). No rule of V1 to V5 is re-implemented as a
   decision.

| Part | Content |
|---|---|
| `env` | `E` with: the fresh sorts appended, each with its noun as declared noun; one predicate per sense appended, named `sense__<word>_<n>`, with `args` the kinds, declared `wording` the selected wording and declared `negative` the automatic negative when there is one; `forms.negatives` extended by the fixed negative of each sense that declares one; `forms.aliases` extended by `s.aliases (isDefault s)` under each sense's symbol, with polarity (these are fixed by the projection, not by a profile block); `source` the projected JSON |
| `lexicon` | `L`'s entries, plus the fresh sorts' nouns and letters, each sense's selected wording, its selected negative when there is one, and the same aliases; `spellings` unchanged. Each list is sorted by symbol, stably, so the projection has one form whatever order the request listed `L` in |
| `envJson` | `E.source` with, under `vocabulary.sorts`, one entry per fresh sort (`description`, and `verbalisation` with `singular` and `plural`), and, under `vocabulary.predicates`, one entry per sense (`arguments`, `description`, `verbalisation` the selected wording, `negative_verbalisation` the automatic negative when there is one). A declared negative is not written there: under S2 alone it would fail V5 |
| `map` | per sense: its symbol, the sense, `isDefault` |

`project` appends and never chooses (Q7): `L`'s selections are kept as they are, and a pack's letters are the
pack's. A stored `envJson` is an environment like any other: decoded by `Env.decode` and read by S2 alone
with the declared wordings and no alias, it gives the same formulas for bare defaults and for the
parenthetical forms (j8, computed on the Lean side).

**Extension.** `used ⊆ used2` gives `Extends` (S2 2.13, `Extends.lean:29`) between the two projections
(`project_extends`; q1 computed with a `Decidable` instance for `Extends`), and a changed default does not
(q2).

### 2.6 Reading with senses

`readWithSenses D E L b s`, in this order; the first step that fails decides the outcome.

1. `D.failures (E.sorts.map (·.name))` not empty: `fault (invalidDictionary f)` with the first failure.
2. `lex s` fails: `lexical r`.
3. `readPreamble D b` on the sentences fails: `fault f`. Otherwise the assignment `A` and the line count `k`.
4. No body sentence: `lexical emptyDocument`.
5. `L.valid E {}` false: `invalidGrammar lexicon`.
6. `used := usedWords D body`; `project D A E L used` fails: `fault f`. Otherwise the projection `P`.
7. S2's checks on `P`, called, not copied (`Lexicon.valid`, `Grammar.wf`, `terminatorFree`, `Grammar.typed`
   and the start type, in `read`'s order, `Read.lean:32–36`): a failure is `invalidGrammar why`.
8. The body sentences are read in order from `DState.init` with `readSentence` under `grammar P.env
   P.lexicon`, `meaning` and the budget `b`. For body sentence `i` (sentence `k + i`) from the state `st`:
   - `.ok F m` with successor `st2`: the unit is resolved: `⟨some (F, m), [], [], st2⟩`, unless its
     derivation uses a quoted-name row (below).
   - `noDerivation`: let `words` be the used words of this sentence that have no default under `A` and an
     **unswitched** occurrence in it (`unresolvedIn`, below). No such word: `stopped (k + i) noDerivation`,
     S2's outcome. More than `candidateCap`
     (8) choices of one sense per word: `fault (tooManyCandidates (k + i) words)`; the choices are counted by
     `choiceCount`, the product of the words' sense counts capped at `candidateCap + 1` word by word, never by
     building them (`choiceCount_gt_iff`; fix round, A1: thirty two-sense words stop at once). Otherwise every choice of
     `choicesOf D words` (the words in `D`'s order, the senses in theirs) is tried in order: `project D
     (A.extend choice) E L used` (a failure is that `fault`), S2's checks on it (a failure is
     `invalidGrammar`), then `readSentence` under it from the same `st`. **Typed admission:** the choice is a
     candidate exactly when the outcome is `.ok F m` and `typedDocument P2.env [F]` holds; `noDerivation` and
     an ill-typed formula drop the choice; `.budget`, `.ambiguous` and `.rejected` are `stopped (k + i) o`.
     No candidate: `stopped (k + i) noDerivation`, with the hint `NoSenseFits` (3.2). **Successor states:**
     when some candidate's successor state differs from the first candidate's, `fault (candidatesDiverge
     (k + i) words why)`, with `why` `referent x` for the first constant that one of the two states has and
     the other lacks, else `binder`. Otherwise the unit is open: `⟨none, candidates, words, st2⟩` with `st2`
     the common successor. One candidate is still an open unit; nothing is guessed (D15, s16).
   - any other outcome `o`: `stopped (k + i) o`.

   **Switched occurrences (R7).** An occurrence of a headword token of a word in sentence `w` (a word token
   whose folded text is one of the word's `headwordTokens`) is **switched** when the tokens after it are `(`
   and a word folding to `meaning`, or a comma and four words folding to `in`, `the`, `sense`, `of`.
   `unresolvedIn D A w` keeps a used word of `w` with no default under `A` only when one of its occurrences in
   `w` is not switched. A glossed occurrence names its sense whatever the assignment, so a choice for it would
   only add candidates that differ in nothing (s22). A switched occurrence still puts its word's senses into
   the projection. The rule errs safely: a word it excludes by mistake gets no
   bare rule, so the sentence can lose a reading and never gains a guessed one; the one such loss known is the
   glossed negative of a past-tense idiom (L11).

   **Words inside a gloss (fix round, Fable B3).** The mark after a switched head and the gloss after the
   mark are not occurrences of any word: `unglossed D w` keeps every token of `w` but those, and both
   `usedWords` and `unswitchedIn` read only its tokens. The gloss is the fewest tokens, over the senses of `D`
   with the head as a headword token, that fold to the parts of one of their glosses, followed by `)` in the
   parenthetical form; when no gloss matches, nothing is skipped. So `funny` 2 glossed `odd thing` adds no
   choice for `odd` in `… is funny (meaning odd thing).`, nor does `tell apart` one for `tells`; without the
   rule both gave candidates that differ in nothing, and could cause a spurious `tooManyCandidates`,
   collision or limit. Skipping the shortest matching gloss errs safely in the same way: a skipped token
   could only lose a rule, and S2 has no row that reads a token after a gloss mark other than the gloss forms
   themselves. Applied on the DRI's instruction to fix every A and B finding of the integration review
   (2026-10-06); regression rows in `VE.Senses.Examples` and `test_gloss_words_are_not_occurrences`.

   **Quoted names (R13).** S2 gives every binary predicate whose two arguments have one sort a `relation.`
   row on its quoted name (`Rules.lean:182–190`), used by the named-reachability sentence. That row has no
   headword token, so the sense map cannot span it. When the derivation of a resolved unit, or of a choice
   that would be a candidate, uses a `relation.` row of a predicate that `P.map` (or the choice's `P2.map`)
   names, the reader stops: `fault (quotedSense (k + i) word)`, with the sense's word. The derivation is the
   one `verdict` returns for the sentence (`.one t`), as for the sense map.

9. When some unit is resolved, `typedDocument P.env` of the resolved formulas must hold, else `illTyped`
   (F5: `typedDocument` is false on the empty list).
10. `ok units senses mixed unused P`, with the sense map, `mixedOf P units` and the unused defaults (the
    assigned words not in `used`).

**Units.** `SenseUnit` has `formula` (the formula and mark of a resolved unit), `candidates`, `unresolved` and
`after`, the state after the unit **(B0)**. In an `ok` outcome exactly one of `formula.isSome` and `candidates
≠ []` holds: at least one by `senses_unit_sound`'s first conjunct, not both by its second and by
`senses_candidate_sound` (R6). `stateBefore units i` is `DState.init` for `i = 0`
and `units[i-1].after` otherwise. The successor check is reachable: S2 computes the state after a sentence
from the constants of its formula (`DState.after`, `Actions.lean:113`), and two senses of one word may differ
in arity (s17).

**Candidates.** A `Candidate` has its `choice`, its formula and mark, and its **resolving lines**,
`Assignment.lines D (A.extend choice)`. Rendering a candidate and checking that rendering use the projection
of its choice (`project D (A.extend choice) E L used`, through the service's `senses.project` mode, plan 2.6);
the base projection has no bare rule for the unresolved word.

**The sense map**, keyed by written occurrence. For the tree `t` of a sentence (`verdict`'s `.one t`, the tree
`readSentence` reads) and each node of `t` whose rule is a lexical rule with a predicate that `P.map` names
(S2's `pred`, `relSubject`, `relObject`, `adjective`, `natSubject`, `copulaRel` actions), one
`SenseOccurrence`: the sentence index, a token span, the symbol, `isDefault` (whether the sense is its word's
default, also when it is written with its gloss, c8) and the candidate index (`none` for a resolved unit; for
an open unit the occurrences of each candidate's tree under its own projection, with that candidate's index).
The span starts at the first child of the node that is a word token folding to a headword token of the sense,
and covers its gloss when one follows among the node's children: `(` to `)`, or `, in the sense of` and the
gloss with its closing comma when the rule has one; when no child is such a token, which W3 excludes, the
span is the node's. No accepted derivation uses a `relation.` row of a sense predicate (`quotedSense`
above), so every sense atom of an accepted formula comes from a node this rule spans. One written occurrence
may stand for several formula occurrences: S2's subject
coordination reads `Legacy, beta and gamma are deployed.` into three atoms from one adjective token (s15), so
`senseMap_ids` relates the map and the formula as sets.

**Mixed.** `senseOccurrences P A` are the predicate names of `A`, with repetition, that `P.map` names.
`mixedOf P units`: for each word of `P.map`, the sense symbols of its occurrences in the resolved formulas, in
order of first occurrence, repeats dropped, when there are two or more (`mixed_exact`). Candidates are not
counted.

**Flip models.** For two candidates `c`, `d` of one unit: the valuation that makes true exactly the senses `c`
chooses and `d` does not, every other predicate false for all arguments; if the two formulas differ in truth
under it, it distinguishes the pair; else the same with `c` and `d` exchanged; else the pair is
`undistinguished` and no reading set is proposed for the unit (plan 2.6, step 7). The model is built over one
entity per sort and constant the unit mentions and is evaluated by the existing evaluator (`VE.Eval`); the
fixtures of 8.7 give the truth values, computed with constant-valued predicates.

### 2.7 Identities, display, ownership

Plan 2.7 (identities: S2's six of the projection, `dictionary_id`, `senses_version` with its own lock), plan
2.8 (display) and plan 2.9 (ownership) stand. Three notes. The pack file's canonical JSON, which
`dictionary_id` digests, now has the sort fields of 2.2. `unneeded D A` is the Lean source of the `Unneeded`
warning. R3, if accepted, changes a locked S2 file, so S2's `actions_version` moves once for every
`english.read` response: that is S2's own versioning and the one exception to D10 this specification asks for
(6.2).

### 2.8 What is trusted, proved and tested

| Layer | Items |
|---|---|
| Trusted definitions | the forms of 2.3; `Dictionary.failures`; `preambleShaped`, `preambleGrammar`, `readPreamble`; `usedWords`; `project` and the projected JSON; `readWithSenses`; the sense map; `mixedOf`; the decoders |
| To be proved (5.3) | `wf_iff_no_failure`, `glossed_negative`, `preamble_unique`, `lines_read`, `project_valid`, `project_total`, `project_extends`, `senses_resolved_one_reading`, `senses_unit_sound`, `senses_candidate_sound`, `candidates_complete`, `mixed_exact`, `senseMap_ids` |
| Checked per request | `Dictionary.wf`; S2's `Lexicon.valid`, `Grammar.wf`, `terminatorFree`, `Grammar.typed` on the projection and on each candidate's projection; `typedDocument`; the equality of successor states |
| Tested only | the fixtures of section 8; the spans of the sense map; the flip models; the texts; the identities; everything in Python |

## 3. English: one reading each

### 3.1 What people write

| Form | Example | Reads |
|---|---|---|
| a default | `In this document, funny means amusing.` | always (a1) |
| a switch, parenthetical, the word last in its wording | `The riddle is funny (meaning strange).` | before a mark; before a space only with R3 (F1) |
| a switch, parenthetical, the word not last | `Alice tells (meaning says aloud) the riddle.` | in the clause position always; in an object relative (`Every joke that alice tells (meaning says aloud) is odd.`), where the cut leaves the word last, before a space only with R3 (c17) |
| a switch, comma, closing comma | `Every joke that is funny, in the sense of strange, is not funny.` | for a last word only with R3; for `tells`, in the clause position always and in an object relative only with R3. Kept only if Q4's rule keeps the comma forms (2.3, 11) |
| a switch, comma, no closing comma | `The riddle is funny, in the sense of strange.` | always; kept only if Q4's rule keeps the comma forms |
| a negative | `The riddle is not funny.`, `The riddle is not funny (meaning strange).`, `Alice does not tell the riddle.` | as the positive form does |

Nothing else is new. No number, symbol or id is written or shown. Zero-training English is the target and is
not measured here (L1).

### 3.2 The texts of the new outcomes

`{i}` is a sentence index shown as S2 shows one. Lean's texts are canonical and relayed verbatim.

| Code | Text |
|---|---|
| `InvalidDictionary` | `The vocabulary pack {pack} is not usable: {detail}.`, and for an own sense `The document's own vocabulary is not usable: {detail}.`, with `detail` a text of 4.2 |
| `UnknownWord` | `Line {i} gives a meaning for {word}, which is not a word of this document's vocabulary.` |
| `UnknownGloss` | `Line {i} says {word} means {gloss}. The senses of {word} here are: {gloss₁}; {gloss₂}. Use one of them.` |
| `RepeatedDefault` | `Line {i} gives {word} a second meaning. A document picks one.` |
| `MalformedPreamble` | `Line {i} begins "In this document," but is not of the form "In this document, <word> means <gloss>."` |
| `PreambleBudget` | `Line {i} could not be read within the work budget. Raise the budget or shorten the line.` |
| `PreambleLate` | `Sentence {i} gives a word a meaning. Such lines come first, before any other sentence.` |
| `Collision` | by the map below (R10) |
| `VocabularyLimit` (`limit "sorts"`) | `This document and its vocabulary packs together have more kinds than one document may have. Use fewer packs or fewer kinds.` |
| `VocabularyLimit` (`limit "predicates"`) | `This document and the words it uses from its vocabulary packs together have more meanings than one document may have. Use fewer words or split the document.` |
| `QuotedSense` | `Sentence {i} names a meaning of {word} in quotation marks. A meaning from a vocabulary pack is written with its word, not named in quotation marks.` |
| `TooManyCandidates` | `Sentence {i} uses {n} words with no chosen sense: {words}. Choose a sense for at least one of them first.` |
| `CandidatesDiverge` (referent) | `Sentence {i} uses {word} with no chosen sense, and its senses do not agree on what the sentence is about: read as {gloss₁} it mentions {name}, read as {gloss₂} it does not. Later sentences depend on that, so choose: add the line "In this document, {word} means {gloss₁}." (or {gloss₂}), or write {word} (meaning {gloss₁}).` |
| `CandidatesDiverge` (binder) | the same with `do not agree on whether the sentence speaks of every or some thing of a kind: read as {gloss₁} it does, read as {gloss₂} it does not` |
| `NoSenseFits` (a hint beside S2's `none`) **(B0)** | `Sentence {i} has no reading under any sense of {word}. The senses of {word} here are: {gloss₁}; {gloss₂}.` |
| `GlossedNatural` (a hint beside S2's `none`) | `Sentence {i} has no reading: a word with its meaning in brackets goes after its noun, not before it. Write "{rewrite}" instead.` The rewrite moves the glossed adjective behind its noun as `that is …` (s10: `Every joke that is funny (meaning strange) is odd.`), and the hint is given only when the rewritten sentence has one derivation under the same projection, so Lean never suggests a text it does not read. Obligation, not computed |
| `Unresolved` (an outcome of a unit), several candidates | plan 2.8 |
| `Unresolved`, one candidate (R11) | plan 2.8's text with `only strange fits a joke` replaced: `Sentence 2 uses odd, which has two senses here, and only strange gives a reading of this sentence. Add the line "In this document, odd means strange." to say so.` The text gives no reason why the other senses fail: in s16 it is the kind, in s20 the derivation, and the reader does not tell them apart |
| `Mixed`, `Unneeded` (warnings) | plan 2.8 |

**The `collision` map (R10).** Every `fault (collision kind name sense)` has exactly one text, chosen by the
first row that applies. `{pack}` is the pack that declares the sort or sense named; `{word}` a sense's word;
`{wording}` the shared text of the colliding pair that step 6 chose (the `text` of the first entry of
`clashes P.env P.lexicon` whose two names are `name` and `sense`), recomputed by the text function from the
projection that step 6 built. It always exists, because step 6 takes `name` and `sense` from one entry of
that list. The rows are disjoint: steps 1 and 4 leave `sense` empty and use the kinds `sort` and `name`;
steps 2 and 3 use the kind `letter`, which no clash has; a step-6 pair never leaves `sense` empty; and step 6
without a pair uses an S2 condition as its kind.

| Fault | From | Text |
|---|---|---|
| `collision "sort" name ""` | step 1 | `The kind {name} is both in the vocabulary pack {pack} and in this document, under different nouns. Use one noun.` (j14) |
| `collision "letter" letter sort` | steps 2, 3 | `The label letter {letter} is used both by the vocabulary pack {pack} (for {sort}) and by this document. Change one.` (j12, j12b) |
| `collision "name" name ""` | step 4 | `The name {name} is used both by the vocabulary pack {pack} and by this document. Rename one.` |
| `collision kind name sense`, `sense` a fresh pack sort and `name` a symbol of the document | step 6 | `The kind {sense} of the vocabulary pack {pack} has the noun {wording}, which this document already uses for {name}. Change one.` (j13: two kinds under one noun) |
| `collision kind name sense`, `sense` a sense symbol and `name` a symbol of the document | step 6 | `The wording {wording} is both in the vocabulary pack {pack} (for {word}) and declared by this document for {name}. Keep one.` (j6, j17) |
| `collision cond name ""`, `cond` one of S2's conditions `V1`, `V2`, `V3`, `V5` | step 6, no colliding pair | `The vocabulary packs cannot be used with this document as they are: the wordings they give for {word} do not pass the checks of this document's vocabulary.`, with `{word}` the word of `name` when it is a sense symbol, else `name`. No fixture reaches this row; it exists so that the map is total |
| any other `collision` (a pair with no side in the document) | step 6 | `The vocabulary packs give the wording {wording} to two of their meanings, so they cannot be used together as they are.` `readWithSenses` with a well-formed dictionary is not known to reach this row, and `project_total`'s premises exclude it; j15 reaches it by calling `project` on d26's dictionary, which W6 refuses. It exists so that the map is total |

A text with no body sentence shows S2's `EmptyDocument` text. S2's codes and texts for the body are unchanged.

### 3.3 The theorems, in plain words

| Statement | Plain English | It does not say |
|---|---|---|
| `wf_iff_no_failure` | A dictionary is well-formed exactly when its list of failed conditions is empty. | |
| `glossed_negative` | For a sense worded `{0} is word`, the automatic negative of the glossed wording is the glossed form of `{0} is not word`. | anything about verbs or declared negatives (computed on the fixtures, not stated) |
| `preamble_unique` | Every preamble line the reader accepts has exactly one derivation in the preamble grammar within the budget. | that the author meant that sense |
| `lines_read` | Rendering an assignment as lines and reading them back, at a budget under which each line parses, gives that assignment and its number of lines. | anything at a smaller budget: the reader then answers `preambleBudget` (a11) |
| `project_valid` | A projection that `project` returns passes S2's lexicon validity. | that `project` returns one |
| `project_total` (proposed, F4) | For a well-formed dictionary and assignment and a valid document lexicon, when the document has no predicate of its own, shares no name and no label letter with the dictionary, declares or selects no noun or spelling with the key of a form or noun of the dictionary, and the document's sorts with the pack sorts number at most 32 and the senses of the used words at most 256, `project` returns a projection. | anything with own predicates, shared keys or more sorts or senses than that: those are decided per request by the same check |
| `project_extends` | Using more words extends the projection in S2's sense, so by S2's `grammar_extension` the smaller grammar maps into the larger rule for rule. | anything about a changed default (q2) |
| `senses_resolved_one_reading` | If the reader accepts a document and every unit is resolved, the projection is the one `project` gives for the assignment the text's own preamble gives and the words of the body, and the body has one reading in S2's sense under it (each sentence one derivation with a meaning, in order from the initial state, the formulas typed). | anything about intent; anything when a unit is open |
| `senses_unit_sound` (proposed, B0) | Every unit of an accepted document has a formula or a candidate. A resolved unit has no candidate; the projection is the one `project` gives for the preamble's assignment and the words of the body; its grammar is well-formed; and the reader's outcome for the unit's sentence, from the state the earlier units leave, is the unit's formula, its mark and the state recorded after it. | |
| `senses_candidate_sound` | A unit with a candidate has no formula of its own, and each candidate is the reader's outcome for that sentence under the projection of the preamble's assignment extended by the candidate's choice, from the state the earlier units leave: that projection is valid, its grammar well-formed, the outcome is the candidate's formula and mark with the state recorded after the unit, the formula is typed there, and the candidate's lines are that extended assignment's lines. | that two candidates differ in meaning (the flip models are checked, not proved) |
| `candidates_complete` | In an accepted document the candidates of an open unit are exactly the choices of senses for its unresolved words under which the sentence reads and types, each with its formula and mark. | anything when a choice ends in a budget, ambiguity or rejection outcome: the document is then `stopped`, not accepted; anything about choices for a word left out of the unresolved words because every occurrence of it is switched (R7, L11) |
| `mixed_exact` | The mixed report lists a word with a list of senses exactly when that list is the senses of the word's occurrences in the resolved formulas, in order of first occurrence, and has two or more members. | |
| `senseMap_ids` | The sense map of a resolved sentence names every sense its formula uses and no other. | the spans, and how often: one written word can stand for several formula occurrences (s15); both are tested. It covers every sense because an accepted document never names a sense by its quoted name (`quotedSense`, R13) |

With `G.wf`, S1's `read_sound` (`Reading.lean:80`) turns the `readSentence` equations of `senses_unit_sound`
and `senses_candidate_sound` into `OneReading`: exactly one derivation, with that result. That every candidate
of a unit leaves the same state is part of `senses_candidate_sound`'s conclusion (the state is `u.after` for
each), not only a run-time check.

## 4. Diagnostics

### 4.1 Outcomes and codes

| Lean value | Status | Code |
|---|---|---|
| `ok` with every unit resolved | `one` | none |
| `ok` with an open unit | `open`, a status of `senses.read` only (the unit's candidates listed) | `Unresolved` per open unit |
| `fault (invalidDictionary f)` | `rejected` | `InvalidDictionary` |
| `fault (unknownWord ..)`, `(unknownGloss ..)`, `(malformedPreamble ..)`, `(preambleBudget ..)`, `(repeatedDefault ..)`, `(preambleLate ..)` | `rejected` (`budget` for `preambleBudget`) | `UnknownWord`, `UnknownGloss`, `MalformedPreamble`, `PreambleBudget`, `RepeatedDefault`, `PreambleLate` |
| `fault (collision kind ..)` | `rejected` | `Collision` |
| `fault (limit ..)` | `rejected` | `VocabularyLimit` |
| `fault (tooManyCandidates ..)`, `(candidatesDiverge ..)`, `(quotedSense ..)` | `rejected` | `TooManyCandidates`, `CandidatesDiverge`, `QuotedSense` |
| `lexical r`, `invalidGrammar why`, `stopped i o`, `illTyped` | S2's (S2 4.1, base 4.2) | S2's |

No existing code or text changes (D10). The response per unit adds the state after it (`referents`,
`binderSeen`), as S2's response does per reading (S2 4.3), and per candidate its choice, formula, mark and
resolving lines; the rest of the response is plan B6.

**As built (fix round, reviews Astra B1 and Fable B2).** `ve_senses_route` writes each unit with its
`sentence` (its index in the whole text), `referents` and `binder_seen`; a fault other than
`invalidDictionary` with `details`, its arguments under the names of `SenseFault`'s fields (`line`,
`sentence`, `word`, `gloss`, `words`, `kind`, `name`, `sense`, `what`, and `why`: `{"referent": x}` or
`"binder"`); `invalidDictionary` with `failure`, its condition, word and detail; and S2's outcomes with exactly
the fields of S2's authoring answer (S2 4.3): `text`, `sentence`, the two `witnesses` of an ambiguity under
the grammar that stopped, and an invalid grammar's `fault` and `failure`. `tests/test_senses_route.py`
compares the S2 fields with `ve_english_route`'s and checks every fault code. The 3.2 texts of the sense
faults are still plan B6.

### 4.2 The texts of `Dictionary.failures`

Each is the `detail` of a failure, written to complete `… is not usable: {detail}.`

| Condition | Detail |
|---|---|
| W1 | `{word} is not a word of two to fifty lower-case letters`; `{word} is a reserved word`; `the senses of {word} are not numbered from 1, each number once`; `the word {word} is in two packs: {pack₁} and {pack₂}`; `the document gives its own sense to {word}, a word of the pack {pack}` |
| W2 | `the gloss {gloss} of {word} is not one to three words of three to fifty lower-case letters, none reserved`; `the gloss of {word} is the word itself`; `the gloss {gloss} of {word} is itself a word of the vocabulary`; `the word {word} has two senses with the gloss {gloss}` |
| W3 | `the wording {wording} of {word}` followed by one of: `does not have each of its places once, with a word`; `does not begin with its first place`; `does not contain {word} exactly once`; `contains a bracket or a full stop`; `contains means or meaning`; `contains in the sense of`; `gives a form longer than two hundred and fifty-six characters` |
| W4 | `{word} does not apply to one or two kinds`; `{word} applies to {kind}, which is not a kind of the pack {pack}`; `{word} applies to {kind}, which is not a kind of the document or of its packs`; `a sense of {word} has no description`; `the kind name {sort} is not lower-case letters, digits and underscores beginning with a letter, at most sixty-four in all`; `the kind name {sort} is reserved`; `the kind {sort} has no description`; `the kind {sort} has no usable noun`; `the kind {sort} has no usable plural`; `the label letter {letter} of the kind {sort} is not one capital letter`; `the kind {sort} is declared differently in two packs`; `the label letter {letter} is given to two kinds: {sort₁} and {sort₂}`; `the noun {noun} is given to two kinds: {sort₁} and {sort₂}`. A name that matches `x` and digits, or begins with `sense__`, is `reserved` |
| W5 | `{word} declares a negative wording although its negative is automatic`; `the negative wording of {word} equals its wording`; `the negative wording {negative} of {word}` followed by a W3 ending |
| W6 | `the wording {form} belongs to both {word₁} and {word₂}` (different words); `the wording {form} belongs to two senses of {word}` (one word); `the wording {form} of {word} is also the noun of the kind {sort}` |
| W7 | `{text} contains in this document` |

The numbering text of W1 is read by a pack's author, who writes the indices; a document's author never sees
it.

## 5. Lean: definitions and the exact statements

### 5.1 Modules and conventions

Plan 4.1 stands: new files only, in `lean/VE/Senses/` (`Dictionary`, `Assignment`, `Preamble`, `Project`,
`Read`, `Examples`, `Decode`), namespace `VE.Senses`, layer 3; the conventions of base 5.1 and base 6 (no
prime, no `?`, no totality escape, the audit's forbidden words absent from comments, one `#print axioms` line
per theorem, the frozen inventory, `tools/lean_statements.py` after every Lean edit). The prototype's tree walk
for the sense map used a totality escape; the built one recurses on the tree as `Tree.yield` does
(`Derives.lean:54`).

### 5.2 The signature

Every line below elaborated in the stub (draft 1), except the last five, which are named here for B2, B5 and
B6, and the lines that draft 2 adds or changes, each marked `-- draft 2`, which have not been elaborated
(G-S0). Bodies are as section 2 defines them; the short ones are shown.

```lean
namespace VE.Senses
open Lean VE.Grammar VE.EnglishGrammar

structure Sense where
  word : String
  index : Nat                    -- 1-based within the word; never displayed
  gloss : String                 -- one to three words
  description : String           -- displayed, never parsed
  kinds : List String            -- one or two argument sorts, in order
  wording : String
  negative : Option String := none   -- only where negativeTemplate gives none (W5)
  deriving DecidableEq, Repr

structure PackSort where
  name : String
  noun : String
  plural : String
  description : String
  letter : String                -- one capital ASCII letter (W4)
  deriving DecidableEq, Repr

structure Pack where
  name : String
  sorts : List PackSort
  senses : List Sense
  deriving Repr

structure Dictionary where
  packs : List Pack
  own : List Sense
  deriving Repr

def reservedWords : List String
def schemaReserved : List String               -- Python's `RESERVED`, `ve/environment.py:28`; draft 2
def maxFormChars : Nat := 256                  -- W3, W4; draft 2
def Sense.symbol (s : Sense) : String := "sense__" ++ s.word ++ "_" ++ toString s.index
def Sense.arity (s : Sense) : Nat := s.kinds.length
def Sense.isSimpleAdjective (s : Sense) : Bool := s.wording == "{0} is " ++ s.word && s.kinds.length == 1
def Sense.headIn (s : Sense) (t : String) : Option String
def Sense.decorate (s : Sense) (t : String) (deco : String → String) : String
def Sense.glossed (s : Sense) (t : String) : String :=
  s.decorate t fun h => h ++ " (meaning " ++ s.gloss ++ ")"
def Sense.commaForms (s : Sense) (t : String) : List String :=
  [s.decorate t fun h => h ++ ", in the sense of " ++ s.gloss ++ ",",
   s.decorate t fun h => h ++ ", in the sense of " ++ s.gloss]
def Sense.selectedWording (s : Sense) (isDefault : Bool) : String :=
  if isDefault then s.wording else s.glossed s.wording
def Sense.automaticNegative (s : Sense) (isDefault : Bool) : Option String :=
  negativeTemplate (s.selectedWording isDefault) s.arity
def Sense.fixedNegative (s : Sense) (isDefault : Bool) : Option String :=
  s.negative.map fun n => if isDefault then n else s.glossed n
def Sense.selectedNegative (s : Sense) (isDefault : Bool) : Option String
def Sense.bareNegative (s : Sense) : Option String := s.selectedNegative true
def Sense.aliases (s : Sense) (isDefault : Bool) : List (String × Bool)
def Sense.headwordTokens (s : Sense) : List String
def Sense.bareForms (s : Sense) : List String
def Sense.decoratedForms (s : Sense) : List String

abbrev DictFailure := String × String × String          -- condition; word, pack or kind; detail
def Dictionary.senses (D : Dictionary) : List Sense := D.packs.flatMap (·.senses) ++ D.own
def Dictionary.sorts (D : Dictionary) : List PackSort := (D.packs.flatMap (·.sorts)).eraseDups
def Dictionary.sensesOf (D : Dictionary) (w : String) : List Sense := D.senses.filter (·.word == w)
def Dictionary.words (D : Dictionary) : List String := (D.senses.map (·.word)).eraseDups
def Dictionary.failures (D : Dictionary) (docSorts : List String) : List DictFailure   -- W1 to W7
def Dictionary.wf (D : Dictionary) (docSorts : List String) : Bool := (D.failures docSorts).isEmpty

structure Assignment where
  defaults : List (String × Nat)     -- word, index; in line order
  deriving DecidableEq, Repr
def Assignment.wf (D : Dictionary) (A : Assignment) : Bool
def Assignment.extend (A : Assignment) (c : List (String × Nat)) : Assignment := ⟨A.defaults ++ c⟩
def defaultOf (D : Dictionary) (A : Assignment) (w : String) : Option Sense
def Assignment.lines (D : Dictionary) (A : Assignment) : String
def unneeded (D : Dictionary) (A : Assignment) : List String

def preambleGrammar (D : Dictionary) : Grammar Terminal
def preambleShaped : List Tok → Bool

inductive Divergence where
  | referent (name : String)
  | binder
  deriving DecidableEq, Repr

inductive SenseFault where
  | invalidDictionary (f : DictFailure)
  | unknownWord (line : Nat) (word : String)
  | unknownGloss (line : Nat) (word gloss : String)
  | malformedPreamble (line : Nat)
  | preambleBudget (line : Nat)
  | repeatedDefault (line : Nat) (word : String)
  | preambleLate (sentence : Nat)
  | collision (kind name : String) (sense : String)   -- kind: sort, letter, name, a kind of a V4 pair, or an S2 condition (2.5)
  | limit (what : String)                             -- "sorts" or "predicates"; draft 2
  | tooManyCandidates (sentence : Nat) (words : List String)
  | candidatesDiverge (sentence : Nat) (words : List String) (why : Divergence)
  | quotedSense (sentence : Nat) (word : String)      -- draft 2
  deriving DecidableEq, Repr

def readPreamble (D : Dictionary) (b : Nat) (sents : List (List Tok)) : Except SenseFault (Assignment × Nat)

/-- The tokens of a sentence with their indices, but the mark and the gloss after a glossed head (2.6). -/
def unglossed (D : Dictionary) (w : List Tok) : List (Nat × Tok)                  -- fix round
def usedWords (D : Dictionary) (sents : List (List Tok)) : List String

structure Projection where
  env : Env
  lexicon : Lexicon
  envJson : Json
  map : List (String × Sense × Bool)                  -- predicate id, sense, is default
  deriving Repr
def Projection.wordOf (P : Projection) (id : String) : Option String :=
  (P.map.find? (·.1 == id)).map (·.2.1.word)
def maxSorts : Nat := 32                       -- `ve/limits.py:6`; draft 2
def maxPredicates : Nat := 256                 -- `ve/limits.py:7`; draft 2
/-- The colliding pairs of a lexicon in S2's V4 order: a selection's kind and name, the kind and name of another
symbol that declares or selects a text with its `wordingKey`, and the selection's text (2.5, step 6). -/
def clashes (E : Env) (L : Lexicon) : List (String × String × String × String × String)   -- draft 2
def project (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String) :
    Except SenseFault Projection

structure Candidate where
  choice : List (String × Nat)
  lines : String                     -- `Assignment.lines D (A.extend choice)`
  formula : EFormula
  mark : Bool
  deriving DecidableEq, Repr

structure SenseUnit where
  formula : Option (EFormula × Bool)  -- some exactly when resolved
  candidates : List Candidate         -- not empty exactly when open
  unresolved : List String
  after : DState                      -- the state after the unit (B0)
  deriving DecidableEq, Repr

structure SenseOccurrence where
  sentence : Nat                      -- index in the whole text
  start : Nat                         -- token index, inclusive
  stop : Nat                          -- token index, exclusive
  symbol : String
  isDefault : Bool
  candidate : Option Nat              -- none for a resolved unit
  deriving DecidableEq, Repr

inductive SensesOutcome where
  | ok (units : List SenseUnit) (senses : List SenseOccurrence) (mixed : List (String × List String))
       (unused : List String) (P : Projection)
  | fault (f : SenseFault)
  | lexical (r : Reject)
  | invalidGrammar (why : GrammarFault)
  | stopped (index : Nat) (o : Outcome Tok Reject EFormula)
      (tags : Array String)           -- fix round: the rule tags of the grammar that stopped, for witnesses
  | illTyped

def candidateCap : Nat := 8
/-- The number of choices counted up to `cap + 1`; `choiceCount_eq` relates it to `choicesOf`. -/
def choiceCount (D : Dictionary) (cap : Nat) : List String → Nat                  -- fix round
  | [] => 1
  | w :: ws => min (cap + 1) ((D.sensesOf w).length * choiceCount D cap ws)
def choicesOf (D : Dictionary) : List String → List (List (String × Nat))
  | [] => [[]]
  | w :: ws => (D.sensesOf w).flatMap fun s => (choicesOf D ws).map fun c => (w, s.index) :: c
/-- Whether the token at `j` is followed by `(` and `meaning`, or by a comma and `in the sense of`. -/
def switchedAt (w : List Tok) (j : Nat) : Bool                                    -- draft 2
/-- Whether some token of `w` outside a gloss folds to a headword token of `x` and is not switched. -/
def unswitchedIn (D : Dictionary) (x : String) (w : List Tok) : Bool              -- draft 2
/-- The used words of one sentence that have no default under `A` and an unswitched occurrence. -/
def unresolvedIn (D : Dictionary) (A : Assignment) (w : List Tok) : List String :=  -- draft 2
  (usedWords D [w]).filter fun x => (defaultOf D A x).isNone && unswitchedIn D x w
def stateBefore (units : List SenseUnit) : Nat → DState
  | 0 => DState.init
  | i + 1 =>
    match units[i]? with
    | some u => u.after
    | none => DState.init
def senseOccurrences (P : Projection) (A : EFormula) : List String
def mixedOf (P : Projection) (units : List SenseUnit) : List (String × List String)
def readWithSenses (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String) : SensesOutcome

/-- The `wordingKey`s of what the document declares or selects: nouns and spellings. -/
def docKeys (E : Env) (L : Lexicon) : List String :=
  ((E.sorts.filterMap (·.noun)) ++ (E.constants.filterMap (·.display)) ++ L.nouns.map (·.2) ++
    L.spellings.map (·.2)).map wordingKey
/-- The `wordingKey`s of every form of every sense and of every pack noun. -/
def dictKeys (D : Dictionary) : List String :=
  ((D.senses.flatMap fun s => s.bareForms ++ s.decoratedForms) ++ D.sorts.map (·.noun)).map wordingKey

def flipModel (P : Projection) (c d : Candidate) : Option Json     -- 2.6; not in the stub
def dictionaryId (D : Dictionary) : String                         -- plan 2.7; not in the stub
def sensesVersion : String                                         -- plan 2.7; not in the stub
/-- The `NoSenseFits` text for sentence `i` and its unresolved words (3.2). -/
def noSenseFitsText (D : Dictionary) (i : Nat) (words : List String) : String   -- draft 2; not in the stub
/-- The `GlossedNatural` rewrite of sentence `w`: `some` only when the rewrite has one derivation
under `P` within `b` (3.2). -/
def glossedNaturalRewrite (P : Projection) (b : Nat) (w : List Tok) : Option String  -- draft 2; not in the stub
```

`Env`, `Lexicon`, `Tok`, `Terminal`, `EFormula`, `DState`, `Reject`, `GrammarFault`, `Outcome`, `Grammar`,
`verdict`, `readSentence`, `DocOneReading`, `grammar`, `meaning`, `acts`, `typedDocument`, `Extends`,
`negativeTemplate`, `wordingKey` and `lex` are S1's and S2's, as merged.

### 5.3 The exact statements

Each elaborated as a definition of type `Prop` with exactly this body in draft 1; the three that draft 2
changes are to be re-elaborated (G-S0).

```lean
theorem wf_iff_no_failure : ∀ (D : Dictionary) (ss : List String),
  D.wf ss = true ↔ D.failures ss = []

theorem glossed_negative : ∀ (s : Sense), s.isSimpleAdjective = true →
  negativeTemplate (s.glossed s.wording) 1 = some (s.glossed ("{0} is not " ++ s.word))

theorem preamble_unique : ∀ (D : Dictionary) (ss : List String) (b : Nat) (sents : List (List Tok))
    (A : Assignment) (k : Nat),
  D.wf ss = true → readPreamble D b sents = .ok (A, k) →
  ∀ i < k, ∀ w, sents[i]? = some w →
    ∃ t, verdict (preambleGrammar D) b w.toArray = some (.one t)

theorem lines_read : ∀ (D : Dictionary) (ss : List String) (b : Nat) (A : Assignment)
    (sents : Array (Array Tok)),
  D.wf ss = true → A.wf D = true → lex (A.lines D) = .ok sents →
  (∀ w ∈ sents, verdict (preambleGrammar D) b w ≠ none) →
  readPreamble D b (sents.toList.map (·.toList)) = .ok (A, A.defaults.length)

theorem project_valid : ∀ (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String)
    (P : Projection),
  project D A E L used = .ok P → P.lexicon.valid P.env {} = true

theorem project_total : ∀ (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String),
  D.wf (E.sorts.map (·.name)) = true → A.wf D = true → L.valid E {} = true →
  E.predicates = [] → E.forms.negatives = [] → E.forms.aliases = [] →
  (∀ n ∈ E.sorts.map (·.name) ++ E.constants.map (·.name),
    n ∉ D.sorts.map (·.name) ∧ n ∉ D.senses.map (·.symbol)) →
  (∀ k ∈ docKeys E L, k ∉ dictKeys D) →
  (∀ x ∈ L.letters, ∀ t ∈ D.sorts, x.2 ≠ t.letter) →
  E.sorts.length + D.sorts.length ≤ maxSorts →
  (D.senses.filter (·.word ∈ used)).length ≤ maxPredicates →
  ∃ P, project D A E L used = .ok P

theorem project_extends : ∀ (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon)
    (used used2 : List String) (P P2 : Projection),
  E.profiles = ["relational-fol@0"] → (∀ w ∈ used, w ∈ used2) →
  project D A E L used = .ok P → project D A E L used2 = .ok P2 →
  P.lexicon.valid P.env {} = true → P2.lexicon.valid P2.env {} = true →
  Extends P.env {} P.lexicon P2.env {} P2.lexicon

theorem senses_resolved_one_reading : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (units : List SenseUnit) (sm : List SenseOccurrence) (mx : List (String × List String)) (un : List String)
    (P : Projection),
  readWithSenses D E L b s = .ok units sm mx un P →
  (∀ u ∈ units, u.candidates = []) →
  ∃ sents A k rs st2, lex s = .ok sents ∧
    readPreamble D b (sents.toList.map (·.toList)) = .ok (A, k) ∧
    project D A E L (usedWords D ((sents.toList.drop k).map (·.toList))) = .ok P ∧
    units.map (·.formula) = rs.map some ∧
    P.lexicon.valid P.env {} = true ∧
    DocOneReading (grammar P.env P.lexicon) (meaning (grammar P.env P.lexicon) (acts P.env P.lexicon))
      DState.init ((sents.toList.drop k).map (·.toList)) rs st2 ∧
    typedDocument P.env (rs.map (·.1)) = true

theorem senses_unit_sound : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (units : List SenseUnit) (sm : List SenseOccurrence) (mx : List (String × List String)) (un : List String)
    (P : Projection) (i : Nat) (u : SenseUnit),
  readWithSenses D E L b s = .ok units sm mx un P →
  units[i]? = some u →
  (u.formula.isSome = true ∨ u.candidates ≠ []) ∧
  ∀ (F : EFormula) (m : Bool), u.formula = some (F, m) →
    u.candidates = [] ∧
    ∃ sents A k w, lex s = .ok sents ∧
      readPreamble D b (sents.toList.map (·.toList)) = .ok (A, k) ∧
      project D A E L (usedWords D ((sents.toList.drop k).map (·.toList))) = .ok P ∧
      (sents.toList.drop k)[i]? = some w ∧
      (grammar P.env P.lexicon).wf = true ∧
      readSentence (grammar P.env P.lexicon) (meaning (grammar P.env P.lexicon) (acts P.env P.lexicon))
        (stateBefore units i) b w = (.ok F m, u.after)

theorem senses_candidate_sound : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (units : List SenseUnit) (sm : List SenseOccurrence) (mx : List (String × List String)) (un : List String)
    (P : Projection) (i : Nat) (u : SenseUnit) (c : Candidate),
  readWithSenses D E L b s = .ok units sm mx un P →
  units[i]? = some u → c ∈ u.candidates →
  u.formula = none ∧
  ∃ sents A k P2 w,
    lex s = .ok sents ∧ readPreamble D b (sents.toList.map (·.toList)) = .ok (A, k) ∧
    project D (A.extend c.choice) E L (usedWords D ((sents.toList.drop k).map (·.toList))) = .ok P2 ∧
    P2.lexicon.valid P2.env {} = true ∧ (grammar P2.env P2.lexicon).wf = true ∧
    c.lines = Assignment.lines D (A.extend c.choice) ∧
    (sents.toList.drop k)[i]? = some w ∧
    readSentence (grammar P2.env P2.lexicon) (meaning (grammar P2.env P2.lexicon) (acts P2.env P2.lexicon))
      (stateBefore units i) b w = (.ok c.formula c.mark, u.after) ∧
    typedDocument P2.env [c.formula] = true

theorem candidates_complete : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (units : List SenseUnit) (sm : List SenseOccurrence) (mx : List (String × List String)) (un : List String)
    (P : Projection) (i : Nat) (u : SenseUnit) (choice : List (String × Nat)) (F : EFormula) (m : Bool),
  readWithSenses D E L b s = .ok units sm mx un P → units[i]? = some u → u.candidates ≠ [] →
  ((choice ∈ choicesOf D u.unresolved ∧
    ∃ sents A k P2 w,
      lex s = .ok sents ∧ readPreamble D b (sents.toList.map (·.toList)) = .ok (A, k) ∧
      project D (A.extend choice) E L (usedWords D ((sents.toList.drop k).map (·.toList))) = .ok P2 ∧
      (sents.toList.drop k)[i]? = some w ∧
      (readSentence (grammar P2.env P2.lexicon) (meaning (grammar P2.env P2.lexicon) (acts P2.env P2.lexicon))
        (stateBefore units i) b w).1 = .ok F m ∧
      typedDocument P2.env [F] = true)
   ↔ ∃ c ∈ u.candidates, c.choice = choice ∧ c.formula = F ∧ c.mark = m)

theorem mixed_exact : ∀ (P : Projection) (units : List SenseUnit) (w : String) (ids : List String),
  (w, ids) ∈ mixedOf P units ↔
    ids = ((units.filterMap (·.formula)).flatMap
             (fun (A, _) => (senseOccurrences P A).filter (P.wordOf · == some w))).eraseDups ∧
    2 ≤ ids.length

theorem senseMap_ids : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (units : List SenseUnit) (sm : List SenseOccurrence) (mx : List (String × List String)) (un : List String)
    (P : Projection) (i : Nat) (u : SenseUnit) (F : EFormula) (m : Bool),
  readWithSenses D E L b s = .ok units sm mx un P → units[i]? = some u → u.formula = some (F, m) →
  ∃ sents A k, lex s = .ok sents ∧ readPreamble D b (sents.toList.map (·.toList)) = .ok (A, k) ∧
    ∀ id, id ∈ (sm.filter (fun o => o.sentence == k + i && o.candidate.isNone)).map (·.symbol)
          ↔ id ∈ senseOccurrences P F
```

Draft 2 changes three statements, none of them re-elaborated yet (G-S0): `project_total` gains the two
count premises (R4); `senses_resolved_one_reading` gains the conjunct that `P` is `project` of the
preamble's assignment and the body's used words (R5); `senses_unit_sound` takes the unit without its formula,
concludes that it has a formula or a candidate (R6), and keeps draft 1's conclusion under `∀ F m, u.formula =
some (F, m) →`, with the same `project` conjunct (R5). The other ten statements are as draft 1 elaborated them.

Four statements differ from the plan's and the review should read them first.

- `project_valid` has no premise (F4). The plan's statement, with its premises, follows from it.
- `project_total` is new (F4). It is the plan's "valid by construction" claim, with the premises the
  computation showed to be needed: disjoint names, disjoint letters, no key shared between what the
  document declares or selects and what the dictionary can select, and Python's two counts (R4).
- `senses_candidate_sound` uses `stateBefore units i` and `u.after` in place of the plan's `stateBefore`
  relation, concludes the full pair of `readSentence` (so the common successor state is stated, not only
  checked), and adds `u.formula = none` and the grammar's well-formedness, which `read_sound` needs.
  `candidates_complete` uses the same state and writes the plan's `preambleOf`, `usedOf` and `sentenceAt` out.
- `senses_unit_sound` is new (B0): without it no statement covers a resolved unit of a document that has an
  open unit elsewhere; since draft 2 it also states that no unit of an accepted document is empty.
  `senseMap_ids` takes the unit by `u.formula = some (F, m)`, since a unit has four fields.

### 5.4 Proof notes and fallbacks

| Statement | Argument | Fallback |
|---|---|---|
| `wf_iff_no_failure` | `List.isEmpty_iff`; proved in the stub | none needed |
| `glossed_negative` | the wording is `{0} is ` and the word; its last part equal to the word lies after the prefix (or no part is the word, when the word has a space, and both sides are undecorated); `negativeTemplate` on a text that starts with `{0} is ` replaces that prefix; checked by `#eval` on seven senses, five of them malformed (8.1) | none needed: a string lemma |
| `preamble_unique` | `readLine` accepts only `some (.one _)`. That `many` never arises under W2 is the reason the fallback row is unreachable, not part of the statement | none needed |
| `lines_read` | each line is the yield of its sense's rule and is shaped; the budget premise makes the verdict `some`; two rules that both derive it have the same word and the same gloss, so by W1 and W2 they are one sense; `acc` then rebuilds the assignment in order | state it for assignments of one line first |
| `project_valid` | `project` returns `ok` only when `Lexicon.failures` is empty; `valid_iff_no_failure` (S2) | none needed |
| `project_total` | steps 1 to 4 by the name and letter premises; step 5 by the count premises; V1 by construction; V2 because every selection is the declared form the projection wrote; V3 from W3 and W4 and a lemma that a decorated form of a `shapeOk` wording is `shapeOk`; V4 from W6 (which compares every pair of forms two senses can select together), W4 and the key premise; V5 because automatic negatives are `negativeTemplate` of the selected wording and declared ones are in `forms.negatives` | deferred with the DRI's signature; the per-request check of `project` stays the guarantee |
| `project_extends` | `envSub`: sorts and constants equal, predicates of the smaller list kept with `args`; `lexiconSub`: the same assignment gives the same entries; validity by the two premises | stated only; q1 and q2 test it |
| `senses_resolved_one_reading` | the reader's loop over `readSentence` is `readDocument`'s (`Reading.lean:66`) when no unit is open; then S1's `doc_sound` with the well-formedness the checks of step 7 give; the typed check of step 9 on a non-empty list | none needed |
| `senses_unit_sound`, `senses_candidate_sound`, `candidates_complete` | unfolding the loop: the state before unit `i` is the `after` of unit `i - 1`; an open unit records the first candidate's successor, and the equality check makes it every candidate's; admission is exactly the right-hand side; a unit is built only by the resolved branch (formula) or the open branch with at least one candidate, since no candidate is `stopped` (R6); `P` is step 6's projection (R5) | none needed |
| `mixed_exact` | `mixedOf` is a `filterMap` over the words of `P.map` without repeats; for a word that `P.map` does not name the list is empty | none needed |
| `senseMap_ids` | membership both ways from the tree walk: every lexical rule of a sense predicate in the derivation yields an atom of that predicate in the formula, and every such atom comes from such a rule (S2's actions build atoms only from `pred`, `relSubject`, `relObject`, `adjective`, `natSubject`, `copulaRel` and `owner`, and `owner` names `owns`; the one other row that names a predicate, `relation.`, never occurs with a sense predicate in an accepted derivation, by `quotedSense`, R13) | stated only; s1, s9 and s15 test it, s23 tests the exclusion |

### 5.5 By construction, and by test

By construction: the preamble grammar is well-formed and terminator-free; a sense's symbol is unique under W1;
a decorated form differs from a bare one under W3. Checked, not by construction: that two senses of one word
share no decorated form (W6, d26). By test only: the spans of the sense map, the order of
candidates, the detail texts, the projected JSON's acceptance by Python's `Environment` (j8, second half), the
flip models as models, the identities.

## 6. Requests to S2

### 6.1 R1 and R2

R2 is withdrawn (plan Q7). **R1 is not needed**: the reader calls `readSentence` per sentence itself, which the
open units require in any case, and calls S2's exported checks; S2's `read` stays as merged and no statement
here mentions it.

### 6.2 R3: the mark that ends a wording (for the DRI and the S2 owner)

**Request.** In `clauseRows` (`Rules.lean:91`), test **each row it builds, after its cut** (the clause, the
subject relative without the leading `{0}`, the object relative lexed without ` {1}`, `Rules.lean:96–98`):
when the row's right-hand side ends with an `exact` punctuation terminal, which is then always glued after,
give that row a second row with the same left-hand side and action whose last terminal is the same mark not
glued after. So the object relative of `{0} tells (meaning says aloud) {1}`, whose wording ends in a hole,
gets a twin, because its row ends in `)` (c17). Nothing else changes: no rule is added for a row that ends in
a word or a hole, and no row outside `clauseRows` (nouns, labels, spellings, the adjective families, `owner`,
`relation.`) is touched.

**Why.** F1. The glue flag after a wording's last mark describes the terminator the lexer appended, not the
wording. Python's pattern for a wording ends at its last character and constrains nothing after it
(`_literal_pattern`, `ve/english.py:882`; read, not run), so today's Lean rule is narrower than the O1 ruling
intends ("Lean accepts the spacing that Python accepts and no other") for any wording that ends in a mark.
Whether any corpus lexicon has such a wording is for S2 to measure; the fixture lexicons of
`ReadExamples.lean` have none.

**Evidence.** Draft 1's stub simulated R3 by appending twin rules to `grammar P.env P.lexicon` with the
original's action index, for **every** lexical row that ends in a glued mark (`openRows`), which is wider than
the request: 36 rules on the 194 of j1's projection with `odd` (230), still well-formed, terminator-free and
typed. Under it every c fixture of draft 1 had the plan's verdict and the joke read to the plan's four
formulas (8.5, 8.7). It is not true that no fixture gains a second derivation: c16 has two with R3 (R9). The
simulation is to be narrowed to the rows of `clauseRows` and the whole R3 column recomputed (12); the counts
above are draft 1's.

**Cost.** `Rules.lean` is locked, so `actions_version` moves once for every `english.read` response; the proof
of `grammar_extension` (`lexRows_sub`) gains a case; G2 is re-run. No S2 statement changes.

**If refused.** (A) The senses reader adds the twin rules to its own grammar: S2 is untouched and D10 has no
exception, but the statements of 5.3 then speak of that grammar instead of `grammar P.env P.lexicon`, a stored
projection read by S2 alone loses the mid-sentence glosses, and `checkRendering` and `grammar_extension` no
longer apply as they are. (B) The forms are restricted to the *as merged* column of 2.3: a glossed adjective
is written before a mark, or with the comma form without its closing comma; the joke is rewritten; the
zero-training target is missed for the main form. **Recommendation: R3.** Until it is decided, the *as merged*
column is what the build must reproduce, and the *with R3* column is the acceptance value once R3 lands.
Either way Q4's rule (11) then decides the comma forms on the column that ships: with R3, c16 drops them.

## 7. Gates

Plan section 5 (batches) and 7 (gates) stand, with these facts. G-S0: draft 1's stub elaborated every
statement of 5.3 against the merged S2 build, and every counterexample fixture the plan review asked for is
present with a computed value (d1, d17, d18, d19, a11, a12, j11, j12, n3, n7, s15, s16, s17, s18). The statement
review converged on FIX (0.1), applied in this draft. G-S0 passes after **one bounded re-review by both
reviewers** of: the diff from draft 1; the three changed statements and the draft-2 lines of 5.2,
re-elaborated against the merged S2 build; and the recomputed rows (d2, d26, j6 and j13 under step 6's pair
rule, j13's text, j15, j16, j17, c16, c17, s22, s23, the whole R3 column under the narrowed simulation, and
every *hand-derived* row of section 8). No
second full review. **B1 to B4 start when G-S0 passes. B5 additionally waits for the DRI's decision on R3
and for Q4, which its rule then decides on the column that ships (11).** G-S0b: met for draft 1's statements;
it is re-run when S2 changes, R3 in particular. The W1, soft and P0 contracts are untouched; R3 keeps its
approval, versioning and regression gate (6.2).

## 8. Acceptance fixtures

*Computed* rows were evaluated in draft 1's stub (section 12); *obligation* rows were not. Rows that draft 2
adds or changes are marked: ***hand-derived*** (derived by reading, not run) or ***computed by a reviewer***
(evaluated by Astra through Lean's standard input against draft 1's stub during the review, with draft 1's
wider R3 simulation). Both kinds are recomputed for G-S0 (7). `Fd` is `F` plus `near` 1 (gloss `beside`,
`{0} is near bob` over person) and `near` 2 (gloss `beside bob`, `{0} is near` over person): the
counterexample of R1. `F` is the pack of 2.2
with the sorts `principal` (`R`) and `resource` (`Q`). `F2` is `F` plus `tells` 2 (gloss `reveals`,
`{0} tells {1}` over person and joke). `Fn` is `F` plus `near` 1 (gloss `beside bob`, `{0} is near bob` over
person) and `near` 2 (gloss `beside`, `{0} is near {1}` over person and person). `F3` is `F` plus `warm`, `cool`
and `mild`, three senses each. `EJ` has the sorts `joke`, `person`, no predicate, the constants `alice`
(person) and `riddle` (joke, display `the riddle`); `LJ` is its lexicon (nouns `joke`, `person`; letters `J`,
`P`; spellings `alice`, `the riddle`), valid. `EJn` adds the person `bob`; `EJs` adds the sort `service` and
the constant `legacy`; `ES` has `service` and `legacy`, `beta`, `gamma`; `EP` has `principal`, `resource`,
`alice`, `api`; each with its lexicon. `J` is the joke:

```text
In this document, funny means amusing.
Every joke that is funny (meaning strange) is not funny.
Alice tells the riddle.
The riddle is funny (meaning strange).
Therefore the riddle is not funny.
```

### 8.1 Dictionary (d), computed

| Id | Case | `failures` |
|---|---|---|
| d1 | `F` | `[]`, though both `funny` senses and both `odd` senses share a bare wording |
| d2 | `funny` 2 with gloss `amusing` | ***hand-derived:*** `[("W2", "funny", "the word funny has two senses with the gloss amusing"), ("W6", "funny", "the wording {0} is funny (meaning amusing) belongs to two senses of funny")]`. Draft 1 computed the W2 failure alone; W6 now compares decorated forms within a word (R1) |
| d3 | `odd` 1 with gloss `odd` | `[("W2", "odd", "the gloss of odd is the word itself")]` |
| d4 | `funny` 2 with gloss `deployed` | `[("W2", "funny", "the gloss deployed of funny is itself a word of the vocabulary")]` |
| d5 | `funny` 1 worded `{0} is amusing` | `[("W3", "funny", "the wording {0} is amusing of funny does not contain funny exactly once")]` |
| d6 | `tells` worded `{1} tells {0}` | `[("W3", "tells", "the wording {1} tells {0} of tells does not begin with its first place")]` |
| d7 | `funny` 1 over `thing` | `[("W4", "funny", "funny applies to thing, which is not a kind of the pack fixtures@1")]` |
| d8 | `funny` 1 with negative `{0} is not funny` | `[("W5", "funny", "funny declares a negative wording although its negative is automatic")]` |
| d9 | `access` without its negative | `[]` (then n6) |
| d10 | `access` with negative `{0} cannot access {1}` | `[]` |
| d11 | `F` plus `weird` worded `{0} is funny weird`, and `funny` 1 worded the same | `[("W6", "funny", "the wording {0} is funny weird belongs to both funny and weird")]`. With the plan's word `strange` the list is two W2 failures and then the W6 one (F6) |
| d12 | a second pack with `funny` | `[("W1", "funny", "the word funny is in two packs: fixtures@1 and other@1")]` |
| d13 | an own sense for `funny` | `[("W1", "funny", "the document gives its own sense to funny, a word of the pack fixtures@1")]` |
| d14 | `funny` 1 worded `{0} is funny (meaning amusing)` | `[("W3", "funny", "the wording {0} is funny (meaning amusing) of funny contains a bracket or a full stop")]` |
| d15 | a sense of the word `every` | `[("W1", "every", "every is a reserved word")]` |
| d16 | `funny` with indices 1 and 3 | `[("W1", "funny", "the senses of funny are not numbered from 1, each number once")]` |
| d17 | d11 with `funny` 2 in place of `funny` 1 | the same W6 failure: equal bare wordings pass within a word (d1) and fail across words whichever sense carries them |
| d18 | `Fn` | `[]`: neither the arity difference nor the literal `bob` is forbidden |
| d19 | `joke` with the letter `P` | `[("W4", "joke", "the label letter P is given to two kinds: joke and person")]` |
| d20 | `joke` with the letter `j` (F2) | `[("W4", "fixtures@1", "the label letter j of the kind joke is not one capital letter")]` |
| d21 | a sense over three kinds (F3) | `[("W4", "gives", "gives does not apply to one or two kinds")]` |
| d22 | a second sort with the noun `joke` | `[("W4", "gag", "the noun joke is given to two kinds: gag and joke")]` |
| d23 | an own sense `dry` over the document sort `remark` | `[]` with `docSorts = ["remark"]`; with `[]`: `[("W4", "dry", "dry applies to remark, which is not a kind of the document or of its packs")]` |
| d24 | `funny` 1 worded `{0} is funny in this document` | `[("W7", "funny", "{0} is funny in this document contains in this document")]` |
| d25 | `glossed_negative`'s equation on `funny` 1, `funny` 2 and on senses with the words `is`, `not`, `{0}`, `a b` and the empty word | true for all seven |
| d26 | `Fd` (R1) | ***hand-derived:*** `[("W6", "near", "the wording {0} is near, in the sense of beside bob belongs to two senses of near")]`: the first form of `near` 1 that a form of `near` 2 shares is its comma form without the closing comma. Under draft 1's W6 the list was `[]` and j15 failed |
| d27 | `F` plus a pack sort named `every`; one named `x1`; one named `sense__joke`; one named `Joke`; a sort and a sense with the description `""`; a gloss part of 51 letters; `funny` 1 worded `{0} is funny` and 260 more characters of words (R2, R3) | ***hand-derived:*** each case a separate change to `F` (a new sort with a letter of its own), each giving one failure: W4 for each of the first six, W2, then W3, with the texts of 4.2 |

### 8.2 Packs and identities (p), obligations

Plan 6.2, p1 to p6, unchanged; not computed (decoder, digest and Python).

### 8.3 Preamble (a), computed

`readPreamble F workBudget` on the sentences of the source unless a budget is given.

| Id | Source | Result |
|---|---|---|
| a1 | `In this document, funny means amusing.` | `ok ([(funny, 1)], 1)` |
| a2 | `In this document, funny means amusing. In this document, reviewed means rated.` | `ok ([(funny, 1), (reviewed, 2)], 2)` |
| a3 | `In this document, funny means amusing. In this document, funny means strange.` | `repeatedDefault 1 funny` |
| a4 | `In this document, purple means amusing.` | `unknownWord 0 purple` |
| a5 | `In this document, funny means purple.` | `unknownGloss 0 funny purple` |
| a6 | `In this document, tells means says aloud.` | `ok ([(tells, 1)], 1)`; `unneeded` is `[tells]` |
| a7 | `in this document , funny means amusing.` | `ok ([], 0)`: not shaped; as a document it is `stopped 0 noDerivation` |
| a8 | `The riddle is funny. In this document, funny means amusing.` | `preambleLate 1` |
| a9 | `In this document, Funny means Amusing.` | as a1 |
| a10 | `Assignment.lines` of a2's assignment (two lines), read back | a2's result |
| a11 | a10 at `b = 0`; a1 at `b = 454` and `b = 455` | `preambleBudget 0`; `preambleBudget 0`; a1's result: a1 takes 455 steps |
| a12 | `In this document, funny is amusing.` | `malformedPreamble 0` |
| a13 | `In this document funny means amusing.` (no comma) | not shaped |
| a14 | `In that document, funny means amusing.` | not shaped |
| a15 | `IN THIS DOCUMENT, funny means amusing.`; `In this document,funny means amusing.`; `In this document, funny Means amusing.`; `In this document, funny means.` | `malformedPreamble 0`, four times: shaped, and no rule derives them |
| a16 | `In this document, funny means amusing strange.` | `unknownGloss 0 funny "amusing strange"` |
| a17 | `In this document, funny means amusing.` alone, as a document | `lexical emptyDocument` (F5) |

### 8.4 Projection (j), computed

| Id | Case | Result |
|---|---|---|
| j1 | `project F [(funny, 1)] EJ LJ [funny, tells]` | `ok`, valid. Predicates: `sense__funny_1` (`{0} is funny`, `{0} is not funny`), `sense__funny_2` (`{0} is funny (meaning strange)`, `{0} is not funny (meaning strange)`), `sense__tells_1` (`{0} tells {1}`, `{0} does not tell {1}`). 16 aliases: 6 of `sense__funny_1` (four comma forms, the glossed wording and negative), 4 of `sense__funny_2`, 6 of `sense__tells_1`, negatives marked. The lexicon keeps `LJ` and adds the nouns and letters of `number` (`N`), `principal` (`R`), `resource` (`Q`), `service` (`S`) |
| j2 | j1 with no default | `ok`, valid: both `funny` senses glossed, 4 aliases each; no bare `funny` wording |
| j3 | j1 with `used = [tells]` | `ok`, valid: `sense__tells_1` only |
| j4 | j1 with `used = [funny, tells, access]` | `ok`, valid: `sense__access_1` worded `{0} may access {1}`, no declared negative in the environment, `forms.negatives` has `(sense__access_1, {0} may not access {1})`, the lexicon selects it |
| j5 | j4 with the default `(access, 1)` added | the same environment JSON, lexicon and aliases as j4 |
| j6 | `EJ` plus an own predicate `funny` worded `{0} is funny`, default `(funny, 1)` | `collision "predicate" "funny" "sense__funny_1"`. Step 6's pair rule gives the same value, with the shared wording `{0} is funny` (***hand-derived***) |
| j6b | j6 with no default | `ok`, valid: the bare wording is the document's alone |
| j7 | `EJ` plus an own predicate `peculiar` worded `{0} is strange` | `ok`, valid; `The riddle is funny (meaning strange).` reads `sense__funny_2(riddle)`, `The riddle is strange.` reads `peculiar(riddle)` |
| j8 | j1's `envJson` decoded by `Env.decode`, with j1's lexicon without its aliases, read by S2's `read` | valid; `The riddle is funny (meaning strange). Alice tells the riddle. The riddle is not funny.` reads `sense__funny_2(riddle)`, `sense__tells_1(alice, riddle)`, `not sense__funny_1(riddle)`. That Python's `Environment` loads the JSON and that its `environment_id` equals Lean's: obligation |
| j9 | j1's `envJson` | sorts `joke`, `person` as `EJ` has them, and `number`, `principal`, `resource`, `service` each with `description` and `verbalisation` |
| j10 | j1 with `used = [funny, tells, is]` | the same as j1 |
| j11 | `usedWords F` on `Alice does not tell the riddle.`; on `Alice is funny.`; on `The riddle is strange.` | `[tells]`; `[funny]`; `[]` |
| j12 | `EJ` plus a sort `story` with the letter `S` | `collision "letter" "S" "service"` (step 3) |
| j12b | `LJ` with `joke`'s letter `K`; with `person`'s letter `S` | `collision "letter" "J" "joke"`; `collision "letter" "P" "person"` (step 2) |
| j13 | a pack with one sort `gag` whose noun is `joke`, under `EJ`, `LJ` (F4) | the pack is well-formed and every premise of the plan's `project_valid` holds; `collision "sort" "joke" "gag"` from S2's V4; step 6's pair rule gives the same value (`gag`'s noun selection against the document's `joke`), with the shared wording `joke`. Its text (R10, ***hand-derived***): `The kind gag of the vocabulary pack {pack} has the noun joke, which this document already uses for joke. Change one.` |
| j14 | `LJ` with the noun `gag` for `joke` | `collision "sort" "joke" ""` (step 1); its text is the shared-kind text of 3.2 |
| j15 | `project Fd [] EJn LJn [near]`, the dictionary of d26 (R1) | ***hand-derived:*** `collision "predicate" "sense__near_1" "sense__near_2"`, from S2's V4 on the shared comma alias: the first clash is `near` 1's alias `{0} is near, in the sense of beside bob` (its wording's comma form without the closing comma) against the same alias of `near` 2, which is the shared wording; the last row of the `collision` map. `readWithSenses` stops before it, at d26's `invalidDictionary` |
| j16 | a pack with one sort over an environment of 32 sorts, with its lexicon (R4) | ***hand-derived:*** `limit "sorts"` (step 5) |
| j17 | `EJ` plus own predicates `a` worded `{0} is funny` and `b` worded `{0} is calm`, over `joke`; a pack with the sort `joke` as `F` declares it and the words `funny` and `calm`, one sense each over `joke`, worded `{0} is funny` and `{0} is calm`; both words used (verification) | ***hand-derived:*** `collision "predicate" "a" "sense__funny_1"`, shared wording `{0} is funny`: `a`'s wording is the first selection with a clash. Draft 2's independent choice of the two names gave `collision "predicate" "a" "sense__calm_1"`, whose names share no wording |

### 8.5 The gloss forms (c), computed

Derivations (cap 2) under the projection of j1 with `odd` also used; *as merged* is `grammar P.env P.lexicon`,
*with R3* the same grammar with the twin rules of 6.2. The *with R3* column below is draft 1's, from the wider
simulation; it is recomputed with the twins restricted to `clauseRows` (R8), and the expectation is that no
value changes, since every twin a c row uses is of a clause or relative row.

| Id | Source | As merged | With R3 |
|---|---|---|---|
| c1 | `The riddle is funny (meaning strange).` | 1 | 1 |
| c2 | `The riddle is funny, in the sense of strange.` | 1 | 1 |
| c3 | `Every joke that is funny, in the sense of strange, is not funny.` | 0 | 1 |
| c4 | `Every joke that is funny, in the sense of strange, and is odd (meaning strange) is not funny.` | 0 | 1 |
| c5 | `Every joke that is funny, in the sense of strange, and is odd (meaning strange) and is funny is not funny.` | 0 | 1 |
| c6 | `Every joke that is funny, in the sense of strange, and is odd (meaning strange), and is funny is not funny.` | 0 | 1 |
| c7 | `The riddle is funny ( meaning strange ).` | 0 | 0 |
| c8 | `The riddle is funny (meaning amusing).` (the default's glossed alias) | 1 | 1 |
| c9 | `Every joke that is funny (meaning strange) is not funny.` | 0 | 1 |
| c10 | `Every joke that is funny, in the sense of strange is not funny.` | 1 | 1 |
| c11 | `The riddle is funny, in the sense of strange,.` | 1 | 1 |
| c12 | `Alice tells (meaning says aloud) the riddle.` | 1 | 1 |
| c13 | `Alice tells, in the sense of says aloud, the riddle.` | 1 | 1 |
| c14 | `Alice tells, in the sense of says aloud the riddle.` | 1 | 1 |
| c15 | `Alice does not tell (meaning says aloud) the riddle.` | 1 | 1 |
| c16 | `Every joke that is funny, in the sense of strange, and is odd, in the sense of strange, and is funny is not funny.` (R9) | 0 | **2** (***computed by a reviewer***): `guard.three-left` with `funny`'s closing-comma alias, and `guard.three-right` with `odd`'s |
| c17 | `Every joke that alice tells (meaning says aloud) is odd (meaning strange).` (R8: the object relative's row ends in `)`) | 0 | 1 (***computed by a reviewer***) |

c11 is the one place the closing-comma form of an adjective reads as merged; it is a text nobody writes. c16
is `many` in the *with R3* column, so under Q4's rule (11) the comma forms are dropped if R3 ships.

### 8.6 Extension (q), computed

| Id | Case | `Extends` |
|---|---|---|
| q1 | j3's projection into j1's | true; j1's into j3's: false |
| q2 | j1's into j1 with the default `(funny, 2)` | false |
| q3 | j1 and j6 | not stated: j6 is a fault |

### 8.7 Reading (s, n, m), computed

`readWithSenses` at `workBudget`. s1 and s2 were run with both readers. s3 to s6, s10 to s14 and m2 were run
with the R3 reader only: s13 and m2 contain `J`'s first body sentence and need R3; for the others the two
readers cannot differ, because the fault precedes reading (s4 to s6), the sentence has no mark for a twin
rule to read (s3, s12), or the sentence has no derivation, which a grammar with fewer rules cannot change
(s10, s11, s14). Every other row was run with the merged grammar. Formulas are written `p(a, b)`, `#0` the
innermost variable. A map entry is `sentence: start-stop symbol`, default or switched.

| Id | Case | Result |
|---|---|---|
| s1 | `J` under `F`, `EJ`, `LJ` | **as merged:** `stopped 1 noDerivation`. **With R3:** `ok`; units `all joke. (sense__funny_2(#0) implies not sense__funny_1(#0))`; `sense__tells_1(alice, riddle)`; `sense__funny_2(riddle)`; `not sense__funny_1(riddle)` marked; states after: no referent with the binder seen, then `[alice, riddle]` three times; map `1: 4-9 sense__funny_2` switched, `1: 11-12 sense__funny_1` default, `2: 1-2 sense__tells_1` default, `3: 3-8 sense__funny_2` switched, `4: 5-6 sense__funny_1` default; mixed `[(funny, [sense__funny_2, sense__funny_1])]`; unused `[]` |
| s2 | `J` without its first line | **as merged:** `stopped 0 noDerivation`. **With R3:** `ok`; unit 0 open over `[funny]` with the candidates `[(funny, 1)]`: s1's first formula, lines `In this document, funny means amusing.`, and `[(funny, 2)]`: `all joke. (sense__funny_2(#0) implies not sense__funny_2(#0))`, lines `In this document, funny means strange.`; units 1 and 2 resolved as in s1; unit 3 open with `not sense__funny_1(riddle)` and `not sense__funny_2(riddle)`, both marked; mixed `[]`. Flip valuations: unit 0, `sense__funny_2` true alone: first candidate true, second false (the exchanged valuation; the first does not separate them); unit 3, `sense__funny_1` true alone: false, true |
| s3 | `In this document, funny means amusing. Legacy is funny.` under `EJs`; the same without the line | `illTyped`; `stopped 0 noDerivation` (both choices read and neither types, so no candidate) |
| s4 | `J` with first line `In this document, funny means purple.` | `fault (unknownGloss 0 funny purple)` |
| s5 | `J` with its line after the second body sentence | `fault (preambleLate 2)` |
| s6 | `J` under j6's environment | `fault (collision "predicate" "funny" "sense__funny_1")` |
| s7 | `Alice tells the riddle.` | `ok`; `sense__tells_1(alice, riddle)`; map `0: 1-2` default: one sense needs no line |
| s8 | `In this document, funny means amusing. The riddle is funny (meaning amusing).` | `ok`; `sense__funny_1(riddle)`; map `1: 3-8 sense__funny_1` default. S2's `checkRendering` of the unit under the projection: `The riddle is funny.` true, `The riddle is funny (meaning amusing).` true, `The riddle is funny (meaning strange).` false |
| s9 | defaults `funny` amusing and `odd` strange, then `Every funny joke is odd.` | `ok`; `all joke. (sense__funny_1(#0) implies sense__odd_1(#0))`; map `2: 1-2`, `2: 4-5` |
| s10 | default `odd` strange, then `Every funny (meaning strange) joke is odd.` | `stopped 1 noDerivation` (L3); the `GlossedNatural` rewrite is an obligation |
| s11 | `The riddle is warm, cool and mild.` under `F3` | `fault (tooManyCandidates 0 [warm, cool, mild])`: 27 choices |
| s12 | `Both alice tells the riddle and the riddle is funny.` under `F2` | `ok`; one open unit over `[funny, tells]` with four candidates, in the order `(funny 1, tells 1)`, `(funny 1, tells 2)`, `(funny 2, tells 1)`, `(funny 2, tells 2)`, each `(sense__tells_n(alice, riddle) and sense__funny_m(riddle))` with its two lines; state after `[alice, riddle]` |
| s13 | `J` with a second line `In this document, odd means strange.` (with R3) | `ok` as s1 with every sentence index one higher; unused `[odd]` |
| s14 | `J` behind a byte-order mark | `stopped 0 noDerivation` (F6): the mark is a word character, so the first sentence is not shaped and has no reading |
| s15 | `Legacy, beta and gamma are deployed.` under `F`, `ES` | `ok`; `(sense__deployed_1(legacy) and (sense__deployed_1(beta) and sense__deployed_1(gamma)))`; the map has **one** entry, `0: 6-7 sense__deployed_1`; the formula has three occurrences |
| s16 | `The riddle is odd.` under `F`, `EJ`, no line | `ok`; one open unit over `[odd]` with **one** candidate, `[(odd, 1)]`: `sense__odd_1(riddle)`, lines `In this document, odd means strange.`; the choice `(odd, 2)` reads and does not type; nothing is chosen for the author |
| s17 | `Alice is near bob.` under `Fn`, `EJn`, no line | `fault (candidatesDiverge 0 [near] (referent bob))`. Under `F` (no `near`): `stopped 0 noDerivation` |
| s18 | `In this document, near means beside. Alice is near bob.` | `ok`; `sense__near_2(alice, bob)`; state after `[alice, bob]` |
| s19 | `In this document, near means beside bob. Alice is near bob. It is near bob.` | `ok`; `sense__near_1(alice)` twice: with one referent `It` resolves, which s17's other sense would prevent |
| s20 | `Alice is near alice.` under `Fn`, `EJn`, no line | `ok`; one candidate, `[(near, 2)]`: `sense__near_2(alice, alice)`; the choice `(near, 1)` has no derivation. Both senses apply to persons, so the one-candidate text names no kind (R11) |
| s21 | `Alice tells the riddle.` at `b = 1`; with `J`'s first line before it at `b = 1` | `stopped 0 budget`; `fault (preambleBudget 0)` |
| s22 | `Both the riddle is odd and the riddle is funny (meaning strange).` under `F`, `EJ`, `LJ`, no line (R7) | ***hand-derived:*** `ok`; one open unit over `[odd]` (`funny` occurs only switched) with **one** candidate, `[(odd, 1)]`: `(sense__odd_1(riddle) and sense__funny_2(riddle))`, lines `In this document, odd means strange.`; the choice `(odd, 2)` reads and does not type. Under draft 1's `unresolvedIn` (***computed by a reviewer***): the unit was over `[funny, odd]` with two candidates of one formula, `(funny 1, odd 1)` and `(funny 2, odd 1)` |
| s23 | `In this document, near means beside. Alice is near bob. Starting from alice, bob is reachable by one or more "sense__near_2" steps.` under `Fn`, `EJn`, `LJn` (R13) | ***hand-derived:*** `fault (quotedSense 2 near)`: `sense__near_2` is binary over one sort, so S2 gives it a `relation.` row, and the third sentence's derivation uses it |
| n1 | default `funny` amusing, `The riddle is not funny.` | `not sense__funny_1(riddle)`; map `1: 4-5` |
| n2 | `The riddle is not funny (meaning strange).`, no line | `not sense__funny_2(riddle)`; map `0: 4-9` switched |
| n3 | `Alice does not tell the riddle.` | `not sense__tells_1(alice, riddle)`; map `0: 3-4 sense__tells_1`: the head is `tell` |
| n4 | default `funny` amusing, `Every joke that is not funny is odd (meaning strange).` | `all joke. (not sense__funny_1(#0) implies sense__odd_1(#0))`; map `1: 5-6 sense__funny_1` default, `1: 7-12 sense__odd_1` switched |
| n5 | `Alice may not access the api.` under `F`, `EP` | `not sense__access_1(alice, api)` |
| n6 | n5 under d9's pack | `stopped 0 noDerivation` |
| n7 | `Alice does not tell the riddle.` under `F2` | `ok`; one open unit over `[tells]` with `not sense__tells_1(alice, riddle)` and `not sense__tells_2(alice, riddle)`; state after `[alice, riddle]`; flip valuation `sense__tells_1` true alone: false, true |
| m1 | s1 with R3 | mixed names `funny` with both senses |
| m2 | `J` ending `Therefore the riddle is not funny (meaning strange).` (with R3) | mixed `[(funny, [sense__funny_2, sense__funny_1])]`: the first body sentence uses both |
| m3 | default `funny` amusing, `The riddle is funny.` | mixed `[]` |
| m4 | `The riddle is funny (meaning strange). The riddle is not funny (meaning strange).` | `ok`, both resolved; mixed `[]` |

### 8.8 The "No X that …" row (w)

Under j1's projection, without the proposed row, under both readers (computed): `No joke that is funny (meaning
strange) is funny.` 0; `No joke that is funny (meaning strange) is not funny.` 0; `No joke is funny.` 1. The
verdicts with the proposed row (plan 6.7, w8 to w10) are B9's obligations and are not item 1.

### 8.9 Service, relay and display (i, g), obligations

Plan 6.8, i1 to i7 and g1 to g10, unchanged; not computed. g1 and g4 render mid-sentence glosses and so depend
on R3.

### 8.10 The claims with two directions

| Claim | Direction | Fixture |
|---|---|---|
| `wf` exactly when `failures` is empty | empty, so well-formed | d1 |
| | a failure, so not | d2 |
| W6 compares every pair of forms of two senses except two bare forms of one word | same word, equal bare forms: passes | d1 |
| | same word, equal decorated forms: fails | d26, d2 |
| | different words, equal bare forms: fails | d11, d17 |
| a sentence is preamble-shaped exactly when it starts `in this document` and a glued comma | shaped | a1, a9, a12, a15 |
| | not shaped | a7 (comma not glued), a13 (no comma), a14 (another word) |
| a shaped line is accepted exactly when it has one derivation | one | a1, a6 |
| | zero | a4, a5, a12 |
| `lines_read`: reading the rendered lines gives the assignment exactly at a sufficient budget | sufficient | a10; a1 at 455 |
| | not | a11 (0; 454) |
| a line is `unneeded` exactly when its word has one sense | one sense | a6 |
| | two | a1 |
| a word has a default exactly when it has a line or exactly one sense | a line; one sense | s1; s7 |
| | two senses and no line | s16, s2 |
| a word is used exactly when one of its headword tokens occurs | occurs, inflected | j11 (`tell`) |
| | does not | j11 (`strange` is a gloss) |
| the automatic negative is declared exactly when `negativeTemplate` gives none | gives one and declared: refused | d8 |
| | gives none: declared or absent, accepted | d10, d9 |
| `project` returns a projection exactly when its six checks pass | pass | j1, j6b, j7 |
| | fail, one per step | j14, j12b, j12, (step 4: obligation), j16, j6 and j13 |
| `collision` has one text per fault | each row of the map | j14, j12, (step 4: obligation), j13, j6 and j17, (step 6 without a pair: obligation), j15 |
| step 6 names a pair that collides | the document's symbol and the sense share a wording | j6, j13, j17 |
| | no side in the document | j15 |
| a used word with no default is unresolved exactly when it has an unswitched occurrence | bare occurrence | s16, s2 (unit 0) |
| | switched occurrences only | s22 (`funny`) |
| an accepted derivation never uses a sense's quoted name | used: refused | s23 |
| | not used | every accepted fixture |
| `Extends` between projections | more words, same assignment | q1 |
| | fewer words; another default | q1 (reverse); q2 |
| a choice is a candidate exactly when the sentence reads and types under its projection | reads and types | s2, s12, n7 |
| | reads, does not type | s16, s3 |
| | does not read | s20 |
| `candidates` is not empty exactly when the unit is open | resolved, none | s1, s7 |
| | open | s2, s16 |
| the document continues past an open unit exactly when the successor states agree | agree | s2, s12, n7 |
| | differ | s17; the `binder` branch of the comparison by `#guard` on two states |
| the typed check of step 9 applies exactly when some unit is resolved | a resolved unit that does not type | s3 (`illTyped`) |
| | no resolved unit | s16, n7 (accepted, open) |
| an occurrence is flagged default exactly when its sense is its word's default | the default, bare or glossed | s1 (`4: 5-6`), s8 |
| | another sense | s1 (`1: 4-9`), n4 |
| `mixed_exact` | two senses in resolved formulas: listed | m1, m2 |
| | one sense, or only in candidates: not listed | m3, m4; s2 |
| `senseMap_ids` | each id of the formula is in the map and conversely | s1, s9, n4 |
| | equal as sets where the counts differ | s15 |
| S2's `checkRendering` under the projection | the bare default re-reads | s8, first and second texts |
| | another sense does not | s8, third text |
| R3: the last mark of a row, after its cut, is read glued or not | before a mark | c1 |
| | before a space | c9 (0 as merged, 1 with R3) |
| | before a space, in an object relative whose wording ends in a hole | c17 (0 as merged, 1 with R3) |
| | inner spacing stays exact | c7 |
| Q4: the comma forms stay exactly when no c fixture is `many` in the column that ships | none `many` | the *as merged* column |
| | one `many` | c16, *with R3* |

## 9. Limits, and what is not claimed

Plan L1 to L10 stand (intent and comprehension; per projection; glossed forms are clauses; kinds are sorts;
one word, one pack; candidates per unit, typed and bounded; formula-level English only; documents later;
mixed senses legal). L9 changes: the Lean-side fixtures of section 8 are now computed, by a prototype; the
rest are obligations. Added:

- **L11 Idioms in the past tense.** A sense worded as an S1 idiom in the past tense has an automatic negative
  only as the default (2.3). With R7's switch rule this costs one more reading: a word with no default whose
  only occurrence in a sentence is that idiom's glossed negative is not unresolved, so the choice that would
  make it the default is never tried and the sentence is `stopped noDerivation`. `candidates_complete` says
  nothing about such choices.
- **L12 The positions of a gloss.** Until R3 is decided, a glossed word that ends its wording, or ends a row
  after S2's cut (the object relative of `tells`, c17), reads only before a mark (F1, R8). The clause position
  of a word that does not end its wording reads always.
- **L13 All pack sorts are projected.** Every sort of a named pack enters the projection, so a document sort
  with a pack-only sort's letter is a collision the author cannot avoid by not using that sort's words (j12;
  Q12).
- **L14 A document's own predicate may take a pack word's bare wording when no default selects it** (j6b);
  with the default it is a collision (j6).
- **L15 Nothing is proved.** The statements elaborate; the prototype agrees with them on the fixtures, which
  is evidence for the statements and not a proof of any.
- **L16 Python was not run.** R3's claim about Python's pattern, F3's claim about `Environment`, the bounds
  of W2 to W4 and the counts of step 5 (R2 to R4), and every fixture of 8.2 and 8.9 rest on reading the
  source.
- **L17 Senses have no quoted name.** The named-reachability sentence cannot name a sense predicate: S2's
  `relation.` row reads it, but the reader refuses the sentence (`quotedSense`, R13), since the name is an id
  the author would have to write and the sense map could not span it.
- **L18 Draft 2 was not run.** The rows marked *hand-derived* and the three changed statements wait for G-S0's
  recomputation and re-elaboration (7).

## 10. Statement review checklist (Astra and Fable)

1. F1 is real and R3 is the right request; the *if refused* paths (6.2) are complete; no statement of 5.3
   depends on the decision.
2. W1 to W7 as written in 2.2 are the conditions `project_total` needs and no more; W6 over every pair of
   forms of two senses, bare forms of one word excepted, is sound (d26); the added W2 to W4 conditions
   (capital letter, plural, description, one or two kinds, distinct nouns; draft 2: lengths, identifier and
   reserved sort names, non-empty descriptions) are right.
3. The forms of 2.3, by parts and by the head, give the plan's forms on every wording W3 admits, and
   `glossed_negative` is true as stated for every sense.
4. The preamble: the shape test, `readLine`'s table (which fault for which line), `preambleLate` wherever a
   later line stands, `lines_read`'s premise, the empty body.
5. `project`: its six steps in that order (draft 2: the `limit` step), the mapping of S2's failures to `collision`, the projected JSON
   (no declared negative in it), the sorted lexicon; `project_valid` without premises and `project_total`
   with its premises (F4, j13).
6. `readWithSenses`: the order of its steps; typed admission; `stopped` for budget, ambiguity and rejection;
   a unit with no candidate; one candidate stays open; the successor check over both state components;
   the typed check skipped when no unit is resolved (F5).
7. `SenseUnit.after` and `stateBefore` are an acceptable way to state "the state the earlier units leave";
   `senses_unit_sound` is wanted.
8. The sense map's span rule and `isDefault`'s meaning; `mixed_exact` and `senseMap_ids` say what 3.3 says.
9. The texts of 3.2 and 4.2 have one reading each and show no number, symbol or id to a document's author.
10. The computed fixtures of section 8 are the right expectations: s1 and s2 in both columns, s12, s15, s16,
    s17, s20, n7, j6b, j13, c11 in particular.
11. Every name passes the audit's rules and collides with nothing in `VE.EnglishGrammar`, `VE.English` or
    `VE.Discourse`.
12. No public message, code, identity, frozen file or theorem statement changes, R3 apart (D10).

For draft 2 the review is bounded (7): every edit of 0.1 is applied as converged; the three changed
statements re-elaborate; the switch rule, the `limit` step, the `quotedSense` fault and the `collision` map
are as 2.5, 2.6 and 3.2 state them; and the recomputed rows match their *hand-derived* or reviewer values, or
each difference is listed as a finding.

## 11. Open points

| # | Point | Recommendation |
|---|---|---|
| Q1 to Q3, Q5, Q6, Q8 to Q10 | plan section 10 | as the plan recommends |
| Q4 | keep the two comma forms | **the rule decides** (R9): drop the comma forms if any c fixture is `many` in the column that ships, and keep the parenthetical form. With R3, c16 is `many`, so they are dropped; as merged, none is `many`, so they stay. The DRI may revise the rule only with a fixture showing `one` for c16's shape. Draft 1's "keep: no c fixture has two derivations" was false |
| Q7 | the adapter's selection rule | closed in the plan; the letters are capitals (F2) |
| Q11 | R3, its two alternatives (6.2) | R3, as restated in draft 2 (each row after its cut, `clauseRows` only); the DRI signs the one `actions_version` move. B5 waits for this decision and for Q4 |
| Q12 | project only the sorts that the used senses name, instead of every pack sort (L13) | measure in B8 how often a pack-only letter collides before changing the rule; `project_extends` holds either way |
| Q13 | `project_total`: prove, or keep the per-request check as the only guarantee | state now, prove in B3 if the `shapeOk` lemma for decorated forms is short |
| Q14 | a shared sort's letter must equal the document's (step 2) | keep (the plan's rule); the alternative, letting the document's letter win for a shared sort, removes j12b and copies no rule |

## 12. How the figures were computed

The scratch file `lean/SpecStubs_senses.lean` imported `VE.EnglishGrammar.ReadExamples` (and through it
`Extends`, `Read`, `Encode`, `Actions`, `Rules`, `Lexicon`, `Lexer` and the engine) from this worktree's build
of the merged tree (`lake build VE.EnglishGrammar.ReadExamples`, then `lake --dir lean env lean
lean/SpecStubs_senses.lean`, Lean 4.24.0, 2026-10-05). It contained:

- the signature of 5.2 with prototype bodies written from section 2 (about 600 lines; one `partial` function
  for the tree walk), except `flipModel`, `dictionaryId` and `sensesVersion`;
- the thirteen statements of 5.3 as definitions of type `Prop`, and a proof of `wf_iff_no_failure`;
- the fixture dictionaries, environments (through `ReadExamples.envJson` and `Env.decode`) and lexicons of
  section 8;
- for the *with R3* column, a second reader whose grammar is `grammar P.env P.lexicon` with, for each lexical
  row whose last symbol is an `exact` punctuation terminal glued after, one more rule that differs in that
  flag only and has the original's action index; S2's `Grammar.wf`, `terminatorFree` and `Grammar.typed` hold
  for it on j1's projection. This is wider than R3 as draft 2 states it (R8): for G-S0 the stub twins only
  the rows that `clauseRows` builds (tags `clause.`, `relative.`, `object-relative.`), and the whole *with R3*
  column is recomputed;
- `#eval` for every computed row of 8.1 and 8.3 to 8.8, and `#guard` for the two-direction rows of 8.10 that
  need no reading (`wf`, W6, the shape test, `usedWords`, `unneeded`, the budget threshold, `lines_read` on
  a2, `glossed_negative` on four adjectives, the three cases of the state comparison, `mixedOf` on hand-built
  units);
- a `Decidable` instance for `Extends` by unfolding, for q1 and q2; a constant-valued evaluator for the flip
  valuations of s2 and n7.

For G-S0 the stub also gains draft 2's definitions (the W2 to W4 bounds, `schemaReserved`, W6 over
same-word decorated forms, `switchedAt` and `unswitchedIn`, the `limit` step, `clashes` and step 6's pair
rule, the `quotedSense` check), the three changed statements, and the rows d2, d26, d27, j6, j13, j15, j16,
j17, c16, c17, s22 and s23. None of this was run for draft 2.

The final run of draft 1's whole file reported no error and no warning, and the file has no `sorry`. It is not
part of the repository; B1 re-creates its definitions module by module, and each computed row of section 8
becomes a `#guard` of `VE/Senses/Examples.lean`. A difference between the built reader and a computed row is a finding against
this specification or against the build, to be decided before the row is changed.

## 13. Edits carried over, and differences from the plan

### 13.1 The plan review's edits

The eighteen edits of plan section 12 (the converged list of Astra and Fable, three rounds, with the DRI
ruling of 2026-10-04 on the three points Astra held) are all carried by this specification. Where each lands:

| Plan edit | Here |
|---|---|
| 1 W6 over coexisting forms | 2.2 W6 (draft 1 restated it for different words only; draft 2 restores the same-word comparison of every form but two bare ones, R1); d1, d2, d11, d17, d26 |
| 2 discovery by generated forms, alias polarity | 2.3 (`headwordTokens`, `aliases`), 2.5; j11, n3, n7 |
| 3 written and formula occurrences | 2.6 (sense map), `senseMap_ids`; s15 |
| 4 typed admission, `stopped` for budget and ambiguity, provenance | 2.6 step 8, `Candidate.lines`, `candidates_complete`; s16, s3, s20, s21 |
| 5 no duplicated checks, `senses_version` | 2.6 step 7, 2.7, 6.1 |
| 6 one defaults channel, `lines_read`'s budget premise, `preamble_unique`'s type | 2.4, 5.3; a10, a11 |
| 7 the shape test and the malformed-line faults | 2.4; a12 to a16 |
| 8 the request's lexicon, pack letters | 2.5; j12, j12b, d19, d20 |
| 9 `wordOf` from the map | 5.2 |
| 10 aliases fixed by the projection | 2.5 |
| 11 `GlossedNatural` as a Lean text | 3.2 |
| 12 `candidatesDiverge` reachable (DRI 1) | 2.6, 3.2; d18, s17, s18, s19 |
| 13 a candidate under its own projection (DRI 2) | 2.6 (candidates), `senses_candidate_sound` |
| 14 interim interfaces and validation (DRI 3) | D19 as amended: the build merged before B0 ran, so the stub is against it |
| 15 the identity count | 2.7 |
| 16 zero-training English unverified | 3.1, L1 |
| 17 batch order | 7 (plan section 5 stands) |
| 18 G-S0's counterexample fixtures | 7; all present, computed |

### 13.2 Differences from the plan, for the statement review

| Plan text | This specification | Why |
|---|---|---|
| the gloss forms read in every position (plan 2.3, c3 to c6, s1) | they read after a word that ends its wording, or ends a row after S2's cut, only before a mark; R3 requested | F1, computed; R8, c17 |
| a pack sort has a name, a noun and a lower-case letter | name, noun, plural, description, capital letter | F2, F3 |
| kinds unbounded in number | one or two | F3 |
| W6 lists the same-word comparisons (glossed forms only) | every pair of forms of two senses, bare forms of one word excepted, comma forms included; draft 1's "different words only" withdrawn | R1, d26: the comma form without its closing comma can coincide; d2 now reports W2 and W6 |
| a gloss of words of three or more letters; a sort with a noun and a letter | parts of 3 to 50 letters; forms, nouns and plurals of at most 256 characters; sort names that Python accepts; descriptions not empty | R2, R3 |
| `project` with no count check | a `limit` step and `project_total`'s count premises | R4 |
| an unresolved word is a used word with no default | a used word with no default and an unswitched occurrence | R7, s22 |
| no rule for a sense's quoted name | `quotedSense` | R13, s23 |
| Q4: keep if every c fixture is `one` | drop if any c fixture is `many` in the column that ships | R9: c7 is `zero` by design, so the plan's literal rule dropped already; c16 |
| the one-candidate text says the sense "fits a joke" | "gives a reading of this sentence" | R11, s20 |
| `project_valid` with six premises | no premise; `project_total` proposed | F4, j13 |
| `project` runs `Lexicon.failures` "with own predicates" | always | F4 |
| `SenseUnit` with three fields; `stateBefore` a relation left to the review | a fourth field `after`; `stateBefore` a function of the units | 5.3 note |
| no statement for a resolved unit beside an open one | `senses_unit_sound` proposed | 5.3 note |
| a unit with no candidate "is `none`" | `stopped i noDerivation` with the `NoSenseFits` hint | `senses_resolved_one_reading` needs every unit of an accepted document to have a formula or a candidate |
| `typedDocument` on every resolved formula | when there is one; an empty body is `emptyDocument` | F5 |
| R1 requested | not needed | 6.1 |
| the stub in two files, the second against interim S2 names | one file against the merged build | D19 |
| d2's detail `gloss amusing repeated` | the English text of 4.2 | details are relayed to people |
| d11 with the word `strange`; j12 by changing `person`'s letter; s3 without a default; s14 `lexical` | rewritten to isolate one condition each; s14 `stopped 0 noDerivation` | F6 |
| the mixed report `[sense__funny_1, sense__funny_2]` | order of first occurrence: `[sense__funny_2, sense__funny_1]` | `mixed_exact` defines the order |
| `unneeded` a display notion | a Lean function | Lean owns the warning's source |

### 13.3 The statement review's edits (draft 2)

The review (`manage-agents/debates/senses-spec/`, Astra and Fable, three rounds, 2026-10-05) converged on FIX:
the union of both reviewers' lists with Astra's qualifications and Fable's round-3 precisions. Section 0.1
lists the thirteen edits with the places they land in this specification. Where the reviewers left a choice
to the applier:

- **The quoted name (R13).** Fable offered a fault or a premise and preferred the fault; Astra required only
  that `senseOccurrences`, the map, `mixed` and their texts not overclaim. The fault is taken: it errs
  safely, keeps the theorems unconditional and keeps an id out of what the author writes.
- **The count limit (R4).** A projection fault, `limit`, at step 5, before the build; `project_total` takes
  both counts as premises, so it stays total on its domain.
- **Exhaustiveness (R6).** The one conjunct is placed in `senses_unit_sound`, which therefore takes the unit
  without its formula; draft 1's conclusion is kept under `∀ F m, u.formula = some (F, m) →`.
- **The one-candidate text (R11).** One text for every one-candidate unit; no typing reason is given, since
  the reader does not record why a choice was dropped.
- **W6's failures.** One failure per pair of senses, so d2 reports one W6 failure after its W2 one, as d11 and
  d17 report one.

**The verification of draft 2** (`manage-agents/senses-p3ver1.final.md`, read-only, no model call) found two
defects, both corrected here. (1) R10's map was not total: step 6 chose the document's symbol and the sense
independently, so the two need not collide (j17), and `{wording}` could not be filled. Step 6 now takes both
names from one entry of `clashes`, the colliding pairs of S2's V4 comparison, whose shared text is
`{wording}`; S2's `Lexicon.failures` still alone decides refusal; a failure list with no V4 entry gets its
own row, so the map is total. j15's value changes accordingly (`sense__near_2` in place of
`sense__near_1`); j6 and j13 keep theirs. (2) R7's switch rule said "three words" before the four words
`in the sense of`; it says four. Nothing else changed.

**The plan (`senses-PLAN.md`)** is aligned in its operative text: its status note, W2, W4 and W6 (2.2), the
Q4 rule (2.3, Q4), the switch rule (2.4, 2.6), the `limit` and `quotedSense` faults (2.5, 2.6), the
colliding pair of a `collision` (2.5), the one-candidate text (2.8), B5, G-S0 and G-S1. Where the two still differ, this specification governs.

### 13.4 The integration review's fix round (2026-10-06)

The integration reviews (`manage-agents/senses-review-astra.final.md`, `manage-agents/reviews/senses-review-fable.md`)
gave FIX. No statement of 5.3 changed (`test_statement_equals_the_approved_text`); the signature of 5.2 gained
what the fixes need:

| Finding | Change | Where |
|---|---|---|
| Astra A1: the cap built every choice | `choiceCount`, proved equal to the capped length (`choiceCount_eq`, `choiceCount_gt_iff`); thirty two-sense words stop at once | 2.6 step 8, 5.2; `Examples.lean` A1 rows, `test_every_refusal_carries_its_arguments[a1-30-words]` |
| Fable B3: words inside a gloss counted as occurrences | `unglossed`, read by `usedWords` and `unswitchedIn` | 2.5, 2.6 (R7), 5.2; `Examples.lean` B3 rows, `test_gloss_words_are_not_occurrences` |
| Astra B1, Fable B2: the response dropped the unit state and the refusals' arguments | `stopped` carries the stopping grammar's rule tags; the route writes the fields of 4.1 *as built* | 4.1, 5.2; `test_every_refusal_carries_its_arguments`, `test_s2_outcomes_match_the_english_route` |

