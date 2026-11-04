import VE.Weighing.Tree
import VE.NormDefaults.Packs
import VE.NormDefaults.Check

/-!
# Weighing's premises and checks (docs/spec/weighing.md 1.4-1.6, 5)

`Weigh_T := Str_T ++ Dec_T ++ Grant_T`, each premise with its label and the request path of its entry; the one
premise generator `condPremise` (a grant premise is its necessary `.off` case); the propositional implication check;
`checkWeigh` (weighing.md 1.6, steps 3 to 7) and `WellFormedWeigh`. The theorems of weighing.md 5 follow.
Each condition is the formula the block decoder (WG-3) gives: today W1's budgeted decoder, since AT-3a's guard
node is not on `main`.
-/

namespace VE.Weighing
open VE.Norms VE.SoftNorms

abbrev RequestPath := VE.NormDefaults.Packs.RequestPath

def blockPath : RequestPath := ["environment", "vocabulary", "weighing"]

/-- `Str_T`: one premise per `outweighs` decision of a strict pair, in `outweighsTriples` order; its origin is the
    first `always` edge (block order) through which the pair is strict. -/
def strengthEntries (Wd : WeighDoc) : List (String × VE.Formula × RequestPath) :=
  (outweighsTriples Wd.D).filterMap (fun (a, L, H) =>
    match Wd.W.always.zipIdx.find? (fun (e, _) => (rankOrder Wd).atLeast H e.1 && (rankOrder Wd).atLeast e.2 L) with
    | some (_, i) => some (s!"weigh:strength:{H}:{L}:{a}",
        bindAll (actSortsOf Wd.D a) (.not (outweighsF Wd.D a L H)), blockPath ++ ["always", toString i])
    | none => none)

/-- The one premise generator (soft's `excPremisesOf` shape). -/
def condPremise (Wd : WeighDoc) (c : CondDecl) : VE.Formula :=
  match c.kind with
  | .sufficient => bindAll (targetSorts Wd c.target) (.implies c.condition (targetF Wd c.target))
  | .necessary => bindAll (targetSorts Wd c.target) (.implies (targetF Wd c.target) c.condition)

/-- `Dec_T`, in block order. -/
def condEntries (Wd : WeighDoc) : List (String × VE.Formula × RequestPath) :=
  Wd.W.conditions.zipIdx.map (fun (c, i) =>
    (s!"weigh:condition:{i}:{c.kind.label}", condPremise Wd c, blockPath ++ ["conditions", toString i]))

def grantEdges (Wd : WeighDoc) (n : String) : List (String × String) :=
  (Wd.W.grants.filter (·.rule == n)).map (fun g => (g.party, g.grantor))

/-- `ρ` is reached from `π` through the grants on rule `n`: `π`'s grantor, that grantor's grantor, … -/
def grantReach (Wd : WeighDoc) (n π ρ : String) : Bool := VE.Closure.reachEval .plus (grantEdges Wd n) π ρ

/-- The parties `π`'s switch on rule `n` is granted through, in declared party order, `π` excluded (on an accepted
    document `π` never reaches itself: grant cycles are refused, 4.5). -/
def grantedThrough (Wd : WeighDoc) (n π : String) : List String :=
  Wd.D.soft.parties.filter (fun ρ => ρ != π && grantReach Wd n π ρ)

/-- `Grant_T` as necessary `.off` conditions on the grantee's switch (debate E3): the grant itself, then for each
    party the switch is granted through, that party's necessary switch conditions and that party's own grant. -/
def grantConds (Wd : WeighDoc) : List (String × CondDecl × RequestPath) :=
  Wd.W.grants.zipIdx.flatMap (fun (g, j) =>
    let tgt := Target.off g.rule g.party
    (s!"weigh:grant:{g.rule}:{g.party}", ⟨tgt, .necessary, atom g.predicate (ruleSorts Wd g.rule)⟩,
        blockPath ++ ["grants", toString j]) ::
    (grantedThrough Wd g.rule g.party).flatMap (fun ρ =>
      (Wd.W.conditions.zipIdx.filterMap (fun (c, i) =>
        if c.target == Target.off g.rule ρ && c.kind == .necessary then
          some (s!"weigh:grant:{g.rule}:{g.party}:condition:{i}", ⟨tgt, .necessary, c.condition⟩,
            blockPath ++ ["conditions", toString i])
        else none)) ++
      (Wd.W.grants.zipIdx.filterMap (fun (g', k) =>
        if g'.rule == g.rule && g'.party == ρ then
          some (s!"weigh:grant:{g.rule}:{g.party}:grant:{ρ}",
            ⟨tgt, .necessary, atom g'.predicate (ruleSorts Wd g.rule)⟩, blockPath ++ ["grants", toString k])
        else none))))

def grantEntries (Wd : WeighDoc) : List (String × VE.Formula × RequestPath) :=
  (grantConds Wd).map (fun (l, c, p) => (l, condPremise Wd c, p))

/-- `Weigh_T := Str_T ++ Dec_T ++ Grant_T`, each premise with its label and the request path of its entry. -/
def weighEntries (Wd : WeighDoc) : List (String × VE.Formula × RequestPath) :=
  strengthEntries Wd ++ condEntries Wd ++ grantEntries Wd

def strengthPremises (Wd : WeighDoc) : List VE.Formula := (strengthEntries Wd).map (·.2.1)
def weighLabelled (Wd : WeighDoc) : List (String × VE.Formula) := (weighEntries Wd).map (fun (l, φ, _) => (l, φ))
def weighOrigins (Wd : WeighDoc) : List (String × RequestPath) := (weighEntries Wd).map (fun (l, _, p) => (l, p))
def weighPremises (Wd : WeighDoc) : List VE.Formula := (weighLabelled Wd).map (·.2)

/-- The decision a target names, as soft's key (profile-composition 1.9: a reader finds a decision by its key). -/
def Target.key : Target → DecisionKey
  | .outweighs a L H => .outweighs a L H
  | .off n π => .off n π

/-- `Pack.conditions` (PK-1's field, profile-composition 1.9): each stated sufficient condition with its decision,
    in block order. Necessary conditions and grants export nothing. -/
def weighConditions (Wd : WeighDoc) : List (DecisionKey × VE.Formula) :=
  Wd.W.conditions.filterMap (fun c => if c.kind == .sufficient then some (c.target.key, c.condition) else none)

def atomsOf : VE.Formula → List VE.Formula
  | .unary p t => [.unary p t]
  | .binary p t w => [.binary p t w]
  | .eq t w => [.eq t w]
  | .not a => atomsOf a
  | .and a b | .or a b | .implies a b => atomsOf a ++ atomsOf b
  | _ => []

/-- A formula read propositionally: each distinct atom is a variable. -/
def evalProp (v : VE.Formula → Bool) : VE.Formula → Bool
  | .top => true
  | .bottom => false
  | .unary p t => v (.unary p t)
  | .binary p t w => v (.binary p t w)
  | .eq t w => v (.eq t w)
  | .not a => !evalProp v a
  | .and a b => evalProp v a && evalProp v b
  | .or a b => evalProp v a || evalProp v b
  | .implies a b => !evalProp v a || evalProp v b
  | .all _ _ | .ex _ _ => false

def subsetsOf {α : Type} : List α → List (List α)
  | [] => [[]]
  | x :: xs => (subsetsOf xs).map (x :: ·) ++ subsetsOf xs

def maxPropAtoms : Nat := 12

def propAtoms (a b : VE.Formula) : List VE.Formula := (atomsOf a ++ atomsOf b).eraseDups

/-- `a → b` holds under every truth assignment to their atoms. Sound (`propImplies_sound`), not complete: equality
    and definitions are not read (W-θ12). Decided exactly; it never searches. -/
def propImplies (a b : VE.Formula) : Bool :=
  VE.Norms.Formula.qfree a && VE.Norms.Formula.qfree b && decide ((propAtoms a b).length ≤ maxPropAtoms) &&
    (subsetsOf (propAtoms a b)).all (fun t =>
      !evalProp (fun φ => t.contains φ) a || evalProp (fun φ => t.contains φ) b)

def targetCheck (Wd : WeighDoc) (t : Target) : Except String Unit := do
  match t with
  | .outweighs a _ _ => if Wd.split.preds.any (·.2.1 == a) then throw (VE.Acts.splitRefusal "act" a)
  | .off n _ => if Wd.split.rules.any (·.2.1 == n) then throw (VE.Acts.splitRefusal "rule" n)
  unless targetExists Wd t do throw s!"NoSuchDecision: {renderTarget t}"

/-- Section 4, steps 3 to 7, in order. -/
def checkWeigh (Wd : WeighDoc) : Except String Unit := do
  let D := Wd.D
  for e in Wd.W.always do
    unless D.soft.outranks.contains e do throw s!"StrengthOnUndeclaredEdge: {e.1}, {e.2}"
    if Wd.W.always.count e > 1 then throw s!"DuplicateDeclaration: strength {e.1}, {e.2}"
  for (c, i) in Wd.W.conditions.zipIdx do
    targetCheck Wd c.target
    match c.target, c.kind with
    | .off _ _, .sufficient => throw s!"InvalidInput: condition {i} on a switch must be necessary"
    | .outweighs _ L H, _ =>
      if strictPair Wd H L then throw s!"ConditionOnStrictPair: {renderTarget c.target}"
    | _, _ => pure ()
    let Γ := (targetSorts Wd c.target).reverse
    typeDiagnostic D.E Γ c.condition
    unless c.condition.check D.E Γ do throw s!"InvalidInput: ill-typed condition {i}"
    if let some q := (preds c.condition).find? (fun q => definedOrRegulated D q || reservedPredicate q) then
      throw s!"InvalidInput: condition {i} mentions {q}"
    unless VE.Norms.Formula.qfree c.condition do throw s!"InvalidInput: condition {i} is not quantifier-free"
  for (f, i) in Wd.W.factors.zipIdx do
    targetCheck Wd f.target
    unless f.factors.length ≤ 16 && f.factors.all (·.utf8ByteSize ≤ 200) do
      throw s!"InvalidInput: invalid factors {i}"
  for g in Wd.W.grants do
    if (Wd.W.grants.filter (fun g' => g'.rule == g.rule && g'.party == g.party)).length > 1 then
      throw s!"DuplicateDeclaration: grant {g.rule}, {g.party}"
    targetCheck Wd (.off g.rule g.party)
    unless targetExists Wd (.off g.rule g.grantor) do
      throw s!"DelegationExceedsGrantor: rule {g.rule}, {g.party}, {g.grantor}"
    unless D.soft.instructionOf.contains (g.predicate, g.grantor) do
      throw s!"GrantNotAttributed: {g.predicate}, {g.grantor}"
    unless D.E.predicates g.predicate == some (ruleSorts Wd g.rule) do
      throw s!"InvalidInput: grant predicate {g.predicate} does not take the arguments of rule {g.rule}"
  for g in Wd.W.grants do
    if grantReach Wd g.rule g.party g.party then throw s!"DelegationCycle: rule {g.rule}, {g.party}"
  for (s, i) in Wd.W.conditions.zipIdx do
    if s.kind == .sufficient then
      for (n, j) in Wd.W.conditions.zipIdx do
        if n.kind == .necessary && n.target == s.target then
          if (propAtoms s.condition n.condition).length > maxPropAtoms then
            throw s!"ResourceLimit: conditions {i}, {j}"
          unless propImplies s.condition n.condition do
            throw s!"ConditionsDisagree: the checker cannot show that condition {i} implies condition {j}"
  for (l, φ) in weighLabelled Wd do
    unless withinLimits φ do throw s!"ResourceLimit: generated weighing premise {l}"

def weighWarnings (Wd : WeighDoc) : List String :=
  if Wd.D.soft.outranking = .strict then Wd.W.always.map (fun e => s!"StrengthInert: {e.1}, {e.2}") else []

def WellFormedWeigh (Wd : WeighDoc) : Bool :=
  WellFormedSoft Wd.D && (match checkWeigh Wd with
    | .ok () => true
    | .error _ => false)

end VE.Weighing
