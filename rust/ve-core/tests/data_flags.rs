use serde_json::json;
use ve_core::{Environment, FiniteModel};

#[test]
fn data_flags_and_string_slots_are_checked() {
    let env = Environment::from_value(&json!({
        "language": "ve.core@0.2",
        "profiles": ["data@0", "relational-fol@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {
            "sorts": {"person": {"description": "Person"}},
            "predicates": {"department": {"arguments": ["person", "$string"],
                "description": "Department", "functional": true, "total": true}},
            "constants": {"alice": {"sort": "person", "description": "Alice"},
                "finance": {"sort": "$string"}, "sales": {"sort": "$string"}}
        }
    })).unwrap();
    let wire = |rows: serde_json::Value| json!({"complete": true,
        "domains": {"person": ["a"], "$string": ["f", "s"]},
        "constants": {"alice": "a", "finance": "f", "sales": "s"},
        "relations": {"department": rows}});
    assert!(FiniteModel::from_value(&env, &wire(json!([["a", "f"]]))).is_ok());
    for rows in [json!([]), json!([["a", "f"], ["a", "s"]])] {
        assert_eq!(FiniteModel::from_value(&env, &wire(rows)).unwrap_err().code, "InvalidModel");
    }
}
