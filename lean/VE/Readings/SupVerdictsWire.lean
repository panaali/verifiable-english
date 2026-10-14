import VE.Readings.SupDependencies
import VE.Readings.SupFillWire
import VE.Norms.WitnessKind

/-! RD-7. The superposed verdict service. Evidence is checked by the existing superposed wire
replays; this module owns the folds, dependency replay, candidate statuses and English selection. -/
namespace VE.Readings.Wire

def dedupChoices (xs : List Choice) : List Choice :=
  xs.foldl (fun acc c => if acc.contains c then acc else acc ++ [c]) []

end VE.Readings.Wire

namespace VE.Readings.Run
open Lean VE.Readings VE.Readings.Wire
open VE.Norms (envAt size targets)
open VE.SoftNorms (soften)
open VE.Rights (correlate)

structure SupBudget where
  maxSteps : Nat := 10000
  maxDomainSize : Nat := 2
  maxModels : Nat := 10000
  maxEvaluations : Nat := 100000

def SupBudget.json (b : SupBudget) : Json := Json.mkObj [
  ("max_steps", toJson b.maxSteps), ("max_domain_size", toJson b.maxDomainSize),
  ("max_models", toJson b.maxModels), ("max_evaluations", toJson b.maxEvaluations)]

structure SupContext where
  b : Admitted2
  nd : Option AdmittedNDFull

def SupContext.D (x : SupContext) : Doc :=
  match x.nd with | some f => fillDoc f.r.N | none => x.b.D
def SupContext.Q (x : SupContext) : VE.Compose.Labelled :=
  match x.nd with | some f => VE.NormDefaults.Admission.fillLabelled (supU f.r.N) | none => []
def SupContext.run (x : SupContext) (kind : String) (j : Json) : Except String Json :=
  match x.nd with
  | some f => runNDKind "readings-verdicts" kind f j
  | none =>
    if kind == "readings-conflict" then runConflict "readings-verdicts" x.b j
    else if kind == "readings-certificate" then runCertificate "readings-verdicts" x.b j
    else runModel "readings-verdicts" x.b j

def supRuleName (D : Doc) (name : String) : String :=
  (((List.range D.sets.length).flatMap (fun m => (D.sets[m]?).toList.flatMap (fun R =>
    (List.range R.candidates.length).flatMap (fun i => (R.candidates[i]?).toList.flatMap (fun a =>
      (candidateNames D m i a).filterMap (fun (original, qualified) => if qualified == name then
        some s!"{original} under {R.id}@{R.version}:{i}" else none)))))).head?).getD name

/-- A reported model must be locally conflict-free as well as satisfy the slot and assertions.
The finite conflict check is the same owner used by the enumerated route. -/
def supModelFree (D : Doc) (M : VE.FiniteModel VE.Bridge.Entity) : Bool :=
  VE.Readings.Wire.localFree ⟨soften (correlate (sup D).1), []⟩ M (fun _ => [])

def SupContext.modelFree (x : SupContext) (j : Json) : Bool :=
  match x.nd with
  | some f => match replayModelND f j with
    | .ok r => supModelFree (fillDoc r.f.r.N) r.M
    | .error _ => false
  | none => match replayModelOf x.b j with
    | .ok r => supModelFree r.D r.M
    | .error _ => false

structure SupWitnessNote where
  summary : String := ""
  classification : String := ""
  target : String := ""
  sorts : List String := []
  tuple : List String := []
  selected : Option (List (String × String)) := none

def supWitnessTexts (x : SupContext) (p answer : Json) : SupWitnessNote := Id.run do
  let w := p.getObjValD "witness"
  let name := strOf (w.getObjValD "target")
  let X := correlate (sup x.D).1
  let W := soften X
  let t := ((targets W).find? (·.1 == name)).getD (name, [], .bottom)
  let values := jstrings (w.getObjValD "tuple")
  let kind := VE.Norms.witnessKind t
  let summary := s!"CONFLICT: {kind} at {", ".intercalate values} under {choiceText x.D (jchoice (answer.getObjValD "choice"))}"
  let setting := ", ".intercalate ((t.2.1.zip values).map (fun (sort, id) => s!"{sort} {id}"))
  let model := match x.nd with
    | some f => do
      let r ← (supReplayND f).toOption
      let ⟨M, _⟩ ← (decodeSupModel r.f.fa.a.re (fillDoc r.f.r.N) r.hyps (filled_frame_E r.f) (w.getObjValD "model")).toOption
      pure M
    | none =>
      if hs : x.b.D.chain ≠ Chain.rights ∧ superposable x.b.D = true then do
        let ⟨M, _⟩ ← (decodeSupModel x.b.a.re x.b.D ⟨x.b.wf, hs.1, hs.2⟩
          (by rw [x.b.frame]; rfl) (w.getObjValD "model")).toOption
        pure M
      else none
  let selected := model.toList.flatMap (fun M => W.T.nodes.filterMap (fun N =>
    if N.pred == name && (VE.Norms.subst W.T (size W) (VE.Norms.selects W.T (VE.Norms.fuel W.T) N)).eval M
      (VE.Norms.tupleVal (t.2.1.zip values)) then
      let role := ((W.T.regulated.find? (·.name == name)).map (·.role)).getD .plain
      let verb := match role, N.sign with
        | .permission, true => "permits" | .permission, false => "forbids"
        | .obligation, true => "requires" | .obligation, false => "releases"
        | .plain, true => "affirms" | .plain, false => "denies"
      some (N.name, verb) else none))
  let rules := selected.map (fun (n, v) => s!"rule {supRuleName x.D n} {v}")
  return ⟨summary, s!"CONFLICT: {kind} at {setting}" ++
    (if rules.isEmpty then "" else ": " ++ "; ".intercalate rules), name, t.2.1, values,
    if W.T.regulated.any (·.name == name) then some selected else none⟩

structure SupScope where
  info : RowInfo
  encoded : List (String × Choice) := []
  used : List (String × List String) := []
  mentions : List (String × List String) := []
  witnessSummary : Option SupWitnessNote := none
  missing : Option String := none
  coherence : List (String × List String) := []

def SupScope.choice (s : SupScope) (piece : String) : Choice :=
  ((s.encoded.find? (·.1 == piece)).map (·.2)).getD s.info.choice
def SupScope.coh (s : SupScope) (piece : String) : List String :=
  ((s.coherence.find? (·.1 == piece)).map (·.2)).getD []
def SupScope.labels (s : SupScope) (piece : String) : List String :=
  ((s.used.find? (·.1 == piece)).map (·.2)).getD []

def supPieceCase (A : Choice) (Γ φ : Json) (e : Json) : Json :=
  e.setObjVal! "assumed" (choiceJson A) |>.setObjVal! "premises" Γ |>.setObjVal! "conclusion" φ

/-- Refused evidence is noted as refused, never turned into a negative verdict. -/
def supScope (x : SupContext) (A : Choice) (Γ φ : Json) (e : Json) : SupScope := Id.run do
  let mut notes : List PieceNote := []
  let mut encoded := []
  let mut used := []
  let mut mentions := []
  let mut coherence := []
  let mut free := false
  let mut conflict := false
  let mut proved := false
  let mut refuted := false
  let mut unsat := false
  let mut model := false
  let mut witnessSummary := none
  let packages := (pieceOf e "conflict").getD (Json.mkObj [])
  let certs := decodeConflictCerts x.D (packages.getObjValD "conflict_certificates")
  for name in ["conflict", "witness", "certificate", "countermodel", "unsat", "model"] do
    if let some p := pieceOf e name then
      let kind := if name == "conflict" || name == "witness" then "readings-conflict"
        else if name == "certificate" || name == "unsat" then "readings-certificate" else "readings-model"
      let body := if name == "certificate" || name == "unsat" then
        p.setObjVal! "conflict_certificates" (packages.getObjValD "conflict_certificates") else p
      let body := supPieceCase A (if name == "model" || name == "unsat" then .arr #[] else Γ)
        (if name == "model" || name == "unsat" then .null else φ) body
      match x.run kind body with
      | .error error => notes := notes ++ [{ name := name, accepted := false, error := some error }]
      | .ok answer =>
        let ok := if name == "conflict" then answer.getObjValD "verdict" == .str "CONFLICT-FREE"
          else if name == "witness" then answer.getObjValD "verdict" == .str "CONFLICT"
          else if name == "certificate" || name == "unsat" then answer.getObjValD "accepted" == .bool true
          else answer.getObjValD "valid" == .bool true && answer.getObjValD "conclusion_value" == .bool false &&
            x.modelFree body
        let shown := if ok && (name == "witness" || name == "countermodel" || name == "model") then
          some (if name == "witness" then (p.getObjValD "witness").getObjValD "model" else p.getObjValD "model")
          else none
        let proof := if name == "certificate" || name == "unsat" then do
          let cert ← (VE.CertificateWire.decodeCertificate (p.getObjValD "certificate")).toOption
          let ⟨(gs, f), _, _⟩ ← (decodeShared x.D (body.getObjValD "premises") (body.getObjValD "conclusion")).toOption
          pure (gs, f, cert)
          else none
        let labels := if ok && (name == "conflict" || name == "certificate" || name == "unsat") then
          supDependencies x.D A x.Q certs proof
          else []
        let coh := if ok then supCoherence x.D (supProofs x.D certs proof) else []
        coherence := coherence ++ [(name, coh)]
        used := used ++ [(name, labels)]
        mentions := mentions ++ [(name, supMentions x.D A x.Q labels)]
        let texts := if name == "witness" && ok then some (supWitnessTexts x p answer) else none
        if let some t := texts then witnessSummary := some t
        notes := notes ++ [⟨name, ok, none, shown, jgaps (answer.getObjValD "gaps"), labels, texts.map (·.classification)⟩]
        if shown.isSome then encoded := encoded ++ [(name, jchoice (answer.getObjValD "choice"))]
        if name == "conflict" then free := ok
        if name == "witness" then conflict := ok
        if name == "certificate" then proved := ok
        if name == "countermodel" then refuted := ok
        if name == "unsat" then unsat := ok
        if name == "model" then model := ok
  let X := correlate (sup x.D).1
  let missing := ((targets (soften X)).zip certs).find? (fun (t, c) =>
    !(c.map (VE.Tableau.checkCertificate (envAt (soften X) 0)
      (VE.Compose.backgroundBaseP X (slotUnder x.D A ++ x.Q.formulas))
      (VE.Norms.targetConclusion t))).getD false)
  return ⟨⟨A, if free then .free else if conflict then .conflict else .unknown,
    if proved then .proved else if refuted then .refuted else .unknown,
    if unsat then .inconsistent else if model then .model else .unknown, notes⟩, encoded, used, mentions, witnessSummary, missing.map (·.1.1), coherence⟩

def supEvidence (j : Json) (A : Choice) : Json :=
  ((evidenceList j).find? (fun e => jchoice (e.getObjValD "choice") == A)).getD (Json.mkObj [])

/-- Global scope first, then complete choices (at most 64), then live candidates for premise checks.
Lean alone enumerates and applies the budget. -/
def supScopes (D : Doc) (question : String) (A : Choice) : List Choice :=
  let cs := chosenOf D A
  VE.Readings.Wire.dedupChoices ([A] ++ (if (choices D).length ≤ maxChoices then cs else []) ++
    (if question == "premises" then (candidatesOf D).filterMap (fun (R, i) =>
      if (droppedBy D R i).isNone && takenBy D [(R.id, i)] then some [(R.id, i)] else none) else []))

def supScopeJson (q : String) (s : SupScope) : Json :=
  Json.mkObj [("row", perChoiceJson q s.info),
    ("encoded", Json.mkObj (s.encoded.map (fun (k, c) => (k, choiceJson c)))),
    ("used", Json.mkObj (s.used.map (fun (k, ls) => (k, toJson ls)))),
    ("mentions", Json.mkObj (s.mentions.map (fun (k, ls) => (k, toJson ls))))]

def supFind (ss : List SupScope) (A : Choice) : SupScope :=
  (ss.find? (·.info.choice == A)).getD { info := ⟨A, .unknown, .unknown, .unknown, []⟩ }
def supProofJson (s : SupScope) : Json := Json.mkObj [
  ("choice", choiceJson s.info.choice), ("conditional_on", toJson (s.coh "certificate" ++ s.labels "certificate")),
  ("reading_premises_used", toJson (s.labels "certificate"))]
def supModelJson (s : SupScope) (p : String) : Json := Json.mkObj [
  ("choice", choiceJson (s.choice p)), ("model", s.info.shown p),
  ("gaps", gapsJson (((s.info.note p).map (·.gaps)).getD []))]

def supCandidateJson (D : Doc) (ss : List SupScope) (dead : List (String × Nat)) : List Json :=
  (candidatesOf D).map (fun (R, i) => Json.mkObj ([("set", .str R.id), ("index", toJson i)] ++
    match droppedBy D R i with
    | some n => [("status", .str "narrowed"), ("narrowing", .str n)]
    | none =>
      if dead.contains (R.id, i) then [("status", .str "dead")]
      else if !takenBy D [(R.id, i)] then [("status", .str "UNKNOWN"), ("reason", .str (untakenText D [(R.id, i)]))]
      else
        let s := supFind ss [(R.id, i)]
        if s.info.premise == .model then [("status", .str "model"), ("choice", choiceJson (s.choice "model"))]
        else [("status", .str (if s.info.premise == .inconsistent then "INCONSISTENT" else "UNKNOWN"))]))

def supResult (D : Doc) (Q : VE.Compose.Labelled) (nd : Bool) (q : String) (A : Choice) (named : Option Choice)
    (ss : List SupScope) (dead : List (String × Nat)) (budget : SupBudget) : Json := Id.run do
  let s := supFind ss A
  let mut fs : List (String × Json) := [("route", .str "superposed")]
  if q == "conflict" then
    fs := fs ++ [("status", .str (word s.info.conflict)), ("assumed", choiceJson A)]
    if s.info.conflict == .free then
      fs := fs ++ [("evidence", .str "certificates"), ("conditional_on", toJson (s.coh "conflict" ++ s.labels "conflict")),
        ("reading_premises_used", toJson (s.labels "conflict")),
        ("status_text", .str (s!"CONFLICT-FREE among rules on the same act, conditional on {(s.coh "conflict").length} coherence premises" ++
          (if (s.labels "conflict").isEmpty then "" else s!" and {(s.labels "conflict").length} reading premises")))]
    else if s.info.conflict == .conflict then
      fs := fs ++ [("evidence", .str "witness"),
        ("target", .str ((s.witnessSummary.map (·.target)).getD "")),
        ("sorts", toJson ((s.witnessSummary.map (·.sorts)).getD [])),
        ("tuple", toJson ((s.witnessSummary.map (·.tuple)).getD [])),
        ("selected", match s.witnessSummary.bind (·.selected) with
          | some pairs => Json.arr (pairs.map (fun (n, v) => Json.arr #[.str n, .str v])).toArray
          | none => .null),
        ("choice", choiceJson (s.choice "witness")),
        ("model", s.info.shown "witness"), ("gaps", gapsJson (((s.info.note "witness").map (·.gaps)).getD [])),
        ("status_text", .str ((s.witnessSummary.map (·.summary)).getD "CONFLICT"))]
    else fs := fs ++ [("detail", .str s!"tableau budget or open branch: {s.missing.getD "target unspecified"}"),
      ("status_text", .str s!"UNKNOWN: tableau budget or open branch: {s.missing.getD "target unspecified"}, budget {budget.maxSteps}"),
      ("budget", budget.json)]
    if nd && A.isEmpty && (choices D).length ≤ maxChoices then
      fs := fs ++ [("choices", Json.arr ((choices D).map (fun c => Json.mkObj [
        ("choice", choiceJson c), ("status", .str (word (if s.info.conflict == .free then ChoiceResult.free else (supFind ss c).info.conflict)))])).toArray)]
  else if q == "premises" then
    fs := fs ++ [("status", .str (word s.info.premise)),
      ("candidates", Json.arr (supCandidateJson D ss dead).toArray)]
    if s.info.premise == .model then fs := fs ++ [("evidence", .str "model"),
      ("choice", choiceJson (s.choice "model")), ("model", s.info.shown "model"),
      ("gaps", gapsJson (((s.info.note "model").map (·.gaps)).getD []))]
    else if s.info.premise == .inconsistent then fs := fs ++ [("evidence", .str "certificate"),
      ("conditional_on", toJson (s.coh "unsat" ++ s.labels "unsat")), ("reading_premises_used", toJson (s.labels "unsat"))]
    else fs := fs ++ [("budget", budget.json)] ++ (if s.info.conflict != .free then
      [("reason", .str s!"conflict status: {word s.info.conflict}")] else [])
  else
    fs := fs ++ assumedFields named
    if s.info.conflict != .free then
      fs := fs ++ [("verdict", .str "UNKNOWN"), ("status", .str s!"UNKNOWN (conflict status: {word s.info.conflict})"),
        ("conflict_status", .str (word s.info.conflict))] ++
        (if nd && s.info.conflict == .conflict then [("choice", choiceJson (s.choice "witness"))] else [])
    else if s.info.query == .proved then
      fs := fs ++ [("verdict", .str "ALL"), ("evidence", .str "certificate"),
        ("conditional_on", toJson (s.coh "certificate" ++ s.labels "certificate")), ("reading_premises_used", toJson (s.labels "certificate")),
        ("mentions", toJson (((s.mentions.find? (·.1 == "certificate")).map (·.2)).getD []))] ++
        (if named.isNone then [("assumed", choiceJson A)] else [])
    else if named.isSome && !nd then
      fs := fs ++ (if s.info.query == .refuted then [("verdict", .str "NOT ALL"),
        ("countermodel", supModelJson s "countermodel")] else [("verdict", .str "UNKNOWN"), ("budget", budget.json)])
    else if (choices D).length > maxChoices then
      fs := fs ++ [("verdict", .str "UNKNOWN"), ("budget", Json.mkObj [("max_choices", toJson maxChoices)])] ++
        (if s.info.query == .refuted then [("status", .str s!"UNKNOWN (not ALL: countermodel under {choiceText D (s.choice "countermodel")})"),
          ("countermodel", supModelJson s "countermodel")] else [])
    else
      let taking := (chosenOf D A).map (supFind ss)
      let proofs := taking.filter (·.info.query == .proved)
      let counters := taking.filter (·.info.query == .refuted)
      let rs := taking.map (fun s => (s.info.choice, s.info.query))
      -- The global conflict certificate supplies the gate for each covered choice.
      let cs := taking.map (fun s => (s.info.choice, ChoiceResult.free))
      match foldEntailment cs rs with
      | .some => fs := fs ++ [("verdict", .str "SOME"), ("proof", supProofJson (proofs.head?.getD s)),
          ("countermodel", supModelJson (counters.head?.getD s) "countermodel")]
      | .none => fs := fs ++ [("verdict", .str "NONE"),
          ("countermodels", Json.arr (counters.map (supModelJson · "countermodel")).toArray),
          ("restrictions", toJson (restrictionsFor D A))]
      | .all =>
        let allUsed := proofs.flatMap (·.labels "certificate") ++ restrictionsFor D A
        let slotNames := (slotLabelled D ++ Q).map (·.1)
        let ls := slotNames.filter allUsed.contains ++ (restrictionsFor D A).filter (fun l => !slotNames.contains l)
        let conditional := dedupStrings (proofs.flatMap (fun p => p.coh "certificate" ++ p.labels "certificate") ++ restrictionsFor D A)
        fs := fs ++ [("verdict", .str "ALL"), ("evidence", .str "certificates"),
          ("proofs", Json.arr (proofs.map supProofJson).toArray), ("conditional_on", toJson conditional),
          ("reading_premises_used", toJson ls), ("restrictions", toJson (restrictionsFor D A))]
      | .unknown =>
        fs := fs ++ [("verdict", .str "UNKNOWN"), ("budget", budget.json)] ++
          (match taking.find? (·.info.query == .unknown) with
            | some t => [("choice", choiceJson t.info.choice)] | none => [])
  return Json.mkObj fs

/-- Wordings for slot labels are selected structurally from their producer, never by name-prefix heuristics. -/
def supProvided (D : Doc) (Q : VE.Compose.Labelled) (ls : List String) : List PlanItem :=
  let ones := (onePremises D).filter (fun x => ls.contains x.1)
  let quiet := (quietOwn D ++ quietShared D).any (fun x => ls.contains x.1)
  let lines := ls.flatMap (fun l =>
    if ones.any (·.1 == l) then
      D.sets.filterMap (fun R => if l == "readings:" ++ label R ++ ":one" then
        some (.text "E4" none [(R.id, 0)] (some l)) else none)
    else if (quietOwn D ++ quietShared D).any (·.1 == l) then []
    else if Q.any (·.1 == l) then [.text "P1" none [] (some l)]
    else conditionItems D l)
  let lines := lines ++ if quiet then [.text "E9" none [] none] else []
  if lines.isEmpty then [] else .text "E3" none [] none :: lines

def supIndependent (D : Doc) (A : Choice) (ls : List String) : List PlanItem :=
  -- E13 is about the named conditions, as on the enumerated route. The
  -- certificate's slot bits are internal evidence, not a named condition.
  (D.sets.filter (fun R => !A.any (·.1 == R.id) && !(mentioned D ls).contains R.id)).map
    (fun R => .text "E13" none [(R.id, 0)] none)

def supShown (ss : List SupScope) (A : Choice) (p r : String) : List PlanItem :=
  match ss.findIdx? (·.info.choice == A) with
  | some k => let s := supFind ss A
    if (s.info.note p).bind (·.shown) |>.isSome then
      [.shown r (s.choice p) s!"{p}@{k}" (((s.info.note p).map (·.gaps)).getD [])] ++
        (if p == "witness" then ((s.info.note p).bind (·.statusText)).toList.map
          (fun t => .text "status" none [] (some t)) else []) else []
  | none => []

def supPlan (D : Doc) (Q : VE.Compose.Labelled) (q : String) (A : Choice) (ss : List SupScope)
    (dead : List (String × Nat)) (res : Json) : List Line :=
  let s := supFind ss A
  let every := if D.sets.length == 1 then "E26" else "E10"
  let provided := supProvided D Q
  let items := if q == "conflict" then
      if s.info.conflict == .free then [.text every (some "R1") [] none] ++ provided (s.labels "conflict") ++
        supIndependent D A (s.labels "conflict")
      else supShown ss A "witness" "R4"
    else if q == "premises" then
      (if s.info.premise == .model then supShown ss A "model" "R5"
       else if s.info.premise == .inconsistent then [.text every (some "R6") [] none] ++
         provided (s.labels "unsat") ++ supIndependent D A (s.labels "unsat") else []) ++
      dead.map (fun (id, i) => .text "E17" none [(id, i)] none)
    else
      let v := strOf (res.getObjValD "verdict")
      if v == "ALL" then
        (if A.isEmpty then [.text every (some "R2") [] none] else [.text "E12" (some "R2") A none]) ++
        provided (jstrings (res.getObjValD "reading_premises_used")) ++
        (if strOf (res.getObjValD "evidence") == "certificate" then supIndependent D A (s.labels "certificate") else [])
      else if v == "SOME" then
        let p := jchoice ((res.getObjValD "proof").getObjValD "choice")
        let c := jchoice ((res.getObjValD "countermodel").getObjValD "choice")
        [.text "E12" (some "R2") p none] ++ provided ((supFind ss p).labels "certificate") ++
          supShown ss c "countermodel" "R3"
      else if v == "NONE" then
        (if D.sets.length ≥ 2 && A.isEmpty then [.text "E27" none [] none] else []) ++
          (chosenOf D A).flatMap (fun c => supShown ss c "countermodel" "R3") ++ provided (restrictionsFor D A)
      else if v == "NOT ALL" then supShown ss A "countermodel" "R3"
      else if !isNull (res.getObjValD "countermodel") && A.isEmpty then
        .text "E28" none [] none :: supShown ss A "countermodel" "R3"
      else []
  items.map (PlanItem.line D)

def supUnchecked (q reason : String) (named : Option Choice) : Json :=
  Json.mkObj ([("route", .str "superposed"),
    (if q == "query" then "verdict" else "status", .str "UNKNOWN"), ("reason", .str reason)] ++
    (if q == "query" then assumedFields named else []) ++
    (if q == "conflict" then [("status_text", .str ("UNKNOWN: " ++ reason))] else []))

/-- Bounded, native choices for the untrusted smaller-vocabulary model generator. -/
def maxSupModelProposals : Nat := 16

def supAnswer (id q : String) (x : SupContext) (A : Choice) (named : Option Choice)
    (ss : List SupScope) (dead : List Json) (budget : SupBudget) (over : Bool) : Json :=
  let infos := if (choices x.D).length ≤ maxChoices then (choices x.D).map (fun c => (supFind ss c).info) else []
  let ds := deadOf x.D infos dead
  let res := if over then supUnchecked q checkBudgetText named
    else supResult x.D x.Q x.nd.isSome q A named ss (ds.1.getD []) budget
  okWith id [("route", .str "superposed"), ("question", .str q), ("result", res),
    ("scopes", Json.arr (ss.map (supScopeJson q)).toArray),
    ("model_proposals", Json.arr ((if over then [] else
      ((checkedChoices x.D).filter (fun c => A.all (c.contains ·))).take maxSupModelProposals).map choiceJson).toArray),
    ("restrictions", toJson (restrictionsFor x.D A)),
    ("dead_readings", if q == "premises" && (choices x.D).length ≤ maxChoices then deadReadingsJson ds.1 else .null),
    ("untaken", untakenJson (if q == "premises" && (choices x.D).length ≤ maxChoices then untakenOf x.D infos else [])),
    ("dead", Json.arr (if q == "premises" then ds.2 else []).toArray),
    ("english", Json.arr ((supPlan x.D x.Q q A ss (if q == "premises" then ds.1.getD [] else []) res).map Line.json).toArray)]

def runSupVerdicts (id : String) (b : Admitted2) (j : Json) : Except String Json := do
  let q ← VE.Bridge.stringField j "question"
  unless verdictsQuestions.contains q do throw s!"InvalidInput: unknown readings-verdicts question {q}"
  let nd ← if underCompletion b.a.re b.D then do
    pure (some (← admitNDFull b)) else pure none
  let x : SupContext := ⟨b, nd⟩
  let refusal := match nd with
    | some f => routeRefusalND f.r.b.a.re f.r.N
    | none => routeRefusal false b.D
  if let some e := refusal then
    unless (choices x.D).length > maxChoiceChecks do throw e
  let ⟨A, _⟩ ← decodeAssumed x.D (j.getObjValD "assumed")
  unless takenBy x.D A do throw (untakenText x.D A)
  let named := if (j.getObjVal? "assumed").toBool && !isNull (j.getObjValD "assumed") then some A else none
  let Γ := if q == "query" then j.getObjValD "premises" else .arr #[]
  let φ := if q == "query" then j.getObjValD "conclusion" else .null
  let _ ← decodeShared x.D Γ φ
  let scopes := supScopes x.D q A
  let ss := scopes.map (fun c => supScope x c Γ φ (supEvidence j c))
  let dead := match j.getObjValD "dead" with | .arr xs => xs.toList | _ => []
  let budget ← match j.getObjValD "budget" with
    | .null => pure (SupBudget.mk 10000 2 10000 100000)
    | data => do
      let read := fun key => match (data.getObjValD key).getNat? with
        | .ok n => pure n | .error _ => throw s!"InvalidInput: invalid search budget {key}"
      pure (SupBudget.mk (← read "max_steps") (← read "max_domain_size")
        (← read "max_models") (← read "max_evaluations"))
  let over := (checkedChoices x.D).length > maxChoiceChecks
  pure (supAnswer id q x A named ss dead budget over)

end VE.Readings.Run
