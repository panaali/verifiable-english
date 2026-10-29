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

#[test]
fn predicate_signature_and_constant_fault_order() {
    let mut case = json!({
        "language": "ve.core@0.2", "profiles": ["relational-fol@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {
            "sorts": {}, "predicates": {"dept": {"arguments": ["$string"], "description": "d"}},
            "constants": {"legal": []}
        }
    });
    let error = Environment::from_value(&case).unwrap_err();
    assert_eq!(error.code, "InvalidInput");
    case["vocabulary"]["constants"]["legal"] = json!({"sort": "other", "description": "d"});
    case["vocabulary"]["predicates"]["dept"]["arguments"] = json!(["missing"]);
    let error = Environment::from_value(&case).unwrap_err();
    assert_eq!(error.code, "UnknownSymbol");
    case["vocabulary"]["constants"]["legal"] = json!("x");
    let error = Environment::from_value(&case).unwrap_err();
    assert_eq!(error.code, "UnknownSymbol");
}

#[test]
fn legacy_undeclared_builtin_sorts_are_unknown_symbols() {
    for sort in ["$int", "$string", "missing"] {
        let case = json!({
            "language": "ve.core@0", "profile": "relational-fol@0",
            "spec_revision": "ve-v0-draft-2026-09-20",
            "vocabulary": {"sorts": {}, "predicates": {
                "p": {"arguments": [sort], "description": "d"}}, "constants": {}}
        });
        let error = Environment::from_value(&case).unwrap_err();
        assert_eq!(error.code, "UnknownSymbol", "{sort}");
    }
    let valid = json!({
        "language": "ve.core@0", "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {"sorts": {"person": {"description": "d"}},
            "predicates": {"p": {"arguments": ["person"], "description": "d"}}, "constants": {}}
    });
    assert!(Environment::from_value(&valid).is_ok());
}

#[test]
fn composed_order_rejects_string_predicate_sort_before_constants() {
    for profiles in [
        json!(["order@0", "relational-fol@0"]),
        json!(["order@0", "relational-fol@0", "time@0"]),
        json!(["data@0", "order@0", "relational-fol@0"]),
    ] {
        let mut case = json!({
            "language": "ve.core@0.2", "profiles": profiles,
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {}, "predicates": {
                "p": {"arguments": ["$string"], "description": "d"}}, "constants": {}}
        });
        assert_eq!(Environment::from_value(&case).unwrap_err().code, "UnknownSymbol");
        case["vocabulary"]["constants"]["bad"] = json!([]);
        let expected = if profiles.as_array().unwrap().len() == 2 {
            "InvalidInput"
        } else {
            "UnknownSymbol"
        };
        assert_eq!(Environment::from_value(&case).unwrap_err().code, expected);
        case["vocabulary"]["constants"] = json!({});
        case["vocabulary"]["predicates"]["p"]["arguments"] = json!(["$int"]);
        assert!(Environment::from_value(&case).is_ok());
    }
}
