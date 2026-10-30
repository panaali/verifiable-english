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

/// The PROBE envelopes of the built-in argument sort class (usecase-safetyfw-b
/// F12-F14) and their Lean codes; tests/test_difffuzz.py holds the whole table.
#[test]
fn builtin_argument_sort_probes_take_lean_codes() {
    let cell = |head: serde_json::Value, sort: &str, constants: serde_json::Value| {
        let mut case = head;
        case["vocabulary"] = json!({"sorts": {}, "constants": constants,
            "predicates": {"p": {"arguments": [sort], "description": "d"}}});
        Environment::from_value(&case).err().map(|e| e.code)
    };
    let v02 = |profiles: &[&str]| json!({"language": "ve.core@0.2", "profiles": profiles,
        "spec_revision": "ve-v0.2-expand2-2026-09-25"});
    let legacy = json!({"language": "ve.core@0", "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20"});
    let soft = v02(&["norms@0", "order@0", "relational-fol@0", "soft-norms@0"]);
    let undeclared = json!({"c": {"sort": "nosuch", "description": "d"}});
    let cases = [
        // F12: the frozen decoder's unknown sort.
        (cell(legacy.clone(), "$int", json!({})), Some("UnknownSymbol")),
        (cell(legacy, "$string", json!({})), Some("UnknownSymbol")),
        // F13: the exact order list checks the constants first, then the sort.
        (cell(v02(&["order@0", "relational-fol@0"]), "$string", json!({})), Some("UnknownSymbol")),
        (cell(v02(&["order@0", "relational-fol@0"]), "$string", json!({"bad": []})), Some("InvalidInput")),
        (cell(v02(&["order@0", "relational-fol@0", "time@0"]), "$string", json!({"bad": []})),
         Some("UnknownSymbol")),
        // F14: soft-norms@0 decodes its vocabulary without the checker profiles.
        (cell(soft.clone(), "$string", json!({})), Some("InvalidInput")),
        (cell(soft.clone(), "$int", json!({})), Some("InvalidInput")),
        (cell(soft, "$string", undeclared.clone()), Some("InvalidInput")),
        // The exact closure+n-ary list defers its unknown sort; a composed one does not.
        (cell(v02(&["closure@0", "nary@0", "relational-fol@0"]), "$int", json!({})), Some("UnknownSymbol")),
        (cell(v02(&["closure@0", "nary@0", "relational-fol@0", "time@0"]), "$int", undeclared.clone()),
         Some("UnknownSymbol")),
        // The route decoder's constant sort fault.
        (cell(v02(&["definitions@0", "relational-fol@0"]), "$int", undeclared), Some("InvalidInput")),
    ];
    for (i, (got, expected)) in cases.into_iter().enumerate() {
        assert_eq!(got.as_deref(), expected, "case {i}");
    }
}
