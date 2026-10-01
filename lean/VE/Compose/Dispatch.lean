import VE.Route.Gate
import VE.SpeechActs.Wire

/-! The dispatcher (docs/spec/composition.md 1.1 to 1.3, 4.2, 8, 9.3).

`today` is `ve/profiles.py` `checker_family`, check for check and text for text, followed by today's route
choice. `dispatch` is `today` on the list without the stack's wrapper profiles, followed by the wrappers: each
present wrapper must sit on that route, and the head is the first wrapper present in stack order, or the
route itself. It is the function the wrappers will call; S0 calls it nowhere. -/
namespace VE.Compose

def unsupported (message : String) : String := "UnsupportedProfile: " ++ message

def registered : List String :=
  ["alternatives@0", "closure@0", "data@0", "definitions@0", "documents@1", "nary@0", "norms@0", "soft-norms@0",
   "order@0", "relational-fol@0", "speech-acts@0", "reports@0", "risk@0", "rights@0", "time@0"]
def speechAllow : List String := ["relational-fol@0", "norms@0", "speech-acts@0"]
/-- The stack's wrapper profiles, in stack order (ranks 1, 2, 3). -/
def wrapperProfiles : List String := ["ve.discourse@1", "right-clauses@0", "readings@1"]

inductive Route
  | frozen | reports | speechActs | alternatives | risk
  | norms | soft | rights
  | readings | clauses | discourse
  deriving DecidableEq, Repr

/-- ve/profiles.py checker_family as a gate: the fifteen checks of 4.2 in order, with its texts. -/
def todayGate (ps : List String) : Except String Unit :=
  if !decide (ps.Pairwise (· < ·)) then .error (unsupported "profiles must be sorted and unique")
  else if ps.contains "alternatives@0" && !ps.contains "norms@0" then
    .error (unsupported "alternatives@0 requires norms@0")
  else if ps.contains "alternatives@0" && ps.contains "soft-norms@0" then
    .error (unsupported "alternatives@0 with soft-norms@0")
  else if ps.contains "risk@0" && !ps.contains "alternatives@0" then
    .error (unsupported "risk@0 requires alternatives@0")
  else match ps.find? (fun p => !registered.contains p) with
  | some p => .error (unsupported s!"Unsupported profile {p}")
  | none =>
  if ps.contains "speech-acts@0" && !ps.contains "norms@0" then
    .error (unsupported "speech-acts@0 requires norms@0")
  else match (if ps.contains "speech-acts@0" then ps.find? (fun p => !speechAllow.contains p) else none) with
  | some p => .error (unsupported s!"speech-acts@0 with {p}")
  | none =>
  if !ps.contains "relational-fol@0" then .error (unsupported "Missing profile relational-fol@0")
  else match (if ps.contains "reports@0" then ["norms@0", "definitions@0", "data@0"].find? ps.contains
              else none) with
  | some p => .error (unsupported s!"reports@0 with {p} layers")
  | none =>
  match (if ps.contains "reports@0" then ["closure@0", "nary@0", "order@0"].find? ps.contains else none) with
  | some p => .error (unsupported s!"reports@0 requires the fol checker, not {p}")
  | none =>
  if ps.contains "order@0" && ps.contains "closure@0" then
    .error (unsupported "Unsupported profile combination closure@0 x order@0")
  else if ps.contains "order@0" && ps.contains "nary@0" then
    .error (unsupported "Unsupported profile combination nary@0 x order@0")
  else if ps.contains "nary@0" && !ps.contains "closure@0" then
    .error (unsupported "Unsupported profile nary@0 without closure@0")
  else if ps.contains "risk@0" && (ps.contains "closure@0" || ps.contains "nary@0" || ps.contains "order@0") then
    .error (unsupported "the risk norms route admits FOL documents only")
  else if ps.contains "rights@0" && !ps.contains "soft-norms@0" then
    .error (unsupported "rights@0 requires soft-norms@0")
  else if ps.contains "soft-norms@0" && !ps.contains "norms@0" then
    .error (unsupported "soft-norms@0 requires norms@0")
  else .ok ()

def todayHead (ps : List String) : Route :=
  if ps.contains "risk@0" then .risk else if ps.contains "alternatives@0" then .alternatives
  else if ps.contains "speech-acts@0" then .speechActs else if ps.contains "reports@0" then .reports
  else if ps.contains "rights@0" then .rights else if ps.contains "soft-norms@0" then .soft
  else if ps.contains "norms@0" then .norms else .frozen

def today (ps : List String) : Except String Route := (todayGate ps).map (fun _ => todayHead ps)

/-- The independent specification of a list today's gate accepts. -/
def TodayList (ps : List String) : Prop :=
  ps.Pairwise (· < ·) ∧ (∀ p ∈ ps, p ∈ registered) ∧ "relational-fol@0" ∈ ps ∧
  ("alternatives@0" ∈ ps → "norms@0" ∈ ps ∧ "soft-norms@0" ∉ ps) ∧
  ("risk@0" ∈ ps → "alternatives@0" ∈ ps ∧ "closure@0" ∉ ps ∧ "nary@0" ∉ ps ∧ "order@0" ∉ ps) ∧
  ("speech-acts@0" ∈ ps → "norms@0" ∈ ps ∧ ∀ p ∈ ps, p ∈ speechAllow) ∧
  ("reports@0" ∈ ps → ∀ p ∈ ["norms@0", "definitions@0", "data@0", "closure@0", "nary@0", "order@0"], p ∉ ps) ∧
  ("order@0" ∈ ps → "closure@0" ∉ ps ∧ "nary@0" ∉ ps) ∧ ("nary@0" ∈ ps → "closure@0" ∈ ps) ∧
  ("rights@0" ∈ ps → "soft-norms@0" ∈ ps) ∧ ("soft-norms@0" ∈ ps → "norms@0" ∈ ps)

/-! ## `today` against its specifications -/

theorem contains_eq (ps : List String) (x : String) : ps.contains x = decide (x ∈ ps) := by
  rw [Bool.eq_iff_iff, decide_eq_true_iff]
  exact List.contains_iff_mem

theorem ite_error_ok {α : Type} {c : Prop} [Decidable c] {e : String} {r : Except String α} {x : α}
    (h : (if c then .error e else r) = .ok x) : ¬ c ∧ r = .ok x := by
  by_cases hc : c
  · rw [if_pos hc] at h; cases h
  · rw [if_neg hc] at h; exact ⟨hc, h⟩

theorem todayGate_sound (ps : List String) (h : todayGate ps = .ok ()) : TodayList ps := by
  unfold todayGate at h
  obtain ⟨hs, h⟩ := ite_error_ok h
  obtain ⟨h1, h⟩ := ite_error_ok h
  obtain ⟨h2, h⟩ := ite_error_ok h
  obtain ⟨h3, h⟩ := ite_error_ok h
  split at h
  · cases h
  rename_i hreg
  obtain ⟨h4, h⟩ := ite_error_ok h
  split at h
  · cases h
  rename_i hsp
  obtain ⟨hrf, h⟩ := ite_error_ok h
  split at h
  · cases h
  rename_i hrep1
  split at h
  · cases h
  rename_i hrep2
  obtain ⟨h5, h⟩ := ite_error_ok h
  obtain ⟨h6, h⟩ := ite_error_ok h
  obtain ⟨h7, h⟩ := ite_error_ok h
  obtain ⟨h8, h⟩ := ite_error_ok h
  obtain ⟨h9, h⟩ := ite_error_ok h
  obtain ⟨h10, h⟩ := ite_error_ok h
  have mem : ∀ {l : List String} {x : String}, ¬ (!l.contains x) = true → x ∈ l := fun h =>
    List.contains_iff_mem.mp (by simpa using h)
  have nmem : ∀ {x : String}, ¬ ps.contains x = true → x ∉ ps := fun h hx => h (List.contains_iff_mem.mpr hx)
  simp only [contains_eq, Bool.not_eq_true', decide_eq_false_iff_not, Bool.and_eq_true, Bool.or_eq_true,
    decide_eq_true_eq, not_and, not_or, Classical.not_not] at hs h1 h2 h3 h4 hrf h5 h6 h7 h8 h9 h10
  refine ⟨hs, fun p hp => mem (List.find?_eq_none.mp hreg p hp), hrf, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro ha; exact ⟨h1 ha, h2 ha⟩
  · intro hr
    exact ⟨h3 hr, fun hc => (h8 hr).1.1 hc, fun hn => (h8 hr).1.2 hn, fun ho => (h8 hr).2 ho⟩
  · intro hsa
    refine ⟨h4 hsa, fun p hp => ?_⟩
    rw [if_pos (List.contains_iff_mem.mpr hsa)] at hsp
    exact mem (List.find?_eq_none.mp hsp p hp)
  · intro hr p hp
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hp
    rw [if_pos (List.contains_iff_mem.mpr hr)] at hrep1 hrep2
    have e1 := List.find?_eq_none.mp hrep1
    have e2 := List.find?_eq_none.mp hrep2
    rcases hp with rfl | rfl | rfl | rfl | rfl | rfl
    · exact nmem (e1 _ (by simp))
    · exact nmem (e1 _ (by simp))
    · exact nmem (e1 _ (by simp))
    · exact nmem (e2 _ (by simp))
    · exact nmem (e2 _ (by simp))
    · exact nmem (e2 _ (by simp))
  · intro ho; exact ⟨h5 ho, h6 ho⟩
  · intro hn; exact h7 hn
  · intro hr; exact h9 hr
  · intro hsn; exact h10 hsn

theorem ite_ok_of {α : Type} {c : Prop} [Decidable c] {e : String} {r : Except String α} {x : α}
    (hc : ¬ c) (h : r = .ok x) : (if c then .error e else r) = .ok x := by
  rw [if_neg hc]; exact h

theorem todayGate_complete (ps : List String) (h : TodayList ps) : todayGate ps = .ok () := by
  obtain ⟨hs, hreg, hrf, ha, hr, hsp, hrep, ho, hn, hri, hso⟩ := h
  have cm := contains_eq ps
  have nm : ∀ {x : String}, x ∉ ps → ps.contains x = false := fun hx => by rw [cm]; exact decide_eq_false hx
  have ym : ∀ {x : String}, x ∈ ps → ps.contains x = true := fun hx => by rw [cm]; exact decide_eq_true hx
  unfold todayGate
  refine ite_ok_of (by simpa using hs) ?_
  refine ite_ok_of ?_ ?_
  · intro hc
    simp only [Bool.and_eq_true, Bool.not_eq_true'] at hc
    rw [ym (ha (List.contains_iff_mem.mp hc.1)).1] at hc
    cases hc.2
  refine ite_ok_of ?_ ?_
  · intro hc
    simp only [Bool.and_eq_true] at hc
    exact (ha (List.contains_iff_mem.mp hc.1)).2 (List.contains_iff_mem.mp hc.2)
  refine ite_ok_of ?_ ?_
  · intro hc
    simp only [Bool.and_eq_true, Bool.not_eq_true'] at hc
    rw [ym (hr (List.contains_iff_mem.mp hc.1)).1] at hc
    cases hc.2
  split
  · rename_i p hp
    exfalso
    have := List.find?_some hp
    rw [List.contains_iff_mem.mpr (hreg p (List.mem_of_find?_eq_some hp))] at this
    cases this
  refine ite_ok_of ?_ ?_
  · intro hc
    simp only [Bool.and_eq_true, Bool.not_eq_true'] at hc
    rw [ym (hsp (List.contains_iff_mem.mp hc.1)).1] at hc
    cases hc.2
  split
  · rename_i p hp
    exfalso
    split at hp
    · rename_i hc
      have := List.find?_some hp
      rw [List.contains_iff_mem.mpr ((hsp (List.contains_iff_mem.mp hc)).2 p (List.mem_of_find?_eq_some hp))] at this
      cases this
    · cases hp
  refine ite_ok_of (by simpa using hrf) ?_
  split
  · rename_i p hp
    exfalso
    split at hp
    · rename_i hc
      have hx := List.mem_of_find?_eq_some hp
      have hpp := List.contains_iff_mem.mp (List.find?_some hp)
      exact hrep (List.contains_iff_mem.mp hc) p (by simp only [List.mem_cons, List.not_mem_nil, or_false] at hx; rcases hx with h | h | h <;> simp [h]) hpp
    · cases hp
  split
  · rename_i p hp
    exfalso
    split at hp
    · rename_i hc
      have hx := List.mem_of_find?_eq_some hp
      have hpp := List.contains_iff_mem.mp (List.find?_some hp)
      exact hrep (List.contains_iff_mem.mp hc) p (by simp only [List.mem_cons, List.not_mem_nil, or_false] at hx; rcases hx with h | h | h <;> simp [h]) hpp
    · cases hp
  refine ite_ok_of ?_ ?_
  · intro hc
    simp only [Bool.and_eq_true] at hc
    exact (ho (List.contains_iff_mem.mp hc.1)).1 (List.contains_iff_mem.mp hc.2)
  refine ite_ok_of ?_ ?_
  · intro hc
    simp only [Bool.and_eq_true] at hc
    exact (ho (List.contains_iff_mem.mp hc.1)).2 (List.contains_iff_mem.mp hc.2)
  refine ite_ok_of ?_ ?_
  · intro hc
    simp only [Bool.and_eq_true, Bool.not_eq_true'] at hc
    rw [ym (hn (List.contains_iff_mem.mp hc.1))] at hc
    cases hc.2
  refine ite_ok_of ?_ ?_
  · intro hc
    simp only [Bool.and_eq_true, Bool.or_eq_true] at hc
    obtain ⟨_, hcl, hna, hor⟩ := hr (List.contains_iff_mem.mp hc.1)
    rcases hc.2 with (h1 | h1) | h1
    · exact hcl (List.contains_iff_mem.mp h1)
    · exact hna (List.contains_iff_mem.mp h1)
    · exact hor (List.contains_iff_mem.mp h1)
  refine ite_ok_of ?_ ?_
  · intro hc
    simp only [Bool.and_eq_true, Bool.not_eq_true'] at hc
    rw [ym (hri (List.contains_iff_mem.mp hc.1))] at hc
    cases hc.2
  refine ite_ok_of ?_ rfl
  · intro hc
    simp only [Bool.and_eq_true, Bool.not_eq_true'] at hc
    rw [ym (hso (List.contains_iff_mem.mp hc.1))] at hc
    cases hc.2

theorem today_ok {ps : List String} {r : Route} (h : today ps = .ok r) :
    todayGate ps = .ok () ∧ r = todayHead ps := by
  unfold today at h
  cases hg : todayGate ps with
  | error e => rw [hg] at h; cases h
  | ok u => rw [hg] at h; cases h; exact ⟨rfl, rfl⟩

theorem today_error {ps : List String} {e : String} : today ps = .error e ↔ todayGate ps = .error e := by
  unfold today
  cases todayGate ps <;> simp [Except.map]

theorem today_sound (ps : List String) (r : Route) (h : today ps = .ok r) : TodayList ps ∧ r = todayHead ps :=
  ⟨todayGate_sound ps (today_ok h).1, (today_ok h).2⟩

theorem today_complete (ps : List String) (h : TodayList ps) : today ps = .ok (todayHead ps) := by
  unfold today
  rw [todayGate_complete ps h]
  rfl

/-- The eight heads of `todayHead`, each with the memberships that select it. -/
theorem todayHead_cases (l : List String) :
    (todayHead l = .risk ∧ "risk@0" ∈ l) ∨
    (todayHead l = .alternatives ∧ "risk@0" ∉ l ∧ "alternatives@0" ∈ l) ∨
    (todayHead l = .speechActs ∧ "risk@0" ∉ l ∧ "alternatives@0" ∉ l ∧ "speech-acts@0" ∈ l) ∨
    (todayHead l = .reports ∧ "risk@0" ∉ l ∧ "alternatives@0" ∉ l ∧ "speech-acts@0" ∉ l ∧ "reports@0" ∈ l) ∨
    (todayHead l = .rights ∧ "risk@0" ∉ l ∧ "alternatives@0" ∉ l ∧ "speech-acts@0" ∉ l ∧ "reports@0" ∉ l ∧
      "rights@0" ∈ l) ∨
    (todayHead l = .soft ∧ "risk@0" ∉ l ∧ "alternatives@0" ∉ l ∧ "speech-acts@0" ∉ l ∧ "reports@0" ∉ l ∧
      "rights@0" ∉ l ∧ "soft-norms@0" ∈ l) ∨
    (todayHead l = .norms ∧ "risk@0" ∉ l ∧ "alternatives@0" ∉ l ∧ "speech-acts@0" ∉ l ∧ "reports@0" ∉ l ∧
      "rights@0" ∉ l ∧ "soft-norms@0" ∉ l ∧ "norms@0" ∈ l) ∨
    (todayHead l = .frozen ∧ "risk@0" ∉ l ∧ "alternatives@0" ∉ l ∧ "speech-acts@0" ∉ l ∧ "reports@0" ∉ l ∧
      "rights@0" ∉ l ∧ "soft-norms@0" ∉ l ∧ "norms@0" ∉ l) := by
  simp only [todayHead, contains_eq, decide_eq_true_eq]
  by_cases h1 : "risk@0" ∈ l
  · simp [h1]
  by_cases h2 : "alternatives@0" ∈ l
  · simp [h1, h2]
  by_cases h3 : "speech-acts@0" ∈ l
  · simp [h1, h2, h3]
  by_cases h4 : "reports@0" ∈ l
  · simp [h1, h2, h3, h4]
  by_cases h5 : "rights@0" ∈ l
  · simp [h1, h2, h3, h4, h5]
  by_cases h6 : "soft-norms@0" ∈ l
  · simp [h1, h2, h3, h4, h5, h6]
  by_cases h7 : "norms@0" ∈ l
  · simp [h1, h2, h3, h4, h5, h6, h7]
  · simp [h1, h2, h3, h4, h5, h6, h7]

theorem todayHead_not_wrapper (l : List String) :
    todayHead l ≠ .readings ∧ todayHead l ≠ .clauses ∧ todayHead l ≠ .discourse := by
  rcases todayHead_cases l with ⟨h, _⟩ | ⟨h, _⟩ | ⟨h, _⟩ | ⟨h, _⟩ | ⟨h, _⟩ | ⟨h, _⟩ | ⟨h, _⟩ | ⟨h, _⟩ <;>
    rw [h] <;> exact ⟨by decide, by decide, by decide⟩

theorem known_registered (p : String) (h : VE.Route.Gate.known p = true) : registered.contains p = true := by
  have hm := List.contains_iff_mem.mp h
  simp only [VE.Route.Gate.registry, VE.Route.Gate.base, List.map_cons, List.map_nil, List.mem_cons,
    List.not_mem_nil, or_false] at hm
  rcases hm with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> rfl

/-- On the frozen gate's registry, today's gate is the frozen classifier with the family forgotten. -/
theorem todayGate_classify (ps : List String) (h : ∀ p ∈ ps, VE.Route.Gate.known p = true) :
    todayGate ps = (VE.Route.Gate.classify ps).map (fun _ => ()) := by
  have nk : ∀ x, VE.Route.Gate.known x = false → ps.contains x = false := fun x hx => by
    cases hc : ps.contains x
    · rfl
    · rw [h x (List.contains_iff_mem.mp hc)] at hx; cases hx
  have hA := nk "alternatives@0" rfl
  have hR := nk "risk@0" rfl
  have hS := nk "speech-acts@0" rfl
  have hP := nk "reports@0" rfl
  have hI := nk "rights@0" rfl
  have hF := nk "soft-norms@0" rfl
  have f1 : ps.find? (fun p => !registered.contains p) = none :=
    List.find?_eq_none.mpr (fun p hp => by rw [known_registered p (h p hp)]; decide)
  have f2 : ps.find? (fun p => !VE.Route.Gate.known p) = none :=
    List.find?_eq_none.mpr (fun p hp => by simp [h p hp])
  unfold todayGate VE.Route.Gate.classify
  rw [f1, f2]
  simp only [hA, hR, hS, hP, hI, hF, Bool.false_and, Bool.and_false, Bool.false_eq_true, if_false]
  have eb : VE.Route.Gate.base = "relational-fol@0" := rfl
  have e1 : VE.Route.Gate.unsupported "profiles must be sorted and unique" =
      unsupported "profiles must be sorted and unique" := rfl
  have e2 : VE.Route.Gate.unsupported s!"Missing profile {VE.Route.Gate.base}" =
      unsupported "Missing profile relational-fol@0" := rfl
  have e3 : VE.Route.Gate.unsupported "Unsupported profile combination closure@0 x order@0" =
      unsupported "Unsupported profile combination closure@0 x order@0" := rfl
  have e4 : VE.Route.Gate.unsupported "Unsupported profile combination nary@0 x order@0" =
      unsupported "Unsupported profile combination nary@0 x order@0" := rfl
  have e5 : VE.Route.Gate.unsupported "Unsupported profile nary@0 without closure@0" =
      unsupported "Unsupported profile nary@0 without closure@0" := rfl
  rw [e1, e2, e3, e4, e5, eb]
  by_cases hs : ps.Pairwise (· < ·)
  · simp only [hs, decide_true, Bool.not_true, Bool.false_eq_true, if_false]
    by_cases hb : ps.contains "relational-fol@0" = true
    · simp only [hb, Bool.not_true, Bool.false_eq_true, if_false]
      cases ho : ps.contains "order@0" <;> cases hc : ps.contains "closure@0" <;>
        cases hn : ps.contains "nary@0" <;> rfl
    · simp only [Bool.not_eq_true] at hb
      simp only [hb, Bool.not_false, if_true]
      rfl
  · simp only [hs, decide_false, Bool.not_false, if_true]
    rfl

/-- On the frozen gate's own registry, today's gate is the frozen classifier: same acceptance, same text. -/
theorem today_classify (ps : List String) (h : ∀ p ∈ ps, VE.Route.Gate.known p = true) :
    (todayGate ps = .ok () ↔ ∃ f, VE.Route.Gate.classify ps = .ok f) ∧
    (∀ e, todayGate ps = .error e ↔ VE.Route.Gate.classify ps = .error e) := by
  rw [todayGate_classify ps h]
  cases VE.Route.Gate.classify ps <;> simp [Except.map]

/-! ## What each of today's heads may rely on -/

/-- What each of today's heads may rely on; these are the requirements of the heads' own Lean gates. -/
theorem today_frozen (ps : List String) (h : today ps = .ok .frozen) :
    ∀ p ∈ ["norms@0", "soft-norms@0", "rights@0", "reports@0", "speech-acts@0", "alternatives@0", "risk@0"],
      p ∉ ps := by
  have he := (today_ok h).2
  intro p hp
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hp
  rcases todayHead_cases ps with ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, h⟩ <;>
    rw [e] at he <;> try cases he
  obtain ⟨a1, a2, a3, a4, a5, a6, a7⟩ := h
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> assumption

theorem today_norms (ps : List String) (h : today ps = .ok .norms) :
    "norms@0" ∈ ps ∧ ∀ p ∈ ["soft-norms@0", "rights@0", "speech-acts@0", "alternatives@0", "risk@0"], p ∉ ps := by
  have he := (today_ok h).2
  rcases todayHead_cases ps with ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, h⟩ | ⟨e, _⟩ <;>
    rw [e] at he <;> try cases he
  obtain ⟨a1, a2, a3, a4, a5, a6, a7⟩ := h
  refine ⟨a7, fun p hp => ?_⟩
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl <;> assumption

theorem today_soft (ps : List String) (h : today ps = .ok .soft) :
    "soft-norms@0" ∈ ps ∧ "norms@0" ∈ ps ∧ "rights@0" ∉ ps := by
  have he := (today_ok h).2
  have hl := todayGate_sound ps (today_ok h).1
  rcases todayHead_cases ps with ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, h⟩ | ⟨e, _⟩ | ⟨e, _⟩ <;>
    rw [e] at he <;> try cases he
  obtain ⟨_, _, _, _, a5, a6⟩ := h
  exact ⟨a6, hl.2.2.2.2.2.2.2.2.2.2 a6, a5⟩

theorem today_rights (ps : List String) (h : today ps = .ok .rights) :
    "rights@0" ∈ ps ∧ "soft-norms@0" ∈ ps ∧ "norms@0" ∈ ps := by
  have he := (today_ok h).2
  have hl := todayGate_sound ps (today_ok h).1
  rcases todayHead_cases ps with ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, h⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ <;>
    rw [e] at he <;> try cases he
  obtain ⟨_, _, _, _, a5⟩ := h
  have hs := hl.2.2.2.2.2.2.2.2.2.1 a5
  exact ⟨a5, hs, hl.2.2.2.2.2.2.2.2.2.2 hs⟩

theorem today_alternatives (ps : List String) (h : today ps = .ok .alternatives) :
    "alternatives@0" ∈ ps ∧ "norms@0" ∈ ps ∧ "soft-norms@0" ∉ ps ∧ "risk@0" ∉ ps := by
  have he := (today_ok h).2
  have hl := todayGate_sound ps (today_ok h).1
  rcases todayHead_cases ps with ⟨e, _⟩ | ⟨e, h⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ <;>
    rw [e] at he <;> try cases he
  obtain ⟨a1, a2⟩ := h
  exact ⟨a2, (hl.2.2.2.1 a2).1, (hl.2.2.2.1 a2).2, a1⟩

theorem today_risk (ps : List String) (h : today ps = .ok .risk) :
    "risk@0" ∈ ps ∧ "alternatives@0" ∈ ps ∧ "norms@0" ∈ ps ∧ "soft-norms@0" ∉ ps := by
  have he := (today_ok h).2
  have hl := todayGate_sound ps (today_ok h).1
  rcases todayHead_cases ps with ⟨e, h⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ <;>
    rw [e] at he <;> try cases he
  have ha := (hl.2.2.2.2.1 h).1
  exact ⟨h, ha, (hl.2.2.2.1 ha).1, (hl.2.2.2.1 ha).2⟩

theorem forIn_yield_ok (l : List String) {f : String → PUnit → Except String (ForInStep PUnit)}
    (hf : ∀ p ∈ l, f p PUnit.unit = .ok (.yield PUnit.unit)) : forIn l PUnit.unit f = .ok PUnit.unit := by
  induction l with
  | nil => rfl
  | cons a as ih =>
    rw [List.forIn_cons, hf a (List.mem_cons_self ..)]
    exact ih (fun p hp => hf p (List.mem_cons_of_mem _ hp))

theorem today_speech (ps : List String) (h : today ps = .ok .speechActs) :
    VE.SpeechActs.Wire.profileGate ps = .ok () := by
  have he := (today_ok h).2
  have hl := todayGate_sound ps (today_ok h).1
  rcases todayHead_cases ps with ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, h⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ <;>
    rw [e] at he <;> try cases he
  obtain ⟨_, _, hsa⟩ := h
  obtain ⟨hn, hall⟩ := hl.2.2.2.2.2.1 hsa
  unfold VE.SpeechActs.Wire.profileGate
  simp only [hl.1, decide_true, VE.SpeechActs.Wire.speechProfile, List.contains_iff_mem.mpr hsa,
    List.contains_iff_mem.mpr hn, if_true, pure_bind]
  rw [forIn_yield_ok ps ?_]
  · rfl
  · intro p hp
    have ha : VE.SpeechActs.Wire.allowlist.contains p = true := by
      have := hall p hp
      simp only [speechAllow, List.mem_cons, List.not_mem_nil, or_false] at this
      rcases this with rfl | rfl | rfl <;> rfl
    simp only [ha, if_true]
    rfl

theorem today_reports (ps : List String) (h : today ps = .ok .reports) :
    "reports@0" ∈ ps ∧ ∀ p ∈ ["norms@0", "definitions@0", "data@0", "closure@0", "nary@0", "order@0"], p ∉ ps := by
  have he := (today_ok h).2
  have hl := todayGate_sound ps (today_ok h).1
  rcases todayHead_cases ps with ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, h⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ <;>
    rw [e] at he <;> try cases he
  obtain ⟨_, _, _, hr⟩ := h
  exact ⟨hr, hl.2.2.2.2.2.2.1 hr⟩

/-! ## The stack -/

def base (ps : List String) : List String := ps.filter (fun p => !wrapperProfiles.contains p)

def sitsOn (w : String) (r : Route) : Bool :=
  if w == "ve.discourse@1" then r == .frozen || r == .norms || r == .soft || r == .rights
  else if w == "right-clauses@0" then r == .rights
  else if w == "readings@1" then r == .norms || r == .soft || r == .rights
  else false

def wrapperHead (w : String) : Route :=
  if w == "ve.discourse@1" then .discourse else if w == "right-clauses@0" then .clauses else .readings

/-- The profile that names a route outside the chain. -/
def outside : Route → Option String
  | .reports => some "reports@0" | .speechActs => some "speech-acts@0"
  | .alternatives => some "alternatives@0" | .risk => some "risk@0" | _ => none

def refusal (w : String) (r : Route) : String :=
  match outside r with
  | some b => unsupported s!"{w} with {b}"
  | none => unsupported (if w == "right-clauses@0" then s!"{w} requires rights@0" else s!"{w} requires norms@0")

def dispatch (ps : List String) : Except String Route :=
  if !decide (ps.Pairwise (· < ·)) then .error (unsupported "profiles must be sorted and unique")
  else match today (base ps) with
  | .error e => .error e
  | .ok r =>
    let ws := wrapperProfiles.filter ps.contains
    match ws.find? (fun w => !sitsOn w r) with
    | some w => .error (refusal w r)
    | none => match ws.head? with
      | some w => .ok (wrapperHead w)
      | none => .ok r

def ChainList (ps : List String) : Prop :=
  ps.Pairwise (· < ·) ∧ ∃ r, today (base ps) = .ok r ∧ (r = .norms ∨ r = .soft ∨ r = .rights) ∧
    ∀ w ∈ wrapperProfiles, w ∈ ps → sitsOn w r = true
def stackHead (ps : List String) : Route :=
  match (wrapperProfiles.filter ps.contains).head? with
  | some w => wrapperHead w
  | none => todayHead (base ps)

theorem mem_base {ps : List String} {p : String} : p ∈ base ps ↔ p ∈ ps ∧ p ∉ wrapperProfiles := by
  simp only [base, List.mem_filter, Bool.not_eq_true', contains_eq, decide_eq_false_iff_not]

theorem base_mem {ps : List String} {p : String} (hp : p ∉ wrapperProfiles) : p ∈ base ps ↔ p ∈ ps := by
  rw [mem_base]
  exact ⟨fun h => h.1, fun h => ⟨h, hp⟩⟩

theorem mem_wrappers {ps : List String} {w : String} :
    w ∈ wrapperProfiles.filter ps.contains ↔ w ∈ wrapperProfiles ∧ w ∈ ps := by
  simp only [List.mem_filter, contains_eq, decide_eq_true_eq]

/-- `dispatch` succeeds exactly on a sorted list whose base has a route that every present wrapper sits on, and
then it answers the stack's head. -/
theorem dispatch_ok_iff (ps : List String) (x : Route) :
    dispatch ps = .ok x ↔ ps.Pairwise (· < ·) ∧ ∃ r, today (base ps) = .ok r ∧
      (∀ w ∈ wrapperProfiles, w ∈ ps → sitsOn w r = true) ∧ x = stackHead ps := by
  constructor
  · intro h
    unfold dispatch at h
    obtain ⟨hs, h⟩ := ite_error_ok h
    refine ⟨by simpa using hs, ?_⟩
    split at h
    · cases h
    rename_i r hr
    refine ⟨r, hr, ?_⟩
    dsimp only at h
    split at h
    · cases h
    rename_i hf
    refine ⟨fun w hw hp => ?_, ?_⟩
    · have := List.find?_eq_none.mp hf w (mem_wrappers.mpr ⟨hw, hp⟩)
      simpa using this
    · unfold stackHead
      split at h
      · cases h
        rfl
      · cases h
        exact (today_ok hr).2
  · rintro ⟨hs, r, hr, hsit, rfl⟩
    have hf : (wrapperProfiles.filter ps.contains).find? (fun w => !sitsOn w r) = none :=
      List.find?_eq_none.mpr (fun w hw => by
        have := mem_wrappers.mp hw
        simp [hsit w this.1 this.2])
    unfold dispatch stackHead
    rw [if_neg (by simpa using hs)]
    simp only [hr, hf]
    cases (wrapperProfiles.filter ps.contains).head? with
    | some w => rfl
    | none => rw [(today_ok hr).2]

theorem base_of_no_wrapper {ps : List String} (h : ∀ w ∈ wrapperProfiles, w ∉ ps) : base ps = ps :=
  List.filter_eq_self.mpr (fun p hp => by
    simp only [Bool.not_eq_true', contains_eq, decide_eq_false_iff_not]
    exact fun hw => h p hw hp)

/-- Today's lists keep today's route, and today's rejections keep today's diagnostic. -/
theorem dispatch_today (ps : List String) (h : ∀ w ∈ wrapperProfiles, w ∉ ps) : dispatch ps = today ps := by
  have hb := base_of_no_wrapper h
  have hws : wrapperProfiles.filter ps.contains = [] :=
    List.filter_eq_nil_iff.mpr (fun w hw => by simp [h w hw])
  by_cases hs : ps.Pairwise (· < ·)
  · unfold dispatch
    rw [if_neg (by simpa using hs), hb]
    cases ht : today ps with
    | error e => rfl
    | ok r => simp [hws]
  · unfold dispatch today todayGate
    rw [if_pos (by simpa using hs), if_pos (by simpa using hs)]
    rfl

theorem dispatch_chain (ps : List String) (h : ChainList ps) : dispatch ps = .ok (stackHead ps) := by
  obtain ⟨hs, r, hr, _, hsit⟩ := h
  exact (dispatch_ok_iff ps _).mpr ⟨hs, r, hr, hsit, rfl⟩

/-- A wrapper that strips its own profile hands dispatch a list it accepts. -/
theorem dispatch_descends (ps : List String) (w : String) (hw : w ∈ wrapperProfiles)
    (h : dispatch ps = .ok (wrapperHead w)) :
    dispatch (ps.filter (· != w)) = .ok (stackHead (ps.filter (· != w))) := by
  obtain ⟨hs, r, hr, hsit, _⟩ := (dispatch_ok_iff ps _).mp h
  have hb : base (ps.filter (· != w)) = base ps := by
    unfold base
    rw [List.filter_filter]
    apply List.filter_congr
    intro p _
    by_cases hp : p = w
    · subst hp
      simp [hw]
    · simp [hp]
  refine (dispatch_ok_iff _ _).mpr ⟨hs.filter _, r, hb ▸ hr, fun v hv hp => hsit v hv ?_, rfl⟩
  exact (List.mem_filter.mp hp).1

/-- Today's discourse lists: the wrapper is the head and what it sits on is today's frozen route. -/
theorem dispatch_discourse_frozen (ps : List String) (hs : ps.Pairwise (· < ·)) (hd : "ve.discourse@1" ∈ ps)
    (hn : "right-clauses@0" ∉ ps ∧ "readings@1" ∉ ps) (hb : today (base ps) = .ok .frozen) :
    dispatch ps = .ok .discourse ∧ dispatch (base ps) = .ok .frozen := by
  constructor
  · have hws : wrapperProfiles.filter ps.contains = ["ve.discourse@1"] := by
      simp [wrapperProfiles, List.filter, hd, hn.1, hn.2]
    refine (dispatch_ok_iff ps _).mpr ⟨hs, .frozen, hb, fun w hw hp => ?_, ?_⟩
    · simp only [wrapperProfiles, List.mem_cons, List.not_mem_nil, or_false] at hw
      rcases hw with rfl | rfl | rfl
      · rfl
      · exact absurd hp hn.1
      · exact absurd hp hn.2
    · unfold stackHead
      rw [hws]
      rfl
  · rw [dispatch_today (base ps) (fun w hw hp => (mem_base.mp hp).2 hw)]
    exact hb

/-- Every error is the order error, today's error on the base list, or a named refusal of a wrapper. -/
theorem dispatch_error (ps : List String) (e : String) (h : dispatch ps = .error e) :
    e = unsupported "profiles must be sorted and unique" ∨ today (base ps) = .error e ∨
    ∃ w ∈ wrapperProfiles, w ∈ ps ∧ ∃ r, today (base ps) = .ok r ∧ sitsOn w r = false ∧ e = refusal w r := by
  unfold dispatch at h
  split at h
  · cases h
    exact Or.inl rfl
  split at h
  · rename_i e' he
    cases h
    exact Or.inr (Or.inl he)
  rename_i r hr
  dsimp only at h
  split at h
  · rename_i w hf
    cases h
    have hm := mem_wrappers.mp (List.mem_of_find?_eq_some hf)
    have hsit := List.find?_some hf
    exact Or.inr (Or.inr ⟨w, hm.1, hm.2, r, hr, by simpa using hsit, rfl⟩)
  split at h <;> cases h

/-- A refusal names two profiles of the list (with), or one of the list and one it lacks (requires). -/
theorem refusal_names (ps : List String) (w : String) (r : Route) (hw : w ∈ ps) (hr : today (base ps) = .ok r)
    (hn : sitsOn w r = false) (hwp : w ∈ wrapperProfiles) :
    (∃ b ∈ ps, refusal w r = unsupported (w ++ " with " ++ b)) ∨
    (∃ b, b ∉ ps ∧ refusal w r = unsupported (w ++ " requires " ++ b)) := by
  have he := (today_ok hr).2
  have nw : ∀ {x}, x ∉ wrapperProfiles → (x ∈ base ps ↔ x ∈ ps) := base_mem
  have nr : "rights@0" ∉ wrapperProfiles := by decide
  have nn : "norms@0" ∉ wrapperProfiles := by decide
  rcases todayHead_cases (base ps) with ⟨e, h1⟩ | ⟨e, _, h1⟩ | ⟨e, _, _, h1⟩ | ⟨e, _, _, _, h1⟩ |
      ⟨e, h⟩ | ⟨e, h⟩ | ⟨e, h⟩ | ⟨e, h⟩ <;> rw [e] at he <;> subst he
  · exact Or.inl ⟨"risk@0", (nw (by decide)).mp h1, rfl⟩
  · exact Or.inl ⟨"alternatives@0", (nw (by decide)).mp h1, rfl⟩
  · exact Or.inl ⟨"speech-acts@0", (nw (by decide)).mp h1, rfl⟩
  · exact Or.inl ⟨"reports@0", (nw (by decide)).mp h1, rfl⟩
  all_goals
    simp only [wrapperProfiles, List.mem_cons, List.not_mem_nil, or_false] at hwp
    rcases hwp with rfl | rfl | rfl <;> simp only [sitsOn] at hn <;> try cases hn
  · obtain ⟨_, _, _, _, h5, _⟩ := h
    refine Or.inr ⟨"rights@0", fun hp => h5 ((nw nr).mpr hp), ?_⟩
    show unsupported (if _ then _ else _) = _
    rw [if_pos (by decide), String.append_assoc]; rfl
  · obtain ⟨_, _, _, _, h5, _⟩ := h
    refine Or.inr ⟨"rights@0", fun hp => h5 ((nw nr).mpr hp), ?_⟩
    show unsupported (if _ then _ else _) = _
    rw [if_pos (by decide), String.append_assoc]; rfl
  · obtain ⟨_, _, _, _, h5, _⟩ := h
    refine Or.inr ⟨"rights@0", fun hp => h5 ((nw nr).mpr hp), ?_⟩
    show unsupported (if _ then _ else _) = _
    rw [if_pos (by decide), String.append_assoc]; rfl
  · obtain ⟨_, _, _, _, _, _, h7⟩ := h
    refine Or.inr ⟨"norms@0", fun hp => h7 ((nw nn).mpr hp), ?_⟩
    show unsupported (if _ then _ else _) = _
    rw [if_neg (by decide), String.append_assoc]; rfl

end VE.Compose
