#![forbid(unsafe_code)]
use serde_json::json;
use ve_core::*;

fn env(unused: bool, constants: bool) -> Environment {
    let mut v = json!({"language":"ve.core@0","profile":"relational-fol@0","spec_revision":"ve-v0-draft-2026-09-20","vocabulary":{"sorts":{"item":{"description":"Item."}},"predicates":{"marked":{"arguments":["item"],"description":"Marked."}},"constants":{}}});
    if unused {
        v["vocabulary"]["predicates"]["unused"] =
            json!({"arguments":["item","item"],"description":"Unused."});
    }
    if constants {
        v["vocabulary"]["constants"] = json!({"first":{"sort":"item","description":"First."},"second":{"sort":"item","description":"Second."}});
    }
    Environment::from_value(&v).unwrap()
}
#[test]
fn unused_predicates_do_not_expand_search() {
    for unused in [false, true] {
        let e = env(unused, false);
        let d = parse(
            &e,
            b"for every item a, ((a is marked) or (not (a is marked))).\n",
        )
        .unwrap();
        let p = CountermodelProblem::new(&e, vec![], d.formulas()[0].clone()).unwrap();
        let r = find_countermodel(
            &e,
            &p,
            SearchBounds {
                max_domain_size: 2,
                ..Default::default()
            },
        )
        .unwrap();
        assert_eq!(r.status, "NotFound");
        assert_eq!(r.models_checked, 7); // 1 + 2 + 4 unary extensions
        let p = CountermodelProblem::new(&e, vec![], Formula::Top).unwrap();
        let r = find_countermodel(
            &e,
            &p,
            SearchBounds {
                max_domain_size: 2,
                ..Default::default()
            },
        )
        .unwrap();
        assert_eq!(r.models_checked, 3); // no predicate used
    }
}
#[test]
fn constants_may_alias_and_empty_domains_are_not_inferred_inhabited() {
    let e = env(false, true);
    let d = parse(&e, b"not (@first equals @second).\n").unwrap();
    let p = CountermodelProblem::new(&e, vec![], d.formulas()[0].clone()).unwrap();
    let r = find_countermodel(&e, &p, Default::default()).unwrap();
    assert_eq!(r.status, "Found");
    assert_eq!(r.models_checked, 1);
    assert!(
        p.check_countermodel(r.model.as_ref().unwrap(), 100)
            .unwrap()
            .valid
    );
    let r = find_countermodel(
        &e,
        &p,
        SearchBounds {
            max_domain_size: 0,
            ..Default::default()
        },
    )
    .unwrap();
    assert_eq!(r.status, "NotFound");
    assert_eq!(r.models_checked, 0);
    let e = env(false, false);
    let d = parse(&e, b"there exists item a, (true).\n").unwrap();
    let p = CountermodelProblem::new(&e, vec![], d.formulas()[0].clone()).unwrap();
    let r = find_countermodel(&e, &p, Default::default()).unwrap();
    assert_eq!(r.status, "Found");
    assert_eq!(r.model.unwrap().to_value()["domains"]["item"], json!([]));
}
#[test]
fn limits_are_operational_and_checked_at_exhaustion_boundary() {
    let e = env(false, false);
    let p = CountermodelProblem::new(&e, vec![], Formula::Top).unwrap();
    for (bound, status, count) in [
        (0, "ResourceLimit", 0),
        (2, "ResourceLimit", 2),
        (3, "NotFound", 3),
    ] {
        let r = find_countermodel(
            &e,
            &p,
            SearchBounds {
                max_models: bound,
                ..Default::default()
            },
        )
        .unwrap();
        assert_eq!(r.status, status);
        assert_eq!(r.models_checked, count);
    }
    let p = CountermodelProblem::new(&e, vec![Formula::Top], Formula::Bottom).unwrap();
    let r = find_countermodel(
        &e,
        &p,
        SearchBounds {
            max_evaluations: 1,
            ..Default::default()
        },
    )
    .unwrap();
    assert_eq!(r.status, "ResourceLimit");
    assert_eq!(r.evaluations, 1);
    let r = find_countermodel(
        &e,
        &p,
        SearchBounds {
            max_evaluations: 2,
            ..Default::default()
        },
    )
    .unwrap();
    assert_eq!(r.status, "Found");
    let model = r.model.unwrap();
    let doc = parse(&e, b"false.\ntrue.\n").unwrap();
    assert_eq!(evaluate(&doc, &model, 0).unwrap().value, None);
    assert_eq!(evaluate(&doc, &model, 1).unwrap().value, Some(false));
    assert_eq!(
        evaluate(&doc, &model, MAX_EVALUATIONS + 1)
            .unwrap_err()
            .code,
        "ResourceLimit"
    );
}
#[test]
fn environment_binding_cannot_be_substituted() {
    let e = env(false, false);
    let mut v = e.to_value();
    v["vocabulary"]["sorts"]["item"]["description"] = json!("Changed.");
    let other = Environment::from_value(&v).unwrap();
    let m = FiniteModel::from_value(
        &other,
        &json!({"complete":true,"domains":{"item":[]},"constants":{},"relations":{"marked":[]}}),
    )
    .unwrap();
    let d = parse(&e, b"true.\n").unwrap();
    assert_eq!(evaluate(&d, &m, 100).unwrap_err().code, "InvalidModel");
    let p = CountermodelProblem::new(&e, vec![], Formula::Bottom).unwrap();
    assert!(find_countermodel(&other, &p, Default::default()).is_err());
}
