import ResponseShape.DefaultsExamples
import VE.SoftNorms.SlotExamples

/-! The slot rows of `soft-norms.json` (`Schemas.SoftNorms.slot_certificate`, `slot_packages`, `slot_witness`) and
the soft rows whose field lists they share, on the mode's own answers to the kind's fixtures
(`VE/SoftNorms/SlotExamples.lean`, kb-3): every answer and refusal is accepted, and an answer with a member added,
dropped or retyped, or a `facts` that is not the number of facts the request sent, is refused. -/
namespace ResponseShape.SlotExamples
open Lean VE.SoftNorms.SlotExamples
open ResponseShape.DefaultsExamples (variants)

def accepts (j a : Json) : Bool :=
  (ResponseShape.decide Schemas.files (.ref "soft-norms.json#/row") { value := j } a).toOption.isSome
def run (j : Json) : Json := VE.SoftNorms.Run.runCaseReported j

def oneFact : String := "[" ++ fact ++ "]"
def certificate : Json := certificateCase "slot-certificate" (some oneFact) claim factCertificateText [factsModel true false]
def conflictFree : Json := slotCase "slot-conflict" (some oneFact) [packagesField, factsModel true false]
def unknown : Json := slotCase "slot-conflict" (some "[]") [packagesField]
def witness : Json := slotCase "slot-conflict" (some "[]") [witnessField]
def soft : List Json := [certificateCase "soft-certificate" none r#"["top"]"# topCertificateText,
  slotCase "soft-conflict" none [packagesField], slotCase "soft-conflict" none [witnessField]]
def refused : List Json := [slotCase "slot-conflict" (some oneFact) [witnessField],
  slotCase "slot-conflict" none [packagesField], slotCase "slot-conflict" (some "7") [packagesField],
  certificateCase "slot-certificate" (some "[]") claim factCertificateText]

-- accepted: each slot answer, the soft answers sharing their field lists, and each refusal (the mode's error row)
#guard [certificate, conflictFree, unknown, witness].all fun j => (run j).getObjValD "status" == .str "ok" && accepts j (run j)
#guard soft.all fun j => (run j).getObjValD "status" == .str "ok" && accepts j (run j)
#guard refused.all fun j => (run j).getObjValD "status" == .str "error" && accepts j (run j)
-- refused: every variant of each slot answer (a member added or dropped, an object, array or leaf retyped)
#guard [certificate, conflictFree, unknown, witness].all fun j => (variants [] 6 (run j)).all (!accepts j ·)
-- refused: `facts` not the number of facts sent (shifted, retyped, dropped), and a soft answer with `facts`
#guard [certificate, conflictFree, unknown, witness].all fun j =>
  let a := run j
  let n := (a.getObjValD "facts").getNat?.toOption.getD 0
  [a.setObjVal! "facts" (toJson (n + 1)), a.setObjVal! "facts" (.str (toString n)), a.setObjVal! "facts" (.bool true),
    a.setObjVal! "facts" (toJson [n])].all (!accepts j ·) &&
  (match a with | .obj kvs => !accepts j (.obj (kvs.erase "facts")) | _ => false)
#guard soft.all fun j => !accepts j ((run j).setObjVal! "facts" (toJson (0 : Nat)))
-- the soft answers whose field lists the slot rows share: every variant refused
#guard soft.all fun j => (variants [] 6 (run j)).all (!accepts j ·)

/-- A witness of `target` in `situation v w`. -/
def witnessAt (target : String) (v w : Bool) : String × Json :=
  ("witness", Json.mkObj [("target", .str target), ("model", parsed (situation v w)), ("tuple", toJson ["a"])])
/-- Fixture (a) with `k` forbidding the permission instead: a pair conflict where both rules fire. -/
def pairNorms : Json := parsed
  r#"[{"norm": {"name": "h", "predicate": "x_required", "sign": true, "guard": ["unary", "v", ["var", 0]], "unless": [], "over": []}}, {"norm": {"name": "k", "predicate": "x_permitted", "sign": false, "guard": ["unary", "w", ["var", 0]], "unless": [], "over": []}}]"#
/-- Witness cases, slot and soft: an UNKNOWN one (no conflict where only `h` fires), a strict collision and a
pair conflict. -/
def witnesses : List Json := [true, false].flatMap fun slot =>
  let mk (extra : String × Json) : Json :=
    if slot then slotCase "slot-conflict" (some "[]") [extra] else slotCase "soft-conflict" none [extra]
  [mk (witnessAt "x_required" true false), mk (witnessAt "x_required" true true),
   (mk (witnessAt "x_required->x_permitted" true true)).setObjVal! "norms" pairNorms]
#guard (witnesses.map fun j => (run j).getObjValD "verdict") ==
  [.str "UNKNOWN", .str "CONFLICT", .str "CONFLICT", .str "UNKNOWN", .str "CONFLICT", .str "CONFLICT"]
#guard (witnesses.map fun j => (run j).getObjValD "witness_kind") == (List.replicate 2
  [.null, .str "strict collision on x_required", .str "pair conflict on x_required->x_permitted"]).flatten
-- each is accepted, its variants refused, and so is another target, a kind of no prefix, or a kind beside UNKNOWN
#guard witnesses.all fun j => accepts j (run j) && (variants [] 6 (run j)).all (!accepts j ·) &&
  !accepts j ((run j).setObjVal! "target" (.str "x_permitted")) &&
  !accepts j ((run j).setObjVal! "witness_kind" (.str "collision on x_required")) &&
  ((run j).getObjValD "verdict" == .str "CONFLICT" ||
    !accepts j ((run j).setObjVal! "witness_kind" (.str "strict collision on x_required")))
-- an ok witness row is no row of another soft kind (the witness entries name their kinds)
#guard witnesses.all fun j => !accepts (j.setObjVal! "kind" (.str "soft-bogus")) (run j)
-- the rows beside the slot kinds: the batch decoder's own refusal at its index, a soft-selected answer, and a
-- case off the soft path (the norms mode's row)
#guard [witness, certificate, unknown].all fun j => (ResponseShape.decide Schemas.files (.ref "soft-norms.json#/row")
  { value := j, index := some 0 } (Json.mkObj [("status", .str "error"), ("case_index", toJson (0 : Nat)),
    ("error", .str "InvalidInput")])).toOption.isSome
#guard let j := slotCase "soft-selected" none [("model", parsed (situation true false)),
    ("queries", parsed r#"[{"predicate": "x_required", "tuple": ["a"]}]"#)]
  (run j).getObjValD "status" == .str "ok" && accepts j (run j)
#guard let j := Json.mkObj [("id", .str "c"), ("kind", .str "defaults-elaborate")]
  (run j).getObjValD "status" == .str "error" && accepts j (run j)

-- the slot answers are not the soft kinds' rows, nor the other way round
#guard !accepts (unknown.setObjVal! "kind" (.str "soft-conflict")) (run unknown)
#guard !accepts (certificate.setObjVal! "kind" (.str "slot-conflict")) (run certificate)

end ResponseShape.SlotExamples
