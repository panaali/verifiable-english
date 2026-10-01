import VE.Risk.Record

/-! Margins (docs/spec/risk.md 4.9 and 7.2): endpoints, perturbation, the outcome
of a perturbed record, the candidates, the candidate limit and the three scans.

`outcomeAt R d e x` validates the admitted record with endpoint `e` set to `x`
(V1 to V11, never admission and never the candidate limit), then evaluates the
regenerated conflict formulas, then the statuses. It reads the record only
through its view (`Record.lean`), so it changes only where an observation does.
`scan`, `scanInvalid` and `scanConflict` evaluate every candidate beyond the
current value in one direction and return the nearest one of their kind; with
`status_piecewise_constant` (`Piecewise.lean`) their soundness follows from the
generic `walk` lemma below. -/
namespace VE.Risk
open VE.Norms (tupleVal)

inductive Outcome | invalid (diagnostic : String) | conflict | statuses (s : List (String × Status))
  deriving DecidableEq, Repr

inductive Side | lo | hi
  deriving DecidableEq, Repr

structure Endpoint where
  estimate : String
  side : Side
  deriving DecidableEq, Repr

inductive Dir | down | up
  deriving DecidableEq, Repr

/-- Each endpoint of each cited estimate (settings excluded; point estimates included). -/
def endpoints (d : Decision) : List Endpoint := d.estimates.flatMap fun e => [⟨e.id, .lo⟩, ⟨e.id, .hi⟩]

/-- The first cited estimate with the endpoint's id. -/
def estimateOf (d : Decision) (id : String) : Option Estimate := d.estimates.find? (·.id == id)

def Estimate.side (est : Estimate) : Side → Int
  | .lo => est.lo
  | .hi => est.hi

def current (d : Decision) (e : Endpoint) : Int := ((estimateOf d e.estimate).map (·.side e.side)).getD 0

def setSide (s : Side) (x : Int) (est : Estimate) : Estimate :=
  match s with
  | .lo => { est with lo := x }
  | .hi => { est with hi := x }

/-- Replace the first element satisfying `p` by its image under `f`. -/
def setFirst {α : Type} (p : α → Bool) (f : α → α) : List α → List α
  | [] => []
  | x :: xs => if p x then f x :: xs else x :: setFirst p f xs

def perturb (d : Decision) (e : Endpoint) (x : Int) : Decision :=
  { d with estimates := setFirst (·.id == e.estimate) (setSide e.side x) d.estimates }

def outcomeOfView (R : RiskDoc) (v : View) : Outcome :=
  match validateView R v with
  | .error t => .invalid t
  | .ok () => if (VE.Alternatives.scenarioConflict (toAlt R) (modelOfView R v)).isSome then .conflict
      else .statuses (statusesOfView R v)

/-- On `perturb d e x`: validation (the diagnostic without its case), then the regenerated conflict formulas on
the decision model, then the statuses; no admission and no candidate limit (4.9). -/
def outcomeAt (R : RiskDoc) (d : Decision) (e : Endpoint) (x : Int) : Outcome :=
  outcomeOfView R (view R (perturb d e x))

/-! ## Candidates (4.9) -/

/-- `⌊t⌋` and `⌈t⌉` of `t = −k / c` (`c ≠ 0`). -/
def floorCeil (k c : Int) : Int × Int :=
  let n := if 0 < c then -k else k
  let m := if 0 < c then c else -c
  let fl := n / m
  (fl, if n % m = 0 then fl else fl + 1)

def LinForm.coeffOf (f : LinForm) (q : String) : Option Int := (f.coeffs.find? (·.1 == q)).map (·.2)

def LinForm.without (f : LinForm) (q : String) : LinForm := ⟨f.coeffs.filter (·.1 != q), f.const⟩

/-- The threshold candidates of one atom for endpoint side `s` of quantity `q`: exactly one extremum of the
atom depends on the endpoint, namely `c·x + K` with `K` the matching extremum of the rest on the box. -/
def atomCandidates (b : Box) (q : String) (s : Side) (f : LinForm) : List Int :=
  match f.coeffOf q with
  | none => []
  | some c =>
    let K := if (s == .lo) == decide (0 ≤ c) then fmin b (f.without q) else fmax b (f.without q)
    let (fl, cl) := floorCeil K c
    [fl - 1, fl, cl, cl + 1]

/-- Duplicates removed (the last occurrence kept). -/
def dedup : List Int → List Int
  | [] => []
  | x :: xs => if (dedup xs).contains x then dedup xs else x :: dedup xs

theorem mem_dedup {a : Int} : ∀ {l : List Int}, a ∈ dedup l ↔ a ∈ l
  | [] => by simp [dedup]
  | x :: xs => by
    simp only [dedup]
    split
    · rename_i h
      rw [mem_dedup, List.mem_cons]
      constructor
      · exact Or.inr
      · rintro (rfl | h')
        · exact mem_dedup.mp (by simpa using h)
        · exact h'
    · simp [mem_dedup]

def recordAtoms (d : Decision) : List LinForm := d.conditions.flatMap fun c => (atomsOf c.cond).map (·.1.val)

/-- 4.9: the current value; `w − 1`, `w`, `w + 1` for every endpoint `w` of every cited estimate of the
endpoint's quantity; and the four threshold neighbours of every atom mentioning that quantity. -/
def candidates (R : RiskDoc) (d : Decision) (e : Endpoint) : List Int :=
  match estimateOf d e.estimate with
  | none => [current d e]
  | some est =>
    let ws := (estimatesOf d est.quantity).flatMap fun x => [x.lo, x.hi]
    dedup (current d e :: ws.flatMap (fun w => [w - 1, w, w + 1]) ++
      (recordAtoms d).flatMap (atomCandidates (box R d) est.quantity e.side))

/-- 4.9 and 9: every endpoint has at most 256 candidates, checked once on the admitted, valid record. -/
def marginLimit (R : RiskDoc) (d : Decision) : Except String Unit :=
  if (endpoints d).all (fun e => (candidates R d e).length ≤ 256) then .ok ()
  else .error "ResourceLimit: risk margin candidates"

/-! ## Scans -/

def Beyond (dir : Dir) (x₀ y : Int) : Prop := match dir with | .down => y < x₀ | .up => x₀ < y

instance (dir : Dir) (x₀ y : Int) : Decidable (Beyond dir x₀ y) := by
  cases dir <;> unfold Beyond <;> infer_instance

def StatusKept (o : Outcome) (a : String) (s : Status) : Prop :=
  o = .conflict ∨ (∃ t, o = .invalid t) ∨ ∃ ss, o = .statuses ss ∧ ss.lookup a = some s

/-- `m` is at least as near to the current value as `y` in direction `dir`. -/
def NearAs (dir : Dir) (m y : Int) : Prop := match dir with | .up => m ≤ y | .down => y ≤ m

instance (dir : Dir) (m y : Int) : Decidable (NearAs dir m y) := by
  cases dir <;> unfold NearAs <;> infer_instance

/-- The value of `l` nearest to the current value in direction `dir` (the least going up). -/
def nearest (dir : Dir) : List Int → Option Int
  | [] => none
  | y :: l => match nearest dir l with
    | none => some y
    | some m => if NearAs dir y m then some y else some m

/-- The nearest candidate beyond the current value at which `P` holds of the outcome. -/
def scanWith (R : RiskDoc) (d : Decision) (e : Endpoint) (dir : Dir) (P : Outcome → Bool) : Option Int :=
  nearest dir ((candidates R d e).filter fun y => decide (Beyond dir (current d e) y) && P (outcomeAt R d e y))

def curStatus (R : RiskDoc) (d : Decision) (e : Endpoint) (a : String) : Option Status :=
  match outcomeAt R d e (current d e) with
  | .statuses ss => ss.lookup a
  | _ => none

def changedAt (a : String) (s : Option Status) : Outcome → Bool
  | .statuses ss => ss.lookup a != s
  | _ => false

def isInvalid : Outcome → Bool
  | .invalid _ => true
  | _ => false

def isConflict : Outcome → Bool
  | .conflict => true
  | _ => false

/-- The nearest candidate beyond the current value at which the outcome is `statuses` with `a`'s status changed. -/
def scan (R : RiskDoc) (d : Decision) (e : Endpoint) (dir : Dir) (a : String) : Option Int :=
  scanWith R d e dir (changedAt a (curStatus R d e a))

/-- The nearest candidate beyond the current value at which the outcome is `invalid`, with its diagnostic. -/
def scanInvalid (R : RiskDoc) (d : Decision) (e : Endpoint) (dir : Dir) : Option (Int × String) :=
  (scanWith R d e dir isInvalid).bind fun x => match outcomeAt R d e x with
    | .invalid t => some (x, t)
    | _ => none

/-- The nearest candidate beyond the current value at which the outcome is `conflict`. -/
def scanConflict (R : RiskDoc) (d : Decision) (e : Endpoint) (dir : Dir) : Option Int :=
  scanWith R d e dir isConflict

/-! ## Generic facts about the scans -/

theorem nearest_spec (dir : Dir) : ∀ l : List Int,
    (nearest dir l = none ↔ l = []) ∧ ∀ m, nearest dir l = some m → m ∈ l ∧ ∀ y ∈ l, NearAs dir m y
  | [] => ⟨by simp [nearest], fun m h => by simp [nearest] at h⟩
  | y :: l => by
    have ih := nearest_spec dir l
    refine ⟨by simp only [nearest]; split <;> (try split) <;> simp, fun m hm => ?_⟩
    simp only [nearest] at hm
    split at hm
    · rename_i hn
      have := ih.1.mp hn
      subst this
      simp only [Option.some.injEq] at hm
      subst hm
      refine ⟨List.mem_cons_self .., fun z hz => ?_⟩
      simp only [List.mem_singleton] at hz
      subst hz
      cases dir <;> simp [NearAs]
    · rename_i m' hm'
      obtain ⟨hm1, hm2⟩ := ih.2 m' hm'
      split at hm
      · rename_i hb
        simp only [Option.some.injEq] at hm
        subst hm
        refine ⟨List.mem_cons_self .., fun z hz => ?_⟩
        rcases List.mem_cons.mp hz with rfl | hz
        · cases dir <;> simp [NearAs]
        · have := hm2 z hz
          cases dir <;> simp only [NearAs] at hb this ⊢ <;> omega
      · rename_i hb
        simp only [Option.some.injEq] at hm
        subst hm
        refine ⟨List.mem_cons_of_mem _ hm1, fun z hz => ?_⟩
        rcases List.mem_cons.mp hz with rfl | hz
        · cases dir <;> simp only [NearAs] at hb ⊢ <;> omega
        · exact hm2 z hz

section Walk
variable {α : Type} {O : Int → α} {C : List Int}

/-- A value beyond `cur` going up that is not a candidate has the outcome of a candidate between them, when
`cur + 1` is a candidate and outcomes change only between two adjacent candidates. -/
theorem walk_up (cur : Int) (hc : cur + 1 ∈ C) (hpw : ∀ x, x ∉ C ∨ x + 1 ∉ C → O x = O (x + 1)) :
    ∀ (n : Nat) (y : Int), y = cur + 1 + n → ∃ z ∈ C, cur < z ∧ z ≤ y ∧ O z = O y
  | 0, y, hy => ⟨y, by rw [hy]; simpa using hc, by omega, Int.le_refl _, rfl⟩
  | n + 1, y, hy => by
    by_cases hyc : y ∈ C
    · exact ⟨y, hyc, by omega, Int.le_refl _, rfl⟩
    · obtain ⟨z, hz, h1, h2, h3⟩ := walk_up cur hc hpw n (y - 1) (by omega)
      have := hpw (y - 1) (Or.inr (by simpa using hyc))
      simp only [Int.sub_add_cancel] at this
      exact ⟨z, hz, h1, by omega, h3.trans this⟩

theorem walk_down (cur : Int) (hc : cur - 1 ∈ C) (hpw : ∀ x, x ∉ C ∨ x + 1 ∉ C → O x = O (x + 1)) :
    ∀ (n : Nat) (y : Int), y = cur - 1 - n → ∃ z ∈ C, z < cur ∧ y ≤ z ∧ O z = O y
  | 0, y, hy => ⟨y, by rw [hy]; simpa using hc, by omega, Int.le_refl _, rfl⟩
  | n + 1, y, hy => by
    by_cases hyc : y ∈ C
    · exact ⟨y, hyc, by omega, Int.le_refl _, rfl⟩
    · obtain ⟨z, hz, h1, h2, h3⟩ := walk_down cur hc hpw n (y + 1) (by omega)
      have := hpw y (Or.inl hyc)
      exact ⟨z, hz, h1, by omega, h3.trans this.symm⟩

/-- Every value beyond `cur` has the outcome of a candidate beyond `cur` no farther out. -/
theorem walk (dir : Dir) (cur : Int) (hc1 : cur + 1 ∈ C) (hc2 : cur - 1 ∈ C)
    (hpw : ∀ x, x ∉ C ∨ x + 1 ∉ C → O x = O (x + 1)) (y : Int) (hy : Beyond dir cur y) :
    ∃ z ∈ C, Beyond dir cur z ∧ (match dir with | .up => z ≤ y | .down => y ≤ z) ∧ O z = O y := by
  cases dir with
  | up =>
    obtain ⟨z, hz, h1, h2, h3⟩ := walk_up cur hc1 hpw (y - cur - 1).toNat y (by simp [Beyond] at hy; omega)
    exact ⟨z, hz, h1, h2, h3⟩
  | down =>
    obtain ⟨z, hz, h1, h2, h3⟩ := walk_down cur hc2 hpw (cur - 1 - y).toNat y (by simp [Beyond] at hy; omega)
    exact ⟨z, hz, h1, h2, h3⟩

end Walk

/-! ## Scan soundness, given that outcomes change only between adjacent candidates -/

theorem mem_filter_scan {R : RiskDoc} {d : Decision} {e : Endpoint} {dir : Dir} {P : Outcome → Bool} {y : Int} :
    y ∈ (candidates R d e).filter (fun y => decide (Beyond dir (current d e) y) && P (outcomeAt R d e y)) ↔
      y ∈ candidates R d e ∧ Beyond dir (current d e) y ∧ P (outcomeAt R d e y) = true := by
  simp [List.mem_filter]

theorem scanWith_sound {R : RiskDoc} {d : Decision} {e : Endpoint} {dir : Dir} {P : Outcome → Bool}
    (hc1 : current d e + 1 ∈ candidates R d e) (hc2 : current d e - 1 ∈ candidates R d e)
    (hpw : ∀ x, x ∉ candidates R d e ∨ x + 1 ∉ candidates R d e → outcomeAt R d e x = outcomeAt R d e (x + 1)) :
    (∀ x, scanWith R d e dir P = some x →
      Beyond dir (current d e) x ∧ P (outcomeAt R d e x) = true ∧
      ∀ y, Beyond dir (current d e) y → Beyond dir y x → P (outcomeAt R d e y) = false) ∧
    (scanWith R d e dir P = none → ∀ y, Beyond dir (current d e) y → P (outcomeAt R d e y) = false) := by
  have hn := nearest_spec dir ((candidates R d e).filter
    (fun y => decide (Beyond dir (current d e) y) && P (outcomeAt R d e y)))
  refine ⟨fun x hx => ?_, fun hx y hy => ?_⟩
  · obtain ⟨hm, hall⟩ := hn.2 x hx
    obtain ⟨_, hb, hp⟩ := mem_filter_scan.mp hm
    refine ⟨hb, hp, fun y hy hyx => ?_⟩
    obtain ⟨z, hz, hzb, hzy, hzo⟩ := walk dir (current d e) hc1 hc2 hpw y hy
    rw [← hzo]
    cases hpz : P (outcomeAt R d e z)
    · rfl
    · have := hall z (mem_filter_scan.mpr ⟨hz, hzb, hpz⟩)
      cases dir <;> simp only [NearAs, Beyond] at this hyx hzy <;> omega
  · have hnil := hn.1.mp hx
    obtain ⟨z, hz, hzb, _, hzo⟩ := walk dir (current d e) hc1 hc2 hpw y hy
    rw [← hzo]
    cases hpz : P (outcomeAt R d e z)
    · rfl
    · have := mem_filter_scan.mpr ⟨hz, hzb, hpz⟩
      rw [hnil] at this
      cases this

theorem mem_estimates_of_endpoint {d : Decision} {e : Endpoint} (he : e ∈ endpoints d) :
    ∃ est, estimateOf d e.estimate = some est := by
  simp only [endpoints, List.mem_flatMap, List.mem_cons, List.not_mem_nil, or_false] at he
  obtain ⟨est, hm, hep⟩ := he
  have : ∃ x ∈ d.estimates, (x.id == e.estimate) = true := ⟨est, hm, by rcases hep with rfl | rfl <;> simp⟩
  cases hf : estimateOf d e.estimate with
  | none =>
    unfold estimateOf at hf
    obtain ⟨x, hx, hp⟩ := this
    exact absurd hp (List.find?_eq_none.mp hf x hx)
  | some est => exact ⟨est, rfl⟩

/-- The candidates of an endpoint include its current value's neighbours. -/
theorem neighbours_mem {R : RiskDoc} {d : Decision} {e : Endpoint} (he : e ∈ endpoints d) :
    current d e + 1 ∈ candidates R d e ∧ current d e - 1 ∈ candidates R d e := by
  obtain ⟨est, hest⟩ := mem_estimates_of_endpoint he
  have hmem : est ∈ d.estimates := List.mem_of_find?_eq_some hest
  have hq : est ∈ estimatesOf d est.quantity := List.mem_filter.mpr ⟨hmem, by simp⟩
  have hcur : current d e = est.side e.side := by simp [current, hest]
  have hw : current d e ∈ (estimatesOf d est.quantity).flatMap (fun x => [x.lo, x.hi]) := by
    rw [hcur]
    exact List.mem_flatMap.mpr ⟨est, hq, by cases e.side <;> simp [Estimate.side]⟩
  simp only [candidates, hest]
  constructor
  · apply mem_dedup.mpr
    apply List.mem_cons_of_mem
    apply List.mem_append_left
    exact List.mem_flatMap.mpr ⟨_, hw, by simp⟩
  · apply mem_dedup.mpr
    apply List.mem_cons_of_mem
    apply List.mem_append_left
    exact List.mem_flatMap.mpr ⟨_, hw, by simp⟩

end VE.Risk
