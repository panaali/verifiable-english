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
      ("kind", .anyOf [ref "common.json#/$defs/kind",
        c "Service.Document.RightsKind: a rights source unit's kind under rights@0." [
          enumS VE.Service.Document.RightsKind.names]]),
      ("meaning", ref "#/$defs/meaning"),
      ("support", c "Discourse.Loader.supports." [enumS VE.Discourse.Loader.supports]),
      ("status", c "Discourse.Loader.statuses: the unit's W2 status." [enumS VE.Discourse.Loader.statuses]),
      ("parent_id", ref "common.json#/$defs/token"), ("content", .anyOf [
        ref "common.json#/$defs/generated_formula",
        n [obj, .required ["norm"], closed [("norm", ref "common.json#/$defs/norm_node")]],
        copied "Service.Document.UnitContent.rights: a rights block of the document's rights source, as written (authored nulls included); the client binds it to the unit's content" <|
          ref "#/$defs/rights_block",
        copied "Service.Document.softCanonical: the unit's soft norm as the single-rule check decoded it, each soft field away from its default and the unit's cites; the client binds every member but the formulas to the unit's content" <|
          ref "#/$defs/soft_content"]),
      ("meaning_id", ref "common.json#/$defs/hex64")]]

/-- An optional member, which the soft and rights routes read as absent when it is `null` (`wireJson`); a required
member is never `null` in an accepted answer, since the decoders refuse it absent. -/
def nullable (s : Shape) : Shape := .anyOf [.type ["null"], s]

def soft_exception : Shape :=
  c "SoftNorms.Phases.exceptionFields: a default rule's exception as written." [
    obj, .required ["sufficient", "necessary", "factors"],
    closed [("decided_by", .type ["string", "null"]),
      ("sufficient", ref "common.json#/$defs/generated_formulas"),
      ("necessary", ref "common.json#/$defs/generated_formulas"),
      ("factors", ref "common.json#/$defs/strings")]]

/-- An authored soft norm object (`SoftNorms.Phases.ruleFields`); a fan-out line's norm may leave its predicate
absent or `null` (`Rights.Wire.decodeLineNorm`). -/
def soft_norm : Shape :=
  c "SoftNorms.Phases.ruleFields: a soft norm object as written." [
    obj, .required ["name", "sign", "guard", "unless", "over"],
    closed [("name", str), ("predicate", .type ["string", "null"]), ("sign", .type ["boolean"]),
      ("guard", ref "common.json#/$defs/generated_formula"),
      ("unless", ref "common.json#/$defs/generated_formulas"), ("over", ref "common.json#/$defs/strings"),
      ("mode", .enum [.null, .str "strict", .str "default"]), ("rank", .type ["string", "null"]),
      ("alterable", nullable (ref "common.json#/$defs/strings")),
      ("exception", nullable (ref "#/$defs/soft_exception")), ("hard", .type ["boolean", "null"])]]

def cites : Shape :=
  c "Rights.Wire.decodeCites: each citation key with the unit ids it cites (a null one is absent)." [
    obj, .object [] (some (nullable (n [arr, .minItems 1, .items str])))]

/-- `Service.Document.softCanonical`'s object: the W1 core re-encoded, the soft fields away from their defaults. -/
def soft_content : Shape :=
  n [obj, .required ["norm"],
    closed [
      ("norm", n [obj, .required ["name", "predicate", "sign", "guard", "unless", "over"],
        closed [("name", str), ("predicate", str), ("sign", .type ["boolean"]),
          ("guard", ref "common.json#/$defs/generated_formula"),
          ("unless", ref "common.json#/$defs/generated_formulas"), ("over", ref "common.json#/$defs/strings"),
          ("mode", constS "default"), ("rank", str), ("alterable", n [arr, .minItems 1, .items str]),
          ("exception", ref "#/$defs/soft_exception"), ("hard", .const (.bool true))]]),
      ("cites", nullable (ref "#/$defs/cites"))]]

def rights_line : Shape :=
  c "Rights.Wire.decodeLine: a line of a right as written." [
    obj, .required ["kind"],
    closed [("kind", enumS ["claim", "liberty", "immunity", "power"]),
      ("norm", nullable (ref "#/$defs/soft_norm")), ("liberty", nullable (ref "#/$defs/soft_norm")),
      ("recognition", nullable (ref "#/$defs/soft_norm")),
      ("fan_out", nullable (n [obj, .object [] (some (.type ["string", "null"]))])),
      ("holder_slot", nullable (ref "common.json#/$defs/nat")), ("cites", nullable (ref "#/$defs/cites"))]]

def rights_condition : Shape :=
  c "Rights.Wire.decodeCondition: a limitation's condition as written. The decoder ignores purposes; copied content binds its arbitrary JSON value to the request." [
    obj, .required ["name", "role", "verbalisation"],
    closed [("name", str), ("role", enumS ["necessary", "sufficient"]), ("verbalisation", str),
      ("decided_by", .type ["string", "null"]), ("purposes", n [])]]

/-- A rights block (`Rights.Wire.addUnit`): one of `right`, `right_lines`, `limitation` and `bar`, as written. -/
def rights_block : Shape :=
  c "Rights.Wire.addUnit: a rights source unit's block as written." [
    .anyOf [
      n [obj, .required ["right"], closed [("right", n [obj, .required ["name", "holder", "lines"],
        closed [("name", str), ("holder", str), ("guard", nullable (ref "common.json#/$defs/generated_formula")),
          ("lines", n [arr, .items (ref "#/$defs/rights_line")])]])]],
      n [obj, .required ["right_lines"], closed [("right_lines", n [obj, .required ["right", "lines"],
        closed [("right", str), ("lines", n [arr, .items (ref "#/$defs/rights_line")])]])]],
      n [obj, .required ["limitation"], closed [("limitation", n [obj,
        .required ["name", "scope", "kinds", "conditions", "factors"],
        closed [("name", str), ("scope", .anyOf [constS "all", ref "common.json#/$defs/strings"]),
          ("kinds", .anyOf [constS "all", n [arr, .items (enumS ["claim", "liberty", "immunity", "power"])]]),
          ("decided_by", .type ["string", "null"]),
          ("conditions", n [arr, .items (ref "#/$defs/rights_condition")]),
          ("factors", ref "common.json#/$defs/strings")]])]],
      n [obj, .required ["bar"], closed [("bar", n [obj, .required ["name", "reading"],
        closed [("name", str), ("reading", enumS ["rule", "query"]), ("decided_by", .type ["string", "null"])]])]]]]

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

/-- A rejected case with no location: the request's id, the message. -/
def plain_error : Shape :=
  n [obj, .required ["id", "status", "error"],
    closed [("id", .echo "/id"), ("status", constS "error"), ("error", ref "common.json#/$defs/text")]]

/-- A distinguishing model's located diagnostic (`Service.Document.locatedModel`, batch 16f): the `model` mode's text
and its non-empty JSON pointer into the model, which the receiver binds to a member of a model the document
supplies. -/
def model_error : Shape :=
  n [obj, .required ["id", "status", "error", "path"],
    closed [("id", .echo "/id"), ("status", constS "error"), ("error", ref "common.json#/$defs/text"),
      ("path", ref "common.json#/$defs/text")]]

/-- A strict fence's located diagnostic (`Service.Document.locatedFence`, batch 16f): the `parse` mode's text and its
span in the fence's text, which the receiver binds to a strict fence of the document sent. -/
def fence_error : Shape :=
  n [obj, .required ["id", "status", "error", "span"],
    closed [("id", n [str, .equals "/id"]), ("status", constS "error"),
      ("error", ref "common.json#/$defs/text"),
      ("span", n [obj, .required ["start", "end", "line", "column"],
        closed [("start", ref "common.json#/$defs/nat"),
          ("end", ref "common.json#/$defs/nat"),
          ("line", ref "common.json#/$defs/nat"),
          ("column", ref "common.json#/$defs/nat")]])]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "#/$defs/plain_error",
    ref "#/$defs/model_error",
    ref "#/$defs/fence_error",
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
  defs := [("plain_error", .schema plain_error), ("model_error", .schema model_error),
    ("fence_error", .schema fence_error), ("unit", .schema unit), ("meaning", .schema meaning), ("narrowing", .schema narrowing), ("coverage", .schema coverage), ("cells", .schema cells),
    ("block_coverage", .schema blockCoverage), ("soft_exception", .schema soft_exception),
    ("soft_norm", .schema soft_norm), ("cites", .schema cites), ("soft_content", .schema soft_content),
    ("rights_line", .schema rights_line), ("rights_condition", .schema rights_condition),
    ("rights_block", .schema rights_block)]

end ResponseShape.Schemas.Document
