-- ve-layer: 4 (fixtures of the document mode's lowering; experimental, unreachable from the service)
import VE.Experimental.CoreDocument

/-! Examples of the lowering (`VE.Experimental.CoreDocument.lower`): one small document per row of the table, a
judgment term read by a soft rule's exception beside a fact about that term, a two-reading set, couplings, and each
refusal. The environment is decoded by the document mode's own decoder (`decodedEnvironment`), soft rules by the soft
route's (`decodeSoftNorm`, `softCanonical`), as `check` has them before its status folds.

Expires: 2026-12-07 -/

namespace VE.Experimental.CoreDocumentExamples
open Lean
open VE.Service.Document
open VE.Experimental.CoreDocument

/-! ## The document's environment and units -/

def arg (description : String) : Json :=
  Json.mkObj [("arguments", Json.arr #[.str "agent"]), ("description", .str description)]

def regulatedArg (description default role : String) (permission : List String := []) : Json :=
  (arg description).setObjVal! "regulated" (Json.mkObj ([("act", .str "{0} release the report"),
    ("default", .str default), ("role", .str role)] ++ permission.map (("permission", .str ·))))

/-- `release_required` is regulated; `redacted` is the judgment term ("significantly redacted"); `reviewed` and
`public` are base predicates; `c` is a constant. -/
def environmentJson (profiles : List String) : Json :=
  Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson profiles),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"),
    ("vocabulary", Json.mkObj [
      ("constants", Json.mkObj [("c", Json.mkObj [("sort", .str "agent"), ("description", .str "the report")])]),
      ("predicates", Json.mkObj [
        ("release_required", regulatedArg "must release" "deny" "obligation" ["release_permitted"]),
        ("release_permitted", regulatedArg "may release" "allow" "permission"),
        ("redacted", arg "significantly redacted"), ("reviewed", arg "reviewed"), ("public", arg "public")]),
      ("sorts", Json.mkObj [("agent", Json.mkObj [("description", .str "an agent")])])])]

def mixedProfiles : List String :=
  ["documents@1", "judgments@0", "norms@0", "readings@1", "relational-fol@0", "soft-norms@0"]

def envOf (profiles : List String) : Option Env := (decodedEnvironment (environmentJson profiles) .none).toOption

/-- The mixed document's environment (the RSP's profiles). -/
def E? : Option Env := envOf mixedProfiles

#guard E?.isSome
#guard (E?.map (·.regulated)) == some ["release_permitted", "release_required"]

/-- The soft route's decoded environment, which reads a unit's soft rule. -/
def softEnv : Option VE.SoftNorms.Wire.SoftEnvironment := E?.bind fun E =>
  (VE.SoftNorms.Wire.decodeSoftSource (wireJson 257 E.lower) (Json.arr #[])).toOption.map (·.se)

#guard softEnv.isSome

def at0 (p : String) : Json := Json.arr #[.str "unary", .str p, Json.arr #[.str "var", toJson (0 : Nat)]]

/-- "The report must be released if reviewed, unless it has been significantly redacted": a default rule whose
exception's sufficient condition reads the judgment term `redacted`. -/
def releaseRule : Json := Json.mkObj [("norm", Json.mkObj [("name", .str "release"),
  ("predicate", .str "release_required"), ("sign", .bool true), ("mode", .str "default"), ("guard", at0 "reviewed"),
  ("unless", Json.arr #[]), ("over", Json.arr #[]), ("exception", Json.mkObj [("decided_by", .str "unstated"),
    ("necessary", Json.arr #[]), ("factors", Json.arr #[]), ("sufficient", Json.arr #[at0 "redacted"])])])]

/-- A unit's soft content as `softContentOf` answers it: the single-rule check, then the canonical form. -/
def softContent (rule : Json) : Option UnitContent := do
  let N ← (VE.SoftNorms.Wire.decodeSoftNorm (← softEnv) (wireJson 257 rule)).toOption
  pure (.soft (softCanonical N (rule.getObjValD "norm")))

#guard (softContent releaseRule).isSome

def asserted : RowKind := match decodeRowKind false (.str "asserted") with
  | .ok k => k
  | .error _ => .rights .right

def unitOf (id : String) (content : Option UnitContent) (meaning : Json := .str "specified") : SourceUnit :=
  { id, span := (0, 0), kind := .str "asserted", decoded := asserted, meaning, support := "assumption",
    status := "", parent := none, content }

def openOn (terms : List String) : Json := Json.mkObj [("open", toJson terms)]

def fact (p : String) : VE.Formula := .unary p (.const "c")

/-- The judgment record of `redacted`, as `Judgments.records` reads it. -/
def redactedRecord : VE.Judgments.Rec := (⟨"redacted", ["agent"], "reviewer", []⟩, 0, 0)

/-- Each unit's view, as `judgedViews` builds it with no active set. -/
def viewOf (u : SourceUnit) (meaning : String) : VE.Judgments.UnitView :=
  VE.Judgments.viewOf [] (fun _ => []) u.id meaning (listedOf u.meaning) true
    (match u.content with
     | some c => (c.judgedIn softEnv none).toOption.join
     | none => none)

/-! ## Rendering an answer -/

def originText (o : Origin) : String :=
  s!"{o.unit} {o.feature}" ++ match o.reading with
    | some (s, i) => s!" {s}#{i}"
    | none => ""

def bodyText : Body → String
  | .soft r => "rule " ++ ((r.getObjValD "norm").getObjValD "name").compress
  | .premise φ => "premise " ++ (VE.Route.Wire.encodeFormula φ).compress
  | .judgment j => "judgment " ++ j.name

/-- Each core document's choice and statements, `origin: body`. -/
def summary (r : Except String (List (Choice × CoreDoc))) : Except String (List (Choice × List String)) :=
  r.map (·.map fun (c, d) => (c, d.statements.map fun s => s!"{originText s.origin}: {bodyText s.body}"))

/-- Whether the lowering answered exactly these core documents. -/
def answers (r : Except String (List (Choice × CoreDoc))) (expected : List (Choice × List String)) : Bool :=
  match summary r with
  | .ok xs => xs == expected
  | .error _ => false

def refusal (r : Except String (List (Choice × CoreDoc))) : String :=
  match r with
  | .error e => e
  | .ok _ => "lowered"

def lowerUnits (units : List SourceUnit) (sets : List ActiveSet := []) (couplings : List Coupling := [])
    (views : Option (List VE.Judgments.UnitView) := none) (env : Option Env := E?) (senses := false)
    (records : List VE.Judgments.Rec := [redactedRecord]) : Except String (List (Choice × CoreDoc)) :=
  match env with
  | some env => lower env senses records (views.getD (units.map (viewOf · "specified"))) units sets couplings
  | none => .error "no environment"

/-! ## One document per row -/

-- soft-norms@0: a rule unit is one soft rule, the core document's one norm object; no premise.
def ruleUnit : SourceUnit := unitOf "u1" (softContent releaseRule)
#guard answers (lowerUnits [ruleUnit]) [([], ["u1 soft-norms@0: rule \"release\""])]

-- facts: a formula unit over base predicates is one premise; a document without reading sets has one core document,
-- with the empty choice.
#guard answers (lowerUnits [unitOf "u1" (some (.formula (fact "reviewed"))), unitOf "u2" (some (.formula (fact "public")))])
  [([], ["u1 facts: premise [\"unary\",\"reviewed\",[\"const\",\"c\"]]",
    "u2 facts: premise [\"unary\",\"public\",[\"const\",\"c\"]]"])]

-- judgments@0: a unit whose `open` meaning lists the term declares it (a base predicate with its decider), no premise.
def guardRule : Json := (releaseRule.setObjVal! "norm" (((releaseRule.getObjValD "norm").setObjVal! "guard"
  (at0 "redacted")).setObjVal! "name" (.str "withheld")))
def guardUnit : SourceUnit := unitOf "u1" (softContent guardRule) (openOn ["redacted"])
#guard answers (lowerUnits [guardUnit] (views := some [viewOf guardUnit "open"]))
  [([], ["u1 judgments@0: judgment redacted", "u1 soft-norms@0: rule \"withheld\""])]

-- register labels (and every unit without content): no statement.
#guard answers (lowerUnits [unitOf "u1" none (.str "aspiration"), unitOf "u2" (some (.formula (fact "public")))])
  [([], ["u2 facts: premise [\"unary\",\"public\",[\"const\",\"c\"]]"])]

/-! ## A judgment term in a rule's exception, and a fact about the term

The rule reads `redacted` in its exception's condition: no premise is produced for the term, and the rule's statement
mentions its predicate. (Under the judgment rules as they are, `Judgments.softContent` reads a soft rule's guard and
carve-outs only, so the rule unit does not depend on the term and does not list it.) The fact unit "the report has been
judged significantly redacted" lists the term and is one premise, with that unit's origin. -/

def judgedFact : SourceUnit := unitOf "u2" (some (.formula (fact "redacted"))) (openOn ["redacted"])
def judgedDoc : Except String (List (Choice × CoreDoc)) :=
  lowerUnits [ruleUnit, judgedFact] (views := some [viewOf ruleUnit "specified", viewOf judgedFact "open"])

#guard answers judgedDoc [([], ["u1 soft-norms@0: rule \"release\"", "u2 judgments@0: judgment redacted",
  "u2 facts: premise [\"unary\",\"redacted\",[\"const\",\"c\"]]"])]
-- One premise, from the fact unit; the rule is the one norm object and mentions the term's predicate.
#guard match judgedDoc with
  | .ok [(_, d)] => d.premises == [fact "redacted"] &&
      (d.statements.filter (·.body.premise?.isSome)).map (·.origin.unit) == ["u2"] &&
      (match d.norms with
       | .arr #[r] => (r.compress.splitOn "\"redacted\"").length == 2
       | _ => false)
  | _ => false
-- The core document is the soft route's source: its environment and norm objects decode as the soft route reads them.
#guard match judgedDoc with
  | .ok [(_, d)] => (VE.SoftNorms.Wire.decodeSoftSource d.environment d.norms).isOk
  | _ => false

/-! ## A strict norm

A W1 norm (`UnitContent.norm`) lowers to a soft rule only where the soft route's decoder reads its encoding as a strict
rule with the same fields: over this soft-norms@0 environment it does. A plain norms@0 document's own environment is
not one the soft decoder reads, so there it has no embedding and is refused (none is invented). -/

def strictNode : VE.Norms.Node :=
  { name := "never", pred := "release_permitted", sign := false, guard := .unary "public" (.var 0), carveOuts := [],
    over := [] }

#guard answers (lowerUnits [unitOf "u1" (some (.norm strictNode))]) [([], ["u1 norms@0: rule \"never\""])]
#guard match lowerUnits [unitOf "u1" (some (.norm strictNode))], softEnv with
  | .ok [(_, d)], some se => match d.norms with
    | .arr #[r] => match VE.SoftNorms.Wire.decodeSoftNorm se r with
      | .ok N => N.toNode == strictNode && N.mode == .strict && N.exception.isNone && !N.hard
      | .error _ => false
    | _ => false
  | _, _ => false

def normsOnly : Option Env := envOf ["documents@1", "norms@0", "relational-fol@0"]
#guard normsOnly.isSome
#guard refusal (lowerUnits [unitOf "u1" (some (.norm strictNode))] (env := normsOnly)) ==
  "UnsupportedLowering: unit u1 feature norms@0: a strict norm has no soft rule: the soft route's decoder refuses " ++
  "the core environment: UnsupportedProfile: soft-norms@0 is required"

/-! ## Readings -/

def readingSet (id unit : String) (fs : List VE.Formula) (status := "open") : ActiveSet :=
  (⟨id, unit, 1, status, fs.zipIdx.map fun (f, i) => (s!"r{i}", f)⟩, fs.map fun f => some (.formula f))

def twoReadings : Except String (List (Choice × CoreDoc)) :=
  lowerUnits [unitOf "u1" (some (.formula (fact "reviewed"))), unitOf "u2" none]
    [readingSet "rs" "u2" [fact "public", .not (fact "public")]]

-- Two core documents, which differ exactly in the statements of the set's unit.
#guard answers twoReadings [
  ([("rs", 0)], ["u1 facts: premise [\"unary\",\"reviewed\",[\"const\",\"c\"]]",
    "u2 facts rs#0: premise [\"unary\",\"public\",[\"const\",\"c\"]]"]),
  ([("rs", 1)], ["u1 facts: premise [\"unary\",\"reviewed\",[\"const\",\"c\"]]",
    "u2 facts rs#1: premise [\"not\",[\"unary\",\"public\",[\"const\",\"c\"]]]"])]

-- A coupling keeps the choices whose readings have one label: two coupled two-reading sets give two choices, not four.
def twoSets : List ActiveSet :=
  [readingSet "a" "u1" [fact "public", .not (fact "public")], readingSet "b" "u2" [fact "reviewed", .not (fact "reviewed")]]

#guard match lowerUnits [unitOf "u1" none, unitOf "u2" none] twoSets [⟨"k", [("a", ["wide", "narrow"]), ("b", ["wide", "narrow"])]⟩] with
  | .ok cs => cs.map Prod.fst == [[("a", 0), ("b", 0)], [("a", 1), ("b", 1)]]
  | .error _ => false
#guard match lowerUnits [unitOf "u1" none, unitOf "u2" none] twoSets with
  | .ok cs => cs.length == 4
  | .error _ => false

/-! ## Refusals -/

-- A formula over a regulated predicate is a claim about the rules, not a premise.
#guard refusal (lowerUnits [unitOf "u1" (some (.formula (.unary "release_required" (.const "c"))))]) ==
  "UnsupportedLowering: unit u1 feature facts: a formula over the regulated predicate release_required is a claim " ++
  "about the rules, not a premise"
-- Unit content the table has no row for.
#guard refusal (lowerUnits [unitOf "u1" (some (.rights (Json.mkObj [])))]) ==
  "UnsupportedLowering: unit u1 feature rights@0: a rights block has no row"
#guard refusal (lowerUnits [unitOf "u1" (some (.cardinality (Json.mkObj [])))]) ==
  "UnsupportedLowering: unit u1 feature cardinality@0: a cardinality statement has no row"
-- Features of the document the table has no row for: norm-defaults, alternatives or risk, senses.
#guard refusal (lowerUnits [unitOf "u1" none] (env := E?.map fun E => { E with profiles := E.profiles ++ ["norm-defaults@0"] })) ==
  "UnsupportedLowering: unit u1 feature norm-defaults@0: the table has no row for it"
#guard refusal (lowerUnits [unitOf "u1" none] (env := E?.map fun E => { E with block := .alternatives })) ==
  "UnsupportedLowering: unit u1 feature alternatives or risk block: the table has no row for it"
#guard refusal (lowerUnits [unitOf "u1" none] (senses := true)) ==
  "UnsupportedLowering: unit u1 feature senses: the table has no row for it"

-- Two readings that lower to the same statements.
#guard refusal (lowerUnits [unitOf "u1" none] [readingSet "rs" "u1" [fact "public", .not (fact "reviewed"), fact "public"]]) ==
  "ReadingsCollapsed: reading set rs readings 0 and 2 lower to the same statements"

-- References the document does not have, or of the wrong category.
#guard refusal (lowerUnits [unitOf "u1" none] [readingSet "rs" "u9" [fact "public", .not (fact "public")]]) ==
  "UnknownPart: reading set rs names unit u9, which the document does not have"
#guard refusal (lowerUnits [unitOf "u1" none] [readingSet "rs" "u1" [fact "public", .not (fact "public")]]
    [⟨"k", [("rs", ["x", "y"]), ("zz", ["x", "y"])]⟩]) ==
  "UnknownPart: coupling k names reading set zz, which is not an active reading set"
#guard refusal (lowerUnits [unitOf "u1" (some (.formula (fact "nowhere")))]) ==
  "UnknownPart: a premise of unit u1 names predicate nowhere, which the vocabulary does not declare"
#guard refusal (lowerUnits [unitOf "u1" none] (views := some [])) ==
  "UnknownPart: the unit views are not the document's units"

-- More than 64 choices: seven independent two-reading sets have 128; thirteen have 8192 combinations to enumerate.
def manySets (n : Nat) : List SourceUnit × List ActiveSet :=
  ((List.range n).map fun i => unitOf s!"u{i}" none,
   (List.range n).map fun i => readingSet s!"s{i}" s!"u{i}" [fact "public", .not (fact "public")])

#guard match lowerUnits (manySets 6).1 (manySets 6).2 with
  | .ok cs => cs.length == 64
  | .error _ => false
#guard refusal (lowerUnits (manySets 7).1 (manySets 7).2) == "ResourceLimit: 128 compatible choices, more than 64"
#guard refusal (lowerUnits (manySets 13).1 (manySets 13).2) ==
  "ResourceLimit: 8192 combinations of readings, more than 4096 to enumerate"

-- The judgment refusals, reused unchanged: a record bound to no base predicate, a specified unit that reads a judgment
-- term, and an open unit that lists a term it does not read.
#guard refusal (lowerUnits [unitOf "u1" none] (records := [(⟨"missing", ["agent"], "reviewer", []⟩, 0, 0)])) ==
  "JudgmentUnbound: missing"
#guard refusal (lowerUnits [unitOf "u1" (some (.formula (fact "redacted")))]) == "JudgmentNotChecked: u1 redacted"
#guard refusal (lowerUnits [unitOf "u1" (softContent releaseRule) (openOn ["redacted"])]
    (views := some [viewOf (unitOf "u1" (softContent releaseRule) (openOn ["redacted"])) "open"])) ==
  "JudgmentListedUnused: u1 redacted"

end VE.Experimental.CoreDocumentExamples
