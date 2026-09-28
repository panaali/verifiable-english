//! W6a ground-unit regeneration for Rust conformance. No proof certificates:
//! Rust regenerates, evaluates and checks countermodels; Lean certifies.
use crate::{Error, Result, digest, error, order_case};
use num_bigint::BigInt;
use serde_json::{Value, json};
use std::fmt;

const NUMBERS2: &str = "$int quantification requires the missing numbers2 route";
const POINTS_SUFFIX: &str = " percentage points";
/// Exactly the characters for which Python's `str.isspace()` holds.
fn is_space(c: char) -> bool {
    matches!(c as u32, 9..=13 | 28..=32 | 0x85 | 0xA0 | 0x1680 | 0x2000..=0x200A
        | 0x2028 | 0x2029 | 0x202F | 0x205F | 0x3000)
}

fn object(v: &Value) -> Result<&serde_json::Map<String, Value>> {
    v.as_object()
        .ok_or_else(|| Error::new("InvalidInput", "expected object"))
}
fn string(v: &Value) -> Result<&str> {
    v.as_str()
        .ok_or_else(|| Error::new("SyntaxError", "expected string"))
}
fn array(v: &Value) -> Result<&[Value]> {
    v.as_array()
        .map(Vec::as_slice)
        .ok_or_else(|| Error::new("SyntaxError", "expected array"))
}
fn shape(v: &Value, required: &[&str], optional: &[&str]) -> Result<()> {
    let o = object(v)?;
    if required.iter().any(|k| !o.contains_key(*k))
        || o.keys()
            .any(|k| !required.contains(&k.as_str()) && !optional.contains(&k.as_str()))
    {
        return error("InvalidInput", "unknown or missing quantity fields");
    }
    Ok(())
}
fn node(v: &Value) -> Result<(&str, &[Value])> {
    let a = array(v)?;
    Ok((
        string(
            a.first()
                .ok_or_else(|| Error::new("SyntaxError", "empty AST"))?,
        )?,
        a,
    ))
}
/// Every array node counts toward 10,000, as in Python's elaborator.
fn budget(v: &Value) -> Result<()> {
    let mut stack = vec![v];
    let mut count = 0usize;
    while let Some(value) = stack.pop() {
        if let Some(items) = value.as_array() {
            count += 1;
            if count > 10_000 {
                return error("ResourceLimit", "quantity AST exceeds node or depth limit");
            }
            stack.extend(items.iter().skip(1));
        }
    }
    Ok(())
}
fn int(s: &str) -> Result<BigInt> {
    if s.len() > 40 {
        return error("ResourceLimit", "integer literal exceeds 40 characters");
    }
    let digits = s.strip_prefix('-').unwrap_or(s);
    if digits.is_empty()
        || (digits.len() > 1 && digits.starts_with('0'))
        || s == "-0"
        || !digits.bytes().all(|b| b.is_ascii_digit())
    {
        return error("SyntaxError", "noncanonical integer literal");
    }
    s.parse()
        .map_err(|_| Error::new("SyntaxError", "invalid integer literal"))
}
fn unit<'a>(e: &'a Value, tag: &'a str) -> Result<&'a str> {
    if tag == "dimensionless" || e["units"].get(tag).is_some() {
        Ok(tag)
    } else {
        error("InvalidInput", format!("UnknownUnit({tag})"))
    }
}
fn scale(e: &Value, tag: &str) -> Result<BigInt> {
    if tag == "dimensionless" {
        return Ok(BigInt::from(1));
    }
    let record = &e["units"][tag];
    shape(record, &["scale", "display"], &[])?;
    let s = string(&record["scale"])?;
    let n = int(s)?;
    if !s.starts_with('1') || !s[1..].bytes().all(|b| b == b'0') {
        return error("InvalidInput", format!("UnitScale({tag})"));
    }
    Ok(n)
}
/// At most 40 digits, sign and point uncounted: every admitted coordinate
/// renders on every declared scale within that bound, so rendering reparses.
fn exact_decimal(e: &Value, tag: &str, s: &str) -> Result<String> {
    if s.bytes().filter(|b| b.is_ascii_digit()).count() > 40 {
        return error("ResourceLimit", "Decimal literal exceeds 40 digits");
    }
    let unsigned = s.strip_prefix('-').unwrap_or(s);
    let p: Vec<_> = unsigned.split('.').collect();
    if p.len() > 2
        || p[0].is_empty()
        || (p[0].len() > 1 && p[0].starts_with('0'))
        || !p
            .iter()
            .all(|x| !x.is_empty() && x.bytes().all(|b| b.is_ascii_digit()))
    {
        return error("SyntaxError", "invalid decimal literal");
    }
    let mut m: BigInt = p
        .join("")
        .parse()
        .map_err(|_| Error::new("SyntaxError", "invalid decimal"))?;
    if s.starts_with('-') {
        m = -m;
    }
    let divisor = BigInt::from(10).pow(if p.len() == 2 { p[1].len() as u32 } else { 0 });
    let grid = scale(e, tag)?;
    let x = m * grid.clone();
    if &x % &divisor != BigInt::from(0) {
        return error(
            "InvalidInput",
            format!("UnitPrecision({tag}, scale={grid})"),
        );
    }
    let n = (x / divisor).to_string();
    int(&n)?;
    Ok(n)
}
fn leap(y: i32) -> bool {
    y % 4 == 0 && (y % 100 != 0 || y % 400 == 0)
}
/// Calendar validity first (`InvalidDate`), then the supported interval
/// (`DateRange`), in Python's order.
fn date_number(s: &str) -> Result<String> {
    let b = s.as_bytes();
    if b.len() != 10
        || b[4] != b'-'
        || b[7] != b'-'
        || !b
            .iter()
            .enumerate()
            .all(|(i, x)| i == 4 || i == 7 || x.is_ascii_digit())
    {
        return error("InvalidInput", format!("InvalidDate({s})"));
    }
    let y: i32 = s[..4].parse().unwrap_or(0);
    let m: usize = s[5..7].parse().unwrap_or(0);
    let d: i32 = s[8..].parse().unwrap_or(0);
    let days = [
        31,
        if leap(y) { 29 } else { 28 },
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ];
    if y < 1 || !(1..=12).contains(&m) || d < 1 || d > days[m - 1] {
        return error("InvalidInput", format!("InvalidDate({s})"));
    }
    if y < 1970 {
        return error("InvalidInput", format!("DateRange({s})"));
    }
    let years = (1970..y)
        .map(|v| if leap(v) { 366 } else { 365 })
        .sum::<i32>();
    Ok((years + days[..m - 1].iter().sum::<i32>() + d - 1).to_string())
}

/// Statement types: unit tags and user sorts are separate namespaces.
#[derive(Clone, PartialEq, Eq, Debug)]
enum Ty {
    Unit(String),
    Sort(String),
}
impl fmt::Display for Ty {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Ty::Unit(t) => write!(f, "unit {t}"),
            Ty::Sort(s) => write!(f, "sort {s}"),
        }
    }
}
fn same(a: &Ty, b: &Ty) -> Result<()> {
    match (a, b) {
        _ if a == b => Ok(()),
        (Ty::Unit(x), Ty::Unit(y)) => error("TypeMismatch", format!("UnitMismatch({x},{y})")),
        _ => error("TypeMismatch", format!("TypeMismatch({a},{b})")),
    }
}
fn quantity(tag: &str) -> Ty {
    Ty::Unit(tag.to_owned())
}
fn depth_ok(depth: usize) -> Result<()> {
    if depth > 64 {
        return error("ResourceLimit", "quantity AST exceeds node or depth limit");
    }
    Ok(())
}
/// Term depth is counted from each atom, separately from formula depth.
fn term(e: &Value, v: &Value, ctx: &[String], depth: usize) -> Result<(Ty, Value, Value)> {
    depth_ok(depth)?;
    let (op, a) = node(v)?;
    match (op, a.len()) {
        ("var", 2) => {
            let i = a[1]
                .as_u64()
                .ok_or_else(|| Error::new("UnboundVariable", "invalid index"))?;
            let sort = ctx
                .get(i as usize)
                .ok_or_else(|| Error::new("UnboundVariable", "unbound index"))?;
            Ok((Ty::Sort(sort.clone()), v.clone(), v.clone()))
        }
        ("var", 3) => error("UnsupportedProfile", NUMBERS2),
        ("const", 2 | 3) => {
            let name = string(a.last().unwrap())?;
            let d = e["vocabulary"]["constants"]
                .get(name)
                .ok_or_else(|| Error::new("UnknownSymbol", "unknown quantity constant"))?;
            let sort = string(&d["sort"])?;
            if sort != "$int" {
                if a.len() != 2 {
                    return error("TypeMismatch", "unit on object constant");
                }
                return Ok((Ty::Sort(sort.into()), v.clone(), v.clone()));
            }
            let tag = if a.len() == 3 {
                unit(e, string(&a[1])?)?
            } else {
                "dimensionless"
            };
            same(
                &quantity(tag),
                &quantity(
                    d.get("unit")
                        .and_then(Value::as_str)
                        .unwrap_or("dimensionless"),
                ),
            )?;
            Ok((
                quantity(tag),
                json!(["const", tag, name]),
                json!(["const", name]),
            ))
        }
        ("num", 2) => {
            let n = int(string(&a[1])?)?.to_string();
            Ok((
                quantity("dimensionless"),
                json!(["num", "dimensionless", n]),
                json!(["num", n]),
            ))
        }
        ("num" | "decimal", 3) => {
            let tag = unit(e, string(&a[1])?)?;
            let n = if op == "num" {
                int(string(&a[2])?)?.to_string()
            } else {
                exact_decimal(e, tag, string(&a[2])?)?
            };
            Ok((quantity(tag), json!(["num", tag, n]), json!(["num", n])))
        }
        ("date", 2) => {
            unit(e, "day")?;
            let n = date_number(string(&a[1])?)?;
            Ok((quantity("day"), json!(["num", "day", n]), json!(["num", n])))
        }
        ("add", 3 | 4) => {
            let (tag, l, r) = if a.len() == 4 {
                (unit(e, string(&a[1])?)?, &a[2], &a[3])
            } else {
                ("dimensionless", &a[1], &a[2])
            };
            let (lt, lq, lc) = term(e, l, ctx, depth + 1)?;
            let (rt, rq, rc) = term(e, r, ctx, depth + 1)?;
            same(&lt, &rt)?;
            same(&quantity(tag), &lt)?;
            if tag == "day" {
                return error("TypeMismatch", "Calendar dates cannot be added");
            }
            Ok((
                quantity(tag),
                json!(["add", tag, lq, rq]),
                json!(["add", lc, rc]),
            ))
        }
        ("scale", 3 | 4) => {
            let (tag, c, t) = if a.len() == 4 {
                (unit(e, string(&a[1])?)?, &a[2], &a[3])
            } else {
                ("dimensionless", &a[1], &a[2])
            };
            let c = int(string(c)?)?.to_string();
            let (tt, tq, tc) = term(e, t, ctx, depth + 1)?;
            same(&quantity(tag), &tt)?;
            if tag == "day" {
                return error("TypeMismatch", "Calendar dates cannot be scaled");
            }
            Ok((
                quantity(tag),
                json!(["scale", tag, c, tq]),
                json!(["scale", c, tc]),
            ))
        }
        _ => error("SyntaxError", "invalid quantity term"),
    }
}
fn guard(t: &Value) -> Value {
    json!([
        "and",
        ["le", ["num", "0"], t],
        ["le", t, ["num", "2932896"]]
    ])
}
fn temporal(e: &Value, op: &str, a: &[Value], ctx: &[String]) -> Result<(Value, Value)> {
    let three = ["within_days", "shift_days", "elapsed_days"].contains(&op);
    if a.len() != if three { 4 } else { 3 } {
        return error("InvalidInput", format!("Invalid {op} node"));
    }
    let (ta, qa, ca) = term(e, &a[1], ctx, 1)?;
    let (tb, qb, cb) = term(e, &a[2], ctx, 1)?;
    let day = quantity(unit(e, "day")?);
    same(&ta, &day)?;
    same(&tb, &day)?;
    let both = json!(["and", guard(&ca), guard(&cb)]);
    let (q, body) = match op {
        "date_on" => (json!([op, qa, qb]), json!(["eq", ca, cb])),
        "date_before" => (json!([op, qa, qb]), json!(["lt", ca, cb])),
        "date_after" => (json!([op, qa, qb]), json!(["lt", cb, ca])),
        "date_no_later" => (json!([op, qa, qb]), json!(["le", ca, cb])),
        "elapsed_days" => {
            let (tv, qv, cv) = term(e, &a[3], ctx, 1)?;
            same(&tv, &quantity(unit(e, "elapsed_day")?))?;
            (
                json!([op, qa, qb, qv]),
                json!(["eq", cv, ["add", cb, ["scale", "-1", ca]]]),
            )
        }
        "within_days" | "shift_days" => {
            let n = int(string(&a[3])?)?;
            if n < BigInt::from(0) {
                return error("InvalidInput", "Day offset must be nonnegative");
            }
            let n = n.to_string();
            let upper = json!(["add", cb, ["num", n]]);
            let body = if op == "within_days" {
                json!(["and", ["le", cb, ca], ["le", ca, upper]])
            } else {
                json!(["eq", ca, upper])
            };
            (json!([op, qa, qb, n]), body)
        }
        _ => return error("SyntaxError", "unknown temporal operation"),
    };
    Ok((q, json!(["and", both, body])))
}
fn formula(e: &Value, v: &Value, ctx: &[String], depth: usize) -> Result<(Value, Value)> {
    depth_ok(depth)?;
    let (op, a) = node(v)?;
    match (op, a.len()) {
        ("top" | "bottom", 1) => Ok((v.clone(), v.clone())),
        ("eq" | "lt" | "le", 3) => {
            let (lt, lq, lc) = term(e, &a[1], ctx, 1)?;
            let (rt, rq, rc) = term(e, &a[2], ctx, 1)?;
            same(&lt, &rt)?;
            if op != "eq" && !matches!(lt, Ty::Unit(_)) {
                return error("TypeMismatch", "order needs quantity terms");
            }
            Ok((json!([op, lq, rq]), json!([op, lc, rc])))
        }
        ("unary" | "binary", 3 | 4) if a.len() == (if op == "unary" { 3 } else { 4 }) => {
            let name = string(&a[1])?;
            let decl = e["vocabulary"]["predicates"]
                .get(name)
                .ok_or_else(|| Error::new("UnknownSymbol", "unknown predicate"))?;
            let signature = array(&decl["arguments"])?;
            if signature.len() != a.len() - 2 {
                return error("TypeMismatch", "predicate arity");
            }
            let mut q = vec![json!(op), json!(name)];
            let mut core = q.clone();
            for (i, arg) in a[2..].iter().enumerate() {
                let sort = string(&signature[i])?;
                let expected = if sort == "$int" {
                    quantity(
                        decl.get("argument_units")
                            .and_then(|m| m.get(i.to_string()))
                            .and_then(Value::as_str)
                            .unwrap_or("dimensionless"),
                    )
                } else {
                    Ty::Sort(sort.to_owned())
                };
                let (found, tq, tc) = term(e, arg, ctx, 1)?;
                same(&found, &expected)?;
                q.push(tq);
                core.push(tc);
            }
            Ok((json!(q), json!(core)))
        }
        ("atom", _) => error(
            "UnsupportedProfile",
            "n-ary atoms are not admitted on the order@0 quantity route",
        ),
        ("not", 2) => {
            let (q, c) = formula(e, &a[1], ctx, depth + 1)?;
            Ok((json!([op, q]), json!([op, c])))
        }
        ("and" | "or" | "implies", 3) => {
            let (lq, lc) = formula(e, &a[1], ctx, depth + 1)?;
            let (rq, rc) = formula(e, &a[2], ctx, depth + 1)?;
            Ok((json!([op, lq, rq]), json!([op, lc, rc])))
        }
        ("forall" | "exists", 3 | 4) if a[1] == "$int" => error("UnsupportedProfile", NUMBERS2),
        ("forall" | "exists", 3) => {
            let sort = string(&a[1])?;
            if e["vocabulary"]["sorts"].get(sort).is_none() {
                return error("InvalidInput", "Invalid quantity binder");
            }
            let mut next = vec![sort.to_owned()];
            next.extend_from_slice(ctx);
            let (q, c) = formula(e, &a[2], &next, depth + 1)?;
            Ok((json!([op, sort, q]), json!([op, sort, c])))
        }
        ("forall" | "exists", _) => error("InvalidInput", "Invalid quantity binder"),
        (
            "date_on" | "date_before" | "date_after" | "date_no_later" | "within_days"
            | "shift_days" | "elapsed_days",
            _,
        ) => temporal(e, op, a, ctx),
        (
            "sunday" | "excluded_sundays" | "forall_date" | "exists_date" | "trace_all"
            | "trace_some",
            _,
        ) => error("UnsupportedProfile", NUMBERS2),
        _ => error("InvalidInput", format!("Unknown quantity formula {op}")),
    }
}
/// Nonempty words of non-space characters joined by single spaces; an input
/// symbol may end in one space.
fn display_string(v: &Value, trailing_space: bool) -> Result<String> {
    spaced(v, trailing_space, "Display string")
}
fn spaced(v: &Value, trailing_space: bool, what: &str) -> Result<String> {
    let s = string(v)?;
    if s.is_empty() {
        return error("InvalidInput", format!("{what} must be nonempty"));
    }
    if s.chars().count() > 256 {
        return error("ResourceLimit", format!("{what} exceeds 256 characters"));
    }
    let mut words: Vec<&str> = s.split(' ').collect();
    if trailing_space && words.len() > 1 && words.last() == Some(&"") {
        words.pop();
    }
    if words.iter().any(|w| w.is_empty() || w.chars().any(is_space)) {
        return error(
            "InvalidInput",
            format!("{what} {s:?} must be whitespace-normalized"),
        );
    }
    Ok(s.to_owned())
}
/// Every enabled literal affix, canonical or alias: (is_prefix, text).
fn affixes(units: &serde_json::Map<String, Value>) -> Result<Vec<(bool, String)>> {
    let mut forms = vec![];
    for record in units.values() {
        let d = &record["display"];
        match string(&d["kind"])? {
            "percent" => {
                forms.push((false, "%".to_owned()));
                forms.push((false, POINTS_SUFFIX.to_owned()));
            }
            "money" => {
                forms.push((true, format!("{} ", string(&d["currency"])?)));
                if let Some(symbol) = d.get("input_symbol") {
                    forms.push((true, string(symbol)?.to_owned()));
                }
            }
            "decimal" => {
                let label = string(&d["label"])?;
                if d.get("placement") == Some(&json!("prefix")) {
                    forms.push((true, format!("{label} ")));
                } else {
                    forms.push((false, format!(" {label}")));
                }
            }
            _ => {}
        }
    }
    Ok(forms)
}
/// No affix touches the amount with a digit, sign or point, and no affix
/// extends another on the same side (Python `check_display_injective`).
fn display_injective(units: &serde_json::Map<String, Value>) -> Result<()> {
    let forms = affixes(units)?;
    let amount = |c: Option<char>| c.is_some_and(|c| c == '-' || c == '.' || c.is_ascii_digit());
    for (prefix, text) in &forms {
        let edge = if *prefix {
            text.chars().next()
        } else {
            text.chars().last()
        };
        if amount(edge) {
            return error("InvalidInput", format!("DisplayCollision({text:?} touches the amount)"));
        }
    }
    for (i, (prefix, text)) in forms.iter().enumerate() {
        for (other_prefix, other) in &forms[i + 1..] {
            let extends = prefix == other_prefix
                && if *prefix {
                    text.starts_with(other.as_str()) || other.starts_with(text.as_str())
                } else {
                    text.ends_with(other.as_str()) || other.ends_with(text.as_str())
                };
            if extends {
                return error("InvalidInput", format!("DisplayCollision({text:?}, {other:?})"));
            }
        }
    }
    Ok(())
}
fn declarations(e: &Value) -> Result<()> {
    shape(
        e,
        &[
            "language",
            "profiles",
            "spec_revision",
            "vocabulary",
            "unit_schema",
            "units",
        ],
        &[],
    )?;
    if e["language"] != "ve.core@0.2"
        || e["unit_schema"] != "ve-units@1"
        || e["spec_revision"] != "ve-v0.2-expand2-2026-09-25"
    {
        return error(
            "UnsupportedProfile",
            "quantity route requires ve-units@1 on ve.core@0.2",
        );
    }
    let profiles = &e["profiles"];
    if profiles != &json!(["order@0", "relational-fol@0", "time@0"])
        && profiles != &json!(["documents@1", "order@0", "relational-fol@0", "time@0"])
    {
        return error(
            "UnsupportedProfile",
            "ve-units@1 requires exactly order@0, relational-fol@0 and time@0, optionally with documents@1",
        );
    }
    let u = object(&e["units"])?;
    if u.len() > 64 {
        return error("ResourceLimit", "At most 64 unit tags");
    }
    for (tag, record) in u {
        if crate::environment::identifier(tag, "InvalidInput").is_err() || tag == "dimensionless" {
            return error("InvalidInput", format!("Invalid unit tag {tag:?}"));
        }
        scale(e, tag)?;
        let d = &record["display"];
        let kind = string(
            d.get("kind")
                .ok_or_else(|| Error::new("InvalidInput", "display kind missing"))?,
        )?;
        match kind {
            "percent" => shape(d, &["kind"], &[])?,
            "money" => {
                shape(d, &["kind", "currency"], &["input_symbol"])?;
                let c = string(&d["currency"])?;
                if c.len() != 3 || !c.bytes().all(|b| b.is_ascii_uppercase()) {
                    return error("InvalidInput", "invalid currency");
                }
                if let Some(symbol) = d.get("input_symbol") {
                    display_string(symbol, true)?;
                }
            }
            "decimal" => {
                shape(d, &["kind", "label"], &["placement"])?;
                display_string(&d["label"], false)?;
                let placement = d
                    .get("placement")
                    .map(string)
                    .transpose()?
                    .unwrap_or("suffix");
                if placement != "prefix" && placement != "suffix" {
                    return error("InvalidInput", "invalid placement");
                }
            }
            "iso_date" => {
                shape(d, &["kind"], &[])?;
                if tag != "day" || record["scale"] != "1" {
                    return error("InvalidInput", "iso_date requires day at scale 1");
                }
            }
            _ => return error("InvalidInput", "unknown display kind"),
        }
        if tag == "day" && record != &json!({"scale":"1","display":{"kind":"iso_date"}}) {
            return error("InvalidInput", "reserved day declaration");
        }
        if tag == "elapsed_day"
            && record != &json!({"scale":"1","display":{"kind":"decimal","label":"days"}})
        {
            return error("InvalidInput", "reserved elapsed_day declaration");
        }
    }
    display_injective(u)?;
    shape(&e["vocabulary"], &["sorts", "predicates", "constants"], &[])?;
    let sorts = object(&e["vocabulary"]["sorts"])?;
    for tag in std::iter::once("dimensionless").chain(u.keys().map(String::as_str)) {
        if sorts.contains_key(tag) {
            return error(
                "InvalidInput",
                format!("Unit tag {tag} collides with a declared sort"),
            );
        }
    }
    for (_, p) in object(&e["vocabulary"]["predicates"])? {
        if let Some(slots) = p.get("argument_units") {
            for (slot, u) in object(slots)? {
                let i: usize = slot
                    .parse()
                    .map_err(|_| Error::new("InvalidInput", "invalid argument unit slot"))?;
                if i.to_string() != *slot
                    || p["arguments"].as_array().and_then(|a| a.get(i)) != Some(&json!("$int"))
                {
                    return error("InvalidInput", "unit on invalid predicate slot");
                }
                unit(e, string(u)?)?;
            }
        }
    }
    let mut spellings = std::collections::HashMap::new();
    for (name, c) in object(&e["vocabulary"]["constants"])? {
        if c.get("sort") == Some(&json!("$string")) {
            return error(
                "UnsupportedProfile",
                "$string literals are not admitted with ve-units@1",
            );
        }
        if let Some(u) = c.get("unit") {
            if c["sort"] != "$int" {
                return error("InvalidInput", "unit on non-integer constant");
            }
            unit(e, string(u)?)?;
        }
        if let Some(words) = c.get("verbalisation") {
            // Normalized like a display string, and distinct from every other
            // constant's spelling even at the start of a sentence.
            let key = sentence_initial(&spaced(words, false, "Verbalisation")?);
            if let Some(other) = spellings.insert(key, name.clone()) {
                return error(
                    "InvalidInput",
                    format!("VerbalisationCollision({other}, {name})"),
                );
            }
        }
    }
    Ok(())
}
/// The sentence-initial spelling of a name: its first letter ASCII-uppercased.
fn sentence_initial(words: &str) -> String {
    let mut chars = words.chars();
    match chars.next() {
        Some(first) => first.to_ascii_uppercase().to_string() + chars.as_str(),
        None => String::new(),
    }
}
/// The regenerated core target environment: W6 declaration fields removed.
fn erased(e: &Value) -> Value {
    let mut target = e.clone();
    target.as_object_mut().unwrap().remove("unit_schema");
    target.as_object_mut().unwrap().remove("units");
    for c in target["vocabulary"]["constants"]
        .as_object_mut()
        .unwrap()
        .values_mut()
    {
        if let Some(c) = c.as_object_mut() {
            c.remove("unit");
            c.remove("verbalisation");
        }
    }
    for p in target["vocabulary"]["predicates"]
        .as_object_mut()
        .unwrap()
        .values_mut()
    {
        if let Some(p) = p.as_object_mut() {
            p.remove("argument_units");
        }
    }
    target
}
/// Decode one submitted quantity object; regenerate Q and the core formula.
fn quantity_payload(e: &Value, p: &Value) -> Result<(Value, Value)> {
    shape(p, &["format", "formula"], &["traces", "Q"])?;
    if p["format"] != "ve-quantity@1" {
        return error("UnsupportedProfile", "quantity format");
    }
    let traces = p.get("traces").cloned().unwrap_or(json!([]));
    if !array(&traces)?.is_empty() {
        return error(
            "UnsupportedProfile",
            "trace declarations require the missing numbers2 route",
        );
    }
    budget(&p["formula"])?;
    let (q, core) = formula(e, &p["formula"], &[], 1)?;
    if p.get("Q").is_some_and(|claimed| claimed != &q) {
        return error(
            "InvalidInput",
            "Quantity Q differs from regenerated formula",
        );
    }
    Ok((q, core))
}
/// Decode annotated source, regenerate Q and core, and validate the core AST.
/// This is evaluation-only and cannot certify a W6 claim. A `countermodel`
/// case takes annotated `premises` and `conclusion` instead of `quantity`.
pub fn quantity_case(v: &Value) -> Result<Value> {
    let countermodel = v.get("mode") == Some(&json!("countermodel"));
    if v.get("mode") == Some(&json!("document")) {
        return quantity_document(v);
    }
    if v.get("mode").is_some() && !countermodel {
        return error(
            "UnsupportedProfile",
            "Rust regenerates and evaluates quantities; Lean checks quantity certificates",
        );
    }
    if countermodel {
        shape(
            v,
            &["kind", "mode", "environment", "premises", "conclusion", "model"],
            &["id"],
        )?;
    } else {
        shape(v, &["kind", "environment", "quantity"], &["id", "model"])?;
    }
    if v["kind"] != "quantity" {
        return error("InvalidInput", "quantity kind required");
    }
    let e = v
        .get("environment")
        .ok_or_else(|| Error::new("InvalidInput", "environment missing"))?;
    declarations(e)?;
    let target = erased(e);
    let id = v.get("id").cloned().unwrap_or(json!(""));
    if countermodel {
        let mut premises = vec![];
        for p in array(&v["premises"])? {
            premises.push(quantity_payload(e, p)?.1);
        }
        let conclusion = quantity_payload(e, &v["conclusion"])?.1;
        let case = json!({"id":id,"kind":"countermodel","environment":target,
            "premises":premises,"conclusion":conclusion,"model":v["model"]});
        let checked = order_case(&case)?;
        return Ok(json!({"id":id,"status":"ok","assurance":"regeneration-only",
            "refutes":checked["valid"]}));
    }
    let p = v
        .get("quantity")
        .ok_or_else(|| Error::new("InvalidInput", "quantity missing"))?;
    let (q, core) = quantity_payload(e, p)?;
    let mut case = json!({"id":id,"kind":"evaluate","environment":target,"ast":[core.clone()]});
    if let Some(model) = v.get("model") {
        case["model"] = model.clone();
    }
    let checked = order_case(&case)?;
    let profiles = array(&e["profiles"])?;
    let version = format!(
        "v0.2:{}",
        profiles
            .iter()
            .map(|x| x.as_str().unwrap())
            .collect::<Vec<_>>()
            .join(",")
    );
    let environment_id = digest(&format!("ve-environment-{version}\n"), e)?;
    let canonical = json!({"format":"ve-quantity@1","formula":q,"traces":[]});
    let meaning_id = digest(
        &format!("ve-meaning-{version}\n"),
        &json!({"environment_id":environment_id,"ast":canonical}),
    )?;
    let mut out = json!({"id":id,"status":"ok",
        "assurance":"regeneration-only",
        "Q":q,"core":core,"environment_id":environment_id,
        "target_environment_id":checked["environment_id"],"meaning_id":meaning_id});
    if let Some(value) = checked.get("value") {
        out["value"] = value.clone();
    }
    Ok(out)
}
/// A W6 quantity document: decode and regenerate every unit, reading and node
/// statement. Admission (provenance rules, certificate replay and the report)
/// belongs to Lean; this reports the regenerated annotated meaning ids only.
fn quantity_document(v: &Value) -> Result<Value> {
    shape(v, &["kind", "mode", "environment", "document"], &["id"])?;
    if v["kind"] != "quantity" {
        return error("InvalidInput", "quantity kind required");
    }
    let e = &v["environment"];
    declarations(e)?;
    if !array(&e["profiles"])?.contains(&json!("documents@1")) {
        return error("UnsupportedProfile", "quantity documents require documents@1");
    }
    let d = &v["document"];
    shape(
        d,
        &["units", "graph"],
        &["lemmas", "open_terms", "reading_sets", "narrowings"],
    )?;
    if d.get("lemmas").map(array).transpose()?.is_some_and(|l| !l.is_empty()) {
        return error(
            "UnsupportedProfile",
            "document citations require a checked bundle binding",
        );
    }
    let id = v.get("id").cloned().unwrap_or(json!(""));
    let mut units = vec![];
    for u in array(&d["units"])? {
        shape(u, &["id", "span", "kind"], &["content"])?;
        units.push(match u.get("content") {
            Some(q) => json!(meaning(e, q)?),
            None => Value::Null,
        });
    }
    for r in d
        .get("reading_sets")
        .map(array)
        .transpose()?
        .unwrap_or(&vec![])
    {
        shape(r, &["id", "version", "readings"], &[])?;
        for q in array(&r["readings"])? {
            meaning(e, q)?;
        }
    }
    let graph = &d["graph"];
    shape(graph, &["root", "nodes"], &[])?;
    let mut nodes = vec![];
    for n in array(&graph["nodes"])? {
        shape(
            n,
            &["name", "quantity"],
            &["label", "unit", "premises", "certificate"],
        )?;
        nodes.push(json!(meaning(e, &n["quantity"])?));
    }
    Ok(json!({"id":id,"status":"ok","assurance":"regeneration-only",
        "unit_meaning_ids":units,"node_meaning_ids":nodes}))
}
/// The annotated meaning id of one submitted quantity statement.
fn meaning(e: &Value, p: &Value) -> Result<String> {
    let (q, _) = quantity_payload(e, p)?;
    let profiles = array(&e["profiles"])?;
    let version = format!(
        "v0.2:{}",
        profiles
            .iter()
            .map(|x| x.as_str().unwrap())
            .collect::<Vec<_>>()
            .join(",")
    );
    let environment_id = digest(&format!("ve-environment-{version}\n"), e)?;
    let canonical = json!({"format":"ve-quantity@1","formula":q,"traces":[]});
    digest(
        &format!("ve-meaning-{version}\n"),
        &json!({"environment_id":environment_id,"ast":canonical}),
    )
}
