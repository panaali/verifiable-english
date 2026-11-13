# kb-2a: follow-ups

- **R16 ties pass** (kb-2a step A, DELTA.md row 1; trusted +147: K +0, S +0, V +147, `tools/trust_map.py --check`
  against 9a3fd7a9f9ac): `lean/VE/Experimental/CoreDocument.lean`, the untied G[V] definitions of the lowering
  (`strictRule`, `premise`, `lowerContent`, `lowerCandidate`, `declarations`, `readingsOf`, `planOf`,
  `UnitPlan.statements`, `choicesOf`, `allChoices`, `compatible`, `judgments`, `wire` and the types `Origin`, `Choice`,
  `ActiveSet`, `Coupling`, `Options`, `UnitPlan`): tie them, when step B promotes the module to the shell, to the
  `slot-admission` theorem (DESIGN 2.2) and to `VE.SoftNorms.Wire.decodeSoftSource` (the core document decodes to
  `X_c`), so the lowering's trusted lines are those the kernel path's statements read.
