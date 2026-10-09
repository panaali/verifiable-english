import ResponseShape

/-! The source of `ve/backends/lean_service_schema/readings-route.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.ReadingsRoute
open Lean ResponseShape

def kind : Def :=
  .group none [
    ("readings-validate", kindIs "readings-validate"),
    ("readings-separate", kindIs "readings-separate"),
    ("readings-elaborate", kindIs "readings-elaborate"),
    ("readings-conflict", kindIs "readings-conflict"),
    ("readings-certificate", kindIs "readings-certificate"),
    ("readings-model", kindIs "readings-model"),
    ("readings-dead", kindIs "readings-dead"),
    ("readings-choice", kindIs "readings-choice"),
    ("readings-verdicts", kindIs "readings-verdicts")]

def pair : Shape :=
  c
    "Readings.Run.pairJson: a separating situation's facts; other_value exactly when the other reading owns no generated key."
    [
      obj,
      .required ["situation", "witness", "separated", "witness_admissible", "witness_value", "other_admissible"],
      closed [
        ("situation", str),
        ("witness", str),
        ("separated", .type ["boolean"]),
        ("witness_admissible", .type ["boolean"]),
        ("witness_value", .type ["boolean", "null"]),
        ("other_admissible", .type ["boolean"]),
        ("other_value", .type ["boolean", "null"])]]

def key : Shape :=
  c "Readings.Wire key JSON: one generated key." [
    .anyOf [
      n [obj, .required ["excepted"], closed [("excepted", str), ("bearer", str)]],
      n [obj, .required ["off", "party"], closed [("off", str), ("party", str), ("bearer", str)]],
      n [
        obj,
        .required ["outweighs", "lower", "higher"],
        closed [("outweighs", str), ("lower", str), ("higher", str)]],
      n [obj, .required ["lim", "act"], closed [("lim", str), ("act", str)]],
      n [obj, .required ["cond", "act", "condition"], closed [("cond", str), ("act", str), ("condition", str)]],
      n [obj, .required ["aimed"], closed [("aimed", str)]]]]

def keys : Shape :=
  n [arr, .items (n [obj, .required ["key", "name"], closed [("key", ref "#/$defs/key"), ("name", str)]])]

def candidate : Shape :=
  c
    "Readings.Run.candidateJson: a pending candidate, or its document hash, owned and shared keys and findings."
    [
      .anyOf [
        n [
          obj,
          .required ["id", "index", "pending"],
          closed [("id", str), ("index", ref "common.json#/$defs/nat"), ("pending", .const (.bool true))]],
        n [
          obj,
          .required ["id", "index", "pending", "document_hash", "owned", "shared", "findings"],
          closed [
            ("id", str),
            ("index", ref "common.json#/$defs/nat"),
            ("pending", .const (.bool false)),
            ("document_hash", ref "common.json#/$defs/hex64"),
            ("owned", ref "#/$defs/keys"),
            ("shared", ref "#/$defs/keys"),
            ("findings", ref "common.json#/$defs/nonempty_strings")]]]]

def validate : Shape :=
  c "Readings.Run.validateResult: no content-bearing set, or one entry per content-bearing open set; under the unspecified completion (Readings.Run.runValidateND) also fill_premises and filled." [
    .anyOf [
      n [
        obj,
        .required ["id", "status", "content_bearing"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("content_bearing", .const (.bool false)),
          ("fill_premises", ref "#/$defs/fill_premises"),
          ("filled", ref "#/$defs/filled")]],
      n [
        obj,
        .required ["id", "status", "content_bearing", "sets"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("content_bearing", .const (.bool true)),
          ("sets", n [
            arr,
            .items (n [
                obj,
                .required ["set", "version", "candidates", "pairs", "findings"],
                closed [
                  ("set", str),
                  ("version", ref "common.json#/$defs/nat"),
                  ("candidates", n [arr, .items (ref "#/$defs/candidate")]),
                  ("pairs", n [
                    arr,
                    .items (n [
                        obj,
                        .required ["reading", "other", "pair"],
                        closed [("reading", str), ("other", str), ("pair", ref "#/$defs/pair")]])]),
                  ("findings", n [
                    arr,
                    .items (n [
                        str,
                        .pattern (Re.prefixes ["SeparatedByDecisionOnly: ", "SeparatedByActOnly: "])])])]])]),
          ("fill_premises", ref "#/$defs/fill_premises"),
          ("filled", ref "#/$defs/filled")]]]]

def fill_premises : Shape :=
  c "Readings.Run.runValidateND (UnspecifiedWire.fillPremisesJson): under the unspecified completion, per reading with content its Fill_T, each premise labelled unsaid:pair:<r>,<m>." [
    arr,
    .items (n [
      obj,
      .required ["set", "index", "premises"],
      closed [
        ("set", str),
        ("index", ref "common.json#/$defs/nat"),
        ("premises", n [
          arr,
          .items (n [
            obj,
            .required ["label", "ast"],
            closed [("label", str), ("ast", ref "common.json#/$defs/generated_formula")]])])]])]

def filled : Shape :=
  c "Readings.Run.runValidateND (UnspecifiedWire.filledJson): under the unspecified completion, the filled frame's environment (unspecified read as deny, norm-defaults@0 removed, every unsaid__p added) and the filled units, the F_p units last." [
    obj,
    .required ["environment", "units"],
    closed [
      ("environment", c "the filled environment" []),
      ("units", arr)]]

def separate : Shape :=
  c "Readings.Run.runCase readings-separate: the requested set and situation's pair facts." [
    obj,
    .required ["id", "status", "set", "pair"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("set", n [str, .equals "/set"]),
      ("pair", n [ref "#/$defs/pair", props [("situation", .equals "/situation")]])]]

/-! The case kinds of S2a (`Readings.Run.runS2`, docs/spec/composition-s2.md 3). -/

def choice : Shape :=
  c "Readings.choiceJson: per open set the choice takes a reading of, the set and the reading's index." [
    arr,
    .items (n [arr, .minItems 2, .maxItems 2, .prefixItems [str, ref "common.json#/$defs/nat"]])]

def over (limit : String) : Shape := n [str, .pattern (.lit s!"over {limit}")]

/-- The fields of `readings-elaborate` past the first three rows of 1.1, and on the superposed route. -/
def elaborateChoices : List (String × Shape) := [
  ("finding", .anyOf [
    .type ["null"],
    n [obj, .required ["text", "cause"], closed [("text", ref "common.json#/$defs/text"), ("cause", str)]]]),
  ("narrowings_stale", ref "common.json#/$defs/strings"),
  ("choice_count", .anyOf [ref "common.json#/$defs/nat", over "64"]),
  ("choices", .anyOf [n [arr, .items (ref "#/$defs/choice")], constS "over"]),
  ("choices_checked", .anyOf [ref "common.json#/$defs/nat", n [str, .pattern (Re.prefixes ["over "])]])]

def generatedPredicates : Shape :=
  n [
    arr,
    .items (n [
      obj,
      .required ["name", "layer", "key"],
      closed [
        ("name", str),
        ("layer", enumS ["readings", "soft", "rights"]),
        ("key", .anyOf [.type ["null"], ref "#/$defs/key"])]])]

def elaborateSuperposed : List (String × Shape) := [
  ("vocabulary", n [
    obj,
    .required ["sorts", "constants", "predicates"],
    closed [
      ("sorts", ref "common.json#/$defs/strings"),
      ("constants", n [obj, .object [] (some str)]),
      ("predicates", n [
        arr,
        .items (n [
            obj,
            .required ["name", "arguments"],
            closed [("name", str), ("arguments", ref "common.json#/$defs/strings")]])])]]),
  ("units", arr),
  ("slot", n [
    arr,
    .items (n [
        obj,
        .required ["label", "ast"],
        closed [("label", str), ("ast", ref "common.json#/$defs/generated_formula")]])]),
  ("names", arr),
  ("sizes", n [
    obj,
    .required ["sorts", "predicates", "nodes", "limits"],
    closed [
      ("sorts", ref "common.json#/$defs/nat"),
      ("predicates", ref "common.json#/$defs/nat"),
      ("nodes", ref "common.json#/$defs/nat"),
      ("limits", n [
        obj,
        .required ["sorts", "predicates", "nodes"],
        closed [
          ("sorts", ref "common.json#/$defs/nat"),
          ("predicates", ref "common.json#/$defs/nat"),
          ("nodes", ref "common.json#/$defs/nat")]])]])]

/-- `fill_premises` and `filled` (Readings.Run.runElaborateNDFilled), as validate answers them. -/
def filledFields : List (String × Shape) :=
  [("fill_premises", ref "#/$defs/fill_premises"), ("filled", ref "#/$defs/filled")]

/-- An answer of exactly `fields` beside `id`, `status` and the route. -/
def elaborateRoute (routes : List String) (fields : List (String × Shape)) : Shape :=
  n [
    obj,
    .required (["id", "status", "route"] ++ fields.map (·.1)),
    closed ([
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("route", enumS routes)] ++ fields)]

def elaborate : Shape :=
  c
    "Readings.Run.runElaborate (Route.elaborateFields): the route of 1.1; past its first three rows the finding of 1.8, the stale narrowings, the compatible choices (or over the limit) and the number checked; on the superposed route also the choice vocabulary, the units of sup D, the labelled slot, the name map and the sizes. The units and the name map are compared whole with Python's regeneration (ve/readings_route.py elaborate). Under the unspecified completion (Readings.Run.runElaborateNDFilled) the row also carries fill_premises and filled."
    [
      .anyOf [
        elaborateRoute ["w2", "pending", "abstention"] [("generated_predicates", generatedPredicates)],
        elaborateRoute ["enumerated"] (("generated_predicates", generatedPredicates) :: elaborateChoices),
        elaborateRoute ["superposed"] (("generated_predicates", generatedPredicates) ::
          (elaborateChoices ++ elaborateSuperposed)),
        -- Under the unspecified completion (Readings.Run.runElaborateNDFilled): each row with the filled document.
        elaborateRoute ["w2", "pending", "abstention"] (("generated_predicates", generatedPredicates) :: filledFields),
        elaborateRoute ["enumerated"] (("generated_predicates", generatedPredicates) :: (elaborateChoices ++ filledFields)),
        elaborateRoute ["superposed"] (("generated_predicates", generatedPredicates) ::
          (elaborateChoices ++ elaborateSuperposed ++ filledFields))]]

def conflict : Shape :=
  c
    "Readings.Run.runConflict: a witness's verdict on its target with the choice its model encodes, or the conflict status the certificates show under the assumed choice."
    [
      .anyOf [
        n [
          obj,
          .required ["id", "status", "verdict", "target", "assumed", "choice"],
          closed [
            ("id", ref "common.json#/$defs/id_ok"),
            ("status", constS "ok"),
            ("verdict", enumS ["CONFLICT", "UNKNOWN"]),
            ("target", n [str, .equals "/witness/target"]),
            ("assumed", ref "#/$defs/choice"),
            ("choice", ref "#/$defs/choice")]],
        n [
          obj,
          .required ["id", "status", "verdict", "assumed", "targets", "reading_premises"],
          closed [
            ("id", ref "common.json#/$defs/id_ok"),
            ("status", constS "ok"),
            ("verdict", enumS ["CONFLICT-FREE", "UNKNOWN"]),
            ("assumed", ref "#/$defs/choice"),
            ("targets", ref "common.json#/$defs/strings"),
            ("reading_premises", ref "common.json#/$defs/strings")]]]]

def certificate : Shape :=
  c "Readings.Run.runCertificate: accepted exactly when the conflict status is certified and the certificate checks." [
    obj,
    .required ["id", "status", "accepted", "conflict_free", "valid", "assumed", "reading_premises"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("accepted", .type ["boolean"]),
      ("conflict_free", .type ["boolean"]),
      ("valid", .type ["boolean"]),
      ("assumed", ref "#/$defs/choice"),
      ("reading_premises", ref "common.json#/$defs/strings")]]

def model : Shape :=
  c "Readings.Run.runModel: the model's check, the conclusion's value, the first failing premise and the choice it encodes." [
    obj,
    .required ["id", "status", "valid", "conclusion_value", "first_failing", "assumed", "choice"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("valid", .type ["boolean"]),
      ("conclusion_value", .type ["boolean"]),
      ("first_failing", .type ["string", "null"]),
      ("assumed", ref "#/$defs/choice"),
      ("choice", ref "#/$defs/choice")]]

def dead : Shape :=
  c "Readings.Run.runDead: whether the certificate shows the reading dead (or the readings unsatisfiable), and the finding." [
    obj,
    .required ["id", "status", "accepted", "finding"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("accepted", .type ["boolean"]),
      ("finding", .anyOf [
        .type ["null"],
        n [str, .pattern (Re.prefixes ["ReadingsUnsatisfiable: ", "DeadReading: "])]])]]

def choice_answer : Shape :=
  c
    "Readings.Run.runChoice: the choice, the document hash of its document, the number of its regenerated assertions and the lower route's answer to the inner case; for a certificate kind also the conflict status and acceptance. The inner answer is the lower route's row for the inner case, whose kind is not the request's, so no row shape of a lower mode selects it here: the caller reads it as that route's answer."
    [
      obj,
      .required ["id", "status", "choice", "document_hash", "assertions", "inner"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("choice", ref "#/$defs/choice"),
        ("document_hash", ref "common.json#/$defs/hex64"),
        ("assertions", ref "common.json#/$defs/nat"),
        ("inner", c "the lower route's row for the inner case" []),
        ("conflict_free", .type ["boolean"]),
        ("accepted", .type ["boolean"])]]

def verdicts_result : Shape :=
  c "Readings.Run.resultOf: the question's result in the form the report gives it (conflictResult, premisesResult, entailmentResult, or W2's budget shape); the caller relays it." [
    obj,
    .required ["route"],
    closed [
      ("status", c "relayed as Lean gives it" []),
      ("route", constS "enumerated"),
      ("conditional_on", c "relayed as Lean gives it" []),
      ("restrictions", c "relayed as Lean gives it" []),
      ("reading_premises_used", c "relayed as Lean gives it" []),
      ("status_text", c "relayed as Lean gives it" []),
      ("choices", c "relayed as Lean gives it" []),
      ("witnesses", c "relayed as Lean gives it" []),
      ("evidence", c "relayed as Lean gives it" []),
      ("choice", c "relayed as Lean gives it" []),
      ("model", c "relayed as Lean gives it" []),
      ("candidates", c "relayed as Lean gives it" []),
      ("verdict", c "relayed as Lean gives it" []),
      ("conflict_status", c "relayed as Lean gives it" []),
      ("proofs", c "relayed as Lean gives it" []),
      ("countermodels", c "relayed as Lean gives it" []),
      ("proof", c "relayed as Lean gives it" []),
      ("countermodel", c "relayed as Lean gives it" []),
      ("assumed", c "relayed as Lean gives it" []),
      ("budget", c "relayed as Lean gives it" []),
      ("units", c "relayed as Lean gives it" [])]]

def verdicts_word : Shape :=
  enumS ["CONFLICT-FREE", "CONFLICT", "UNKNOWN", "proved", "refuted", "model", "INCONSISTENT"]

def verdicts_row : Shape :=
  c "Readings.Run.perChoiceJson: one compatible choice taking assumed, its rows and what Lean made of each piece of its evidence (maps keyed by the piece: accepted, its refusal, its shown model, its filled gaps)." [
    obj,
    .required ["choice", "conflict", "evidence", "errors", "shown", "gaps", "status_text"],
    closed [
      ("choice", ref "#/$defs/choice"),
      ("conflict", verdicts_word),
      ("query", verdicts_word),
      ("premises", verdicts_word),
      ("evidence", n [obj, .object [] (some (.type ["boolean"]))]),
      ("errors", n [obj, .object [] (some str)]),
      ("shown", n [obj, .object [] (some (c "a shown model, the generator's complete model" []))]),
      ("gaps", n [obj, .object [] (some arr)]),
      ("status_text", .type ["string", "null"])]]

def verdicts_line : Shape :=
  c "Readings.Line.json: one line of the English plan (readings-defaults 2.4)." [
    obj,
    .required ["frame", "result", "readings", "model", "gaps", "label"],
    closed [
      ("frame", str),
      ("result", .type ["string", "null"]),
      ("readings", ref "#/$defs/choice"),
      ("model", .type ["string", "null"]),
      ("gaps", arr),
      ("label", .type ["string", "null"])]]

def verdicts_dead : Shape :=
  c "Readings.Run.deadOf: what Lean made of one dead reading's certificate." [
    obj,
    .required ["accepted"],
    closed [("set", str), ("index", ref "common.json#/$defs/nat"), ("accepted", .type ["boolean"])]]

def verdicts : Shape :=
  c
    "Readings.Run.runVerdicts (readings-defaults RD-3): on the enumerated route, the question's answer folded in Lean over the compatible choices taking assumed: the result in the form the report gives it, one entry per choice with its rows and what Lean made of each piece of evidence, the labels E3 cites, the dead readings, the untaken candidates and the dead evidence (premises), and the English plan."
    [
      obj,
      .required ["id", "status", "route", "question", "finding_sets", "restrictions", "result", "per_choice", "labels",
        "dead_readings", "untaken", "dead", "english"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("route", constS "enumerated"),
        ("question", str),
        ("finding_sets", ref "common.json#/$defs/strings"),
        ("restrictions", ref "common.json#/$defs/strings"),
        ("result", ref "#/$defs/verdicts_result"),
        ("per_choice", n [arr, .items (ref "#/$defs/verdicts_row")]),
        ("labels", ref "common.json#/$defs/strings"),
        ("dead_readings", .anyOf [
          .type ["null"],
          n [arr, .items (n [
            obj,
            .required ["set", "index", "finding"],
            closed [("set", str), ("index", ref "common.json#/$defs/nat"),
              ("finding", n [str, .pattern (Re.prefixes ["DeadReading: "])])]])]]),
        ("untaken", ref "#/$defs/choice"),
        ("dead", n [arr, .items (ref "#/$defs/verdicts_dead")]),
        ("english", n [arr, .items (ref "#/$defs/verdicts_line")])]]

def «row» : Shape :=
  .select [
    (ref "#/$defs/kind/readings-validate", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      ref "#/$defs/validate"]),
    (ref "#/$defs/kind/readings-separate", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      ref "#/$defs/separate"]),
    (ref "#/$defs/kind/readings-elaborate", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      ref "#/$defs/elaborate"]),
    (ref "#/$defs/kind/readings-conflict", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      ref "#/$defs/conflict"]),
    (ref "#/$defs/kind/readings-certificate", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      ref "#/$defs/certificate"]),
    (ref "#/$defs/kind/readings-model", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      ref "#/$defs/model"]),
    (ref "#/$defs/kind/readings-dead", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      ref "#/$defs/dead"]),
    (ref "#/$defs/kind/readings-choice", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      ref "#/$defs/choice_answer"]),
    (ref "#/$defs/kind/readings-verdicts", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      ref "#/$defs/verdicts"]),
    ((.bool true), .anyOf [
      ref "rights.json#/row",
      ref "soft-norms.json#/row",
      ref "norm-defaults.json#/row",
      ref "norms.json#/row"])]

def file : File where
  name := "readings-route.json"
  comment := some "Mode readings-route: Readings.Run.runCaseReported (formerly ve_readings_route). readings-validate, readings-separate and the S2a kinds (Readings.Run.runS2) are the readings runner's; every other case goes, with readings@1 stripped from its profiles, to the runner Compose.dispatch names (rights, soft-norms or norm-defaults, else norms; Readings.Run.runLower). The client does not evaluate Compose.dispatch, so such a row is any of those four modes' rows for the case."
  top := [("row", «row»)]
  defs := [
    ("kind", kind),
    ("pair", .schema pair),
    ("key", .schema key),
    ("keys", .schema keys),
    ("candidate", .schema candidate),
    ("validate", .schema validate),
    ("fill_premises", .schema fill_premises),
    ("filled", .schema filled),
    ("separate", .schema separate),
    ("choice", .schema choice),
    ("elaborate", .schema elaborate),
    ("conflict", .schema conflict),
    ("certificate", .schema certificate),
    ("model", .schema model),
    ("dead", .schema dead),
    ("choice_answer", .schema choice_answer),
    ("verdicts_result", .schema verdicts_result),
    ("verdicts_row", .schema verdicts_row),
    ("verdicts_line", .schema verdicts_line),
    ("verdicts_dead", .schema verdicts_dead),
    ("verdicts", .schema verdicts)]

end ResponseShape.Schemas.ReadingsRoute
