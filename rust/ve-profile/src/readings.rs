//! Evaluation-only shadow of S1 separation. The formulas and per-reading
//! environments arrive already elaborated; Rust neither builds readings nor
//! decides whether a situation separates them.
use crate::evaluate_formula;
use serde_json::{Value, json};
use ve_kernel::{Document, Environment, Error, FiniteModel, MAX_EVALUATIONS, Result, internal::error};

pub fn readings_evaluate_case(v: &Value) -> Result<Value> {
    if v.get("kind").and_then(Value::as_str) != Some("readings-evaluate") {
        return error("InvalidInput", "not a readings-evaluate case");
    }
    if v.get("untrusted") != Some(&Value::Bool(true)) {
        return error("InvalidInput", "reading formulas are untrusted input: mark the case untrusted");
    }
    let sides = v.get("sides").and_then(Value::as_array)
        .filter(|items| items.len() == 2)
        .ok_or_else(|| Error::new("InvalidInput", "readings-evaluate needs two sides"))?;
    let mut results = Vec::with_capacity(2);
    for side in sides {
        let env = Environment::from_value(side.get("environment")
            .ok_or_else(|| Error::new("InvalidInput", "missing reading environment"))?)?;
        let model = FiniteModel::from_value(&env, side.get("model")
            .ok_or_else(|| Error::new("InvalidInput", "missing reading model"))?)?;
        let mut values = serde_json::Map::new();
        for name in ["premises", "outcomes", "selections", "assertions"] {
            let formulas = side.get(name).and_then(Value::as_array)
                .ok_or_else(|| Error::new("InvalidInput", format!("missing reading {name}")))?;
            if formulas.is_empty() {
                values.insert(name.to_owned(), json!([]));
                continue;
            }
            let doc = Document::from_value(&env, &json!(formulas))?;
            let checked = (0..doc.formulas().len())
                .map(|index| evaluate_formula(&doc, index, &model, MAX_EVALUATIONS)
                    .and_then(|result| result.value.ok_or_else(||
                        Error::new("ResourceLimit", "reading formula evaluation budget exhausted"))))
                .collect::<Result<Vec<_>>>()?;
            values.insert(name.to_owned(), json!(checked));
        }
        results.push(Value::Object(values));
    }
    Ok(json!({"id":v.get("id").cloned().unwrap_or(json!("")),
        "status":"ok", "untrusted":true, "sides":results}))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn evaluates_both_untrusted_readings_without_claiming_separation() {
        let environment = json!({"language":"ve.core@0.2",
            "profiles":["relational-fol@0"],
            "spec_revision":"ve-v0.2-expand2-2026-09-25",
            "vocabulary":{"sorts":{},"predicates":{},"constants":{}}});
        let model = json!({"complete":true,"domains":{},"relations":{},"constants":{}});
        let side = |outcome: Value| json!({"environment":environment,"model":model,
            "premises":[["top"]],"outcomes":[outcome],
            "selections":[["bottom"]],"assertions":[]});
        let input = json!({"kind":"readings-evaluate","untrusted":true,
            "sides":[side(json!(["top"])), side(json!(["bottom"]))]});
        let result = readings_evaluate_case(&input).unwrap();
        assert_eq!(result["untrusted"], true);
        assert_eq!(result["sides"][0]["outcomes"], json!([true]));
        assert_eq!(result["sides"][1]["outcomes"], json!([false]));
        assert!(result.get("separated").is_none());
        let mut unmarked = input.clone();
        unmarked["untrusted"] = json!(false);
        assert!(readings_evaluate_case(&unmarked).is_err());
    }
}
