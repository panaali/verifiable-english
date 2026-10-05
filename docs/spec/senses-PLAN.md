# Vocabulary out of the box: senses (plan)

**Status:** plan, draft 2 (converged by DRI ruling), 2026-10-04, branch `design/senses`. Planning only: no
code, proof, test or model call. Brief: ARCH-ROADMAP entries (a) to (e), "Vocabulary out of the box without
losing one reading" (lead-approved 2026-10-04). It builds on english-lean S2
([english-lean-s2.md](english-lean-s2.md) draft 5, the **S2 spec**, and
[english-lean-S2-PLAN.md](english-lean-S2-PLAN.md) draft 6, both on `design/english-lean-s2`), on the S1 build
on `english-lean/integrate` at `689219b1` (`Lexicon.valid`, `lex`, the engine), and on the ownership rules of
`docs/LEAN-FIRST-PLAN.md` draft 3 (branch `design/lean-first`; the **lean-first plan**). Section numbers
written `S2 2.6` refer to the S2 spec, `base 2.9` to [english-lean.md](english-lean.md). **Nothing was built
or run for this draft.** Every expected value in section 6 is derived by hand and is an obligation on the
implementation, not a measurement. Every `file:line` was read on 2026-10-04 and must be re-read at each step.

**Draft 2** applies the plan review's converged edits (Astra and Fable, three rounds, 2026-10-04) and the DRI
ruling of the same day on the three points Astra held; section 12 lists every edit with the finding it
answers. The verdict is BUILD with mandatory B0 corrections: the corrections are in this draft, and B0's
statement review (D16) gates the amended text before any proof.

**Status note, 2026-10-05 (no design edit).** B0's statement spec is [senses.md](senses.md) draft 1. Its stub
ran against the S2 build that `main` now carries (merged into this branch at `7746f24a`), so the fixtures of
section 6 that the Lean side decides were computed there, not derived by hand. Six computed results differ
from this plan's hand-derived text (the gloss forms in mid-sentence, label letters, the pack sort fields and
arity, `project_valid`, the typed check on an empty list, several fixture values); spec section 0 lists them
as findings F1 to F6 for the statement review and the DRI. Where the two documents differ on a computed value, the spec is the measurement and this plan
is the expectation it overturned; nothing else in this plan changed after draft 2 except that n3 is named in
the two counterexample lists (5.1 B0, G-S0), as the review's joint position has it.

**Alignment note, 2026-10-05 (statement review).** The statement review of the spec
(`manage-agents/debates/senses-spec/`, Astra and Fable) converged on FIX, applied in [senses.md](senses.md)
draft 2 (its section 0.1, edits R1 to R13). This plan's operative text is aligned with it where the review
touched it: W2, W4 and W6 (2.2); the Q4 rule (2.3, 10); the switch rule for unresolved words (2.4, 2.6); the
`limit` and `quotedSense` faults (2.5, 2.6); the one-candidate text (2.8); B5, G-S0 and G-S1. **Where this plan
and the spec differ, the spec governs**: its statements (spec 5.3) replace those of 4.3 here, and its fixtures
(spec 8) replace the hand-derived values of section 6. The W1, soft and P0 contracts are untouched.

**Evidence for the need** (ARCH-ROADMAP, 2026-10-04): writing a small VE joke needed about five declaration
lines per word in the environment file (name, argument sorts, description, wording, negative wording), the
negatives were written by hand, and the text hit the "No X that …" gap (S2's W12, `No service that is
deployed is not reviewed.` has no derivation). The joke itself is not in the repository; section 6.6 writes
a joke of the same shape as the end-to-end fixture, and section 7 measures the before and after on it.

## 0. Decision in brief

A **sense dictionary** gives each word numbered senses, each with a meaning description, argument kinds, a
wording and (automatically for simple adjectives) a negative wording. A document names the packs it uses
and, for each word with more than one sense that it uses bare, **one default sense in one English line**
(`In this document, funny means amusing.`). Any occurrence may switch sense with a short gloss the parser
recognises (`funny (meaning strange)`, or `funny, in the sense of strange,`). A word used bare with no
default and more than one sense is not guessed: the sentence becomes an **open reading set** with one
candidate per sense, so the document's answers are conditional until the author chooses. Mixed senses of one
word in one document are an **editor warning**, never a rejection.

Zero-training English (people read and write these texts as regular English, with no symbol, number or id)
is the target of this design and is **unverified** here: the measured claims of section 7 are declaration
counts and parsing outcomes; nothing in this plan measures whether a novice understands a sense line or a
gloss (limit L1).

Three things are decided here and nowhere else.

1. **Lean owns all of it.** The dictionary's validity, the preamble lines, the choice of sense for every
   occurrence, the projection onto S2's lexicon, the reading, the sense map, the mixed-sense report and the
   candidates of an unresolved word are Lean definitions behind one service mode, `senses.read`. The preamble
   is the reader's one channel for defaults (no assignment argument, D5). The document's own lexicon arrives
   in the request as it does for `english.read` (S2's one producer, validated by Lean); the projection appends
   only what the dictionary determines (D8, Q7). Python keeps files (packs, the review pin, the reading-set
   file it writes from Lean's candidates), the CLI and the display (inline gloss, glossary, hover data,
   warnings). No Python mirror exists, so the operation has `authority: lean` from its first commit
   (lean-first rule 6: no new Python semantics).
2. **S2 is untouched.** A sense is an ordinary predicate of a *projected* environment, with an ordinary wording;
   the senses layer is a producer of S2's `Env`, `Overlay` and `Lexicon` (2.5), and S2's `Lexicon.valid` (V1 to
   V5), `read`, `EnglishOneReading` and the six identities decide the body exactly as for any other document.
   A non-default sense's glossed wording is its ordinary selected wording; the comma forms are aliases fixed
   by the projection (not by a profile block) and carried in `forms.aliases`, the carrier base 2.9 already
   reads. One reading per sentence is therefore S2's theorem applied to the projection, not a new claim.
3. **Precision machinery stays invisible by default.** People read and write words, one plain line per
   default, and the two gloss forms. Sense numbers, sense ids and the projected environment never appear in
   what people read or write; they are in the stored JSON and the service response only.

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | A **pack** is a reviewed JSON file (`ve/senses/packs/<name>@<n>.json`) of sorts and senses; a document names its packs and may add **own senses** in its front matter. A pack sort declares its noun and its label letter. Packs are request data that Lean validates (`Dictionary.wf`) and identifies (`dictionary_id`), as overlays are today; no generated Lean literal, no lock file (Q2 records the alternative) | 2.2, 2.7 |
| D2 | A **sense** is a predicate: id `sense__<word>_<n>`, argument sorts (its *kinds*), one wording in which the word occurs exactly once. Kinds are sort names of the pack or the document; there is no polymorphism over sorts in this plan (Q3) | 2.2 |
| D3 | The dictionary's negatives are **automatic**: `negativeTemplate` of the (bare or glossed) wording, the S1 function, unchanged. A pack declares a negative only where the automatic one does not exist (modal wordings); a declared negative enters the projection as a profile-fixed negative (V5's exception) | 2.3 |
| D4 | A word's **default** sense is the bare wording's meaning. A word with one sense has it as default with no line. The default's wording is the bare one; every other sense's wording is the **glossed** one, `word (meaning gloss)`, with `word, in the sense of gloss,` and `word, in the sense of gloss` as input aliases; the default also accepts its glossed forms as aliases | 2.3, 2.4 |
| D5 | Defaults are **preamble lines**: `In this document, <word> means <gloss>.`, leading sentences only, read by the S1 engine on a grammar with one rule per sense. A later such line is a fault. The preamble is the reader's **one channel**: `readWithSenses` takes no assignment. `ve-document@1` (B11) may give the same assignment as exact ids in its JSON front matter; the Lean `document` mode renders them as the lines (`Assignment.lines`) and prepends the lines to the source before reading, so every rendered form carries them and no merge rule exists | 2.4, 4.2 |
| D6 | A bare word with no default and more than one sense has no rule. The sentence is read once per sense choice of its unresolved words (at most `candidateCap` = 8 choices), each under its own projection; a choice is a **candidate** exactly when the sentence reads and types under that projection. The candidates are an open reading set. The document continues only when every candidate leaves the same document state; otherwise the unit is `candidatesDiverge`, a reachable fault (2.6, s17) that the run-time check owns. Lean also proposes one **flip model** per candidate pair; Python writes the W2 reading set from them and the existing readings route checks it. A candidate is rendered and re-checked under the Lean-computed projection of its choice, with its resolving line | 2.6, 4.2 |
| D7 | **Mixed senses** (one word read under two senses in one document) are computed by Lean from the formulas and reported; Python displays a warning. Nothing rejects | 2.6 |
| D8 | The projected environment is ordinary environment JSON (sorts, predicates, constants) built by Lean; `typedDocument`, Python's renderer and every other consumer read it as they read any environment. Its `environment_id` is computed by Lean with the existing identity (lean-first 2.2); S2's six identities are those of the projection; `dictionary_id` and `senses_version` are added (D17). The document's own lexicon is the request's, as for `english.read`; the projection appends the pack nouns and letters and the sense forms, and copies no selection rule (Q7). No existing identity changes | 2.5, 2.7 |
| D9 | The **sense map** (per sentence: token span, sense id, word, gloss, description, default flag) is computed by Lean from the derivation and the projection; hover, inline gloss and glossary are three displays of it. The checked text carries every sense: defaults in the preamble, switches inline. The glossary and footnotes are display additions and never the only place | 2.8 |
| D10 | Documents without a `senses` request are unaffected: no public message, code, identity, frozen file or theorem statement changes | everywhere |
| D11 | The "No X that …" shape (`No joke that is funny (meaning strange) is funny.`) is written as a **proposed** row of S2's fixed-rule source with its meaning, measured on the fixtures, and excluded from the generated table until signed (S2 D11, Q10 of the S2 spec) | 5 (B9), 6.7 |
| D12 | `Dictionary.wf` checks distinctness, by `wordingKey`, of every pair of forms that can **coexist under one assignment** (two senses of one word never both select their bare wording), so V4 of the projected lexicon is a lookup and `project_valid` is provable | 2.2, 4.3 |
| D13 | The reserved words of the dictionary (`reservedWords`) are one Lean list; Python's `_RESERVED` (`ve/english.py:47`) is the duplicate E2 deletes. The preamble keywords `in this document`, `means`, `meaning`, `in the sense of` are reserved in wordings, nouns and glosses | 2.2, 8 |
| D14 | Starter packs (policies and permissions, rights, software services, risk) are seeded from the use cases' reviewed overlays and the UDHR and constitution pilots' vocabularies, reviewed, and pinned in `ve/senses/reviewed-packs.json`. OEWN stays advisory, for proposing entries only | 5 (B8) |
| D15 | Nothing is claimed about intent: a chosen sense is the author's declaration. Silent ambiguity stays forbidden (D6 never guesses) | 9 |
| D16 | The statement review (Astra and Fable, converged) of the item-1 spec comes before any proof, as for S2 | 5 (B0) |
| D17 | `senses_version` is a **separate identity** with its own lock list (`ve/senses/LOCK.json`), not folded into `actions_version`: a senses change never changes an ordinary document's identities (D10). A response carries S2's six identities, `dictionary_id` and `senses_version` | 2.7 |
| D18 | A word is **used** when a body sentence contains one of its headword tokens, the tokens at the word's position in its generated forms (bare, negative, glossed, comma), so `tell` in `Alice does not tell the riddle.` finds `tells` (n3, n7). Discovery never scans for the headword alone | 2.5 |
| D19 | B0's stub elaborates the dictionary, assignment, preamble and projection statements against the S1 build and the S2-dependent statements against **named interim interfaces** (a stub file of S2's signatures). That is a shape check, not validation: every S2-dependent statement is re-elaborated against the merged S2.3 build before B5 is accepted (G-S0b) | 4.2, 5 (B0), 7.1 |

## 2. The design

### 2.1 Terms

| Term | Meaning |
|---|---|
| word | a lower-case ASCII word that a pack or a document gives senses to (`funny`) |
| sense | one numbered meaning of a word, with its kinds, wording, gloss and description (2.2) |
| gloss | the one-to-three-word English key of a sense that people write and read (`strange`); distinct among a word's senses |
| description | the sense's meaning in free English; displayed, never parsed |
| kind | an argument sort of a sense (`joke`); a sort of the pack or of the document |
| pack | a reviewed file of sorts and senses (`software-services@1`) |
| dictionary | the packs a document names plus its own senses |
| assignment | the document's default sense per word (its preamble) |
| default | the sense a bare occurrence of a word means in this document |
| switch | an occurrence written with a gloss, meaning that sense whatever the default |
| unresolved word | a word used bare with no default and more than one sense |
| projection | the S2 environment and lexicon that the dictionary and assignment determine for a document (2.5) |
| preamble | the leading `In this document, … means ….` sentences of a text (2.4) |
| body | the sentences after the preamble |

### 2.2 The dictionary: words, senses, packs

A pack file:

```json
{"format": "ve.sense-pack@1", "name": "fixtures@1",
 "sorts": [{"name": "joke", "noun": "joke", "letter": "j"}, {"name": "service", "noun": "service", "letter": "s"},
           {"name": "person", "noun": "person", "letter": "p"}, {"name": "number", "noun": "number", "letter": "n"}],
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

(The last entry belongs to the policies pack; it is shown for the declared-negative case, and the fixture
pack of section 6 adds the two sorts it needs.) Hidden from people: `index`, the ids, the JSON. Shown to
people: the word, the gloss, the description and the wordings.

**`Dictionary.wf`** (Lean, 4.2) holds when every condition below holds; `Dictionary.failures` lists each
failure as (condition, word or pack, detail), in condition order, and `wf` is "no failure".

| # | Condition |
|---|---|
| W1 | **Words.** A word is two to fifty lower-case ASCII letters and not in `reservedWords`. The senses of a word in a pack have indices `1` to `n`, each once. A word belongs to exactly one pack of the dictionary; an own sense of the document does not use a pack word |
| W2 | **Glosses.** A gloss is one to three words of three to fifty lower-case ASCII letters, none in `reservedWords`, not equal to the word, and not equal to the word of any sense of the dictionary; the glosses of one word's senses are pairwise distinct by `wordingKey`. Every form of a sense (2.3) has at most 256 characters (spec W3, Python's verbalisation limit) |
| W3 | **Wording.** The wording passes S1's `shapeOk` for arity `kinds.length`, begins with `{0}`, contains the word exactly once as a whole word, and contains no `(`, `)`, `.`, `means`, `meaning` or `in the sense of` |
| W4 | **Kinds and sorts.** Every kind is a sort of the pack, or, for an own sense, of the document or a named pack. A pack sort has a noun that passes S1's noun conditions (V2's honest forms: the declared noun) and a label letter, one lower-case ASCII letter; the letters of the dictionary's sorts are pairwise distinct (their distinctness from the document's letters is the per-request check of 2.5). As amended by the spec (F2, F3, R2, R3; the pack and fixtures of this plan predate it): the letter is one capital ASCII letter; a sense has one or two kinds and a description that is not empty; a pack sort has a plural and a description that is not empty, a noun and plural of at most 256 characters, and a name that Python's `Environment` accepts (`[a-z][a-z0-9_]*`, at most 64 characters, not a reserved schema word, not `x` and digits) and that does not begin with `sense__` |
| W5 | **Negative.** When `negativeTemplate wording kinds.length` is `some t`, the entry has no `negative` (it would duplicate `t`). When it is `none`, the entry may declare one; a declared negative passes W3's shape and word conditions, differs from the wording, and begins with `{0}` |
| W6 | **Distinctness of coexisting forms.** Two forms are compared only when one assignment can select both. For every two different senses: every form of one against every form of the other (the wording, the glossed wording, the two comma forms, the negative, automatic or declared, and the glossed and comma forms of that negative), pairwise distinct by `wordingKey`, **checked, not argued**, with one exception: for two senses of the **same** word, their bare forms **may coincide**, since at most one of them is the default under any assignment (`F`'s two `funny` senses both have `{0} is funny`, d1). Distinct glosses do not keep the decorated forms apart: `near` with glosses `beside` and `beside bob` and wordings `{0} is near bob` and `{0} is near` share the comma form `{0} is near, in the sense of beside bob` (spec R1, d26). Every form of every sense is distinct by `wordingKey` from every pack noun and plural |
| W7 | **Reserved phrases.** No wording, negative, noun or gloss contains `in this document` |

W6 is what makes V4 of the projected lexicon a lookup (D12): under one assignment the projection selects,
for each word, one bare wording (the default's) and the decorated forms of the others, and W6 has compared
every pair two senses can select together. W2's "not equal to the word of any sense" keeps a gloss from reading as a switch to
another word. Nothing in W1 to W7 constrains the arity or the literal words of two senses of one word
against each other beyond distinctness: `{0} is near bob` (unary) and `{0} is near {1}` (binary) are both
legal senses of `near` (d18), which is why the run-time state check of 2.6 exists.

### 2.3 Glossed forms and automatic negatives

For a sense `s` and a text `t` in which `s.word` occurs once as a whole word:

| Form | Text | Role |
|---|---|---|
| bare | `t` | the default sense's selected wording |
| glossed | `t` with the word replaced by `word (meaning gloss)` | a non-default sense's selected wording; an alias of the default |
| comma, mid-sentence | the word replaced by `word, in the sense of gloss,` | an input alias |
| comma, final | the word replaced by `word, in the sense of gloss` | an input alias |

`(` and `)` are punctuation tokens of the S1 lexer (base 2.2), so `funny (meaning strange)` lexes as the word,
`(` glued after, `meaning`, `strange`, `)` glued before, and the rules carry those flags: no other spacing is
accepted (DRI ruling 1 on O1). The two comma forms exist because the brief's `funny, in the sense of strange,`
closes with a comma mid-sentence and cannot at a sentence end; both are aliases, never the selected wording,
and the c fixtures decide whether they stay, by Q4's rule: **if any c fixture is `many` in the column that
ships (spec 8.5: as merged, or with R3), the comma forms are dropped and the parenthetical form alone
remains** (open question Q4). The spec's c16 (`Every joke that is funny, in the sense of strange, and is odd,
in the sense of strange, and is funny is not funny.`) has two derivations with R3, so with R3 the comma forms
are dropped unless the DRI revises the rule with a fixture showing `one` (spec R9).

**Negatives.** The selected negative of a sense is `negativeTemplate` of its *selected* wording (bare or
glossed), when that exists: `{0} is funny` gives `{0} is not funny`, `{0} is funny (meaning strange)` gives
`{0} is not funny (meaning strange)`, `{0} tells {1}` gives `{0} does not tell {1}`. This is V5 by
construction (`glossed_negative`, 4.3). A declared negative (W5) is glossed by the same replacement and enters
the projection as a profile-fixed negative, V5's exception. No pack and no document writes a negative for a
simple adjective: that is ARCH-ROADMAP (b).

**The simple-adjective families of S2.** A default sense whose wording is `{0} is w` with `w` one lower-case
word is exactly S2's adjective family (S2 2.6), so `Every funny joke is reviewed.`, `Some joke is funny and
odd.` and `The riddle is funny, odd and reviewed.` read as S2 reads them. A glossed wording is not of that
shape and has the clause and relative forms only (limit L3).

### 2.4 Documents: preamble, defaults, switches, unresolved words

**Preamble.** The leading sentences of the form `In this document, <word> means <gloss>.` A sentence is
**preamble-shaped** when its first three word tokens fold to `in this document` and the next token is a comma
glued before (`preambleShaped`, 4.2); the test reads no dictionary. The preamble is the longest leading run of
preamble-shaped sentences; the body starts at the first sentence that is not shaped. A shaped sentence is read
with the S1 engine on `preambleGrammar D` (one rule per sense, 4.2) under the budget `b`: `verdict` `some (.one
t)` names one sense (`preamble_unique`); `none` (budget exhausted) is `preambleBudget`; otherwise the line is
shaped but underivable, and the fault is found by lookup: its fourth token is not a word of the dictionary,
`unknownWord`; the tokens between `means` and the period are not one of that word's glosses, `unknownGloss`,
with the senses listed in the text (3.2); any other shaped remainder (no `means`, extra words, no period in
place) is `malformedPreamble`. One line per word; a second line for the same word is `repeatedDefault`. A
preamble-shaped sentence after the body has started is `preambleLate` (a8). A line for a word with one sense is
allowed and reported as `unneeded` (display only). The preamble is the reader's one channel for defaults
(D5): `readWithSenses` takes no assignment, so no rule for a disagreement between a supplied assignment and
the text is needed.

**Defaults.** `defaultOf D A w` is the assigned sense, else the only sense when `w` has one, else none.

**Switches.** A glossed occurrence means its sense whatever the default. Because every non-default sense's
selected wording is glossed and the default's bare, a text's reading never depends on an occurrence that is
not written: the bare word is the default or nothing.

**Unresolved words.** A sentence that uses a bare word with no default has no derivation under the
projection (the bare wording of that word is nobody's). The reader then (2.6) lists the unresolved words of
that sentence and reads it once per choice of a sense for each, under the projection of the assignment
extended by that choice. A word whose every occurrence in the sentence is **switched** (followed by `(` and
`meaning`, or by a comma and `in the sense of`) is not unresolved there: its gloss names its sense whatever
the assignment, so a choice for it would only add candidates that differ in nothing (spec R7, s22). The sentence's unit is open; the document continues from the same state (checked,
2.6). Nothing is guessed, and a sentence with no unresolved word that has no derivation stays `none`, as in
S2.

**`ve-document@1`.** The front matter gains `"senses": {"packs": ["software-services@1"], "defaults":
{"funny": 1}, "own": [ … ]}`. `defaults` holds exact indices; the Lean `document` mode renders them as
preamble lines (`Assignment.lines`) and **prepends** the lines to the source before `readWithSenses` reads
it, so the preamble stays the one channel and a document with both front-matter defaults and written lines
is read as one preamble (a repeated word is then `repeatedDefault`, as in plain text). The unit fences stay
formula-level English read sentence by sentence; the document form is batch B11, after the lean-first
`document` mode exists (lean-first batch 16a), with the data shape fixed here.

### 2.5 The projection onto S2's lexicon

`project D A E L used` builds, from the dictionary, the assignment, the document's own environment `E`
(sorts, predicates, constants with their declared forms, as today), the document's own lexicon `L` (the
proposed lexicon of the request, exactly what `english.read` receives from S2's one producer, S2 2.10; it must
pass `L.valid E {}` first, else S2's `invalidGrammar lexicon`) and the used words, the S2 triple.

**Used words** (D18). The **headword tokens** of a word are the whole-word tokens that stand at the word's
position in each of its generated forms: for `tells`, `tells` from `{0} tells {1}` and `tell` from the
automatic negative `{0} does not tell {1}`; the glossed and comma forms add no token beyond these. A word of
`D` is used when some body sentence contains one of its headword tokens, folded (`usedWords`, 4.2). The scan
is over generated forms, never the headword alone, so a verb written only negatively is found (n3) and a
two-sense verb written negatively with no default is unresolved, not `noDerivation` (n7). A token that is a
headword token of no word is ignored (j10).

| S2 input | Content |
|---|---|
| `Env` | `E`'s sorts plus the pack sorts (with their nouns as declared nouns; a pack sort that names a sort of `E` is that sort when the two nouns agree by `wordingKey`, else `collision sort <name>`); `E`'s predicates and constants unchanged; for each used word and each of its senses, one predicate `sense__<word>_<n>` with `args` = kinds, declared `wording` = the selected wording of 2.3 (bare for the default, glossed otherwise), declared `negative` = the automatic negative when it exists; `profiles` = `E.profiles` (no new profile: the projection is an ordinary environment); `forms.negatives` = `E.forms.negatives` plus the declared (W5) negatives, glossed where the sense is not the default; `forms.aliases` = `E.forms.aliases` plus `Sense.aliases` of each sense (4.2), each **with its polarity**: the comma forms of the selected wording negated `false`, those of the selected negative negated `true`, and for the default sense its glossed wording and glossed negative likewise. These aliases are fixed by the projection, not by any profile block; `forms` is the carrier `Lexicon.valid` reads (V2 compares `L.aliases` with `Env.forms.aliases`); `source` = the projected environment JSON (below) |
| `Overlay` | empty: the overlay, if any, is already applied to `E`'s own forms, as S2's adapter applies it (S2 2.10) |
| `Lexicon` | `L`'s entries for `E`'s own symbols, unchanged (nouns, letters, wordings, negatives, aliases, spellings: the producer's selections, validated), **plus** what the dictionary determines: each pack sort's declared noun and declared letter (W4), and for each sense predicate its selected wording, its selected negative when one exists, and its aliases as above. No selection rule of the S2 adapter is copied (Q7, R2 withdrawn): `project` appends, it never chooses. Lean checks the pack letters: a pack sort merged with a sort of `E` (same name, nouns agreeing) must carry `L`'s letter for it, and every other pack sort's letter must differ from every letter of `L` (else `collision letter <l> <sort>`; j12) |

Every selection is an honest *declared* form of its own symbol (V2), has the right holes (V3, by W3), is
distinct from every other symbol's forms (V4, by W6 for the sense forms among themselves and by the
run-time check against `E`'s own forms and `L`'s selections), and every negative is `negativeTemplate` of its
wording or profile-fixed (V5, by D3). V1 holds by construction. So `Lexicon.valid` holds for a well-formed
dictionary over a validated base lexicon of a document with no own predicates (`project_valid`, 4.3, with
`L.valid E {} = true` among its premises); with own predicates, `Lexicon.failures` is run and any failure is
reported as `collision` naming the document's symbol and the sense (3.2): the author declared a wording a
pack already gives, and the message says which. Before the build, `project` checks Python's counts on the
projected environment (at most 32 sorts and 256 predicates, `ve/limits.py:6–7`), which no pack check can
hold since they count the document's own symbols too: `fault (limit …)` (spec 2.5 step 5, R4).

**The projected environment JSON** is `E`'s validated JSON with the pack sorts and the sense predicates
inserted into `vocabulary` in canonical order, each predicate with `arguments`, `description` (the sense's),
`verbalisation` and, when it exists, `negative_verbalisation`. `typedDocument` reads it (S2 2.3), Python's
renderer reads it, and its `environment_id` is the existing identity computed by Lean (D8). It never
contains the word `senses` and names no new profile: it is an environment like any other, and a document
that stored it and dropped its packs would read every text written with the selected wordings (bare
defaults, parenthetical switches) to the same formulas under S2 alone (j8); only the comma aliases, which
live in `forms`, need `senses.read`. That is the sense in which the data extends S2's lexicon without
touching its identity rules.

**Extension.** `used ⊆ used2` gives `Extends` between the two projections (S2 2.13: every symbol kept with
its signature, every selection kept, both valid), so by `grammar_extension` a sentence that reads under the
smaller projection reads the same under the larger or is rejected as ambiguous, never silently differently
(`project_extends`, 4.3; stated against S2's `Extends` body and proved after S2.3 accepts it).

### 2.6 Reading with senses

`readWithSenses D E L b s` (4.2):

1. `D.wf`, else `fault (invalidDictionary f)` with the first failure.
2. `lex s`, else `lexical r` (S2's codes). The preamble is read from the sentences (2.4) by `readPreamble`:
   the assignment `A` and the line count `k`, else its fault.
3. `used` from the body sentences by headword tokens (2.5); `L.valid E {}`, else `invalidGrammar lexicon`
   (S2's outcome for the request's own lexicon); `project D A E L used`, else `fault (collision …)`.
4. S2's three grammar checks on the projection, else `invalidGrammar why`. Then the body is read sentence by
   sentence with S1's `readSentence`, from `DState.init`, under the budget `b` (S2's `workBudget`):
   - `.ok A m`: a resolved unit;
   - `noDerivation`, and the sentence has unresolved words (used, no default, and at least one occurrence not
     switched, 2.4): every choice of one sense per unresolved word is
     tried (more than `candidateCap` choices: `fault (tooManyCandidates i words)`), each with `readSentence`
     under the projection of `A.extend choice` from the same state. **Typed admission:** a choice is a
     candidate exactly when its outcome is `.ok F m` and `typedDocument P2.env [F]` holds under its projection
     `P2`; `noDerivation` and an ill-typed formula drop the choice (the `odd` senses over `joke` and `number`
     make `The riddle is odd.` keep one candidate, s16); any other outcome of any choice, `.budget`
     (`Reading.lean:50`), `.ambiguous` or `.rejected`, is the unit's `stopped i o`, so a dropped alternative
     is never confused with exhausted work. Enumeration is exhaustive within the cap, which is what
     `candidates_complete` states. Zero candidates: the unit is `none` with the unresolved words named (3.2).
     One candidate: the unit is still unresolved with that one candidate; nothing is guessed (D15), and the
     text names the one sense to declare. **Successor states:** the document continues only when every
     candidate's successor `DState` (`referents` and `binderSeen`, S1 `Syntax.lean:79–84`) is equal; otherwise
     `fault (candidatesDiverge i words why)`. The fault is **reachable**: S2 computes the successor referents
     from the constants in the formula (S2 2.7), and two senses of one word may differ in arity, so `{0} is
     near bob` reads `Alice is near bob.` with referents `{alice}` and `{0} is near {1}` with `{alice, bob}`,
     which changes what a later `It` can resolve (s17). Dictionary validity cannot exclude this, since
     constants are document-local; the run-time check is the right owner, and it compares both components of
     the state. The text (3.2) names the differing referent or the binder and asks the author to choose a
     sense;
   - any other outcome: `stopped i o`, S2's outcome for a sentence that is not a sense problem.
   - in either reading branch, a derivation that uses S2's quoted-name `relation.` row of a sense predicate
     (a binary sense over one sort, `Rules.lean:182–190`) is `fault (quotedSense i word)`: the name is an id
     the author would write, and the sense map cannot span it (spec R13).
5. `typedDocument` on every resolved formula, else `illTyped` (candidates were typed at admission, under
   their own projections).
6. The **sense map**, keyed by **written occurrence**: for each sentence, each lexical rule of a sense
   predicate in its derivation, as the rule's token span, its sense from the projection's map and the default
   flag, once per written occurrence; for an unresolved unit, the occurrences of the candidates' choices are
   listed per candidate. A written occurrence may stand for several formula occurrences (S2's subject
   coordination reads `Legacy, beta and gamma are deployed.` into three `pred` nodes from one adjective token,
   s15); the map does not repeat it, and `senseMap_ids` relates the two as sets (4.3). The **mixed** report:
   each word whose resolved occurrences (candidates excluded) use two or more sense ids, with those ids. The
   **unused defaults**: assigned words that no body sentence uses.
7. For each unresolved unit and each pair of candidates, a **flip model**: one entity per sort the unit
   mentions (and the constants it mentions), the first candidate's differing sense true everywhere and the
   second's false, every other predicate false; if the two formulas evaluate differently under it (Lean's
   evaluator), it is the pair's distinguishing model; else the complement; else the pair is reported
   `undistinguished` and no reading set is proposed for that unit (the unit stays open with its candidates
   listed). The models are proposals that the existing readings route checks when Python writes the set (B7).

**Candidate provenance.** Each candidate carries its `choice`, its formula and mark, and its **resolving
lines**, `Assignment.lines D (A.extend choice)`: the preamble under which this candidate is the one reading
of its sentence. The service (B6) adds, per candidate, the identities of its projection (`environment_id`,
`lexicon_id`, `grammar_id` of `project D (A.extend choice) E L used`). Rendering a candidate as English and
checking that rendering use the **Lean-computed projection of that choice**, obtained through the service's
`senses.project` mode with the candidate's resolving lines; the resolving lines alone do not make the base
projection (in which the unresolved word has no bare rule) fit to render or re-read a candidate. The display
(2.8) shows each candidate with the lines of its `choice` that the document does not yet have.

The result `ok units sm mixed unused P` carries the units (formula and mark, or candidates), the sense map,
the reports and the projection (its environment JSON, lexicon and identities). Sentence numbers in faults,
texts and the sense map count from the first sentence of the text, the preamble included: unit `i` of the
body is sentence `k + i`, and the texts of 3.2 show the number as S2's texts show theirs.

### 2.7 Identities and evidence

Every `senses.read` response carries S2's six identities **of the projection** (`environment_id` of the
projected environment, `overlay_digest` absent, `lexicon_id`, `grammar_id`, `actions_version`,
`source_sha256` of the whole source, preamble included), plus:

| Field | Identity of | Computed as |
|---|---|---|
| `dictionary_id` | the dictionary | the digest, under the new domain `ve-senses-dictionary-v1`, of the canonical JSON of the named packs (name and content) and the own senses, in order |
| `senses_version` | the senses definitions | the string constant `sensesVersion` of the senses modules, locked by `ve/senses/LOCK.json` (D17) |
| `assignment` | the defaults | the list of (word, index) in word order, inside the response; it is bound by `source_sha256` (the preamble is in the source) |

`senses_version` is a **separate** identity (D17). Its lock file `ve/senses/LOCK.json` holds the SHA-256 of
each senses definition file (`Dictionary`, `Assignment`, `Preamble`, `Project`, `Read`, `Decode`), and the
commit hook fails when a hash changes and the version does not, as S2's lock does for `actions_version` (S2
2.9, i5). The senses files are **not** added to `ve/english_grammar/LOCK.json`: folding them into
`actions_version` would force a bump that changes every ordinary `english.read` response, against D10. So a
change to `project`, `Dictionary.wf` or the preamble grammar changes `senses_version` and leaves the six
identities of documents without senses equal. A record that cites a reading with senses cites S2's six
identities of the projection, `dictionary_id` and `senses_version`. A record that cites a candidate cites, in
addition, the identities of the candidate's projection (2.6). No existing identity changes (D8, D10).

A pack is **reviewed** when its `dictionary_id` for that pack alone is pinned in `ve/senses/reviewed-packs.json`
with the reviewer's name, date and scope, as `ve/reviewed-overlays.json` pins overlays; the response's
`review_status` of each pack is read from that repository file by Python (provenance display, as today for
overlays; not a semantic decision).

### 2.8 Display

| Where | What the reader sees | Source |
|---|---|---|
| the checked text | the preamble lines, then the body with a gloss on every occurrence that is not the default and nothing on the default | the text itself; the renderer produces exactly this from the projected environment's wordings and Lean's `Assignment.lines`, and Lean's `checkRendering` confirms the round trip |
| hover (editor, web app) | on any sense word: its gloss and description, and `default` or `switched` | the sense map's entry for that span |
| glossary (print, `--glossary`) | a block after the text: one line per used sense, `funny: amusing (the default); funny (meaning strange): odd, hard to explain`, and the unused defaults | the sense map and the reports; display only, outside the checked text |
| warnings | `The word funny is used in two senses here: amusing (sentences 2, 5) and strange (sentences 2, 4).`; `The line for odd is not needed: odd has one sense.` | the mixed and unused reports |
| unresolved | `Sentence 2 uses funny, which has two senses here: amusing; strange. Add the line "In this document, funny means amusing." or write funny (meaning strange).`, with the candidates as English sentences, each under the lines of its choice that the document does not yet have; with one candidate (s16): `Sentence 2 uses odd, which has two senses here, and only strange gives a reading of this sentence. Add the line "In this document, odd means strange." to say so.` (no typing reason is claimed: in the spec's s20 the other sense fails by derivation, spec R11) | the candidates and the dictionary |
| diverging | the `CandidatesDiverge` text of 3.2, naming the referent or the binder that differs | the fault |

Rule (ARCH-ROADMAP (e)): every rendered form carries each sense in the text (preamble and inline); hover
and glossary add, never replace. Python formats; every text above is a fixed Lean text with the slots
filled, relayed verbatim (lean-first rule 2); the English of each candidate is Python's renderer over the
candidate's formula under the **Lean-computed projection of its choice** (`senses.project` with the
candidate's resolving lines, 2.6), re-read by Lean's `checkRendering` under that same projection; the base
projection is never used to render a candidate.

### 2.9 Ownership: one owner per piece

| Logic | Owner | Python |
|---|---|---|
| pack schema validity, word and gloss rules, distinctness (`Dictionary.wf`) | Lean | reads the file bytes, sends them |
| the preamble: which lines, which sense | Lean (`readPreamble`); the one channel for defaults | none (B11's front matter becomes lines inside the Lean `document` mode) |
| which words are used (discovery by generated forms, D18) | Lean (`usedWords`) | none |
| the document's own lexicon (nouns, letters, spellings, selections for `E`'s symbols) | S2's one producer, as for `english.read`; validated by Lean (`L.valid`) | sends it in the request, as the `english.read` adapter does |
| the comma and glossed aliases of the senses | Lean (`Sense.aliases`, fixed by the projection; carried in `forms.aliases`, not profile data) | none |
| which sense an occurrence means | Lean (the projection's selected wordings and S2's reader) | none |
| the projected environment and lexicon, their identities | Lean (`project`, the existing identity; the `senses.project` mode) | writes the JSON when asked (`ve senses project`), compares bytes with `--check` |
| the one-reading decision of the body | Lean (S2's `read`, called) | none |
| candidates of an unresolved word (typed admission, state equality), flip models | Lean | writes the W2 reading-set file; the readings route validates it |
| the projection a candidate is rendered and checked under | Lean (`senses.project` for the candidate's resolving lines) | renders under it, never under the base projection |
| sense map, mixed, unused | Lean | displays |
| `senses_version` and its lock | Lean constant, `ve/senses/LOCK.json`, the commit hook | none |
| automatic negatives | Lean (`negativeTemplate`, S1) | none for sense predicates (`negative_template` in Python is the E2 deletion) |
| reserved words | Lean (`reservedWords`) | `_RESERVED` deleted in E2 |
| review status of a pack | repository file | displays |
| proposing pack entries from OEWN | Python tool (`tools/senses_propose.py`, B8), untrusted, never at check time | — |

## 3. English: one reading each

### 3.1 What people write

| Form | Example |
|---|---|
| a default | `In this document, funny means amusing.` |
| a switch, parenthetical | `The riddle is funny (meaning strange).` |
| a switch, comma, mid-sentence | `Every joke that is funny, in the sense of strange, is not funny.` |
| a switch, comma, final | `The riddle is funny, in the sense of strange.` |
| a negative | `The riddle is not funny.`, `The riddle is not funny (meaning strange).`, `Alice does not tell the riddle.` |

Nothing else is new. No number, symbol or id is ever written or shown.

### 3.2 The texts of the new outcomes

| Code | Text |
|---|---|
| `InvalidDictionary` | `The vocabulary pack {pack} is not usable: {detail}.` with `detail` one of the W1 to W7 texts, for example `the word funny has two senses with the gloss strange` |
| `UnknownWord` | `Line {i} gives a meaning for {word}, which is not a word of this document's vocabulary.` |
| `UnknownGloss` | `Line {i} says {word} means {gloss}. The senses of {word} here are: {gloss₁}; {gloss₂}. Use one of them.` |
| `RepeatedDefault` | `Line {i} gives {word} a second meaning. A document picks one.` |
| `MalformedPreamble` | `Line {i} begins "In this document," but is not of the form "In this document, <word> means <gloss>."` |
| `PreambleBudget` | `Line {i} could not be read within the work budget. Raise the budget or shorten the line.` |
| `PreambleLate` | `Sentence {i} gives a word a meaning. Such lines come first, before any other sentence.` |
| `Collision` (wording) | `The wording {wording} is both in the vocabulary pack {pack} (for {word}) and declared by this document for {symbol}. Keep one.` |
| `Collision` (letter) | `The label letter {letter} is used both by the vocabulary pack {pack} (for {sort}) and by this document (for {sort₂}). Change one.` |
| `Collision`, every case | superseded by the spec's total map from `collision kind name sense` to one text (spec 3.2, R10), which adds the text for a pack kind whose noun the document already uses |
| `VocabularyLimit`, `QuotedSense` | spec 3.2 (R4, R13) |
| `TooManyCandidates` | `Sentence {i} uses {n} words with no chosen sense: {words}. Choose a sense for at least one of them first.` |
| `CandidatesDiverge` (referent) | `Sentence {i} uses {word} with no chosen sense, and its senses do not agree on what the sentence is about: read as {gloss₁} it mentions {name}, read as {gloss₂} it does not. Later sentences depend on that, so choose: add the line "In this document, {word} means {gloss₁}." (or {gloss₂}), or write {word} (meaning {gloss₁}).` |
| `CandidatesDiverge` (binder) | `Sentence {i} uses {word} with no chosen sense, and its senses do not agree on whether the sentence speaks of every or some thing of a kind: read as {gloss₁} it does, read as {gloss₂} it does not. Later sentences depend on that, so choose: add the line "In this document, {word} means {gloss₁}." (or {gloss₂}), or write {word} (meaning {gloss₁}).` |
| `GlossedNatural` (a hint beside S2's `none`, not a rejection) | `Sentence {i} has no reading: a word with its meaning in brackets goes after its noun, not before it. Write "{rewrite}" instead.` with `rewrite` the sentence rewritten by Lean with the natural subject as a relative clause (s10: `Every joke that is funny (meaning strange) is odd.`) |
| `Unresolved` (an outcome of a unit, not a rejection) | 2.8, both forms (several candidates; one candidate) |
| `Mixed`, `Unneeded` (warnings) | 2.8 |

S2's codes and texts for the body are unchanged. Lean's texts are canonical (lean-first DRI answer 3). The
`CandidatesDiverge` texts replace draft 1's "Report this: it should not happen": the fault is reachable
(2.6) and the author resolves it by choosing a sense.

### 3.3 The theorems, in plain words

| Statement | Plain English | It does not say |
|---|---|---|
| `wf_iff_no_failure` | A dictionary is well-formed exactly when its list of failed conditions is empty. | |
| `preamble_unique` | Every preamble line the reader accepts has exactly one derivation in the preamble grammar, so it names one sense. | that the author meant that sense |
| `lines_read` | Rendering an assignment as preamble lines and reading them back, with a budget under which each line parses, gives that assignment. | anything at a budget too small to parse a line (a11): the reader then stops with `preambleBudget` |
| `glossed_negative` | The automatic negative of a glossed simple adjective is the glossed automatic negative. | anything about declared negatives |
| `project_valid` | For a well-formed dictionary and assignment over a document whose own lexicon is valid, has no own predicates and shares no sort name, noun, display form or label letter with the packs, the projected lexicon passes S2's validity. | anything with own predicates or shared forms: that is checked per request |
| `project_extends` | Using more words extends the projection in S2's sense, so existing sentences keep their reading or become ambiguous, never different. | anything about reselection: a changed default is a new document |
| `senses_resolved_one_reading` | If the senses reader accepts a document and every unit is resolved, the body has one reading under the projection in S2's sense (every sentence one derivation, typed), from the initial state, with the preamble the text itself carries. | anything about intent |
| `senses_candidate_sound` | Each candidate of an unresolved unit is the one reading of that sentence under the projection of the preamble's assignment extended by its choice, from the state the earlier units leave, its formula is typed under that projection, and its resolving lines are that extended assignment's lines. | that the candidates are distinguishable (the flip models are checked, not proved); that their successor states agree (checked at run time, `candidatesDiverge`) |
| `candidates_complete` | The candidates are exactly the choices of senses for the unresolved words under which the sentence reads and types, when the number of choices is within the cap. | anything when a choice stops with a budget or ambiguity outcome: the unit is then `stopped`, not unresolved |
| `mixed_exact` | The mixed report names exactly the words whose resolved occurrences use two or more senses, with those senses. | |
| `senseMap_ids` | The sense map of a resolved sentence names every sense its formula uses and no other. | the spans, and how many times: one written word can stand for several formula occurrences (coordination, s15); both are tested |

## 4. Lean: definitions and the exact statements

### 4.1 Modules and conventions

New files only, in `lean/VE/Senses/`, namespace `VE.Senses`, layer 3 (`tools/layer_policy.py`); the service
mode in `EnglishMain.lean` (S2.4's executable, not frozen; `Main.lean` is frozen) in layer 4. Conventions as
base 5.1 and base 6: no prime, no `?`, no totality escape, the audit's forbidden words absent from comments
too, one `#print axioms` line per theorem in `VE/Audit.lean`, every file in the frozen inventory, the JSON
files pinned in `ve/assurance-manifest.json`, `tools/lean_statements.py` re-run after every Lean edit. The
candidate evaluation uses the existing evaluator (`VE.Eval`, `eval_iff_denote`) through the typed decoder,
not a copy.

| Module | Content |
|---|---|
| `VE/Senses/Dictionary.lean` | `Sense`, `PackSort`, `Pack`, `Dictionary`, `reservedWords`, the forms of 2.3, `headwordTokens`, `Dictionary.failures`, `wf`, `wf_iff_no_failure`, `glossed_negative` |
| `VE/Senses/Assignment.lean` | `Assignment`, `wf`, `defaultOf`, `lines` |
| `VE/Senses/Preamble.lean` | `preambleShaped`, `preambleGrammar`, `readPreamble`, `preamble_unique`, `lines_read` |
| `VE/Senses/Project.lean` | `usedWords`, `Projection`, `Projection.wordOf`, `project`, `envJson`, `project_valid`, `project_extends` |
| `VE/Senses/Read.lean` | `Candidate`, `SenseUnit`, `Divergence`, `SenseFault`, `SensesOutcome`, `readWithSenses`, `senseMap`, `mixed`, `flipModel`, the statements of 4.3 |
| `VE/Senses/Examples.lean` | the fixtures of section 6 as `#guard` checks |
| `VE/Senses/Decode.lean` | the pack and request decoders, `dictionaryId` |

### 4.2 The signature

```lean
namespace VE.Senses
open VE.EnglishGrammar VE.Grammar

structure Sense where
  word : String
  index : Nat                    -- 1-based within the word; never displayed
  gloss : String                 -- the key people write: one to three words
  description : String           -- displayed, never parsed
  kinds : List String            -- argument sorts in order; arity = kinds.length
  wording : String               -- `{0} is funny`; the word occurs once as a whole word
  negative : Option String := none   -- only where negativeTemplate gives none (W5)
  deriving DecidableEq, Repr

structure PackSort where
  name : String
  noun : String
  letter : String                    -- one lower-case ASCII letter (W4)
  deriving DecidableEq, Repr

structure Pack where
  name : String
  sorts : List PackSort
  senses : List Sense
  deriving Repr

structure Dictionary where
  packs : List Pack
  own : List Sense                   -- the document's own senses, over its own or pack sorts
  deriving Repr

def reservedWords : List String        -- Python's `_RESERVED` plus `means`, `meaning`, `document`
def Sense.symbol (s : Sense) : String := "sense__" ++ s.word ++ "_" ++ toString s.index
def Sense.arity (s : Sense) : Nat := s.kinds.length
def Sense.isSimpleAdjective (s : Sense) : Bool := s.wording == "{0} is " ++ s.word && s.kinds.length == 1
/-- `t` with its one whole-word occurrence of `s.word` replaced by `s.word ++ " (meaning " ++ s.gloss ++ ")"`. -/
def Sense.glossed (s : Sense) (t : String) : String
/-- The two comma forms of 2.3: with and without the closing comma. -/
def Sense.commaForms (s : Sense) (t : String) : List String
def Sense.selectedWording (s : Sense) (isDefault : Bool) : String :=
  if isDefault then s.wording else s.glossed s.wording
/-- The automatic negative of the selected wording, when it exists. -/
def Sense.automaticNegative (s : Sense) (isDefault : Bool) : Option String :=
  negativeTemplate (s.selectedWording isDefault) s.arity
/-- The declared negative, glossed when the sense is not the default. -/
def Sense.fixedNegative (s : Sense) (isDefault : Bool) : Option String :=
  s.negative.map fun n => if isDefault then n else s.glossed n
/-- The input aliases of 2.3 with their polarity: the two comma forms of the selected wording (`false`) and
of the selected negative (`true`); for the default sense also its glossed wording and negative. Fixed by the
projection; carried in `Env.forms.aliases` (2.5). -/
def Sense.aliases (s : Sense) (isDefault : Bool) : List (String × Bool)
/-- The whole-word tokens at the word's position in the sense's generated forms, folded: `tells` and `tell`
for `{0} tells {1}` (D18). -/
def Sense.headwordTokens (s : Sense) : List String
abbrev DictFailure := String × String × String                   -- condition, word or pack, detail
def Dictionary.senses (D : Dictionary) : List Sense
def Dictionary.sorts (D : Dictionary) : List PackSort
def Dictionary.failures (D : Dictionary) (docSorts : List String) : List DictFailure   -- W1 to W7
def Dictionary.wf (D : Dictionary) (docSorts : List String) : Bool := (D.failures docSorts).isEmpty
def Dictionary.sensesOf (D : Dictionary) (w : String) : List Sense

structure Assignment where
  defaults : List (String × Nat)     -- word, index; at most one entry per word
  deriving DecidableEq, Repr
def Assignment.wf (D : Dictionary) (A : Assignment) : Bool
def Assignment.extend (A : Assignment) (c : List (String × Nat)) : Assignment
def defaultOf (D : Dictionary) (A : Assignment) (w : String) : Option Sense
/-- `In this document, funny means amusing.` per default, in word order. -/
def Assignment.lines (D : Dictionary) (A : Assignment) : String

def preambleGrammar (D : Dictionary) : Grammar Terminal     -- one rule per sense; start 0; all ranks 0
/-- Dictionary-independent: the first three word tokens fold to `in this document` and a comma glued before
follows (2.4). -/
def preambleShaped (w : List Tok) : Bool
/-- The leading preamble-shaped sentences (2.4): their assignment and their count, or the first fault
(`unknownWord`, `unknownGloss`, `malformedPreamble`, `repeatedDefault`, `preambleBudget`). -/
def readPreamble (D : Dictionary) (b : Nat) (sents : List (List Tok)) : Except SenseFault (Assignment × Nat)

/-- The words of `D` one of whose headword tokens occurs in a sentence (D18). -/
def usedWords (D : Dictionary) (sents : List (List Tok)) : List String

structure Projection where
  env : Env
  lexicon : Lexicon
  envJson : Lean.Json                                  -- the projected environment (2.5)
  map : List (String × Sense × Bool)                  -- predicate id, sense, is default
  deriving Repr
/-- The word of a sense predicate, from `map`; ids are never parsed. -/
def Projection.wordOf (P : Projection) (id : String) : Option String
/-- `L` is the document's own lexicon, validated (`L.valid E {}`) before the call; the projection appends
the pack nouns and letters and the sense forms to it (2.5). -/
def project (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String) :
    Except SenseFault Projection

/-- Why two candidates' successor states differ (2.6): a constant one mentions and the other does not, or
`binderSeen`. -/
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
  | collision (kind name : String) (sense : String)        -- kind `predicate`, `sort` or `letter`
  | tooManyCandidates (sentence : Nat) (words : List String)
  | candidatesDiverge (sentence : Nat) (words : List String) (why : Divergence)
  deriving DecidableEq, Repr

structure Candidate where
  choice : List (String × Nat)       -- the unresolved words' senses
  lines : String                     -- `Assignment.lines D (A.extend choice)`: the resolving lines (2.6)
  formula : EFormula
  mark : Bool
  deriving DecidableEq, Repr

structure SenseUnit where
  formula : Option (EFormula × Bool)  -- some when resolved
  candidates : List Candidate         -- nonempty exactly when unresolved
  unresolved : List String
  deriving DecidableEq, Repr

structure SenseOccurrence where
  sentence : Nat
  start : Nat                         -- token index
  stop : Nat
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
  | illTyped

def candidateCap : Nat := 8
/-- No assignment argument: the preamble inside `s` is the one channel for defaults (D5). -/
def readWithSenses (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String) : SensesOutcome
def mixedOf (P : Projection) (units : List SenseUnit) : List (String × List String)
def senseOccurrences (P : Projection) (A : EFormula) : List String   -- the sense ids in `A`, with repetition
def flipModel (P : Projection) (c d : Candidate) : Option Lean.Json   -- 2.6 (7); the existing model wire form
def dictionaryId (D : Dictionary) : String
def sensesVersion : String
```

The body reading is S2's. To state the theorems over the body's sentences, S2's `read` is asked to be
written as `lex`, then `readSentences E O L b (sents : List (List Tok))` (the three checks, `readDocument`,
`typedDocument`), with `read E O L b s = match lex s with | .ok sents => readSentences … sents.toList | …`.
That is a request to S2.3 (R1 in section 10); it changes no S2 statement. If refused, `readWithSenses`
**calls** S2's exported functions itself, in `read`'s order (`Lexicon.valid`, `Grammar.wf` and
`terminatorFree`, `typed` and the start type, then `readDocument` and `typedDocument`), and the statements
below are written against `readDocument` directly; no check is re-implemented in the senses modules.

**Interim S2 interfaces (D19).** The S2 build does not exist when B0 runs. The stub therefore comes in two
files: `lean/SpecStubs_senses.lean` elaborates the dictionary, assignment, preamble and projection statements
(`wf_iff_no_failure`, `glossed_negative`, `preamble_unique`, `lines_read`, `project_valid`, `mixed_exact`)
against the S1 build, whose `Lexicon`, `Lexicon.valid`, `lex`, `verdict`, `readSentence`, `DState`,
`DocOneReading` and `negativeTemplate` are real; `lean/SpecStubs_senses_s2.lean` declares, as `opaque`
constants with the signatures of S2 5.2 to 5.4, the names the reading statements need and S1 lacks
(`grammar`, `meaning`, `acts`, `typedDocument`, `Extends`, `ReadOutcome`, `GrammarFault`) and elaborates
`project_extends`, `senses_resolved_one_reading`, `senses_candidate_sound`, `candidates_complete` and
`senseMap_ids` against them. The second file is a **shape check** of the statements, not validation: it
proves nothing about S2, and the names it declares are listed in the B0 report as interim. Validation is the
re-elaboration of those five statements against the merged S2.3 build, unchanged or with every difference
listed and re-reviewed, before B5 is accepted (G-S0b). Both stub files stay uncommitted, as S2's did.

### 4.3 The exact statements

Superseded by spec 5.3 (draft 2), which governs: `project_valid` without premises, `project_total` and
`senses_unit_sound` added, and the changes of the statement review (R4 to R6). The text below is draft 2 of
this plan, kept as the record the spec's 13.2 compares against.

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

theorem lines_read : ∀ (D : Dictionary) (ss : List String) (b : Nat) (A : Assignment) (sents : Array (Array Tok)),
  D.wf ss = true → A.wf D = true → lex (A.lines D) = .ok sents →
  (∀ w ∈ sents, verdict (preambleGrammar D) b w ≠ none) →
  readPreamble D b (sents.toList.map (·.toList)) = .ok (A, A.defaults.length)

theorem project_valid : ∀ (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used : List String)
    (P : Projection),
  D.wf (E.sorts.map (·.name)) = true → A.wf D = true → L.valid E {} = true → E.predicates = [] →
  (∀ t ∈ E.sorts, t.name ∉ D.sorts.map (·.name)) →
  (∀ t ∈ E.sorts, ∀ n, t.noun = some n → ∀ n2 ∈ D.sorts.map (·.noun), wordingKey n2 ≠ wordingKey n) →
  (∀ c ∈ E.constants, ∀ d, c.display = some d → ∀ n ∈ D.sorts.map (·.noun), wordingKey n ≠ wordingKey d) →
  (∀ x ∈ L.letters, ∀ t ∈ D.sorts, x.2 ≠ t.letter) →
  project D A E L used = .ok P → P.lexicon.valid P.env {} = true

theorem project_extends : ∀ (D : Dictionary) (A : Assignment) (E : Env) (L : Lexicon) (used used2 : List String)
    (P P2 : Projection),
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
    units.map (·.formula) = rs.map some ∧
    P.lexicon.valid P.env {} = true ∧
    DocOneReading (grammar P.env P.lexicon) (meaning (grammar P.env P.lexicon) (acts P.env P.lexicon))
      DState.init ((sents.toList.drop k).map (·.toList)) rs st2 ∧
    typedDocument P.env (rs.map (·.1)) = true

theorem senses_candidate_sound : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (units : List SenseUnit) (sm : List SenseOccurrence) (mx : List (String × List String)) (un : List String)
    (P : Projection) (i : Nat) (u : SenseUnit) (c : Candidate),
  readWithSenses D E L b s = .ok units sm mx un P →
  units[i]? = some u → c ∈ u.candidates →
  ∃ sents A k used P2 st1 w,
    lex s = .ok sents ∧ readPreamble D b (sents.toList.map (·.toList)) = .ok (A, k) ∧
    used = usedWords D ((sents.toList.drop k).map (·.toList)) ∧
    project D (A.extend c.choice) E L used = .ok P2 ∧ P2.lexicon.valid P2.env {} = true ∧
    c.lines = Assignment.lines D (A.extend c.choice) ∧
    (sents.toList.drop k)[i]? = some w ∧
    stateBefore D E L b s i st1 ∧
    (readSentence (grammar P2.env P2.lexicon) (meaning (grammar P2.env P2.lexicon) (acts P2.env P2.lexicon))
      st1 b w).1 = .ok c.formula c.mark ∧
    typedDocument P2.env [c.formula] = true

theorem candidates_complete : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (units : List SenseUnit) (sm : List SenseOccurrence) (mx : List (String × List String)) (un : List String)
    (P : Projection) (i : Nat) (u : SenseUnit) (choice : List (String × Nat)) (F : EFormula) (m : Bool),
  readWithSenses D E L b s = .ok units sm mx un P → units[i]? = some u → u.candidates ≠ [] →
  (choice ∈ choicesOf D u.unresolved ∧
   ∃ A P2 st1 w, preambleOf D b s A ∧ project D (A.extend choice) E L (usedOf D s) = .ok P2 ∧
     stateBefore D E L b s i st1 ∧ sentenceAt s i w ∧
     (readSentence (grammar P2.env P2.lexicon) (meaning (grammar P2.env P2.lexicon) (acts P2.env P2.lexicon))
       st1 b w).1 = .ok F m ∧
     typedDocument P2.env [F] = true)
  ↔ ∃ c ∈ u.candidates, c.choice = choice ∧ c.formula = F ∧ c.mark = m

theorem mixed_exact : ∀ (P : Projection) (units : List SenseUnit) (w : String) (ids : List String),
  (w, ids) ∈ mixedOf P units ↔
    ids = ((units.filterMap (·.formula)).flatMap
             (fun (A, _) => (senseOccurrences P A).filter (P.wordOf · == some w))).eraseDups ∧
    2 ≤ ids.length

theorem senseMap_ids : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (units : List SenseUnit) (sm : List SenseOccurrence) (mx : List (String × List String)) (un : List String)
    (P : Projection) (i : Nat) (F : EFormula) (m : Bool),
  readWithSenses D E L b s = .ok units sm mx un P → units[i]? = some ⟨some (F, m), [], []⟩ →
  ∃ sents A k, lex s = .ok sents ∧ readPreamble D b (sents.toList.map (·.toList)) = .ok (A, k) ∧
    ∀ id, id ∈ (sm.filter (fun o => o.sentence == k + i && o.candidate.isNone)).map (·.symbol)
          ↔ id ∈ senseOccurrences P F
```

`stateBefore`, `sentenceAt`, `choicesOf`, `usedOf` and `preambleOf` are the small definitions the stub
writes to name the state after the first `i` units of the body (the state `readDocument` threads; equal
across a unit's candidates by the run-time check of 2.6, which is a premise of continuing, not a theorem),
the sentence `i` of the body, the product of the unresolved words' senses, the used words of a source, and
the assignment the source's preamble gives. Their exact bodies are fixed at the statement review; the stub
elaborates every statement above as a `Prop`-valued definition first (base 5.1), against the S1 build for the
dictionary, assignment, preamble and projection statements, and against the interim S2 interfaces of 4.2 for
the reading statements (D19), which are re-elaborated against the merged S2.3 build before B5 is accepted.
Three statements changed shape in draft 2 and the review should read them first: `preamble_unique` compares
S1's `verdict G b w : Option (Verdict T)` (`Table.lean:284`) with `some (.one t)`; `lines_read` carries the
sufficient-budget premise, without which it is false at `b = 0` (a11); `senseMap_ids` is set membership,
not a permutation, because one written occurrence can stand for several formula occurrences (s15).

### 4.4 Proof notes and fallbacks

| Statement | Argument | Fallback if the stub or the proof fails |
|---|---|---|
| `wf_iff_no_failure` | unfolds `wf` | none needed |
| `glossed_negative` | `negativeTemplate` on a text that begins with `{0} is ` is the `replaceFirst` branch; the replacement commutes with the gloss insertion after the prefix | none needed: a string lemma |
| `preamble_unique` | two derivations of one line are two rules with the same yield; the yield fixes the word (fold) and the gloss words (fold); W2 makes the gloss keys distinct, and a gloss's `wordingKey` is its fold (letters and single spaces only); so the rules are one sense, one rule; then `verdict_one` of the engine | stated as a `Prop` definition, with the per-request check (`verdict = .one`) that `readPreamble` performs anyway |
| `lines_read` | each line is the yield of its sense's rule and is preamble-shaped; the budget premise makes `verdict` `some`, and `preamble_unique`'s argument makes it `.one`; the lexer's treatment of `In`, the comma and the period | as above |
| `project_valid` | V1 by construction; V2: every selection is the declared form the projection wrote, and `L`'s selections are declared forms of `E` by `L.valid`; V3: W3 and `shapeOk` of the glossed form (the gloss adds words, no hole); V4: W6 is the pairwise key check over exactly the forms one assignment selects, plus the sort-name, noun, constant-display and letter premises against `E` and `L`; V5: automatic negatives are `negativeTemplate` of the selected wording by definition, declared ones are in `forms.negatives` | the theorem is deferred with the DRI's signature and the per-request `Lexicon.valid` stays the guarantee; the plan then claims "checked per request", not "by construction" |
| `project_extends` | `envSub`: sorts, predicates with `args`, constants kept; `lexiconSub`: every entry of the smaller projection is an entry of the larger (`L`'s entries are in both; the same word gives the same entries); `Extends` needs S2 2.13's body as accepted | stated only, until S2.3 accepts `Extends`; q-fixtures of 6.5 test it |
| `senses_resolved_one_reading` | unfolds `readWithSenses`: all units resolved means every `readSentence` returned `.ok`, which is `readDocument`'s `.ok` branch; then S2's `read_ok` argument on the body sentences (R1) | none needed if R1 is accepted; else the proof is against `readDocument`, through the calls of 4.2 |
| `senses_candidate_sound`, `candidates_complete` | the candidates are computed by exactly the right-hand side: the product of choices, `readSentence` under each choice's projection, `typedDocument` of the formula; `.budget`, `.ambiguous` and `.rejected` leave the `.ok` branch, so the unit is `stopped` and the statements do not apply; the state equality is checked at run time (`candidatesDiverge`) | none needed |
| `mixed_exact`, `senseMap_ids` | definitions unfolded; for `senseMap_ids`, membership both ways from the tree walk: every lexical rule of a sense predicate in the derivation yields `pred` nodes of that sense and every `pred` node of a sense comes from such a rule (coordination yields several nodes from one rule) | `senseMap_ids` stated only if the tree-walk correspondence is long; the fixtures (s1, s15) test it |

Theorems are proved after the statement review (B0, D16), as S2.3's are.

## 5. Batches

Every batch is 2 to 6 hours, ends with its fixtures passing and its `done when`, and names what it deletes
or declines to duplicate. Lean batches need the S1 build (`english-lean/integrate` at `689219b1`) unless
they say S2; the S2 build is S2.3 and S2.4 of the S2 plan (`read`, `EnglishOneReading`, the executable).
Order, following the Needs column: B0 → statement review → B1 → B2; B4 after B1; B3 after B2 (its base
lexicon is S1's `Lexicon` type and `Lexicon.valid`, which exist; the request decoder for it is S2.4's and
belongs to B6); B5 after B3, B4 and the **merged** S2.3 build, with G-S0b passed; B6 after the merged S2.4
build; B7 and B8 after B6, then B10; B9 behind S2.0 and S2's signed widening gate, never on this plan's
clock; B11 deferred until lean-first batch 16a. Nothing S2-dependent is accepted against an interim
interface (D19).

| # | Batch | Hours | Owner | Needs |
|---|---|---:|---|---|
| B0 | **Statement spec** `docs/spec/senses.md`: sections 2 to 4 of this plan written out as a spec in the form of the S2 spec (decisions, definitions, English, diagnostics, Lean signatures and statements, fixtures, limits, checklist), with section 12's fix table carried over; two uncommitted stubs (D19): `lean/SpecStubs_senses.lean` elaborating every signature of 4.2 and the S1-dependent statements of 4.3 as `Prop` definitions against the S1 build, and `lean/SpecStubs_senses_s2.lean` elaborating the five S2-dependent statements against named interim interfaces (shape check only; the names listed as interim in the B0 report); `preambleGrammar` of the fixture pack run through `parse` on the preamble fixtures (a1 to a8) with `#guard`; the statement review (Astra and Fable, converged) | 4 | planner | S1 build |
| B1 | **Dictionary.** `Dictionary.lean`: the structures, `reservedWords`, `glossed`, `commaForms`, `selectedWording`, the negatives, `failures`, `wf`, `wf_iff_no_failure` proved, `glossed_negative` proved; `PackSort` and `headwordTokens`; `Examples.lean` with d1 to d19 as `#guard`; audit, inventory, layer, `lean_statements.py` | 4 | Lean | B0 |
| B2 | **Packs as files.** The pack schema (2.2) in `docs/spec/senses.md`; `ve/senses/packs/fixtures@1.json` (section 6's pack) and the loader `ve/senses/__init__.py` (read bytes, canonical JSON, nothing else); `ve/senses/reviewed-packs.json` with the fixture pack unpinned; `Decode.lean`: the pack decoder (null rejected, unknown fields rejected, as the frozen decoders do) and `dictionaryId`; fixtures p1 to p6 | 3 | Python files + Lean decoder | B1 |
| B3 | **Projection.** `Project.lean`: `usedWords` (by headword tokens, D18), `Projection`, `project` over the request's own lexicon `L` (appending the pack nouns and letters and the sense forms, the letter check), `envJson` (canonical insertion into the validated environment JSON; its `environment_id` through the existing Lean identity), `project_valid` proved with the `L.valid E {} = true` premise (or deferred as 4.4 says, with the DRI's signature in the batch report), `project_extends` stated against the interim `Extends`; fixtures j1 to j12 | 5 | Lean | B1, B2 (the base lexicon is S1's `Lexicon`) |
| B4 | **Preamble.** `Assignment.lean`, `Preamble.lean`: `preambleShaped`, `preambleGrammar` (one rule per sense, kw and content terminals, the comma glued before, `Grammar.wf` and `terminatorFree` true by construction and checked by `#guard` on the fixture pack), `readPreamble` through S1's `verdict` with the lookup faults and `preambleBudget`, `lines`, `preamble_unique` and `lines_read` proved (or as 4.4); fixtures a1 to a12 | 4 | Lean | B1 |
| B5 | **Reader.** `Read.lean`: `readWithSenses`, the units, candidates with typed admission (`candidateCap`, `lines`), the successor-state check (`candidatesDiverge` with its `Divergence`), `senseMap` from the derivations keyed by written occurrence, `mixedOf`, unused defaults, `flipModel` through the existing evaluator; `senses_resolved_one_reading`, `senses_candidate_sound`, `candidates_complete`, `mixed_exact`, `senseMap_ids` proved against the merged S2.3; R1 to S2.3; fixtures s1 to s18, n1 to n7, c1 to c8 (verdict obligations that decide the comma forms, Q4), m1 to m4; as amended by the spec: its fixtures of 8.5 and 8.7 (c1 to c17, s1 to s23), `senses_unit_sound`, the switch rule, `quotedSense` | 6 | Lean | B3, B4, S2.3 merged, G-S0b, the DRI's decision on R3, and Q4 decided by its rule on the column that ships |
| B6 | **Service and relay.** Modes in `ve_english_route` (`EnglishMain.lean`): `senses.read`, request (environment, its proposed lexicon as `english.read` receives it, packs' bytes, own senses, source, mode, cap), response (status, S2's six identities of the projection, `dictionary_id`, `senses_version`, units with candidates, each candidate with its resolving lines and the identities of its own projection, flip models, the sense map with byte spans from `lexSpans`, mixed, unused, the preamble lines, the projected environment JSON, code and text); `senses.project`, request (environment, its lexicon, packs, own senses, preamble lines, used words), response (the projected environment JSON and its identities), which is what the CLI's `ve senses project` and the candidate display call; null fields omitted; `ve/senses/LOCK.json` with `sensesVersion` and the hook rule (D17); `ve/assurance-manifest.json`: operations `senses.read` and `senses.project`, `authority: lean`, `target: lean`, no `python` entry, the decoders pinned; `ve/backends/senses.py`: the relay (`decide`, Lean's code and text verbatim, `CheckerUnavailable` only for operational faults); CLI `ve check --surface english --senses PACK …` and `ve senses project|check`; fixtures i1 to i7 | 3 | Lean service + Python relay | B5, S2.4 merged |
| B7 | **Display.** `ve render --view ve_english --senses …`: Lean's preamble lines, then Python's renderer over the projected environment, then `checkRendering` through the service on the result (a mismatch is `CheckerUnavailable`: the renderer is an untrusted producer, lean-first 2.3); `--glossary`; `--json` with the sense map for hover; the mixed, unneeded, unresolved and diverging texts printed verbatim; each candidate rendered under the projection `senses.project` returns for its resolving lines and re-read by `checkRendering` under it, shown with the lines the document lacks; `ve senses resolve FILE --word W --gloss G` (inserts the preamble line, re-checks); `ve senses propose-readings FILE` writes the W2 reading set of each unresolved unit with two or more candidates from Lean's candidates and flip models (`status: open`, `admission.who: "senses"`, `why` the Lean text, `distinguishing_models` the flip models by id, each reading's text rendered under its candidate's projection) and runs the existing readings validation on the file; a one-candidate unit gets no set and a line saying which line resolves it; the web-app JSON contract documented in `docs/spec/senses.md` (the web app itself is on its own branch, Z4) ; fixtures g1 to g9 | 4 | Python | B6 |
| B8 | **Starter packs.** Four packs seeded from the reviewed overlays and the pilots' vocabularies (D14): `policies@1` (agent-policy and cedar-attributes: principals, resources, `access`, `allowed`, `denied`, `owns` …), `rights@1` (the UDHR pilot's holders, duties, `entitled`, `protected`, `free` …), `software-services@1` (fluent, assist and the readability eval: `deployed`, `reviewed`, `safe`, `owns`, `depends on` …), `risk@1` (the risk use case: `severe`, `avoidable`, `leads to` …); `tools/senses_propose.py` drafts entries from an environment, its overlay and OEWN glosses for review (untrusted, Python); each pack reviewed and pinned; **measurement** (7.2): every English sentence of the four use cases and the fluent examples re-read with the pack in place of its overlay, counting sentences that read with the same formula up to the renaming of predicate names to sense ids, sentences that need a preamble line, sentences that need a switch, and sentences that no longer read, with the reasons | 6 | data + review + measurement | B6 |
| B9 | **The "No X that …" row.** `natural-no.guard`: `natural_no → no ⟨declaration⟩ ⟨relative_pronoun⟩ ⟨guard⟩ ⟨relative⟩`, action `noGuard`: `not (ex s (and G R))`, with `blockedWording "natural-negation"` when `R` is a negation as `everySubject` does (S2 2.7), as a row with `"status": "proposed"` in `ve/english_grammar/relational-fol@0.json`; fixtures w8 to w10 (section 6.7) under the fixture grammar with the row and without; the decision to accept it is the signed widening of S2 D11 and is not taken here | 3 | Lean + JSON row | S2.0 |
| B10 | **Report.** `docs/spec/senses-report.md`: every fixture's result, the proved and deferred statements, the measurements of section 7, the before and after of the joke, latency, and what was deleted | 2 | planner | B7, B8, B9 |
| B11 | **`ve-document@1`** (later): the `senses` front matter (2.4) read by the Lean `document` mode; the defaults as exact indices; the preamble lines rendered from them by `Assignment.lines` and prepended to the source before `readWithSenses`, so the reader keeps its one channel (D5) | 4 | Lean + Python | lean-first batch 16a |

### 5.1 Per batch: fixtures, deletions, done when

**B0.** Fixtures: the S1 stub elaborates; the interim S2 stub elaborates (a shape check, D19); a1 to a8
computed; every counterexample fixture of draft 2 is present with its expected value (d1's note, d17, d18,
d19, a11, a12, j11, j12, n3, n7, s15, s16, s17, s18). Deletes nothing. Done when the review converges with its
FIX list applied and both stubs re-elaborate. Status 2026-10-05: the review converged on FIX, applied in spec
draft 2; G-S0 (7.1) is the remaining condition.

**B1.** Fixtures d1 to d19. Not duplicated: `reservedWords` is the one list (D13); `wordingKey`,
`negativeTemplate`, `shapeOk` are S1's, called, not copied. Done when every d fixture holds (d1 and d17
together pin W6 over coexisting forms) and the audit is clean.

**B2.** Fixtures p1 to p6. Python reads bytes and computes nothing: no schema check in Python (Lean's
decoder decides, and its text is relayed). Not duplicated: no Python `wf`. Done when a malformed pack's Lean
text reaches the CLI unchanged and a valid pack's `dictionary_id` is stable across whitespace changes.

**B3.** Fixtures j1 to j12. Not duplicated: no selection rule of the S2 adapter is copied; the document's
own lexicon arrives validated from S2's producer in the request, pack sorts declare their letters (W4), and
`project` appends what the dictionary determines (Q7 closed, R2 withdrawn). Done when j1's projection passes
`Lexicon.valid` over `LJ`, j6's collision is reported with the sense and the symbol, j11 finds `tells`
through `tell`, j12 reports the letter collision, and `project_valid` is proved or its deferral signed.

**B4.** Fixtures a1 to a12. Not duplicated: the preamble is parsed by the S1 engine, not by a hand parser;
`preambleShaped` reads tokens only and names no sense. Done when a1 to a12 hold (a11 shows the budget
premise, a12 the malformed line) and `preamble_unique` is proved or its deferral signed.

**B5.** Fixtures s1 to s18, n1 to n7, c1 to c8, m1 to m4. Not duplicated: the body reader is S2's, called;
the candidates reuse `readSentence` and `typedDocument`; the flip-model evaluation is the existing evaluator.
Done when s1 (the joke) gives the formulas of 6.6, s2 gives its candidates and flip models, s16 keeps one
typed candidate without choosing it, s17 reaches `candidatesDiverge` with the referent named, n7 is
unresolved and not `noDerivation`, the five reading theorems are proved against the merged S2.3, and Q4 is
decided by its rule (10) on the spec's c fixtures in the column that ships. B5 does not start before the
DRI's decision on R3 (spec 6.2).

**B6.** Fixtures i1 to i7. Deleted: nothing yet. Not duplicated: no Python decision site in
`ve/backends/senses.py` (a grep test until lean-first batch 0's `tools/relay_lint.py` exists, then that);
no Python text of its own; the request's lexicon is built by the `english.read` adapter's existing export,
not a second one. Done when `ve check --senses fixtures@1 joke.txt` prints Lean's result, `senses.project`
returns a candidate's projection with the identities the `senses.read` response lists for it (i7), and the
manifest test passes with the two new operations.

**B7.** Fixtures g1 to g9. Not duplicated: Python's renderer produces text that Lean re-reads; every
candidate is rendered and re-read under the projection Lean computed for its choice, never under the base
projection; the glossary and hover are formatted from the sense map; the reading set is written from Lean's
candidates and models and validated by the existing route; `suggest_vocabulary` and `ve propose` are not
extended (listed for E2's retirement once B8's measurement shows the packs cover their adjective and verb
lists). Done when the joke renders with its preamble and one inline gloss, re-reads to the same formulas, the
unresolved joke yields a reading-set file the readings route accepts whose readings re-read under their own
projections (g4), and a one-candidate unit yields no set and the resolving line (g9).

**B8.** Fixtures: the four packs pass `wf`; the measurement table of 7.2 is produced by
`conformance/senses_usecases.py`. Not duplicated: `tools/senses_propose.py` proposes and never decides.
Done when each pack is pinned with a reviewer and date and the table is in the report.

**B9.** Fixtures w8 to w10. Not duplicated: the row lives in S2's JSON source and its action in S2's
library; nothing is added to Python (`english.py`'s natural parser is the comparator E2 retires). Done when
the row is generated into no table (`--check` passes with the row proposed) and the three verdicts are
measured.

**B10.** Done when the report states every number with how it was measured.

## 6. Fixtures

Every expected value is hand-derived and an obligation. `F` is the fixture pack of 2.2 extended with the
sorts `principal` and `resource` (nouns `principal`, `resource`; letters `r`, `q`). `EJ` (the joke
environment) declares the sorts `joke` and `person` (nouns `joke`, `person`), no predicate, the constants
`alice` (person, display `alice`) and `riddle` (joke, display `the riddle`), and profiles
`["relational-fol@0"]`; `LJ` is its own lexicon as S2's producer exports it (nouns `joke`, `person`; letters
`j`, `p`, which agree with `F`'s for the merged sorts; spellings `alice`, `the riddle`). `F2` is `F` with a
second sense of `tells` (gloss `reveals`, description `gives away the answer of the joke`, kinds `[person,
joke]`, wording `{0} tells {1}`). `Fn` is `F` plus the word `near` with two senses: 1, gloss `beside bob`,
description `is beside bob in particular`, kinds `[person]`, wording `{0} is near bob`; 2, gloss `beside`,
description `is beside someone`, kinds `[person, person]`, wording `{0} is near {1}`. `EJn` is `EJ` plus the
constant `bob` (person, display `bob`), `LJn` its lexicon. `ES` declares the sort `service` (noun `service`,
letter `s`) and the constants `legacy`, `beta`, `gamma` (displays `legacy`, `beta`, `gamma`), `LS` its
lexicon. `var 0` is the innermost binder.

### 6.1 Dictionary (d)

| Id | Case | Expected |
|---|---|---|
| d1 | `F` | `wf` true; `failures = []`, although `funny` senses 1 and 2 share the bare wording `{0} is funny`: W6 compares coexisting forms only (D12) |
| d2 | `F` with `funny` sense 2's gloss `amusing` | `[("W2", "funny", "gloss amusing repeated")]` |
| d3 | `F` with `odd` sense 1's gloss `odd` | W2 (gloss equals the word) |
| d4 | `F` with `funny` sense 2's gloss `deployed` | W2 (gloss is a word of the dictionary) |
| d5 | `F` with `funny` sense 1's wording `{0} is amusing` | W3 (the word does not occur) |
| d6 | `F` with `tells` wording `{1} tells {0}` | W3 (does not begin with `{0}`) |
| d7 | `F` with `funny` sense 1's kinds `["thing"]` | W4 (`thing` is no sort) |
| d8 | `F` with `funny` sense 1 given `negative: "{0} is not funny"` | W5 (the automatic negative exists) |
| d9 | `F` with `access` without its negative | `wf` true: a sense without any negative is allowed (`Alice may not access …` then has no reading, n6) |
| d10 | `F` with `access` negative `{0} cannot access {1}` | `wf` true (W5 allows a declared negative there) |
| d11 | `F` plus a word `strange` with wording `{0} is funny strange`, and `funny` sense 1's wording changed to `{0} is funny strange` | W6 (two senses of different words select one key) |
| d12 | `F` plus a second pack that also has `funny` | W1 (a word in two packs) |
| d13 | `F` with an own sense for `funny` in the document | W1 (own sense of a pack word) |
| d14 | `F` with `funny` sense 1's wording `{0} is funny (meaning amusing)` | W3 (contains `(`) |
| d15 | `F` with a sense whose word is `every` | W1 (reserved) |
| d16 | `F` with `funny` indices 1 and 3 | W1 (indices not `1..n`) |
| d17 | `F` plus a word `strange` with wording `{0} is funny strange`, and `funny` sense 2's wording changed to `{0} is funny strange` | W6 (different words: every form compared; the bare forms coincide and so do the automatic negatives `{0} is not funny strange`). With d1 and d11 this pins the amended W6: equal bare forms pass within one word and fail across words whichever sense carries them |
| d18 | `Fn` (`near` unary over `person` with the literal `bob`, and binary) | `wf` true: W1 to W7 forbid neither the arity difference nor the literal word; the dictionary cannot exclude the divergence of s17 |
| d19 | `F` with `joke`'s letter changed to `p` | W4 (two pack sorts with one letter) |

### 6.2 Packs and identities (p)

| Id | Case | Expected |
|---|---|---|
| p1 | `fixtures@1.json` reformatted (whitespace, key order) | the same `dictionary_id` |
| p2 | one gloss changed | a different `dictionary_id` |
| p3 | a pack with `null` for a description | the decoder rejects it; the Lean text reaches the CLI |
| p4 | a pack with an unknown field | rejected, likewise |
| p5 | the fixture pack unpinned | `review_status: unreviewed` displayed; nothing rejects |
| p6 | the fixture pack pinned with a wrong digest | `unreviewed` |

### 6.3 Preamble (a)

| Id | Source (first sentences) | Expected |
|---|---|---|
| a1 | `In this document, funny means amusing.` | `(A = [(funny, 1)], k = 1)`; one derivation |
| a2 | `In this document, funny means amusing. In this document, reviewed means rated.` | `([(funny, 1), (reviewed, 2)], 2)` |
| a3 | `In this document, funny means amusing. In this document, funny means strange.` | `repeatedDefault 1 funny` |
| a4 | `In this document, purple means amusing.` | `unknownWord 0 purple` |
| a5 | `In this document, funny means purple.` | `unknownGloss 0 funny purple`; text lists `amusing; strange` |
| a6 | `In this document, tells means says aloud.` | `([(tells, 1)], 1)`; `unneeded` lists `tells` |
| a7 | `in this document , funny means amusing.` | not a preamble line (the comma is not glued): `k = 0`; the sentence then has no derivation in the body: `stopped 0 noDerivation` |
| a8 | `The riddle is funny. In this document, funny means amusing.` | `preambleLate 1` |
| a9 | `In this document, Funny means Amusing.` | as a1 (content terminals fold case) |
| a10 | `A.lines` of a2's assignment, lexed and read | a2's assignment (`lines_read`) |
| a11 | a10 at `b = 0` | `preambleBudget 0`: `verdict` is `none` for the first line; `lines_read` needs its sufficient-budget premise |
| a12 | `In this document, funny is amusing.` | `malformedPreamble 0` (shaped, no `means`); not a body sentence |

### 6.4 Projection (j) and the gloss forms (c)

| Id | Case | Expected |
|---|---|---|
| j1 | `F`, `EJ`, `LJ`, `A = [(funny, 1)]`, `used = [funny, tells]` | `env.predicates` names `sense__funny_1` (wording `{0} is funny`, negative `{0} is not funny`), `sense__funny_2` (wording `{0} is funny (meaning strange)`, negative `{0} is not funny (meaning strange)`), `sense__tells_1` (`{0} tells {1}`, `{0} does not tell {1}`); `forms.aliases` has the comma forms of each wording (`false`) and of each negative (`true`) and the glossed wording and negative of `sense__funny_1`; `lexicon` keeps `LJ`'s entries and adds the nouns and letters of `service`, `number`, `principal`, `resource`; `lexicon.valid` true |
| j2 | j1 with `A = []` | `sense__funny_1` and `sense__funny_2` both glossed; no bare `funny` rule; valid |
| j3 | j1 with `used = [tells]` | only `sense__tells_1`; valid; j1 extends j3 (`project_extends`, q1) |
| j4 | j1 with `used = [funny, tells, access]` | `sense__access_1` with wording `{0} may access {1}` and `forms.negatives` `(sense__access_1, {0} may not access {1})`; valid |
| j5 | j4 with `A = [(funny, 1), (access, 1)]` | the same as j4 (one sense: the line is unneeded, not wrong) |
| j6 | `EJ` plus an own predicate `funny` over `joke` with wording `{0} is funny`, `A = [(funny, 1)]` | `collision predicate funny sense__funny_1` |
| j7 | `EJ` plus an own predicate `peculiar` over `joke` with wording `{0} is strange` (a gloss as a wording) | valid: a gloss is not a form; `The riddle is funny (meaning strange).` still reads as `sense__funny_2` (the glossed form is one wording, not a clause of `peculiar`) |
| j8 | the projected environment JSON of j1 | loads with today's Python `Environment`; its `environment_id` equals Lean's; a document using it without packs reads `The riddle is funny (meaning strange).` to the same formula under S2 alone (D8's last claim) |
| j9 | j1's `envJson` with the packs' sorts | `sorts` includes `joke`, `service`, `person`, `number`, `principal`, `resource` with their nouns |
| j10 | `project` on `used` containing a word of no sense (`is`) | the word is ignored (`usedWords` filters by the dictionary); valid |
| j11 | `usedWords F` on the body `Alice does not tell the riddle.` | `[tells]`: `tell` is a headword token of `tells` (the automatic negative, D18); the projection then has `sense__tells_1` and n3 reads |
| j12 | `LJ` with the letter of `person` changed to `s` | `collision letter s service`: a pack-only sort's letter equals a letter of the document's lexicon |

Gloss-form verdicts (under the projection of j1; obligations that decide Q4):

| Id | Source | Verdict |
|---|---|---|
| c1 | `The riddle is funny (meaning strange).` | one |
| c2 | `The riddle is funny, in the sense of strange.` | one |
| c3 | `Every joke that is funny, in the sense of strange, is not funny.` | one |
| c4 | `Every joke that is funny, in the sense of strange, and is odd (meaning strange) is not funny.` | one (`guard.two` with the mid-sentence form) |
| c5 | `Every joke that is funny, in the sense of strange, and is odd (meaning strange) and is funny is not funny.` | one (`guard.three-right` with the final form, then `, and`); if `many`, the comma forms are dropped |
| c6 | `Every joke that is funny, in the sense of strange, and is odd (meaning strange), and is funny is not funny.` | one (`guard.three-left` with the mid-sentence form) |
| c7 | `The riddle is funny ( meaning strange ).` | zero (spacing not glued) |
| c8 | `The riddle is funny (meaning amusing).` under `A = [(funny, 1)]` | one; `sense__funny_1` (the default's glossed alias) |

### 6.5 Extension (q)

| Id | Case | Expected |
|---|---|---|
| q1 | j3 and j1 | `Extends` holds; a rule map exists (`grammar_extension`) |
| q2 | j1 and j1 with `A = [(funny, 2)]` | `Extends` fails (`lexiconSub`: `sense__funny_1`'s wording changed); a changed default is a new document |
| q3 | j1 and j6 | `Extends` is not stated (j6 is a fault) |

### 6.6 The joke, end to end (s), negatives (n), mixed (m)

The joke document `J`:

```text
In this document, funny means amusing.
Every joke that is funny (meaning strange) is not funny.
Alice tells the riddle.
The riddle is funny (meaning strange).
Therefore the riddle is not funny.
```

| Id | Case | Expected |
|---|---|---|
| s1 | `J` under `F`, `EJ` | `ok`; `k = 1`; units: `all joke (implies (pred sense__funny_2 [var 0]) (not (pred sense__funny_1 [var 0])))`; `pred sense__tells_1 [const alice, const riddle]`; `pred sense__funny_2 [const riddle]`; `not (pred sense__funny_1 [const riddle])` with mark true; mixed `[(funny, [sense__funny_1, sense__funny_2])]`; unused `[]`; sense map (sentences counted from the preamble line, 2.6): sentence 1 spans `funny (meaning strange)` → `sense__funny_2` not default, `funny` → `sense__funny_1` default; sentence 2 `tells`; sentence 3 `funny (meaning strange)`; sentence 4 `funny` default |
| s2 | `J` without its first line | unit 0 unresolved, `unresolved = [funny]`, two candidates: choice `[(funny, 1)]` giving s1's formula, choice `[(funny, 2)]` giving `all joke (implies (pred sense__funny_2 [var 0]) (not (pred sense__funny_2 [var 0])))`; unit 2 resolved (the gloss decides); unit 3 unresolved with two candidates `not (pred sense__funny_1 [const riddle])`, `not (pred sense__funny_2 [const riddle])`, mark true; flip model of unit 0's pair: domain one joke, `sense__funny_2` true, `sense__funny_1` false: candidate 1 true, candidate 2 false; mixed `[]` (candidates excluded) |
| s3 | `Legacy is funny.` with a constant `legacy` of sort `service` | `illTyped` (kinds) |
| s4 | `J` with `In this document, funny means purple.` first | `fault (unknownGloss 0 funny purple)` |
| s5 | `J` with its first line moved after sentence 2 | `fault (preambleLate 2)` |
| s6 | `J` under `EJ` plus own predicate `funny` | `fault (collision …)` |
| s7 | `Alice tells the riddle.` alone | `ok`, one unit, resolved: one sense needs no line |
| s8 | `The riddle is funny (meaning amusing).` under `A = [(funny, 1)]` | `pred sense__funny_1 [const riddle]`; rendering drops the gloss; `checkRendering` of `The riddle is funny.` true |
| s9 | `Every funny joke is odd.` under `A = [(funny, 1), (odd, 1)]` | `all joke (implies (pred sense__funny_1 [var 0]) (pred sense__odd_1 [var 0]))` (S2's natural subject over the default's bare adjective) |
| s10 | `Every funny (meaning strange) joke is odd.` | zero: the glossed form is no adjective (limit L3); the text `none` with the suggestion to write `Every joke that is funny (meaning strange) is odd.` (fixture g5 for the text) |
| s11 | a sentence with three unresolved words of three senses each (a fixture pack `F3`) | `fault (tooManyCandidates i [w1, w2, w3])` (27 choices > 8) |
| s12 | a sentence with two unresolved words of two senses each | four candidates; `candidates_complete` holds |
| s13 | `J` with `In this document, funny means amusing. In this document, odd means strange.` | `ok`; unused `[odd]` |
| s14 | `J`'s source bytes with a byte-order mark | S2's lexer decides (`badCharacter`): `lexical` |
| s15 | `Legacy, beta and gamma are deployed.` under `F`, `ES`, `LS` | `ok`, resolved (`deployed` has one sense): S2's subject coordination, three `pred sense__deployed_1` nodes (`const legacy`, `const beta`, `const gamma`) in S2's conjunction shape; the sense map has **one** entry for the span `deployed`; `senseMap_ids` holds as sets (the one id on both sides) while the counts differ (1 written, 3 in the formula) |
| s16 | `The riddle is odd.` under `F`, `EJ`, `LJ`, no preamble | unit 0 unresolved, `unresolved = [odd]`; the choice `[(odd, 2)]` reads but `pred sense__odd_2 [const riddle]` is ill-typed (`number` against `joke`) and is dropped; one candidate, `[(odd, 1)]`, `pred sense__odd_1 [const riddle]`, lines `In this document, odd means strange.`; the unit is **not** resolved (nothing is guessed, D15); the one-candidate text of 2.8; no flip model (no pair) |
| s17 | `Alice is near bob.` under `Fn`, `EJn`, `LJn`, no preamble | both choices read and type: `[(near, 1)]` gives `pred sense__near_1 [const alice]` with successor referents `[alice]`, `[(near, 2)]` gives `pred sense__near_2 [const alice, const bob]` with `[alice, bob]`; `fault (candidatesDiverge 0 [near] (referent bob))`; the referent text of 3.2 names `bob`, `beside bob` and `beside`. Under `F` alone the sentence is `stopped 0 noDerivation` |
| s18 | s17 with `In this document, near means beside.` first | `ok`; `pred sense__near_2 [const alice, const bob]`; `k = 1` |
| n1 | `The riddle is not funny.` under `A = [(funny, 1)]` | `not (pred sense__funny_1 [const riddle])` |
| n2 | `The riddle is not funny (meaning strange).` | `not (pred sense__funny_2 [const riddle])` |
| n3 | `Alice does not tell the riddle.` | `not (pred sense__tells_1 [const alice, const riddle])`: `tells` is used through its headword token `tell` (j11, D18) |
| n4 | `Every joke that is not funny is odd (meaning strange).` under `A = [(funny, 1)]` | `all joke (implies (not (pred sense__funny_1 [var 0])) (pred sense__odd_1 [var 0]))` |
| n5 | `Alice may not access the api.` under `F` with constants over `principal`, `resource` | `not (pred sense__access_1 [const alice, const api])` (the declared negative, profile-fixed) |
| n6 | n5 under d9's pack | zero (no negative form; the text `none`) |
| n7 | `Alice does not tell the riddle.` under `F2`, `EJ`, `LJ`, no preamble | unit 0 unresolved, `unresolved = [tells]` (found through `tell`), two candidates `not (pred sense__tells_1 [const alice, const riddle])` and `not (pred sense__tells_2 [const alice, const riddle])`, equal successor states; **not** `stopped 0 noDerivation`, which headword-only discovery would give |
| m1 | s1 | mixed names `funny` with both senses |
| m2 | `J` with sentence 4 written `Therefore the riddle is not funny (meaning strange).` | mixed still names `funny` (sentence 1 uses both) |
| m3 | a document using `funny` only bare under a default | mixed `[]` |
| m4 | a document using `funny` only glossed as `strange`, no default | mixed `[]`; nothing unresolved |

### 6.7 The "No X that …" row (w)

Under S2's fixture grammar `GF` extended with the projection of j1 and with the proposed row (`GFn`), and
without it (`GF`):

| Id | Source | `GF` | `GFn` |
|---|---|---|---|
| w8 | `No joke that is funny (meaning strange) is funny.` | zero (S2 b29's shape) | one: `not (ex joke (and (pred sense__funny_2 [var 0]) (pred sense__funny_1 [var 0])))` |
| w9 | `No joke that is funny (meaning strange) is not funny.` | zero | one derivation; meaning `blockedWording "natural-negation"` (as S2 b44) |
| w10 | S2's b1 to b55 | unchanged | unchanged (no fixture changes verdict) |

### 6.8 Service, relay and display (i, g)

| Id | Case | Expected |
|---|---|---|
| i1 | `senses.read` on `J` | the response of B6 with S2's six identities of the projection, `dictionary_id` and `senses_version`; `environment_id` equals Python's over the returned environment JSON |
| i2 | the same request twice | byte-identical responses |
| i3 | a request without `packs` and without own senses | the mode refuses: `InvalidInput` (use `english.read`) |
| i4 | a pack whose bytes differ from the pinned digest | `review_status: unreviewed`; the reading is unchanged |
| i5 | the service killed mid-request | `CheckerUnavailable` from the relay, once retried |
| i6 | the manifest | `senses.read` and `senses.project` have `authority: lean`, no `python` entry; the manifest test that every JSON-reading Lean file is classified passes |
| i7 | `senses.project` with `J`'s packs, environment and lexicon and the resolving lines of s2's second candidate (`In this document, funny means strange.`) | the projected environment JSON of that choice (`sense__funny_2` bare, `sense__funny_1` glossed) and its identities, equal to the identities the `senses.read` response of s2 lists for that candidate |
| g1 | `ve render … J` | the preamble line, then the body with one gloss (sentence 1 and 3's `funny (meaning strange)`), none on the defaults; `checkRendering` true |
| g2 | `--glossary` | the block of 2.8 with `funny: amusing (the default)` and `funny (meaning strange): odd, hard to explain`, and `tells: says aloud` |
| g3 | `--json` | the sense map with byte spans that cut the source at the token boundaries of `lexSpans` |
| g4 | s2 through the CLI | the unresolved text of 2.8 with both candidates rendered as English, each under the projection `senses.project` returns for its resolving lines and re-read by `checkRendering` under it (the first renders `Every joke that is funny (meaning strange) is not funny.`, the second `Every joke that is funny is not funny.` under `funny means strange`), each shown with its resolving line, and the suggested line |
| g5 | s10 through the CLI | S2's `none` text and the suggestion |
| g6 | `ve senses resolve J2 --word funny --gloss amusing` on s2's source | the file gains the first line; the re-check is s1 |
| g7 | `ve senses propose-readings` on s2's source | a reading-set file with two `open` sets, two readings each, flip models by id; the readings route accepts it; the document's conclusion check reports SOME or UNKNOWN as the route decides (not claimed here) |
| g8 | the mixed warning on s1 | printed once, Lean's text, exit code unchanged |
| g9 | s16 through the CLI | the one-candidate text of 2.8; `ve senses propose-readings` writes no set for that unit (a set needs two readings) and prints the resolving line; `ve senses resolve --word odd --gloss strange` inserts the line and the re-check resolves the unit |
| g10 | s17 through the CLI | the `CandidatesDiverge` referent text, verbatim; no reading set; `ve senses resolve --word near --gloss beside` gives s18 |

## 7. Gates and measured claims

### 7.1 Gates

| Gate | After | Passes when |
|---|---|---|
| G-S0 | B0 | the statement review converges on FIX or PASS with its list applied; the S1 stub elaborates the dictionary, assignment, preamble and projection statements; the interim S2 stub elaborates the five reading statements (a shape check, D19, with its interim names listed); a1 to a8 computed; every counterexample fixture of draft 2 is present with its expected value: d1's note, d17, d18, d19, a11, a12, j11, j12, n3, n7, s15, s16, s17, s18. **As amended (spec 7):** the review converged on FIX; G-S0 passes after one bounded re-review by both reviewers of the spec's diff from draft 1, the three changed statements re-elaborated against the merged S2 build, and the recomputed rows (d2, d26, j13's text, j15, j16, c16, c17, s22, s23, the whole R3 column under the narrowed simulation, every hand-derived row); no second full review. B1 to B4 start when G-S0 passes |
| G-S0b | before B5 is accepted | the five S2-dependent statements (`project_extends`, `senses_resolved_one_reading`, `senses_candidate_sound`, `candidates_complete`, `senseMap_ids`) re-elaborate against the **merged** S2.3 build, unchanged, or with every difference listed, re-reviewed by the statement reviewers and signed by the DRI; no S2-dependent proof counts before this gate |
| G-S1 | B5 | every fixture of 6.1 to 6.6 holds, s15 to s18 and n7 included; `lean/audit.py` clean, standard axioms only; the theorems of 4.3 proved, or each deferral signed by the DRI and listed in the report; Q4 decided by its rule (10) on the spec's c fixtures in the column that ships, after the DRI's decision on R3 |
| G-S2 | B7, B8, B9 | the joke reads, renders and re-reads (g1); the four packs pinned; the measurement of 7.2 in the report; no Python decision site in the relay or the display (lint); latency: `senses.read` on `J` and on each use-case document within S2's `english.read` budget plus 10 ms for the preamble and projection, warm, measured as S1 measured (`bench/english_lean_g1a.py`'s method) |

### 7.2 Measured claims (obligations of the report)

| Claim | How measured |
|---|---|
| Declaration lines per word, before and after | on `J`: today's environment JSON for the same vocabulary (lines per predicate: name, arguments, description, verbalisation, negative) against the senses form (preamble lines per multi-sense word used bare, 0 for others); on each use case: the overlay and environment lines its predicates need against the pack lines |
| Hand-written negatives removed | count of `negative_verbalisation` entries in the use cases' overlays whose wording is a simple adjective (`{0} is w`): all become automatic; the count is reported |
| Pack coverage of the use cases | B8's table: per use case, sentences that read with the same formula up to renaming, that need a line, that need a switch, that do not read, with reasons |
| One reading | the theorems of 4.3 in the audit inventory; G-S1 |
| Latency | 7.1, G-S2 |
| The "No X that …" gap | w8 to w10: measured under the proposed row; not accepted |

Nothing is claimed about readability, intent or human comprehension (limit L1).

## 8. What is deleted or not duplicated

| Item | Disposition |
|---|---|
| hand-written `negative_verbalisation` for simple adjectives | unnecessary for sense predicates (automatic, D3); the environment field stays for own predicates until E2 |
| `ve/english.py` `_RESERVED` (`:47`) | duplicate of `reservedWords`; deleted in E2 with the Python producer (lean-first 2.3) |
| `ve/english_vocabulary.py` `negative_template`, `ve/printer.py` `_negative_template` | not called for sense predicates; E2 deletes them (S1 ported them) |
| `ve/english.py` `EnglishVocabulary`, the lint, `suggest_vocabulary` | not extended; no sense logic enters them; `suggest_vocabulary`'s finite adjective and verb lists are listed for retirement in E2 once B8's table shows the packs cover their cases |
| `ve/lexicon` (OEWN) | advisory for `ve propose` and `tools/senses_propose.py` only; never read at check time (unchanged) |
| Python sense resolution, preamble parsing, projection, mixed check, candidate construction | never written (D1 of section 0) |
| Python texts for the new outcomes | none; Lean's are relayed (lean-first rule 2) |
| the S2 adapter's noun, letter and spelling selection | **not copied** into `project`: the document's own lexicon arrives in the request from S2's one producer, validated by Lean; pack sorts declare their letters (W4); `project` appends (Q7 closed, R2 withdrawn) |
| S2's reader checks | not re-implemented: R1's split, or calls of S2's exported functions (4.2) |
| the senses lock | its own file `ve/senses/LOCK.json` (D17); nothing is added to `ve/english_grammar/LOCK.json` |
| a second projection for candidate display | none: the display calls `senses.project` for the candidate's resolving lines and renders under what Lean returns |
| the web app's hover | consumes the JSON contract; no second computation |
| S2's files | unchanged, except R1 (a definitional split of `read`, no statement change) if accepted |

## 9. Limits, and what is not claimed

- **L1 Intent and comprehension.** A chosen sense is a declaration. Nothing here says the author meant it,
  or that a pack's description is right. Review of a pack is a pinned record, as for overlays. Zero-training
  English is the target and is unverified: fewer declaration lines and successful parsing (section 7) say
  nothing about whether a novice understands a sense line or a gloss.
- **L2 Per projection.** Every one-reading claim fixes one projection (one dictionary, one assignment, the
  used words). A changed default is a different projection (q2).
- **L3 Glossed forms are clauses.** A switched occurrence has the clause and relative forms only; the natural
  forms (`Every funny joke`, coordination) exist for the default sense (s10).
- **L4 Kinds are sorts.** A word that applies to several sorts needs one sense per sort (Q3).
- **L5 One word, one pack.** Packs cannot share a word; a document cannot redefine a pack word (W1).
- **L6 Candidates are per unit, typed and bounded.** Candidates are computed per unresolved unit, within
  `candidateCap`, and are independent across units **when every candidate of a unit leaves the same
  successor state**; `n` such units give `n` independent open sets and the conclusion check treats them so.
  When the candidates of a unit do not agree on the state, the unit faults (`candidatesDiverge`, reachable,
  s17) and the document stops there, with the differing referent or binder named. Admission is typed: a
  choice that reads but does not type is dropped, so a unit may keep one candidate, which is still not
  chosen for the author (s16). The flip models are proposals checked by the readings route, and a pair they
  do not separate stays open without a set.
- **L7 Formula-level English only.** Statement-layer English (norm act phrases, rights lines) gets senses
  with E3, not here.
- **L8 Documents.** `ve-document@1` waits for the Lean `document` mode (B11).
- **L9 Nothing is run for this draft.** Every verdict, formula and count of section 6 is an obligation.
- **L10 Mixed senses are legal.** The joke relies on it; the warning is advice.

## 10. Open questions and requests

| # | Question | Recommendation |
|---|---|---|
| Q1 | `senses.read` with `authority: lean` from the first commit, with no Python implementation and so no shadow | yes: lean-first rule 6; the corpus evidence is section 6 and B8's table |
| Q2 | packs as request data (D1) against generated Lean literals with a lock file, as S2's fixed rules | request data: one owner, no generator, identified by `dictionary_id` and pinned by review, as overlays; `wf` costs one check per request, cached by `dictionary_id` |
| Q3 | kinds as sorts, one sense per sort (L4), against a `thing` kind with subsorting | sorts: VE has no subsorts; measure in B8 how many words need two senses for two sorts before designing more |
| Q4 | keep the two comma forms | the rule decides: **drop the comma forms if any c fixture is `many` in the column that ships** (spec 8.5: as merged, or with R3), and keep the parenthetical form. Draft 2's wording ("keep if every c fixture is `one`") is replaced, since c7 is `zero` by design. With R3, the spec's c16 is `many`, so the comma forms are dropped unless the DRI revises the rule with a fixture showing `one` (spec R9) |
| Q5 | `candidateCap` = 8 | yes; s11 is the fixture; raise only with a measured need |
| Q6 | the preamble as leading sentences (D5), against a separate block or front matter only | leading sentences for plain text, front matter for `ve-document@1`, both read by one Lean function |
| Q7 | S2 to expose the letter rule and display-form selection from Lean, so `project` calls them instead of copying the adapter's rule | **closed in draft 2, no copy and no request:** the document's own lexicon arrives in the request exactly as `english.read` receives it (S2's one producer), Lean validates it, pack sorts declare their letters (W4), and `project` appends only what the dictionary determines (2.5). R2 is withdrawn. If S2.3 later exposes a selection helper, calling it is equally acceptable |
| Q8 | the "No X that …" row's meaning with a negative relative (w9): block, as the natural `every` does, or accept `not (ex s (and G (not R)))` | block in the proposed row; the signed widening decides |
| Q9 | a pack review record per pack (D14) against one record for all | per pack, by `dictionary_id` of the pack alone |
| Q10 | the sense id form `sense__<word>_<n>` | yes: the `risk__` convention for generated symbols; within `MAX_IDENTIFIER_BYTES` (W1 bounds the word) |

Requests to S2: **R1** (4.2) `read` written as `lex` then `readSentences`, additive; if refused,
`readWithSenses` calls S2's exported functions and duplicates no check. **R2** is withdrawn (Q7).

## 11. Statement review checklist (Astra and Fable, at B0)

1. The projection (2.5) over the request's validated lexicon `L` makes every selection an honest declared
   form, so V1 to V5 hold by W1 to W7 (W6 over coexisting forms, d1 and d17) and the premises of
   `project_valid` (`L.valid`, the letter premise included); nothing in S2 changes and nothing of the S2
   adapter is copied.
2. The preamble grammar has one derivation per line under W2 (`preamble_unique`, with S1's `verdict`
   signature), the shape test of 2.4 separates "preamble ends" from each malformed-line fault (a4, a5, a8,
   a12), `lines_read`'s budget premise is the right one (a11), and the comma and capitalisation rules (a7,
   a9) are the lexer's.
3. The gloss forms (2.3) give every switched occurrence one reading in every position of S2's grammar
   (c1 to c8), and the decision rule of Q4 is right.
4. The unresolved rule (2.4, 2.6) never guesses, admits exactly the typed readings (`candidates_complete`
   with its typing conjunct), sends `.budget`, `.ambiguous` and `.rejected` to `stopped`, keeps a
   one-candidate unit open (s16), and the successor-state equality (both components of `DState`) is the
   right condition for continuing the document, with `candidatesDiverge` reachable (s17) and its texts right.
5. The mixed and unused reports, the sense map keyed by written occurrence and the flip models are defined
   as 2.6 says; `mixed_exact` (word from `P.map`) and `senseMap_ids` (set membership, s15) say what 3.3 says.
6. The texts of 3.2 have one reading each and name only words, glosses and, for divergence, a constant's
   display form.
7. The identities of 2.7 are additive (S2's six, `dictionary_id`, `senses_version` with its own lock) and
   bind what a record needs, a candidate's projection identities included.
8. The ownership table (2.9) and the ledger (8) leave no decision in Python, candidate rendering under
   `senses.project` included.
9. The fixtures of section 6 are the right expectations, s1, s2, s15, s16, s17, n7, c5, j6, j11, w8 and w9
   in particular.
10. Every name passes the audit's rules and collides with nothing in `VE.EnglishGrammar`, `VE.English` or
    `VE.Discourse`.
11. No public message, code, identity, frozen file or theorem statement changes (D10).
12. Discovery by headword tokens (D18) finds every form S2 generates for a sense (clause, relatives,
    negative, aliases) and nothing a sense does not generate.
13. The interim S2 interfaces (4.2) are the S2 spec's signatures and nothing more, every S2-dependent
    statement is marked as elaborated against them, and G-S0b is the gate that validates them.

## 12. Draft 2: the converged edits and the DRI ruling

The plan review (`manage-agents/debates/design-senses/`, Astra and Fable, three rounds, 2026-10-04) did
not converge by the recorder's rule: Fable converged in rounds 2 and 3, Astra held three points. The DRI
ruled the same day: adopt Fable's round-3 joint position plus Astra's three points. Every edit below is in
this draft; none is deferred to B0.

| # | Finding | Edit | Where |
|---|---|---|---|
| 1 | W6 rejected its own fixture: both `funny` senses have `{0} is funny` (Astra r1 1, Fable r2 1) | W6 compares only forms that coexist under one assignment; same-word bare forms may coincide | D12, 2.2, d1, d17, 4.4 |
| 2 | Headword scanning misses `tell` in n3, and negative aliases lost their polarity in 2.5 (Astra r1 2, Fable r2 2) | discovery by headword tokens over generated forms (D18); `forms.aliases` carries `Sense.aliases` with polarity | D18, 2.5, 4.2, j11, n3, n7 |
| 3 | One written adjective becomes several formula occurrences under coordination, so a permutation is false (Astra r1 3, Fable r2 3; shape settled r3) | the sense map is keyed by written occurrence; `senseMap_ids` is set membership both ways; spans and counts tested | 2.6, 3.3, 4.3, 4.4, s15 |
| 4 | Candidate admission underspecified: ill-typed candidates failed the document, `.budget` ignored, no provenance (Astra r1 4, Fable r2 4) | typed admission; `.budget`, `.ambiguous`, `.rejected` are the unit's `stopped`; exhaustive within the cap; `lines` on each candidate; a one-candidate unit stays open | D6, 2.6, 2.8, 4.2, 4.3, L6, s16, g9 |
| 5 | R1/R2 fallbacks duplicated logic; locking senses files in `actions_version` broke D10 (Astra r1 5, Fable r2 5) | R1 fallback "calls", not "repeats"; Q7 closed without a copy (the request's lexicon, pack letters); `senses_version` a separate identity with its own lock | D17, 2.7, 4.2, 8, 10 |
| 6 | Supplied assignment versus preamble had no merge rule; `lines_read` false at `b = 0`; `preamble_unique` ill-typed (Astra r1 6, Fable r2 6) | no assignment argument, the preamble is the one channel, B11 prepends the lines; `lines_read` gets the sufficient-budget premise; `preamble_unique` against `verdict G b w = some (.one t)` | D5, 2.4, 4.2, 4.3, a11 |
| 7 | `readPreamble` lacked a dictionary-independent shape test (Fable r1 2) | `preambleShaped`; lookup faults; `malformedPreamble`, `preambleBudget` | 2.4, 3.2, 4.2, a12 |
| 8 | Q7 was a real duplicate of the adapter's selection rule (Fable r1 3, accepted by Astra r2) | `project D A E L used` over the request's validated lexicon; pack sorts declare letters; `project_valid` gains `L.valid E {} = true` and the letter premise; R2 withdrawn | D1, D8, 2.5, 2.9, 4.2, 4.3, B3, B6, 8, 10, j12, d19 |
| 9 | `mixed_exact` used an undefined `wordOf` (Fable r1 4) | `Projection.wordOf` from `map`; ids are never parsed | 4.2, 4.3 |
| 10 | The comma and glossed aliases read as profile data (Fable r1 5) | stated as fixed by the projection, carried in `forms.aliases` | 0, 2.5, 2.9, 4.2 |
| 11 | s10's suggestion was a new, unlisted text (Fable r1 7) | `GlossedNatural`, a Lean text with the rewrite slot | 3.2 |
| 12 | `candidatesDiverge` is reachable: two senses of one word may differ in arity, S2 computes referents from the formula's constants, `DState` has `binderSeen` (Astra r2, r3; Fable r3 concession; **DRI point 1**) | the run-time equality check kept and owned by Lean, over both state components; `Divergence`; the texts ask the author to choose; `near` as a dictionary fixture (d18) and a reading fixture (s17, s18); L6 as Astra wrote it | D6, 2.2, 2.6, 3.2, 4.2, 9, d18, s17, s18, g10 |
| 13 | Rendering and checking a candidate need the Lean-computed projection of that choice; resolving lines alone are no substitute (Astra r3; **DRI point 2**) | `senses.project` mode; per-candidate projection identities in the response; the display and the reading-set texts render and re-read under it | D6, 2.6, 2.8, 2.9, B6, B7, i7, g4 |
| 14 | B0 cannot elaborate S2-dependent statements against S1; interim stubs are not validation (Astra r2, r3; **DRI point 3**) | two stub files; D19; G-S0b before B5 is accepted; order text | D19, 4.2, 5, B0, 7.1, checklist 13 |
| 15 | Identity count: six S2 identities plus `dictionary_id` and `senses_version` (Astra r3 4) | stated so in 2.7 and i1; the per-candidate identities added | 2.7, i1 |
| 16 | Zero-training English is an unverified usability target (Astra r1, r2; Fable r2, r3) | stated in section 0 and L1; measured claims are counts and parsing | 0, 9 |
| 17 | Batch order must follow the Needs column: B2 after B1, B3 after B2, B5 after the merged S2.3, B9 behind the widening gate, B11 deferred (Astra r1, r2; Fable r2, r3) | the order paragraph and the Needs column | 5 |
| 18 | G-S0 gains every counterexample fixture (Fable r3) | listed in G-S0 and B0 | 7.1, 5.1 |

**Three places where the applier had to choose, for the statement review to confirm or overturn.**

- Fable's round 3 named the `near` fixture "d18, both routes". Here d18 is the dictionary fixture (`wf`
  true) and s17 the reading fixture through the referents route. The second route Fable named (`{0} likes
  every cat` against `{0} likes {1}`, flipping `binderSeen`) is **not** a fixture: S2's base grammar has
  `every` at sentence level only (S2 2.5) and no quantified object term, so under S2 the binary sense gives
  `Alice likes every cat.` no derivation and no divergence would be observed. The check compares
  `binderSeen` all the same, and a fixture is added the day a grammar widening makes the route readable.
- A unit whose only typed choice is one candidate stays unresolved (s16). Typed admission plus D15 (a chosen
  sense is the author's declaration) gives this; the alternative, resolving by typing alone, is a guess the
  author never wrote.
- The `senses.project` service mode is the entry the DRI's point 2 needs. Draft 1 already had `ve senses
  project` in the CLI; naming the mode makes the candidate display's projection a Lean computation and not a
  Python one.
