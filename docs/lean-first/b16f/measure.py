"""Measure batch 16f's residues: the rows of the committed 16c ledger that batches 16d and 16e did not take.

16d took the norm-defaults rows (the `norm_defaults` corpus, the document corpus's exact norm-defaults cause and the
pilots under it), 16e the `rights` corpus, and the eight `ve-document@2` pilots are the discourse route's. Of the 130
rows left, the batch's groups (`GROUPS`) are soft norms, norm content, senses, fenced content, distinguishing models,
and the malformed-profile and environment-key groups. The other twelve rows (pilots under `order@0`, `readings@1` or
`rights@0`) are named by no batch's groups: they are measured and saved with `"outside": true`, and a valid one that
stays on the retained path is reported, not counted as this batch's failure.

A pilot is written as it is loaded in place, with the files its front matter names beside it as its branch holds
them (`lean_first_diff.write_pilot`: a senses document's pack; review F2). The corpus generators and the ledger must
agree on case names and source bytes. Every case is decided twice, by
Lean's `document` mode (the new path) and by Python's retained loader (the prior path), and compared as 16e's
`measure.py` compares them:

* `ok`: Lean accepted; the public report built from Lean's answer must equal the prior path's report.
* `error`: Lean rejected; the prior path must reject too, with the same code and text or a listed `prior_error`.
* `retained`: Lean answered `CheckerUnavailable` or `ResourceLimit` (`_lean_answer` hands both to the prior path);
  the prior path must reject the case as a genuinely invalid input: any error but `CheckerUnavailable`, and a
  `ResourceLimit` only with Lean's own text.
"""
from __future__ import annotations

from collections import Counter
import gzip
import json
import multiprocessing
from pathlib import Path
import sys
import tempfile

from tools.lean_first_diff import document_corpus, error_record, outcome, pilot_documents, public, write_pilot
from ve import document as D
from ve.errors import CheckerUnavailable, ResourceLimit, VEError

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LEDGER = ROOT / "docs/lean-first/b16c/evidence/residues.json.gz"
UNAVAILABLE = ("CheckerUnavailable", "ResourceLimit")
NORM_DEFAULTS = "retained: document checks under norm-defaults@0 need its Lean profile route"


def ours(row: dict) -> bool:
    """Whether a 16c ledger row is this batch's, not 16d's, 16e's or the discourse route's."""
    if row["corpus"] in ("norm_defaults", "rights") or row["cause"].startswith("discourse route"):
        return False
    if row["corpus"] == "document":
        return row["cause"] != NORM_DEFAULTS
    return not (row["corpus"] == "pilots" and "norm-defaults@0 need its Lean profile route" in row["cause"])


GROUPS = ("soft norms", "norm content", "senses", "fenced content", "distinguishing models", "environment key",
          "malformed profile")


def group(cause: str) -> str:
    """The batch's name for a 16c ledger cause."""
    for needle, name in (("soft-norms@0", "soft norms"), ("norm content", "norm content"),
                         ("senses", "senses"), ("fenced", "fenced content"),
                         ("distinguishing model", "distinguishing models"), ("environment block", "environment key"),
                         ("readings@1", "readings@1 pilots"), ("rights@0", "rights@0 pilots"),
                         ("order@0", "order@0")):
        if needle in cause:
            return name
    return "malformed profile"


def prior(raw: bytes, path: Path) -> dict:
    """The retained loader's public outcome of `check_document` (`_report` of `_load_document`)."""
    return outcome(lambda: D._report(D._load_document(raw, path, None)))


def unavailable(record: dict) -> bool:
    return "raised" in record and record["raised"].get("code") in UNAVAILABLE


def decision(item: tuple[str, str, str, str, bytes]) -> dict:
    corpus, case, source_hash, old_cause, raw = item
    with tempfile.TemporaryDirectory(prefix="b16f-case-") as directory:
        if corpus == "pilots":
            # A pilot is checked as it is loaded in place, with the files it names beside it (review F2).
            name, blob = case.rsplit("/", 1)
            path = write_pilot(ROOT, Path(directory), name, blob, raw)
        else:
            path = Path(directory) / "document.ve.md"
            path.write_bytes(raw)
        old = prior(raw, path)
        try:
            answer = D._lean_answer(raw, True, path.parent)
            if answer is None:
                from ve.backends.relay import answer as relay_answer
                _, reason = relay_answer("document", D._document_case(raw, True, path.parent) or
                                         {"id": "document", "document": raw.decode("utf-8"), "admit": True})
                name, cause, new = "retained", str(reason), None
            else:
                report = D._report(D._lean_document(raw, path, answer, admitted=True))
                name, cause, new = "ok", None, {"returned": public(report)}
        except (CheckerUnavailable, ResourceLimit) as exc:
            name, cause, new = "retained", str(exc), None
        except VEError as exc:
            name, cause, new = "error", str(exc), {"raised": error_record(exc)}
    row = {"corpus": corpus, "case": case, "source_sha256": source_hash, "group": group(old_cause),
           "decision": name}
    problem = None
    if name == "ok":
        if old != new:
            problem = "Lean's accepted report differs from the prior path's"
    elif name == "error":
        row["error"] = new["raised"]
        if "raised" not in old or unavailable(old):
            problem = "Lean rejected a case the prior path accepts or cannot decide"
        elif old != new:
            row["prior_error"] = old["raised"]
    else:
        row["cause"] = cause
        limit = "raised" in old and old["raised"].get("code") == "ResourceLimit" and old["raised"].get("message") == cause
        if "raised" not in old or (unavailable(old) and not limit):
            problem = "a valid or undecidable residue is retained"
        else:
            row["prior_error"] = old["raised"]
    if row["group"] not in GROUPS:
        row["outside"] = True
        if problem:
            row["outside_problem"] = problem
    elif problem:
        row["problem"] = problem
    return row


def items() -> list[tuple[str, str, str, str, bytes]]:
    ledger = [r for r in json.loads(gzip.decompress(LEDGER.read_bytes())) if ours(r)]
    if len(ledger) != 130:
        raise RuntimeError(f"16c ledger has {len(ledger)} rows for batch 16f, expected 130")
    documents = {r["case"]: r for r in ledger if r["corpus"] == "document"}
    pilots = {r["case"].rsplit("/", 1)[-1]: r for r in ledger if r["corpus"] == "pilots"}
    out = []
    with tempfile.TemporaryDirectory(prefix="b16f-corpus-") as directory:
        path = Path(directory) / "document.json"
        document_corpus(path)
        for entry in json.loads(path.read_text()):
            if entry["case"] in documents:
                old = documents.pop(entry["case"])
                out.append(("document", entry["case"], old["source_sha256"], old["cause"], entry["text"].encode()))
    for _name, blob, raw in pilot_documents(ROOT):
        if blob in pilots:
            old = pilots.pop(blob)
            out.append(("pilots", old["case"], old["source_sha256"], old["cause"], raw))
    if documents or pilots:
        raise RuntimeError(f"ledger cases missing from the corpora: {sorted(documents) + sorted(pilots)}")
    import hashlib
    for corpus, case, source_hash, _, raw in out:
        if corpus == "document" and hashlib.sha256(raw).hexdigest() != source_hash:
            raise RuntimeError(f"document source changed since 16c: {case}")
    return out


def main() -> None:
    work = items()
    with multiprocessing.get_context("fork").Pool(8) as pool:
        rows = pool.map(decision, work, chunksize=1)
    problems = [r for r in rows if "problem" in r]
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence"
    out.mkdir(parents=True, exist_ok=True)
    (out / "cases.json.gz").write_bytes(gzip.compress(json.dumps(
        rows, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode(), mtime=0))
    share = {}
    for name in sorted({r["group"] for r in rows}):
        mine = [r for r in rows if r["group"] == name]
        share[name] = {"cases": len(mine), **dict(sorted(Counter(r["decision"] for r in mine).items()))}
    share["problems"] = len(problems)
    share["outside_valid_retained"] = sum("outside_problem" in r for r in rows)
    (out / "share.json").write_text(json.dumps(share, indent=2) + "\n")
    print(json.dumps(share, indent=1), flush=True)
    for r in problems:
        print("PROBLEM", r["corpus"], r["case"], r["problem"], r.get("cause"), flush=True)
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
