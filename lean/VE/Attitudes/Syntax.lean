import VE.Attitudes.Scale
import VE.Attribution.Content
import VE.Attribution.Words
import VE.Norms.SmallModel
import VE.Norms.Tree
import VE.EnglishGrammar.Lexicon

/-! The syntax of `attitudes@0` (docs/spec/attitudes.md sections 2.2 to 2.6): modes, attitude
conditions, guards, rules and documents; keys and their generated names `attitudes__<mode>__<i>`;
the environments that declare those names; elaboration to a W1 document (2.5); and the
well-formedness check `checkAtt` (2.6). Content identity is syntax-tree equality, never a
hash (D-A3); keys are de-duplicated by `reports@0`'s `VE.Reports.dedup`. -/

namespace VE.Attitudes
open VE.Reports (Act)
universe u

/-! ## 2.2 Modes, conditions, guards, rules, documents -/

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
  /-- the decider of every generated open term; "unstated" (the one W2 token, C2) when the document names none;
      rendered legend lines take their wording from the token's owner -/
  decidedBy : String
  /-- the English lexical data; checked by `checkAtt` (D6a, D6b) -/
  lex : Lex
  /-- (at-rev, AT-R1) the closed attitude nodes of the document's reading-set parts (PC-11's `attitude` case), in
      document order; `[]` on a document without a reading set -/
  parts : List Cond := []

/-- The table's pairs and the document's own. -/
def AttDoc.scale (A : AttDoc) : Scale := ⟨A.T.words, A.T.scale.above ++ A.declared⟩

/-! ## 2.3 Keys and generated names -/

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

/-- (at-rev, AT-R1) The reading-set parts, each read in the empty context: a part is closed. -/
def partsOf (A : AttDoc) : List (List String × Cond) := A.parts.map (fun c => ([], c))

def keys (A : AttDoc) : List Key :=
  VE.Reports.dedup ((condsOf A ++ partsOf A).filterMap (fun p => p.2.key A p.1))

/-- `attitudes__<mode>__<i>`, `i` the 1-based position among the keys of that mode. -/
def name (A : AttDoc) (k : Key) : String :=
  "attitudes__" ++ k.mode.slug ++ "__" ++ toString (((keys A).filter (·.mode == k.mode)).idxOf k + 1)

def keyOf (A : AttDoc) (r : String) : Option Key := (keys A).find? (fun k => name A k == r)

/-! ## 2.4 Environments -/

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

/-! ## 2.5 Elaboration -/

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

/-- (at-rev, AT-R1) A reading-set part's claim, PC-11's `attitude φ`: the part's atom at its holder, closed. -/
def partClaim (A : AttDoc) (c : Cond) : Option VE.Formula := (AFormula.att c).toFormula A []

/-! ## 2.6 The well-formedness check -/

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
    document's selected one. `part`: the condition is a reading-set part (at-rev, AT-R1), where D14c also words a
    closed `wants` of one unary base predicate on a constant; in a guard or carve-out it stays refused. -/
def renderCheck (A : AttDoc) (c : Cond) (part : Bool := false) : Except String Unit := do
  throwIf (match c.slot with | some _ => !mentionsSlot c.content | none => false)
    "InvalidInput: an attitude content does not mention its slot"
  throwIf (match c.slot with | some (_, .const _) => true | _ => false)
    "InvalidInput: an attitude slot term is not a variable of the guard"
  let worded : Bool := match c.mode, c.slot, c.content with
    | .act .wants, some _, .unary p (.var 0) =>
        ((A.lex.lexicon.wordings.lookup p).bind (fun w => VE.Reports.wantsPhrase? (w.stripPrefix "{0} "))).isSome
    | .act .wants, none, .unary p (.const _) =>
        part && ((A.lex.lexicon.wordings.lookup p).bind (fun w => VE.Reports.wantsPhrase? (w.stripPrefix "{0} "))).isSome
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

/-- One condition, in its context `Γ`; `part` as `renderCheck`'s. -/
def checkCond (A : AttDoc) (Γ : List String) (c : Cond) (part : Bool := false) : Except String Unit := do
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
  renderCheck A c part

def checkConds (A : AttDoc) : List (List String × Cond) → Except String Unit
  | [] => pure ()
  | (Γ, c) :: rest => do checkCond A Γ c; checkConds A rest

/-- (at-rev, AT-R1) The reading-set parts, in order: each is checked as a condition in the empty context, with
    `part`, so a holder or slot term that is a variable fails `termSort`, and a slot at a constant fails D14b. -/
def checkParts (A : AttDoc) : List Cond → Except String Unit
  | [] => pure ()
  | c :: rest => do checkCond A [] c (part := true); checkParts A rest

def checkNames (A : AttDoc) : List Key → Except String Unit
  | [] => pure ()
  | k :: rest => do
    let n := name A k
    throwIf ((A.E.predicates n).isSome || (A.regulated.map (·.name) ++ A.definitions.map (·.name)).contains n)
      s!"DuplicateDeclaration: generated predicate {n}"
    throwIf (n.utf8ByteSize > VE.Limits.maxIdentifierBytes) s!"ResourceLimit: generated predicate {n} exceeds 64 bytes"
    throwIf (n.any (· == ':')) s!"InvalidInput: generated predicate {n} contains ':'"
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
  checkParts A A.parts
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

end VE.Attitudes
