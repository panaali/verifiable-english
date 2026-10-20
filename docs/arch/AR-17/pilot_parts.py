"""AR-17's corpus A/B: `tools/lean_first_diff.py`'s corpora, its pilots corpus narrowed to the readings parts (L70).

    uv run python docs/arch/AR-17/pilot_parts.py record --root DIR --out FILE [--workers N]
    uv run python docs/arch/AR-17/pilot_parts.py compare BASE HEAD --base-commit SHA --head-commit SHA \
        --out FILE [--delta DELTA.json]

The task names the UDHR and constitution pilots' readings part documents and forbids whole-UDHR and
whole-constitution runs (PIPELINE-LIMITS L70: 18-30 GB and 11-18 min each, unavailable on both sides). `selected`
is that rule: the UDHR pilot's `translation-part<n>` documents and the constitution pilot's `readings/` documents
except the whole ones (`all-*`, `nd-all`), and any `udhr-part<n>` document. `record` appends the tool's own record
(`pilot_check` of `ve document check`, written by `write_pilot`) of each selected document to FILE, which already
holds the other corpora from `lean_first_diff.py record --corpus ...`. `compare` is the tool's `compare` over
both recordings, expecting every case of those corpora and exactly the selected pilot documents, saved with the
commits and the recordings' digests as `python -m tools.evidence ab` saves it.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import lean_first_diff as diff  # noqa: E402

OTHER = ("probe", "conformance", "readings", "discourse", "rights", "quantity", "norm_defaults", "document")


def selected(name: str) -> bool:
    branch, _, path = name.partition(":")
    leaf = path.rsplit("/", 1)[-1]
    if re.fullmatch(r"udhr-part\d+\.ve\.md", leaf):
        return True
    if branch.startswith("pilot/udhr-"):
        return re.fullmatch(r"translation-part\d+\.ve\.md", leaf) is not None
    if branch.startswith("pilot/cc-"):
        return "/readings/" in path and not leaf.startswith(("all-", "nd-all"))
    return False


def documents():
    return [doc for doc in diff.pilot_documents(ROOT) if selected(doc[0])]


def record(root: Path, out: Path, workers: int) -> int:
    scratch = out.with_suffix(".pilot-parts")
    scratch.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONPATH": str(root), "VE_SHADOW_LOG": str(scratch / "english-shadow.jsonl")}
    env.pop("VE_AUTHORITY", None)

    def check(item):
        name, blob, text = item
        path = diff.write_pilot(ROOT, scratch, name, blob, text)
        return {"corpus": "pilots", "case": name, "op": "document_check", "source_sha256": blob,
                "authority": "default", "outcome": diff.pilot_check(root, path, env)}
    with open(out, "a") as handle, ThreadPoolExecutor(max_workers=workers) as pool:
        for row in pool.map(check, documents()):
            handle.write(diff.line(row))
    return 0


def compare(args) -> int:
    expected = diff.expected_cases(ROOT, OTHER)
    # The selected documents the base recording holds: a pilot branch added after it is in neither side's corpus.
    rows = (json.loads(line) for line in args.base.read_text().split("\n") if line.strip())
    recorded = {row["case"] for row in rows if row.get("corpus") == "pilots"}
    expected[("pilots", "default")] = {name: diff.only("document_check") for name, _, _ in documents()
                                       if name in recorded}
    delta = json.loads(args.delta.read_text()) if args.delta else None
    comparison = diff.compare(str(args.base), str(args.head), delta, expected=expected)
    comparison.update(base_commit=args.base_commit, head_commit=args.head_commit,
                      recordings={side: hashlib.sha256(Path(path).read_bytes()).hexdigest()
                                  for side, path in (("base", args.base), ("head", args.head))},
                      corpora=sorted((*OTHER, "pilots")),
                      pilots="the readings part documents only (L70): docs/arch/AR-17/pilot_parts.py `selected`")
    args.out.write_text(json.dumps(comparison, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({key: comparison[key] for key in ("totals", "records", "unavailable_both", "unlisted")}))
    return 0 if comparison["unlisted"] == 0 else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("record")
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--workers", type=int, default=4)
    p = sub.add_parser("compare")
    p.add_argument("base", type=Path)
    p.add_argument("head", type=Path)
    p.add_argument("--base-commit", required=True)
    p.add_argument("--head-commit", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--delta", type=Path)
    args = parser.parse_args(argv)
    if args.command == "record":
        return record(args.root.resolve(), args.out.resolve(), args.workers)
    return compare(args)


if __name__ == "__main__":
    raise SystemExit(main())
