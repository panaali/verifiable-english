import VE.Readings.Choice

/-! The theorems of the superposed route (docs/spec/composition-s2.md 8.4).

The choice atoms are patterns over bit literals on one constant, so every structure spells exactly one pattern
per set (`pattern_denote`, `pattern_unique`): a slot-admissible base of `sup D` encodes one compatible choice
(`encodes_unique`), and the choice's atoms hold in a structure exactly for the entries of the choice it encodes
(`encodes_atoms`). A certificate from `choiceCore D` is about the bits alone: every compatible choice gives a
one-element structure, admissible over the certificate's vocabulary because the checker types every premise,
that satisfies the core with the choice's atoms true (`dead_sound`, `unsat_sound`). -/
namespace VE.Readings
open VE.Norms (Regulated Sat tupleVal envAt size elaborate targets)
open VE.SoftNorms (SoftDoc soften ValueSoft circ WellFormedSoft)
open VE.Rights (RightsDoc correlate limPremises BaseAdmissibleR RightsConflictFree)
open VE.Compose (BaseAdmissibleP ConflictFreeP SlotWellFormed backgroundP backgroundValidP slotConflictFreeCheck
  adjoinOne Labelled)
universe u

/-! ## Identity, well-formedness, the slot -/

/-- Definitional: superposable D runs the chain's check on sup D. Stated so that the instance is a checked fact. -/
theorem sup_wellFormed (D : Doc) (hs : superposable D = true) :
    chainWF D.chain (sup D).1 = true ∧ WellFormedSoft (correlate (sup D).1) = true := by
  simp only [superposable, sideWF, Bool.and_eq_true] at hs
  exact ⟨hs.2.1, chain_soft D.chain _ hs.2.1⟩

/-! ## Bits -/

/-- The number whose bit `j` is `P j` for `j < b`. -/
def bitsVal (P : Nat → Bool) : Nat → Nat
  | 0 => 0
  | b + 1 => bitsVal P b + (if P b then 2 ^ b else 0)

theorem bitsVal_lt (P : Nat → Bool) : ∀ b, bitsVal P b < 2 ^ b
  | 0 => by simp [bitsVal]
  | b + 1 => by
    have := bitsVal_lt P b
    simp only [bitsVal, Nat.pow_succ]
    split <;> omega

theorem testBit_ge {x b j : Nat} (hx : x < 2 ^ b) (hj : b ≤ j) : x.testBit j = false :=
  Nat.testBit_lt_two_pow (Nat.lt_of_lt_of_le hx (Nat.pow_le_pow_right (by decide) hj))

theorem testBit_bitsVal (P : Nat → Bool) : ∀ b j, (bitsVal P b).testBit j = (decide (j < b) && P j)
  | 0, j => by simp [bitsVal]
  | b + 1, j => by
    have hlt := bitsVal_lt P b
    simp only [bitsVal]
    by_cases hP : P b
    · rw [if_pos hP, Nat.add_comm]
      rcases Nat.lt_trichotomy j b with h | rfl | h
      · rw [Nat.testBit_two_pow_add_gt h, testBit_bitsVal P b j]
        simp [h, Nat.lt_succ_of_lt h]
      · rw [Nat.testBit_two_pow_add_eq, Nat.testBit_lt_two_pow hlt]
        simp [hP]
      · have : 2 ^ b + bitsVal P b < 2 ^ (b + 1) := by rw [Nat.pow_succ]; omega
        rw [testBit_ge this h]
        simp; omega
    · simp only [hP, Bool.false_eq_true, if_false, Nat.add_zero]
      rw [testBit_bitsVal P b j]
      by_cases hj : j = b
      · subst hj; simp [hP]
      · by_cases h : j < b
        · simp [h, Nat.lt_succ_of_lt h]
        · simp [h]; omega

theorem eq_of_low_bits {b x y : Nat} (hx : x < 2 ^ b) (hy : y < 2 ^ b)
    (h : ∀ j, j < b → x.testBit j = y.testBit j) : x = y := by
  apply Nat.eq_of_testBit_eq
  intro j
  by_cases hj : j < b
  · exact h j hj
  · rw [testBit_ge hx (by omega), testBit_ge hy (by omega)]

theorem le_two_pow_bitsOf (k : Nat) : k ≤ 2 ^ bitsOf k := by
  unfold bitsOf
  cases hf : (List.range (k + 1)).find? (fun b => decide (k ≤ 2 ^ b)) with
  | none =>
    have := List.find?_eq_none.mp hf k (List.mem_range.mpr (Nat.lt_succ_self k))
    simp only [decide_eq_true_eq] at this
    exact absurd (Nat.le_of_lt (Nat.lt_pow_self (by decide))) this
  | some b =>
    have := List.find?_some hf
    simpa using this

/-! ## Conjunctions and patterns -/

theorem conj_denote (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    ∀ l : List VE.Formula, (conj l).denote S ρ ↔ ∀ a ∈ l, a.denote S ρ
  | [] => by simp [conj, VE.Formula.denote]
  | [a] => by simp [conj]
  | a :: b :: l => by
    show (VE.Formula.and a (conj (b :: l))).denote S ρ ↔ _
    rw [VE.Formula.denote, conj_denote S ρ (b :: l)]
    simp

theorem disj_denote (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    ∀ l : List VE.Formula, (disj l).denote S ρ ↔ ∃ a ∈ l, a.denote S ρ
  | [] => by simp [disj, VE.Formula.denote]
  | [a] => by simp [disj]
  | a :: b :: l => by
    show (VE.Formula.or a (disj (b :: l))).denote S ρ ↔ _
    rw [VE.Formula.denote, disj_denote S ρ (b :: l)]
    simp

/-- The positive literal of bit `j` of the `n`-th set. -/
def bitOn (S : VE.Structure.{u}) (n j : Nat) : Prop := (VE.Formula.unary (bitName n j) here).denote S []

theorem pattern_denote (S : VE.Structure.{u}) (n k i : Nat) :
    (pattern n k i).denote S [] ↔ ∀ j, j < bitsOf k → (bitOn S n j ↔ i.testBit j = true) := by
  rw [pattern, conj_denote]
  simp only [List.mem_map, List.mem_range, forall_exists_index, and_imp, forall_apply_eq_imp_iff₂]
  apply forall_congr'; intro j; apply imp_congr_right; intro _
  unfold lit bitOn
  cases i.testBit j <;> simp [VE.Formula.denote]

/-- Two indices spelled by one structure in one set are equal. -/
theorem pattern_unique (S : VE.Structure.{u}) (n k i i' : Nat) (hi : i < 2 ^ bitsOf k) (hi' : i' < 2 ^ bitsOf k)
    (h : (pattern n k i).denote S []) (h' : (pattern n k i').denote S []) : i = i' := by
  rw [pattern_denote] at h h'
  apply eq_of_low_bits hi hi'
  intro j hj
  have a := h j hj
  have b := h' j hj
  cases hx : i.testBit j <;> cases hy : i'.testBit j <;> simp_all

/-- Every structure spells some index below 2^b in every set. -/
theorem pattern_exists (S : VE.Structure.{u}) (n k : Nat) :
    ∃ i, i < 2 ^ bitsOf k ∧ (pattern n k i).denote S [] := by
  classical
  refine ⟨bitsVal (fun j => decide (bitOn S n j)) (bitsOf k), bitsVal_lt _ _, ?_⟩
  rw [pattern_denote]
  intro j hj
  rw [testBit_bitsVal]
  simp [hj]

/-! ## Sets and atoms -/

theorem findIdx_set {D : Doc} {s : String} {m : Nat} (h : D.sets.findIdx? (·.id == s) = some m) :
    ∃ hm : m < D.sets.length, D.sets[m].id = s := by
  obtain ⟨hm, hp, _⟩ := List.findIdx?_eq_some_iff_getElem.mp h
  exact ⟨hm, by simpa using hp⟩

theorem findIdx_of_nodup {D : Doc} (hn : (D.sets.map (·.id)).Nodup) {m : Nat} (hm : m < D.sets.length) :
    D.sets.findIdx? (·.id == D.sets[m].id) = some m := by
  apply List.findIdx?_eq_some_iff_getElem.mpr
  refine ⟨hm, by simp, fun j hj => ?_⟩
  simp only [beq_iff_eq]
  intro he
  have hj' : j < D.sets.length := Nat.lt_trans hj hm
  have := List.pairwise_iff_getElem.mp hn j m (by simp; exact hj') (by simp; exact hm) hj
  simp only [List.getElem_map] at this
  exact this he

theorem find_eq_findIdx {α : Type} (p : α → Bool) (l : List α) : l.find? p = (l.findIdx? p).bind (l[·]?) := by
  cases h : l.findIdx? p with
  | none =>
    simp only [Option.bind_none]
    apply List.find?_eq_none.mpr
    intro x hx
    simp [List.findIdx?_eq_none_iff.mp h x hx]
  | some m =>
    obtain ⟨hm, hp, hj⟩ := List.findIdx?_eq_some_iff_getElem.mp h
    simp only [Option.bind_some, List.getElem?_eq_getElem hm]
    apply List.find?_eq_some_iff_getElem.mpr
    exact ⟨hp, m, hm, rfl, fun j hjm => by simpa using hj j hjm⟩

theorem find_findIdx {D : Doc} {s : String} {m : Nat} (h : D.sets.findIdx? (·.id == s) = some m) :
    D.sets.find? (·.id == s) = D.sets[m]? := by
  rw [find_eq_findIdx, h]
  rfl

theorem setSize_eq {D : Doc} {m : Nat} (hm : m < D.sets.length) : setSize D m = D.sets[m].candidates.length := by
  simp [setSize, List.getElem?_eq_getElem hm]

/-- The set and index of a valid entry. -/
theorem candidate_isSome {D : Doc} {s : String} {i : Nat} (h : (candidate D s i).isSome = true) :
    ∃ m, D.sets.findIdx? (·.id == s) = some m ∧ i < setSize D m := by
  simp only [candidate, Option.isSome_iff_exists, Option.bind_eq_some_iff] at h
  obtain ⟨a, R, hR, ha⟩ := h
  cases hf : D.sets.findIdx? (·.id == s) with
  | none =>
    rw [find_eq_findIdx, hf] at hR
    cases hR
  | some m =>
    rw [find_findIdx hf] at hR
    obtain ⟨hm, _⟩ := findIdx_set hf
    rw [List.getElem?_eq_getElem hm] at hR
    cases hR
    refine ⟨m, rfl, ?_⟩
    rw [setSize_eq hm]
    exact (List.getElem?_eq_some_iff.mp ha).1

theorem choiceAtom_eq {D : Doc} {s : String} {i m : Nat} (hf : D.sets.findIdx? (·.id == s) = some m)
    (hi : i < setSize D m) : choiceAtom D s i = pattern (m + 1) (setSize D m) i := by
  simp [choiceAtom, hf, hi]

theorem choiceAtom_bottom {D : Doc} {s : String} {i : Nat}
    (h : ¬ ∃ m, D.sets.findIdx? (·.id == s) = some m ∧ i < setSize D m) : choiceAtom D s i = .bottom := by
  unfold choiceAtom
  split
  · rename_i m hm
    rw [if_neg (fun hi => h ⟨m, hm, hi⟩)]
  · rfl

theorem complete_mem {D : Doc} {c : Choice} (hc : complete D c = true) {x : String × Nat} (hx : x ∈ c) :
    (candidate D x.1 x.2).isSome = true := by
  simp only [complete, Bool.and_eq_true, List.all_eq_true] at hc
  exact hc.2 x hx

theorem complete_map {D : Doc} {c : Choice} (hc : complete D c = true) : c.map (·.1) = D.sets.map (·.id) := by
  simp only [complete, Bool.and_eq_true, beq_iff_eq] at hc
  exact hc.1

/-- `encodes_atoms`: under an encoding, the atoms of `A` hold exactly when `A`'s entries are the choice's. -/
theorem encodes_atoms (D : Doc) (c : Choice) (hc : complete D c = true) (S : VE.Structure.{u}) (he : Encodes D c S)
    (A : Choice) : Sat S (atoms D A) ↔ ∀ x ∈ A, x ∈ c := by
  simp only [Sat, atoms, List.mem_map, forall_exists_index, and_imp, forall_apply_eq_imp_iff₂]
  apply forall_congr'; intro x; apply imp_congr_right; intro _
  by_cases hx : ∃ m, D.sets.findIdx? (·.id == x.1) = some m ∧ x.2 < setSize D m
  · obtain ⟨m, hf, hi⟩ := hx
    obtain ⟨hm, hid⟩ := findIdx_set hf
    have := he D.sets[m] (List.getElem_mem hm) x.2 (by rw [← setSize_eq hm]; exact hi)
    rw [hid] at this
    exact this
  · rw [choiceAtom_bottom hx]
    simp only [VE.Formula.denote, false_iff]
    intro hxc
    exact hx (candidate_isSome (complete_mem hc hxc))

/-! ## Every admissible base of sup D is one compatible choice -/

theorem sat_of_mem_labelled {S : VE.Structure.{u}} {L : Labelled} (h : Sat S L.formulas) {l : String}
    {a : VE.Formula} (ha : (l, a) ∈ L) : a.denote S [] :=
  h a (List.mem_map.mpr ⟨(l, a), ha, rfl⟩)

theorem slotP_choice {D : Doc} {S : VE.Structure.{u}} (h : Sat S (slotP D)) : Sat S (choicePremises D) := by
  intro a ha
  apply h a
  simp only [slotP, slotLabelled, Labelled.formulas, List.map_append, List.mem_append]
  exact Or.inl (Or.inr ha)

theorem choice_core_sat {D : Doc} {S : VE.Structure.{u}} (h : Sat S (choicePremises D)) :
    Sat S (onePremises D).formulas ∧ Sat S (couplingPremises D).formulas ∧ Sat S (narrowingPremises D).formulas := by
  simp only [choicePremises, choiceLabelled, Labelled.formulas, List.map_append] at h
  refine ⟨fun a ha => h a ?_, fun a ha => h a ?_, fun a ha => h a ?_⟩ <;> simp_all [Labelled.formulas]

theorem isEmpty_false_of_mem {α : Type} {l : List α} {a : α} (h : a ∈ l) : l.isEmpty = false := by
  cases l <;> simp_all

/-- The one premise of the `m`-th set: no index at or above the set's size is spelled. -/
theorem one_sat {D : Doc} {S : VE.Structure.{u}} (h : Sat S (onePremises D).formulas) {m : Nat}
    (hm : m < D.sets.length) {i : Nat} (hi : i < 2 ^ bitsOf (setSize D m))
    (hp : (pattern (m + 1) (setSize D m) i).denote S []) : i < setSize D m := by
  refine Classical.byContradiction fun hk => ?_
  rw [setSize_eq hm] at hk hi hp
  have hu : i ∈ (List.range (2 ^ bitsOf D.sets[m].candidates.length)).filter (D.sets[m].candidates.length ≤ ·) := by
    simp only [List.mem_filter, List.mem_range, decide_eq_true_eq]; omega
  have hmem : ("readings:" ++ label D.sets[m] ++ ":one",
      conj (((List.range (2 ^ bitsOf D.sets[m].candidates.length)).filter (D.sets[m].candidates.length ≤ ·)).map
        (fun i => .not (pattern (m + 1) D.sets[m].candidates.length i)))) ∈ onePremises D := by
    simp only [onePremises, List.mem_filterMap, List.mem_range]
    refine ⟨m, hm, ?_⟩
    rw [List.getElem?_eq_getElem hm]
    simp only [Option.bind_some]
    rw [if_neg (by rw [isEmpty_false_of_mem hu]; decide)]
  exact (conj_denote S [] _).mp (sat_of_mem_labelled h hmem) _ (List.mem_map.mpr ⟨i, hu, rfl⟩) hp

theorem ids_inj {D : Doc} (hn : (D.sets.map (·.id)).Nodup) {m m' : Nat} (hm : m < D.sets.length)
    (hm' : m' < D.sets.length) (he : D.sets[m].id = D.sets[m'].id) : m = m' := by
  rcases Nat.lt_trichotomy m m' with h | h | h
  · have := List.pairwise_iff_getElem.mp hn m m' (by simpa using hm) (by simpa using hm') h
    simp only [List.getElem_map] at this
    exact absurd he this
  · exact h
  · have := List.pairwise_iff_getElem.mp hn m' m (by simpa using hm') (by simpa using hm) h
    simp only [List.getElem_map] at this
    exact absurd he.symm this

theorem supReady_nodup {D : Doc} (hr : supReady D = true) : (D.sets.map (·.id)).Nodup := by
  simp only [supReady, Bool.and_eq_true, decide_eq_true_eq] at hr
  exact hr.1.1.1.1.1.1

theorem superposable_supReady {D : Doc} (hs : superposable D = true) : supReady D = true := by
  simp only [superposable, Bool.and_eq_true] at hs
  exact hs.1.1

/-- The atom of a set given by its position, under a structure that spells `v` there. -/
theorem atom_at {D : Doc} (hn : (D.sets.map (·.id)).Nodup) (S : VE.Structure.{u}) {m : Nat}
    (hm : m < D.sets.length) {v : Nat} (hv : v < setSize D m)
    (hp : (pattern (m + 1) (setSize D m) v).denote S []) {i : Nat} (hi : i < setSize D m) :
    (choiceAtom D D.sets[m].id i).denote S [] ↔ i = v := by
  rw [choiceAtom_eq (findIdx_of_nodup hn hm) hi]
  have hk := le_two_pow_bitsOf (setSize D m)
  constructor
  · intro h; exact pattern_unique S _ _ _ _ (by omega) (by omega) h hp
  · rintro rfl; exact hp

theorem mem_sets_getElem {D : Doc} {R : ReadingSet} (h : R ∈ D.sets) : ∃ m, ∃ hm : m < D.sets.length, D.sets[m] = R :=
  List.getElem_of_mem h

theorem find_of_nodup {D : Doc} (hn : (D.sets.map (·.id)).Nodup) {m : Nat} (hm : m < D.sets.length) :
    D.sets.find? (·.id == D.sets[m].id) = some D.sets[m] := by
  rw [find_findIdx (findIdx_of_nodup hn hm), List.getElem?_eq_getElem hm]

theorem candidate_at {D : Doc} (hn : (D.sets.map (·.id)).Nodup) {m : Nat} (hm : m < D.sets.length) (i : Nat) :
    candidate D D.sets[m].id i = D.sets[m].candidates[i]? := by
  simp [candidate, find_of_nodup hn hm]

/-- Every slot-admissible base of `sup D` encodes exactly one compatible choice among the complete ones. -/
theorem encodes_unique (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) (B : VE.Structure.{u})
    (hB : BaseAdmissibleP (correlate (sup D).1) (slotP D) B) :
    ∃ c, Compatible D c ∧ Encodes D c B ∧ ∀ c', complete D c' = true → Encodes D c' B → c' = c := by
  classical
  have hr := superposable_supReady hs
  have hn := supReady_nodup hr
  obtain ⟨hone, hcp, hnp⟩ := choice_core_sat (slotP_choice hB.2)
  let val : Nat → Nat := fun m => bitsVal (fun j => decide (bitOn B (m + 1) j)) (bitsOf (setSize D m))
  have hpat : ∀ m, (pattern (m + 1) (setSize D m) (val m)).denote B [] := by
    intro m
    rw [pattern_denote]
    intro j hj
    show bitOn B (m + 1) j ↔ (bitsVal _ _).testBit j = true
    rw [testBit_bitsVal]
    simp [hj]
  have hval : ∀ m (hm : m < D.sets.length), val m < setSize D m :=
    fun m hm => one_sat hone hm (bitsVal_lt _ _) (hpat m)
  have hatom : ∀ m (hm : m < D.sets.length) i, i < setSize D m →
      ((choiceAtom D D.sets[m].id i).denote B [] ↔ i = val m) :=
    fun m hm i hi => atom_at hn B hm (hval m hm) (hpat m) hi
  let c : Choice := List.ofFn (fun m : Fin D.sets.length => (D.sets[m].id, val m))
  have hlen : c.length = D.sets.length := List.length_ofFn
  have hmap : c.map (·.1) = D.sets.map (·.id) := by
    apply List.ext_getElem (by simp [c])
    intro p h1 h2
    simp [c]
  have hcn : (c.map (·.1)).Nodup := hmap ▸ hn
  have hmem : ∀ x, x ∈ c ↔ ∃ m, ∃ hm : m < D.sets.length, x = (D.sets[m].id, val m) := by
    intro x
    simp only [c, List.mem_ofFn]
    constructor
    · rintro ⟨⟨m, hm⟩, rfl⟩; exact ⟨m, hm, rfl⟩
    · rintro ⟨m, hm, rfl⟩; exact ⟨⟨m, hm⟩, rfl⟩
  have hidx : ∀ m (hm : m < D.sets.length), c.index D.sets[m].id = some (val m) :=
    fun m hm => index_of_mem hcn ((hmem _).mpr ⟨m, hm, rfl⟩)
  have hsz : ∀ m (hm : m < D.sets.length), setSize D m = D.sets[m].candidates.length := fun m hm => setSize_eq hm
  -- the choice is compatible
  have hcomplete : complete D c = true := by
    simp only [complete, Bool.and_eq_true, beq_iff_eq, List.all_eq_true]
    refine ⟨hmap, fun x hx => ?_⟩
    obtain ⟨m, hm, rfl⟩ := (hmem x).mp hx
    rw [candidate_at hn hm]
    have := hval m hm
    rw [hsz m hm] at this
    simp [List.getElem?_eq_getElem this]
  have hshape : ∀ K ∈ D.couplings, couplingShape D K = true := by
    simp only [supReady, Bool.and_eq_true, List.all_eq_true] at hr
    exact hr.1.1.1.2
  have hcoup : ∀ K ∈ D.couplings, couplingHolds D c K = true := by
    intro K hK
    have hsh := hshape K hK
    simp only [couplingShape, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.any_eq_true,
      beq_iff_eq] at hsh
    have hset : ∀ x ∈ K.sets, ∃ m, ∃ hm : m < D.sets.length, D.sets[m].id = x.1 ∧
        ∀ a ∈ D.sets[m].candidates, (labelOf a K.axis).isSome = true := by
      intro x hx
      obtain ⟨R, hR, ⟨⟨hid, _⟩, hlab⟩⟩ := hsh.2 x hx
      obtain ⟨m, hm, rfl⟩ := mem_sets_getElem hR
      exact ⟨m, hm, hid, hlab⟩
    simp only [couplingHolds, List.all_eq_true]
    rintro ⟨x, y⟩ hxy
    obtain ⟨hx, hy⟩ := List.of_mem_zip hxy
    have hy' : y ∈ K.sets := List.mem_of_mem_tail hy
    obtain ⟨m, hm, hidm, hlm⟩ := hset x hx
    obtain ⟨m', hm', hidm', hlm'⟩ := hset y hy'
    have hvm := hval m hm
    have hvm' := hval m' hm'
    rw [hsz m hm] at hvm
    rw [hsz m' hm'] at hvm'
    obtain ⟨l, hl⟩ := Option.isSome_iff_exists.mp (hlm _ (List.getElem_mem hvm))
    obtain ⟨l', hl'⟩ := Option.isSome_iff_exists.mp (hlm' _ (List.getElem_mem hvm'))
    simp only [← hidm, ← hidm', hidx m hm, hidx m' hm', candidate_at hn hm, candidate_at hn hm',
      List.getElem?_eq_getElem hvm, List.getElem?_eq_getElem hvm', Option.bind_some, hl, hl', beq_iff_eq]
    refine Classical.byContradiction fun hne => ?_
    let body := (K.sets.zip K.sets.tail).flatMap (fun (x, y) =>
      match D.sets.find? (·.id == x.1), D.sets.find? (·.id == y.1) with
      | some R, some R' => (List.range R.candidates.length).flatMap (fun i => (List.range R'.candidates.length).filterMap (fun j =>
          if (R.candidates[i]?.bind (labelOf · K.axis)) != (R'.candidates[j]?.bind (labelOf · K.axis))
          then some (VE.Formula.not (.and (choiceAtom D R.id i) (choiceAtom D R'.id j))) else none))
      | _, _ => [])
    have hf : VE.Formula.not (.and (choiceAtom D D.sets[m].id (val m)) (choiceAtom D D.sets[m'].id (val m'))) ∈ body := by
      simp only [body, List.mem_flatMap]
      refine ⟨(x, y), hxy, ?_⟩
      simp only [← hidm, ← hidm', find_of_nodup hn hm, find_of_nodup hn hm', List.mem_flatMap, List.mem_range,
        List.mem_filterMap]
      refine ⟨val m, hvm, val m', hvm', ?_⟩
      simp only [List.getElem?_eq_getElem hvm, List.getElem?_eq_getElem hvm', Option.bind_some, hl, hl', bne_iff_ne,
        ne_eq, Option.some.injEq]
      rw [if_pos hne]
    have hin : ("coupling:" ++ K.id, conj body) ∈ couplingPremises D := by
      simp only [couplingPremises, List.mem_filterMap]
      refine ⟨K, hK, ?_⟩
      show (if body.isEmpty then none else some ("coupling:" ++ K.id, conj body)) = _
      rw [isEmpty_false_of_mem hf]
      rfl
    have := (conj_denote B [] body).mp (sat_of_mem_labelled hcp hin) _ hf
    exact this ⟨(hatom m hm (val m) (hval m hm)).mpr rfl, (hatom m' hm' (val m') (hval m' hm')).mpr rfl⟩
  have hnar : ∀ N ∈ D.narrowings, narrowingHolds D c N = true := by
    intro N hN
    unfold narrowingHolds
    split
    · rename_i R hR
      obtain ⟨m, hm, rfl⟩ := mem_sets_getElem (List.mem_of_find?_eq_some hR)
      rw [hidx m hm]
      have hvm := hval m hm
      rw [hsz m hm] at hvm
      simp only [List.getElem?_eq_getElem hvm, Option.map_some, Option.getD_some]
      refine Classical.byContradiction fun hk => ?_
      have hk' : N.keeps.contains D.sets[m].candidates[val m].id = false := by simpa using hk
      let dropped := (List.range D.sets[m].candidates.length).filter (fun i =>
        !((D.sets[m].candidates[i]?.map (fun a => N.keeps.contains a.id)).getD true))
      have hd : val m ∈ dropped := by
        simp only [dropped, List.mem_filter, List.mem_range, List.getElem?_eq_getElem hvm, Option.map_some,
          Option.getD_some, hk', Bool.not_false, and_true]
        exact hvm
      have hin : ("narrowing:" ++ N.id, conj (dropped.map (fun i => .not (choiceAtom D D.sets[m].id i)))) ∈
          narrowingPremises D := by
        simp only [narrowingPremises, List.mem_filterMap]
        refine ⟨N, hN, ?_⟩
        rw [hR]
        show (if dropped.isEmpty then none else _) = _
        rw [isEmpty_false_of_mem hd]
        rfl
      have := (conj_denote B [] _).mp (sat_of_mem_labelled hnp hin) _ (List.mem_map.mpr ⟨val m, hd, rfl⟩)
      exact this ((hatom m hm (val m) (hval m hm)).mpr rfl)
    · rfl
  have hcompat : Compatible D c := by
    simp only [Compatible, compatible, Bool.and_eq_true, List.all_eq_true]
    exact ⟨⟨hcomplete, hcoup⟩, hnar⟩
  -- the choice is encoded
  have henc : Encodes D c B := by
    intro R hR i hi
    obtain ⟨m, hm, rfl⟩ := mem_sets_getElem hR
    rw [hatom m hm i (by rw [hsz m hm]; exact hi), hmem]
    constructor
    · rintro rfl; exact ⟨m, hm, rfl⟩
    · rintro ⟨m', hm', he⟩
      simp only [Prod.mk.injEq] at he
      have := ids_inj hn hm hm' he.1
      subst this
      exact he.2
  refine ⟨c, hcompat, henc, fun c' hc' he' => ?_⟩
  have hmap' := complete_map hc'
  have hlen' : c'.length = D.sets.length := by simpa using congrArg List.length hmap'
  apply List.ext_getElem (by rw [hlen, hlen'])
  intro p h1 h2
  have hp : p < D.sets.length := hlen' ▸ h1
  have hfst : c'[p].1 = D.sets[p].id := by
    have := congrArg (·[p]?) hmap'
    simpa [List.getElem?_eq_getElem h1, List.getElem?_eq_getElem hp] using this
  have hx : c'[p] ∈ c' := List.getElem_mem h1
  obtain ⟨m, hf, hi⟩ := candidate_isSome (complete_mem hc' hx)
  rw [hfst, findIdx_of_nodup hn hp] at hf
  cases hf
  have hin := (he' D.sets[p] (List.getElem_mem hp) c'[p].2 (by rw [← hsz p hp]; exact hi)).mpr
    (by rw [← hfst]; exact hx)
  rw [hatom p hp _ hi] at hin
  simp only [c, List.getElem_ofFn]
  rw [← hin]
  exact Prod.ext (by simpa using hfst) rfl

/-! ## Bit names -/

theorem digit_char (n : Nat) (h : n < 10) :
    (Nat.digitChar n ≥ '0' && Nat.digitChar n ≤ '9') = true ∧ (Nat.digitChar n).toNat - 48 = n := by
  match n with
  | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 => decide
  | n + 10 => omega

theorem toDigitsCore_valid (fuel n : Nat) (ds : List Char) (h : ds.all (fun c => c ≥ '0' && c ≤ '9') = true) :
    (Nat.toDigitsCore 10 fuel n ds).all (fun c => c ≥ '0' && c ≤ '9') = true := by
  induction fuel generalizing n ds with
  | zero => exact h
  | succ fuel ih =>
    have hd := (digit_char (n % 10) (Nat.mod_lt _ (by decide))).1
    simp only [Nat.toDigitsCore]
    split
    · simp [hd, h]
    · exact ih _ _ (by simp [hd, h])

theorem toDigitsCore_value (fuel n : Nat) (ds : List Char) (h : n < fuel) :
    (Nat.toDigitsCore 10 fuel n ds).foldl (fun v c => 10 * v + (c.toNat - 48)) 0 =
      ds.foldl (fun v c => 10 * v + (c.toNat - 48)) n := by
  induction fuel generalizing n ds with
  | zero => omega
  | succ fuel ih =>
    have hd := (digit_char (n % 10) (Nat.mod_lt _ (by decide))).2
    simp only [Nat.toDigitsCore]
    split
    next =>
      simp only [List.foldl_cons, Nat.mul_zero, Nat.zero_add, hd]
      have : n % 10 = n := by omega
      rw [this]
    next =>
      rw [ih (n / 10) _ (by omega)]
      simp only [List.foldl_cons, hd]
      congr 1
      omega

theorem toString_data (n : Nat) : (toString n).data = Nat.toDigits 10 n := rfl

theorem digits_ne (n : Nat) : ∀ c ∈ Nat.toDigits 10 n, c ≠ '_' := by
  have hv := toDigitsCore_valid (n + 1) n [] (by rfl)
  intro c hc
  have := List.all_eq_true.mp hv c hc
  simp only [Bool.and_eq_true, decide_eq_true_eq] at this
  intro he; subst he
  exact absurd this.2 (by decide)

theorem split_underscore : ∀ (a a' b b' : List Char), (∀ c ∈ a, c ≠ '_') → (∀ c ∈ a', c ≠ '_') →
    a ++ '_' :: b = a' ++ '_' :: b' → a = a' ∧ b = b'
  | [], [], b, b', _, _, h => by simpa using h
  | [], c :: a', b, b', _, h', h => by
    simp at h; exact absurd h.1.symm (h' c (by simp))
  | c :: a, [], b, b', ha, _, h => by
    simp at h; exact absurd h.1 (ha c (by simp))
  | c :: a, c' :: a', b, b', ha, ha', h => by
    simp only [List.cons_append, List.cons.injEq] at h
    obtain ⟨h1, h2⟩ := split_underscore a a' b b' (fun x hx => ha x (by simp [hx]))
      (fun x hx => ha' x (by simp [hx])) h.2
    exact ⟨by rw [h.1, h1], h2⟩

theorem toDigits_inj {n m : Nat} (h : Nat.toDigits 10 n = Nat.toDigits 10 m) : n = m := by
  have hn := toDigitsCore_value (n+1) n [] (by omega)
  have hm := toDigitsCore_value (m+1) m [] (by omega)
  simp only [List.foldl_nil] at hn hm
  rw [← hn, ← hm]
  exact congrArg (List.foldl (fun v c => 10 * v + (c.toNat - 48)) 0) h

theorem bitName_inj {n j n' j' : Nat} (h : bitName n j = bitName n' j') : n = n' ∧ j = j' := by
  have := congrArg String.toList h
  simp only [bitName, String.toList, String.data_append, toString_data, List.append_assoc] at this
  have h2 := List.append_cancel_left this
  obtain ⟨h3, h4⟩ := split_underscore _ _ _ _ (digits_ne n) (digits_ne n') h2
  have h5 : Nat.toDigits 10 j = Nat.toDigits 10 j' := List.append_cancel_left h4
  exact ⟨toDigits_inj h3, toDigits_inj h5⟩

/-! ## Dead readings and unsatisfiable readings (1.9) -/

theorem term_relation_congr (S : VE.Structure.{u}) (R : String → List S.Carrier → Prop) (ρ : VE.Valuation S)
    (t : VE.Term) : t.denote { S with relation := R } ρ = t.denote S ρ := by
  cases t <;> rfl

/-- Two structures that differ only off the declared signatures agree on every typed formula. -/
theorem denote_relation_congr (E : VE.Environment) (S : VE.Structure.{u}) (R : String → List S.Carrier → Prop)
    (hR : ∀ p ss, E.predicates p = some ss → ∀ vs : List S.Carrier, vs.length = ss.length →
      (S.relation p vs ↔ R p vs)) :
    ∀ (φ : VE.Formula) (Γ : List String) (ρ : VE.Valuation S), φ.check E Γ = true →
      (φ.denote S ρ ↔ φ.denote { S with relation := R } ρ)
  | .top, _, _, _ => Iff.rfl
  | .bottom, _, _, _ => Iff.rfl
  | .unary p t, Γ, ρ, hc => by
    simp only [VE.Formula.check] at hc
    split at hc
    · rename_i s _ hp _
      simp only [VE.Formula.denote, term_relation_congr]
      exact exists_congr fun v => and_congr_right fun _ => hR p [s] hp [v] rfl
    · cases hc
  | .binary p t t', Γ, ρ, hc => by
    simp only [VE.Formula.check] at hc
    split at hc
    · rename_i s r _ _ hp _ _
      simp only [VE.Formula.denote, term_relation_congr]
      exact exists_congr fun v => exists_congr fun w => and_congr_right fun _ => and_congr_right fun _ =>
        hR p [s, r] hp [v, w] rfl
    · cases hc
  | .eq t t', _, ρ, _ => by simp only [VE.Formula.denote, term_relation_congr]
  | .not a, Γ, ρ, hc => not_congr (denote_relation_congr E S R hR a Γ ρ hc)
  | .and a b, Γ, ρ, hc => by
    simp only [VE.Formula.check, Bool.and_eq_true] at hc
    exact and_congr (denote_relation_congr E S R hR a Γ ρ hc.1) (denote_relation_congr E S R hR b Γ ρ hc.2)
  | .or a b, Γ, ρ, hc => by
    simp only [VE.Formula.check, Bool.and_eq_true] at hc
    exact or_congr (denote_relation_congr E S R hR a Γ ρ hc.1) (denote_relation_congr E S R hR b Γ ρ hc.2)
  | .implies a b, Γ, ρ, hc => by
    simp only [VE.Formula.check, Bool.and_eq_true] at hc
    exact imp_congr (denote_relation_congr E S R hR a Γ ρ hc.1) (denote_relation_congr E S R hR b Γ ρ hc.2)
  | .all s a, Γ, ρ, hc => by
    simp only [VE.Formula.check, Bool.and_eq_true] at hc
    exact forall_congr' fun v => imp_congr_right fun _ => denote_relation_congr E S R hR a (s :: Γ) (v :: ρ) hc.2
  | .ex s a, Γ, ρ, hc => by
    simp only [VE.Formula.check, Bool.and_eq_true] at hc
    exact exists_congr fun v => and_congr_right fun _ => denote_relation_congr E S R hR a (s :: Γ) (v :: ρ) hc.2

theorem mem_of_index {c : Choice} {s : String} {i : Nat} (h : c.index s = some i) : (s, i) ∈ c := by
  simp only [Choice.index, Option.map_eq_some_iff] at h
  obtain ⟨x, hx, rfl⟩ := h
  have hm := List.mem_of_find?_eq_some hx
  have he : x.1 = s := by simpa using List.find?_some hx
  rw [← he]
  exact hm

/-- A compatible choice read as a structure of the bits alone: one element, every constant at it, the positive
    bit literals exactly the chosen indices' bits. -/
theorem core_model (D : Doc) (hr : supReady D = true) (E : VE.Environment) (c : Choice) (hc : Compatible D c) :
    ∃ S : VE.Structure.{0}, S.Admissible E ∧
      (∀ a ∈ choiceCore D, a.check E [] = true → a.denote S []) ∧
      (∀ s i, (choiceAtom D s i).check E [] = true → ((choiceAtom D s i).denote S [] ↔ (s, i) ∈ c)) := by
  have hn := supReady_nodup hr
  have hcm : complete D c = true := by
    simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
  have hcoup : ∀ K ∈ D.couplings, couplingHolds D c K = true := by
    simp only [Compatible, compatible, Bool.and_eq_true, List.all_eq_true] at hc; exact hc.1.2
  have hnar : ∀ N ∈ D.narrowings, narrowingHolds D c N = true := by
    simp only [Compatible, compatible, Bool.and_eq_true, List.all_eq_true] at hc; exact hc.2
  have hmap := complete_map hcm
  have hcn : (c.map (·.1)).Nodup := hmap ▸ hn
  let chosen : Nat → Nat := fun m => (c.index ((D.sets[m]?.map (·.id)).getD "")).getD 0
  have hlen : c.length = D.sets.length := by simpa using congrArg List.length hmap
  have hchosen : ∀ m (hm : m < D.sets.length), c.index D.sets[m].id = some (chosen m) ∧ chosen m < setSize D m := by
    intro m hm
    have hcm' : m < c.length := hlen ▸ hm
    have hfst : c[m].1 = D.sets[m].id := by
      have := congrArg (·[m]?) hmap
      simpa [List.getElem?_eq_getElem hcm', List.getElem?_eq_getElem hm] using this
    have hidx := index_of_mem hcn (List.getElem_mem hcm')
    rw [hfst] at hidx
    have hch : chosen m = c[m].2 := by simp [chosen, List.getElem?_eq_getElem hm, hidx]
    refine ⟨by rw [hidx, hch], ?_⟩
    obtain ⟨m', hf, hi⟩ := candidate_isSome (complete_mem hcm (List.getElem_mem hcm'))
    rw [hfst, findIdx_of_nodup hn hm] at hf
    cases hf
    rw [hch]; exact hi
  let on : String → Prop := fun p => ∃ m j, m < D.sets.length ∧ p = bitName (m + 1) j ∧ (chosen m).testBit j = true
  let S : VE.Structure.{0} :=
    ⟨Unit, fun _ _ => True, fun _ => some (), fun p vs => (∃ σ, E.predicates p = some [σ]) ∧ vs = [()] ∧ on p⟩
  let R' : String → List Unit → Prop := fun p vs => vs = [()] ∧ on p
  have htr : ∀ φ : VE.Formula, φ.check E [] = true → (φ.denote S [] ↔ φ.denote { S with relation := R' } []) := by
    intro φ hφ
    refine denote_relation_congr E S R' (fun p ss hp vs hl => ?_) φ [] [] hφ
    show ((∃ σ, E.predicates p = some [σ]) ∧ vs = [()] ∧ on p) ↔ (vs = [()] ∧ on p)
    constructor
    · exact fun h => h.2
    · rintro ⟨rfl, ho⟩
      match ss, hl with
      | [σ], _ => exact ⟨⟨σ, hp⟩, rfl, ho⟩
  let S' : VE.Structure.{0} := { S with relation := R' }
  have hbit : ∀ m (hm : m < D.sets.length) j, bitOn S' (m + 1) j ↔ (chosen m).testBit j = true := by
    intro m hm j
    show (∃ v, some () = some v ∧ (v :: [] = [()] ∧ on (bitName (m + 1) j))) ↔ _
    constructor
    · rintro ⟨_, _, _, m', j', hm', he, hb⟩
      obtain ⟨h1, h2⟩ := bitName_inj he
      have : m = m' := by omega
      subst this; subst h2; exact hb
    · intro hb; exact ⟨(), rfl, rfl, m, j, hm, rfl, hb⟩
  have hpat : ∀ m (hm : m < D.sets.length) i, i < 2 ^ bitsOf (setSize D m) →
      ((pattern (m + 1) (setSize D m) i).denote S' [] ↔ i = chosen m) := by
    intro m hm i hi
    have hk := le_two_pow_bitsOf (setSize D m)
    have hcl := (hchosen m hm).2
    rw [pattern_denote]
    constructor
    · intro h
      apply eq_of_low_bits hi (by omega)
      intro j hj
      have := (hbit m hm j).symm.trans (h j hj)
      cases h1 : i.testBit j <;> cases h2 : (chosen m).testBit j <;> simp_all
    · rintro rfl j _
      exact hbit m hm j
  have hatom : ∀ s i, (choiceAtom D s i).denote S' [] ↔ (s, i) ∈ c := by
    intro s i
    constructor
    · intro h
      by_cases hx : ∃ m, D.sets.findIdx? (·.id == s) = some m ∧ i < setSize D m
      · obtain ⟨m, hf, hi⟩ := hx
        obtain ⟨hm, rfl⟩ := findIdx_set hf
        rw [choiceAtom_eq hf hi, hpat m hm i (by have := le_two_pow_bitsOf (setSize D m); omega)] at h
        subst h
        exact mem_of_index (hchosen m hm).1
      · rw [choiceAtom_bottom hx] at h; exact h.elim
    · intro h
      obtain ⟨m, hf, hi⟩ := candidate_isSome (complete_mem hcm h)
      obtain ⟨hm, he⟩ := findIdx_set hf
      simp only at hf hi he
      have := index_of_mem hcn h
      simp only at this
      rw [← he, (hchosen m hm).1] at this
      cases this
      rw [choiceAtom_eq hf hi, hpat m hm _ (by have := le_two_pow_bitsOf (setSize D m); omega)]
  -- the core holds in S'
  have hcore : ∀ a ∈ choiceCore D, a.denote S' [] := by
    intro a ha
    simp only [choiceCore, Labelled.formulas, List.map_append, List.mem_append, List.mem_map] at ha
    rcases ha with (⟨⟨l, a'⟩, hl, rfl⟩ | ⟨⟨l, a'⟩, hl, rfl⟩) | ⟨⟨l, a'⟩, hl, rfl⟩
    · -- one
      simp only [onePremises, List.mem_filterMap, List.mem_range] at hl
      obtain ⟨m, hm, hb⟩ := hl
      rw [List.getElem?_eq_getElem hm] at hb
      simp only [Option.bind_some] at hb
      split at hb
      · cases hb
      · cases hb
        apply (conj_denote S' [] _).mpr
        intro f hf
        obtain ⟨i', hi', rfl⟩ := List.mem_map.mp hf
        simp only [List.mem_filter, List.mem_range, decide_eq_true_eq] at hi'
        intro hp
        rw [← setSize_eq hm] at hi' hp
        have := (hpat m hm i' hi'.1).mp hp
        have := (hchosen m hm).2
        omega
    · -- couplings
      simp only [couplingPremises, List.mem_filterMap] at hl
      obtain ⟨K, hK, hb⟩ := hl
      split at hb
      · cases hb
      · cases hb
        apply (conj_denote S' [] _).mpr
        intro f hf
        simp only [List.mem_flatMap] at hf
        obtain ⟨⟨x, y⟩, hxy, hf⟩ := hf
        split at hf
        · rename_i R R' hR hR'
          simp only [List.mem_flatMap, List.mem_range, List.mem_filterMap] at hf
          obtain ⟨i, hi, j, hj, hf⟩ := hf
          split at hf
          · rename_i hne
            cases hf
            rintro ⟨h1, h2⟩
            have hm1 := (hatom _ _).mp h1
            have hm2 := (hatom _ _).mp h2
            have hx1 : R.id = x.1 := by simpa using List.find?_some hR
            have hy1 : R'.id = y.1 := by simpa using List.find?_some hR'
            have hi1 := index_of_mem hcn hm1
            have hj1 := index_of_mem hcn hm2
            simp only at hi1 hj1
            rw [hx1] at hi1
            rw [hy1] at hj1
            have := List.all_eq_true.mp (hcoup K hK) (x, y) hxy
            simp only [hi1, hj1, candidate, hR, hR', Option.bind_some] at this
            revert this hne
            cases R.candidates[i]?.bind (labelOf · K.axis) <;> cases R'.candidates[j]?.bind (labelOf · K.axis) <;>
              simp
          · cases hf
        · cases hf
    · -- narrowings
      simp only [narrowingPremises, List.mem_filterMap] at hl
      obtain ⟨N, hN, hb⟩ := hl
      cases hR : inForce D N with
      | none => rw [hR] at hb; cases hb
      | some R =>
        rw [hR] at hb
        simp only [Option.bind_some] at hb
        split at hb
        · cases hb
        · cases hb
          apply (conj_denote S' [] _).mpr
          intro f hf
          obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hf
          intro hχ
          have hm1 := index_of_mem hcn ((hatom _ _).mp hχ)
          simp only at hm1
          have := hnar N hN
          simp only [narrowingHolds, hR, hm1] at this
          simp only [List.mem_filter, List.mem_range] at hi
          revert this hi
          cases R.candidates[i]?.map (fun a => N.keeps.contains a.id) <;> simp
          exact fun h _ => h
  refine ⟨S, ⟨fun _ _ _ => ⟨(), rfl, trivial⟩, ?_⟩, fun a ha hc => (htr a hc).mpr (hcore a ha),
    fun s i hc => (htr _ hc).trans (hatom s i)⟩
  rintro p vs ⟨⟨σ, hσ⟩, rfl, _⟩
  exact ⟨[σ], hσ, trivial, trivial⟩

theorem checkCertificate_typed {E : VE.Environment} {P : List VE.Formula} {φ : VE.Formula}
    {cert : VE.Tableau.Certificate} (h : VE.Tableau.checkCertificate E P φ cert = true) :
    (∀ a ∈ P, a.check E [] = true) ∧ φ.check E [] = true := by
  simp only [VE.Tableau.checkCertificate, Bool.and_eq_true, List.all_eq_true] at h
  exact ⟨h.1.1.2, h.1.2⟩

def deadCheck (D : Doc) (s : String) (i : Nat) (cert : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate (envAt (soften (correlate (sup D).1)) 0) (choiceCore D) (.not (choiceAtom D s i)) cert
def unsatCheck (D : Doc) (cert : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate (envAt (soften (correlate (sup D).1)) 0) (choiceCore D) .bottom cert

theorem dead_sound (D : Doc) (hr : supReady D = true) (s : String) (i : Nat) (cert : VE.Tableau.Certificate)
    (hd : deadCheck D s i cert = true) : ∀ c, Compatible D c → (s, i) ∉ c := by
  intro c hc hmem
  obtain ⟨hP, hφ⟩ := checkCertificate_typed hd
  obtain ⟨S, hS, hcore, hatom⟩ := core_model D hr _ c hc
  have := VE.Tableau.checkCertificate_sound.{0} _ _ _ cert hd S hS (fun a ha => hcore a ha (hP a ha))
  exact this ((hatom s i hφ).mpr hmem)

theorem unsat_sound (D : Doc) (hr : supReady D = true) (cert : VE.Tableau.Certificate)
    (hu : unsatCheck D cert = true) : ¬ ∃ c, Compatible D c := by
  rintro ⟨c, hc⟩
  obtain ⟨hP, _⟩ := checkCertificate_typed hu
  obtain ⟨S, hS, hcore, _⟩ := core_model D hr _ c hc
  exact VE.Tableau.checkCertificate_sound.{0} _ _ _ cert hu S hS (fun a ha => hcore a ha (hP a ha))

end VE.Readings
