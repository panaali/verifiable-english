import VE.Alternatives.Validate

/-! The alternatives decoder (docs/spec/alternatives.md 3, 7.3): the profile
gate, the strict `alternatives` block decoder, the fixed verbalisations, the
norm objects with profile-word guards, the document's base premises and the
regenerated `table_complete`, and `decodeAltSource`.

The W1 decoder never sees the block: `normsView` removes the `alternatives`
field and the `alternatives@0` profile and hands the rest to the unchanged
`VE.Norms.Wire.decodeNormsEnvironment`. The original complete environment is
kept for identity (3.5). Norm objects are W1's (`VE.Norms.Wire.decodeNorm`);
their guards may mention the profile words and are inlined before W1's
validation (`WellFormedAlt`). A case carries `norms` (the norm objects, as on
the W1 route) and optionally `premises` (the active base units as
`{"label", "ast"}`; positive cells are units `leads_to(c_a, c_h)` over
constants). -/
namespace VE.Alternatives.Wire
open Lean
open VE.Bridge (exactFields fields stringField strings)
open VE.Norms

/-! ## The profile gate and the W1 view -/

/-- 3.1: `alternatives@0` requires `norms@0` and excludes `soft-norms@0`. -/
def profileGate (environment : Json) : Except String (List String) := do
  let ps ← VE.Route.Gate.profilesOf environment
  unless decide (ps.Pairwise (· < ·)) do throw (VE.Route.Gate.unsupported "profiles must be sorted and unique")
  unless ps.contains "alternatives@0" do throw "UnsupportedProfile: alternatives@0 is required"
  unless ps.contains "norms@0" do throw "UnsupportedProfile: alternatives@0 requires norms@0"
  if ps.contains "soft-norms@0" then throw "UnsupportedProfile: alternatives@0 with soft-norms@0"
  pure ps

/-- The environment W1's decoder sees: the block removed, `alternatives@0` dropped. -/
def normsView (environment : Json) (ps : List String) : Except String Json := do
  let kept := (← fields environment).filter (·.1 != "alternatives")
  pure ((Json.mkObj kept).setObjVal! "profiles" (toJson (ps.filter (· != "alternatives@0"))))

/-! ## The block (1.1, 3.1) -/

def mandatoryFields : List String := ["action", "available", "chooser", "harm", "leads_to", "outcomes"]
def optionalFields : List String := ["decided_by", "fulfilments", "inaction", "performed", "proximate", "taken"]

/-- The fixed verbalisation of each role predicate (1.1). -/
def canonicalWording : List (String × String) :=
  [("available", "{0} is available to {1}"), ("leads_to", "{0} leads to {1}"), ("inaction", "{0} is inaction"),
   ("taken", "{0} is taken"), ("proximate", "{0} causes {1}")]

def blockString (raw : Json) (field : String) : Except String String :=
  match raw.getObjValD field with
  | .str s => pure s
  | _ => throw s!"InvalidInput: alternatives.{field}"

def optString (raw : Json) (field : String) : Except String (Option String) :=
  match raw.getObjVal? field with
  | .error _ => pure none
  | .ok (.str s) => pure (some s)
  | .ok _ => throw s!"InvalidInput: alternatives.{field}"

def decodeOutcomes (raw : Json) : Except String Outcomes :=
  match raw with
  | .str "signed" => pure .signed
  | .obj _ => do
    let fs ← fields raw
    unless (fs.map Prod.fst).contains "complete_by" do throw "MissingOutcomeDecider: alternatives.outcomes"
    unless fs.length == 1 do throw "InvalidInput: alternatives.outcomes"
    match raw.getObjValD "complete_by" with
    | .str d => if d.trim.isEmpty then throw "MissingOutcomeDecider: alternatives.outcomes" else pure (.completeBy d)
    | _ => throw "MissingOutcomeDecider: alternatives.outcomes"
  | _ => throw "InvalidInput: alternatives.outcomes"

/-- A decoded block: the roles and the obligations whose fulfilment is `avoids`. -/
structure Block where
  alt : AltEnv
  avoidsOn : List String

/-- The strict block decoder (unknown fields rejected); `avoids` is the body
`¬leads_to(a, h)` over `[harm, action]`. -/
def decodeBlock (raw : Json) : Except String Block := do
  let keys ← match fields raw with
    | .ok fs => pure (fs.map Prod.fst)
    | .error _ => throw "InvalidInput: alternatives.block"
  if let some m := mandatoryFields.find? (fun k => !keys.contains k) then throw s!"InvalidInput: alternatives.{m}"
  if let some u := (sortBy (fun a b => decide (a < b)) keys).find? (fun k => !(mandatoryFields ++ optionalFields).contains k) then
    throw s!"InvalidInput: alternatives.{u}"
  let chooser ← blockString raw "chooser"
  let action ← blockString raw "action"
  let harm ← blockString raw "harm"
  let available ← blockString raw "available"
  let leadsTo ← blockString raw "leads_to"
  let outcomes ← decodeOutcomes (raw.getObjValD "outcomes")
  let decidedBy ← optString raw "decided_by"
  if let some d := decidedBy then
    if d.utf8ByteSize > 64 then throw "InvalidInput: alternatives.decided_by"
  let performed ← match raw.getObjVal? "performed" with
    | .error _ => pure none
    | .ok p => do
      unless (exactFields p ["permission", "obligation"]).isOk do throw "InvalidInput: alternatives.performed"
      match p.getObjValD "permission", p.getObjValD "obligation" with
      | .str m, .str q => pure (some (m, q))
      | _, _ => throw "InvalidInput: alternatives.performed"
  let inaction ← optString raw "inaction"
  let taken ← optString raw "taken"
  let proximate ← optString raw "proximate"
  let items ← match raw.getObjVal? "fulfilments" with
    | .error _ => pure []
    | .ok (.arr xs) => pure xs.toList
    | .ok _ => throw "InvalidInput: alternatives.fulfilments"
  if items.length > 16 then throw "ResourceLimit: fulfilments"
  let mut fs : List Fulfilment := []
  let mut avoidsOn : List String := []
  for item in items do
    unless (exactFields item ["obligation", "body"]).isOk do throw "InvalidInput: alternatives.fulfilments"
    let o ← match item.getObjValD "obligation" with
      | .str o => pure o
      | _ => throw "InvalidInput: alternatives.fulfilments"
    if fs.any (·.obligation == o) then throw s!"DuplicateDeclaration: fulfilment {o}"
    match item.getObjValD "body" with
    | .str "avoids" =>
      fs := fs ++ [⟨o, .not (.binary leadsTo (.var 1) (.var 0))⟩]
      avoidsOn := avoidsOn ++ [o]
    | .arr _ =>
      let body ← match VE.Bridge.decodeFormula 64 (item.getObjValD "body") with
        | .ok b => pure b
        | .error _ => throw "InvalidInput: alternatives.fulfilments"
      fs := fs ++ [⟨o, body⟩]
    | _ => throw "InvalidInput: alternatives.fulfilments"
  pure ⟨⟨chooser, action, harm, available, leadsTo, outcomes, decidedBy, performed, inaction, taken, proximate, fs⟩,
    avoidsOn⟩

/-- The role predicates' verbalisations (1.1): each declared role reads its canonical
wording, and no other predicate uses a role's wording. -/
def checkVerbalisations (alt : AltEnv) (vocabulary : Json) : Except String Unit := do
  let predicates ← fields (← vocabulary.getObjVal? "predicates")
  let roleName (role : String) : Option String := match role with
    | "available" => some alt.available
    | "leads_to" => some alt.leadsTo
    | "inaction" => alt.inaction
    | "taken" => alt.taken
    | "proximate" => alt.proximate
    | _ => none
  let wordingOf (p : String) : Option String := match (predicates.find? (·.1 == p)).map Prod.snd with
    | some entry => match entry.getObjValD "verbalisation" with
      | .str w => some w
      | _ => none
    | none => none
  for (role, wording) in canonicalWording do
    if let some p := roleName role then
      unless wordingOf p == some wording do throw s!"AlternativesVerbalisation: {role} must read \"{wording}\""
  for (role, wording) in canonicalWording do
    for (p, _) in predicates do
      if wordingOf p == some wording && roleName role != some p then
        throw s!"AlternativesVerbalisation: {role} must be declared for \"{wording}\""

/-- `avoids` only on obligations over `(chooser, harm)` (3.1). -/
def checkAvoids (A : AltDoc) (avoidsOn : List String) : Except String Unit := do
  for o in avoidsOn do
    match findReg A.T o with
    | some r => unless r.sorts == [A.alt.chooser, A.alt.harm] do throw s!"FulfilmentSort: {o}"
    | none => throw s!"FulfilmentSort: {o}"

/-! ## Premises and cells (1.4, 4.4) -/

/-- The positive cells of the document: units `leads_to(c_a, c_h)` over constants. -/
def positiveCells (leadsTo : String) (units : List VE.Formula) : List (String × String) :=
  units.filterMap fun u => match u with
    | .binary p (.const a) (.const h) => if p = leadsTo then some (a, h) else none
    | _ => none

def decodePremises (premises : Json) : Except String (List (String × VE.Formula)) := do
  let items ← match premises with
    | .null => pure []
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: premises must be an array"
  items.mapM fun item => do
    exactFields item ["label", "ast"]
    let label ← stringField item "label"
    let ast ← VE.Bridge.decodeFormula 64 (item.getObjValD "ast")
    pure (label, ast)

/-! ## The source -/

/-- A decoded, well-formed alternatives source. -/
structure AltSource where
  profiles : List String
  ne : VE.Norms.Wire.NormsEnvironment
  A : AltDoc
  labels : List String
  wf : WellFormedAlt A = true
  env : A.E = ne.rv.environment

/-- Decode the environment with its block, the norm objects and the base premises; regenerate
`table_complete` under `complete_by`; run `WellFormedAlt` with its diagnostics. -/
def decodeAltSource (environment norms premises : Json) : Except String AltSource := do
  let ps ← profileGate environment
  let block ← match environment.getObjVal? "alternatives" with
    | .ok b => pure b
    | .error _ => throw "InvalidInput: alternatives.block"
  let ne ← VE.Norms.Wire.decodeNormsEnvironment (← normsView environment ps)
  unless ne.rv.definitions.isEmpty do
    throw "UnsupportedProfile: alternatives route with definitions is not implemented"
  unless ne.rv.flags.isEmpty do
    throw "UnsupportedProfile: alternatives route with data flags is not implemented"
  let b ← decodeBlock block
  let units ← match norms with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: norms must be an array"
  if units.length > 256 then throw "ResourceLimit: rules"
  let nodes ← units.mapM VE.Norms.Wire.decodeNorm
  let raw ← decodePremises premises
  let A0 : AltDoc := ⟨ne.rv.environment, ne.rv.literals, b.alt, ⟨ne.regulated, [], nodes⟩, []⟩
  checkBlock A0
  checkVerbalisations b.alt (← environment.getObjVal? "vocabulary")
  checkAvoids A0 b.avoidsOn
  for (label, a) in raw do
    unless a.check (extEnv A0) [] do throw s!"InvalidInput: ill-typed premise {label}"
  let gamma := raw.map (fun (l, a) => (l, inline A0 a))
  let gamma := match b.alt.outcomes with
    | .signed => gamma
    | .completeBy _ => gamma ++ [("alternatives:table_complete", tableComplete A0 (positiveCells b.alt.leadsTo (raw.map Prod.snd)))]
  let A : AltDoc := { A0 with Γ := gamma.map Prod.snd }
  match hv : validateAlt A with
  | .error e => throw e
  | .ok () => pure ⟨ps, ne, A, gamma.map Prod.fst, by unfold WellFormedAlt; rw [hv], rfl⟩

/-! ## Regenerated outputs (`alt-elaborate`) -/

def enc (a : VE.Formula) : Json := VE.Route.Wire.encodeFormula a

def encodeNode (N : Node) : Json :=
  Json.mkObj [("norm", Json.mkObj [("name", .str N.name), ("predicate", .str N.pred), ("sign", .bool N.sign),
    ("guard", enc N.guard), ("unless", Json.arr (N.carveOuts.map enc).toArray), ("over", toJson N.over)])]

/-- Obligations that do not bear on the choice: neither the `performed` obligation nor mapped. -/
def unmappedObligations (A : AltDoc) : List Regulated :=
  A.T.regulated.filter fun r => r.role == .obligation &&
    !(A.alt.performed.any (fun mq => mq.2 == r.name)) && !(A.alt.fulfilments.any (·.obligation == r.name))

def labelled (labels : List String) (fs : List VE.Formula) : Json :=
  Json.arr ((labels.zip fs).map (fun (l, a) => Json.mkObj [("label", .str l), ("ast", enc a)])).toArray

/-- 2.3: the legend generated from the block (untrusted text; the English surface renders the
fulfilment bodies other than `avoids`). -/
def legend (A : AltDoc) : List String :=
  let a := A.alt
  let decider := match a.outcomes with
    | .completeBy d => d
    | .signed => a.decidedBy.getD "unstated"
  let quoted (act : Option String) := s!"\"{act.getD ""}\""
  [s!"Each {a.chooser} faces one choice among the actions available to it and takes at most one of them.",
   s!"Each {a.action} is available to at most one {a.chooser}."] ++
  (if a.inaction.isSome then [s!"Doing nothing counts as one of a {a.chooser}'s actions; every checked situation " ++
      s!"lists exactly one inaction per {a.chooser} with any alternative."] else []) ++
  [s!"\"<{a.action}> leads to <{a.harm}>\" records the declared model; for an action not taken it is a " ++
      s!"counterfactual judgment by {a.decidedBy.getD "unstated"}.",
   match a.outcomes with
   | .signed => "Every cell of the outcome table is stated."
   | .completeBy _ => s!"An action leads to a harm only where this document says so; {decider} stands behind " ++
       "every unstated cell."] ++
  (if a.proximate.isSome then [s!"\"<{a.action}> causes <{a.harm}>\" records a proximate-cause judgment by " ++
      s!"{a.decidedBy.getD "unstated"}; an action that causes a harm leads to it."] else []) ++
  a.fulfilments.map (fun f =>
    let act := quoted ((findReg A.T f.obligation).bind (·.act))
    if f.body == .not (.binary a.leadsTo (.var 1) (.var 0)) then
      s!"A {a.chooser} fulfils {act} by taking an action that does not lead to that {a.harm}."
    else s!"A {a.chooser} fulfils {act} by taking an action that satisfies its declared fulfilment.") ++
  (match unmappedObligations A with
   | [] => []
   | rs => [s!"The following duties do not bear on the choice: {", ".intercalate (rs.map (fun r => quoted r.act))}."])

def regenerated (src : AltSource) : List (String × Json) :=
  let A := src.A
  [("legend", toJson (legend A)),
   ("inlined", Json.arr ((inlineTree A).T.nodes.map encodeNode).toArray),
   ("alternatives", labelled (altPremiseLabels A) (altPremises A)),
   ("base_premises", labelled src.labels A.Γ),
   ("followable", Json.mkObj [("ast", enc (allFollowable A)), ("followable", enc (followableF A)),
     ("clear", enc (clearF A))]),
   ("unmapped_obligations", Json.arr ((unmappedObligations A).map (fun r =>
     Json.mkObj [("obligation", .str r.name), ("act", .str (r.act.getD ""))])).toArray)] ++
  VE.Norms.Wire.regenerated (inlineTree A)

end VE.Alternatives.Wire
