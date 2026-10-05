import VE.Readings.SupFree

/-! ALL under `A` (docs/spec/composition-s2.md 4.5, 8.4 `superpose_all`, `superpose_all_base`).

A certificate on `sup D` proves `φ` in every situation of every compatible reading that takes `A`'s candidates. A
base of the reading's document is first given an element (`adjoinOne`; truth of a closed sentence over the
complete vocabulary is carried by `canon_subst` and `adjoin_denote`), then lifted to a slot-admissible base of
`sup D` (`upB`). Conflict-freedom under the slot gives that base a document expansion, an intended structure of
`sup D` on which the certificate is sound (`slot_route_intended`); a sentence over the complete vocabulary has one
truth on the expansion and on the canonical interpretation (both satisfy the layer meanings over one base), and
`superpose_situation` carries the hypotheses up and the conclusion down. -/
namespace VE.Readings
open VE.Norms (envAt size Regulated tupleVal Sat ConstantsTyped elaborate)
open VE.SoftNorms (SoftNode SoftDoc soften canon envPrime circ)
open VE.Rights (RightsDoc correlate)
open VE.Compose (BaseAdmissibleP ConflictFreeP adjoinOne)
universe u

section Shared
variable {D : Doc} (hh : Hyps D)
include hh

/-- A sentence over the shared vocabulary is one over a choice's complete vocabulary. -/
theorem shared_liftY (c : Choice) {φ : VE.Formula} {Γ : List String} (hφ : φ.WellFormed (sharedEnv D) Γ) :
    φ.WellFormed (envAt (soften (choiceDoc D c).1.soft) (size (soften (choiceDoc D c).1.soft))) Γ := by
  have hd : (VE.Norms.layerNames (soften (choiceDoc D c).1.soft).T).drop (size (soften (choiceDoc D c).1.soft)) = [] := by
    simp [VE.Norms.layerNames, VE.Norms.size]
  refine wf_sub ?_ ?_ ?_ φ Γ hφ
  · intro s hs
    rw [sharedEnv_sorts] at hs
    show s ∈ (choiceDoc D c).1.soft.E.sorts
    rw [choice_E c]; exact hs
  · intro x s hx
    rw [sharedEnv_constants] at hx
    show (choiceDoc D c).1.soft.E.constants x = some s
    rw [choice_E c]; exact hx
  · intro p ss hp
    simp only [envAt, hd, VE.Norms.hide, List.not_mem_nil, if_false]
    exact free_envPrime_sub hh c (sharedEnv_sub hh hp)

omit hh in
/-- Adjoining an element does not change the truth of a closed sentence on the canonical interpretation. -/
theorem canon_adjoin {Dd : VE.Norms.Doc} (hv : VE.Norms.Valid Dd) (B : VE.Structure.{u})
    (hcB : ConstantsTyped Dd B) {φ : VE.Formula} (hφ : φ.WellFormed (envAt Dd (size Dd)) []) :
    φ.denote (canon Dd (adjoinOne B)) [] ↔ φ.denote (canon Dd B) [] := by
  have hcA : ConstantsTyped Dd (adjoinOne B) := by
    intro x s hx
    obtain ⟨v, hv', hd⟩ := hcB x s hx
    exact ⟨some v, by show (B.constant x).map some = _; rw [hv']; rfl, v, rfl, hd⟩
  rw [← VE.SoftNorms.canon_subst hv _ hcA _ φ [] hφ [] (typed_nil _),
    ← VE.SoftNorms.canon_subst hv _ hcB _ φ [] hφ [] (typed_nil _)]
  exact VE.Compose.adjoin_denote B _ []

/-- A sentence over the shared vocabulary reads the choice's expansion of the pulled lift as that of `B₀`. -/
theorem canon_pull_up {c : Choice} (hc : Compatible D c) (B₀ : VE.Structure.{u}) (e : B₀.Carrier)
    (hB₀ : VE.SoftNorms.BaseAdmissible' (choiceDoc D c).1.soft B₀) {φ : VE.Formula} {Γ : List String}
    (hφ : φ.WellFormed (sharedEnv D) Γ) (ρ : VE.Valuation B₀) :
    φ.denote (canon (soften (choiceDoc D c).1.soft) (pull D c (upB D c B₀ e))) ρ ↔
      φ.denote (canon (soften (choiceDoc D c).1.soft) B₀) ρ := by
  have hvY := choice_valid hh hc
  obtain ⟨hs, hk, _⟩ := sharedEnv_noChoice hh.wf hh.ready
  have lift : ∀ (F : VE.Formula) (Γ' : List String), F.WellFormed (envAt (soften (choiceDoc D c).1.soft) 0) Γ' →
      F.WellFormed (envPrime (choiceDoc D c).1.soft) Γ' := fun F Γ' h =>
    VE.Norms.wf_mono (E := envAt (soften (choiceDoc D c).1.soft) 0) (E' := envPrime (choiceDoc D c).1.soft)
      rfl rfl (fun r ss h => envAt_sub h) F Γ' h
  refine ext_denote (E := sharedEnv D) (S := canon (soften (choiceDoc D c).1.soft) B₀) hs hk
    (canon (soften (choiceDoc D c).1.soft) (pull D c (upB D c B₀ e))).relation (upDom B₀) (upConst B₀ e)
    (fun p _ _ vs => ?_) (fun σ hσ => ?_) (fun x hx => ?_) φ Γ ρ hφ
  · show (match VE.Norms.expTable (soften (choiceDoc D c).1.soft).T (size (soften (choiceDoc D c).1.soft)) p with
        | some F => F.denote (pull D c (upB D c B₀ e)) (tupleVal vs)
        | none => (pull D c (upB D c B₀ e)).relation p vs) ↔
      (match VE.Norms.expTable (soften (choiceDoc D c).1.soft).T (size (soften (choiceDoc D c).1.soft)) p with
        | some F => F.denote B₀ (tupleVal vs)
        | none => B₀.relation p vs)
    cases hF : VE.Norms.expTable (soften (choiceDoc D c).1.soft).T (size (soften (choiceDoc D c).1.soft)) p with
    | none => exact pull_upB hh c B₀ e hB₀.1.1 p vs
    | some F =>
      obtain ⟨ss, _, hFw⟩ := VE.Norms.expTable_wellFormed hvY _ p F hF
      exact pull_up hh B₀ e hB₀.1.1 F _ (lift _ _ hFw) _
  · show (if σ = "ve__reading" then _ else _) = _; exact if_neg hσ
  · show (if x = "ve__here" then _ else _) = _; exact if_neg hx

end Shared

/-- ALL under A: a certificate on sup D proves φ in every situation of every compatible reading that takes A's
    candidates, read in that reading's own document. -/
theorem superpose_all (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights) (hs : superposable D = true)
    (A : Choice) (hA : ∀ x ∈ A, (candidate D x.1 x.2).isSome)
    (hcf : ConflictFreeP.{u} (correlate (sup D).1) (slotUnder D A))
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) [])
    (hφ : φ.WellFormed (sharedEnv D) []) (cert : VE.Tableau.Certificate)
    (accepted : supCertificateCheck D A Γ φ cert = true)
    (c : Choice) (hc : Compatible D c) (hAc : ∀ x ∈ A, x ∈ c) (B : VE.Structure.{u})
    (hB : VE.Rights.BaseAdmissibleR (choiceDoc D c).1 B)
    (hp : Sat (expand (choiceDoc D c).1 B) ((choiceDoc D c).2 ++ Γ)) :
    φ.denote (expand (choiceDoc D c).1 B) [] := by
  have hh : Hyps D := ⟨h, hch, hs⟩
  have hX : correlate (sup D).1 = (sup D).1.soft := sup_correlate hh
  have hYc : correlate (choiceDoc D c).1 = (choiceDoc D c).1.soft := choice_correlate hh c
  have hYn := choiceDoc_noRights D c hh.noRights
  have hvY := choice_valid hh hc
  have hvX := sup_valid hh
  have hwf := sup_wfSoft hh
  unfold expand at hp ⊢
  rw [hYc] at hp ⊢
  have hB₀ : VE.SoftNorms.BaseAdmissible' (choiceDoc D c).1.soft B := by
    have := hB.1; rwa [hYc] at this
  have hcB : ConstantsTyped (soften (choiceDoc D c).1.soft) B := hB₀.1.1.1
  -- the sentences involved, over the complete vocabularies
  have hwY : ∀ a ∈ (choiceDoc D c).2 ++ Γ, a.WellFormed (sharedEnv D) [] := by
    intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · exact asserted_shared D h hh.ready c hc a ha
    · exact hΓ a ha
  -- lift to a base with an element
  have hB' : VE.SoftNorms.BaseAdmissible' (choiceDoc D c).1.soft (adjoinOne B) :=
    ((VE.Compose.adjoin_baseAdmissibleP _ [] B).mpr ⟨hB₀, fun _ h => nomatch h⟩).1
  have hcB' : ConstantsTyped (soften (choiceDoc D c).1.soft) (adjoinOne B) := hB'.1.1.1
  have hp' : Sat (canon (soften (choiceDoc D c).1.soft) (adjoinOne B)) ((choiceDoc D c).2 ++ Γ) := fun a ha =>
    (canon_adjoin hvY B hcB (shared_liftY hh c (hwY a ha))).mpr (hp a ha)
  suffices hgoal : φ.denote (canon (soften (choiceDoc D c).1.soft) (adjoinOne B)) [] from
    (canon_adjoin hvY B hcB (shared_liftY hh c hφ)).mp hgoal
  let e : (adjoinOne B).Carrier := none
  -- the lifted base of sup D
  have henc := upB_encodes hh.ready hc (adjoinOne B) e
  have hcm : complete D c = true := by
    simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
  have hUbase : VE.Norms.BaseAdmissible (soften (sup D).1.soft) (upB D c (adjoinOne B) e) :=
    ⟨upB_admissible hh hc _ e hB'.1.1, upB_literals hh _ e hB'.1.2⟩
  have hUsoft : Sat (upB D c (adjoinOne B) e) (VE.SoftNorms.softPremises (sup D).1.soft) := by
    intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · exact upB_exc hh hc _ e hB' a ha
    · exact upB_coh hh hc _ e hB' a ha
  have hUslot : Sat (upB D c (adjoinOne B) e) (slotUnder D A) := by
    intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · exact upB_slot hh hc _ e a ha
    · exact (encodes_atoms D c hcm _ henc A).mpr hAc a ha
  have hUs : BaseAdmissibleP (correlate (sup D).1) (slotP D) (upB D c (adjoinOne B) e) := by
    rw [hX]; exact ⟨⟨hUbase, hUsoft⟩, upB_slot hh hc _ e⟩
  have hcfU := hcf _ (by rw [hX]; exact ⟨⟨hUbase, hUsoft⟩, hUslot⟩)
  rw [hX] at hcfU
  -- the situation of c on the lifted base
  obtain ⟨_, hsh, has⟩ := superpose_situation D h hch hs c hc _ hUs henc
  unfold expand at hsh has
  rw [hX, hYc] at hsh has
  have hXsat : Sat (canon (soften (sup D).1.soft) (upB D c (adjoinOne B) e)) ((sup D).2 ++ Γ) := by
    intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · refine has.mpr (fun b hb => ?_) a ha
      exact (canon_pull_up hh hc _ e hB' (hwY b (List.mem_append_left _ hb)) []).mpr
        (hp' b (List.mem_append_left _ hb))
    · exact (hsh a (hΓ a ha)).mpr ((canon_pull_up hh hc _ e hB' (hΓ a ha) []).mpr
        (hp' a (List.mem_append_right _ ha)))
  -- the document expansion of the lifted base
  obtain ⟨S0, ⟨hr0, hA0, hsat0⟩, _⟩ := (VE.SoftNorms.coherent_expands _ hwf _ hUbase).mpr hcfU
  have hc0 : ConstantsTyped (soften (sup D).1.soft) S0 := VE.Norms.constantsTyped_of_admissible hA0
  have hsd := (VE.Norms.sat_document hvX S0).mp hsat0
  have ha0 := VE.Norms.agreesBelow_of_meanings hsd.2.1
  have key : ∀ ψ : VE.Formula, ψ.WellFormed (envAt (soften (sup D).1.soft) (size (soften (sup D).1.soft))) [] →
      (ψ.denote S0 [] ↔ ψ.denote (canon (soften (sup D).1.soft) (upB D c (adjoinOne B) e)) []) := by
    intro ψ hψ
    rw [← hr0, ← VE.Norms.subst_restrict_denote hvX _ S0 hc0 ha0 ψ [] hψ [] (typed_nil _)]
    exact VE.SoftNorms.canon_subst hvX (VE.Norms.restrictAll (soften (sup D).1.soft).T S0) hc0 _ ψ [] hψ []
      (typed_nil _)
  have hsupwf : ∀ a ∈ (sup D).2,
      a.WellFormed (envAt (soften (sup D).1.soft) (size (soften (sup D).1.soft))) [] := by
    have hw : sideWF D (sup D) = true := by
      have := hs; simp only [superposable, Bool.and_eq_true] at this; exact this.2
    simp only [sideWF, Bool.and_eq_true, List.all_eq_true] at hw
    intro a ha
    have := (VE.check_iff_wellFormed _ _ _).mp (hw.2 a ha)
    rwa [hX] at this
  have hslotwf := slot_wellFormed D h hch hs A hA
  rw [hX] at hslotwf
  have hsv := sup_softValid hh
  have restrict : ∀ a : VE.Formula, a.WellFormed (envAt (soften (sup D).1.soft) 0) [] →
      a.denote (upB D c (adjoinOne B) e) [] → a.denote S0 [] := fun a hw ha => by
    rw [← hr0] at ha
    exact (VE.Norms.restrictAll_denote a [] hw S0 []).mp ha
  have accepted' := accepted
  unfold supCertificateCheck at accepted'
  rw [hX] at accepted'
  have hφS := VE.Compose.slot_route_intended _ hwf (slotUnder D A) ((sup D).2 ++ Γ) φ cert accepted' S0 hA0
    ((VE.SoftNorms.soft_elaborate_iff _ hwf S0).mp (fun a ha => hsat0 a (List.mem_append_right _ ha)))
    (fun a ha => hsat0 a (List.mem_append_left _ (List.mem_append_left _ (List.mem_append_left _ ha))))
    (fun a ha => hsat0 a (List.mem_append_left _ (List.mem_append_right _ ha)))
    (fun a ha => hsat0 a (List.mem_append_left _ (List.mem_append_left _ (List.mem_append_right _ ha))))
    (fun a ha => restrict a (hsv.premTyped a ha) (hUsoft a ha))
    (fun a ha => restrict a (hslotwf a ha) (hUslot a ha))
    (fun a ha => by
      rcases List.mem_append.mp ha with ha' | ha'
      · exact (key a (hsupwf a ha')).mpr (hXsat a ha)
      · exact (key a (shared_lift hh (hΓ a ha'))).mpr (hXsat a ha))
  have h1 := (key φ (shared_lift hh hφ)).mp hφS
  exact (canon_pull_up hh hc _ e hB' hφ []).mp ((hsh φ hφ).mp h1)

theorem envAt_zero_le {Dd : VE.Norms.Doc} {p : String} {ss : List String} (k : Nat)
    (hp : (envAt Dd 0).predicates p = some ss) : (envAt Dd k).predicates p = some ss := by
  simp only [envAt, VE.Norms.hide] at hp ⊢
  split at hp
  · cases hp
  · rename_i hn
    rw [if_neg (fun h => hn (by simpa using List.mem_of_mem_drop h))]
    exact hp

theorem genKeys_find_frame {D : Doc} (X : RightsDoc) (hX : noRights X = true)
    (hfresh : ∀ d ∈ VE.SoftNorms.decisions X.soft, D.frame.soft.E.predicates d.1 = none) {p : String}
    (hp : D.frame.soft.E.predicates p ≠ none) : (genKeys X).find? (·.2.1 == p) = none := by
  cases hf : (genKeys X).find? (·.2.1 == p) with
  | none => rfl
  | some g =>
    exfalso
    have hg := genKeys_decision hX (List.mem_of_find?_eq_some hf)
    rw [(correlate_noRights X hX).1] at hg
    have hn : g.2.1 = p := by simpa using List.find?_some hf
    have := hfresh _ hg
    simp only at this
    rw [hn] at this
    exact hp this

section Author
variable {D : Doc} (hh : Hyps D)
include hh

theorem author_frame {p : String} {ss : List String} (hp : (authorEnv D).predicates p = some ss) :
    D.frame.soft.E.predicates p = some ss := envAt_sub hp

/-- A sentence over the author's base vocabulary is one over the shared vocabulary. -/
theorem author_shared {φ : VE.Formula} {Γ : List String} (hφ : φ.WellFormed (authorEnv D) Γ) :
    φ.WellFormed (sharedEnv D) Γ := by
  have hfn := free_noRights D hh.noRights
  have hK := keepsFrame_build D (fun u => (attached D u).isEmpty) (fun _ => none)
  refine wf_sub ?_ ?_ ?_ φ Γ hφ
  · intro s hs; rw [sharedEnv_sorts]; exact hs
  · intro x s hx; rw [sharedEnv_constants]; exact hx
  · intro p ss hp
    have hfr := author_frame hh hp
    have hfresh : ∀ d ∈ VE.SoftNorms.decisions (free D).1.soft, D.frame.soft.E.predicates d.1 = none := by
      intro d hd
      have := (free_soft_valid hh).decFresh d.1 (List.mem_map.mpr ⟨d, hd, rfl⟩)
      rwa [free_E] at this
    have h0 := envAt_author D (free D).1 hK (genKeys_find_frame _ hfn hfresh (by rw [hfr]; simp)) hp
    exact envAt_zero_le _ h0

/-- A sentence over the author's base vocabulary is one over a choice's base vocabulary. -/
theorem author_choice (c : Choice) {φ : VE.Formula} {Γ : List String} (hφ : φ.WellFormed (authorEnv D) Γ) :
    φ.WellFormed (envAt (soften (choiceDoc D c).1.soft) 0) Γ := by
  have hYn := choiceDoc_noRights D c hh.noRights
  have hK := keepsFrame_build D (fun _ => true) (pickC c)
  refine wf_sub ?_ ?_ ?_ φ Γ hφ
  · intro s hs
    show s ∈ (choiceDoc D c).1.soft.E.sorts
    rw [choice_E c]; exact hs
  · intro x s hx
    show (choiceDoc D c).1.soft.E.constants x = some s
    rw [choice_E c]; exact hx
  · intro p ss hp
    have hfr := author_frame hh hp
    have h0 := envAt_author D (choiceDoc D c).1 hK
      (genKeys_find_frame _ hYn (fun d hd => choice_decision_fresh hh c hd) (by rw [hfr]; simp)) hp
    rwa [choice_correlate hh c] at h0

end Author

/-- The plan's form, a corollary: over the author's base vocabulary the expansion changes nothing (canon_base). -/
theorem superpose_all_base (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) (A : Choice) (hA : ∀ x ∈ A, (candidate D x.1 x.2).isSome)
    (hcf : ConflictFreeP.{u} (correlate (sup D).1) (slotUnder D A)) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (authorEnv D) []) (hφ : φ.WellFormed (authorEnv D) [])
    (cert : VE.Tableau.Certificate) (accepted : supCertificateCheck D A Γ φ cert = true)
    (c : Choice) (hc : Compatible D c) (hAc : ∀ x ∈ A, x ∈ c) (B : VE.Structure.{u})
    (hB : VE.Rights.BaseAdmissibleR (choiceDoc D c).1 B) (ha : ∀ a ∈ (choiceDoc D c).2, a.WellFormed (authorEnv D) [])
    (hp : Sat B ((choiceDoc D c).2 ++ Γ)) :
    φ.denote B [] := by
  have hh : Hyps D := ⟨h, hch, hs⟩
  have hwa : ∀ a ∈ (choiceDoc D c).2 ++ Γ, a.WellFormed (authorEnv D) [] := by
    intro a hm
    rcases List.mem_append.mp hm with hm | hm
    · exact ha a hm
    · exact hΓ a hm
  have hp' : Sat (expand (choiceDoc D c).1 B) ((choiceDoc D c).2 ++ Γ) := by
    intro a hm
    unfold expand
    rw [choice_correlate hh c]
    exact (VE.SoftNorms.canon_base B a [] (author_choice hh c (hwa a hm)) []).mpr (hp a hm)
  have := superpose_all D h hch hs A hA hcf Γ φ (fun a hm => author_shared hh (hΓ a hm)) (author_shared hh hφ)
    cert accepted c hc hAc B hB hp'
  unfold expand at this
  rw [choice_correlate hh c] at this
  exact (VE.SoftNorms.canon_base B φ [] (author_choice hh c hφ) []).mp this

end VE.Readings
