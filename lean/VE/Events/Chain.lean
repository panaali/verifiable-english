import VE.Events.Wire
import VE.NormDefaults.LayeredAdmission

/-! The chain hook (docs/spec/events-time-causation.md 6.3): a certificate the layered route accepts at PK-1's
assembled `X` with the `events` pack last (`X ++ eventsX V`, `Packs.packOrder`) is an `EntailsX` with the pack's
premises. With `calendar_sat`, every calendar reading that satisfies the other packs, the conventions and `Γ`
satisfies `φ` (D7). `replayEventsEntailment` is the soft route's `norm-defaults-certificate` on such a document, and
`events_wire_acceptance` its wire theorem; the answer-level theorems over situations are et-4c's. -/
namespace VE.Events
open Lean
open VE.NormDefaults (UDoc fill WellFormedU EntailsX)
open VE.NormDefaults.Wire (LayeredU hookPacks hookBlock caseOpenTerms decodeSoftU replayLayeredOn softLabelledU)
open VE.Norms (size envAt)
open VE.Order.ProfileGate (bind_ok)
universe u

/-- Certified entailment at PK-1's assembled X (events last). With `calendar_sat`, every calendar reading that
    satisfies the other packs, the conventions and Γ satisfies φ (D7). -/
theorem events_certificate_calendar (U : UDoc) (h : WellFormedU U = true) (V : EventsEnv) (X Γ : List VE.Formula)
    (φ : VE.Formula) (hX : ∀ a ∈ X ++ eventsX V, a.WellFormed (envAt (fill U) 0) [])
    (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (fill U) (size (fill U)))
      (VE.NormDefaults.Wire.premisesX U (X ++ eventsX V) Γ) φ cert = true) :
    EntailsX.{u} U (X ++ eventsX V) Γ φ :=
  VE.NormDefaults.acceptanceX U h (X ++ eventsX V) hX Γ φ cert hv

/-- A successful hook names the block `decodeEvents` reads: `LinkNotOpen` only refuses. -/
theorem eventsHook_block {environment terms : Json} {H : Option EventsHook} {d : EventsDecoded}
    (h : eventsHook environment terms = .ok H) (hd : hookBlock H = some d) :
    decodeEvents environment = .ok (some d) := by
  unfold eventsHook at h
  split at h
  · obtain ⟨_, _, h⟩ := bind_ok h
    obtain ⟨r, hr, h⟩ := bind_ok h
    obtain ⟨_, _, h⟩ := bind_ok h
    cases h
    have : r = some d := by simpa [hookBlock] using hd
    exact this ▸ decodeEventsWith_ok hr
  · cases h
    simp [hookBlock] at hd

/-- The soft route's `X` with the block's hook: the other packs' premises, then `eventsX V` (`assemble`'s order). -/
theorem hooked_X {environment norms : Json} {H : Option EventsHook} {L : LayeredU} {d : EventsDecoded}
    (h : decodeSoftU environment norms H = .ok L) (hd : hookBlock H = some d) :
    L.X = (softLabelledU L.U L.D).map (·.2) ++ eventsX d.V := by
  obtain ⟨_, src, _, _, hD, _, hl, _⟩ := VE.NormDefaults.Wire.decodeSoftU_source environment norms L h
  simp only [LayeredU.X, hl, hookPacks, hd, Option.map_some, Option.toList_some, VE.NormDefaults.Packs.X,
    VE.NormDefaults.Packs.labelledX, eventsPack, VE.NormDefaults.Wire.softPack, hD, eventsX, d.labelled_eq,
    List.cons_append, List.nil_append, List.flatMap_cons, List.flatMap_nil, List.append_nil, List.map_append]

/-- The rights route's packs with the hook, as `decodeSoftU_source` gives the soft route's. -/
theorem decodeRightsU_packs {environment document : Json} {H : Option EventsHook} {L : LayeredU}
    (h : VE.NormDefaults.Wire.decodeRightsU environment document H = .ok L) :
    ∃ D R, L.X = VE.NormDefaults.Packs.X (VE.NormDefaults.Packs.ordered
      ([VE.NormDefaults.Wire.softPack L.U D, VE.NormDefaults.Wire.rightsPack R] ++ hookPacks H)) := by
  unfold VE.NormDefaults.Wire.decodeRightsU at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨src, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  split at h
  · split at h
    · obtain ⟨_, _, h⟩ := bind_ok h
      obtain ⟨_, _, h⟩ := bind_ok h
      obtain ⟨_, _, h⟩ := bind_ok h
      obtain ⟨_, _, h⟩ := bind_ok h
      obtain ⟨_, _, h⟩ := bind_ok h
      obtain ⟨_, hq, h⟩ := bind_ok h
      cases h
      exact ⟨VE.Rights.correlate src.D, src.D, congrArg VE.NormDefaults.Packs.X (VE.NormDefaults.Packs.assemble_order hq).1⟩
    · cases h
  · cases h

/-- Spec 6.3: a list the row refuses is refused with its text before any events check, one it admits without
`cardinality@0` is gated as the list without `events@0` (`Compose.gate_events`; the `cardinality@0` row refuses
`events@0` by name), and the block's only effect on the route is its pack, last in `X`. -/
theorem events_row_composition (environment terms : Json) (hs : (VE.Compose.listedProfiles environment).Pairwise (· < ·))
    (he : "events@0" ∈ VE.Compose.listedProfiles environment)
    (hk : (VE.Compose.listedProfiles environment).find?
      (fun p => !VE.Compose.profileTable.any (·.profile == p)) = none) :
    (∀ t, VE.Compose.eventsFault (VE.Compose.listedProfiles environment) = some t →
      eventsHook environment terms = .error (VE.Compose.unsupported t)) ∧
    (VE.Compose.eventsFault (VE.Compose.listedProfiles environment) = none →
      "cardinality@0" ∉ VE.Compose.listedProfiles environment →
      VE.Compose.gateOf VE.Compose.profileTable (VE.Compose.listedProfiles environment) =
        VE.Compose.gateOf VE.Compose.profileTable ((VE.Compose.listedProfiles environment).erase "events@0")) ∧
    (∀ (H : Option EventsHook) (d : EventsDecoded), hookBlock H = some d →
      (∀ norms L, decodeSoftU environment norms H = .ok L →
        L.X = (softLabelledU L.U L.D).map (·.2) ++ eventsX d.V) ∧
      (∀ document L, VE.NormDefaults.Wire.decodeRightsU environment document H = .ok L →
        ∃ D R, L.X = VE.NormDefaults.Packs.X [VE.NormDefaults.Wire.softPack L.U D, VE.NormDefaults.Wire.rightsPack R] ++
          eventsX d.V)) := by
  have hg := VE.Compose.gate_events _ hs hk
  refine ⟨fun t ht => ?_, fun ht => ?_, fun H d hd => ⟨fun _ _ h => hooked_X h hd, fun _ L h => ?_⟩⟩
  · rw [ht] at hg
    simp only [] at hg
    unfold eventsHook
    simp [List.contains_iff_mem, he, hg, bind, Except.bind]
  · rw [ht] at hg
    exact hg
  · obtain ⟨D, R, hX⟩ := decodeRightsU_packs h
    refine ⟨D, R, ?_⟩
    rw [hX]
    simp [hookPacks, hd, VE.NormDefaults.Packs.ordered, VE.NormDefaults.Packs.packOrder, VE.NormDefaults.Packs.X,
      VE.NormDefaults.Packs.labelledX, VE.NormDefaults.Wire.softPack, VE.NormDefaults.Wire.rightsPack, eventsPack,
      eventsX, d.labelled_eq]

/-- A replayed entailment on an events document (spec 6.3). -/
structure EventsEntailmentReplay where
  U : UDoc
  V : EventsEnv
  E : VE.Environment
  X : List VE.Formula
  premises : List VE.Formula
  conclusion : VE.Formula
  valid : Bool

/-- The hook, `decodeSoftU` with it, the assembled `X` typed over the route's base environment (the regenerated
environment types the pack, `eventsPremises_wellFormed`, but the route's own environment is the one read here), then
the one replay of the layered route, bound to the environment as written. A list without a block has no pack: its
certificates are `replayUnblockedEntailment`'s. -/
def replayEventsEntailment (j : Json) : Except String EventsEntailmentReplay := do
  let environment ← j.getObjVal? "environment"
  let H ← eventsHook environment (caseOpenTerms j)
  match hookBlock H with
  | none => throw "InvalidInput: events"
  | some d =>
    match decodeSoftU environment (j.getObjValD "norms") H with
    | .error e => throw e
    | .ok L =>
      if hw : L.X.all (·.check (envAt (fill L.U) 0) []) = true then
        let r ← replayLayeredOn L (fun a ha => (VE.check_iff_wellFormed _ _ a).mp (List.all_eq_true.mp hw a ha)) j
        pure ⟨L.U, d.V, d.E, (softLabelledU L.U L.D).map (·.2), r.premises, r.conclusion, r.valid⟩
      else throw "InvalidInput: events"

/-- The wire: a replayed entailment decodes to exactly this block and holds with its premises. -/
theorem events_wire_acceptance (j : Lean.Json) (r : EventsEntailmentReplay) (h : replayEventsEntailment j = .ok r)
    (hv : r.valid = true) :
    (decodeEvents (j.getObjValD "environment")).map (·.map (fun d => (d.V, d.E))) = .ok (some (r.V, r.E)) ∧
      EntailsX.{u} r.U (r.X ++ eventsX r.V) r.premises r.conclusion := by
  unfold replayEventsEntailment at h
  obtain ⟨environment, he, h⟩ := bind_ok h
  have hj : j.getObjValD "environment" = environment := by simp only [Json.getObjValD, he]; rfl
  obtain ⟨H, hH, h⟩ := bind_ok h
  split at h
  · cases h
  rename_i d hd
  split at h
  · cases h
  rename_i L hL
  split at h
  · rename_i hw
    obtain ⟨q, hq, h⟩ := bind_ok h
    cases h
    have hqL := VE.NormDefaults.Wire.replayLayeredOn_L hq
    subst hqL
    refine ⟨by rw [hj, eventsHook_block hH hd]; rfl, ?_⟩
    rw [← hooked_X hL hd]
    exact VE.NormDefaults.Wire.layered_entailment_of_valid q hv
  · cases h

/-- Without a block the hook adds no pack (spec 1.11): `X` is soft's premises, as on the list without `events@0`. -/
theorem unhooked_X {environment norms : Json} {H : Option EventsHook} {L : LayeredU}
    (h : decodeSoftU environment norms H = .ok L) (hd : hookBlock H = none) :
    L.X = (softLabelledU L.U L.D).map (·.2) := by
  obtain ⟨_, src, _, _, hD, _, hl, _⟩ := VE.NormDefaults.Wire.decodeSoftU_source environment norms L h
  simp [LayeredU.X, hl, hookPacks, hd, VE.NormDefaults.Packs.X, VE.NormDefaults.Packs.labelledX,
    VE.NormDefaults.Wire.softPack, hD]

theorem unhooked_X_wellFormed {environment norms : Json} {H : Option EventsHook} {L : LayeredU}
    (h : decodeSoftU environment norms H = .ok L) (hd : hookBlock H = none) :
    ∀ a ∈ L.X, a.WellFormed (envAt (fill L.U) 0) [] := by
  obtain ⟨_, src, _, _, hD, hU, _, _⟩ := VE.NormDefaults.Wire.decodeSoftU_source environment norms L h
  have hw := L.wfU
  rw [unhooked_X h hd, hD]
  rw [hU] at hw ⊢
  simpa using VE.NormDefaults.Wire.softLabelledU_wellFormed src.D _ src.wf hw

/-- `norm-defaults-certificate` on a list with `events@0` and no block: the layered replay over the hook's view, which
neither widens nor narrows the route (spec 1.1), with soft's `X` (`unhooked_X`). A block is `replayEventsEntailment`'s. -/
def replayUnblockedEntailment (j : Json) : Except String VE.NormDefaults.Wire.LayeredEntailment := do
  let environment ← j.getObjVal? "environment"
  let H ← eventsHook environment (caseOpenTerms j)
  match hd : hookBlock H with
  | some _ => throw "InvalidInput: events"
  | none =>
    match hL : decodeSoftU environment (j.getObjValD "norms") H with
    | .error e => throw e
    | .ok L => replayLayeredOn L (unhooked_X_wellFormed hL hd) j

/-- The wire without a block: a replayed entailment holds with soft's premises alone. -/
theorem unblocked_wire_acceptance (j : Lean.Json) (r : VE.NormDefaults.Wire.LayeredEntailment)
    (h : replayUnblockedEntailment j = .ok r) (hv : r.valid = true) :
    r.L.X = (softLabelledU r.L.U r.L.D).map (·.2) ∧ EntailsX.{u} r.L.U r.L.X r.premises r.conclusion := by
  unfold replayUnblockedEntailment at h
  obtain ⟨environment, _, h⟩ := bind_ok h
  obtain ⟨H, _, h⟩ := bind_ok h
  split at h
  · cases h
  rename_i hd
  split at h
  · cases h
  rename_i L hL
  rw [VE.NormDefaults.Wire.replayLayeredOn_L h]
  exact ⟨unhooked_X hL hd, VE.NormDefaults.Wire.replayLayeredOn_L h ▸ VE.NormDefaults.Wire.layered_entailment_of_valid r hv⟩

end VE.Events
