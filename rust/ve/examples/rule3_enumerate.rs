//! Measurement-only stream of Rust search candidates; no evaluation or verdict.
use std::io::{self, BufRead, Write};

use serde_json::{Value, json};
use ve_core::{CandidateIterator, CountermodelProblem, Document, Environment, Error, FiniteModel, Result};

fn field<'a>(value: &'a Value, key: &str) -> Result<&'a Value> {
    value.get(key).ok_or_else(|| Error::new("InvalidInput", format!("missing {key}")))
}

fn number(value: &Value, key: &str, default: u64) -> Result<u64> {
    value.get(key).map_or(Ok(default), |v| v.as_u64().ok_or_else(||
        Error::new("InvalidInput", format!("{key} must be a nonnegative integer"))))
}

fn run(value: &Value, batch: usize) -> Result<()> {
    let env = Environment::from_value(field(value, "environment")?)?;
    let premises = field(value, "premises")?.as_array()
        .ok_or_else(|| Error::new("InvalidInput", "premises must be an array"))?;
    let mut ast = premises.clone();
    ast.push(field(value, "conclusion")?.clone());
    let doc = Document::from_value(&env, &json!(ast))?;
    let (conclusion, premises) = doc.formulas().split_last().expect("nonempty document");
    let problem = CountermodelProblem::new(&env, premises.to_vec(), conclusion.clone())?;
    let guard_document = value.get("nonvacuous_for")
        .map(|formula| Document::from_value(&env, &json!([formula]))).transpose()?;
    let guard = guard_document.as_ref().map(|document| &document.formulas()[0]);
    let maximum = usize::try_from(number(value, "max_domain_size", 2)?)
        .map_err(|_| Error::new("ResourceLimit", "domain bound overflow"))?;
    let minimum = usize::try_from(number(value, "min_domain_size", 0)?)
        .map_err(|_| Error::new("ResourceLimit", "minimum domain bound overflow"))?
        .max(usize::from(value.get("nonempty_domains") == Some(&json!(true))));
    let limit = number(value, "max_models", 10_000)?;
    let mut models = CandidateIterator::new(&env, &problem, maximum, minimum, guard)?;
    let mut next = models.next_model()?;
    let mut emitted = 0;
    let stdout = io::stdout();
    let mut out = stdout.lock();
    loop {
        let mut chunk = Vec::new();
        while chunk.len() < batch && emitted < limit {
            let Some(model) = next.take() else { break };
            chunk.push(FiniteModel::to_value(&model));
            emitted += 1;
            next = models.next_model()?;
        }
        let exhausted = next.is_none();
        writeln!(out, "{}", json!({"models": chunk, "exhausted": exhausted}))
            .map_err(|e| Error::new("InvalidInput", e.to_string()))?;
        out.flush().map_err(|e| Error::new("InvalidInput", e.to_string()))?;
        if exhausted || emitted == limit { break }
    }
    Ok(())
}

fn main() {
    let mut input = String::new();
    if let Err(error) = io::stdin().lock().read_line(&mut input)
        .map_err(|e| e.to_string())
        .and_then(|_| serde_json::from_str::<Value>(&input).map_err(|e| e.to_string()))
        .and_then(|value| {
            let batch = std::env::args().nth(1).unwrap_or_else(|| "256".into())
                .parse::<usize>().map_err(|e| e.to_string())?;
            if batch == 0 { return Err("batch must be positive".into()); }
            run(&value, batch).map_err(|e| format!("{e:?}"))
        })
    {
        eprintln!("{error}");
        std::process::exit(1);
    }
}
