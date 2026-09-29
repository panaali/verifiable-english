//! Untrusted stage-A condition evaluator for differential checks against Lean.
//! Coordinates are integers on their declared W6 grid; this module neither
//! admits a decision nor certifies a policy verdict.
use crate::{error, Error, Result};
use num_bigint::{BigInt, Sign};
use serde_json::{json, Value};
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

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Relation {
    Lt,
    Le,
    Eq,
    Ne,
}

#[derive(Clone, Debug)]
enum Condition {
    Atom(Form, Relation),
    And(Box<Self>, Box<Self>),
    Or(Box<Self>, Box<Self>),
    Top,
    Bottom,
}

fn shape<'a>(value: &'a Value) -> Result<(&'a str, &'a [Value])> {
    let parts = value
        .as_array()
        .ok_or_else(|| Error::new("InvalidInput", "risk condition node"))?;
    let name = parts
        .first()
        .and_then(Value::as_str)
        .ok_or_else(|| Error::new("InvalidInput", "risk condition tag"))?;
    Ok((name, parts))
}

fn text(value: &Value) -> Result<&str> {
    value
        .as_str()
        .ok_or_else(|| Error::new("InvalidInput", "risk condition string"))
}

fn integer(value: &Value) -> Result<BigInt> {
    let s = text(value)?;
    let digits = s.strip_prefix('-').unwrap_or(s);
    if digits.is_empty()
        || digits.len() > 40
        || (digits.len() > 1 && digits.starts_with('0'))
        || s == "-0"
        || !digits.bytes().all(|b| b.is_ascii_digit())
    {
        return error("InvalidInput", "risk coefficient");
    }
    s.parse()
        .map_err(|_| Error::new("InvalidInput", "risk coefficient"))
}

fn decimal(value: &Value, tag: &str, scales: &BTreeMap<String, BigInt>) -> Result<BigInt> {
    let s = text(value)?;
    let unsigned = s.strip_prefix('-').unwrap_or(s);
    let halves: Vec<_> = unsigned.split('.').collect();
    if halves.is_empty()
        || halves.len() > 2
        || halves[0].is_empty()
        || (halves[0].len() > 1 && halves[0].starts_with('0'))
        || halves
            .iter()
            .any(|part| part.is_empty() || !part.bytes().all(|b| b.is_ascii_digit()))
        || s.starts_with("-0") && unsigned == "0"
        || unsigned.len() > 41
    {
        return error("InvalidInput", "risk decimal");
    }
    let scale = if tag == "dimensionless" {
        BigInt::from(1)
    } else {
        scales
            .get(tag)
            .cloned()
            .ok_or_else(|| Error::new("UnknownSymbol", format!("unit {tag}")))?
    };
    let places = if halves.len() == 2 {
        halves[1].len()
    } else {
        0
    };
    if halves.iter().map(|x| x.len()).sum::<usize>() > 40 {
        return error("ResourceLimit", "risk decimal digits");
    }
    let numerator: BigInt = halves
        .concat()
        .parse()
        .map_err(|_| Error::new("InvalidInput", "risk decimal"))?;
    let divisor = BigInt::from(10).pow(places as u32);
    let scaled = numerator * scale;
    if &scaled % &divisor != BigInt::from(0) {
        return error("UnitPrecision", format!("{tag}, scale"));
    }
    let coordinate = scaled / divisor;
    Ok(if s.starts_with('-') {
        -coordinate
    } else {
        coordinate
    })
}

fn add(left: Form, right: Form) -> Result<Form> {
    if left.tag != right.tag {
        return error("UnitMismatch", format!("{},{}", left.tag, right.tag));
    }
    let mut coefficients = left.coefficients;
    for (name, coefficient) in right.coefficients {
        *coefficients.entry(name).or_default() += coefficient;
    }
    coefficients.retain(|_, coefficient| *coefficient != BigInt::from(0));
    Ok(Form {
        tag: left.tag,
        coefficients,
        constant: left.constant + right.constant,
    })
}

fn scale(mut form: Form, coefficient: BigInt) -> Form {
    form.constant *= &coefficient;
    for value in form.coefficients.values_mut() {
        *value *= &coefficient;
    }
    form.coefficients
        .retain(|_, value| *value != BigInt::from(0));
    form
}

fn term(
    value: &Value,
    ranges: &BTreeMap<String, Range>,
    scales: &BTreeMap<String, BigInt>,
) -> Result<Form> {
    let (name, parts) = shape(value)?;
    match (name, parts.len()) {
        ("quantity", 2) => {
            let id = text(&parts[1])?;
            let range = ranges
                .get(id)
                .ok_or_else(|| Error::new("RiskUnestimated", id))?;
            Ok(Form {
                tag: range.tag.clone(),
                coefficients: BTreeMap::from([(id.to_owned(), BigInt::from(1))]),
                constant: BigInt::from(0),
            })
        }
        ("decimal", 3) => {
            let tag = text(&parts[1])?;
            Ok(Form {
                tag: tag.to_owned(),
                coefficients: BTreeMap::new(),
                constant: decimal(&parts[2], tag, scales)?,
            })
        }
        ("add", 4) => {
            let tag = text(&parts[1])?;
            let result = add(
                term(&parts[2], ranges, scales)?,
                term(&parts[3], ranges, scales)?,
            )?;
            if result.tag != tag {
                return error("UnitMismatch", format!("{tag},{}", result.tag));
            }
            Ok(result)
        }
        ("scale", 4) => {
            let tag = text(&parts[1])?;
            let result = scale(term(&parts[3], ranges, scales)?, integer(&parts[2])?);
            if result.tag != tag {
                return error("UnitMismatch", format!("{tag},{}", result.tag));
            }
            Ok(result)
        }
        _ => error("InvalidInput", "risk term"),
    }
}

fn condition(
    value: &Value,
    negated: bool,
    ranges: &BTreeMap<String, Range>,
    scales: &BTreeMap<String, BigInt>,
) -> Result<Condition> {
    let (name, parts) = shape(value)?;
    match (name, parts.len()) {
        ("top", 1) => Ok(if negated {
            Condition::Bottom
        } else {
            Condition::Top
        }),
        ("bottom", 1) => Ok(if negated {
            Condition::Top
        } else {
            Condition::Bottom
        }),
        ("not", 2) => condition(&parts[1], !negated, ranges, scales),
        ("and" | "or", 3) => {
            let left = condition(&parts[1], negated, ranges, scales)?;
            let right = condition(&parts[2], negated, ranges, scales)?;
            Ok(if (name == "and") != negated {
                Condition::And(Box::new(left), Box::new(right))
            } else {
                Condition::Or(Box::new(left), Box::new(right))
            })
        }
        ("lt" | "le" | "eq", 3) => {
            let left = term(&parts[1], ranges, scales)?;
            let right = scale(term(&parts[2], ranges, scales)?, BigInt::from(-1));
            let mut form = add(left, right)?;
            let relation = match (name, negated) {
                ("lt", false) => Relation::Lt,
                ("le", false) => Relation::Le,
                ("eq", false) => Relation::Eq,
                ("eq", true) => Relation::Ne,
                ("lt", true) => Relation::Le,
                _ => Relation::Lt,
            };
            if negated && name != "eq" {
                form = scale(form, BigInt::from(-1));
            }
            Ok(Condition::Atom(form, relation))
        }
        _ => error("InvalidInput", "risk condition"),
    }
}

/// Lean's `LinForm`: coefficients in written order, uncollected until an atom
/// is built.
#[derive(Clone, Debug, PartialEq, Eq)]
struct Linear {
    coefficients: Vec<(String, BigInt)>,
    constant: BigInt,
}

/// Lean's elaborated `Cond` (lean/VE/Risk/Record.lean `elabCond`): the tree as
/// written, no negation normal form, atoms over `LinForm.normalize`d forms.
/// Used only for the structural `decide (S = N)` of `cellObs`.
#[derive(Clone, Debug, PartialEq, Eq)]
enum Structural {
    Top,
    Bottom,
    Atom(Linear, Relation),
    And(Box<Self>, Box<Self>),
    Or(Box<Self>, Box<Self>),
    Not(Box<Self>),
}

impl Structural {
    /// Lean's `atomsOf`: atoms left to right, through `not`.
    fn atoms<'a>(&'a self, out: &mut Vec<(&'a Linear, Relation)>) {
        match self {
            Structural::Top | Structural::Bottom => {}
            Structural::Atom(form, relation) => out.push((form, *relation)),
            Structural::And(a, b) | Structural::Or(a, b) => {
                a.atoms(out);
                b.atoms(out);
            }
            Structural::Not(a) => a.atoms(out),
        }
    }
}

impl Linear {
    fn scaled(self, k: &BigInt) -> Self {
        Linear {
            coefficients: self
                .coefficients
                .into_iter()
                .map(|(name, c)| (name, k * c))
                .collect(),
            constant: k * self.constant,
        }
    }

    /// `LinForm.normalize`: collect per name in first-occurrence order, then
    /// drop zero coefficients.
    fn normalize(self) -> Self {
        let mut collected: Vec<(String, BigInt)> = Vec::new();
        for (name, c) in self.coefficients {
            match collected.iter_mut().find(|(seen, _)| *seen == name) {
                Some((_, total)) => *total += c,
                None => collected.push((name, c)),
            }
        }
        collected.retain(|(_, c)| *c != BigInt::from(0));
        Linear {
            coefficients: collected,
            constant: self.constant,
        }
    }
}

fn structural_term(
    value: &Value,
    ranges: &BTreeMap<String, Range>,
    scales: &BTreeMap<String, BigInt>,
) -> Result<(String, Linear)> {
    let (name, parts) = shape(value)?;
    match (name, parts.len()) {
        ("quantity", 2) => {
            let id = text(&parts[1])?;
            let range = ranges
                .get(id)
                .ok_or_else(|| Error::new("RiskUnestimated", id))?;
            Ok((
                range.tag.clone(),
                Linear {
                    coefficients: vec![(id.to_owned(), BigInt::from(1))],
                    constant: BigInt::from(0),
                },
            ))
        }
        ("decimal", 3) => {
            let tag = text(&parts[1])?;
            Ok((
                tag.to_owned(),
                Linear {
                    coefficients: Vec::new(),
                    constant: decimal(&parts[2], tag, scales)?,
                },
            ))
        }
        ("add", 4) => {
            let tag = text(&parts[1])?;
            let (ta, mut fa) = structural_term(&parts[2], ranges, scales)?;
            let (tb, fb) = structural_term(&parts[3], ranges, scales)?;
            for t in [&ta, &tb] {
                if t != tag {
                    return error("UnitMismatch", format!("{tag},{t}"));
                }
            }
            fa.coefficients.extend(fb.coefficients);
            fa.constant += fb.constant;
            Ok((tag.to_owned(), fa))
        }
        ("scale", 4) => {
            let tag = text(&parts[1])?;
            let k = integer(&parts[2])?;
            let (ta, fa) = structural_term(&parts[3], ranges, scales)?;
            if ta != tag {
                return error("UnitMismatch", format!("{tag},{ta}"));
            }
            Ok((tag.to_owned(), fa.scaled(&k)))
        }
        _ => error("InvalidInput", "risk term"),
    }
}

fn structural(
    value: &Value,
    ranges: &BTreeMap<String, Range>,
    scales: &BTreeMap<String, BigInt>,
) -> Result<Structural> {
    let (name, parts) = shape(value)?;
    let sub = |i: usize| structural(&parts[i], ranges, scales).map(Box::new);
    match (name, parts.len()) {
        ("top", 1) => Ok(Structural::Top),
        ("bottom", 1) => Ok(Structural::Bottom),
        ("not", 2) => Ok(Structural::Not(sub(1)?)),
        ("and", 3) => Ok(Structural::And(sub(1)?, sub(2)?)),
        ("or", 3) => Ok(Structural::Or(sub(1)?, sub(2)?)),
        ("lt" | "le" | "eq", 3) => {
            let relation = match name {
                "lt" => Relation::Lt,
                "le" => Relation::Le,
                _ => Relation::Eq,
            };
            let (ta, mut fa) = structural_term(&parts[1], ranges, scales)?;
            let (tb, fb) = structural_term(&parts[2], ranges, scales)?;
            if ta != tb {
                return error("UnitMismatch", format!("{ta},{tb}"));
            }
            let fb = fb.scaled(&BigInt::from(-1));
            fa.coefficients.extend(fb.coefficients);
            fa.constant += fb.constant;
            Ok(Structural::Atom(fa.normalize(), relation))
        }
        _ => error("InvalidInput", "risk condition"),
    }
}

/// V8's sameness test, `decide (S = N)` over Lean's elaborated conditions.
/// If either side fails to elaborate, the raw comparison is kept so the
/// evaluation path below reports the error exactly as before.
fn same_condition(
    sufficient: &Value,
    necessary: &Value,
    ranges: &BTreeMap<String, Range>,
    scales: &BTreeMap<String, BigInt>,
) -> bool {
    match (
        structural(sufficient, ranges, scales),
        structural(necessary, ranges, scales),
    ) {
        (Ok(s), Ok(n)) => s == n,
        _ => sufficient == necessary,
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
        Condition::Top => (true, true),
        Condition::Bottom => (false, false),
        Condition::And(a, b) => {
            let x = evaluate(a, ranges);
            let y = evaluate(b, ranges);
            (x.0 && y.0, x.1 && y.1)
        }
        Condition::Or(a, b) => {
            let x = evaluate(a, ranges);
            let y = evaluate(b, ranges);
            (x.0 || y.0, x.1 || y.1)
        }
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
pub fn evaluate_risk_condition(
    value: &Value,
    ranges: &BTreeMap<String, Range>,
    scales: &BTreeMap<String, BigInt>,
) -> Result<(bool, bool)> {
    if ranges.len() > 64 {
        return error("ResourceLimit", "risk quantities");
    }
    for (tag, scale) in scales {
        let digits = scale.to_string();
        if digits.len() > 40 || !digits.starts_with('1') || !digits[1..].bytes().all(|b| b == b'0')
        {
            return error("UnitScale", tag.clone());
        }
    }
    for (id, range) in ranges {
        if range.lo > range.hi {
            return error("RiskRange", id.clone());
        }
        if range.tag != "dimensionless" && !scales.contains_key(&range.tag) {
            return error("UnknownSymbol", format!("unit {}", range.tag));
        }
    }
    // V7 in Lean's order (Record.lean `checkConditions`): scope (elaboration
    // reports an unranged quantity as RiskUnestimated), then `sharedName`,
    // then `unitBad`, both read in atom order with names in normalised
    // first-occurrence order. `nnf` keeps that order and only flips lt/le and
    // eq/ne and coefficient signs, so the written tree is read directly.
    let written = structural(value, ranges, scales)?;
    let mut atoms = Vec::new();
    written.atoms(&mut atoms);
    let is_point = |id: &str| ranges[id].lo == ranges[id].hi;
    let names: Vec<&str> = atoms
        .iter()
        .flat_map(|(form, _)| form.coefficients.iter().map(|(id, _)| id.as_str()))
        .collect();
    if let Some(id) = names
        .iter()
        .find(|id| !is_point(id) && names.iter().filter(|other| other == id).count() > 1)
    {
        return error("RiskConditionShared", *id);
    }
    let unit = |c: &BigInt| *c == BigInt::from(1) || *c == BigInt::from(-1);
    if let Some(id) = atoms
        .iter()
        .filter(|(_, relation)| matches!(relation, Relation::Eq | Relation::Ne))
        .find_map(|(form, _)| {
            form.coefficients
                .iter()
                .find(|(id, c)| !is_point(id) && !unit(c))
                .map(|(id, _)| id)
        })
    {
        return error("RiskEqualityCoefficient", id.clone());
    }
    let tree = condition(value, false, ranges, scales)?;
    Ok(evaluate(&tree, ranges))
}

/// Regenerate marginal `might` and `leads` cells from admitted source sides.
/// This accepts a prepared differential input, not a raw decision or policy.
/// The Lean route remains responsible for authentication and all verdicts.
pub fn regenerate_risk_cells(
    input: &Value,
    ranges: &BTreeMap<String, Range>,
    scales: &BTreeMap<String, BigInt>,
) -> Result<Value> {
    let object = input
        .as_object()
        .ok_or_else(|| Error::new("InvalidInput", "risk cells"))?;
    let names = |key| -> Result<Vec<String>> {
        object
            .get(key)
            .and_then(Value::as_array)
            .ok_or_else(|| Error::new("InvalidInput", format!("risk {key}")))?
            .iter()
            .map(|item| {
                item.as_str()
                    .map(str::to_owned)
                    .ok_or_else(|| Error::new("InvalidInput", format!("risk {key}")))
            })
            .collect()
    };
    let actions = names("alternatives")?;
    let harms = names("harms")?;
    if actions.len() > 16 || harms.len() > 32 {
        return error("ResourceLimit", "risk cells");
    }
    let classes = object
        .get("classes")
        .and_then(Value::as_object)
        .ok_or_else(|| Error::new("InvalidInput", "risk classes"))?;
    let always: BTreeSet<_> = names("always_possible")?.into_iter().collect();
    let unexamined = object
        .get("unexamined")
        .ok_or_else(|| Error::new("InvalidInput", "risk unexamined"))?;
    if unexamined != "possible"
        && unexamined
            .get("ruled_out_by")
            .and_then(Value::as_str)
            .is_none()
    {
        return error("InvalidInput", "risk unexamined");
    }
    let sources = object
        .get("cells")
        .and_then(Value::as_array)
        .ok_or_else(|| Error::new("InvalidInput", "risk cells"))?;
    let mut by_cell = BTreeMap::new();
    for source in sources {
        let action = source
            .get("action")
            .and_then(Value::as_str)
            .ok_or_else(|| Error::new("InvalidInput", "risk cell action"))?;
        let harm = source
            .get("harm")
            .and_then(Value::as_str)
            .ok_or_else(|| Error::new("InvalidInput", "risk cell harm"))?;
        if !actions.iter().any(|name| name == action) || !harms.iter().any(|name| name == harm) {
            return error("UnknownSymbol", format!("risk cell {action}/{harm}"));
        }
        if by_cell.insert((action, harm), source).is_some() {
            return error("RiskTwoSources", format!("{action}/{harm}"));
        }
    }
    let top = json!(["top"]);
    let bottom = json!(["bottom"]);
    let mut cells = Vec::new();
    for action in &actions {
        for harm in &harms {
            let source = by_cell.get(&(action.as_str(), harm.as_str())).copied();
            let addressed = source.is_some();
            let sufficient = source.and_then(|s| s.get("sufficient")).unwrap_or(&bottom);
            let default_possible = unexamined == "possible"
                || classes
                    .get(harm)
                    .and_then(Value::as_str)
                    .is_some_and(|klass| always.contains(klass));
            let unaddressed_necessary = if default_possible { &top } else { &bottom };
            let necessary = source
                .and_then(|s| s.get("necessary"))
                .unwrap_or(if addressed {
                    &top
                } else {
                    unaddressed_necessary
                });
            cells.push((action, harm, source, sufficient, necessary));
        }
    }
    // Lean's pass order: V7 on every side's own condition checks, then V8 on
    // every cell, then the stated-might check on every cell.
    let mut values = Vec::new();
    for (_, _, _, sufficient, necessary) in &cells {
        let leads = evaluate_risk_condition(sufficient, ranges, scales)?.1;
        let might = evaluate_risk_condition(necessary, ranges, scales)?.0;
        values.push((might, leads));
    }
    for (action, harm, _, sufficient, necessary) in &cells {
        if !same_condition(sufficient, necessary, ranges, scales) {
            let inconsistency = json!(["and", sufficient, ["not", necessary]]);
            if evaluate_risk_condition(&inconsistency, ranges, scales)?.0 {
                return error("SufficientOutsideNecessary", format!("{action}/{harm}"));
            }
        }
    }
    let mut rows = Vec::new();
    for ((action, harm, source, _, _), (might, leads)) in cells.iter().zip(values) {
        if source
            .and_then(|s| s.get("stated_might"))
            .and_then(Value::as_bool)
            == Some(true)
            && !might
        {
            return error("RiskInconsistent", format!("{action}/{harm}"));
        }
        rows.push(
            json!({"action":action,"harm":harm,"might":might,"leads":leads,
            "unexamined":source.is_none()}),
        );
    }
    Ok(json!(rows))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn exact_endpoints_and_collected_coefficients() {
        let box_ = BTreeMap::from([(
            "q".into(),
            Range {
                tag: "count".into(),
                lo: 0.into(),
                hi: 1.into(),
            },
        )]);
        let scales = BTreeMap::from([("count".into(), 1.into())]);
        let q = json!(["quantity", "q"]);
        let zero = json!(["decimal", "count", "0"]);
        let one = json!(["decimal", "count", "1"]);
        assert_eq!(
            evaluate_risk_condition(
                &json!([
                    "eq",
                    [
                        "add",
                        "count",
                        q,
                        ["scale", "count", "-1", ["quantity", "q"]]
                    ],
                    one
                ]),
                &box_,
                &scales
            )
            .unwrap(),
            (false, false)
        );
        assert_eq!(
            evaluate_risk_condition(
                &json!(["not", ["eq", ["quantity", "q"], zero]]),
                &box_,
                &scales
            )
            .unwrap(),
            (true, false)
        );
    }

    #[test]
    fn shared_and_nonunit_equality_are_rejected() {
        let box_ = BTreeMap::from([(
            "q".into(),
            Range {
                tag: "count".into(),
                lo: 0.into(),
                hi: 2.into(),
            },
        )]);
        let scales = BTreeMap::from([("count".into(), 1.into())]);
        let q = json!(["quantity", "q"]);
        let zero = json!(["decimal", "count", "0"]);
        let one = json!(["decimal", "count", "1"]);
        assert_eq!(
            evaluate_risk_condition(
                &json!(["and", ["lt", q, one], ["lt", ["quantity", "q"], one]]),
                &box_,
                &scales
            )
            .unwrap_err()
            .code,
            "RiskConditionShared"
        );
        assert_eq!(
            evaluate_risk_condition(
                &json!(["eq", ["scale", "count", "2", q], zero]),
                &box_,
                &scales
            )
            .unwrap_err()
            .code,
            "RiskEqualityCoefficient"
        );
    }

    #[test]
    fn source_defaults_and_precaution_are_marginal() {
        let ranges = BTreeMap::from([(
            "q".into(),
            Range {
                tag: "count".into(),
                lo: 0.into(),
                hi: 1.into(),
            },
        )]);
        let scales = BTreeMap::from([("count".into(), 1.into())]);
        let record = json!({"alternatives":["run","wait"],"harms":["outage"],
            "classes":{"outage":"severe"},"always_possible":["severe"],
            "unexamined":{"ruled_out_by":"team"},
            "cells":[{"action":"run","harm":"outage",
                "necessary":["lt",["quantity","q"],["decimal","count","1"]]}]});
        let rows = regenerate_risk_cells(&record, &ranges, &scales).unwrap();
        assert_eq!(rows[0]["might"], true);
        assert_eq!(rows[0]["leads"], false);
        assert_eq!(rows[1]["might"], true);
        assert_eq!(rows[1]["unexamined"], true);
    }

    fn gb_ranges() -> (BTreeMap<String, Range>, BTreeMap<String, BigInt>) {
        let range = |lo: i64, hi: i64| Range {
            tag: "gb".into(),
            lo: lo.into(),
            hi: hi.into(),
        };
        (
            BTreeMap::from([
                ("peak".into(), range(6, 12)),
                ("a".into(), range(0, 4)),
                ("b".into(), range(0, 4)),
                ("other".into(), range(0, 4)),
            ]),
            BTreeMap::from([("gb".into(), 1.into())]),
        )
    }

    fn one_cell(sufficient: Value, necessary: Value) -> Value {
        json!({"alternatives":["run"],"harms":["outage"],
            "classes":{"outage":"severe"},"always_possible":[],
            "unexamined":"possible",
            "cells":[{"action":"run","harm":"outage",
                "sufficient":sufficient,"necessary":necessary}]})
    }

    #[test]
    fn sameness_is_structural_over_elaborated_conditions() {
        let (ranges, scales) = gb_ranges();
        let peak = json!(["quantity", "peak"]);
        let s = json!(["lt", ["decimal", "gb", "8"], peak]);
        let n = json!(["lt", ["decimal", "gb", "8.0"], peak]);
        assert!(same_condition(&s, &n, &ranges, &scales));
        let rows = regenerate_risk_cells(&one_cell(s.clone(), n), &ranges, &scales).unwrap();
        assert_eq!(rows[0]["might"], true);
        assert_eq!(
            rows[0]["leads"],
            evaluate_risk_condition(&s, &ranges, &scales).unwrap().1
        );
        assert_eq!(rows[0]["leads"], false);
        assert!(same_condition(
            &json!(["top"]),
            &json!(["top"]),
            &ranges,
            &scales
        ));
        assert!(!same_condition(
            &json!(["top"]),
            &json!(["bottom"]),
            &ranges,
            &scales
        ));
    }

    #[test]
    fn coefficient_order_is_part_of_sameness() {
        let (ranges, scales) = gb_ranges();
        let zero = json!(["decimal", "gb", "0"]);
        let s = json!([
            "lt",
            ["add", "gb", ["quantity", "a"], ["quantity", "b"]],
            zero
        ]);
        let n = json!([
            "lt",
            ["add", "gb", ["quantity", "b"], ["quantity", "a"]],
            zero
        ]);
        assert!(!same_condition(&s, &n, &ranges, &scales));
        assert_eq!(
            regenerate_risk_cells(&one_cell(s, n), &ranges, &scales)
                .unwrap_err()
                .code,
            "RiskConditionShared"
        );
    }

    #[test]
    fn negation_is_kept_structurally() {
        let (ranges, scales) = gb_ranges();
        let s = json!(["lt", ["decimal", "gb", "8"], ["quantity", "peak"]]);
        let n = json!(["not", ["not", s]]);
        assert!(!same_condition(&s, &n, &ranges, &scales));
        assert_eq!(
            regenerate_risk_cells(&one_cell(s, n), &ranges, &scales)
                .unwrap_err()
                .code,
            "RiskConditionShared"
        );
    }

    #[test]
    fn zero_scaled_terms_are_collected_away() {
        let (ranges, scales) = gb_ranges();
        let peak = json!(["quantity", "peak"]);
        let eight = json!(["decimal", "gb", "8"]);
        let padded = |k: &str| {
            json!([
                "lt",
                [
                    "add",
                    "gb",
                    eight,
                    ["scale", "gb", k, ["quantity", "other"]]
                ],
                peak
            ])
        };
        let n = json!(["lt", eight, peak]);
        assert!(same_condition(&padded("0"), &n, &ranges, &scales));
        assert!(!same_condition(&padded("1"), &n, &ranges, &scales));
        let rows = regenerate_risk_cells(&one_cell(padded("0"), n), &ranges, &scales).unwrap();
        assert_eq!(rows[0]["might"], true);
        assert_eq!(rows[0]["leads"], false);
        // Collection happens within an atom: q - q cancels to the constant.
        let cancelled = json!([
            "lt",
            [
                "add",
                "gb",
                eight,
                ["add", "gb", peak, ["scale", "gb", "-1", peak]]
            ],
            ["decimal", "gb", "9"]
        ]);
        let constant = json!(["lt", eight, ["decimal", "gb", "9"]]);
        assert!(same_condition(&cancelled, &constant, &ranges, &scales));
    }

    #[test]
    fn shared_name_is_first_in_atom_order() {
        let range = |lo: i64, hi: i64| Range {
            tag: "gb".into(),
            lo: lo.into(),
            hi: hi.into(),
        };
        let ranges = BTreeMap::from([
            ("peak_memory".into(), range(6, 12)),
            ("free_memory".into(), range(8, 10)),
        ]);
        let scales = BTreeMap::from([("gb".into(), 1.into())]);
        let peak = json!(["quantity", "peak_memory"]);
        let free = json!(["quantity", "free_memory"]);
        let twenty = json!(["decimal", "gb", "20"]);
        let s = json!(["lt", ["add", "gb", peak, free], twenty]);
        let n = json!(["lt", ["add", "gb", free, peak], twenty]);
        let err = regenerate_risk_cells(&one_cell(s, n), &ranges, &scales).unwrap_err();
        assert_eq!(err.code, "RiskConditionShared");
        assert_eq!(err.message, "peak_memory");
    }

    #[test]
    fn shared_is_reported_before_equality_coefficient() {
        let (ranges, scales) = gb_ranges();
        let a = json!(["quantity", "a"]);
        let one = json!(["decimal", "gb", "1"]);
        let condition = json!([
            "and",
            [
                "eq",
                ["scale", "gb", "2", ["quantity", "b"]],
                ["decimal", "gb", "0"]
            ],
            ["and", ["lt", a, one], ["le", a, one]]
        ]);
        let err = evaluate_risk_condition(&condition, &ranges, &scales).unwrap_err();
        assert_eq!(err.code, "RiskConditionShared");
        assert_eq!(err.message, "a");
    }

    #[test]
    fn equality_coefficient_names_first_occurrence() {
        let (mut ranges, scales) = gb_ranges();
        ranges.insert(
            "fixed".into(),
            Range {
                tag: "gb".into(),
                lo: 3.into(),
                hi: 3.into(),
            },
        );
        // Points are skipped; among the rest, `peak` precedes `a` as written.
        let condition = json!([
            "and",
            ["lt", ["quantity", "b"], ["decimal", "gb", "1"]],
            [
                "not",
                [
                    "eq",
                    [
                        "add",
                        "gb",
                        ["scale", "gb", "5", ["quantity", "fixed"]],
                        [
                            "add",
                            "gb",
                            ["scale", "gb", "2", ["quantity", "peak"]],
                            ["scale", "gb", "3", ["quantity", "a"]]
                        ]
                    ],
                    ["decimal", "gb", "0"]
                ]
            ]
        ]);
        let err = evaluate_risk_condition(&condition, &ranges, &scales).unwrap_err();
        assert_eq!(err.code, "RiskEqualityCoefficient");
        assert_eq!(err.message, "peak");
    }

    #[test]
    fn prepared_units_must_be_declared_grids() {
        let ranges = BTreeMap::from([(
            "q".into(),
            Range {
                tag: "count".into(),
                lo: 0.into(),
                hi: 1.into(),
            },
        )]);
        let condition = json!(["top"]);
        assert_eq!(
            evaluate_risk_condition(&condition, &ranges, &BTreeMap::new())
                .unwrap_err()
                .code,
            "UnknownSymbol"
        );
        assert_eq!(
            evaluate_risk_condition(
                &condition,
                &ranges,
                &BTreeMap::from([("count".into(), 2.into())])
            )
            .unwrap_err()
            .code,
            "UnitScale"
        );
    }
}
