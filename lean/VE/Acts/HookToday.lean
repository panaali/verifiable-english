import VE.Acts.Hook

/-! The decoders' equality theorems of the acts hook (kb-4a; docs/spec/kernel-boundary.md decisions 2 and 5, row KB-4).

`Today` keeps the norms decoders as they were before the hook (main `4a5d3460d3`, lean/VE/Norms/Wire.lean), frozen
for these statements only: no product code reads them. With `ActsHook.acts` the parameterised decoders equal today's
on every input (by `rfl`); with `ActsHook.lexical` they do wherever no joined act is admitted (`joined := false`);
with `ActsHook.plain` they do on every environment from which `acts@0` is not read (`actsProfiles … = []`, which
holds in particular whenever the environment does not list `acts@0`: `actsProfiles_eq_nil`), and elsewhere the plain
decoder refuses (`decodeNormsEnvironment_plain_refuses`). The runners' theorems are in `VE.Acts.HookTwins`. -/
namespace VE.Acts.HookToday
open Lean VE.Norms VE.Norms.Wire
open VE.Bridge (exactFields fields stringField strings)

namespace Today

/-- Today's `Norms.Wire.decodeNormsEnvironment`, frozen. -/
def decodeNormsEnvironment (environment : Json)
    (displayConstants : Bool := true) (acts : Bool := false) (joined : Bool := false) :
    Except String NormsEnvironment := do
  let ps := actsProfiles acts environment
  let e ← VE.Route.Gate.decodeEnvelope (if ps.isEmpty then environment else actsView environment ps)
  unless e.profiles.contains "norms@0" do throw "UnsupportedProfile: norms@0 is required"
  unless e.family == .fol do
    throw (VE.Route.Gate.unsupported "the norms route admits FOL documents only")
  let fx ← actsFixed ps environment
  let V ← actsVocab ps environment
  let vocab := e.vocabulary
  let predicates ← fields (← vocab.getObjVal? "predicates")
  let stripped ← predicates.mapM fun (p, entry) => do
    pure (p, Json.mkObj ((← fields entry).filter (·.1 != "regulated")))
  let vocab' := vocab.setObjVal! "predicates" (Json.mkObj stripped)
  let rv ← VE.Route.Wire.decodeVocabulary e.profiles vocab' displayConstants
  let regs ← predicates.filterMapM fun (p, entry) => do
    match entry.getObjVal? "regulated" with
    | .error _ => pure none
    | .ok raw =>
      if (entry.getObjVal? "defined").isOk then
        throw s!"RegulatedDefinedPredicate: {p}"
      if (entry.getObjVal? "functional").isOk || (entry.getObjVal? "total").isOk then
        throw s!"RegulatedFlag: {p}"
      let args ← strings (← entry.getObjVal? "arguments")
      some <$> (if joined then decodeRegulatedShape ps fx else decodeRegulatedIn ps fx) p args raw
  if regs.length > 64 then throw "ResourceLimit: regulated predicates"
  actChecks regs
  let acts ← joinedActs joined ps fx V regs
  pure ⟨rv, regs, if ps.isEmpty then e.profiles else ps, environment, acts⟩

/-- Today's `Norms.Wire.decodeSource`, frozen. -/
def decodeSource (environment norms : Json) (flags : Bool := false)
    (displayConstants : Bool := true) (joined : Bool := true) : Except String Source := do
  let ne ← Today.decodeNormsEnvironment environment displayConstants (acts := true) (joined := joined)
  unless ne.rv.definitions.isEmpty || ne.profiles.contains "definitions@0" do
    throw "defined declarations require the definitions@0 profile"
  unless flags || ne.rv.flags.isEmpty do
    throw "UnsupportedProfile: norms route with data flags is not implemented"
  let units ← match norms with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: norms must be an array"
  if units.length > 256 then throw "ResourceLimit: rules"
  let nodes ← units.mapM decodeNorm
  let defs := ne.rv.definitions.map fun d => ({ name := d.name, args := d.args, body := d.body } : Definition)
  let D : Doc := ⟨ne.rv.environment, ne.rv.literals, ⟨ne.regulated, defs, nodes⟩⟩
  match hv : validate D with
  | .error e => throw e
  | .ok () => pure ⟨ne, D, by unfold WellFormed; rw [hv], rfl, rfl⟩

/-- Today's `Norms.Wire.decodeFlagged`, frozen. -/
abbrev decodeFlagged : SourceDecoder := fun environment norms => Today.decodeSource environment norms (flags := true)

end Today

/-! ## With `ActsHook.acts`: today's decoders, on every input -/

theorem decodeNormsEnvironment_acts (environment : Json) (displayConstants acts joined : Bool) :
    decodeNormsEnvironmentWith ActsHook.acts environment displayConstants acts joined =
      Today.decodeNormsEnvironment environment displayConstants acts joined := rfl

theorem decodeSource_acts (environment norms : Json) (flags displayConstants joined : Bool) :
    decodeSource ActsHook.acts environment norms flags displayConstants joined =
      Today.decodeSource environment norms flags displayConstants joined := rfl

theorem decodeFlaggedActs_today (environment norms : Json) :
    decodeFlaggedActs environment norms = Today.decodeFlagged environment norms := rfl

/-! ## With `ActsHook.lexical`: today's decoder wherever no joined act is admitted -/

theorem decodeNormsEnvironment_lexical (environment : Json) (displayConstants acts : Bool) :
    decodeNormsEnvironmentWith ActsHook.lexical environment displayConstants acts false =
      Today.decodeNormsEnvironment environment displayConstants acts false := rfl

/-! ## With `ActsHook.plain`: today's decoders wherever `acts@0` is not read -/

/-- An environment that does not list `acts@0` is one from which it is not read. -/
theorem actsProfiles_eq_nil (acts : Bool) (environment : Json)
    (h : ∀ ps, VE.Route.Gate.profilesOf environment = .ok ps → "acts@0" ∉ ps) :
    actsProfiles acts environment = [] := by
  unfold actsProfiles
  split
  · rename_i ps hps
    have := h ps hps
    simp [readsActs, this]
  · rfl

theorem canonicalShape_nil (fx : List String) : canonicalShape [] fx = canonicalAct := by
  funext name k raw
  simp [canonicalShape]

theorem decodeNormsEnvironment_plain (environment : Json) (displayConstants acts joined : Bool)
    (h : actsProfiles acts environment = []) :
    decodeNormsEnvironmentWith ActsHook.plain environment displayConstants acts joined =
      Today.decodeNormsEnvironment environment displayConstants acts joined := by
  simp only [decodeNormsEnvironmentWith, Today.decodeNormsEnvironment, ActsHook.plain, h, List.isEmpty_nil,
    if_true, pure_bind, actsFixed, actsVocab, decodeRegulatedShape, decodeRegulatedIn, canonicalShape_nil,
    canonicalActIn_without_acts [] _ List.not_mem_nil, joinedActs, List.contains_nil, Bool.and_false]
  rfl

/-- Elsewhere the plain decoder refuses, before it reads anything else. -/
theorem decodeNormsEnvironment_plain_refuses (environment : Json) (displayConstants acts joined : Bool)
    (h : actsProfiles acts environment ≠ []) :
    decodeNormsEnvironmentWith ActsHook.plain environment displayConstants acts joined = .error actsHookRefusal := by
  have : (actsProfiles acts environment).isEmpty = false := by
    cases hp : actsProfiles acts environment
    · exact absurd hp h
    · rfl
  simp only [decodeNormsEnvironmentWith, ActsHook.plain, this]
  rfl

theorem decodeSource_plain (environment norms : Json) (flags displayConstants joined : Bool)
    (h : actsProfiles true environment = []) :
    decodeSource ActsHook.plain environment norms flags displayConstants joined =
      Today.decodeSource environment norms flags displayConstants joined := by
  unfold decodeSource Today.decodeSource
  rw [decodeNormsEnvironment_plain environment displayConstants true joined h]
  rfl

theorem decodeFlagged_plain (environment norms : Json) (h : actsProfiles true environment = []) :
    decodeFlagged environment norms = Today.decodeFlagged environment norms :=
  decodeSource_plain environment norms true true true h

end VE.Acts.HookToday
