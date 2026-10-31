//! The generated contract tables (docs/spec/wire-contract-s4-2.md 4 and 9): every embedded
//! hash equals its lock entry, and every table's rows can be dumped for the comparison with the
//! rows `tools/wire_contract.py` reads from the contract JSON (`tests/test_wire_contract_rust.py`).
mod corpus_tables;

use serde_json::{Value as Json, json};
use std::path::Path;
use ve_kernel::contract::*;
use ve_kernel::contract_tables;

fn modules() -> [(&'static [Source], &'static [&'static Table], &'static str); 2] {
    [
        (contract_tables::SOURCES, contract_tables::TABLES, "ve/wire_contract/contracts.lock"),
        (corpus_tables::SOURCES, corpus_tables::TABLES, "conformance/wire-contract/contracts/contracts.lock"),
    ]
}

#[test]
fn embedded_hashes_equal_their_lock_entries() {
    for (sources, tables, lock) in modules() {
        let path = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..").join(lock);
        let lock: Json = serde_json::from_slice(&std::fs::read(&path).unwrap()).unwrap();
        for source in sources {
            let entry = &lock[source.file];
            assert_eq!(entry["sha256"], source.sha256, "{} in {}", source.file, path.display());
            assert_eq!(entry["revision"], source.revision, "{} in {}", source.file, path.display());
        }
        for table in tables {
            let file = format!("{}.json", table.contract);
            let source = sources.iter().find(|s| s.file == file).expect("a table without a source");
            assert_eq!(source.revision, table.revision, "{file}");
        }
    }
}

fn kind_word(kind: &Kind) -> &'static str {
    match kind {
        Kind::HasType(_) => "type",
        Kind::ExactKeys(_) => "exact_keys",
        Kind::Keys(..) => "keys",
        Kind::Const(_) => "const",
        Kind::OneOf(_) => "enum",
        Kind::MaxItems(_) => "max_items",
        Kind::MaxBytes(_) => "max_bytes",
        Kind::MaxCount(..) => "max_count",
        Kind::Name(..) => "name",
        Kind::SortedUnique => "sorted_unique",
        Kind::UniqueSoFar => "unique_so_far",
        Kind::DeclaredIn(_) => "declared_in",
        Kind::RequiresMember(_) | Kind::RequiresItem(_) => "requires",
        Kind::ExcludesMember(_) | Kind::ExcludesItem(_) => "excludes",
        Kind::Hook(_) => "hook",
        Kind::Classifier(..) => "classifier",
    }
}

fn text(pieces: &[Piece]) -> Json {
    let word = |r: &Renderer| match r {
        Renderer::Raw => "raw",
        Renderer::Json => "json",
        Renderer::Index => "index",
        Renderer::Count => "count",
        Renderer::List => "list",
    };
    pieces
        .iter()
        .map(|p| match p {
            Piece::Lit(s) => json!(["lit", s]),
            Piece::Arg(name, r) => json!(["arg", name, word(r)]),
        })
        .collect()
}

fn row(contract: &str, rows: &[Json], phase: &str, id: &str, kind: &str) -> Json {
    json!({"contract": contract, "position": rows.len(), "phase": phase, "id": id, "kind": kind,
           "code": null, "class": null, "text": null, "limit": null, "keys": null, "args": []})
}

fn walk(contract: &str, phase: &str, entries: &[Entry], rows: &mut Vec<Json>) {
    for entry in entries {
        match entry {
            Entry::Check(c) => {
                let mut r = row(contract, rows, phase, c.id, kind_word(&c.kind));
                r["code"] = json!(c.code);
                r["class"] = json!(c.cls);
                r["text"] = text(c.text);
                r["args"] = c.args.iter().map(|(name, _)| json!(name)).collect();
                match c.kind {
                    Kind::MaxItems(n) | Kind::MaxBytes(n) | Kind::MaxCount(_, n) => r["limit"] = json!(n),
                    Kind::ExactKeys(keys) => r["keys"] = json!([keys]),
                    Kind::Keys(required, optional) => r["keys"] = json!([required, optional]),
                    _ => {}
                }
                rows.push(r.clone());
                if let Kind::Classifier(_, members) = c.kind {
                    for m in members {
                        let mut member = r.clone();
                        member["position"] = json!(rows.len());
                        member["id"] = json!(m.id);
                        member["kind"] = json!("member");
                        member["code"] = json!(m.code);
                        member["class"] = json!(m.cls);
                        member["text"] = text(m.text);
                        member["args"] = json!([]);
                        rows.push(member);
                    }
                }
            }
            Entry::Each(id, _, _, inner) => {
                rows.push(row(contract, rows, phase, id, "each"));
                walk(contract, phase, inner, rows);
            }
            Entry::Scope(id, _, _, recode, inner) => {
                let mut r = row(contract, rows, phase, id, "include");
                if let Some((code, cls)) = recode {
                    r["code"] = json!(code);
                    r["class"] = json!(cls);
                }
                rows.push(r);
                walk(contract, phase, inner, rows);
            }
        }
    }
}

/// Every table's rows; written as JSON lines to `$VE_CONTRACT_DUMP` when it is set.
#[test]
fn dump_rows() {
    let mut lines = String::new();
    for (_, tables, _) in modules() {
        for table in tables {
            let mut rows = Vec::new();
            for phase in table.phases {
                walk(table.contract, phase.name, phase.entries, &mut rows);
            }
            assert!(!rows.is_empty(), "{}", table.contract);
            for r in rows {
                lines.push_str(&r.to_string());
                lines.push('\n');
            }
        }
    }
    if let Some(path) = std::env::var_os("VE_CONTRACT_DUMP") {
        std::fs::write(path, lines).unwrap();
    }
}
