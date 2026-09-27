use serde_json::json;
use ve_core::{Document, Environment, parse, print_document};

fn environment(arity: usize) -> Environment {
    Environment::from_value(&json!({
        "language": "ve.core@0.2",
        "profiles": ["closure@0", "nary@0", "relational-fol@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {
            "sorts": {"s": {"description": "S"}},
            "predicates": {"p": {"arguments": vec!["s"; arity], "description": "P"}},
            "constants": {"a": {"sort": "s", "description": "A"}}
        }
    })).unwrap()
}

#[test]
fn nary_wire_and_strict_round_trip() {
    for arity in 3..=6 {
        let env = environment(arity);
        let atom = json!(["atom", "p", vec![json!(["const", "a"]); arity]]);
        let doc = Document::from_value(&env, &json!([atom])).unwrap();
        let printed = print_document(&doc).unwrap();
        assert_eq!(printed, format!("p({}).\n", vec!["@a"; arity].join(", ")));
        assert_eq!(parse(&env, printed.as_bytes()).unwrap(), doc);
        assert_eq!(doc.to_value(), json!([atom]));
    }
}

#[test]
fn hostile_nary_wire_is_rejected() {
    let env = environment(3);
    for terms in [json!(["not a list"]), json!(["a", "b"]),
                  json!(vec![json!(["const", "a"]); 7])] {
        assert!(Document::from_value(&env, &json!([["atom", "p", terms]])).is_err());
    }
    assert!(Environment::from_value(&json!({
        "language": "ve.core@0.2",
        "profiles": ["closure@0", "nary@0", "relational-fol@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {"sorts": {"s": {"description": "S"}},
            "predicates": {"p": {"arguments": vec!["s"; 7], "description": "P"}},
            "constants": {}}
    })).is_err());
}
