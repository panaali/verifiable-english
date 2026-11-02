# English in Lean, S6 first layer: authored W1 rule blocks (statement specification)

> Status: statement specification, draft 2 (2026-10-31), branch `design/spec-el-s6` from `main` at `09fca5013`.
> Draft 2 applies the FIX edits of the statement review of draft 1 (`manage-agents/debates/spec-el-s6`, round 2
> of both seats, both Opus) and makes no other change.
> Backlog row spec-el-s6 (DRI 2026-10-31 00:15Z, sprint lever E3). This file states the item-1 statements of the
> **first S6 statement layer** of [english-lean-PLAN.md](english-lean-PLAN.md) (the **plan**): norm rule blocks and
> precedence lines, the first row of the plan's table 1.4. It covers authored blocks only (authoring mode). Nothing
> was built or run for this draft. No Lean block here has been elaborated. Every expected result in section 6 was
> derived by hand from the Python reader it replaces. Every Lean name cited as existing was read on `main` at
> `09fca5013`; every other name is new and is proposed here. Plans are frozen until 2026-11-12. This spec adds no
> design. Where the plans leave a point open, section 7 states it as an OPEN line.

## 0. Scope, one paragraph

Today `ve/norm_english.py` reads a W1 rule block in two ways. A hand splitter cuts the block at `", if "`,
`", unless "` and `" Except when "` and matches the consequence against an enumerated list. Separately, an Earley
run over the whole block checks that it has one derivation. Nothing connects the split to the tree (plan 1.4,
row 1). This layer moves the reading onto english-lean's proved engine. The block grammar becomes data: the
formula grammar `grammar E L` unchanged, followed by the norm rows. Every sentence of a block text must then
have exactly one derivation, and its meaning is computed from that derivation. A condition is read by the
formula grammar's own rules. A rule reaches the W1 node format only through the existing decoder
`VE.Norms.Wire.decodeNorm`. This item adds the Lean reader and its statements. It adds no service mode, no
Python relay and no authority change. Those are the layer's later steps, each with its own gate (section 5).

## 1. Sources and decisions

**Sources.**
- The plan: `english-lean-PLAN.md`, read on `design/syn2-english-lean` at `e64aee81d`. That is `main`'s text
  plus section 11, the DRI-decided synthesis round 2 edits. The parts used here:
  - 1.4 row 1 (line 164);
  - 2.5 (statement layers on the engine, line 325);
  - section 5, row S6: one layer per step, in the order of 1.4. Per layer, a delta report is reviewed and
    the DRI decides each changed rejection (line 608);
  - section 6: statement layers keep their current trust rows until their S6 step (line 710);
  - 7.8 (statement layers will show real differences);
  - section 11, "The E3 norm step": en-e3-norm is scheduled as one S6 statement layer (line 863).
- The layer's detailed plan: `docs/spec/en-e3-norm-PLAN.md` draft 1, read on `design/en-e3-norm` at `8a3e0778c`.
  The parts used are D1 to D4 and D10, and batch EN-1 (authored W1 blocks, lines 215-427). That plan's own review
  has not run (OPEN-2). This spec takes EN-1's objects and statements as its starting point. Section 1.2 lists
  each place where main forces a change.
- The frozen engine contracts on `main`:
  - `VE.Grammar`: `Meaning`, `OneReading`, `DocOneReading`, `readDocument`, `Outcome`, `doc_sound`,
    `doc_complete`, `doc_unique`, `RuleMap`, `RuleMap.Ok`, `rule_map_sem`;
  - the English instance `VE.EnglishGrammar`: `Tok`, `Terminal`, `terminators`, `terminatorFree`, `lex`,
    `grammar`, `ty`, `acts`, `sig`, `Sem`, `Ctx`, `Ctx.start`, `Scope`, `EFormula`, `ETerm`, `Reject`,
    `DState`, `Lexicon.valid`, `GrammarFault`, `read`, `read_complete_english`;
  - the W1 node and decoders: `VE.Norms.Node`, `VE.Norms.Role`, `VE.Norms.Regulated`,
    `VE.Norms.Wire.decodeNorm`, `VE.Norms.Wire.decodeNormsEnvironment`.
- The reference behaviour: `ve/norm_english.py` on `main`: `_bindings` :28-45, `_consequence` :90-109,
  `render_rule_sentence` :155-170, `_block_grammar` :210-245, `_parse_consequence` :248-268 and
  `parse_english` :272-366. The fixtures come from `tests/test_norm_english.py`.

### 1.1 Decisions taken from the plans (not reopened)

- **One reader** (en-e3-norm D1). Authored blocks are read by one grammar on `VE.Grammar`'s engine. The norm
  rows are data. No second reader, no matcher of commands.
- **Conditions are the formula grammar's reading** (D2). The norm grammar keeps every rule of `grammar E L`,
  with the same numbers, as a prefix. A condition subtree therefore has the value `read` gives it
  (`condition_same`).
- **`many` is refused in authoring** (D3, plan section 11 D11). Two derivations stop the reading, and both
  trees are kept.
- **One output path** (D4). A rule becomes a W1 node only through `VE.Norms.Wire.decodeNorm` (`Clause.toNode`).
- **Authority moves per layer, after a delta** (D10, plan section 5 row S6). This item changes no authority.

### 1.2 Corrections forced by main (proposed; the review decides)

- **R1. A block spans several sentences.** `lex` splits a text at every terminator token, and `read` refuses a
  grammar whose rows mention one (`terminatorFree`, `Read.lean:39-41`). "Rule 1. Every act may be done." is
  therefore two sentences. en-e3-norm's sketch gives each sentence one `NormStatement`
  (`DocOneReading … (rs.map (·, false))`), which cannot hold for a block of two or more sentences. Here each
  sentence has one **piece** (`Piece`, 2.3). A pure function `assemble` (2.4) groups the pieces into
  statements. The sketch's `NState.block` goes, and the state carries only the scope of the current clause.
- **R2. Plain-role consequences have no modal word.** EN-1 lists "the plain-role wordings" among its rows, but
  the sketch's `Force` has only the four modal words. Here `Clause.force` is a `Polarity` (2.2): a modal word,
  or a plain wording with its sign.
- **R3. The outcome keeps the engine's outcome.** `NormOutcome.stopped` carries the sentence index and the
  engine's `Outcome Tok Reject Piece`, as `ReadOutcome.stopped` does. This keeps the two witness trees of an
  ambiguous sentence. A resource stop is `.stopped i .budget`, as in `read`. Assembly faults get their own
  constructor, `misplaced`.
- **R4. Conditions are read in a fresh discourse state.** Python reads each condition alone
  (`_parse_guard`, `norm_english.py:54-72`, through a new `EnglishParser`). The norm actions therefore evaluate a
  condition in `{ Ctx.start DState.init with scope := σ }`, where `σ` is the consequence's bindings. The
  sketch's `NState.base : DState` is never changed, so it is dropped.
- **R5. Lexed sentences are an array.** `lex` returns `Array (Array Tok)`. `NormOneReading` therefore reads
  `sents.toList.map (·.toList)`, as `EnglishOneReading` does, not `sents.map`.
- **R6. Regulated declarations come from the environment JSON.** The Lean `Env` keeps only a predicate's
  `modal` flag. The rows therefore read the regulated declarations as the norms route decodes them
  (`regulatedOf`, 2.5). `Env.source`'s comment, 'read by `typedDocument` only' (`Lexicon.lean:356`), is then
  no longer true. A one-line comment hunk in `Lexicon.lean` joins the shared files.
- **R7. A soft-norms environment is decoded without its soft constructs** (en-s6b; DRI decision
  reviews/dri-decisions-20261102-en-s6b.md item 2). W1's decoder refuses `soft-norms@0`, and both pinned
  environments name it, so R6's `regulatedOf` would be `[]` there and no pinned block could read. Python's
  `_consequence` reads `regulated` under either profile. An environment whose `profiles` name `soft-norms@0` is
  therefore decoded after `VE.SoftNorms.Wire.stripSoft`, as the soft route decodes it; any other environment is
  decoded as R6 states.
- **R8. `Polarity.fits` lands with its theorem** (en-s6b; DRI decision reviews/dri-decisions-20261102-en-s6b.md item
  4). The reader does not read it: only `readNorm_regulated` states it. en-s6b decides that statement by a `#guard`
  over every section 6 fixture (section 4's substitution note), so `fits` is that guard's oracle in
  `Norm/Examples.lean`; it moves to `Norm/Rules.lean` with `readNorm_regulated`'s proof (en-s6c).

## 2. Definitions

### 2.1 Terms

- **Block text**: the text given to the reader. It is a sequence of rule blocks and precedence lines.
- **Rule block**: a header sentence, then one clause sentence, then zero or more except-when sentences.
- **Header sentence**: `Rule n.`, `Rule n (exception to rule m).` or `Rule n (exception to rules m1, m2 and m3).`.
  After "rules", each further number follows `,` or `and`, as Python's `rule_refs` allows (`norm_english.py:239`).
- **Clause sentence**: a consequence, then optionally `, if <formula>`, then optionally `, unless <formula>` or
  `, except when <formula>`, in that order, then the terminator.
- **Except-when sentence**: `Except when <formula>.`.
- **Precedence line**: `Rule n takes precedence over rule m.`.
- **Regulated predicate**: a predicate whose declaration has a `regulated` entry. Its role is `obligation`,
  `permission` or `plain` (`VE.Norms.Role`).
- **Consequence wording**: one of the fixed phrases that `_consequence` and `_block_grammar` generate for a
  regulated predicate and a sign (2.5). A consequence is matched only as a whole.
- **Bindings** of a consequence: the scope that `_bindings` builds, innermost first. Each argument sort has a
  reference text. The reference is "that <noun>" for a sort that occurs once. For a sort that occurs twice it
  is "the first <noun>" or "the second <noun>".

### 2.2 Values (`lean/VE/EnglishGrammar/Norm/Value.lean`, new)

```lean
namespace VE.EnglishGrammar.Norm
open VE.EnglishGrammar

/-- The four W1 modal words (`VE.Acts.Op` without `right`). -/
inductive Force where
  | must | needNot | may | mustNot
  deriving DecidableEq, Repr

/-- W1's stored sign: obligation `must` true, `need not` false; permission `may` true, `must not` false
(`ve/norm_english.py:97-100`). -/
def Force.sign : Force → Bool
  | .must => true | .needNot => false | .may => true | .mustNot => false

/-- R2: a consequence's force, either a modal word or a plain wording with its sign. -/
inductive Polarity where
  | modal (f : Force)
  | plain (positive : Bool)
  deriving DecidableEq, Repr

def Polarity.sign : Polarity → Bool
  | .modal f => f.sign
  | .plain b => b

/-- `strict` is W1; `default d` is a soft-norms default rule (EN-4; never produced here). -/
inductive Mode where
  | strict
  | default (decider : String)
  deriving DecidableEq, Repr

/-- Whom a clause binds, as read (en-e3-norm D8). Authoring produces only `every`. -/
inductive Bearer where
  | every (sort : String)
  | named (const : String)
  | author
  | unstated
  deriving DecidableEq, Repr

inductive Place where
  | act | guard | carveOut | bearer
  deriving DecidableEq, Repr

/-- A phrase parsed and not formalised (en-e3-norm D5, EN-7). Always empty in authoring. -/
structure Residual where
  start : Nat
  stop : Nat
  row : String
  owner : String
  place : Place
  deriving DecidableEq, Repr

/-- One reading of one norm clause. In authoring `args = []`: W1 binds every slot of the predicate by
"Every"/"each", and the W1 wire has no argument field (`normFields`, `Norms/Wire.lean:319`). -/
structure Clause where
  bearer : Bearer
  force : Polarity
  mode : Mode
  pred : String
  args : List ETerm
  guard : EFormula
  carveOuts : List EFormula
  residuals : List Residual
  deriving DecidableEq, Repr

structure Header where
  number : Nat
  exceptionTo : List Nat
  deriving DecidableEq, Repr

inductive NormStatement where
  | rule (h : Header) (c : Clause)
  | precedence (n m : Nat)
  | source (cs : List Clause)        -- translation mode (EN-5); never produced here
  deriving DecidableEq, Repr

def NormStatement.clauses : NormStatement → List Clause
  | .rule _ c => [c] | .precedence _ _ => [] | .source cs => cs

def NormStatement.number? : NormStatement → Option Nat
  | .rule h _ => some h.number | _ => none

/-- The rule numbers a statement names: a header's exception targets, both sides of a precedence line. -/
def NormStatement.refs : NormStatement → List Nat
  | .rule h _ => h.exceptionTo | .precedence n m => [n, m] | .source _ => []

def ruleCount (rs : List NormStatement) : Nat := (rs.filterMap NormStatement.number?).length
```

### 2.3 Pieces and state (R1, R4; `Norm/Value.lean`)

```lean
/-- The value of one sentence of a block text. -/
inductive Piece where
  | header (h : Header)
  | clause (c : Clause)
  | exceptWhen (φ : EFormula)
  | precedence (n m : Nat)
  deriving DecidableEq, Repr

/-- The bindings of the current block's consequence (a `Scope`), or none. -/
structure NState where
  scope : Option (List (String × String))
  deriving DecidableEq, Repr

def NState.init : NState := ⟨none⟩
```

Transitions, one per piece. A header or a precedence line sets `scope := none`. A clause sets
`scope := some σ`, where `σ` is its consequence's bindings. An except-when sentence leaves the state unchanged.
Its formula is evaluated with the state's scope, or with `[]` when the scope is none.

Numbers: a numeral token's value `v : Int` becomes `v.toNat`. "Rule 0", or a reference to 0, is therefore
refused by `assemble` (`expectedRule` or `unknownRule`). No new `Reject` constructor is needed.

### 2.4 Assembly

```lean
inductive BlockFault where
  | expectedRule (index number : Nat)   -- sentence `index` opens a block not numbered `number`
  | noConsequence (index : Nat)         -- the header at `index` has no clause sentence
  | strayConsequence (index : Nat)      -- a clause sentence outside a block, or a second one in a block
  | strayCarveOut (index : Nat)         -- an except-when sentence before its block's clause
  | unknownRule (number : Nat)          -- a reference outside 1 … number of blocks
  deriving DecidableEq, Repr

def assemble (ps : List Piece) : Except BlockFault (List NormStatement)
```

`assemble` reads the pieces left to right and keeps an open block, if there is one, and the count `k` of blocks
opened so far.
- A header `h` at index `i` first closes the open block. The block fails with `noConsequence` if it has no clause.
  If `h.number ≠ k + 1`, the result is `expectedRule i (k + 1)`. Otherwise `h` opens block `k + 1`.
- A clause `c` at `i` needs an open block without a clause, else `strayConsequence i`. It becomes that block's
  clause.
- `exceptWhen φ` at `i` needs an open block with a clause, else `strayCarveOut i`. It appends `φ` to that
  clause's `carveOuts`.
- `precedence n m` closes the open block and emits `.precedence n m`.

At the end, the open block is closed. Then every number in `rs.flatMap NormStatement.refs` must lie in
`1 … ruleCount rs`, else `unknownRule` with the first one out of range. A block is emitted as `.rule h c` at its
header's position, so statements keep text order.

Python's counterparts: `Expected Rule {index} with its own block`, `Expected a complete rule sentence` and
`UnknownRule: display reference` (`norm_english.py:296`, :305, :326, :347).

### 2.5 The grammar, actions and types (`Norm/Rules.lean`, new; generated `Fixed/Norms.lean`)

```lean
/-- Whether a polarity is one that the role's consequence rows generate. It is here, not in `Value.lean`, so
that `Value.lean` imports only `Syntax.lean` (R8: in `Norm/Examples.lean` until `readNorm_regulated` is proved). -/
def Polarity.fits : Polarity → VE.Norms.Role → Bool
  | .modal .must, .obligation => true
  | .modal .needNot, .obligation => true
  | .modal .may, .permission => true
  | .modal .mustNot, .permission => true
  | .plain _, .plain => true
  | _, _ => false

/-- R6: the regulated declarations, as the norms route decodes them (`decodeSource`, `Wire.lean:371`). R7: an
environment that names `soft-norms@0` is decoded without its soft constructs. -/
def regulatedOf (E : Env) : List VE.Norms.Regulated :=
  let soft := (VE.Route.Gate.profilesOf E.source).toOption.any (·.contains VE.SoftNorms.Wire.softProfile)
  match (if soft then VE.SoftNorms.Wire.stripSoft E.source else .ok E.source) >>=
      (VE.Norms.Wire.decodeNormsEnvironment · (acts := true)) with
  | .ok ne => ne.regulated
  | .error _ => []

/-- `grammar E L`'s rules first and unchanged, then the norm table's rows (`ve/english_grammar/norms@0.json`),
then the consequence rows generated from `regulatedOf E` and `L`. New nonterminals are numbered from
`(grammar E L).rank.size`; the start symbol is the norm sentence. -/
def normGrammar (E : Env) (L : Lexicon) : VE.Grammar.Grammar Terminal

/-- `acts E L` first and unchanged, then the norm actions. -/
def normActs (E : Env) (L : Lexicon) : Array (VE.Grammar.Action sig)

/-- `ty E L` below `(grammar E L).rank.size`; the norm types above. -/
def normTy (E : Env) (L : Lexicon) : Nat → Ty

def prefixMap : VE.Grammar.RuleMap := ⟨id, id⟩

/-- The value of a norm sentence's tree: the start symbol's value applied to the state. -/
def normMeaning (G : VE.Grammar.Grammar Terminal) (acts : Array (VE.Grammar.Action sig)) :
    VE.Grammar.Meaning Tok NState Reject Piece
```

**One new semantic type.** `Ty` gains `norm`, with `Sem .norm = NState → Except Reject (Piece × Bool × NState)`.
The start symbol has that type. Other new types are allowed if the rows need them. All new constructors of
`Ty` and their `Sem` cases go in one hunk each of `Syntax.lean` and `Actions.lean` (en-e3-norm 2.2), plus one
`import VE.EnglishGrammar.Norm.Value` line in `Actions.lean`. No existing
constructor, case or statement changes. `normMeaning` mirrors `meaning`: `some ⟨.norm, f⟩ => f st`, and
anything else is `.error .internal`.

**The norm table's rows.** The exact token sequences follow. `kw` is the engine's structure-word terminal.
"N" is the numeral class `cls .numeral`. "F" is the condition nonterminal: the formula nonterminal that the
sentence rule of `grammar E L` reads, which the stub names.

| Sentence | Rows | Value |
|---|---|---|
| header | `kw "rule"` N | `.header ⟨n, []⟩` |
| | `kw "rule"` N `(` `kw "exception"` `kw "to"` `kw "rule"` N `)` | `.header ⟨n, [m]⟩` |
| | `kw "rule"` N `(` `kw "exception"` `kw "to"` `kw "rules"` N (`,` N \| `kw "and"` N)* `)` | `.header ⟨n, refs⟩`, in text order |
| precedence | `kw "rule"` N `kw "takes"` `kw "precedence"` `kw "over"` `kw "rule"` N | `.precedence n m` |
| clause | C [`,` `kw "if"` F] [`,` (`kw "unless"` \| `kw "except"` `kw "when"`) F] | `.clause c`. `c` is C's skeleton with `guard` the first F (`.top` if absent) and `carveOuts` the second (`[]` if absent) |
| except-when | `kw "except"` `kw "when"` F | `.exceptWhen φ` |

`(`, `)` and `,` are `exact` punctuation terminals with the spacing Python renders: "1, 2", "rule 1)".

**The consequence rows (C).** Python generates these in `_block_grammar` :216-228. For each `r ∈ regulatedOf E`,
whose predicate `p` has argument sorts `s1 … sk`, and each sign `b`, the wording is:
- obligation: the act with `{0} ` replaced once by `{0} must ` (`b` true) or `{0} need not ` (`b` false);
- permission: the same with `may` (`b` true) or `must not` (`b` false);
- plain: `L`'s negative of `p` when `b` is false and one is selected, else `L`'s wording of `p`. When `b` is false
  and no negative is selected, the wording is "For every <noun1>, for each <noun2>, …, it is not the case that
  <wording with the references>", with the first letter capitalised.

The slots are filled with "Every <noun1>" and "each <nouni>" for i ≥ 2, where `<nouni>` is the i-th display of
`_bindings` (:28-44): `L`'s noun, prefixed "first " or "second " when its sort occurs twice. Variants are added
as follows:
- when k = 2, the same wording with "each <noun2>" replaced by "any <noun2>";
- for a permission with `b` false, "Every <noun1> must not " replaced once by "No <noun1> may ".

Each variant is made from the base wording; the two are not combined. Duplicate variants of one predicate and
sign are removed. A predicate with no argument gets no rows. A predicate whose arguments have a sort three or
more times gets no rows (Python raises `ResourceLimit` there, :41). Each variant is one rule whose right side is
`textSyms v contentTerminal` (`Rules.lean:122`): a word is `content` (equal after `fold`); every other token is
`exact`, glued flags included. A variant for which `textSyms` is `none` gets no row. Its value is the skeleton below, with the bindings `σ` of `_bindings`:
`{ bearer := .every s1, force, mode := .strict, pred := p, args := [], guard := .top, carveOuts := [], residuals := [] }`.
The `force` is `.modal` of the modal word for obligation and permission, and `.plain b` for plain.

**Conditions.** Each F is evaluated in `{ Ctx.start DState.init with scope := σ }` (R4). In a clause, `σ` is the
consequence's bindings; in an except-when sentence it is the state's. A rejection from F is the sentence's
rejection. The conclusion mark is always `false`: no norm row has a conclusion marker.

### 2.6 Reading

```lean
inductive NormOutcome where
  | ok (rs : List NormStatement)
  | invalidGrammar (why : GrammarFault)
  | lexical (r : Reject)
  | stopped (index : Nat) (o : VE.Grammar.Outcome Tok Reject Piece)
  | misplaced (f : BlockFault)

/-- `read`'s checks, on the norm grammar, in `read`'s order. The start type is `.norm`. Then `lex`, then
`readDocument` from `NState.init`, then `assemble`. -/
def readNorm (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) : NormOutcome

def NormOneReading (E : Env) (O : Overlay) (L : Lexicon) (s : String) (rs : List NormStatement) : Prop :=
  L.valid E O = true ∧
  ∃ sents ps st2, lex s = .ok sents ∧
    VE.Grammar.DocOneReading (normGrammar E L) (normMeaning (normGrammar E L) (normActs E L)) NState.init
      (sents.toList.map (·.toList)) (ps.map (·, false)) st2 ∧
    assemble ps = .ok rs
```

### 2.7 To the W1 node (`Norm/Elab.lean`, new)

```lean
def ruleName (i : Nat) : String := "rule-" ++ toString i

/-- `{"norm": {"name", "predicate", "sign", "guard", "unless", "over"}}`: `predicate` is `c.pred`, `sign`
is `c.force.sign`, `guard` is `c.guard.encode`, `unless` is `c.carveOuts.map EFormula.encode`. -/
def Clause.wire (name : String) (over : List String) (c : Clause) : Lean.Json

def Clause.toNode (name : String) (over : List String) (c : Clause) : Except String VE.Norms.Node :=
  VE.Norms.Wire.decodeNorm (c.wire name over)

/-- Rule `n`'s `over`: its header's targets, then the `m` of every `.precedence n m`, in text order
(`norm_english.py:290`, :323). -/
def overOf (rs : List NormStatement) (n : Nat) : List Nat

/-- The nodes of the rules in order; rule `i` is named `ruleName i` (Python without a manifest, :307). -/
def toNodes (rs : List NormStatement) : Except String (List VE.Norms.Node)
```

## 3. English: one reading each

### 3.1 The sentence forms

- **"Rule 3."** Block 3 starts here. It is an exception to no rule.
- **"Rule 3 (exception to rule 1)."** Block 3 starts here, and its rule is an exception to rule 1.
- **"Rule 3 (exception to rules 1 and 2)."** Block 3 starts here, and its rule is an exception to rules 1 and 2,
  in that order.
- **"Rule 2 takes precedence over rule 1."** Rule 1 is added to the rules that rule 2 overrides. The line opens
  no block.
- **"Every act must be done."** For each act, doing it is obligatory. Obligation, sign true.
- **"Every act need not be done."** No act is obligatory. Obligation, sign false.
- **"Every act may be done."** Each act is permitted. Permission, sign true.
- **"Every act must not be done."**, or equally **"No act may be done."** No act is permitted. Permission, sign
  false.
- **"Every state may help each person."**, or equally **"… any person."** For each state and each person, the
  state is permitted to help the person. Every slot is bound.
- **"Every item is admitted."** Each item is admitted. Plain role, sign true.
- **"Every item is not admitted."** and **"For every item, it is not the case that that item is admitted."**
  No item is admitted. Plain role, sign false. The first form needs a selected negative; the second is the form
  without one.
- **"…, if <A>"** The rule applies to a case only when A holds of it. A refers to the consequence's subjects by
  "that <noun>".
- **"…, unless <B>"**, **"…, except when <B>"** and **"Except when <B>."** The rule does not apply where B holds.
  Several carve-outs each exclude their cases, in the order written.

### 3.2 The theorems, in plain words

- `prefixMap_ok`: the norm grammar contains the formula grammar unchanged, with the same rule numbers and actions.
- `condition_same`: any piece of text that the formula grammar derives, the norm grammar derives too, with the
  same value. A condition therefore means exactly what it means in a formula-level sentence.
- `start_norm`: the norm grammar's start symbol has the norm sentence type.
- `normMeaning_unmarked`: no norm sentence carries a conclusion mark.
- `readNorm_sound`: when the reader returns statements, each sentence of the text has exactly one derivation,
  the derivations' pieces assemble into exactly those statements, and the lexicon is valid.
- `readNorm_complete`: when a text has that property and the grammar passes its checks, the reader returns those
  statements, unless it runs out of budget.
- `readNorm_unique`: a text has at most one list of statements.
- `readNorm_numbered`: blocks are numbered 1, 2, … in order, and every rule a header or precedence line names
  exists.
- `readNorm_authoring`: every clause read is a strict W1 clause over "Every <first sort>". It has no argument
  terms and no residuals.
- `readNorm_regulated`: every clause names a regulated predicate of the environment, with a force that the
  predicate's role allows.
- `toNode_fields`: the decoder keeps the rule's name, predicate, sign, `over` list and number of carve-outs.

## 4. Lean: the exact statements

Namespace `VE.EnglishGrammar.Norm`. The modules are those of en-e3-norm EN-1: `Norm/Value.lean`,
`Norm/Rules.lean`, `Norm/Read.lean`, `Norm/Elab.lean` and `Norm/Examples.lean`, plus the generated
`Fixed/Norms.lean`.

```lean
theorem prefixMap_ok : ∀ (E : Env) (L : Lexicon),
  prefixMap.Ok (grammar E L) { normGrammar E L with start := (grammar E L).start } (acts E L) (normActs E L)

theorem condition_same : ∀ (E : Env) (L : Lexicon) (X : VE.Grammar.Sym Terminal) (t : VE.Grammar.Tree Tok),
  t.derives (grammar E L) X = true →
  t.derives (normGrammar E L) X = true ∧ t.sem (normGrammar E L) sig (normActs E L) = t.sem (grammar E L) sig (acts E L)

theorem start_norm : ∀ (E : Env) (L : Lexicon), normTy E L (normGrammar E L).start = .norm

theorem normMeaning_unmarked : ∀ (E : Env) (L : Lexicon) (st st2 : NState) (t : VE.Grammar.Tree Tok) (p : Piece)
    (c : Bool),
  normMeaning (normGrammar E L) (normActs E L) st t = .ok (p, c, st2) → c = false

theorem readNorm_sound : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) (rs : List NormStatement),
  readNorm E O L b s = .ok rs → NormOneReading E O L s rs

theorem readNorm_complete : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List NormStatement),
  NormOneReading E O L s rs →
  (normGrammar E L).wf = true → terminatorFree (normGrammar E L) = true →
  (normGrammar E L).typed sig (normTy E L) (normActs E L) = true → normTy E L (normGrammar E L).start = .norm →
  readNorm E O L b s = .ok rs ∨ ∃ i, readNorm E O L b s = .stopped i .budget

theorem readNorm_unique : ∀ (E : Env) (O : Overlay) (L : Lexicon) (s : String) (rs rs2 : List NormStatement),
  NormOneReading E O L s rs → NormOneReading E O L s rs2 → rs2 = rs

theorem readNorm_numbered : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List NormStatement),
  readNorm E O L b s = .ok rs →
  rs.filterMap NormStatement.number? = List.range' 1 (ruleCount rs) ∧
  ∀ n ∈ rs.flatMap NormStatement.refs, 1 ≤ n ∧ n ≤ ruleCount rs

theorem readNorm_authoring : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List NormStatement),
  readNorm E O L b s = .ok rs →
  (∀ r ∈ rs, ∀ cs, r ≠ .source cs) ∧
  ∀ c ∈ rs.flatMap NormStatement.clauses,
    c.mode = .strict ∧ c.residuals = [] ∧ c.args = [] ∧
    ∃ r ∈ regulatedOf E, r.name = c.pred ∧ ∃ s1 rest, r.sorts = s1 :: rest ∧ c.bearer = .every s1

theorem readNorm_regulated : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List NormStatement),
  readNorm E O L b s = .ok rs →
  ∀ c ∈ rs.flatMap NormStatement.clauses, ∃ r ∈ regulatedOf E, r.name = c.pred ∧ c.force.fits r.role = true

theorem toNode_fields : ∀ (n : String) (o : List String) (c : Clause) (nd : VE.Norms.Node),
  c.toNode n o = .ok nd →
  nd.name = n ∧ nd.pred = c.pred ∧ nd.sign = c.force.sign ∧ nd.over = o ∧ nd.carveOuts.length = c.carveOuts.length
```

**How each is expected to follow.** These notes are not part of the statements.
- `prefixMap_ok` unfolds the definitions: the rules and actions are array prefixes.
- `condition_same` is `rule_map_sem` with `prefixMap_ok`. `prefixMap.tree t = t` and
  `Sym.rename id X = X` are small lemmas, and `Tree.derives` does not read `start`.
- `start_norm` is `rfl`.
- `normMeaning_unmarked` is a case split over the norm actions.
- The three reading theorems come from `doc_sound`, `doc_complete` and `doc_unique`. `readNorm_unique` also
  uses the injectivity of `(·, false)` and the determinism of `assemble`. `readNorm_complete`'s premises are
  `read_complete_english`'s, on the norm grammar.
- `readNorm_numbered` comes from `assemble`'s checks.
- `readNorm_authoring` and `readNorm_regulated` need an induction over the actions: every clause value comes
  from a consequence row, and its data comes from `regulatedOf E`.
- `toNode_fields` reads `decodeNorm`'s fields.

As en-e3-norm EN-1 allows for `toNode_fields`, a proof of `readNorm_authoring`, `readNorm_regulated` or
`toNode_fields` that exceeds the batch may become a `#guard` over every fixture of section 6. The build records
each such substitution. No other statement may be weakened.

**Not claimed.** The reader does not claim that the rules form a valid W1 document: typing in the predicate's
context, cycles and the `GuardOnOwnOutcome` advice. That stays with the existing W1 checks that run when
`toNodes`' output is decoded as a document (`VE.Norms.Wire.decodeSource`, `validate`). Section 6 tests it.

## 5. What this item is not

- Not the mode `english.statement`, the relay or shadow (EN-2); not authority or Python deletions (EN-3); not soft
  blocks (EN-4); not translation mode, residuals, commitment rows or list items (EN-5 to EN-9).
- No trust or assurance-manifest row moves. The layer keeps its current row until its S6 step (plan section 6).
  The new `Norm/*.lean` definition files and `norms@0.json` join the `actions_version` lock (plan section 4).
- Every behaviour difference from Python is recorded at EN-2, in the delta report that the S6 gate reviews. The
  differences already known from the definitions above:
  - an empty text: Python accepts zero rules, Lean refuses with `lexical .emptyDocument`;
  - layout: blocks sharing a line, a block over several lines, a blank or trailing line (:283). EN-1 has no
    layout check; the DRI decides at EN-2's delta (plan section 5, row S6);
  - conditions out of the rendered order, or two `, if` parts, which Python's split may accept;
  - a predicate with a sort three times, which makes Python refuse every text in its environment;
  - a predicate with no argument;
  - a consequence variant that does not lex as one sentence: Lean gives it no row, while Python's grammar has one;
  - casing: Lean's `kw` accepts a sentence-initial lowercase `rule` or `except when`, which Python's
    case-sensitive `_HEADER`, precedence match and `" Except when "` split refuse; Python's `re.I` carve-out match
    accepts `, except When` and other mixed casings, which `kw` refuses (`Token.lean:74`);
  - case folding outside ASCII (`fold` against Python's `casefold`);
  - spacing outside the lexer's rule.

## 6. Acceptance fixtures (`Norm/Examples.lean` `#guard`s, and `tests/test_english_statement_blocks.py`)

The environments come from `tests/test_norm_english.py` and `tests.test_norms`: `environment`, `permission`,
`obligation`, and the plain environment of `test_plain_negative_is_inside_universal_and_uses_declared_negative`.
Sentence indices count from 0.

| # | Text | Expected |
|---|---|---|
| f1 | the four-rule text `render_english` gives in `test_four_wordings_and_identity_manifest` | `ok`; `toNodes` equals Python's nodes, including `over = ["rule-1"]` |
| f2 | `Rule 1. No act may be done.` | `ok`; one clause, `force = .modal .mustNot`, sign false |
| f3 | `Rule 1. A act may be done.` | `stopped 1 .noDerivation` |
| f4 | `Rule 1. Every act should be done.` | `stopped 1 .noDerivation` (a soft wording; EN-4) |
| f5 | `Rule 1. Every state may help each person.`, and the `any person` variant | both `ok`, same statements |
| f6 | the same with `every person` | `stopped 1 .noDerivation` |
| f7 | `Rule 1. Every act must not be done.` `Rule 2. Every act may be done.` `Rule 2 takes precedence over rule 1.` (three lines) | `ok`; rule 2's `overOf` is `[1]`; node `over = ["rule-1"]` |
| f8 | the three-rule text of `test_whole_block_earley_checks_multiple_parents_and_clause_boundary` | `ok`; rule 3's `exceptionTo = [1, 2]` |
| f9 | f8 with `rules 1, and 2` | `stopped 4 .noDerivation` (the third header) |
| f10 | `Rule 1. Every act may be done, except when this holds in all cases.` | `ok`; `carveOuts` has one formula |
| f11 | the rendered text of `test_deontic_guard_and_carveout_round_trip` (a guard, then two `Except when` sentences) | `ok`; `toNodes` equals Python's nodes |
| f12 | the two plain texts of `test_plain_negative_…` (with and without a selected negative) | `ok`; sign false; nodes equal Python's |
| f13 | `Rule 2. Every act may be done.` | `misplaced (.expectedRule 0 1)` |
| f14 | `Rule 1. Every act may be done.` `Rule 1 takes precedence over rule 3.` | `misplaced (.unknownRule 3)` |
| f15 | `Rule 1. Rule 2. Every act may be done.` | `misplaced (.noConsequence 0)` |
| f16 | `Rule 1. Except when this holds in all cases.` | `misplaced (.strayCarveOut 1)` |
| f17 | `Rule 1. Every act must be sung.` (undeclared act) | `stopped 1 .noDerivation` |
| f18 | environment `FD` (`ReadExamples.lean:77`) with `norms@0` and one permission predicate over `service`, named in `Norm/Examples.lean`; text `Rule 1. <its may wording>, if every deployed service is reviewed.` | `stopped 1 (.ambiguous t u)`, with `t ≠ u` (that formula is `many` at `ReadExamples.lean:253`). If EN-0's stub shows otherwise, f18 becomes an EN-0 computed fixture and the change is recorded |
| f19 | the empty text | `lexical .emptyDocument` |
| f20 | the RSP lines `rules.d1.ve:16`, `:22`, `:28`, `:40` named by en-e3-norm EN-1 (f6-maintain, f6-keep-past, f8-public, f10-in-line) | `ok`; nodes equal Python's |
| f21 | the constitution unit u0125.s04.p2's block, `Rule 1. Every instance of Claude must not directly deny being Claude.` | `ok`; permission, sign false |
| f22 | the 120 pinned blocks (RSP 76, FSF 44; en-e3-norm :159, :205) | Python's node for each block not headed by `should`; `stopped 1 .noDerivation` for each `should` block; a block that differs is listed for EN-2's delta and does not fail this item |
| f23 | the text of `test_same_sort_binary_rule_round_trip_and_dangling_precedence` (`Rule 1. Every first act may help each second act.`), and its `any second act` variant | both `ok`, with the same statements |
| f24 | `Rule 9 takes precedence over rule 1.` | `misplaced (.unknownRule 9)` |

f1, f7, f8 and f11 also pass `toNodes`' output to `VE.Norms.Wire.decodeSource` (the "not claimed" line of
section 4) and expect `ok`.

**Seeded bugs.** Each is introduced, shown to fail, and restored.
- Map `.mustNot` to `true` in `Force.sign`: f1, f2 and f21 fail.
- Drop the carve-out in the `, unless`/`, except when` action: f10 fails.
- Skip the number check in `assemble`: f13 fails.
- Evaluate an except-when condition with scope `[]`: f11 fails.

## 7. OPEN lines (for the DRI; not decided here)

- **OPEN-2. Owner and remaining EN-0 work.** english-lean-PLAN section 11 schedules en-e3-norm as this S6 layer,
  and en-e3-norm's EN-0 names its own spec file, `docs/spec/en-e3-norm.md`. That plan's review has not run, and
  its pipeline has been held since 2026-10-29 19:12Z. This file states EN-1's statements only. The DRI decides
  three things:
  - whether a PASS of this review stands as EN-0's statement review for EN-1;
  - whether the backlog rows en-s6 and en-e3 are pointed at EN-1;
  - who does the rest of EN-0: the stub elaboration under Lean 4.24.0, recording Python's nodes for the pinned
    blocks, and the `Catalogue.lean` question of en-e3-norm 2.2. This spec assumes they become the first step
    of the build row.
- **OPEN-3 (answered by the review).** The 120 blocks are RSP 76 and FSF 44 (en-e3-norm :159).
  `usecases/openai-preparedness/rules.d1.ve` is not pinned.
