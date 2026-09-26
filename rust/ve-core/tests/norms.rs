use serde_json::json;
use ve_core::{Environment, FiniteModel};

#[test]
fn regulated_environment_and_profile_model() {
    let env_data = json!({
        "language": "ve.core@0.2",
        "profiles": ["norms@0", "relational-fol@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {
            "sorts": {"act": {"description": "act"}},
            "predicates": {
                "required": {"arguments": ["act"], "description": "required",
                    "regulated": {"role": "obligation", "default": "deny",
                                  "act": "{0} be done", "permission": "permitted"}},
                "permitted": {"arguments": ["act"], "description": "permitted",
                    "regulated": {"role": "permission", "default": "deny",
                                  "act": "{0} be done"}}
            },
            "constants": {}
        }
    });
    let env = Environment::from_value(&env_data).unwrap();
    let bad = json!({"complete": true, "domains": {"act": ["a"]},
                     "constants": {}, "relations": {"required": [["a"]], "permitted": []}});
    assert_eq!(FiniteModel::from_value(&env, &bad).unwrap_err().code, "InvalidModel");
    let good = json!({"complete": true, "domains": {"act": ["a"]},
                      "constants": {}, "relations": {"required": [["a"]], "permitted": [["a"]]}});
    assert!(FiniteModel::from_value(&env, &good).is_ok());
    let mut missing_dual = env_data.clone();
    missing_dual["vocabulary"]["predicates"]["required"]["regulated"]
        .as_object_mut().unwrap().remove("permission");
    assert!(Environment::from_value(&missing_dual).unwrap_err().message.contains("MissingPermissionDual"));
}
