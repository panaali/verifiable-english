import VE.Readings.Lines
import VE.Compose.Adjoin

/-! Choices, the choice vocabulary, the superposed document and `Choice_D` (docs/spec/composition-s2.md 1.2 to
1.8, 8.3).

A **choice** names one candidate per open set. `choiceDoc D c` is S1's `build` with every fixed unit kept and the
chosen candidate of every open set. `sup D` holds every candidate of every open set: a candidate's rule is renamed
`rd-<k>-<n>` and its guard and sufficient exception conditions are conjoined with the choice atom `χ_{s,i}`, a
pattern over ⌈log₂ k⌉ bit predicates of one fresh sort; a fixed rule's `over` entry on an interface name names
every qualified copy. `Choice_D` is the labelled slot of the reading premises: the excluded bit patterns, the
quiescence of every generated predicate that some candidate owns, the couplings and the narrowings in force.
`pull D c S` reads a structure of `sup D` as one of `choiceDoc D c` through the name map. -/
namespace VE.Readings
open VE.Norms (Sat envAt size bindAll atom)
open VE.SoftNorms (SoftNode SoftDoc soften)
open VE.Rights (RightsDoc correlate limPremises limPremisesLabelled)
open VE.Compose (Content Labelled)
universe u

/-! ## Choices (1.2) -/

abbrev Choice := List (String × Nat)
def Choice.index (c : Choice) (s : String) : Option Nat := (c.find? (·.1 == s)).map (·.2)
def labelOf (a : Candidate) (axis : String) : Option String := (a.labels.find? (·.1 == axis)).map (·.2)
/-- The open set a narrowing is in force on: its set at the active version. -/
def inForce (D : Doc) (N : Narrowing) : Option ReadingSet :=
  D.sets.find? (fun R => R.id == N.set && R.version == N.version)
/-- The shape part of what today's `validate_couplings` requires (7; not its shared-value or satisfiability checks):
    at least two sets, none twice, each an open set at its active version, every candidate of which is labelled on
    the axis. -/
def couplingShape (D : Doc) (K : Coupling) : Bool :=
  decide (2 ≤ K.sets.length) && decide (K.sets.map (·.1)).Nodup &&
    K.sets.all (fun x => D.sets.any (fun R => R.id == x.1 && R.version == x.2 &&
      R.candidates.all (fun a => (labelOf a K.axis).isSome)))
/-- The shape of a narrowing in force as today's `validate_narrowings` requires it (7): it keeps at least one
    candidate and only candidates of its set. A narrowing not in force adds nothing (1.2). -/
def narrowingShape (D : Doc) (N : Narrowing) : Bool :=
  match inForce D N with
  | some R => !N.keeps.isEmpty && N.keeps.all (fun x => R.candidates.any (·.id == x))
  | none => true
/-- ⌈log₂ k⌉: the least b with k ≤ 2^b. -/
def bitsOf (k : Nat) : Nat := ((List.range (k + 1)).find? (fun b => k ≤ 2 ^ b)).getD k
def bitName (n j : Nat) : String := "ve__bit__" ++ toString n ++ "__" ++ toString j
def setSize (D : Doc) (m : Nat) : Nat := (D.sets[m]?.map (·.candidates.length)).getD 0
/-- The bit predicates of the choice vocabulary (1.3), sets in source order, bits ascending. -/
def bitDecls (D : Doc) : List (String × List String) :=
  (List.range D.sets.length).flatMap (fun m =>
    (List.range (bitsOf (setSize D m))).map (fun j => (bitName (m + 1) j, ["ve__reading"])))
/-- The frame declares neither the constant `ve__here` nor a bit predicate of the choice vocabulary (1.8, DRI
    ruling 1). `VE.Environment` lists constants and predicates as functions, so `WellFormedDoc` cannot see these
    names; the wire decoders refuse every `ve__` name (S1 1.8), and this conjunct carries that refusal to a `Doc`
    built as a Lean value. Without it `choiceEnv` would override a frame declaration in `sup D` that the choice's
    document keeps (fixtures KH and KB of 9.2). -/
def choiceFresh (D : Doc) : Bool :=
  D.frame.soft.E.constants "ve__here" == none && (bitDecls D).all (fun d => D.frame.soft.E.predicates d.1 == none)
/-- The unit an item stands for: a fixed unit's or a bar's id, or the unit an open set reads. -/
def itemUnit : Item → String
  | .fixed u _ _ => u
  | .bar u _ => u
  | .set R => R.unit
/-- Every item stands for its own unit (1.8): today's decoders refuse a repeated unit id (`duplicate or invalid
    unit id`), and S1's attachment is computed per unit id, so a repeated id would attach an assertion unit to a set
    through another unit of the same id. -/
def unitsDistinct (D : Doc) : Bool := decide (D.items.map itemUnit).Nodup
/-- 1.1 row 2 and 1.8: distinct set ids, every open set with a candidate, every candidate with content; the couplings
    and narrowings in today's shape, with distinct ids; the frame free of the choice vocabulary (`choiceFresh`);
    every item a unit of its own (`unitsDistinct`). The Lean counterpart of the shape part of the decoder checks
    of 7, and of that part only. -/
def supReady (D : Doc) : Bool :=
  decide (D.sets.map (·.id)).Nodup &&
    D.sets.all (fun R => !R.candidates.isEmpty && R.candidates.all (·.content.isSome)) &&
    decide (D.couplings.map (·.id)).Nodup && D.couplings.all (couplingShape D) &&
    decide (D.narrowings.map (·.id)).Nodup && D.narrowings.all (narrowingShape D) && choiceFresh D &&
    unitsDistinct D
def complete (D : Doc) (c : Choice) : Bool :=
  c.map (·.1) == D.sets.map (·.id) && c.all (fun x => (candidate D x.1 x.2).isSome)
/-- Consecutive sets of the coupling take candidates with one label on the axis. -/
def couplingHolds (D : Doc) (c : Choice) (K : Coupling) : Bool :=
  (K.sets.zip K.sets.tail).all (fun (x, y) =>
    match c.index x.1, c.index y.1 with
    | some i, some j => match (candidate D x.1 i).bind (labelOf · K.axis), (candidate D y.1 j).bind (labelOf · K.axis) with
      | some l, some l' => l == l'
      | _, _ => false
    | _, _ => false)
def narrowingHolds (D : Doc) (c : Choice) (N : Narrowing) : Bool :=
  match inForce D N with
  | some R => match c.index R.id with
    | some i => (R.candidates[i]?.map (fun a => N.keeps.contains a.id)).getD false
    | none => false
  | none => true
def compatible (D : Doc) (c : Choice) : Bool :=
  complete D c && D.couplings.all (couplingHolds D c) && D.narrowings.all (narrowingHolds D c)
def Compatible (D : Doc) (c : Choice) : Prop := compatible D c = true
/-- Every fixed unit and the chosen candidate of every open set, under their own names (S1's build). -/
def choiceDoc (D : Doc) (c : Choice) : RightsDoc × List VE.Formula :=
  build D (fun _ => true) (fun R => (c.index R.id).bind (R.candidates[·]?))
def maxChoices : Nat := 64

/-- Candidate i of R is kept by every narrowing in force on R: a pruning test of the search (`compatible`
    re-checks it on the complete choice). -/
def entryKept (D : Doc) (R : ReadingSet) (i : Nat) : Bool :=
  D.narrowings.all (fun N => match inForce D N with
    | some R' => R'.id != R.id || (R.candidates[i]?.map (fun a => N.keeps.contains a.id)).getD false
    | none => true)
/-- Every compatible choice extending `pre` over the sets `L`, in canonical order. -/
def allFrom (D : Doc) : List ReadingSet → Choice → List Choice
  | [], pre => if compatible D pre then [pre] else []
  | R :: rest, pre => (List.range R.candidates.length).flatMap (fun i =>
      if entryKept D R i then allFrom D rest (pre ++ [(R.id, i)]) else [])
/-- `allFrom` cut after `b` choices, without computing the choices past the cut. -/
def search (D : Doc) : List ReadingSet → Choice → Nat → List Choice
  | [], pre, b => if compatible D pre then [pre].take b else []
  | R :: rest, pre, b => (List.range R.candidates.length).foldl (fun acc i =>
      if b ≤ acc.length then acc
      else if entryKept D R i then acc ++ search D rest (pre ++ [(R.id, i)]) (b - acc.length) else acc) []
/-- The compatible choices in canonical order (sets in source order, candidates by index), cut after maxChoices + 1. -/
def choices (D : Doc) : List Choice := search D D.sets [] (maxChoices + 1)

/-! ### `choices_spec` -/

theorem take_step {α : Type} (b : Nat) (xs ys : List α) (f : Nat → List α)
    (hf : ∀ n, n ≠ 0 → f n = ys.take n) :
    (if b ≤ (xs.take b).length then xs.take b else xs.take b ++ f (b - (xs.take b).length)) =
      (xs ++ ys).take b := by
  split
  · rename_i h
    rw [List.take_append_of_le_length (by simp at h; omega)]
  · rename_i h
    have hx : xs.length < b := by simp at h; omega
    rw [List.take_of_length_le (by omega), hf _ (by omega), List.take_append]
    simp [List.take_of_length_le (Nat.le_of_lt hx)]

theorem search_eq (D : Doc) : ∀ (L : List ReadingSet) (pre : Choice) (b : Nat),
    search D L pre b = (allFrom D L pre).take b
  | [], pre, b => by
    simp only [search, allFrom]
    split <;> simp
  | R :: rest, pre, b => by
    simp only [search, allFrom]
    let g : Nat → List Choice := fun i => if entryKept D R i then allFrom D rest (pre ++ [(R.id, i)]) else []
    suffices h : ∀ (is : List Nat) (xs : List Choice),
        is.foldl (fun acc i => if b ≤ acc.length then acc
          else if entryKept D R i then acc ++ search D rest (pre ++ [(R.id, i)]) (b - acc.length) else acc)
          (xs.take b) = (xs ++ is.flatMap g).take b by
      simpa [g] using h (List.range R.candidates.length) []
    intro is
    induction is with
    | nil => intro xs; simp
    | cons i is ih =>
      intro xs
      simp only [List.foldl_cons, List.flatMap_cons]
      rw [← List.append_assoc, ← ih (xs ++ g i)]
      congr 1
      by_cases hk : entryKept D R i
      · have := take_step b xs (g i) (fun n => search D rest (pre ++ [(R.id, i)]) n)
          (fun n _ => by simp [g, hk, search_eq D rest])
        simpa [hk] using this
      · have := take_step b xs (g i) (fun _ => []) (fun n _ => by simp [g, hk])
        simp only [hk, Bool.false_eq_true, if_false, List.append_nil, ite_self] at this ⊢
        exact this

/-- The entries of a choice match the sets `L` in order, each with a valid index kept by the narrowings. -/
def Fits (D : Doc) : List ReadingSet → Choice → Prop
  | [], [] => True
  | R :: L, x :: suf => x.1 = R.id ∧ x.2 < R.candidates.length ∧ entryKept D R x.2 = true ∧ Fits D L suf
  | _, _ => False

theorem mem_allFrom (D : Doc) : ∀ (L : List ReadingSet) (pre c : Choice),
    c ∈ allFrom D L pre ↔ compatible D c = true ∧ ∃ suf, c = pre ++ suf ∧ Fits D L suf
  | [], pre, c => by
    simp only [allFrom]
    constructor
    · intro h
      split at h
      · rename_i hc
        simp at h; subst h
        exact ⟨hc, [], by simp, trivial⟩
      · cases h
    · rintro ⟨hc, suf, rfl, hf⟩
      cases suf with
      | nil => simp at hc ⊢; simp [hc]
      | cons _ _ => exact hf.elim
  | R :: rest, pre, c => by
    simp only [allFrom, List.mem_flatMap, List.mem_range]
    constructor
    · rintro ⟨i, hi, h⟩
      split at h
      · rename_i hk
        obtain ⟨hc, suf, rfl, hf⟩ := (mem_allFrom D rest _ c).mp h
        exact ⟨hc, (R.id, i) :: suf, by simp, rfl, hi, hk, hf⟩
      · cases h
    · rintro ⟨hc, suf, rfl, hf⟩
      cases suf with
      | nil => exact hf.elim
      | cons x suf =>
        obtain ⟨h1, h2, h3, h4⟩ := hf
        refine ⟨x.2, h2, ?_⟩
        rw [if_pos h3]
        apply (mem_allFrom D rest _ _).mpr
        refine ⟨hc, suf, ?_, h4⟩
        obtain ⟨a, b⟩ := x
        simp at h1; subst h1
        simp

theorem fits_of (D : Doc) : ∀ (L : List ReadingSet) (suf : Choice), suf.map (·.1) = L.map (·.id) →
    (∀ x ∈ suf, ∀ R ∈ L, R.id = x.1 → x.2 < R.candidates.length ∧ entryKept D R x.2 = true) → Fits D L suf
  | [], [], _, _ => trivial
  | [], _ :: _, h, _ => by simp at h
  | _ :: _, [], h, _ => by simp at h
  | R :: L, x :: suf, h, hx => by
    simp only [List.map_cons, List.cons.injEq] at h
    have := hx x List.mem_cons_self R List.mem_cons_self h.1.symm
    exact ⟨h.1, this.1, this.2, fits_of D L suf h.2
      (fun y hy R' hR' he => hx y (List.mem_cons_of_mem _ hy) R' (List.mem_cons_of_mem _ hR') he)⟩

theorem inj_of_nodup_map {α β : Type} {f : α → β} : ∀ {l : List α}, (l.map f).Nodup → ∀ {a b : α}, a ∈ l → b ∈ l →
    f a = f b → a = b
  | [], _, _, _, ha, _, _ => by cases ha
  | x :: l, hn, a, b, ha, hb, he => by
    rw [List.map_cons, List.nodup_cons] at hn
    rcases List.mem_cons.mp ha with h1 | ha'
    · rcases List.mem_cons.mp hb with h2 | hb'
      · rw [h1, h2]
      · subst h1; exact absurd (List.mem_map.mpr ⟨b, hb', he.symm⟩) hn.1
    · rcases List.mem_cons.mp hb with h2 | hb'
      · subst h2; exact absurd (List.mem_map.mpr ⟨a, ha', he⟩) hn.1
      · exact inj_of_nodup_map hn.2 ha' hb' he

theorem find_id_unique {D : Doc} (hn : (D.sets.map (·.id)).Nodup) {R : ReadingSet} (hR : R ∈ D.sets) :
    D.sets.find? (·.id == R.id) = some R := by
  obtain ⟨R', hR'⟩ : ∃ R', D.sets.find? (·.id == R.id) = some R' := by
    cases h : D.sets.find? (·.id == R.id) with
    | none => simp [List.find?_eq_none] at h; exact absurd rfl (h R hR)
    | some R' => exact ⟨R', rfl⟩
  have hm := List.mem_of_find?_eq_some hR'
  have he : R'.id = R.id := by simpa using List.find?_some hR'
  rw [hR']
  congr
  exact (inj_of_nodup_map hn hm hR he)

theorem index_of_mem {c : Choice} (hn : (c.map (·.1)).Nodup) {x : String × Nat} (hx : x ∈ c) :
    c.index x.1 = some x.2 := by
  induction c with
  | nil => cases hx
  | cons y c ih =>
    rw [List.map_cons, List.nodup_cons] at hn
    rcases List.mem_cons.mp hx with rfl | hx
    · simp [Choice.index]
    · have hne : y.1 ≠ x.1 := fun e => hn.1 (List.mem_map.mpr ⟨x, hx, e.symm⟩)
      have := ih hn.2 hx
      simp only [Choice.index] at this ⊢
      rw [List.find?_cons_of_neg (by simpa using hne)]
      exact this

/-- Every choice the search returns is compatible, whatever its cut. -/
theorem compatible_of_mem_search (D : Doc) (b : Nat) (c : Choice) (h : c ∈ search D D.sets [] b) :
    Compatible D c := by
  rw [search_eq] at h
  exact ((mem_allFrom D D.sets [] c).mp (List.mem_of_mem_take h)).1

theorem mem_allFrom_sets (D : Doc) (hr : supReady D = true) (c : Choice) :
    c ∈ allFrom D D.sets [] ↔ Compatible D c := by
  simp only [supReady, Bool.and_eq_true, decide_eq_true_eq] at hr
  have hn := hr.1.1.1.1.1.1.1
  rw [mem_allFrom, Compatible]
  constructor
  · exact fun h => h.1
  · intro hc
    refine ⟨hc, c, by simp, ?_⟩
    simp only [compatible, complete, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hc
    obtain ⟨⟨⟨hm, hs⟩, _⟩, hN⟩ := hc
    have hcn : (c.map (·.1)).Nodup := hm ▸ hn
    apply fits_of D D.sets c hm
    intro x hx R hR he
    have hfind := find_id_unique hn hR
    refine ⟨?_, ?_⟩
    · have := hs x hx
      simp only [candidate, ← he, hfind, Option.bind_some, Option.isSome_iff_exists] at this
      obtain ⟨a, ha⟩ := this
      exact (List.getElem?_eq_some_iff.mp ha).1
    · simp only [entryKept, List.all_eq_true]
      intro N hNm
      have hh := hN N hNm
      simp only [narrowingHolds] at hh
      split
      · rename_i R' hR'
        by_cases hid : R'.id = R.id
        · have hR'm : R' ∈ D.sets := List.mem_of_find?_eq_some hR'
          have : R' = R := inj_of_nodup_map hn hR'm hR hid
          subst this
          rw [hR'] at hh
          simp only at hh
          rw [he, index_of_mem hcn hx] at hh
          simpa using hh
        · simp [hid]
      · rfl

/-- Below its cut the search lists exactly the compatible choices. -/
theorem search_spec (D : Doc) (hr : supReady D = true) (b : Nat) (hlt : (search D D.sets [] b).length < b)
    (c : Choice) : c ∈ search D D.sets [] b ↔ Compatible D c := by
  have heq : search D D.sets [] b = allFrom D D.sets [] := by
    rw [search_eq] at hlt ⊢
    apply List.take_of_length_le
    simp only [List.length_take] at hlt
    omega
  rw [heq]
  exact mem_allFrom_sets D hr c

theorem choices_spec (D : Doc) (hr : supReady D = true) (hle : (choices D).length ≤ maxChoices) (c : Choice) :
    c ∈ choices D ↔ Compatible D c :=
  search_spec D hr (maxChoices + 1) (by simp only [choices] at hle; omega) c

/-- 1.2: a document whose search finds a choice has a compatible choice. -/
theorem exists_compatible_of_choices (D : Doc) (h : (choices D).isEmpty = false) : ∃ c, Compatible D c := by
  cases hc : choices D with
  | nil => rw [hc] at h; cases h
  | cons c _ =>
    have hm : c ∈ choices D := by rw [hc]; exact List.mem_cons_self
    exact ⟨c, compatible_of_mem_search D _ c hm⟩

/-- 1.2, 4.1 step 3: a document whose search finds no choice has none (`ReadingsUnsatisfiable`, 7). -/
theorem no_compatible_of_choices (D : Doc) (hr : supReady D = true) (h : (choices D).isEmpty = true) :
    ¬ ∃ c, Compatible D c := by
  rintro ⟨c, hc⟩
  have hnil : choices D = [] := List.isEmpty_iff.mp h
  have := (choices_spec D hr (by rw [hnil]; simp [maxChoices]) c).mpr hc
  rw [hnil] at this
  cases this

/-! ### The checked choices (DRI ruling 5 of 2026-10-03)

The superposed route runs the soft check on the document of every compatible choice, up to `maxChoiceChecks`
choices; `choice_wellFormed` takes the check's success as its hypothesis (`ChoiceWF.lean`), and the replays of the
superposed case kinds carry it (`SupReplay.checked`). -/

def maxChoiceChecks : Nat := 1024
/-- The compatible choices whose documents the superposed route checks, cut after `maxChoiceChecks + 1`. -/
def checkedChoices (D : Doc) : List Choice := search D D.sets [] (maxChoiceChecks + 1)
/-- The runtime check: at most `maxChoiceChecks` compatible choices, each of whose soft documents passes the soft
    check (`WellFormedSoft`, its size limits on generated formulas included). -/
def choicesSoftChecked (D : Doc) : Bool :=
  decide ((checkedChoices D).length ≤ maxChoiceChecks) &&
    (checkedChoices D).all (fun c => VE.SoftNorms.WellFormedSoft (choiceDoc D c).1.soft)

/-- Some checked compatible choice takes every candidate of `A` (a named reading is not vacuous). -/
def takenBy (D : Doc) (A : Choice) : Bool := (checkedChoices D).any (fun c => A.all (fun x => c.contains x))

theorem exists_taking (D : Doc) (A : Choice) (h : takenBy D A = true) :
    ∃ c, Compatible D c ∧ ∀ x ∈ A, x ∈ c := by
  simp only [takenBy, List.any_eq_true, List.all_eq_true, List.contains_iff_mem] at h
  obtain ⟨c, hc, hA⟩ := h
  exact ⟨c, compatible_of_mem_search D _ c hc, fun x hx => hA x hx⟩

theorem choicesSoftChecked_spec (D : Doc) (hr : supReady D = true) (hw : choicesSoftChecked D = true) (c : Choice)
    (hc : Compatible D c) : VE.SoftNorms.WellFormedSoft (choiceDoc D c).1.soft = true := by
  simp only [choicesSoftChecked, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true] at hw
  have hlt : (search D D.sets [] (maxChoiceChecks + 1)).length < maxChoiceChecks + 1 := by
    have := hw.1; simp only [checkedChoices] at this; omega
  exact hw.2 c ((search_spec D hr _ hlt c).mpr hc)

/-! ## The choice vocabulary and the atoms (1.3) -/

def here : VE.Term := .const "ve__here"
def conj : List VE.Formula → VE.Formula
  | [] => .top
  | [a] => a
  | a :: as => .and a (conj as)
def disj : List VE.Formula → VE.Formula
  | [] => .bottom
  | [a] => a
  | a :: as => .or a (disj as)
def lit (n j : Nat) (b : Bool) : VE.Formula :=
  if b then .unary (bitName n j) here else .not (.unary (bitName n j) here)
/-- The pattern of the n-th set (1-based) with k candidates spelling i. -/
def pattern (n k i : Nat) : VE.Formula := conj ((List.range (bitsOf k)).map (fun j => lit n j (i.testBit j)))
/-- χ_{s,i}; ⊥ when s is no open set or i is no candidate of it. (`atom` is W1's predicate atom; this is the choice's.) -/
def choiceAtom (D : Doc) (s : String) (i : Nat) : VE.Formula :=
  match D.sets.findIdx? (·.id == s) with
  | some m => if i < setSize D m then pattern (m + 1) (setSize D m) i else .bottom
  | none => .bottom
def atoms (D : Doc) (A : Choice) : List VE.Formula := A.map (fun x => choiceAtom D x.1 x.2)
def choiceEnv (D : Doc) (E : VE.Environment) : VE.Environment :=
  if D.sets.isEmpty then E else
  { sorts := E.sorts ++ ["ve__reading"],
    constants := fun x => if x == "ve__here" then some "ve__reading" else E.constants x,
    predicates := fun p => match (bitDecls D).find? (·.1 == p) with
      | some d => some d.2
      | none => E.predicates p }

/-! ## The superposed document (1.4) -/

def qualify (k : Nat) (n : String) : String := "rd-" ++ toString k ++ "-" ++ n
/-- The 1-based position of candidate i of the m-th set in the canonical order. -/
def position (D : Doc) (m i : Nat) : Nat := ((D.sets.take m).map (·.candidates.length)).sum + i + 1
/-- Candidate i of the m-th set declares the author rule name n. -/
def declaresRule (D : Doc) (m i : Nat) (n : String) : Bool :=
  (((D.sets[m]?).bind (·.candidates[i]?)).bind (·.content)).any (fun c => c.declared.contains ("rule", n))
/-- The origin of a rule name of sup D (1.5): the candidate (set 0-based, index) whose qualified copy it is; none for
    a fixed rule's name. Defined on the names of sup D and not on author names: an interface name is declared by
    every candidate of its set and has no one origin (the name map goes through qName instead). -/
def origin (D : Doc) (n : String) : Option (Nat × Nat) :=
  (List.range D.sets.length).findSome? (fun m =>
    ((List.range (setSize D m)).find? (fun i =>
      (((D.sets[m]?).bind (·.candidates[i]?)).bind (·.content)).any
        (fun c => c.declared.any (fun d => qualify (position D m i) d.2 == n)))).map (fun i => (m, i)))
/-- The qualified copies of an interface rule name, in candidate order; [n] for a fixed name. -/
def copies (D : Doc) (n : String) : List String :=
  match D.sets.findIdx? (fun R => (interfaceOf R).contains ("rule", n)) with
  | some m => (List.range (setSize D m)).map (fun i => qualify (position D m i) n)
  | none => [n]
def copyOver (D : Doc) (N : SoftNode) : SoftNode := { N with over := N.over.flatMap (copies D) }
def copyCites (D : Doc) (cs : List (String × List String)) : List (String × List String) :=
  cs.flatMap (fun kv => if kv.1.startsWith "over:" then (copies D (kv.1.drop 5)).map (fun n => ("over:" ++ n, kv.2))
                        else [kv])
/-- A fixed content in sup D: its over and cites entries on interface names name every copy (S2a: norms). -/
def copyContent (D : Doc) : Content → Content
  | .norm N => .norm (copyOver D N)
  | c => c
/-- Candidate i of the m-th set: gated and qualified (S2a: assertions and norms; the other contents are S2b's). -/
def gateContent (D : Doc) (m i : Nat) : Content → Content
  | .assertion φ => .assertion (.implies (pattern (m + 1) (setSize D m) i) φ)
  | .norm N =>
    let χ := pattern (m + 1) (setSize D m) i
    .norm { N with name := qualify (position D m i) N.name, guard := .and N.guard χ,
                   exception := N.exception.map (fun e => { e with sufficient := e.sufficient.map (fun C => .and C χ) }) }
  | c => c
def supFrame (D : Doc) : RightsDoc := { D.frame with soft := { D.frame.soft with E := choiceEnv D D.frame.soft.E } }
def sup (D : Doc) : RightsDoc × List VE.Formula :=
  (D.items.foldl (fun acc it => match it with
    | .fixed _ c cs => ((place acc.1.1 (copyContent D c) (copyCites D cs), acc.1.2 ++ asserted c), acc.2)
    | .bar _ b => (({ acc.1.1 with bars := acc.1.1.bars ++ [b] }, acc.1.2), acc.2)
    | .set R =>
      ((List.range R.candidates.length).foldl (fun acc' i =>
        match R.candidates[i]?.bind (fun a => a.content.map (fun c => (c, a.cites))) with
        | some (c, cs) => let g := gateContent D acc.2 i c
                          (place acc'.1 g cs, acc'.2 ++ asserted g)
        | none => acc') acc.1, acc.2 + 1)) ((supFrame D, []), 0)).1

/-! ## Owners and Choice_D (1.5, 1.6) -/

/-- The owner contributed by one comparable colliding pair of sup D: the origins of its two rules; none when they
    are different candidates of one set (never chosen together). -/
def pairOwner (D : Doc) (M N : SoftNode) : Option (List (Nat × Nat)) :=
  match origin D M.name, origin D N.name with
  | some o, some o' => if o.1 == o'.1 && o.2 != o'.2 then none else some (VE.SoftNorms.dedup [o, o'])
  | o, o' => some (o.toList ++ o'.toList)
/-- The owners of a generated key of sup D (1.5); [] among them means the fixed units alone generate it. -/
def owners (D : Doc) (k : GenKey) : List (List (Nat × Nat)) :=
  match k with
  | .excepted r _ => [(origin D r).toList]
  | .off r _ _ => [(origin D r).toList]
  | .outweighs a L H =>
    let X := correlate (sup D).1
    VE.SoftNorms.dedup ((VE.SoftNorms.collidingPairs X).filterMap (fun (M, N) =>
      if VE.SoftNorms.Comparable X M N && VE.SoftNorms.pairTriple X M N == (a, L, H) then pairOwner D M N
      else none))
  | _ => [[]]                                                                -- lim, cond, aimed: S2b
def fixedGenerated (D : Doc) (k : GenKey) : Bool := (owners D k).contains []
def atomAt (D : Doc) (o : Nat × Nat) : VE.Formula := choiceAtom D ((D.sets[o.1]?.map (·.id)).getD "") o.2
def quietFormula (D : Doc) (g : GenKey × String × List String) : VE.Formula :=
  bindAll g.2.2 (.implies (atom g.2.1 g.2.2) (disj ((owners D g.1).map (fun o => conj (o.map (atomAt D))))))
def label (R : ReadingSet) : String := R.id ++ "@" ++ toString R.version
def onePremises (D : Doc) : Labelled :=
  (List.range D.sets.length).filterMap (fun m => (D.sets[m]?).bind (fun R =>
    let k := R.candidates.length
    let unused := (List.range (2 ^ bitsOf k)).filter (k ≤ ·)
    if unused.isEmpty then none
    else some ("readings:" ++ label R ++ ":one", conj (unused.map (fun i => .not (pattern (m + 1) k i))))))
/-- The keys of sup D with exactly one owner, under that candidate's label; then every other key that is not
    fixed-generated, under its own label (keys in genKeys order). -/
def quietOwn (D : Doc) : Labelled :=
  (List.range D.sets.length).flatMap (fun m => (D.sets[m]?).toList.flatMap (fun R =>
    (List.range R.candidates.length).filterMap (fun i =>
      let mine := (genKeys (sup D).1).filter (fun g => owners D g.1 == [[(m, i)]])
      if mine.isEmpty then none
      else some ("readings:" ++ label R ++ ":" ++ toString i ++ ":quiet", conj (mine.map (quietFormula D))))))
/-- The source key in colon form (1.6); only the outweighs form is reachable in S2a. -/
def keyLabel : GenKey → String
  | .excepted r b => "excepted:" ++ r ++ (b.map (":" ++ ·)).getD ""
  | .off r b π => "off:" ++ r ++ (b.map (":" ++ ·)).getD "" ++ ":" ++ π
  | .outweighs a L H => "outweighs:" ++ a ++ ":" ++ L ++ ":" ++ H
  | .lim L a => "lim:" ++ L ++ ":" ++ a
  | .cond L a c => "cond:" ++ L ++ ":" ++ a ++ ":" ++ c
  | .aimed m => "aimed:" ++ m
def quietShared (D : Doc) : Labelled :=
  ((genKeys (sup D).1).filter (fun g => !fixedGenerated D g.1 &&
      ((owners D g.1).length != 1 || (owners D g.1).any (·.length != 1)))).map
    (fun g => ("readings:quiet:" ++ keyLabel g.1, quietFormula D g))
def couplingPremises (D : Doc) : Labelled :=
  D.couplings.filterMap (fun K =>
    let body := (K.sets.zip K.sets.tail).flatMap (fun (x, y) =>
      match D.sets.find? (·.id == x.1), D.sets.find? (·.id == y.1) with
      | some R, some R' => (List.range R.candidates.length).flatMap (fun i => (List.range R'.candidates.length).filterMap (fun j =>
          if (R.candidates[i]?.bind (labelOf · K.axis)) != (R'.candidates[j]?.bind (labelOf · K.axis))
          then some (.not (.and (choiceAtom D R.id i) (choiceAtom D R'.id j))) else none))
      | _, _ => [])
    if body.isEmpty then none else some ("coupling:" ++ K.id, conj body))
def narrowingPremises (D : Doc) : Labelled :=
  D.narrowings.filterMap (fun N => (inForce D N).bind (fun R =>
    let dropped := (List.range R.candidates.length).filter (fun i =>
      !((R.candidates[i]?.map (fun a => N.keeps.contains a.id)).getD true))
    if dropped.isEmpty then none
    else some ("narrowing:" ++ N.id, conj (dropped.map (fun i => .not (choiceAtom D R.id i))))))
def choiceLabelled (D : Doc) : Labelled :=
  onePremises D ++ quietOwn D ++ quietShared D ++ couplingPremises D ++ narrowingPremises D
def choicePremises (D : Doc) : List VE.Formula := (choiceLabelled D).formulas
def choiceCore (D : Doc) : List VE.Formula := (onePremises D ++ couplingPremises D ++ narrowingPremises D).formulas
def gatedRel (_ : Doc) : Labelled := []                                     -- S3
def slotLabelled (D : Doc) : Labelled := limPremisesLabelled (sup D).1 ++ choiceLabelled D ++ gatedRel D
def slotP (D : Doc) : List VE.Formula := (slotLabelled D).formulas
def slotUnder (D : Doc) (A : Choice) : List VE.Formula := slotP D ++ atoms D A

/-! ## Superposable (1.8) -/

/-- The rule named n that a content declares (S2a: a norm content's rule when it has that name). -/
def ruleNamed (c : Content) (n : String) : Option SoftNode :=
  match c with
  | .norm N => if N.name == n then some N else none
  | _ => none
/-- Two lists with the same members. -/
def sameMembers (l l' : List String) : Bool := l.all (l'.contains ·) && l'.all (l.contains ·)
/-- Every candidate of a set gives an interface rule name it carries the same `over` list, as a set. -/
def uniformOn (R : ReadingSet) (n : String) : Bool :=
  R.candidates.all (fun a => R.candidates.all (fun b =>
    match a.content.bind (ruleNamed · n), b.content.bind (ruleNamed · n) with
    | some Na, some Nb => sameMembers Na.over Nb.over
    | _, _ => true))
def uniformPrecedence (D : Doc) : Bool :=
  D.items.all (fun it => match it with
    | .fixed _ (.norm N) _ => N.over.all (fun n =>
        D.sets.all (fun R => !(interfaceOf R).contains ("rule", n) || uniformOn R n))
    | _ => true)

theorem uniformPrecedence_spec (D : Doc) : uniformPrecedence D = true ↔
    ∀ u c cs, Item.fixed u c cs ∈ D.items → ∀ N, c = .norm N → ∀ n ∈ N.over, ∀ R ∈ D.sets, ("rule", n) ∈ interfaceOf R →
      ∀ a ∈ R.candidates, ∀ b ∈ R.candidates, ∀ Na Nb, a.content.bind (ruleNamed · n) = some Na →
        b.content.bind (ruleNamed · n) = some Nb → ∀ m, m ∈ Na.over ↔ m ∈ Nb.over := by
  have hsame : ∀ l l' : List String, sameMembers l l' = true ↔ ∀ m, m ∈ l ↔ m ∈ l' := by
    intro l l'
    simp only [sameMembers, Bool.and_eq_true, List.all_eq_true, List.contains_iff_mem]
    exact ⟨fun h m => ⟨h.1 m, h.2 m⟩, fun h => ⟨fun m hm => (h m).mp hm, fun m hm => (h m).mpr hm⟩⟩
  have hon : ∀ R n, uniformOn R n = true ↔ ∀ a ∈ R.candidates, ∀ b ∈ R.candidates, ∀ Na Nb,
      a.content.bind (ruleNamed · n) = some Na → b.content.bind (ruleNamed · n) = some Nb →
      ∀ m, m ∈ Na.over ↔ m ∈ Nb.over := by
    intro R n
    simp only [uniformOn, List.all_eq_true]
    constructor
    · intro h a ha b hb Na Nb hNa hNb
      have := h a ha b hb
      rw [hNa, hNb] at this
      exact (hsame _ _).mp this
    · intro h a ha b hb
      split
      · rename_i Na Nb hNa hNb
        exact (hsame _ _).mpr (h a ha b hb Na Nb hNa hNb)
      · rfl
  simp only [uniformPrecedence, List.all_eq_true]
  constructor
  · intro h u c cs hit N hc n hn R hR hi
    subst hc
    have := h _ hit
    simp only [List.all_eq_true, Bool.or_eq_true, Bool.not_eq_true'] at this
    rcases this n hn R hR with h' | h'
    · exact absurd hi (by simpa using h')
    · exact (hon R n).mp h'
  · intro h it hit
    split
    · rename_i u N cs
      simp only [List.all_eq_true, Bool.or_eq_true, Bool.not_eq_true']
      intro n hn R hR
      by_cases hi : ("rule", n) ∈ interfaceOf R
      · exact Or.inr ((hon R n).mpr (h u _ cs hit N rfl n hn R hR hi))
      · exact Or.inl (by simpa using hi)
    · rfl
def superposable (D : Doc) : Bool := supReady D && uniformPrecedence D && sideWF D (sup D)

/-! ## The name map and the pulled structure (1.7) -/

/-- The name a declared rule name n of c's document takes in sup D: found through the set that declares n (an
    interface name is declared by every candidate of its set, so the set and not the name decides; by
    distinctAcrossSets at most one set declares n) and qualified by the candidate c takes in that set when that
    candidate declares n; itself for a fixed name. -/
def qName (D : Doc) (c : Choice) (n : String) : String :=
  match D.sets.findIdx? (fun R => (declaredBy R).contains ("rule", n)) with
  | some m => match c.index ((D.sets[m]?.map (·.id)).getD "") with
    | some i => if declaresRule D m i n then qualify (position D m i) n else n
    | none => n
  | none => n
def qualifyKey (D : Doc) (c : Choice) : GenKey → GenKey
  | .excepted r b => .excepted (qName D c r) b
  | .off r b π => .off (qName D c r) b π
  | k => k                                                                   -- outweighs; lim, cond, aimed: S2b
def nameMap (D : Doc) (c : Choice) (p : String) : String :=
  match (genKeys (choiceDoc D c).1).find? (·.2.1 == p) with
  | some g => (((genKeys (sup D).1).find? (·.1 == qualifyKey D c g.1)).map (·.2.1)).getD p
  | none => p
/-- The complete vocabulary of c's document. -/
def choiceEnvFull (D : Doc) (c : Choice) : VE.Environment :=
  envAt (soften (correlate (choiceDoc D c).1)) (size (soften (correlate (choiceDoc D c).1)))
def pull (D : Doc) (c : Choice) (S : VE.Structure.{u}) : VE.Structure.{u} :=
  { S with relation := fun p vs => (choiceEnvFull D c).predicates p ≠ none ∧ S.relation (nameMap D c p) vs }
def Encodes (D : Doc) (c : Choice) (S : VE.Structure.{u}) : Prop :=
  ∀ R ∈ D.sets, ∀ i, i < R.candidates.length → ((choiceAtom D R.id i).denote S [] ↔ (R.id, i) ∈ c)
/-- S' is S with only the choice vocabulary of D reinterpreted: its sort, its constant and its bit predicates. -/
def ChoiceExtension (D : Doc) (S S' : VE.Structure.{u}) : Prop :=
  ∃ (R : String → List S.Carrier → Prop) (dom : String → S.Carrier → Prop) (k : String → Option S.Carrier),
    S' = { S with relation := R, domain := dom, constant := k } ∧
    (∀ p, p ∉ (bitDecls D).map (·.1) → ∀ vs, R p vs ↔ S.relation p vs) ∧
    (∀ σ, σ ≠ "ve__reading" → dom σ = S.domain σ) ∧ (∀ x, x ≠ "ve__here" → k x = S.constant x)
/-- The complete vocabulary every reading shares: the author's, the regulated and defined predicates, and the
    decision predicates of the fixed units that depend on no open set. -/
def sharedEnv (D : Doc) : VE.Environment :=
  envAt (soften (correlate (free D).1)) (size (soften (correlate (free D).1)))
end VE.Readings
