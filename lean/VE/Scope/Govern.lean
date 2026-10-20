import VE.Layout.List
import VE.Scope.Effects
import VE.Discourse.Manifest

/-! Scope's GOVERN step (scope@0, docs/spec/scope.md 1.1, 1.3, 1.5 and 4.2): the reaches, the block's admission and
    `govern`, which returns the complete document with each affected unit's content composed as the chain's own
    norm object. Two parts come later, and until then what they read is refused, never skipped: the precedence
    graph step (sc-1ad), and the anchor and label reaches with `admitBlock`'s anchor checks (sc-3ab). -/

namespace VE.Scope
open Lean
open VE.SoftNorms (SoftNode)

inductive Reach
  | list (lead : String)
  | listName (name : String)
  | anchor (id : String)
  | label (item : String)
  | rules (names : List String)
  | frontier
  | fixed (units : List String)   -- never on the wire: a frontier reach fixed by one joint choice (SC-5)

structure Governor where
  id : String
  unit : String
  effect : Effect
  reach : Reach
  units : List String       -- the recorded reach, regenerated and compared; empty for a frontier reach

structure SDoc where
  layout : List VE.Layout.Unit
  doc : Json                -- the document as written after RESOLVE: `{"units": [...], ...}`
  block : Json              -- the `scope` block as written
  governors : List Governor
  listNames : List (VE.Discourse.ContentName × String × String)   -- name, its lead-in, its registering unit
  anchors : List VE.Discourse.Anchor
  re : VE.Readings.Wire.ReadingsEnvironment

/-! JSON access (read only; scope decodes no rule field itself) -/

def keysOf (j : Json) : List String := (members j).map (·.1)
def unitsOf (doc : Json) : List Json := match doc.getObjValD "units" with
  | .arr xs => xs.toList
  | _ => []
def idOf (u : Json) : String := (u.getObjValD "id").getStr?.toOption.getD ""
def unitIds (doc : Json) : List String := (unitsOf doc).map idOf
def contentOf (doc : Json) (u : String) : Json :=
  (((unitsOf doc).find? (idOf · == u)).map (·.getObjValD "content")).getD .null
def isPart (c : Json) : Bool := keysOf c == ["part"] || keysOf c == ["cites", "part"]
def isNorm (c : Json) : Bool := keysOf c == ["norm"] || keysOf c == ["cites", "norm"]
def objectOf (c : Json) : Json := if isPart c then c.getObjValD "part" else c.getObjValD "norm"
def partUnits (D : SDoc) : List String := (unitIds D.doc).filter (fun u => isPart (contentOf D.doc u))
def ruleUnits (D : SDoc) : List String :=
  (unitIds D.doc).filter (fun u => isPart (contentOf D.doc u) || isNorm (contentOf D.doc u))
def setUnits (doc : Json) : List String := match doc.getObjValD "reading_sets" with
  | .arr xs => xs.toList.map (fun s => (s.getObjValD "unit").getStr?.toOption.getD "")
  | _ => []

/-! Applying effects (on the rule's JSON object) -/

def applyEffect (u : String) : Effect → Json → Except String Json
  | .reguard c, o => match o.getObjVal? "guard" with
    | .ok g => pure (o.setObjVal! "guard" (substOwn g depthLimit c))
    | .error _ => throw s!"ScopeNotARule: {u}"
  | .carveOut c, o => match o.getObjVal? "guard", o.getObjVal? "unless" with
    | .ok g, .ok (.arr xs) => pure (o.setObjVal! "unless" (.arr (xs.push (substOwn g depthLimit c))))
    | _, _ => throw s!"ScopeNotARule: {u}"
  | _, o => pure o

/-- An item's rule as the chain reads it (the explain route). -/
def itemRule (D : SDoc) (u : String) (lead item : Json) : Except String SoftNode :=
  do VE.Readings.Wire.decodeNorm D.re (← mergeParts u lead item)

/-! Reaches -/

def isFrame : Effect → Bool | .frame _ => true | _ => false
def unary : Effect → Bool | .reguard _ | .carveOut _ => true | _ => false
def graph : Effect → Bool | .precedes | .yields => true | _ => false

def coveredLayout (D : SDoc) : Reach → Except String (List String)
  | .list lead => VE.Layout.listRun D.layout lead
  | .listName n => match D.listNames.find? (·.1.name == n) with
    | some (cn, lead, _) => do
      let us ← VE.Layout.listRun D.layout lead
      if cn.units == us then pure us else throw s!"ManifestMismatch: scope.list_names.{n}.units"
    | none => throw s!"ScopeUnknownName: {n}"
  | .anchor _ => throw "UnsupportedProfile: scope@0 anchor reach requires SC-3a"   -- sc-3ab: `anchorReach`
  | .label _ => throw "UnsupportedProfile: scope@0 label reach requires SC-3a"     -- sc-3ab: `itemRun`
  | .rules _ => .ok []
  | .frontier => throw "UnsupportedProfile: scope@0 frontier reach requires SC-5"   -- SC-5: its addendum (9.4)
  | .fixed us => .ok us

def frameOn (D : SDoc) (u : String) : List Governor :=
  D.governors.filter (fun g => isFrame g.effect && ((coveredLayout D g.reach).toOption.getD []).contains u)

def baseObj (D : SDoc) (u : String) : Except String Json :=
  let c := contentOf D.doc u
  if !(isPart c || isNorm c) then .error s!"ScopeNotARule: {u}" else
  match frameOn D u with
  | [] => if isPart c then .error s!"ScopeOrphanPart: {u}" else .ok (objectOf c)
  | [g] => match g.effect with
    | .frame lead => mergeParts u lead (objectOf c)
    | _ => .ok (objectOf c)
  | g₁ :: g₂ :: _ => .error s!"ScopeOrder: {u}: {g₁.id}, {g₂.id}"

def baseName (D : SDoc) (u : String) : Option String :=
  ((baseObj D u).toOption.bind fun o => (VE.Readings.Wire.decodeNorm D.re o).toOption).map (·.name)

def covered (D : SDoc) : Reach → Except String (List String)
  | .rules ns => do
    for n in ns do
      unless (ruleUnits D).any (fun u => baseName D u == some n) do throw s!"ScopeUnknownRule: {n}"
    pure ((ruleUnits D).filter (fun u => (baseName D u).any ns.contains))
  | r => coveredLayout D r

/-! Order (plan 1.4) -/

def classOf : Reach → Nat
  | .anchor _ => 0 | .label _ => 1 | .list _ => 2 | .listName _ => 2 | .rules _ => 3 | .frontier => 4
  | .fixed _ => 4

def position (D : SDoc) (u : String) : Nat := (VE.Layout.indexOf D.layout u).getD D.layout.length

def ordered (D : SDoc) : List Governor :=
  D.governors.mergeSort (fun g h => classOf g.reach < classOf h.reach ||
    (classOf g.reach == classOf h.reach && position D g.unit ≤ position D h.unit))

def coversU (D : SDoc) (g : Governor) (u : String) : Bool := ((covered D g.reach).toOption.getD []).contains u

def governorsOf (D : SDoc) (u : String) : List Governor := (ordered D).filter (fun g => unary g.effect && coversU D g u)

def composed (D : SDoc) (u : String) : Except String Json := do
  (governorsOf D u).foldlM (fun o g => applyEffect u g.effect o) (← baseObj D u)

def orderCheck (D : SDoc) : Except String Unit := do
  for u in unitIds D.doc do
    let gs := governorsOf D u
    for g₁ in gs do
      for g₂ in gs do
        if g₁.id != g₂.id && !Commutes g₁.effect g₂.effect then throw s!"ScopeOrder: {u}: {g₁.id}, {g₂.id}"

def affected (D : SDoc) : List String :=
  (ruleUnits D).filter fun u =>
    isPart (contentOf D.doc u) || !(frameOn D u).isEmpty || !(governorsOf D u).isEmpty ||
    D.governors.any (fun g => match g.effect with
      | .precedes => g.unit == u
      | .yields => coversU D g u
      | _ => false)

/-! The block's admission and `govern` -/

def conditions : Effect → List Json
  | .reguard c => [c]
  | .carveOut c => [c]
  | _ => []

def vocabularyNames (D : SDoc) : List String :=
  let v := D.re.se.ne.rv.vocabulary
  v.sorts ++ v.predicates.map (·.1) ++ v.constants.map (·.1)

def firstDup : List String → Option String
  | [] => none
  | x :: xs => if xs.contains x then some x else firstDup xs

/-- Spec 6.2's steps 1 to 6 and 8. Step 7 (discourse's anchor checks) and step 8's check of an anchor's heading or
    a label's item unit are sc-3ab's; until then `coveredLayout` refuses an anchor or label reach. -/
def admitBlock (D : SDoc) : Except String Unit := do
  if D.governors.length > 256 then throw "ResourceLimit: scope governors"
  if D.listNames.length > 256 then throw "ResourceLimit: scope list names"
  if let some i := firstDup (D.governors.map (·.id)) then throw s!"DuplicateDeclaration: governor {i}"
  if let some n := firstDup (D.listNames.map (·.1.name)) then throw s!"DuplicateDeclaration: list name {n}"
  for g in D.governors do
    unless (unitIds D.doc).contains g.unit do throw s!"ScopeUnknownUnit: {g.unit}"
  if D.governors.any (fun g => !(conditions g.effect).isEmpty) && (vocabularyNames D).contains "own" then
    throw "ScopeReserved: own"
  for (cn, lead, unit) in D.listNames do
    unless cn.scope == "doc" do throw s!"InvalidInput: scope@0 list_names.{cn.name}.scope must be doc"
    unless (unitIds D.doc).contains unit do throw s!"ScopeUnknownUnit: {unit}"
    let us ← VE.Layout.listRun D.layout lead
    unless cn.units == us do throw s!"ManifestMismatch: scope.list_names.{cn.name}.units"
  for g in D.governors do
    for c in conditions g.effect do
      unless depthOk depthLimit c do throw "ResourceLimit: scope condition depth exceeds 64"
      unless ownSafe depthLimit c do throw s!"ScopeOwnBound: {g.id}"
    match g.effect, g.reach with
    | .frame _, .list lead =>
      unless lead == g.unit do throw s!"ManifestMismatch: scope.governors.{g.id}.unit"
    | .frame _, .listName n =>
      unless (D.listNames.find? (·.1.name == n)).any (·.2.1 == g.unit) do
        throw s!"ManifestMismatch: scope.governors.{g.id}.unit"
    | .frame _, _ => throw s!"ScopeReach: {g.id}"
    | .title, .anchor _ => pure ()
    | .title, .label _ => pure ()
    | .title, _ => throw s!"ScopeReach: {g.id}"
    | .precedes, .frontier => throw s!"ScopeReach: {g.id}"
    | .yields, .frontier => throw s!"ScopeReach: {g.id}"
    | _, _ => pure ()
    let us ← covered D g.reach
    unless us == g.units do throw s!"ManifestMismatch: scope.governors.{g.id}.units"
    for u in g.unit :: us do
      if (setUnits D.doc).contains u then throw s!"ScopeReadings: {u}"
    if isFrame g.effect || unary g.effect then
      for u in us do
        let c := contentOf D.doc u
        unless c.isNull || isPart c || isNorm c do throw s!"ScopeNotARule: {u}"

def newContent (c o : Json) : Json :=
  if isPart c then Json.mkObj ((members c).filter (·.1 != "part") ++ [("norm", o)]) else c.setObjVal! "norm" o

def patch (D : SDoc) (comp : List (String × Json)) : Json :=
  D.doc.setObjVal! "units" (.arr ((unitsOf D.doc).map fun u =>
    match comp.lookup (idOf u) with
    | some o => u.setObjVal! "content" (newContent (u.getObjValD "content") o)
    | none => u).toArray)

/-- The block is admitted first, with or without governors. The precedence graph step (`ruleTable`, `edgesOf`,
    `ScopeNoEffect`, `addOver`) is sc-1ad's; until then a `precedes` or `yields` governor is refused. -/
def govern (D : SDoc) : Except String Json := do
  admitBlock D
  if D.governors.isEmpty then
    match partUnits D with
    | [] => pure D.doc
    | u :: _ => throw s!"ScopeOrphanPart: {u}"
  else
    orderCheck D
    let comp ← (affected D).mapM (fun u => do pure (u, ← composed D u))
    if (ordered D).any (graph ·.effect) then throw "UnsupportedProfile: scope@0 precedence requires SC-4"   -- sc-1ad
    pure (patch D comp)

end VE.Scope
