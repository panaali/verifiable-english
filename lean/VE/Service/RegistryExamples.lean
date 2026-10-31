import VE.Service.Registry

/-! The service's modes as `#guard` checks: each is registered once, `senses.project` (senses B6) among them. -/

#guard VE.Service.Mode.ofName? "senses.project" == some .sensesProject && VE.Service.modes.length == 41 &&
  (VE.Service.modes.map (·.name)).eraseDups.length == 41
