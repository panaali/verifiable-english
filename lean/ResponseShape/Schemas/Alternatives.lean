import VE.Service.Protocol
import ResponseShape

/-! The source of `ve/backends/lean_service_schema/alternatives.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.Alternatives
open Lean ResponseShape

def alt_path : Shape :=
  decidedBy "Alternatives.Run.usesAltPath" VE.Alternatives.Run.usesAltPath <|
  c
    "Alternatives.Run.usesAltPath: the alternatives@0 profile, the environment's alternatives block or an alt-* kind."
    [
      obj,
      .anyOf [
        n [
          .required ["environment"],
          props [
            ("environment", n [
              obj,
              .required ["profiles"],
              props [("profiles", n [arr, .contains (constS "alternatives@0")])]])]],
        n [.required ["environment"], props [("environment", n [obj, .required ["alternatives"]])]],
        n [.required ["kind"], props [("kind", n [str, .pattern (Re.prefixes ["alt-"])])]]]]

def kind : Def :=
  .group none [
    ("admission", kindIs "admission"),
    ("alt-elaborate", kindIs "alt-elaborate"),
    ("alt-validate", kindIs "alt-validate"),
    ("alt-conflict", kindIs "alt-conflict"),
    ("alt-followable", kindIs "alt-followable"),
    ("alt-certificate", kindIs "alt-certificate")]

def alt_labels : Shape :=
  c "Alternatives.Background.altPremiseLabels." [
    arr,
    .items (enumS [
        "alternatives:own",
        "alternatives:one_taken",
        "alternatives:one_inaction",
        "alternatives:proximate"])]

def admission : Shape :=
  c "Alternatives.Run.encodeAdmitted: W2's admission answer and the source labels it is conditional on." [
    obj,
    .required ["id", "status", "admitted", "report", "report_id", "kinds", "conditional_on"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("admitted", .const (.bool true)),
      ("report", ref "common.json#/$defs/bound_report"),
      ("report_id", ref "common.json#/$defs/hex64"),
      ("kinds", n [arr, .items (ref "common.json#/$defs/kind"), .equals "/document/units/*/kind"]),
      ("conditional_on", ref "common.json#/$defs/strings")]]

def regenerated : Def :=
  .group (some "Alternatives.Wire.regenerated before the norms fields: the fields risk-elaborate repeats.") [
    ("inlined", n [
      arr,
      .items (n [obj, .required ["norm"], closed [("norm", ref "common.json#/$defs/norm_node")]])]),
    ("alternatives", n [
      arr,
      .items (n [
          ref "common.json#/$defs/labelled",
          props [
            ("label", enumS [
              "alternatives:own",
              "alternatives:one_taken",
              "alternatives:one_inaction",
              "alternatives:proximate"])]])]),
    ("followable", n [
      obj,
      .required ["ast", "followable", "clear"],
      closed [
        ("ast", ref "common.json#/$defs/generated_formula"),
        ("followable", ref "common.json#/$defs/generated_formula"),
        ("clear", ref "common.json#/$defs/generated_formula")]]),
    ("unmapped_obligations", n [
      arr,
      .items (n [obj, .required ["obligation", "act"], closed [("obligation", str), ("act", str)]])])]

def elaborate : Shape :=
  c
    "Alternatives.Wire.regenerated: the legend, the inlined tree, the alternatives premises, the base premises, the followability formulas, the profile words' existential probes, the unmapped obligations, then Norms.Wire.regenerated of the inlined tree."
    [
      obj,
      .required ["id", "status", "legend", "inlined", "alternatives", "base_premises", "followable", "profile_exists", "unmapped_obligations", "order", "background", "premises", "conflict_targets", "fragment"],
      closed [
        ("id", ref "common.json#/$defs/id_ok"),
        ("status", constS "ok"),
        ("legend", ref "common.json#/$defs/nonempty_strings"),
        ("inlined", ref "#/$defs/regenerated/inlined"),
        ("alternatives", ref "#/$defs/regenerated/alternatives"),
        ("base_premises", ref "common.json#/$defs/labelled_list"),
        ("followable", ref "#/$defs/regenerated/followable"),
        ("profile_exists", n [
          obj,
          .required ["avoidable", "unavoidable", "allows", "prevents"],
          closed [
            ("avoidable", ref "common.json#/$defs/generated_formula"),
            ("unavoidable", ref "common.json#/$defs/generated_formula"),
            ("allows", ref "common.json#/$defs/generated_formula"),
            ("prevents", ref "common.json#/$defs/generated_formula")]]),
        ("unmapped_obligations", ref "#/$defs/regenerated/unmapped_obligations"),
        ("order", ref "common.json#/$defs/strings"),
        ("background", ref "common.json#/$defs/norms_background"),
        ("premises", ref "common.json#/$defs/layer_premises"),
        ("conflict_targets", ref "common.json#/$defs/conflict_targets"),
        ("fragment", .type ["boolean"]),
        ("coverage", ref "#/$defs/coverage")]]

def coverage : Shape :=
  c "Alternatives.Wire.coverage: accepted unit cells and their Lean-owned residual fold." [
    obj,
    .required ["alternatives", "residual"],
    .allOf [
      .countWhere "/alternatives/alternatives_declared" (.bool true) "/residual/alternatives_declared",
      .countWhere "/alternatives/counterfactual_leaves" (.bool true) "/residual/counterfactual_leaves",
      .countWhere "/alternatives/assumed_harm_free" (.bool true) "/residual/assumed_harm_free",
      .countWhere "/alternatives/proximate_judgments" (.bool true) "/residual/proximate_judgments",
      .countWhere "/alternatives/unmapped_obligations" (.bool true) "/residual/unmapped_obligations",
      .countWhere "/alternatives/dilemmas" (.bool true) "/residual/dilemmas",
      .countWhere "/alternatives/narrowings" (.bool true) "/residual/narrowings",
      .references "/alternatives/alternatives_declared" "unit" "/coverage_units/*/id",
      .references "/alternatives/counterfactual_leaves" "unit" "/coverage_units/*/id",
      .references "/alternatives/proximate_judgments" "unit" "/coverage_units/*/id",
      .presenceCount "/alternatives/table_complete" "/residual/table_complete"],
    closed [
      ("alternatives", n [obj,
        .required ["alternatives_declared", "counterfactual_leaves", "assumed_harm_free",
          "table_complete", "proximate_judgments", "unmapped_obligations", "dilemmas", "narrowings"],
        closed [
          ("alternatives_declared", arr),
          ("counterfactual_leaves", arr),
          ("assumed_harm_free", arr),
          ("table_complete", .anyOf [.type ["null"], n [obj,
            .required ["decider", "premise"],
            closed [("decider", str), ("premise", str)]]]),
          ("proximate_judgments", arr),
          ("unmapped_obligations", ref "common.json#/$defs/strings"),
          ("dilemmas", n [arr, .maxItems 0]),
          ("narrowings", arr)]]),
      ("residual", n [obj,
        .required ["alternatives_declared", "counterfactual_leaves", "assumed_harm_free",
          "table_complete", "proximate_judgments", "unmapped_obligations", "dilemmas", "narrowings"],
        closed [
          ("alternatives_declared", ref "common.json#/$defs/nat"),
          ("counterfactual_leaves", ref "common.json#/$defs/nat"),
          ("assumed_harm_free", ref "common.json#/$defs/nat"),
          ("table_complete", ref "common.json#/$defs/nat"),
          ("proximate_judgments", ref "common.json#/$defs/nat"),
          ("unmapped_obligations", ref "common.json#/$defs/nat"),
          ("dilemmas", ref "common.json#/$defs/nat"),
          ("narrowings", ref "common.json#/$defs/nat")]])]]

def chooser : Shape :=
  c "Alternatives.Run.chooserReport: violations and breaches exactly when the block names a taken predicate." [
    obj,
    .required ["chooser", "alternatives", "inaction", "permitted", "required", "avoidable", "unavoidable", "allows", "prevents", "clear", "text"],
    closed [
      ("chooser", str),
      ("alternatives", ref "common.json#/$defs/strings"),
      ("inaction", ref "common.json#/$defs/strings"),
      ("permitted", ref "common.json#/$defs/strings"),
      ("required", ref "common.json#/$defs/strings"),
      ("avoidable", ref "common.json#/$defs/strings"),
      ("unavoidable", ref "common.json#/$defs/strings"),
      ("allows", n [arr, .items (ref "common.json#/$defs/string_pair")]),
      ("prevents", n [arr, .items (ref "common.json#/$defs/string_pair")]),
      ("clear", ref "common.json#/$defs/strings"),
      ("text", ref "common.json#/$defs/text"),
      ("violations", n [
        arr,
        .items (.anyOf [
            str,
            n [
              obj,
              .required ["obligation", "arguments"],
              closed [("obligation", str), ("arguments", ref "common.json#/$defs/strings")]]])]),
      ("breaches", ref "common.json#/$defs/strings")],
    .ite
      (.onCase (n [
          .required ["environment"],
          props [
            ("environment", n [
              obj,
              .required ["alternatives"],
              props [("alternatives", n [obj, .required ["taken"]])]])]]))
      (.required ["violations", "breaches"])
      (.not (.anyOf [.required ["violations"], .required ["breaches"]]))]

def validate : Shape :=
  c "Alternatives.Run.runValidate: a CONFLICT on the scenario, or the per-chooser evaluation." [
    .anyOf [
      n [
        obj,
        .required ["id", "status", "verdict", "target", "tuple", "model_id", "environment_id", "document_hash", "text"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("verdict", constS "CONFLICT"),
          ("target", str),
          ("tuple", ref "common.json#/$defs/strings"),
          ("model_id", ref "common.json#/$defs/hex64_or_empty"),
          ("environment_id", ref "common.json#/$defs/hex64"),
          ("document_hash", ref "common.json#/$defs/hex64"),
          ("text", ref "common.json#/$defs/text")]],
      n [
        obj,
        .required ["id", "status", "model_id", "environment_id", "document_hash", "choosers", "assumed_harm_free", "unmapped_obligations", "conditional_on", "text"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("model_id", ref "common.json#/$defs/hex64_or_empty"),
          ("environment_id", ref "common.json#/$defs/hex64"),
          ("document_hash", ref "common.json#/$defs/hex64"),
          ("choosers", n [arr, .items (ref "#/$defs/chooser")]),
          ("assumed_harm_free", ref "common.json#/$defs/strings"),
          ("unmapped_obligations", ref "common.json#/$defs/text"),
          ("conditional_on", n [arr, .items (constS "alternatives:table_complete"), .maxItems 1]),
          ("text", ref "common.json#/$defs/text")]]]]

def conflict_witness : Shape :=
  c "Alternatives.Run.runConflictWitness: the requested target (no target list)." [
    obj,
    .required ["id", "status", "verdict", "target"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("verdict", enumS ["CONFLICT", "UNKNOWN"]),
      ("target", n [str, .equals "/witness/target"])]]

def followable_witness : Shape :=
  c "Alternatives.Run.runFollowable with a dilemma witness." [
    .anyOf [
      n [
        obj,
        .required ["id", "status", "verdict", "text"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("verdict", enumS ["not computed", "UNKNOWN"]),
          ("text", ref "common.json#/$defs/text")]],
      n [
        obj,
        .required ["id", "status", "verdict", "chooser", "diagnosis", "text"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("verdict", constS "DILEMMA"),
          ("chooser", n [str, .equals "/witness/chooser"]),
          ("diagnosis", ref "common.json#/$defs/text"),
          ("text", ref "common.json#/$defs/text")]]]]

def followable : Shape :=
  c "Alternatives.Run.runFollowable over a certificate package." [
    .anyOf [
      n [
        obj,
        .required ["id", "status", "verdict", "text"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("verdict", enumS ["not computed", "UNKNOWN"]),
          ("text", ref "common.json#/$defs/text")]],
      n [
        obj,
        .required ["id", "status", "verdict", "conditional_on", "text"],
        closed [
          ("id", ref "common.json#/$defs/id_ok"),
          ("status", constS "ok"),
          ("verdict", constS "FOLLOWABLE"),
          ("conditional_on", ref "common.json#/$defs/strings"),
          ("text", n [str, .pattern (Re.prefixes ["FOLLOWABLE: "])])]]]]

def certificate : Shape :=
  c "Alternatives.Run.runCase alt-certificate." [
    obj,
    .required ["id", "status", "valid", "background", "layers", "conditional_on"],
    closed [
      ("id", ref "common.json#/$defs/id_ok"),
      ("status", constS "ok"),
      ("valid", .type ["boolean"]),
      ("background", ref "common.json#/$defs/nat"),
      ("layers", ref "common.json#/$defs/nat"),
      ("conditional_on", ref "#/$defs/alt_labels")]]

def «row» : Shape :=
  .select [
    (ref "#/$defs/alt_path", .anyOf [
      ref "common.json#/$defs/case_error",
      ref "common.json#/$defs/route_path_error",
      .select [
        (ref "#/$defs/kind/admission", ref "#/$defs/admission"),
        (ref "#/$defs/kind/alt-elaborate", ref "#/$defs/elaborate"),
        (ref "#/$defs/kind/alt-validate", ref "#/$defs/validate"),
        (.allOf [ref "#/$defs/kind/alt-conflict", .required ["witness"]], ref "#/$defs/conflict_witness"),
        (ref "#/$defs/kind/alt-conflict", ref "common.json#/$defs/packages_conflict"),
        (.allOf [ref "#/$defs/kind/alt-followable", .required ["witness"]], ref "#/$defs/followable_witness"),
        (ref "#/$defs/kind/alt-followable", ref "#/$defs/followable"),
        (ref "#/$defs/kind/alt-certificate", ref "#/$defs/certificate")]]),
    ((.bool true), ref "norms.json#/row")]

def file : File where
  name := "alternatives.json"
  comment := some "Mode alternatives: Alternatives.Run.runCaseReported (formerly ve_alternatives_route). A case on the alternatives path (usesAltPath) is answered by the alternatives runner; every other case is delegated unchanged to the norms mode's runner."
  top := [("row", «row»)]
  defs := [
    ("alt_path", .schema alt_path),
    ("kind", kind),
    ("alt_labels", .schema alt_labels),
    ("admission", .schema admission),
    ("regenerated", regenerated),
    ("elaborate", .schema elaborate),
    ("coverage", .schema coverage),
    ("chooser", .schema chooser),
    ("validate", .schema validate),
    ("conflict_witness", .schema conflict_witness),
    ("followable_witness", .schema followable_witness),
    ("followable", .schema followable),
    ("certificate", .schema certificate)]

end ResponseShape.Schemas.Alternatives
