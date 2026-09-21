#![forbid(unsafe_code)]
use serde_json::json;
use ve_core::*;

#[test]
fn shared_evaluation_corpus() {
    let cases = loads_json(include_bytes!("../../../conformance/evaluation.json")).unwrap();
    let mut count = 0;
    for case in cases.as_array().unwrap() {
        let env = Environment::from_value(&case["environment"]).unwrap();
        let doc = Document::from_value(&env, &case["ast"]).unwrap();
        let model = FiniteModel::from_value(&env, &case["model"]).unwrap();
        let canonical = print_document(&doc);
        assert_eq!(
            canonical,
            case["source"].as_str().unwrap(),
            "{}",
            case["id"]
        );
        assert_eq!(parse(&env, canonical.as_bytes()).unwrap(), doc);
        for (i, expected) in case["expected"].as_array().unwrap().iter().enumerate() {
            let result = evaluate_formula(&doc, i, &model, MAX_EVALUATIONS).unwrap();
            assert_eq!(json!(result.value), *expected, "{} formula {i}", case["id"]);
            count += 1;
        }
    }
    assert_eq!(count, 776);
}

#[test]
fn restricted_json_and_canonical_order() {
    for raw in [
        r#"{"a":1,"\u0061":2}"#,
        r#"{"a":{"b":1,"b":2}}"#,
        r#""\ud800""#,
        "null",
        "1.0",
        "1e0",
        "-1",
        "9007199254740992",
        "01",
        "[true,]",
    ] {
        assert!(loads_json(raw.as_bytes()).is_err(), "{raw}");
    }
    assert_eq!(loads_json(b"-0").unwrap(), json!(0));
    assert_eq!(
        canonical_json(&json!({"\u{e000}":0,"😀":1})).unwrap(),
        "{\"😀\":1,\"\u{e000}\":0}".as_bytes()
    );
    let deep = format!("{}true{}", "[".repeat(257), "]".repeat(257));
    assert_eq!(
        loads_json(deep.as_bytes()).unwrap_err().code,
        "ResourceLimit"
    );
}

#[test]
fn shared_parser_and_identity_fixtures() {
    let parser = loads_json(include_bytes!("../../../conformance/parser.json")).unwrap();
    for case in parser.as_array().unwrap() {
        let env = Environment::from_value(&case["environment"]).unwrap();
        let result = parse(&env, case["source"].as_str().unwrap().as_bytes());
        let expected = &case["expected_parser"];
        if let Some(code) = expected.get("error_code") {
            assert_eq!(
                result.unwrap_err().code,
                code.as_str().unwrap(),
                "{}",
                case["id"]
            );
        } else {
            let doc = result.unwrap();
            assert_eq!(
                print_document(&doc),
                expected["canonical"].as_str().unwrap()
            );
            assert_eq!(doc.to_value(), expected["ast"]);
        }
    }
    let identities = loads_json(include_bytes!("../../../conformance/identity.json")).unwrap();
    for case in identities.as_array().unwrap() {
        let env = Environment::from_value(&case["environment"]).unwrap();
        let doc = Document::from_value(&env, &case["ast"]).unwrap();
        let model = FiniteModel::from_value(&env, &case["model"]).unwrap();
        let expected = &case["expected_identity"];
        assert_eq!(
            env.environment_id(),
            expected["environment_id"].as_str().unwrap()
        );
        assert_eq!(
            doc.meaning_id().unwrap(),
            expected["meaning_id"].as_str().unwrap()
        );
        assert_eq!(model.model_id(), expected["model_id"].as_str().unwrap());
        for i in 0..doc.formulas().len() {
            assert_eq!(
                doc.formula_meaning_id(i).unwrap(),
                expected["formula_meaning_ids"][i].as_str().unwrap()
            );
        }
        for (key, value) in [
            ("canonical_environment", env.to_value()),
            ("canonical_ast", doc.to_value()),
            ("canonical_model", model.to_value()),
        ] {
            assert_eq!(
                canonical_json(&value).unwrap(),
                expected[key].as_str().unwrap().as_bytes()
            );
        }
    }
}
