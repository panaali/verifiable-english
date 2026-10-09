#![forbid(unsafe_code)]
//! Measurement-only stream of the order@0 search's candidates (lean-first batch 15b); no
//! evaluation or verdict. One search case on stdin; batches of `{"models", "exhausted"}` lines
//! on stdout, as `rule3_enumerate` writes them.
use std::io::{self, BufRead, Write};

use serde_json::{Value, json};
use ve_core::{Error, Result, order_candidates};

fn run(value: &Value, batch: usize) -> Result<()> {
    let limit = value.get("max_models").map_or(Ok(10_000), |v| v.as_u64().ok_or_else(||
        Error::new("InvalidInput", "max_models must be a nonnegative integer")))?;
    let stdout = io::stdout();
    let mut out = stdout.lock();
    let mut chunk = Vec::new();
    let mut emitted = 0u64;
    let mut write = |models: &mut Vec<Value>, exhausted: bool| -> Result<()> {
        writeln!(out, "{}", json!({"models": std::mem::take(models), "exhausted": exhausted}))
            .and_then(|()| out.flush())
            .map_err(|e| Error::new("InvalidInput", e.to_string()))
    };
    let mut stopped = false;
    order_candidates(value, &mut |model| {
        if emitted == limit {
            stopped = true;
            return Ok(true);
        }
        chunk.push(model);
        emitted += 1;
        if chunk.len() == batch {
            write(&mut chunk, false)?;
        }
        Ok(false)
    })?;
    write(&mut chunk, !stopped)
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
