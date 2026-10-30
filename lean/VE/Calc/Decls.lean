import VE.Calc.Eval
import VE.Numbers.Bits

namespace VE.Calc
open VE.Numbers

inductive Counted where
  | ok (v : Option Rat)
  | exhausted
  deriving Repr, DecidableEq

inductive Source where
  | stated (q : Rat)
  | defined (e : Expr)
  | free
  | counted (value : Thunk (Option Rat)) (run : Counted)

structure Decl where
  name : String
  source : Source

def Decl.valueUnder (d : Decl) (σ : Values) : Option Rat :=
  match d.source with
  | .stated q => some q
  | .defined e => e.eval σ
  | .free => none
  | .counted q _ => q.get

def values (ds : List Decl) : Values :=
  ds.foldl (fun σ d n => if n = d.name then d.valueUnder σ else σ n) (fun _ => none)

def WellFormed (ds : List Decl) : Prop :=
  (ds.map Decl.name).Nodup ∧
    (∀ (i : Nat) (hi : i < ds.length) (e : Expr), (ds[i]'hi).source = .defined e →
      ∀ n ∈ e.names, n ∈ (ds.take i).map Decl.name) ∧
    ∀ d ∈ ds, ∀ q v, d.source = .counted q (.ok v) → q.get = v

theorem fold_values_other (ds : List Decl) (σ : Values) (n : String)
    (h : n ∉ ds.map Decl.name) :
    ds.foldl (fun τ d m => if m = d.name then d.valueUnder τ else τ m) σ n = σ n := by
  induction ds generalizing σ with
  | nil => rfl
  | cons d rest ih =>
      simp only [List.map_cons, List.mem_cons, not_or] at h
      simp only [List.foldl_cons]
      rw [ih _ h.2]
      simp [h.1]

theorem values_missing (ds : List Decl) (n : String)
    (h : n ∉ ds.map Decl.name) : values ds n = none := by
  exact fold_values_other ds _ n h

theorem values_at (ds : List Decl) (hn : (ds.map Decl.name).Nodup)
    (d : Decl) (hd : d ∈ ds) :
    ∃ pre post : List Decl, ds = pre ++ d :: post ∧
      values ds d.name = d.valueUnder (values pre) := by
  obtain ⟨pre, post, hds⟩ := List.mem_iff_append.mp hd
  subst ds
  have hright : (d.name :: post.map Decl.name).Nodup := by
    exact (List.nodup_append.mp (by simpa [List.map_append] using hn)).2.1
  have hnot : d.name ∉ post.map Decl.name := (List.nodup_cons.mp hright).1
  refine ⟨pre, post, rfl, ?_⟩
  unfold values
  rw [List.foldl_append, List.foldl_cons]
  rw [fold_values_other post _ d.name hnot]
  simp [values]

theorem values_stated (ds : List Decl) (h : WellFormed ds) (d : Decl)
    (hd : d ∈ ds) (q : Rat) (hs : d.source = .stated q) :
    values ds d.name = some q := by
  obtain ⟨_, _, _, hv⟩ := values_at ds h.1 d hd
  simpa [Decl.valueUnder, hs] using hv

theorem values_free (ds : List Decl) (h : WellFormed ds) (d : Decl)
    (hd : d ∈ ds) (hs : d.source = .free) :
    values ds d.name = none := by
  obtain ⟨_, _, _, hv⟩ := values_at ds h.1 d hd
  simpa [Decl.valueUnder, hs] using hv

theorem values_counted (ds : List Decl) (h : WellFormed ds) (d : Decl)
    (hd : d ∈ ds) (q : Thunk (Option Rat)) (r : Counted)
    (hs : d.source = .counted q r) : values ds d.name = q.get := by
  obtain ⟨_, _, _, hv⟩ := values_at ds h.1 d hd
  simpa [Decl.valueUnder, hs] using hv

theorem Expr.eval_congr_on (e : Expr) (σ τ : Values)
    (h : ∀ n ∈ e.names, σ n = τ n) : e.eval σ = e.eval τ := by
  induction e with
  | lit _ => rfl
  | val n => exact h n (by simp [Expr.names])
  | add a b iha ihb =>
      have ha := iha (by intro n hn; exact h n (by simp [Expr.names, hn]))
      have hb := ihb (by intro n hn; exact h n (by simp [Expr.names, hn]))
      simp [Expr.eval, ha, hb]
  | sub a b iha ihb =>
      have ha := iha (by intro n hn; exact h n (by simp [Expr.names, hn]))
      have hb := ihb (by intro n hn; exact h n (by simp [Expr.names, hn]))
      simp [Expr.eval, ha, hb]
  | mul a b iha ihb =>
      have ha := iha (by intro n hn; exact h n (by simp [Expr.names, hn]))
      have hb := ihb (by intro n hn; exact h n (by simp [Expr.names, hn]))
      simp [Expr.eval, ha, hb]
  | div a b iha ihb =>
      have ha := iha (by intro n hn; exact h n (by simp [Expr.names, hn]))
      have hb := ihb (by intro n hn; exact h n (by simp [Expr.names, hn]))
      simp [Expr.eval, ha, hb]
  | pow a k iha =>
      have ha := iha (by intro n hn; exact h n (by simp [Expr.names, hn]))
      simp [Expr.eval, ha]

theorem values_defined (ds : List Decl) (h : WellFormed ds) (d : Decl)
    (hd : d ∈ ds) (e : Expr) (hs : d.source = .defined e) (q : Rat) :
    values ds d.name = some q ↔ Denotes (values ds) e q := by
  obtain ⟨pre, post, hds, hv⟩ := values_at ds h.1 d hd
  subst ds
  have hi : pre.length < (pre ++ d :: post).length := by simp
  have hsource : ((pre ++ d :: post)[pre.length]'hi).source = .defined e := by
    simpa using hs
  have hbefore := h.2.1 pre.length hi e hsource
  have hnames : ∀ n ∈ e.names, n ∈ pre.map Decl.name := by
    simpa using hbefore
  have hdisj := (List.nodup_append.mp
    (by simpa [List.map_append] using h.1)).2.2
  have hval : ∀ n ∈ pre.map Decl.name,
      values (pre ++ d :: post) n = values pre n := by
    intro n hn
    have hnot : n ∉ (d :: post).map Decl.name := by
      intro hm
      exact hdisj n hn n hm rfl
    unfold values
    rw [List.foldl_append]
    exact fold_values_other (d :: post) _ n hnot
  have heval := Expr.eval_congr_on e (values (pre ++ d :: post)) (values pre)
    (by intro n hn; exact hval n (hnames n hn))
  rw [hv]
  simp only [Decl.valueUnder, hs]
  rw [← heval]
  exact Expr.eval_iff _ _ _

def maxDigits : Nat := 4096
def digitCount (n : Nat) : Nat := (Nat.toDigits 10 n).length
def Small (q : Rat) : Prop :=
  digitCount q.num.natAbs ≤ maxDigits ∧ digitCount q.den ≤ maxDigits

theorem toDigitsCore_length_ge (fuel n : Nat) (ds : List Char) (hf : 0 < fuel) :
    ds.length + 1 ≤ (Nat.toDigitsCore 10 fuel n ds).length := by
  induction fuel generalizing n ds with
  | zero => omega
  | succ fuel ih =>
    unfold Nat.toDigitsCore
    dsimp only
    split
    · simp
    · cases fuel with
      | zero => simp [Nat.toDigitsCore]
      | succ f => have := ih (n / 10) ((n % 10).digitChar :: ds) (by omega); simp at this; omega

theorem toDigitsCore_le_iff (fuel n k : Nat) (ds : List Char) (hn : n < fuel) :
    (Nat.toDigitsCore 10 fuel n ds).length ≤ ds.length + (k + 1) ↔ n < 10 ^ (k + 1) := by
  induction fuel generalizing n k ds with
  | zero => omega
  | succ fuel ih =>
    unfold Nat.toDigitsCore
    dsimp only
    split
    · simp only [List.length_cons]
      have : 10 ≤ 10 ^ (k + 1) := Nat.le_self_pow (by omega) _
      constructor <;> intro <;> omega
    · have hlt : n / 10 < fuel := by omega
      cases k with
      | zero =>
        have := toDigitsCore_length_ge fuel (n / 10) ((n % 10).digitChar :: ds) (by omega)
        simp only [List.length_cons] at this
        constructor <;> intro <;> omega
      | succ k =>
        have := ih (n / 10) k ((n % 10).digitChar :: ds) hlt
        simp only [List.length_cons] at this
        rw [show ds.length + (k + 1 + 1) = ds.length + 1 + (k + 1) by omega, this, Nat.div_lt_iff_lt_mul (by omega),
          Nat.pow_succ 10 (k + 1)]

set_option exponentiation.threshold 4096 in
/-- 2.4's digit limit as one comparison (3.2 (b)): no digit list is built. -/
theorem digitCount_le_iff (n : Nat) : digitCount n ≤ maxDigits ↔ n < 10 ^ maxDigits := by
  exact toDigitsCore_le_iff (n + 1) n 4095 [] (by omega)

/-- `10 ^ maxDigits`, the least value of more than `maxDigits` digits; irreducible, so no proof unfolds the power. -/
@[irreducible] def digitBound : Nat := 10 ^ maxDigits

/-- `Small` by two comparisons (`digitCount_le_iff`): every `Val.guard` is decided without a digit list. -/
instance (q : Rat) : Decidable (Small q) :=
  decidable_of_iff (q.num.natAbs < digitBound ∧ q.den < digitBound) (by
    simp only [Small, digitCount_le_iff]; unfold digitBound; exact Iff.rfl)

inductive Val where
  | ok (q : Rat) | undefined | tooLarge | exhausted
  deriving Repr, DecidableEq

def Val.guard (q : Rat) : Val := if Small q then .ok q else .tooLarge

def Val.bin (f : Rat → Rat → Val) : Val → Val → Val
  | .ok x, .ok y => f x y
  | .ok _, v => v
  | v, _ => v

def Val.all : List Val → Except Val (List Rat)
  | [] => .ok []
  | .ok q :: vs => (Val.all vs).map (q :: ·)
  | v :: _ => .error v

def Expr.evalL (τ : String → Val) : Expr → Val
  | .lit q => Val.guard q
  | .val n => τ n
  | .add a b => Val.bin (fun x y => Val.guard (x + y)) (a.evalL τ) (b.evalL τ)
  | .sub a b => Val.bin (fun x y => Val.guard (x - y)) (a.evalL τ) (b.evalL τ)
  | .mul a b => Val.bin (fun x y => Val.guard (x * y)) (a.evalL τ) (b.evalL τ)
  | .div a b => Val.bin (fun x y => if y = 0 then .undefined else Val.guard (x / y))
      (a.evalL τ) (b.evalL τ)
  | .pow a k => match a.evalL τ with
    | .ok x => Val.guard (x ^ k)
    | v => v

private def Val.Agrees (v : Val) (w : Option Rat) : Prop :=
  match v with
  | .ok q => w = some q
  | .undefined => w = none
  | .tooLarge | .exhausted => True

theorem Val.guard_agrees (q : Rat) : (Val.guard q).Agrees (some q) := by
  by_cases hs : Small q <;> simp [Val.guard, Val.Agrees, hs]

theorem Val.div_agrees (x y : Rat) :
    (if y = 0 then Val.undefined else Val.guard (x / y)).Agrees
      (if y = 0 then none else some (x / y)) := by
  by_cases hy : y = 0
  · simp [hy, Val.Agrees]
  · simpa [hy] using Val.guard_agrees (x / y)

theorem Expr.evalL_agrees (e : Expr) (τ : String → Val) (σ : Values)
    (h : ∀ n, (τ n).Agrees (σ n)) : (e.evalL τ).Agrees (e.eval σ) := by
  induction e with
  | lit q => exact Val.guard_agrees q
  | val n => exact h n
  | add a b iha ihb =>
      have ha := iha
      have hb := ihb
      cases va : a.evalL τ <;> cases vb : b.evalL τ <;>
        simp_all [Expr.evalL, Expr.eval, Val.bin, Val.Agrees] <;>
        simpa [Val.Agrees] using (Val.guard_agrees _)
  | sub a b iha ihb =>
      have ha := iha
      have hb := ihb
      cases va : a.evalL τ <;> cases vb : b.evalL τ <;>
        simp_all [Expr.evalL, Expr.eval, Val.bin, Val.Agrees] <;>
        simpa [Val.Agrees] using (Val.guard_agrees _)
  | mul a b iha ihb =>
      have ha := iha
      have hb := ihb
      cases va : a.evalL τ <;> cases vb : b.evalL τ <;>
        simp_all [Expr.evalL, Expr.eval, Val.bin, Val.Agrees] <;>
        simpa [Val.Agrees] using (Val.guard_agrees _)
  | div a b iha ihb =>
      have ha := iha
      have hb := ihb
      cases va : a.evalL τ <;> cases vb : b.evalL τ <;>
        simp_all [Expr.evalL, Expr.eval, Val.bin, Val.Agrees] <;>
        simpa [Val.Agrees] using (Val.div_agrees _ _)
  | pow a k iha =>
      have ha := iha
      cases va : a.evalL τ <;>
        simp_all [Expr.evalL, Expr.eval, Val.Agrees] <;>
        simpa [Val.Agrees] using (Val.guard_agrees _)

def Decl.valL (d : Decl) (τ : String → Val) : Val :=
  match d.source with
  | .stated q => Val.guard q
  | .defined e => e.evalL τ
  | .free => .undefined
  | .counted _ (.ok (some q)) => Val.guard q
  | .counted _ (.ok none) => .undefined
  | .counted _ .exhausted => .exhausted

def valuesL (ds : List Decl) : String → Val :=
  ds.foldl (fun τ d n => if n = d.name then d.valL τ else τ n) (fun _ => .undefined)

theorem Decl.valL_agrees (d : Decl) (τ : String → Val) (σ : Values)
    (h : ∀ n, (τ n).Agrees (σ n))
    (hc : ∀ q v, d.source = .counted q (.ok v) → q.get = v) :
    (d.valL τ).Agrees (d.valueUnder σ) := by
  cases hs : d.source with
  | stated q => simpa [Decl.valL, Decl.valueUnder, hs] using Val.guard_agrees q
  | defined e => simpa [Decl.valL, Decl.valueUnder, hs] using Expr.evalL_agrees e τ σ h
  | free => simp [Decl.valL, Decl.valueUnder, Val.Agrees, hs]
  | counted q r =>
      cases r with
      | exhausted => simp [Decl.valL, Decl.valueUnder, Val.Agrees, hs]
      | ok v =>
          have hv : q.get = v := hc q v hs
          cases v with
          | none => simp [Decl.valL, Decl.valueUnder, Val.Agrees, hs, hv]
          | some x => simpa [Decl.valL, Decl.valueUnder, hs, hv] using Val.guard_agrees x

theorem fold_valuesL_agrees (ds : List Decl) (τ : String → Val) (σ : Values)
    (h : ∀ n, (τ n).Agrees (σ n))
    (hc : ∀ d ∈ ds, ∀ q v, d.source = .counted q (.ok v) → q.get = v) :
    ∀ n, ((ds.foldl (fun τ d n => if n = d.name then d.valL τ else τ n) τ) n).Agrees
      ((ds.foldl (fun σ d n => if n = d.name then d.valueUnder σ else σ n) σ) n) := by
  induction ds generalizing τ σ with
  | nil => exact h
  | cons d rest ih =>
      simp only [List.foldl_cons]
      apply ih
      · intro n
        by_cases hn : n = d.name
        · simpa [hn] using Decl.valL_agrees d τ σ h (by
            intro q v hs; exact hc d (by simp) q v hs)
        · simpa [hn] using h n
      · intro d' hd' q v hs
        exact hc d' (by simp [hd']) q v hs

theorem valuesL_agrees (ds : List Decl) (h : WellFormed ds) (n : String) :
    (valuesL ds n).Agrees (values ds n) := by
  unfold valuesL values
  exact fold_valuesL_agrees ds _ _ (by intro _; simp [Val.Agrees]) h.2.2 n

def firstFault : List Val → Option Val
  | [] => none
  | .ok _ :: vs => firstFault vs
  | v :: _ => some v

def Claim.run (ds : List Decl) (c : Claim) : Outcome :=
  match firstFault (c.exprs.map (Expr.evalL (valuesL ds))) with
  | some .tooLarge => .unknown (.limit .digits)
  | some .exhausted => .unknown (.limit .evaluations)
  | some _ => .decided .undefined
  | none => .decided (c.decide (values ds))

inductive NameOverflows (ds : List Decl) : String → Prop
  | here {n : String} {e : Expr} :
      (∃ d ∈ ds, d.name = n ∧ d.source = .defined e) →
      (∃ e' ∈ e.subexprs, ∃ q, Denotes (values ds) e' q ∧ ¬ Small q) → NameOverflows ds n
  | dep {n m : String} {e : Expr} :
      (∃ d ∈ ds, d.name = n ∧ d.source = .defined e) → m ∈ e.names →
      NameOverflows ds m → NameOverflows ds n

def Expr.Overflows (ds : List Decl) (e : Expr) : Prop :=
  (∃ e' ∈ e.subexprs, ∃ q, Denotes (values ds) e' q ∧ ¬ Small q) ∨
    ∃ m ∈ e.names, NameOverflows ds m

def Claim.Overflows (ds : List Decl) (c : Claim) : Prop :=
  ∃ e ∈ c.exprs, e.Overflows ds

inductive NameExhausted (ds : List Decl) : String → Prop
  | here {n : String} {q : Thunk (Option Rat)} :
      (∃ d ∈ ds, d.name = n ∧ d.source = .counted q .exhausted) → NameExhausted ds n
  | dep {n m : String} {e : Expr} :
      (∃ d ∈ ds, d.name = n ∧ d.source = .defined e) → m ∈ e.names →
      NameExhausted ds m → NameExhausted ds n

def Expr.ReadsExhausted (ds : List Decl) (e : Expr) : Prop :=
  ∃ m ∈ e.names, NameExhausted ds m

def Claim.ReadsExhausted (ds : List Decl) (c : Claim) : Prop :=
  ∃ e ∈ c.exprs, e.ReadsExhausted ds

theorem Expr.overflow_lift (ds : List Decl) (parent child : Expr)
    (hsub : ∀ e ∈ child.subexprs, e ∈ parent.subexprs)
    (hnames : ∀ n ∈ child.names, n ∈ parent.names)
    (h : child.Overflows ds) : parent.Overflows ds := by
  rcases h with ⟨e, he, q, hq, hbig⟩ | ⟨n, hn, hc⟩
  · exact Or.inl ⟨e, hsub e he, q, hq, hbig⟩
  · exact Or.inr ⟨n, hnames n hn, hc⟩

theorem Expr.exhausted_lift (ds : List Decl) (parent child : Expr)
    (hnames : ∀ n ∈ child.names, n ∈ parent.names)
    (h : child.ReadsExhausted ds) : parent.ReadsExhausted ds := by
  obtain ⟨n, hn, hc⟩ := h
  exact ⟨n, hnames n hn, hc⟩

theorem Val.bin_tooLarge (f : Rat → Rat → Val) (a b : Val)
    (h : Val.bin f a b = .tooLarge) :
    a = .tooLarge ∨
      ∃ x, a = .ok x ∧ (b = .tooLarge ∨ ∃ y, b = .ok y ∧ f x y = .tooLarge) := by
  cases a <;> cases b <;> simp_all [Val.bin]

theorem Val.bin_exhausted (f : Rat → Rat → Val) (a b : Val)
    (hf : ∀ x y, f x y ≠ .exhausted)
    (h : Val.bin f a b = .exhausted) :
    a = .exhausted ∨ ∃ x, a = .ok x ∧ b = .exhausted := by
  cases a <;> cases b <;> simp_all [Val.bin]

theorem Expr.evalL_causes (ds : List Decl) (e : Expr) (τ : String → Val)
    (hagrees : ∀ n, (τ n).Agrees (values ds n))
    (hlarge : ∀ n, τ n = .tooLarge →
      (∃ q, values ds n = some q ∧ ¬ Small q) ∨ NameOverflows ds n)
    (hexhausted : ∀ n, τ n = .exhausted → NameExhausted ds n) :
    (e.evalL τ = .tooLarge → e.Overflows ds) ∧
      (e.evalL τ = .exhausted → e.ReadsExhausted ds) := by
  induction e with
  | lit q =>
      constructor
      · intro hv
        have hbig : ¬ Small q := by
          simp [Expr.evalL, Val.guard] at hv
          exact hv
        exact Or.inl ⟨.lit q, by simp [Expr.subexprs], q, Denotes.lit, hbig⟩
      · intro hv
        by_cases hs : Small q <;> simp [Expr.evalL, Val.guard, hs] at hv
  | val n =>
      constructor
      · intro hv
        rcases hlarge n hv with ⟨q, hq, hbig⟩ | hc
        · exact Or.inl ⟨.val n, by simp [Expr.subexprs], q, Denotes.val hq, hbig⟩
        · exact Or.inr ⟨n, by simp [Expr.names], hc⟩
      · intro hv
        exact ⟨n, by simp [Expr.names], hexhausted n hv⟩
  | add a b iha ihb =>
      have hleftSub : ∀ t ∈ a.subexprs, t ∈ (Expr.add a b).subexprs := by
        intro t ht
        simp [Expr.subexprs, ht]
      have hrightSub : ∀ t ∈ b.subexprs, t ∈ (Expr.add a b).subexprs := by
        intro t ht
        simp [Expr.subexprs, ht]
      have hleftNames : ∀ n ∈ a.names, n ∈ (Expr.add a b).names := by
        intro n hn
        simp [Expr.names, hn]
      have hrightNames : ∀ n ∈ b.names, n ∈ (Expr.add a b).names := by
        intro n hn
        simp [Expr.names, hn]
      constructor
      · intro hv
        have hc := Val.bin_tooLarge _ _ _ hv
        rcases hc with ha | ⟨x, ha, hc⟩
        · exact Expr.overflow_lift ds _ _ hleftSub hleftNames (iha.1 ha)
        rcases hc with hb | ⟨y, hb, hguard⟩
        · exact Expr.overflow_lift ds _ _ hrightSub hrightNames (ihb.1 hb)
        · have hax : a.eval (values ds) = some x := by
            have h := Expr.evalL_agrees a τ (values ds) hagrees
            rw [ha] at h
            exact h
          have hby : b.eval (values ds) = some y := by
            have h := Expr.evalL_agrees b τ (values ds) hagrees
            rw [hb] at h
            exact h
          have hbig : ¬ Small (x + y) := by
            simp [Val.guard] at hguard
            exact hguard
          exact Or.inl ⟨.add a b, by simp [Expr.subexprs], x + y,
            Denotes.add ((Expr.eval_iff _ _ _).mp hax)
              ((Expr.eval_iff _ _ _).mp hby), hbig⟩
      · intro hv
        have hf : ∀ x y, Val.guard (x + y) ≠ .exhausted := by
          intro x y; simp [Val.guard]; split <;> simp
        have hc := Val.bin_exhausted _ _ _ hf hv
        rcases hc with ha | ⟨x, ha, hb⟩
        · exact Expr.exhausted_lift ds _ _ hleftNames (iha.2 ha)
        · exact Expr.exhausted_lift ds _ _ hrightNames (ihb.2 hb)
  | pow a k iha =>
      have hsub : ∀ t ∈ a.subexprs, t ∈ (Expr.pow a k).subexprs := by
        intro t ht; simp [Expr.subexprs, ht]
      have hnames : ∀ n ∈ a.names, n ∈ (Expr.pow a k).names := by
        intro n hn; simpa [Expr.names] using hn
      constructor
      · intro hv
        cases ha : a.evalL τ with
        | tooLarge => exact Expr.overflow_lift ds _ _ hsub hnames (iha.1 ha)
        | exhausted | undefined => simp [Expr.evalL, ha] at hv
        | ok x =>
            have hax : a.eval (values ds) = some x := by
              have h := Expr.evalL_agrees a τ (values ds) hagrees
              rw [ha] at h
              exact h
            have hbig : ¬ Small (x ^ k) := by
              simp [Expr.evalL, ha, Val.guard] at hv
              exact hv
            exact Or.inl ⟨.pow a k, by simp [Expr.subexprs], x ^ k,
              Denotes.pow ((Expr.eval_iff _ _ _).mp hax), hbig⟩
      · intro hv
        cases ha : a.evalL τ with
        | exhausted => exact Expr.exhausted_lift ds _ _ hnames (iha.2 ha)
        | tooLarge | undefined => simp [Expr.evalL, ha] at hv
        | ok x =>
            by_cases hs : Small (x ^ k) <;>
              simp [Expr.evalL, ha, Val.guard, hs] at hv

  | sub a b iha ihb =>
      have hleftSub : ∀ t ∈ a.subexprs, t ∈ (Expr.sub a b).subexprs := by
        intro t ht
        simp [Expr.subexprs, ht]
      have hrightSub : ∀ t ∈ b.subexprs, t ∈ (Expr.sub a b).subexprs := by
        intro t ht
        simp [Expr.subexprs, ht]
      have hleftNames : ∀ n ∈ a.names, n ∈ (Expr.sub a b).names := by
        intro n hn
        simp [Expr.names, hn]
      have hrightNames : ∀ n ∈ b.names, n ∈ (Expr.sub a b).names := by
        intro n hn
        simp [Expr.names, hn]
      constructor
      · intro hv
        have hc := Val.bin_tooLarge _ _ _ hv
        rcases hc with ha | ⟨x, ha, hc⟩
        · exact Expr.overflow_lift ds _ _ hleftSub hleftNames (iha.1 ha)
        rcases hc with hb | ⟨y, hb, hguard⟩
        · exact Expr.overflow_lift ds _ _ hrightSub hrightNames (ihb.1 hb)
        · have hax : a.eval (values ds) = some x := by
            have h := Expr.evalL_agrees a τ (values ds) hagrees
            rw [ha] at h
            exact h
          have hby : b.eval (values ds) = some y := by
            have h := Expr.evalL_agrees b τ (values ds) hagrees
            rw [hb] at h
            exact h
          have hbig : ¬ Small (x - y) := by
            simp [Val.guard] at hguard
            exact hguard
          exact Or.inl ⟨.sub a b, by simp [Expr.subexprs], x - y,
            Denotes.sub ((Expr.eval_iff _ _ _).mp hax)
              ((Expr.eval_iff _ _ _).mp hby), hbig⟩
      · intro hv
        have hf : ∀ x y, Val.guard (x - y) ≠ .exhausted := by
          intro x y; simp [Val.guard]; split <;> simp
        have hc := Val.bin_exhausted _ _ _ hf hv
        rcases hc with ha | ⟨x, ha, hb⟩
        · exact Expr.exhausted_lift ds _ _ hleftNames (iha.2 ha)
        · exact Expr.exhausted_lift ds _ _ hrightNames (ihb.2 hb)
  | mul a b iha ihb =>
      have hleftSub : ∀ t ∈ a.subexprs, t ∈ (Expr.mul a b).subexprs := by
        intro t ht
        simp [Expr.subexprs, ht]
      have hrightSub : ∀ t ∈ b.subexprs, t ∈ (Expr.mul a b).subexprs := by
        intro t ht
        simp [Expr.subexprs, ht]
      have hleftNames : ∀ n ∈ a.names, n ∈ (Expr.mul a b).names := by
        intro n hn
        simp [Expr.names, hn]
      have hrightNames : ∀ n ∈ b.names, n ∈ (Expr.mul a b).names := by
        intro n hn
        simp [Expr.names, hn]
      constructor
      · intro hv
        have hc := Val.bin_tooLarge _ _ _ hv
        rcases hc with ha | ⟨x, ha, hc⟩
        · exact Expr.overflow_lift ds _ _ hleftSub hleftNames (iha.1 ha)
        rcases hc with hb | ⟨y, hb, hguard⟩
        · exact Expr.overflow_lift ds _ _ hrightSub hrightNames (ihb.1 hb)
        · have hax : a.eval (values ds) = some x := by
            have h := Expr.evalL_agrees a τ (values ds) hagrees
            rw [ha] at h
            exact h
          have hby : b.eval (values ds) = some y := by
            have h := Expr.evalL_agrees b τ (values ds) hagrees
            rw [hb] at h
            exact h
          have hbig : ¬ Small (x * y) := by
            simp [Val.guard] at hguard
            exact hguard
          exact Or.inl ⟨.mul a b, by simp [Expr.subexprs], x * y,
            Denotes.mul ((Expr.eval_iff _ _ _).mp hax)
              ((Expr.eval_iff _ _ _).mp hby), hbig⟩
      · intro hv
        have hf : ∀ x y, Val.guard (x * y) ≠ .exhausted := by
          intro x y; simp [Val.guard]; split <;> simp
        have hc := Val.bin_exhausted _ _ _ hf hv
        rcases hc with ha | ⟨x, ha, hb⟩
        · exact Expr.exhausted_lift ds _ _ hleftNames (iha.2 ha)
        · exact Expr.exhausted_lift ds _ _ hrightNames (ihb.2 hb)

  | div a b iha ihb =>
      have hleftSub : ∀ t ∈ a.subexprs, t ∈ (Expr.div a b).subexprs := by
        intro t ht
        simp [Expr.subexprs, ht]
      have hrightSub : ∀ t ∈ b.subexprs, t ∈ (Expr.div a b).subexprs := by
        intro t ht
        simp [Expr.subexprs, ht]
      have hleftNames : ∀ n ∈ a.names, n ∈ (Expr.div a b).names := by
        intro n hn
        simp [Expr.names, hn]
      have hrightNames : ∀ n ∈ b.names, n ∈ (Expr.div a b).names := by
        intro n hn
        simp [Expr.names, hn]
      constructor
      · intro hv
        have hc := Val.bin_tooLarge _ _ _ hv
        rcases hc with ha | ⟨x, ha, hc⟩
        · exact Expr.overflow_lift ds _ _ hleftSub hleftNames (iha.1 ha)
        rcases hc with hb | ⟨y, hb, hguard⟩
        · exact Expr.overflow_lift ds _ _ hrightSub hrightNames (ihb.1 hb)
        · have hax : a.eval (values ds) = some x := by
            have h := Expr.evalL_agrees a τ (values ds) hagrees
            rw [ha] at h
            exact h
          have hby : b.eval (values ds) = some y := by
            have h := Expr.evalL_agrees b τ (values ds) hagrees
            rw [hb] at h
            exact h
          have hy : y ≠ 0 := by
            intro hz
            simp [hz] at hguard
          have hbig : ¬ Small (x / y) := by
            simp [hy, Val.guard] at hguard
            exact hguard
          exact Or.inl ⟨.div a b, by simp [Expr.subexprs], x / y,
            Denotes.div ((Expr.eval_iff _ _ _).mp hax)
              ((Expr.eval_iff _ _ _).mp hby) hy, hbig⟩
      · intro hv
        have hf : ∀ x y,
            (if y = 0 then Val.undefined else Val.guard (x / y)) ≠ .exhausted := by
          intro x y
          by_cases hy : y = 0 <;> simp [hy, Val.guard] <;> split <;> simp
        have hc := Val.bin_exhausted _ _ _ hf hv
        rcases hc with ha | ⟨x, ha, hb⟩
        · exact Expr.exhausted_lift ds _ _ hleftNames (iha.2 ha)
        · exact Expr.exhausted_lift ds _ _ hrightNames (ihb.2 hb)

theorem Expr.evalL_congr_on (e : Expr) (τ υ : String → Val)
    (h : ∀ n ∈ e.names, τ n = υ n) : e.evalL τ = e.evalL υ := by
  induction e with
  | lit _ => rfl
  | val n => exact h n (by simp [Expr.names])
  | add a b iha ihb =>
      have ha := iha (by intro n hn; exact h n (by simp [Expr.names, hn]))
      have hb := ihb (by intro n hn; exact h n (by simp [Expr.names, hn]))
      simp [Expr.evalL, ha, hb]

  | sub a b iha ihb =>
      have ha := iha (by intro n hn; exact h n (by simp [Expr.names, hn]))
      have hb := ihb (by intro n hn; exact h n (by simp [Expr.names, hn]))
      simp [Expr.evalL, ha, hb]
  | mul a b iha ihb =>
      have ha := iha (by intro n hn; exact h n (by simp [Expr.names, hn]))
      have hb := ihb (by intro n hn; exact h n (by simp [Expr.names, hn]))
      simp [Expr.evalL, ha, hb]
  | div a b iha ihb =>
      have ha := iha (by intro n hn; exact h n (by simp [Expr.names, hn]))
      have hb := ihb (by intro n hn; exact h n (by simp [Expr.names, hn]))
      simp [Expr.evalL, ha, hb]
  | pow a k iha =>
      have ha := iha (by intro n hn; exact h n (by simp [Expr.names, hn]))
      simp [Expr.evalL, ha]

theorem Expr.evalL_causes_on_names (ds : List Decl) (e : Expr) (τ : String → Val)
    (hagrees : ∀ n ∈ e.names, (τ n).Agrees (values ds n))
    (hlarge : ∀ n ∈ e.names, τ n = .tooLarge →
      (∃ q, values ds n = some q ∧ ¬ Small q) ∨ NameOverflows ds n)
    (hexhausted : ∀ n ∈ e.names, τ n = .exhausted → NameExhausted ds n) :
    (e.evalL τ = .tooLarge → e.Overflows ds) ∧
      (e.evalL τ = .exhausted → e.ReadsExhausted ds) := by
  let υ : String → Val := fun n =>
    if n ∈ e.names then τ n else
      match values ds n with
      | some q => .ok q
      | none => .undefined
  have hc : e.evalL τ = e.evalL υ :=
    Expr.evalL_congr_on e τ υ (by intro n hn; simp [υ, hn])
  have ha : ∀ n, (υ n).Agrees (values ds n) := by
    intro n
    by_cases hn : n ∈ e.names
    · simpa [υ, hn] using hagrees n hn
    · cases hv : values ds n <;> simp [υ, hn, hv, Val.Agrees]
  have hl : ∀ n, υ n = .tooLarge →
      (∃ q, values ds n = some q ∧ ¬ Small q) ∨ NameOverflows ds n := by
    intro n hv
    by_cases hn : n ∈ e.names
    · exact hlarge n hn (by simpa [υ, hn] using hv)
    · cases hv' : values ds n <;> simp [υ, hn, hv'] at hv
  have he : ∀ n, υ n = .exhausted → NameExhausted ds n := by
    intro n hv
    by_cases hn : n ∈ e.names
    · exact hexhausted n hn (by simpa [υ, hn] using hv)
    · cases hv' : values ds n <;> simp [υ, hn, hv'] at hv
  have result := Expr.evalL_causes ds e υ ha hl he
  simpa [hc] using result

theorem values_append_prefix (pre rest : List Decl) (n : String)
    (hn : n ∉ rest.map Decl.name) :
    values (pre ++ rest) n = values pre n := by
  unfold values
  rw [List.foldl_append]
  exact fold_values_other rest _ n hn

private def CausesAt (ds : List Decl) (τ : String → Val) : Prop :=
  (∀ n, τ n = .tooLarge →
    (∃ q, values ds n = some q ∧ ¬ Small q) ∨ NameOverflows ds n) ∧
  (∀ n, τ n = .exhausted → NameExhausted ds n)

theorem causes_step (ds : List Decl) (h : WellFormed ds)
    (pre : List Decl) (d : Decl) (tail : List Decl)
    (hds : ds = pre ++ d :: tail) (hprev : CausesAt ds (valuesL pre)) :
    CausesAt ds (valuesL (pre ++ [d])) := by
  have hd : d ∈ ds := by rw [hds]; simp
  have hdisj := (List.nodup_append.mp
    (by simpa [hds, List.map_append] using h.1)).2.2
  have hnot (n : String) (hn : n ∈ pre.map Decl.name) :
      n ∉ (d :: tail).map Decl.name := by
    intro hm
    exact hdisj n hn n hm rfl
  have hcpre : ∀ d' ∈ pre, ∀ q v,
      d'.source = .counted q (.ok v) → q.get = v := by
    intro d' hd' q v hs
    exact h.2.2 d' (by rw [hds]; simp [hd']) q v hs
  have hagreePre : ∀ n, (valuesL pre n).Agrees (values pre n) := by
    unfold valuesL values
    exact fold_valuesL_agrees pre _ _ (by intro _; simp [Val.Agrees]) hcpre
  have hagreeFull (n : String) (hn : n ∈ pre.map Decl.name) :
      (valuesL pre n).Agrees (values ds n) := by
    rw [hds, values_append_prefix pre (d :: tail) n (hnot n hn)]
    exact hagreePre n
  have hupdate (n : String) :
      valuesL (pre ++ [d]) n =
        if n = d.name then d.valL (valuesL pre) else valuesL pre n := by
    simp [valuesL, List.foldl_append]
  have hi : pre.length < ds.length := by rw [hds]; simp
  have hsource (e : Expr) (hs : d.source = .defined e) :
      ∀ n ∈ e.names, n ∈ pre.map Decl.name := by
    have hget : (ds[pre.length]'hi).source = .defined e := by
      simpa [hds] using hs
    simpa [hds] using h.2.1 pre.length hi e hget
  constructor
  · intro n hv
    rw [hupdate] at hv
    by_cases hn : n = d.name
    · subst n
      simp only [if_true] at hv
      cases hs : d.source with
      | stated q =>
          have hbig : ¬ Small q := by
            simp [Decl.valL, hs, Val.guard] at hv
            exact hv
          exact Or.inl ⟨q, values_stated ds h d hd q hs, hbig⟩
      | defined e =>
          have hc := Expr.evalL_causes_on_names ds e (valuesL pre)
            (by intro n hn; exact hagreeFull n (hsource e hs n hn))
            (by intro n _ hv; exact hprev.1 n hv)
            (by intro n _ hv; exact hprev.2 n hv)
          have he : e.Overflows ds := hc.1 (by simpa [Decl.valL, hs] using hv)
          rcases he with direct | ⟨m, hm, cause⟩
          · exact Or.inr (NameOverflows.here ⟨d, hd, rfl, hs⟩ direct)
          · exact Or.inr (NameOverflows.dep ⟨d, hd, rfl, hs⟩ hm cause)
      | free => simp [Decl.valL, hs] at hv
      | counted q result =>
          cases result with
          | exhausted => simp [Decl.valL, hs] at hv
          | ok v =>
              cases v with
              | none => simp [Decl.valL, hs] at hv
              | some x =>
                  have hbig : ¬ Small x := by
                    simp [Decl.valL, hs, Val.guard] at hv
                    exact hv
                  have hq : q.get = some x := h.2.2 d hd q (.some x) hs
                  exact Or.inl ⟨x, by simpa [hq] using values_counted ds h d hd q (.ok (.some x)) hs,
                    hbig⟩
    · simp only [if_neg hn] at hv
      exact hprev.1 n hv
  · intro n hv
    rw [hupdate] at hv
    by_cases hn : n = d.name
    · subst n
      simp only [if_true] at hv
      cases hs : d.source with
      | stated q =>
          by_cases hs' : Small q <;> simp [Decl.valL, hs, Val.guard, hs'] at hv
      | defined e =>
          have hc := Expr.evalL_causes_on_names ds e (valuesL pre)
            (by intro n hn; exact hagreeFull n (hsource e hs n hn))
            (by intro n _ hv; exact hprev.1 n hv)
            (by intro n _ hv; exact hprev.2 n hv)
          obtain ⟨m, hm, cause⟩ := hc.2 (by simpa [Decl.valL, hs] using hv)
          exact NameExhausted.dep ⟨d, hd, rfl, hs⟩ hm cause
      | free => simp [Decl.valL, hs] at hv
      | counted q result =>
          cases result with
          | exhausted => exact NameExhausted.here ⟨d, hd, rfl, hs⟩
          | ok v =>
              cases v with
              | none => simp [Decl.valL, hs] at hv
              | some x =>
                  by_cases hs' : Small x <;>
                    simp [Decl.valL, hs, Val.guard, hs'] at hv
    · simp only [if_neg hn] at hv
      exact hprev.2 n hv

theorem causes_accumulate (ds : List Decl) (h : WellFormed ds)
    (pre rest : List Decl) :
    ds = pre ++ rest → CausesAt ds (valuesL pre) →
      CausesAt ds (valuesL (pre ++ rest)) := by
  induction rest generalizing pre with
  | nil =>
      intro _ hp
      simpa using hp
  | cons d tail ih =>
      intro hds hp
      have hs := causes_step ds h pre d tail hds hp
      have hds' : ds = (pre ++ [d]) ++ tail := by
        simpa [List.append_assoc] using hds
      have result := ih (pre ++ [d]) hds' hs
      simpa [List.append_assoc] using result

theorem valuesL_causes (ds : List Decl) (h : WellFormed ds) :
    CausesAt ds (valuesL ds) := by
  have hb : CausesAt ds (valuesL []) := by
    constructor
    · intro n hv; simp [valuesL] at hv
    · intro n hv; simp [valuesL] at hv
  simpa using causes_accumulate ds h [] ds (by simp) hb
inductive FindingKind where
  | source | transcriptionUnchecked | softwareUnreproduced
  deriving Repr, DecidableEq

def findingKind (software : Option String) (checks : List Bool) : FindingKind :=
  if software.isSome then .softwareUnreproduced
  else if checks ≠ [] ∧ checks.all id then .source
  else .transcriptionUnchecked

theorem findingKind_source_iff (software : Option String) (checks : List Bool) :
    findingKind software checks = .source ↔
      software = none ∧ checks ≠ [] ∧ ∀ b ∈ checks, b = true := by
  cases software <;> simp [findingKind, List.all_eq_true]

theorem firstFault_mem (vs : List Val) (v : Val)
    (h : firstFault vs = some v) : v ∈ vs := by
  induction vs with
  | nil => simp [firstFault] at h
  | cons w rest ih =>
      cases w with
      | ok _ => exact List.mem_cons_of_mem _ (ih h)
      | undefined | tooLarge | exhausted =>
          simp only [firstFault, Option.some.injEq] at h
          subst v
          simp

theorem firstFault_not_ok (vs : List Val) (q : Rat) :
    firstFault vs ≠ some (.ok q) := by
  induction vs with
  | nil => simp [firstFault]
  | cons w rest ih =>
      cases w <;> simp [firstFault, ih]

theorem Claim.run_decided (ds : List Decl) (h : WellFormed ds) (c : Claim)
    (v : Verdict) (hr : c.run ds = .decided v) : v = c.decide (values ds) := by
  unfold Claim.run at hr
  cases hf : firstFault (c.exprs.map (Expr.evalL (valuesL ds))) with
  | none => simpa [hf] using hr.symm
  | some fault =>
      cases fault with
      | tooLarge => simp [hf] at hr
      | exhausted => simp [hf] at hr
      | ok q => exact False.elim ((firstFault_not_ok _ q) hf)
      | undefined =>
          have hm := firstFault_mem _ .undefined hf
          obtain ⟨e, he, hev⟩ := List.mem_map.mp hm
          have hrel := Expr.evalL_agrees e (valuesL ds) (values ds)
            (valuesL_agrees ds h)
          rw [hev] at hrel
          have heval : e.eval (values ds) = none := hrel
          have hnd : ¬ c.Defined (values ds) := by
            intro hd
            obtain ⟨q, hq⟩ := hd e he
            have := (Expr.eval_iff _ _ _).mpr hq
            simp [heval] at this
          have hv := (Claim.decide_undefined (values ds) c).mpr hnd
          simpa [hf, hv] using hr.symm

theorem Claim.run_unknown (ds : List Decl) (h : WellFormed ds) (c : Claim)
    (u : UnknownReason) (hr : c.run ds = .unknown u) :
    (u = .limit .digits ∧ c.Overflows ds) ∨
      (u = .limit .evaluations ∧ c.ReadsExhausted ds) := by
  have causes := valuesL_causes ds h
  unfold Claim.run at hr
  cases hf : firstFault (c.exprs.map (Expr.evalL (valuesL ds))) with
  | none => simp [hf] at hr
  | some fault =>
      cases fault with
      | ok q => exact False.elim ((firstFault_not_ok _ q) hf)
      | undefined => simp [hf] at hr
      | tooLarge =>
          have hm := firstFault_mem _ .tooLarge hf
          obtain ⟨e, he, hev⟩ := List.mem_map.mp hm
          have hc := Expr.evalL_causes ds e (valuesL ds)
            (by intro n; exact valuesL_agrees ds h n) causes.1 causes.2
          have hover : c.Overflows ds := ⟨e, he, hc.1 hev⟩
          have hu : u = .limit .digits := by simpa [hf] using hr.symm
          exact Or.inl ⟨hu, hover⟩
      | exhausted =>
          have hm := firstFault_mem _ .exhausted hf
          obtain ⟨e, he, hev⟩ := List.mem_map.mp hm
          have hc := Expr.evalL_causes ds e (valuesL ds)
            (by intro n; exact valuesL_agrees ds h n) causes.1 causes.2
          have hread : c.ReadsExhausted ds := ⟨e, he, hc.2 hev⟩
          have hu : u = .limit .evaluations := by simpa [hf] using hr.symm
          exact Or.inr ⟨hu, hread⟩

theorem Claim.run_complete (ds : List Decl) (h : WellFormed ds) (c : Claim)
    (hc : ¬ c.Overflows ds) (he : ¬ c.ReadsExhausted ds) :
    c.run ds = .decided (c.decide (values ds)) := by
  cases hr : c.run ds with
  | decided v =>
      have hv := Claim.run_decided ds h c v hr
      simpa [hr, hv]
  | unknown u =>
      have hu := Claim.run_unknown ds h c u hr
      rcases hu with ⟨_, hover⟩ | ⟨_, hread⟩
      · exact False.elim (hc hover)
      · exact False.elim (he hread)

namespace Work

/-! ## The work of a case (spec 3.2 (a), (b) and limit 10; me-2nb): each value computed once, its size charged. The
names are the stub's, in its namespace (`VE.Calc.Table` is ME-4's data table). -/

/-- The size of an exact value: its numerator's and its denominator's (12.2's `bits`). -/
def qbits (q : Rat) : Nat := bits q.num + bits q.den

/-- Limit 10: the units one case may spend, 12.2's unit (one per visit, plus the size of each value computed). -/
def maxWork : Nat := 2 ^ 33

/-- `10 ^ maxDigits` lies between `2 ^ (smallBits - 1)` and `2 ^ smallBits`. -/
def smallBits : Nat := 13607

/-- A power that is beyond the digit limit, known from its base's size before it is computed. -/
def powTooLarge (x : Rat) (k : Nat) : Bool :=
  smallBits ≤ (bits x.num - 1) * k || smallBits ≤ (bits x.den - 1) * k

theorem pow_beyond (a k : Nat) (h : smallBits ≤ a.log2 * k) : digitBound ≤ a ^ k := by
  have ha : a ≠ 0 := by intro h0; subst h0; simp [Nat.log2_zero, smallBits] at h
  have hb : digitBound ≤ 2 ^ smallBits := by unfold digitBound maxDigits smallBits; decide +kernel
  calc digitBound ≤ 2 ^ smallBits := hb
    _ ≤ 2 ^ (a.log2 * k) := Nat.pow_le_pow_right (by omega) h
    _ = (2 ^ a.log2) ^ k := Nat.pow_mul _ _ _
    _ ≤ a ^ k := Nat.pow_le_pow_left (Nat.log2_self_le ha) _

theorem powTooLarge_sound (x : Rat) (k : Nat) (h : powTooLarge x k = true) : Val.guard (x ^ k) = .tooLarge := by
  have hs : ¬ Small (x ^ k) := fun hs => by
    have hd : (x ^ k).num.natAbs < digitBound ∧ (x ^ k).den < digitBound := by
      unfold digitBound; simpa only [Small, digitCount_le_iff] using hs
    simp only [Rat.num_pow, Rat.den_pow, Int.natAbs_pow] at hd
    simp only [powTooLarge, bits, Nat.add_sub_cancel, Int.natAbs_natCast, Bool.or_eq_true, decide_eq_true_eq] at h
    rcases h with h | h
    · have := pow_beyond _ k h; omega
    · have := pow_beyond _ k h; omega
  simp [Val.guard, hs]

/-- The values so far, the latest declaration first. -/
abbrev Table := List (String × Val)

def Table.read (t : Table) (n : String) : Val := (t.lookup n).getD .undefined

/-- 2.4's values, each declaration's computed once from the entries before it. -/
def valueTable (ds : List Decl) : Table := ds.foldl (fun (t : Table) d => (d.name, d.valL t.read) :: t) []

/-- The meaning: the table reads what 2.4's `valuesL` gives, so every theorem of 2.4 and 3.4 is unchanged. -/
theorem valueTable_read (ds : List Decl) : (valueTable ds).read = valuesL ds := by
  suffices h : ∀ (t : Table) (τ : String → Val), t.read = τ →
      Table.read (ds.foldl (fun (t : Table) d => (d.name, d.valL t.read) :: t) t) =
        ds.foldl (fun τ d n => if n = d.name then d.valL τ else τ n) τ from
    h [] _ (funext fun _ => rfl)
  induction ds with
  | nil => intro t τ h; exact h
  | cons d rest ih =>
    intro t τ h
    apply ih
    funext n
    subst h
    by_cases hn : n = d.name
    · subst hn; simp [Table.read]
    · have : (n == d.name) = false := by simpa using hn
      simp only [Table.read, List.lookup, this, hn, if_false]

/-- One visit, refused when the units would pass `limit`. -/
def visitC {α : Type} (limit w : Nat) (k : Nat → Option (α × Nat)) : Option (α × Nat) :=
  if limit ≤ w then none else k (w + 1)

/-- A value computed is charged its size, then held to the digit limit. -/
def chargeQ (limit : Nat) (q : Rat) (w : Nat) : Option (Val × Nat) :=
  if limit < w + qbits q then none else some (Val.guard q, w + qbits q)

/-- A value read from the table is charged its size; a fault costs nothing more. -/
def chargeV (limit : Nat) (v : Val) (w : Nat) : Option (Val × Nat) :=
  match v with
  | .ok q => if limit < w + qbits q then none else some (v, w + qbits q)
  | v => some (v, w)

/-- 2.4's `Val.bin`, charged: `f` computes a value only from two values, and the first fault decides. -/
def binC (limit : Nat) (f : Rat → Rat → Option Rat) (a b : Val) (w : Nat) : Option (Val × Nat) :=
  match a, b with
  | .ok x, .ok y => match f x y with
    | some q => chargeQ limit q w
    | none => some (.undefined, w)
  | .ok _, v => some (v, w)
  | v, _ => some (v, w)

/-- 2.4's `Expr.evalL` over the table, charged; `none` when the units would pass `limit`. A read is a lookup. -/
def Expr.evalC (limit : Nat) (t : Table) : Expr → Nat → Option (Val × Nat)
  | .lit q, w => visitC limit w (chargeQ limit q)
  | .val n, w => visitC limit w (chargeV limit (t.read n))
  | .add a b, w => visitC limit w fun w => (Expr.evalC limit t a w).bind fun (x, w) =>
      (Expr.evalC limit t b w).bind fun (y, w) => binC limit (fun x y => some (x + y)) x y w
  | .sub a b, w => visitC limit w fun w => (Expr.evalC limit t a w).bind fun (x, w) =>
      (Expr.evalC limit t b w).bind fun (y, w) => binC limit (fun x y => some (x - y)) x y w
  | .mul a b, w => visitC limit w fun w => (Expr.evalC limit t a w).bind fun (x, w) =>
      (Expr.evalC limit t b w).bind fun (y, w) => binC limit (fun x y => some (x * y)) x y w
  | .div a b, w => visitC limit w fun w => (Expr.evalC limit t a w).bind fun (x, w) =>
      (Expr.evalC limit t b w).bind fun (y, w) => binC limit (fun x y => if y = 0 then none else some (x / y)) x y w
  | .pow a k, w => visitC limit w fun w => (Expr.evalC limit t a w).bind fun
    | (.ok x, w) => if powTooLarge x k then some (.tooLarge, w) else chargeQ limit (x ^ k) w
    | (v, w) => some (v, w)

def Decl.valC (limit : Nat) (t : Table) (d : Decl) (w : Nat) : Option (Val × Nat) :=
  match d.source with
  | .stated q | .counted _ (.ok (some q)) => visitC limit w (chargeQ limit q)
  | .defined e => Expr.evalC limit t e w
  | .free | .counted _ (.ok none) => some (.undefined, w)
  | .counted _ .exhausted => some (.exhausted, w)

/-- The table, charged: each declaration once, in order. -/
def valueTableC (limit : Nat) : List Decl → Table → Nat → Option (Table × Nat)
  | [], t, w => some (t, w)
  | d :: ds, t, w => (Decl.valC limit t d w).bind fun (v, w) => valueTableC limit ds ((d.name, v) :: t) w

/-- Expressions in order, each once. -/
def Expr.evalsC (limit : Nat) (t : Table) : List Expr → Nat → Option (List Val × Nat)
  | [], w => some ([], w)
  | e :: es, w => (Expr.evalC limit t e w).bind fun (v, w) => (Expr.evalsC limit t es w).map fun r => (v :: r.1, r.2)

/-- A claim's verdict from its sides' values, in `Claim.exprs`' order (2.2's `Claim.decide`, read from the sides). -/
def Claim.decideSides : Claim → List Rat → Verdict
  | .compare c _ _, [x, y] => if c.Holds x y then .holds else .fails
  | .within .., [x, l, h] => if l ≤ x ∧ x ≤ h then .holds else .fails
  | .rounds r _ p, [x] => if RoundsTo r p x then .holds else .fails
  | _, _ => .undefined

/-- 2.4's `Claim.run`, read from the sides evaluated once; the row's `sides`, `display` and `tie` read them too. -/
def Claim.ofSides (c : Claim) (vs : List Val) : Outcome :=
  match firstFault vs with
  | some .tooLarge => .unknown (.limit .digits)
  | some .exhausted => .unknown (.limit .evaluations)
  | some _ => .decided .undefined
  | none => .decided (Claim.decideSides c (vs.filterMap fun | .ok q => some q | _ => none))

/-! What the charged steps mean: 2.4's value with no more than `limit` units spent (`_some`), and the same answer
under any larger limit (`_mono`). -/

theorem visitC_some {α : Type} {limit w : Nat} {k : Nat → Option (α × Nat)} {r : α × Nat}
    (h : visitC limit w k = some r) : w < limit ∧ k (w + 1) = some r := by
  unfold visitC at h; split at h
  · cases h
  · exact ⟨by omega, h⟩

theorem visitC_mono {α : Type} {limit limit' w : Nat} {k k' : Nat → Option (α × Nat)} {r : α × Nat}
    (hk : ∀ w r, k w = some r → k' w = some r) (hl : limit ≤ limit') (h : visitC limit w k = some r) :
    visitC limit' w k' = some r := by
  obtain ⟨hw, h⟩ := visitC_some h
  unfold visitC; rw [if_neg (by omega)]; exact hk _ _ h

theorem chargeQ_some {limit : Nat} {q : Rat} {w : Nat} {v : Val} {w' : Nat} (h : chargeQ limit q w = some (v, w')) :
    v = Val.guard q ∧ w ≤ w' ∧ w' ≤ limit := by
  unfold chargeQ at h; split at h
  · cases h
  · cases h; exact ⟨rfl, by omega, by omega⟩

theorem chargeQ_mono {limit limit' : Nat} {q : Rat} {w : Nat} {r : Val × Nat} (hl : limit ≤ limit')
    (h : chargeQ limit q w = some r) : chargeQ limit' q w = some r := by
  unfold chargeQ at *; split at h
  · cases h
  · rw [if_neg (by omega)]; exact h

theorem binC_some {limit : Nat} {f : Rat → Rat → Option Rat} {a b v : Val} {w w' : Nat} (hw : w ≤ limit)
    (h : binC limit f a b w = some (v, w')) :
    v = Val.bin (fun x y => (f x y).elim .undefined Val.guard) a b ∧ w ≤ w' ∧ w' ≤ limit := by
  cases a <;> cases b <;> simp only [binC, Val.bin] at h ⊢
  case ok.ok x y =>
    cases hq : f x y with
    | some q => rw [hq] at h; exact chargeQ_some h
    | none => rw [hq] at h; cases h; exact ⟨rfl, by omega, hw⟩
  all_goals (cases h; exact ⟨rfl, by omega, hw⟩)

theorem binC_mono {limit limit' : Nat} {f : Rat → Rat → Option Rat} {a b : Val} {w : Nat} {r : Val × Nat}
    (hl : limit ≤ limit') (h : binC limit f a b w = some r) : binC limit' f a b w = some r := by
  cases a <;> cases b <;> simp only [binC] at h ⊢
  case ok.ok x y =>
    cases hq : f x y with
    | some q => rw [hq] at h; exact chargeQ_mono hl h
    | none => rw [hq] at h; exact h
  all_goals exact h

theorem Expr.evalC_some (limit : Nat) (t : Table) (e : Expr) (w : Nat) (v : Val) (w' : Nat)
    (h : Expr.evalC limit t e w = some (v, w')) : v = e.evalL t.read ∧ w < w' ∧ w' ≤ limit := by
  induction e generalizing w v w' with
  | lit q =>
    obtain ⟨hw, h⟩ := visitC_some h; obtain ⟨rfl, h1, h2⟩ := chargeQ_some h; exact ⟨rfl, by omega, h2⟩
  | val n =>
    obtain ⟨hw, h⟩ := visitC_some h
    unfold chargeV at h; split at h
    · split at h
      · cases h
      · cases h; exact ⟨rfl, by omega, by omega⟩
    · cases h; exact ⟨rfl, by omega, by omega⟩
  | add a b iha ihb | sub a b iha ihb | mul a b iha ihb | div a b iha ihb =>
    obtain ⟨hw, h⟩ := visitC_some h
    obtain ⟨⟨x, w1⟩, ha, h⟩ := Option.bind_eq_some_iff.mp h
    obtain ⟨⟨y, w2⟩, hb, h⟩ := Option.bind_eq_some_iff.mp h
    obtain ⟨rfl, ha1, ha2⟩ := iha _ _ _ ha
    obtain ⟨rfl, hb1, hb2⟩ := ihb _ _ _ hb
    obtain ⟨rfl, h1, h2⟩ := binC_some hb2 h
    refine ⟨?_, by omega, h2⟩
    simp only [Expr.evalL]
    first | rfl | (congr 1; funext x y; split <;> rfl)
  | pow a k iha =>
    obtain ⟨hw, h⟩ := visitC_some h
    obtain ⟨⟨x, w1⟩, ha, h⟩ := Option.bind_eq_some_iff.mp h
    obtain ⟨hx, ha1, ha2⟩ := iha _ _ _ ha
    simp only [Expr.evalL, ← hx]
    cases x with
    | ok q =>
      simp only at h ⊢
      by_cases hp : powTooLarge q k = true
      · rw [if_pos hp] at h; cases h; exact ⟨(powTooLarge_sound _ _ hp).symm, by omega, ha2⟩
      · rw [if_neg hp] at h; obtain ⟨rfl, h1, h2⟩ := chargeQ_some h; exact ⟨rfl, by omega, h2⟩
    | _ => simp only at h; cases h; exact ⟨rfl, by omega, ha2⟩

/-- A value evaluated once over the table is 2.4's (3.2 (a)). -/
theorem Expr.evalC_agrees (limit : Nat) (t : Table) (e : Expr) (w : Nat) (v : Val) (w' : Nat)
    (h : Expr.evalC limit t e w = some (v, w')) : v = e.evalL t.read :=
  (Expr.evalC_some limit t e w v w' h).1

theorem Expr.evalC_mono {limit limit' : Nat} (t : Table) (e : Expr) (w : Nat) (r : Val × Nat) (hl : limit ≤ limit')
    (h : Expr.evalC limit t e w = some r) : Expr.evalC limit' t e w = some r := by
  induction e generalizing w r with
  | lit q => exact visitC_mono (fun _ _ => chargeQ_mono hl) hl h
  | val n =>
    refine visitC_mono (fun w r h => ?_) hl h
    unfold chargeV at *; split at h
    · split at h
      · cases h
      · rw [if_neg (by omega)]; exact h
    · exact h
  | add a b iha ihb | sub a b iha ihb | mul a b iha ihb | div a b iha ihb =>
    refine visitC_mono (fun w r h => ?_) hl h
    obtain ⟨⟨x, w1⟩, ha, h⟩ := Option.bind_eq_some_iff.mp h
    obtain ⟨⟨y, w2⟩, hb, h⟩ := Option.bind_eq_some_iff.mp h
    simp only [iha _ _ ha, ihb _ _ hb, Option.bind_some]
    exact binC_mono hl h
  | pow a k iha =>
    refine visitC_mono (fun w r h => ?_) hl h
    obtain ⟨⟨x, w1⟩, ha, h⟩ := Option.bind_eq_some_iff.mp h
    simp only [iha _ _ ha, Option.bind_some]
    cases x with
    | ok q =>
      simp only at h ⊢
      by_cases hp : powTooLarge q k = true
      · rw [if_pos hp] at h ⊢; exact h
      · rw [if_neg hp] at h ⊢; exact chargeQ_mono hl h
    | _ => exact h

theorem Decl.valC_some {limit : Nat} {t : Table} {d : Decl} {w : Nat} {v : Val} {w' : Nat} (hw : w ≤ limit)
    (h : Decl.valC limit t d w = some (v, w')) : v = d.valL t.read ∧ w ≤ w' ∧ w' ≤ limit := by
  unfold Decl.valC at h; unfold Decl.valL
  split at h <;> rename_i hs <;> rw [hs]
  · obtain ⟨_, h⟩ := visitC_some h; obtain ⟨rfl, _, h2⟩ := chargeQ_some h; exact ⟨rfl, by omega, h2⟩
  · obtain ⟨_, h⟩ := visitC_some h; obtain ⟨rfl, _, h2⟩ := chargeQ_some h; exact ⟨rfl, by omega, h2⟩
  · obtain ⟨rfl, h1, h2⟩ := Expr.evalC_some _ _ _ _ _ _ h; exact ⟨rfl, by omega, h2⟩
  all_goals cases h; exact ⟨rfl, by omega, hw⟩

theorem Decl.valC_mono {limit limit' : Nat} {t : Table} {d : Decl} {w : Nat} {r : Val × Nat} (hl : limit ≤ limit')
    (h : Decl.valC limit t d w = some r) : Decl.valC limit' t d w = some r := by
  unfold Decl.valC at *
  split at h
  · exact visitC_mono (fun _ _ => chargeQ_mono hl) hl h
  · exact visitC_mono (fun _ _ => chargeQ_mono hl) hl h
  · exact Expr.evalC_mono _ _ _ _ hl h
  all_goals exact h

theorem valueTableC_some (limit : Nat) (ds : List Decl) (t : Table) (w : Nat) (t' : Table) (w' : Nat)
    (hw : w ≤ limit) (h : valueTableC limit ds t w = some (t', w')) :
    t' = ds.foldl (fun (t : Table) d => (d.name, d.valL t.read) :: t) t ∧ w ≤ w' ∧ w' ≤ limit := by
  induction ds generalizing t w with
  | nil => cases h; exact ⟨rfl, by omega, hw⟩
  | cons d ds ih =>
    obtain ⟨⟨v, w1⟩, hv, h⟩ := Option.bind_eq_some_iff.mp h
    obtain ⟨rfl, h1, h2⟩ := Decl.valC_some hw hv
    obtain ⟨rfl, h3, h4⟩ := ih _ _ h2 h
    exact ⟨rfl, by omega, h4⟩

theorem valueTableC_eq (limit : Nat) (ds : List Decl) (t : Table) (w : Nat)
    (h : valueTableC limit ds [] 0 = some (t, w)) : t = valueTable ds :=
  (valueTableC_some limit ds [] 0 t w (Nat.zero_le _) h).1

theorem valueTableC_mono {limit limit' : Nat} (ds : List Decl) (t : Table) (w : Nat) (r : Table × Nat)
    (hl : limit ≤ limit') (h : valueTableC limit ds t w = some r) : valueTableC limit' ds t w = some r := by
  induction ds generalizing t w with
  | nil => exact h
  | cons d ds ih =>
    obtain ⟨⟨v, w1⟩, hv, h⟩ := Option.bind_eq_some_iff.mp h
    simp only [valueTableC, Decl.valC_mono hl hv, Option.bind_some]
    exact ih _ _ h

theorem Expr.evalsC_some (limit : Nat) (t : Table) (es : List Expr) (w : Nat) (vs : List Val) (w' : Nat)
    (hw : w ≤ limit) (h : Expr.evalsC limit t es w = some (vs, w')) :
    vs = es.map (Expr.evalL t.read) ∧ w ≤ w' ∧ w' ≤ limit := by
  induction es generalizing w vs with
  | nil => cases h; exact ⟨rfl, by omega, hw⟩
  | cons e es ih =>
    obtain ⟨⟨v, w1⟩, hv, h⟩ := Option.bind_eq_some_iff.mp h
    obtain ⟨⟨vs', w2⟩, hr, h⟩ := Option.map_eq_some_iff.mp h
    cases h
    obtain ⟨rfl, h1, h2⟩ := Expr.evalC_some _ _ _ _ _ _ hv
    obtain ⟨rfl, h3, h4⟩ := ih _ _ h2 hr
    exact ⟨rfl, by omega, h4⟩

theorem Expr.evalsC_mono {limit limit' : Nat} (t : Table) (es : List Expr) (w : Nat) (r : List Val × Nat)
    (hl : limit ≤ limit') (h : Expr.evalsC limit t es w = some r) : Expr.evalsC limit' t es w = some r := by
  induction es generalizing w r with
  | nil => exact h
  | cons e es ih =>
    obtain ⟨⟨v, w1⟩, hv, h⟩ := Option.bind_eq_some_iff.mp h
    obtain ⟨r', hr, rfl⟩ := Option.map_eq_some_iff.mp h
    simp only [Expr.evalsC, Expr.evalC_mono _ _ _ _ hl hv, Option.bind_some, ih _ _ hr, Option.map_some]

theorem firstFault_none {vs : List Val} (h : firstFault vs = none) : ∀ v ∈ vs, ∃ q, v = .ok q := by
  induction vs with
  | nil => simp
  | cons v vs ih => cases v <;> simp_all [firstFault]

/-- A claim's outcome from its sides is 2.4's `Claim.run`. -/
theorem Claim.ofSides_eq (ds : List Decl) (h : WellFormed ds) (c : Claim) :
    Claim.ofSides c (c.exprs.map (Expr.evalL (valuesL ds))) = c.run ds := by
  unfold Claim.ofSides Claim.run
  cases hf : firstFault (c.exprs.map (Expr.evalL (valuesL ds))) with
  | some v => cases v <;> rfl
  | none =>
  have hok : ∀ e ∈ c.exprs, ∃ q, e.evalL (valuesL ds) = .ok q ∧ e.eval (values ds) = some q := fun e he => by
    obtain ⟨q, hq⟩ := firstFault_none hf _ (List.mem_map_of_mem he)
    have := Expr.evalL_agrees e (valuesL ds) (values ds) (valuesL_agrees ds h)
    rw [hq] at this; exact ⟨q, hq, this⟩
  congr 1
  cases c with
  | compare k a b =>
    obtain ⟨x, hx, hx'⟩ := hok a (by simp [Claim.exprs]); obtain ⟨y, hy, hy'⟩ := hok b (by simp [Claim.exprs])
    simp [Claim.exprs, Claim.decideSides, Claim.decide, hx, hy, hx', hy']
  | within e lo hi =>
    obtain ⟨x, hx, hx'⟩ := hok e (by simp [Claim.exprs]); obtain ⟨l, hl, hl'⟩ := hok lo (by simp [Claim.exprs])
    obtain ⟨u, hu, hu'⟩ := hok hi (by simp [Claim.exprs])
    simp [Claim.exprs, Claim.decideSides, Claim.decide, hx, hl, hu, hx', hl', hu']
  | rounds r e p =>
    obtain ⟨x, hx, hx'⟩ := hok e (by simp [Claim.exprs])
    simp [Claim.exprs, Claim.decideSides, Claim.decide, hx, hx']

end Work

end VE.Calc
