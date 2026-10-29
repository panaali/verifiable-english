import VE.Events.Premises
import VE.Finite

/-! The calendar check on finite situations (docs/spec/events-time-causation.md 1.6, 6.1): the days
are strictly ordered by `before`, each named date denotes a day, the named days are in date order,
and no gap holds more unnamed days than the calendar has between (or beyond) the named dates.
`embeddable` is its success; `numbering` numbers the days as civil days. -/
namespace VE.Events
open VE.Time (Civil dateMax)

section Finite
variable {α : Type} [DecidableEq α]

def beforeB (V : EventsEnv) (M : VE.FiniteModel α) (x y : α) : Bool := decide ([x, y] ∈ M.relations V.before)
def rank (V : EventsEnv) (M : VE.FiniteModel α) (x : α) : Nat :=
  ((M.domains V.day).filter (fun y => beforeB V M y x)).length
def dateDay (V : EventsEnv) (M : VE.FiniteModel α) (D : Civil) : Option α :=
  (M.constants (dateName D)).filter (fun x => (M.domains V.day).contains x)
def namedRank (V : EventsEnv) (M : VE.FiniteModel α) (D : Civil) : Nat :=
  ((dateDay V M D).map (rank V M)).getD 0
def daysText (n : Nat) : String := if n = 1 then "1 day" else s!"{n} days"

def strictLinearB (V : EventsEnv) (M : VE.FiniteModel α) : Bool :=
  let ds := M.domains V.day
  decide ds.Nodup && ds.all (fun x => !beforeB V M x x) &&
    ds.all (fun x => ds.all (fun y => ds.all (fun z => !(beforeB V M x y && beforeB V M y z) || beforeB V M x z))) &&
    ds.all (fun x => ds.all (fun y => x == y || beforeB V M x y || beforeB V M y x))

/-- The first failing condition of 1.6, as its diagnostic text; `none` when the situation passes. -/
def calendarCheck (V : EventsEnv) (M : VE.FiniteModel α) : Option String :=
  let ds := M.domains V.day
  let r := namedRank V M
  if !strictLinearB V M then some "NotCalendar: before is not a strict linear order on the days"
  else match V.dates.find? (fun D => (dateDay V M D).isNone) with
  | some D => some s!"NotCalendar: {D.iso} denotes no day"
  | none =>
  match (consecutive V).find? (fun p => !decide (r p.1 < r p.2)) with
  | some p => some s!"NotCalendar: {p.1.iso} is not before {p.2.iso}"
  | none =>
  match V.dates with
  | [] =>
    if ds.length ≤ dateMax + 1 then none
    else some s!"NotCalendar: {daysText ds.length}, at most {dateMax + 1}"
  | D₁ :: rest =>
    let Dk := (D₁ :: rest).getLastD D₁
    if r D₁ > D₁.num then some s!"NotCalendar: {daysText (r D₁)} before {D₁.iso}, at most {D₁.num}"
    else match (consecutive V).find? (fun p => decide (r p.2 - r p.1 - 1 > p.2.num - p.1.num - 1)) with
    | some p =>
      some s!"NotCalendar: {daysText (r p.2 - r p.1 - 1)} between {p.1.iso} and {p.2.iso}, at most {p.2.num - p.1.num - 1}"
    | none =>
      if ds.length - 1 - r Dk > dateMax - Dk.num then
        some s!"NotCalendar: {daysText (ds.length - 1 - r Dk)} after {Dk.iso}, at most {dateMax - Dk.num}"
      else none

def embeddable (V : EventsEnv) (M : VE.FiniteModel α) : Bool := (calendarCheck V M).isNone

/-- A named day takes its date's number; an unnamed day the number of the last named day below it
    plus the rank difference (below the first named day: that day's number minus the difference;
    with no named date: its rank). -/
def numbering (V : EventsEnv) (M : VE.FiniteModel α) (x : α) : Nat :=
  let r := namedRank V M
  match (V.dates.filter (fun D => decide (r D ≤ rank V M x))).getLast? with
  | some D => D.num + (rank V M x - r D)
  | none =>
    match V.dates with
    | [] => rank V M x
    | D₁ :: _ => D₁.num - (r D₁ - rank V M x)
end Finite

/-! ## Proofs: counting days by number (a pigeonhole argument over lists) -/

section Count
variable {β : Type} (f : β → Nat)

theorem countP_lt_succ (l : List β) (b : Nat) :
    l.countP (fun y => decide (f y < b + 1)) =
      l.countP (fun y => decide (f y < b)) + l.countP (fun y => decide (f y = b)) := by
  induction l with
  | nil => rfl
  | cons y l ih =>
    simp only [List.countP_cons, ih, decide_eq_true_eq]
    by_cases h : f y < b
    · simp [h, Nat.lt_succ_of_lt h, Nat.ne_of_lt h]; omega
    · by_cases h' : f y = b
      · simp [h']; omega
      · simp [h, h', show ¬ f y < b + 1 by omega]

/-- On a list without repeats, a function one-to-one on it takes each value at most once. -/
theorem countP_eq_le_one {l : List β} (hn : l.Nodup) (inj : ∀ x ∈ l, ∀ y ∈ l, f x = f y → x = y) (b : Nat) :
    l.countP (fun y => decide (f y = b)) ≤ 1 := by
  induction l with
  | nil => simp
  | cons y l ih =>
    obtain ⟨hy, hn⟩ := List.nodup_cons.1 hn
    have ih := ih hn (fun x hx z hz => inj x (.tail _ hx) z (.tail _ hz))
    rw [List.countP_cons]
    by_cases h : f y = b
    · have : l.countP (fun z => decide (f z = b)) = 0 := List.countP_eq_zero.2 fun z hz hzb =>
        hy ((inj z (.tail _ hz) y (.head _) (by simp at hzb; omega)) ▸ hz)
      simp [h, this]
    · simpa [h] using ih

/-- The pigeonhole step: at most `b - a` elements take a value in `a..b - 1`. -/
theorem countP_lt_le {l : List β} (hn : l.Nodup) (inj : ∀ x ∈ l, ∀ y ∈ l, f x = f y → x = y) (a k : Nat) :
    l.countP (fun y => decide (f y < a + k)) ≤ l.countP (fun y => decide (f y < a)) + k := by
  induction k with
  | zero => simp
  | succ k ih =>
    rw [← Nat.add_assoc, countP_lt_succ]
    have := countP_eq_le_one f hn inj (a + k)
    omega

/-- An element of the list is counted below every larger value but not below its own. -/
theorem countP_lt_lt {l : List β} {x : β} (hx : x ∈ l) {b : Nat} (h : f x < b) :
    l.countP (fun y => decide (f y < f x)) < l.countP (fun y => decide (f y < b)) := by
  have hpos : 0 < l.countP (fun y => decide (f y = f x)) := List.countP_pos_iff.2 ⟨x, hx, by simp⟩
  have hmono : l.countP (fun y => decide (f y < f x + 1)) ≤ l.countP (fun y => decide (f y < b)) :=
    List.countP_mono_left fun y _ hy => by simp at hy ⊢; omega
  rw [countP_lt_succ] at hmono
  omega
end Count

/-- Every situation whose days some numbering embeds passes the check. The counts of step 4 of 1.6 are
    pigeonhole bounds: a day's rank is the number of days with a smaller number. -/
theorem embeddable_complete {α : Type} [DecidableEq α] (E : VE.Environment) (V : EventsEnv)
    (hT : EventsTyped E V = true) (M : VE.FiniteModel α) (valid : M.Valid E) (hn : (M.domains V.day).Nodup)
    (num : α → Nat) (hm : Embeds V M.asStructure num) :
    embeddable V M = true := by
  have _ := valid
  obtain ⟨inj, le, ord, dates⟩ := hm
  have hlt : ∀ p ∈ consecutive V, p.1.num < p.2.num := by
    simp only [EventsTyped, Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hT; exact hT.2
  have inj' : ∀ x ∈ M.domains V.day, ∀ y ∈ M.domains V.day, num x = num y → x = y := fun x hx y hy => inj x y hx hy
  let c : Nat → Nat := fun b => (M.domains V.day).countP (fun y => decide (num y < b))
  have bef : ∀ x ∈ M.domains V.day, ∀ y ∈ M.domains V.day, beforeB V M x y = decide (num x < num y) :=
    fun x hx y hy => decide_eq_decide.2 (ord x y hx hy)
  have rankEq : ∀ x ∈ M.domains V.day, rank V M x = c (num x) := fun x hx => by
    simp only [rank, c, ← List.countP_eq_length_filter]
    exact List.countP_congr fun y hy => by rw [bef y hy x hx]
  have day : ∀ D ∈ V.dates, ∃ x ∈ M.domains V.day, dateDay V M D = some x ∧ num x = D.num := fun D hD => by
    obtain ⟨x, hx, dx, nx⟩ := dates D hD
    have hx : M.constants (dateName D) = some x := hx
    have dx : x ∈ M.domains V.day := dx
    exact ⟨x, dx, by simp [dateDay, hx, dx], nx⟩
  have named : ∀ D ∈ V.dates, namedRank V M D = c D.num := fun D hD => by
    obtain ⟨x, dx, hx, nx⟩ := day D hD
    simp only [namedRank, hx, Option.map_some, Option.getD_some, rankEq x dx, nx]
  have upper : ∀ a k, c (a + k) ≤ c a + k := countP_lt_le num hn inj'
  have below : ∀ D ∈ V.dates, ∀ b, D.num < b → c D.num < c b := fun D hD b h => by
    obtain ⟨x, dx, -, nx⟩ := day D hD
    rw [← nx] at h ⊢; exact countP_lt_lt num dx h
  have all : c (dateMax + 1) = (M.domains V.day).length :=
    List.countP_eq_length.2 fun x hx => by have := le x hx; simp; omega
  have hsl : strictLinearB V M = true := by
    simp only [strictLinearB, Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq, Bool.not_eq_true',
      Bool.or_eq_true, beq_iff_eq]
    refine ⟨⟨⟨hn, fun x hx => ?_⟩, fun x hx y hy z hz => ?_⟩, fun x hx y hy => ?_⟩
    · rw [bef x hx x hx]; simp
    · rw [bef x hx y hy, bef y hy z hz, bef x hx z hz]
      by_cases h1 : num x < num y <;> by_cases h2 : num y < num z <;> simp [h1, h2] <;> omega
    · rw [bef x hx y hy, bef y hy x hx]
      rcases Nat.lt_trichotomy (num x) (num y) with h | h | h
      · simp [h]
      · exact .inl (.inl (inj' x hx y hy h))
      · simp [h]
  have h2 : V.dates.find? (fun D => (dateDay V M D).isNone) = none := List.find?_eq_none.2 fun D hD => by
    obtain ⟨x, -, hx, -⟩ := day D hD; simp [hx]
  have h3 : (consecutive V).find? (fun p => !decide (namedRank V M p.1 < namedRank V M p.2)) = none :=
    List.find?_eq_none.2 fun p hp => by
      obtain ⟨m1, m2⟩ := mem_dates_of_consecutive hp
      simp only [named _ m1, named _ m2, Bool.not_eq_true', decide_eq_false_iff_not, Classical.not_not]
      exact below _ m1 _ (hlt p hp)
  have h4 : (consecutive V).find? (fun p => decide (namedRank V M p.2 - namedRank V M p.1 - 1 >
      p.2.num - p.1.num - 1)) = none := List.find?_eq_none.2 fun p hp => by
    obtain ⟨m1, m2⟩ := mem_dates_of_consecutive hp
    have := upper p.1.num (p.2.num - p.1.num)
    rw [Nat.add_sub_cancel' (Nat.le_of_lt (hlt p hp))] at this
    simp only [named _ m1, named _ m2, decide_eq_true_eq, gt_iff_lt, Nat.not_lt]
    omega
  have h0 : c 0 = 0 := List.countP_eq_zero.2 fun _ _ => by simp
  unfold embeddable calendarCheck
  simp only [hsl, h2, h3, h4, Bool.not_true, Bool.false_eq_true, if_false]
  split
  · have := upper 0 (dateMax + 1)
    rw [Nat.zero_add, h0, all] at this
    rw [if_pos (by omega)]; rfl
  · next D₁ rest hd =>
    have m1 : D₁ ∈ V.dates := by rw [hd]; exact List.mem_cons_self ..
    have mk : (D₁ :: rest).getLastD D₁ ∈ V.dates := by
      rw [hd, List.getLastD_cons]; exact List.getLastD_mem_cons ..
    obtain ⟨x, dx, -, nx⟩ := day _ mk
    have hk := le x dx
    have := upper 0 D₁.num
    rw [Nat.zero_add, h0] at this
    have := upper ((D₁ :: rest).getLastD D₁).num (dateMax + 1 - ((D₁ :: rest).getLastD D₁).num)
    rw [Nat.add_sub_cancel' (by omega), all] at this
    rw [if_neg (by rw [named _ m1]; omega), if_neg (by rw [named _ mk]; omega)]
    rfl

end VE.Events
