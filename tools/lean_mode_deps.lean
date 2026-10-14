import VE.Service.Protocol

/-! The service dispatch pins are equations proved by `rfl`. This tool reads their
compiled right-hand sides and follows the shared response-coding helper through
the compiler environment. The roots come from Lean, not a copied table. -/
open Lean Elab Command

/-- External modules used by a declaration, following helpers defined in the
service protocol. `coding` is the shared response path for every mode. -/
def responseModules (env : Environment) (start : Name) : List String := Id.run do
  let mut pending := [start]
  let mut seen : List Name := []
  let mut modules : List String := []
  while !pending.isEmpty do
    let name := pending.head!
    pending := pending.tail!
    if seen.contains name then continue
    seen := name :: seen
    let some info := env.find? name | continue
    let some value := info.value? | continue
    for used in value.getUsedConstants.toList do
      if let some idx := env.getModuleIdxFor? used then
        let module := env.header.moduleNames[idx.toNat]!
        if (toString module).startsWith "VE." && module != `VE.Service.Protocol then
          modules := (toString module) :: modules
        else if module == `VE.Service.Protocol then
          pending := used :: pending
      else if (toString used).startsWith "VE.Service." then
        pending := used :: pending
  return modules.eraseDups

example (j : Json) :
    VE.Service.runMode .document j = VE.Service.Document.runCaseReported j := rfl

run_cmd do
  let env ← getEnv
  let mut rows := #[]
  let shared := responseModules env ``VE.Service.coding
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
    let roots := ((rhs.getUsedConstants.toList.filterMap fun name => do
      let idx ← env.getModuleIdxFor? name
      let module := env.header.moduleNames[idx.toNat]!
      if (toString module).startsWith "VE." && module != `VE.Service.Protocol then
        some (toString module)
      else none) ++ shared).eraseDups
    if roots.isEmpty then throwError m!"dispatch pin {pin} has no project dependency"
    rows := rows.push (mode.name, toJson roots)
  logInfo (Json.mkObj rows.toList).compress
