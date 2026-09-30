import VE.Discourse.Resolve

/-! # Well-formedness `WellFormedDiscourse` (docs/spec/discourse.md 4.1) and the theorems
that rely on it (9.2, 9.3)

`wellFormed` runs the manifest-level checks of 4.1 in order, each returning the diagnostic
text of section 8: the anchor tree (2), names, content names and documents (3), mentions
(4, 5), the bound units (6: every unit with a formula-producing mention validates, which
includes accessibility, typing, uniqueness and slot correspondence), groups and
constraints (7), the joint set (8) and the limits (11). The envelope and profile checks
(1), and the decoding and identity of embedded and imported documents (10), run in the
wrapper (`Admission.lean`). Definition/proof dependencies (9) are W3's, unchanged. -/
namespace VE.Discourse
open VE.English (Tok)
open VE.Route.Admission (ReadingSet DocUnit)
universe u

def req (b : Bool) (e : String) : Except String Unit := if b then .ok () else .error e

/-- Run the stages in order; the first failure is the diagnostic. -/
def runAll : List (Unit → Except String Unit) → Except String Unit
  | [] => .ok ()
  | f :: fs => match f () with
    | .ok _ => runAll fs
    | .error e => .error e

theorem runAll_ok : ∀ (fs : List (Unit → Except String Unit)), runAll fs = .ok () → ∀ f ∈ fs, f () = .ok ()
  | [], _, _, hf => nomatch hf
  | g :: gs, h, f, hf => by
    unfold runAll at h
    split at h
    · rename_i hg
      rcases List.mem_cons.mp hf with rfl | hf
      · exact hg
      · exact runAll_ok gs h f hf
    · cases h

def allOk {α : Type} (xs : List α) (f : α → Except String Unit) : Except String Unit :=
  runAll (xs.map fun x _ => f x)

theorem allOk_ok {α : Type} (xs : List α) (f : α → Except String Unit) (h : allOk xs f = .ok ()) :
    ∀ x ∈ xs, f x = .ok () := by
  intro x hx
  exact runAll_ok _ h _ (List.mem_map.mpr ⟨x, hx, rfl⟩)

theorem runAll_nil : runAll [] = .ok () := rfl

theorem runAll_cons (f : Unit → Except String Unit) (fs : List (Unit → Except String Unit)) :
    runAll (f :: fs) = .ok () ↔ f () = .ok () ∧ runAll fs = .ok () := by
  show (match f () with | .ok _ => runAll fs | .error e => .error e) = .ok () ↔ _
  cases h : f () with
  | ok v => simp
  | error e => simp

theorem req_ok (b : Bool) (e : String) : req b e = .ok () ↔ b = true := by
  unfold req; cases b <;> simp

theorem allOk_iff {α : Type} (xs : List α) (f : α → Except String Unit) :
    allOk xs f = .ok () ↔ ∀ x ∈ xs, f x = .ok () := by
  unfold allOk
  induction xs with
  | nil => simp [runAll]
  | cons x xs ih => simp [runAll_cons, ih]

def spanIn (inner outer : Nat × Nat) : Bool := outer.1 ≤ inner.1 && inner.2 ≤ outer.2
def spansDisjoint (a b : Nat × Nat) : Bool := a.2 ≤ b.1 || b.2 ≤ a.1
def spansNested (a b : Nat × Nat) : Bool := a != b && (spanIn a b || spanIn b a)

def dupOf : List String → Option String
  | [] => none
  | x :: xs => if xs.contains x then some x else dupOf xs

theorem dupOf_none : ∀ xs : List String, dupOf xs = none → xs.Nodup
  | [], _ => List.nodup_nil
  | x :: xs, h => by
    unfold dupOf at h
    split at h
    · cases h
    · rename_i hc
      exact List.nodup_cons.mpr ⟨by simpa using hc, dupOf_none xs h⟩

def firstDup (xs : List String) : Option String :=
  (xs.zipIdx.find? fun (x, i) => (xs.take i).contains x).map Prod.fst

/-- The anchor reaches the root through parents within the fuel. -/
def reachesRoot (D : DDoc) : Nat → Anchor → Bool
  | 0, _ => false
  | n + 1, a => match a.parent with
    | none => true
    | some p => match anchorOf D p with
      | some b => spanIn a.span b.span && reachesRoot D n b
      | none => false

def definitionIn (D : DDoc) (a : Anchor) : Bool :=
  D.base.units.any fun x => decide (x.kind = .definition) && spanIn (x.start, x.stop) a.span

/-- 4.1(2): one tree, nested and non-overlapping spans, unique labels per parent, exports. -/
def anchorsOk (D : DDoc) : Except String Unit := runAll [
  fun _ => req (D.K.anchors.length ≤ 1024) "ResourceLimit: anchors",
  fun _ => match dupOf (D.K.anchors.map Anchor.id) with
    | some a => .error ("DuplicateDeclaration: anchor " ++ a)
    | none => .ok (),
  fun _ => req ((D.K.anchors.filter (·.parent.isNone)).length == 1 || D.K.anchors.isEmpty)
    "InvalidInput: anchors must form one tree",
  fun _ => allOk D.K.anchors fun a => req (reachesRoot D (D.K.anchors.length + 1) a)
    ("DanglingAnchor: " ++ ((a.parent).getD a.id)),
  fun _ => allOk D.K.anchors fun a => allOk D.K.anchors fun b =>
    if a.id != b.id && a.parent == b.parent && a.parent.isSome then
      if a.label.toLower == b.label.toLower then .error ("DuplicateAnchor: " ++ a.label)
      else req (spansDisjoint a.span b.span) ("InvalidInput: anchors " ++ a.id ++ ", " ++ b.id ++ " overlap")
    else .ok (),
  fun _ => allOk D.K.anchors fun a => req (a.exports.all fun p => unaryPred D.E p && definitionIn D a)
    ("ManifestMismatch: anchors." ++ a.id ++ ".exports")]

def scopesOverlap (D : DDoc) (a b : String) : Bool :=
  match anchorOf D a, anchorOf D b with
  | some x, some y => !spansDisjoint x.span y.span
  | _, _ => true

def unitIdsOf (D : DDoc) : List String := D.base.units.map DocUnit.id

/-- 4.1(3): names, content names, documents and imports. -/
def tablesOk (D : DDoc) : Except String Unit := runAll [
  fun _ => req (D.K.names.length ≤ 1024) "ResourceLimit: names",
  fun _ => allOk D.K.names fun n =>
    if !(notBinder n.constant && (D.E.constants n.constant).isSome) then
      .error ("InvalidInput: name " ++ n.constant ++ " is not a declared constant")
    else req (anchorOf D n.scope).isSome ("DanglingAnchor: " ++ n.scope),
  fun _ => match dupOf (D.K.names.map Name.constant) with
    | some c => .error ("DuplicateDeclaration: name " ++ c)
    | none => .ok (),
  fun _ => allOk D.K.names fun n => allOk D.K.names fun n' =>
    if n.constant != n'.constant && n.display.toLower == n'.display.toLower && scopesOverlap D n.scope n'.scope then
      .error ("DuplicateDeclaration: name " ++ n.display) else .ok (),
  fun _ => allOk D.K.contentNames fun c => req (c.units.all (unitIdsOf D).contains && (anchorOf D c.scope).isSome)
    ("InvalidInput: content name " ++ c.name),
  fun _ => allOk D.K.contentNames fun c => allOk D.K.contentNames fun c' =>
    if c.units != c'.units && c.name.toLower == c'.name.toLower && scopesOverlap D c.scope c'.scope then
      .error ("DuplicateDeclaration: content_name " ++ c.name) else .ok (),
  fun _ => req (D.K.documents.length ≤ 64 && D.K.imports.length ≤ 64) "ResourceLimit: documents",
  fun _ => req (D.K.documents.isEmpty || D.E.sorts.contains D.K.documentSort)
    ("InvalidInput: document sort " ++ D.K.documentSort ++ " is not declared"),
  fun _ => match dupOf (D.K.documents.map DocName.name) with
    | some d => .error ("DuplicateDeclaration: document " ++ d)
    | none => .ok (),
  fun _ => allOk D.K.documents fun d =>
    if D.E.constants d.name != some D.K.documentSort then
      .error ("InvalidInput: document " ++ d.name ++ " is not a constant of the document sort")
    else match d.refers with
      | .self => req (d.sourceId.isNone && d.documentId.isNone) ("InvalidInput: document " ++ d.name ++ " pins")
      | .part a => req ((anchorOf D a).isSome && d.sourceId.isNone && d.documentId.isNone) ("DanglingAnchor: " ++ a)
      | .embedded u => req (D.base.units.any fun x => x.id == u && decide (x.kind = .«meta»))
          ("UnknownDocument: " ++ d.name)
      | .imported k => req (D.K.imports.any (·.key == k) && d.sourceId.isSome && d.documentId.isSome)
          ("UnknownDocument: " ++ d.name)]

def formText : Form → String
  | .pronoun => "pronoun" | .demonstrative => "demonstrative" | .definite => "definite"
  | .ordinalPair => "ordinal_pair" | .such => "such" | .possessive => "possessive" | .plural => "plural"
  | .sectionRef => "section_ref" | .definitionRef => "definition_ref" | .documentName => "document_name"
  | .citation => "citation" | .navigation => "navigation"

def kindText : TargetKind → String
  | .entity => "entity" | .predicate => "predicate" | .unit => "unit" | .anchor => "anchor"
  | .rule => "rule" | .claim => "claim" | .document => "document"

def mentionUnitLength (D : DDoc) (x : Mention) : Option Nat := (D.text x.unit).map List.length

def groupedUnits (D : DDoc) : List String := D.K.groups.flatMap Group.spans

def contentOf (D : DDoc) (u : String) : Option VE.Formula := (unitOf D.base u).bind DocUnit.content

/-- The unit carries an active reading set: its readings are its meaning (W2 drops its content). -/
def setUnit (D : DDoc) (u : String) : Bool := D.sets.any (·.unit == u)

/-- A slot position (1.4): a unit with meaning (content or an active reading set) or a group
span is read by a derivation, so a pronoun or demonstrative in it is a slot. -/
def slotUnit (D : DDoc) (u : String) : Bool :=
  (contentOf D u).isSome || setUnit D u || (groupedUnits D).contains u

/-- 4.1(4): a location binding's target exists: an anchor of the table (`DanglingAnchor`), or a
nonempty list of source units (`UnresolvedReference`) that its content name, if any, lists
exactly (`ManifestMismatch: mentions.<m>.content_name`). A formula-producing mention's target is
checked by `Acc` (4.2). -/
def locationTargetOk (D : DDoc) (x : Mention) : Except String Unit :=
  match x.target.kind with
  | .anchor => match x.target.name with
    | some a => req (anchorOf D a).isSome ("DanglingAnchor: " ++ a)
    | none => .error ("InvalidInput: mention " ++ x.id ++ " target")
  | .unit => runAll [
    fun _ => req (!x.target.units.isEmpty && x.target.units.all (unitIdsOf D).contains)
      ("UnresolvedReference: " ++ x.id),
    fun _ => match x.target.contentName with
      | some n => req (D.K.contentNames.any fun c => c.name == n && c.units == x.target.units)
          ("ManifestMismatch: mentions." ++ x.id ++ ".content_name")
      | none => .ok ()]
  | _ => .ok ()

/-- The sort the restriction's context `[σ]` names. -/
def restrictionSort (D : DDoc) (m : Mention) : Option String :=
  match m.restriction with
  | some (.unary q _) => match D.E.predicates q with
    | some [s] => some s
    | _ => none
  | some (.binary q _ _) => match D.E.predicates q with
    | some [s, _] => some s
    | _ => none
  | _ => none

def targetShapeOk (x : Mention) : Bool :=
  let t := x.target
  (x.form != .plural || (decide (2 ≤ t.members.length) && decide t.members.Nodup)) &&
  (x.form != .ordinalPair || match t.pair, t.name with
    | some p, some c => c == p.1 || c == p.2
    | _, _ => false)

/-- The W3 definition version of predicate `p` at `definitions_version`, regenerated from the
environment: the base pair declares no definition versions (W2 admission defers definitions), so
there is none, and a recorded pin can never be confirmed. -/
def definitionVersion (_D : DDoc) (_p : String) : Option Nat := none

/-- A target's recorded `version` pin (3.1): only a `definition_ref` to a predicate carries one,
and it must equal the regenerated definition version (`StaleTarget: <mention>: <target>@<version>`,
4.9); a pin is never carried unchecked. -/
def pinOk (D : DDoc) (x : Mention) : Except String Unit :=
  match x.pin with
  | none => .ok ()
  | some v =>
    if x.form != .definitionRef || x.target.kind != .predicate then .error ("InvalidInput: mention " ++ x.id ++ " target")
    else match x.target.name with
      | some p => req (definitionVersion D p == some v) ("StaleTarget: " ++ x.id ++ ": " ++ p ++ "@" ++ toString v)
      | none => .error ("InvalidInput: mention " ++ x.id ++ " target")

/-- 4.1(4, 5): mentions, their spans, target shapes and pins, kind fit, restrictions and carriers. -/
def mentionsOk (D : DDoc) : Except String Unit := runAll [
  fun _ => req (D.K.mentions.length ≤ mentionLimit) "ResourceLimit: mentions",
  fun _ => match dupOf (D.K.mentions.map Mention.id) with
    | some m => .error ("DuplicateDeclaration: mention " ++ m)
    | none => .ok (),
  fun _ => allOk D.K.mentions fun x =>
    req ((unitIdsOf D).contains x.unit && decide (x.span.1 < x.span.2) &&
      (match mentionUnitLength D x with
       | some n => decide (x.span.2 ≤ n)
       | none => !producing x)) ("InvalidInput: mention " ++ x.id ++ " span"),
  fun _ => allOk D.K.mentions fun x => allOk D.K.mentions fun y =>
    if x.id != y.id && x.unit == y.unit && !spansDisjoint x.span y.span && !spansNested x.span y.span then
      .error ("InvalidInput: mentions " ++ x.id ++ ", " ++ y.id ++ " overlap") else .ok (),
  fun _ => allOk D.K.mentions fun x => req (targetShapeOk x) ("InvalidInput: mention " ++ x.id ++ " target"),
  fun _ => allOk D.K.mentions (pinOk D),
  fun _ => allOk D.K.mentions fun x =>
    req (!((x.form == .pronoun || x.form == .demonstrative) && x.target.kind == .claim))
      ("UnsupportedTarget: " ++ x.id ++ ": claim"),
  fun _ => allOk D.K.mentions fun x => req (formFits x.form x.target.kind)
    ("TargetKindMismatch: " ++ x.id ++ ": " ++ formText x.form ++ ", " ++ kindText x.target.kind),
  -- a location target in a slot position (1.4): a pronoun or demonstrative naming a unit is a
  -- location binding only in a unit no derivation reads
  fun _ => allOk D.K.mentions fun x =>
    req (!(formulaForm x.form && locationKind x.target.kind && slotUnit D x.unit))
      ("TargetKindMismatch: " ++ x.id ++ ": " ++ formText x.form ++ ", " ++ kindText x.target.kind),
  fun _ => allOk D.K.mentions fun x => if producing x then .ok () else locationTargetOk D x,
  fun _ => allOk D.K.mentions fun x =>
    if x.form == .definite then
      match x.restriction, x.reading, restrictionSort D x with
      | some Dr, some .presuppositional, some σ => match x.presuppositionUnit with
        | some u => req (decide (VE.Route.Admission.AssertedUnit D.base u (uniqueD σ Dr)))
            ("ManifestMismatch: mentions." ++ x.id ++ ".presupposition_unit")
        | none => .ok ()
      | some _, some .assertive, some _ => .ok ()
      | _, _, _ => .error ("InvalidInput: restriction of " ++ x.id)
    else .ok ()]

/-- A unit whose meaning is admitted on its own: it carries content or an active reading set,
and is not a group span (a span's meaning is its group's, 1.5). A reading set is never a way
around slot discovery. -/
def contentUnit (D : DDoc) (u : String) : Bool :=
  ((contentOf D u).isSome || setUnit D u) && !(groupedUnits D).contains u

/-- The unit's text has a reference slot: a derivation with a slot, or a reference surface the
grammar does not place (3.4: slots are discovered from the source, never only from the
manifest's recorded mentions). -/
def hasSourceSlot (D : DDoc) (u : String) : Bool :=
  match D.text u with
  | some s => (derivs D u s).any (fun d => !d.slots.isEmpty) || !(discovered D u).isEmpty
  | none => false

/-- The units elaborated on their own: every unit carrying a recorded formula-producing
mention, and every unit with content or a reading set whose source has a reference slot
(recorded or not). -/
def boundUnits (D : DDoc) : List String :=
  (D.K.mentions.filter fun x => producing x).map Mention.unit ++
    (unitIdsOf D).filter fun u => contentUnit D u && hasSourceSlot D u

/-- The prose byte ranges of the unit's recorded formula-producing mentions (a location binding
is never a slot, so it never accounts for one). -/
def recordedBytes (D : DDoc) (u : String) : List (Nat × Nat) :=
  (D.K.mentions.filter fun x => x.unit == u && producing x).map Mention.bytes

/-- The first reference surface of the unit that no recorded formula-producing mention records
with exactly its byte range: overlapping or containing it is not enough (a pronoun `It` recorded
inside the document display `It is safe` leaves the display unrecorded). The Python
`_unrecorded`. -/
def uncoveredSurface (D : DDoc) (u : String) : Option (Nat × Nat) :=
  (discovered D u).find? fun r => !(recordedBytes D u).contains r

/-- Every reference surface of a unit with meaning is recorded (`UnrecordedSlot: <unit>: [a, b)`,
prose bytes, the Python text). -/
def coveredOk (D : DDoc) (u : String) : Except String Unit :=
  if contentUnit D u then match uncoveredSurface D u with
    | some r => .error ("UnrecordedSlot: " ++ u ++ ": [" ++ toString r.1 ++ ", " ++ toString r.2 ++ ")")
    | none => .ok ()
  else .ok ()

/-- 4.1(6), coverage: in document order, every unit with meaning records every reference surface
of its text, before any unit is resolved (Python checks every unit before resolving one). -/
def coverageOk (D : DDoc) : Except String Unit := allOk (unitIdsOf D) (coveredOk D)

/-- 4.1(6): every bound unit validates. -/
def boundOk (D : DDoc) : Except String Unit :=
  allOk (boundUnits D) fun u => match validate D u with
    | .ok _ => .ok ()
    | .error e => .error e

/-- 4.8: the active open reading sets (the latest version per unit, status `open`), in
document order: the sets of the joint enumeration. -/
def activeSets (D : DDoc) : List ReadingSet :=
  (D.sets.filter (·.status == "open")).map fun s => ⟨s.id, s.version, s.readings.map Prod.snd⟩

/-- The reading the owning set records for a group (the comparison point, never trusted). -/
def recordedGroupReading (D : DDoc) (g : Group) : Option VE.Formula :=
  (D.sets.find? fun rs => rs.id == g.set && rs.version == g.version && g.spans.head? == some rs.unit).bind
    fun rs => (rs.readings[g.reading]?).map Prod.snd

/-- A group's reading as the wire names it: its id in the set version (1.5). -/
def readingName (D : DDoc) (g : Group) : String :=
  ((D.sets.find? fun rs => rs.id == g.set && rs.version == g.version).bind fun rs =>
    (rs.readings[g.reading]?).map Prod.fst).getD (toString g.reading)

/-- The first span of a same-witness group (4.6): exactly one derivation, `a|an|some [ADJ]
SORT is P.` with no slot; its sort and the body over the witness. -/
def witnessOpening (D : DDoc) (u : String) : Option (String × VE.Formula) :=
  match D.text u with
  | none => none
  | some s => match derivs D u s with
    | [⟨.core (.some _ .none srt p), []⟩] => some (srt, .unary p (.var 0))
    | [⟨.core (.some _ (.adj q) srt p), []⟩] => some (srt, .and (.unary q (.var 0)) (.unary p (.var 0)))
    | _ => none

/-- A later span of a same-witness group: exactly one derivation, `PRONOUN is P.`, with `P`
a unary predicate of the witness's sort; its body over the witness. -/
def witnessContinuation (D : DDoc) (srt u : String) : Option VE.Formula :=
  match D.text u with
  | none => none
  | some s => match derivs D u s with
    | [⟨.core (.pred (.slot m) false p), _⟩] =>
      if m.form == .pronoun && D.E.predicates p == some [srt] then some (.unary p (.var 0)) else none
    | _ => none

/-- The owning set's reading, regenerated per group from the spans' English (4.6): one
existential over the opening span's sort whose body conjoins every span's predication of
the witness. The recorded reading is compared with it, never used in its place. -/
def groupFormula (D : DDoc) (g : Group) : Option VE.Formula :=
  match g.spans with
  | [] => none
  | first :: rest => do
    let (srt, body) ← witnessOpening D first
    let later ← rest.mapM (witnessContinuation D srt)
    pure (.ex srt (conj (body :: later)))

def owningUnit (_D : DDoc) (g : Group) : Option String := g.spans.head?

/-- 4.1(7): groups and constraints. -/
def groupsOk (D : DDoc) : Except String Unit := runAll [
  fun _ => req (D.K.groups.length ≤ 256 && D.K.groups.all (fun g => decide (g.spans.length ≤ 16)) &&
    D.K.constraints.length ≤ 1024) "ResourceLimit: groups",
  fun _ => allOk D.K.groups fun g =>
    let name := g.set ++ "@" ++ toString g.version ++ ":" ++ readingName D g
    match recordedGroupReading D g with
    | none => .error ("InvalidInput: reading " ++ readingName D g ++ " not in " ++ g.set ++ "@" ++ toString g.version)
    | some φ =>
      if g.spans.isEmpty then .error ("InvalidInput: group " ++ g.set ++ " has no spans") else
      match g.spans.find? (fun u => (contentOf D u).isSome || (boundUnits D).contains u || !(unitIdsOf D).contains u ||
          D.sets.any fun rs => rs.unit == u && !(rs.id == g.set && rs.version == g.version)) with
      | some u => .error ("IndependentFragment: " ++ u)
      | none =>
        if !sharedWitness φ then .error ("WitnessSplit: " ++ name) else
        match groupFormula D g with
        | none => .error ("InvalidInput: group " ++ name ++ " spans are outside the supported fragment")
        | some ψ => req (ψ == φ) ("ManifestMismatch: groups." ++ name),
  fun _ => allOk D.K.constraints fun k => req ([k.a, k.b].all fun (s, v, i) =>
      (activeSets D).any fun rs => rs.id == s && rs.version == v && decide (i < rs.readings.length))
    ("InvalidInput: constraint names an inactive reading")]

/-- 4.1(8): the joint set, validated to completion and nonempty, or UNKNOWN (not a rejection). -/
def jointOk (D : DDoc) : Except String Unit :=
  match compatibleChoices D.K (activeSets D) 64 with
  | .ok _ => .ok ()
  | .error e => if e.startsWith "ResourceLimit" then .ok () else .error e

/-- The validity wording after the document name (2.1): `is [not] a valid VE document.` -/
def validityTail (holds : Bool) : List Tok :=
  ((if holds then ["is"] else ["is", "not"]) ++ ["a", "valid", "ve", "document", "."]).map Tok.word

/-- The validity claims a unit's own wording makes: the document whose display it names and
the polarity. Anything else (a self-truth wording such as `Everything in this document is
true.`) makes none. -/
def validityWording (D : DDoc) (u : String) : List (String × Bool) :=
  match D.text u with
  | none => []
  | some s => D.K.documents.flatMap fun d => [true, false].filterMap fun h =>
      if d.display.any (fun x => lexWords x ++ validityTail h == s) then some (d.name, h) else none

/-- Validity bindings (4.7): `meta` units without content, not self-truth, naming a declared
document that is not a `part`, with the document and polarity regenerated from the unit's
wording. -/
def claimsOk (D : DDoc) (claims : List Validity) : Except String Unit :=
  allOk claims fun v =>
    if !(D.base.units.any fun x => x.id == v.unit && decide (x.kind = .«meta») && x.content.isNone) then
      .error ("InvalidInput: validity unit " ++ v.unit)
    else if D.K.selfTruth.contains v.unit then .error ("InvalidInput: " ++ v.unit ++ " is a self-truth sentence")
    else match D.K.documents.find? (·.name == v.document) with
      | none => .error ("UnknownDocument: " ++ v.document)
      | some d => match d.refers with
        | .part _ => .error ("UnsupportedTarget: " ++ v.unit ++ ": part")
        | _ => match validityWording D v.unit with
          | [(name, holds)] =>
            if name != v.document then .error ("ManifestMismatch: validity." ++ v.unit ++ ".document")
            else req (holds == v.holds) ("ManifestMismatch: validity." ++ v.unit ++ ".holds")
          | [] => .error ("InvalidInput: validity unit " ++ v.unit ++ " is not a validity wording")
          | _ => .error ("InvalidInput: validity unit " ++ v.unit ++ " names more than one document")

/-- Validity bindings and self-truth labels (4.7): `meta` units without content. -/
def labelsOk (D : DDoc) : Except String Unit := runAll [
  fun _ => claimsOk D D.K.validity,
  fun _ => allOk D.K.selfTruth fun u =>
    req (D.base.units.any fun x => x.id == u && decide (x.kind = .«meta») && x.content.isNone)
      ("InvalidInput: self-truth unit " ++ u)]

/-- 4.1 in order; every check returns the diagnostic text of section 8. -/
def wellFormed (D : DDoc) : Except String Unit :=
  runAll [fun _ => anchorsOk D, fun _ => tablesOk D, fun _ => mentionsOk D, fun _ => coverageOk D, fun _ => boundOk D,
    fun _ => groupsOk D, fun _ => jointOk D, fun _ => labelsOk D]

def WellFormedDiscourse (D : DDoc) : Bool := (wellFormed D).toBool

theorem wellFormed_of (D : DDoc) (h : WellFormedDiscourse D = true) : wellFormed D = .ok () := by
  unfold WellFormedDiscourse at h
  cases hw : wellFormed D with
  | ok v => rfl
  | error e => rw [hw] at h; cases h

theorem wf_bound (D : DDoc) (h : WellFormedDiscourse D = true) (x : Mention) (hx : x ∈ D.K.mentions)
    (hf : producing x = true) : ∃ A, validate D x.unit = .ok A := by
  have hb := runAll_ok _ (wellFormed_of D h) (fun _ => boundOk D) (by simp)
  have hu : x.unit ∈ boundUnits D := by
    unfold boundUnits
    exact List.mem_append_left _ (List.mem_map.mpr ⟨x, List.mem_filter.mpr ⟨hx, hf⟩, rfl⟩)
  have := allOk_ok _ _ hb x.unit hu
  split at this
  · rename_i A hA; exact ⟨A, hA⟩
  · cases this

/-! ## The theorems of 9.2 and 9.3 over well-formed documents -/

/-- The validator is sound: whatever it returns is the unique accepted resolution of that unit's text. -/
theorem validate_sound (D : DDoc) (h : WellFormedDiscourse D = true) (u : String) (A : VE.Formula)
    (s : List Tok) (hs : D.text u = some s) (hv : validate D u = .ok A) : Accepted D u s A :=
  validate_accepted D u A s hs hv

/-- Slot correspondence: the recorded formula-producing mentions of the unit are the accepted
derivation's slots. -/
theorem validate_slots_recorded (D : DDoc) (h : WellFormedDiscourse D = true) (u : String) (A : VE.Formula)
    (s : List Tok) (hs : D.text u = some s) (hv : validate D u = .ok A) :
    ∃ d σ, Derives D u s d ∧ (∀ m ∈ d.slots, recordedTarget D m = some (σ m)) ∧ elaborateD D d σ = some A ∧
      recordedSlots D u = d.slots :=
  validate_recorded D u A s hs hv

theorem derives_units {D : DDoc} {u : String} {s : List Tok} {d : DTree} (hd : Derives D u s d) :
    ∀ m ∈ d.slots, m.unit = u ∧ formulaForm m.form = true := by
  obtain ⟨hs, j, hj, _⟩ := hd
  rw [hs]
  intro m hm
  have hnp : ∀ (i e : Nat) (np : NP), npEnd D u s i np = some e → ∀ m ∈ npSlots np, m.unit = u ∧ formulaForm m.form = true := by
    intro i e np h m hm
    cases np with
    | name => simp [npSlots] at hm
    | slot x =>
      simp only [npSlots, List.mem_singleton] at hm
      subst hm
      simp only [npEnd] at h
      split at h
      · rename_i hc
        simp only [Bool.and_eq_true, beq_iff_eq] at hc
        refine ⟨hc.1.1.1, ?_⟩
        have hsf := hc.1.2
        revert hsf
        cases m.form <;> simp [simpleForm, formulaForm]
      · cases h
    | definite x r =>
      cases r with
      | noun p =>
        simp only [npSlots, List.mem_singleton] at hm
        subst hm
        simp only [npEnd] at h
        split at h
        · rename_i hc
          simp only [Bool.and_eq_true, beq_iff_eq] at hc
          rw [hc.1.1.1]; simp [formulaForm]
        · cases h
      | rel p q =>
        simp only [npSlots, List.mem_cons, List.not_mem_nil, or_false] at hm
        simp only [npEnd] at h
        split at h
        · rename_i hc
          simp only [Bool.and_eq_true, beq_iff_eq] at hc
          rcases hm with rfl | rfl
          · rw [hc.1.1.1]; simp [formulaForm]
          · rw [hc.1.1.2]; simp [formulaForm]
        · cases h
  have hmod : ∀ (i e : Nat) (md : Mod), modEnd D u s i md = some e → ∀ m ∈ modSlots md, m.unit = u ∧ formulaForm m.form = true := by
    intro i e md h m hm
    cases md with
    | slot x =>
      simp only [modSlots, List.mem_singleton] at hm
      subst hm
      simp only [modEnd] at h
      split at h
      · rename_i hc
        simp only [Bool.and_eq_true, beq_iff_eq] at hc
        rw [hc.1]; simp [formulaForm]
      · cases h
    | _ => simp [modSlots] at hm
  have hcore : ∀ (i e : Nat) (c : Core), coreEnd D u s i c = some e → ∀ m ∈ coreSlots c, m.unit = u ∧ formulaForm m.form = true := by
    intro i e c h m hm
    cases c with
    | pred subj are p =>
      simp only [coreEnd] at h
      split at h
      · rename_i j hj; exact hnp i j subj hj m hm
      · cases h
    | coord => simp [coreSlots] at hm
    | rel subj p obj =>
      simp only [coreEnd] at h
      split at h
      · rename_i j hj
        split at h
        · rcases List.mem_append.mp hm with hm | hm
          · exact hnp i j subj hj m hm
          · exact hnp (j + 1) e obj h m hm
        · cases h
      · cases h
    | every md srt p =>
      simp only [coreEnd] at h
      split at h
      · split at h
        · rename_i j hj; exact hmod (i + 1) j md hj m hm
        · cases h
      · cases h
    | some an md srt p =>
      simp only [coreEnd] at h
      split at h
      · split at h
        · rename_i j hj; exact hmod (i + 1) j md hj m hm
        · cases h
      · cases h
    | everyDef x srt p sec =>
      simp only [coreEnd] at h
      split at h
      · rename_i hc
        simp only [Bool.and_eq_true, beq_iff_eq] at hc
        simp only [coreSlots, List.mem_singleton] at hm
        subst hm
        rw [hc.2]; simp [formulaForm]
      · cases h
  cases ht : d.tree with
  | core c =>
    rw [ht] at hj hm
    exact hcore 0 j c hj m hm
  | cite x c =>
    rw [ht] at hj hm
    simp only [treeEnd] at hj
    split at hj
    · rename_i hc
      simp only [Bool.and_eq_true, beq_iff_eq] at hc
      rcases List.mem_cons.mp hm with rfl | hm
      · rw [hc.1.1.1.2]; simp [formulaForm]
      · exact hcore 4 j c hj m hm
    · cases hj

/-- A recorded slot names a recorded mention at its unit, span and form. -/
theorem recorded_mention {D : DDoc} {m : Slot} {t : Target} (h : recordedTarget D m = some t) :
    ∃ x ∈ D.K.mentions, mentionAt D m = some x ∧ x.unit = m.unit ∧ x.span = m.span ∧ x.form = m.form := by
  unfold recordedTarget at h
  cases hx : mentionAt D m with
  | none => rw [hx] at h; cases h
  | some x =>
    have hx' := hx
    unfold mentionAt at hx'
    have hp := List.find?_some hx'
    simp only [Bool.and_eq_true, beq_iff_eq] at hp
    exact ⟨x, List.mem_of_find?_eq_some hx', rfl, hp.1.1.1, hp.1.1.2, hp.1.2⟩

/-- The mention an ill-typed derivation's diagnostic names: its culprit slot's recorded
mention, a mention of the unit. -/
theorem ill_culprit {D : DDoc} {u : String} {s : List Tok} {d : DTree} (hd : d ∈ derivs D u s)
    (hi : illTypedOf D d = true) :
    ∃ m ∈ d.slots, ∃ x ∈ D.K.mentions, mentionAt D m = some x ∧ x.unit = u ∧
      illTypedText D u d = "IllTypedTarget: " ++ x.id ++ ": " ++ (((recordedTarget D m).map targetText).getD "?") := by
  simp only [illTypedOf, Bool.and_eq_true, Bool.not_eq_true'] at hi
  obtain ⟨hne, hi⟩ := hi
  cases hv : recordedVec D d with
  | none => rw [hv] at hi; cases hi
  | some vec =>
    obtain ⟨_, hrec⟩ := mapM_recorded D d.slots vec hv
    unfold illTypedText
    rw [hv]
    simp only [Option.getD_some]
    cases hc : culprit D d (assignOf d.slots vec) with
    | none =>
      exfalso
      unfold culprit at hc
      split at hc
      · cases hc
      · cases hsl : d.slots with
        | nil => rw [hsl] at hne; cases hne
        | cons y ys => rw [hsl] at hc; cases hc
    | some m =>
      have hm := culprit_mem D d _ m hc
      obtain ⟨x, hx, hmx, hu, _, _⟩ := recorded_mention (hrec m hm)
      have hu' := (derives_units ((mem_derivs D u s d).mp hd) m hm).1
      exact ⟨m, hm, x, hx, hmx, by rw [hu, hu'], by simp [mentionIdAt, hmx]⟩

/-- The type check is the only filter: an ill-typed recorded elaboration is the named error
`IllTypedTarget: <mention>: <target>`, naming a recorded mention of the unit: the slot whose
target does not fit the sort its position expects (lean/DISCOURSE.md: the statement's
per-slot conclusion cannot hold for every slot of a two-slot derivation;
`ill_typed_target_single` is that conclusion for a unit with one recorded slot). -/
theorem ill_typed_target (D : DDoc) (u : String) (s : List Tok) (hs : D.text u = some s)
    (hlim : D.K.mentions.length ≤ mentionLimit) (d : DTree) (σ : Assignment)
    (hd : Derives D u s d) (hr : ∀ m ∈ d.slots, Acc D m (σ m) ∧ recordedTarget D m = some (σ m))
    (m : Slot) (hm : m ∈ d.slots) (A : VE.Formula) (he : elaborateD D d σ = some A) (hc : A.check D.E [] = false) :
    ∃ x ∈ D.K.mentions, x.unit = u ∧ ∃ rest, validate D u = .error ("IllTypedTarget: " ++ x.id ++ ": " ++ rest) := by
  obtain ⟨d'', hd'', hi, hv⟩ := ill_typed_found D u s hs hlim d σ hd hr m hm A he hc
  obtain ⟨m', _, x, hx, _, hu, ht⟩ := ill_culprit hd'' hi
  exact ⟨x, hx, hu, ((recordedTarget D m').map targetText).getD "?", by rw [hv, ht]⟩

/-- With one recorded formula-producing mention in the unit, the error names exactly it. -/
theorem ill_typed_target_single (D : DDoc) (u : String) (s : List Tok) (hs : D.text u = some s)
    (hlim : D.K.mentions.length ≤ mentionLimit) (d : DTree) (σ : Assignment)
    (hd : Derives D u s d) (hr : ∀ m ∈ d.slots, Acc D m (σ m) ∧ recordedTarget D m = some (σ m))
    (m : Slot) (hm : m ∈ d.slots) (A : VE.Formula) (he : elaborateD D d σ = some A) (hc : A.check D.E [] = false)
    (hone : recordedSlots D u = [m]) :
    ∃ rest, validate D u = .error ("IllTypedTarget: " ++ mentionIdAt D m ++ rest) := by
  obtain ⟨d'', hd'', hi, hv⟩ := ill_typed_found D u s hs hlim d σ hd hr m hm A he hc
  obtain ⟨m', hm', x, hx, hmx, hu, ht⟩ := ill_culprit hd'' hi
  have hmx' := hmx
  unfold mentionAt at hmx'
  have hp := List.find?_some hmx'
  simp only [Bool.and_eq_true, beq_iff_eq] at hp
  have hf := (derives_units ((mem_derivs D u s d'').mp hd'') m' hm').2
  have hin : m' ∈ recordedSlots D u := by
    unfold recordedSlots
    rw [List.mem_mergeSort]
    refine List.mem_map.mpr ⟨x, List.mem_filter.mpr ⟨hx, ?_⟩, ?_⟩
    · simp [producing, hu, hp.1.2, hp.2, hf]
    · rcases m' with ⟨mu, msp, mf⟩
      simp only at hp ⊢
      rw [hp.1.1.1, hp.1.1.2, hp.1.2]
  rw [hone, List.mem_singleton] at hin
  subst hin
  refine ⟨": " ++ ((recordedTarget D m').map targetText).getD "?", ?_⟩
  rw [hv, ht]
  simp [mentionIdAt, hmx, String.append_assoc]

theorem recordedSlots_nil {D : DDoc} {u : String} (h : recordedSlots D u = []) :
    ∀ x ∈ D.K.mentions, x.unit = u → producing x = false := by
  intro x hx hu
  have hl := List.length_mergeSort (le := slotBefore)
    ((D.K.mentions.filter fun x => x.unit == u && producing x).map fun x => (⟨x.unit, x.span, x.form⟩ : Slot))
  unfold recordedSlots at h
  rw [h] at hl
  simp only [List.length_nil, List.length_map] at hl
  have hn := List.length_eq_zero_iff.mp hl.symm
  cases hf : producing x
  · rfl
  · have hmem : x ∈ D.K.mentions.filter (fun x => x.unit == u && producing x) :=
      List.mem_filter.mpr ⟨hx, by simp [hu, hf]⟩
    rw [hn] at hmem
    cases hmem

theorem recordedTarget_none {D : DDoc} {u : String} (h : recordedSlots D u = []) (m : Slot) (hu : m.unit = u)
    (hf : formulaForm m.form = true) : recordedTarget D m = none := by
  unfold recordedTarget mentionAt
  cases hx : D.K.mentions.find? (fun x => x.unit == m.unit && x.span == m.span && x.form == m.form &&
      !locationKind x.target.kind) with
  | none => rfl
  | some x =>
    have hm := List.mem_of_find?_eq_some hx
    have hp := List.find?_some hx
    simp only [Bool.and_eq_true, beq_iff_eq] at hp
    have := recordedSlots_nil h x hm (by rw [hp.1.1.1, hu])
    simp [producing, hp.1.2, hf, hp.2] at this

theorem vectors_acc (D : DDoc) : ∀ (slots : List Slot) (vec : List Target),
    vec ∈ vectors (slots.map (accCands D)) → ∀ m ∈ slots, Acc D m (assignOf slots vec m)
  | [], _, _, m, hm => nomatch hm
  | x :: xs, vec, hv, m, hm => by
    simp only [List.map_cons, vectors, List.mem_flatMap, List.mem_map] at hv
    obtain ⟨t, ht, vs, hvs, rfl⟩ := hv
    by_cases hxm : x = m
    · subst hxm
      rw [assignOf_cons_self]
      exact (List.mem_filter.mp ht).2
    · rw [assignOf_cons_ne x m t xs vs hxm]
      rcases List.mem_cons.mp hm with h | h
      · exact absurd h.symm hxm
      · exact vectors_acc D xs vs hvs m h

theorem slots_of_derivs (D : DDoc) (u : String) (s : List Tok) (d : DTree) (h : d ∈ derivs D u s) :
    d.slots = slotsOf d.tree := ((mem_derivs D u s d).mp h).1

theorem definiteRestrs_nil {t : STree} (h : slotsOf t = []) : definiteRestrs t = [] := by
  unfold definiteRestrs
  split
  · simp [slotsOf, coreSlots, npSlots] at h
    revert h; rename_i r _ _; cases r <;> simp [npSlots]
  · simp [slotsOf] at h
  · rfl

theorem elaborate_tree {D : DDoc} {d d' : DTree} (h : d'.tree = d.tree) (σ : Assignment) :
    elaborateD D d' σ = elaborateD D d σ := by
  unfold elaborateD; rw [h]

/-- Complete on the supported fragment within fuel. -/
theorem validate_complete (D : DDoc) (h : WellFormedDiscourse D = true) (u : String) (s : List Tok)
    (hs : D.text u = some s) (hsup : Supported D u s) (A : VE.Formula) (hA : Accepted D u s A) :
    validate D u = .ok A := by
  by_cases hb : recordedSlots D u = []
  · -- no recorded formula-producing mention at `u`: the validator's steps succeed on `hA`
    obtain ⟨d, σ, hd, hr, he, hck, hall⟩ := hA
    have hnil : d.slots = [] := by
      cases hsl : d.slots with
      | nil => rfl
      | cons m ms =>
        have hm : m ∈ d.slots := by rw [hsl]; exact List.mem_cons_self
        obtain ⟨hu, hf⟩ := derives_units hd m hm
        have := (hr m hm).2
        rw [recordedTarget_none hb m hu hf] at this
        cases this
    have hill : (derivs D u s).find? (illTypedOf D) = none := by
      apply List.find?_eq_none.mpr
      intro d' hd' hi
      simp only [illTypedOf, Bool.and_eq_true, Bool.not_eq_true'] at hi
      obtain ⟨hne, hi⟩ := hi
      cases hsl : d'.slots with
      | nil => rw [hsl] at hne; cases hne
      | cons m ms =>
        split at hi
        · rename_i vec hvec
          obtain ⟨_, hrec⟩ := mapM_recorded D d'.slots vec hvec
          have hm : m ∈ d'.slots := by rw [hsl]; exact List.mem_cons_self
          obtain ⟨hu, hf⟩ := derives_units ((mem_derivs D u s d').mp hd') m hm
          have := hrec m hm
          rw [recordedTarget_none hb m hu hf] at this
          cases this
        · cases hi
    have hd0 : d ∈ derivs D u s := (mem_derivs D u s d).mpr hd
    have hcomp : (d, ([] : List Target), A) ∈ typedComps D (derivs D u s) := by
      refine (mem_typedComps D _ _ _ _).mpr ⟨hd0, by simp [hnil, vectors], ?_, hck⟩
      rw [elaborate_congr D d _ σ (fun m hm => by rw [← hd.1, hnil] at hm; cases hm)]
      exact he
    have hcomps : ∀ x ∈ typedComps D (derivs D u s), x.1.tree = d.tree ∧ x.1.slots = [] ∧
        elaborateD D x.1 (assignOf x.1.slots x.2.1) = some A := by
      intro x hx
      obtain ⟨d', vec', A'⟩ := x
      obtain ⟨hd', hv', he', hc'⟩ := (mem_typedComps D _ d' vec' A').mp hx
      have hder := (mem_derivs D u s d').mp hd'
      have hacc : ∀ m ∈ d'.slots, Acc D m (assignOf d'.slots vec' m) := by
        intro m hm
        exact vectors_acc D d'.slots vec' hv' m hm
      obtain ⟨ht, hsl, _⟩ := hall d' (assignOf d'.slots vec') A' hder hacc he' hc'
      refine ⟨ht, by rw [hsl, hnil], ?_⟩
      simp only
      rw [elaborate_tree ht, elaborate_congr D d _ σ (fun m hm => by rw [← hd.1, hnil] at hm; cases hm)]
      exact he
    unfold validate
    rw [if_neg (Nat.not_lt.mpr hsup.1), hs]
    dsimp only
    rw [hill, if_neg (Nat.not_lt.mpr hsup.2)]
    cases hc : typedComps D (derivs D u s) with
    | nil => rw [hc] at hcomp; cases hcomp
    | cons x rest =>
      obtain ⟨d0, vec0, A0⟩ := x
      have h0 := hcomps (d0, vec0, A0) (by rw [hc]; exact List.mem_cons_self)
      simp only at h0
      obtain ⟨ht0, hs0, he0⟩ := h0
      have hrest : rest.find? (fun x => !aligned D d0 x.1 vec0 x.2.1) = none := by
        apply List.find?_eq_none.mpr
        intro x hx
        obtain ⟨htx, hsx, _⟩ := hcomps x (by rw [hc]; exact List.mem_cons_of_mem _ hx)
        simp [aligned, htx, hsx, ht0, hs0]
      simp only [hrest]
      unfold checkRecorded
      have hrv : recordedVec D d0 = some [] := by simp [recordedVec, hs0]
      have hres : restrictionMismatch D d0 (assignOf d0.slots []) = none := by
        unfold restrictionMismatch
        rw [definiteRestrs_nil (by rw [← hs0]; exact (slots_of_derivs D u s d0 (by
          have := (mem_typedComps D _ d0 vec0 A0).mp (by rw [hc]; exact List.mem_cons_self)
          exact this.1)).symm)]
        rfl
      rw [hs0] at hres he0
      have hassign : assignOf [] vec0 = assignOf [] [] := by funext m; simp [assignOf]
      rw [hassign] at he0
      simp only [hrv, hs0, List.zip_nil_left, List.all_nil, Bool.not_true, Bool.false_eq_true, if_false,
        aligned, beq_self_eq_true, Bool.and_self, hb, bne_self_eq_false, hres, he0, hck, if_true]
  · -- a recorded formula-producing mention at `u`: `u` is bound, so well-formedness validated it
    obtain ⟨x, hx, hxf⟩ : ∃ x ∈ D.K.mentions, x.unit = u ∧ producing x = true := by
      unfold recordedSlots at hb
      cases hl : (D.K.mentions.filter fun x => x.unit == u && producing x) with
      | nil => simp [hl] at hb
      | cons x xs =>
        have hm : x ∈ D.K.mentions.filter fun x => x.unit == u && producing x := by rw [hl]; exact List.mem_cons_self
        obtain ⟨hmem, hp⟩ := List.mem_filter.mp hm
        simp only [Bool.and_eq_true, beq_iff_eq] at hp
        exact ⟨x, hmem, hp⟩
    obtain ⟨A', hA'⟩ := wf_bound D h x hx hxf.2
    rw [hxf.1] at hA'
    rw [hA', accepted_unique D u s A' A (validate_accepted D u A' s hs hA') hA]

/-! ## The intended meaning and faithfulness (9.3) -/

/-! ## Typing a derivation directly (without the elaboration)

`TreeTyped D d σ` sorts a derivation under an assignment: each predicate is applied to terms
of its declared sorts (constants, a plural's members, the binder of a quantifier or a
description), each quantifier and description binds a declared sort, and a relational
restriction's other argument has the relation's sort. It reads the tree and the targets only;
`elaborate_typed` shows it is exactly the type check of the elaboration. -/

def RestrTyped (D : DDoc) (σ : Assignment) : Restr → Prop
  | .noun q => ∃ s, D.E.predicates q = some [s] ∧ s ∈ D.E.sorts
  | .rel q poss => ∃ s r c, D.E.predicates q = some [s, r] ∧ termConst (canonTarget D (σ poss)) = some c ∧
      s ∈ D.E.sorts ∧ D.E.constants c = some r

def PredTyped (D : DDoc) (σ : Assignment) (subj : NP) (p : String) : Prop :=
  match subj with
  | .definite _ r => RestrTyped D σ r ∧ ∃ s Dr, restrFormula D σ r = some (s, Dr) ∧ D.E.predicates p = some [s]
  | _ => ∃ cs s, npConsts D σ subj = some cs ∧ D.E.predicates p = some [s] ∧ ∀ c ∈ cs, D.E.constants c = some s

def ModTyped (D : DDoc) (σ : Assignment) (md : Mod) (srt : String) : Prop :=
  match modPred D σ md with
  | some none => True
  | some (some q) => D.E.predicates q = some [srt]
  | none => False

def CoreTyped (D : DDoc) (σ : Assignment) : Core → Prop
  | .pred subj _ p => PredTyped D σ subj p
  | .coord a _ b _ p => ∃ s, D.E.predicates p = some [s] ∧ D.E.constants a = some s ∧ D.E.constants b = some s
  | .rel subj p obj => ∃ a b s r, npConsts D σ subj = some [a] ∧ npConsts D σ obj = some [b] ∧
      D.E.predicates p = some [s, r] ∧ D.E.constants a = some s ∧ D.E.constants b = some r
  | .every md srt p | .some _ md srt p => srt ∈ D.E.sorts ∧ ModTyped D σ md srt ∧ D.E.predicates p = some [srt]
  | .everyDef m srt p _ => srt ∈ D.E.sorts ∧
      (∃ q, propertyOf (canonTarget D (σ m)) = some q ∧ D.E.predicates q = some [srt]) ∧ D.E.predicates p = some [srt]

def TreeTyped (D : DDoc) (d : DTree) (σ : Assignment) : Prop :=
  match d.tree with
  | .core c | .cite _ c => CoreTyped D σ c

theorem conj_wf (E : VE.Environment) (Γ : List String) : ∀ l : List VE.Formula,
    (conj l).WellFormed E Γ ↔ ∀ r ∈ l, r.WellFormed E Γ
  | [] => by simp [conj, VE.Formula.WellFormed]
  | [a] => by simp [conj]
  | a :: b :: l => by simp [conj, VE.Formula.WellFormed, conj_wf E Γ (b :: l)]

theorem npConsts_ne (D : DDoc) (σ : Assignment) (np : NP) (cs : List String) (h : npConsts D σ np = some cs) :
    cs ≠ [] := by
  cases np with
  | name c k => simp only [npConsts, Option.some.injEq] at h; subst h; simp
  | slot m =>
    simp only [npConsts] at h
    split at h
    · unfold pluralMembers at h
      split at h
      · split at h
        · rename_i ms _ hl
          cases h
          intro he; rw [he] at hl; simp at hl
        · cases h
      · cases h
    · cases hc : termConst (canonTarget D (σ m)) with
      | none => rw [hc] at h; cases h
      | some c => rw [hc] at h; simp only [Option.map_some, Option.some.injEq] at h; subst h; simp
  | definite => simp [npConsts] at h

theorem conjOn_wf (E : VE.Environment) (p : String) (cs : List String) (hne : cs ≠ []) :
    (conjOn p cs).WellFormed E [] ↔ ∃ s, E.predicates p = some [s] ∧ ∀ c ∈ cs, E.constants c = some s := by
  unfold conjOn
  rw [conj_wf]
  simp only [List.mem_map, forall_exists_index, and_imp, forall_apply_eq_imp_iff₂, VE.Formula.WellFormed,
    VE.Term.sortOf]
  constructor
  · intro h
    obtain ⟨c, hc⟩ := List.exists_mem_of_ne_nil cs hne
    obtain ⟨s, hp, _⟩ := h c hc
    refine ⟨s, hp, fun c' hc' => ?_⟩
    obtain ⟨s', hp', hs'⟩ := h c' hc'
    rw [hp] at hp'
    cases hp'
    exact hs'
  · rintro ⟨s, hp, hs⟩ c hc
    exact ⟨s, hp, hs c hc⟩

theorem restr_wf (D : DDoc) (σ : Assignment) (r : Restr) (s : String) (Dr : VE.Formula)
    (h : restrFormula D σ r = some (s, Dr)) (Γ : List String) :
    (s ∈ D.E.sorts ∧ Dr.WellFormed D.E (s :: Γ)) ↔ RestrTyped D σ r := by
  cases r with
  | noun q =>
    simp only [restrFormula] at h
    split at h
    · rename_i s' hq
      cases h
      simp [VE.Formula.WellFormed, VE.Term.sortOf, RestrTyped, hq]
    · cases h
  | rel q poss =>
    simp only [restrFormula] at h
    split at h
    · rename_i s' r' c hq hc
      cases h
      simp only [VE.Formula.WellFormed, VE.Term.sortOf, RestrTyped, hq, hc, List.getElem?_cons_zero,
        Option.some.injEq, List.cons.injEq, and_true]
      constructor
      · rintro ⟨hs, s1, r, ⟨rfl, rfl⟩, _, hcr⟩; exact ⟨_, _, _, ⟨rfl, rfl⟩, rfl, hs, hcr⟩
      · rintro ⟨s1, r, c', ⟨rfl, rfl⟩, rfl, hs, hcr⟩; exact ⟨hs, _, _, ⟨rfl, rfl⟩, rfl, hcr⟩
    · cases h

theorem unary_var_wf (E : VE.Environment) (p s : String) (Γ : List String) :
    (VE.Formula.unary p (.var 0)).WellFormed E (s :: Γ) ↔ E.predicates p = some [s] := by
  simp [VE.Formula.WellFormed, VE.Term.sortOf]

/-- The type check of an elaboration is the typing of its derivation. -/
theorem core_typed (D : DDoc) (σ : Assignment) (c : Core) (A : VE.Formula) (h : coreFormula D σ c = some A) :
    A.WellFormed D.E [] ↔ CoreTyped D σ c := by
  cases c with
  | pred subj are p =>
    simp only [coreFormula, CoreTyped] at h ⊢
    cases subj with
    | definite m r =>
      simp only [predFormula, definiteFormula, PredTyped] at h ⊢
      split at h
      · cases hr : restrFormula D σ r with
        | none => rw [hr] at h; simp at h
        | some x =>
          obtain ⟨s, Dr⟩ := x
          rw [hr] at h
          have h0 := restr_wf D σ r s Dr hr []
          have h1 := restr_wf D σ r s Dr hr [s]
          have hex : (∃ s' Dr', some (s, Dr) = some (s', Dr') ∧ D.E.predicates p = some [s']) ↔
              D.E.predicates p = some [s] := by
            constructor
            · rintro ⟨s', Dr', he, hp⟩; cases he; exact hp
            · intro hp; exact ⟨s, Dr, rfl, hp⟩
          rw [hex]
          cases hread : readingAt D m with
          | none => rw [hread] at h; simp at h
          | some rd =>
            rw [hread] at h
            cases rd with
            | assertive =>
              simp only [Option.some.injEq] at h
              subst h
              have heq : (VE.Formula.eq (.var 0) (.var 1)).WellFormed D.E [s, s] := ⟨s, rfl, rfl⟩
              change s ∈ D.E.sorts ∧ (Dr.WellFormed D.E [s] ∧ ((s ∈ D.E.sorts ∧ (Dr.WellFormed D.E [s, s] ∧
                (VE.Formula.eq (.var 0) (.var 1)).WellFormed D.E [s, s])) ∧
                (VE.Formula.unary p (.var 0)).WellFormed D.E [s])) ↔ _
              rw [unary_var_wf, ← h0]
              constructor
              · rintro ⟨hs, hd, _, hp⟩; exact ⟨⟨hs, hd⟩, hp⟩
              · rintro ⟨⟨hs, hd⟩, hp⟩; exact ⟨hs, hd, ⟨hs, (h1.mpr (h0.mp ⟨hs, hd⟩)).2, heq⟩, hp⟩
            | presuppositional =>
              simp only [Option.some.injEq] at h
              subst h
              change s ∈ D.E.sorts ∧ (Dr.WellFormed D.E [s] ∧ (VE.Formula.unary p (.var 0)).WellFormed D.E [s]) ↔ _
              rw [unary_var_wf, ← h0]
              constructor
              · rintro ⟨hs, hd, hp⟩; exact ⟨⟨hs, hd⟩, hp⟩
              · rintro ⟨⟨hs, hd⟩, hp⟩; exact ⟨hs, hd, hp⟩
            | distributive => simp at h
      · cases h
    | name c k =>
      simp only [predFormula, PredTyped] at h ⊢
      cases hc : npConsts D σ (.name c k) with
      | none => rw [hc] at h; cases h
      | some cs =>
        rw [hc] at h
        simp only [Option.map_some, Option.some.injEq] at h
        subst h
        rw [conjOn_wf D.E p cs (npConsts_ne D σ _ cs hc)]
        simp
    | slot m =>
      simp only [predFormula, PredTyped] at h ⊢
      cases hc : npConsts D σ (.slot m) with
      | none => rw [hc] at h; cases h
      | some cs =>
        rw [hc] at h
        simp only [Option.map_some, Option.some.injEq] at h
        subst h
        rw [conjOn_wf D.E p cs (npConsts_ne D σ _ cs hc)]
        simp
  | coord a ka b kb p =>
    simp only [coreFormula, CoreTyped, Option.some.injEq] at h ⊢
    subst h
    simp only [VE.Formula.WellFormed, VE.Term.sortOf]
    constructor
    · rintro ⟨⟨s, hp, ha⟩, ⟨s', hp', hb⟩⟩
      rw [hp] at hp'; cases hp'
      exact ⟨s, hp, ha, hb⟩
    · rintro ⟨s, hp, ha, hb⟩
      exact ⟨⟨s, hp, ha⟩, ⟨s, hp, hb⟩⟩
  | rel subj p obj =>
    simp only [coreFormula, CoreTyped] at h ⊢
    unfold relFormula at h
    split at h
    · rename_i a b ha hb
      cases h
      simp only [VE.Formula.WellFormed, VE.Term.sortOf]
      constructor
      · rintro ⟨s, r, hp, hsa, hsb⟩; exact ⟨a, b, s, r, ha, hb, hp, hsa, hsb⟩
      · rintro ⟨a', b', s, r, ha', hb', hp, hsa, hsb⟩
        rw [ha] at ha'; rw [hb] at hb'
        cases ha'; cases hb'
        exact ⟨s, r, hp, hsa, hsb⟩
    · cases h
  | every md srt p =>
    simp only [coreFormula, CoreTyped, ModTyped] at h ⊢
    cases hq : modPred D σ md with
    | none => rw [hq] at h; cases h
    | some q =>
      rw [hq] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      cases q with
      | none => simp [VE.Formula.WellFormed, quantBody, VE.Term.sortOf, eq_comm]
      | some q => simp [VE.Formula.WellFormed, quantBody, VE.Term.sortOf, eq_comm]
  | some an md srt p =>
    simp only [coreFormula, CoreTyped, ModTyped] at h ⊢
    cases hq : modPred D σ md with
    | none => rw [hq] at h; cases h
    | some q =>
      rw [hq] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      cases q with
      | none => simp [VE.Formula.WellFormed, quantBody, VE.Term.sortOf, eq_comm]
      | some q => simp [VE.Formula.WellFormed, quantBody, VE.Term.sortOf, eq_comm]
  | everyDef m srt p sec =>
    simp only [coreFormula, CoreTyped] at h ⊢
    cases hq : propertyOf (canonTarget D (σ m)) with
    | none => rw [hq] at h; cases h
    | some q =>
      rw [hq] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      simp [VE.Formula.WellFormed, VE.Term.sortOf, eq_comm]

/-- The type check of an elaboration is the typing of its derivation, read off the tree. -/
theorem elaborate_typed (D : DDoc) (d : DTree) (σ : Assignment) (A : VE.Formula) (h : elaborateD D d σ = some A) :
    A.check D.E [] = true ↔ TreeTyped D d σ := by
  rw [VE.check_iff_wellFormed]
  unfold elaborateD at h
  unfold TreeTyped
  split at h
  · rename_i c hc
    rw [hc]
    exact core_typed D σ c A h
  · rename_i m c hc
    rw [hc]
    split at h
    · exact core_typed D σ c A h
    · cases h

/-- Where the slot-by-slot meaning is defined, so is the elaboration. -/
theorem elaborate_of_meaning (D : DDoc) (S : VE.Structure.{u}) (d : DTree) (σ : Assignment)
    (h : (meaningOf D S d σ).isSome = true) : (elaborateD D d σ).isSome = true := by
  have core : ∀ c, (coreMeaning D S σ c).isSome = true → (coreFormula D σ c).isSome = true := by
    intro c hc
    cases c with
    | pred subj are p =>
      cases subj with
      | definite m r =>
        simp only [coreMeaning, coreFormula, predMeaning, predFormula, definiteMeaning, definiteFormula] at hc ⊢
        split at hc
        · rename_i hb
          rw [if_pos hb]
          have hfst := (restr_agree D S σ r).1
          cases hr : restrMeaning D S σ r with
          | none => rw [hr] at hc; simp at hc
          | some x =>
            obtain ⟨s, R⟩ := x
            rw [hr] at hc hfst
            cases hf : restrFormula D σ r with
            | none => rw [hf] at hfst; cases hfst
            | some y =>
              obtain ⟨s', Dr⟩ := y
              cases hrd : readingAt D m with
              | none => rw [hrd] at hc; simp at hc
              | some rd => rw [hrd] at hc; cases rd <;> simp_all
        · simp at hc
      | name c k => simpa [coreMeaning, coreFormula, predMeaning, predFormula] using hc
      | slot m => simpa [coreMeaning, coreFormula, predMeaning, predFormula] using hc
    | coord => simp [coreFormula]
    | rel subj p obj =>
      simp only [coreMeaning, coreFormula, relFormula] at hc ⊢
      split at hc
      · rename_i a b ha hb; simp [ha, hb]
      · simp at hc
    | every md srt p => simpa [coreMeaning, coreFormula] using hc
    | some an md srt p => simpa [coreMeaning, coreFormula] using hc
    | everyDef m srt p sec => simpa [coreMeaning, coreFormula] using hc
  rcases d with ⟨t, sl⟩
  cases t with
  | core c => exact core c h
  | cite m c =>
    simp only [meaningOf, elaborateD] at h ⊢
    split at h
    · rename_i hcl; simp only [hcl, if_true]; exact core c h
    · simp at h

/-- 4.4: the intended meaning: some derivation and validated assignment (the recorded,
accessible, well-sorted one) whose slot-by-slot meaning holds in `S`, all read off the tree
and the targets directly, without the elaboration. -/
def Intended (D : DDoc) (u : String) (s : List Tok) (S : VE.Structure.{u}) : Prop :=
  ∃ d σ, Derives D u s d ∧ (∀ m ∈ d.slots, Acc D m (σ m) ∧ recordedTarget D m = some (σ m)) ∧
    TreeTyped D d σ ∧ SlotMeaning D S [] d σ

/-- 4.4: the elaborated formula holds exactly when the intended meaning does, on every
admissible structure. -/
theorem elaborate_faithful (D : DDoc) (h : WellFormedDiscourse D = true) (u : String) (s : List Tok)
    (hs : D.text u = some s) (A : VE.Formula) (hv : validate D u = .ok A) (S : VE.Structure) (hS : S.Admissible D.E) :
    A.denote S [] ↔ Intended D u s S := by
  have hacc := validate_sound D h u A s hs hv
  constructor
  · intro hA
    obtain ⟨d, σ, hd, hr, he, hck, _⟩ := hacc
    exact ⟨d, σ, hd, hr, (elaborate_typed D d σ A he).mp hck,
      (elaborateD_capture D d σ A he S hS [] (VE.typed_empty S)).mp hA⟩
  · rintro ⟨d', σ', hd', hr', hty, hM⟩
    have hsome : (meaningOf D S d' σ').isSome = true := by
      unfold SlotMeaning at hM
      cases hmo : meaningOf D S d' σ' with
      | none => rw [hmo] at hM; exact hM.elim
      | some _ => rfl
    obtain ⟨A', he'⟩ := Option.isSome_iff_exists.mp (elaborate_of_meaning D S d' σ' hsome)
    have hc' := (elaborate_typed D d' σ' A' he').mpr hty
    have hAA := accepted_no_pruning D u s A hacc d' σ' A' hd' (fun m hm => (hr' m hm).1) he' hc'
    rw [← hAA]
    exact (elaborateD_capture D d' σ' A' he' S hS [] (VE.typed_empty S)).mpr hM

/-- The symbols a formula uses: sorts of binders, predicates and constants. -/
def termSymbols : VE.Term → List String
  | .var _ => []
  | .const c => [c]

def symbolsOf : VE.Formula → List String
  | .top | .bottom => []
  | .unary p t => p :: termSymbols t
  | .binary p t w => p :: (termSymbols t ++ termSymbols w)
  | .eq t w => termSymbols t ++ termSymbols w
  | .not a => symbolsOf a
  | .and a b | .or a b | .implies a b => symbolsOf a ++ symbolsOf b
  | .all s a | .ex s a => s :: symbolsOf a

/-- A symbol declared in the environment. -/
def DeclaredSymbol (E : VE.Environment) (q : String) : Prop :=
  q ∈ E.sorts ∨ E.predicates q ≠ none ∨ E.constants q ≠ none

theorem termSymbols_declared {E : VE.Environment} {Γ : List String} {t : VE.Term} {s : String}
    (h : t.sortOf E Γ = some s) : ∀ q ∈ termSymbols t, DeclaredSymbol E q := by
  cases t with
  | var => simp [termSymbols]
  | const c =>
    simp only [termSymbols, List.mem_singleton]
    rintro q rfl
    simp only [VE.Term.sortOf] at h
    exact Or.inr (Or.inr (by rw [h]; simp))

theorem symbolsOf_declared {E : VE.Environment} : ∀ (a : VE.Formula) (Γ : List String), a.WellFormed E Γ →
    ∀ q ∈ symbolsOf a, DeclaredSymbol E q
  | .top, _, _, q, hq => nomatch hq
  | .bottom, _, _, q, hq => nomatch hq
  | .unary p t, Γ, ⟨s, hp, ht⟩, q, hq => by
    rcases List.mem_cons.mp hq with rfl | hq
    · exact Or.inr (Or.inl (by rw [hp]; simp))
    · exact termSymbols_declared ht q hq
  | .binary p t w, Γ, ⟨s, r, hp, ht, hw⟩, q, hq => by
    rcases List.mem_cons.mp hq with rfl | hq
    · exact Or.inr (Or.inl (by rw [hp]; simp))
    · rcases List.mem_append.mp hq with hq | hq
      · exact termSymbols_declared ht q hq
      · exact termSymbols_declared hw q hq
  | .eq t w, Γ, ⟨s, ht, hw⟩, q, hq => by
    rcases List.mem_append.mp hq with hq | hq
    · exact termSymbols_declared ht q hq
    · exact termSymbols_declared hw q hq
  | .not a, Γ, h, q, hq => symbolsOf_declared a Γ h q hq
  | .and a b, Γ, h, q, hq | .or a b, Γ, h, q, hq | .implies a b, Γ, h, q, hq => by
    rcases List.mem_append.mp hq with hq | hq
    · exact symbolsOf_declared a Γ h.1 q hq
    · exact symbolsOf_declared b Γ h.2 q hq
  | .all s a, Γ, h, q, hq | .ex s a, Γ, h, q, hq => by
    rcases List.mem_cons.mp hq with rfl | hq
    · exact Or.inl h.1
    · exact symbolsOf_declared a (s :: Γ) h.2 q hq

/-- No new symbols: the elaboration is well formed over `E` itself and every symbol it uses is
declared there (no witness constant, choice function or fresh predicate). -/
theorem elaborate_no_new_symbols (D : DDoc) (u : String) (A : VE.Formula) (hv : validate D u = .ok A) :
    A.WellFormed D.E [] ∧ ∀ q ∈ symbolsOf A, DeclaredSymbol D.E q := by
  have hw := (VE.check_iff_wellFormed D.E [] A).mp (validate_closed D u A hv)
  exact ⟨hw, symbolsOf_declared A [] hw⟩

end VE.Discourse
