"""Measure the rights residues named by the committed 16c ledger.

The corpus generator and the residue ledger must agree on both case names and
source bytes. A retained valid document is a batch failure, not an invalid
input exception.
"""
from __future__ import annotations

from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import tempfile

from tools.lean_first_diff import rights_corpus
from ve import document as D
from ve.errors import CheckerUnavailable, ResourceLimit, VEError

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LEDGER = ROOT / "docs/lean-first/b16c/evidence/residues.json.gz"


def prior(raw: bytes, path: Path) -> dict:
    try:
        D._report(D._load_document(raw, path, None))
    except (CheckerUnavailable, ResourceLimit) as exc:
        return {"unavailable": str(exc)}
    except VEError as exc:
        return {"code": type(exc).__name__, "text": str(exc)}
    return {"valid": True}


def decision(case: str, raw: bytes, source_hash: str) -> dict:
    try:
        answer = D._lean_answer(raw, True)
        if answer is None:
            from ve.backends.relay import answer as relay_answer

            _, reason = relay_answer("document", {
                "id": "document", "document": raw.decode("utf-8"), "admit": True,
            })
            outcome, cause = "retained", str(reason)
        else:
            outcome, cause = "ok", None
    except (CheckerUnavailable, ResourceLimit) as exc:
        outcome, cause = "retained", str(exc)
    except VEError as exc:
        outcome, cause = "error", str(exc)
    row = {"corpus": "rights", "case": case, "source_sha256": source_hash,
           "decision": outcome}
    if outcome == "retained":
        with tempfile.TemporaryDirectory(prefix="b16e-invalid-") as directory:
            path = Path(directory) / "document.ve.md"
            path.write_bytes(raw)
            old = prior(raw, path)
        if old.get("valid") or old.get("unavailable"):
            raise RuntimeError(f"valid or unavailable rights residue retained: {case}: {cause}")
        row.update({"cause": cause, "prior_error": old})
    return row


def main() -> None:
    old = {r["case"]: r for r in json.loads(gzip.decompress(LEDGER.read_bytes()))
           if r["corpus"] == "rights"}
    if len(old) != 1250:
        raise RuntimeError(f"16c rights ledger has {len(old)} rows, expected 1250")
    with tempfile.TemporaryDirectory(prefix="b16e-corpus-") as directory:
        path = Path(directory) / "rights.json"
        rights_corpus(path)
        corpus = json.loads(path.read_text())
    if {r["case"] for r in corpus} != set(old):
        raise RuntimeError("rights corpus names differ from the 16c ledger")
    rows = []
    for item in corpus:
        case, raw = item["case"], item["text"].encode("utf-8")
        source_hash = hashlib.sha256(raw).hexdigest()
        if source_hash != old[case]["source_sha256"]:
            raise RuntimeError(f"rights source changed since 16c: {case}")
        rows.append(decision(case, raw, source_hash))
    evidence = HERE / "evidence"
    evidence.mkdir(exist_ok=True)
    (evidence / "cases.json.gz").write_bytes(gzip.compress(json.dumps(
        rows, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode(), mtime=0))
    counts = Counter(r["decision"] for r in rows)
    (evidence / "share.json").write_text(json.dumps({"rights": {
        "documents": len(rows), **dict(counts),
    }}, indent=2) + "\n")
    print(counts, flush=True)


if __name__ == "__main__":
    main()
