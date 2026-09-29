import VE.Alternatives.Validate

/-! Risk documents (docs/spec/risk.md 1.1, 1.2, 4.1, 4.5 and 7.1).

A `RiskDoc` is an alternatives document over an environment carrying the
`risk` block. `riskEnv R` is `E_risk` (1.2): `E` plus the fresh severity sort,
one constant per class and the three generated predicates
`risk__might_lead_to(action, harm)`, `risk__class(harm, s)` and
`risk__more_severe(s, s)`. Guards, carve-outs and assertion units may also
mention the two defined words `risk__or_worse(harm, s)` and
`risk__less_worst(action, action)`; `riskInline` replaces them by their fixed
bodies (4.5, capture-avoiding, through W1's `inst`) and leaves alt's four
profile words for alt's own `inline`. `toAlt R` is the alternatives document
over `E_risk` whose tree has the risk words inlined.

`WellFormedRisk` is the executable check of 4.1 with the diagnostics of 6. Its
last step is the Boolean `riskSemanticCheck`, from which the facts the proofs
use (`RiskValid`) follow, as alt's `altSemanticCheck` gives `AltValid`. The
checks that need the complete declaration inventory (a symbol beginning with
`risk__`, a harm constant without a class) run in the wire decoder, which has
the vocabulary lists; `WellFormedRisk` checks the names the proofs use. -/
namespace VE.Risk
open VE.Norms
open VE.Alternatives (AltEnv AltDoc Row inlineTree WellFormedAlt profileDef profileWords)

inductive Unexamined | possible | ruledOutBy (decider : String) | ruledOutByChooser
  deriving DecidableEq, Repr

inductive Combination | latest | hull | intersection
  deriving DecidableEq, Repr

structure SeverityDecl where
  sort : String
  /-- 1 to 16, distinct -/
  classes : List String
  /-- declared "more severe" edges -/
  edges : List (String × String)
  unranked : List (String × String)
  decidedBy : String
  deriving DecidableEq, Repr

structure RiskEnv where
  severity : SeverityDecl
  /-- `(harm constant, class)` -/
  harmClasses : List (String × String)
  unexamined : Unexamined
  alwaysPossible : List String
  combination : Option Combination
  alternativeKinds : List (String × String)
  requiredAlternatives : List (String × List String)
  /-- `(kind, tag)` -/
  quantityKinds : List (String × String)
  requiredEstimators : List (String × List String)
  useAllRecorded : Bool
  deriving DecidableEq, Repr

structure RiskDoc where
  /-- the complete original environment, without the generated vocabulary -/
  E : VE.Environment
  /-- W6 tags with the exponent `k` of their scale `10^k` -/
  units : List (String × Nat)
  lits : List String
  /-- fulfilments with `excludes` expanded over `risk__might_lead_to` -/
  alt : AltEnv
  risk : RiskEnv
  /-- guards and carve-outs may mention alt's four words and the two risk words -/
  T : Tree
  /-- active base assertion units, risk words inlined -/
  Γ : List VE.Formula

def mightName : String := "risk__might_lead_to"
def classPred : String := "risk__class"
def moreSeverePred : String := "risk__more_severe"
def orWorseName : String := "risk__or_worse"
def lessWorstName : String := "risk__less_worst"
def riskWords : List String := [orWorseName, lessWorstName]
def generatedPreds : List String := [mightName, classPred, moreSeverePred]

def RiskDoc.sev (R : RiskDoc) : String := R.risk.severity.sort
def RiskDoc.classes (R : RiskDoc) : List String := R.risk.severity.classes

/-- `E_risk` (1.2): `E` plus the fresh sort, the class constants and the three predicates. -/
def riskEnv (R : RiskDoc) : VE.Environment where
  sorts := R.E.sorts ++ [R.sev]
  predicates := fun p =>
    if p = mightName then some [R.alt.action, R.alt.harm]
    else if p = classPred then some [R.alt.harm, R.sev]
    else if p = moreSeverePred then some [R.sev, R.sev]
    else R.E.predicates p
  constants := fun c => if c ∈ R.classes then some R.sev else R.E.constants c

/-! ## The defined words (4.5) -/

/-- `or_worse(h, c) := ∃s. class(h, s) ∧ (s = c ∨ more_severe(s, c))`, context `[harm, s].reverse`. -/
def orWorseF (R : RiskDoc) : VE.Formula :=
  .ex R.sev (.and (.binary classPred (.var 2) (.var 0))
    (.or (.eq (.var 0) (.var 1)) (.binary moreSeverePred (.var 0) (.var 1))))

/-- `less_worst(a′, a) := ∃h s. might(a, h) ∧ class(h, s) ∧ ∀h′. might(a′, h′) → ∃s′. class(h′, s′) ∧
more_severe(s, s′)`, context `[action, action].reverse` (index 0 is `a`, index 1 is `a′`). -/
def lessWorstF (R : RiskDoc) : VE.Formula :=
  .ex R.alt.harm (.ex R.sev (.and (.binary mightName (.var 2) (.var 1))
    (.and (.binary classPred (.var 1) (.var 0))
      (.all R.alt.harm (.implies (.binary mightName (.var 4) (.var 0))
        (.ex R.sev (.and (.binary classPred (.var 1) (.var 0)) (.binary moreSeverePred (.var 2) (.var 0)))))))))

/-- A risk word's argument sorts (in argument order) and body. -/
def riskWordDef (R : RiskDoc) (p : String) : Option (List String × VE.Formula) :=
  if p = orWorseName then some ([R.alt.harm, R.sev], orWorseF R)
  else if p = lessWorstName then some ([R.alt.action, R.alt.action], lessWorstF R)
  else none

/-- `riskEnv R` plus alt's four profile words and the two risk words. -/
def riskExtEnv (R : RiskDoc) : VE.Environment :=
  { riskEnv R with predicates := fun p => match riskWordDef R p with
      | some (ss, _) => some ss
      | none => match profileDef R.alt p with
        | some (ss, _) => some ss
        | none => (riskEnv R).predicates p }

/-- Replace every risk-word atom by its body at the atom's arguments; nothing else is replaced. -/
def riskInline (R : RiskDoc) : VE.Formula → VE.Formula
  | .top => .top
  | .bottom => .bottom
  | .unary p t => .unary p t
  | .binary p t u => match riskWordDef R p with
    | some (_, F) => inst [u, t] F
    | none => .binary p t u
  | .eq t u => .eq t u
  | .not a => .not (riskInline R a)
  | .and a b => .and (riskInline R a) (riskInline R b)
  | .or a b => .or (riskInline R a) (riskInline R b)
  | .implies a b => .implies (riskInline R a) (riskInline R b)
  | .all s a => .all s (riskInline R a)
  | .ex s a => .ex s (riskInline R a)

def riskInlineNode (R : RiskDoc) (N : Node) : Node :=
  { N with guard := riskInline R N.guard, carveOuts := N.carveOuts.map (riskInline R) }

def riskInlineTree (R : RiskDoc) : Tree := { R.T with nodes := R.T.nodes.map (riskInlineNode R) }

/-- The two words interpreted by their bodies, same carrier. -/
def withRiskDefinitions (R : RiskDoc) (S : VE.Structure.{u}) : VE.Structure.{u} :=
  { S with relation := fun p vs => match riskWordDef R p with
      | some (ss, F) => VE.TupleTyped S ss vs ∧ F.denote S (tupleVal vs)
      | none => S.relation p vs }

def toAlt (R : RiskDoc) : AltDoc := ⟨riskEnv R, R.lits, R.alt, riskInlineTree R, R.Γ⟩

/-! ## The severity order (4.1(3)) -/

/-- One closing step over the declared classes: `(a, b)` when `a → b` or `a → m → b`. -/
def closeStep (cs : List String) (rel : List (String × String)) : List (String × String) :=
  cs.flatMap fun a => cs.filterMap fun b =>
    if rel.contains (a, b) || cs.any (fun m => rel.contains (a, m) && rel.contains (m, b)) then some (a, b) else none

def closeIter (cs : List String) : Nat → List (String × String) → List (String × String)
  | 0, rel => rel
  | n + 1, rel => closeIter cs n (closeStep cs rel)

/-- The transitive closure of the declared edges, in class order (each step doubles the path length). -/
def closure (R : RiskDoc) : List (String × String) :=
  closeIter R.classes (R.classes.length + 1) R.risk.severity.edges

def closureIrrefl (R : RiskDoc) : Bool := (closure R).all (fun p => p.1 != p.2)
def closureTrans (R : RiskDoc) : Bool :=
  (closure R).all fun p => (closure R).all fun q => p.2 != q.1 || (closure R).contains (p.1, q.2)

/-- The classes of the harm constant `h`. -/
def classOf (R : RiskDoc) (h : String) : Option String := (R.risk.harmClasses.find? (·.1 == h)).map Prod.snd

/-- The harm constants, in declaration order. -/
def harms (R : RiskDoc) : List String := R.risk.harmClasses.map Prod.fst

/-! ## Well-formedness (4.1) -/

/-- The conditions the proofs use, as one Boolean (reached after every diagnostic). -/
def riskSemanticCheck (R : RiskDoc) : Bool :=
  WellFormedAlt (toAlt R) &&
  !R.E.sorts.contains R.sev &&
  (generatedPreds ++ riskWords).all (fun p => R.E.predicates p == none) &&
  R.classes.all (fun c => R.E.constants c == none && R.E.predicates c == none && !R.E.sorts.contains c) &&
  decide R.classes.Nodup && !R.classes.isEmpty && R.classes.length ≤ 16 &&
  !(generatedPreds ++ riskWords).contains R.sev &&
  R.T.regulated.all (fun r => !(generatedPreds ++ riskWords).contains r.name) &&
  closureIrrefl R && closureTrans R &&
  (closure R).all (fun p => R.classes.contains p.1 && R.classes.contains p.2) &&
  R.risk.harmClasses.all (fun p => R.E.constants p.1 == some R.alt.harm && R.classes.contains p.2) &&
  decide (harms R).Nodup &&
  R.alt.outcomes == .signed &&
  (VE.Alternatives.roleNames R.alt).all (fun p => R.E.predicates p != none) &&
  [R.alt.chooser, R.alt.action, R.alt.harm].all R.E.sorts.contains &&
  R.lits.all (fun l => R.E.constants l != some R.sev && !R.classes.contains l) &&
  R.T.definitions.all (fun d => !(generatedPreds ++ riskWords).contains d.name)

def classPairs (R : RiskDoc) : List (String × String) := R.classes.flatMap fun a => R.classes.map (a, ·)

/-- Clauses 2 to 6 of 4.1, with the diagnostics of 6. -/
def checkRiskBlock (R : RiskDoc) : Except String Unit := do
  let s := R.risk.severity
  if R.E.sorts.contains s.sort then throw s!"RiskSeverityNotFresh: {s.sort}"
  for p in generatedPreds ++ riskWords do
    if R.E.predicates p != none || R.E.constants p != none || R.E.sorts.contains p then throw s!"RiskReserved: {p}"
  for c in s.classes do
    if R.E.constants c != none || R.E.predicates c != none || R.E.sorts.contains c then throw s!"RiskReserved: {c}"
  if s.classes.isEmpty || s.classes.length > 16 then throw "ResourceLimit: risk classes"
  let mut seen : List String := []
  for c in s.classes do
    if seen.contains c then throw s!"DuplicateDeclaration: risk class {c}"
    seen := seen ++ [c]
  for (a, b) in s.edges ++ s.unranked do
    for c in [a, b] do
      unless s.classes.contains c do throw s!"UnknownSymbol: risk.severity {c}"
  match VE.Route.dependencyOrder (s.classes.map fun c => ⟨c, (s.edges.filter (·.1 == c)).map Prod.snd⟩) with
  | .error e => throw e
  | .ok _ => pure ()
  for (a, b) in s.unranked do
    if (closure R).contains (a, b) || (closure R).contains (b, a) then throw s!"RiskUnrankedAgainstOrder: {a}, {b}"
  let mut hs : List String := []
  for (h, c) in R.risk.harmClasses do
    unless R.E.constants h == some R.alt.harm do throw s!"UnknownSymbol: risk.harm_classes {h}"
    unless s.classes.contains c do throw s!"UnknownSymbol: risk.severity {c}"
    if hs.contains h then throw s!"HarmTwoClasses: {h}"
    hs := hs ++ [h]
  for c in R.risk.alwaysPossible do
    unless s.classes.contains c do throw s!"UnknownSymbol: risk.always_possible {c}"
  for (_, ks) in R.risk.requiredAlternatives do
    for k in ks do
      unless (R.risk.alternativeKinds.map Prod.fst).contains k do throw "InvalidInput: risk.required_alternatives"
  for (w, _) in R.risk.requiredAlternatives do
    unless (R.risk.alternativeKinds.map Prod.fst).contains w do throw "InvalidInput: risk.required_alternatives"
  for (_, t) in R.risk.quantityKinds do
    unless (R.units.map Prod.fst).contains t do throw s!"UnknownSymbol: unit {t}"
  for (k, _) in R.risk.requiredEstimators do
    unless (R.risk.quantityKinds.map Prod.fst).contains k do throw "InvalidInput: risk.required_estimators"
  unless R.alt.outcomes == .signed do throw "RiskOutcomes: risk@0 requires outcomes signed"

/-- The number of AST nodes a formula may have after inlining. -/
def maxNodes : Nat := 10000

/-- Clause 7: `T` over `E_risk` extended by the six words, and the inlining limit. -/
def checkRiskTyping (R : RiskDoc) : Except String Unit := do
  for N in R.T.nodes do
    if let some r := VE.Alternatives.findReg R.T N.pred then
      for φ in N.guard :: N.carveOuts do
        typeDiagnostic (riskExtEnv R) r.sorts.reverse φ
        unless φ.check (riskExtEnv R) r.sorts.reverse do throw s!"InvalidInput: ill-typed rule {N.name}"
        if VE.Bridge.formulaNodes (riskInline R φ) > maxNodes then
          throw s!"ResourceLimit: risk inlining of rule {N.name}"

/-- 4.1 in the diagnostic order of 6: the block, the rules over the extended environment, then
alt's well-formedness of `toAlt R`. -/
def checkRisk (R : RiskDoc) : Except String Unit := do
  checkRiskBlock R
  checkRiskTyping R
  VE.Alternatives.validateAlt (toAlt R)

def validateRisk (R : RiskDoc) : Except String Unit :=
  match checkRisk R with
  | .error e => .error e
  | .ok () => if riskSemanticCheck R then .ok () else .error "InvalidInput: risk block is not well-formed"

def WellFormedRisk (R : RiskDoc) : Bool := match validateRisk R with
  | .ok () => true
  | .error _ => false

theorem riskSemanticCheck_of_wellFormed (R : RiskDoc) (h : WellFormedRisk R = true) :
    riskSemanticCheck R = true := by
  unfold WellFormedRisk validateRisk at h
  split at h <;> rename_i heq
  · split at heq
    · cases heq
    · split at heq
      · assumption
      · cases heq
  · cases h

/-- The conditions `riskSemanticCheck` records, as propositions. -/
structure RiskValid (R : RiskDoc) : Prop where
  alt : WellFormedAlt (toAlt R) = true
  fresh : R.sev ∉ R.E.sorts
  reserved : ∀ p ∈ generatedPreds ++ riskWords, R.E.predicates p = none
  classesFresh : ∀ c ∈ R.classes, R.E.constants c = none ∧ R.E.predicates c = none ∧ c ∉ R.E.sorts
  nodup : R.classes.Nodup
  nonempty : R.classes ≠ []
  bound : R.classes.length ≤ 16
  sevName : R.sev ∉ generatedPreds ++ riskWords
  regulated : ∀ r ∈ R.T.regulated, r.name ∉ generatedPreds ++ riskWords
  irrefl : ∀ p ∈ closure R, p.1 ≠ p.2
  trans : ∀ p ∈ closure R, ∀ q ∈ closure R, p.2 = q.1 → (p.1, q.2) ∈ closure R
  closureClasses : ∀ p ∈ closure R, p.1 ∈ R.classes ∧ p.2 ∈ R.classes
  harmClasses : ∀ p ∈ R.risk.harmClasses, R.E.constants p.1 = some R.alt.harm ∧ p.2 ∈ R.classes
  harmsNodup : (harms R).Nodup
  signed : R.alt.outcomes = .signed
  roles : ∀ p ∈ VE.Alternatives.roleNames R.alt, R.E.predicates p ≠ none
  sorts : R.alt.chooser ∈ R.E.sorts ∧ R.alt.action ∈ R.E.sorts ∧ R.alt.harm ∈ R.E.sorts
  lits : ∀ l ∈ R.lits, R.E.constants l ≠ some R.sev ∧ l ∉ R.classes
  definitions : ∀ d ∈ R.T.definitions, d.name ∉ generatedPreds ++ riskWords

theorem riskValid_of_wellFormed (R : RiskDoc) (h : WellFormedRisk R = true) : RiskValid R := by
  have hc := riskSemanticCheck_of_wellFormed R h
  simp only [riskSemanticCheck, closureIrrefl, closureTrans, Bool.and_eq_true, Bool.not_eq_true',
    decide_eq_true_eq, beq_iff_eq, List.all_eq_true, List.contains_iff_mem, List.isEmpty_eq_false_iff,
    and_assoc] at hc
  obtain ⟨hwa, hfr, hres, hcf, hnd, hne, hbd, hsn, hreg, hirr, htr, hcc, hhc, hhn, hsg, hrole, hsrt, hlit, hdef⟩ := hc
  refine ⟨hwa, ?_, hres, fun c hc' => ?_, hnd, ?_, hbd, ?_, fun r hr => ?_, fun p hp => ?_, fun p hp q hq => ?_,
    fun p hp => ?_, fun p hp => ?_, hhn, hsg, fun p hp => ?_, ?_, fun l hl => ?_, fun d hd => ?_⟩
  · simpa using hfr
  · simpa using hcf c hc'
  · simpa using hne
  · simpa using hsn
  · simpa using hreg r hr
  · simpa using hirr p hp
  · have := htr p hp q hq
    simp only [Bool.or_eq_true, bne_iff_ne, ne_eq, List.contains_iff_mem] at this
    intro he
    rcases this with h1 | h1
    · exact absurd he h1
    · simpa using h1
  · simpa using hcc p hp
  · simpa using hhc p hp
  · simpa using hrole p hp
  · simpa using hsrt
  · simpa using hlit l hl
  · simpa using hdef d hd

theorem riskEnv_might (R : RiskDoc) : (riskEnv R).predicates mightName = some [R.alt.action, R.alt.harm] := by
  simp [riskEnv]

theorem riskEnv_class (R : RiskDoc) : (riskEnv R).predicates classPred = some [R.alt.harm, R.sev] := by
  simp [riskEnv, classPred, mightName]

theorem riskEnv_ms (R : RiskDoc) : (riskEnv R).predicates moreSeverePred = some [R.sev, R.sev] := by
  simp [riskEnv, classPred, mightName, moreSeverePred]

theorem riskEnv_sev (R : RiskDoc) : R.sev ∈ (riskEnv R).sorts := by simp [riskEnv]

end VE.Risk
