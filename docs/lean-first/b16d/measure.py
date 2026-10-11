"""Capture batch 16d's exact cases from the saved 16c residue ledger."""
from __future__ import annotations

from collections import Counter
import gzip
import json
from pathlib import Path
import tempfile

from tools.lean_first_diff import document_corpus, norm_defaults_corpus, pilot_documents
from ve import document as D
from ve.errors import CheckerUnavailable, ResourceLimit, VEError

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent / "evidence"
OLD = ROOT / "docs/lean-first/b16c/evidence/residues.json.gz"


def legacy(raw: bytes, path: Path) -> dict:
    try:
        D._report(D._load_document(raw, path, None))
    except (VEError, CheckerUnavailable) as exc:
        return {"code": type(exc).__name__, "text": str(exc)}
    return {"valid": True}


def measure(corpus: str, case: str, raw: bytes, source: str) -> dict:
    try:
        answer = D._lean_answer(raw, True)
        if answer is None:
            from ve.backends.relay import answer as relay_answer
            _, unavailable = relay_answer("document", {"id": "document", "document": raw.decode(),
                                                       "admit": True})
            decision, cause = "retained", str(unavailable)
        else:
            decision, cause = "ok", None
    except (CheckerUnavailable, ResourceLimit) as exc:
        decision, cause = "retained", str(exc)
    except VEError as exc:
        decision, cause = "error", str(exc)
    result = {"corpus": corpus, "case": case, "source_sha256": source, "decision": decision}
    if decision == "retained":
        with tempfile.TemporaryDirectory(prefix="b16d-invalid-") as directory:
            path = Path(directory) / "document.ve.md"
            path.write_bytes(raw)
            prior = legacy(raw, path)
        if prior.get("valid"):
            raise RuntimeError(f"valid residue was retained: {corpus}/{case}: {cause}")
        result.update({"cause": cause, "prior_error": prior})
    return result


def main() -> None:
    ledger = json.loads(gzip.decompress(OLD.read_bytes()))
    document_rows = {r["case"]: r for r in ledger if r["corpus"] == "document" and
                     r["cause"] == "retained: document checks under norm-defaults@0 need its Lean profile route"}
    pilot_rows = {r["case"].rsplit("/", 1)[-1]: r for r in ledger if r["corpus"] == "pilots" and
                  "norm-defaults@0 need its Lean profile route" in r["cause"]}
    norm_rows = {r["case"]: r for r in ledger if r["corpus"] == "norm_defaults"}
    assert (len(document_rows), len(pilot_rows), len(norm_rows)) == (904, 339, 1010)
    rows = []
    with tempfile.TemporaryDirectory(prefix="b16d-corpora-") as directory:
        corpus = Path(directory) / "norm.json"
        norm_defaults_corpus(corpus)
        for item in json.loads(corpus.read_text()):
            old = norm_rows[item["case"]]
            rows.append(measure("norm_defaults", item["case"], item["text"].encode(), old["source_sha256"]))
        print("norm_defaults", Counter(r["decision"] for r in rows), flush=True)
        corpus = Path(directory) / "document.json"
        document_corpus(corpus)
        for item in json.loads(corpus.read_text()):
            if item["case"] in document_rows:
                old = document_rows[item["case"]]
                rows.append(measure("document", item["case"], item["text"].encode(), old["source_sha256"]))
        print("document", Counter(r["decision"] for r in rows if r["corpus"] == "document"), flush=True)
    for name, blob, raw in pilot_documents(ROOT):
        if blob in pilot_rows:
            old = pilot_rows[blob]
            rows.append(measure("pilots", old["case"], raw, old["source_sha256"]))
    print("pilots", Counter(r["decision"] for r in rows if r["corpus"] == "pilots"), flush=True)
    assert Counter(r["corpus"] for r in rows) == {"norm_defaults": 1010, "document": 904, "pilots": 339}
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "cases.json.gz").write_bytes(gzip.compress(json.dumps(rows, sort_keys=True,
        ensure_ascii=False, separators=(",", ":")).encode(), mtime=0))
    summary = {name: {"documents": sum(r["corpus"] == name for r in rows),
                      **dict(Counter(r["decision"] for r in rows if r["corpus"] == name))}
               for name in ("norm_defaults", "document", "pilots")}
    (EVIDENCE / "share.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
