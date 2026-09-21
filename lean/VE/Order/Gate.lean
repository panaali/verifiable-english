import VE.CertificateWire

namespace VE.Order
open Lean

/-- This proposed envelope remains rejected by the existing certificate entry
point. No arithmetic proof rules are added or delegated to an external solver. -/
def envelope (vocabulary : Json) : Json := Json.mkObj [
  ("language", .str "ve.core@0.1"),
  ("profiles", toJson (["order@0", "relational-fol@0"] : List String)),
  ("spec_revision", .str "ve-v0.1-order-2026-09-21"),
  ("vocabulary", vocabulary)]

set_option maxRecDepth 4096 in
theorem certificate_profile_gate (vocabulary : Json) :
    VE.Closure.Bridge.decodeEnvironment (envelope vocabulary) =
      .error "unsupported closure environment version/profiles" := by
  rfl

/-- Composition is explicitly unavailable at this implementation boundary. -/
def combinedEnvelope (vocabulary : Json) : Json := Json.mkObj [
  ("language", .str "ve.core@0.1"),
  ("profiles", toJson (["closure@0", "order@0", "relational-fol@0"] : List String)),
  ("spec_revision", .str "ve-v0.1-order-2026-09-21"),
  ("vocabulary", vocabulary)]

set_option maxRecDepth 4096 in
theorem combined_profile_gate (vocabulary : Json) :
    VE.Closure.Bridge.decodeEnvironment (combinedEnvelope vocabulary) =
      .error "unsupported closure environment version/profiles" := by
  rfl

end VE.Order
