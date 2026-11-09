import VE.Commands.Read

/-! The step reader (docs/spec/commands-imperatives.md section 7, CI-3; item ci-3a): the shapes of a wording
(`If <c>, <x>.`, `Then <x>.`, `<x₁>, then <x₂>.`, the merged wording), each read through `readCommand`, and the
combination of competing shapes' complete alternatives. No route calls it yet; ci-3 wires it into
`readInstruction`. The definitions are section 7's text; `Form` is section 10's (CI-6), defined here because
section 7's `Alt` names it. -/

namespace VE.Commands

open VE.SpeechActs (Scope)
open VE.SpeechActs.Wire (SpeechEnvironment)
open VE.EnglishGrammar (Env Lexicon)

inductive Shape
  | core (s : String)                      -- a merged wording
  | preposed (c x : String)                -- `If <c>, <x>.`
  | after (x : String)                     -- `Then <x>.`: a step after its named source antecedent (finding (c))
  | seq (xs : List String)                 -- `<x₁>, then <x₂>[, then …].`, 2 to 8 steps, none conditioned
  deriving DecidableEq, Repr

def capitalise (x : String) : String :=
  match x.toList with
  | c :: cs => String.mk (c.toUpper :: cs)
  | [] => x

def hasThen (s : String) : Bool := ((trimmed s).splitOn ", then ").length > 1

/-- Every split of `If <c>, <x>.` at a `, `, left to right; `Then <x>.`; the sequence; else the merged wording. -/
def shapes (s : String) : List Shape :=
  let t := trimmed s
  if !(t.endsWith ".") then [.core s] else
  let body := t.dropRight 1
  let pre : List Shape :=
    if body.startsWith "If " then
      let ws := (body.drop 3).splitOn ", "
      (List.range (ws.length - 1)).map fun i =>
        .preposed (", ".intercalate (ws.take (i + 1))) (", ".intercalate (ws.drop (i + 1)))
    else []
  let aft : List Shape := if body.startsWith "Then " then [.after (body.drop 5)] else []
  let xs := body.splitOn ", then "
  let sq : List Shape := if 2 ≤ xs.length && xs.length ≤ 8 && !body.startsWith "If " then [.seq xs] else []
  match pre ++ aft ++ sq with
  | [] => [.core s]
  | l => l

/-- Section 10's forms of a wording (CI-6), named here by section 7's `Alt.form`. -/
inductive Form
  | command | supposition | permission | conditionalClaim | remark | heading
  deriving DecidableEq, Repr

/-- One competing reading of a unit, as `many` lists it. CI-3 adds `shape`; CI-6 `form`; CI-7 `purpose`. -/
inductive Alt
  | shape (sh : Shape) (rs : List Reading)
  | form (f : Form)                          -- CI-6
  | purpose (r : Reading) (p : String)       -- CI-7b
  deriving DecidableEq, Repr

inductive StepOutcome
  | one (r : Reading) (afterPrevious : Bool)
  | steps (rs : List Reading)
  | many (alts : List Alt)
  | refused (code text : String)
  | limit
  | mixed (r : Reading) (p : String)         -- CI-7b
  deriving DecidableEq, Repr

/-- A merged outcome as a step outcome; `after` marks a `Then <x>.` step. -/
def lift (sh : Shape) (after : Bool) : Outcome → StepOutcome
  | .one r => .one r after
  | .many rs => .many (rs.map fun r => .shape sh [r])
  | .refused code text => .refused code text
  | .limit => .limit

def conditionScope : StepOutcome :=
  .refused "ConditionScope" "a condition with a sequence of steps: write one sentence per step, with the condition on each step or on the first only"

/-- The individual shape's complete outcomes. Core, preposed and after use `lift`; `seq` combines every step,
including all readings of a `many` step. The precedence and cap are specified immediately below. -/
def readingTuples : List (List Reading) → List (List Reading)
  | [] => [[]]
  | xs :: rest => xs.flatMap fun x => (readingTuples rest).map (x :: ·)

def shapeOutcome (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) : Shape → StepOutcome
  | .core s => lift (.core s) false (readCommand se sc E L b s)
  | .preposed c x =>
    if hasThen (x ++ ".") then conditionScope
    else lift (.preposed c x) false (readCommand se sc E L b (capitalise x ++ ", if " ++ c ++ "."))
  | .after x => lift (.after x) true (readCommand se sc E L b (capitalise x ++ "."))
  | .seq xs =>
    let os := xs.map fun x => readCommand se sc E L b (capitalise x ++ ".")
    let firstFault := os.findSome? fun o => match o with
      | .refused code text => some (.refused code text)
      | .one r => if r.guard == .top then none else some conditionScope
      | .many rs => if rs.any (·.guard != .top) then some conditionScope else none
      | .limit => none
    match firstFault with
    | some fault => fault
    | none =>
      if os.any (fun o => match o with | .limit => true | _ => false) then .limit
      else
        let choices := os.map fun o => match o with
          | .one r => [r]
          | .many rs => rs
          | _ => []
        let all := readingTuples choices
        if all.length > maxCandidates then .limit
        else match all with
          | [rs] => .steps rs
          | [] => .refused "InvalidInput" "no single speech-act reading"
          | alts => if alts.length ≤ VE.SpeechActs.Wire.readingsBound
              then .many (alts.map fun rs => .shape (.seq xs) rs) else .limit

/-- Each alternative is a complete interpretation of its shape: a sequence alternative has exactly one reading
for every step. `one` and `steps` contribute one alternative; `many` contributes each of its alternatives. -/
def shapeAlts (sh : Shape) (o : StepOutcome) : List Alt :=
  match o with
  | .one r _ => [.shape sh [r]]
  | .steps rs => [.shape sh rs]
  | .many alts => alts
  | _ => []

/-- Combine the outcomes of competing shapes as specified below. -/
def combineShapes (os : List (Shape × StepOutcome)) : StepOutcome :=
  let alts := os.flatMap fun (sh, o) => shapeAlts sh o
  if alts.length > VE.SpeechActs.Wire.readingsBound then .limit
  else if 2 ≤ alts.length then .many alts
  else if os.any (fun (_, o) => match o with | .limit => true | _ => false) then .limit
  else match os.findSome? (fun (_, o) => match o with
      | .one _ _ => some o
      | .steps _ => some o
      | .many _ => some o
      | _ => none) with
    | some o => o
    | none =>
      if os.any (fun (_, o) => match o with
          | .refused code _ => code == "ConditionScope"
          | _ => false) then conditionScope
      else .refused "InvalidInput" "no single speech-act reading"

/-- A single shape passes through; multiple shapes combine their complete alternatives and limit flags. -/
def readStep (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String) : StepOutcome :=
  let os := (shapes s).map fun sh => (sh, shapeOutcome se sc E L b sh)
  match os with
  | [(_, o)] => o
  | _ => combineShapes os

/-- A shape has a completed reading, including an alternative of `many`. -/
def reads (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (sh : Shape) : Bool :=
  !(shapeAlts sh (shapeOutcome se sc E L b sh)).isEmpty

/-! ## The statements (section 7) -/

variable (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String)

theorem mem_readingTuples : ∀ {cs : List (List Reading)} {rs : List Reading}, rs ∈ readingTuples cs →
    rs.length = cs.length
  | [], _, h => by simp_all [readingTuples]
  | _ :: _, _, h => by
    simp only [readingTuples, List.mem_flatMap, List.mem_map] at h
    obtain ⟨_, _, _, h, rfl⟩ := h
    simp [mem_readingTuples h]

/-- A product with one member: every step had exactly that one reading. -/
theorem readingTuples_single {α : Type} (φ : α → List Reading) : ∀ (l : List α) (rs : List Reading),
    readingTuples (l.map φ) = [rs] ↔ l.length = rs.length ∧ ∀ p ∈ l.zip rs, φ p.1 = [p.2]
  | [], rs => by cases rs <;> simp [readingTuples]
  | x :: l, rs => by
    simp only [List.map_cons, readingTuples]
    have ih := readingTuples_single φ l
    constructor
    · intro h
      match hx : φ x, hl : readingTuples (l.map φ) with
      | [y], [t] =>
        simp only [hx, hl, List.flatMap_cons, List.map_cons, List.map_nil, List.flatMap_nil, List.append_nil,
          List.cons.injEq, and_true] at h
        subst h
        obtain ⟨h1, h2⟩ := (ih t).1 hl
        refine ⟨by simp [h1], ?_⟩
        simp only [List.zip_cons_cons, List.mem_cons]
        rintro p (rfl | hp)
        · exact hx
        · exact h2 p hp
      | [], _ => simp [hx] at h
      | _ :: _ :: _, [] =>
        have : ∀ m : List Reading, m.flatMap (fun x => ([] : List (List Reading)).map (x :: ·)) = [] := fun m => by
          induction m <;> simp_all
        rw [hx, hl, this] at h
        cases h
      | _ :: _ :: _, _ :: _ => simp_all [List.flatMap_cons]
      | [_], [] => simp_all
      | [_], _ :: _ :: _ => simp_all
    · intro ⟨h1, h2⟩
      cases rs with
      | nil => simp at h1
      | cons r rs =>
        simp only [List.zip_cons_cons, List.mem_cons, forall_eq_or_imp, List.length_cons,
          Nat.add_right_cancel_iff] at h1 h2
        rw [h2.1, (ih rs).2 ⟨h1, h2.2⟩]
        simp

theorem exists_mem_zip {α β : Type} : ∀ {l : List α} {m : List β}, l.length = m.length → ∀ x ∈ l,
    ∃ y, (x, y) ∈ l.zip m
  | [], _, _, _, h => by simp at h
  | _ :: _, [], hl, _, _ => by simp at hl
  | a :: l, c :: m, hl, x, hx => by
    simp only [List.length_cons, Nat.add_right_cancel_iff, List.mem_cons] at hl hx
    rcases hx with rfl | hx
    · exact ⟨c, by simp⟩
    · obtain ⟨y, hy⟩ := exists_mem_zip hl x hx
      exact ⟨y, by simp [hy]⟩

theorem lift_many {sh : Shape} {a : Bool} {o : Outcome} {alts : List Alt} (h : lift sh a o = .many alts) :
    ∃ rs, o = .many rs ∧ alts = rs.map fun r => .shape sh [r] := by
  cases o <;> simp_all [lift]

theorem lift_one {sh : Shape} {a a' : Bool} {o : Outcome} {r : Reading} :
    lift sh a o = .one r a' ↔ o = .one r ∧ a = a' := by
  cases o <;> simp [lift]

theorem guard_top (g : VE.Formula) : (g == .top) = true ↔ g = .top := by
  cases g <;> simp <;> rfl

theorem two_le {α : Type} : ∀ (l : List α), (l = [] → False) → (∀ x, l = [x] → False) → 2 ≤ l.length
  | [], h, _ => absurd rfl h
  | [x], _, h => absurd rfl (h x)
  | _ :: _ :: _, _, _ => by simp

/-- A sequence's first fault is a refusal. -/
theorem seqFault {os : List Outcome} {f : StepOutcome} (h : os.findSome? (fun o => match o with
      | .refused code text => some (.refused code text)
      | .one r => if r.guard == .top then none else some conditionScope
      | .many rs => if rs.any (·.guard != .top) then some conditionScope else none
      | .limit => none) = some f) : ∃ c t, f = .refused c t := by
  obtain ⟨o, _, ho⟩ := List.exists_of_findSome?_eq_some h
  cases o with
  | refused c t => cases ho; exact ⟨c, t, rfl⟩
  | one r => simp only at ho; split at ho <;> cases ho; exact ⟨_, _, rfl⟩
  | many rs => simp only at ho; split at ho <;> cases ho; exact ⟨_, _, rfl⟩
  | limit => cases ho

/-- Every `many` alternative of a sequence holds one reading per step, and there are at least two. -/
theorem seq_many (xs : List String) (alts : List Alt) (h : shapeOutcome se sc E L b (.seq xs) = .many alts) :
    ∃ all : List (List Reading), alts = all.map (fun rs => .shape (.seq xs) rs) ∧ 2 ≤ all.length ∧ ∀ rs ∈ all, rs.length = xs.length := by
  simp only [shapeOutcome] at h
  split at h
  · obtain ⟨_, _, rfl⟩ := seqFault ‹_›
    simp at h
  · split at h
    · simp at h
    split at h
    · simp at h
    split at h
    · simp at h
    · simp at h
    · rename_i h1 h2
      split at h
      · exact ⟨_, (StepOutcome.many.inj h).symm, two_le _ h2 h1, fun rs hr => by simpa using mem_readingTuples hr⟩
      · simp at h

theorem shapeOutcome_many {sh : Shape} {alts : List Alt} (h : shapeOutcome se sc E L b sh = .many alts) :
    2 ≤ alts.length := by
  have hc : ∀ {sh' : Shape} {a : Bool} {s' : String}, lift sh' a (readCommand se sc E L b s') = .many alts →
      2 ≤ alts.length := fun h => by
    obtain ⟨rs, h1, rfl⟩ := lift_many h
    simpa using ((readCommand_many se sc E L b _ rs).1 h1).2.2.1
  cases sh with
  | core => exact hc h
  | preposed c x =>
    simp only [shapeOutcome] at h
    split at h
    · simp [conditionScope] at h
    · exact hc h
  | after => exact hc h
  | seq xs =>
    obtain ⟨all, rfl, h2, _⟩ := seq_many se sc E L b xs alts h
    simpa using h2

theorem readStep_one {sh : Shape} (h : shapes s = [sh]) : readStep se sc E L b s = shapeOutcome se sc E L b sh := by
  simp [readStep, h]

theorem readStep_combine (h : ∀ sh, shapes s ≠ [sh]) :
    readStep se sc E L b s = combineShapes ((shapes s).map fun sh => (sh, shapeOutcome se sc E L b sh)) := by
  unfold readStep
  match hs : shapes s, h with
  | [a], h => exact absurd rfl (h a)
  | [], _ => rfl
  | _ :: _ :: _, _ => rfl

theorem combine_alts (l : List Shape) (f : Shape → StepOutcome) :
    (l.map fun sh => (sh, f sh)).flatMap (fun (sh, o) => shapeAlts sh o) =
      (l.map fun sh => shapeAlts sh (f sh)).flatten := by
  induction l <;> simp_all

theorem after_eq (x : String) (r : Reading) (h : shapes s = [.after x]) :
    readStep se sc E L b s = .one r true ↔ readCommand se sc E L b (capitalise x ++ ".") = .one r := by
  rw [readStep_one se sc E L b s h]
  simp [shapeOutcome, lift_one]

theorem seq_eq (xs : List String) (rs : List Reading) (h : shapes s = [.seq xs]) :
    readStep se sc E L b s = .steps rs ↔ xs.length = rs.length ∧
      ∀ p ∈ xs.zip rs, readCommand se sc E L b (capitalise p.1 ++ ".") = .one p.2 ∧ p.2.guard = .top := by
  rw [readStep_one se sc E L b s h]
  simp only [shapeOutcome]
  constructor
  · intro h
    split at h
    · obtain ⟨_, _, rfl⟩ := seqFault ‹_›
      simp at h
    rename_i hff
    split at h
    · simp at h
    split at h
    · simp at h
    split at h
    · rename_i rs' hall
      cases h
      rw [List.map_map] at hall
      obtain ⟨h1, h2⟩ := (readingTuples_single _ xs rs).1 hall
      refine ⟨h1, fun p hp => ?_⟩
      have hg := List.findSome?_eq_none_iff.1 hff _ (List.mem_map_of_mem (List.of_mem_zip hp).1)
      have hc := h2 p hp
      simp only [Function.comp] at hc
      revert hg hc
      cases hf : readCommand se sc E L b (capitalise p.1 ++ ".") with
      | one r =>
        intro hg hc
        simp only [List.cons.injEq, and_true] at hg hc
        subst hc
        simpa using hg
      | many rs' =>
        have := ((readCommand_many se sc E L b _ rs').1 hf).2.2.1
        intro _ hc; subst hc; simp at this
      | _ => simp
    · simp at h
    · split at h <;> simp at h
  · intro ⟨h1, h2⟩
    have hx : ∀ x ∈ xs, ∃ r, readCommand se sc E L b (capitalise x ++ ".") = .one r ∧ r.guard = .top := by
      intro x hx
      obtain ⟨r, hr⟩ := exists_mem_zip h1 x hx
      obtain ⟨h3, h4⟩ := h2 (x, r) hr
      exact ⟨r, h3, h4⟩
    have hff : ∀ o ∈ xs.map (fun x => readCommand se sc E L b (capitalise x ++ ".")),
        ∃ r, o = .one r ∧ r.guard = .top := by
      simp only [List.mem_map]
      rintro _ ⟨x, hx', rfl⟩
      exact hx x hx'
    have hall : readingTuples ((xs.map (fun x => readCommand se sc E L b (capitalise x ++ "."))).map
        (fun o => match o with | .one r => [r] | .many rs => rs | _ => [])) = [rs] := by
      rw [List.map_map]
      refine (readingTuples_single _ xs rs).2 ⟨h1, fun p hp => ?_⟩
      simp [(h2 p hp).1]
    rw [List.findSome?_eq_none_iff.2 (fun o ho => by obtain ⟨r, rfl, hr⟩ := hff o ho; simp [hr]),
      List.any_eq_false.2 (fun o ho => by obtain ⟨r, rfl, _⟩ := hff o ho; simp), hall]
    simp [maxCandidates]

/-- At least two completed alternatives establish ambiguity, including two from one shape. -/
theorem shapes_ambiguous
    (h : 2 ≤ (((shapes s).map fun sh => shapeAlts sh (shapeOutcome se sc E L b sh)).flatten).length)
    (hc : (((shapes s).map fun sh => shapeAlts sh (shapeOutcome se sc E L b sh)).flatten).length ≤
      VE.SpeechActs.Wire.readingsBound) :
    ∃ alts, readStep se sc E L b s = .many alts ∧ 2 ≤ alts.length := by
  by_cases h1 : ∃ sh, shapes s = [sh]
  · obtain ⟨sh, hs⟩ := h1
    rw [readStep_one se sc E L b s hs]
    simp only [hs, List.map_cons, List.map_nil, List.flatten_cons, List.flatten_nil, List.append_nil] at h
    revert h
    cases shapeOutcome se sc E L b sh <;> simp [shapeAlts]
  · rw [readStep_combine se sc E L b s (fun sh hs => h1 ⟨sh, hs⟩)]
    simp only [combineShapes, combine_alts]
    exact ⟨_, by rw [if_neg (Nat.not_lt.mpr hc), if_pos h], h⟩

/-- Every reported sequence alternative contains every step. -/
theorem seq_ambiguous (xs : List String) (alts : List Alt) (hs : shapes s = [.seq xs])
    (hr : readStep se sc E L b s = .many alts) :
    ∀ a ∈ alts, ∃ rs, a = .shape (.seq xs) rs ∧ rs.length = xs.length := by
  rw [readStep_one se sc E L b s hs] at hr
  obtain ⟨all, rfl, _, hl⟩ := seq_many se sc E L b xs alts hr
  intro a ha
  obtain ⟨rs, hrs, rfl⟩ := List.mem_map.1 ha
  exact ⟨rs, rfl, hl rs hrs⟩

/-- With fewer than two completed alternatives, a stopped sibling prevents uniqueness. -/
theorem shapes_limit (hs : 2 > (((shapes s).map fun sh => shapeAlts sh (shapeOutcome se sc E L b sh)).flatten).length)
    (hl : ∃ sh ∈ shapes s, shapeOutcome se sc E L b sh = .limit) :
    readStep se sc E L b s = .limit := by
  obtain ⟨sh, hm, ho⟩ := hl
  by_cases h1 : ∃ sh, shapes s = [sh]
  · obtain ⟨sh', hs'⟩ := h1
    rw [readStep_one se sc E L b s hs']
    rw [hs', List.mem_singleton] at hm
    subst hm
    exact ho
  · rw [readStep_combine se sc E L b s (fun sh hs => h1 ⟨sh, hs⟩)]
    simp only [combineShapes, combine_alts]
    rw [if_neg (by simp only [VE.SpeechActs.Wire.readingsBound]; omega), if_neg (by omega), if_pos]
    simp only [List.any_eq_true, List.mem_map]
    exact ⟨_, ⟨sh, hm, rfl⟩, by simp [ho]⟩

/-- When no shape stopped and the cap holds, a `many` answer lists every completed alternative. -/
theorem shapes_complete (alts : List Alt)
    (hl : ∀ sh ∈ shapes s, shapeOutcome se sc E L b sh ≠ .limit)
    (hc : (((shapes s).map fun sh => shapeAlts sh (shapeOutcome se sc E L b sh)).flatten).length ≤
      VE.SpeechActs.Wire.readingsBound)
    (hr : readStep se sc E L b s = .many alts) :
    ∀ sh ∈ shapes s, ∀ a ∈ shapeAlts sh (shapeOutcome se sc E L b sh), a ∈ alts := by
  by_cases h1 : ∃ sh, shapes s = [sh]
  · obtain ⟨sh', hs'⟩ := h1
    rw [readStep_one se sc E L b s hs'] at hr
    intro sh hm a ha
    rw [hs', List.mem_singleton] at hm
    subst hm
    rw [hr] at ha
    exact ha
  · rw [readStep_combine se sc E L b s (fun sh hs => h1 ⟨sh, hs⟩)] at hr
    simp only [combineShapes, combine_alts] at hr
    intro sh hm a ha
    have haA : a ∈ ((shapes s).map fun sh => shapeAlts sh (shapeOutcome se sc E L b sh)).flatten :=
      List.mem_flatten.2 ⟨_, List.mem_map.2 ⟨sh, hm, rfl⟩, ha⟩
    rw [if_neg (Nat.not_lt.mpr hc)] at hr
    split at hr
    · cases hr
      exact haA
    rw [if_neg (by
      simp only [Bool.not_eq_true, List.any_eq_false, List.mem_map]
      rintro _ ⟨sh', hm', rfl⟩
      have := hl sh' hm'
      revert this
      cases shapeOutcome se sc E L b sh' <;> simp)] at hr
    split at hr
    · rename_i o hfo
      subst hr
      obtain ⟨_, hm1, ho1⟩ := List.exists_of_findSome?_eq_some hfo
      obtain ⟨sh2, hm2, rfl⟩ := List.mem_map.1 hm1
      have hmany : shapeOutcome se sc E L b sh2 = .many alts := by
        revert ho1
        cases shapeOutcome se sc E L b sh2 <;> simp
      have h2 := shapeOutcome_many se sc E L b hmany
      have hmem : alts ∈ (shapes s).map fun sh => shapeAlts sh (shapeOutcome se sc E L b sh) :=
        List.mem_map.2 ⟨sh2, hm2, by rw [hmany]; rfl⟩
      have hsub := (List.sublist_flatten_of_mem hmem).length_le
      omega
    · split at hr <;> simp [conditionScope] at hr

end VE.Commands
