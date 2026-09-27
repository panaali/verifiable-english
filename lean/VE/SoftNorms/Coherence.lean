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

end VE.SoftNorms
