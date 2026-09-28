import VE.Route.Admission
import VE.Definitions.Layer
import VE.Norms.Tree

/-! `reports@0` (docs/spec/attribution.md, draft 10): contents, keys, identities,
generated names, `E_reports`, elaboration and the executable well-formedness
check of spec 4.1.

Conventions fixed here (recorded in `lean/REPORTS.md`):

* A canonical object (spec 3.4) is a `CJson` value: JSON with an explicit key
  order, formula ASTs and W1 rule blocks embedded as leaves (rendered by the
  frozen encoders), and no `null` (an absent optional field is an absent key).
  It has decidable equality, so the collision check of spec 4.1 step 4 compares
  canonical objects themselves, never their text.
* `canonical` is the identity on ASTs: formula ASTs are de Bruijn terms, and P5
  normalisation only renames binders and prints, so it changes no AST.
* A quoted package's pinned environment is a `Pinned` record: the decoded
  environment, its `environment_id` (recomputed from the inline JSON) and the
  Background of its own frozen route. It coerces to `VE.Environment`.
* `ReportDoc` carries the profile list and `environment_id(E)`, the inputs of
  the identity domain and of every formula's canonical object. -/
namespace VE.Reports
open Lean

inductive Act | says | believes | wants | intends
  deriving DecidableEq, Repr
inductive Judgment | may | probably
  deriving DecidableEq, Repr
inductive Tense | present | past | perfect
  deriving DecidableEq, Repr

def Act.name : Act → String
  | .says => "says" | .believes => "believes" | .wants => "wants" | .intends => "intends"
def Judgment.name : Judgment → String
  | .may => "may" | .probably => "probably"
def Tense.name : Tense → String
  | .present => "present" | .past => "past" | .perfect => "perfect"

structure Context where
  id : String
  tense : Tense
  /-- a tag with no temporal inference -/
  referenceTime : Option String
  description : String
  deriving DecidableEq, Repr

/-- W2's complete open-term record, per assessment. `decidedBy` is never absent. -/
structure Assessment where
  id : String
  /-- a constant of the evidence sort -/
  context : String
  /-- "unresolved_decider" when the source names none -/
  decidedBy : String
  necessary : List VE.Formula
  sufficient : List VE.Formula
  factors : List String
  precedents : List String
  jurisdiction : String
  version : Nat
  deriving DecidableEq, Repr

/-- A quoted package's pinned local environment: the decoded environment, its
identity and the Background of its own frozen route (spec 5.1). -/
structure Pinned where
  env : VE.Environment
  id : String
  background : List VE.Formula

instance : Coe Pinned VE.Environment := ⟨Pinned.env⟩

/-- 1.1: contents and statements in one type. `negated` wraps one report or
assessment node (4.1 step 4). -/
inductive Content where
  | formula (φ : VE.Formula)
  | norm (Eq : Pinned) (D : VE.Norms.Doc)
  | definition (Eq : Pinned) (ds : List VE.Definitions.Def) (stmt : Option VE.Formula)
  | report (holder : String) (act : Act) (ctx : String) (body : Content) (literal : Option String)
  | assessment (j : Judgment) (a : String) (body : Content)
  | negated (n : Content)

def Content.isReport : Content → Bool
  | .report .. => true
  | _ => false
def Content.isAssessment : Content → Bool
  | .assessment .. => true
  | _ => false

/-- The top-level form (the statement grammar of 1.1): a report, an assessment,
or the negation of one. -/
def Content.Statement : Content → Prop
  | .report .. => True
  | .assessment .. => True
  | .negated n => n.isReport = true ∨ n.isAssessment = true
  | _ => False

def Content.isStatement : Content → Bool
  | .report .. => true
  | .assessment .. => true
  | .negated n => n.isReport || n.isAssessment
  | _ => false

theorem Content.isStatement_iff (x : Content) : x.isStatement = true ↔ x.Statement := by
  cases x <;> simp [isStatement, Statement]

/-- Every node of a tree, including the root. -/
def Content.nodes : Content → List Content
  | x@(.report _ _ _ b _) => x :: b.nodes
  | x@(.assessment _ _ b) => x :: b.nodes
  | x@(.negated n) => x :: n.nodes
  | x => [x]

/-- 4.1 step 4: a leaf counts one, a report or assessment node one more than its
body, a negated node nothing, as it counts nothing in a W2 kind (3.3). -/
def Content.depth : Content → Nat
  | .report _ _ _ b _ => b.depth + 1
  | .assessment _ _ b => b.depth + 1
  | .negated n => n.depth
  | _ => 1

theorem Content.mem_nodes_self (x : Content) : x ∈ x.nodes := by
  cases x <;> simp [nodes]

structure ReportKey where
  act : Act
  sort : String
  ctx : String
  /-- the complement id -/
  content : String
  deriving DecidableEq, Repr

structure AssessKey where
  j : Judgment
  a : String
  content : String
  deriving DecidableEq, Repr

/-- One top-level unit: its id and its statement; document order is the order
of `ReportDoc.units`. -/
structure Unit where
  id : String
  content : Content

/-- 5.2: a unit and a depth. Depth 0 is the unit's root complement (the legacy
target); depth n descends n times, once per `1` of the rendered path. -/
structure Path where
  unit : String
  depth : Nat
  deriving DecidableEq, Repr

structure Bridge where
  id : String
  target : Path
  acceptedBy : String
  reason : List String
  deriving DecidableEq, Repr

structure ScopedCheck where
  id : String
  payloads : List Path
  conclusion : VE.Formula
  deriving DecidableEq, Repr

structure ReportDoc where
  /-- the author's environment, with the reports block decoded -/
  E : VE.Environment
  lits : List String
  /-- holder sorts -/
  holders : List String
  /-- the evidence sort -/
  evidence : String
  contexts : List Context
  assessments : List Assessment
  /-- report, assessment and negated units, one sequence, document order -/
  units : List Unit
  bridges : List Bridge
  «scoped» : List ScopedCheck
  /-- the envelope's profile list: the identity domain `ve-*-<identity_version>` -/
  profiles : List String
  /-- `environment_id(E)`, recomputed from the raw environment -/
  environmentId : String

def Occurs (D : ReportDoc) (x : Content) : Prop := ∃ u ∈ D.units, x ∈ u.content.nodes

/-- 3.4: a complement object occurs in D when some report node of some tree,
under a negated node or not, has that body and literal. -/
def OccursComplement (D : ReportDoc) (body : Content) (lit : Option String) : Prop :=
  ∃ hd act c, Occurs D (.report hd act c body lit)

def Positive (D : ReportDoc) : Prop := ∀ u ∈ D.units, ¬ ∃ n, u.content = .negated n

/-! ## Canonical objects and identities (3.4) -/

/-- Canonical JSON with formula ASTs and W1 rule blocks as leaves. Arrays and
objects are cons chains (`acons … anil`, `ocons … onil`), so the type is not
nested and has derived decidable equality. -/
inductive CJson where
  | str (s : String)
  | num (n : Nat)
  | ast (φ : VE.Formula)
  | rules (ns : List VE.Norms.Node)
  | anil
  | acons (x : CJson) (xs : CJson)
  | onil
  | ocons (k : String) (v : CJson) (xs : CJson)
  deriving DecidableEq

def CJson.a (xs : List CJson) : CJson := xs.foldr .acons .anil
def CJson.o (kvs : List (String × CJson)) : CJson := kvs.foldr (fun kv r => .ocons kv.1 kv.2 r) .onil

theorem CJson.o_inj {xs ys : List (String × CJson)} (h : CJson.o xs = CJson.o ys) : xs = ys := by
  induction xs generalizing ys with
  | nil => cases ys <;> simp_all [CJson.o]
  | cons x xs ih =>
    cases ys with
    | nil => simp [CJson.o] at h
    | cons y ys =>
      obtain ⟨k, v⟩ := x
      obtain ⟨k', v'⟩ := y
      simp only [CJson.o, List.foldr_cons, CJson.ocons.injEq] at h
      obtain ⟨rfl, rfl, h⟩ := h
      rw [ih h]

/-- W1 rule nodes in the `{"norm": …}` wire form of norms.md 3.2. -/
def encodeNode (n : VE.Norms.Node) : Json :=
  Json.mkObj [("norm", Json.mkObj [("name", .str n.name), ("predicate", .str n.pred),
    ("sign", .bool n.sign), ("guard", VE.Route.Wire.encodeFormula n.guard),
    ("unless", Json.arr (n.carveOuts.map VE.Route.Wire.encodeFormula).toArray),
    ("over", Json.arr (n.over.map Json.str).toArray)])]

/-- The JSON a canonical object stands for (keys are sorted by the canonical
serialiser, so chain order is immaterial to the digest). -/
def CJson.toJson : CJson → Json
  | .str s => .str s
  | .num n => Lean.toJson n
  | .ast φ => VE.Route.Wire.encodeFormula φ
  | .rules ns => Json.arr (ns.map encodeNode).toArray
  | .anil => Json.arr #[]
  | .acons x xs => match xs.toJson with
    | .arr ys => .arr (#[x.toJson] ++ ys)
    | _ => .arr #[x.toJson]
  | .onil => Json.mkObj []
  | .ocons k v xs => (xs.toJson).setObjVal! k v.toJson

/-- The P5 normal form of a formula AST: the identity, because ASTs are de
Bruijn terms and P5 normalisation only renames binders and prints. -/
def canonical (φ : VE.Formula) : VE.Formula := φ

def holderSort (D : ReportDoc) (h : String) : Option String :=
  match D.E.constants h with
  | some s => if D.holders.contains s then some s else none
  | none => none

def recordOf (D : ReportDoc) (a : String) : Option Assessment := D.assessments.find? (·.id == a)
def contextOf (D : ReportDoc) (c : String) : Option Context := D.contexts.find? (·.id == c)
def tenseOf (D : ReportDoc) (c : String) : Option Tense := (contextOf D c).map (·.tense)

def optField (k : String) : Option String → List (String × CJson)
  | some s => [(k, .str s)]
  | none => []

def contextObject (D : ReportDoc) (c : String) : CJson :=
  match contextOf D c with
  | some x => .o ([("id", .str x.id), ("tense", .str x.tense.name)] ++
      optField "reference_time" x.referenceTime ++ [("description", .str x.description)])
  | none => .o [("id", .str c)]

def recordObject (D : ReportDoc) (a : String) : CJson :=
  match recordOf D a with
  | some r => .o [("id", .str r.id), ("context", .str r.context), ("decided_by", .str r.decidedBy),
      ("necessary", .a (r.necessary.map .ast)), ("sufficient", .a (r.sufficient.map .ast)),
      ("factors", .a (r.factors.map .str)), ("precedents", .a (r.precedents.map .str)),
      ("jurisdiction", .str r.jurisdiction), ("version", .num r.version)]
  | none => .o [("id", .str a)]

/-- object(x) of 3.4. -/
def canonicalObject (D : ReportDoc) : Content → CJson
  | .formula φ => .o [("environment_id", .str D.environmentId), ("ast", .ast (canonical φ))]
  | .norm Eq N => .o [("environment_id", .str Eq.id), ("norms", .rules N.T.nodes)]
  | .definition Eq _ st => .o ([("environment_id", .str Eq.id)] ++
      match st with
      | some φ => [("content", .o [("environment_id", .str Eq.id), ("ast", .ast (canonical φ))])]
      | none => [])
  | .report h act c b lit => .o [("holder", .str h), ("act", .str act.name),
      ("context", contextObject D c),
      ("complement", .o ([("content", canonicalObject D b)] ++ optField "literal" lit))]
  | .assessment j a b => .o [("judgment", .str j.name), ("record", recordObject D a),
      ("content", canonicalObject D b)]
  | .negated n => .o [("negated", canonicalObject D n)]

/-- The complement object of a report node: its body's object and literal words. -/
def complementObject (D : ReportDoc) (body : Content) (lit : Option String) : CJson :=
  .o ([("content", canonicalObject D body)] ++ optField "literal" lit)

def identityVersion (D : ReportDoc) : String := VE.Route.Wire.identityVersion D.profiles

/-- The digest naming a canonical object in the content-id domain. -/
def digestOf (D : ReportDoc) (o : CJson) : String :=
  match VE.CertificateWire.digest ("ve-content-" ++ identityVersion D ++ "\n") o.toJson with
  | .ok s => s
  | .error _ => ""

def contentId (D : ReportDoc) (x : Content) : String := digestOf D (canonicalObject D x)
def complementId (D : ReportDoc) (body : Content) (lit : Option String) : String :=
  digestOf D (complementObject D body lit)

def pathObject (p : Path) : CJson := .o [("unit", .str p.unit), ("depth", .num p.depth)]

/-- The canonical document object behind `document_id(D)`. -/
def documentObject (D : ReportDoc) : CJson :=
  .o [("environment_id", .str D.environmentId),
    ("document", .o [
      ("units", .a (D.units.map fun u => .o [("id", .str u.id), ("content", canonicalObject D u.content)])),
      ("contexts", .a (D.contexts.map fun c => contextObject D c.id)),
      ("assessments", .a (D.assessments.map fun a => recordObject D a.id)),
      ("bridges", .a (D.bridges.map fun b => .o [("id", .str b.id), ("target", pathObject b.target),
        ("accepted_by", .str b.acceptedBy), ("reason", .a (b.reason.map .str))])),
      ("scoped", .a (D.«scoped».map fun s => .o [("id", .str s.id),
        ("payloads", .a (s.payloads.map pathObject)), ("conclusion", .ast s.conclusion)]))])]

def documentId (D : ReportDoc) : String :=
  match VE.CertificateWire.digest ("ve-reports-" ++ identityVersion D ++ "\n") (documentObject D).toJson with
  | .ok s => s
  | .error _ => ""

/-! ## Keys and generated names (1.5) -/

def reportKeyOf (D : ReportDoc) : Content → Option ReportKey
  | .report h act c b lit => (holderSort D h).map fun s => ⟨act, s, c, complementId D b lit⟩
  | _ => none

def assessKeyOf (D : ReportDoc) : Content → Option AssessKey
  | .assessment j a b => some ⟨j, a, contentId D b⟩
  | _ => none

/-- A top-level unit's key: its own, or its operand's when it is negated. -/
def topReportKeyOf (D : ReportDoc) : Content → Option ReportKey
  | .negated n => reportKeyOf D n
  | x => reportKeyOf D x

def topAssessKeyOf (D : ReportDoc) : Content → Option AssessKey
  | .negated n => assessKeyOf D n
  | x => assessKeyOf D x

def allNodes (D : ReportDoc) : List Content := D.units.flatMap (·.content.nodes)

def dedup {α : Type} [DecidableEq α] : List α → List α
  | [] => []
  | x :: xs => if x ∈ dedup xs then dedup xs else x :: dedup xs

theorem mem_dedup {α : Type} [DecidableEq α] (a : α) : ∀ l : List α, a ∈ dedup l ↔ a ∈ l
  | [] => by simp [dedup]
  | x :: xs => by
    unfold dedup
    split
    · rename_i hx
      rw [mem_dedup a xs, List.mem_cons]
      constructor
      · exact Or.inr
      · rintro (rfl | h)
        · exact (mem_dedup _ xs).mp hx
        · exact h
    · rw [List.mem_cons, List.mem_cons, mem_dedup a xs]

theorem length_dedup {α : Type} [DecidableEq α] : ∀ l : List α, (dedup l).length ≤ l.length
  | [] => by simp [dedup]
  | x :: xs => by
    unfold dedup
    have := length_dedup xs
    split <;> simp <;> omega

/-- Lexicographic order on string tuples, as Python compares tuples of `str`. -/
def lexLe : List String → List String → Bool
  | [], _ => true
  | _ :: _, [] => false
  | x :: xs, y :: ys => decide (x < y) || (x == y && lexLe xs ys)

def ReportKey.fields (k : ReportKey) : List String := [k.act.name, k.sort, k.ctx, k.content]
def AssessKey.fields (k : AssessKey) : List String := [k.j.name, k.a, k.content]

/-- Every report node of every tree, deduplicated, sorted by (act, holder sort,
context id, content id). -/
def keys (D : ReportDoc) : List ReportKey :=
  (dedup ((allNodes D).filterMap (reportKeyOf D))).mergeSort (fun a b => lexLe a.fields b.fields)

def akeys (D : ReportDoc) : List AssessKey :=
  (dedup ((allNodes D).filterMap (assessKeyOf D))).mergeSort (fun a b => lexLe a.fields b.fields)

/-- Keys of the top-level report units, asserted or denied. -/
def topKeys (D : ReportDoc) : List ReportKey := D.units.filterMap (fun u => topReportKeyOf D u.content)
def topAKeys (D : ReportDoc) : List AssessKey := D.units.filterMap (fun u => topAssessKeyOf D u.content)

/-- `reports__<act>__<i>`, `i` the 1-based position among the keys of that act. -/
def reportName (D : ReportDoc) (k : ReportKey) : String :=
  "reports__" ++ k.act.name ++ "__" ++ toString (((keys D).filter (·.act == k.act)).idxOf k + 1)

def assessName (D : ReportDoc) (k : AssessKey) : String :=
  "reports__" ++ k.j.name ++ "__" ++ toString (((akeys D).filter (·.j == k.j)).idxOf k + 1)

def names (D : ReportDoc) : List String := (keys D).map (reportName D) ++ (akeys D).map (assessName D)

/-- The key whose generated name is `r`. -/
def keyOf (D : ReportDoc) (r : String) : Option (ReportKey ⊕ AssessKey) :=
  match (keys D).find? (fun k => reportName D k == r) with
  | some k => some (.inl k)
  | none => ((akeys D).find? (fun k => assessName D k == r)).map .inr

/-- E + one unary predicate per key. -/
def envReports (D : ReportDoc) : VE.Environment :=
  { D.E with predicates := fun r =>
      match keyOf D r with
      | some (.inl k) => some [k.sort]
      | some (.inr _) => some [D.evidence]
      | none => D.E.predicates r }

def contentCount (D : ReportDoc) : Nat := (allNodes D).length

/-! ## Elaboration (4.3) -/

/-- Total on formula, report, assessment and negated nodes; none on norm and
definition nodes. -/
def «elab» (D : ReportDoc) : Content → Option VE.Formula
  | .formula φ => some φ
  | .report h act c b lit =>
      (holderSort D h).map fun s => .unary (reportName D ⟨act, s, c, complementId D b lit⟩) (.const h)
  | .assessment j a b =>
      (recordOf D a).map fun r => .unary (assessName D ⟨j, a, contentId D b⟩) (.const r.context)
  | .negated n => («elab» D n).map .not
  | _ => none

def unitPremise (D : ReportDoc) (u : Unit) : Option VE.Formula := «elab» D u.content

/-- Γ_reports(D), in document order. -/
def premises (D : ReportDoc) : List VE.Formula := D.units.filterMap (unitPremise D)

/-- W2's open-term inventory: the generated assessment names (5.3). -/
def openTerms (D : ReportDoc) : List String := (akeys D).map (assessName D)

/-- 4.4: well-formed signed generated atoms. -/
def SignedAtom (D : ReportDoc) (a : VE.Formula) : Prop :=
  ∃ r ∈ names D, ∃ h, (VE.Formula.unary r (.const h)).WellFormed (envReports D) [] ∧
    (a = .unary r (.const h) ∨ a = .not (.unary r (.const h)))

/-- One row of `neqs`: the disequality between `h` and the holder of a denied
atom of `P`. -/
def neqRow (h P : String) : VE.Formula → Option VE.Formula
  | .not (.unary P' (.const h')) => if P' = P then some (.not (.eq (.const h) (.const h'))) else none
  | _ => none

def neqsOf (R : List VE.Formula) : VE.Formula → List VE.Formula
  | .unary P (.const h) => R.filterMap (neqRow h P)
  | _ => []

/-- The holder disequalities of a signed list: `¬(h = h')` for `P(h) ∈ R` and
`¬P(h') ∈ R`, in R's order. -/
def neqs (R : List VE.Formula) : List VE.Formula := R.flatMap (neqsOf R)

def UniformPolarity (R : List VE.Formula) : Prop :=
  ¬ ∃ P h h', VE.Formula.unary P (.const h) ∈ R ∧ VE.Formula.not (.unary P (.const h')) ∈ R

/-! ## Paths (5.2) -/

/-- `complementOf` passes through a negated node into its operand; a norm node
has no complement. -/
def complementOf : Content → Option Content
  | .report _ _ _ b _ => some b
  | .assessment _ _ b => some b
  | .definition _ _ (some st) => some (.formula st)
  | .negated n => complementOf n
  | _ => none

def unitOf (D : ReportDoc) (u : String) : Option Unit := D.units.find? (·.id == u)

/-- The node whose complement the path names. -/
def parentAt (D : ReportDoc) (u : String) : Nat → Option Content
  | 0 => (unitOf D u).map (·.content)
  | n + 1 => (parentAt D u n).bind complementOf

/-- The unit's root complement, then `complementOf` depth times. -/
def contentAt (D : ReportDoc) (p : Path) : Option Content := (parentAt D p.unit p.depth).bind complementOf

/-- The scope of the author's environment: `E` and its literals. -/
def authorScope (D : ReportDoc) : Pinned :=
  ⟨D.E, D.environmentId, VE.Route.Background.literals D.lits⟩

/-- The scope a descent from a node enters: a definition package's pinned one. -/
def enterScope (s : Pinned) : Content → Pinned
  | .definition Eq _ _ => Eq
  | _ => s

def scopeAux (D : ReportDoc) (u : String) : Nat → Option Pinned
  | 0 => (parentAt D u 0).map (enterScope (authorScope D))
  | n + 1 => match scopeAux D u n, parentAt D u (n + 1) with
    | some s, some x => some (enterScope s x)
    | _, _ => none

/-- The scope of the node a path names: `E` with its literals, or the pinned
environment of the enclosing quoted package. -/
def scopeAt (D : ReportDoc) (p : Path) : Option Pinned := scopeAux D p.unit p.depth

/-- D.E, or the pinned Eq of the enclosing package. -/
def envAt (D : ReportDoc) (p : Path) : Option VE.Environment := (scopeAt D p).map Pinned.env

def holderOf : Content → Option String
  | .report h .. => some h
  | .negated n => holderOf n
  | _ => none

def isAssessNode : Content → Bool
  | .assessment .. => true
  | .negated n => isAssessNode n
  | _ => false

/-- The holder of the report node whose complement p names. -/
def holderAt (D : ReportDoc) (p : Path) : Option String := (parentAt D p.unit p.depth).bind holderOf

/-- p names an assessment node's complement. -/
def isAssessmentAt (D : ReportDoc) (p : Path) : Bool :=
  match parentAt D p.unit p.depth with
  | some x => isAssessNode x
  | none => false

def bridgeFormula (D : ReportDoc) (p : Path) : Option VE.Formula := (contentAt D p).bind («elab» D)

/-- 5.1: the payloads' scope and formulas, when every payload path names a
formula node and all of them lie in one scope (compared by environment id). -/
def payloadFormulas (D : ReportDoc) (s : ScopedCheck) : Option (Pinned × List VE.Formula) :=
  match s.payloads with
  | [] => none
  | p :: _ =>
    match scopeAt D p with
    | none => none
    | some Eq =>
      let fs := s.payloads.filterMap fun q =>
        match contentAt D q, scopeAt D q with
        | some (.formula φ), some Eq' => if Eq'.id == Eq.id then some φ else none
        | _, _ => none
      if fs.length == s.payloads.length then some (Eq, fs) else none

/-- Background(Eq) of Eq's own frozen route (5.1). -/
def background (Eq : Pinned) : List VE.Formula := Eq.background

/-! ## The reports gate (9.4) -/

def reportsProfile : String := "reports@0"

/-- A function around the frozen classifier, never a change to it. -/
def reportsGate (ps : List String) : Except String _root_.Unit :=
  if ps.contains reportsProfile then
    match VE.Route.Gate.classify (ps.erase reportsProfile) with
    | .error e => .error e
    | .ok .fol =>
      match ["data@0", "definitions@0", "norms@0"].find? ps.contains with
      | some p => .error (VE.Route.Gate.unsupported s!"reports@0 with {p} layers")
      | none => .ok ()
    | .ok _ => .error (VE.Route.Gate.unsupported "reports@0 requires the FOL family")
  else .error (VE.Route.Gate.unsupported "reports@0 is required")

theorem reports_gate_sound (ps : List String) (h : reportsGate ps = .ok ()) :
    "reports@0" ∈ ps ∧ VE.Route.Gate.classify (ps.erase "reports@0") = .ok .fol ∧
      "norms@0" ∉ ps ∧ "definitions@0" ∉ ps ∧ "data@0" ∉ ps := by
  unfold reportsGate at h
  split at h
  · rename_i hr
    split at h
    · cases h
    · rename_i hc
      split at h
      · cases h
      · rename_i hf
        have hn := fun p hp => List.find?_eq_none.mp hf p hp
        refine ⟨by simpa [reportsProfile] using hr, hc, ?_, ?_, ?_⟩ <;>
          intro hm <;> simp_all
    · cases h
  · cases h

/-! ## Well-formedness (4.1) -/

/-- The per-node checks of 4.1 step 4. -/
def nodeOk (D : ReportDoc) : Content → Bool
  | .formula φ => φ.check D.E []
  | .report h _ c _ _ => (holderSort D h).isSome && (contextOf D c).isSome
  | .assessment _ a _ => (recordOf D a).isSome
  | .negated n => n.isReport || n.isAssessment
  | .norm _ _ => true
  | .definition Eq _ st => st.all (·.check Eq.env [])

/-- The objects a document digests: the content object of every node and the
complement object of every report node, with their digests. -/
def digestTable (D : ReportDoc) : List (String × CJson) :=
  (allNodes D).flatMap fun x =>
    (contentId D x, canonicalObject D x) ::
      match x with
      | .report _ _ _ b lit => [(complementId D b lit, complementObject D b lit)]
      | _ => []

def assessmentOk (D : ReportDoc) (a : Assessment) : Bool :=
  D.E.constants a.context == some D.evidence && VE.Route.Admission.token a.decidedBy &&
    (a.necessary ++ a.sufficient).all (·.check D.E [])

def scopedOk (D : ReportDoc) (s : ScopedCheck) : Bool :=
  s.payloads.length ≤ 64 &&
    match payloadFormulas D s with
    | some (Eq, _) => s.conclusion.check Eq.env []
    | none => false

def bridgeOk (D : ReportDoc) (b : Bridge) : Bool :=
  decide (1 ≤ b.target.depth) && (bridgeFormula D b.target).isSome &&
    match scopeAt D b.target with
    | some Eq => Eq.id == D.environmentId
    | none => false

/-- 4.1, as one executable check. The HashCollision part compares the objects of
`digestTable` and no other. -/
def WellFormedReports (D : ReportDoc) : Bool :=
  (reportsGate D.profiles).toBool &&
  decide (D.units.map (·.id)).Nodup &&
  D.units.all (·.content.isStatement) &&
  D.units.all (fun u => decide (u.content.depth ≤ 16)) &&
  (allNodes D).all (nodeOk D) &&
  decide (D.contexts.map (·.id)).Nodup &&
  decide (D.assessments.map (·.id)).Nodup &&
  D.assessments.all (assessmentOk D) &&
  decide (∀ a ∈ digestTable D, ∀ b ∈ digestTable D, a.1 = b.1 → a.2 = b.2) &&
  (names D).all (fun n => (D.E.predicates n).isNone && decide (n.utf8ByteSize ≤ 64)) &&
  decide (names D).Nodup &&
  D.lits.all (fun l => D.E.constants l == some VE.Route.Background.stringSort) &&
  D.«scoped».all (scopedOk D) &&
  D.bridges.all (bridgeOk D)

end VE.Reports
