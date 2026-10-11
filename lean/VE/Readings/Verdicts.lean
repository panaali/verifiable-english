import VE.Readings.UnspecifiedWire

/-! Verdicts across readings in Lean, on the enumerated route (docs/spec/readings-defaults.md 1.6 to 1.8, 2.3 to 2.5,
4.4, 6.4 and 6.5; plan RD-3).

The per-choice results (`ChoiceResult`) and what each claims of its choice (`Holds`); the folds of composition-s2
4.6 with the gate of 14.8 (`foldConflict`, `foldEntailment`, `foldPremises`) and what an UNKNOWN names (`reasonOf`);
the fold theorems (`fold_all_sound`, `fold_none_sound`, `fold_some_sound`, `fold_conflict_free_sound`,
`fold_conflict_sound`, `fold_premises_model_sound`, `fold_premises_inconsistent_sound`), each over rows that are
exactly the compatible choices taking `A` (`Covers`), the conflict rows beside the query rows (`RowsHold`). The
conditions: the couplings and narrowings that exclude some complete choice taking `A`, computed locally without
enumerating the complete choices (`restrictionsFor`, `restrictionsFor_spec`), and the labels a checked answer uses,
dropped greedily while every certificate still checks (`usedLabels`, `usedLabels_sound`). The English plan
(`englishPlan`) is in `VerdictsWire.lean`, beside the kind `readings-verdicts` that computes it.

Each fold theorem follows from a row lemma that reads the fold alone (`foldEntailment_all`, ...), so the same lemmas
give the lower route's wire theorem, whose rows are the lower route's own checked answers. -/
namespace VE.Readings
open VE.Norms (Regulated Sat envAt size restrictAll DocumentExpansion)
open VE.NormDefaults (EntailsU)
universe u

/-! ## Per-choice results and the folds (1.6, 1.7) -/

inductive ChoiceResult | proved | refuted | free | conflict | model | inconsistent | unknown
  deriving DecidableEq, Repr
inductive ReadingVerdict | all | some | none | unknown
  deriving DecidableEq, Repr
def foldConflict (rs : List (Choice × ChoiceResult)) : ChoiceResult :=
  if rs.any (·.2 == .conflict) then .conflict
  else if !rs.isEmpty && rs.all (·.2 == .free) then .free else .unknown
/-- composition-s2 4.6 with its gate (14.8; review A2): `conflicts` are the conflict rows of the same choices. -/
def foldEntailment (conflicts rs : List (Choice × ChoiceResult)) : ReadingVerdict :=
  if foldConflict conflicts != .free then .unknown
  else if rs.isEmpty then .unknown
  else if rs.all (·.2 == .proved) then .all
  else if rs.all (·.2 == .refuted) then .none
  else if rs.any (·.2 == .proved) && rs.any (·.2 == .refuted) then .some
  else .unknown
def foldPremises (rs : List (Choice × ChoiceResult)) : ChoiceResult :=
  if rs.any (·.2 == .model) then .model
  else if !rs.isEmpty && rs.all (·.2 == .inconsistent) then .inconsistent else .unknown
/-- What an UNKNOWN entailment names (1.7). -/
inductive Reason | conflictStatus (status : ChoiceResult) (c : Choice) | noResult (c : Choice)
  deriving DecidableEq, Repr
def reasonOf (conflicts rs : List (Choice × ChoiceResult)) : Option Reason :=
  match foldConflict conflicts with
  | .free =>
    if foldEntailment conflicts rs == .unknown then
      (rs.find? (fun x => x.2 != .proved && x.2 != .refuted)).map (fun x => .noResult x.1)
    else none
  | s => (conflicts.find? (fun x => if s == .conflict then x.2 == .conflict else x.2 != .free)).map
      (fun x => .conflictStatus s x.1)

/-- A situation of a choice's filled document where the premises hold and the conclusion fails. -/
def CounterU (U : VE.NormDefaults.UDoc) (Γ : List VE.Formula) (φ : VE.Formula) : Prop :=
  ∃ S : VE.Structure.{0},
    VE.NormDefaults.BaseAdmissibleU U (restrictAll (VE.NormDefaults.fill U).T S) ∧
    DocumentExpansion (VE.NormDefaults.fill U) (restrictAll (VE.NormDefaults.fill U).T S) S ∧
    Sat S Γ ∧ ¬ φ.denote S []
/-- A situation of a choice's filled document where the premises hold. -/
def ConsistentU (U : VE.NormDefaults.UDoc) (Γ : List VE.Formula) : Prop :=
  ∃ S : VE.Structure.{0},
    VE.NormDefaults.BaseAdmissibleU U (restrictAll (VE.NormDefaults.fill U).T S) ∧
    DocumentExpansion (VE.NormDefaults.fill U) (restrictAll (VE.NormDefaults.fill U).T S) S ∧ Sat S Γ
/-- What a checked result says of its choice; RD-2a's theorems establish it for every result Lean records. -/
def Holds (N : NDoc) (Γ : List VE.Formula) (φ : VE.Formula) (c : Choice) : ChoiceResult → Prop
  | .proved => VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) ∧ EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
  | .refuted => CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
  | .free => VE.NormDefaults.ConflictFreeU.{u} (choiceU N c)
  | .conflict => ¬ VE.NormDefaults.ConflictFreeU.{0} (choiceU N c)
  | .model => ConsistentU (choiceU N c) (choiceDoc N.D c).2
  | .inconsistent => VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) ∧
      EntailsU.{u} (choiceU N c) (choiceDoc N.D c).2 .bottom
  | .unknown => True
/-- The rows are exactly the compatible choices taking `A`. -/
def Covers (N : NDoc) (A : Choice) (rs : List (Choice × ChoiceResult)) : Prop :=
  ∀ c, (Compatible N.D c ∧ ∀ x ∈ A, x ∈ c) ↔ c ∈ rs.map (·.1)
/-- The fold theorems' shared hypotheses: conflict rows `cs` and query rows `rs`, both exactly the compatible
    choices taking `A`, each row's result holding of its choice. -/
def RowsHold (N : NDoc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula) (cs rs : List (Choice × ChoiceResult)) :
    Prop :=
  Covers N A cs ∧ Covers N A rs ∧ (∀ x ∈ cs, Holds.{u} N [] .bottom x.1 x.2) ∧ ∀ x ∈ rs, Holds.{u} N Γ φ x.1 x.2

/-! ### What each fold says of its rows (the folds alone) -/

theorem foldConflict_free {rs : List (Choice × ChoiceResult)} (h : foldConflict rs = .free) :
    rs ≠ [] ∧ ∀ x ∈ rs, x.2 = .free := by
  unfold foldConflict at h
  split at h
  · cases h
  · split at h
    · rename_i hs
      simp only [Bool.and_eq_true, Bool.not_eq_true', List.isEmpty_eq_false_iff, List.all_eq_true,
        beq_iff_eq] at hs
      exact hs
    · cases h

theorem foldConflict_conflict {rs : List (Choice × ChoiceResult)} (h : foldConflict rs = .conflict) :
    ∃ x ∈ rs, x.2 = .conflict := by
  unfold foldConflict at h
  split at h
  · rename_i hs
    simpa using hs
  · split at h <;> cases h

/-- No entailment verdict past an unpassed gate (A2). -/
theorem foldEntailment_gate {cs rs : List (Choice × ChoiceResult)} (h : foldEntailment cs rs ≠ .unknown) :
    foldConflict cs = .free := by
  unfold foldEntailment at h
  split at h
  · exact absurd rfl h
  · rename_i hc
    simpa using hc

theorem foldEntailment_all {cs rs : List (Choice × ChoiceResult)} (h : foldEntailment cs rs = .all) :
    foldConflict cs = .free ∧ rs ≠ [] ∧ ∀ x ∈ rs, x.2 = .proved := by
  refine ⟨foldEntailment_gate (by rw [h]; exact nofun), ?_⟩
  unfold foldEntailment at h
  split at h
  · cases h
  · split at h
    · cases h
    · rename_i he
      split at h
      · rename_i ha
        simp only [List.isEmpty_iff] at he
        simp only [List.all_eq_true, beq_iff_eq] at ha
        exact ⟨he, ha⟩
      · split at h
        · cases h
        · split at h <;> cases h

theorem foldEntailment_none {cs rs : List (Choice × ChoiceResult)} (h : foldEntailment cs rs = .none) :
    foldConflict cs = .free ∧ rs ≠ [] ∧ ∀ x ∈ rs, x.2 = .refuted := by
  refine ⟨foldEntailment_gate (by rw [h]; exact nofun), ?_⟩
  unfold foldEntailment at h
  split at h
  · cases h
  · split at h
    · cases h
    · rename_i he
      split at h
      · cases h
      · split at h
        · rename_i ha
          simp only [List.isEmpty_iff] at he
          simp only [List.all_eq_true, beq_iff_eq] at ha
          exact ⟨he, ha⟩
        · split at h <;> cases h

theorem foldEntailment_some {cs rs : List (Choice × ChoiceResult)} (h : foldEntailment cs rs = .some) :
    foldConflict cs = .free ∧ (∃ x ∈ rs, x.2 = .proved) ∧ ∃ x ∈ rs, x.2 = .refuted := by
  refine ⟨foldEntailment_gate (by rw [h]; exact nofun), ?_⟩
  unfold foldEntailment at h
  split at h
  · cases h
  · split at h
    · cases h
    · split at h
      · cases h
      · split at h
        · cases h
        · split at h
          · rename_i ha
            simp only [Bool.and_eq_true, List.any_eq_true, beq_iff_eq] at ha
            exact ha
          · cases h

theorem foldPremises_model {rs : List (Choice × ChoiceResult)} (h : foldPremises rs = .model) :
    ∃ x ∈ rs, x.2 = .model := by
  unfold foldPremises at h
  split at h
  · rename_i hs
    simpa using hs
  · split at h <;> cases h

theorem foldPremises_inconsistent {rs : List (Choice × ChoiceResult)} (h : foldPremises rs = .inconsistent) :
    rs ≠ [] ∧ ∀ x ∈ rs, x.2 = .inconsistent := by
  unfold foldPremises at h
  split at h
  · cases h
  · split at h
    · rename_i hs
      simp only [Bool.and_eq_true, Bool.not_eq_true', List.isEmpty_eq_false_iff, List.all_eq_true,
        beq_iff_eq] at hs
      exact hs
    · cases h

/-- A covered choice has a row; every row is a covered choice. -/
theorem covers_row {N : NDoc} {A : Choice} {rs : List (Choice × ChoiceResult)} (hc : Covers N A rs) {c : Choice}
    (hcc : Compatible N.D c) (hA : ∀ x ∈ A, x ∈ c) : ∃ r, (c, r) ∈ rs := by
  obtain ⟨x, hx, he⟩ := List.mem_map.mp ((hc c).mp ⟨hcc, hA⟩)
  exact ⟨x.2, by rw [← he]; exact hx⟩

theorem covers_mem {N : NDoc} {A : Choice} {rs : List (Choice × ChoiceResult)} (hc : Covers N A rs)
    {x : Choice × ChoiceResult} (hx : x ∈ rs) : Compatible N.D x.1 ∧ ∀ y ∈ A, y ∈ x.1 :=
  (hc x.1).mpr (List.mem_map.mpr ⟨x, hx, rfl⟩)

/-! ### The fold theorems (6.4) -/

theorem fold_all_sound (N : NDoc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cs rs : List (Choice × ChoiceResult)) (hr : RowsHold.{u} N A Γ φ cs rs) (h : foldEntailment cs rs = .all) :
  ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) →
    VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) ∧ EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ := by
  obtain ⟨_, _, hall⟩ := foldEntailment_all h
  obtain ⟨_, hq, _, hrs⟩ := hr
  intro c hc hA
  obtain ⟨r, hm⟩ := covers_row hq hc hA
  have hp := hall _ hm
  have := hrs _ hm
  simp only at hp
  rw [hp] at this
  exact this

theorem fold_none_sound (N : NDoc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cs rs : List (Choice × ChoiceResult)) (hr : RowsHold.{u} N A Γ φ cs rs) (h : foldEntailment cs rs = .none) :
  ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) →
    VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) ∧ CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ := by
  obtain ⟨hf, _, hall⟩ := foldEntailment_none h
  obtain ⟨_, hfree⟩ := foldConflict_free hf
  obtain ⟨hcc, hq, hcs, hrs⟩ := hr
  intro c hc hA
  obtain ⟨r, hm⟩ := covers_row hq hc hA
  obtain ⟨r', hm'⟩ := covers_row hcc hc hA
  have hp := hall _ hm
  have hp' := hfree _ hm'
  have h1 := hrs _ hm
  have h2 := hcs _ hm'
  simp only at hp hp'
  rw [hp] at h1
  rw [hp'] at h2
  exact ⟨h2, h1⟩

theorem fold_some_sound (N : NDoc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cs rs : List (Choice × ChoiceResult)) (hr : RowsHold.{u} N A Γ φ cs rs) (h : foldEntailment cs rs = .some) :
  (∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → VE.NormDefaults.ConflictFreeU.{u} (choiceU N c)) ∧
  (∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧ EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ) ∧
  (∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧ CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ) := by
  obtain ⟨hf, ⟨xp, hxp, hp⟩, ⟨xn, hxn, hn⟩⟩ := foldEntailment_some h
  obtain ⟨_, hfree⟩ := foldConflict_free hf
  obtain ⟨hcc, hq, hcs, hrs⟩ := hr
  refine ⟨fun c hc hA => ?_, ?_, ?_⟩
  · obtain ⟨r', hm'⟩ := covers_row hcc hc hA
    have h2 := hcs _ hm'
    have hp' := hfree _ hm'
    simp only at hp'
    rw [hp'] at h2
    exact h2
  · obtain ⟨hc, hA⟩ := covers_mem hq hxp
    have h1 := hrs _ hxp
    rw [hp] at h1
    exact ⟨xp.1, hc, hA, h1.2⟩
  · obtain ⟨hc, hA⟩ := covers_mem hq hxn
    have h1 := hrs _ hxn
    rw [hn] at h1
    exact ⟨xn.1, hc, hA, h1⟩

theorem fold_conflict_free_sound (N : NDoc) (A : Choice) (cs : List (Choice × ChoiceResult)) (hc : Covers N A cs)
    (hr : ∀ x ∈ cs, Holds.{u} N [] .bottom x.1 x.2) (h : foldConflict cs = .free) :
  ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) := by
  obtain ⟨_, hfree⟩ := foldConflict_free h
  intro c hcc hA
  obtain ⟨r, hm⟩ := covers_row hc hcc hA
  have h2 := hr _ hm
  have hp := hfree _ hm
  simp only at hp
  rw [hp] at h2
  exact h2

theorem fold_conflict_sound (N : NDoc) (A : Choice) (cs : List (Choice × ChoiceResult)) (hc : Covers N A cs)
    (hr : ∀ x ∈ cs, Holds.{u} N [] .bottom x.1 x.2) (h : foldConflict cs = .conflict) :
  ∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧ ¬ VE.NormDefaults.ConflictFreeU.{0} (choiceU N c) := by
  obtain ⟨x, hx, hp⟩ := foldConflict_conflict h
  obtain ⟨hcc, hA⟩ := covers_mem hc hx
  have h2 := hr _ hx
  rw [hp] at h2
  exact ⟨x.1, hcc, hA, h2⟩

theorem fold_premises_model_sound (N : NDoc) (A : Choice) (ps : List (Choice × ChoiceResult)) (hc : Covers N A ps)
    (hr : ∀ x ∈ ps, Holds.{u} N [] .bottom x.1 x.2) (h : foldPremises ps = .model) :
  ∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧ ConsistentU (choiceU N c) (choiceDoc N.D c).2 := by
  obtain ⟨x, hx, hp⟩ := foldPremises_model h
  obtain ⟨hcc, hA⟩ := covers_mem hc hx
  have h2 := hr _ hx
  rw [hp] at h2
  exact ⟨x.1, hcc, hA, h2⟩

theorem fold_premises_inconsistent_sound (N : NDoc) (A : Choice) (ps : List (Choice × ChoiceResult))
    (hc : Covers N A ps) (hr : ∀ x ∈ ps, Holds.{u} N [] .bottom x.1 x.2) (h : foldPremises ps = .inconsistent) :
  ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) →
    VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) ∧ EntailsU.{u} (choiceU N c) (choiceDoc N.D c).2 .bottom := by
  obtain ⟨_, hall⟩ := foldPremises_inconsistent h
  intro c hcc hA
  obtain ⟨r, hm⟩ := covers_row hc hcc hA
  have h2 := hr _ hm
  have hp := hall _ hm
  simp only at hp
  rw [hp] at h2
  exact h2

/-! ## Conditions (1.8, 6.5) -/

/-- The coupling or narrowing labelled `l` fails on `c` (`couplingHolds`, `narrowingHolds`). -/
def excludedBy (D : Doc) (l : String) (c : Choice) : Bool :=
  D.couplings.any (fun K => "coupling:" ++ K.id == l && !couplingHolds D c K) ||
    D.narrowings.any (fun N => "narrowing:" ++ N.id == l && !narrowingHolds D c N)
/-- `A` names no candidate of set `s`, or names candidate `i`. -/
def allows (A : Choice) (s : String) (i : Nat) : Bool := (A.index s).all (· == i)
/-- The number of candidates of set `s`, found as `candidate` finds it; 0 when `D` has no such set. -/
def candCount (D : Doc) (s : String) : Nat := ((D.sets.find? (·.id == s)).map (·.candidates.length)).getD 0
/-- Two consecutive sets of `K` have candidates that `A` allows and whose labels on `K`'s axis differ (or one is
    missing); a coupling naming a set `D` lacks is skipped (`ve/readings_verdicts.py:126-134`). -/
def couplingExcludes (D : Doc) (A : Choice) (K : Coupling) : Bool :=
  K.sets.all (fun x => D.sets.any (·.id == x.1)) &&
  (K.sets.zip K.sets.tail).any (fun (x, y) =>
    (List.range (candCount D x.1)).any (fun i => allows A x.1 i &&
      (List.range (candCount D y.1)).any (fun j => allows A y.1 j &&
        match (candidate D x.1 i).bind (labelOf · K.axis), (candidate D y.1 j).bind (labelOf · K.axis) with
        | some l, some l' => l != l'
        | _, _ => true)))
/-- `N` is in force on a set that `A` does not fix, and drops one of its candidates
    (`ve/readings_verdicts.py:135-138`). -/
def narrowingExcludes (D : Doc) (A : Choice) (N : Narrowing) : Bool :=
  match inForce D N with
  | some R => (A.index R.id).isNone && R.candidates.any (fun a => !N.keeps.contains a.id)
  | none => false
/-- The couplings and narrowings in force that exclude some complete choice taking `A`, couplings first, each in
    document order (1.8). Computed locally, as Python computes it; it never enumerates the complete choices (SR3). -/
def restrictionsFor (D : Doc) (A : Choice) : List String :=
  (D.couplings.filter (couplingExcludes D A)).map ("coupling:" ++ ·.id) ++
    (D.narrowings.filter (narrowingExcludes D A)).map ("narrowing:" ++ ·.id)

/-! ### `restrictionsFor_spec` -/

/-- `c` with set `s`'s entry replaced by `(s, i)`. -/
def setAt (c : Choice) (s : String) (i : Nat) : Choice := c.map (fun x => if x.1 == s then (s, i) else x)

theorem setAt_fst (c : Choice) (s : String) (i : Nat) : (setAt c s i).map (·.1) = c.map (·.1) := by
  simp only [setAt, List.map_map]
  congr 1
  funext x
  simp only [Function.comp]
  split
  · rename_i h
    simp only [beq_iff_eq] at h
    simp [h]
  · rfl

theorem mem_setAt_of_ne {c : Choice} {s : String} {i : Nat} {x : String × Nat} (hx : x.1 ≠ s) :
    x ∈ setAt c s i ↔ x ∈ c := by
  simp only [setAt, List.mem_map]
  constructor
  · rintro ⟨y, hy, he⟩
    split at he
    · subst he; exact absurd rfl hx
    · subst he; exact hy
  · intro h
    exact ⟨x, h, by simp [hx]⟩

theorem mem_setAt_self {c : Choice} {s : String} (i : Nat) (hs : s ∈ c.map (·.1)) : (s, i) ∈ setAt c s i := by
  obtain ⟨y, hy, he⟩ := List.mem_map.mp hs
  exact List.mem_map.mpr ⟨y, hy, by simp [he]⟩

/-- A set's entry in a choice whose sets are distinct is its index. -/
theorem index_eq_of_mem {c : Choice} (hn : (c.map (·.1)).Nodup) {s : String} {i : Nat} (h : (s, i) ∈ c) :
    c.index s = some i := index_of_mem hn h

theorem index_none_of_not_mem {c : Choice} {s : String} (h : s ∉ c.map (·.1)) : c.index s = none := by
  simp only [Choice.index, Option.map_eq_none_iff, List.find?_eq_none]
  intro x hx he
  exact h (List.mem_map.mpr ⟨x, hx, by simpa using he⟩)

theorem index_some_of_mem {c : Choice} {s : String} (h : s ∈ c.map (·.1)) : ∃ i, c.index s = some i := by
  cases hi : c.index s with
  | some i => exact ⟨i, rfl⟩
  | none =>
    simp only [Choice.index, Option.map_eq_none_iff, List.find?_eq_none] at hi
    obtain ⟨x, hx, he⟩ := List.mem_map.mp h
    exact absurd (by simpa using he) (hi x hx)

theorem candidate_isSome_iff (D : Doc) (s : String) (i : Nat) :
    (candidate D s i).isSome = true ↔ i < candCount D s := by
  simp only [candidate, candCount]
  cases D.sets.find? (·.id == s) with
  | none => simp
  | some R =>
    simp only [Option.bind_some, Option.map_some, Option.getD_some]
    rw [Option.isSome_iff_ne_none, ne_eq, List.getElem?_eq_none_iff]
    omega

theorem candidate_of_mem {D : Doc} (hn : (D.sets.map (·.id)).Nodup) {R : ReadingSet} (hR : R ∈ D.sets) (i : Nat) :
    candidate D R.id i = R.candidates[i]? := by
  simp only [candidate, find_id_unique hn hR, Option.bind_some]

theorem complete_setAt {D : Doc} {c : Choice} (hc : complete D c = true) {s : String} {i : Nat}
    (hs : (candidate D s i).isSome = true) : complete D (setAt c s i) = true := by
  simp only [complete, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hc ⊢
  refine ⟨by rw [setAt_fst]; exact hc.1, fun x hx => ?_⟩
  simp only [setAt, List.mem_map] at hx
  obtain ⟨y, hy, he⟩ := hx
  split at he
  · subst he; exact hs
  · subst he; exact hc.2 y hy

/-- In a complete choice the set ids are distinct. -/
theorem complete_nodup {D : Doc} (hn : (D.sets.map (·.id)).Nodup) {c : Choice} (hc : complete D c = true) :
    (c.map (·.1)).Nodup := by
  simp only [complete, Bool.and_eq_true, beq_iff_eq] at hc
  rw [hc.1]; exact hn

/-- A compatible choice taking `A` fixes each set `A` names to the index `A` names first. -/
theorem allows_of_taking {A c : Choice} (hn : (c.map (·.1)).Nodup) (hA : ∀ x ∈ A, x ∈ c) {s : String} {i : Nat}
    (hi : c.index s = some i) : allows A s i = true := by
  simp only [allows]
  cases ha : A.index s with
  | none => rfl
  | some k =>
    have hk := index_eq_of_mem hn (hA _ (mem_of_index ha))
    rw [hi] at hk
    cases hk
    simp

/-- Setting a set `A` allows keeps the choice taking `A`, given a compatible choice taking `A` (which fixes every
    entry of `A` for its set). -/
theorem taking_setAt {A c : Choice} (hn : (c.map (·.1)).Nodup) (hA : ∀ x ∈ A, x ∈ c) {s : String} {i : Nat}
    (ha : allows A s i = true) : ∀ x ∈ A, x ∈ setAt c s i := by
  intro x hx
  by_cases hs : x.1 = s
  · obtain ⟨k, hk⟩ := index_some_of_mem (show s ∈ A.map (·.1) from List.mem_map.mpr ⟨x, hx, hs⟩)
    simp only [allows, hk, Option.all_some, beq_iff_eq] at ha
    subst ha
    -- every entry of `A` on `s` is the one `c` takes, which is `A`'s first
    have h1 := index_eq_of_mem hn (hA _ (mem_of_index hk))
    have h2 := index_eq_of_mem hn (hA x hx)
    rw [hs] at h2
    rw [h1] at h2
    cases h2
    obtain ⟨a, b⟩ := x
    simp only at hs
    subst hs
    exact mem_setAt_self _ (List.mem_map.mpr ⟨_, hA _ hx, rfl⟩)
  · exact (mem_setAt_of_ne hs).mpr (hA x hx)

theorem index_setAt_self {c : Choice} {s : String} {i : Nat} (hs : s ∈ c.map (·.1)) :
    (setAt c s i).index s = some i := by
  induction c with
  | nil => cases hs
  | cons x c ih =>
    simp only [setAt, Choice.index, List.map_cons] at ih ⊢
    by_cases hx : x.1 = s
    · have h1 : (x.1 == s) = true := by simp [hx]
      simp only [h1, if_true, List.find?_cons, beq_self_eq_true, Option.map_some]
    · have hc : s ∈ c.map (·.1) := by
        rcases List.mem_cons.mp hs with h | h
        · exact absurd h.symm hx
        · exact h
      have h1 : (x.1 == s) = false := by simp [hx]
      simp only [h1, Bool.false_eq_true, if_false, List.find?_cons]
      exact ih hc

theorem index_setAt_ne {c : Choice} {s t : String} {i : Nat} (h : t ≠ s) :
    (setAt c s i).index t = c.index t := by
  induction c with
  | nil => rfl
  | cons x c ih =>
    simp only [setAt, Choice.index, List.map_cons] at ih ⊢
    by_cases hx : x.1 = s
    · have h1 : (x.1 == s) = true := by simp [hx]
      have h2 : (s == t) = false := by simp [Ne.symm h]
      have h3 : (x.1 == t) = false := by simp [hx, Ne.symm h]
      simp only [h1, if_true, List.find?_cons, h2, h3]
      exact ih
    · have h1 : (x.1 == s) = false := by simp [hx]
      simp only [h1, Bool.false_eq_true, if_false, List.find?_cons]
      cases (x.1 == t)
      · exact ih
      · rfl

/-- The narrowing part of `restrictionsFor_spec`. -/
theorem narrowingExcludes_iff (D : Doc) (hn : (D.sets.map (·.id)).Nodup) (A : Choice)
    (hA : ∃ c, Compatible D c ∧ ∀ x ∈ A, x ∈ c) (N : Narrowing) (hN : N ∈ D.narrowings) :
    narrowingExcludes D A N = true ↔
      ∃ c, complete D c = true ∧ (∀ x ∈ A, x ∈ c) ∧ narrowingHolds D c N = false := by
  obtain ⟨c0, hc0, hA0⟩ := hA
  simp only [Compatible, compatible, Bool.and_eq_true, List.all_eq_true] at hc0
  have hcomp0 : complete D c0 = true := hc0.1.1
  have hh0 : narrowingHolds D c0 N = true := hc0.2 N hN
  have hn0 := complete_nodup hn hcomp0
  unfold narrowingExcludes
  cases hf : inForce D N with
  | none =>
    simp only [Bool.false_eq_true, false_iff, not_exists, not_and]
    intro c _ _
    simp [narrowingHolds, hf]
  | some R =>
    have hR : R ∈ D.sets := List.mem_of_find?_eq_some hf
    have hsets : ∀ {c : Choice}, complete D c = true → R.id ∈ c.map (·.1) := fun hc => by
      simp only [complete, Bool.and_eq_true, beq_iff_eq] at hc
      rw [hc.1]; exact List.mem_map.mpr ⟨R, hR, rfl⟩
    simp only [Bool.and_eq_true, Option.isNone_iff_eq_none, List.any_eq_true, Bool.not_eq_true']
    constructor
    · rintro ⟨hAR, a, ha, hk⟩
      obtain ⟨j, hj, rfl⟩ := List.getElem_of_mem ha
      refine ⟨setAt c0 R.id j, complete_setAt hcomp0 (by rw [candidate_of_mem hn hR]; simp [hj]),
        taking_setAt hn0 hA0 (by simp [allows, hAR]), ?_⟩
      simp only [narrowingHolds, hf, index_setAt_self (hsets hcomp0), List.getElem?_eq_getElem hj,
        Option.map_some, Option.getD_some]
      simpa [List.contains_iff_mem] using hk
    · rintro ⟨c, hc, hAc, hh⟩
      have hnc := complete_nodup hn hc
      obtain ⟨i, hi⟩ := index_some_of_mem (hsets hc)
      simp only [narrowingHolds, hf, hi] at hh
      refine ⟨?_, ?_⟩
      · cases hAi : A.index R.id with
        | none => rfl
        | some k =>
          exfalso
          have hk := mem_of_index hAi
          have h1 := index_eq_of_mem hnc (hAc _ hk)
          rw [hi] at h1
          cases h1
          have h0 := index_eq_of_mem hn0 (hA0 _ hk)
          simp only [narrowingHolds, hf, h0] at hh0
          rw [hh0] at hh
          cases hh
      · have hci : (candidate D R.id i).isSome = true := by
          simp only [complete, Bool.and_eq_true, List.all_eq_true] at hc
          exact hc.2 _ (mem_of_index hi)
        rw [candidate_of_mem hn hR] at hci
        obtain ⟨a, ha⟩ := Option.isSome_iff_exists.mp hci
        rw [ha] at hh
        refine ⟨a, List.mem_of_getElem? ha, ?_⟩
        simpa [List.contains_iff_mem] using hh

/-- Consecutive sets of a coupling with distinct set names are distinct. -/
theorem zip_tail_ne {l : List (String × Nat)} (hn : (l.map (·.1)).Nodup) {x y : String × Nat}
    (h : (x, y) ∈ l.zip l.tail) : x.1 ≠ y.1 := by
  induction l with
  | nil => cases h
  | cons a l ih =>
    cases l with
    | nil => cases h
    | cons b l =>
      simp only [List.tail_cons, List.zip_cons_cons, List.mem_cons] at h
      rw [List.map_cons, List.nodup_cons] at hn
      rcases h with h | h
      · simp only [Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        exact fun e => hn.1 (List.mem_map.mpr ⟨y, List.mem_cons_self, e.symm⟩)
      · exact ih hn.2 (by simpa using h)

/-- The coupling part of `restrictionsFor_spec`. -/
theorem couplingExcludes_iff (D : Doc) (hn : (D.sets.map (·.id)).Nodup) (A : Choice)
    (hA : ∃ c, Compatible D c ∧ ∀ x ∈ A, x ∈ c) (K : Coupling) (hk : couplingShape D K = true) :
    couplingExcludes D A K = true ↔
      ∃ c, complete D c = true ∧ (∀ x ∈ A, x ∈ c) ∧ couplingHolds D c K = false := by
  obtain ⟨c0, hc0, hA0⟩ := hA
  simp only [Compatible, compatible, Bool.and_eq_true, List.all_eq_true] at hc0
  have hcomp0 : complete D c0 = true := hc0.1.1
  have hn0 := complete_nodup hn hcomp0
  simp only [couplingShape, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.any_eq_true,
    beq_iff_eq] at hk
  obtain ⟨⟨_, hkn⟩, hks⟩ := hk
  have hset : ∀ x ∈ K.sets, ∃ R ∈ D.sets, R.id = x.1 := fun x hx => by
    obtain ⟨R, hR, h⟩ := hks x hx
    exact ⟨R, hR, by simpa using h.1.1⟩
  have hsets : ∀ {c : Choice}, complete D c = true → ∀ x ∈ K.sets, x.1 ∈ c.map (·.1) := fun hc x hx => by
    simp only [complete, Bool.and_eq_true, beq_iff_eq] at hc
    obtain ⟨R, hR, he⟩ := hset x hx
    rw [hc.1]; exact List.mem_map.mpr ⟨R, hR, he⟩
  have hfirst : (K.sets.all (fun x => D.sets.any (·.id == x.1))) = true := by
    simp only [List.all_eq_true, List.any_eq_true, beq_iff_eq]
    exact hset
  unfold couplingExcludes
  rw [hfirst, Bool.true_and]
  simp only [List.any_eq_true, Bool.and_eq_true, List.mem_range]
  constructor
  · rintro ⟨⟨x, y⟩, hxy, i, hi, hai, j, hj, haj, hl⟩
    have hx : x ∈ K.sets := (List.of_mem_zip hxy).1
    have hy : y ∈ K.sets := List.mem_of_mem_tail (List.of_mem_zip hxy).2
    have hne := zip_tail_ne hkn hxy
    let c1 := setAt c0 x.1 i
    let c := setAt c1 y.1 j
    have hn1 : (c1.map (·.1)).Nodup := by simp only [c1, setAt_fst]; exact hn0
    have hA1 := taking_setAt hn0 hA0 hai
    have hcomp1 := complete_setAt hcomp0 ((candidate_isSome_iff D _ _).mpr hi)
    refine ⟨c, complete_setAt hcomp1 ((candidate_isSome_iff D _ _).mpr hj), taking_setAt hn1 hA1 ?_, ?_⟩
    · -- `A` allows `j` on `y`, and setting `x` first does not change what `A` reads
      exact haj
    · simp only [couplingHolds, List.all_eq_false]
      refine ⟨(x, y), hxy, ?_⟩
      have hix : c.index x.1 = some i := by
        simp only [c]
        rw [index_setAt_ne hne]
        exact index_setAt_self (hsets hcomp0 x hx)
      have hiy : c.index y.1 = some j := index_setAt_self (by simp only [c1, setAt_fst]; exact hsets hcomp0 y hy)
      simp only [hix, hiy]
      revert hl
      cases (candidate D x.1 i).bind (labelOf · K.axis) <;> cases (candidate D y.1 j).bind (labelOf · K.axis) <;>
        simp
  · rintro ⟨c, hc, hAc, hh⟩
    have hnc := complete_nodup hn hc
    simp only [couplingHolds, List.all_eq_false] at hh
    obtain ⟨⟨x, y⟩, hxy, hb⟩ := hh
    have hx : x ∈ K.sets := (List.of_mem_zip hxy).1
    have hy : y ∈ K.sets := List.mem_of_mem_tail (List.of_mem_zip hxy).2
    obtain ⟨i, hi⟩ := index_some_of_mem (hsets hc x hx)
    obtain ⟨j, hj⟩ := index_some_of_mem (hsets hc y hy)
    simp only [hi, hj] at hb
    have hcs : ∀ {s : String} {k : Nat}, c.index s = some k → k < candCount D s := fun h => by
      simp only [complete, Bool.and_eq_true, List.all_eq_true] at hc
      exact (candidate_isSome_iff D _ _).mp (hc.2 _ (mem_of_index h))
    refine ⟨(x, y), hxy, i, hcs hi, allows_of_taking hnc hAc hi, j, hcs hj, allows_of_taking hnc hAc hj, ?_⟩
    revert hb
    cases (candidate D x.1 i).bind (labelOf · K.axis) <;> cases (candidate D y.1 j).bind (labelOf · K.axis) <;>
      simp

/-- The local computation is the existential meaning, given distinct set ids, `supReady`'s coupling shape, and a
    compatible choice taking `A` (SR3). -/
theorem restrictionsFor_spec (D : Doc) (hn : (D.sets.map (·.id)).Nodup)
    (hk : D.couplings.all (couplingShape D) = true) (A : Choice) (hA : ∃ c, Compatible D c ∧ ∀ x ∈ A, x ∈ c)
    (l : String) :
  l ∈ restrictionsFor D A ↔ ∃ c, complete D c = true ∧ (∀ x ∈ A, x ∈ c) ∧ excludedBy D l c = true := by
  simp only [restrictionsFor, List.mem_append, List.mem_map, List.mem_filter]
  simp only [List.all_eq_true] at hk
  constructor
  · rintro (⟨K, ⟨hK, he⟩, rfl⟩ | ⟨N, ⟨hN, he⟩, rfl⟩)
    · obtain ⟨c, hc, hAc, hh⟩ := (couplingExcludes_iff D hn A hA K (hk K hK)).mp he
      refine ⟨c, hc, hAc, ?_⟩
      simp only [excludedBy, Bool.or_eq_true, List.any_eq_true, Bool.and_eq_true, beq_iff_eq, Bool.not_eq_true']
      exact Or.inl ⟨K, hK, rfl, hh⟩
    · obtain ⟨c, hc, hAc, hh⟩ := (narrowingExcludes_iff D hn A hA N hN).mp he
      refine ⟨c, hc, hAc, ?_⟩
      simp only [excludedBy, Bool.or_eq_true, List.any_eq_true, Bool.and_eq_true, beq_iff_eq, Bool.not_eq_true']
      exact Or.inr ⟨N, hN, rfl, hh⟩
  · rintro ⟨c, hc, hAc, hx⟩
    simp only [excludedBy, Bool.or_eq_true, List.any_eq_true, Bool.and_eq_true, beq_iff_eq,
      Bool.not_eq_true'] at hx
    rcases hx with ⟨K, hK, rfl, hh⟩ | ⟨N, hN, rfl, hh⟩
    · exact Or.inl ⟨K, ⟨hK, (couplingExcludes_iff D hn A hA K (hk K hK)).mpr ⟨c, hc, hAc, hh⟩⟩, rfl⟩
    · exact Or.inr ⟨N, ⟨hN, (narrowingExcludes_iff D hn A hA N hN).mpr ⟨c, hc, hAc, hh⟩⟩, rfl⟩

/-! ### The labels an answer uses -/

/-- `L` with the formulas of every label outside `keep` replaced by `⊤`. -/
def blank (L : VE.Compose.Labelled) (keep : List String) : List VE.Formula :=
  L.map (fun x => if keep.contains x.1 then x.2 else .top)
/-- Greedy, in label order: a label is dropped when every check still passes without it. -/
def usedLabels (check : List VE.Formula → Bool) (pre : List VE.Formula) (L : VE.Compose.Labelled)
    (post : List VE.Formula) : List String :=
  (L.map (·.1)).foldl (fun keep l =>
    if check (pre ++ blank L (keep.erase l) ++ post) then keep.erase l else keep) (L.map (·.1))

theorem blank_all (L : VE.Compose.Labelled) : blank L (L.map (·.1)) = L.formulas := by
  simp only [blank, VE.Compose.Labelled.formulas]
  apply List.map_congr_left
  intro x hx
  have : (L.map (·.1)).contains x.1 = true := List.contains_iff_mem.mpr (List.mem_map.mpr ⟨x, hx, rfl⟩)
  rw [if_pos this]

theorem usedLabels_sound (check : List VE.Formula → Bool) (pre : List VE.Formula) (L : VE.Compose.Labelled)
    (post : List VE.Formula) (hl : L.wellLabelled = true) (h : check (pre ++ L.formulas ++ post) = true) :
  check (pre ++ blank L (usedLabels check pre L post) ++ post) = true := by
  have _ := hl
  unfold usedLabels
  suffices ∀ (ls keep : List String), check (pre ++ blank L keep ++ post) = true →
      check (pre ++ blank L (ls.foldl (fun keep l =>
        if check (pre ++ blank L (keep.erase l) ++ post) then keep.erase l else keep) keep) ++ post) = true from
    this _ _ (by rw [blank_all]; exact h)
  intro ls
  induction ls with
  | nil => exact fun _ h => h
  | cons l ls ih =>
    intro keep hk
    simp only [List.foldl_cons]
    apply ih
    split
    · assumption
    · exact hk

end VE.Readings
