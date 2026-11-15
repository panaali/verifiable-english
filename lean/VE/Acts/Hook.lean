-- ve-layer: 2 (the acts instances of the layer-2 norms decoder's hook, kb-4a: it imports only VE.Norms.Wire)
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

/-- Today's decoder by its name and signature: `decodeNormsEnvironmentWith ActsHook.acts`, which is today's on every
input (`VE.Acts.HookToday.decodeNormsEnvironment_acts`). Every caller in this repository names its hook
(`decodeNormsEnvironmentWith`), except lean/VE/EnglishGrammar/Norm/Rules.lean, whose bytes the English grammar lock
pins (ve/english_grammar/LOCK.json: a change there needs a new `actions_version`, which every English answer
carries as an identity); it reads `acts@0` as before through this name. -/
def decodeNormsEnvironment (environment : Json) (displayConstants : Bool := true) (acts : Bool := false)
    (joined : Bool := false) : Except String NormsEnvironment :=
  decodeNormsEnvironmentWith ActsHook.acts environment displayConstants acts joined

/-- The route's decoder with `acts@0` read and joined acts admitted, without elaborating them: today's
`decodeFlagged` (`VE.Acts.HookToday.decodeFlaggedActs_today`). -/
abbrev decodeFlaggedActs : SourceDecoder := fun environment norms =>
  decodeSource ActsHook.acts environment norms (flags := true)

end VE.Norms.Wire
