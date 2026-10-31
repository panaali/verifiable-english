import ResponseShape
import VE.Senses.Run

/-! The source of `ve/backends/lean_service_schema/senses.project.json` (`file`; `tools/response_schemas.py` writes
it): the `senses.project` mode's row (`VE.Senses.Run.projectCaseReported`, docs/spec/senses-PLAN.md 2.6, B6). The
projected environment is the request's with the dictionary's sorts and predicates added: the relay reads it as an
environment and binds its identity, and the lexicon's, to the JSON returned (`ve.backends.senses`). -/
namespace ResponseShape.Schemas.SensesProject
open Lean ResponseShape

def pair : Shape := n [arr, .prefixItems [str, str], .minItems 2, .maxItems 2]

def lexicon : Shape :=
  c "VE.Senses.Run.lexiconJson: the projected lexicon as english.read receives one, naming the projected environment." [
    obj, .required ["format", "environment_id", "nouns", "letters", "wordings", "negatives", "aliases", "spellings"],
    closed [("format", constS VE.EnglishGrammar.Run.lexiconFormat), ("environment_id", ref "common.json#/$defs/hex64"),
      ("nouns", n [arr, .items (ref "#/$defs/pair")]), ("letters", n [arr, .items (ref "#/$defs/pair")]),
      ("wordings", n [arr, .items (ref "#/$defs/pair")]), ("negatives", n [arr, .items (ref "#/$defs/pair")]),
      ("aliases", n [arr, .items (n [arr, .prefixItems [str, str, .type ["boolean"]], .minItems 3, .maxItems 3])]),
      ("spellings", n [arr, .items (ref "#/$defs/pair")])]]

def identities : Shape :=
  c "VE.Senses.Run.projectionIds with S2's actions version: the projection's environment, lexicon and grammar." [
    obj, .required ["environment_id", "lexicon_id", "grammar_id", "actions_version"],
    closed [("environment_id", ref "common.json#/$defs/hex64"), ("lexicon_id", ref "common.json#/$defs/hex64"),
      ("grammar_id", ref "common.json#/$defs/hex64"), ("actions_version", ref "common.json#/$defs/text")]]

/-- A fault with `code`'s status and arguments (`VE.Senses.Run.faultJson`, `faultFields`). -/
def fault (status code : String) (args : List (String × Shape)) : Shape :=
  n [obj, .required ["status", "code", "details"],
    closed [("status", constS status), ("code", constS code),
      ("details", n [obj, .required (args.map (·.1)), closed args])]]

def projection : Shape :=
  let nat := ref "common.json#/$defs/nat"
  let words := ref "common.json#/$defs/strings"
  .anyOf [
    c "The projection: its environment, its lexicon and their identities." [
      obj, .required ["status", "environment", "lexicon", "identities"],
      closed [("status", constS "ok"),
        ("environment", copied "the request's environment with the projection's sorts and predicates (VE.Senses.projectedJson)" obj),
        ("lexicon", ref "#/$defs/lexicon"), ("identities", ref "#/$defs/identities")]],
    c "VE.Senses.Run.faultJson of a dictionary failure: its check, name and reason." [
      obj, .required ["status", "code", "failure"],
      closed [("status", constS "rejected"), ("code", constS "InvalidDictionary"),
        ("failure", n [arr, .prefixItems [str, str, str], .minItems 3, .maxItems 3])]],
    fault "rejected" "UnknownWord" [("line", nat), ("word", str)],
    fault "rejected" "UnknownGloss" [("line", nat), ("word", str), ("gloss", str)],
    fault "rejected" "MalformedPreamble" [("line", nat)],
    fault "budget" "PreambleBudget" [("line", nat)],
    fault "rejected" "RepeatedDefault" [("line", nat), ("word", str)],
    fault "rejected" "PreambleLate" [("sentence", nat)],
    fault "rejected" "Collision" [("kind", str), ("name", str), ("sense", str)],
    fault "rejected" "VocabularyLimit" [("what", str)],
    fault "rejected" "TooManyCandidates" [("sentence", nat), ("words", words)],
    fault "rejected" "CandidatesDiverge" [("sentence", nat), ("words", words),
      ("why", .anyOf [constS "binder", n [obj, .required ["referent"], closed [("referent", str)]]])],
    fault "rejected" "QuotedSense" [("sentence", nat), ("word", str)]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    n [obj, .required ["id", "status", "error"],
      closed [("id", .echo "/id"), ("status", constS "error"), ("error", ref "common.json#/$defs/text")]],
    n [obj, .required ["id", "status", "result"],
      closed [("id", n [str, .equals "/id"]), ("status", constS "ok"),
        ("result", n [obj, .required ["dictionary_id", "senses_version", "projection"],
          closed [("dictionary_id", ref "common.json#/$defs/hex64"), ("senses_version", ref "common.json#/$defs/text"),
            ("projection", ref "#/$defs/projection")]])]]]

def file : File where
  name := "senses.project.json"
  comment := some "Mode senses.project: VE.Senses.Run.projectCaseReported. A projection with its identities, or its fault."
  top := [("row", «row»)]
  defs := [("pair", .schema pair), ("lexicon", .schema lexicon), ("identities", .schema identities),
    ("projection", .schema projection)]

end ResponseShape.Schemas.SensesProject
