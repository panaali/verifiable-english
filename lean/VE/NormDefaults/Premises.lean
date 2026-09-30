import VE.NormDefaults.Semantics
import VE.SoftNorms.Coherence

/-! Pair premises at gaps and admissible fillings (docs/spec/norm-defaults.md 2.4,
3.1 and 7).

`gapF U p` is "no author rule on `p` decides", substituted on `fill U` (so lower
gaps appear as unsaid atoms). `Fill_T` (`fillPremises`) says, for every declared
pair with an unspecified member, "whatever must be done may be done" wherever one
member is a gap. `BaseAdmissibleU` adds it to W1's base admissibility on `fill U`.

A filling is a table per unsaid predicate over a base structure; `withFill` reads
it on typed tuples only, so every filling of an admissible base structure is
admissible for `E‴_base`. The evaluation lemmas read `Fill_T` through `canon`
(soft's canonical interpretation of the layer symbols), where `fill_decides` says
the synthetic rule's value is the filling at the gap:
`canonical_fill_sat` (the filling "true on permission members, false elsewhere"
satisfies `Fill_T`) and `fill_extends` (`Fill_T` constrains only the tables of pair
members) follow from one pointwise argument, `fill_sat_of`. -/
namespace VE.NormDefaults
open VE.Norms VE.Route
open VE.SoftNorms (canon canon_subst canon_off)
universe u

/-- `gap_p` (2.4): author rules only, substituted on `fill U`; `.bottom` unless `p ∈ U.unspec`. -/
def gapF (U : UDoc) (p : String) : VE.Formula :=
  if p ∈ U.unspec then
    .and (.not (subst (fill U).T (before (fill U) p) (pos U.D.T p)))
         (.not (subst (fill U).T (before (fill U) p) (neg U.D.T p)))
  else .bottom

/-- `default reached` (3.2) for any regulated `p`, deny/allow included: `gapF`'s
`.and` body without its `unspec` test. -/
def reachedF (U : UDoc) (p : String) : VE.Formula :=
  .and (.not (subst (fill U).T (before (fill U) p) (pos U.D.T p)))
       (.not (subst (fill U).T (before (fill U) p) (neg U.D.T p)))

def fillPremises (U : UDoc) : List VE.Formula :=
  ((pairs U.D.T).filter (fun pr => pr.req ∈ U.unspec ∨ pr.perm ∈ U.unspec)).map fun pr =>
    bindAll pr.sorts (.not (.and (pairConflict (fill U) pr) (.or (gapF U pr.req) (gapF U pr.perm))))

def BaseAdmissibleU (U : UDoc) (B : VE.Structure.{u}) : Prop :=
  BaseAdmissible (fill U) B ∧ Sat B (fillPremises U)

def ConflictFreeU (U : UDoc) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleU U B → ConflictFree (fill U) B

/-- Unsaid tables over `B`'s carrier, indexed by the unsaid predicate names. -/
def FillTables (_U : UDoc) (B : VE.Structure.{u}) : Type u := String → List B.Carrier → Prop

/-- `B` extended by the unsaid tables, read on typed tuples; `B.Carrier` is kept
definitionally. -/
def withFill (U : UDoc) (B : VE.Structure.{u}) (F : FillTables U B) : VE.Structure.{u} :=
  { B with relation := fun n vs => match U.unspec.find? (fun p => unsaidName p == n) with
      | some p => F n vs ∧ VE.TupleTyped B (sortsOf U.D p) vs
      | none => B.relation n vs }

/-- True on the permission members of declared pairs, false elsewhere. -/
def canonicalFill (U : UDoc) (B : VE.Structure.{u}) : FillTables U B :=
  fun n _ => ∃ pr ∈ pairs U.D.T, pr.perm ∈ U.unspec ∧ n = unsaidName pr.perm

/-- The canonical expansion of a filling with the unsaid tables forgotten. -/
def expandFill (U : UDoc) (B : VE.Structure.{u}) (F : FillTables U B) : VE.Structure.{u} :=
  forget (unsaidNames U) (canon (fill U) (withFill U B F))

/-! ## Conservativity and the conflict iff -/

theorem fillPremises_nil (U : UDoc) (h0 : U.unspec = []) : fillPremises U = [] := by
  simp [fillPremises, h0]

/-- `fill_conservative`: without unspecified predicates `fill` is the identity and
`Fill_T` is empty. -/
theorem fill_conservative (U : UDoc) (h0 : U.unspec = []) : fill U = U.D ∧ fillPremises U = [] :=
  ⟨fill_eq_self U h0, fillPremises_nil U h0⟩

/-- `conflictFreeU_iff`: W1's pointwise iff, instantiated: conflict-free under every
admissible filling is a unique filled expansion under every admissible filling. -/
theorem conflictFreeU_iff (U : UDoc) (h : WellFormedU U = true) :
    ConflictFreeU.{u} U ↔ ∀ B : VE.Structure.{u}, BaseAdmissibleU U B → Unique (DocumentExpansion (fill U) B) :=
  ⟨fun hc B hB => (conflictFree_expands_document (fill U) (fill_wellFormed U h) B hB.1).mpr (hc B hB),
   fun hu B hB => (conflictFree_expands_document (fill U) (fill_wellFormed U h) B hB.1).mp (hu B hB)⟩

/-! ## Fillings -/

theorem withFill_unsaid (U : UDoc) (B : VE.Structure.{u}) (F : FillTables U B) {p : String} (hp : p ∈ U.unspec)
    (vs : List B.Carrier) :
    (withFill U B F).relation (unsaidName p) vs ↔ F (unsaidName p) vs ∧ VE.TupleTyped B (sortsOf U.D p) vs := by
  simp only [withFill]
  cases hf : U.unspec.find? (fun q => unsaidName q == unsaidName p) with
  | none => exact absurd hp fun hp => List.find?_eq_none.mp hf p hp (by simp)
  | some q =>
    have := unsaidName_inj (by simpa using List.find?_some hf)
    subst this
    exact Iff.rfl

theorem withFill_off (U : UDoc) (B : VE.Structure.{u}) (F : FillTables U B) {n : String} (hn : n ∉ unsaidNames U)
    (vs : List B.Carrier) : (withFill U B F).relation n vs ↔ B.relation n vs := by
  simp only [withFill]
  rw [show U.unspec.find? (fun p => unsaidName p == n) = none from
    List.find?_eq_none.mpr fun p hp he => hn (List.mem_map.mpr ⟨p, hp, by simpa using he⟩)]

theorem sat_literals_relation (lits : List String) (S : VE.Structure.{u}) (R : String → List S.Carrier → Prop) :
    Sat { S with relation := R } (VE.Route.Background.literals lits) ↔ Sat S (VE.Route.Background.literals lits) := by
  simp only [Sat, VE.Route.Background.literals, List.mem_map, forall_exists_index, and_imp,
    forall_apply_eq_imp_iff₂, VE.Route.Background.literalPremise_denote]

section Fillings
variable {U : UDoc} (hu : UValid U)
include hu

/-- Every filling of an admissible base structure is admissible for `E‴_base`. -/
theorem withFill_baseAdmissible {B : VE.Structure.{u}} (hB : BaseAdmissible U.D B) (F : FillTables U B) :
    BaseAdmissible (fill U) (withFill U B F) := by
  refine ⟨⟨fun c s hc => hB.1.1 c s hc, fun n vs hn => ?_⟩, ?_⟩
  · by_cases hun : n ∈ unsaidNames U
    · obtain ⟨p, hp, rfl⟩ := List.mem_map.mp hun
      obtain ⟨_, ht⟩ := (withFill_unsaid U B F hp vs).mp hn
      exact ⟨_, envAt_fill_unsaid hu 0 hp, (tupleTyped_relation B _ _ vs).mpr ht⟩
    · obtain ⟨ss, hss, ht⟩ := hB.1.2 n vs ((withFill_off U B F hun vs).mp hn)
      exact ⟨ss, envAt_fill_mono hu 0 n ss hss, (tupleTyped_relation B _ _ vs).mpr ht⟩
  · exact (sat_literals_relation U.D.lits B _).mpr hB.2

/-- Forgetting the unsaid tables of a filling gives back the base structure. -/
theorem forget_withFill {B : VE.Structure.{u}} (hB : B.Admissible (envAt U.D 0)) (F : FillTables U B) :
    forget (unsaidNames U) (withFill U B F) = B := by
  cases B with
  | mk C d c rel =>
    simp only [forget, withFill, VE.Structure.mk.injEq, heq_eq_eq, true_and]
    funext n vs
    apply propext
    by_cases hn : n ∈ unsaidNames U
    · simp only [hn, not_true_eq_false, false_and, false_iff]
      intro hr
      obtain ⟨ss, hss, _⟩ := hB.2 n vs hr
      obtain ⟨p, hp, rfl⟩ := List.mem_map.mp hn
      have : (envAt U.D 0).predicates (unsaidName p) = none := by
        simp only [envAt, hide]
        split
        · rfl
        · exact hu.freshPred p hp
      rw [this] at hss
      cases hss
    · have := withFill_off U ⟨C, d, c, rel⟩ F hn vs
      simp only [withFill] at this
      simp only [hn, not_false_eq_true, true_and]
      exact this

theorem before_fill (p : String) : before (fill U) p = before U.D p := by
  simp only [before, layerNames_fill hu]

omit hu in
/-- `O_q‴°` at a base structure is `q`'s completed outcome on `T‴` at `canon`. -/
theorem outcomeBase_fill (h : WellFormedU U = true) {B : VE.Structure.{u}} (hc : ConstantsTyped (fill U) B)
    {q : Regulated} (hq : q ∈ U.D.T.regulated) (vs : List B.Carrier) (hvs : VE.TupleTyped B q.sorts vs) :
    (outcomeBase (fill U) q.name).denote B (tupleVal vs) ↔
      (if q.allowByDefault then ¬ DecidesD (fill U).T (canon (fill U) B) (tupleVal vs) q.name false
       else DecidesD (fill U).T (canon (fill U) B) (tupleVal vs) q.name true) := by
  have hv' := valid_of_wellFormed _ (fill_wellFormed U h)
  have hk := index_before hv' (show q ∈ (fill U).T.regulated from hq)
  have hT := rulesTyped_of_valid hv' hk
  simp only [outcomeBase, find_regulated hv' hk]
  rw [canon_subst hv' B hc _ _ _ (outcome_wellFormed hT) _ (tupleVal_typed B _ vs hvs), outcome_denote, pos, neg,
    decides_denote, decides_denote]

/-- `gap_p` at a base structure: no author rule on `p` decides at `canon`. -/
theorem gapF_fill (h : WellFormedU U = true) {B : VE.Structure.{u}} (hc : ConstantsTyped (fill U) B)
    {r : Regulated} (hr : r ∈ U.D.T.regulated) (hp : r.name ∈ U.unspec) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B r.sorts vs) :
    (gapF U r.name).denote B (tupleVal vs) ↔
      ¬ DecidesD U.D.T (canon (fill U) B) (tupleVal vs) r.name true ∧
        ¬ DecidesD U.D.T (canon (fill U) B) (tupleVal vs) r.name false := by
  have hv' := valid_of_wellFormed _ (fill_wellFormed U h)
  have hk := index_before hu.valid hr
  have hT := rulesTyped_of_valid hu.valid hk
  have hmono : ∀ sign, (decides U.D.T r.name sign).WellFormed (envAt (fill U) (before U.D r.name))
      r.sorts.reverse := fun sign => by
    rw [← VE.check_iff_wellFormed]
    exact check_envAt_fill hu ((VE.check_iff_wellFormed _ _ _).mpr (decides_wellFormed hT sign))
  have hρ := tupleVal_typed B _ vs hvs
  simp only [gapF, hp, if_true, VE.Formula.denote, before_fill hu, pos, neg]
  rw [canon_subst hv' B hc _ _ _ (hmono true) _ hρ, canon_subst hv' B hc _ _ _ (hmono false) _ hρ,
    decides_denote, decides_denote]

/-- At a gap, the outcome of an unspecified predicate is its filling. -/
theorem outcome_at_gap (h : WellFormedU U = true) {B : VE.Structure.{u}} (hc : ConstantsTyped (fill U) B)
    {r : Regulated} (hr : r ∈ U.D.T.regulated) (hp : r.name ∈ U.unspec) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B r.sorts vs) (hg : (gapF U r.name).denote B (tupleVal vs)) :
    (outcomeBase (fill U) r.name).denote B (tupleVal vs) ↔ B.relation (unsaidName r.name) vs := by
  obtain ⟨r', hr', hrn, hra⟩ := hu.declared _ hp
  have hrr := hu.regulated_eq hr' hr hrn
  subst hrr
  rw [outcomeBase_fill h hc hr' vs hvs, hra, if_neg (by simp), (fill_decides U h _ hp _ _).1,
    sortsOf_reg hu hr']
  obtain ⟨hP, hN⟩ := (gapF_fill hu h hc hr' hp vs hvs).mp hg
  have ha := (hu.ok.2.2.1 r' hr').2.1
  have hnl : unsaidName r'.name ∉ layerNames (fill U).T := by
    rw [layerNames_fill hu]
    intro hm
    obtain ⟨ss, hss⟩ := layer_declared hu hm
    rw [hu.freshPred _ hp] at hss
    cases hss
  rw [atom_denote (canon (fill U) B) _ _ ha vs ((tupleTyped_relation B _ _ vs).mpr hvs), canon_off B hnl vs]
  simp [hP, hN]

omit hu in
theorem pair_req {pr : Pair} (hpr : pr ∈ pairs U.D.T) :
    ∃ r ∈ U.D.T.regulated, r.name = pr.req ∧ r.role = .obligation ∧ r.permission = some pr.perm ∧
      r.sorts = pr.sorts := by
  simp only [pairs, mem_sortBy, List.mem_filterMap] at hpr
  obtain ⟨r, hr, he⟩ := hpr
  split at he
  · rename_i hro hrp
    cases he
    exact ⟨r, hr, rfl, hro, hrp, rfl⟩
  · cases he

theorem pair_perm {pr : Pair} (hpr : pr ∈ pairs U.D.T) :
    ∃ m ∈ U.D.T.regulated, m.name = pr.perm ∧ m.role = .permission ∧ m.sorts = pr.sorts := by
  obtain ⟨r, hr, _, hro, hrp, _⟩ := pair_req hpr
  obtain ⟨m, hm, hmr⟩ := actChecks_dual hu.ok.2.2.2.1 hr hro hrp
  obtain ⟨_, _, ⟨m', hm', hm'n, hm's⟩⟩ := hu.valid.pairs pr hpr
  have hmn : m.name = pr.perm := by simpa using List.find?_some hm
  have := hu.regulated_eq (List.mem_of_find?_eq_some hm) (mem_syms_reg hm') (hmn.trans hm'n.symm)
  subst this
  exact ⟨m, List.mem_of_find?_eq_some hm, hmn, hmr, hm's⟩

/-- No predicate is both the obligation and the permission member of declared pairs. -/
theorem pair_roles {pr pr' : Pair} (hpr : pr ∈ pairs U.D.T) (hpr' : pr' ∈ pairs U.D.T) : pr.req ≠ pr'.perm := by
  intro e
  obtain ⟨r, hr, hrn, hro, _⟩ := pair_req hpr
  obtain ⟨m, hm, hmn, hmr, _⟩ := pair_perm hu hpr'
  have := hu.regulated_eq hr hm (hrn.trans (e.trans hmn.symm))
  subst this
  rw [hro] at hmr
  cases hmr

/-- `Fill_T` holds wherever the permission members' gaps are filled "yes" and the
obligation members' gaps "no". -/
theorem fill_sat_of (h : WellFormedU U = true) {B : VE.Structure.{u}} (hB : BaseAdmissible (fill U) B)
    (hperm : ∀ pr ∈ pairs U.D.T, pr.perm ∈ U.unspec → ∀ vs, VE.TupleTyped B pr.sorts vs →
      B.relation (unsaidName pr.perm) vs)
    (hreq : ∀ pr ∈ pairs U.D.T, pr.req ∈ U.unspec → ∀ vs, VE.TupleTyped B pr.sorts vs →
      ¬ B.relation (unsaidName pr.req) vs) :
    Sat B (fillPremises U) := by
  intro a ha
  obtain ⟨pr, hpr, rfl⟩ := List.mem_map.mp ha
  have hpr := (List.mem_filter.mp hpr).1
  rw [bindAll_denote_nil]
  intro vs hvs
  have hc : ConstantsTyped (fill U) B := hB.1.1
  obtain ⟨r, hr, hrn, _, _, hrs⟩ := pair_req hpr
  obtain ⟨m, hm, hmn, _, hms⟩ := pair_perm hu hpr
  simp only [VE.Formula.denote, pairConflict]
  rintro ⟨⟨hOr, hnOm⟩, hg⟩
  rcases hg with hg | hg
  · by_cases hp : pr.req ∈ U.unspec
    · rw [← hrn] at hg hOr hp
      have := (outcome_at_gap hu h hc hr hp vs (hrs ▸ hvs) hg).mp hOr
      exact hreq pr hpr (hrn ▸ hp) vs hvs (hrn ▸ this)
    · simp [gapF, hp, VE.Formula.denote] at hg
  · by_cases hp : pr.perm ∈ U.unspec
    · rw [← hmn] at hg hnOm hp
      exact hnOm ((outcome_at_gap hu h hc hm hp vs (hms ▸ hvs) hg).mpr (hmn ▸ hperm pr hpr (hmn ▸ hp) vs hvs))
    · simp [gapF, hp, VE.Formula.denote] at hg

end Fillings

/-- `canonical_fill_sat`: the filling "true for permission members of pairs, false
elsewhere" satisfies `Fill_T` in every base situation. -/
theorem canonical_fill_sat (U : UDoc) (h : WellFormedU U = true) (B : VE.Structure.{u})
    (hB : BaseAdmissible U.D B) : BaseAdmissibleU U (withFill U B (canonicalFill U B)) := by
  have hu := uvalid h
  have hB' := withFill_baseAdmissible hu hB (canonicalFill U B)
  refine ⟨hB', fill_sat_of hu h hB' (fun pr hpr hp vs hvs => ?_) (fun pr hpr hp vs hvs => ?_)⟩
  · obtain ⟨m, hm, hmn, _, hms⟩ := pair_perm hu hpr
    refine (withFill_unsaid U B _ hp vs).mpr ⟨⟨pr, hpr, hp, rfl⟩, ?_⟩
    rw [← hmn, sortsOf_reg hu hm, hms]
    exact (tupleTyped_relation B _ _ vs).mp hvs
  · intro hrel
    obtain ⟨⟨pr', hpr', _, he⟩, _⟩ := (withFill_unsaid U B _ hp vs).mp hrel
    exact pair_roles hu hpr hpr' (unsaidName_inj he)

/-- `fill_extends`: `Fill_T` constrains only the unsaid tables of pair members. -/
theorem fill_extends (U : UDoc) (h : WellFormedU U = true) (B : VE.Structure.{u}) (hB : BaseAdmissible U.D B)
    (F : FillTables U B) :
    ∃ F' : FillTables U B, (∀ p, p ∉ (pairMembers U).map unsaidName → F' p = F p) ∧
      BaseAdmissibleU U (withFill U B F') := by
  have hu := uvalid h
  classical
  let F' : FillTables U B := fun n vs =>
    if n ∈ (pairMembers U).map unsaidName then canonicalFill U B n vs else F n vs
  have hB' := withFill_baseAdmissible hu hB F'
  have hmem : ∀ pr ∈ pairs U.D.T, (pr.req ∈ U.unspec ∨ pr.perm ∈ U.unspec) →
      unsaidName pr.req ∈ (pairMembers U).map unsaidName ∧ unsaidName pr.perm ∈ (pairMembers U).map unsaidName := by
    intro pr hpr ho
    have hop : pr ∈ openPairs U := List.mem_filter.mpr ⟨hpr, by simpa using ho⟩
    exact ⟨List.mem_map.mpr ⟨pr.req, List.mem_flatMap.mpr ⟨pr, hop, by simp⟩, rfl⟩,
      List.mem_map.mpr ⟨pr.perm, List.mem_flatMap.mpr ⟨pr, hop, by simp⟩, rfl⟩⟩
  refine ⟨F', fun p hp => funext fun vs => by
      show (if p ∈ (pairMembers U).map unsaidName then canonicalFill U B p vs else F p vs) = F p vs
      rw [if_neg hp], hB',
    fill_sat_of hu h hB' (fun pr hpr hp vs hvs => ?_) (fun pr hpr hp vs hvs => ?_)⟩
  · obtain ⟨m, hm, hmn, _, hms⟩ := pair_perm hu hpr
    refine (withFill_unsaid U B _ hp vs).mpr ⟨?_, ?_⟩
    · simp only [F', (hmem pr hpr (Or.inr hp)).2, if_true]
      exact ⟨pr, hpr, hp, rfl⟩
    · rw [← hmn, sortsOf_reg hu hm, hms]
      exact (tupleTyped_relation B _ _ vs).mp hvs
  · intro hrel
    obtain ⟨hF, _⟩ := (withFill_unsaid U B _ hp vs).mp hrel
    simp only [F', (hmem pr hpr (Or.inl hp)).1, if_true] at hF
    obtain ⟨pr', hpr', _, he⟩ := hF
    exact pair_roles hu hpr hpr' (unsaidName_inj he)

end VE.NormDefaults
