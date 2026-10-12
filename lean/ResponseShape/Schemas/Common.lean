import VE.Service.Protocol
import ResponseShape

/-! `common.json`: the value domains every mode shares. Each domain of a Lean decoder is the
decoder's own (`lean` nodes: the decoder decides every value beside the grammar and the two
must agree), and each enumeration the Lean list it names. -/
namespace ResponseShape.Schemas.Common
open Lean ResponseShape

/-- `Route.Admission.tokenChar`. -/
def tokenRe : Re := .rep (.cls [('A', 'Z'), ('a', 'z'), ('0', '9'), ('_', '_'), ('.', '.'), ('-', '-')]) 1 64

/-- A natural number in canonical decimal. -/
def natRe : Re := .alt (.lit "0") (.seq (.cls [('1', '9')]) (.star (.cls [('0', '9')])))

def seqs : List Re → Re
  | [] => .eps
  | [r] => r
  | r :: rs => .seq r (seqs rs)

def alts : List Re → Re
  | [] => .empty
  | [r] => r
  | r :: rs => .alt r (alts rs)

def onString (f : String → Bool) : Json → Bool
  | .str s => f s
  | _ => false

def text : Shape :=
  n [str, .minLength 1]

def code : Shape :=
  c
    "Service.Protocol.rejectionCode: the public diagnostic code of a rejection, which the client relays with the message (docs/LEAN-FIRST-PLAN.md, batch 0); the handshake's codes."
    [enumS VE.Service.rejectionCodes]

def nat : Shape :=
  n [.type ["integer"], .minimum 0]

def booleans : Shape :=
  n [arr, .items (.type ["boolean"])]

def strings : Shape :=
  n [arr, .items str]

def hex64 : Shape :=
  c "SHA-256 digests (CertificateWire.digest, Service.Protocol.caseDigest)." [
    str,
    .pattern (.rep (.cls [('0', '9'), ('a', 'f')]) 64 64)]

def token : Shape :=
  .lean "Route.Admission.token" (c "Route.Admission.token: nonempty, at most 64 bytes, [A-Za-z0-9_.-]." [
    str,
    .pattern tokenRe]) (onString VE.Route.Admission.token)

def integer_text : Shape :=
  .lean "Order.Wire.decodeInt" (c "Order.Wire.decodeInt: canonical decimal, at most maxNumeralChars = 40 characters." [
    str,
    .maxLength 40,
    .pattern (.alt (.lit "0") (.seq (Re.optional (.lit "-")) (.seq (.cls [('1', '9')]) (.star (.cls [('0', '9')])))))])
    (onString fun s => (VE.Order.Wire.decodeInt s).toBool)

def values : Shape :=
  c "Evaluation values: one per requested formula (binding to the request's ast)." [
    arr,
    .items (.type ["boolean"]),
    .length "/ast"]

def fol_term : Shape :=
  c "Bridge.decodeTerm." [.tagged [("var", [ref "#/$defs/nat"]), ("const", [str])]]

def fol_formula : Shape :=
  .lean "Bridge.decodeFormula 64" (c "Bridge.decodeFormula 64: a formula the runner decoded from the request (a claim)." [
    .fuel "fol_formula" 64,
    .tagged [
      ("top", []),
      ("bottom", []),
      ("unary", [str, ref "#/$defs/fol_term"]),
      ("binary", [str, ref "#/$defs/fol_term", ref "#/$defs/fol_term"]),
      ("eq", [ref "#/$defs/fol_term", ref "#/$defs/fol_term"]),
      ("not", [ref "#/$defs/fol_formula"]),
      ("and", [ref "#/$defs/fol_formula", ref "#/$defs/fol_formula"]),
      ("or", [ref "#/$defs/fol_formula", ref "#/$defs/fol_formula"]),
      ("implies", [ref "#/$defs/fol_formula", ref "#/$defs/fol_formula"]),
      ("forall", [str, ref "#/$defs/fol_formula"]),
      ("exists", [str, ref "#/$defs/fol_formula"])]])
    (fun j => (VE.Bridge.decodeFormula 64 j).toBool)

def generated_formula : Shape :=
  decidedBy "Bridge.decodeFormula" (fun j => (VE.Bridge.decodeFormula j.compress.length j).toBool) <|
  c
    "Route.Wire.encodeFormula of a formula the runner generated (Background, norms premises and conflict targets, English parses): Bridge.decodeFormula's grammar at any depth. The decoder's 64 bounds the inputs, not these: a definition premise wraps a body of depth 64 in two binders and a biconditional (68), an English parse nests one negation per 'it is not the case that', and a norms elaboration nests every rule, carve-out and lower layer."
    [
      .tagged [
        ("top", []),
        ("bottom", []),
        ("unary", [str, ref "#/$defs/fol_term"]),
        ("binary", [str, ref "#/$defs/fol_term", ref "#/$defs/fol_term"]),
        ("eq", [ref "#/$defs/fol_term", ref "#/$defs/fol_term"]),
        ("not", [ref "#/$defs/generated_formula"]),
        ("and", [ref "#/$defs/generated_formula", ref "#/$defs/generated_formula"]),
        ("or", [ref "#/$defs/generated_formula", ref "#/$defs/generated_formula"]),
        ("implies", [ref "#/$defs/generated_formula", ref "#/$defs/generated_formula"]),
        ("forall", [str, ref "#/$defs/generated_formula"]),
        ("exists", [str, ref "#/$defs/generated_formula"])]]

def generated_formulas : Shape :=
  n [arr, .items (ref "#/$defs/generated_formula")]

def order_term : Shape :=
  c "Order.Wire.decodeTerm 64." [
    .fuel "order_term" 64,
    .tagged [
      ("var", [ref "#/$defs/nat"]),
      ("const", [str]),
      ("num", [ref "#/$defs/integer_text"]),
      ("add", [ref "#/$defs/order_term", ref "#/$defs/order_term"]),
      ("scale", [ref "#/$defs/integer_text", ref "#/$defs/order_term"])]]

def order_formula : Shape :=
  .lean "Order.Wire.decodeFormula 64" (c "Order.Wire.decodeFormula 64; each term has its own depth budget." [
    .fuel "order_formula" 64,
    .tagged [
      ("top", []),
      ("bottom", []),
      ("unary", [str, ref "#/$defs/order_term"]),
      ("binary", [str, ref "#/$defs/order_term", ref "#/$defs/order_term"]),
      ("eq", [ref "#/$defs/order_term", ref "#/$defs/order_term"]),
      ("lt", [ref "#/$defs/order_term", ref "#/$defs/order_term"]),
      ("le", [ref "#/$defs/order_term", ref "#/$defs/order_term"]),
      ("not", [ref "#/$defs/order_formula"]),
      ("and", [ref "#/$defs/order_formula", ref "#/$defs/order_formula"]),
      ("or", [ref "#/$defs/order_formula", ref "#/$defs/order_formula"]),
      ("implies", [ref "#/$defs/order_formula", ref "#/$defs/order_formula"]),
      ("forall", [str, ref "#/$defs/order_formula"]),
      ("exists", [str, ref "#/$defs/order_formula"])]])
    (fun j => (VE.Order.Wire.decodeFormula 64 j).toBool)

def atomic_kind : Shape :=
  decidedBy "Route.Admission.atomicKind" (onString fun s => (VE.Route.Admission.atomicKind s).isSome) <|
  c "Route.Admission.atomicKind." [
    enumS [
      "asserted",
      "norm",
      "definition",
      "question",
      "instruction",
      "example",
      "exposition",
      "analogy",
      "explanation",
      "meta"]]

def act : Shape :=
  c "Route.Admission.acts." [enumS VE.Route.Admission.acts]

def modality : Shape :=
  c "Route.Admission.modalities." [enumS VE.Route.Admission.modalities]

def relation : Shape :=
  c "Route.Admission.relations." [enumS VE.Route.Admission.relations]

def kind : Shape :=
  .lean "Route.Admission.decodeKind 16" (c "Route.Admission.decodeKind 16." [
    .fuel "kind" 16,
    .anyOf [
      n [str, ref "#/$defs/atomic_kind"],
      n [
        arr,
        .tagged [
          ("attributed", [ref "#/$defs/token", ref "#/$defs/act", ref "#/$defs/kind"]),
          ("hedged", [ref "#/$defs/modality", ref "#/$defs/kind"]),
          ("causal", [ref "#/$defs/relation", ref "#/$defs/kind", ref "#/$defs/kind"]),
          ("unformalised", [ref "#/$defs/token"])]]]])
    (fun j => (VE.Route.Admission.decodeKind 16 j).toBool)

def generator : Shape :=
  c "Route.Background.generators." [enumS VE.Route.Background.generators]

def label : Shape :=
  .lean "Route.Admission.parseLabel" (c "Canonical labels: Route.Admission.parseLabel (the parsed label renders to the input)." [
    str,
    .pattern (alts [
      .lit "asserted",
      seqs [.lit "bridge:accepts(", tokenRe, .lit ",", tokenRe, .lit ")"],
      seqs [.lit "background:", Re.oneOf VE.Route.Background.generators],
      seqs [.lit "cite:", tokenRe, .lit "/", tokenRe],
      seqs [.lit "open:", tokenRe],
      seqs [.lit "readings:", tokenRe, .lit "@", natRe, .lit ":", .alt natRe (.lit "all")],
      seqs [.lit "narrowing:", tokenRe]])])
    (onString fun s => (VE.Route.Admission.parseLabel s).isSome)

def claim : Shape :=
  c "Route.Run.claimJson: a decoded graph node of the request, re-encoded; the default label is omitted." [
    obj,
    .required ["name", "ast"],
    closed [("name", str), ("ast", ref "#/$defs/fol_formula"), ("label", n [str, .not (constS "asserted")])]]

def admission : Shape :=
  c
    "Route.Run.runAdmit and Norms.Run.encodeAdmitted: every claim belongs to the request graph, the root is the request's root and kinds are the request's unit kinds (decodeKind_render). The exact unfolding remains the service's invariant."
    [
      obj,
      .claimNodes ["/report/root", "/report/assumptions"],
      .required ["id", "status", "admitted", "report", "report_id", "kinds"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("admitted", .const (.bool true)),
        ("report", n [
          obj,
          .required ["root", "assumptions"],
          closed [
            ("root", n [ref "#/$defs/claim", props [("name", .equals "/document/graph/root")]]),
            ("assumptions", n [arr, .items (ref "#/$defs/claim")])]]),
        ("report_id", ref "#/$defs/hex64"),
        ("kinds", n [arr, .items (ref "#/$defs/kind"), .equals "/document/units/*/kind"])]]

def case_error : Shape :=
  c "Service.Protocol.caseError: a case the batch decoder rejected on its own." [
    obj,
    .required ["status", "case_index", "error"],
    closed [
      ("status", constS "error"),
      ("case_index", n [.type ["integer"], .index]),
      ("error", ref "#/$defs/text")]]

def case_error_valid : Shape :=
  c "Service.Protocol.caseError for check-certificate and order." [
    obj,
    .required ["status", "case_index", "error", "valid"],
    closed [
      ("status", constS "error"),
      ("case_index", n [.type ["integer"], .index]),
      ("error", ref "#/$defs/text"),
      ("valid", .const (.bool false))]]

def error : Shape :=
  c "A case the runner rejected: the request's id (null if absent), message, and optional model JSON pointer." [
    obj,
    .required ["id", "status", "error"],
    closed [("id", .echo "/id"), ("status", constS "error"),
      ("error", ref "#/$defs/text"), ("path", str)]]

def error_valid : Shape :=
  c "The same with valid: false (CertificateWire and Order.Surface runCaseReported)." [
    obj,
    .required ["id", "status", "error", "valid"],
    closed [
      ("id", .echo "/id"),
      ("status", constS "error"),
      ("error", ref "#/$defs/text"),
      ("valid", .const (.bool false))]]

def no_kind : Shape :=
  c "Selector over the request case: no kind field." [obj, .not (.required ["kind"])]

def id_ok : Shape :=
  c "Route.Wire.ok: an answer's id is the request's id, a string (Bridge.stringField)." [str, .equals "/id"]

def hex64_or_empty : Shape :=
  c "An identity the encoder writes as `.toOption.getD \"\"`." [.anyOf [ref "#/$defs/hex64", constS ""]]

def nonempty_strings : Shape :=
  n [arr, .items (ref "#/$defs/text")]

def string_map : Shape :=
  c "An object with string values." [obj, .object [] (some str)]

/-- The predicate entry required of source, decision and rights-generated environment fields. -/
def environment_predicate : Shape :=
  n [obj, .required ["arguments"], props [("arguments", ref "#/$defs/strings")]]

def string_pair : Shape :=
  n [arr, .prefixItems [str, str], .minItems 2, .maxItems 2]

def report : Shape :=
  c "Norms.Run.reportJson: the root and its assumptions, each a Route.Run.claimJson." [
    obj,
    .required ["root", "assumptions"],
    closed [("root", ref "#/$defs/claim"), ("assumptions", n [arr, .items (ref "#/$defs/claim")])]]

def bound_report : Shape :=
  c "A report whose root and assumptions are claims of the request graph." [
    ref "#/$defs/report",
    .claimNodes ["/root", "/assumptions"],
    props [("root", props [("name", .equals "/document/graph/root")])]]

def labelled : Shape :=
  c "Route.Wire.labelled and its copies: a premise label and its generated formula." [
    obj,
    .required ["label", "ast"],
    closed [("label", ref "#/$defs/text"), ("ast", ref "#/$defs/generated_formula")]]

def labelled_list : Shape :=
  n [arr, .items (ref "#/$defs/labelled")]

def norms_background : Shape :=
  c "Norms.Wire.regenerated: the Background of the definitions, literals and profile generators." [
    arr,
    .items (n [
        obj,
        .required ["generator", "ast"],
        closed [
          ("generator", enumS ["definitions", "literals", "profile"]),
          ("ast", ref "#/$defs/generated_formula")]])]

def layer_premises : Shape :=
  c "Norms.Wire.regenerated: one premise per layer." [
    arr,
    .items (n [
        obj,
        .required ["label", "ast"],
        closed [
          ("label", n [str, .pattern (Re.prefixes ["layer:norms:"])]),
          ("ast", ref "#/$defs/generated_formula")]])]

def conflict_targets : Shape :=
  c "Norms.Wire.regenerated: one target per layer, then per declared pair, with its argument sorts." [
    arr,
    .items (n [
        obj,
        .required ["target", "sorts", "ast"],
        closed [
          ("target", ref "#/$defs/text"),
          ("sorts", ref "#/$defs/strings"),
          ("ast", ref "#/$defs/generated_formula")]])]

def norm_node : Shape :=
  c "Alternatives.Wire.encodeNode and SpeechActs.Run.encodeNode: a norm of the inlined tree." [
    obj,
    .required ["name", "predicate", "sign", "guard", "unless", "over"],
    closed [
      ("name", str),
      ("predicate", str),
      ("sign", .type ["boolean"]),
      ("guard", ref "#/$defs/generated_formula"),
      ("unless", ref "#/$defs/generated_formulas"),
      ("over", ref "#/$defs/strings")]]

def witness_conflict : Shape :=
  c "A conflict witness replay (Norms.Replay.witnessFrom and its copies): the requested target." [
    obj,
    .required ["id", "status", "verdict", "target", "targets"],
    closed [
      ("id", ref "#/$defs/id_ok"),
      ("status", constS "ok"),
      ("verdict", enumS ["CONFLICT", "UNKNOWN"]),
      ("target", n [str, .equals "/witness/target"]),
      ("targets", ref "#/$defs/strings")]]

def packages_conflict : Shape :=
  c
    "A conflict-freedom replay over certificate packages: `detail` (the first failed target) exactly when the verdict is UNKNOWN."
    [
      obj,
      .required ["id", "status", "verdict", "targets"],
      closed [
        ("id", ref "#/$defs/id_ok"),
        ("status", constS "ok"),
        ("verdict", enumS ["CONFLICT-FREE", "UNKNOWN"]),
        ("targets", ref "#/$defs/strings"),
        ("detail", ref "#/$defs/text")],
      .ite (props [("verdict", constS "UNKNOWN")]) (.required ["detail"]) (.not (.required ["detail"]))]

def route_path_error : Shape :=
  c
    "The error row of a statement-layer route's own runner (`runCaseReported`): the request's id (null if absent) and the message. The public code (and generator) is the bound entry's (envelope.json)."
    [
      obj,
      .required ["id", "status", "error"],
      closed [("id", .echo "/id"), ("status", constS "error"), ("error", ref "#/$defs/text")]]

def environment : Shape :=
  encodedEnvironment (c
    "Norms.Wire.canonicalEnvironmentJson and its extensions (SoftNorms.Wire.primeJson, Rights.Wire.primeJsonR): the request environment after its envelope check (exactly language, profiles, spec_revision and vocabulary), with decision and generated predicates added. Its content is compared with Python's regeneration by the caller."
    [
      obj,
      .required ["language", "profiles", "spec_revision", "vocabulary"],
      closed [
        ("language", n [str, .equals "/environment/language"]),
        ("profiles", ref "#/$defs/strings"),
        ("spec_revision", n [str, .equals "/environment/spec_revision"]),
        ("vocabulary", n [
          obj,
          .required ["sorts", "predicates", "constants"],
          closed [
            ("sorts", n [obj, .equals "/environment/vocabulary/sorts"]),
            ("constants", n [obj, .equals "/environment/vocabulary/constants"]),
            ("predicates", n [
              obj,
              .object [] (some (ref "#/$defs/environment_predicate"))]),
            ("soft", n [obj, .equals "/environment/vocabulary/soft"]),
            ("rights", n [obj, .equals "/environment/vocabulary/rights"])],
          .allOf [
            .ite (.onCase (ref "#/$defs/request_block/soft")) (.required ["soft"]) (.bool true),
            .ite (.onCase (ref "#/$defs/request_block/rights")) (.required ["rights"]) (.bool true)]])]])

def request_block : Def :=
  .group (some "Selectors over the request case: its environment's vocabulary declares the block.") [
    ("soft", n [
      obj,
      .required ["environment"],
      props [
        ("environment", n [obj, .required ["vocabulary"], props [("vocabulary", n [obj, .required ["soft"]])]])]]),
    ("rights", n [
      obj,
      .required ["environment"],
      props [
        ("environment", n [obj, .required ["vocabulary"], props [("vocabulary", n [obj, .required ["rights"]])]])]])]

def file : File where
  name := "common.json"
  comment := some "Shared value domains of Lean service results. Every domain is the one the named Lean decoder accepts (lean/VE/...). Every file of this directory is rendered from lean/ResponseShape/Schemas (tools/response_schemas.py; never edit it by hand): the response validator in ve/backends/lean_service.py is compiled from these files, and ve_response_decode (lean/ResponseDecode.lean) decides responses with the same Lean shapes, the named decoders deciding beside them. Well-formedness, request binding and certificate step and background counts are described here; graph unfoldings, dependency orders and verdict details remain the service's responsibility and are tested on its outputs (docs/spec/lean-service.md, threat model). Dialect: README.md in this directory."
  top := []
  defs := [
    ("text", .schema text),
    ("code", .schema code),
    ("nat", .schema nat),
    ("booleans", .schema booleans),
    ("strings", .schema strings),
    ("hex64", .schema hex64),
    ("token", .schema token),
    ("integer_text", .schema integer_text),
    ("values", .schema values),
    ("fol_term", .schema fol_term),
    ("fol_formula", .schema fol_formula),
    ("generated_formula", .schema generated_formula),
    ("generated_formulas", .schema generated_formulas),
    ("order_term", .schema order_term),
    ("order_formula", .schema order_formula),
    ("atomic_kind", .schema atomic_kind),
    ("act", .schema act),
    ("modality", .schema modality),
    ("relation", .schema relation),
    ("kind", .schema kind),
    ("generator", .schema generator),
    ("label", .schema label),
    ("claim", .schema claim),
    ("admission", .schema admission),
    ("case_error", .schema case_error),
    ("case_error_valid", .schema case_error_valid),
    ("error", .schema error),
    ("error_valid", .schema error_valid),
    ("no_kind", .schema no_kind),
    ("id_ok", .schema id_ok),
    ("hex64_or_empty", .schema hex64_or_empty),
    ("nonempty_strings", .schema nonempty_strings),
    ("string_map", .schema string_map),
    ("environment_predicate", .schema environment_predicate),
    ("string_pair", .schema string_pair),
    ("report", .schema report),
    ("bound_report", .schema bound_report),
    ("labelled", .schema labelled),
    ("labelled_list", .schema labelled_list),
    ("norms_background", .schema norms_background),
    ("layer_premises", .schema layer_premises),
    ("conflict_targets", .schema conflict_targets),
    ("norm_node", .schema norm_node),
    ("witness_conflict", .schema witness_conflict),
    ("packages_conflict", .schema packages_conflict),
    ("route_path_error", .schema route_path_error),
    ("environment", .schema environment),
    ("request_block", request_block)]

end ResponseShape.Schemas.Common
