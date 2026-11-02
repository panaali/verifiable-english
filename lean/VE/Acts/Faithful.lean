import VE.Acts.Decode

/-! Faithfulness of the elaboration (docs/spec/act-phrases.md 6.6, C17): each part means what the source rules mean,
read of the part.

`IntendedActs` is stated over the source tree and the structure read through `readAs`, not over the elaborated tree.
`intended_tracks` carries a predicate of one tree to a predicate of the other when a map tracks their rules; the proof
uses it twice, for a predicate with no parts (`id`) and for part i (rule i of each rule). The two trees' fuels differ,
so `decides_tracks` compares them at their sum. `h0` is needed: FaithfulExamples.lean `ce` is a source that is not well
formed, which `elaborate` accepts, and on which the two sides differ (reviews/dri-decisions-20261102-ap-3dd.md).
-/

namespace VE.Acts
open VE.Norms VE.NormDefaults VE.Route
universe u

/-- `S` with `p` read as `q`. -/
def readAs (p q : String) (S : VE.Structure.{u}) : VE.Structure.{u} :=
  { S with relation := fun r vs => if r = p then S.relation q vs else S.relation r vs }

/-- The source's meaning per the table: part i of `p` means what the source rules on `p` mean, read of `p__i`. -/
def IntendedActs (D : ActsDoc) (S : VE.Structure.{u}) : Prop :=
  ∀ r ∈ D.U.D.T.regulated, ∀ q ∈ partNames D r.name, VE.Norms.IntendedAt D.U.D.T r (readAs r.name q S)

/-! ### What `elaborateMap` leaves -/

theorem elaborateMap_refsOk {D : ActsDoc} {U' : UDoc} {M : SplitMap} (h : elaborateMap D = .ok (U', M)) :
    refsOk D (splitAtoms D) = .ok () := by
  unfold elaborateMap at h
  cases h1 : D.acts.mapM (fun x => readingOf D x.1 x.2) with
  | error e => simp only [h1, bind, Except.bind] at h; cases h
  | ok Rs =>
  simp only [h1, bind, Except.bind] at h
  rw [splits_eq h1] at h
  cases h2 : refsOk D (splitAtoms D) <;> simp only [h2] at h
  · cases h
  · rfl

/-- A guard or carve-out names no split predicate. -/
theorem refsOk_preds {D : ActsDoc} {sa : String → Option (List Atom)} (h : refsOk D sa = .ok ()) {N : Node}
    (hN : N ∈ D.U.D.T.nodes) {φ : VE.Formula} (hφ : φ ∈ N.guard :: N.carveOuts) {q : String} (hq : q ∈ preds φ) :
    sa q = none := by
  unfold refsOk at h
  dsimp only at h
  split at h
  · cases h
  next hn =>
    have := List.find?_eq_none.mp hn N hN
    cases hs : sa q with
    | none => rfl
    | some a =>
      refine absurd ?_ this
      simp only [List.any_eq_true, Option.isSome_iff_exists]
      exact ⟨φ, hφ, q, hq, a, hs⟩

/-- A part name is undeclared in the source, and part names are distinct. -/
theorem namesOk_preds {D : ActsDoc} {M : SplitMap} (h : namesOk D M = .ok ()) :
    (∀ q ∈ M.preds.map (·.1), D.U.D.E.predicates q = none ∧ ∀ r ∈ D.U.D.T.regulated, r.name ≠ q) ∧
    (M.preds.map (·.1)).Nodup := by
  unfold namesOk at h
  dsimp only at h
  split at h
  · cases h
  · cases h
  next hq _ =>
    have hq := List.find?_eq_none.mp hq
    refine ⟨fun q m => ?_, List.nodup_iff_count.mpr fun q => ?_⟩
    · have := hq q m
      simp only [Bool.or_eq_true, decide_eq_true_eq, List.any_eq_true, beq_iff_eq, not_or] at this
      refine ⟨?_, fun r hr e => this.1.1.1.2 ⟨r, hr, e⟩⟩
      cases he : D.U.D.E.predicates q with
      | none => rfl
      | some _ => exact absurd (by simp [he]) this.1.1.1.1
    · by_cases m : q ∈ M.preds.map (·.1)
      · have := hq q m
        simp only [Bool.or_eq_true, decide_eq_true_eq, not_or] at this
        exact Nat.le_of_not_gt this.1.2
      · rw [List.count_eq_zero_of_not_mem m]; exact Nat.zero_le _

theorem inj_of_nodup_map {α β : Type} {f : α → β} :
    ∀ {l : List α}, (l.map f).Nodup → ∀ {x y}, x ∈ l → y ∈ l → f x = f y → x = y
  | [], _, _, _, hx, _, _ => absurd hx List.not_mem_nil
  | a :: l, h, x, y, hx, hy, e => by
    rw [List.map_cons, List.nodup_cons] at h
    simp only [List.mem_cons] at hx hy
    rcases hx with rfl | hx <;> rcases hy with rfl | hy
    · rfl
    · exact absurd (e ▸ List.mem_map_of_mem hy) h.1
    · exact absurd (e.symm ▸ List.mem_map_of_mem hx) h.1
    · exact inj_of_nodup_map h.2 hx hy e

theorem partRule_inj {m n : String} {i : Nat} (h : partRule m i = partRule n i) : m = n := by
  have := congrArg String.toList h
  exact String.ext (by simpa [partRule] using this)

section Parts
variable {D : ActsDoc} {sa : String → Option (List Atom)}

theorem mem_splitReg {r s : Regulated} : s ∈ splitReg D sa r ↔ (partsOf sa r.name = [] ∧ s = r) ∨
    ∃ x ∈ partsOf sa r.name, s = { r with name := partPred r.name x.2, act := some (partAct D.fixed r.role x.1),
                                          permission := r.permission.map (partPred · x.2) } := by
  unfold splitReg
  cases partsOf sa r.name with
  | nil => simp
  | cons y ys =>
    simp only [List.mem_map, reduceCtorEq, false_and, false_or]
    constructor <;> rintro ⟨x, hx, e⟩ <;> exact ⟨x, hx, e.symm⟩

theorem mem_splitNode {N K : Node} : K ∈ splitNode sa N ↔ (partsOf sa N.pred = [] ∧ K = N) ∨
    ∃ x ∈ partsOf sa N.pred, K = { N with name := partRule N.name x.2, pred := partPred N.pred x.2,
                                          over := N.over.map (partRule · x.2) } := by
  unfold splitNode
  cases partsOf sa N.pred with
  | nil => simp
  | cons y ys =>
    simp only [List.mem_map, reduceCtorEq, false_and, false_or]
    constructor <;> rintro ⟨x, hx, e⟩ <;> exact ⟨x, hx, e.symm⟩

theorem part_mem_preds {p : String} (hp : ∃ r ∈ D.U.D.T.regulated, r.name = p) {x : Atom × Nat}
    (hx : x ∈ partsOf sa p) : (partPred p x.2, p, x.2) ∈ (splitMap D sa).preds := by
  obtain ⟨r, hr, rfl⟩ := hp
  exact List.mem_flatMap.mpr ⟨r, hr, List.mem_map.mpr ⟨x, hx, rfl⟩⟩

/-- The names of a regulated `p`: its parts, or `p` when it has none. -/
theorem mem_partNamesIn {p q : String} (hp : ∃ r ∈ D.U.D.T.regulated, r.name = p) :
    q ∈ partNamesIn (splitMap D sa) p ↔ (partsOf sa p = [] ∧ q = p) ∨ ∃ x ∈ partsOf sa p, q = partPred p x.2 := by
  have hf : ∀ y, y ∈ (splitMap D sa).preds.filter (·.2.1 == p) ↔ ∃ x ∈ partsOf sa p, y = (partPred p x.2, p, x.2) := by
    intro y
    simp only [List.mem_filter, beq_iff_eq]
    constructor
    · rintro ⟨hy, rfl⟩
      obtain ⟨r, _, hy⟩ := List.mem_flatMap.mp hy
      obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hy
      exact ⟨x, hx, rfl⟩
    · rintro ⟨x, hx, rfl⟩
      exact ⟨part_mem_preds hp hx, rfl⟩
  unfold partNamesIn
  split
  next h0 =>
    have hn : partsOf sa p = [] := List.eq_nil_iff_forall_not_mem.mpr fun x hx =>
      List.not_mem_nil (h0 ▸ (hf _).mpr ⟨x, hx, rfl⟩)
    simp [hn]
  next h0 =>
    have hn : partsOf sa p ≠ [] := fun e => h0 (List.eq_nil_iff_forall_not_mem.mpr fun y hy => by
      obtain ⟨x, hx, _⟩ := (hf y).mp hy
      simp [e] at hx)
    simp only [List.mem_map, hn, false_and, false_or]
    constructor
    · rintro ⟨y, hy, rfl⟩
      obtain ⟨x, hx, rfl⟩ := (hf y).mp hy
      exact ⟨x, hx, rfl⟩
    · rintro ⟨x, hx, rfl⟩
      exact ⟨_, (hf _).mpr ⟨x, hx, rfl⟩, rfl⟩

end Parts

/-! ### One predicate of `T` tracks one of `T'` -/

theorem catalaValue_congr {P Q P' Q' : Prop} (h : P ↔ P') (k : Q ↔ Q') (d : Bool) :
    catalaValue P Q d = catalaValue P' Q' d := by
  rw [propext h, propext k]

section Tracks
variable {T T' : Tree} {p q : String} {f : Node → Node} {S₁ S₂ : VE.Structure.{u}}
  {ρ₁ : VE.Valuation S₁} {ρ₂ : VE.Valuation S₂}
  (hon : ∀ N ∈ T.nodes, N.pred = p → f N ∈ T'.nodes ∧ (f N).pred = q ∧ (f N).sign = N.sign)
  (honto : ∀ K ∈ T'.nodes, K.pred = q → ∃ N ∈ T.nodes, N.pred = p ∧ K = f N)
  (hover : ∀ N C, (f N).name ∈ (f C).over ↔ N.name ∈ C.over)
  (happ : ∀ N ∈ T.nodes, N.pred = p → (AppliesD S₁ ρ₁ N ↔ AppliesD S₂ ρ₂ (f N)))
include hon honto hover

theorem children_tracks {N : Node} (hN : N ∈ T.nodes) (hp : N.pred = p) {C' : Node} :
    C' ∈ children T' (f N) ↔ ∃ C ∈ children T N, C' = f C := by
  have hq := (hon N hN hp).2.1
  constructor
  · intro hc
    obtain ⟨hC', hpq, ho⟩ := mem_children_iff.mp hc
    obtain ⟨C, hC, hpC, rfl⟩ := honto C' hC' (hpq.trans hq)
    exact ⟨C, mem_children_iff.mpr ⟨hC, hpC.trans hp.symm, (hover N C).mp ho⟩, rfl⟩
  · rintro ⟨C, hc, rfl⟩
    obtain ⟨hC, hpC, ho⟩ := mem_children_iff.mp hc
    have := hon C hC (hpC.trans hp)
    exact mem_children_iff.mpr ⟨this.1, this.2.1.trans hq.symm, (hover N C).mpr ho⟩

include happ

theorem yields_tracks : ∀ (g : Nat) (N : Node), N ∈ T.nodes → N.pred = p →
    (YieldsD T S₁ ρ₁ g N ↔ YieldsD T' S₂ ρ₂ g (f N))
  | 0, N, hN, hp => happ N hN hp
  | g + 1, N, hN, hp => by
    simp only [YieldsD]
    apply or_congr (happ N hN hp)
    constructor
    · rintro ⟨C, hc, hy⟩
      obtain ⟨hC, hpC, _⟩ := mem_children_iff.mp hc
      exact ⟨f C, (children_tracks hon honto hover hN hp).mpr ⟨C, hc, rfl⟩,
        (yields_tracks g C hC (hpC.trans hp)).mp hy⟩
    · rintro ⟨C', hc, hy⟩
      obtain ⟨C, hc', rfl⟩ := (children_tracks hon honto hover hN hp).mp hc
      obtain ⟨hC, hpC, _⟩ := mem_children_iff.mp hc'
      exact ⟨C, hc', (yields_tracks g C hC (hpC.trans hp)).mpr hy⟩

theorem selects_tracks (g : Nat) {N : Node} (hN : N ∈ T.nodes) (hp : N.pred = p) :
    SelectsD T S₁ ρ₁ g N ↔ SelectsD T' S₂ ρ₂ g (f N) := by
  simp only [SelectsD]
  apply and_congr (happ N hN hp)
  apply not_congr
  constructor
  · rintro ⟨C, hc, hy⟩
    obtain ⟨hC, hpC, _⟩ := mem_children_iff.mp hc
    exact ⟨f C, (children_tracks hon honto hover hN hp).mpr ⟨C, hc, rfl⟩,
      (yields_tracks hon honto hover happ g C hC (hpC.trans hp)).mp hy⟩
  · rintro ⟨C', hc, hy⟩
    obtain ⟨C, hc', rfl⟩ := (children_tracks hon honto hover hN hp).mp hc
    obtain ⟨hC, hpC, _⟩ := mem_children_iff.mp hc'
    exact ⟨C, hc', (yields_tracks hon honto hover happ g C hC (hpC.trans hp)).mpr hy⟩

/-- The two trees' fuels differ; both exceed every rule's height, so each rule selects at their sum. -/
theorem decides_tracks (hac : DagAcyclic (precedenceNodes T)) (hac' : DagAcyclic (precedenceNodes T')) (sign : Bool) :
    DecidesD T S₁ ρ₁ p sign ↔ DecidesD T' S₂ ρ₂ q sign := by
  have hs : ∀ {N}, N ∈ T.nodes → N.pred = p →
      (SelectsD T S₁ ρ₁ (fuel T) N ↔ SelectsD T' S₂ ρ₂ (fuel T') (f N)) := fun {N} hN hp => by
    have h1 := belowCount_lt hac hN
    have h2 := belowCount_lt hac' (hon N hN hp).1
    have e1 : fuel T = T.nodes.length := rfl
    have e2 : fuel T' = T'.nodes.length := rfl
    rw [selects_stable hac S₁ ρ₁ (fuel T) (fuel T + fuel T') hN (by omega) (by omega),
      selects_stable hac' S₂ ρ₂ (fuel T') (fuel T + fuel T') (hon N hN hp).1 (by omega) (by omega)]
    exact selects_tracks hon honto hover happ _ hN hp
  simp only [DecidesD, rulesOn, List.mem_filter, beq_iff_eq]
  constructor
  · rintro ⟨N, ⟨hN, hp⟩, hg, hc⟩
    have := hon N hN hp
    exact ⟨f N, ⟨this.1, this.2.1⟩, this.2.2.trans hg, (hs hN hp).mp hc⟩
  · rintro ⟨K, ⟨hK, hq⟩, hg, hc⟩
    obtain ⟨N, hN, hp, rfl⟩ := honto K hK hq
    exact ⟨N, ⟨hN, hp⟩, (hon N hN hp).2.2.symm.trans hg, (hs hN hp).mpr hc⟩

end Tracks

theorem tupleTyped_readAs (p q : String) (S : VE.Structure.{u}) : ∀ (ss : List String) (vs : List S.Carrier),
    VE.TupleTyped (readAs p q S) ss vs ↔ VE.TupleTyped S ss vs
  | [], [] | [], _ :: _ | _ :: _, [] => Iff.rfl
  | s :: ss, v :: vs => by
    simp only [VE.TupleTyped]
    exact and_congr Iff.rfl (tupleTyped_readAs p q S ss vs)

/-- Truth of a typed formula reads only the declared relations it names. -/
theorem denote_preds_congr (S : VE.Structure.{u}) (R R' : String → List S.Carrier → Prop) {E : VE.Environment}
    (a : VE.Formula) (Γ : List String) (ρ : List S.Carrier) (hw : a.WellFormed E Γ)
    (h : ∀ r ∈ preds a, E.predicates r ≠ none → ∀ vs, R r vs ↔ R' r vs) :
    a.denote { S with relation := R } ρ ↔ a.denote { S with relation := R' } ρ := by
  induction a generalizing Γ ρ with
  | unary r t =>
    obtain ⟨_, hr, _⟩ := hw
    simp only [VE.Formula.denote, VE.Term.denote, h r (by simp [preds]) (by simp [hr]) _]
  | binary r t w =>
    obtain ⟨_, _, hr, _⟩ := hw
    simp only [VE.Formula.denote, VE.Term.denote, h r (by simp [preds]) (by simp [hr]) _]
  | eq t w => exact Iff.rfl
  | top | bottom => exact Iff.rfl
  | not a ih => simp only [VE.Formula.denote]; rw [ih Γ ρ hw h]
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    simp only [VE.Formula.denote]
    rw [ia Γ ρ hw.1 fun r hr => h r (by simp [preds, hr]), ib Γ ρ hw.2 fun r hr => h r (by simp [preds, hr])]
  | all t a ih | ex t a ih =>
    simp only [VE.Formula.denote]
    first
    | exact forall_congr' fun v => imp_congr_right fun _ => ih (t :: Γ) (v :: ρ) hw.2 h
    | exact exists_congr fun v => and_congr_right fun _ => ih (t :: Γ) (v :: ρ) hw.2 h

theorem applies_agree {S₁ S₂ : VE.Structure.{u}} {ρ₁ : VE.Valuation S₁} {ρ₂ : VE.Valuation S₂} {N K : Node}
    (hg : K.guard = N.guard) (hc : K.carveOuts = N.carveOuts)
    (h : ∀ φ ∈ N.guard :: N.carveOuts, φ.denote S₁ ρ₁ ↔ φ.denote S₂ ρ₂) : AppliesD S₁ ρ₁ N ↔ AppliesD S₂ ρ₂ K := by
  simp only [AppliesD, hg, hc]
  apply and_congr (h _ List.mem_cons_self)
  apply not_congr
  exact exists_congr fun U => and_congr_right fun hU => h U (List.mem_cons_of_mem _ hU)

/-- `r` of `T`, read as `r'`, means what `r'` means in `T'`, when `f` tracks their rules. -/
theorem intended_tracks {T T' : Tree} {f : Node → Node} (S : VE.Structure.{u}) {r r' : Regulated}
    (hon : ∀ N ∈ T.nodes, N.pred = r.name → f N ∈ T'.nodes ∧ (f N).pred = r'.name ∧ (f N).sign = N.sign)
    (honto : ∀ K ∈ T'.nodes, K.pred = r'.name → ∃ N ∈ T.nodes, N.pred = r.name ∧ K = f N)
    (hover : ∀ N C, (f N).name ∈ (f C).over ↔ N.name ∈ C.over)
    (happ : ∀ ρ : List S.Carrier, ∀ N ∈ T.nodes, N.pred = r.name →
      (AppliesD (forget [r.name] (readAs r.name r'.name S)) ρ N ↔ AppliesD (forget [r'.name] S) ρ (f N)))
    (hac : DagAcyclic (precedenceNodes T)) (hac' : DagAcyclic (precedenceNodes T'))
    (hs : r'.sorts = r.sorts) (hd : r'.allowByDefault = r.allowByDefault) :
    IntendedAt T r (readAs r.name r'.name S) ↔ IntendedAt T' r' S := by
  have key : ∀ vs : List S.Carrier,
      Value T r (forget [r.name] (readAs r.name r'.name S)) vs = Value T' r' (forget [r'.name] S) vs := fun vs => by
    unfold Value
    rw [hd]
    exact catalaValue_congr (decides_tracks hon honto hover (happ _) hac hac' true)
      (decides_tracks hon honto hover (happ _) hac hac' false) _
  have rel : ∀ vs : List S.Carrier, (readAs r.name r'.name S).relation r.name vs ↔ S.relation r'.name vs := fun vs => by
    simp [readAs]
  simp only [IntendedAt, hs]
  constructor
  · intro H vs hv
    obtain ⟨b, hb, hi⟩ := H vs ((tupleTyped_readAs _ _ S _ vs).mpr hv)
    exact ⟨b, (key vs).symm.trans hb, (rel vs).symm.trans hi⟩
  · intro H vs hv
    obtain ⟨b, hb, hi⟩ := H vs ((tupleTyped_readAs _ _ S _ vs).mp hv)
    exact ⟨b, (key vs).trans hb, (rel vs).trans hi⟩

section Source
variable {D : ActsDoc} (h0 : VE.Norms.WellFormed D.U.D = true)
include h0

theorem node_regulated {N : Node} (hN : N ∈ D.U.D.T.nodes) : ∃ r ∈ D.U.D.T.regulated, r.name = N.pred := by
  obtain ⟨_, _, r, hr, _⟩ := ((wellFormed_iff D.U.D).mp h0).1.2.2.2.2.2.2.1.1 N hN
  exact ⟨r, List.mem_of_find?_eq_some hr, by simpa using List.find?_some hr⟩

theorem node_typed {N : Node} (hN : N ∈ D.U.D.T.nodes) {φ : VE.Formula} (hφ : φ ∈ N.guard :: N.carveOuts) :
    ∃ Γ, φ.WellFormed D.U.D.E Γ := by
  obtain ⟨_, _, _, _, ht⟩ := ((wellFormed_iff D.U.D).mp h0).1.2.2.2.2.2.2.1.1 N hN
  exact ⟨_, (VE.check_iff_wellFormed _ _ _).mp (ht φ hφ).2⟩

end Source

/-- Faithfulness: the elaborated document's intended reading is the table's reading of the source. -/
theorem elaborate_faithful (D : ActsDoc) {U' : VE.NormDefaults.UDoc} (h0 : VE.Norms.WellFormed D.U.D = true)
    (h : elaborate D = .ok U') (S : VE.Structure.{u}) : VE.Norms.holdsCatala U'.D.T S ↔ IntendedActs D S := by
  obtain ⟨M, hM⟩ := elaborate_ok h
  have hrefs := elaborateMap_refsOk hM
  obtain ⟨_, hn, rfl, rfl, hwU, _⟩ := elaborateMap_ok hM
  have hnm := namesOk_preds hn
  have hac := (precedence_acyclic _ h0).1
  have hac' := (precedence_acyclic _ (uvalid hwU).wf).1
  have hfresh : ∀ {p x}, (∃ r ∈ D.U.D.T.regulated, r.name = p) → x ∈ partsOf (splitAtoms D) p →
      partPred p x.2 ∈ (splitMap D (splitAtoms D)).preds.map (·.1) := fun hp hx =>
    List.mem_map.mpr ⟨_, part_mem_preds hp hx, rfl⟩
  -- A predicate with no parts: the same rules, the same relations.
  have whole : ∀ r ∈ D.U.D.T.regulated, partsOf (splitAtoms D) r.name = [] →
      (IntendedAt D.U.D.T r (readAs r.name r.name S) ↔
        IntendedAt (splitDoc D (splitAtoms D) (splitMap D (splitAtoms D))).D.T r S) := by
    intro r hr hp
    refine intended_tracks (f := id) S (fun N hN e => ?_) (fun K hK e => ?_) (fun _ _ => Iff.rfl)
      (fun ρ N hN _ => applies_agree rfl rfl fun φ hφ => let ⟨Γ, hw⟩ := node_typed h0 hN hφ
        denote_preds_congr S _ _ φ Γ ρ hw fun t _ _ vs => ?_) hac hac' rfl rfl
    · exact ⟨List.mem_flatMap.mpr ⟨N, hN, mem_splitNode.mpr (.inl ⟨e ▸ hp, rfl⟩)⟩, e, rfl⟩
    · obtain ⟨N, hN, hs⟩ := List.mem_flatMap.mp hK
      rcases mem_splitNode.mp hs with ⟨_, rfl⟩ | ⟨x, hx, rfl⟩
      · exact ⟨K, hN, e, rfl⟩
      · exact absurd e.symm ((hnm.1 _ (hfresh (node_regulated h0 hN) hx)).2 r hr)
    · by_cases ht : t = r.name <;> simp [ht, forget, readAs]
  -- Part i of a predicate: rule i of each rule, and the guards name neither the source nor the part.
  have part : ∀ r ∈ D.U.D.T.regulated, ∀ x ∈ partsOf (splitAtoms D) r.name, ∀ r' : Regulated,
      r'.name = partPred r.name x.2 → r'.sorts = r.sorts → r'.allowByDefault = r.allowByDefault →
      (IntendedAt D.U.D.T r (readAs r.name r'.name S) ↔
        IntendedAt (splitDoc D (splitAtoms D) (splitMap D (splitAtoms D))).D.T r' S) := by
    intro r hr x hx r' hq hs hd
    have hreg : ∃ t ∈ D.U.D.T.regulated, t.name = r.name := ⟨r, hr, rfl⟩
    have hsome : splitAtoms D r.name ≠ none := fun e => by simp [partsOf, e] at hx
    have hq' := hnm.1 _ (hfresh hreg hx)
    refine intended_tracks
      (f := fun N => { N with name := partRule N.name x.2, pred := partPred N.pred x.2,
                              over := N.over.map (partRule · x.2) })
      S (fun N hN e => ?_) (fun K hK e => ?_) (fun N C => ?_)
      (fun ρ N hN _ => applies_agree rfl rfl fun φ hφ => let ⟨Γ, hw⟩ := node_typed h0 hN hφ
        denote_preds_congr S _ _ φ Γ ρ hw fun t ht hdecl vs => ?_) hac hac' hs hd
    · exact ⟨List.mem_flatMap.mpr ⟨N, hN, mem_splitNode.mpr (.inr ⟨x, e ▸ hx, rfl⟩)⟩, by simp [e, hq], rfl⟩
    · rw [hq] at e
      obtain ⟨N, hN, hs⟩ := List.mem_flatMap.mp hK
      rcases mem_splitNode.mp hs with ⟨_, rfl⟩ | ⟨y, hy, rfl⟩
      · obtain ⟨t, ht, et⟩ := node_regulated h0 hN
        exact absurd (et.trans e) (hq'.2 t ht)
      · have := inj_of_nodup_map hnm.2 (part_mem_preds (node_regulated h0 hN) hy) (part_mem_preds hreg hx) e
        simp only [Prod.mk.injEq] at this
        obtain ⟨_, e1, e2⟩ := this
        exact ⟨N, hN, e1, by rw [e2]⟩
    · simp only [List.mem_map]
      constructor
      · rintro ⟨m, hm, e⟩
        exact partRule_inj e ▸ hm
      · exact fun hm => ⟨_, hm, rfl⟩
    · have hne : t ≠ r.name := fun e => hsome (e ▸ refsOk_preds hrefs hN hφ ht)
      have hnq : t ≠ r'.name := fun e => hdecl (by rw [e, hq]; exact hq'.1)
      simp [hne, hnq, forget, readAs]
  have part' := fun r hr x hx => part r hr x hx
    { r with name := partPred r.name x.2, act := some (partAct D.fixed r.role x.1),
             permission := r.permission.map (partPred · x.2) } rfl rfl rfl
  constructor
  · intro H r hr q hq
    rcases (mem_partNamesIn ⟨r, hr, rfl⟩).mp hq with ⟨hp, rfl⟩ | ⟨x, hx, rfl⟩
    · exact (whole r hr hp).mpr (H r (List.mem_flatMap.mpr ⟨r, hr, mem_splitReg.mpr (.inl ⟨hp, rfl⟩)⟩))
    · exact (part' r hr x hx).mpr (H _ (List.mem_flatMap.mpr ⟨r, hr, mem_splitReg.mpr (.inr ⟨x, hx, rfl⟩)⟩))
  · intro H r' hr'
    obtain ⟨r, hr, hs⟩ := List.mem_flatMap.mp hr'
    rcases mem_splitReg.mp hs with ⟨hp, rfl⟩ | ⟨x, hx, rfl⟩
    · exact (whole r' hr hp).mp (H r' hr _ ((mem_partNamesIn ⟨r', hr, rfl⟩).mpr (.inl ⟨hp, rfl⟩)))
    · exact (part' r hr x hx).mp (H r hr _ ((mem_partNamesIn ⟨r, hr, rfl⟩).mpr (.inr ⟨x, hx, rfl⟩)))

/-- `decodeElaboratedU` establishes `h0`, so the claim over every decoded document is unconditional. -/
theorem Decode.decodeElaboratedU_faithful {environment norms : Lean.Json} {e : Decode.ElaboratedU}
    (h : Decode.decodeElaboratedU environment norms = .ok e) (S : VE.Structure.{u}) :
    VE.Norms.holdsCatala e.U'.D.T S ↔ IntendedActs e.D S := by
  have hw : VE.Norms.WellFormed e.D.U.D = true := by
    rw [e.hU, e.s.doc]
    exact e.s.src.wf
  exact elaborate_faithful e.D hw (by simp [elaborate, e.hE, Except.map]) S

end VE.Acts
