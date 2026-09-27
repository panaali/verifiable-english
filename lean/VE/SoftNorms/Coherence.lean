import VE.SoftNorms.Semantics

/-! Decision assignments, coherence and what CONFLICT-FREE means
(docs/spec/soft-norms.md 6, 9.3).

`Exc_T`, `Coh_T` and `Soft_T` are generated in `Soften.lean`; here are
`Background_base′`, `BaseAdmissible′` and the conditional contract.

The key tool is `canon`: over a base structure `B` every layer symbol of `T′` is
interpreted by its substituted meaning. It needs no conflict-freedom (at a
conflict point it is simply one of the two readings), and on typed valuations
`φ°` in `B` is `φ` in `canon B` (`canon_subst`). Through it every base conflict
formula of `T′` becomes a statement about the direct semantics, and
`soft_conflict_decomposition` is proved from `hard_over_soft`,
`weighing_points_complete` and the coherence premises. -/
namespace VE.SoftNorms
open VE.Norms
open VE.Route (Unique)
universe u

/-! ## 6.1 -/

def backgroundBase' (D : SoftDoc) : List VE.Formula := VE.Norms.backgroundBase (soften D) ++ softPremises D
def background' (D : SoftDoc) : List VE.Formula := VE.Norms.background (soften D) ++ softPremises D

def BaseAdmissible' (D : SoftDoc) (B : VE.Structure.{u}) : Prop :=
  VE.Norms.BaseAdmissible (soften D) B ∧ Sat B (softPremises D)

def PrefixAdmissible' (D : SoftDoc) (k : Nat) (S : VE.Structure.{u}) : Prop :=
  VE.Norms.PrefixAdmissible (soften D) k S ∧ Sat (restrictAll (soften D).T S) (softPremises D)

/-! ## 6.3 -/

def NoStrictCollision (D : SoftDoc) (B : VE.Structure.{u}) : Prop :=
  ∀ r ∈ D.T.regulated, ∀ vs, VE.TupleTyped B r.sorts vs →
    ¬ ((subst (soften D).T (size (soften D)) (.and (strictPos D r.name) (strictNeg D r.name))).denote B (tupleVal vs))

def NoHardPairConflict (D : SoftDoc) (B : VE.Structure.{u}) : Prop :=
  ∀ pr ∈ pairs (soften D).T, ∀ vs, VE.TupleTyped B pr.sorts vs →
    ¬ ((pairConflict (soften D) pr).denote B (tupleVal vs) ∧
       ¬ (subst (soften D).T (size (soften D)) (.and (defaultPos D pr.req) (defaultNeg D pr.perm))).denote B
          (tupleVal vs))

def SoftConflictFree (D : SoftDoc) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissible' D B → VE.Norms.ConflictFree (soften D) B

/-! ## The canonical interpretation of the layer symbols -/

/-- Every layer symbol read as its substituted meaning over `B`. -/
def canon (Dd : Doc) (B : VE.Structure.{u}) : VE.Structure.{u} :=
  { B with relation := fun n vs => match expTable Dd.T (size Dd) n with
      | some F => F.denote B (tupleVal vs)
      | none => B.relation n vs }

section Canon
variable {Dd : Doc} (hv : Valid Dd) (B : VE.Structure.{u})
include hv

omit hv in
theorem canon_off' {n : String} (h : expTable Dd.T (size Dd) n = none) (vs : List B.Carrier) :
    (canon Dd B).relation n vs ↔ B.relation n vs := by
  simp [canon, h]

omit hv in
theorem canon_off {n : String} (hn : n ∉ layerNames Dd.T) (vs : List B.Carrier) :
    (canon Dd B).relation n vs ↔ B.relation n vs := by
  have : expTable Dd.T (size Dd) n = none := by
    apply expTable_none
    rw [List.take_of_length_le (by simp [size, layerNames])]
    exact hn
  simp [canon, this]

omit hv in
theorem canon_base (φ : VE.Formula) (Γ : List String) (hφ : φ.WellFormed (envAt Dd 0) Γ)
    (ρ : VE.Valuation B) : φ.denote (canon Dd B) ρ ↔ φ.denote B ρ :=
  denote_relation_congr (ns := layerNames Dd.T) (fun _ hr => envAt_zero_later hr) B _
    (fun _ vs hr => canon_off B hr vs) φ Γ ρ hφ

theorem canon_agrees (hc : ConstantsTyped Dd B) : ∀ k, AgreesBelow Dd k (canon Dd B) := by
  suffices h : ∀ j (q : Sym), (syms Dd.T)[j]? = some q → ∀ vs, VE.TupleTyped (canon Dd B) q.sorts vs →
      ((canon Dd B).relation q.name vs ↔ (q.meaning Dd.T).denote (canon Dd B) (tupleVal vs)) from
    fun k j q _ hq => h j q hq
  intro j
  induction j using Nat.strongRecOn with
  | ind j ih =>
    intro q hq vs hvs
    have hj : j < size Dd := (List.getElem?_eq_some_iff.mp hq).1
    have hvs' : VE.TupleTyped B q.sorts vs := (tupleTyped_relation B _ _ vs).mp hvs
    have hrel : (canon Dd B).relation q.name vs ↔
        (substWith (expTable Dd.T j) (q.meaning Dd.T)).denote B (tupleVal vs) := by
      simp only [canon, expTable_at hv (size Dd) j q hj hq]
    rw [hrel]
    have hsub := subst_wellFormed hv j (q.meaning Dd.T) _ (meaning_wellFormed hv hq)
    show (subst Dd.T j (q.meaning Dd.T)).denote B (tupleVal vs) ↔ _
    rw [← canon_base B _ _ hsub]
    exact subst_denote hv j (canon Dd B) hc (fun j' q' hj' hq' => ih j' hj' q' hq') _ _
      (meaning_wellFormed hv hq) _ (tupleVal_typed _ _ vs hvs)

/-- `φ°` in `B` is `φ` in `canon B`, on typed valuations. -/
theorem canon_subst (hc : ConstantsTyped Dd B) (k : Nat) (φ : VE.Formula) (Γ : List String)
    (hφ : φ.WellFormed (envAt Dd k) Γ) (ρ : VE.Valuation B) (hρ : VE.Valuation.Typed B Γ ρ) :
    (subst Dd.T k φ).denote B ρ ↔ φ.denote (canon Dd B) ρ :=
  (canon_base B _ Γ (subst_wellFormed hv k φ Γ hφ) ρ).symm.trans
    (subst_denote hv k (canon Dd B) hc (canon_agrees hv B hc k) φ Γ hφ ρ hρ)

end Canon

/-! ## Decisions at the canonical interpretation -/

section AtCanon
variable (D : SoftDoc) (S : VE.Structure.{u}) (ρ : VE.Valuation S)

theorem defaultDecides_denote (p : String) (sign : Bool) :
    (defaultDecidesF D p sign).denote S ρ ↔ DefaultDecidesD D S ρ p sign := by
  simp only [defaultDecidesF, anyF_denote, List.mem_map, List.mem_filter, beq_iff_eq, DefaultDecidesD]
  constructor
  · rintro ⟨_, ⟨N, ⟨⟨hN, hd⟩, hs⟩, rfl⟩, h⟩
    refine ⟨N, hN, hd, hs, ?_⟩
    rw [selects', selects_denote, fuel_soften] at h
    exact (selectsD_prime D S ρ _ N).mp h
  · rintro ⟨N, hN, hd, hs, h⟩
    refine ⟨_, ⟨N, ⟨⟨hN, hd⟩, hs⟩, rfl⟩, ?_⟩
    rw [selects', selects_denote, fuel_soften]
    exact (selectsD_prime D S ρ _ N).mpr h

theorem selects'_denote (N : SoftNode) : (selects' D N).denote S ρ ↔ SelectsSoftD D S ρ (fuel D) N := by
  rw [selects', selects_denote, fuel_soften]
  exact selectsD_prime D S ρ _ N

end AtCanon

section Split
variable {D : SoftDoc} (hv : SoftValid D) {S : VE.Structure.{u}} {ρ : VE.Valuation S}
include hv

theorem child_strict {N C : SoftNode} (hN : N ∈ D.T.nodes) (hs : N.mode = .strict) (hC : C ∈ children D N) :
    C.mode = .strict := by
  obtain ⟨hC, _, hover⟩ := mem_childrenIn_iff.mp hC
  cases hm : C.mode
  · rfl
  · have := hv.softOverHard C hC hm N.name hover N
      (find_key (fun N : SoftNode => N.name) _ hv.names N hN)
    rw [hs] at this; cases this

theorem yields_strict : ∀ (f : Nat) (N : SoftNode), N ∈ D.T.nodes → N.mode = .strict →
    (YieldsSoftD D S ρ f N ↔ StrictYieldsD D S ρ f N)
  | 0, N, _, hs => by simp [YieldsSoftD, StrictYieldsD, AppliesSoftD, hs]
  | f + 1, N, hN, hs => by
    simp only [YieldsSoftD, StrictYieldsD, AppliesSoftD, hs, true_and]
    apply or_congr_right
    constructor
    · rintro ⟨C, hC, hy⟩
      exact ⟨C, hC, (yields_strict f C (mem_childrenIn_iff.mp hC).1 (child_strict hv hN hs hC)).mp hy⟩
    · rintro ⟨C, hC, hy⟩
      exact ⟨C, hC, (yields_strict f C (mem_childrenIn_iff.mp hC).1 (child_strict hv hN hs hC)).mpr hy⟩

theorem selects_strict (f : Nat) (N : SoftNode) (hN : N ∈ D.T.nodes) (hs : N.mode = .strict) :
    SelectsSoftD D S ρ f N ↔ StrictSelectsD D S ρ f N := by
  simp only [SelectsSoftD, StrictSelectsD, AppliesSoftD, hs, true_and]
  apply and_congr_right
  intro _
  apply not_congr
  constructor
  · rintro ⟨C, hC, hy⟩
    exact ⟨C, hC, (yields_strict hv f C (mem_childrenIn_iff.mp hC).1 (child_strict hv hN hs hC)).mp hy⟩
  · rintro ⟨C, hC, hy⟩
    exact ⟨C, hC, (yields_strict hv f C (mem_childrenIn_iff.mp hC).1 (child_strict hv hN hs hC)).mpr hy⟩

/-- A predicate is decided by a strict rule or by a default rule. -/
theorem decides_split (p : String) (sign : Bool) :
    DecidesSoftD D S ρ p sign ↔ StrictDecidesD D S ρ p sign ∨ DefaultDecidesD D S ρ p sign := by
  constructor
  · rintro ⟨N, hN, hs, h⟩
    cases hm : N.mode
    · exact Or.inl ⟨N, hN, hs, (selects_strict hv _ N (mem_rulesOn.mp hN).1 hm).mp h⟩
    · exact Or.inr ⟨N, hN, hm, hs, h⟩
  · rintro (⟨N, hN, hs, h⟩ | ⟨N, hN, _, hs, h⟩)
    · exact ⟨N, hN, hs, (selects_strict hv _ N (mem_rulesOn.mp hN).1 h.1).mpr h⟩
    · exact ⟨N, hN, hs, h⟩

theorem sortsOf_reg {r : Regulated} (hr : r ∈ D.T.regulated) : sortsOf D r.name = r.sorts := by
  unfold sortsOf sortsIn
  rw [find_key Regulated.name _ hv.regNames r hr]
  rfl

theorem reg_of_node {N : SoftNode} (hN : N ∈ D.T.nodes) :
    ∃ r ∈ D.T.regulated, r.name = N.pred ∧ r.sorts = sortsOf D N.pred := by
  obtain ⟨r, hr, hn⟩ := List.mem_map.mp (hv.predReg N hN)
  exact ⟨r, hr, hn, by rw [← hn, sortsOf_reg hv hr]⟩

theorem pair_regs {pr : Pair} (hpr : pr ∈ pairs D.base.T) :
    (∃ r ∈ D.T.regulated, r.name = pr.req ∧ r.sorts = pr.sorts) ∧
    (∃ m ∈ D.T.regulated, m.name = pr.perm ∧ m.sorts = pr.sorts) := by
  have hv' := valid_of_wellFormed _ hv.wf
  obtain ⟨_, ⟨r, hr, hrn, hrs⟩, ⟨m, hm, hmn, hms⟩⟩ := hv'.pairs pr hpr
  exact ⟨⟨r, mem_syms_reg hr, hrn, hrs⟩, ⟨m, mem_syms_reg hm, hmn, hms⟩⟩

end Split

/-! ## The decomposition -/

section Decomposition
variable {D : SoftDoc} (hv : SoftValid D) (B : VE.Structure.{u}) (hB : VE.Norms.BaseAdmissible (soften D) B)
include hv hB

theorem conflict_canon {r : Regulated} (hr : r ∈ D.T.regulated) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B r.sorts vs) :
    (conflict (soften D) r).denote B (tupleVal vs) ↔
      DecidesSoftD D (canon (soften D) B) (tupleVal vs) r.name true ∧
        DecidesSoftD D (canon (soften D) B) (tupleVal vs) r.name false := by
  have hv' := valid_of_wellFormed _ hv.wf
  have hk := index_before hv' hr
  have hT := rulesTyped_of_valid hv' hk
  have hρ := tupleVal_typed B _ vs hvs
  simp only [conflict, pos, neg, VE.Formula.denote]
  rw [canon_subst hv' B hB.1.1 _ _ _ (decides_wellFormed hT true) _ hρ,
    canon_subst hv' B hB.1.1 _ _ _ (decides_wellFormed hT false) _ hρ,
    decides_denote, decides_denote, decidesD_soften, decidesD_soften]

theorem outcome_canon {r : Regulated} (hr : r ∈ D.T.regulated) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B r.sorts vs) :
    (outcomeBase (soften D) r.name).denote B (tupleVal vs) ↔
      (if r.allowByDefault then ¬ DecidesSoftD D (canon (soften D) B) (tupleVal vs) r.name false
       else DecidesSoftD D (canon (soften D) B) (tupleVal vs) r.name true) := by
  have hv' := valid_of_wellFormed _ hv.wf
  have hk := index_before hv' hr
  have hT := rulesTyped_of_valid hv' hk
  have hρ := tupleVal_typed B _ vs hvs
  simp only [outcomeBase, find_regulated hv' hk]
  rw [canon_subst hv' B hB.1.1 _ _ _ (outcome_wellFormed hT) _ hρ, outcome_denote, pos, neg,
    decides_denote, decides_denote, decidesD_soften, decidesD_soften]

theorem circ_canon (φ : VE.Formula) (Γ : List String)
    (hφ : φ.WellFormed (envAt (soften D) (size (soften D))) Γ) (ρ : VE.Valuation B)
    (hρ : VE.Valuation.Typed B Γ ρ) :
    (subst (soften D).T (size (soften D)) φ).denote B ρ ↔ φ.denote (canon (soften D) B) ρ :=
  canon_subst (valid_of_wellFormed _ hv.wf) B hB.1.1 _ φ Γ hφ ρ hρ

theorem coh_canon {M N : SoftNode} (hc : (M, N) ∈ collidingPairs D) :
    (cohPremise D M N).denote B [] ↔ ∀ vs, VE.TupleTyped B (actSorts D M) vs →
      ¬ (SelectsSoftD D (canon (soften D) B) (tupleVal vs) (fuel D) M ∧
         SelectsSoftD D (canon (soften D) B) (tupleVal vs) (fuel D) N) := by
  obtain ⟨hM, hN, _⟩ := mem_collidingPairs.mp hc
  have hs := hv.cpSorts _ hc
  rw [cohPremise, bindAll_denote_nil]
  apply forall_congr'
  intro vs
  apply imp_congr_right
  intro hvs
  have hρ := tupleVal_typed B _ vs hvs
  simp only [VE.Formula.denote]
  rw [circ_canon hv B hB _ _ (hv.selTyped M hM) _ hρ, circ_canon hv B hB _ _ (by
      have := hv.selTyped N hN; rwa [← hs] at this) _ hρ, selects'_denote, selects'_denote]

end Decomposition

/-- W1's pointwise document iff on `T′`, instantiated (reused, not restated). -/
theorem coherent_expands (D : SoftDoc) (h : WellFormedSoft D = true) (B : VE.Structure.{u})
    (hB : VE.Norms.BaseAdmissible (soften D) B) :
    VE.Route.Unique (VE.Norms.DocumentExpansion (soften D) B) ↔ VE.Norms.ConflictFree (soften D) B :=
  VE.Norms.conflictFree_expands_document (soften D) (soften_wellFormed D h) B hB

/-- 6.3: conflict-freedom of `T′` is exactly: no strict collision, no pair conflict unless both
sides come from default rules, and coherence. -/
theorem soft_conflict_decomposition (D : SoftDoc) (h : WellFormedSoft D = true) (B : VE.Structure.{u})
    (hB : VE.Norms.BaseAdmissible (soften D) B) :
    VE.Norms.ConflictFree (soften D) B ↔
      NoStrictCollision D B ∧ NoHardPairConflict D B ∧ Sat B (cohPremises D) := by
  have hv := softValid_of_wellFormed D h
  have hv' := valid_of_wellFormed _ hv.wf
  -- abbreviations at the canonical interpretation
  let S := canon (soften D) B
  constructor
  · rintro ⟨hc1, hc2⟩
    have noBoth : ∀ r ∈ D.T.regulated, ∀ vs, VE.TupleTyped B r.sorts vs →
        ¬ (DecidesSoftD D S (tupleVal vs) r.name true ∧ DecidesSoftD D S (tupleVal vs) r.name false) :=
      fun r hr vs hvs hb => hc1 r hr vs hvs ((conflict_canon hv B hB hr vs hvs).mpr hb)
    refine ⟨fun r hr vs hvs hcol => ?_, fun pr hpr vs hvs ⟨hpc, _⟩ => hc2 pr hpr vs hvs hpc, ?_⟩
    · have hρ := tupleVal_typed B _ vs hvs
      rw [circ_canon hv B hB _ _ (by
        exact ⟨hv.decTyped r hr _ (by simp), hv.decTyped r hr _ (by simp)⟩) _ hρ] at hcol
      simp only [VE.Formula.denote, strictPos, strictNeg, strictDecides_denote] at hcol
      exact noBoth r hr vs hvs ⟨(decides_split hv _ _).mpr (Or.inl hcol.1),
        (decides_split hv _ _).mpr (Or.inl hcol.2)⟩
    · intro a ha
      obtain ⟨⟨M, N⟩, hc, rfl⟩ := List.mem_map.mp ha
      rw [coh_canon hv B hB hc]
      intro vs hvs ⟨sM, sN⟩
      obtain ⟨hM, hN, hMd, hNd, _, hi⟩ := mem_collidingPairs.mp hc
      obtain ⟨r, hr, hrn, hrs⟩ := reg_of_node hv hM
      have hvr : VE.TupleTyped B r.sorts vs := by rw [hrs]; exact hvs
      have decM : DecidesSoftD D S (tupleVal vs) M.pred M.sign := ⟨M, mem_rulesOn.mpr ⟨hM, rfl⟩, rfl, sM⟩
      have decN : DecidesSoftD D S (tupleVal vs) N.pred N.sign := ⟨N, mem_rulesOn.mpr ⟨hN, rfl⟩, rfl, sN⟩
      unfold Incompatible at hi
      simp only [Bool.or_eq_true, Bool.and_eq_true, beq_iff_eq, bne_iff_ne, ne_eq,
        Bool.not_eq_true'] at hi
      -- the pair case, with the requiring rule `Q` on `r` and the forbidding rule `F` on `m`
      have pairCase : ∀ Q F : SoftNode, Q ∈ D.T.nodes → Q.sign = true → F.sign = false →
          dualPerm D Q.pred = some F.pred → sortsOf D Q.pred = sortsOf D M.pred →
          DecidesSoftD D S (tupleVal vs) Q.pred true → DecidesSoftD D S (tupleVal vs) F.pred false → False := by
        intro Q F _ _ _ hd hQs decQ decF
        obtain ⟨pr, hpr, hreq, hperm⟩ := dualPerm_some hd
        obtain ⟨⟨rq, hrq, hrqn, hrqs⟩, ⟨rm, hrm, hrmn, hrms⟩⟩ := pair_regs hv hpr
        have hsorts : pr.sorts = r.sorts := by
          rw [← hrqs, ← sortsOf_reg hv hrq, hrqn, hreq, hQs, ← hrn, sortsOf_reg hv hr]
        have hvp : VE.TupleTyped B pr.sorts vs := by rw [hsorts]; exact hvr
        have e1 : rq.name = Q.pred := hrqn.trans hreq
        have e2 : rm.name = F.pred := hrmn.trans hperm
        rw [← e1] at decQ
        rw [← e2] at decF
        have hvq : VE.TupleTyped B rq.sorts vs := by rw [hrqs]; exact hvp
        have hvm : VE.TupleTyped B rm.sorts vs := by rw [hrms]; exact hvp
        apply hc2 pr hpr vs hvp
        simp only [pairConflict, VE.Formula.denote]
        rw [← hrqn, ← hrmn, outcome_canon hv B hB hrq vs hvq, outcome_canon hv B hB hrm vs hvm]
        refine ⟨?_, ?_⟩
        · split
          · exact fun hneg => noBoth rq hrq vs hvq ⟨decQ, hneg⟩
          · exact decQ
        · split
          · exact fun hn => hn decF
          · exact fun hpos => noBoth rm hrm vs hvm ⟨hpos, decF⟩
      rcases hi with (⟨hp, hs⟩ | ⟨⟨hMs, hNs⟩, hd⟩) | ⟨⟨hNs, hMs⟩, hd⟩
      · apply noBoth r hr vs hvr
        rw [hrn]
        cases hMs : M.sign <;> cases hNs : N.sign
        · exact absurd (hMs.trans hNs.symm) hs
        · exact ⟨by rw [hp]; rw [hNs] at decN; exact decN, by rw [hMs] at decM; exact decM⟩
        · exact ⟨by rw [hMs] at decM; exact decM, by rw [hp]; rw [hNs] at decN; exact decN⟩
        · exact absurd (hMs.trans hNs.symm) hs
      · exact pairCase M N hM hMs hNs hd rfl (by rw [hMs] at decM; exact decM)
          (by rw [hNs] at decN; exact decN)
      · have hNs' : sortsOf D N.pred = sortsOf D M.pred := (hv.cpSorts _ hc).symm
        exact pairCase N M hN hNs hMs hd hNs' (by rw [hNs] at decN; exact decN)
          (by rw [hMs] at decM; exact decM)
  · rintro ⟨hns, hnp, hcoh⟩
    have cohAt : ∀ M N, (M, N) ∈ collidingPairs D → ∀ vs, VE.TupleTyped B (actSorts D M) vs →
        ¬ (SelectsSoftD D S (tupleVal vs) (fuel D) M ∧ SelectsSoftD D S (tupleVal vs) (fuel D) N) :=
      fun M N hc => (coh_canon hv B hB hc).mp (hcoh _ (List.mem_map.mpr ⟨(M, N), hc, rfl⟩))
    refine ⟨fun r hr vs hvs hcon => ?_, fun pr hpr vs hvs hpc => ?_⟩
    · have hρ := tupleVal_typed B _ vs hvs
      obtain ⟨hpos, hneg⟩ := (conflict_canon hv B hB hr vs hvs).mp hcon
      have hoh := hard_over_soft D h S (tupleVal vs)
      rcases (decides_split hv _ _).mp hpos with sp | dp <;>
        rcases (decides_split hv _ _).mp hneg with sn | dn
      · apply hns r hr vs hvs
        rw [circ_canon hv B hB _ _ (by
          exact ⟨hv.decTyped r hr _ (by simp), hv.decTyped r hr _ (by simp)⟩) _ hρ]
        simp only [VE.Formula.denote, strictPos, strictNeg, strictDecides_denote]
        exact ⟨sp, sn⟩
      · exact (hoh.1 _ _ sp).2 dn
      · exact (hoh.1 _ _ sn).1 dp
      · obtain ⟨M, N, hc, hMp, _, sM, sN, _⟩ := (weighing_points_complete D h S (tupleVal vs)).1 _ dp dn
        apply cohAt M N hc vs _ ⟨sM, sN⟩
        rw [actSorts, hMp, sortsOf_reg hv hr]
        exact hvs
    · have hρ := tupleVal_typed B _ vs hvs
      obtain ⟨⟨rq, hrq, hrqn, hrqs⟩, _⟩ := pair_regs hv hpr
      have hdd := Classical.byContradiction fun hn => hnp pr hpr vs hvs ⟨hpc, hn⟩
      rw [circ_canon hv B hB _ _ (by
        refine ⟨?_, ?_⟩
        · have := hv.decTyped rq hrq (defaultPos D rq.name) (by simp)
          rw [hrqn, hrqs] at this; exact this
        · obtain ⟨_, ⟨rm, hrm, hrmn, hrms⟩⟩ := pair_regs hv hpr
          have := hv.decTyped rm hrm (defaultNeg D rm.name) (by simp)
          rw [hrmn, hrms] at this; exact this) _ hρ] at hdd
      simp only [VE.Formula.denote, defaultPos, defaultNeg, defaultDecides_denote] at hdd
      obtain ⟨M, N, hc, hpreds, sM, sN, _⟩ :=
        (weighing_points_complete D h S (tupleVal vs)).2 pr hpr hdd.1 hdd.2
      obtain ⟨⟨_, _, _⟩, ⟨rm, hrm, hrmn, hrms⟩⟩ := pair_regs hv hpr
      apply cohAt M N hc vs _ ⟨sM, sN⟩
      rcases hpreds with ⟨hMp, _⟩ | ⟨hMp, _⟩
      · rw [actSorts, hMp, ← hrqn, sortsOf_reg hv hrq, hrqs]; exact hvs
      · rw [actSorts, hMp, ← hrmn, sortsOf_reg hv hrm, hrms]; exact hvs

/-- Over coherent bases the check is exactly "no strict collision and no hard pair conflict". -/
theorem soft_conflict_free_iff (D : SoftDoc) (h : WellFormedSoft D = true) :
    SoftConflictFree.{u} D ↔
      ∀ B : VE.Structure.{u}, BaseAdmissible' D B → NoStrictCollision D B ∧ NoHardPairConflict D B := by
  constructor
  · intro hc B hB
    have := (soft_conflict_decomposition D h B hB.1).mp (hc B hB)
    exact ⟨this.1, this.2.1⟩
  · intro hc B hB
    exact (soft_conflict_decomposition D h B hB.1).mpr
      ⟨(hc B hB).1, (hc B hB).2, fun a ha => hB.2 a (List.mem_append_right _ ha)⟩

/-- A conflict witness in a coherent base is strict–strict or involves a strict rule or a completion. -/
theorem soft_witness_classified (D : SoftDoc) (h : WellFormedSoft D = true) (B : VE.Structure.{u})
    (hB : BaseAdmissible' D B) (hn : ¬ VE.Norms.ConflictFree (soften D) B) :
    ¬ NoStrictCollision D B ∨ ¬ NoHardPairConflict D B := by
  refine Classical.byContradiction fun hno => hn ?_
  exact (soft_conflict_decomposition D h B hB.1).mpr
    ⟨Classical.byContradiction fun h1 => hno (Or.inl h1), Classical.byContradiction fun h2 => hno (Or.inr h2),
      fun a ha => hB.2 a (List.mem_append_right _ ha)⟩

/-- Unique expansion over coherent bases. -/
theorem soft_coherent_expands_all (D : SoftDoc) (h : WellFormedSoft D = true) :
    (∀ B : VE.Structure.{u}, BaseAdmissible' D B → VE.Route.Unique (VE.Norms.DocumentExpansion (soften D) B)) ↔
      SoftConflictFree.{u} D :=
  ⟨fun hu B hB => (coherent_expands D h B hB.1).mp (hu B hB),
   fun hc B hB => (coherent_expands D h B hB.1).mpr (hc B hB)⟩

/-! ## The certified statement: W1's conflict check over `Background_base′` -/

/-- W1's `conflictFreeCheck` on `T′` with `Background_base′` in place of `Background_base`:
every target of `soften D` has an accepted certificate for
`Background_base′ ⊢ ∀x̄. ¬conflict` over the regenerated `E′_base`. -/
def softConflictFreeCheck (D : SoftDoc) (certs : List (Option VE.Tableau.Certificate)) : Bool :=
  (targets (soften D)).length == certs.length &&
    ((targets (soften D)).zip certs).all (fun (t, c) => match c with
      | some c => VE.Tableau.checkCertificate (envAt (soften D) 0) (backgroundBase' D) (targetConclusion t) c
      | none => false)

theorem softConflictFreeCheck_target {D : SoftDoc} {certs : List (Option VE.Tableau.Certificate)}
    (hc : softConflictFreeCheck D certs = true) {t : String × List String × VE.Formula}
    (ht : t ∈ targets (soften D)) :
    ∃ c, VE.Tableau.checkCertificate (envAt (soften D) 0) (backgroundBase' D) (targetConclusion t) c = true := by
  simp only [softConflictFreeCheck, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hc
  obtain ⟨hl, hall⟩ := hc
  obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp ht
  have hlt : i < (targets (soften D)).length := (List.getElem?_eq_some_iff.mp hi).1
  have hlt' : i < certs.length := hl ▸ hlt
  have hmem : (t, certs[i]) ∈ (targets (soften D)).zip certs := by
    apply List.mem_iff_getElem?.mpr
    refine ⟨i, ?_⟩
    rw [List.getElem?_zip_eq_some]
    exact ⟨hi, List.getElem?_eq_getElem hlt'⟩
  have := hall _ hmem
  cases hci : certs[i] with
  | none => rw [hci] at this; cases this
  | some c => rw [hci] at this; exact ⟨c, this⟩

theorem sat_backgroundBase' {D : SoftDoc} {B : VE.Structure.{u}} (hB : BaseAdmissible' D B) :
    ∀ a ∈ backgroundBase' D, a.denote B [] := by
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact hB.1.2 a ha
  · exact hB.2 a ha

/-- 6.3, the certified statement. -/
theorem soft_conflict_free (D : SoftDoc) (h : WellFormedSoft D = true)
    (certs : List (Option VE.Tableau.Certificate)) (hc : softConflictFreeCheck D certs = true) :
    SoftConflictFree.{u} D := by
  have hv := valid_of_wellFormed _ (soften_wellFormed D h)
  intro B hB
  have cert : ∀ t ∈ targets (soften D), ∀ vs, VE.TupleTyped B t.2.1 vs → ¬ t.2.2.denote B (tupleVal vs) := by
    intro t ht vs hvs
    obtain ⟨c, hcc⟩ := softConflictFreeCheck_target hc ht
    have he := VE.Tableau.checkCertificate_sound.{u} _ _ _ c hcc B hB.1.1 (sat_backgroundBase' hB)
    exact (bindAll_denote_nil B _ _).mp he vs hvs
  refine ⟨fun r hr vs hvs => ?_, fun pr hpr vs hvs => ?_⟩
  · exact cert (r.name, r.sorts, conflict (soften D) r)
      (List.mem_append_left _ (List.mem_filterMap.mpr ⟨.reg r, hv.regulated r hr, rfl⟩)) vs hvs
  · exact cert (pr.req ++ "->" ++ pr.perm, pr.sorts, pairConflict (soften D) pr)
      (List.mem_append_right _ (List.mem_map.mpr ⟨pr, hpr, rfl⟩)) vs hvs

/-! ## Witnesses -/

/-- W1's `backgroundValid` on `soften D` and the finite evaluation of every soft premise. -/
def backgroundValid' {α : Type u} [DecidableEq α] (D : SoftDoc) (M : VE.FiniteModel α) : Bool :=
  VE.Norms.backgroundValid (soften D) M && (softPremises D).all (fun a => a.eval M [])

/-- Classification evaluates `Exc_T` only, never a coherence conjunct. -/
def classificationBackgroundValid {α : Type u} [DecidableEq α] (D : SoftDoc) (M : VE.FiniteModel α) : Bool :=
  VE.Norms.backgroundValid (soften D) M && (excPremises D).all (fun a => a.eval M [])

theorem baseAdmissible'_of_valid {α : Type u} [DecidableEq α] (D : SoftDoc) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt (soften D) 0)) (hb : backgroundValid' D M = true) :
    BaseAdmissible' D M.asStructure := by
  simp only [backgroundValid', Bool.and_eq_true, List.all_eq_true] at hb
  exact ⟨baseAdmissible_of_valid _ M valid hb.1, fun a ha => (VE.eval_iff_denote M [] a).mp (hb.2 a ha)⟩

/-- A typed finite base witness over `E′_base` passing the extended Background check refutes the
conditional claim. -/
theorem soft_conflict_witness_sound {α : Type u} [DecidableEq α] (D : SoftDoc) (h : WellFormedSoft D = true)
    (t : String × List String × VE.Formula) (ht : t ∈ VE.Norms.targets (soften D))
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (soften D) 0)) (hb : backgroundValid' D M = true)
    (vs : List α) (typed : VE.TupleTyped M.asStructure t.2.1 vs) (hw : t.2.2.eval M (tupleVal vs) = true) :
    ¬ VE.Norms.ConflictFree (soften D) M.asStructure ∧
    ¬ VE.Route.Unique (VE.Norms.DocumentExpansion (soften D) M.asStructure) ∧ ¬ SoftConflictFree.{u} D ∧
    (¬ NoStrictCollision D M.asStructure ∨ ¬ NoHardPairConflict D M.asStructure) := by
  have hB := baseAdmissible'_of_valid D M valid hb
  obtain ⟨hn, hu, _⟩ := Replay.target_refutes (soften D) (soften_wellFormed D h) t ht M.asStructure hB.1 vs typed
    ((VE.eval_iff_denote M _ _).mp hw)
  exact ⟨hn, hu, fun hc => hn (hc _ hB), soft_witness_classified D h _ hB hn⟩

/-! ## The fragment gate and substructures -/

/-- A universally closed quantifier-free formula. -/
def universalQF : VE.Formula → Bool
  | .all _ a => universalQF a
  | φ => VE.Norms.Formula.qfree φ

/-- The complete syntactic fragment gate of 6.1, including the separately generated soft premises. -/
def InFragment (D : SoftDoc) : Bool :=
  VE.Norms.InFragment (soften D) && (softPremises D).all universalQF

/-- A sort-respecting substructure of `E′_base`: an injective embedding preserving sorts,
constants retained, the base relations restricted. -/
def BaseSubstructure (D : SoftDoc) (B₀ B : VE.Structure.{u}) : Prop :=
  ∃ e : B₀.Carrier → B.Carrier, (∀ x y, e x = e y → x = y) ∧
    (∀ s v, B₀.domain s v → B.domain s (e v)) ∧
    (∀ c, B.constant c = (B₀.constant c).map e) ∧
    (∀ p vs, ((envAt (soften D) 0).predicates p).isSome → (B₀.relation p vs ↔ B.relation p (vs.map e)))

section Sub
variable {D : SoftDoc} {B₀ B : VE.Structure.{u}} (e : B₀.Carrier → B.Carrier)

theorem term_embed (hc : ∀ c, B.constant c = (B₀.constant c).map e) (ρ : VE.Valuation B₀) (t : VE.Term) :
    t.denote B (ρ.map e) = (t.denote B₀ ρ).map e := by
  cases t with
  | var i => simp [VE.Term.denote, List.getElem?_map]
  | const c => simp [VE.Term.denote, hc c]

theorem qfree_embed (hinj : ∀ x y, e x = e y → x = y) (hc : ∀ c, B.constant c = (B₀.constant c).map e)
    (hr : ∀ p vs, ((envAt (soften D) 0).predicates p).isSome → (B₀.relation p vs ↔ B.relation p (vs.map e))) :
    ∀ (φ : VE.Formula) (Γ : List String) (ρ : VE.Valuation B₀),
    VE.Norms.Formula.qfree φ = true → φ.WellFormed (envAt (soften D) 0) Γ →
    (φ.denote B (ρ.map e) ↔ φ.denote B₀ ρ)
  | .top, _, _, _, _ | .bottom, _, _, _, _ => Iff.rfl
  | .unary p t, _, ρ, _, ⟨_, hp, _⟩ => by
    simp only [VE.Formula.denote, term_embed e hc]
    have hpd : ((envAt (soften D) 0).predicates p).isSome := by simp [hp]
    constructor
    · rintro ⟨w, hw, hrel⟩
      obtain ⟨v, hv, rfl⟩ := Option.map_eq_some_iff.mp hw
      exact ⟨v, hv, (hr p [v] hpd).mpr hrel⟩
    · rintro ⟨v, hv, hrel⟩
      exact ⟨e v, by rw [hv]; rfl, (hr p [v] hpd).mp hrel⟩
  | .binary p t w, _, ρ, _, ⟨_, _, hp, _⟩ => by
    simp only [VE.Formula.denote, term_embed e hc]
    have hpd : ((envAt (soften D) 0).predicates p).isSome := by simp [hp]
    constructor
    · rintro ⟨a, b, ha, hb, hrel⟩
      obtain ⟨v, hv, rfl⟩ := Option.map_eq_some_iff.mp ha
      obtain ⟨v', hv', rfl⟩ := Option.map_eq_some_iff.mp hb
      exact ⟨v, v', hv, hv', (hr p [v, v'] hpd).mpr hrel⟩
    · rintro ⟨v, v', hv, hv', hrel⟩
      exact ⟨e v, e v', by rw [hv]; rfl, by rw [hv']; rfl, (hr p [v, v'] hpd).mp hrel⟩
  | .eq t w, _, ρ, _, _ => by
    simp only [VE.Formula.denote, term_embed e hc]
    constructor
    · rintro ⟨a, ha, hb⟩
      obtain ⟨v, hv, rfl⟩ := Option.map_eq_some_iff.mp ha
      obtain ⟨v', hv', he⟩ := Option.map_eq_some_iff.mp hb
      exact ⟨v, hv, by rw [hv', hinj _ _ he]⟩
    · rintro ⟨v, hv, hv'⟩
      exact ⟨e v, by rw [hv]; rfl, by rw [hv']; rfl⟩
  | .not a, Γ, ρ, hq, hw => by
    simp only [VE.Formula.denote]; rw [qfree_embed hinj hc hr a Γ ρ hq hw]
  | .and a b, Γ, ρ, hq, hw | .or a b, Γ, ρ, hq, hw | .implies a b, Γ, ρ, hq, hw => by
    simp only [VE.Norms.Formula.qfree, Bool.and_eq_true] at hq
    simp only [VE.Formula.denote]
    rw [qfree_embed hinj hc hr a Γ ρ hq.1 hw.1, qfree_embed hinj hc hr b Γ ρ hq.2 hw.2]
  | .all _ _, _, _, hq, _ | .ex _ _, _, _, hq, _ => by simp [VE.Norms.Formula.qfree] at hq

theorem universal_down (hinj : ∀ x y, e x = e y → x = y) (hc : ∀ c, B.constant c = (B₀.constant c).map e)
    (hr : ∀ p vs, ((envAt (soften D) 0).predicates p).isSome → (B₀.relation p vs ↔ B.relation p (vs.map e)))
    (hd : ∀ s v, B₀.domain s v → B.domain s (e v)) :
    ∀ (φ : VE.Formula) (Γ : List String) (ρ : VE.Valuation B₀),
    universalQF φ = true → φ.WellFormed (envAt (soften D) 0) Γ →
    φ.denote B (ρ.map e) → φ.denote B₀ ρ
  | .all s a, Γ, ρ, hq, hw, h => by
    intro v hv
    exact universal_down hinj hc hr hd a (s :: Γ) (v :: ρ) hq hw.2 (h (e v) (hd s v hv))
  | .top, Γ, ρ, hq, hw, h | .bottom, Γ, ρ, hq, hw, h | .unary _ _, Γ, ρ, hq, hw, h
  | .binary _ _ _, Γ, ρ, hq, hw, h | .eq _ _, Γ, ρ, hq, hw, h | .not _, Γ, ρ, hq, hw, h
  | .and _ _, Γ, ρ, hq, hw, h | .or _ _, Γ, ρ, hq, hw, h | .implies _ _, Γ, ρ, hq, hw, h
  | .ex _ _, Γ, ρ, hq, hw, h =>
    (qfree_embed e hinj hc hr _ Γ ρ hq hw).mp h

end Sub

/-- 6.1: the complete fragment gate makes every generated soft premise survive substructures. -/
theorem soft_premises_substructure (D : SoftDoc) (h : WellFormedSoft D = true) (hf : InFragment D = true)
    (B₀ B : VE.Structure.{u}) (hsub : BaseSubstructure D B₀ B) (hs : Sat B (softPremises D)) :
    Sat B₀ (softPremises D) := by
  have hv := softValid_of_wellFormed D h
  obtain ⟨e, hinj, hd, hc, hr⟩ := hsub
  simp only [InFragment, Bool.and_eq_true, List.all_eq_true] at hf
  intro a ha
  exact universal_down e hinj hc hr hd a [] [] (hf.2 a ha) (hv.premTyped a ha) (hs a ha)

/-! ## The restated route (W1's `Layer.lean` shape with `PrefixAdmissible′` and `background′`) -/

section SoftLayer
variable {D : SoftDoc} (hv : Valid (soften D)) {k : Nat} {q : Sym} (hk : (syms (soften D).T)[k]? = some q)
include hv hk

omit hv in
theorem soft_restrict_admissible (S : VE.Structure.{u}) (h : PrefixAdmissible' D (k + 1) S) :
    PrefixAdmissible' D k (forget [q.name] S) := by
  refine ⟨?_, ?_⟩
  · have h1 := h.1
    simp only [PrefixAdmissible, hk] at h1
    exact h1.2.1
  · rw [restrictAll_forget (name_mem_layerNames hk)]
    exact h.2

theorem soft_layer_expands
    (hc : ∀ S₀ : VE.Structure.{u}, PrefixAdmissible' D k S₀ → ConflictFreeAtIdx (soften D) k S₀)
    (S₀ : VE.Structure.{u}) (h₀ : PrefixAdmissible' D k S₀) :
    Unique fun S => forget [q.name] S = S₀ ∧ PrefixAdmissible' D (k + 1) S ∧
      ∀ a ∈ symPremises (soften D).T q, a.denote S [] := by
  have := (local_expands hv hk S₀ h₀.1).mpr (hc S₀ h₀)
  refine (unique_congr fun S => ?_).mp this
  constructor
  · rintro ⟨h₁, h₂⟩
    refine ⟨h₁, ⟨h₂, ?_⟩, symPremises_sat hv hk S h₂⟩
    rw [← restrictAll_forget (name_mem_layerNames hk) S, h₁]
    exact h₀.2
  · rintro ⟨h₁, h₂, _⟩
    exact ⟨h₁, h₂.1⟩

end SoftLayer

/-- The soft layer of the `k`-th layer symbol of `T′`: W1's `symLayer` with `PrefixAdmissible′`. -/
def softSymLayer (D : SoftDoc) (hv : Valid (soften D)) (k : Nat) (q : Sym)
    (hk : (syms (soften D).T)[k]? = some q)
    (hc : ∀ S₀ : VE.Structure.{u}, PrefixAdmissible' D k S₀ → ConflictFreeAtIdx (soften D) k S₀) :
    VE.Route.Layer VE.Route.fol.{u} Unit where
  E_in := envAt (soften D) k
  E_out := envAt (soften D) (k + 1)
  extends_env a h := envAt_mono (Nat.le_succ k) a [] h
  premises _ := symPremises (soften D).T q
  premises_wellFormed _ := symPremises_wellFormed hv hk
  Admissible_in := PrefixAdmissible' D k
  Admissible_out := PrefixAdmissible' D (k + 1)
  admissible_out _ h := prefixAdmissible_admissible h.1
  restrict := forget [q.name]
  restrict_admissible S h := soft_restrict_admissible hk S h
  restrict_holds S a _ ha := denote_forget (self_hidden hv hk) S a [] [] ha
  Intended _ S := LayerMeaning (soften D).T S q
  faithful _ S h := symLayer_faithful hv hk S h.1
  expands _ S₀ h₀ := soft_layer_expands hv hk hc S₀ h₀

/-- A composed prefix of the soft route. -/
structure SoftChain (D : SoftDoc) (k : Nat) where
  R : VE.Route.Layer VE.Route.fol.{u} Unit
  E_in : R.E_in = envAt (soften D) 0
  E_out : R.E_out = envAt (soften D) k
  A_in : ∀ S, R.Admissible_in S ↔ PrefixAdmissible' D 0 S
  A_out : ∀ S, R.Admissible_out S ↔ PrefixAdmissible' D k S
  restrict : ∀ S, R.restrict S = forget ((layerNames (soften D).T).take k) S
  premises : ∀ d, R.premises d = ((syms (soften D).T).take k).flatMap (symPremises (soften D).T)

def softChain (D : SoftDoc) (hv : Valid (soften D))
    (hc : ∀ k (S₀ : VE.Structure.{u}), PrefixAdmissible' D k S₀ → ConflictFreeAtIdx (soften D) k S₀) :
    (k : Nat) → k ≤ size (soften D) → SoftChain.{u} D k
  | 0, _ =>
    { R := VE.Route.Layer.id (envAt (soften D) 0) (PrefixAdmissible' D 0) (fun _ h => h.1.1)
      E_in := rfl
      E_out := rfl
      A_in := fun _ => Iff.rfl
      A_out := fun _ => Iff.rfl
      restrict := fun S => by simp [VE.Route.Layer.id, forget_nil]
      premises := fun _ => by simp [VE.Route.Layer.id] }
  | k + 1, hk =>
    let C := softChain D hv hc k (Nat.le_of_succ_le hk)
    have hlt : k < (syms (soften D).T).length := hk
    let q := (syms (soften D).T)[k]
    have hq : (syms (soften D).T)[k]? = some q := List.getElem?_eq_getElem hlt
    let L := softSymLayer D hv k q hq (hc k)
    { R := VE.Route.Layer.comp C.R L C.E_out.symm (fun S => (C.A_out S).symm)
      E_in := C.E_in
      E_out := rfl
      A_in := C.A_in
      A_out := fun _ => Iff.rfl
      restrict := fun S => by
        show C.R.restrict (forget [q.name] S) = _
        rw [C.restrict, forget_forget, List.take_succ, names_getElemOpt hq]
        rfl
      premises := fun d => by
        simp only [VE.Route.Layer.comp]
        rw [C.premises, List.take_succ, hq]
        simp [L, softSymLayer] }

theorem prefixAdmissible'_zero (D : SoftDoc) (B : VE.Structure.{u}) :
    PrefixAdmissible' D 0 B ↔ BaseAdmissible' D B := by
  constructor
  · rintro ⟨hB, hs⟩
    exact ⟨hB, by rw [restrictAll_self B hB.1] at hs; exact hs⟩
  · rintro ⟨hB, hs⟩
    exact ⟨hB, by rw [restrictAll_self B hB.1]; exact hs⟩

/-- Coherent conflict-freedom gives every soft layer's hypothesis. -/
theorem softChain_hc {D : SoftDoc} (hv : Valid (soften D)) (hc : SoftConflictFree.{u} D) :
    ∀ k (S₀ : VE.Structure.{u}), PrefixAdmissible' D k S₀ → ConflictFreeAtIdx (soften D) k S₀ := by
  intro k S₀ h₀
  cases hk : (syms (soften D).T)[k]? with
  | none => simp [ConflictFreeAtIdx, hk]
  | some q =>
    have hB := ((prefix_char hv k (prefixAdmissible_le h₀.1) S₀).mp h₀.1).2.1
    exact conflictFreeAt_of_base hv hk S₀ h₀.1 (hc _ ⟨hB, h₀.2⟩)

def softRouteChain (D : SoftDoc) (h : WellFormedSoft D = true) (hc : SoftConflictFree.{u} D) :
    SoftChain.{u} D (size (soften D)) :=
  softChain D (valid_of_wellFormed _ (soften_wellFormed D h))
    (softChain_hc (valid_of_wellFormed _ (soften_wellFormed D h)) hc) _ (Nat.le_refl _)

theorem softRouteChain_premises (D : SoftDoc) (h : WellFormedSoft D = true) (hc : SoftConflictFree.{u} D)
    (d : Unit) : (softRouteChain D h hc).R.premises d = elaborate (soften D).T := by
  rw [(softRouteChain D h hc).premises, elaborate_eq_flatMap]
  simp [size]

theorem softRouteChain_restrict (D : SoftDoc) (h : WellFormedSoft D = true) (hc : SoftConflictFree.{u} D)
    (S : VE.Structure.{u}) : (softRouteChain D h hc).R.restrict S = restrictAll (soften D).T S := by
  rw [(softRouteChain D h hc).restrict, List.take_of_length_le (by simp [size, layerNames])]
  rfl

/-- The soft route: the composed frozen P0 layers of `T′` with `BaseAdmissible′` as input admissibility. -/
def softRoute (D : SoftDoc) (h : WellFormedSoft D = true) (hc : SoftConflictFree.{u} D) :
    { R : VE.Route.Layer VE.Route.fol.{u} Unit // R.E_in = envAt (soften D) 0 ∧
      (∀ B, R.Admissible_in B ↔ BaseAdmissible' D B) ∧ R.E_out = envAt (soften D) (size (soften D)) ∧
      R.premises () = VE.Norms.elaborate (soften D).T } :=
  ⟨(softRouteChain D h hc).R, (softRouteChain D h hc).E_in,
    fun B => ((softRouteChain D h hc).A_in B).trans (prefixAdmissible'_zero D B),
    (softRouteChain D h hc).E_out, softRouteChain_premises D h hc ()⟩

theorem sat_soft_restrict {D : SoftDoc} (hv : SoftValid D) (S : VE.Structure.{u}) :
    Sat (restrictAll (soften D).T S) (softPremises D) ↔ Sat S (softPremises D) := by
  constructor
  · intro hs a ha
    exact (restrictAll_denote a [] (hv.premTyped a ha) S []).mp (hs a ha)
  · intro hs a ha
    exact (restrictAll_denote a [] (hv.premTyped a ha) S []).mpr (hs a ha)

theorem soft_route_backgroundSound (D : SoftDoc) (h : WellFormedSoft D = true) (hc : SoftConflictFree.{u} D) :
    VE.Route.BackgroundSound (softRoute D h hc).1 (background' D) := by
  have hsv := softValid_of_wellFormed D h
  have hv := valid_of_wellFormed _ hsv.wf
  intro d S hS _
  have hpa := ((softRouteChain D h hc).A_out S).mp hS
  obtain ⟨_, hB, hM, hP⟩ := (prefix_char hv _ (Nat.le_refl _) S).mp hpa.1
  have hdoc := (sat_document hv S).mpr ⟨(sat_literals_forget _ _ S).mp hB.2, hM, hP⟩
  have hsoft := (sat_soft_restrict hsv S).mp hpa.2
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact hdoc a (List.mem_append_left _ ha)
  · exact hsoft a ha

theorem soft_route_backgroundComplete (D : SoftDoc) (h : WellFormedSoft D = true) (hc : SoftConflictFree.{u} D) :
    VE.Route.BackgroundComplete (softRoute D h hc).1 (background' D) := by
  have hsv := softValid_of_wellFormed D h
  have hv := valid_of_wellFormed _ hsv.wf
  intro d S hA hbg hprem
  have hA' : S.Admissible (envAt (soften D) (size (soften D))) := by
    have := (softRoute D h hc).2.2.2.1
    simp only [VE.Route.fol] at hA
    rw [this] at hA
    exact hA
  have hprem' : Sat S (elaborate (soften D).T) := by
    have := softRouteChain_premises D h hc d
    intro a ha
    exact hprem a (by show a ∈ (softRouteChain D h hc).R.premises d; rw [this]; exact ha)
  have hsat : Sat S (background (soften D) ++ elaborate (soften D).T) := fun a ha => by
    rcases List.mem_append.mp ha with ha | ha
    · exact hbg a (List.mem_append_left _ ha)
    · exact hprem' a ha
  obtain ⟨hl, hM, hP⟩ := (sat_document hv S).mp hsat
  apply ((softRouteChain D h hc).A_out S).mpr
  refine ⟨(prefix_char hv _ (Nat.le_refl _) S).mpr
    ⟨hA', ⟨restrictAll_admissible _ S hA', (sat_literals_forget _ _ S).mpr hl⟩, hM, hP⟩, ?_⟩
  exact (sat_soft_restrict hsv S).mpr (fun a ha => hbg a (List.mem_append_right _ ha))

/-- Prefix satisfaction on the soft route. -/
theorem soft_prefix_satisfaction (D : SoftDoc) (h : WellFormedSoft D = true) (i : Nat)
    (hi : i ≤ size (soften D)) (S : VE.Structure.{u}) :
    PrefixAdmissible' D i S ↔ S.Admissible (envAt (soften D) i) ∧ BaseAdmissible' D (restrictAll (soften D).T S) ∧
      Sat S (VE.Norms.PrefixPremises (soften D) i) := by
  rw [PrefixAdmissible', prefix_satisfaction (soften D) (soften_wellFormed D h) i hi S, BaseAdmissible']
  constructor
  · rintro ⟨⟨hA, hB, hP⟩, hs⟩
    exact ⟨hA, ⟨hB, hs⟩, hP⟩
  · rintro ⟨hA, ⟨hB, hs⟩, hP⟩
    exact ⟨⟨hA, hB, hP⟩, hs⟩

theorem soft_conflictFree_prefix (D : SoftDoc) (h : WellFormedSoft D = true) (r : Regulated)
    (_hr : r ∈ D.T.regulated) (hc : SoftConflictFree.{u} D) (S₀ : VE.Structure.{u})
    (h₀ : PrefixAdmissible' D (before (soften D) r.name) S₀) :
    VE.Norms.ConflictFreeAt (soften D) r.name S₀ :=
  softChain_hc (valid_of_wellFormed _ (soften_wellFormed D h)) hc _ S₀ h₀

/-- The first half of `soft_route_acceptance`, which needs no conflict-freedom. -/
theorem soft_route_intended (D : SoftDoc) (h : WellFormedSoft D = true)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envAt (soften D) (size (soften D)))
                  (background' D ++ VE.Norms.elaborate (soften D).T ++ Γ) φ c = true)
    (S : VE.Structure.{u}) (hS : S.Admissible (envAt (soften D) (size (soften D)))) (hsoft : holdsSoft D S)
    (hdef : VE.Norms.definitionsHold (soften D) S) (hprof : VE.Norms.profileHold (soften D) S)
    (hbase : Sat S (VE.Norms.backgroundBase (soften D))) (hsp : Sat S (softPremises D)) (hΓ : Sat S Γ) :
    φ.denote S [] := by
  apply VE.Tableau.checkCertificate_sound.{u} _ _ _ c accepted S hS
  intro a ha
  simp only [List.mem_append, background', background] at ha
  rcases ha with ((((ha | ha) | ha) | ha) | ha) | ha
  · exact hdef a ha
  · exact hbase a ha
  · exact hprof a ha
  · exact hsp a ha
  · exact (soft_elaborate_iff D h S).mpr hsoft a ha
  · exact hΓ a ha

/-- 6.4: W1's `norms_route_acceptance` restated with `BaseAdmissible′` and `background′`. -/
theorem soft_route_acceptance (D : SoftDoc) (h : WellFormedSoft D = true) (hc : SoftConflictFree.{u} D)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envAt (soften D) (size (soften D)))
                  (background' D ++ VE.Norms.elaborate (soften D).T ++ Γ) φ c = true) :
    (∀ S : VE.Structure.{u}, S.Admissible (envAt (soften D) (size (soften D))) → holdsSoft D S →
      VE.Norms.definitionsHold (soften D) S → VE.Norms.profileHold (soften D) S →
      Sat S (VE.Norms.backgroundBase (soften D)) → Sat S (softPremises D) → Sat S Γ → φ.denote S []) ∧
    ((∀ a ∈ Γ, a.WellFormed (envAt (soften D) 0) []) → φ.WellFormed (envAt (soften D) 0) [] →
      ∀ B : VE.Structure.{u}, BaseAdmissible' D B → Sat B Γ → φ.denote B []) := by
  refine ⟨fun S hS hsoft hdef hprof hbase hsp hΓ =>
    soft_route_intended D h Γ φ c accepted S hS hsoft hdef hprof hbase hsp hΓ, fun hΓ hφ => ?_⟩
  · let R := softRoute D h hc
    have hacc : (VE.Route.Checker.tableau R.1.E_out).valid c
        (VE.Route.checkedPremises R.1 (background' D) () Γ) φ := by
      show VE.Tableau.checkCertificate R.1.E_out _ φ c = true
      rw [R.2.2.2.1, VE.Route.checkedPremises, R.2.2.2.2]
      exact accepted
    have := VE.Route.route_acceptance R.1 (background' D) (soft_route_backgroundSound D h hc)
      (VE.Route.Checker.tableau R.1.E_out) () Γ φ c _ φ hacc (List.map_id _) rfl
    intro B hB hs
    exact this.2.2 (by rw [R.2.1]; exact hΓ) (by rw [R.2.1]; exact hφ) B ((R.2.2.1 B).mpr hB) hs

/-- 6.4: W1's `norms_route_countermodel` restated. -/
theorem soft_route_countermodel (D : SoftDoc) (h : WellFormedSoft D = true) (hc : SoftConflictFree.{u} D)
    (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAt (soften D) 0) []) (hφ : φ.WellFormed (envAt (soften D) 0) [])
    (B : VE.Structure.{u}) (hB : BaseAdmissible' D B) (hs : Sat B Γ) (hn : ¬ φ.denote B []) :
    ∃ S, VE.Norms.DocumentExpansion (soften D) B S ∧ Sat S (softPremises D) ∧ Sat S Γ ∧ ¬ φ.denote S [] := by
  let R := softRoute D h hc
  obtain ⟨S, hr, hA, hsat, hno⟩ := VE.Route.route_countermodel_expands R.1 (background' D)
    (soft_route_backgroundSound D h hc) () Γ φ (by rw [R.2.1]; exact hΓ) (by rw [R.2.1]; exact hφ)
    B ((R.2.2.1 B).mpr hB) hs hn
  obtain ⟨hbg, hp, hg⟩ := (VE.Route.sat_checked R.1 (background' D) S () Γ).mp hsat
  have hp' : Sat S (elaborate (soften D).T) := by
    intro a ha
    exact hp a (by show a ∈ R.1.premises (); rw [R.2.2.2.2]; exact ha)
  refine ⟨S, ⟨by rw [← softRouteChain_restrict D h hc]; exact hr,
    prefixAdmissible_admissible (((softRouteChain D h hc).A_out S).mp hA).1, fun a ha => ?_⟩,
    fun a ha => hbg a (List.mem_append_right _ ha), hg, hno⟩
  rcases List.mem_append.mp ha with ha | ha
  · exact hbg a (List.mem_append_left _ ha)
  · exact hp' a ha

theorem soft_route_entails_iff (D : SoftDoc) (h : WellFormedSoft D = true) (hc : SoftConflictFree.{u} D)
    (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAt (soften D) 0) []) (hφ : φ.WellFormed (envAt (soften D) 0) []) :
    VE.Entails.{u} (envAt (soften D) (size (soften D))) (background' D ++ VE.Norms.elaborate (soften D).T ++ Γ) φ ↔
      ∀ B : VE.Structure.{u}, BaseAdmissible' D B → Sat B Γ → φ.denote B [] := by
  let R := softRoute D h hc
  have := VE.Route.route_entails_iff R.1 (background' D) (soft_route_backgroundSound D h hc)
    (soft_route_backgroundComplete D h hc) () Γ φ (by rw [R.2.1]; exact hΓ) (by rw [R.2.1]; exact hφ)
  rw [R.2.2.2.1, VE.Route.checkedPremises, R.2.2.2.2] at this
  rw [VE.Route.fol_entails_iff] at this
  rw [this]
  exact ⟨fun h B hB hs => h B ((R.2.2.1 B).mpr hB) hs, fun h B hB hs => h B ((R.2.2.1 B).mp hB) hs⟩

end VE.SoftNorms
