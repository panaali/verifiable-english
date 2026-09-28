import VE.Norms.Replay

/-! Alternatives documents (docs/spec/alternatives.md 1, 3.1, 4.1, 4.3 and 7.1).

An `AltDoc` is a W1 norm document whose guards and carve-outs may mention the
four profile words `avoidable`, `unavoidable`, `allows`, `prevents`, over an
environment carrying the `alternatives` block (`AltEnv`). The profile words
have fixed bodies over the block's base predicates `available(action, chooser)`
and `leads_to(action, harm)`; `inline` replaces every profile-word atom by its
body (capture-avoiding, through W1's `inst`), and `inlineTree` is the plain W1
`Doc` the route runs on.

Argument orders are fixed once (7): `avoidable` and `unavoidable` take
`(harm, chooser)`, `allows` and `prevents` take `(action, harm)`. A body's
context is its argument list reversed (de Bruijn index 0 is the last argument).

`WellFormedAlt` is the executable check of 4.1 with the diagnostics of 6; its
last step is the Boolean `altSemanticCheck`, from which the facts the proofs use
(`AltValid`) follow, as W1's `semanticCheck` gives `Valid`. -/
namespace VE.Alternatives
open VE.Norms

inductive Outcomes | signed | completeBy (decider : String)
  deriving DecidableEq, Repr

structure Fulfilment where
  /-- obligation-role predicate, first sort = chooser -/
  obligation : String
  /-- context `(action :: remaining sorts of the obligation).reverse`; base predicates only -/
  body : VE.Formula
  deriving DecidableEq, Repr

structure AltEnv where
  chooser : String
  action : String
  harm : String
  /-- `(action, chooser)` -/
  available : String
  /-- `(action, harm)` -/
  leadsTo : String
  outcomes : Outcomes
  /-- `none` = "unstated" -/
  decidedBy : Option String
  /-- `(m, q)`: the W1 permission and obligation meaning "take a" -/
  performed : Option (String × String)
  inaction : Option String
  taken : Option String
  proximate : Option String
  fulfilments : List Fulfilment
  deriving DecidableEq, Repr

structure AltDoc where
  /-- the complete original environment; the role predicates are base predicates of `E` -/
  E : VE.Environment
  lits : List String
  alt : AltEnv
  /-- guards and carve-outs may mention the four profile words; no fulfilment atoms (1.3) -/
  T : Tree
  /-- active base assertion units, inlined; `tableComplete` appended under `completeBy` -/
  Γ : List VE.Formula

/-- 3.3: one signed row of a supplied scenario. -/
structure Row where
  /-- a constant of the action sort -/
  action : String
  /-- a constant of the harm sort -/
  harm : String
  leadsTo : Bool
  support : String
  deriving DecidableEq, Repr

def profileWords : List String := ["avoidable", "unavoidable", "allows", "prevents"]

/-! ## The profile bodies (4.3) -/

/-- `avoidable(h, r) := ∃a. available(a, r) ∧ ¬leads_to(a, h)`, context `[chooser, harm]`. -/
def avoidableF (A : AltEnv) : VE.Formula :=
  .ex A.action (.and (.binary A.available (.var 0) (.var 1)) (.not (.binary A.leadsTo (.var 0) (.var 2))))

/-- `unavoidable(h, r) := (∃a. available(a, r)) ∧ ¬avoidable(h, r)`, context `[chooser, harm]`. -/
def unavoidableF (A : AltEnv) : VE.Formula :=
  .and (.ex A.action (.binary A.available (.var 0) (.var 1))) (.not (avoidableF A))

/-- `allows(a, h) := leads_to(a, h) ∧ ∃r. available(a, r) ∧ avoidable(h, r)`, context `[harm, action]`. -/
def allowsF (A : AltEnv) : VE.Formula :=
  .and (.binary A.leadsTo (.var 1) (.var 0))
    (.ex A.chooser (.and (.binary A.available (.var 2) (.var 0))
      (.ex A.action (.and (.binary A.available (.var 0) (.var 1)) (.not (.binary A.leadsTo (.var 0) (.var 2)))))))

/-- `prevents(a, h) := ¬leads_to(a, h) ∧ ∃r. available(a, r) ∧ ∃a'. available(a', r) ∧ leads_to(a', h)`,
context `[harm, action]`. -/
def preventsF (A : AltEnv) : VE.Formula :=
  .and (.not (.binary A.leadsTo (.var 1) (.var 0)))
    (.ex A.chooser (.and (.binary A.available (.var 2) (.var 0))
      (.ex A.action (.and (.binary A.available (.var 0) (.var 1)) (.binary A.leadsTo (.var 0) (.var 2))))))

/-- A profile word's argument sorts (in argument order) and body. -/
def profileDef (A : AltEnv) (p : String) : Option (List String × VE.Formula) :=
  if p = "avoidable" then some ([A.harm, A.chooser], avoidableF A)
  else if p = "unavoidable" then some ([A.harm, A.chooser], unavoidableF A)
  else if p = "allows" then some ([A.action, A.harm], allowsF A)
  else if p = "prevents" then some ([A.action, A.harm], preventsF A)
  else none

theorem profileDef_isSome {A : AltEnv} {p : String} : (profileDef A p).isSome ↔ p ∈ profileWords := by
  unfold profileDef profileWords
  by_cases h1 : p = "avoidable" <;> by_cases h2 : p = "unavoidable" <;>
    by_cases h3 : p = "allows" <;> by_cases h4 : p = "prevents" <;> simp_all

/-- `E` plus the four profile words with their fixed sorts (4.1(2): no collision). -/
def extEnv (A : AltDoc) : VE.Environment :=
  { A.E with predicates := fun p => match profileDef A.alt p with
      | some (ss, _) => some ss
      | none => A.E.predicates p }

/-! ## Inlining -/

/-- Replace every profile-word atom by its body at the atom's arguments (W1's
capture-avoiding `inst`); nothing else is replaced. -/
def inlineWith (A : AltEnv) : VE.Formula → VE.Formula
  | .top => .top
  | .bottom => .bottom
  | .unary p t => .unary p t
  | .binary p t u => match profileDef A p with
    | some (_, F) => inst [u, t] F
    | none => .binary p t u
  | .eq t u => .eq t u
  | .not a => .not (inlineWith A a)
  | .and a b => .and (inlineWith A a) (inlineWith A b)
  | .or a b => .or (inlineWith A a) (inlineWith A b)
  | .implies a b => .implies (inlineWith A a) (inlineWith A b)
  | .all s a => .all s (inlineWith A a)
  | .ex s a => .ex s (inlineWith A a)

def inline (A : AltDoc) : VE.Formula → VE.Formula := inlineWith A.alt

def inlineNode (A : AltDoc) (N : Node) : Node :=
  { N with guard := inline A N.guard, carveOuts := N.carveOuts.map (inline A) }

/-- `⟨E, lits, T with every guard and carve-out inlined⟩`, the W1 document of the route. -/
def inlineTree (A : AltDoc) : Doc :=
  ⟨A.E, A.lits, { A.T with nodes := A.T.nodes.map (inlineNode A) }⟩

/-- `S` plus the four profile words interpreted by their bodies (same carrier). -/
def withDefinitions (A : AltDoc) (S : VE.Structure.{u}) : VE.Structure.{u} :=
  { S with relation := fun p vs => match profileDef A.alt p with
      | some (ss, F) => VE.TupleTyped S ss vs ∧ F.denote S (tupleVal vs)
      | none => S.relation p vs }

/-! ## Well-formedness (4.1) -/

def roleSorts (A : AltEnv) : List (String × String × List String) :=
  [("available", A.available, [A.action, A.chooser]), ("leads_to", A.leadsTo, [A.action, A.harm])] ++
    (A.inaction.map (fun p => ("inaction", p, [A.action]))).toList ++
    (A.taken.map (fun p => ("taken", p, [A.action]))).toList ++
    (A.proximate.map (fun p => ("proximate", p, [A.action, A.harm]))).toList

/-- The regulated declaration named `n`. -/
def findReg (T : Tree) (n : String) : Option Regulated := T.regulated.find? (·.name == n)

/-- The sorts of an obligation after the chooser (`restSorts`, 7.1). -/
def restSorts (A : AltDoc) (f : Fulfilment) : List String :=
  match findReg A.T f.obligation with
  | some r => r.sorts.tail
  | none => []

def performedOk (A : AltDoc) : Bool :=
  match A.alt.performed with
  | none => true
  | some (m, q) => match findReg A.T m, findReg A.T q with
    | some rm, some rq => rm.role == .permission && rm.sorts == [A.alt.action] &&
        rq.role == .obligation && rq.sorts == [A.alt.action] && rq.permission == some m
    | _, _ => false

def fulfilmentOk (A : AltDoc) (f : Fulfilment) : Bool :=
  match findReg A.T f.obligation with
  | some r => r.role == .obligation && r.sorts.head? == some A.alt.chooser &&
      (r.sorts.length == 1 || r.sorts.length == 2) &&
      (A.alt.performed.all (fun mq => mq.2 != f.obligation)) &&
      f.body.check (envAt (inlineTree A) 0) (A.alt.action :: r.sorts.tail).reverse
  | none => false

/-- The conditions the proofs use, as one Boolean (reached after every diagnostic). -/
def altSemanticCheck (A : AltDoc) : Bool :=
  let E0 := envAt (inlineTree A) 0
  WellFormed (inlineTree A) &&
  [A.alt.chooser, A.alt.action, A.alt.harm].all A.E.sorts.contains &&
  A.alt.chooser != A.alt.action && A.alt.chooser != A.alt.harm && A.alt.action != A.alt.harm &&
  profileWords.all (fun w => A.E.predicates w == none) &&
  (roleSorts A.alt).all (fun (_, p, ss) => E0.predicates p == some ss) &&
  performedOk A &&
  A.alt.fulfilments.all (fulfilmentOk A) &&
  A.Γ.all (fun a => a.check E0 [])

def sortTuple (ss : List String) : String := "(" ++ ", ".intercalate ss ++ ")"

/-- Clause 2: the sorts, reserved names and role predicates, with the diagnostics of 6. -/
def checkBlock (A : AltDoc) : Except String Unit := do
  let a := A.alt
  for (role, s) in [("chooser", a.chooser), ("action", a.action), ("harm", a.harm)] do
    unless A.E.sorts.contains s do throw s!"UnknownSymbol: alternatives.{role} {s}"
  unless a.chooser != a.action && a.chooser != a.harm && a.action != a.harm do
    throw "AlternativesSort: sorts must be distinct"
  for w in profileWords do
    if A.E.sorts.contains w || (A.E.predicates w).isSome || (A.E.constants w).isSome then
      throw s!"AlternativesReserved: {w}"
  let layer := regulatedNames A.T ++ A.T.definitions.map Definition.name
  for (role, p, ss) in roleSorts a do
    match A.E.predicates p with
    | none => throw s!"UnknownSymbol: alternatives.{role} {p}"
    | some actual =>
      if layer.contains p then throw s!"AlternativesRegulated: {role} {p}"
      unless actual == ss do throw s!"AlternativesSort: {role} expects {sortTuple ss}"
  -- Clause 3.
  if let some (m, q) := a.performed then
    unless performedOk A do throw s!"AlternativesPerformed: {m}, {q}"

/-- The number of AST nodes of a formula (`ve/limits.py` `MAX_NODES` counts the same). -/
def maxNodes : Nat := 10000

/-- Clause 5: `T` over `E` extended by the profile words. -/
def checkProfileTyping (A : AltDoc) : Except String Unit := do
  for N in A.T.nodes do
    if let some r := findReg A.T N.pred then
      for φ in N.guard :: N.carveOuts do
        typeDiagnostic (extEnv A) r.sorts.reverse φ
        unless φ.check (extEnv A) r.sorts.reverse do throw s!"InvalidInput: ill-typed rule {N.name}"
      for φ in N.guard :: N.carveOuts do
        if VE.Bridge.formulaNodes (inline A φ) > maxNodes then
          throw s!"ResourceLimit: alternatives inlining of rule {N.name}"

/-- Clause 4: fulfilments. -/
def checkFulfilments (A : AltDoc) : Except String Unit := do
  if A.alt.fulfilments.length > 16 then throw "ResourceLimit: fulfilments"
  let mut seen : List String := []
  for f in A.alt.fulfilments do
    if seen.contains f.obligation then throw s!"DuplicateDeclaration: fulfilment {f.obligation}"
    seen := seen ++ [f.obligation]
    if A.alt.performed.any (fun mq => mq.2 == f.obligation) then
      throw s!"FulfilmentOnPerformed: {f.obligation}"
    match findReg A.T f.obligation with
    | none => throw s!"FulfilmentSort: {f.obligation}"
    | some r =>
      unless r.role == .obligation && r.sorts.head? == some A.alt.chooser do
        throw s!"FulfilmentSort: {f.obligation}"
      unless f.body.check (envAt (inlineTree A) 0) (A.alt.action :: r.sorts.tail).reverse do
        throw s!"FulfilmentNotBase: {f.obligation}"

/-- 4.1 in the diagnostic order of 6: the block, the rules over the extended
environment, W1 on the inlined tree, fulfilments, then `Γ_base`. -/
def checkAlt (A : AltDoc) : Except String Unit := do
  checkBlock A
  checkProfileTyping A
  validate (inlineTree A)
  checkFulfilments A
  unless A.Γ.all (fun a => a.check (envAt (inlineTree A) 0) []) do
    throw "InvalidInput: ill-typed alternatives premise"

/-- `checkAlt`, then the conditions of the metatheory (the executable's diagnostic). -/
def validateAlt (A : AltDoc) : Except String Unit :=
  match checkAlt A with
  | .error e => .error e
  | .ok () => if altSemanticCheck A then .ok () else .error "InvalidInput: alternatives block is not well-formed"

def WellFormedAlt (A : AltDoc) : Bool := match validateAlt A with
  | .ok () => true
  | .error _ => false

theorem altSemanticCheck_of_wellFormed (A : AltDoc) (h : WellFormedAlt A = true) :
    altSemanticCheck A = true := by
  unfold WellFormedAlt validateAlt at h
  split at h <;> rename_i heq
  · split at heq
    · cases heq
    · split at heq
      · assumption
      · cases heq
  · cases h

end VE.Alternatives
