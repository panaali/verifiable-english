use serde_json::{json, Value};
use ve_core::{evaluate_formula, Document, Environment, FiniteModel};

#[test]
fn replay_untrusted_norm_defaults_fillings() {
    // Rust never elaborates (norm-defaults 8). Python's filled premise lists
    // arrive as untrusted ordinary VE inputs: over the filled base vocabulary,
    // whose unsaid tables are base tables, the Fill_T premises, the conflict
    // targets and the reached targets; over E''' the layers of `fill U`.
    let cases: Value = serde_json::from_slice(include_bytes!(
        "../../../conformance/norm_defaults_rust.json"
    ))
    .unwrap();
    let rows = cases.as_array().unwrap();
    assert_eq!(rows.len(), 79);
    for case in rows {
        let name = case["id"].as_str().unwrap();
        assert_eq!(case["untrusted"], Value::Bool(true), "{name} source trust flag");
        let environment = Environment::from_value(&case["environment"]).unwrap();
        let document = Document::from_value(&environment, &case["formulas"]).unwrap();
        let model = FiniteModel::from_value(&environment, &case["model"]).unwrap();
        let mut values = Vec::new();
        for (index, expected) in case["expected"].as_array().unwrap().iter().enumerate() {
            let actual = evaluate_formula(&document, index, &model, 1_000_000).unwrap();
            assert_eq!(Value::Bool(actual.value.unwrap()), *expected, "{name} formula {index}");
            values.push(actual.value.unwrap());
        }
        if case["kind"] == "base" {
            // A filling is admissible exactly when every Fill_T premise holds.
            let start = case["target_start"].as_u64().unwrap() as usize;
            let admissible = values[..start].iter().all(|value| *value);
            assert_eq!(admissible, case["admissible"].as_bool().unwrap(), "{name} Fill_T");
        } else {
            // The expansion of an admissible, conflict-free filling satisfies every layer.
            assert!(values.iter().all(|value| *value), "{name} layers");
        }
    }
}

#[test]
fn norm_defaults_profile_is_refused() {
    // The profile is elaborated by Python and checked by Lean; Rust decodes
    // only the filled vocabularies, so an environment that enables it is refused.
    let raw = json!({
        "language": "ve.core@0.2",
        "profiles": ["norm-defaults@0", "norms@0", "relational-fol@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {
            "sorts": {"act": {"description": "act"}},
            "predicates": {
                "permitted": {"arguments": ["act"], "description": "permitted",
                    "regulated": {"role": "permission", "default": "unspecified",
                                  "act": "{0} be done"}}
            },
            "constants": {}
        }
    });
    assert_eq!(Environment::from_value(&raw).unwrap_err().code, "UnsupportedProfile");
    let mut without = raw.clone();
    without["profiles"] = json!(["norms@0", "relational-fol@0"]);
    let error = Environment::from_value(&without).unwrap_err();
    assert_eq!(error.code, "UnsupportedProfile");
    assert_eq!(error.message, "UnsupportedProfile: unspecified completion requires norm-defaults@0");
}
