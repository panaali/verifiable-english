# English in Lean, item 1: the grammar engine and the English reading contract (statement specification)

> Status: statement specification, draft 2 (2026-10-03). This is the item-1 statement spec of
> [english-lean-PLAN.md](english-lean-PLAN.md) draft 2 (the **plan**). It writes out the statements of the plan's
> section 3: the generic grammar engine, whose proofs are stage S1b, and the contract of the English instance,
> which stages S2 to S5 build. It covers formula-level English only. The statement layers (S6), the static tier
> (plan 3.6) and display-only text are not specified here. The plan had its Astra + Fable review
> (`manage-agents/debates/design-english-lean/{fable,astra}.md`, converged after round 3). Draft 1 of this
> specification had its statement review on 2026-10-03
> (`manage-agents/debates/english-lean-spec/{fable,astra}.md`, converged after round 3). The verdict is **FIX,
> then build**: the architecture, the scope and the frozen W1/soft/P0 contracts stand. Draft 2 applies the
> corrections of the joint position, which section 12 lists, and makes no other change. The DRI checks the text
> against that list. There is no second full review: only a change of meaning returns to the reviewers. S0 and
> S1a continue. S1b waits for the corrected statements, for their elaboration under Lean 4.24.0 in S1a (5.1),
> and for G1a. The review found the plan's edits 5 to 7 present (plan, section 9). Fixtures are implementation
> obligations, not claims of completed tests.
> **Nothing was built or run for this draft**: no Lean block here has been elaborated, and every expected result
> in section 8 was derived by hand. Every `file:line` reference was read on branch `design/english-lean` at
> `88762d95` and must be re-read at each step. Nothing here changes a verdict, an identity, a public code, a
> frozen file, an existing theorem statement or a checker function.

## 0. Scope, one paragraph

Today a hand-written Python parser reads an English sentence, and a separate Earley run checks that a generated
grammar derives the text in exactly one way. Nothing ties the two together, and no proof covers either. Item 1
fixes what replaces them. A grammar is data. A **derivation** is a tree that a small checking function accepts.
One parser returns the derivations of a sentence, up to a cap, and is proved sound and complete against that
checking function. The engine is stated for any token type, any terminal type and any matching between them;
English supplies its own. A meaning function gives each derivation a formula, a conclusion mark and a successor state,
or a declared rejection. A sentence **has one reading** when it has exactly one derivation and that derivation
has a meaning. A document has one reading when its sentences do, in order, with the state threaded. The English
instance adds its tokens and terminals, a lexer, a selected lexicon that Lean validates and identifies, the
rules built from both, and the check of every rendered text by the same reader. This specification fixes the definitions, the exact Lean
statements, the English of every outcome and claim, the diagnostics, and the acceptance fixtures. It builds
nothing.

In this specification: the decisions (1), the definitions (2), the English, one reading each (3), the diagnostics
(4), the Lean definitions and the exact statements (5), files, generated artefacts and gates (6), what S0 and
S1a must deliver to this specification (7), the acceptance fixtures (8), limits (9), the statement review
checklist (10), the choices this draft resolves, with the open points (11), and the response to the statement
review (12).

Two tiers of exactness. **Tier A** is the generic engine (5.2 to 5.7): every definition and statement is exact
and is frozen by the statement review, because S1b proves against it. It is generic in the token type, the
terminal type and the matching function, so no tier A file names an English token or terminal. **Tier B** is the
English instance (5.8): the signatures and theorem statements are exact. Its tokens, its terminals and their
matching are written out in full, and they may still change with S0's findings (11, O1 to O3) and with later
stages (S6 adds token classes). The contents of four lists (token rules of the lexer, `Ty`, `Reject`, the
constructors of the surface AST) are drafts that S0's inventory closes. A tier B change is reported in S2's
delta report and does not reopen tier A.

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | A derivation is a tree accepted by the checking function `Tree.derives`. That function, with the matching function of the instance (for English, `Terminal.accepts`) and `Tree.yield`, is the grammar relation. Nothing else defines what a sentence's derivations are | 2.5, 5.3 |
| D2 | A sentence has one reading when it has exactly one derivation and that derivation has a meaning. Two derivations with the same formula are two readings. Uniqueness is decided before meanings are computed | 2.8, 5.6 |
| D3 | The guarantee is a decision per sentence. No statement here says that a grammar is unambiguous | 2.6, 9 |
| D4 | The parser is proved against the relation for every grammar. Soundness and the ambiguous verdict need no well-formedness; completeness needs `Grammar.wf` | 5.4 |
| D5 | The table satisfies the cap invariant, with rule-suffix memoisation and shared witnesses. The cost bound is stated for that algorithm only | 2.6 |
| D6 | The work budget is a deterministic step count per sentence. Every rule attempt is counted, also one that fails. A verdict never depends on the budget, except to become `budget` | 2.6, 5.4 |
| D7 | A reading exposes the formula, the conclusion mark and the successor state. A document reading is a fold over the state that exposes every formula and mark | 2.8, 5.6 |
| D8 | The one-reading claim is made for a validated, identified lexicon. `Lexicon.valid` has five conditions, including cross-symbol distinctness and negative polarity. No claim is made across two lexicons | 2.9, 5.8 |
| D9 | An extension is an embedding of trees that preserves yields and successful meanings. Under it a reading is kept or the sentence becomes ambiguous. Reselecting vocabulary is not an extension | 2.11, 5.7 |
| D10 | A rendered text is checked by reading it. The check concludes formulas and marks | 5.8 |
| D11 | Every verdict is bound to six identities: source, environment, overlay, lexicon, grammar tables, and the reader's definitions (the action library and every other trusted definition file) | 2.12 |
| D12 | No public message, code or identity changes with item 1. Lean's texts appear in `english.read` responses and in shadow logs | 4 |
| D13 | The attribute-property product is factored into two rule families, one derivation per pair | 2.10 |
| D14 | The engine is generic in the token type, the terminal type and the matching function. The English tokens, terminals and matching, and the terminator condition W4, belong to the English instance | 2.2 to 2.4, 5.2, 5.8 |

## 2. Definitions

### 2.1 Terms

| Term | Meaning |
|---|---|
| source | the exact bytes submitted as English text, decoded as UTF-8 |
| token | for the engine, a member of any type; for English, one unit the lexer produces: a word, a quoted identifier, a label, a numeral or a punctuation mark (2.2) |
| sentence | the tokens between two sentence terminators, without the terminators |
| terminal | for the engine, a member of any type that has a matching function over tokens; for English, a pattern over one token (2.3) |
| grammar | rules, a start symbol and a rank for each nonterminal (2.4) |
| derivation of a sentence | a tree that the checking function accepts for the start symbol and whose leaves, in order, are exactly the sentence's tokens (2.5) |
| verdict | for one sentence: no derivation, exactly one, or more than one, with witnesses (2.6) |
| meaning of a derivation | its formula, its conclusion mark and the state after it; or a declared rejection (2.7) |
| reading of a sentence | a derivation of it together with its meaning, when the meaning is not a rejection |
| one reading | exactly one derivation, and that derivation has a meaning (2.8) |
| state | what earlier sentences contribute to later ones: for English, the constants mentioned so far and whether a quantifier occurred (2.8) |
| lexicon | the selected wording of every sort, predicate and constant (2.9) |
| valid lexicon | a lexicon that passes `Lexicon.valid` for an environment and overlay (2.9) |
| evidence | the six identities a verdict is bound to (2.12) |

"Reading" is used only in this sense. A sentence with two derivations does not have one reading, even if both
derivations give the same formula, and even if all but one are rejected by a side condition.

The engine (2.4 to 2.8 and 2.11) is generic: it is stated for any token type, any terminal type and any
function that says which tokens a terminal accepts. Sections 2.2 and 2.3 give the tokens, the terminals and the
matching of the English instance.

### 2.2 The English tokens and the lexer

An English token is one of five kinds.

| Kind | Carries | Example |
|---|---|---|
| word | its text exactly as written, and the flag `initial` | `service`, `Every` (initial) |
| quoted | the characters between the quotes, exactly | `"has_owner"` |
| label | a run of upper-case ASCII letters and a positive number | `S1` |
| numeral | an integer value | `12` |
| punct | its text | `,` `;` `:` `(` `)` `[` `]` `+` `-` `*`, and the four list markers `(a)` `(b)` `(i)` `(ii)` |

The lexer `lex` reads a source left to right and returns the sentences, or a rejection. It is a definition; it
has no theorem, and it is part of the trusted base.

1. **Limits first.** A source over 65,536 bytes is rejected (`sourceTooLong`). A source whose length after
   collapsing every whitespace run outside quotes to one space is over 10,000 characters is rejected
   (`textTooLong`). These are today's limits (`MAX_SOURCE_BYTES`, `MAX_NODES`).
2. **Whitespace** separates tokens and is otherwise ignored. Inside a quoted identifier it is kept.
3. **A quoted identifier** runs from `"` to the next `"` that is not escaped by `\`. No closing quote:
   `openQuote`.
4. **A chunk** is a maximal run of ASCII letters, ASCII digits, `_`, and characters outside ASCII that are not
   whitespace. A chunk of upper-case ASCII letters followed by a decimal number with no leading zero is a label.
   A chunk of digits is a numeral; a leading zero on a longer chunk of digits is `badNumeral`. Any other chunk is
   a word.
5. **Punctuation.** Each of the four list markers is one token when written without inner spaces. Otherwise each
   punctuation character of the table above is one token. `.` is the sentence terminator.
6. **Any other ASCII character** is rejected (`badCharacter`).
7. **Sentences.** A terminator ends the current sentence. Tokens after the last terminator: `unterminated`. A
   sentence with no token: `emptySentence`. No sentence at all: `emptyDocument`.
8. **`initial`.** A word is initial when it is the first token of its sentence, or when the tokens before it in
   the sentence are exactly one of the four conclusion markers (`therefore`, `so`, `hence`, `it follows that`).
   No other token is initial. The lexer lower-cases nothing: a word keeps its text, and terminals decide what a
   capital letter may match (2.3).

The lexer does not read the lexicon or the environment. A companion function returns the same tokens with their
byte spans, for diagnostics; `lex` is that function with the spans erased.

The token type, the terminals of 2.3 and their matching belong to the English instance and are tier B: a change
to them edits no tier A file. The token rules of items 2, 4 and 5 are drafts. Section 11 lists what S0 must
settle about them (adjacency, signed numerals, the whitespace table).

### 2.3 The English terminals and matching

| Terminal | Accepts |
|---|---|
| `kw s` | a word whose text is `s`; or, when the word is initial, whose text is `s` with its first letter in upper case |
| `content s` | a word whose text equals `s` after case folding, at any position |
| `exact t` | a token equal to `t`, the flag `initial` ignored |
| `cls numeral` | any numeral |
| `cls (label l)` | a label whose letters are `l` |

`kw` is for structure words and for lower-case spellings: it is exact, except for one capital at a sentence
start. `content` is for vocabulary words of nouns and predicate wordings. `exact` is for punctuation, quoted
identifiers and words that have a capital of their own.

**Case folding** maps `A` to `Z` onto `a` to `z`, the characters `İ` and `ı` onto `i`, `ſ` onto `s`, the Kelvin
sign onto `k`, and leaves every other character unchanged. These four are the characters that Python's
case-insensitive matching equates with ASCII letters; the discourse lexer uses the same table
(`VE.Discourse.foldChar`, `lean/VE/Discourse/Access.lean:41`).

### 2.4 Grammars and well-formedness

A **symbol** is a terminal or a nonterminal. Nonterminals are numbers. A **rule** has a left-hand nonterminal, a
right-hand list of symbols, an action index and a tag. The tag names the rule in diagnostics and has no effect
on any verdict. A **grammar** has an array of rules, a start nonterminal and an array `rank` with one number per
nonterminal.

A grammar is **well-formed** when all of the following hold. The check is one pass over the rules.

| # | Condition | Why |
|---|---|---|
| W1 | the start symbol, every left-hand side and every nonterminal on a right-hand side is below `rank.size` | the table is finite |
| W2 | no right-hand side is empty | every symbol after the first starts at a later position |
| W3 | when a right-hand side begins with a nonterminal, its rank is strictly below the rank of the left-hand side | no left recursion and no unit cycle: the first symbol reads an entry filled earlier in the same row |

`rank` is a certificate, not a trusted input. Any array that passes W3 proves the absence of left recursion,
whoever computed it.

W1 to W3 are the whole of `Grammar.wf`, and they are all that the statements of 5.3 to 5.7 use. The English
instance adds one condition of its own. It is not part of `Grammar.wf`, because the generic engine has no
terminator.

| # | Condition | Why |
|---|---|---|
| W4 | no terminal of any rule accepts the terminator | splitting at terminators loses no derivation |

The English reader checks W4 beside `Grammar.wf` (`terminatorFree`, 5.8). A grammar that is not well-formed,
or that fails W4, is never parsed by the English reader: the outcome is `invalidGrammar`.

### 2.5 Trees and derivations

A **tree** is a leaf holding a token, or a node holding a rule index and a list of trees. Its **yield** is its
leaf tokens from left to right.

The checking function `Tree.derives G X t` is true in exactly two cases:

- `X` is a terminal, `t` is a leaf, and the terminal accepts the leaf's token;
- `X` is a nonterminal `A`, `t` is a node with rule index `r`, rule `r` exists in `G`, its left-hand side is
  `A`, it has as many right-hand symbols as the node has children, and each child is accepted for the symbol
  at its position.

`Derives G X w t` holds when `t` is accepted for `X` and the yield of `t` is `w`. The derivations of a sentence
`w` are the trees `t` with `Derives G S w t`, where `S` is the start nonterminal.

Three consequences that the fixtures test. A tree names its rules by index, so two rules that are equal as data
give two derivations. A leaf holds the token itself, so the leaves of a derivation of `w` are determined by `w`:
two derivations of one sentence differ only in their nodes. A terminal is not a token: two rules whose terminals
accept the same token give two derivations.

### 2.6 The parser

`parse G cap budget w` returns up to `cap` derivations of the start symbol over the whole of `w`, or nothing
when the budget is exhausted.

**The table.** Let `n` be the number of tokens. For each start position `i`, nonterminal `A` and end position
`j` with `i < j ≤ n`, an **entry** holds trees that derive `A` over the tokens from `i` to `j`. For each start
position `p`, rule `R`, position `d ≥ 2` in its right-hand side and end position `j`, a **suffix entry** holds
lists of trees that derive the symbols of `R` from position `d` on, over the tokens from `p` to `j`.

**Fill order.** Rows are filled from `i = n − 1` down to `0`. Within a row, nonterminals are filled in
increasing rank; then the suffix entries of the row are filled. A rule for `A` at `i` reads its first symbol at
`i`: a token, or an entry of the same row with a lower rank (W3). The rest of the rule is one suffix entry at a
later position (W2), already filled. The function is total by structural recursion on the rows and the rule
list. It has no fuel.

**Cap invariant.** Every entry and every suffix entry is a duplicate-free list of what it should hold, of length
at most `cap`, and it is **either complete or of length exactly `cap`**. Building an entry takes the union over
rules and split points and truncates to `cap`. Truncation preserves the invariant: if a part that was used is
incomplete, it has `cap` members, and combining `cap` distinct members with one member of the other part already
gives `cap` distinct results. An entry shorter than `cap` is therefore complete. This is the whole content of
`parse_complete`.

**Rule-suffix memoisation.** A suffix is matched once per start position, not once per way of splitting the
span. Without it, a cap on complete entries does not bound the work: a right-hand side of `k` symbols has on the
order of `n^(k−1)` splits.

**Shared witnesses.** A stored tree refers to the stored trees of its parts. A suffix entry is a tree followed
by a reference to a later suffix entry. Nothing is copied.

**Cost.** Let `|G|` be the total length of all right-hand sides. The steps are at most a constant times
`|G| · n³ · cap²`, and the tables hold at most `|G| · n² · cap` references. Both bounds are for this algorithm.
An implementation may skip entries that cannot match (first-word indexing; indexing a hole-led rule by the first
terminal after the hole), provided the statements of 5.4 hold for it. No statement here depends on indexing.

**Budget.** A **step** is one attempt to apply a rule, or to extend a rule suffix, at a position, or one
combination of an entry with a suffix entry. An attempt is a step whether it fails or succeeds, so the budget
bounds the time and not only the successful work. `budget` bounds the steps of one sentence. When the bound is exceeded the result is nothing, never a shorter list. The result does not otherwise
depend on the budget (`parse_mono`), and for a well-formed grammar some budget always suffices
(`parse_adequate`).

**The last pass.** `parse` re-checks each tree it returns with `Tree.derives` and its yield, and removes
duplicates. Under well-formedness both passes change nothing, by the invariant. They make `parse_sound` and
`parse_nodup` hold for every grammar, without the invariant.

**Verdict.** `verdict G budget w` is `parse` with cap 2: `zero` for no tree, `one t` for one tree, `many t u`
for two. A `many` verdict carries two distinct derivations and is self-certifying. There may be more than two.

### 2.7 Meanings

A **signature** gives a set of semantic types, a set of values for each type, and the type and value of a leaf.
An **action** has a list of argument types, a result type and a function from arguments of those types to a
result of that type. A grammar is **typed** for a table of actions and a type for each nonterminal when every
rule's action exists, takes exactly the types of the rule's right-hand symbols (a terminal has the leaf type),
and returns the type of the rule's left-hand side.

The **value of a tree** is computed bottom-up: a leaf gives its token; a node applies the action of its rule to
the values of its children, when their types fit. Under the typing check, every derivation has a value of the
type of its symbol (`sem_total`). The typing check says nothing about the type of the start symbol. For
English that type is `sentence` (`start_sentence`, 5.8), so the value of a derivation of a sentence is a
sentence value, and a derivation never lacks a meaning for an internal reason (`meaning_total`).

For English the value of a sentence is a function from the state before the sentence to either a declared
rejection or the sentence's formula, its conclusion mark and the state after it. **Side conditions** are the
declared rejections: an unbound reference, a name already in scope, a list marker at the wrong depth, a limit,
an unresolved `it`, a blocked wording. They are computed by actions. They never remove a derivation: a sentence
with two derivations is ambiguous even when a side condition would reject one of them (D2).

Rules are data; meanings are not. A rule is only as reviewable as its action. The action library is hand-written
Lean and is part of the trusted base.

### 2.8 Readings, documents and the state

`OneReading G μ st w A c st2`: the sentence `w` has exactly one derivation, and the meaning function `μ` gives
that derivation, from state `st`, the value `A`, the conclusion mark `c` and the successor state `st2`.

`DocOneReading G μ st ws rs st2`: the sentences `ws`, read in order from state `st`, each have one reading; `rs`
lists each sentence's value with its mark; `st2` is the state after the last sentence. Each sentence is read
from the state its predecessor left.

`readSentence` computes the verdict first and the meaning second. Its outcomes:

| Outcome | When | State |
|---|---|---|
| `ok A c` | one derivation, and its meaning is `A`, `c` | the successor state |
| `noDerivation` | no derivation | unchanged |
| `ambiguous t u` | more than one derivation; `t` and `u` are two of them | unchanged |
| `rejected r` | one derivation, and its meaning is the rejection `r` | unchanged |
| `budget` | the step budget was exhausted | unchanged |

`readDocument` reads the sentences in order and stops at the first outcome that is not `ok`, reporting its index.

**The English state** has two parts: the constants mentioned in earlier sentences, as a sorted list without
duplicates, and whether any earlier sentence contains a quantifier. The pronoun `it` denotes a constant only as
the first token of a sentence's formula, when exactly one constant has been mentioned and no quantifier has
occurred (`english.py:957–961`, `:1376–1378`). Otherwise a derivation that uses it is rejected
(`pronounUnresolved`). This is today's rule, kept exactly (plan 7.9).

### 2.9 The lexicon and its validity

A **lexicon** selects, for an environment and an overlay: one noun and one label letter per sort; one wording
per predicate, at most one negative wording, and its input aliases; one spelling per constant. A producer
proposes it. Lean validates it and identifies it (2.12).

The **honest wordings** of a predicate `p` are:

| Kind | Wording |
|---|---|
| declared | the `verbalisation` of `p` in the environment, or in the overlay when the overlay gives one |
| profile | the wording that a profile block fixes for `p` (`alternatives@0`, `risk@0`, `rights@0`, `norms@0`) |
| mechanical | for a lower-case identifier: `{0} is p`, `{0} p {1}`, or the recorded-relation form for three to six arguments (`printer.py:190–195`) |
| fallback | `{0} is classified as "p"` or `{0} has the recorded relation "p" to {1}` (`english.py:380–381`) |

Sorts and constants have the same four kinds: the declared noun or display form, a profile noun, the bare
identifier, and the quoted fallback (`entity of sort "s"`, `"c"`).

`wordingKey` is the Lean port of `wording_key` (`english_phrases.py:49`): outside quoted parts, case is folded
and every run of whitespace and hyphens becomes one space. `negativeTemplate` is the Lean port of
`negative_template` (`english_vocabulary.py:58`, `printer.py:119`), with the idiom table and the irregular-verb
table it reads.

`Lexicon.valid E O L` holds when all five conditions hold.

| # | Condition | Source |
|---|---|---|
| V1 | **Coverage.** `L` has exactly one entry for each sort, predicate and constant of `E`, including the symbols a profile block generates, and no other entry | plan 2.4 |
| V2 | **Honesty.** Every selected wording, noun and spelling is an honest wording of its own symbol. A selected negative is the declared negative of its predicate, or the negative a profile block fixes for it. The aliases of a predicate are exactly the aliases a profile block fixes for it | plan 2.4 (1) |
| V3 | **Shape.** A wording of a predicate with `k` arguments contains each of the holes `{0}` to `{k−1}` exactly once and no other hole, and has at least one word that is not a hole. A noun and a spelling have no hole | plan 2.4 (1) |
| V4 | **Distinctness.** No selected wording, negative or alias of a predicate, no selected noun of a sort and no selected spelling of a constant equals, by `wordingKey`, any of these of another symbol: a declared wording, a declared negative, an alias or a profile wording of a predicate; a declared or selected noun of a sort; a declared or selected spelling of a constant | plan 2.4 (2); debate E1; statement review |
| V5 | **Polarity.** A selected negative equals `negativeTemplate` of the selected wording of the same predicate, unless a profile block fixes that negative | plan 2.4 (3); debate E1 |

Notes.

- V4 compares a selection with what the other symbols **declare**, not only with what the lexicon selects for
  them. When two predicates declare one template, neither may keep it; both fall back, as Python does
  (`english.py:263`, `:368`).
- V4 names sort nouns and constant spellings on both sides of the comparison, with predicate wordings. Python
  demotes a duplicate noun and a colliding constant spelling in the same way (`english.py:249–252`,
  `:498–508`).
- V5 is why a producer cannot present a positive wording as the negative of a predicate. Without a declared
  wording being selected there is no negative: the negative of a fallback wording is never a declared negative.
- The profile exceptions of V2 and V5 are data of the fixed rules, not a producer's choice. `risk@0` fixes two
  negatives (`{0} might not lead to {1}`, `{0} cannot lead to {1}`; `english.py:428–429`), and `alternatives@0`
  fixes three aliases (`english.py:409–414`). The plan debate's text of condition 3 does not mention them; the
  statement review accepted them (11, O7).

**Scope of the guarantee.** Every statement of 5.8 fixes one lexicon. Nothing is proved about two valid
lexicons. A text can have one reading under each of two valid lexicons; this specification does not prove that
the two readings are the same formula. The mutation replay gate tests it on the corpus (plan, section 5).

### 2.10 The English grammar

`grammar E L` has two parts.

- **Fixed rules**, per profile: generated table literals from a JSON source under `ve/english_grammar/`. A rule
  in the source is
  `{"tag": "exists.such-that", "lhs": "existential", "act": "exists", "rhs": ["there", "is", {"n": "article"}, {"n": "declaration"}, "such", "that", {"n": "formula"}]}`.
  A plain string is a `kw` terminal. `{"n": …}` is a nonterminal. `{"c": …}` is a `content` word, `{"p": …}` a
  punctuation token, `{"q": …}` a quoted identifier, `{"cls": …}` a token class.
- **Lexical rules**, built by `lexRules` from the environment and the lexicon: for each predicate, a clause rule,
  a subject-relative rule and an object-relative rule for its wording, its negative and its aliases; for each
  sort, its noun; for each constant, its spellings; for each profile, the rules that need a declaration (named
  relations of a reach clause, attribute sugar). In a wording, a hole becomes the term nonterminal of its slot
  (object or integer), a word becomes a `content` terminal, and a quoted part becomes an `exact` quoted token.

Each lexical rule has its own action, built by a constructor of the action library from the symbol's name, its
polarity and the order of its holes. The action table of a grammar is the fixed actions followed by these.

**The factored product (D13).** Python has one alternative `the R of t is P` for each pair of a functional
total binary relation `R` whose value sort is not the string sort and a unary predicate `P` on that value sort
(`english.py:1907–1912`). Lean has:

- one rule per such relation `R` with value sort `s`: `atom → the R of term is property_s`;
- one rule per unary predicate `P` on sort `s`: `property_s → P`.

A pair `(R, P)` has exactly one derivation in both grammars: Python's alternative, and Lean's relation rule over
the property rule. The meaning is unchanged: there is a value of sort `s` that `R` relates the term to and that
satisfies `P` (`english.py:1018–1019`). For 128 relations and 128 properties this is 256 rules, not 16,384. The
`property_s` rules begin with a terminal, so W3 puts no condition on them.

### 2.11 Extensions

A grammar grows when a profile is added, a predicate is declared, or a wording is added. An **embedding** of `G`
into `G2` is a map on trees with three properties:

1. it sends every derivation of a sentence in `G` to a derivation of the same sentence in `G2`;
2. it sends two different derivations of one sentence to two different derivations;
3. when a derivation has a meaning in `G` (a formula, a mark and a successor state), its image has exactly that
   meaning in `G2`, from the same initial state.

An injective map on rules that preserves each rule's two sides and its action induces such a map on trees
(`rule_map_embeds`). Types need no separate clause: an action fixes the types of both sides of its rule.

Under an embedding, a sentence with one reading in `G` either has the same reading in `G2`, or has at least two
derivations in `G2` and is rejected as ambiguous. It never silently gets another formula.

**Not an extension:** a change after which an existing symbol has a different selected wording. The old rule
is then absent from `G2`, no embedding exists, and nothing is proved. An added declaration can cause this (a
collision demotes an existing wording to its fallback; a new name changes a label letter).

### 2.12 Evidence and identities

Every `english.read` response carries six identities, computed by the service from the request it decided.

| Field | Identity of | Computed as |
|---|---|---|
| `source_sha256` | the exact source bytes | SHA-256 of the bytes |
| `environment_id` | the environment | the existing identity, unchanged |
| `overlay_digest` | the overlay | the existing digest (`ve-english-vocabulary-v1`); the field is absent when there is no overlay |
| `lexicon_id` | the selected lexicon | the digest of its canonical JSON under the new domain `ve-english-lexicon-v1` |
| `grammar_id` | the fixed-rule tables of the environment's profiles | the digest, under the new domain `ve-english-grammar-v1`, of the profile names with the SHA-256 of each table's JSON source |
| `actions_version` | the reader's definitions: every Lean file that holds a trusted definition of 2.13 (the tokens and their matching, the lexer, the derivation checker, well-formedness, lexicon validity with `wordingKey` and `negativeTemplate`, `lexRules`, the action library and `meaning`, the AST encoding) | a string constant of the Lean library (`actionsVersion`), raised on every change to one of those files |

A lock file under `ve/english_grammar/` holds the SHA-256 of each table source and of every Lean file that
holds a trusted definition of 2.13, with the current `actions_version`. It lists those files by path. The
commit hook fails when a hash changes and the version does not. The field keeps the name `actions_version`; it
is the version of all the reader's definitions, not only of the actions. So a change to `lex`,
`Terminal.accepts`, `lexRules`, `Lexicon.valid` or `EFormula.encode` cannot leave all six identities equal. A
record that cites a reading cites all six identities. A change to any of them invalidates the record. The fields are
additive: no existing identity changes.

### 2.13 What is trusted, what is proved, what is tested

| Layer | Items |
|---|---|
| Trusted definitions | `Tree.derives`, `Tree.yield`, `Grammar.wf` as the meaning of "well-formed"; the English tokens and terminals, `Terminal.accepts`, the terminator condition `terminatorFree`; `lex`; `Lexicon.valid`, `wordingKey`, `negativeTemplate`; `lexRules`, the fixed-rule data; the action library and `meaning`; the wire encoding of the surface AST; the statements of section 5 |
| Proved | the parser against the relation; the verdicts; the totality of meanings, with the type of the English start symbol; the sentence and document readers against `OneReading` and `DocOneReading`; uniqueness (P1) for a fixed lexicon; the rendered-text check; the extension theorems |
| Checked at run time, per request | `Lexicon.valid`, `Grammar.wf`, `terminatorFree`, `Grammar.typed`; each tree returned by the parser |
| Tested only | agreement with Python on the sealed corpus and the reverse corpus; lexicon mutation replay; the tree correspondence; performance |
| Outside | intent and source fidelity; that a declared wording means what its predicate means; the Lean kernel, compiler and runtime; JSON decoding and the service glue |

## 3. English: one reading each

Item 1 adds no wording that an author writes. It adds sentences that the system says: the claim a record may
make, the outcome of a read, and the plain-English form of each theorem. Each is fixed here with what it means
exactly and what it does not mean.

### 3.1 The claim sentences

| Id | Sentence | Means exactly | Does not mean |
|---|---|---|---|
| C1 | `Lean read this text and reported one reading per sentence. The reader's correctness has not yet been proved.` | `read` returned `ok`, and the theorems of 5.4 to 5.8 are not yet all in the audit inventory | that uniqueness is proved; the label "Lean-verified" is never used for it |
| C2 | `Each sentence of this text has exactly one reading under the identified vocabulary selection. Lean checked this, and the check is proved correct relative to the grammar definitions.` | `read` returned `ok`, the theorems are in the audit inventory, and the six identities are attached | that the reading is what the author intended; that another valid vocabulary selection gives the same reading; that the grammar definitions are right |
| C3 | `This rendered text was read back by Lean and has exactly one reading: the formulas it was rendered from, with their conclusion marks.` | `checkRendering` returned true for this text and these formulas | that the renderer always succeeds; that the text is good English |
| C4 | `The marked conclusions were not checked here.` | conclusion marks are part of the reading; whether a marked sentence follows from the earlier ones is decided elsewhere | that a marked conclusion is valid, or that it is invalid |

C1 is the label until gate G1b and the S2 statements are in the audit. C2 replaces it afterwards. C4 accompanies
either whenever a mark is present.

### 3.2 The outcomes, in plain words

`{i}` is the number of the sentence, counted from one in these texts.

| Status | Text | Means exactly |
|---|---|---|
| `one` | (no message) | every sentence has one reading and the document passed the type check |
| `none` | `Sentence {i} has no reading with the current vocabulary.` | no tree is a derivation of the sentence |
| `many` | `Sentence {i} can be read in more than one way. Two of the ways are shown.` | at least two different trees are derivations; exactly two are returned |
| `rejected` | one text per code (4.2), for example `Sentence {i} uses a name before introducing it.` | the sentence has exactly one derivation, and its meaning is that rejection; or the lexer or the type check rejected the text; or, in translation mode, the text has more than one sentence (4.3) |
| `budget` | `Sentence {i} needs more work than the limit allows. No verdict was reached.` | the step budget was exhausted; nothing is known about the sentence |
| `invalidGrammar` | `The vocabulary selection sent with this text was not accepted. No text was read.` | `Lexicon.valid`, `Grammar.wf`, the terminator check `terminatorFree` or `Grammar.typed` returned false |

`many` says "can be read in more than one way", not "has two meanings": the two ways may give the same formula.
`budget` and `invalidGrammar` are not verdicts about the text.

### 3.3 The theorems, in plain words

| Statement | Plain English | It does not say |
|---|---|---|
| `yield_ne_nil` | If the grammar is well-formed, every tree that the checking function accepts covers at least one token. | |
| `parse_sound` | Every tree the parser returns is a derivation of the sentence. | that the parser returns every derivation |
| `parse_nodup` | The parser returns no tree twice. | |
| `parse_length` | The parser returns at most as many trees as the cap. | |
| `parse_complete` | If the grammar is well-formed and the parser returns fewer trees than the cap, it has returned every derivation of the sentence. | anything when the list has reached the cap |
| `parse_mono` | A larger budget never changes a result; it can only turn "no result" into a result. | |
| `parse_adequate` | For a well-formed grammar, every sentence gets a result when the budget is large enough. | how large |
| `verdict_zero` | If the grammar is well-formed and the verdict is "none", the sentence has no derivation. | |
| `verdict_one` | If the grammar is well-formed and the verdict is "one", the returned tree is a derivation and every derivation of the sentence equals it. | |
| `verdict_many` | If the verdict is "many", the two returned trees are different derivations of the sentence. | that there are only two |
| `sem_total` | If the grammar is typed, every derivation has a value of the type of its symbol. | that the value is a formula: it may be a function that returns a declared rejection |
| `read_sound` | If the grammar is well-formed and the reader accepts a sentence with a formula, a mark and a successor state, then the sentence has exactly one derivation and that derivation has exactly that formula, mark and successor state. | |
| `read_complete` | If the grammar is well-formed and a sentence has one reading, the reader returns that reading, or reports that the budget was exhausted. | |
| `read_none` | If the grammar is well-formed and the reader reports no derivation, the sentence has no derivation, and the state is unchanged. | |
| `read_ambiguous` | If the reader reports an ambiguity, the two returned trees are different derivations of the sentence, and the state is unchanged. | that there are only two |
| `read_rejected` | If the grammar is well-formed and the reader reports a rejection, the sentence has exactly one derivation, the meaning of that derivation is that rejection, and the state is unchanged. | |
| `doc_sound`, `doc_complete` | The same two statements for a document: sentence by sentence, in order, with each sentence read from the state its predecessor left. | |
| `doc_stopped` | If the grammar is well-formed and the document reader stops at a sentence, every sentence before that one has one reading, in order; the reported outcome is the reader's outcome for that sentence, from the state the earlier sentences leave; and that outcome is not an acceptance. | anything about the sentences after that one |
| `one_reading_unique`, `doc_unique`, `english_reading_unique` | If a sentence has one reading from a given state, its formula, mark and successor state are determined. The same holds for a document, and for an English text under one valid lexicon. | that a sentence has at most one reading: a sentence with two derivations that both have a meaning has two readings; anything about a second lexicon |
| `one_reading_single` | If a sentence has one reading, every derivation of it that has a meaning has that same formula, mark and successor state. | the converse: one formula does not imply one derivation |
| `readings_exact` | If the grammar is well-formed and the parser returns fewer trees than the cap, the listed results are exactly the results of the derivations that have a meaning. | anything when the list of trees has reached the cap |
| `extension_safe` | Under an embedding, a sentence with one reading in the smaller grammar has the same reading in the larger one, or has at least two derivations there. | anything when vocabulary was reselected |
| `extension_keeps_many` | Under an embedding, a sentence with two derivations still has two. | |
| `rule_map_sem` | Under a rule map that satisfies `RuleMap.Ok`, the image of a tree accepted in the smaller grammar is accepted in the larger grammar for the renamed symbol, has the same yield and has the same value. | |
| `rule_map_embeds` | A rule map that satisfies `RuleMap.Ok` gives an embedding, when both grammars compute the meaning of a tree from the tree's value by the same function. | that such a rule map exists for two given grammars |
| `read_ok` | If the English reader accepts a text, then the lexicon is valid, and each sentence of the text has exactly one reading, in order, with the returned formulas and marks, and the formulas are well typed. | that the reading is intended |
| `read_complete_english` | If an English text has one reading under a valid lexicon, and the grammar passes the three checks the reader runs on it (well-formed, free of the terminator, typed), the reader returns that reading, or reports that the budget was exhausted. | |
| `start_sentence` | The start symbol of the grammar built for an environment and a lexicon has the type `sentence`. | |
| `meaning_total` | If a grammar is typed and its start symbol has the type `sentence`, every derivation of a sentence has a sentence value, and the meaning of the derivation is that value applied to the state. The fallback branch of `meaning` is not reached. | that the result is a formula: it may be a rejection that an action declared |
| `checked_rendering` | If the check of a rendered text succeeds, the text has exactly one reading, and it is the given formulas and marks. | that every formula has a rendering that passes |

`grammar_extension` has no row. Its statement is deferred (5.8), so there is nothing to paraphrase yet.

### 3.4 Wordings this replaces, and why

| Today | Problem | Replaced by |
|---|---|---|
| "unique derivation" for the Earley audit, and "the reading" for the hand parser's formula | two artefacts; nothing shows the formula is the meaning of the derivation (plan G1) | "one reading": one derivation and its meaning, from one artefact |
| `English has two derivations:` followed by two Lark trees (`unambiguity.py:75`) | the trees are over regex terminals; structure inside a wording is invisible | `many`, with two trees over word tokens, as rule tags with token spans |
| `ResourceLimit` for a 30-second wall clock (`unambiguity.py:15`) | not reproducible | `budget`, a step count |
| "Lean-verified English" | no theorem covers the full surface today | C1 before the proofs, C2 after, never the bare label |

## 4. Diagnostics

No public message, code or identity changes with item 1 (D12). Under shadow, Python's result is returned and
Lean's is logged. Under Lean authority (S5) Python's message is still the one shown when both reject in mapped
classes, as for `_parse_lean` (`ve/parser.py:387`); a disagreement fails closed as `CheckerUnavailable`.

### 4.1 Statuses and their Python classes

| `english.read` status | Lean outcome | Python class today | Python public code |
|---|---|---|---|
| `one` | `read = ok rs` | accepted | — |
| `none` | `stopped i noDerivation` | `SyntaxError` | `SyntaxError` |
| `many` | `stopped i (ambiguous t u)` | `AmbiguousDerivation` | `SyntaxError` |
| `rejected` | `stopped i (rejected r)`, `lexical r` or `illTyped`; in translation mode also a text of more than one sentence (4.3) | by code (4.2) | by code |
| `budget` | `stopped i budget` | `ResourceLimit`, wall clock; excluded from the comparison and listed | `ResourceLimit` |
| `invalidGrammar` | `invalidGrammar why` | none: the producer and Lean disagree | `CheckerUnavailable` at the adapter |

`invalidGrammar` is operational. The lexicon comes from Python's own vocabulary policy, so an invalid one is a
producer fault, not a fault of the author's text.

### 4.2 Rejection codes

The list is tier B: S0 closes it from the 49 rejection sites of the hand parser (plan 1.3) and gives each
blocked wording its `id`. Each code has one fixed text. The Python column was read from the source where a line
is cited; S0 confirms the other rows.

| Code | Text | Python today |
|---|---|---|
| `SourceTooLong` | `The text is longer than 65,536 bytes.` | `ResourceLimit` (`english.py:1643`) |
| `TextTooLong` | `The text is longer than 10,000 characters after spaces are collapsed.` | `ResourceLimit` (`unambiguity.py:32`) |
| `BadCharacter` | `The character at position {offset} cannot appear outside a quoted name.` | `SyntaxError` |
| `OpenQuote` | `The quoted name that starts at position {offset} is not closed.` | `SyntaxError` |
| `BadNumeral` | `The number at position {offset} is not written in canonical form.` | `SyntaxError` |
| `EmptyDocument` | `Write at least one statement ending with a period.` | `SyntaxError`, the same text (`english.py:1632`) |
| `EmptySentence` | `Sentence {i} is empty.` | `SyntaxError` |
| `Unterminated` | `The text after the last period is not a sentence. End it with a period.` | `SyntaxError` |
| `UnboundReference` | `Sentence {i} uses a name before introducing it.` | `SyntaxError` |
| `ShadowedName` | `Sentence {i} introduces a name that is already in use.` | `SyntaxError` (`english.py:943`) |
| `SortMismatch` | `Sentence {i} relates two things of different kinds where the same kind is required.` | `SyntaxError` (`english.py:1472`) |
| `MarkerDepth` | `Sentence {i} uses a list marker that does not fit its depth.` | `SyntaxError` |
| `NestingLimit` | `Sentence {i} is nested more than 64 levels deep.` | `ResourceLimit` (`english.py:1371`) |
| `NumeralBound` | `Sentence {i} contains a number that is too long.` | `ResourceLimit` |
| `PronounUnresolved` | `Sentence {i} uses "it", and it is not settled what "it" refers to. Repeat the name.` | `SyntaxError` (`english.py:1378`) |
| `BlockedWording` | the fixed rewrite advice of the wording `id` | `SyntaxError` |
| `IllTyped` | `The text was read, and its formulas do not pass the type check.` | `UnknownSymbol`, `TypeMismatch` |
| `NotOneSentence` | `This text has more than one sentence. Translation mode reads exactly one.` | none: translation mode is new (4.3) |
| `Internal` | none. It is produced only by the fallback branch of `meaning`, which a derivation of a typed grammar whose start symbol has the type `sentence` never reaches (`meaning_total`). For `grammar E L` the start type is given by `start_sentence`, or by the check in `read` if the fallback of 5.8 is used | — |

### 4.3 The response

`english.read` takes the environment, the overlay, the selected lexicon, the source, the mode (`authoring` or
`translation`) and the cap. Its response has:

| Field | Present | Content |
|---|---|---|
| `status` | always | one of the six of 4.1 |
| `identities` | always | the six of 2.12 |
| `sentence` | `none`, `many`, `budget`, and `rejected` by a side condition | the index of the first sentence that is not `ok`, from zero |
| `code`, `text` | every status but `one` | the code and its fixed text |
| `ast`, `canonical`, `conclusions` | `one` | the formulas in wire form, the canonical strict text, the indices of the marked sentences |
| `derivation` | `one` | per sentence, the tree as rule tags with token spans |
| `witnesses` | `many` | the two trees, as rule tags with token spans |
| `readings`, `complete` | translation mode | the results of the returned trees that have a meaning (`readingSet`); `complete` is true exactly when the parser returned fewer trees than the cap |

**Translation mode** reads exactly one sentence, from the initial state `DState.init`. A text of more than one
sentence is `rejected` with the code `NotOneSentence`; this is decided on the result of `lex`, before any
sentence is parsed. `complete` is computed from the trees the parser returned, before any meaning is computed.
It is not computed from `readings`: a rejected meaning makes `readings` shorter and tells nothing about whether
the parser returned every derivation. When `complete` is true, `readings_exact` applies.

A field that would be null is omitted (the service's decoder, `lean/VE/Json.lean`, rejects `null`). `english.grammar` exports the
instantiated grammar as JSON: the rules with their tags, the nonterminal names, the ranks and the identities.

### 4.4 Tool diagnostics

| Tool | Failure | Message names |
|---|---|---|
| fixed-rule generator `--check` | a generated Lean table differs from its JSON source | the profile and the first differing rule tag |
| the same | the lock file's hash of a table or of a trusted definition file (2.12) differs, with the version unchanged | the file and the two hashes |
| grammar instantiation | `Grammar.wf` or `terminatorFree` is false | the first failing rule by tag, and the condition W1 to W4 |
| the same | `Grammar.typed` is false | the first failing rule by tag, the action's types and the rule's types |
| lexicon validation | `Lexicon.valid` is false | the first failing symbol and the condition V1 to V5 |

## 5. Lean: definitions and the exact statements

### 5.1 Modules and conventions

New files only; no existing Lean file is edited. Names have no prime and no `?`. No function uses a totality
escape. Every theorem gets a `#print axioms` line in `VE/Audit.lean`; only `propext`, `Classical.choice` and
`Quot.sound` may appear. Free variables in a statement are implicit arguments, bound by the `variable` line
above it. `S` is never an abbreviation here: the start symbol is written `.n G.start`. A `def`, `instance` or
`structure` shown without a body is a signature: section 2 says what it computes, and the stage named in 5.9
writes it. A `theorem` is shown without its proof. A `def` shown with a body is the definition.

The engine of 5.2 to 5.7 is generic. `T` is the token type, `K` is the terminal type, and an instance of the
class `Accepts K T` says which tokens a terminal accepts. No definition or statement of 5.2 to 5.7 names an
English token or terminal, so no proof of S1b can do a case analysis on one. The English instance (5.8)
supplies `Tok`, `Terminal` and the instance. An instance argument on a `variable` line (`[DecidableEq T]`,
`[Accepts K T]`) belongs to the declarations that use it: `[Accepts K T]` to `Tree.derives` and to what
mentions it, `[DecidableEq T]` to the parser and to what calls it.

**Elaboration.** No block of this section has been elaborated. S1a elaborates the definitions and the theorem
types of 5.2 to 5.7 under Lean 4.24.0, with each theorem written as a definition of type `Prop`, because the
audit admits no unproved theorem. A correction that elaboration forces and that leaves the meaning unchanged (a
binder, an instance argument, the placement of a `variable` line, a derived instance written by hand) is listed
in S1a's report and checked by the DRI. A change of meaning returns to the reviewers. S1b starts from the
elaborated statements.

| Module | Namespace | Content | Tier |
|---|---|---|---|
| `VE/Grammar/Basic.lean` | `VE.Grammar` | the matching class `Accepts`, symbols, rules, grammars, `wf` | A |
| `VE/Grammar/Derives.lean` | `VE.Grammar` | trees, `yield`, `derives`, `Derives` | A |
| `VE/Grammar/Table.lean` | `VE.Grammar` | `parse`, `verdict` | A |
| `VE/Grammar/TableProofs.lean` | `VE.Grammar` | the statements of 5.4 | A |
| `VE/Grammar/Meaning.lean` | `VE.Grammar` | signatures, actions, `typed`, `Tree.sem`, `sem_total` | A |
| `VE/Grammar/Reading.lean` | `VE.Grammar` | `OneReading`, `DocOneReading`, the readers, the statements of 5.6 | A |
| `VE/Grammar/Extension.lean` | `VE.Grammar` | `Embeds`, `RuleMap`, the statements of 5.7 | A |
| `VE/EnglishGrammar/*.lean` | `VE.EnglishGrammar` | tokens, terminals and their matching, the terminator condition, surface AST, lexer, lexicon, rules, actions, `read`, the statements of 5.8 | B |

`VE.English.Tok`, `VE.English.Tree`, `VE.English.Lexicon`, `VE.English.OneReading` and `VE.Discourse.Derives`
already exist. The new names live in other namespaces and no new module opens `VE.English` or `VE.Discourse`.

### 5.2 Matching, symbols, grammars (`Basic.lean`)

```lean
namespace VE.Grammar

/-- Which tokens a terminal accepts. The engine is generic in the token type `T`, the terminal
type `K` and this function. -/
class Accepts (K T : Type) where
  accepts : K → T → Bool

inductive Sym (K : Type) where
  | t (a : K)
  | n (A : Nat)
  deriving DecidableEq, Repr

structure Rule (K : Type) where
  lhs : Nat
  rhs : List (Sym K)
  act : Nat
  tag : String
  deriving DecidableEq, Repr

/-- Nonterminals are the numbers below `rank.size`. -/
structure Grammar (K : Type) where
  rules : Array (Rule K)
  start : Nat
  rank : Array Nat

variable {K : Type}

/-- W1 to W3 of the specification, for one rule. -/
def Rule.wf (G : Grammar K) (R : Rule K) : Bool :=
  decide (R.lhs < G.rank.size) &&
  !R.rhs.isEmpty &&
  R.rhs.all (fun
    | .t _ => true
    | .n A => decide (A < G.rank.size)) &&
  (match R.rhs with
    | .n B :: _ => decide (G.rank.getD B 0 < G.rank.getD R.lhs 0)
    | _ => true)

def Grammar.wf (G : Grammar K) : Bool :=
  decide (G.start < G.rank.size) && G.rules.all (Rule.wf G)

end VE.Grammar
```

`Rule.wf` has no clause for the terminator: the engine has none. W4 is `terminatorFree`, in 5.8.

### 5.3 Trees and derivations (`Derives.lean`)

```lean
namespace VE.Grammar

inductive Tree (T : Type) where
  | leaf (tok : T)
  | node (rule : Nat) (kids : List (Tree T))
  deriving Repr

instance {T : Type} [DecidableEq T] : DecidableEq (Tree T)   -- derived or written by hand; the type is nested

variable {T K : Type} [Accepts K T]

mutual
def Tree.yield : Tree T → List T
  | .leaf tok => [tok]
  | .node _ kids => yieldAll kids
def yieldAll : List (Tree T) → List T
  | [] => []
  | t :: ts => t.yield ++ yieldAll ts
end

mutual
/-- The grammar relation, as a checking function. -/
def Tree.derives (G : Grammar K) : Sym K → Tree T → Bool
  | .t a, .leaf tok => Accepts.accepts a tok
  | .n A, .node r kids =>
      match G.rules[r]? with
      | some R => R.lhs == A && derivesAll G R.rhs kids
      | none => false
  | _, _ => false
def derivesAll (G : Grammar K) : List (Sym K) → List (Tree T) → Bool
  | [], [] => true
  | X :: Xs, t :: ts => t.derives G X && derivesAll G Xs ts
  | _, _ => false
end

def Derives (G : Grammar K) (X : Sym K) (w : List T) (t : Tree T) : Prop :=
  t.derives G X = true ∧ t.yield = w

variable {G : Grammar K} {X : Sym K} {t : Tree T}

/-- No empty rule: a derivation covers at least one token. -/
theorem yield_ne_nil : G.wf = true → t.derives G X = true → t.yield ≠ []

end VE.Grammar
```

### 5.4 The parser and the verdict (`Table.lean`, `TableProofs.lean`)

```lean
namespace VE.Grammar

variable {T K : Type} [DecidableEq T] [Accepts K T]

/-- Up to `cap` derivations of the start symbol over `w`; `none` when the step budget is exhausted. -/
def parse (G : Grammar K) (cap budget : Nat) (w : Array T) : Option (List (Tree T))

variable {G : Grammar K} {cap b b2 : Nat} {w : Array T} {ts : List (Tree T)} {t u : Tree T}

theorem parse_sound    : parse G cap b w = some ts → t ∈ ts → Derives G (.n G.start) w.toList t
theorem parse_nodup    : parse G cap b w = some ts → ts.Nodup
theorem parse_length   : parse G cap b w = some ts → ts.length ≤ cap
theorem parse_complete : G.wf = true → parse G cap b w = some ts → ts.length < cap →
    Derives G (.n G.start) w.toList t → t ∈ ts
theorem parse_mono     : parse G cap b w = some ts → b ≤ b2 → parse G cap b2 w = some ts
theorem parse_adequate : G.wf = true → ∃ b0, ∀ b, b0 ≤ b → (parse G cap b w).isSome = true

inductive Verdict (T : Type) where
  | zero
  | one (t : Tree T)
  | many (t u : Tree T)

def verdict (G : Grammar K) (budget : Nat) (w : Array T) : Option (Verdict T) :=
  match parse G 2 budget w with
  | none => none
  | some [] => some .zero
  | some [t] => some (.one t)
  | some (t :: u :: _) => some (.many t u)

theorem verdict_zero : G.wf = true → verdict G b w = some .zero →
    ∀ u, ¬ Derives G (.n G.start) w.toList u
theorem verdict_one  : G.wf = true → verdict G b w = some (.one t) →
    Derives G (.n G.start) w.toList t ∧ ∀ u, Derives G (.n G.start) w.toList u → u = t
theorem verdict_many : verdict G b w = some (.many t u) →
    Derives G (.n G.start) w.toList t ∧ Derives G (.n G.start) w.toList u ∧ t ≠ u

end VE.Grammar
```

`parse_sound`, `parse_nodup`, `parse_length`, `parse_mono` and `verdict_many` have no well-formedness
hypothesis. `parse_complete` is the one hard theorem. It is proved from the cap invariant, stated here for an
entry `e` that should hold the derivations of `X` over the tokens from `i` to `j`:

```lean
def Span (G : Grammar K) (w : Array T) (X : Sym K) (i j : Nat) (t : Tree T) : Prop :=
  Derives G X ((w.toList.drop i).take (j - i)) t

def EntryOk (G : Grammar K) (cap : Nat) (w : Array T) (X : Sym K) (i j : Nat) (e : List (Tree T)) : Prop :=
  e.Nodup ∧ (∀ t ∈ e, Span G w X i j t) ∧ e.length ≤ cap ∧
  (e.length < cap → ∀ t, Span G w X i j t → t ∈ e)
```

The invariant lemma says: for a well-formed grammar, every entry of the filled table satisfies `EntryOk`, and
every suffix entry satisfies the same four clauses for lists of trees and `derivesAll`. Its exact form depends
on the table type that S1a chooses, so it is an internal lemma; the reviewed statements are the ones in the
block above. The proof is by induction on the fill order: on the row, from the last to the first, and within a
row on the rank. `yield_ne_nil` places every symbol after the first in a later row.

### 5.5 Meanings (`Meaning.lean`)

```lean
namespace VE.Grammar

/-- A signature over the token type `T`. -/
structure Sig (T : Type) where
  Ty : Type
  decEq : DecidableEq Ty
  Sem : Ty → Type
  tok : Ty
  leaf : T → Sem tok

variable {T K : Type}

/-- The arguments of an action: one value per type. -/
def Args (S : Sig T) : List S.Ty → Type
  | [] => Unit
  | τ :: τs => S.Sem τ × Args S τs

structure Action (S : Sig T) where
  args : List S.Ty
  out : S.Ty
  run : Args S args → S.Sem out

def symTy (S : Sig T) (ty : Nat → S.Ty) : Sym K → S.Ty
  | .t _ => S.tok
  | .n A => ty A

/-- Each rule's action exists and fits both sides of the rule. -/
def Grammar.typed (G : Grammar K) (S : Sig T) (ty : Nat → S.Ty) (acts : Array (Action S)) : Bool

/-- A value with its type. -/
abbrev Val (S : Sig T) := (τ : S.Ty) × S.Sem τ

/-- The values as arguments of the given types, when their types are exactly those. -/
def toArgs (S : Sig T) : (τs : List S.Ty) → List (Val S) → Option (Args S τs)

mutual
def Tree.sem (G : Grammar K) (S : Sig T) (acts : Array (Action S)) : Tree T → Option (Val S)
  | .leaf tok => some ⟨S.tok, S.leaf tok⟩
  | .node r kids =>
      match G.rules[r]? with
      | some R =>
          match acts[R.act]? with
          | some a =>
              match semAll G S acts kids with
              | some vs => (toArgs S a.args vs).map fun xs => ⟨a.out, a.run xs⟩
              | none => none
          | none => none
      | none => none
def semAll (G : Grammar K) (S : Sig T) (acts : Array (Action S)) : List (Tree T) → Option (List (Val S))
  | [] => some []
  | t :: ts =>
      match t.sem G S acts, semAll G S acts ts with
      | some v, some vs => some (v :: vs)
      | _, _ => none
end

variable [Accepts K T]
variable {G : Grammar K} {S : Sig T} {ty : Nat → S.Ty} {acts : Array (Action S)} {X : Sym K} {t : Tree T}

theorem sem_total : G.typed S ty acts = true → t.derives G X = true →
    ∃ v : S.Sem (symTy S ty X), t.sem G S acts = some ⟨symTy S ty X, v⟩

end VE.Grammar
```

`Grammar.typed` is true exactly when, for every rule `R` of `G`, `acts[R.act]?` is some `a` with
`a.args = R.rhs.map (symTy S ty)` and `a.out = ty R.lhs`, both compared by `S.decEq`. The value of a tree does
not depend on `ty`: a value carries its type. This is what makes the statements of 5.7 plain equalities.

### 5.6 Readings and documents (`Reading.lean`)

The reader is stated for any meaning function. The English instance supplies one (5.8).

```lean
namespace VE.Grammar

/-- From the state before a sentence and a tree: the sentence's value, its conclusion mark and the
state after it; or a declared rejection. -/
abbrev Meaning (T σ ρ α : Type) := σ → Tree T → Except ρ (α × Bool × σ)

variable {T K σ ρ α : Type} [DecidableEq T] [Accepts K T]
variable {G : Grammar K} {μ : Meaning T σ ρ α} {st st1 st2 st3 : σ} {b cap : Nat}
variable {w : Array T} {ws : List (Array T)} {A B : α} {c d : Bool} {t u : Tree T} {r : ρ}

/-- One derivation, and its complete result. -/
def OneReading (G : Grammar K) (μ : Meaning T σ ρ α) (st : σ) (w : List T) (A : α) (c : Bool) (st2 : σ) : Prop :=
  ∃ t, Derives G (.n G.start) w t ∧ (∀ u, Derives G (.n G.start) w u → u = t) ∧ μ st t = .ok (A, c, st2)

inductive Outcome (T ρ α : Type) where
  | ok (A : α) (conclusion : Bool)
  | noDerivation
  | ambiguous (t u : Tree T)
  | rejected (r : ρ)
  | budget

def readSentence (G : Grammar K) (μ : Meaning T σ ρ α) (st : σ) (b : Nat) (w : Array T) : Outcome T ρ α × σ :=
  match verdict G b w with
  | none => (.budget, st)
  | some .zero => (.noDerivation, st)
  | some (.many t u) => (.ambiguous t u, st)
  | some (.one t) =>
      match μ st t with
      | .ok (A, c, st2) => (.ok A c, st2)
      | .error r => (.rejected r, st)

theorem read_sound : G.wf = true → readSentence G μ st b w = (.ok A c, st2) →
    OneReading G μ st w.toList A c st2
theorem read_complete : G.wf = true → OneReading G μ st w.toList A c st2 →
    readSentence G μ st b w = (.ok A c, st2) ∨ readSentence G μ st b w = (.budget, st)
theorem read_none : G.wf = true → readSentence G μ st b w = (.noDerivation, st2) →
    st2 = st ∧ ∀ u, ¬ Derives G (.n G.start) w.toList u
theorem read_ambiguous : readSentence G μ st b w = (.ambiguous t u, st2) →
    st2 = st ∧ Derives G (.n G.start) w.toList t ∧ Derives G (.n G.start) w.toList u ∧ t ≠ u
theorem read_rejected : G.wf = true → readSentence G μ st b w = (.rejected r, st2) →
    st2 = st ∧ ∃ t, Derives G (.n G.start) w.toList t ∧
      (∀ u, Derives G (.n G.start) w.toList u → u = t) ∧ μ st t = .error r

theorem one_reading_unique {w : List T} : OneReading G μ st w A c st2 → OneReading G μ st w B d st3 →
    B = A ∧ d = c ∧ st3 = st2
theorem one_reading_single {w : List T} : OneReading G μ st w A c st2 → Derives G (.n G.start) w t →
    μ st t = .ok (B, d, st3) → B = A ∧ d = c ∧ st3 = st2

/-- Translation mode: the results of the listed trees that have a meaning. -/
def readingSet (μ : Meaning T σ ρ α) (st : σ) (ts : List (Tree T)) : List (α × Bool × σ) :=
  ts.filterMap fun t => match μ st t with
    | .ok x => some x
    | .error _ => none

theorem readings_exact {ts : List (Tree T)} {x : α × Bool × σ} :
    G.wf = true → parse G cap b w = some ts → ts.length < cap →
    (x ∈ readingSet μ st ts ↔ ∃ t, Derives G (.n G.start) w.toList t ∧ μ st t = .ok x)

/-- A document: its sentences read in order, the state threaded. Every value and mark is exposed. -/
def DocOneReading (G : Grammar K) (μ : Meaning T σ ρ α) : σ → List (List T) → List (α × Bool) → σ → Prop
  | st, [], [], st2 => st2 = st
  | st, w :: ws, (A, c) :: rs, st2 =>
      ∃ st1, OneReading G μ st w A c st1 ∧ DocOneReading G μ st1 ws rs st2
  | _, _, _, _ => False

inductive DocOutcome (T ρ α : Type) where
  | ok (rs : List (α × Bool))
  | stopped (index : Nat) (o : Outcome T ρ α)

/-- Reads the sentences in order and stops at the first outcome that is not `ok`. The state returned
with `stopped` is the state before that sentence. -/
def readDocument (G : Grammar K) (μ : Meaning T σ ρ α) (st : σ) (b : Nat) (ws : List (Array T)) :
    DocOutcome T ρ α × σ

variable {rs rs2 : List (α × Bool)} {i : Nat} {o : Outcome T ρ α}

theorem doc_sound : G.wf = true → readDocument G μ st b ws = (.ok rs, st2) →
    DocOneReading G μ st (ws.map (·.toList)) rs st2
theorem doc_complete : G.wf = true → DocOneReading G μ st (ws.map (·.toList)) rs st2 →
    readDocument G μ st b ws = (.ok rs, st2) ∨
    ∃ i st1, readDocument G μ st b ws = (.stopped i .budget, st1)
theorem doc_stopped : G.wf = true → readDocument G μ st b ws = (.stopped i o, st1) →
    ∃ rs w, DocOneReading G μ st ((ws.take i).map (·.toList)) rs st1 ∧ ws[i]? = some w ∧
      (readSentence G μ st1 b w).1 = o ∧ ∀ A c, o ≠ .ok A c
theorem doc_unique {ws : List (List T)} : DocOneReading G μ st ws rs st2 → DocOneReading G μ st ws rs2 st3 →
    rs2 = rs ∧ st3 = st2

end VE.Grammar
```

No statement of this block has a typing hypothesis. Typing matters to what `μ` can return, not to the reader.
`doc_stopped` makes a failure report exact: the sentences before the reported index each have one reading, and
the reported outcome is the outcome of the sentence at that index.

### 5.7 Extensions (`Extension.lean`)

```lean
namespace VE.Grammar

variable {T K σ ρ α : Type} [Accepts K T]
variable {G G2 : Grammar K} {μ μ2 : Meaning T σ ρ α} {emb : Tree T → Tree T}
variable {st st2 : σ} {w : List T} {A : α} {c : Bool} {t u : Tree T}

/-- A map on trees that carries derivations of `G` to derivations of `G2` of the same sentence, keeps
different derivations different, and keeps every successful meaning: the value, the conclusion mark
and the successor state, from the same initial state. -/
structure Embeds (G G2 : Grammar K) (μ μ2 : Meaning T σ ρ α) (emb : Tree T → Tree T) : Prop where
  derives : ∀ w t, Derives G (.n G.start) w t → Derives G2 (.n G2.start) w (emb t)
  injective : ∀ w t u, Derives G (.n G.start) w t → Derives G (.n G.start) w u → emb t = emb u → t = u
  meaning : ∀ st w t x, Derives G (.n G.start) w t → μ st t = .ok x → μ2 st (emb t) = .ok x

theorem extension_safe : Embeds G G2 μ μ2 emb → OneReading G μ st w A c st2 →
    OneReading G2 μ2 st w A c st2 ∨
    ∃ t u, Derives G2 (.n G2.start) w t ∧ Derives G2 (.n G2.start) w u ∧ t ≠ u

theorem extension_keeps_many : Embeds G G2 μ μ2 emb →
    Derives G (.n G.start) w t → Derives G (.n G.start) w u → t ≠ u →
    Derives G2 (.n G2.start) w (emb t) ∧ Derives G2 (.n G2.start) w (emb u) ∧ emb t ≠ emb u

/-- A map on rule indices and on nonterminals. -/
structure RuleMap where
  rule : Nat → Nat
  nt : Nat → Nat

def Sym.rename (nt : Nat → Nat) : Sym K → Sym K
  | .t a => .t a
  | .n A => .n (nt A)

/-- Renumbers the rule of every node. -/
def RuleMap.tree (e : RuleMap) : Tree T → Tree T

variable {S : Sig T} {acts acts2 : Array (Action S)} {e : RuleMap} {X : Sym K}

/-- The rule map is injective on the rules of `G`, and the image of each rule has the renamed sides
and the same action. -/
structure RuleMap.Ok (e : RuleMap) (G G2 : Grammar K) (acts acts2 : Array (Action S)) : Prop where
  start : e.nt G.start = G2.start
  injective : ∀ r r2, r < G.rules.size → r2 < G.rules.size → e.rule r = e.rule r2 → r = r2
  rules : ∀ r R, G.rules[r]? = some R → ∃ R2, G2.rules[e.rule r]? = some R2 ∧
    R2.lhs = e.nt R.lhs ∧ R2.rhs = R.rhs.map (Sym.rename e.nt) ∧ acts2[R2.act]? = acts[R.act]?

theorem rule_map_sem : e.Ok G G2 acts acts2 → t.derives G X = true →
    (e.tree t).derives G2 (X.rename e.nt) = true ∧ (e.tree t).yield = t.yield ∧
    (e.tree t).sem G2 S acts2 = t.sem G S acts

/-- A rule map induces an embedding, for any way `k` of turning a tree's value into a meaning. -/
theorem rule_map_embeds (k : σ → Option (Val S) → Except ρ (α × Bool × σ)) :
    e.Ok G G2 acts acts2 →
    Embeds G G2 (fun st t => k st (t.sem G S acts)) (fun st t => k st (t.sem G2 S acts2)) e.tree

end VE.Grammar
```

`extension_safe` uses excluded middle on "every derivation of `w` in `G2` equals the image". `Embeds.injective`
is not needed for it; it is what `extension_keeps_many` rests on, so that growth cannot hide an ambiguity.

### 5.8 The English instance (`VE/EnglishGrammar/*`)

The block begins with the tokens, the terminals and their matching (2.2, 2.3). They instantiate the engine:
an English grammar is a `Grammar Terminal`, and its trees are `Tree Tok`.

```lean
namespace VE.EnglishGrammar
open VE.Grammar

inductive Tok where
  | word (text : String) (initial : Bool)
  | quoted (name : String)
  | label (letter : String) (index : Nat)
  | numeral (value : Int)
  | punct (text : String)
  deriving DecidableEq, Repr, Inhabited

/-- The sentence terminator. The lexer never puts it inside a sentence. -/
def terminator : Tok := .punct "."

inductive TokClass where
  | numeral
  | label (letter : String)
  deriving DecidableEq, Repr

inductive Terminal where
  | kw (s : String)
  | content (s : String)
  | exact (t : Tok)
  | cls (c : TokClass)
  deriving DecidableEq, Repr

/-- ASCII letters to lower case; `İ` and `ı` to `i`, `ſ` to `s`, the Kelvin sign to `k`. -/
def foldChar (c : Char) : Char :=
  if c.isAlphanum then c.toLower
  else if c.val == 0x130 || c.val == 0x131 then 'i'
  else if c.val == 0x17F then 's'
  else if c.val == 0x212A then 'k'
  else c

def fold (s : String) : String := s.map foldChar

/-- The first character in ASCII upper case, the rest unchanged. -/
def capitalise (s : String) : String :=
  match s.toList with
  | [] => s
  | c :: cs => String.mk (c.toUpper :: cs)

def Tok.plain : Tok → Tok
  | .word text _ => .word text false
  | t => t

def TokClass.accepts : TokClass → Tok → Bool
  | .numeral, .numeral _ => true
  | .label l, .label l2 _ => l == l2
  | _, _ => false

def Terminal.accepts : Terminal → Tok → Bool
  | .kw s, .word text initial => text == s || (initial && text == capitalise s)
  | .content s, .word text _ => fold text == fold s
  | .exact t, tok => tok.plain == t.plain
  | .cls c, tok => c.accepts tok
  | _, _ => false

/-- The matching of the English instance. -/
instance : Accepts Terminal Tok := ⟨Terminal.accepts⟩

/-- W4 of the specification: no terminal of any rule accepts the terminator. -/
def terminatorFree (G : Grammar Terminal) : Bool :=
  G.rules.all fun R => R.rhs.all fun
    | .t a => !a.accepts terminator
    | .n _ => true

/-- The surface AST: the strict AST of formula-level English. Tier B: S0 closes the constructor list
against `ve/ast.py`. -/
inductive ETerm where
  | var (index : Nat)
  | const (name : String)
  | num (value : Int)
  | add (left right : ETerm)
  | scale (coefficient : Int) (term : ETerm)
  deriving DecidableEq, Repr

inductive EFormula where
  | top
  | bottom
  | pred (name : String) (args : List ETerm)
  | eq (left right : ETerm)
  | lt (left right : ETerm)
  | le (left right : ETerm)
  | not (body : EFormula)
  | and (left right : EFormula)
  | or (left right : EFormula)
  | implies (left right : EFormula)
  | all (sort : String) (body : EFormula)
  | ex (sort : String) (body : EFormula)
  | reachNamed (reflexive : Bool) (relation : String) (left right : ETerm)
  | reachBody (reflexive : Bool) (sort : String) (body : EFormula) (left right : ETerm)
  deriving DecidableEq, Repr

/-- The wire form of the strict AST. -/
def EFormula.encode : EFormula → Lean.Json

structure Env                 -- sorts, predicates with their flags and declared wordings, constants,
                              -- profiles and profile blocks, and the validated environment itself
structure Overlay             -- replaced wordings and constant display forms
structure Lexicon where
  nouns : List (String × String)              -- sort, selected noun
  letters : List (String × String)            -- sort, label letter
  wordings : List (String × String)           -- predicate, selected wording
  negatives : List (String × String)          -- predicate, selected negative
  aliases : List (String × String × Bool)     -- predicate, input wording, negated
  spellings : List (String × String)          -- constant, selected spelling

/-- The existing typed decoder of the environment's family, on the encoded document. -/
def typedDocument (E : Env) (As : List EFormula) : Bool

def wordingKey : String → String
def negativeTemplate (wording : String) (arity : Nat) : Option String
def Lexicon.valid (E : Env) (O : Overlay) (L : Lexicon) : Bool          -- V1 to V5 of 2.9

/-- The declared rejections. Tier B: S0 closes the list. -/
inductive Reject where
  | sourceTooLong | textTooLong | badCharacter (offset : Nat) | openQuote (offset : Nat)
  | badNumeral (offset : Nat) | emptyDocument | emptySentence (index : Nat) | unterminated
  | unboundReference | shadowedName | sortMismatch | markerDepth | nestingLimit | numeralBound
  | pronounUnresolved | blockedWording (id : String)
  | internal
  deriving DecidableEq, Repr

def lex : String → Except Reject (Array (Array Tok))

/-- The state of the `it` rule. `referents` is sorted and has no duplicate. -/
structure DState where
  referents : List String
  binderSeen : Bool
  deriving DecidableEq, Repr

def DState.init : DState := ⟨[], false⟩

/-- The semantic types. Tier B: S0 closes the list. -/
inductive Ty where
  | tok | sentence | formula | term | intTerm | declaration | guard | relative
  deriving DecidableEq, Repr

def sig : Sig Tok             -- `sig.Ty = Ty`, `sig.tok = .tok`, `sig.Sem .tok = Tok`,
                              -- `sig.Sem .sentence = DState → Except Reject (EFormula × Bool × DState)`

def fixedRules (profiles : List String) : Array (Rule Terminal)   -- generated table literals
def lexRules (E : Env) (L : Lexicon) : Array (Rule Terminal)
def grammar (E : Env) (L : Lexicon) : Grammar Terminal
def ty (E : Env) (L : Lexicon) : Nat → Ty
def acts (E : Env) (L : Lexicon) : Array (Action sig)
def actionsVersion : String   -- the version of every trusted definition file of the reader (2.12)

/-- The meaning of a tree: its value, when it is a sentence value, applied to the state. -/
def meaning (G : Grammar Terminal) (acts : Array (Action sig)) : Meaning Tok DState Reject EFormula :=
  fun st t => match t.sem G sig acts with
    | some ⟨.sentence, f⟩ => f st
    | _ => .error .internal

inductive GrammarFault where
  | lexicon | notWellFormed | notTyped
  deriving DecidableEq, Repr

inductive ReadOutcome where
  | ok (rs : List (EFormula × Bool))
  | invalidGrammar (why : GrammarFault)
  | lexical (r : Reject)
  | stopped (index : Nat) (o : Outcome Tok Reject EFormula)
  | illTyped

def read (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) : ReadOutcome :=
  if !L.valid E O then .invalidGrammar .lexicon
  else if !((grammar E L).wf && terminatorFree (grammar E L)) then .invalidGrammar .notWellFormed
  else if !(grammar E L).typed sig (ty E L) (acts E L) then .invalidGrammar .notTyped
  else match lex s with
    | .error r => .lexical r
    | .ok sents =>
        match readDocument (grammar E L) (meaning (grammar E L) (acts E L)) DState.init b sents.toList with
        | (.ok rs, _) => if typedDocument E (rs.map (·.1)) then .ok rs else .illTyped
        | (.stopped i o, _) => .stopped i o

/-- `rs` lists each sentence's formula with its conclusion mark. The lexicon's validity is part of
the claim. -/
def EnglishOneReading (E : Env) (O : Overlay) (L : Lexicon) (s : String) (rs : List (EFormula × Bool)) : Prop :=
  L.valid E O = true ∧
  ∃ sents st2, lex s = .ok sents ∧
    DocOneReading (grammar E L) (meaning (grammar E L) (acts E L)) DState.init
      (sents.toList.map (·.toList)) rs st2 ∧
    typedDocument E (rs.map (·.1)) = true

variable {E : Env} {O : Overlay} {L : Lexicon} {b : Nat} {s : String} {rs rs2 : List (EFormula × Bool)}
variable {G : Grammar Terminal} {st : DState} {w : List Tok} {t : Tree Tok}

theorem read_ok : read E O L b s = .ok rs → EnglishOneReading E O L s rs

theorem read_complete_english : EnglishOneReading E O L s rs →
    (grammar E L).wf = true → terminatorFree (grammar E L) = true →
    (grammar E L).typed sig (ty E L) (acts E L) = true →
    read E O L b s = .ok rs ∨ ∃ i, read E O L b s = .stopped i .budget

/-- P1, for one validated, identified lexicon. It says nothing about a second lexicon. -/
theorem english_reading_unique : EnglishOneReading E O L s rs → EnglishOneReading E O L s rs2 → rs2 = rs

/-- The start symbol of every English grammar has the type `sentence`. -/
theorem start_sentence : ty E L (grammar E L).start = .sentence

/-- For a typed grammar whose start symbol is a sentence, the meaning of a derivation is its sentence
value applied to the state: the fallback branch of `meaning` is never reached. -/
theorem meaning_total {acts : Array (Action sig)} {ty : Nat → Ty} :
    G.typed sig ty acts = true → ty G.start = .sentence → Derives G (.n G.start) w t →
    ∃ f, t.sem G sig acts = some ⟨.sentence, f⟩ ∧ meaning G acts st t = f st

/-- The check of a rendered text: reading it returns exactly these formulas and marks. -/
def checkRendering (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (rs : List (EFormula × Bool)) (s : String) :
    Bool :=
  match read E O L b s with
  | .ok rs2 => decide (rs2 = rs)
  | _ => false

theorem checked_rendering : checkRendering E O L b rs s = true → EnglishOneReading E O L s rs

end VE.EnglishGrammar
```

`meaning_total` is the totality statement for English. Its premise `ty G.start = .sentence` does not follow
from `typed`: rule typing fixes the type of each rule's two sides and says nothing about the type of the start
symbol. `start_sentence` supplies the premise for `grammar E L`. With both, a rejection is always one that an
action declared. `Reject.internal` is constructed only in the fallback branch of `meaning`; that no action
constructs it is a property of the action library, checked by its review and by a source test.

**The start type: theorem by default, check as the fallback.** S2 proves `start_sentence`. If it cannot be
proved as stated, the fallback is a check at run time, and both reviewers have approved it in advance: `read`
tests `ty E L (grammar E L).start = .sentence` together with the typing check and returns
`invalidGrammar notTyped` when the test fails, and `read_complete_english` takes that equality as one more
premise. The check runs before any meaning is evaluated. The `Internal` row of 4.2 cites whichever of the two
is used. Using the fallback is not a change of meaning that returns to the reviewers.

**W4.** `read` checks `terminatorFree` with `Grammar.wf` and reports a failure of either as
`invalidGrammar notWellFormed`. `read_complete_english` has both as premises. No statement of 5.3 to 5.7 uses
W4.

**`grammar_extension` is deferred.** Draft 1 proposed one further statement: for a relation
`Extends E L E2 L2` ("`E2`, `L2` extend `E`, `L`"), a rule map `e` exists with
`e.Ok (grammar E L) (grammar E2 L2) (acts E L) (acts E2 L2)`. `Extends` has no body, so the statement cannot
be reviewed, and the statement review accepted nothing of it. It is not a statement of this specification.
When S2 writes the body of `Extends`, with explicit preservation premises, that definition and the statement
go to the reviewers. That review covers one definition and does not block S1b. The profile case stays deferred
after that. Until a statement is accepted, `extension_safe` has no proved instance for English, and growth of
the English grammar is covered by the replay gates of the plan only.

### 5.9 The statements, in one table

| Statement | Module | Needs `wf` | Stage | Contract obligation |
|---|---|---|---|---|
| `yield_ne_nil` | `Derives` | yes | S1b | — |
| `parse_sound` | `TableProofs` | no | S1b | P2 |
| `parse_nodup`, `parse_length` | `TableProofs` | no | S1b | — |
| `parse_complete` | `TableProofs` | yes | S1b | P3 |
| `parse_mono` | `TableProofs` | no | S1b | budget rule |
| `parse_adequate` | `TableProofs` | yes | S1b | P3: not a reject-everything parser |
| `verdict_zero`, `verdict_one` | `TableProofs` | yes | S1b | P2, P3 |
| `verdict_many` | `TableProofs` | no | S1b | — |
| `sem_total` | `Meaning` | no; needs `typed` | S1b | totality of meanings |
| `read_sound`, `read_none`, `read_rejected` | `Reading` | yes | S1b | P2 |
| `read_ambiguous` | `Reading` | no | S1b | — |
| `read_complete` | `Reading` | yes | S1b | P3 within the budget |
| `one_reading_unique`, `doc_unique` | `Reading` | no | S1b | P1, generic |
| `one_reading_single`, `readings_exact` | `Reading` | the second | S1b | meaning sets |
| `doc_sound`, `doc_complete`, `doc_stopped` | `Reading` | yes | S1b | P2, P3 for documents |
| `extension_safe`, `extension_keeps_many` | `Extension` | no | S1b | conservativity, part 1 |
| `rule_map_sem`, `rule_map_embeds` | `Extension` | no | S1b | the same |
| `read_ok` | `EnglishGrammar` | checked by `read`, with W4 and `typed` | S2 | P2 for English |
| `read_complete_english` | `EnglishGrammar` | yes, with W4 and `typed`, as premises | S2 | P3 for English |
| `english_reading_unique` | `EnglishGrammar` | no | S2 | P1, per lexicon |
| `start_sentence` | `EnglishGrammar` | no | S2; the check in `read` is the approved fallback (5.8) | totality: the start type that `meaning_total` needs |
| `meaning_total` | `EnglishGrammar` | no; needs `typed` and the start type | S2 | totality |
| `checked_rendering` | `EnglishGrammar` | checked by `read` | S2 | the per-output round trip |
| `grammar_extension` | `EnglishGrammar` | — | deferred: no statement until `Extends` has a reviewed body (5.8) | conservativity for English |

In this table `wf` is `Grammar.wf`, that is W1 to W3. W4 appears only in the rows of the English instance.

### 5.10 What is not claimed

- No statement says that a grammar is unambiguous, or that any class of sentences is.
- No statement relates two lexicons.
- No statement says that `lex` agrees with Python's normalisation, or that `grammar E L` derives what Python's
  generated grammar derives. Both are measured (plan, section 5).
- No statement says that `grammar E L` is well-formed, free of the terminator or typed for every valid lexicon.
  All three are checked per request. Only the type of its start symbol is stated for every environment and
  lexicon (`start_sentence`).
- No statement says that the English grammar of a larger environment embeds the grammar of a smaller one:
  `grammar_extension` is deferred (5.8).
- No statement says that a sentence has at most one reading. The uniqueness statements say that, when a
  sentence has one reading, its result is determined.
- No statement says that the renderer produces a text that passes `checkRendering`.
- No statement covers the compiled binary, JSON decoding or the service glue.
- `EFormula.encode` and `typedDocument` are trusted links to the existing strict surface.

## 6. Files, generated artefacts and gates

| Artefact | Rule |
|---|---|
| `ve/english_grammar/<profile>.json` | the source of the fixed rules of one profile (plan 2.3; plan 7.11 is open, 11 O6) |
| generated `VE/EnglishGrammar/Fixed/*.lean` | table literals only, no theorem; `--check` in the commit hook fails on any drift |
| `ve/english_grammar/LOCK.json` | the hash of each table source and of every trusted definition file, with `actions_version` (2.12) |
| `lean/VE/Audit.lean` | one `#print axioms` line per theorem of 5.9; `lean/axioms.txt` regenerated |
| `lean/VE/Route/frozen-sources.sha256` | one line per new file, and the new hash of `Audit.lean` |
| layer map | `VE.Grammar.*` and `VE.EnglishGrammar.*` in layer 3; the service mode in layer 4 (plan 7.13) |
| `ve/assurance-manifest.json` | every new Lean file that decodes JSON is pinned; `english.admission` keeps `authority: python` until S5 |

Rules of `lean/audit.py` that this code must respect. The words it forbids are forbidden in comments and in
identifiers too; that is why a match of the rest of a rule is called a suffix entry everywhere in this
specification, and why the Lean blocks of section 5 can be copied with their comments. A theorem name has no
prime and no `?`, and stays short enough for one `#print axioms` line. After each `mutual … end` block the
namespace is closed and reopened, as `lean/VE/WireContract/Engine.lean` does.

Gates, as the plan fixes them: G1a before any proof (plan, section 5); before S1b, the statement review of
this specification with its corrections (12) and the elaboration of 5.2 to 5.7 in S1a (5.1); G1b (audit clean,
standard axioms only) for tier A; G2 for tier B. The body of `Extends` goes to the reviewers when S2 writes it
(5.8); that review does not block S1b.

## 7. What S0 and S1a deliver to this specification

| From | Delivery | Closes |
|---|---|---|
| S0 | the token rules of the lexer after the character-versus-token probes | 2.2, items 2, 4, 5; O1 to O3 |
| S0 | the constructor list of the surface AST | `ETerm`, `EFormula` |
| S0 | the classification of the 49 rejection sites; the `id` of each blocked wording | `Reject`, 4.2 |
| S0 | the list of semantic types and of actions | `Ty`, the action library |
| S0 | the sort of every lint code into subsumed, ported or retained | further conditions of `valid` (O5) |
| S0 | the tree correspondence, including the factoring of 2.10 | the G2 comparison |
| S0 | grammar sizes on synthetic limit environments | the grammar-size ceiling |
| S1a | the table type, the step counter, which charges every rule attempt, failed or not (2.6), and the measured budgets | the form of the invariant lemma; the value of `b` |
| S1a | the elaboration of 5.2 to 5.7 under Lean 4.24.0, each theorem as a definition of type `Prop`, with the list of the corrections that elaboration forced (5.1) | the Lean blocks of tier A, before S1b; a change of meaning returns to the reviewers |

Two items come back from S2: the proof of `start_sentence`, or the use of its fallback (5.8); and the body of
`Extends`, for the reviewers (5.8; O4).

## 8. Acceptance fixtures for item 1

Every fixture is an obligation on the implementation. Expected results were derived by hand from the
definitions of section 5. Trees are written `r(…)` with the rule's name and its children; a leaf is its token.

### 8.1 The engine corpus (`conformance/english-lean/engine.json`)

The engine is generic. This corpus runs it with the English tokens, terminals and matching of 5.8, and g11 to
g14 test that matching.

The grammars. Lower-case words are `kw` terminals unless marked. The start symbol is `S`.

| Grammar | Rules | Ranks |
|---|---|---|
| `G1` | `r0: S → a A`; `r1: A → b` | `S` 0, `A` 0 |
| `G2` | `r0: S → x`; `r1: S → x` | `S` 0 |
| `G3` | `r0: S → A B`; `r1: A → a`; `r2: A → a a`; `r3: B → a`; `r4: B → a a` | `S` 1, `A` 0, `B` 0 |
| `G4` | `r0: S → A B C`; `A`, `B`, `C` each `→ a` and `→ a a` (`r1` to `r6`) | `S` 1, others 0 |
| `G5` | `r0: S → A`; `r1: A → B`; `r2: B → x` | `S` 2, `A` 1, `B` 0 |
| `G6` | `r0: S → every N`; `r1: N → content "service"`; `r2: N → exact (quoted "svc")`; `r3: N → cls (label "S")`; `r4: N → cls numeral` | `S` 0, `N` 0 |

| Id | Grammar, input | Expected |
|---|---|---|
| g1 | `G1`, `a b` | `one`: `r0(a, r1(b))` |
| g2 | `G1`, `a`; `a b b`; `b a`; the empty sentence | `zero`, each |
| g3 | `G2`, `x` | `many`: `r0(x)` and `r1(x)`. Two rules equal as data are two derivations |
| g4 | `G3`, `a a` | `one`: `r0(r1(a), r3(a))` |
| g5 | `G3`, `a a a` | `many`: `r0(r1(a), r4(a, a))` and `r0(r2(a, a), r3(a))` |
| g6 | `G3`, `a a a a` | `one`: `r0(r2(a, a), r4(a, a))` |
| g7 | `G4`, `a a a a`, cap 4 | three trees, the splits 1-1-2, 1-2-1 and 2-1-1; the length 3 is below the cap, so the list is complete |
| g8 | `G4`, `a a a a`, cap 2 | two of those three trees, different from each other; `verdict` is `many` |
| g9 | `G4`, `a a a a`, cap 3 | three trees; the length equals the cap, so completeness is not concluded |
| g10 | `G5`, `x` | `one`: `r0(r1(r2(x)))`. A chain of unit rules with decreasing rank |
| g11 | `G6`, `every service`; `Every Service` with `Every` initial; `every SERVICE`; `every ſervice` | `one`, each, by `r1` |
| g12 | `G6`, `Every service` with `Every` not initial; `EVERY service` with `EVERY` initial; `every services` | `zero`, each |
| g13 | `G6`, `every "svc"`; `every S3`; `every 7` | `one`, by `r2`, `r3`, `r4` |
| g14 | `G6`, `every "SVC"`; `every T3`; `every svc` | `zero`, each |
| g15 | not well-formed, one grammar each: `S → S x` and `S → x` with any ranks; a rule with an empty right-hand side; `A → B`, `B → A`; a right-hand nonterminal at or above `rank.size`; a start symbol at or above `rank.size` | `Grammar.wf` is false, each. The W4 case is e27 (8.6) |
| g16 | `G3`, `a a a`, budgets `0, 1, 2, …` up to a budget that gives a result | no result up to some budget, then the result of g5 for every larger budget; never a shorter list |
| g17 | `S → A A A A A A A A z`, `A → a` and `A → a a`; input: forty `a` with no `z` | `zero`; the step count is below the bound of 2.6 with the constant S1a measures |
| g18 | random small grammars (at most 6 rules, right-hand sides of at most 3 symbols, 2 terminals) and every input up to length 6 | for each well-formed grammar, with cap 64: the returned trees are distinct derivations; their number is the smaller of 64 and `N`, where `N` is the number of derivations that a brute-force enumerator in the test harness finds; and when `N` is at most 64, the returned set equals the enumerated set. For each grammar that is not well-formed, every returned tree is a derivation |
| g19 | every tree returned in g1 to g18 and in g20 | `Tree.derives` is true for the start symbol and the yield is the input |
| g20 | saturation: `r0: S → A A A`; `r1: S → A A A`; `r2: A → B B`; `r3: B → a`; `r4: B → a`; ranks `S` 2, `A` 1, `B` 0; input: six `a` | the sentence has 2 · 4³ = 128 derivations. With cap 64: 64 distinct derivations; the length equals the cap, so completeness is not concluded. With cap 129: all 128 |

The brute-force enumerator of g18 is test code. It enumerates trees by size and checks each with a second
implementation of the relation, written from 2.5. The grammar of g20 is within the limits of g18, so a cap of
64 can be reached there. That is why g18 asks for set equality only when the enumerator finds at most 64
derivations.

### 8.2 Meanings

A test signature: types `tok` and `num`; `Sem num` is the natural numbers; the leaf value of a token is the
token. Grammar `GA`: `e0: E → cls numeral` with the action "the numeral's value"; `e1: E → ( E + E )` with the
action "the sum of the second and fourth arguments".

| Id | Case | Expected |
|---|---|---|
| m1 | `GA` with its two actions | `typed` is true |
| m2 | `( 1 + ( 2 + 3 ) )` | `one`; the value of the tree is 6, of type `num` |
| m3 | `GA` with the action of `e1` given three arguments | `typed` is false |
| m4 | `GA` with an action index beyond the table | `typed` is false |
| m5 | the tree of m2, valued with the action table of m3 | the value is absent; `sem_total` does not apply, because `typed` is false |

### 8.3 Sentences, documents and the state

A test meaning `μ1` on `G1`: from state `k` (a number) the value is `k`, the mark is false, the successor state
is `k + 1`. A test meaning `μ2`: the rejection `no` for every tree.

| Id | Case | Expected |
|---|---|---|
| r1 | `readSentence G1 μ1 5`, `a b` | `ok 5 false`, state 6 |
| r2 | `readSentence G1 μ1 5`, `a` | `noDerivation`, state 5 |
| r3 | `readSentence G2 μ1 5`, `x` | `ambiguous` with the two trees of g3, state 5. The meaning is not consulted |
| r4 | `readSentence G1 μ2 5`, `a b` | `rejected no`, state 5 |
| r5 | `readSentence G3 μ1 5`, `a a a`, with a budget below the threshold that g16 finds | `budget`, state 5 |
| r6 | `readDocument G1 μ1 0`, three times `a b` | `ok [(0, false), (1, false), (2, false)]`, state 3 |
| r7 | `readDocument G1 μ1 0`, `a b`, `a`, `a b` | `stopped 1 noDerivation`, state 1 |
| r8 | `readDocument G1 μ1 0`, no sentence | `ok []`, state 0 |
| r9 | a meaning that gives two trees of g5 the same value | `readSentence` is still `ambiguous`; `readingSet` over both trees has two equal members |
| r10 | translation mode: `parse G2` on `x` with cap 2, and a meaning that gives `r0(x)` a value and rejects `r1(x)` | the parser returns both trees; `readingSet` has one member, the result of `r0(x)`; `complete` is false, because the number of trees is not below the cap |

### 8.4 The lexer

| Id | Source | Expected |
|---|---|---|
| x1 | `Every service is reviewed.` | one sentence: `Every` (initial), `service`, `is`, `reviewed` |
| x2 | `Legacy is deployed.  It is reviewed.` | two sentences; `Legacy` and `It` are initial; nothing else is |
| x3 | `Therefore legacy is deployed.` | `Therefore` and `legacy` are initial |
| x4 | `It follows that Legacy is deployed.` | `It` and `Legacy` are initial; `follows` and `that` are not |
| x5 | `alice is classified as "has_owner".` | the quoted token `has_owner`; one sentence |
| x6 | `"a. b" is deployed.` | one sentence: the period inside the quotes is not a terminator |
| x7 | `For every service named S1, S1 is reviewed.` | `S1` is a label with letter `S` and index 1, twice; `,` is a punctuation token |
| x8 | `(a) x; (b) y.` and `( a ) x.` | the first has the marker tokens `(a)` and `(b)`; the second has `(`, the word `a`, `)` |
| x9 | `Every service is reviewed` | `unterminated` |
| x10 | the empty source; a source of spaces only | `emptyDocument` |
| x11 | `Alice owns legacy..` | `emptySentence`, index 1 |
| x12 | `alice is classified as "has_owner.` | `openQuote` at the offset of the quote |
| x13 | `alice owns 007.` | `badNumeral` |
| x14 | `alice owns #legacy.` | `badCharacter` at the offset of `#` |
| x17 | `ſervice café.` | one sentence of two words, `ſervice` and `café`: a character outside ASCII is a word character |
| x15 | a source of 65,537 bytes; a source of 10,001 characters after collapsing | `sourceTooLong`; `textTooLong` |
| x16 | x1 with every space replaced by a run of spaces, tabs and line breaks | the same tokens as x1 |

### 8.5 Lexicon validity

`F` is `examples/fluent/environment.json`: sorts `person` and `service`; `deployed` with wording
`{0} is deployed`; `reviewed` with `{0} is reviewed` and negative `{0} is not reviewed`; `owns` with
`{0} owns {1}` and negative `{0} does not own {1}`; constants `alice` and `legacy`. `LF` selects every declared
wording and negative, the nouns `person` and `service`, the letters `P` and `S`, and the spellings `alice` and
`legacy`. `F2` is `F` with one more predicate `audited` on `service`, declared with the wording
`{0} is reviewed`.

| Id | Environment, lexicon | Expected | Condition |
|---|---|---|---|
| v1 | `F`, `LF` | valid | |
| v2 | `F`, `LF` with `owns` moved to `{0} has the recorded relation "owns" to {1}` and its negative removed | valid | |
| v3 | `F`, as v2 but the negative `{0} does not own {1}` kept | not valid | V5 |
| v4 | `F`, `LF` with `reviewed` moved to `{0} is checked` | not valid | V2, V5 |
| v5 | `F`, `LF` with `owns` moved to `{0} owns` | not valid | V2, V3, V5 |
| v6 | `F`, `LF` with the negative of `reviewed` set to `{0} is reviewed` | not valid | V2, V5 |
| v7 | `F`, `LF` without the entry for `legacy`; `LF` with an entry for an undeclared `bob` | not valid, each | V1 |
| v8 | `F2`, `reviewed` on `{0} is reviewed` and `audited` on its fallback | not valid | V4 |
| v9 | `F2`, `audited` on `{0} is reviewed` and `reviewed` on its fallback | not valid | V4 |
| v10 | `F2`, both on their fallbacks, no negative for `reviewed` | valid | |
| v11 | `F2`, `reviewed` on `{0} is  Reviewed` (two spaces, a capital) and `audited` on its fallback | not valid: equal by `wordingKey` to the wording `audited` declares | V2, V4 |
| v12 | `negativeTemplate` on `{0} is deployed`, 1; `{0} owns {1}`, 2; `{0} has a parent {1}`, 2; `{0} carries {1}`, 2; `{0} glass {1}`, 2 | `{0} is not deployed`; `{0} does not own {1}`; `{0} does not have a parent {1}`; `{0} does not carry {1}`; none | |

### 8.6 The English reader

Under `F` and `LF`. De Bruijn index 0 is the innermost binder. Expected formulas were derived by hand from the
hand parser's source and are confirmed against Python in S2; a difference is a finding, not a failed fixture.

| Id | Source | Expected |
|---|---|---|
| e1 | `Every service is reviewed.` | `ok`: `all service (pred reviewed [var 0])`, unmarked |
| e2 | `Every service that is deployed is reviewed.` | `ok`: `all service (implies (pred deployed [var 0]) (pred reviewed [var 0]))` |
| e3 | `For every service that is deployed, there is a person who owns that service.` | `ok`: `all service (implies (pred deployed [var 0]) (ex person (pred owns [var 0, var 1])))` |
| e4 | `Alice owns legacy.` | `ok`: `pred owns [const alice, const legacy]`; the state after it has the referents `alice`, `legacy` |
| e5 | `Legacy is not reviewed.` | `ok`: `not (pred reviewed [const legacy])` |
| e6 | `Both legacy is deployed and legacy is reviewed.` | `ok`: `and (pred deployed [const legacy]) (pred reviewed [const legacy])` |
| e7 | `Legacy is deployed. It is reviewed.` | `ok`: `pred deployed [const legacy]`, then `pred reviewed [const legacy]` |
| e8 | `Alice owns legacy. It is deployed.` | `stopped 1 (rejected pronounUnresolved)`: two referents |
| e9 | `Every service is reviewed. It is deployed.` | `stopped 1 (rejected pronounUnresolved)`: no referent, and a quantifier occurred |
| e10 | `Legacy is deployed. Therefore legacy is deployed.` | `ok`, marks false and true. Whether the conclusion follows is not checked here |
| e11 | `every Service is reviewed.` | as e1: a noun matches in any case |
| e12 | `EVERY service is reviewed.` | `stopped 0 noDerivation` |
| e13 | `Every sevice is reviewed.` | `stopped 0 noDerivation` |
| e14 | `Every service is reviewed` | `lexical unterminated` |
| e15 | `For every service named S1, S1 is reviewed.` | as e1 |
| e16 | `For every service named S1, for every service named S1, S1 is reviewed.` | `stopped 0 (rejected shadowedName)` |
| e17 | `S1 is reviewed.` | `stopped 0 (rejected unboundReference)`: the sentence has one derivation, and its meaning is the rejection |
| e18 | `Alice is deployed.` | `illTyped`: one reading, and `deployed` takes a service |
| e19 | e4 under the lexicon of v2 | `stopped 0 noDerivation`; and `Alice has the recorded relation "owns" to legacy.` reads as e4's formula |
| e20 | under `F2` and the lexicon of v10: `Legacy is reviewed.`; `Legacy is classified as "reviewed".`; `Legacy is classified as "audited".` | `stopped 0 noDerivation`; `pred reviewed [const legacy]`; `pred audited [const legacy]` |
| e21 | any source, under the lexicon of v8 | `invalidGrammar lexicon`; nothing is read |
| e22 | `checkRendering` for e2's formula, unmarked, with e2's source; with e1's source; with e2's formula marked | true; false; false |
| e23 | mutation replay: e1 to e7 under the lexicon of v2 | e3 and e4, which use the wording of `owns`, lose their readings; the others keep their formulas; none gets another formula |

Environment `FA` is a `data@0` environment with one functional total relation `colour` from `service` to a sort
`shade`, a unary predicate `dark` on `shade`, and the constant `legacy`.

| Id | Source | Expected |
|---|---|---|
| e24 | `The colour of legacy is dark.` | `ok`: `ex shade (and (pred colour [const legacy, var 0]) (pred dark [var 0]))`; the derivation uses the relation rule over the property rule (2.10), and it is the only one |
| e25 | the grammar of a synthetic environment with 128 such relations and 128 properties on one value sort | at most 256 attribute and property rules; Python's grammar has 16,384 alternatives for the same pairs; each pair has one derivation in both |

Two fixtures on the checks that `read` runs before it reads, and one on translation mode. e26 and e27 use
grammars built by hand over the English tokens and terminals, not `grammar E L`. e28 is under `F` and `LF`.

| Id | Case | Expected |
|---|---|---|
| e26 | the start type. A grammar with the one rule `S → x`; the type table gives `S` the type `formula`; the action of the rule takes one `tok` argument and returns a value of the type `formula`; the sentence `x` | `typed` is true, and the sentence has one derivation. `meaning` of that derivation is the rejection `internal`: `meaning_total` does not apply, because the start type is not `sentence`. If the fallback of 5.8 is used, the start-type test is false for this grammar and type table, the outcome is `invalidGrammar notTyped`, and no meaning is evaluated |
| e27 | W4. A grammar with the one rule `S → x exact (punct ".")` | `Grammar.wf` is true and `terminatorFree` is false. This is the check that `read` reports as `invalidGrammar notWellFormed` |
| e28 | translation mode, `Legacy is deployed. Legacy is reviewed.` | `rejected` with the code `NotOneSentence`; no reading is returned and no sentence is parsed |

### 8.7 Extensions

| Id | Case | Expected |
|---|---|---|
| q1 | `G1`, and `G1` with one more rule `r2: S → c`; the identity rule map | an embedding; `a b` keeps its reading |
| q2 | `G1`, and `G1` with one more rule `r2: S → a b`; the identity rule map | an embedding; `a b` has two derivations in the larger grammar: the second branch of `extension_safe` |
| q3 | `G1`, and the same two rules in the other order; the rule map that swaps 0 and 1 | an embedding; the image of `r0(a, r1(b))` is `r1(a, r0(b))`, with the same value |
| q4 | `G1`, and `G1` with the action of `r1` replaced | `RuleMap.Ok` fails on its last clause; no embedding is claimed |
| q5 | `F` with `LF`, and `F2` with `reviewed` and `audited` on their fallbacks | not an extension: the wording of `reviewed` was reselected. `Legacy is reviewed.` loses its reading (e20) |
| q6 | `F` with `LF`, and `F` plus a predicate `archived` on `service` with wording `{0} is archived`, the other selections unchanged | an extension; e1 to e7 keep their readings |

### 8.8 Evidence

| Id | Case | Expected |
|---|---|---|
| i1 | e1, twice | the six identities are equal in both responses |
| i2 | e1 with one more space in the source | `source_sha256` differs; the other five are equal; the formulas are equal |
| i3 | e1 under `LF` and under the lexicon of v2 | `lexicon_id` differs; the other five are equal |
| i4 | a request whose caller states a `lexicon_id` that is not the digest of the lexicon it sends | the response carries the digest the service computed; the adapter fails closed on the difference |
| i5 | a change, with `actions_version` unchanged, to each of these in turn: one action of the library, `lex`, `Terminal.accepts`, `lexRules`, `Lexicon.valid`, `EFormula.encode` | the commit hook's check fails, each |
| i6 | a response with no overlay | no `overlay_digest` field; no `null` anywhere |

### 8.9 Tooling

| Id | Case | Expected |
|---|---|---|
| t1 | a rule edited in a generated Lean table, the JSON source unchanged | `--check` fails and names the profile and the rule tag |
| t2 | a theorem of 5.9 without its `#print axioms` line | the audit fails |
| t3 | a new Lean file without its line in the frozen inventory | the frozen-sources test fails |
| t4 | the engine corpus run through the service mode and through the one-shot executable | equal responses |

## 9. Limits, and what is not claimed

1. **Intent.** One reading is not the intended reading. No statement here concerns intent or source fidelity.
2. **Declared wordings.** A template is a trusted declaration. Lean cannot tell that a wording was declared for
   the wrong predicate.
3. **Per lexicon.** Every claim fixes one validated, identified lexicon (2.9).
4. **Per sentence.** No grammar is proved unambiguous (D3). The static tier of plan 3.6 is later work.
5. **The lexer is a definition.** Its agreement with Python's normalisation is measured, not proved. Tokens do
   not record adjacency (11, O1).
6. **Well-formedness is checked, not proved.** A valid lexicon whose grammar is not well-formed, has a terminal
   that accepts the terminator, or is not typed is refused as `invalidGrammar`.
7. **Meanings are code.** A wrong action gives a wrong formula with a correct uniqueness proof. The corpus
   replay, the three-way differential and the check of every rendered text are the mitigations (plan 7.5).
8. **Conclusions.** A mark is part of the reading. Whether a marked sentence follows is decided by the existing
   proof search, outside this item.
9. **Translation mode reads one sentence.** It reads exactly one sentence, from the initial state, and rejects
   a longer text (4.3). `readings_exact` is stated for one sentence and one initial state. A set of readings
   for a document, where the state after a sentence depends on which reading is chosen, is not specified.
10. **Performance.** The cost bound of 2.6 is a bound, not a measurement. G1a decides.
11. **Statement layers and display-only text** are outside item 1 (plan S6, S7).

## 10. Statement review checklist (Astra + Fable, before S1b)

The review of 2026-10-03 worked through this list on draft 1; section 12 records its result. The list is kept,
with items 1 and 2 corrected, for the DRI's check of the edits and for any return to the reviewers.

1. `Tree.derives` (5.3) is the intended grammar relation, and `Terminal.accepts` (5.8) matches 2.3 case by case.
2. W1 to W3 are what `parse_complete` needs, and nothing more is assumed. In particular W3 excludes left
   recursion and unit cycles. W4 is a check of the English instance and no statement of 5.3 to 5.7 uses it.
3. The cap invariant (2.6, `EntryOk`) is preserved by truncation, and `parse_complete` follows from it.
4. `parse_sound`, `parse_nodup` and `verdict_many` hold without well-formedness, given the last pass of 2.6.
5. `parse_mono` and `parse_adequate` together make a verdict independent of the budget.
6. `sem_total` in the tagged form is the totality the plan asks for, and `meaning_total` follows from it.
7. `OneReading` exposes the mark and the successor state; `DocOneReading` threads the state; `doc_sound`,
   `doc_complete` and `doc_stopped` are the complete correspondence (plan edit 7).
8. `Embeds` is semantic and sufficient; `RuleMap.Ok` induces it; vocabulary reselection is excluded (plan edit 5).
9. V1 to V5 are the agreed conditions; the profile exceptions of V2 and V5 are acceptable (plan edit 6; O7).
10. `EnglishOneReading` includes `Lexicon.valid`; `read_ok` and `checked_rendering` conclude formulas and marks;
    `english_reading_unique` is P1 for a fixed lexicon and claims nothing more (plan edits 6 and 7).
11. The six identities bind what was decided (2.12, plan edit 7).
12. The statuses and codes of section 4 map onto today's public codes with no public change.
13. Every name passes the audit's rules; no new name collides with `VE.English` or `VE.Discourse`.
14. The claim sentences of 3.1 and the plain-English forms of 3.3 say what the statements say, and no more.
15. The hand-derived expectations of section 8 are right, e3, e17, e24 and g7 to g9 in particular.
16. The changes to the plan's sketches listed in 11 are acceptable.

## 11. Choices this draft resolves, and open points

### 11.1 Changes to the plan's sketches

The statement review accepted R1 to R14, with R13 amended as shown. R15 and R16 are corrections of the review
itself.

| # | Plan, section 3 | This specification | Reason |
|---|---|---|---|
| R1 | `decide`, `Verdict.none` | `verdict`, `Verdict.zero`; theorems `verdict_zero`, `verdict_one`, `verdict_many` | inside the namespace `decide` would shadow the core function, and a constructor `none` under `Option` invites mistakes |
| R2 | the reader takes `ty` and `acts`; `read_sound` and `read_complete` assume `typed` | the reader takes any meaning function `μ`; no typing hypothesis | the reader does not depend on how meanings are computed; the statements are stronger and the generic layer has no English type |
| R3 | `Tree.sem : (X : Sym) → Tree → Option (SemOf ty X)` | `Tree.sem : Tree → Option (Val S)`, a value with its type; `sem_total` restated | no dependence on `ty` in the type, so the statements of 5.7 are plain equalities |
| R4 | four parser statements | plus `parse_length` and `parse_mono` | the budget rule of the verification contract: a verdict must not depend on the budget |
| R5 | `Terminal.exact` on a whole token | equality with the flag `initial` ignored | a word with its own capital must match at any position |
| R6 | token classes: numeral, coefficient, label | numeral and label | a coefficient is a numeral in a rule position |
| R7 | `Formula`, `Formula.check E []` | the surface AST `EFormula`, and the existing typed decoder of the environment's family on its wire form | several Lean formula types exist, one per family; the wire AST is the common form, and `check` mode already types it (`lean/VE/Service/Standalone.lean`, `decodeTyped`) |
| R8 | `DocOutcome` for both the fold and `read` | `DocOutcome` for the fold, `ReadOutcome` for `read` | two types |
| R9 | `Embeds G G2` with free `ty2` | `Embeds G G2 μ μ2 emb`; `RuleMap.Ok` as the inducing structure; `extension_keeps_many` added | plan edit 5; injectivity is required on derivations only |
| R10 | `extension_safe` among the English statements | in `VE/Grammar/Extension.lean` | it is generic |
| R11 | one budget | the budget is per sentence | a document's cost is then linear in its sentences, and a `budget` outcome names its sentence |
| R12 | status `invalidGrammar` | mapped to `CheckerUnavailable` at the adapter | it is a producer fault, not a fault of the text |
| R13 | case folding undecided (plan 7.12) | the discourse table, copied into the English instance (5.8), with a test that the two tables agree | the discourse files are frozen and the new modules do not import them; the table belongs with the English tokens (R15) |
| R14 | — | `read_none`, `read_ambiguous`, `read_rejected`, `doc_stopped`, `doc_unique`, `read_complete_english`, `meaning_total` added | every outcome has an exact statement, not only `ok` |
| R15 | `Tok`, `Terminal` and `Terminal.accepts` in `VE/Grammar/Basic.lean`; "no rule mentions the sentence terminator" inside `Grammar.wf` | the engine is generic in the token type `T`, the terminal type `K` and the matching `Accepts K T`; `Tok`, `TokClass`, `Terminal`, `foldChar` and W4 (`terminatorFree`) are in the English instance; `Grammar.wf` is W1 to W3; `read` checks W4, and `read_complete_english` has it as a premise | statement review: no statement of 5.3 to 5.7 inspects a token or uses W4, and O1, S6 and S7 would otherwise each edit a proved, frozen file |
| R16 | `meaning` total under `typed` alone | `start_sentence` added, with a check in `read` as the approved fallback | statement review: rule typing does not fix the type of the start symbol |

### 11.2 Open points

| # | Point | Recommendation |
|---|---|---|
| O1 | **Token adjacency.** Tokens do not record whether whitespace preceded them. `non-citizen` and `non - citizen` lex alike; Python's wording patterns accept only the first. This is the unsafe direction of plan 7.2 | keep the token type; let S0's probes and the reverse corpus's spacing mutants measure the class; if it is not empty, add a `glued` flag to `punct` before S2. The token type belongs to the English instance, so this edits no tier A file |
| O2 | **Signed numerals.** `-3` is one numeral in Python's grammar and `-` is also an operator | decide in S3 with the `order@0` rules; the token type already has integer values |
| O3 | **Whitespace table.** Python's `str.isspace` is wider than Lean's `Char.isWhitespace` | S0 fixes the table; the lexer uses a literal list |
| O4 | **`grammar_extension`.** Should S2 prove it, or is the replay gate enough for English | deferred by the statement review (5.8). Nothing is accepted until `Extends` has a body with explicit preservation premises; that definition returns to the reviewers when S2 writes it. The profile case stays deferred after that |
| O5 | **Non-ASCII wording letters.** Folding covers four characters beyond ASCII; a declared wording with other letters would match more loosely in Python | let S0's lint sort decide whether `valid` requires ASCII wordings |
| O6 | **Source of truth for fixed rules** (plan 7.11) | closed: the statement review accepted JSON with generated Lean literals |
| O7 | **Profile-fixed negatives and aliases.** V2 and V5 accept the negatives and aliases a profile block fixes; the plan debate's text of the polarity condition does not mention them. Without the exception `risk@0` would have no valid lexicon | closed: the statement review accepted them, with the fixed forms as generated data that the review of S3 reads |
| O8 | **Nouns and spellings in V4.** In draft 1 the condition named wordings, negatives and aliases of predicates only | closed by the statement review: V4 names selected nouns and constant spellings on both sides of the comparison (2.9) |
| O9 | **Translation mode over documents** (9, item 9) | this version reads one sentence and rejects a longer text (4.3). A document form stays unspecified until the IDE needs it |
| O10 | **Argument lists of actions.** Every right-hand symbol gives an argument, also a keyword. A listing rule then has about eighteen arguments | accept for S1b; S2 may split long fixed rules, which changes derivation shapes and so belongs in the tree correspondence |

## 12. Statement review response (draft 2)

The statement review of draft 1 (`manage-agents/debates/english-lean-spec/{fable,astra}.md`) converged after
round 3 on **FIX, then build**. Both reviewers keep the architecture and the formula-level scope, and both
found no change to a frozen W1/soft/P0 statement, wire form or identity. The joint position is Astra's round 2
position with the concrete forms of Fable's round 3 and the resolutions of Astra's round 3; the two round 3
texts crossed and agree. All of its corrections are in this draft.

| # | Converged correction | Where applied |
|---|---|---|
| 1 | **Generic engine.** 5.2 to 5.7 are generic in the token type, the terminal type and the matching. `Tok`, `TokClass`, `Terminal`, `foldChar` and W4 move to the English instance. `Grammar.wf` keeps W1 to W3. W4 is a check in `read`, reported as `invalidGrammar notWellFormed`, and a premise of `read_complete_english`. The W4 case of g15 moves to 8.6. Checklist item 2 names W1 to W3 | status, section 0, the tiers paragraph, D1, D14, 2.1 to 2.4, 2.13, 3.2, 4.4, 5.1 to 5.9, 8.1 (introduction, g15), 8.6 (e27), 9 (item 6), 10 (items 1, 2), 11.1 (R13, R15), O1 |
| 2 | **Elaboration.** S1a elaborates 5.2 to 5.7 under Lean 4.24.0, with each unproved statement as a definition of type `Prop`. Corrections that elaboration forces are listed; a change of meaning returns to the reviewers | status, 5.1, 6 (gates), 7 |
| 3 | **Step counter.** A failed rule attempt is charged like a combination, so the budget bounds time. G1a keeps its latency and memory gates | D6, 2.6, 7 |
| 4 | **g18 was false.** Five rules within its limits give 128 derivations of six tokens. g18 now asks for distinct derivations, the smaller of 64 and the exhaustive count, and set equality when that count is at most 64. g20 is the saturation fixture: cap 64 gives 64, cap 129 gives all 128 | 8.1 (g18, g19, g20) |
| 5 | **Start type.** `typed` says nothing about the type of the start symbol. `start_sentence` is added as an S2 theorem; a check in `read`, with one more premise of `read_complete_english`, is the approved fallback. The `Internal` row cites whichever is used. Fixture: a typed grammar whose start has the type `formula` | 2.7, 2.13, 3.3, 4.2, 5.8, 5.9, 5.10, 7, 8.6 (e26), 11.1 (R16) |
| 6 | **Identity of the definitions.** A change to `lex`, `Terminal.accepts`, `lexRules`, `Lexicon.valid` or the AST encoding could change a reading with all six identities equal. `actions_version` now covers every trusted definition file of 2.13; the lock file hashes each; i5 widens. `grammar_id` is unchanged | D11, 2.12, 4.4, 5.8 (`actionsVersion`), 6, 8.8 (i5) |
| 7 | **Paraphrases.** 2.1 speaks of derivations. `readings_exact` gains "if the grammar is well-formed". The uniqueness rows are conditional on one reading. Every retained statement of 5.9 has a row | 2.1, 3.3, 5.10 |
| 8 | **Translation mode.** It reads exactly one sentence, from the initial state; a longer text is `rejected` under the new tier B code `NotOneSentence`. `complete` is true exactly when the parser returned fewer trees than the cap. Fixture: `G2`, `x`, cap 2, a meaning that rejects `r1(x)` | 3.2, 4.1, 4.2, 4.3, 8.3 (r10), 8.6 (e28), 9 (item 9), O9 |
| 9 | **V4.** It names predicates, selected nouns and constant spellings on both sides. The contrary note is removed. O8 is closed | 2.9, 7, O8 |
| 10 | **v4, v5.** v4 also fails V5; v5 also fails V2 and V5 | 8.5 |
| 11 | **C1.** `Lean read this text and reported one reading per sentence. The reader's correctness has not yet been proved.` | 3.1 |
| 12 | **`grammar_extension`.** Deferred until `Extends` has a body with explicit preservation premises that the reviewers can assess. The profile case stays deferred | 3.3, 5.8, 5.9, 5.10, 6, 7, O4 |
| 13 | **Accepted as proposed.** O6 (JSON as the source of the fixed rules), O7 (profile-fixed negatives and aliases), R1 to R14 | 2.9 (note), 11.1, 11.2 |

Notes for the DRI's check.

- **Form of the genericity.** The joint position fixes what is generic, not how it is written. This draft uses
  two type parameters, `T` and `K`, and a class `Accepts K T` for the matching. With that form the text of every
  theorem of 5.3 to 5.7 is unchanged: only the `variable` lines and the types in the signatures differ. Another
  form with the same meaning (an explicit matching argument, a bundled structure) would be an elaboration-level
  choice for S1a.
- **Names that the joint position leaves open.** `start_sentence`, `terminatorFree`, the code `NotOneSentence`
  with its text, and the fixture numbers g20, r10, e26, e27 and e28 are chosen here.
- **V4, the two sides.** The selection side lists the selected wording, negative and aliases of a predicate,
  the selected noun of a sort and the selected spelling of a constant. The other side keeps the four declared
  items of a predicate from draft 1 and adds the declared or selected noun of a sort and the declared or
  selected spelling of a constant, of another symbol in each case.
- **Two fixtures beyond the listed ones.** e27 is the W4 case that left g15. e28 tests the new rejection of
  translation mode. Neither states anything that the joint position does not.
- **Not changed:** the propositions of the theorems of 5.3 to 5.7 (their binders name `T` and `K` where they
  named `Tok`, `Tree` and `Grammar`); `EnglishOneReading`, `read_ok`, `english_reading_unique`,
  `meaning_total`, `checkRendering` and `checked_rendering`; the lexer rules; V1 to V3 and V5; the six
  statuses; every other fixture; D2 to D5, D7 to D10, D12 and D13; the frozen W1/soft/P0 contracts.

What happens next: the DRI checks these edits against the table. S0 and S1a continue. S1b waits for the
elaboration of 5.2 to 5.7 and for G1a. A change of meaning, and the body of `Extends` when S2 writes it, go to
the reviewers.
