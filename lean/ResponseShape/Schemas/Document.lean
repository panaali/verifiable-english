import ResponseShape.Schemas.Alternatives

/-! The checked projection of the W2 wrapper. Content admission is not a field
of this row; the wrapper carries source partition and coverage only. An
`alternatives@0` or `risk@0` document's coverage adds its block route's
`alternatives` cells (`Alternatives.Wire.coverage`), with the cell shapes of
`alternatives.json`; its narrowings are the document's own, not the request's. -/
namespace ResponseShape.Schemas.Document
open Lean ResponseShape

def unit : Shape :=
  n [obj, .required ["id", "span", "kind", "meaning", "support", "status"],
    closed [
      ("id", ref "common.json#/$defs/token"), ("span", n [arr, .prefixItems [ref "common.json#/$defs/nat", ref "common.json#/$defs/nat"], .minItems 2, .maxItems 2]),
      ("kind", ref "common.json#/$defs/kind"), ("meaning", ref "#/$defs/meaning"),
      ("support", c "Discourse.Loader.supports." [enumS VE.Discourse.Loader.supports]),
      ("status", c "Discourse.Loader.statuses: the unit's W2 status." [enumS VE.Discourse.Loader.statuses]),
      ("parent_id", ref "common.json#/$defs/token"), ("content", .anyOf [
        ref "common.json#/$defs/generated_formula",
        n [obj, .required ["norm"], closed [("norm", ref "common.json#/$defs/norm_node")]]]),
      ("meaning_id", ref "common.json#/$defs/hex64")]]

/-- `Service.Document.Meaning.json`: a meaning `Loader.meaningStatus` accepts. -/
def meaning : Shape :=
  c "Discourse.Loader.meaningStatus: specified, or one contextual, open or unformalised member." [
    .anyOf [
      constS "specified",
      n [obj, .required ["contextual"], closed [("contextual", n [str, .minLength 1])]],
      n [obj, .required ["open"], closed [("open", n [arr, .minItems 1, .items str])]],
      n [obj, .required ["unformalised"], closed [("unformalised", ref "common.json#/$defs/token")]]]]

/-- A narrowing of the front matter, which the block route's coverage relays as the document's own
(`Discourse.Loader.narrowingIds` checked it). -/
def narrowing : Shape :=
  c "Discourse.Loader.narrowingIds: a front-matter narrowing, relayed whole." [
    obj, .required ["id", "set", "version", "keeps", "by", "reason_spans"],
    closed [
      ("id", ref "common.json#/$defs/token"), ("set", ref "common.json#/$defs/token"),
      ("version", n [.type ["integer"], .minimum 1]), ("keeps", n [arr, .minItems 1, .items str]),
      ("by", ref "common.json#/$defs/token"), ("reason_spans", n [arr, .minItems 1, .items str])]]

def cells : Shape :=
  c "Alternatives.Wire.coverage's cells, as the document mode relays them." [
    obj,
    .required ["alternatives_declared", "counterfactual_leaves", "assumed_harm_free",
      "table_complete", "proximate_judgments", "unmapped_obligations", "dilemmas", "narrowings"],
    closed [
      ("alternatives_declared", n [arr, .items Alternatives.declaredCell]),
      ("counterfactual_leaves", n [arr, .items Alternatives.counterfactualCell]),
      ("assumed_harm_free", n [arr, .items Alternatives.assumedCell]),
      ("table_complete", .anyOf [.type ["null"], n [obj,
        .required ["decider", "premise"],
        closed [("decider", str), ("premise", constS "alternatives:table_complete")]]]),
      ("proximate_judgments", n [arr, .items Alternatives.proximateCell]),
      ("unmapped_obligations", ref "common.json#/$defs/strings"),
      ("dilemmas", n [arr, .maxItems 0]),
      ("narrowings", copied "the document's front-matter narrowings, copied from the request's document (Loader.optionalList); the client binds them to it" <|
        n [arr, .items (ref "#/$defs/narrowing")])]]

/-- The block route's whole coverage line, of which the row relays the cells (`Fits.getObjVal`). -/
def blockCoverage : Shape :=
  n [obj, .required ["alternatives", "residual"],
    closed [("alternatives", ref "#/$defs/cells"),
      ("residual", n [obj, .object [] (some (ref "common.json#/$defs/nat"))])]]

/-- `coverage(doc)`: the byte tables, the residual counts and a composed block's cells. -/
def coverage : Shape :=
  n [obj,
    .required ["source_bytes", "accounted_bytes", "coverage_percent", "bytes_by_kind",
      "bytes_by_status", "unformalised_reasons", "residual", "residual_total"],
    closed [
      ("source_bytes", ref "common.json#/$defs/nat"),
      ("accounted_bytes", ref "common.json#/$defs/nat"),
      ("coverage_percent", .const (toJson (100 : Nat))),
      ("bytes_by_kind", n [obj, .object [] (some (ref "common.json#/$defs/nat"))]),
      ("bytes_by_status", n [obj, .object [] (some (ref "common.json#/$defs/nat"))]),
      ("unformalised_reasons", n [obj, .object [] (some (ref "common.json#/$defs/nat"))]),
      ("residual", n [obj, .object [] (some (ref "common.json#/$defs/nat"))]),
      ("residual_total", ref "common.json#/$defs/nat"),
      ("alternatives", ref "#/$defs/cells")]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "common.json#/$defs/error",
    n [obj,
      .required ["id", "status", "document_id", "source_id", "source", "units", "coverage"],
      closed [
        ("id", n [str, .equals "/id"]),
        ("status", constS "ok"),
        ("document_id", ref "common.json#/$defs/hex64"),
        ("source_id", ref "common.json#/$defs/hex64"),
        ("source", str),
        ("units", n [arr, .items (ref "#/$defs/unit")]),
        ("coverage", ref "#/$defs/coverage")]]]

def file : File where
  name := "document.json"
  comment := some "Mode document: W2 wrapper byte partition, inferred unit statuses and base coverage."
  top := [("row", «row»)]
  defs := [("unit", .schema unit), ("meaning", .schema meaning), ("narrowing", .schema narrowing), ("coverage", .schema coverage), ("cells", .schema cells),
    ("block_coverage", .schema blockCoverage)]

end ResponseShape.Schemas.Document
