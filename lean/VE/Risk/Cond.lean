import Std

/-! Conditions of `risk@0` records (docs/spec/risk.md 3.2, 4.2 and 7.1).

A comparison is held in normal form `f ⋈ 0` with `f = Σ cᵢ·qᵢ + k` and
`⋈ ∈ {<, ≤, =, ≠}`. Normality (distinct quantity names, no zero coefficient)
is a typed invariant: an atom holds a `NormLinForm`, built only by
`LinForm.normalize`, which collects coefficients per name in first-occurrence
order and drops zeros (`normalize_normal`, `normalize_eval`).

`nnf` pushes negations to the atoms (`¬(f < 0)` is `−f ≤ 0`, `¬(f ≤ 0)` is
`−f < 0`, `¬(f = 0)` is `f ≠ 0`, `¬(f ≠ 0)` is `f = 0`), so `≠` stays one
atom. A box gives every quantity an inclusive integer range; `Scoped`,
`Separable` and `UnitCoefficients` are the decidable side conditions of the
endpoint theorems (`Derive.lean`). -/
namespace VE.Risk

/-! ## Linear forms -/

inductive Rel | lt | le | eq | ne
  deriving DecidableEq, Repr, BEq

structure LinForm where
  coeffs : List (String × Int)
  const : Int
  deriving DecidableEq, Repr, BEq

abbrev Valuation := String → Int

def LinForm.eval (f : LinForm) (v : Valuation) : Int :=
  (f.coeffs.map (fun (q, c) => c * v q)).sum + f.const

/-- 4.2: names distinct, no zero coefficient. -/
def LinForm.Normal (f : LinForm) : Prop :=
  (f.coeffs.map (·.1)).Nodup ∧ ∀ p ∈ f.coeffs, p.2 ≠ 0

/-- Add `c` to the coefficient of `q`, appending `q` if it is new. -/
def addCoeff : List (String × Int) → String × Int → List (String × Int)
  | [], p => [p]
  | (q', c') :: rest, (q, c) => if q' = q then (q', c' + c) :: rest else (q', c') :: addCoeff rest (q, c)

def collect (l : List (String × Int)) : List (String × Int) := l.foldl addCoeff []

/-- 4.2: collect coefficients per name in first-occurrence order and drop zeros. -/
def LinForm.normalize (f : LinForm) : LinForm :=
  ⟨(collect f.coeffs).filter (fun p => p.2 != 0), f.const⟩

def termSum (l : List (String × Int)) (v : Valuation) : Int := (l.map (fun (q, c) => c * v q)).sum

theorem termSum_cons (p : String × Int) (l : List (String × Int)) (v : Valuation) :
    termSum (p :: l) v = p.2 * v p.1 + termSum l v := by
  simp [termSum]

theorem termSum_nil (v : Valuation) : termSum [] v = 0 := rfl

theorem termSum_append (l m : List (String × Int)) (v : Valuation) :
    termSum (l ++ m) v = termSum l v + termSum m v := by
  induction l with
  | nil => simp [termSum]
  | cons p l ih => simp only [List.cons_append, termSum_cons, ih]; omega

theorem eval_eq_termSum (f : LinForm) (v : Valuation) : f.eval v = termSum f.coeffs v + f.const := rfl

theorem termSum_addCoeff (l : List (String × Int)) (p : String × Int) (v : Valuation) :
    termSum (addCoeff l p) v = termSum l v + p.2 * v p.1 := by
  induction l with
  | nil => simp [addCoeff, termSum]
  | cons x rest ih =>
    obtain ⟨q', c'⟩ := x
    obtain ⟨q, c⟩ := p
    simp only [addCoeff]
    split
    · rename_i h
      subst h
      simp only [termSum_cons]
      rw [Int.add_mul]
      omega
    · simp only [termSum_cons, ih]
      omega

theorem termSum_foldl (l acc : List (String × Int)) (v : Valuation) :
    termSum (l.foldl addCoeff acc) v = termSum acc v + termSum l v := by
  induction l generalizing acc with
  | nil => simp [termSum]
  | cons p l ih =>
    simp only [List.foldl_cons, ih, termSum_addCoeff, termSum_cons]
    omega

theorem termSum_filter_nonzero (l : List (String × Int)) (v : Valuation) :
    termSum (l.filter (fun p => p.2 != 0)) v = termSum l v := by
  induction l with
  | nil => rfl
  | cons p l ih =>
    by_cases hp : p.2 = 0
    · simp only [List.filter_cons, hp, bne_self_eq_false, Bool.false_eq_true, if_false, ih, termSum_cons]
      simp
    · have : (p.2 != 0) = true := by simpa using hp
      simp only [List.filter_cons, this, if_true, termSum_cons, ih]

theorem mem_names_addCoeff (l : List (String × Int)) (p : String × Int) (q : String) :
    q ∈ (addCoeff l p).map (·.1) ↔ q ∈ l.map (·.1) ∨ q = p.1 := by
  induction l with
  | nil => simp [addCoeff]
  | cons x rest ih =>
    obtain ⟨q', c'⟩ := x
    obtain ⟨q0, c⟩ := p
    simp only [addCoeff]
    split
    · rename_i h
      subst h
      simp only [List.map_cons, List.mem_cons]
      constructor
      · rintro (h | h)
        · exact Or.inl (Or.inl h)
        · exact Or.inl (Or.inr h)
      · rintro ((h | h) | h)
        · exact Or.inl h
        · exact Or.inr h
        · exact Or.inl h
    · simp only [List.map_cons, List.mem_cons, ih]
      constructor
      · rintro (h | h | h)
        · exact Or.inl (Or.inl h)
        · exact Or.inl (Or.inr h)
        · exact Or.inr h
      · rintro ((h | h) | h)
        · exact Or.inl h
        · exact Or.inr (Or.inl h)
        · exact Or.inr (Or.inr h)

theorem nodup_addCoeff (l : List (String × Int)) (p : String × Int) (h : (l.map (·.1)).Nodup) :
    ((addCoeff l p).map (·.1)).Nodup := by
  induction l with
  | nil => simp [addCoeff]
  | cons x rest ih =>
    obtain ⟨q', c'⟩ := x
    obtain ⟨q, c⟩ := p
    simp only [List.map_cons, List.nodup_cons] at h
    simp only [addCoeff]
    split
    · simpa using h
    · rename_i hne
      simp only [List.map_cons, List.nodup_cons]
      refine ⟨?_, ih h.2⟩
      rw [mem_names_addCoeff]
      rintro (h' | h')
      · exact h.1 h'
      · exact hne h'

theorem nodup_foldl (l acc : List (String × Int)) (h : (acc.map (·.1)).Nodup) :
    ((l.foldl addCoeff acc).map (·.1)).Nodup := by
  induction l generalizing acc with
  | nil => simpa using h
  | cons p l ih => exact ih _ (nodup_addCoeff acc p h)

theorem nodup_filter_names (l : List (String × Int)) (P : String × Int → Bool)
    (h : (l.map (·.1)).Nodup) : ((l.filter P).map (·.1)).Nodup := by
  induction l with
  | nil => simp
  | cons x l ih =>
    simp only [List.map_cons, List.nodup_cons] at h
    by_cases hx : P x = true
    · simp only [List.filter_cons, hx, if_true, List.map_cons, List.nodup_cons]
      refine ⟨fun hm => h.1 ?_, ih h.2⟩
      obtain ⟨y, hy, he⟩ := List.mem_map.mp hm
      exact List.mem_map.mpr ⟨y, (List.mem_filter.mp hy).1, he⟩
    · simp only [List.filter_cons, hx, Bool.false_eq_true, if_false]
      exact ih h.2

/-- 4.2: the normaliser's result is normal. -/
theorem normalize_normal (f : LinForm) : f.normalize.Normal := by
  refine ⟨nodup_filter_names _ _ (nodup_foldl _ [] (by simp)), fun p hp => ?_⟩
  have := (List.mem_filter.mp hp).2
  simpa using this

/-- 4.2: the normaliser keeps the value under every valuation. -/
theorem normalize_eval (f : LinForm) (v : Valuation) : f.normalize.eval v = f.eval v := by
  simp only [LinForm.normalize, eval_eq_termSum, termSum_filter_nonzero, collect, termSum_foldl]
  simp [termSum]

abbrev NormLinForm := {f : LinForm // f.Normal}

def NormLinForm.mk' (f : LinForm) : NormLinForm := ⟨f.normalize, normalize_normal f⟩

/-- Every coefficient and the constant negated (`nnf`); stays normal. -/
def LinForm.neg (f : LinForm) : LinForm := ⟨f.coeffs.map (fun (q, c) => (q, -c)), -f.const⟩

theorem neg_names (f : LinForm) : f.neg.coeffs.map (·.1) = f.coeffs.map (·.1) := by
  simp [LinForm.neg]

theorem neg_normal {f : LinForm} (h : f.Normal) : f.neg.Normal := by
  refine ⟨by rw [neg_names]; exact h.1, fun p hp => ?_⟩
  simp only [LinForm.neg, List.mem_map] at hp
  obtain ⟨⟨q, c⟩, hm, rfl⟩ := hp
  have := h.2 _ hm
  simpa using this

def NormLinForm.neg (f : NormLinForm) : NormLinForm := ⟨f.val.neg, neg_normal f.property⟩

theorem termSum_neg (l : List (String × Int)) (v : Valuation) :
    termSum (l.map (fun (q, c) => (q, -c))) v = - termSum l v := by
  induction l with
  | nil => rfl
  | cons p l ih =>
    simp only [List.map_cons, termSum_cons, ih, Int.neg_mul]
    omega

theorem neg_eval (f : LinForm) (v : Valuation) : f.neg.eval v = - f.eval v := by
  simp only [eval_eq_termSum, LinForm.neg, termSum_neg]
  omega

/-! ## Conditions -/

inductive Cond
  | top
  | bottom
  | atom (f : NormLinForm) (r : Rel)
  | and (a b : Cond)
  | or (a b : Cond)
  | not (a : Cond)
  deriving DecidableEq

def Rel.holds : Rel → Int → Prop
  | .lt, n => n < 0
  | .le, n => n ≤ 0
  | .eq, n => n = 0
  | .ne, n => n ≠ 0

def Rel.test : Rel → Int → Bool
  | .lt, n => decide (n < 0)
  | .le, n => decide (n ≤ 0)
  | .eq, n => decide (n = 0)
  | .ne, n => decide (n ≠ 0)

theorem Rel.test_iff (r : Rel) (n : Int) : r.test n = true ↔ r.holds n := by
  cases r <;> simp [Rel.test, Rel.holds]

def Cond.holds : Cond → Valuation → Prop
  | .top, _ => True
  | .bottom, _ => False
  | .atom f r, v => r.holds (f.val.eval v)
  | .and a b, v => a.holds v ∧ b.holds v
  | .or a b, v => a.holds v ∨ b.holds v
  | .not a, v => ¬ a.holds v

/-- The Boolean evaluation of a condition at one valuation. -/
def Cond.eval : Cond → Valuation → Bool
  | .top, _ => true
  | .bottom, _ => false
  | .atom f r, v => r.test (f.val.eval v)
  | .and a b, v => a.eval v && b.eval v
  | .or a b, v => a.eval v || b.eval v
  | .not a, v => !a.eval v

theorem Cond.eval_iff (c : Cond) (v : Valuation) : c.eval v = true ↔ c.holds v := by
  induction c with
  | top | bottom => simp [Cond.eval, Cond.holds]
  | atom f r => exact Rel.test_iff r _
  | and a b ia ib => simp [Cond.eval, Cond.holds, ia, ib]
  | or a b ia ib => simp [Cond.eval, Cond.holds, ia, ib]
  | not a ia =>
    simp only [Cond.eval, Cond.holds]
    cases h : a.eval v <;> simp_all

instance (c : Cond) (v : Valuation) : Decidable (c.holds v) :=
  decidable_of_iff _ (Cond.eval_iff c v)

/-- The negated atom of `nnf`. -/
def negAtom (f : NormLinForm) : Rel → Cond
  | .lt => .atom f.neg .le
  | .le => .atom f.neg .lt
  | .eq => .atom f .ne
  | .ne => .atom f .eq

/-- Negation normal form: `nnfAux true c` is `c`, `nnfAux false c` is `¬c`, with every negation at an atom. -/
def nnfAux : Bool → Cond → Cond
  | true, .top => .top
  | false, .top => .bottom
  | true, .bottom => .bottom
  | false, .bottom => .top
  | true, .atom f r => .atom f r
  | false, .atom f r => negAtom f r
  | true, .and a b => .and (nnfAux true a) (nnfAux true b)
  | false, .and a b => .or (nnfAux false a) (nnfAux false b)
  | true, .or a b => .or (nnfAux true a) (nnfAux true b)
  | false, .or a b => .and (nnfAux false a) (nnfAux false b)
  | p, .not a => nnfAux (!p) a

/-- 4.2. -/
def nnf (c : Cond) : Cond := nnfAux true c

theorem negAtom_holds (f : NormLinForm) (r : Rel) (v : Valuation) :
    (negAtom f r).holds v ↔ ¬ r.holds (f.val.eval v) := by
  cases r <;> simp [negAtom, Cond.holds, Rel.holds, NormLinForm.neg, neg_eval] <;> omega

theorem nnfAux_holds (c : Cond) (v : Valuation) :
    ∀ p : Bool, (nnfAux p c).holds v ↔ (if p then c.holds v else ¬ c.holds v) := by
  induction c with
  | top => intro p; cases p <;> simp [nnfAux, Cond.holds]
  | bottom => intro p; cases p <;> simp [nnfAux, Cond.holds]
  | atom f r => intro p; cases p <;> simp [nnfAux, Cond.holds, negAtom_holds]
  | and a b ia ib =>
    intro p; cases p
    · simp only [nnfAux, Cond.holds, ia, ib]; simp only [Bool.false_eq_true, if_false]
      constructor
      · rintro (h | h) ⟨ha, hb⟩
        · exact h ha
        · exact h hb
      · intro h
        by_cases ha : a.holds v
        · exact Or.inr fun hb => h ⟨ha, hb⟩
        · exact Or.inl ha
    · simp [nnfAux, Cond.holds, ia, ib]
  | or a b ia ib =>
    intro p; cases p
    · simp only [nnfAux, Cond.holds, ia, ib]; simp only [Bool.false_eq_true, if_false]
      constructor
      · rintro ⟨ha, hb⟩ (h | h)
        · exact ha h
        · exact hb h
      · intro h
        exact ⟨fun ha => h (Or.inl ha), fun hb => h (Or.inr hb)⟩
    · simp [nnfAux, Cond.holds, ia, ib]
  | not a ia =>
    intro p; cases p
    · simp only [nnfAux, Bool.not_false, ia, Cond.holds]; simp
    · simp only [nnfAux, Bool.not_true, ia, Cond.holds]; simp

/-- 4.2: `nnf` keeps the meaning. -/
theorem nnf_holds (c : Cond) (v : Valuation) : (nnf c).holds v ↔ c.holds v := by
  simpa using nnfAux_holds c v true

/-- A condition without `not` (the image of `nnf`). -/
def Cond.NotFree : Cond → Prop
  | .top | .bottom | .atom _ _ => True
  | .and a b | .or a b => a.NotFree ∧ b.NotFree
  | .not _ => False

theorem negAtom_notFree (f : NormLinForm) (r : Rel) : (negAtom f r).NotFree := by
  cases r <;> trivial

theorem nnfAux_notFree (c : Cond) : ∀ p, (nnfAux p c).NotFree := by
  induction c with
  | top | bottom => intro p; cases p <;> trivial
  | atom f r => intro p; cases p
                · exact negAtom_notFree f r
                · trivial
  | and a b ia ib | or a b ia ib => intro p; cases p <;> exact ⟨ia _, ib _⟩
  | not a ia => intro p; cases p <;> exact ia _

theorem nnf_notFree (c : Cond) : (nnf c).NotFree := nnfAux_notFree c true

/-! ## Quantities of a condition -/

def LinForm.names (f : LinForm) : List String := f.coeffs.map (·.1)

/-- The quantity names of every atom, atom by atom, left to right (one entry per atom occurrence). -/
def Cond.atomNames : Cond → List String
  | .top | .bottom => []
  | .atom f _ => f.val.names
  | .and a b | .or a b => a.atomNames ++ b.atomNames
  | .not a => a.atomNames

theorem negAtom_atomNames (f : NormLinForm) (r : Rel) : (negAtom f r).atomNames = f.val.names := by
  cases r <;> simp [negAtom, Cond.atomNames, NormLinForm.neg, LinForm.names, neg_names]

theorem nnfAux_atomNames (c : Cond) : ∀ p, (nnfAux p c).atomNames = c.atomNames := by
  induction c with
  | top | bottom => intro p; cases p <;> rfl
  | atom f r => intro p; cases p
                · exact negAtom_atomNames f r
                · rfl
  | and a b ia ib | or a b ia ib => intro p; cases p <;> simp [nnfAux, Cond.atomNames, ia, ib]
  | not a ia => intro p; simp [nnfAux, Cond.atomNames, ia]

theorem nnf_atomNames (c : Cond) : (nnf c).atomNames = c.atomNames := nnfAux_atomNames c true

/-! ## Boxes -/

structure BoxEntry where
  name : String
  tag : String
  lo : Int
  hi : Int
  deriving DecidableEq, Repr, BEq

structure Box where
  entries : List BoxEntry
  deriving DecidableEq, Repr

def Box.WF (b : Box) : Prop := (b.entries.map (·.name)).Nodup ∧ ∀ q ∈ b.entries, q.lo ≤ q.hi

def InBox (b : Box) (v : Valuation) : Prop := ∀ q ∈ b.entries, q.lo ≤ v q.name ∧ v q.name ≤ q.hi

def Box.find (b : Box) (q : String) : Option BoxEntry := b.entries.find? (·.name == q)

def Box.lo (b : Box) (q : String) : Int := ((b.find q).map (·.lo)).getD 0
def Box.hi (b : Box) (q : String) : Int := ((b.find q).map (·.hi)).getD 0

/-- An entry is a point when `lo = hi`; settings are points. A name with no entry is not a point. -/
def Box.isPoint (b : Box) (q : String) : Bool :=
  match b.find q with
  | some e => e.lo == e.hi
  | none => false

def Box.mem (b : Box) (q : String) : Bool := (b.find q).isSome

/-- 4.2: every quantity of `c` is an entry of `b`. -/
def Scoped (b : Box) (c : Cond) : Bool := c.atomNames.all b.mem

/-- The separability test on one condition: no non-point entry occurs in two atoms. -/
def sepOK (b : Box) (c : Cond) : Bool :=
  c.atomNames.all (fun q => b.isPoint q || c.atomNames.count q ≤ 1)

/-- 4.2: in `nnf c`, no entry with `lo < hi` occurs in two atoms. -/
def Separable (b : Box) (c : Cond) : Bool := sepOK b (nnf c)

def unitForm (b : Box) (f : LinForm) : Bool :=
  f.coeffs.all (fun p => b.isPoint p.1 || p.2 == 1 || p.2 == -1)

/-- The unit-coefficient test on one condition. -/
def unitOK (b : Box) : Cond → Bool
  | .top | .bottom => true
  | .atom f r => match r with
    | .eq | .ne => unitForm b f.val
    | .lt | .le => true
  | .and a c | .or a c => unitOK b a && unitOK b c
  | .not a => unitOK b a

/-- 4.2: in `nnf c`, `=` and `≠` atoms have coefficient ±1 on entries with `lo < hi`. -/
def UnitCoefficients (b : Box) (c : Cond) : Bool := unitOK b (nnf c)

/-! ## Endpoint values (4.3) -/

/-- `Σ (cᵢ ≥ 0 ? cᵢ·loᵢ : cᵢ·hiᵢ)` and its maximising twin. -/
def minSum (b : Box) (l : List (String × Int)) : Int :=
  (l.map (fun (q, c) => if 0 ≤ c then c * b.lo q else c * b.hi q)).sum

def maxSum (b : Box) (l : List (String × Int)) : Int :=
  (l.map (fun (q, c) => if 0 ≤ c then c * b.hi q else c * b.lo q)).sum

def fmin (b : Box) (f : LinForm) : Int := minSum b f.coeffs + f.const
def fmax (b : Box) (f : LinForm) : Int := maxSum b f.coeffs + f.const

/-- The minimising and maximising valuations of a form (every other quantity at its lower bound). -/
def minVal (b : Box) (f : LinForm) : Valuation := fun q =>
  match f.coeffs.find? (·.1 == q) with
  | some (_, c) => if 0 ≤ c then b.lo q else b.hi q
  | none => b.lo q

def maxVal (b : Box) (f : LinForm) : Valuation := fun q =>
  match f.coeffs.find? (·.1 == q) with
  | some (_, c) => if 0 ≤ c then b.hi q else b.lo q
  | none => b.lo q

end VE.Risk
