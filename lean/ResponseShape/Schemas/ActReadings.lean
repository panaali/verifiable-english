import ResponseShape
import VE.Acts.Run

/-! The `act-readings` row (act-phrases 7, AP-4): a phrase's readings under a rule's modal words, each as its simple
acts and its paraphrase, with Lean's lexing of the phrase (`tokens`, UTF-8 byte spans) and each act's token indices
(`from`). The relay (`ve/acts.py`) binds the spans to the phrase, the indices to `tokens`, and the readings' distinctness;
it cannot see a reading dropped with its row (spec 7, "What binding cannot show"). -/
namespace ResponseShape.Schemas.ActReadings
open Lean ResponseShape

def nat : Shape := ref "common.json#/$defs/nat"

def «act» : Shape :=
  n [obj, .required ["act", "text", "from"],
    closed [("act", str), ("text", str), ("from", n [arr, .items nat])]]

def reading : Shape :=
  n [obj, .required ["acts", "paraphrase"],
    closed [("acts", n [arr, .items (ref "#/$defs/act")]), ("paraphrase", str)]]

def result : Shape :=
  c "VE.Acts.Run.runActReadings (runActReadings_fits): LISTED with the phrase's tokens and readings; LIMIT or REFUSED with Lean's diagnostic and both lists empty." [
    obj, .required ["id", "status", "verdict", "tokens", "readings"],
    .ite (props [("verdict", constS "LISTED")]) (.not (.required ["diagnostic"])) (.required ["diagnostic"]),
    closed [
      ("id", n [str, .equals "/id"]),
      ("status", constS "ok"),
      ("verdict", enumS ["LISTED", "LIMIT", "REFUSED"]),
      ("tokens", n [arr, .items (n [arr, .prefixItems [nat, nat], .minItems 2, .maxItems 2])]),
      ("readings", n [arr, .items (ref "#/$defs/reading"), .maxItems VE.Acts.maxReadings]),
      ("diagnostic", str)]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    n [obj, .required ["id", "status", "error"],
      closed [("id", .echo "/id"), ("status", constS "error"), ("error", ref "common.json#/$defs/text")]],
    ref "#/$defs/result"]

def file : File where
  name := "act-readings.json"
  comment := some "Lean's readings of one act phrase under a modal, with its token spans and each act's token indices."
  top := [("row", «row»)]
  defs := [("act", .schema «act»), ("reading", .schema reading), ("result", .schema result)]

end ResponseShape.Schemas.ActReadings
