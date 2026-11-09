import VE.RightClauses.PlainWellFormed.SoftValid

/-! What a checked structured line and a well-formed rights document give `plain_wellFormed` (8.3): each line
instance's node is its source line's norm (`mem_linesOf`); a checked entry's clauses and relation atom are typed
over the base vocabulary in the line's context (`entry_typed`); the base stratum order exists, so a base
predicate is never regulated or defined (`base_keep`); no generated rights predicate is an author predicate
(`genDecls_fresh`). Proof vocabulary only. -/
namespace VE.RightClauses.PWF
open VE.Rights (RightsDoc SourceLine Line linesOf sourceLines)
open VE.SoftNorms (SoftNode SoftDoc)

open VE.Rights (checkBlock authorNodes beginsRightsRule beginsRightsPred genDecls rightOf checkSourceLine checkShape
  validDecider identifier)

/-- `checkRights` after its `genDecls` loop (the same statements). -/
def restRights (D : RightsDoc) : Except String Unit := do
  for M in D.rs.flatMap (fun R => R.lines.flatMap authorNodes) ++ D.soft.T.nodes do
    for m in M.over do
      if beginsRightsRule m then throw s!"UnknownSymbol: rule {m}"
  for R in D.rs do
    unless D.rights.holders.contains R.holder do throw s!"UnknownSymbol: sort {R.holder}"
    VE.Norms.typeDiagnostic D.soft.E [R.holder] R.guard
    unless R.guard.check D.soft.E [R.holder] do throw s!"InvalidInput: ill-typed right {R.name}"
    for S in R.lines do
      checkSourceLine D R S
  for RN in linesOf D do
    match rightOf D RN.1 with
    | none => throw s!"UnknownRight: {RN.1}"
    | some R =>
      checkShape D R RN.2
      if RN.2.node.carveOuts.length > 6 then throw s!"ResourceLimit: carve-outs of rule {RN.2.node.name}"
  for R in D.rs do
    unless (linesOf D).any (·.1 == R.name) do throw s!"RightWithoutIncident: {R.name}"
  for L in D.limits do
    match L.scope with
    | none => pure ()
    | some rs =>
      if rs.isEmpty then throw s!"InvalidInput: invalid scope of limitation {L.name}"
      for r in rs do
        unless (D.rs.map (·.name)).contains r do throw s!"UnknownRight: {r}"
    if L.kinds == some [] then throw s!"InvalidInput: invalid kinds of limitation {L.name}"
    if L.conditions.length > 8 then throw "ResourceLimit: conditions"
    for c in L.conditions do
      unless identifier c.name do throw s!"InvalidInput: invalid condition {c.name}"
      unless validDecider c.decidedBy do throw s!"InvalidInput: invalid decider for condition {c.name}"
    if let some c := VE.SoftNorms.dupOf (L.conditions.map (·.name)) then
      throw s!"DuplicateDeclaration: condition {c}"
    unless validDecider L.decidedBy do throw s!"InvalidInput: invalid decider for limitation {L.name}"
    if L.decidedBy.isNone then throw s!"MissingExceptionDecider: limitation {L.name}"
  if D.bars.length > 1 then throw "DuplicateDeclaration: bar"
  for b in D.bars do
    unless validDecider b.decidedBy do throw s!"InvalidInput: invalid decider for bar {b.name}"
  -- 4.1 step 3: every citation names a source unit, so no citation to a non-existent unit
  -- licenses a mechanism (4.5).
  for cs in D.rs.flatMap (fun R => R.lines.map (·.cites)) ++ D.outsideCites.map (·.2) do
    for kv in cs do
      for u in kv.2 do
        unless D.sourceUnits.contains u do throw s!"UnknownSymbol: unit {u}"

/-- `checkRights` up to its `genDecls` loop, then `k`. -/
def checkRightsK (D : RightsDoc) (k : Except String Unit) : Except String Unit := do
  checkBlock D
  if D.rs.length > 128 then throw "ResourceLimit: rights"
  if D.limits.length > 16 then throw "ResourceLimit: limitations"
  let names := D.rs.map (·.name) ++ D.limits.map (·.name) ++ D.bars.map (·.name)
  let ruleNames := (D.rs.flatMap (fun R => R.lines.flatMap authorNodes)).map (·.name) ++ D.soft.T.nodes.map (·.name)
  for n in names ++ ruleNames do
    if beginsRightsRule n then throw s!"InvalidInput: name {n} begins with rights-"
  if let some n := VE.SoftNorms.dupOf (names ++ ruleNames) then
    if (D.rs.map (·.name)).contains n then throw s!"DuplicateDeclaration: right {n}"
    else if (D.limits.map (·.name)).contains n then throw s!"DuplicateDeclaration: limitation {n}"
    else if (D.bars.map (·.name)).contains n then throw "DuplicateDeclaration: bar"
    else throw s!"DuplicateDeclaration: rule {n}"
  for p in D.soft.T.regulated.map (·.name) ++ D.soft.T.definitions.map (·.name) do
    if beginsRightsPred p then throw s!"InvalidInput: author predicate {p} begins with rights__"
  for d in genDecls D do
    if (D.soft.E.predicates d.1).isSome then throw s!"InvalidInput: author predicate {d.1} begins with rights__"
  k

theorem checkRights_eq (D : RightsDoc) : VE.Rights.checkRights D = checkRightsK D (restRights D) := rfl

theorem genDecls_fresh (X : RightsDoc) (h : VE.Rights.checkRights X = .ok ()) :
    ∀ d ∈ genDecls X, X.soft.E.predicates d.1 = none := by
  rw [checkRights_eq] at h
  generalize restRights X = k at h
  unfold checkRightsK at h
  simp only [] at h
  obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
  split at h
  · simp [bind, Except.bind] at h
  obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
  split at h
  · simp [bind, Except.bind] at h
  obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
  obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
  split at h
  · split at h
    · simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind] at h
    · split at h
      · simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind] at h
      · split at h <;> simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind] at h
  · obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
    obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
    obtain ⟨u, h4, -⟩ := bind_eq_ok.1 h
    cases u
    intro d hd
    have hb := (VE.NormDefaults.forIn_unit_ok _ (fun x r hx => by
      split at hx <;> simp_all [bind, Except.bind, pure, Except.pure]) (genDecls X)).1 h4 d hd
    cases hp : X.soft.E.predicates d.1 with
    | none => rfl
    | some s => simp [hp, bind, Except.bind] at hb

end VE.RightClauses.PWF
