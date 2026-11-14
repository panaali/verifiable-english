import VE.Norms.Wire

/-! The `acts@0` hook of the norms decoder (docs/spec/kernel-boundary.md decisions 2 and 5, row KB-4; kb-4a): today's
acts operations, packaged unchanged as the instances of `Norms.Wire.ActsHook` that read the profile. The plain decoder
(`ActsHook.plain`, lean/VE/Norms/Wire.lean) references none of them. The equality theorems (with `ActsHook.acts` the
decoders are today's on every input; with `ActsHook.plain`, on every environment from which `acts@0` is not read)
are in `VE.Acts.HookTwins`. -/
namespace VE.Norms.Wire
open Lean

/-- Today's acts operations: `actsProfiles`, `actsFixed`, `actsVocab`, `canonicalActIn`, `canonicalShape` and the
joined-act check `joinedActs` (`actsOf`, which builds the act grammar's reader). -/
def ActsHook.acts : ActsHook where
  Vocab := VE.Acts.Vocab
  profiles acts environment := pure (actsProfiles acts environment)
  fixed := actsFixed
  vocab := actsVocab
  check := canonicalActIn
  shape := canonicalShape
  joined := joinedActs

/-- `ActsHook.acts` without the joined-act check, for a decoder that never admits a joined act (`joined := false`,
where `joinedActs` reads nothing): the soft-norms frame (`SoftNorms.Phases.declarations`), which reads the `acts`
block of an `acts@0` frame but no joined act, so that its path references no act grammar. -/
def ActsHook.lexical : ActsHook where
  Vocab := VE.Acts.Vocab
  profiles acts environment := pure (actsProfiles acts environment)
  fixed := actsFixed
  vocab := actsVocab
  check := canonicalActIn
  shape := canonicalShape
  joined _ _ _ _ _ := pure []

/-- The route's decoder with `acts@0` read and joined acts admitted, without elaborating them: today's
`decodeFlagged` (`VE.Acts.HookTwins.decodeFlaggedActs_today`). -/
abbrev decodeFlaggedActs : SourceDecoder := fun environment norms =>
  decodeSource ActsHook.acts environment norms (flags := true)

end VE.Norms.Wire
