//! W6 compatibility route: relay every quantity decision to the Lean service.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::io::{BufRead, BufReader, Write};
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};
use std::sync::{Mutex, OnceLock};
use ve_kernel::{Error, Result};

struct Service {
    _child: Child,
    input: ChildStdin,
    output: BufReader<ChildStdout>,
}

fn service() -> Result<Service> {
    let executable = std::env::var_os("VE_LEAN_SERVICE")
        .map(std::path::PathBuf::from)
        .or_else(|| {
            let locations = [std::env::current_dir().ok(), std::env::current_exe().ok()];
            locations.into_iter().flatten().flat_map(|p| p.ancestors()
                .map(std::path::Path::to_path_buf).collect::<Vec<_>>()).find_map(|p| {
                    let candidate = p.join("lean/.lake/build/bin/ve_service");
                    candidate.is_file().then_some(candidate)
                })
        })
        .ok_or_else(|| Error::new("CheckerUnavailable", "Lean service executable missing"))?;
    let mut child = Command::new(executable).stdin(Stdio::piped()).stdout(Stdio::piped())
        .stderr(Stdio::null()).spawn()
        .map_err(|e| Error::new("CheckerUnavailable", e.to_string()))?;
    let input = child.stdin.take()
        .ok_or_else(|| Error::new("CheckerUnavailable", "Lean service stdin missing"))?;
    let output = child.stdout.take()
        .ok_or_else(|| Error::new("CheckerUnavailable", "Lean service stdout missing"))?;
    let mut output = BufReader::new(output);
    let mut handshake = String::new();
    output.read_line(&mut handshake)
        .map_err(|e| Error::new("CheckerUnavailable", e.to_string()))?;
    let hello: Value = serde_json::from_str(&handshake)
        .map_err(|e| Error::new("CheckerUnavailable", e.to_string()))?;
    if hello["protocol"] != 2 || hello["service"] != "ve-lean@1" {
        return Err(Error::new("CheckerUnavailable", "unexpected Lean service handshake"));
    }
    Ok(Service { _child: child, input, output })
}

static SERVICE: OnceLock<Mutex<Option<Service>>> = OnceLock::new();

/// Relay a legacy Rust quantity case to Lean's quantity service mode.
pub fn quantity_case(case: &Value) -> Result<Value> {
    let mut submitted = case.clone();
    let object = submitted.as_object_mut()
        .ok_or_else(|| Error::new("InvalidInput", "quantity case must be an object"))?;
    let kind = match object.get("mode").and_then(Value::as_str) {
        Some("document") => "document",
        Some("countermodel") => "countermodel",
        Some("certificate") => "certificate",
        _ => "admission",
    };
    object.remove("mode");
    object.insert("kind".into(), json!(kind));
    let id = object.get("id").cloned().unwrap_or(json!("quantity"));
    object.insert("id".into(), id.clone());
    let case_digest = format!("{:x}", Sha256::digest(submitted.to_string().as_bytes()));
    let mutex = SERVICE.get_or_init(|| Mutex::new(None));
    let mut guard = mutex.lock()
        .map_err(|_| Error::new("CheckerUnavailable", "Lean service lock poisoned"))?;
    if guard.is_none() { *guard = Some(service()?); }
    let connected = guard.as_mut().unwrap();
    let request = json!({"id":"rust-quantity", "mode":"quantity", "cases":[submitted]});
    writeln!(connected.input, "{request}")
        .and_then(|_| connected.input.flush())
        .map_err(|e| Error::new("CheckerUnavailable", e.to_string()))?;
    let mut line = String::new();
    connected.output.read_line(&mut line)
        .map_err(|e| Error::new("CheckerUnavailable", e.to_string()))?;
    let response: Value = serde_json::from_str(&line)
        .map_err(|e| Error::new("CheckerUnavailable", e.to_string()))?;
    if response["status"] != "ok" || response["id"] != "rust-quantity" ||
        response["mode"] != "quantity" || response["counts"]["cases"] != 1 {
        return Err(Error::new("CheckerUnavailable", "malformed Lean service response"));
    }
    let results = response["results"].as_array()
        .ok_or_else(|| Error::new("CheckerUnavailable", "missing Lean quantity result"))?;
    if results.len() != 1 {
        return Err(Error::new("CheckerUnavailable", "wrong Lean quantity result count"));
    }
    let entry = &results[0];
    if entry["index"] != 0 || entry["digest"] != case_digest || entry["result"]["id"] != id {
        return Err(Error::new("CheckerUnavailable", "misbound Lean quantity result"));
    }
    let result = &entry["result"];
    if result["status"] == "error" {
        let code = entry["code"].as_str().ok_or_else(||
            Error::new("CheckerUnavailable", "missing Lean diagnostic code"))?;
        let message = result["error"].as_str().ok_or_else(||
            Error::new("CheckerUnavailable", "missing Lean diagnostic text"))?;
        return Err(Error::new(code, message));
    }
    if result["status"] != "ok" {
        return Err(Error::new("CheckerUnavailable", "malformed Lean quantity row"));
    }
    Ok(result.clone())
}
