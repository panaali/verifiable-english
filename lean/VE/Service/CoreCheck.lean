import VE.Service.CoreDocument
import VE.Kernel.DocumentFold
import VE.SoftNorms.SlotSound
import VE.Route.CodecRoundTrip
import VE.Calc.Ties

/-! The document mode on the core document (kb-2a-b; the architect seat's design for kb-2a, sections 2.2 to 2.6).

A document that today ends in the refusal "judgments@0 with soft-norms@0" (an exception condition beside a judgment
term) or "soft-norms with readings" (`readings@1`, no alternatives or risk), and whose profiles all have a row of the
lowering, is read here (`routed`): `Document.decode` with `core`, then `CoreDocument.lower`, one core document `(X, P)`
per compatible choice of readings. Each is sent to the soft route's kernel runner as a `slot-admission` case (`caseOf`:
its environment and norm objects as the lowering made them, its premises encoded by the route's own formula encoder),
and the answer is `VE.Kernel.DocumentFold.fold` of the kernel's rows (`VE.Kernel.shell`): today's fields with each
unit's status from the fold, each unit's core statements per choice, and the rows verbatim. One refused row: the
document is refused with that row's diagnostic and the choice. Nothing here is trusted (`document_core_sound`). -/

namespace VE.Service.CoreCheck
open Lean
open VE.Discourse (FrontSet)
open VE.Service.Document
open VE.Service.CoreDocument
open VE.Kernel
open VE.Kernel.DocumentFold (UnitRow Stmt fold)
open VE.Compose.SlotWire (SlotAdmission replaySlotAdmission SlotAdmitted decodeFacts)
open VE.Kit.Except (bind_ok)

/-! ## The kernel path -/

/-- What an accepted `slot-admission` row means (`VE.SoftNorms.Run.slot_wire_admission`). -/
def AdmissionMeaning (case answer : Json) : Prop :=
  VE.Route.Run.caseKind case = .ok "slot-admission" → VE.SoftNorms.Run.usesSoftPath case = true →
    ∃ (id : String) (r : SlotAdmission), VE.Bridge.stringField case "id" = .ok id ∧
      replaySlotAdmission case = .ok r ∧ SlotAdmitted case r ∧ answer = VE.SoftNorms.Run.slotAdmissionAnswer id r

/-- The softNorms kernel path: its runner, and `slot_wire_admission` as what its rows mean. -/
def softNormsPath : Path where
  run := VE.SoftNorms.Run.runCase
  Meaning := AdmissionMeaning
  sound := fun case answer h hk hn => by
    obtain ⟨id, r, hid, _, hr, hs, hw, hE, hl, hd, hP, ha⟩ :=
      VE.SoftNorms.Run.slot_wire_admission case answer h hk hn
    exact ⟨id, r, hid, hr, ⟨hs, hw, hE, hl, hd, hP⟩, ha⟩

/-! ## Cases -/

/-- The premises as the route's formula encoder writes them. -/
def factsJson (P : List VE.Formula) : Json := Json.arr (P.map VE.Route.Wire.encodeFormula).toArray

/-- The case of choice `i`: its core document as the lowering made it, sent unchanged, with its premises. -/
def caseOf (i : Nat) (d : CoreDoc) : Json :=
  Json.mkObj [("id", .str s!"choice-{i}"), ("kind", .str "slot-admission"), ("environment", d.environment),
    ("norms", d.norms), ("facts", factsJson d.premises)]

/-- The four hypotheses of the encoder's inverse (`decodeFormulas_encode`: typing, depth, nodes; the data flag is off
for facts) over the source's base vocabulary, and `decodeFacts`'s own: no soft decision predicate. -/
def roundTrips (src : VE.SoftNorms.Wire.SoftSource) (P : List VE.Formula) : Bool :=
  P.all (·.check (VE.Norms.envAt (VE.SoftNorms.soften src.D) 0) []) &&
    P.all (fun φ => decide (VE.Surface.formulaDepth φ < VE.Limits.maxDepth)) &&
    decide ((P.map VE.Bridge.formulaNodes).foldl (· + ·) 0 ≤ VE.Limits.maxNodes) &&
    (P.flatMap VE.Norms.preds).all (!(VE.SoftNorms.decisionNames src.D).contains ·)

/-- The refusal of premises that would not read back: the decoder's own diagnostic. -/
def factsRefusal (src : VE.SoftNorms.Wire.SoftSource) (P : List VE.Formula) : String :=
  match decodeFacts src (Json.mkObj [("facts", factsJson P)]) with
  | .error e => e
  | .ok _ => "UnsupportedLowering: facts: the premises do not read back"

/-- A core document whose premises would not read back as themselves. A source the soft decoder refuses is the
kernel's to refuse, in its row. -/
def caseFault (d : CoreDoc) : Option String :=
  match VE.SoftNorms.Wire.decodeSoftSource d.environment d.norms with
  | .error _ => none
  | .ok src => if roundTrips src d.premises then none else some (factsRefusal src d.premises)

/-- One case per core document from choice `i` on, in the lowering's order. -/
def casesFrom : Nat → List (Choice × CoreDoc) → Except String (List Json)
  | _, [] => .ok []
  | i, d :: ds => match caseFault d.2 with
    | some e => .error s!"{e} (core document of choice {i})"
    | none => (casesFrom (i + 1) ds).map (caseOf i d.2 :: ·)

def casesOf (docs : List (Choice × CoreDoc)) : Except String (List Json) := casesFrom 0 docs

/-! ## The request's table and the view -/

/-- What the shell reads before the lowering: `Document.decode`'s values and the steps of `check` that refuse. -/
structure Inputs where
  id : String
  d : Decoded
  documentId : String
  active : List (FrontSet × List Bool)
  views : List VE.Judgments.UnitView
  sets : List ActiveSet
  meanings : List String
  rows : List RowUnit
  block : Option BlockCoverage

/-- A feature the lowering has no row for and cannot see in its inputs: refused, never lowered as if absent. -/
def unsupportedFeature (front : Json) (units : List SourceUnit) : Option String :=
  (["couplings", "narrowings", "graph", "completions"].find? fun k => (front.getObjVal? k).isOk).map fun k =>
    unsupported ((units.head?.map (·.id)).getD "") k "the table has no row for it"

def inputs (j : Json) : Except String Inputs := do
  let id ← VE.Bridge.stringField j "id"
  let text ← VE.Bridge.stringField j "document"
  let d ← decode text (j.getObjVal? "lexicon").toOption (j.getObjVal? "packs").toOption none none
    (j.getObjVal? "chain_of").toOption (core := true)
  if let some e := unsupportedFeature d.front d.units then throw e
  let active := VE.Discourse.Loader.activeOf d.all
  let rules := (d.S.bind (·.rules)) <|> (d.R.bind (·.rules))
  let views ← if d.judged then judgedViews d.E d.front d.names active d.units rules d.R else pure []
  let sets ← active.mapM fun (s, _) => return (s, ← setCandidates d.E d.front s)
  VE.Discourse.Loader.checkLemmas d.front
  for u in d.units do
    if u.kind == .str "asserted" && u.content.isNone && !(d.all.any (·.1.unit == u.id)) then
      throw "asserted unit needs content or a reading set"
  VE.Discourse.Loader.checkWeights d.front
  let meanings ← d.units.mapM fun u => VE.Discourse.Loader.meaningStatus d.openNames u.meaning (python := true)
  pure ⟨id, d, ← documentId d.doc, active, views, sets, meanings, ← d.units.mapM rowOf,
    ← blockCoverage d.E d.front d.units⟩

/-- A soft rule's exception conditions (`sufficient`, `necessary`), which the soft theory reads and the judgment
reader's `softContent` does not (pc-1 review F1): a statement whose exception reads a judgment term reads it. -/
def exceptionFormulas (S : Option VE.SoftNorms.Wire.SoftEnvironment) : Option UnitContent → List VE.Formula
  | some (.soft rule) => match S with
    | some se =>
      let N := (VE.SoftNorms.Wire.decodeSoftNorm se rule).toOption <|>
        (VE.SoftNorms.Wire.decodeSoftNorm se (Json.mkObj [("norm", rule.getObjValD "norm")])).toOption
      ((N.bind (·.exception)).map fun e => e.sufficient ++ e.necessary).getD []
    | none => []
  | _ => []

/-- The judgment terms a statement reads (directly or through a definition): its unit's own content, with a soft
rule's exception conditions, or the candidate of the reading it comes from; a judgment declaration reads none. -/
def reads (I : Inputs) (u : SourceUnit) (st : Statement) : List String :=
  let rules := (I.d.S.bind (·.rules)) <|> (I.d.R.bind (·.rules))
  let formulas : List VE.Formula := match st.body, st.origin.reading with
    | .judgment _, _ => []
    | _, some (s, i) => (((I.sets.find? (·.1.id == s)).bind fun x => x.2[i]?).join.map (·.formulas)).getD []
    | _, none => ((u.content.bind fun c => (c.judgedIn rules I.d.R).toOption).join.map (·.formulas)).getD [] ++
        exceptionFormulas rules u.content
  VE.Judgments.dependsOn I.d.E.rv.definitions I.d.J formulas

/-- The unit table of the fold: each unit's meaning class, its core statements over every choice with what they
read, its active set's flag and the rights route's opening. -/
def tableOf (I : Inputs) (docs : List (Choice × CoreDoc)) : List UnitRow :=
  (I.d.units.zip I.meanings).map fun (u, m) =>
    { id := u.id, meaning := m,
      statements := docs.flatMap fun (_, c) => (c.statements.filter fun (st : Statement) => st.origin.unit == u.id).map fun st => ⟨reads I u st⟩,
      set := (I.active.find? (·.1.unit == u.id)).map fun (rs, kinds) => rs.status == "authored" && kinds.all id,
      rightsOpen := (I.d.R.bind fun R => R.opens.lookup u.id) == some true }

def statementJson (st : Statement) : Json :=
  Json.mkObj ([("feature", .str st.origin.feature)] ++
    (st.origin.reading.toList.map fun (s, i) => ("reading", Json.mkObj [("set", .str s), ("index", toJson i)])) ++
    [match st.body with
      | .soft r => ("rule", r)
      | .premise φ => ("premise", VE.Route.Wire.encodeFormula φ)
      | .judgment t => ("judgment", .str t.name)])

/-- Each unit's core statements, choice by choice, for the units that have one. -/
def statementsJson (units : List SourceUnit) (docs : List (Choice × CoreDoc)) : Json :=
  Json.arr (units.filterMap fun u =>
    let per := docs.map fun (_, c) => c.statements.filter fun (st : Statement) => st.origin.unit == u.id
    if per.all (·.isEmpty) then none else
      some (Json.mkObj [("id", .str u.id),
        ("choices", Json.arr (per.map fun sts => Json.arr (sts.map statementJson).toArray).toArray)])).toArray

def choicesJson (docs : List (Choice × CoreDoc)) : Json :=
  Json.arr (docs.map fun (c, _) =>
    Json.arr (c.map fun (s, i) => Json.mkObj [("set", .str s), ("reading", toJson i)]).toArray).toArray

/-- The answer's name of a status of the fold. -/
def unitStatus : DocumentFold.Status → UnitStatus
  | .checked => .checked
  | .opened => .opened
  | .labelled => .labelled
  | .unformalised => .unformalised

/-- The view: today's answer fields over the fold's statuses (`Document.encode`), each unit's core statements per
choice, and the choices. It reads the statuses it is given and decides none. -/
def viewOf (I : Inputs) (docs : List (Choice × CoreDoc)) (statuses : List (String × DocumentFold.Status)) : Json :=
  let status := fun (id : String) (own : UnitStatus) => ((statuses.lookup id).map unitStatus).getD own
  let units := I.d.units.map fun u =>
    { u with status := ((statuses.lookup u.id).map fun s => (unitStatus s).name).getD u.status }
  let rows := I.rows.map fun r => { r with status := status r.id r.status }
  let J := I.d.records.map (·.1)
  let c : Checked := ⟨I.documentId, VE.Discourse.Loader.sourceIdOf I.d.E.version I.d.doc.source, I.d.doc.source, units, rows, I.d.front,
    I.block, if I.d.judged then some (VE.Judgments.usageMap I.d.E.rv.definitions I.d.J I.views) else none,
    (J, if I.d.judged then statusRows I.d.E.rv.definitions J I.views else []),
    if I.d.judged then VE.Judgments.undeclaredEvaluative VE.EnglishGrammar.evaluativeRows I.d.E.basePredicates I.d.J
    else [], none, none, I.active, none⟩
  Json.mkObj (encodeFields c ++ [("choices", choicesJson docs), ("statements", statementsJson I.d.units docs)])

/-! ## The answer -/

structure Prepared where
  I : Inputs
  docs : List (Choice × CoreDoc)
  cases : List Json

def prepare (j : Json) : Except String Prepared := do
  let I ← inputs j
  let docs ← lower I.d.E I.d.senses I.d.records I.views I.d.units I.sets []
  let cases ← casesOf docs
  pure ⟨I, docs, cases⟩

/-- The first refused row from index `i` on: its index and diagnostic. -/
def firstRefused : List Row → Nat → Option (Nat × String)
  | [], _ => none
  | r :: rs, i => match r.result with
    | .error e => some (i, e)
    | .ok _ => firstRefused rs (i + 1)

/-- A refused row's diagnostic, naming its choice. -/
def refusal (docs : List (Choice × CoreDoc)) (i : Nat) (e : String) : String :=
  s!"{e} (core document of choice {i}: {((docs[i]?.map (·.1)).getD []).map fun (s, k) => s!"{s} reading {k}"})"

/-- A unit whose authored status is not the fold's. -/
def contradicted (I : Inputs) (statuses : List (String × DocumentFold.Status)) : Bool :=
  I.d.units.any fun u => u.explicit.any (some · != (statuses.lookup u.id).map fun s => (unitStatus s).name)

def answer (j : Json) : Except String Json := do
  let p ← prepare j
  let a ← shell softNormsPath (fun _ => .ok p.cases) (fold (viewOf p.I p.docs) (tableOf p.I p.docs)) j
  match firstRefused (p.cases.map softNormsPath.row) 0 with
  | some (i, e) => throw (refusal p.docs i e)
  | none =>
    if contradicted p.I (DocumentFold.statuses (tableOf p.I p.docs) (p.cases.map softNormsPath.row)) then
      throw "unit status contradicts content, meaning, or active reading set"
    else pure (VE.Route.Wire.ok p.I.id [("view", a.getObjValD "view"), ("rows", a.getObjValD "rows")])

/-! ## Routing -/

/-- The two refusals the core path replaces (`Document.environmentOf`). -/
def routedRefusals : List String :=
  [unavailable "judgments@0 with soft-norms@0 needs its composed Lean route",
   unavailable "soft-norms with readings, alternatives or risk needs its composed Lean route"]

/-- A document the core path reads: one that `environmentOf` refuses with one of the two refusals, whose profiles all
have a row of the lowering, and that has no senses. -/
def routed (j : Json) : Bool :=
  match frontOf j with
  | none => false
  | some (front, _) =>
    let env := front.getObjValD "environment"
    !(front.getObjVal? "senses").isOk && (listedProfiles env).all rowProfiles.contains &&
      match environmentOf env (front.getObjValD "units") false (some (VE.Discourse.Loader.optionalList front "open_terms")) with
      | .error e => routedRefusals.contains e
      | .ok _ => false

/-- The document mode's entry: a routed document is answered here or refused here, its refusal row marked
`lowering` (so no other path decides it); every other case is `Document.runCaseReported`'s, unchanged. -/
def runCaseReported (j : Json) : Json :=
  if routed j then
    match answer j with
    | .ok a => a
    | .error message =>
      let row := match locatedOf j message with
        | some (text, at_) => locatedRow j text at_
        | none => Standalone.reported (fun _ => .error message) j
      row.setObjVal! "lowering" (.bool true)
  else Document.runCaseReported j

/-! ## Theorems -/

theorem casesFrom_ok : ∀ (docs : List (Choice × CoreDoc)) (i : Nat) (cases : List Json),
    casesFrom i docs = .ok cases → cases.length = docs.length ∧
      ∀ k (hk : k < docs.length), cases[k]? = some (caseOf (i + k) docs[k].2) ∧ caseFault docs[k].2 = none
  | [], _, cases, h => by
    simp only [casesFrom, Except.ok.injEq] at h
    subst h
    exact ⟨rfl, fun k hk => absurd hk (Nat.not_lt_zero k)⟩
  | d :: ds, i, cases, h => by
    unfold casesFrom at h
    split at h
    · cases h
    · rename_i hf
      cases hr : casesFrom (i + 1) ds with
      | error e => rw [hr] at h; cases h
      | ok rest =>
        rw [hr] at h
        simp only [Except.map, Except.ok.injEq] at h
        subst h
        obtain ⟨hl, hk⟩ := casesFrom_ok ds (i + 1) rest hr
        refine ⟨by simp [hl], fun k hk' => ?_⟩
        cases k with
        | zero => exact ⟨by simp, hf⟩
        | succ k =>
          obtain ⟨h1, h2⟩ := hk k (by simpa using hk')
          exact ⟨by simpa [Nat.add_assoc, Nat.add_comm 1 k] using h1, by simpa using h2⟩

/-- The rows are the lowering's list: one case per core document, in its order, each the core document of its choice;
the shell found no premise that would not read back. -/
theorem casesOf_ok {docs : List (Choice × CoreDoc)} {cases : List Json} (h : casesOf docs = .ok cases) :
    cases.length = docs.length ∧
      ∀ k (hk : k < docs.length), cases[k]? = some (caseOf k docs[k].2) ∧ caseFault docs[k].2 = none := by
  obtain ⟨hl, hk⟩ := casesFrom_ok docs 0 cases h
  exact ⟨hl, fun k h' => by simpa using hk k h'⟩

theorem firstRefused_none : ∀ (rows : List Row) (i : Nat), firstRefused rows i = none →
    ∀ r ∈ rows, ∃ x, r.result = .ok x
  | [], _, _, r, hr => nomatch hr
  | r :: rs, i, h, x, hx => by
    unfold firstRefused at h
    split at h
    · cases h
    · rename_i a ha
      rcases List.mem_cons.mp hx with rfl | hx
      · exact ⟨a, ha⟩
      · exact firstRefused_none rs (i + 1) h x hx

theorem caseOf_get (i : Nat) (d : CoreDoc) :
    (caseOf i d).getObjValD "environment" = d.environment ∧ (caseOf i d).getObjValD "norms" = d.norms ∧
      (caseOf i d).getObjVal? "facts" = .ok (factsJson d.premises) := by
  have hn : ([("id", Json.str s!"choice-{i}"), ("kind", Json.str "slot-admission"), ("environment", d.environment),
      ("norms", d.norms), ("facts", factsJson d.premises)].map (·.1)).Nodup := by simp
  have g := fun (k : String) (v : Json) (hm : (k, v) ∈ [("id", Json.str s!"choice-{i}"), ("kind", Json.str "slot-admission"),
      ("environment", d.environment), ("norms", d.norms), ("facts", factsJson d.premises)]) =>
    VE.Calc.Run.mkObj_get _ k v hn hm
  unfold caseOf
  refine ⟨?_, ?_, g _ _ (by simp)⟩
  · simp only [Json.getObjValD, g "environment" d.environment (by simp)]; rfl
  · simp only [Json.getObjValD, g "norms" d.norms (by simp)]; rfl

/-- The round trip: for every case the shell builds from a core document `(X, P)`, the facts `decodeFacts` reads from
it, over the source the kernel decodes from the same case, are exactly `P` (`decodeFormulas_encode`); the shell refused
every core document for which a hypothesis of the round trip fails, with the decoder's own diagnostic (`caseFault`). -/
theorem core_facts_round_trip {docs : List (Choice × CoreDoc)} {cases : List Json} (h : casesOf docs = .ok cases)
    (k : Nat) (hk : k < docs.length) (src : VE.SoftNorms.Wire.SoftSource)
    (hs : VE.SoftNorms.Wire.decodeSoftSource ((caseOf k docs[k].2).getObjValD "environment")
      ((caseOf k docs[k].2).getObjValD "norms") = .ok src) :
    cases[k]? = some (caseOf k docs[k].2) ∧
      decodeFacts src (caseOf k docs[k].2) =
        .ok (docs[k].2.premises, docs[k].2.premises.map VE.Route.Wire.encodeFormula) := by
  obtain ⟨hc, hf⟩ := (casesOf_ok h).2 k hk
  refine ⟨hc, ?_⟩
  obtain ⟨hE, hN, hF⟩ := caseOf_get k docs[k].2
  rw [hE, hN] at hs
  unfold caseFault at hf
  rw [hs] at hf
  simp only at hf
  split at hf
  · rename_i hr
    simp only [roundTrips, Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hr
    obtain ⟨⟨⟨hC, hD⟩, hNo⟩, hDec⟩ := hr
    generalize docs[k].2.premises = P at *
    unfold decodeFacts
    rw [hF]
    simp only [factsJson, Json.getArr?, pure, Except.pure]
    split
    · rename_i he
      have : P = [] := by simpa using he
      subst this
      rfl
    · rw [VE.Route.Wire.decodeFormulas_encode _ P false hC hD hNo (fun h => absurd h (by decide))]
      have hnone : P.findSome? (fun x => (VE.Norms.preds x).find? fun p => decide (p ∈ VE.SoftNorms.decisionNames src.D)) =
          none := by
        rw [List.findSome?_eq_none_iff]
        intro x hx
        rw [List.find?_eq_none]
        intro p hp
        simpa using hDec p (List.mem_flatMap.mpr ⟨x, hx, hp⟩)
      simp [bind, Except.bind]
      rw [hnone]
  · cases hf

/-- `document_core_sound`, the instance of `shell_sound`: a document answer of the core path is the fold of the rows
the kernel gave for the cases built from the lowering's core documents, one per choice in the lowering's order; every
row was accepted, and each means what `slot_wire_admission` says of its case. -/
theorem document_core_sound (j row : Json) (h : answer j = .ok row) :
    ∃ p : Prepared, prepare j = .ok p ∧
      lower p.I.d.E p.I.d.senses p.I.d.records p.I.views p.I.d.units p.I.sets [] = .ok p.docs ∧
      p.cases.length = p.docs.length ∧ (∀ k (hk : k < p.docs.length), p.cases[k]? = some (caseOf k p.docs[k].2)) ∧
      ∃ rows : List Row, rows = p.cases.map softNormsPath.row ∧
        (∀ r ∈ rows, softNormsPath.Ran r ∧ ∃ x, r.result = .ok x ∧ softNormsPath.Meaning r.case x) ∧
        row = VE.Route.Wire.ok p.I.id
          [("view", (fold (viewOf p.I p.docs) (tableOf p.I p.docs) j rows).getObjValD "view"),
           ("rows", (fold (viewOf p.I p.docs) (tableOf p.I p.docs) j rows).getObjValD "rows")] := by
  unfold answer at h
  obtain ⟨p, hp, h⟩ := bind_ok h
  obtain ⟨a, ha, h⟩ := bind_ok h
  have hdocs : lower p.I.d.E p.I.d.senses p.I.d.records p.I.views p.I.d.units p.I.sets [] = .ok p.docs ∧
      casesOf p.docs = .ok p.cases := by
    unfold prepare at hp
    obtain ⟨I, hI, hp⟩ := bind_ok hp
    obtain ⟨docs, hd, hp⟩ := bind_ok hp
    obtain ⟨cases, hc, hp⟩ := bind_ok hp
    cases hp
    exact ⟨hd, hc⟩
  obtain ⟨hlen, hget⟩ := casesOf_ok hdocs.2
  have hshell : a = fold (viewOf p.I p.docs) (tableOf p.I p.docs) j (p.cases.map softNormsPath.row) := by
    simp only [shell, Except.map, Except.ok.injEq] at ha
    exact ha.symm
  split at h
  · cases h
  rename_i hnone
  split at h
  · cases h
  simp only [pure, Except.pure, Except.ok.injEq] at h
  refine ⟨p, hp, hdocs.1, hlen, fun k hk => (hget k hk).1, _, rfl, fun r hr => ⟨?_, ?_⟩, ?_⟩
  · obtain ⟨c, _, rfl⟩ := List.mem_map.mp hr
    rfl
  · obtain ⟨x, hx⟩ := firstRefused_none _ 0 hnone r hr
    obtain ⟨c, _, rfl⟩ := List.mem_map.mp hr
    exact ⟨x, hx, softNormsPath.sound c x hx⟩
  · rw [← h, hshell]

end VE.Service.CoreCheck
