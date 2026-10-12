import VE.Service.Protocol

/-! The service dispatch pins are equations proved by `rfl`. This tool reads their
compiled right-hand sides, so a mode's direct Lean dependencies come from the
dispatch itself rather than a second hand-maintained table. -/
open Lean Elab Command

example (j : Json) :
    VE.Service.runMode .document j = VE.Service.Document.runCaseReported j := rfl

run_cmd do
  let env ← getEnv
  let mut rows := #[]
  for mode in VE.Service.modes do
    let key := (toString (repr mode)).splitOn "." |>.getLast!
    let pin := Name.str `VE.Service s!"runMode_{key}"
    let rhs ← if mode == .document then pure (mkConst ``VE.Service.Document.runCaseReported) else do
      let some info := env.find? pin | throwError m!"missing dispatch pin {pin}"
      let .forallE _ _ body _ := info.type | throwError m!"malformed dispatch pin {pin}"
      let args := body.getAppArgs
      unless body.getAppFn.isConstOf ``Eq && args.size == 3 do
        throwError m!"dispatch pin {pin} is not an equation"
      pure args[2]!
    let roots := (rhs.getUsedConstants.toList.filterMap fun name => do
      let idx ← env.getModuleIdxFor? name
      let module := env.header.moduleNames[idx.toNat]!
      if (toString module).startsWith "VE." && module != `VE.Service.Protocol then
        some (toString module)
      else none).eraseDups
    if roots.isEmpty then throwError m!"dispatch pin {pin} has no project dependency"
    rows := rows.push (mode.name, toJson roots)
  logInfo (Json.mkObj rows.toList).compress
