import ResponseShape

/-! The source of `ve/backends/lean_service_schema/risk-eval.json` (`file`; `tools/response_schemas.py` writes it). -/
namespace ResponseShape.Schemas.RiskEval
open Lean ResponseShape

def result : Shape :=
  c
    "Risk.Eval.evalCondition: the condition's diagnostic, or whether it is possible and certain over the quantities' box with a witness valuation (an integer per quantity) exactly when possible."
    [
      .anyOf [
        n [obj, .required ["error"], closed [("error", ref "common.json#/$defs/text")]],
        n [
          obj,
          .required ["possible", "certain", "witness"],
          closed [
            ("possible", .type ["boolean"]),
            ("certain", .type ["boolean"]),
            ("witness", .anyOf [.const .null, n [obj, .object [] (some (.type ["integer"]))]])],
          .ite (props [("possible", .const (.bool true))]) (props [("witness", obj)]) (props [
              ("witness", .const .null)])]]]

def «row» : Shape :=
  .anyOf [
    ref "common.json#/$defs/case_error",
    n [
      obj,
      .required ["status", "error"],
      closed [("status", constS "error"), ("error", ref "common.json#/$defs/text")]],
    n [
      obj,
      .required ["status", "results"],
      closed [
        ("status", constS "ok"),
        ("results", n [arr, .length "/conditions", .items (ref "#/$defs/result")])]]]

def file : File where
  name := "risk-eval.json"
  comment := some "Mode risk-eval: Risk.Eval.runCaseReported, the test-only differential harness of docs/spec/risk.md 8.3 (ve_risk_eval). Its rows carry no id; the binding is the case digest."
  top := [("row", «row»)]
  defs := [
    ("result", .schema result)]

end ResponseShape.Schemas.RiskEval
