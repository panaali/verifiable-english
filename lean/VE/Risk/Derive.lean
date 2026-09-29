import VE.Risk.Cond

/-! Endpoint evaluation (docs/spec/risk.md 4.3 and 7.2).

`possibleE b c` and `certainE b c` evaluate the table of 4.3 on `nnf c`: an
atom `f ⋈ 0` is decided by `fmin` and `fmax`, the extremal values of the form
over the box, and the connectives by `∧`/`∨`. The evaluator `endsE` returns
both answers at once and swaps them at a `not` (never reached on `nnf c`),
so the recursion needs no mutual block.

The directions `possibleE_complete` and `certainE_sound` need only scoping.
The others need normal atoms (by type), a well-formed box, separability (on
separable conditions `∃` distributes over `∧` and `∀` over `∨`) and, for `=`
and `≠`, unit coefficients: the values of a unit-coefficient form cover an
integer interval with no gaps (`stepEq_exact`). `witnessE` is the canonical
witness of 4.3. -/
namespace VE.Risk

/-! ## The table -/

def atomPossible (b : Box) (f : LinForm) : Rel → Bool
  | .lt => decide (fmin b f < 0)
  | .le => decide (fmin b f ≤ 0)
  | .eq => decide (fmin b f ≤ 0) && decide (0 ≤ fmax b f)
  | .ne => !(decide (fmin b f = 0) && decide (fmax b f = 0))

def atomCertain (b : Box) (f : LinForm) : Rel → Bool
  | .lt => decide (fmax b f < 0)
  | .le => decide (fmax b f ≤ 0)
  | .eq => decide (fmin b f = 0) && decide (fmax b f = 0)
  | .ne => decide (0 < fmin b f) || decide (fmax b f < 0)

/-- `(possible, certain)` by the table of 4.3; `not` swaps and negates (it never occurs on `nnf c`). -/
def endsE (b : Box) : Cond → Bool × Bool
  | .top => (true, true)
  | .bottom => (false, false)
  | .atom f r => (atomPossible b f.val r, atomCertain b f.val r)
  | .and x y => ((endsE b x).1 && (endsE b y).1, (endsE b x).2 && (endsE b y).2)
  | .or x y => ((endsE b x).1 || (endsE b y).1, (endsE b x).2 || (endsE b y).2)
  | .not x => (!(endsE b x).2, !(endsE b x).1)

/-- 4.3: the table on `nnf c`. -/
def possibleE (b : Box) (c : Cond) : Bool := (endsE b (nnf c)).1
def certainE (b : Box) (c : Cond) : Bool := (endsE b (nnf c)).2

/-! ## Boxes -/

theorem find_some {b : Box} {q : String} {e : BoxEntry} (h : b.find q = some e) :
    e ∈ b.entries ∧ e.name = q := by
  unfold Box.find at h
  exact ⟨List.mem_of_find?_eq_some h, by simpa using List.find?_some h⟩

theorem find_of_mem {b : Box} (hn : (b.entries.map (·.name)).Nodup) {e : BoxEntry} (he : e ∈ b.entries) :
    b.find e.name = some e := by
  unfold Box.find
  generalize b.entries = l at hn he
  induction l with
  | nil => cases he
  | cons x l ih =>
    simp only [List.map_cons, List.nodup_cons] at hn
    rw [List.find?_cons]
    by_cases hx : x = e
    · subst hx; simp
    · have he' : e ∈ l := by
        rcases List.mem_cons.mp he with h | h
        · exact absurd h.symm hx
        · exact h
      have hne : (x.name == e.name) = false := by
        simp only [beq_eq_false_iff_ne, ne_eq]
        intro heq
        exact hn.1 (heq ▸ List.mem_map.mpr ⟨e, he', rfl⟩)
      rw [hne]
      exact ih hn.2 he'

theorem mem_find {b : Box} {q : String} (h : b.mem q = true) :
    ∃ e, b.find q = some e ∧ e ∈ b.entries ∧ e.name = q := by
  unfold Box.mem at h
  cases hf : b.find q with
  | none => rw [hf] at h; cases h
  | some e => exact ⟨e, rfl, find_some hf⟩

theorem inBox_bounds {b : Box} {v : Valuation} (hv : InBox b v) {q : String} (h : b.mem q = true) :
    b.lo q ≤ v q ∧ v q ≤ b.hi q := by
  obtain ⟨e, hf, he, rfl⟩ := mem_find h
  simp only [Box.lo, Box.hi, hf, Option.map_some, Option.getD_some]
  exact hv e he

theorem wf_lo_le_hi {b : Box} (hb : b.WF) (q : String) : b.lo q ≤ b.hi q := by
  unfold Box.lo Box.hi
  cases hf : b.find q with
  | none => simp
  | some e => simp only [Option.map_some, Option.getD_some]; exact hb.2 e (find_some hf).1

theorem isPoint_eq {b : Box} {q : String} (h : b.isPoint q = true) : b.lo q = b.hi q := by
  unfold Box.isPoint at h
  unfold Box.lo Box.hi
  cases hf : b.find q with
  | none => rw [hf] at h; cases h
  | some e => rw [hf] at h; simpa using h

/-- A valuation in a well-formed box takes the value of a point entry. -/
theorem inBox_point {b : Box} {v : Valuation} (hv : InBox b v) {q : String} (hm : b.mem q = true)
    (hp : b.isPoint q = true) : v q = b.lo q := by
  have := inBox_bounds hv hm
  have := isPoint_eq hp
  omega

/-! ## Linear-form bounds -/

theorem term_min_le (b : Box) (v : Valuation) (q : String) (c : Int) (hq : b.lo q ≤ v q ∧ v q ≤ b.hi q) :
    (if 0 ≤ c then c * b.lo q else c * b.hi q) ≤ c * v q := by
  split
  · exact Int.mul_le_mul_of_nonneg_left hq.1 (by assumption)
  · exact Int.mul_le_mul_of_nonpos_left (by omega) hq.2

theorem term_le_max (b : Box) (v : Valuation) (q : String) (c : Int) (hq : b.lo q ≤ v q ∧ v q ≤ b.hi q) :
    c * v q ≤ (if 0 ≤ c then c * b.hi q else c * b.lo q) := by
  split
  · exact Int.mul_le_mul_of_nonneg_left hq.2 (by assumption)
  · exact Int.mul_le_mul_of_nonpos_left (by omega) hq.1

theorem minSum_cons (b : Box) (p : String × Int) (l : List (String × Int)) :
    minSum b (p :: l) = (if 0 ≤ p.2 then p.2 * b.lo p.1 else p.2 * b.hi p.1) + minSum b l := by
  simp [minSum]

theorem maxSum_cons (b : Box) (p : String × Int) (l : List (String × Int)) :
    maxSum b (p :: l) = (if 0 ≤ p.2 then p.2 * b.hi p.1 else p.2 * b.lo p.1) + maxSum b l := by
  simp [maxSum]

theorem sum_bounds (b : Box) (v : Valuation) (hv : InBox b v) :
    ∀ l : List (String × Int), (∀ p ∈ l, b.mem p.1 = true) →
      minSum b l ≤ termSum l v ∧ termSum l v ≤ maxSum b l
  | [], _ => by simp [minSum, maxSum, termSum]
  | p :: l, h => by
    have hp := inBox_bounds hv (h p (List.mem_cons_self ..))
    have ih := sum_bounds b v hv l (fun x hx => h x (List.mem_cons_of_mem _ hx))
    rw [minSum_cons, maxSum_cons, termSum_cons]
    have h1 := term_min_le b v p.1 p.2 hp
    have h2 := term_le_max b v p.1 p.2 hp
    omega

/-- Every value of a scoped form over the box lies between its endpoint values. -/
theorem eval_bounds {b : Box} {v : Valuation} (hv : InBox b v) {f : LinForm}
    (hs : ∀ q ∈ f.names, b.mem q = true) : fmin b f ≤ f.eval v ∧ f.eval v ≤ fmax b f := by
  have := sum_bounds b v hv f.coeffs (fun p hp => hs p.1 (List.mem_map.mpr ⟨p, hp, rfl⟩))
  unfold fmin fmax
  rw [eval_eq_termSum]
  omega

/-! ## Extremal valuations -/

theorem find_coeff {l : List (String × Int)} (hn : (l.map (·.1)).Nodup) {p : String × Int} (hp : p ∈ l) :
    l.find? (·.1 == p.1) = some p := by
  induction l with
  | nil => cases hp
  | cons x l ih =>
    simp only [List.map_cons, List.nodup_cons] at hn
    rw [List.find?_cons]
    by_cases hx : x = p
    · subst hx; simp
    · have hp' : p ∈ l := by
        rcases List.mem_cons.mp hp with h | h
        · exact absurd h.symm hx
        · exact h
      have hne : (x.1 == p.1) = false := by
        simp only [beq_eq_false_iff_ne, ne_eq]
        intro heq
        exact hn.1 (heq ▸ List.mem_map.mpr ⟨p, hp', rfl⟩)
      rw [hne]
      exact ih hn.2 hp'

theorem termSum_congr_terms (v : Valuation) (g : String × Int → Int) :
    ∀ l : List (String × Int), (∀ p ∈ l, p.2 * v p.1 = g p) → termSum l v = (l.map g).sum
  | [], _ => rfl
  | p :: l, h => by
    rw [termSum_cons, List.map_cons, List.sum_cons, h p (List.mem_cons_self ..),
      termSum_congr_terms v g l (fun x hx => h x (List.mem_cons_of_mem _ hx))]

theorem minVal_eval (b : Box) {f : LinForm} (hf : f.Normal) : f.eval (minVal b f) = fmin b f := by
  rw [eval_eq_termSum, fmin, minSum,
    termSum_congr_terms _ (fun (q, c) => if 0 ≤ c then c * b.lo q else c * b.hi q) f.coeffs ?_]
  intro p hp
  simp only [minVal, find_coeff hf.1 hp]
  split <;> first | rfl | trivial

theorem maxVal_eval (b : Box) {f : LinForm} (hf : f.Normal) : f.eval (maxVal b f) = fmax b f := by
  rw [eval_eq_termSum, fmax, maxSum,
    termSum_congr_terms _ (fun (q, c) => if 0 ≤ c then c * b.hi q else c * b.lo q) f.coeffs ?_]
  intro p hp
  simp only [maxVal, find_coeff hf.1 hp]
  split <;> first | rfl | trivial

theorem inBox_of_endpoints {b : Box} (hb : b.WF) {v : Valuation}
    (h : ∀ q, v q = b.lo q ∨ v q = b.hi q) : InBox b v := by
  intro e he
  have hf := find_of_mem hb.1 he
  have hle := hb.2 e he
  rcases h e.name with h | h <;> simp [h, Box.lo, Box.hi, hf] <;> omega

theorem minVal_inBox {b : Box} (hb : b.WF) (f : LinForm) : InBox b (minVal b f) := by
  apply inBox_of_endpoints hb
  intro q
  simp only [minVal]
  split
  · split
    · exact Or.inl rfl
    · exact Or.inr rfl
  · exact Or.inl rfl

theorem maxVal_inBox {b : Box} (hb : b.WF) (f : LinForm) : InBox b (maxVal b f) := by
  apply inBox_of_endpoints hb
  intro q
  simp only [maxVal]
  split
  · split
    · exact Or.inr rfl
    · exact Or.inl rfl
  · exact Or.inl rfl

/-! ## Unit-coefficient forms cover an interval (the `=` witness) -/

def update (v : Valuation) (q : String) (x : Int) : Valuation := fun q' => if q' = q then x else v q'

/-- 4.3: move each quantity of the form, in the form's order, from its minimising endpoint
towards its maximising one until `need` steps are taken (each step changes the form by 1). -/
def stepEq (b : Box) : List (String × Int) → Valuation → Int → Valuation
  | [], v, _ => v
  | (q, c) :: rest, v, need =>
    let δ := min need (b.hi q - b.lo q)
    if c = 1 then stepEq b rest (update v q (b.lo q + δ)) (need - δ)
    else if c = -1 then stepEq b rest (update v q (b.hi q - δ)) (need - δ)
    else stepEq b rest v need

/-- The number of unit steps a list of terms can take. -/
def capacity (b : Box) : List (String × Int) → Int
  | [] => 0
  | (q, c) :: rest => (if c = 1 ∨ c = -1 then b.hi q - b.lo q else 0) + capacity b rest

theorem termSum_update_not_mem (v : Valuation) (q : String) (x : Int) :
    ∀ l : List (String × Int), q ∉ l.map (·.1) → termSum l (update v q x) = termSum l v
  | [], _ => rfl
  | p :: l, h => by
    simp only [List.map_cons, List.mem_cons, not_or] at h
    rw [termSum_cons, termSum_cons, termSum_update_not_mem v q x l h.2]
    have : p.1 ≠ q := fun he => h.1 he.symm
    simp [update, this]

theorem termSum_update_mem (v : Valuation) (x : Int) :
    ∀ (l : List (String × Int)), (l.map (·.1)).Nodup → ∀ p ∈ l,
      termSum l (update v p.1 x) = termSum l v + p.2 * (x - v p.1)
  | [], _, p, hp => by cases hp
  | y :: l, hn, p, hp => by
    simp only [List.map_cons, List.nodup_cons] at hn
    rw [termSum_cons, termSum_cons]
    by_cases hy : y = p
    · subst hy
      rw [termSum_update_not_mem v y.1 x l hn.1]
      simp only [update, if_true, Int.mul_sub]
      omega
    · have hp' : p ∈ l := by
        rcases List.mem_cons.mp hp with h | h
        · exact absurd h.symm hy
        · exact h
      have hne : y.1 ≠ p.1 := fun he => hn.1 (he ▸ List.mem_map.mpr ⟨p, hp', rfl⟩)
      rw [termSum_update_mem v x l hn.2 p hp']
      simp only [update, hne, if_false]
      omega

theorem capacity_nonneg {b : Box} (hb : b.WF) : ∀ l : List (String × Int), 0 ≤ capacity b l
  | [] => by simp [capacity]
  | (q, c) :: rest => by
    have := capacity_nonneg hb rest
    have := wf_lo_le_hi hb q
    simp only [capacity]
    split <;> omega

/-- The stepping invariant: on a sublist `l` of a normal form's terms (names unique), started from
the minimising endpoints of `l`, stepping adds `min need (capacity l)` to the form. -/
theorem stepEq_eval (b : Box) (hb : b.WF) (f : LinForm) (hf : f.Normal) :
    ∀ (l : List (String × Int)) (v : Valuation) (need : Int),
      (l.map (·.1)).Nodup → (∀ p ∈ l, p ∈ f.coeffs) →
      (∀ p ∈ l, v p.1 = if 0 ≤ p.2 then b.lo p.1 else b.hi p.1) → 0 ≤ need →
      f.eval (stepEq b l v need) = f.eval v + min need (capacity b l) ∧
      (∀ q, q ∉ l.map (·.1) → stepEq b l v need q = v q) ∧
      (∀ p ∈ l, b.lo p.1 ≤ stepEq b l v need p.1 ∧ stepEq b l v need p.1 ≤ b.hi p.1)
  | [], v, need, _, _, _, hneed => by
    refine ⟨?_, fun _ _ => rfl, fun p hp => by cases hp⟩
    simp only [stepEq, capacity]
    omega
  | (q, c) :: rest, v, need, hn, hsub, hstart, hneed => by
    simp only [List.map_cons, List.nodup_cons] at hn
    have hsub' : ∀ p ∈ rest, p ∈ f.coeffs := fun p hp => hsub p (List.mem_cons_of_mem _ hp)
    have hqc : (q, c) ∈ f.coeffs := hsub _ (List.mem_cons_self ..)
    have hlohi := wf_lo_le_hi hb q
    have hcap := capacity_nonneg hb rest
    have hv0 : v q = if 0 ≤ c then b.lo q else b.hi q := hstart _ (List.mem_cons_self ..)
    have hupd (x : Int) : ∀ p ∈ rest, (v p.1 = if 0 ≤ p.2 then b.lo p.1 else b.hi p.1) →
        (update v q x p.1 = if 0 ≤ p.2 then b.lo p.1 else b.hi p.1) := fun p hp h => by
      have : p.1 ≠ q := fun he => hn.1 (he ▸ List.mem_map.mpr ⟨p, hp, rfl⟩)
      simp only [update, this, if_false]; exact h
    have hstartRest : ∀ p ∈ rest, v p.1 = if 0 ≤ p.2 then b.lo p.1 else b.hi p.1 :=
      fun p hp => hstart p (List.mem_cons_of_mem _ hp)
    have hevalUpd (x : Int) : f.eval (update v q x) = f.eval v + c * (x - v q) := by
      rw [eval_eq_termSum, eval_eq_termSum, termSum_update_mem v x f.coeffs hf.1 (q, c) hqc]
      simp only
      omega
    have hnotin (q' : String) (hq' : q' ∉ List.map (fun x => x.1) ((q, c) :: rest)) :
        q' ≠ q ∧ q' ∉ rest.map (·.1) := by
      simp only [List.map_cons, List.mem_cons, not_or] at hq'
      exact hq'
    by_cases h1 : c = 1
    · subst h1
      have hv0' : v q = b.lo q := by simpa using hv0
      have hδ : 0 ≤ min need (b.hi q - b.lo q) := by omega
      have hδ' : min need (b.hi q - b.lo q) ≤ b.hi q - b.lo q := Int.min_le_right _ _
      obtain ⟨ih1, ih2, ih3⟩ := stepEq_eval b hb f hf rest (update v q (b.lo q + min need (b.hi q - b.lo q)))
        (need - min need (b.hi q - b.lo q)) hn.2 hsub' (fun p hp => hupd _ p hp (hstartRest p hp))
        (by omega)
      have e1 : stepEq b ((q, 1) :: rest) v need = stepEq b rest (update v q (b.lo q + min need (b.hi q - b.lo q)))
          (need - min need (b.hi q - b.lo q)) := by simp [stepEq]
      have e2 : capacity b ((q, 1) :: rest) = (b.hi q - b.lo q) + capacity b rest := by simp [capacity]
      rw [e1, e2]
      refine ⟨?_, fun q' hq' => ?_, fun p hp => ?_⟩
      · rw [ih1, hevalUpd, hv0']
        simp only [Int.min_def]
        split <;> split <;> omega
      · obtain ⟨hne, hrest⟩ := hnotin q' hq'
        rw [ih2 q' hrest]
        simp [update, hne]
      · rcases List.mem_cons.mp hp with rfl | hp
        · rw [ih2 _ hn.1]
          simp only [update, if_true]
          omega
        · exact ih3 p hp
    · by_cases h2 : c = -1
      · subst h2
        have hv0' : v q = b.hi q := by simpa using hv0
        have hδ : 0 ≤ min need (b.hi q - b.lo q) := by omega
        have hδ' : min need (b.hi q - b.lo q) ≤ b.hi q - b.lo q := Int.min_le_right _ _
        obtain ⟨ih1, ih2, ih3⟩ := stepEq_eval b hb f hf rest (update v q (b.hi q - min need (b.hi q - b.lo q)))
          (need - min need (b.hi q - b.lo q)) hn.2 hsub' (fun p hp => hupd _ p hp (hstartRest p hp))
          (by omega)
        have e1 : stepEq b ((q, -1) :: rest) v need = stepEq b rest (update v q (b.hi q - min need (b.hi q - b.lo q)))
            (need - min need (b.hi q - b.lo q)) := by simp [stepEq]
        have e2 : capacity b ((q, -1) :: rest) = (b.hi q - b.lo q) + capacity b rest := by simp [capacity]
        rw [e1, e2]
        refine ⟨?_, fun q' hq' => ?_, fun p hp => ?_⟩
        · rw [ih1, hevalUpd, hv0']
          simp only [Int.min_def]
          split <;> split <;> omega
        · obtain ⟨hne, hrest⟩ := hnotin q' hq'
          rw [ih2 q' hrest]
          simp [update, hne]
        · rcases List.mem_cons.mp hp with rfl | hp
          · rw [ih2 _ hn.1]
            simp only [update, if_true]
            omega
          · exact ih3 p hp
      · have hnot : ¬ (c = 1 ∨ c = -1) := by omega
        obtain ⟨ih1, ih2, ih3⟩ := stepEq_eval b hb f hf rest v need hn.2 hsub' hstartRest hneed
        have e1 : stepEq b ((q, c) :: rest) v need = stepEq b rest v need := by simp [stepEq, h1, h2]
        have e2 : capacity b ((q, c) :: rest) = capacity b rest := by simp [capacity, h1, h2]
        rw [e1, e2]
        refine ⟨ih1, fun q' hq' => ?_, fun p hp => ?_⟩
        · exact ih2 q' (hnotin q' hq').2
        · rcases List.mem_cons.mp hp with rfl | hp
          · rw [ih2 _ hn.1]
            show b.lo q ≤ v q ∧ v q ≤ b.hi q
            split at hv0 <;> omega
          · exact ih3 p hp

/-- `capacity` is the width of a unit-coefficient form's value range. -/
theorem capacity_eq (b : Box) : ∀ l : List (String × Int),
    (∀ p ∈ l, b.isPoint p.1 = true ∨ p.2 = 1 ∨ p.2 = -1) → capacity b l = maxSum b l - minSum b l
  | [], _ => by simp [capacity, maxSum, minSum]
  | (q, c) :: rest, h => by
    have ih := capacity_eq b rest (fun p hp => h p (List.mem_cons_of_mem _ hp))
    simp only [capacity, maxSum_cons, minSum_cons, ih]
    rcases h (q, c) (List.mem_cons_self ..) with hp | hc | hc
    · have := isPoint_eq hp
      simp only at this
      rw [this]
      split <;> split <;> omega
    · simp only at hc; subst hc; simp; omega
    · simp only at hc; subst hc; simp; omega

theorem unitForm_terms {b : Box} {f : LinForm} (h : unitForm b f = true) :
    ∀ p ∈ f.coeffs, b.isPoint p.1 = true ∨ p.2 = 1 ∨ p.2 = -1 := by
  intro p hp
  have := List.all_eq_true.mp h p hp
  simp only [Bool.or_eq_true, beq_iff_eq] at this
  rcases this with (h | h) | h
  · exact Or.inl h
  · exact Or.inr (Or.inl h)
  · exact Or.inr (Or.inr h)

/-- The position of a quantity among the box's entries, which follow the record's quantity order;
a name outside the box comes after every entry. -/
def boxIndex (b : Box) (q : String) : Nat := b.entries.findIdx (·.name == q)

/-- 4.3: the terms of `f` in the record's quantity order (a stable sort, so ties keep the form's order). -/
def recordOrder (b : Box) (f : LinForm) : List (String × Int) :=
  f.coeffs.mergeSort (fun p q => decide (boxIndex b p.1 ≤ boxIndex b q.1))

theorem recordOrder_perm (b : Box) (f : LinForm) : (recordOrder b f).Perm f.coeffs :=
  List.mergeSort_perm _ _

theorem capacity_perm (b : Box) {l₁ l₂ : List (String × Int)} (h : l₁.Perm l₂) :
    capacity b l₁ = capacity b l₂ := by
  induction h with
  | nil => rfl
  | cons x _ ih =>
    obtain ⟨q, c⟩ := x
    simp only [capacity, ih]
  | swap x y l =>
    obtain ⟨q, c⟩ := x
    obtain ⟨q', c'⟩ := y
    simp only [capacity]
    omega
  | trans _ _ ih₁ ih₂ => exact ih₁.trans ih₂

/-- The `=` witness (4.3): from the minimising endpoints, `−fmin` unit steps, moving the quantities in
the record's quantity order. -/
def eqWit (b : Box) (f : LinForm) : Valuation := stepEq b (recordOrder b f) (minVal b f) (-(fmin b f))

theorem minVal_start (b : Box) {f : LinForm} (hf : f.Normal) :
    ∀ p ∈ f.coeffs, minVal b f p.1 = if 0 ≤ p.2 then b.lo p.1 else b.hi p.1 := by
  intro p hp
  simp only [minVal, find_coeff hf.1 hp]

/-- 4.3: on a unit-coefficient normal form whose endpoint values bracket 0, the `=` witness lies in
the box and the form is 0 there. -/
theorem eqWit_sound {b : Box} (hb : b.WF) {f : LinForm} (hf : f.Normal) (hu : unitForm b f = true)
    (h1 : fmin b f ≤ 0) (h2 : 0 ≤ fmax b f) : InBox b (eqWit b f) ∧ f.eval (eqWit b f) = 0 := by
  have hperm := recordOrder_perm b f
  obtain ⟨e1, e2, e3⟩ := stepEq_eval b hb f hf (recordOrder b f) (minVal b f) (-(fmin b f))
    ((hperm.map _).nodup_iff.mpr hf.1) (fun p h => hperm.mem_iff.mp h)
    (fun p h => minVal_start b hf p (hperm.mem_iff.mp h)) (by omega)
  have hcap := capacity_eq b f.coeffs (unitForm_terms hu)
  rw [← capacity_perm b hperm] at hcap
  refine ⟨fun e he => ?_, ?_⟩
  · have hfind := find_of_mem hb.1 he
    have hlo : b.lo e.name = e.lo := by simp [Box.lo, hfind]
    have hhi : b.hi e.name = e.hi := by simp [Box.hi, hfind]
    by_cases hn : e.name ∈ (recordOrder b f).map (·.1)
    · obtain ⟨p, hp, hpe⟩ := List.mem_map.mp hn
      have := e3 p hp
      rw [hpe, hlo, hhi] at this
      exact this
    · unfold eqWit
      rw [e2 e.name hn]
      have := minVal_inBox hb f e he
      exact this
  · unfold eqWit
    rw [e1, minVal_eval b hf, hcap]
    unfold fmin fmax at *
    simp only [Int.min_def]
    split <;> omega

/-! ## Agreement on the quantities a condition mentions -/

theorem termSum_congr (v w : Valuation) :
    ∀ l : List (String × Int), (∀ q ∈ l.map (·.1), v q = w q) → termSum l v = termSum l w
  | [], _ => rfl
  | p :: l, h => by
    rw [termSum_cons, termSum_cons, h p.1 (List.mem_cons_self ..),
      termSum_congr v w l (fun q hq => h q (List.mem_cons_of_mem _ hq))]

theorem holds_congr {v w : Valuation} : ∀ c : Cond, (∀ q ∈ c.atomNames, v q = w q) → (c.holds v ↔ c.holds w)
  | .top, _ | .bottom, _ => Iff.rfl
  | .atom f r, h => by
    simp only [Cond.holds, eval_eq_termSum, termSum_congr v w f.val.coeffs h]
  | .and x y, h => and_congr (holds_congr x fun q hq => h q (List.mem_append_left _ hq))
      (holds_congr y fun q hq => h q (List.mem_append_right _ hq))
  | .or x y, h => or_congr (holds_congr x fun q hq => h q (List.mem_append_left _ hq))
      (holds_congr y fun q hq => h q (List.mem_append_right _ hq))
  | .not x, h => not_congr (holds_congr x h)

/-- Take `x`'s quantities from `va` and every other quantity from `vb`. -/
def combine (x : Cond) (va vb : Valuation) : Valuation := fun q => if q ∈ x.atomNames then va q else vb q

theorem count_two {q : String} {l m : List String} (hl : q ∈ l) (hm : q ∈ m) : 2 ≤ (l ++ m).count q := by
  rw [List.count_append]
  have := List.count_pos_iff.mpr hl
  have := List.count_pos_iff.mpr hm
  omega

theorem combine_ok {b : Box} {x y : Cond} {va vb : Valuation} (ha : InBox b va) (hvb : InBox b vb)
    (hs : (x.atomNames ++ y.atomNames).all (fun q => b.isPoint q || (x.atomNames ++ y.atomNames).count q ≤ 1) = true)
    (hy : y.atomNames.all b.mem = true) :
    InBox b (combine x va vb) ∧ (∀ q ∈ x.atomNames, combine x va vb q = va q) ∧
      (∀ q ∈ y.atomNames, combine x va vb q = vb q) := by
  refine ⟨fun e he => ?_, fun q hq => by simp [combine, hq], fun q hq => ?_⟩
  · unfold combine
    split
    · exact ha e he
    · exact hvb e he
  · unfold combine
    split
    · rename_i hx
      have hpt := List.all_eq_true.mp hs q (List.mem_append_right _ hq)
      have hc := count_two hx hq
      simp only [Bool.or_eq_true, decide_eq_true_eq] at hpt
      have hpoint : b.isPoint q = true := by
        rcases hpt with h | h
        · exact h
        · omega
      have hmem := List.all_eq_true.mp hy q hq
      rw [inBox_point ha hmem hpoint, inBox_point hvb hmem hpoint]
    · rfl

theorem sepOK_and_left {b : Box} {x y : Cond}
    (h : (x.atomNames ++ y.atomNames).all (fun q => b.isPoint q || (x.atomNames ++ y.atomNames).count q ≤ 1) = true) :
    sepOK b x = true := by
  unfold sepOK
  apply List.all_eq_true.mpr
  intro q hq
  have := List.all_eq_true.mp h q (List.mem_append_left _ hq)
  simp only [Bool.or_eq_true, decide_eq_true_eq] at this ⊢
  rcases this with h | h
  · exact Or.inl h
  · exact Or.inr (Nat.le_trans ((List.sublist_append_left _ _).count_le q) h)

theorem sepOK_and_right {b : Box} {x y : Cond}
    (h : (x.atomNames ++ y.atomNames).all (fun q => b.isPoint q || (x.atomNames ++ y.atomNames).count q ≤ 1) = true) :
    sepOK b y = true := by
  unfold sepOK
  apply List.all_eq_true.mpr
  intro q hq
  have := List.all_eq_true.mp h q (List.mem_append_right _ hq)
  simp only [Bool.or_eq_true, decide_eq_true_eq] at this ⊢
  rcases this with h | h
  · exact Or.inl h
  · exact Or.inr (Nat.le_trans ((List.sublist_append_right _ _).count_le q) h)

theorem scoped_left {b : Box} {x y : Cond} (h : (x.atomNames ++ y.atomNames).all b.mem = true) :
    x.atomNames.all b.mem = true := by
  rw [List.all_append] at h
  simp only [Bool.and_eq_true] at h
  exact h.1

theorem scoped_right {b : Box} {x y : Cond} (h : (x.atomNames ++ y.atomNames).all b.mem = true) :
    y.atomNames.all b.mem = true := by
  rw [List.all_append] at h
  simp only [Bool.and_eq_true] at h
  exact h.2

/-! ## The directions that need only scoping -/

theorem atom_easy (b : Box) (f : LinForm) (r : Rel) (hs : ∀ q ∈ f.names, b.mem q = true) :
    ((∃ v, InBox b v ∧ r.holds (f.eval v)) → atomPossible b f r = true) ∧
    (atomCertain b f r = true → ∀ v, InBox b v → r.holds (f.eval v)) := by
  constructor
  · rintro ⟨v, hv, hr⟩
    have := eval_bounds hv hs
    cases r <;> simp only [atomPossible, Rel.holds] at hr ⊢ <;> simp <;> omega
  · intro hc v hv
    have := eval_bounds hv hs
    cases r <;> simp only [atomCertain, Rel.holds] at hc ⊢ <;> simp at hc <;> omega

theorem ends_easy (b : Box) : ∀ c : Cond, c.atomNames.all b.mem = true →
    ((∃ v, InBox b v ∧ c.holds v) → (endsE b c).1 = true) ∧
    ((endsE b c).2 = true → ∀ v, InBox b v → c.holds v)
  | .top, _ => ⟨fun _ => rfl, fun _ _ _ => trivial⟩
  | .bottom, _ => ⟨fun ⟨_, _, h⟩ => h.elim, fun h => by cases h⟩
  | .atom f r, h => atom_easy b f.val r (fun q hq => List.all_eq_true.mp h q hq)
  | .and x y, h => by
    have ix := ends_easy b x (scoped_left h)
    have iy := ends_easy b y (scoped_right h)
    refine ⟨fun ⟨v, hv, h1, h2⟩ => ?_, fun hc v hv => ?_⟩
    · simp only [endsE, Bool.and_eq_true]
      exact ⟨ix.1 ⟨v, hv, h1⟩, iy.1 ⟨v, hv, h2⟩⟩
    · simp only [endsE, Bool.and_eq_true] at hc
      exact ⟨ix.2 hc.1 v hv, iy.2 hc.2 v hv⟩
  | .or x y, h => by
    have ix := ends_easy b x (scoped_left h)
    have iy := ends_easy b y (scoped_right h)
    refine ⟨fun ⟨v, hv, h1⟩ => ?_, fun hc v hv => ?_⟩
    · simp only [endsE, Bool.or_eq_true]
      rcases h1 with h1 | h1
      · exact Or.inl (ix.1 ⟨v, hv, h1⟩)
      · exact Or.inr (iy.1 ⟨v, hv, h1⟩)
    · simp only [endsE, Bool.or_eq_true] at hc
      rcases hc with hc | hc
      · exact Or.inl (ix.2 hc v hv)
      · exact Or.inr (iy.2 hc v hv)
  | .not x, h => by
    have ix := ends_easy b x h
    refine ⟨fun ⟨v, hv, h1⟩ => ?_, fun hc v hv h1 => ?_⟩
    · simp only [endsE, Bool.not_eq_true']
      cases hx : (endsE b x).2
      · rfl
      · exact absurd (ix.2 hx v hv) h1
    · simp only [endsE, Bool.not_eq_true'] at hc
      rw [ix.1 ⟨v, hv, h1⟩] at hc
      cases hc

/-! ## Exactness on separable, unit-coefficient conditions -/

theorem box_nonempty {b : Box} (hb : b.WF) : InBox b (fun q => b.lo q) := by
  apply inBox_of_endpoints hb
  intro q; exact Or.inl rfl

theorem atom_exact {b : Box} (hb : b.WF) (f : NormLinForm) (r : Rel) (hs : ∀ q ∈ f.val.names, b.mem q = true)
    (hu : unitOK b (.atom f r) = true) :
    (atomPossible b f.val r = true ↔ ∃ v, InBox b v ∧ r.holds (f.val.eval v)) ∧
    (atomCertain b f.val r = true ↔ ∀ v, InBox b v → r.holds (f.val.eval v)) := by
  have easy := atom_easy b f.val r hs
  have hmin := minVal_eval b f.property
  have hmax := maxVal_eval b f.property
  have imin := minVal_inBox hb f.val
  have imax := maxVal_inBox hb f.val
  refine ⟨⟨fun hp => ?_, easy.1⟩, ⟨easy.2, fun hall => ?_⟩⟩
  · cases r with
    | lt => exact ⟨_, imin, by simp only [Rel.holds]; simp [atomPossible] at hp; omega⟩
    | le => exact ⟨_, imin, by simp only [Rel.holds]; simp [atomPossible] at hp; omega⟩
    | eq =>
      simp only [atomPossible, Bool.and_eq_true, decide_eq_true_eq] at hp
      have hu' : unitForm b f.val = true := hu
      obtain ⟨h1, h2⟩ := eqWit_sound hb f.property hu' hp.1 hp.2
      exact ⟨_, h1, h2⟩
    | ne =>
      simp only [atomPossible, Bool.not_eq_true', Bool.and_eq_false_iff, decide_eq_false_iff_not] at hp
      rcases hp with hp | hp
      · exact ⟨_, imin, by simp only [Rel.holds]; omega⟩
      · exact ⟨_, imax, by simp only [Rel.holds]; omega⟩
  · cases r with
    | lt => have := hall _ imax; simp only [Rel.holds] at this; simp [atomCertain]; omega
    | le => have := hall _ imax; simp only [Rel.holds] at this; simp [atomCertain]; omega
    | eq =>
      have h1 := hall _ imin
      have h2 := hall _ imax
      simp only [Rel.holds] at h1 h2
      simp [atomCertain]; omega
    | ne =>
      simp only [atomCertain, Bool.or_eq_true, decide_eq_true_eq]
      refine Classical.byContradiction fun hn => ?_
      have hu' : unitForm b f.val = true := hu
      obtain ⟨w1, w2⟩ := eqWit_sound hb f.property hu' (by omega) (by omega)
      exact hall _ w1 w2

theorem ends_exact {b : Box} (hb : b.WF) : ∀ c : Cond, c.atomNames.all b.mem = true → sepOK b c = true →
    unitOK b c = true →
    ((endsE b c).1 = true ↔ ∃ v, InBox b v ∧ c.holds v) ∧
    ((endsE b c).2 = true ↔ ∀ v, InBox b v → c.holds v)
  | .top, _, _, _ => ⟨⟨fun _ => ⟨_, box_nonempty hb, trivial⟩, fun _ => rfl⟩, ⟨fun _ _ _ => trivial, fun _ => rfl⟩⟩
  | .bottom, _, _, _ => ⟨⟨(fun h => by cases h), fun ⟨_, _, h⟩ => h.elim⟩,
      ⟨(fun h => by cases h), fun h => (h _ (box_nonempty hb)).elim⟩⟩
  | .atom f r, h, _, hu => atom_exact hb f r (fun q hq => List.all_eq_true.mp h q hq) hu
  | .and x y, h, hs, hu => by
    simp only [unitOK, Bool.and_eq_true] at hu
    have ix := ends_exact hb x (scoped_left h) (sepOK_and_left hs) hu.1
    have iy := ends_exact hb y (scoped_right h) (sepOK_and_right hs) hu.2
    refine ⟨⟨fun hp => ?_, (ends_easy b _ h).1⟩, ⟨(ends_easy b _ h).2, fun hall => ?_⟩⟩
    · simp only [endsE, Bool.and_eq_true] at hp
      obtain ⟨va, hva, hxa⟩ := ix.1.1 hp.1
      obtain ⟨vb, hvb, hyb⟩ := iy.1.1 hp.2
      obtain ⟨hin, hcx, hcy⟩ := combine_ok hva hvb hs (scoped_right h)
      exact ⟨_, hin, (holds_congr x hcx).mpr hxa, (holds_congr y hcy).mpr hyb⟩
    · simp only [endsE, Bool.and_eq_true]
      exact ⟨ix.2.2 fun v hv => (hall v hv).1, iy.2.2 fun v hv => (hall v hv).2⟩
  | .or x y, h, hs, hu => by
    simp only [unitOK, Bool.and_eq_true] at hu
    have ix := ends_exact hb x (scoped_left h) (sepOK_and_left hs) hu.1
    have iy := ends_exact hb y (scoped_right h) (sepOK_and_right hs) hu.2
    refine ⟨⟨fun hp => ?_, (ends_easy b _ h).1⟩, ⟨(ends_easy b _ h).2, fun hall => ?_⟩⟩
    · simp only [endsE, Bool.or_eq_true] at hp
      rcases hp with hp | hp
      · obtain ⟨v, hv, hx⟩ := ix.1.1 hp
        exact ⟨v, hv, Or.inl hx⟩
      · obtain ⟨v, hv, hy⟩ := iy.1.1 hp
        exact ⟨v, hv, Or.inr hy⟩
    · simp only [endsE, Bool.or_eq_true]
      refine Classical.byContradiction fun hn => ?_
      simp only [not_or, Bool.not_eq_true] at hn
      have nx : ¬ ∀ v, InBox b v → x.holds v := fun h' => by rw [ix.2.2 h'] at hn; exact Bool.noConfusion hn.1
      have ny : ¬ ∀ v, InBox b v → y.holds v := fun h' => by rw [iy.2.2 h'] at hn; exact Bool.noConfusion hn.2
      have ⟨va, hva, hxa⟩ : ∃ v, InBox b v ∧ ¬ x.holds v := by
        refine Classical.byContradiction fun h' => ?_
        exact nx fun v hv => by
          refine Classical.byContradiction fun h'' => ?_
          exact h' ⟨v, hv, h''⟩
      have ⟨vb, hvb, hyb⟩ : ∃ v, InBox b v ∧ ¬ y.holds v := by
        refine Classical.byContradiction fun h' => ?_
        exact ny fun v hv => by
          refine Classical.byContradiction fun h'' => ?_
          exact h' ⟨v, hv, h''⟩
      obtain ⟨hin, hcx, hcy⟩ := combine_ok hva hvb hs (scoped_right h)
      rcases hall _ hin with h1 | h1
      · exact hxa ((holds_congr x hcx).mp h1)
      · exact hyb ((holds_congr y hcy).mp h1)
  | .not x, h, hs, hu => by
    have ix := ends_exact hb x h hs hu
    refine ⟨⟨fun hp => ?_, (ends_easy b _ h).1⟩, ⟨(ends_easy b _ h).2, fun hall => ?_⟩⟩
    · simp only [endsE, Bool.not_eq_true'] at hp
      refine Classical.byContradiction fun hn => ?_
      have : ∀ v, InBox b v → x.holds v := fun v hv => by
        refine Classical.byContradiction fun h' => ?_
        exact hn ⟨v, hv, h'⟩
      rw [ix.2.2 this] at hp
      cases hp
    · simp only [endsE, Bool.not_eq_true']
      cases hx : (endsE b x).1
      · rfl
      · obtain ⟨v, hv, h1⟩ := ix.1.1 hx
        exact absurd h1 (hall v hv)

/-! ## The theorems of 7.2 -/

theorem scoped_nnf (b : Box) (c : Cond) : (nnf c).atomNames.all b.mem = Scoped b c := by
  rw [nnf_atomNames]; rfl

theorem holds_nnf_ex (b : Box) (c : Cond) :
    (∃ v, InBox b v ∧ (nnf c).holds v) ↔ ∃ v, InBox b v ∧ c.holds v := by
  simp only [nnf_holds]

theorem holds_nnf_all (b : Box) (c : Cond) :
    (∀ v, InBox b v → (nnf c).holds v) ↔ ∀ v, InBox b v → c.holds v := by
  simp only [nnf_holds]

/-- 4.3: the direction of `possibleE` that needs only scoping. -/
theorem possibleE_complete (b : Box) (c : Cond) (hq : Scoped b c = true) :
    (∃ v, InBox b v ∧ c.holds v) → possibleE b c = true := by
  intro h
  exact (ends_easy b (nnf c) (by rw [scoped_nnf]; exact hq)).1 ((holds_nnf_ex b c).mpr h)

/-- 4.3: the direction of `certainE` that needs only scoping. -/
theorem certainE_sound (b : Box) (c : Cond) (hq : Scoped b c = true) :
    certainE b c = true → ∀ v, InBox b v → c.holds v := by
  intro h
  exact (holds_nnf_all b c).mp ((ends_easy b (nnf c) (by rw [scoped_nnf]; exact hq)).2 h)

/-- 4.3: endpoint evaluation of possibility is exact on scoped, separable, unit-coefficient
conditions. Every atom holds a `NormLinForm`, so the uncollected `q − q − 1` of fixture k34 cannot
occur. -/
theorem possibleE_iff (b : Box) (c : Cond) (hb : b.WF) (hq : Scoped b c = true)
    (hs : Separable b c = true) (hu : UnitCoefficients b c = true) :
    possibleE b c = true ↔ ∃ v, InBox b v ∧ c.holds v := by
  rw [← holds_nnf_ex]
  exact (ends_exact hb (nnf c) (by rw [scoped_nnf]; exact hq) hs hu).1

theorem certainE_iff (b : Box) (c : Cond) (hb : b.WF) (hq : Scoped b c = true)
    (hs : Separable b c = true) (hu : UnitCoefficients b c = true) :
    certainE b c = true ↔ ∀ v, InBox b v → c.holds v := by
  rw [← holds_nnf_all]
  exact (ends_exact hb (nnf c) (by rw [scoped_nnf]; exact hq) hs hu).2

/-! ## The canonical witness (4.3) -/

def atomWit (b : Box) (f : LinForm) : Rel → Valuation
  | .lt | .le => minVal b f
  | .ne => if fmin b f ≠ 0 then minVal b f else maxVal b f
  | .eq => eqWit b f

def wit (b : Box) : Cond → Valuation
  | .top | .bottom => fun q => b.lo q
  | .atom f r => atomWit b f.val r
  | .and x y => combine x (wit b x) (wit b y)
  | .or x y => if (endsE b x).1 then wit b x else wit b y
  | .not x => wit b x

/-- 4.3: the canonical witness of a possible condition. -/
def witnessE (b : Box) (c : Cond) : Option Valuation :=
  if possibleE b c then some (wit b (nnf c)) else none

theorem wit_sound {b : Box} (hb : b.WF) : ∀ c : Cond, c.NotFree → c.atomNames.all b.mem = true →
    sepOK b c = true → unitOK b c = true → (endsE b c).1 = true → InBox b (wit b c) ∧ c.holds (wit b c)
  | .top, _, _, _, _, _ => ⟨box_nonempty hb, trivial⟩
  | .bottom, _, _, _, _, hp => by cases hp
  | .atom f r, _, _, _, hu, hp => by
    have hmin := minVal_eval b f.property
    have hmax := maxVal_eval b f.property
    have imin := minVal_inBox hb f.val
    have imax := maxVal_inBox hb f.val
    cases r with
    | lt => exact ⟨imin, by simp only [wit, atomWit, Cond.holds, Rel.holds]; simp [endsE, atomPossible] at hp; omega⟩
    | le => exact ⟨imin, by simp only [wit, atomWit, Cond.holds, Rel.holds]; simp [endsE, atomPossible] at hp; omega⟩
    | eq =>
      simp only [endsE, atomPossible, Bool.and_eq_true, decide_eq_true_eq] at hp
      exact eqWit_sound hb f.property hu hp.1 hp.2
    | ne =>
      simp only [endsE, atomPossible, Bool.not_eq_true', Bool.and_eq_false_iff, decide_eq_false_iff_not] at hp
      simp only [wit, atomWit, Cond.holds, Rel.holds]
      by_cases h0 : fmin b f.val = 0
      · simp only [h0, ne_eq, not_true_eq_false, if_false]
        rcases hp with hp | hp
        · exact absurd h0 hp
        · exact ⟨imax, by omega⟩
      · simp only [ne_eq, h0, not_false_eq_true, if_true]
        exact ⟨imin, by omega⟩
  | .and x y, hn, h, hs, hu, hp => by
    simp only [unitOK, Bool.and_eq_true] at hu
    simp only [endsE, Bool.and_eq_true] at hp
    obtain ⟨ha, hxa⟩ := wit_sound hb x hn.1 (scoped_left h) (sepOK_and_left hs) hu.1 hp.1
    obtain ⟨hb', hyb⟩ := wit_sound hb y hn.2 (scoped_right h) (sepOK_and_right hs) hu.2 hp.2
    obtain ⟨hin, hcx, hcy⟩ := combine_ok ha hb' hs (scoped_right h)
    exact ⟨hin, (holds_congr x hcx).mpr hxa, (holds_congr y hcy).mpr hyb⟩
  | .or x y, hn, h, hs, hu, hp => by
    simp only [unitOK, Bool.and_eq_true] at hu
    simp only [wit]
    by_cases hx : (endsE b x).1 = true
    · rw [if_pos hx]
      obtain ⟨h1, h2⟩ := wit_sound hb x hn.1 (scoped_left h) (sepOK_and_left hs) hu.1 hx
      exact ⟨h1, Or.inl h2⟩
    · rw [if_neg hx]
      simp only [endsE, Bool.or_eq_true] at hp
      have hy : (endsE b y).1 = true := hp.resolve_left hx
      obtain ⟨h1, h2⟩ := wit_sound hb y hn.2 (scoped_right h) (sepOK_and_right hs) hu.2 hy
      exact ⟨h1, Or.inr h2⟩
  | .not _, hn, _, _, _, _ => hn.elim

/-- 4.3: the canonical witness of a possible scoped, separable, unit-coefficient condition lies in
the box and satisfies the condition. -/
theorem witnessE_sound (b : Box) (c : Cond) (hb : b.WF) (hq : Scoped b c = true)
    (hs : Separable b c = true) (hu : UnitCoefficients b c = true) (hp : possibleE b c = true) :
    ∃ v, witnessE b c = some v ∧ InBox b v ∧ c.holds v := by
  obtain ⟨h1, h2⟩ := wit_sound hb (nnf c) (nnf_notFree c) (by rw [scoped_nnf]; exact hq) hs hu hp
  exact ⟨_, by simp [witnessE, hp], h1, (nnf_holds c _).mp h2⟩

end VE.Risk
