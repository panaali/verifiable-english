import ResponseShape.Schemas.Quantity

/-! The `quantity` response schema's report claim (`Schemas.Quantity.claim`, date-arith): rendered as
`ve/backends/lean_service_schema/quantity.json` holds it, with the optional `inputs` (the dates a statement's
ground date expressions start from, at least one). -/
namespace ResponseShape.QuantityClaimExamples
open Lean ResponseShape

#guard (render "quantity.json" 64 Schemas.Quantity.claim).toOption.map (·.compress) ==
  (Json.parse r##"{"$comment":"Time.Document.claimJson: a node of the request's graph with its quantity and meaning identity, and the dates its ground date expressions start from (omitted when none); the default label is omitted.","additionalProperties":false,"properties":{"inputs":{"items":{"type":"string"},"minItems":1,"type":"array"},"label":{"not":{"const":"asserted"},"type":"string"},"meaning_id":{"$ref":"common.json#/$defs/hex64"},"name":{"type":"string"},"quantity":{"additionalProperties":false,"properties":{"format":{"const":"ve-quantity@1"},"formula":{"$ref":"#/$defs/q_formula"},"traces":{"maxItems":0,"type":"array"}},"required":["format","formula","traces"],"type":"object"}},"required":["name","quantity","meaning_id"],"type":"object"}"##).toOption.map (·.compress)

end ResponseShape.QuantityClaimExamples
