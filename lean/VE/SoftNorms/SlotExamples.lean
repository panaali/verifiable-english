import VE.SoftNorms.SlotSound

/-! Examples of the slot kinds `slot-certificate` and `slot-conflict` (kb-3) on fixture (a) of
tests/test_slot_premises.py: two strict rules over act X, `h` requiring it where `v` holds and `k` forbidding it
where `w` holds, which collide where both hold; the fact `forall x. not (v(x) and w(x))` excludes that
situation. The packages were proved by Python's prover over `Background_base′ ++ [fact]` (the test's
`slot_packages`) and are replayed here by `replaySlotConflict`. Each `#guard` is the Lean twin of a case of the
test module (fixture (a), T1, T3, T4, T5). -/
namespace VE.SoftNorms.SlotExamples
open Lean VE.SoftNorms.Run

def environmentText : String :=
  r#"{"language": "ve.core@0.2", "profiles": ["norms@0", "relational-fol@0", "soft-norms@0"], "spec_revision": "ve-v0.2-expand2-2026-09-25", "vocabulary": {"sorts": {"assistant": {"description": "assistant"}, "user": {"description": "user"}}, "predicates": {"x_required": {"arguments": ["assistant"], "description": "obligation", "regulated": {"role": "obligation", "default": "deny", "act": "{0} do x", "permission": "x_permitted"}}, "x_permitted": {"arguments": ["assistant"], "description": "permission", "regulated": {"role": "permission", "default": "allow", "act": "{0} do x"}}, "v": {"arguments": ["assistant"], "description": "v"}, "w": {"arguments": ["assistant"], "description": "w"}}, "constants": {}}}"#

def normsText : String :=
  r#"[{"norm": {"name": "h", "predicate": "x_required", "sign": true, "guard": ["unary", "v", ["var", 0]], "unless": [], "over": []}}, {"norm": {"name": "k", "predicate": "x_required", "sign": false, "guard": ["unary", "w", ["var", 0]], "unless": [], "over": []}}]"#

/-- Conflict packages for the three targets over `Background_base′ ++ [fact]`. -/
def packagesText : String :=
  r#"{"x_permitted":{"environment_id":"3eb973d9d7889fa10550e4a1fdf13ac3230ecfc7c6c58f90ddbc74ed72acb728","document_hash":"35fdfc1ada37122d81b9e47785370e8ab6dbaaad49b3ec16270874c73495a200","target":"x_permitted","certificate":{"checker_version":"ve-tableau-checker@2","environment_id":"6f481de1d35d7f6f57feda072e16b966811032050e61d5d9ff79fbce9573a67b","premise_meaning_ids":["d90d71302dab0516f2b61332f617bdb32c4247049fb95c00d18a92d31e3c5b6b"],"conclusion_meaning_id":"0301a6ad25138b637148ca8003ef4af569021bb4ab4b57cc01c60a83644b5e68","trace":{"rule":"expand","at":1,"children":[{"rule":"expand","at":2,"children":[{"rule":"expand","at":3,"children":[{"rule":"close"}]}]}]}}},"x_required":{"environment_id":"3eb973d9d7889fa10550e4a1fdf13ac3230ecfc7c6c58f90ddbc74ed72acb728","document_hash":"35fdfc1ada37122d81b9e47785370e8ab6dbaaad49b3ec16270874c73495a200","target":"x_required","certificate":{"checker_version":"ve-tableau-checker@2","environment_id":"6f481de1d35d7f6f57feda072e16b966811032050e61d5d9ff79fbce9573a67b","premise_meaning_ids":["d90d71302dab0516f2b61332f617bdb32c4247049fb95c00d18a92d31e3c5b6b"],"conclusion_meaning_id":"096b9827ae4cd5a4e51e6c32eba060796e429853679dab11d5cbc3654b5dbcd3","trace":{"rule":"expand","at":1,"children":[{"rule":"expand","at":0,"children":[{"rule":"expand","at":2,"children":[{"rule":"expand","at":3,"children":[{"rule":"expand","at":4,"children":[{"rule":"expand","at":5,"children":[{"rule":"expand","at":6,"children":[{"rule":"close"},{"rule":"expand","at":7,"children":[{"rule":"close"},{"rule":"expand","at":9,"children":[{"rule":"expand","at":11,"children":[{"rule":"close"}]}]}]}]},{"rule":"expand","at":6,"children":[{"rule":"close"},{"rule":"expand","at":7,"children":[{"rule":"close"},{"rule":"expand","at":10,"children":[{"rule":"expand","at":11,"children":[{"rule":"close"}]}]}]}]}]}]}]}]}],"parameter":"w:0"}]}}},"x_required->x_permitted":{"environment_id":"3eb973d9d7889fa10550e4a1fdf13ac3230ecfc7c6c58f90ddbc74ed72acb728","document_hash":"35fdfc1ada37122d81b9e47785370e8ab6dbaaad49b3ec16270874c73495a200","target":"x_required->x_permitted","certificate":{"checker_version":"ve-tableau-checker@2","environment_id":"6f481de1d35d7f6f57feda072e16b966811032050e61d5d9ff79fbce9573a67b","premise_meaning_ids":["d90d71302dab0516f2b61332f617bdb32c4247049fb95c00d18a92d31e3c5b6b"],"conclusion_meaning_id":"fdbebb1230082cea58286696ebec0da576fc51d986cc2778fdd939d7dd9e074d","trace":{"rule":"expand","at":1,"children":[{"rule":"expand","at":2,"children":[{"rule":"expand","at":3,"children":[{"rule":"expand","at":4,"children":[{"rule":"close"},{"rule":"expand","at":5,"children":[{"rule":"expand","at":6,"children":[{"rule":"close"}]}]}]}]}]}]}}}}"#

def parsed (text : String) : Json := (Json.parse text).toOption.getD .null

def fact : String := r#"["forall", "assistant", ["not", ["and", ["unary", "v", ["var", 0]], ["unary", "w", ["var", 0]]]]]"#

/-- A base model with one assistant `a`. -/
def situation (v w : Bool) : String :=
  "{\"complete\": true, \"domains\": {\"assistant\": [\"a\"], \"user\": []}, \"constants\": {}, \"relations\": {\"v\": " ++
    (if v then "[[\"a\"]]" else "[]") ++ ", \"w\": " ++ (if w then "[[\"a\"]]" else "[]") ++ "}}"

/-- A case of `kind` with `facts` (a JSON text, or none for no key) and further fields. -/
def slotCase (kind : String) (facts : Option String) (extra : List (String × Json)) : Json :=
  Json.mkObj ([("id", .str "c"), ("kind", .str kind), ("environment", parsed environmentText),
    ("norms", parsed normsText)] ++ (facts.map fun f => ("facts", parsed f)).toList ++ extra)

def packagesField : String × Json := ("packages", parsed packagesText)
def factsModel (v w : Bool) : String × Json := ("facts_model", parsed (situation v w))
def witnessField : String × Json :=
  ("witness", Json.mkObj [("target", .str "x_required"), ("model", parsed (situation true true)),
    ("tuple", toJson ["a"])])
def certificateFields : List (String × Json) :=
  [("premises", Json.arr #[]), ("conclusion", parsed r#"["top"]"#), ("certificate", Json.mkObj [])]

/-- The verdict, or the refusal. -/
def verdictOf (j : Json) : String :=
  match runCase j with
  | .ok a => match a.getObjValD "verdict" with
    | .str v => v ++ s!" facts={a.getObjValD "facts"}"
    | _ => a.compress
  | .error e => "error: " ++ e

/-! ## Fixture (a) -/

-- No facts: the target `x_required` has no certificate over the soft background alone.
#guard verdictOf (slotCase "slot-conflict" (some "[]") [packagesField]) == "UNKNOWN facts=0"
-- With the fact and a model of it, every target's certificate replays: CONFLICT-FREE.
#guard verdictOf (slotCase "slot-conflict" (some ("[" ++ fact ++ "]")) [packagesField, factsModel true false]) ==
  "CONFLICT-FREE facts=1"
-- The same packages without the fact bind to nothing.
#guard verdictOf (slotCase "slot-conflict" (some "[]") [packagesField]) == "UNKNOWN facts=0"
-- A witness in the situation the fact excludes: CONFLICT without facts, refused with the fact.
#guard verdictOf (slotCase "slot-conflict" (some "[]") [witnessField]) == "CONFLICT facts=0"
#guard verdictOf (slotCase "slot-conflict" (some ("[" ++ fact ++ "]")) [witnessField]) ==
  "error: InvalidModel(facts): the model violates a fact"

/-! ## slot-certificate -/

/-- A certificate of `claim` from `background′ ++ [fact] ++ layer premises`, and one of `top` with no facts,
each bound as `replaySlotEntailment` binds it (Python's prover, the test's `slot_certificate`). -/
def claim : String := r#"["forall", "assistant", ["implies", ["unary", "v", ["var", 0]], ["not", ["unary", "w", ["var", 0]]]]]"#
def factCertificateText : String := r#"{"checker_version":"ve-tableau-checker@2","environment_id":"3eb973d9d7889fa10550e4a1fdf13ac3230ecfc7c6c58f90ddbc74ed72acb728","premise_meaning_ids":["38ba47e33900bc08cb00bb3218c2c6867ffdff842e6d9d0261dee564f1f16cbc","80d405ebfe1bcc5cd5511e9d67353ed08a77dc6da1592c5e3ba5b396d24988e3","6d9310a7bf46d7a205a785596452bfc6c7c56829416e3052e5b17db5690e77a3","a4d5fadcfaf39a790711f232d1dea2eeb25516e29b16d06bee7d9b71870894fb"],"conclusion_meaning_id":"afa05fd90352f3f0ada1b819b24e948e7297a51445c7f876a5e35ee70a3d33c2","trace":{"rule":"expand","at":4,"children":[{"rule":"expand","at":1,"children":[{"rule":"expand","at":6,"children":[{"rule":"expand","at":5,"children":[{"rule":"expand","at":7,"children":[{"rule":"close"},{"rule":"expand","at":9,"children":[{"rule":"close"}]}]}]}]}],"parameter":"w:0"}]}}"#
def topCertificateText : String := r#"{"checker_version":"ve-tableau-checker@2","environment_id":"3eb973d9d7889fa10550e4a1fdf13ac3230ecfc7c6c58f90ddbc74ed72acb728","premise_meaning_ids":["38ba47e33900bc08cb00bb3218c2c6867ffdff842e6d9d0261dee564f1f16cbc","6d9310a7bf46d7a205a785596452bfc6c7c56829416e3052e5b17db5690e77a3","a4d5fadcfaf39a790711f232d1dea2eeb25516e29b16d06bee7d9b71870894fb"],"conclusion_meaning_id":"0d5c1d1252b393e57a2408efa3d2188975980180136726032b7d839e0494ee96","trace":{"rule":"close"}}"#

def certificateCase (kind : String) (facts : Option String) (conclusion certificate : String)
    (extra : List (String × Json) := []) : Json :=
  slotCase kind facts ([("premises", Json.arr #[]), ("conclusion", parsed conclusion),
    ("certificate", parsed certificate)] ++ extra)

def validOf (j : Json) : String :=
  match runCase j with
  | .ok a => s!"valid={a.getObjValD "valid"} facts={a.getObjValD "facts"}"
  | .error e => "error: " ++ e

-- With its fact, the claim's certificate replays; with the facts reordered or dropped it is bound to nothing.
#guard validOf (certificateCase "slot-certificate" (some ("[" ++ fact ++ "]")) claim factCertificateText
  [factsModel true false]) == "valid=true facts=1"
#guard validOf (certificateCase "slot-certificate" (some "[]") claim factCertificateText) ==
  "error: certificate is stale or bound to different inputs"
-- No facts: slot-certificate answers soft-certificate's answer and `facts: 0` (`slot_wire_empty`).
#guard match runCase (certificateCase "soft-certificate" none r#"["top"]"# topCertificateText),
    runCase (certificateCase "slot-certificate" (some "[]") r#"["top"]"# topCertificateText) with
  | .ok soft, .ok slot => slot == soft.setObjVal! "facts" (toJson (0 : Nat)) && soft.getObjValD "valid" == .bool true
  | _, _ => false

/-! ## The acceptance addendum's Lean-side cases -/

/-- The refusal of `facts` on each slot form (certificate, conflict over packages, witness). -/
def refusals (facts : String) : List String :=
  [verdictOf (slotCase "slot-certificate" (some facts) (certificateFields ++ [factsModel true false])),
   verdictOf (slotCase "slot-conflict" (some facts) [packagesField, factsModel true false]),
   verdictOf (slotCase "slot-conflict" (some facts) [witnessField])]

-- T1: a fact naming a rule's regulated predicate, or its permission, is refused by the decoder.
#guard refusals r#"[["forall", "assistant", ["unary", "x_required", ["var", 0]]]]"# ==
  List.replicate 3 "error: ill-typed or unbound formula"
#guard refusals r#"[["forall", "assistant", ["unary", "x_permitted", ["var", 0]]]]"# ==
  List.replicate 3 "error: ill-typed or unbound formula"
-- T3: every item decodes or the case is refused; `facts` must be an array, and is required.
#guard refusals ("[" ++ fact ++ ", 7]") == List.replicate 3 "error: array expected"
#guard refusals ("[" ++ fact ++ ", \"\"]") == List.replicate 3 "error: array expected"
#guard refusals r#"[["forall", "assistant", ["unary", "undeclared", ["var", 0]]]]"# ==
  List.replicate 3 "error: ill-typed or unbound formula"
#guard refusals "7" == List.replicate 3 "error: InvalidInput: facts must be an array"
#guard verdictOf (slotCase "slot-conflict" none [packagesField]) ==
  "error: InvalidInput: a slot case needs a facts array"
-- T4: a made-up constant, and a declared predicate at the wrong arity.
#guard refusals r#"[["unary", "v", ["const", "nobody"]]]"# == List.replicate 3 "error: ill-typed or unbound formula"
#guard refusals r#"[["forall", "assistant", ["binary", "v", ["var", 0], ["var", 0]]]]"# ==
  List.replicate 3 "error: ill-typed or unbound formula"
-- T5: facts that contradict each other have no model; without one they are refused before any replay.
def contradiction : String :=
  r#"[["forall", "assistant", ["unary", "v", ["var", 0]]], ["forall", "assistant", ["not", ["unary", "v", ["var", 0]]]]]"#
#guard verdictOf (slotCase "slot-conflict" (some contradiction) [packagesField, factsModel true false]) ==
  "error: InvalidModel(facts): the model violates a fact"
#guard verdictOf (slotCase "slot-conflict" (some contradiction) [packagesField, factsModel false false]) ==
  "error: InvalidModel(facts): the model violates a fact"
#guard verdictOf (slotCase "slot-conflict" (some contradiction) [packagesField]) ==
  "error: InvalidInput: facts need a facts_model: a base model of the background and the facts"
#guard verdictOf (slotCase "slot-certificate" (some contradiction) (certificateFields ++ [factsModel true false])) ==
  "error: InvalidModel(facts): the model violates a fact"

end VE.SoftNorms.SlotExamples
