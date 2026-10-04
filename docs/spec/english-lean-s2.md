# English in Lean, S2: the English instance (statement specification)

> Status: statement specification, draft 5 (2026-10-04), branch `design/english-lean-s2`. This is the item-1
> statement spec of [english-lean-S2-PLAN.md](english-lean-S2-PLAN.md) draft 6 (the **S2 plan**). It writes out
> stage S2 of [english-lean-PLAN.md](english-lean-PLAN.md) (the **base plan**, draft 2) on top of
> [english-lean.md](english-lean.md) draft 2 (the **base spec**), whose tier A engine is proved and whose tier B
> lexer, tokens and `Lexicon.valid` are built on branch `english-lean/integrate` at `689219b1`
> ([english-lean-s1.md](english-lean-s1.md), the **S1 report**; [english-lean-measured.md](english-lean-measured.md),
> the **S0 report**). Base-spec definitions and statements are not repeated; a section number written `base 2.9`
> refers to the base spec. **Nothing was built for this draft.** What was run for draft 1: every Lean signature
> and statement of section 5 was elaborated as a stub against the S1 build (each statement as a definition of
> type `Prop`, as base 5.1 prescribes for unproved statements), and every verdict, count and step figure of
> section 8 was computed by the proved S1 parser on the hand-built fixture grammar of 8.1, over the S1 lexer's
> tokens (section 12). **Draft 2 applies the statement review** (`manage-agents/debates/english-lean-s2-spec`,
> Astra and Fable, converged FIX after round 2 on 2026-10-04; section 13 lists the edits). The stub was re-run
> for draft 2 on the amended signatures, statements, ranks and fixtures, and every check passed (section 12).
> **Draft 3 applies the two corrections of the first verification pass** (`manage-agents/english-lean-s2-p3ver1.final.md`,
> FAIL, 2026-10-04; section 14 lists them with their consequences). **Draft 4 applies the one correction of the
> second verification pass** (`manage-agents/english-lean-s2-p3ver2.final.md`, FAIL, 2026-10-04; section 15): the
> hand parser can match a text that the `{1}`-first subject relative derives, so `relativeForm` maps onto two
> Python classes, not one. **Draft 5 applies the one correction of the third verification pass**
> (`manage-agents/english-lean-s2-p3ver3.final.md`, FAIL, 2026-10-04; section 16): the `check_document` rejection
> that e51, e53 and e43 under `F` rely on is `UnsupportedProfile`, which base 4.2's `IllTyped` row does not list;
> 4.2 amends the row, and every rejected fixture's Python class was re-read against the check that fires first.
> Nothing was re-run for drafts 3 to 5, because no figure of section 12 depends on any of the four corrections
> (sections 14 to 16); the stub of section 12 was re-elaborated unchanged for draft 5. The review's PASS follows a
> bounded re-check of the edits of sections 13 to 16, not this draft.
> Formulas in section 8 were derived by hand from `ve/english.py` and are confirmed against Python in S2; a
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
(11), how the figures were computed (12), the statement review's edits (13), the first verification pass's
corrections (14), the second verification pass's correction (15), and the third's (16).

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | `grammar E L` is `fixedRules E.profiles` followed by `lexRules E L`, in that order, with one fixed nonterminal catalogue; the start symbol is nonterminal 0, `sentence` | 2.4, 2.5, 5.6 (`grammar_rules`) |
| D2 | Every fixed rule is one row of a JSON source, generated into a Lean table literal; punctuation terminals carry the `glued` flags of DRI ruling 1, so the fixed rules accept exactly Python's spacing | 2.5, 2.9 |
| D3 | A wording becomes rules by one procedure, `lexRules`: clause, subject relative and object relative per wording, negative and alias, cut exactly as Python's Lark grammar cuts them; noun, label and spelling rules per sort and constant; the natural-view families as Python's `_natural_grammar` instantiates them | 2.6 |
| D4 | Meanings are computed bottom-up from a context (scope, state, list depth, nesting, leftmost position). Side conditions are declared rejections computed by actions; they never remove a derivation | 2.7, 2.8 |
| D5 | `start_sentence` holds by construction: `ty E L 0 = .sentence` for every environment and lexicon. `read` and `translate` keep base 5.8's start-type test, which is therefore always true for `grammar E L` and costs one comparison; `read_complete_english` carries it as a premise, as base 5.8's fallback wording allows | 5.3, 5.6, 5.7 |
| D6 | `Reject` gains `coordinationRepeated`, `coordinationForm`, `naturalScoped` and `relativeForm` (tier B, for the DRI). Every other side condition of the S2 constructs maps to an existing code | 2.8 |
| D7 | Translation mode is `translate`: one sentence from `DState.init`; its set is complete exactly when the parser returned fewer trees than the cap; a text of two or more sentences is `NotOneSentence` | 2.3, 5.3, 8.4 |
| D8 | The service modes are `english.read` and `english.grammar`, in a new executable; the six identities of base 2.12 are computed by the service | 2.10, 4.3, 4.4 |
| D9 | The adapter runs under `dispatch.execute("english.admission", …)`; authority stays `python`; the shadow log is G2's instrument; `invalidGrammar` fails closed as `CheckerUnavailable` | 2.10, 4.5 |
| D10 | G2 compares verdict, formulas, canonical text, marks and witness multiplicity under the written tree correspondence; the reverse corpus is sampled from the `english.grammar` export; mutation replay is empirical | 2.11 |
| D11 | The readability writing gaps are fixtures. The two rules that would accept the two rejected sentence shapes are written, measured and excluded from the generated table until signed | 2.12, 8.5 |
| D12 | `Extends` gets a body: the base profile on both sides, every symbol kept with its full signature (argument sorts, constant sorts), every selection kept, both lexicons valid. The actions are `fixedActs ++ lexActs E L` with `fixedActs` closed and the sort data carried in values, so corresponding actions are equal terms. `grammar_extension` is stated against it for the reviewers | 2.3, 2.7, 2.13, 5.4, 5.6 |
| D13 | All eighteen lint codes stay in the Python producer in S2. The final sort of the eight retained codes is proposed here and fixed at the statement review | 2.14 |
| D14 | Lean's texts for `none`, `many`, `rejected` and `budget` are the base spec's; the adapter's nearest-wording suggestion quotes whole tokens only | 3.2, 3.3, 4.5 |
| D15 | The fixed table mirrors Lark rule for rule (coordination over `term`, relatives cut as Lark cuts them); every further restriction of the hand parser (scope, name spellings, distinctness, sorts, label letters, negation under `every`) is an action. The tree correspondence is therefore one to one and the hand parser's acceptance is the meaning | 2.5, 2.6, 2.7, 2.11 |
| D16 | The unit that `english.admission` dispatches is the grammatical reading up to the typed check (`check_document`); `_check_conclusions` runs after it in Python for either backend. G2 compares at that boundary | 2.10, 2.11 |

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
| name form | a constant spelling that Python's coordination accepts as a name: letters and single spaces, optionally after `the `, and the capitalised form of such a spelling that begins with `the ` (`english.py:1574–1577`; 2.6, 2.7) |
| signature | a predicate's argument sorts in order (`PredDecl.args`) or a constant's sort (`ConstDecl.sort`) (2.3) |

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
  declared wording and negative, constants with display forms, profiles, `ProfileForms`). S2 adds the
  signatures, which the lexical rules and the actions of 2.6 and 2.7 need: `PredDecl.args : List String`, the
  argument sorts in order (`arity = args.length`), and `ConstDecl.sort : String`. It adds one more field,
  `source : Lean.Json := .null`, the validated environment JSON; `typedDocument` re-decodes the formulas against
  it through the existing typed decoder (`lean/VE/Service/Standalone.lean:331`, `decodeTyped`), and **no other
  definition reads `source`**: `lexRules`, `ty`, the actions and `Env.decode`'s consumers read the typed fields
  only. S2 writes `Env.decode : Json → Json → Except String Env` from the environment and the overlay; it fills
  `args` and `sort` from the environment's declarations. For the base profile `forms` is empty (S3 computes the
  profile forms).
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
| 17 | `term` | `term` | context → term, with the constant's datum when the term is a written constant (`TermVal`, 5.2) |
| 18 | `noun` | `noun` | the sort and the noun's text |
| 19 | `label` | `label` | the sort whose letter it is, and the label's text |
| 20 | `constant` | `constant` | the constant's name, its sort, and whether the spelling is a name form (`ConstVal`, 5.2) |
| 21 | `relative` | `relative` | |
| 22 | `object_relative` | `relative` | |
| 23 | `adjective` | `adjective` | the unary predicate's name and its argument sort |
| 24 | `natural` | `formula` | |
| 25 | `natural_some` | `formula` | |
| 26 | `some_tail` | `relative` | |
| 27 | `copula_relative` | `relative` | |
| 28 | `copula_adjective` | `adjective` | |
| 29 | `natural_no` | `formula` | |
| 30 | `natural_every` | `formula` | |
| 31 | `natural_tail` | `relative` | |
| 32 | `natural_subject` | `natSubject` | the adjective's predicate, the noun's sort and the noun's text |
| 33 | `owner_clause` | `relative` | |
| 34 | `reach` | `formula` | |
| 35 | `count` | `count` | `true` for zero or more (reflexive) |
| 36 | `relation` | `relation` | the relation's name |

`Ty` therefore gains `marker`, `unit`, `listMarker`, `noun`, `label`, `constant`, `adjective`, `natSubject`,
`count`, `relation` (tier B: base 5.8 left the list to S2). `intTerm` stays for S3. The ranks (W3) are one
fixed array, the certificate for every lexicon: terminals-first nonterminals at rank 0; `term`, `declaration`,
`natural` at 1; `atom`, `object_relative`, `coordination`, `relative` at 2; `some_tail`, `natural_tail`,
`guard_atom`, `formula` at 3; `guard_relative`, `guard`, `sentence` at 4. `coordination` is at 2 because its
rules begin with `term` (2.5); `relative` is at 2 because Lark's subject cut strips one leading `term ` only
(2.6), so a wording whose first two symbols are holes (`{0} {1} are related`, which V3 allows) gives a subject
relative that begins with `term`; a wording that begins with `{1}` does not (its leading `term ` is stripped
too, 2.6). `some_tail`, `natural_tail` and `guard_atom` follow `relative`. The array is one certificate for
every lexicon, so it covers that corner whether or not a lexicon reaches it. `Grammar.wf` of the fixture
grammar is true under these ranks (8.1, section 12).

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
| `formula.atom` … `formula.natural` (9 rows) | `formula → ⟨atom⟩` `⟨negation⟩` `⟨compact⟩` `⟨listing⟩` `⟨universal⟩` `⟨existential⟩` `⟨reach⟩` `⟨coordination⟩` `⟨natural⟩` | `nest` |
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
| `coordination.subject-and` | `coordination → ⟨term⟩, ⟨term⟩ and ⟨term⟩ are ⟨adjective⟩` | `coordSubjects and` |
| `coordination.subject-or` | `coordination → ⟨term⟩, ⟨term⟩ or ⟨term⟩ is ⟨adjective⟩` | `coordSubjects or` |
| `coordination.predicate-and` | `coordination → ⟨term⟩ is ⟨adjective⟩, ⟨adjective⟩ and ⟨adjective⟩` | `coordAdjectives and` |
| `coordination.predicate-or` | `coordination → ⟨term⟩ is ⟨adjective⟩, ⟨adjective⟩ or ⟨adjective⟩` | `coordAdjectives or` |
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

Five remarks. The `formula → natural` row is in the fixed table because Python's natural hook extends `formula`
(`english.py:1990`); its scope restriction is a side condition (2.8, `naturalScoped`). The coordination rows
take `term`, as Lark's do (`:1835–1838`); the hand parser's restrictions to top-level sentences and to constants
written as names (`:1572–1577`) are side conditions of `coordSubjects` and `coordAdjectives` (2.7, 2.8), so
`It, alice and legacy are deployed.` has one derivation and a rejected meaning (b48, e50), as it has one Lark
derivation and a hand-parser rejection. The three-atom guards keep Python's two associations (`guard`,
`:1286–1293`): `a and b, and c` is `And (And a b) c`, `a, and b and c` is `And a (And b c)`. The reach rows are
in the base table because Lark's and the hand parser's reach forms are unconditional (`:1458`, `:1866–1868`);
the profile `closure@0` is enforced by `typedDocument`, as `check_document` enforces it (`ve/ast.py:281–282`,
`UnsupportedProfile`: a class of the `illTyped` outcome, 4.2), so `fixedRules` returns the base table for every profile list that names `relational-fol@0` and gives
`closure@0` no table of its own (profile tables are S3). The longest fixed right-hand side has 28 symbols
(`listing.*.words`), as S0 measured over tokens.

### 2.6 The lexical rules

`lexRules E L` appends, in the order of the lexicon's lists, the rules below. A wording's or a noun's text is
lexed by `lex` (with a terminator appended); its word tokens become `content` terminals, a quoted part an
`exact` quoted token, a punctuation token an `exact` punctuation token with its flags, and a hole `{k}` the
nonterminal `term` (the slot's sort is an integer sort only under `order@0`, S3). This is Lark's `content_lit`
(`english.py:1827–1829`): the fallback noun `entity of sort "s"` (`:247`) therefore lexes as three `content`
words and one `exact` quoted token, never as four words. `action` constructors are those of 2.7; each carries
the data written after it, read from the lexicon entry and from the declaration's signature (2.3), and nothing
else.

| Family | For | Rules | Action |
|---|---|---|---|
| clause | every selected wording, negative and alias of a predicate `p` of arity `k` | `atom → w₀ ⟨term⟩ w₁ … ⟨term⟩ wₖ` with the holes in the wording's order | `pred p order negated` |
| subject relative | the same | when the wording begins with a hole, whichever hole it is, the clause without its leading `⟨term⟩`: `relative → w …` (`{1} follows {0}` gives `relative → follows ⟨term⟩`); when it begins with a word, the clause itself, `relative → w₀ ⟨term⟩ …` (Lark strips one leading `term `, and nothing else, `:1923–1924`) | `relSubject p order negated` |
| object relative | the same, for binary wordings that contain ` {1}` (the hole after a space) | the clause without that `⟨term⟩` and the space before it, wherever it is: `object_relative → w₀ ⟨term⟩ w₁ w₂` for `{0} w₁ {1} w₂` (Lark and the hand parser delete ` {1}`, `:1056`, `:1926`) | `relObject p negated` |
| noun | every sort `s` with selected noun `n` | `noun → ⟨the tokens of n⟩` | `noun s n` |
| label | every sort `s` with letter `ℓ` | `label → cls (label ℓ)` | `label s` |
| spelling | every constant `c` of sort `s` with selected spelling `sp` | `constant → sp` (one `kw` per word; a quoted spelling is one `exact` quoted token); when `sp` is one lower-case word, also `constant → the sp`; when `sp` begins with `the `, also the capitalised spelling (2.2, Q5) | `const c s nf` with `nf` true for `constant → sp` and for the capitalised spelling when `sp` is a name form (2.1), false otherwise and always for `constant → the sp` (`:1574–1577`: Python's coordination names are the display texts and their capitalised `The …` forms, not the added article) |
| adjective | every unary `p` on sort `s` whose selected wording is `{0} is a` with `a` one lower-case ASCII word | `adjective → c:a` | `adjective p s` |
| natural subject | every such `p` on a sort `s` that has a selected noun `n` | `natural_subject → c:a ⟨the tokens of n⟩` | `natSubject p s n` |
| copula | the same `p` | `copula_relative → c:is c:a`; `copula_adjective → c:a` | `copulaRel p`; `adjective p s` |
| owner | when a binary predicate named `owns`, with argument sorts `s₁ s₂`, has the selected wording `{0} owns {1}` | `owner_clause → has an owner` | `owner s₁ s₂` |
| relation | every binary predicate whose two argument sorts are equal | `relation → exact (quoted name)` | `relation name` |

Conditions, as Python's: the adjective, natural-subject and copula families exist only for wordings of the form
`{0} is a` with `a` matching `[a-z]+` (`english.py:1946–1950`, `:1978–1986`); the owner clause only for that
exact wording (`:1987–1989`); the relation family only for equal argument sorts (`:1899–1900`). A sort without a
selected noun has no noun rule and no natural subjects; a lexicon that passes V1 gives every sort a noun.

Python has two subject cuts: Lark's generator strips one leading `term ` whichever hole it is (`:1924`), and
the hand parser strips a leading `{0} ` only (`:1054`). They agree on every wording that begins with `{0}` or
with a word, which is every wording Python's producer emits in S2 (its `TEMPLATE_SHAPE` lint keeps `{0}`
first). Three corners follow Lark for the derivation and the hand parser for the meaning (D15):

- a wording that begins with a word keeps every `⟨term⟩` in its subject relative under both cuts, and
  `relSubject` then prepends `var 0` to the clause's arguments exactly as the hand parser does (`:1085–1089`),
  so the formula has one argument too many and fails `typedDocument`, as it fails `check_document` in Python
  (e51);
- a wording whose first symbol is a hole other than `{0}` loses that `⟨term⟩` under Lark's cut
  (`relative → follows ⟨term⟩` for `{1} follows {0}`) and keeps it under the hand parser's, whose pattern
  therefore begins with a term and has one term group more than the rule has terms. Python never accepts a
  text the rule derives, and rejects it in one of two classes. When the pattern does not match the text, the
  hand parser falls to `unknown_atom` (`:1101`, `SyntaxError`): e52, where nothing of `F` is spelled `follows`
  or begins with it. When the pattern re-segments the text, which the spellings of a lexicon can allow, the
  hand parser prepends `var 0` to one argument too many (`:1089`) and builds an `Atom` node of three arguments
  (`:1096–1097`). Where object relatives are allowed (the guard of a `for every` or `every` sentence,
  `:1284–1285`), the same wording's object alternative, whose cut deletes nothing from a wording without ` {1}`
  (`:1056`), matches the same span with the extra argument appended instead (`:1090`), and the hand parser's own
  ambiguity guard rejects the clause (`:1104–1107`, `SyntaxError`). Everywhere else (`every … relative`,
  `there is … who`, the natural clauses: `:1447`, `:1454`, `:1484`, `:1506`, `:1538`) the atom reaches
  `check_document`, which rejects it with `UnsupportedProfile`, because an `Atom` node needs `nary@0`
  (`ast.py:272–273`, before the arity check of `:275–276`): the `illTyped` class as 4.2 amends it, as for e51.
  That is e53, the wording `{1} {0} are related` with persons spelled `alice`, `bob` and `alice bob`, where the
  rule `relative → ⟨term⟩ are related` reads `alice bob are related` with one constant and the pattern
  `(term) (term) are related` reads it with two. The rule is generated as Lark generates it, so the tree
  correspondence stays one to one (2.11), and `relSubject` rejects every derivation of it with `relativeForm`
  (2.7, 2.8; e52, e53). The action sees its term children, not the text, so it cannot tell the Python outcomes
  apart: `relativeForm` maps onto either class, and G2 accepts either (2.8, 2.11);
- a binary wording that begins with `{1}` contains no ` {1}`, so it gets no object relative in Lean, while
  Python's rule for it reads the literal text `{1}`, which the lexer rejects (`badCharacter`: `{` is no chunk
  or punctuation character) before any rule applies.

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
the state `after A`: referents joined with the constants of `A` (every `const` node anywhere in `A`,
`_mentioned_constants`, `english.py:88–100`), `binderSeen` or-ed with "A has a binder", which is
`_has_discourse_binder` (`:103–115`): an `all` or `ex` node anywhere in `A`, under any connective, in a reach
body included (`:1623–1624`).

**Actions as data.** `acts E L = fixedActs ++ lexActs E L` (5.2). `fixedActs` is one closed array: the actions of
the fixed rows read neither `E` nor `L`; the sort of a constant, an adjective, a label or a natural subject
reaches them inside the child's value (2.4). `lexActs E L` has one action per rule of `lexRules E L`, in its
order, each a constructor of the table below applied to the data 2.6 names. This is what makes `grammar_extension`
provable (2.13): under `Extends` the same entry and the same signature give the same data, so the same term.

**The `it` rule** (`english.py:957–961`, `:1069–1073`, `:1376–1378`): `termIt` returns the term `const c` (as
`⟨const c, none⟩`: not a written constant) when
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
| `nest` | `formula → formula` (the nine `formula.*` rows) | the child's value, after rejecting with `nestingLimit` when the context's nesting exceeds 64 (`MAX_DEPTH`): Python checks at the entry of every `formula()` call (`english.py:1369–1371`), which is every `formula` node |
| `not` | `formula → formula` | `not A`, the child at nesting + 1, leftmost false |
| `and2`, `or2` | `formula, formula → formula` (the children are `atom` nodes) | `and A B`, `or A B`; both children leftmost false, nesting unchanged (Python reads atoms there, `:1428–1430`, and atoms do not enter `formula()`) |
| `implies2` | `formula, formula → formula` | `implies A B`; both children leftmost false, nesting + 1 (`child()`, `:1428–1430`) |
| `listWords k`, `listMarkers k` | two formulas (and two markers) → `formula` | `k A B` with both children at depth + 1, nesting + 1 (`child(listed=True)`, `:1408–1420`); `listMarkers` first checks the markers: at even depth they must be `(a)` and `(b)`, at odd depth `(i)` and `(ii)` (`_markers`, `english.py:564`), else `markerDepth` |
| `guardAnd`, `guardLeft`, `guardRight`, `relAnd` | relatives → `relative` | `and a b`; `and (and a b) c`; `and a (and b c)`; `and a b` |
| `forallBody` | `declaration, formula → formula` | push the binding; `all s B`; the body at nesting + 1 (`child(inner)`, `:1439`) |
| `forallGuardBody` | `declaration, unit, relative, formula → formula` | push; `all s (implies G B)`; the body at nesting + 1 (`:1439`); the guard at the same nesting (it is atoms) |
| `forallRel`, `forallGuardRel` | as above with a relative body | `all s R`; `all s (implies G R)`; no nesting change (`:1447`) |
| `existsBody`, `existsRel` | `unit, declaration, formula/relative → formula` | push; `ex s B`; the body of `existsBody` at nesting + 1 (`:1456`), `existsRel`'s relative unchanged (`:1454`) |
| `declThat`, `declOrdinal o`, `declNamed` | `noun → declaration`; `tok, noun`; `noun, tok, label` | the binding `(s, "that " ++ n)`, `(s, "the " ++ o ++ " " ++ n)` with `n` the noun's text, `(s, label text)`; `declNamed` first requires the label's sort (the sort whose letter it is, 2.6) to be the noun's sort `s`, else `sortMismatch` (`english.py:935–938`: each sort's noun is offered its own letter only, so `For every service named P1, P1 is reviewed.` is rejected; b49, e48); if the reference text is already in the scope, `shadowedName` (`:942–943`) |
| `termConst`, `termLabel`, `termRef pre` | `constant → term`; `label → term`; `tok, noun → term` | `⟨const c, some ⟨c, s, nf⟩⟩` from the constant's datum; the innermost binding whose reference text is the label's text, or `pre ++ " " ++ n`, as `⟨var i, none⟩`; none: `unboundReference` |
| `termIt` | → `term` | the `it` rule above, as `⟨const c, none⟩`: a resolved `it` is not a written constant |
| `top`, `bottom`, `eq` | → `formula` | `top`; `bottom`; `eq t u` (the left term keeps `leftmost`) |
| `pred p order negated` | terms → `formula` | `pred p args` with the arguments in declaration order (the wording's hole order permutes them); `not` of it when negated; the first term keeps `leftmost`, later terms get false |
| `relSubject p order negated`, `relObject p negated` | terms → `relative` | as `pred` with `var 0` in the subject slot, or in the object slot. `relSubject` tells the two corners of 2.6 apart from `order` and the number of its term children: when the wording begins with a word, the rule keeps every term and `relSubject` prepends `var 0` to the clause's arguments as the hand parser does (`:1085–1089`), so the formula is ill-typed; when the wording begins with a hole other than `{0}` (the first of `order` is not 0), the rule has lost that term and `relSubject` rejects with `relativeForm`, because the hand parser's subject cut (`:1054`) never accepts a text the rule derives: its pattern misses the text, or re-segments it into an atom with one argument too many that the hand parser's ambiguity guard or `check_document` rejects (2.6); the action, which sees its term children and not the text, cannot tell which, and rejects with the one code |
| `noun s n`, `label s`, `const c s nf`, `adjective p s`, `natSubject p s n`, `relation r`, `count refl`, `copulaRel p` | terminals → their type | the datum; `copulaRel p` (`copula_relative → is a`) is the relative `pred p [var 0]` (`:1484`, the first clause of a `some` sentence is an ordinary relative) |
| `coordSubjects k` | `term ×3, adjective → formula` | in this order (`english.py:1570–1599`): the scope must be empty, else `coordinationForm` (`:1572`); the three terms are run (the first keeps `leftmost`, the others get false; `It, alice and legacy are deployed.` as a first sentence is therefore `pronounUnresolved`, b48); each must be a written constant whose spelling is a name form, `⟨const cᵢ, some ⟨cᵢ, sᵢ, true⟩⟩`, else `coordinationForm` (`:1574–1577`: a resolved `it`, a reference, a label, a quoted spelling or the added article `the sp` is not a name); the three names distinct, else `coordinationRepeated` (`:1592`); each `sᵢ` equal to the adjective's sort, else `sortMismatch` (`:1594–1595`); then `k (pred p [const c₁]) (k (pred p [const c₂]) (pred p [const c₃]))` (`:1597–1599`) |
| `coordAdjectives k` | `term, adjective ×3 → formula` | the same scope and subject conditions on the one term (`:1572–1577`, `:1600–1604`); the three predicates distinct, else `coordinationRepeated` (`:1606`); the subject's sort equal to each adjective's sort, else `sortMismatch` (`:1607–1608`); then `k (pred p₁ [const c]) (k (pred p₂ [const c]) (pred p₃ [const c]))` |
| `naturalTop` | `formula → formula` | the child; if the scope is not empty, `naturalScoped` (`english.py:1967–1968`) |
| `someDecl` | `declaration, relative → formula` | push; `ex s T` |
| `copulaAnd` | `relative, adjective → relative` | `and R (pred a [var 0])`; the adjective's sort must be the scope's innermost sort, else `sortMismatch` (`english.py:1491–1498`) |
| `noDecl` | `declaration, relative → formula` | push; `not (ex s R)` |
| `everySubject` | `natSubject, relative → formula` | push `(s, "that " ++ n)` with `n` the natural subject's noun text (`:1533`); `all s (implies (pred p [var 0]) T)`; if the tail's relative is a negation, `blockedWording "natural-negation"`: that is, if `T` is `not _` (`natural-tail.relative`) or `T` is `and (not _) _` (`natural-tail.both`, whose left conjunct is the relative; Python checks the relative before it reads `and`, `english.py:1538–1540`, so `Every deployed service is not reviewed and has an owner.` is blocked too, b50, e49) |
| `everyOwner` | `declaration, relative → formula` | push; `all s O` |
| `owner s₁ s₂` | → `relative` | `ex s₁ (pred owns [var 0, var 1])`; `s₂` must be the scope's innermost sort, else `sortMismatch` (`english.py:1555–1558`) |
| `reachNamed` | `term, term, count, relation → formula` | `reachNamed refl r t u` |
| `reachBody listed` | `term, term, count, unit, declaration, unit, declaration, formula → formula` | the source declaration is run in the context's scope and the destination declaration in that scope with the source pushed (`:1469–1471`), so a destination with the source's reference text is `shadowedName` (b46, b47, e43); both declarations the same sort, else `sortMismatch` (`:1472`); push source then destination (the destination is `var 0`, the source `var 1`, `:1476`); `reachBody refl s B t u`; the body at nesting + 1, and at depth + 1 when `listed` (`child(…, listed=listed)`, `:1476`) |

The nesting increments are exactly those of Python's `child()` (`english.py:1395–1396`): `not`, `implies2`,
`listWords`, `listMarkers`, `forallBody`, `forallGuardBody`, `existsBody` and `reachBody` run their formula
children at nesting + 1; no other action changes the nesting, and `nest` alone checks it. Every action increments
nothing but what is named. `textTooLong` is the lexer's. No action constructs `Reject.internal` (a source test,
5.7).

### 2.8 Side conditions

The S1 `Reject` list (`Syntax.lean`) with four additions, all tier B and for the DRI:

| Code | When | Python today |
|---|---|---|
| `coordinationRepeated` | a coordination names one constant, or one adjective, twice | `coordination` returns nothing (`english.py:1592`, `:1606`); the text falls to `unknown_atom` (b34), or its leading atom is read and the sentence end is missed at the comma (`:1625`, b35): `SyntaxError` either way |
| `coordinationForm` | a coordination under a binder, or one whose subject is not a constant written as a name form (2.7) | `coordination` returns nothing when the scope is not empty (`english.py:1572`) or when a subject is not one of its names (`:1574–1577`, `:1590–1592`); the text falls to `unknown_atom`: `SyntaxError` |
| `naturalScoped` | a natural clause under a binder | `_natural_parser` returns nothing when the scope is not empty; the generic forms then fail: `SyntaxError` |
| `relativeForm` | a subject relative of a wording whose first symbol is a hole other than `{0}` (2.6) | the hand parser's subject cut keeps the leading term (`english.py:1054`), so its pattern has one term group more than Lark's rule has terms; either the pattern misses the text, which falls to `unknown_atom` (`:1101`): `SyntaxError` (e52), or the pattern re-segments the text and the atom has one argument too many (`:1089`), which the hand parser's ambiguity guard rejects where object relatives are allowed (`:1104–1107`, `SyntaxError`) and `check_document` rejects elsewhere with `UnsupportedProfile` (`ast.py:272–273`: no `nary@0`): the `illTyped` class as 4.2 amends it (e53) |

The first three map onto `SyntaxError`. `relativeForm` maps onto `SyntaxError` or onto the `illTyped` class
(whose Python classes, `UnsupportedProfile` among them, 4.2 lists) by the text, and the action cannot tell which
(2.6), so G2 accepts either class for it and records which one Python gave (2.11). No public code changes (D12 of the base spec): under Python authority the public code is Python's, and
once the hole-order rule of `TEMPLATE_SHAPE` is a V3 condition (2.14, E2) no valid lexicon has such a wording, so
the rule is never generated. The S2 constructs
use these existing codes: `shadowedName`, `unboundReference`, `pronounUnresolved`, `sortMismatch` (for the
sorts of coordination, copula, owner and reach, and for a label letter that is not the noun's sort),
`markerDepth`, `nestingLimit`, `blockedWording "natural-negation"`. The ill-typed formula of a subject relative
of a wording that begins with a word (2.6) is no side condition: `typedDocument` rejects it (`illTyped`).

### 2.9 The fixed-rule source, the generator and the lock file

`ve/english_grammar/relational-fol@0.json` is an array of rows `{"tag", "lhs", "act", "rhs", "status"?}`. `lhs` is
a nonterminal name of 2.4; `act` an action name of 2.7 with its data (`{"act": "listWords", "kind": "and"}`);
`rhs` a list of: a string (a `kw` terminal); `{"c": word}` (content); `{"p": text, "before": bool,
"after": bool}` (punctuation with its flags; the flags default to false); `{"q": name}` (a quoted identifier);
`{"cls": "numeral"}` or `{"cls": "label", "letter": "S"}`; `{"kwMid": word}` (the terminal of 2.2, Q5; it
occurs in no fixed row, and the export of 4.4 uses it for the capitalised spelling rules); `{"n": name}` (a
nonterminal). A row with
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
  result type of `parse_english`. **The dispatched unit** (D16) is the grammatical reading up to the typed
  check: in `_parse_english_document_uncached` (`ve/english.py:1636–1672`) the hand parser, the Lark audit
  (`require_unique_derivation`, `require_correspondence`) and `ast.check_document` (`:1661`), which is what
  `read` computes (parse, meaning, `typedDocument`). That part runs under `dispatch.execute("english.admission",
  payload, python=…, lean=…)`. `_check_conclusions` (`:1665`), the entailment check of every marked sentence
  against the earlier unmarked ones, is not part of the reading: it runs after the dispatch, in Python,
  unchanged, for either backend and under every authority; `read` returns the marks and does not judge them. Under
  the default authority nothing changes. Under `VE_AUTHORITY_OVERRIDES=english.admission=shadow` the Python
  result of the dispatched unit is returned and every difference is recorded in `ve-shadow.jsonl` with the
  classes of `dispatch._classes`, plus the fields of 4.5. Under `lean` authority (not in S2), an `invalidGrammar`
  response is `CheckerUnavailable`.

### 2.11 The G2 harness

**Tree correspondence.** A Lark derivation of `english_lark_grammar(env)` corresponds to the Lean derivation
obtained by: replacing the document rule by the lexer's sentence split; replacing each phrase terminal by its
word tokens in place (`kw` for case-sensitive words, `content` for case-insensitive, `exact` for quoted and
punctuation tokens with the flags of the spacing Python's regex accepts); replacing `LABEL`, `NUMERAL` and
`INT_OP` by the token-class rules; dropping rules over `IMPOSSIBLE`; mapping the capitalised constant duplicate
onto the `kwMid` rule (2.2); and mapping the nonterminals of Lark's EBNF expansion (`?formula` inlining, the
`__start_plus_0` document rule) onto the catalogue of 2.4. These are the rules of `conformance/english_lean_tokens.py`
(S0 report, section 7) with the `kwMid` case added. The map is one to one because the fixed table and
`lexRules` mirror Lark rule for rule (D15): coordination over `term` (`english.py:1835–1838`), subject relatives
cut by stripping one leading `term ` whichever hole it is (`:1924`; 2.6), object relatives by deleting ` {1}` (`:1926`), nouns lexed as
`content_lit` lexes them (`:1827–1829`), the capitalised constant alternative as `kwMid`. The hand parser's
further restrictions (scope, name spellings, distinctness, sorts, label letters, negation under `every`) remove
no derivation on either side: Lark derives, the hand parser rejects, and Lean's action rejects (2.7). So the
witness multiplicity (zero, one, two or more) is compared directly, and a text with one Lark derivation and a
hand-parser rejection is `one` with a rejected meaning on both sides (b48, b49, b50, b53 to b55).

**Comparison** (`conformance/english_lean_g2.py`), per text of the sealed corpus (`conformance/english-lean/corpus-seal.json`,
checked first with `english_lean_seal.py --check`): Python's outcome **at the dispatched boundary of 2.10**, that
is after `check_document` and before `_check_conclusions` (class, formulas in wire form, canonical strict text,
conclusion indices, witness count from the Lark forest), against Lean's (status, `ast`, `canonical`,
`conclusions`, witness count). Agreement is the base plan's comparison rule (section 5): equal formulas, canonical
text, identities and marks when both accept; mapped classes when both reject (base 4.1, with base 4.2's `IllTyped`
row read as 4.2 of this specification amends it: `UnsupportedProfile` is a class of `illTyped`), where `relativeForm` is
mapped onto two classes, `SyntaxError` and the `illTyped` class, the harness accepting either and recording which
one Python gave, because the hand parser's class there turns on a re-segmentation of the text that the action
does not see (2.6, 2.8); wall-clock `ResourceLimit` excluded and listed. A text whose grammatical reading agrees and whose marked conclusion Python's
entailment check then refuses is not a difference: that check is Python's for either backend (D16), and the
harness records it separately as `conclusion_rejected`. Everything else is a difference, closed only as a Lean
fix, a Python fix or a recorded product decision.

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

`Extends E O L E2 O2 L2` holds when: `E` has the base profile alone, `E.profiles = ["relational-fol@0"]`, and
`E2` the same profiles (the supported domain of the statement; S3 widens it); every sort of `E` is a sort of
`E2`; every predicate of `E` is a predicate of `E2` with the same arity **and the same argument sorts**; every
constant of `E` is a constant of `E2` **with the same sort**; every entry of `L` (noun, letter, wording,
negative, alias, spelling) is an entry of `L2`; and `L` is valid for `E`, `O`, and `L2` for `E2`, `O2`. Names
and arities alone would not do: re-declaring `owns` over `service × person` keeps its name and arity, drops the
`relation` rule and changes the `owner` action's data (q7).

Under it a rule map exists (`grammar_extension`, 5.6), by this argument. `fixedRules` is the same array, since
the profiles are equal, and `fixedActs` is one closed array, so every fixed rule and its action are the same
terms on both sides. Every lexical rule of `L` is a lexical rule of `L2`: each family of 2.6 is built from one
lexicon entry and the signature of its symbol (the hole order and the negation flag from the wording's text, the
noun's text, the spelling's text and its name form, `args` and `sort`), the entry is in `L2` by `lexiconSub` and
the signature is unchanged by `envSub`, so the right-hand side is the same list and the action is the same
constructor applied to the same data: `acts2[R2.act]? = acts[R.act]?` holds by reflexivity after substitution,
which is what `RuleMap.Ok` demands. No action closes over `E` or `L` (2.7), so an action never differs on the
symbols of `E2 \ E`. `e.nt` is the identity (the catalogue of 2.4 is fixed in S2; S3's per-sort property
nonterminals revisit this) and `e.rule` sends each rule index of `grammar E L` to the index of the same rule in
`grammar E2 L2`; it is injective because V4 makes the selections distinct, so no two rules of `grammar E L`
coincide. Reselecting a wording breaks `lexiconSub` (q5); adding a predicate with its own wording keeps it (q6);
changing a signature breaks `envSub` (q7). The profile case stays deferred (base O4). If the amended stub of
section 12 does not elaborate `grammar_extension` as stated, the statement is deferred rather than weakened (the
review's fallback).

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
| Trusted definitions | the fixed-rule data of 2.5 (JSON source and generated literal); `lexRules`; `ty` and the rank array; the action library (`fixedActs`, `lexActs`) and `meaning`; `Env.decode`; `EFormula.encode`; `typedDocument` as a link to the existing typed decoder |
| Proved | `read_ok`, `read_complete_english`, `read_stopped`, `english_reading_unique`, `start_sentence`, `meaning_total`, `checked_rendering`, `checked_rendering_exact`, `translate_exact`, `translate_one_sentence`, `grammar_rules`, `lexRules_terminatorFree`; `grammar_extension` once its premise is accepted |
| Checked per request | `Lexicon.valid`, `Grammar.wf`, `terminatorFree`, `Grammar.typed` |
| Tested only | the fixed table against the JSON source; the fixtures of section 8; the G2 comparison, reverse corpus and mutation replay; `Reject.internal` unconstructed; the wire form of `EFormula.encode` against Python's |

## 3. English: one reading each

### 3.1 The claim sentences

Unchanged from base 3.1: C1 until the theorems of 5.6 are in the audit inventory, then C2; C4 with any mark. S2
adds no claim sentence. The adapter attaches none in S2: records keep `python:surface`.

### 3.2 The outcomes

Unchanged from base 3.2. Four rejection texts are added (4.2):

| Code | Text |
|---|---|
| `CoordinationRepeated` | `Sentence {i} lists the same name or the same property twice in one list.` |
| `CoordinationForm` | `Sentence {i} lists three names or three properties where that form is not available. Use it only as a whole sentence, with each name written as it is declared.` |
| `NaturalScoped` | `Sentence {i} uses a some, no or every clause inside another clause. Write it with for every or there is.` |
| `RelativeForm` | `Sentence {i} uses a wording as a relative clause where that form is not available. Write the clause in full, with for every or there is.` |

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
| `read_stopped` | If the English reader stops at a sentence, the lexicon was valid and the grammar passed all its checks (well-formed, terminator-free, typed, with a sentence as its start symbol), every sentence before that one has one reading in order, and the reported outcome is the reader's outcome for that sentence from the state the earlier sentences leave; it is not an acceptance. | anything about later sentences |
| `checked_rendering_exact` | The check of a rendered text succeeds exactly when reading the text returns exactly the given formulas and marks. | that the renderer produces such a text |
| `translate_exact` | If translation mode returns a complete set for a text, the text is one sentence and the set lists exactly the results of the derivations of that sentence that have a meaning from the initial state. | anything when the set is not complete |
| `translate_one_sentence` | If a text has a number of sentences other than one and the checks pass, translation mode reports that it reads exactly one sentence. | |
| `grammar_rules` | The rules of the English grammar are the fixed rules of the profiles followed by the lexical rules. | |
| `lexRules_terminatorFree` | No lexical rule has a terminal that accepts a sentence terminator. | anything about the fixed rules: they are checked by `read` |
| `valid_iff_no_failure` | A lexicon is valid exactly when its list of failed conditions is empty. | |
| `grammar_extension` | If an environment and lexicon of the base profile extend another (every symbol kept with its argument sorts or its sort, every selection kept, both valid), there is a rule map from the smaller grammar into the larger that keeps every rule's sides and action. | anything about other profiles; anything when a wording was reselected or a signature changed |

## 4. Diagnostics

### 4.1 Statuses

Base 4.1, unchanged. `translate`'s `notOneSentence` is status `rejected` with code `NotOneSentence`; its
`budget` is status `budget`.

### 4.2 Rejection codes added, and one inherited row amended

| Code | Text | Python today |
|---|---|---|
| `CoordinationRepeated` | 3.2 | `SyntaxError` (unknown phrase) |
| `CoordinationForm` | 3.2 | `SyntaxError` (unknown phrase) |
| `NaturalScoped` | 3.2 | `SyntaxError` |
| `RelativeForm` | 3.2 | `SyntaxError` (unknown phrase, or the hand parser's ambiguity guard where object relatives are allowed), or `UnsupportedProfile` from `check_document` when the hand parser re-segments the text elsewhere: a class of `IllTyped` below (2.6, 2.8) |
| `IllTyped` (base 4.2, amended) | base 4.2 | `UnknownSymbol`, `TypeMismatch`, `UnsupportedProfile` |

**The amended row.** Base 4.2 maps `IllTyped` onto `UnknownSymbol` and `TypeMismatch`. `check_document`
(`ve/ast.py:377–385`: the Python checker, under the default typing authority of `ve/assurance-manifest.json`,
`typing`, `authority: python`) raises a third class on formulas the hand parser builds from the base profile:
`UnsupportedProfile`, for an `Atom` node (three or more arguments) under a profile list without `nary@0`
(`:272–273`), raised before the arity check of `:275–276`, and for a `Reach` node under a profile list without
`closure@0` (`:281–282`). Both are reached from the base profile: e51 and e53 build three-argument atoms, b51 and
b52 under `F` build reach formulas (e43). Lean's `typedDocument` returns `false` on all of them, so the outcome is
`illTyped`, and the comparison of 2.11 maps it onto the three classes. The other `UnsupportedProfile` sites of
`check_document` are outside the base profile and outside S2: `order@0` arithmetic and comparisons (`:243–244`,
`:303–304`; S3), `data@0` string quantification (`:319–320`), W6 environments (`:219–220`). No public message or
code changes: under Python authority the class shown is Python's, as before.

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

`rhs` uses the symbol encoding of 2.9, with `{"p": …}` carrying both flags always and `{"kwMid": word}` for the
`kwMid` terminal of the capitalised spelling rules (2.2, 2.6), so that the export covers every terminal
`grammar E L` can contain. `act` is the action's name with its data, as 2.9 writes it. The rules are in the
order of `grammar E L`, so `index` is the rule index that `derivation` and `witnesses` name.

### 4.5 Tool, adapter and shadow diagnostics

| Tool | Failure | Message names |
|---|---|---|
| `tools/english_grammar_gen.py --check` | a generated table differs from its source; a `proposed` row is in the table | the profile and the first differing tag |
| the same | a lock-file hash differs with `actions_version` unchanged | the file and the two hashes |
| adapter | `invalidGrammar` | `CheckerUnavailable` with the fault (`lexicon`, `notWellFormed`, `notTyped`) and, for `lexicon`, the first failure of `Lexicon.failures` |
| shadow record | any difference | the record has `op`, the six identities, `python` (class, formulas, canonical text, conclusions, witness count, taken at the dispatched boundary of 2.10), `lean` (status, code, formulas, canonical text, conclusions, witness count, `sentence`), `classes` from `dispatch._classes`, and `conclusion_rejected` when Python's `_check_conclusions` refused the document after the dispatch (not a difference, 2.11) |
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
| `VE/EnglishGrammar/Actions.lean` | `Ctx`, `ConstVal`, `TermVal`, `Sem`, `sig`, the action library of 2.7, `fixedActs`, `lexActs`, `acts` |
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

/-- The datum of a written constant (2.6): its name, its sort, and whether the spelling that wrote it is a
name form (2.1), which the coordination actions require (2.7). -/
structure ConstVal where
  name : String
  sort : String
  nameForm : Bool
  deriving DecidableEq, Repr

/-- A term with the constant's datum when the term is a constant written by a spelling rule; `none` for
`it`, a reference and a label (2.7). -/
structure TermVal where
  term : ETerm
  written : Option ConstVal := none
  deriving DecidableEq, Repr

def Sem : Ty → Type
  | .tok => Tok
  | .sentence => DState → Except Reject (EFormula × Bool × DState)
  | .formula => Ctx → Except Reject EFormula
  | .relative => Ctx → Except Reject EFormula   -- the subject is `var 0`
  | .term => Ctx → Except Reject TermVal
  | .intTerm => Ctx → Except Reject TermVal     -- S3
  | .declaration => Ctx → Except Reject (String × String)   -- sort, reference text
  | .guard => Ctx → Except Reject EFormula
  | .marker => Bool
  | .unit => Unit
  | .listMarker => String
  | .noun => String × String            -- sort, noun text
  | .label => String × String           -- the sort whose letter it is, the label's text
  | .constant => ConstVal
  | .adjective => String × String       -- predicate, its argument sort
  | .natSubject => String × String × String   -- predicate, sort, noun text
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
def ranks : Array Nat                                        -- the certificate of 2.4, one array for every lexicon
def grammar (E : Env) (L : Lexicon) : Grammar Terminal     -- rules := fixedRules E.profiles ++ lexRules E L, start := 0, rank := ranks
def ty (E : Env) (L : Lexicon) : Nat → Ty                    -- the table of 2.4, independent of `E` and `L`
def fixedActs : Array (Action sig)                           -- closed: reads neither `E` nor `L` (2.7)
def lexActs (E : Env) (L : Lexicon) : Array (Action sig)    -- one action per rule of `lexRules E L`, in its order
def acts (E : Env) (L : Lexicon) : Array (Action sig) := fixedActs ++ lexActs E L
def actionsVersion : String
def EFormula.encode : EFormula → Lean.Json
def typedDocument (E : Env) (As : List EFormula) : Bool
```

The `act` field of a fixed rule indexes `fixedActs`; the `act` of the `i`-th lexical rule is
`fixedActs.size + i`. `acts` is a definition, not an opaque constant: `grammar_extension` unfolds it.

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
  E.profiles = ["relational-fol@0"] ∧ E2.profiles = E.profiles ∧
  (∀ s ∈ E.sorts, ∃ s2 ∈ E2.sorts, s2.name = s.name) ∧
  (∀ p ∈ E.predicates, ∃ q ∈ E2.predicates, q.name = p.name ∧ q.arity = p.arity ∧ q.args = p.args) ∧
  (∀ c ∈ E.constants, ∃ c2 ∈ E2.constants, c2.name = c.name ∧ c2.sort = c.sort)

def Extends (E : Env) (O : Overlay) (L : Lexicon) (E2 : Env) (O2 : Overlay) (L2 : Lexicon) : Prop :=
  envSub E E2 ∧ lexiconSub L L2 ∧ L.valid E O = true ∧ L2.valid E2 O2 = true
```

`envSub` does not mention `source`, `wording`, `negative`, `noun` or `display`: `lexRules` and `lexActs` read
none of them (2.3, 2.6), and `valid` is a separate conjunct.

### 5.5 The statements, in one table

| Statement | Module | Needs | Contract obligation |
|---|---|---|---|
| `read_ok` | `Read` | checked by `read` | P2 for English (base) |
| `read_complete_english` | `Read` | `wf`, W4, `typed`, start type as premises | P3 for English (base) |
| `read_stopped` | `Read` | checked by `read` (all four checks are concluded) | P2 for a stopped document (new) |
| `english_reading_unique` | `Read` | — | P1 per lexicon (base) |
| `start_sentence` | `Rules` | — | totality (base); `rfl` |
| `meaning_total` | `Read` | `typed`, start type | totality (base) |
| `checked_rendering`, `checked_rendering_exact` | `Read` | checked by `read` | the per-output round trip (base), both directions (new) |
| `translate_exact` | `Read` | checked by `translate` (`wf` is inside `.readings`) | meaning sets for English (new) |
| `translate_one_sentence` | `Read` | the three checks | translation reads one sentence (new) |
| `grammar_rules` | `Rules` | — | D1 (new) |
| `lexRules_terminatorFree` | `Rules` | — | W4 for the lexical half (new) |
| `valid_iff_no_failure` | `Lexicon` or `Rules` | — | the diagnostic of 4.5 is exact (new; proved in the stub) |
| `grammar_extension` | `Extends` | `Extends` (base profile, full signatures, 2.13) | conservativity for English (base O4; the premise is for the reviewers) |

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
  (grammar E L).typed sig (ty E L) (acts E L) = true ∧ ty E L (grammar E L).start = .sentence ∧
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
  translate E O L cap b s = .readings rs true →
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

`valid_iff_no_failure` was proved in the stub (it unfolds `Lexicon.valid`), and `grammar_rules` is `rfl` there.
The others elaborated as `Prop`s, in draft 2's form: `read_stopped` with its two added conclusions,
`translate_exact` without the `wf` premise (a `.readings` result is reached only after `translate`'s three
checks, which include `wf`, so the proof derives it) and `grammar_extension` over the `Extends` of 5.4 and the
`acts` of 5.2 (section 12). Their proofs are S2.3.

### 5.7 By construction, and by test

- `start_sentence` is `rfl`: `grammar E L` has `start := 0` and `ty E L 0 = .sentence` by the table of 2.4.
- `grammar_rules` is `rfl` against the definition of `grammar`.
- `lexRules_terminatorFree` is by induction on the lexicon's lists: every terminal of a lexical rule is a
  `content`, a `kw` or `kwMid` of a spelling word, an `exact` of a token that `lex` produced inside a sentence,
  or a `cls`; none accepts a token whose text is `.` because the lexer never produces one inside a sentence (2.6).
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
| S2 returns | `start_sentence` proved by construction (the start-type test stays in `read`, always true); the body of `Extends` (2.13) for the reviewers; four `Reject` codes, the `Ty` additions, `kwMid` and the V3 proposal for the DRI; the G2 report with the two owed budgets | base 5.8, O4; S2 plan Q2 to Q7 |

## 8. Acceptance fixtures

Every fixture is an obligation on the implementation. **Verdicts, counts and steps in 8.1, 8.3, 8.4, 8.5 and 8.6
were computed** (section 12) by the proved S1 parser on the fixture grammar `GF`: the 88 fixed rules of 2.5
(the four coordination rows over `term`) and the 29 lexical rules that 2.6 gives for `F` and `LF` (base 8.5:
sorts `person`, `service`; `deployed`, `reviewed` with its negative, `owns` with its negative; `alice`,
`legacy`), 117 rules in all, `|G|` = 479, 37 nonterminals, with the ranks of 2.4; `Grammar.wf` and
`terminatorFree` true. The figures were recomputed for draft 2 and every row below holds under it; where draft 1
had a different value the row says so. The expected formulas of 8.2 are hand-derived. A fixture whose expected
value is marked *obligation* was not computed.

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
| b46 | `Starting from legacy, legacy is reachable by zero or more steps, where a step from a service to a service satisfies this condition: that service is deployed.` | one | the derivation exists; the meaning is `shadowedName`: both declarations bind `that service` (e43) |
| b47 | `Starting from legacy, legacy is reachable by one or more steps, where a step from a service to a service satisfies the following: (a) that service is deployed.` | one | the same |
| b48 | `It, alice and legacy are deployed.` | one | coordination takes `term`, as Lark's does; spine `formula.coordination › coordination.subject-and › term.it`; the meaning is `pronounUnresolved` (e50). Draft 1 computed `zero` over `constant` |
| b49 | `For every service named P1, P1 is reviewed.` | one | `label.P` is a rule of `GF`; the meaning is `sortMismatch`: `P` is `person`'s letter (e48) |
| b50 | `Every deployed service is not reviewed and has an owner.` | one | spine `natural-every.subject`, tail `natural-tail.both` with the negative relative; the meaning is `blockedWording natural-negation` (e49) |
| b51 | `Starting from legacy, legacy is reachable by zero or more steps, where a step from a service to a second service satisfies this condition: that service is deployed.` | one | the positive reach pair (e43): under `F` the meaning is `illTyped`, under `F` with `closure@0` a formula |
| b52 | `Starting from legacy, legacy is reachable by one or more steps, where a step from a service to a second service satisfies the following: (a) that service is deployed.` | one | the same |
| b53 | `For every person, legacy, beta and gamma are deployed.` under the extended `F` of e34 | one | the meaning is `coordinationForm`: the scope is not empty (e50) |
| b54 | `The legacy, beta and gamma are deployed.` under the extended `F` of e34 | one | `constant → the legacy` derives; the meaning is `coordinationForm`: the added article is not a name form (e50) |
| b55 | `Legacy is deployed. It, alice and legacy are deployed.` | one, one | the second sentence's meaning is `coordinationForm`: `it` resolves to `legacy` and is not a written constant (e50) |

The extended `F` of e34 (`GF3` in the stub) adds the services `beta` and `gamma` with their spellings and
article forms; `Legacy, beta and gamma are deployed.` is `one` under it (e34's accepted case).

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
| e43 | b46, b47; b51, b52 | b46, b47: `stopped 0 (rejected shadowedName)`, the destination declaration is run with the source `that service` in scope (2.7; `english.py:942`, `:1471`). b51, b52 under `F`: `illTyped`, a reach formula needs `closure@0` (`ast.py:281–282`; Python's class is `UnsupportedProfile`, a class of `illTyped` by 4.2). b51, b52 under `F` with `profiles = ["relational-fol@0", "closure@0"]`: `reachBody true service (pred deployed [var 1]) (const legacy) (const legacy)` (zero or more: reflexive) and `reachBody false …`: the destination `the second service` is `var 0`, the source `that service` is `var 1` |
| e44 | `Therefore it is deployed.` after `Legacy is deployed.` | `ok`, marks false and true; `it` resolves: `leftmost` is true after the marker. The reader's result is the same for `Therefore it is reviewed.`, whose conclusion Python's `_check_conclusions` then refuses (`english.py:1710–1713`) after the dispatched unit (2.10): the fixture uses the entailed conclusion so that the reader and Python's admission agree |
| e45 | `Alice owns it.` after `Legacy is deployed.` | `stopped 1 (rejected pronounUnresolved)`: `it` is not leftmost |
| e46 | `For every service, it is reviewed.` after `Legacy is deployed.` | `stopped 1 (rejected pronounUnresolved)`: the scope is not empty |
| e47 | `EFormula.encode` of every result of e1 to e7, e29 to e46 and e48 to e53 that is `ok` | equal to Python's wire form of `parse_english` on the same sources; the rejected and ill-typed results have no wire form and are excluded |
| e48 | b49 | `stopped 0 (rejected sortMismatch)`: the label's sort `person` is not the noun's sort `service` |
| e49 | b50 | `stopped 0 (rejected (blockedWording "natural-negation"))`: the relative of the `both` tail is a negation |
| e50 | b48; b53; b54; b55 | `stopped 0 (rejected pronounUnresolved)` (the `it` rule fails first: no referent); `stopped 0 (rejected coordinationForm)`; `stopped 0 (rejected coordinationForm)`; `stopped 1 (rejected coordinationForm)`. Compare e34's `coordinationRepeated` and `sortMismatch`, which are checked after the form |
| e51 | *obligation*: `F` with a binary `owner_of` over `service × person` declared `the owner of {0} is {1}`, and `Every service that the owner of that service is alice is reviewed.` | one derivation, `universal.guard-relative` whose guard is the subject relative that keeps both its `⟨term⟩`s (2.6, the wording begins with a word; the object relative `the owner of ⟨term⟩ is` leaves `alice is reviewed`, which no relative derives); the meaning `all service (implies (pred owner_of [var 0, var 0, const alice]) (pred reviewed [var 0]))` is `illTyped`, as `check_document` rejects the hand parser's three-argument atom (`english.py:1089–1097`, the longest match: the object alternative `the owner of (term) is` matches a shorter span and loses) with `UnsupportedProfile` (`ast.py:272–273`: an `Atom` node needs `nary@0`, which `F` lacks; the arity check of `:275–276` is not reached), a class of `illTyped` by 4.2 |
| e52 | *obligation*: `F` with a binary `follows` over `person × person` declared `{1} follows {0}`, and `Every person who follows alice owns legacy.` | one derivation, `universal.guard-relative` whose guard is the subject relative `follows ⟨term⟩` (2.6: Lark strips the leading `term ` of a `{1}`-first wording too; the wording contains no ` {1}`, so there is no object relative); the meaning is `stopped 0 (rejected relativeForm)`: the hand parser's subject cut keeps the leading term (`english.py:1054`), its pattern `(term) follows (term)` matches nothing at `follows alice` (no term of `F` is spelled `follows` or begins with it), and the sentence falls to `unknown_atom` (`:1101`, `SyntaxError`); compare e53 |
| e53 | *obligation*: `F` with a binary `related` over `person × person` declared `{1} {0} are related`, two more persons spelled `bob` and `alice bob`, and `Every person alice bob are related.` | one derivation, `universal.relative` whose relative is the subject relative `⟨term⟩ are related` (2.6: Lark's rule for the wording is `term term are related` and its cut strips one leading `term `, `english.py:1924`; the term is the constant spelled `alice bob`, the only term that leaves `are related`); the meaning is `stopped 0 (rejected relativeForm)`. Python does not fall to `unknown_atom`: the hand parser's pattern `(term) (term) are related` (`:1054` strips nothing from a `{1}`-first wording) re-segments `alice bob are related` as `alice`, `bob`, prepends `var 0` (`:1089`) and builds the three-argument atom `related(var 0, alice, bob)` (`:1096–1097`); the relative of `every … relative` is read without object alternatives (`:1447`), so no second match competes, the Lark audit passes (one derivation; `require_correspondence` checks extension readings only, `unambiguity.py:81–103`), and `check_document` rejects the atom with `UnsupportedProfile` (`ast.py:272–273`: an `Atom` node needs `nary@0`, which `F` lacks; the arity check of `:275–276` is not reached): the `illTyped` class as 4.2 amends it, as for e51, not `SyntaxError`. (The same clause inside a guard, `Every person who alice bob are related owns legacy.`, meets the hand parser's ambiguity guard instead, `:1104–1107`, `SyntaxError`: 2.6.) Both sides reject; the class differs, and G2 accepts either for `relativeForm` (2.8, 2.11). The second verification pass's counterexample (section 15), its Python class corrected by the third (section 16) |

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

The three figures were re-measured for draft 2 under the coordination rows over `term` and the ranks of 2.4,
and are unchanged from draft 1: none of the three sentences predicts a coordination past its first token.

The two owed G1a budgets are obligations of the G2 report: BlueDot ≤ 1 s, generated modules ≤ 60 s of
`lake build`.

### 8.7 Extensions

| Id | Case | Expected |
|---|---|---|
| q5 | `F`, `LF` and `F2` (base 8.5) with `reviewed` and `audited` on their fallbacks | `Extends` is false: `lexiconSub` fails on `reviewed`'s wording; `Legacy is reviewed.` loses its reading (base e20) |
| q6 | `F`, `LF` and `F` plus `archived` on `service` with wording `{0} is archived`, selections otherwise unchanged | `Extends` is true; `grammar_extension` gives a rule map; b1 to b55 keep their verdicts |
| q7 | `F`, `LF` and `F` with `owns` re-declared over `service × person` (same name, same arity), selections unchanged | `Extends` is false: `envSub` fails on `owns`'s `args`. Without the signature clause it would hold while the `owner s₁ s₂` action and the `relation` family differ (2.13) |

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
| `Extends` holds exactly when the base profile, the symbols with their signatures and the selections are kept and both lexicons are valid | kept → embeds | q6 |
| | reselected → not; signature changed → not | q5; q7 |
| a sentence has a derivation under `GF` exactly when Python's grammar derives it (the tree correspondence) | derives → one | b1 to b23, b32 to b55 (b34, b35, b44, b46 to b55 with a rejected meaning, as the hand parser rejects them) |
| | does not → zero | b24, b25, b27 to b31; d1 to d3 for `many` |

## 9. Limits, and what is not claimed

Base section 9 stands. In addition: no statement says that `grammar E L` is well-formed, terminator-free or
typed for every valid lexicon (checked per request); no statement relates the fixed table to Python's grammar
(measured by G2); the widenings are measured, not accepted; `Extends` and `grammar_extension` are proposals
until reviewed, and `grammar_extension` speaks of the base profile only; the formulas of 8.2 are hand-derived
until S2 confirms them; the conclusion check of a marked sentence is not part of the reading and is claimed
nowhere (D16); the Python class of a `relativeForm` rejection is one of two (`SyntaxError`, or `UnsupportedProfile`
within the `illTyped` class), and the reader does not say which (2.8, 4.2); nothing here moves authority.

## 10. Statement review checklist (Astra + Fable, before S2.3)

1. The fixed rules of 2.5 are Lark's grammar rule for rule over tokens (coordination over `term`), with the
   spacing flags Python accepts; every further restriction of the hand parser is an action (D15).
2. `lexRules` (2.6) instantiates exactly the families and conditions of `english_lark_grammar` and
   `_natural_grammar`, with Lark's cuts for subject and object relatives and `content_lit`'s lexing of nouns.
3. The action library (2.7) gives each rule the formula the hand parser gives, in particular the guard
   associations, the coordination nesting and its scope, name-form, distinctness and sort conditions, the label
   sort of `declNamed`, the natural-view translations, the negation check on both `every` tails, the nesting
   increments of `child()`, the reach bindings and the de Bruijn indices of `owner`.
4. The `it` rule as `leftmost` plus the state is Python's rule exactly (e44 to e46), with the binder test of
   `_has_discourse_binder`.
5. The four new codes (2.8) and the `Ty` additions (2.4) are the right closure of the tier B lists.
6. `read`'s start-type test and `start_sentence` by construction match base 5.8's approved fallback wording (D5).
7. `read_stopped`, `checked_rendering_exact`, `translate_exact`, `translate_one_sentence`, `grammar_rules`,
   `lexRules_terminatorFree` say what 3.4 says, and no more.
8. The body of `Extends` (2.13, 5.4) is sufficient for `grammar_extension`: the base profile, full signatures,
   `fixedActs` closed and `lexActs` built from entry and signature alone; it excludes vocabulary reselection
   (q5) and signature changes (q7).
9. The tree correspondence (2.11) is one to one, including the `kwMid` case, and the comparison is taken at the
   dispatched boundary of 2.10 (D16).
10. The widening rules (2.12) are correctly stated as proposals and their meanings are the intended ones.
11. The lint sort (2.14) follows the DRI's rule by effect.
12. The computed fixtures of section 8 are the right expectations, b34, b38, b44, b46 to b55, d1, tr1 and tr2
    in particular; the hand-derived formulas of 8.2 are right, e43, e44, e48 to e53 in particular; the Python
    class named for every rejected fixture is the class of the check that fires first on Python's path (4.2).
13. Every name passes the audit's rules and collides with nothing in `VE.English` or `VE.Discourse`.
14. No public message, code or identity changes.

## 11. Open points

| # | Point | Recommendation |
|---|---|---|
| Q1 | the widenings | measured here; signed decision before any table change (S2 plan, Q1) |
| Q2 | `coordinationRepeated`, `coordinationForm`, `naturalScoped`, `relativeForm` | adopt (tier B, as `coefficientNotNumeral` was); the review added `coordinationForm` for the hand parser's scope and name-form conditions on coordination (section 13); the first verification pass added `relativeForm` for the subject relative of a wording whose first symbol is a hole other than `{0}`, which Lark derives and the hand parser never accepts (section 14); the second corrected its Python class, `SyntaxError` or the `illTyped` class by the text, either accepted by G2 (section 15); the third named the class behind `illTyped` there, `UnsupportedProfile`, which base 4.2's row lacked (4.2, section 16) |
| Q3 | the final lint list | adopt 2.14 at this review; implement in E2 |
| Q4 | `Extends` | adopt 2.13 for the base profile, with full signatures and closed fixed actions (the review's resolution); profiles stay deferred; defer the statement if the amended stub does not elaborate it |
| Q5 | `kwMid` | adopt; otherwise mid-sentence `The api` is a recorded difference |
| Q6 | V3 and the terminator | adopt; one fixture (l4) |
| Q7 | the owed budgets | measured in S2.6 |
| Q8 | the `english.grammar` shape | 4.4; a later change is a tool change |
| Q9 | translation over documents | unspecified (base O9) |
| Q10 | W12's own shape (`No ⟨declaration⟩ that ⟨guard⟩ ⟨relative⟩`) | not proposed: needs a product decision on negative relatives under `no` |

## 12. How the figures were computed

For draft 1, a scratch file `lean/SpecStubs_english-lean-s2.lean` (not committed) imported the S1 modules
(`VE.Grammar.Reading`, `VE.Grammar.Extension`, `VE.EnglishGrammar.Lexer`, `VE.EnglishGrammar.Lexicon`) from the
`english-lean/integrate` build at `689219b1` (`lake env lean` against that checkout) and: declared the S2
signatures of 5.2 as `opaque` constants; wrote `meaning`, `read`, `translate`, `checkRendering`,
`EnglishOneReading`, `Extends` as in 5.3 and 5.4; wrote every statement of 5.6 as a definition of type `Prop`
and checked it with `#check`; proved `valid_iff_no_failure`; built `GF`, `GFD`, `GFv2` and `GFw` as rule lists
with the ranks of 2.4; and ran `lex`, `parse` (cap 2 and the caps of 8.4), `Grammar.wf`, `terminatorFree`,
`Lexicon.valid`, `Lexicon.failures` and `Prepared.steps` under `#guard` and `#eval` for every computed row of
section 8. All checks passed on 2026-10-04 under Lean 4.24.0 for draft 1.

**For draft 2 the stub was amended and re-run** the same day, against the same build, and every check passed:

- the signature of 5.2 (`ConstVal`, `TermVal`, the `Sem` table over the S1 `Ty`, `fixedActs`, `lexActs`,
  `acts` and `grammar` as definitions, `ranks`) and the statements of 5.6 in their draft 2 form
  (`read_stopped` with its two added conclusions, `translate_exact` without the `wf` premise,
  `grammar_extension` over the `Extends` of 5.4) elaborate as `Prop`s; `grammar_rules` is `rfl`. The S1 `Env`
  has no `args` or `sort` fields, so the stub carries the signatures beside it in a structure `EnvS2` (the S1
  `Env` plus `predArgs : List (String × List String)` and `constSorts : List (String × String)`) and `envSub`
  compares them by `lookup`; the real `Env.decode` puts them in `PredDecl` and `ConstDecl` (2.3);
- `GF`, `GF3` (the extended `F` of e34), `GFD`, `GFv2`, `GFw` with the coordination rows over `term` and the
  ranks of 2.4: `Grammar.wf` and `terminatorFree` true, 117 rules, `|G|` = 479, 37 nonterminals, the longest
  fixed right-hand side 28;
- every verdict of 8.1, 8.3, 8.4 and 8.5, b48 (now `one`) and the new rows b49 to b55 included, with the
  spines of b48 and b50 as 8.1 states them;
- the steps of 8.6, unchanged.

The `kwMid` rows c1 to c3, the V3 row l4, e51, e52 and e53 stay obligations. The file is re-created from this
specification when S2.1 starts; its contents are sections 2.4 to 2.6, 5.2 to 5.4 and 8. Nothing was re-run
for drafts 3 to 5 (sections 14 to 16); for draft 5 the unchanged stub was elaborated once more against the S1
build, with the same results (section 16).

## 13. The statement review's edits (draft 2)

The review (`manage-agents/debates/english-lean-s2-spec`, Astra and Fable, two rounds on 2026-10-04) converged
on FIX with one joint list. Draft 2 applies all of it and nothing else. Where the two texts differ, the
resolution recorded in the second round governs.

| # | Finding | Applied in |
|---|---|---|
| 1 | `declaration.named` accepted a label of another sort (`For every service named P1, P1 is reviewed.`) | `label s` carries its sort; `declNamed` rejects `sortMismatch` (2.6, 2.7); b49, e48 |
| 2 | `Env` had no argument sorts or constant sorts, which the lexical rules and the sort checks need; nothing may recover them through `source` | `PredDecl.args`, `ConstDecl.sort`, filled by `Env.decode`; `source` read by `typedDocument` only (2.3) |
| 3 | `grammar_extension` was unprovable: `RuleMap.Ok` needs equal action terms, and names and arities do not fix the lexical actions | `acts E L = fixedActs ++ lexActs E L`, `fixedActs` closed, sorts carried in values; `envSub` keeps `args` and `sort`; the base-profile premise; the argument of 2.13; q7 (2.7, 2.13, 5.2, 5.4) |
| 4 | The tree correspondence was false: Lark's coordination takes `term`; b48 has one Lark derivation; subject relatives with `{0}` not first and object relatives with ` {1}` not final are cut differently | the table mirrors Lark, the hand parser's scope, name-form, distinctness and sort conditions are actions with the code `coordinationForm`; b48 is `one` with `pronounUnresolved`; relatives cut as Lark cuts them; ranks recomputed (2.4, 2.5, 2.6, 2.7, 2.8, 2.11); b53 to b55, e50, e51 |
| 5 | `everySubject` blocked a negation only under `natural-tail.relative`; Python checks before `and` | the check covers `natural-tail.both` (2.7); b50, e49 |
| 6 | b46 and b47 bind `that service` twice and are `shadowedName`; a positive reach document needs `closure@0`, which base `F` lacks | e43 rewritten; b51, b52 under `F` and under `F` plus `closure@0`; `fixedRules` for a profile list with `closure@0` (2.5, 2.7, 8.1, 8.2) |
| 7 | The nesting increments of `for every`, `such that` and reach bodies were unstated, so `nestingLimit` would fire a level late; `copulaRel` was used and undefined | the increments of `child()` and the `nest` action; `copulaRel p` (2.7) |
| 8 | Fallback nouns `entity of sort "s"` have a quoted token; `c:n₁ … c:nₘ` lost it | nouns and natural subjects lexed as wordings; `noun s n`, `natSubject p s n` carry the text (2.6) |
| 9 | The dispatched unit was unstated: `_parse_english_document_uncached` runs `check_document` and `_check_conclusions`; e44's conclusion was not entailed | D16; 2.10; the G2 comparison at that boundary and `conclusion_rejected` (2.11, 4.5); e44 uses `Therefore it is deployed.` |
| 10 | e47 compared encodings of rejected results | restricted to `ok` results (8.2) |
| 11 | `read_stopped` omitted the typed and start-type conclusions; `translate_exact`'s `wf` premise was redundant; D5 contradicted `read`; "A has a binder" was undefined; `kwMid` had no export encoding | 5.6; D5; 2.7 (`_has_discourse_binder`); 2.9 and 4.4 (`{"kwMid": word}`) |

One consequence the review did not name follows from its item 4 and is recorded here: under Lark's cut a
subject relative can begin with `term`, so `relative` and the nonterminals that begin with it move up one rank
(2.4). Draft 2 gave the wrong example for it, a wording that begins with `{1}`; Lark strips that wording's
leading `term ` as well, and the case that remains is a wording whose first two symbols are holes (section 14;
the ranks are unchanged). One choice was the editor's: the hand parser's two
preconditions on coordination (empty scope, name-form subjects) share one new code, `coordinationForm`, because
Python's behaviour is the same for both (2.8); the DRI may split it (Q2).

The review's closing condition: the stub is re-run on the amended fixtures and ranks (done, section 12), and
PASS follows a bounded re-check limited to these edits and their consequences (exact statements against 3.4, the
extension premises and the action construction, the regenerated fixtures, the Python comparison at the
dispatched boundary). Python authority, the frozen W1, soft and P0 contracts and the signed-widening rule are
untouched.

## 14. The verification pass's corrections (draft 3)

The first verification pass of draft 2 (`manage-agents/english-lean-s2-p3ver1.final.md`, read-only, 2026-10-04)
returned FAIL on two inconsistencies and found no unrelated substantive change. Draft 3 applies the two and
their consequences, and nothing else.

| # | Finding | Applied in |
|---|---|---|
| 1 | 2.5 gave the nine `formula.*` rows the action `through`, while 2.7 says `nest` alone checks `nestingLimit`: the nesting check was unwired | the nine rows take `nest` (2.5); 2.7 unchanged |
| 2 | 2.6 stripped the leading `⟨term⟩` of a subject relative only when the wording begins with `{0}`, while Python's generator strips any leading `term ` (`english.py:1924`): for `{1} follows {0}` Python generates `relative → follows term` and the specification generated `relative → term follows term`, so the one-to-one correspondence was false and 2.4's reason for `relative`'s rank repeated the error | the subject-relative row strips the leading `⟨term⟩` whichever hole it is (2.6); the two-cuts paragraph becomes three corners (2.6); `relSubject` tells them apart from `order` and its term count (2.7); 2.11 names the cut exactly; 2.4 gives the right reason for rank 2 and keeps the ranks; the note of section 13 is corrected |

Two consequences of finding 2 were not in the verifier's text and are recorded here. First, the corrected rule
derives texts that the hand parser never accepts: its own subject cut strips a leading `{0} ` only
(`english.py:1054`), so for a wording whose first symbol is a hole other than `{0}` its pattern keeps a leading
term, which either misses the text (the sentence falls to `unknown_atom`, `:1101`, `SyntaxError`) or, as the
second verification pass showed, re-segments it into an atom with one argument too many that `check_document`
rejects (section 15; draft 3 claimed the first outcome alone). An action that built a formula there would accept
what Python rejects, the unsafe direction, so `relSubject` rejects, and the rejection needs a code. It is a fourth
tier B code, `relativeForm`, in the family the statement review created for hand-parser-only rejections that fall
to `unknown_atom` (`coordinationRepeated`, `coordinationForm`), mapping onto `SyntaxError` like them when the
pattern misses (D6, 2.8, 3.2, 4.2, 7, 10.5, Q2; section 15 adds the second class); fixture e52 (an obligation)
pins it. Second, the rank array is unchanged: `relative` stays at 2
because a subject relative can still begin with `term`, for a wording whose first two symbols are holes, which
base V3 allows (2.4).

Nothing was re-run. No figure of section 12 depends on either correction: the stub evaluates no action, so the
`through`/`nest` column is outside it, and every wording of `F`, `LF`, the extended `F` of e34, `FD` and the
lexicon of l2 begins with `{0}`, so no fixture grammar has a rule whose shape the second correction changes.
The second verification pass re-checked these edits, confirmed both, and returned one finding on the first
consequence above (section 15).

## 15. The second verification pass's correction (draft 4)

The second verification pass (`manage-agents/english-lean-s2-p3ver2.final.md`, read-only, 2026-10-04) confirmed
both corrections of section 14 (all nine `formula.*` rows take `nest`; subject relatives strip the leading term
whichever hole it is), found no unrelated substantive edit, and returned FAIL on one finding. Draft 4 applies it
and its consequences, and nothing else.

| # | Finding | Applied in |
|---|---|---|
| 1 | Draft 3 assumed that the hand parser's pattern matches no text that the `{1}`-first subject relative derives, and mapped `relativeForm` onto `SyntaxError` alone. Counterexample: the wording `{1} {0} are related` with persons spelled `alice`, `bob` and `alice bob`; for `Every person alice bob are related.` Lark's relative reads the one constant `alice bob`, while the hand parser's pattern reads two terms, `alice` and `bob`, prepends `var 0` (`english.py:1089`) and builds a three-argument atom that `check_document` rejects: it does not fall to `unknown_atom` | 2.6 (the second corner has two Python outcomes); 2.7 (`relSubject`'s reason); 2.8 (the `relativeForm` row and the class paragraph); 2.11 (G2 accepts either class for `relativeForm` and records which); 4.2; 9; e52's reason; e53 (an obligation); Q2; the record of section 14 |

What the correction keeps and what it changes. The rejection stays unconditional on Lean's side, because Python
never accepts a text the rule derives: the hand parser's pattern has one term group more than the rule has terms,
so when it matches it builds an atom of arity plus one, and when it does not match the text falls to
`unknown_atom`. What changes is the claim and the class: the action sees its term children, not the text, so it
cannot tell a re-segmented text from a missed one, and `relativeForm` is mapped onto both `SyntaxError` and the
`illTyped` class, G2 accepting either and recording which (2.8, 2.11). This is the smallest correction that makes
the specification true. Making the action reproduce the hand parser's re-segmentation would put the text inside an
action, against the action design of 2.7 (values and a context, not text); excluding the wording by validity would
move the hole-order rule of `TEMPLATE_SHAPE` from E2 into S2, against DRI ruling 4, under which the retained lint
codes stay Python checks in S2 (2.14). Neither was asked for. Once that rule is a V3 condition (E2), no valid
lexicon reaches the corner.

Nothing was re-run. No figure of section 12 depends on the correction: the stub evaluates no action, e53 is an
obligation like e51 and e52, the ranks are unchanged, and every wording of the fixture grammars begins with `{0}`.
The third verification pass re-checked these edits, confirmed them, and returned one finding on the Python class
named for the `check_document` rejection (section 16).

## 16. The third verification pass's correction (draft 5)

The third verification pass (`manage-agents/english-lean-s2-p3ver3.final.md`, read-only on `32409057`,
2026-10-04) confirmed the correction of section 15 (the re-segmentation explanation, e53 and the plan's record
are present; the earlier corrections stand; no unrelated substantive change) and returned FAIL on one finding.
Draft 5 applies it and its consequences, and nothing else.

| # | Finding | Applied in |
|---|---|---|
| 1 | e53 is stated under `F`, which lacks `nary@0`; its three-argument atom is rejected by `check_document` at `ast.py:272` with `UnsupportedProfile`, before the arity check, while the inherited `IllTyped` row (base 4.2) lists `UnknownSymbol` and `TypeMismatch` only, so the "`SyntaxError` or `illTyped` class" rule of section 15 did not explicitly cover its own counterexample | 4.2 (the amended `IllTyped` row and its paragraph); 2.5, 2.6, 2.8, 2.11; e43, e51, e53; 9; 10.12; Q2 |

The same kind of gap was looked for across the specification: for every fixture that expects a rejection, the
Python class named was re-read against the check that fires first on Python's path
(`_parse_english_document_uncached`, `english.py:1636–1665`: the hand parser, then the Lark audit, then
`check_document`, then `_check_conclusions`), and every claim that Python's parser cannot match a text was re-read
against the patterns it builds. Three more findings, the first the verifier's under other fixtures:

- e51 (a wording that begins with a word) and e43's b51, b52 under `F` rely on the same two `check_document`
  rejections, the `Atom` check (`ast.py:272–273`) and the `Reach` check (`:281–282`), both `UnsupportedProfile`.
  Their class is now named (8.2), as is 2.5's remark on reach. The class is the Python checker's: `typing` has
  `authority: python` in `ve/assurance-manifest.json`, and `check_document` runs the Python checker under it
  (`ast.py:377–385`).
- the re-segmentation corner of 2.6 has a third Python path that section 15's two did not name: inside a guard,
  where object relatives are allowed (`english.py:1284–1285`), the object alternative of the same `{1}`-first
  wording matches the same span (its cut deletes nothing from a wording without ` {1}`, `:1056`), and the hand
  parser's ambiguity guard rejects the clause (`:1104–1107`, `SyntaxError`) before `check_document` is reached.
  The class is one of the two G2 already accepts, so the rule of section 15 is unchanged; 2.6, 2.8 and e53 now
  say which path fires where. Nothing between the hand parser and `check_document` fires for e51 or e53: each has
  one Lark derivation, and `require_correspondence` (`ve/surface/unambiguity.py:81–103`) checks extension
  readings only, which the natural hook does not produce for them (`_natural_parser`, `english.py:1966–1969`,
  `natural_clause`, `:1508–1548`).
- 2.8's `coordinationRepeated` row said the text falls to `unknown_atom`; for the predicate form (b35) the
  hand parser reads the leading atom and misses the sentence end at the comma instead (`:1625`). `SyntaxError`
  either way; the row says so.

Every other rejected fixture's class was confirmed as stated, each at the check that fires first: e33
(`need('(a) ')`, `:1414`), e34 and e50 (`coordination` returns `None`, `:1572–1613`; `unknown_atom`, `:1267`),
e41 and e49 (`:1540`), e42 (`_natural_parser` returns `None` under a binder, `:1967`; then `unknown_atom`),
e43's b46 and b47 (`:943`, before the sort check of `:1472`), e45 (`:1071–1072`, then `unknown_atom`), e46
(`unknown_atom`), e48 (`need(', ')`, `:1438`), e52 (`unknown_atom`, `:1101`): all `SyntaxError`, as the codes
they map onto require. The claims that Python cannot match a text hold as written: e52's pattern needs a term
spelled `follows` or beginning with it, and `F`'s terms are `that person`, `alice`, `legacy`, their `the`
forms and, when resolved, `it` (`term_options`, `:948–962`); e51's object alternative matches a shorter span
and loses to the longest match (`:1104`); Lark's object relative of a `{1}`-first wording carries the literal
text `{1}` (`:1926–1928`), which no lexed sentence contains.

What the correction keeps. The `illTyped` outcome, `typedDocument`, the four codes, the rule that G2 accepts
either class for `relativeForm`, and every Lean statement are unchanged; the one change is the class list behind
`illTyped` in the comparison, stated in 4.2 as this stage's reading of base 4.2 (the base row itself is amended
when the base spec is next revised). No public message or code changes. Nothing was re-run for the figures of
section 12, which depend on no class; the stub of section 12, unchanged, was elaborated once more against the
`english-lean/integrate` build (checkout at `83eeec56`): every statement a `Prop`, every `#guard` passing, the
same counts, spines and steps. It is not committed (section 12); the sandbox of this session refused to delete
it, so the untracked file remains in the worktree. The next step is a bounded re-verification of the edits of
this section; PASS follows that re-verification, not this draft.
