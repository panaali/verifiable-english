import VE.RightClauses.PlainWellFormed.W1Check

/-! `checkSoft` under a change of guards (8.3, `plain_wellFormed`). `checkSoft D` is `checkSoftK D (checkW1 D.base)
(tailK D)` (`checkSoft_eq`, `rfl`): a prefix that reads no guard, with two holes, W1's check of the base document
and the tail (6.9-6.15). On `mapG γ C` the prefix is the same (`checkSoftK_mapG`), and the tail throws nothing but
resource limits apart from `validateW1 (soften ·)`. Proof vocabulary only. -/
namespace VE.RightClauses.PWF
open VE.SoftNorms
open VE.Norms (syms elabPremise targets targetConclusion)

/-- `checkSoft` from 6.9 on (the same statements). -/
def tailK (D : SoftDoc) : Except String Unit := do
  for (N, s) in D.T.nodes.zip (derivedSizes D) do
    if N.carveOuts.length + (if hasDerived N then 1 else 0) > 8 || (hasDerived N && !fits s) then
      throw s!"ResourceLimit: derived carve-out of rule {N.name}"
  for N in D.T.nodes do
    unless (derivedList D N).all withinLimits do
      throw s!"ResourceLimit: derived carve-out of rule {N.name}"
  validateW1 (soften D)
  let sizes := generatedSizes D
  for s in sizes.soft do
    unless fits s do throw "ResourceLimit: generated soft premise"
  for φ in softPremises D do
    unless withinLimits φ do throw "ResourceLimit: generated soft premise"
  for (p, s) in sizes.layers do
    unless fits s do throw s!"ResourceLimit: generated norm layer layer:norms:{p}"
  for s in syms (soften D).T do
    if let .reg r := s then
      unless withinLimits (elabPremise (soften D).T r) do
        throw s!"ResourceLimit: generated norm layer layer:norms:{r.name}"
  for (t, s) in sizes.targets do
    unless fits s do throw s!"ResourceLimit: generated conflict target {t}"
  for t in targets (soften D) do
    unless withinLimits (targetConclusion t) do throw s!"ResourceLimit: generated conflict target {t.1}"
  unless fitsTogether ((VE.Norms.background (soften D)).map (fsize noSubst) ++ sizes.soft) do
    throw "ResourceLimit: generated background"
  unless fitsTogether (sizes.layers.map (·.2) ++ [fsize noSubst .top]) do
    throw "ResourceLimit: generated norm layers"

/-- `checkSoft` up to 6.9, with W1's check of the base document as `w` and the rest as `k`. -/
def checkSoftK (D : SoftDoc) (w k : Except String Unit) : Except String Unit := do
  let env := D.soft
  checkSoftEnv D
  for (p, _) in D.T.regulated.map (fun r => (r.name, r.sorts)) do
    if containsDunder p then throw s!"InvalidInput: invalid soft name {p}"
  for p in D.T.definitions.map (·.name) do
    if reservedPredicate p then throw s!"InvalidInput: invalid soft name {p}"
  w
  for N in D.T.nodes do
    checkSoftRule D N
  for N in D.T.nodes do
    if N.mode = .default then
      for m in N.over do
        match D.T.nodes.find? (·.name == m) with
        | some M => if M.mode = .strict then throw s!"SoftOverHard: rule {N.name} over {M.name}"
        | none => pure ()
  match checkSoft.dependencyOrderOf env with
  | .error e => throw e
  | .ok _ => pure ()
  for (a, b) in env.ties do
    if outranksPlus env a b || outranksPlus env b a then throw s!"TieAgainstOrder: {a}, {b}"
  if (env.ties.map (fun (a, b) => if a ≤ b then (a, b) else (b, a))).eraseDups.length != env.ties.length then
    throw "DuplicateDeclaration: tie"
  k

theorem checkSoft_eq (D : SoftDoc) : checkSoft D = checkSoftK D (checkW1 D.base) (tailK D) := rfl

end VE.RightClauses.PWF
