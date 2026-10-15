"""Bounded before/after timing of Q2.4 document reports, without model calls.

Both roots must have built `lean/.lake/build/bin/ve_service`. The before root is
the archive of 4edf751ef^, before the words mode replaced Python wording.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


NORM_REPORT = """
import sys
from conformance import norm_defaults_differential as generator
from conformance import frozen_norm_defaults as oracle
from ve import norm_defaults_english as english
from ve.model import FiniteModel
from ve.norm_defaults import UnspecifiedDocument, report, search_reached
from ve.norm_defaults_route import run_case
env, rules, raw = generator.case(int(sys.argv[1]), profiled=True)
frozen = oracle.UnspecifiedDocument(env, rules)
document = UnspecifiedDocument(env, rules)
situation = FiniteModel.from_dict(document.situation_environment(), raw)
english.legend(env)
for case, _, kind in generator.point_cases(frozen, raw):
    row = run_case(case)
    if row.get('status') != 'ok':
        continue
    if kind.startswith('conflict:'):
        if row.get('verdict') == 'CONFLICT' and row.get('kind') == 'latent':
            english.latent_conflict_sentence(document, situation, row)
    elif kind != 'table3' and 'point_status' in row:
        english.status_sentence(document, situation, row)
for line in report(document, model=raw)['report']:
    if line.get('reached') == 'reachable' and 'witness' in line:
        english.gap_sentence(document, situation, line)
for predicate in document.unspec:
    english.completion_question(document, predicate, search_reached(document, predicate))
"""


def one(root: Path, document: Path, python: Path, rust: Path, git_dir: Path,
        norm_seed: int | None = None) -> dict:
    if norm_seed is None:
        code = "from pathlib import Path; from ve.document import check_document; " \
               "import sys; check_document(Path(sys.argv[1]))"
        argument = str(document)
    else:
        code, argument = NORM_REPORT, str(norm_seed)
    command = ["/usr/bin/time", "-f", "Q2_WORDS_TIME %e %U %S", str(python), "-c", code, argument]
    env = os.environ.copy()
    env["VE_RUST_JSONL"] = str(rust)
    env["GIT_DIR"] = str(git_dir)
    done = subprocess.run(command, cwd=root, env=env, text=True, capture_output=True)
    timing = next((line for line in done.stderr.splitlines() if line.startswith("Q2_WORDS_TIME ")), None)
    if done.returncode or timing is None:
        raise RuntimeError(f"{root} {document}: exit {done.returncode}: {done.stderr[-1000:]}")
    wall, user, system = map(float, timing.split()[1:])
    return {"wall_s": wall, "cpu_s": round(user + system, 2)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    parser.add_argument("--rust", type=Path, help="one Rust executable used in both revisions")
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument("--norm-seed", type=int, help="also time the norm-defaults report for this generator seed")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("documents", nargs="+", type=Path)
    args = parser.parse_args()
    rust = (args.rust or args.after / "rust/target/release/ve").absolute()
    if not rust.is_file():
        parser.error(f"Rust executable is missing: {rust}")
    git_dir = Path(subprocess.check_output(["git", "-C", str(args.after), "rev-parse", "--path-format=absolute",
                                            "--git-common-dir"], text=True).strip())
    records = []
    cases = [(document.name, document, None) for document in args.documents]
    if args.norm_seed is not None:
        cases.append((f"norm-defaults-seed-{args.norm_seed}", Path(f"seed-{args.norm_seed}"), args.norm_seed))
    for name, document, norm_seed in cases:
        for label, root in (("before", args.before), ("after", args.after)):
            for run in range(args.runs):
                figures = one(root.resolve(), document.resolve(), args.python.absolute(), rust, git_dir, norm_seed)
                sha = hashlib.sha256(document.read_bytes()).hexdigest() if norm_seed is None else None
                records.append({"document": name, "sha256": sha,
                                "revision": label, "run": run + 1, **figures})
                print(records[-1], flush=True)
    args.out.write_text(json.dumps({"method": "cold check_document (readings and pilot) or generator report "
                                              "(norm-defaults); GNU time wall and user+system CPU, including "
                                              f"reaped Lean service children; {args.runs} runs per case",
                                    "before": "4edf751ef^", "after": "qa-q2 final candidate",
                                    "rust_sha256": hashlib.sha256(rust.read_bytes()).hexdigest(),
                                    "rows": records}, indent=2) + "\n")


if __name__ == "__main__":
    main()
