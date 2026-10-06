import VE.Service.Protocol
import ResponseShape
import ResponseShape.CaseDeciders

/-! The source of `ve/backends/lean_service_schema/speech-acts.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.SpeechActs
open Lean ResponseShape

def speech_path : Shape :=
  decidedCase .speechPath <|
  c
    "SpeechActs.Run.usesSpeechPath: the speech-acts@0 profile, the environment's speech_acts block, a speech-* kind, or a unit of kind binding or with command or question content."
    [
      obj,
      .anyOf [
        n [
          .required ["environment"],
          props [
            ("environment", n [
              obj,
              .required ["profiles"],
              props [("profiles", n [arr, .contains (constS "speech-acts@0")])]])]],
        n [.required ["environment"], props [("environment", n [obj, .required ["speech_acts"]])]],
        n [.required ["kind"], props [("kind", n [str, .pattern (Re.prefixes ["speech-"])])]],
        n [
          .required ["document"],
          props [
            ("document", n [
              obj,
              .required ["units"],
              props [
                ("units", n [
                  arr,
                  .contains (n [
                      obj,
                      .anyOf [
                        n [.required ["kind"], props [("kind", constS "binding")]],
                        n [.required ["content"], props [("content", n [obj, .required ["command"]])]],
                        n [.required ["content"], props [("content", n [obj, .required ["question"]])]]]])])]])]]]]

def kind : Def :=
  .group none [
    ("speech-elaborate", kindIs "speech-elaborate"),
    ("speech-answer", kindIs "speech-answer"),
    ("speech-consequence", kindIs "speech-consequence"),
    ("speech-conflict", kindIs "speech-conflict")]

def question : Shape :=
  c
    "SpeechActs.Run.questionJson with its meaning id: unit, mode, presupposition and meaning_id, then the mode's fields."
    [
      obj,
      .required ["unit", "mode", "presupposition", "meaning_id"],
      props [
        ("unit", str),
        ("mode", enumS ["polar", "which_one", "which_all", "follows", "reading"]),
        ("presupposition", ref "common.json#/$defs/generated_formula"),
        ("meaning_id", ref "common.json#/$defs/hex64_or_empty")],
      .anyOf [
        n [
          .required ["tokens", "body"],
          closed [
            ("unit", (.bool true)),
            ("mode", constS "polar"),
            ("presupposition", (.bool true)),
            ("meaning_id", (.bool true)),
            ("tokens", .const (Json.arr #[(.str "yes"), (.str "no")])),
            ("body", ref "common.json#/$defs/generated_formula")]],
        n [
          .required ["tokens", "body"],
          closed [
            ("unit", (.bool true)),
            ("mode", constS "which_one"),
            ("presupposition", (.bool true)),
            ("meaning_id", (.bool true)),
            ("tokens", ref "common.json#/$defs/strings"),
            ("body", ref "common.json#/$defs/generated_formula")]],
        n [
          .required ["domain", "body"],
          closed [
            ("unit", (.bool true)),
            ("mode", constS "which_all"),
            ("presupposition", (.bool true)),
            ("meaning_id", (.bool true)),
            ("domain", ref "common.json#/$defs/strings"),
            ("body", ref "common.json#/$defs/generated_formula")]],
        n [
          .required ["query"],
          closed [
            ("unit", (.bool true)),
            ("mode", constS "follows"),
            ("presupposition", (.bool true)),
            ("meaning_id", (.bool true)),
            ("query", str)]],
        n [
          .required ["set", "version"],
          closed [
            ("unit", (.bool true)),
            ("mode", constS "reading"),
            ("presupposition", (.bool true)),
            ("meaning_id", (.bool true)),
            ("set", str),
            ("version", ref "common.json#/$defs/nat")]]]]

def elaborate : Shape :=
  c
    "SpeechActs.Run.elaborated: the environment id, the effective scope (Wire.encodeScope), its legend, the premises, the policy (Norms.Wire.regenerated of the command tree), the active commands, the dormant ones, the questions and the queries."
    [
      obj,
      .required ["id", "status", "environment_id", "scope", "legend", "premises", "policy", "commands", "dormant", "questions", "queries"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("environment_id", ref "common.json#/$defs/hex64_or_empty"),
        ("scope", n [
          obj,
          .required ["task"],
          closed [
            ("task", str),
            ("addressee", n [obj, .required ["sort", "constant"], closed [("sort", str), ("constant", str)]]),
            ("definites", ref "common.json#/$defs/string_map")]]),
        ("legend", ref "common.json#/$defs/nonempty_strings"),
        ("premises", ref "common.json#/$defs/generated_formulas"),
        ("policy", n [
          obj,
          .required ["order", "background", "premises", "conflict_targets", "fragment"],
          closed [
            ("order", ref "common.json#/$defs/strings"),
            ("background", ref "common.json#/$defs/norms_background"),
            ("premises", ref "common.json#/$defs/layer_premises"),
            ("conflict_targets", ref "common.json#/$defs/conflict_targets"),
            ("fragment", .type ["boolean"])]]),
        ("commands", n [
          arr,
          .items (n [
              obj,
              .required ["unit", "force", "demand", "paraphrase", "meaning_id"],
              closed [
                ("unit", str),
                ("force", enumS ["require", "forbid"]),
                ("demand", ref "common.json#/$defs/norm_node"),
                ("paraphrase", n [
                  str,
                  .pattern (Re.prefixes ["In this task, you are required to ", "In this task, you are not permitted to "])]),
                ("meaning_id", ref "common.json#/$defs/hex64_or_empty")]])]),
        ("dormant", ref "common.json#/$defs/strings"),
        ("questions", n [arr, .items (ref "#/$defs/question")]),
        ("queries", n [
          arr,
          .items (n [
              obj,
              .required ["id", "premises", "target"],
              closed [
                ("id", str),
                ("premises", ref "common.json#/$defs/generated_formulas"),
                ("target", ref "common.json#/$defs/generated_formula"),
                ("warning", n [str, .pattern (Re.prefixes ["TrivialQuery: "])])]])])]]

def answer : Shape :=
  c "SpeechActs.Run speech-answer: the requested question and its answer line (AnswerReplay.line)." [
    obj,
    .required ["id", "status", "question", "answer"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("question", n [str, .equals "/question"]),
      ("answer", ref "common.json#/$defs/text")]]

def consequence : Shape :=
  c "SpeechActs.Run speech-consequence: the requested query and its judgment." [
    obj,
    .required ["id", "status", "query", "judgment"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("query", n [str, .equals "/query"]),
      ("judgment", n [str, .pattern (Re.prefixes ["follows (", "gap (", "unresolved ("])])]]

def «row» : Shape :=
  .select [
    (ref "#/$defs/speech_path", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      .select [
        (ref "#/$defs/kind/speech-elaborate", ref "#/$defs/elaborate"),
        (ref "#/$defs/kind/speech-answer", ref "#/$defs/answer"),
        (ref "#/$defs/kind/speech-consequence", ref "#/$defs/consequence"),
        (.allOf [ref "#/$defs/kind/speech-conflict", .required ["witness"]], ref "common.json#/$defs/witness_conflict"),
        (ref "#/$defs/kind/speech-conflict", ref "common.json#/$defs/packages_conflict")]]),
    ((.bool true), ref "norms.json#/row")]

def file : File where
  name := "speech-acts.json"
  comment := some "Mode speech-acts: SpeechActs.Run.runCaseReported (formerly ve_speech_acts_route). A case on the speech path (SpeechActs.Run.usesSpeechPath) is answered by the speech runner; every other case is delegated unchanged to the norms mode's runner."
  top := [("row", «row»)]
  defs := [
    ("speech_path", .schema speech_path),
    ("kind", kind),
    ("question", .schema question),
    ("elaborate", .schema elaborate),
    ("answer", .schema answer),
    ("consequence", .schema consequence)]

end ResponseShape.Schemas.SpeechActs
