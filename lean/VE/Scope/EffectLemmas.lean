import VE.Scope.Govern
import VE.Readings.Strings
import VE.NormDefaults.Check

/-! Decoder and loop lemmas for spec 5.4's SC-2 statements (sc-2c): the base guard decoder's value does not depend on
    its node count or depth fuel; a scalar or term position `substOwn` leaves, for any guard that decodes as a formula;
    and a loop fails only with an error of its body (sc-2c); and what the chain's decoder reads from a rule object
    (sc-2d). `Theorems.lean` states 5.4's theorems over them. -/

namespace VE.Scope
open Lean
open VE.Norms.Wire (budgetFormula budgetTerm)

/-! The base guard decoder -/

theorem budgetTerm_ok {k : Nat} {j : Json} {t : VE.Term} {c : Nat} (h : budgetTerm k j = .ok (t, c)) :
    VE.Bridge.decodeTerm j = .ok t ∧ c = k + 1 := by
  unfold budgetTerm at h
  cases hd : VE.Bridge.decodeTerm j with
  | error e => by_cases hk : k + 1 > VE.Limits.maxNodes <;> simp_all [bind, Except.bind, pure, Except.pure]
  | ok d =>
    by_cases hk : k + 1 > VE.Limits.maxNodes <;> simp [hk, hd, bind, Except.bind, pure, Except.pure] at h
    cases d <;> simp at h <;> (try split at h) <;> simp_all

theorem budgetTerm_val {k k' : Nat} {j : Json} {t t' : VE.Term} {c c' : Nat}
    (h : budgetTerm k j = .ok (t, c)) (h' : budgetTerm k' j = .ok (t', c')) : t = t' := by
  have := (budgetTerm_ok h).1; have := (budgetTerm_ok h').1; simp_all

/-- The decoded formula is the same whatever the node count or depth fuel, when both decodes succeed. -/
theorem budgetFormula_val : ∀ (n n' k k' : Nat) (j : Json) (φ ψ : VE.Formula) (c c' : Nat),
    budgetFormula n k j = .ok (φ, c) → budgetFormula n' k' j = .ok (ψ, c') → φ = ψ
  | 0, _, _, _, _, _, _, _, _, h, _ => by simp [budgetFormula, throw, throwThe, MonadExceptOf.throw] at h
  | _, 0, _, _, _, _, _, _, _, _, h => by simp [budgetFormula, throw, throwThe, MonadExceptOf.throw] at h
  | n + 1, n' + 1, k, k', j, φ, ψ, c, c', h, h' => by
    unfold budgetFormula at h h'
    cases j <;> simp only [Json.getArr?, bind, Except.bind, pure, Except.pure, throw, throwThe, MonadExceptOf.throw] at h h' <;>
      split at h <;> (try (simp at h; done)) <;> split at h' <;> (try (simp at h'; done))
    rename_i xs _ _
    split at h <;> rename_i heq <;> simp only [heq] at h' <;> (repeat' (first | split at h | split at h')) <;>
      simp_all
    all_goals (obtain ⟨rfl, -⟩ := h; obtain ⟨rfl, -⟩ := h'; congr 1 <;>
      first | (apply budgetTerm_val <;> assumption) | (apply budgetFormula_val <;> assumption))
theorem decodeBudgeted_ok {j : Json} {φ : VE.Formula} (h : VE.Norms.Wire.decodeBudgeted j = .ok φ) :
    ∃ c, budgetFormula VE.Limits.maxDepth 0 j = .ok (φ, c) := by
  unfold VE.Norms.Wire.decodeBudgeted at h
  cases hb : budgetFormula VE.Limits.maxDepth 0 j with
  | error e => simp [hb, Functor.map, Except.map] at h
  | ok p => simp [hb, Functor.map, Except.map] at h; exact ⟨p.2, by rw [← h]⟩

/-! `substOwn` at a position the decoder reads as a scalar or a term -/

/-- A scalar `substOwn` writes is the value as written, for any guard: `own` became a guard array, not a scalar. -/
theorem substOwn_scalar {g₁ : Json} (g₂ : Json) (hg : ∃ a, g₁ = .arr a) :
    ∀ (m : Nat) (x v : Json), (∀ a, v ≠ .arr a) → (∀ o, v ≠ .obj o) → substOwn g₁ m x = v → substOwn g₂ m x = v
  | 0, _, _, _, _, h => h
  | m + 1, x, v, ha, ho, h => by
    obtain ⟨a, rfl⟩ := hg
    cases x with
    | str s' =>
      by_cases hs : s' = "own"
      · simp only [substOwn, hs] at h; exact absurd h.symm (ha a)
      · simp_all [substOwn]
    | arr => simp only [substOwn] at h; exact absurd h.symm (ha _)
    | obj => simp only [substOwn] at h; exact absurd h.symm (ho _)
    | _ => simp_all [substOwn]

theorem substOwn_term {g₁ : Json} (g₂ : Json) (hg : ∃ a, g₁ = .arr a)
    (ht : ∀ t, VE.Bridge.decodeTerm g₁ ≠ .ok t) :
    ∀ (m : Nat) (x : Json) (t : VE.Term), VE.Bridge.decodeTerm (substOwn g₁ m x) = .ok t →
      substOwn g₂ m x = substOwn g₁ m x
  | 0, _, _, _ => rfl
  | m + 1, x, t, h => by
    cases x with
    | str s => by_cases hs : s = "own" <;> simp_all [substOwn, VE.Bridge.decodeTerm, Json.getArr?, bind, Except.bind]
    | arr xs =>
      rcases xs with ⟨l⟩
      rcases l with _ | ⟨y0, _ | ⟨y1, _ | ⟨y2, l⟩⟩⟩ <;>
        simp [substOwn, VE.Bridge.decodeTerm, Json.getArr?, bind, Except.bind, pure, Except.pure, throw, throwThe, MonadExceptOf.throw] at h ⊢
      split at h <;> rename_i heq <;> simp only [List.cons.injEq, and_true] at heq <;> try simp at h
      · rename_i i
        cases i <;> simp [Json.getNat?, throw, throwThe, MonadExceptOf.throw] at h
        rw [heq.1, heq.2]
        exact ⟨substOwn_scalar g₂ hg m y0 _ (by simp) (by simp) heq.1,
          substOwn_scalar g₂ hg m y1 _ (by simp) (by simp) heq.2⟩
      · rw [heq.1, heq.2]
        exact ⟨substOwn_scalar g₂ hg m y0 _ (by simp) (by simp) heq.1,
          substOwn_scalar g₂ hg m y1 _ (by simp) (by simp) heq.2⟩
    | obj => simp [substOwn, VE.Bridge.decodeTerm, Json.getArr?, bind, Except.bind] at h
    | _ => rfl

theorem substOwn_str {g : Json} (hg : ∃ a, g = .arr a) :
    ∀ (m : Nat) (x : Json) (s : String), substOwn g m x = .str s → x = .str s
  | 0, _, _, h => h
  | m + 1, x, s, h => by
    obtain ⟨a, rfl⟩ := hg
    cases x with
    | str s' => by_cases hs : s' = "own" <;> simp_all [substOwn]
    | arr => simp [substOwn] at h
    | obj => simp [substOwn] at h
    | _ => simp [substOwn] at h

theorem substOwn_str_self (g : Json) (s : String) (hs : s ≠ "own") : ∀ m, substOwn g m (.str s) = .str s
  | 0 => rfl
  | _ + 1 => by simp [substOwn, hs]

theorem budgetFormula_arr {n k : Nat} {j : Json} {r : VE.Formula × Nat} (h : budgetFormula n k j = .ok r) :
    ∃ a, j = .arr a := by
  cases n with
  | zero => simp [budgetFormula, throw, throwThe, MonadExceptOf.throw] at h
  | succ n =>
    unfold budgetFormula at h
    cases j <;> simp only [Json.getArr?, bind, Except.bind, pure, Except.pure, throw, throwThe,
      MonadExceptOf.throw] at h <;> first | exact ⟨_, rfl⟩ | (split at h <;> simp at h)

theorem budgetFormula_not_term {n k : Nat} {j : Json} {r : VE.Formula × Nat} (h : budgetFormula n k j = .ok r)
    (t : VE.Term) : VE.Bridge.decodeTerm j ≠ .ok t := by
  intro ht
  obtain ⟨⟨l⟩, rfl⟩ := budgetFormula_arr h
  cases n with
  | zero => simp [budgetFormula, throw, throwThe, MonadExceptOf.throw] at h
  | succ n =>
    unfold VE.Bridge.decodeTerm at ht
    simp only [Json.getArr?, bind, Except.bind, pure, Except.pure] at ht
    unfold budgetFormula at h
    simp only [Json.getArr?, bind, Except.bind, pure, Except.pure, throw, throwThe, MonadExceptOf.throw] at h
    split at ht <;> (try simp [throw, throwThe, MonadExceptOf.throw] at ht) <;> (split at h <;> simp at h)

theorem elt_str {g₁ : Json} (g₂ : Json) (hg : ∃ a, g₁ = .arr a) {m : Nat} {y : Json} {s : String}
    (hv : substOwn g₁ m y = .str s) : substOwn g₂ m y = substOwn g₁ m y := by
  rw [hv]; exact substOwn_scalar g₂ hg m y _ (by simp) (by simp) hv

theorem elt_term {g₁ : Json} (g₂ : Json) (hg : ∃ a, g₁ = .arr a) (ht : ∀ t, VE.Bridge.decodeTerm g₁ ≠ .ok t)
    {m k : Nat} {y : Json} {p : VE.Term × Nat} (hv : budgetTerm k (substOwn g₁ m y) = .ok p) :
    substOwn g₂ m y = substOwn g₁ m y :=
  substOwn_term g₂ hg ht m y p.1 (budgetTerm_ok hv).1

/-! The chain's decoder (sc-2d): what spec 5.4's effect theorems need of it. A formula that decodes under a node count
    decodes, as the same formula, under any smaller one; W1's reader takes each field from its member of the rule
    object, and the guard and each carve-out are read by `decodeBudgeted`; the soft reader takes each soft field from
    its member and the rule's name. -/

theorem budgetTerm_mono {k : Nat} {j : Json} {t : VE.Term} {c : Nat} (h : budgetTerm k j = .ok (t, c))
    {k' : Nat} {r : Except String (VE.Term × Nat)} (hr : budgetTerm k' j = r) (hk : k' ≤ k) :
    ∃ c', r = .ok (t, c') ∧ c' ≤ c := by
  subst hr
  obtain ⟨hd, rfl⟩ := budgetTerm_ok h
  refine ⟨k' + 1, ?_, by omega⟩
  have hm : ¬ k + 1 > VE.Limits.maxNodes := by
    intro hm; unfold budgetTerm at h; simp [hm, bind, Except.bind] at h
  have hm' : ¬ k' + 1 > VE.Limits.maxNodes := by omega
  unfold budgetTerm at h ⊢
  simp only [hm, hm', hd, if_false, bind, Except.bind, pure, Except.pure] at h ⊢
  cases t <;> simp at h ⊢ <;> (try split at h) <;> simp_all

/-- A formula that decodes under a node count decodes, as the same formula, under any smaller count. -/
theorem budgetFormula_mono : ∀ (n k : Nat) (j : Json) (φ : VE.Formula) (c : Nat),
    budgetFormula n k j = .ok (φ, c) → ∀ {k' : Nat} {r : Except String (VE.Formula × Nat)},
      budgetFormula n k' j = r → k' ≤ k → ∃ c', r = .ok (φ, c') ∧ c' ≤ c
  | 0, _, _, _, _, h, _, _, _, _ => by simp [budgetFormula, throw, throwThe, MonadExceptOf.throw] at h
  | n + 1, k, j, φ, c, h, k', r, hr, hk => by
    have ih := budgetFormula_mono n
    unfold budgetFormula at h hr
    have hm : ¬ k + 1 > VE.Limits.maxNodes := by intro hm; simp [hm, bind, Except.bind] at h
    have hm' : ¬ k' + 1 > VE.Limits.maxNodes := by omega
    simp only [hm, hm', if_false] at h hr
    cases j <;> simp only [Json.getArr?, bind, Except.bind, pure, Except.pure, throw, throwThe,
      MonadExceptOf.throw] at h hr <;> try (cases h)
    split at h <;> rename_i heq <;> (try (simp at h; done)) <;> simp only [heq] at hr
    all_goals
      repeat
        split at h
        · cases h
        rename_i v hv
        obtain ⟨v₁, v₂⟩ := v
        split at hr
        · rename_i e he
          obtain ⟨_, h₁, _⟩ : ∃ c', _ ∧ _ := by
            first | exact budgetTerm_mono hv he (by omega) | exact ih _ _ _ _ hv he (by omega)
          cases h₁
        rename_i w hw
        obtain ⟨c₁, h₁, hle⟩ : ∃ c', _ ∧ _ := by
          first | exact budgetTerm_mono hv hw (by omega) | exact ih _ _ _ _ hv hw (by omega)
        cases h₁
    all_goals (cases h; subst hr; exact ⟨_, rfl, by omega⟩)

theorem decodeBudgeted_of {n k : Nat} {j : Json} {φ : VE.Formula} {c : Nat} (h : budgetFormula n k j = .ok (φ, c))
    (hn : n = VE.Limits.maxDepth) : VE.Norms.Wire.decodeBudgeted j = .ok φ := by
  subst hn
  obtain ⟨_, h₁, _⟩ := budgetFormula_mono _ _ _ _ _ h rfl (Nat.zero_le k)
  simp [VE.Norms.Wire.decodeBudgeted, h₁, Functor.map, Except.map]

theorem budgetFormula_and {n k : Nat} {a b : Json} {φ : VE.Formula} {c : Nat}
    (h : budgetFormula n k (.arr #[.str "and", a, b]) = .ok (φ, c)) :
    ∃ A B, (∃ n k c, budgetFormula n k a = .ok (A, c)) ∧ (∃ n k c, budgetFormula n k b = .ok (B, c)) ∧ φ = .and A B := by
  cases n with
  | zero => simp [budgetFormula, throw, throwThe, MonadExceptOf.throw] at h
  | succ n =>
    unfold budgetFormula at h
    simp only [Json.getArr?, bind, Except.bind, pure, Except.pure, throw, throwThe, MonadExceptOf.throw] at h
    split at h
    · cases h
    split at h <;> (try (cases h; done)) <;> rename_i heq <;> (try (simp at heq; done))
    · simp only [List.cons.injEq, and_true] at heq
      obtain ⟨-, rfl, rfl⟩ := heq
      split at h
      · cases h
      rename_i v hv
      split at h
      · cases h
      rename_i w hw
      cases h
      exact ⟨_, _, ⟨_, _, _, hv⟩, ⟨_, _, _, hw⟩, rfl⟩

/-- The guard a narrowing writes decodes as the conjunction of the old guard and the narrowing's condition. -/
theorem narrowed_guard {g C : Json} {G C' φ : VE.Formula} (hg : VE.Norms.Wire.decodeBudgeted g = .ok G)
    (hC : VE.Norms.Wire.decodeBudgeted C = .ok C') (h : VE.Norms.Wire.decodeBudgeted (.arr #[.str "and", g, C]) = .ok φ) :
    φ = .and G C' := by
  obtain ⟨_, hb⟩ := decodeBudgeted_ok h
  obtain ⟨A, B, ⟨_, _, _, hA⟩, ⟨_, _, _, hB⟩, rfl⟩ := budgetFormula_and hb
  obtain ⟨_, hA'⟩ := decodeBudgeted_ok hg
  obtain ⟨_, hB'⟩ := decodeBudgeted_ok hC
  rw [budgetFormula_val _ _ _ _ _ _ _ _ _ hA hA', budgetFormula_val _ _ _ _ _ _ _ _ _ hB hB']

theorem guard_comm {g a b : Json} {φ ψ : VE.Formula}
    (h₁ : VE.Norms.Wire.decodeBudgeted (.arr #[.str "and", .arr #[.str "and", g, a], b]) = .ok φ)
    (h₂ : VE.Norms.Wire.decodeBudgeted (.arr #[.str "and", .arr #[.str "and", g, b], a]) = .ok ψ)
    (S : VE.Structure.{v}) (ρ : VE.Valuation S) : φ.denote S ρ ↔ ψ.denote S ρ := by
  obtain ⟨_, h₁⟩ := decodeBudgeted_ok h₁
  obtain ⟨_, h₂⟩ := decodeBudgeted_ok h₂
  obtain ⟨X, B, ⟨_, _, _, hX⟩, ⟨_, _, _, hB⟩, rfl⟩ := budgetFormula_and h₁
  obtain ⟨G, A, ⟨_, _, _, hG⟩, ⟨_, _, _, hA⟩, rfl⟩ := budgetFormula_and hX
  obtain ⟨X', A', ⟨_, _, _, hX'⟩, ⟨_, _, _, hA'⟩, rfl⟩ := budgetFormula_and h₂
  obtain ⟨G', B', ⟨_, _, _, hG'⟩, ⟨_, _, _, hB'⟩, rfl⟩ := budgetFormula_and hX'
  rw [budgetFormula_val _ _ _ _ _ _ _ _ _ hG' hG, budgetFormula_val _ _ _ _ _ _ _ _ _ hA' hA,
    budgetFormula_val _ _ _ _ _ _ _ _ _ hB' hB]
  simp only [VE.Formula.denote]
  exact and_right_comm

/-- The carve-out loop of W1's decoder appends the decoded value of each member, in order. -/
theorem forIn_carve {f : Json → MProd (List VE.Formula) Nat → Except String (ForInStep (MProd (List VE.Formula) Nat))}
    (hf : ∀ x s r, f x s = .ok r → ∃ φ, VE.Norms.Wire.decodeBudgeted x = .ok φ ∧ ∃ c, r = .yield ⟨s.1 ++ [φ], c⟩) :
    ∀ (xs : List Json) (s r : MProd (List VE.Formula) Nat), forIn xs s f = .ok r →
      (∀ x ∈ xs, ∃ φ, VE.Norms.Wire.decodeBudgeted x = .ok φ) ∧
        r.1 = s.1 ++ xs.filterMap (fun x => (VE.Norms.Wire.decodeBudgeted x).toOption)
  | [], s, r, h => by simp [pure, Except.pure] at h; subst h; simp
  | x :: xs, s, r, h => by
    simp only [List.forIn_cons, bind, Except.bind] at h
    cases hx : f x s with
    | error e => rw [hx] at h; cases h
    | ok st =>
      rw [hx] at h
      obtain ⟨φ, hφ, c, rfl⟩ := hf x s st hx
      obtain ⟨hall, hr⟩ := forIn_carve hf xs _ r h
      refine ⟨fun y hy => ?_, ?_⟩
      · rcases List.mem_cons.mp hy with rfl | hy
        · exact ⟨φ, hφ⟩
        · exact hall y hy
      · simp [hr, hφ, Except.toOption]

open VE.NormDefaults (ebind_ok) in
/-- What W1's field reader reads: each field from its member of the rule object. -/
theorem normFields_spec (j : Json) (r : String × String × Bool × Json × List Json × List String)
    (h : VE.Norms.Wire.normFields j = .ok r) :
    let raw := j.getObjValD "norm"
    raw.getObjValD "name" = .str r.1 ∧ VE.Bridge.stringField raw "predicate" = .ok r.2.1 ∧
      raw.getObjValD "sign" = .bool r.2.2.1 ∧ r.2.2.2.1 = raw.getObjValD "guard" ∧
      (∃ xs, raw.getObjValD "unless" = .arr xs ∧ r.2.2.2.2.1 = xs.toList) ∧
      VE.Bridge.strings (raw.getObjValD "over") = .ok r.2.2.2.2.2 := by
  unfold VE.Norms.Wire.normFields at h
  obtain ⟨_, -, h⟩ := (ebind_ok _ _ _).mp h
  obtain ⟨raw, hr, h⟩ := (ebind_ok _ _ _).mp h
  obtain ⟨_, -, h⟩ := (ebind_ok _ _ _).mp h
  have hj : j.getObjValD "norm" = raw := by simp [Json.getObjValD, hr, Except.toOption]
  simp only [hj]
  cases hn : raw.getObjValD "name" with
  | str s =>
    simp only [hn] at h
    cases hp : VE.Bridge.stringField raw "predicate" <;> simp only [hp, bind, Except.bind, pure, Except.pure] at h
    · cases h
    split at h <;> try simp only [bind, Except.bind, pure, Except.pure, throw, throwThe, MonadExceptOf.throw] at h
    · split at h <;> try simp only [bind, Except.bind, pure, Except.pure, throw, throwThe, MonadExceptOf.throw] at h
      · split at h <;> try simp only [bind, Except.bind, pure, Except.pure, throw, throwThe, MonadExceptOf.throw] at h
        · revert h; cases hs : VE.Bridge.strings (raw.getObjValD "over") <;> intro h
          · cases h
          · cases h; simp_all
        · cases h
      · cases h
    · cases h
  | _ => simp [hn, bind, Except.bind] at h

theorem w1_spec (j raw : Json) (hj : j.getObjValD "norm" = raw) (sh : Bool) (N : VE.Norms.Node)
    (h : VE.Norms.Wire.decodeNorm j sh = .ok N) :
    raw.getObjValD "name" = .str N.name ∧ VE.Bridge.stringField raw "predicate" = .ok N.pred ∧
      raw.getObjValD "sign" = .bool N.sign ∧ VE.Bridge.strings (raw.getObjValD "over") = .ok N.over ∧
      VE.Norms.Wire.decodeBudgeted (raw.getObjValD "guard") = .ok N.guard ∧
      ∃ xs, raw.getObjValD "unless" = .arr xs ∧ (∀ x ∈ xs.toList, ∃ φ, VE.Norms.Wire.decodeBudgeted x = .ok φ) ∧
        N.carveOuts = xs.toList.filterMap (fun x => (VE.Norms.Wire.decodeBudgeted x).toOption) := by
  unfold VE.Norms.Wire.decodeNorm at h
  obtain ⟨r, hf, h⟩ := (VE.NormDefaults.ebind_ok _ _ _).mp h
  obtain ⟨nm, pr, sg, gJ, uJ, ov⟩ := r
  obtain ⟨hn, hp, hs, hgJ, ⟨xs, hx, hu⟩, ho⟩ := normFields_spec _ _ hf
  obtain ⟨⟨G, c⟩, hg, h⟩ := (VE.NormDefaults.ebind_ok _ _ _).mp h
  obtain ⟨⟨carve, cnt⟩, hl, h⟩ := (VE.NormDefaults.ebind_ok _ _ _).mp h
  cases h
  simp only [hj] at hn hp hs hgJ hx ho hu
  subst hu hgJ
  obtain ⟨hall, hc⟩ := forIn_carve (fun x s r hr => by
      obtain ⟨⟨φ, n⟩, hb, hr⟩ := (VE.NormDefaults.ebind_ok _ _ _).mp hr
      exact ⟨φ, decodeBudgeted_of hb rfl, n, by cases hr; rfl⟩) _ _ _ hl
  exact ⟨hn, hp, hs, ho, decodeBudgeted_of hg rfl, xs, hx, hall, by simpa using hc⟩

open VE.NormDefaults (ebind_ok) in
theorem ite_bind_ok {ε α β : Type} {c : Prop} [Decidable c] (a b : Except ε α) (k : α → Except ε β) (r : β)
    (h : (if c then a >>= k else b >>= k) = .ok r) : ∃ u, k u = .ok r := by
  split at h <;> obtain ⟨u, -, h⟩ := (ebind_ok _ _ _).mp h <;> exact ⟨u, h⟩

open VE.NormDefaults (ebind_ok) in
open VE.SoftNorms (SoftNode) in
theorem ruleFields_spec (x : Option String) (j : Json) (R : SoftNode)
    (h : VE.SoftNorms.Phases.ruleFields x j = .ok R) :
    let raw := j.getObjValD "norm"
    (∃ obj, VE.Bridge.fields raw = .ok obj ∧
      VE.Norms.Wire.decodeNorm (Json.mkObj [("norm", Json.mkObj (obj.filter
        (fun kv => VE.SoftNorms.Phases.w1Keys.contains kv.1)))]) false = .ok R.toNode) ∧
    R.mode = (match raw.getObjVal? "mode" with | .ok (.str "default") => .default | _ => .strict) ∧
    R.rank = (match raw.getObjVal? "rank" with | .ok (.str r) => some r | _ => none) ∧
    R.alterable = (match raw.getObjVal? "alterable" with | .ok v => (VE.Bridge.strings v).toOption.getD [] | _ => []) ∧
    R.hard = (match raw.getObjVal? "hard" with | .ok (.bool b) => b | _ => false) ∧
    R.exception = (match raw.getObjVal? "exception" with
      | .ok .null | .error _ => none
      | .ok e => (VE.SoftNorms.Phases.exceptionFields x R.name e).toOption) ∧
    R.splitFrom = none := by
  unfold VE.SoftNorms.Phases.ruleFields at h
  extract_lets raw seen given k₁ at h
  split at h
  · obtain ⟨_, -, h⟩ := (ebind_ok _ _ _).mp h
    simp -zeta only [k₁] at h
    obtain ⟨obj, ho, h⟩ := (ebind_ok _ _ _).mp h
    extract_lets keys k₂ at h
    split at h
    · obtain ⟨_, -, h⟩ := (ebind_ok _ _ _).mp h
      simp -zeta only [k₂] at h
      obtain ⟨N, hN, h⟩ := (ebind_ok _ _ _).mp h
      simp only [VE.SoftNorms.Phases.inherited] at ho hN
      split at ho <;> cases ho
      split at hN <;> cases hN
      extract_lets bad j₁ j₂ j₃ at h
      obtain ⟨_, h⟩ := ite_bind_ok _ _ _ _ h
      simp -zeta only [j₃] at h
      obtain ⟨_, h⟩ := ite_bind_ok _ _ _ _ h
      simp -zeta only [j₂] at h
      obtain ⟨_, -, h⟩ := (ebind_ok _ _ _).mp h
      obtain ⟨md, hmd, h⟩ : ∃ y, y = (match raw.getObjVal? "mode" with
          | .ok (.str "default") => VE.SoftNorms.Mode.default | _ => .strict) ∧ j₁ y = .ok R := by
        split at h <;> rename_i heq <;> obtain ⟨u, hu, h⟩ := (ebind_ok _ _ _).mp h <;>
          simp only [pure, Except.pure, VE.SoftNorms.Phases.fail, reduceCtorEq, Except.ok.injEq] at hu <;>
          exact ⟨u, by subst hu; simp [heq], h⟩
      simp -zeta only [j₁] at h
      extract_lets jr at h
      obtain ⟨rk, hrk, h⟩ : ∃ y, y = (match raw.getObjVal? "rank" with
          | .ok (.str r) => some r | _ => none) ∧ jr y = .ok R := by
        split at h <;> rename_i heq <;> obtain ⟨u, hu, h⟩ := (ebind_ok _ _ _).mp h <;>
          simp only [pure, Except.pure, VE.SoftNorms.Phases.fail, reduceCtorEq, Except.ok.injEq] at hu <;>
          exact ⟨u, by subst hu; simp [heq], h⟩
      simp -zeta only [jr] at h
      extract_lets ja at h
      obtain ⟨al, hal, h⟩ : ∃ y, y = (match raw.getObjVal? "alterable" with
          | .ok v => (VE.Bridge.strings v).toOption.getD [] | _ => []) ∧ ja y = .ok R := by
        split at h <;> rename_i heq
        · obtain ⟨u, hu, h⟩ := (ebind_ok _ _ _).mp h
          simp only [pure, Except.pure, Except.ok.injEq] at hu
          exact ⟨u, by subst hu; simp [heq], h⟩
        · split at h <;> rename_i heq' <;> obtain ⟨u, hu, h⟩ := (ebind_ok _ _ _).mp h <;>
            simp only [pure, Except.pure, VE.SoftNorms.Phases.fail, reduceCtorEq, Except.ok.injEq] at hu
          exact ⟨u, by subst hu; simp [heq, heq', Except.toOption], h⟩
      simp -zeta only [ja] at h
      extract_lets jh jb at h
      obtain ⟨_, h⟩ := ite_bind_ok _ _ _ _ h
      simp -zeta only [jb] at h
      obtain ⟨hd, hhd, h⟩ : ∃ y, y = (match raw.getObjVal? "hard" with
          | .ok (.bool b) => b | _ => false) ∧ jh y = .ok R := by
        split at h <;> rename_i heq <;> obtain ⟨u, hu, h⟩ := (ebind_ok _ _ _).mp h <;>
          simp only [pure, Except.pure, VE.SoftNorms.Phases.fail, reduceCtorEq, Except.ok.injEq] at hu <;>
          exact ⟨u, by subst hu; simp [heq], h⟩
      simp -zeta only [jh] at h
      extract_lets je jc at h
      obtain ⟨_, h⟩ := ite_bind_ok _ _ _ _ h
      simp -zeta only [jc] at h
      have hg : given = (match raw.getObjVal? "exception" with | .error _ | .ok .null => none | .ok e => some e) := rfl
      clear_value given
      obtain ⟨ex, hex, h⟩ : ∃ y, y = (match raw.getObjVal? "exception" with
          | .ok .null | .error _ => none
          | .ok e => (VE.SoftNorms.Phases.exceptionFields x N.name e).toOption) ∧ je y = .ok R := by
        split at h <;> obtain ⟨u, hu, h⟩ := (ebind_ok _ _ _).mp h
        all_goals first | (simp [VE.SoftNorms.Phases.fail] at hu; done) | skip
        · simp only [pure, Except.pure, Except.ok.injEq] at hu
          subst hu; refine ⟨_, ?_, h⟩
          split <;> rename_i heq <;> simp only [heq] at hg <;> first | rfl | (simp at hg; done) | cases hg
        · simp only [Functor.map, Except.map] at hu
          split at hu
          · cases hu
          rename_i v hv
          simp only [Except.ok.injEq] at hu
          subst hu; refine ⟨_, ?_, h⟩
          split <;> rename_i heq <;> simp only [heq] at hg <;> first | cases hg | skip
          simp [hv, Except.toOption]
      simp -zeta only [je] at h
      cases h
      subst hmd hrk hal hhd hex
      exact ⟨⟨obj, by assumption, by assumption⟩, rfl, rfl, rfl, rfl, rfl, rfl⟩
    · obtain ⟨_, h', -⟩ := (ebind_ok _ _ _).mp h; cases h'
  · obtain ⟨_, h', -⟩ := (ebind_ok _ _ _).mp h; cases h'

open VE.SoftNorms (SoftNode) in
theorem decodeSoft_rule (se : VE.SoftNorms.Wire.SoftEnvironment) (j : Json) (N : SoftNode)
    (h : VE.SoftNorms.Wire.decodeSoftNorm se j = .ok N) : VE.SoftNorms.Phases.ruleFields se.soft.exceptionDecider j = .ok N := by
  unfold VE.SoftNorms.Wire.decodeSoftNorm at h
  split at h
  · next R hR =>
      cases h
      obtain ⟨R', hR', h⟩ := (VE.NormDefaults.ebind_ok _ _ _).mp hR
      revert h; cases VE.SoftNorms.Phases.ruleReferences _ _ R' <;> simp [Except.map]
      intro h; subst h; exact hR'
  · cases h

theorem narrowing_some {c C : Json} (h : narrowing c = some C) :
    c = .arr #[.str "and", .str "own", C] ∧ hasOwn depthLimit C = false := by
  revert h
  cases c with
  | arr xs =>
    rcases xs with ⟨_ | ⟨a, _ | ⟨b, _ | ⟨D, _ | ⟨_, _⟩⟩⟩⟩⟩
    all_goals delta narrowing narrowing.match_1; dsimp only
    all_goals try (simp; done)
    split
    · simp only [Array.getLit, List.getElem_toArray, List.getElem_cons_zero, List.getElem_cons_succ]
      cases a <;> dsimp only <;> (try (simp; done))
      rename_i s _
      by_cases hs : s = "and"
      · subst hs
        simp only [dite_true]
        cases b <;> dsimp only <;> (try (simp; done))
        rename_i t _
        by_cases ht : t = "own"
        · subst ht
          simp only [dite_true]
          split <;> simp_all <;> (rintro rfl; assumption)
        · simp [ht]
      · simp [hs]
    · simp
  | _ => delta narrowing narrowing.match_1; dsimp only; simp

theorem anyF_snoc (l : List VE.Formula) (C : VE.Formula) : VE.Norms.anyF (l ++ [C]) = .or (VE.Norms.anyF l) C := by
  simp [VE.Norms.anyF, List.foldl_append]

/-! Loops -/

/-- A loop over a list fails only with an error of its body. -/
theorem forIn_error {α : Type} (P : String → Prop) (f : α → PUnit.{1} → Except String (ForInStep PUnit.{1}))
    (hf : ∀ x e, f x PUnit.unit = .error e → P e) :
    ∀ (l : List α) (e : String), forIn l PUnit.unit f = .error e → P e
  | [], e, h => by simp [pure, Except.pure] at h
  | x :: l, e, h => by
    simp only [List.forIn_cons, bind, Except.bind] at h
    cases hx : f x PUnit.unit with
    | error e' => rw [hx] at h; cases h; exact hf x e hx
    | ok r => rw [hx] at h; cases r with
      | done => simp [pure, Except.pure] at h
      | yield => exact forIn_error P f hf l e h

theorem scopeOrder_prefix (a b c : String) :
    (toString "ScopeOrder: " ++ toString a ++ toString ": " ++ toString b ++ toString ", " ++ toString c).startsWith
      "ScopeOrder" = true := by
  have := VE.Readings.startsWith_append_ascii "ScopeOrder" (": " ++ a ++ ": " ++ b ++ ", " ++ c) (by decide)
  simpa only [toString, String.append_assoc] using this

end VE.Scope
