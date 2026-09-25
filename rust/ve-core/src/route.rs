//! ve.core@0.2 route helpers mirrored from `lean/VE/Route` and `ve/admission.py`,
//! `ve/background.py`: the claim-label grammar and the dependency-DAG order.
use crate::{Error, Result, error};
use std::collections::BTreeSet;

const GENERATORS: [&str; 4] = ["flags", "definitions", "literals", "profile"];

/// Names inside labels: nonempty, at most 64 bytes, `[A-Za-z0-9_.-]`.
pub fn token(s: &str) -> bool {
    !s.is_empty()
        && s.len() <= 64
        && s.bytes()
            .all(|b| b.is_ascii_alphanumeric() || matches!(b, b'_' | b'.' | b'-'))
}

fn natural(s: &str) -> bool {
    s == "0"
        || (s.starts_with(|c: char| ('1'..='9').contains(&c))
            && s.bytes().all(|b| b.is_ascii_digit()))
}

fn pair(s: &str, separator: char) -> Option<(&str, &str)> {
    let mut parts = s.split(separator);
    match (parts.next(), parts.next(), parts.next()) {
        (Some(a), Some(b), None) => Some((a, b)),
        _ => None,
    }
}

/// Only canonical labels parse: a parsed label renders back to exactly `s`.
pub fn label_is_canonical(s: &str) -> bool {
    if s == "asserted" {
        return true;
    }
    if let Some(inner) = s
        .strip_prefix("bridge:accepts(")
        .and_then(|rest| rest.strip_suffix(')'))
    {
        return pair(inner, ',').is_some_and(|(a, u)| token(a) && token(u));
    }
    if let Some(g) = s.strip_prefix("background:") {
        return GENERATORS.contains(&g);
    }
    if let Some(rest) = s.strip_prefix("cite:") {
        return pair(rest, '/').is_some_and(|(b, l)| token(b) && token(l));
    }
    if let Some(t) = s.strip_prefix("open:") {
        return token(t);
    }
    if let Some(rest) = s.strip_prefix("readings:") {
        return pair(rest, '@').is_some_and(|(set, rest)| {
            pair(rest, ':')
                .is_some_and(|(v, c)| token(set) && natural(v) && (c == "all" || natural(c)))
        });
    }
    if let Some(n) = s.strip_prefix("narrowing:") {
        return token(n);
    }
    false
}

pub fn check_label(s: &str) -> Result<()> {
    if label_is_canonical(s) {
        Ok(())
    } else {
        error("AdmissionError", format!("invalid label {s}"))
    }
}

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
