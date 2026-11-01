import VE.Closure.Paths
import VE.SoftNorms.Tree
import VE.Risk.Decl

namespace VE.Closure

/-- A finite order: `(a, b) ∈ edges` says `a` is directly above `b`. -/
structure Order (α : Type) where
  elems : List α
  edges : List (α × α)

structure Caps where
  elems : Nat
  edges : Nat

namespace Order
def admit {α : Type} [DecidableEq α] (c : Caps) (o : Order α) : Except String Unit :=
  if o.elems.length > c.elems then .error s!"ResourceLimit: At most {c.elems} grades"
  else if o.edges.length > c.edges then .error s!"ResourceLimit: At most {c.edges} order pairs"
  else if o.edges.all (fun e => o.elems.contains e.1 && o.elems.contains e.2) then .ok ()
  else .error "UnknownSymbol: an order pair names an undeclared element"
end Order

def Order.above {α : Type} [DecidableEq α] (o : Order α) (a b : α) : Bool := reachEval .plus o.edges a b
def Order.atLeast {α : Type} [DecidableEq α] (o : Order α) (a b : α) : Bool := reachEval .star o.edges a b

theorem path_iff_transGen {α : Type u} {R : α → α → Prop} {a b : α} :
    Path R a b ↔ Relation.TransGen R a b := by
  constructor
  · intro h
    induction h with
    | edge h => exact .single h
    | cons h _ ih => exact (Relation.TransGen.single h).trans ih
  · intro h
    induction h with
    | single h => exact .edge h
    | tail _ h ih => exact ih.trans (.edge h)

theorem reachable_star_iff {α : Type u} {R : α → α → Prop} {a b : α} :
    Reachable .star R a b ↔ a = b ∨ Relation.TransGen R a b := by
  simp [Reachable, path_iff_transGen]

theorem atLeast_refl {α : Type} [DecidableEq α] (o : Order α) (a : α) :
    o.atLeast a a = true := by
  exact (reachEval_iff .star o.edges a a).mpr (.inl rfl)

theorem atLeast_trans {α : Type} [DecidableEq α] (o : Order α) {a b c : α}
    (h₁ : o.atLeast a b = true) (h₂ : o.atLeast b c = true) : o.atLeast a c = true := by
  apply (reachEval_iff .star o.edges a c).mpr
  rcases (reachEval_iff .star o.edges a b).mp h₁ with rfl | h₁
  · exact (reachEval_iff .star o.edges a c).mp h₂
  rcases (reachEval_iff .star o.edges b c).mp h₂ with rfl | h₂
  · exact .inr h₁
  · exact .inr (h₁.trans h₂)

theorem above_iff {α : Type} [DecidableEq α] (o : Order α) (a b : α) :
    o.above a b = true ↔ Relation.TransGen (fun x y => (x, y) ∈ o.edges) a b := by
  exact (reachEval_iff .plus o.edges a b).trans path_iff_transGen

theorem atLeast_iff {α : Type} [DecidableEq α] (o : Order α) (a b : α) :
    o.atLeast a b = true ↔ a = b ∨ Relation.TransGen (fun x y => (x, y) ∈ o.edges) a b := by
  exact (reachEval_iff .star o.edges a b).trans reachable_star_iff

/-- `VE.SoftNorms.outranksPlus` agrees with `above` on admitted ranks. -/
theorem outranksPlus_eq_above (env : VE.SoftNorms.SoftEnv)
    (hv : VE.SoftNorms.RanksValid env) (a b : String) :
    VE.SoftNorms.outranksPlus env a b = (Order.mk env.ranks env.outranks).above a b := by
  have hp : ∀ {x y}, VE.Route.DepPath (VE.SoftNorms.rankNodes env) x y ↔
      Path (fun p q => (p, q) ∈ env.outranks) x y := by
    intro x y
    constructor
    · intro h
      induction h with
      | edge h => exact .edge ((VE.SoftNorms.depEdge_iff hv).mp h)
      | trans _ _ ih₁ ih₂ => exact ih₁.trans ih₂
    · intro h
      induction h with
      | edge h => exact .edge ((VE.SoftNorms.depEdge_iff hv).mpr h)
      | cons h _ ih => exact (VE.Route.DepPath.edge ((VE.SoftNorms.depEdge_iff hv).mpr h)).trans ih
  have hiff : VE.SoftNorms.outranksPlus env a b = true ↔
      (Order.mk env.ranks env.outranks).above a b = true := by
    exact (VE.SoftNorms.outranksPlus_iff_path hv a b).trans
      (hp.trans (reachEval_iff .plus env.outranks a b).symm)
  cases h₁ : VE.SoftNorms.outranksPlus env a b <;>
    cases h₂ : (Order.mk env.ranks env.outranks).above a b <;>
    simp_all

theorem risk_step_iff (cs : List String) (es : List (String × String)) (a b : String) :
    (a, b) ∈ VE.Risk.closeStep cs es ↔
      a ∈ cs ∧ b ∈ cs ∧ ((a, b) ∈ es ∨ ∃ m ∈ cs, (a, m) ∈ es ∧ (m, b) ∈ es) := by
  simp [VE.Risk.closeStep, List.mem_flatMap, List.mem_filterMap, List.any_eq_true]
  constructor
  · rintro ⟨x, hx, y, hy, h, rfl, rfl⟩
    exact ⟨hx, hy, h⟩
  · rintro ⟨ha, hb, h⟩
    exact ⟨a, ha, b, hb, h, rfl, rfl⟩

theorem risk_step_in (cs : List String) (es : List (String × String)) :
    ∀ e ∈ VE.Risk.closeStep cs es, e.1 ∈ cs ∧ e.2 ∈ cs := by
  rintro ⟨a, b⟩ h
  exact ⟨((risk_step_iff cs es a b).mp h).1, ((risk_step_iff cs es a b).mp h).2.1⟩

theorem risk_step_extends (cs : List String) (es : List (String × String))
    (he : ∀ e ∈ es, e.1 ∈ cs ∧ e.2 ∈ cs) :
    ∀ e ∈ es, e ∈ VE.Risk.closeStep cs es := by
  rintro ⟨a, b⟩ h
  exact (risk_step_iff cs es a b).mpr ⟨(he _ h).1, (he _ h).2, .inl h⟩

theorem risk_step_mono (cs : List String) (es fs : List (String × String))
    (h : ∀ e ∈ es, e ∈ fs) :
    ∀ e ∈ VE.Risk.closeStep cs es, e ∈ VE.Risk.closeStep cs fs := by
  rintro ⟨a, b⟩ he
  obtain ⟨ha, hb, he | ⟨m, hm, h₁, h₂⟩⟩ := (risk_step_iff cs es a b).mp he
  · exact (risk_step_iff cs fs a b).mpr ⟨ha, hb, .inl (h _ he)⟩
  · exact (risk_step_iff cs fs a b).mpr ⟨ha, hb, .inr ⟨m, hm, h _ h₁, h _ h₂⟩⟩

theorem risk_iter_mono (cs : List String) (n : Nat) (es fs : List (String × String))
    (h : ∀ e ∈ es, e ∈ fs) :
    ∀ e ∈ VE.Risk.closeIter cs n es, e ∈ VE.Risk.closeIter cs n fs := by
  induction n generalizing es fs with
  | zero => exact h
  | succ n ih =>
    exact ih _ _ (risk_step_mono cs es fs h)

theorem risk_pivot_in (cs : List String) (v : String)
    (hv : v ∈ cs) (es : List (String × String))
    (he : ∀ e ∈ es, e.1 ∈ cs ∧ e.2 ∈ cs) :
    ∀ e ∈ pivot v es, e ∈ VE.Risk.closeStep cs es := by
  rintro ⟨a, b⟩ h
  rcases (mem_pivot v a b es).mp h with h | ⟨h₁, h₂⟩
  · exact risk_step_extends cs es he _ h
  · exact (risk_step_iff cs es a b).mpr
      ⟨(he _ h₁).1, (he _ h₂).2, .inr ⟨v, hv, h₁, h₂⟩⟩

theorem risk_warshall_in (cs vs : List String)
    (hv : ∀ v ∈ vs, v ∈ cs) (es : List (String × String))
    (he : ∀ e ∈ es, e.1 ∈ cs ∧ e.2 ∈ cs) :
    ∀ e ∈ warshall vs es, e ∈ VE.Risk.closeIter cs vs.length es := by
  induction vs generalizing es with
  | nil => exact fun _ h => h
  | cons v vs ih =>
    intro e h
    have hp := risk_pivot_in cs v (hv v (by simp)) es he
    have hi := ih (fun w hw => hv w (by simp [hw])) (pivot v es)
      (fun e he' => risk_step_in cs es _ (hp _ he'))
    change e ∈ warshall vs (pivot v es) at h
    change e ∈ VE.Risk.closeIter cs vs.length (VE.Risk.closeStep cs es)
    exact risk_iter_mono cs vs.length (pivot v es) (VE.Risk.closeStep cs es) hp _ (hi _ h)

theorem risk_iter_in (cs : List String) (n : Nat) (es : List (String × String))
    (he : ∀ e ∈ es, e.1 ∈ cs ∧ e.2 ∈ cs) :
    ∀ e ∈ VE.Risk.closeIter cs n es, e.1 ∈ cs ∧ e.2 ∈ cs := by
  induction n generalizing es with
  | zero => exact he
  | succ n ih => exact ih _ (risk_step_in cs es)

theorem risk_iter_succ (cs : List String) (n : Nat) (es : List (String × String))
    (he : ∀ e ∈ es, e.1 ∈ cs ∧ e.2 ∈ cs) :
    ∀ e ∈ VE.Risk.closeIter cs n es, e ∈ VE.Risk.closeIter cs (n + 1) es := by
  exact risk_iter_mono cs n es (VE.Risk.closeStep cs es)
    (risk_step_extends cs es he)

theorem risk_iter_sound (cs : List String) (n : Nat) (es orig : List (String × String))
    (h : ∀ a b, (a, b) ∈ es → Path (fun x y => (x, y) ∈ orig) a b) :
    ∀ a b, (a, b) ∈ VE.Risk.closeIter cs n es →
      Path (fun x y => (x, y) ∈ orig) a b := by
  induction n generalizing es with
  | zero => exact h
  | succ n ih =>
    apply ih _
    intro a b hab
    obtain ⟨_, _, hab | ⟨m, _, h₁, h₂⟩⟩ := (risk_step_iff cs es a b).mp hab
    · exact h a b hab
    · exact (h a m h₁).trans (h m b h₂)

/-- `VE.Risk.closure` agrees with `above` when severity edges are declared. -/
theorem risk_closure_eq (R : VE.Risk.RiskDoc)
    (hd : ∀ e ∈ R.risk.severity.edges, e.1 ∈ R.classes ∧ e.2 ∈ R.classes) (a b : String) :
    (VE.Risk.closure R).contains (a, b) =
      (Order.mk R.classes R.risk.severity.edges).above a b := by
  let cs := R.classes
  let es := R.risk.severity.edges
  have hw : ∀ a b, Path (fun x y => (x, y) ∈ es) a b → (a, b) ∈ warshall cs es := by
    intro x y p
    induction p with
    | edge h => exact warshall_extends cs es h
    | @cons x m y h _ ih =>
      exact warshall_closed cs es ((hd _ h).2) x y (warshall_extends cs es h) ih
  have hiff : (VE.Risk.closure R).contains (a, b) = true ↔
      (Order.mk R.classes R.risk.severity.edges).above a b = true := by
    constructor
    · intro hc
      apply (reachEval_iff .plus es a b).mpr
      exact risk_iter_sound cs (cs.length + 1) es es (fun x y h => .edge h)
        a b (List.contains_iff_mem.mp hc)
    · intro ha
      have hp := (reachEval_iff .plus es a b).mp ha
      have hi := risk_warshall_in cs cs (fun _ h => h) es hd _ (hw a b hp)
      apply List.contains_iff_mem.mpr
      exact risk_iter_succ cs cs.length es hd _ hi
  cases h₁ : (VE.Risk.closure R).contains (a, b) <;>
    cases h₂ : (Order.mk R.classes R.risk.severity.edges).above a b <;>
    simp_all

end VE.Closure
