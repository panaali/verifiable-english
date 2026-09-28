//! The `elaborated-document` family (docs/spec/discourse.md 11). Rust never resolves
//! references: a discourse case carries the elaborated formulas another checker regenerated,
//! marked `untrusted: true`. Rust re-checks them as ordinary closed formulas of the base
//! environment (the profile list without `ve.discourse@1`) and computes their identities and
//! verdicts, which must agree with Python's and Lean's (regression evidence; the trust path is
//! the Lean route).
use crate::{
    CountermodelProblem, Document, Environment, FiniteModel, Formula, MAX_EVALUATIONS, Result,
    SearchBounds, error, evaluate_formula, find_countermodel,
};
use serde_json::{Value, json};

pub const ELABORATED_DOCUMENT: &str = "elaborated-document";

/// Check an `elaborated-document` case: `environment` (the base pair), `formulas` (the
/// elaborated premises, in unit order) and optionally `model` (evaluated formula by formula).
/// The verdicts are the formulas' meaning ids and premise consistency: `model` when a finite
/// model of the premises is found, `UNKNOWN` otherwise (never a proof of inconsistency).
pub fn elaborated_document_case(v: &Value) -> Result<Value> {
    if v.get("family").and_then(Value::as_str) != Some(ELABORATED_DOCUMENT) {
        return error("InvalidInput", "not an elaborated-document case");
    }
    if v.get("untrusted") != Some(&Value::Bool(true)) {
        return error(
            "InvalidInput",
            "elaborated-document formulas are untrusted input: mark the case untrusted",
        );
    }
    let environment = v
        .get("environment")
        .ok_or_else(|| crate::Error::new("InvalidInput", "missing environment"))?;
    if environment
        .get("profiles")
        .and_then(Value::as_array)
        .is_some_and(|ps| ps.contains(&json!("ve.discourse@1")))
    {
        return error(
            "UnsupportedProfile",
            "ve.discourse@1: Rust checks only the elaborated document under the base profiles",
        );
    }
    let env = Environment::from_value(environment)?;
    let formulas = v
        .get("formulas")
        .ok_or_else(|| crate::Error::new("InvalidInput", "missing formulas"))?;
    let doc = Document::from_value(&env, formulas)?;
    let meaning_ids = (0..doc.formulas().len())
        .map(|i| doc.formula_meaning_id(i))
        .collect::<Result<Vec<_>>>()?;
    let problem = CountermodelProblem::new(&env, doc.formulas().to_vec(), Formula::Bottom)?;
    let search = find_countermodel(&env, &problem, SearchBounds::default())?;
    let premises = if search.status == "Found" {
        let model = search
            .model
            .as_ref()
            .expect("a found search carries its model");
        json!({"status": "model", "model_id": model.model_id()})
    } else {
        json!({"status": "UNKNOWN", "search": search.status})
    };
    let mut out = json!({"id": v.get("id").cloned().unwrap_or(json!("")), "status": "ok",
        "family": ELABORATED_DOCUMENT, "untrusted": true, "environment_id": env.environment_id(),
        "formulas": doc.to_value(), "meaning_ids": meaning_ids, "premises": premises});
    if let Some(model) = v.get("model") {
        let model = FiniteModel::from_value(&env, model)?;
        let values = (0..doc.formulas().len())
            .map(|i| {
                evaluate_formula(&doc, i, &model, MAX_EVALUATIONS).and_then(|r| {
                    r.value.ok_or_else(|| {
                        crate::Error::new("ResourceLimit", "evaluation budget exhausted")
                    })
                })
            })
            .collect::<Result<Vec<_>>>()?;
        out["values"] = json!(values);
    }
    Ok(out)
}
