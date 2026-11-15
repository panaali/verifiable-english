# kb-4a follow-ups

| Owner | Request | Reason |
|---|---|---|
| Lean service maintainers | R16 ties pass: tie `VE.Norms.Wire.ActsHook.acts`, `ActsHook.lexical`, `decodeNormsEnvironment` and `decodeFlaggedActs` (lean/VE/Acts/Hook.lean) and `ActsHook.plain` (lean/VE/Norms/Wire.lean) to the equality theorems of `VE.Acts.HookToday` (`decodeNormsEnvironment_acts`, `_lexical`, `_plain`, `_plain_refuses`, `decodeSource_acts`, `decodeFlaggedActs_today`), and `VE.Norms.Run.runCaseActs`, `decidesActs`, `runCaseActsRouted` and `runCaseRouted` to those of `VE.Acts.HookTwins` (`runCaseActs_today`, `runCaseActsRouted_today`, `runCaseRouted_today`), once the frozen copies they compare with are anchors the ties rule accepts (today they are proof helpers, class P), so the V +99 leaves the untied count. | R16 signs the trusted growth now (DELTA.md row 1) and asks for this pass. |
