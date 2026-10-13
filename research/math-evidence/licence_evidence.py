"""ME-0, decision rule D22: quote the licence field of each deep-learning candidate's page, in rank order.

Reads the pages `fetch_sources.py` pinned (plain HTTP, no model) and writes
`docs/research/evidence/math-evidence/dl-licence-check/licence-evidence.json`: per candidate, the page's SHA-256 and
the exact licence strings found. The rule: the first candidate whose licence field is a CC BY licence is pinned.

    python3 -I research/math-evidence/licence_evidence.py
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/math-evidence"

CANDIDATES = [
    ("1", "LoRA (arXiv 2106.09685)", "dl-licence-check/raw/arxiv-2106.09685-abs.html",
     r'href="(http[^"]*arxiv\.org/licenses/[^"]*|http[^"]*creativecommons\.org/licenses/[^"]*)"[^>]*title="Rights to this article"'),
    ("2", "Vision Transformers Need Registers (arXiv 2309.16588)", "dl-licence-check/raw/arxiv-2309.16588-abs.html",
     r'href="(http[^"]*arxiv\.org/licenses/[^"]*|http[^"]*creativecommons\.org/licenses/[^"]*)"[^>]*title="Rights to this article"'),
    ("3", "AlphaFold (Nature 596, 583-589, doi:10.1038/s41586-021-03819-2)", "dl-alphafold/raw/nature-article.html",
     r'"license":"([^"]*)"'),
]


def main() -> None:
    rows, pinned = [], None
    for rank, name, rel, pattern in CANDIDATES:
        data = (EVIDENCE / rel).read_bytes()
        found = sorted(set(re.findall(pattern, data.decode("utf-8", "replace"))))
        cc_by = any(re.search(r"creativecommons\.org/licenses/by/", f) for f in found)
        rows.append({"rank": rank, "candidate": name, "page": rel, "page_sha256": hashlib.sha256(data).hexdigest(),
                     "licence_field": found, "cc_by": cc_by})
        if cc_by and pinned is None:
            pinned = name
    xml = (EVIDENCE / "dl-alphafold/raw/europepmc-fulltext.xml").read_text(encoding="utf-8")
    jats = sorted(set(re.findall(r'<license[^>]*xlink:href="([^"]*)"|<ali:license_ref[^>]*>([^<]*)<', xml)))
    out = {"rule": "first ranked candidate whose licence field is CC BY (plan D22)", "pinned": pinned,
           "candidates": rows, "europepmc_jats_licence": [a or b for a, b in jats]}
    path = EVIDENCE / "dl-licence-check/licence-evidence.json"
    path.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
