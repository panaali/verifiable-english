use serde_json::Value;
use ve_core::{evaluate_formula, Document, Environment, FiniteModel};

#[test]
fn replay_untrusted_soft_elaborations() {
    // Python and Lean independently regenerate every source in this corpus.
    // Rust decodes the resulting E' and T' as untrusted ordinary VE inputs,
    // validates their types, then evaluates every layer and soft premise.
    let cases: Value = serde_json::from_slice(include_bytes!(
        "../../../conformance/soft_norms_rust.json"
    ))
    .unwrap();
    assert_eq!(cases.as_array().unwrap().len(), 24);
    for case in cases.as_array().unwrap() {
        let name = case["id"].as_str().unwrap();
        assert_eq!(case["untrusted"], Value::Bool(true), "{name} source trust flag");
        let environment = Environment::from_value(&case["environment"]).unwrap();
        let document = Document::from_value(&environment, &case["formulas"]).unwrap();
        let model = FiniteModel::from_value(&environment, &case["model"]).unwrap();
        let mut verdicts = Vec::new();
        for (index, expected) in case["expected"].as_array().unwrap().iter().enumerate() {
            let actual = evaluate_formula(&document, index, &model, 1_000_000).unwrap();
            assert_eq!(Value::Bool(actual.value.unwrap()), *expected, "{name} formula {index}");
            verdicts.push(actual.value.unwrap());
        }
        let start = case["target_start"].as_u64().unwrap() as usize;
        let conflict = verdicts[start..].iter().any(|value| *value);
        assert_eq!(conflict, case["conflict"].as_bool().unwrap(), "{name} conflict verdict");
    }
}
