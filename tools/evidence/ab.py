"""Corpus A/B: `tools/lean_first_diff.py compare` over the base's and the head's recordings, saved with the head
commit and the recordings' digests (gate item 2 of every batch that touches `ve/` or `lean/`).

    python -m tools.evidence ab BASE.jsonl HEAD.jsonl --base-commit SHA --head-commit SHA \
        --out DIR/evidence/ab.json [--delta DELTA.json] [--corpus NAME ...]

Recording stays `lean_first_diff.py record` (one run per checkout). This command refuses an empty or missing
recording before comparing (the lf-0 class: the A/B tool accepted empty evidence), runs the comparison in a
child process, and fails unless it compared every required corpus with no unlisted difference. An unavailable
pair counts only when both results are identical and the delta lists a reason (standing ruling R7).
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from tools.evidence import ROOT, EvidenceError, base_problems, dump, load

LEAN_FIRST_DIFF = ROOT / "tools/lean_first_diff.py"
# The seven corpora tools/batch_evidence.py has always required; a batch's toml may name more.
REQUIRED_CORPORA = frozenset({"probe", "conformance", "readings", "pilots", "discourse", "rights", "quantity"})


def recording_problems(path: Path) -> list[str]:
    if not Path(path).is_file():
        return [f"{path}: no recording"]
    if not any(line.strip() for line in Path(path).read_text().splitlines()):
        return [f"{path}: the recording is empty"]
    return []


def compare(base: Path, head: Path, base_commit: str, head_commit: str, delta: Path | None = None,
            corpora: list[str] | None = None) -> tuple[dict | None, list[str]]:
    """The saved comparison of two recordings and its errors (`problems`); None when it could not run."""
    errors = recording_problems(base) + recording_problems(head)
    errors += base_problems({"base_commit": base_commit, "head_commit": head_commit}, "corpus comparison")
    if errors:
        return None, errors
    with tempfile.TemporaryDirectory(prefix="ve-evidence-ab-") as scratch:
        out = Path(scratch) / "comparison.json"
        command = [sys.executable, str(LEAN_FIRST_DIFF), "compare", str(base), str(head), "--json", str(out)]
        command += ["--delta", str(delta)] if delta else []
        command += ["--corpus", *corpora] if corpora else []
        run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        if run.returncode not in (0, 1) or not out.is_file():
            return None, [f"lean_first_diff compare could not compare (exit {run.returncode}): "
                          f"{(run.stdout + run.stderr).strip()[-2000:]}"]
        comparison = load(out)
    comparison.update(base_commit=base_commit, head_commit=head_commit,
                      recordings={side: hashlib.sha256(Path(path).read_bytes()).hexdigest()
                                  for side, path in (("base", base), ("head", head))},
                      corpora=sorted(corpora) if corpora else "all")
    return comparison, problems(comparison, head_commit, corpora or REQUIRED_CORPORA)


def problems(comparison: dict, head: str, corpora=REQUIRED_CORPORA, base: str | None = None) -> list[str]:
    """The errors of a saved comparison for the batch head `head` (and, given, its merge base `base`)."""
    if not isinstance(comparison, dict):
        return ["corpus comparison is not a record"]
    errors = base_problems(comparison, "corpus comparison", base)
    if comparison.get("head_commit") != head:
        errors.append("corpus comparison did not run on HEAD")
    if comparison.get("unlisted") != 0:
        errors.append("corpus comparison has an unlisted result")
    unavailable = comparison.get("unavailable_both")
    if not isinstance(unavailable, dict) or any(type(n) is not int or n < 1 for n in unavailable.values()):
        errors.append("corpus comparison has malformed unavailable counts")
    elif unavailable:
        counted = Counter()
        rows = comparison.get("differences")
        if not isinstance(rows, list):
            errors.append("corpus comparison omitted signed unavailable rows")
        else:
            seen = set()
            for row in rows:
                if not isinstance(row, dict) or row.get("class") != "unavailable":
                    continue
                key = f"{row.get('corpus')}/{row.get('authority')}"
                counted[key] += 1
                record = (key, row.get("case"), row.get("op"))
                outcome = row.get("base")
                if (row.get("listed") is not True or record in seen or
                        json.dumps(outcome, sort_keys=True) !=
                        json.dumps(row.get("head"), sort_keys=True) or
                        not isinstance(outcome, dict) or
                        ("timeout" not in outcome and '"CheckerUnavailable' not in json.dumps(outcome))):
                    errors.append("unavailable result lacks an identical, listed R7 pair")
                seen.add(record)
            if dict(counted) != unavailable:
                errors.append("signed unavailable rows do not match corpus counts")
    records = comparison.get("records")
    compared = {key.split("/", 1)[0] for key, count in records.items() if type(count) is int and count > 0} \
        if isinstance(records, dict) else set()
    if not set(corpora) <= compared:
        errors.append("corpus comparison omitted a required corpus")
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("base", type=Path)
    parser.add_argument("head", type=Path)
    parser.add_argument("--base-commit", required=True, help="the commit BASE was recorded at")
    parser.add_argument("--head-commit", required=True, help="the commit HEAD was recorded at")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--delta", type=Path)
    parser.add_argument("--corpus", nargs="+")
    args = parser.parse_args(argv)
    try:
        comparison, errors = compare(args.base, args.head, args.base_commit, args.head_commit, args.delta,
                                     args.corpus)
    except EvidenceError as exc:
        comparison, errors = None, [str(exc)]
    if comparison is not None:
        dump(args.out, comparison)
    print("\n".join(errors) if errors else f"ab PASS: {args.out}")
    return 1 if errors else 0
