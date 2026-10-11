// `memory` holds the binary's one allowed unsafe impl, the counting allocator; all else is safe.
#![deny(unsafe_code)]
mod memory;

use serde_json::{Value, json};
use std::io::{self, BufRead, Read, Write};
use std::sync::Mutex;
use ve_core::*;

#[global_allocator]
static ALLOCATOR: memory::Budget = memory::Budget;

/// The `ve jsonl` case being answered (its `id`, `""` when it has none), so that exhausting the
/// memory budget still answers it. None outside `ve jsonl`.
static ANSWERING: Mutex<Option<Value>> = Mutex::new(None);
static JSONL: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);

/// The memory budget is exhausted (`memory.rs`). `ve jsonl` answers the case it was serving with
/// ResourceLimit, as any rejected case (exit 1). Every other command reports it as a failed
/// command (exit 2). Then the process ends: memory is not reclaimed from a case midway.
fn out_of_memory(limit: usize) -> ! {
    let error = Error::new("ResourceLimit",
        format!("memory budget exhausted: {limit} bytes ({})", memory::VARIABLE));
    if JSONL.load(std::sync::atomic::Ordering::Relaxed) {
        let record = match ANSWERING.try_lock().ok().and_then(|mut id| id.take()) {
            Some(id) => json!({"id":id,"status":"error","error":error}),
            None => json!({"status":"error","error":error}),
        };
        let mut stdout = io::stdout();
        let _ = writeln!(stdout, "{record}");
        let _ = stdout.flush();
        std::process::exit(1);
    }
    eprintln!("{}", json!({"status":"error","error":error}));
    std::process::exit(2);
}

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
/// The case's `soft_premises` (a validated soft document's Background slot),
/// typed over the environment and attached to it.
fn soft(env: Environment, v: &Value) -> Result<Environment> {
    match v.get("soft_premises") {
        None => Ok(env),
        Some(asts) => {
            let premises = Document::from_value(&env, asts)?.formulas().to_vec();
            Ok(env.with_soft_premises(premises))
        }
    }
}
fn case(v: &Value) -> Result<Value> {
    if v.get("kind") == Some(&json!("readings-superposed-evaluate")) {
        return readings_superposed_evaluate_case(v);
    }
    // Rust checks no quantity: the Lean quantity route owns W6 typing, certificates,
    // countermodels and documents (docs/LEAN-FIRST-PLAN.md, batch 9), so the case is refused.
    if v.get("kind") == Some(&json!("quantity")) {
        return Err(Error::new("UnsupportedProfile", "quantities are checked by the Lean quantity route"));
    }
    // A reports case names its profile. Rust checks no discourse elaboration: the Lean discourse
    // route owns the profile (docs/LEAN-FIRST-PLAN.md, batch 4), so any other family is refused.
    if v.get("family") == Some(&json!("elaborated-document")) && v.get("profile") == Some(&json!("reports@0")) {
        if v.get("untrusted") != Some(&json!(true))
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
    if v.get("family").is_some() {
        return Err(Error::new("UnsupportedProfile", "Rust checks no elaborated-document family but reports@0"));
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
        let env = soft(Environment::from_value(field(v, "environment")?)?, v)?;
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
        let env = soft(Environment::from_value(field(v, "environment")?)?, v)?;
        if env.order() {
            return order_case(v);
        }
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
    let env = soft(Environment::from_value(field(v, "environment")?)?, v)?;
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
    // Rust reads no source text and prints no canonical text or document identities: Python
    // parses and prints, and Lean checks (docs/LEAN-FIRST-PLAN.md, batch 15b). Any other case
    // shape is refused.
    Err(Error::new("InvalidInput", "unknown case: Rust checks search cases only"))
}

/// Untrusted S2a shadow of the formulas regenerated by Python and checked by
/// Lean.  Rust evaluates each group on a shown complete model; it neither
/// elaborates readings nor grants a verdict from these Boolean values.
fn readings_superposed_evaluate_case(v: &Value) -> Result<Value> {
    if v.get("untrusted") != Some(&json!(true)) {
        return Err(Error::new("InvalidInput", "S2 formulas must be marked untrusted"));
    }
    let env = Environment::from_value(field(v, "environment")?)?;
    let model = FiniteModel::from_value(&env, field(v, "model")?)?;
    let mut groups = serde_json::Map::new();
    for key in ["slot", "assertions", "conflict_targets", "conclusions"] {
        let formulas = field(v, key)?.as_array()
            .ok_or_else(|| Error::new("InvalidInput", format!("{key} must be an array")))?;
        if formulas.is_empty() {
            groups.insert(key.to_owned(), json!([]));
            continue;
        }
        let doc = Document::from_value(&env, &json!(formulas))?;
        let values = (0..doc.formulas().len())
            .map(|index| {
                evaluate_formula(&doc, index, &model, MAX_EVALUATIONS).and_then(|result| {
                    result.value.ok_or_else(|| {
                        Error::new("ResourceLimit", "evaluation budget exhausted")
                    })
                })
            })
            .collect::<Result<Vec<_>>>()?;
        groups.insert(key.to_owned(), json!(values));
    }
    Ok(json!({"id":v.get("id").cloned().unwrap_or(json!("")), "status":"ok",
              "untrusted":true, "model_id":model.model_id(), "values":groups}))
}

#[cfg(test)]
mod readings_s2_tests {
    use super::*;

    #[test]
    fn evaluates_four_untrusted_s2_groups_without_a_verdict() {
        let environment = json!({"language":"ve.core@0.2",
            "profiles":["relational-fol@0"],
            "spec_revision":"ve-v0.2-expand2-2026-09-25",
            "vocabulary":{"sorts":{},"predicates":{},"constants":{}}});
        let input = json!({"id":"s2", "kind":"readings-superposed-evaluate",
            "untrusted":true, "environment":environment,
            "model":{"complete":true,"domains":{},"relations":{},"constants":{}},
            "slot":[["top"]], "assertions":[["bottom"]],
            "conflict_targets":[], "conclusions":[["top"],["bottom"]]});
        let out = case(&input).unwrap();
        assert_eq!(out["status"], "ok");
        assert_eq!(out["untrusted"], true);
        assert_eq!(out["values"]["slot"], json!([true]));
        assert_eq!(out["values"]["assertions"], json!([false]));
        assert_eq!(out["values"]["conflict_targets"], json!([]));
        assert_eq!(out["values"]["conclusions"], json!([true, false]));
        assert!(out.get("verdict").is_none());
        let mut unmarked = input;
        unmarked["untrusted"] = json!(false);
        assert!(case(&unmarked).is_err());
    }
}

#[cfg(test)]
mod search_only_tests {
    use super::*;

    fn environment() -> Value {
        json!({"language":"ve.core@0.2", "profiles":["relational-fol@0"],
               "spec_revision":"ve-v0.2-expand2-2026-09-25",
               "vocabulary":{"sorts":{"item":{"description":"item"}},
                             "predicates":{"marked":{"arguments":["item"],"description":"marked"}},
                             "constants":{}}})
    }

    #[test]
    fn source_label_order_and_identity_cases_are_refused() {
        // Rust reads no source text, checks no label or dependency order and prints no
        // canonical text: each such case is an unknown case, never an answer.
        for input in [
            json!({"id":"s", "environment":environment(), "source":"true.\n"}),
            json!({"id":"a", "environment":environment(), "ast":[["top"]]}),
            json!({"id":"m", "environment":environment(), "ast":[["top"]],
                   "model":{"complete":true,"domains":{"item":[]},"constants":{},
                            "relations":{"marked":[]}}}),
            json!({"id":"l", "kind":"label", "environment":environment(), "label":"asserted"}),
            json!({"id":"d", "kind":"dependency-order", "environment":environment(),
                   "nodes":[{"name":"a","mentions":[]}]}),
        ] {
            let error = case(&input).unwrap_err();
            assert_eq!(error.code, "InvalidInput", "{input}");
            assert!(error.message.starts_with("unknown case"), "{input}");
        }
    }

    #[test]
    fn countermodel_search_and_check_are_kept() {
        let marked = json!(["exists","item",["unary","marked",["var",0]]]);
        let search = json!({"id":"q", "environment":environment(), "premises":[],
                            "conclusion":marked, "max_domain_size":1});
        let found = case(&search).unwrap();
        assert_eq!(found["status"], "Found");
        assert_eq!(found["id"], "q");
        let mut check = search.clone();
        check["model"] = found["model"].clone();
        let checked = case(&check).unwrap();
        assert_eq!(checked["valid"], true);
        let mut valid = search;
        valid["premises"] = json!([marked]);
        assert_eq!(case(&valid).unwrap()["status"], "NotFound");
    }
}

#[cfg(test)]
mod quantity_tests {
    use super::*;

    #[test]
    fn quantity_cases_are_the_lean_routes() {
        for mode in ["admission", "countermodel", "certificate", "document"] {
            let input = json!({"id":"q", "kind":"quantity", "mode":mode, "environment":{},
                               "quantity":{"format":"ve-quantity@1","formula":["top"]}});
            assert_eq!(case(&input).unwrap_err().code, "UnsupportedProfile");
        }
    }
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
        // a discourse elaboration (no reports profile) is the Lean discourse route's: refused
        let mut discourse = input.clone();
        discourse.as_object_mut().unwrap().remove("profile");
        discourse["formulas"] = json!([["unary","safe",["const","alice"]]]);
        assert_eq!(case(&discourse).unwrap_err().code, "UnsupportedProfile");
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
            JSONL.store(true, std::sync::atomic::Ordering::Relaxed);
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
                    Ok(v) => {
                        *ANSWERING.lock().unwrap_or_else(|e| e.into_inner()) =
                            Some(v.get("id").cloned().unwrap_or(json!("")));
                        case_record(&v)
                    }
                    Err(e) => json!({"status":"error","error":e}),
                };
                failed |= out["status"] == "error";
                writeln!(stdout, "{out}").map_err(|e| Error::new("InvalidInput", e.to_string()))?;
                // Each record is flushed as it is answered, so one process can serve a
                // client that waits for every answer before it sends the next case
                // (`ve/backends/rust_jsonl.py`, docs/LEAN-FIRST-PLAN.md F6).
                stdout
                    .flush()
                    .map_err(|e| Error::new("InvalidInput", e.to_string()))?;
                ANSWERING.lock().unwrap_or_else(|e| e.into_inner()).take();
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
        "VE v0 experimental Rust core: untrusted search and evaluation over wire ASTs\nve conformance [CASES.json|-]\nve jsonl [CASES.jsonl|-]\nve canonical-json [INPUT.json|-]\nmemory budget: {} bytes ({}; default {})",
        memory::limit(), memory::VARIABLE, memory::DEFAULT_LIMIT
    );
}
fn main() {
    memory::on_exhausted(out_of_memory);
    if let Err(message) = memory::configure() {
        eprintln!("{}", json!({"status":"error","error":Error::new("InvalidInput", message)}));
        std::process::exit(2);
    }
    let code = match run(&std::env::args().skip(1).collect::<Vec<_>>()) {
        Ok(code) => code,
        Err(e) => {
            eprintln!("{}", json!({"status":"error","error":e}));
            2
        }
    };
    std::process::exit(code);
}
