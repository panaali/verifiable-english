"""ME-0, decision rule D22: quote the licence field of each deep-learning candidate's page, in rank order.

Reads the pages `fetch_sources.py` pinned (plain HTTP, no model) and writes
`docs/research/evidence/math-evidence/dl-licence-check/licence-evidence.json`: per candidate, the page's SHA-256 and
the exact licence strings found. The rule: the first candidate whose licence field is a CC BY licence is pinned.

`--check` re-derives the committed file instead of writing it. A pinned page that is absent because the live page
no longer matches its SHA-256 (`fetch_sources.py` then keeps the live bytes in `raw/refetched/`) is read from there:
its licence field and the rule's result are compared, its digest is reported as differing, and the row says so.

    python3 -I research/math-evidence/licence_evidence.py [--check]
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
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


def derive(check: bool) -> tuple[dict, list[str]]:
    rows, pinned, notes = [], None, []
    for rank, name, rel, pattern in CANDIDATES:
        path = EVIDENCE / rel
        if check and not path.exists():
            path = path.parent / "refetched" / path.name
            notes.append(f"rank {rank}: pinned page absent; licence field read from the live re-fetch {path.name}, "
                         f"sha256 {hashlib.sha256(path.read_bytes()).hexdigest()} (not the pinned bytes)")
        data = path.read_bytes()
        found = sorted(set(re.findall(pattern, data.decode("utf-8", "replace"))))
        cc_by = any(re.search(r"creativecommons\.org/licenses/by/", f) for f in found)
        rows.append({"rank": rank, "candidate": name, "page": rel, "page_sha256": hashlib.sha256(data).hexdigest(),
                     "licence_field": found, "cc_by": cc_by})
        if cc_by and pinned is None:
            pinned = name
    xml = (EVIDENCE / "dl-alphafold/raw/europepmc-fulltext.xml").read_text(encoding="utf-8")
    jats = sorted(set(re.findall(r'<license[^>]*xlink:href="([^"]*)"|<ali:license_ref[^>]*>([^<]*)<', xml)))
    return ({"rule": "first ranked candidate whose licence field is CC BY (plan D22)", "pinned": pinned,
             "candidates": rows, "europepmc_jats_licence": [a or b for a, b in jats]}, notes)


def main(check: bool) -> int:
    out, notes = derive(check)
    path = EVIDENCE / "dl-licence-check/licence-evidence.json"
    if not check:
        path.write_text(json.dumps(out, indent=1) + "\n")
        print(json.dumps(out, indent=1))
        return 0
    committed = json.loads(path.read_text())
    differ = [key for key in ("rule", "pinned", "europepmc_jats_licence") if out[key] != committed[key]]
    for new, old in zip(out["candidates"], committed["candidates"]):
        for key in ("licence_field", "cc_by"):
            if new[key] != old[key]:
                differ.append(f"rank {new['rank']} {key}")
        if new["page_sha256"] != old["page_sha256"]:
            notes.append(f"rank {new['rank']}: page sha256 differs from the pin {old['page_sha256']}")
    for line in notes:
        print(line)
    print("differs:", differ or "nothing the rule reads")
    return 1 if differ else 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
