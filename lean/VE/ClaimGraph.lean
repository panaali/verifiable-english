import VE.Consequence
import VE.Typing

namespace VE.Graph
universe u

/-- Identity here is the exact name/AST pair; wire hashes are not substituted
for mathematical identity. All claims live under the checker's one environment. -/
structure Claim where
  name : String
  formula : Formula
  deriving DecidableEq, BEq, Repr

structure Edge (Certificate : Type) where
  premises : List String
  certificate : Certificate

/-- `none` explicitly marks an undischarged assumption. A submitted deduction
with invalid or missing evidence is rejected, never converted to an assumption. -/
structure Node (Certificate : Type) where
  claim : Claim
  deduction : Option (Edge Certificate)

/-- Nodes are supplied in topological order, premises before conclusions.
This order is a checked witness, not a trusted promise or a sorting algorithm. -/
structure ClaimGraph (Certificate : Type) where
  nodes : List (Node Certificate)
  root : String

structure Report where
  root : Claim
  assumptions : List Claim
  deriving DecidableEq, BEq, Repr

abbrev CertificatePredicate (Certificate : Type) :=
  Certificate → List Claim → Claim → Prop

/-- The abstract replay contract is a theorem premise, not a global assumption.
It binds evidence to these exact named claims and this exact environment. -/
def CertificateSound (E : Environment) (valid : CertificatePredicate Certificate) : Prop :=
  ∀ certificate premises conclusion, valid certificate premises conclusion →
    Entails.{u} E (premises.map Claim.formula) conclusion.formula

def rank (g : ClaimGraph Certificate) (name : String) : Nat :=
  (g.nodes.map (fun n => n.claim.name)).idxOf name

/-- Every dependency must decrease the submitted topological rank. -/
def acyclicCheck (g : ClaimGraph Certificate) : Bool :=
  g.nodes.all fun n => match n.deduction with
    | none => true
    | some edge => edge.premises.all (fun p => rank g p < rank g n.claim.name)

def uniqueNames (g : ClaimGraph Certificate) : Bool :=
  decide (g.nodes.map (fun n => n.claim.name)).Nodup

/-- An independent directed-edge and nonempty-path relation on claim names. -/
def Dependency (g : ClaimGraph Certificate) (parent child : String) : Prop :=
  ∃ n ∈ g.nodes, n.claim.name = parent ∧
    ∃ edge, n.deduction = some edge ∧ child ∈ edge.premises

inductive Path (g : ClaimGraph Certificate) : String → String → Prop where
  | edge {a b} : Dependency g a b → Path g a b
  | trans {a b c} : Path g a b → Path g b c → Path g a c

def Acyclic (g : ClaimGraph Certificate) : Prop := ∀ name, ¬ Path g name name

def lookup (seen : List Report) (name : String) : Option Report :=
  seen.find? (fun r => r.root.name == name)

/-- Ordered resolution preserves duplicates, and rejects every missing name. -/
def resolve (seen : List Report) : List String → Option (List Report)
  | [] => some []
  | name :: names => do
    let r ← lookup seen name
    let rs ← resolve seen names
    some (r :: rs)

def checkNode (E : Environment) (valid : CertificatePredicate Certificate)
    [∀ c ps r, Decidable (valid c ps r)] (seen : List Report) (node : Node Certificate) :
    Option Report :=
  if node.claim.formula.check E [] then
    match node.deduction with
    | none => some ⟨node.claim, [node.claim]⟩
    | some edge => do
      let children ← resolve seen edge.premises
      if valid edge.certificate (children.map Report.root) node.claim then
        some ⟨node.claim, children.flatMap Report.assumptions⟩
      else none
  else none

def checkNodes (E : Environment) (valid : CertificatePredicate Certificate)
    [∀ c ps r, Decidable (valid c ps r)] :
    List (Node Certificate) → List Report → Option (List Report)
  | [], seen => some seen
  | node :: nodes, seen => do
    let r ← checkNode E valid seen node
    checkNodes E valid nodes (r :: seen)

def check (E : Environment) (valid : CertificatePredicate Certificate)
    [∀ c ps r, Decidable (valid c ps r)] (g : ClaimGraph Certificate) : Option Report := do
  if !uniqueNames g || !acyclicCheck g then none else do
    let seen ← checkNodes E valid g.nodes []
    lookup seen g.root

/-- A named leaf really is an explicitly marked assumption in the submitted graph. -/
def IsAssumption (g : ClaimGraph Certificate) (claim : Claim) : Prop :=
  ∃ node ∈ g.nodes, node.claim = claim ∧ node.deduction = none

/-- Independent specification of the exact ordered leaf list obtained by
unfolding named edges. Shared children and repeated premise references retain
all occurrences; empty-premise deductions contribute no assumptions. -/
inductive Unfolds (g : ClaimGraph Certificate) : Claim → List Claim → Prop where
  | assumption (node : Node Certificate) (member : node ∈ g.nodes)
      (leaf : node.deduction = none) : Unfolds g node.claim [node.claim]
  | deduction (node : Node Certificate) (member : node ∈ g.nodes)
      (edge : Edge Certificate) (submitted : node.deduction = some edge)
      (children : List Report)
      (names : children.map (fun r => r.root.name) = edge.premises)
      (branches : ∀ r ∈ children, Unfolds g r.root r.assumptions) :
      Unfolds g node.claim (children.flatMap Report.assumptions)

/-- The semantic invariant contains both entailment and exact name/AST
provenance. Lists retain their order and multiplicity, including shared leaves. -/
def SoundReport (E : Environment) (g : ClaimGraph Certificate) (r : Report) : Prop :=
  r.root.formula.WellFormed E [] ∧
  (∃ node ∈ g.nodes, node.claim = r.root) ∧
  (∀ leaf ∈ r.assumptions, leaf.formula.WellFormed E [] ∧ IsAssumption g leaf) ∧
  Entails.{u} E (r.assumptions.map Claim.formula) r.root.formula ∧
  Unfolds g r.root r.assumptions

theorem acyclicCheck_dependency (g : ClaimGraph Certificate) (h : acyclicCheck g = true)
    (parent child : String) (hd : Dependency g parent child) : rank g child < rank g parent := by
  obtain ⟨node, hn, he, edge, hd, hm⟩ := hd
  have hc := List.all_eq_true.mp h node hn
  simp only [hd] at hc
  have hr := List.all_eq_true.mp hc child hm
  simpa [he] using hr

theorem path_rank (g : ClaimGraph Certificate) (h : acyclicCheck g = true)
    (parent child : String) (hp : Path g parent child) : rank g child < rank g parent := by
  induction hp with
  | edge hd => exact acyclicCheck_dependency g h _ _ hd
  | trans _ _ ih1 ih2 => omega

theorem acyclicCheck_sound (g : ClaimGraph Certificate) (h : acyclicCheck g = true) :
    Acyclic g := by
  intro name hp
  have := path_rank g h name name hp
  omega

theorem lookup_sound (seen : List Report) (name : String) (r : Report)
    (h : lookup seen name = some r) : r ∈ seen ∧ r.root.name = name := by
  exact ⟨List.mem_of_find?_eq_some h, by simpa using List.find?_some h⟩

/-- Resolving an ordered premise list returns only existing reports and exactly
the requested names, preserving order and repeated references. -/
theorem resolve_sound (seen : List Report) (names : List String) (rs : List Report)
    (h : resolve seen names = some rs) :
    (∀ r ∈ rs, r ∈ seen) ∧ rs.map (fun r => r.root.name) = names := by
  induction names generalizing rs with
  | nil =>
    simp only [resolve, Option.some.injEq] at h
    subst rs
    simp
  | cons name names ih =>
    cases hl : lookup seen name with
    | none => simp only [resolve, hl, bind, Option.bind, reduceCtorEq] at h
    | some r =>
      cases ht : resolve seen names with
      | none => simp only [resolve, hl, ht, bind, Option.bind, reduceCtorEq] at h
      | some tail =>
        simp only [resolve, hl, ht, bind, Option.bind, Option.some.injEq] at h
        subst rs
        obtain ⟨hm, hn⟩ := lookup_sound seen name r hl
        obtain ⟨hi, he⟩ := ih tail ht
        constructor
        · intro x hx
          rcases List.mem_cons.mp hx with rfl | hx
          · exact hm
          · exact hi x hx
        · simp [hn, he]

/-- Each successful local check composes the exact resolved children and keeps
all their undischarged named assumptions. -/
theorem checkNode_sound (E : Environment) (valid : CertificatePredicate Certificate)
    [∀ c ps r, Decidable (valid c ps r)] (certificates : CertificateSound.{u} E valid)
    (g : ClaimGraph Certificate) (seen : List Report)
    (hs : ∀ r ∈ seen, SoundReport.{u} E g r) (node : Node Certificate)
    (hn : node ∈ g.nodes) (r : Report) (h : checkNode E valid seen node = some r) :
    SoundReport.{u} E g r := by
  unfold checkNode at h
  split at h
  next hw =>
    have htyped := (check_iff_wellFormed E [] node.claim.formula).mp hw
    cases hd : node.deduction with
    | none =>
      simp only [hd, Option.some.injEq] at h
      subst r
      refine ⟨htyped, ⟨node, hn, rfl⟩, ?_, ?_, Unfolds.assumption node hn hd⟩
      · intro leaf hl
        simp only [List.mem_singleton] at hl
        subst leaf
        exact ⟨htyped, node, hn, rfl, hd⟩
      · intro S _ hall
        exact hall node.claim.formula (by simp)
    | some edge =>
      cases hc : resolve seen edge.premises with
      | none => simp only [hd, hc, bind, Option.bind, reduceCtorEq] at h
      | some children =>
        simp only [hd, hc, bind, Option.bind] at h
        split at h
        next hv =>
          have he := Option.some.inj h
          subst r
          have hh : ∀ child ∈ children, SoundReport.{u} E g child := by
            intro child hm
            exact hs child ((resolve_sound seen edge.premises children hc).1 child hm)
          refine ⟨htyped, ⟨node, hn, rfl⟩, ?_, ?_, ?_⟩
          · intro leaf hl
            obtain ⟨child, hm, hl⟩ := List.mem_flatMap.mp hl
            exact (hh child hm).2.2.1 leaf hl
          · apply entails_cut (certificates edge.certificate (children.map Report.root) node.claim hv)
            intro premise hp
            obtain ⟨claim, hclaim, he⟩ := List.mem_map.mp hp
            obtain ⟨child, hm, hec⟩ := List.mem_map.mp hclaim
            subst claim
            subst premise
            intro S hS hall
            apply (hh child hm).2.2.2.1 S hS
            intro a ha
            obtain ⟨leaf, hl, he⟩ := List.mem_map.mp ha
            subst a
            apply hall leaf.formula
            apply List.mem_map.mpr
            exact ⟨leaf, List.mem_flatMap.mpr ⟨child, hm, hl⟩, rfl⟩
          · exact Unfolds.deduction node hn edge hd children
              (resolve_sound seen edge.premises children hc).2
              (fun child hm => (hh child hm).2.2.2.2)
        next => contradiction
  next => contradiction

/-- The executable fold preserves the semantic/provenance invariant. -/
theorem checkNodes_sound (E : Environment) (valid : CertificatePredicate Certificate)
    [∀ c ps r, Decidable (valid c ps r)] (certificates : CertificateSound.{u} E valid)
    (g : ClaimGraph Certificate) (nodes : List (Node Certificate))
    (hn : ∀ node ∈ nodes, node ∈ g.nodes) (seen : List Report)
    (hs : ∀ r ∈ seen, SoundReport.{u} E g r) (out : List Report)
    (h : checkNodes E valid nodes seen = some out) : ∀ r ∈ out, SoundReport.{u} E g r := by
  induction nodes generalizing seen with
  | nil =>
    simp only [checkNodes, Option.some.injEq] at h
    subst out
    exact hs
  | cons node nodes ih =>
    cases hc : checkNode E valid seen node with
    | none => simp only [checkNodes, hc, bind, Option.bind, reduceCtorEq] at h
    | some r =>
      simp only [checkNodes, hc, bind, Option.bind] at h
      apply ih (fun n hm => hn n (by simp [hm])) (r :: seen) _ h
      intro x hx
      rcases List.mem_cons.mp hx with rfl | hx
      · exact checkNode_sound E valid certificates g seen hs node (hn node (by simp)) x hc
      · exact hs x hx

/-- P10 for an executable named DAG checker, conditional only on the explicit
valid-certificate contract. Acyclicity, alias uniqueness, exact root identity,
leaf provenance, typing and entailment are all conclusions of acceptance. -/
theorem check_sound (E : Environment) (valid : CertificatePredicate Certificate)
    [∀ c ps r, Decidable (valid c ps r)] (certificates : CertificateSound.{u} E valid)
    (g : ClaimGraph Certificate) (r : Report) (accepted : check E valid g = some r) :
    Acyclic g ∧ (g.nodes.map (fun n => n.claim.name)).Nodup ∧
    r.root.name = g.root ∧ SoundReport.{u} E g r := by
  unfold check at accepted
  split at accepted
  next => contradiction
  next hgood =>
    have hg : uniqueNames g = true ∧ acyclicCheck g = true := by
      simpa using hgood
    cases hn : checkNodes E valid g.nodes [] with
    | none => simp only [hn, bind, Option.bind, reduceCtorEq] at accepted
    | some seen =>
      simp only [hn, bind, Option.bind] at accepted
      obtain ⟨hm, he⟩ := lookup_sound seen g.root r accepted
      exact ⟨acyclicCheck_sound g hg.2, by simpa [uniqueNames] using hg.1, he,
        checkNodes_sound E valid certificates g g.nodes (fun _ h => h) []
          (by simp) seen hn r hm⟩

/-- Direct P10 consequence of the complete acceptance theorem. -/
theorem check_entails (E : Environment) (valid : CertificatePredicate Certificate)
    [∀ c ps r, Decidable (valid c ps r)] (certificates : CertificateSound.{u} E valid)
    (g : ClaimGraph Certificate) (r : Report) (accepted : check E valid g = some r) :
    Entails.{u} E (r.assumptions.map Claim.formula) r.root.formula :=
  (check_sound E valid certificates g r accepted).2.2.2.2.2.2.1

/-- Acceptance reports precisely a leaf list permitted by ordered graph
unfolding; it cannot silently discard a shared or repeated dependency. -/
theorem check_unfolds (E : Environment) (valid : CertificatePredicate Certificate)
    [∀ c ps r, Decidable (valid c ps r)] (certificates : CertificateSound.{u} E valid)
    (g : ClaimGraph Certificate) (r : Report) (accepted : check E valid g = some r) :
    Unfolds g r.root r.assumptions :=
  (check_sound E valid certificates g r accepted).2.2.2.2.2.2.2

end VE.Graph
