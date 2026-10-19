import VE.Calc.Decls

/-! Inlining (spec 2.7, J3): every name outside the kept ones is replaced by its stated or counted value as a literal,
or by its inlined definition; the kept names stay `val` nodes. One function for derivations, consistency checks and
identities, built by ME-9, which landed first. Each declaration is inlined once, in order, into a table that later
definitions read, so a chain of definitions is shared, not copied. -/

namespace VE.Calc

/-- The free values, in declaration order: the unknowns of derivations and identities. -/
def freeNames (ds : List Decl) : List String :=
  (ds.filter fun d => match d.source with | .free => true | _ => false).map Decl.name

/-- The declarations with each name in `ns` given the value `κ n`. -/
def assign (ds : List Decl) (ns : List String) (κ : String → Rat) : List Decl :=
  ds.map fun d => if d.name ∈ ns then { d with source := .stated (κ d.name) } else d

/-- What each name inlines to, the latest declaration first. -/
abbrev Inlined := List (String × Except Val Expr)

def Inlined.at (t : Inlined) (n : String) : Except Val Expr := (t.lookup n).getD (.error .undefined)

def Expr.bin2 (f : Expr → Expr → Expr) : Except Val Expr → Except Val Expr → Except Val Expr
  | .ok a, .ok b => .ok (f a b)
  | .ok _, .error v => .error v
  | .error v, _ => .error v

/-- Replaces each name by its entry; the first faulty name, left to right, names the fault. -/
def Expr.subst (t : Inlined) : Expr → Except Val Expr
  | .lit q => .ok (.lit q)
  | .val n => t.at n
  | .add a b => Expr.bin2 .add (a.subst t) (b.subst t)
  | .sub a b => Expr.bin2 .sub (a.subst t) (b.subst t)
  | .mul a b => Expr.bin2 .mul (a.subst t) (b.subst t)
  | .div a b => Expr.bin2 .div (a.subst t) (b.subst t)
  | .pow a k => (a.subst t).map (.pow · k)

def Decl.inlineUnder (keep : List String) (t : Inlined) (d : Decl) : Except Val Expr :=
  if d.name ∈ keep then .ok (.val d.name) else
  match d.source with
  | .stated q | .counted _ (.ok (some q)) => .ok (.lit q)
  | .defined e => e.subst t
  | .free | .counted _ (.ok none) => .error .undefined
  | .counted _ .exhausted => .error .exhausted

def inlineTable (ds : List Decl) (keep : List String) : Inlined :=
  ds.foldl (fun t d => (d.name, d.inlineUnder keep t) :: t) []

/-- Inlining. `.error .undefined` when a name read outside `keep` has no value (a free value, a missing name, a counted
value that is undefined); `.error .exhausted` when it reads, directly or through definitions, a counted value whose
budget ran out. With no statistics yet (ME-7), it never meets the digit limit. -/
def Expr.inline (ds : List Decl) (keep : List String) (e : Expr) : Except Val Expr :=
  e.subst (inlineTable ds keep)

/-- The table's entries read only kept names, and its faults name their causes in `D`. -/
structure Inlined.Faults (D : List Decl) (keep : List String) (t : Inlined) : Prop where
  names : ∀ n e', t.at n = .ok e' → ∀ m ∈ e'.names, m ∈ keep
  exhausted : ∀ n, t.at n = .error .exhausted → NameExhausted D n
  faults : ∀ n v, t.at n = .error v → v = .undefined ∨ v = .exhausted

/-- The table agrees with the values `σ` when each kept name `m` has the value `κ m`. -/
structure Inlined.Agrees (κ : String → Rat) (σ : Values) (t : Inlined) : Prop where
  ok : ∀ n e', t.at n = .ok e' → σ n = e'.eval (fun m => some (κ m))
  undefined : ∀ n, t.at n = .error .undefined → σ n = none

theorem Expr.subst_faults {D keep t} (ht : Inlined.Faults D keep t) (e : Expr) :
    (∀ e', e.subst t = .ok e' → ∀ m ∈ e'.names, m ∈ keep) ∧
    (e.subst t = .error .exhausted → ∃ m ∈ e.names, NameExhausted D m) ∧
    (∀ v, e.subst t = .error v → v = .undefined ∨ v = .exhausted) := by
  induction e with
  | lit q => simp [Expr.subst, Expr.names]
  | val n => exact ⟨ht.names n, fun h => ⟨n, by simp [Expr.names], ht.exhausted n h⟩, ht.faults n⟩
  | pow a k ih => cases ha : a.subst t <;> simp_all [Expr.subst, Expr.names, Except.map]
  | add a b iha ihb | sub a b iha ihb | mul a b iha ihb | div a b iha ihb =>
      cases ha : a.subst t <;> cases hb : b.subst t <;> simp_all [Expr.subst, Expr.bin2, Expr.names] <;> grind

theorem Expr.subst_agrees {κ σ t} (ht : Inlined.Agrees κ σ t) (e : Expr) :
    (∀ e', e.subst t = .ok e' → e.eval σ = e'.eval (fun m => some (κ m))) ∧
    (e.subst t = .error .undefined → e.eval σ = none) := by
  induction e with
  | lit q => simp [Expr.subst, Expr.eval]
  | val n => exact ⟨fun e' h => by simpa [Expr.eval] using ht.ok n e' h, fun h => by simpa [Expr.eval] using ht.undefined n h⟩
  | pow a k ih => cases ha : a.subst t <;> simp_all [Expr.subst, Expr.eval, Except.map]
  | add a b iha ihb | sub a b iha ihb | mul a b iha ihb | div a b iha ihb =>
      cases ha : a.subst t <;> cases hb : b.subst t <;> simp_all [Expr.subst, Expr.bin2, Expr.eval]

theorem Inlined.at_cons (t : Inlined) (m : String) (r : Except Val Expr) (n : String) :
    Inlined.at ((m, r) :: t) n = if n = m then r else t.at n := by
  simp only [Inlined.at, List.lookup]; split <;> simp_all

theorem inlineTable_faults (D : List Decl) (keep : List String) (ds : List Decl) (t : Inlined)
    (hD : ∀ d ∈ ds, d ∈ D) (ht : Inlined.Faults D keep t) :
    Inlined.Faults D keep (ds.foldl (fun t d => (d.name, d.inlineUnder keep t) :: t) t) := by
  induction ds generalizing t with
  | nil => exact ht
  | cons d ds ih =>
      refine ih _ (fun d' h => hD d' (by simp [h])) ?_
      have hs := Expr.subst_faults ht
      have hdD : d ∈ D := hD d (by simp)
      constructor <;> intro n <;> simp only [Inlined.at_cons] <;> by_cases hn : n = d.name <;>
        simp only [hn, if_true, if_false]
      all_goals first
        | exact ht.names n | exact ht.exhausted n | exact ht.faults n
        | (by_cases hk : d.name ∈ keep <;> rcases hsrc : d.source with q | e | _ | ⟨q, ⟨_ | v⟩ | _⟩ <;>
            simp_all [Decl.inlineUnder, Expr.names] <;>
            first
              | exact NameExhausted.here ⟨d, hdD, rfl, hsrc⟩ | exact (hs e).1 | exact (hs e).2.2
              | (intro h; obtain ⟨m, hm, hx⟩ := (hs e).2.1 h; exact NameExhausted.dep ⟨d, hdD, rfl, hsrc⟩ hm hx))

theorem inlineTable_agrees (keep : List String) (κ : String → Rat) (ds : List Decl) (σ : Values) (t : Inlined)
    (hc : ∀ d ∈ ds, ∀ q v, d.source = .counted q (.ok v) → q.get = v) (ht : Inlined.Agrees κ σ t) :
    Inlined.Agrees κ ((assign ds keep κ).foldl (fun σ d n => if n = d.name then d.valueUnder σ else σ n) σ)
      (ds.foldl (fun t d => (d.name, d.inlineUnder keep t) :: t) t) := by
  induction ds generalizing σ t with
  | nil => exact ht
  | cons d ds ih =>
      simp only [assign, List.map_cons, List.foldl_cons] at ih ⊢
      refine ih _ _ (fun d' h => hc d' (by simp [h])) ?_
      have hs := Expr.subst_agrees ht
      have hcd := hc d (by simp)
      by_cases hk : d.name ∈ keep <;> simp only [hk, if_true, if_false] <;>
        constructor <;> intro n <;> simp only [Inlined.at_cons] <;> by_cases hn : n = d.name <;>
        simp only [hn, if_true, if_false]
      all_goals first
        | exact ht.ok n | exact ht.undefined n
        | (rcases hsrc : d.source with q | e | _ | ⟨q, ⟨_ | v⟩ | _⟩ <;>
            simp_all [Decl.inlineUnder, Decl.valueUnder, Expr.eval])

theorem inline_faults (ds : List Decl) (keep : List String) : Inlined.Faults ds keep (inlineTable ds keep) :=
  inlineTable_faults ds keep ds [] (fun _ h => h) ⟨by simp [Inlined.at], by simp [Inlined.at], by simp [Inlined.at]⟩

theorem inline_agrees (ds : List Decl) (h : WellFormed ds) (keep : List String) (κ : String → Rat) :
    Inlined.Agrees κ (values (assign ds keep κ)) (inlineTable ds keep) :=
  inlineTable_agrees keep κ ds _ [] h.2.2 ⟨by simp [Inlined.at], by simp [Inlined.at]⟩

theorem Expr.inline_names (ds : List Decl) (keep : List String) (e e' : Expr) (he : e.inline ds keep = .ok e') :
    ∀ n ∈ e'.names, n ∈ keep :=
  (Expr.subst_faults (inline_faults ds keep) e).1 e' he

theorem Expr.inline_error (ds : List Decl) (keep : List String) (e : Expr) (v : Val)
    (he : e.inline ds keep = .error v) : v = .undefined ∨ v = .exhausted :=
  (Expr.subst_faults (inline_faults ds keep) e).2.2 v he

theorem Expr.inline_sound (ds : List Decl) (h : WellFormed ds) (keep : List String)
    (hk : ∀ n ∈ keep, n ∈ ds.map Decl.name) (e e' : Expr) (he : e.inline ds keep = .ok e') (κ : String → Rat)
    (x : Rat) : Denotes (values (assign ds keep κ)) e x ↔ Denotes (fun n => some (κ n)) e' x := by
  rw [← Expr.eval_iff, ← Expr.eval_iff, (Expr.subst_agrees (inline_agrees ds h keep κ) e).1 e' he]

theorem Expr.inline_undefined (ds : List Decl) (h : WellFormed ds) (keep : List String) (e : Expr)
    (he : e.inline ds keep = .error .undefined) : ∀ κ x, ¬ Denotes (values (assign ds keep κ)) e x := by
  intro κ x hx
  have := (Expr.subst_agrees (inline_agrees ds h keep κ) e).2 he
  simp [(Expr.eval_iff _ _ _).mpr hx] at this

theorem Expr.inline_exhausted (ds : List Decl) (keep : List String) (e : Expr)
    (he : e.inline ds keep = .error .exhausted) : e.ReadsExhausted ds :=
  (Expr.subst_faults (inline_faults ds keep) e).2.1 he

end VE.Calc
