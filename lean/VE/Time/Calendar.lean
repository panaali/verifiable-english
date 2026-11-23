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
before year `lo` is `DateRange`, in Python's order. -/
def parseIsoFrom (lo : Nat) (s : String) : Except String Civil :=
  match s.toList with
  | [y1, y2, y3, y4, '-', m1, m2, '-', d1, d2] =>
    match digitsNat [y1, y2, y3, y4], digitsNat [m1, m2], digitsNat [d1, d2] with
    | some y, some m, some d =>
      if 1 ≤ y ∧ 1 ≤ m ∧ m ≤ 12 ∧ 1 ≤ d ∧ d ≤ monthLen y m then
        if lo ≤ y then .ok ⟨y, m, d⟩ else .error s!"DateRange({s})"
      else .error s!"InvalidDate({s})"
    | _, _, _ => .error s!"InvalidDate({s})"
  | _ => .error s!"InvalidDate({s})"

/-- ISO `YYYY-MM-DD` from the epoch: a date before 1970 is `DateRange`. -/
def parseIso (s : String) : Except String Civil := parseIsoFrom 1970 s

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

/-- A date decoded from year `lo` has a valid month and day and a year in `lo..9999`. -/
theorem parseIsoFrom_valid {lo : Nat} {s : String} {D : Civil} (h : parseIsoFrom lo s = .ok D) :
    lo ≤ D.year ∧ D.year ≤ 9999 ∧ 1 ≤ D.month ∧ D.month ≤ 12 ∧ 1 ≤ D.day ∧
      D.day ≤ monthLen D.year D.month := by
  unfold parseIsoFrom at h
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
          exact ⟨by assumption, by simp; omega, hc.2.1, hc.2.2.1, hc.2.2.2.1, hc.2.2.2.2⟩
        · cases h
      · cases h
    · cases h
  · cases h

theorem parseIso_eq (s : String) : parseIso s = parseIsoFrom 1970 s := rfl

/-- Every decoded date is an accepted date. -/
theorem parseIso_valid {s : String} {D : Civil} (h : parseIso s = .ok D) : D.Valid := by
  obtain ⟨h1, h2, h3, h4, h5, h6⟩ := parseIsoFrom_valid h
  exact ⟨⟨h1, h3, h4, h5, h6⟩, h2⟩

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

/-! ## Ground date expressions (date-arith)

A ground date expression (`VE.Time.Wire.elabCal`) is worked out while a statement is
decoded. Its dates may lie from 1900 (`minGroundYear`); only a value that becomes a day
number must be `Valid` (1970..9999). -/

/-- Earliest year a ground date expression may name. -/
def minGroundYear : Nat := 1900

/-- A date a ground date expression may name: a valid month and day, a year in 1900..9999. -/
abbrev Civil.Ground (D : Civil) : Prop :=
  minGroundYear ≤ D.year ∧ D.year ≤ 9999 ∧ 1 ≤ D.month ∧ D.month ≤ 12 ∧ 1 ≤ D.day ∧
    D.day ≤ monthLen D.year D.month

instance (a b : Civil) : Decidable (a.Before b) := by unfold Civil.Before; infer_instance

/-- What a month offset does when the kept day is missing from the target month. -/
inductive MonthEnd where | last | next

/-- `D` plus `k` months (signed): the day is kept; if the target month lacks it, `last` gives
that month's last day, `next` the day after it, and no reading `none` (refused). -/
def Civil.addMonths (D : Civil) (k : Int) (r : Option MonthEnd) : Option Civil :=
  let i : Int := (D.year : Int) * 12 + ((D.month : Int) - 1) + k
  if i < 0 then none else
  let y := (i / 12).toNat
  let m := (i % 12).toNat + 1
  if D.day ≤ monthLen y m then some ⟨y, m, D.day⟩ else
  match r with
  | some .last => some ⟨y, m, monthLen y m⟩
  | some .next => some (Civil.succ ⟨y, m, monthLen y m⟩)
  | none => none

/-- `D'` is `D` plus `k` months under reading `r`: `(y, m)` is `k` months on from `D`'s month;
`D`'s day if it has it, else its last day (`last`) or the day after that (`next`). -/
def Civil.MonthsLater (D : Civil) (k : Int) (r : Option MonthEnd) (D' : Civil) : Prop :=
  ∃ y m : Nat, 1 ≤ m ∧ m ≤ 12 ∧ (y : Int) * 12 + m = D.year * 12 + D.month + k ∧
    if D.day ≤ monthLen y m then D' = ⟨y, m, D.day⟩
    else r = some .last ∧ D' = ⟨y, m, monthLen y m⟩ ∨ r = some .next ∧ D' = Civil.succ ⟨y, m, monthLen y m⟩

/-- Day of the week, 0 = Monday .. 6 = Sunday (day 0, 1970-01-01, was a Thursday). -/
def Civil.weekday (D : Civil) : Nat := (D.num + 3) % 7

/-- The `n`th weekday `w` (0 = Monday) of month `m` of year `y` (1970..9999), if it exists. -/
def nthWeekday (n w m y : Nat) : Option Civil :=
  let d := 1 + (w + 7 - Civil.weekday ⟨y, m, 1⟩) % 7 + 7 * (n - 1)
  if 1970 ≤ y ∧ y ≤ 9999 ∧ 1 ≤ m ∧ m ≤ 12 ∧ 1 ≤ n ∧ w < 7 ∧ d ≤ monthLen y m
  then some ⟨y, m, d⟩ else none

/-! ### Their proofs (SIZING section 3, items 1-7 and 9) -/

theorem monthLen_le {y m : Nat} : monthLen y m ≤ 31 := by
  unfold monthLen; split <;> (try split) <;> omega

/-- Items 1 and 2: a month offset computes `MonthsLater`: the kept day when the target month
has it (item 1), else `last` or `next` (item 2); with no reading it gives nothing then. -/
theorem addMonths_spec {D D' : Civil} {k : Int} {r : Option MonthEnd}
    (h : D.addMonths k r = some D') : D.MonthsLater k r D' := by
  unfold Civil.addMonths at h
  dsimp only at h
  split at h
  · cases h
  · rename_i hi
    refine ⟨((↑D.year * 12 + (↑D.month - 1) + k) / 12).toNat,
      ((↑D.year * 12 + (↑D.month - 1) + k) % 12).toNat + 1, by omega, by omega, by omega, ?_⟩
    split at h
    · rename_i hd; cases h; rw [if_pos hd]
    · rename_i hd
      rw [if_neg hd]
      split at h <;> cases h
      · exact Or.inl ⟨rfl, rfl⟩
      · exact Or.inr ⟨rfl, rfl⟩

/-- Item 2: with no reading, a missing day has no result (refused, never rolled). -/
theorem addMonths_none_missing {D D' : Civil} {k : Int} (h : D.addMonths k none = some D') :
    D'.day = D.day := by
  obtain ⟨y, m, _, _, _, hs⟩ := addMonths_spec h
  split at hs
  · subst hs; rfl
  · simp at hs

theorem succ_monthLast (y m : Nat) : (Civil.mk y m (monthLen y m)).succ =
    if m < 12 then ⟨y, m + 1, 1⟩ else ⟨y + 1, 1, 1⟩ := by simp [Civil.succ]

/-- `MonthsLater` as three outcomes, each by its target month index and day. -/
theorem monthsLater_cases {D D' : Civil} {k : Int} {r : Option MonthEnd} (h : D.MonthsLater k r D') :
    ∃ y m : Nat, 1 ≤ m ∧ m ≤ 12 ∧ (y : Int) * 12 + m = D.year * 12 + D.month + k ∧
      1 ≤ monthLen y m ∧ monthLen y m ≤ 31 ∧
      (D.day ≤ monthLen y m ∧ D' = ⟨y, m, D.day⟩ ∨
       monthLen y m < D.day ∧ r = some .last ∧ D' = ⟨y, m, monthLen y m⟩ ∨
       monthLen y m < D.day ∧ r = some .next ∧ (D'.year : Int) * 12 + D'.month = y * 12 + m + 1 ∧
         1 ≤ D'.month ∧ D'.month ≤ 12 ∧ D'.day = 1) := by
  obtain ⟨y, m, h1, h12, hi, hs⟩ := h
  refine ⟨y, m, h1, h12, hi, monthLen_pos h1 h12, monthLen_le, ?_⟩
  split at hs
  · exact Or.inl ⟨by assumption, hs⟩
  · rcases hs with ⟨hr, rfl⟩ | ⟨hr, rfl⟩
    · exact Or.inr (Or.inl ⟨by omega, hr, rfl⟩)
    · refine Or.inr (Or.inr ⟨by omega, hr, ?_⟩)
      rw [succ_monthLast]; split <;> exact ⟨by simp only; omega, by simp only; omega, by simp only; omega, rfl⟩

/-- Item 3: a result in 1900..9999 has a valid month and day. -/
theorem addMonths_ground {D D' : Civil} {k : Int} {r : Option MonthEnd} (hD : D.Ground)
    (h : D.addMonths k r = some D') (hlo : minGroundYear ≤ D'.year) (hhi : D'.year ≤ 9999) :
    D'.Ground := by
  obtain ⟨y, m, h1, h12, _, hp, _, hs⟩ := monthsLater_cases (addMonths_spec h)
  rcases hs with ⟨hd, rfl⟩ | ⟨_, _, rfl⟩ | ⟨_, _, _, hm1, hm12, hd1⟩
  · exact ⟨hlo, hhi, h1, h12, hD.2.2.2.2.1, hd⟩
  · exact ⟨hlo, hhi, h1, h12, hp, Nat.le_refl _⟩
  · exact ⟨hlo, hhi, hm1, hm12, by omega, by rw [hd1]; exact monthLen_pos hm1 hm12⟩

/-- Item 4: month offsets keep the order of ground dates (when both have a result).
Additivity is not claimed: 31 January plus 1 month plus 1 month is not 31 January plus 2. -/
theorem addMonths_mono {D E D' E' : Civil} {k : Int} {r : Option MonthEnd}
    (hD : D.Ground) (hE : E.Ground) (hle : ¬ E.Before D)
    (h1 : D.addMonths k r = some D') (h2 : E.addMonths k r = some E') : ¬ E'.Before D' := by
  obtain ⟨y, m, m1, m12, hi, _, _, hs⟩ := monthsLater_cases (addMonths_spec h1)
  obtain ⟨y', m', m1', m12', hi', _, _, hs'⟩ := monthsLater_cases (addMonths_spec h2)
  obtain ⟨_, _, _, _, _, _⟩ := hD
  obtain ⟨_, _, _, _, _, _⟩ := hE
  unfold Civil.Before at hle ⊢
  by_cases hyy : y = y' ∧ m = m'
  · obtain ⟨rfl, rfl⟩ := hyy
    rcases hs with ⟨_, rfl⟩ | ⟨_, hr, rfl⟩ | ⟨_, hr, _⟩ <;>
    rcases hs' with ⟨_, rfl⟩ | ⟨_, hr', rfl⟩ | ⟨_, hr', _⟩ <;>
    (try (rw [hr] at hr'; cases hr')) <;> (try simp only) <;> omega
  · rcases hs with ⟨_, rfl⟩ | ⟨_, hr, rfl⟩ | ⟨_, hr, _⟩ <;>
    rcases hs' with ⟨_, rfl⟩ | ⟨_, hr', rfl⟩ | ⟨_, hr', _⟩ <;>
    (try (rw [hr] at hr'; cases hr')) <;> (try simp only) <;> omega

/-- Item 5: the last day of a month is proper and its successor is the first of the next month. -/
theorem monthLast_spec {D : Civil} (h : D.Proper) :
    (Civil.mk D.year D.month (monthLen D.year D.month)).Proper ∧
      (Civil.mk D.year D.month (monthLen D.year D.month)).succ =
        if D.month < 12 then ⟨D.year, D.month + 1, 1⟩ else ⟨D.year + 1, 1, 1⟩ := by
  obtain ⟨hy, h1, h12, _, _⟩ := h
  exact ⟨⟨hy, h1, h12, monthLen_pos h1 h12, Nat.le_refl _⟩, by simp [Civil.succ]⟩

theorem monthFirst_proper {D : Civil} (h : D.Proper) : (Civil.mk D.year D.month 1).Proper :=
  ⟨h.1, h.2.1, h.2.2.1, Nat.le_refl 1, monthLen_pos h.2.1 h.2.2.1⟩

/-- Item 6: 1970-01-01 was a Thursday, and each next day is the next weekday. -/
theorem weekday_epoch : epoch.weekday = 3 := by unfold Civil.weekday; rw [num_epoch]

theorem weekday_succ {D : Civil} (h : D.Proper) : D.succ.weekday = (D.weekday + 1) % 7 := by
  unfold Civil.weekday; rw [num_succ h]; omega

/-- Item 7: the `n`th weekday `w` of a month is a valid date of that month with weekday `w`,
and `n - 1` whole weeks of that month lie before it (so exactly `n - 1` earlier days of the
month share its weekday). -/
theorem nthWeekday_spec {n w m y : Nat} {D : Civil} (h : nthWeekday n w m y = some D) :
    D.Valid ∧ D.year = y ∧ D.month = m ∧ D.weekday = w ∧ 1 ≤ n ∧ (D.day - 1) / 7 = n - 1 := by
  unfold nthWeekday at h
  dsimp only at h
  split at h
  · rename_i hc
    cases h
    obtain ⟨hy, hy9, hm1, hm12, hn, hw, hd⟩ := hc
    have hk : (w + 7 - Civil.weekday ⟨y, m, 1⟩) % 7 < 7 := Nat.mod_lt _ (by decide)
    refine ⟨⟨⟨hy, hm1, hm12, Nat.le_trans (Nat.le_add_right 1 _) (Nat.le_add_right _ _), hd⟩, hy9⟩,
      rfl, rfl, ?_, hn, ?_⟩
    rotate_left
    · dsimp only; omega
    unfold Civil.weekday at *
    simp only [Civil.num] at *
    omega
  · cases h

/-- The decidable order is `Civil.Before`, for dates of any year. -/
theorem decide_before (a b : Civil) : decide (a.Before b) = true ↔ a.Before b := decide_eq_true_iff

end VE.Time
