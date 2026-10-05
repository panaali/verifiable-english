import VE.Readings.Lines
import VE.Rights.Wire
import VE.Compose.Dispatch

/-! The wire of `readings@1` part A (docs/spec/composition-s1.md 3, 4.1, 7, 8.4).

A case carries the environment (with `readings@1` in its profiles) and a document
`{"units": [{"id", "kind", "content"}], "reading_sets": [...]}`: each unit's `content` is a formula, a unit content
of the chain (`{"norm", "cites"?}`, `{"right"}`, `{"right_lines"}`, `{"limitation"}`, `{"bar"}`) or absent, its
`kind` the W2 kind that decides whether the content is in force (`inForce`), and the reading sets are W2's, with
S1's `situations`. Other keys of a unit or a document are not read here: the
structural validation of W2 is Python's (4.1). The decoder builds the `Doc` of 1.2 from the active version of
every set (W2: the latest version per unit): an open set is an item `.set`, the one signed reading of an authored
set is a fixed unit, and every other unit with content is a fixed unit or a bar. It runs the checks of 4.1 in
order with section 7's texts and gates the result on `WellFormedDoc`, so a replay carries its proof.

A situation is decoded over the author's base vocabulary: `base` is the finite-model wire form with exactly the
base predicates (`complete` may be omitted), tables are `{"key", "tuples"}` with entity names, and the probe is
`{"outcome": {"predicate", "tuple"}}`, `{"selects": {"kind", "predicate", "tuple"}}` or `"holds"`. Its id is the
digest, under `ve-situation-<identity version>`, of `{"environment_id", "situation"}`. The decoder checks the
whole of 4.5 step 1: the id, the base's validity (the proof `valid` of `SeparateReplay`) and `situationWF` (the
field `shape`). -/
namespace VE.Readings.Wire
open Lean
open VE.Bridge (fields strings stringField Entity)
open VE.Rights (RightsDoc)
open VE.Compose (Content)
open VE.SoftNorms.Wire (SoftEnvironment)

def readingsProfile : String := "readings@1"

/-! ## The environment -/

/-- The environment without `readings@1`. -/
def stripReadings (environment : Json) : Except String Json := do
  let profiles ← strings (← environment.getObjVal? "profiles")
  pure (environment.setObjVal! "profiles" (toJson (profiles.filter (· != readingsProfile))))

def emptySoft : VE.SoftNorms.SoftEnv := ⟨[], [], [], [], .strict, none, none, [], []⟩
def emptyRights : VE.Rights.RightsEnv := ⟨[], [], [], []⟩

/-- A decoded environment: the chain (1.1), the profiles with and without `readings@1`, the chain's soft
    decoding (an empty soft block on the norms chain) and its rights block (empty off the rights chain). -/
structure ReadingsEnvironment where
  chain : Chain
  profiles : List String
  lower : List String
  se : SoftEnvironment
  block : VE.Rights.RightsEnv
  json : Json
  lowerJson : Json

def decodeEnvironment (environment : Json) : Except String ReadingsEnvironment := do
  let profiles ← match environment.getObjVal? "profiles" >>= strings with
    | .ok ps => pure ps
    | .error _ => throw (VE.Compose.unsupported "profiles must be a sorted unique array")
  unless profiles.contains readingsProfile do throw "UnsupportedProfile: readings@1 is required"
  match VE.Compose.dispatch profiles with
  | .ok .readings => pure ()
  | .ok _ => throw "UnsupportedProfile: readings@1 is not the head of this profile list"
  | .error e => throw e
  let lowerJson ← stripReadings environment
  let lower := profiles.filter (· != readingsProfile)
  -- `norm-defaults@0` beside content is S1's named abstention (1.1): the frame is decoded without it.
  let frameJson := lowerJson.setObjVal! "profiles" (toJson (lower.filter (· != "norm-defaults@0")))
  match chainOf profiles with
  | .rights =>
    let re ← VE.Rights.Wire.decodeRightsEnvironment frameJson
    pure ⟨.rights, profiles, lower, re.se, re.block, environment, lowerJson⟩
  | .soft =>
    let checked ← match VE.SoftNorms.Phases.checkSource frameJson (.arr #[]) with
      | .ok c => pure c
      | .error f => throw f.message
    pure ⟨.soft, profiles, lower, ⟨checked.ne, checked.soft, checked.profiles, frameJson⟩, emptyRights,
      environment, lowerJson⟩
  | .norms =>
    let ne ← VE.Norms.Wire.decodeNormsEnvironment frameJson
    pure ⟨.norms, profiles, lower, ⟨ne, emptySoft, lower, lowerJson⟩, emptyRights, environment, lowerJson⟩

/-- The frame (1.2): the environment and no unit. -/
def frameOf (re : ReadingsEnvironment) (unitIds : List String) : RightsDoc :=
  ⟨⟨re.se.ne.rv.environment, re.se.ne.rv.literals, re.se.soft, ⟨re.se.ne.regulated, [], []⟩⟩,
   re.block, [], [], [], [], some [], unitIds⟩

/-- The author's base model vocabulary: the declared predicates without the regulated ones. -/
def authorVocabulary (re : ReadingsEnvironment) : VE.Bridge.Vocabulary :=
  { re.se.ne.rv.modelVocabulary with
    predicates := re.se.ne.rv.modelVocabulary.predicates.filter
      (fun p => !(re.se.ne.regulated.map (·.name)).contains p.1) }

/-! ## Contents -/

/-- A decoded unit or candidate content (1.2). -/
inductive Decoded
  | content (c : Content) (cites : List (String × List String))
  | bar (b : VE.Rights.Bar)
  | pending

/-- A norm object: the chain's own decoder (W1's on the norms chain, so a soft field is W1's error there). -/
def decodeNorm (re : ReadingsEnvironment) (raw : Json) : Except String VE.SoftNorms.SoftNode :=
  match re.chain with
  | .norms => do
    let N ← VE.Norms.Wire.decodeNorm (Json.mkObj [("norm", raw)])
    pure { toNode := N, mode := .strict, rank := none, alterable := [], exception := none, hard := false }
  | _ => VE.SoftNorms.Wire.decodeSoftNorm re.se (Json.mkObj [("norm", raw)])

def decodeContent (re : ReadingsEnvironment) (j : Json) : Except String Decoded := do
  match j with
  | .null => pure .pending
  | .arr _ => pure (.content (.assertion (← VE.Bridge.decodeFormula 64 j)) [])
  | .obj _ =>
    let keys := (← fields j).map (·.1)
    if keys == ["norm"] || keys == ["cites", "norm"] then
      pure (.content (.norm (← decodeNorm re (j.getObjValD "norm"))) (← VE.Rights.Wire.optCites j))
    else if keys == ["right"] then
      pure (.content (.right (← VE.Rights.Wire.decodeRight re.se (j.getObjValD "right"))) [])
    else if keys == ["right_lines"] then
      let rl := j.getObjValD "right_lines"
      pure (.content (.rightLines (← stringField rl "right") (← VE.Rights.Wire.decodeLines re.se rl)) [])
    else if keys == ["limitation"] then
      pure (.content (.limitation (← VE.Rights.Wire.decodeLimitation (j.getObjValD "limitation"))) [])
    else if keys == ["bar"] then
      pure (.bar (← VE.Rights.Wire.decodeBar (j.getObjValD "bar")))
    else pure .pending
  | _ => pure .pending

/-! ## The document -/

/-- A reading of a set as written: id, kind (`none` for a composite W2 kind, which is not a string), content,
    admission, labels. -/
structure ReadingJ where
  id : String
  kind : Option String
  content : Json
  models : List (String × String)
  labels : List (String × String)

/-- A reading set as written. -/
structure SetJ where
  id : String
  unit : String
  version : Nat
  status : String
  readings : List ReadingJ
  situations : List (String × Json)

def invalidSet : String := "invalid reading set"

def decodeReading (j : Json) : Except String ReadingJ := do
  let id ← stringField j "id"
  let kind ← match j.getObjValD "kind" with
    | .str k => pure (some k)
    | .arr _ => pure none
    | _ => throw "invalid reading"
  let models ← match (j.getObjValD "admission").getObjVal? "distinguishing_models" with
    | .ok m => (← fields m).mapM fun (k, v) => do
        match v with
        | .str s => pure (k, s)
        | _ => throw "invalid distinguishing model id"
    | .error _ => pure []
  let labels ← match j.getObjVal? "labels" with
    | .ok l => (← fields l).mapM fun (k, v) => do
        match v with
        | .str s => pure (k, s)
        | _ => throw "invalid rights candidate labels"
    | .error _ => pure []
  pure ⟨id, kind, j.getObjValD "content", models, labels⟩

def decodeSet (j : Json) : Except String SetJ := do
  let id ← match stringField j "id" with
    | .ok s => pure s
    | .error _ => throw invalidSet
  let unit ← match stringField j "unit" with
    | .ok s => pure s
    | .error _ => throw invalidSet
  let version ← match (j.getObjValD "version").getNat? with
    | .ok n => pure n
    | .error _ => throw "invalid or duplicate reading set version"
  let status ← match j.getObjValD "status" with
    | .str s => pure s
    | _ => throw "invalid reading set unit or status"
  let readings ← match j.getObjValD "readings" with
    | .arr rs => rs.toList.mapM decodeReading
    | _ => throw "reading sets hold 1 to 64 readings"
  let situations ← match j.getObjVal? "situations" with
    | .ok s => fields s
    | .error _ => pure []
  pure ⟨id, unit, version, status, readings, situations⟩

/-- W2's active version of each unit: the latest. -/
def active (sets : List SetJ) : List SetJ :=
  sets.filter (fun R => sets.all (fun R' => R'.unit != R.unit || R'.version ≤ R.version))

/-- An item of the document with the JSON it was decoded from (for the chain's document hash). -/
inductive ItemJ
  | fixed (unit : String) (json : Json)
  | bar (unit : String) (json : Json)
  | set (R : SetJ)

/-- The decoded document: the items, their JSON, and the unit ids. -/
structure Decoded2 where
  items : List Item
  itemsJ : List ItemJ
  units : List String

def contentKind : Content → String := Content.kind

/-- The unit kinds whose content is in force (1.2). A formula is asserted only by a unit of kind `asserted`, and a
    norm is a rule only in a unit of kind `norm`; a rights block is correlated from a unit of any rights kind or
    `norm` (the content's block decides, as the rights decoder reads it). Any other kind, a composite W2 kind
    (quoted, hedged, causal; not a string) included, keeps its content out of the document, as Python's W2 loader
    does. -/
def rightsKinds : List String := ["right", "right_lines", "limitation", "bar", "norm"]

def inForce (kind : Option String) : Content → Bool
  | .assertion _ => kind == some "asserted"
  | .norm _ => kind == some "norm"
  | _ => kind.any rightsKinds.contains

def decodeCandidate (re : ReadingsEnvironment) (setId : String) (r : ReadingJ) : Except String Candidate := do
  match ← decodeContent re r.content with
  | .pending => pure ⟨r.id, none, [], r.labels⟩
  | .bar _ => throw "UnsupportedProfile: readings@1 bar candidate content is not implemented"
  | .content c cs =>
    match c with
    -- A formula of a kind other than `asserted` (a question, a quoted or hedged formula) is pending (1.2).
    | .assertion _ => pure ⟨r.id, if r.kind == some "asserted" then some c else none, cs, r.labels⟩
    | _ =>
      if r.kind != some c.kind then
        throw s!"InvalidInput: reading {setId}:{r.id} has kind {r.kind.getD "composite"} and content of kind {c.kind}"
      pure ⟨r.id, some c, cs, r.labels⟩

def decodeDocument (re : ReadingsEnvironment) (document : Json) : Except String Decoded2 := do
  -- Each unit carries its kind: whether its content is in force depends on it (`inForce`).
  let units ← match document.getObjValD "units" with
    | .arr us => us.toList.mapM fun u => do
        let kind ← match u.getObjValD "kind" with
          | .str k => pure (some k)
          | .arr _ => pure none
          | .null => if u.getObjValD "content" == .null then pure none else throw "InvalidInput: unit kind is required"
          | _ => throw "InvalidInput: unit kind is required"
        pure (← stringField u "id", kind, u.getObjValD "content")
    | _ => throw "InvalidInput: document must list units"
  let sets ← match document.getObjValD "reading_sets" with
    | .arr ss => ss.toList.mapM decodeSet
    | .null => pure []
    | _ => throw "reading_sets must be a list"
  let act := active sets
  let unitIds := units.map (·.1)
  let mut items : List Item := []
  let mut itemsJ : List ItemJ := []
  for (u, kind, content) in units do
    match act.find? (·.unit == u) with
    | some R =>
      if R.status == "open" then
        let cands ← R.readings.mapM (decodeCandidate re R.id)
        items := items ++ [.set ⟨R.id, R.unit, R.version, cands⟩]
        itemsJ := itemsJ ++ [.set R]
      else
        match R.readings with
        | [r] =>
          match ← decodeContent re r.content with
          | .content c cs =>
            if inForce r.kind c then items := items ++ [.fixed u c cs]; itemsJ := itemsJ ++ [.fixed u r.content]
          | .bar b =>
            if r.kind.any rightsKinds.contains then items := items ++ [.bar u b]; itemsJ := itemsJ ++ [.bar u r.content]
          | .pending => pure ()
        | _ => throw "authored reading needs one signed choice"
    | none =>
      match ← decodeContent re content with
      | .content c cs =>
        if inForce kind c then items := items ++ [.fixed u c cs]; itemsJ := itemsJ ++ [.fixed u content]
      | .bar b =>
        if kind.any rightsKinds.contains then items := items ++ [.bar u b]; itemsJ := itemsJ ++ [.bar u content]
      | .pending => pure ()
  pure ⟨items, itemsJ, unitIds⟩

/-! ## Keys, tables, probes and situations -/

def keyJson : GenKey → Json
  | .excepted r b => Json.mkObj ([("excepted", .str r)] ++ (b.toList.map (fun x => ("bearer", .str x))))
  | .off r b π => Json.mkObj ([("off", .str r), ("party", .str π)] ++ (b.toList.map (fun x => ("bearer", .str x))))
  | .outweighs a L H => Json.mkObj [("outweighs", .str a), ("lower", .str L), ("higher", .str H)]
  | .lim L a => Json.mkObj [("lim", .str L), ("act", .str a)]
  | .cond L a c => Json.mkObj [("cond", .str L), ("act", .str a), ("condition", .str c)]
  | .aimed m => Json.mkObj [("aimed", .str m)]

/-- A key as `<key>` is written in section 7: `excepted <r>`, `off <r> <π>`, …, ` bearer <b>` after the rule. -/
def keyText : GenKey → String
  | .excepted r b => s!"excepted {r}" ++ (b.map (" bearer " ++ ·)).getD ""
  | .off r b π => s!"off {r}" ++ (b.map (" bearer " ++ ·)).getD "" ++ s!" {π}"
  | .outweighs a L H => s!"outweighs {a} {L} {H}"
  | .lim L a => s!"lim {L} {a}"
  | .cond L a c => s!"cond {L} {a} {c}"
  | .aimed m => s!"aimed {m}"

def decodeKey (bad : String) (j : Json) : Except String GenKey := do
  let keys ← match fields j with
    | .ok kvs => pure (kvs.map (·.1))
    | .error _ => throw bad
  let str (k : String) : Except String String := match j.getObjValD k with
    | .str s => pure s
    | _ => throw bad
  let bearer : Except String (Option String) := match j.getObjVal? "bearer" with
    | .ok (.str s) => pure (some s)
    | .ok _ => throw bad
    | .error _ => pure none
  if keys == ["excepted"] || keys == ["bearer", "excepted"] then return .excepted (← str "excepted") (← bearer)
  if keys == ["off", "party"] || keys == ["bearer", "off", "party"] then
    return .off (← str "off") (← bearer) (← str "party")
  if keys == ["higher", "lower", "outweighs"] then return .outweighs (← str "outweighs") (← str "lower") (← str "higher")
  if keys == ["act", "lim"] then return .lim (← str "lim") (← str "act")
  if keys == ["act", "cond", "condition"] then return .cond (← str "cond") (← str "act") (← str "condition")
  if keys == ["aimed"] then return .aimed (← str "aimed")
  throw bad

/-- The declared sorts of the generated predicate that reads key `k` in X, if any. -/
def keySorts (X : RightsDoc) (k : GenKey) : Option (List String) :=
  ((genKeys X).find? (·.1 == k)).map (·.2.2)

def tupleOf (bad : String) (sorts : List String) (j : Json) : Except String (List Entity) := do
  let names ← match strings j with
    | .ok xs => pure xs
    | .error _ => throw bad
  unless names.length == sorts.length do throw bad
  pure (sorts.zip names)

def decodeTables (bad : String) (sortsOf : GenKey → Option (List String)) (j : Json) :
    Except String (List (GenKey × List (List Entity))) := do
  let entries ← match j with
    | .arr xs => pure xs.toList
    | .null => pure []
    | _ => throw bad
  entries.mapM fun e => do
    match fields e with
    | .ok kvs => unless kvs.map (·.1) == ["key", "tuples"] do throw bad
    | .error _ => throw bad
    let k ← decodeKey bad (e.getObjValD "key")
    let some ss := sortsOf k | throw bad
    let rows ← match e.getObjValD "tuples" with
      | .arr rs => rs.toList.mapM (tupleOf bad ss)
      | _ => throw bad
    pure (k, rows)

def regSorts (D : Doc) (p : String) : List String := VE.SoftNorms.sortsIn D.frame.soft.T.regulated p

def decodeProbe (bad : String) (D : Doc) (j : Json) : Except String (Probe Entity) := do
  match j with
  | .str "holds" => pure .holds
  | _ =>
    match j.getObjVal? "outcome", j.getObjVal? "selects" with
    | .ok o, .error _ => do
      let p ← match o.getObjValD "predicate" with
        | .str p => pure p
        | _ => throw bad
      pure (.outcome p (← tupleOf bad (regSorts D p) (o.getObjValD "tuple")))
    | .error _, .ok s => do
      let k ← match s.getObjValD "kind" with
        | .str k => pure k
        | _ => throw bad
      let p ← match s.getObjValD "predicate" with
        | .str p => pure p
        | _ => throw bad
      pure (.selects k p (← tupleOf bad (regSorts D p) (s.getObjValD "tuple")))
    | _, _ => throw bad

/-- A situation as written, with the witness's reading id. -/
structure SituationJ where
  id : String
  witness : String
  σ : Situation Entity
  data : VE.Bridge.ModelData
  base : σ.base = data.toModel

/-- 1.8: an element name of a situation must not contain `__` or begin `rd-`. -/
def elementNames (data : VE.Bridge.ModelData) : List String := data.domains.flatMap (·.2)

def decodeSituation (re : ReadingsEnvironment) (D : Doc) (s : String) (i j : Nat) (sid : String) (entry : Json) :
    Except String SituationJ := do
  let bad := s!"InvalidInput: invalid situation {sid}"
  match fields entry with
  | .ok kvs =>
    unless kvs.map (·.1) == ["base", "decisions", "fixed", "probe", "value", "witness"] do throw bad
  | .error _ => throw bad
  let envId ← VE.Route.Wire.environmentId re.profiles (← VE.Norms.Wire.canonicalEnvironmentJson re.json)
  let computed ← VE.CertificateWire.digest s!"ve-situation-{VE.Route.Wire.identityVersion re.profiles}\n"
    (Json.mkObj [("environment_id", .str envId), ("situation", entry)])
  unless computed == sid do throw "distinguishing model id does not match model"
  let witness ← match entry.getObjValD "witness" with
    | .str w => pure w
    | _ => throw bad
  let base := entry.getObjValD "base"
  let base := if (base.getObjVal? "complete").toBool then base else base.setObjVal! "complete" (.bool true)
  let data ← match VE.Bridge.decodeModelData (authorVocabulary re) base with
    | .ok d => pure d
    | .error _ => throw bad
  for n in elementNames data do
    if n.startsWith "rd-" then throw s!"InvalidInput: name {n} begins with rd-"
    if (n.splitOn "__").length > 1 then throw bad
  let Xi := (one D s i).1
  let Xj := (one D s j).1
  let sortsOf := fun k => (keySorts Xi k).or (keySorts Xj k)
  let fixed ← decodeTables bad sortsOf (entry.getObjValD "fixed")
  let decisions ← decodeTables bad sortsOf (entry.getObjValD "decisions")
  let probe ← decodeProbe bad D (entry.getObjValD "probe")
  let value ← match entry.getObjValD "value" with
    | .bool b => pure b
    | _ => throw bad
  pure ⟨sid, witness, ⟨data.toModel, fixed, decisions, probe, value⟩, data, rfl⟩

/-- 4.5 step 1 with section 7's texts, `i` the witness. -/
def stepOne (D : Doc) (s : String) (i j : Nat) (sid : String) (wName : String) (σ : Situation Entity) :
    Except String Unit := do
  let bad := s!"InvalidInput: invalid situation {sid}"
  for t in σ.decisions do
    unless owned D s i t.1 do throw s!"InvalidInput: situation {sid} decides {keyText t.1}, which reading {wName} does not own"
  for t in σ.fixed do
    if owned D s i t.1 || owned D s j t.1 then
      throw s!"InvalidInput: situation {sid} decides {keyText t.1}, which reading {wName} does not own"
  unless situationWF D s i j σ do throw bad

/-! ## The checks of 4.1 -/

/-- A side's chain checks as specified: the chain's validation, then each assertion typed over the complete
    environment of `soften (correlate X.1)`, rebuilt for each assertion. -/
def chainTextSpec (c : Chain) (X : RightsDoc × List VE.Formula) : Option String :=
  let chain : Option String := match c with
    -- The line order first (DRI ruling 1): each entry a line of its right, none listed twice (`linesOnce`).
    | .rights => (lineOrderText X.1).or <| match VE.Rights.validateRights X.1 with
      | .error e => some e
      | .ok () => none
    | .soft =>
      if !noRights X.1 then some "UnsupportedProfile: rights content requires rights@0"
      else match VE.SoftNorms.validateSoft X.1.soft with
        | .error e => some e
        | .ok () => none
    | .norms =>
      if !noRights X.1 then some "UnsupportedProfile: rights content requires rights@0"
      else if !allStrict X.1 then some "InvalidInput: invalid norm fields"
      else match VE.SoftNorms.validateSoft X.1.soft with
        | .error e => some e
        | .ok () => none
  match chain with
  | some e => some e
  | none =>
    if X.2.all (fun a => a.check (VE.Norms.envAt (VE.SoftNorms.soften (VE.Rights.correlate X.1))
        (VE.Norms.size (VE.SoftNorms.soften (VE.Rights.correlate X.1)))) []) then none
    else some "InvalidInput: ill-typed assertion"

/-- A side's chain checks, each validation with its layers computed once (`validateRightsOnce`,
    `validateSoftOnce`) and the complete environment computed once for every assertion (plan F5d). -/
def chainText (c : Chain) (X : RightsDoc × List VE.Formula) : Option String :=
  let chain : Option String := match c with
    | .rights => (lineOrderText X.1).or <| match VE.Rights.validateRightsOnce X.1 with
      | .error e => some e
      | .ok () => none
    | .soft =>
      if !noRights X.1 then some "UnsupportedProfile: rights content requires rights@0"
      else match VE.SoftNorms.validateSoftOnce X.1.soft with
        | .error e => some e
        | .ok () => none
    | .norms =>
      if !noRights X.1 then some "UnsupportedProfile: rights content requires rights@0"
      else if !allStrict X.1 then some "InvalidInput: invalid norm fields"
      else match VE.SoftNorms.validateSoftOnce X.1.soft with
        | .error e => some e
        | .ok () => none
  match chain with
  | some e => some e
  | none =>
    let S := VE.SoftNorms.soften (VE.Rights.correlate X.1)
    let En := VE.Norms.envAt S (VE.Norms.size S)
    if X.2.all (fun a => a.check En []) then none
    else some "InvalidInput: ill-typed assertion"

theorem chainText_eq (c : Chain) (X : RightsDoc × List VE.Formula) : chainText c X = chainTextSpec c X := by
  simp only [chainText, chainTextSpec, VE.Rights.validateRightsOnce_eq, VE.SoftNorms.validateSoftOnce_eq]

def contentBearing (R : ReadingSet) : Bool :=
  R.candidates.any (fun a => match a.content with
    | some (.assertion _) | none => false
    | some _ => true)

def firstSome {α β : Type} (l : List α) (f : α → Option β) : Option β := (l.filterMap f).head?

/-- 1.1, 1.2: the named abstentions. -/
def abstention (re : ReadingsEnvironment) (D : Doc) : Option String :=
  if re.lower.contains "norm-defaults@0" && D.sets.any contentBearing then
    some "UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented"
  else firstSome D.sets (fun R => firstSome R.candidates (fun a => match a.content with
    | some c => match c.needs with
      | some p => if re.lower.contains p then none
                  else some s!"UnsupportedProfile: reading {R.id}:{a.id} of kind {c.kind} requires {p}"
      | none => none
    | none => none))

/-- 1.8. -/
def reservedText (re : ReadingsEnvironment) (D : Doc) : Option String :=
  let v := re.se.ne.rv.vocabulary
  let syms := v.sorts ++ v.predicates.map (·.1) ++ v.constants.map (·.1) ++ re.se.ne.rv.literals
  match syms.find? reservedSym with
  | some n => some s!"InvalidInput: name {n} begins with ve__"
  | none =>
    let names := D.items.flatMap (fun it => match it with
      | .fixed _ c _ => c.declared.map (·.2)
      | .bar _ _ => []
      | .set R => R.candidates.flatMap (fun a => ((a.content.map (·.declared)).getD []).map (·.2)))
    (names.find? reservedName).map (fun n => s!"InvalidInput: name {n} begins with rd-")

/-- The chain's text for a name two fixed units declare (4.3). -/
def fixedDuplicateText (c : Chain) (D : Doc) (n : String) : String :=
  let decl := D.items.flatMap (fun it => match it with
    | .fixed _ c _ => c.declared
    | .bar _ b => [("bar", b.name)]
    | .set _ => [])
  match c with
  | .rights =>
    if decl.contains ("right", n) then s!"DuplicateDeclaration: right {n}"
    else if decl.contains ("limitation", n) then s!"DuplicateDeclaration: limitation {n}"
    else if decl.contains ("bar", n) then "DuplicateDeclaration: bar"
    else s!"DuplicateDeclaration: rule {n}"
  | _ => s!"DuplicateDeclaration: rule {n}"

/-- 4.3, first in source order. -/
def duplicateText (c : Chain) (D : Doc) : Option String :=
  let fixedNames := D.items.flatMap Item.names
  let sets := D.sets
  let setText := firstSome (sets.zip (List.range sets.length)) (fun (R, k) =>
    firstSome (declaredBy R) (fun n =>
      if fixedNames.contains n.2 then some s!"DuplicateDeclaration: {n.2} in reading sets {R.id} and the document"
      else firstSome (sets.drop (k + 1)) (fun R' =>
        if R'.id != R.id && (declaredBy R').any (·.2 == n.2) then
          some s!"DuplicateDeclaration: {n.2} in reading sets {R.id} and {R'.id}"
        else none)))
  match setText with
  | some t => some t
  | none =>
    firstSome (D.items.zip (List.range D.items.length)) (fun (it, k) =>
      firstSome it.names (fun n =>
        if ((D.items.take k).flatMap Item.names).contains n then some (fixedDuplicateText c D n) else none))

/-- 4.2, closure. -/
def interfaceText (D : Doc) : Option String :=
  firstSome D.sets (fun R => firstSome D.items (fun it => match it with
    | .fixed _ c cs => firstSome (uses c cs) (fun n =>
        if (declaredBy R).contains n && !(interfaceOf R).contains n then some s!"ReadingInterface: {R.id}: {n.2}"
        else none)
    | _ => none))

/-- 4.2, single attachment: the first two sets in source order. -/
def attachmentText (D : Doc) : Option String :=
  let ids := D.sets.map (·.id)
  firstSome (fixedNames D) (fun u =>
    match ids.filter (attached D u).contains with
    | s :: t :: _ => some s!"UnsupportedProfile: readings@1 fixed unit {u} depends on reading sets {s} and {t}"
    | _ => none)

/-- The checks of 4.1 up to and including each candidate's well-formedness, in order. -/
def admissionText (re : ReadingsEnvironment) (D : Doc) : Option String :=
  (abstention re D).or <| (reservedText re D).or <| (duplicateText re.chain D).or <| (interfaceText D).or <|
    (attachmentText D).or <| (chainText D.chain (free D)).or <|
    firstSome D.sets (fun R => firstSome (List.range R.candidates.length) (fun i =>
      if (R.candidates[i]?.bind (·.content)).isNone then none
      else (chainText D.chain (one D R.id i)).map (· ++ s!" under {R.id}@{R.version}:{i}")))

/-- The `Doc` of a decoded document (1.2). -/
def docOf (re : ReadingsEnvironment) (doc : Decoded2) : Doc := ⟨re.chain, frameOf re doc.units, doc.items, [], []⟩

/-- A document admitted without separation: `WellFormedDoc` holds. -/
structure Admitted where
  re : ReadingsEnvironment
  doc : Decoded2
  wf : WellFormedDoc (docOf re doc) = true

def Admitted.D (a : Admitted) : Doc := docOf a.re a.doc

/-- Admission as specified: the checks of 4.1, then `WellFormedDoc` evaluated in full. It elaborates and
    validates `free D` and every candidate's `one D s i` twice, once in `admissionText` and once in
    `WellFormedDoc`; `admitReadings` is the same function with each validated once (`admitReadings_eq`). -/
def admitReadingsSpec (environment document : Json) : Except String Admitted := do
  let re ← decodeEnvironment environment
  let doc ← decodeDocument re document
  match admissionText re (docOf re doc) with
  | some e => throw e
  | none =>
    if h : WellFormedDoc (docOf re doc) = true then pure ⟨re, doc, h⟩
    else throw "InvalidInput: readings document is not well-formed"

/-- `WellFormedDoc` without the chain checks of `free D` and of each candidate's `one D s i`. -/
def frameWF (D : Doc) : Bool := reservedFree D && distinctAcrossSets D && interfaceClosed D && singlyAttached D

/-- A side without a chain diagnostic is well-formed: `chainText` computes `sideWF`'s two conjuncts. -/
theorem sideWF_of_chainText (D : Doc) (X : RightsDoc × List VE.Formula) (h : chainText D.chain X = none) :
    sideWF D X = true := by
  rw [chainText_eq] at h
  unfold chainTextSpec at h
  unfold sideWF
  generalize D.chain = c at h ⊢
  cases c with
  | rights =>
    cases hl : lineOrderText X.1 <;> cases hv : VE.Rights.validateRights X.1 <;>
      simp only [hl, hv, Option.or, chainWF, VE.Rights.WellFormedRights] at h ⊢ <;> (try split at h) <;> simp_all
  | soft =>
    cases hn : noRights X.1 <;> cases hv : VE.SoftNorms.validateSoft X.1.soft <;>
      simp only [hn, hv, chainWF, VE.SoftNorms.WellFormedSoft] at h ⊢ <;> (try split at h) <;> simp_all
  | norms =>
    cases hn : noRights X.1 <;> cases hs : allStrict X.1 <;> cases hv : VE.SoftNorms.validateSoft X.1.soft <;>
      simp only [hn, hs, hv, chainWF, VE.SoftNorms.WellFormedSoft] at h ⊢ <;> (try split at h) <;> simp_all

theorem firstSome_eq_none {α β : Type} {l : List α} {f : α → Option β} (h : firstSome l f = none) :
    ∀ x ∈ l, f x = none := by
  unfold firstSome at h
  exact List.filterMap_eq_nil_iff.mp (List.head?_eq_none_iff.mp h)

/-- Once `admissionText` has found nothing, `WellFormedDoc` is `frameWF`. -/
theorem wellFormedDoc_of_admissionText (re : ReadingsEnvironment) (D : Doc) (h : admissionText re D = none) :
    WellFormedDoc D = frameWF D := by
  simp only [admissionText, Option.or_eq_none_iff] at h
  obtain ⟨-, -, -, -, -, hfree, hsets⟩ := h
  have hone : ∀ R ∈ D.sets, ∀ i ∈ List.range R.candidates.length,
      (R.candidates[i]?.bind (·.content)).isNone = true ∨ sideWF D (one D R.id i) = true := by
    intro R hR i hi
    have h1 := firstSome_eq_none hsets R hR
    have h2 := firstSome_eq_none h1 i hi
    by_cases hc : (R.candidates[i]?.bind (·.content)).isNone = true
    · exact Or.inl hc
    · rw [if_neg hc, Option.map_eq_none_iff] at h2
      exact Or.inr (sideWF_of_chainText D _ h2)
  unfold WellFormedDoc frameWF
  rw [sideWF_of_chainText D _ hfree]
  have hall : (D.sets.all (fun R => (List.range R.candidates.length).all (fun i =>
      (R.candidates[i]?.bind (·.content)).isNone || sideWF D (one D R.id i)))) = true := by
    simp only [List.all_eq_true, Bool.or_eq_true]
    exact hone
  rw [hall]
  simp only [Bool.and_true]

/-- Admission with `free D` and each candidate validated once: `WellFormedDoc`'s chain checks are `admissionText`'s,
    so only `frameWF` is evaluated after it. -/
def admitReadings (environment document : Json) : Except String Admitted := do
  let re ← decodeEnvironment environment
  let doc ← decodeDocument re document
  match h : admissionText re (docOf re doc) with
  | some e => throw e
  | none =>
    if hf : frameWF (docOf re doc) = true then pure ⟨re, doc, (wellFormedDoc_of_admissionText re _ h).trans hf⟩
    else throw "InvalidInput: readings document is not well-formed"

theorem admitReadings_eq (environment document : Json) :
    admitReadings environment document = admitReadingsSpec environment document := by
  unfold admitReadings admitReadingsSpec
  simp only [bind, Except.bind]
  split
  · rfl
  · rename_i re _
    split
    · rfl
    · rename_i doc _
      split
      · rename_i e h
        simp only [h]
      · rename_i h
        have hw := wellFormedDoc_of_admissionText re _ h
        simp only [h]
        by_cases hf : frameWF (docOf re doc) = true
        · rw [dif_pos hf, dif_pos (hw.trans hf)]
        · rw [dif_neg hf, dif_neg (fun h' => hf (hw.symm.trans h'))]

/-! ## The replay -/

/-- The base decoded over the author's base vocabulary is valid over `authorEnv`. -/
theorem layerNames_sub {T : VE.Norms.Tree} {x : String} (h : x ∈ VE.Norms.layerNames T) :
    x ∈ T.regulated.map (·.name) ++ T.definitions.map (·.name) := by
  obtain ⟨q, hq, rfl⟩ := List.mem_map.mp h
  obtain ⟨y, _, hl⟩ := List.mem_filterMap.mp hq
  have hn := lookupSym_name hl
  cases q with
  | reg r => exact List.mem_append_left _ (List.mem_map.mpr ⟨r, VE.Norms.lookupSym_reg hl, rfl⟩)
  | defn d => exact List.mem_append_right _ (List.mem_map.mpr ⟨d, VE.Norms.lookupSym_defn hl, rfl⟩)

theorem author_valid (re : ReadingsEnvironment) (D : Doc) (units : List String) (hf : D.frame = frameOf re units)
    (data : VE.Bridge.ModelData) (h : data.valid (authorVocabulary re) = true) :
    data.toModel.Valid (authorEnv D) := by
  have hv := VE.Bridge.modelData_valid data _ h
  refine ⟨fun c s hc => hv.1 c s ?_, fun p vs hp => ?_⟩
  · simp only [authorEnv, VE.Norms.envAt, VE.Norms.hide, hf, frameOf, VE.SoftNorms.SoftDoc.base] at hc
    exact hc
  · obtain ⟨ss, hss, ht⟩ := hv.2 p vs hp
    refine ⟨ss, ?_, ht⟩
    change VE.Bridge.lookup (re.se.ne.rv.modelVocabulary.predicates.filter
      (fun p => !(re.se.ne.regulated.map (·.name)).contains p.1)) p = some ss at hss
    rw [VE.Norms.Replay.lookup_filter_not] at hss
    split at hss
    · cases hss
    · rename_i hnr
      simp only [authorEnv, VE.Norms.envAt, VE.Norms.hide, List.drop_zero, hf, frameOf]
      rw [if_neg (fun hl => by
        have := layerNames_sub hl
        simp only [VE.SoftNorms.SoftDoc.base, List.map_nil, List.append_nil] at this
        exact hnr this)]
      exact hss

structure SeparateReplay where
  D : Doc
  wf : WellFormedDoc D = true
  set : String
  witness : Nat
  other : Nat
  hw : (candidate D set witness).bind (·.content) ≠ none
  ho : (candidate D set other).bind (·.content) ≠ none
  σ : Situation VE.Bridge.Entity
  /-- 4.5 step 1, the base: valid over the author's vocabulary. `separates` does not test it. -/
  valid : σ.base.Valid (authorEnv D)
  /-- 4.5 step 1, the keys, the tables and the probe: the decoder refuses a malformed situation with section 7's
      texts. -/
  shape : situationWF D set witness other σ = true

def readingIndex (D : Doc) (s r : String) : Option Nat :=
  (D.sets.find? (·.id == s)).bind (fun R => R.candidates.findIdx? (·.id == r))

def setJ (doc : Decoded2) (s : String) : Option SetJ :=
  doc.itemsJ.findSome? (fun it => match it with
    | .set R => if R.id == s then some R else none
    | _ => none)

/-- Decode the pair `(witness, other)` of set `s` and the situation `sid` recorded for it, with 4.5 step 1. -/
def replayPair (a : Admitted) (s : String) (sid : String) (otherName : String) :
    Except String (SeparateReplay × SituationJ) := do
  let D := a.D
  let some R := setJ a.doc s | throw s!"InvalidInput: unknown reading set {s}"
  let some entry := R.situations.lookup sid | throw "distinguishing model id does not match model"
  let wName ← match entry.getObjValD "witness" with
    | .str w => pure w
    | _ => throw s!"InvalidInput: invalid situation {sid}"
  let some i := readingIndex D s wName | throw s!"InvalidInput: invalid situation {sid}"
  let some j := readingIndex D s otherName | throw s!"InvalidInput: invalid situation {sid}"
  if i == j then throw s!"InvalidInput: invalid situation {sid}"
  let sj ← decodeSituation a.re D s i j sid entry
  stepOne D s i j sid wName sj.σ
  if hw : ((candidate D s i).bind (·.content)).isSome then
    if ho : ((candidate D s j).bind (·.content)).isSome then
      if hd : sj.data.valid (authorVocabulary a.re) = true then
        if hs : situationWF D s i j sj.σ = true then
          pure (⟨D, a.wf, s, i, j, Option.isSome_iff_ne_none.mp hw, Option.isSome_iff_ne_none.mp ho, sj.σ,
            sj.base ▸ author_valid a.re D a.doc.units rfl sj.data hd, hs⟩, sj)
        else throw s!"InvalidInput: invalid situation {sid}"
      else throw s!"InvalidInput: invalid situation {sid}"
    else throw s!"InvalidInput: invalid situation {sid}"
  else throw s!"InvalidInput: invalid situation {sid}"

/-- The `readings-separate` input: environment, document, set, situation id and the other reading. -/
def replaySeparate (j : Lean.Json) : Except String SeparateReplay := do
  let a ← admitReadings (← j.getObjVal? "environment") (← j.getObjVal? "document")
  let s ← stringField j "set"
  let sid ← stringField j "situation"
  let other ← stringField j "other"
  pure (← replayPair a s sid other).1

theorem readings_wire_separate_sound (j : Lean.Json) (r : SeparateReplay) (h : replaySeparate j = .ok r)
    (hs : separates r.D r.set r.witness r.other r.σ = true) :
  Achieves r.D r.set r.witness r.σ.base.asStructure (tablesOf r.σ.fixed) r.σ.probe r.σ.value ∧
    ¬ Achieves r.D r.set r.other r.σ.base.asStructure (tablesOf r.σ.fixed) r.σ.probe r.σ.value :=
  separates_sound r.D r.wf r.set r.witness r.other r.hw r.ho r.σ r.valid hs

end VE.Readings.Wire
