import VE.Route.Gate
import VE.SpeechActs.Wire

/-! The dispatcher (docs/spec/composition.md 1.1 to 1.3, 4.2, 8, 9.3).

`today` is the former `ve/profiles.py` `checker_family` (`tests/profile_gate_oracle.py`), check for check and
text for text, followed by today's route choice (nine routes since `norm-defaults@0` was merged). `dispatch` is
`today` on the list without the stack's wrapper profiles, followed by the wrappers: each present wrapper must sit on
that route, and the head is the first wrapper present in stack order, or the route itself. Since AR-10 no runner
calls them: they are the specification of the legacy gate, and the runners call `gateOf profileTable` (below), which
`gate_legacy` shows is `dispatch` on the legacy profiles. -/
namespace VE.Compose

def unsupported (message : String) : String := "UnsupportedProfile: " ++ message

def registered : List String :=
  ["alternatives@0", "closure@0", "data@0", "definitions@0", "documents@1", "nary@0", "norm-defaults@0",
   "norms@0", "soft-norms@0", "order@0", "relational-fol@0", "speech-acts@0", "reports@0", "risk@0", "rights@0",
   "time@0"]
def speechAllow : List String := ["relational-fol@0", "norms@0", "speech-acts@0"]
/-- The stack's wrapper profiles, in stack order (ranks 1, 2, 3). -/
def wrapperProfiles : List String := ["ve.discourse@1", "right-clauses@0", "readings@1"]

inductive Route
  | frozen | reports | speechActs | alternatives | risk
  | norms | normDefaults | soft | rights
  | readings | clauses | discourse
  deriving DecidableEq, Repr

/-- The former ve/profiles.py checker_family as a gate: the eighteen checks of 4.2 in order, with its texts. -/
def todayGate (ps : List String) : Except String Unit :=
  if !decide (ps.Pairwise (· < ·)) then .error (unsupported "profiles must be sorted and unique")
  else if ps.contains "alternatives@0" && !ps.contains "norms@0" then
    .error (unsupported "alternatives@0 requires norms@0")
  else if ps.contains "alternatives@0" && ps.contains "soft-norms@0" then
    .error (unsupported "alternatives@0 with soft-norms@0")
  else if ps.contains "risk@0" && !ps.contains "alternatives@0" then
    .error (unsupported "risk@0 requires alternatives@0")
  else if ps.contains "risk@0" && ps.contains "norm-defaults@0" then
    .error (unsupported "risk@0 with norm-defaults@0 is not implemented")
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
  else if ps.contains "norm-defaults@0" && !ps.contains "norms@0" then
    .error (unsupported "norm-defaults@0 requires norms@0")
  else .ok ()

/-- The composed blocks with `norm-defaults@0` that no route but the block's own reads yet. The gate refuses
`risk@0` with the completion (check 5, the same text); ET-7 answers `alternatives@0` sources with it on the
alternatives route only, and et-7b admits their documents (docs/spec/events-time-causation.md 5). Until then each
reader that does not read the completion refuses such a list by name, before any decoder of its own:
* the `document` mode (`Service.Document.environmentOf`), after the environment mode's own first fault, and never
  `CheckerUnavailable`, which would hand the document to Python's path and the norm-defaults route;
* the norm-defaults route (`NormDefaults.Run.runGated`), before the norms envelope's field check;
* the alternatives decoder without the completion (`Alternatives.Wire.decodeAltSource`; `decodeAltSourceU` reads
  the completion over `placeholderJson`, without the profile), which the English reader's boundary (`ve ask`) and
  the route's `admission` call. -/
def pendingWithDefaults (ps : List String) : Option String :=
  if ps.contains "norm-defaults@0" then
    (["risk@0", "alternatives@0"].find? ps.contains).map
      fun block => unsupported s!"{block} with norm-defaults@0 is not implemented"
  else none

def todayHead (ps : List String) : Route :=
  if ps.contains "risk@0" then .risk else if ps.contains "alternatives@0" then .alternatives
  else if ps.contains "speech-acts@0" then .speechActs else if ps.contains "reports@0" then .reports
  else if ps.contains "rights@0" then .rights else if ps.contains "soft-norms@0" then .soft
  else if ps.contains "norm-defaults@0" then .normDefaults else if ps.contains "norms@0" then .norms else .frozen

def today (ps : List String) : Except String Route := (todayGate ps).map (fun _ => todayHead ps)

/-- The independent specification of a list today's gate accepts. -/
def TodayList (ps : List String) : Prop :=
  ps.Pairwise (· < ·) ∧ (∀ p ∈ ps, p ∈ registered) ∧ "relational-fol@0" ∈ ps ∧
  ("alternatives@0" ∈ ps → "norms@0" ∈ ps ∧ "soft-norms@0" ∉ ps) ∧
  ("risk@0" ∈ ps → "alternatives@0" ∈ ps ∧ "closure@0" ∉ ps ∧ "nary@0" ∉ ps ∧ "order@0" ∉ ps) ∧
  ("speech-acts@0" ∈ ps → "norms@0" ∈ ps ∧ ∀ p ∈ ps, p ∈ speechAllow) ∧
  ("reports@0" ∈ ps → ∀ p ∈ ["norms@0", "definitions@0", "data@0", "closure@0", "nary@0", "order@0"], p ∉ ps) ∧
  ("order@0" ∈ ps → "closure@0" ∉ ps ∧ "nary@0" ∉ ps) ∧ ("nary@0" ∈ ps → "closure@0" ∈ ps) ∧
  ("rights@0" ∈ ps → "soft-norms@0" ∈ ps) ∧ ("soft-norms@0" ∈ ps → "norms@0" ∈ ps) ∧
  ("norm-defaults@0" ∈ ps → "norms@0" ∈ ps ∧ "risk@0" ∉ ps)

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
  obtain ⟨hd1, h⟩ := ite_error_ok h
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
  obtain ⟨h11, h⟩ := ite_error_ok h
  have mem : ∀ {l : List String} {x : String}, ¬ (!l.contains x) = true → x ∈ l := fun h =>
    List.contains_iff_mem.mp (by simpa using h)
  have nmem : ∀ {x : String}, ¬ ps.contains x = true → x ∉ ps := fun h hx => h (List.contains_iff_mem.mpr hx)
  simp only [contains_eq, Bool.not_eq_true', decide_eq_false_iff_not, Bool.and_eq_true, Bool.or_eq_true,
    decide_eq_true_eq, not_and, not_or, Classical.not_not] at hs h1 h2 h3 hd1 h4 hrf h5 h6 h7 h8 h9 h10 h11
  refine ⟨hs, fun p hp => mem (List.find?_eq_none.mp hreg p hp), hrf, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
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
  · intro hnd; exact ⟨h11 hnd, fun hr => hd1 hr hnd⟩

theorem ite_ok_of {α : Type} {c : Prop} [Decidable c] {e : String} {r : Except String α} {x : α}
    (hc : ¬ c) (h : r = .ok x) : (if c then .error e else r) = .ok x := by
  rw [if_neg hc]; exact h

theorem todayGate_complete (ps : List String) (h : TodayList ps) : todayGate ps = .ok () := by
  obtain ⟨hs, hreg, hrf, ha, hr, hsp, hrep, ho, hn, hri, hso, hnd⟩ := h
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
  refine ite_ok_of ?_ ?_
  · intro hc
    simp only [Bool.and_eq_true] at hc
    exact (hnd (List.contains_iff_mem.mp hc.2)).2 (List.contains_iff_mem.mp hc.1)
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
  refine ite_ok_of ?_ ?_
  · intro hc
    simp only [Bool.and_eq_true, Bool.not_eq_true'] at hc
    rw [ym (hso (List.contains_iff_mem.mp hc.1))] at hc
    cases hc.2
  refine ite_ok_of ?_ rfl
  · intro hc
    simp only [Bool.and_eq_true, Bool.not_eq_true'] at hc
    rw [ym (hnd (List.contains_iff_mem.mp hc.1)).1] at hc
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

/-- The nine heads of `todayHead`, each with the memberships that select it. -/
theorem todayHead_cases (l : List String) :
    (todayHead l = .risk ∧ "risk@0" ∈ l) ∨
    (todayHead l = .alternatives ∧ "risk@0" ∉ l ∧ "alternatives@0" ∈ l) ∨
    (todayHead l = .speechActs ∧ "risk@0" ∉ l ∧ "alternatives@0" ∉ l ∧ "speech-acts@0" ∈ l) ∨
    (todayHead l = .reports ∧ "risk@0" ∉ l ∧ "alternatives@0" ∉ l ∧ "speech-acts@0" ∉ l ∧ "reports@0" ∈ l) ∨
    (todayHead l = .rights ∧ "risk@0" ∉ l ∧ "alternatives@0" ∉ l ∧ "speech-acts@0" ∉ l ∧ "reports@0" ∉ l ∧
      "rights@0" ∈ l) ∨
    (todayHead l = .soft ∧ "risk@0" ∉ l ∧ "alternatives@0" ∉ l ∧ "speech-acts@0" ∉ l ∧ "reports@0" ∉ l ∧
      "rights@0" ∉ l ∧ "soft-norms@0" ∈ l) ∨
    (todayHead l = .normDefaults ∧ "risk@0" ∉ l ∧ "alternatives@0" ∉ l ∧ "speech-acts@0" ∉ l ∧
      "reports@0" ∉ l ∧ "rights@0" ∉ l ∧ "soft-norms@0" ∉ l ∧ "norm-defaults@0" ∈ l) ∨
    (todayHead l = .norms ∧ "risk@0" ∉ l ∧ "alternatives@0" ∉ l ∧ "speech-acts@0" ∉ l ∧ "reports@0" ∉ l ∧
      "rights@0" ∉ l ∧ "soft-norms@0" ∉ l ∧ "norm-defaults@0" ∉ l ∧ "norms@0" ∈ l) ∨
    (todayHead l = .frozen ∧ "risk@0" ∉ l ∧ "alternatives@0" ∉ l ∧ "speech-acts@0" ∉ l ∧ "reports@0" ∉ l ∧
      "rights@0" ∉ l ∧ "soft-norms@0" ∉ l ∧ "norm-defaults@0" ∉ l ∧ "norms@0" ∉ l) := by
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
  by_cases hd : "norm-defaults@0" ∈ l
  · simp [h1, h2, h3, h4, h5, h6, hd]
  by_cases h7 : "norms@0" ∈ l
  · simp [h1, h2, h3, h4, h5, h6, hd, h7]
  · simp [h1, h2, h3, h4, h5, h6, hd, h7]

theorem todayHead_not_wrapper (l : List String) :
    todayHead l ≠ .readings ∧ todayHead l ≠ .clauses ∧ todayHead l ≠ .discourse := by
  rcases todayHead_cases l with ⟨h, _⟩ | ⟨h, _⟩ | ⟨h, _⟩ | ⟨h, _⟩ | ⟨h, _⟩ | ⟨h, _⟩ | ⟨h, _⟩ | ⟨h, _⟩ | ⟨h, _⟩ <;>
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
  have hD := nk "norm-defaults@0" rfl
  have f1 : ps.find? (fun p => !registered.contains p) = none :=
    List.find?_eq_none.mpr (fun p hp => by rw [known_registered p (h p hp)]; decide)
  have f2 : ps.find? (fun p => !VE.Route.Gate.known p) = none :=
    List.find?_eq_none.mpr (fun p hp => by simp [h p hp])
  unfold todayGate VE.Route.Gate.classify
  rw [f1, f2]
  simp only [hA, hR, hS, hP, hI, hF, hD, Bool.false_and, Bool.and_false, Bool.false_eq_true, if_false]
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

/-- What each of today's heads may rely on; these are the requirements of the heads' own Lean gates. -/
theorem today_frozen (ps : List String) (h : today ps = .ok .frozen) :
    ∀ p ∈ ["norms@0", "norm-defaults@0", "soft-norms@0", "rights@0", "reports@0", "speech-acts@0",
      "alternatives@0", "risk@0"], p ∉ ps := by
  have he := (today_ok h).2
  intro p hp
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hp
  rcases todayHead_cases ps with ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, h⟩ <;>
    rw [e] at he <;> try cases he
  obtain ⟨a1, a2, a3, a4, a5, a6, a7, a8⟩ := h
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> assumption

theorem today_norms (ps : List String) (h : today ps = .ok .norms) :
    "norms@0" ∈ ps ∧
      ∀ p ∈ ["norm-defaults@0", "soft-norms@0", "rights@0", "speech-acts@0", "alternatives@0", "risk@0"], p ∉ ps := by
  have he := (today_ok h).2
  rcases todayHead_cases ps with ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, h⟩ | ⟨e, _⟩ <;>
    rw [e] at he <;> try cases he
  obtain ⟨a1, a2, a3, a4, a5, a6, a7, a8⟩ := h
  refine ⟨a8, fun p hp => ?_⟩
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl <;> assumption

theorem today_normDefaults (ps : List String) (h : today ps = .ok .normDefaults) :
    "norm-defaults@0" ∈ ps ∧ "norms@0" ∈ ps ∧
      ∀ p ∈ ["soft-norms@0", "rights@0", "speech-acts@0", "alternatives@0", "risk@0"], p ∉ ps := by
  have he := (today_ok h).2
  have hl := todayGate_sound ps (today_ok h).1
  rcases todayHead_cases ps with ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, h⟩ | ⟨e, _⟩ | ⟨e, _⟩ <;>
    rw [e] at he <;> try cases he
  obtain ⟨a1, a2, a3, a4, a5, a6, a7⟩ := h
  refine ⟨a7, (hl.2.2.2.2.2.2.2.2.2.2.2 a7).1, fun p hp => ?_⟩
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl <;> assumption

theorem today_soft (ps : List String) (h : today ps = .ok .soft) :
    "soft-norms@0" ∈ ps ∧ "norms@0" ∈ ps ∧ "rights@0" ∉ ps := by
  have he := (today_ok h).2
  have hl := todayGate_sound ps (today_ok h).1
  rcases todayHead_cases ps with ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, h⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ <;>
    rw [e] at he <;> try cases he
  obtain ⟨_, _, _, _, a5, a6⟩ := h
  exact ⟨a6, hl.2.2.2.2.2.2.2.2.2.2.1 a6, a5⟩

theorem today_rights (ps : List String) (h : today ps = .ok .rights) :
    "rights@0" ∈ ps ∧ "soft-norms@0" ∈ ps ∧ "norms@0" ∈ ps := by
  have he := (today_ok h).2
  have hl := todayGate_sound ps (today_ok h).1
  rcases todayHead_cases ps with ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, h⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ <;>
    rw [e] at he <;> try cases he
  obtain ⟨_, _, _, _, a5⟩ := h
  have hs := hl.2.2.2.2.2.2.2.2.2.1 a5
  exact ⟨a5, hs, hl.2.2.2.2.2.2.2.2.2.2.1 hs⟩

theorem today_alternatives (ps : List String) (h : today ps = .ok .alternatives) :
    "alternatives@0" ∈ ps ∧ "norms@0" ∈ ps ∧ "soft-norms@0" ∉ ps ∧ "risk@0" ∉ ps := by
  have he := (today_ok h).2
  have hl := todayGate_sound ps (today_ok h).1
  rcases todayHead_cases ps with ⟨e, _⟩ | ⟨e, h⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ <;>
    rw [e] at he <;> try cases he
  obtain ⟨a1, a2⟩ := h
  exact ⟨a2, (hl.2.2.2.1 a2).1, (hl.2.2.2.1 a2).2, a1⟩

theorem today_risk (ps : List String) (h : today ps = .ok .risk) :
    "risk@0" ∈ ps ∧ "alternatives@0" ∈ ps ∧ "norms@0" ∈ ps ∧ "soft-norms@0" ∉ ps ∧ "norm-defaults@0" ∉ ps := by
  have he := (today_ok h).2
  have hl := todayGate_sound ps (today_ok h).1
  rcases todayHead_cases ps with ⟨e, h⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ <;>
    rw [e] at he <;> try cases he
  have ha := (hl.2.2.2.2.1 h).1
  exact ⟨h, ha, (hl.2.2.2.1 ha).1, (hl.2.2.2.1 ha).2, fun hd => (hl.2.2.2.2.2.2.2.2.2.2.2 hd).2 h⟩

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
  rcases todayHead_cases ps with ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, h⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ <;>
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
  rcases todayHead_cases ps with ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, h⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ | ⟨e, _⟩ <;>
    rw [e] at he <;> try cases he
  obtain ⟨_, _, _, hr⟩ := h
  exact ⟨hr, hl.2.2.2.2.2.2.1 hr⟩

/-! ## The stack -/

def base (ps : List String) : List String := ps.filter (fun p => !wrapperProfiles.contains p)

def sitsOn (w : String) (r : Route) : Bool :=
  if w == "ve.discourse@1" then r == .frozen || r == .norms || r == .normDefaults || r == .soft || r == .rights
  else if w == "right-clauses@0" then r == .rights
  else if w == "readings@1" then r == .norms || r == .normDefaults || r == .soft || r == .rights
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
  ps.Pairwise (· < ·) ∧ ∃ r, today (base ps) = .ok r ∧ (r = .norms ∨ r = .normDefaults ∨ r = .soft ∨ r = .rights) ∧
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

/-- D-unsorted: every list that is not strictly increasing gets the order error, whatever it contains. -/
theorem dispatch_unsorted (ps : List String) (h : ¬ ps.Pairwise (· < ·)) :
    dispatch ps = .error (unsupported "profiles must be sorted and unique") := by
  unfold dispatch
  rw [if_pos (by simpa using h)]

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
      ⟨e, h⟩ | ⟨e, h⟩ | ⟨e, h⟩ | ⟨e, h⟩ | ⟨e, h⟩ <;> rw [e] at he <;> subst he
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
  · obtain ⟨_, _, _, _, h5, _⟩ := h
    refine Or.inr ⟨"rights@0", fun hp => h5 ((nw nr).mpr hp), ?_⟩
    show unsupported (if _ then _ else _) = _
    rw [if_pos (by decide), String.append_assoc]; rfl
  · obtain ⟨_, _, _, _, _, _, _, h8⟩ := h
    refine Or.inr ⟨"norms@0", fun hp => h8 ((nw nn).mpr hp), ?_⟩
    show unsupported (if _ then _ else _) = _
    rw [if_neg (by decide), String.append_assoc]; rfl

/-! ## The profile-gate table (AR-10, SYNTHESIS 2.2)

`profileTable` is the only place a profile is registered, and `gateOf profileTable` is the gate every runner
calls. The rows are checks in a fixed fault order: after the order error and an unregistered profile, each row in
table order, its requirements before its refusals, each in list order. A row applies when its profile is listed,
or when it requires its own profile (a mandatory profile). A profile may have more than one row when its checks sit
apart in the fault order (`risk@0`; a wrapper refuses an outside route before it requires its own). A missing
requirement reads `Missing profile q` for a mandatory profile, the frozen classifier's `Unsupported profile p
without q` on a checker row, and `p requires q` otherwise. The route is the first head of `heads` with a listed
row; `gate_legacy` shows that on the legacy profiles this is `dispatch`, text and fault order included. -/

structure ProfileRow where
  profile  : String
  requires : List String              -- profiles that must be present
  refuses  : List (String × String)   -- a profile that must be absent, and its refusal text
  slot     : String                   -- the route head or wrapper position it sits on
  deriving Repr

/-- A row's refusal of each listed profile, with `p with q`. -/
def refusing (p : String) (qs : List String) : List (String × String) := qs.map fun q => (q, s!"{p} with {q}")

/-- What `speech-acts@0` refuses: every other base profile but its own two, in code point order. -/
def speechOthers : List String :=
  ["alternatives@0", "closure@0", "data@0", "definitions@0", "documents@1", "nary@0", "norm-defaults@0",
   "order@0", "reports@0", "rights@0", "risk@0", "soft-norms@0", "time@0"]

/-- What `acts@0` refuses (act-phrases 4.4): every route whose norm decoder it does not hook. -/
def actsRefuses : List (String × String) :=
  (["soft-norms@0", "rights@0", "alternatives@0", "speech-acts@0"].map fun q =>
    (q, s!"acts@0 with {q} is not implemented")) ++
  (["closure", "order"].map fun f => (s!"{f}@0", VE.Norms.Wire.actsFamilyRefusal f)) ++
  [("ve.discourse@1", "acts@0 with ve.discourse@1 is not implemented")]

def baseRows : List ProfileRow := [
  ⟨"alternatives@0", ["norms@0"], refusing "alternatives@0" ["soft-norms@0"], "alternatives"⟩,
  ⟨"risk@0", ["alternatives@0"], [("norm-defaults@0", "risk@0 with norm-defaults@0 is not implemented")], "risk"⟩,
  ⟨"speech-acts@0", ["norms@0"], refusing "speech-acts@0" speechOthers, "speechActs"⟩,
  ⟨"relational-fol@0", ["relational-fol@0"], [], "checker"⟩,
  ⟨"reports@0", [], [("norms@0", "reports@0 with norms@0 layers"),
    ("definitions@0", "reports@0 with definitions@0 layers"), ("data@0", "reports@0 with data@0 layers"),
    ("closure@0", "reports@0 requires the fol checker, not closure@0"),
    ("nary@0", "reports@0 requires the fol checker, not nary@0"),
    ("order@0", "reports@0 requires the fol checker, not order@0")], "reports"⟩,
  ⟨"order@0", [], [("closure@0", "Unsupported profile combination closure@0 x order@0"),
    ("nary@0", "Unsupported profile combination nary@0 x order@0")], "checker"⟩,
  ⟨"nary@0", ["closure@0"], [], "checker"⟩,
  ⟨"risk@0", [], ["closure@0", "nary@0", "order@0"].map (·, "the risk norms route admits FOL documents only"),
    "risk"⟩,
  ⟨"rights@0", ["soft-norms@0"], [], "rights"⟩,
  ⟨"soft-norms@0", ["norms@0"], [], "soft"⟩,
  ⟨"norm-defaults@0", ["norms@0"], [], "normDefaults"⟩,
  ⟨"norms@0", [], [], "norms"⟩,
  ⟨"acts@0", ["norms@0"], actsRefuses, "layer"⟩,
  ⟨"closure@0", [], [], "checker"⟩,
  ⟨"data@0", [], [], "layer"⟩,
  ⟨"definitions@0", [], [], "layer"⟩,
  ⟨"documents@1", [], [], "layer"⟩,
  ⟨"time@0", [], [], "layer"⟩]

/-- The routes outside the chain, which no wrapper sits on, as `outside` names them. -/
def outsideProfiles : List String := ["risk@0", "alternatives@0", "speech-acts@0", "reports@0"]

/-- The stack's wrappers in stack order. -/
def wrapperRows : List ProfileRow := [
  ⟨"ve.discourse@1", [], refusing "ve.discourse@1" outsideProfiles, "discourse"⟩,
  ⟨"right-clauses@0", [], refusing "right-clauses@0" outsideProfiles, "clauses"⟩,
  ⟨"right-clauses@0", ["rights@0"], [], "clauses"⟩,
  ⟨"readings@1", [], refusing "readings@1" outsideProfiles, "readings"⟩,
  ⟨"readings@1", ["norms@0"], [], "readings"⟩]

def profileTable : List ProfileRow := baseRows ++ wrapperRows

/-- The one wrapper an environment lists: the environment mode gates a list with it by the whole table, and any
other list by the base rows. -/
def environmentWrapper : String := "readings@1"

/-- The profiles an environment may list, in table order (`ve/profiles.py` `BY_NAME`). -/
def environmentProfiles : List String := (baseRows.map (·.profile)).eraseDups ++ [environmentWrapper]

/-- The route heads in precedence order: the first one with a listed row is the route. -/
def heads : List (String × Route) :=
  [("discourse", .discourse), ("clauses", .clauses), ("readings", .readings), ("risk", .risk),
   ("alternatives", .alternatives), ("speechActs", .speechActs), ("reports", .reports), ("rights", .rights),
   ("soft", .soft), ("normDefaults", .normDefaults), ("norms", .norms)]

def routeOf (t : List ProfileRow) (ps : List String) : Route :=
  match heads.find? (fun h => t.any fun r => r.slot == h.1 && ps.contains r.profile) with
  | some h => h.2
  | none => .frozen

def needText (r : ProfileRow) (q : String) : String :=
  if q == r.profile then s!"Missing profile {q}"
  else if r.slot == "checker" then s!"Unsupported profile {r.profile} without {q}"
  else s!"{r.profile} requires {q}"

/-- A row's checks in order, each a fault condition and its text. -/
def rowChecks (ps : List String) (r : ProfileRow) : List (Bool × String) :=
  let on := ps.contains r.profile || r.requires.contains r.profile
  r.requires.map (fun q => (on && !ps.contains q, needText r q)) ++
    r.refuses.map (fun x => (on && ps.contains x.1, x.2))

def gateOf (t : List ProfileRow) (ps : List String) : Except String Route :=
  if !decide (ps.Pairwise (· < ·)) then .error (unsupported "profiles must be sorted and unique")
  else match ps.find? (fun p => !t.any (·.profile == p)) with
  | some p => .error (unsupported s!"Unsupported profile {p}")
  | none => match (t.flatMap (rowChecks ps)).find? (·.1) with
    | some c => .error (unsupported c.2)
    | none => .ok (routeOf t ps)

/-- What the table admits, read row by row. -/
def TableAdmits (t : List ProfileRow) (ps : List String) : Prop :=
  ps.Pairwise (· < ·) ∧ (∀ p ∈ ps, ∃ r ∈ t, r.profile = p) ∧
    ∀ r ∈ t, (r.profile ∈ ps ∨ r.profile ∈ r.requires) → (∀ q ∈ r.requires, q ∈ ps) ∧ ∀ x ∈ r.refuses, x.1 ∉ ps

def legacyProfiles : List String := registered ++ wrapperProfiles

theorem checks_none (t : List ProfileRow) (ps : List String) :
    (t.flatMap (rowChecks ps)).find? (·.1) = none ↔
      ∀ r ∈ t, (r.profile ∈ ps ∨ r.profile ∈ r.requires) → (∀ q ∈ r.requires, q ∈ ps) ∧ ∀ x ∈ r.refuses, x.1 ∉ ps := by
  rw [List.find?_eq_none]
  simp only [List.mem_flatMap, rowChecks, List.mem_append, List.mem_map]
  constructor
  · intro h r hr hon
    have hon' : (ps.contains r.profile || r.requires.contains r.profile) = true := by simpa using hon
    refine ⟨fun q hq => ?_, fun x hx hxp => ?_⟩
    · have := h _ ⟨r, hr, Or.inl ⟨q, hq, rfl⟩⟩
      simp only [hon', Bool.true_and, Bool.not_eq_true'] at this
      simpa using this
    · have := h _ ⟨r, hr, Or.inr ⟨x, hx, rfl⟩⟩
      simp only [hon', Bool.true_and] at this
      simp [hxp] at this
  · rintro h c ⟨r, hr, (⟨q, hq, rfl⟩ | ⟨x, hx, rfl⟩)⟩ <;> intro hc <;>
      simp only [Bool.and_eq_true, Bool.or_eq_true, List.contains_iff_mem] at hc
    · exact (by simpa using hc.2 : q ∉ ps) ((h r hr hc.1).1 q hq)
    · exact (h r hr hc.1).2 x hx hc.2

theorem gateOf_iff (t ps r) : gateOf t ps = .ok r ↔ TableAdmits t ps ∧ r = routeOf t ps := by
  unfold gateOf TableAdmits
  by_cases hs : ps.Pairwise (· < ·)
  · rw [if_neg (by simpa using hs)]
    have hk : ps.find? (fun p => !t.any (·.profile == p)) = none ↔ ∀ p ∈ ps, ∃ q ∈ t, q.profile = p := by
      rw [List.find?_eq_none]; simp
    split
    · rename_i p hp
      simp only [reduceCtorEq, false_iff]
      rintro ⟨⟨_, hk', _⟩, _⟩
      rw [hk.mpr hk'] at hp; cases hp
    · rename_i hp
      split
      · rename_i c hc
        simp only [reduceCtorEq, false_iff]
        rintro ⟨⟨_, _, hall⟩, _⟩
        rw [(checks_none t ps).mpr hall] at hc; cases hc
      · rename_i hc
        simp only [Except.ok.injEq]
        exact ⟨fun e => ⟨⟨hs, hk.mp hp, (checks_none t ps).mp hc⟩, e.symm⟩, fun h => h.2.symm⟩
  · rw [if_pos (by simpa using hs)]
    simp [hs]

/-! ### `gate_legacy`: on the legacy profiles the table is `dispatch` -/

/-- The answer of the first failed check, or none. -/
def faultOf (o : Option (Bool × String)) : Except String Unit :=
  match o with | some c => .error (unsupported c.2) | none => .ok ()

theorem faultOf_ite (c : Bool) (x : Bool × String) (o : Option (Bool × String)) :
    faultOf (if c = true then some x else o) = if c = true then .error (unsupported x.2) else faultOf o := by
  cases c <;> rfl
theorem faultOf_none : faultOf none = .ok () := rfl

theorem find_cons_ite (c : Bool) (e : String) (l : List (Bool × String)) :
    ((c, e) :: l).find? (·.1) = if c then some (c, e) else l.find? (·.1) := by cases c <;> rfl

/-- `todayGate`'s match on a found profile. -/
abbrev gateMatch (o : Option String) (f : String → Except String Unit) (b : Except String Unit) :=
  todayGate.match_1 (fun _ => Except String Unit) o f (fun _ => b)

theorem gateMatch_find (c : Bool) (l : List String) (g : String → Bool) f b :
    gateMatch (if c = true then l.find? g else none) f b =
      l.foldr (fun q acc => if (c && g q) = true then f q else acc) b := by
  induction l with
  | nil => cases c <;> rfl
  | cons a l ih =>
    cases c
    · simpa using ih
    · cases h : g a
      · rw [List.foldr_cons, ← ih, List.find?_cons, h]; simp
      · rw [List.foldr_cons, List.find?_cons, h]; simp

theorem base_contains (ps : List String) (x : String) :
    (base ps).contains x = (ps.contains x && !wrapperProfiles.contains x) := by
  simp only [contains_eq, mem_base, Bool.decide_and, decide_not]

theorem ite_and3 (a b c d : Bool) (e : Except String Unit) (r : Except String Unit) :
    (if (a && b) = true then e else if (a && c) = true then e else if (a && d) = true then e else r) =
      if (a && (b || c || d)) = true then e else r := by
  cases a <;> cases b <;> cases c <;> cases d <;> rfl

theorem find_first {l : List String} {P : String → Bool} {x : String} (hl : l.Pairwise (· < ·))
    (hx : l.find? P = some x) : ∀ z ∈ l, P z = true → z = x ∨ x < z := by
  induction l with
  | nil => cases hx
  | cons a l ih =>
    intro z hz hp
    rw [List.find?_cons] at hx
    cases ha : P a <;> rw [ha] at hx
    · rcases List.mem_cons.mp hz with rfl | hz
      · rw [ha] at hp; cases hp
      · exact ih (List.pairwise_cons.mp hl).2 hx z hz hp
    · cases hx
      rcases List.mem_cons.mp hz with rfl | hz
      · exact Or.inl rfl
      · exact Or.inr ((List.pairwise_cons.mp hl).1 z hz)

/-- On two strictly increasing lists, the first element of one that the other lists is the first of the other. -/
theorem sorted_find {l m : List String} (hl : l.Pairwise (· < ·)) (hm : m.Pairwise (· < ·)) :
    l.find? m.contains = m.find? l.contains := by
  cases ha : l.find? m.contains with
  | none =>
    symm; rw [List.find?_eq_none] at ha ⊢
    intro x hx hc
    exact ha x (List.contains_iff_mem.mp hc) (List.contains_iff_mem.mpr hx)
  | some x =>
    have hxl := List.mem_of_find?_eq_some ha
    have hxm := List.contains_iff_mem.mp (List.find?_some ha)
    cases hb : m.find? l.contains with
    | none =>
      rw [List.find?_eq_none] at hb
      exact absurd (List.contains_iff_mem.mpr hxl) (hb x hxm)
    | some y =>
      have hym := List.mem_of_find?_eq_some hb
      have hyl := List.contains_iff_mem.mp (List.find?_some hb)
      rcases find_first hl ha y hyl (List.contains_iff_mem.mpr hym) with rfl | h1
      · rfl
      rcases find_first hm hb x hxm (List.contains_iff_mem.mpr hxl) with rfl | h2
      · rfl
      exact absurd h2 (String.lt_asymm h1)

theorem find_congr {l : List String} {f g : String → Bool} (h : ∀ x ∈ l, f x = g x) : l.find? f = l.find? g := by
  induction l with
  | nil => rfl
  | cons a l ih =>
    rw [List.find?_cons, List.find?_cons, h a (List.mem_cons_self ..),
      ih fun x hx => h x (List.mem_cons_of_mem _ hx)]

/-- Today's gate on the base list is the first failed check of the base rows. -/
theorem todayGate_base (ps : List String) (hs : ps.Pairwise (· < ·)) (h : ∀ p ∈ ps, p ∈ legacyProfiles) :
    todayGate (base ps) = faultOf ((baseRows.flatMap (rowChecks ps)).find? (·.1)) := by
  have hsb : (base ps).Pairwise (· < ·) := hs.filter _
  have hreg : ∀ p ∈ base ps, p ∈ registered := fun p hp => by
    have := h p (mem_base.mp hp).1
    simp only [legacyProfiles, List.mem_append] at this
    exact this.resolve_right (mem_base.mp hp).2
  have hunk : (base ps).find? (fun p => !registered.contains p) = none :=
    List.find?_eq_none.mpr fun p hp => by simpa using hreg p hp
  have hsp : (base ps).find? (fun p => !speechAllow.contains p) = speechOthers.find? ps.contains := by
    have e1 : (base ps).find? (fun p => !speechAllow.contains p) = (base ps).find? speechOthers.contains :=
      find_congr fun p hp => by
        have := hreg p hp
        simp only [registered, List.mem_cons, List.not_mem_nil, or_false] at this
        rcases this with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl |
          rfl <;> rfl
    rw [e1, sorted_find hsb (by decide)]
    exact find_congr fun p hp => by
      simp only [speechOthers, List.mem_cons, List.not_mem_nil, or_false] at hp
      rw [base_contains]
      rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;>
        simp [wrapperProfiles]
  have hj : ps.contains "acts@0" = false := by
    cases hc : ps.contains "acts@0"
    · rfl
    · have := h _ (List.contains_iff_mem.mp hc)
      simp [legacyProfiles, registered, wrapperProfiles] at this
  unfold todayGate
  rw [hunk, hsp]
  simp only [decide_eq_true hsb, Bool.not_true, Bool.false_eq_true, if_false]
  simp only [speechOthers, gateMatch_find, List.foldr_cons, List.foldr_nil]
  simp only [base_contains, wrapperProfiles, List.contains_cons, List.contains_nil, String.reduceBEq,
    Bool.or_false, Bool.not_false, Bool.and_true]
  simp only [baseRows, refusing, speechOthers, rowChecks, List.flatMap_cons, List.flatMap_nil, List.map_cons,
    List.map_nil, List.cons_append, List.nil_append, List.append_nil, find_cons_ite, List.contains_cons,
    List.contains_nil, needText, List.find?_nil, String.reduceBEq, Bool.or_false, Bool.or_true,
    Bool.true_and, toString, String.reduceAppend, if_false, if_true, Bool.false_eq_true, faultOf_ite, faultOf_none,
    actsRefuses, hj, Bool.false_and]
  simp only [ite_and3]

theorem todayHead_base (ps : List String) : todayHead (base ps) = todayHead ps := by
  simp only [todayHead, base_contains, wrapperProfiles, List.contains_cons, List.contains_nil, String.reduceBEq,
    Bool.or_false, Bool.not_false, Bool.and_true]

/-- The table's route: the first wrapper present, else today's head. -/
theorem routeOf_table (ps : List String) : routeOf profileTable ps =
    if ps.contains "ve.discourse@1" then .discourse else if ps.contains "right-clauses@0" then .clauses
    else if ps.contains "readings@1" then .readings else todayHead ps := by
  simp only [routeOf, heads, profileTable, baseRows, wrapperRows, todayHead, List.find?_cons, List.find?_nil,
    List.any_cons, List.any_nil, List.cons_append, List.nil_append, String.reduceBEq, Bool.false_and,
    Bool.true_and, Bool.or_false, Bool.false_or, Bool.or_self]
  cases ps.contains "ve.discourse@1" <;> cases ps.contains "right-clauses@0" <;> cases ps.contains "readings@1" <;>
    cases ps.contains "risk@0" <;> cases ps.contains "alternatives@0" <;> cases ps.contains "speech-acts@0" <;>
    cases ps.contains "reports@0" <;> cases ps.contains "rights@0" <;> cases ps.contains "soft-norms@0" <;>
    cases ps.contains "norm-defaults@0" <;> cases ps.contains "norms@0" <;> rfl

/-- On the legacy profiles the table runs today's gate: verdict, refusal text, fault order and route. -/
theorem gate_legacy (ps) (h : ∀ p ∈ ps, p ∈ legacyProfiles) :
    gateOf profileTable ps = dispatch ps := by
  by_cases hs : ps.Pairwise (· < ·)
  case neg => rw [dispatch_unsorted ps hs]; unfold gateOf; rw [if_pos (by simpa using hs)]
  have hk : ps.find? (fun p => !profileTable.any (·.profile == p)) = none :=
    List.find?_eq_none.mpr fun p hp => by
      have := h p hp
      simp only [legacyProfiles, registered, wrapperProfiles, List.cons_append, List.nil_append, List.mem_cons,
        List.not_mem_nil, or_false] at this
      rcases this with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl |
        rfl | rfl | rfl | rfl <;> decide
  unfold gateOf dispatch today
  rw [if_neg (by simpa using hs), if_neg (by simpa using hs), hk, todayGate_base ps hs h]
  rw [routeOf_table, todayHead_base]
  simp only [profileTable, List.flatMap_append, List.find?_append]
  cases hA : (baseRows.flatMap (rowChecks ps)).find? (·.1) with
  | some c => rfl
  | none =>
    have hrows := (checks_none baseRows ps).mp hA
    have row : ∀ r ∈ baseRows, r.profile ∈ ps → ∀ q ∈ r.requires, q ∈ ps := fun r hr hp => (hrows r hr (.inl hp)).1
    have hsoft : "soft-norms@0" ∈ ps → "norms@0" ∈ ps := fun hp =>
      row ⟨"soft-norms@0", ["norms@0"], [], "soft"⟩ (by simp [baseRows]) hp _ (by simp)
    have hnd : "norm-defaults@0" ∈ ps → "norms@0" ∈ ps := fun hp =>
      row ⟨"norm-defaults@0", ["norms@0"], [], "normDefaults"⟩ (by simp [baseRows]) hp _ (by simp)
    have hri : "rights@0" ∈ ps → "soft-norms@0" ∈ ps := fun hp =>
      row ⟨"rights@0", ["soft-norms@0"], [], "rights"⟩ (by simp [baseRows]) hp _ (by simp)
    simp only [Option.none_or, faultOf_none, Except.map]
    clear hrows row hA hk h
    simp only [wrapperRows, refusing, outsideProfiles, rowChecks, List.flatMap_cons, List.flatMap_nil, List.map_cons,
      List.map_nil, List.cons_append, List.nil_append, List.append_nil, find_cons_ite, List.contains_cons,
      List.contains_nil, needText, List.find?_nil, String.reduceBEq, Bool.or_false,
      toString, String.reduceAppend, if_false, Bool.false_eq_true, wrapperProfiles, List.filter_cons,
      List.filter_nil]
    simp only [contains_eq] at *
    rcases todayHead_cases ps with ⟨e, h1⟩ | ⟨e, h1⟩ | ⟨e, h1⟩ | ⟨e, h1⟩ | ⟨e, h1⟩ | ⟨e, h1⟩ | ⟨e, h1⟩ |
      ⟨e, h1⟩ | ⟨e, h1⟩ <;> rw [e] <;>
      by_cases hd : "ve.discourse@1" ∈ ps <;> by_cases hc : "right-clauses@0" ∈ ps <;>
      by_cases hr : "readings@1" ∈ ps <;>
      simp [hd, hc, hr, h1, hsoft, hnd, hri, sitsOn, refusal, outside, wrapperHead, toString, String.reduceAppend]

/-- The base rows' route: today's head. -/
theorem routeOf_base (ps : List String) : routeOf baseRows ps = todayHead ps := by
  simp only [routeOf, heads, baseRows, todayHead, List.find?_cons, List.find?_nil, List.any_cons, List.any_nil,
    String.reduceBEq, Bool.false_and, Bool.true_and, Bool.or_false, Bool.false_or, Bool.or_self]
  cases ps.contains "risk@0" <;> cases ps.contains "alternatives@0" <;> cases ps.contains "speech-acts@0" <;>
    cases ps.contains "reports@0" <;> cases ps.contains "rights@0" <;> cases ps.contains "soft-norms@0" <;>
    cases ps.contains "norm-defaults@0" <;> cases ps.contains "norms@0" <;> rfl

/-- The base rows alone, where a wrapper is not registered, run `today` on the registered profiles. -/
theorem baseGate_today (ps : List String) (h : ∀ p ∈ ps, p ∈ registered) : gateOf baseRows ps = today ps := by
  by_cases hs : ps.Pairwise (· < ·)
  case neg => unfold gateOf today todayGate; rw [if_pos (by simpa using hs), if_pos (by simpa using hs)]; rfl
  have hl : ∀ p ∈ ps, p ∈ legacyProfiles := fun p hp => List.mem_append_left _ (h p hp)
  have hb : base ps = ps := base_of_no_wrapper fun w hw hp => by
    have := h w hp
    simp only [wrapperProfiles, List.mem_cons, List.not_mem_nil, or_false] at hw
    rcases hw with rfl | rfl | rfl <;> simp [registered] at this
  have hk : ps.find? (fun p => !baseRows.any (·.profile == p)) = none :=
    List.find?_eq_none.mpr fun p hp => by
      have := h p hp
      simp only [registered, List.mem_cons, List.not_mem_nil, or_false] at this
      rcases this with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl |
        rfl <;> decide
  have ht := todayGate_base ps hs hl
  rw [hb] at ht
  unfold gateOf today
  rw [if_neg (by simpa using hs), hk, ht, routeOf_base]
  cases (baseRows.flatMap (rowChecks ps)).find? (·.1) <;> rfl


/-! ### `gate_acts`: `acts@0` changes no route (act-phrases 4.4) -/

theorem gate_acts (ps : List String) (h : "acts@0" ∈ ps) (r : Route)
    (hg : gateOf profileTable ps = .ok r) :
    gateOf profileTable (ps.erase "acts@0") = .ok r ∧ (r = .norms ∨ r = .normDefaults ∨ r = .readings) := by
  obtain ⟨⟨hs, hk, hrows⟩, rfl⟩ := (gateOf_iff _ _ _).mp hg
  have hn : ps.Nodup := hs.imp fun h e => by subst e; exact String.lt_asymm h h
  have hmem : ∀ x, x ≠ "acts@0" → (x ∈ ps.erase "acts@0" ↔ x ∈ ps) := fun x hx => by
    rw [hn.mem_erase_iff]; exact ⟨And.right, fun hp => ⟨hx, hp⟩⟩
  have hreq : ∀ r ∈ profileTable, "acts@0" ∉ r.requires := by decide
  have row := fun (r : ProfileRow) (hr : r ∈ profileTable) (hp : r.profile ∈ ps) => hrows r hr (.inl hp)
  have hacts := row ⟨"acts@0", ["norms@0"], actsRefuses, "layer"⟩ (by simp [profileTable, baseRows]) h
  simp only [actsRefuses, List.map_cons, List.map_nil, List.cons_append, List.nil_append, List.mem_cons,
    List.not_mem_nil, or_false, forall_eq_or_imp, forall_eq, toString, String.reduceAppend] at hacts
  obtain ⟨hno, hso, hri, hal, hsp, hcl, hor, hdi⟩ := hacts
  have hrc : "right-clauses@0" ∉ ps := fun hp =>
    hri ((row ⟨"right-clauses@0", ["rights@0"], [], "clauses"⟩ (by simp [profileTable, wrapperRows]) hp).1 _ (by simp))
  have hrk : "risk@0" ∉ ps := fun hp =>
    hal ((row ⟨"risk@0", ["alternatives@0"], [("norm-defaults@0", "risk@0 with norm-defaults@0 is not implemented")],
      "risk"⟩ (by simp [profileTable, baseRows]) hp).1 _ (by simp))
  have hre : "reports@0" ∉ ps := fun hp =>
    (row (baseRows[4]'(by decide)) (by simp [profileTable]) hp).2 ("norms@0", "reports@0 with norms@0 layers")
      (by simp [baseRows]) hno
  have hc : ∀ x, x ≠ "acts@0" → (ps.erase "acts@0").contains x = ps.contains x := fun x hx => by
    simp only [contains_eq, hmem x hx]
  refine ⟨(gateOf_iff _ _ _).mpr ⟨⟨hs.sublist (List.erase_sublist ..),
    fun p hp => hk p (List.mem_of_mem_erase hp), fun r hr hon => ?_⟩, ?_⟩, ?_⟩
  · by_cases hpa : r.profile = "acts@0"
    · exfalso
      rw [hpa] at hon
      rcases hon with he | he
      · exact List.Nodup.not_mem_erase hn he
      · exact hreq r hr he
    · have ⟨hq, hx⟩ := hrows r hr (hon.imp (fun hp => (hmem _ hpa).mp hp) id)
      exact ⟨fun q hq' => (hmem q (fun e => hreq r hr (e ▸ hq'))).mpr (hq q hq'),
        fun x hx' hp => hx x hx' (List.mem_of_mem_erase hp)⟩
  · have e : ∀ x ∈ ["ve.discourse@1", "right-clauses@0", "readings@1", "risk@0", "alternatives@0", "speech-acts@0",
        "reports@0", "rights@0", "soft-norms@0", "norm-defaults@0", "norms@0"],
        (ps.erase "acts@0").contains x = ps.contains x := fun x hx => hc x (by rintro rfl; simp at hx)
    simp only [List.mem_cons, List.not_mem_nil, or_false, forall_eq_or_imp, forall_eq] at e
    obtain ⟨e1, e2, e3, e4, e5, e6, e7, e8, e9, e10, e11⟩ := e
    rw [routeOf_table, routeOf_table]
    simp only [todayHead, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10, e11]
  · rw [routeOf_table]
    by_cases hr : "readings@1" ∈ ps <;> by_cases hd : "norm-defaults@0" ∈ ps <;>
      simp [todayHead, hr, hd, hno, hso, hri, hal, hsp, hdi, hrc, hrk, hre]

end VE.Compose
