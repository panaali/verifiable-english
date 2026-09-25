import VE.Route.Checker

/-! The route (PLAN-EXPAND2 3.4, 3.5): one dependency DAG over definitions and
regulated predicates orders the layers; the checker receives Background, then
every layer's premises, then the document's own premises; and the abstract
acceptance theorem carries an accepted certificate down the layers to the
document-level statement over the input environment.

The DAG check is executable and mirrored by Python `ve/background.py:
dependency_order` with the same algorithm and the same diagnostic (see
docs/P0-Lean-NOTES.md). The same check serves the norm precedence graph. -/
namespace VE.Route
universe u

/-! ## One dependency DAG -/

/-- A node of the dependency graph: a defined or regulated predicate (or, for
the precedence graph, a rule name) and every symbol its body or guard mentions
after expansion. Mentions of symbols that are not nodes (base vocabulary) carry
no edge. -/
structure DepNode where
  name : String
  mentions : List String
  deriving DecidableEq, Repr

def nodeNames (ns : List DepNode) : List String := ns.map DepNode.name

/-- The node-to-node edges out of `n`. -/
def deps (ns : List DepNode) (n : DepNode) : List String :=
  n.mentions.filter (nodeNames ns).contains

/-- An edge `a → b`: node `a` mentions node `b`. -/
def DepEdge (ns : List DepNode) (a b : String) : Prop :=
  ∃ n ∈ ns, n.name = a ∧ b ∈ deps ns n

inductive DepPath (ns : List DepNode) : String → String → Prop where
  | edge {a b} : DepEdge ns a b → DepPath ns a b
  | trans {a b c} : DepPath ns a b → DepPath ns b c → DepPath ns a c

/-- No symbol depends on itself, directly or transitively. -/
def DagAcyclic (ns : List DepNode) : Prop := ∀ a, ¬ DepPath ns a a

def sortStrings (xs : List String) : List String := xs.mergeSort (fun a b => decide (a ≤ b))

/-- The one diagnostic for a cyclic graph, shared with Python: the sorted
names of every node that cannot be placed. -/
def cycleDiagnostic (unresolved : List String) : String :=
  "DependencyCycle: " ++ ", ".intercalate (sortStrings unresolved)

def smallest : List String → Option String
  | [] => none
  | x :: xs => some (xs.foldl (fun acc y => if y < acc then y else acc) x)

/-- Kahn's algorithm, placing the smallest ready name first (deterministic, so
Python and Lean produce the same order). -/
def kahn (ns : List DepNode) : Nat → List String → Except String (List String)
  | 0, placed => .ok placed
  | fuel + 1, placed =>
    let remaining := ns.filter (fun n => !placed.contains n.name)
    if remaining.isEmpty then .ok placed
    else
      let ready := remaining.filter (fun n => (deps ns n).all placed.contains)
      match smallest (ready.map DepNode.name) with
      | none => .error (cycleDiagnostic (remaining.map DepNode.name))
      | some m => kahn ns fuel (placed ++ [m])

/-- The independent check of a proposed order: a permutation of the node
names in which every edge points strictly earlier. -/
def verifyOrder (ns : List DepNode) (order : List String) : Bool :=
  decide order.Nodup && (nodeNames ns).all order.contains && order.all (nodeNames ns).contains &&
    ns.all (fun n => (deps ns n).all (fun m => order.idxOf m < order.idxOf n.name))

/-- The route's layer order, or the cycle diagnostic. Duplicate names are
rejected; the result of the search is re-verified before it is returned. -/
def dependencyOrder (ns : List DepNode) : Except String (List String) :=
  match (nodeNames ns).find? (fun n => (nodeNames ns).count n > 1) with
  | some n => .error s!"DuplicateDeclaration: dependency node {n}"
  | none => match kahn ns (ns.length + 1) [] with
    | .error e => .error e
    | .ok order => if verifyOrder ns order then .ok order else .error (cycleDiagnostic (nodeNames ns))

theorem verifyOrder_sound (ns : List DepNode) (order : List String)
    (h : verifyOrder ns order = true) :
    order.Nodup ∧ (∀ x, x ∈ order ↔ x ∈ nodeNames ns) ∧
      ∀ n ∈ ns, ∀ m ∈ deps ns n, order.idxOf m < order.idxOf n.name := by
  simp only [verifyOrder, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true,
    List.contains_iff_mem] at h
  obtain ⟨⟨⟨hn, hsub⟩, hsup⟩, hedges⟩ := h
  refine ⟨hn, fun x => ⟨hsup x, hsub x⟩, fun n hn m hm => ?_⟩
  simpa using hedges n hn m hm

theorem depPath_rank (ns : List DepNode) (order : List String)
    (hedges : ∀ n ∈ ns, ∀ m ∈ deps ns n, order.idxOf m < order.idxOf n.name)
    (a b : String) (hp : DepPath ns a b) : order.idxOf b < order.idxOf a := by
  induction hp with
  | edge he =>
    obtain ⟨n, hn, rfl, hm⟩ := he
    exact hedges n hn _ hm
  | trans _ _ ih₁ ih₂ => omega

/-- `Route.dag_acyclic`: an accepted order is a permutation of the nodes, every
dependency is placed strictly before its dependant (so a guard or body only
mentions symbols strictly below it), and the graph has no cycle. -/
theorem dag_acyclic (ns : List DepNode) (order : List String)
    (h : dependencyOrder ns = .ok order) :
    order.Nodup ∧ (∀ x, x ∈ order ↔ x ∈ nodeNames ns) ∧
      (∀ n ∈ ns, ∀ m ∈ deps ns n, order.idxOf m < order.idxOf n.name) ∧ DagAcyclic ns := by
  unfold dependencyOrder at h
  split at h
  · cases h
  · split at h
    · cases h
    · split at h
      · rename_i hv
        cases h
        obtain ⟨hn, hm, he⟩ := verifyOrder_sound ns _ hv
        exact ⟨hn, hm, he, fun a hp => by have := depPath_rank ns _ he a a hp; omega⟩
      · cases h

/-! ## The route and its acceptance theorem -/

section Acceptance
variable {L : Semantics.{u}} {Doc : Type} (R : Layer L Doc) (background : List L.Formula)

/-- What the checker receives: Background, then every layer's premises (in
route order), then the document's own premises. -/
def checkedPremises (d : Doc) (Γ : List L.Formula) : List L.Formula :=
  background ++ R.premises d ++ Γ

/-- Background holds on the route: it is implied by admissibility and the
layers' premises (literal distinctness and flags by admissibility, definition
biconditionals and profile premises by the layers). -/
def BackgroundSound : Prop :=
  ∀ d S, R.Admissible_out S → L.Sat S (R.premises d) → L.Sat S background

/-- Background invalidates models (PLAN-EXPAND2 3.1): a structurally
admissible structure satisfying Background and the layers' premises is an
admissible output structure. Needed only for the converse (countermodel)
direction. -/
def BackgroundComplete : Prop :=
  ∀ d S, L.Admissible R.E_out S → L.Sat S background → L.Sat S (R.premises d) → R.Admissible_out S

theorem sat_checked (S : L.Model) (d : Doc) (Γ : List L.Formula) :
    L.Sat S (checkedPremises R background d Γ) ↔
      L.Sat S background ∧ L.Sat S (R.premises d) ∧ L.Sat S Γ := by
  unfold checkedPremises
  rw [L.sat_append, L.sat_append, and_assoc]

/-- The checked entailment holds in every intended structure. -/
theorem route_intended (hbg : BackgroundSound R background) (d : Doc) (Γ : List L.Formula)
    (φ : L.Formula) (h : L.Entails R.E_out (checkedPremises R background d Γ) φ)
    (S : L.Model) (hS : R.Admissible_out S) (hi : R.Intended d S) (hΓ : L.Sat S Γ) :
    L.Holds S φ := by
  have hp : L.Sat S (R.premises d) := (R.faithful d S hS).mpr hi
  exact h S (R.admissible_out S hS)
    ((sat_checked R background S d Γ).mpr ⟨hbg d S hS hp, hp, hΓ⟩)

/-- Through unique expansion, the checked entailment is the document-level
statement over the input environment: it holds in every structure admissible
below the route that satisfies the document's premises. -/
theorem route_base (hbg : BackgroundSound R background) (d : Doc) (Γ : List L.Formula)
    (φ : L.Formula) (hΓ : ∀ a ∈ Γ, L.WellFormed R.E_in a) (hφ : L.WellFormed R.E_in φ)
    (h : L.Entails R.E_out (checkedPremises R background d Γ) φ)
    (S₀ : L.Model) (h₀ : R.Admissible_in S₀) (hs : L.Sat S₀ Γ) : L.Holds S₀ φ := by
  obtain ⟨S, ⟨rfl, hS, hp⟩, _⟩ := R.expands d S₀ h₀
  apply (R.restrict_holds S φ hS hφ).mpr
  exact h S (R.admissible_out S hS) ((sat_checked R background S d Γ).mpr
    ⟨hbg d S hS hp, hp, (R.sat_restrict S hS Γ hΓ).mp hs⟩)

/-- Every countermodel on the route restricts to a countermodel below it. -/
theorem route_countermodel_restricts (Γ : List L.Formula) (φ : L.Formula)
    (hΓ : ∀ a ∈ Γ, L.WellFormed R.E_in a) (hφ : L.WellFormed R.E_in φ)
    (S : L.Model) (hS : R.Admissible_out S) (hs : L.Sat S Γ) (hn : ¬ L.Holds S φ) :
    R.Admissible_in (R.restrict S) ∧ L.Sat (R.restrict S) Γ ∧ ¬ L.Holds (R.restrict S) φ :=
  ⟨R.restrict_admissible S hS, (R.sat_restrict S hS Γ hΓ).mpr hs,
    fun h => hn ((R.restrict_holds S φ hS hφ).mp h)⟩

/-- Every countermodel below the route expands to one the checker sees, so a
checked NO below survives elaboration. -/
theorem route_countermodel_expands (hbg : BackgroundSound R background) (d : Doc)
    (Γ : List L.Formula) (φ : L.Formula)
    (hΓ : ∀ a ∈ Γ, L.WellFormed R.E_in a) (hφ : L.WellFormed R.E_in φ)
    (S₀ : L.Model) (h₀ : R.Admissible_in S₀) (hs : L.Sat S₀ Γ) (hn : ¬ L.Holds S₀ φ) :
    ∃ S, R.restrict S = S₀ ∧ R.Admissible_out S ∧
      L.Sat S (checkedPremises R background d Γ) ∧ ¬ L.Holds S φ := by
  obtain ⟨S, ⟨rfl, hS, hp⟩, _⟩ := R.expands d S₀ h₀
  refine ⟨S, rfl, hS, (sat_checked R background S d Γ).mpr
    ⟨hbg d S hS hp, hp, (R.sat_restrict S hS Γ hΓ).mp hs⟩, fun h => hn ?_⟩
  exact (R.restrict_holds S φ hS hφ).mpr h

/-- Model correspondence: for statements over the input environment, the
checked entailment on the route is exactly consequence over the structures
admissible below it. -/
theorem route_entails_iff (hbg : BackgroundSound R background)
    (hc : BackgroundComplete R background) (d : Doc) (Γ : List L.Formula) (φ : L.Formula)
    (hΓ : ∀ a ∈ Γ, L.WellFormed R.E_in a) (hφ : L.WellFormed R.E_in φ) :
    L.Entails R.E_out (checkedPremises R background d Γ) φ ↔
      ∀ S₀, R.Admissible_in S₀ → L.Sat S₀ Γ → L.Holds S₀ φ := by
  constructor
  · exact route_base R background hbg d Γ φ hΓ hφ
  · intro h S hS hs
    obtain ⟨hb, hp, hg⟩ := (sat_checked R background S d Γ).mp hs
    have ho := hc d S hS hb hp
    apply (R.restrict_holds S φ ho hφ).mp
    exact h _ (R.restrict_admissible S ho) ((R.sat_restrict S ho Γ hΓ).mpr hg)

/-- The abstract acceptance theorem of a route. An accepted certificate of any
sound checker on the checked premise list gives (1) the checked entailment,
(2) the statement in every intended structure of `E_out`, and (3) for
statements over `E_in`, the statement in every structure admissible below the
route. `route_countermodel_restricts` and `route_countermodel_expands` give the
countermodel half. -/
theorem route_acceptance (hbg : BackgroundSound R background) (checker : Checker L R.E_out)
    (d : Doc) (Γ : List L.Formula) (φ : L.Formula)
    (c : checker.Cert) (ps : List checker.Stmt) (r : checker.Stmt)
    (accepted : checker.valid c ps r)
    (hps : ps.map checker.formula = checkedPremises R background d Γ) (hr : checker.formula r = φ) :
    L.Entails R.E_out (checkedPremises R background d Γ) φ ∧
      (∀ S, R.Admissible_out S → R.Intended d S → L.Sat S Γ → L.Holds S φ) ∧
      ((∀ a ∈ Γ, L.WellFormed R.E_in a) → L.WellFormed R.E_in φ →
        ∀ S₀, R.Admissible_in S₀ → L.Sat S₀ Γ → L.Holds S₀ φ) := by
  have he : L.Entails R.E_out (checkedPremises R background d Γ) φ := by
    have := checker.sound c ps r accepted
    rwa [hps, hr] at this
  exact ⟨he, route_intended R background hbg d Γ φ he,
    fun hΓ hφ => route_base R background hbg d Γ φ hΓ hφ he⟩

end Acceptance
end VE.Route
