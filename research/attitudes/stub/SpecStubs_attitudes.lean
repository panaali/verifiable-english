import VE.Attribution.Content
import VE.Norms.Tree
import VE.Norms.SmallModel
import VE.NormDefaults.Evidence
import VE.NormDefaults.Layered
import VE.Closure.Paths
import VE.Readings.SupExtra
import VE.EnglishGrammar.Lexicon

/-! Statement stub for docs/spec/attitudes.md (AT-0): spec draft 4's Lean (draft 3's, which draft 4 keeps) with the
re-review's RR-1 and RR-2 (spec section 17), and E1's and E2's frozen table written into `table`
(docs/research/attitudes-e1e2.md 4.3). Not product code: it is
elaborated with `lake env lean` against `lean/` at this branch's base, and `research/attitudes/experiments.py`
pins it by sha256. Sections: S0 stand-ins for other owners' interfaces (QS-1, AT-1w's `wants` test), S1 AT-1
definitions, S2 AT-1 statements, S3 AT-2 to AT-5 statements, S4 executable evaluators, S5 fixtures, S6
small-scope search. -/

/-! ## S0. QS-1's interface (owner: quantities; reviewed in QT-0). A stand-in with the bodies 2.3 of the
synthesis names, so that attitudes' statements elaborate. Not attitudes' code. -/
namespace VE.Closure

structure Order (α : Type) where
  elems : List α
  edges : List (α × α)

structure Caps where
  elems : Nat
  edges : Nat

def Order.admit {α : Type} [DecidableEq α] (c : Caps) (o : Order α) : Except String Unit :=
  if o.elems.length > c.elems then .error "ResourceLimit: order elements"
  else if o.edges.length > c.edges then .error "ResourceLimit: order edges"
  else if o.edges.all (fun e => o.elems.contains e.1 && o.elems.contains e.2) then .ok ()
  else .error "InvalidInput: an order edge names an element that is not declared"

def Order.atLeast {α : Type} [DecidableEq α] (o : Order α) (a b : α) : Bool := reachEval .star o.edges a b

end VE.Closure

/-! ## S0b. AT-1w's `wants` test (owner: reports@0, moved into Lean by AT-1w). A stand-in with just the behaviour
the fixtures and the search use, so that D14c computes: the infinitive of a unary wording "{0} is …" is "be …";
any other wording has none here. Not attitudes' code. -/
namespace VE.Attribution.Words

def wantsPhrase? (w : String) : Option String :=
  if w.startsWith "{0} is " then some ("be " ++ w.drop 7) else none

end VE.Attribution.Words

/-! ## S1. AT-1 definitions -/
namespace VE.Attitudes
open VE.Reports (Act)
universe u

/-- A likelihood word as written after "thinks it", in lower case: "quite likely". -/
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
  /-- frame premise 3, per word (E2's per-word items); a word not listed gets no premise 3 -/
  knowsThinks : List (Word × Item)
  deriving DecidableEq, Repr

def Table.words (t : Table) : List Word := t.lowerBound.map (·.1)

def Table.scale (t : Table) : Scale := ⟨t.words, t.above.map (fun p => (p.1, p.2.1))⟩

def Table.hasPair (t : Table) (a b : Word) : Bool := t.above.any (fun p => p.1 == a && p.2.1 == b)

/-- The closure review (debate round 3): the closure of the frozen pairs adds no pair, and no premise-3 word,
    without its own passing item; every entry is between admitted words; premises 2 and 3 need premise 1. -/
def Table.reviewed (t : Table) : Bool :=
  let ws := t.words
  t.candidates.length ≤ 8 &&
  ws.all t.candidates.contains &&
  t.above.all (fun p => ws.contains p.1 && ws.contains p.2.1) &&
  t.knowsThinks.all (fun p => ws.contains p.1) &&
  ws.all (fun a => ws.all (fun b => a == b || !t.scale.atLeast a b || t.hasPair a b)) &&
  t.knowsThinks.all (fun p => ws.all (fun w => !t.scale.atLeast p.1 w || t.knowsThinks.any (·.1 == w))) &&
  (t.factive.isSome || (t.knowsBelieves.isNone && t.knowsThinks.isEmpty))

/-- E1's eight words. -/
def e1Words : List Word :=
  ["almost certain", "very likely", "quite likely", "likely", "more likely than not", "as likely as not",
    "unlikely", "very unlikely"]

/-- The frozen table: E1's and E2's outcomes (2026-10-13, docs/research/attitudes-e1e2.md 4.3), each entry with
    the item that passed it, as `experiments.py table` emitted it (`e-table.lean`; the resolution removed no word).
    Five words keep their lower-bound reading; "as likely as not", "unlikely" and "very unlikely" are refused. -/
def table : Table :=
  { candidates := e1Words,
    lowerBound := [("almost certain", "E1.cert.almost-certain"), ("very likely", "E1.cert.very-likely"),
      ("quite likely", "E1.cert.quite-likely"), ("likely", "E1.cert.likely"),
      ("more likely than not", "E1.cert.more-likely-than-not")],
    above := [("almost certain", "very likely", "E1.pair.almost-certain.very-likely"),
      ("almost certain", "quite likely", "E1.pair.almost-certain.quite-likely"),
      ("almost certain", "likely", "E1.pair.almost-certain.likely"),
      ("almost certain", "more likely than not", "E1.pair.almost-certain.more-likely-than-not"),
      ("very likely", "quite likely", "E1.pair.very-likely.quite-likely"),
      ("very likely", "likely", "E1.pair.very-likely.likely"),
      ("very likely", "more likely than not", "E1.pair.very-likely.more-likely-than-not"),
      ("quite likely", "likely", "E1.pair.quite-likely.likely"),
      ("quite likely", "more likely than not", "E1.pair.quite-likely.more-likely-than-not"),
      ("likely", "more likely than not", "E1.pair.likely.more-likely-than-not")],
    factive := some "E2.factive",
    knowsBelieves := some "E2.knows-believes",
    knowsThinks := [("almost certain", "E2.knows-thinks.almost-certain"), ("very likely", "E2.knows-thinks.very-likely"),
      ("quite likely", "E2.knows-thinks.quite-likely"), ("likely", "E2.knows-thinks.likely"),
      ("more likely than not", "E2.knows-thinks.more-likely-than-not")] }

/-- The bounds on a document's scale (debate A5): E1's eight words and 64 pairs. -/
def scaleCaps : VE.Closure.Caps := ⟨8, 64⟩

/-! ### Syntax -/

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

/-- One attitude condition. `holder` is a term of the guard. `slot = some (s, t)`: the content's variable 0 has
    sort `s` and stands for the guard's term `t`; `slot = none`: the content is closed. -/
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

/-- The base vocabulary (debate A2): `E` without the regulated and defined predicates. -/
def baseEnv (A : AttDoc) : VE.Environment :=
  VE.Norms.hide A.E (A.regulated.map (·.name) ++ A.definitions.map (·.name))

/-- What makes two conditions one attitude (D-A3): syntax-tree equality of the content, no hashing. -/
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

/-- `E` plus one predicate per key, on the key's sorts. -/
def envAtt (A : AttDoc) : VE.Environment :=
  { A.E with predicates := fun r =>
      match keyOf A r with
      | some k => some k.sorts
      | none => A.E.predicates r }

/-- The base vocabulary plus the generated predicates: the vocabulary of the frame (debate A2). -/
def baseEnvAtt (A : AttDoc) : VE.Environment :=
  let B := baseEnv A
  { B with predicates := fun r =>
      match keyOf A r with
      | some k => some k.sorts
      | none => B.predicates r }

/-! ### Elaboration -/

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

/-! ### The executable check, with its diagnostics in order -/

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

/-- A predicate a condition names has its lexicon entry (RC-1): the lexical view declares it with `A.E`'s argument
    sorts, and the lexicon selects its wording. -/
def lexPred (A : AttDoc) (p : String) : Bool :=
  (A.lex.env.predicate? p).any (fun d => A.E.predicates p == some d.args && d.arity == d.args.length) &&
    (A.lex.lexicon.wordings.lookup p).isSome

/-- A term a condition names has its lexicon entry (RC-1): a variable needs none; the lexical view declares a
    constant with its `A.E` sort, and the lexicon selects its spelling. -/
def lexTerm (A : AttDoc) : VE.Term → Bool
  | .var _ => true
  | .const c => (A.lex.env.constants.find? (·.name == c)).any (fun d => A.E.constants c == some d.sort) &&
      (A.lex.lexicon.spellings.lookup c).isSome

/-- Every predicate and constant of a content has its lexicon entry (RC-1). -/
def lexCovers (A : AttDoc) : VE.Formula → Bool
  | .top | .bottom => true
  | .unary p t => lexPred A p && lexTerm A t
  | .binary p t u => lexPred A p && lexTerm A t && lexTerm A u
  | .eq t u => lexTerm A t && lexTerm A u
  | .not a | .all _ a | .ex _ a => lexCovers A a
  | .and a b | .or a b | .implies a b => lexCovers A a && lexCovers A b

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
  throwIf (!(lexTerm A c.holder && c.slot.all (fun p => lexTerm A p.2) && lexCovers A c.content))
    "InvalidInput: an attitude condition names a symbol with no entry in the English lexicon"

def renderable (A : AttDoc) (c : Cond) : Bool := (renderCheck A c).toBool

/-- The lexicon describes the document's environment (SR-3): the same sorts; the author's predicates and no others
    (symbols the lexical view marks generated aside), each with its `A.E` argument sorts; every constant with its
    `A.E` sort. It checks the lexicon's symbols against `A.E`; that each symbol a condition names is in the
    lexicon is D14d's check, `lexCovers` (RC-1). -/
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

/-- Section 5.2 of the spec: the document-level checks (the lexicon's D6a and D6b among them), then every condition
    in document order (rules, then guard before carve-outs, pre-order), then the generated names, then W1's own
    check of the elaborated document. -/
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

/-- The guard-level well-formedness `att_elaboration_faithful` reads: base formulas over `E`, each condition's
    key one of the document's, its holder and slot terms typed. -/
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

/-! ### The frame -/

/-- An attitude of mode `m` implies one of mode `m2` on the same subject (D-A4), read from the table: premise 2
    when E2 passed it; premise 3 for `w` when some word with its own E2 item is at or above `w`; premise 4 for
    the pairs of the document's scale. -/
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

/-- Frame premise 1. -/
def factive (A : AttDoc) (k : Key) : VE.Formula := closeOver k (.implies (atomAt A k) k.content)

/-- Frame premises 2 to 4. -/
def entails (A : AttDoc) (p : Key × Key) : VE.Formula :=
  closeOver p.1 (.implies (atomAt A p.1) (atomAt A p.2))

def framePremises (A : AttDoc) : List VE.Formula :=
  (knowsKeys A).map (factive A) ++ (framePairs A).map (entails A)

/-- One label per premise, distinct (PK-1 requires distinct labels). -/
def frameLabels (A : AttDoc) : List String :=
  (knowsKeys A).map (fun k => "attitude:factive:" ++ name A k) ++
    (framePairs A).map (fun p => "attitude:entails:" ++ name A p.1 ++ ":" ++ name A p.2)

/-! ### Semantics, independent of `elab` -/

structure AttModel (A : AttDoc) where
  S : VE.Structure.{u}
  J : Key → List S.Carrier → Prop

/-- A key's content at a tuple: closed content at `[h]`, slot content at `[h, x]` with `x` as variable 0. -/
def contentAt (S : VE.Structure.{u}) (k : Key) : List S.Carrier → Prop
  | [_] => k.slotSort = none ∧ k.content.denote S []
  | [_, x] => k.slotSort.isSome ∧ k.content.denote S [x]
  | _ => False

/-- What the attitude words mean, and nothing more: typed relations, factive knowing, the frame pairs. -/
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

/-- The structure over `envAtt A`: each generated name read as its key's relation. -/
def interp (A : AttDoc) (m : AttModel.{u} A) : VE.Structure.{u} :=
  { m.S with relation := fun r vs =>
      match keyOf A r with
      | some k => m.J k vs
      | none => m.S.relation r vs }

/-- An `envAtt A` structure read back as an attitude model. -/
def restrict (A : AttDoc) (T : VE.Structure.{u}) : AttModel.{u} A :=
  ⟨{ T with relation := fun r vs => keyOf A r = none ∧ T.relation r vs },
    fun k vs => k ∈ keys A ∧ T.relation (name A k) vs⟩

/-- The frame closure of a seed (synthesis edit 2): `(k2, vs)` is in it when some seed member `(k, vs)` reaches
    `k2` through frame pairs, the tuple unchanged. -/
def seedClosure (A : AttDoc) {C : Type u} (seed : List (Key × List C)) (k2 : Key) (vs : List C) : Prop :=
  ∃ k, (k, vs) ∈ seed ∧ VE.Closure.Reachable .star (fun a b => (a, b) ∈ framePairs A) k k2

/-! ## S2. AT-1 statements, each `def <theorem name> (binders) : Prop := <conclusion>` -/

def names_fresh (A : AttDoc) (_h : WellFormedAtt A = true) : Prop :=
  ∀ k ∈ keys A, A.E.predicates (name A k) = none ∧ (name A k).utf8ByteSize ≤ 64 ∧
    name A k ∉ A.regulated.map (·.name) ++ A.definitions.map (·.name)
def names_injective (A : AttDoc) (_h : WellFormedAtt A = true) : Prop :=
  ∀ k ∈ keys A, ∀ k2 ∈ keys A, name A k = name A k2 → k = k2
def keyOf_name (A : AttDoc) (_h : WellFormedAtt A = true) : Prop :=
  ∀ k ∈ keys A, keyOf A (name A k) = some k
def envAtt_extends (A : AttDoc) (_h : WellFormedAtt A = true) (Γ : List String) (φ : VE.Formula)
    (_hφ : φ.WellFormed A.E Γ) : Prop :=
  φ.WellFormed (envAtt A) Γ
def toNorms_wellFormed (A : AttDoc) (_h : WellFormedAtt A = true) : Prop :=
  ∃ D, toNorms A = some D ∧ VE.Norms.WellFormed D = true
def frame_wellFormed (A : AttDoc) (_h : WellFormedAtt A = true) : Prop :=
  ∀ φ ∈ framePremises A, φ.WellFormed (baseEnvAtt A) []
def frame_universalQF (A : AttDoc) (_h : WellFormedAtt A = true) : Prop :=
  ∀ φ ∈ framePremises A, VE.NormDefaults.UniversalQF φ
def frameLabels_nodup (A : AttDoc) (_h : WellFormedAtt A = true) : Prop :=
  (frameLabels A).length = (framePremises A).length ∧ (frameLabels A).Nodup
/-- D-A9: no frame pair starts at says, believes, wants or intends, and none ends at knows. -/
def framePairs_modes (A : AttDoc) : Prop :=
  ∀ p ∈ framePairs A, (p.1.mode = .knows ∨ ∃ w, p.1.mode = .thinks w) ∧ p.2.mode ≠ .knows
def framePairs_transitive (A : AttDoc) (k1 k2 k3 : Key) (_h12 : (k1, k2) ∈ framePairs A)
    (_h23 : (k2, k3) ∈ framePairs A) (_hne : k1 ≠ k3) : Prop :=
  (k1, k3) ∈ framePairs A

/-- Faithfulness, guards: the elaborated guard means what the attitude guard means. -/
def att_elaboration_faithful (A : AttDoc) (_h : WellFormedAtt A = true) (m : AttModel.{u} A) (Γ : List String)
    (ρ : VE.Valuation m.S) (a : AFormula) (_ha : AWellFormed A Γ a) (φ : VE.Formula)
    (_he : a.toFormula A Γ = some φ) : Prop :=
  φ.denote (interp A m) ρ ↔ a.denote A m Γ ρ
/-- Faithfulness, the frame: the frame premises hold exactly when the relations mean what `Intended` says. -/
def frame_iff_intended (A : AttDoc) (_h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (_hJ : ∀ k vs, m.J k vs → k ∈ keys A ∧ VE.TupleTyped m.S k.sorts vs) : Prop :=
  VE.Norms.Sat (interp A m) (framePremises A) ↔ Intended A m
/-- Model correspondence, both ways. -/
def interp_admissible (A : AttDoc) (_h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (_hS : m.S.Admissible A.E) (_hI : Intended A m) : Prop :=
  (interp A m).Admissible (envAtt A)
def restrict_admissible (A : AttDoc) (_h : WellFormedAtt A = true) (T : VE.Structure.{u})
    (_hT : T.Admissible (envAtt A)) : Prop :=
  (restrict A T).S.Admissible A.E
def restrict_intended (A : AttDoc) (_h : WellFormedAtt A = true) (T : VE.Structure.{u})
    (_hT : T.Admissible (envAtt A)) (_hX : VE.Norms.Sat T (framePremises A)) : Prop :=
  Intended A (restrict A T)
def interp_restrict (A : AttDoc) (_h : WellFormedAtt A = true) (T : VE.Structure.{u})
    (_hT : T.Admissible (envAtt A)) (r : String) (vs : List T.Carrier) : Prop :=
  (interp A (restrict A T)).relation r vs ↔ T.relation r vs
def old_formula_invariant (A : AttDoc) (_h : WellFormedAtt A = true) (m : AttModel.{u} A) (Γ : List String)
    (ρ : VE.Valuation m.S) (φ : VE.Formula) (_hφ : φ.WellFormed A.E Γ) : Prop :=
  φ.denote (interp A m) ρ ↔ φ.denote m.S ρ

/-- The expansion step of the `attitudes` pack (PK-1, kind `vocabulary`): empty attitude relations satisfy
    every frame premise, over any structure. -/
def empty_relations_frame (A : AttDoc) (S : VE.Structure.{u}) : Prop :=
  VE.Norms.Sat (interp A ⟨S, fun _ _ => False⟩) (framePremises A)
/-- Conservativity (VISION rule 4). No hypothesis that the frame is empty. -/
def att_old_language_conservative (A : AttDoc) (_h : WellFormedAtt A = true) (Γ : List VE.Formula)
    (φ : VE.Formula) (_hΓ : ∀ a ∈ Γ, a.WellFormed A.E []) (_hφ : φ.WellFormed A.E []) : Prop :=
  VE.Entails.{u} (envAtt A) (Γ ++ framePremises A) φ ↔ VE.Entails.{u} A.E Γ φ
/-- A document with no attitude condition: no key, no frame, the same environment. -/
def att_conservative_doc (A : AttDoc) (_h0 : condsOf A = []) : Prop :=
  keys A = [] ∧ framePremises A = [] ∧ envAtt A = A.E

/-- Frame premise 1 as a fact of every intended model. -/
def knows_factive (A : AttDoc) (m : AttModel.{u} A) (_hI : Intended A m) (k : Key) (_hk : k ∈ keys A)
    (_hm : k.mode = .knows) (vs : List m.S.Carrier) (_hJ : m.J k vs) : Prop :=
  contentAt m.S k vs
/-- The frame closure of a typed seed whose knowing members have true contents is intended. -/
def seed_intended (A : AttDoc) (S : VE.Structure.{u}) (seed : List (Key × List S.Carrier))
    (_hseed : ∀ p ∈ seed, p.1 ∈ keys A ∧ VE.TupleTyped S p.1.sorts p.2)
    (_hfact : ∀ p ∈ seed, p.1.mode = .knows → contentAt S p.1 p.2) : Prop :=
  Intended A ⟨S, seedClosure A seed⟩
/-- Every intended model holding the seed holds its frame closure. -/
def seed_least (A : AttDoc) (m : AttModel.{u} A) (_hI : Intended A m) (seed : List (Key × List m.S.Carrier))
    (_hs : ∀ p ∈ seed, m.J p.1 p.2) : Prop :=
  ∀ k vs, seedClosure A seed k vs → m.J k vs
/-- Nothing beyond the frame (F3, synthesis edit 2): a seed forces an attitude exactly when frame pairs reach it
    from a seed member at the same tuple. No closure under consequence or conjunction, nothing across holders,
    contents or tuples. -/
def forced_iff_reachable (A : AttDoc) (S : VE.Structure.{u}) (seed : List (Key × List S.Carrier))
    (_hseed : ∀ p ∈ seed, p.1 ∈ keys A ∧ VE.TupleTyped S p.1.sorts p.2)
    (_hfact : ∀ p ∈ seed, p.1.mode = .knows → contentAt S p.1 p.2) (k : Key) (vs : List S.Carrier) : Prop :=
  (∀ J : Key → List S.Carrier → Prop, Intended A ⟨S, J⟩ → (∀ p ∈ seed, J p.1 p.2) → J k vs) ↔
    seedClosure A seed k vs
/-- The audit's requirement (R 2.2): any attitude other than knowing may be held of a false content; an instance
    of `seed_intended` with the seed `[(k, vs)]`. No hypothesis about the content appears. -/
def mistaken_belief_admissible (A : AttDoc) (S : VE.Structure.{u}) (k : Key) (_hk : k ∈ keys A)
    (_hm : k.mode ≠ .knows) (vs : List S.Carrier) (_hvs : VE.TupleTyped S k.sorts vs) : Prop :=
  ∃ J : Key → List S.Carrier → Prop, Intended A ⟨S, J⟩ ∧ J k vs
/-- R 5's collapse (repaired, debate A3): when a frame pair links the two keys, `(ck ∧ a) ∨ ct` is `ct`. -/
def guard_collapse (A : AttDoc) (m : AttModel.{u} A) (_hI : Intended A m) (Γ : List String)
    (ρ : VE.Valuation m.S) (ck ct : Cond) (a : AFormula) (k kt : Key) (_hk : ck.key A Γ = some k)
    (_hkt : ct.key A Γ = some kt) (_hp : (k, kt) ∈ framePairs A) (_hh : ck.holder = ct.holder)
    (_hsl : ck.slot.map (·.2) = ct.slot.map (·.2)) : Prop :=
  AFormula.denote A m Γ ρ (.or (.and (.att ck) a) (.att ct)) ↔ AFormula.denote A m Γ ρ (.att ct)
/-- The frozen table passes its closure review. -/
def table_reviewed : Prop := table.reviewed = true

end VE.Attitudes

/-! ## S3a. PK-1's interface (owner: the RD-9 composition owner; its own review). Stand-ins only. -/
namespace VE.NormDefaults.Packs

inductive PackKind
  | vocabulary
  | constraint
  deriving DecidableEq, Repr

abbrev RequestPath := List String

structure Pack where
  id : String
  kind : PackKind
  decls : List (String × List String)
  labelled : List (String × VE.Formula)
  origins : List (String × RequestPath)

def packOrder : List String := ["soft", "rights", "weighing", "attitudes", "scales", "events"]

/-- Stand-in: the premises of the pack `id` in a layered source, as PK-1's `LayeredU.packs` will give them. -/
opaque packPremises : VE.NormDefaults.Wire.LayeredU → String → List VE.Formula

end VE.NormDefaults.Packs

/-! ## S3b. AT-2 (the layered route), with PK-1's attitudes pack -/
namespace VE.Attitudes
open VE.Norms (Regulated Sat envAt)
open VE.NormDefaults (UDoc SettledAs UndecidedAt FillTables withFill BaseAdmissibleU fill unsaidName)
open VE.NormDefaults.Wire (BaseAdmissibleX UndecidedAtX)
universe u

/-- The norm-defaults view of an attitudes document. -/
def toU (A : AttDoc) (unspec : List String) : Option UDoc := (toNorms A).map (fun D => ⟨D, unspec⟩)

/-- SETTLED over the fillings that also satisfy `X` (the counterpart of `UndecidedAtX`). -/
def SettledAsX (U : UDoc) (X : List VE.Formula) (B : VE.Structure.{u}) (r : Regulated) (vs : List B.Carrier)
    (b : Bool) : Prop :=
  ∀ F : FillTables U B, BaseAdmissibleX U X (withFill U B F) →
    ((VE.Norms.outcomeBase (fill U) r.name).denote (withFill U B F) (VE.Norms.tupleVal vs) ↔ b = true)

/-- A premise that reads no `unsaid__` table of `U`. -/
def UnsaidFree (U : UDoc) (φ : VE.Formula) : Prop := ∀ p ∈ U.unspec, unsaidName p ∉ VE.Norms.preds φ

/-- How the pack's origins name request occurrences (AT-3a fixes the paths). -/
opaque keyOrigin : AttDoc → Key → VE.NormDefaults.Packs.RequestPath
opaque labelOrigin : AttDoc → String → VE.NormDefaults.Packs.RequestPath

/-- The `attitudes` pack (synthesis edit 6). -/
def attitudesPack (A : AttDoc) : VE.NormDefaults.Packs.Pack :=
  { id := "attitudes", kind := .vocabulary,
    decls := (keys A).map (fun k => (name A k, k.sorts)),
    labelled := (frameLabels A).zip (framePremises A),
    origins := (keys A).map (fun k => (name A k, keyOrigin A k)) ++
      (frameLabels A).map (fun l => (l, labelOrigin A l)) }

def attitudesPack_premises (A : AttDoc) (_h : WellFormedAtt A = true) : Prop :=
  (attitudesPack A).labelled.map (·.2) = framePremises A ∧ (attitudesPack A).labelled.map (·.1) = frameLabels A
def frame_typed_fill (A : AttDoc) (_h : WellFormedAtt A = true) (unspec : List String) (U : UDoc)
    (_hU : toU A unspec = some U) (_hw : VE.NormDefaults.WellFormedU U = true) : Prop :=
  ∀ φ ∈ framePremises A, φ.WellFormed (envAt (fill U) 0) []
/-- `hw` is needed (SR-1): without it, a base predicate named `unsaid__<p>` used in a `knows` content puts that
    name into a factive premise (fixture F-AT8). -/
def frame_unsaidFree (A : AttDoc) (_h : WellFormedAtt A = true) (unspec : List String) (U : UDoc)
    (_hU : toU A unspec = some U) (_hw : VE.NormDefaults.WellFormedU U = true) : Prop :=
  ∀ φ ∈ framePremises A, UnsaidFree U φ
def settledX_of_settled (U : UDoc) (X : List VE.Formula) (B : VE.Structure.{u}) (r : Regulated)
    (vs : List B.Carrier) (b : Bool) (_hs : SettledAs U B r vs b) : Prop :=
  SettledAsX U X B r vs b
/-- At a base satisfying an assembled `X` that reads no unsaid table, SETTLED with and without `X` agree. -/
def settled_frame_agree (U : UDoc) (X : List VE.Formula) (_hfree : ∀ φ ∈ X, UnsaidFree U φ)
    (B : VE.Structure.{u}) (_hX : Sat B X) (r : Regulated) (vs : List B.Carrier) (b : Bool) : Prop :=
  SettledAs U B r vs b ↔ SettledAsX U X B r vs b
def undecided_frame_agree (U : UDoc) (X : List VE.Formula) (_hfree : ∀ φ ∈ X, UnsaidFree U φ)
    (B : VE.Structure.{u}) (_hX : Sat B X) (r : Regulated) (vs : List B.Carrier) : Prop :=
  UndecidedAt U B r vs ↔ UndecidedAtX U X B r vs

end VE.Attitudes

/-! ## S3c. AT-3a: the guard-node hook and the layered kinds. New functions are stand-ins here. -/
namespace VE.Attitudes.Wire
open Lean

/-- The decoder of an attitudes case: the chain's norm decoder with the guard-node hook, then the
    `environment.attitudes` block. -/
opaque decodeAttDoc : Json → Except String VE.Attitudes.AttDoc
/-- The `attitudes-elaborate` answer's fields. -/
opaque encodeElaboration : VE.Attitudes.AttDoc → List (String × Json)

/-- The decoder ends with `checkAtt` (SR-7): a decoded document is well formed, its lexicon included, so the
    elaborate kind never encodes a document that was not checked. -/
def decodeAttDoc_wellFormed (j : Json) (A : VE.Attitudes.AttDoc) (_hd : decodeAttDoc j = .ok A) : Prop :=
  VE.Attitudes.WellFormedAtt A = true
/-- The answer is exactly the encoding of the elaboration of the case's own decoded document. -/
def attitudes_elaborate_acceptance (j : Json) (A : VE.Attitudes.AttDoc) (_hd : decodeAttDoc j = .ok A)
    (L : VE.NormDefaults.Wire.LayeredU) (_hL : VE.NormDefaults.Wire.decodeLayered j = .ok L) (id : String) : Prop :=
  VE.NormDefaults.Wire.layeredCase L id "attitudes-elaborate" j = .ok (some (VE.Route.Wire.ok id (encodeElaboration A)))
/-- A replayed status point satisfies the frame; SETTLED and UNDECIDED hold over the assembled X; UNKNOWN claims
    nothing. -/
def attitudes_status_sound (j : Json) (L : VE.NormDefaults.Wire.LayeredU) (d : VE.NormDefaults.Wire.StatusX L)
    (_hr : VE.NormDefaults.Wire.replayStatusX L j = .ok d) : Prop :=
  VE.Norms.Sat d.S.M.asStructure (VE.NormDefaults.Packs.packPremises L "attitudes") ∧
  (∀ b, d.status = .settled b → VE.Attitudes.SettledAsX.{0} L.U L.X d.S.M.asStructure d.r d.vs b) ∧
  (d.status = .undecided → VE.NormDefaults.Wire.UndecidedAtX.{0} L.U L.X d.S.M.asStructure d.r d.vs)

end VE.Attitudes.Wire

/-! ## S3d. AR-10's profile-gate table (owner: AR-10). Stand-ins only. -/
namespace VE.Compose
structure ProfileRow where
  profile : String
  requires : List String
  refuses : List (String × String)
  slot : String
opaque profileTable : List ProfileRow
opaque gateOf : List ProfileRow → List String → Except String String
end VE.Compose

namespace VE.Attitudes
/-- `attitudes@0`'s row. -/
def attitudesRow : VE.Compose.ProfileRow :=
  { profile := "attitudes@0", requires := ["norms@0"],
    refuses := [("reports@0", "UnsupportedProfile: attitudes@0 with reports@0 is not admitted")],
    slot := "norms-chain extra premises" }
/-- The row's composition fact: an admitted list with `attitudes@0` runs on a chain that carries its pack. -/
def attitudes_row_composes (ps : List String) (r : String) (_h : VE.Compose.gateOf VE.Compose.profileTable ps = .ok r)
    (_ha : "attitudes@0" ∈ ps) : Prop :=
  "norms@0" ∈ ps ∧ ("norm-defaults@0" ∈ ps ∨ "readings@1" ∈ ps) ∧ "reports@0" ∉ ps
end VE.Attitudes

/-! ## S3e. AT-4: the readings chain (provider obligations; families at PK-1's assembled X) -/
namespace VE.Readings
open VE.Rights (correlate)
open VE.Compose (BaseAdmissibleP ConflictFreeP)
universe u

/-- One environment's declarations are among another's. -/
def EnvExtends (E E' : VE.Environment) : Prop :=
  (∀ s ∈ E.sorts, s ∈ E'.sorts) ∧ (∀ c s, E.constants c = some s → E'.constants c = some s) ∧
    (∀ p ss, E.predicates p = some ss → E'.predicates p = some ss)

/-- Frame typing over any environment extending the frame's own vocabulary (debate A2: proved, not assumed). -/
def frame_shared (Att : VE.Attitudes.AttDoc) (_hA : VE.Attitudes.WellFormedAtt Att = true) (E' : VE.Environment)
    (_hE : EnvExtends (VE.Attitudes.baseEnvAtt Att) E') : Prop :=
  ∀ φ ∈ VE.Attitudes.framePremises Att, φ.WellFormed E' []
/-- The attitudes pack's provider obligation 4 on the readings route. -/
def frame_transfers (N : NDoc) (Att : VE.Attitudes.AttDoc) (_hA : VE.Attitudes.WellFormedAtt Att = true)
    (_hN : WellFormedND N = true) (_hF : WellFormedDoc (fillDoc N) = true) (_hs : superposable (fillDoc N) = true)
    (_hE : EnvExtends (VE.Attitudes.baseEnvAtt Att) (sharedEnv (fillDoc N))) : Prop :=
  Transfers.{u} (fillDoc N) (VE.Attitudes.framePremises Att) (fun _ => VE.Attitudes.framePremises Att)

/-- The assembled family with the frame at its `packOrder` place: earlier packs `P`, later packs `R`. -/
def attQ (N : NDoc) (Att : VE.Attitudes.AttDoc) (P R : List VE.Formula) : List VE.Formula :=
  VE.NormDefaults.fillPremises (supU N) ++ (P ++ (VE.Attitudes.framePremises Att ++ R))
def attQ' (N : NDoc) (Att : VE.Attitudes.AttDoc) (P' R' : Choice → List VE.Formula) (c : Choice) :
    List VE.Formula :=
  VE.NormDefaults.fillPremises (choiceU N c) ++ (P' c ++ (VE.Attitudes.framePremises Att ++ R' c))

def att_nd_superpose_conflict_free (N : NDoc) (Att : VE.Attitudes.AttDoc)
    (_hA : VE.Attitudes.WellFormedAtt Att = true) (_hN : WellFormedND N = true)
    (_hF : WellFormedDoc (fillDoc N) = true) (_hs : superposable (fillDoc N) = true)
    (_hsu : VE.NormDefaults.WellFormedU (supU N) = true)
    (_hE : EnvExtends (VE.Attitudes.baseEnvAtt Att) (sharedEnv (fillDoc N)))
    (P R : List VE.Formula) (P' R' : Choice → List VE.Formula) (_hP : Transfers.{u} (fillDoc N) P P')
    (_hR : Transfers.{u} (fillDoc N) R R') (A : Choice) (_hAc : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome) : Prop :=
  ConflictFreeP.{u} (correlate (sup (fillDoc N)).1) (slotUnder (fillDoc N) A ++ attQ N Att P R) ↔
    ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) →
      ConflictFreeP.{u} (correlate (choiceDoc (fillDoc N) c).1)
        (VE.Rights.limPremises (choiceDoc (fillDoc N) c).1 ++ attQ' N Att P' R' c)
def att_nd_superpose_all (N : NDoc) (Att : VE.Attitudes.AttDoc)
    (_hA : VE.Attitudes.WellFormedAtt Att = true) (_hN : WellFormedND N = true)
    (_hF : WellFormedDoc (fillDoc N) = true) (_hs : superposable (fillDoc N) = true)
    (_hsu : VE.NormDefaults.WellFormedU (supU N) = true)
    (_hE : EnvExtends (VE.Attitudes.baseEnvAtt Att) (sharedEnv (fillDoc N)))
    (P R : List VE.Formula) (P' R' : Choice → List VE.Formula) (_hP : Transfers.{u} (fillDoc N) P P')
    (_hR : Transfers.{u} (fillDoc N) R R') (_hQw : VE.Compose.SlotWellFormed (correlate (sup (fillDoc N)).1) (attQ N Att P R))
    (A : Choice) (_hAc : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome)
    (_hcf : ConflictFreeP.{u} (correlate (sup (fillDoc N)).1) (slotUnder (fillDoc N) A ++ attQ N Att P R))
    (Γ : List VE.Formula) (φ : VE.Formula) (_hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv (fillDoc N)) [])
    (_hφ : φ.WellFormed (sharedEnv (fillDoc N)) []) (cert : VE.Tableau.Certificate)
    (_accepted : supCertificateCheckExtra (fillDoc N) A (attQ N Att P R) Γ φ cert = true)
    (c : Choice) (_hc : Compatible (fillDoc N) c) (_hAc2 : ∀ x ∈ A, x ∈ c) (B : VE.Structure.{u})
    (_hB : BaseAdmissibleP (correlate (choiceDoc (fillDoc N) c).1)
      (VE.Rights.limPremises (choiceDoc (fillDoc N) c).1 ++ attQ' N Att P' R' c) B)
    (_hp : VE.Norms.Sat (expand (choiceDoc (fillDoc N) c).1 B) ((choiceDoc (fillDoc N) c).2 ++ Γ)) : Prop :=
  φ.denote (expand (choiceDoc (fillDoc N) c).1 B) []
def att_nd_superpose_countermodel {α : Type u} [DecidableEq α] (N : NDoc) (Att : VE.Attitudes.AttDoc)
    (_hA : VE.Attitudes.WellFormedAtt Att = true) (_hN : WellFormedND N = true)
    (_hF : WellFormedDoc (fillDoc N) = true) (_hs : superposable (fillDoc N) = true)
    (_hsu : VE.NormDefaults.WellFormedU (supU N) = true)
    (_hE : EnvExtends (VE.Attitudes.baseEnvAtt Att) (sharedEnv (fillDoc N)))
    (P R : List VE.Formula) (P' R' : Choice → List VE.Formula) (_hP : Transfers.{u} (fillDoc N) P P')
    (_hR : Transfers.{u} (fillDoc N) R R') (A : Choice)
    (Γ : List VE.Formula) (φ : VE.Formula) (_hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv (fillDoc N)) [])
    (_hφ : φ.WellFormed (sharedEnv (fillDoc N)) []) (M : VE.FiniteModel α)
    (_valid : M.Valid (VE.Norms.envAt (VE.SoftNorms.soften (correlate (sup (fillDoc N)).1)) 0))
    (_hm : supModelCheckExtra (fillDoc N) A (attQ N Att P R) Γ M = true)
    (_hn : (VE.SoftNorms.circ (correlate (sup (fillDoc N)).1) φ).eval M [] = false) : Prop :=
  ∃ c, Compatible (fillDoc N) c ∧ (∀ x ∈ A, x ∈ c) ∧ Encodes (fillDoc N) c M.asStructure ∧
    BaseAdmissibleP (correlate (choiceDoc (fillDoc N) c).1)
      (VE.Rights.limPremises (choiceDoc (fillDoc N) c).1 ++ attQ' N Att P' R' c) (pull (fillDoc N) c M.asStructure) ∧
    VE.Norms.Sat (expand (choiceDoc (fillDoc N) c).1 (pull (fillDoc N) c M.asStructure))
      ((choiceDoc (fillDoc N) c).2 ++ Γ) ∧
    ¬ φ.denote (expand (choiceDoc (fillDoc N) c).1 (pull (fillDoc N) c M.asStructure)) []

end VE.Readings

/-! ## S3f. AT-5: English (new functions are stand-ins here; refusal rows live in english-lean's catalogue) -/
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

opaque renderCond : AttDoc → List String → Cond → String
opaque readCond : AttDoc → List String → String → Except String Cond
opaque readGuard : AttDoc → List String → String → Except String AFormula
opaque readGuardAll : AttDoc → List String → String → List AFormula
opaque readRule : AttDoc → String → Except String ARule
opaque readRuleAll : AttDoc → String → List ARule
opaque refusalOf : AttDoc → Site → String → Option Refusal
/-- Section 3.1's admitted row "both P and H does not know that P", rendered for the `knows` condition `c`. -/
opaque renderAssertedNotKnows : AttDoc → List String → Cond → String

/-- `P̂` (section 3.4): the content with the slot term for variable 0; the content itself when closed. A content is
    quantifier-free (D12), so variable 0 is replaced directly (`Formula.subst` of `lean/VE/Core/Substitution.lean`
    is over `VE.Core.Formula`, not `VE.Formula`). -/
def slotTermIn (t : VE.Term) : VE.Term → VE.Term
  | .var 0 => t
  | u => u
def slotIn (t : VE.Term) : VE.Formula → VE.Formula
  | .unary p u => .unary p (slotTermIn t u)
  | .binary p u v => .binary p (slotTermIn t u) (slotTermIn t v)
  | .eq u v => .eq (slotTermIn t u) (slotTermIn t v)
  | .not a => .not (slotIn t a)
  | .and a b => .and (slotIn t a) (slotIn t b)
  | .or a b => .or (slotIn t a) (slotIn t b)
  | .implies a b => .implies (slotIn t a) (slotIn t b)
  | φ => φ
def assertedOf (c : Cond) : VE.Formula :=
  match c.slot with
  | none => c.content
  | some (_, t) => slotIn t c.content
/-- The one reading of section 3.1's admitted row (E2, six items), read whole (RR-1): `and P̂ (not K)`. It is not a
    composition of `NegatedFactive`'s candidates under "both P and …", which would give two trees,
    `and P̂ (and P̂ (not K))` and `and P̂ (not K)`: equivalent, but two derivations. -/
def assertedNotKnows (c : Cond) : AFormula := .and (.base (assertedOf c)) (.not (.att c))

/-- Rendering then reading an admitted attitude condition gives it back, under the document's own lexicon `A.lex`,
    which `WellFormedAtt` validates and ties to `A.E` (D6a, D6b), with an entry for every symbol the condition
    names (D14d). -/
def att_english_roundtrip (A : AttDoc) (_h : WellFormedAtt A = true) (Γ : List String) (c : Cond)
    (_hc : (Γ, c) ∈ condsOf A) : Prop :=
  readCond A Γ (renderCond A Γ c) = .ok c
/-- Rendering is injective on the admitted occurrences of one document, lexicon and context: two admitted conditions
    with one sentence are one condition (one key, holder term and slot term). -/
def renderCond_injective (A : AttDoc) (_h : WellFormedAtt A = true) (Γ : List String) (c c2 : Cond)
    (_hc : (Γ, c) ∈ condsOf A) (_hc2 : (Γ, c2) ∈ condsOf A) (_he : renderCond A Γ c = renderCond A Γ c2) : Prop :=
  c = c2
/-- Each refused form with mechanical rewrites (SR-4, SR-5), at its row's category and in its context: the form is
    refused with the row's code; each rewrite has exactly one reading; the rewrites' readings are exactly the row's
    candidates, in order; the candidates are pairwise distinct. -/
def refused_have_rewrites (A : AttDoc) (_h : WellFormedAtt A = true) (site : Site) (s : String) (r : Refusal)
    (_hr : refusalOf A site s = some r) : Prop :=
  2 ≤ r.rewrites.length ∧
    match site, r.candidates with
    | .guard Γ, .guards cs =>
        readGuard A Γ s = .error r.code ∧ (∀ s2 ∈ r.rewrites, (readGuardAll A Γ s2).length = 1) ∧
          r.rewrites.flatMap (readGuardAll A Γ) = cs ∧ cs.Nodup
    | .rule, .rules cs =>
        readRule A s = .error r.code ∧ (∀ s2 ∈ r.rewrites, (readRuleAll A s2).length = 1) ∧
          r.rewrites.flatMap (readRuleAll A) = cs ∧ cs.Nodup
    | _, _ => False
/-- Section 3.1's admitted row has exactly one reading, its own (RR-1): for each admitted `knows` occurrence, the
    row's text in that context is admitted and its every derivation is `assertedNotKnows c`. -/
def assertedNotKnows_one_reading (A : AttDoc) (_h : WellFormedAtt A = true) (Γ : List String) (c : Cond)
    (_hc : (Γ, c) ∈ condsOf A) (_hk : c.mode = .knows) : Prop :=
  readGuard A Γ (renderAssertedNotKnows A Γ c) = .ok (assertedNotKnows c) ∧
    readGuardAll A Γ (renderAssertedNotKnows A Γ c) = [assertedNotKnows c]

end VE.Attitudes

/-! ## S4. Executable evaluators over finite attitude models (stub only: the search's oracle) -/
namespace VE.Attitudes.Check
open VE.Attitudes

abbrev FM := VE.FiniteModel Nat
abbrev Rel := List (Key × List Nat)

def typedB (M : FM) : List String → List Nat → Bool
  | [], [] => true
  | s :: ss, v :: vs => (M.domains s).contains v && typedB M ss vs
  | _, _ => false

def contentB (M : FM) (k : Key) : List Nat → Bool
  | [_] => k.slotSort.isNone && k.content.eval M []
  | [_, x] => k.slotSort.isSome && k.content.eval M [x]
  | _ => false

/-- `Intended`, executable. -/
def intendedB (A : AttDoc) (M : FM) (J : Rel) : Bool :=
  J.all (fun p => (keys A).contains p.1 && typedB M p.1.sorts p.2) &&
  J.all (fun p => p.1.mode != .knows || contentB M p.1 p.2) &&
  (framePairs A).all (fun q => J.all (fun p => p.1 != q.1 || J.contains (q.2, p.2)))

/-- `interp`, as a finite model over `envAtt A`. -/
def interpM (A : AttDoc) (M : FM) (J : Rel) : FM :=
  { M with relations := fun r => match keyOf A r with
      | some k => (J.filter (·.1 == k)).map (·.2)
      | none => M.relations r }

def frameB (A : AttDoc) (M : FM) (J : Rel) : Bool := (framePremises A).all (fun φ => φ.eval (interpM A M J) [])

/-- `AFormula.denote`, executable, independent of `toFormula`. -/
def evalA (A : AttDoc) (M : FM) (J : Rel) : List String → List Nat → AFormula → Bool
  | _, ρ, .base φ => φ.eval M ρ
  | Γ, ρ, .att c => match c.key A Γ, c.holder.denote M.asStructure ρ with
      | some k, some vh => match c.slot with
        | none => J.contains (k, [vh])
        | some (_, t) => match t.denote M.asStructure ρ with
          | some vx => J.contains (k, [vh, vx])
          | none => false
      | _, _ => false
  | Γ, ρ, .not a => !(evalA A M J Γ ρ a)
  | Γ, ρ, .and a b => evalA A M J Γ ρ a && evalA A M J Γ ρ b
  | Γ, ρ, .or a b => evalA A M J Γ ρ a || evalA A M J Γ ρ b
  | Γ, ρ, .implies a b => !(evalA A M J Γ ρ a) || evalA A M J Γ ρ b
  | Γ, ρ, .all s a => (M.domains s).all (fun v => evalA A M J (s :: Γ) (v :: ρ) a)
  | Γ, ρ, .ex s a => (M.domains s).any (fun v => evalA A M J (s :: Γ) (v :: ρ) a)

/-- `seedClosure`, through `VE.Closure.reachEval` (the closure QS-1 wraps). -/
def closureB (A : AttDoc) (seed : Rel) : Rel :=
  VE.Reports.dedup (seed.flatMap (fun p =>
    ((keys A).filter (fun k => VE.Closure.reachEval .star (framePairs A) p.1 k)).map (·, p.2) ++ [p]))

def inClosureB (A : AttDoc) (seed : Rel) (k : Key) (vs : List Nat) : Bool :=
  seed.any (fun p => p.2 == vs && VE.Closure.reachEval .star (framePairs A) p.1 k)

/-- Every sublist of a list (the relations a search tries). -/
def sublists {α : Type} : List α → List (List α)
  | [] => [[]]
  | x :: xs => let r := sublists xs; r ++ r.map (x :: ·)

/-- The typed tuples of a key in `M`. -/
def tuplesOf (M : FM) (k : Key) : List (List Nat) :=
  match k.slotSort with
  | none => (M.domains k.holderSort).map (fun h => [h])
  | some s => (M.domains k.holderSort).flatMap (fun h => (M.domains s).map (fun x => [h, x]))

/-- Every typed relation over the document's keys in `M`. -/
def allJ (A : AttDoc) (M : FM) : List Rel :=
  sublists ((keys A).flatMap (fun k => (tuplesOf M k).map (k, ·)))

end VE.Attitudes.Check

/-! ## S5. Fixtures -/
namespace VE.Attitudes.Fixtures
open VE.Attitudes VE.Attitudes.Check
open VE.Reports (Act)

/-- A hypothetical table, written before E1 and E2 reported and kept only for the fixtures that need a table they
    did not give: a table without the pair (F-AT3), premise 3 for one word only (F-AT7), the review failures
    (D3), the long word (D17). Every other fixture runs on the frozen `table`. -/
def fixtureTable : Table :=
  { candidates := e1Words,
    lowerBound := [("very likely", "E1.cert.very-likely"), ("quite likely", "E1.cert.quite-likely")],
    above := [("very likely", "quite likely", "E1.pair.very-likely.quite-likely")],
    factive := some "E2.factive",
    knowsBelieves := some "E2.knows-believes",
    knowsThinks := [("very likely", "E2.knows-thinks.very-likely"), ("quite likely", "E2.knows-thinks.quite-likely")] }

/-- As `fixtureTable` without the pair: the order of the two words then comes only from a document. -/
def fixtureTableNoPair : Table := { fixtureTable with above := [] }

/-- Closure-review failures: a derived premise-3 word without its own item; a derived pair without its own item. -/
def badTableKnows : Table := { fixtureTable with knowsThinks := [("very likely", "E2.knows-thinks.very-likely")] }
def badTablePair : Table :=
  { fixtureTable with
    lowerBound := fixtureTable.lowerBound ++ [("likely", "E1.cert.likely")],
    above := fixtureTable.above ++ [("quite likely", "likely", "E1.pair.quite-likely.likely")],
    knowsThinks := fixtureTable.knowsThinks ++ [("likely", "E2.knows-thinks.likely")] }

def sortC : String := "claude_instance"
def sortS : String := "situation"

/-- The environment of the pilot fixtures: categories, the regulated act, and the hand-named intention terms. -/
def preds (ns : List (String × List String)) : String → Option (List String) :=
  fun p => (ns.find? (·.1 == p)).map (·.2)

def categories : List String :=
  ["mass_casualty_weapon_uplift", "critical_infrastructure_attack_uplift", "damaging_cyberweapon",
    "undermining_ai_oversight", "disempowering_humanity", "illegitimate_power_seizure", "csam_generation"]

def predicateList : List (String × List String) :=
  categories.map (fun c => (c, [sortS])) ++
  (List.range 7).map (fun i => (s!"intentionally_does_restricted_action_{i + 1}", [sortC, sortS])) ++
  [("weapons_uplift_permitted", [sortC, sortS])]

def envP : VE.Environment := { sorts := [sortC, sortS], predicates := preds predicateList, constants := fun _ => none }

def regulatedP : VE.Norms.Regulated :=
  { name := "weapons_uplift_permitted", sorts := [sortC, sortS], allowByDefault := false, role := .permission,
    act := some "{0} do the weapons uplift in {1}", permission := none }

/-! ### The fixture lexicon (SR-3, RC-3) -/

/-- The pilot's wording of each hand-named intention term (the first as section 3.3 renders it; no two alike, V4)
    and of the regulated act; every category atom takes the quoted fallback. -/
def actions : List String :=
  ["the weapons uplift", "the infrastructure attack uplift", "the cyberweapon work", "the oversight undermining",
    "the disempowering work", "the power seizure work", "the abuse material generation"]

def declaredWording (p : String) : Option String :=
  if p == "weapons_uplift_permitted" then some "{0} is permitted to do the weapons uplift in {1}" else
  ((List.range 7).find? (fun i => p == s!"intentionally_does_restricted_action_{i + 1}")).map
    (fun i => "{0} intentionally does " ++ actions[i]! ++ " in {1}")

def nounOf (s : String) : String := if s == "claude_instance" then "instance of Claude" else s

/-- The lexical view and the selected lexicon of a vocabulary: sorts with their nouns, predicates (name, argument
    sorts, declared wording) with the declared wording or else the quoted fallback, constants (name, sort) spelled as
    their names, no overlay, no negatives or aliases. -/
def lexOf (ss : List String) (ps : List (String × List String × Option String)) (cs : List (String × String)) :
    Lex :=
  { env := { sorts := ss.map (fun s => { name := s, noun := some (nounOf s) }),
             predicates := ps.map (fun p => { name := p.1, arity := p.2.1.length, args := p.2.1, wording := p.2.2 }),
             constants := cs.map (fun c => { name := c.1, sort := c.2 }) },
    overlay := {},
    lexicon := { nouns := ss.map (fun s => (s, nounOf s)), letters := ss.map (fun s => (s, s.take 1)),
                 wordings := ps.map (fun p =>
                   (p.1, p.2.2.getD ((VE.EnglishGrammar.fallbackWording p.1 p.2.1.length).getD ""))),
                 negatives := [], aliases := [], spellings := cs.map (fun c => (c.1, c.1)) } }

def vocabP : List (String × List String × Option String) :=
  predicateList.map (fun p => (p.1, p.2, declaredWording p.1))

/-- The fixture lexicon. -/
def lexP : Lex := lexOf [sortC, sortS] vocabP []

def contentOf (cat : String) : VE.Formula := .unary cat (.var 0)

def cond (m : Mode) (cat : String) : Cond :=
  { holder := .var 1, mode := m, slot := some (sortS, .var 0), content := contentOf cat }

def ql : Mode := .thinks "quite likely"

def docOf (T : Table) (declared : List (Word × Word)) (rules : List ARule) : AttDoc :=
  { E := envP, lits := [], authorPredicates := predicateList.map (·.1), regulated := [regulatedP],
    definitions := [], rules := rules, holders := [sortC], T := T, declared := declared,
    decidedBy := "unresolved_decider", lex := lexP }

/-- A fixture document with more vocabulary: extra predicates `ps` declared in `E`; those of `authored` also in
    `authorPredicates`, and those of `worded` also in the lexical view and the lexicon; constants `cs` of sort
    `situation` in `E`, and those of `spelled` also in the view and the lexicon. -/
def docWith (rules : List ARule) (ps : List (String × List String)) (authored worded : List String)
    (cs spelled : List String) : AttDoc :=
  let d := docOf table [] rules
  { d with
    E := { envP with predicates := preds (predicateList ++ ps),
                     constants := fun c => if cs.contains c then some sortS else none },
    authorPredicates := d.authorPredicates ++ authored,
    lex := lexOf [sortC, sortS]
      (vocabP ++ (ps.filter (fun p => worded.contains p.1)).map (fun p => (p.1, p.2, none)))
      ((spelled.filter cs.contains).map (·, sortS)) }

def ruleOf (n : String) (g : AFormula) : ARule :=
  { name := n, pred := "weapons_uplift_permitted", sign := false, guard := g, carveOuts := [], over := [] }

/-- F-AT1: u0165.s01 with u0173.s01, `intends` kept as a fixture (debate F4). -/
def guard1 : AFormula :=
  .or (.and (.att (cond .knows categories[0]!)) (.att (cond (.act .intends) categories[0]!)))
    (.att (cond ql categories[0]!))
def fat1 : AttDoc := docOf table [] [ruleOf "u0165-s01" guard1]

/-- F-AT5: the pilot's shape (debate F4): the intention conjunct is the hand-named open term. -/
def guardP (i : Nat) : AFormula :=
  .or (.and (.att (cond .knows categories[i]!))
      (.base (.binary s!"intentionally_does_restricted_action_{i + 1}" (.var 1) (.var 0))))
    (.att (cond ql categories[i]!))
def fat5 : AttDoc := docOf table [] ((List.range 7).map (fun i => ruleOf s!"u0165-s0{i + 1}" (guardP i)))

/-- F-AT2: two categories, u0165.s01 and u0165.s07, `intends` as in F-AT1. -/
def guard2 (cat : String) : AFormula :=
  .or (.and (.att (cond .knows cat)) (.att (cond (.act .intends) cat))) (.att (cond ql cat))
def fat2 : AttDoc :=
  docOf table [] [ruleOf "u0165-s01" (guard2 categories[0]!), ruleOf "u0165-s07" (guard2 categories[6]!)]

/-- F-AT3: two degrees on one content, with and without the document's pair (a table without the pair), and on
    the frozen table, whose own pair (very likely, quite likely) gives the premise. -/
def guard3 : AFormula := .or (.att (cond (.thinks "very likely") categories[0]!)) (.att (cond ql categories[0]!))
def fat3 : AttDoc := docOf fixtureTableNoPair [("very likely", "quite likely")] [ruleOf "u0165-s01" guard3]
def fat3none : AttDoc := docOf fixtureTableNoPair [] [ruleOf "u0165-s01" guard3]
def fat3frozen : AttDoc := docOf table [] [ruleOf "u0165-s01" guard3]

/-- F-AT0: F-AT1 with the attitude conditions removed. -/
def fat0 : AttDoc := docOf table [] [ruleOf "u0165-s01" (.base (contentOf categories[0]!))]

/-- F-AT1 with its `knows` condition changed to `c`, and extra vocabulary as `docWith`. -/
def withKnows (c : Cond) (ps : List (String × List String)) (authored worded cs spelled : List String) : AttDoc :=
  docWith [ruleOf "u0165-s01" (.or (.and (.att c) (.att (cond (.act .intends) categories[0]!)))
    (.att (cond ql categories[0]!)))] ps authored worded cs spelled

/-- F-AT8 (SR-1): a base predicate `unsaid__weapons_uplift_permitted` on `situation`, with a wording, in the
    `knows` content. -/
def unsaidP : String := "unsaid__weapons_uplift_permitted"
def fat8 : AttDoc :=
  withKnows { cond .knows categories[0]! with content := .unary unsaidP (.var 0) } [(unsaidP, [sortS])]
    [unsaidP] [unsaidP] [] []

/-- C-a (SR-2): the `knows` content `⊤`, closed; and with the slot kept (D14a). -/
def ca1 : AttDoc := withKnows { cond .knows categories[0]! with slot := none, content := .top } [] [] [] [] []
def ca2 : AttDoc := withKnows { cond .knows categories[0]! with content := .top } [] [] [] [] []
/-- C-b (SR-2): the closed `knows` content `C(s1)`; and `C(var 0)` slotted at the constant `s1` (D14b). -/
def cb1 : AttDoc :=
  withKnows { cond .knows categories[0]! with slot := none, content := .unary categories[0]! (.const "s1") }
    [] [] [] ["s1"] ["s1"]
def cb2 : AttDoc :=
  withKnows { cond .knows categories[0]! with slot := some (sortS, .const "s1") } [] [] [] ["s1"] ["s1"]
/-- C-c (SR-2): F-AT1 with the `intends` condition made `wants`, content `C(var 0)`; and `C(var 0) ∧ csam(var 0)`
    (D14c). -/
def wantsDoc (φ : VE.Formula) : AttDoc :=
  docWith [ruleOf "u0165-s01" (.or (.and (.att (cond .knows categories[0]!))
    (.att { cond (.act .wants) categories[0]! with content := φ })) (.att (cond ql categories[0]!)))] [] [] [] [] []
def cc1 : AttDoc := wantsDoc (contentOf categories[0]!)
def cc2 : AttDoc := wantsDoc (.and (contentOf categories[0]!) (contentOf categories[6]!))
/-- C-d (RC-1): C-b's first document with `s1` in `E` only; and a base predicate `extra_case` on `situation` in `E`
    only, named by the `knows` content (D14d). -/
def cd1 : AttDoc :=
  withKnows { cond .knows categories[0]! with slot := none, content := .unary categories[0]! (.const "s1") }
    [] [] [] ["s1"] []
def cd2 : AttDoc :=
  withKnows { cond .knows categories[0]! with content := .unary "extra_case" (.var 0) } [("extra_case", [sortS])]
    [] [] [] []

/-- F-AT9 (new, E2's admission): F-AT1's rule with the guard "both that situation is classified as … and that
    instance of Claude does not know that that situation is classified as …". -/
def guard9 : AFormula := assertedNotKnows (cond .knows categories[0]!)
def fat9 : AttDoc := docOf table [] [ruleOf "u0165-s01" guard9]

/-- One instance `0`, one situation `1`; the category true or false. -/
def model (cat : Bool) : FM :=
  { domains := fun s => if s == sortC then [0] else if s == sortS then [1] else [],
    constants := fun _ => none,
    relations := fun r => if cat && r == categories[0]! then [[1]] else [] }

instance : Inhabited Key := ⟨⟨.knows, "", none, .top⟩⟩

def kOf (A : AttDoc) (m : Mode) : Key := ((keys A).find? (·.mode == m)).get!

def M1 : Rel := [(kOf fat1 ql, [0, 1])]
def M2 : Rel := [(kOf fat1 .knows, [0, 1]), (kOf fat1 ql, [0, 1])]
def M3 : Rel := [(kOf fat1 .knows, [0, 1])]
def M4 : Rel := []
/-- The rule's context `[situation, claude_instance]`: variable 0 is the situation `1`, variable 1 the instance `0`. -/
def ρ1 : List Nat := [1, 0]
def Γ1 : List String := [sortS, sortC]

end VE.Attitudes.Fixtures

/-! ### F-AT1 -/
namespace VE.Attitudes.Fixtures
open VE.Attitudes VE.Attitudes.Check

#eval ("F-AT1 check", checkAtt fat1)
#eval ("F-AT1 names", (keys fat1).map (name fat1))
#eval ("F-AT1 frame labels", frameLabels fat1)
#eval ("F-AT1 frame size", (framePremises fat1).length)
#eval ("F-AT1 frame", framePremises fat1)
#eval ("F-AT1 elaborated guard", guard1.toFormula fat1 Γ1)
/-- Per model: frame holds, intended, guard (attitude semantics), guard (elaborated, on interp). -/
def row (J : Rel) (cat : Bool) : Bool × Bool × Bool × Bool :=
  (frameB fat1 (model cat) J, intendedB fat1 (model cat) J, evalA fat1 (model cat) J Γ1 ρ1 guard1,
    match guard1.toFormula fat1 Γ1 with
    | some φ => φ.eval (interpM fat1 (model cat) J) ρ1
    | none => false)
#eval ("M1 cat false, thinks", row M1 false)
#eval ("M2 cat false, knows+thinks", row M2 false)
#eval ("M3 cat true, knows only", row M3 true)
#eval ("M4 cat true, none", row M4 true)
/-- guard_collapse at the intended models M1 and M4: (ck ∧ ci) ∨ ct against ct alone. -/
def collapse (J : Rel) (cat : Bool) : Bool × Bool :=
  (evalA fat1 (model cat) J Γ1 ρ1 guard1, evalA fat1 (model cat) J Γ1 ρ1 (.att (cond ql categories[0]!)))
#eval ("collapse M1", collapse M1 false)
#eval ("collapse M4", collapse M4 true)
-- forced_iff_reachable: the closure of a seed.
#eval ("closure of [thinks]", (closureB fat1 M1).map (fun p => (name fat1 p.1, p.2)))
#eval ("closure of [knows]", (closureB fat1 M3).map (fun p => (name fat1 p.1, p.2)))
#eval ("closure of [knows] is intended (cat true)", intendedB fat1 (model true) (closureB fat1 M3))
#eval ("closure of [thinks] is intended (cat false): mistaken belief", intendedB fat1 (model false) (closureB fat1 M1))
/-- Forced = in every intended J holding the seed (enumerated), against reachable. -/
def forced (A : AttDoc) (M : FM) (seed : Rel) (k : Key) (vs : List Nat) : Bool :=
  (allJ A M).all (fun J => !(intendedB A M J && seed.all J.contains) || J.contains (k, vs))
#eval ("knows forces thinks: forced, reachable",
  forced fat1 (model true) M3 (kOf fat1 ql) [0, 1], inClosureB fat1 M3 (kOf fat1 ql) [0, 1])
#eval ("thinks forces knows: forced, reachable",
  forced fat1 (model false) M1 (kOf fat1 .knows) [0, 1], inClosureB fat1 M1 (kOf fat1 .knows) [0, 1])
#eval ("knows forces intends: forced, reachable",
  forced fat1 (model true) M3 (kOf fat1 (.act .intends)) [0, 1], inClosureB fat1 M3 (kOf fat1 (.act .intends)) [0, 1])

/-! ### F-AT0, F-AT2, F-AT3, F-AT5, the table -/
#eval ("F-AT0 check, keys, frame", checkAtt fat0, (keys fat0).length, (framePremises fat0).length)
#eval ("F-AT0 envAtt agrees with E on every declared name and three generated-looking names",
  (predicateList.map (·.1) ++ ["attitudes__knows__1", "attitudes__thinks_quite_likely__1", "unknown"]).all
    (fun p => (envAtt fat0).predicates p == envP.predicates p))
#eval ("F-AT2 check", checkAtt fat2)
#eval ("F-AT2 names", (keys fat2).map (name fat2))
#eval ("F-AT2 frame labels", frameLabels fat2)
#eval ("F-AT2 knows__1 reaches thinks__1, thinks__2, knows__2",
  ["attitudes__thinks_quite_likely__1", "attitudes__thinks_quite_likely__2", "attitudes__knows__2"].map
    (fun n => (n, inClosureB fat2 [(((keys fat2).find? (fun k => name fat2 k == "attitudes__knows__1")).get!, [0, 1])]
      (((keys fat2).find? (fun k => name fat2 k == n)).get!) [0, 1])))
#eval ("F-AT3 with the document's pair: check, labels", checkAtt fat3, frameLabels fat3)
#eval ("F-AT3 without it: check, labels", checkAtt fat3none, frameLabels fat3none)
#eval ("F-AT3 atLeast (very, quite), (quite, very) with and without",
  fat3.scale.atLeast "very likely" "quite likely", fat3.scale.atLeast "quite likely" "very likely",
  fat3none.scale.atLeast "very likely" "quite likely")
#eval ("F-AT3 on the frozen table: check, labels", checkAtt fat3frozen, frameLabels fat3frozen)
#eval ("F-AT5 check", checkAtt fat5)
#eval ("F-AT5 generated, hand-named, residual", (keys fat5).length, 7, (keys fat5).length + 7)
#eval ("F-AT5 frame size", (framePremises fat5).length)
#eval ("F-AT5 names", (keys fat5).map (name fat5))
#eval ("tables reviewed: table, fixture, no pair, bad knows, bad pair",
  table.reviewed, fixtureTable.reviewed, fixtureTableNoPair.reviewed, badTableKnows.reviewed, badTablePair.reviewed)
#eval ("badTablePair closure derives (very likely, likely)", badTablePair.scale.atLeast "very likely" "likely",
  badTablePair.hasPair "very likely" "likely")
#eval ("frozen table: admitted words, pairs, closure pairs among the five words",
  table.words, table.above.length,
  (table.words.flatMap (fun a => table.words.filter (fun b => a != b && table.scale.atLeast a b))).length)
#eval ("the fixture lexicon: Lexicon.failures, lexAgrees on F-AT1",
  VE.EnglishGrammar.Lexicon.failures lexP.env lexP.overlay lexP.lexicon, lexAgrees fat1)

/-! ### Diagnostics, in `checkAtt`'s order (each fixture fails exactly one check) -/
def withCond (c : Cond) : AttDoc := docOf table [] [ruleOf "u0165-s01" (.att c)]
def longWord : Word := "extraordinarily overwhelmingly and almost certainly likely"
def longTable : Table :=
  { fixtureTable with candidates := [longWord], lowerBound := [(longWord, "x")], above := [], knowsThinks := [] }
/-- D6a: the lexicon selects no wording for the first category. D6b: the lexical view declares it on
    `claude_instance`. -/
def lexNoWording : Lex :=
  { lexP with lexicon := { lexP.lexicon with
      wordings := lexP.lexicon.wordings.filter (·.1 != categories[0]!) } }
def lexWrongArgs : Lex :=
  { lexP with env := { lexP.env with predicates := lexP.env.predicates.map (fun d =>
      if d.name == categories[0]! then { d with args := [sortC] } else d) } }
/-- D15 (RC-3): 240 more author predicates, each declared in `E` on `situation` and in the fixture lexicon with its
    quoted fallback wording. -/
def morePreds : List (String × List String) := (List.range 240).map (fun i => (s!"p{i}", [sortS]))
def fat15 : AttDoc := docWith fat1.rules morePreds (morePreds.map (·.1)) (morePreds.map (·.1)) [] []
def diagnostics : List (String × Except String Unit) :=
  [("D1 decided_by", checkAtt { fat1 with decidedBy := "" }),
   ("D2 holder sort", checkAtt { fat1 with holders := ["robot"] }),
   ("D3 table review", checkAtt { fat1 with T := badTableKnows }),
   ("D4 declared word", checkAtt { fat1 with declared := [("as likely as not", "quite likely")] }),
   ("D5 scale caps", checkAtt { fat1 with declared := List.replicate 64 ("very likely", "quite likely") }),
   ("D6 reserved prefix", checkAtt { fat1 with authorPredicates := fat1.authorPredicates ++ ["attitudes__x"] }),
   ("D6a lexicon valid", checkAtt { fat1 with lex := lexNoWording }),
   ("D6b lexicon describes E", checkAtt { fat1 with lex := lexWrongArgs }),
   ("D7 holder term", checkAtt (withCond { cond ql categories[0]! with holder := .var 5 })),
   ("D8 holder sort of the term", checkAtt (withCond { cond ql categories[0]! with holder := .var 0 })),
   ("D9 word not admitted", checkAtt (withCond (cond (.thinks "unlikely") categories[0]!))),
   ("D0 a word E1 refused, frozen table", checkAtt (withCond (cond (.thinks "as likely as not") categories[0]!))),
   ("D10 slot sort", checkAtt (withCond { cond ql categories[0]! with slot := some ("place", .var 0) })),
   ("D11 slot term sort", checkAtt (withCond { cond ql categories[0]! with slot := some (sortS, .var 1) })),
   ("D12 quantifier", checkAtt (withCond { cond ql categories[0]! with
      content := .ex sortS (.unary categories[0]! (.var 0)) })),
   ("D13 regulated predicate in content", checkAtt (withCond { cond ql categories[0]! with
      content := .binary "weapons_uplift_permitted" (.var 0) (.var 0) })),
   ("D14 closed content with a variable", checkAtt (withCond { cond ql categories[0]! with slot := none })),
   ("D14a slot not mentioned (C-a)", checkAtt ca2),
   ("D14b slot term a constant (C-b)", checkAtt cb2),
   ("D14c wants wording (C-c)", checkAtt cc2),
   ("D14d symbol without a lexicon entry (C-d)", checkAtt cd1),
   ("D15 predicate count", checkAtt fat15),
   ("D16 generated name declared", checkAtt { fat1 with
      E := { envP with predicates := fun p => if p == "attitudes__knows__1" then some [sortS] else envP.predicates p } }),
   ("D17 generated name length", checkAtt (docOf longTable [] [ruleOf "u0165-s01" (.att (cond (.thinks longWord) categories[0]!))])),
   ("D18 W1 check of the elaborated document", checkAtt { fat1 with rules := [ruleOf "u0165-s01"
      (.and (.att (cond ql categories[0]!)) (.base (.unary categories[0]! (.var 1))))] })]
#eval diagnostics
/-- The texts section 5.2 fixes, in its order; each row's fixture answers exactly its text. -/
def diagnosticTexts : List String :=
  ["InvalidInput: attitudes decided_by is not a token",
   "UnknownSymbol: Unknown holder sort 'robot'",
   "InvalidInput: the attitude table is not closure-reviewed",
   "UnsupportedProfile: a declared scale pair names a word that attitudes@0 does not admit",
   "ResourceLimit: order edges",
   "InvalidInput: predicate attitudes__x uses the reserved prefix attitudes__",
   "InvalidInput: the English lexicon fails V1 for predicate mass_casualty_weapon_uplift",
   "InvalidInput: the English lexicon does not describe the document's environment",
   "UnboundVariable: Variable index 5 is outside its scope",
   "InvalidInput: attitude holder of sort situation is not of a holder sort",
   "UnsupportedProfile: 'thinks it unlikely' is not admitted by attitudes@0",
   "UnsupportedProfile: 'thinks it as likely as not' is not admitted by attitudes@0",
   "UnknownSymbol: Unknown slot sort 'place'",
   "TypeMismatch: attitude slot term has sort 'claude_instance', not 'situation'",
   "InvalidInput: an attitude content has a quantifier",
   "UnknownSymbol: Unknown predicate 'weapons_uplift_permitted'",
   "UnboundVariable: Variable index 0 is outside its scope",
   "InvalidInput: an attitude content does not mention its slot",
   "InvalidInput: an attitude slot term is not a variable of the guard",
   "UnsupportedProfile: this 'wants' content has no reviewed wording in attitudes@0",
   "InvalidInput: an attitude condition names a symbol with no entry in the English lexicon",
   "ResourceLimit: MAX_PREDICATES",
   "DuplicateDeclaration: generated predicate attitudes__knows__1",
   "ResourceLimit: generated predicate attitudes__thinks_extraordinarily_overwhelmingly_and_almost_certainly_likely__1 exceeds 64 bytes",
   "TypeMismatch: Predicate 'mass_casualty_weapon_uplift' expects ('situation',), received ('claude_instance',)"]
def errText : Except String Unit → String
  | .error e => e
  | .ok () => "ok"
#eval ("diagnostics that differ from section 5.2's text",
  (diagnostics.zip diagnosticTexts).filter (fun p => errText p.1.2 != p.2) |>.map (fun p => (p.1.1, errText p.1.2)))

/-! ### Draft 2's and 3's documents (SR-1, SR-2, RC-1) and E2's admitted form (F-AT9) -/
#eval ("C-a closed ⊤, C-b closed C(s1), C-c wants C(x): check", checkAtt ca1, checkAtt cb1, checkAtt cc1)
#eval ("C-d: s1 and extra_case without lexicon entries", checkAtt cd1, checkAtt cd2)
#eval ("C-a: the two documents' knows keys differ only in slotSort",
  (keys ca1).find? (·.mode == .knows), (keys ca2).find? (·.mode == .knows))
def U8 : Option VE.NormDefaults.UDoc := toU fat8 ["weapons_uplift_permitted"]
#eval ("F-AT8 check, toU some, WellFormedU, a factive premise names the unsaid table",
  checkAtt fat8, U8.isSome, U8.map VE.NormDefaults.WellFormedU,
  (framePremises fat8).any (fun φ => (VE.Norms.preds φ).contains (VE.NormDefaults.unsaidName "weapons_uplift_permitted")))
#eval ("F-AT9 check, names, frame labels, elaborated guard", checkAtt fat9, (keys fat9).map (name fat9),
  frameLabels fat9, guard9.toFormula fat9 Γ1)
#eval ("F-AT9's reading is NegatedFactive's first candidate, and P̂ is the category at the rule's situation",
  guard9 == .and (.base (contentOf categories[0]!)) (.not (.att (cond .knows categories[0]!))))
/-- F-AT9 per point: intended, guard (attitude semantics), guard (elaborated, on interp). -/
def row9 (J : Rel) (cat : Bool) : Bool × Bool × Bool :=
  (intendedB fat9 (model cat) J, evalA fat9 (model cat) J Γ1 ρ1 guard9,
    match guard9.toFormula fat9 Γ1 with
    | some φ => φ.eval (interpM fat9 (model cat) J) ρ1
    | none => false)
def K9 : Rel := [(kOf fat9 .knows, [0, 1])]
#eval ("F-AT9: cat true none, cat true knows, cat false none, cat false knows",
  row9 [] true, row9 K9 true, row9 [] false, row9 K9 false)

/-! ### AT-5's acceptance fixtures for the admitted row and its boundary (RR-2; spec 7.6). The readers are AT-5's,
so these are recorded here, elaborated, and computed at AT-5; the `#guard`s below check what is computable now. -/

/-- What AT-5's reader must answer for a text: its one reading (`readGuard` gives it and `readGuardAll` gives it
    alone), or a refusal with the catalogue row's code. -/
inductive Expect where
  | one (a : AFormula)
  | refused (code : String)

structure ReadFixture where
  id : String
  doc : AttDoc
  site : Site
  text : String
  expect : Expect

def ReadFixture.holds (f : ReadFixture) : Prop :=
  match f.site, f.expect with
  | .guard Γ, .one a => readGuard f.doc Γ f.text = .ok a ∧ readGuardAll f.doc Γ f.text = [a]
  | .guard Γ, .refused code => readGuard f.doc Γ f.text = .error code
  | .rule, .refused code => readRule f.doc f.text = .error code
  | .rule, .one _ => False

/-- The texts, in F-AT1's rule context (spec 3.3's rendering): `H` "that instance of Claude", `P` the category on a
    situation term. -/
def H9 : String := "that instance of Claude"
def P9 (t cat : String) : String := t ++ " is classified as \"" ++ cat ++ "\""
def notKnows9 (t cat : String) : String := H9 ++ " does not know that " ++ P9 t cat
def x9 : String := "that situation"
def C0 : String := categories[0]!
def C6 : String := categories[6]!

/-- The closed `knows` content `C(s1)`, as C-b's first document. -/
def cond9c : Cond := { cond .knows C0 with slot := none, content := .unary C0 (.const "s1") }
/-- F-AT9 with `s1` declared and spelled; with the row on the closed content; and with the row nested in a frame. -/
def fat9s1 : AttDoc := docWith [ruleOf "u0165-s01" guard9] [] [] [] ["s1"] ["s1"]
def fat9c : AttDoc := docWith [ruleOf "u0165-s01" (assertedNotKnows cond9c)] [] [] [] ["s1"] ["s1"]
def guard9n : AFormula := .or guard9 (.att (cond ql C0))
def fat9n : AttDoc := docOf table [] [ruleOf "u0165-s01" guard9n]

def negatedFactive : String := "NegatedFactive"

/-- The admitted row's exact one reading, alone, closed and nested; then the boundary of `NegatedFactive`'s
    exception: content, slot term (both ways) and conjunct order mismatched, the row's shape under "either … or",
    bare negated knowledge, and "unless" (a whole rule). -/
def readFixtures : List ReadFixture :=
  [⟨"row", fat9, .guard Γ1, "both " ++ P9 x9 C0 ++ " and " ++ notKnows9 x9 C0, .one guard9⟩,
   ⟨"row-closed", fat9c, .guard Γ1, "both " ++ P9 "s1" C0 ++ " and " ++ notKnows9 "s1" C0,
     .one (assertedNotKnows cond9c)⟩,
   ⟨"row-nested", fat9n, .guard Γ1,
     "either both " ++ P9 x9 C0 ++ " and " ++ notKnows9 x9 C0 ++ ", or " ++ H9 ++ " thinks it quite likely that " ++
       P9 x9 C0 ++ ", or both", .one guard9n⟩,
   ⟨"content-mismatch", fat9, .guard Γ1, "both " ++ P9 x9 C6 ++ " and " ++ notKnows9 x9 C0, .refused negatedFactive⟩,
   ⟨"slot-mismatch", fat9s1, .guard Γ1, "both " ++ P9 "s1" C0 ++ " and " ++ notKnows9 x9 C0,
     .refused negatedFactive⟩,
   ⟨"slot-mismatch-closed", fat9s1, .guard Γ1, "both " ++ P9 x9 C0 ++ " and " ++ notKnows9 "s1" C0,
     .refused negatedFactive⟩,
   ⟨"order", fat9, .guard Γ1, "both " ++ notKnows9 x9 C0 ++ " and " ++ P9 x9 C0, .refused negatedFactive⟩,
   ⟨"either", fat9, .guard Γ1, "either " ++ P9 x9 C0 ++ " or " ++ notKnows9 x9 C0 ++ ", or both",
     .refused negatedFactive⟩,
   ⟨"bare", fat9, .guard Γ1, notKnows9 x9 C0, .refused negatedFactive⟩,
   ⟨"unless", fat1, .rule,
     "Every instance of Claude must not do the weapons uplift in each situation if " ++ P9 x9 C0 ++ ", unless " ++
       H9 ++ " knows that " ++ P9 x9 C0 ++ ".", .refused negatedFactive⟩]

/-- AT-5's acceptance (RR-2): every fixture holds. -/
def readFixtures_hold : Prop := ∀ f ∈ readFixtures, f.holds
/-- `assertedNotKnows_one_reading`'s instance on F-AT9 (computed at AT-5). -/
def fat9_one_reading (h : WellFormedAtt fat9 = true) (hc : (Γ1, cond .knows C0) ∈ condsOf fat9) : Prop :=
  assertedNotKnows_one_reading fat9 h Γ1 (cond .knows C0) hc rfl

#eval ("AT-5 read fixtures (RR-2)", readFixtures.map (fun f => (f.id, f.text)))
#eval ("RR-2 documents: F-AT9 with s1, the closed row, the nested row: check",
  checkAtt fat9s1, checkAtt fat9c, checkAtt fat9n)

/-! ### AT-2: the route at F-AT1's points (unspecified completion) -/
def U1 : VE.NormDefaults.UDoc :=
  match toU fat1 ["weapons_uplift_permitted"] with
  | some U => U
  | none => ⟨⟨envP, [], ⟨[], [], []⟩⟩, []⟩
#eval ("U1 WellFormedU", VE.NormDefaults.WellFormedU U1)
def routeModel (cat : Bool) (J : List (String × List Nat)) : FM :=
  { domains := fun s => if s == sortC then [0] else if s == sortS then [1] else [],
    constants := fun _ => none,
    relations := fun r => if cat && r == categories[0]! then [[1]] else (J.filter (·.1 == r)).map (·.2) }
def RM1 : FM := routeModel false [("attitudes__thinks_quite_likely__1", [0, 1])]
def RM2 : FM := routeModel false [("attitudes__knows__1", [0, 1]), ("attitudes__thinks_quite_likely__1", [0, 1])]
def RM3 : FM := routeModel true [("attitudes__knows__1", [0, 1])]
def RM4 : FM := routeModel true []
/-- The first failing frame premise's label (PK-1's diagnostic names it), or none. -/
def firstFailing (A : AttDoc) (M : FM) : Option String :=
  ((frameLabels A).zip (framePremises A) |>.find? (fun p => !p.2.eval M [])).map (·.1)
#eval ("frame at RM1..RM4", [RM1, RM2, RM3, RM4].map (firstFailing fat1))
#eval ("diagnostic at RM2", (firstFailing fat1 RM2).map VE.Route.Wire.invalidModel)
#eval ("table3 at RM1, RM4", VE.NormDefaults.table3 U1 RM1 "weapons_uplift_permitted" [0, 1],
  VE.NormDefaults.table3 U1 RM4 "weapons_uplift_permitted" [0, 1])
#eval ("enumerateSettled at RM1, RM4", VE.NormDefaults.enumerateSettled U1 RM1 "weapons_uplift_permitted" [0, 1],
  VE.NormDefaults.enumerateSettled U1 RM4 "weapons_uplift_permitted" [0, 1])
def Fyes : VE.NormDefaults.FiniteFill U1 Nat := fun n => if n == "unsaid__weapons_uplift_permitted" then [[0, 1]] else []
def Fno : VE.NormDefaults.FiniteFill U1 Nat := fun _ => []
#eval ("RM4 fillings: fillValid yes/no, outcome yes/no",
  VE.NormDefaults.fillValid U1 RM4 Fyes, VE.NormDefaults.fillValid U1 RM4 Fno,
  (VE.Norms.outcomeBase (VE.NormDefaults.fill U1) "weapons_uplift_permitted").eval (RM4.withFill Fyes) [1, 0],
  (VE.Norms.outcomeBase (VE.NormDefaults.fill U1) "weapons_uplift_permitted").eval (RM4.withFill Fno) [1, 0])
#eval ("frame unsaid-free on U1", (framePremises fat1).all (fun φ =>
  U1.unspec.all (fun p => !(VE.Norms.preds φ).contains (VE.NormDefaults.unsaidName p))))
#eval ("frame typed over envAt (fill U1) 0 and baseEnvAtt", (framePremises fat1).all (fun φ =>
  φ.check (VE.Norms.envAt (VE.NormDefaults.fill U1) 0) [] && φ.check (baseEnvAtt fat1) []))
#eval ("RM1 fillings: fillValid yes/no, outcome yes/no",
  VE.NormDefaults.fillValid U1 RM1 Fyes, VE.NormDefaults.fillValid U1 RM1 Fno,
  (VE.Norms.outcomeBase (VE.NormDefaults.fill U1) "weapons_uplift_permitted").eval (RM1.withFill Fyes) [1, 0],
  (VE.Norms.outcomeBase (VE.NormDefaults.fill U1) "weapons_uplift_permitted").eval (RM1.withFill Fno) [1, 0])
#eval ("frame on RM4's two filled situations", (framePremises fat1).all (·.eval (RM4.withFill Fyes) []),
  (framePremises fat1).all (·.eval (RM4.withFill Fno) []))
#eval ("today's W1 decoder on an attitude node", VE.Norms.Wire.decodeBudgeted (Lean.Json.mkObj [("attitude", Lean.Json.mkObj [])]))

/-! ### More fixtures: F-AT6 (transitivity), F-AT7 (premise 3 per word), model correspondence -/
def guard6 : AFormula :=
  .or (.or (.att (cond .knows categories[0]!)) (.att (cond (.thinks "very likely") categories[0]!)))
    (.att (cond ql categories[0]!))
def fat6 : AttDoc := docOf table [] [ruleOf "u0165-s01" guard6]
#eval ("F-AT6 check, labels", checkAtt fat6, frameLabels fat6)
def table7 : Table := { fixtureTableNoPair with knowsThinks := [("quite likely", "E2.knows-thinks.quite-likely")] }
def guard7 : AFormula := .or (.att (cond .knows categories[0]!)) (.att (cond (.thinks "very likely") categories[0]!))
def fat7 : AttDoc := docOf table7 [] [ruleOf "u0165-s01" guard7]
def fat7item : AttDoc := docOf fixtureTableNoPair [] [ruleOf "u0165-s01" guard7]
#eval ("F-AT7 very likely without its own item: reviewed, check, labels", table7.reviewed, checkAtt fat7, frameLabels fat7)
#eval ("F-AT7 with its own item: check, labels", checkAtt fat7item, frameLabels fat7item)
def fat7frozen : AttDoc := docOf table [] [ruleOf "u0165-s01" guard7]
#eval ("F-AT7 on the frozen table (very likely has its own item): check, labels", checkAtt fat7frozen,
  frameLabels fat7frozen)

/-- Every tuple of a relation is declared with matching sorts (`Structure.Admissible`, finite, no constants). -/
def admissibleB (E : VE.Environment) (M : FM) (names : List String) : Bool :=
  names.all (fun r => (M.relations r).all (fun vs => match E.predicates r with
    | some ss => typedB M ss vs
    | none => false))
def allNames (A : AttDoc) : List String := predicateList.map (·.1) ++ (keys A).map (name A)
/-- `restrict`, finite: base relations without generated names, and `J` read off the generated names. -/
def restrictJ (A : AttDoc) (T : FM) : Rel := (keys A).flatMap (fun k => (T.relations (name A k)).map (k, ·))
def restrictBase (A : AttDoc) (T : FM) : FM :=
  { T with relations := fun r => if (keyOf A r).isSome then [] else T.relations r }
#eval ("interp_admissible: M1 intended (typed J)", admissibleB (envAtt fat1) (interpM fat1 (model false) M1) (allNames fat1))
#eval ("interp of an untyped J is not admissible", admissibleB (envAtt fat1) (interpM fat1 (model false) [(kOf fat1 ql, [1, 0])]) (allNames fat1))
#eval ("restrict (interp M1): J back, base back, base admissible over E",
  restrictJ fat1 (interpM fat1 (model false) M1) == M1,
  (allNames fat1).all (fun r => (restrictBase fat1 (interpM fat1 (model true) M3)).relations r == (model true).relations r),
  admissibleB envP (restrictBase fat1 (interpM fat1 (model true) M3)) (allNames fat1))
#eval ("restrict of a frame model is intended: RM1 yes, RM2 no",
  intendedB fat1 (model false) (restrictJ fat1 RM1), intendedB fat1 (model false) (restrictJ fat1 RM2))
#eval ("interp_restrict on a generated name: tuple in J, tuple not in J",
  (interpM fat1 (model false) (restrictJ fat1 RM1)).relations "attitudes__thinks_quite_likely__1" == RM1.relations "attitudes__thinks_quite_likely__1",
  (interpM fat1 (model false) (restrictJ fat1 RM1)).relations "attitudes__knows__1" == RM1.relations "attitudes__knows__1")
def phi0 : VE.Formula := .all sortS (contentOf categories[0]!)
#eval ("old_formula_invariant: forall situations category, on cat true and cat false (M, interp)",
  phi0.eval (model true) [], phi0.eval (interpM fat1 (model true) M3) [],
  phi0.eval (model false) [], phi0.eval (interpM fat1 (model false) M1) [])
#eval ("conservativity, the failing direction: empty relations satisfy the frame and refute phi0",
  frameB fat1 (model false) [], phi0.eval (interpM fat1 (model false) []) [], phi0.eval (model false) [])
/-- Conservativity, the holding direction: `[phi0] ⊢ phi0` on both sides. -/
example : VE.Entails.{0} (envAtt fat1) ([phi0] ++ framePremises fat1) phi0 ∧ VE.Entails.{0} fat1.E [phi0] phi0 :=
  ⟨fun _ _ h => h phi0 (List.mem_append_left _ (List.mem_singleton_self _)),
   fun _ _ h => h phi0 (List.mem_singleton_self _)⟩
#eval ("knows_factive: intended J with knows has a true content, on cat true / cat false",
  (allJ fat1 (model true)).all (fun J => !intendedB fat1 (model true) J ||
    J.all (fun p => p.1.mode != .knows || contentB (model true) p.1 p.2)),
  (allJ fat1 (model false)).all (fun J => !intendedB fat1 (model false) J || J.all (fun p => p.1.mode != .knows)))
def M1pk : Rel := [(kOf fat1 .knows, [0, 1]), (kOf fat1 (.act .intends), [0, 1]), (kOf fat1 ql, [0, 1])]
#eval ("guard_collapse with a = intends: (ck ∧ ci) ∨ ct against ct, at an intended J with all three, cat true",
  intendedB fat1 (model true) M1pk, evalA fat1 (model true) M1pk Γ1 ρ1 guard1,
  evalA fat1 (model true) M1pk Γ1 ρ1 (.att (cond ql categories[0]!)))
#eval ("F-AT5 collapse with the hand-named term true: intended J = knows+thinks, cat true",
  let J : Rel := [(kOf fat5 .knows, [0, 1]), (kOf fat5 ql, [0, 1])]
  let M : FM := { model true with relations := fun r =>
    if r == "intentionally_does_restricted_action_1" then [[0, 1]] else (model true).relations r }
  (intendedB fat5 M J, evalA fat5 M J Γ1 ρ1 (guardP 0), evalA fat5 M J Γ1 ρ1 (.att (cond ql categories[0]!))))
#eval ("F-AT5 collapse, no attitude, hand-named term true, cat true",
  let M : FM := { model true with relations := fun r =>
    if r == "intentionally_does_restricted_action_1" then [[0, 1]] else (model true).relations r }
  (intendedB fat5 M [], evalA fat5 M [] Γ1 ρ1 (guardP 0), evalA fat5 M [] Γ1 ρ1 (.att (cond ql categories[0]!))))

/-! ### One `#guard` per theorem (A3): F-AT1, F-AT2 or the stated fixture -/
#guard (keys fat1).all (fun k => (fat1.E.predicates (name fat1 k)).isNone && (name fat1 k).utf8ByteSize ≤ 64)
#guard decide ((keys fat2).map (name fat2)).Nodup
#guard (keys fat2).all (fun k => keyOf fat2 (name fat2 k) == some k)
#guard (contentOf categories[0]!).check fat1.E [sortS] && (contentOf categories[0]!).check (envAtt fat1) [sortS]
#guard match toNorms fat1 with
  | some D => VE.Norms.WellFormed D
  | none => false
#guard (framePremises fat2).all (·.check (baseEnvAtt fat2) [])
#guard (framePremises fat2).all VE.SoftNorms.universalQF
#guard (frameLabels fat2).length == (framePremises fat2).length && decide (frameLabels fat2).Nodup
#guard (framePairs fat6).all (fun p => (p.1.mode == .knows || match p.1.mode with | .thinks _ => true | _ => false) &&
  p.2.mode != .knows)
#guard (framePairs fat6).length == 3 && (framePairs fat6).contains (kOf fat6 .knows, kOf fat6 ql)
#guard row M1 false == (true, true, true, true) && row M4 true == (true, true, false, false)
#guard row M2 false == (false, false, true, true) && row M3 true == (false, false, false, false)
#guard frameB fat1 (model true) [] && frameB fat1 (model false) [] && frameB fat2 (model false) []
#guard intendedB fat1 (model false) M1 && (closureB fat1 M1).length == 1
#guard collapse M1 false == (true, true) && collapse M4 true == (false, false)
#guard table.reviewed && fixtureTable.reviewed && !badTableKnows.reviewed && !badTablePair.reviewed
#guard (frameLabels fat3).length == 1 && (frameLabels fat3none).length == 0
#guard (frameLabels fat7).length == 1 && (frameLabels fat7item).length == 2
#guard (keys fat5).length == 14 && (framePremises fat5).length == 14
#guard (diagnostics.map (·.2.toBool)).all (· == false)
#guard VE.NormDefaults.table3 U1 RM1 "weapons_uplift_permitted" [0, 1] == some false
#guard VE.NormDefaults.table3 U1 RM4 "weapons_uplift_permitted" [0, 1] == none
#guard (attitudesPack fat1).labelled.map (·.2) == framePremises fat1 &&
  (attitudesPack fat1).labelled.map (·.1) == frameLabels fat1

/-! ### Draft 2's and 3's `#guard`s (section 7.5), and the frozen table's -/
-- the frozen table: five words, ten pairs, already closed
#guard table.words.length == 5 && table.above.length == 10 &&
  (table.words.flatMap (fun a => table.words.filter (fun b => a != b && table.scale.atLeast a b))).length == 10
-- the fixture lexicon is valid and describes the fixture environment (D6a, D6b pass on F-AT1)
#guard (VE.EnglishGrammar.Lexicon.failures lexP.env lexP.overlay lexP.lexicon).isEmpty && lexAgrees fat1
-- every diagnostic row answers exactly section 5.2's text (D6a, D6b, D14a–D14d and D0 included)
#guard diagnostics.length == diagnosticTexts.length &&
  (diagnostics.zip diagnosticTexts).all (fun p => errText p.1.2 == p.2)
-- frame_unsaidFree: with `hw` on F-AT1; F-AT8 passes `checkAtt`, its factive premise names an unsaid table, and
-- `WellFormedU` fails, so the statement without `hw` is false and with it does not apply
#guard VE.NormDefaults.WellFormedU U1 && (framePremises fat1).all (fun φ =>
  U1.unspec.all (fun p => !(VE.Norms.preds φ).contains (VE.NormDefaults.unsaidName p)))
#guard (checkAtt fat8).toBool && U8.map VE.NormDefaults.WellFormedU == some false &&
  (framePremises fat8).any (fun φ => (VE.Norms.preds φ).contains (VE.NormDefaults.unsaidName "weapons_uplift_permitted"))
-- the collision pairs and the `wants` pair: the first document of each is admitted, the second refused at its row
#guard (checkAtt ca1).toBool && (checkAtt cb1).toBool && (checkAtt cc1).toBool
#guard errText (checkAtt cd2) == "InvalidInput: an attitude condition names a symbol with no entry in the English lexicon"
-- F-AT3 and F-AT7 on the frozen table: its own pair gives premise 4, and "very likely" has its premise 3
#guard (frameLabels fat3frozen).length == 1 && (frameLabels fat7frozen).length == 2
-- F-AT9, the admitted "both P and H does not know that P": one key, the factive premise only; true exactly at the
-- intended point where the category holds and the knowing does not; elaborated and attitude readings agree
#guard (checkAtt fat9).toBool && (keys fat9).length == 1 && (framePremises fat9).length == 1
#guard row9 [] true == (true, true, true) && row9 K9 true == (true, false, false) &&
  row9 [] false == (true, false, false) && row9 K9 false == (false, false, false)
-- RR-1: the row's one reading is its own tree `and P̂ (not K)` (P̂ the content at the slot term, the content itself
-- when closed), not the composed `and P̂ (and P̂ (not K))`; F-AT9's and the closed row's `knows` occurrences meet
-- `assertedNotKnows_one_reading`'s hypotheses
#guard guard9 == .and (.base (contentOf C0)) (.not (.att (cond .knows C0))) &&
  assertedNotKnows cond9c == .and (.base (.unary C0 (.const "s1"))) (.not (.att cond9c)) &&
  assertedOf { cond .knows C0 with slot := some (sortS, .const "s1") } == .unary C0 (.const "s1") &&
  (condsOf fat9).contains (Γ1, cond .knows C0) && (condsOf fat9c).contains (Γ1, cond9c)
-- RR-2: the fixtures' documents are admitted, their texts distinct, and exactly the three row texts have one reading
#guard (checkAtt fat9s1).toBool && (checkAtt fat9c).toBool && (checkAtt fat9n).toBool &&
  (readFixtures.map (·.text)).eraseDups.length == readFixtures.length && readFixtures.length == 10 &&
  (readFixtures.filter (fun f => match f.expect with | .one _ => true | _ => false)).map (·.id) ==
    ["row", "row-closed", "row-nested"]

end VE.Attitudes.Fixtures

/-! ## S6. Small-scope counterexample search (debate round 3): every document of at most two keys and two holder
sorts built from a pool of conditions, on every model of at most two elements. A counterexample fails the review. -/
namespace VE.Attitudes.Search
open VE.Attitudes VE.Attitudes.Check
open VE.Reports (Act)

def sC : String := "claude_instance"
def sS : String := "situation"
def sU : String := "user"
def pP : String := "p_case"
def pQ : String := "q_case"

/-- `c0` is in the search lexicon; `c1` is declared in `E` only (D14d's member). -/
def envS : VE.Environment :=
  { sorts := [sC, sS, sU], constants := fun c => if c == "c0" || c == "c1" then some sS else none,
    predicates := fun p => if p == pP || p == pQ then some [sS] else if p == "act_ok" then some [sC, sS] else none }

/-- The search lexicon (SR-8): valid, and `lexAgrees` holds. -/
def lexS : Lex :=
  VE.Attitudes.Fixtures.lexOf [sC, sS, sU] [(pP, [sS], none), (pQ, [sS], none), ("act_ok", [sC, sS], none)]
    [("c0", sS)]

def regS : VE.Norms.Regulated :=
  { name := "act_ok", sorts := [sC, sS], allowByDefault := false, role := .permission, act := some "{0} act in {1}",
    permission := none }

instance : Inhabited AFormula := ⟨.base .top⟩

def ql : Mode := .thinks "quite likely"
def vl : Mode := .thinks "very likely"
def onS (m : Mode) (φ : VE.Formula) : Cond := { holder := .var 1, mode := m, slot := some (sS, .var 0), content := φ }
def closed (m : Mode) (φ : VE.Formula) : Cond := { holder := .var 1, mode := m, slot := none, content := φ }
def Px : VE.Formula := .unary pP (.var 0)
def Qx : VE.Formula := .unary pQ (.var 0)

/-- Conditions in the rule's context `[situation, claude_instance]`: draft 1's twelve members (0–11), the four that
    the draft-2 and draft-3 checks refuse (12–15: D14a, D14b, D14c, D14d), the `wants` member they admit (16), and
    the form E2 admitted, "both P and H does not know that P" (17). -/
def pool : List AFormula :=
  [.att (onS .knows Px), .att (onS ql Px), .att (onS vl Px), .att (onS (.act .believes) Px),
   .att (onS (.act .intends) Px), .att (onS .knows Qx), .att (onS ql Qx), .att (onS .knows (.not Px)),
   .att (closed .knows .top), .att (closed ql .bottom),
   .ex sU (.att { holder := .var 0, mode := .knows, slot := some (sS, .var 1), content := Px }),
   .ex sU (.att { holder := .var 0, mode := ql, slot := some (sS, .var 1), content := Px }),
   .att (onS .knows .top),
   .att { onS .knows Px with slot := some (sS, .const "c0") },
   .att (onS (.act .wants) (.and Px Qx)),
   .att (closed .knows (.unary pP (.const "c1"))),
   .att (onS (.act .wants) Px),
   assertedNotKnows (onS .knows Px)]

/-- The admitted form's member. -/
def ank : AFormula := pool[17]!

/-- The diagnostic of each refused member: section 5.2's row. -/
def refusedRow (i : Nat) : Option String :=
  if i == 12 then some "InvalidInput: an attitude content does not mention its slot"
  else if i == 13 then some "InvalidInput: an attitude slot term is not a variable of the guard"
  else if i == 14 then some "UnsupportedProfile: this 'wants' content has no reviewed wording in attitudes@0"
  else if i == 15 then some "InvalidInput: an attitude condition names a symbol with no entry in the English lexicon"
  else none

def docS (g : AFormula) : AttDoc :=
  { E := envS, lits := [], authorPredicates := [pP, pQ, "act_ok"], regulated := [regS], definitions := [],
    rules := [{ name := "r", pred := "act_ok", sign := false, guard := g, carveOuts := [], over := [] }],
    holders := [sC, sU], T := table, declared := [], decidedBy := "d", lex := lexS }

/-- One search document: its guard, the diagnostic it must answer when it holds a refused member (the first, in
    document order, since `checkAtt` checks conditions in that order), and whether it holds the admitted form. -/
structure Case where
  g : AFormula
  refused : Option String
  hasAnk : Bool
  members : List Nat

def caseOf (is : List Nat) (g : AFormula) : Case :=
  ⟨g, (is.filterMap refusedRow).head?, is.contains 17, is⟩

def cases : List Case :=
  (List.range pool.length).map (fun i => caseOf [i] pool[i]!) ++
  (List.range pool.length).flatMap (fun i => (List.range pool.length).flatMap (fun j =>
    if i < j then [caseOf [i, j] (.or pool[i]! pool[j]!), caseOf [i, j] (.and pool[i]! pool[j]!),
      caseOf [i, j] (.not (.or pool[i]! pool[j]!))] else []))

def guards : List AFormula := cases.map (·.g)

/-- A document with its keys, frame and names computed once. -/
structure CDoc where
  A : AttDoc
  g : AFormula
  ks : List Key
  fps : List (Key × Key)
  prem : List VE.Formula
  nm : List (Key × String)
  elaborated : Option VE.Formula
  wf : Bool
  answer : String

def compile (g : AFormula) : CDoc :=
  let A := docS g
  { A := A, g := g, ks := keys A, fps := framePairs A, prem := framePremises A,
    nm := (keys A).map (fun k => (k, name A k)), elaborated := g.toFormula A [sS, sC], wf := WellFormedAtt A,
    answer := match checkAtt A with
      | .ok () => "ok"
      | .error e => e }

def interpC (d : CDoc) (M : FM) (J : Rel) : FM :=
  { M with relations := fun r => match d.nm.find? (·.2 == r) with
      | some (k, _) => (J.filter (·.1 == k)).map (·.2)
      | none => M.relations r }

def intendedC (d : CDoc) (M : FM) (J : Rel) : Bool :=
  J.all (fun p => d.ks.contains p.1 && typedB M p.1.sorts p.2) &&
  J.all (fun p => p.1.mode != .knows || contentB M p.1 p.2) &&
  d.fps.all (fun q => J.all (fun p => p.1 != q.1 || J.contains (q.2, p.2)))

def frameC (d : CDoc) (M : FM) (J : Rel) : Bool := d.prem.all (fun φ => φ.eval (interpC d M J) [])

def tuplesC (M : FM) (k : Key) : List (List Nat) := tuplesOf M k
def allJC (d : CDoc) (M : FM) : List Rel := sublists (d.ks.flatMap (fun k => (tuplesC M k).map (k, ·)))

/-- Models of at most two elements (sorts may share elements), with every choice of `p_case` and `q_case`. -/
def configs : List (List (String × List Nat)) :=
  [[(sC, [0]), (sS, [1]), (sU, [])], [(sC, [0]), (sS, [0]), (sU, [0])], [(sC, [0]), (sS, [1]), (sU, [1])],
   [(sC, [0]), (sS, [0, 1]), (sU, [1])], [(sC, [0, 1]), (sS, [1]), (sU, [0])]]

def modelsOf (cfg : List (String × List Nat)) : List FM :=
  let dom := fun s => ((cfg.find? (·.1 == s)).map (·.2)).getD []
  (sublists (dom sS)).flatMap (fun ps => (sublists (dom sS)).map (fun qs =>
    { domains := dom, constants := fun _ => none,
      relations := fun r => if r == pP then ps.map ([·]) else if r == pQ then qs.map ([·]) else [] }))

def valuations (M : FM) : List (List Nat) := (M.domains sS).flatMap (fun x => (M.domains sC).map (fun c => [x, c]))

/-- The conditions of a guard, in the rule's context. -/
def condsG (g : AFormula) : List (List String × Cond) := g.conds [sS, sC]

/-- T1 frame_iff_intended, T2 att_elaboration_faithful (with a non-elaborating guard counted apart). -/
def t12 (d : CDoc) (M : FM) : Nat × Nat :=
  (allJC d M).foldl (fun (acc : Nat × Nat) J =>
    let t1 := if frameC d M J == intendedC d M J then 0 else 1
    let t2 := match d.elaborated with
      | some φ => (valuations M).countP (fun ρ => φ.eval (interpC d M J) ρ != evalA d.A M J [sS, sC] ρ d.g)
      | none => 1
    (acc.1 + t1, acc.2 + t2)) (0, 0)

/-- T3 guard_collapse with `hp` (the repaired statement), and the draft-1 statement (no `hp`, `ct` from the pool). -/
def t3 (d : CDoc) (M : FM) : Nat × Nat :=
  let cs := condsG d.g
  let poolConds := (pool.flatMap condsG).filter (fun p => p.1 == [sS, sC])
  let rest : List AFormula := [.base Px, .base .top, .att (onS (.act .intends) Px)]
  let intendedJs := (allJC d M).filter (intendedC d M)
  let check := fun (ck ct : Cond) => intendedJs.foldl (fun n J => n + rest.foldl (fun n2 a =>
      n2 + (valuations M).countP (fun ρ =>
        evalA d.A M J [sS, sC] ρ (.or (.and (.att ck) a) (.att ct)) != evalA d.A M J [sS, sC] ρ (.att ct))) 0) 0
  let repaired := cs.foldl (fun n p => n + cs.foldl (fun n2 q =>
      match p.2.key d.A p.1, q.2.key d.A q.1 with
      | some k, some kt =>
        if p.1 == [sS, sC] && q.1 == [sS, sC] && d.fps.contains (k, kt) && p.2.holder == q.2.holder &&
            p.2.slot.map (·.2) == q.2.slot.map (·.2) then n2 + check p.2 q.2 else n2
      | _, _ => n2) 0) 0
  let draft1 := cs.foldl (fun n p => n + poolConds.foldl (fun n2 q =>
      match p.2.key d.A p.1, q.2.key d.A q.1 with
      | some k, some kt =>
        if p.1 == [sS, sC] && k.mode == .knows && (match kt.mode with | .thinks _ => true | _ => false) &&
            sameSubject k kt && p.2.holder == q.2.holder && p.2.slot == q.2.slot then n2 + check p.2 q.2 else n2
      | _, _ => n2) 0) 0
  (repaired, draft1)

/-- The seeds T4 checks: the sublists of the atoms with no nonfactive knowing. -/
def seedsOf (M : FM) (atoms : List (Key × List Nat)) : List (List (Key × List Nat)) :=
  (sublists atoms).filter (fun s => s.all (fun p => p.1.mode != .knows || contentB M p.1 p.2))

/-- T4 seed_intended and forced_iff_reachable, T5 mistaken_belief_admissible. -/
def t45 (d : CDoc) (M : FM) : Nat × Nat :=
  let Js := allJC d M
  let intendedJs := Js.filter (intendedC d M)
  let atoms := d.ks.flatMap (fun k => (tuplesC M k).map (k, ·))
  let seeds := seedsOf M atoms
  let t4 := seeds.foldl (fun n seed =>
    let cl := VE.Reports.dedup (seed.flatMap (fun p =>
      (d.ks.filter (fun k => VE.Closure.reachEval .star d.fps p.1 k)).map (·, p.2) ++ [p]))
    let bad1 := if intendedC d M cl then 0 else 1
    let bad2 := atoms.countP (fun kv =>
      let forced := intendedJs.all (fun J => !(seed.all J.contains) || J.contains kv)
      let reach := seed.any (fun p => p.2 == kv.2 && VE.Closure.reachEval .star d.fps p.1 kv.1)
      forced != reach)
    n + bad1 + bad2) 0
  let t5 := atoms.countP (fun kv => kv.1.mode != .knows && !intendedJs.any (fun J => J.contains kv))
  (t4, t5)

/-- T7 framePairs_transitive and the D-A9 modes, per document. -/
def t7 (d : CDoc) : Nat :=
  (d.fps.foldl (fun n p => n + (d.fps.filter (fun q => q.1 == p.2 && q.2 != p.1 && !d.fps.contains (p.1, q.2))).length) 0) +
  d.fps.countP (fun p => p.2.mode == .knows || match p.1.mode with | .act _ => true | _ => false)

/-- T8: empty attitude relations satisfy the frame and change no old formula. -/
def oldFormulas : List VE.Formula :=
  [.all sS (.unary pP (.var 0)), .ex sS (.and (.unary pP (.var 0)) (.not (.unary pQ (.var 0)))),
   .all sS (.implies (.unary pP (.var 0)) (.unary pQ (.var 0)))]
def t8 (d : CDoc) (M : FM) : Nat :=
  (if frameC d M [] then 0 else 1) +
  oldFormulas.countP (fun φ => φ.eval M [] != φ.eval (interpC d M []) [])

/-- Non-vacuity: how many collapse instances (pairs linked by a frame pair) the search tried, how many candidate
    seeds it enumerated, and how many of them T4 checked (`seedsOf`). -/
def instancesOf (d : CDoc) (M : FM) : Nat × Nat × Nat :=
  let cs := condsG d.g
  let pairs := cs.foldl (fun n p => n + cs.countP (fun q =>
    match p.2.key d.A p.1, q.2.key d.A q.1 with
    | some k, some kt => p.1 == [sS, sC] && q.1 == [sS, sC] && d.fps.contains (k, kt) && p.2.holder == q.2.holder
    | _, _ => false)) 0
  let atoms := d.ks.flatMap (fun k => (tuplesC M k).map (k, ·))
  (pairs, (sublists atoms).length, (seedsOf M atoms).length)

/-- T9, the admitted form's reading `P ∧ ¬knows(P)` (E2): at each valuation where P holds, some intended relation
    makes the member true and some makes it false (the frame neither refutes nor forces it); where P fails, no
    intended relation makes it true. Counts the valuations where that fails; `ankTried` counts the valuations. -/
def t9 (d : CDoc) (M : FM) : Nat × Nat :=
  let intendedJs := (allJC d M).filter (intendedC d M)
  let vals := valuations M
  (vals.countP (fun ρ =>
    let tv := intendedJs.any (fun J => evalA d.A M J [sS, sC] ρ ank)
    let fv := intendedJs.any (fun J => !evalA d.A M J [sS, sC] ρ ank)
    if Px.eval M ρ then !(tv && fv) else tv), vals.length)

structure Tally where
  collapseCases : Nat := 0
  /-- candidate seeds enumerated, and those T4 checked (no nonfactive knowing) -/
  seeds : Nat := 0
  seedsChecked : Nat := 0
  docs : Nat := 0
  wf : Nat := 0
  /-- documents of draft 1's twelve members only, and how many of them `checkAtt` admits -/
  earlier : Nat := 0
  earlierWf : Nat := 0
  /-- documents holding a refused member, and those that do not answer that member's row -/
  refused : Nat := 0
  refusalMiss : Nat := 0
  /-- documents with no refused member that `checkAtt` refuses, or that have more than two keys -/
  unexpected : Nat := 0
  /-- documents holding the admitted form, and the valuations T9 tried -/
  ankDocs : Nat := 0
  ankTried : Nat := 0
  models : Nat := 0
  t1 : Nat := 0
  t2 : Nat := 0
  t3 : Nat := 0
  t3draft1 : Nat := 0
  t4 : Nat := 0
  t5 : Nat := 0
  t7 : Nat := 0
  t8 : Nat := 0
  t9 : Nat := 0
  deriving Repr

def runSearch (cs : List Case) (cfgs : List (List (String × List Nat))) : Tally :=
  cs.foldl (fun (t : Tally) c =>
    let d := compile c.g
    let early : Nat := if c.members.all (· < 12) then 1 else 0
    let earlyWf : Nat := if d.wf then early else 0
    let t : Tally := { t with docs := t.docs + 1, earlier := t.earlier + early, earlierWf := t.earlierWf + earlyWf }
    match c.refused with
    | some row =>
      let miss : Nat := if d.answer == row then 0 else 1
      { t with refused := t.refused + 1, refusalMiss := t.refusalMiss + miss }
    | none =>
    if !d.wf || d.ks.length > 2 then { t with unexpected := t.unexpected + 1 } else
    let ank : Nat := if c.hasAnk then 1 else 0
    let t : Tally := { t with wf := t.wf + 1, t7 := t.t7 + t7 d, ankDocs := t.ankDocs + ank }
    (cfgs.flatMap modelsOf).foldl (fun (t : Tally) M =>
      let (a, b) := t12 d M
      let (c3, c1) := t3 d M
      let (e, f) := t45 d M
      let (g1, g2, g3) := instancesOf d M
      let (n9, v9) := if c.hasAnk then t9 d M else (0, 0)
      { t with
        models := t.models + 1, t1 := t.t1 + a, t2 := t.t2 + b, t3 := t.t3 + c3, t3draft1 := t.t3draft1 + c1,
        t4 := t.t4 + e, t5 := t.t5 + f, t8 := t.t8 + t8 d M, t9 := t.t9 + n9, ankTried := t.ankTried + v9,
        collapseCases := t.collapseCases + g1, seeds := t.seeds + g2, seedsChecked := t.seedsChecked + g3 }) t) {}

#eval ("guards", guards.length)
#eval ("search lexicon: Lexicon.failures, lexAgrees", VE.EnglishGrammar.Lexicon.failures lexS.env lexS.overlay lexS.lexicon,
  lexAgrees (docS (.base .top)))
def result : Tally := runSearch cases configs
#eval result
#guard (VE.EnglishGrammar.Lexicon.failures lexS.env lexS.overlay lexS.lexicon).isEmpty && lexAgrees (docS (.base .top))
#guard result.t1 + result.t2 + result.t3 + result.t4 + result.t5 + result.t7 + result.t8 + result.t9 == 0 &&
  result.t3draft1 > 0
#guard result.refusalMiss == 0 && result.unexpected == 0 && result.earlier == 210 && result.earlierWf == 210 &&
  result.wf + result.refused == result.docs && result.ankDocs > 0 && result.ankTried > 0 &&
  0 < result.seedsChecked && result.seedsChecked ≤ result.seeds

end VE.Attitudes.Search
