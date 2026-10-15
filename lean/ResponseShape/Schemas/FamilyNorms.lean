import ResponseShape
import ResponseShape.Schemas.Norms

/-! The source of `ve/backends/lean_service_schema/family-norms.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.FamilyNorms
open Lean ResponseShape

/-- Generated core and order formulas may be deeper than the input decoder's
64-node nesting bound. The Lean encoder theorem supplies their grammar; this
shape checks the whole wire type before Python sees a row. -/
def familyTerm : Shape :=
  .tagged [
    ("var", [ref "common.json#/$defs/nat"]), ("const", [str]),
    ("num", [ref "common.json#/$defs/integer_text"]),
    ("add", [ref "#/$defs/familyTerm", ref "#/$defs/familyTerm"]),
    ("scale", [ref "common.json#/$defs/integer_text", ref "#/$defs/familyTerm"])]

def familyEdge : Shape :=
  .tagged [
    ("named", [str]),
    ("body", [str, ref "#/$defs/familyFormula"])]

def familyFormula : Shape :=
  .tagged [
    ("top", []), ("bottom", []),
    ("unary", [str, ref "#/$defs/familyTerm"]),
    ("binary", [str, ref "#/$defs/familyTerm", ref "#/$defs/familyTerm"]),
    ("atom", [str, n [arr, .items (ref "#/$defs/familyTerm")]]),
    ("eq", [ref "#/$defs/familyTerm", ref "#/$defs/familyTerm"]),
    ("lt", [ref "#/$defs/familyTerm", ref "#/$defs/familyTerm"]),
    ("le", [ref "#/$defs/familyTerm", ref "#/$defs/familyTerm"]),
    ("not", [ref "#/$defs/familyFormula"]),
    ("and", [ref "#/$defs/familyFormula", ref "#/$defs/familyFormula"]),
    ("or", [ref "#/$defs/familyFormula", ref "#/$defs/familyFormula"]),
    ("implies", [ref "#/$defs/familyFormula", ref "#/$defs/familyFormula"]),
    ("forall", [str, ref "#/$defs/familyFormula"]),
    ("exists", [str, ref "#/$defs/familyFormula"]),
    ("reach", [enumS ["star", "plus"], ref "#/$defs/familyEdge",
      ref "#/$defs/familyTerm", ref "#/$defs/familyTerm"]) ]

def elaborate : Shape :=
  ResponseShape.Schemas.Norms.elaborateWith (ref "#/$defs/familyFormula")

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    ref "common.json#/$defs/error",
    .select [
      (ref "norms.json#/$defs/kind/norms-elaborate", ref "#/$defs/elaborate"),
      (ref "norms.json#/$defs/kind/norms-certificate", ref "norms.json#/$defs/norms-certificate"),
      (.allOf [ref "norms.json#/$defs/kind/norms-conflict", .required ["witness"]], ref "norms.json#/$defs/norms-witness"),
      (ref "norms.json#/$defs/kind/norms-conflict", ref "norms.json#/$defs/norms-conflict"),
      ((.bool true), (.bool false))]]

def file : File where
  name := "family-norms.json"
  comment := some "Mode family-norms: Service.FamilyNorms.runCase, with typed generated core and order formulas."
  top := [("row", «row»)]
  defs := [("familyTerm", .schema familyTerm), ("familyEdge", .schema familyEdge),
    ("familyFormula", .schema familyFormula), ("elaborate", .schema elaborate)]

end ResponseShape.Schemas.FamilyNorms
