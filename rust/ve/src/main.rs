#![forbid(unsafe_code)]
use serde_json::{Value, json};
use std::io::{self, BufRead, Read, Write};
use ve_core::*;

fn read(path: &str) -> Result<Vec<u8>> {
    let mut out = Vec::new();
    let input: Box<dyn Read> = if path == "-" {
        Box::new(io::stdin())
    } else {
        Box::new(std::fs::File::open(path).map_err(|e| Error::new("InvalidInput", e.to_string()))?)
    };
    input
        .take((MAX_PACKAGE_BYTES + 1) as u64)
        .read_to_end(&mut out)
        .map_err(|e| Error::new("InvalidInput", e.to_string()))?;
    if out.len() > MAX_PACKAGE_BYTES {
        return Err(Error::new("ResourceLimit", "input exceeds 16 MiB"));
    }
    Ok(out)
}
fn field<'a>(v: &'a Value, name: &str) -> Result<&'a Value> {
    v.get(name)
        .ok_or_else(|| Error::new("InvalidInput", format!("missing {name}")))
}
fn number(v: &Value, name: &str, default: u64) -> Result<u64> {
    match v.get(name) {
        None => Ok(default),
        Some(n) => n.as_u64().ok_or_else(|| {
            Error::new(
                "InvalidInput",
                format!("{name} must be a nonnegative integer"),
            )
        }),
    }
}
fn nonvacuity(env: &Environment, v: &Value) -> Result<(Option<Formula>, bool)> {
    let semantic = match v.get("semantic_nonvacuity") {
        None => false,
        Some(value) => value.as_bool().ok_or_else(||
            Error::new("InvalidInput", "semantic_nonvacuity must be Boolean"))?,
    };
    let guard = match v.get("nonvacuous_for") {
        None => None,
        Some(value) => Some(Document::from_value(env, &json!([value]))?.formulas()[0].clone()),
    };
    if semantic && guard.is_none() {
        return Err(Error::new("InvalidInput", "semantic_nonvacuity requires nonvacuous_for"));
    }
    Ok((guard, semantic))
}
/// The route kinds that need only a gated envelope: the label grammar and the
/// dependency-DAG order (same diagnostics as Python and the Lean `route`).
fn route_case(v: &Value, kind: &str) -> Result<Value> {
    Environment::from_value(field(v, "environment")?)?;
    let id = v.get("id").cloned().unwrap_or(json!(""));
    if kind == "label" {
        let label = field(v, "label")?
            .as_str()
            .ok_or_else(|| Error::new("InvalidInput", "label must be a string"))?;
        check_label(label)?;
        return Ok(json!({"id":id,"status":"ok","label":label}));
    }
    let bad = || Error::new("InvalidInput", "dependency nodes are {name, mentions}");
    let nodes = field(v, "nodes")?
        .as_array()
        .ok_or_else(bad)?
        .iter()
        .map(|node| {
            let object = node.as_object().filter(|o| o.len() == 2).ok_or_else(bad)?;
            let name = object.get("name").and_then(Value::as_str).ok_or_else(bad)?;
            let mentions = object
                .get("mentions")
                .and_then(Value::as_array)
                .ok_or_else(bad)?
                .iter()
                .map(|m| m.as_str().map(str::to_owned).ok_or_else(bad))
                .collect::<Result<Vec<_>>>()?;
            Ok((name.to_owned(), mentions))
        })
        .collect::<Result<Vec<_>>>()?;
    Ok(json!({"id":id,"status":"ok","order":dependency_order(&nodes)?}))
}
fn case(v: &Value) -> Result<Value> {
    if v.get("kind") == Some(&json!("quantity")) {
        return quantity_case(v);
    }
    if v.get("family") == Some(&json!("elaborated-document")) {
        if v.get("profile") != Some(&json!("reports@0"))
            || v.get("untrusted") != Some(&json!(true))
            || v.get("envelope").is_none()
            || v.get("conclusion").is_none() {
            return Err(Error::new("InvalidInput", "reports search needs an untrusted elaboration, envelope and conclusion"));
        }
        let mut plain = v.clone();
        let object = plain.as_object_mut().ok_or_else(|| Error::new("InvalidInput", "reports search object"))?;
        for key in ["family", "profile", "untrusted", "envelope"] { object.remove(key); }
        let mut result = case(&plain)?;
        result["untrusted"] = json!(true);
        result["envelope"] = v["envelope"].clone();
        return Ok(result);
    }
    if let Some(kind @ ("label" | "dependency-order")) = v.get("kind").and_then(Value::as_str) {
        return route_case(v, kind);
    }
    if v.get("kind").and_then(Value::as_str) == Some("check") {
        let env = Environment::from_value(field(v, "environment")?)?;
        if env.order() {
            return order_case(v);
        }
        let ast = field(v, "ast")?;
        let items = ast.as_array().ok_or_else(|| Error::new("SyntaxError", "AST must be an array"))?;
        let document = if items.first().is_some_and(Value::is_string) {
            json!([ast])
        } else {
            ast.clone()
        };
        Document::from_value(&env, &document)?;
        return Ok(json!({"id":v.get("id").cloned().unwrap_or(json!("")),
            "status":"ok","well_typed":true}));
    }
    if v.get("kind").and_then(Value::as_str) == Some("evaluate-budgeted") {
        let env = Environment::from_value(field(v, "environment")?)?;
        if env.order() {
            return order_case(v);
        }
        let doc = Document::from_value(&env, field(v, "ast")?)?;
        let model = FiniteModel::from_value(&env, field(v, "model")?)?;
        let budget = number(v, "max_evaluations", MAX_EVALUATIONS)?;
        let trace = v.get("trace").and_then(Value::as_bool).unwrap_or(false);
        let mut out = if trace {
            let trace_budget = number(v, "max_trace_nodes", 10_000)?;
            serde_json::to_value(evaluate_traced(&doc, &model, budget, trace_budget)?).unwrap()
        } else {
            serde_json::to_value(evaluate(&doc, &model, budget)?).unwrap()
        };
        out["id"] = v.get("id").cloned().unwrap_or(json!(""));
        return Ok(out);
    }
    if v.get("kind").and_then(Value::as_str) == Some("distinguishing-model") {
        let env = Environment::from_value(field(v, "environment")?)?;
        let doc = Document::from_value(&env, &json!([field(v, "a")?, field(v, "b")?]))?;
        let bounds = SearchBounds {
            max_domain_size: usize::try_from(number(v, "max_domain_size", 2)?)
                .map_err(|_| Error::new("ResourceLimit", "domain bound overflow"))?,
            max_models: number(v, "max_models", 10_000)?,
            max_evaluations: number(v, "max_evaluations", MAX_EVALUATIONS)?,
        };
        let minimum = usize::try_from(number(v, "min_domain_size", 0)?)
            .map_err(|_| Error::new("ResourceLimit", "minimum domain bound overflow"))?;
        let nonempty = v.get("nonempty_domains").and_then(Value::as_bool).unwrap_or(false);
        let (guard, semantic) = nonvacuity(&env, v)?;
        let mut out = find_distinguishing_model_with_nonvacuity(&env, doc.formulas()[0].clone(),
            doc.formulas()[1].clone(), bounds, minimum.max(usize::from(nonempty)),
            guard.as_ref(), semantic)?.to_value();
        out["id"] = v.get("id").cloned().unwrap_or(json!(""));
        return Ok(out);
    }
    if v.get("environment")
        .and_then(|e| e.get("profiles"))
        .and_then(Value::as_array)
        .is_some_and(|profiles| profiles.contains(&json!("order@0")))
    {
        return order_case(v);
    }
    let env = Environment::from_value(field(v, "environment")?)?;
    if let Some(conclusion) = v.get("conclusion") {
        let ps = field(v, "premises")?
            .as_array()
            .ok_or_else(|| Error::new("SyntaxError", "premises must be an array"))?;
        let mut all = ps.clone();
        all.push(conclusion.clone());
        let doc = Document::from_value(&env, &json!(all))?;
        let (last, premises) = doc.formulas().split_last().unwrap();
        let problem = CountermodelProblem::new(&env, premises.to_vec(), last.clone())?;
        let maximum = number(v, "max_evaluations", MAX_EVALUATIONS)?;
        if let Some(model) = v.get("model") {
            let model = FiniteModel::from_value(&env, model)?;
            let mut out =
                serde_json::to_value(problem.check_countermodel(&model, maximum)?).unwrap();
            out["id"] = v.get("id").cloned().unwrap_or(json!(""));
            return Ok(out);
        }
        let bounds = SearchBounds {
            max_domain_size: usize::try_from(number(v, "max_domain_size", 2)?)
                .map_err(|_| Error::new("ResourceLimit", "domain bound overflow"))?,
            max_models: number(v, "max_models", 10_000)?,
            max_evaluations: maximum,
        };
        let minimum = usize::try_from(number(v, "min_domain_size", 0)?)
            .map_err(|_| Error::new("ResourceLimit", "minimum domain bound overflow"))?;
        let nonempty = v.get("nonempty_domains").and_then(Value::as_bool).unwrap_or(false);
        let (guard, semantic) = nonvacuity(&env, v)?;
        let mut out = find_countermodel_with_nonvacuity(&env, &problem, bounds,
            minimum.max(usize::from(nonempty)), guard.as_ref(), semantic)?.to_value();
        out["id"] = v.get("id").cloned().unwrap_or(json!(""));
        return Ok(out);
    }
    let doc = if let Some(ast) = v.get("ast") {
        Document::from_value(&env, ast)?
    } else {
        parse(
            &env,
            field(v, "source")?
                .as_str()
                .ok_or_else(|| Error::new("SyntaxError", "source must be text"))?
                .as_bytes(),
        )?
    };
    if let Some(source) = v.get("source") {
        let parsed = parse(
            &env,
            source
                .as_str()
                .ok_or_else(|| Error::new("SyntaxError", "source must be text"))?
                .as_bytes(),
        )?;
        if parsed != doc {
            return Err(Error::new("TypeMismatch", "source/AST mismatch"));
        }
    }
    let mut out = json!({"id":v.get("id").cloned().unwrap_or(json!("")),"status":"ok","canonical":print_document(&doc)?,"ast":doc.to_value(),"environment_id":env.environment_id(),"meaning_id":doc.meaning_id()?,"formula_meaning_ids":(0..doc.formulas().len()).map(|i| doc.formula_meaning_id(i)).collect::<Result<Vec<_>>>()?});
    out["canonical_environment"] =
        json!(String::from_utf8(canonical_json(&env.to_value())?).unwrap());
    out["canonical_ast"] = json!(String::from_utf8(canonical_json(&doc.to_value())?).unwrap());
    if let Some(model) = v.get("model") {
        let model = FiniteModel::from_value(&env, model)?;
        out["canonical_model"] =
            json!(String::from_utf8(canonical_json(&model.to_value())?).unwrap());
        let values = (0..doc.formulas().len())
            .map(|i| {
                evaluate_formula(&doc, i, &model, MAX_EVALUATIONS).and_then(|r| {
                    r.value
                        .ok_or_else(|| Error::new("ResourceLimit", "evaluation budget exhausted"))
                })
            })
            .collect::<Result<Vec<_>>>()?;
        out["value"] = json!(values.iter().all(|v| *v));
        out["values"] = json!(values);
        out["model_id"] = json!(model.model_id());
    }
    Ok(out)
}

#[cfg(test)]
mod reports_tests {
    use super::*;

    #[test]
    fn untrusted_reports_search_keeps_envelope_and_finds_nonfactive_witness() {
        let env = json!({
            "language":"ve.core@0.2",
            "profiles":["documents@1","relational-fol@0","reports@0"],
            "spec_revision":"ve-v0.2-expand2-2026-09-25",
            "vocabulary":{
                "reports":{"holders":["person","text"],"evidence":"evidence"},
                "sorts":{"person":{"description":"person"},"text":{"description":"text"},
                         "evidence":{"description":"evidence"}},
                "predicates":{"safe":{"arguments":["person"],"description":"safe"},
                              "reports__says__1":{"arguments":["text"],"description":"report"}},
                "constants":{"article":{"sort":"text","description":"article"},
                             "alice":{"sort":"person","description":"Alice"}}
            }
        });
        let input = json!({"family":"elaborated-document","profile":"reports@0",
                           "untrusted":true,"envelope":{"document_id":"bound"},
                           "environment":env,
                           "premises":[["unary","reports__says__1",["const","article"]]],
                           "conclusion":["unary","safe",["const","alice"]]});
        let result = case(&input).unwrap();
        assert_eq!(result["status"], "Found");
        assert_eq!(result["untrusted"], true);
        assert_eq!(result["envelope"], input["envelope"]);
        assert_eq!(result["model"]["relations"]["safe"], json!([]));
        let mut unmarked = input.clone();
        unmarked["untrusted"] = json!(false);
        assert!(case(&unmarked).is_err());
    }

    #[test]
    fn reports_holder_verbalisation_reserved_in_any_ascii_case() {
        for (words, reserved) in [("the stated assessment", true), ("The Stated Assessment", true),
                                  ("the stated assessments", false)] {
            let env = json!({
                "language":"ve.core@0.2",
                "profiles":["relational-fol@0","reports@0"],
                "spec_revision":"ve-v0.2-expand2-2026-09-25",
                "vocabulary":{
                    "reports":{"holders":["text"],"evidence":"evidence"},
                    "sorts":{"text":{"description":"text"},"evidence":{"description":"evidence"}},
                    "predicates":{},
                    "constants":{"article":{"sort":"text","description":"article","verbalisation":words}}
                }
            });
            assert_eq!(ve_core::Environment::from_value(&env).is_err(), reserved, "{words}");
        }
    }
}
fn case_record(v: &Value) -> Value {
    match case(v) {
        Ok(out) => out,
        Err(e) => {
            json!({"id":v.get("id").cloned().unwrap_or(json!("")),"status":"error","error":e})
        }
    }
}
fn option(args: &[String], name: &str) -> Result<String> {
    args.iter()
        .position(|x| x == name)
        .and_then(|i| args.get(i + 1))
        .cloned()
        .ok_or_else(|| Error::new("InvalidInput", format!("missing {name}")))
}
fn run(args: &[String]) -> Result<i32> {
    let Some(command) = args.first().map(String::as_str) else {
        help();
        return Ok(0);
    };
    match command {
        "--help" | "help" => {
            help();
            Ok(0)
        }
        "conformance" => {
            let data = loads_json(&read(args.get(1).map_or("-", String::as_str))?)?;
            let cases = if let Some(a) = data.as_array() {
                a.clone()
            } else {
                vec![data]
            };
            let out: Vec<_> = cases.iter().map(case_record).collect();
            let failed = out.iter().any(|r| r["status"] == "error");
            println!("{}", json!(out));
            Ok(i32::from(failed))
        }
        "jsonl" => {
            let input: Box<dyn Read> = if args.get(1).is_none_or(|x| x == "-") {
                Box::new(io::stdin())
            } else {
                Box::new(
                    std::fs::File::open(&args[1])
                        .map_err(|e| Error::new("InvalidInput", e.to_string()))?,
                )
            };
            let mut input = io::BufReader::new(input);
            let mut stdout = io::BufWriter::new(io::stdout().lock());
            let mut failed = false;
            loop {
                let mut line = Vec::new();
                let count = (&mut input)
                    .take((MAX_PACKAGE_BYTES + 1) as u64)
                    .read_until(b'\n', &mut line)
                    .map_err(|e| Error::new("InvalidInput", e.to_string()))?;
                if count == 0 {
                    break;
                }
                let out = match loads_json(&line) {
                    Ok(v) => case_record(&v),
                    Err(e) => json!({"status":"error","error":e}),
                };
                failed |= out["status"] == "error";
                writeln!(stdout, "{out}").map_err(|e| Error::new("InvalidInput", e.to_string()))?;
                if count > MAX_PACKAGE_BYTES {
                    // Drop only the rest of this record, using the reader's
                    // fixed-size buffer rather than allocating the whole line.
                    if line.last() != Some(&b'\n') {
                        loop {
                            let buffer = input
                                .fill_buf()
                                .map_err(|e| Error::new("InvalidInput", e.to_string()))?;
                            let end = buffer.iter().position(|b| *b == b'\n');
                            let consumed = end.map_or(buffer.len(), |i| i + 1);
                            input.consume(consumed);
                            if consumed == 0 || end.is_some() {
                                break;
                            }
                        }
                    }
                }
            }
            stdout
                .flush()
                .map_err(|e| Error::new("InvalidInput", e.to_string()))?;
            Ok(i32::from(failed))
        }
        "countermodel" | "check-countermodel" => {
            let env = loads_json(&read(&option(args, "--env")?)?)?;
            let environment = Environment::from_value(&env)?;
            let premises_bytes = read(&option(args, "--premises")?)?;
            let premises = parse(&environment, &premises_bytes)?.to_value();
            let conclusion = parse(&environment, &read(&option(args, "--conclusion")?)?)?;
            if conclusion.formulas().len() != 1 {
                return Err(Error::new(
                    "SyntaxError",
                    "conclusion must have exactly one statement",
                ));
            }
            let mut input = json!({"environment":env,"premises":premises,"conclusion":conclusion.formulas()[0].to_value()});
            if command == "check-countermodel" {
                input["model"] = loads_json(&read(&option(args, "--model")?)?)?;
            }
            for name in ["max-domain-size", "max-models", "max-evaluations"] {
                let flag = format!("--{name}");
                if args.contains(&flag) {
                    input[name.replace('-', "_")] = json!(
                        option(args, &flag)?
                            .parse::<u64>()
                            .map_err(|_| Error::new("InvalidInput", "invalid search bound"))?
                    );
                }
            }
            let out = case(&input)?;
            println!("{out}");
            Ok(match out["status"].as_str() {
                Some("Found" | "Valid") => 0,
                Some("ResourceLimit") => 2,
                _ => 1,
            })
        }
        "parse" | "format" | "evaluate" => {
            let env = Environment::from_json(&read(&option(args, "--env")?)?)?;
            let doc = parse(&env, &read(&option(args, "--source")?)?)?;
            if command == "format" {
                print!("{}", print_document(&doc)?);
                return Ok(0);
            }
            if command == "parse" {
                println!(
                    "{}",
                    json!({"ast":doc.to_value(),"canonical":print_document(&doc)?,"environment_id":env.environment_id(),"meaning_id":doc.meaning_id()?,"assurance":"experimental","intent":"unconfirmed","proof":"not_checked"})
                );
                return Ok(0);
            }
            let model = FiniteModel::from_json(&env, &read(&option(args, "--model")?)?)?;
            let result = evaluate(&doc, &model, MAX_EVALUATIONS)?;
            println!("{}", serde_json::to_string(&result).unwrap());
            Ok(match result.value {
                Some(true) => 0,
                Some(false) => 1,
                None => 2,
            })
        }
        "canonical-json" => {
            let v = loads_json(&read(args.get(1).map_or("-", String::as_str))?)?;
            io::stdout()
                .write_all(&canonical_json(&v)?)
                .map_err(|e| Error::new("InvalidInput", e.to_string()))?;
            Ok(0)
        }
        _ => Err(Error::new("InvalidInput", "unknown command; use --help")),
    }
}
fn help() {
    println!(
        "VE v0 experimental Rust core\nve parse|format --env ENV.json --source SOURCE.ve\nve evaluate --env ENV.json --source SOURCE.ve --model MODEL.json\nve conformance [CASES.json|-]\nve jsonl [CASES.jsonl|-]\nve canonical-json [INPUT.json|-]\nve countermodel --env ENV.json --premises PREMISES.ve --conclusion CONCLUSION.ve [--max-domain-size N] [--max-models N] [--max-evaluations N]\nve check-countermodel --env ENV.json --premises PREMISES.ve --conclusion CONCLUSION.ve --model MODEL.json"
    );
}
fn main() {
    let code = match run(&std::env::args().skip(1).collect::<Vec<_>>()) {
        Ok(code) => code,
        Err(e) => {
            eprintln!("{}", json!({"status":"error","error":e}));
            2
        }
    };
    std::process::exit(code);
}
