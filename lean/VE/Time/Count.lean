import VE.Order.Finite

/-! Bounded user-sort counting sugar (units-schema §5), expanded on core order@0
formulas exactly as Python `ve/surface/count.py` does, and its meaning.

The expansion nests one fresh binder per witness. Under binder `j` it lists
`x_j != x_1, ..., x_j != x_(j-1)` in that order, then the counted body with its
outer references shifted past the `j - 1` earlier binders, then the next binder.
`expand_atLeast_iff` proves the expansion holds exactly when at least `n`
distinct objects satisfy the body, in every structure and outer scope;
`expand_atLeast_eval_iff` is the finite-model form. Lean does not recover the
sugar from an already expanded statement; the `count` route case regenerates
the canonical expansion so Python's can be compared with it. -/
namespace VE.Time
universe u
open VE.Order (Structure Value Term Formula FiniteModel)

/-- Shift variables at or above `c` by `k` (Python `_rebase`). -/
def Term.liftFrom (c k : Nat) : Term → Term
  | .var i => if i < c then .var i else .var (i + k)
  | .const n => .const n
  | .num z => .num z
  | .add t u => .add (Term.liftFrom c k t) (Term.liftFrom c k u)
  | .scale z t => .scale z (Term.liftFrom c k t)

def Formula.liftFrom (c k : Nat) : Formula → Formula
  | .top => .top
  | .bottom => .bottom
  | .unary p t => .unary p (Term.liftFrom c k t)
  | .binary p t u => .binary p (Term.liftFrom c k t) (Term.liftFrom c k u)
  | .eq t u => .eq (Term.liftFrom c k t) (Term.liftFrom c k u)
  | .lt t u => .lt (Term.liftFrom c k t) (Term.liftFrom c k u)
  | .le t u => .le (Term.liftFrom c k t) (Term.liftFrom c k u)
  | .not a => .not (Formula.liftFrom c k a)
  | .and a b => .and (Formula.liftFrom c k a) (Formula.liftFrom c k b)
  | .or a b => .or (Formula.liftFrom c k a) (Formula.liftFrom c k b)
  | .implies a b => .implies (Formula.liftFrom c k a) (Formula.liftFrom c k b)
  | .all s a => .all s (Formula.liftFrom (c + 1) k a)
  | .ex s a => .ex s (Formula.liftFrom (c + 1) k a)

theorem term_liftFrom_denote (S : Structure.{u}) (xs ys zs : VE.Order.Valuation S) (t : Term) :
    (Term.liftFrom xs.length ys.length t).denote S (xs ++ (ys ++ zs)) = t.denote S (xs ++ zs) := by
  induction t with
  | var i =>
    simp only [Term.liftFrom]
    split
    · rename_i h
      simp [Term.denote, List.getElem?_append_left h]
    · rename_i h
      simp only [Term.denote]
      rw [List.getElem?_append_right (by omega), List.getElem?_append_right (by omega),
        List.getElem?_append_right (by omega)]
      congr 1
      omega
  | const n => rfl
  | num z => rfl
  | add t u it iu => simp only [Term.liftFrom, Term.denote, it, iu]
  | scale z t it => simp only [Term.liftFrom, Term.denote, it]

theorem liftFrom_denote (S : Structure.{u}) (a : Formula) :
    ∀ (xs ys zs : VE.Order.Valuation S),
      (Formula.liftFrom xs.length ys.length a).denote S (xs ++ (ys ++ zs)) ↔
        a.denote S (xs ++ zs) := by
  induction a with
  | top | bottom => intros; rfl
  | unary p t => intros; simp only [Formula.liftFrom, Formula.denote, term_liftFrom_denote]
  | binary p t u => intros; simp only [Formula.liftFrom, Formula.denote, term_liftFrom_denote]
  | eq t u => intros; simp only [Formula.liftFrom, Formula.denote, term_liftFrom_denote]
  | lt t u => intros; simp only [Formula.liftFrom, Formula.denote, term_liftFrom_denote]
  | le t u => intros; simp only [Formula.liftFrom, Formula.denote, term_liftFrom_denote]
  | not a ih => intro xs ys zs; simp only [Formula.liftFrom, Formula.denote, ih]
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro xs ys zs; simp only [Formula.liftFrom, Formula.denote, ia, ib]
  | all s a ih =>
    intro xs ys zs
    simp only [Formula.liftFrom, Formula.denote]
    exact forall_congr' fun v => imp_congr_right fun _ => ih (.inl v :: xs) ys zs
  | ex s a ih =>
    intro xs ys zs
    simp only [Formula.liftFrom, Formula.denote]
    exact exists_congr fun v => and_congr_right fun _ => ih (.inl v :: xs) ys zs

/-- Right-associated conjunction with no trailing `true`. -/
def chain : List Formula → Formula
  | [] => .top
  | [a] => a
  | a :: b :: rest => .and a (chain (b :: rest))

theorem chain_denote (S : Structure.{u}) (ρ : VE.Order.Valuation S) :
    ∀ parts : List Formula, (chain parts).denote S ρ ↔ ∀ a ∈ parts, a.denote S ρ
  | [] => by simp [chain, Formula.denote]
  | [a] => by simp [chain]
  | a :: b :: rest => by
    simp only [chain, Formula.denote, chain_denote S ρ (b :: rest), List.mem_cons, forall_eq_or_imp]

/-- `x_j != x_i` for `i = 1, ..., j - 1`, in that order. -/
def distinct (j : Nat) : List Formula :=
  (List.range (j - 1)).map (fun i => .not (.eq (.var 0) (.var (j - (i + 1)))))

/-- Binder `j` of `r` remaining binders. -/
def expandFrom (s : String) (body : Formula) : Nat → Nat → Formula
  | _, 0 => .top
  | j, 1 => .ex s (chain (distinct j ++ [Formula.liftFrom 1 (j - 1) body]))
  | j, r + 2 => .ex s (chain (distinct j ++
      [Formula.liftFrom 1 (j - 1) body, expandFrom s body (j + 1) (r + 1)]))

def atLeast (s : String) (n : Nat) (body : Formula) : Formula :=
  if n = 0 then .top else expandFrom s body 1 n

def exactly (s : String) (n : Nat) (body : Formula) : Formula :=
  .and (atLeast s n body) (.not (atLeast s (n + 1) body))

def atMost (s : String) (n : Nat) (body : Formula) : Formula :=
  .not (atLeast s (n + 1) body)

def nOfM (s : String) (n m : Nat) (selected property : Formula) : Formula :=
  .and (exactly s m selected) (exactly s n (.and selected property))

theorem mem_distinct {j : Nat} {a : Formula} :
    a ∈ distinct j ↔ ∃ m, m < j - 1 ∧ a = .not (.eq (.var 0) (.var (m + 1))) := by
  simp only [distinct, List.mem_map, List.mem_range]
  constructor
  · rintro ⟨i, hi, rfl⟩
    exact ⟨j - 2 - i, by omega, by congr 3; omega⟩
  · rintro ⟨m, hm, rfl⟩
    exact ⟨j - 2 - m, by omega, by congr 3; omega⟩

theorem distinct_denote (S : Structure.{u}) (ρ : VE.Order.Valuation S) (x : S.Carrier)
    (ws : List S.Carrier) (j : Nat) (hj : ws.length = j - 1) :
    (∀ a ∈ distinct j, a.denote S (.inl x :: (ws.map .inl ++ ρ))) ↔ x ∉ ws := by
  have key : ∀ m, m < j - 1 →
      ((Formula.not (.eq (.var 0) (.var (m + 1)))).denote S (.inl x :: (ws.map .inl ++ ρ)) ↔
        ws[m]? ≠ some x) := by
    intro m hm
    have hm' : m < (ws.map (Sum.inl : S.Carrier → Value S.Carrier)).length := by simp; omega
    simp only [Formula.denote, Term.denote, List.getElem?_cons_zero, List.getElem?_cons_succ,
      List.getElem?_append_left hm', List.getElem?_map, Option.some.injEq, exists_eq_left',
      Option.map_eq_some_iff, Sum.inl.injEq, ne_eq]
    constructor
    · intro h he; exact h ⟨x, he, rfl⟩
    · rintro h ⟨y, hy, rfl⟩; exact h hy
  constructor
  · intro h hx
    obtain ⟨m, hm, he⟩ := List.getElem_of_mem hx
    exact (key m (by omega)).mp (h _ (mem_distinct.mpr ⟨m, by omega, rfl⟩))
      (by rw [List.getElem?_eq_getElem hm, he])
  · intro hx a ha
    obtain ⟨m, hm, rfl⟩ := mem_distinct.mp ha
    rw [key m hm]
    intro he
    obtain ⟨hlt, heq⟩ := List.getElem?_eq_some_iff.mp he
    exact hx (heq ▸ List.getElem_mem hlt)

theorem body_lift_denote (S : Structure.{u}) (ρ : VE.Order.Valuation S) (x : S.Carrier)
    (ws : List S.Carrier) (j : Nat) (hj : ws.length = j - 1) (body : Formula) :
    (Formula.liftFrom 1 (j - 1) body).denote S (.inl x :: (ws.map .inl ++ ρ)) ↔
      body.denote S (.inl x :: ρ) := by
  have := liftFrom_denote S body [.inl x] (ws.map .inl) ρ
  simpa [hj] using this

/-- The expansion from binder `j` with `r` binders left, after distinct
witnesses `ws` (most recent first). -/
theorem expandFrom_iff (S : Structure.{u}) (ρ : VE.Order.Valuation S) (s : String)
    (body : Formula) :
    ∀ (r j : Nat) (ws : List S.Carrier), 1 ≤ r → ws.length = j - 1 → 1 ≤ j → ws.Nodup →
      ((expandFrom s body j r).denote S (ws.map .inl ++ ρ) ↔
        ∃ ys : List S.Carrier, ys.length = r ∧ (ys ++ ws).Nodup ∧
          ∀ y ∈ ys, S.objects s y ∧ body.denote S (.inl y :: ρ))
  | 0, _, _, h, _, _, _ => absurd h (by decide)
  | 1, j, ws, _, hj, _, hnd => by
    simp only [expandFrom, Formula.denote, chain_denote, List.mem_append, List.mem_singleton]
    constructor
    · rintro ⟨x, hx, hall⟩
      have hd := (distinct_denote S ρ x ws j hj).mp (fun a ha => hall a (Or.inl ha))
      have hb := (body_lift_denote S ρ x ws j hj body).mp (hall _ (Or.inr rfl))
      exact ⟨[x], rfl, List.nodup_cons.mpr ⟨hd, hnd⟩, by simp [hx, hb]⟩
    · rintro ⟨ys, hl, hn, hy⟩
      match ys, hl, hn, hy with
      | [x], _, hn, hy =>
        obtain ⟨hx, hb⟩ := hy x (by simp)
        refine ⟨x, hx, ?_⟩
        rintro a (ha | rfl)
        · exact (distinct_denote S ρ x ws j hj).mpr (List.nodup_cons.mp hn).1 a ha
        · exact (body_lift_denote S ρ x ws j hj body).mpr hb
  | r + 2, j, ws, _, hj, hj1, hnd => by
    simp only [expandFrom, Formula.denote, chain_denote, List.mem_append, List.mem_cons,
      List.not_mem_nil, or_false]
    constructor
    · rintro ⟨x, hx, hall⟩
      have hd := (distinct_denote S ρ x ws j hj).mp (fun a ha => hall a (Or.inl ha))
      have hb := (body_lift_denote S ρ x ws j hj body).mp (hall _ (Or.inr (Or.inl rfl)))
      have hrest := hall _ (Or.inr (Or.inr rfl))
      have ih := expandFrom_iff S ρ s body (r + 1) (j + 1) (x :: ws) (by omega)
        (by simp; omega) (by omega) (List.nodup_cons.mpr ⟨hd, hnd⟩)
      simp only [List.map_cons, List.cons_append] at ih
      obtain ⟨ys, hl, hn, hy⟩ := ih.mp hrest
      refine ⟨x :: ys, by simp [hl], ?_, ?_⟩
      · exact (List.perm_middle.nodup_iff).mp hn
      · intro y hy'
        rcases List.mem_cons.mp hy' with rfl | hy'
        · exact ⟨hx, hb⟩
        · exact hy y hy'
    · rintro ⟨ys, hl, hn, hy⟩
      match ys, hl, hn, hy with
      | x :: ys', hl, hn, hy =>
        obtain ⟨hx, hb⟩ := hy x (by simp)
        have hn' : (ys' ++ x :: ws).Nodup := (List.perm_middle.nodup_iff).mpr hn
        have hxws : x ∉ ws := fun h => (List.nodup_cons.mp hn).1 (by simp [h])
        have ih := expandFrom_iff S ρ s body (r + 1) (j + 1) (x :: ws) (by omega)
          (by simp; omega) (by omega) (List.nodup_cons.mpr ⟨hxws, hnd⟩)
        simp only [List.map_cons, List.cons_append] at ih
        have hrest := ih.mpr ⟨ys', by simpa using hl, hn', fun y h => hy y (by simp [h])⟩
        refine ⟨x, hx, ?_⟩
        rintro a (ha | rfl | rfl)
        · exact (distinct_denote S ρ x ws j hj).mpr hxws a ha
        · exact (body_lift_denote S ρ x ws j hj body).mpr hb
        · exact hrest

/-- **`expand_atLeast_iff`**: the canonical expansion holds iff at least `n`
distinct objects of the sort satisfy the body, in any structure and outer scope. -/
theorem expand_atLeast_iff (S : Structure.{u}) (ρ : VE.Order.Valuation S) (s : String)
    (n : Nat) (body : Formula) :
    (atLeast s n body).denote S ρ ↔
      ∃ xs : List S.Carrier, xs.length = n ∧ xs.Nodup ∧
        ∀ x ∈ xs, S.objects s x ∧ body.denote S (.inl x :: ρ) := by
  unfold atLeast
  split
  · rename_i h
    subst h
    exact ⟨fun _ => ⟨[], rfl, List.nodup_nil, by simp⟩, fun _ => trivial⟩
  · have := expandFrom_iff S ρ s body n 1 [] (by omega) rfl (Nat.le_refl 1) List.nodup_nil
    simpa using this

/-- The finite-model form, for the evaluator's `eval`. -/
theorem expand_atLeast_eval_iff {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (ρ : List (Value α)) (s : String) (n : Nat) (body : Formula) :
    (atLeast s n body).eval M ρ = true ↔
      ∃ xs : List α, xs.length = n ∧ xs.Nodup ∧
        ∀ x ∈ xs, x ∈ M.domains s ∧ body.eval M (.inl x :: ρ) = true := by
  rw [VE.Order.eval_iff_denote, expand_atLeast_iff]
  simp only [VE.Order.eval_iff_denote]

/-- Exact counting is at least `n` and not at least `n + 1`. -/
theorem expand_exactly_iff (S : Structure.{u}) (ρ : VE.Order.Valuation S) (s : String)
    (n : Nat) (body : Formula) :
    (exactly s n body).denote S ρ ↔
      (∃ xs : List S.Carrier, xs.length = n ∧ xs.Nodup ∧
        ∀ x ∈ xs, S.objects s x ∧ body.denote S (.inl x :: ρ)) ∧
      ¬ ∃ xs : List S.Carrier, xs.length = n + 1 ∧ xs.Nodup ∧
        ∀ x ∈ xs, S.objects s x ∧ body.denote S (.inl x :: ρ) := by
  simp only [exactly, Formula.denote, expand_atLeast_iff]

theorem expand_atMost_iff (S : Structure.{u}) (ρ : VE.Order.Valuation S) (s : String)
    (n : Nat) (body : Formula) :
    (atMost s n body).denote S ρ ↔
      ¬ ∃ xs : List S.Carrier, xs.length = n + 1 ∧ xs.Nodup ∧
        ∀ x ∈ xs, S.objects s x ∧ body.denote S (.inl x :: ρ) := by
  simp only [atMost, Formula.denote, expand_atLeast_iff]

end VE.Time
