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

def udhr (profiles : List String) : Json :=
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
  let limitation := Json.mkObj [("limitation", Json.mkObj [("name", "l29"), ("scope", "all"), ("kinds", "all"),
    ("decided_by", "unstated"), ("factors", none), ("conditions", Json.arr (udhrTerms.map fun t => Json.mkObj [
      ("name", .str t), ("role", if t == "just_requirements" then "necessary" else "sufficient"),
      ("verbalisation", .str t), ("decided_by", .null)]).toArray)])]
  let first := "Everyone has the right to freedom of opinion and expression.\n"
  let body := first ++ "Everyone shall be subject only to such limitations as meet the just requirements of " ++
    "morality, public order and the general welfare.\n"
  let front := Json.mkObj [("format", "ve-document@1"), ("environment", Json.mkObj [("language", "ve.core@0.2"),
      ("profiles", Lean.toJson profiles), ("spec_revision", "ve-v0.2-expand2-2026-09-25"),
      ("vocabulary", vocabulary)]),
    ("units", Json.arr #[Json.mkObj [("id", "u029"), ("span", Lean.toJson [0, first.length]), ("kind", "right"),
        ("meaning", "specified"), ("support", "none"), ("content", right)],
      Json.mkObj [("id", "u111"), ("span", Lean.toJson [first.length, body.length]), ("kind", "limitation"),
        ("meaning", Json.mkObj [("open", Lean.toJson udhrTerms)]), ("support", "none"), ("content", limitation)]]),
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

end VE.Judgments.ChainExamples
