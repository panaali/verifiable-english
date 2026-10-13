#![forbid(unsafe_code)]
//! premise-scale: per-sort domain bounds and the ground-fact route of the countermodel search.
use serde_json::{Value, json};
use ve_core::*;

const SPEC: &str = "ve-v0.2-expand2-2026-09-25";

/// Sort `principal_type` with three constants and a unary `principal`.
fn principals() -> Environment {
    Environment::from_value(&json!({
        "language":"ve.core@0.2", "profiles":["relational-fol@0"], "spec_revision":SPEC,
        "vocabulary":{
            "sorts":{"principal_type":{"description":"Principal type."}},
            "predicates":{"principal":{"arguments":["principal_type"],"description":"Principal."}},
            "constants":{"anthropic":{"sort":"principal_type","description":"A."},
                         "operators":{"sort":"principal_type","description":"O."},
                         "users":{"sort":"principal_type","description":"U."}}}})).unwrap()
}

/// The three constants are principals and pairwise distinct.
fn three_distinct(e: &Environment) -> CountermodelProblem {
    let names = ["anthropic", "operators", "users"];
    let mut facts: Vec<Value> = names.iter().map(|n| json!(["unary","principal",["const",n]])).collect();
    for (i, a) in names.iter().enumerate() {
        for b in &names[i + 1..] {
            facts.push(json!(["not",["eq",["const",a],["const",b]]]));
        }
    }
    let premise = facts.into_iter().rev().reduce(|acc, f| json!(["and", f, acc])).unwrap();
    let document = Document::from_value(e, &json!([premise, ["bottom"]])).unwrap();
    let (last, premises) = document.formulas().split_last().unwrap();
    CountermodelProblem::new(e, premises.to_vec(), last.clone()).unwrap()
}

fn bounded(e: &Environment, p: &CountermodelProblem, bounds: &SortBounds, ground: bool) -> SearchResult {
    find_countermodel_bounded(e, p, SearchBounds::default(), 0, None, false, bounds, ground).unwrap()
}

#[test]
fn shared_bound_cannot_hold_three_distinct_constants() {
    let e = principals();
    let r = bounded(&e, &three_distinct(&e), &SortBounds::new(), false);
    assert_eq!(r.status, "NotFound");
}

#[test]
fn a_raised_sort_is_searched_at_its_size() {
    let e = principals();
    let p = three_distinct(&e);
    let bounds = SortBounds::from([("principal_type".to_owned(), (3, 3))]);
    let r = bounded(&e, &p, &bounds, false);
    assert_eq!(r.status, "Found");
    let model = r.model.unwrap();
    assert_eq!(model.to_value()["domains"]["principal_type"].as_array().unwrap().len(), 3);
    assert!(p.check_countermodel(&model, 100_000).unwrap().valid);
}

#[test]
fn the_ground_route_tries_the_stated_facts_alone() {
    let e = principals();
    let p = three_distinct(&e);
    // Within the shared bound the candidate (three entities) does not fit: nothing is tried.
    let r = bounded(&e, &p, &SortBounds::new(), true);
    assert_eq!((r.status, r.models_checked), ("NotFound", 0));
    let bounds = SortBounds::from([("principal_type".to_owned(), (3, 3))]);
    let r = bounded(&e, &p, &bounds, true);
    assert_eq!((r.status, r.models_checked), ("Found", 1));
    let model = r.model.unwrap().to_value();
    assert_eq!(model["relations"]["principal"], json!([["e0"], ["e1"], ["e2"]]));
    assert_eq!(model["constants"], json!({"anthropic":"e0","operators":"e1","users":"e2"}));
}

#[test]
fn a_ground_candidate_the_premises_reject_is_no_witness() {
    let e = principals();
    // anthropic is stated a principal and not one: the candidate fails the premises.
    let document = Document::from_value(&e, &json!([
        ["and",["unary","principal",["const","anthropic"]],["not",["unary","principal",["const","anthropic"]]]],
        ["bottom"]])).unwrap();
    let (last, premises) = document.formulas().split_last().unwrap();
    let p = CountermodelProblem::new(&e, premises.to_vec(), last.clone()).unwrap();
    let r = bounded(&e, &p, &SortBounds::from([("principal_type".to_owned(), (3, 3))]), true);
    assert_eq!((r.status, r.models_checked), ("NotFound", 1));
}

#[test]
fn sort_bounds_name_declared_sorts_in_order() {
    let e = principals();
    let p = three_distinct(&e);
    for (bounds, code) in [(SortBounds::from([("ghost".to_owned(), (1, 1))]), "InvalidInput"),
                           (SortBounds::from([("principal_type".to_owned(), (3, 2))]), "ResourceLimit"),
                           (SortBounds::from([("principal_type".to_owned(), (1, 1001))]), "ResourceLimit")] {
        let error = find_countermodel_bounded(&e, &p, SearchBounds::default(), 0, None, false, &bounds, false)
            .unwrap_err();
        assert_eq!(error.code, code);
    }
}

#[test]
fn ground_route_on_stated_quantities() {
    // H's shape through the order search: the stated values are the model, at once.
    let constants: serde_json::Map<String, Value> = (0..60)
        .map(|i| (format!("q{i:02}"), json!({"sort":"$int","description":"q"}))).collect();
    let facts: Vec<Value> = (0..60).map(|i| json!(["eq",["const",format!("q{i:02}")],["num",(4000 + 7 * i).to_string()]])).collect();
    let premises: Vec<Value> = facts.chunks(20)
        .map(|c| c.iter().cloned().rev().reduce(|acc, f| json!(["and", f, acc])).unwrap()).collect();
    let case = |ground: bool| json!({"id":"q","environment":{"language":"ve.core@0.2",
        "profiles":["documents@1","order@0","relational-fol@0","time@0"],"spec_revision":SPEC,
        "vocabulary":{"sorts":{},"predicates":{},"constants":constants}},
        "premises":premises,"conclusion":["bottom"],"max_models":500,"max_evaluations":100_000,
        "ground_only":ground});
    let searched = order_case(&case(false)).unwrap();
    assert_eq!(searched["status"], "ResourceLimit");
    let ground = order_case(&case(true)).unwrap();
    assert_eq!((ground["status"].as_str(), ground["models_checked"].as_u64()), (Some("Found"), Some(1)));
    assert_eq!(ground["model"]["constants"]["q59"], json!((4000 + 7 * 59).to_string()));
}
