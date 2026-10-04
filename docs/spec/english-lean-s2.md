# English in Lean, S2: the English instance (statement specification)

> Status: statement specification, draft 1 (2026-10-04), branch `design/english-lean-s2`. This is the item-1
> statement spec of [english-lean-S2-PLAN.md](english-lean-S2-PLAN.md) draft 2 (the **S2 plan**). It writes out
> stage S2 of [english-lean-PLAN.md](english-lean-PLAN.md) (the **base plan**, draft 2) on top of
> [english-lean.md](english-lean.md) draft 2 (the **base spec**), whose tier A engine is proved and whose tier B
> lexer, tokens and `Lexicon.valid` are built on branch `english-lean/integrate` at `689219b1`
> ([english-lean-s1.md](english-lean-s1.md), the **S1 report**; [english-lean-measured.md](english-lean-measured.md),
> the **S0 report**). Base-spec definitions and statements are not repeated; a section number written `base 2.9`
> refers to the base spec. **Nothing was built for this draft.** What was run: every Lean signature and statement
> of section 5 was elaborated as a stub against the S1 build (each statement as a definition of type `Prop`, as
> base 5.1 prescribes for unproved statements), and every verdict, count and step figure of section 8 was
> computed by the proved S1 parser on the hand-built fixture grammar of 8.1, over the S1 lexer's tokens (section
> 12). Formulas in section 8 were derived by hand from `ve/english.py` and are confirmed against Python in S2; a
> difference there is a finding, not a failed fixture. Every `file:line` was read on 2026-10-04 and must be
> re-read at each step. Nothing here changes a verdict, an identity, a public code, a frozen file, an existing
> theorem statement or a checker function.

## 0. Scope, one paragraph

S2 gives the generic engine its English instance for the base profile (`relational-fol@0`): the fixed rules as
data, the lexical rules built from the validated lexicon, the action library that gives every derivation a
formula, a conclusion mark and a successor state or a declared rejection, the readers, the English theorems of
base 5.8 and five more, two service modes, the Python adapter in shadow, and the G2 harness. The constructs are
the base plan's S2 row: base constructs (atoms, negation, the compact `both`/`either`/`if` forms, the listing
forms, universals, existentials, declarations and references, labels, `it`), contractions (the `every … relative`
and `there is … who` forms), validated negatives, coordination, closure (reach), and the natural clauses. Profiles
are S3. Nothing user-visible changes: `english.admission` keeps `authority: python`.

In this specification: the decisions (1), the definitions (2), the English of every new outcome and claim (3),
the diagnostics (4), the Lean definitions and the exact statements (5), files and gates (6), what is consumed
and returned (7), the acceptance fixtures (8), limits (9), the statement review checklist (10), the open points
(11), and how the figures were computed (12).

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | `grammar E L` is `fixedRules E.profiles` followed by `lexRules E L`, in that order, with one fixed nonterminal catalogue; the start symbol is nonterminal 0, `sentence` | 2.4, 2.5, 5.6 (`grammar_rules`) |
| D2 | Every fixed rule is one row of a JSON source, generated into a Lean table literal; punctuation terminals carry the `glued` flags of DRI ruling 1, so the fixed rules accept exactly Python's spacing | 2.5, 2.9 |
| D3 | A wording becomes rules by one procedure, `lexRules`: clause, subject relative and object relative per wording, negative and alias; noun, label and spelling rules per sort and constant; the natural-view families as Python's `_natural_grammar` instantiates them | 2.6 |
| D4 | Meanings are computed bottom-up from a context (scope, state, list depth, nesting, leftmost position). Side conditions are declared rejections computed by actions; they never remove a derivation | 2.7, 2.8 |
| D5 | `start_sentence` holds by construction: `ty E L 0 = .sentence` for every environment and lexicon. The fallback check of base 5.8 is not used | 5.6, 5.7 |
| D6 | `Reject` gains `coordinationRepeated` and `naturalScoped` (tier B, for the DRI). Every other side condition of the S2 constructs maps to an existing code | 2.8 |
| D7 | Translation mode is `translate`: one sentence from `DState.init`; its set is complete exactly when the parser returned fewer trees than the cap; a text of two or more sentences is `NotOneSentence` | 2.3, 5.3, 8.4 |
| D8 | The service modes are `english.read` and `english.grammar`, in a new executable; the six identities of base 2.12 are computed by the service | 2.10, 4.3, 4.4 |
| D9 | The adapter runs under `dispatch.execute("english.admission", …)`; authority stays `python`; the shadow log is G2's instrument; `invalidGrammar` fails closed as `CheckerUnavailable` | 2.10, 4.5 |
| D10 | G2 compares verdict, formulas, canonical text, marks and witness multiplicity under the written tree correspondence; the reverse corpus is sampled from the `english.grammar` export; mutation replay is empirical | 2.11 |
| D11 | The readability writing gaps are fixtures. The two rules that would accept the two rejected sentence shapes are written, measured and excluded from the generated table until signed | 2.12, 8.5 |
| D12 | `Extends` gets a body: equal profiles, every symbol and selection kept, both lexicons valid. `grammar_extension` is stated against it for the reviewers | 2.13, 5.6 |
| D13 | All eighteen lint codes stay in the Python producer in S2. The final sort of the eight retained codes is proposed here and fixed at the statement review | 2.14 |
| D14 | Lean's texts for `none`, `many`, `rejected` and `budget` are the base spec's; the adapter's nearest-wording suggestion quotes whole tokens only | 3.2, 3.3, 4.5 |

## 2. Definitions

### 2.1 Terms

| Term | Meaning |
|---|---|
| fixed rule | a rule of the base profile that does not depend on the environment or the lexicon (2.5) |
| lexical rule | a rule built from one selection of the lexicon, or from one declaration (2.6) |
| context | what an action receives besides its children's values: the scope, the document state, the list-marker depth, the nesting depth, and whether the value is at the first token of the sentence's formula (2.7) |
| scope | the bindings in force, innermost first: pairs of a sort and a reference text (`that service`, `the first service`, `S1`) |
| side condition | a declared rejection computed by an action (2.8) |
| widening | a rule whose addition gives a derivation to a text that has none today (2.12) |
| tree correspondence | the map between a Lark derivation of Python's generated grammar and a Lean derivation of `grammar E L` (2.11) |

### 2.2 Tokens and terminals

The tokens, terminals and matching are those of the S1 build (`lean/VE/EnglishGrammar/Token.lean`): `Tok.punct`
carries `gluedBefore` and `gluedAfter`; `terminators` lists the four spacings of `.`; `terminatorFree` checks
all four. The lexer is `lex` of `Lexer.lean`.

**One proposed terminal (Q5).** Python's grammar derives a capitalised spelling of a constant whose display form
begins with `the` (`The api`) anywhere in a sentence (`english.py:1892`), and its hand parser accepts it
(`:951`). The S0 conversion dropped that alternative because `kw` already accepts the sentence-initial capital,
and recorded the mid-sentence case as a difference to dispose of in S2. A rule `exact (word "The")` would give
the sentence-initial `The api` two derivations (`kw "the"` accepts it when initial). The proposal is a fifth
terminal:

| Terminal | Accepts |
|---|---|
| `kwMid s` | a word whose text is exactly `s` and whose flag `initial` is false |

With it the spelling `the api` of a constant gives the rules `the api` (two `kw` terminals) and `kwMid "The"`,
`kw "api"`; the second never matches at a sentence start. This is a tier B change to `Terminal` and
`Terminal.accepts`; it edits no tier A file. Fixtures c1 to c3 (8.1) are obligations, not computed.

### 2.3 The reader's inputs

- **`Env`** is the lexical view of the S1 build (`Lexicon.lean`: sorts with nouns, predicates with arity,
  declared wording and negative, constants with display forms, profiles, `ProfileForms`). S2 adds one field,
  `source : Lean.Json := .null`, the validated environment JSON; `typedDocument` re-decodes the formulas against
  it through the existing typed decoder (`lean/VE/Service/Standalone.lean:331`, `decodeTyped`). S2 writes
  `Env.decode : Json → Json → Except String Env` from the environment and the overlay. For the base profile
  `forms` is empty (S3 computes the profile forms).
- **`Overlay`** and **`Lexicon`** are the S1 structures. `Lexicon.valid` is V1 to V5 of base 2.9, unchanged in
  S2 except for the proposal of 2.6 on V3.
- **The budget** `b` of `read` is `workBudget` = 2,100,000 steps per sentence (DRI ruling 5, S1 build).
- **The cap** of `translate` is the request's `cap`; `read` uses cap 2 through `verdict`.

### 2.4 Nonterminals and their types

One fixed catalogue, numbered in this order; `ty E L` is the fixed function below, independent of `E` and `L`.
The type of a nonterminal says what value a derivation of it carries (2.7).

| # | Nonterminal | `Ty` | Value |
|---|---|---|---|
| 0 | `sentence` | `sentence` | state → formula, mark, state |
| 1 | `marker` | `marker` | the mark `true` |
| 2 | `formula` | `formula` | context → formula |
| 3 | `atom` | `formula` | |
| 4 | `negation` | `formula` | |
| 5 | `compact` | `formula` | |
| 6 | `listing` | `formula` | |
| 7 | `universal` | `formula` | |
| 8 | `existential` | `formula` | |
| 9 | `coordination` | `formula` | |
| 10 | `guard` | `relative` | context → formula whose subject is `var 0` |
| 11 | `guard_relative` | `relative` | |
| 12 | `guard_atom` | `relative` | |
| 13 | `relative_pronoun` | `unit` | |
| 14 | `list_marker` | `listMarker` | the marker's text |
| 15 | `article` | `unit` | |
| 16 | `declaration` | `declaration` | context → sort and reference text |
| 17 | `term` | `term` | context → term |
| 18 | `noun` | `noun` | the sort |
| 19 | `label` | `label` | the label's text |
| 20 | `constant` | `constant` | the constant's name |
| 21 | `relative` | `relative` | |
| 22 | `object_relative` | `relative` | |
| 23 | `adjective` | `adjective` | the unary predicate's name |
| 24 | `natural` | `formula` | |
| 25 | `natural_some` | `formula` | |
| 26 | `some_tail` | `relative` | |
| 27 | `copula_relative` | `relative` | |
| 28 | `copula_adjective` | `adjective` | |
| 29 | `natural_no` | `formula` | |
| 30 | `natural_every` | `formula` | |
| 31 | `natural_tail` | `relative` | |
| 32 | `natural_subject` | `natSubject` | the adjective's predicate and the noun's sort |
| 33 | `owner_clause` | `relative` | |
| 34 | `reach` | `formula` | |
| 35 | `count` | `count` | `true` for zero or more (reflexive) |
| 36 | `relation` | `relation` | the relation's name |

`Ty` therefore gains `marker`, `unit`, `listMarker`, `noun`, `label`, `constant`, `adjective`, `natSubject`,
`count`, `relation` (tier B: base 5.8 left the list to S2). `intTerm` stays for S3. The ranks (W3) are the
certificate of 8.1: terminals-first nonterminals at rank 0; `term`, `declaration`, `some_tail`,
`natural_tail`, `natural`, `coordination` at 1; `atom`, `object_relative` at 2; `guard_atom`, `formula` at 3;
`guard_relative`, `guard`, `sentence` at 4. `Grammar.wf` of the fixture grammar is true (8.1).

### 2.5 The fixed rules of the base profile

Notation. A plain word is a `kw` terminal; `c:word` is a `content` terminal; `⟨name⟩` is a nonterminal. A comma,
semicolon or colon written attached to the symbol before it is the token `punct` with `gluedBefore` true and
`gluedAfter` false, which is how Python spaces them; `(a)` `(b)` `(i)` `(ii)` are `punct` tokens free on both
sides. The action column names the action of 2.7. The table has 88 rows; it is the source
`ve/english_grammar/relational-fol@0.json` written out (2.9). The rules come from `english_lark_grammar`
(`ve/english.py:1830–1873`) and `_natural_grammar` (`:1990–2000`), rule for rule, with the EBNF of Lark's `?`
rule expanded and the document rule removed (the lexer splits sentences; W4).

| Tag | Rule | Action |
|---|---|---|
| `sentence.plain` | `sentence → ⟨formula⟩` | `sentence false` |
| `sentence.marked` | `sentence → ⟨marker⟩ ⟨formula⟩` | `sentence true` |
| `marker.therefore` | `marker → therefore` | `mark` |
| `marker.so` | `marker → so` | `mark` |
| `marker.hence` | `marker → hence` | `mark` |
| `marker.it-follows-that` | `marker → it follows that` | `mark` |
| `formula.atom` … `formula.natural` (9 rows) | `formula → ⟨atom⟩` `⟨negation⟩` `⟨compact⟩` `⟨listing⟩` `⟨universal⟩` `⟨existential⟩` `⟨reach⟩` `⟨coordination⟩` `⟨natural⟩` | `through` |
| `negation` | `negation → it is not the case that ⟨formula⟩` | `not` |
| `compact.and` | `compact → both ⟨atom⟩ and ⟨atom⟩` | `and2` |
| `compact.or` | `compact → either ⟨atom⟩ or ⟨atom⟩, or both` | `or2` |
| `compact.if` | `compact → if ⟨formula⟩, then ⟨formula⟩` | `implies2` |
| `listing.all.words` | `listing → all of the following hold: first clause: ⟨formula⟩; end first clause; second clause: ⟨formula⟩; end second clause` | `listWords and` |
| `listing.both.words` | the same with `both of the following hold:` | `listWords and` |
| `listing.any.words` | the same with `at least one of the following holds:` | `listWords or` |
| `listing.if.words` | the same with `if the following holds:` | `listWords implies` |
| `listing.all.markers` | `listing → all of the following hold: ⟨list_marker⟩ ⟨formula⟩; ⟨list_marker⟩ ⟨formula⟩` | `listMarkers and` |
| `listing.both.markers` | the same with `both of the following hold:` | `listMarkers and` |
| `listing.any.markers` | the same with `at least one of the following holds:` | `listMarkers or` |
| `listing.if.markers` | `listing → if the following holds: ⟨list_marker⟩ ⟨formula⟩; then the following holds: ⟨list_marker⟩ ⟨formula⟩` | `listMarkers implies` |
| `marker.a` `marker.b` `marker.i` `marker.ii` | `list_marker → (a)` `(b)` `(i)` `(ii)` | `listMarker` |
| `guard.one` | `guard → ⟨guard_atom⟩` | `through` |
| `guard.two` | `guard → ⟨guard_atom⟩ and ⟨guard_relative⟩` | `guardAnd` |
| `guard.three-left` | `guard → ⟨guard_atom⟩ and ⟨guard_relative⟩, and ⟨guard_relative⟩` | `guardLeft` |
| `guard.three-right` | `guard → ⟨guard_atom⟩, and ⟨guard_relative⟩ and ⟨guard_relative⟩` | `guardRight` |
| `guard-rel.bare` `guard-rel.who` `guard-rel.that` | `guard_relative → ⟨guard_atom⟩` \| `who ⟨guard_atom⟩` \| `that ⟨guard_atom⟩` | `through` |
| `guard-atom.relative` `guard-atom.object` | `guard_atom → ⟨relative⟩` \| `⟨object_relative⟩` | `through` |
| `pronoun.who` `pronoun.that` | `relative_pronoun → who` \| `that` | `unit` |
| `universal.global` | `universal → for every ⟨declaration⟩, ⟨formula⟩` | `forallBody` |
| `universal.guard` | `universal → for every ⟨declaration⟩ ⟨relative_pronoun⟩ ⟨guard⟩, ⟨formula⟩` | `forallGuardBody` |
| `universal.relative` | `universal → every ⟨declaration⟩ ⟨relative⟩` | `forallRel` |
| `universal.guard-relative` | `universal → every ⟨declaration⟩ ⟨relative_pronoun⟩ ⟨guard⟩ ⟨relative⟩` | `forallGuardRel` |
| `existential.global` | `existential → there is ⟨article⟩ ⟨declaration⟩ such that ⟨formula⟩` | `existsBody` |
| `existential.who` `existential.that` | `existential → there is ⟨article⟩ ⟨declaration⟩ who ⟨relative⟩` \| `… that ⟨relative⟩` | `existsRel` |
| `article.a` `article.an` | `article → a` \| `an` | `unit` |
| `declaration.noun` | `declaration → ⟨noun⟩` | `declThat` |
| `declaration.first` `.second` `.third` | `declaration → c:first ⟨noun⟩` \| `c:second ⟨noun⟩` \| `c:third ⟨noun⟩` | `declOrdinal` |
| `declaration.named` | `declaration → ⟨noun⟩ c:named ⟨label⟩` | `declNamed` |
| `term.constant` | `term → ⟨constant⟩` | `termConst` |
| `term.it` | `term → it` | `termIt` |
| `term.that` | `term → c:that ⟨noun⟩` | `termRef "that"` |
| `term.the-first` `.the-second` `.the-third` | `term → c:the c:first ⟨noun⟩` … | `termRef "the first"` … |
| `term.label` | `term → ⟨label⟩` | `termLabel` |
| `atom.top` | `atom → this holds in all cases` | `top` |
| `atom.bottom` | `atom → this is impossible` | `bottom` |
| `atom.eq` | `atom → ⟨term⟩ c:is c:the c:same c:as ⟨term⟩` | `eq` |
| `coordination.subject-and` | `coordination → ⟨constant⟩, ⟨constant⟩ and ⟨constant⟩ are ⟨adjective⟩` | `coordSubjects and` |
| `coordination.subject-or` | `coordination → ⟨constant⟩, ⟨constant⟩ or ⟨constant⟩ is ⟨adjective⟩` | `coordSubjects or` |
| `coordination.predicate-and` | `coordination → ⟨constant⟩ is ⟨adjective⟩, ⟨adjective⟩ and ⟨adjective⟩` | `coordAdjectives and` |
| `coordination.predicate-or` | `coordination → ⟨constant⟩ is ⟨adjective⟩, ⟨adjective⟩ or ⟨adjective⟩` | `coordAdjectives or` |
| `natural.some` `natural.no` `natural.every` | `natural → ⟨natural_some⟩` \| `⟨natural_no⟩` \| `⟨natural_every⟩` | `naturalTop` |
| `natural-some` | `natural_some → some ⟨declaration⟩ ⟨some_tail⟩` | `someDecl` |
| `some-tail.relative` | `some_tail → ⟨relative⟩` | `through` |
| `some-tail.two` | `some_tail → ⟨relative⟩ and ⟨relative⟩` | `relAnd` |
| `some-tail.copula` | `some_tail → ⟨copula_relative⟩ and ⟨copula_adjective⟩` | `copulaAnd` |
| `natural-no` | `natural_no → no ⟨declaration⟩ ⟨relative⟩` | `noDecl` |
| `natural-every.subject` | `natural_every → every ⟨natural_subject⟩ ⟨natural_tail⟩` | `everySubject` |
| `natural-every.owner` | `natural_every → every ⟨declaration⟩ ⟨owner_clause⟩` | `everyOwner` |
| `natural-tail.relative` `natural-tail.owner` | `natural_tail → ⟨relative⟩` \| `⟨owner_clause⟩` | `through` |
| `natural-tail.both` | `natural_tail → ⟨relative⟩ and ⟨owner_clause⟩` | `relAnd` |
| `reach.named` | `reach → starting from ⟨term⟩, ⟨term⟩ is reachable by ⟨count⟩ or more ⟨relation⟩ steps` | `reachNamed` |
| `reach.body` | `reach → starting from ⟨term⟩, ⟨term⟩ is reachable by ⟨count⟩ or more steps, where a step from ⟨article⟩ ⟨declaration⟩ to ⟨article⟩ ⟨declaration⟩ satisfies this condition: ⟨formula⟩` | `reachBody false` |
| `reach.body.listed` | the same with `satisfies the following: (a) ⟨formula⟩` | `reachBody true` |
| `count.one` `count.zero` | `count → one` \| `zero` | `count false` \| `count true` |

Three remarks. The `formula → natural` row is in the fixed table because Python's natural hook extends `formula`
(`english.py:1990`); its scope restriction is a side condition (2.8, `naturalScoped`). The three-atom guards keep
Python's two associations (`guard`, `:1286–1293`): `a and b, and c` is `And (And a b) c`, `a, and b and c` is
`And a (And b c)`. The longest fixed right-hand side has 28 symbols (`listing.*.words`), as S0 measured over
tokens.

### 2.6 The lexical rules

`lexRules E L` appends, in the order of the lexicon's lists, the rules below. A wording's text is lexed by `lex`
(with a terminator appended); its word tokens become `content` terminals, a quoted part an `exact` quoted token,
a punctuation token an `exact` punctuation token with its flags, and a hole `{k}` the nonterminal `term` (the
slot's sort is an integer sort only under `order@0`, S3). `action` constructors are those of 2.7.

| Family | For | Rules | Action |
|---|---|---|---|
| clause | every selected wording, negative and alias of a predicate `p` of arity `k` | `atom → w₀ ⟨term⟩ w₁ … ⟨term⟩ wₖ` with the holes in the wording's order | `pred p order negated` |
| subject relative | the same, when `{0}` is the first symbol | the clause without its leading `⟨term⟩`: `relative → w …` | `relSubject p order negated` |
| object relative | the same, for binary wordings ending in ` {1}` | the clause without its trailing `⟨term⟩`: `object_relative → ⟨term⟩ w …` | `relObject p negated` |
| noun | every sort `s` with selected noun `n` | `noun → c:n₁ … c:nₘ` | `noun s` |
| label | every sort `s` with letter `ℓ` | `label → cls (label ℓ)` | `label` |
| spelling | every constant `c` with selected spelling `sp` | `constant → sp` (one `kw` per word; a quoted spelling is one `exact` quoted token); when `sp` is one lower-case word, also `constant → the sp`; when `sp` begins with `the `, also the capitalised spelling (2.2, Q5) | `const c` |
| adjective | every unary `p` whose selected wording is `{0} is a` with `a` one lower-case ASCII word | `adjective → c:a` | `adjective p` |
| natural subject | every such `p` on a sort `s` that has a selected noun `n` | `natural_subject → c:a c:n₁ … c:nₘ` | `natSubject p s` |
| copula | the same `p` | `copula_relative → c:is c:a`; `copula_adjective → c:a` | `copulaRel p`; `adjective p` |
| owner | when a binary predicate named `owns` has the selected wording `{0} owns {1}` | `owner_clause → has an owner` | `owner` |
| relation | every binary predicate whose two argument sorts are equal | `relation → exact (quoted name)` | `relation name` |

Conditions, as Python's: the adjective, natural-subject and copula families exist only for wordings of the form
`{0} is a` with `a` matching `[a-z]+` (`english.py:1946–1950`, `:1978–1986`); the owner clause only for that
exact wording (`:1987–1989`); the relation family only for equal argument sorts (`:1899–1900`). A sort without a
selected noun has no noun rule and no natural subjects; a lexicon that passes V1 gives every sort a noun.

**Proposal on V3 (Q6).** A wording whose text does not lex as exactly one sentence of word, quoted and
punctuation tokens other than a terminator (for example one containing `.`) gives no rule. To make this a
validity condition instead of a silent omission, V3 is strengthened: "the wording, with its holes replaced by a
space, lexes as one sentence with no terminator inside". `lexRules_terminatorFree` (5.6) then holds for every
lexicon, valid or not, because `lexRules` skips such wordings; the condition makes the skip visible as
`invalidGrammar lexicon`. Python's `PHRASE_SYNTAX` lint already refuses such wordings, so no corpus lexicon
changes class (S0 report, section 6).

### 2.7 The action library

**Context.** `Ctx` has the scope (innermost binding first), the document state `st : DState`, the list-marker
depth, the nesting depth, and `leftmost : Bool`: whether the value's first token is the first token of the
sentence's formula. An action passes its context to its children; `leftmost` stays true only for the first
child when the parent's is true and no terminal precedes it. A `formula` value is a function from the context
to a formula or a rejection; a `relative` value is the same with the subject being `var 0` of the context's
scope; a `term` value gives a term; a `declaration` value gives the binding it introduces.

**State.** `DState` is the S1 structure: `referents`, the constants mentioned in earlier sentences, sorted,
without duplicates; `binderSeen`, whether an earlier sentence had a quantifier. The `sentence` action returns
the state `after A`: referents joined with the constants of `A`, `binderSeen` or-ed with "A has a binder"
(`english.py:1623–1624`).

**The `it` rule** (`english.py:957–961`, `:1069–1073`, `:1376–1378`): `termIt` returns `const c` when
`leftmost` is true, the scope is empty, `st.referents = [c]` and `st.binderSeen` is false; otherwise it rejects
with `pronounUnresolved`. Because `leftmost` is false after any terminal, `it` can only be the subject of a
top-level clause or equality at the start of the formula, as in Python.

**The actions.** Each row gives the argument types in rule order (a terminal child has type `tok` and is
ignored unless named), the result, and the value. Scope-extending actions push the binding at index 0 and shift
nothing else: formulas use de Bruijn indices, 0 the innermost (`ETerm.var`).

| Action | Arguments → result | Value |
|---|---|---|
| `sentence m` | `formula → sentence` | from `st`: run the formula in the initial context (empty scope, `st`, depth 0, nesting 1, leftmost true); result `(A, m, st.after A)` |
| `mark`, `unit`, `listMarker` | terminals → `marker`, `unit`, `listMarker` | the mark; nothing; the marker's text |
| `through` | `X → X` | the child's value |
| `not` | `formula → formula` | `not A`, the child at nesting + 1, leftmost false |
| `and2`, `or2`, `implies2` | `formula, formula → formula` | `and A B` etc.; both children leftmost false, nesting + 1 |
| `listWords k`, `listMarkers k` | two formulas (and two markers) → `formula` | `k A B` with both children at depth + 1, nesting + 1; `listMarkers` first checks the markers: at even depth they must be `(a)` and `(b)`, at odd depth `(i)` and `(ii)` (`_markers`, `english.py:564`), else `markerDepth` |
| `guardAnd`, `guardLeft`, `guardRight`, `relAnd` | relatives → `relative` | `and a b`; `and (and a b) c`; `and a (and b c)`; `and a b` |
| `forallBody` | `declaration, formula → formula` | push the binding; `all s B` |
| `forallGuardBody` | `declaration, unit, relative, formula → formula` | push; `all s (implies G B)` |
| `forallRel`, `forallGuardRel` | as above with a relative body | `all s R`; `all s (implies G R)` |
| `existsBody`, `existsRel` | `unit, declaration, formula/relative → formula` | push; `ex s B` |
| `declThat`, `declOrdinal o`, `declNamed` | `noun → declaration`; `tok, noun`; `noun, tok, label` | the binding `(s, "that " ++ n)`, `(s, "the " ++ o ++ " " ++ n)`, `(s, label text)`; if the reference text is already in the scope, `shadowedName` (`english.py:942–943`) |
| `termConst c`, `termLabel`, `termRef pre` | → `term` | `const c`; the innermost binding whose reference text is the label's text, or `pre ++ " " ++ noun`, as `var i`; none: `unboundReference` |
| `termIt` | → `term` | the `it` rule above |
| `top`, `bottom`, `eq` | → `formula` | `top`; `bottom`; `eq t u` (the left term keeps `leftmost`) |
| `pred p order negated` | terms → `formula` | `pred p args` with the arguments in declaration order (the wording's hole order permutes them); `not` of it when negated; the first term keeps `leftmost`, later terms get false |
| `relSubject p order negated`, `relObject p negated` | terms → `relative` | as `pred` with `var 0` in the subject slot, or in the object slot |
| `noun s`, `label`, `const c`, `adjective p`, `natSubject p s`, `relation r`, `count refl` | terminals → their type | the datum |
| `coordSubjects k` | `constant ×3, adjective → formula` | `k (pred p [c₁]) (k (pred p [c₂]) (pred p [c₃]))` (`english.py:1597–1599`); the three constants distinct, else `coordinationRepeated`; each constant's sort equal to `p`'s argument sort, else `sortMismatch` |
| `coordAdjectives k` | `constant, adjective ×3 → formula` | `k (pred p₁ [c]) (k (pred p₂ [c]) (pred p₃ [c]))`; the three predicates distinct, else `coordinationRepeated`; sorts as above |
| `naturalTop` | `formula → formula` | the child; if the scope is not empty, `naturalScoped` (`english.py:1967–1968`) |
| `someDecl` | `declaration, relative → formula` | push; `ex s T` |
| `copulaAnd` | `relative, adjective → relative` | `and R (pred a [var 0])`; `a`'s sort must be the scope's innermost sort, else `sortMismatch` (`english.py:1491–1498`) |
| `noDecl` | `declaration, relative → formula` | push; `not (ex s R)` |
| `everySubject` | `natSubject, relative → formula` | push `(s, "that " ++ noun)`; `all s (implies (pred p [var 0]) T)`; if `T` is `not _` from a `natural-tail.relative`, `blockedWording "natural-negation"` (`english.py:1539–1540`) |
| `everyOwner` | `declaration, relative → formula` | push; `all s O` |
| `owner` | → `relative` | `ex s' (pred owns [var 0, var 1])` where `s'` is the first argument sort of `owns`; its second argument sort must be the scope's innermost sort, else `sortMismatch` (`english.py:1555–1558`) |
| `reachNamed` | `term, term, count, relation → formula` | `reachNamed refl r t u` |
| `reachBody listed` | `term, term, count, unit, declaration, unit, declaration, formula → formula` | both declarations the same sort, else `sortMismatch` (`english.py:1472`); push source then destination; `reachBody refl s B t u`; the body at depth + 1 when `listed` |

Every action increments nothing but what is named; a formula action rejects with `nestingLimit` when the
nesting depth exceeds 64 (`MAX_DEPTH`; `english.py:1370–1371`). `textTooLong` is the lexer's. No action
constructs `Reject.internal` (a source test, 5.7).

### 2.8 Side conditions

The S1 `Reject` list (`Syntax.lean`) with two additions, both tier B and for the DRI:

| Code | When | Python today |
|---|---|---|
| `coordinationRepeated` | a coordination names one constant, or one adjective, twice | `coordination` returns nothing; the text falls to `unknown_atom`: `SyntaxError` |
| `naturalScoped` | a natural clause under a binder | `_natural_parser` returns nothing when the scope is not empty; the generic forms then fail: `SyntaxError` |

Both map onto `SyntaxError`, so the public code does not change (D12 of the base spec). The S2 constructs use
these existing codes: `shadowedName`, `unboundReference`, `pronounUnresolved`, `sortMismatch`, `markerDepth`,
`nestingLimit`, `blockedWording "natural-negation"`.

### 2.9 The fixed-rule source, the generator and the lock file

`ve/english_grammar/relational-fol@0.json` is an array of rows `{"tag", "lhs", "act", "rhs", "status"?}`. `lhs` is
a nonterminal name of 2.4; `act` an action name of 2.7 with its data (`{"act": "listWords", "kind": "and"}`);
`rhs` a list of: a string (a `kw` terminal); `{"c": word}` (content); `{"p": text, "before": bool,
"after": bool}` (punctuation with its flags; the flags default to false); `{"q": name}` (a quoted identifier);
`{"cls": "numeral"}` or `{"cls": "label", "letter": "S"}`; `{"n": name}` (a nonterminal). A row with
`"status": "proposed"` is kept in the source and excluded from the generated table (2.12). The generator
`tools/english_grammar_gen.py` writes `lean/VE/EnglishGrammar/Fixed/RelationalFol.lean` (an `Array (Rule
Terminal)` literal and the nonterminal names) and, with `--check`, fails on any drift, naming the profile and the
first differing tag. `ve/english_grammar/LOCK.json` holds the SHA-256 of each table source and of every trusted
definition file of base 2.13 and 2.12, with `actions_version`; the commit hook fails when a hash changes and the
version does not (fixture i5).

### 2.10 Service, adapter and identities

- **Executable.** `lean_exe ve_english_route`, root `EnglishMain.lean` (`Main.lean` is frozen). Modes:
  `english.read` (request: environment, overlay or none, lexicon, source, mode `authoring` or `translation`,
  cap; response: base 4.3) and `english.grammar` (4.4). The service caches `grammar E L` by `environment_id`
  and `lexicon_id`.
- **Identities** (base 2.12): computed by the service from the request it decided; `lexicon_id` under
  `ve-english-lexicon-v1` as `conformance/english_lean_lexicon.py` already computes it; `grammar_id` under
  `ve-english-grammar-v1` over the profile names and the SHA-256 of each table source; `actions_version` the
  constant `actionsVersion` of the lock file.
- **Adapter.** `ve/backends/english_lean.py` builds the request from the environment, the overlay options and
  Python's `EnglishVocabulary` (exported as the lexicon by `conformance/english_lean_lexicon.py`'s export, moved
  under `ve/`), calls the service through `LeanService` (`ve/backends/lean_service.py`), and returns the public
  result type of `parse_english`. `_parse_english_document_uncached` (`ve/english.py:1636`) runs under
  `dispatch.execute("english.admission", payload, python=…, lean=…)`. Under the default authority nothing
  changes. Under `VE_AUTHORITY_OVERRIDES=english.admission=shadow` the Python result is returned and every
  difference is recorded in `ve-shadow.jsonl` with the classes of `dispatch._classes`, plus the fields of 4.5.
  Under `lean` authority (not in S2), an `invalidGrammar` response is `CheckerUnavailable`.

### 2.11 The G2 harness

**Tree correspondence.** A Lark derivation of `english_lark_grammar(env)` corresponds to the Lean derivation
obtained by: replacing the document rule by the lexer's sentence split; replacing each phrase terminal by its
word tokens in place (`kw` for case-sensitive words, `content` for case-insensitive, `exact` for quoted and
punctuation tokens with the flags of the spacing Python's regex accepts); replacing `LABEL`, `NUMERAL` and
`INT_OP` by the token-class rules; dropping rules over `IMPOSSIBLE`; mapping the capitalised constant duplicate
onto the `kwMid` rule (2.2); and mapping the nonterminals of Lark's EBNF expansion (`?formula` inlining, the
`__start_plus_0` document rule) onto the catalogue of 2.4. These are the rules of `conformance/english_lean_tokens.py`
(S0 report, section 7) with the `kwMid` case added. Two derivations correspond one to one under it, so the
witness multiplicity (zero, one, two or more) is compared directly.

**Comparison** (`conformance/english_lean_g2.py`), per text of the sealed corpus (`conformance/english-lean/corpus-seal.json`,
checked first with `english_lean_seal.py --check`): Python's outcome (class, formulas in wire form, canonical
strict text, conclusion indices, witness count from the Lark forest) against Lean's (status, `ast`, `canonical`,
`conclusions`, witness count). Agreement is the base plan's comparison rule (section 5): equal formulas, canonical
text, identities and marks when both accept; mapped classes when both reject (base 4.1); wall-clock
`ResourceLimit` excluded and listed. Everything else is a difference, closed only as a Lean fix, a Python fix or
a recorded product decision.

**Reverse corpus** (`conformance/english_lean_reverse.py`): from the `english.grammar` export, derivations are
sampled by bounded size (depth at most 6, at most 60 tokens) uniformly over rule choices with a fixed seed, the
yield is spelled as text (one space between tokens except at glued punctuation; the first word capitalised;
terminator appended), and each text gets two mutant families: spacing (a space inserted before or removed after
each `,` `;` `:`) and word split (one word cut into two at a random position). Each text and mutant is read by
Lean and by Python (`parse_english`, and the Lark audit alone). A text Lean accepts and Python rejects is the
unsafe direction and a difference; a mutant that either side accepts is a difference. 5,000 texts per
configuration (S0 report, section 10).

**Lexicon mutation replay** (`conformance/english_lean_mutate.py`): for each corpus environment and each symbol
with more than one honest wording (declared, mechanical, fallback; the negative dropped when the positive
changes), the lexicon with that one selection changed is validated and, when valid, the environment's corpus
texts are read again. A text may become `none` or `rejected`; a text that gets a different formula is a
difference. Empirical (base 2.4).

**Three-way differential.** On the 57,765 core texts of `conformance/english-lean-report.json`, Python, the W7
reader and `english.read` must agree on acceptance and formulas.

**Budgets owed from G1a:** the BlueDot document through `english.read` ≤ 1 s warm; `lake build` of the generated
modules ≤ 60 s. Met, or a reviewed revision.

### 2.12 The readability writing gaps

The readability evaluation (`experiments/readability-sonnet/RESULTS.md`, 2026-10-03) found four writing gaps; the
DRI made them fixtures of this stage (ARCH-ROADMAP, "English grammar coverage").

| Gap | Text | Today | In this stage |
|---|---|---|---|
| W14 | `Every service is deployed or reviewed, or both.` | no derivation; Python: `Expected '.' here` | fixture b27 (zero); widening rules `widen.or-both.adjectives` (`atom → ⟨term⟩ is ⟨adjective⟩ or ⟨adjective⟩, or both`) and `widen.or-both.relative` (`relative → is ⟨adjective⟩ or ⟨adjective⟩, or both`), action `orAdjectives`: `or (pred a [t]) (pred b [t])`; fixture w1 (one) |
| W08 | `For every person, if that person was born … and that person is subject …, then that person is a citizen ….` | no derivation; Python: `Expected ', then ' here` | fixture b28 (zero); widening rule `widen.if-and-then` (`compact → if ⟨atom⟩ and ⟨atom⟩, then ⟨formula⟩`), action `implies (and A B) C`; fixture w2 (one) |
| W12 | `No service that is deployed is not reviewed.` | no derivation; Python: `Unknown English phrase 't'` | fixture b29 (zero), with and without the widenings (w7); the fix is the diagnostic of 3.3, not a rule: the shape `no ⟨declaration⟩ ⟨relative_pronoun⟩ ⟨guard⟩ ⟨relative⟩` is not proposed here, because its meaning with a negative relative (`not (ex s (and G (not R)))`) and Python's `natural-negation` block need a product decision first |
| W02 | a prohibition written as an exception to a declared default (`Rule 2 (exception to rule 1).` with no rule 1) | `Expected Rule 1 with its own block` | a statement-layer (`norms@0`) message, outside formula-level English: recorded as fixture n1 for E3, not S2 |

The three widening rules are rows of the JSON source with `"status": "proposed"` (2.9) and are not in the
generated table. Their effect is measured in 8.5: each gap sentence gets exactly one derivation and no fixture of
8.1 changes verdict in the sample. Accepting them is a signed widening under SEMANTICS-MIGRATION-PLAN 2.3; it is
not parity and not an S2 decision (S2 plan, Q1).

### 2.13 Extensions: the body of `Extends`

`Extends E O L E2 O2 L2` holds when: the profiles of `E` and `E2` are equal; every sort of `E` is a sort of `E2`,
every predicate of `E` a predicate of `E2` with the same arity, every constant of `E` a constant of `E2`; every
entry of `L` (noun, letter, wording, negative, alias, spelling) is an entry of `L2`; and `L` is valid for `E`,
`O`, and `L2` for `E2`, `O2`. Under it, `fixedRules` is the same array and every lexical rule of `L` is a lexical
rule of `L2` with the same action, so a rule map exists (`grammar_extension`, 5.6): `e.nt` is the identity (the
catalogue of 2.4 is fixed in S2; S3's per-sort property nonterminals revisit this) and `e.rule` sends each rule
index of `grammar E L` to the index of the same rule in `grammar E2 L2`. Reselecting a wording breaks `lexiconSub`
(q5); adding a predicate with its own wording keeps it (q6). The profile case stays deferred (base O4).

### 2.14 The lint codes: the proposed final list

DRI ruling 4 fixes the final list at this statement review; LEAN-FIRST DRI answer 5 gives the rule: a retained
code that changes accept/reject protects the one-reading promise and becomes a Lean acceptance check; a purely
stylistic one becomes a Python editor warning that never rejects. In S2 all eighteen codes stay in the Python
producer, so no text widens. The proposal, for E2:

| Code | Group | Why |
|---|---|---|
| `LOGICAL_WORD` | Lean (V6) | a wording containing `and`, `or`, `not`, `every`, `if` reads as logical structure that it does not have |
| `NEGATED_HEAD` | Lean (V6) | `un-`/`non-` plus another predicate's head reads as that predicate's negation |
| `SYMBOL_COLLISION` | Lean (V6) | a wording containing another symbol's name or head reads as about that symbol |
| `BINARY_AUXILIARY` | Lean (V6) | a passive wording reads with its arguments reversed |
| `BINARY_CONVERSE` | Lean (V6) | a wording ending in `by`, `to`, `of` reads with its arguments reversed |
| `TEMPLATE_SHAPE`, hole order | Lean (V3) | `{1} … {0}` reads with its arguments reversed |
| `TEMPLATE_LENGTH` | Python warning | size and style only |
| `BINARY_VERB` | Python warning | style: a present-tense verb first |
| `IDIOM_UNRELATED` | Python warning | the honesty of a declared template is a trusted declaration either way (base 9, item 2) |

### 2.15 What is trusted, proved and tested in this stage

| Layer | Items added by S2 |
|---|---|
| Trusted definitions | the fixed-rule data of 2.5 (JSON source and generated literal); `lexRules`; `ty`; the action library and `meaning`; `Env.decode`; `EFormula.encode`; `typedDocument` as a link to the existing typed decoder |
| Proved | `read_ok`, `read_complete_english`, `read_stopped`, `english_reading_unique`, `start_sentence`, `meaning_total`, `checked_rendering`, `checked_rendering_exact`, `translate_exact`, `translate_one_sentence`, `grammar_rules`, `lexRules_terminatorFree`; `grammar_extension` once its premise is accepted |
| Checked per request | `Lexicon.valid`, `Grammar.wf`, `terminatorFree`, `Grammar.typed` |
| Tested only | the fixed table against the JSON source; the fixtures of section 8; the G2 comparison, reverse corpus and mutation replay; `Reject.internal` unconstructed; the wire form of `EFormula.encode` against Python's |

## 3. English: one reading each

### 3.1 The claim sentences

Unchanged from base 3.1: C1 until the theorems of 5.6 are in the audit inventory, then C2; C4 with any mark. S2
adds no claim sentence. The adapter attaches none in S2: records keep `python:surface`.

### 3.2 The outcomes

Unchanged from base 3.2. Two rejection texts are added (4.2):

| Code | Text |
|---|---|
| `CoordinationRepeated` | `Sentence {i} lists the same name or the same property twice in one list.` |
| `NaturalScoped` | `Sentence {i} uses a some, no or every clause inside another clause. Write it with for every or there is.` |

### 3.3 The diagnostics the readability gaps asked for

| Gap | What the reader says | What the adapter says |
|---|---|---|
| W12 | `Sentence 1 has no reading with the current vocabulary.` (`none`) | Python's nearest-wording suggestion, with the quoted phrase cut at token boundaries of the lexer: never a fragment of a word such as `'t'` (fixture g1) |
| W14, W08 | the same `none` text | the same suggestion rule; when the proposed rules are signed, `one` |
| W02 | outside S2 | `Expected Rule 1 with its own block` is a `norms@0` message; E3 ports it (fixture n1 records the text) |

### 3.4 The theorems, in plain words

| Statement | Plain English | It does not say |
|---|---|---|
| `read_ok`, `read_complete_english`, `english_reading_unique`, `start_sentence`, `meaning_total`, `checked_rendering` | base 3.3 | base 3.3 |
| `read_stopped` | If the English reader stops at a sentence, the lexicon was valid and the grammar passed its checks, every sentence before that one has one reading in order, and the reported outcome is the reader's outcome for that sentence from the state the earlier sentences leave; it is not an acceptance. | anything about later sentences |
| `checked_rendering_exact` | The check of a rendered text succeeds exactly when reading the text returns exactly the given formulas and marks. | that the renderer produces such a text |
| `translate_exact` | If translation mode returns a complete set for a text, the text is one sentence and the set lists exactly the results of the derivations of that sentence that have a meaning from the initial state. | anything when the set is not complete |
| `translate_one_sentence` | If a text has a number of sentences other than one and the checks pass, translation mode reports that it reads exactly one sentence. | |
| `grammar_rules` | The rules of the English grammar are the fixed rules of the profiles followed by the lexical rules. | |
| `lexRules_terminatorFree` | No lexical rule has a terminal that accepts a sentence terminator. | anything about the fixed rules: they are checked by `read` |
| `valid_iff_no_failure` | A lexicon is valid exactly when its list of failed conditions is empty. | |
| `grammar_extension` | If an environment and lexicon extend another (same profiles, every symbol and selection kept, both valid), there is a rule map from the smaller grammar into the larger that keeps every rule's sides and action. | anything about profiles; anything when a wording was reselected |

## 4. Diagnostics

### 4.1 Statuses

Base 4.1, unchanged. `translate`'s `notOneSentence` is status `rejected` with code `NotOneSentence`; its
`budget` is status `budget`.

### 4.2 Rejection codes added

| Code | Text | Python today |
|---|---|---|
| `CoordinationRepeated` | 3.2 | `SyntaxError` (unknown phrase) |
| `NaturalScoped` | 3.2 | `SyntaxError` |

### 4.3 The response

Base 4.3, with two fields made exact: `derivation` and `witnesses` list, per tree, the rule tags along a
pre-order walk with each node's token span `[start, end)` in the sentence; `readings` lists, per result, the
formula in wire form, the mark and the successor state's `referents` and `binderSeen`.

### 4.4 The `english.grammar` export

```json
{"identities": {…the six…},
 "nonterminals": ["sentence", "marker", …],
 "ranks": [4, 0, …],
 "rules": [{"index": 0, "tag": "sentence.plain", "lhs": "sentence", "act": "sentence false",
            "rhs": [{"n": "formula"}]}, …]}
```

`rhs` uses the symbol encoding of 2.9, with `{"p": …}` carrying both flags always. The rules are in the order
of `grammar E L`, so `index` is the rule index that `derivation` and `witnesses` name.

### 4.5 Tool, adapter and shadow diagnostics

| Tool | Failure | Message names |
|---|---|---|
| `tools/english_grammar_gen.py --check` | a generated table differs from its source; a `proposed` row is in the table | the profile and the first differing tag |
| the same | a lock-file hash differs with `actions_version` unchanged | the file and the two hashes |
| adapter | `invalidGrammar` | `CheckerUnavailable` with the fault (`lexicon`, `notWellFormed`, `notTyped`) and, for `lexicon`, the first failure of `Lexicon.failures` |
| shadow record | any difference | the record has `op`, the six identities, `python` (class, formulas, canonical text, conclusions, witness count), `lean` (status, code, formulas, canonical text, conclusions, witness count, `sentence`), and `classes` from `dispatch._classes` |
| nearest-wording suggestion | the quoted phrase is not a run of whole lexer tokens | test failure (fixture g1) |

## 5. Lean: definitions and the exact statements

### 5.1 Modules and conventions

New files only, except the two tier B additions named: `Ty` (2.4) and `Reject` (2.8) in `Syntax.lean`, and the
optional `Terminal.kwMid` (2.2) in `Token.lean`; each change re-runs the S1 fixtures and `tools/lean_statements.py`.
Conventions as base 5.1 and base 6: no prime, no `?`, no totality escape, one `#print axioms` line per theorem
in `VE/Audit.lean`, namespaces closed and reopened after each `mutual` block, every file in the frozen inventory
and in layer 3 (`tools/layer_policy.py`), the executable in layer 4.

| Module | Content |
|---|---|
| `VE/EnglishGrammar/Fixed/RelationalFol.lean` | generated: the fixed rules and nonterminal names of 2.5 |
| `VE/EnglishGrammar/Rules.lean` | the catalogue of 2.4, `ty`, `lexRules`, `grammar`, `grammar_rules`, `lexRules_terminatorFree`, `start_sentence` |
| `VE/EnglishGrammar/Actions.lean` | `Ctx`, `Sem`, `sig`, the action library of 2.7, `acts` |
| `VE/EnglishGrammar/Encode.lean` | `EFormula.encode`, `typedDocument`, `Env.decode` |
| `VE/EnglishGrammar/Read.lean` | `meaning`, `read`, `translate`, `checkRendering`, `EnglishOneReading`, the statements of 5.6 |
| `VE/EnglishGrammar/Extends.lean` | `envSub`, `lexiconSub`, `Extends`, `grammar_extension` |
| `VE/EnglishGrammar/ReadExamples.lean` | the fixtures of section 8 as `#guard` checks |
| `EnglishMain.lean` | the executable of 2.10 |

### 5.2 The signature

```lean
namespace VE.EnglishGrammar
open VE.Grammar

abbrev Scope := List (String × String)          -- (sort, reference text), index 0 innermost

structure Ctx where
  scope : Scope
  st : DState
  depth : Nat          -- list-marker depth
  nesting : Nat        -- formula nesting, 1 at the top
  leftmost : Bool      -- at the first token of the sentence's formula

def Sem : Ty → Type
  | .tok => Tok
  | .sentence => DState → Except Reject (EFormula × Bool × DState)
  | .formula => Ctx → Except Reject EFormula
  | .relative => Ctx → Except Reject EFormula   -- the subject is `var 0`
  | .term => Ctx → Except Reject ETerm
  | .intTerm => Ctx → Except Reject ETerm       -- S3
  | .declaration => Ctx → Except Reject (String × String)
  | .guard => Ctx → Except Reject EFormula
  | .marker => Bool
  | .unit => Unit
  | .listMarker => String
  | .noun => String
  | .label => String
  | .constant => String
  | .adjective => String
  | .natSubject => String × String
  | .count => Bool
  | .relation => String

def sig : Sig Tok where
  Ty := Ty
  decEq := inferInstance
  Sem := Sem
  tok := .tok
  leaf := fun t => t

def fixedRules (profiles : List String) : Array (Rule Terminal)
def lexRules (E : Env) (L : Lexicon) : Array (Rule Terminal)
def grammar (E : Env) (L : Lexicon) : Grammar Terminal     -- rules := fixedRules E.profiles ++ lexRules E L, start := 0
def ty (E : Env) (L : Lexicon) : Nat → Ty                    -- the table of 2.4, independent of `E` and `L`
def acts (E : Env) (L : Lexicon) : Array (Action sig)
def actionsVersion : String
def EFormula.encode : EFormula → Lean.Json
def typedDocument (E : Env) (As : List EFormula) : Bool
```

### 5.3 The readers

```lean
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
  else if !((grammar E L).typed sig (ty E L) (acts E L) && decide (ty E L (grammar E L).start = .sentence)) then
    .invalidGrammar .notTyped
  else match lex s with
    | .error r => .lexical r
    | .ok sents =>
        match readDocument (grammar E L) (meaning (grammar E L) (acts E L)) DState.init b sents.toList with
        | (.ok rs, _) => if typedDocument E (rs.map (·.1)) then .ok rs else .illTyped
        | (.stopped i o, _) => .stopped i o

def EnglishOneReading (E : Env) (O : Overlay) (L : Lexicon) (s : String) (rs : List (EFormula × Bool)) : Prop :=
  L.valid E O = true ∧
  ∃ sents st2, lex s = .ok sents ∧
    DocOneReading (grammar E L) (meaning (grammar E L) (acts E L)) DState.init
      (sents.toList.map (·.toList)) rs st2 ∧
    typedDocument E (rs.map (·.1)) = true

def checkRendering (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (rs : List (EFormula × Bool)) (s : String) :
    Bool :=
  match read E O L b s with
  | .ok rs2 => decide (rs2 = rs)
  | _ => false

inductive TranslateOutcome where
  | readings (rs : List (EFormula × Bool × DState)) (complete : Bool)
  | invalidGrammar (why : GrammarFault)
  | lexical (r : Reject)
  | notOneSentence
  | budget

def translate (E : Env) (O : Overlay) (L : Lexicon) (cap b : Nat) (s : String) : TranslateOutcome :=
  -- the three checks of `read`, then:
  … match lex s with
    | .error r => .lexical r
    | .ok sents =>
      match sents.toList with
      | [w] =>
        match parse (grammar E L) cap b w with
        | none => .budget
        | some ts => .readings (readingSet (meaning (grammar E L) (acts E L)) DState.init ts) (decide (ts.length < cap))
      | _ => .notOneSentence
```

The start-type test inside `read` is written so that `read` is total without `start_sentence`; the theorem
makes it always true for `grammar E L` and `ty E L` (D5), and `read_complete_english` carries it as the fifth
premise exactly as base 5.8's fallback wording allows. It costs one comparison per request.

### 5.4 Extensions

```lean
def lexiconSub (L L2 : Lexicon) : Prop :=
  (∀ x ∈ L.nouns, x ∈ L2.nouns) ∧ (∀ x ∈ L.letters, x ∈ L2.letters) ∧
  (∀ x ∈ L.wordings, x ∈ L2.wordings) ∧ (∀ x ∈ L.negatives, x ∈ L2.negatives) ∧
  (∀ x ∈ L.aliases, x ∈ L2.aliases) ∧ (∀ x ∈ L.spellings, x ∈ L2.spellings)

def envSub (E E2 : Env) : Prop :=
  E.profiles = E2.profiles ∧
  (∀ s ∈ E.sorts, ∃ s2 ∈ E2.sorts, s2.name = s.name) ∧
  (∀ p ∈ E.predicates, ∃ q ∈ E2.predicates, q.name = p.name ∧ q.arity = p.arity) ∧
  (∀ c ∈ E.constants, ∃ c2 ∈ E2.constants, c2.name = c.name)

def Extends (E : Env) (O : Overlay) (L : Lexicon) (E2 : Env) (O2 : Overlay) (L2 : Lexicon) : Prop :=
  envSub E E2 ∧ lexiconSub L L2 ∧ L.valid E O = true ∧ L2.valid E2 O2 = true
```

### 5.5 The statements, in one table

| Statement | Module | Needs | Contract obligation |
|---|---|---|---|
| `read_ok` | `Read` | checked by `read` | P2 for English (base) |
| `read_complete_english` | `Read` | `wf`, W4, `typed`, start type as premises | P3 for English (base) |
| `read_stopped` | `Read` | checked by `read` | P2 for a stopped document (new) |
| `english_reading_unique` | `Read` | — | P1 per lexicon (base) |
| `start_sentence` | `Rules` | — | totality (base); `rfl` |
| `meaning_total` | `Read` | `typed`, start type | totality (base) |
| `checked_rendering`, `checked_rendering_exact` | `Read` | checked by `read` | the per-output round trip (base), both directions (new) |
| `translate_exact` | `Read` | `wf` | meaning sets for English (new) |
| `translate_one_sentence` | `Read` | the three checks | translation reads one sentence (new) |
| `grammar_rules` | `Rules` | — | D1 (new) |
| `lexRules_terminatorFree` | `Rules` | — | W4 for the lexical half (new) |
| `valid_iff_no_failure` | `Lexicon` or `Rules` | — | the diagnostic of 4.5 is exact (new; proved in the stub) |
| `grammar_extension` | `Extends` | `Extends` | conservativity for English (base O4; the premise is for the reviewers) |

### 5.6 The exact statements

Free variables are implicit arguments bound by `variable` lines in the modules; here they are written as
explicit binders, which is how the stub elaborated them.

```lean
theorem read_ok : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) (rs : List (EFormula × Bool)),
  read E O L b s = .ok rs → EnglishOneReading E O L s rs

theorem read_complete_english : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List (EFormula × Bool)),
  EnglishOneReading E O L s rs →
  (grammar E L).wf = true → terminatorFree (grammar E L) = true →
  (grammar E L).typed sig (ty E L) (acts E L) = true → ty E L (grammar E L).start = .sentence →
  read E O L b s = .ok rs ∨ ∃ i, read E O L b s = .stopped i .budget

theorem read_stopped : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) (i : Nat)
    (o : Outcome Tok Reject EFormula),
  read E O L b s = .stopped i o →
  L.valid E O = true ∧ (grammar E L).wf = true ∧ terminatorFree (grammar E L) = true ∧
  ∃ sents rs st1 w, lex s = .ok sents ∧
    DocOneReading (grammar E L) (meaning (grammar E L) (acts E L)) DState.init
      ((sents.toList.take i).map (·.toList)) rs st1 ∧
    sents.toList[i]? = some w ∧
    (readSentence (grammar E L) (meaning (grammar E L) (acts E L)) st1 b w).1 = o ∧ ∀ A c, o ≠ .ok A c

theorem english_reading_unique : ∀ (E : Env) (O : Overlay) (L : Lexicon) (s : String)
    (rs rs2 : List (EFormula × Bool)),
  EnglishOneReading E O L s rs → EnglishOneReading E O L s rs2 → rs2 = rs

theorem start_sentence : ∀ (E : Env) (L : Lexicon), ty E L (grammar E L).start = .sentence

theorem meaning_total : ∀ (G : Grammar Terminal) (acts : Array (Action sig)) (ty : Nat → Ty)
    (st : DState) (w : List Tok) (t : Tree Tok),
  G.typed sig ty acts = true → ty G.start = .sentence → Derives G (.n G.start) w t →
  ∃ f, t.sem G sig acts = some ⟨.sentence, f⟩ ∧ meaning G acts st t = f st

theorem checked_rendering : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat)
    (rs : List (EFormula × Bool)) (s : String),
  checkRendering E O L b rs s = true → EnglishOneReading E O L s rs

theorem checked_rendering_exact : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat)
    (rs : List (EFormula × Bool)) (s : String),
  checkRendering E O L b rs s = true ↔ read E O L b s = .ok rs

theorem translate_exact : ∀ (E : Env) (O : Overlay) (L : Lexicon) (cap b : Nat) (s : String)
    (rs : List (EFormula × Bool × DState)) (x : EFormula × Bool × DState),
  translate E O L cap b s = .readings rs true → (grammar E L).wf = true →
  ∃ w, lex s = .ok #[w] ∧
    (x ∈ rs ↔ ∃ t, Derives (grammar E L) (.n (grammar E L).start) w.toList t ∧
      meaning (grammar E L) (acts E L) DState.init t = .ok x)

theorem translate_one_sentence : ∀ (E : Env) (O : Overlay) (L : Lexicon) (cap b : Nat) (s : String)
    (sents : Array (Array Tok)),
  lex s = .ok sents → sents.size ≠ 1 → L.valid E O = true →
  (grammar E L).wf = true → terminatorFree (grammar E L) = true →
  (grammar E L).typed sig (ty E L) (acts E L) = true → ty E L (grammar E L).start = .sentence →
  translate E O L cap b s = .notOneSentence

theorem grammar_rules : ∀ (E : Env) (L : Lexicon),
  (grammar E L).rules = fixedRules E.profiles ++ lexRules E L

theorem lexRules_terminatorFree : ∀ (E : Env) (L : Lexicon),
  terminatorFree { rules := lexRules E L, start := 0, rank := #[] } = true

theorem valid_iff_no_failure : ∀ (E : Env) (O : Overlay) (L : Lexicon),
  L.valid E O = true ↔ L.failures E O = []

theorem grammar_extension : ∀ (E : Env) (O : Overlay) (L : Lexicon) (E2 : Env) (O2 : Overlay) (L2 : Lexicon),
  Extends E O L E2 O2 L2 →
  ∃ e : RuleMap, e.Ok (grammar E L) (grammar E2 L2) (acts E L) (acts E2 L2)
```

`valid_iff_no_failure` was proved in the stub (it unfolds `Lexicon.valid`). The others elaborated as `Prop`s;
their proofs are S2.3.

### 5.7 By construction, and by test

- `start_sentence` is `rfl`: `grammar E L` has `start := 0` and `ty E L 0 = .sentence` by the table of 2.4.
- `grammar_rules` is `rfl` against the definition of `grammar`.
- `lexRules_terminatorFree` is by induction on the lexicon's lists: every terminal of a lexical rule is a
  `content`, a `kw` of a spelling word, an `exact` of a token that `lex` produced inside a sentence, or a
  `cls`; none accepts a token whose text is `.` because the lexer never produces one inside a sentence (2.6).
- `Reject.internal` is never constructed outside `meaning`: a grep test over `Actions.lean`, plus
  `meaning_total`, which makes the fallback branch unreachable from any derivation of `grammar E L`.
- `EFormula.encode` equals Python's wire form on the fixtures of 8.2: a differential test, not a theorem.

## 6. Files, generated artefacts and gates

| Artefact | Rule |
|---|---|
| `ve/english_grammar/relational-fol@0.json`, `LOCK.json` | 2.9 |
| `lean/VE/EnglishGrammar/Fixed/RelationalFol.lean` | generated; `--check` in the commit hook |
| the modules of 5.1 | frozen-inventory lines; `Audit.lean` lines for every theorem of 5.5; `lean/declarations.txt`, `statements.txt`, `axioms.txt` regenerated (`tools/lean_statements.py`, `lean/audit.py --write`) |
| `lakefile.toml` | `lean_exe ve_english_route`, root `EnglishMain`, in `defaultTargets` |
| `ve/backends/english_lean.py` | the adapter of 2.10; `english.admission` keeps `authority: python` in `ve/assurance-manifest.json`; the new Lean files that decode JSON are pinned there |
| `conformance/english_lean_{g2,reverse,mutate}.py`; `conformance/english_lean_lexicon.py` export moved under `ve/` | 2.11 |
| `docs/spec/english-lean-s2-report.md` | the G2 report |

Gates: the statement review of this specification before S2.3's proofs; G2 as the S2 plan states it.

## 7. What S2 consumes and returns

| From | Delivery | Used in |
|---|---|---|
| S0 | the rejection-site classes and blocked-wording ids; the lint sort; the conversion rules; the seal; the token-length figures | 2.7, 2.8, 2.14, 2.11 |
| S1 | the engine theorems; `Tok` with `glued`; `lex`; `Lexicon.valid`; `workBudget`; the G1a figures | 2.2, 2.3, 2.11 |
| the readability evaluation | the four gaps | 2.12, 3.3 |
| S2 returns | `start_sentence` proved by construction (no fallback); the body of `Extends` (2.13) for the reviewers; two `Reject` codes, the `Ty` additions, `kwMid` and the V3 proposal for the DRI; the G2 report with the two owed budgets | base 5.8, O4; S2 plan Q2 to Q7 |

## 8. Acceptance fixtures

Every fixture is an obligation on the implementation. **Verdicts, counts and steps in 8.1, 8.3, 8.4, 8.5 and 8.6
were computed** (section 12) by the proved S1 parser on the fixture grammar `GF`: the 88 fixed rules of 2.5 and
the 29 lexical rules that 2.6 gives for `F` and `LF` (base 8.5: sorts `person`, `service`; `deployed`,
`reviewed` with its negative, `owns` with its negative; `alice`, `legacy`), 117 rules in all, `|G|` = 479, 37
nonterminals, `Grammar.wf` and `terminatorFree` true. The expected formulas of 8.2 are hand-derived. A fixture
whose expected value is marked *obligation* was not computed.

### 8.1 Verdicts

`one`, `zero`, `many` are the verdicts of the sentences in order; `lexical r` the lexer's rejection.

| Id | Source | Verdict | Note |
|---|---|---|---|
| b1 | `Every service is reviewed.` | one | base e1 |
| b2 | `Every service that is deployed is reviewed.` | one | `universal.guard-relative` |
| b3 | `For every service that is deployed, there is a person who owns that service.` | one | 7,331 steps |
| b4 | `Alice owns legacy.` | one | |
| b5 | `Legacy is not reviewed.` | one | the validated negative |
| b6 | `Both legacy is deployed and legacy is reviewed.` | one | |
| b7 | `Legacy is deployed. It is reviewed.` | one, one | the `it` rule is a side condition: both sentences derive |
| b8 | `Legacy is deployed. Therefore legacy is deployed.` | one, one | `sentence.marked` |
| b9 | `For every service named S1, S1 is reviewed.` | one | |
| b10 | `There is a service such that that service is deployed.` | one | |
| b11 | `If legacy is deployed, then legacy is reviewed.` | one | |
| b12 | `Either legacy is deployed or legacy is reviewed, or both.` | one | |
| b13 | `This holds in all cases.` | one | |
| b14 | `Legacy is the same as legacy.` | one | |
| b15 | `It is not the case that legacy is deployed.` | one | `it` here is a keyword of `negation` |
| b16 | `For every person who owns legacy, that person owns legacy.` | one | |
| b17 | `Every person who owns legacy owns legacy.` | one | |
| b18 | `For every service that is deployed and is reviewed, and is deployed, that service is reviewed.` | one | `guard.three-left` |
| b19 | `For every service that is deployed, and is reviewed and is deployed, that service is reviewed.` | one | `guard.three-right` |
| b20 | `Every service that alice owns is reviewed.` | one | the object relative; spine `universal.guard-relative` |
| b21 | `All of the following hold: first clause: legacy is deployed; end first clause; second clause: legacy is reviewed; end second clause.` | one | 13,162 steps |
| b22 | `Both of the following hold: (a) legacy is deployed; (b) legacy is reviewed.` | one | |
| b23 | `If the following holds: (a) legacy is deployed; then the following holds: (b) legacy is reviewed.` | one | |
| b24 | `EVERY service is reviewed.` | zero | `kw` accepts one initial capital only |
| b25 | `Every sevice is reviewed.` | zero | |
| b26 | `Every service is reviewed` | lexical `unterminated` | |
| b27 | `Every service is deployed or reviewed, or both.` | zero | W14 (2.12) |
| b28 | `For every person, if that person is deployed and that person is reviewed, then that person is reviewed.` | zero | W08 (2.12) |
| b29 | `No service that is deployed is not reviewed.` | zero | W12 (2.12) |
| b30 | `Either legacy is deployed or legacy is reviewed , or both.` | zero | DRI ruling 1: the comma is not glued |
| b31 | `For every service that is deployed , there is a person who owns that service.` | zero | the same |
| b32 | `Alice does not own legacy.` | one | the binary negative |
| b33 | `Every person who does not own legacy owns legacy.` | one | |
| b34 | `Legacy, alice and legacy are deployed.` | one | the derivation exists; the meaning is `coordinationRepeated` (first) or `sortMismatch` (8.2, e34) |
| b35 | `Legacy is deployed, reviewed and deployed.` | one | meaning `coordinationRepeated` |
| b36 | `Some service is deployed.` | one | |
| b37 | `No service is deployed.` | one | |
| b38 | `Every deployed service is reviewed.` | one | spine `natural-every.subject`; the generic universal does not match, `deployed service` is no noun of `F` |
| b39 | `Every deployed service has an owner.` | one | |
| b40 | `Every service has an owner.` | one | `natural-every.owner` |
| b41 | `Every deployed service is reviewed and has an owner.` | one | |
| b42 | `Some service is deployed and reviewed.` | one | `some-tail.copula` |
| b43 | `Some service is deployed and is reviewed.` | one | `some-tail.two` |
| b44 | `Every deployed service is not reviewed.` | one | meaning `blockedWording natural-negation` |
| b45 | `Starting from legacy, legacy is reachable by one or more "owns" steps.` | zero | `F` has no relation over one sort: no `relation` rule |
| b46 | `Starting from legacy, legacy is reachable by zero or more steps, where a step from a service to a service satisfies this condition: that service is deployed.` | one | |
| b47 | `Starting from legacy, legacy is reachable by one or more steps, where a step from a service to a service satisfies the following: (a) that service is deployed.` | one | |
| b48 | `It, alice and legacy are deployed.` | zero | coordination takes constants only |

The constructed ambiguity of `tests/test_natural.py:543–553`: `FD` is `F` with one more sort whose selected noun
is `deployed service` and letter `D`.

| Id | Source (under `FD`) | Verdict | Witnesses (leftmost spines) |
|---|---|---|---|
| d1 | `Every deployed service is reviewed.` | many | `formula.universal › universal.relative` and `formula.natural › natural.every › natural-every.subject`; 2,514 steps |
| d2 | `It is not the case that every deployed service is reviewed.` | many | the same two under `negation` |
| d3 | `Every DEPLOYED service is reviewed.` | many | content words match in any case |
| d4 | `Every service is reviewed.` | one | |

The W4 check, both directions, on grammars built by hand: k1, the one rule `S → x exact(punct ".")`: `wf` true,
`terminatorFree` false; k2, the one rule `S → x`: both true.

The `kwMid` proposal (2.2), *obligations*: under an environment with a constant whose selected spelling is
`the api`: c1 `The api is reviewed.` one; c2 `Alice owns The api.` one; c3 `Alice owns the api.` one.

### 8.2 Meanings

Base e1 to e28 stand. Expected formulas below are hand-derived from `ve/english.py`; `var 0` is the innermost
binder.

| Id | Source | Expected |
|---|---|---|
| e29 | b18 | `all service (implies (and (and deployed reviewed) deployed) reviewed)` with `pred … [var 0]` throughout |
| e30 | b19 | `all service (implies (and deployed (and reviewed deployed)) reviewed)` |
| e31 | b20 | `all service (implies (pred owns [const alice, var 0]) (pred reviewed [var 0]))` |
| e32 | b21, b22 | `and (pred deployed [const legacy]) (pred reviewed [const legacy])`; b22 at depth 0 accepts `(a)` `(b)` |
| e33 | b22 with `(i)` `(ii)` | `stopped 0 (rejected markerDepth)` |
| e34 | b34; `Legacy, alice and legacy are deployed.` and `Legacy, alice and legacy are deployed.` with three distinct services `legacy`, `beta`, `gamma` in an extended `F` | `rejected coordinationRepeated`; with `Legacy, beta and gamma are deployed.`: `and (pred deployed [const legacy]) (and (pred deployed [const beta]) (pred deployed [const gamma]))`; with a person among them: `rejected sortMismatch` |
| e35 | b35 | `rejected coordinationRepeated` |
| e36 | b36, b37 | `ex service (pred deployed [var 0])`; `not (ex service (pred deployed [var 0]))` |
| e37 | b38 | `all service (implies (pred deployed [var 0]) (pred reviewed [var 0]))` |
| e38 | b39, b40 | `all service (implies (pred deployed [var 0]) (ex person (pred owns [var 0, var 1])))`; `all service (ex person (pred owns [var 0, var 1]))` |
| e39 | b41 | `all service (implies (pred deployed [var 0]) (and (pred reviewed [var 0]) (ex person (pred owns [var 0, var 1]))))` |
| e40 | b42, b43 | both `ex service (and (pred deployed [var 0]) (pred reviewed [var 0]))` |
| e41 | b44 | `stopped 0 (rejected (blockedWording "natural-negation"))` |
| e42 | `For every person, some service is deployed.` | `stopped 0 (rejected naturalScoped)` |
| e43 | b46, b47 | `reachBody true service (pred deployed [var 0]) (const legacy) (const legacy)` (zero or more: reflexive); `reachBody false …` |
| e44 | `Therefore it is reviewed.` after `Legacy is deployed.` | `ok`, marks false and true; `it` resolves: `leftmost` is true after the marker |
| e45 | `Alice owns it.` after `Legacy is deployed.` | `stopped 1 (rejected pronounUnresolved)`: `it` is not leftmost |
| e46 | `For every service, it is reviewed.` after `Legacy is deployed.` | `stopped 1 (rejected pronounUnresolved)`: the scope is not empty |
| e47 | `EFormula.encode` of e1 to e7 and e29 to e43 | equal to Python's wire form of `parse_english` on the same sources |

### 8.3 Lexicon and mutation replay

Computed on the S1 `Lexicon.valid`.

| Id | Case | Expected |
|---|---|---|
| l1 | `F`, `LF` | valid; `failures = []` |
| l2 | `F`, `LF` with `owns` on `{0} has the recorded relation "owns" to {1}` and its negative removed (base v2) | valid |
| l3 | as l2 with the negative `{0} does not own {1}` kept (base v3) | not valid; `failures = [("V5", "negative", "owns")]` |
| m1 | `Alice owns legacy.` under the lexicon of l2 | zero |
| m2 | `Alice has the recorded relation "owns" to legacy.` under l2 | one |
| m3 | b3 under l2 | zero: the text loses its reading |
| m4 | b1 under l2 | one |
| m5 | b7 under l2 | one, one |

m1 to m5 are the verdict half of base e23: under the mutated lexicon the texts that use `owns` lose their
derivation and no other text changes verdict; that no text gets a different formula is e23's meaning half.
The V3 proposal (2.6), *obligation*: l4, `F` with `deployed` declared as `{0} is v1.2 compliant` and `LF`
selecting it: not valid under the proposal (V3), valid under the S1 definition.

### 8.4 Translation mode

| Id | Case | Expected |
|---|---|---|
| tr1 | d1 under `FD`, cap 2 | 2 trees; `complete` false |
| tr2 | d1 under `FD`, cap 3 | 2 trees; `complete` true |
| tr3 | b1, cap 2 | 1 tree; `complete` true |
| tr4 | `Legacy is deployed. Legacy is reviewed.` | `notOneSentence` (code `NotOneSentence`); nothing is parsed |

### 8.5 The widenings

`GFw` is `GF` with the three proposed rules of 2.12.

| Id | Source under `GFw` | Verdict |
|---|---|---|
| w1 | b27 | one |
| w2 | b28 | one |
| w3 | b12 | one (unchanged) |
| w4 | b11 | one (unchanged) |
| w5 | b35 | one (unchanged) |
| w6 | b2 | one (unchanged) |
| w7 | b29 | zero (unchanged: the W12 fix is a message) |

`GFw` is well-formed and terminator-free. The full sample of 8.1 under `GFw` is an obligation of the G2 harness
when the widening is signed.

### 8.6 Steps and budgets

| Fixture | Steps (cap 2) | Against the budget |
|---|---|---|
| b3 | 7,331 | 0.35% of 2,100,000 |
| b21 | 13,162 | 0.63% |
| d1 | 2,514 | 0.12% |

The two owed G1a budgets are obligations of the G2 report: BlueDot ≤ 1 s, generated modules ≤ 60 s of
`lake build`.

### 8.7 Extensions

| Id | Case | Expected |
|---|---|---|
| q5 | `F`, `LF` and `F2` (base 8.5) with `reviewed` and `audited` on their fallbacks | `Extends` is false: `lexiconSub` fails on `reviewed`'s wording; `Legacy is reviewed.` loses its reading (base e20) |
| q6 | `F`, `LF` and `F` plus `archived` on `service` with wording `{0} is archived`, selections otherwise unchanged | `Extends` is true; `grammar_extension` gives a rule map; b1 to b47 keep their verdicts |

### 8.8 Evidence and tooling

Base i1 to i6 and t1 to t4 stand, with i5 over the lock file of 2.9. Added:

| Id | Case | Expected |
|---|---|---|
| t5 | a `proposed` row generated into the table | `--check` fails and names the tag |
| g1 | W12's text through the adapter | the suggestion quotes whole tokens; it does not contain `'t'` |
| n1 | `Rule 2 (exception to rule 1). …` with no rule 1 (`norms@0`) | recorded: `Expected Rule 1 with its own block`; outside S2 |

### 8.9 The iff claims, both directions

| Claim | Direction | Fixture |
|---|---|---|
| `complete` is true exactly when the parser returned fewer trees than the cap | fewer → true | tr2, tr3 |
| | not fewer → false | tr1 |
| `terminatorFree` is false exactly when some terminal accepts a terminator spelling | accepts → false | k1 |
| | none accepts → true | k2 |
| `valid` exactly when `failures` is empty | empty → valid | l1, l2 |
| | not empty → not valid | l3 |
| `checked_rendering_exact`: the check succeeds exactly when `read` returns these formulas and marks | ok rs → true | base e22, first case |
| | otherwise → false | base e22, second and third cases |
| `Extends` holds exactly when profiles, symbols and selections are kept and both lexicons are valid | kept → embeds | q6 |
| | reselected → not | q5 |
| a sentence has a derivation under `GF` exactly when Python's grammar derives it (the tree correspondence) | derives → one | b1 to b23, b32 to b47 |
| | does not → zero | b24, b25, b27 to b31, b48; d1 to d3 for `many` |

## 9. Limits, and what is not claimed

Base section 9 stands. In addition: no statement says that `grammar E L` is well-formed, terminator-free or
typed for every valid lexicon (checked per request); no statement relates the fixed table to Python's grammar
(measured by G2); the widenings are measured, not accepted; `Extends` and `grammar_extension` are proposals
until reviewed; the formulas of 8.2 are hand-derived until S2 confirms them; nothing here moves authority.

## 10. Statement review checklist (Astra + Fable, before S2.3)

1. The fixed rules of 2.5 are Python's grammar rule for rule over tokens, with the spacing flags Python accepts.
2. `lexRules` (2.6) instantiates exactly the families and conditions of `english_lark_grammar` and `_natural_grammar`.
3. The action library (2.7) gives each rule the formula the hand parser gives, in particular the guard
   associations, the coordination nesting, the natural-view translations and the de Bruijn indices of `owner`.
4. The `it` rule as `leftmost` plus the state is Python's rule exactly (e44 to e46).
5. The two new codes (2.8) and the `Ty` additions (2.4) are the right closure of the tier B lists.
6. `read`'s start-type test and `start_sentence` by construction match base 5.8's approved fallback wording.
7. `read_stopped`, `checked_rendering_exact`, `translate_exact`, `translate_one_sentence`, `grammar_rules`,
   `lexRules_terminatorFree` say what 3.4 says, and no more.
8. The body of `Extends` (2.13) is sufficient for `grammar_extension` and excludes vocabulary reselection.
9. The tree correspondence (2.11) is one to one, including the `kwMid` case.
10. The widening rules (2.12) are correctly stated as proposals and their meanings are the intended ones.
11. The lint sort (2.14) follows the DRI's rule by effect.
12. The computed fixtures of section 8 are the right expectations, b34, b38, b44, d1, tr1 and tr2 in particular;
    the hand-derived formulas of 8.2 are right.
13. Every name passes the audit's rules and collides with nothing in `VE.English` or `VE.Discourse`.
14. No public message, code or identity changes.

## 11. Open points

| # | Point | Recommendation |
|---|---|---|
| Q1 | the widenings | measured here; signed decision before any table change (S2 plan, Q1) |
| Q2 | `coordinationRepeated`, `naturalScoped` | adopt (tier B, as `coefficientNotNumeral` was) |
| Q3 | the final lint list | adopt 2.14 at this review; implement in E2 |
| Q4 | `Extends` | adopt 2.13 for the base profile; profiles stay deferred |
| Q5 | `kwMid` | adopt; otherwise mid-sentence `The api` is a recorded difference |
| Q6 | V3 and the terminator | adopt; one fixture (l4) |
| Q7 | the owed budgets | measured in S2.6 |
| Q8 | the `english.grammar` shape | 4.4; a later change is a tool change |
| Q9 | translation over documents | unspecified (base O9) |
| Q10 | W12's own shape (`No ⟨declaration⟩ that ⟨guard⟩ ⟨relative⟩`) | not proposed: needs a product decision on negative relatives under `no` |

## 12. How the figures were computed

A scratch file `lean/SpecStubs_english-lean-s2.lean` (not committed) imported the S1 modules
(`VE.Grammar.Reading`, `VE.Grammar.Extension`, `VE.EnglishGrammar.Lexer`, `VE.EnglishGrammar.Lexicon`) from the
`english-lean/integrate` build at `689219b1` (`lake env lean` against that checkout) and: declared the S2
signatures of 5.2 as `opaque` constants; wrote `meaning`, `read`, `translate`, `checkRendering`,
`EnglishOneReading`, `Extends` as in 5.3 and 5.4; wrote every statement of 5.6 as a definition of type `Prop`
and checked it with `#check`; proved `valid_iff_no_failure`; built `GF`, `GFD`, `GFv2` and `GFw` as rule lists
with the ranks of 2.4; and ran `lex`, `parse` (cap 2 and the caps of 8.4), `Grammar.wf`, `terminatorFree`,
`Lexicon.valid`, `Lexicon.failures` and `Prepared.steps` under `#guard` and `#eval` for every computed row of
section 8. All checks passed on 2026-10-04 under Lean 4.24.0. The file is to be re-created from this
specification when S2.1 starts; its contents are sections 2.4 to 2.6, 5.2 to 5.4 and 8.
