import VE.Risk.Report

/-! `status_piecewise_constant` and the certified scans (docs/spec/risk.md 4.9 and
7.2).

The outcome at a value `x` of endpoint `e` is a function of the record's view
(`Record.lean`): the record with its estimate values erased, and a finite list
of observations of the box (range checks, point-ness, and the signs of the
extrema of every atom). Between `x` and `x + 1`:

* every value that depends on the moved endpoint is *gap-stable*: it is the
  moved value itself at both points, or it is constant there and equal to an
  endpoint of a cited estimate of the same quantity (`GS`). Comparisons of
  gap-stable values agree at `x` and `x + 1` when neither is such an endpoint
  (`Gap`), which the endpoint candidates `w − 1, w, w + 1` guarantee;
* an atom's extremum that depends on the endpoint is `c·x + K`, whose sign
  changes only between two of the threshold candidates (`sign_step`).

So the observations, the view, and the outcome agree. -/
namespace VE.Risk

/-! ## Gap-stable values -/

def Gap (x : Int) (W : List Int) : Prop := ∀ w ∈ W, x ≠ w ∧ x + 1 ≠ w

/-- The identity on `{x, x + 1}`, or constant there with its value in `W`. -/
def GS (x : Int) (W : List Int) (f : Int → Int) : Prop :=
  (f x = x ∧ f (x + 1) = x + 1) ∨ (f x = f (x + 1) ∧ f x ∈ W)

section GapStable
variable {x : Int} {W : List Int}

theorem GS.const {w : Int} (hw : w ∈ W) : GS x W (fun _ => w) := Or.inr ⟨rfl, hw⟩

theorem GS.id : GS x W (fun y => y) := Or.inl ⟨rfl, rfl⟩

theorem GS.min (hg : Gap x W) {f g : Int → Int} (hf : GS x W f) (hg' : GS x W g) :
    GS x W (fun y => min (f y) (g y)) := by
  unfold GS
  dsimp only
  rcases hf with ⟨f1, f2⟩ | ⟨f1, f2⟩ <;> rcases hg' with ⟨g1, g2⟩ | ⟨g1, g2⟩
  · left; exact ⟨by rw [f1, g1]; simp, by rw [f2, g2]; simp⟩
  · have hw := hg _ g2
    by_cases h : x < g x
    · left
      exact ⟨by rw [f1]; exact Int.min_eq_left (by omega), by rw [f2, ← g1]; exact Int.min_eq_left (by omega)⟩
    · right
      refine ⟨by rw [f1, f2, ← g1, Int.min_eq_right (by omega), Int.min_eq_right (by omega)], ?_⟩
      rw [f1, Int.min_eq_right (by omega)]; exact g2
  · have hw := hg _ f2
    by_cases h : x < f x
    · left
      exact ⟨by rw [g1]; exact Int.min_eq_right (by omega), by rw [g2, ← f1]; exact Int.min_eq_right (by omega)⟩
    · right
      refine ⟨by rw [g1, g2, ← f1, Int.min_eq_left (by omega), Int.min_eq_left (by omega)], ?_⟩
      rw [g1, Int.min_eq_left (by omega)]; exact f2
  · right
    refine ⟨by rw [f1, g1], ?_⟩
    rcases Int.le_total (f x) (g x) with h | h
    · rw [Int.min_eq_left h]; exact f2
    · rw [Int.min_eq_right h]; exact g2

theorem GS.max (hg : Gap x W) {f g : Int → Int} (hf : GS x W f) (hg' : GS x W g) :
    GS x W (fun y => max (f y) (g y)) := by
  unfold GS
  dsimp only
  rcases hf with ⟨f1, f2⟩ | ⟨f1, f2⟩ <;> rcases hg' with ⟨g1, g2⟩ | ⟨g1, g2⟩
  · left; exact ⟨by rw [f1, g1]; simp, by rw [f2, g2]; simp⟩
  · have hw := hg _ g2
    by_cases h : g x < x
    · left
      exact ⟨by rw [f1]; exact Int.max_eq_left (by omega), by rw [f2, ← g1]; exact Int.max_eq_left (by omega)⟩
    · right
      refine ⟨by rw [f1, f2, ← g1, Int.max_eq_right (by omega), Int.max_eq_right (by omega)], ?_⟩
      rw [f1, Int.max_eq_right (by omega)]; exact g2
  · have hw := hg _ f2
    by_cases h : f x < x
    · left
      exact ⟨by rw [g1]; exact Int.max_eq_right (by omega), by rw [g2, ← f1]; exact Int.max_eq_right (by omega)⟩
    · right
      refine ⟨by rw [g1, g2, ← f1, Int.max_eq_left (by omega), Int.max_eq_left (by omega)], ?_⟩
      rw [g1, Int.max_eq_left (by omega)]; exact f2
  · right
    refine ⟨by rw [f1, g1], ?_⟩
    rcases Int.le_total (f x) (g x) with h | h
    · rw [Int.max_eq_right h]; exact g2
    · rw [Int.max_eq_left h]; exact f2

theorem GS.le (hg : Gap x W) {f g : Int → Int} (hf : GS x W f) (hg' : GS x W g) :
    (f x ≤ g x ↔ f (x + 1) ≤ g (x + 1)) := by
  rcases hf with ⟨f1, f2⟩ | ⟨f1, f2⟩ <;> rcases hg' with ⟨g1, g2⟩ | ⟨g1, g2⟩
  · omega
  · have := hg _ g2; omega
  · have := hg _ f2; omega
  · omega

theorem GS.eq (hg : Gap x W) {f g : Int → Int} (hf : GS x W f) (hg' : GS x W g) :
    (f x = g x ↔ f (x + 1) = g (x + 1)) := by
  rcases hf with ⟨f1, f2⟩ | ⟨f1, f2⟩ <;> rcases hg' with ⟨g1, g2⟩ | ⟨g1, g2⟩
  · omega
  · have := hg _ g2; omega
  · have := hg _ f2; omega
  · omega

theorem GS.decide_le (hg : Gap x W) {f g : Int → Int} (hf : GS x W f) (hg' : GS x W g) :
    decide (f x ≤ g x) = decide (f (x + 1) ≤ g (x + 1)) := by
  simp only [decide_eq_decide]; exact GS.le hg hf hg'

theorem GS.foldl (hg : Gap x W) (op : Int → Int → Int)
    (hop : ∀ f g : Int → Int, GS x W f → GS x W g → GS x W (fun y => op (f y) (g y))) :
    ∀ (L : List (Int → Int)) (acc : Int → Int), GS x W acc → (∀ f ∈ L, GS x W f) →
      GS x W (fun y => (L.map (· y)).foldl op (acc y))
  | [], acc, ha, _ => by simpa using ha
  | f :: L, acc, ha, hL => by
    simp only [List.map_cons, List.foldl_cons]
    exact GS.foldl hg op hop L (fun y => op (acc y) (f y)) (hop _ _ ha (hL f (List.mem_cons_self ..)))
      (fun g hgm => hL g (List.mem_cons_of_mem _ hgm))

end GapStable

/-! ## The threshold of one atom -/

/-- Two integers have the same sign. -/
def SignEq (a b : Int) : Prop := (a < 0 ↔ b < 0) ∧ (a = 0 ↔ b = 0)

theorem SignEq.refl (a : Int) : SignEq a a := ⟨Iff.rfl, Iff.rfl⟩

theorem SignEq.pos {a b : Int} (h : SignEq a b) : (0 < a ↔ 0 < b) := by
  obtain ⟨h1, h2⟩ := h
  constructor
  · intro ha
    rcases Int.lt_trichotomy b 0 with hb | hb | hb
    · have := h1.mpr hb; omega
    · have := h2.mpr hb; omega
    · exact hb
  · intro hb
    rcases Int.lt_trichotomy a 0 with ha | ha | ha
    · have := h1.mp ha; omega
    · have := h2.mp ha; omega
    · exact ha

theorem SignEq.neg {a b : Int} (h : SignEq a b) : SignEq (-a) (-b) := by
  have hp := h.pos
  obtain ⟨_, h2⟩ := h
  refine ⟨⟨fun h' => ?_, fun h' => ?_⟩, ⟨fun h' => ?_, fun h' => ?_⟩⟩
  · have := hp.mp (by omega); omega
  · have := hp.mpr (by omega); omega
  · have := h2.mp (by omega); omega
  · have := h2.mpr (by omega); omega

/-- Where `c·y + K` has its sign: below, at and above `⌊t⌋` for `t = −K / c`. -/
theorem sign_regions (c K y : Int) (hc : c ≠ 0) :
    let fl := (floorCeil K c).1
    (y ≤ fl - 1 → (0 < c → c * y + K < 0) ∧ (c < 0 → 0 < c * y + K)) ∧
    (fl + 1 ≤ y → (0 < c → 0 < c * y + K) ∧ (c < 0 → c * y + K < 0)) := by
  simp only [floorCeil]
  by_cases hpos : 0 < c
  · simp only [hpos, if_true]
    have hq := Int.mul_ediv_add_emod (-K) c
    have hr1 := Int.emod_nonneg (-K) hc
    have hr2 := Int.emod_lt_of_pos (-K) hpos
    generalize (-K) / c = q at hq ⊢
    generalize (-K) % c = r at hq hr1 hr2
    have e1 := Int.mul_sub c y q
    have key : c * y + K = c * (y - q) - r := by omega
    refine ⟨fun hy => ⟨fun _ => ?_, fun h => ?_⟩, fun hy => ⟨fun _ => ?_, fun h => ?_⟩⟩
    · have : c * (y - q) ≤ c * (-1) := Int.mul_le_mul_of_nonneg_left (by omega) (by omega)
      omega
    · exact absurd h (Int.not_lt.mpr (Int.le_of_lt hpos))
    · have : c * 1 ≤ c * (y - q) := Int.mul_le_mul_of_nonneg_left (by omega) (by omega)
      omega
    · exact absurd h (Int.not_lt.mpr (Int.le_of_lt hpos))
  · have hneg : c < 0 := by omega
    simp only [hpos, if_false]
    have hm : 0 < -c := by omega
    have hq := Int.mul_ediv_add_emod K (-c)
    have hr1 := Int.emod_nonneg K (by omega : -c ≠ 0)
    have hr2 := Int.emod_lt_of_pos K hm
    generalize K / (-c) = q at hq ⊢
    generalize K % (-c) = r at hq hr1 hr2
    have e1 := Int.mul_sub (-c) y q
    have e2 := Int.neg_mul c y
    have e3 := Int.neg_mul c q
    have key : c * y + K = -((-c) * (y - q) - r) := by omega
    refine ⟨fun hy => ⟨fun h => ?_, fun _ => ?_⟩, fun hy => ⟨fun h => ?_, fun _ => ?_⟩⟩
    · exact h.elim
    · have : (-c) * (y - q) ≤ (-c) * (-1) := Int.mul_le_mul_of_nonneg_left (by omega) (by omega)
      omega
    · exact h.elim
    · have : (-c) * 1 ≤ (-c) * (y - q) := Int.mul_le_mul_of_nonneg_left (by omega) (by omega)
      omega

theorem floorCeil_snd (K c : Int) :
    (floorCeil K c).2 = (floorCeil K c).1 ∨ (floorCeil K c).2 = (floorCeil K c).1 + 1 := by
  simp only [floorCeil]
  generalize (if 0 < c then -K else K) = n
  generalize (if 0 < c then c else -c) = m
  by_cases h : n % m = 0 <;> simp [h]

/-- The sign of `c·y + K` is the same at `x` and `x + 1` unless both are threshold candidates. -/
theorem sign_step (c K x : Int) (hc : c ≠ 0)
    (hx : x ∉ [(floorCeil K c).1 - 1, (floorCeil K c).1, (floorCeil K c).2, (floorCeil K c).2 + 1] ∨
      x + 1 ∉ [(floorCeil K c).1 - 1, (floorCeil K c).1, (floorCeil K c).2, (floorCeil K c).2 + 1]) :
    SignEq (c * x + K) (c * (x + 1) + K) := by
  have hr := sign_regions c K
  have hs := floorCeil_snd K c
  generalize (floorCeil K c).1 = fl at hr hs hx
  generalize (floorCeil K c).2 = cl at hs hx
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
  have hx' : x ≤ fl - 2 ∨ fl + 1 ≤ x := by omega
  rcases hx' with h | h
  · obtain ⟨a1, a2⟩ := (hr x hc).1 (by omega)
    obtain ⟨b1, b2⟩ := (hr (x + 1) hc).1 (by omega)
    by_cases hp : 0 < c
    · have := a1 hp; have := b1 hp; constructor <;> omega
    · have := a2 (by omega); have := b2 (by omega); constructor <;> omega
  · obtain ⟨a1, a2⟩ := (hr x hc).2 (by omega)
    obtain ⟨b1, b2⟩ := (hr (x + 1) hc).2 (by omega)
    by_cases hp : 0 < c
    · have := a1 hp; have := b1 hp; constructor <;> omega
    · have := a2 (by omega); have := b2 (by omega); constructor <;> omega

/-! ## Endpoint evaluation agrees on boxes with the same observations -/

/-- The extrema of `f` have the same signs on `b₁` and `b₂`. -/
def ExtremaAgree (b₁ b₂ : Box) (f : LinForm) : Prop :=
  SignEq (fmin b₁ f) (fmin b₂ f) ∧ SignEq (fmax b₁ f) (fmax b₂ f)

theorem minSum_neg (b : Box) (l : List (String × Int)) :
    minSum b (l.map fun (q, c) => (q, -c)) = - maxSum b l := by
  induction l with
  | nil => simp [minSum, maxSum]
  | cons p l ih =>
    have e1 := minSum_cons b (p.1, -p.2) (l.map fun (q, c) => (q, -c))
    have e2 := maxSum_cons b p l
    simp only [List.map_cons] at e1 ⊢
    rw [e1, e2, ih]
    by_cases h : 0 ≤ p.2
    · by_cases h' : p.2 = 0
      · simp [h']
      · rw [if_neg (by omega), if_pos h]; simp only [Int.neg_mul]; omega
    · rw [if_pos (by omega), if_neg h]; simp only [Int.neg_mul]; omega

theorem maxSum_neg (b : Box) (l : List (String × Int)) :
    maxSum b (l.map fun (q, c) => (q, -c)) = - minSum b l := by
  induction l with
  | nil => simp [minSum, maxSum]
  | cons p l ih =>
    have e1 := maxSum_cons b (p.1, -p.2) (l.map fun (q, c) => (q, -c))
    have e2 := minSum_cons b p l
    simp only [List.map_cons] at e1 ⊢
    rw [e1, e2, ih]
    by_cases h : 0 ≤ p.2
    · by_cases h' : p.2 = 0
      · simp [h']
      · rw [if_neg (by omega), if_pos h]; simp only [Int.neg_mul]; omega
    · rw [if_pos (by omega), if_neg h]; simp only [Int.neg_mul]; omega

theorem fmin_neg (b : Box) (f : LinForm) : fmin b f.neg = - fmax b f := by
  simp only [fmin, fmax, LinForm.neg, minSum_neg]; omega

theorem fmax_neg (b : Box) (f : LinForm) : fmax b f.neg = - fmin b f := by
  simp only [fmin, fmax, LinForm.neg, maxSum_neg]; omega

theorem ExtremaAgree.neg {b₁ b₂ : Box} {f : LinForm} (h : ExtremaAgree b₁ b₂ f) : ExtremaAgree b₁ b₂ f.neg := by
  simp only [ExtremaAgree, fmin_neg, fmax_neg]
  exact ⟨h.2.neg, h.1.neg⟩

theorem atoms_nnfAux (c : Cond) : ∀ p, ∀ fr ∈ atomsOf (nnfAux p c), ∃ gr ∈ atomsOf c, fr.1 = gr.1 ∨ fr.1 = gr.1.neg := by
  induction c with
  | top | bottom => intro p fr h; cases p <;> simp [nnfAux, atomsOf] at h
  | atom f r =>
    intro p fr h
    cases p
    · cases r <;> simp [nnfAux, negAtom, atomsOf] at h <;> subst h <;> simp [atomsOf]
    · simp [nnfAux, atomsOf] at h; subst h; simp [atomsOf]
  | and a b ia ib | or a b ia ib =>
    intro p fr h
    cases p <;> simp only [nnfAux, atomsOf, List.mem_append] at h <;> rcases h with h | h
    all_goals first
      | (obtain ⟨gr, hg, he⟩ := ia _ fr h; exact ⟨gr, List.mem_append_left _ hg, he⟩)
      | (obtain ⟨gr, hg, he⟩ := ib _ fr h; exact ⟨gr, List.mem_append_right _ hg, he⟩)
  | not a ia =>
    intro p fr h
    cases p <;> simp only [nnfAux] at h <;>
      (obtain ⟨gr, hg, he⟩ := ia _ fr h; exact ⟨gr, hg, he⟩)

theorem atomPossible_congr {b₁ b₂ : Box} {f : LinForm} (h : ExtremaAgree b₁ b₂ f) (r : Rel) :
    atomPossible b₁ f r = atomPossible b₂ f r ∧ atomCertain b₁ f r = atomCertain b₂ f r := by
  obtain ⟨⟨h1, h2⟩, ⟨h3, h4⟩⟩ := h
  have le1 : fmin b₁ f ≤ 0 ↔ fmin b₂ f ≤ 0 := by rw [Int.le_iff_lt_or_eq, Int.le_iff_lt_or_eq, h1, h2]
  have le2 : fmax b₁ f ≤ 0 ↔ fmax b₂ f ≤ 0 := by rw [Int.le_iff_lt_or_eq, Int.le_iff_lt_or_eq, h3, h4]
  have ge2 : 0 ≤ fmax b₁ f ↔ 0 ≤ fmax b₂ f := by rw [← Int.not_lt, ← Int.not_lt, h3]
  have gt1 : 0 < fmin b₁ f ↔ 0 < fmin b₂ f := SignEq.pos ⟨h1, h2⟩
  cases r <;> simp only [atomPossible, atomCertain, decide_eq_decide, h1, h2, h3, h4, le1, le2, ge2, gt1] <;>
    exact ⟨trivial, trivial⟩

theorem endsE_congr {b₁ b₂ : Box} : ∀ c : Cond, (∀ fr ∈ atomsOf c, ExtremaAgree b₁ b₂ fr.1.val) →
    endsE b₁ c = endsE b₂ c
  | .top, _ | .bottom, _ => rfl
  | .atom f r, h => by
    have := atomPossible_congr (h (f, r) (by simp [atomsOf])) r
    simp only [endsE, this.1, this.2]
  | .and a b, h | .or a b, h => by
    have ia := endsE_congr a (fun fr hf => h fr (List.mem_append_left _ hf))
    have ib := endsE_congr b (fun fr hf => h fr (List.mem_append_right _ hf))
    simp only [endsE, ia, ib]
  | .not a, h => by
    have ia := endsE_congr a h
    simp only [endsE, ia]

/-- Boxes with the same membership and point-ness on which every atom's extrema have the same signs. -/
structure BoxAgree (b₁ b₂ : Box) (c : Cond) : Prop where
  mem : ∀ q, b₁.mem q = b₂.mem q
  point : ∀ q, b₁.isPoint q = b₂.isPoint q
  atoms : ∀ fr ∈ atomsOf c, ExtremaAgree b₁ b₂ fr.1.val

theorem BoxAgree.nnf {b₁ b₂ : Box} {c : Cond} (h : BoxAgree b₁ b₂ c) :
    ∀ fr ∈ atomsOf (nnf c), ExtremaAgree b₁ b₂ fr.1.val := by
  intro fr hfr
  obtain ⟨gr, hg, he⟩ := atoms_nnfAux c true fr hfr
  rcases he with he | he
  · rw [he]; exact h.atoms gr hg
  · rw [he]; exact (h.atoms gr hg).neg

theorem possibleE_congr {b₁ b₂ : Box} {c : Cond} (h : BoxAgree b₁ b₂ c) : possibleE b₁ c = possibleE b₂ c := by
  simp only [possibleE, endsE_congr (nnf c) h.nnf]

theorem certainE_congr {b₁ b₂ : Box} {c : Cond} (h : BoxAgree b₁ b₂ c) : certainE b₁ c = certainE b₂ c := by
  simp only [certainE, endsE_congr (nnf c) h.nnf]

theorem scoped_congr {b₁ b₂ : Box} {c : Cond} (h : BoxAgree b₁ b₂ c) : Scoped b₁ c = Scoped b₂ c := by
  have : b₁.mem = b₂.mem := funext h.mem
  simp only [Scoped, this]

theorem sepOK_congr {b₁ b₂ : Box} (hp : ∀ q, b₁.isPoint q = b₂.isPoint q) (c : Cond) : sepOK b₁ c = sepOK b₂ c := by
  simp only [sepOK, hp]

theorem unitOK_congr {b₁ b₂ : Box} (hp : ∀ q, b₁.isPoint q = b₂.isPoint q) : ∀ c : Cond, unitOK b₁ c = unitOK b₂ c
  | .top | .bottom => rfl
  | .atom f r => by cases r <;> simp [unitOK, unitForm, hp]
  | .and a b | .or a b => by simp only [unitOK, unitOK_congr hp a, unitOK_congr hp b]
  | .not a => by simp only [unitOK, unitOK_congr hp a]

theorem condOK_congr {b₁ b₂ : Box} {c : Cond} (h : BoxAgree b₁ b₂ c) : condOK b₁ c = condOK b₂ c := by
  simp only [condOK, scoped_congr h, Separable, UnitCoefficients, sepOK_congr h.point, unitOK_congr h.point]

theorem sharedName_congr {b₁ b₂ : Box} (hp : ∀ q, b₁.isPoint q = b₂.isPoint q) (c : Cond) :
    sharedName b₁ c = sharedName b₂ c := by
  simp only [sharedName, hp]

theorem unitBad_congr {b₁ b₂ : Box} (hp : ∀ q, b₁.isPoint q = b₂.isPoint q) (c : Cond) :
    unitBad b₁ c = unitBad b₂ c := by
  simp only [unitBad, hp]

/-! ## The perturbed estimates -/

/-- The estimates as functions of the moved value: the first estimate with the endpoint's id moves, every
other one is constant. -/
def famOf (p : Estimate → Bool) (s : Side) : List Estimate → List (Int → Estimate)
  | [] => []
  | est :: rest => if p est then (fun y => setSide s y est) :: rest.map (fun e _ => e)
      else (fun _ => est) :: famOf p s rest

theorem famOf_eval (p : Estimate → Bool) (s : Side) (y : Int) :
    ∀ l : List Estimate, (famOf p s l).map (· y) = setFirst p (setSide s y) l
  | [] => rfl
  | est :: rest => by
    simp only [famOf, setFirst]
    split
    · simp only [List.map_cons, List.map_map, List.cons.injEq, true_and]
      exact List.map_id' rest |>.symm ▸ rfl
    · simp [famOf_eval p s y rest]

theorem setSide_fields (s : Side) (y : Int) (est : Estimate) :
    (setSide s y est).id = est.id ∧ (setSide s y est).seq = est.seq ∧ (setSide s y est).quantity = est.quantity := by
  cases s <;> exact ⟨rfl, rfl, rfl⟩

/-- Each function of the family is constant (an estimate of the list), or moves the first estimate
satisfying `p` on side `s`. -/
theorem famOf_mem (p : Estimate → Bool) (s : Side) :
    ∀ (l : List Estimate) (f : Int → Estimate), f ∈ famOf p s l →
      (∃ est ∈ l, f = fun _ => est) ∨ ∃ est, l.find? p = some est ∧ f = fun y => setSide s y est
  | [], f, h => by cases h
  | est :: rest, f, h => by
    simp only [famOf] at h
    split at h
    · rename_i hp
      rcases List.mem_cons.mp h with rfl | h
      · exact Or.inr ⟨est, by simp [List.find?_cons, hp], rfl⟩
      · obtain ⟨e', he', rfl⟩ := List.mem_map.mp h
        exact Or.inl ⟨e', List.mem_cons_of_mem _ he', rfl⟩
    · rename_i hp
      rcases List.mem_cons.mp h with rfl | h
      · exact Or.inl ⟨est, List.mem_cons_self .., rfl⟩
      · rcases famOf_mem p s rest f h with ⟨e', he', rfl⟩ | ⟨e', hf, rfl⟩
        · exact Or.inl ⟨e', List.mem_cons_of_mem _ he', rfl⟩
        · exact Or.inr ⟨e', by simp [List.find?_cons, hp, hf], rfl⟩

theorem famOf_find (p : Estimate → Bool) (s : Side) :
    ∀ (l : List Estimate) (est : Estimate), l.find? p = some est → (fun y => setSide s y est) ∈ famOf p s l
  | [], _, h => by cases h
  | e :: rest, est, h => by
    simp only [List.find?_cons] at h
    simp only [famOf]
    split
    · rename_i hp
      rw [hp] at h
      simp only [Option.some.injEq] at h
      subst h
      exact List.mem_cons_self ..
    · rename_i hp
      simp only [Bool.not_eq_true] at hp
      rw [hp] at h
      exact List.mem_cons_of_mem _ (famOf_find p s rest est h)

theorem map_setFirst {α β : Type} (p : α → Bool) (f : α → α) (g : α → β) (hg : ∀ a, g (f a) = g a) :
    ∀ l : List α, (setFirst p f l).map g = l.map g
  | [] => rfl
  | a :: l => by
    simp only [setFirst]
    split
    · simp [hg]
    · simp [map_setFirst p f g hg l]

theorem strip_perturb (d : Decision) (e : Endpoint) (y : Int) : strip (perturb d e y) = strip d := by
  simp only [strip, perturb]
  congr 1
  apply map_setFirst
  intro est
  cases e.side <;> rfl

/-! ## Combination of moved estimates -/

def SeqConst (f : Int → Estimate) : Prop := ∀ y y', (f y).seq = (f y').seq

/-- `latestOf` on functions, choosing by the (constant) sequence numbers. -/
def latestF : (Int → Estimate) → List (Int → Estimate) → (Int → Estimate)
  | f, [] => f
  | f, g :: gs => latestF (if (f 0).seq < (g 0).seq then g else f) gs

theorem latestOf_F (y : Int) : ∀ (f : Int → Estimate) (gs : List (Int → Estimate)),
    (∀ g ∈ f :: gs, SeqConst g) → latestOf (f y) (gs.map (· y)) = latestF f gs y
  | f, [], _ => rfl
  | f, g :: gs, h => by
    simp only [List.map_cons, latestOf, latestF]
    have hf := h f (List.mem_cons_self ..)
    have hg := h g (List.mem_cons_of_mem _ (List.mem_cons_self ..))
    have hs : ((f y).seq < (g y).seq) = ((f 0).seq < (g 0).seq) := by rw [hf y 0, hg y 0]
    by_cases hlt : (f 0).seq < (g 0).seq
    · have : (f y).seq < (g y).seq := by rw [hs]; exact hlt
      simp only [this, hlt, if_true]
      exact latestOf_F y g gs (fun g' hg' => h g' (by
        rcases List.mem_cons.mp hg' with rfl | hg'
        · exact List.mem_cons_of_mem _ (List.mem_cons_self ..)
        · exact List.mem_cons_of_mem _ (List.mem_cons_of_mem _ hg')))
    · have : ¬ (f y).seq < (g y).seq := by rw [hs]; exact hlt
      simp only [this, hlt, if_false]
      exact latestOf_F y f gs (fun g' hg' => h g' (by
        rcases List.mem_cons.mp hg' with rfl | hg'
        · exact List.mem_cons_self ..
        · exact List.mem_cons_of_mem _ (List.mem_cons_of_mem _ hg')))

theorem latestF_mem : ∀ (f : Int → Estimate) (gs : List (Int → Estimate)), latestF f gs ∈ f :: gs
  | f, [] => List.mem_cons_self ..
  | f, g :: gs => by
    simp only [latestF]
    split
    · have := latestF_mem g gs
      rcases List.mem_cons.mp this with h | h
      · rw [h]; exact List.mem_cons_of_mem _ (List.mem_cons_self ..)
      · exact List.mem_cons_of_mem _ (List.mem_cons_of_mem _ h)
    · have := latestF_mem f gs
      rcases List.mem_cons.mp this with h | h
      · rw [h]; exact List.mem_cons_self ..
      · exact List.mem_cons_of_mem _ (List.mem_cons_of_mem _ h)

theorem GS.foldl_field {x : Int} {W : List Int} (hg : Gap x W) (op : Int → Int → Int)
    (hop : ∀ f g : Int → Int, GS x W f → GS x W g → GS x W (fun y => op (f y) (g y))) (g : Estimate → Int) :
    ∀ (L : List (Int → Estimate)) (acc : Int → Int), GS x W acc → (∀ f ∈ L, GS x W (fun y => g (f y))) →
      GS x W (fun y => (L.map (· y)).foldl (fun m e => op m (g e)) (acc y))
  | [], acc, ha, _ => by simpa using ha
  | f :: L, acc, ha, hL => by
    simp only [List.map_cons, List.foldl_cons]
    exact GS.foldl_field hg op hop g L (fun y => op (acc y) (g (f y))) (hop _ _ ha (hL f (List.mem_cons_self ..)))
      (fun f' hf' => hL f' (List.mem_cons_of_mem _ hf'))

theorem foldl_field_congr (op : Int → Int → Int) (g : Estimate → Int) (y y' : Int) :
    ∀ (L : List (Int → Estimate)) (init : Int), (∀ f ∈ L, g (f y) = g (f y')) →
      (L.map (· y)).foldl (fun m e => op m (g e)) init = (L.map (· y')).foldl (fun m e => op m (g e)) init
  | [], _, _ => rfl
  | f :: L, init, h => by
    simp only [List.map_cons, List.foldl_cons, h f (List.mem_cons_self ..)]
    exact foldl_field_congr op g y y' L _ (fun f' hf' => h f' (List.mem_cons_of_mem _ hf'))

/-- The effective range of moved estimates is gap-stable. -/
theorem combine_GS {x : Int} {W : List Int} (hg : Gap x W) (comb : Option Combination) :
    ∀ (Fq : List (Int → Estimate)), Fq ≠ [] → (∀ f ∈ Fq, SeqConst f) →
      (∀ f ∈ Fq, GS x W (fun y => (f y).lo)) → (∀ f ∈ Fq, GS x W (fun y => (f y).hi)) →
      GS x W (fun y => (combineRange comb (Fq.map (· y))).1) ∧ GS x W (fun y => (combineRange comb (Fq.map (· y))).2)
  | [], hne, _, _, _ => absurd rfl hne
  | [f0], _, _, hlo, hhi => by
    simp only [List.map_cons, List.map_nil, combineRange]
    exact ⟨hlo f0 (List.mem_cons_self ..), hhi f0 (List.mem_cons_self ..)⟩
  | f0 :: f1 :: fs, _, hseq, hlo, hhi => by
    have hlo' : ∀ f ∈ f1 :: fs, GS x W (fun y => (f y).lo) := fun f hf => hlo f (List.mem_cons_of_mem _ hf)
    have hhi' : ∀ f ∈ f1 :: fs, GS x W (fun y => (f y).hi) := fun f hf => hhi f (List.mem_cons_of_mem _ hf)
    have hmin : ∀ f g : Int → Int, GS x W f → GS x W g → GS x W (fun y => min (f y) (g y)) :=
      fun f g hf hg' => GS.min hg hf hg'
    have hmax : ∀ f g : Int → Int, GS x W f → GS x W g → GS x W (fun y => max (f y) (g y)) :=
      fun f g hf hg' => GS.max hg hf hg'
    cases comb with
    | none => exact ⟨hlo f0 (List.mem_cons_self ..), hhi f0 (List.mem_cons_self ..)⟩
    | some c =>
      cases c with
      | hull =>
        exact ⟨GS.foldl_field hg min hmin (·.lo) (f1 :: fs) _ (hlo f0 (List.mem_cons_self ..)) hlo',
          GS.foldl_field hg max hmax (·.hi) (f1 :: fs) _ (hhi f0 (List.mem_cons_self ..)) hhi'⟩
      | intersection =>
        exact ⟨GS.foldl_field hg max hmax (·.lo) (f1 :: fs) _ (hlo f0 (List.mem_cons_self ..)) hlo',
          GS.foldl_field hg min hmin (·.hi) (f1 :: fs) _ (hhi f0 (List.mem_cons_self ..)) hhi'⟩
      | latest =>
        have hl : ∀ y, latestOf (f0 y) ((f1 :: fs).map (· y)) = latestF f0 (f1 :: fs) y :=
          fun y => latestOf_F y f0 (f1 :: fs) hseq
        have hm := latestF_mem f0 (f1 :: fs)
        show GS x W (fun y => (latestOf (f0 y) ((f1 :: fs).map (· y))).lo) ∧
          GS x W (fun y => (latestOf (f0 y) ((f1 :: fs).map (· y))).hi)
        simp only [hl]
        exact ⟨hlo _ hm, hhi _ hm⟩

/-- The effective lower (upper) bound does not move when no lower (upper) bound moves. -/
theorem combine_const (comb : Option Combination) (Fq : List (Int → Estimate)) (y y' : Int)
    (hseq : ∀ f ∈ Fq, SeqConst f) :
    ((∀ f ∈ Fq, (f y).lo = (f y').lo) → (combineRange comb (Fq.map (· y))).1 = (combineRange comb (Fq.map (· y'))).1) ∧
    ((∀ f ∈ Fq, (f y).hi = (f y').hi) → (combineRange comb (Fq.map (· y))).2 = (combineRange comb (Fq.map (· y'))).2) := by
  match Fq with
  | [] => exact ⟨fun _ => rfl, fun _ => rfl⟩
  | [f0] =>
    simp only [List.map_cons, List.map_nil, combineRange]
    exact ⟨fun h => h f0 (List.mem_cons_self ..), fun h => h f0 (List.mem_cons_self ..)⟩
  | f0 :: f1 :: fs =>
    have hl : ∀ z, latestOf (f0 z) ((f1 :: fs).map (· z)) = latestF f0 (f1 :: fs) z :=
      fun z => latestOf_F z f0 (f1 :: fs) hseq
    have hm := latestF_mem f0 (f1 :: fs)
    have h0 : ∀ (g : Estimate → Int), (∀ f ∈ f0 :: f1 :: fs, g (f y) = g (f y')) → g (f0 y) = g (f0 y') :=
      fun g h => h f0 (List.mem_cons_self ..)
    have hr : ∀ (g : Estimate → Int), (∀ f ∈ f0 :: f1 :: fs, g (f y) = g (f y')) → ∀ f ∈ f1 :: fs, g (f y) = g (f y') :=
      fun g h f hf => h f (List.mem_cons_of_mem _ hf)
    cases comb with
    | none => exact ⟨fun h => h f0 (List.mem_cons_self ..), fun h => h f0 (List.mem_cons_self ..)⟩
    | some c =>
      cases c with
      | hull =>
        refine ⟨fun h => ?_, fun h => ?_⟩
        · show ((f1 :: fs).map (· y)).foldl (fun m e => min m e.lo) (f0 y).lo =
            ((f1 :: fs).map (· y')).foldl (fun m e => min m e.lo) (f0 y').lo
          rw [h0 (·.lo) h]
          exact foldl_field_congr min (·.lo) y y' (f1 :: fs) _ (hr (·.lo) h)
        · show ((f1 :: fs).map (· y)).foldl (fun m e => max m e.hi) (f0 y).hi =
            ((f1 :: fs).map (· y')).foldl (fun m e => max m e.hi) (f0 y').hi
          rw [h0 (·.hi) h]
          exact foldl_field_congr max (·.hi) y y' (f1 :: fs) _ (hr (·.hi) h)
      | intersection =>
        refine ⟨fun h => ?_, fun h => ?_⟩
        · show ((f1 :: fs).map (· y)).foldl (fun m e => max m e.lo) (f0 y).lo =
            ((f1 :: fs).map (· y')).foldl (fun m e => max m e.lo) (f0 y').lo
          rw [h0 (·.lo) h]
          exact foldl_field_congr max (·.lo) y y' (f1 :: fs) _ (hr (·.lo) h)
        · show ((f1 :: fs).map (· y)).foldl (fun m e => min m e.hi) (f0 y).hi =
            ((f1 :: fs).map (· y')).foldl (fun m e => min m e.hi) (f0 y').hi
          rw [h0 (·.hi) h]
          exact foldl_field_congr min (·.hi) y y' (f1 :: fs) _ (hr (·.hi) h)
      | latest =>
        refine ⟨fun h => ?_, fun h => ?_⟩
        · show (latestOf (f0 y) ((f1 :: fs).map (· y))).lo = (latestOf (f0 y') ((f1 :: fs).map (· y'))).lo
          rw [hl, hl]; exact h _ hm
        · show (latestOf (f0 y) ((f1 :: fs).map (· y))).hi = (latestOf (f0 y') ((f1 :: fs).map (· y'))).hi
          rw [hl, hl]; exact h _ hm

/-! ## One step of the moved endpoint -/

theorem filterMap_congrOf {α β : Type} {f g : α → Option β} :
    ∀ {l : List α}, (∀ a ∈ l, f a = g a) → l.filterMap f = l.filterMap g
  | [], _ => rfl
  | a :: l, h => by
    simp only [List.filterMap_cons, h a (List.mem_cons_self ..),
      filterMap_congrOf (l := l) (fun b hb => h b (List.mem_cons_of_mem _ hb))]

theorem setFirst_self {p : Estimate → Bool} {s : Side} {est0 : Estimate} :
    ∀ {l : List Estimate}, l.find? p = some est0 → setFirst p (setSide s (est0.side s)) l = l
  | [], h => by cases h
  | e :: l, h => by
    simp only [List.find?_cons] at h
    simp only [setFirst]
    split
    · rename_i hp
      rw [hp] at h
      simp only [Option.some.injEq] at h
      subst h
      cases s <;> rfl
    · rename_i hp
      simp only [Bool.not_eq_true] at hp
      rw [hp] at h
      rw [setFirst_self h]

/-- The record at the current value is the record. -/
theorem perturb_current {d : Decision} {e : Endpoint} {est0 : Estimate} (hest : estimateOf d e.estimate = some est0) :
    perturb d e (current d e) = d := by
  have hc : current d e = est0.side e.side := by simp [current, hest]
  unfold perturb
  rw [hc, setFirst_self hest]

section Step
variable {R : RiskDoc} {d : Decision} {e : Endpoint} {est0 : Estimate}

/-- The family of the moved estimates. -/
def fam (d : Decision) (e : Endpoint) : List (Int → Estimate) := famOf (·.id == e.estimate) e.side d.estimates

theorem perturb_estimates (y : Int) : (perturb d e y).estimates = (fam d e).map (· y) := by
  simp only [perturb, fam, famOf_eval]

theorem fam_cases (hest : estimateOf d e.estimate = some est0) {f : Int → Estimate} (hf : f ∈ fam d e) :
    (∃ est ∈ d.estimates, f = fun _ => est) ∨ f = fun y => setSide e.side y est0 := by
  rcases famOf_mem _ _ _ f hf with h | ⟨est, hfind, rfl⟩
  · exact Or.inl h
  · have : est = est0 := by
      have h2 : estimateOf d e.estimate = some est := hfind
      rw [hest] at h2; cases h2; rfl
    subst this
    exact Or.inr rfl

theorem fam_seq (hest : estimateOf d e.estimate = some est0) {f : Int → Estimate} (hf : f ∈ fam d e) :
    SeqConst f ∧ ∀ y, (f y).quantity = (f 0).quantity := by
  rcases fam_cases hest hf with ⟨est, _, rfl⟩ | rfl
  · exact ⟨fun _ _ => rfl, fun _ => rfl⟩
  · exact ⟨fun y y' => by rw [(setSide_fields _ y est0).2.1, (setSide_fields _ y' est0).2.1],
      fun y => by rw [(setSide_fields _ y est0).2.2, (setSide_fields _ 0 est0).2.2]⟩

/-- The moved estimates of quantity `p`. -/
def famOn (d : Decision) (e : Endpoint) (p : String) : List (Int → Estimate) :=
  (fam d e).filter (fun f => (f 0).quantity == p)

theorem estimatesOf_perturb (hest : estimateOf d e.estimate = some est0) (p : String) (y : Int) :
    estimatesOf (perturb d e y) p = (famOn d e p).map (· y) := by
  simp only [estimatesOf, perturb_estimates, famOn, List.filter_map]
  congr 1
  apply List.filter_congr
  intro f hf
  simp only [Function.comp, (fam_seq hest hf).2 y]

theorem est0_mem (hest : estimateOf d e.estimate = some est0) : est0 ∈ d.estimates :=
  List.mem_of_find?_eq_some hest

/-- Estimates of another quantity do not move. -/
theorem famOn_const (hest : estimateOf d e.estimate = some est0) {p : String} (hp : p ≠ est0.quantity)
    {f : Int → Estimate} (hf : f ∈ famOn d e p) : ∃ est ∈ d.estimates, f = fun _ => est := by
  have hm := (List.mem_filter.mp hf)
  rcases fam_cases hest hm.1 with h | rfl
  · exact h
  · exfalso
    have := hm.2
    simp only [beq_iff_eq, (setSide_fields _ 0 est0).2.2] at this
    exact hp this.symm

theorem estimatesOf_other (hest : estimateOf d e.estimate = some est0) {p : String} (hp : p ≠ est0.quantity)
    (y y' : Int) : estimatesOf (perturb d e y) p = estimatesOf (perturb d e y') p := by
  rw [estimatesOf_perturb hest, estimatesOf_perturb hest]
  apply List.map_congr_left
  intro f hf
  obtain ⟨est, _, rfl⟩ := famOn_const hest hp hf
  rfl

theorem famOn_ne (hest : estimateOf d e.estimate = some est0) : famOn d e est0.quantity ≠ [] := by
  intro h
  have hm : (fun y => setSide e.side y est0) ∈ fam d e := famOf_find _ _ _ _ hest
  have : (fun y => setSide e.side y est0) ∈ famOn d e est0.quantity :=
    List.mem_filter.mpr ⟨hm, by simp [(setSide_fields _ 0 est0).2.2]⟩
  rw [h] at this
  cases this

/-- The endpoints of the cited estimates of the moved quantity. -/
def endsOf (d : Decision) (q : String) : List Int := (estimatesOf d q).flatMap fun z => [z.lo, z.hi]

theorem mem_endsOf {d : Decision} {est : Estimate} (h : est ∈ d.estimates) :
    est.lo ∈ endsOf d est.quantity ∧ est.hi ∈ endsOf d est.quantity := by
  have : est ∈ estimatesOf d est.quantity := List.mem_filter.mpr ⟨h, by simp⟩
  exact ⟨List.mem_flatMap.mpr ⟨est, this, by simp⟩, List.mem_flatMap.mpr ⟨est, this, by simp⟩⟩

/-- On the moved quantity, each bound of each estimate is gap-stable, and the bound on the other side of the
endpoint does not move. -/
theorem famOn_bounds (hest : estimateOf d e.estimate = some est0) {x : Int} {f : Int → Estimate}
    (hf : f ∈ famOn d e est0.quantity) :
    GS x (endsOf d est0.quantity) (fun y => (f y).lo) ∧ GS x (endsOf d est0.quantity) (fun y => (f y).hi) ∧
    (e.side = .hi → ∀ y y', (f y).lo = (f y').lo) ∧ (e.side = .lo → ∀ y y', (f y).hi = (f y').hi) := by
  have hm := List.mem_filter.mp hf
  rcases fam_cases hest hm.1 with ⟨est, hin, rfl⟩ | rfl
  · have hq : est.quantity = est0.quantity := by simpa using hm.2
    have := mem_endsOf hin
    rw [hq] at this
    exact ⟨GS.const this.1, GS.const this.2, fun _ _ _ => rfl, fun _ _ _ => rfl⟩
  · have := mem_endsOf (est0_mem hest)
    cases hs : e.side with
    | lo =>
      refine ⟨?_, ?_, (fun h => by cases h), fun _ y y' => ?_⟩
      · show GS x _ (fun y => (setSide .lo y est0).lo); exact GS.id
      · show GS x _ (fun y => (setSide .lo y est0).hi); exact GS.const this.2
      · show (setSide .lo y est0).hi = (setSide .lo y' est0).hi; rfl
    | hi =>
      refine ⟨?_, ?_, fun _ y y' => ?_, (fun h => by cases h)⟩
      · show GS x _ (fun y => (setSide .hi y est0).lo); exact GS.const this.1
      · show GS x _ (fun y => (setSide .hi y est0).hi); exact GS.id
      · show (setSide .hi y est0).lo = (setSide .hi y' est0).lo; rfl

end Step

/-! ## The box at `x` and at `x + 1` -/

theorem boxEntry_name {R : RiskDoc} {d : Decision} {qd : Quantity} {en : BoxEntry}
    (h : boxEntry R d qd = some en) : en.name = qd.name := by
  unfold boxEntry at h
  split at h
  · cases h; rfl
  · split at h
    · cases h
    · cases h; rfl

theorem boxEntry_isSome_name {R : RiskDoc} {d : Decision} {qd qd' : Quantity} (h : qd.name = qd'.name) :
    (boxEntry R d qd).isSome = (boxEntry R d qd').isSome := by
  unfold boxEntry
  rw [h]
  split
  · rfl
  · split <;> rfl

theorem find_filterMap_none {q : String} {g : Quantity → Option BoxEntry}
    (hg : ∀ qd en, g qd = some en → en.name = qd.name) :
    ∀ {l : List Quantity}, (∀ qd ∈ l, qd.name = q → g qd = none) → (l.filterMap g).find? (·.name == q) = none
  | [], _ => rfl
  | a :: l, h => by
    simp only [List.filterMap_cons]
    cases ha : g a with
    | none => exact find_filterMap_none hg (fun b hb => h b (List.mem_cons_of_mem _ hb))
    | some en =>
      have hn := hg a en ha
      have hne : a.name ≠ q := fun he => by rw [h a (List.mem_cons_self ..) he] at ha; cases ha
      have : (a.name == q) = false := by simpa using hne
      simp only [List.find?_cons, hn, this]
      exact find_filterMap_none hg (fun b hb => h b (List.mem_cons_of_mem _ hb))

/-- The box entry of a quantity is the entry of the first quantity of that name. -/
theorem find_box (R : RiskDoc) (d : Decision) (q : String) :
    (box R d).find q = (d.quantities.find? (·.name == q)).bind (boxEntry R d) := by
  unfold box Box.find
  generalize d.quantities = l
  induction l with
  | nil => rfl
  | cons a l ih =>
    simp only [List.filterMap_cons, List.find?_cons]
    by_cases hq : a.name = q
    · simp only [hq, beq_self_eq_true, Option.bind_some]
      cases ha : boxEntry R d a with
      | none =>
        simp only
        apply find_filterMap_none (fun qd en h => boxEntry_name h)
        intro b _ hb
        have := boxEntry_isSome_name (R := R) (d := d) (hb.trans hq.symm)
        rw [ha] at this
        cases hb' : boxEntry R d b with
        | none => rfl
        | some _ => rw [hb'] at this; cases this
      | some en =>
        simp [boxEntry_name ha, hq]
    · have : (a.name == q) = false := by simpa using hq
      rw [this]
      cases ha : boxEntry R d a with
      | none => exact ih
      | some en =>
        simp only [List.find?_cons, boxEntry_name ha, this]
        exact ih

section BoxStep
variable {R : RiskDoc} {d : Decision} {e : Endpoint} {est0 : Estimate}

def Elo (R : RiskDoc) (d : Decision) (e : Endpoint) (q : String) (y : Int) : Int :=
  (combineRange R.risk.combination ((famOn d e q).map (· y))).1
def Ehi (R : RiskDoc) (d : Decision) (e : Endpoint) (q : String) (y : Int) : Int :=
  (combineRange R.risk.combination ((famOn d e q).map (· y))).2

theorem boxEntry_other (hest : estimateOf d e.estimate = some est0) {qd : Quantity} (hq : qd.name ≠ est0.quantity)
    (y : Int) : boxEntry R (perturb d e y) qd = boxEntry R d qd := by
  have h := estimatesOf_other hest hq y (current d e)
  rw [perturb_current hest] at h
  unfold boxEntry
  rw [h]
  rfl

theorem boxEntry_moved (hest : estimateOf d e.estimate = some est0) {qd : Quantity} (hq : qd.name = est0.quantity)
    (y : Int) :
    boxEntry R (perturb d e y) qd = match settingOf d qd.name with
      | some st => some ⟨qd.name, qd.tag, st.value, st.value⟩
      | none => some ⟨qd.name, qd.tag, Elo R d e est0.quantity y, Ehi R d e est0.quantity y⟩ := by
  have he := estimatesOf_perturb hest qd.name y
  have hne : (famOn d e qd.name).map (· y) ≠ [] := by
    rw [hq]; intro h; exact famOn_ne hest (List.map_eq_nil_iff.mp h)
  have hset : settingOf (perturb d e y) qd.name = settingOf d qd.name := rfl
  unfold boxEntry
  rw [hset]
  cases hs : settingOf d qd.name with
  | some st => rfl
  | none =>
    simp only
    rw [he]
    cases hl : (famOn d e qd.name).map (· y) with
    | nil => exact absurd hl hne
    | cons z zs =>
      simp only [Elo, Ehi, ← hq, hl]

/-- The facts about one step of the moved endpoint, at the level of boxes. -/
structure BoxStep (b₁ b₂ b₀ : Box) (q : String) : Prop where
  other : ∀ p, p ≠ q → b₁.find p = b₀.find p ∧ b₂.find p = b₀.find p
  mem : ∀ p, b₁.mem p = b₂.mem p
  point : ∀ p, b₁.isPoint p = b₂.isPoint p
  wf : boxWFB b₁ = boxWFB b₂

def wfView (en : BoxEntry) : String × Bool := (en.name, decide (en.lo ≤ en.hi))

theorem boxWFB_view (b : Box) :
    boxWFB b = (decide (((b.entries.map wfView).map Prod.fst).Nodup) && (b.entries.map wfView).all Prod.snd) := by
  simp [boxWFB, wfView, List.map_map, Function.comp_def]

theorem E_GS (hest : estimateOf d e.estimate = some est0) {x : Int} (hg : Gap x (endsOf d est0.quantity)) :
    GS x (endsOf d est0.quantity) (Elo R d e est0.quantity) ∧ GS x (endsOf d est0.quantity) (Ehi R d e est0.quantity) :=
  combine_GS hg R.risk.combination (famOn d e est0.quantity) (famOn_ne hest)
    (fun f hf => (fam_seq hest (List.mem_filter.mp hf).1).1)
    (fun f hf => (famOn_bounds hest hf).1) (fun f hf => (famOn_bounds hest hf).2.1)

theorem E_const (hest : estimateOf d e.estimate = some est0) (y y' : Int) :
    (e.side = .hi → Elo R d e est0.quantity y = Elo R d e est0.quantity y') ∧
    (e.side = .lo → Ehi R d e est0.quantity y = Ehi R d e est0.quantity y') := by
  have hc := combine_const R.risk.combination (famOn d e est0.quantity) y y'
    (fun f hf => (fam_seq hest (List.mem_filter.mp hf).1).1)
  exact ⟨fun hs => hc.1 (fun f hf => (famOn_bounds (x := 0) hest hf).2.2.1 hs y y'),
    fun hs => hc.2 (fun f hf => (famOn_bounds (x := 0) hest hf).2.2.2 hs y y')⟩

/-- The box lookup of the moved quantity: fixed, or the effective range. -/
theorem find_moved (hest : estimateOf d e.estimate = some est0) :
    (∃ F0, ∀ y, (box R (perturb d e y)).find est0.quantity = F0) ∨
    ∃ tag, ∀ y, (box R (perturb d e y)).find est0.quantity =
      some ⟨est0.quantity, tag, Elo R d e est0.quantity y, Ehi R d e est0.quantity y⟩ := by
  cases hf : d.quantities.find? (·.name == est0.quantity) with
  | none =>
    left
    exact ⟨none, fun y => by rw [find_box]; exact (by rw [show (perturb d e y).quantities = d.quantities from rfl, hf]; rfl)⟩
  | some qd =>
    have hq : qd.name = est0.quantity := by simpa using List.find?_some hf
    cases hs : settingOf d qd.name with
    | some st =>
      left
      refine ⟨some ⟨qd.name, qd.tag, st.value, st.value⟩, fun y => ?_⟩
      rw [find_box, show (perturb d e y).quantities = d.quantities from rfl, hf, Option.bind_some,
        boxEntry_moved hest hq y, hs]
    | none =>
      right
      refine ⟨qd.tag, fun y => ?_⟩
      rw [find_box, show (perturb d e y).quantities = d.quantities from rfl, hf, Option.bind_some,
        boxEntry_moved hest hq y, hs, hq]

theorem find_other (hest : estimateOf d e.estimate = some est0) {p : String} (hp : p ≠ est0.quantity) (y : Int) :
    (box R (perturb d e y)).find p = (box R d).find p := by
  rw [find_box, find_box, show (perturb d e y).quantities = d.quantities from rfl]
  cases hf : d.quantities.find? (·.name == p) with
  | none => rfl
  | some qd =>
    have hq : qd.name = p := by simpa using List.find?_some hf
    simp only [Option.bind_some]
    exact boxEntry_other hest (hq ▸ hp) y

theorem boxStep (hest : estimateOf d e.estimate = some est0) {x : Int} (hg : Gap x (endsOf d est0.quantity)) :
    BoxStep (box R (perturb d e x)) (box R (perturb d e (x + 1))) (box R d) est0.quantity := by
  have hE := E_GS (R := R) hest hg
  refine ⟨fun p hp => ⟨find_other hest hp x, find_other hest hp (x + 1)⟩, fun p => ?_, fun p => ?_, ?_⟩
  · by_cases hp : p = est0.quantity
    · subst hp
      rcases find_moved (R := R) hest with ⟨F0, hF⟩ | ⟨tag, hF⟩ <;> simp [Box.mem, hF]
    · simp [Box.mem, find_other hest hp]
  · by_cases hp : p = est0.quantity
    · subst hp
      rcases find_moved (R := R) hest with ⟨F0, hF⟩ | ⟨tag, hF⟩
      · simp [Box.isPoint, hF]
      · simp only [Box.isPoint, hF]
        rw [Bool.eq_iff_iff, beq_iff_eq, beq_iff_eq]
        exact GS.eq hg hE.1 hE.2
    · simp [Box.isPoint, find_other hest hp]
  · rw [boxWFB_view, boxWFB_view]
    have : (box R (perturb d e x)).entries.map wfView = (box R (perturb d e (x + 1))).entries.map wfView := by
      simp only [box, List.map_filterMap]
      show d.quantities.filterMap _ = d.quantities.filterMap _
      apply filterMap_congrOf
      intro qd _
      by_cases hq : qd.name = est0.quantity
      · rw [boxEntry_moved hest hq, boxEntry_moved hest hq]
        cases settingOf d qd.name with
        | some st => rfl
        | none =>
          simp only [Option.map_some, wfView]
          rw [GS.decide_le hg hE.1 hE.2]
      · rw [boxEntry_other hest hq, boxEntry_other hest hq]
    rw [this]

end BoxStep

/-! ## Atoms at `x` and at `x + 1` -/

def termMin (b : Box) (p : String × Int) : Int := if 0 ≤ p.2 then p.2 * b.lo p.1 else p.2 * b.hi p.1
def termMax (b : Box) (p : String × Int) : Int := if 0 ≤ p.2 then p.2 * b.hi p.1 else p.2 * b.lo p.1

theorem minSum_split (b : Box) {q : String} {c : Int} :
    ∀ {l : List (String × Int)}, (l.map (·.1)).Nodup → (q, c) ∈ l →
      minSum b l = termMin b (q, c) + minSum b (l.filter (·.1 != q))
  | [], _, h => by cases h
  | p :: l, hn, h => by
    simp only [List.map_cons, List.nodup_cons] at hn
    rw [minSum_cons]
    rcases List.mem_cons.mp h with rfl | h
    · have : l.filter (·.1 != q) = l := by
        apply List.filter_eq_self.mpr
        intro a ha
        have : a.1 ≠ q := fun he => hn.1 (he ▸ List.mem_map.mpr ⟨a, ha, rfl⟩)
        simpa using this
      simp [List.filter_cons, this, termMin]
    · have hne : p.1 ≠ q := fun he => hn.1 (he ▸ List.mem_map.mpr ⟨(q, c), h, rfl⟩)
      have : (p.1 != q) = true := by simpa using hne
      rw [List.filter_cons, if_pos this, minSum_cons, minSum_split b hn.2 h]
      omega

theorem maxSum_split (b : Box) {q : String} {c : Int} :
    ∀ {l : List (String × Int)}, (l.map (·.1)).Nodup → (q, c) ∈ l →
      maxSum b l = termMax b (q, c) + maxSum b (l.filter (·.1 != q))
  | [], _, h => by cases h
  | p :: l, hn, h => by
    simp only [List.map_cons, List.nodup_cons] at hn
    rw [maxSum_cons]
    rcases List.mem_cons.mp h with rfl | h
    · have : l.filter (·.1 != q) = l := by
        apply List.filter_eq_self.mpr
        intro a ha
        have : a.1 ≠ q := fun he => hn.1 (he ▸ List.mem_map.mpr ⟨a, ha, rfl⟩)
        simpa using this
      simp [List.filter_cons, this, termMax]
    · have hne : p.1 ≠ q := fun he => hn.1 (he ▸ List.mem_map.mpr ⟨(q, c), h, rfl⟩)
      have : (p.1 != q) = true := by simpa using hne
      rw [List.filter_cons, if_pos this, maxSum_cons, maxSum_split b hn.2 h]
      omega

theorem sums_congr {b₁ b₂ : Box} :
    ∀ (l : List (String × Int)), (∀ p ∈ l, b₁.lo p.1 = b₂.lo p.1 ∧ b₁.hi p.1 = b₂.hi p.1) →
      minSum b₁ l = minSum b₂ l ∧ maxSum b₁ l = maxSum b₂ l
  | [], _ => ⟨rfl, rfl⟩
  | p :: l, h => by
    have ih := sums_congr l (fun a ha => h a (List.mem_cons_of_mem _ ha))
    have hp := h p (List.mem_cons_self ..)
    rw [minSum_cons, minSum_cons, maxSum_cons, maxSum_cons, ih.1, ih.2, hp.1, hp.2]
    simp

theorem coeffOf_mem {f : LinForm} {q : String} {c : Int} (h : f.coeffOf q = some c) : (q, c) ∈ f.coeffs := by
  unfold LinForm.coeffOf at h
  cases hf : f.coeffs.find? (·.1 == q) with
  | none => rw [hf] at h; cases h
  | some p =>
    rw [hf] at h
    simp only [Option.map_some, Option.some.injEq] at h
    have := List.find?_some hf
    simp only [beq_iff_eq] at this
    have hm := List.mem_of_find?_eq_some hf
    rw [← this, ← h]
    exact hm

theorem coeffOf_none {f : LinForm} {q : String} (h : f.coeffOf q = none) : ∀ p ∈ f.coeffs, p.1 ≠ q := by
  unfold LinForm.coeffOf at h
  cases hf : f.coeffs.find? (·.1 == q) with
  | some _ => rw [hf] at h; cases h
  | none =>
    intro p hp he
    have := List.find?_eq_none.mp hf p hp
    simp [he] at this

theorem atomCandidates_some {b : Box} {q : String} {s : Side} {f : LinForm} {c : Int} (h : f.coeffOf q = some c) :
    atomCandidates b q s f =
      let K := if (s == .lo) == decide (0 ≤ c) then fmin b (f.without q) else fmax b (f.without q)
      [(floorCeil K c).1 - 1, (floorCeil K c).1, (floorCeil K c).2, (floorCeil K c).2 + 1] := by
  unfold atomCandidates
  rw [h]

section AtomStep
variable {R : RiskDoc} {d : Decision} {e : Endpoint} {est0 : Estimate}

theorem lookups_other (hest : estimateOf d e.estimate = some est0) {p : String} (hp : p ≠ est0.quantity) (y : Int) :
    (box R (perturb d e y)).lo p = (box R d).lo p ∧ (box R (perturb d e y)).hi p = (box R d).hi p := by
  simp only [Box.lo, Box.hi, find_other hest hp y]
  simp

theorem without_split (b : Box) {f : LinForm} (hf : f.Normal) {q : String} {c : Int} (h : (q, c) ∈ f.coeffs) :
    fmin b f = termMin b (q, c) + fmin b (f.without q) ∧ fmax b f = termMax b (q, c) + fmax b (f.without q) := by
  simp only [fmin, fmax, LinForm.without]
  rw [minSum_split b hf.1 h, maxSum_split b hf.1 h]
  constructor <;> omega

theorem without_other (hest : estimateOf d e.estimate = some est0) (f : LinForm) (y : Int) :
    fmin (box R (perturb d e y)) (f.without est0.quantity) = fmin (box R d) (f.without est0.quantity) ∧
    fmax (box R (perturb d e y)) (f.without est0.quantity) = fmax (box R d) (f.without est0.quantity) := by
  have := sums_congr (b₁ := box R (perturb d e y)) (b₂ := box R d) (f.without est0.quantity).coeffs (by
    intro p hp
    simp only [LinForm.without, List.mem_filter, bne_iff_ne, ne_eq] at hp
    exact lookups_other hest hp.2 y)
  simp only [fmin, fmax, this.1, this.2]
  simp

theorem atom_step (hest : estimateOf d e.estimate = some est0) {x : Int} (hg : Gap x (endsOf d est0.quantity))
    {f : LinForm} (hf : f.Normal)
    (hthr : x ∉ atomCandidates (box R d) est0.quantity e.side f ∨
      x + 1 ∉ atomCandidates (box R d) est0.quantity e.side f) :
    ExtremaAgree (box R (perturb d e x)) (box R (perturb d e (x + 1))) f := by
  cases hc : f.coeffOf est0.quantity with
  | none =>
    have hn := coeffOf_none hc
    have := sums_congr (b₁ := box R (perturb d e x)) (b₂ := box R (perturb d e (x + 1))) f.coeffs (by
      intro p hp
      rw [(lookups_other hest (hn p hp) x).1, (lookups_other hest (hn p hp) x).2,
        (lookups_other hest (hn p hp) (x + 1)).1, (lookups_other hest (hn p hp) (x + 1)).2]
      exact ⟨rfl, rfl⟩)
    simp only [ExtremaAgree, fmin, fmax, this.1, this.2]
    exact ⟨SignEq.refl _, SignEq.refl _⟩
  | some c =>
    have hmem := coeffOf_mem hc
    have hc0 : c ≠ 0 := hf.2 _ hmem
    obtain ⟨m1, M1⟩ := without_split (box R (perturb d e x)) hf hmem
    obtain ⟨m2, M2⟩ := without_split (box R (perturb d e (x + 1))) hf hmem
    obtain ⟨w1, W1⟩ := without_other (R := R) hest f x
    obtain ⟨w2, W2⟩ := without_other (R := R) hest f (x + 1)
    unfold ExtremaAgree
    rw [m1, m2, M1, M2, w1, w2, W1, W2]
    rw [atomCandidates_some (b := box R d) (s := e.side) hc] at hthr
    generalize fmin (box R d) (f.without est0.quantity) = Kmin at hthr ⊢
    generalize fmax (box R d) (f.without est0.quantity) = Kmax at hthr ⊢
    rcases find_moved (R := R) hest with ⟨F0, hF⟩ | ⟨tag, hF⟩
    · have hl : (box R (perturb d e x)).lo est0.quantity = (box R (perturb d e (x + 1))).lo est0.quantity := by
        simp only [Box.lo, hF]
      have hh : (box R (perturb d e x)).hi est0.quantity = (box R (perturb d e (x + 1))).hi est0.quantity := by
        simp only [Box.hi, hF]
      simp only [termMin, termMax, hl, hh]
      exact ⟨SignEq.refl _, SignEq.refl _⟩
    · have hl : ∀ y, (box R (perturb d e y)).lo est0.quantity = Elo R d e est0.quantity y := by
        intro y; simp [Box.lo, hF]
      have hh : ∀ y, (box R (perturb d e y)).hi est0.quantity = Ehi R d e est0.quantity y := by
        intro y; simp [Box.hi, hF]
      simp only [termMin, termMax, hl, hh]
      obtain ⟨gLo, gHi⟩ := E_GS (R := R) hest hg
      have kc := E_const (R := R) hest x (x + 1)
      cases hs : e.side with
      | lo =>
        rw [hs] at hthr
        have eh := kc.2 hs
        by_cases hpos : 0 ≤ c
        · simp only [hpos, if_true, eh]
          refine ⟨?_, SignEq.refl _⟩
          rcases gLo with ⟨h1, h2⟩ | ⟨h1, _⟩
          · rw [h1, h2]
            exact sign_step c _ x hc0 (by simpa [hpos] using hthr)
          · rw [h1]; exact SignEq.refl _
        · simp only [hpos, if_false, eh]
          refine ⟨SignEq.refl _, ?_⟩
          rcases gLo with ⟨h1, h2⟩ | ⟨h1, _⟩
          · rw [h1, h2]
            exact sign_step c _ x hc0 (by simpa [hpos] using hthr)
          · rw [h1]; exact SignEq.refl _
      | hi =>
        rw [hs] at hthr
        have el := kc.1 hs
        by_cases hpos : 0 ≤ c
        · simp only [hpos, if_true, el]
          refine ⟨SignEq.refl _, ?_⟩
          rcases gHi with ⟨h1, h2⟩ | ⟨h1, _⟩
          · rw [h1, h2]
            exact sign_step c _ x hc0 (by simpa [hpos] using hthr)
          · rw [h1]; exact SignEq.refl _
        · simp only [hpos, if_false, el]
          refine ⟨?_, SignEq.refl _⟩
          rcases gHi with ⟨h1, h2⟩ | ⟨h1, _⟩
          · rw [h1, h2]
            exact sign_step c _ x hc0 (by simpa [hpos] using hthr)
          · rw [h1]; exact SignEq.refl _

end AtomStep

/-! ## The observations, the view and the outcome -/

section Assembly
variable {R : RiskDoc} {d : Decision} {e : Endpoint} {est0 : Estimate}

theorem recordAtoms_normal {f : LinForm} (hf : f ∈ recordAtoms d) : f.Normal := by
  simp only [recordAtoms, List.mem_flatMap, List.mem_map] at hf
  obtain ⟨_, _, fr, _, rfl⟩ := hf
  exact fr.1.property

theorem sources_atoms {C : Cond} (hC : C ∈ d.conditions.map (·.cond) ∨ C = .top ∨ C = .bottom) :
    ∀ fr ∈ atomsOf C, fr.1.val ∈ recordAtoms d := by
  intro fr hfr
  rcases hC with hC | rfl | rfl
  · obtain ⟨c, hc, rfl⟩ := List.mem_map.mp hC
    exact List.mem_flatMap.mpr ⟨c, hc, List.mem_map.mpr ⟨fr, hfr, rfl⟩⟩
  · cases hfr
  · cases hfr

theorem suff_atoms (a h : String) : ∀ fr ∈ atomsOf (Suff R d a h), fr.1.val ∈ recordAtoms d := by
  apply sources_atoms
  unfold Suff
  cases hs : suffSources d a h with
  | nil => exact Or.inr (Or.inr rfl)
  | cons C cs =>
    have hm : C ∈ suffSources d a h := by rw [hs]; exact List.mem_cons_self ..
    simp only [List.headD_cons]
    simp only [suffSources, List.mem_append, List.mem_filterMap] at hm
    rcases hm with ⟨c, hc, hc'⟩ | ⟨st, _, hst⟩
    · split at hc'
      · cases hc'
      · cases hc'
        exact Or.inl (List.mem_map.mpr ⟨c, (List.mem_filter.mp hc).1, rfl⟩)
    · split at hst
      · cases hst; exact Or.inr (Or.inl rfl)
      · cases hst

theorem nec_atoms (a h : String) : ∀ fr ∈ atomsOf (Nec R d a h), fr.1.val ∈ recordAtoms d := by
  apply sources_atoms
  unfold Nec
  cases hs : necSources d a h with
  | nil =>
    simp only
    split
    · exact Or.inr (Or.inl rfl)
    · unfold completion
      split
      · exact Or.inr (Or.inl rfl)
      · split
        · exact Or.inr (Or.inl rfl)
        · exact Or.inr (Or.inr rfl)
  | cons C cs =>
    have hm : C ∈ necSources d a h := by rw [hs]; exact List.mem_cons_self ..
    simp only
    simp only [necSources, List.mem_append, List.mem_filterMap] at hm
    rcases hm with ⟨c, hc, hc'⟩ | ⟨st, _, hst⟩
    · split at hc'
      · cases hc'
      · cases hc'
        exact Or.inl (List.mem_map.mpr ⟨c, (List.mem_filter.mp hc).1, rfl⟩)
    · split at hst
      · cases hst; exact Or.inr (Or.inr rfl)
      · cases hst

/-- The hypotheses of one step, from the candidates. -/
theorem step_hyps (hest : estimateOf d e.estimate = some est0) {x : Int}
    (hx : x ∉ candidates R d e ∨ x + 1 ∉ candidates R d e) :
    Gap x (endsOf d est0.quantity) ∧
    ∀ f ∈ recordAtoms d, x ∉ atomCandidates (box R d) est0.quantity e.side f ∨
      x + 1 ∉ atomCandidates (box R d) est0.quantity e.side f := by
  have hc : ∀ z, z ∈ candidates R d e ↔ z = current d e ∨
      z ∈ (endsOf d est0.quantity).flatMap (fun w => [w - 1, w, w + 1]) ∨
      z ∈ (recordAtoms d).flatMap (atomCandidates (box R d) est0.quantity e.side) := by
    intro z
    simp only [candidates, hest]
    show z ∈ dedup (current d e :: (endsOf d est0.quantity).flatMap (fun w => [w - 1, w, w + 1]) ++
      (recordAtoms d).flatMap (atomCandidates (box R d) est0.quantity e.side)) ↔ _
    rw [mem_dedup]
    simp only [List.mem_append, List.mem_cons, or_assoc]
  refine ⟨fun w hw => ?_, fun f hf => ?_⟩
  · have h3 : ∀ z, z = w - 1 ∨ z = w ∨ z = w + 1 → z ∈ candidates R d e := by
      intro z hz
      apply (hc z).mpr
      right; left
      apply List.mem_flatMap.mpr
      refine ⟨w, hw, ?_⟩
      rcases hz with rfl | rfl | rfl <;> simp
    rcases hx with hx | hx
    · constructor
      · intro he; exact hx (h3 x (Or.inr (Or.inl he)))
      · intro he; exact hx (h3 x (Or.inl (by omega)))
    · constructor
      · intro he; exact hx (h3 (x + 1) (Or.inr (Or.inr (by omega))))
      · intro he; exact hx (h3 (x + 1) (Or.inr (Or.inl he)))
  · have hsub : ∀ z ∈ atomCandidates (box R d) est0.quantity e.side f, z ∈ candidates R d e := fun z hz =>
      (hc z).mpr (Or.inr (Or.inr (List.mem_flatMap.mpr ⟨f, hf, hz⟩)))
    rcases hx with hx | hx
    · exact Or.inl (fun h => hx (hsub x h))
    · exact Or.inr (fun h => hx (hsub (x + 1) h))

theorem boxAgree_step (hest : estimateOf d e.estimate = some est0) {x : Int}
    (hx : x ∉ candidates R d e ∨ x + 1 ∉ candidates R d e) {C : Cond}
    (hC : ∀ fr ∈ atomsOf C, fr.1.val ∈ recordAtoms d) :
    BoxAgree (box R (perturb d e x)) (box R (perturb d e (x + 1))) C := by
  obtain ⟨hg, hthr⟩ := step_hyps hest hx
  have hs := boxStep (R := R) hest hg
  exact ⟨hs.mem, hs.point, fun fr hfr => atom_step hest hg (recordAtoms_normal (hC fr hfr)) (hthr _ (hC fr hfr))⟩

theorem intersects_step (hest : estimateOf d e.estimate = some est0) {x : Int} (hg : Gap x (endsOf d est0.quantity))
    (p : String) :
    intersects (estimatesOf (perturb d e x) p) = intersects (estimatesOf (perturb d e (x + 1)) p) := by
  by_cases hp : p = est0.quantity
  · subst hp
    rw [estimatesOf_perturb hest, estimatesOf_perturb hest]
    cases hF : famOn d e est0.quantity with
    | nil => exact absurd hF (famOn_ne hest)
    | cons f0 fs =>
      have hmem : ∀ f ∈ f0 :: fs, f ∈ famOn d e est0.quantity := fun f hf => by rw [hF]; exact hf
      have hlo : ∀ f ∈ f0 :: fs, GS x (endsOf d est0.quantity) (fun y => (f y).lo) :=
        fun f hf => (famOn_bounds hest (hmem f hf)).1
      have hhi : ∀ f ∈ f0 :: fs, GS x (endsOf d est0.quantity) (fun y => (f y).hi) :=
        fun f hf => (famOn_bounds hest (hmem f hf)).2.1
      have g1 := GS.foldl_field hg max (fun f g hf hg' => GS.max hg hf hg') (·.lo) (f0 :: fs) _
        (hlo f0 (List.mem_cons_self ..)) hlo
      have g2 := GS.foldl_field hg min (fun f g hf hg' => GS.min hg hf hg') (·.hi) (f0 :: fs) _
        (hhi f0 (List.mem_cons_self ..)) hhi
      have k : ∀ y, intersects ((f0 :: fs).map (· y)) =
          decide (((f0 :: fs).map (· y)).foldl (fun m e => max m e.lo) (f0 y).lo ≤
            ((f0 :: fs).map (· y)).foldl (fun m e => min m e.hi) (f0 y).hi) := by
        intro y
        simp only [intersects, List.foldl_map]
        rfl
      rw [k, k]
      exact GS.decide_le hg g1 g2
  · rw [estimatesOf_other hest hp x (x + 1)]

theorem obs_step (hest : estimateOf d e.estimate = some est0) {x : Int}
    (hx : x ∉ candidates R d e ∨ x + 1 ∉ candidates R d e) :
    obs R (perturb d e x) = obs R (perturb d e (x + 1)) := by
  obtain ⟨hg, _⟩ := step_hyps hest hx
  have hs := boxStep (R := R) hest hg
  simp only [obs]
  congr 1
  · -- the range checks
    rw [perturb_estimates, perturb_estimates, List.map_map, List.map_map]
    apply List.map_congr_left
    intro f hf
    rcases fam_cases hest hf with ⟨est, _, rfl⟩ | rfl
    · rfl
    · have hw := mem_endsOf (est0_mem hest)
      simp only [Function.comp]
      cases e.side with
      | lo => exact GS.decide_le hg GS.id (GS.const hw.2)
      | hi => exact GS.decide_le hg (GS.const hw.1) GS.id
  · -- the intersections
    apply List.map_congr_left
    intro qd _
    exact intersects_step hest hg qd.name
  · exact hs.wf
  · -- the conditions
    apply List.map_congr_left
    intro c hc
    have hC : ∀ fr ∈ atomsOf c.cond, fr.1.val ∈ recordAtoms d := sources_atoms (Or.inl (List.mem_map.mpr ⟨c, hc, rfl⟩))
    have hA := boxAgree_step (R := R) hest hx hC
    rw [scoped_congr hA, sharedName_congr hA.point, unitBad_congr hA.point]
  · -- the cells
    apply List.map_congr_left
    intro p _
    obtain ⟨a, h⟩ := p
    have hS := boxAgree_step (R := R) hest hx (suff_atoms (R := R) a h)
    have hN := boxAgree_step (R := R) hest hx (nec_atoms (R := R) a h)
    have hSN := boxAgree_step (R := R) (d := d) hest hx (C := Cond.and (Suff R d a h) (.not (Nec R d a h)))
      (fun fr hfr => by
        simp only [atomsOf, List.mem_append] at hfr
        rcases hfr with hfr | hfr
        · exact suff_atoms a h fr hfr
        · exact nec_atoms a h fr hfr)
    have e1 : ∀ y, Suff R (perturb d e y) a h = Suff R d a h := fun _ => rfl
    have e2 : ∀ y, Nec R (perturb d e y) a h = Nec R d a h := fun _ => rfl
    simp only [cellObs, e1, e2]
    rw [condOK_congr hS, condOK_congr hN, scoped_congr hSN, sharedName_congr hSN.point, possibleE_congr hSN,
      possibleE_congr hN, certainE_congr hS]

end Assembly

/-- 4.9: outcomes change only between consecutive candidates. -/
theorem status_piecewise_constant (R : RiskDoc) (h : WellFormedRisk R = true) (d : Decision) (e : Endpoint)
    (he : e ∈ endpoints d) (x : Int) (hx : x ∉ candidates R d e ∨ x + 1 ∉ candidates R d e) :
    outcomeAt R d e x = outcomeAt R d e (x + 1) := by
  have _ := h
  obtain ⟨est0, hest⟩ := mem_estimates_of_endpoint he
  unfold outcomeAt
  have : view R (perturb d e x) = view R (perturb d e (x + 1)) := by
    simp only [view, strip_perturb, obs_step (R := R) hest hx]
  rw [this]

/-! ## The certified scans (4.9) -/

theorem pw_of {R : RiskDoc} (h : WellFormedRisk R = true) {d : Decision} {e : Endpoint} (he : e ∈ endpoints d) :
    ∀ x, x ∉ candidates R d e ∨ x + 1 ∉ candidates R d e → outcomeAt R d e x = outcomeAt R d e (x + 1) :=
  status_piecewise_constant R h d e he

theorem changedAt_true {a : String} {s : Status} {o : Outcome} (h : changedAt a (some s) o = true) :
    ∃ ss', o = .statuses ss' ∧ ss'.lookup a ≠ some s := by
  cases o with
  | statuses ss' => exact ⟨ss', rfl, by simpa [changedAt] using h⟩
  | invalid _ | conflict => cases h

theorem changedAt_false {a : String} {s : Status} {o : Outcome} (h : changedAt a (some s) o = false) :
    StatusKept o a s := by
  cases o with
  | statuses ss' => exact Or.inr (Or.inr ⟨ss', rfl, by simpa [changedAt] using h⟩)
  | invalid t => exact Or.inr (Or.inl ⟨t, rfl⟩)
  | conflict => exact Or.inl rfl

/-- 4.9: the certified check. `scan` returns the nearest valid status change, or none; everything strictly between
(or beyond, for none) keeps the current status or is invalid or a conflict. -/
theorem scan_sound (R : RiskDoc) (h : WellFormedRisk R = true) (d : Decision) (e : Endpoint)
    (he : e ∈ endpoints d) (dir : Dir) (a : String) (ss : List (String × Status)) (s : Status)
    (hcur : outcomeAt R d e (current d e) = .statuses ss) (hs : ss.lookup a = some s) :
    (∀ x, scan R d e dir a = some x →
        Beyond dir (current d e) x ∧
        (∃ ss', outcomeAt R d e x = .statuses ss' ∧ ss'.lookup a ≠ some s) ∧
        ∀ y, Beyond dir (current d e) y → Beyond dir y x → StatusKept (outcomeAt R d e y) a s) ∧
    (scan R d e dir a = none → ∀ y, Beyond dir (current d e) y → StatusKept (outcomeAt R d e y) a s) := by
  have hcs : curStatus R d e a = some s := by simp [curStatus, hcur, hs]
  obtain ⟨hn1, hn2⟩ := neighbours_mem (R := R) he
  obtain ⟨h1, h2⟩ := scanWith_sound (dir := dir) (P := changedAt a (curStatus R d e a)) hn1 hn2 (pw_of h he)
  rw [hcs] at h1 h2
  refine ⟨fun x hx => ?_, fun hx y hy => changedAt_false (h2 (by unfold scan at hx; rw [hcs] at hx; exact hx) y hy)⟩
  obtain ⟨hb, hp, hall⟩ := h1 x (by unfold scan at hx; rw [hcs] at hx; exact hx)
  exact ⟨hb, changedAt_true hp, fun y hy hyx => changedAt_false (hall y hy hyx)⟩

theorem isInvalid_false {o : Outcome} (h : isInvalid o = false) : ∀ t', o ≠ .invalid t' := by
  intro t' he; subst he; cases h

theorem isConflict_false {o : Outcome} (h : isConflict o = false) : o ≠ .conflict := by
  intro he; subst he; cases h

/-- 4.9: the record-level lines, one scan per kind. Each certifies only its own kind: a value of the other kind may
lie strictly between (fixtures k38 and k40). -/
theorem scanInvalid_sound (R : RiskDoc) (h : WellFormedRisk R = true) (d : Decision) (e : Endpoint)
    (he : e ∈ endpoints d) (dir : Dir) :
    (∀ x t, scanInvalid R d e dir = some (x, t) →
        Beyond dir (current d e) x ∧ outcomeAt R d e x = .invalid t ∧
        ∀ y, Beyond dir (current d e) y → Beyond dir y x → ∀ t', outcomeAt R d e y ≠ .invalid t') ∧
    (scanInvalid R d e dir = none → ∀ y, Beyond dir (current d e) y → ∀ t', outcomeAt R d e y ≠ .invalid t') := by
  obtain ⟨hn1, hn2⟩ := neighbours_mem (R := R) he
  obtain ⟨h1, h2⟩ := scanWith_sound (dir := dir) (P := isInvalid) hn1 hn2 (pw_of h he)
  refine ⟨fun x t hx => ?_, fun hx y hy => ?_⟩
  · unfold scanInvalid at hx
    cases hw : scanWith R d e dir isInvalid with
    | none => rw [hw] at hx; cases hx
    | some x' =>
      rw [hw] at hx
      simp only [Option.bind_some] at hx
      obtain ⟨hb, hp, hall⟩ := h1 x' hw
      split at hx
      · rename_i t'' ho
        cases hx
        exact ⟨hb, ho, fun y hy hyx => isInvalid_false (hall y hy hyx)⟩
      · cases hx
  · unfold scanInvalid at hx
    cases hw : scanWith R d e dir isInvalid with
    | none => exact isInvalid_false (h2 hw y hy)
    | some x' =>
      rw [hw] at hx
      simp only [Option.bind_some] at hx
      obtain ⟨_, hp, _⟩ := h1 x' hw
      split at hx
      · cases hx
      · rename_i hno
        cases ho : outcomeAt R d e x' with
        | invalid t'' => exact absurd ho (hno t'')
        | conflict | statuses _ => rw [ho] at hp; cases hp

theorem scanConflict_sound (R : RiskDoc) (h : WellFormedRisk R = true) (d : Decision) (e : Endpoint)
    (he : e ∈ endpoints d) (dir : Dir) :
    (∀ x, scanConflict R d e dir = some x →
        Beyond dir (current d e) x ∧ outcomeAt R d e x = .conflict ∧
        ∀ y, Beyond dir (current d e) y → Beyond dir y x → outcomeAt R d e y ≠ .conflict) ∧
    (scanConflict R d e dir = none → ∀ y, Beyond dir (current d e) y → outcomeAt R d e y ≠ .conflict) := by
  obtain ⟨hn1, hn2⟩ := neighbours_mem (R := R) he
  obtain ⟨h1, h2⟩ := scanWith_sound (dir := dir) (P := isConflict) hn1 hn2 (pw_of h he)
  refine ⟨fun x hx => ?_, fun hx y hy => isConflict_false (h2 hx y hy)⟩
  obtain ⟨hb, hp, hall⟩ := h1 x hx
  refine ⟨hb, ?_, fun y hy hyx => isConflict_false (hall y hy hyx)⟩
  cases ho : outcomeAt R d e x with
  | conflict => rfl
  | invalid _ | statuses _ => rw [ho] at hp; cases hp

end VE.Risk
