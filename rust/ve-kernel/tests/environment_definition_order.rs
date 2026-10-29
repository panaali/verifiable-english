#![forbid(unsafe_code)]

use serde_json::json;
use ve_kernel::Environment;

fn environment(body: serde_json::Value) -> serde_json::Value {
    json!({
        "language": "ve.core@0.2",
        "profiles": ["relational-fol@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {
            "sorts": {"person": {"description": "a person"}},
            "predicates": {
                "base": {"arguments": ["person", "person"], "description": "base relation"},
                "above": {"arguments": ["person", "person"], "description": "above relation",
                    "defined": {"arguments": ["person", "person"], "body": body}}
            },
            "constants": {}
        }
    })
}

#[test]
fn malformed_nested_definition_precedes_unsupported_field() {
    let bad = environment(json!(["binary", "base", ["var", 1], ["var", {}]]));
    let error = Environment::from_value(&bad).unwrap_err();
    assert_eq!(error.code, "UnboundVariable");

    let good = environment(json!(["binary", "base", ["var", 1], ["var", 0]]));
    let error = Environment::from_value(&good).unwrap_err();
    assert_eq!(error.code, "InvalidInput");
    assert!(error.message.contains("expected exactly fields"));
}
