# kb-2a-b: follow-ups

- **R16 ties pass** (kb-2a-b, DELTA.md row 5; trusted +268: K +0, S +48, V +220, `tools/trust_map.py --check` against
  4a5d3460d36c): tie the untied shell definitions of `lean/VE/Service/CoreCheck.lean` (`inputs`, `Inputs`, `reads`,
  `exceptionFormulas`, `tableOf`, `viewOf`, `unitStatus`, `routed`, `routedRefusals`, `runCaseReported`, `factsJson`,
  `roundTrips`), `VE.Kernel.DocumentFold.statuses` and `VE.Service.Document.decode` to theorems: the unit table's
  `reads` to `VE.Judgments.dependsOnC` over the unit's contents (the fold reads what `Judgments.status` reads, exceptions
  added), `viewOf` to `ResponseShape.Encoders.CoreCheck.view_fits` and to a statement that each unit's rendered status
  is `DocumentFold.status`, `routed` to a statement of the two refusals of `Document.environmentOf`, `roundTrips` and
  `factsJson` to `core_facts_round_trip`. kb-2a's own ties pass (its FOLLOW-UPS.md: the lowering's untied definitions,
  to `slot_wire_admission` and `decodeSoftSource`) is still open: step B promoted the module but did not tie it.
