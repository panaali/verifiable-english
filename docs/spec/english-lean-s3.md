# English in Lean, S3 + E2: the profiles and the authority (statement specification)

> Status: statement specification, draft 1 (2026-10-05), branch `design/english-lean-s3`. This is the item-1
> statement spec of [english-lean-S3-PLAN.md](english-lean-S3-PLAN.md) draft 2 (the **plan**). It writes out stage
> S3 of [english-lean-PLAN.md](english-lean-PLAN.md) (the **base plan**) and track E2 of `docs/LEAN-FIRST-PLAN.md`
> (branch `design/lean-first`) on top of [english-lean.md](english-lean.md) draft 2 (the **base spec**) and
> [english-lean-s2.md](english-lean-s2.md) draft 5 with its integration amendment (the **S2 spec**), whose reader is
> built and proved on `main` at `1e68d6d6`. Definitions and statements of those two are not repeated; `base 2.9`
> and `S2 2.6` refer to them. **Nothing was built for this draft.** What was run: a scratch file imported the S2
> build and (a) wrote the profile rows of 2.5 and 2.6 and the actions of 2.7 by hand over the S2 `sig`, (b)
> elaborated every definition and statement of section 5, each unproved statement as a definition of type
> `Prop`, and (c) computed every verdict, formula, rejection, validity result, count and step figure of section
> 8 with the proved parser, the S2 reader and the S2 `Lexicon.valid` (section 12). A fixture marked
> *obligation* was not computed. **Python's outcome on each fixture was read from `ve/english.py`, not run**; S3.5
> runs it, and a difference there is a finding, not a failed fixture. Every `file:line` was read on 2026-10-05
> in this worktree and must be re-read at each step. Under S3 nothing changes a verdict, an identity, a public
> code or an existing theorem statement; E2 changes who decides, and lists every visible change in its
> `DELTA.md`.

## 0. Scope, one paragraph

S3 extends the English instance to the formula-level surfaces of five profiles: integer terms and comparisons
(`order@0`), attribute sugar (`data@0`), the guard phrases (`alternatives@0`), the risk wordings and their
blocked forms (`risk@0`), and the modal wording of regulated predicates (`norms@0`). It adds two fixed tables,
four lexical families, the actions for them, one validity condition, and the comparison harness that S2 left
owing. E2 then makes Lean the authority for `english.admission`: an admission function that returns the reading
and the obligations of the marked conclusions, Lean's codes and texts as the ones shown, a check of rendered
candidates, the lint codes that change acceptance as a validity condition, and Python's parser as a comparator
that decides nothing. Statement-layer English is E3.

In this specification: the decisions (1), the definitions (2), the English of every new wording, outcome and
claim (3), the diagnostics (4), the Lean definitions and the exact statements (5), files and gates (6), what is
consumed and returned (7), the acceptance fixtures (8), limits (9), the statement review checklist (10), the
open points (11), and how the figures were computed (12).

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | `grammar E L` is `fixedRules E.profiles` followed by `lexRules E L`, as in S2. The fixed table of a profile list is the base table, then the `order@0` table when that profile is named, then the `alternatives@0` table when that one is. `data@0`, `risk@0` and `norms@0` have no table: their rows are lexical or they only fix wordings | 2.5, 5.2 |
| D2 | A profile list that names none of `order@0`, `data@0`, `alternatives@0` gets exactly S2's fixed rules, actions and rank certificate. The base table source is not edited | 2.4, 5.5 (`unstaged_fixed`), ev1 |
| D3 | One rank certificate, `ranksStaged`, serves every other profile list; the property nonterminals are appended with rank 0 | 2.4 |
| D4 | S3 adds no constructor to `Ty`, no field to `Ctx` or `TermVal`, and no rejection code. Integer depth reuses `Ctx.nesting`; a text value reuses the type `listMarker`; a property reuses `adjective` | 2.4, 2.7, 2.8 |
| D5 | Integer terms mirror Lark's rules (`int_term`, `int_atom`, `int_neg`), with four small nonterminals for the marks whose spacing varies. A signed numeral is the sign and a numeral token (base O2) | 2.2, 2.5 |
| D6 | The attribute-property product is factored over one property nonterminal per value sort (base D13, converged edit 1). Derivations stay one to one | 2.6, 2.11, da17 to da20 |
| D7 | The guard rows are lexical: they hold the action noun, exactly as written. The verb of a guard is a relative, or the guard's own reference followed by a relative or by `is the same as` and a term. This is the hand parser's acceptance stated as rules | 2.6, 2.11 |
| D8 | V3 gains "subject first": a selected wording, negative or alias begins with `{0}` and a space, and its holes are in increasing order | 2.9, lx12, lx13 |
| D9 | `risk__more_severe` has the fixed wording `{0} is more severe than {1}` (DRI ruling 2) | 2.9, ri7, lx3 to lx6 |
| D10 | After the flip the admission function is `admit`: `read`, then the obligations of the marked sentences. A marked sentence with no earlier unmarked sentence is refused by Lean. The proof of each obligation stays with the entailment operation | 2.10, 5.3, 5.5 |
| D11 | Lean's codes and texts are the ones shown (LEAN-FIRST DRI answer 3). A sentence without a reading may carry one advice from a fixed table; advice never changes a verdict | 4.2, 4.3 |
| D12 | The hand parser and the Lark audit are a comparator: on only in gate runs, logged, never able to change a result. `EnglishParser` stays for the statement layers until E3 | 2.10 |
| D13 | A rendered candidate is displayed only if `checkRendering` is true for it; the service returns the first such candidate of a list | 2.10, 5.3 |
| D14 | The five lint codes that change acceptance become V6 of `Lexicon.valid` in E2.1; the flip waits for it | 2.9 |
| D15 | `Extends` is restated for any one profile list, with a renaming of the property nonterminals | 2.13, 5.4 |
| D16 | No type, wire form or identity preimage that the senses layer reads changes: `Lexicon`, `ve.english-lexicon@1`, the six identities | 2.14 |

## 2. Definitions

### 2.1 Terms

| Term | Meaning |
|---|---|
| staged profile | `order@0`, `data@0` or `alternatives@0`: a profile whose presence changes the rules of the grammar |
| integer slot | a hole of a wording whose argument sort is `$int`, in an environment that names `order@0` |
| object slot | any other hole |
| integer constant | a constant of sort `$int` in an environment that names `order@0` |
| attribute | a binary predicate declared functional and total, in an environment that names `data@0` |
| value sort | the second argument sort of an attribute, when it is not `$string` |
| property of a sort | a unary predicate on that sort |
| guard | one of the three phrases `every N available to`, `every other N available to`, `another N available to`, where `N` is the selected noun of the action sort |
| reference action | the innermost binding of the action sort in scope where a guard is written |
| guard's own reference | `that N` inside an `every` guard, `that other N` inside the other two |
| obligation | a marked sentence with the earlier unmarked sentences of its document |
| comparator | Python's hand parser with the Lark audit, run beside Lean after the flip |

### 2.2 Tokens and the spacing of the integer marks

The tokens, terminals and lexer are S2's. `[`, `]`, `+`, `-`, `*` are punctuation tokens with their `glued`
flags; a numeral token is not negative. The fixed rules accept exactly the spacing the hand parser accepts
(DRI ruling 1):

| Mark | Flags accepted | Python |
|---|---|---|
| `[` | `gluedAfter` true; `gluedBefore` either | a term follows at once (`english.py:1166–1169`) |
| `]` | `gluedBefore` true; `gluedAfter` either | (`:1175–1177`) |
| a sign `-` before a term or a numeral | `gluedAfter` true; `gluedBefore` either | (`:1157`, `:1196`, the numeral pattern `:1139`) |
| an operator `+`, `-`, `*` | both flags false | the operator is `' + '`, `' - '` or `' * '` (`:1171–1172`) |

So `[budget+1]`, `[ budget + 1]` and `- budget` have no derivation (or22 to or26).

### 2.3 The reader's inputs

`Env` and `PredDecl` gain fields, all with defaults, so every S2 producer and fixture is unchanged:

| Field | Meaning | Read by |
|---|---|---|
| `PredDecl.functional`, `PredDecl.total : Bool := false` | the declaration's flags | the attribute family (2.6) |
| `Env.alternatives : Option AltBlock := none` | the block's action, chooser and harm sorts and its `available` and `leads_to` predicates | the guard family (2.6) |
| `Env.risk : Bool := false` | whether the environment has a risk block | the guard action (2.7) |

`Env.decode` fills them from the environment JSON and, as Python's display environment does, adds the symbols
that the blocks generate and the forms that they fix:

- `alternatives@0` (`ve/environment.py:661–664`, `english.py:393–414`): the predicates `avoidable` and
  `unavoidable` over harm and chooser, `allows` and `prevents` over action and harm; the wordings of the role
  predicates as declared, `{0} is avoidable by {1}`, `{0} is unavoidable by {1}`, `{0} allows {1} to happen`,
  `{0} prevents {1}`; the aliases `{0} is preventable by {1}` (`avoidable`), `{0} lets {1} happen` (`allows`)
  and, without a risk block, the negated alias `{0} does not lead to {1}` of the `leads_to` predicate.
- `risk@0` (`environment.py:668–678`, `english.py:415–468`): the severity sort with the noun `severity`, its
  classes as constants, and the predicates `risk__might_lead_to`, `risk__class`, `risk__more_severe`,
  `risk__or_worse`, `risk__less_worst`; the wordings of 3.1; `prevents` becomes `{0} might prevent {1}`; the
  negatives `{0} might not lead to {1}` (of `leads_to`) and `{0} cannot lead to {1}` (of
  `risk__might_lead_to`).
- `norms@0` (`english.py:519–525`): for a predicate regulated as a permission or an obligation with act
  phrase `a`, the wording `a` with `{0} ` replaced once by `{0} may ` or `{0} must `; it has no negative.

`rights@0` wordings are installed by the rights correlation on a derived environment (`ve/rights.py:542`); Lean
does not compute them in this stage (plan, question 6). `Overlay` and `Lexicon` are S2's. The budget is
`workBudget`, the design point 300 tokens (DRI ruling 5).

### 2.4 Nonterminals, types and ranks

The catalogue of S2 (0 to 36) is unchanged. S3 appends fourteen fixed nonterminals and, per environment, one
property nonterminal per value sort.

| # | Nonterminal | `Ty` | Value |
|---|---|---|---|
| 37 | `int_term` | `intTerm` | context → term |
| 38 | `int_atom` | `intTerm` | |
| 39 | `int_neg` | `intTerm` | |
| 40 | `int_constant` | `constant` | the constant's name, the sort `$int` |
| 41 | `int_plain_constant` | `constant` | the same, for a spelling of one lower-case word |
| 42 | `numeral` | `intTerm` | the numeral as a term |
| 43 | `int_op` | `listMarker` | the operator's text |
| 44 | `minus` | `unit` | |
| 45 | `lbracket` | `unit` | |
| 46 | `rbracket` | `unit` | |
| 47 | `alt_available_guard` | `formula` | |
| 48 | `alt_verb_phrase` | `relative` | context → formula whose subject is `var 0`, the guard's action |
| 49 | `alt_verb_atom` | `relative` | |
| 50 | `alt_head` | `listMarker` | the reference text it spells |
| 51 + i | `property_i` | `adjective` | a property of the i-th value sort: its name and that sort |

`valueSorts E` lists the value sorts of `E` without repeats, in the order of the first attribute of
`E.predicates` that has each. `ty E L n` is `ntTy n` below 37, the table above from 37 to 50, `adjective` for
the `(valueSorts E).length` numbers from 51, and `tok` beyond. It does not depend on `L`.

**Ranks.** `ranksFor profiles` is S2's `ranks` when no staged profile is named, and otherwise `ranksStaged`:

```
ranksStaged = [6, 0, 5, 4, 0, 0, 0, 0, 0, 2, 6, 6, 5, 0, 0, 0, 1, 1, 0, 0, 0, 4, 4, 0, 1, 0, 5, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0,
               3, 2, 1, 0, 0, 1, 0, 0, 0, 0, 0, 6, 5, 0]
```

`atom`, `relative` and `object_relative` rise to 4 because a clause, a subject relative of a wording whose
second symbol is an integer hole, and an object relative of a wording whose `{0}` is an integer slot can begin
with `int_term` (rank 3); the nonterminals above them rise with them. The grammar's `rank` is `ranksFor
E.profiles` followed by a 0 for each value sort. `Grammar.wf` holds for every fixture grammar of section 8,
for every profile's rows together (cb1), and for an S2 grammar under either certificate; S2's certificate does
not fit the integer rows (sz7).

### 2.5 The fixed rules of `order@0` and `alternatives@0`

Notation as S2 2.5. A mark written `[·` is `[` with `gluedAfter` true; the two rows of `lbracket`, `rbracket`
and `minus` are the two values of the free flag (2.2).

**`order@0`** (25 rows; `english.py:1984–1997` and `:50–51`):

| Tag | Rule | Action |
|---|---|---|
| `int-term.atom` | `int_term → ⟨int_atom⟩` | `through` |
| `int-term.minus` | `int_term → ⟨minus⟩ ⟨int_neg⟩` | `intNegate` |
| `int-atom.constant` | `int_atom → ⟨int_constant⟩` | `intConst` |
| `int-atom.numeral` | `int_atom → ⟨numeral⟩` | `through` |
| `int-atom.bracket` | `int_atom → ⟨lbracket⟩ ⟨int_term⟩ ⟨int_op⟩ ⟨int_term⟩ ⟨rbracket⟩` | `intBracket` |
| `int-atom.twice` | `int_atom → twice the ⟨int_plain_constant⟩` | `intTwice` |
| `int-neg.constant` | `int_neg → ⟨int_constant⟩` | `intConst` |
| `int-neg.bracket` | `int_neg → ⟨lbracket⟩ ⟨int_term⟩ ⟨int_op⟩ ⟨int_term⟩ ⟨rbracket⟩` | `intBracket` |
| `int-neg.minus` | `int_neg → ⟨minus⟩ ⟨int_neg⟩` | `intNegate` |
| `numeral.plain` | `numeral → cls numeral` | `numeral false` |
| `numeral.signed` | `numeral → ⟨minus⟩ cls numeral` | `numeral true` |
| `int-op.plus` `.minus` `.times` | `int_op → +` \| `-` \| `*`, free on both sides | `op` |
| `minus.free` `minus.glued` | `minus → -·` | `unit` |
| `lbracket.free` `lbracket.glued` | `lbracket → [·` | `unit` |
| `rbracket.free` `rbracket.glued` | `rbracket → ·]` | `unit` |
| `atom.int-eq` | `atom → ⟨int_term⟩ c:is c:the c:same c:as ⟨int_term⟩` | `intCmp eq` |
| `atom.less` | `atom → ⟨int_term⟩ c:is c:less c:than ⟨int_term⟩` | `intCmp lt` |
| `atom.at-most` | `atom → ⟨int_term⟩ c:is c:at c:most ⟨int_term⟩` | `intCmp le` |
| `atom.more` | `atom → ⟨int_term⟩ c:is c:more c:than ⟨int_term⟩` | `intCmp lt`, swapped |
| `atom.at-least` | `atom → ⟨int_term⟩ c:is c:at c:least ⟨int_term⟩` | `intCmp le`, swapped |

`int_neg` has no numeral and no `twice` row, as in Lark, so `--5` and `-twice the budget` have no derivation
although the hand parser's pattern matches them (or20, or21): Python's audit finds no derivation and rejects.

**`alternatives@0`** (8 rows; `english.py:1934–1942`, `:1329–1346`):

| Tag | Rule | Action |
|---|---|---|
| `formula.alternatives` | `formula → ⟨alt_available_guard⟩` | `nest` |
| `verb-phrase.one` | `alt_verb_phrase → ⟨alt_verb_atom⟩` | `through` |
| `verb-phrase.either` | `alt_verb_phrase → either ⟨alt_verb_atom⟩ or ⟨alt_verb_atom⟩` | `relOr` |
| `verb-phrase.either-both` | the same followed by `, or both` | `relOr` |
| `verb-phrase.both` | `alt_verb_phrase → both ⟨alt_verb_atom⟩ and ⟨alt_verb_atom⟩` | `relAnd` |
| `verb-atom.relative` | `alt_verb_atom → ⟨relative⟩` | `through` |
| `verb-atom.subject` | `alt_verb_atom → ⟨alt_head⟩ ⟨relative⟩` | `verbSubject` |
| `verb-atom.same` | `alt_verb_atom → ⟨alt_head⟩ c:is c:the c:same c:as ⟨term⟩` | `verbSame` |

Lark writes `alt_verb_atom: relative | atom`. The hand parser reads an atom there only when the text starts
with the guard's own reference and a space, compared exactly (`:1330–1333`), and a relative otherwise. An atom
that starts with that reference is a clause of a subject-first wording, which is the reference followed by
that wording's subject relative, or the equality. The two rows `verb-atom.subject` and `verb-atom.same` are
those two cases (D7; the correspondence is in 2.11).

### 2.6 The lexical rules

S2's families stand, with one change to the first three and four new families. In an environment that names
`order@0`, a hole is `⟨int_term⟩` when it is an integer slot and `⟨term⟩` otherwise.

| Family | For | Rules | Action |
|---|---|---|---|
| clause | as S2 | as S2, each hole by its slot kind | `pred p order negated` |
| subject relative | as S2, **when `{0}` is an object slot** (`english.py:1978–1979`, `:1028`) | the clause without its leading `⟨term⟩` | `relSubject p order negated` |
| object relative | as S2, **when `{1}` is an object slot** (`:1980`, `:1029`) | the clause without ` {1}` | `relObject p negated` |
| spelling | a constant that is **not** an integer constant | as S2 | `const c s nf` |
| integer constant | an integer constant `c` with selected spelling `sp` (`:1989`, `:1993–1995`) | `int_constant → sp` (one `kw` per word); when `sp` is one lower-case word, also `int_plain_constant → sp` | `const c "$int" false` |
| attribute | an attribute `r` over `s₁ s₂` (`:1959–1961`) | `atom → the r of ⟨term⟩ is ⟨term⟩` | `attribute r` |
| attribute property | the same, when `s₂` is the i-th value sort (`:1962–1965`) | `atom → the r of ⟨term⟩ is ⟨property_i⟩` | `attributeProperty r s₂` |
| property | a unary predicate `p` on the i-th value sort (`:1966–1967`) | `property_i → p` | `adjective p s` |
| guard | the block's action sort `a` with selected noun `N` (`:1936–1938`, `:1301–1303`) | `alt_available_guard → every N available to ⟨term⟩ ⟨alt_verb_phrase⟩`; `… → every other N available to ⟨term⟩ ⟨alt_verb_phrase⟩`; `… → another N available to ⟨term⟩ ⟨alt_verb_phrase⟩`; the last two also with `excluding ⟨term⟩` before the verb phrase | `guard mode excluding` with the data `a`, `N`, the `available` predicate and the risk flag |
| guard head | the same | `alt_head → that N`; `alt_head → that other N` | `altHead` with the text spelled |
| other reference | the same (`:1935`) | `term → c:that c:other c:N` | `termOther N` |

Notes.

- **Names are written exactly.** In the attribute and property rows `r` and `p` are the identifiers, one `kw`
  terminal for the token the lexer gives each (Lark's `lit(name)`, `:1959`, `:1962`; the hand parser's
  `re.escape(name)`, `:989`, `:1004`). `the`, `of`, `is` are `kw` terminals.
- **The guard rows are exact too.** `every`, `other`, `another`, `available`, `to`, `excluding` and the words
  of `N` are `kw` terminals, because the hand parser reads the whole prefix with an exact `take` (`:1301–1304`,
  `:907–916`). Lark's noun terminal there ignores case; a capitalised noun has one Lark derivation, a
  hand-parser rejection, and no Lean derivation (al25, 2.11). The `alt_head` rows are exact for the same reason
  (`:1331`). The reference `that other N` elsewhere matches in any case, as Lark's and the hand parser's do
  (`:964–966`; al30).
- **Subject first is assumed.** The cut of a subject relative and the two head rows are right only for a
  wording that begins with `{0}`. V3 guarantees it (2.9).
- A wording of an integer `{0}` has no subject relative, and one of an integer `{1}` no object relative. An
  object relative of a wording whose `{0}` is an integer slot begins with `⟨int_term⟩` (cb1 holds such rows).

### 2.7 The action library

`acts E L = fixedActs E.profiles ++ lexActs E L`. The fixed actions of a profile list are the actions of its
fixed rows, in table order; they read neither `E` nor `L`.

**Integer terms.** An integer term is evaluated at a depth, kept in `Ctx.nesting`: a clause runs each of its
integer terms at depth 1, whatever the nesting of the formula. This is Python's `int_syntax` (`:1148–1179`).

| Action | Arguments → result | Value |
|---|---|---|
| `intNegate` | `unit, intTerm → intTerm` | `scale (-1) t`, the child one level deeper |
| `intConst` | `constant → intTerm` | `nestingLimit` when the depth exceeds 64; else `const c` |
| `intTwice` | `constant → intTerm` | the same check; `scale 2 (const c)` (`:1188–1195`) |
| `numeral negative` | the numeral token (after `minus` when negative) → `intTerm` | the same check; then `numeralBound` when the digits, plus one for the sign, are more than 40 characters (`ve/ast.py:177`, `:204–209`); else `num v` or `num (-v)` |
| `intBracket` | `unit, intTerm, listMarker, intTerm, unit → intTerm` | the same check; the left term one level deeper, the right term one level deeper, or two after the operator `-` (`:1169–1175`); then `add a b` for `+`, `add a (scale (-1) b)` for `-`, and for `*`: `scale k b` when `a` is `num k`, else `coefficientNotNumeral` (`:1212–1216`). If either operand fails with `nestingLimit`, that is the result |
| `op` | the token → `listMarker` | its text |
| `intCmp k`, swapped or not | `intTerm, intTerm → formula` | both terms at depth 1; `eq`, `lt` or `le` of them, the two exchanged when swapped (`:50–51`, `:1091–1092`); `nestingLimit` first, as in a clause |

**A clause's slots** (`pred`, `relSubject`, `relObject`; `:1063–1090`). The object terms are read first, in
order, the first keeping `leftmost` when it begins the rule; the first rejection among them is the result.
Then, if any integer term fails with `nestingLimit`, that is the result. Then the first other rejection among
the integer terms, in order. Python does the same: an unbound reference keeps the template from matching at
all, the shape and depth of every integer term are checked before any is evaluated (`:1075–1079`), and the
numeral bound and the coefficient are found on evaluation (`:1086–1088`). The formula is S2's, with the
arguments in declaration order.

**Attributes** (`:985–1019`).

| Action | Arguments → result | Value |
|---|---|---|
| `attribute r` | `term, term → formula` | `pred r [t, u]`; **both terms are read with the clause's own `leftmost`**, so `it` resolves in either slot when the attribute starts the sentence's formula, and nowhere else (da12 to da16). The hand parser builds its term table once at the start of the atom (`:971`) and this branch has no check on the position of `it` (`:995–997`) |
| `attributeProperty r s` | `term, adjective → formula` | `ex s (and (pred r [t↑, var 0]) (pred p [var 0]))` with `p` the property and `t↑` the term with a variable's index raised by one (`:1015–1019`); the term is read as above |

**Guards** (`:1296–1367`). `guard mode excluding`, with the action sort `a`, its noun `N`, the predicate
`available` and the risk flag, in this order:

1. for `other` and `another`: the scope must hold a binding of sort `a`, else `unboundReference` (`:1307–1310`);
   let `k` be the index of the innermost one;
2. the owner term is read in the scope, not leftmost; its rejection is the result (`:1318`);
3. with `excluding`: that term is read; it must be a variable whose binding has sort `a`, else `sortMismatch`;
   `k` becomes its index (`:1320–1325`);
4. the binding `(a, "that " ++ N)` for `every`, `(a, "that other " ++ N)` otherwise, is pushed; the verb phrase
   is read under it (`:1327`). No check for a name already in scope is made here, as in Python: inside an
   `every` guard `that N` is the guard's action;
5. for `every` under the risk flag: if the verb's formula is `not (pred risk__might_lead_to [_, _])`, or a
   conjunction or disjunction with such a part, the result is `blockedWording "risk-every-cannot"`
   (`:1349–1360`);
6. the formula: with `A = pred available [var 0, owner↑]` and `B` the verb's formula, `all a (implies A B)`
   for `every`; `all a (implies (and A (not (eq (var 0) (var (k + 1))))) B)` for `other`; `ex a (and (and A
   (not (eq (var 0) (var (k + 1))))) B)` for `another` (`:1361–1367`).

| Action | Arguments → result | Value |
|---|---|---|
| `altHead` | terminals → `listMarker` | the reference text: `that N` or `that other N` |
| `verbSubject` | `listMarker, relative → relative` | the relative, when the head's text is the reference text of the innermost binding; else `unboundReference` |
| `verbSame` | `listMarker, term → relative` | `eq (var 0) t` under the same condition |
| `relOr`, `relAnd` | `relative, relative → relative` | `or a b`, `and a b` |
| `termOther N` | terminals → `term` | the innermost binding whose reference text is `that other N`, else `unboundReference` |

`formula.alternatives` takes `nest`, as every `formula` row does. No action here changes the nesting of a
formula. No action constructs `Reject.internal`.

### 2.8 Side conditions

No code is added (D4). The profile constructs use these, with Python's class today:

| Code | When | Python today |
|---|---|---|
| `nestingLimit` | an integer term deeper than 64 | `ResourceLimit` (`english.py:1160–1161`) |
| `numeralBound` | a numeral longer than 40 characters with its sign | `ResourceLimit` (`ast.py:207–208`) |
| `coefficientNotNumeral` | `[a * b]` with `a` not a numeral | `SyntaxError` (`:1213–1214`) |
| `unboundReference` | `every other` or `another` with no action in scope; an owner or reference that is not bound; a verb head that is not the guard's own reference | `SyntaxError` (`:1310`, `:1314–1316`, `:1274`; the head: unknown phrase, `:1101`) |
| `sortMismatch` | the excluded term is not an action in scope | `SyntaxError` (`:1322–1324`) |
| `blockedWording "risk-every-cannot"` | 2.7, step 5 | `SyntaxError` (`:1360`) |
| `pronounUnresolved` | `it` as an owner, or in an attribute that does not start the formula | `SyntaxError` |

The rejected risk wordings, the condition wordings and the `alternatives@0` advice (`:61–69`, `:82–85`,
`:1247–1264`) are not side conditions: no rule derives those texts, the outcome is `none` (ri17), and the
advice of 4.3 names the rewrite.

### 2.9 The lexicon and its validity

V1, V2, V4 and V5 are unchanged; they now read forms that Lean computes (2.3).

- **`risk__more_severe`** is in the forms of `risk@0` with `{0} is more severe than {1}`. Without it Python's
  lexicon of today fails V1 (lx4, the S0 finding); with the entry and without the form it fails V2 (lx6).
- **Profile negatives and aliases** stay the only ones V2 and V5 accept beyond the declared ones (lx7, lx8).
- **A modal wording has no negative**: `negativeTemplate` of `{0} may access {1}` is none, so a selected
  negative fails V5 (lx11).

**V3 gains subject first (D8).** A selected wording, negative or alias `w` passes when `w` begins with `{0}`
and a space and the holes of `w`, in order of occurrence, are `0, 1, …`. Every idiom, every profile-fixed
form, every mechanical and fallback wording passes (lx12); `the owner of {0} is {1}`, `{1} follows {0}` and
`{1} {0} are related` do not, so the lexicons of S2's fixtures e51 to e53 become invalid (lx13) and the
`relativeForm` branch of `relSubject` is unreachable for a valid lexicon. This is the part of Python's
`TEMPLATE_SHAPE` that a reading depends on (`ve/printer.py:283–286`); it does not require `{1}` last, which
the profile forms and idioms do not satisfy.

**V6, in E2.1 (D14).** For a predicate of one or two arguments whose selected wording is its declared wording
and is neither profile-fixed nor an idiom of its arity, let the phrase be the wording without `{0} ` and,
for two arguments, without ` {1}`, and its words the matches of `[A-Za-z][A-Za-z0-9_]*(-[A-Za-z]+)?`. The
wording passes when none of the five holds, or when the rescue applies:

| Code | Holds when (`printer.py:234–248`, `:298–302`) |
|---|---|
| `LOGICAL_WORD` | a word is in the list of logical words (with the reach words under `closure@0`) |
| `SYMBOL_COLLISION` | a word is the name of another sort, predicate or constant, the head of another predicate's wording, or the last word of another sort's noun |
| `NEGATED_HEAD` | a word is `un`, `non`, `un-` or `non-` joined to a predicate's name or head |
| `BINARY_AUXILIARY` | two arguments, and the first word is one of `is are was were be been being gets got` |
| `BINARY_CONVERSE` | two arguments, and the last word is one of `by to of from with for` |

The rescue is `english.py:274–309`: a wording that matches one of the fixed complement or verb patterns
(`:31–43`), has no collision and no negated head by the stricter tests there, and is at most 80 characters.
E2.1 ports it with its two tables as data; its statement review is bounded to that port. `TEMPLATE_LENGTH`,
`BINARY_VERB` and `IDIOM_UNRELATED` become editor warnings and reject nothing.

### 2.10 Admission, the relay and the comparator (E2)

- **`admit`** (5.3) is `read` followed by the obligations: for each marked sentence `i`, the indices of the
  unmarked sentences before it. If some marked sentence has none, the outcome is `noPremise` with the first
  such index (Python: `A conclusion needs an earlier premise.`, `english.py:1763–1764`). Otherwise the outcome
  is the reading with its obligations.
- **The relay.** `parse_english`, `parse_english_with_metadata` and `parse_english_argument` send the
  environment, the overlay, the lexicon Python's producer selects, and the source; they return Lean's reading
  or raise Lean's code and text. For each obligation the relay calls the existing entailment operation with the
  premises and the conclusion Lean named; the document is admitted when every one is found. A refusal there is
  the relay outcome `ConclusionNotDerived` (4.2). `invalidGrammar` stays `CheckerUnavailable`.
- **Rendered text.** `english.check` takes formulas with marks and a list of candidate texts and returns the
  index of the first candidate for which `checkRendering` is true, or none (`firstChecked`, 5.3). The renderer
  displays that candidate, with claim C3, or the source when there is none. Python's re-parse of its own
  renderings (`english.py:1775–1779`) is deleted.
- **The service.** `english.read`, `english.grammar` and `english.check` are modes of `ve_service`. The
  service keeps `grammar E L`, prepared, by `environment_id` and `lexicon_id`.
- **The comparator.** With `VE_ENGLISH_COMPARATOR=1` (set by the suite, the corpus harness and the nightly
  run, never by default) the relay also runs `_python_reading` and writes one record per call with the six
  identities, both outcomes and the classes of S2 4.5. Its result is never returned and its failure never
  raises. Without the switch Python's parser is not called by any admission entry point.
- **What Python keeps:** file I/O, spans for display, the vocabulary policy as the producer of the lexicon,
  rendering as a producer of candidates, the nearest-wording suggestion as editor help, and, until E3, the
  statement layers that construct `EnglishParser` themselves.

### 2.11 The harness and the tree correspondence

S3.5 builds S2 2.11's harness (comparison at the dispatched boundary, reverse corpus, mutation replay,
three-way differential) and runs it per profile. The correspondence of S2 2.11 is extended as follows.

| Profile | Lark | Lean | One to one because |
|---|---|---|---|
| `order@0` | the anonymous terminals `"["`, `"]"`, `"-"` and `INT_OP`, `NUMERAL` | the nodes `lbracket`, `rbracket`, `minus`, `int_op`, `numeral` | each token has one pair of flags, so each of these nodes has one derivation |
| `data@0` | one alternative `the R of term is P` per pair | `atom → the R of ⟨term⟩ is ⟨property_i⟩` over `property_i → P` | `P` is on one sort, so one property row derives it; computed on six pairs, verdicts and formulas (da17 to da19) |
| `alternatives@0` | the noun inline in three alternatives, each with an optional `excluding term` | five guard rows | Lark's `?` expands to the same five |
| | `alt_verb_phrase: relative \| atom \| …` and `alt_verb_atom: relative \| atom` | `verb-phrase.one` over `alt_verb_atom`; `verb-atom.subject` and `verb-atom.same` for the atom | on a text Python accepts, the atom is headed by the guard's reference (2.5) |

**Where Lean derives less than Lark.** Two classes of text have one Lark derivation and none in Lean: a guard
whose noun is not written exactly (al25, al26), and a guard's verb that is an atom not headed by the guard's
own reference written exactly (al24, al27, al28). The hand parser rejects both before the audit runs, so the
outcomes agree (`none` against `SyntaxError`). On these texts the harness compares Python's outcome, not the
count of the Lark forest. Everywhere else the comparison is S2's.

### 2.12 The readability writing gaps

They stay required fixtures (plan, P6). The three sentences of S2 2.12 keep verdict zero under the `order@0`,
`data@0` and combined fixture grammars (rg1 to rg3, computed). The three widening rules stay proposed and
outside every generated table. W12's message is the advice `negated-existential` (4.3, ad11). W02 is a
`norms@0` statement-layer message and stays with E3 (S2 n1).

### 2.13 Extensions

`Extends E O L E2 O2 L2` (5.4) holds when `E2` has the profile list of `E`, the same `alternatives` block and
risk flag; every sort of `E` is a sort of `E2`; every predicate of `E` is a predicate of `E2` with the same
argument sorts and the same `functional` and `total` flags; every constant is kept with its sort; every entry
of `L` is an entry of `L2`; and both lexicons are valid. Under it every row of `grammar E L` is a row of
`grammar E2 L2` after the property nonterminal of each value sort of `E` is renamed to that sort's nonterminal
in `E2`: the fixed rows are equal because the profile lists are, and each lexical row is built from one lexicon
entry, the signature and flags of its symbol and, for the guard family, the block. The rule map of
`grammar_extension` therefore has a renaming on nonterminals, which `RuleMap.Ok` allows, and the identity on
the fixed 51. Indices of property nonterminals carry no meaning (da20). Reselection (S2 q5), a changed
signature (S2 q7), a changed flag (ex3) and a changed profile list (ex4) are not extensions.

### 2.14 Identities, and what the next stage may rely on

- `Lexicon`, `Overlay` and the wire form `ve.english-lexicon@1` are unchanged, and so is the preimage of each
  of the six identities (base 2.12). `grammar_id` covers the profile names and the SHA-256 of each table
  source; S3 adds two sources and edits none, so the `grammar_id` of an environment without `order@0` and
  `alternatives@0` is unchanged (ev1).
- `actions_version` rises with S3 and again with E2: the lock lists the two new generated tables and every
  edited definition file.
- Every new field of `Env` and `PredDecl` has a default. A producer that sets none gets S2's grammar
  (`unstaged_fixed`, and the S2 fixtures, which pass unchanged).
- A rule's tag is built from its family and its symbol's name. Adding entries to a lexicon changes
  `lexicon_id` and adds rules; it changes no tag of an existing rule, so a `derivation` that survives an
  extension is the same list of tags.

### 2.15 What is trusted, proved and tested in this stage

| Layer | Items added |
|---|---|
| Trusted definitions | the two table sources and their generated literals; `ranksStaged`, `valueSorts`, `ty`; the lexical families and actions of 2.6 and 2.7; the profile part of `Env.decode`; subject first and V6 in `Lexicon.valid`; `obligations` and `admit`; the message table |
| Proved | the S2 statements over the wider grammar; `unstaged_fixed`, `ty_catalogue`, `ty_property`, `valid_subject_first`; `obligations_exact`, `admit_ok`, `admit_exact`, `admit_no_premise`, `first_checked`; `grammar_extension` for one profile list, or S2's if that proof is deferred |
| Checked per request | as S2 |
| Tested only | agreement with Python per profile (G3, GE2); the factoring; the advice table; the comparator's records; latency |
| Outside | the proof of each obligation (the entailment operation); the choice of the lexicon; `rights@0` wordings |

## 3. English: one reading each

### 3.1 The wordings the profiles add

Each row is a form an author writes, what it means exactly, and what it does not mean. `B`, `L` are integer
terms, `t`, `u` terms, `N` the action noun, `V` a verb phrase.

| Form | Means exactly | Does not mean |
|---|---|---|
| `B is less than L`, `B is at most L` | `B < L`, `B ≤ L` | |
| `B is more than L`, `B is at least L` | `L < B`, `L ≤ B` | `at least` never counts things: `at least one of the following holds` is a listing |
| `B is the same as L` | `B = L` | |
| `[B + L]`, `[B - L]`, `[3 * B]`, `-B`, `twice the budget` | the sum; `B + (−1 · L)`; `3 · B`; `−1 · B`; `2 · budget` | `[B * L]` with two non-numerals is not a product; it is refused |
| `the r of t is u` | `r(t, u)`, for an attribute `r` written by its identifier | that `u` is the only value: functionality is the declaration's |
| `the r of t is p` | there is a value that `r` relates `t` to and that is `p` | that `t` itself is `p` |
| `every N available to t V` | every action available to `t` satisfies `V` | anything about actions not available to `t` |
| `every other N available to t V` | every action available to `t`, other than the reference action, satisfies `V` | that the reference action satisfies `V` |
| `another N available to t V` | some action available to `t`, other than the reference action, satisfies `V` | that exactly one does |
| `… excluding u …` | the action left out is `u` instead of the reference action | |
| `a leads to h` | the declared outcome predicate | |
| `a might lead to h` | `risk__might_lead_to(a, h)` | permission: `may lead to` is refused |
| `a cannot lead to h` | not `risk__might_lead_to(a, h)` | `a does not lead to h`, which is refused under `risk@0` |
| `a might not lead to h` | not `leads_to(a, h)` | not `might lead to` |
| `h is c`, `h is c or worse` | `risk__class(h, c)`, `risk__or_worse(h, c)` | |
| `c is more severe than d` | `risk__more_severe(c, d)` | a comparison of harms: both are severity classes |
| `a has a less severe worst case than b` | `risk__less_worst(a, b)` | that `a` is safer in every case |
| `a might prevent h` | `prevents(a, h)` | |
| `x may access y`, `x must review y` | the atom of the regulated predicate | that a rule grants or imposes it: a norm does that, in a rule block |

`every N available to t cannot lead to h` is refused under `risk@0`, because it can be read as "no available
action might lead to it" or as "some available action cannot": the advice gives both rewrites (4.2).

### 3.2 The claim sentences

Base 3.1 stands. From the flip, a record of an admitted document carries C2 with the six identities, and C4
whenever a mark is present; when its obligations were proved it adds:

| Id | Sentence | Means exactly | Does not mean |
|---|---|---|---|
| C5 | `Each marked conclusion was checked against the earlier unmarked sentences of this text.` | for each obligation Lean named, the entailment operation reported a checked derivation | that the premises are true; that the English reader checked the derivation |

### 3.3 The outcomes

Base 3.2 and S2 3.2 stand. Added by E2.2: the two texts of 4.2 and the advice line of 4.3.

### 3.4 The theorems, in plain words

| Statement | Plain English | It does not say |
|---|---|---|
| the S2 statements | S2 3.4, now also for environments with the profiles | |
| `unstaged_fixed` | For a profile list that names the base profile and none of `order@0`, `data@0`, `alternatives@0`, the fixed table is the base table and the rank certificate is S2's. | anything about the lexical rules |
| `ty_catalogue`, `ty_property` | The first 37 nonterminals keep their S2 types, and each property nonterminal has the type of an adjective. | |
| `valid_subject_first` | In a valid lexicon every wording, negative and alias begins with `{0}` and has its holes in increasing order. | that `{1}` comes last |
| `obligations_exact` | A pair of an index and a list is an obligation exactly when the sentence at that index is marked and the list is the unmarked sentences before it, in order. | that the conclusion follows |
| `admit_ok` | If admission succeeds, the text has one reading per sentence, the obligations returned are those of that reading, and each has at least one premise. | that any obligation is provable |
| `admit_exact` | Admission succeeds with given formulas and marks exactly when the reader returns them and every marked sentence has an earlier unmarked one. | |
| `admit_no_premise` | If admission reports a conclusion without a premise, the reader accepted the text, that sentence is marked, and no earlier sentence is unmarked. | |
| `first_checked` | If the check of candidates returns an index, that candidate reads back as exactly the given formulas and marks, and no earlier candidate does. | that some candidate passes |
| `grammar_extension` | If an environment and lexicon extend another under one profile list (every symbol kept with its signature and flags, every selection kept, the block kept, both valid), there is a rule map from the smaller grammar into the larger that keeps every rule's sides, up to the renaming of property nonterminals, and its action. | anything when the profile list, a wording, a signature or a flag changed |

## 4. Diagnostics

### 4.1 Statuses

Base 4.1 stands. From the flip the public class is the one mapped from Lean's status and code (S2 4.2's map);
Python's own message is no longer shown.

### 4.2 Codes and texts added

| Code | Text | Python today |
|---|---|---|
| `ConclusionWithoutPremise` (`admit`: `noPremise i`) | `Sentence {i} is marked as a conclusion, and no earlier sentence is a premise.` | `SyntaxError`: `A conclusion needs an earlier premise.` |
| `ConclusionNotDerived` (relay) | `Sentence {i} is marked as a conclusion, and no checked derivation from the earlier premises was found.` | `SyntaxError`: `The marked conclusion has no checked derivation from earlier premises: …` |
| `BlockedWording`, id `risk-every-cannot` | `Choose whether no available action might lead to the harm: "it is not the case that there is an action such that both that action is available to the chooser and that action might lead to the harm"; or some available action cannot lead to it: "there is an action such that both that action is available to the chooser and that action cannot lead to the harm".` | the same advice with the chooser and the harm spelled (`english.py:77–81`) |

The texts live in one Lean table with the codes; `english.grammar` exports it, and the relay holds no text of
its own. Every text that differs from Python's is a `wording` row of `DELTA.md`.

### 4.3 Advice for a sentence without a reading

When the status is `none`, the response may carry `advice`: an id and its text. `advice profiles w` is
computed on the folded words of the sentence, a token that is not a word matching nothing: first
`negated-existential` when the first word is `no` and some word is `that` or `who`; then `plural-pronoun` when
the first word is one of `they them their her him his`; then, for each position from the left, the first row
of the table whose profile is named and one of whose patterns is a prefix of the words from that position.

| Id | Profile | Patterns | Text (Python's, `english.py:61–69`, `:82–85`, `:1252–1264`, `:1382`) |
|---|---|---|---|
| `risk-may` | `risk@0` | `may lead to` | `Use 'might lead to': 'may' is permission.` |
| `risk-does-not` | `risk@0` | `does not lead to` | `Choose 'cannot lead to' or 'might not lead to'.` |
| `risk-degree` | `risk@0` | `could lead to`; `risks`; `is likely to lead to`; `increases the risk of` | `Use 'might lead to' for possibility under the declared record.` |
| `risk-certainly` | `risk@0` | `certainly leads to` | `Use 'leads to' for certainty under the declared record.` |
| `risk-prevents` | `risk@0` | `prevents` | `Use 'might prevent' in a risk environment.` |
| `risk-safer` | `risk@0` | `is safer than` | `Use 'has a less severe worst case than'.` |
| `risk-condition` | `risk@0` | `unless`; `exactly when` | the text of `_RISK_CONDITION_IN_RULE` |
| `alternatives-causes` | `alternatives@0` | `causes` | `The proximate cause wording needs a declared proximate role; declare it or write 'leads to'.` |
| `alternatives-results` | `alternatives@0` | `results in`; `brings about` | `Use the declared Boolean wording 'leads to' for this outcome.` |
| `alternatives-degree` | `alternatives@0` | `could lead to`; `risks`; `increases the risk of`; `contributes to`; `provides uplift to` | `This outcome wording is not Boolean. State a supported leads-to cell or label the degree of risk as open.` |
| `alternatives-inaction` | `alternatives@0` | `through inaction allows` | `Through inaction allows has two readings. State whether inaction leads to the harm, or whether an avoidable harm is allowed.` |
| `plural-pronoun` | any | above | `Plural or possessive reference needs an explicit-name or scoped-referent confirmation.` |
| `negated-existential` | any | above | `A sentence that begins with "no" cannot use "that" or "who" after the noun. Write "it is not the case that there is ... such that ..." instead.` |

Python's two remaining `alternatives@0` messages (`allows a harm to a human being to happen`, and `allows X to
Y` for a person) need a pattern with a free word; they are rows of the table with that matcher, *obligations*
(ad15, ad16). Advice is advisory: it is computed after the verdict and is no input to it. Python's
nearest-wording suggestion stays editor help; it quotes whole tokens of Lean's lexer (S2 g1).

### 4.4 The response, and the comparator's record

`english.read` gains, with status `one`, `obligations`: a list of `{"conclusion": i, "premises": [j, …]}`; the
status `rejected` with code `ConclusionWithoutPremise` and its `sentence`; and `advice` with status `none`.
`english.check` returns `{"index": i}` or `{}` with the six identities. The comparator's record is S2 4.5's
shadow record with the roles exchanged: `lean` is the result returned, `python` the one compared.

## 5. Lean: definitions and the exact statements

### 5.1 Modules and conventions

Conventions as S2 5.1. Edited: `Lexicon.lean` (the new fields, subject first, V6), `Catalogue.lean` (`ntTy`
from 37, new `FixedAct` constructors), `Rules.lean`, `Actions.lean`, `Encode.lean` (`Env.decode`), `Read.lean`
(`obligations`, `admit`, `firstChecked`), `Extends.lean`. New: `Fixed/Order.lean` and `Fixed/Alternatives.lean`
(generated), `Advice.lean`, `ProfileExamples.lean` (the fixtures of section 8 as `#guard` checks). `Syntax.lean`
and `Token.lean` are not edited (D4).

### 5.2 The signature

```lean
namespace VE.EnglishGrammar
open VE.Grammar

structure AltBlock where
  action : String
  chooser : String
  harm : String
  available : String
  leadsTo : String
  deriving DecidableEq, Repr

-- PredDecl gains:  functional : Bool := false    total : Bool := false
-- Env gains:       alternatives : Option AltBlock := none    risk : Bool := false

def staged (profiles : List String) : Bool :=
  profiles.contains "order@0" || profiles.contains "data@0" || profiles.contains "alternatives@0"

def fixedTable (profiles : List String) : Array FixedRow      -- base, then order@0, then alternatives@0 (D1)
def fixedRules (profiles : List String) : Array (Rule Terminal)   -- row i of the table, with act := i
def ranksStaged : Array Nat                                    -- 2.4, 51 entries
def ranksFor (profiles : List String) : Array Nat := if staged profiles then ranksStaged else ranks
def valueSorts (E : Env) : List String                        -- 2.4
def lexRules (E : Env) (L : Lexicon) : Array (Rule Terminal)  -- rule i has act := (fixedTable E.profiles).size + i
def grammar (E : Env) (L : Lexicon) : Grammar Terminal :=
  { rules := fixedRules E.profiles ++ lexRules E L, start := 0,
    rank := ranksFor E.profiles ++ Array.replicate (valueSorts E).length 0 }
def ty (E : Env) (L : Lexicon) : Nat → Ty                     -- 2.4
def fixedActs (profiles : List String) : Array (Action sig)   -- the actions of `fixedTable profiles`
def lexActs (E : Env) (L : Lexicon) : Array (Action sig)
def acts (E : Env) (L : Lexicon) : Array (Action sig) := fixedActs E.profiles ++ lexActs E L

def holeOrder (w : String) : Bool := (holes w).1 == List.range (holes w).1.length
def subjectFirst (w : String) : Bool := w.startsWith "{0} " && holeOrder w
```

`read`, `translate`, `checkRendering`, `EnglishOneReading` and `meaning` are S2's definitions, word for word.

### 5.3 Admission and the check of candidates

```lean
def obligations (rs : List (EFormula × Bool)) : List (Nat × List Nat) :=
  (List.range rs.length).filterMap fun i =>
    match rs[i]? with
    | some (_, true) => some (i, (List.range i).filter fun j => (rs[j]?).map (·.2) == some false)
    | _ => none

inductive AdmitOutcome where
  | ok (rs : List (EFormula × Bool)) (obligations : List (Nat × List Nat))
  | noPremise (index : Nat)
  | refused (o : ReadOutcome)

def admit (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) : AdmitOutcome :=
  match read E O L b s with
  | .ok rs =>
    match (obligations rs).find? (fun o => o.2.isEmpty) with
    | some (i, _) => .noPremise i
    | none => .ok rs (obligations rs)
  | o => .refused o

def firstChecked (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (rs : List (EFormula × Bool))
    (candidates : List String) : Option Nat :=
  candidates.findIdx? (checkRendering E O L b rs)
```

### 5.4 Extensions

```lean
def envSub (E E2 : Env) : Prop :=
  E2.profiles = E.profiles ∧ E2.alternatives = E.alternatives ∧ E2.risk = E.risk ∧
  (∀ s ∈ E.sorts, ∃ s2 ∈ E2.sorts, s2.name = s.name) ∧
  (∀ p ∈ E.predicates, ∃ q ∈ E2.predicates, q.name = p.name ∧ q.arity = p.arity ∧ q.args = p.args ∧
    q.functional = p.functional ∧ q.total = p.total) ∧
  (∀ c ∈ E.constants, ∃ c2 ∈ E2.constants, c2.name = c.name ∧ c2.sort = c.sort)

def Extends (E : Env) (O : Overlay) (L : Lexicon) (E2 : Env) (O2 : Overlay) (L2 : Lexicon) : Prop :=
  envSub E E2 ∧ lexiconSub L L2 ∧ L.valid E O = true ∧ L2.valid E2 O2 = true
```

`lexiconSub` is S2's. S2's `envSub` fixed the profile list to the base profile; this one fixes it to be equal.

### 5.5 The statements

The S2 statements `read_ok`, `read_complete_english`, `read_stopped`, `english_reading_unique`,
`start_sentence`, `meaning_total`, `checked_rendering`, `checked_rendering_exact`, `translate_exact`,
`translate_one_sentence`, `grammar_rules`, `lexRules_terminatorFree` and `valid_iff_no_failure` keep their
statements word for word over the definitions of 5.2. Their proofs are generic in `grammar E L` and `acts E L`
except `start_sentence` and `grammar_rules`, which stay `rfl`, and `lexRules_terminatorFree`, whose rows are
filtered as in S2. Added:

```lean
theorem unstaged_fixed : ∀ (profiles : List String), staged profiles = false →
  profiles.contains baseProfile = true → fixedTable profiles = relationalFolRows ∧ ranksFor profiles = ranks

theorem ty_catalogue : ∀ (E : Env) (L : Lexicon) (n : Nat), n < 37 → ty E L n = ntTy n

theorem ty_property : ∀ (E : Env) (L : Lexicon) (i : Nat), i < (valueSorts E).length →
  ty E L ((ranksFor E.profiles).size + i) = .adjective

theorem valid_subject_first : ∀ (E : Env) (O : Overlay) (L : Lexicon), L.valid E O = true →
  (∀ x ∈ L.wordings, subjectFirst x.2 = true) ∧ (∀ x ∈ L.negatives, subjectFirst x.2 = true) ∧
  (∀ x ∈ L.aliases, subjectFirst x.2.1 = true)

theorem obligations_exact : ∀ (rs : List (EFormula × Bool)) (i : Nat) (js : List Nat),
  (i, js) ∈ obligations rs ↔
    (∃ A, rs[i]? = some (A, true)) ∧ js = (List.range i).filter fun j => (rs[j]?).map (·.2) == some false

theorem admit_ok : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) (rs : List (EFormula × Bool))
    (obs : List (Nat × List Nat)),
  admit E O L b s = .ok rs obs →
  EnglishOneReading E O L s rs ∧ obs = obligations rs ∧ ∀ o ∈ obs, o.2 ≠ []

theorem admit_exact : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) (rs : List (EFormula × Bool)),
  (∃ obs, admit E O L b s = .ok rs obs) ↔ (read E O L b s = .ok rs ∧ ∀ o ∈ obligations rs, o.2 ≠ [])

theorem admit_no_premise : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) (i : Nat),
  admit E O L b s = .noPremise i →
  ∃ rs A, read E O L b s = .ok rs ∧ rs[i]? = some (A, true) ∧ ∀ j B, j < i → rs[j]? ≠ some (B, false)

theorem first_checked : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (rs : List (EFormula × Bool))
    (candidates : List String) (i : Nat),
  firstChecked E O L b rs candidates = some i →
  ∃ s, candidates[i]? = some s ∧ read E O L b s = .ok rs ∧
    ∀ j t, j < i → candidates[j]? = some t → read E O L b t ≠ .ok rs

theorem grammar_extension : ∀ (E : Env) (O : Overlay) (L : Lexicon) (E2 : Env) (O2 : Overlay) (L2 : Lexicon),
  Extends E O L E2 O2 L2 →
  ∃ e : RuleMap, e.Ok (grammar E L) (grammar E2 L2) (acts E L) (acts E2 L2)
```

In the stub `valid_subject_first` was proved for S2's `valid` conjoined with subject first, `grammar_rules` and
the rank equation are `rfl`, and the others elaborated as `Prop`s (section 12).

### 5.6 By construction, and by test

- `unstaged_fixed`, `ty_catalogue` and `ty_property` unfold the definitions of 5.2.
- `obligations_exact` is membership in a `filterMap` over a range; the three `admit` statements split on
  `read` and on `find?`, with `read_ok`; `first_checked` is `List.findIdx?` with `checked_rendering_exact`.
- The fixed tables against their JSON sources, the fixtures of section 8, the advice table and the message
  table against `DELTA.md` are tests.

## 6. Files, generated artefacts and gates

| Artefact | Rule |
|---|---|
| `ve/english_grammar/order@0.json`, `alternatives@0.json`; `LOCK.json` | 2.5; S2 2.9's row format, with the new action names |
| `lean/VE/EnglishGrammar/Fixed/Order.lean`, `Fixed/Alternatives.lean` | generated; `--check` in the commit hook |
| the modules of 5.1 | frozen-inventory lines, `Audit.lean` lines for the statements of 5.5, the generated lists regenerated |
| `ve_service` modes `english.read`, `english.grammar`, `english.check`; `ve_english_route` deleted | E2.0 |
| `ve/english.py`, `ve/backends/english_lean.py`, `ve/backends/dispatch.py`, `ve/assurance-manifest.json` | E2.3: the relay, `english.admission` out of `SHADOW_ONLY`, `authority: lean` |
| `conformance/english_lean_{g2,reverse,mutate}.py` | S3.5 |
| `docs/spec/english-lean-s3-report.md`; `docs/lean-first/e2/DELTA.md`, `LEDGER.md` | G3; GE2 |

Gates: the statement review of this specification before S3.4's proofs; G3 and GE2 as the plan states them.

## 7. What this stage consumes and returns

| From | Delivery | Used in |
|---|---|---|
| S0 | the rejection-site classes of the profile constructs; the conversion of the integer marks; the V1 finding on `risk__more_severe` | 2.2, 2.8, 2.9 |
| S2 | the reader, its statements and fixtures; `Env`, `Lexicon`, `Lexicon.valid`; the adapter and the shadow record | everywhere |
| LEAN-FIRST | the gate of 5.1; DRI answers 3 and 5 | 2.9, 4.2, GE2 |
| returns | subject first, which retires `relativeForm` for valid lexicons; `admit`; the answer to S2's question whether the conclusion check moves (it is split, D10); the per-profile correspondence; for the senses layer, 2.14 | S2 Q2, Q11; `design/senses` |

## 8. Acceptance fixtures

Every fixture is an obligation on the implementation. All values below were computed (section 12) unless
marked *obligation*. `one`, `zero`, `many` are derivation counts at cap 2; an outcome is the reader's before
the typed check. Formulas use S2's notation, `var 0` innermost.

### 8.1 `order@0`

`FO`: `F` and `LF` (base 8.5) with `order@0`, `costs` over a service and an integer worded `{0} costs {1}`,
`exceeds` over two integers worded `{0} exceeds {1}`, and the integer constants `budget` and `limit`.
`costs(x)` abbreviates `pred costs [const legacy, x]`.

| Id | Source | Expected |
|---|---|---|
| or1 | `Legacy costs 5.` | one; `costs(num 5)` |
| or2 | `Legacy costs -5.` | `costs(num -5)` |
| or3 | `Legacy costs -0.` | `costs(num 0)` |
| or4 | `Legacy costs [budget + 1].` | `costs(add (const budget) (num 1))` |
| or5 | `Legacy costs [budget - limit].` | `costs(add (const budget) (scale -1 (const limit)))` |
| or6 | `Legacy costs [3 * budget].`; `… [-3 * budget].` | `costs(scale 3 (const budget))`; `scale -3` |
| or7 | `Legacy costs [budget * limit].` | one; `rejected coefficientNotNumeral` |
| or8 | `Legacy costs [[budget + 1] * limit].` | `rejected coefficientNotNumeral` |
| or9 | `Legacy costs twice the budget.` | `costs(scale 2 (const budget))` |
| or10 | `Legacy costs -budget.`; `… --budget.` | `costs(scale -1 (const budget))`; `scale -1 (scale -1 …)` |
| or11 | `Legacy costs -[budget + 1].` | `costs(scale -1 (add (const budget) (num 1)))` |
| or12 | `Legacy costs [budget - -5].` | `costs(add (const budget) (scale -1 (num -5)))` |
| or13 | `Legacy costs [[budget + 1] + [2 * limit]].` | `costs(add (add (const budget) (num 1)) (scale 2 (const limit)))` |
| or14 | `Legacy costs [[budget + 1] + [limit * 2]].` | `rejected coefficientNotNumeral` |
| or15 | `Budget is at most 5.`; `Budget IS AT MOST 5.` | `le (const budget) (num 5)`, both |
| or16 | `Budget is less than limit.`; `Budget is more than limit.` | `lt (const budget) (const limit)`; `lt (const limit) (const budget)` |
| or17 | `Budget is at least [limit + 1].` | `le (add (const limit) (num 1)) (const budget)` |
| or18 | `Budget is the same as limit.`; `Budget exceeds limit.` | `eq (const budget) (const limit)`; `pred exceeds [const budget, const limit]` |
| or19 | `Every service that costs 5 is reviewed.`; `Every service costs twice the budget.` | `all service (implies (pred costs [var 0, num 5]) (pred reviewed [var 0]))`; `all service (pred costs [var 0, scale 2 (const budget)])` |
| or20 | `Legacy costs --5.` | zero |
| or21 | `Legacy costs -twice the budget.` | zero |
| or22 | `Legacy costs - budget.` | zero |
| or23 | `Legacy costs [budget+1].`; `… [budget +1].` | zero; zero |
| or24 | `Legacy costs [ budget + 1].`; `… [budget + 1 ].` | zero; zero |
| or25 | `Legacy costs 007.` | lexical `badNumeral 13` |
| or26 | `Legacy costs legacy.`; `Legacy is the same as budget.`; `Budget is the same as legacy.`; `Legacy costs twice the 5.` | zero, each |
| or27 | `Legacy is deployed. It costs 5.` | `ok`: `pred deployed [const legacy]`, `costs(num 5)` |
| or28 | `It costs 5.`; `That service costs 5.` | `rejected pronounUnresolved`; `rejected unboundReference` |
| or29 | `Legacy costs ` 63 signs `budget.` | `costs` of 63 nested `scale -1` |
| or30 | the same with 64 signs | one; `rejected nestingLimit` |
| or31 | `Legacy costs [[budget * limit] + ` 64 signs `budget].` | `rejected nestingLimit`, not `coefficientNotNumeral` |
| or32 | `That service costs ` 64 signs `budget.` | `rejected unboundReference`, not `nestingLimit` |
| or33 | `Budget is at most ` 64 signs `budget.`; `[budget * limit] is at most ` 64 signs `budget.` | `rejected nestingLimit`, both |
| or34 | a numeral of 40 nines; of 41 | `ok`; `rejected numeralBound` |
| or35 | `-` and 39 nines; `-` and 40 | `ok`; `rejected numeralBound` |
| or36 | S2's b1 and b3 under `FO` | one, each |

### 8.2 `data@0`

`FD`: `F` with `data@0`, `senior` on persons worded `{0} is senior`, and the attributes `owner_of` (service to
person) and `backup_of` (service to service), both on their quoted fallback; lexicon `LD`. Value sorts:
`person`, `service`.

| Id | Source | Expected |
|---|---|---|
| da1 | `The owner_of of legacy is alice.` | `pred owner_of [const legacy, const alice]` |
| da2 | `Legacy has the recorded relation "owner_of" to alice.` | the same formula |
| da3 | `The owner_of of legacy is senior.` | `ex person (and (pred owner_of [const legacy, var 0]) (pred senior [var 0]))` |
| da4 | `The owner_of of legacy is deployed.` | zero: `deployed` is a property of services |
| da5 | `The backup_of of legacy is deployed.` | `ex service (and (pred backup_of [const legacy, var 0]) (pred deployed [var 0]))` |
| da6 | `For every service, the owner_of of that service is senior.` | `all service (ex person (and (pred owner_of [var 1, var 0]) (pred senior [var 0])))` |
| da7 | `The owns of alice is legacy.` | zero: `owns` is no attribute |
| da8 | `The Owner_of of legacy is alice.` | zero |
| da9 | `If legacy is deployed, then The owner_of of legacy is alice.` | zero |
| da10 | `Every service that the owner_of of that service is alice is reviewed.` | zero: an attribute is no relative |
| da11 | `If legacy is deployed, then the owner_of of legacy is alice.` | `implies (pred deployed [const legacy]) (pred owner_of [const legacy, const alice])` |
| da12 | `Legacy is deployed. The backup_of of it is legacy.` | `ok`; second `pred backup_of [const legacy, const legacy]` |
| da13 | `Legacy is deployed. The backup_of of legacy is it.` | the same |
| da14 | `Legacy is deployed. The backup_of of it is deployed.` | `ok`; second `ex service (and (pred backup_of [const legacy, var 0]) (pred deployed [var 0]))` |
| da15 | `Legacy is deployed. If legacy is deployed, then the backup_of of it is legacy.` | `stopped 1 (rejected pronounUnresolved)` |
| da16 | `The backup_of of it is legacy.` | `stopped 0 (rejected pronounUnresolved)` |
| da17 | the six sentences `The r of legacy is p.` for `r` in `owner_of`, `backup_of` and `p` in `senior`, `deployed`, `reviewed` | one, zero, zero, zero, one, one |
| da18 | the same six under `FP`, Python's shape: one rule `atom → the r of ⟨term⟩ is p` per pair | the same six verdicts |
| da19 | the same six, outcomes under `FD` and `FP` | equal, formula for formula |
| da20 | the same six with the property nonterminals renumbered (a third value sort first) | the outcomes of da19 |

### 8.3 `alternatives@0`

`FA`: sorts `action`, `agent`, `harm`; `available` over action and agent worded `{0} is available to {1}`,
`leads_to` over action and harm worded `{0} leads to {1}`, `safe` on actions, the four generated predicates
with their forms and the three aliases of 2.3; constants `wait` (action), `robot` (agent), `injury` (harm);
letters `A`, `G`, `H`. `A(o) = pred available [var 0, o]`, `D(i) = not (eq (var 0) (var i))`, `S = pred safe
[var 0]`, `Ld = pred leads_to [var 0, const injury]`, `r = const robot`.

| Id | Source | Expected |
|---|---|---|
| al1 | `Every action available to robot is safe.` | one; `all action (implies A(r) S)` |
| al2 | `For every action, every other action available to robot is safe.` | `all action (all action (implies (and A(r) D(1)) S))` |
| al3 | `For every action, another action available to robot is safe.` | `all action (ex action (and (and A(r) D(1)) S))` |
| al4 | `Every other action available to robot is safe.`; `Another action available to robot is safe.` | one; `rejected unboundReference`, both |
| al5 | `For every action named A1, for every action named A2, every other action available to robot is safe.` | three binders, `D(1)` |
| al6 | the same with `excluding A1` before `is safe` | three binders, `D(2)` |
| al7 | al6 with `another` | `all action (all action (ex action (and (and A(r) D(2)) S)))` |
| al8 | `For every action, every other action available to robot excluding robot is safe.` | `rejected sortMismatch` |
| al9 | `For every agent, for every action, every other action available to robot excluding that agent is safe.` | `rejected sortMismatch` |
| al10 | `Every action available to robot excluding robot is safe.` | zero: `every` takes no `excluding` |
| al11 | `For every action, every other action available to robot that other action leads to injury.` | `all action (all action (implies (and A(r) D(1)) Ld))` |
| al12 | `For every action, another action available to robot either is safe or leads to injury.` | `all action (ex action (and (and A(r) D(1)) (or S Ld)))` |
| al13 | al12 with `, or both` | the same formula |
| al14 | `For every action, another action available to robot both is safe and leads to injury.` | `… (and S Ld)` |
| al15 | `For every action, every other action available to robot either that other action is safe or leads to injury.` | `all action (all action (implies (and A(r) D(1)) (or S Ld)))` |
| al16 | `For every action, another action available to robot that other action is the same as wait.` | `… (eq (var 0) (const wait))` |
| al17 | `For every action, every other action available to robot is the same as wait.` | zero: an equality is no relative |
| al18 | `Every action available to robot that action is safe.` | `all action (implies A(r) S)` |
| al19 | `Every action available to robot that other action is safe.` | one; `rejected unboundReference` |
| al20 | `For every action, every other action available to robot that action is safe.` | `rejected unboundReference` |
| al21 | `For every action, that other action is safe.` | one; `rejected unboundReference` |
| al22 | `Every action available to it is safe.`; `… to that agent is safe.` | `rejected pronounUnresolved`; `rejected unboundReference` |
| al23 | `For every agent, every action available to that agent is safe.` | `all agent (all action (implies A(var 1) S))` |
| al24 | `For every action, every other action available to robot That other action is safe.` | zero |
| al25 | `Every Action available to robot is safe.` | zero |
| al26 | `Every action Available to robot is safe.` | zero |
| al27 | `Every action available to robot wait is safe.` | zero |
| al28 | `Every action available to robot this holds in all cases.` | zero |
| al29 | `For every action, every other action available to robot is the same as that other action.` | `stopped 0 none` |
| al30 | `For every action, another action available to robot that other action is the same as That Other Action.` | `… (eq (var 0) (var 0))` |
| al31 | `Injury is preventable by robot.`; `Injury is avoidable by robot.` | `pred avoidable [const injury, const robot]`, both |
| al32 | `Wait lets injury happen.`; `Wait does not lead to injury.`; `Wait prevents injury.` | `pred allows [const wait, const injury]`; `not (pred leads_to …)`; `pred prevents …` |
| al33 | `Wait is safe. Therefore every action available to robot is safe.` | `ok`, marks false and true |
| al34 | `For every action, every action available to robot is safe.` | `all action (all action (implies A(r) S))` |
| al35 | `Wait cannot lead to injury.` | zero: no risk block |

### 8.4 `risk@0`

`FR`: `FA` with the risk block: the sort `severity`, the classes `minor` and `catastrophic`, the five risk
predicates, the forms of 2.3 and `risk__more_severe` (D9). `M(a, h) = pred risk__might_lead_to [a, h]`.

| Id | Source | Expected |
|---|---|---|
| ri1 | `Wait might lead to injury.` | `M(const wait, const injury)` |
| ri2 | `Wait cannot lead to injury.` | `not M(…)` |
| ri3 | `Wait might not lead to injury.`; `Wait leads to injury.` | `not (pred leads_to …)`; `pred leads_to …` |
| ri4 | `Injury is catastrophic.` | `pred risk__class [const injury, const catastrophic]` |
| ri5 | `Injury is minor or worse.` | `pred risk__or_worse [const injury, const minor]` |
| ri6 | `Wait has a less severe worst case than wait.` | `pred risk__less_worst [const wait, const wait]` |
| ri7 | `Catastrophic is more severe than minor.` | one; `pred risk__more_severe [const catastrophic, const minor]` |
| ri8 | `Wait might prevent injury.` | `pred prevents [const wait, const injury]` |
| ri9 | `For every harm that is catastrophic, wait cannot lead to that harm.` | `all harm (implies (pred risk__class [var 0, const catastrophic]) (not M(const wait, var 0)))` |
| ri10 | `Every action available to robot cannot lead to injury.` | one; `rejected (blockedWording "risk-every-cannot")` |
| ri11 | `Every action available to robot either is safe or cannot lead to injury.`; `… both cannot lead to injury and is safe.` | the same rejection, both |
| ri12 | `For every action, every other action available to robot cannot lead to injury.` | `all action (all action (implies (and A(r) D(1)) (not M(var 0, const injury))))` |
| ri13 | ri12 with `another` | `all action (ex action (and (and A(r) D(1)) (not M(var 0, const injury))))` |
| ri14 | `Every action available to robot might not lead to injury.` | `all action (implies A(r) (not Ld))` |
| ri15 | `Every action available to robot might lead to injury.` | `all action (implies A(r) M(var 0, const injury))` |
| ri16 | ri10 with the guards built without the risk flag | `all action (implies A(r) (not M(var 0, const injury)))` |
| ri17 | `Wait may lead to injury.`; `Wait does not lead to injury.`; `Wait could lead to injury.`; `Wait risks injury.`; `Wait is likely to lead to injury.`; `Wait increases the risk of injury.`; `Wait certainly leads to injury.`; `Wait prevents injury.`; `Wait is safer than wait.`; `Wait leads to injury unless wait is safe.`; `Wait cannot lead to injury exactly when wait is safe.`; `Wait causes injury.`; `Wait results in injury.` | zero, each |

### 8.5 Modal atoms

`FM`: `F` with `norms@0`, `access` and `review` over person and service, the forms `{0} may access {1}` and
`{0} must review {1}`.

| Id | Source | Expected |
|---|---|---|
| mo1 | `Alice may access legacy.`; `Alice must review legacy.` | `pred access [const alice, const legacy]`; `pred review […]` |
| mo2 | `Every person who may access legacy owns legacy.` | `all person (implies (pred access [var 0, const legacy]) (pred owns [var 0, const legacy]))` |
| mo3 | `Alice may not access legacy.`; `Alice access legacy.` | zero; zero |

### 8.6 The lexicon

Computed with S2's `Lexicon.failures`; lx12 and lx13 with `subjectFirst` of 5.2.

| Id | Case | Expected |
|---|---|---|
| lx1 | `LD` for `FD`'s environment | valid |
| lx2 | `LA` for `FA`'s | valid; `failures = []` |
| lx3 | `LR` for `FR`'s | valid |
| lx4 | `LR` without `risk__more_severe`, the environment without its form (Python today) | `[("V1", "predicate", "risk__more_severe")]` |
| lx5 | the same lexicon, the environment with the form | the same failure |
| lx6 | `LR`, the environment without the form | `[("V2", "predicate", "risk__more_severe")]` |
| lx7 | `LR` with the negative `{0} is not {1}` for `risk__class` | `[("V2", "negative", "risk__class")]` |
| lx8 | `LR` with the alias `{0} does not lead to {1}` | `[("V2", "alias", "leads_to")]` |
| lx9 | `LM` for `FM`'s | valid |
| lx10 | `LM`, the environment without the modal forms | `[("V2", "predicate", "access"), ("V2", "predicate", "review")]` |
| lx11 | `LM` with the declared negative `{0} may not access {1}` | `[("V5", "negative", "access")]` |
| lx12 | subject first on: the 13 unary and 25 binary idioms; every form of 2.3; the mechanical wordings of one, two and three arguments and the two fallbacks; every entry of `LF`, `LD`, `LA`, `LR`, `LM`; `{0} {1} are related`; `{0} gives {1} away` | true, each |
| lx13 | subject first on `the owner of {0} is {1}`, `{1} follows {0}`, `{1} {0} are related`; S2's lexicons of e51, e52, e53 | false, each; the three lexicons are valid under S2's conditions and not valid with subject first |
| lx14 | *obligation*: over the 39 corpus environments of S0, every wording, negative and alias Python selects | subject first; a counterexample is a finding for the DRI |
| lx15 to lx19 | *obligations* (E2.1): for each code of V6, a declared wording that the code refuses and one it passes: `{0} never fails` and `{0} is deployed`; a wording with another predicate's head and one without; `{0} is undeployed` beside `deployed`; `{0} is owned by {1}` and `{0} owns {1}` (auxiliary); `{0} reports to {1}` passes by the rescue and `{0} belongs to {1}` does not | refused, then accepted; Python's selection on the same environments agrees |

### 8.7 Ambiguity, the combined grammar, the readability sentences

| Id | Case | Expected |
|---|---|---|
| am1 | `FR` with a severity class spelled `safe`: `Wait is safe.` | many; under `FR`, one |
| am2 | `FD` with a person spelled `senior`: `The owner_of of legacy is senior.` | many; `The owner_of of legacy is alice.` one |
| cb1 | `FD`'s vocabulary with the rows of every profile, and four rows that begin with `⟨int_term⟩` | `wf`, terminator-free and typed; 196 rules |
| cb2 | under cb1: `Legacy costs [budget + 1].`; `The owner_of of legacy is senior.`; `Every service that is deployed is reviewed.`; `Every service available to alice costs 5.` | one, each |
| rg1 | `Every service is deployed or reviewed, or both.` under `FO`, `FD`, cb1 | zero, each |
| rg2 | `For every person, if that person is deployed and that person is reviewed, then that person is reviewed.` under `FO`, cb1 | zero |
| rg3 | `No service that is deployed is not reviewed.` under `FO`, `FD`, cb1 | zero |

### 8.8 Advice

| Id | Profiles; sentence | Expected |
|---|---|---|
| ad1 to ad7 | risk; the sentences of ri17 with `may lead to`, `does not lead to`, `could lead to`, `certainly leads to`, `prevents`, `is safer than`, `unless` | `risk-may`, `risk-does-not`, `risk-degree`, `risk-certainly`, `risk-prevents`, `risk-safer`, `risk-condition` |
| ad8 | risk; `Wait causes injury.` | `alternatives-causes` |
| ad9 | alternatives without risk; `Wait could lead to injury.` | `alternatives-degree` |
| ad10 | base; `Wait may lead to injury.` | none |
| ad11 | base; `No service that is deployed is not reviewed.` | `negated-existential` |
| ad12 | base; `No service is deployed.` | none |
| ad13 | base; `They are deployed.` | `plural-pronoun` |
| ad14 | base; `Every sevice is reviewed.` | none |
| ad15, ad16 | *obligations*: the two `allows` messages of 4.3 | their ids |

### 8.9 Admission

Under `F`, `LF`, with S2's `read`.

| Id | Source | Expected |
|---|---|---|
| cn1 | `Legacy is deployed. Therefore legacy is deployed.` | `ok`, obligations `[(1, [0])]` |
| cn2 | `Legacy is deployed.` | `ok`, no obligation |
| cn3 | `Therefore legacy is deployed.` | `noPremise 0` |
| cn4 | `Therefore legacy is deployed. So legacy is deployed.` | `noPremise 0` |
| cn5 | `Legacy is deployed. So legacy is reviewed. Legacy is reviewed. Hence legacy is deployed.` | `ok`, obligations `[(1, [0]), (3, [0, 2])]` |
| cn6 | `Every sevice is reviewed.` | `refused` |
| cn7 | `obligations` on marks `[false, true]`; `[true]`; `[false, true, false, true]`; `[true, true]`; `[false, false]` | `[(1, [0])]`; `[(0, [])]`; `[(1, [0]), (3, [0, 2])]`; `[(0, []), (1, [])]`; `[]` |
| cn8 | candidates `Legacy is reviewed.`, `Legacy is deployed`, `Legacy is deployed.`, `legacy is deployed.` for `pred deployed [const legacy]`, unmarked | `firstChecked = some 2` |
| cn9 | the one candidate `Legacy is reviewed.` for the same formula | none |

### 8.10 Sizes and steps

| Id | Measure | Value |
|---|---|---|
| sz1 | rows of the `order@0` and `alternatives@0` tables; guard-family rows of one block | 25; 8; 8 |
| sz2 | rules and `\|G\|` of the fixture grammars `FO`, `FD`, `FP`, `FA`, `FR`, cb1 | 159 and 575; 147 and 587; 145 and 590; 159 and 646; 185 and 746; 196 and 729 |
| sz3 | attribute rows for 128 attributes into one sort with 128 properties: Python's shape; factored | 16,512; 384 |
| sz4 | steps, cap 2: S2's b3 under `FO`; or13; or17 | 8,801; 8,797; 5,262 |
| sz5 | steps: da6; al6; al13; ri12 | 6,606; 14,503; 12,571; 10,697 |
| sz6 | steps: S2's b3 under cb1 | 11,149 |
| sz7 | `wf` of an S2 grammar under `ranks` and under `ranksStaged`; of `FO`'s rules under `ranks` extended with zeros | true, true; false |
| sz8 | *obligation*: `ranksFor` of `["relational-fol@0"]`, of `["closure@0", "relational-fol@0"]`, of `["norms@0", "relational-fol@0"]` | `ranks`, each |
| sz9 | *obligation*: `ranksFor` of a list that names `order@0`; `data@0`; `alternatives@0` | `ranksStaged`, each |

The largest figure, 14,503, is 0.69% of `workBudget`. S2's b3 costs 7,736 steps without the profile rows.
The budgets of GE2 are obligations of its report.

### 8.11 Extensions

*Obligations*; they need `lexRules` of 2.6.

| Id | Case | Expected |
|---|---|---|
| ex1 | `FO`'s environment and the same with one more integer constant and one more predicate | `Extends` holds; every row of the smaller grammar is a row of the larger; or1 to or36 keep their outcomes |
| ex2 | `FD`'s environment and the same with a new attribute whose value sort comes first in `valueSorts` | `Extends` holds; the map renames the property nonterminals; da1 to da16 keep their outcomes (da20 is the computed half) |
| ex3 | `FD`'s environment with `owner_of` no longer total | `Extends` is false: `envSub` fails on the flag |
| ex4 | `F` and `FO`'s environment | `Extends` is false: the profile lists differ |

### 8.12 Evidence and tooling

*Obligations.*

| Id | Case | Expected |
|---|---|---|
| ev1 | `grammar_id` of `F` before and after S3 | equal |
| ev2 | `english.read` as a service mode on S2's 89 route fixtures | the answers of `ve_english_route` |
| ev3 | two requests with one `environment_id` and `lexicon_id` | the second does not instantiate the grammar |
| ev4 | `english.check` on cn8 and cn9 | `{"index": 2}`; `{}` |
| ev5 | the Python outcome of every computed fixture of 8.1 to 8.5 and 8.7, at the dispatched boundary | the mapped class and the same formulas; a difference is a finding |
| ev6 | the comparator off: an admission call | `_python_reading` is not called |
| ev7 | the comparator on, with a reader that disagrees | one record; the result returned is Lean's |

### 8.13 The iff claims, both directions

| Claim | Direction | Fixture |
|---|---|---|
| an integer term is refused for depth exactly when it is deeper than 64 | 64 → read | or29 |
| | 65 → `nestingLimit` | or30 |
| a numeral is refused exactly when it is longer than 40 characters with its sign | 40, and 39 with a sign → read | or34, or35 |
| | 41, and 40 with a sign → `numeralBound` | or34, or35 |
| `[a * b]` is read exactly when `a` is a numeral | numeral → read | or6 |
| | otherwise → `coefficientNotNumeral` | or7, or8 |
| the property form derives exactly when the property is on the attribute's value sort | on it → one | da3, da5 |
| | not on it → zero | da4 |
| the factored rows derive a pair exactly when Python's rows do | both one | da17, da18 (first, fifth, sixth) |
| | both zero | da17, da18 (the other three) |
| `it` is read in an attribute exactly when the attribute starts the sentence's formula and the state resolves it | starts → read | da12, da13, da14 |
| | not at the start; no referent → rejected | da15; da16 |
| `every other` and `another` are read exactly when an action is in scope | in scope → read | al2, al3 |
| | none → `unboundReference` | al4 |
| a verb head is read exactly when it is the guard's own reference | own → read | al11, al18 |
| | the other reference → `unboundReference` | al19, al20 |
| `excluding` is read exactly when its term is an action in scope | action → read | al6, al7 |
| | a constant; another sort → `sortMismatch` | al8; al9 |
| the `every … cannot` block fires exactly under `every`, the risk flag, and a `cannot` part | all three → blocked | ri10, ri11 |
| | `other`, `another`; no flag; `might not` → read | ri12, ri13; ri16; ri14 |
| a wording passes subject first exactly when it begins with `{0} ` and its holes are in order | passes | lx12 |
| | fails | lx13 |
| `(i, js)` is an obligation exactly when sentence `i` is marked and `js` is the unmarked sentences before it | marked → listed | cn1, cn5, cn7 |
| | unmarked → not listed | cn2, cn7 (last) |
| `admit` is `ok` exactly when `read` is `ok` and every obligation has a premise | both → `ok` | cn1, cn2, cn5 |
| | a mark without a premise → `noPremise`; `read` not `ok` → `refused` | cn3, cn4; cn6 |
| `firstChecked` is an index exactly when some candidate reads back as the formulas | some → the first | cn8 |
| | none → none | cn9 |
| advice of a risk row is given exactly when `risk@0` is named and a pattern occurs | both → the id | ad1 |
| | no profile; no pattern → none | ad10; ad14 |
| a guard derives exactly when its words and its noun are written exactly | exact → one | al1 |
| | a capital in the noun or in a word → zero | al25, al26 |
| the rank certificate is S2's exactly when no staged profile is named | none named → `ranks` | sz8 (*obligation*); the S2 fixtures pass unchanged |
| | one named → `ranksStaged`; `ranks` would not fit | sz9 (*obligation*); sz7 |
| `Extends` holds exactly when the profile list, the block, the symbols with their signatures and flags, and the selections are kept and both lexicons are valid | kept → a rule map | ex1, ex2 (*obligations*) |
| | a flag changed; the list changed → not | ex3; ex4 (*obligations*) |
| the comparator runs exactly when its switch is set | set → one record, Lean's result returned | ev7 (*obligation*) |
| | not set → Python's parser is not called | ev6 (*obligation*) |

## 9. Limits, and what is not claimed

Base section 9 and S2 section 9 stand. In addition: every Python outcome named here was read from the source
and not run; nothing is proved about the profile tables against Python's grammar (G3 measures it); Lean derives
less than Lark on the two classes of 2.11; `rights@0` wordings are outside the reader; the advice table is
wider than Python's and proves nothing; the obligations of marked conclusions are computed by Lean and proved
elsewhere, and no English statement speaks of that proof; V6's rescue is not yet a definition; the lexicon is
still selected by Python; `grammar_extension` for profiles is a statement until proved; the latency budgets
are unmeasured; `EnglishParser` remains in use by the statement layers after E2.

## 10. Statement review checklist (Astra + Fable, before S3.4)

1. The `order@0` rows (2.5) are Lark's integer grammar rule for rule over tokens, with the spacing of 2.2;
   `int_neg` has no numeral and no `twice`.
2. The depth, bound and coefficient rules of 2.7 are `int_syntax` and `int_term` exactly, in Python's order,
   including the precedence of the depth check and of an unbound object term (or31 to or33).
3. The attribute rows and actions (2.6, 2.7) are the hand parser's branch `english.py:985–1019`, including
   `it` in either slot (da12 to da16) and the exact name.
4. The factoring is one to one and the value-sort nonterminals are the right granularity (da17 to da20, sz3).
5. The guard rows, the two head rows and the six steps of the guard action are `alternatives_guard` exactly:
   the order of the checks, the index of the excluded action, the lifting of the owner, the shadowing in an
   `every` guard.
6. The two classes where Lean derives less than Lark (2.11) are exactly the texts the hand parser rejects
   there, and no text Python accepts is lost.
7. Subject first (2.9) loses no lexicon Python's producer makes, and is sufficient for 2.6's cuts and heads.
8. The forms of 2.3 are Python's, and `{0} is more severe than {1}` collides with no other form.
9. `obligations`, `admit` and their four statements say what 3.4 says; the split with the entailment
   operation (D10) is the right boundary.
10. `Extends` (5.4) is sufficient for `grammar_extension` with the renaming, or the statement is deferred.
11. The advice table (4.3) ports Python's texts and never reaches a verdict.
12. The computed fixtures of section 8 are the right expectations, or31 to or33, da12 to da16, al18 to al30
    and ri10 to ri16 in particular; the Python class named for each rejected fixture is the class of the check
    that fires first.
13. Every name passes the audit's rules; no public message, code or identity changes before the flip.

## 11. Open points

| # | Point | Recommendation |
|---|---|---|
| Q1 | the two classes with fewer derivations than Lark (2.11) | accept: outcomes agree; the alternative needs the written text of a reference in `TermVal` |
| Q2 | subject first in S3 instead of E2 | adopt now; confirm on the corpus (lx14) |
| Q3 | V6's rescue: port the two pattern tables, or list the rescued wordings per environment | port (E2.1), with a bounded review |
| Q4 | whether Lean should compute the lexicon | not in this stage (plan, question 4) |
| Q5 | `rights@0` forms | E3, with the rights layer (plan, question 6) |
| Q6 | the conclusion check inside Lean | split as D10 now; revisit with the entailment batch |
| Q7 | V4 and names that are both a property and a spelling (am1, am2) | leave to the per-sentence verdict; both sides reject |
| Q8 | the text of `risk-every-cannot` without the chooser and the harm spelled | accept as a `wording` change, or give `blockedWording` two parameters |
| Q9 | `-0` | read as 0, as Python's `numeral_value` does (or3) |
| Q10 | the widenings of S2 2.12 | still proposed; a signed decision, not this stage's |

## 12. How the figures were computed

A scratch file `lean/SpecStubs_english-lean-s3.lean` (not committed) imported `VE.EnglishGrammar.ReadExamples`
from this worktree's build of `main` at `1e68d6d6` (`lake build` of the reader's modules, then `lake env lean`)
under Lean 4.24.0, and:

- wrote the catalogue of 2.4 (`ntTy` extended, `ranksStaged`), the 25 and 8 fixed rows of 2.5, the guard,
  attribute, property and integer rows of 2.6 as functions of their data, Python's product rows for da18, and
  every action of 2.7 as an `Action sig` over S2's `Ty`, `Ctx`, `TermVal` and `Reject`, with S2's `build`,
  `constant`, `ofToken`, `polarity` and `permute`;
- built each fixture grammar as S2's `grammar E L` for the object vocabulary followed by the S3 rows, with
  `acts E L` followed by their actions, and checked `Grammar.wf`, `terminatorFree` and `Grammar.typed` for
  each (`FO`, `FD`, `FP`, the renumbered `FD`, `FA`, `FR`, `FM`, cb1);
- computed every verdict with `parse` at cap 2 and `workBudget`, every outcome with `readDocument` and S2's
  `meaning`, every step figure with `Prepared.steps`, and every size by counting, all under `#guard` or
  `#eval`; the typed check of the environment was not run, because the fixture environments are Lean data
  without an environment JSON;
- computed lx1 to lx11 with S2's `Lexicon.failures` on environments written as `Env` values with their forms,
  and lx12, lx13 with `subjectFirst`; proved `valid_subject_first` for S2's `valid` conjoined with subject
  first;
- wrote `advice`, `obligations`, `admit` and `firstChecked` as in 4.3 and 5.3 and computed 8.8 and 8.9, the
  last two on S2's real `read` over `F` and `LF`;
- declared the signature of 5.2 with `fixedTable`, `lexRules`, `ranksFor`, `valueSorts`, `ty`, `fixedActs`,
  `lexActs` and `valid` as `opaque` constants over a structure that carries S2's `Env` with the new fields
  beside it (the flags as the list of attributes), and elaborated `unstaged_fixed`, `ty_catalogue`,
  `ty_property`, `valid_subject_first`, `grammar_extension`, `start_sentence` and `lexRules_terminatorFree`
  against it, and `obligations_exact`, `admit_ok`, `admit_exact`, `admit_no_premise` and `first_checked`
  against S2's `read`, each as a definition of type `Prop`; `grammar_rules` and the rank equation are `rfl`
  there; the S2 statements `read_ok`, `english_reading_unique` and `checked_rendering_exact` were re-checked
  at the types 5.5 cites.

All checks passed on 2026-10-05. What the stub does not show: that `lexRules` as it will be written produces
the hand-written rows (S3.2's "done when"), and anything about Python (ev5). The file is re-created from this
specification when S3.2 starts; its contents are sections 2.4 to 2.7, 5.2 to 5.4 and 8.
