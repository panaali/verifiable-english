//! Untrusted stage-A condition evaluator for differential checks against Lean.
//! Coordinates are integers on their declared W6 grid; this module neither
//! admits a decision nor certifies a policy verdict.
use crate::{Error, Result, error};
use num_bigint::{BigInt, Sign};
use serde_json::Value;
use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Debug)]
pub struct Range {
    pub tag: String,
    pub lo: BigInt,
    pub hi: BigInt,
}

#[derive(Clone, Debug)]
struct Form {
    tag: String,
    coefficients: BTreeMap<String, BigInt>,
    constant: BigInt,
}

#[derive(Clone, Copy, Debug)]
enum Relation { Lt, Le, Eq, Ne }

#[derive(Clone, Debug)]
enum Condition {
    Atom(Form, Relation), And(Box<Self>, Box<Self>), Or(Box<Self>, Box<Self>), Top, Bottom,
}

fn shape<'a>(value: &'a Value) -> Result<(&'a str, &'a [Value])> {
    let parts = value.as_array().ok_or_else(|| Error::new("InvalidInput", "risk condition node"))?;
    let name = parts.first().and_then(Value::as_str)
        .ok_or_else(|| Error::new("InvalidInput", "risk condition tag"))?;
    Ok((name, parts))
}

fn text(value: &Value) -> Result<&str> {
    value.as_str().ok_or_else(|| Error::new("InvalidInput", "risk condition string"))
}

fn integer(value: &Value) -> Result<BigInt> {
    let s = text(value)?;
    let digits = s.strip_prefix('-').unwrap_or(s);
    if digits.is_empty() || digits.len() > 40 || (digits.len() > 1 && digits.starts_with('0'))
        || s == "-0" || !digits.bytes().all(|b| b.is_ascii_digit()) {
        return error("InvalidInput", "risk coefficient");
    }
    s.parse().map_err(|_| Error::new("InvalidInput", "risk coefficient"))
}

fn decimal(value: &Value, tag: &str, scales: &BTreeMap<String, BigInt>) -> Result<BigInt> {
    let s = text(value)?;
    let unsigned = s.strip_prefix('-').unwrap_or(s);
    let halves: Vec<_> = unsigned.split('.').collect();
    if halves.is_empty() || halves.len() > 2 || halves[0].is_empty()
        || (halves[0].len() > 1 && halves[0].starts_with('0'))
        || halves.iter().any(|part| part.is_empty() || !part.bytes().all(|b| b.is_ascii_digit()))
        || s.starts_with("-0") && unsigned == "0" || unsigned.len() > 41 {
        return error("InvalidInput", "risk decimal");
    }
    let scale = if tag == "dimensionless" { BigInt::from(1) } else {
        scales.get(tag).cloned().ok_or_else(|| Error::new("UnknownSymbol", format!("unit {tag}")))?
    };
    let places = if halves.len() == 2 { halves[1].len() } else { 0 };
    if halves.iter().map(|x| x.len()).sum::<usize>() > 40 {
        return error("ResourceLimit", "risk decimal digits");
    }
    let numerator: BigInt = halves.concat().parse().map_err(|_| Error::new("InvalidInput", "risk decimal"))?;
    let divisor = BigInt::from(10).pow(places as u32);
    let scaled = numerator * scale;
    if &scaled % &divisor != BigInt::from(0) {
        return error("UnitPrecision", format!("{tag}, scale"));
    }
    let coordinate = scaled / divisor;
    Ok(if s.starts_with('-') { -coordinate } else { coordinate })
}

fn add(left: Form, right: Form) -> Result<Form> {
    if left.tag != right.tag { return error("UnitMismatch", format!("{},{}", left.tag, right.tag)); }
    let mut coefficients = left.coefficients;
    for (name, coefficient) in right.coefficients {
        *coefficients.entry(name).or_default() += coefficient;
    }
    coefficients.retain(|_, coefficient| *coefficient != BigInt::from(0));
    Ok(Form { tag: left.tag, coefficients, constant: left.constant + right.constant })
}

fn scale(mut form: Form, coefficient: BigInt) -> Form {
    form.constant *= &coefficient;
    for value in form.coefficients.values_mut() { *value *= &coefficient; }
    form.coefficients.retain(|_, value| *value != BigInt::from(0));
    form
}

fn term(value: &Value, ranges: &BTreeMap<String, Range>, scales: &BTreeMap<String, BigInt>) -> Result<Form> {
    let (name, parts) = shape(value)?;
    match (name, parts.len()) {
        ("quantity", 2) => {
            let id = text(&parts[1])?;
            let range = ranges.get(id).ok_or_else(|| Error::new("RiskUnestimated", id))?;
            Ok(Form { tag: range.tag.clone(), coefficients: BTreeMap::from([(id.to_owned(), BigInt::from(1))]),
                      constant: BigInt::from(0) })
        }
        ("decimal", 3) => {
            let tag = text(&parts[1])?;
            Ok(Form { tag: tag.to_owned(), coefficients: BTreeMap::new(),
                      constant: decimal(&parts[2], tag, scales)? })
        }
        ("add", 4) => {
            let tag = text(&parts[1])?;
            let result = add(term(&parts[2], ranges, scales)?, term(&parts[3], ranges, scales)?)?;
            if result.tag != tag { return error("UnitMismatch", format!("{tag},{}", result.tag)); }
            Ok(result)
        }
        ("scale", 4) => {
            let tag = text(&parts[1])?;
            let result = scale(term(&parts[3], ranges, scales)?, integer(&parts[2])?);
            if result.tag != tag { return error("UnitMismatch", format!("{tag},{}", result.tag)); }
            Ok(result)
        }
        _ => error("InvalidInput", "risk term"),
    }
}

fn condition(value: &Value, negated: bool, ranges: &BTreeMap<String, Range>,
             scales: &BTreeMap<String, BigInt>, counts: &mut BTreeMap<String, usize>) -> Result<Condition> {
    let (name, parts) = shape(value)?;
    match (name, parts.len()) {
        ("top", 1) => Ok(if negated { Condition::Bottom } else { Condition::Top }),
        ("bottom", 1) => Ok(if negated { Condition::Top } else { Condition::Bottom }),
        ("not", 2) => condition(&parts[1], !negated, ranges, scales, counts),
        ("and" | "or", 3) => {
            let left = condition(&parts[1], negated, ranges, scales, counts)?;
            let right = condition(&parts[2], negated, ranges, scales, counts)?;
            Ok(if (name == "and") != negated { Condition::And(Box::new(left), Box::new(right)) }
               else { Condition::Or(Box::new(left), Box::new(right)) })
        }
        ("lt" | "le" | "eq", 3) => {
            let left = term(&parts[1], ranges, scales)?;
            let right = scale(term(&parts[2], ranges, scales)?, BigInt::from(-1));
            let mut form = add(left, right)?;
            let relation = match (name, negated) {
                ("lt", false) => Relation::Lt, ("le", false) => Relation::Le,
                ("eq", false) => Relation::Eq, ("eq", true) => Relation::Ne,
                ("lt", true) => Relation::Le, _ => Relation::Lt,
            };
            if negated && name != "eq" { form = scale(form, BigInt::from(-1)); }
            for (id, coefficient) in &form.coefficients {
                if ranges[id].lo != ranges[id].hi {
                    *counts.entry(id.clone()).or_default() += 1;
                    if matches!(relation, Relation::Eq | Relation::Ne) && coefficient != &BigInt::from(1)
                        && coefficient != &BigInt::from(-1) {
                        return error("RiskEqualityCoefficient", id.clone());
                    }
                }
            }
            Ok(Condition::Atom(form, relation))
        }
        _ => error("InvalidInput", "risk condition"),
    }
}

fn atom_bounds(form: &Form, ranges: &BTreeMap<String, Range>) -> (BigInt, BigInt) {
    let mut min = form.constant.clone();
    let mut max = form.constant.clone();
    for (id, coefficient) in &form.coefficients {
        let range = &ranges[id];
        if coefficient.sign() == Sign::Minus {
            min += coefficient * &range.hi;
            max += coefficient * &range.lo;
        } else {
            min += coefficient * &range.lo;
            max += coefficient * &range.hi;
        }
    }
    (min, max)
}

fn evaluate(cond: &Condition, ranges: &BTreeMap<String, Range>) -> (bool, bool) {
    match cond {
        Condition::Top => (true, true), Condition::Bottom => (false, false),
        Condition::And(a, b) => { let x = evaluate(a, ranges); let y = evaluate(b, ranges); (x.0 && y.0, x.1 && y.1) }
        Condition::Or(a, b) => { let x = evaluate(a, ranges); let y = evaluate(b, ranges); (x.0 || y.0, x.1 || y.1) }
        Condition::Atom(form, relation) => {
            let (min, max) = atom_bounds(form, ranges);
            let zero = BigInt::from(0);
            match relation {
                Relation::Lt => (min < zero, max < zero),
                Relation::Le => (min <= zero, max <= zero),
                Relation::Eq => (min <= zero && max >= zero, min == zero && max == zero),
                Relation::Ne => (min != zero || max != zero, min > zero || max < zero),
            }
        }
    }
}

/// Evaluate a separable condition with exact endpoint arithmetic. `ranges`
/// contains already-lowered coordinates; `scales` gives unit-grid powers of 10.
pub fn evaluate_risk_condition(value: &Value, ranges: &BTreeMap<String, Range>,
                               scales: &BTreeMap<String, BigInt>) -> Result<(bool, bool)> {
    if ranges.len() > 64 { return error("ResourceLimit", "risk quantities"); }
    for (id, range) in ranges {
        if range.lo > range.hi { return error("RiskRange", id.clone()); }
    }
    let mut counts = BTreeMap::new();
    let tree = condition(value, false, ranges, scales, &mut counts)?;
    let shared: BTreeSet<_> = counts.into_iter().filter(|(_, count)| *count > 1).map(|(id, _)| id).collect();
    if let Some(id) = shared.first() { return error("RiskConditionShared", id.clone()); }
    Ok(evaluate(&tree, ranges))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn exact_endpoints_and_collected_coefficients() {
        let box_ = BTreeMap::from([("q".into(), Range { tag: "count".into(), lo: 0.into(), hi: 1.into() })]);
        let scales = BTreeMap::from([("count".into(), 1.into())]);
        let q = json!(["quantity", "q"]);
        let zero = json!(["decimal", "count", "0"]);
        let one = json!(["decimal", "count", "1"]);
        assert_eq!(evaluate_risk_condition(&json!(["eq", ["add", "count", q,
            ["scale", "count", "-1", ["quantity", "q"]]], one]), &box_, &scales).unwrap(), (false, false));
        assert_eq!(evaluate_risk_condition(&json!(["not", ["eq", ["quantity", "q"], zero]]),
                                           &box_, &scales).unwrap(), (true, false));
    }

    #[test]
    fn shared_and_nonunit_equality_are_rejected() {
        let box_ = BTreeMap::from([("q".into(), Range { tag: "count".into(), lo: 0.into(), hi: 2.into() })]);
        let scales = BTreeMap::from([("count".into(), 1.into())]);
        let q = json!(["quantity", "q"]);
        let zero = json!(["decimal", "count", "0"]);
        let one = json!(["decimal", "count", "1"]);
        assert_eq!(evaluate_risk_condition(&json!(["and", ["lt", q, one],
            ["lt", ["quantity", "q"], one]]), &box_, &scales).unwrap_err().code, "RiskConditionShared");
        assert_eq!(evaluate_risk_condition(&json!(["eq", ["scale", "count", "2", q], zero]),
                                           &box_, &scales).unwrap_err().code, "RiskEqualityCoefficient");
    }
}
