//! W6a ground-unit regeneration for Rust conformance. No proof certificates.
use crate::{Error, Result, digest, error, order_case};
use num_bigint::BigInt;
use serde_json::{Value, json};
use std::collections::BTreeSet;

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
fn budget(v: &Value) -> Result<()> {
    let mut stack = vec![(v, 1usize)];
    let mut count = 0usize;
    while let Some((value, depth)) = stack.pop() {
        if let Some(items) = value.as_array() {
            count += 1;
            if count > 10_000 || depth > 64 {
                return error("ResourceLimit", "quantity AST exceeds node or depth limit");
            }
            if items.len() > 1 {
                for item in &items[1..] {
                    stack.push((item, depth + 1));
                }
            }
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
fn exact_decimal(e: &Value, tag: &str, s: &str) -> Result<String> {
    if s.len() > 40 {
        return error("ResourceLimit", "decimal literal exceeds 40 characters");
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
        return error("InvalidInput", "InvalidDate");
    }
    let y: i32 = s[..4].parse().unwrap_or(0);
    let m: usize = s[5..7].parse().unwrap_or(0);
    let d: i32 = s[8..].parse().unwrap_or(0);
    if !(1970..=9999).contains(&y) || !(1..=12).contains(&m) {
        return error("InvalidInput", "DateRange");
    }
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
    if d < 1 || d > days[m - 1] {
        return error("InvalidInput", "InvalidDate");
    }
    let years = (1970..y)
        .map(|v| if leap(v) { 366 } else { 365 })
        .sum::<i32>();
    Ok((years + days[..m - 1].iter().sum::<i32>() + d - 1).to_string())
}
fn same(a: &str, b: &str) -> Result<()> {
    if a == b {
        Ok(())
    } else {
        error("TypeMismatch", format!("UnitMismatch({a},{b})"))
    }
}
fn term(e: &Value, v: &Value, ctx: &[String], depth: usize) -> Result<(String, Value, Value)> {
    if depth > 64 {
        return error("ResourceLimit", "quantity term depth");
    }
    let (op, a) = node(v)?;
    match (op, a.len()) {
        ("num", 2) => {
            let n = int(string(&a[1])?)?.to_string();
            Ok((
                "dimensionless".into(),
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
            Ok((tag.into(), json!(["num", tag, n]), json!(["num", n])))
        }
        ("date", 2) => {
            unit(e, "day")?;
            let n = date_number(string(&a[1])?)?;
            Ok(("day".into(), json!(["num", "day", n]), json!(["num", n])))
        }
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
                return Ok((sort.into(), v.clone(), v.clone()));
            }
            let tag = if a.len() == 3 {
                unit(e, string(&a[1])?)?
            } else {
                "dimensionless"
            };
            same(
                tag,
                d.get("unit")
                    .and_then(Value::as_str)
                    .unwrap_or("dimensionless"),
            )?;
            Ok((
                tag.into(),
                json!(["const", tag, name]),
                json!(["const", name]),
            ))
        }
        ("add", 3 | 4) => {
            let (tag, l, r) = if a.len() == 4 {
                (unit(e, string(&a[1])?)?, &a[2], &a[3])
            } else {
                ("dimensionless", &a[1], &a[2])
            };
            let (lt, lq, lc) = term(e, l, ctx, depth + 1)?;
            let (rt, rq, rc) = term(e, r, ctx, depth + 1)?;
            same(tag, &lt)?;
            same(tag, &rt)?;
            if tag == "day" {
                return error("TypeMismatch", "calendar dates cannot be added");
            }
            Ok((
                tag.into(),
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
            same(tag, &tt)?;
            if tag == "day" {
                return error("TypeMismatch", "calendar dates cannot be scaled");
            }
            Ok((
                tag.into(),
                json!(["scale", tag, c, tq]),
                json!(["scale", c, tc]),
            ))
        }
        ("var", 2) => {
            let i = a[1]
                .as_u64()
                .ok_or_else(|| Error::new("UnboundVariable", "invalid index"))?;
            let sort = ctx
                .get(i as usize)
                .ok_or_else(|| Error::new("UnboundVariable", "unbound index"))?;
            if sort == "$int" {
                return error(
                    "UnsupportedProfile",
                    "$int quantification requires the missing numbers2 route",
                );
            }
            Ok((sort.clone(), v.clone(), v.clone()))
        }
        ("var", 3) => error(
            "UnsupportedProfile",
            "$int quantification requires the missing numbers2 route",
        ),
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
fn temporal(
    e: &Value,
    op: &str,
    a: &[Value],
    ctx: &[String],
    depth: usize,
) -> Result<(Value, Value)> {
    let three = ["within_days", "shift_days", "elapsed_days"].contains(&op);
    if a.len() != if three { 4 } else { 3 } {
        return error("SyntaxError", "invalid temporal arity");
    }
    let (ta, qa, ca) = term(e, &a[1], ctx, depth + 1)?;
    let (tb, qb, cb) = term(e, &a[2], ctx, depth + 1)?;
    same(&ta, "day")?;
    same(&tb, "day")?;
    let both = json!(["and", guard(&ca), guard(&cb)]);
    let (q, body) = match op {
        "date_on" => (json!([op, qa, qb]), json!(["eq", ca, cb])),
        "date_before" => (json!([op, qa, qb]), json!(["lt", ca, cb])),
        "date_after" => (json!([op, qa, qb]), json!(["lt", cb, ca])),
        "date_no_later" => (json!([op, qa, qb]), json!(["le", ca, cb])),
        "elapsed_days" => {
            let (tv, qv, cv) = term(e, &a[3], ctx, depth + 1)?;
            same(&tv, "elapsed_day")?;
            (
                json!([op, qa, qb, qv]),
                json!(["eq", cv, ["add", cb, ["scale", "-1", ca]]]),
            )
        }
        "within_days" | "shift_days" => {
            let n = int(string(&a[3])?)?;
            if n < BigInt::from(0) {
                return error("InvalidInput", "day offset must be nonnegative");
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
    if depth > 64 {
        return error("ResourceLimit", "quantity formula depth");
    }
    let (op, a) = node(v)?;
    match (op, a.len()) {
        ("top" | "bottom", 1) => Ok((v.clone(), v.clone())),
        ("eq" | "lt" | "le", 3) => {
            let (lt, lq, lc) = term(e, &a[1], ctx, depth + 1)?;
            let (rt, rq, rc) = term(e, &a[2], ctx, depth + 1)?;
            same(&lt, &rt)?;
            if op != "eq" && lt != "dimensionless" && e["units"].get(&lt).is_none() {
                return error("TypeMismatch", "order needs integers");
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
                let expected = if signature[i] == "$int" {
                    decl.get("argument_units")
                        .and_then(|m| m.get(i.to_string()))
                        .and_then(Value::as_str)
                        .unwrap_or("dimensionless")
                } else {
                    string(&signature[i])?
                };
                let (found, tq, tc) = term(e, arg, ctx, depth + 1)?;
                same(expected, &found)?;
                q.push(tq);
                core.push(tc);
            }
            Ok((json!(q), json!(core)))
        }
        ("not", 2) => {
            let (q, c) = formula(e, &a[1], ctx, depth + 1)?;
            Ok((json!([op, q]), json!([op, c])))
        }
        ("and" | "or" | "implies", 3) => {
            let (lq, lc) = formula(e, &a[1], ctx, depth + 1)?;
            let (rq, rc) = formula(e, &a[2], ctx, depth + 1)?;
            Ok((json!([op, lq, rq]), json!([op, lc, rc])))
        }
        ("forall" | "exists", 3) => {
            let sort = string(&a[1])?;
            if sort == "$int" {
                return error(
                    "UnsupportedProfile",
                    "$int quantification requires the missing numbers2 route",
                );
            }
            if e["vocabulary"]["sorts"].get(sort).is_none() {
                return error("UnknownSymbol", "unknown binder sort");
            }
            let mut next = vec![sort.to_owned()];
            next.extend_from_slice(ctx);
            let (q, c) = formula(e, &a[2], &next, depth + 1)?;
            Ok((json!([op, sort, q]), json!([op, sort, c])))
        }
        (
            "date_on" | "date_before" | "date_after" | "date_no_later" | "within_days"
            | "shift_days" | "elapsed_days",
            _,
        ) => temporal(e, op, a, ctx, depth),
        (
            "sunday" | "excluded_sundays" | "forall_date" | "exists_date" | "trace_all"
            | "trace_some" | "forall" | "exists",
            _,
        ) => error(
            "UnsupportedProfile",
            "$int quantification requires the missing numbers2 route",
        ),
        _ => error(
            "UnsupportedProfile",
            "quantity formula route not supported in Rust",
        ),
    }
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
    let profiles = array(&e["profiles"])?;
    if !["order@0", "relational-fol@0", "time@0"]
        .iter()
        .all(|p| profiles.contains(&json!(p)))
    {
        return error(
            "UnsupportedProfile",
            "quantities require order@0 and time@0",
        );
    }
    let u = object(&e["units"])?;
    if u.len() > 64 {
        return error("ResourceLimit", "At most 64 unit tags");
    }
    let mut forms = BTreeSet::new();
    let mut money_codes = BTreeSet::new();
    let mut decimal_prefixes = BTreeSet::new();
    for (tag, record) in u {
        crate::environment::identifier(tag, "InvalidInput")?;
        if tag == "dimensionless" {
            return error("InvalidInput", "reserved unit tag");
        }
        scale(e, tag)?;
        let d = &record["display"];
        let kind = string(
            d.get("kind")
                .ok_or_else(|| Error::new("InvalidInput", "display kind missing"))?,
        )?;
        let key = match kind {
            "percent" => {
                shape(d, &["kind"], &[])?;
                "percent".into()
            }
            "money" => {
                shape(d, &["kind", "currency"], &["input_symbol"])?;
                let c = string(&d["currency"])?;
                if c.len() != 3 || !c.bytes().all(|b| b.is_ascii_uppercase()) {
                    return error("InvalidInput", "invalid currency");
                }
                money_codes.insert(c.to_owned());
                if let Some(raw) = d.get("input_symbol") {
                    let symbol = string(raw)?;
                    if symbol.is_empty()
                        || symbol.chars().count() > 256
                        || !forms.insert(format!("symbol:{symbol}"))
                    {
                        return error("InvalidInput", "DisplayCollision(input_symbol)");
                    }
                }
                format!("money:{c}")
            }
            "decimal" => {
                shape(d, &["kind", "label"], &["placement"])?;
                let label = string(&d["label"])?;
                if label.is_empty() || label.chars().count() > 256 {
                    return error("InvalidInput", "invalid label");
                }
                let placement = d
                    .get("placement")
                    .map(string)
                    .transpose()?
                    .unwrap_or("suffix");
                if placement != "prefix" && placement != "suffix" {
                    return error("InvalidInput", "invalid placement");
                }
                if placement == "prefix" {
                    decimal_prefixes.insert(label.to_owned());
                }
                format!("decimal:{label}")
            }
            "iso_date" => {
                shape(d, &["kind"], &[])?;
                if tag != "day" || record["scale"] != "1" {
                    return error("InvalidInput", "iso_date requires day at scale 1");
                }
                "iso_date".into()
            }
            _ => return error("InvalidInput", "unknown display kind"),
        };
        if !forms.insert(key) {
            return error("InvalidInput", "DisplayCollision");
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
    if money_codes.intersection(&decimal_prefixes).next().is_some() {
        return error("InvalidInput", "DisplayCollision(currency label)");
    }
    shape(&e["vocabulary"], &["sorts", "predicates", "constants"], &[])?;
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
    for (_, c) in object(&e["vocabulary"]["constants"])? {
        if let Some(u) = c.get("unit") {
            if c["sort"] != "$int" {
                return error("InvalidInput", "unit on non-integer constant");
            }
            unit(e, string(u)?)?;
        }
    }
    Ok(())
}
/// Decode annotated source, regenerate Q and core, and validate the core AST.
/// This is evaluation-only and cannot certify a W6 claim.
pub fn quantity_case(v: &Value) -> Result<Value> {
    shape(v, &["kind", "environment", "quantity"], &["id", "model"])?;
    if v["kind"] != "quantity" {
        return error("InvalidInput", "quantity kind required");
    }
    let e = v
        .get("environment")
        .ok_or_else(|| Error::new("InvalidInput", "environment missing"))?;
    declarations(e)?;
    let p = v
        .get("quantity")
        .ok_or_else(|| Error::new("InvalidInput", "quantity missing"))?;
    shape(p, &["format", "formula"], &["traces", "Q"])?;
    if p["format"] != "ve-quantity@1" {
        return error("UnsupportedProfile", "quantity format");
    }
    let traces = p.get("traces").cloned().unwrap_or(json!([]));
    if !array(&traces)?.is_empty() {
        return error(
            "UnsupportedProfile",
            "trace declarations require numbers2 route",
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
    let mut target = e.clone();
    target.as_object_mut().unwrap().remove("unit_schema");
    target.as_object_mut().unwrap().remove("units");
    for c in target["vocabulary"]["constants"]
        .as_object_mut()
        .unwrap()
        .values_mut()
    {
        let c = c.as_object_mut().unwrap();
        c.remove("unit");
        c.remove("verbalisation");
    }
    for p in target["vocabulary"]["predicates"]
        .as_object_mut()
        .unwrap()
        .values_mut()
    {
        p.as_object_mut().unwrap().remove("argument_units");
    }
    let mut case = json!({"id":v.get("id").cloned().unwrap_or(json!("")),"kind":"evaluate",
        "environment":target,"ast":[core.clone()]});
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
    let mut out = json!({"id":v.get("id").cloned().unwrap_or(json!("")),"status":"ok",
        "assurance":"regeneration-only",
        "Q":q,"core":core,"environment_id":environment_id,
        "target_environment_id":checked["environment_id"],"meaning_id":meaning_id});
    if let Some(value) = checked.get("value") {
        out["value"] = value.clone();
    }
    Ok(out)
}
