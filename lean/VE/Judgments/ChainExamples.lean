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
      ("decided_by", "unresolved_decider"), ("necessary", Json.arr #[]), ("sufficient", Json.arr #[]),
      ("factors", Json.arr #[]), ("precedents", Json.arr #[]), ("jurisdiction", "document"), ("version", 1)]]),
    ("reading_sets", Json.arr #[Json.mkObj [("id", "s"), ("unit", "u0052.s01"), ("version", 1), ("status", "open"),
      ("readings", Json.arr readings.toArray), ("models", Json.mkObj models)]])]
  Json.mkObj [("id", "c"), ("document", .str ("---\n" ++ front.compress ++ "\n---\n" ++ body))]

def layer : List String := ["documents@1", "judgments@0", "norms@0", "relational-fol@0", "soft-norms@0"]
def noDocuments : List String := layer.erase "documents@1"
def plain : List String := layer.erase "judgments@0"

/-- The model's identities with and without `judgments@0` (`v₁`, `v₂`), read off a case stating it under `k`. -/
def ids (inputs : Bool) (profiles : List String := layer) : String × String :=
  match statedPairs (case profiles [] [("k", model inputs)]) with
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
def bothRules (profiles : List String) : Json :=
  let rule (name pred : String) (guard : Json) := Json.mkObj [("norm", Json.mkObj [("name", .str name),
    ("predicate", .str pred), ("sign", true), ("mode", "default"), ("guard", guard), ("unless", Json.arr #[]),
    ("over", Json.arr #[]), ("exception", Json.mkObj [("decided_by", "unstated"), ("sufficient", Json.arr #[]),
      ("necessary", Json.arr #[]), ("factors", Json.arr #[])])])]
  let unit (id : String) (span : List Nat) (listed : List String) (content : Json) := Json.mkObj [("id", .str id),
    ("span", Lean.toJson span), ("kind", "norm"), ("meaning", Json.mkObj [("open", Lean.toJson listed)]),
    ("support", "assumption"), ("content", content)]
  let record (name : String) := Json.mkObj [("name", .str name), ("arguments", Lean.toJson ["situation"]),
    ("decided_by", "unresolved_decider"), ("necessary", Json.arr #[]), ("sufficient", Json.arr #[]),
    ("factors", Json.arr #[]), ("precedents", Json.arr #[]), ("jurisdiction", "document"), ("version", 1)]
  let body := "Claude should always use good judgment when evaluating conversational inputs. Claude should ask.\n"
  let front := Json.mkObj [("format", "ve-document@1"), ("environment", environment profiles),
    ("units", Json.arr #[unit "u0052.s01" [0, 79] ["good_judgment", "soft__excepted__good_judgment"]
        (rule "good-judgment" "uses_judgment" (Json.arr #["and", u "evaluating_inputs", u "good_judgment"])),
      unit "u0036.s05" [79, body.length] ["genuinely_ambiguous", "soft__excepted__ask_clarification"]
        (rule "ask-clarification" "asks_clarification" (u "genuinely_ambiguous"))]),
    ("open_terms", Json.arr #[record "good_judgment", record "genuinely_ambiguous"])]
  Json.mkObj [("id", "c"), ("document", .str ("---\n" ++ front.compress ++ "\n---\n" ++ body))]

-- Admitted with the layer, each unit OPEN through its judgment; the twin is admitted too.
#guard match checkDocSets (bothRules layer), checkDocSets (bothRules plain) with
  | .ok a, .ok _ => a.getObjValD "judgments" == Json.mkObj [("used", Json.arr #[
      Json.mkObj [("term", "good_judgment"), ("units", Lean.toJson ["u0052.s01"])],
      Json.mkObj [("term", "genuinely_ambiguous"), ("units", Lean.toJson ["u0036.s05"])]]), ("unused", Json.arr #[])]
  | _, _ => false
-- What the layer stays apart from in this mode (`judgmentsApart`), each by its own text.
#guard ["alternatives@0", "rights@0", "risk@0"].all fun p =>
  refusal (bothRules ((p :: layer).mergeSort fun a b => decide (a ≤ b))) ==
    some s!"CheckerUnavailable: judgments@0 with {p} needs its composed Lean route"

end VE.Judgments.ChainExamples
