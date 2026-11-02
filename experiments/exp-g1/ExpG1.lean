import VE.Readings.SupPacks
import VE.Readings.SupExtraExamples
import VE.NormDefaults.LayeredEntail

/-! EXP-G1: may one pack's premises mention another pack's names? (docs/spec/profile-composition-PLAN.md, EXP-G1).
Scratch work: not imported by `lean/VE.lean`, compiled with `lake env lean` from `lean/`; see REPORT.md.

Part 1 is on main's definitions. Part 2 is a COPY of the unbuilt G1b text (profile-composition.md 1.6): the statement
`acceptanceXV` is a `Prop` here, never a theorem. Part 3 is fixture `EXP-G1-mixed`, the condition PC-11 cites. -/
namespace ExpG1
open VE.NormDefaults VE.NormDefaults.Packs
open VE.Readings (Doc Choice Transfers)
open VE.Norms (envAt size Sat restrictAll)
universe u

/-! ## Part 1: the order of `X` on main's definitions -/

theorem X_perm {qs qs' : List Pack} (h : qs.Perm qs') : (X qs).Perm (X qs') :=
  (h.flatMap_right _).map _

theorem sat_perm (S : VE.Structure.{u}) {as bs : List VE.Formula} (h : as.Perm bs) : Sat S as ↔ Sat S bs :=
  ⟨fun hs a ha => hs a (h.mem_iff.mpr ha), fun hs a ha => hs a (h.mem_iff.mp ha)⟩

/-- `Sat` does not read the order of `X`. -/
theorem sat_X_perm (S : VE.Structure.{u}) {qs qs' : List Pack} (h : qs.Perm qs') : Sat S (X qs) ↔ Sat S (X qs') :=
  sat_perm S (X_perm h)

/-- `Transfers` does not read the order of either family. -/
theorem transfers_perm {D : Doc} {Q Q₂ : List VE.Formula} {Qc Qc₂ : Choice → List VE.Formula}
    (hQ : Q.Perm Q₂) (hc : ∀ c, (Qc c).Perm (Qc₂ c)) (h : Transfers.{u} D Q Qc) : Transfers.{u} D Q₂ Qc₂ :=
  ⟨fun c hcc a ha => h.1 c hcc a ((hc c).mem_iff.mpr ha), fun c hcc B hB he =>
    (sat_perm B hQ).symm.trans ((h.2 c hcc B hB he).trans (sat_perm _ (hc c)))⟩

/-- `transfers_X`'s conclusion does not read the order of the packs. -/
theorem transfers_X_perm (D : Doc) {qs qs' : List Pack} (h : qs.Perm qs') (Qc : Pack → Choice → List VE.Formula) :
    Transfers.{u} D (X qs) (fun c => qs.flatMap (fun p => Qc p c)) ↔
      Transfers.{u} D (X qs') (fun c => qs'.flatMap (fun p => Qc p c)) :=
  ⟨transfers_perm (X_perm h) (fun _ => h.flatMap_right _),
    transfers_perm (X_perm h.symm) (fun _ => h.symm.flatMap_right _)⟩

/-- `transfers_X` itself, at either order, from the same per-pack hypotheses: no hypothesis mentions another pack. -/
theorem transfers_X_either (D : Doc) {qs qs' : List Pack} (hp : qs.Perm qs') (Qc : Pack → Choice → List VE.Formula)
    (h : ∀ p ∈ qs, Transfers.{u} D (p.labelled.map (·.2)) (Qc p)) :
    Transfers.{u} D (X qs') (fun c => qs'.flatMap (fun p => Qc p c)) :=
  VE.Readings.transfers_X D qs' Qc (fun p hm => h p (hp.mem_iff.mpr hm))

theorem baseAdmissibleX_perm (U : UDoc) {X₁ X₂ : List VE.Formula} (h : X₁.Perm X₂) (B : VE.Structure.{u}) :
    Wire.BaseAdmissibleX U X₁ B ↔ Wire.BaseAdmissibleX U X₂ B :=
  and_congr_right fun _ => sat_perm B h

/-- G1 (`EntailsX`, main's), the constraint-pack case: no hypothesis at all. -/
theorem entailsX_perm (U : UDoc) {qs qs' : List Pack} (h : qs.Perm qs') (Γ : List VE.Formula) (φ : VE.Formula) :
    EntailsX.{u} U (X qs) Γ φ ↔ EntailsX.{u} U (X qs') Γ φ :=
  forall_congr' fun S => by rw [baseAdmissibleX_perm U (X_perm h) (restrictAll (fill U).T S)]

/-- `acceptanceX` (main's, proved) from a certificate at one order gives the entailment at the other. -/
theorem acceptanceX_order_free (U : UDoc) (hU : WellFormedU U = true) {qs qs' : List Pack} (h : qs.Perm qs')
    (hX : ∀ a ∈ X qs, a.WellFormed (envAt (fill U) 0) []) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (fill U) (size (fill U))) (Wire.premisesX U (X qs) Γ) φ cert = true) :
    EntailsX.{u} U (X qs') Γ φ :=
  (entailsX_perm U h Γ φ).mp (acceptanceX U hU (X qs) hX Γ φ cert hv)

/-! ## Part 2: G1b, a COPY of the unbuilt statement (profile-composition.md 1.6, at 3dfadd302) -/

def fullEnvX (U : UDoc) (qs : List Pack) : VE.Environment :=
  extendEnv (fullEnv U) (qs.flatMap (·.decls)) (qs.flatMap (·.consts))

def BaseAdmissibleXV (U : UDoc) (qs : List Pack) (B : VE.Structure.{u}) : Prop :=
  B.Admissible (envX U qs) ∧ Sat B (VE.Norms.backgroundBase (fill U)) ∧ Sat B (fillPremises U) ∧ Sat B (X qs)

def DocumentExpansionXV (U : UDoc) (qs : List Pack) (B S : VE.Structure.{u}) : Prop :=
  restrictAll (fill U).T S = B ∧ S.Admissible (fullEnvX U qs) ∧
    Sat S (VE.Norms.background (fill U) ++ VE.Norms.elaborate (fill U).T)

def EntailsXV (U : UDoc) (qs : List Pack) (Γ : List VE.Formula) (φ : VE.Formula) : Prop :=
  ∀ S : VE.Structure.{u}, BaseAdmissibleXV U qs (restrictAll (fill U).T S) →
    DocumentExpansionXV U qs (restrictAll (fill U).T S) S → Sat S Γ → φ.denote S []

/-- `acceptanceXV`'s statement as a `Prop`: nothing here proves it (PK-1's owner builds it). -/
def AcceptanceXV : Prop :=
  ∀ (U : UDoc) (_ : WellFormedU U = true) (qs : List Pack)
    (_ : ∀ n ∈ names qs, declaredIn (fullEnv U) n = false)
    (_ : ∀ a ∈ X qs, a.WellFormed (envX U qs) []) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate)
    (_ : VE.Tableau.checkCertificate (fullEnvX U qs) (Wire.premisesX U (X qs) Γ) φ cert = true),
    EntailsXV.{u} U qs Γ φ

/-! ### The order claim over the copy -/

theorem lookup_perm {β : Type} {l l' : List (String × β)} (h : l.Perm l') (hn : (l.map (·.1)).Nodup) (n : String) :
    l.lookup n = l'.lookup n := by
  induction h with
  | nil => rfl
  | cons x _ ih =>
    obtain ⟨k, v⟩ := x
    simp only [List.map_cons, List.nodup_cons] at hn
    simp only [List.lookup, ih hn.2]
  | swap x y l =>
    obtain ⟨k₁, v₁⟩ := x
    obtain ⟨k₂, v₂⟩ := y
    simp only [List.map_cons, List.nodup_cons, List.mem_cons, not_or] at hn
    have hne : k₂ ≠ k₁ := hn.1.1
    simp only [List.lookup]
    by_cases h₁ : n = k₁
    · subst h₁
      have : (n == k₂) = false := by simpa using hne.symm
      simp [this]
    · have : (n == k₁) = false := by simpa using h₁
      simp [this]
  | trans h₁ _ ih₁ ih₂ =>
    rw [ih₁ hn, ih₂ ((h₁.map _).nodup_iff.mp hn)]

theorem declKeys_sublist (qs : List Pack) : ((qs.flatMap (·.decls)).map (·.1)).Sublist (names qs) := by
  induction qs with
  | nil => exact List.Sublist.refl _
  | cons p ps ih =>
    simp only [List.flatMap_cons, List.map_append, names, Pack.names]
    exact (List.sublist_append_left _ _).append ih

theorem constKeys_sublist (qs : List Pack) : ((qs.flatMap (·.consts)).map (·.1)).Sublist (names qs) := by
  induction qs with
  | nil => exact List.Sublist.refl _
  | cons p ps ih =>
    simp only [List.flatMap_cons, List.map_append, names, Pack.names]
    exact (List.sublist_append_right _ _).append ih

/-- `extendEnv` reads the order of its lists only through `lookup`'s first match. -/
theorem extendEnv_perm (E : VE.Environment) {qs qs' : List Pack} (h : qs.Perm qs') (hd : (names qs).Nodup) :
    extendEnv E (qs.flatMap (·.decls)) (qs.flatMap (·.consts)) =
      extendEnv E (qs'.flatMap (·.decls)) (qs'.flatMap (·.consts)) := by
  have h₁ := lookup_perm (h.flatMap_right (·.decls)) (hd.sublist (declKeys_sublist qs))
  have h₂ := lookup_perm (h.flatMap_right (·.consts)) (hd.sublist (constKeys_sublist qs))
  simp only [extendEnv, h₁, h₂]

theorem envX_perm (U : UDoc) {qs qs' : List Pack} (h : qs.Perm qs') (hd : (names qs).Nodup) :
    envX U qs = envX U qs' := extendEnv_perm _ h hd

theorem fullEnvX_perm (U : UDoc) {qs qs' : List Pack} (h : qs.Perm qs') (hd : (names qs).Nodup) :
    fullEnvX U qs = fullEnvX U qs' := extendEnv_perm _ h hd

theorem names_perm {qs qs' : List Pack} (h : qs.Perm qs') : (names qs).Perm (names qs') := h.flatMap_right _

theorem baseAdmissibleXV_perm (U : UDoc) {qs qs' : List Pack} (h : qs.Perm qs') (hd : (names qs).Nodup)
    (B : VE.Structure.{u}) : BaseAdmissibleXV U qs B ↔ BaseAdmissibleXV U qs' B := by
  simp only [BaseAdmissibleXV, envX_perm U h hd, sat_X_perm B h]

theorem documentExpansionXV_perm (U : UDoc) {qs qs' : List Pack} (h : qs.Perm qs') (hd : (names qs).Nodup)
    (B S : VE.Structure.{u}) : DocumentExpansionXV U qs B S ↔ DocumentExpansionXV U qs' B S := by
  simp only [DocumentExpansionXV, fullEnvX_perm U h hd]

/-- G1b's entailment does not read the order, on a list with distinct names. -/
theorem entailsXV_perm (U : UDoc) {qs qs' : List Pack} (h : qs.Perm qs') (hd : (names qs).Nodup)
    (Γ : List VE.Formula) (φ : VE.Formula) : EntailsXV.{u} U qs Γ φ ↔ EntailsXV.{u} U qs' Γ φ := by
  simp only [EntailsXV, baseAdmissibleXV_perm U h hd, documentExpansionXV_perm U h hd]

/-- `acceptanceXV`'s hypotheses other than the certificate do not read the order. The certificate does: `Trace`
    names premises by index. So one certificate at either order gives the entailment at the other. -/
theorem acceptanceXV_order_free (hA : AcceptanceXV.{u}) (U : UDoc) (hU : WellFormedU U = true) {qs qs' : List Pack}
    (h : qs.Perm qs') (hd : (names qs).Nodup) (hfresh : ∀ n ∈ names qs', declaredIn (fullEnv U) n = false)
    (hX : ∀ a ∈ X qs', a.WellFormed (envX U qs') []) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (fullEnvX U qs) (Wire.premisesX U (X qs) Γ) φ cert = true) :
    EntailsXV.{u} U qs' Γ φ :=
  (entailsXV_perm U h hd Γ φ).mp <| hA U hU qs (fun n hn => hfresh n ((names_perm h).mem_iff.mp hn))
    (fun a ha => envX_perm U h hd ▸ hX a ((X_perm h).mem_iff.mp ha)) Γ φ cert hv

theorem firstRepeat_none : ∀ (seen : List String) (l : List (String × String)), firstRepeat seen l = none →
    (l.map (·.2)).Nodup ∧ ∀ n ∈ l.map (·.2), n ∉ seen
  | _, [], _ => ⟨List.nodup_nil, fun _ hn => nomatch hn⟩
  | seen, (i, n) :: rest, h => by
    simp only [firstRepeat] at h
    split at h
    · cases h
    rename_i hs
    obtain ⟨hn, hr⟩ := firstRepeat_none (n :: seen) rest h
    refine ⟨List.nodup_cons.mpr ⟨fun hm => hr n hm (List.mem_cons_self ..), hn⟩, fun m hm => ?_⟩
    rcases List.mem_cons.mp hm with rfl | hm
    · simpa using hs
    · exact fun hc => hr m hm (List.mem_cons_of_mem _ hc)

theorem named_keys (qs : List Pack) :
    (qs.flatMap (fun p => p.names.map (fun n => (p.id, n)))).map (·.2) = names qs := by
  simp [names, List.map_flatMap, Function.comp_def]

/-- Assembly's own check: every list `assembleIn` returns has distinct names, so "declared by some pack" is "by one". -/
theorem assembleIn_distinct {pre : List (String × String)} {E : VE.Environment} {used : Nat} {ps qs : List Pack}
    (h : assembleIn pre E used ps = .ok qs) : (names qs).Nodup := by
  obtain ⟨_, _, _, _, _, hr, _⟩ := assembleIn_ok h
  simpa [named_keys] using (firstRepeat_none [] _ hr).1

/-- Assembly's own check: `hfresh`, as 1.6 says. -/
theorem assembleIn_fresh {pre : List (String × String)} {E : VE.Environment} {used : Nat} {ps qs : List Pack}
    (h : assembleIn pre E used ps = .ok qs) : ∀ n ∈ names qs, declaredIn E n = false := by
  obtain ⟨_, _, _, _, hf, _⟩ := assembleIn_ok h
  intro n hn
  rw [← named_keys] at hn
  obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hn
  exact hf x hx

/-- The whole order claim for G1b on what `assemble` returns: a certificate at `packOrder`'s order gives the
    entailment at every reordering of the list, with only `hX` (every name is declared) as a typing hypothesis. -/
theorem g1b_order_free (hA : AcceptanceXV.{u}) (U : UDoc) (hU : WellFormedU U = true) {used : Nat} {ps qs qs' : List Pack}
    (hok : assemble U used ps = .ok qs) (h : qs.Perm qs') (hX : ∀ a ∈ X qs, a.WellFormed (envX U qs) [])
    (Γ : List VE.Formula) (φ : VE.Formula) (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (fullEnvX U qs) (Wire.premisesX U (X qs) Γ) φ cert = true) :
    EntailsXV.{u} U qs' Γ φ :=
  (entailsXV_perm U h (assembleIn_distinct hok) Γ φ).mp (hA U hU qs (assembleIn_fresh hok) hX Γ φ cert hv)

end ExpG1
