import VE.Calc.Eval

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

instance (q : Rat) : Decidable (Small q) := by
  unfold Small
  infer_instance

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

end VE.Calc
