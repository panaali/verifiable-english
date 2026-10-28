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

/-! ## Proofs: the numbering embeds every situation that passes the check -/

theorem pairwise_of_chain {β : Type} (R : β → β → Prop) (trans : ∀ a b c, R a b → R b c → R a c) :
    ∀ (l : List β), (∀ p ∈ l.zip l.tail, R p.1 p.2) → l.Pairwise R
  | [], _ => .nil
  | a :: rest, h => .cons (chain_head R trans rest a h) (pairwise_of_chain R trans rest fun p hp => h p (by
      cases rest with
      | nil => simp at hp
      | cons c rest => exact List.mem_cons_of_mem _ hp))

/-- In a list related pairwise in order, every element is its last element or related to it. -/
theorem rel_getLast {β : Type} {R : β → β → Prop} {l : List β} (hp : l.Pairwise R) {E : β}
    (he : l.getLast? = some E) : ∀ D ∈ l, D = E ∨ R D E := by
  obtain ⟨ys, rfl⟩ := List.getLast?_eq_some_iff.1 he
  intro D hD
  rcases List.mem_append.1 hD with hD | hD
  · exact .inr ((List.pairwise_append.1 hp).2.2 D hD E (by simp))
  · exact .inl (by simpa using hD)

/-- A count grows strictly when the counted property grows and gains an element. -/
theorem countP_lt_of {β : Type} {p q : β → Bool} : ∀ {l : List β}, (∀ z ∈ l, p z = true → q z = true) →
    ∀ {x : β}, x ∈ l → q x = true → p x = false → l.countP p < l.countP q
  | [], _, _, hx, _, _ => absurd hx List.not_mem_nil
  | y :: l, hpq, x, hx, hq, hp => by
    have mono : l.countP p ≤ l.countP q := List.countP_mono_left fun z hz => hpq z (.tail _ hz)
    rw [List.countP_cons, List.countP_cons]
    rcases List.mem_cons.1 hx with rfl | hx
    · simp [hq, hp]; omega
    · have := countP_lt_of (fun z hz => hpq z (.tail _ hz)) hx hq hp
      by_cases hy : p y = true
      · simp [hy, hpq y (.head _) hy]; omega
      · by_cases hy' : q y = true <;> simp [hy, hy'] <;> omega

/-- The check passes only when the numbering embeds the situation (the check itself gives the calendar premises on
    the situation's days, so none is assumed: SR-B2). A day's number is its rank plus the offset (date number minus
    rank) of the last named day at or below it; the gap bounds make the offsets grow, and the year bound of
    `EventsTyped` keeps the last date, so every day, within `dateMax`. -/
theorem embeddable_sound {α : Type} [DecidableEq α] (E : VE.Environment) (V : EventsEnv)
    (hT : EventsTyped E V = true) (M : VE.FiniteModel α) (valid : M.Valid E) (he : embeddable V M = true) :
    Embeds V M.asStructure (numbering V M) := by
  have _ := valid
  simp only [EventsTyped, Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hT
  have hlt := hT.2
  have hmax : ∀ D ∈ V.dates, D.num ≤ dateMax := fun D hD => by
    have hp := (VE.Time.Civil.properB_iff D).1 (hT.1.2 D hD).1.1
    exact (VE.Time.valid_iff hp).1 ⟨hp, (hT.1.2 D hD).1.2⟩
  let r := namedRank V M
  unfold embeddable calendarCheck at he
  by_cases hsl : strictLinearB V M = true
  case neg => simp [hsl] at he
  simp only [hsl, Bool.not_true, Bool.false_eq_true, if_false] at he
  split at he
  · simp at he
  rename_i h2
  split at he
  · simp at he
  rename_i h3
  simp only [strictLinearB, Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq, Bool.not_eq_true',
    Bool.or_eq_true, beq_iff_eq] at hsl
  obtain ⟨⟨⟨-, irr⟩, tr⟩, tot⟩ := hsl
  have trans : ∀ x ∈ M.domains V.day, ∀ y ∈ M.domains V.day, ∀ z ∈ M.domains V.day,
      beforeB V M x y = true → beforeB V M y z = true → beforeB V M x z = true := fun x hx y hy z hz h₁ h₂ => by
    rcases tr x hx y hy z hz with h | h
    · simp [h₁, h₂] at h
    · exact h
  have rankLt : ∀ x ∈ M.domains V.day, rank V M x < (M.domains V.day).length := fun x hx =>
    List.length_filter_lt_length_iff_exists.2 ⟨x, hx, by simp [irr x hx]⟩
  have rankMono : ∀ x ∈ M.domains V.day, ∀ y ∈ M.domains V.day, beforeB V M x y = true →
      rank V M x < rank V M y := fun x hx y hy h => by
    simp only [rank, ← List.countP_eq_length_filter]
    exact countP_lt_of (fun z hz hzx => trans z hz x hx y hy hzx h) hx h (irr x hx)
  have day : ∀ D ∈ V.dates, ∃ x ∈ M.domains V.day, M.constants (dateName D) = some x ∧
      namedRank V M D = rank V M x := fun D hD => by
    have := List.find?_eq_none.1 h2 D hD
    cases hd : dateDay V M D with
    | none => simp [hd] at this
    | some x =>
      obtain ⟨hc, hx⟩ := Option.filter_eq_some_iff.1 hd
      exact ⟨x, by simpa using hx, hc, by simp [namedRank, hd]⟩
  -- a day's number is its rank plus a growing offset
  obtain ⟨h, hnum, hmono, hdate, hbound⟩ : ∃ h : Nat → Nat,
      (∀ x, numbering V M x = rank V M x + h (rank V M x)) ∧ (∀ k k', k ≤ k' → h k ≤ h k') ∧
      (∀ D ∈ V.dates, namedRank V M D + h (namedRank V M D) = D.num) ∧
      (∀ x ∈ M.domains V.day, rank V M x + h (rank V M x) ≤ dateMax) := by
    split at he
    · next hd =>
      refine ⟨fun _ => 0, fun x => ?_, fun _ _ _ => Nat.le_refl _, fun D hD => by simp [hd] at hD, fun x hx => ?_⟩
      · simp [numbering, hd]
      · have := rankLt x hx
        dsimp only
        split at he
        · omega
        · simp at he
    · next D₁ rest hd =>
      split at he
      · simp at he
      rename_i h1
      split at he
      · simp at he
      rename_i h4
      split at he
      · simp at he
      rename_i h5
      let P : Civil → Civil → Prop := fun D E => namedRank V M D < namedRank V M E ∧
        (namedRank V M D ≤ D.num → namedRank V M E ≤ E.num ∧ D.num - namedRank V M D ≤ E.num - namedRank V M E)
      have pw : V.dates.Pairwise P := pairwise_of_chain P (fun a b c ab bc => by
          refine ⟨Nat.lt_trans ab.1 bc.1, fun ha => ?_⟩
          obtain ⟨hb, hb'⟩ := ab.2 ha
          obtain ⟨hc, hc'⟩ := bc.2 hb
          exact ⟨hc, by omega⟩) V.dates (fun p hp => by
        have a := List.find?_eq_none.1 h3 p hp
        have b := List.find?_eq_none.1 h4 p hp
        have c := hlt p hp
        simp only [Bool.not_eq_true', decide_eq_false_iff_not, Classical.not_not, decide_eq_true_eq] at a b
        exact ⟨a, fun _ => ⟨by omega, by omega⟩⟩)
      have m1 : D₁ ∈ V.dates := by rw [hd]; exact List.mem_cons_self ..
      have headRel : ∀ D ∈ V.dates, D = D₁ ∨ P D₁ D := fun D hD => by
        rw [hd] at hD pw
        rcases List.mem_cons.1 hD with rfl | hD
        · exact .inl rfl
        · exact .inr ((List.pairwise_cons.1 pw).1 D hD)
      have offOk : ∀ D ∈ V.dates, namedRank V M D ≤ D.num := fun D hD => by
        rcases headRel D hD with rfl | hP
        · omega
        · exact (hP.2 (by omega)).1
      have off : ∀ D ∈ V.dates, ∀ D', D = D' ∨ P D D' →
          D.num - namedRank V M D ≤ D'.num - namedRank V M D' := fun D hD D' h => by
        rcases h with rfl | h
        · exact Nat.le_refl _
        · exact (h.2 (offOk D hD)).2
      have lastF : ∀ k D', (V.dates.filter (fun D => decide (namedRank V M D ≤ k))).getLast? = some D' →
          D' ∈ V.dates ∧ namedRank V M D' ≤ k ∧ ∀ D ∈ V.dates, namedRank V M D ≤ k → D = D' ∨ P D D' :=
        fun k D' hL => by
          have hm := List.mem_filter.1 (List.mem_of_getLast? hL)
          exact ⟨hm.1, by simpa using hm.2, fun D hD hk =>
            rel_getLast (pw.filter _) hL D (List.mem_filter.2 ⟨hD, by simpa using hk⟩)⟩
      have noneF : ∀ k, (V.dates.filter (fun D => decide (namedRank V M D ≤ k))).getLast? = none →
          ∀ D ∈ V.dates, k < namedRank V M D := fun k hN D hD => by
        have := List.filter_eq_nil_iff.1 (List.getLast?_eq_none_iff.1 hN) D hD
        simp at this; omega
      refine ⟨fun k => match (V.dates.filter (fun D => decide (namedRank V M D ≤ k))).getLast? with
        | some D => D.num - namedRank V M D
        | none => D₁.num - namedRank V M D₁, fun x => ?_, fun k k' hk => ?_, fun D hD => ?_, fun x hx => ?_⟩
      · simp only [numbering]
        split
        · next D hL =>
          have := (lastF _ D hL).2.1; have := offOk D (lastF _ D hL).1
          omega
        · next hL =>
          rw [hd]; dsimp only
          have := noneF _ hL D₁ m1; have := offOk D₁ m1
          omega
      · dsimp only
        split
        · next D hL =>
          obtain ⟨hD, hkD, -⟩ := lastF k D hL
          split
          · next D' hL' => exact off D hD D' ((lastF k' D' hL').2.2 D hD (by omega))
          · next hL' => exact absurd (noneF k' hL' D hD) (by omega)
        · next hL =>
          split
          · next D' hL' => exact off D₁ m1 D' ((headRel D' (lastF k' D' hL').1).imp_left Eq.symm)
          · exact Nat.le_refl _
      · dsimp only
        split
        · next D' hL =>
          obtain ⟨-, hk, hall⟩ := lastF _ D' hL
          rcases hall D hD (Nat.le_refl _) with rfl | hP
          · have := offOk D hD; omega
          · exact absurd hP.1 (by omega)
        · next hL => exact absurd (noneF _ hL D hD) (Nat.lt_irrefl _)
      · obtain ⟨Dk, hDk⟩ : ∃ Dk, Dk = (D₁ :: rest).getLastD D₁ := ⟨_, rfl⟩
        rw [← hDk] at h5
        have mk : Dk ∈ V.dates := by rw [hd, hDk, List.getLastD_cons]; exact List.getLastD_mem_cons ..
        have hlast : V.dates.getLast? = some Dk := by
          rw [hd, hDk, List.getLast?_cons, List.getLastD_cons, List.getLastD_eq_getLast?]
        have toLast : ∀ D ∈ V.dates, D = Dk ∨ P D Dk := rel_getLast pw hlast
        have hk : (match (V.dates.filter (fun D => decide (namedRank V M D ≤ rank V M x))).getLast? with
            | some D => D.num - namedRank V M D
            | none => D₁.num - namedRank V M D₁) ≤ Dk.num - namedRank V M Dk := by
          split
          · next D hL => exact off D (lastF _ D hL).1 Dk (toLast D (lastF _ D hL).1)
          · exact off D₁ m1 Dk (toLast D₁ m1)
        obtain ⟨y, hy, -, hr⟩ := day Dk mk
        have := rankLt y hy; have := rankLt x hx; have := offOk Dk mk; have := hmax Dk mk
        dsimp only
        omega
  refine ⟨fun x y hx hy heq => ?_, fun x hx => by rw [hnum]; exact hbound x hx, fun x y hx hy => ?_,
    fun D hD => ?_⟩
  · have hx : x ∈ M.domains V.day := hx
    have hy : y ∈ M.domains V.day := hy
    rw [hnum, hnum] at heq
    rcases tot x hx y hy with (h' | h') | h'
    · exact h'
    · have := rankMono x hx y hy h'; have := hmono _ _ (Nat.le_of_lt this); omega
    · have := rankMono y hy x hx h'; have := hmono _ _ (Nat.le_of_lt this); omega
  · have hx : x ∈ M.domains V.day := hx
    have hy : y ∈ M.domains V.day := hy
    show [x, y] ∈ M.relations V.before ↔ numbering V M x < numbering V M y
    have hb : [x, y] ∈ M.relations V.before ↔ beforeB V M x y = true := by simp [beforeB]
    rw [hb, hnum, hnum]
    constructor
    · intro h'; have := rankMono x hx y hy h'; have := hmono _ _ (Nat.le_of_lt this); omega
    · intro h'
      rcases tot x hx y hy with (rfl | h'') | h''
      · omega
      · exact h''
      · have := rankMono y hy x hx h''; have := hmono _ _ (Nat.le_of_lt this); omega
  · obtain ⟨x, hx, hc, hr⟩ := day D hD
    exact ⟨x, hc, hx, by rw [hnum, ← hr]; exact hdate D hD⟩

end VE.Events
