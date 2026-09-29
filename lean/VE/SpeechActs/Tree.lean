import VE.Norms.Layer

/-! Speech-act documents (docs/spec/speech-acts.md sections 1, 3, 4.1, 4.2 and
8.1): the scope block, commands, questions, queries, the semantic core
`SpeechDoc`, the command elaboration `demand`, the regenerated W1 policy and
premise list, and the executable well-formedness check `WellFormedSpeech`.

`eqGuard`, `demand`, `policy` and `premises` are defined here rather than in
`Demand.lean` (spec 8's file list) because `WellFormedSpeech` checks the
regenerated policy with W1's `WellFormed`; `Demand.lean` holds their theorems.

Nothing here changes a W1 definition: `policy D` is an ordinary `VE.Norms.Doc`
and every W1 function and theorem applies to it unchanged. -/
namespace VE.SpeechActs
open VE.Norms (Regulated Role Node Tree Doc WellFormed validate elaborate background envAt size
  typeDiagnostic pyRepr)

inductive Force | require | forbid
  deriving DecidableEq, Repr

inductive Mode | polar | whichAll | whichOne | follows | reading
  deriving DecidableEq, Repr

/-- The scope block of the environment (1.1, 3.1). -/
structure Scope where
  task      : String
  /-- (sort, constant) bound to the word "you" -/
  addressee : Option (String × String)
  /-- (phrase, constant), sorted by phrase -/
  definites : List (String × String)
  deriving DecidableEq, Repr

structure Command where
  unit  : String
  force : Force
  /-- the realising regulated predicate -/
  act   : String
  /-- constants for the slots after slot 0 -/
  args  : List String
  /-- closed; `.top` when absent -/
  guard : VE.Formula
  deriving DecidableEq, Repr

structure Query where
  id         : String
  /-- the pinned asserted unit ids (1.4), document order -/
  premiseIds : List String
  /-- regenerated from the pinned unit ids, document order -/
  premises   : List VE.Formula
  target     : VE.Formula
  deriving DecidableEq, Repr

structure Question where
  unit       : String
  mode       : Mode
  /-- closed (polar); context `[sort]` (which modes); ignored otherwise -/
  body       : VE.Formula
  sort       : Option String
  /-- 2 to 16 distinct constants of `sort`, wording order -/
  domain     : List String
  query      : Option String
  readingSet : Option (String × Nat)
  deriving DecidableEq, Repr

inductive Answer
  | yes | no
  | one (a : String)
  /-- a sublist of the domain, in domain order -/
  | all (S : List String)
  deriving DecidableEq, Repr

/-- The semantic core. The frozen `VE.Environment` (`lean/VE/Syntax.lean`) holds only sorts, predicate signatures and
constants, so the validated regulated declarations (3.1: names, sorts, defaults, roles, acts, duals) are stored
here explicitly, as W1's own decoder returns them; nothing recovers them from `E`. -/
structure SpeechDoc where
  E         : VE.Environment
  lits      : List String
  scope     : Scope
  /-- the validated `regulated` declarations of 3.1, W1's decoder output -/
  regulated : List Regulated
  /-- active author norm units, document order -/
  norms     : List Node
  /-- active commands, document order (1.2) -/
  commands  : List Command
  questions : List Question
  queries   : List Query
  /-- W2's fixed asserted premises with their unit ids, document order -/
  asserted  : List (String × VE.Formula)

/-! ## Elaboration of commands (4.2) -/

def regOf (D : SpeechDoc) (p : String) : Option Regulated := D.regulated.find? (fun r => r.name == p)

/-- The argument sorts of the realising predicate (`E.predicates c.act`). -/
def actSorts (D : SpeechDoc) (c : Command) : List String := (D.E.predicates c.act).getD []

def addresseeConst (D : SpeechDoc) : Option String := D.scope.addressee.map Prod.snd

/-- A right-nested conjunction; `.top` for none, the formula itself for one. -/
def conj : List VE.Formula → VE.Formula
  | [] => .top
  | [a] => a
  | a :: rest => .and a (conj rest)

/-- `var k = @a₀, var (k-1) = @a₁, …`: one equality per slot, the first slot at index `k`. -/
def eqsFrom : Nat → List String → List VE.Formula
  | _, [] => []
  | k, a :: as => .eq (.var k) (.const a) :: eqsFrom (k - 1) as

/-- The bound constants of a command in argument order: the addressee, then the arguments. -/
def slotConsts (D : SpeechDoc) (c : Command) : List String := (addresseeConst D).getD "" :: c.args

/-- One equality per situation variable: slot i of n+1 slots is `var (n - i)`; slot 0 is the addressee (4.2). -/
def eqGuard (D : SpeechDoc) (c : Command) : VE.Formula := conj (eqsFrom c.args.length (slotConsts D c))

def demand (D : SpeechDoc) (c : Command) : Node :=
  { name := "cmd-" ++ c.unit, pred := c.act, sign := decide (c.force = .require),
    guard := .and (eqGuard D c) c.guard, carveOuts := [], over := [] }

def policy (D : SpeechDoc) : Doc :=
  ⟨D.E, D.lits, ⟨D.regulated, [], D.norms ++ D.commands.map (demand D)⟩⟩

def assertedFormulas (D : SpeechDoc) : List VE.Formula := D.asserted.map Prod.snd

def premises (D : SpeechDoc) : List VE.Formula :=
  background (policy D) ++ elaborate (policy D).T ++ assertedFormulas D

def En (D : SpeechDoc) : VE.Environment := envAt (policy D) (size (policy D))

/-- 4.3: the tuple of constants denoted in `S`, in argument order; `none` when one does not denote. -/
def constsOf (S : VE.Structure) : List String → Option (List S.Carrier)
  | [] => some []
  | a :: as => match S.constant a, constsOf S as with
    | some v, some vs => some (v :: vs)
    | _, _ => none

/-- 4.3: the bound tuple of a command in a structure, argument order. -/
def boundTuple (D : SpeechDoc) (c : Command) (S : VE.Structure) : Option (List S.Carrier) :=
  match addresseeConst D with
  | none => none
  | some you => constsOf S (you :: c.args)

/-! ## Queries (1.4, 4.6) -/

/-- Membership of formulas through their `DecidableEq` (the derived `BEq` is not lawful). -/
instance instDecidableMemFormula (a : VE.Formula) (l : List VE.Formula) : Decidable (a ∈ l) :=
  @List.instDecidableMemOfLawfulBEq _ instBEqOfDecidableEq inferInstance a l

def queryPremises (D : SpeechDoc) (qr : Query) : List VE.Formula :=
  background (policy D) ++ elaborate (policy D).T ++ qr.premises

/-- 1.4: the pinned premises regenerated from the asserted units named by the query, in document order. -/
def pinnedAsserted (D : SpeechDoc) (qr : Query) : List VE.Formula :=
  (D.asserted.filter (fun u => u.1 ∈ qr.premiseIds)).map Prod.snd

/-- 1.4: the target is itself one of the pinned premises (`TrivialQuery`, a warning; the task stands). -/
def trivialQuery (D : SpeechDoc) (qr : Query) : Bool := decide (qr.target ∈ pinnedAsserted D qr)

/-! ## Combination (4.8) -/

/-- 4.8: the only way two documents' units reach one policy. Documents with different scope blocks are never
combined; documents over different environments (or regulated declarations, or literals) are not either, as the
W3 bundle rule requires one environment identity. Environment equality is not decidable on the function-valued
`VE.Environment`, so this is the specification-level operation; the executable form compares environment ids. -/
noncomputable def combine (D₁ D₂ : SpeechDoc) : Except String SpeechDoc :=
  open Classical in
  if D₁.scope ≠ D₂.scope then .error ("ScopeMismatch: " ++ D₁.scope.task ++ ", " ++ D₂.scope.task)
  else if D₁.E = D₂.E ∧ D₁.lits = D₂.lits ∧ D₁.regulated = D₂.regulated then
    .ok { D₁ with
      norms := D₁.norms ++ D₂.norms
      commands := D₁.commands ++ D₂.commands
      questions := D₁.questions ++ D₂.questions
      queries := D₁.queries ++ D₂.queries
      asserted := D₁.asserted ++ D₂.asserted }
  else .error "InvalidInput: combined documents need one environment identity"

/-- The active-unit projection: what `premises` may depend on. -/
def core (D : SpeechDoc) :
    VE.Environment × List String × Scope × List Regulated × List Node × List Command × List (String × VE.Formula) :=
  (D.E, D.lits, D.scope, D.regulated, D.norms, D.commands, D.asserted)

/-! ## Well-formedness (4.1) -/

/-- A W2 token: `[A-Za-z0-9_.-]`, 1 to 64 bytes. -/
def token (s : String) : Bool :=
  !s.isEmpty && s.utf8ByteSize ≤ 64 &&
    s.toList.all (fun c => c.isAlphanum || c == '_' || c == '.' || c == '-')

/-- Each constant declared with the sort in the same position. -/
def constsTyped (E : VE.Environment) : List String → List String → Bool
  | [], [] => true
  | a :: as, s :: ss => E.constants a == some s && constsTyped E as ss
  | _, _ => false

/-- The pairs `(aᵢ, aⱼ)` with `i < j`. -/
def pairsOf {α : Type} : List α → List (α × α)
  | [] => []
  | x :: xs => xs.map (fun y => (x, y)) ++ pairsOf xs

def scopeOk (D : SpeechDoc) : Bool :=
  token D.scope.task &&
  (match D.scope.addressee with
   | none => true
   | some (s, a) => D.E.sorts.contains s && D.E.constants a == some s) &&
  D.scope.definites.length ≤ 64 &&
  decide (D.scope.definites.map Prod.fst).Nodup &&
  D.scope.definites.all (fun (_, a) => (D.E.constants a).isSome)

/-- 4.1(3) and 3.2: the realising predicate has the role the force needs and the sorts of the declaration; the
addressee and every argument are declared constants of the slot sorts; the guard is closed and typed. -/
def commandOk (D : SpeechDoc) (c : Command) : Bool :=
  match regOf D c.act, D.scope.addressee with
  | some r, some (s, you) =>
    r.role == (if c.force = .require then Role.obligation else Role.permission) &&
    D.E.predicates c.act == some r.sorts &&
    r.sorts.head? == some s &&
    constsTyped D.E (you :: c.args) r.sorts &&
    c.guard.check D.E []
  | _, _ => false

/-- 4.1(4) at the level of the core: which modes carry 2 to 16 distinct constants of a declared sort and a body
over `[sort]`; a polar body is closed; a follows question names a query; a reading question names a set version. -/
def questionOk (D : SpeechDoc) (q : Question) : Bool :=
  match q.mode with
  | .polar => q.body.check D.E []
  | .whichAll | .whichOne => match q.sort with
    | some s => D.E.sorts.contains s && 2 ≤ q.domain.length && q.domain.length ≤ 16 &&
        decide q.domain.Nodup && q.domain.all (fun a => D.E.constants a == some s) && q.body.check D.E [s]
    | none => false
  | .follows => match q.query with
    | some i => D.queries.any (·.id == i)
    | none => false
  | .reading => match q.readingSet with
    | some (_, v) => 1 ≤ v
    | none => false

/-- 1.4: the stored premise list is the regenerated one; the target is closed and typed. -/
def queryOk (D : SpeechDoc) (qr : Query) : Bool :=
  decide (qr.premises = pinnedAsserted D qr) && qr.target.check D.E [] &&
    qr.premiseIds.all (fun i => D.asserted.any (·.1 == i))

/-- 12.4: commands take no precedence and are taken precedence over by nothing. -/
def noCommandOver (D : SpeechDoc) : Bool :=
  D.norms.all (fun N => N.over.all (fun m => !(D.commands.any (fun c => "cmd-" ++ c.unit == m))))

/-- The conditions the proofs use, as one Boolean; reached only after every diagnostic has passed. -/
def semanticSpeech (D : SpeechDoc) : Bool :=
  scopeOk D && D.commands.all (commandOk D) && noCommandOver D && D.questions.all (questionOk D) &&
    D.queries.all (queryOk D) && D.asserted.all (fun u => u.2.check D.E []) && WellFormed (policy D)

private def firstDup (ns : List String) : Option String := ns.find? (fun n => ns.count n > 1)

/-- The diagnostics of section 7 in the order it fixes: the environment block; units in document order (kind,
content, slots, mode, domain, query); `policy(D)` through W1's `validate` (its diagnostics verbatim); queries.
The profile gate, wordings (`ModeMismatch`), bindings and records are decoded on the wire (`Wire.lean`). -/
def checkSpeech (D : SpeechDoc) : Except String Unit := do
  unless token D.scope.task do throw "InvalidInput: speech_acts block"
  if let some (s, a) := D.scope.addressee then
    unless D.E.sorts.contains s do throw s!"UnknownSymbol: sort {s}"
    unless D.E.constants a == some s do throw s!"UnknownSymbol: {a}"
  if D.scope.definites.length > 64 then throw "ResourceLimit: definites"
  if (firstDup (D.scope.definites.map Prod.fst)).isSome then throw "InvalidInput: speech_acts block"
  for (_, a) in D.scope.definites do
    unless (D.E.constants a).isSome do throw s!"UnknownSymbol: {a}"
  for c in D.commands do
    let r ← match regOf D c.act with
      | some r => pure r
      | none => throw s!"UnknownSymbol: regulated predicate {c.act}"
    if c.force = .require && r.role != .obligation then
      throw s!"MissingObligationRole: {r.act.getD c.act}"
    if c.force = .forbid && r.role != .permission then
      throw s!"MissingPermissionRole: {r.act.getD c.act}"
    let some (s, you) := D.scope.addressee | throw "UnboundSlot: you"
    unless D.E.predicates c.act == some r.sorts do throw s!"InvalidInput: invalid command fields for {c.unit}"
    unless r.sorts.head? == some s do throw "TypeMismatch: addressee"
    for a in c.args do
      unless (D.E.constants a).isSome do throw s!"UnknownSymbol: {a}"
    unless constsTyped D.E (you :: c.args) r.sorts do
      throw s!"TypeMismatch: command args for {c.unit}"
    typeDiagnostic D.E [] c.guard
    unless c.guard.check D.E [] do throw s!"InvalidInput: invalid command fields for {c.unit}"
  if D.questions.length > 256 then throw "ResourceLimit: questions"
  for q in D.questions do
    match q.mode with
    | .polar =>
      typeDiagnostic D.E [] q.body
      unless q.body.check D.E [] do throw s!"InvalidInput: invalid question fields for {q.unit}"
    | .whichAll | .whichOne =>
      let some s := q.sort | throw s!"InvalidInput: invalid question fields for {q.unit}"
      unless D.E.sorts.contains s do throw s!"UnknownSymbol: sort {s}"
      if q.domain.length > 16 then throw "ResourceLimit: alternatives"
      if q.domain.length < 2 then throw s!"InvalidInput: invalid question fields for {q.unit}"
      for a in q.domain do
        match D.E.constants a with
        | none => throw s!"UnknownAlternative: {q.unit}, {a}"
        | some t => unless t == s do throw s!"AlternativeSort: {q.unit}"
      if let some a := firstDup q.domain then throw s!"DuplicateAlternative: {q.unit}, {a}"
      typeDiagnostic D.E [s] q.body
      unless q.body.check D.E [s] do throw s!"InvalidInput: invalid question fields for {q.unit}"
    | .follows =>
      let some i := q.query | throw s!"InvalidInput: invalid question fields for {q.unit}"
      unless D.queries.any (·.id == i) do throw s!"QueryMismatch: {q.unit}"
    | .reading =>
      let some (_, v) := q.readingSet | throw s!"InvalidInput: invalid question fields for {q.unit}"
      unless 1 ≤ v do throw s!"InvalidInput: invalid question fields for {q.unit}"
  for (u, a) in D.asserted do
    unless a.check D.E [] do throw s!"InvalidInput: ill-typed asserted unit {u}"
  for N in D.norms do
    for m in N.over do
      if D.commands.any (fun c => "cmd-" ++ c.unit == m) then throw s!"UnknownRule: rule {m}"
  validate (policy D)
  for qr in D.queries do
    for i in qr.premiseIds do
      unless D.asserted.any (·.1 == i) do throw s!"QueryMismatch: {qr.id}"
    typeDiagnostic D.E [] qr.target
    unless qr.target.check D.E [] do throw s!"QueryMismatch: {qr.id}"
    unless decide (qr.premises = pinnedAsserted D qr) do throw s!"QueryMismatch: {qr.id}"

/-- `checkSpeech`, then the conditions of the metatheory. -/
def validateSpeech (D : SpeechDoc) : Except String Unit :=
  match checkSpeech D with
  | .error e => .error e
  | .ok () => if semanticSpeech D then .ok () else .error "InvalidInput: speech-act document is not well-formed"

/-- 4.1, executable, with the diagnostics of section 7; includes `Norms.WellFormed (policy D)`. -/
def WellFormedSpeech (D : SpeechDoc) : Bool := match validateSpeech D with
  | .ok () => true
  | .error _ => false

theorem semanticSpeech_of_wellFormed (D : SpeechDoc) (h : WellFormedSpeech D = true) :
    semanticSpeech D = true := by
  unfold WellFormedSpeech validateSpeech at h
  split at h <;> rename_i heq
  · split at heq
    · cases heq
    · split at heq
      · assumption
      · cases heq
  · cases h

/-- The facts about a well-formed speech-act document that the proofs use. -/
structure ValidSpeech (D : SpeechDoc) : Prop where
  scope : scopeOk D = true
  commands : ∀ c ∈ D.commands, commandOk D c = true
  noOver : ∀ N ∈ D.norms, ∀ c ∈ D.commands, "cmd-" ++ c.unit ∉ N.over
  questions : ∀ q ∈ D.questions, questionOk D q = true
  queries : ∀ qr ∈ D.queries, queryOk D qr = true
  asserted : ∀ u ∈ D.asserted, u.2.check D.E [] = true
  policy : WellFormed (policy D) = true

theorem validSpeech_of_wellFormed (D : SpeechDoc) (h : WellFormedSpeech D = true) : ValidSpeech D := by
  have h := semanticSpeech_of_wellFormed D h
  simp only [semanticSpeech, Bool.and_eq_true, List.all_eq_true] at h
  obtain ⟨⟨⟨⟨⟨⟨hs, hc⟩, hn⟩, hq⟩, hr⟩, ha⟩, hp⟩ := h
  refine ⟨hs, hc, fun N hN c hc' hm => ?_, hq, hr, ha, hp⟩
  simp only [noCommandOver, List.all_eq_true, Bool.not_eq_true', List.any_eq_false, beq_iff_eq] at hn
  exact hn N hN _ hm c hc' rfl

end VE.SpeechActs
