# Typed attitudes as conditions of norms (`attitudes@0`): statement spec (AT-0)

> **Status.** Draft 2, 2026-10-13, branch `design/attitudes`. AT-0's statement spec for
> [attitudes-PLAN.md](attitudes-PLAN.md) draft 3 (cited as **PLAN**; its debate items as **A1–A6**, **F3–F7**, the
> cross-plan synthesis edits as **edit 1–10**). For AT-0's statement review; nothing here is built or proved.
> Draft 2 applies the statement review of draft 1 (Astra and Fable, `manage-agents/debates/attitudes-spec/`,
> converged after round 3 on **FIX; the build may not start**). Its corrections are cited as **SR-1 to SR-8** and
> listed in section 14; draft 2 makes them and no other change.
>
> **What was checked, and how.** Draft 1's definitions and statements were type-checked in the untracked stub
> `lean/SpecStubs_attitudes.lean`, each statement as `def <name> (binders) : Prop := <conclusion>` (the stub
> prefixes unused binder names with `_`), by `lake --dir /home/seyran/code/ve-nightly/lean env lean
> lean/SpecStubs_attitudes.lean` against the build of `main` at `49de179e`, this branch's base (the branch adds
> docs only). Draft 1's fixture numbers were computed by `#eval`, `#guard` or `decide` in that stub, not by hand.
> **Draft 2's changes are not elaborated**: the stub in the worktree is still draft 1's, and every definition,
> statement, diagnostic text and fixture value that section 14 lists as changed or new is written here, not
> computed. They are marked *expected* where a value is given. Elaborating a statement is not evidence that it holds:
> a small-scope counterexample search (section 9) found none on draft 1, and only AT-1's proofs will establish the
> statements. No model calls were made.
>
> **Not passable yet.** AT-0 PASS needs, in this order (SR-8): E1's and E2's outcomes written into `table` with
> their items, including E2's decision on the asserted-content negated knowledge row (section 3.1's last row,
> section 11 item 16); the closure review holding on the frozen table; the stub updated to draft 2 and elaborated;
> every fixture and the section 9 search re-run on the frozen table, with draft 2's new refusals (D6a–D6b,
> D14a–D14c) in the search's pool; and the reviewers' re-review of the statements section 14 lists as changed, and
> only those. Until E1 and E2 report, the frozen `table` admits nothing: `knows` and every "thinks it *w*" are
> refused (fixture D0, section 5). The fixtures use `fixtureTable`, a hypothetical E1/E2 outcome written only for
> fixtures.

## 0. Reading this spec

- Section 1 says who owns what. Section 2 defines the profile in Lean. Section 3 gives the English, with one reading
  per wording. Section 4 is the wire. Section 5 lists the diagnostics in order. Section 6 states the theorems of
  AT-1 to AT-5. Section 7 lists the fixtures with their computed values, and section 9 the counterexample search.
  Section 10 answers the integration questions the PLAN left to AT-0. Section 11 lists every place where this spec
  differs from the PLAN's Lean text, with the reason. Section 12 is the review checklist. Section 14 lists draft 2's
  corrections (SR-1 to SR-8), each with the places it changes.
- Names owned by other plans are used through their reviewed interfaces only. The stub declares stand-ins for them,
  with the bodies the synthesis gives, so that this profile's statements elaborate: QS-1's `VE.Closure.Order`,
  `Caps`, `Order.admit`, `Order.atLeast` (owner: quantities, reviewed in QT-0); PK-1's `PackKind`, `RequestPath`,
  `Pack`, `packOrder` and a pack-premises accessor (owner: the RD-9 composition owner); AR-10's `ProfileRow`,
  `profileTable`, `gateOf` (owner: AR-10). The functions new in AT-3a (`decodeAttDoc`, `encodeElaboration`) and AT-5
  (`renderCond`, `readCond`, `readGuard`, `readGuardAll`, `readRule`, `readRuleAll`, `refusalOf`) are stand-ins
  too; their bodies are those batches' work. So is `VE.Attribution.Words.wantsPhrase?`, `reports@0`'s `wants` test
  moved into Lean by AT-1 (section 2.6, SR-3). The English grammar's lexical data (`VE.EnglishGrammar.Env`,
  `Overlay`, `Lexicon`, `Lexicon.failures`) is used as it is on `main`. A changed interface reopens only the
  statements that name it.

## 1. Owners

| Piece | Owner | Here |
|---|---|---|
| The four report acts and their names | `VE.Reports.Act`, `Act.name` (`reports@0`) | reused as `Mode.act` |
| Their English verbs and synonyms | `lean/VE/Attribution/Words.lean` (new: AT-1 creates it with the `wants` test, SR-3; AT-5 adds the verbs, F6) | `VE.Attitudes.Words` imports it and adds only `knows` and `thinks` |
| Content identity | syntax-tree equality (`VE.Reports.content_structural`) | reused; no hashing |
| De-duplication of keys | `VE.Reports.dedup` | reused |
| Quantifier-free formulas | `VE.Norms.Formula.qfree` | reused (A5) |
| Order closure, caps | QS-1: `VE.Closure.Order`, `Order.atLeast := reachEval .star`, `Caps`, `Order.admit`, `atLeast_refl`, `atLeast_trans`, `reachable_star_iff` | `Scale.atLeast` is `Order.atLeast`; no second closure (edit 1) |
| Likelihood words, `table`, E1/E2 gating, `lowerBound`, the record of which item passed each entry, the closure review | attitudes (`VE.Attitudes.Scale`) | section 2.1 |
| Extra base premises on the layered and readings routes | PK-1 packs, `transfers_append` | attitudes is the `attitudes` provider (edit 6) |
| Profile registration | AR-10's profile-gate table | one row (edit 7) |
| Refusals and their rewrites (English) | english-lean's catalogue | rows added by AT-5 (edit 9), each with its category and candidate readings (SR-5) |
| English lexical data: sort nouns, predicate wordings, constant spellings, and their validity | the English grammar: `VE.EnglishGrammar.Env`, `Overlay`, `Lexicon`, `Lexicon.failures`, `Lexicon.valid` (`lean/VE/EnglishGrammar/Lexicon.lean`); decoded by `Env.decode`, `Overlay.decode`, `Run.decodeLexicon` | carried as `AttDoc.lex`; checked by D6a–D6b; read by D14c, `renderCond` and the readers (SR-3) |
| The `wants` verb-phrase test ("Y to VP") | `reports@0`: `_subject_split` and `_infinitive` in `ve/report_english.py` (Python only on `main`) | moved into Lean as `VE.Attribution.Words.wantsPhrase?` by AT-1, the first batch whose check calls it; D14c and `renderCond` call it; no attitude-local classifier (SR-3; section 12 records the Python copy's removal as open) |
| Intentional action ("intends to VP") | residual; events-time-causation's ET-D2 designs the bridge | not admitted (edit 3) |
| Distribution over joined acts | act-phrases, deontic modals only | none here (edit 4) |
| Hedged calculation claims | a separate bridge, unowned | not attitude conditions (edit 5) |

## 2. Definitions

All Lean in this section is in `namespace VE.Attitudes` with `open VE.Reports (Act)` and `universe u`, in the order
the stub elaborates it. AT-1 places it in `lean/VE/Attitudes/{Scale,Syntax,Frame,Semantics}.lean`.

### 2.1 Words, the scale and the frozen table

A **likelihood word** is written after "thinks it", in lower case. A word is **admitted** only if E1's certainty
item confirms its lower-bound reading ("quite likely" read as "quite likely or more"); every other word, including
words that point downward such as "unlikely", is refused (A1). A **scale pair** `(a, b)` reads "a is at least as
likely as b". The **frozen table** records each admitted entry with the pre-registered item that passed it. Its
**closure review** (debate round 3) holds exactly when the reflexive and transitive closure of the frozen pairs
adds no pair, and no premise-3 word, without its own passing item; every entry is between admitted words; and
premises 2 and 3 are present only with premise 1.

```lean
abbrev Word := String
/-- The id of the pre-registered E1 or E2 item that passed an entry, e.g. "E1.pair.very-likely.quite-likely". -/
abbrev Item := String

/-- `above` lists pairs `(a, b)` read "a is at least as likely as b". -/
structure Scale where
  words : List Word
  above : List (Word × Word)
  deriving DecidableEq, Repr

def Scale.toOrder (σ : Scale) : VE.Closure.Order Word := ⟨σ.words, σ.above⟩

/-- The reflexive and transitive closure of `above`: QS-1's, never a second closure. -/
def Scale.atLeast (σ : Scale) (a b : Word) : Bool := σ.toOrder.atLeast a b

/-- The frozen meaning of `attitudes@0`: each admitted entry with the item that passed it. -/
structure Table where
  /-- E1's words, in E1's order -/
  candidates : List Word
  /-- words whose certainty item passed (E1, at least 34 of 40): the only words admitted after "thinks it" -/
  lowerBound : List (Word × Item)
  /-- `(a, b, item)`: "a is at least as likely as b", passed by its own E1 or E2 item -/
  above : List (Word × Word × Item)
  /-- frame premise 1 (E2's three factivity items); `none`: `knows` is not admitted -/
  factive : Option Item
  /-- frame premise 2 (E2's three knows-believes items); `none`: no such premise -/
  knowsBelieves : Option Item
  /-- frame premise 3, per word (E2's per-word items); a word not listed gets no premise 3 of its own -/
  knowsThinks : List (Word × Item)
  deriving DecidableEq, Repr

def Table.words (t : Table) : List Word := t.lowerBound.map (·.1)
def Table.scale (t : Table) : Scale := ⟨t.words, t.above.map (fun p => (p.1, p.2.1))⟩
def Table.hasPair (t : Table) (a b : Word) : Bool := t.above.any (fun p => p.1 == a && p.2.1 == b)

/-- The closure review: the closure of the frozen pairs adds no pair, and no premise-3 word, without its own
    passing item; every entry is between admitted words; premises 2 and 3 need premise 1. -/
def Table.reviewed (t : Table) : Bool :=
  let ws := t.words
  t.candidates.length ≤ 8 &&
  ws.all t.candidates.contains &&
  t.above.all (fun p => ws.contains p.1 && ws.contains p.2.1) &&
  t.knowsThinks.all (fun p => ws.contains p.1) &&
  ws.all (fun a => ws.all (fun b => a == b || !t.scale.atLeast a b || t.hasPair a b)) &&
  t.knowsThinks.all (fun p => ws.all (fun w => !t.scale.atLeast p.1 w || t.knowsThinks.any (·.1 == w))) &&
  (t.factive.isSome || (t.knowsBelieves.isNone && t.knowsThinks.isEmpty))

def e1Words : List Word :=
  ["almost certain", "very likely", "quite likely", "likely", "more likely than not", "as likely as not",
    "unlikely", "very unlikely"]

/-- The frozen table. E1 and E2 have not reported: nothing is admitted yet. AT-0 writes their outcomes here,
    each entry with its item, before PASS. -/
def table : Table :=
  { candidates := e1Words, lowerBound := [], above := [], factive := none, knowsBelieves := none,
    knowsThinks := [] }

/-- The bounds on a document's scale (A5): E1's eight words and 64 pairs, checked by QS-1's `Order.admit`. -/
def scaleCaps : VE.Closure.Caps := ⟨8, 64⟩
```

`#guard table.reviewed` holds (section 7.6).

### 2.2 Modes, conditions, guards, rules, documents

A **mode** is `knows`, `thinks w`, or one of `reports@0`'s four acts. An **attitude condition** names a holder (a
term of the guard), a mode, an optional **slot** (a sort and a term of the guard: the content's variable 0 stands
for that term, de re), and a **content**: a quantifier-free formula over the base vocabulary in context `[s]` (with
a slot of sort `s`) or `[]` (closed). An **attitude guard** is W1's guard formula with attitude conditions as atoms.
An **attitudes document** is W1's document with attitude guards and carve-outs, its holder sorts, the frozen table,
its own scale pairs, its decider, and its English lexical data (SR-3): the English grammar's lexical view of the
environment, its vocabulary overlay and its selected lexicon. Admission, rendering and reading all take that one
lexicon from the document, so they cannot disagree about it.

```lean
/-- `act a` is the act `a` of reports@0; `knows` and `thinks w` are new. -/
inductive Mode where
  | act (a : Act)
  | knows
  | thinks (w : Word)
  deriving DecidableEq, Repr

def Mode.slug : Mode → String
  | .act a => a.name
  | .knows => "knows"
  | .thinks w => "thinks_" ++ w.map (fun c => if c == ' ' then '_' else c)

/-- The mode's English words, for diagnostics. -/
def Mode.words : Mode → String
  | .act a => a.name
  | .knows => "knows"
  | .thinks w => "thinks it " ++ w

/-- One attitude condition. `holder` is a term of the guard. `slot = some (s, t)`: the content's variable 0 has sort
    `s` and stands for the guard's term `t`; `slot = none`: the content is closed. -/
structure Cond where
  holder : VE.Term
  mode : Mode
  slot : Option (String × VE.Term)
  content : VE.Formula
  deriving DecidableEq, Repr

/-- W1's guard formulas with attitude conditions as atoms. -/
inductive AFormula where
  | base (φ : VE.Formula)
  | att (c : Cond)
  | not (a : AFormula)
  | and (a b : AFormula)
  | or (a b : AFormula)
  | implies (a b : AFormula)
  | all (s : String) (a : AFormula)
  | ex (s : String) (a : AFormula)
  deriving DecidableEq, Repr

/-- A W1 rule whose guard and carve-outs may carry attitude conditions. -/
structure ARule where
  name : String
  pred : String
  sign : Bool
  guard : AFormula
  carveOuts : List AFormula
  over : List String
  deriving DecidableEq, Repr

/-- The English grammar's lexical data for one document (SR-3), from its owner `VE.EnglishGrammar`. -/
structure Lex where
  /-- the lexical view of the environment -/
  env : VE.EnglishGrammar.Env
  /-- the vocabulary overlay; `{}` when the case has none -/
  overlay : VE.EnglishGrammar.Overlay
  /-- the selected nouns, wordings, negatives, aliases and spellings -/
  lexicon : VE.EnglishGrammar.Lexicon

structure AttDoc where
  E : VE.Environment
  lits : List String
  /-- the author's declared predicate names, as decoded (the count `MAX_PREDICATES` bounds) -/
  authorPredicates : List String
  regulated : List VE.Norms.Regulated
  definitions : List VE.Norms.Definition
  rules : List ARule
  /-- the holder sorts -/
  holders : List String
  /-- the frozen table; the decoder always sets `table` -/
  T : Table
  /-- the document's own pairs between admitted words -/
  declared : List (Word × Word)
  /-- the decider of every generated open term; "unresolved_decider" when the document names none -/
  decidedBy : String
  /-- the English lexical data; checked by `checkAtt` (D6a, D6b) -/
  lex : Lex

/-- The table's pairs and the document's own. -/
def AttDoc.scale (A : AttDoc) : Scale := ⟨A.T.words, A.T.scale.above ++ A.declared⟩
```

### 2.3 Keys and generated names

A **key** is (mode, holder sort, slot sort, content). Two conditions are one attitude exactly when their keys are
equal: content identity is syntax-tree equality, never a hash (D-A3). Keys are listed once each, in document order
(rules, then guard before carve-outs, pre-order). Each key gets the predicate `attitudes__<mode>__<i>` on its sorts,
`i` the 1-based position among the keys of that mode.

```lean
structure Key where
  mode : Mode
  holderSort : String
  slotSort : Option String
  content : VE.Formula
  deriving DecidableEq, Repr

def Key.sorts (k : Key) : List String := k.holderSort :: k.slotSort.toList

def Cond.key (A : AttDoc) (Γ : List String) (c : Cond) : Option Key :=
  match c.holder.sortOf A.E Γ with
  | some hs => if A.holders.contains hs then some ⟨c.mode, hs, c.slot.map (·.1), c.content⟩ else none
  | none => none

def AFormula.conds : List String → AFormula → List (List String × Cond)
  | _, .base _ => []
  | Γ, .att c => [(Γ, c)]
  | Γ, .not a => a.conds Γ
  | Γ, .and a b => a.conds Γ ++ b.conds Γ
  | Γ, .or a b => a.conds Γ ++ b.conds Γ
  | Γ, .implies a b => a.conds Γ ++ b.conds Γ
  | Γ, .all s a => a.conds (s :: Γ)
  | Γ, .ex s a => a.conds (s :: Γ)

/-- A rule's guard context: its predicate's sorts, the last argument as variable 0. -/
def ruleContext (A : AttDoc) (r : ARule) : List String :=
  match A.regulated.find? (·.name == r.pred) with
  | some d => d.sorts.reverse
  | none => []

def condsOf (A : AttDoc) : List (List String × Cond) :=
  A.rules.flatMap (fun r => (r.guard :: r.carveOuts).flatMap (·.conds (ruleContext A r)))

def keys (A : AttDoc) : List Key := VE.Reports.dedup ((condsOf A).filterMap (fun p => p.2.key A p.1))

/-- `attitudes__<mode>__<i>`, `i` the 1-based position among the keys of that mode. -/
def name (A : AttDoc) (k : Key) : String :=
  "attitudes__" ++ k.mode.slug ++ "__" ++ toString (((keys A).filter (·.mode == k.mode)).idxOf k + 1)

def keyOf (A : AttDoc) (r : String) : Option Key := (keys A).find? (fun k => name A k == r)
```

### 2.4 Environments

`A.E` is the author's whole environment. The **base vocabulary** `baseEnv A` is `E` without the regulated and
defined predicates: the vocabulary `BaseAdmissible` ranges over, and the only one a content may use (A2). `envAtt
A` adds one predicate per key to `E` (the elaborated document's environment); `baseEnvAtt A` adds them to the base
vocabulary (the frame's vocabulary).

```lean
def baseEnv (A : AttDoc) : VE.Environment :=
  VE.Norms.hide A.E (A.regulated.map (·.name) ++ A.definitions.map (·.name))

def envAtt (A : AttDoc) : VE.Environment :=
  { A.E with predicates := fun r =>
      match keyOf A r with
      | some k => some k.sorts
      | none => A.E.predicates r }

def baseEnvAtt (A : AttDoc) : VE.Environment :=
  let B := baseEnv A
  { B with predicates := fun r =>
      match keyOf A r with
      | some k => some k.sorts
      | none => B.predicates r }
```

### 2.5 Elaboration

Each condition becomes `attitudes__<mode>__<i>(holder)` (closed content) or `attitudes__<mode>__<i>(holder, t)`
(slot term `t`); the rule becomes an ordinary `VE.Norms.Node`; the document becomes a W1 document over `envAtt A`.
Regulated predicates, completions, act phrases and definitions are unchanged. (`elab` is a Lean keyword, so the
PLAN's `AFormula.elab` and `ARule.elab` are named `toFormula` and `toNode`; section 11.)

```lean
def atom (A : AttDoc) (k : Key) (h : VE.Term) : Option VE.Term → VE.Formula
  | none => .unary (name A k) h
  | some t => .binary (name A k) h t

def AFormula.toFormula (A : AttDoc) : List String → AFormula → Option VE.Formula
  | _, .base φ => some φ
  | Γ, .att c => (c.key A Γ).map (fun k => atom A k c.holder (c.slot.map (·.2)))
  | Γ, .not a => (a.toFormula A Γ).map .not
  | Γ, .and a b => (a.toFormula A Γ).bind (fun x => (b.toFormula A Γ).map (.and x))
  | Γ, .or a b => (a.toFormula A Γ).bind (fun x => (b.toFormula A Γ).map (.or x))
  | Γ, .implies a b => (a.toFormula A Γ).bind (fun x => (b.toFormula A Γ).map (.implies x))
  | Γ, .all s a => (a.toFormula A (s :: Γ)).map (.all s)
  | Γ, .ex s a => (a.toFormula A (s :: Γ)).map (.ex s)

def ARule.toNode (A : AttDoc) (r : ARule) : Option VE.Norms.Node :=
  (r.guard.toFormula A (ruleContext A r)).bind (fun g =>
    (r.carveOuts.mapM (fun (a : AFormula) => a.toFormula A (ruleContext A r))).map
      (fun cs => ⟨r.name, r.pred, r.sign, g, cs, r.over⟩))

/-- The elaborated W1 document over `envAtt A`. -/
def toNorms (A : AttDoc) : Option VE.Norms.Doc :=
  (A.rules.mapM (fun (r : ARule) => r.toNode A)).map
    (fun ns => ⟨envAtt A, A.lits, ⟨A.regulated, A.definitions, ns⟩⟩)
```

### 2.6 The well-formedness check

`checkAtt` runs the checks in the order of section 5.2 and stops at the first failure; `WellFormedAtt` is its
success. Its last step is W1's own `VE.Norms.validate` on the elaborated document, so nothing W1 checks is checked
twice. `AWellFormed` is the guard-level condition `att_elaboration_faithful` reads.

**Admission is what English can word (SR-2).** `checkAtt` admits only conditions that section 3.1 can word, so every
admitted key has the wording template that `attitudes-elaborate` answers (section 4) and the legend's line
(section 3.3). After D7–D14 have typed the condition and admitted its mode, `renderable` adds three checks, each
with its own diagnostic: a slot's content mentions the slot (D14a: otherwise `knows ⊤` with an unused slot and the
closed `knows ⊤` are two keys with one sentence); a slot term is a variable of the guard (D14b: otherwise `C(var 0)`
slotted at a constant `s1` and the closed `C(s1)` are two keys with one sentence; write the closed content; telling
de re from de dicto about a named constant is a later admission with its own E2 items); a `wants` content is section
3.1's one `wants` wording (D14c). The lexicon those checks and the renderer read is `A.lex`; `checkAtt` validates it
with the English grammar's own `Lexicon.failures` (D6a) and checks that it describes `A.E` (D6b), so
`WellFormedAtt` carries both to every statement that assumes it (SR-3).

```lean
def throwIf (b : Bool) (msg : String) : Except String Unit := if b then .error msg else .ok ()

/-- Whether a quantifier-free content mentions variable 0, the slot. -/
def mentionsSlot : VE.Formula → Bool
  | .unary _ t => t == .var 0
  | .binary _ t u => t == .var 0 || u == .var 0
  | .eq t u => t == .var 0 || u == .var 0
  | .not a => mentionsSlot a
  | .and a b => mentionsSlot a || mentionsSlot b
  | .or a b => mentionsSlot a || mentionsSlot b
  | .implies a b => mentionsSlot a || mentionsSlot b
  | _ => false

/-- The conditions section 3.1 can word, after D7–D14 (SR-2): one definition, whose first failing part is the
    condition's diagnostic. `wantsPhrase?` is reports@0's `wants` test (section 1); the wording it reads is the
    document's selected one. -/
def renderCheck (A : AttDoc) (c : Cond) : Except String Unit := do
  throwIf (match c.slot with | some _ => !mentionsSlot c.content | none => false)
    "InvalidInput: an attitude content does not mention its slot"
  throwIf (match c.slot with | some (_, .const _) => true | _ => false)
    "InvalidInput: an attitude slot term is not a variable of the guard"
  let worded : Bool := match c.mode, c.slot, c.content with
    | .act .wants, some _, .unary p (.var 0) =>
        ((A.lex.lexicon.wordings.lookup p).bind VE.Attribution.Words.wantsPhrase?).isSome
    | .act .wants, _, _ => false
    | _, _, _ => true
  throwIf (!worded) "UnsupportedProfile: this 'wants' content has no reviewed wording in attitudes@0"

def renderable (A : AttDoc) (c : Cond) : Bool := (renderCheck A c).toBool

/-- The lexicon describes the document's environment (SR-3): the same sorts; the author's predicates and no others
    (symbols the lexical view marks generated aside), each with its `A.E` argument sorts; every constant with its
    `A.E` sort. -/
def lexAgrees (A : AttDoc) : Bool :=
  let L := A.lex.env
  let ps := L.predicates.filter (!·.generated)
  L.sorts.all (fun d => d.generated || A.E.sorts.contains d.name) &&
  A.E.sorts.all (fun s => L.sorts.any (·.name == s)) &&
  ps.all (fun d => A.authorPredicates.contains d.name && A.E.predicates d.name == some d.args &&
    d.arity == d.args.length) &&
  A.authorPredicates.all (fun p => ps.any (·.name == p)) &&
  L.constants.all (fun d => d.generated || A.E.constants d.name == some d.sort)

/-- One condition, in its context `Γ`. -/
def checkCond (A : AttDoc) (Γ : List String) (c : Cond) : Except String Unit := do
  let hs ← VE.Norms.termSort A.E Γ c.holder
  throwIf (!A.holders.contains hs) s!"InvalidInput: attitude holder of sort {hs} is not of a holder sort"
  let admitted : Bool := match c.mode with
    | .knows => A.T.factive.isSome
    | .thinks w => A.T.words.contains w
    | .act _ => true
  throwIf (!admitted) s!"UnsupportedProfile: '{c.mode.words}' is not admitted by attitudes@0"
  let ctx ← match c.slot with
    | none => pure []
    | some (s, t) => do
      throwIf (!A.E.sorts.contains s) s!"UnknownSymbol: Unknown slot sort {VE.Norms.pyRepr s}"
      let ts ← VE.Norms.termSort A.E Γ t
      throwIf (ts != s) s!"TypeMismatch: attitude slot term has sort {VE.Norms.pyRepr ts}, not {VE.Norms.pyRepr s}"
      pure [s]
  throwIf (!VE.Norms.Formula.qfree c.content) "InvalidInput: an attitude content has a quantifier"
  VE.Norms.typeDiagnostic (baseEnv A) ctx c.content
  throwIf (!c.content.check (baseEnv A) ctx) "InvalidInput: ill-typed attitude content"
  renderCheck A c

def checkConds (A : AttDoc) : List (List String × Cond) → Except String Unit
  | [] => pure ()
  | (Γ, c) :: rest => do checkCond A Γ c; checkConds A rest

def checkNames (A : AttDoc) : List Key → Except String Unit
  | [] => pure ()
  | k :: rest => do
    let n := name A k
    throwIf ((A.E.predicates n).isSome || (A.regulated.map (·.name) ++ A.definitions.map (·.name)).contains n)
      s!"DuplicateDeclaration: generated predicate {n}"
    throwIf (n.utf8ByteSize > 64) s!"ResourceLimit: generated predicate {n} exceeds 64 bytes"
    checkNames A rest

def checkAtt (A : AttDoc) : Except String Unit := do
  throwIf (!VE.Route.Admission.token A.decidedBy) "InvalidInput: attitudes decided_by is not a token"
  for s in A.holders do
    throwIf (!A.E.sorts.contains s) s!"UnknownSymbol: Unknown holder sort {VE.Norms.pyRepr s}"
  throwIf (!A.T.reviewed) "InvalidInput: the attitude table is not closure-reviewed"
  for p in A.declared do
    throwIf (!(A.T.words.contains p.1 && A.T.words.contains p.2))
      s!"UnsupportedProfile: a declared scale pair names a word that attitudes@0 does not admit"
  match VE.Closure.Order.admit scaleCaps A.scale.toOrder with
  | .error e => throw e
  | .ok () => pure ()
  for p in A.authorPredicates do
    throwIf (p.startsWith "attitudes__") s!"InvalidInput: predicate {p} uses the reserved prefix attitudes__"
  match (VE.EnglishGrammar.Lexicon.failures A.lex.env A.lex.overlay A.lex.lexicon).head? with
  | some (code, kind, n) => throw s!"InvalidInput: the English lexicon fails {code} for {kind} {n}"
  | none => pure ()
  throwIf (!lexAgrees A) "InvalidInput: the English lexicon does not describe the document's environment"
  checkConds A (condsOf A)
  throwIf (A.authorPredicates.length + (keys A).length > VE.Reports.maxPredicates) "ResourceLimit: MAX_PREDICATES"
  checkNames A (keys A)
  throwIf (!decide ((keys A).map (name A)).Nodup) "InvalidInput: generated predicate names collide"
  match toNorms A with
  | none => throw "InvalidInput: an attitude condition has no key"
  | some D => VE.Norms.validate D

def WellFormedAtt (A : AttDoc) : Bool := (checkAtt A).toBool

def AWellFormed (A : AttDoc) : List String → AFormula → Prop
  | Γ, .base φ => φ.WellFormed A.E Γ
  | Γ, .att c => ∃ k, c.key A Γ = some k ∧ k ∈ keys A ∧
      match c.slot with
      | none => True
      | some (s, t) => t.sortOf A.E Γ = some s
  | Γ, .not a => AWellFormed A Γ a
  | Γ, .and a b => AWellFormed A Γ a ∧ AWellFormed A Γ b
  | Γ, .or a b => AWellFormed A Γ a ∧ AWellFormed A Γ b
  | Γ, .implies a b => AWellFormed A Γ a ∧ AWellFormed A Γ b
  | Γ, .all s a => s ∈ A.E.sorts ∧ AWellFormed A (s :: Γ) a
  | Γ, .ex s a => s ∈ A.E.sorts ∧ AWellFormed A (s :: Γ) a
```

### 2.7 The frame

D-A4, read from the table. For keys `k`, `k2` on the same subject (holder sort, slot sort, content):

1. **factive**, for each `knows` key: `∀h ∀x. k(h, x) → content(x)`;
2. `knows → believes`, when `T.knowsBelieves` is set;
3. `knows → thinks w`, when some word `w0` with its own premise-3 item is at or above `w` on the document's scale;
4. `thinks w → thinks w2`, when `w ≠ w2` and `w` is at or above `w2` on the document's scale.

Nothing else is a frame pair: no pair starts at says, believes, wants or intends, and none ends at knows (D-A9;
`framePairs_modes`). Within the frozen table, premise 3 through the closure adds nothing the review has not passed
(`Table.reviewed`). A document's own scale pairs extend the order as the author's stipulation; premise 3 then
reaches through them too, and the legend shows each declared pair (section 3.3).

```lean
def entailsMode (A : AttDoc) : Mode → Mode → Bool
  | .knows, .act .believes => A.T.knowsBelieves.isSome
  | .knows, .thinks w => A.T.knowsThinks.any (fun p => A.scale.atLeast p.1 w)
  | .thinks w, .thinks w2 => w != w2 && A.scale.atLeast w w2
  | _, _ => false

def sameSubject (k k2 : Key) : Bool :=
  k.holderSort == k2.holderSort && k.slotSort == k2.slotSort && k.content == k2.content

def framePairs (A : AttDoc) : List (Key × Key) :=
  (keys A).flatMap (fun k =>
    ((keys A).filter (fun k2 => sameSubject k k2 && entailsMode A k.mode k2.mode)).map (k, ·))

/-- `∀h. body` or `∀h ∀x. body`: the slot is variable 0, the holder variable 1 (or 0 when closed). -/
def closeOver (k : Key) (body : VE.Formula) : VE.Formula :=
  match k.slotSort with
  | none => .all k.holderSort body
  | some s => .all k.holderSort (.all s body)

def atomAt (A : AttDoc) (k : Key) : VE.Formula :=
  match k.slotSort with
  | none => .unary (name A k) (.var 0)
  | some _ => .binary (name A k) (.var 1) (.var 0)

def knowsKeys (A : AttDoc) : List Key := (keys A).filter (·.mode == .knows)

def factive (A : AttDoc) (k : Key) : VE.Formula := closeOver k (.implies (atomAt A k) k.content)

def entails (A : AttDoc) (p : Key × Key) : VE.Formula :=
  closeOver p.1 (.implies (atomAt A p.1) (atomAt A p.2))

def framePremises (A : AttDoc) : List VE.Formula :=
  (knowsKeys A).map (factive A) ++ (framePairs A).map (entails A)

/-- One label per premise, distinct (PK-1 requires distinct labels). -/
def frameLabels (A : AttDoc) : List String :=
  (knowsKeys A).map (fun k => "attitude:factive:" ++ name A k) ++
    (framePairs A).map (fun p => "attitude:entails:" ++ name A p.1 ++ ":" ++ name A p.2)
```

### 2.8 Semantics, independent of the elaboration

An **attitude model** is a structure over `E` with one relation per key. `Intended` says what the attitude words
mean, and nothing more: the relations are typed and range over the document's keys, knowing is factive, and each
frame pair holds. `AFormula.denote` reads attitude guards directly in such a model; `interp` reads the elaborated
document's generated names as the keys' relations; `restrict` reads an `envAtt` structure back. The **frame closure**
of a seed (a finite list of key-tuple pairs) adds, at the same tuple, every key the seed's keys reach through frame
pairs (`VE.Closure.Reachable .star`; `Relation.ReflTransGen` is not in the pinned Lean core, edit 2).

```lean
structure AttModel (A : AttDoc) where
  S : VE.Structure.{u}
  J : Key → List S.Carrier → Prop

/-- A key's content at a tuple: closed content at `[h]`, slot content at `[h, x]` with `x` as variable 0. -/
def contentAt (S : VE.Structure.{u}) (k : Key) : List S.Carrier → Prop
  | [_] => k.slotSort = none ∧ k.content.denote S []
  | [_, x] => k.slotSort.isSome ∧ k.content.denote S [x]
  | _ => False

def Intended (A : AttDoc) (m : AttModel.{u} A) : Prop :=
  (∀ k vs, m.J k vs → k ∈ keys A ∧ VE.TupleTyped m.S k.sorts vs) ∧
  (∀ k ∈ keys A, k.mode = .knows → ∀ vs, m.J k vs → contentAt m.S k vs) ∧
  (∀ p ∈ framePairs A, ∀ vs, m.J p.1 vs → m.J p.2 vs)

def AFormula.denote (A : AttDoc) (m : AttModel.{u} A) : List String → VE.Valuation m.S → AFormula → Prop
  | _, ρ, .base φ => φ.denote m.S ρ
  | Γ, ρ, .att c => ∃ k, c.key A Γ = some k ∧ ∃ vh, c.holder.denote m.S ρ = some vh ∧
      match c.slot with
      | none => m.J k [vh]
      | some (_, t) => ∃ vx, t.denote m.S ρ = some vx ∧ m.J k [vh, vx]
  | Γ, ρ, .not a => ¬ a.denote A m Γ ρ
  | Γ, ρ, .and a b => a.denote A m Γ ρ ∧ b.denote A m Γ ρ
  | Γ, ρ, .or a b => a.denote A m Γ ρ ∨ b.denote A m Γ ρ
  | Γ, ρ, .implies a b => a.denote A m Γ ρ → b.denote A m Γ ρ
  | Γ, ρ, .all s a => ∀ v, m.S.domain s v → a.denote A m (s :: Γ) (v :: ρ)
  | Γ, ρ, .ex s a => ∃ v, m.S.domain s v ∧ a.denote A m (s :: Γ) (v :: ρ)

def interp (A : AttDoc) (m : AttModel.{u} A) : VE.Structure.{u} :=
  { m.S with relation := fun r vs =>
      match keyOf A r with
      | some k => m.J k vs
      | none => m.S.relation r vs }

def restrict (A : AttDoc) (T : VE.Structure.{u}) : AttModel.{u} A :=
  ⟨{ T with relation := fun r vs => keyOf A r = none ∧ T.relation r vs },
    fun k vs => k ∈ keys A ∧ T.relation (name A k) vs⟩

def seedClosure (A : AttDoc) {C : Type u} (seed : List (Key × List C)) (k2 : Key) (vs : List C) : Prop :=
  ∃ k, (k, vs) ∈ seed ∧ VE.Closure.Reachable .star (fun a b => (a, b) ∈ framePairs A) k k2
```

### 2.9 The route views and the `attitudes` pack

```lean
open VE.Norms (Regulated Sat envAt)
open VE.NormDefaults (UDoc SettledAs UndecidedAt FillTables withFill BaseAdmissibleU fill unsaidName)
open VE.NormDefaults.Wire (BaseAdmissibleX UndecidedAtX)

/-- The norm-defaults view of an attitudes document. -/
def toU (A : AttDoc) (unspec : List String) : Option UDoc := (toNorms A).map (fun D => ⟨D, unspec⟩)

/-- SETTLED over the fillings that also satisfy `X` (the counterpart of `UndecidedAtX`). -/
def SettledAsX (U : UDoc) (X : List VE.Formula) (B : VE.Structure.{u}) (r : Regulated) (vs : List B.Carrier)
    (b : Bool) : Prop :=
  ∀ F : FillTables U B, BaseAdmissibleX U X (withFill U B F) →
    ((VE.Norms.outcomeBase (fill U) r.name).denote (withFill U B F) (VE.Norms.tupleVal vs) ↔ b = true)

/-- A premise that reads no `unsaid__` table of `U`. -/
def UnsaidFree (U : UDoc) (φ : VE.Formula) : Prop := ∀ p ∈ U.unspec, unsaidName p ∉ VE.Norms.preds φ

/-- The `attitudes` pack (edit 6). `keyOrigin` and `labelOrigin` give each key's and label's full request
    occurrence: holder term, mode, content, slot, enclosing rule and guard location (A6); AT-3a fixes the paths. -/
def attitudesPack (A : AttDoc) : VE.NormDefaults.Packs.Pack :=
  { id := "attitudes", kind := .vocabulary,
    decls := (keys A).map (fun k => (name A k, k.sorts)),
    labelled := (frameLabels A).zip (framePremises A),
    origins := (keys A).map (fun k => (name A k, keyOrigin A k)) ++
      (frameLabels A).map (fun l => (l, labelOrigin A l)) }

/-- `attitudes@0`'s row in AR-10's table (edit 7). -/
def attitudesRow : VE.Compose.ProfileRow :=
  { profile := "attitudes@0", requires := ["norms@0"],
    refuses := [("reports@0", "UnsupportedProfile: attitudes@0 with reports@0 is not admitted")],
    slot := "norms-chain extra premises" }
```

`attitudes__` is registered in PK-1's `reservedPrefixes`. The pack's position inside X is PK-1's fixed
`packOrder`: after weighing, before scales.

## 3. English, one reading each

AT-5 builds this in the Lean English grammar; until then the structured form (section 4) is what a writer writes.
`H` is the holder's rendering (a rule variable as "that instance of Claude", a constant by its name); `P` is the
content rendered as a clause, with the slot term in place of variable 0 ("that situation is classified as
"mass_casualty_weapon_uplift""); `w` is an admitted word.

### 3.1 Wordings that are admitted

| Mode | Wording (rendered and read) | Reading |
|---|---|---|
| `knows` | "H knows that P" | knows |
| `thinks w` | "H thinks it w that P" | thinks it w or more likely (lower bound, D-A5) |
| `act .believes` | "H believes that P" | `reports@0`'s believes |
| `act .says` | "H says that P" | `reports@0`'s says |
| `act .intends` | "H intends that P" | `reports@0`'s intends, of a content; never intentional action |
| `act .wants` | "H wants Y to VP", only when the content is one unary base predicate on the slot term `Y` whose template is a verb phrase (as `reports@0` words it); any other `wants` content has no reviewed wording | `reports@0`'s wants |
| negation of a whole condition | "it is not the case that …" (VE's external negation) | negation, nothing asserted |
| "P, and X does not know that P" | written "both P and H does not know that P" | `P ∧ ¬knows(P)`; admitted only if its three E2 items reach 36 of 40 (A4) |

"Intends to VP" and "wants Y to VP" with an act phrase are not admitted; intentional action stays residual until a
reviewed act-performance bridge (ET-D2) fits this profile's contract, and act-phrases landing does not admit them
(edit 3). A joined act phrase under `intends` or `believes` is never split or distributed (edit 4).

The structured form admits exactly the conditions this table words (SR-2, section 2.6), so no admitted document holds
a condition without a sentence, and no sentence stands for two admitted conditions: a slot is mentioned by its
content (D14a), a slot term is a variable of the guard (D14b; about a constant, write the closed content, "H knows
that s1 is classified as …"), and `wants` takes only its row's wording (D14c). `H`, `P`, `Y` and the verb phrase are
rendered from the document's own lexicon (`A.lex`), the one `checkAtt` validated (SR-3).

### 3.2 Boundaries: framed connectives and the complement-boundary rule

In a guard written in English, every binary connective is framed, as VE's `relational-fol@0` grammar writes them:
"both A and B", "either A or B, or both", "if A, then B". **Complement-boundary rule** (A4): a content clause after
"knows that", "believes that", "says that", "intends that" or "thinks it w that" ends at the first frame word ("and"
of "both", "or" of "either", ", or both", ", then") whose frame opened outside the clause, or at the end of the
sentence; a content that is itself compound opens its own frame right after "that" ("H knows that both P1 and P2").
So every "and" and "or" closes the innermost open frame, and a sentence has one parse. An adverb written inside a
declared predicate's template (the hand-named "{0} intentionally does the weapons uplift in {1}") is part of that
one predicate, matched whole, and is not the refused attitude adverb of section 3.4; its factor ("what counts as
intentionally doing …") is decided by its decider (section 11, item 15).

### 3.3 The pilot sentence and its legend

u0165.s01 with u0173.s01's condition, as Lean renders it (F4: the intention conjunct is the hand-named open term):

> Every instance of Claude must not do the weapons uplift in each situation if either both that instance of Claude
> knows that that situation is classified as "mass_casualty_weapon_uplift" and that instance of Claude intentionally
> does the weapons uplift in that situation, or that instance of Claude thinks it quite likely that that situation
> is classified as "mass_casualty_weapon_uplift", or both.

The legend, rendered by Lean, one line per frame premise and per open-term record:

> If an instance of Claude knows that a situation is classified as "mass_casualty_weapon_uplift", then that
> situation is classified as "mass_casualty_weapon_uplift".
> If an instance of Claude knows that a situation is classified as "mass_casualty_weapon_uplift", then that instance
> of Claude thinks it quite likely that that situation is classified as "mass_casualty_weapon_uplift".
> "Quite likely" means quite likely or more likely. How likely counts as quite likely is not decided by VE (decided
> by: unresolved decider).
> What counts as intentionally doing the weapons uplift in a situation is not decided by VE (decided by: unresolved
> decider).

A document's own scale pair adds the line "This document says that "very likely" is at least as likely as "quite
likely"." Templates: factive "If H₀ knows that P₀, then P₀."; premise 2 "If H₀ knows that P₀, then H₀ believes that
P₀."; premises 3 and 4 "If H₀ knows that P₀ / thinks it w₁ that P₀, then H₀ thinks it w₂ that P₀.", with `H₀` the
indefinite holder ("an instance of Claude") and `P₀` the content with the indefinite slot ("a situation"), then
"that …" on repetition, as VE renders bound variables today.

### 3.4 Refused forms (rows in english-lean's catalogue, edit 9)

Refusals with mechanical rewrites (`refused_have_rewrites` applies, SR-4, SR-5). Each row records its category and
its candidate readings, written here independently of its rewrites: the form is refused; each rewrite has exactly
one reading; the rewrites' readings are exactly the candidates, in the row's order; the candidates are pairwise
distinct. A guard row is read in its enclosing rule's context `Γ = ruleContext A r`, so "that instance of Claude"
resolves to the rule's variable; a rule row is read as a whole rule, whose context is its own. In the candidates,
`σ` is the slot, `K := att ⟨H, knows, σ, P⟩`, `T w := att ⟨H, thinks w, σ, P⟩`, `B := att ⟨H, act believes, σ, P⟩`,
`P̂ := base (P with the slot term for variable 0)` (`Formula.subst`, `lean/VE/Core/Substitution.lean`; `P` itself
when closed), and `r` is the enclosing rule with guard `g` and carve-outs `cs` (the refused carve-out removed).

| Refused form | Why | Code | Category | Candidate readings | Rewrites |
|---|---|---|---|---|---|
| "H does not know that P" (anywhere but section 3.1's admitted row) | with and without `P` | `NegatedFactive` | guard (`AFormula`) | `and P̂ (not K)`; `not K` | "both P and it is not the case that H knows that P"; "it is not the case that H knows that P" |
| "unless H knows that P" (a carve-out) | its presupposition is unresolved (debate round 3) | `NegatedFactive` | rule (`ARule`): the readings move the condition from a carve-out into the guard, which a guard formula cannot represent | `{ r with guard := and g (not K), carveOuts := cs }`; `{ r with guard := and g (and P̂ (not K)), carveOuts := cs }` | "if it is not the case that H knows that P" (in the guard); "if both P and it is not the case that H knows that P" |
| "H does not think it w that P" | neg-raising: two readings | `NegRaising` | guard (`AFormula`) | `not (T w)`; `att ⟨H, thinks w, σ, not P⟩` | "it is not the case that H thinks it w that P"; "H thinks it w that it is not the case that P" |
| "H thinks that P" | belief or opinion (as `reports@0`) | `BareThinks` | guard (`AFormula`) | `B`; then `T w` for each admitted `w`, in `table`'s order | "H believes that P"; "H thinks it w that P" for each admitted `w` |

Refusals with advice only (the rewrite needs what the sentence lacks; the catalogue row's advice text names it):

| Refused form | Why | Code | Advice |
|---|---|---|---|
| "H knowingly / intentionally / deliberately VPs" | scope of the adverb | `AttitudeAdverb` | "Write the attitude as its own condition about the case it concerns: 'both H knows that <case> and …'. Intentional action has no reviewed wording; name it as an open term." |
| "it thinks …", "they know …" with a pronoun that is not a rule variable | unresolved holder (no pronoun crosses a quote boundary) | `UnresolvedHolder` | "Name the holder: 'that instance of Claude', or a declared constant." |

E2's three "unless" items are evidence for a later admission only, with its own statement review. If E1 admits no
word, `BareThinks` has one rewrite, and the review revisits that row (section 12).

## 4. Wire (structured content; JSON never carries `null`)

```text
environment.attitudes = { "holders": [sort, …], "scale": [[word, word], …], "decided_by": token }
guard node             = { "attitude": { "holder": term, "mode": "knows" | "thinks" | "believes" | "wants"
                           | "intends" | "says", "degree": word (only with "thinks"),
                           "slot": { "sort": sort, "term": term } (optional), "content": formula } }
```

- Terms and formulas are W1's indexed JSON (`VE.Norms.Wire.budgetFormula`), sharing its node budget.
- The block decodes to `holders`, `declared` (the `scale` pairs) and `decidedBy`; `T` is always `table`.
- The English lexical data (SR-3) comes with the case as the English grammar's requests carry it: `lexicon` (the
  export `ve.english-lexicon@1`, naming the environment) and, optionally, `overlay`. `decodeAttDoc` decodes them
  with the grammar's own decoders (`VE.EnglishGrammar.Env.decode`, `Overlay.decode`, `Run.decodeLexicon`, as
  `Run.decodeCase` does) into `lex`, at AT-3a, because `attitudes-elaborate` already answers a wording template per
  key. A case without `lexicon` fails with the decoder's own text.
- `decodeAttDoc` ends with `checkAtt` (SR-7): it returns a document only when every check of section 5.2 passes,
  and otherwise answers the first failing check's diagnostic, which is then the kind's answer
  (`decodeAttDoc_wellFormed`, section 6.3).
- Attitude nodes are admitted in guards and carve-outs only (not in soft exception conditions, not in definitions).
- The layered route's kinds (edit 7): `attitudes-elaborate` answers the generated predicates (name, sorts, key,
  wording template, open-term record), the frame (label, formula), each key's and label's request origin, and the
  elaborated guards; `attitudes-status`, `attitudes-conflict` and `attitudes-report` are the layered route's own
  status, conflict and report kinds over the assembled X.

## 5. Diagnostics, in order

### 5.1 Decoding (AT-3a; texts fixed here, computed when AT-3a exists)

**With `attitudes@0` off, nothing changes (SR-6).** W1's, soft's and P0's entry points, and every route that calls
them, keep today's answers and today's fault order for every input, malformed attitude objects included: a JSON
object with the key `attitude` where a formula is expected answers `array expected` (computed on `main` at
`49de179e`), as today. The new code is not reached on those routes, so no frozen W1, soft or P0 diagnostic changes
(PLAN D-A1). The text `UnsupportedProfile: an attitude condition needs attitudes@0` is answered only at the new,
profile-aware admission boundary, `decodeAttDoc` (the `attitudes-*` kinds of section 4), for a case whose profile
list lacks `attitudes@0`.

With `attitudes@0` on, in this order, as the decoder meets them: fields other than those of section 4: the
decoder's `exactFields` text; an unknown mode: `InvalidInput: unknown attitude mode <m>`; `degree` with a mode other
than `thinks`: `InvalidInput: degree is allowed only with thinks`; `thinks` without `degree`: `InvalidInput: thinks
needs a degree`; then the block: `decided_by` and `holders` as section 5.2, a `scale` entry that is not a pair of
strings: `InvalidInput: a scale entry is a pair of words`; then the lexical data (`lexicon`, `overlay`): the English
grammar decoders' own texts; then `checkAtt`, in section 5.2's order (SR-7).

### 5.2 `checkAtt`, in order (each fixture fails exactly its own check)

Draft 1's rows were computed in the stub. Rows D6a, D6b and D14a–D14c are new in draft 2 (SR-2, SR-3): their texts
are fixed here and their fixtures' answers are *expected*, to be computed when the stub is updated to draft 2. Every
fixture document now carries the fixture lexicon (section 7), and an earlier row's answer is unchanged by it.

| # | Check | Fixture (F-AT1 with one change) | Diagnostic |
|---|---|---|---|
| D1 | `decided_by` is a token | `decidedBy := ""` | `InvalidInput: attitudes decided_by is not a token` |
| D2 | holder sorts declared | `holders := ["robot"]` | `UnknownSymbol: Unknown holder sort 'robot'` |
| D3 | table closure-reviewed | `T := badTableKnows` | `InvalidInput: the attitude table is not closure-reviewed` |
| D4 | declared pairs between admitted words | `declared := [("likely", "quite likely")]` | `UnsupportedProfile: a declared scale pair names a word that attitudes@0 does not admit` |
| D5 | scale caps (QS-1's `Order.admit`) | 64 declared pairs (65 edges) | `ResourceLimit: order edges` |
| D6 | no author predicate uses `attitudes__` | author predicate `attitudes__x` | `InvalidInput: predicate attitudes__x uses the reserved prefix attitudes__` |
| D6a | the English lexicon is valid (`Lexicon.failures` empty; its first failure is named) | the lexicon selects no wording for `mass_casualty_weapon_uplift` | *expected* `InvalidInput: the English lexicon fails V1 for predicate mass_casualty_weapon_uplift` |
| D6b | the lexicon describes `A.E` (`lexAgrees`) | the lexical view declares `mass_casualty_weapon_uplift` on (`claude_instance`) | *expected* `InvalidInput: the English lexicon does not describe the document's environment` |
| D7 | holder term typed | holder `var 5` | `UnboundVariable: Variable index 5 is outside its scope` |
| D8 | holder of a holder sort | holder `var 0` (a situation) | `InvalidInput: attitude holder of sort situation is not of a holder sort` |
| D9 | mode admitted | `thinks "unlikely"` | `UnsupportedProfile: 'thinks it unlikely' is not admitted by attitudes@0` |
| D0 | mode admitted, frozen table | F-AT1 with `T := table` | `UnsupportedProfile: 'knows' is not admitted by attitudes@0` |
| D10 | slot sort declared | slot sort `place` | `UnknownSymbol: Unknown slot sort 'place'` |
| D11 | slot term of the slot's sort | slot `(situation, var 1)` | `TypeMismatch: attitude slot term has sort 'claude_instance', not 'situation'` |
| D12 | content quantifier-free | content `∃ situation. C(var 0)` | `InvalidInput: an attitude content has a quantifier` |
| D13 | content over the base vocabulary | content `weapons_uplift_permitted(var 0, var 0)` | `UnknownSymbol: Unknown predicate 'weapons_uplift_permitted'` |
| D14 | content typed in its context | closed content `C(var 0)` | `UnboundVariable: Variable index 0 is outside its scope` |
| D14a | a slot's content mentions the slot (`renderable`) | the `knows` content `⊤`, slot kept | *expected* `InvalidInput: an attitude content does not mention its slot` |
| D14b | a slot term is a variable of the guard (`renderable`) | the `knows` slot `(situation, s1)`, `s1` a constant of sort `situation` | *expected* `InvalidInput: an attitude slot term is not a variable of the guard` |
| D14c | a `wants` content has section 3.1's wording (`renderable`) | the `intends` condition made `wants`, content `and C(var 0) csam_generation(var 0)` | *expected* `UnsupportedProfile: this 'wants' content has no reviewed wording in attitudes@0` |
| D15 | predicates within `MAX_PREDICATES` | 240 more author predicates | `ResourceLimit: MAX_PREDICATES` (as `reports@0`) |
| D16 | generated names undeclared | `E` declares `attitudes__knows__1` | `DuplicateDeclaration: generated predicate attitudes__knows__1` |
| D17 | generated names at most 64 bytes | a table word of 58 bytes | `ResourceLimit: generated predicate attitudes__thinks_extraordinarily_overwhelmingly_and_almost_certainly_likely__1 exceeds 64 bytes` |
| D18 | W1's check of the elaborated document | a base conjunct `C(var 1)` | `TypeMismatch: Predicate 'mass_casualty_weapon_uplift' expects ('situation',), received ('claude_instance',)` |

The table is in `checkAtt`'s order: D1–D6, D6a, D6b, D7–D9 (D0 is D9's check on the frozen table), D10–D14,
D14a–D14c, D15–D18. Draft 1's numbers are kept, so its fixtures keep their names. The check `generated predicate
names collide` follows D17 and cannot fire with E1's words (no two slugs coincide); it stays as a guard on future
tables.

### 5.3 On the route

A point whose model breaks a frame premise is refused, never evidence, with PK-1's diagnostic naming the first
failing premise's label in X order; with today's `VE.Route.Wire.invalidModel` format that is (computed, RM2):
`InvalidModel(attitude:factive:attitudes__knows__1): the model violates a background premise`; at RM3 the failing
label is `attitude:entails:attitudes__knows__1:attitudes__thinks_quite_likely__1`. Every UNKNOWN stays UNKNOWN.

## 6. Statements

Each is checked in the stub as `def <name> (binders) : Prop := <conclusion>`. Namespaces and opens as in section 2.

### 6.1 AT-1 (`lean/VE/Attitudes/Theorems.lean`)

```lean
theorem names_fresh (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ k ∈ keys A, A.E.predicates (name A k) = none ∧ (name A k).utf8ByteSize ≤ 64 ∧
      name A k ∉ A.regulated.map (·.name) ++ A.definitions.map (·.name)
theorem names_injective (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ k ∈ keys A, ∀ k2 ∈ keys A, name A k = name A k2 → k = k2
theorem keyOf_name (A : AttDoc) (h : WellFormedAtt A = true) : ∀ k ∈ keys A, keyOf A (name A k) = some k
theorem envAtt_extends (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List String) (φ : VE.Formula)
    (hφ : φ.WellFormed A.E Γ) : φ.WellFormed (envAtt A) Γ
theorem toNorms_wellFormed (A : AttDoc) (h : WellFormedAtt A = true) :
    ∃ D, toNorms A = some D ∧ VE.Norms.WellFormed D = true
/-- Typed over the base vocabulary extended by the generated names (A2). -/
theorem frame_wellFormed (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ φ ∈ framePremises A, φ.WellFormed (baseEnvAtt A) []
theorem frame_universalQF (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ φ ∈ framePremises A, VE.NormDefaults.UniversalQF φ
theorem frameLabels_nodup (A : AttDoc) (h : WellFormedAtt A = true) :
    (frameLabels A).length = (framePremises A).length ∧ (frameLabels A).Nodup
/-- D-A9: no frame pair starts at says, believes, wants or intends, and none ends at knows. -/
theorem framePairs_modes (A : AttDoc) :
    ∀ p ∈ framePairs A, (p.1.mode = .knows ∨ ∃ w, p.1.mode = .thinks w) ∧ p.2.mode ≠ .knows
theorem framePairs_transitive (A : AttDoc) (k1 k2 k3 : Key) (h12 : (k1, k2) ∈ framePairs A)
    (h23 : (k2, k3) ∈ framePairs A) (hne : k1 ≠ k3) : (k1, k3) ∈ framePairs A

/-- Faithfulness, guards: the elaborated guard means what the attitude guard means. -/
theorem att_elaboration_faithful (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (Γ : List String) (ρ : VE.Valuation m.S) (a : AFormula) (ha : AWellFormed A Γ a) (φ : VE.Formula)
    (he : a.toFormula A Γ = some φ) : φ.denote (interp A m) ρ ↔ a.denote A m Γ ρ
/-- Faithfulness, the frame: the frame premises hold exactly when the relations mean what `Intended` says. -/
theorem frame_iff_intended (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (hJ : ∀ k vs, m.J k vs → k ∈ keys A ∧ VE.TupleTyped m.S k.sorts vs) :
    VE.Norms.Sat (interp A m) (framePremises A) ↔ Intended A m
/-- Model correspondence, both ways. -/
theorem interp_admissible (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (hS : m.S.Admissible A.E) (hI : Intended A m) : (interp A m).Admissible (envAtt A)
theorem restrict_admissible (A : AttDoc) (h : WellFormedAtt A = true) (T : VE.Structure.{u})
    (hT : T.Admissible (envAtt A)) : (restrict A T).S.Admissible A.E
theorem restrict_intended (A : AttDoc) (h : WellFormedAtt A = true) (T : VE.Structure.{u})
    (hT : T.Admissible (envAtt A)) (hX : VE.Norms.Sat T (framePremises A)) : Intended A (restrict A T)
theorem interp_restrict (A : AttDoc) (h : WellFormedAtt A = true) (T : VE.Structure.{u})
    (hT : T.Admissible (envAtt A)) (r : String) (vs : List T.Carrier) :
    (interp A (restrict A T)).relation r vs ↔ T.relation r vs
theorem old_formula_invariant (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (Γ : List String) (ρ : VE.Valuation m.S) (φ : VE.Formula) (hφ : φ.WellFormed A.E Γ) :
    φ.denote (interp A m) ρ ↔ φ.denote m.S ρ

/-- The expansion step of the `attitudes` pack (PK-1, kind `vocabulary`): empty attitude relations satisfy every
    frame premise, over any structure. -/
theorem empty_relations_frame (A : AttDoc) (S : VE.Structure.{u}) :
    VE.Norms.Sat (interp A ⟨S, fun _ _ => False⟩) (framePremises A)
/-- Conservativity (VISION rule 4). No hypothesis that the frame is empty. -/
theorem att_old_language_conservative (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List VE.Formula)
    (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed A.E []) (hφ : φ.WellFormed A.E []) :
    VE.Entails.{u} (envAtt A) (Γ ++ framePremises A) φ ↔ VE.Entails.{u} A.E Γ φ
/-- A document with no attitude condition: no key, no frame, the same environment. -/
theorem att_conservative_doc (A : AttDoc) (h0 : condsOf A = []) :
    keys A = [] ∧ framePremises A = [] ∧ envAtt A = A.E

/-- Frame premise 1 as a fact of every intended model. -/
theorem knows_factive (A : AttDoc) (m : AttModel.{u} A) (hI : Intended A m) (k : Key) (hk : k ∈ keys A)
    (hm : k.mode = .knows) (vs : List m.S.Carrier) (hJ : m.J k vs) : contentAt m.S k vs
/-- The frame closure of a typed seed whose knowing members have true contents is intended. -/
theorem seed_intended (A : AttDoc) (S : VE.Structure.{u}) (seed : List (Key × List S.Carrier))
    (hseed : ∀ p ∈ seed, p.1 ∈ keys A ∧ VE.TupleTyped S p.1.sorts p.2)
    (hfact : ∀ p ∈ seed, p.1.mode = .knows → contentAt S p.1 p.2) : Intended A ⟨S, seedClosure A seed⟩
/-- Every intended model holding the seed holds its frame closure. -/
theorem seed_least (A : AttDoc) (m : AttModel.{u} A) (hI : Intended A m) (seed : List (Key × List m.S.Carrier))
    (hs : ∀ p ∈ seed, m.J p.1 p.2) : ∀ k vs, seedClosure A seed k vs → m.J k vs
/-- Nothing beyond the frame (F3, edit 2): a seed forces an attitude exactly when frame pairs reach it from a seed
    member at the same tuple. No closure under consequence or conjunction, nothing across holders, contents or
    tuples. -/
theorem forced_iff_reachable (A : AttDoc) (S : VE.Structure.{u}) (seed : List (Key × List S.Carrier))
    (hseed : ∀ p ∈ seed, p.1 ∈ keys A ∧ VE.TupleTyped S p.1.sorts p.2)
    (hfact : ∀ p ∈ seed, p.1.mode = .knows → contentAt S p.1 p.2) (k : Key) (vs : List S.Carrier) :
    (∀ J : Key → List S.Carrier → Prop, Intended A ⟨S, J⟩ → (∀ p ∈ seed, J p.1 p.2) → J k vs) ↔
      seedClosure A seed k vs
/-- The audit's requirement (R 2.2): any attitude other than knowing may be held of a false content; an instance
    of `seed_intended` with the seed `[(k, vs)]`. No hypothesis about the content appears. -/
theorem mistaken_belief_admissible (A : AttDoc) (S : VE.Structure.{u}) (k : Key) (hk : k ∈ keys A)
    (hm : k.mode ≠ .knows) (vs : List S.Carrier) (hvs : VE.TupleTyped S k.sorts vs) :
    ∃ J : Key → List S.Carrier → Prop, Intended A ⟨S, J⟩ ∧ J k vs
/-- R 5's collapse (repaired, A3): when a frame pair links the two keys, `(ck ∧ a) ∨ ct` is `ct`. -/
theorem guard_collapse (A : AttDoc) (m : AttModel.{u} A) (hI : Intended A m) (Γ : List String)
    (ρ : VE.Valuation m.S) (ck ct : Cond) (a : AFormula) (k kt : Key) (hk : ck.key A Γ = some k)
    (hkt : ct.key A Γ = some kt) (hp : (k, kt) ∈ framePairs A) (hh : ck.holder = ct.holder)
    (hsl : ck.slot.map (·.2) = ct.slot.map (·.2)) :
    AFormula.denote A m Γ ρ (.or (.and (.att ck) a) (.att ct)) ↔ AFormula.denote A m Γ ρ (.att ct)
/-- The frozen table passes its closure review. -/
theorem table_reviewed : table.reviewed = true
```

Proof notes. `names_*` and `keyOf_name` from `checkNames` and the `Nodup` check. Conservativity: extend by the empty
relations (`empty_relations_frame`, `old_formula_invariant`); the other direction restricts (`restrict_admissible`,
`interp_restrict`). `frame_iff_intended`: closed contents are typed in `[]` and slot contents in `[s]`, so the
premise's extra binders do not change them, and contents use no generated name (`names_fresh`). `seed_intended`: no
frame pair ends at `knows` (`framePairs_modes`), so factivity is needed of the seed only; reachability is closed
under one more pair; frame pairs relate keys with the same sorts. `seed_least`: induction on `VE.Closure.Path`.
`forced_iff_reachable` is the two together. `guard_collapse` is the third conjunct of `Intended` at `hp`.
`framePairs_transitive` uses QS-1's `atLeast_trans`. `table_reviewed` by `decide`.

### 6.2 AT-2 (`lean/VE/Attitudes/Route.lean`)

```lean
/-- The `attitudes` pack's premises are `framePremises A` (replaces PLAN draft 1's `FrameSource` and
    `frameSource_X`). -/
theorem attitudesPack_premises (A : AttDoc) (h : WellFormedAtt A = true) :
    (attitudesPack A).labelled.map (·.2) = framePremises A ∧ (attitudesPack A).labelled.map (·.1) = frameLabels A
/-- PK-1's typing obligation for this provider (A2). -/
theorem frame_typed_fill (A : AttDoc) (h : WellFormedAtt A = true) (unspec : List String) (U : UDoc)
    (hU : toU A unspec = some U) (hw : VE.NormDefaults.WellFormedU U = true) :
    ∀ φ ∈ framePremises A, φ.WellFormed (envAt (fill U) 0) []
/-- `hw` is needed (SR-1): without it, a base predicate named `unsaid__<p>` used in a `knows` content puts that
    name into a factive premise (fixture F-AT8). -/
theorem frame_unsaidFree (A : AttDoc) (h : WellFormedAtt A = true) (unspec : List String) (U : UDoc)
    (hU : toU A unspec = some U) (hw : VE.NormDefaults.WellFormedU U = true) : ∀ φ ∈ framePremises A, UnsaidFree U φ
theorem settledX_of_settled (U : UDoc) (X : List VE.Formula) (B : VE.Structure.{u}) (r : Regulated)
    (vs : List B.Carrier) (b : Bool) (hs : SettledAs U B r vs b) : SettledAsX U X B r vs b
/-- At a base satisfying an assembled `X` that reads no unsaid table, SETTLED with and without `X` agree. -/
theorem settled_frame_agree (U : UDoc) (X : List VE.Formula) (hfree : ∀ φ ∈ X, UnsaidFree U φ)
    (B : VE.Structure.{u}) (hX : Sat B X) (r : Regulated) (vs : List B.Carrier) (b : Bool) :
    SettledAs U B r vs b ↔ SettledAsX U X B r vs b
theorem undecided_frame_agree (U : UDoc) (X : List VE.Formula) (hfree : ∀ φ ∈ X, UnsaidFree U φ)
    (B : VE.Structure.{u}) (hX : Sat B X) (r : Regulated) (vs : List B.Carrier) :
    UndecidedAt U B r vs ↔ UndecidedAtX U X B r vs
```

`frame_unsaidFree`'s proof note (SR-1): `WellFormedU U` includes norm-defaults' `reservedFree`, which requires
`U.D.E.predicates (unsaidName p) = none` for each `p ∈ U.unspec` (`lean/VE/NormDefaults/Tree.lean:109`). A frame
premise names only generated `attitudes__` names and base predicates of its content, which is typed over `baseEnv A`;
the environment of `toU A unspec` is `envAtt A`, which declares every such base predicate, so none of them is an
`unsaidName p`. `att_conflict_sound` is no new theorem: it is `VE.NormDefaults.Wire.layered_conflict_sound` at
PK-1's assembled X (edit 6). PLAN draft 1's `mistaken_belief_settled` and its placeholder `decidesAt` become fixture
R1 (section 7.3), through the existing `settled_of_table3` and `settledX_of_settled`.

### 6.3 AT-3a (`lean/VE/Attitudes/Wire.lean`; the layered kinds)

```lean
namespace VE.Attitudes.Wire
/-- The decoder ends with `checkAtt` (SR-7): a decoded document is well formed, its lexicon included, so the
    elaborate kind never encodes a document that was not checked. -/
theorem decodeAttDoc_wellFormed (j : Lean.Json) (A : VE.Attitudes.AttDoc) (hd : decodeAttDoc j = .ok A) :
    VE.Attitudes.WellFormedAtt A = true
/-- The answer is exactly the encoding of the elaboration of the case's own decoded document. -/
theorem attitudes_elaborate_acceptance (j : Lean.Json) (A : VE.Attitudes.AttDoc) (hd : decodeAttDoc j = .ok A)
    (L : VE.NormDefaults.Wire.LayeredU) (hL : VE.NormDefaults.Wire.decodeLayered j = .ok L) (id : String) :
    VE.NormDefaults.Wire.layeredCase L id "attitudes-elaborate" j =
      .ok (some (VE.Route.Wire.ok id (encodeElaboration A)))
/-- A replayed status point satisfies the frame; SETTLED and UNDECIDED hold over the assembled X; UNKNOWN claims
    nothing. -/
theorem attitudes_status_sound (j : Lean.Json) (L : VE.NormDefaults.Wire.LayeredU)
    (d : VE.NormDefaults.Wire.StatusX L) (hr : VE.NormDefaults.Wire.replayStatusX L j = .ok d) :
    VE.Norms.Sat d.S.M.asStructure (VE.NormDefaults.Packs.packPremises L "attitudes") ∧
    (∀ b, d.status = .settled b → VE.Attitudes.SettledAsX.{0} L.U L.X d.S.M.asStructure d.r d.vs b) ∧
    (d.status = .undecided → VE.NormDefaults.Wire.UndecidedAtX.{0} L.U L.X d.S.M.asStructure d.r d.vs)
end VE.Attitudes.Wire

namespace VE.Attitudes
/-- The row's composition fact: an admitted list with `attitudes@0` runs on a chain that carries its pack. -/
theorem attitudes_row_composes (ps : List String) (r : String)
    (h : VE.Compose.gateOf VE.Compose.profileTable ps = .ok r) (ha : "attitudes@0" ∈ ps) :
    "norms@0" ∈ ps ∧ ("norm-defaults@0" ∈ ps ∨ "readings@1" ∈ ps) ∧ "reports@0" ∉ ps
end VE.Attitudes
```

`decodeAttDoc_wellFormed` holds by construction, since `decodeAttDoc`'s last step is `checkAtt` (section 4); with
it, `attitudes_elaborate_acceptance` speaks only of checked documents, and a case whose document fails a check of
section 5.2 gets that check's diagnostic as the kind's answer (fixtures in section 7.6).
`attitudes_status_sound` is false on today's `main` for the `table3` and `enumerate` methods (section 10, item 2);
it holds once PK-1 adds the point check. `packPremises` stands for PK-1's accessor of one pack's premises. The
existing `ResponseShape.Encoders.NormDefaults.runCaseReported_fits` keeps its statement; its skeleton gains the new
kinds' rows. No `VE.Service.runMode_attitudes`, no `attitudes.json`, no `MODES` entry (edit 7).

### 6.4 AT-4 (`lean/VE/Attitudes/Readings.lean`)

```lean
namespace VE.Readings
open VE.Rights (correlate)
open VE.Compose (BaseAdmissibleP ConflictFreeP)

/-- One environment's declarations are among another's. -/
def EnvExtends (E E' : VE.Environment) : Prop :=
  (∀ s ∈ E.sorts, s ∈ E'.sorts) ∧ (∀ c s, E.constants c = some s → E'.constants c = some s) ∧
    (∀ p ss, E.predicates p = some ss → E'.predicates p = some ss)

/-- The assembled family with the frame at its `packOrder` place: earlier packs `P`, later packs `R`. -/
def attQ (N : NDoc) (Att : VE.Attitudes.AttDoc) (P R : List VE.Formula) : List VE.Formula :=
  VE.NormDefaults.fillPremises (supU N) ++ (P ++ (VE.Attitudes.framePremises Att ++ R))
def attQ' (N : NDoc) (Att : VE.Attitudes.AttDoc) (P' R' : Choice → List VE.Formula) (c : Choice) :
    List VE.Formula :=
  VE.NormDefaults.fillPremises (choiceU N c) ++ (P' c ++ (VE.Attitudes.framePremises Att ++ R' c))

/-- Frame typing over any environment extending the frame's own vocabulary (A2: proved, not assumed). -/
theorem frame_shared (Att : VE.Attitudes.AttDoc) (hA : VE.Attitudes.WellFormedAtt Att = true)
    (E' : VE.Environment) (hE : EnvExtends (VE.Attitudes.baseEnvAtt Att) E') :
    ∀ φ ∈ VE.Attitudes.framePremises Att, φ.WellFormed E' []
/-- The attitudes pack's provider obligation on the readings route. -/
theorem frame_transfers (N : NDoc) (Att : VE.Attitudes.AttDoc) (hA : VE.Attitudes.WellFormedAtt Att = true)
    (hN : WellFormedND N = true) (hF : WellFormedDoc (fillDoc N) = true) (hs : superposable (fillDoc N) = true)
    (hE : EnvExtends (VE.Attitudes.baseEnvAtt Att) (sharedEnv (fillDoc N))) :
    Transfers.{u} (fillDoc N) (VE.Attitudes.framePremises Att) (fun _ => VE.Attitudes.framePremises Att)
theorem att_nd_superpose_conflict_free (N : NDoc) (Att : VE.Attitudes.AttDoc)
    (hA : VE.Attitudes.WellFormedAtt Att = true) (hN : WellFormedND N = true)
    (hF : WellFormedDoc (fillDoc N) = true) (hs : superposable (fillDoc N) = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true)
    (hE : EnvExtends (VE.Attitudes.baseEnvAtt Att) (sharedEnv (fillDoc N)))
    (P R : List VE.Formula) (P' R' : Choice → List VE.Formula) (hP : Transfers.{u} (fillDoc N) P P')
    (hR : Transfers.{u} (fillDoc N) R R') (A : Choice) (hAc : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome) :
    ConflictFreeP.{u} (correlate (sup (fillDoc N)).1) (slotUnder (fillDoc N) A ++ attQ N Att P R) ↔
      ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) →
        ConflictFreeP.{u} (correlate (choiceDoc (fillDoc N) c).1)
          (VE.Rights.limPremises (choiceDoc (fillDoc N) c).1 ++ attQ' N Att P' R' c)
theorem att_nd_superpose_all (N : NDoc) (Att : VE.Attitudes.AttDoc)
    (hA : VE.Attitudes.WellFormedAtt Att = true) (hN : WellFormedND N = true)
    (hF : WellFormedDoc (fillDoc N) = true) (hs : superposable (fillDoc N) = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true)
    (hE : EnvExtends (VE.Attitudes.baseEnvAtt Att) (sharedEnv (fillDoc N)))
    (P R : List VE.Formula) (P' R' : Choice → List VE.Formula) (hP : Transfers.{u} (fillDoc N) P P')
    (hR : Transfers.{u} (fillDoc N) R R')
    (hQw : VE.Compose.SlotWellFormed (correlate (sup (fillDoc N)).1) (attQ N Att P R))
    (A : Choice) (hAc : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome)
    (hcf : ConflictFreeP.{u} (correlate (sup (fillDoc N)).1) (slotUnder (fillDoc N) A ++ attQ N Att P R))
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv (fillDoc N)) [])
    (hφ : φ.WellFormed (sharedEnv (fillDoc N)) []) (cert : VE.Tableau.Certificate)
    (accepted : supCertificateCheckExtra (fillDoc N) A (attQ N Att P R) Γ φ cert = true)
    (c : Choice) (hc : Compatible (fillDoc N) c) (hAc2 : ∀ x ∈ A, x ∈ c) (B : VE.Structure.{u})
    (hB : BaseAdmissibleP (correlate (choiceDoc (fillDoc N) c).1)
      (VE.Rights.limPremises (choiceDoc (fillDoc N) c).1 ++ attQ' N Att P' R' c) B)
    (hp : VE.Norms.Sat (expand (choiceDoc (fillDoc N) c).1 B) ((choiceDoc (fillDoc N) c).2 ++ Γ)) :
    φ.denote (expand (choiceDoc (fillDoc N) c).1 B) []
theorem att_nd_superpose_countermodel {α : Type u} [DecidableEq α] (N : NDoc) (Att : VE.Attitudes.AttDoc)
    (hA : VE.Attitudes.WellFormedAtt Att = true) (hN : WellFormedND N = true)
    (hF : WellFormedDoc (fillDoc N) = true) (hs : superposable (fillDoc N) = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true)
    (hE : EnvExtends (VE.Attitudes.baseEnvAtt Att) (sharedEnv (fillDoc N)))
    (P R : List VE.Formula) (P' R' : Choice → List VE.Formula) (hP : Transfers.{u} (fillDoc N) P P')
    (hR : Transfers.{u} (fillDoc N) R R') (A : Choice)
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv (fillDoc N)) [])
    (hφ : φ.WellFormed (sharedEnv (fillDoc N)) []) (M : VE.FiniteModel α)
    (valid : M.Valid (VE.Norms.envAt (VE.SoftNorms.soften (correlate (sup (fillDoc N)).1)) 0))
    (hm : supModelCheckExtra (fillDoc N) A (attQ N Att P R) Γ M = true)
    (hn : (VE.SoftNorms.circ (correlate (sup (fillDoc N)).1) φ).eval M [] = false) :
    ∃ c, Compatible (fillDoc N) c ∧ (∀ x ∈ A, x ∈ c) ∧ Encodes (fillDoc N) c M.asStructure ∧
      BaseAdmissibleP (correlate (choiceDoc (fillDoc N) c).1)
        (VE.Rights.limPremises (choiceDoc (fillDoc N) c).1 ++ attQ' N Att P' R' c)
        (pull (fillDoc N) c M.asStructure) ∧
      VE.Norms.Sat (expand (choiceDoc (fillDoc N) c).1 (pull (fillDoc N) c M.asStructure))
        ((choiceDoc (fillDoc N) c).2 ++ Γ) ∧
      ¬ φ.denote (expand (choiceDoc (fillDoc N) c).1 (pull (fillDoc N) c M.asStructure)) []
end VE.Readings
```

`transfers_append` is PK-1's and is not restated (edit 6). The three `att_nd_superpose_*` are
`superpose_*_extra` at `D := fillDoc N` and `Q := attQ N Att P R`, with `Transfers` from `fill_transfers`,
`frame_transfers`, `hP`, `hR` and PK-1's `transfers_append`.

### 6.5 AT-5 (`lean/VE/Attitudes/English.lean`)

```lean
namespace VE.Attitudes
/-- Where a text is read (SR-4): a guard or carve-out, in its enclosing rule's context; or a whole rule, whose
    context is its own. -/
inductive Site where
  | guard (Γ : List String)
  | rule

/-- A catalogue row's candidate readings, written independently of its rewrites, at the row's category (SR-5). -/
inductive Candidates where
  | guards (fs : List AFormula)
  | rules (rs : List ARule)

structure Refusal where
  code : String
  candidates : Candidates
  rewrites : List String

/-- Rendering then reading an admitted attitude condition gives it back, under the document's own lexicon `A.lex`,
    which `WellFormedAtt` validates and ties to `A.E` (D6a, D6b). -/
theorem att_english_roundtrip (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List String) (c : Cond)
    (hc : (Γ, c) ∈ condsOf A) : readCond A Γ (renderCond A Γ c) = .ok c
/-- Rendering is injective on the admitted occurrences of one document, lexicon and context: two admitted conditions
    with one sentence are one condition (one key, holder term and slot term). -/
theorem renderCond_injective (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List String) (c c2 : Cond)
    (hc : (Γ, c) ∈ condsOf A) (hc2 : (Γ, c2) ∈ condsOf A) (he : renderCond A Γ c = renderCond A Γ c2) : c = c2
/-- Each refused form with mechanical rewrites (SR-4, SR-5), at its row's category and in its context: the form is
    refused with the row's code; each rewrite has exactly one reading; the rewrites' readings are exactly the row's
    candidates, in order; the candidates are pairwise distinct. -/
theorem refused_have_rewrites (A : AttDoc) (h : WellFormedAtt A = true) (site : Site) (s : String) (r : Refusal)
    (hr : refusalOf A site s = some r) :
    2 ≤ r.rewrites.length ∧
      match site, r.candidates with
      | .guard Γ, .guards cs =>
          readGuard A Γ s = .error r.code ∧ (∀ s2 ∈ r.rewrites, (readGuardAll A Γ s2).length = 1) ∧
            r.rewrites.flatMap (readGuardAll A Γ) = cs ∧ cs.Nodup
      | .rule, .rules cs =>
          readRule A s = .error r.code ∧ (∀ s2 ∈ r.rewrites, (readRuleAll A s2).length = 1) ∧
            r.rewrites.flatMap (readRuleAll A) = cs ∧ cs.Nodup
      | _, _ => False
end VE.Attitudes
```

`renderCond` and `readCond` (atomic conditions only), `readGuard` and `readGuardAll` (a guard or carve-out, in the
context given), `readRule` and `readRuleAll` (a whole rule) and `refusalOf` (a lookup in english-lean's catalogue,
which instantiates a row's candidates for the text and its site) are AT-5's; each `…All` lists every derivation, as
the all-derivations gate does. All of them read `A.lex` and call the English grammar's lexicon functions and
`wantsPhrase?`; none has a template classifier of its own (SR-3). `renderCond_injective` follows from
`att_english_roundtrip` (apply `readCond A Γ` to `he`). Whole-sentence acceptance (A4): `readRuleAll A s` has length 1
for the section 3.3 sentence and for each of the seven pilot guards rendered as rules.

## 7. Fixtures (draft 1's computed in the stub; draft 2's new ones *expected*)

The fixture environment: sorts `claude_instance`, `situation`; base predicates the seven category atoms on
`situation` (`mass_casualty_weapon_uplift`, `critical_infrastructure_attack_uplift`, `damaging_cyberweapon`,
`undermining_ai_oversight`, `disempowering_humanity`, `illegitimate_power_seizure`, `csam_generation`) and seven
hand-named `intentionally_does_restricted_action_<i>` on (`claude_instance`, `situation`); the regulated permission
`weapons_uplift_permitted (claude_instance, situation)`, act "{0} do the weapons uplift in {1}", default deny (the
placeholder `unspecified` requires it). Holder sort `claude_instance`. Every condition: holder `var 1`, slot
`("situation", var 0)`, content `<category>(var 0)`. `fixtureTable`: words "very likely" and "quite likely", the
pair ("very likely", "quite likely"), premises 1 and 2, premise 3 for both words (all hypothetical).

The **fixture lexicon** (SR-3; new in draft 2): the lexical view of that environment, no overlay, and a lexicon that
selects the pilot's wordings: nouns "instance of Claude" and "situation"; each category atom `{0} is classified as
"<category>"`; each hand-named term its own pilot wording (`{0} intentionally does the weapons uplift in {1}` for
the first, section 3.3; no two alike, as V4 requires); the regulated act's wording. Its letters and spellings are
the grammar's defaults. `Lexicon.valid` holds on it and `lexAgrees` holds (*expected*). Draft 2 adds a constant
`s1 : situation` (spelled "s1") for the D14b fixture and its collision pair only.

### 7.1 Documents

| Fixture | Document | Computed |
|---|---|---|
| F-AT1 | u0165.s01: guard `(knows C ∧ intends C) ∨ thinks quite likely C`; `intends` kept only as a fixture (F4) | check ok; names `attitudes__knows__1`, `attitudes__intends__1`, `attitudes__thinks_quite_likely__1`; 2 frame premises, labels `attitude:factive:attitudes__knows__1`, `attitude:entails:attitudes__knows__1:attitudes__thinks_quite_likely__1`; elaborated guard `or (and knows__1(v1,v0) intends__1(v1,v0)) thinks_quite_likely__1(v1,v0)` |
| F-AT2 | u0165.s01 and u0165.s07, F-AT1's shape on two categories | check ok; six keys `__1` and `__2` per mode; 4 frame premises (factive ×2, knows→thinks ×2), none across contents; from `knows__1`: reaches `thinks_quite_likely__1`, not `thinks_quite_likely__2`, not `knows__2` |
| F-AT3 | "very likely" or "quite likely" on one content, table without the pair, document declares it | with the pair: one premise `thinks_very_likely__1 → thinks_quite_likely__1`; without it: none; `atLeast` (very, quite) true, (quite, very) false |
| F-AT5 | the pilot's shape (F4), seven rules: `(knows C_i ∧ intentionally_does_restricted_action_i(c, s)) ∨ thinks quite likely C_i` | check ok; 14 generated keys + 7 hand-named = 21 open terms; 14 frame premises |
| F-AT6 | knows, very likely, quite likely on one content | 4 premises: factive, knows→very, knows→quite, very→quite (`framePairs_transitive`'s instance) |
| F-AT7 | knows and very likely, table with premise 3 for "quite likely" only | 1 premise (factive); with "very likely"'s own item: 2 (factive, knows→very) |
| F-AT0 | F-AT1 with the attitude conditions removed | check ok; 0 keys; 0 premises; `envAtt` agrees with `E` on every declared name and on three generated-looking names |
| Tables | `table`, `fixtureTable`, `fixtureTableNoPair`, `badTableKnows` (premise 3 for "very likely" only, with the pair), `badTablePair` (adds "likely" and the pair ("quite likely", "likely") but not ("very likely", "likely")) | reviewed: true, true, true, false, false; `badTablePair`'s closure derives ("very likely", "likely") without an item |
| F-AT8 (SR-1) | F-AT1 with a base predicate `unsaid__weapons_uplift_permitted` on `situation` (with a wording) and the `knows` content `unsaid__weapons_uplift_permitted(var 0)`; `unspec := ["weapons_uplift_permitted"]` | *expected*, as the reviewer evaluated draft 1 through Lean: check ok; `toU` gives a document; its factive premise names `unsaid__weapons_uplift_permitted`; `WellFormedU` false. So `frame_unsaidFree` without `hw` is false, and with `hw` it does not apply |
| C-a (SR-2) | two documents: F-AT1 with the `knows` content the closed `⊤` (no slot); and with the content `⊤`, slot kept | *expected*: draft 1 admitted both, as two keys differing only in `slotSort`, with one sentence (section 3's rendering does not show an unused slot); draft 2 admits the first and refuses the second at D14a |
| C-b (SR-2) | two documents: F-AT1 with the `knows` content the closed `mass_casualty_weapon_uplift(s1)`; and with the content `mass_casualty_weapon_uplift(var 0)`, slot `(situation, s1)` | *expected*: draft 1 admitted both (two keys, unrelated relations) with one sentence "… knows that s1 is classified as "mass_casualty_weapon_uplift""; draft 2 admits the first and refuses the second at D14b |
| C-c (SR-2) | F-AT1 with the `intends` condition made `wants`: content `mass_casualty_weapon_uplift(var 0)`; and content `and mass_casualty_weapon_uplift(var 0) csam_generation(var 0)` | *expected*: the first is admitted ("that instance of Claude wants that situation to be classified as …", `wantsPhrase?` of `is classified as …` is `be classified as …`); the second is refused at D14c |

### 7.2 F-AT1's points (one instance `0`, one situation `1`)

| Point | Category | Attitudes | Frame holds | Intended | Guard (attitude semantics) | Guard (elaborated, on `interp`) |
|---|---|---|---|---|---|---|
| M1 | false | thinks | true | true | true | true |
| M2 | false | knows, thinks | false | false | true | true |
| M3 | true | knows | false | false | false | false |
| M4 | true | none | true | true | false | false |

### 7.3 F-AT1 on the layered route (`toU fat1 ["weapons_uplift_permitted"]`, `WellFormedU` true)

| Point | First failing frame label | `table3` | `enumerateSettled` | Two fillings (yes, no): valid, outcome | Status |
|---|---|---|---|---|---|
| RM1 (M1) | none | `some false` | `some false` | valid, valid; false, false | SETTLED no (R1: `settled_of_table3`, then `settledX_of_settled`) |
| RM2 (M2) | `attitude:factive:attitudes__knows__1` | — | — | — | refused (`InvalidModel(…)`, section 5.3) |
| RM3 (M3) | `attitude:entails:attitudes__knows__1:attitudes__thinks_quite_likely__1` | — | — | — | refused |
| RM4 (M4) | none | `none` | `none` | valid, valid; true, false | UNDECIDED (u0173.s04's unknowing contribution) |

The frame reads no unsaid table on `U` and is typed over `envAt (fill U) 0` and `baseEnvAtt` (computed); it holds
on both of RM4's filled situations.

### 7.4 Each iff and "exactly when", both directions

| Claim | Both sides true | Both sides false |
|---|---|---|
| `frame_iff_intended` | M1, M4 | M2, M3 |
| `att_elaboration_faithful` | M1 (guard true both ways) | M4 (false both ways) |
| `guard_collapse` (a = `intends`) | M1; and `knows`+`intends`+`thinks`, category true (intended; both true) | M4 |
| `guard_collapse` (a = hand-named term, F-AT5) | `knows`+`thinks`, term true, category true | no attitude, term true, category true |
| `forced_iff_reachable` | seed `[knows]` forces and reaches `thinks quite likely` | seed `[thinks]` neither forces nor reaches `knows`; seed `[knows]` neither forces nor reaches `intends` |
| `old_formula_invariant` (φ = every situation is C) | category true: M and `interp` both true | category false: both false |
| `att_old_language_conservative` | `[φ] ⊢ φ` on both sides (proved in the stub by `example`) | `[] ⊢ φ`: empty attitude relations satisfy the frame and refute φ (computed), a countermodel to both sides |
| `interp_restrict` | a generated name's tuple in `J` | a generated name's tuple not in `J` (both relations empty) |
| `restrict_intended` (its hypothesis) | RM1 satisfies the frame: restriction intended | RM2 breaks it: restriction not intended |
| `interp_admissible` (its hypothesis) | M1's typed `J`: admissible | an untyped `J` (tuple reversed): not admissible |
| `settled_frame_agree` | RM1, `b = false`: SETTLED with and without X | RM4, either `b`: the two valid fillings disagree, and X holds on both |
| `undecided_frame_agree` | RM4 | RM1 (`enumerateSettled` gives `some false`, so no two admissible fillings disagree) |
| premise 3 exactly where its item passed (D-A4) | F-AT7 with the item | F-AT7 without it |
| premise 4 exactly when the scale orders the words | F-AT3 with the pair | F-AT3 without it; and the reverse direction |
| `Table.reviewed` exactly when the closure adds nothing unreviewed | `fixtureTable`, `table` | `badTableKnows`, `badTablePair` |
| `checkAtt` | F-AT0 to F-AT8, the first document of C-a and of C-b, and the first of C-c pass | D1 to D18, D0, D6a, D6b and D14a–D14c each fail at their own check (draft 2's rows *expected*) |
| `frame_unsaidFree`'s `hw` (SR-1) | F-AT1 with `unspec := ["weapons_uplift_permitted"]`: `WellFormedU` true, the frame unsaid-free | F-AT8: `WellFormedU` false, a factive premise names an unsaid table (*expected*) |
| `renderCond_injective` (SR-2) | the three conditions of F-AT1: three sentences | each collision pair C-a, C-b: one sentence for two keys in draft 1; in draft 2 one of the two is not admitted (*expected*) |

### 7.5 One `#guard` per theorem (A3)

`names_fresh` (F-AT1); `names_injective`, `keyOf_name` (F-AT2); `envAtt_extends` (F-AT1's category atom);
`toNorms_wellFormed` (F-AT1); `frame_wellFormed`, `frame_universalQF`, `frameLabels_nodup` (F-AT2);
`framePairs_modes`, `framePairs_transitive` (F-AT6); `att_elaboration_faithful`, `frame_iff_intended` (F-AT1, M1–M4);
`empty_relations_frame` (F-AT1, F-AT2); `seed_intended`, `mistaken_belief_admissible` (F-AT1, M1); `guard_collapse`
(F-AT1); `table_reviewed`; `settledX_of_settled` (RM1, through `table3 = some false`); `attitudesPack_premises`
(F-AT1); the diagnostics D1–D18 all fail. Every `#guard` of draft 1 holds. Draft 2 adds, to be written and run when
the stub is updated: `frame_unsaidFree` on F-AT1 (with `hw`) and F-AT8 (without it); the diagnostics D6a, D6b and
D14a–D14c; the collision pairs C-a, C-b and the `wants` pair C-c. The statements about wire, route kinds, readings
and English (sections 6.3 to 6.5) have no finite instance before their batches; section 7.6 lists their acceptance
fixtures.

### 7.6 Acceptance fixtures of later batches (not computable before them)

- AT-2: F-AT1's points through the layered status kind with the point check (RM1 SETTLED no, RM4 UNDECIDED, RM2 and
  RM3 refused with the labels above); F-AT1 conflict-free under the assembled X; every existing profile's layered
  output byte-identical.
- AT-3a: F-AT1 as wire cases, each kind, with the fixture lexicon; section 5.1's malformed cases with their texts;
  `attitudes_row_composes`'s lists (`norms@0` with `norm-defaults@0`, `norms@0` with `readings@1`, and a list with
  `reports@0` refused).
- AT-3a, the decoder's last step (SR-7): `attitudes-elaborate` on F-AT1's wire case with one change of section 5.2
  (D1, D6a, D6b, D9, D14a, D14b, D14c, D18) answers that row's diagnostic, not an elaboration; and with the
  `lexicon` field missing, the decoder's own text.
- AT-3a, unchanged contracts (SR-6): on W1's, soft's and P0's routes, with `attitudes@0` off, a guard holding
  `{"attitude": {}}`, `{"attitude": 1}`, a well-formed attitude node, or an attitude node with an extra field
  answers exactly what `main` at AT-3a's base answers (`array expected` at `49de179e`); and fault order is today's:
  a document with an unknown predicate in an earlier rule and an attitude node in a later one answers the unknown
  predicate, and with the two swapped answers `array expected`, as `main` does. Recorded from `main` before the hook
  lands, then compared byte for byte after it.
- AT-3b: fuzz mutants as PLAN AT-3b, including swaps of two keys' holders, request paths and labels.
- AT-4: every existing readings fixture byte-identical; the main translation's eight choices with the frame.
- AT-5: `att_english_roundtrip` on every condition of F-AT1 to F-AT8 and of C-c's admitted document;
  `renderCond_injective` on F-AT2's six conditions in their context; `refused_have_rewrites` on each row of section
  3.4's first table, at its site (the guard rows in F-AT1's rule context, the "unless" row as a whole rule of
  F-AT1), against the row's candidates; `readRuleAll` of the section 3.3 sentence and of the seven pilot guards has
  length 1.

## 8. Limits

No new budget. Generated predicates count against `MAX_PREDICATES` (256, with the author's; D15). A document's
scale: at most 8 words and 64 pairs (`scaleCaps`, D5). A generated name is at most 64 bytes (D17). Formulas share
W1's node budget (10,000) and depth (64). A refused document is refused, never given a verdict. Every UNKNOWN of the
routes stays UNKNOWN. The constitution's main translation would use about 88 predicates (68 − 1 + 14 + 7;
**estimate**).

## 9. Small-scope counterexample search (debate round 3)

Method (stub section S6). Vocabulary: sorts `claude_instance`, `situation`, `user`; base `p_case`, `q_case` on
`situation`; holder sorts `claude_instance` and `user`. A pool of twelve conditions: `knows`, `thinks quite likely`,
`thinks very likely`, `believes`, `intends` of `p_case(x)`; `knows` and `thinks quite likely` of `q_case(x)`; `knows`
of `¬p_case(x)`; closed `knows ⊤` and `thinks quite likely ⊥`; and, under `∃ user`, a user's `knows` and `thinks
quite likely` of `p_case(x)`. Documents: every condition alone, and every pair under `or`, `and` and `not (or …)`:
210 documents, each with at most two keys and two holder sorts. Models: five domain layouts of at most two elements
(sorts may share an element), with every `p_case` and `q_case`; on each, every typed attitude relation. Checked per
document and model: `frame_iff_intended` (T1), `att_elaboration_faithful` at every valuation (T2), `guard_collapse`
with `a` ranging over `p_case(x)`, `⊤` and an `intends` condition (T3), `seed_intended` and `forced_iff_reachable`
for every seed (T4), `mistaken_belief_admissible` (T5), `framePairs_transitive` and `framePairs_modes` (T7),
`empty_relations_frame` and `old_formula_invariant` (T8). As a control, PLAN draft 1's `guard_collapse` (no `hp`, the
thinks condition drawn from the whole pool) is checked the same way.

Result (computed; the stub's final `#guard` asserts it):

| | Count |
|---|---:|
| documents, all well formed, each with at most two keys | 210 |
| document-model pairs | 6,720 |
| collapse instances tried (a frame pair links the two conditions) | 480 |
| seeds tried | 63,188 |
| counterexamples to T1, T2, T3, T4, T5, T7, T8 | 0 each |
| counterexample valuations to PLAN draft 1's `guard_collapse` (the control) | 17,096 |

The control shows the search finds A3's counterexample class, as the debate expected: a `thinks` condition whose key
is not in the document. The search is evidence against small counterexamples only; AT-1's proofs decide.

**The rerun for draft 2 (SR-8; not yet run).** The result above is this spec's draft 1's. Before PASS the search
runs again on the frozen table, with a lexicon for the search vocabulary (valid, and `lexAgrees` holds) and four
more pool members: three that draft 2's new checks refuse, `knows ⊤` with an unused slot (D14a), `knows
p_case(var 0)` slotted at a constant `c0 : situation` (D14b) and `wants` of `p_case(x) ∧ q_case(x)` (D14c); and one
they admit, `wants` of `p_case(x)`. Every document holding a refused member must fail `checkAtt` at that member's
row, and every other document is checked for T1–T8 as above. Each of the twelve earlier members has a closed content,
or a slot term that is a guard variable and a content that mentions it, and none is `wants`, so draft 2 is expected
to admit all 210 earlier documents; the new counts replace the table above.

## 10. Integration points AT-0 pins

1. **Guard-node hook.** One point: `VE.Norms.Wire.decodeNorm`'s guard and carve-out decoding
   (`budgetFormula 64 count` at `lean/VE/Norms/Wire.lean:266–272`). Soft's `ruleFields` calls `decodeNorm` for the
   W1 fields (`lean/VE/SoftNorms/Phases.lean:240–241`) and `VE.Readings.Wire.decodeNorm` calls it too
   (`Readings/Wire.lean:119–124`), so no second guard decoder remains. With `attitudes@0` on, `decodeNorm` reads
   guards and carve-outs as `AFormula` (W1's formula grammar plus the `{"attitude": …}` object, one node budget) and
   returns an `ARule`; the chain's source decoder elaborates the whole document once (`toNorms`), since names depend
   on all keys. With it off, `decodeNorm` and every caller are unchanged and answer `array expected` for the object,
   as today; section 5.1's new text belongs to `decodeAttDoc` only (SR-6). Soft exception conditions
   (`exceptionFields`, `decodeBudgeted`) admit no attitude node. Serialised after act-phrases' AP-1 and AP-3.
2. **The point check.** `VE.NormDefaults.Wire.replayStatusX` does not check X on the point's model for the `table3`
   and `enumerate` methods today: `situationX` checks the model's validity and literals only, and only the
   `undecided` method checks `extraValid` on its two fillings (`Layered.lean:253–263, 341–369`). So PK-1 adds the
   check once, for all packs: every X premise that reads no unsaid table is checked on the point's model before any
   method; the others stay on fillings, as today.
3. **`ve document` dispatch.** On `main` at `49de179e` both `ve/document.py` and Lean's `document` mode
   (`lean/VE/Service/Document.lean`) exist; AT-3b's dispatch edit is first in the document-mode queue after `lf-16g`
   (edit 7).
4. **The English word table's export.** `ve/english_grammar/codes.json` (`tools/english_codes.py`) has the fixed
   format `codes`, `statuses`, `unsentenced` (`CODES_FORMAT`); it does not carry a word table. AT-5 adds a new
   generated entry `attitude-words` in `tools/regen_generated.py` (a hand-written registration).
5. **The readings route.** The decoder's call reduces to the `attitudes` pack provider's registration plus the hook of
   item 1 (edit 7); it lands after `lf-14d`.

## 11. Where this spec differs from the PLAN's Lean text, and why

Each is a statement-level decision for the review; none changes the PLAN's design.

1. `AFormula.elab`, `ARule.elab` are `toFormula`, `toNode`: `elab` is a Lean keyword (elaboration error).
2. `AttDoc` carries `T : Table`, `declared` and `authorPredicates` instead of `scale : Scale`: A1's per-word
   gating needs the table with its items, `MAX_PREDICATES` needs the author's predicate list (as `ReportDoc`), and
   fixtures need a hypothetical table. The decoder always sets `T := table`.
3. `entailsMode` reads `A.T` and `A.scale`; premise 3 for `w` holds when an item-passed word is at or above `w`. In
   the frozen table the closure review makes this the same as the per-word list; a document's declared pair extends
   it as the author's stipulation, shown in the legend. This keeps `framePairs_transitive` true.
4. Labels are distinct per premise (`attitude:factive:<name>`, `attitude:entails:<name>:<name>`): PK-1 refuses
   repeated labels. The PLAN's `attitude:factive`/`attitude:entails` are their prefixes.
5. `contentAt` takes a structure, not a model (the seed theorems have no model yet).
6. `att_elaboration_faithful` drops `hS` and `hρ`, and `frame_iff_intended` drops `hS`: neither is needed, so the
   statements are stronger. `AWellFormed` requires each condition's key to be in `keys A`; without it the statement
   is false for a condition outside the document (A3's lesson).
7. `mistaken_belief_admissible` drops `h` and `hS`; `framePairs_transitive` drops `h`.
8. `guard_collapse` takes any `a` in place of `.att ci` (it covers the hand-named intention term, F4) and compares
   slot terms (`hsl`); `hp` replaces PLAN draft 1's mode and subject hypotheses (A3).
9. `toNorms_isSome` becomes `toNorms_wellFormed`: `WellFormedAtt` ends with W1's `validate`, so the elaborated
   document is W1-well-formed, not only present.
10. New statements: `keyOf_name`, `frameLabels_nodup`, `framePairs_modes` (D-A9), `restrict_intended`,
    `empty_relations_frame` (PK-1's expansion step), `frame_typed_fill` (PK-1's typing), `frame_unsaidFree`,
    `settledX_of_settled`, `attitudesPack_premises`, `frame_shared`, `attitudes_row_composes`; in draft 2,
    `decodeAttDoc_wellFormed` (SR-7) and `renderCond_injective` (SR-2).
11. `settled_frame_agree` and `undecided_frame_agree` are stated for any unsaid-free assembled X, with
    `frame_unsaidFree` for the frame (edit 6 asks for the assembled X; soft's coherence premises can read unsaid
    tables, so the hypothesis is needed).
12. `checkNames` also refuses a generated name equal to a regulated or defined name (else `hide` could hide it).
13. The `MAX_PREDICATES` refusal is `ResourceLimit: MAX_PREDICATES`, `reports@0`'s text, not the PLAN's
    `InvalidInput`.
14. `refused_have_rewrites` adds `2 ≤ r.rewrites.length` (the PLAN's checklist) and applies to section 3.4's first
    table; `AttitudeAdverb` and `UnresolvedHolder` get advice rows, since their rewrites need what the sentence
    lacks. Draft 2 (SR-4, SR-5) states it at the row's category and site, against the row's candidate readings.
15. A declared predicate's template may contain "intentionally" (the hand-named intention term, F4); the
    `AttitudeAdverb` refusal applies to an adverb modifying an act phrase or attitude verb in a guard, not to a
    template matched whole.
16. The section 3.4 rewrites use VE's external negation "it is not the case that …" for negated knowledge. That it
    carries no presupposition for readers is VE's convention (as `reports@0`'s `_NOT`), not measured; the review
    decides whether it needs E2-style items. The statement review (SR-8) made this decision, with the admission of
    section 3.1's last row (asserted-content negated knowledge), part of E2's record: both are written into the
    frozen table's record before PASS.

## 12. Review checklist

| Item (PLAN section 8) | State in this draft |
|---|---|
| `Intended` says what the words mean and nothing more | section 2.8; `forced_iff_reachable`, `framePairs_modes` |
| `mistaken_belief_admissible` has no hypothesis about the content, and is about the given `S` | yes |
| `att_old_language_conservative` has no hypothesis that the frame is empty | yes |
| every frame premise universal with a quantifier-free body | `frame_universalQF`; F-AT2's `#guard` |
| generated names cannot collide with other families | prefix `attitudes__` in PK-1's `reservedPrefixes`; D6, D16 |
| E1's pairs and E2's decisions in `table` with their items, closure review holds | **open**: E1 and E2 have not run; `table` is empty and reviewed. E2's record includes the asserted-content negated knowledge decision (section 11, item 16; SR-8) |
| every key a hypothesis names is in `keys A` (A3) | yes (`hk`, `hp`, `AWellFormed`, `hseed`) |
| one `#guard` per theorem; the search finds no counterexample | draft 1: section 7.5, section 9. **Open** for draft 2: the stub updated and elaborated, the new `#guard`s of section 7.5 and the search rerun with the new pool members (section 9) |
| contents over the base vocabulary; the frame's typing proved on every route (A2) | D13; `frame_wellFormed`, `frame_typed_fill`, `frame_shared` |
| every refused form has two or more one-reading rewrites | section 3.4's first table; advice rows for two forms (section 11, item 14); `BareThinks` needs an admitted word |
| the rewrites are the refused form's readings, at its category and in its context (SR-4, SR-5) | section 3.4's candidate readings; `refused_have_rewrites` with `Site` and `Candidates` |
| every admitted condition has its one sentence, and no sentence two admitted conditions (SR-2) | `renderable` in `checkCond` (D14a–D14c); `att_english_roundtrip` on `(Γ, c) ∈ condsOf A`; `renderCond_injective`; C-a, C-b, C-c |
| admission, rendering and reading share one validated lexicon from its owner (SR-3) | `AttDoc.lex`; D6a (`Lexicon.failures`), D6b (`lexAgrees`); decoded at AT-3a (section 4). **Open, for the re-review**: `wantsPhrase?` moves `reports@0`'s Python `_subject_split`/`_infinitive` into Lean in AT-1; until AT-5 removes the Python copy (reports@0's printer then reads Lean's), the test exists twice. If that interval is not accepted, the Python printer's switch moves into AT-1 |
| a decoded document is a checked document (SR-7) | `decodeAttDoc` ends with `checkAtt`; `decodeAttDoc_wellFormed`; section 7.6's route fixtures |
| W1, soft and P0 answers unchanged with `attitudes@0` off (SR-6) | section 5.1; section 10 item 1; section 7.6's compatibility fixtures |
| `frame_unsaidFree` holds as stated (SR-1) | `hw` added; F-AT8 |
| no forbidden word in a Lean comment; no prime; names under about 57 characters | the longest is `VE.Attitudes.Wire.attitudes_elaborate_acceptance` (48); the stub's stand-ins use `opaque`, which AT-1's files must not |

## 13. Reproducing

From the worktree root, with the `ve-nightly` build at `49de179e`:
`lake --dir /home/seyran/code/ve-nightly/lean env lean lean/SpecStubs_attitudes.lean`. The stub is untracked and
not committed; it holds no `sorry`. Its sections: S0 stand-ins, S1 definitions, S2–S3 statements, S4 evaluators,
S5 fixtures and `#guard`s, S6 the search. The stub is still draft 1's: updating it to draft 2 (section 14's list)
and elaborating it is the next step, and the command above is the one to run then.

## 14. Draft 2: the statement review's corrections

The review of draft 1 (`manage-agents/debates/attitudes-spec/`: `astra.md`, `fable.md`, `result.txt`) converged
after round 3 on **FIX; the build may not start**. Astra's four findings (round 1) and Fable's additions (rounds 1–3)
became one joint position; draft 2 applies it and changes nothing else.

| # | Correction | Where |
|---|---|---|
| SR-1 | `frame_unsaidFree` was false as stated: a base predicate `unsaid__<p>` in a `knows` content, with `p` unspecified, passes `checkAtt` and puts an unsaid name into a factive premise. It gains `hw : WellFormedU U = true`, as `frame_typed_fill` has; the counterexample is a fixture (Astra 1) | 6.2; F-AT8 in 7.1, 7.4 |
| SR-2 | The English round trip's hypothesis `c.key A Γ ≠ none` admitted refused modes and slot collisions. The renderable subset now governs admission: `renderable`, defined once and called by `checkCond` after D14, refuses an unused slot (D14a), a slot term that is not a guard variable (D14b) and a `wants` content without section 3.1's wording (D14c), each with its own text in a fixed order. The round trip takes `(Γ, c) ∈ condsOf A` under `WellFormedAtt A`; `renderCond_injective` is added. De re versus de dicto about a named constant is left to a later admission with its own E2 items (Astra 2, Fable 1) | 2.6; 3.1; 5.2; 6.5; C-a, C-b, C-c in 7.1 |
| SR-3 | `AttDoc` had no lexicon, so the wording check and the renderer read nothing. `AttDoc.lex` carries the English grammar's `Env`, `Overlay` and `Lexicon`; `checkAtt` validates it with `Lexicon.failures` (D6a) and ties it to `A.E` on names and arities (D6b); `decodeAttDoc` decodes it at AT-3a with the grammar's own decoders. D14c and the readers call the grammar's lexicon functions and `reports@0`'s `wants` test (`wantsPhrase?`, moved into Lean by AT-1); no attitude-local template classifier (Astra round 2, Fable round 3) | 1; 2.2; 2.6; 4; 6.5; 7; 12 |
| SR-4 | The rewrites were read as atomic conditions in context `[]`, which cannot hold conjunction, negation or rule syntax, nor resolve a rule's variables. `readCond` reads atomic conditions only; rewrites are read as guards (`AFormula`, in the enclosing rule's context) or as whole rules (`ARule`), by `readGuard`, `readGuardAll`, `readRule`, `readRuleAll` (Astra 3) | 3.4; 6.5 |
| SR-5 | `refused_have_rewrites` did not tie the rewrites to the refused form's readings. Each catalogue row carries its category and its candidate readings, written independently of the rewrites; the theorem says the form is refused, each rewrite has exactly one reading, the rewrites' readings are exactly the candidates, and the candidates are pairwise distinct (Fable 2) | 3.4; 6.5; 7.6 |
| SR-6 | Draft 1 changed W1's frozen answer `array expected` for an attitude object when `attitudes@0` is off. Old entry points keep it; the new text appears only at `decodeAttDoc`. W1, soft and P0 compatibility fixtures cover malformed attitude objects and fault order (Astra 4) | 5.1; 10 item 1; 7.6 |
| SR-7 | `attitudes_elaborate_acceptance` could vouch for unchecked documents. `decodeAttDoc` ends with `checkAtt`; `decodeAttDoc_wellFormed` is added, with route fixtures where a check's failure is the kind's answer (Fable 3) | 4; 5.1; 6.3; 7.6 |
| SR-8 | PASS waits on E1 and E2 recorded in `table` (with the asserted-content negated knowledge decision), the closure review, the stub updated and elaborated, every fixture and the section 9 search rerun on the frozen table with the new refusals in the pool, and a re-review of the changed statements only (both reviewers) | status; 9; 11 item 16; 12 |

Statements changed or added, for the re-review: `frame_unsaidFree`, `decodeAttDoc_wellFormed`,
`att_english_roundtrip`, `renderCond_injective`, `refused_have_rewrites`; definitions changed or added: `Lex`,
`AttDoc.lex`, `mentionsSlot`, `renderCheck`, `renderable`, `lexAgrees`, `checkCond`, `checkAtt`, `Site`,
`Candidates`, `Refusal`; the diagnostics D6a, D6b, D14a–D14c and section 5.1's profile-off rule. Every other statement
is draft 1's, unchanged.
