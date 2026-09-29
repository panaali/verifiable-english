import VE.Route.Wire

/-! Executable admission of documents on the new route (PLAN-EXPAND2 3.6). A
JSON document on `ve.core@0.2` is decoded to units with nested kind trees
(`attributed(agent, act, kind)`, `hedged(modality, kind)`, `causal(relation,
kind, kind)`), declared lemmas (with their transitive leaves), open terms,
reading sets, narrowings and a claim graph whose nodes carry provenance labels.

Admission checks, per node: a node that names a quoted unit (attributed or
hedged) is a bridge leaf `bridge:accepts(<agent>,<unit>)` naming that unit,
with exactly the unit's formula. Formula-equal independent leaves retain their
own provenance. An asserted leaf is exactly an
asserted unit's formula; a background leaf is a premise regenerated from the
environment under its generator; cite, open, readings and narrowing leaves name
declared objects. Per report: every cited lemma's transitive leaves are present
with their labels, and reading choices are compatible (one version and one
choice per reading set). The claim graph is then checked by the unchanged
`VE.Graph.check` with the production `tableauValid`, and `admit_report_sound`
states that an admitted document's report is a `SoundReport` whose assumption
list carries exactly the decoded labels. A general decoder for legacy graph
artefacts is deferred (PLAN-EXPAND2 section 7). -/
namespace VE.Route.Admission
open Lean
open VE.Bridge (exactFields fields stringField strings)
open VE.Graph (Claim Report)
universe u

/-! ## Tokens, kinds and labels -/

def tokenChar (c : Char) : Bool := c.isAlphanum || c == '_' || c == '-' || c == '.'

/-- Names inside kinds and labels: nonempty, at most 64 bytes, `[A-Za-z0-9_.-]`. -/
def token (s : String) : Bool := !s.isEmpty && s.utf8ByteSize ≤ 64 && s.all tokenChar

/-- The W2 content kinds; kinds nest. -/
inductive Kind where
  | asserted
  | norm
  | definition
  | attributed (agent act : String) (body : Kind)
  | hedged (modality : String) (body : Kind)
  | causal (relation : String) (cause effect : Kind)
  | question
  | instruction
  | «example»
  | exposition
  | analogy
  | explanation
  | «meta»
  | unformalised (reason : String)
  deriving DecidableEq, Repr

def acts : List String := ["says", "promised", "believes", "intends", "expects", "denies"]
def modalities : List String := ["could", "likely", "generally", "typically", "effectively"]
def relations : List String := ["because", "in order to", "prevents"]

/-- Quoted content: the unit reports someone's statement or a hedge. -/
def Kind.quoted : Kind → Bool
  | .attributed .. | .hedged .. => true
  | _ => false

def Kind.agent? : Kind → Option String
  | .attributed a _ _ => some a
  | _ => none

def Kind.depth : Kind → Nat
  | .attributed _ _ b | .hedged _ b => b.depth + 1
  | .causal _ c e => max c.depth e.depth + 1
  | _ => 1

def atomicKind : String → Option Kind
  | "asserted" => some .asserted
  | "norm" => some .norm
  | "definition" => some .definition
  | "question" => some .question
  | "instruction" => some .instruction
  | "example" => some .«example»
  | "exposition" => some .exposition
  | "analogy" => some .analogy
  | "explanation" => some .explanation
  | "meta" => some .«meta»
  | _ => none

/-- The kind wire form: a string for an atomic kind, else a tagged array. -/
def renderKind : Kind → Json
  | .asserted => .str "asserted"
  | .norm => .str "norm"
  | .definition => .str "definition"
  | .attributed a act b => Json.arr #[.str "attributed", .str a, .str act, renderKind b]
  | .hedged m b => Json.arr #[.str "hedged", .str m, renderKind b]
  | .causal r c e => Json.arr #[.str "causal", .str r, renderKind c, renderKind e]
  | .question => .str "question"
  | .instruction => .str "instruction"
  | .«example» => .str "example"
  | .exposition => .str "exposition"
  | .analogy => .str "analogy"
  | .explanation => .str "explanation"
  | .«meta» => .str "meta"
  | .unformalised r => Json.arr #[.str "unformalised", .str r]

def decodeKind : Nat → Json → Except String Kind
  | 0, _ => .error "ResourceLimit: kind depth exceeds 16"
  | _ + 1, .str s => match atomicKind s with
    | some k => .ok k
    | none => .error s!"unknown kind {s}"
  | n + 1, .arr a => match a.toList with
    | [.str "attributed", .str agent, .str act, body] =>
      if token agent && acts.contains act then (decodeKind n body).map (.attributed agent act)
      else .error "invalid attributed kind"
    | [.str "hedged", .str m, body] =>
      if modalities.contains m then (decodeKind n body).map (.hedged m)
      else .error "invalid hedged kind"
    | [.str "causal", .str r, c, e] =>
      if relations.contains r then
        match decodeKind n c, decodeKind n e with
        | .ok c', .ok e' => .ok (.causal r c' e')
        | .error m, _ => .error m
        | _, .error m => .error m
      else .error "invalid causal kind"
    | [.str "unformalised", .str r] =>
      if token r then .ok (.unformalised r) else .error "invalid unformalised reason"
    | _ => .error "invalid kind"
  | _ + 1, _ => .error "invalid kind"

theorem atomicKind_render (s : String) (k : Kind) (h : atomicKind s = some k) :
    renderKind k = .str s := by
  unfold atomicKind at h
  split at h <;> cases h <;> rfl

/-- A decoded kind tree renders back to exactly the JSON it was decoded from
(hence byte-identically under canonical serialisation). -/
theorem decodeKind_render (n : Nat) (j : Json) (k : Kind) (h : decodeKind n j = .ok k) :
    renderKind k = j := by
  induction n generalizing j k with
  | zero => cases h
  | succ n ih =>
    cases j with
    | str s =>
      simp only [decodeKind] at h
      split at h
      · rename_i k' hk
        cases h
        exact atomicKind_render s _ hk
      · cases h
    | arr a =>
      cases a with
      | mk l =>
        simp only [decodeKind] at h
        split at h
        · rename_i _ agent act body
          split at h
          · cases hb : decodeKind n body with
            | error e => simp [hb, Except.map] at h
            | ok b =>
              simp [hb, Except.map] at h
              subst h
              simp [renderKind, ih body b hb]
          · cases h
        · rename_i _ m body
          split at h
          · cases hb : decodeKind n body with
            | error e => simp [hb, Except.map] at h
            | ok b =>
              simp [hb, Except.map] at h
              subst h
              simp [renderKind, ih body b hb]
          · cases h
        · rename_i _ r c e _
          split at h
          · split at h
            · rename_i c' e' hc he
              cases h
              simp [renderKind, ih c c' hc, ih e e' he]
            · cases h
            · cases h
          · cases h
        · rename_i _ r
          split at h
          · cases h
            simp [renderKind]
          · cases h
        · cases h
    | _ => simp [decodeKind] at h

/-- Provenance labels (PLAN-EXPAND2 3.6). -/
inductive Label where
  | asserted
  | bridge (agent unit : String)
  | background (generator : String)
  | cite (bundle lemma : String)
  | openTerm (term : String)
  | readings (set : String) (version : Nat) (choice : Option Nat)
  | narrowing (id : String)
  deriving DecidableEq, Repr

def Label.render : Label → String
  | .asserted => "asserted"
  | .bridge a u => "bridge:accepts(" ++ a ++ "," ++ u ++ ")"
  | .background g => "background:" ++ g
  | .cite b l => "cite:" ++ b ++ "/" ++ l
  | .openTerm t => "open:" ++ t
  | .readings s v c => "readings:" ++ s ++ "@" ++ toString v ++ ":" ++
      (match c with | some i => toString i | none => "all")
  | .narrowing n => "narrowing:" ++ n

def parseLabelRaw (s : String) : Option Label :=
  if s == "asserted" then some .asserted
  else if s.startsWith "bridge:accepts(" && s.endsWith ")" then
    match ((s.drop 15).dropRight 1).splitOn "," with
    | [a, u] => if token a && token u then some (.bridge a u) else none
    | _ => none
  else if s.startsWith "background:" then
    let g := s.drop 11
    if Background.generators.contains g then some (.background g) else none
  else if s.startsWith "cite:" then
    match (s.drop 5).splitOn "/" with
    | [b, l] => if token b && token l then some (.cite b l) else none
    | _ => none
  else if s.startsWith "open:" then
    let t := s.drop 5
    if token t then some (.openTerm t) else none
  else if s.startsWith "readings:" then
    match (s.drop 9).splitOn "@" with
    | [set, rest] =>
      match rest.splitOn ":" with
      | [v, c] =>
        match token set, v.toNat? with
        | true, some vn =>
          if c == "all" then some (.readings set vn none)
          else (c.toNat?).map (fun i => .readings set vn (some i))
        | _, _ => none
      | _ => none
    | _ => none
  else if s.startsWith "narrowing:" then
    let n := s.drop 10
    if token n then some (.narrowing n) else none
  else none

/-- Only canonical label strings parse: the parsed label renders back to the
exact input, so a label string and its meaning determine each other. -/
def parseLabel (s : String) : Option Label :=
  match parseLabelRaw s with
  | some l => if l.render == s then some l else none
  | none => none

theorem parseLabel_render (s : String) (l : Label) (h : parseLabel s = some l) : l.render = s := by
  unfold parseLabel at h
  split at h
  · split at h
    · rename_i hr
      cases h
      exact beq_iff_eq.mp hr
    · cases h
  · cases h

/-! ## Documents -/

structure DocUnit where
  id : String
  start : Nat
  stop : Nat
  kind : Kind
  content : Option VE.Formula
  deriving DecidableEq, Repr

structure Lemma where
  name : String
  conclusion : VE.Formula
  leaves : List (VE.Formula × String)
  deriving DecidableEq, Repr

structure ReadingSet where
  id : String
  version : Nat
  readings : List VE.Formula
  deriving DecidableEq, Repr

structure Doc where
  literals : List String
  flags : List VE.Data.Background.Flag
  units : List DocUnit
  lemmas : List Lemma
  openTerms : List String
  readingSets : List ReadingSet
  narrowings : List String

/-- A decoded graph node: the claim (with its label), the unit it formalises
(if any) and its deduction (if any). -/
structure WireNode where
  claim : Claim
  unit : Option String
  deduction : Option (VE.Graph.Edge VE.Tableau.Certificate)

def WireNode.toNode (w : WireNode) : VE.Graph.Node VE.Tableau.Certificate := ⟨w.claim, w.deduction⟩

/-- The disjunction of a reading set's readings (right-nested), the content of
a `readings:<set>@<version>:all` leaf. -/
def disjunction : List VE.Formula → Option VE.Formula
  | [] => none
  | [a] => some a
  | a :: as => (disjunction as).map (.or a)

/-! ## The admission rules, as independent propositions -/

def AssertedUnit (D : Doc) (u : String) (φ : VE.Formula) : Prop :=
  ∃ x ∈ D.units, x.id = u ∧ x.kind = .asserted ∧ x.content = some φ

/-- An attributed unit's bridge names its attributed agent; other quoted
units (hedges) record whoever accepts them. -/
def agentMatches (k : Kind) (agent : String) : Bool :=
  match k.agent? with
  | some g => agent == g
  | none => true

def QuotedUnit (D : Doc) (agent u : String) (φ : VE.Formula) : Prop :=
  ∃ x ∈ D.units, x.id = u ∧ x.kind.quoted = true ∧ x.content = some φ ∧ agentMatches x.kind agent = true

def ReadingContent (D : Doc) (s : String) (v : Nat) (c : Option Nat) (φ : VE.Formula) : Prop :=
  ∃ rs ∈ D.readingSets, rs.id = s ∧ rs.version = v ∧
    match c with
    | some i => rs.readings[i]? = some φ
    | none => disjunction rs.readings = some φ

/-- The provenance rule for an undischarged leaf. -/
def LeafAdmitted (D : Doc) (w : WireNode) : Prop :=
  match parseLabel w.claim.label with
  | some .asserted => ∃ u, w.unit = some u ∧ AssertedUnit D u w.claim.formula
  | some (.bridge a u) => (w.unit = none ∨ w.unit = some u) ∧ QuotedUnit D a u w.claim.formula
  | some (.background g) => w.unit = none ∧
      ∃ p ∈ (VE.Data.Background.generate D.flags).map (fun a => (a, "flags")) ++
        Background.background D.literals, p = (w.claim.formula, g)
  | some (.cite b l) => w.unit = none ∧ ∃ m ∈ D.lemmas, m.name = b ++ "/" ++ l ∧ m.conclusion = w.claim.formula
  | some (.openTerm t) => w.unit = none ∧ t ∈ D.openTerms
  | some (.readings s v c) => w.unit = none ∧ ReadingContent D s v c w.claim.formula
  | some (.narrowing n) => w.unit = none ∧ n ∈ D.narrowings
  | none => False

/-- A deduction is an asserted claim; if it formalises a unit, that unit is an
asserted unit with exactly its formula. -/
def NodeAdmitted (D : Doc) (w : WireNode) : Prop :=
  match w.deduction with
  | some _ => w.claim.label = "asserted" ∧ ∀ u, w.unit = some u → AssertedUnit D u w.claim.formula
  | none => LeafAdmitted D w

/-- The label cites this lemma. -/
def citesLemma (label : String) (m : Lemma) : Bool :=
  match parseLabel label with
  | some (.cite b l) => m.name == b ++ "/" ++ l
  | _ => false

/-- Every cited lemma's transitive leaves are in the report with their labels. -/
def CitationsClosed (D : Doc) (r : Report) : Prop :=
  ∀ leaf ∈ r.assumptions, ∀ m ∈ D.lemmas, citesLemma leaf.label m = true →
    ∀ x ∈ m.leaves, ∃ y ∈ r.assumptions, y.formula = x.1 ∧ y.label = x.2

/-- Two labels are compatible unless they name the same reading set with
different versions or different concrete choices (`all` is compatible with any
choice: a result under every reading holds under each). -/
def compatible (x y : String) : Bool :=
  match parseLabel x, parseLabel y with
  | some (.readings s v c), some (.readings s' v' c') =>
    s != s' || (v == v' && match c, c' with
      | some i, some j => i == j
      | _, _ => true)
  | _, _ => true

def ChoicesCompatible (r : Report) : Prop :=
  ∀ a ∈ r.assumptions, ∀ b ∈ r.assumptions, compatible a.label b.label = true

instance (D : Doc) (u : String) (φ : VE.Formula) : Decidable (AssertedUnit D u φ) := by
  unfold AssertedUnit; infer_instance

instance (D : Doc) (a u : String) (φ : VE.Formula) : Decidable (QuotedUnit D a u φ) := by
  unfold QuotedUnit; infer_instance

instance (D : Doc) (s : String) (v : Nat) (c : Option Nat) (φ : VE.Formula) :
    Decidable (ReadingContent D s v c φ) := by
  unfold ReadingContent
  cases c <;> infer_instance

instance (D : Doc) (w : WireNode) : Decidable (LeafAdmitted D w) := by
  unfold LeafAdmitted
  split <;> infer_instance

instance (D : Doc) (w : WireNode) : Decidable (NodeAdmitted D w) := by
  unfold NodeAdmitted
  split
  · exact decidable_of_iff (w.claim.label = "asserted" ∧
      ∀ u ∈ w.unit.toList, AssertedUnit D u w.claim.formula) (by simp)
  · infer_instance

instance (D : Doc) (r : Report) : Decidable (CitationsClosed D r) := by
  unfold CitationsClosed; infer_instance

instance (r : Report) : Decidable (ChoicesCompatible r) := by
  unfold ChoicesCompatible; infer_instance

/-! ## Diagnostics (untrusted text; only success carries a theorem) -/

def unitOf (D : Doc) (u : String) : Option DocUnit := D.units.find? (fun x => x.id == u)

def nodeDiagnostic (D : Doc) (w : WireNode) : String :=
  let bridgeNaming := match parseLabel w.claim.label, w.deduction with
    | some (.bridge _ u), none => some u
    | _, _ => none
  match w.unit.bind (unitOf D) with
  | some x =>
    if x.kind.quoted && bridgeNaming != some x.id then
      s!"AdmissionError: quoted content of unit {x.id} is used without a bridge leaf"
    else s!"AdmissionError: node {w.claim.name} is not admitted under label {w.claim.label}"
  | none =>
    match parseLabel w.claim.label with
    | none => s!"AdmissionError: invalid label {w.claim.label}"
    | some _ => s!"AdmissionError: node {w.claim.name} is not admitted under label {w.claim.label}"

/-! ## Decoding -/

/-- A small `require` helper so every check is one bind step. -/
abbrev require := Gate.require

def decodeUnit (E : VE.Environment) (data : Bool) (j : Json) : Except String DocUnit := do
  VE.Bridge.displayFields j ["id", "span", "kind"] ["content"]
  let id ← stringField j "id"
  require (token id) s!"invalid unit id {id}"
  let (start, stop) ← match (← (← j.getObjVal? "span").getArr?).toList with
    | [a, b] => pure (← a.getNat?, ← b.getNat?)
    | _ => throw "invalid span"
  require (start ≤ stop) "invalid span"
  let kind ← decodeKind 16 (← j.getObjVal? "kind")
  let content ← match j.getObjVal? "content" with
    | .ok ast => some <$> Wire.decodeClosed E ast data
    | .error _ => pure none
  pure ⟨id, start, stop, kind, content⟩

def sortedSpans : List DocUnit → Bool
  | a :: b :: rest => a.stop ≤ b.start && sortedSpans (b :: rest)
  | _ => true

def decodeLeaf (E : VE.Environment) (data : Bool) (j : Json) : Except String (VE.Formula × String) := do
  exactFields j ["ast", "label"]
  let l ← stringField j "label"
  match parseLabel l with
  | none => throw s!"AdmissionError: invalid label {l}"
  | some (.cite _ _) => throw "AdmissionError: lemma leaves must be transitive (no cite labels)"
  | some _ =>
    let a ← Wire.decodeClosed E (← j.getObjVal? "ast") (data && !l.startsWith "background:")
    pure (a, l)

def decodeLemma (E : VE.Environment) (data : Bool) (j : Json) : Except String Lemma := do
  exactFields j ["name", "conclusion", "leaves"]
  let name ← stringField j "name"
  match parseLabel ("cite:" ++ name) with
  | some (.cite _ _) => pure ()
  | _ => throw s!"invalid lemma name {name}"
  let c ← Wire.decodeClosed E (← j.getObjVal? "conclusion") data
  let leaves ← (← (← j.getObjVal? "leaves").getArr?).toList.mapM (decodeLeaf E data)
  require (leaves.length ≤ 1000) "ResourceLimit: lemma leaves"
  pure ⟨name, c, leaves⟩

def decodeReadingSet (E : VE.Environment) (data : Bool) (j : Json) : Except String ReadingSet := do
  exactFields j ["id", "version", "readings"]
  let id ← stringField j "id"
  require (token id) s!"invalid reading set id {id}"
  let version ← (← j.getObjVal? "version").getNat?
  let readings ← (← (← j.getObjVal? "readings").getArr?).toList.mapM
    (fun a => Wire.decodeClosed E a data)
  require (!readings.isEmpty && readings.length ≤ 64) "reading sets hold 1 to 64 readings"
  pure ⟨id, version, readings⟩

def tokens (j : Json) : Except String (List String) := do
  let xs ← strings j
  require (xs.all token) "invalid name"
  pure xs

/-- Decode one graph node. Premises and certificate come together; the
default label `asserted` is omitted on the wire (an explicit default is
non-canonical and rejected). -/
def decodeNode (E : VE.Environment) (data : Bool) (j : Json) :
    Except String (WireNode × Json) := do
  VE.Bridge.displayFields j ["name", "ast"] ["label", "unit", "premises", "certificate"]
  let name ← stringField j "name"
  let astJson ← j.getObjVal? "ast"
  let label ← match j.getObjVal? "label" with
    | .ok l => do
      let s ← l.getStr?
      require (s != "asserted") "non-canonical label: the default label asserted is omitted"
      pure s
    | .error _ => pure "asserted"
  let formula ← Wire.decodeClosed E astJson (data && !label.startsWith "background:")
  let unit ← match j.getObjVal? "unit" with
    | .ok u => some <$> u.getStr?
    | .error _ => pure none
  let deduction ← match j.getObjVal? "premises", j.getObjVal? "certificate" with
    | .ok ps, .ok c => do
      pure (some ⟨← strings ps, ← VE.CertificateWire.decodeCertificate c⟩)
    | .error _, .error _ => pure none
    | _, _ => throw "premises and certificate come together"
  pure (⟨{ name, formula, label }, unit, deduction⟩, astJson)

/-- Every deduction's certificate binds the environment, the premise nodes'
ASTs in order and the node's AST by `ve.core@0.2` meaning ids. -/
def checkBindings (profiles : List String) (environment : Json) (nodes : List (WireNode × Json)) :
    Except String Unit := do
  for (w, ast) in nodes do
    if let some edge := w.deduction then
      let premiseAsts ← edge.premises.mapM fun p =>
        match nodes.find? (fun n => n.1.claim.name == p) with
        | some n => pure n.2
        | none => throw s!"dangling premise {p}"
      Wire.bindingOk profiles environment premiseAsts ast edge.certificate.environment_id
        edge.certificate.premise_meaning_ids edge.certificate.conclusion_meaning_id

/-- The result of admission. -/
structure Admitted where
  rv : Wire.RouteVocabulary
  doc : Doc
  wires : List WireNode
  graph : VE.Graph.ClaimGraph VE.Tableau.Certificate
  report : Report
  kinds : List Json

def decodeDoc (rv : Wire.RouteVocabulary) (data : Bool) (j : Json)
    (E : VE.Environment := rv.environment) : Except String Doc := do
  let units ← (← (← j.getObjVal? "units").getArr?).toList.mapM (decodeUnit E data)
  require (units.length ≤ 10000) "ResourceLimit: unit count"
  require ((units.map DocUnit.id).eraseDups.length == units.length) "duplicate unit id"
  require (sortedSpans units) "unit spans must be sorted and non-overlapping"
  let optional := fun (key : String) => match j.getObjVal? key with
    | .ok v => v.getArr?.map Array.toList
    | .error _ => pure []
  let lemmas ← (← optional "lemmas").mapM (decodeLemma E data)
  require ((lemmas.map Lemma.name).eraseDups.length == lemmas.length) "duplicate lemma"
  let openTerms ← tokens (Json.arr (← optional "open_terms").toArray)
  let readingSets ← (← optional "reading_sets").mapM (decodeReadingSet E data)
  require ((readingSets.map (fun r => (r.id, r.version))).eraseDups.length == readingSets.length)
    "duplicate reading set version"
  let narrowings ← tokens (Json.arr (← optional "narrowings").toArray)
  pure ⟨rv.literals, rv.flags, units, lemmas, openTerms, readingSets, narrowings⟩

/-- The first node that is not admitted, if any. -/
def firstUnadmitted (D : Doc) (ws : List WireNode) : Option WireNode :=
  ws.find? (fun w => !decide (NodeAdmitted D w))

def admitNodes (D : Doc) (ws : List WireNode) : Except String Unit :=
  match firstUnadmitted D ws with
  | some w => .error (nodeDiagnostic D w)
  | none => .ok ()

def graphRejected : String :=
  "graph rejected: cycle, duplicate name, dangling premise, ill-typed claim or invalid certificate"

/-- A certificate needing more than Python's 10,000 replay steps is not
established, so the graph is rejected as for any invalid certificate. -/
def checkGraph (E : VE.Environment) (g : VE.Graph.ClaimGraph VE.Tableau.Certificate) :
    Except String Report :=
  if g.nodes.any (fun n => match n.deduction with
      | some e => Steps.fol e.certificate.trace > Steps.maxSteps
      | none => false) then .error graphRejected
  else match VE.Graph.checkTableau E g with
  | some r => .ok r
  | none => .error graphRejected

def admitDocument (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (j : Json) :
    Except String Admitted := do
  VE.Bridge.displayFields j ["units", "graph"] ["lemmas", "open_terms", "reading_sets", "narrowings"]
  let D₀ ← decodeDoc rv (profiles.contains "data@0") j
  let D := { D₀ with literals := rv.literals, flags := rv.flags }
  let graphJson ← j.getObjVal? "graph"
  exactFields graphJson ["root", "nodes"]
  let root ← stringField graphJson "root"
  let nodeArray ← (← graphJson.getObjVal? "nodes").getArr?
  require (nodeArray.size ≤ 1000) "ResourceLimit: graph node count"
  let decoded ← nodeArray.toList.mapM (decodeNode rv.environment (profiles.contains "data@0"))
  checkBindings profiles environment decoded
  let wires := decoded.map Prod.fst
  admitNodes D wires
  let g : VE.Graph.ClaimGraph VE.Tableau.Certificate := ⟨wires.map WireNode.toNode, root⟩
  let r ← checkGraph rv.environment g
  require (decide (CitationsClosed D r)) "AdmissionError: a cited lemma's leaves are missing from the report"
  require (decide (ChoicesCompatible r)) "AdmissionError: incompatible reading choices"
  pure ⟨rv, D, wires, g, r, D.units.map (fun x => renderKind x.kind)⟩

theorem admitNodes_ok (D : Doc) (ws : List WireNode) (u : Unit) (h : admitNodes D ws = .ok u) :
    ∀ w ∈ ws, NodeAdmitted D w := by
  unfold admitNodes at h
  split at h
  · cases h
  · rename_i hf
    intro w hw
    have := List.find?_eq_none.mp hf w hw
    simpa using this

theorem checkGraph_ok (E : VE.Environment) (g : VE.Graph.ClaimGraph VE.Tableau.Certificate)
    (r : Report) (h : checkGraph E g = .ok r) : VE.Graph.checkTableau E g = some r := by
  unfold checkGraph at h
  split at h
  · cases h
  split at h
  · cases h
    assumption
  · cases h

open VE.Order.ProfileGate in
/-- `admit_report_sound`: an admitted document's report is a `SoundReport` for
the decoded claim graph (acyclic, unique names, exact root, typed leaves that
are explicitly submitted assumptions, entailment, exact ordered unfolding);
every decoded node satisfies its admission rule; every assumption of the report
is a decoded leaf, carrying exactly its decoded label and satisfying the leaf
rule for that label; cited lemmas' leaves are present with their labels; and
reading choices are compatible. -/
theorem admit_report_sound (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary)
    (j : Json) (res : Admitted) (h : admitDocument profiles environment rv j = .ok res) :
    res.rv = rv ∧ res.doc.literals = rv.literals ∧ res.doc.flags = rv.flags ∧
    res.graph.nodes = res.wires.map WireNode.toNode ∧
    VE.Graph.Acyclic res.graph ∧ (res.graph.nodes.map (fun n => n.claim.name)).Nodup ∧
    res.report.root.name = res.graph.root ∧
    VE.Graph.SoundReport.{u} rv.environment res.graph res.report ∧
    (∀ w ∈ res.wires, NodeAdmitted res.doc w) ∧
    (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
      w.claim = leaf ∧ w.deduction = none ∧ LeafAdmitted res.doc w) ∧
    CitationsClosed res.doc res.report ∧ ChoicesCompatible res.report := by
  unfold admitDocument at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨D₀, _, h⟩ := bind_ok h
  obtain ⟨gj, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨root, _, h⟩ := bind_ok h
  obtain ⟨nj, _, h⟩ := bind_ok h
  obtain ⟨arr, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨decoded, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, hadm, h⟩ := bind_ok h
  obtain ⟨r, hr, h⟩ := bind_ok h
  obtain ⟨_, hc, h⟩ := bind_ok h
  obtain ⟨_, hch, h⟩ := bind_ok h
  cases h
  have hnodes := admitNodes_ok _ _ _ hadm
  obtain ⟨hacyc, hnd, hroot, hsound⟩ :=
    VE.Graph.check_sound.{u} rv.environment _ r (checkGraph_ok _ _ r hr)
  refine ⟨rfl, rfl, rfl, rfl, hacyc, hnd, hroot, hsound, hnodes, ?_,
    of_decide_eq_true (Gate.require_ok hc), of_decide_eq_true (Gate.require_ok hch)⟩
  intro leaf hl
  obtain ⟨node, hn, hcl, hde⟩ := (hsound.2.2.1 leaf hl).2
  obtain ⟨w, hw, rfl⟩ := List.mem_map.mp hn
  refine ⟨w, hw, hcl, hde, ?_⟩
  have := hnodes w hw
  unfold NodeAdmitted at this
  simp only [WireNode.toNode] at hde
  rw [hde] at this
  exact this

/-- Labels are exactly the decoded ones: each assumption's label is the label
of the decoded leaf node it is, so stripping or changing a label on the wire
changes the report. -/
theorem admit_labels_decoded (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary)
    (j : Json) (res : Admitted) (h : admitDocument profiles environment rv j = .ok res) :
    ∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires, w.claim.label = leaf.label ∧
      w.claim.name = leaf.name ∧ w.claim.formula = leaf.formula := by
  intro leaf hl
  obtain ⟨w, hw, rfl, _, _⟩ := (admit_report_sound.{0} profiles environment rv j res h).2.2.2.2.2.2.2.2.2.1 leaf hl
  exact ⟨w, hw, rfl, rfl, rfl⟩

/-- Admitted background leaves are discharged by the decoded literal and flag
meanings. Author formulas still pass the stage-1 `$string` binder restriction. -/
theorem admit_string_sound (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary)
    (j : Json) (res : Admitted) (h : admitDocument profiles environment rv j = .ok res)
    (S : VE.Structure.{u})
    (hS : VE.Data.Background.DataAdmissible rv.environment rv.literals rv.flags S)
    (hleaves : ∀ leaf ∈ res.report.assumptions,
      (∀ g, parseLabel leaf.label ≠ some (.background g)) → leaf.formula.denote S []) :
    res.report.root.formula.denote S [] := by
  obtain ⟨_, hlit, hflags, _, _, _, _, hsound, _, hleaf, _, _⟩ :=
    admit_report_sound.{u} profiles environment rv j res h
  apply hsound.2.2.2.1 S hS.1.1
  intro a ha
  obtain ⟨leaf, hl, rfl⟩ := List.mem_map.mp ha
  by_cases hb : ∃ g, parseLabel leaf.label = some (.background g)
  · obtain ⟨g, hg⟩ := hb
    obtain ⟨w, _, hwl, _, hadm⟩ := hleaf leaf hl
    unfold LeafAdmitted at hadm
    rw [hwl, hg] at hadm
    obtain ⟨_, p, hp, hpe⟩ := hadm
    subst hpe
    rw [hlit, hflags] at hp
    rcases List.mem_append.mp hp with hf | hl
    · obtain ⟨b, hbm, hbe⟩ := List.mem_map.mp hf
      simp only [Prod.mk.injEq] at hbe
      rw [← hbe.1]
      exact (VE.Data.Background.generate_sat_iff S rv.flags).mpr hS.2 b hbm
    · obtain ⟨b, hbm, hbe⟩ := List.mem_map.mp hl
      simp only [Prod.mk.injEq] at hbe
      rw [← hbe.1]
      exact (Background.literals_sat_iff S rv.literals rv.nodup).mpr hS.1.2 b hbm
  · exact hleaves leaf hl (fun g hg => hb ⟨g, hg⟩)

end VE.Route.Admission
