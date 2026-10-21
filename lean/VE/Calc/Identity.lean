import VE.Calc.Inline
import VE.Calc.Poly
import VE.Limits

/-! Identities over named values (spec 8.2, J3): both sides are inlined with the free values kept (spec 2.7), then
decided by the normaliser of `Poly.lean` and the point search. The meaning `IsIdentity`, its bridge theorems and the
runner `identityRun`, with one theorem per outcome. -/

namespace VE.Calc
open VE.Numbers

/-- The meaning of an identity: the two sides are equal wherever both denote, for every value of the free values. -/
def IsIdentity (ds : List Decl) (a b : Expr) : Prop :=
  ∀ κ x y, Denotes (values (assign ds (freeNames ds) κ)) a x → Denotes (values (assign ds (freeNames ds) κ)) b y →
    x = y

/-- What a "not an identity" row states. -/
def NotIdentity (ds : List Decl) (a b : Expr) : Prop :=
  ∃ κ x y, Denotes (values (assign ds (freeNames ds) κ)) a x ∧ Denotes (values (assign ds (freeNames ds) κ)) b y ∧
    x ≠ y

theorem not_isIdentity (ds : List Decl) (a b : Expr) (h : NotIdentity ds a b) : ¬ IsIdentity ds a b := by
  obtain ⟨κ, x, y, hx, hy, hne⟩ := h
  exact fun hi => hne (hi κ x y hx hy)

theorem Denotes.mono {σ τ : Values} {e : Expr} {x : Rat} (h : Denotes σ e x) (hστ : ∀ n q, σ n = some q → τ n = some q) :
    Denotes τ e x := by
  induction h with
  | lit => exact .lit
  | val hv => exact .val (hστ _ _ hv)
  | add _ _ iha ihb => exact .add iha ihb
  | sub _ _ iha ihb => exact .sub iha ihb
  | mul _ _ iha ihb => exact .mul iha ihb
  | div _ _ hne iha ihb => exact .div iha ihb hne
  | pow _ ih => exact .pow ih

/-- Over the inlined sides, the normaliser proves the identity and a differing point refutes it (J3). -/
theorem isIdentity_of_check (ds : List Decl) (h : WellFormed ds) (a b a' b' : Expr)
    (ha : a.inline ds (freeNames ds) = .ok a') (hb : b.inline ds (freeNames ds) = .ok b')
    (hc : identityCheck a' b' = true) : IsIdentity ds a b := by
  intro κ x y hx hy
  exact identity_sound a' b' hc κ x y ((Expr.inline_sound ds h _ (freeNames_mem ds) a a' ha κ x).mp hx)
    ((Expr.inline_sound ds h _ (freeNames_mem ds) b b' hb κ y).mp hy)

theorem notIdentity_of_differsAt (ds : List Decl) (h : WellFormed ds) (a b a' b' : Expr)
    (ha : a.inline ds (freeNames ds) = .ok a') (hb : b.inline ds (freeNames ds) = .ok b')
    (κ : List (String × Rat)) (hd : differsAt a' b' κ = true) : NotIdentity ds a b := by
  obtain ⟨x, y, hx, hy, hne⟩ := differsAt_sound a' b' κ hd
  let κ' : String → Rat := fun n => (κ.lookup n).getD 0
  have hm : ∀ n q, κ.lookup n = some q → some (κ' n) = some q := by intro n q h; simp [κ', h]
  exact ⟨κ', x, y, (Expr.inline_sound ds h _ (freeNames_mem ds) a a' ha κ' x).mpr (hx.mono hm),
    (Expr.inline_sound ds h _ (freeNames_mem ds) b b' hb κ' y).mpr (hy.mono hm), hne⟩

/-- A divisor whose fraction form has no terms above the line is zero wherever it denotes, so the side denotes nothing
anywhere and an identity over it would hold only vacuously (me-9 review F3). A divisor whose form is refused counts
as nonzero. Read only on a side the normaliser accepted, so within the node limit. -/
def Expr.zeroDivisor : Expr → Bool
  | .lit _ | .val _ => false
  | .add a b | .sub a b | .mul a b => a.zeroDivisor || b.zeroDivisor
  | .div a b => a.zeroDivisor || b.zeroDivisor || ((Frac.go b).map (·.1.isEmpty)).getD false
  | .pow a _ => a.zeroDivisor

theorem Expr.zeroDivisor_sound (κ : String → Rat) {e : Expr} (h : e.zeroDivisor = true) (x : Rat) :
    ¬ Denotes (fun v => some (κ v)) e x := by
  intro hx; revert h
  induction hx with
  | lit | val _ => simp [Expr.zeroDivisor]
  | add _ _ iha ihb | sub _ _ iha ihb | mul _ _ iha ihb =>
      simp only [Expr.zeroDivisor, Bool.or_eq_true]; rintro (h | h) <;> first | exact iha h | exact ihb h
  | pow _ ih => exact ih
  | @div a b x y _ hb hne iha ihb =>
      simp only [Expr.zeroDivisor, Bool.or_eq_true]; rintro ((h | h) | h)
      · exact iha h
      · exact ihb h
      cases hf : Frac.go b with
      | none => simp [hf] at h
      | some f =>
          simp only [hf, Option.map_some, Option.getD_some, List.isEmpty_iff] at h
          have := (Frac.go_sound κ b y hb f hf).2
          rw [h, Poly.eval_nil] at this; exact hne (by rw [this]; grind)

/-- Why the normaliser gave no answer: a side past the node limit once its named values are inlined (it may still
have one term, review F4), or a polynomial on the way past the limits of `Poly.lean`. -/
inductive IdentityStop where
  | nodes | form | budget
  deriving Repr, DecidableEq

def IdentityStop.text : IdentityStop → String
  | .nodes => "unknown: a side would have more than 10,000 nodes once its named values are written out"
  | .form => "unknown: a normal form on the way would have more than 10,000 terms before like terms merge, " ++
      "an exponent above 4,096 or a coefficient of more than 4,096 digits"
  | .budget => (UnknownReason.limit .evaluations).text VE.Limits.maxEvaluations

/-- The values tried, in order: point `i` gives the `j`th name the value `identityValues[i * (j + 1) % 13]`, so
point 0 sets every name to 1. -/
def identityValues : List Rat := [1, 2, 3, -1, 1/2, 5, -2, 1/3, 7, -3, 3/2, 11, 0]

def identityPoint (names : List String) (i : Nat) : List (String × Rat) :=
  names.mapIdx fun j n => (n, identityValues.getD (i * (j + 1) % 13) 0)

/-- A row: its outcome; for `fails` the point (one value per free value read, in declaration order) and the two sides'
values there; for an unknown at the normaliser's limits, which limit. -/
structure IdentityRow where
  outcome : Outcome
  point : Option (List (String × Rat)) := none
  sides : Option (Rat × Rat) := none
  stop : Option IdentityStop := none
  deriving Repr, DecidableEq

/-- The reason a row shows: the stop's text at the normaliser's limits, else the text of its unknown reason (1.5). -/
def IdentityRow.reason (budget : Nat) (r : IdentityRow) : Option String :=
  match r.outcome with
  | .unknown u => some ((r.stop.map IdentityStop.text).getD (u.text budget))
  | .decided _ => none

/-- Over inlined sides: compare the normal forms; a side with a zero divisor denotes nothing (before `holds`); else try
the 13 points over the names of `keep` the sides read. Those names, and the zero divisors, are looked for only once
the normaliser has accepted both sides, whose trees are then within the node limit. -/
def identityDecide (keep : List String) (a' b' : Expr) : IdentityRow :=
  match Identity.compare a' b' with
  | none =>
    { outcome := .unknown (.limit .polyTerms),
      stop := if (a'.nodesWithin maxPolyTerms).isSome && (b'.nodesWithin maxPolyTerms).isSome then some .form else some .nodes }
  | some r =>
    if a'.zeroDivisor || b'.zeroDivisor then { outcome := .decided .undefined } else
    if r then { outcome := .decided .holds } else
    let names := keep.filter (· ∈ a'.names ++ b'.names)
    match ((List.range 13).map (identityPoint names)).find? (differsAt a' b') with
    | some κ => { outcome := .decided .fails, point := some κ,
                  sides := (a'.eval (κ.lookup ·)).bind fun x => (b'.eval (κ.lookup ·)).map (x, ·) }
    | none => { outcome := .unknown .identityNotShown }

/-! ### The row within the work budget (me-9c)

`identityDecide` within `n` evaluation units (`Poly.lean`'s budget): one pass over each side builds its fraction form
and finds its zero divisors, so nested divisors cost no more than their nodes; then the cross products and the points.
Past the budget the row is `budgetRow`; within it, `identityDecide`'s row (`identityDecideB_eq`). -/

/-- `Frac.go` within a budget, with `Expr.zeroDivisor` found in the same pass. -/
def Frac.goB : Expr → Nat → Budgeted (Option (Frac × Bool))
  | .lit q, n => charge 1 n fun _ => (Frac.go (.lit q)).map (·, false)
  | .val x, n => charge 1 n fun _ => (Frac.go (.val x)).map (·, false)
  | .add a b, n => Budgeted.bin (Frac.goB a n) (Frac.goB b) fun f g n => (Frac.add?B f.1 g.1 n).map fun (h, n) =>
      (h.map (·, f.2 || g.2), n)
  | .sub a b, n => Budgeted.bin (Frac.goB a n) (Frac.goB b) fun f g n => (Frac.add?B f.1 (Poly.neg g.1.1, g.1.2) n).map
      fun (h, n) => (h.map (·, f.2 || g.2), n)
  | .mul a b, n => Budgeted.bin (Frac.goB a n) (Frac.goB b) fun f g n => (Frac.mul?B f.1 g.1 n).map fun (h, n) =>
      (h.map (·, f.2 || g.2), n)
  | .div a b, n => Budgeted.bin (Frac.goB a n) (Frac.goB b) fun f g n => (Frac.div?B f.1 g.1 n).map fun (h, n) =>
      (h.map (·, f.2 || g.2 || g.1.1.isEmpty), n)
  | .pow a k, n => Budgeted.bin (Frac.goB a n) (fun n => some (some (), n)) fun f _ n => (Frac.pow?B f.1 k n).map
      fun (h, n) => (h.map (·, f.2), n)

/-- `Identity.compare` within a budget, and whether either side has a zero divisor. -/
def Identity.compareB (a b : Expr) (n : Nat) : Budgeted (Option (Bool × Bool)) :=
  let form (e : Expr) (n : Nat) := if (e.nodesWithin maxPolyTerms).isSome then Frac.goB e n else some (none, n)
  Budgeted.bin (form a n) (form b) fun fa fb n =>
    charge (2 * Poly.mulCost fa.1.1 fb.1.2 + Poly.mulCost fb.1.1 fa.1.2) n fun _ =>
      ((Poly.mul? fa.1.1 fb.1.2).bind fun l => (Poly.mul? fb.1.1 fa.1.2).map (l == ·)).map (·, fa.2 || fb.2)

/-- The first point where the sides denote and differ, with their values there, within a budget. -/
def pointsB (a b : Expr) :
    List (List (String × Rat)) → Nat → Budgeted (Option (List (String × Rat) × Option (Rat × Rat)))
  | [], n => some (none, n)
  | κ :: ks, n => match sidesAtB a b κ n with
    | some (s, n) => if (s.map fun s => s.1 != s.2).getD false then some (some (κ, s), n) else pointsB a b ks n
    | none => none

def budgetRow : IdentityRow := { outcome := .unknown (.limit .polyTerms), stop := some .budget }

def identityDecideB (keep : List String) (a' b' : Expr) (n : Nat) : IdentityRow :=
  match Identity.compareB a' b' n with
  | none => budgetRow
  | some (none, _) =>
    { outcome := .unknown (.limit .polyTerms),
      stop := if (a'.nodesWithin maxPolyTerms).isSome && (b'.nodesWithin maxPolyTerms).isSome then some .form
        else some .nodes }
  | some (some (r, z), n) =>
    if z then { outcome := .decided .undefined } else
    if r then { outcome := .decided .holds } else
    let read := a'.names ++ b'.names  -- once, not once per kept name
    let names := keep.filter (· ∈ read)
    match pointsB a' b' ((List.range 13).map (identityPoint names)) n with
    | some (some (κ, s), _) => { outcome := .decided .fails, point := some κ, sides := s }
    | some (none, _) => { outcome := .unknown .identityNotShown }
    | none => budgetRow

/-- The identity row (spec 8.2): inline both sides with the free values kept, the first faulty side naming the fault;
then decide over the free values the sides read, in declaration order, within the budget. -/
def identityRun (ds : List Decl) (a b : Expr) : IdentityRow :=
  match a.inline ds (freeNames ds), b.inline ds (freeNames ds) with
  | .ok a', .ok b' => identityDecideB (freeNames ds) a' b' VE.Limits.maxEvaluations
  | .error .exhausted, _ | .ok _, .error .exhausted => { outcome := .unknown (.limit .evaluations) }
  | _, _ => { outcome := .decided .undefined }

theorem identityDecide_outcome (keep : List String) (a' b' : Expr) :
    ((identityDecide keep a' b').outcome = .decided .holds → identityCheck a' b' = true) ∧
    ((identityDecide keep a' b').outcome = .decided .fails → ∃ κ, differsAt a' b' κ = true) ∧
    ((identityDecide keep a' b').outcome = .decided .undefined → a'.zeroDivisor ∨ b'.zeroDivisor) ∧
    (∀ u, (identityDecide keep a' b').outcome = .unknown u → u = .limit .polyTerms ∨ u = .identityNotShown) := by
  unfold identityDecide
  split
  · simp
  · rename_i r hr
    by_cases hz : (a'.zeroDivisor || b'.zeroDivisor) = true
    · simp only [hz, if_true]; simpa using hz
    · simp only [hz, if_false, Bool.false_eq_true]
      by_cases hr' : r = true
      · simp [hr', identityCheck, hr]
      · simp only [hr', if_false, Bool.false_eq_true]; split
        · rename_i κ hκ; simpa using ⟨κ, List.find?_some hκ⟩
        · simp

theorem Frac.flag_eq {x : Budgeted (Option Frac)} {z : Bool} {X : Option Frac} (hx : ∀ r m, x = some (r, m) → r = X)
    {r : Option (Frac × Bool)} {m : Nat} (h : (x.map fun (h, n) => (h.map (·, z), n)) = some (r, m)) :
    r = X.map (·, z) := by
  simp only [Option.map_eq_some_iff] at h; obtain ⟨⟨h', n⟩, hx', he⟩ := h; cases he; rw [hx _ _ hx']

/-- **Budget**: within it, a side's form and its zero divisors are `Frac.go`'s and `Expr.zeroDivisor`'s. -/
theorem Frac.goB_eq (e : Expr) : ∀ n {r : Option (Frac × Bool)} {m : Nat}, Frac.goB e n = some (r, m) →
    r = (Frac.go e).map (·, e.zeroDivisor) := by
  induction e with
  | lit q => intro n r m h; rw [charge_eq h]; rfl
  | val x => intro n r m h; rw [charge_eq h]; rfl
  | add a b iha ihb | sub a b iha ihb | mul a b iha ihb | div a b iha ihb =>
      intro n r m h; simp only [Frac.goB] at h
      rw [Budgeted.bin_eq (fun _ _ h => iha _ h) (fun _ _ _ h => ihb _ h)
        (fun _ _ _ _ _ h => Frac.flag_eq (fun _ _ h => charge_eq h) h) h]
      simp only [Frac.go, Expr.zeroDivisor]; cases Frac.go a <;> cases Frac.go b <;> simp
  | pow a k iha =>
      intro n r m h; simp only [Frac.goB] at h
      rw [Budgeted.bin_eq (fun _ _ h => iha _ h) (Y := some ()) (fun _ _ _ h => by simp_all)
        (fun _ _ _ _ _ h => Frac.flag_eq (fun _ _ h => Frac.pow?B_eq _ _ _ h) h) h]
      simp only [Frac.go, Expr.zeroDivisor]; cases Frac.go a <;> simp

theorem Identity.compareB_eq (a b : Expr) (n : Nat) {r : Option (Bool × Bool)} {m : Nat}
    (h : Identity.compareB a b n = some (r, m)) :
    r = (Identity.compare a b).map (·, a.zeroDivisor || b.zeroDivisor) := by
  have form : ∀ e n r m, (if (e.nodesWithin maxPolyTerms).isSome then Frac.goB e n else some (none, n)) = some (r, m) →
      r = (Frac.ofExpr? e).map (·, e.zeroDivisor) := by
    intro e n r m h; unfold Frac.ofExpr?; split at h
    · rename_i hs; simp only [hs, if_true]; exact Frac.goB_eq e n h
    · rename_i hs; simp only [hs]; cases h; rfl
  rw [Budgeted.bin_eq (fun _ _ h => form _ _ _ _ h) (fun _ _ _ h => form _ _ _ _ h) (fun _ _ _ _ _ h => charge_eq h) h]
  simp only [Identity.compare]
  cases Frac.ofExpr? a <;> cases Frac.ofExpr? b <;> simp

theorem pointsB_eq (a b : Expr) (ks : List (List (String × Rat))) : ∀ n {r} {m : Nat}, pointsB a b ks n = some (r, m) →
    r = (ks.find? (differsAt a b)).map fun κ =>
      (κ, (a.eval (κ.lookup ·)).bind fun x => (b.eval (κ.lookup ·)).map (x, ·)) := by
  induction ks with
  | nil => intro n r m h; simp only [pointsB, Option.some.injEq, Prod.mk.injEq] at h; simp [h.1]
  | cons κ ks ih =>
      intro n r m h; simp only [pointsB] at h; split at h
      · rename_i s n' hs; obtain ⟨h1, h2⟩ := sidesAtB_eq a b κ n hs
        simp only [List.find?_cons, h2]; split at h
        · rename_i hd; simp only [hd]; cases h; simp [h1]
        · rename_i hd; simp only [hd]; exact ih n' h
      · cases h

theorem identityDecide_stop (keep : List String) (a' b' : Expr) : (identityDecide keep a' b').stop ≠ some .budget := by
  unfold identityDecide; split
  · split <;> simp
  · split
    · simp
    · split
      · simp
      · dsimp only; split <;> simp

/-- **Budget**: the budgeted row is `identityDecide`'s row, or the budget's unknown row. -/
theorem identityDecideB_eq (keep : List String) (a' b' : Expr) (n : Nat) :
    identityDecideB keep a' b' n = budgetRow ∨ identityDecideB keep a' b' n = identityDecide keep a' b' := by
  unfold identityDecideB identityDecide
  split
  · exact .inl rfl
  · rename_i n' hc; have := Identity.compareB_eq a' b' n hc
    cases hcmp : Identity.compare a' b' with
    | none => simp
    | some r => simp [hcmp] at this
  · rename_i r z n' hc; have := Identity.compareB_eq a' b' n hc
    cases hcmp : Identity.compare a' b' with
    | none => simp [hcmp] at this
    | some r' =>
      simp only [hcmp, Option.map_some, Option.some.injEq, Prod.mk.injEq] at this; obtain ⟨rfl, rfl⟩ := this
      split
      · right; simp_all
      · split
        · right; simp_all
        · rename_i hz hr; simp only [hr, Bool.false_eq_true, if_false]
          split
          · rename_i hp; have := pointsB_eq a' b' _ _ hp; right
            split <;> rename_i hf <;> rw [hf] at this <;> simp_all
          · rename_i hp; have := pointsB_eq a' b' _ _ hp; right
            split <;> rename_i hf <;> rw [hf] at this <;> simp_all
          · exact .inl rfl

/-- **Budget**: a row within the budget is the unbudgeted row; a row past it is the unknown row, never a verdict. -/
theorem identityDecideB_within (keep : List String) (a' b' : Expr) (n : Nat)
    (h : (identityDecideB keep a' b' n).stop ≠ some .budget) :
    identityDecideB keep a' b' n = identityDecide keep a' b' :=
  (identityDecideB_eq keep a' b' n).resolve_left fun he => h (by rw [he]; rfl)

theorem identityDecideB_exhausted (keep : List String) (a' b' : Expr) (n : Nat)
    (h : (identityDecideB keep a' b' n).stop = some .budget) : identityDecideB keep a' b' n = budgetRow :=
  (identityDecideB_eq keep a' b' n).resolve_right fun he => identityDecide_stop keep a' b' (he ▸ h)

theorem identityDecideB_outcome (keep : List String) (a' b' : Expr) (n : Nat) :
    ((identityDecideB keep a' b' n).outcome = .decided .holds → identityCheck a' b' = true) ∧
    ((identityDecideB keep a' b' n).outcome = .decided .fails → ∃ κ, differsAt a' b' κ = true) ∧
    ((identityDecideB keep a' b' n).outcome = .decided .undefined → a'.zeroDivisor ∨ b'.zeroDivisor) ∧
    (∀ u, (identityDecideB keep a' b' n).outcome = .unknown u → u = .limit .polyTerms ∨ u = .identityNotShown) := by
  rcases identityDecideB_eq keep a' b' n with h | h <;> rw [h]
  · simp [budgetRow]
  · exact identityDecide_outcome keep a' b'

theorem identityRun_holds (ds : List Decl) (h : WellFormed ds) (a b : Expr)
    (hr : (identityRun ds a b).outcome = .decided .holds) : IsIdentity ds a b := by
  cases ha : a.inline ds (freeNames ds) with
  | error v => cases v <;> simp [identityRun, ha] at hr
  | ok a' =>
    cases hb : b.inline ds (freeNames ds) with
    | error v => cases v <;> simp [identityRun, ha, hb] at hr
    | ok b' =>
        simp only [identityRun, ha, hb] at hr
        exact isIdentity_of_check ds h a b _ _ ha hb ((identityDecideB_outcome _ _ _ _).1 hr)

theorem identityRun_fails (ds : List Decl) (h : WellFormed ds) (a b : Expr)
    (hr : (identityRun ds a b).outcome = .decided .fails) : NotIdentity ds a b := by
  cases ha : a.inline ds (freeNames ds) with
  | error v => cases v <;> simp [identityRun, ha] at hr
  | ok a' =>
    cases hb : b.inline ds (freeNames ds) with
    | error v => cases v <;> simp [identityRun, ha, hb] at hr
    | ok b' =>
        simp only [identityRun, ha, hb] at hr
        obtain ⟨κ, hκ⟩ := (identityDecideB_outcome _ _ _ _).2.1 hr
        exact notIdentity_of_differsAt ds h a b _ _ ha hb κ hκ

theorem identityRun_undefined (ds : List Decl) (h : WellFormed ds) (a b : Expr)
    (hr : (identityRun ds a b).outcome = .decided .undefined) :
    ∃ e ∈ [a, b], ∀ κ x, ¬ Denotes (values (assign ds (freeNames ds) κ)) e x := by
  have hu := fun e (he : e.inline ds (freeNames ds) = .error .undefined) => Expr.inline_undefined ds h _ e he
  have hz := fun e e' (he : e.inline ds (freeNames ds) = .ok e') (hz : e'.zeroDivisor = true) κ x hx =>
    Expr.zeroDivisor_sound κ hz x ((Expr.inline_sound ds h _ (freeNames_mem ds) e e' he κ x).mp hx)
  cases ha : a.inline ds (freeNames ds) with
  | error v =>
      rcases Expr.inline_error ds _ a v ha with rfl | rfl
      · exact ⟨a, by simp, hu a ha⟩
      · simp [identityRun, ha] at hr
  | ok a' =>
    cases hb : b.inline ds (freeNames ds) with
    | error v =>
        rcases Expr.inline_error ds _ b v hb with rfl | rfl
        · exact ⟨b, by simp, hu b hb⟩
        · simp [identityRun, ha, hb] at hr
    | ok b' =>
        simp only [identityRun, ha, hb] at hr
        rcases (identityDecideB_outcome _ _ _ _).2.2.1 hr with h' | h'
        · exact ⟨a, by simp, hz a a' ha h'⟩
        · exact ⟨b, by simp, hz b b' hb h'⟩

/-- An unknown row gives one of the identity's reasons, with the cause the evaluation budget names (spec 3.4). -/
theorem identityRun_unknown (ds : List Decl) (a b : Expr) (u : UnknownReason)
    (hr : (identityRun ds a b).outcome = .unknown u) :
    u ∈ [.limit .polyTerms, .identityNotShown, .limit .digits, .limit .evaluations] ∧
      (u = .limit .digits → ∃ e ∈ [a, b], e.Overflows ds) ∧
      (u = .limit .evaluations → ∃ e ∈ [a, b], e.ReadsExhausted ds) := by
  cases ha : a.inline ds (freeNames ds) with
  | error v =>
      rcases Expr.inline_error ds _ a v ha with rfl | rfl
      · simp [identityRun, ha] at hr
      · simp only [identityRun, ha, Outcome.unknown.injEq] at hr; subst hr
        simpa using Or.inl (Expr.inline_exhausted ds _ a ha)
  | ok a' =>
    cases hb : b.inline ds (freeNames ds) with
    | error v =>
        rcases Expr.inline_error ds _ b v hb with rfl | rfl
        · simp [identityRun, ha, hb] at hr
        · simp only [identityRun, ha, hb, Outcome.unknown.injEq] at hr; subst hr
          simpa using Or.inr (Expr.inline_exhausted ds _ b hb)
    | ok b' =>
        simp only [identityRun, ha, hb] at hr
        rcases (identityDecideB_outcome _ _ _ _).2.2.2 u hr with rfl | rfl <;> simp

/-- **Budget**: a row whose budget ran out is the unknown row `budgetRow`, never a verdict. -/
theorem identityRun_exhausted (ds : List Decl) (a b : Expr) (h : (identityRun ds a b).stop = some .budget) :
    identityRun ds a b = budgetRow := by
  cases ha : a.inline ds (freeNames ds) with
  | error v => cases v <;> simp [identityRun, ha] at h
  | ok a' =>
    cases hb : b.inline ds (freeNames ds) with
    | error v => cases v <;> simp [identityRun, ha, hb] at h
    | ok b' => simp only [identityRun, ha, hb] at h ⊢; exact identityDecideB_exhausted _ _ _ _ h

end VE.Calc
