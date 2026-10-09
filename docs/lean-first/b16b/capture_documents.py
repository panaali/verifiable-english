"""Freeze the `document` corpus of `tools/lean_first_diff.py` (lean-first batch 16b).

Every `ve-document@1` seed of `conformance/document_wrapper.py` as it is, then the differential fuzzer's document
mutants (`tools/difffuzz.py` `DocumentSurface`, `sample` with a fixed seed): `ONES` 1-fault and `TWOS` 2-fault
mutants. The file holds each seed's `{"front", "body"}` once and each mutant as its seed and mutations;
`texts` writes every entry as its document text (`document_wrapper.text_of` of `difffuzz.apply_all`). The corpus
is written once, at the batch base, so the base and the head are recorded over the same texts:

    python docs/lean-first/b16b/capture_documents.py [--out docs/lean-first/document-corpus.json.gz]
"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/lean-first/document-corpus.json.gz"
SEED, ONES, TWOS = 16, 1500, 300


def entries() -> list[dict]:
    sys.path.insert(0, str(ROOT))
    from conformance import document_wrapper as dw
    from tools import difffuzz
    surface = difffuzz.DocumentSurface()
    seeds = [difffuzz.Seed("document", "document@1" if dw.owned(doc) else "document@1:unowned", name, doc,
                           ("python", "lean")) for name, doc in dw.seeds()]
    rows = [{"id": f"seed/{seed.id}", "seed": seed.id, "mutations": []} for seed in seeds]
    fuzzed = [seed for seed in seeds if dw.fuzzed(seed.root)]
    for index, (seed, mutations) in enumerate(
            difffuzz.sample(surface, fuzzed, ONES, TWOS, random.Random(SEED))[len(fuzzed):]):
        rows.append({"id": f"mutant/{index}", "seed": seed.id, "mutations": mutations})
    return {"seeds": {seed.id: seed.root for seed in seeds}, "entries": rows}


def texts(corpus: dict) -> list[dict]:
    """`[{"id", "text"}]`: every entry of a corpus `entries` wrote, as its document text."""
    sys.path.insert(0, str(ROOT))
    from conformance import document_wrapper as dw
    from tools import difffuzz
    return [{"id": entry["id"],
             "text": dw.text_of(difffuzz.apply_all(corpus["seeds"][entry["seed"]], entry["mutations"]))}
            for entry in corpus["entries"]]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    data = json.dumps(entries(), ensure_ascii=False, sort_keys=True).encode("utf-8")
    args.out.write_bytes(gzip.compress(data, mtime=0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
