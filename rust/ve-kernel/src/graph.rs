//! The dependency-DAG order (kernel): `Environment` checks definition order with it and the
//! `ve` binary answers `dependency-order` route cases with it.
use crate::{Error, Result, error};
use std::collections::BTreeSet;

/// One DAG over defined and regulated symbols: repeatedly place the smallest
/// ready node; edges run only to mentioned symbols that are nodes.
pub fn dependency_order(nodes: &[(String, Vec<String>)]) -> Result<Vec<String>> {
    if nodes.len() > 256 {
        return error("ResourceLimit", "dependency graph size");
    }
    if let Some((name, _)) = nodes
        .iter()
        .find(|(n, _)| nodes.iter().filter(|(m, _)| m == n).count() > 1)
    {
        return Err(Error::new(
            "DuplicateDeclaration",
            format!("dependency node {name}"),
        ));
    }
    let names: BTreeSet<&str> = nodes.iter().map(|(n, _)| n.as_str()).collect();
    let mut remaining: Vec<(&str, BTreeSet<&str>)> = nodes
        .iter()
        .map(|(n, ms)| {
            (
                n.as_str(),
                ms.iter()
                    .map(String::as_str)
                    .filter(|m| names.contains(m))
                    .collect(),
            )
        })
        .collect();
    let mut order = Vec::new();
    while !remaining.is_empty() {
        let Some(ready) = remaining
            .iter()
            .filter(|(_, deps)| deps.is_empty())
            .map(|(n, _)| *n)
            .min()
        else {
            let mut unplaced: Vec<&str> = remaining.iter().map(|(n, _)| *n).collect();
            unplaced.sort_unstable();
            return error("DependencyCycle", unplaced.join(", "));
        };
        order.push(ready.to_owned());
        remaining.retain(|(n, _)| *n != ready);
        for (_, deps) in &mut remaining {
            deps.remove(ready);
        }
    }
    Ok(order)
}
