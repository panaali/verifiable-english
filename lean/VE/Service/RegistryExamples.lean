import VE.Service.Registry

/-! The service's modes as `#guard` checks: each is registered once, `senses.project` (senses B6) and
`english.command` (CI-2), `act-readings` (act-phrases AP-4) and `clauses-elaborate` (cmp-s3-cfr-1) among them. -/

#guard VE.Service.Mode.ofName? "senses.project" == some .sensesProject &&
  VE.Service.Mode.ofName? "english.command" == some .englishCommand &&
  VE.Service.Mode.ofName? "act-readings" == some .actReadings &&
  VE.Service.Mode.ofName? "clauses-elaborate" == some .clausesElaborate && VE.Service.modes.length == 44 &&
  (VE.Service.modes.map (·.name)).eraseDups.length == 44
