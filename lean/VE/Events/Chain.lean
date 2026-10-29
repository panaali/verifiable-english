import VE.Events.Wire
import VE.NormDefaults.LayeredEntail

/-! The chain hook (docs/spec/events-time-causation.md 6.3): a certificate the layered route accepts at PK-1's
assembled `X` with the `events` pack last (`X ++ eventsX V`, `Packs.packOrder`) is an `EntailsX` with the pack's
premises. With `calendar_sat`, every calendar reading that satisfies the other packs, the conventions and `Γ`
satisfies `φ` (D7). The wire replay (`events_wire_acceptance`) and the answer-level theorems are et-4b's. -/
namespace VE.Events
open VE.NormDefaults (UDoc fill WellFormedU EntailsX)
open VE.Norms (size envAt)
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

end VE.Events
