import VE.Calc.Inline
import VE.Calc.Poly

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

theorem freeNames_mem (ds : List Decl) : ∀ n ∈ freeNames ds, n ∈ ds.map Decl.name := by
  intro n hn; simp only [freeNames, List.mem_map, List.mem_filter] at hn ⊢
  obtain ⟨d, ⟨hd, _⟩, rfl⟩ := hn; exact ⟨d, hd, rfl⟩

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
as nonzero. -/
def Expr.zeroDivisor : Expr → Bool
  | .lit _ | .val _ => false
  | .add a b | .sub a b | .mul a b => a.zeroDivisor || b.zeroDivisor
  | .div a b => a.zeroDivisor || b.zeroDivisor || ((Frac.ofExpr? b).map (·.1.isEmpty)).getD false
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
      cases hf : Frac.ofExpr? b with
      | none => simp [hf] at h
      | some f =>
          simp only [hf, Option.map_some, Option.getD_some, List.isEmpty_iff] at h
          have := (Frac.ofExpr_sound κ b f.1 f.2 y hf hb).2
          rw [h, Poly.eval_nil] at this; exact hne (by rw [this]; grind)

/-- Why the normaliser gave no answer: a side past the node limit once its named values are inlined (it may still
have one term, review F4), or a polynomial on the way past the limits of `Poly.lean`. -/
inductive IdentityStop where
  | nodes | form
  deriving Repr, DecidableEq

def IdentityStop.text : IdentityStop → String
  | .nodes => "unknown: a side would have more than 10,000 nodes once its named values are written out"
  | .form => "unknown: a normal form on the way would have more than 10,000 terms before like terms merge, " ++
      "an exponent above 4,096 or a coefficient of more than 4,096 digits"

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

/-- The identity row (spec 8.2): inline both sides with the free values kept, the first faulty side naming the fault;
then decide over the free values the sides read, in declaration order. -/
def identityRun (ds : List Decl) (a b : Expr) : IdentityRow :=
  match a.inline ds (freeNames ds), b.inline ds (freeNames ds) with
  | .ok a', .ok b' => identityDecide (freeNames ds) a' b'
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

theorem identityRun_holds (ds : List Decl) (h : WellFormed ds) (a b : Expr)
    (hr : (identityRun ds a b).outcome = .decided .holds) : IsIdentity ds a b := by
  cases ha : a.inline ds (freeNames ds) with
  | error v => cases v <;> simp [identityRun, ha] at hr
  | ok a' =>
    cases hb : b.inline ds (freeNames ds) with
    | error v => cases v <;> simp [identityRun, ha, hb] at hr
    | ok b' =>
        simp only [identityRun, ha, hb] at hr
        exact isIdentity_of_check ds h a b _ _ ha hb ((identityDecide_outcome _ _ _).1 hr)

theorem identityRun_fails (ds : List Decl) (h : WellFormed ds) (a b : Expr)
    (hr : (identityRun ds a b).outcome = .decided .fails) : NotIdentity ds a b := by
  cases ha : a.inline ds (freeNames ds) with
  | error v => cases v <;> simp [identityRun, ha] at hr
  | ok a' =>
    cases hb : b.inline ds (freeNames ds) with
    | error v => cases v <;> simp [identityRun, ha, hb] at hr
    | ok b' =>
        simp only [identityRun, ha, hb] at hr
        obtain ⟨κ, hκ⟩ := (identityDecide_outcome _ _ _).2.1 hr
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
        rcases (identityDecide_outcome _ _ _).2.2.1 hr with h' | h'
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
        rcases (identityDecide_outcome _ _ _).2.2.2 u hr with rfl | rfl <;> simp

end VE.Calc
