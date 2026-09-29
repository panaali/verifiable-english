import Std

/-! W6 calendar coordinates (units-schema §6.1). Proleptic Gregorian civil
dates, epoch 1970-01-01 = 0, no time of day and no timezone. The supported
literal/display interval is 1970-01-01 through 9999-12-31, i.e. `0..dateMax`.

Day numbers use a closed form, so conversion is constant time. The facts proved
here are the ones the W6 obligations name: every accepted date has a unique
coordinate (`num_injective`), every coordinate in range is some accepted date
(`exists_valid_of_le`), chronological order is integer order (`before_iff`),
and the civil successor adds exactly one day (`num_succ`). -/
namespace VE.Time

def leap (y : Nat) : Bool := y % 4 == 0 && (y % 100 != 0 || y % 400 == 0)

def yearLen (y : Nat) : Nat := if leap y then 366 else 365

def monthLen (y m : Nat) : Nat :=
  match m with
  | 1 => 31 | 2 => if leap y then 29 else 28 | 3 => 31 | 4 => 30 | 5 => 31 | 6 => 30
  | 7 => 31 | 8 => 31 | 9 => 30 | 10 => 31 | 11 => 30 | 12 => 31 | _ => 0

/-- Days of year `y` before month `m` (months are 1-based). -/
def daysBeforeMonth (y : Nat) : Nat → Nat
  | 0 => 0
  | m + 1 => daysBeforeMonth y m + monthLen y m

/-- Days from the proleptic 0000-01-01 to January 1 of year `y`, counting
leap years in `[0, y)` (year 0 is a Gregorian leap year). -/
def yearStart (y : Nat) : Nat := 365 * y + (y + 3) / 4 - (y + 99) / 100 + (y + 399) / 400

/-- Days from 1970-01-01 to January 1 of year `y` (for `y ≥ 1970`). -/
def daysToYear (y : Nat) : Nat := yearStart y - yearStart 1970

def dateMax : Nat := 2932896

structure Civil where
  year : Nat
  month : Nat
  day : Nat
  deriving DecidableEq, Repr

/-- Month and day are valid for the year; the year is on or after the epoch. -/
def Civil.Proper (D : Civil) : Prop :=
  1970 ≤ D.year ∧ 1 ≤ D.month ∧ D.month ≤ 12 ∧ 1 ≤ D.day ∧ D.day ≤ monthLen D.year D.month

/-- A supported (accepted) date. -/
def Civil.Valid (D : Civil) : Prop := D.Proper ∧ D.year ≤ 9999

def Civil.num (D : Civil) : Nat :=
  daysToYear D.year + daysBeforeMonth D.year D.month + (D.day - 1)

/-- Chronological order of civil dates, defined without day numbers. -/
def Civil.Before (a b : Civil) : Prop :=
  a.year < b.year ∨ a.year = b.year ∧ (a.month < b.month ∨ a.month = b.month ∧ a.day < b.day)

/-- The next civil date. -/
def Civil.succ (D : Civil) : Civil :=
  if D.day < monthLen D.year D.month then ⟨D.year, D.month, D.day + 1⟩
  else if D.month < 12 then ⟨D.year, D.month + 1, 1⟩
  else ⟨D.year + 1, 1, 1⟩

/-- The date `k` civil days after `D`. -/
def Civil.addDays (D : Civil) (k : Nat) : Civil := Nat.repeat Civil.succ k D

def epoch : Civil := ⟨1970, 1, 1⟩
def lastDate : Civil := ⟨9999, 12, 31⟩

/-! ## Year and month arithmetic -/

theorem yearLen_eq (y : Nat) :
    yearLen y = 365 + (if y % 4 = 0 ∧ (y % 100 ≠ 0 ∨ y % 400 = 0) then 1 else 0) := by
  unfold yearLen leap
  by_cases h4 : y % 4 = 0 <;> by_cases h100 : y % 100 = 0 <;> by_cases h400 : y % 400 = 0 <;>
    simp [h4, h100, h400]

/-- Year length as a sum of the three Gregorian divisibility corrections. -/
theorem yearLen_val (y : Nat) : yearLen y = 365 + (if y % 4 = 0 then 1 else 0) -
    (if y % 100 = 0 then 1 else 0) + (if y % 400 = 0 then 1 else 0) := by
  rw [yearLen_eq]
  by_cases h4 : y % 4 = 0 <;> by_cases h100 : y % 100 = 0 <;> by_cases h400 : y % 400 = 0 <;>
    simp only [h4, h100, h400, if_true, if_false, ne_eq, not_true_eq_false, not_false_eq_true,
      and_true, or_false, and_false, or_true] <;> omega

theorem yearStart_succ (y : Nat) : yearStart (y + 1) = yearStart y + yearLen y := by
  have e4 : (y + 1 + 3) / 4 = (y + 3) / 4 + (if y % 4 = 0 then 1 else 0) := by split <;> omega
  have e100 : (y + 1 + 99) / 100 = (y + 99) / 100 + (if y % 100 = 0 then 1 else 0) := by
    split <;> omega
  have e400 : (y + 1 + 399) / 400 = (y + 399) / 400 + (if y % 400 = 0 then 1 else 0) := by
    split <;> omega
  have le1 : (y + 99) / 100 ≤ (y + 3) / 4 := by omega
  unfold yearStart
  rw [e4, e100, e400, yearLen_val]
  split <;> split <;> split <;> omega

theorem yearStart_mono {y y' : Nat} (h : y ≤ y') : yearStart y ≤ yearStart y' := by
  induction h with
  | refl => exact Nat.le_refl _
  | step _ ih => rw [yearStart_succ]; omega

theorem yearLen_ge (y : Nat) : 365 ≤ yearLen y := by rw [yearLen_eq]; split <;> omega

theorem daysToYear_succ {y : Nat} (h : 1970 ≤ y) :
    daysToYear (y + 1) = daysToYear y + yearLen y := by
  have := yearStart_mono h
  unfold daysToYear
  rw [yearStart_succ]
  omega

theorem daysToYear_mono {y y' : Nat} (h : y ≤ y') : daysToYear y ≤ daysToYear y' := by
  unfold daysToYear
  have := yearStart_mono h
  omega

theorem daysBeforeMonth_succ (y m : Nat) :
    daysBeforeMonth y (m + 1) = daysBeforeMonth y m + monthLen y m := rfl

theorem daysBeforeMonth_mono (y : Nat) {m m' : Nat} (h : m ≤ m') :
    daysBeforeMonth y m ≤ daysBeforeMonth y m' := by
  induction h with
  | refl => exact Nat.le_refl _
  | step _ ih => rw [daysBeforeMonth_succ]; omega

theorem daysBeforeMonth_thirteen (y : Nat) : daysBeforeMonth y 13 = yearLen y := by
  simp only [daysBeforeMonth, monthLen, yearLen]
  cases leap y <;> rfl

theorem monthLen_pos {y m : Nat} (h1 : 1 ≤ m) (h12 : m ≤ 12) : 1 ≤ monthLen y m := by
  have : m = 1 ∨ m = 2 ∨ m = 3 ∨ m = 4 ∨ m = 5 ∨ m = 6 ∨ m = 7 ∨ m = 8 ∨ m = 9 ∨ m = 10 ∨
    m = 11 ∨ m = 12 := by omega
  rcases this with h | h | h | h | h | h | h | h | h | h | h | h <;> subst h <;>
    simp only [monthLen] <;> (try split) <;> omega

theorem monthLen_twelve (y : Nat) : monthLen y 12 = 31 := rfl

/-- The day of a proper date lies inside its year. -/
theorem inYear {D : Civil} (h : D.Proper) :
    daysBeforeMonth D.year D.month + (D.day - 1) < yearLen D.year := by
  obtain ⟨_, _, h12, hd, hdm⟩ := h
  have hm := daysBeforeMonth_mono D.year (show D.month + 1 ≤ 13 by omega)
  rw [daysBeforeMonth_succ, daysBeforeMonth_thirteen] at hm
  omega

theorem num_lt_nextYear {D : Civil} (h : D.Proper) : D.num < daysToYear (D.year + 1) := by
  have := inYear h
  rw [daysToYear_succ h.1]
  unfold Civil.num
  omega

/-! ## Order -/

theorem num_lt_of_before {a b : Civil} (ha : a.Proper) (_hb : b.Proper) (h : a.Before b) :
    a.num < b.num := by
  rcases h with hy | ⟨hy, hm | ⟨hm, hd⟩⟩
  · have h1 := num_lt_nextYear ha
    have h2 := daysToYear_mono (show a.year + 1 ≤ b.year by omega)
    unfold Civil.num at *
    omega
  · have h1 := inYear ha
    obtain ⟨_, _, _, hda, hdm⟩ := ha
    have h2 := daysBeforeMonth_mono a.year (show a.month + 1 ≤ b.month by omega)
    rw [daysBeforeMonth_succ] at h2
    unfold Civil.num
    rw [hy] at h2 hdm ⊢
    omega
  · unfold Civil.num
    rw [hy, hm]
    obtain ⟨_, _, _, hda, _⟩ := ha
    omega

theorem before_trichotomy (a b : Civil) : a.Before b ∨ a = b ∨ b.Before a := by
  unfold Civil.Before
  rcases a with ⟨ay, am, ad⟩
  rcases b with ⟨by', bm, bd⟩
  simp only [Civil.mk.injEq]
  omega

/-- Every accepted date has exactly one coordinate. -/
theorem num_injective {a b : Civil} (ha : a.Proper) (hb : b.Proper) (h : a.num = b.num) :
    a = b := by
  rcases before_trichotomy a b with hab | hab | hab
  · have := num_lt_of_before ha hb hab; omega
  · exact hab
  · have := num_lt_of_before hb ha hab; omega

/-- Chronological order agrees with integer order. -/
theorem before_iff {a b : Civil} (ha : a.Proper) (hb : b.Proper) :
    a.Before b ↔ a.num < b.num := by
  constructor
  · exact num_lt_of_before ha hb
  · intro h
    rcases before_trichotomy a b with hab | hab | hab
    · exact hab
    · subst hab; omega
    · have := num_lt_of_before hb ha hab; omega

/-! ## Successor and offsets -/

theorem succ_proper {D : Civil} (h : D.Proper) : D.succ.Proper := by
  obtain ⟨hy, hm1, hm12, hd1, hdm⟩ := h
  unfold Civil.succ
  split
  · refine ⟨hy, hm1, hm12, ?_, ?_⟩ <;> dsimp only <;> omega
  · split
    · refine ⟨hy, ?_, ?_, Nat.le_refl 1, ?_⟩ <;> dsimp only
      · omega
      · omega
      · exact monthLen_pos (by omega) (by omega)
    · refine ⟨?_, Nat.le_refl 1, ?_, Nat.le_refl 1, ?_⟩ <;> dsimp only
      · omega
      · omega
      · simp [monthLen]

theorem num_succ {D : Civil} (h : D.Proper) : D.succ.num = D.num + 1 := by
  obtain ⟨hy, hm1, hm12, hd1, hdm⟩ := h
  unfold Civil.succ
  split
  · unfold Civil.num; simp only; omega
  · rename_i hnot
    split
    · unfold Civil.num
      simp only [daysBeforeMonth_succ]
      omega
    · rename_i h12
      have hm : D.month = 12 := by omega
      have hd : D.day = 31 := by rw [hm, monthLen_twelve] at hdm hnot; omega
      have ht := daysBeforeMonth_thirteen D.year
      rw [daysBeforeMonth_succ, monthLen_twelve] at ht
      unfold Civil.num
      simp only [daysToYear_succ hy, daysBeforeMonth, monthLen]
      rw [hm, hd]
      omega

theorem addDays_zero (D : Civil) : D.addDays 0 = D := rfl

theorem addDays_succ (D : Civil) (k : Nat) : D.addDays (k + 1) = (D.addDays k).succ := rfl

theorem addDays_proper {D : Civil} (h : D.Proper) (k : Nat) : (D.addDays k).Proper := by
  induction k with
  | zero => exact h
  | succ k ih => rw [addDays_succ]; exact succ_proper ih

theorem num_addDays {D : Civil} (h : D.Proper) (k : Nat) : (D.addDays k).num = D.num + k := by
  induction k with
  | zero => rw [addDays_zero, Nat.add_zero]
  | succ k ih => rw [addDays_succ, num_succ (addDays_proper h k), ih]; omega

/-! ## The supported interval -/

theorem daysToYear_epoch : daysToYear 1970 = 0 := by unfold daysToYear; omega

theorem epoch_proper : epoch.Proper := by unfold Civil.Proper epoch; decide

theorem num_epoch : epoch.num = 0 := by
  unfold Civil.num epoch
  simp [daysToYear_epoch, daysBeforeMonth, monthLen]

theorem num_lastDate : lastDate.num = dateMax := by
  simp [Civil.num, lastDate, dateMax, daysToYear, yearStart, daysBeforeMonth, monthLen, leap]

theorem lastDate_valid : lastDate.Valid := by
  unfold Civil.Valid Civil.Proper lastDate; decide

/-- Every natural coordinate is the day number of a proper date. -/
theorem exists_proper (n : Nat) : ∃ D : Civil, D.Proper ∧ D.num = n :=
  ⟨epoch.addDays n, addDays_proper epoch_proper n, by rw [num_addDays epoch_proper, num_epoch]; omega⟩

/-- A proper date is accepted exactly when its coordinate is at most `dateMax`. -/
theorem valid_iff {D : Civil} (h : D.Proper) : D.Valid ↔ D.num ≤ dateMax := by
  constructor
  · intro hv
    rcases before_trichotomy D lastDate with hb | hb | hb
    · have := num_lt_of_before h lastDate_valid.1 hb; rw [num_lastDate] at this; omega
    · rw [hb, num_lastDate]; omega
    · have hy9 := hv.2
      have hm12 := h.2.2.1
      have hdm := h.2.2.2.2
      rcases hb with hy | ⟨hy, hm | ⟨hm, hd⟩⟩
      · simp only [lastDate] at hy; omega
      · simp only [lastDate] at hm; omega
      · simp only [lastDate] at hy hm hd
        rw [← hy, ← hm, monthLen_twelve] at hdm
        omega
  · intro hn
    refine ⟨h, ?_⟩
    apply Classical.byContradiction
    intro hy
    have hb : lastDate.Before D := Or.inl (by simp [lastDate]; omega)
    have := num_lt_of_before lastDate_valid.1 h hb
    rw [num_lastDate] at this
    omega

/-- Every coordinate in `0..dateMax` is the day number of exactly one accepted date. -/
theorem exists_valid_of_le {n : Nat} (hn : n ≤ dateMax) : ∃ D : Civil, D.Valid ∧ D.num = n := by
  obtain ⟨D, hp, hd⟩ := exists_proper n
  exact ⟨D, (valid_iff hp).mpr (hd ▸ hn), hd⟩

/-! ## Executable conversion (the wire decoder) -/

/-- Decidable form of `Civil.Proper`, used by the decoder. -/
def Civil.properB (D : Civil) : Bool :=
  decide (1970 ≤ D.year) && decide (1 ≤ D.month) && decide (D.month ≤ 12) &&
    decide (1 ≤ D.day) && decide (D.day ≤ monthLen D.year D.month)

theorem Civil.properB_iff (D : Civil) : D.properB = true ↔ D.Proper := by
  simp [Civil.properB, Civil.Proper, and_assoc]

def digitValue (c : Char) : Option Nat :=
  if 48 ≤ c.toNat ∧ c.toNat ≤ 57 then some (c.toNat - 48) else none

def digitsNat : List Char → Option Nat
  | [] => some 0
  | c :: cs => do
    let d ← digitValue c
    let rest ← digitsNat cs
    pure (d * 10 ^ cs.length + rest)

/-- ISO `YYYY-MM-DD`. Calendar-invalid text is `InvalidDate`, then a date
before the epoch is `DateRange`, in Python's order. -/
def parseIso (s : String) : Except String Civil :=
  match s.toList with
  | [y1, y2, y3, y4, '-', m1, m2, '-', d1, d2] =>
    match digitsNat [y1, y2, y3, y4], digitsNat [m1, m2], digitsNat [d1, d2] with
    | some y, some m, some d =>
      if 1 ≤ y ∧ 1 ≤ m ∧ m ≤ 12 ∧ 1 ≤ d ∧ d ≤ monthLen y m then
        if 1970 ≤ y then .ok ⟨y, m, d⟩ else .error s!"DateRange({s})"
      else .error s!"InvalidDate({s})"
    | _, _, _ => .error s!"InvalidDate({s})"
  | _ => .error s!"InvalidDate({s})"

theorem digitsNat_bound : ∀ (cs : List Char) (n : Nat), digitsNat cs = some n → n < 10 ^ cs.length
  | [], n, h => by simp [digitsNat] at h; subst h; simp
  | c :: cs, n, h => by
    simp only [digitsNat, Option.bind_eq_bind, Option.bind_eq_some_iff, Option.pure_def,
      Option.some.injEq] at h
    obtain ⟨d, hd, rest, hr, rfl⟩ := h
    have hd' : d < 10 := by
      unfold digitValue at hd
      split at hd
      · rename_i hc
        cases hd
        omega
      · cases hd
    have := digitsNat_bound cs rest hr
    simp only [List.length_cons, Nat.pow_succ]
    have : d * 10 ^ cs.length + rest < (d + 1) * 10 ^ cs.length := by
      rw [Nat.add_mul, Nat.one_mul]; omega
    have : (d + 1) * 10 ^ cs.length ≤ 10 * 10 ^ cs.length := Nat.mul_le_mul_right _ hd'
    rw [Nat.mul_comm (10 ^ cs.length) 10]
    omega

/-- Every decoded date is an accepted date. -/
theorem parseIso_valid {s : String} {D : Civil} (h : parseIso s = .ok D) : D.Valid := by
  unfold parseIso at h
  split at h
  · rename_i y1 y2 y3 y4 m1 m2 d1 d2 _
    split at h
    · rename_i y m d hy _ _
      have hb := digitsNat_bound _ _ hy
      simp only [List.length_cons, List.length_nil] at hb
      split at h
      · rename_i hc
        split at h
        · cases h
          exact ⟨⟨by assumption, hc.2.1, hc.2.2.1, hc.2.2.2.1, hc.2.2.2.2⟩, by simp; omega⟩
        · cases h
      · cases h
    · cases h
  · cases h

def pad (width : Nat) (n : Nat) : String :=
  let s := toString n
  String.mk (List.replicate (width - s.length) '0') ++ s

def Civil.iso (D : Civil) : String := s!"{pad 4 D.year}-{pad 2 D.month}-{pad 2 D.day}"

/-- The accepted date with coordinate `n`, by year and month search whose result
is checked, so a returned date always has exactly this coordinate. -/
def findYear (n : Nat) : Nat → Nat → Nat
  | 0, y => y
  | fuel + 1, y => if daysToYear (y + 1) ≤ n then findYear n fuel (y + 1) else y

/-- The month of day-of-year `r` in year `y`, searching upward from month `m`. -/
def findMonth (y r : Nat) : Nat → Nat → Nat
  | 0, m => m
  | fuel + 1, m => if m < 12 ∧ daysBeforeMonth y (m + 1) ≤ r then findMonth y r fuel (m + 1) else m

/-- The candidate date for coordinate `n`; `civilCandidate_spec` proves it is the
accepted date with that coordinate whenever `n ≤ dateMax`. -/
def civilCandidate (n : Nat) : Civil :=
  let y := findYear n 64 (1970 + n / 366)
  let r := n - daysToYear y
  let m := findMonth y r 11 1
  ⟨y, m, r - daysBeforeMonth y m + 1⟩

def checkedCivil (n : Nat) (D : Civil) : Option Civil :=
  if D.properB && D.num == n && decide (D.year ≤ 9999) then some D else none

def civilOf (n : Nat) : Option Civil := checkedCivil n (civilCandidate n)

theorem checkedCivil_sound {n : Nat} {C D : Civil} (h : checkedCivil n C = some D) :
    D.Valid ∧ D.num = n := by
  unfold checkedCivil at h
  split at h
  · rename_i hc
    cases h
    simp only [Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq] at hc
    exact ⟨⟨(Civil.properB_iff _).mp hc.1.1, hc.2⟩, hc.1.2⟩
  · cases h

theorem civilOf_sound {n : Nat} {D : Civil} (h : civilOf n = some D) : D.Valid ∧ D.num = n :=
  checkedCivil_sound h

theorem yearLen_le (y : Nat) : yearLen y ≤ 366 := by rw [yearLen_eq]; split <;> omega

/-- Each year after the epoch has 365 or 366 days. -/
theorem daysToYear_bounds (k : Nat) :
    365 * k ≤ daysToYear (1970 + k) ∧ daysToYear (1970 + k) ≤ 366 * k := by
  induction k with
  | zero => simp [daysToYear_epoch]
  | succ k ih =>
    rw [show 1970 + (k + 1) = 1970 + k + 1 by omega, daysToYear_succ (by omega)]
    have := yearLen_ge (1970 + k)
    have := yearLen_le (1970 + k)
    omega

/-- The year search ends at the year containing `n` if that year is within reach. -/
theorem findYear_spec (n : Nat) : ∀ (fuel y : Nat), daysToYear y ≤ n →
    n < daysToYear (y + fuel + 1) →
    daysToYear (findYear n fuel y) ≤ n ∧ n < daysToYear (findYear n fuel y + 1) ∧
      y ≤ findYear n fuel y
  | 0, y, h1, h2 => by
    simp only [findYear]
    exact ⟨h1, by simpa using h2, Nat.le_refl y⟩
  | fuel + 1, y, h1, h2 => by
    rw [findYear]
    split
    · rename_i h
      have := findYear_spec n fuel (y + 1) h (by rw [show y + 1 + fuel + 1 = y + (fuel + 1) + 1 by omega]; exact h2)
      exact ⟨this.1, this.2.1, by omega⟩
    · rename_i h
      exact ⟨h1, by omega, Nat.le_refl y⟩

/-- The month search ends at the month containing day-of-year `r`. -/
theorem findMonth_spec (y r : Nat) : ∀ (fuel m : Nat), 1 ≤ m → m ≤ 12 →
    daysBeforeMonth y m ≤ r → 12 ≤ m + fuel →
    1 ≤ findMonth y r fuel m ∧ findMonth y r fuel m ≤ 12 ∧
      daysBeforeMonth y (findMonth y r fuel m) ≤ r ∧
      (findMonth y r fuel m = 12 ∨ r < daysBeforeMonth y (findMonth y r fuel m + 1))
  | 0, m, h1, h12, hd, hf => ⟨h1, h12, hd, Or.inl (show m = 12 by omega)⟩
  | fuel + 1, m, h1, h12, hd, hf => by
    unfold findMonth
    split
    · rename_i h
      exact findMonth_spec y r fuel (m + 1) (by omega) (by omega) h.2 (by omega)
    · rename_i h
      refine ⟨h1, h12, hd, ?_⟩
      by_cases hm : m < 12
      · exact Or.inr (by omega)
      · exact Or.inl (by omega)

theorem daysToYear_tenThousand : daysToYear 10000 = dateMax + 1 := by
  simp [daysToYear, yearStart, dateMax]

/-- **Completeness of conversion**: every coordinate in `0..dateMax` has its
accepted date as the candidate. -/
theorem civilCandidate_spec {n : Nat} (hn : n ≤ dateMax) :
    (civilCandidate n).Valid ∧ (civilCandidate n).num = n := by
  have hmax : dateMax = 2932896 := rfl
  have hlo := (daysToYear_bounds (n / 366)).2
  have hhi := (daysToYear_bounds (n / 366 + 65)).1
  obtain ⟨hy1, hy2, hy3⟩ := findYear_spec n 64 (1970 + n / 366) (by omega)
    (by rw [show 1970 + n / 366 + 64 + 1 = 1970 + (n / 366 + 65) by omega]; omega)
  unfold civilCandidate
  dsimp only
  generalize findYear n 64 (1970 + n / 366) = y at hy1 hy2 hy3
  have hy : 1970 ≤ y := by omega
  rw [daysToYear_succ hy] at hy2
  have hyl := daysBeforeMonth_thirteen y
  obtain ⟨hm1, hm12, hmd, hmr⟩ := findMonth_spec y (n - daysToYear y) 11 1 (by omega) (by omega)
    (by simp [daysBeforeMonth, monthLen]) (by omega)
  generalize findMonth y (n - daysToYear y) 11 1 = m at hm1 hm12 hmd hmr
  have hlen : n - daysToYear y - daysBeforeMonth y m < monthLen y m := by
    rcases hmr with hm | hm
    · subst hm
      rw [daysBeforeMonth_succ] at hyl
      omega
    · rw [daysBeforeMonth_succ] at hm
      omega
  have h9999 : y ≤ 9999 := by
    apply Classical.byContradiction
    intro hc
    have := daysToYear_mono (show 10000 ≤ y by omega)
    rw [daysToYear_tenThousand] at this
    omega
  have hday : 1 ≤ n - daysToYear y - daysBeforeMonth y m + 1 := by omega
  have hdm : n - daysToYear y - daysBeforeMonth y m + 1 ≤ monthLen y m := by omega
  have hnum : daysToYear y + daysBeforeMonth y m + (n - daysToYear y - daysBeforeMonth y m + 1 - 1)
      = n := by omega
  exact ⟨⟨⟨hy, hm1, hm12, hday, hdm⟩, h9999⟩, hnum⟩

/-- Every coordinate in `0..dateMax` converts to a date. -/
theorem civilOf_complete {n : Nat} (hn : n ≤ dateMax) : civilOf n = some (civilCandidate n) := by
  obtain ⟨⟨hp, h9⟩, hnum⟩ := civilCandidate_spec hn
  unfold civilOf checkedCivil
  rw [if_pos]
  simp [(Civil.properB_iff _).mpr hp, hnum, h9]

/-- **Calendar inverse**: every accepted date converts to its coordinate and back. -/
theorem civilOf_num {D : Civil} (hD : D.Valid) : civilOf D.num = some D := by
  have h := civilOf_complete ((valid_iff hD.1).mp hD)
  rw [h, num_injective (civilCandidate_spec ((valid_iff hD.1).mp hD)).1.1 hD.1
    (civilCandidate_spec ((valid_iff hD.1).mp hD)).2]

/-- Conversion is defined exactly on `0..dateMax`. -/
theorem civilOf_isSome_iff (n : Nat) : (civilOf n).isSome ↔ n ≤ dateMax := by
  constructor
  · intro h
    obtain ⟨D, hD⟩ := Option.isSome_iff_exists.mp h
    obtain ⟨hv, hn⟩ := civilOf_sound hD
    exact hn ▸ (valid_iff hv.1).mp hv
  · intro h
    rw [civilOf_complete h]
    rfl

end VE.Time
