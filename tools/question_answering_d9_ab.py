"""Recheck D9's readings generator against its pre-change package construction.

Input is the JSONL query capture from ``-p tools.question_answering_agreement``.
The before side substitutes only the generator method changed by 37136ab20;
both sides use the same document, conclusion, checker, and current Lean service.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUT = ROOT / "docs/spec/question-answering-q2/evidence/d9-readings-ab.json"


def _before_packages(self):
    """The exact pre-D9 Fill_T-only method from 37136ab20^:ve/readings_verdicts.py."""
    from ve.ast import Not, formula_to_data
    from ve.entailment import prove_entailment
    from ve.norms import _bind
    from ve.readings_verdicts import BUDGET
    from ve.wire import digest

    row = self.elaboration

    def meaning(ast):
        return digest(f"ve-meaning-{self.base.identity_version}\n",
                      {"environment_id": self.base.environment_id, "ast": ast})

    fill = self._base_fill()
    packages = {}
    for target, sorts, formula in self.targets:
        conclusion = _bind(Not(formula), sorts)
        proof = prove_entailment(self.base, fill, conclusion, max_steps=BUDGET["max_steps"], _background=False)
        if proof.status != "Found":
            continue
        certificate = {**proof.certificate, "environment_id": self.base.environment_id,
                       "premise_meaning_ids": [meaning(item["ast"]) for item in row["fill"]],
                       "conclusion_meaning_id": meaning(formula_to_data(self.base, conclusion, _generated=True))}
        packages[target] = {"environment_id": row["environment_id"], "document_hash": row["document_hash"],
                            "target": target, "certificate": certificate}
    return packages


def _verdict(document: str, conclusion: object) -> dict:
    from ve.document import main
    with tempfile.TemporaryDirectory(prefix="ve-q2-d9-") as name:
        path = Path(name) / "document.ve.md"
        path.write_text(document)
        query = Path(name) / "conclusion.json"
        query.write_text(json.dumps(conclusion))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["readings", str(path), "--conclusion", str(query)])
    if code:
        raise RuntimeError(f"readings route exited {code}: {output.getvalue()[:200]}")
    answer = json.loads(output.getvalue())
    return {"verdict": answer["verdict"], "reason": answer.get("reason")}


def compare(paths: list[Path]) -> dict:
    from ve.readings_verdicts import _FilledChoiceDocument
    records = {}
    for path in paths:
        files = sorted(path.glob("*.jsonl")) if path.is_dir() else [path]
        for file in files:
            for line in file.read_text().splitlines():
                row = json.loads(line)
                if row["corpus"] != "readings":
                    continue
                key = hashlib.sha256((row["document"] + "\n" + json.dumps(row["conclusion"],
                                                                          sort_keys=True)).encode()).hexdigest()
                records[key] = row
    current = _FilledChoiceDocument._packages
    results = []
    for key, row in sorted(records.items()):
        _FilledChoiceDocument._packages = _before_packages
        try:
            before = _verdict(row["document"], row["conclusion"])
        finally:
            _FilledChoiceDocument._packages = current
        after = _verdict(row["document"], row["conclusion"])
        if after != {"verdict": row["older"], "reason": row.get("older_reason")}:
            raise RuntimeError(f"current capture changed for {key}")
        if before["verdict"] != after["verdict"] and not (
                before["verdict"] == "UNKNOWN" and after["verdict"] in {"ALL", "NONE"}):
            raise RuntimeError(f"D9 changed a decided verdict for {key}: {before} -> {after}")
        results.append({"key": key, "before": before, "after": after})
        print(f"{len(results)}/{len(records)}: {before['verdict']} -> {after['verdict']}", flush=True)
    return {"method": "readings-suite conclusions, pre-D9 Fill_T-only packages versus current generator",
            "queries": len(results), "changes": [r for r in results if r["before"]["verdict"] != r["after"]["verdict"]],
            "rows": results}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: question_answering_d9_ab.py CAPTURE_DIR...")
    result = compare([Path(arg) for arg in sys.argv[1:]])
    OUT.write_text(json.dumps(result, indent=1) + "\n")
