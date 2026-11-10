import VE.Rights.Admission
import VE.SoftNorms.Run
import VE.Judgments.Scan

/-! The `ve_service` mode `rights` (docs/spec/rights.md 9.4), formerly the one-shot `ve_rights_route`. Each case is
`{"id", "environment", "kind", "document", ...}`; a `rights@0` environment must also enable
`soft-norms@0` and `norms@0`; `document` is the array of unit contents of 3.2.

* `rights-elaborate`: → `environment_prime` (`E″′`), `generated` (each rights-generated
  predicate with its source keys), `lines` (per instance: right, source and instance kind,
  rule name, predicate, holder slot, bearer, node), `limitations` (the labelled `Lim_D`),
  `bars`, `derived`, `order`, `background` (with the `soft` and `rights` slots), `premises`,
  `colliding_pairs`, `conflict_targets`, `narrowings` (per line: the limitations in scope, the
  bar's reach, and each mechanism with its licence without certificates and the grounds it rests
  on), `rule_narrowings` (per rule: the mechanisms naming it, and what each of its citations
  licenses), `distinction` (per right-derived predicate), `findings` with `located_findings` (each with its line's
  span when the request's optional `located` names each unit's source unit), `fragment`,
  `warnings`; or the shared diagnostic.
* `rights-projections`: `model` (a finite base model over `E″′_base` passing
  `Background_base″`) and optionally `holder` / `bearer` → `rights_of`, `duties_of`: the
  selecting line instances with their tuples.
* `rights-scope`: `certificates` (scope target `<rule>:<mechanism>` ↦ package) → `findings`
  and, per mechanism, its licence and the certification target `∀x̄. cond_n° → limpack_N`
  (`conclusion`) a package must prove (`Wire.rights_wire_scope_sound`).
* `rights-conflict`: `packages` (target ↦ package over `Background_base″`) and optionally a `situation` (a finite base
  model, checked) → `CONFLICT-FREE` with `conditional_on` and 7.3's parts (`weighing_points`, `situation_exhibited`,
  `budget`, `situation`), or `UNKNOWN` (`Wire.rights_wire_conflict_sound`); or `witness` →
  `CONFLICT`, classified (`Wire.rights_wire_conflict_witness_sound`).
* `rights-bar`: rule reading → per right-derived permission predicate: the barred right
  lines, the blocked default rules (on `m` or `require` on its dual) and the strict rules
  that are composition candidates (4.7); without an overlap witness no conflict is asserted.
  Query reading → per predicate the
  target `∀x̄. aimed_m(x̄) → ¬m(x̄)` and, when a certificate is supplied, whether it is entailed.
* `rights-certificate`: `premises`, `conclusion`, `certificate` bound to
  `background″ ++ layer premises ++ premises` over `E″′` → `valid`, `conditional_on`
  (`Wire.rights_wire_acceptance`).
* `admission`: a W2 document with active rights units and exact regenerated leaves.
* A case without a rights construct is delegated unchanged to soft's `Run.runCase`. -/
namespace VE.Rights.Run
open Lean
open VE.Norms
open VE.SoftNorms (SoftNode soften)
open VE.Rights.Wire
open VE.SoftNorms.Wire (enc)

/-- A rights construct: the `rights@0` profile, the vocabulary's `rights` block, a `rights-*`
case kind, or a rights unit in the document. -/
def usesRightsPath (j : Json) : Bool :=
  let env := j.getObjValD "environment"
  let profile := match env.getObjValD "profiles" with
    | .arr ps => ps.toList.any (·.getStr?.toOption == some rightsProfile)
    | _ => false
  let block := ((env.getObjValD "vocabulary").getObjVal? "rights").toBool
  let kind := match j.getObjValD "kind" with
    | .str k => k.startsWith "rights-"
    | _ => false
  let rightsUnit (u : Json) := ["right", "right_lines", "limitation", "bar"].any (fun k => (u.getObjVal? k).toBool)
  let units := match j.getObjValD "document" with
    | .arr us => us.toList.any rightsUnit
    | d => match d.getObjValD "units" with
      | .arr us => us.toList.any (fun u => rightsUnit (u.getObjValD "content"))
      | _ => false
  profile || block || kind || units

/-! ## Regenerated outputs -/

def kindText : Kind → String
  | .claim => "claim" | .liberty => "liberty" | .immunity => "immunity" | .power => "power"

def ikindText : IKind → String
  | .claim => "claim" | .liberty => "liberty" | .immunity => "immunity"
  | .powerLiberty => "powerLiberty" | .powerRecognition => "powerRecognition"

/-- The source keys rendered beside each generated predicate name (1.6). -/
def generatedKeys (D : RightsDoc) : List Json :=
  (limKeys D).map (fun k => Json.mkObj [("name", .str (limName ((limKeys D).idxOf k + 1))),
      ("kind", .str "lim"), ("limitation", .str k.1), ("act", .str k.2)]) ++
  (condKeys D).map (fun k => Json.mkObj [("name", .str (condName ((condKeys D).idxOf k + 1))),
      ("kind", .str "cond"), ("limitation", .str k.1), ("act", .str k.2.1), ("condition", .str k.2.2)]) ++
  (if D.bars = [] then [] else (barPreds D).map (fun m => Json.mkObj [("name", .str (aimedName (barIndex D m))),
      ("kind", .str "aimed"), ("predicate", .str m)]))

/-- The fixed English wording of a generated rights predicate. -/
def conjugatedAct (phrase : String) : String :=
  match phrase.splitOn " " with
  | head :: verb :: rest =>
    if head != "{0}" then phrase else
    let stem := verb.dropRight 1
    let ending := if verb == "be" then "is"
      else if verb == "have" then "has"
      else if verb == "do" then "does"
      else if verb == "go" then "goes"
      else if ["s", "x", "z", "ch", "sh", "o"].any verb.endsWith then verb ++ "es"
      else if verb.endsWith "y" && !(stem.toList.getLast?.map (fun c => ("aeiou".toList.contains c))).getD true
        then stem ++ "ies"
      else verb ++ "s"
    String.intercalate " " (["{0}", ending] ++ rest)
  | _ => phrase

def generatedWordings (D : RightsDoc) : Json := Json.mkObj <|
  (limKeys D).map (fun k => (limName ((limKeys D).idxOf k + 1),
    .str s!"limitation {limDisplay D k.1} holds where {conjugatedAct (actPhrase D k.2)}")) ++
  (condKeys D).map (fun k => (condName ((condKeys D).idxOf k + 1),
    .str s!"{condVerbalisation D k.1 k.2.2} where {conjugatedAct (actPhrase D k.2.1)}")) ++
  (if D.bars == [] then [] else (barPreds D).map (fun m =>
    (aimedName (barIndex D m), .str s!"{conjugatedAct (actPhrase D m)} aimed at the destruction of a right")))

def nodeJson (X : SoftNode) : Json :=
  Json.mkObj [("name", .str X.name), ("predicate", .str X.pred), ("sign", .bool X.sign),
    ("mode", .str (if X.mode == .strict then "strict" else "default")), ("guard", enc X.guard),
    ("unless", Json.arr (X.carveOuts.map enc).toArray), ("over", toJson X.over), ("hard", .bool X.hard)]

def lineJson (D : RightsDoc) (RN : String × Line) : Json :=
  Json.mkObj ([("right", .str RN.1), ("kind", .str (kindText RN.2.kind)), ("instance", .str (ikindText RN.2.ikind)),
    ("rule", .str RN.2.node.name), ("predicate", .str RN.2.node.pred), ("holder_slot", toJson (holderSlot D RN.2)),
    ("node", nodeJson (nodeOf D RN.2))] ++
    (match RN.2.bearer, RN.2.source.norm with
     | some b, some n => [("bearer", .str b), ("source_line", .str n.name)]
     | _, _ => []))

/-- The licence of a mechanism without certificates, or `none`: the text of its grounds. -/
def licence (D : RightsDoc) (N : Line) (n : Narrowing) : Option String := (ground D N n).map Ground.text

/-- The licence is the first relation of Scope.lean the request holds: a citation, a collision with
another right's line, a same-effect strict rule; the limitation and the bar license themselves. -/
theorem licence_spec (D : RightsDoc) (N : Line) (n : Narrowing) :
    licence D N n = match n with
      | .limPack => some "limitation"
      | .bar => some "bar"
      | .blockedBy M =>
        if cited D N n then some "cited" else if rightCollision D N n then some "collision"
        else if sameEffectStrict D N M then some s!"effect delivered by strict rule {M}" else none
      | _ => if cited D N n then some "cited" else if rightCollision D N n then some "collision" else none := by
  have text : ∀ {n : Narrowing}, n ≠ .limPack → n ≠ .bar →
      (citedGround D N n).map Ground.text = if cited D N n then some "cited" else none := by
    intro n h1 h2
    have hk := citedGround_isSome D N n h1 h2
    cases hg : citedGround D N n with
    | some g =>
      obtain ⟨_, _, _, rfl⟩ := citedGround_eq hg
      rw [hg] at hk; simp [← hk, Ground.text]
    | none => rw [hg] at hk; simp [← hk]
  cases n with
  | limPack => rfl
  | bar => rfl
  | blockedBy M =>
    have ht := text (n := .blockedBy M) (by simp) (by simp)
    simp only [licence, ground, Option.map_or]
    rw [ht]
    cases cited D N (.blockedBy M) <;> cases rightCollision D N (.blockedBy M) <;>
      cases sameEffectStrict D N M <;> simp [Ground.text]
  | dominatedBy M =>
    have ht := text (n := .dominatedBy M) (by simp) (by simp)
    simp only [licence, ground, Option.map_or]
    rw [ht]
    cases cited D N (.dominatedBy M) <;> cases rightCollision D N (.dominatedBy M) <;> simp [Ground.text]
  | carveOut i =>
    simp only [licence, ground, text (n := .carveOut i) (by simp) (by simp)]; simp [rightCollision]
  | exception M =>
    simp only [licence, ground, text (n := .exception M) (by simp) (by simp)]; simp [rightCollision]
  | excepted => simp only [licence, ground, text (n := .excepted) (by simp) (by simp)]; simp [rightCollision]
  | switch π => simp only [licence, ground, text (n := .switch π) (by simp) (by simp)]; simp [rightCollision]

def narrowingsJson (D : RightsDoc) (certs : List (Option VE.Tableau.Certificate)) : Json :=
  Json.arr ((linesOf D).map (fun RN => Json.mkObj [("right", .str RN.1), ("rule", .str RN.2.node.name),
    ("in_scope", .bool (D.limits.any (fun L => inScope D L RN.1 RN.2))),
    ("mechanisms", Json.arr ((narrowings D RN.2).map (fun n => Json.mkObj ([("mechanism", .str (mechText n)),
      ("target", .str (scopeTargetName RN.2 n)), ("conclusion", enc (certTarget D RN.2 n))] ++
      match licence D RN.2 n with
      | some l => [("licence", .str l)]
      | none => if certified D certs RN.2 n then [("licence", .str "certified")] else [("licence", .null)]))).toArray)])).toArray

/-- The rule a rule-named mechanism names: `exception M`, `blockedBy M`, `dominatedBy M`. -/
def namedRule : Narrowing → Option String
  | .exception M | .blockedBy M | .dominatedBy M => some M
  | _ => none

/-- A licence's grounds as the elaboration writes them: the citation, the colliding line or the
strict rule; `null` for the limitation and the bar, which license themselves, and for none. -/
def groundJson : Option Ground → Json
  | some (.cited R K) => Json.mkObj [("citation", Json.mkObj [("rule", .str R), ("key", .str K)])]
  | some (.collision M) => Json.mkObj [("line", .str M)]
  | some (.effect M) => Json.mkObj [("rule", .str M)]
  | _ => .null

/-- The elaboration's narrowings: per line, the limitations in scope (the limitation mechanism is
listed exactly when there is one, `limPack_mem_narrowings`) and the bar's reach (the bar mechanism is
listed exactly when there is one, `bar_mem_narrowings`); per mechanism, its licence without
certificates and the grounds it rests on (`licence` is their text). -/
def elaboratedNarrowingsJson (D : RightsDoc) : Json :=
  Json.arr ((linesOf D).map (fun RN => Json.mkObj [("right", .str RN.1), ("rule", .str RN.2.node.name),
    ("in_scope", .bool !(scopeLimits D RN.2).isEmpty),
    ("limitations", toJson ((scopeLimits D RN.2).map (·.name))),
    ("bar", match ruleBarReach D RN.2 with | some m => .str m | none => .null),
    ("mechanisms", Json.arr ((narrowings D RN.2).map (fun n => Json.mkObj [("mechanism", .str (mechText n)),
      ("target", .str (scopeTargetName RN.2 n)), ("conclusion", enc (certTarget D RN.2 n)),
      ("licence", match licence D RN.2 n with | some l => .str l | none => .null),
      ("grounds", groundJson (ground D RN.2 n))])).toArray)])).toArray

/-- Per rule of `T″` without bars (`directNodes`, in order): the mechanisms that name it, and per
citation of its source in key order (`citesOf`), the mechanisms whose licence rests on it. -/
def ruleNarrowingsJson (D : RightsDoc) : Json :=
  let mechs := (linesOf D).flatMap (fun RN => (narrowings D RN.2).map (fun n =>
    (scopeTargetName RN.2 n, namedRule n, ground D RN.2 n)))
  Json.arr ((directNodes D).map (fun X => Json.mkObj [("rule", .str X.name),
    ("narrows", toJson ((mechs.filter (fun m => m.2.1 == some X.name)).map (·.1))),
    ("citations", Json.arr ((citesOf D X.name).map (fun kv => Json.mkObj [("key", .str kv.1),
      ("licenses", toJson ((mechs.filter (fun m => m.2.2 == some (Ground.cited X.name kv.1))).map (·.1)))])).toArray)])).toArray

def distinctionJson (D : RightsDoc) : Json :=
  Json.arr ((VE.SoftNorms.dedup ((linesOf D).map (·.2.node.pred))).map (fun p => Json.mkObj
    [("predicate", .str p), ("independent", .bool (independentReported D p)),
     ("hits", Json.arr ((distinctionHits D p).map (fun (N, q, c) => Json.mkObj [("rule", .str N.node.name),
        ("right", .str N.right), ("protected", .str q), ("cited", .bool c)])).toArray)])).toArray

/-- A finding as a report row (8): its code, rule and right, its line's span (`lineSpan`; `null` when the request
locates no line) and its text. -/
def findingJson (f : Finding) : Json :=
  Json.mkObj [("code", .str f.code), ("rule", .str f.rule), ("right", .str f.right),
    ("span", if f.span.isEmpty then .null else .str f.span), ("text", .str f.text)]

def regenerated (D : RightsDoc) (environment : Json) : List (String × Json) :=
  let soft := VE.SoftNorms.Wire.regeneratedCore (correlate D) environment
  let findings := noDistinction D
  [("environment_prime", (primeJsonR D environment).toOption.getD .null),
   ("generated", Json.arr (generatedKeys D).toArray),
   ("wordings", generatedWordings D),
   ("lines", Json.arr ((linesOf D).map (lineJson D)).toArray),
   ("limitations", Json.arr ((limPremisesLabelled D).map (fun (l, a) =>
      Json.mkObj [("label", .str l), ("ast", enc a)])).toArray),
   ("bars", Json.arr ((barNodes D).map nodeJson).toArray),
   ("rights_background", Json.arr ((limPremisesLabelled D).map (fun (l, a) =>
      VE.SoftNorms.Wire.bgEntry "rights" l a)).toArray),
   ("narrowings", elaboratedNarrowingsJson D),
   ("rule_narrowings", ruleNarrowingsJson D),
   ("distinction", distinctionJson D),
   ("findings", Json.arr (findings.map (fun f => Json.str f.text)).toArray),
   ("located_findings", Json.arr (findings.map findingJson).toArray)] ++
  soft.filter (fun kv => kv.1 != "environment_prime")

/-! ## Status of rights source units -/

/-- A rule is open (rights spec 7.2) when it is a default, has switches, or an open name occurs in its act, its guard
or a carve-out; the act is read by the shared scan as the atom of `N.pred` (only its name is read). A line's
limitations and their conditions are its carve-outs here (`nodeOf`) and `scopeLimits` in `unitOpen`. -/
def nodeOpen (openNames : List String) (N : SoftNode) : Bool :=
  N.mode == .default || !N.alterable.isEmpty ||
    !(VE.Judgments.opensIn openNames (.unary N.pred (.var 0) :: N.guard :: N.carveOuts)).isEmpty

/-- `nodeOpen` read through the shared scan (judgment-terms spec 3). It was byte-neutral to the body before the scan;
since rights-cfr-4 (DRI 2026-11-09, reviews/dri-decisions-20261109-lp0801.md item 1) it also reads the act, so a rule
whose act predicate is an open name is open where it was not before; every other rule keeps its answer. -/
theorem nodeOpen_eq (openNames : List String) (N : SoftNode) :
    nodeOpen openNames N =
      (N.mode == .default || !N.alterable.isEmpty || openNames.contains N.pred ||
        (VE.Norms.preds N.guard).any openNames.contains ||
        N.carveOuts.any (fun f => (VE.Norms.preds f).any openNames.contains)) := by
  simp only [nodeOpen, VE.Judgments.opensIn_isEmpty, List.any_cons, List.any_nil, VE.Norms.preds, Bool.or_false,
    Bool.or_assoc]

def sourceRuleNames (line : Json) : List String :=
  ["norm", "liberty", "recognition"].filterMap (fun field =>
    ((line.getObjValD field).getObjValD "name").getStr?.toOption)

def unitRuleNames (unit : Json) : List String :=
  let body := if (unit.getObjVal? "right").toBool then unit.getObjValD "right"
              else unit.getObjValD "right_lines"
  match body.getObjValD "lines" with
  | .arr lines => lines.toList.flatMap sourceRuleNames
  | _ => []

def lineSourceName (N : Line) : String :=
  match N.ikind with
  | .powerLiberty => (N.source.liberty.map (·.name)).getD ""
  | .powerRecognition => (N.source.recognition.map (·.name)).getD ""
  | _ => (N.source.norm.map (·.name)).getD ""

def unitOpen (D : RightsDoc) (openNames : List String) (unit : Json) : Bool :=
  if (unit.getObjVal? "limitation").toBool || (unit.getObjVal? "bar").toBool then true
  else if (unit.getObjVal? "norm").toBool then
    let name := ((unit.getObjValD "norm").getObjValD "name").getStr?.toOption.getD ""
    (outsideRules D).any (fun n => n.name == name && nodeOpen openNames n)
  else
    let names := unitRuleNames unit
    (linesOf D).any (fun (_, line) => names.contains (lineSourceName line) &&
      (nodeOpen openNames (nodeOf D line) || !(scopeLimits D line).isEmpty ||
        (D.bars != [] && (line.ikind == .liberty || line.ikind == .powerLiberty))))

def unitStatuses (D : RightsDoc) (openNames : List String) (document : Json) : Json :=
  let names := openNames ++ (genEntries D).map (·.1) ++ VE.SoftNorms.decisionNames (correlate D)
  match document with
  | .arr units => toJson (units.toList.map (unitOpen D names))
  | _ => toJson ([] : List Bool)

/-- The located lines of a request (8): its optional `located` field gives, for each unit of `document` after the
`source_units` entry, the id of the source unit it was copied from, one of `source_units`; every line of a `right` or
`right_lines` unit is located at that id. Its length is compared before its items are decoded. -/
def locate (D : RightsDoc) (j : Json) : Except String (List (String × String)) := do
  let .ok value := j.getObjVal? "located" | pure []
  let units := match j.getObjValD "document" with
    | .arr us => us.toList.filter (fun (u : Json) => !(u.getObjVal? "source_units").toBool)
    | _ => []
  unless (value.getArr?.map Array.size).toOption == some units.length do
    throw "InvalidInput: located must name one source unit per document unit"
  let ids ← VE.Bridge.strings value
  if let some u := ids.find? (fun u => !D.sourceUnits.contains u) then throw s!"UnknownSymbol: unit {u}"
  let names : List (String × String) := (units.zip ids).flatMap (fun (u, i) => (unitRuleNames u).map (·, i))
  pure ((linesOf D).filterMap (fun (_, N) =>
    (names.find? (·.1 == lineSourceName N)).map (fun (_, i) => (N.node.name, i))))

/-- The exhibited situation's tables (5.3 (2)): for each decision predicate of `T″` (the exceptions, switches and
`outweighs` decisions) and each rights-generated predicate (limitation, condition and, under a bar, aimed), its
tuples in the checked finite base model. -/
def situationTables (D : RightsDoc) (M : VE.FiniteModel VE.Bridge.Entity) : Json :=
  Json.arr ((VE.SoftNorms.decisionNames (correlate D) ++ (genEntries D).map (·.1)).map (fun p => Json.mkObj
    [("predicate", .str p), ("tuples", toJson ((M.relations p).map (·.map (·.2))))])).toArray

/-! ## Projections on a finite base model -/

/-- Every typed tuple of the sorts over the model's domains. -/
def tuples (M : VE.FiniteModel VE.Bridge.Entity) : List String → List (List VE.Bridge.Entity)
  | [] => [[]]
  | s :: ss => (M.domains s).flatMap (fun x => (tuples M ss).map (x :: ·))

def projections (D : RightsDoc) (M : VE.FiniteModel VE.Bridge.Entity) : List (String × Line × List VE.Bridge.Entity) :=
  (linesOf D).flatMap (fun RN => (tuples M (sortsOf D RN.2)).filterMap (fun vs =>
    if (outcomeSubst D (selectsR D RN.2)).eval M (tupleVal vs) then some (RN.1, RN.2, vs) else none))

def entryJson (t : String × Line × List VE.Bridge.Entity) : Json :=
  Json.mkObj [("right", .str t.1), ("rule", .str t.2.1.node.name), ("instance", .str (ikindText t.2.1.ikind)),
    ("tuple", toJson (t.2.2.map (·.2)))]

def projectionsResult (src : RightsSource) (j : Json) : Except String (List (String × Json)) := do
  let ⟨M, _⟩ ← decodeModelR src (Json.mkObj [("model", j.getObjValD "model")])
  unless backgroundValidR src.D M do throw (VE.Route.Wire.invalidModel "rights background")
  let sel := projections src.D M
  let holder := (j.getObjValD "holder").getStr?.toOption
  let bearer := (j.getObjValD "bearer").getStr?.toOption
  let rightsOf := sel.filter (fun t => match holder with
    | some h => (t.2.2[holderSlot src.D t.2.1]?).map (·.2) == some h
    | none => true)
  let dutiesOf := sel.filter (fun t => dutyKind t.2.1 && match bearer with
    | some b => (t.2.2.head?).map (·.2) == some b
    | none => true)
  pure [("rights_of", Json.arr (rightsOf.map entryJson).toArray), ("duties_of", Json.arr (dutiesOf.map entryJson).toArray)]

/-! ## Premises used by a certificate -/

def rightsLabelled (D : RightsDoc) : List (String × VE.Formula) :=
  VE.SoftNorms.Wire.softLabelled (correlate D) ++ limPremisesLabelled D

/-- `Background_base″` with the labelled premise replaced by `⊤` at its position. -/
def baseWithout (D : RightsDoc) (label : String) : List VE.Formula :=
  VE.Norms.backgroundBase (soften (correlate D)) ++ (rightsLabelled D).map (fun (l, f) => if l == label then .top else f)

def conflictUses (r : RightsConflictReplay) (label : String) : Bool :=
  ((targets (soften (correlate r.src.D))).zip r.certs).any (fun (t, c) => match c with
    | some c => !VE.Tableau.checkCertificate (envAt (soften (correlate r.src.D)) 0) (baseWithout r.src.D label)
        (targetConclusion t) c
    | none => false)

def entailmentUses (r : RightsEntailmentReplay) (label : String) : Bool :=
  !VE.Tableau.checkCertificate (envAt (soften (correlate r.src.D)) (size (soften (correlate r.src.D))))
    (VE.Norms.background (soften (correlate r.src.D)) ++
      (rightsLabelled r.src.D).map (fun (l, f) => if l == label then .top else f) ++
      elaborate (soften (correlate r.src.D)).T ++ r.premises) r.conclusion r.cert

/-- The premises a result is conditional on: the open coherence labels and every limitation label. -/
def openLabels (D : RightsDoc) : List String :=
  VE.SoftNorms.Wire.openCoherence (correlate D) ++ (limPremisesLabelled D).map (·.1)

/-! ## The bar -/

def barResult (src : RightsSource) (environment document certs : Json) : List (String × Json) :=
  let D := src.D
  let C := correlate D
  let rows := (if D.bars.isEmpty then [] else barPreds D).map (fun m =>
    if ruleReading D then
      let barred := ((lineNodes D).filter (fun X => X.pred == m && X.sign)).map (·.name)
      let blocked := (C.T.nodes.filter (fun X => X.mode == .default &&
        (X.pred == m || (X.sign && VE.SoftNorms.dualPerm C X.pred == some m)))).map (·.name)
      let composition := (D.soft.T.nodes.filter (fun X => X.mode == .strict &&
        ((X.pred == m && X.sign) || (X.sign && VE.SoftNorms.dualPerm C X.pred == some m)))).map (·.name) ++
        ((lineNodes D).filter (fun X => X.mode == .strict && X.sign && VE.SoftNorms.dualPerm C X.pred == some m)).map (·.name)
      Json.mkObj [("predicate", .str m), ("aimed", .str (aimedName (barIndex D m))), ("reading", .str "rule"),
        ("barred", toJson barred), ("blocked_defaults", toJson blocked),
        ("composition_candidates", toJson composition), ("composition_conflicts", toJson ([] : List String))]
    else
      let target := bindAll (VE.SoftNorms.sortsOf D.soft m) (.implies (aimedF D m) (.not (atom m (VE.SoftNorms.sortsOf D.soft m))))
      let entailed : Option Bool := match certs.getObjVal? m with
        | .error _ => none
        | .ok cj => match VE.CertificateWire.decodeCertificate cj, primeJsonR D environment with
          | .ok c, .ok prime =>
            match VE.Route.Wire.bindingOk src.re.profiles prime
                ((backgroundR D ++ elaborate (soften C).T).map enc) (enc target)
                c.environment_id c.premise_meaning_ids c.conclusion_meaning_id with
            | .ok () => some (VE.Tableau.checkCertificate (envAt (soften C) (size (soften C)))
                (backgroundR D ++ elaborate (soften C).T) target c)
            | .error _ => some false
          | _, _ => some false
      Json.mkObj ([("predicate", .str m), ("aimed", .str (aimedName (barIndex D m))), ("reading", .str "query"),
        ("target", enc target)] ++ match entailed with
          | some b => [("entailed", .bool b)]
          | none => []))
  let _ := document
  [("bars", Json.arr rows.toArray)]

/-! ## The conflict answer (7.3) -/

/-- The situation a request exhibits (5.3 (2)): its optional `situation`, a finite base model over `E″′_base` that
must pass `Background_base″`; `none` when the request has none. -/
def exhibit (src : RightsSource) (j : Json) : Except String (Option (VE.FiniteModel VE.Bridge.Entity)) :=
  match j.getObjVal? "situation" with
  | .ok m => do
    let ⟨M, _⟩ ← decodeModelR src (Json.mkObj [("model", m)])
    unless backgroundValidR src.D M do throw (VE.Route.Wire.invalidModel "rights background")
    pure (some M)
  | .error _ => pure none

/-- The budget the rights route quotes (7.3: `UNKNOWN (<budget>)`). No situation is searched for here. -/
def conflictBudget : Nat := 10000

/-- 7.3's situation part on this route: `yes` for the request's checked situation; with none supplied, no search ran,
so the line says so and that the budget went unused (rights-cfr-2-budget-1), never an UNKNOWN of a search. -/
def exhibitedText (supplied : Bool) : String :=
  if supplied then "yes" else s!"none supplied (not searched; budget {conflictBudget} unused)"

/-- What this route's `<j>` counts (7.3), named after it: WP(T) with no pair evidence (`openCoherence`); the soft
route's `<j>` is its `conditional_on` instead (docs/rights/rights-cfr-2-budget-1/REPORT.md). -/
def weighingGloss : String := "colliding default pairs no ranking resolves"

/-- A rights-conflict answer over certificate packages, from the replay's verdict `free`, its first failing certificate
and the premises its certificates use. CONFLICT-FREE carries 7.3's status line: the premises it is conditional on with
their labels, the weighing points open (the colliding default pairs no ranking resolves; no pair evidence is taken
here) and whether a situation is exhibited (`exhibitedText`); beside it the same parts as fields. UNKNOWN
names the first failing certificate. -/
def conflictAnswerOf (id : String) (D : RightsDoc) (free : Bool) (failure : Option String) (uses : String → Bool)
    (M : Option (VE.FiniteModel VE.Bridge.Entity)) : Json :=
  let verdict := if free then "CONFLICT-FREE" else "UNKNOWN"
  let weighing := VE.SoftNorms.Wire.openCoherence (correlate D)
  let labels := weighing ++ (limPremisesLabelled D).map (·.1)
  let conditional := if free then labels.filter uses else []
  let coherence := conditional.filter (fun l => l.startsWith "soft:")
  let limitation := conditional.filter (fun l => l.startsWith "rights:")
  let exhibited := exhibitedText M.isSome
  let statusText := if free then
    s!"CONFLICT-FREE among rules on the same act, conditional on {coherence.length} coherence premises and {limitation.length} limitation premises ({", ".intercalate conditional}); {weighing.length} weighing points open ({weighingGloss}); situation exhibited: {exhibited}"
    else s!"UNKNOWN: {failure.getD "target unspecified"}, budget 10000"
  VE.Route.Wire.ok id ([("verdict", .str verdict), ("status_text", .str statusText),
    ("targets", toJson ((targets (soften (correlate D))).map (·.1))),
    ("conditional_on", toJson conditional)] ++
    (if free then [("weighing_points", toJson weighing), ("situation_exhibited", .bool M.isSome),
      ("budget", toJson conflictBudget), ("situation", (M.map (situationTables D)).getD .null)] else []) ++
    match failure with
    | some d => if free then [] else [("detail", .str d)]
    | none => [])

def conflictAnswer (id : String) (res : RightsConflictReplay) (M : Option (VE.FiniteModel VE.Bridge.Entity)) : Json :=
  conflictAnswerOf id res.src.D res.conflictFree (firstFailure res) (conflictUses res) M

/-! ## Dispatch -/

def encodeAdmitted (id reportId : String) (res : Admission.Admitted) : Json :=
  let labels := VE.SoftNorms.Wire.openCoherence (correlate res.src.D) ++
    (limPremisesLabelled res.src.D).map (·.1)
  let conditional := labels.filter (fun l => res.report.assumptions.any (fun c => c.label == l))
  VE.Route.Wire.ok id [("admitted", .bool true), ("report", Norms.Run.reportJson res.report),
    ("report_id", .str reportId), ("kinds", Json.arr res.kinds.toArray),
    ("conditional_on", toJson conditional)]

def runAdmission (id : String) (environment document : Json) : Except String Json := do
  let res ← Admission.admitDocument environment document
  let canonical ← Norms.Wire.canonicalEnvironmentJson environment
  let envId ← VE.Route.Wire.environmentId res.src.re.profiles canonical
  let reportId ← VE.CertificateWire.digest (Norms.Run.reportDomain res.src.re.profiles)
    (Norms.Run.reportPayload envId document res.report)
  return encodeAdmitted id reportId res

def RightsAdmissionAnswer (id : String) (environment document answer : Json) : Prop :=
  ∃ res : Admission.Admitted, ∃ reportId : String,
    Admission.admitDocument environment document = .ok res ∧
    WellFormedRights res.src.D = true ∧
    answer = encodeAdmitted id reportId res ∧
    VE.Rights.Wire.primeJsonR res.src.D environment = .ok res.prime ∧
    VE.Norms.Admission.checkBindings res.src.re.profiles res.prime res.decoded = .ok () ∧
    VE.Graph.SoundReport.{0} (VE.SoftNorms.envPrime (correlate res.src.D)) res.graph res.report ∧
    (∀ w ∈ res.wires, Admission.NodeAdmitted res.src res.doc res.couplingIds w) ∧
    VE.Route.Admission.CitationsClosed res.doc res.report ∧
    VE.Route.Admission.ChoicesCompatible res.report ∧
    Admission.CouplingChoicesCompatible document res.report = true ∧
    (∀ S : VE.Structure.{0}, S.Admissible (VE.SoftNorms.envPrime (correlate res.src.D)) →
      Sat S (backgroundR res.src.D ++ elaborate (soften (correlate res.src.D)).T) →
      Sat S ((Admission.otherAssumptions res).map (·.formula)) →
      res.report.root.formula.denote S []) ∧
    ∃ canonical envId, Norms.Wire.canonicalEnvironmentJson environment = .ok canonical ∧
      VE.Route.Wire.environmentId res.src.re.profiles canonical = .ok envId ∧
      VE.CertificateWire.digest (Norms.Run.reportDomain res.src.re.profiles)
        (Norms.Run.reportPayload envId document res.report) = .ok reportId

open VE.Order.ProfileGate (bind_ok) in
theorem runAdmission_sound (id : String) (environment document answer : Json)
    (h : runAdmission id environment document = .ok answer) :
    RightsAdmissionAnswer id environment document answer := by
  unfold runAdmission at h
  obtain ⟨res, hr, h⟩ := bind_ok h
  obtain ⟨canonical, hc, h⟩ := bind_ok h
  obtain ⟨envId, he, h⟩ := bind_ok h
  obtain ⟨reportId, hd, h⟩ := bind_ok h
  cases h
  obtain ⟨hwf, hp, hb, hs, hn, hcit, hch, hcoupling⟩ :=
    Admission.admitDocument_spec environment document res hr
  exact ⟨res, reportId, hr, hwf, rfl, hp, hb, hs, hn, hcit, hch, hcoupling,
    (fun S hS hg ho => Admission.rights_wire_report_consequence environment document res hr S hS hg ho),
    canonical, envId, hc, he, hd⟩

def runRightsKind (id kind : String) (j : Json) : Except String Json := do
  if kind == "admission" then
    return ← runAdmission id (← j.getObjVal? "environment") (← j.getObjVal? "document")
  if kind == "rights-elaborate" then
    let environment ← j.getObjVal? "environment"
    let document ← j.getObjVal? "document"
    let src ← decodeRightsSource environment document
    let openNames ← match j.getObjVal? "open_predicates" with
      | .ok value => VE.Bridge.strings value
      | .error _ => pure []
    let D := { src.D with located := ← locate src.D j }
    return VE.Route.Wire.ok id (regenerated D environment ++ [("unit_open", unitStatuses D openNames document)])
  if kind == "rights-projections" then
    let src ← decodeRightsSource (← j.getObjVal? "environment") (j.getObjValD "document")
    return VE.Route.Wire.ok id (← projectionsResult src j)
  if kind == "rights-scope" then
    let r ← replayRightsScope j
    -- The replay's findings with their spans: the same texts, so `licensed` is `r.findings.isEmpty`
    -- (`limitationScope_texts`) and `rights_wire_scope_sound` speaks of this answer.
    let findings := limitationScope { r.src.D with located := ← locate r.src.D j } r.certs
    return VE.Route.Wire.ok id [("findings", Json.arr (findings.map (fun f => Json.str f.text)).toArray),
      ("licensed", .bool findings.isEmpty), ("located_findings", Json.arr (findings.map findingJson).toArray),
      ("narrowings", narrowingsJson r.src.D r.certs)]
  if kind == "rights-certificate" then
    let r ← replayRightsEntailment j
    let conditional := if r.valid then (openLabels r.src.D).filter (entailmentUses r) else []
    return VE.Route.Wire.ok id [("valid", .bool r.valid),
      ("background", toJson (backgroundR r.src.D).length),
      ("layers", toJson (elaborate (soften (correlate r.src.D)).T).length),
      ("conditional_on", toJson conditional)]
  if kind == "rights-bar" then
    let environment ← j.getObjVal? "environment"
    let document := j.getObjValD "document"
    let src ← decodeRightsSource environment document
    return VE.Route.Wire.ok id (barResult src environment document (j.getObjValD "certificates"))
  if kind == "rights-conflict" && (j.getObjVal? "witness").toBool then
    let ⟨src, w⟩ ← replayRightsWitness j
    let names ← VE.Bridge.strings ((j.getObjValD "witness").getObjValD "tuple")
    let situation := String.intercalate ", " names
    return VE.Route.Wire.ok id ([("verdict", .str (if w.conflict then "CONFLICT" else "UNKNOWN")),
      ("target", .str w.target.1), ("targets", toJson ((targets (soften (correlate src.D))).map (·.1))),
      ("status_text", .str (if w.conflict then s!"CONFLICT: {witnessKind w.target} at {situation}"
                            else s!"UNKNOWN: {w.target.1}, budget 10000"))] ++
      (if w.conflict then [("witness_kind", .str (witnessKind w.target))] else []))
  if kind == "rights-conflict" then
    let res ← replayRightsConflict j
    return conflictAnswer id res (← exhibit res.src j)
  throw s!"UnsupportedProfile: case kind {kind} is not available on the rights route"

def runCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  if !usesRightsPath j then return ← VE.SoftNorms.Run.runCase j
  runRightsKind id kind j

open VE.Order.ProfileGate (bind_ok) in
theorem rights_wire_acceptance (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hn : usesRightsPath j = true) :
    ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
      RightsAdmissionAnswer id (j.getObjValD "environment") (j.getObjValD "document") answer := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  obtain ⟨kind, hkind, h⟩ := bind_ok h
  have heq : kind = "admission" := by rw [hkind] at hk; cases hk; rfl
  subst kind
  simp [hn] at h
  unfold runRightsKind at h
  simp at h
  obtain ⟨environment, he, h⟩ := bind_ok h
  obtain ⟨document, hd, h⟩ := bind_ok h
  have he' : j.getObjValD "environment" = environment := by
    simp only [Json.getObjValD, he]; rfl
  have hd' : j.getObjValD "document" = document := by
    simp only [Json.getObjValD, hd]; rfl
  rw [he', hd']
  exact ⟨id, hid, runAdmission_sound id environment document answer (by simpa using h)⟩

def runCaseReported (j : Json) : Json :=
  if usesRightsPath j then
    match runCase j with
    | .ok result => result
    | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"),
        ("error", .str message)]
  else VE.SoftNorms.Run.runCaseReported j

end VE.Rights.Run
