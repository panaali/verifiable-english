import VE.Service.Registry

/-! The service's modes as `#guard` checks: each is registered once, `senses.project` (senses B6),
`english.command` (CI-2), `act-readings` (act-phrases AP-4) and `english.statement` (en-e3-norm EN-2) among them. -/

#guard VE.Service.Mode.ofName? "senses.project" == some .sensesProject &&
  VE.Service.Mode.ofName? "english.command" == some .englishCommand &&
  VE.Service.Mode.ofName? "act-readings" == some .actReadings &&
  VE.Service.Mode.ofName? "english.statement" == some .englishStatement && VE.Service.modes.length == 44 &&
  (VE.Service.modes.map (·.name)).eraseDups.length == 44
