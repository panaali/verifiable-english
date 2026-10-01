import VE.Rights.Route

/-! The base-premise slot (docs/spec/composition.md 1.4, 1.5, 4.3, 4.4, 9.2).

A slot `P` is a list of closed base formulas over `E′_base := envAt (soften X) 0` that a layer above the
chain adds to base admissibility, as `Soft_T` narrows W1's and `Lim_D` narrows soft's. Everything the soft
route proves for `BaseAdmissible′` is restated here relative to `P`, by the proof the rights route has for
`P := Lim_D` (`lean/VE/Rights/Route.lean`), in which `Lim_D` is used only as satisfied formulas and, where a
premise moves between a structure and its base restriction, as closed formulas typed over `E′_base`. The
rights route is then the instance `P := Lim_D`, by definition. -/
namespace VE.Compose
open VE.Norms
open VE.Route (Unique)
open VE.SoftNorms (SoftDoc soften WellFormedSoft BaseAdmissible' PrefixAdmissible' background' backgroundBase'
  softPremises holdsSoft SoftConflictFree softConflictFreeCheck NoStrictCollision NoHardPairConflict)
universe u

/-! ## Definitions (1.4) -/

/-- Every formula of the slot is closed and well-formed over the base vocabulary of the soft route. -/
def SlotWellFormed (X : SoftDoc) (P : List VE.Formula) : Prop := ∀ a ∈ P, a.WellFormed (envAt (soften X) 0) []
def slotCheck (X : SoftDoc) (P : List VE.Formula) : Bool := P.all (fun a => a.check (envAt (soften X) 0) [])

theorem slotCheck_sound (X : SoftDoc) (P : List VE.Formula) (h : slotCheck X P = true) : SlotWellFormed X P := by
  intro a ha
  simp only [slotCheck, List.all_eq_true] at h
  exact (VE.check_iff_wellFormed _ _ a).mp (h a ha)

def BaseAdmissibleP (X : SoftDoc) (P : List VE.Formula) (B : VE.Structure.{u}) : Prop :=
  BaseAdmissible' X B ∧ Sat B P
def backgroundBaseP (X : SoftDoc) (P : List VE.Formula) : List VE.Formula := backgroundBase' X ++ P
def backgroundP (X : SoftDoc) (P : List VE.Formula) : List VE.Formula := background' X ++ P
def ConflictFreeP (X : SoftDoc) (P : List VE.Formula) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleP X P B → ConflictFree (soften X) B

theorem sat_nil (B : VE.Structure.{u}) : Sat B [] := fun _ h => nomatch h

theorem sat_append (B : VE.Structure.{u}) (P Q : List VE.Formula) : Sat B (P ++ Q) ↔ Sat B P ∧ Sat B Q :=
  ⟨fun h => ⟨fun a ha => h a (List.mem_append_left _ ha), fun a ha => h a (List.mem_append_right _ ha)⟩,
   fun h a ha => (List.mem_append.mp ha).elim (h.1 a) (h.2 a)⟩

/-! ## Identity when unused, and monotonicity -/

theorem slot_empty (X : SoftDoc) (B : VE.Structure.{u}) : BaseAdmissibleP X [] B ↔ BaseAdmissible' X B :=
  ⟨fun h => h.1, fun h => ⟨h, sat_nil B⟩⟩

theorem slot_empty_conflictFree (X : SoftDoc) : ConflictFreeP.{u} X [] ↔ SoftConflictFree.{u} X :=
  ⟨fun h B hB => h B ((slot_empty X B).mpr hB), fun h B hB => h B hB.1⟩

theorem slot_empty_background (X : SoftDoc) :
    backgroundP X [] = background' X ∧ backgroundBaseP X [] = backgroundBase' X :=
  ⟨List.append_nil _, List.append_nil _⟩

theorem baseAdmissibleP_append (X : SoftDoc) (P Q : List VE.Formula) (B : VE.Structure.{u}) :
    BaseAdmissibleP X (P ++ Q) B ↔ BaseAdmissibleP X P B ∧ Sat B Q := by
  rw [BaseAdmissibleP, BaseAdmissibleP, sat_append, and_assoc]

theorem slotWellFormed_append (X : SoftDoc) (P Q : List VE.Formula) :
    SlotWellFormed X (P ++ Q) ↔ SlotWellFormed X P ∧ SlotWellFormed X Q :=
  ⟨fun h => ⟨fun a ha => h a (List.mem_append_left _ ha), fun a ha => h a (List.mem_append_right _ ha)⟩,
   fun h a ha => (List.mem_append.mp ha).elim (h.1 a) (h.2 a)⟩

/-- A longer slot admits fewer bases, so conflict-freedom survives appending; the converse is not claimed. -/
theorem conflictFreeP_append (X : SoftDoc) (P Q : List VE.Formula) (hc : ConflictFreeP.{u} X P) :
    ConflictFreeP.{u} X (P ++ Q) :=
  fun B hB => hc B ((baseAdmissibleP_append X P Q B).mp hB).1

/-! ## Gating (1.5, 4.4) -/

def gate (χ : VE.Formula) (P : List VE.Formula) : List VE.Formula := P.map (fun ρ => .implies χ ρ)

theorem gate_wellFormed (X : SoftDoc) (χ : VE.Formula) (P : List VE.Formula)
    (hχ : χ.WellFormed (envAt (soften X) 0) []) (hP : SlotWellFormed X P) : SlotWellFormed X (gate χ P) := by
  intro a ha
  obtain ⟨ρ, hρ, rfl⟩ := List.mem_map.mp ha
  exact ⟨hχ, hP ρ hρ⟩

theorem sat_gate_on (B : VE.Structure.{u}) (χ : VE.Formula) (P : List VE.Formula) (h : χ.denote B []) :
    Sat B (gate χ P) ↔ Sat B P := by
  constructor
  · intro hs ρ hρ
    exact hs _ (List.mem_map.mpr ⟨ρ, hρ, rfl⟩) h
  · intro hs a ha
    obtain ⟨ρ, hρ, rfl⟩ := List.mem_map.mp ha
    exact fun _ => hs ρ hρ

theorem sat_gate_off (B : VE.Structure.{u}) (χ : VE.Formula) (P : List VE.Formula) (h : ¬ χ.denote B []) :
    Sat B (gate χ P) := by
  intro a ha
  obtain ⟨ρ, _, rfl⟩ := List.mem_map.mp ha
  exact fun hχ => absurd hχ h

/-! ## Labels (1.5) -/

abbrev Labelled := List (String × VE.Formula)
def Labelled.formulas (L : Labelled) : List VE.Formula := L.map (·.2)
def Labelled.wellLabelled (L : Labelled) : Bool := decide (L.map (·.1)).Nodup

/-! ## Unique expansion and conflict-freedom relative to a slot (4.3) -/

theorem slot_coherent_expands_all (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula) :
    (∀ B : VE.Structure.{u}, BaseAdmissibleP X P B →
       VE.Route.Unique (VE.Norms.DocumentExpansion (soften X) B)) ↔ ConflictFreeP.{u} X P :=
  ⟨fun hu B hB => (VE.SoftNorms.coherent_expands X h B hB.1.1).mp (hu B hB),
   fun hc B hB => (VE.SoftNorms.coherent_expands X h B hB.1.1).mpr (hc B hB)⟩

/-- W1's conflictFreeCheck on soften X with backgroundBaseP X P in place of Background_base. -/
def slotConflictFreeCheck (X : SoftDoc) (P : List VE.Formula) (certs : List (Option VE.Tableau.Certificate)) :
    Bool :=
  (targets (soften X)).length == certs.length &&
    ((targets (soften X)).zip certs).all (fun (t, c) => match c with
      | some c => VE.Tableau.checkCertificate (envAt (soften X) 0) (backgroundBaseP X P) (targetConclusion t) c
      | none => false)

theorem slot_empty_check (X : SoftDoc) (certs : List (Option VE.Tableau.Certificate)) :
    slotConflictFreeCheck X [] certs = softConflictFreeCheck X certs := by
  unfold slotConflictFreeCheck backgroundBaseP
  rw [List.append_nil]
  rfl

theorem slotConflictFreeCheck_target {X : SoftDoc} {P : List VE.Formula}
    {certs : List (Option VE.Tableau.Certificate)} (hc : slotConflictFreeCheck X P certs = true)
    {t : String × List String × VE.Formula} (ht : t ∈ targets (soften X)) :
    ∃ c, VE.Tableau.checkCertificate (envAt (soften X) 0) (backgroundBaseP X P) (targetConclusion t) c = true := by
  simp only [slotConflictFreeCheck, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hc
  obtain ⟨hl, hall⟩ := hc
  obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp ht
  have hlt : i < (targets (soften X)).length := (List.getElem?_eq_some_iff.mp hi).1
  have hlt' : i < certs.length := hl ▸ hlt
  have hmem : (t, certs[i]) ∈ (targets (soften X)).zip certs := by
    apply List.mem_iff_getElem?.mpr
    refine ⟨i, ?_⟩
    rw [List.getElem?_zip_eq_some]
    exact ⟨hi, List.getElem?_eq_getElem hlt'⟩
  have := hall _ hmem
  cases hci : certs[i] with
  | none => rw [hci] at this; cases this
  | some c => rw [hci] at this; exact ⟨c, this⟩

theorem sat_backgroundBaseP {X : SoftDoc} {P : List VE.Formula} {B : VE.Structure.{u}}
    (hB : BaseAdmissibleP X P B) : ∀ a ∈ backgroundBaseP X P, a.denote B [] := by
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact VE.SoftNorms.sat_backgroundBasePrime hB.1 a ha
  · exact hB.2 a ha

theorem slot_conflict_free (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula)
    (certs : List (Option VE.Tableau.Certificate)) (hc : slotConflictFreeCheck X P certs = true) :
    ConflictFreeP.{u} X P := by
  have hv := valid_of_wellFormed _ (VE.SoftNorms.soften_wellFormed _ h)
  intro B hB
  have cert : ∀ t ∈ targets (soften X), ∀ vs, VE.TupleTyped B t.2.1 vs → ¬ t.2.2.denote B (tupleVal vs) := by
    intro t ht vs hvs
    obtain ⟨c, hcc⟩ := slotConflictFreeCheck_target hc ht
    have he := VE.Tableau.checkCertificate_sound.{u} _ _ _ c hcc B hB.1.1.1 (sat_backgroundBaseP hB)
    exact (bindAll_denote_nil B _ _).mp he vs hvs
  refine ⟨fun r hr vs hvs => ?_, fun pr hpr vs hvs => ?_⟩
  · exact cert (r.name, r.sorts, conflict (soften X) r)
      (List.mem_append_left _ (List.mem_filterMap.mpr ⟨.reg r, hv.regulated r hr, rfl⟩)) vs hvs
  · exact cert (pr.req ++ "->" ++ pr.perm, pr.sorts, pairConflict (soften X) pr)
      (List.mem_append_right _ (List.mem_map.mpr ⟨pr, hpr, rfl⟩)) vs hvs

/-- Soft's backgroundValid' and the finite evaluation of every slot premise. -/
def backgroundValidP {α : Type u} [DecidableEq α] (X : SoftDoc) (P : List VE.Formula) (M : VE.FiniteModel α) :
    Bool :=
  VE.SoftNorms.backgroundValid' X M && P.all (fun a => a.eval M [])

theorem baseAdmissibleP_of_valid {α : Type u} [DecidableEq α] (X : SoftDoc) (P : List VE.Formula)
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (soften X) 0)) (hb : backgroundValidP X P M = true) :
    BaseAdmissibleP X P M.asStructure := by
  simp only [backgroundValidP, Bool.and_eq_true, List.all_eq_true] at hb
  exact ⟨VE.SoftNorms.baseAdmissiblePrime_of_valid _ M valid hb.1,
    fun a ha => (VE.eval_iff_denote M [] a).mp (hb.2 a ha)⟩

theorem slot_conflict_witness_sound {α : Type u} [DecidableEq α] (X : SoftDoc) (h : WellFormedSoft X = true)
    (P : List VE.Formula) (t : String × List String × VE.Formula) (ht : t ∈ targets (soften X))
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (soften X) 0)) (hb : backgroundValidP X P M = true)
    (vs : List α) (typed : VE.TupleTyped M.asStructure t.2.1 vs) (hw : t.2.2.eval M (tupleVal vs) = true) :
    ¬ ConflictFree (soften X) M.asStructure ∧ ¬ ConflictFreeP.{u} X P ∧
    (¬ NoStrictCollision X M.asStructure ∨ ¬ NoHardPairConflict X M.asStructure) := by
  have hB := baseAdmissibleP_of_valid X P M valid hb
  obtain ⟨hn, _, _⟩ := Replay.target_refutes (soften X) (VE.SoftNorms.soften_wellFormed _ h) t ht
    M.asStructure hB.1.1 vs typed ((VE.eval_iff_denote M _ _).mp hw)
  exact ⟨hn, fun hc => hn (hc _ hB), VE.SoftNorms.soft_witness_classified _ h _ hB.1 hn⟩

/-! ## The route relative to a slot (4.3) -/

/-- `PrefixAdmissible′` with the slot on the base restriction. -/
def PrefixAdmissibleP (X : SoftDoc) (P : List VE.Formula) (k : Nat) (S : VE.Structure.{u}) : Prop :=
  PrefixAdmissible' X k S ∧ Sat (restrictAll (soften X).T S) P

section SlotLayer
variable {X : SoftDoc} {P : List VE.Formula} (hv : Valid (soften X)) {k : Nat} {q : Sym}
  (hk : (syms (soften X).T)[k]? = some q)
include hv hk

omit hv in
theorem slot_restrict_admissible (S : VE.Structure.{u}) (h : PrefixAdmissibleP X P (k + 1) S) :
    PrefixAdmissibleP X P k (forget [q.name] S) := by
  refine ⟨VE.SoftNorms.soft_restrict_admissible hk S h.1, ?_⟩
  rw [restrictAll_forget (name_mem_layerNames hk)]
  exact h.2

theorem slot_layer_expands
    (hc : ∀ S₀ : VE.Structure.{u}, PrefixAdmissibleP X P k S₀ → ConflictFreeAtIdx (soften X) k S₀)
    (S₀ : VE.Structure.{u}) (h₀ : PrefixAdmissibleP X P k S₀) :
    Unique fun S => forget [q.name] S = S₀ ∧ PrefixAdmissibleP X P (k + 1) S ∧
      ∀ a ∈ symPremises (soften X).T q, a.denote S [] := by
  have := (local_expands hv hk S₀ h₀.1.1).mpr (hc S₀ h₀)
  refine (unique_congr fun S => ?_).mp this
  constructor
  · rintro ⟨h₁, h₂⟩
    refine ⟨h₁, ⟨⟨h₂, ?_⟩, ?_⟩, symPremises_sat hv hk S h₂⟩
    · rw [← restrictAll_forget (name_mem_layerNames hk) S, h₁]
      exact h₀.1.2
    · rw [← restrictAll_forget (name_mem_layerNames hk) S, h₁]
      exact h₀.2
  · rintro ⟨h₁, h₂, _⟩
    exact ⟨h₁, h₂.1.1⟩

end SlotLayer

/-- The slot layer of the `k`-th layer symbol of `T′`. -/
def slotSymLayer (X : SoftDoc) (P : List VE.Formula) (hv : Valid (soften X)) (k : Nat) (q : Sym)
    (hk : (syms (soften X).T)[k]? = some q)
    (hc : ∀ S₀ : VE.Structure.{u}, PrefixAdmissibleP X P k S₀ → ConflictFreeAtIdx (soften X) k S₀) :
    VE.Route.Layer VE.Route.fol.{u} Unit where
  E_in := envAt (soften X) k
  E_out := envAt (soften X) (k + 1)
  extends_env a h := envAt_mono (Nat.le_succ k) a [] h
  premises _ := symPremises (soften X).T q
  premises_wellFormed _ := symPremises_wellFormed hv hk
  Admissible_in := PrefixAdmissibleP X P k
  Admissible_out := PrefixAdmissibleP X P (k + 1)
  admissible_out _ h := prefixAdmissible_admissible h.1.1
  restrict := forget [q.name]
  restrict_admissible S h := slot_restrict_admissible hk S h
  restrict_holds S a _ ha := denote_forget (self_hidden hv hk) S a [] [] ha
  Intended _ S := LayerMeaning (soften X).T S q
  faithful _ S h := symLayer_faithful hv hk S h.1.1
  expands _ S₀ h₀ := slot_layer_expands hv hk hc S₀ h₀

/-- A composed prefix of the route relative to a slot. -/
structure SlotChain (X : SoftDoc) (P : List VE.Formula) (k : Nat) where
  R : VE.Route.Layer VE.Route.fol.{u} Unit
  E_in : R.E_in = envAt (soften X) 0
  E_out : R.E_out = envAt (soften X) k
  A_in : ∀ S, R.Admissible_in S ↔ PrefixAdmissibleP X P 0 S
  A_out : ∀ S, R.Admissible_out S ↔ PrefixAdmissibleP X P k S
  restrict : ∀ S, R.restrict S = forget ((layerNames (soften X).T).take k) S
  premises : ∀ d, R.premises d = ((syms (soften X).T).take k).flatMap (symPremises (soften X).T)

def slotChain (X : SoftDoc) (P : List VE.Formula) (hv : Valid (soften X))
    (hc : ∀ k (S₀ : VE.Structure.{u}), PrefixAdmissibleP X P k S₀ → ConflictFreeAtIdx (soften X) k S₀) :
    (k : Nat) → k ≤ size (soften X) → SlotChain.{u} X P k
  | 0, _ =>
    { R := VE.Route.Layer.id (envAt (soften X) 0) (PrefixAdmissibleP X P 0) (fun _ h => h.1.1.1)
      E_in := rfl
      E_out := rfl
      A_in := fun _ => Iff.rfl
      A_out := fun _ => Iff.rfl
      restrict := fun S => by simp [VE.Route.Layer.id, forget_nil]
      premises := fun _ => by simp [VE.Route.Layer.id] }
  | k + 1, hk =>
    let C := slotChain X P hv hc k (Nat.le_of_succ_le hk)
    have hlt : k < (syms (soften X).T).length := hk
    let q := (syms (soften X).T)[k]
    have hq : (syms (soften X).T)[k]? = some q := List.getElem?_eq_getElem hlt
    let L := slotSymLayer X P hv k q hq (hc k)
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
        simp [L, slotSymLayer] }

theorem prefixAdmissibleP_zero (X : SoftDoc) (P : List VE.Formula) (B : VE.Structure.{u}) :
    PrefixAdmissibleP X P 0 B ↔ BaseAdmissibleP X P B := by
  constructor
  · rintro ⟨hB, hs⟩
    refine ⟨(VE.SoftNorms.prefixAdmissiblePrime_zero _ B).mp hB, ?_⟩
    rw [restrictAll_self B hB.1.1] at hs
    exact hs
  · rintro ⟨hB, hs⟩
    refine ⟨(VE.SoftNorms.prefixAdmissiblePrime_zero _ B).mpr hB, ?_⟩
    rw [restrictAll_self B hB.1.1]
    exact hs

/-- Conflict-freedom relative to the slot gives every layer's hypothesis. -/
theorem slotChain_hc {X : SoftDoc} {P : List VE.Formula} (hv : Valid (soften X)) (hc : ConflictFreeP.{u} X P) :
    ∀ k (S₀ : VE.Structure.{u}), PrefixAdmissibleP X P k S₀ → ConflictFreeAtIdx (soften X) k S₀ := by
  intro k S₀ h₀
  cases hk : (syms (soften X).T)[k]? with
  | none => simp [ConflictFreeAtIdx, hk]
  | some q =>
    have hB := ((prefix_char hv k (prefixAdmissible_le h₀.1.1) S₀).mp h₀.1.1).2.1
    exact conflictFreeAt_of_base hv hk S₀ h₀.1.1 (hc _ ⟨⟨hB, h₀.1.2⟩, h₀.2⟩)

def slotRouteChain (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula) (hc : ConflictFreeP.{u} X P) :
    SlotChain.{u} X P (size (soften X)) :=
  slotChain X P (valid_of_wellFormed _ (VE.SoftNorms.soften_wellFormed _ h))
    (slotChain_hc (valid_of_wellFormed _ (VE.SoftNorms.soften_wellFormed _ h)) hc) _ (Nat.le_refl _)

theorem slotRouteChain_premises (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula)
    (hc : ConflictFreeP.{u} X P) (d : Unit) : (slotRouteChain X h P hc).R.premises d = elaborate (soften X).T := by
  rw [(slotRouteChain X h P hc).premises, elaborate_eq_flatMap]
  simp [size]

theorem slotRouteChain_restrict (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula)
    (hc : ConflictFreeP.{u} X P) (S : VE.Structure.{u}) :
    (slotRouteChain X h P hc).R.restrict S = restrictAll (soften X).T S := by
  rw [(slotRouteChain X h P hc).restrict, List.take_of_length_le (by simp [size, layerNames])]
  rfl

/-- The composed frozen P0 layers of soften X with BaseAdmissibleP X P as input admissibility. -/
def slotRoute (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula) (hc : ConflictFreeP.{u} X P) :
    { L : VE.Route.Layer VE.Route.fol.{u} Unit // L.E_in = envAt (soften X) 0 ∧
      (∀ B, L.Admissible_in B ↔ BaseAdmissibleP X P B) ∧ L.E_out = envAt (soften X) (size (soften X)) ∧
      L.premises () = elaborate (soften X).T } :=
  ⟨(slotRouteChain X h P hc).R, (slotRouteChain X h P hc).E_in,
    fun B => ((slotRouteChain X h P hc).A_in B).trans (prefixAdmissibleP_zero X P B),
    (slotRouteChain X h P hc).E_out, slotRouteChain_premises X h P hc ()⟩

theorem sat_slot_restrict {X : SoftDoc} {P : List VE.Formula} (hP : SlotWellFormed X P) (S : VE.Structure.{u}) :
    Sat (restrictAll (soften X).T S) P ↔ Sat S P := by
  constructor
  · intro hs a ha
    exact (restrictAll_denote a [] (hP a ha) S []).mp (hs a ha)
  · intro hs a ha
    exact (restrictAll_denote a [] (hP a ha) S []).mpr (hs a ha)

theorem slot_route_backgroundSound (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula)
    (hP : SlotWellFormed X P) (hc : ConflictFreeP.{u} X P) :
    VE.Route.BackgroundSound (slotRoute X h P hc).1 (backgroundP X P) := by
  have hsv := VE.SoftNorms.softValid_of_wellFormed X h
  have hv := valid_of_wellFormed _ (VE.SoftNorms.soften_wellFormed _ h)
  intro d S hS _
  have hpa := ((slotRouteChain X h P hc).A_out S).mp hS
  obtain ⟨_, hB, hM, hPr⟩ := (prefix_char hv _ (Nat.le_refl _) S).mp hpa.1.1
  have hdoc := (sat_document hv S).mpr ⟨(sat_literals_forget _ _ S).mp hB.2, hM, hPr⟩
  have hsoft := (VE.SoftNorms.sat_soft_restrict hsv S).mp hpa.1.2
  have hslot := (sat_slot_restrict hP S).mp hpa.2
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · rcases List.mem_append.mp ha with ha | ha
    · exact hdoc a (List.mem_append_left _ ha)
    · exact hsoft a ha
  · exact hslot a ha

theorem slot_route_backgroundComplete (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula)
    (hP : SlotWellFormed X P) (hc : ConflictFreeP.{u} X P) :
    VE.Route.BackgroundComplete (slotRoute X h P hc).1 (backgroundP X P) := by
  have hsv := VE.SoftNorms.softValid_of_wellFormed X h
  have hv := valid_of_wellFormed _ (VE.SoftNorms.soften_wellFormed _ h)
  intro d S hA hbg hprem
  have hA' : S.Admissible (envAt (soften X) (size (soften X))) := by
    have := (slotRoute X h P hc).2.2.2.1
    simp only [VE.Route.fol] at hA
    rw [this] at hA
    exact hA
  have hprem' : Sat S (elaborate (soften X).T) := by
    have := slotRouteChain_premises X h P hc d
    intro a ha
    exact hprem a (by show a ∈ (slotRouteChain X h P hc).R.premises d; rw [this]; exact ha)
  have hsat : Sat S (background (soften X) ++ elaborate (soften X).T) := fun a ha => by
    rcases List.mem_append.mp ha with ha | ha
    · exact hbg a (List.mem_append_left _ (List.mem_append_left _ ha))
    · exact hprem' a ha
  obtain ⟨hl, hM, hPr⟩ := (sat_document hv S).mp hsat
  apply ((slotRouteChain X h P hc).A_out S).mpr
  refine ⟨⟨(prefix_char hv _ (Nat.le_refl _) S).mpr
    ⟨hA', ⟨restrictAll_admissible _ S hA', (sat_literals_forget _ _ S).mpr hl⟩, hM, hPr⟩, ?_⟩, ?_⟩
  · exact (VE.SoftNorms.sat_soft_restrict hsv S).mpr
      (fun a ha => hbg a (List.mem_append_left _ (List.mem_append_right _ ha)))
  · exact (sat_slot_restrict hP S).mpr (fun a ha => hbg a (List.mem_append_right _ ha))

/-- The first half of slot_route_acceptance: no conflict-freedom, no typing of the slot. -/
theorem slot_route_intended (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envAt (soften X) (size (soften X)))
                  (backgroundP X P ++ elaborate (soften X).T ++ Γ) φ c = true)
    (S : VE.Structure.{u}) (hS : S.Admissible (envAt (soften X) (size (soften X)))) (hsoft : holdsSoft X S)
    (hdef : VE.Norms.definitionsHold (soften X) S) (hprof : VE.Norms.profileHold (soften X) S)
    (hbase : Sat S (VE.Norms.backgroundBase (soften X))) (hsp : Sat S (softPremises X)) (hslot : Sat S P)
    (hΓ : Sat S Γ) :
    φ.denote S [] := by
  apply VE.Tableau.checkCertificate_sound.{u} _ _ _ c accepted S hS
  intro a ha
  simp only [List.mem_append, backgroundP, background', background] at ha
  rcases ha with (((((ha | ha) | ha) | ha) | ha) | ha) | ha
  · exact hdef a ha
  · exact hbase a ha
  · exact hprof a ha
  · exact hsp a ha
  · exact hslot a ha
  · exact (VE.SoftNorms.soft_elaborate_iff _ h S).mpr hsoft a ha
  · exact hΓ a ha

/-- One statement for every base-premise slot: the soft route relative to P. -/
theorem slot_route_acceptance (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula)
    (hP : SlotWellFormed X P) (hc : ConflictFreeP.{u} X P)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envAt (soften X) (size (soften X)))
                  (backgroundP X P ++ elaborate (soften X).T ++ Γ) φ c = true) :
    (∀ S : VE.Structure.{u}, S.Admissible (envAt (soften X) (size (soften X))) → holdsSoft X S →
       VE.Norms.definitionsHold (soften X) S → VE.Norms.profileHold (soften X) S →
       Sat S (VE.Norms.backgroundBase (soften X)) → Sat S (softPremises X) → Sat S P → Sat S Γ → φ.denote S []) ∧
    ((∀ a ∈ Γ, a.WellFormed (envAt (soften X) 0) []) → φ.WellFormed (envAt (soften X) 0) [] →
       ∀ B : VE.Structure.{u}, BaseAdmissibleP X P B → Sat B Γ → φ.denote B []) := by
  refine ⟨fun S hS hsoft hdef hprof hbase hsp hslot hΓ =>
    slot_route_intended X h P Γ φ c accepted S hS hsoft hdef hprof hbase hsp hslot hΓ, fun hΓ hφ => ?_⟩
  let R := slotRoute X h P hc
  have hacc : (VE.Route.Checker.tableau R.1.E_out).valid c
      (VE.Route.checkedPremises R.1 (backgroundP X P) () Γ) φ := by
    show VE.Tableau.checkCertificate R.1.E_out _ φ c = true
    rw [R.2.2.2.1, VE.Route.checkedPremises, R.2.2.2.2]
    exact accepted
  have := VE.Route.route_acceptance R.1 (backgroundP X P) (slot_route_backgroundSound X h P hP hc)
    (VE.Route.Checker.tableau R.1.E_out) () Γ φ c _ φ hacc (List.map_id _) rfl
  intro B hB hs
  exact this.2.2 (by rw [R.2.1]; exact hΓ) (by rw [R.2.1]; exact hφ) B ((R.2.2.1 B).mpr hB) hs

theorem slot_route_countermodel (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula)
    (hP : SlotWellFormed X P) (hc : ConflictFreeP.{u} X P) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAt (soften X) 0) []) (hφ : φ.WellFormed (envAt (soften X) 0) [])
    (B : VE.Structure.{u}) (hB : BaseAdmissibleP X P B) (hs : Sat B Γ) (hn : ¬ φ.denote B []) :
    ∃ S, VE.Norms.DocumentExpansion (soften X) B S ∧ Sat S (softPremises X) ∧ Sat S P ∧ Sat S Γ ∧
      ¬ φ.denote S [] := by
  let R := slotRoute X h P hc
  obtain ⟨S, hr, hA, hsat, hno⟩ := VE.Route.route_countermodel_expands R.1 (backgroundP X P)
    (slot_route_backgroundSound X h P hP hc) () Γ φ (by rw [R.2.1]; exact hΓ) (by rw [R.2.1]; exact hφ)
    B ((R.2.2.1 B).mpr hB) hs hn
  obtain ⟨hbg, hp, hg⟩ := (VE.Route.sat_checked R.1 (backgroundP X P) S () Γ).mp hsat
  have hp' : Sat S (elaborate (soften X).T) := by
    intro a ha
    exact hp a (by show a ∈ R.1.premises (); rw [R.2.2.2.2]; exact ha)
  refine ⟨S, ⟨by rw [← slotRouteChain_restrict X h P hc]; exact hr,
    prefixAdmissible_admissible (((slotRouteChain X h P hc).A_out S).mp hA).1.1, fun a ha => ?_⟩,
    fun a ha => hbg a (List.mem_append_left _ (List.mem_append_right _ ha)),
    fun a ha => hbg a (List.mem_append_right _ ha), hg, hno⟩
  rcases List.mem_append.mp ha with ha | ha
  · exact hbg a (List.mem_append_left _ (List.mem_append_left _ ha))
  · exact hp' a ha

theorem slot_route_entails_iff (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula)
    (hP : SlotWellFormed X P) (hc : ConflictFreeP.{u} X P) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAt (soften X) 0) []) (hφ : φ.WellFormed (envAt (soften X) 0) []) :
    VE.Entails.{u} (envAt (soften X) (size (soften X))) (backgroundP X P ++ elaborate (soften X).T ++ Γ) φ ↔
      ∀ B : VE.Structure.{u}, BaseAdmissibleP X P B → Sat B Γ → φ.denote B [] := by
  let R := slotRoute X h P hc
  have := VE.Route.route_entails_iff R.1 (backgroundP X P) (slot_route_backgroundSound X h P hP hc)
    (slot_route_backgroundComplete X h P hP hc) () Γ φ (by rw [R.2.1]; exact hΓ) (by rw [R.2.1]; exact hφ)
  rw [R.2.2.2.1, VE.Route.checkedPremises, R.2.2.2.2] at this
  rw [VE.Route.fol_entails_iff] at this
  rw [this]
  exact ⟨fun h B hB hs => h B ((R.2.2.1 B).mpr hB) hs, fun h B hB hs => h B ((R.2.2.1 B).mp hB) hs⟩

/-! ## The existing routes are instances -/

open VE.Rights (RightsDoc correlate limPremises WellFormedRights BaseAdmissibleR RightsConflictFree backgroundR
  backgroundBaseR rightsConflictFreeCheck backgroundValidR)

theorem rights_is_slot (D : RightsDoc) (B : VE.Structure.{u}) :
    BaseAdmissibleR D B ↔ BaseAdmissibleP (correlate D) (limPremises D) B :=
  Iff.rfl

theorem rights_conflictFree_is_slot (D : RightsDoc) :
    RightsConflictFree.{u} D ↔ ConflictFreeP.{u} (correlate D) (limPremises D) :=
  Iff.rfl

theorem rights_background_is_slot (D : RightsDoc) :
    backgroundR D = backgroundP (correlate D) (limPremises D) ∧
    backgroundBaseR D = backgroundBaseP (correlate D) (limPremises D) :=
  ⟨rfl, rfl⟩

theorem rights_check_is_slot (D : RightsDoc) (certs : List (Option VE.Tableau.Certificate)) :
    rightsConflictFreeCheck D certs = slotConflictFreeCheck (correlate D) (limPremises D) certs :=
  rfl

theorem rights_valid_is_slot {α : Type u} [DecidableEq α] (D : RightsDoc) (M : VE.FiniteModel α) :
    backgroundValidR D M = backgroundValidP (correlate D) (limPremises D) M :=
  rfl

theorem rights_slot_wellFormed (D : RightsDoc) (h : WellFormedRights D = true) :
    SlotWellFormed (correlate D) (limPremises D) :=
  (VE.Rights.rightsValid_of_wellFormed D h).limTyped

/-- rights_route_acceptance, its statement copied unchanged from lean/VE/Rights/Route.lean, proved here from
the slot theorems alone. The original is not touched. -/
theorem rights_acceptance_from_slot (D : RightsDoc) (h : WellFormedRights D = true) (hc : RightsConflictFree.{u} D)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (VE.Norms.envAt (soften (correlate D)) (size (soften (correlate D))))
                  (backgroundR D ++ VE.Norms.elaborate (soften (correlate D)).T ++ Γ) φ c = true) :
    (∀ S : VE.Structure.{u}, S.Admissible (VE.Norms.envAt (soften (correlate D)) (size (soften (correlate D)))) →
       holdsSoft (correlate D) S → VE.Norms.definitionsHold (soften (correlate D)) S →
       VE.Norms.profileHold (soften (correlate D)) S → Sat S (VE.Norms.backgroundBase (soften (correlate D))) →
       Sat S (softPremises (correlate D)) → Sat S (limPremises D) → Sat S Γ → φ.denote S []) ∧
    ((∀ a ∈ Γ, a.WellFormed (VE.Norms.envAt (soften (correlate D)) 0) []) →
       φ.WellFormed (VE.Norms.envAt (soften (correlate D)) 0) [] →
       ∀ B : VE.Structure.{u}, BaseAdmissibleR D B → Sat B Γ → φ.denote B []) :=
  slot_route_acceptance (correlate D) (VE.Rights.correlate_wellFormed D h) (limPremises D)
    (rights_slot_wellFormed D h) hc Γ φ c accepted

/-- rights_route_countermodel, its statement copied unchanged, proved from the slot theorems alone. -/
theorem rights_countermodel_from_slot (D : RightsDoc) (h : WellFormedRights D = true)
    (hc : RightsConflictFree.{u} D) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (VE.Norms.envAt (soften (correlate D)) 0) [])
    (hφ : φ.WellFormed (VE.Norms.envAt (soften (correlate D)) 0) [])
    (B : VE.Structure.{u}) (hB : BaseAdmissibleR D B) (hs : Sat B Γ) (hn : ¬ φ.denote B []) :
    ∃ S, VE.Norms.DocumentExpansion (soften (correlate D)) B S ∧ Sat S (softPremises (correlate D)) ∧
      Sat S (limPremises D) ∧ Sat S Γ ∧ ¬ φ.denote S [] :=
  slot_route_countermodel (correlate D) (VE.Rights.correlate_wellFormed D h) (limPremises D)
    (rights_slot_wellFormed D h) hc Γ φ hΓ hφ B hB hs hn

end VE.Compose
