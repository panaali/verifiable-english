//! The Rust engine on the engine corpus (docs/spec/wire-contract-s4-2.md 7 and 9, F5 and F6): every fault
//! and `clean` record is byte-identical (canonical JSON) to `conformance/wire-contract/engine-golden.json`;
//! every deferred outcome is counted under Rust's deferred share and never compared.
#[allow(dead_code)]
mod corpus_tables;

use serde_json::{Value as Json, json};
use std::path::Path;
use ve_kernel::contract::*;
use ve_kernel::canonical_json;

fn read(relative: &str) -> Json {
    let path = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..").join(relative);
    serde_json::from_slice(&std::fs::read(path).unwrap()).unwrap()
}

fn table(unit: &str) -> &'static Table {
    corpus_tables::TABLES.iter().find(|t| t.contract == unit).expect("a corpus unit")
}

/// The unit's adapter of 2.1: the object with exactly the contract's `input` members, `null` when absent.
fn root(unit: &str, case: &Json) -> Json {
    let contract = read(&format!("conformance/wire-contract/contracts/{unit}.json"));
    let members = contract["input"].as_array().unwrap().iter().map(|name| {
        let name = name.as_str().unwrap();
        (name.to_string(), case.get(name).cloned().unwrap_or(Json::Null))
    });
    Json::Object(members.collect())
}

/// engine.json's cases with their hand-derived `expected` (8.1), or `$VE_ENGINE_CASES` (a JSON list of
/// `{unit, id, root}`, each with an optional `expected`).
fn cases() -> Vec<(String, String, Json, Option<Json>)> {
    let (list, unit) = match std::env::var_os("VE_ENGINE_CASES") {
        Some(path) => (serde_json::from_slice(&std::fs::read(path).unwrap()).unwrap(), None),
        None => (read("conformance/wire-contract/engine.json"), Some("demo@0")),
    };
    let list: &Vec<Json> = list.as_array().unwrap();
    list.iter()
        .map(|c| {
            let at = unit.or(c["unit"].as_str()).unwrap().to_string();
            (at, c["id"].as_str().unwrap().into(), c["root"].clone(), c.get("expected").cloned())
        })
        .collect()
}

fn canonical(v: &Json) -> String {
    String::from_utf8(canonical_json(v).unwrap()).unwrap()
}

/// F5: every fault and `clean` equals the golden record of its id byte for byte; an engine.json case
/// the golden names otherwise (`E2`, `E6`, `E17b`, `E19`), or a case sent with `expected`, equals its check, path and text.
/// Every deferred outcome is counted, never compared. The outcomes go to `$VE_ENGINE_OUT` as JSON lines.
#[test]
fn engine_corpus_equals_the_golden() {
    let all = read("conformance/wire-contract/engine-golden.json");
    let (mut golden, mut expected, mut deferred, mut lines) = (0, 0, Vec::new(), String::new());
    for (unit, id, case, hand) in cases() {
        let outcome = run(table(&unit), &root(&unit, &case)).unwrap();
        let row = match &outcome {
            Outcome::Fault(record) => json!({"id": id, "outcome": "fault", "record": record}),
            Outcome::Clean => json!({"id": id, "outcome": "clean"}),
            Outcome::Deferred(at) => json!({"id": id, "outcome": "deferred", "deferred": at}),
        };
        lines.push_str(&format!("{row}\n"));
        let rust = match outcome {
            Outcome::Fault(record) => record,
            Outcome::Clean => json!("clean"),
            Outcome::Deferred(at) => {
                deferred.push(format!("{id}@{at}"));
                continue;
            }
        };
        if let Some(record) = all[&unit].get(&id) {
            assert_eq!(canonical(&rust), canonical(record), "{unit} {id}");
            golden += 1;
        } else {
            let hand = hand.unwrap_or_else(|| panic!("no golden for {unit} {id}"));
            let triple = |r: &Json| json!([r["check"], r["path"], r["text"]]);
            assert_eq!(if rust == "clean" { Json::Null } else { triple(&rust) },
                       if hand.is_null() { hand } else { triple(&hand) }, "{id}");
            expected += 1;
        }
    }
    eprintln!("engine corpus in Rust: {golden} equal to the golden, {expected} to their hand-derived expected, {} deferred: {}",
              deferred.len(), deferred.join(" "));
    if let Some(path) = std::env::var_os("VE_ENGINE_OUT") {
        std::fs::write(path, lines).unwrap();
    }
    if std::env::var_os("VE_ENGINE_CASES").is_none() {
        assert_eq!((golden, expected, deferred.len()), (24, 3, 10), "Rust's share of engine.json changed");
    }
}

/// Plan row d: a deferred outcome names a hook, a classifier or an include with a view of its table.
#[test]
fn every_deferred_outcome_names_what_rust_lacks() {
    let lacking = |t: &Table| -> Vec<String> {
        fn walk(ids: &str, entries: &[Entry], out: &mut Vec<String>) {
            for e in entries {
                match e {
                    Entry::Check(c) if matches!(c.kind, Kind::Hook(_) | Kind::Classifier(..)) => {
                        out.push(format!("{ids}{}", c.id))
                    }
                    Entry::Check(_) => {}
                    Entry::Each(_, _, _, inner) => walk(ids, inner, out),
                    Entry::Scope(id, _, Some(_), _, _) => out.push(format!("{ids}{id}")),
                    Entry::Scope(id, _, None, _, inner) => walk(&format!("{ids}{id}/"), inner, out),
                }
            }
        }
        let mut out = Vec::new();
        t.phases.iter().for_each(|p| walk("", p.entries, &mut out));
        out
    };
    for (unit, id, case, _) in cases() {
        if let Outcome::Deferred(at) = run(table(&unit), &root(&unit, &case)).unwrap() {
            assert!(lacking(table(&unit)).contains(&at), "{unit} {id} deferred at {at}");
        }
    }
}

/// `inner@0` has no hook: Rust gives Lean's outcomes on it (tests/test_wire_contract_lean.py
/// `test_inner_contract_alone`), `clean` included.
#[test]
fn a_unit_without_hooks_is_clean_or_gives_lean_s_record() {
    let inner = table("inner@0");
    assert_eq!(run(inner, &json!({"x": 1, "ys": ["u"]})).unwrap(), Outcome::Clean);
    let Outcome::Fault(record) = run(inner, &json!({"x": true, "ys": null})).unwrap() else { panic!("b1 fails") };
    assert_eq!(canonical(&record), canonical(&json!({"contract": "inner@0", "revision": 1, "check": "b1",
        "phase": "body", "code": "INNER_BAD", "class": "InvalidInput", "path": "/x", "text": "Inner: x is true",
        "args": {"value": "true"}})));
}

/// A well-formed `demo@0` document whose table has `n` entries; the run defers at `3.4`.
fn large(n: usize) -> Json {
    let table: serde_json::Map<String, Json> = (0..n).map(|i| (format!("k{i}"), json!(i))).collect();
    json!({"doc": {"items": [{"name": "a", "tags": ["x"]}], "mode": "open", "owner": "root", "refs": ["a"],
                   "table": table, "part": {"x": 1, "ys": ["u"]}, "seed": 7}})
}

/// F6, the DRI's rule of 2026-10-27: the units a run spends grow by a fixed amount per table entry; the
/// largest document within `MAX_ENGINE_UNITS` ends within it, and one entry more is refused with
/// `ResourceLimit`, the limit's own code.
#[test]
fn a_large_input_ends_within_the_limit_and_one_step_over_is_refused() {
    let demo = table("demo@0");
    let spent = |n| run_within(demo, &large(n), u64::MAX).unwrap().1;
    let (base, step) = (spent(0), spent(1) - spent(0));
    // Each entry: one node for the domain pass, and the checks of the table entries (2.3a, 2.3b) reading it.
    assert_eq!((base, step), (129, 11));
    assert_eq!(spent(1000), base + 1000 * step);
    let n = ((MAX_ENGINE_UNITS - base) / step) as usize;
    assert_eq!(n, 90_897);
    let (outcome, used) = run_within(demo, &large(n), MAX_ENGINE_UNITS).unwrap();
    assert_eq!((outcome, used), (Outcome::Deferred("3.4".into()), base + n as u64 * step));
    assert_eq!(run(demo, &large(n)).unwrap(), Outcome::Deferred("3.4".into()));
    let over = run(demo, &large(n + 1)).unwrap_err();
    assert_eq!((over.code.as_str(), over.message.as_str()), ("ResourceLimit", "wire contract engine exceeds 1000000 units"));
}
