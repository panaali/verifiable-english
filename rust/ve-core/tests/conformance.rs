#![forbid(unsafe_code)]
use serde_json::json;
use ve_core::*;

#[test]
fn discourse_elaboration_is_an_untrusted_core_carrier() {
    // Reference resolution belongs to the discourse validator. The Rust core
    // consumes only the elaborated formula under the stripped base profile.
    let environment = json!({"language":"ve.core@0.2", "profiles":["relational-fol@0"],
        "spec_revision":"ve-v0.2-expand2-2026-09-25",
        "vocabulary":{"sorts":{"service":{"description":"service"}},
            "predicates":{"safe":{"arguments":["service"],"description":"safe"}},
            "constants":{"api":{"sort":"service","description":"Api"}}}});
    let case = json!({"id":"alpha","family":"elaborated-document", "untrusted":true,
        "environment":environment, "formulas":[["unary","safe",["const","api"]]],
        "model":{"complete":true,"domains":{"service":["a"]},
            "constants":{"api":"a"},"relations":{"safe":[["a"]]}}});
    let out = elaborated_document_case(&case).unwrap();
    assert_eq!(out["family"], ELABORATED_DOCUMENT);
    assert_eq!(out["untrusted"], true);
    assert_eq!(out["values"], json!([true]));
    assert_eq!(out["premises"]["status"], "model");
    let env = Environment::from_value(&environment).unwrap();
    let doc = Document::from_value(&env, &case["formulas"]).unwrap();
    assert_eq!(out["meaning_ids"], json!([doc.formula_meaning_id(0).unwrap()]));
    // the family is untrusted input by construction, and never the discourse profile
    let mut trusted = case.clone();
    trusted["untrusted"] = json!(false);
    assert_eq!(elaborated_document_case(&trusted).unwrap_err().code, "InvalidInput");
    let mut profiled = case.clone();
    profiled["environment"]["profiles"] = json!(["relational-fol@0", "ve.discourse@1"]);
    assert_eq!(elaborated_document_case(&profiled).unwrap_err().code, "UnsupportedProfile");
}

#[test]
fn defined_declaration_computes_its_table() {
    let env = json!({"language":"ve.core@0.2",
        "profiles":["definitions@0","relational-fol@0"],
        "spec_revision":"ve-v0.2-expand2-2026-09-25",
        "vocabulary":{"sorts":{"point":{"description":"point"}},
            "predicates":{"base":{"arguments":["point"],"description":"base"},
                "alias":{"arguments":["point"],"description":"alias",
                    "defined":{"arguments":["point"],"body":["unary","base",["var",0]]}}},
            "constants":{}}});
    let env = Environment::from_value(&env).unwrap();
    let model = FiniteModel::from_value(&env, &json!({"complete":true,"domains":{"point":["p","q"]},
        "constants":{},"relations":{"base":[["p"]]}})).unwrap();
    let doc = Document::from_value(&env, &json!([["unary","alias",["const","x"]]]));
    assert!(doc.is_err());
    let values = evaluate(&Document::from_value(&env, &json!([["exists","point",["unary","alias",["var",0]]],
        ["forall","point",["unary","alias",["var",0]]]])).unwrap(), &model, 1000).unwrap();
    assert_eq!(values.value, Some(false));
    let supplied = FiniteModel::from_value(&env, &json!({"complete":true,"domains":{"point":["p"]},
        "constants":{},"relations":{"base":[["p"]],"alias":[["p"]]}})).unwrap_err();
    assert_eq!(supplied.code, "InvalidModel");
    assert!(supplied.message.ends_with("(definitions)"));
}

#[test]
fn nary_defined_declaration_computes_its_table() {
    let env = json!({"language":"ve.core@0.2",
        "profiles":["closure@0","definitions@0","nary@0","relational-fol@0"],
        "spec_revision":"ve-v0.2-expand2-2026-09-25",
        "vocabulary":{"sorts":{"point":{"description":"point"}},
            "predicates":{"base":{"arguments":["point","point","point"],"description":"base"},
                "alias":{"arguments":["point","point","point"],"description":"alias",
                    "defined":{"arguments":["point","point","point"],
                               "body":["atom","base",[["var",2],["var",1],["var",0]]]}}},
            "constants":{"a":{"sort":"point","description":"a"},
                         "b":{"sort":"point","description":"b"}}}});
    let env = Environment::from_value(&env).unwrap();
    let model = FiniteModel::from_value(&env, &json!({"complete":true,
        "domains":{"point":["a","b"]},"constants":{"a":"a","b":"b"},
        "relations":{"base":[["a","b","a"]]}})).unwrap();
    let doc = Document::from_value(&env, &json!([
        ["atom","alias",[["const","a"],["const","b"],["const","a"]]],
        ["atom","alias",[["const","b"],["const","a"],["const","b"]]]])).unwrap();
    assert!(evaluate_formula(&doc, 0, &model, 1000).unwrap().value.unwrap());
    assert!(!evaluate_formula(&doc, 1, &model, 1000).unwrap().value.unwrap());
}

#[test]
fn shared_evaluation_corpus() {
    let cases = loads_json(include_bytes!("../../../conformance/evaluation.json")).unwrap();
    let mut count = 0;
    for case in cases.as_array().unwrap() {
        let env = Environment::from_value(&case["environment"]).unwrap();
        let doc = Document::from_value(&env, &case["ast"]).unwrap();
        let model = FiniteModel::from_value(&env, &case["model"]).unwrap();
        let canonical = print_document(&doc).unwrap();
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
    assert_eq!(count, 4912);
}

#[test]
fn shared_countermodel_corpus() {
    let cases = loads_json(include_bytes!("../../../conformance/countermodels.json")).unwrap();
    assert_eq!(cases.as_array().unwrap().len(), 708);
    for case in cases.as_array().unwrap() {
        let env = Environment::from_value(&case["environment"]).unwrap();
        let model = FiniteModel::from_value(&env, &case["model"]).unwrap();
        let mut ast = case["premises"].as_array().unwrap().clone();
        ast.push(case["conclusion"].clone());
        let doc = Document::from_value(&env, &json!(ast)).unwrap();
        let (conclusion, premises) = doc.formulas().split_last().unwrap();
        let problem =
            CountermodelProblem::new(&env, premises.to_vec(), conclusion.clone()).unwrap();
        let result = problem.check_countermodel(&model, MAX_EVALUATIONS).unwrap();
        assert_eq!(
            json!(result.valid),
            case["expected_refutes"],
            "{}",
            case["id"]
        );
    }
}

#[test]
fn shared_wire_diagnostic_classes() {
    let cases = loads_json(include_bytes!("../../../conformance/wire.json")).unwrap();
    for case in cases.as_array().unwrap() {
        let result = loads_json(case["raw"].as_str().unwrap().as_bytes());
        if let Some(code) = case.get("expected_error") {
            assert_eq!(
                result.unwrap_err().code,
                code.as_str().unwrap(),
                "{}",
                case["id"]
            );
        } else {
            assert_eq!(
                canonical_json(&result.unwrap()).unwrap(),
                case["expected"].as_str().unwrap().as_bytes()
            );
        }
    }
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
                print_document(&doc).unwrap(),
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

#[test]
fn canonical_output_budget_is_separate_from_ast_budget() {
    let cases = loads_json(include_bytes!("../../../conformance/evaluation.json")).unwrap();
    let env = Environment::from_value(&cases[0]["environment"]).unwrap();
    let f = Formula::Implies(Box::new(Formula::Top), Box::new(Formula::Top));
    let doc = Document::check(&env, vec![f; 3000]).unwrap();
    assert_eq!(print_document(&doc).unwrap_err().code, "ResourceLimit");
}
