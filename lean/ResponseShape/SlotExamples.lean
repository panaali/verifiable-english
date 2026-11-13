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
-- the slot answers are not the soft kinds' rows, nor the other way round
#guard !accepts (unknown.setObjVal! "kind" (.str "soft-conflict")) (run unknown)
#guard !accepts (certificate.setObjVal! "kind" (.str "slot-conflict")) (run certificate)

end ResponseShape.SlotExamples
