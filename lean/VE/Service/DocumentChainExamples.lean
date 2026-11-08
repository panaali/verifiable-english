import VE.Service.DocumentChain

/-! PC-2a's fixtures (docs/spec/profile-composition.md 5.2): constitution sentences as soft rules under `norm-defaults@0`,
each read through `Document.check` and `DocumentChain.layeredOf`, the same documents as
`tests/data/composition/pc2a/chain.json`. -/

namespace VE.Service.DocumentChain.Examples
open Lean
open VE.Service.Document

def arg (description : String) : Json :=
  Json.mkObj [("arguments", Json.arr #[.str "claude_instance"]), ("description", .str description)]

def regulated (description act default role : String) (permission : List String := []) : Json :=
  (arg description).setObjVal! "regulated" (Json.mkObj ([("act", .str act), ("default", .str default), ("role", .str role)] ++
    permission.map (("permission", .str ·))))

def environmentOver (profiles : List String) (predicates : List (String × Json)) : Json :=
  Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson profiles),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"),
    ("vocabulary", Json.mkObj [("constants", Json.mkObj []), ("predicates", Json.mkObj predicates),
      ("sorts", Json.mkObj [("claude_instance", Json.mkObj [("description", .str "Claude")])])])]

def chain : List String := ["documents@1", "norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"]

/-- F2.1's vocabulary: constitution u0073.s05 on `unspecified`. -/
def complyPredicates : List (String × Json) :=
  [("comply_required", regulated "complies" "{0} comply with the system prompt's instructions" "unspecified" "obligation"
      ["comply_permitted"]),
   ("comply_permitted", regulated "may comply" "{0} comply with the system prompt's instructions" "allow" "permission"),
   ("unsafe_to_comply", arg "not safe"), ("unethical_to_comply", arg "unethical"), ("against_guidelines", arg "against")]

def ofVar (p : String) : Json :=
  Json.arr #[.str "unary", .str p, Json.arr #[.str "var", toJson (0 : Nat)]]

/-- F2.1's rule: a soft default rule with three exceptions. -/
def complyRule : Json := Json.mkObj [("norm", Json.mkObj [("name", .str "comply"), ("predicate", .str "comply_required"),
  ("sign", .bool true), ("mode", .str "default"), ("guard", Json.arr #[.str "top"]), ("unless", Json.arr #[]),
  ("over", Json.arr #[]), ("exception", Json.mkObj [("decided_by", .str "unstated"), ("necessary", Json.arr #[]),
    ("factors", Json.arr #[]), ("sufficient", Json.arr #[ofVar "unsafe_to_comply", ofVar "unethical_to_comply",
      ofVar "against_guidelines"])])])]

/-- F2.2's vocabulary and rule: constitution u0125.s04.p2, strict. -/
def denyPredicates : List (String × Json) :=
  [("deny_being_claude_permitted", regulated "may deny" "{0} directly deny being Claude" "unspecified" "permission")]

def denyRule : Json := Json.mkObj [("norm", Json.mkObj [("name", .str "never-deny"),
  ("predicate", .str "deny_being_claude_permitted"), ("sign", .bool false), ("guard", Json.arr #[.str "top"]),
  ("unless", Json.arr #[]), ("over", Json.arr #[])])]

/-- A one-unit document, of one byte per source character. -/
def document (environment rule : Json) (members : List (String × Json) := []) : Json :=
  Json.mkObj ([("format", .str "ve-document@1"), ("environment", environment),
    ("units", Json.arr #[Json.mkObj [("id", .str "u1"), ("span", toJson [0, 1]), ("kind", .str "norm"),
      ("meaning", .str "specified"), ("support", .str "assumption"), ("content", rule)]])] ++ members)

def textOf (front : Json) : String := "---\n" ++ front.compress ++ "\n---\nx"

def complyDocument (members : List (String × Json) := []) : Json :=
  document (environmentOver chain complyPredicates) complyRule members

/-- `layeredOf` on what `check` read of a document. -/
def layered (front : Json) : Except String VE.NormDefaults.Wire.LayeredU := do
  let c ← check (textOf front)
  let E ← environmentOf (c.front.getObjValD "environment") (c.front.getObjValD "units")
  layeredOf E c.front c.units

def checkError (front : Json) : Option String :=
  match check (textOf front) with
  | .ok _ => none
  | .error e => some e

def holds {α} (x : Except String α) (p : α → Bool) : Bool :=
  match x with
  | .ok a => p a
  | .error _ => false

/-- A situation of one Claude instance, with its exceptions and its soft decision. -/
def situation (danger excepted : Bool) : Json :=
  let row (b : Bool) : Json := if b then Json.arr #[Json.arr #[.str "c"]] else Json.arr #[]
  Json.mkObj [("complete", .bool true), ("domains", Json.mkObj [("claude_instance", Json.arr #[.str "c"])]),
    ("constants", Json.mkObj []), ("relations", Json.mkObj [("unsafe_to_comply", row danger),
      ("unethical_to_comply", row false), ("against_guidelines", row false), ("soft__excepted__comply", row excepted)])]

def filling (yes : Bool) : Json :=
  Json.mkObj [("unsaid__comply_required", if yes then Json.arr #[Json.arr #[.str "c"]] else Json.arr #[])]

/-- The point status of `comply_required` at the situation, by the `norm-defaults` mode's own replay. -/
def statusAt (m : Json) (method : String) : Except String String := do
  let L ← layered (complyDocument)
  let d ← VE.NormDefaults.Wire.replayStatusX L (Json.mkObj [("model", m), ("predicate", .str "comply_required"),
    ("tuple", Json.arr #[.str "c"]), ("method", .str method), ("yes", filling true), ("no", filling false)])
  pure d.status.label

/-! ## F2.1 -/

-- `layeredOf_ids`: the soft pack, its three exception premises.
#guard holds (layered complyDocument) fun L => L.packs.map (·.id) == ["soft"] && L.X.length == 3
-- The case and no exception: SETTLED yes.
#guard holds (statusAt (situation false false) "enumerate") (· == "SETTLED yes")
-- An exception: UNDECIDED, by the two fillings.
#guard holds (statusAt (situation true true) "undecided") (· == "UNDECIDED")
-- The other direction: no exception holds, so the two fillings are no UNDECIDED witness.
#guard holds (statusAt (situation false false) "undecided") (· == "UNKNOWN")
-- The exception case reads the soft pack: an exception holding without its decision is no situation of the document.
#guard match (do
    let L ← layered complyDocument
    let _ ← VE.NormDefaults.Wire.filledX L (Json.mkObj [("model", situation true false), ("filling", filling true),
      ("tuple", Json.arr #[.str "c"])])
    pure ()) with
  | .error e => e == "InvalidModel(soft): the model violates a background premise"
  | .ok _ => false
-- Its decision given, the same situation is one.
#guard (do
    let L ← layered complyDocument
    let _ ← VE.NormDefaults.Wire.filledX L (Json.mkObj [("model", situation true true), ("filling", filling true),
      ("tuple", Json.arr #[.str "c"])])
    pure () : Except String Unit) matches .ok _

/-! ## F2.1b: `validateCompletions`' text, and the entries it accepts -/

def completions (predicate cite : String) : Json :=
  Json.mkObj [(predicate, Json.mkObj [("cites", Json.arr #[.str cite]), ("reason", .str "the rule")])]

#guard checkError (complyDocument [("completions", completions "comply_permitted" "absent")]) ==
  some "InvalidInput: completion grounding for comply_permitted cites an unknown unit"
#guard checkError (complyDocument [("completions", completions "comply_permitted" "u1")]) == none
#guard checkError complyDocument == none

/-! ## F2.2 and `requestOf`'s case -/

#guard holds (layered (document (environmentOver chain denyPredicates) denyRule))
  fun L => L.packs.map (·.id) == ["soft"] && L.X.isEmpty

/-- The case a document makes, on what `check` read. -/
def caseOf (front : Json) : Except String Json := do
  let c ← check (textOf front)
  let E ← environmentOf (c.front.getObjValD "environment") (c.front.getObjValD "units")
  pure (requestOf E c.front c.units)

-- The free norms, the environment `E.lower` and the `completions`.
#guard holds (caseOf (complyDocument [("completions", completions "comply_permitted" "u1")])) fun j =>
  j.getObjValD "norms" == Json.arr #[wireJson 257 complyRule] &&
  j.getObjValD "environment" == wireJson 257 (environmentOver chain complyPredicates) &&
  j.getObjValD "completions" == completions "comply_permitted" "u1"

/-- A case with the given unit kind and reading sets over `E`, built without `check`. -/
def plainCase (environment : Json) (kind : String) (members : List (String × Json)) : Except String Json := do
  let E ← environmentOf environment
  let unit : SourceUnit :=
    { id := "u1", span := (0, 1), kind := .str kind, decoded := RowKind.route VE.Route.Admission.Kind.norm,
      meaning := .str "specified", support := "assumption", status := "CHECKED", parent := none,
      content := some (UnitContent.soft complyRule) }
  pure (requestOf E (Json.mkObj members) [unit])

-- A norm under a reading set is no free norm, nor is another kind's; a free unit's is.
#guard holds (plainCase (environmentOver chain complyPredicates) "norm"
    [("reading_sets", Json.arr #[Json.mkObj [("unit", .str "u1")]])]) (·.getObjValD "norms" == Json.arr #[])
#guard holds (plainCase (environmentOver chain complyPredicates) "quoted" []) (·.getObjValD "norms" == Json.arr #[])
#guard holds (plainCase (environmentOver chain complyPredicates) "norm" []) (·.getObjValD "norms" != Json.arr #[])

-- An environment off the soft route makes no case: the mode's decoder refuses it.
#guard holds (plainCase (environmentOver ["documents@1", "norms@0", "relational-fol@0"] []) "norm" []) (· == .null)

/-! ## What the mode still refuses -/

def refusal (profiles : List String) : Option String :=
  match environmentOf (environmentOver profiles complyPredicates) with
  | .ok _ => none
  | .error e => some e

#guard refusal (chain ++ ["readings@1"]) ==
  some "CheckerUnavailable: soft-norms with readings, alternatives or risk needs its composed Lean route"
end VE.Service.DocumentChain.Examples
