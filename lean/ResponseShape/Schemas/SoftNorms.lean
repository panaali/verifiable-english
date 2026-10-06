import VE.Service.Protocol
import ResponseShape

/-! The source of `ve/backends/lean_service_schema/soft-norms.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.SoftNorms
open Lean ResponseShape

def soft_path : Shape :=
  decidedBy "SoftNorms.Run.usesSoftPath" VE.SoftNorms.Run.usesSoftPath <|
  c
    "SoftNorms.Run.usesSoftPath: the soft-norms@0 profile, the vocabulary's soft block, an instruction_of predicate, a soft-* kind, or a soft field (Phases.softKeys) on a norm of `norms` or of a document unit."
    [
      obj,
      .anyOf [
        n [
          .required ["environment"],
          props [
            ("environment", n [
              obj,
              .required ["profiles"],
              props [("profiles", n [arr, .contains (constS "soft-norms@0")])]])]],
        n [
          .required ["environment"],
          props [
            ("environment", n [
              obj,
              .required ["vocabulary"],
              props [("vocabulary", n [obj, .required ["soft"]])]])]],
        n [
          .required ["environment"],
          props [
            ("environment", n [
              obj,
              .required ["vocabulary"],
              props [
                ("vocabulary", n [
                  obj,
                  .required ["predicates"],
                  props [
                    ("predicates", n [
                      obj,
                      .not (.object [] (some (.not (n [obj, .required ["instruction_of"]]))))])]])]])]],
        n [.required ["kind"], props [("kind", n [str, .pattern (Re.prefixes ["soft-"])])]],
        n [.required ["norms"], props [("norms", n [arr, .contains (ref "#/$defs/soft_field")])]],
        n [
          .required ["document"],
          props [
            ("document", n [
              obj,
              .required ["units"],
              props [
                ("units", n [
                  arr,
                  .contains (n [obj, .required ["content"], props [("content", ref "#/$defs/soft_field")]])])]])]]]]

def soft_field : Shape :=
  n [
    obj,
    .required ["norm"],
    props [
      ("norm", n [
        obj,
        .anyOf [
          .required ["mode"],
          .required ["rank"],
          .required ["alterable"],
          .required ["exception"],
          .required ["hard"]]])]]

def kind : Def :=
  .group none [
    ("admission", kindIs "admission"),
    ("soft-rule", kindIs "soft-rule"),
    ("soft-elaborate", kindIs "soft-elaborate"),
    ("soft-pairs", kindIs "soft-pairs"),
    ("soft-certificate", kindIs "soft-certificate"),
    ("soft-conflict", kindIs "soft-conflict")]

def error : Shape :=
  c
    "SoftNorms.Run.runCaseReported: a soft rejection carries its soft-norms@0 contract code (reportedCode), which the relay keeps as the error's code."
    [
      obj,
      .required ["id", "status", "error", "code"],
      closed [
        ("id", .echo "/id"),
        ("status", constS "error"),
        ("error", ref "common.json#/$defs/text"),
        ("code", enumS [
          "SOFT_DEPENDENCY_CYCLE",
          "SOFT_DUPLICATE_DECLARATION",
          "SOFT_EXCEPTION_ARRAY",
          "SOFT_HARD_CONSTRAINT",
          "SOFT_INVALID_ALTERABLE",
          "SOFT_INVALID_ARRAY",
          "SOFT_INVALID_BLOCK",
          "SOFT_INVALID_DECIDER",
          "SOFT_INVALID_EXCEPTION_CONDITION",
          "SOFT_INVALID_FACTORS",
          "SOFT_INVALID_INPUT",
          "SOFT_INVALID_NAME",
          "SOFT_INVALID_OUTRANKING",
          "SOFT_INVALID_OUTRANKS_PAIR",
          "SOFT_INVALID_RULE_FIELDS",
          "SOFT_INVALID_TIES_PAIR",
          "SOFT_MISSING_DECIDER",
          "SOFT_MISSING_EXCEPTION",
          "SOFT_OVER_HARD",
          "SOFT_RESOURCE_LIMIT",
          "SOFT_STRICT_EXCEPTION",
          "SOFT_STRICT_OUTRANKING_DECIDER",
          "SOFT_TIE_AGAINST_ORDER",
          "SOFT_UNKNOWN_PARTY",
          "SOFT_UNKNOWN_RANK",
          "SOFT_UNSUPPORTED_PROFILE"]),
        ("dual_guard_cycle", .const (.bool true))]]

def coherence_labels : Shape :=
  n [arr, .items (n [str, .pattern (Re.prefixes ["soft:coherence:"])])]

def rule : Shape :=
  c "SoftNorms.Run.runSoftKind: Lean accepted the standalone soft rule." [
    obj, .required ["id", "status", "accepted"],
    closed [("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"), ("accepted", .const (.bool true))]]

def admission : Shape :=
  c "SoftNorms.Run.encodeAdmitted: W2's admission answer and the open coherence premises the report assumes." [
    obj,
    .required ["id", "status", "admitted", "report", "report_id", "kinds", "conditional_on"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("admitted", .const (.bool true)),
      ("report", ref "common.json#/$defs/bound_report"),
      ("report_id", ref "common.json#/$defs/hex64"),
      ("kinds", n [arr, .items (ref "common.json#/$defs/kind"), .equals "/document/units/*/kind"]),
      ("conditional_on", ref "#/$defs/coherence_labels")]]

def background : Shape :=
  c
    "SoftNorms.Wire.regenerated: Background' in generator order; a soft premise carries its label (bgEntry), no other does."
    [
      arr,
      .items (n [
          obj,
          .required ["generator", "ast"],
          closed [
            ("generator", enumS ["definitions", "literals", "profile", "soft"]),
            ("ast", ref "common.json#/$defs/generated_formula"),
            ("label", n [str, .pattern (Re.prefixes ["soft:exception:", "soft:coherence:"])])],
          .ite (props [("generator", constS "soft")]) (.required ["label"]) (.not (.required ["label"]))])]

def elaborated : Def :=
  .group (some "SoftNorms.Wire.regenerated without environment_prime: the fields rights-elaborate repeats.") [
    ("decisions", n [
      arr,
      .items (n [
          obj,
          .required ["name", "arguments"],
          closed [
            ("name", n [str, .pattern (Re.prefixes ["soft__"])]),
            ("arguments", ref "common.json#/$defs/strings")]])]),
    ("derived", n [
      arr,
      .items (n [
          obj,
          .required ["rule", "ast"],
          closed [("rule", str), ("ast", .anyOf [.const .null, ref "common.json#/$defs/generated_formula"])]])]),
    ("colliding_pairs", n [
      arr,
      .items (n [
          obj,
          .required ["pair", "act", "comparable", "label", "ast"],
          closed [
            ("pair", ref "common.json#/$defs/string_pair"),
            ("act", str),
            ("comparable", .type ["boolean"]),
            ("label", n [str, .pattern (Re.prefixes ["soft:coherence:"])]),
            ("ast", ref "common.json#/$defs/generated_formula")]])])]

def elaborate : Shape :=
  c
    "SoftNorms.Wire.regenerated: E' (primeJson), the decision predicates, each rule's derived carve-out (null for a strict rule without alterable), the layers, Background', the colliding pairs with their coherence premises, the conflict targets, the open coherence labels, the fragment flag and the warnings."
    [
      obj,
      .required ["id", "status", "environment_prime", "document_hash", "decisions", "ranks_above", "derived", "order", "background", "premises", "colliding_pairs", "conflict_targets", "conditional_on", "soft_residual", "soft_status", "default_exceptions_by_decider", "fragment", "warnings"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("environment_prime", ref "common.json#/$defs/environment"),
        ("document_hash", ref "common.json#/$defs/hex64"),
        ("decisions", ref "#/$defs/elaborated/decisions"),
        ("ranks_above", n [obj, .object [] (some (ref "common.json#/$defs/strings"))]),
        ("derived", ref "#/$defs/elaborated/derived"),
        ("order", ref "common.json#/$defs/strings"),
        ("background", ref "#/$defs/background"),
        ("premises", ref "common.json#/$defs/layer_premises"),
        ("colliding_pairs", ref "#/$defs/elaborated/colliding_pairs"),
        ("conflict_targets", ref "common.json#/$defs/conflict_targets"),
        ("conditional_on", ref "#/$defs/coherence_labels"),
        ("soft_residual", ref "#/$defs/soft_residual"),
        ("soft_status", enumS ["CHECKED", "OPEN"]),
        ("default_exceptions_by_decider", n [obj, .object [] (some (ref "common.json#/$defs/nat"))]),
        ("fragment", .type ["boolean"]),
        ("warnings", ref "common.json#/$defs/nonempty_strings"),
        ("overlaps", copied "A Lean-checked witness echoes its model and tuple, and names the selected pair." <|
          n [arr, .items (n [obj, .required ["pair", "tuple", "model", "line"], closed [
            ("pair", ref "common.json#/$defs/string_pair"),
            ("tuple", ref "common.json#/$defs/strings"),
            ("model", obj),
            ("line", n [str, .pattern (Re.prefixes ["Overlap("])])]])]),
        ("override_cycles", copied "A Lean-checked witness echoes its model and tuple, and names the preference cycle." <|
          n [arr, .items (n [obj, .required ["cycle", "tuple", "model", "line"], closed [
            ("cycle", ref "common.json#/$defs/strings"),
            ("tuple", ref "common.json#/$defs/strings"),
            ("model", obj),
            ("line", n [str, .pattern (Re.prefixes ["override_cycles:"])])]])])]]

def pairs : Shape :=
  c
    "SoftNorms.Run.pairsResult: each colliding pair's status (detail beside a weighing point or UNKNOWN only), the discharged labels and the open ones."
    [
      obj,
      .required ["id", "status", "pairs", "discharged", "weighing_points"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("pairs", n [
          arr,
          .items (n [
              obj,
              .required ["pair", "label", "status"],
              closed [
                ("pair", ref "common.json#/$defs/string_pair"),
                ("label", n [str, .pattern (Re.prefixes ["soft:coherence:"])]),
                ("status", enumS ["RANK-RESOLVED", "DISJOINT", "WEIGHING POINT", "UNKNOWN"]),
                ("detail", ref "common.json#/$defs/text")],
              .ite (props [("status", enumS ["RANK-RESOLVED", "DISJOINT"])]) (.not (.required ["detail"])) (.required
                  ["detail"])])]),
        ("discharged", ref "#/$defs/coherence_labels"),
        ("weighing_points", ref "#/$defs/coherence_labels")]]

def certificate : Shape :=
  c
    "SoftNorms.Run.runSoftKind soft-certificate: the replay's verdict, Background' and layer counts, and the coherence premises a valid certificate is conditional on."
    [
      obj,
      .required ["id", "status", "valid", "background", "layers", "conditional_on"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("valid", .type ["boolean"]),
        ("background", ref "common.json#/$defs/nat"),
        ("layers", ref "common.json#/$defs/nat"),
        ("conditional_on", ref "#/$defs/coherence_labels")]]

def witness : Shape :=
  c
    "SoftNorms.Run.runSoftKind soft-conflict with a witness: the requested target, and its kind beside a CONFLICT."
    [
      obj,
      .required ["id", "status", "verdict", "target", "targets", "status_text"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("verdict", enumS ["CONFLICT", "UNKNOWN"]),
        ("target", n [str, .equals "/witness/target"]),
        ("targets", ref "common.json#/$defs/strings"),
        ("status_text", ref "common.json#/$defs/text"),
        ("witness_kind", n [str, .pattern (Re.prefixes ["pair conflict on ", "strict collision on "])])],
      .ite (props [("verdict", constS "CONFLICT")]) (.required ["witness_kind"]) (.not (.required ["witness_kind"]))]

def packages : Shape :=
  c
    "SoftNorms.Run.runSoftKind soft-conflict over certificate packages: detail exactly beside UNKNOWN (firstFailure)."
    [
      obj,
      .required ["id", "status", "verdict", "status_text", "coherent_exhibit", "budget", "targets", "conditional_on"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("verdict", enumS ["CONFLICT-FREE", "UNKNOWN"]),
        ("status_text", ref "common.json#/$defs/text"),
        ("coherent_exhibit", .type ["boolean"]),
        ("budget", ref "common.json#/$defs/nat"),
        ("targets", ref "common.json#/$defs/strings"),
        ("conditional_on", ref "#/$defs/coherence_labels"),
        ("detail", ref "common.json#/$defs/text")],
      .ite (props [("verdict", constS "UNKNOWN")]) (.required ["detail"]) (.not (.required ["detail"]))]

def «row» : Shape :=
  .select [
    (ref "#/$defs/soft_path", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "#/$defs/error",
      .select [
        (ref "#/$defs/kind/admission", ref "#/$defs/admission"),
        (ref "#/$defs/kind/soft-rule", ref "#/$defs/rule"),
        (ref "#/$defs/kind/soft-elaborate", ref "#/$defs/elaborate"),
        (ref "#/$defs/kind/soft-pairs", ref "#/$defs/pairs"),
        (ref "#/$defs/kind/soft-certificate", ref "#/$defs/certificate"),
        (.allOf [ref "#/$defs/kind/soft-conflict", .required ["witness"]], ref "#/$defs/witness"),
        (ref "#/$defs/kind/soft-conflict", ref "#/$defs/packages")]]),
    ((.bool true), ref "norms.json#/row")]

def file : File where
  name := "soft-norms.json"
  comment := some "Mode soft-norms: SoftNorms.Run.runCaseReported (formerly ve_soft_norms_route). A case on the soft path (SoftNorms.Run.usesSoftPath) is answered by the soft runner (runCase: admission, else runSoftKind); every other case is delegated unchanged to the norms mode's runner."
  top := [("row", «row»)]
  defs := [
    ("soft_path", .schema soft_path),
    ("soft_field", .schema soft_field),
    ("kind", kind),
    ("error", .schema error),
    ("coherence_labels", .schema coherence_labels),
    ("rule", .schema rule),
    ("admission", .schema admission),
    ("background", .schema background),
    ("soft_residual", .schema (n [obj,
      .required ["default_exceptions", "instruction_switches", "holistic_overrides", "weighing_points"],
      closed [
        ("default_exceptions", ref "common.json#/$defs/nat"),
        ("instruction_switches", ref "common.json#/$defs/nat"),
        ("holistic_overrides", ref "common.json#/$defs/nat"),
        ("weighing_points", ref "common.json#/$defs/nat")]])),
    ("elaborated", elaborated),
    ("elaborate", .schema elaborate),
    ("pairs", .schema pairs),
    ("certificate", .schema certificate),
    ("witness", .schema witness),
    ("packages", .schema packages)]

end ResponseShape.Schemas.SoftNorms
