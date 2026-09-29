import VE.Risk.Derive
import VE.Risk.Words
import VE.Time.Decimal
import VE.Time.Calendar
import VE.Order.Wire

/-! Decision records, log entries and admission (docs/spec/risk.md 1.3, 1.4, 3.2,
3.3 and 4.4 A1 to A3).

A record is the `content` of a `decision` log entry. `admitDecision R dx es`
authenticates it once against the entries `es` (the supplied entries, or the
log prefix in the audit): the decision entry's own hash, the binding to the
loaded policy, the per-decision limits, then each citation in cite order
(`HindsightEntry`, `MissingEntry`, `AlteredEntry`, `WithdrawnEntry`) and the
facts' entries. The admitted `Decision` carries the record, the decoded
contents of its cited entries (estimates lowered onto their unit grids) and
the decision entry's sequence number and day. Problems that validation
reports at a later step (an unknown quantity, a value off the grid, a tag
mismatch in a condition, a statement form) are kept in `issues` with the step
that reports them, so the diagnostic order of 4.4 is preserved. -/
namespace VE.Risk
open Lean
open VE.Norms (layerNames envAt tupleVal)
open VE.Alternatives (Row AltDoc inlineTree)
open VE.Bridge (exactFields fields stringField strings)

/-! ## Records -/

inductive Support | observation | statistical | calculation | testimony | assumption
  deriving DecidableEq, Repr

def Support.name : Support → String
  | .observation => "observation"
  | .statistical => "statistical"
  | .calculation => "calculation"
  | .testimony => "testimony"
  | .assumption => "assumption"

def Support.ofString : String → Option Support
  | "observation" => some .observation
  | "statistical" => some .statistical
  | "calculation" => some .calculation
  | "testimony" => some .testimony
  | "assumption" => some .assumption
  | _ => none

inductive Form | sufficient | necessary | exact
  deriving DecidableEq, Repr

inductive Stated | leads | cannot | might
  deriving DecidableEq, Repr

structure Cited where
  id : String
  seq : Nat
  hash : String
  deriving DecidableEq, Repr

structure Alternative where
  name : String
  label : String
  kind : Option String
  inaction : Bool
  deriving DecidableEq, Repr

structure Quantity where
  name : String
  label : String
  tag : String
  kind : Option String
  deriving DecidableEq, Repr

structure Estimate where
  id : String
  seq : Nat
  quantity : String
  lo : Int
  hi : Int
  /-- the estimator's name; `""` when missing (`EstimateProvenance … estimator`) -/
  estimator : String
  /-- `none` when missing (`EstimateProvenance … support`) -/
  support : Option Support
  supersedes : Option String
  deriving DecidableEq, Repr

structure Setting where
  id : String
  quantity : String
  value : Int
  alternative : String
  deriving DecidableEq, Repr

structure Condition where
  id : String
  action : String
  harm : String
  form : Form
  cond : Cond
  author : String
  support : Option Support

structure Statement where
  id : String
  action : String
  harm : String
  stated : Stated
  author : String
  support : Option Support
  deriving DecidableEq, Repr

structure Fact where
  predicate : String
  args : List String
  entry : String
  deriving DecidableEq, Repr

structure Decision where
  id : String
  /-- the decision entry's (4.4 A1) -/
  seq : Nat
  /-- the decision entry's -/
  day : Int
  chooser : String
  chooserLabel : String
  /-- `(environment_id, document_hash)` -/
  policy : String × String
  alternatives : List Alternative
  quantities : List Quantity
  /-- the cited estimates, lowered; none withdrawn (4.4 A2) -/
  estimates : List Estimate
  settings : List Setting
  conditions : List Condition
  statements : List Statement
  facts : List Fact
  cited : List Cited
  /-- problems found while decoding contents, with the validation step (1 to 11) that reports them -/
  issues : List (Nat × String)

/-! ## Log entries (3.3) -/

inductive EntryKind | estimate | setting | condition | statement | supersession | instruction | decision | taken | outcome
  deriving DecidableEq, Repr

def EntryKind.name : EntryKind → String
  | .estimate => "estimate"
  | .setting => "setting"
  | .condition => "condition"
  | .statement => "statement"
  | .supersession => "supersession"
  | .instruction => "instruction"
  | .decision => "decision"
  | .taken => "taken"
  | .outcome => "outcome"

def EntryKind.ofString : String → Option EntryKind
  | "estimate" => some .estimate
  | "setting" => some .setting
  | "condition" => some .condition
  | "statement" => some .statement
  | "supersession" => some .supersession
  | "instruction" => some .instruction
  | "decision" => some .decision
  | "taken" => some .taken
  | "outcome" => some .outcome
  | _ => none

structure Entry where
  seq : Nat
  day : Int
  id : String
  kind : EntryKind
  content : Json
  prev : String
  hash : String

abbrev Log := List Entry

/-- The W6 day of a coordinate, `YYYY-MM-DD`. -/
def dayString (d : Int) : String :=
  match VE.Time.civilOf d.toNat with
  | some D => if 0 ≤ d then D.iso else ""
  | none => ""

def entryJson (x : Entry) : Json :=
  Json.mkObj [("seq", toJson x.seq), ("day", .str (dayString x.day)), ("id", .str x.id), ("kind", .str x.kind.name),
    ("content", x.content), ("prev", .str x.prev)]

/-- 3.3: SHA-256 of the canonical JSON of `{seq, day, id, kind, content, prev}`. A content outside the
canonical wire format has no hash (the result is not a hexadecimal digest, so it matches no hash field). -/
def entryHash (x : Entry) : String :=
  match VE.CertificateWire.canonical 257 (entryJson x) with
  | .ok text => VE.CertificateWire.sha256 text.toUTF8
  | .error _ => "!"

/-- Some entry of `es` with `seq < k` is a supersession naming `id`, or an estimate whose `supersedes` is `id`. -/
def withdrawnBefore (es : Log) (k : Nat) (id : String) : Bool :=
  es.any fun x => decide (x.seq < k) &&
    ((x.kind == .supersession && x.content.getObjValD "estimate" == .str id) ||
     (x.kind == .estimate && x.content.getObjValD "supersedes" == .str id))

/-! ## The decision record's JSON (3.3) -/

structure RecordRaw where
  id : String
  chooser : String
  chooserLabel : String
  policy : String × String
  alternatives : List Alternative
  quantities : List Quantity
  cites : List Cited
  facts : List Fact

def recordError (field : String) : String := s!"InvalidInput: risk-decision.{field}"

def optStr (j : Json) (field : String) (what : String) : Except String (Option String) :=
  match j.getObjVal? field with
  | .error _ => pure none
  | .ok (.str s) => pure (some s)
  | .ok _ => throw (recordError what)

def reqStr (j : Json) (field : String) (what : String) : Except String String :=
  match j.getObjValD field with
  | .str s => pure s
  | _ => throw (recordError what)

def reqNat (j : Json) (field : String) (what : String) : Except String Nat :=
  match (j.getObjValD field).getNat? with
  | .ok n => pure n
  | .error _ => throw (recordError what)

def arrayOf (j : Json) (what : String) : Except String (List Json) :=
  match j with
  | .arr xs => pure xs.toList
  | _ => throw (recordError what)

def keysIn (j : Json) (required optional : List String) (what : String) : Except String Unit := do
  let keys ← match fields j with
    | .ok fs => pure (fs.map Prod.fst)
    | .error _ => throw (recordError what)
  unless required.all keys.contains && keys.all (fun k => required.contains k || optional.contains k) do
    throw (recordError what)

def decodeRecord (j : Json) : Except String RecordRaw := do
  keysIn j ["format", "id", "chooser", "chooser_label", "policy", "alternatives", "quantities", "cites", "facts"] []
    "record"
  unless j.getObjValD "format" == .str "ve-risk-decision@0" do throw (recordError "format")
  let id ← reqStr j "id" "id"
  let chooser ← reqStr j "chooser" "chooser"
  let chooserLabel ← reqStr j "chooser_label" "chooser_label"
  let p := j.getObjValD "policy"
  keysIn p ["environment_id", "document_hash"] [] "policy"
  let policy := (← reqStr p "environment_id" "policy", ← reqStr p "document_hash" "policy")
  let alts ← (← arrayOf (j.getObjValD "alternatives") "alternatives").mapM fun a => do
    keysIn a ["name", "label"] ["kind", "inaction"] "alternatives"
    let inaction ← match a.getObjVal? "inaction" with
      | .error _ => pure false
      | .ok (.bool b) => pure b
      | .ok _ => throw (recordError "alternatives")
    pure (⟨← reqStr a "name" "alternatives", ← reqStr a "label" "alternatives",
      ← optStr a "kind" "alternatives", inaction⟩ : Alternative)
  let qs ← (← arrayOf (j.getObjValD "quantities") "quantities").mapM fun q => do
    keysIn q ["name", "label", "tag"] ["kind"] "quantities"
    pure (⟨← reqStr q "name" "quantities", ← reqStr q "label" "quantities", ← reqStr q "tag" "quantities",
      ← optStr q "kind" "quantities"⟩ : Quantity)
  let cites ← (← arrayOf (j.getObjValD "cites") "cites").mapM fun c => do
    keysIn c ["id", "seq", "hash"] [] "cites"
    pure (⟨← reqStr c "id" "cites", ← reqNat c "seq" "cites", ← reqStr c "hash" "cites"⟩ : Cited)
  let facts ← (← arrayOf (j.getObjValD "facts") "facts").mapM fun f => do
    keysIn f ["predicate", "args", "entry"] [] "facts"
    let args ← match strings (f.getObjValD "args") with
      | .ok xs => pure xs
      | .error _ => throw (recordError "facts")
    pure (⟨← reqStr f "predicate" "facts", args, ← reqStr f "entry" "facts"⟩ : Fact)
  pure ⟨id, chooser, chooserLabel, policy, alts, qs, cites, facts⟩

/-! ## Units and conditions (3.2, 4.2) -/

/-- The exponent `k` of a tag's scale `10^k` (the reserved `dimensionless` tag has scale 1). -/
def scaleOf (R : RiskDoc) (tag : String) : Option Nat :=
  if tag = "dimensionless" then some 0 else VE.Bridge.lookup R.units tag

def precisionText (R : RiskDoc) (tag : String) : String :=
  s!"UnitPrecision({tag}, scale={10 ^ (scaleOf R tag).getD 0})"

/-- A W6 decimal string lowered onto the tag's grid; the error is W6's text. -/
def lowerDecimal (R : RiskDoc) (tag : String) (s : String) : Except String Int := do
  let some k := scaleOf R tag | throw s!"UnknownSymbol: unit {tag}"
  let d ← match VE.Time.parseDecimal s with
    | .ok d => pure d
    | .error e => throw e
  match VE.Time.lower d k with
  | some v => pure v
  | none => throw (precisionText R tag)

/-- An elaboration failure with the validation step that reports it (0: malformed input). -/
abbrev Elab := Except (Nat × String)

def LinForm.add (f g : LinForm) : LinForm := ⟨f.coeffs ++ g.coeffs, f.const + g.const⟩
def LinForm.scale (k : Int) (f : LinForm) : LinForm := ⟨f.coeffs.map (fun (q, c) => (q, k * c)), k * f.const⟩
def LinForm.sub (f g : LinForm) : LinForm := f.add (g.scale (-1))

def malformed : Nat × String := (0, recordError "condition")

/-- A term of 3.2: its tag and its linear form (uncollected). -/
def elabTerm (R : RiskDoc) (qs : List Quantity) : Nat → Json → Elab (String × LinForm)
  | 0, _ => throw malformed
  | n + 1, j => do
    let items ← match j with
      | .arr xs => pure xs.toList
      | _ => throw malformed
    match items with
    | [.str "quantity", .str q] =>
      match qs.find? (·.name == q) with
      | some qd => pure (qd.tag, ⟨[(q, 1)], 0⟩)
      | none => throw (1, s!"UnknownSymbol: quantity {q}")
    | [.str "decimal", .str tag, .str s] =>
      match lowerDecimal R tag s with
      | .ok v => pure (tag, ⟨[], v⟩)
      | .error e => throw (7, e)
    | [.str "add", .str tag, a, b] => do
      let (ta, fa) ← elabTerm R qs n a
      let (tb, fb) ← elabTerm R qs n b
      unless ta == tag do throw (7, s!"UnitMismatch({tag},{ta})")
      unless tb == tag do throw (7, s!"UnitMismatch({tag},{tb})")
      pure (tag, fa.add fb)
    | [.str "scale", .str tag, .str k, a] => do
      let c ← match VE.Order.Wire.decodeInt k with
        | .ok c => pure c
        | .error _ => throw malformed
      let (ta, fa) ← elabTerm R qs n a
      unless ta == tag do throw (7, s!"UnitMismatch({tag},{ta})")
      pure (tag, fa.scale c)
    | _ => throw malformed

def elabCond (R : RiskDoc) (qs : List Quantity) : Nat → Json → Elab Cond
  | 0, _ => throw malformed
  | n + 1, j => do
    let items ← match j with
      | .arr xs => pure xs.toList
      | _ => throw malformed
    match items with
    | [.str "top"] => pure .top
    | [.str "bottom"] => pure .bottom
    | [.str "not", a] => pure (.not (← elabCond R qs n a))
    | [.str "and", a, b] => pure (.and (← elabCond R qs n a) (← elabCond R qs n b))
    | [.str "or", a, b] => pure (.or (← elabCond R qs n a) (← elabCond R qs n b))
    | [.str op, a, b] =>
      let rel ← match op with
        | "lt" => pure Rel.lt
        | "le" => pure Rel.le
        | "eq" => pure Rel.eq
        | _ => throw malformed
      let (ta, fa) ← elabTerm R qs n a
      let (tb, fb) ← elabTerm R qs n b
      unless ta == tb do throw (7, s!"UnitMismatch({ta},{tb})")
      pure (.atom (NormLinForm.mk' (fa.sub fb)) rel)
    | _ => throw malformed

def Cond.nodes : Cond → Nat
  | .top | .bottom => 1
  | .atom f _ => 1 + f.val.coeffs.length
  | .and a b | .or a b => 1 + a.nodes + b.nodes
  | .not a => 1 + a.nodes

/-! ## Building the admitted record -/

def supportOf (j : Json) (what : String) : Except String (Option Support) :=
  match j.getObjVal? "support" with
  | .error _ => pure none
  | .ok (.str s) => match Support.ofString s with
    | some x => pure (some x)
    | none => throw (recordError what)
  | .ok _ => throw (recordError what)

/-- The decoded content of a cited entry, or the issues it raises. -/
inductive Item
  | estimate (e : Estimate)
  | setting (s : Setting)
  | condition (c : Condition)
  | statement (s : Statement)
  | other
  | issue (step : Nat) (text : String)

def decodeItem (R : RiskDoc) (qs : List Quantity) (x : Entry) : Except String Item := do
  let c := x.content
  match x.kind with
  | .estimate =>
    keysIn c ["quantity", "lo", "hi", "method", "basis"] ["estimator", "support", "supersedes"] "estimate"
    let q ← reqStr c "quantity" "estimate"
    let lo ← reqStr c "lo" "estimate"
    let hi ← reqStr c "hi" "estimate"
    let estimator ← match c.getObjVal? "estimator" with
      | .error _ => pure ""
      | .ok e => do
        keysIn e ["name"] ["version"] "estimator"
        reqStr e "name" "estimator"
    let support ← supportOf c "estimate"
    let supersedes ← optStr c "supersedes" "estimate"
    match qs.find? (·.name == q) with
    | none => pure (.issue 1 s!"UnknownSymbol: quantity {q}")
    | some qd =>
      match lowerDecimal R qd.tag lo, lowerDecimal R qd.tag hi with
      | .ok l, .ok h => pure (.estimate ⟨x.id, x.seq, q, l, h, estimator, support, supersedes⟩)
      | .error e, _ | _, .error e => pure (.issue 3 e)
  | .setting =>
    keysIn c ["quantity", "value", "alternative"] [] "setting"
    let q ← reqStr c "quantity" "setting"
    let v ← reqStr c "value" "setting"
    let a ← reqStr c "alternative" "setting"
    match qs.find? (·.name == q) with
    | none => pure (.issue 1 s!"UnknownSymbol: quantity {q}")
    | some qd => match lowerDecimal R qd.tag v with
      | .ok value => pure (.setting ⟨x.id, q, value, a⟩)
      | .error e => pure (.issue 4 e)
  | .condition =>
    keysIn c ["action", "harm", "form", "condition", "author", "support"] ["note"] "condition"
    let form ← match c.getObjValD "form" with
      | .str "sufficient" => pure Form.sufficient
      | .str "necessary" => pure Form.necessary
      | .str "exact" => pure Form.exact
      | _ => throw (recordError "condition")
    match elabCond R qs 64 (c.getObjValD "condition") with
    | .ok cond =>
      if cond.nodes > maxNodes then throw "ResourceLimit: risk condition nodes"
      pure (.condition ⟨x.id, ← reqStr c "action" "condition", ← reqStr c "harm" "condition", form, cond,
        ← reqStr c "author" "condition", ← supportOf c "condition"⟩)
    | .error (0, e) => throw e
    | .error (step, e) => pure (.issue step e)
  | .statement =>
    keysIn c ["action", "harm", "stated", "author", "support"] ["note"] "statement"
    let action ← reqStr c "action" "statement"
    let harm ← reqStr c "harm" "statement"
    let author ← reqStr c "author" "statement"
    let support ← supportOf c "statement"
    match c.getObjValD "stated" with
    | .str "leads" => pure (.statement ⟨x.id, action, harm, .leads, author, support⟩)
    | .str "cannot" => pure (.statement ⟨x.id, action, harm, .cannot, author, support⟩)
    | .str "might" => pure (.statement ⟨x.id, action, harm, .might, author, support⟩)
    | .str other => pure (.issue 6 s!"RiskStatementForm: {other}")
    | _ => throw (recordError "statement")
  | _ => pure .other

/-- The entry of `es` a citation names (id and sequence number). -/
def citedEntry (es : Log) (c : Cited) : Option Entry := es.find? (fun x => x.id == c.id && x.seq == c.seq)

def itemsEstimates (items : List Item) : List Estimate := items.filterMap fun | .estimate e => some e | _ => none
def itemsSettings (items : List Item) : List Setting := items.filterMap fun | .setting s => some s | _ => none
def itemsConditions (items : List Item) : List Condition := items.filterMap fun | .condition c => some c | _ => none
def itemsStatements (items : List Item) : List Statement := items.filterMap fun | .statement s => some s | _ => none
def itemsIssues (items : List Item) : List (Nat × String) := items.filterMap fun | .issue k t => some (k, t) | _ => none

def buildDecision (R : RiskDoc) (dx : Entry) (r : RecordRaw) (es : Log) : Except String Decision :=
  match (r.cites.filterMap (citedEntry es)).mapM (decodeItem R r.quantities) with
  | .error e => .error e
  | .ok items =>
    if (itemsEstimates items).length + (itemsSettings items).length > 64 then
      .error "ResourceLimit: risk estimates and settings"
    else if (itemsConditions items).length + (itemsStatements items).length > 128 then
      .error "ResourceLimit: risk conditions and statements"
    else .ok ⟨r.id, dx.seq, dx.day, r.chooser, r.chooserLabel, r.policy, r.alternatives, r.quantities,
      itemsEstimates items, itemsSettings items, itemsConditions items, itemsStatements items, r.facts, r.cites,
      itemsIssues items⟩

/-! ## Admission (4.4 A1 to A3) -/

/-- A2 for one citation, in the order `HindsightEntry`, `MissingEntry`, `AlteredEntry`, `WithdrawnEntry`. -/
def citeFailure (dx : Entry) (es : Log) (c : Cited) : Option String :=
  if dx.seq ≤ c.seq then some s!"HindsightEntry: {c.id}"
  else match citedEntry es c with
    | none => some s!"MissingEntry: {c.id}"
    | some x =>
      if !(entryHash x == x.hash && x.hash == c.hash) then some s!"AlteredEntry: {c.id}"
      else if withdrawnBefore es dx.seq c.id then some s!"WithdrawnEntry: {c.id}"
      else none

/-- A3: every fact cites an instruction or statement entry that the record also cites. -/
def factFailure (r : RecordRaw) (es : Log) : Option String :=
  r.facts.findSome? fun f =>
    match r.cites.find? (·.id == f.entry) with
    | some c => match citedEntry es c with
      | some x => if x.kind == .instruction || x.kind == .statement then none else some (recordError "facts")
      | none => some (recordError "facts")
    | none => some (recordError "facts")

/-- A1's per-decision limits (9), except the margin-candidate limit (4.9). -/
def limitFailure (R : RiskDoc) (r : RecordRaw) : Option String :=
  if r.alternatives.length > 16 then some "ResourceLimit: risk alternatives"
  else if (harms R).length > 32 then some "ResourceLimit: risk harms"
  else none

/-- 4.4 A1 to A3, the texts of 6: `dx` is the decision entry; `es` the supplied entries, or the log prefix. -/
def admitDecision (R : RiskDoc) (dx : Entry) (es : Log) : Except String Decision :=
  if dx.kind != .decision then .error (recordError "kind")
  else if entryHash dx != dx.hash then .error s!"AlteredEntry: {dx.id}"
  else match decodeRecord dx.content with
    | .error e => .error e
    | .ok r =>
      if r.policy != R.policy then .error "RiskBinding: policy"
      else match limitFailure R r with
        | some e => .error e
        | none => match r.cites.findSome? (citeFailure dx es) with
          | some e => .error e
          | none => match factFailure r es with
            | some e => .error e
            | none => buildDecision R dx r es

theorem buildDecision_fields {R : RiskDoc} {dx : Entry} {r : RecordRaw} {es : Log} {d : Decision}
    (h : buildDecision R dx r es = .ok d) : d.seq = dx.seq ∧ d.cited = r.cites := by
  unfold buildDecision at h
  split at h
  · cases h
  split at h
  · cases h
  split at h
  · cases h
  cases h
  exact ⟨rfl, rfl⟩

theorem citeFailure_none {dx : Entry} {es : Log} {c : Cited} (h : citeFailure dx es c = none) :
    c.seq < dx.seq ∧ (∃ x ∈ es, x.id = c.id ∧ x.seq = c.seq ∧ x.hash = c.hash ∧ entryHash x = x.hash) ∧
    withdrawnBefore es dx.seq c.id = false := by
  unfold citeFailure at h
  split at h
  · cases h
  rename_i hlt
  cases hx : citedEntry es c with
  | none => rw [hx] at h; cases h
  | some x =>
    rw [hx] at h
    simp only at h
    split at h
    · cases h
    rename_i hh
    split at h
    · cases h
    rename_i hw
    have hmem := List.mem_of_find?_eq_some hx
    have hp := List.find?_some hx
    simp only [Bool.and_eq_true, beq_iff_eq] at hp
    simp only [Bool.not_eq_true', Bool.and_eq_false_iff, beq_eq_false_iff_ne, ne_eq, not_or,
      Classical.not_not] at hh
    exact ⟨by omega, ⟨x, hmem, hp.1, hp.2, hh.2, hh.1⟩, by simpa using hw⟩

/-- 4.4: the admitted record takes the decision entry's sequence number, and every citation precedes it,
matches an entry of `es` by id, sequence number and recomputed hash, and names no estimate withdrawn before
the decision among the entries of `es`. -/
theorem admitDecision_sound (R : RiskDoc) (dx : Entry) (es : Log) (d : Decision)
    (h : admitDecision R dx es = .ok d) :
    d.seq = dx.seq ∧ entryHash dx = dx.hash ∧
    ∀ c ∈ d.cited, c.seq < dx.seq ∧
      (∃ x ∈ es, x.id = c.id ∧ x.seq = c.seq ∧ x.hash = c.hash ∧ entryHash x = x.hash) ∧
      withdrawnBefore es dx.seq c.id = false := by
  unfold admitDecision at h
  split at h
  · cases h
  split at h
  · cases h
  rename_i _ hhash
  split at h
  · cases h
  rename_i r _
  split at h
  · cases h
  split at h
  · cases h
  split at h
  · cases h
  rename_i hcites
  split at h
  · cases h
  obtain ⟨hseq, hcited⟩ := buildDecision_fields h
  refine ⟨hseq, by simpa using hhash, fun c hc => ?_⟩
  rw [hcited] at hc
  have := List.findSome?_eq_none_iff.mp hcites c hc
  exact citeFailure_none this

/-! ## The box and the cells (1.4) -/

def names (d : Decision) : List String := d.alternatives.map (·.name)

def estimatesOf (d : Decision) (q : String) : List Estimate := d.estimates.filter (·.quantity == q)
def settingOf (d : Decision) (q : String) : Option Setting := d.settings.find? (·.quantity == q)

/-- The estimate recorded last (largest sequence number; the first among equals). -/
def latestOf : Estimate → List Estimate → Estimate
  | e, [] => e
  | e, x :: xs => latestOf (if e.seq < x.seq then x else e) xs

/-- 1.4: the effective range of the cited estimates of one quantity. Without a combination rule, two
estimates are `ConflictingEstimates` (V5) and the first one's range stands in. -/
def combineRange (comb : Option Combination) : List Estimate → Int × Int
  | [] => (0, 0)
  | [e] => (e.lo, e.hi)
  | e :: es => match comb with
    | some .hull => (es.foldl (fun m x => min m x.lo) e.lo, es.foldl (fun m x => max m x.hi) e.hi)
    | some .intersection => (es.foldl (fun m x => max m x.lo) e.lo, es.foldl (fun m x => min m x.hi) e.hi)
    | some .latest => ((latestOf e es).lo, (latestOf e es).hi)
    | none => (e.lo, e.hi)

def boxEntry (R : RiskDoc) (d : Decision) (q : Quantity) : Option BoxEntry :=
  match settingOf d q.name with
  | some s => some ⟨q.name, q.tag, s.value, s.value⟩
  | none => match estimatesOf d q.name with
    | [] => none
    | es => some ⟨q.name, q.tag, (combineRange R.risk.combination es).1, (combineRange R.risk.combination es).2⟩

/-- 1.4: combination, then settings as points; one entry per quantity with an estimate or a setting. -/
def box (R : RiskDoc) (d : Decision) : Box := ⟨d.quantities.filterMap (boxEntry R d)⟩

def condsOn (d : Decision) (a h : String) : List Condition := d.conditions.filter (fun c => c.action == a && c.harm == h)
def stmtsOn (d : Decision) (a h : String) : List Statement := d.statements.filter (fun s => s.action == a && s.harm == h)

/-- The sufficient sources of a cell: sufficient and exact conditions, then stated `leads` (`⊤`). -/
def suffSources (d : Decision) (a h : String) : List Cond :=
  (condsOn d a h).filterMap (fun c => if c.form == .necessary then none else some c.cond) ++
    (stmtsOn d a h).filterMap (fun s => if s.stated == .leads then some .top else none)

/-- The necessary sources of a cell: necessary and exact conditions, then stated `cannot` (`⊥`). -/
def necSources (d : Decision) (a h : String) : List Cond :=
  (condsOn d a h).filterMap (fun c => if c.form == .sufficient then none else some c.cond) ++
    (stmtsOn d a h).filterMap (fun s => if s.stated == .cannot then some .bottom else none)

def addressed (d : Decision) (a h : String) : Bool := !(condsOn d a h).isEmpty || !(stmtsOn d a h).isEmpty

/-- 2.4: the necessary side of an unaddressed cell. -/
def completion (R : RiskDoc) (h : String) : Cond :=
  match R.risk.unexamined with
  | .possible => .top
  | _ => if (classOf R h).any R.risk.alwaysPossible.contains then .top else .bottom

/-- The sufficient source, else `⊥`. -/
def Suff (_R : RiskDoc) (d : Decision) (a h : String) : Cond := (suffSources d a h).headD .bottom

/-- The necessary source, else `⊤` on an addressed cell or the completion value (4.4). -/
def Nec (R : RiskDoc) (d : Decision) (a h : String) : Cond :=
  match necSources d a h with
  | c :: _ => c
  | [] => if addressed d a h then .top else completion R h

def Completed (R : RiskDoc) (d : Decision) (v : Valuation) (H : String → String → Bool) : Prop :=
  InBox (box R d) v ∧ ∀ a ∈ names d, ∀ h ∈ harms R,
    ((Suff R d a h).holds v → H a h = true) ∧ (H a h = true → (Nec R d a h).holds v)

/-- Every cell `(alternative, harm constant)`, alternatives first. -/
def cellsOf (R : RiskDoc) (d : Decision) : List (String × String) := (names d).flatMap fun a => (harms R).map (a, ·)

structure Tables where
  might : List (String × String)
  leads : List (String × String)
  /-- the canonical witness of every might cell -/
  witness : List ((String × String) × Valuation)

/-- 4.4: `might` by `possibleE` of the necessary side, `leads` by `certainE` of the sufficient side. -/
def regenerate (R : RiskDoc) (d : Decision) : Tables :=
  { might := (cellsOf R d).filter (fun (a, h) => possibleE (box R d) (Nec R d a h))
    leads := (cellsOf R d).filter (fun (a, h) => certainE (box R d) (Suff R d a h))
    witness := (cellsOf R d).filterMap fun (a, h) => (witnessE (box R d) (Nec R d a h)).map ((a, h), ·) }

/-! ## The observations validation reads (4.4, 4.9) -/

/-- The first non-point quantity that occurs in two atoms of `nnf c`. -/
def sharedName (b : Box) (c : Cond) : Option String :=
  (nnf c).atomNames.find? (fun q => !b.isPoint q && decide ((nnf c).atomNames.count q > 1))

def atomsOf : Cond → List (NormLinForm × Rel)
  | .top | .bottom => []
  | .atom f r => [(f, r)]
  | .and a b | .or a b => atomsOf a ++ atomsOf b
  | .not a => atomsOf a

/-- The first non-point quantity with a coefficient other than ±1 in an `=` or `≠` atom of `nnf c`. -/
def unitBad (b : Box) (c : Cond) : Option String :=
  (atomsOf (nnf c)).findSome? fun (f, r) =>
    if r == .eq || r == .ne then
      (f.val.coeffs.find? (fun p => !b.isPoint p.1 && p.2 != 1 && p.2 != -1)).map (·.1)
    else none

structure CondObs where
  inScope : Bool
  shared : Option String
  unitBad : Option String

structure CellObs where
  cell : String × String
  /-- the sufficient side is scoped, separable and unit-coefficient on the box -/
  suffOK : Bool
  necOK : Bool
  /-- `S` and `N` are the same condition -/
  same : Bool
  snScoped : Bool
  snShared : Option String
  snPossible : Bool
  might : Bool
  leads : Bool

structure Obs where
  /-- per cited estimate: `lo ≤ hi` -/
  range : List Bool
  /-- per quantity: the intersection of its estimates is nonempty -/
  nonEmpty : List Bool
  boxWF : Bool
  conds : List CondObs
  cells : List CellObs

def condOK (b : Box) (c : Cond) : Bool := Scoped b c && Separable b c && UnitCoefficients b c

def cellObs (R : RiskDoc) (d : Decision) (b : Box) (a h : String) : CellObs :=
  let S := Suff R d a h
  let N := Nec R d a h
  let SN := Cond.and S (.not N)
  ⟨(a, h), condOK b S, condOK b N, decide (S = N), Scoped b SN, sharedName b SN, possibleE b SN,
    possibleE b N, certainE b S⟩

def boxWFB (b : Box) : Bool := decide (b.entries.map (·.name)).Nodup && b.entries.all (fun e => decide (e.lo ≤ e.hi))

def intersects (es : List Estimate) : Bool :=
  decide ((es.map (·.lo)).foldl max ((es.head?.map (·.lo)).getD 0) ≤ (es.map (·.hi)).foldl min ((es.head?.map (·.hi)).getD 0))

def obs (R : RiskDoc) (d : Decision) : Obs :=
  let b := box R d
  { range := d.estimates.map (fun e => decide (e.lo ≤ e.hi))
    nonEmpty := d.quantities.map (fun q => intersects (estimatesOf d q.name))
    boxWF := boxWFB b
    conds := d.conditions.map fun c => ⟨Scoped b c.cond, sharedName b c.cond, unitBad b c.cond⟩
    cells := (cellsOf R d).map fun (a, h) => cellObs R d b a h }

/-- The record with its estimate values erased: everything validation reads besides the observations. -/
def strip (d : Decision) : Decision := { d with estimates := d.estimates.map fun e => { e with lo := 0, hi := 0 } }

structure View where
  strip : Decision
  obs : Obs

def view (R : RiskDoc) (d : Decision) : View := ⟨strip d, obs R d⟩

def mightOfView (v : View) : List (String × String) := (v.obs.cells.filter (·.might)).map (·.cell)
def leadsOfView (v : View) : List (String × String) := (v.obs.cells.filter (·.leads)).map (·.cell)

/-! ## The decision model (4.4) -/

def genPredList (R : RiskDoc) : List (String × List String) :=
  [(mightName, [R.alt.action, R.alt.harm]), (classPred, [R.alt.harm, R.sev]), (moreSeverePred, [R.sev, R.sev])]

/-- Its environment is `envAt (inlineTree (toAlt R)) 0` (`modelVocabulary_valid`). -/
def modelVocabulary (R : RiskDoc) : VE.Bridge.Vocabulary :=
  ⟨R.vocab.sorts ++ [R.sev],
   genPredList R ++ R.vocab.predicates.filter (fun p => !(layerNames (inlineTree (toAlt R)).T).contains p.1),
   R.classes.map (·, R.sev) ++ R.vocab.constants⟩

def constsOfSort (R : RiskDoc) (s : String) : List String :=
  (R.vocab.constants.filter (·.2 == s)).map Prod.fst

/-- The constant table: every constant of `E_risk`, then the record-local names (4.4). -/
def constTable (R : RiskDoc) (d : Decision) : List (String × VE.Bridge.Entity) :=
  R.classes.map (fun c => (c, (R.sev, c))) ++ R.vocab.constants.map (fun (c, s) => (c, (s, c))) ++
    [(d.chooser, (R.alt.chooser, d.chooser))] ++ d.alternatives.map (fun a => (a.name, (R.alt.action, a.name)))

def entityIn (R : RiskDoc) (d : Decision) (x : String) : VE.Bridge.Entity :=
  (VE.Bridge.lookup (constTable R d) x).getD ("", x)

def pairRows (R : RiskDoc) (cells : List (String × String)) : List (List VE.Bridge.Entity) :=
  cells.map fun (a, h) => [(R.alt.action, a), (R.alt.harm, h)]

def factRows (R : RiskDoc) (d : Decision) : List (String × List (List VE.Bridge.Entity)) :=
  let preds := (d.facts.map (·.predicate)).eraseDups
  preds.map fun p => (p, (d.facts.filter (·.predicate == p)).map (fun f => f.args.map (entityIn R d)))

def dataCore (R : RiskDoc) (d : Decision) (might leads : List (String × String)) : VE.Bridge.ModelData :=
  let domains := (R.vocab.sorts ++ [R.sev]).map fun s =>
    if s = R.alt.chooser then (s, d.chooser :: constsOfSort R s)
    else if s = R.alt.action then (s, names d)
    else if s = R.alt.harm then (s, harms R)
    else if s = R.sev then (s, R.classes)
    else (s, constsOfSort R s)
  let inaction := match R.alt.inaction with
    | some p => [(p, (d.alternatives.filter (·.inaction)).map (fun a => [(R.alt.action, a.name)]))]
    | none => []
  ⟨domains, constTable R d,
   [(R.alt.leadsTo, pairRows R leads), (mightName, pairRows R might),
    (R.alt.available, d.alternatives.map (fun a => [(R.alt.action, a.name), (R.alt.chooser, d.chooser)])),
    (classPred, R.risk.harmClasses.map (fun (h, c) => [(R.alt.harm, h), (R.sev, c)])),
    (moreSeverePred, (closure R).map (fun (c, c') => [(R.sev, c), (R.sev, c')]))] ++ inaction ++ factRows R d⟩

def dataOfView (R : RiskDoc) (v : View) : VE.Bridge.ModelData := dataCore R v.strip (mightOfView v) (leadsOfView v)

def decisionData (R : RiskDoc) (d : Decision) : VE.Bridge.ModelData := dataOfView R (view R d)

def modelAdmissible (R : RiskDoc) (d : Decision) : Bool := (decisionData R d).valid (modelVocabulary R)

def decisionModel (R : RiskDoc) (d : Decision) : VE.FiniteModel VE.Bridge.Entity := (decisionData R d).toModel

def supportName (_R : RiskDoc) (d : Decision) (a h : String) : String :=
  match (condsOn d a h).head? with
  | some _ => "calculation"
  | none => match (stmtsOn d a h).head? with
    | some s => (s.support.map Support.name).getD "assumption"
    | none => "assumption"

def rowsOfView (R : RiskDoc) (v : View) : List Row :=
  v.obs.cells.map fun o => ⟨o.cell.1, o.cell.2, o.leads, supportName R v.strip o.cell.1 o.cell.2⟩

/-- One signed row per cell, named by the alternative and the harm constant. -/
def decisionRows (R : RiskDoc) (d : Decision) : List Row := rowsOfView R (view R d)

/-- The named rows of `risk__might_lead_to` and `leads_to` in a model. -/
def modelTables (R : RiskDoc) (M : VE.FiniteModel VE.Bridge.Entity) : Tables :=
  let named (p : String) := (M.relations p).filterMap fun t => match t with
    | [a, h] => some (a.2, h.2)
    | _ => none
  ⟨named mightName, named R.alt.leadsTo, []⟩

/-! ## Validation (4.4 V1 to V11) -/

def modelOfView (R : RiskDoc) (v : View) : VE.FiniteModel VE.Bridge.Entity := (dataOfView R v).toModel

/-- The first issue decoding raised for validation step `k`. -/
def issueAt (d : Decision) (k : Nat) : Except String Unit :=
  match d.issues.find? (·.1 == k) with
  | some (_, t) => .error t
  | none => .ok ()

def dupOf (xs : List String) : Option String := xs.find? (fun x => xs.count x > 1)

/-- V1: names, harms, kinds, record-local names and fact predicates. -/
def checkNames (R : RiskDoc) (d : Decision) : Except String Unit := do
  issueAt d 1
  if let some n := dupOf (names d) then throw s!"DuplicateDeclaration: alternative {n}"
  if let some n := dupOf (d.quantities.map (·.name)) then throw s!"DuplicateDeclaration: quantity {n}"
  if R.alt.inaction.isSome then
    match d.alternatives.filter (·.inaction) with
    | [] => throw (VE.Alternatives.modelError s!"{d.chooser} has no inaction")
    | [_] => pure ()
    | a :: b :: _ => throw (VE.Alternatives.modelError s!"{d.chooser} has two inactions: {a.name}, {b.name}")
  for (a, h) in d.conditions.map (fun c => (c.action, c.harm)) ++ d.statements.map (fun s => (s.action, s.harm)) do
    unless (harms R).contains h do throw s!"UnknownHarm: {h}"
    unless (names d).contains a do throw s!"UnknownSymbol: alternative {a}"
  for st in d.settings do
    unless (names d).contains st.alternative do throw s!"UnknownSymbol: alternative {st.alternative}"
  for a in d.alternatives do
    if let some k := a.kind then
      unless (R.risk.alternativeKinds.map Prod.fst).contains k do throw s!"UnknownSymbol: kind {k}"
  for q in d.quantities do
    unless (scaleOf R q.tag).isSome do throw s!"UnknownSymbol: unit {q.tag}"
    if let some k := q.kind then
      match VE.Bridge.lookup R.risk.quantityKinds k with
      | none => throw s!"UnknownSymbol: kind {k}"
      | some t => unless t == q.tag do throw s!"UnitMismatch({t},{q.tag})"
  let constants := R.classes ++ R.vocab.constants.map Prod.fst
  let actionConsts := constsOfSort R R.alt.action
  if constants.contains d.chooser then throw s!"RiskConstant: {d.chooser}"
  for a in d.alternatives do
    if a.name == d.chooser then throw s!"RiskConstant: {a.name}"
    if constants.contains a.name && !actionConsts.contains a.name then throw s!"RiskConstant: {a.name}"
  let layer := layerNames (inlineTree (toAlt R)).T
  for f in d.facts do
    let p := f.predicate
    unless (VE.Bridge.lookup R.vocab.predicates p).isSome && !layer.contains p &&
        !(VE.Alternatives.roleNames R.alt).contains p && !generatedPreds.contains p do
      throw s!"RiskFact: {p}"

/-- V2. -/
def checkRequired (R : RiskDoc) (d : Decision) : Except String Unit := do
  let kinds := d.alternatives.filterMap (·.kind)
  for (w, reqs) in R.risk.requiredAlternatives do
    if kinds.contains w then
      for k in reqs do
        unless kinds.contains k do throw s!"RequiredAlternativeMissing: {k} (with {w})"

/-- V3. -/
def checkEstimates (R : RiskDoc) (v : View) : Except String Unit := do
  let d := v.strip
  issueAt d 3
  for (e, ok) in d.estimates.zip v.obs.range do
    unless ok do throw s!"RiskRange: {e.id}"
    if e.estimator == "" then throw s!"EstimateProvenance: {e.id} estimator"
    if e.support.isNone then throw s!"EstimateProvenance: {e.id} support"
    let kind := (d.quantities.find? (·.name == e.quantity)).bind (·.kind)
    if let some k := kind then
      if let some allowed := VE.Bridge.lookup R.risk.requiredEstimators k then
        unless allowed.contains e.estimator do throw s!"EstimatorNotAllowed: {e.id} {e.estimator}"

/-- V4. -/
def checkSettings (d : Decision) : Except String Unit := do
  issueAt d 4
  for q in d.quantities do
    let n := (d.settings.filter (·.quantity == q.name)).length
    if n > 1 || (n == 1 && !(estimatesOf d q.name).isEmpty) then throw s!"RiskSettingTwice: {q.name}"
  for c in d.conditions do
    for q in c.cond.atomNames do
      if let some st := settingOf d q then
        unless st.alternative == c.action do throw s!"RiskSettingScope: {st.id} {c.action}"

/-- V5. -/
def checkCombination (R : RiskDoc) (v : View) : Except String Unit := do
  let d := v.strip
  for (q, ok) in d.quantities.zip v.obs.nonEmpty do
    if (estimatesOf d q.name).length > 1 then
      match R.risk.combination with
      | none => throw s!"ConflictingEstimates: {q.name}"
      | some .intersection => unless ok do throw s!"RiskInconsistent: {q.name} estimates do not intersect"
      | some _ => pure ()
  for c in d.conditions do
    for q in c.cond.atomNames do
      unless (settingOf d q).isSome || !(estimatesOf d q).isEmpty do throw s!"RiskUnestimated: {q}"

/-- V6. -/
def checkSources (R : RiskDoc) (d : Decision) : Except String Unit := do
  issueAt d 6
  for (a, h) in cellsOf R d do
    if (suffSources d a h).length > 1 then throw s!"RiskTwoSources: {a}/{h} sufficient"
    if (necSources d a h).length > 1 then throw s!"RiskTwoSources: {a}/{h} necessary"

/-- V7. -/
def checkConditions (v : View) : Except String Unit := do
  let d := v.strip
  issueAt d 7
  for (c, o) in d.conditions.zip v.obs.conds do
    unless o.inScope do throw s!"RiskUnestimated: {c.id}"
    if let some q := o.shared then throw s!"RiskConditionShared: {q}"
    if let some q := o.unitBad then throw s!"RiskEqualityCoefficient: {c.id} {q}"

/-- Whether the cell's first sufficient (necessary) source is a condition rather than a stated cell. -/
def suffIsCondition (d : Decision) (a h : String) : Bool := (condsOn d a h).any (·.form != .necessary)
def necIsCondition (d : Decision) (a h : String) : Bool := (condsOn d a h).any (·.form != .sufficient)

/-- V8 and V9 (the witness case is rendered by the route). -/
def checkCells (v : View) : Except String Unit := do
  let d := v.strip
  for o in v.obs.cells do
    let (a, h) := o.cell
    unless o.same do
      if let some q := o.snShared then throw s!"RiskConditionShared: {q}"
      if o.snPossible then
        if suffIsCondition d a h && necIsCondition d a h then throw s!"SufficientOutsideNecessary: {a}/{h}"
        else throw s!"RiskInconsistent: {a}/{h}"
  for o in v.obs.cells do
    let (a, h) := o.cell
    if (stmtsOn d a h).any (·.stated == .might) && !o.might then throw s!"RiskInconsistent: {a}/{h}"

/-- V10: model validity, with its diagnostics. -/
def checkModel (R : RiskDoc) (v : View) : Except String Unit := do
  let d := v.strip
  for c in constsOfSort R R.alt.action do
    unless (names d).contains c do throw s!"RiskConstant: {c}"
  let M := modelOfView R v
  let ps := (modelVocabulary R).environment.predicates
  for f in d.facts do
    match ps f.predicate with
    | some ss => unless VE.Bridge.tupleCheck M ss (f.args.map (entityIn R d)) &&
        f.args.all (fun x => (VE.Bridge.lookup (constTable R d) x).isSome) do throw s!"RiskFact: {f.predicate}"
    | none => throw s!"RiskFact: {f.predicate}"
  unless (dataOfView R v).valid (modelVocabulary R) do throw "InvalidInput: risk decision model"

/-- V11: alt's validation of the regenerated model (premises, rows, E1 to E3, `Γ`), then the risk premises. -/
def checkAlternatives (R : RiskDoc) (v : View) : Except String Unit := do
  let M := modelOfView R v
  VE.Alternatives.validateAlternativesWith R.labels (toAlt R) M (rowsOfView R v)
  unless (riskPremises R).all (fun p => p.eval M []) do throw "InvalidInput: a risk premise fails on the decision model"

def cellGate (o : CellObs) : Bool := o.suffOK && o.necOK && (o.same || (o.snScoped && !o.snPossible))

/-- The conditions the theorems use, as one Boolean (reached after every diagnostic). -/
def viewGate (R : RiskDoc) (v : View) : Bool :=
  v.obs.boxWF && v.obs.cells.all cellGate &&
  (dataOfView R v).valid (modelVocabulary R) &&
  VE.Alternatives.altModelChecks (toAlt R) (modelOfView R v) (rowsOfView R v) &&
  (riskPremises R).all (fun p => p.eval (modelOfView R v) [])

def checkView (R : RiskDoc) (v : View) : Except String Unit := do
  checkNames R v.strip
  checkRequired R v.strip
  checkEstimates R v
  checkSettings v.strip
  checkCombination R v
  checkSources R v.strip
  checkConditions v
  checkCells v
  checkModel R v
  checkAlternatives R v

def validateView (R : RiskDoc) (v : View) : Except String Unit :=
  match checkView R v with
  | .error e => .error e
  | .ok () => if viewGate R v then .ok () else .error "InvalidInput: risk decision record is not valid"

/-- 4.4 V1 to V11 on an admitted record, the texts of 6. -/
def validateDecision (R : RiskDoc) (d : Decision) : Except String Unit := validateView R (view R d)

theorem viewGate_of_validate {R : RiskDoc} {v : View} (h : validateView R v = .ok ()) : viewGate R v = true := by
  unfold validateView at h
  split at h
  · cases h
  · split at h
    · assumption
    · cases h

/-! ## Statuses (4.8) -/

structure Status where
  permitted : Bool
  required : Bool
  clear : Bool
  deriving DecidableEq, Repr

def statusesOfView (R : RiskDoc) (v : View) : List (String × Status) :=
  let M := modelOfView R v
  let r : VE.Bridge.Entity := (R.alt.chooser, v.strip.chooser)
  v.strip.alternatives.map fun a =>
    let x : VE.Bridge.Entity := (R.alt.action, a.name)
    (a.name, ⟨VE.Alternatives.permittedAt (toAlt R) M x, VE.Alternatives.requiredAt (toAlt R) M x,
      (VE.Alternatives.clearF (toAlt R)).eval M (tupleVal [r, x])⟩)

/-- Per alternative: `permittedAt`, `requiredAt` and `clearF` evaluated on the decision model at the chooser. -/
def statuses (R : RiskDoc) (d : Decision) : List (String × Status) := statusesOfView R (view R d)

/-! ## Theorems (7.2) -/

theorem boxWFB_iff (b : Box) : boxWFB b = true ↔ b.WF := by
  simp [boxWFB, Box.WF]

theorem condOK_iff {b : Box} {c : Cond} :
    condOK b c = true ↔ Scoped b c = true ∧ Separable b c = true ∧ UnitCoefficients b c = true := by
  simp [condOK, and_assoc]

theorem mem_cellsOf {R : RiskDoc} {d : Decision} {a h : String} (ha : a ∈ names d) (hh : h ∈ harms R) :
    (a, h) ∈ cellsOf R d :=
  List.mem_flatMap.mpr ⟨a, ha, List.mem_map.mpr ⟨h, hh, rfl⟩⟩

/-- What a successful validation gives the regeneration theorems. -/
theorem validate_facts {R : RiskDoc} {d : Decision} (hv : validateDecision R d = .ok ()) :
    (box R d).WF ∧ ∀ p ∈ cellsOf R d, cellGate (cellObs R d (box R d) p.1 p.2) = true := by
  have hg := viewGate_of_validate hv
  simp only [viewGate, Bool.and_eq_true, List.all_eq_true] at hg
  obtain ⟨⟨⟨⟨hwf, hcells⟩, _⟩, _⟩, _⟩ := hg
  refine ⟨(boxWFB_iff _).mp hwf, fun p hp => ?_⟩
  exact hcells _ (List.mem_map.mpr ⟨p, hp, rfl⟩)

/-- On a valid record, the sufficient side implies the necessary side at every valuation of the box. -/
theorem suff_nec {R : RiskDoc} {d : Decision} {a h : String}
    (hg : cellGate (cellObs R d (box R d) a h) = true) (v : Valuation) (hv : InBox (box R d) v)
    (hs : (Suff R d a h).holds v) : (Nec R d a h).holds v := by
  simp only [cellGate, cellObs, Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq, Bool.not_eq_true'] at hg
  obtain ⟨⟨_, _⟩, hsame | ⟨hsc, hsn⟩⟩ := hg
  · rw [← hsame]; exact hs
  · refine Classical.byContradiction fun hn => ?_
    have := possibleE_complete (box R d) (.and (Suff R d a h) (.not (Nec R d a h))) hsc ⟨v, hv, hs, hn⟩
    rw [hsn] at this
    cases this

/-- The case that follows `S` everywhere and sets the cell `(a, h)` to `t`. -/
noncomputable def caseAt (R : RiskDoc) (d : Decision) (v : Valuation) (a h : String) (t : Bool) :
    String → String → Bool := by
  classical
  exact fun a' h' => if a' = a ∧ h' = h then t else decide ((Suff R d a' h').holds v)

theorem caseAt_completed {R : RiskDoc} {d : Decision} (hv : validateDecision R d = .ok ()) {v : Valuation}
    (hin : InBox (box R d) v) {a h : String} {t : Bool} (ht1 : (Suff R d a h).holds v → t = true)
    (ht2 : t = true → (Nec R d a h).holds v) : Completed R d v (caseAt R d v a h t) := by
  classical
  obtain ⟨_, hcells⟩ := validate_facts hv
  refine ⟨hin, fun a' ha' h' hh' => ?_⟩
  have hg := hcells _ (mem_cellsOf ha' hh')
  simp only [caseAt]
  by_cases he : a' = a ∧ h' = h
  · obtain ⟨rfl, rfl⟩ := he
    simp only [and_self, if_true]
    exact ⟨ht1, ht2⟩
  · simp only [he, if_false, decide_eq_true_eq]
    exact ⟨id, suff_nec hg v hin⟩

/-- 1.5 and 4.4: the regenerated tables are the completed-case semantics. -/
theorem regenerate_sound (R : RiskDoc) (h : WellFormedRisk R = true) (d : Decision)
    (hv : validateDecision R d = .ok ()) (a hm : String) (ha : a ∈ names d) (hh : hm ∈ harms R) :
    ((a, hm) ∈ (regenerate R d).might ↔ ∃ v H, Completed R d v H ∧ H a hm = true) ∧
    ((a, hm) ∈ (regenerate R d).leads ↔ ∀ v H, Completed R d v H → H a hm = true) := by
  have _ := h
  obtain ⟨hwf, hcells⟩ := validate_facts hv
  have hg := hcells _ (mem_cellsOf ha hh)
  have hg' := hg
  simp only [cellGate, cellObs, Bool.and_eq_true, condOK_iff] at hg'
  obtain ⟨⟨⟨hsq, hss, hsu⟩, ⟨hnq, hns, hnu⟩⟩, _⟩ := hg'
  have hcell := mem_cellsOf (R := R) ha hh
  constructor
  · simp only [regenerate, List.mem_filter, hcell, true_and]
    rw [possibleE_iff _ _ hwf hnq hns hnu]
    constructor
    · rintro ⟨v, hin, hn⟩
      exact ⟨v, caseAt R d v a hm true, caseAt_completed hv hin (fun _ => rfl) (fun _ => hn), by
        classical
        simp [caseAt]⟩
    · rintro ⟨v, H, ⟨hin, hc⟩, hH⟩
      exact ⟨v, hin, (hc a ha hm hh).2 hH⟩
  · simp only [regenerate, List.mem_filter, hcell, true_and]
    rw [certainE_iff _ _ hwf hsq hss hsu]
    constructor
    · intro hall v H ⟨hin, hc⟩
      exact (hc a ha hm hh).1 (hall v hin)
    · intro hall v hin
      refine Classical.byContradiction fun hn => ?_
      have := hall v (caseAt R d v a hm false) (caseAt_completed hv hin (fun hs => absurd hs hn)
        (fun hf => by cases hf))
      classical
      simp [caseAt] at this

theorem certain_within_possible (R : RiskDoc) (h : WellFormedRisk R = true) (d : Decision)
    (hv : validateDecision R d = .ok ()) :
    ∀ p ∈ (regenerate R d).leads, p ∈ (regenerate R d).might := by
  have _ := h
  obtain ⟨hwf, hcells⟩ := validate_facts hv
  intro p hp
  simp only [regenerate, List.mem_filter] at hp ⊢
  obtain ⟨hc, hcert⟩ := hp
  refine ⟨hc, ?_⟩
  have hg := hcells _ hc
  have hg' := hg
  simp only [cellGate, cellObs, Bool.and_eq_true, condOK_iff] at hg'
  obtain ⟨⟨⟨hsq, _, _⟩, ⟨hnq, _, _⟩⟩, _⟩ := hg'
  have hin := box_nonempty hwf
  have hs := certainE_sound _ _ hsq hcert _ hin
  exact possibleE_complete _ _ hnq ⟨_, hin, suff_nec hg _ hin hs⟩

theorem regenerate_witness (R : RiskDoc) (h : WellFormedRisk R = true) (d : Decision)
    (hv : validateDecision R d = .ok ()) (a hm : String) (v : Valuation)
    (hw : ((a, hm), v) ∈ (regenerate R d).witness) :
    ∃ H, Completed R d v H ∧ H a hm = true := by
  have _ := h
  obtain ⟨hwf, hcells⟩ := validate_facts hv
  simp only [regenerate, List.mem_filterMap, Option.map_eq_some_iff, Prod.mk.injEq] at hw
  obtain ⟨⟨a', h'⟩, hc, v', hwit, ⟨rfl, rfl⟩, rfl⟩ := hw
  have hg := hcells _ hc
  have hg' := hg
  simp only [cellGate, cellObs, Bool.and_eq_true, condOK_iff] at hg'
  obtain ⟨⟨_, ⟨hnq, hns, hnu⟩⟩, _⟩ := hg'
  have hp : possibleE (box R d) (Nec R d a' h') = true := by
    unfold witnessE at hwit
    split at hwit
    · assumption
    · cases hwit
  obtain ⟨v'', hv'', hin, hn⟩ := witnessE_sound _ _ hwf hnq hns hnu hp
  rw [hwit] at hv''
  cases hv''
  exact ⟨caseAt R d v' a' h' true, caseAt_completed hv hin (fun _ => rfl) (fun _ => hn), by
    classical
    simp [caseAt]⟩

/-! ### The decision model -/

theorem lookup_append {α : Type} (l m : List (String × α)) (k : String) :
    VE.Bridge.lookup (l ++ m) k = (VE.Bridge.lookup l k).or (VE.Bridge.lookup m k) := by
  induction l with
  | nil => simp [VE.Bridge.lookup]
  | cons x l ih =>
    simp only [VE.Bridge.lookup, List.cons_append, List.find?_cons] at ih ⊢
    split <;> simp_all

theorem lookup_classes (cs : List String) (s k : String) :
    VE.Bridge.lookup (cs.map (·, s)) k = if k ∈ cs then some s else none := by
  induction cs with
  | nil => simp [VE.Bridge.lookup]
  | cons c cs ih =>
    simp only [VE.Bridge.lookup, List.map_cons, List.find?_cons] at ih ⊢
    by_cases hk : c = k
    · subst hk; simp
    · have : (c == k) = false := by simpa using hk
      rw [this]
      simp only [ih, List.mem_cons]
      by_cases hm : k ∈ cs <;> simp [hm, Ne.symm hk]

theorem modelVocabulary_valid {R : RiskDoc} (hv : RiskValid R) (M : VE.FiniteModel VE.Bridge.Entity)
    (h : M.Valid (modelVocabulary R).environment) : M.Valid (envAt (inlineTree (toAlt R)) 0) := by
  have hconst : ∀ c, (envAt (inlineTree (toAlt R)) 0).constants c = (modelVocabulary R).environment.constants c := by
    intro c
    change (riskEnv R).constants c = VE.Bridge.lookup (R.classes.map (·, R.sev) ++ R.vocab.constants) c
    rw [lookup_append, lookup_classes]
    by_cases hc : c ∈ R.risk.severity.classes
    · simp [riskEnv, RiskDoc.classes, hc]
    · simp [riskEnv, RiskDoc.classes, hc, RiskDoc.E, VE.Bridge.Vocabulary.environment]
  refine ⟨fun c s hc => h.1 c s (by rw [← hconst]; exact hc), fun p vs hp => ?_⟩
  obtain ⟨ss, hss, ht⟩ := h.2 p vs hp
  refine ⟨ss, ?_, ht⟩
  change VE.Bridge.lookup (genPredList R ++ R.vocab.predicates.filter _) p = some ss at hss
  rw [lookup_append] at hss
  by_cases hg : p ∈ generatedPreds
  · have hnl := not_layer hv (List.mem_append_left _ hg)
    rw [VE.Norms.envAt_base hnl]
    simp only [generatedPreds, List.mem_cons, List.not_mem_nil, or_false] at hg
    rcases hg with rfl | rfl | rfl
    · simp [genPredList, VE.Bridge.lookup] at hss; rw [← hss]; exact riskEnv_might R
    · simp [genPredList, VE.Bridge.lookup, mightName, classPred] at hss; rw [← hss]; exact riskEnv_class R
    · simp [genPredList, VE.Bridge.lookup, mightName, classPred, moreSeverePred] at hss; rw [← hss]
      exact riskEnv_ms R
  · have hnone : VE.Bridge.lookup (genPredList R) p = none := by
      simp only [generatedPreds, List.mem_cons, List.not_mem_nil, or_false, not_or] at hg
      simp [genPredList, VE.Bridge.lookup, Ne.symm hg.1, Ne.symm hg.2.1, Ne.symm hg.2.2]
    rw [hnone, Option.none_or, VE.Norms.Replay.lookup_filter_not] at hss
    simp only [envAt, VE.Norms.hide, List.drop_zero]
    split at hss
    · cases hss
    · rename_i hl
      simp only [hl, if_false]
      have hr : (riskEnv R).predicates p = R.E.predicates p := by
        simp only [generatedPreds, List.mem_cons, List.not_mem_nil, or_false, not_or] at hg
        simp [riskEnv, hg.1, hg.2.1, hg.2.2]
      show (riskEnv R).predicates p = some ss
      rw [hr]
      exact hss

theorem regenerate_might_view (R : RiskDoc) (d : Decision) : (regenerate R d).might = mightOfView (view R d) := by
  simp only [regenerate, mightOfView, view, obs, List.filter_map, List.map_map]
  rw [List.map_congr_left (g := id) (by intro p _; rfl), List.map_id]
  rfl

theorem regenerate_leads_view (R : RiskDoc) (d : Decision) : (regenerate R d).leads = leadsOfView (view R d) := by
  simp only [regenerate, leadsOfView, view, obs, List.filter_map, List.map_map]
  rw [List.map_congr_left (g := id) (by intro p _; rfl), List.map_id]
  rfl

theorem named_pairRows (R : RiskDoc) (cells : List (String × String)) :
    (pairRows R cells).filterMap (fun t => match t with
      | [a, h] => some (a.2, h.2)
      | _ => none) = cells := by
  induction cells with
  | nil => rfl
  | cons c cs ih => simp [pairRows] at ih ⊢; exact ih

/-- 4.4 and 4.8: a valid record's regenerated model is a valid alternatives scenario whose base structure
satisfies the risk premises, and its tables are the regenerated ones. The first conjunct comes from the
checked step V10 (`modelAdmissible`), which frozen `validateAlternatives` leaves to its caller. -/
theorem risk_scenario_sound (R : RiskDoc) (h : WellFormedRisk R = true) (d : Decision)
    (hv : validateDecision R d = .ok ()) :
    (decisionModel R d).Valid (envAt (inlineTree (toAlt R)) 0) ∧
    VE.Alternatives.validateAlternatives (toAlt R) (decisionModel R d) (decisionRows R d) = .ok () ∧
    backgroundValidRisk R (decisionModel R d) = true ∧
    BaseAdmissibleRisk R (decisionModel R d).asStructure ∧
    (modelTables R (decisionModel R d)).might = (regenerate R d).might ∧
    (modelTables R (decisionModel R d)).leads = (regenerate R d).leads := by
  have hrv := riskValid_of_wellFormed R h
  have hg := viewGate_of_validate hv
  simp only [viewGate, Bool.and_eq_true] at hg
  obtain ⟨⟨⟨⟨_, _⟩, hdata⟩, halt⟩, hprem⟩ := hg
  have hvalid : (decisionModel R d).Valid (envAt (inlineTree (toAlt R)) 0) :=
    modelVocabulary_valid hrv _ (VE.Bridge.modelData_valid _ _ hdata)
  have hbg : backgroundValidRisk R (decisionModel R d) = true := by
    simp only [VE.Alternatives.altModelChecks, Bool.and_eq_true] at halt
    simp only [backgroundValidRisk, Bool.and_eq_true]
    exact ⟨halt.1.1.1.1.1, hprem⟩
  have hlt : R.alt.leadsTo ≠ mightName := by
    intro he
    have := hrv.roles R.alt.leadsTo (by simp [VE.Alternatives.roleNames])
    rw [he, hrv.reserved mightName (by simp [generatedPreds])] at this
    exact this rfl
  refine ⟨hvalid, VE.Alternatives.validateAlternativesWith_ok.mpr halt, hbg,
    baseAdmissibleRisk_of_valid R _ hvalid hbg, ?_, ?_⟩
  · simp only [modelTables, decisionModel, decisionData, dataOfView, dataCore, VE.Bridge.ModelData.toModel,
      VE.Bridge.lookup, List.find?_cons, List.cons_append]
    have : (R.alt.leadsTo == mightName) = false := by simpa using hlt
    simp only [this, beq_self_eq_true, Option.map_some, Option.getD_some]
    rw [named_pairRows, regenerate_might_view]
  · simp only [modelTables, decisionModel, decisionData, dataOfView, dataCore, VE.Bridge.ModelData.toModel,
      VE.Bridge.lookup, List.find?_cons, List.cons_append, beq_self_eq_true, Option.map_some, Option.getD_some]
    rw [named_pairRows, regenerate_leads_view]

end VE.Risk
