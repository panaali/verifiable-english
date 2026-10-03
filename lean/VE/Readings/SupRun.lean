import VE.Readings.SupWire
import VE.Compose.Dispatch

/-! The case kinds of S2a on `ve_readings_route` (docs/spec/composition-s2.md 3). Every case carries the environment
(with `readings@1`) and the document of `SupWire.lean`.

* `readings-elaborate`: the route of 1.1 and, past the first three rows, the regenerated elaboration
  (`Route.elaborateFields`); on the superposed and enumerated routes `ReadingsUnsatisfiable` when no choice is
  compatible and the chain's diagnostic under the first compatible choice whose document fails (`routeRefusal`).
  The superposed kinds below refuse the same documents (`supReplayOf`), and past `maxChoiceChecks` choices.
* `readings-conflict`: `assumed` (a choice, default `[]`) and either `conflict_certificates` (target → certificate
  over `Background_base′ ++ slotP D ++ atoms`) → `CONFLICT-FREE` or `UNKNOWN`, or `witness` (`model`, `target`,
  `tuple`) → `CONFLICT` with the choice the model encodes.
* `readings-certificate`: `assumed`, `premises`, `conclusion`, `conflict_certificates`, `certificate` →
  `accepted` exactly when the conflict status under `assumed` is certified and the certificate checks on `sup D`
  (`readings_wire_all_sound`).
* `readings-model`: `assumed`, `premises`, optional `conclusion`, `model` → `valid` (`supModelCheck`), the first
  failing slot label, the conclusion's value, the choice the model encodes (`readings_wire_model_sound`).
* `readings-dead`: `set` and `index` with a certificate of `¬χ` from `choiceCore D` (`DeadReading`), or no index
  and a certificate of `⊥` (`ReadingsUnsatisfiable`).
* `readings-choice`: `choice` and `inner` (a case of the lower route without environment or document): Lean checks
  `compatible D c`, builds `choiceDoc D c`'s units and runs the lower route on them; the answer is the inner answer
  with the chain's document hash of `choiceDoc D c`. -/
namespace VE.Readings.Run
open Lean
open VE.Readings
open VE.Readings.Wire
open VE.Norms (envAt size targets)
open VE.SoftNorms (soften)
open VE.Rights (correlate)

def okWith (id : String) (fields : List (String × Json)) : Json := VE.Route.Wire.ok id fields

/-- The complete choice a structure's bits spell, over the open sets in source order. -/
def encodedChoice {α : Type} [DecidableEq α] (D : Doc) (M : VE.FiniteModel α) : Choice :=
  D.sets.filterMap (fun R => ((List.range R.candidates.length).find?
    (fun i => (choiceAtom D R.id i).eval M [])).map (fun i => (R.id, i)))

def slotLabels (D : Doc) : List String := (slotLabelled D).map (·.1)

/-- The first slot premise, or assumed atom, a model falsifies. -/
def firstFailing {α : Type} [DecidableEq α] (D : Doc) (A : Choice) (M : VE.FiniteModel α) : Option String :=
  ((slotLabelled D ++ A.map (fun x => (s!"readings:{x.1}:{x.2}", choiceAtom D x.1 x.2))).find?
    (fun x => !x.2.eval M [])).map (·.1)

/-! ## `readings-elaborate` -/

def runElaborate (id : String) (j : Json) : Except String Json := do
  let b ← admitS2 (← j.getObjVal? "environment") (← j.getObjVal? "document")
  let nd := b.a.re.lower.contains "norm-defaults@0"
  -- 4.1 steps 3 and 5: no verdict over no reading, and no reading whose document the chain refuses.
  if let some e := routeRefusal nd b.D then throw e
  pure (okWith id (elaborateFields nd b.a.re.se.ne.rv.vocabulary.predicates.length b.D))

/-! ## `readings-conflict` -/

def runConflict (id : String) (j : Json) : Except String Json := do
  let b ← admitS2 (← j.getObjVal? "environment") (← j.getObjVal? "document")
  let r ← supReplayOf b
  let D := r.D
  let ⟨A, _⟩ ← decodeAssumed D (j.getObjValD "assumed")
  unless takenBy D A do throw (untakenText D A)
  let X := correlate (sup D).1
  let w := j.getObjValD "witness"
  if (j.getObjVal? "witness").toBool then
    if hs : b.D.chain ≠ .rights ∧ superposable b.D = true then
      let ⟨M, _⟩ ← decodeSupModel b.a.re b.D ⟨b.wf, hs.1, hs.2⟩ (by rw [b.frame]; rfl) (w.getObjValD "model")
      unless VE.Compose.backgroundValidP X (slotUnder D A) M do
        throw (VE.Route.Wire.invalidModel "readings background")
      let name ← VE.Bridge.stringField w "target"
      let ids ← VE.Bridge.strings (w.getObjValD "tuple")
      let some t := (targets (soften X)).find? (·.1 == name) | throw s!"InvalidInput: unknown conflict target {name}"
      let tuple := t.2.1.zip ids
      unless ids.length == t.2.1.length && VE.Bridge.tupleCheck M t.2.1 tuple do
        throw "InvalidInput: witness tuple has the wrong length or sort"
      let conflict := t.2.2.eval M (VE.Norms.tupleVal tuple)
      return okWith id [("verdict", .str (if conflict then "CONFLICT" else "UNKNOWN")), ("target", .str t.1),
        ("assumed", choiceJson A), ("choice", choiceJson (encodedChoice D M))]
    else throw "InvalidInput: readings document is not superposable"
  let certs := decodeConflictCerts D (j.getObjValD "conflict_certificates")
  let free := VE.Compose.slotConflictFreeCheck X (slotUnder D A) certs
  pure (okWith id [("verdict", .str (if free then "CONFLICT-FREE" else "UNKNOWN")), ("assumed", choiceJson A),
    ("targets", toJson ((targets (soften X)).map (·.1))), ("reading_premises", toJson (slotLabels D))])

/-! ## `readings-certificate` and `readings-model` -/

def runCertificate (id : String) (j : Json) : Except String Json := do
  let r ← replayCertificate j
  let X := correlate (sup r.D).1
  let free := VE.Compose.slotConflictFreeCheck X (slotUnder r.D r.assumed) r.conflictCerts
  let valid := supCertificateCheck r.D r.assumed r.Γ r.φ r.cert
  pure (okWith id [("accepted", .bool (free && valid)), ("conflict_free", .bool free), ("valid", .bool valid),
    ("assumed", choiceJson r.assumed), ("reading_premises", toJson (slotLabels r.D))])

def runModel (id : String) (j : Json) : Except String Json := do
  let r ← replayModel j
  unless r.assumed.all (fun x => (candidate r.D x.1 x.2).isSome) && takenBy r.D r.assumed do
    throw (if r.assumed.all (fun x => (candidate r.D x.1 x.2).isSome) then untakenText r.D r.assumed
           else "InvalidInput: assumed reading is no candidate")
  let X := correlate (sup r.D).1
  let valid := supModelCheck r.D r.assumed r.Γ r.M
  let value := (VE.SoftNorms.circ X r.φ).eval r.M []
  pure (okWith id [("valid", .bool valid), ("conclusion_value", .bool value),
    ("first_failing", match firstFailing r.D r.assumed r.M with | some l => .str l | none => .null),
    ("assumed", choiceJson r.assumed), ("choice", choiceJson (encodedChoice r.D r.M))])

/-! ## `readings-dead` -/

def runDead (id : String) (j : Json) : Except String Json := do
  let b ← admitS2 (← j.getObjVal? "environment") (← j.getObjVal? "document")
  let D := b.D
  let cert ← VE.CertificateWire.decodeCertificate (← j.getObjVal? "certificate")
  match j.getObjValD "index" with
  | .null =>
    let ok := supReady D && unsatCheck D cert
    pure (okWith id [("accepted", .bool ok),
      ("finding", if ok then .str ("ReadingsUnsatisfiable: " ++ ", ".intercalate (restrictionIds D)) else .null)])
  | n =>
    let s ← VE.Bridge.stringField j "set"
    let i ← match n.getNat? with | .ok i => pure i | .error _ => throw "InvalidInput: invalid index"
    -- A candidate a narrowing in force drops is reported under the narrowing, never as dead (1.9, 14.7).
    let dropped := D.narrowings.any (fun N => match inForce D N with
      | some R => R.id == s && (R.candidates[i]?.map (fun a => !N.keeps.contains a.id)).getD false
      | none => false)
    let ok := supReady D && deadCheck D s i cert
    pure (okWith id [("accepted", .bool ok),
      ("finding", if ok && !dropped then .str s!"DeadReading: {s}:{i}" else .null)])

/-! ## `readings-choice` -/

/-- The unit contents of `choiceDoc D c` in source order, as written (formulas are not sent to the lower route). -/
def choiceJsons (itemsJ : List ItemJ) (c : Choice) : List Json :=
  itemsJ.flatMap (fun it => match it with
    | .fixed _ j => if j matches .arr _ then [] else [j]
    | .bar _ j => [j]
    | .set R => match c.index R.id with
      | some i => match R.readings[i]? with
        | some r => if r.content matches .obj _ then [r.content] else []
        | none => []
      | none => [])

def choiceHash (b : Admitted2) (units : List Json) : Except String String :=
  match b.a.re.chain with
  | .rights => VE.Rights.Wire.rightsDocumentHash b.a.re.lower b.a.re.lowerJson
      (Json.arr ((Json.mkObj [("source_units", toJson b.a.doc.units)] :: units).toArray))
  | .soft => VE.SoftNorms.Wire.softDocumentHash b.a.re.lower b.a.re.lowerJson (Json.arr units.toArray)
  | .norms => VE.Norms.Replay.documentHash b.a.re.lower b.a.re.lowerJson (Json.arr units.toArray)

/-- `lower` runs a case of the lower route named by `dispatch` (`Run.lean` supplies the runners). -/
def runChoice (lower : List String → Json → Json) (id : String) (j : Json) : Except String Json := do
  let b ← admitS2 (← j.getObjVal? "environment") (← j.getObjVal? "document")
  let c ← decodeChoice (j.getObjValD "choice")
  unless compatible b.D c do throw "InvalidInput: the choice is not a compatible complete choice"
  let units := choiceJsons b.a.doc.itemsJ c
  let inner := j.getObjValD "inner"
  let lowerCase := match b.a.re.chain with
    | .rights => (inner.setObjVal! "environment" b.a.re.lowerJson).setObjVal! "document"
        (Json.arr ((Json.mkObj [("source_units", toJson b.a.doc.units)] :: units).toArray))
    | _ => (inner.setObjVal! "environment" b.a.re.lowerJson).setObjVal! "norms" (Json.arr units.toArray)
  let lowerCase := lowerCase.setObjVal! "id" (.str id)
  let answer := lower b.a.re.lower lowerCase
  pure (okWith id [("choice", choiceJson c), ("document_hash", .str (← choiceHash b units)), ("inner", answer)])

/-! ## Dispatch -/

def s2Kinds : List String :=
  ["readings-elaborate", "readings-conflict", "readings-certificate", "readings-model", "readings-dead",
   "readings-choice"]

def runS2 (lower : List String → Json → Json) (id kind : String) (j : Json) : Except String Json := do
  if kind == "readings-elaborate" then return ← runElaborate id j
  if kind == "readings-conflict" then return ← runConflict id j
  if kind == "readings-certificate" then return ← runCertificate id j
  if kind == "readings-model" then return ← runModel id j
  if kind == "readings-dead" then return ← runDead id j
  if kind == "readings-choice" then return ← runChoice lower id j
  throw s!"UnsupportedProfile: case kind {kind} is not available on the readings route"

end VE.Readings.Run
