//! ve.core@0.2 route helpers mirrored from `lean/VE/Route` and `ve/admission.py`,
//! `ve/background.py`: the claim-label grammar (the dependency-DAG order is kernel `graph`).
use crate::{Error, Formula, Result, error};

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

/// Bind a reading leaf to the latest registered version of its set and the
/// formula at its index. `all` is the right-nested disjunction of that set.
/// Bundle citation labels must be resolved through checked citations, not
/// accepted as leaves.
pub fn check_reading_binding(
    label: &str,
    formula: &Formula,
    sets: &[(String, u64, Vec<Formula>)],
) -> Result<()> {
    check_label(label)?;
    if label.starts_with("cite:") {
        return error("AdmissionError", "Unresolved citation hypothesis");
    }
    let Some(rest) = label.strip_prefix("readings:") else {
        return Ok(());
    };
    let (set, rest) = pair(rest, '@').expect("canonical reading label");
    let (version, choice) = pair(rest, ':').expect("canonical reading label");
    let version: u64 = version
        .parse()
        .map_err(|_| Error::new("AdmissionError", "reading version out of range"))?;
    let mut matches = sets.iter().filter(|(id, v, _)| id == set && *v == version);
    let Some((_, _, readings)) = matches.next() else {
        return error(
            "AdmissionError",
            "Reading label has no registered reading set",
        );
    };
    if matches.next().is_some() {
        return error(
            "AdmissionError",
            "Reading label has no unique registered reading set",
        );
    }
    if sets.iter().any(|(id, v, _)| id == set && *v > version) {
        return error(
            "AdmissionError",
            "Reading label depends on a superseded reading set version",
        );
    }
    if readings.is_empty() || readings.len() > 64 {
        return error("AdmissionError", "reading sets hold 1 to 64 readings");
    }
    let expected = if choice == "all" {
        readings
            .iter()
            .cloned()
            .rev()
            .reduce(|right, left| Formula::Or(Box::new(left), Box::new(right)))
    } else {
        let index: usize = choice
            .parse()
            .map_err(|_| Error::new("AdmissionError", "reading index out of range"))?;
        readings.get(index).cloned()
    };
    if expected.as_ref() != Some(formula) {
        return error(
            "AdmissionError",
            "Reading label is not bound to its registered reading formula",
        );
    }
    Ok(())
}

#[cfg(test)]
mod reading_binding_tests {
    use super::*;

    #[test]
    fn labels_name_only_registered_formulas_and_all_disjunction() {
        let p = Formula::Top;
        let not_p = Formula::Not(Box::new(Formula::Top));
        let all = Formula::Or(Box::new(p.clone()), Box::new(not_p.clone()));
        let sets = vec![("u".to_string(), 0, vec![p.clone(), not_p.clone()])];
        assert!(check_reading_binding("readings:u@0:0", &p, &sets).is_ok());
        assert!(check_reading_binding("readings:u@0:all", &all, &sets).is_ok());
        assert!(check_reading_binding("readings:u@0:0", &not_p, &sets).is_err());
        assert!(check_reading_binding("readings:u@0:all", &not_p, &sets).is_err());
        assert!(check_reading_binding("readings:u@0:1", &p, &sets).is_err());
        let duplicates = vec![
            ("u".to_string(), 0, vec![p.clone()]),
            ("u".to_string(), 0, vec![not_p.clone()]),
        ];
        assert!(check_reading_binding("readings:u@0:0", &p, &duplicates).is_err());
        assert!(check_reading_binding("cite:local/A", &p, &sets).is_err());
    }

    #[test]
    fn superseded_reading_version_is_rejected() {
        let p = Formula::Top;
        let not_p = Formula::Not(Box::new(p.clone()));
        let sets = vec![
            ("u".to_string(), 0, vec![p.clone()]),
            ("u".to_string(), 1, vec![p.clone(), not_p]),
        ];
        assert!(check_reading_binding("readings:u@0:all", &p, &sets).is_err());
        assert!(check_reading_binding("readings:u@1:0", &p, &sets).is_ok());
    }
}
