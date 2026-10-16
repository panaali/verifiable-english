//! premise-scale: the ground-fact candidate. A premise set whose facts are ground (a constant
//! equal to a numeral, a predicate applied to constants) states its own model: each constant
//! its own entity (constants a premise equates share one), each integer constant the numeral it
//! is equated to (else a bound a premise gives it, else 0), each stated atom true and every
//! other atom false. Search tries it before its enumeration, as one more untrusted candidate
//! within the same per-sort bounds; Lean checks it like every witness, and a candidate the
//! premises reject costs one model attempt.
use num_bigint::BigInt;
use serde_json::{Value, json};
use std::collections::BTreeMap;
use ve_kernel::{Environment, internal::EnvironmentInternals};

fn tag(v: &Value) -> Option<(&str, &[Value])> {
    let a = v.as_array()?;
    Some((a.first()?.as_str()?, a.as_slice()))
}

/// The top-level conjuncts of a formula: what every model of it makes true.
fn conjuncts<'a>(f: &'a Value, out: &mut Vec<&'a Value>) {
    match tag(f) {
        Some(("and", a)) if a.len() == 3 => {
            conjuncts(&a[1], out);
            conjuncts(&a[2], out);
        }
        _ => out.push(f),
    }
}

fn constant(t: &Value) -> Option<&str> {
    match tag(t)? {
        ("const", [_, name]) => name.as_str(),
        _ => None,
    }
}

fn numeral(t: &Value) -> Option<BigInt> {
    match tag(t)? {
        ("num", [_, n]) => n.as_str()?.parse().ok(),
        _ => None,
    }
}

/// The class representative of `c` (union by least name).
fn find(parent: &mut BTreeMap<String, String>, c: &str) -> String {
    let mut root = c.to_owned();
    while let Some(next) = parent.get(&root).filter(|p| **p != root) {
        root = next.clone();
    }
    parent.insert(c.to_owned(), root.clone());
    root
}

/// The candidate model's JSON, or None when it does not fit the per-sort bounds: `sorts`,
/// `minima` and `maxima` are the search's (one entry per model sort).
pub(crate) fn candidate(env: &Environment, premises: &[Value], sorts: &[String], minima: &[usize],
                        maxima: &[usize]) -> Option<Value> {
    let mut facts = Vec::new();
    for premise in premises {
        conjuncts(premise, &mut facts);
    }
    let constants = env.constants();
    let is_int = |c: &str| constants.get(c).is_some_and(|s| s == "$int");
    // Integer constants: an equated numeral first, then a stated bound.
    let mut values: BTreeMap<String, BigInt> = BTreeMap::new();
    let (mut lower, mut upper): (BTreeMap<String, BigInt>, BTreeMap<String, BigInt>) =
        (BTreeMap::new(), BTreeMap::new());
    let mut parent: BTreeMap<String, String> = BTreeMap::new();
    for fact in &facts {
        let Some((kind, a)) = tag(fact) else { continue };
        if a.len() != 3 { continue; }
        match kind {
            "eq" => match (constant(&a[1]), constant(&a[2]), numeral(&a[1]), numeral(&a[2])) {
                (Some(c), _, _, Some(n)) | (_, Some(c), Some(n), _) if is_int(c) => {
                    values.entry(c.to_owned()).or_insert(n);
                }
                (Some(c), Some(d), _, _) if !is_int(c) && constants.get(c) == constants.get(d) => {
                    let (x, y) = (find(&mut parent, c), find(&mut parent, d));
                    let (low, high) = if x <= y { (x, y) } else { (y, x) };
                    parent.insert(high, low);
                }
                _ => {}
            },
            "le" | "lt" => {
                let strict = BigInt::from(u8::from(kind == "lt"));
                match (constant(&a[1]), constant(&a[2]), numeral(&a[1]), numeral(&a[2])) {
                    (Some(c), _, _, Some(n)) if is_int(c) => {
                        let bound = n - strict;
                        let entry = upper.entry(c.to_owned()).or_insert_with(|| bound.clone());
                        if bound < *entry { *entry = bound; }
                    }
                    (_, Some(c), Some(n), _) if is_int(c) => {
                        let bound = n + strict;
                        let entry = lower.entry(c.to_owned()).or_insert_with(|| bound.clone());
                        if bound > *entry { *entry = bound; }
                    }
                    _ => {}
                }
            }
            _ => {}
        }
    }
    // Equated integer constants share a value.
    loop {
        let mut changed = false;
        for fact in &facts {
            let Some(("eq", [_, t, u])) = tag(fact) else { continue };
            let (Some(c), Some(d)) = (constant(t), constant(u)) else { continue };
            if !(is_int(c) && is_int(d)) { continue; }
            match (values.get(c).cloned(), values.get(d).cloned()) {
                (Some(v), None) => { values.insert(d.to_owned(), v); changed = true; }
                (None, Some(v)) => { values.insert(c.to_owned(), v); changed = true; }
                _ => {}
            }
        }
        if !changed { break; }
    }
    // One entity per class of object constants, in constant-name order, padded to the minimum.
    let mut domains: BTreeMap<&String, Vec<String>> = BTreeMap::new();
    let mut entity: BTreeMap<String, String> = BTreeMap::new();
    for ((sort, least), most) in sorts.iter().zip(minima).zip(maxima) {
        let mut entities = Vec::new();
        for (name, s) in constants {
            if s != sort { continue; }
            let root = find(&mut parent, name);
            if !entity.contains_key(&root) {
                let e = format!("e{}", entities.len());
                entities.push(e.clone());
                entity.insert(root.clone(), e);
            }
        }
        while entities.len() < *least {
            entities.push(format!("e{}", entities.len()));
        }
        if entities.len() > *most {
            return None;
        }
        domains.insert(sort, entities);
    }
    let cell = |t: &Value, parent: &mut BTreeMap<String, String>| -> Option<Value> {
        if let Some(n) = numeral(t) {
            return Some(json!(n.to_string()));
        }
        let c = constant(t)?;
        if is_int(c) {
            return Some(json!(values.get(c).cloned()
                .or_else(|| lower.get(c).cloned()).or_else(|| upper.get(c).cloned())
                .unwrap_or_default().to_string()));
        }
        constants.get(c)?;
        Some(json!(entity[&find(parent, c)]))
    };
    let mut model_constants = serde_json::Map::new();
    for name in constants.keys() {
        model_constants.insert(name.clone(), cell(&json!(["const", name]), &mut parent)?);
    }
    let mut relations: BTreeMap<&String, Vec<Vec<Value>>> = env.predicates().keys()
        .filter(|p| !env.is_defined(p)).map(|p| (p, Vec::new())).collect();
    for fact in &facts {
        let (name, terms): (&str, Vec<&Value>) = match tag(fact) {
            Some(("unary" | "binary", a)) if a.len() >= 3 => match a[1].as_str() {
                Some(name) => (name, a[2..].iter().collect()),
                None => continue,
            },
            Some(("atom", [_, name, terms])) => match (name.as_str(), terms.as_array()) {
                (Some(name), Some(terms)) => (name, terms.iter().collect()),
                _ => continue,
            },
            _ => continue,
        };
        let Some(rows) = relations.iter_mut().find(|(p, _)| p.as_str() == name).map(|(_, r)| r) else {
            continue;
        };
        let row: Option<Vec<Value>> = terms.into_iter().map(|t| cell(t, &mut parent)).collect();
        if let Some(row) = row.filter(|row| !rows.contains(row)) {
            rows.push(row);
        }
    }
    Some(json!({"complete": true, "domains": domains, "constants": model_constants,
                "relations": relations}))
}
