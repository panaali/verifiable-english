import VE.RightClauses.Plain

/-! Guard extensions (docs/spec/right-clauses.md 8.3, `plain_wellFormed`): the relation `FExt` between a formula and
the same formula with some subformulas conjoined with typed base formulas, what it keeps (typing, the predicates a
stratum DAG sees), and the `ResourceLimit` disjunction the proof of `plain_wellFormed` carries through `validateRights`.
Nothing here is trusted: definitions are proof vocabulary only. -/
namespace VE.RightClauses.PWF
open VE.Norms (preds anyF)

/-! ## `ResourceLimit` or success -/

/-- Success, or an error that is a resource limit. -/
def OkOrRL (x : Except String Unit) : Prop := x = .ok () ∨ ∃ e, x = .error e ∧ "ResourceLimit: ".isPrefixOf e = true

theorem okOrRL_ok : OkOrRL (.ok ()) := Or.inl rfl

theorem okOrRL_of_eq {x y : Except String Unit} (h : x = y) (hy : y = .ok ()) : OkOrRL x := Or.inl (h.trans hy)

theorem okOrRL_rl (e : String) (h : "ResourceLimit: ".isPrefixOf e = true) : OkOrRL (.error e) := Or.inr ⟨e, rfl, h⟩

theorem okOrRL_bind {x : Except String Unit} {f : Unit → Except String Unit} (hx : OkOrRL x)
    (hf : x = .ok () → OkOrRL (f ())) : OkOrRL (x >>= f) := by
  rcases hx with hx | ⟨e, hx, he⟩
  · rw [hx]; exact hf hx
  · rw [hx]; exact Or.inr ⟨e, rfl, he⟩

theorem bind_ok {x : Except String Unit} {f : Unit → Except String Unit} (h : (x >>= f) = .ok ()) :
    x = .ok () ∧ f () = .ok () := by
  cases x with
  | error e => cases h
  | ok u => exact ⟨rfl, h⟩

/-- A loop whose every throw is a resource limit. -/
theorem okOrRL_forIn {α : Type} (l : List α) (f : α → PUnit → Except String (ForInStep PUnit))
    (hf : ∀ a u, f a u = .ok (.yield ()) ∨ ∃ e, f a u = .error e ∧ "ResourceLimit: ".isPrefixOf e = true) :
    OkOrRL (forIn l PUnit.unit f >>= fun _ => pure ()) := by
  induction l with
  | nil => exact Or.inl rfl
  | cons a l ih =>
    rcases hf a PUnit.unit with h | ⟨e, h, he⟩
    · simpa [List.forIn_cons, h] using ih
    · exact Or.inr ⟨e, by simp [List.forIn_cons, h]; rfl, he⟩

/-! ## Guard extensions -/

/-- `ψ` is `φ` with some subformulas `a` replaced by a `b` with `P a b`, under the connectives only. -/
inductive FExt (P : VE.Formula → VE.Formula → Prop) : VE.Formula → VE.Formula → Prop
  | refl (φ : VE.Formula) : FExt P φ φ
  | base {a b : VE.Formula} : P a b → FExt P a b
  | not {a a' : VE.Formula} : FExt P a a' → FExt P (.not a) (.not a')
  | and {a a' b b' : VE.Formula} : FExt P a a' → FExt P b b' → FExt P (.and a b) (.and a' b')
  | or {a a' b b' : VE.Formula} : FExt P a a' → FExt P b b' → FExt P (.or a b) (.or a' b')
  | implies {a a' b b' : VE.Formula} : FExt P a a' → FExt P b b' → FExt P (.implies a b) (.implies a' b')

theorem FExt.check {P : VE.Formula → VE.Formula → Prop} {E : VE.Environment} {Γ : List String}
    (hP : ∀ a b, P a b → a.check E Γ = true → b.check E Γ = true) :
    ∀ {φ ψ}, FExt P φ ψ → φ.check E Γ = true → ψ.check E Γ = true
  | _, _, .refl _, h => h
  | _, _, .base hab, h => hP _ _ hab h
  | _, _, .not h1, h => by simp only [VE.Formula.check] at h ⊢; exact FExt.check hP h1 h
  | _, _, .and h1 h2, h | _, _, .or h1 h2, h | _, _, .implies h1 h2, h => by
    simp only [VE.Formula.check, Bool.and_eq_true] at h ⊢
    exact ⟨FExt.check hP h1 h.1, FExt.check hP h2 h.2⟩

/-- What a stratum DAG reads of the predicates: those `keep` selects. -/
theorem FExt.preds {P : VE.Formula → VE.Formula → Prop} {keep : String → Bool}
    (hP : ∀ a b, P a b → (preds b).filter keep = (preds a).filter keep) :
    ∀ {φ ψ}, FExt P φ ψ → (preds ψ).filter keep = (preds φ).filter keep
  | _, _, .refl _ => rfl
  | _, _, .base hab => hP _ _ hab
  | _, _, .not h1 => by simp only [VE.Norms.preds]; exact FExt.preds hP h1
  | _, _, .and h1 h2 | _, _, .or h1 h2 | _, _, .implies h1 h2 => by
    simp only [VE.Norms.preds, List.filter_append, FExt.preds hP h1, FExt.preds hP h2]

theorem FExt.mono {P Q : VE.Formula → VE.Formula → Prop} (hPQ : ∀ a b, P a b → Q a b) :
    ∀ {φ ψ}, FExt P φ ψ → FExt Q φ ψ
  | _, _, .refl _ => .refl _
  | _, _, .base hab => .base (hPQ _ _ hab)
  | _, _, .not h1 => .not (FExt.mono hPQ h1)
  | _, _, .and h1 h2 => .and (FExt.mono hPQ h1) (FExt.mono hPQ h2)
  | _, _, .or h1 h2 => .or (FExt.mono hPQ h1) (FExt.mono hPQ h2)
  | _, _, .implies h1 h2 => .implies (FExt.mono hPQ h1) (FExt.mono hPQ h2)

theorem FExt.foldl_or {P : VE.Formula → VE.Formula → Prop} {ι : Type} (f g : ι → VE.Formula) :
    ∀ (L : List ι) (a b : VE.Formula), FExt P a b → (∀ i ∈ L, FExt P (f i) (g i)) →
      FExt P ((L.map f).foldl .or a) ((L.map g).foldl .or b)
  | [], _, _, hab, _ => hab
  | i :: L, a, b, hab, h => by
    simp only [List.map_cons, List.foldl_cons]
    exact FExt.foldl_or f g L _ _ (.or hab (h i (by simp))) (fun j hj => h j (by simp [hj]))

/-- `anyF` of pointwise extensions. -/
theorem FExt.anyF {P : VE.Formula → VE.Formula → Prop} {ι : Type} (f g : ι → VE.Formula) (L : List ι)
    (h : ∀ i ∈ L, FExt P (f i) (g i)) : FExt P (anyF (L.map f)) (anyF (L.map g)) :=
  FExt.foldl_or f g L _ _ (.refl _) h

theorem FExt.ite {P : VE.Formula → VE.Formula → Prop} (c : Prop) [Decidable c] {a a' b b' : VE.Formula}
    (h1 : c → FExt P a a') (h2 : ¬ c → FExt P b b') : FExt P (if c then a else b) (if c then a' else b') := by
  by_cases hc : c <;> simp [hc] <;> first | exact h1 hc | exact h2 hc

/-! ## The conjuncts `plain` adds -/

/-- An environment that shows the base vocabulary `E0` as it is. -/
def EnvOK (E0 E : VE.Environment) : Prop :=
  E.sorts = E0.sorts ∧ E.constants = E0.constants ∧ ∀ p s, E0.predicates p = some s → E.predicates p = some s

theorem sortOf_envOK {E0 E : VE.Environment} (h : EnvOK E0 E) (Γ : List String) (t : VE.Term) :
    t.sortOf E Γ = t.sortOf E0 Γ := by
  cases t <;> simp [VE.Term.sortOf, h.2.1]

theorem check_envOK {E0 E : VE.Environment} (h : EnvOK E0 E) :
    ∀ (φ : VE.Formula) (Γ : List String), φ.check E0 Γ = true → φ.check E Γ = true
  | .top, _, _ | .bottom, _, _ => rfl
  | .unary p t, Γ, hc => by
    simp only [VE.Formula.check, sortOf_envOK h] at hc ⊢
    cases hp : E0.predicates p with
    | none => simp [hp] at hc
    | some s => rw [h.2.2 p s hp]; simpa [hp] using hc
  | .binary p t u, Γ, hc => by
    simp only [VE.Formula.check, sortOf_envOK h] at hc ⊢
    cases hp : E0.predicates p with
    | none => simp [hp] at hc
    | some s => rw [h.2.2 p s hp]; simpa [hp] using hc
  | .eq t u, Γ, hc => by simpa only [VE.Formula.check, sortOf_envOK h] using hc
  | .not a, Γ, hc => check_envOK h a Γ hc
  | .and a b, Γ, hc | .or a b, Γ, hc | .implies a b, Γ, hc => by
    simp only [VE.Formula.check, Bool.and_eq_true] at hc ⊢
    exact ⟨check_envOK h a Γ hc.1, check_envOK h b Γ hc.2⟩
  | .all s a, Γ, hc | .ex s a, Γ, hc => by
    simp only [VE.Formula.check, Bool.and_eq_true, h.1] at hc ⊢
    exact ⟨hc.1, check_envOK h a _ hc.2⟩

/-- A formula typed over `E0` mentions only predicates `E0` declares. -/
theorem preds_declared {E0 : VE.Environment} :
    ∀ (φ : VE.Formula) (Γ : List String), φ.check E0 Γ = true → ∀ p ∈ preds φ, (E0.predicates p).isSome
  | .top, _, _ | .bottom, _, _ | .eq _ _, _, _ => by simp [VE.Norms.preds]
  | .unary q t, Γ, hc | .binary q t _, Γ, hc => by
    simp only [VE.Norms.preds, List.mem_singleton]
    rintro p rfl
    simp only [VE.Formula.check] at hc
    cases hq : E0.predicates p <;> simp_all
  | .not a, Γ, hc => preds_declared a Γ hc
  | .and a b, Γ, hc | .or a b, Γ, hc | .implies a b, Γ, hc => by
    simp only [VE.Formula.check, Bool.and_eq_true] at hc
    simp only [VE.Norms.preds, List.mem_append]
    rintro p (hp | hp)
    · exact preds_declared a Γ hc.1 p hp
    · exact preds_declared b Γ hc.2 p hp
  | .all s a, Γ, hc | .ex s a, Γ, hc => by
    simp only [VE.Formula.check, Bool.and_eq_true] at hc
    exact preds_declared a _ hc.2

/-- One step of `plain`: `b` is `a` with conjuncts typed over `E0` in `Γ`, none a predicate `hidden` names. -/
def Plus (E0 : VE.Environment) (hidden : String → Bool) (Γ : List String) (a b : VE.Formula) : Prop :=
  ∃ cs : List VE.Formula, b = cs.foldl .and a ∧ ∀ c ∈ cs, c.check E0 Γ = true ∧ ∀ p ∈ preds c, hidden p = false

theorem foldl_and_check (E : VE.Environment) (Γ : List String) :
    ∀ (cs : List VE.Formula) (a : VE.Formula),
    (cs.foldl .and a).check E Γ = (a.check E Γ && cs.all (·.check E Γ))
  | [], a => by simp
  | c :: cs, a => by
    simp only [List.foldl_cons, foldl_and_check E Γ cs, VE.Formula.check, List.all_cons, Bool.and_assoc]

theorem foldl_and_preds : ∀ (cs : List VE.Formula) (a : VE.Formula),
    preds (cs.foldl .and a) = preds a ++ cs.flatMap preds
  | [], a => by simp
  | c :: cs, a => by simp [foldl_and_preds cs, VE.Norms.preds, List.append_assoc]

theorem Plus.check {E0 E : VE.Environment} {hidden : String → Bool} {Γ : List String} (hE : EnvOK E0 E)
    {a b : VE.Formula} (h : Plus E0 hidden Γ a b) (ha : a.check E Γ = true) : b.check E Γ = true := by
  obtain ⟨cs, rfl, hcs⟩ := h
  rw [foldl_and_check]
  simp only [ha, Bool.true_and, List.all_eq_true]
  exact fun c hc => check_envOK hE c Γ (hcs c hc).1

theorem Plus.preds {E0 : VE.Environment} {hidden : String → Bool} {Γ : List String} {a b : VE.Formula}
    (h : Plus E0 hidden Γ a b) : (VE.Norms.preds b).filter hidden = (VE.Norms.preds a).filter hidden := by
  obtain ⟨cs, rfl, hcs⟩ := h
  rw [foldl_and_preds, List.filter_append]
  suffices (cs.flatMap VE.Norms.preds).filter hidden = [] by rw [this, List.append_nil]
  rw [List.filter_eq_nil_iff]
  intro p hp
  obtain ⟨c, hc, hpc⟩ := List.mem_flatMap.1 hp
  simp [(hcs c hc).2 p hpc]

end VE.RightClauses.PWF
