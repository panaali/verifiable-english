#![forbid(unsafe_code)]
use serde_json::json;
use ve_core::*;

fn environment() -> Environment {
    Environment::from_value(&json!({
        "language":"ve.core@0.1", "profiles":["closure@0","relational-fol@0"],
        "spec_revision":"ve-v0.1-closure-2026-09-21",
        "vocabulary":{"sorts":{"node":{"description":"Node."}},
            "predicates":{"edge":{"arguments":["node","node"],"description":"Edge."}},
            "constants":{"start":{"sort":"node","description":"Start."},
                         "end":{"sort":"node","description":"End."}}}
    }))
    .unwrap()
}

fn model(env: &Environment, rows: Vec<Vec<String>>, end: &str) -> FiniteModel {
    FiniteModel::from_value(
        env,
        &json!({"complete":true,"domains":{"node":["a","b","c"]},
        "constants":{"start":"a","end":end},"relations":{"edge":rows}}),
    )
    .unwrap()
}

#[test]
fn all_closure_conformance_formulas() {
    let cases = loads_json(include_bytes!("../../../conformance/closure.json")).unwrap();
    let mut count = 0;
    for case in cases.as_array().unwrap() {
        let env = Environment::from_value(&case["environment"]).unwrap();
        let doc = Document::from_value(&env, &case["ast"]).unwrap();
        let model = FiniteModel::from_value(&env, &case["model"]).unwrap();
        assert_eq!(print_document(&doc).unwrap(), case["source"]);
        assert_eq!(
            parse(&env, case["source"].as_str().unwrap().as_bytes()).unwrap(),
            doc
        );
        for (i, expected) in case["expected"].as_array().unwrap().iter().enumerate() {
            assert_eq!(
                json!(
                    evaluate_formula(&doc, i, &model, MAX_EVALUATIONS)
                        .unwrap()
                        .value
                ),
                *expected,
                "{} formula {i}",
                case["id"]
            );
            count += 1;
        }
    }
    assert_eq!(count, 866);
}

#[test]
fn all_three_vertex_graphs_agree_with_independent_path_search() {
    let env = environment();
    let mut formulas = Vec::new();
    for source in 0..3 {
        for destination in 0..3 {
            // Select each ordered pair by constant assignment below.
            formulas.push((source, destination));
        }
    }
    let doc = parse(&env, b"tc[edge](@start, @end).\nrtc[edge](@start, @end).\ntc[node a, b | (a edge b)](@start, @end).\n").unwrap();
    let names = ["a", "b", "c"];
    for mask in 0..512 {
        let mut rows = Vec::new();
        for &(a, b) in &formulas {
            if mask & (1 << (a * 3 + b)) != 0 {
                rows.push(vec![names[a].to_owned(), names[b].to_owned()]);
            }
        }
        for &(source, destination) in &formulas {
            let mut seen = [false; 3];
            let mut pending = vec![source];
            while let Some(a) = pending.pop() {
                for (b, visited) in seen.iter_mut().enumerate() {
                    if mask & (1 << (a * 3 + b)) != 0 && !*visited {
                        *visited = true;
                        pending.push(b);
                    }
                }
            }
            let mut raw = model(&env, rows.clone(), names[destination]).to_value();
            raw["constants"]["start"] = json!(names[source]);
            let m = FiniteModel::from_value(&env, &raw).unwrap();
            for i in 0..3 {
                let expected = seen[destination] || (i == 1 && source == destination);
                assert_eq!(
                    evaluate_formula(&doc, i, &m, MAX_EVALUATIONS)
                        .unwrap()
                        .value,
                    Some(expected),
                    "mask {mask}, {source}->{destination}, formula {i}"
                );
            }
        }
    }
}

#[test]
fn captured_parameters_and_models_cannot_share_stale_closures() {
    let env = environment();
    let doc = parse(
        &env,
        b"for every node z, (tc[node a, b | ((a edge b) and (not (b equals z)))](@start, @end)).\n",
    )
    .unwrap();
    let m = model(
        &env,
        vec![vec!["a".into(), "b".into()], vec!["b".into(), "c".into()]],
        "c",
    );
    // z=a admits the path; z=b blocks it. A cache missing z returns true.
    assert_eq!(
        evaluate(&doc, &m, MAX_EVALUATIONS).unwrap().value,
        Some(false)
    );
    let doc = parse(&env, b"tc[edge](@start, @end).\n").unwrap();
    assert_eq!(
        evaluate(&doc, &m, MAX_EVALUATIONS).unwrap().value,
        Some(true)
    );
    let empty = model(&env, Vec::new(), "c");
    assert_eq!(
        evaluate(&doc, &empty, MAX_EVALUATIONS).unwrap().value,
        Some(false)
    );
    assert_eq!(
        evaluate(&doc, &m, MAX_EVALUATIONS).unwrap().value,
        Some(true)
    );
}

#[test]
fn warshall_and_nested_body_work_exhausts_without_a_boolean() {
    let env = environment();
    let m = model(
        &env,
        vec![vec!["a".into(), "b".into()], vec!["b".into(), "c".into()]],
        "c",
    );
    for source in [
        "tc[edge](@start, @end).\n",
        "tc[node a, b | (a edge b)](@start, @end).\n",
        "tc[node a, b | (rtc[node c, d | (c edge d)](a, b))](@start, @end).\n",
    ] {
        let doc = parse(&env, source.as_bytes()).unwrap();
        let full = evaluate(&doc, &m, MAX_EVALUATIONS).unwrap();
        assert_eq!(full.value, Some(true));
        for budget in 0..full.evaluations {
            let partial = evaluate(&doc, &m, budget).unwrap();
            assert_eq!(partial.status, "ResourceLimit");
            assert_eq!(partial.value, None);
            assert_eq!(partial.evaluations, budget);
        }
        assert_eq!(
            evaluate(&doc, &m, full.evaluations).unwrap().value,
            Some(true)
        );
    }
}

#[test]
fn body_depth_scope_and_aggregate_node_limits() {
    let env = environment();
    let make = |body| {
        Formula::Reach(
            ReachKind::Plus,
            Edge::Body("node".into(), Box::new(body)),
            Term::Const("start".into()),
            Term::Const("end".into()),
        )
    };
    let bad = make(Formula::Eq(Term::Var(0), Term::Var(2)));
    assert_eq!(
        Document::check(&env, vec![bad]).unwrap_err().code,
        "UnboundVariable"
    );
    let mut f = Formula::Top;
    for _ in 0..63 {
        f = make(f);
    }
    let doc = Document::check(&env, vec![f.clone()]).unwrap();
    assert_eq!(Document::from_value(&env, &doc.to_value()).unwrap(), doc);
    assert_eq!(
        Document::check(&env, vec![make(f)]).unwrap_err().code,
        "ResourceLimit"
    );
    let f = make(Formula::Top); // four AST nodes; edge wrapper is not a node
    assert!(Document::check(&env, vec![f.clone(); 2500]).is_ok());
    assert_eq!(
        Document::check(&env, vec![f; 2501]).unwrap_err().code,
        "ResourceLimit"
    );
    let invalid = Formula::Reach(
        ReachKind::Invalid("plus".into()),
        Edge::Named("edge".into()),
        Term::Const("start".into()),
        Term::Const("end".into()),
    );
    assert_eq!(
        Document::check(&env, vec![invalid]).unwrap_err().code,
        "TypeMismatch"
    );
}
