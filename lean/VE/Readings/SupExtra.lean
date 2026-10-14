import VE.Readings.SupAll
import VE.Readings.SupWitness
import VE.Readings.SupFill

/-! S2a with a carried base-premise family (docs/spec/readings-defaults.md 6.7, plan RD-6a).

`superpose_conflict_free`, `superpose_all` and `superpose_countermodel` with a family `Q` appended to the slot of
`sup D` and `Q' c` to the limitation premises of each choice's document. `Transfers D Q Q'` is the one bridge: `Q'
c` is typed over the complete vocabulary of `c`'s own document, which holds no choice symbol, and at a
slot-admissible base of `sup D` encoding `c`, `Q` holds exactly when `Q' c` holds of the pulled base. Downward, a
base of `sup D` pulls back to a base of the choice's document (`base_down`) and `Transfers` carries `Q` to `Q' c`.
Upward, a base `B₀` of the choice's document is lifted (`upB`); the pulled lift reads every formula over the choice's
complete vocabulary as `B₀` does (`pull_up`), so `Q' c` holds of it, and `Transfers` gives `Q` on the lift.

The certificate route (`superpose_all_extra`) reads `Q` on an intended structure of `sup D`, whose restriction is
the lifted base; that needs `Q` typed over `sup D`'s base vocabulary (`hQw`), as `slot_route_acceptance` needs of
every slot premise. Without it the approved statement is false: `Q = [φ]` with `φ` over a regulated predicate proves
`φ` by a one-step certificate while `Transfers` only reads `φ` on the base's own relation. The approved S2a
statements are the instances at `transfers_nil` (`superpose_*_nil` at the end check this without restating them). -/
namespace VE.Readings
open VE.Norms (Regulated Sat envAt size restrictAll DocumentExpansion ConstantsTyped)
open VE.SoftNorms (SoftNode SoftDoc soften canon circ)
open VE.Rights (RightsDoc correlate)
open VE.Compose (Content adjoinOne)
open VE.NormDefaults (EntailsU)
universe u

section Extra
open VE.Compose (BaseAdmissibleP ConflictFreeP)
/-- A carried base-premise family: `Q' c` is over the vocabulary of `c`'s own document, so it mentions no choice
    symbol (review A1), and at a slot-admissible base of `sup D` encoding `c`, `Q` holds exactly when `Q' c` holds of
    the pulled base. -/
def Transfers (D : Doc) (Q : List VE.Formula) (Q' : Choice → List VE.Formula) : Prop :=
  (∀ c, Compatible D c → ∀ a ∈ Q' c, a.WellFormed (choiceEnvFull D c) []) ∧
  ∀ c, Compatible D c → ∀ B : VE.Structure.{u}, BaseAdmissibleP (correlate (sup D).1) (slotP D) B →
    Encodes D c B → (Sat B Q ↔ Sat (pull D c B) (Q' c))
/-- `supCertificateCheck` with `Q` after `slotUnder D A`. -/
def supCertificateCheckExtra (D : Doc) (A : Choice) (Q Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate) : Bool :=
  let X := correlate (sup D).1
  VE.Tableau.checkCertificate (envAt (soften X) (size (soften X)))
    (VE.Compose.backgroundP X (slotUnder D A ++ Q) ++ VE.Norms.elaborate (soften X).T ++ ((sup D).2 ++ Γ)) φ cert
/-- `supModelCheck` with `Q` after `slotUnder D A`. -/
def supModelCheckExtra {α : Type u} [DecidableEq α] (D : Doc) (A : Choice) (Q Γ : List VE.Formula)
    (M : VE.FiniteModel α) : Bool :=
  let X := correlate (sup D).1
  VE.Compose.backgroundValidP X (slotUnder D A ++ Q) M && ((sup D).2 ++ Γ).all (fun a => (VE.SoftNorms.circ X a).eval M [])

/-- The carried family `Q' c`, typed over the choice's complete vocabulary, reads the pulled lift of an admissible
    base `B₀` of the choice's document as it reads `B₀`. -/
theorem sat_pull_up {D : Doc} (hh : Hyps D) {Q' : Choice → List VE.Formula}
    (hw : ∀ c, Compatible D c → ∀ a ∈ Q' c, a.WellFormed (choiceEnvFull D c) []) {c : Choice} (hc : Compatible D c)
    (B₀ : VE.Structure.{u}) (e : B₀.Carrier) (hadm : B₀.Admissible (envAt (soften (choiceDoc D c).1.soft) 0)) :
    Sat (pull D c (upB D c B₀ e)) (Q' c) ↔ Sat B₀ (Q' c) := by
  have lift : ∀ a ∈ Q' c, a.WellFormed (VE.SoftNorms.envPrime (choiceDoc D c).1.soft) [] := by
    intro a ha
    refine wf_sub ?_ ?_ ?_ a [] (hw c hc a ha)
    · intro s hs
      simp only [choiceEnvFull, envAt, choice_correlate hh c] at hs
      rw [envPrime_sorts]; exact hs
    · intro x s hx
      simp only [choiceEnvFull, envAt, choice_correlate hh c] at hx
      rw [envPrime_constants]; exact hx
    · intro p ss hp
      rw [← choiceEnvFull_eq hh c p]; exact hp
  exact ⟨fun h a ha => (pull_up hh B₀ e hadm a [] (lift a ha) []).mp (h a ha),
    fun h a ha => (pull_up hh B₀ e hadm a [] (lift a ha) []).mpr (h a ha)⟩

theorem superpose_conflict_free_extra (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) (A : Choice) (hA : ∀ x ∈ A, (candidate D x.1 x.2).isSome)
    (Q : List VE.Formula) (Q' : Choice → List VE.Formula) (hq : Transfers.{u} D Q Q') :
  ConflictFreeP.{u} (correlate (sup D).1) (slotUnder D A ++ Q) ↔
    ∀ c, Compatible D c → (∀ x ∈ A, x ∈ c) →
      ConflictFreeP.{u} (correlate (choiceDoc D c).1) (VE.Rights.limPremises (choiceDoc D c).1 ++ Q' c) := by
  have hh : Hyps D := ⟨h, hch, hs⟩
  constructor
  · intro hcf c hc hAc B₀ hB
    have hYn := (correlate_noRights _ (choiceDoc_noRights D c hh.noRights))
    rw [hYn.1]
    rw [hYn.1, hYn.2, List.nil_append] at hB
    obtain ⟨hB₀, hQ'⟩ := hB
    by_cases hne : Nonempty B₀.Carrier
    · obtain ⟨e⟩ := hne
      have hcm : complete D c = true := by
        simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
      have henc := upB_encodes hh.ready hc B₀ e
      have hBs : BaseAdmissibleP (correlate (sup D).1) (slotP D) (upB D c B₀ e) := by
        rw [sup_correlate hh]
        refine ⟨⟨⟨upB_admissible hh hc B₀ e hB₀.1.1, upB_literals hh B₀ e hB₀.1.2⟩, ?_⟩, upB_slot hh hc B₀ e⟩
        intro a ha
        rcases List.mem_append.mp ha with ha | ha
        · exact upB_exc hh hc B₀ e hB₀ a ha
        · exact upB_coh hh hc B₀ e hB₀ a ha
      have hQ : Sat (upB D c B₀ e) Q :=
        (hq.2 c hc _ hBs henc).mpr ((sat_pull_up hh hq.1 hc B₀ e hB₀.1.1).mpr hQ')
      have hBA : BaseAdmissibleP (correlate (sup D).1) (slotUnder D A ++ Q) (upB D c B₀ e) :=
        ⟨hBs.1, (VE.Compose.sat_append _ _ _).mpr ⟨fun a ha => by
          rcases List.mem_append.mp ha with ha | ha
          · exact hBs.2 a ha
          · exact (encodes_atoms D c hcm _ henc A).mpr hAc a ha, hQ⟩⟩
      have hY := (superpose_conflict_iff D h hch hs c hc _ hBs henc).mp (hcf _ hBA)
      rw [choice_correlate hh c] at hY
      exact up_conflictFree hh hc B₀ e hB₀ hY
    · exact conflictFree_empty (choice_valid hh hc) B₀ hne
  · intro hall B hB
    obtain ⟨hBA, hQ⟩ := (VE.Compose.baseAdmissibleP_append _ _ _ B).mp hB
    have hBs : BaseAdmissibleP (correlate (sup D).1) (slotP D) B :=
      ⟨hBA.1, fun a ha => hBA.2 a (List.mem_append_left _ ha)⟩
    obtain ⟨c, hc, he, _⟩ := encodes_unique D h hch hs B hBs
    have hcm : complete D c = true := by
      simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
    have hAc := (encodes_atoms D c hcm B he A).mp (fun a ha => hBA.2 a (List.mem_append_right _ ha))
    have hdown := base_down D h hch hs c hc B hBs he
    have hY := hall c hc hAc _
      ⟨hdown.1, (VE.Compose.sat_append _ _ _).mpr ⟨hdown.2, (hq.2 c hc B hBs he).mp hQ⟩⟩
    exact (superpose_conflict_iff D h hch hs c hc B hBs he).mpr hY

/-- ALL under `A` with the carried family. `hQw` (not in the approved text, which is false without it; see the
    module comment) types `Q` over `sup D`'s base vocabulary, as every slot premise is. -/
theorem superpose_all_extra (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) (A : Choice) (hA : ∀ x ∈ A, (candidate D x.1 x.2).isSome)
    (Q : List VE.Formula) (Q' : Choice → List VE.Formula) (hq : Transfers.{u} D Q Q')
    (hQw : VE.Compose.SlotWellFormed (correlate (sup D).1) Q)
    (hcf : ConflictFreeP.{u} (correlate (sup D).1) (slotUnder D A ++ Q))
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) [])
    (hφ : φ.WellFormed (sharedEnv D) []) (cert : VE.Tableau.Certificate)
    (accepted : supCertificateCheckExtra D A Q Γ φ cert = true)
    (c : Choice) (hc : Compatible D c) (hAc : ∀ x ∈ A, x ∈ c) (B : VE.Structure.{u})
    (hB : BaseAdmissibleP (correlate (choiceDoc D c).1) (VE.Rights.limPremises (choiceDoc D c).1 ++ Q' c) B)
    (hp : Sat (expand (choiceDoc D c).1 B) ((choiceDoc D c).2 ++ Γ)) :
  φ.denote (expand (choiceDoc D c).1 B) [] := by
  have hh : Hyps D := ⟨h, hch, hs⟩
  have hX : correlate (sup D).1 = (sup D).1.soft := sup_correlate hh
  have hYc : correlate (choiceDoc D c).1 = (choiceDoc D c).1.soft := choice_correlate hh c
  have hYl := (correlate_noRights _ (choiceDoc_noRights D c hh.noRights)).2
  have hvY := choice_valid hh hc
  have hvX := sup_valid hh
  have hwf := sup_wfSoft hh
  unfold expand at hp ⊢
  rw [hYc] at hp ⊢
  rw [hYc, hYl, List.nil_append] at hB
  have hcB : ConstantsTyped (soften (choiceDoc D c).1.soft) B := hB.1.1.1.1
  have hwY : ∀ a ∈ (choiceDoc D c).2 ++ Γ, a.WellFormed (sharedEnv D) [] := by
    intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · exact asserted_shared D h hh.ready c hc a ha
    · exact hΓ a ha
  -- lift to a base with an element; the family holds there too
  obtain ⟨hB', hQ'⟩ := (VE.Compose.adjoin_baseAdmissibleP _ (Q' c) B).mpr hB
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
  have hUQ : Sat (upB D c (adjoinOne B) e) Q :=
    (hq.2 c hc _ hUs henc).mpr ((sat_pull_up hh hq.1 hc (adjoinOne B) e hB'.1.1).mpr hQ')
  have hcfU := hcf _ (by rw [hX]; exact ⟨⟨hUbase, hUsoft⟩, (VE.Compose.sat_append _ _ _).mpr ⟨hUslot, hUQ⟩⟩)
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
  have hslotwf := (VE.Compose.slotWellFormed_append _ _ _).mpr ⟨slot_wellFormed D h hch hs A hA, hQw⟩
  rw [hX] at hslotwf
  have hsv := sup_softValid hh
  have restrict : ∀ a : VE.Formula, a.WellFormed (envAt (soften (sup D).1.soft) 0) [] →
      a.denote (upB D c (adjoinOne B) e) [] → a.denote S0 [] := fun a hw ha => by
    rw [← hr0] at ha
    exact (VE.Norms.restrictAll_denote a [] hw S0 []).mp ha
  have accepted' := accepted
  unfold supCertificateCheckExtra at accepted'
  rw [hX] at accepted'
  have hφS := VE.Compose.slot_route_intended _ hwf (slotUnder D A ++ Q) ((sup D).2 ++ Γ) φ cert accepted' S0 hA0
    ((VE.SoftNorms.soft_elaborate_iff _ hwf S0).mp (fun a ha => hsat0 a (List.mem_append_right _ ha)))
    (fun a ha => hsat0 a (List.mem_append_left _ (List.mem_append_left _ (List.mem_append_left _ ha))))
    (fun a ha => hsat0 a (List.mem_append_left _ (List.mem_append_right _ ha)))
    (fun a ha => hsat0 a (List.mem_append_left _ (List.mem_append_left _ (List.mem_append_right _ ha))))
    (fun a ha => restrict a (hsv.premTyped a ha) (hUsoft a ha))
    (fun a ha => restrict a (hslotwf a ha) ((VE.Compose.sat_append _ _ _).mpr ⟨hUslot, hUQ⟩ a ha))
    (fun a ha => by
      rcases List.mem_append.mp ha with ha' | ha'
      · exact (key a (hsupwf a ha')).mpr (hXsat a ha)
      · exact (key a (shared_lift hh (hΓ a ha'))).mpr (hXsat a ha))
  have h1 := (key φ (shared_lift hh hφ)).mp hφS
  exact (canon_pull_up hh hc _ e hB' hφ []).mp ((hsh φ hφ).mp h1)

theorem superpose_countermodel_extra {α : Type u} [DecidableEq α] (D : Doc) (h : WellFormedDoc D = true)
    (hch : D.chain ≠ .rights) (hs : superposable D = true) (A : Choice)
    (Q : List VE.Formula) (Q' : Choice → List VE.Formula) (hq : Transfers.{u} D Q Q')
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) [])
    (hφ : φ.WellFormed (sharedEnv D) []) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt (soften (correlate (sup D).1)) 0)) (hm : supModelCheckExtra D A Q Γ M = true)
    (hn : (VE.SoftNorms.circ (correlate (sup D).1) φ).eval M [] = false) :
  ∃ c, Compatible D c ∧ (∀ x ∈ A, x ∈ c) ∧ Encodes D c M.asStructure ∧
    BaseAdmissibleP (correlate (choiceDoc D c).1) (VE.Rights.limPremises (choiceDoc D c).1 ++ Q' c)
      (pull D c M.asStructure) ∧
    Sat (expand (choiceDoc D c).1 (pull D c M.asStructure)) ((choiceDoc D c).2 ++ Γ) ∧
    ¬ φ.denote (expand (choiceDoc D c).1 (pull D c M.asStructure)) [] := by
  have hh : Hyps D := ⟨h, hch, hs⟩
  simp only [supModelCheckExtra, Bool.and_eq_true, List.all_eq_true] at hm
  obtain ⟨hb, hall⟩ := hm
  obtain ⟨hBA, hQ⟩ := (VE.Compose.baseAdmissibleP_append _ _ _ _).mp
    (VE.Compose.baseAdmissibleP_of_valid _ _ M valid hb)
  have hBs : BaseAdmissibleP (correlate (sup D).1) (slotP D) M.asStructure :=
    ⟨hBA.1, fun a ha => hBA.2 a (List.mem_append_left _ ha)⟩
  obtain ⟨c, hc, he, _⟩ := encodes_unique D h hch hs M.asStructure hBs
  have hcomp : complete D c = true := by
    simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
  have hA := (encodes_atoms D c hcomp M.asStructure he A).mp (fun a ha => hBA.2 a (List.mem_append_right _ ha))
  have hdown := base_down D h hch hs c hc _ hBs he
  obtain ⟨_, hsh, has⟩ := superpose_situation D h hch hs c hc _ hBs he
  -- the model's truth through the outcome substitution is truth on the expansion
  have hBX := hBs
  rw [sup_correlate hh] at hBX
  have hcirc : ∀ a : VE.Formula, a.WellFormed (envAt (soften (sup D).1.soft) (size (soften (sup D).1.soft))) [] →
      ((circ (correlate (sup D).1) a).eval M [] = true ↔ a.denote (expand (sup D).1 M.asStructure) []) := by
    intro a ha
    rw [VE.eval_iff_denote, expand, sup_correlate hh]
    exact VE.SoftNorms.circ_canon (sup_softValid hh) _ hBX.1.1 a [] ha [] (typed_nil _)
  have hsupwf : ∀ a ∈ (sup D).2, a.WellFormed (envAt (soften (sup D).1.soft) (size (soften (sup D).1.soft))) [] := by
    have hw : sideWF D (sup D) = true := by
      have := hs; simp only [superposable, Bool.and_eq_true] at this; exact this.2
    simp only [sideWF, Bool.and_eq_true, List.all_eq_true] at hw
    intro a ha
    have := (VE.check_iff_wellFormed _ _ _).mp (hw.2 a ha)
    rwa [sup_correlate hh] at this
  refine ⟨c, hc, hA, he, ⟨hdown.1, (VE.Compose.sat_append _ _ _).mpr
    ⟨hdown.2, (hq.2 c hc _ hBs he).mp hQ⟩⟩, fun a ha => ?_, fun hφY => ?_⟩
  · rcases List.mem_append.mp ha with ha | ha
    · exact (has.mp (fun b hb => (hcirc b (hsupwf b hb)).mp (hall b (List.mem_append_left _ hb)))) a ha
    · exact (hsh a (hΓ a ha)).mp ((hcirc a (shared_lift hh (hΓ a ha))).mp (hall a (List.mem_append_right _ ha)))
  · have := (hcirc φ (shared_lift hh hφ)).mpr ((hsh φ hφ).mpr hφY)
    rw [hn] at this; cases this

theorem transfers_nil (D : Doc) : Transfers.{u} D [] (fun _ => []) :=
  ⟨fun _ _ _ ha => (nomatch ha), fun _ _ B _ _ => ⟨fun _ => VE.Compose.sat_nil _, fun _ => VE.Compose.sat_nil B⟩⟩

/-! ## The approved S2a statements are the instances at `transfers_nil` -/

theorem supCertificateCheckExtra_nil (D : Doc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate) : supCertificateCheckExtra D A [] Γ φ cert = supCertificateCheck D A Γ φ cert := by
  simp only [supCertificateCheckExtra, supCertificateCheck, List.append_nil]

theorem supModelCheckExtra_nil {α : Type u} [DecidableEq α] (D : Doc) (A : Choice) (Γ : List VE.Formula)
    (M : VE.FiniteModel α) : supModelCheckExtra D A [] Γ M = supModelCheck D A Γ M := by
  simp only [supModelCheckExtra, supModelCheck, List.append_nil]

theorem baseAdmissibleR_nil (X : RightsDoc) (B : VE.Structure.{u}) :
    BaseAdmissibleP (correlate X) (VE.Rights.limPremises X ++ []) B ↔ VE.Rights.BaseAdmissibleR X B := by
  rw [List.append_nil]; exact Iff.rfl

example (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) (A : Choice) (hA : ∀ x ∈ A, (candidate D x.1 x.2).isSome) :
    ConflictFreeP.{u} (correlate (sup D).1) (slotUnder D A) ↔
      ∀ c, Compatible D c → (∀ x ∈ A, x ∈ c) → VE.Rights.RightsConflictFree.{u} (choiceDoc D c).1 := by
  have := superpose_conflict_free_extra.{u} D h hch hs A hA [] (fun _ => []) (transfers_nil D)
  rw [List.append_nil] at this
  refine this.trans (forall_congr' fun c => imp_congr_right fun _ => imp_congr_right fun _ =>
    forall_congr' fun B => imp_congr_left (baseAdmissibleR_nil _ B))

example (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights) (hs : superposable D = true)
    (A : Choice) (hA : ∀ x ∈ A, (candidate D x.1 x.2).isSome)
    (hcf : ConflictFreeP.{u} (correlate (sup D).1) (slotUnder D A))
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) [])
    (hφ : φ.WellFormed (sharedEnv D) []) (cert : VE.Tableau.Certificate)
    (accepted : supCertificateCheck D A Γ φ cert = true)
    (c : Choice) (hc : Compatible D c) (hAc : ∀ x ∈ A, x ∈ c) (B : VE.Structure.{u})
    (hB : VE.Rights.BaseAdmissibleR (choiceDoc D c).1 B)
    (hp : Sat (expand (choiceDoc D c).1 B) ((choiceDoc D c).2 ++ Γ)) :
    φ.denote (expand (choiceDoc D c).1 B) [] :=
  superpose_all_extra D h hch hs A hA [] (fun _ => []) (transfers_nil D) (fun _ ha => nomatch ha)
    (by rw [List.append_nil]; exact hcf) Γ φ hΓ hφ cert (by rw [supCertificateCheckExtra_nil]; exact accepted)
    c hc hAc B ((baseAdmissibleR_nil _ B).mpr hB) hp

example {α : Type u} [DecidableEq α] (D : Doc) (h : WellFormedDoc D = true)
    (hch : D.chain ≠ .rights) (hs : superposable D = true) (A : Choice)
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) [])
    (hφ : φ.WellFormed (sharedEnv D) []) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt (soften (correlate (sup D).1)) 0)) (hm : supModelCheck D A Γ M = true)
    (hn : (circ (correlate (sup D).1) φ).eval M [] = false) :
    ∃ c, Compatible D c ∧ (∀ x ∈ A, x ∈ c) ∧ Encodes D c M.asStructure ∧
      VE.Rights.BaseAdmissibleR (choiceDoc D c).1 (pull D c M.asStructure) ∧
      Sat (expand (choiceDoc D c).1 (pull D c M.asStructure)) ((choiceDoc D c).2 ++ Γ) ∧
      ¬ φ.denote (expand (choiceDoc D c).1 (pull D c M.asStructure)) [] := by
  obtain ⟨c, hc, hA, he, hB, hp, hφc⟩ := superpose_countermodel_extra D h hch hs A [] (fun _ => [])
    (transfers_nil D) Γ φ hΓ hφ M valid (by rw [supModelCheckExtra_nil]; exact hm) hn
  exact ⟨c, hc, hA, he, (baseAdmissibleR_nil _ _).mp hB, hp, hφc⟩

/-! ## Superposition under the completion (RD-6b) -/

theorem fill_transfers (N : NDoc) (hN : WellFormedND N = true) (hF : WellFormedDoc (fillDoc N) = true)
    (hs : superposable (fillDoc N) = true) (hsu : VE.NormDefaults.WellFormedU (supU N) = true) :
  Transfers.{u} (fillDoc N) (VE.NormDefaults.fillPremises (supU N)) (fun c => VE.NormDefaults.fillPremises (choiceU N c)) := by
  refine ⟨fun c hc a ha => ?_, fun c hc B hB he => fillPremises_pull hN hF hs hc hB he hsu⟩
  have hh := hyps_fill hN hF hs
  have hw := fillPremises_wf_v (valid_fill_choiceU hN hF hs hc) a ha
  have he : choiceEnvFull (fillDoc N) c = envAt (VE.NormDefaults.fill (choiceU N c))
      (size (VE.NormDefaults.fill (choiceU N c))) := by
    unfold choiceEnvFull; rw [choice_correlate hh c, ← fill_choiceU hN hF hs]
  rw [he]; exact VE.Norms.envAt_mono (Nat.zero_le _) a [] hw
theorem nd_superpose_conflict_free (N : NDoc) (hN : WellFormedND N = true) (hF : WellFormedDoc (fillDoc N) = true)
    (hs : superposable (fillDoc N) = true) (hsu : VE.NormDefaults.WellFormedU (supU N) = true)
    (A : Choice) (hA : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome) :
  ConflictFreeP.{u} (correlate (sup (fillDoc N)).1) (slotUnder (fillDoc N) A ++ VE.NormDefaults.fillPremises (supU N)) ↔
    ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) := by
  have hh := hyps_fill hN hF hs
  have hA' : ∀ x ∈ A, (candidate (fillDoc N) x.1 x.2).isSome := fun x hx => by
    rw [candidate_fillDoc]; simpa using hA x hx
  rw [superpose_conflict_free_extra (fillDoc N) hF hh.chain hs A hA' _ _ (fill_transfers N hN hF hs hsu)]
  have hY : ∀ c, VE.Compose.ConflictFreeP.{u} (correlate (choiceDoc (fillDoc N) c).1)
      (VE.Rights.limPremises (choiceDoc (fillDoc N) c).1 ++ VE.NormDefaults.fillPremises (choiceU N c)) ↔
      VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) := by
    intro c
    have hX := strict_choice_fillDoc N (wellFormedND_parts hN).2.1 c
    have hfc := (fillDoc_choice N (wellFormedND_parts hN).2.1 (wellFormedND_parts hN).2.2.1 c).1
    unfold VE.Compose.ConflictFreeP VE.NormDefaults.ConflictFreeU
    rw [hfc]
    exact forall_congr' fun B => imp_congr_left (baseAdmissibleP_choiceU hN c B)
  exact forall_congr' fun c => by rw [compatible_fillDoc, hY c]
theorem nd_superpose_all (N : NDoc) (hN : WellFormedND N = true) (hF : WellFormedDoc (fillDoc N) = true)
    (hs : superposable (fillDoc N) = true) (hsu : VE.NormDefaults.WellFormedU (supU N) = true)
    (A : Choice) (hA : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome)
    (hcf : ConflictFreeP.{u} (correlate (sup (fillDoc N)).1)
        (slotUnder (fillDoc N) A ++ VE.NormDefaults.fillPremises (supU N)))
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv (fillDoc N)) [])
    (hφ : φ.WellFormed (sharedEnv (fillDoc N)) []) (cert : VE.Tableau.Certificate)
    (accepted : supCertificateCheckExtra (fillDoc N) A (VE.NormDefaults.fillPremises (supU N)) Γ φ cert = true) :
  ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ := by
  intro c hc hAc S hBU hE hΓS
  have hh := hyps_fill hN hF hs
  have hp := wellFormedND_parts hN
  have hc' : Compatible (fillDoc N) c := (compatible_fillDoc N c).mpr hc
  have hA' : ∀ x ∈ A, (candidate (fillDoc N) x.1 x.2).isSome := fun x hx => by
    rw [candidate_fillDoc]; simpa using hA x hx
  have hQw : VE.Compose.SlotWellFormed (correlate (sup (fillDoc N)).1) (VE.NormDefaults.fillPremises (supU N)) := by
    intro a ha
    have := VE.NormDefaults.Wire.fillPremises_wellFormed hsu a ha
    rwa [← (fillDoc_sup N hp.2.1 hp.2.2.1).1] at this
  have hfc := fillDoc_choice N hp.2.1 hp.2.2.1 c
  have hvY := valid_fill_choiceU hN hF hs hc'
  have key := superpose_all_extra (fillDoc N) hF hh.chain hs A hA' _ _ (fill_transfers N hN hF hs hsu) hQw hcf Γ φ
    hΓ hφ cert accepted c hc' hAc _ ((baseAdmissibleP_choiceU hN c _).mpr hBU)
  unfold expand at key
  rw [hfc.1, hfc.2] at key
  have hlift : ∀ a : VE.Formula, a.WellFormed (sharedEnv (fillDoc N)) [] →
      a.WellFormed (envAt (VE.NormDefaults.fill (choiceU N c)) (size (VE.NormDefaults.fill (choiceU N c)))) [] := by
    intro a ha
    have := shared_liftY hh c ha
    rwa [fill_choiceU hN hF hs]
  have hsh := asserted_shared (fillDoc N) hF hh.ready c hc'
  rw [hfc.2] at hsh
  refine (documentExpansion_canon hvY hE φ (hlift φ hφ)).mpr (key fun a ha => ?_)
  rcases List.mem_append.mp ha with ha' | ha'
  · exact (documentExpansion_canon hvY hE a (hlift a (hsh a ha'))).mp (hΓS a ha)
  · exact (documentExpansion_canon hvY hE a (hlift a (hΓ a ha'))).mp (hΓS a ha)

end Extra
end VE.Readings
