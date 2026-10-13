"""Measure the rights residues named by the committed 16c ledger.

The corpus generator and the residue ledger must agree on both case names and
source bytes. Every case is decided twice: by Lean's `document` mode (the new
path) and by Python's retained loader (the prior path), and every outcome is
compared with the prior one, not only the retained ones (16e review F2):

* `ok`: Lean accepted; the public report built from Lean's answer must equal
  the prior path's report.
* `error`: Lean rejected; the prior path must reject too (an accepted case is
  a batch failure), with the same code and text or a listed `prior_error`.
* `retained`: Lean answered `CheckerUnavailable`, or `ResourceLimit`, which
  `_lean_answer` hands to the prior path by contract; the prior path must reject
  the case as a genuinely invalid input: with any error but `CheckerUnavailable`,
  and a `ResourceLimit` only with Lean's own text (both name the same exceeded
  input limit, never an unavailable checker).
"""
from __future__ import annotations

from collections import Counter
import gzip
import hashlib
import json
import multiprocessing
from pathlib import Path
import tempfile

from tools.lean_first_diff import error_record, outcome, public, rights_corpus
from ve import document as D
from ve.errors import CheckerUnavailable, ResourceLimit, VEError

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LEDGER = ROOT / "docs/lean-first/b16c/evidence/residues.json.gz"
UNAVAILABLE = ("CheckerUnavailable", "ResourceLimit")


def prior(raw: bytes, path: Path) -> dict:
    """The retained loader's public outcome of `check_document` (`_report` of `_load_document`)."""
    return outcome(lambda: D._report(D._load_document(raw, path, None)))


def unavailable(record: dict) -> bool:
    return "raised" in record and record["raised"].get("code") in UNAVAILABLE


def decision(case: str, raw: bytes, source_hash: str) -> dict:
    with tempfile.TemporaryDirectory(prefix="b16e-case-") as directory:
        path = Path(directory) / "document.ve.md"
        path.write_bytes(raw)
        old = prior(raw, path)
        try:
            answer = D._lean_answer(raw, True)
            if answer is None:
                from ve.backends.relay import answer as relay_answer

                _, reason = relay_answer("document", {
                    "id": "document", "document": raw.decode("utf-8"), "admit": True})
                outcome_name, cause, new = "retained", str(reason), None
            else:
                report = D._report(D._lean_document(raw, path, answer, admitted=True))
                outcome_name, cause, new = "ok", None, {"returned": public(report)}
        except (CheckerUnavailable, ResourceLimit) as exc:
            outcome_name, cause, new = "retained", str(exc), None
        except VEError as exc:
            outcome_name, cause, new = "error", str(exc), {"raised": error_record(exc)}
    row = {"corpus": "rights", "case": case, "source_sha256": source_hash, "decision": outcome_name}
    if outcome_name == "ok":
        if old != new:
            raise RuntimeError(f"Lean's accepted report differs from the prior path's: {case}")
    elif outcome_name == "error":
        if "raised" not in old or unavailable(old):
            raise RuntimeError(f"Lean rejected a case the prior path accepts or cannot decide: {case}: {cause}")
        row["error"] = new["raised"]
        if old != new:
            row["prior_error"] = old["raised"]
    else:
        limit = "raised" in old and old["raised"].get("code") == "ResourceLimit" and old["raised"].get("message") == cause
        if "raised" not in old or (unavailable(old) and not limit):
            raise RuntimeError(f"valid or unavailable rights residue retained: {case}: {cause}")
        row.update({"cause": cause, "prior_error": old["raised"]})
    return row


def _decide(item: tuple[str, str, str]) -> dict:
    case, text, source_hash = item
    return decision(case, text.encode("utf-8"), source_hash)


def main() -> None:
    old = {r["case"]: r for r in json.loads(gzip.decompress(LEDGER.read_bytes()))
           if r["corpus"] == "rights"}
    if len(old) != 1250:
        raise RuntimeError(f"16c rights ledger has {len(old)} rows, expected 1250")
    with tempfile.TemporaryDirectory(prefix="b16e-corpus-") as directory:
        path = Path(directory) / "rights.json"
        rights_corpus(path)
        corpus = json.loads(path.read_text())
    if [r["case"] for r in corpus] != list(old):
        raise RuntimeError("rights corpus names or order differ from the 16c ledger")
    items = []
    for item in corpus:
        source_hash = hashlib.sha256(item["text"].encode("utf-8")).hexdigest()
        if source_hash != old[item["case"]]["source_sha256"]:
            raise RuntimeError(f"rights source changed since 16c: {item['case']}")
        items.append((item["case"], item["text"], source_hash))
    with multiprocessing.get_context("fork").Pool(8) as pool:
        rows = pool.map(_decide, items, chunksize=8)
    evidence = HERE / "evidence"
    evidence.mkdir(exist_ok=True)
    (evidence / "cases.json.gz").write_bytes(gzip.compress(json.dumps(
        rows, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode(), mtime=0))
    counts = Counter(r["decision"] for r in rows)
    share = {"rights": {"documents": len(rows), **dict(sorted(counts.items())),
                        "errors_differing_from_prior": sum("prior_error" in r for r in rows
                                                           if r["decision"] == "error")}}
    (evidence / "share.json").write_text(json.dumps(share, indent=2) + "\n")
    print(json.dumps(share), flush=True)


if __name__ == "__main__":
    main()
