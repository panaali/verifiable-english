import VE.Compose.ContractExamples
import VE.Service.Document

/-! PC-1's examples (docs/spec/profile-composition.md 5.1): the reader's carve-outs and the clash validation on
F1.3l, F1.3m and F1.3o, over F1.1's soft document (constitution u0052.s01). Each request and its twin answer row 16
first; each request whose own exchange is not one-to-one has a twin whose exchange is not one-to-one either
(`swapInjective_twin`, proved in pc-1g: reviews/dri-decisions-20261031-pc-1.md). -/

namespace VE.Judgments.ChainExamples
open Lean (Json)
open VE.Service.Document

/-- F1.2b's rule: the judgment only in a carve-out (an `unless` clause). -/
def carved : VE.SoftNorms.SoftNode :=
  { toNode := { name := "n", pred := "asks", sign := true, guard := .top,
                carveOuts := [.unary "genuinely_ambiguous" (.var 0)], over := [] },
    mode := .default, rank := none, alterable := [], exception := none, hard := false }

-- F1.2b's reader: a soft rule's carve-outs are read (`softContent_formulas`).
#guard opensIn ["genuinely_ambiguous"] (softContent carved).formulas == ["genuinely_ambiguous"]

-- The spec stub's values (F1.3o): `j₁`'s own exchange is one-to-one and its twin's is not; `j₂`'s and `t`'s are not;
-- F1.3h's values (`k2` twice) are one-to-one on both sides.
#guard swapInjectiveOf ["a1", "w"] [("a1", "a1", "a2"), ("w", "a1", "a2")] (swap "a1" "a2")
#guard ["a1", "w"].map (swap "a1" "a2") == ["a2", "w"]
#guard clashRefusalOf true (some (swapInjectiveOf ["a2", "w"] [("a2", "a1", "a2"), ("w", "a1", "a2")]
  (swap "a1" "a2"))) == some swapClash
#guard clashRefusalOf (swapInjectiveOf ["a2", "w"] [("a2", "a1", "a2"), ("w", "a1", "a2")] (swap "a1" "a2"))
  none == some swapClash
#guard clashRefusalOf (swapInjectiveOf ["k1", "k1"] [("k1", "k1", "k2")] (swap "k1" "k2"))
  (some (swapInjectiveOf ["k2", "k2"] [("k2", "k1", "k2")] (swap "k1" "k2"))) == none

def u (p : String) : Json := Json.arr #["unary", .str p, Json.arr #["var", 0]]

def environment (profiles : List String) : Json := Json.mkObj [("language", "ve.core@0.2"),
  ("profiles", Lean.toJson profiles), ("spec_revision", "ve-v0.2-expand2-2026-09-25"),
  ("vocabulary", Json.mkObj [("sorts", Json.mkObj [("situation", Json.mkObj [("description", "a situation")])]),
    ("constants", Json.mkObj []),
    ("predicates", Json.mkObj [("evaluating_inputs", Json.mkObj [("arguments", Lean.toJson ["situation"]),
        ("description", "evaluating")]),
      ("good_judgment", Json.mkObj [("arguments", Lean.toJson ["situation"]), ("description", "good")]),
      ("genuinely_ambiguous", Json.mkObj [("arguments", Lean.toJson ["situation"]), ("description", "ambiguous")]),
      ("asks_clarification", Json.mkObj [("arguments", Lean.toJson ["situation"]), ("description", "asks"),
        ("regulated", Json.mkObj [("role", "obligation"), ("default", "deny"), ("act", "{0} clarify")])]),
      ("uses_judgment", Json.mkObj [("arguments", Lean.toJson ["situation"]), ("description", "uses"),
        ("regulated", Json.mkObj [("role", "obligation"), ("default", "deny"), ("act", "{0} use judgment")])])])])]

/-- F1.3h's distinguishing model: one situation, inputs being evaluated. -/
def model (inputs : Bool) : Json := Json.mkObj [("complete", true),
  ("domains", Json.mkObj [("situation", Lean.toJson ["s"])]), ("constants", Json.mkObj []),
  ("relations", Json.mkObj [("evaluating_inputs", Lean.toJson (if inputs then [["s"]] else ([] : List (List String)))),
    ("good_judgment", Lean.toJson ([] : List (List String))), ("uses_judgment", Lean.toJson ([] : List (List String)))])]

def reading (id : String) (refs : List (String × String)) : Json := Json.mkObj [("id", .str id), ("kind", "asserted"),
  ("meaning_id", "pending"), ("content", .null), ("admission", Json.mkObj [("who", "reviewer"), ("why", "a reading"),
    ("distinguishing_models", Json.mkObj (refs.map fun (o, k) => (o, Json.str k)))])]

/-- A case over F1.1's document with one reading set on its unit: `readings`, and `models` under their keys. -/
def case (profiles : List String) (readings : List Json) (models : List (String × Json)) : Json :=
  let rule := Json.mkObj [("name", "good-judgment"), ("predicate", "uses_judgment"), ("sign", true),
    ("mode", "default"), ("guard", Json.arr #["and", u "evaluating_inputs", u "good_judgment"]),
    ("unless", Json.arr #[]), ("over", Json.arr #[]), ("exception", Json.mkObj [("decided_by", "unstated"),
      ("sufficient", Json.arr #[]), ("necessary", Json.arr #[]), ("factors", Json.arr #[])])]
  let body := "Claude should always use good judgment when evaluating conversational inputs.\n"
  let front := Json.mkObj [("format", "ve-document@1"), ("environment", environment profiles),
    ("units", Json.arr #[Json.mkObj [("id", "u0052.s01"), ("span", Lean.toJson [0, body.length]), ("kind", "norm"),
      ("meaning", Json.mkObj [("open", Lean.toJson ["good_judgment"])]), ("support", "assumption"),
      ("content", Json.mkObj [("norm", rule)])]]),
    ("open_terms", Json.arr #[Json.mkObj [("name", "good_judgment"), ("arguments", Lean.toJson ["situation"]),
      ("decided_by", "unstated"), ("necessary", Json.arr #[]), ("sufficient", Json.arr #[]),
      ("factors", Json.arr #[]), ("precedents", Json.arr #[]), ("jurisdiction", "document"), ("version", 1)]]),
    ("reading_sets", Json.arr #[Json.mkObj [("id", "s"), ("unit", "u0052.s01"), ("version", 1), ("status", "open"),
      ("readings", Json.arr readings.toArray), ("models", Json.mkObj models)]])]
  Json.mkObj [("id", "c"), ("document", .str ("---\n" ++ front.compress ++ "\n---\n" ++ body))]

def layer : List String := ["documents@1", "judgments@0", "norms@0", "relational-fol@0", "soft-norms@0"]
def noDocuments : List String := layer.erase "documents@1"
def plain : List String := layer.erase "judgments@0"

/-- The model's identities with and without `judgments@0` (`v₁`, `v₂`), read off a case stating it under `k`. -/
def ids (inputs : Bool) (profiles : List String := layer) : String × String :=
  match statedPairs (case profiles [reading "r0" []] [("k", model inputs)]) with
  | [(_, v₁, v₂)] => (v₁, v₂)
  | _ => ("", "")

/-- The document mode's refusal of a case, if any. -/
def refusal (j : Json) : Option String :=
  match checkDocSets j with
  | .error e => some e
  | .ok _ => none

/-- Row 16 first on a case and on its twin, whose own exchange is not one-to-one. -/
def clashBothSides (j : Json) : Bool :=
  swapInjective (withoutJudgments j) == false &&
    [refusal j, refusal (withoutJudgments j)].all (· == some swapClash)

#guard (ids true).1 != (ids true).2 && (ids true).1 != (ids false).1

/-- F1.3l: F1.3h (two readings, model `d` under a key that is neither identity) with a third reading whose reference
names no model and reads `d`'s twin key. With `noDocuments`, F1.3m. -/
def f13l (profiles : List String) : Json :=
  case profiles [reading "r0" [("r1", "d"), ("r2", "d")], reading "r1" [("r0", "d"), ("r2", "d")],
    reading "r2" [("r0", (ids true profiles).2), ("r1", "d")]] [("d", model true)]

#guard swapInjective (f13l layer) == false && clashBothSides (f13l layer)
#guard swapInjective (f13l noDocuments) == false && clashBothSides (f13l noDocuments)
-- F1.3m's twin is a plain request, refused by its own exchange.
#guard (withoutJudgments (f13l noDocuments)) |> fun t => profilesOf t == plain.erase "documents@1" && swapInjective t == false

/-- F1.3o: two models of one content `c` (A and B), A under `key`, B under `w`; F1.3h's two readings reference them. -/
def f13o (profiles : List String) (key : String) : Json :=
  case profiles [reading "r0" [("r1", key)], reading "r1" [("r0", "w")]] [(key, model true), ("w", model true)]

-- `j₁`: its own exchange is one-to-one, its twin's is not; `j₂` and `t`: their own are not.
#guard swapInjective (f13o layer (ids true).1) && clashBothSides (f13o layer (ids true).1)
#guard swapInjective (f13o layer (ids true).2) == false && clashBothSides (f13o layer (ids true).2)
#guard swapInjective (f13o plain (ids true).2) == false && refusal (f13o plain (ids true).2) == some swapClash
-- The twin of `j₁` and of `j₂` is `t`'s document (its key exchanged; kept).
#guard [(ids true).1, (ids true).2].all fun k =>
  readingSetsOf (withoutJudgments (f13o layer k)) == readingSetsOf (f13o plain (ids true).2)
-- F1.3h's values: two readings referencing one model under its own identity pass the check on both sides.
#guard clashRefusal (case layer [reading "r0" [("r1", (ids false).1)], reading "r1" [("r0", (ids false).1)]]
  [((ids false).1, model false)]) == none

/-- F1.1 and F1.2 in one soft document: each unit's `open` meaning lists its judgment and its rule's soft decision
predicate (`softLayer`'s names, declared and generated). -/
def bothRules (profiles : List String) (conditions : List (String × Json) := []) : Json :=
  let given (k : String) := Json.arr (conditions.filterMap fun (k', f) => if k' == k then some f else none).toArray
  let rule (name pred : String) (guard : Json) := Json.mkObj [("norm", Json.mkObj [("name", .str name),
    ("predicate", .str pred), ("sign", true), ("mode", "default"), ("guard", guard), ("unless", Json.arr #[]),
    ("over", Json.arr #[]), ("exception", Json.mkObj [("decided_by", "unstated"), ("sufficient", given "sufficient"),
      ("necessary", given "necessary"), ("factors", Json.arr #[])])])]
  let unit (id : String) (span : List Nat) (listed : List String) (content : Json) := Json.mkObj [("id", .str id),
    ("span", Lean.toJson span), ("kind", "norm"), ("meaning", Json.mkObj [("open", Lean.toJson listed)]),
    ("support", "assumption"), ("content", content)]
  let record (name : String) := Json.mkObj [("name", .str name), ("arguments", Lean.toJson ["situation"]),
    ("decided_by", "unstated"), ("necessary", Json.arr #[]), ("sufficient", Json.arr #[]),
    ("factors", Json.arr #[]), ("precedents", Json.arr #[]), ("jurisdiction", "document"), ("version", 1)]
  let body := "Claude should always use good judgment when evaluating conversational inputs. Claude should ask.\n"
  let front := Json.mkObj [("format", "ve-document@1"), ("environment", environment profiles),
    ("units", Json.arr #[unit "u0052.s01" [0, 79] ["good_judgment", "soft__excepted__good_judgment"]
        (rule "good-judgment" "uses_judgment" (Json.arr #["and", u "evaluating_inputs", u "good_judgment"])),
      unit "u0036.s05" [79, body.length] ["genuinely_ambiguous", "soft__excepted__ask_clarification"]
        (rule "ask-clarification" "asks_clarification" (u "genuinely_ambiguous"))]),
    ("open_terms", Json.arr #[record "good_judgment", record "genuinely_ambiguous"])]
  Json.mkObj [("id", "c"), ("document", .str ("---\n" ++ front.compress ++ "\n---\n" ++ body))]

-- The profiles every check reads (`profilesOf`, row 16's environments and the scope test), read directly.
#guard profilesOf (bothRules layer) == layer && profilesOf (bothRules plain) == plain &&
  profilesOf (Json.mkObj [("id", "c"), ("document", "no front matter")]) == []

-- Admitted with the layer, each unit OPEN through its judgment; the twin is admitted too.
#guard match checkDocSets (bothRules layer), checkDocSets (bothRules plain) with
  | .ok a, .ok _ => a.getObjValD "judgments" == Json.mkObj [("used", Json.arr #[
      Json.mkObj [("term", "good_judgment"), ("units", Lean.toJson ["u0052.s01"])],
      Json.mkObj [("term", "genuinely_ambiguous"), ("units", Lean.toJson ["u0036.s05"])]]), ("unused", Json.arr #[])]
  | _, _ => false
-- What the layer stays apart from in this mode (`judgmentsApart`), each by its own text; `rights@0` is read since
-- pc-1g (F1.4 below).
#guard ["alternatives@0", "risk@0"].all fun p =>
  refusal (bothRules ((p :: layer).mergeSort fun a b => decide (a ≤ b))) ==
    some s!"CheckerUnavailable: judgments@0 with {p} needs its composed Lean route"

/-! pc-1 review F1: a rule's exception conditions are rules of the soft theory that `softContent` does not read, so
a document with one keeps main's refusal of the pairing (`exceptionConditioned`), in a unit or in a `MIXED` part, the
condition a judgment or not; empty or absent conditions do not. -/

def withCondition (k : String) (inPart : Bool) : Json :=
  let unit := Json.mkObj [("id", "u"), ("content", Json.mkObj [("norm", Json.mkObj [("mode", "default"),
    ("exception", Json.mkObj [(k, Json.arr #[u "good_judgment"])])])])]
  Json.arr #[if inPart then Json.mkObj [("id", "m"), ("status", "MIXED"), ("parts", Json.arr #[unit])] else unit]

#guard [("sufficient", false), ("necessary", false), ("sufficient", true), ("necessary", true)].all fun (k, p) =>
  exceptionConditioned (withCondition k p)
#guard !exceptionConditioned (withCondition "factors" false) && !exceptionConditioned (bothRules layer) &&
  !exceptionConditioned (Json.arr #[Json.mkObj [("content", Json.mkObj [("norm", Json.mkObj [("mode", "strict")])])]])
#guard ["sufficient", "necessary"].all fun k => [u "good_judgment", u "evaluating_inputs"].all fun f =>
  refusal (bothRules layer [(k, f)]) == some "CheckerUnavailable: judgments@0 with soft-norms@0 needs its composed Lean route"

-- pc-1g review F1: the same exception reader visits all written rights rules, added lines, and MIXED parts.
def rightsWithCondition (block ruleKey field : String) (inPart : Bool) : Json :=
  let rule := Json.mkObj [("mode", "default"), ("exception", Json.mkObj
    [(field, Json.arr #[u "good_judgment"])])]
  let line := Json.mkObj [(ruleKey, rule)]
  let content := Json.mkObj [(block, Json.mkObj [("lines", Json.arr #[line])])]
  let unit := Json.mkObj [("content", content)]
  Json.arr #[if inPart then Json.mkObj [("parts", Json.arr #[unit])] else unit]

#guard ["right", "right_lines"].all fun block =>
  ["norm", "liberty", "recognition"].all fun key =>
    ["sufficient", "necessary"].all fun field =>
      [false, true].all fun part => exceptionConditioned (rightsWithCondition block key field part)

def rightsWithEmptyCondition : Json :=
  let rule := Json.mkObj [("exception", Json.mkObj [("sufficient", Json.arr #[])])]
  let line := Json.mkObj [("norm", rule)]
  let content := Json.mkObj [("right", Json.mkObj [("lines", Json.arr #[line])])]
  Json.arr #[Json.mkObj [("content", content)]]

#guard !exceptionConditioned (rightsWithCondition "right" "norm" "factors" false) &&
  !exceptionConditioned rightsWithEmptyCondition

-- The profile gate consumes the scan: no conditioned rights shape may reach judgment usage.
#guard match frontOf (bothRules (("rights@0" :: layer).mergeSort fun a b => decide (a ≤ b))) with
  | some (front, _) => ["right", "right_lines"].all fun block =>
      ["norm", "liberty", "recognition"].all fun key =>
        ["sufficient", "necessary"].all fun field =>
          [false, true].all fun part =>
            match environmentOf (front.getObjValD "environment") (rightsWithCondition block key field part) with
            | .error message => message == "CheckerUnavailable: judgments@0 with rights@0 needs its composed Lean route"
            | .ok _ => false
  | none => false

-- Both orders of the minimal profile pair fix the gate's fault when either profile is dropped.
-- The preceding guards cover every written rights-rule shape and condition field.
#guard (["judgments@0", "rights@0"] :: [["rights@0", "judgments@0"]]).all fun profiles =>
  match environmentOf (Json.mkObj [("profiles", Lean.toJson profiles)])
      (rightsWithCondition "right" "norm" "sufficient" false) with
  | .error message => message == "CheckerUnavailable: judgments@0 with rights@0 needs its composed Lean route"
  | .ok _ => false

/-! pc-1 review F2: row 16 reads reading sets of 1 to 64 readings; a case with a set of more is answered by the
chain's own check, in its order, before any work over its stated values. F1.3l's clash with readings added: at 64 it
is row 16's, at 65 the chain's. -/

def f13lWith (n : Nat) : Json :=
  case layer ([reading "r0" [("r1", "d"), ("r2", "d")], reading "r1" [("r0", "d"), ("r2", "d")],
    reading "r2" [("r0", (ids true layer).2), ("r1", "d")]] ++ (List.range n).map fun i => reading s!"x{i}" [])
    [("d", model true)]

#guard refusal (f13lWith 61) == some swapClash
#guard refusal (f13lWith 62) == some "reading sets hold 1 to 64 readings" && statedIds (f13lWith 62) == [] &&
  statedPairs (f13lWith 62) == []

-- Row 16 runs once on a `scope@0` request: first in the scope branch, and `checkCore`, which that branch calls on
-- GOVERN's case, does not run it again.
#guard let j := f13l (("scope@0" :: noDocuments).mergeSort fun a b => decide (a ≤ b))
  refusal j == some swapClash && (match checkCore j with
    | .error e => e != swapClash
    | .ok _ => true)

-- The run's check is the spec's on values a set states twice and on the stub's values (`swapInjectiveH_eq`).
#guard [(["k1", "k1"], [("k1", "k1", "k2")]), (["a2", "w"], [("a2", "a1", "a2"), ("w", "a1", "a2")]),
    (["a1", "w", "a1"], [("a1", "a1", "a2"), ("w", "a1", "a2")])].all fun (ids, pairs) =>
  swapInjectiveH ids pairs == swapInjectiveOf ids pairs (exchangeOf pairs)

/-! pc-1g, the statement stop (docs/profile-composition/pc-1g/REPORT.md): `swap_correct` as the spec states it is
false. One key `K` stated in two reading sets for two contents, `K` the layer identity of the second set's model:
the exchange is one-to-one on the values (`swapInjective`), `(K, b₁, b₂)` is a pair with `K = b₁`, and the exchange
of `K` (by its first pair, the first set's) is `K`, not `b₂`. No digest collision is needed. -/

/-- `case` with a second reading set `s2` on the same unit, stating its model `m₂` under `k₂`. -/
def twoSets (k₁ : String) (m₁ : Json) (k₂ : String) (m₂ : Json) : Json :=
  let j := case layer [reading "r0" []] [(k₁, m₁)]
  match frontOf j with
  | some (front, body) =>
    let s₁ := (readingSetsIn front).headD .null
    let s₂ := (s₁.setObjVal! "id" "s2").setObjVal! "models" (Json.mkObj [(k₂, m₂)])
    j.setObjVal! "document" (.str ("---\n" ++ (front.setObjVal! "reading_sets" (Json.arr #[s₁, s₂])).compress ++
      "\n---\n" ++ body))
  | none => j

#guard let j := twoSets (ids true).1 (model false) (ids true).1 (model true)
  swapInjective j && (statedIds j).contains (ids true).1 && match statedPairs j with
    | [_, (x, v₁, v₂)] => x == v₁ && (exchange j x == v₂) == false
    | _ => false

/-! pc-1g: F1.4, UDHR u111 (Art. 29(2)) as a rights limitation whose conditions are the four bound judgments, beside
Art. 19 as a right, a part document (tests/data/composition/pc1g/udhr-u111.json): admitted with the layer, u111 OPEN
and using the four; `Lim_D` the same with and without the layer; the twin's verdict fields equal. -/

def udhrTerms : List String := ["general_welfare", "just_requirements", "morality", "public_order"]

def udhr (profiles : List String) (split : Bool := false) : Json :=
  let args := Lean.toJson ["person"]
  let none := Json.arr #[]
  let vocabulary := Json.mkObj [("sorts", Json.mkObj [("person", Json.mkObj [("description", "a person")])]),
    ("constants", Json.mkObj []), ("predicates", Json.mkObj (("express_permitted", Json.mkObj [("arguments", args),
      ("description", "may express"), ("regulated", Json.mkObj [("role", "permission"), ("default", "allow"),
        ("act", "{0} express opinions")])]) :: udhrTerms.map fun t =>
      (t, Json.mkObj [("arguments", args), ("description", .str t)]))),
    ("rights", Json.mkObj [("holders", args), ("bearers", args), ("protected", none), ("alters", Json.mkObj [])]),
    ("soft", Json.mkObj [("parties", none), ("ranks", none), ("outranks", none),
      ("outranking", Json.mkObj [("mode", "strict")])])]
  let right := Json.mkObj [("right", Json.mkObj [("name", "r19"), ("holder", "person"), ("lines", Json.arr #[
    Json.mkObj [("kind", "liberty"), ("cites", Json.mkObj []), ("norm", Json.mkObj [("name", "express-19"),
      ("predicate", "express_permitted"), ("sign", true), ("guard", Json.arr #["top"]), ("unless", none),
      ("over", none)])]])])]
  let limitation (name : String) (terms : List String) := Json.mkObj [("limitation", Json.mkObj [("name", .str name),
    ("scope", "all"), ("kinds", "all"), ("decided_by", "unstated"), ("factors", none), ("conditions",
      Json.arr (terms.map fun t => Json.mkObj [("name", .str t), ("verbalisation", .str t), ("decided_by", .null),
        ("role", if t == "just_requirements" then "necessary" else "sufficient")]).toArray)])]
  let limit (id : String) (span : List Nat) (terms : List String) := Json.mkObj [("id", .str id),
    ("span", Lean.toJson span), ("kind", "limitation"), ("meaning", Json.mkObj [("open", Lean.toJson terms)]),
    ("support", "none"), ("content", limitation (id.replace "u111" "l29") terms)]
  let first := "Everyone has the right to freedom of opinion and expression.\n"
  let body := first ++ "Everyone shall be subject only to such limitations as meet the just requirements of " ++
    "morality, public order and the general welfare.\n"
  let front := Json.mkObj [("format", "ve-document@1"), ("environment", Json.mkObj [("language", "ve.core@0.2"),
      ("profiles", Lean.toJson profiles), ("spec_revision", "ve-v0.2-expand2-2026-09-25"),
      ("vocabulary", vocabulary)]),
    ("units", Json.arr (#[Json.mkObj [("id", "u029"), ("span", Lean.toJson [0, first.length]), ("kind", "right"),
        ("meaning", "specified"), ("support", "none"), ("content", right)]
      ] ++ (if split then #[limit "u111a" [first.length, first.length + 40] (udhrTerms.take 2),
        limit "u111b" [first.length + 40, body.length] (udhrTerms.drop 2)]
      else #[limit "u111" [first.length, body.length] udhrTerms]))),
    ("open_terms", Json.arr (udhrTerms.map fun t => Json.mkObj [("name", .str t), ("arguments", args),
      ("decided_by", "unstated"), ("necessary", none), ("sufficient", none), ("factors", none),
      ("precedents", none), ("jurisdiction", "document"), ("version", 1)]).toArray)]
  Json.mkObj [("id", "c"), ("document", .str ("---\n" ++ front.compress ++ "\n---\n" ++ body))]

def rightsLayer : List String :=
  ["documents@1", "judgments@0", "norms@0", "relational-fol@0", "rights@0", "soft-norms@0"]

/-- `Lim_D`, labelled, as the document mode's rights reader decodes the case's rights source. -/
def udhrLim (profiles : List String) : Option (List (String × VE.Formula)) := do
  let (front, _) ← frontOf (udhr profiles)
  let E ← (environmentOf (front.getObjValD "environment") (front.getObjValD "units")).toOption
  let raw := match front.getObjValD "units" with
    | .arr us => us.toList
    | _ => []
  let R ← (rightsDoc E front udhrTerms raw).toOption
  pure (VE.Rights.limPremisesLabelled R.src.D)

#guard (udhrLim rightsLayer).getD [] != [] && udhrLim rightsLayer == udhrLim (rightsLayer.erase "judgments@0")
#guard match checkDocSets (udhr rightsLayer), checkDocSets (withoutJudgments (udhr rightsLayer)) with
  | .ok a, .ok b => unitStatuses a == [("u029", "OPEN"), ("u111", "OPEN")] &&
      a.getObjValD "judgments" == Json.mkObj [("unused", Json.arr #[]), ("used", Json.arr (udhrTerms.map fun t =>
        Json.mkObj [("term", .str t), ("units", Lean.toJson ["u111"])]).toArray)] &&
      (unitStatuses b).map (·.1) == ["u029", "u111"]
  | _, _ => false
-- The rights reader by block: a limitation reads its conditions, a right its lines, a bar nothing.
#guard match frontOf (udhr rightsLayer) with
  | some (front, _) => match (front.getObjValD "units").getArrVal? 1 with
    | .ok u => (do
        let E ← (environmentOf (front.getObjValD "environment") (front.getObjValD "units")).toOption
        let R ← (rightsDoc E front udhrTerms [u]).toOption
        let fs ← (blockFormulas R.src.D (u.getObjValD "content")).toOption
        pure (opensIn udhrTerms fs == udhrTerms)) == some true
    | .error _ => false
  | none => false

-- The rights reader by line: a rule's guard, then each `unless` clause; a power's `liberty` and `recognition` (an
-- absent guard is `⊤`).
#guard match linesFormulas (Json.mkObj [("lines", Json.arr #[
    Json.mkObj [("kind", "claim"), ("norm", Json.mkObj [("guard", u "a"), ("unless", Json.arr #[u "b", u "c"])])],
    Json.mkObj [("kind", "power"), ("liberty", Json.mkObj [("guard", u "d")]),
      ("recognition", Json.mkObj [("unless", Json.arr #[u "e"])])]])]) with
  | .ok fs => opensIn ["a", "b", "c", "d", "e"] fs == ["a", "b", "c", "d", "e"] && fs.length == 6
  | .error _ => false
-- The rights source's author formulas read the limitation's conditions by name (`correlate_judged`'s right side).
#guard match frontOf (udhr rightsLayer) with
  | some (front, _) => (do
      let E ← (environmentOf (front.getObjValD "environment") (front.getObjValD "units")).toOption
      let raw := match front.getObjValD "units" with
        | .arr us => us.toList
        | _ => []
      let R ← (rightsDoc E front udhrTerms raw).toOption
      pure (opensIn udhrTerms (rightsAuthorFormulas R.src.D) == udhrTerms)) == some true
  | none => false

/-- F1.4's rights source as the document mode decodes it (`rightsDoc`). -/
def udhrRights (split : Bool := false) : Option VE.Rights.RightsDoc := do
  let (front, _) ← frontOf (udhr rightsLayer split)
  let E ← (environmentOf (front.getObjValD "environment") (front.getObjValD "units")).toOption
  let raw := match front.getObjValD "units" with
    | .arr us => us.toList
    | _ => []
  pure (← (rightsDoc E front udhrTerms raw).toOption).src.D

-- u111 as two limitations, two judgments each: each unit reads its own limitation's conditions, and the source's
-- author formulas read all four; a bar block reads nothing.
#guard match checkDocSets (udhr rightsLayer true) with
  | .ok a => unitStatuses a == [("u029", "OPEN"), ("u111a", "OPEN"), ("u111b", "OPEN")]
  | .error _ => false
#guard ((udhrRights true).map fun R => opensIn udhrTerms (rightsAuthorFormulas R)) == some udhrTerms &&
  ((udhrRights).bind fun R => (blockFormulas R (Json.mkObj [("bar", Json.mkObj [("name", "b30")])])).toOption) ==
    some []

/-! pc-1g: F1.3b, F1.3c, F1.3i, F1.3j and F1.3k on F1.1's document (spec 5.1). -/

/-- A case with its front matter's first unit edited by `f`. -/
def editUnit (j : Json) (f : Json → Json) : Json :=
  match frontOf j with
  | some (front, body) => match (front.getObjValD "units").getArrVal? 0 with
    | .ok u => j.setObjVal! "document" (.str ("---\n" ++
        (front.setObjVal! "units" (Json.arr #[f u])).compress ++ "\n---\n" ++ body))
    | .error _ => j
  | none => j

def f11 : Json := case layer [reading "r0" []] []

-- F1.3b: a unit `meaning_id` wrong under both environments is refused on both sides (the exchange keeps it).
#guard let j := editUnit f11 (·.setObjVal! "meaning_id" (.str (String.mk (List.replicate 64 '0'))))
  [refusal j, refusal (withoutJudgments j)].all (· == some "unit meaning id does not match content")
/-- F1.3c: F1.1 with its judgment binary, declared with repeated argument sorts (`["situation", "situation"]`). -/
def f13c : Json := match frontOf f11 with
  | some (front, body) =>
    let two := Lean.toJson ["situation", "situation"]
    let record := ((front.getObjValD "open_terms").getArrVal? 0).toOption.getD .null
    let env := front.getObjValD "environment"
    let voc := env.getObjValD "vocabulary"
    let env := env.setObjVal! "vocabulary" (voc.setObjVal! "predicates" ((voc.getObjValD "predicates").setObjVal!
      "good_judgment" (Json.mkObj [("arguments", two), ("description", "good")])))
    let unit := ((front.getObjValD "units").getArrVal? 0).toOption.getD .null
    let norm := ((unit.getObjValD "content").getObjValD "norm").setObjVal! "guard" (Json.arr #["and",
      u "evaluating_inputs", Json.arr #["binary", "good_judgment", Json.arr #["var", 0], Json.arr #["var", 0]]])
    let front := ((front.setObjVal! "open_terms" (Json.arr #[record.setObjVal! "arguments" two])).setObjVal!
      "environment" env).setObjVal! "units" (Json.arr #[unit.setObjVal! "content" (Json.mkObj [("norm", norm)])])
    f11.setObjVal! "document" (.str ("---\n" ++ front.compress ++ "\n---\n" ++ body))
  | none => f11

-- F1.3c: admitted with the layer; the twin refused by W2, the one relaxation (`layerRelaxes`).
#guard refusal f13c == none && (refusal (withoutJudgments f13c)).any layerRelaxes.contains
-- F1.3i: an authored OPEN; its status-omitted form succeeds with equal verdict fields and statuses (2c).
#guard let j := editUnit f11 (·.setObjVal! "status" "OPEN")
  !noUnitStatus j && noUnitStatus (withoutStatuses j) && match checkDocSets j, checkDocSets (withoutStatuses j) with
    | .ok a, .ok b => verdictFields a == verdictFields b && unitStatuses a == unitStatuses b &&
        unitStatuses a == [("u0052.s01", "OPEN")]
    | _, _ => false
-- F1.3j, F1.3k: an authored status the original request's own validation refuses, never a refusal of the layer.
#guard [(Json.str "CHECKED", "unit status contradicts content, meaning, or active reading set"),
    ((5 : Nat), "invalid unit status")].all fun (v, e) =>
  refusal (editUnit f11 (·.setObjVal! "status" v)) == some e && !layerRefusal e
-- 2d: the layer's own refusals and gate texts are accepted, validation texts are not.
#guard layerRefusal "JudgmentListedUnused: u0036.s05 reasonable" &&
  layerRefusal "UnsupportedProfile: judgments@0 requires documents@1" &&
  layerRefusal "CheckerUnavailable: judgments@0 with alternatives@0 needs its composed Lean route" &&
  !layerRefusal swapClash && !layerRefusal "unit meaning id does not match content" &&
  !layerRefusal "UnsupportedProfile: rights@0 is required"

-- 2d, each of the layer's codes.
#guard ["JudgmentListedUnused", "JudgmentNotListed", "JudgmentNotChecked", "JudgmentUnbound", "JudgmentArguments",
  "JudgmentRegulated", "JudgmentCriterionAsUnit", "JudgmentDecider"].all fun c => layerRefusal (c ++ ": u x")

/-- A case with its units' authored statuses set, unit by unit (`none`: no status). -/
def withStatuses (j : Json) (statuses : List (Option String)) : Json :=
  match frontOf j with
  | some (front, body) => match front.getObjValD "units" with
    | .arr us => j.setObjVal! "document" (.str ("---\n" ++ (front.setObjVal! "units" (.arr (us.toList.zip statuses
        |>.map (fun (u, s) => match s with
          | some s => u.setObjVal! "status" (.str s)
          | none => u)).toArray)).compress ++ "\n---\n" ++ body))
    | _ => j
  | none => j

-- 2b, 2c on two units: a status on either unit is stated; `withoutStatuses` removes both and keeps both units; a case
-- without front matter or units states none.
#guard [[none, some "OPEN"], [some "OPEN", none]].all
    (fun ss => !noUnitStatus (withStatuses (bothRules layer) ss)) &&
  noUnitStatus (Json.mkObj [("id", "c"), ("document", "no front matter")]) &&
  noUnitStatus (Json.mkObj [("id", "c"), ("document", "---\n{\"format\":\"ve-document@1\"}\n---\nx\n")])
#guard let j := withoutStatuses (withStatuses (bothRules layer) [some "OPEN", some "OPEN"])
  noUnitStatus j &&
    (frontOf j).map (fun (f, _) => (f.getObjValD "units").getArr?.toOption.map (·.size)) == some (some 2)

/-- 2e's answer: units `u0`, `u1`; reading sets `s0`, `s1`, each with three models out of key order and readings `r0`,
`r1` that reference two of them. With `ids`, as the mode answers; without, as `verdictFields` must leave it. -/
def answer2e (ids : Bool) : Json :=
  let given (fields : List (String × Json)) : List (String × Json) := if ids then fields else []
  let always (fields : List (String × Json)) : List (String × Json) := fields
  let unit (i : String) := Json.mkObj (always [("id", .str i), ("kind", "norm")] ++
    given [("status", "OPEN"), ("meaning_id", .str ("m" ++ i))])
  let reading (r : String) := Json.mkObj (always [("id", .str r), ("admission", Json.mkObj [("distinguishing_models",
    if ids then Json.mkObj [("r1", "k1"), ("r2", "k2")] else Json.arr #["r1", "r2"])])] ++
    given [("meaning_id", .str ("m" ++ r))])
  let set (s : String) := Json.mkObj [("id", .str s), ("readings", Json.arr #[reading "r0", reading "r1"]),
    ("models", if ids then Json.mkObj [("k1", "A"), ("k2", "C"), ("k3", "B")] else Json.arr #["A", "B", "C"])]
  Json.mkObj (always [("id", "c"), ("status", "ok"), ("source", "t"), ("units", Json.arr #[unit "u0", unit "u1"]),
    ("reading_sets", Json.arr #[set "s0", set "s1"])] ++ given [("document_id", "d"), ("source_id", "s"),
      ("coverage", Json.mkObj []), ("judgments", Json.mkObj []), ("judgment_lines", Json.mkObj []),
      ("undeclared_evaluative", Json.arr #[])])

-- 2e on an answer: the fields the layer may change and the identities are dropped, every other field kept.
#guard verdictFields (answer2e true) == answer2e false

/-! pc-1g: F1.1 and F1.6, F1.4's twin. The case and its twin have the same verdict fields (`undeclared_evaluative`
dropped, DRI 2026-11-03 pc-1g stop item 4) and their own identities. -/

#guard [f11, udhr rightsLayer].all fun j => match checkDocSets j, checkDocSets (withoutJudgments j) with
  | .ok a, .ok b => verdictFields a == verdictFields b && a.getObjValD "document_id" != b.getObjValD "document_id" &&
      (unitStatuses a).map (·.1) == (unitStatuses b).map (·.1)
  | _, _ => false
#guard match checkDocSets f11, checkDocSets (withoutJudgments f11) with
  | .ok a, .ok b => unitStatuses a == [("u0052.s01", "OPEN")] &&
      ((a.getObjValD "units").getArrVal? 0 |>.toOption |>.map (·.getObjValD "meaning_id")) !=
        ((b.getObjValD "units").getArrVal? 0 |>.toOption |>.map (·.getObjValD "meaning_id"))
  | _, _ => false

/-! pc-1g, the trusted boundary `Json.compress` / `Json.parse` (DRI 2026-11-03 pc-1g stop item 2: the kernel cannot
unfold either in Lean v4.24.0, so their round trip is checked, not proved). A twin reads back the front matter
`withoutJudgments` built, on every fixture; and on values the renderer emits, drawn by a fixed linear congruential
generator: escapes, non-ASCII and astral characters, naturals up to 2^53-1, nested arrays and objects. -/

/-- The front matter `withoutJudgments` builds for a case with no exchange (`withoutJudgmentsIn []`), as a value. -/
def twinFront (j : Json) : Option Json := (frontOf j).map fun (front, _) =>
  front.setObjVal! "environment" (VE.Compose.withoutDocumentLayers (front.getObjValD "environment"))

#guard [f11, f13c, udhr rightsLayer, bothRules layer, f13l noDocuments].all fun j =>
  (frontOf (withoutJudgments j)).map (·.1) == twinFront j && (twinFront j).isSome

/-- A leaf the renderer emits, by `seed`: a string with escapes, non-ASCII and astral characters, a natural up to
2^53-1, a Boolean or `null`. -/
def drawnLeaf (seed : Nat) : Json :=
  match seed % 4 with
  | 0 => .str (String.mk ((List.range (seed / 4 % 9)).map fun i =>
      #['a', '"', '\\', '\n', '\t', 'é', '𝔸', '\u0001', '/', ' '][(seed / 36 + i * 7) % 10]!))
  | 1 => .num (seed * 2654435761 % 9007199254740992 : Nat)
  | 2 => .bool (seed % 8 < 4)
  | _ => .null

/-- A value of `depth` levels at most, by `seed`: arrays and objects of up to 3 members, keys with escapes. -/
def drawn : Nat → Nat → Json
  | 0, seed => drawnLeaf seed
  | depth + 1, seed =>
    let next (i : Nat) := (seed * 1103515245 + 12345 + i * 7919) % 2147483648
    match seed % 5 with
    | 0 => .arr ((List.range (seed / 5 % 4)).map fun i => drawn depth (next i)).toArray
    | 1 => Json.mkObj ((List.range (seed / 5 % 4)).map fun i =>
        (s!"k{next i % 13}\"é𝔸", drawn depth (next (i + 1))))
    | _ => drawnLeaf (seed / 5)

#guard (List.range 300).all fun n => let v := drawn 4 (n * 2654435761 % 2147483648)
  (Json.parse v.compress).toOption == some v

/-! pc-1tm (trust mutants of `checkDocSetsFast`, the run `checkDocSets_eq_fast` makes the compiler use): with one
governed set, on `i1` (`VE.Compose.ContractExamples.governedSet`), the run admits the case and hands the chain the
governed sets (`withSets`); the units alone (`withUnits`) are refused. It reads no `checkDocSets`: a mutant of the run
breaks that `@[csimp]` lemma, and a check reading it is no kill (trust_mutants' probe). -/

#guard let j := VE.Compose.ContractExamples.governedSet
  (checkDocSetsFast j).isOk && ((do
    let D ← VE.Scope.decodeScope j
    let out ← VE.Scope.governSetsWith VE.Scope.governFast D
    pure (VE.Scope.governedSetUnits D, (checkCore (withUnits j out)).isOk,
      (checkDocSetsFast j).toOption == (do pure (VE.Scope.foldGovernors D (← checkCore (withSets j out)))).toOption)) :
    Except String _).toOption == some (["i1"], false, true)

end VE.Judgments.ChainExamples
