import VE.NormDefaults.Premises

/-! Expansions, statuses and their meaning (docs/spec/norm-defaults.md 2.2, 2.5, 5
and 7): `fill_expansions` (adequacy: the source expansions are exactly the filled
W1 expansions with the unsaid tables forgotten), `conflictFreeU_consistent`, the
status theorems `settled_expansions`, `settled_all_expansions` and
`undecided_expansions`, and `unreached_switch`.

Two structures that differ only on the unsaid tables satisfy the same Background,
the same `IntendedAt3` and the same author decisions (`sat_background_congr`,
`intendedAt3_congr`), because none of those formulas mentions an unsaid predicate.
The filling read off a source expansion `S` is `fillOf U S` (`unsaid__p := p`). -/
namespace VE.NormDefaults
open VE.Norms VE.Route
open VE.SoftNorms (canon canon_off)
universe u

/-! ## Formulas that do not mention the unsaid tables -/

theorem denote_congr_preds (X : VE.Structure.{u}) (R : String → List X.Carrier → Prop) :
    ∀ (φ : VE.Formula) (ρ : VE.Valuation X), (∀ p ∈ preds φ, ∀ vs, R p vs ↔ X.relation p vs) →
      (φ.denote { X with relation := R } ρ ↔ φ.denote X ρ) := by
  intro φ
  induction φ with
  | top | bottom => intros; exact Iff.rfl
  | unary p t =>
    intro ρ h
    simp only [VE.Formula.denote, VE.Term.denote, h p (by simp [preds])]
  | binary p t w =>
    intro ρ h
    simp only [VE.Formula.denote, VE.Term.denote, h p (by simp [preds])]
  | eq t w => intros; exact Iff.rfl
  | not a ih =>
    intro ρ h
    simp only [VE.Formula.denote]; rw [ih ρ (by simpa [preds] using h)]
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro ρ h
    simp only [VE.Formula.denote]
    rw [ia ρ (fun p hp => h p (by simp [preds, hp])), ib ρ (fun p hp => h p (by simp [preds, hp]))]
  | all s a ih | ex s a ih =>
    intro ρ h
    simp only [VE.Formula.denote]
    first
    | exact forall_congr' fun v => imp_congr_right fun _ => ih (v :: ρ) (by simpa [preds] using h)
    | exact exists_congr fun v => and_congr_right fun _ => ih (v :: ρ) (by simpa [preds] using h)

theorem denote_rel_iff (X : VE.Structure.{u}) (R₁ R₂ : String → List X.Carrier → Prop)
    (h : ∀ n vs, R₁ n vs ↔ R₂ n vs) (φ : VE.Formula) (ρ : VE.Valuation X) :
    φ.denote { X with relation := R₁ } ρ ↔ φ.denote { X with relation := R₂ } ρ := by
  have : R₁ = R₂ := funext fun n => funext fun vs => propext (h n vs)
  subst this
  exact Iff.rfl

theorem preds_bindAll (ss : List String) (φ : VE.Formula) : preds (bindAll ss φ) = preds φ := by
  induction ss with
  | nil => rfl
  | cons s ss ih => exact ih

theorem preds_atom_sub (p : String) (ss : List String) : ∀ x ∈ preds (atom p ss), x = p := by
  intro x hx
  unfold atom at hx
  split at hx <;> simp_all [preds]

section Congr
variable {U : UDoc} (hu : UValid U)
include hu

/-- Every predicate in Background is declared in `E`. -/
theorem background_declared : ∀ φ ∈ background U.D, ∀ x ∈ preds φ, ∃ ss, U.D.E.predicates x = some ss := by
  intro φ hφ x hx
  simp only [background, List.mem_append] at hφ
  rcases hφ with (hφ | hφ) | hφ
  · simp only [definitionPremises, List.mem_filterMap] at hφ
    obtain ⟨q, hq, he⟩ := hφ
    cases q with
    | reg _ => cases he
    | defn d =>
      simp only [Option.some.injEq] at he
      subst he
      obtain ⟨h1, _, _, _, h5⟩ := hu.ok.2.2.2.2.1 d (mem_syms_defn hq)
      have hx' : x ∈ preds (atom d.name d.args) ∨ x ∈ preds d.body := by
        simp only [Definition.premise, preds_bindAll, iffF, preds, List.mem_append] at hx
        rcases hx with (hx | hx) | (hx | hx)
        · exact Or.inl hx
        · exact Or.inr hx
        · exact Or.inr hx
        · exact Or.inl hx
      rcases hx' with hx' | hx'
      · rw [preds_atom_sub _ _ x hx']; exact ⟨_, h1⟩
      · exact preds_declared d.body _ ((VE.check_iff_wellFormed _ _ _).mp h5) x hx'
  · simp only [backgroundBase, VE.Route.Background.literals, List.mem_map] at hφ
    obtain ⟨pp, _, rfl⟩ := hφ
    simp [VE.Route.Background.literalPremise, preds] at hx
  · simp only [pairPremises, List.mem_map] at hφ
    obtain ⟨pr, hpr, rfl⟩ := hφ
    simp only [Pair.premise, preds_bindAll, preds, List.mem_append] at hx
    rcases hx with hx | hx
    · rw [preds_atom_sub _ _ x hx]
      obtain ⟨r, hr, hrn, _⟩ := pair_req hpr
      exact ⟨_, hrn ▸ hu.declared_pred hr⟩
    · rw [preds_atom_sub _ _ x hx]
      obtain ⟨m, hm, hmn, _⟩ := pair_perm hu hpr
      exact ⟨_, hmn ▸ hu.declared_pred hm⟩

theorem sat_background_congr (X : VE.Structure.{u}) (R : String → List X.Carrier → Prop)
    (hR : ∀ n, n ∉ unsaidNames U → ∀ vs, R n vs ↔ X.relation n vs) :
    Sat { X with relation := R } (background U.D) ↔ Sat X (background U.D) := by
  have key : ∀ φ ∈ background U.D, (φ.denote { X with relation := R } [] ↔ φ.denote X []) := fun φ hφ =>
    denote_congr_preds X R φ [] fun p hp vs => by
      obtain ⟨ss, hss⟩ := background_declared hu φ hφ p hp
      exact hR p (hu.not_unsaid hss) vs
  exact ⟨fun h' a ha => (key a ha).mp (h' a ha), fun h' a ha => (key a ha).mpr (h' a ha)⟩

theorem unsaid_undeclared (k : Nat) : ∀ n ∈ unsaidNames U, (envAt U.D k).predicates n = none := by
  intro n hn
  obtain ⟨p, hp, rfl⟩ := List.mem_map.mp hn
  simp only [envAt, hide]
  split
  · rfl
  · exact hu.freshPred p hp

theorem decides_congr {r : Regulated} (hr : r ∈ U.D.T.regulated) (X : VE.Structure.{u})
    (R : String → List X.Carrier → Prop) (hR : ∀ n, n ∉ unsaidNames U → ∀ vs, R n vs ↔ X.relation n vs)
    (ρ : VE.Valuation X) (sign : Bool) :
    DecidesD U.D.T (forget [r.name] { X with relation := R }) ρ r.name sign ↔
      DecidesD U.D.T (forget [r.name] X) ρ r.name sign := by
  rw [← decides_denote, ← decides_denote]
  obtain ⟨k, hk⟩ := mem_syms_index (hu.valid.regulated r hr)
  exact denote_relation_congr (unsaid_undeclared hu k) (forget [r.name] X) (fun n vs => n ∉ [r.name] ∧ R n vs)
    (fun n vs hn => by simp only [forget]; rw [hR n hn vs]) _ _ _
    (decides_wellFormed (rulesTyped_of_valid hu.valid hk) sign)

theorem intendedAt3_congr {r : Regulated} (hr : r ∈ U.D.T.regulated) (X : VE.Structure.{u})
    (R : String → List X.Carrier → Prop) (hR : ∀ n, n ∉ unsaidNames U → ∀ vs, R n vs ↔ X.relation n vs) :
    IntendedAt3 U r { X with relation := R } ↔ IntendedAt3 U r X := by
  unfold IntendedAt3
  apply forall_congr'
  intro vs
  rw [tupleTyped_relation]
  apply imp_congr_right
  intro _
  have hv : Value3 U r (forget [r.name] { X with relation := R }) vs = Value3 U r (forget [r.name] X) vs := by
    unfold Value3
    rw [propext (decides_congr hu hr X R hR _ true), propext (decides_congr hu hr X R hR _ false)]
  rw [hv]
  have hrel : R r.name vs ↔ X.relation r.name vs := hR _ (hu.not_unsaid (hu.declared_pred hr)) vs
  cases Value3 U r (forget [r.name] X) vs <;> simp only [hrel]

theorem background_fill : background (fill U) = background U.D := by
  simp only [background, definitionPremises, syms_fill hu]
  rfl

end Congr

/-! ## Adequacy -/

/-- The filling read off a source expansion: `unsaid__p := p`. -/
def fillOf (U : UDoc) (S : VE.Structure.{u}) : FillTables U S :=
  fun n vs => ∃ p ∈ U.unspec, n = unsaidName p ∧ S.relation p vs

section Adequacy
variable {U : UDoc} (hu : UValid U)
include hu

theorem size_fill : size (fill U) = size U.D := by
  simp only [size, syms_fill hu]

omit hu in
theorem withFill_agrees (X : VE.Structure.{u}) (F : FillTables U X) :
    ∀ n, n ∉ unsaidNames U → ∀ vs, (withFill U X F).relation n vs ↔ X.relation n vs :=
  fun _ hn vs => withFill_off U X F hn vs

omit hu in
theorem forget_agrees (X : VE.Structure.{u}) :
    ∀ n, n ∉ unsaidNames U → ∀ vs, (forget (unsaidNames U) X).relation n vs ↔ X.relation n vs :=
  fun _ hn vs => forget_relation X hn vs

omit hu in
/-- In a filled expansion, `Fill_T` holds: the pair premise holds in the expansion. -/
theorem fillPremises_of_expansion (h : WellFormedU U = true) {S : VE.Structure.{u}}
    (hB : BaseAdmissible (fill U) (restrictAll (fill U).T S))
    (hE : DocumentExpansion (fill U) (restrictAll (fill U).T S) S) :
    Sat (restrictAll (fill U).T S) (fillPremises U) := by
  have hv' := valid_of_wellFormed _ (fill_wellFormed U h)
  obtain ⟨_, hpa⟩ := (documentExpansion_iff hv' _ S hB).mp hE
  obtain ⟨hA, _, hM, hP⟩ := (prefix_char hv' _ (Nat.le_refl _) S).mp hpa
  have hc : ConstantsTyped (fill U) S := hA.1
  intro a ha
  obtain ⟨pr, hpr, rfl⟩ := List.mem_map.mp ha
  have hpr : pr ∈ pairs (fill U).T := (List.mem_filter.mp hpr).1
  rw [bindAll_denote_nil]
  intro vs hvs ⟨⟨ho, hno⟩, _⟩
  rw [tupleTyped_restrictAll] at hvs
  obtain ⟨_, ⟨i, r, hi, hrn, hrs, _⟩, ⟨j, m, hj, hmn, hms, _⟩⟩ := pair_members hv' hpr
  have hil := (List.getElem?_eq_some_iff.mp hi).1
  have hjl := (List.getElem?_eq_some_iff.mp hj).1
  rw [← hrn] at ho
  rw [← hmn] at hno
  have h₁ := (outcomeBase_relation hv' hi hil S hc hM vs (by rwa [hrs])).mp ho
  have h₂ := (pair_premise_iff pr (pair_arity hv' hpr) S).mp
    (hP pr hpr (pair_closes_lt_size hv' hpr)) vs hvs (hrn ▸ h₁)
  exact hno ((outcomeBase_relation hv' hj hjl S hc hM vs (by rwa [hms])).mpr (hmn ▸ h₂))

/-- The filled W1 expansion of a source expansion. -/
theorem expansion_filled (h : WellFormedU U = true) {B S : VE.Structure.{u}} (hS : Expansion3 U B S) :
    BaseAdmissibleU U (restrictAll (fill U).T (withFill U S (fillOf U S))) ∧
      DocumentExpansion (fill U) (restrictAll (fill U).T (withFill U S (fillOf U S))) (withFill U S (fillOf U S)) := by
  obtain ⟨_, hA, hbg, hint⟩ := hS
  have hw' := fill_wellFormed U h
  let S' := withFill U S (fillOf U S)
  have hA' : S'.Admissible (envAt (fill U) (size (fill U))) := by
    refine ⟨fun c s hc => hA.1 c s hc, fun n vs hn => ?_⟩
    rw [size_fill hu]
    by_cases hun : n ∈ unsaidNames U
    · obtain ⟨p, hp, rfl⟩ := List.mem_map.mp hun
      obtain ⟨_, ht⟩ := (withFill_unsaid U S _ hp vs).mp hn
      exact ⟨_, envAt_fill_unsaid hu _ hp, (tupleTyped_relation S _ _ vs).mpr ht⟩
    · obtain ⟨ss, hss, ht⟩ := hA.2 n vs ((withFill_off U S _ hun vs).mp hn)
      exact ⟨ss, envAt_fill_mono hu _ n ss hss, (tupleTyped_relation S _ _ vs).mpr ht⟩
  have hbg' : Sat S' (background (fill U)) := by
    rw [background_fill hu]
    exact (sat_background_congr hu S _ (withFill_agrees S _)).mpr hbg
  have hel : Sat S' (elaborate (fill U).T) := by
    intro a ha
    apply (elaborate_iff (fill U) hw' S').mpr _ a ha
    intro r hr
    refine (fill_intended U h r hr S').mpr ⟨(intendedAt3_congr hu hr S _ (withFill_agrees S _)).mpr (hint r hr),
      fun hp vs hvs _ => ?_⟩
    have hrel : S'.relation r.name vs ↔ S.relation r.name vs :=
      withFill_off U S _ (hu.not_unsaid (hu.declared_pred hr)) vs
    rw [hrel, withFill_unsaid U S _ hp vs, sortsOf_reg hu hr]
    have hvs' : VE.TupleTyped S r.sorts vs := (tupleTyped_relation S _ _ vs).mp hvs
    constructor
    · intro hs; exact ⟨⟨r.name, hp, rfl, hs⟩, hvs'⟩
    · rintro ⟨⟨q, _, hq, hs⟩, _⟩
      rwa [unsaidName_inj hq]
  have hE : DocumentExpansion (fill U) (restrictAll (fill U).T S') S' :=
    ⟨rfl, hA', fun a ha => by
      rcases List.mem_append.mp ha with ha | ha
      · exact hbg' a ha
      · exact hel a ha⟩
  have hB' : BaseAdmissible (fill U) (restrictAll (fill U).T S') := by
    refine ⟨restrictAll_admissible _ S' hA', (sat_literals_forget _ _ S').mpr fun a ha => hbg' a ?_⟩
    simp only [background, backgroundBase, List.mem_append] at ha ⊢
    exact Or.inl (Or.inr ha)
  exact ⟨⟨hB', fillPremises_of_expansion h hB' hE⟩, hE⟩

theorem restrictAll_forget_unsaid (S : VE.Structure.{u}) :
    restrictAll U.D.T (forget (unsaidNames U) S) = forget (unsaidNames U) (restrictAll (fill U).T S) := by
  unfold restrictAll
  rw [forget_forget, forget_forget, layerNames_fill hu]
  apply forget_congr
  intro r
  simp only [List.mem_append]
  exact or_comm

end Adequacy

/-- `fill_expansions` (adequacy): the source expansions are exactly the filled W1
expansions with the unsaid tables forgotten. -/
theorem fill_expansions (U : UDoc) (h : WellFormedU U = true) (B : VE.Structure.{u}) (hB : BaseAdmissible U.D B)
    (S : VE.Structure.{u}) :
    Expansion3 U B S ↔
      restrictAll U.D.T S = B ∧
      ∃ S' : VE.Structure.{u}, forget (unsaidNames U) S' = S ∧
        BaseAdmissibleU U (restrictAll (fill U).T S') ∧
        DocumentExpansion (fill U) (restrictAll (fill U).T S') S' := by
  have _ := hB
  have hu := uvalid h
  have hw' := fill_wellFormed U h
  constructor
  · intro hS
    obtain ⟨hBU, hE⟩ := expansion_filled hu h hS
    exact ⟨hS.1, _, forget_withFill hu hS.2.1 _, hBU, hE⟩
  · rintro ⟨hrs, S', rfl, _, hE⟩
    obtain ⟨_, hA', hsat⟩ := hE
    refine ⟨hrs, ⟨fun c s hc => hA'.1 c s hc, fun n vs hn => ?_⟩, ?_, fun r hr => ?_⟩
    · obtain ⟨hnu, hn⟩ := hn
      obtain ⟨ss, hss, ht⟩ := hA'.2 n vs hn
      refine ⟨ss, ?_, (tupleTyped_forget _ S' ss vs).mpr ht⟩
      rw [envAt_size_predicates] at hss ⊢
      rwa [fill_E, fillEnv_off U hnu] at hss
    · have hbg : Sat S' (background U.D) := by
        rw [← background_fill hu]
        exact fun a ha => hsat a (List.mem_append_left _ ha)
      exact (sat_background_congr hu S' _ (forget_agrees S')).mpr hbg
    · have hint : IntendedAt (fill U).T r S' :=
        (elaborate_iff (fill U) hw' S').mp (fun a ha => hsat a (List.mem_append_right _ ha)) r hr
      exact (intendedAt3_congr hu hr S' _ (forget_agrees S')).mpr ((fill_intended U h r hr S').mp hint).1

/-- `conflictFreeU_consistent`: a CONFLICT-FREE document has an expansion in every
base situation (the text never contradicts itself, however it is filled). -/
theorem conflictFreeU_consistent (U : UDoc) (h : WellFormedU U = true) (hc : ConflictFreeU.{u} U)
    (B : VE.Structure.{u}) (hB : BaseAdmissible U.D B) : ∃ S, Expansion3 U B S := by
  have hu := uvalid h
  have hw' := fill_wellFormed U h
  have hBU := canonical_fill_sat U h B hB
  obtain ⟨S', hE, _⟩ := (conflictFree_expands_document (fill U) hw' _ hBU.1).mpr (hc _ hBU)
  have hr : restrictAll (fill U).T S' = withFill U B (canonicalFill U B) := hE.1
  refine ⟨forget (unsaidNames U) S', (fill_expansions U h B hB _).mpr ⟨?_, S', rfl, hr ▸ hBU, hr ▸ hE⟩⟩
  rw [restrictAll_forget_unsaid hu, hr, forget_withFill hu hB.1]

/-! ## Statuses -/

/-- Statuses (2.5) count every admissible filling, conflicting ones included. -/
def SettledAs (U : UDoc) (B : VE.Structure.{u}) (r : Regulated) (vs : List B.Carrier) (b : Bool) : Prop :=
  ∀ F : FillTables U B, BaseAdmissibleU U (withFill U B F) →
    ((outcomeBase (fill U) r.name).denote (withFill U B F) (tupleVal vs) ↔ b = true)

def UndecidedAt (U : UDoc) (B : VE.Structure.{u}) (r : Regulated) (vs : List B.Carrier) : Prop :=
  ∃ F₁ F₂ : FillTables U B,
    BaseAdmissibleU U (withFill U B F₁) ∧ BaseAdmissibleU U (withFill U B F₂) ∧
    (outcomeBase (fill U) r.name).denote (withFill U B F₁) (tupleVal vs) ∧
    ¬ (outcomeBase (fill U) r.name).denote (withFill U B F₂) (tupleVal vs)

/-- A W1 expansion is `canonTyped` of its base restriction. -/
theorem expansion_eq_canonTyped {D : Doc} (hv : Valid D) (S : VE.Structure.{u})
    (hB : BaseAdmissible D (restrictAll D.T S)) (hE : DocumentExpansion D (restrictAll D.T S) S) :
    S = canonTyped D (restrictAll D.T S) := by
  obtain ⟨_, hpa⟩ := (documentExpansion_iff hv _ S hB).mp hE
  obtain ⟨hA, _, hM, _⟩ := (prefix_char hv _ (Nat.le_refl _) S).mp hpa
  have hc : ConstantsTyped D S := hA.1
  have ha := agreesBelow_of_meanings hM
  have hrel : ∀ n vs, S.relation n vs ↔ (canonTyped D (restrictAll D.T S)).relation n vs := by
    intro n vs
    by_cases hn : n ∈ layerNames D.T
    · obtain ⟨j, hj⟩ := List.mem_iff_getElem?.mp hn
      obtain ⟨q, hq, rfl⟩ : ∃ q, (syms D.T)[j]? = some q ∧ q.name = n := by
        simp only [layerNames, List.getElem?_map, Option.map_eq_some_iff] at hj
        exact hj
      have hjl : j < size D := (List.getElem?_eq_some_iff.mp hq).1
      have hdecl := (hv.decl q (List.mem_of_getElem? hq)).1
      have hcanon : (canon D (restrictAll D.T S)).relation q.name vs ↔
          (subst D.T j (q.meaning D.T)).denote (restrictAll D.T S) (tupleVal vs) := by
        simp only [canon, expTable_at hv (size D) j q hjl hq]
        rfl
      simp only [canonTyped, hcanon]
      constructor
      · intro hs
        obtain ⟨ss, hss, ht⟩ := hA.2 _ vs hs
        rw [envAt_size_predicates, hdecl] at hss
        cases hss
        refine ⟨(subst_restrict_denote hv j S hc (fun j' q' hj' => ha j' q' (Nat.lt_trans hj' hjl)) _ _
          (meaning_wellFormed hv hq) _ (tupleVal_typed S _ vs ht)).mpr ((hM j q hjl hq vs ht).2.mp hs),
          fun _ => ⟨_, hdecl, (tupleTyped_forget _ S _ vs).mpr ht⟩⟩
      · rintro ⟨hm, hty⟩
        obtain ⟨ss, hss, ht⟩ := hty hn
        rw [hdecl] at hss
        cases hss
        have ht' : VE.TupleTyped S q.sorts vs := (tupleTyped_forget _ S _ vs).mp ht
        exact (hM j q hjl hq vs ht').2.mpr ((subst_restrict_denote hv j S hc
          (fun j' q' hj' => ha j' q' (Nat.lt_trans hj' hjl)) _ _ (meaning_wellFormed hv hq) _
          (tupleVal_typed S _ vs ht')).mp hm)
    · simp only [canonTyped, hn, false_implies, and_true]
      exact ((canon_off (restrictAll D.T S) hn vs).trans (forget_relation S hn vs)).symm
  cases S with
  | mk C d c rel =>
    simp only [canonTyped, restrictAll, forget, VE.Structure.mk.injEq, heq_eq_eq, true_and]
    funext n vs
    exact propext (hrel n vs)

/-- `canonTyped`'s relation of a regulated predicate at a typed tuple is its outcome
at the base. -/
theorem canonTyped_regulated {D : Doc} (hv : Valid D) (B : VE.Structure.{u}) {r : Regulated}
    (hr : r ∈ D.T.regulated) (vs : List B.Carrier) (hvs : VE.TupleTyped B r.sorts vs) :
    (canonTyped D B).relation r.name vs ↔ (outcomeBase D r.name).denote B (tupleVal vs) := by
  obtain ⟨k, hk⟩ := mem_syms_index (hv.regulated r hr)
  have hkl : k < size D := (List.getElem?_eq_some_iff.mp hk).1
  have hb : before D r.name = k := before_eq hv hk
  have hn : r.name ∈ layerNames D.T := name_mem_layerNames hk
  have hdecl := (hv.decl _ (List.mem_of_getElem? hk)).1
  have he : expTable D.T (size D) r.name = some (substWith (expTable D.T k) (outcome D.T r)) :=
    expTable_at hv (size D) k (.reg r) hkl hk
  simp only [canonTyped, canon, he, outcomeBase, find_regulated hv hk, hb]
  constructor
  · exact fun h => h.1
  · exact fun h => ⟨h, fun _ => ⟨_, hdecl, hvs⟩⟩

section Status
variable {U : UDoc} (hu : UValid U)
include hu

omit hu in
/-- The canonical expansion of an admissible conflict-free filling. -/
theorem canonTyped_expansion (h : WellFormedU U = true) {B : VE.Structure.{u}} {F : FillTables U B}
    (hF : BaseAdmissibleU U (withFill U B F)) (hcf : ConflictFree (fill U) (withFill U B F)) :
    DocumentExpansion (fill U) (withFill U B F) (canonTyped (fill U) (withFill U B F)) := by
  have hw' := fill_wellFormed U h
  have hv' := valid_of_wellFormed _ hw'
  obtain ⟨S', hE, _⟩ := (conflictFree_expands_document (fill U) hw' _ hF.1).mpr hcf
  have hr : restrictAll (fill U).T S' = withFill U B F := hE.1
  have heq : S' = canonTyped (fill U) (withFill U B F) := by
    rw [← hr]
    exact expansion_eq_canonTyped hv' S' (hr ▸ hF.1) (hr ▸ hE)
  exact heq ▸ hE

theorem expandFill_expansion (h : WellFormedU U = true) {B : VE.Structure.{u}} (hB : BaseAdmissible U.D B)
    {F : FillTables U B} (hF : BaseAdmissibleU U (withFill U B F)) (hcf : ConflictFree (fill U) (withFill U B F)) :
    Expansion3 U B (expandFill U B F) := by
  have hE := canonTyped_expansion h hF hcf
  have hr : restrictAll (fill U).T (canonTyped (fill U) (withFill U B F)) = withFill U B F := hE.1
  refine (fill_expansions U h B hB _).mpr ⟨?_, canonTyped (fill U) (withFill U B F), rfl,
    by rw [hr]; exact hF, by rw [hr]; exact hE⟩
  show restrictAll U.D.T (forget (unsaidNames U) (canonTyped (fill U) (withFill U B F))) = B
  rw [restrictAll_forget_unsaid hu, hr, forget_withFill hu hB.1]

theorem expandFill_relation (h : WellFormedU U = true) (B : VE.Structure.{u}) (F : FillTables U B)
    {r : Regulated} (hr : r ∈ U.D.T.regulated) (vs : List B.Carrier) (typed : VE.TupleTyped B r.sorts vs) :
    (expandFill U B F).relation r.name vs ↔ (outcomeBase (fill U) r.name).denote (withFill U B F) (tupleVal vs) := by
  have hv' := valid_of_wellFormed _ (fill_wellFormed U h)
  unfold expandFill
  rw [forget_relation (canonTyped (fill U) (withFill U B F)) (hu.not_unsaid (hu.declared_pred hr)) vs]
  exact canonTyped_regulated hv' (withFill U B F) hr vs ((tupleTyped_relation B _ _ vs).mpr typed)

omit hu in
/-- In a filled expansion, the relation at a typed tuple is the outcome at the base. -/
theorem relation_of_expansion (h : WellFormedU U = true) {S' : VE.Structure.{u}}
    (hB' : BaseAdmissible (fill U) (restrictAll (fill U).T S'))
    (hE : DocumentExpansion (fill U) (restrictAll (fill U).T S') S') {r : Regulated}
    (hr : r ∈ U.D.T.regulated) (vs : List S'.Carrier) (hvs : VE.TupleTyped S' r.sorts vs) :
    S'.relation r.name vs ↔ (outcomeBase (fill U) r.name).denote (restrictAll (fill U).T S') (tupleVal vs) := by
  have hv' := valid_of_wellFormed _ (fill_wellFormed U h)
  obtain ⟨_, hpa⟩ := (documentExpansion_iff hv' _ S' hB').mp hE
  obtain ⟨hA, _, hM, _⟩ := (prefix_char hv' _ (Nat.le_refl _) S').mp hpa
  obtain ⟨k, hk⟩ := mem_syms_index (hv'.regulated r hr)
  exact (outcomeBase_relation hv' hk (List.getElem?_eq_some_iff.mp hk).1 S' hA.1 hM vs hvs).symm

/-- The filled expansion's base is the source expansion's base with the filling. -/
theorem restrict_withFill_rel (S : VE.Structure.{u}) (F : FillTables U S) (n : String) (vs : List S.Carrier) :
    (restrictAll (fill U).T (withFill U S F)).relation n vs ↔ (withFill U (restrictAll U.D.T S) F).relation n vs := by
  by_cases hun : n ∈ unsaidNames U
  · obtain ⟨p, hp, rfl⟩ := List.mem_map.mp hun
    have hn : unsaidName p ∉ layerNames (fill U).T := by
      rw [layerNames_fill hu]
      intro hm
      obtain ⟨ss, hss⟩ := layer_declared hu hm
      rw [hu.freshPred p hp] at hss
      cases hss
    unfold restrictAll
    rw [forget_relation (withFill U S F) hn, withFill_unsaid U S F hp,
      withFill_unsaid U (forget (layerNames U.D.T) S) F hp]
    exact and_congr_right fun _ => (tupleTyped_forget _ S _ vs).symm
  · rw [withFill_off U (restrictAll U.D.T S) F hun vs]
    unfold restrictAll
    simp only [forget, layerNames_fill hu]
    rw [withFill_off U S F hun vs]

theorem restrict_withFill (S : VE.Structure.{u}) (F : FillTables U S) :
    restrictAll (fill U).T (withFill U S F) = withFill U (restrictAll U.D.T S) F := by
  show ({ S with relation := _ } : VE.Structure.{u}) = { S with relation := _ }
  congr 1
  funext n vs
  exact propext (restrict_withFill_rel hu S F n vs)

end Status

/-- `settled_expansions`: a SETTLED point has its value in the canonical expansion
of every admissible conflict-free filling. Section 7 has no `typed`; it is needed,
as for `settled_all_expansions`, because an outcome formula may be true at an
ill-typed tuple, where no admissible structure holds (statement finding, reported). -/
theorem settled_expansions (U : UDoc) (h : WellFormedU U = true) (B : VE.Structure.{u}) (hB : BaseAdmissible U.D B)
    (r : Regulated) (hr : r ∈ U.D.T.regulated) (vs : List B.Carrier) (typed : VE.TupleTyped B r.sorts vs) (b : Bool)
    (hs : SettledAs U B r vs b) (F : FillTables U B) (hF : BaseAdmissibleU U (withFill U B F))
    (hcf : ConflictFree (fill U) (withFill U B F)) :
    Expansion3 U B (expandFill U B F) ∧ ((expandFill U B F).relation r.name vs ↔ b = true) := by
  have hu := uvalid h
  exact ⟨expandFill_expansion hu h hB hF hcf, (expandFill_relation hu h B F hr vs typed).trans (hs F hF)⟩

/-- `settled_all_expansions`: the headline reading of 2.2: in a CONFLICT-FREE
document a SETTLED point has its value in every expansion. -/
theorem settled_all_expansions (U : UDoc) (h : WellFormedU U = true) (hc : ConflictFreeU.{u} U) (r : Regulated)
    (hr : r ∈ U.D.T.regulated) (S : VE.Structure.{u}) (hS : Expansion3 U (restrictAll U.D.T S) S)
    (vs : List S.Carrier) (typed : VE.TupleTyped S r.sorts vs) (b : Bool)
    (hs : SettledAs U (restrictAll U.D.T S) r vs b) :
    S.relation r.name vs ↔ b = true := by
  have _ := hc
  have hu := uvalid h
  obtain ⟨hBU, hE⟩ := expansion_filled hu h hS
  have hrel := relation_of_expansion h hBU.1 hE hr vs ((tupleTyped_relation S _ _ vs).mpr typed)
  rw [withFill_off U S _ (hu.not_unsaid (hu.declared_pred hr)) vs] at hrel
  have hBU' : BaseAdmissibleU U (withFill U (restrictAll U.D.T S) (fillOf U S)) := by
    rw [← restrict_withFill hu S (fillOf U S)]; exact hBU
  have hiff : (outcomeBase (fill U) r.name).denote (restrictAll (fill U).T (withFill U S (fillOf U S))) (tupleVal vs) ↔
      (outcomeBase (fill U) r.name).denote (withFill U (restrictAll U.D.T S) (fillOf U S)) (tupleVal vs) :=
    denote_rel_iff S _ _ (restrict_withFill_rel hu S (fillOf U S)) _ _
  exact hrel.trans (hiff.trans (hs (fillOf U S) hBU'))

/-- `undecided_expansions`: in a CONFLICT-FREE document an UNDECIDED point has
opposite values in two expansions. Section 7 has no `typed`; it is needed for the
same reason as in `settled_expansions` (statement finding, reported). -/
theorem undecided_expansions (U : UDoc) (h : WellFormedU U = true) (hc : ConflictFreeU.{u} U) (B : VE.Structure.{u})
    (hB : BaseAdmissible U.D B) (r : Regulated) (hr : r ∈ U.D.T.regulated) (vs : List B.Carrier)
    (typed : VE.TupleTyped B r.sorts vs) (hund : UndecidedAt U B r vs) :
    ∃ F₁ F₂ : FillTables U B, Expansion3 U B (expandFill U B F₁) ∧ Expansion3 U B (expandFill U B F₂) ∧
      (expandFill U B F₁).relation r.name vs ∧ ¬ (expandFill U B F₂).relation r.name vs := by
  have hu := uvalid h
  obtain ⟨F₁, F₂, h₁, h₂, v₁, v₂⟩ := hund
  exact ⟨F₁, F₂, expandFill_expansion hu h hB h₁ (hc _ h₁), expandFill_expansion hu h hB h₂ (hc _ h₂),
    (expandFill_relation hu h B F₁ hr vs typed).mpr v₁,
    fun h' => v₂ ((expandFill_relation hu h B F₂ hr vs typed).mp h')⟩

/-! ## Switching a completion to `unspecified` -/

/-- Decisions read the rules only. -/
theorem decidesD_nodes {T₁ T₂ : Tree} (h : T₁.nodes = T₂.nodes) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (q : String) (sign : Bool) : DecidesD T₁ S ρ q sign ↔ DecidesD T₂ S ρ q sign := by
  have hc : ∀ N, children T₁ N = children T₂ N := fun N => by unfold children; rw [h]
  have hy : ∀ f N, YieldsD T₁ S ρ f N ↔ YieldsD T₂ S ρ f N := by
    intro f
    induction f with
    | zero => intro; exact Iff.rfl
    | succ f ih => intro N; simp only [YieldsD, hc, ih]
  unfold DecidesD SelectsD rulesOn fuel
  rw [h]
  simp only [hc, hy]

/-- The decision formulas read the rules only. -/
theorem decides_eq_nodes {T₁ T₂ : Tree} (h : T₁.nodes = T₂.nodes) (q : String) (sign : Bool) :
    decides T₁ q sign = decides T₂ q sign := by
  have hc : ∀ N, children T₁ N = children T₂ N := fun N => by unfold children; rw [h]
  have hy : ∀ f N, yields T₁ f N = yields T₂ f N := by
    intro f
    induction f with
    | zero => intro; rfl
    | succ f ih =>
      intro N
      simp only [yields, hc]
      rw [show yields T₁ f = yields T₂ f from funext ih]
  unfold decides selects rulesOn fuel
  rw [h]
  simp only [hc]
  rw [show yields T₁ T₂.nodes.length = yields T₂ T₂.nodes.length from funext (hy _)]

def swReg (p : String) (r : Regulated) : Regulated := if r.name = p then { r with allowByDefault := false } else r

def swSym (p : String) : Sym → Sym
  | .reg r => .reg (swReg p r)
  | .defn d => .defn d

@[simp] theorem swReg_name (p : String) (r : Regulated) : (swReg p r).name = r.name := by
  unfold swReg; split <;> rfl
@[simp] theorem swReg_sorts (p : String) (r : Regulated) : (swReg p r).sorts = r.sorts := by
  unfold swReg; split <;> rfl
@[simp] theorem swReg_role (p : String) (r : Regulated) : (swReg p r).role = r.role := by
  unfold swReg; split <;> rfl
@[simp] theorem swReg_permission (p : String) (r : Regulated) : (swReg p r).permission = r.permission := by
  unfold swReg; split <;> rfl
@[simp] theorem swSym_name (p : String) (q : Sym) : (swSym p q).name = q.name := by
  cases q <;> simp [swSym, Sym.name]

section Switch
variable (U : UDoc) (p : String)

theorem switch_regulated : (U.switch p).D.T.regulated = U.D.T.regulated.map (swReg p) := rfl

theorem stratum_switch : stratumNodes (U.switch p).D.T = stratumNodes U.D.T := by
  simp only [stratumNodes, switch_regulated, List.map_map]
  congr 1
  apply List.map_congr_left
  intro r _
  simp [Sym.formulas, rulesOn, UDoc.switch]

theorem lookupSym_switch (n : String) :
    lookupSym (U.switch p).D.T n = (lookupSym U.D.T n).map (swSym p) := by
  unfold lookupSym
  rw [switch_regulated, List.find?_map]
  have : ((fun x : Regulated => x.name == n) ∘ swReg p) = (fun x => x.name == n) := by
    funext r; simp
  rw [this]
  cases U.D.T.regulated.find? (fun x => x.name == n) with
  | some r => rfl
  | none =>
    show Option.map Sym.defn _ = Option.map (swSym p) (Option.map Sym.defn _)
    rw [Option.map_map]
    rfl

theorem syms_switch : syms (U.switch p).D.T = (syms U.D.T).map (swSym p) := by
  unfold syms VE.Norms.order
  rw [stratum_switch]
  have : lookupSym (U.switch p).D.T = fun n => (lookupSym U.D.T n).map (swSym p) := funext (lookupSym_switch U p)
  rw [this, List.map_filterMap]

theorem layerNames_switch : layerNames (U.switch p).D.T = layerNames U.D.T := by
  simp [layerNames, syms_switch]

theorem size_switch : size (U.switch p).D = size U.D := by
  simp [size, syms_switch]

theorem envAt_switch (k : Nat) : envAt (U.switch p).D k = envAt U.D k := by
  simp only [envAt, layerNames_switch]
  rfl

theorem restrictAll_switch (S : VE.Structure.{u}) : restrictAll (U.switch p).D.T S = restrictAll U.D.T S := by
  simp only [restrictAll, layerNames_switch]

theorem pairs_switch : pairs (U.switch p).D.T = pairs U.D.T := by
  simp only [pairs, switch_regulated, List.filterMap_map]
  congr 2
  funext r
  simp [swReg_role, swReg_permission]

theorem background_switch : background (U.switch p).D = background U.D := by
  have h1 : definitionPremises (U.switch p).D.T = definitionPremises U.D.T := by
    simp only [definitionPremises, syms_switch, List.filterMap_map]
    congr 1
    funext q
    cases q <;> rfl
  have h2 : pairPremises (U.switch p).D.T = pairPremises U.D.T := by simp only [pairPremises, pairs_switch]
  simp only [background, h1, h2]
  rfl

theorem decides_switch (S : VE.Structure.{u}) (ρ : VE.Valuation S) (q : String) (sign : Bool) :
    DecidesD (U.switch p).D.T S ρ q sign ↔ DecidesD U.D.T S ρ q sign :=
  decidesD_nodes (T₁ := (U.switch p).D.T) (T₂ := U.D.T) rfl S ρ q sign

end Switch

/-- `unreached_switch`: switching a deny/allow completion that no admissible filling
of the switched document reaches to `unspecified` changes no expansion (5, 6.3).
Section 7 quantifies `hnr` over the fillings of `U`; that statement is false: a
pair premise can exclude, under the completion, every filling that reaches `p`,
while the switched document allows one (statement finding, reported). -/
theorem unreached_switch (U : UDoc) (h : WellFormedU U = true) (p : String) (hp : p ∈ regulatedNames U.D.T)
    (hnp : p ∉ U.unspec) (h' : WellFormedU (U.switch p) = true)
    (hnr : ∀ B : VE.Structure.{u}, BaseAdmissibleU (U.switch p) B → ∀ vs, VE.TupleTyped B (sortsOf U.D p) vs →
      ¬ (reachedF (U.switch p) p).denote B (tupleVal vs)) :
    ∀ B S : VE.Structure.{u}, BaseAdmissible U.D B → (Expansion3 U B S ↔ Expansion3 (U.switch p) B S) := by
  intro B S _
  have _ := hp
  have hu := uvalid h
  have hu' := uvalid h'
  have hw' := fill_wellFormed _ h'
  have hv' := valid_of_wellFormed _ hw'
  -- the intended predicate readings, pointwise
  have hne : ∀ r ∈ U.D.T.regulated, r.name ≠ p → (IntendedAt3 (U.switch p) (swReg p r) S ↔ IntendedAt3 U r S) := by
    intro r _ hrp
    have hsw : swReg p r = r := by simp [swReg, hrp]
    rw [hsw]
    unfold IntendedAt3 Value3
    have hc : completionOf (U.switch p) r = completionOf U r := by
      have : r.name ∉ U.unspec ++ [p] ↔ r.name ∉ U.unspec := by simp [hrp]
      simp only [completionOf, UDoc.switch]
      by_cases hr : r.name ∈ U.unspec
      · simp [hr]
      · simp [hr, hrp]
    rw [hc]
    simp only [decides_switch]
  -- the unspecified reading is weaker
  have hweak : ∀ r ∈ U.D.T.regulated, r.name = p → IntendedAt3 U r S → IntendedAt3 (U.switch p) (swReg p r) S := by
    intro r _ hrp hi
    have hsw : swReg p r = { r with allowByDefault := false } := by simp [swReg, hrp]
    have hc : completionOf (U.switch p) { r with allowByDefault := false } = .unspecified := by
      simp [completionOf, UDoc.switch, hrp]
    rw [hsw]
    intro vs hvs
    have := hi vs hvs
    unfold Value3 at this ⊢
    dsimp only at this ⊢
    rw [hc, decides_switch, decides_switch]
    unfold value3 at this ⊢
    by_cases hP : DecidesD U.D.T (forget [r.name] S) (tupleVal vs) r.name true <;>
    by_cases hN : DecidesD U.D.T (forget [r.name] S) (tupleVal vs) r.name false <;>
    simp_all
  constructor
  · rintro ⟨hrs, hA, hbg, hint⟩
    refine ⟨by rw [restrictAll_switch]; exact hrs, by rw [size_switch, envAt_switch]; exact hA,
      by rw [background_switch]; exact hbg, ?_⟩
    rw [switch_regulated, List.forall_mem_map]
    intro r hr
    by_cases hrp : r.name = p
    · exact hweak r hr hrp (hint r hr)
    · exact (hne r hr hrp).mpr (hint r hr)
  · intro hS'
    obtain ⟨hrs, hA, hbg, hint⟩ := hS'
    obtain ⟨hBU, hE⟩ := expansion_filled hu' h' ⟨hrs, hA, hbg, hint⟩
    refine ⟨by rw [← restrictAll_switch U p]; exact hrs, by rw [← size_switch U p, ← envAt_switch U p]; exact hA,
      by rw [← background_switch U p]; exact hbg, fun r hr => ?_⟩
    rw [switch_regulated, List.forall_mem_map] at hint
    by_cases hrp : r.name = p
    · -- no admissible filling reaches `p`, so the completion never decides
      have hsw : swReg p r = { r with allowByDefault := false } := by simp [swReg, hrp]
      have hi := hint r hr
      rw [hsw] at hi
      intro vs hvs
      have hi' := hi vs hvs
      have hc : completionOf (U.switch p) { r with allowByDefault := false } = .unspecified := by
        simp [completionOf, UDoc.switch, hrp]
      unfold Value3 at hi'
      dsimp only at hi'
      rw [hc, decides_switch, decides_switch] at hi'
      -- the author rules decide p at vs
      let S' := withFill (U.switch p) S (fillOf (U.switch p) S)
      have hr' : swReg p r ∈ (fill (U.switch p)).T.regulated := List.mem_map_of_mem hr
      obtain ⟨k, hk⟩ := mem_syms_index (hv'.regulated _ hr')
      have hb : before (fill (U.switch p)) p = k := by
        have := before_eq hv' hk
        simpa [Sym.name, hrp] using this
      obtain ⟨_, hpa⟩ := (documentExpansion_iff hv' _ S' hBU.1).mp hE
      obtain ⟨hA', _, hM, _⟩ := (prefix_char hv' _ (Nat.le_refl _) S').mp hpa
      have ha := agreesBelow_of_meanings hM
      have hkl : k < size (fill (U.switch p)) := (List.getElem?_eq_some_iff.mp hk).1
      have hvs' : VE.TupleTyped S' r.sorts vs := (tupleTyped_relation S _ _ vs).mpr hvs
      have hρ := tupleVal_typed S' _ vs hvs'
      -- `pos`/`neg` of the author rules, typed below `p` on `T‴`
      obtain ⟨j, hj⟩ := mem_syms_index (hu'.valid.regulated _ (List.mem_map_of_mem hr : swReg p r ∈ (U.switch p).D.T.regulated))
      have hkj : j = k := by
        have e1 : before (U.switch p).D p = j := by
          have := before_eq hu'.valid hj
          simpa [Sym.name, hrp] using this
        rw [← e1, ← hb, before_fill hu']
      subst hkj
      have hT := rulesTyped_of_valid hu'.valid hj
      have hmono : ∀ sign, (decides (U.switch p).D.T p sign).WellFormed (envAt (fill (U.switch p)) j) r.sorts.reverse := by
        intro sign
        rw [← VE.check_iff_wellFormed]
        have := (VE.check_iff_wellFormed _ _ _).mpr (decides_wellFormed hT sign)
        simp only [hrp] at this
        exact check_envAt_fill hu' this
      have hsub : ∀ sign, (subst (fill (U.switch p)).T j (decides (U.switch p).D.T p sign)).denote
          (restrictAll (fill (U.switch p)).T S') (tupleVal vs) ↔ DecidesD U.D.T S' (tupleVal vs) p sign := by
        intro sign
        rw [subst_restrict_denote hv' j S' hA'.1 (fun j' q' hj' => ha j' q' (Nat.lt_trans hj' hkl)) _ _ (hmono sign) _ hρ,
          decides_denote]
        exact decides_switch U p S' _ p sign
      -- the decisions at `forget [p] S` are those at `S'`
      have hdec : ∀ sign, DecidesD U.D.T (forget [r.name] S) (tupleVal vs) r.name sign ↔
          DecidesD U.D.T S' (tupleVal vs) p sign := by
        intro sign
        rw [hrp, ← decides_denote, ← decides_denote]
        have hT0 := decides_wellFormed hT sign
        simp only [hrp] at hT0
        rw [decides_eq_nodes (T₁ := (U.switch p).D.T) (T₂ := U.D.T) rfl] at hT0
        refine denote_relation_congr (ns := p :: unsaidNames (U.switch p)) (fun n hn => ?_) S'
          (fun n vs => n ∉ [p] ∧ S.relation n vs) (fun n vs hn => ?_) _ _ _ hT0
        · rcases List.mem_cons.mp hn with hn | hn
          · rw [hn]; exact self_hidden hu'.valid hj _ (by simp [Sym.name, hrp])
          · exact unsaid_undeclared hu' j n hn
        · have hn1 : n ≠ p := fun e => hn (e ▸ List.mem_cons_self)
          have hn2 : n ∉ unsaidNames (U.switch p) := fun h => hn (List.mem_cons_of_mem _ h)
          simp only [List.mem_singleton, hn1, not_false_eq_true, true_and]
          exact (withFill_off _ S _ hn2 vs).symm
      have hreach : ¬ (reachedF (U.switch p) p).denote (restrictAll (fill (U.switch p)).T S') (tupleVal vs) := by
        refine hnr _ hBU vs ?_
        have hs : sortsOf U.D p = r.sorts := by rw [← hrp]; exact sortsOf_reg hu hr
        rw [tupleTyped_restrictAll, hs]
        exact hvs'
      simp only [reachedF, VE.Formula.denote, hb, pos, neg, hsub, not_and, Classical.not_not] at hreach
      unfold Value3
      rw [hdec true, hdec false] at hi' ⊢
      have hPN : DecidesD U.D.T S' (tupleVal vs) p true ∨ DecidesD U.D.T S' (tupleVal vs) p false := by
        by_cases hP : DecidesD U.D.T S' (tupleVal vs) p true
        · exact Or.inl hP
        · exact Or.inr (hreach hP)
      have hcU : completionOf U r = if r.allowByDefault then .allow else .deny := by
        simp only [completionOf, hrp, hnp, if_false]
      simp only [hcU]
      unfold value3 at hi' ⊢
      rcases hPN with hP | hN
      · by_cases hN : DecidesD U.D.T S' (tupleVal vs) p false <;> simp_all
      · by_cases hP : DecidesD U.D.T S' (tupleVal vs) p true <;> simp_all
    · exact (hne r hr hrp).mp (hint r hr)

end VE.NormDefaults
