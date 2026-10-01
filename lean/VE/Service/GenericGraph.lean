/-! The named claim-graph checker of `VE/ClaimGraph.lean`, over any formula
type and any model semantics (SEMANTICS-MIGRATION-PLAN.md section 2.1, the
`graph` mode on the closure, core and order families).

`VE.Graph` fixes the relational FOL of `VE.Formula`. Here a semantics is an
explicit model type, an admissibility predicate and a truth relation `Holds`,
and consequence is truth in every admissible model (`Ent`). Each family's
consequence relation (`VE.Closure.Entails`, `VE.Core.Entails`,
`VE.Order.Entails`) is this relation at its own models, definitionally. The
checker, the provenance invariant (`SoundReport`, `Unfolds`) and the proofs
are those of `VE.Graph`, with typing as a decidable `wf` test and certificate
validity as a Boolean predicate on claims. Nothing in `VE/ClaimGraph.lean`
changes. -/
namespace VE.Service.GenericGraph
universe u v

structure Claim (F : Type) where
  name : String
  formula : F
  label : String := "asserted"

structure Edge (C : Type) where
  premises : List String
  certificate : C

/-- `none` marks an undischarged assumption. -/
structure Node (F C : Type) where
  claim : Claim F
  deduction : Option (Edge C)

/-- Nodes are supplied in topological order, premises before conclusions. -/
structure ClaimGraph (F C : Type) where
  nodes : List (Node F C)
  root : String

structure Report (F : Type) where
  root : Claim F
  assumptions : List (Claim F)

/-- Consequence: truth in every admissible model. -/
def Ent {F : Type} {Model : Type v} (Adm : Model → Prop) (Holds : Model → F → Prop)
    (premises : List F) (conclusion : F) : Prop :=
  ∀ S, Adm S → (∀ a ∈ premises, Holds S a) → Holds S conclusion

section
variable {F C : Type}

def rank (g : ClaimGraph F C) (name : String) : Nat :=
  (g.nodes.map (fun n => n.claim.name)).idxOf name

def acyclicCheck (g : ClaimGraph F C) : Bool :=
  g.nodes.all fun n => match n.deduction with
    | none => true
    | some edge => edge.premises.all (fun p => rank g p < rank g n.claim.name)

def uniqueNames (g : ClaimGraph F C) : Bool :=
  decide (g.nodes.map (fun n => n.claim.name)).Nodup

def Dependency (g : ClaimGraph F C) (parent child : String) : Prop :=
  ∃ n ∈ g.nodes, n.claim.name = parent ∧
    ∃ edge, n.deduction = some edge ∧ child ∈ edge.premises

inductive Path (g : ClaimGraph F C) : String → String → Prop where
  | edge {a b} : Dependency g a b → Path g a b
  | trans {a b c} : Path g a b → Path g b c → Path g a c

def Acyclic (g : ClaimGraph F C) : Prop := ∀ name, ¬ Path g name name

def lookup (seen : List (Report F)) (name : String) : Option (Report F) :=
  seen.find? (fun r => r.root.name == name)

def resolve (seen : List (Report F)) : List String → Option (List (Report F))
  | [] => some []
  | name :: names => do
    let r ← lookup seen name
    let rs ← resolve seen names
    some (r :: rs)

def checkNode (wf : F → Bool) (valid : C → List (Claim F) → Claim F → Bool)
    (seen : List (Report F)) (node : Node F C) : Option (Report F) :=
  if wf node.claim.formula then
    match node.deduction with
    | none => some ⟨node.claim, [node.claim]⟩
    | some edge => do
      let children ← resolve seen edge.premises
      if valid edge.certificate (children.map Report.root) node.claim then
        some ⟨node.claim, children.flatMap Report.assumptions⟩
      else none
  else none

def checkNodes (wf : F → Bool) (valid : C → List (Claim F) → Claim F → Bool) :
    List (Node F C) → List (Report F) → Option (List (Report F))
  | [], seen => some seen
  | node :: nodes, seen => do
    let r ← checkNode wf valid seen node
    checkNodes wf valid nodes (r :: seen)

def check (wf : F → Bool) (valid : C → List (Claim F) → Claim F → Bool) (g : ClaimGraph F C) :
    Option (Report F) := do
  if !uniqueNames g || !acyclicCheck g then none else do
    let seen ← checkNodes wf valid g.nodes []
    lookup seen g.root

def IsAssumption (g : ClaimGraph F C) (claim : Claim F) : Prop :=
  ∃ node ∈ g.nodes, node.claim = claim ∧ node.deduction = none

inductive Unfolds (g : ClaimGraph F C) : Claim F → List (Claim F) → Prop where
  | assumption (node : Node F C) (member : node ∈ g.nodes)
      (leaf : node.deduction = none) : Unfolds g node.claim [node.claim]
  | deduction (node : Node F C) (member : node ∈ g.nodes)
      (edge : Edge C) (submitted : node.deduction = some edge)
      (children : List (Report F))
      (names : children.map (fun r => r.root.name) = edge.premises)
      (branches : ∀ r ∈ children, Unfolds g r.root r.assumptions) :
      Unfolds g node.claim (children.flatMap Report.assumptions)

/-- The certificate contract: an accepted certificate proves consequence of
its exact ordered premises. -/
def CertificateSound {Model : Type v} (Adm : Model → Prop) (Holds : Model → F → Prop)
    (valid : C → List (Claim F) → Claim F → Bool) : Prop :=
  ∀ c ps r, valid c ps r = true → Ent Adm Holds (ps.map Claim.formula) r.formula

/-- Entailment and exact name/AST provenance, as `VE.Graph.SoundReport`. -/
def SoundReport {Model : Type v} (Adm : Model → Prop) (Holds : Model → F → Prop) (wf : F → Bool)
    (g : ClaimGraph F C) (r : Report F) : Prop :=
  wf r.root.formula = true ∧
  (∃ node ∈ g.nodes, node.claim = r.root) ∧
  (∀ leaf ∈ r.assumptions, wf leaf.formula = true ∧ IsAssumption g leaf) ∧
  Ent Adm Holds (r.assumptions.map Claim.formula) r.root.formula ∧
  Unfolds g r.root r.assumptions

theorem acyclicCheck_dependency (g : ClaimGraph F C) (h : acyclicCheck g = true)
    (parent child : String) (hd : Dependency g parent child) : rank g child < rank g parent := by
  obtain ⟨node, hn, he, edge, hd, hm⟩ := hd
  have hc := List.all_eq_true.mp h node hn
  simp only [hd] at hc
  have hr := List.all_eq_true.mp hc child hm
  simpa [he] using hr

theorem path_rank (g : ClaimGraph F C) (h : acyclicCheck g = true)
    (parent child : String) (hp : Path g parent child) : rank g child < rank g parent := by
  induction hp with
  | edge hd => exact acyclicCheck_dependency g h _ _ hd
  | trans _ _ ih1 ih2 => omega

theorem acyclicCheck_sound (g : ClaimGraph F C) (h : acyclicCheck g = true) : Acyclic g := by
  intro name hp
  have := path_rank g h name name hp
  omega

theorem lookup_sound (seen : List (Report F)) (name : String) (r : Report F)
    (h : lookup seen name = some r) : r ∈ seen ∧ r.root.name = name := by
  exact ⟨List.mem_of_find?_eq_some h, by simpa using List.find?_some h⟩

theorem resolve_sound (seen : List (Report F)) (names : List String) (rs : List (Report F))
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

theorem checkNode_sound {Model : Type v} (Adm : Model → Prop) (Holds : Model → F → Prop)
    (wf : F → Bool) (valid : C → List (Claim F) → Claim F → Bool)
    (certificates : CertificateSound Adm Holds valid)
    (g : ClaimGraph F C) (seen : List (Report F))
    (hs : ∀ r ∈ seen, SoundReport Adm Holds wf g r) (node : Node F C)
    (hn : node ∈ g.nodes) (r : Report F) (h : checkNode wf valid seen node = some r) :
    SoundReport Adm Holds wf g r := by
  unfold checkNode at h
  split at h
  next htyped =>
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
          have hh : ∀ child ∈ children, SoundReport Adm Holds wf g child := by
            intro child hm
            exact hs child ((resolve_sound seen edge.premises children hc).1 child hm)
          refine ⟨htyped, ⟨node, hn, rfl⟩, ?_, ?_, ?_⟩
          · intro leaf hl
            obtain ⟨child, hm, hl⟩ := List.mem_flatMap.mp hl
            exact (hh child hm).2.2.1 leaf hl
          · intro S hS hall
            apply certificates edge.certificate (children.map Report.root) node.claim hv S hS
            intro premise hp
            obtain ⟨claim, hclaim, rfl⟩ := List.mem_map.mp hp
            obtain ⟨child, hm, rfl⟩ := List.mem_map.mp hclaim
            apply (hh child hm).2.2.2.1 S hS
            intro a ha
            obtain ⟨leaf, hl, rfl⟩ := List.mem_map.mp ha
            apply hall leaf.formula
            exact List.mem_map.mpr ⟨leaf, List.mem_flatMap.mpr ⟨child, hm, hl⟩, rfl⟩
          · exact Unfolds.deduction node hn edge hd children
              (resolve_sound seen edge.premises children hc).2
              (fun child hm => (hh child hm).2.2.2.2)
        next => contradiction
  next => contradiction

theorem checkNodes_sound {Model : Type v} (Adm : Model → Prop) (Holds : Model → F → Prop)
    (wf : F → Bool) (valid : C → List (Claim F) → Claim F → Bool)
    (certificates : CertificateSound Adm Holds valid)
    (g : ClaimGraph F C) (nodes : List (Node F C))
    (hn : ∀ node ∈ nodes, node ∈ g.nodes) (seen : List (Report F))
    (hs : ∀ r ∈ seen, SoundReport Adm Holds wf g r) (out : List (Report F))
    (h : checkNodes wf valid nodes seen = some out) : ∀ r ∈ out, SoundReport Adm Holds wf g r := by
  induction nodes generalizing seen with
  | nil =>
    simp only [checkNodes, Option.some.injEq] at h
    subst out
    exact hs
  | cons node nodes ih =>
    cases hc : checkNode wf valid seen node with
    | none => simp only [checkNodes, hc, bind, Option.bind, reduceCtorEq] at h
    | some r =>
      simp only [checkNodes, hc, bind, Option.bind] at h
      apply ih (fun n hm => hn n (by simp [hm])) (r :: seen) _ h
      intro x hx
      rcases List.mem_cons.mp hx with rfl | hx
      · exact checkNode_sound Adm Holds wf valid certificates g seen hs node (hn node (by simp)) x hc
      · exact hs x hx

/-- Acceptance gives acyclicity, alias uniqueness, the exact root, and a sound
report, conditional only on the certificate contract (`VE.Graph.check_sound_of_certificateSound`). -/
theorem check_sound {Model : Type v} (Adm : Model → Prop) (Holds : Model → F → Prop)
    (wf : F → Bool) (valid : C → List (Claim F) → Claim F → Bool)
    (certificates : CertificateSound Adm Holds valid)
    (g : ClaimGraph F C) (r : Report F) (accepted : check wf valid g = some r) :
    Acyclic g ∧ (g.nodes.map (fun n => n.claim.name)).Nodup ∧
    r.root.name = g.root ∧ SoundReport Adm Holds wf g r := by
  unfold check at accepted
  split at accepted
  next => contradiction
  next hgood =>
    have hg : uniqueNames g = true ∧ acyclicCheck g = true := by
      simpa using hgood
    cases hn : checkNodes wf valid g.nodes [] with
    | none => simp only [hn, bind, Option.bind, reduceCtorEq] at accepted
    | some seen =>
      simp only [hn, bind, Option.bind] at accepted
      obtain ⟨hm, he⟩ := lookup_sound seen g.root r accepted
      exact ⟨acyclicCheck_sound g hg.2, by simpa [uniqueNames] using hg.1, he,
        checkNodes_sound Adm Holds wf valid certificates g g.nodes (fun _ h => h) []
          (by simp) seen hn r hm⟩

end

end VE.Service.GenericGraph
