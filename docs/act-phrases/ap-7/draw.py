"""AP-7's constitution draw: 30 norm sentences with *and*, *or* or *nor* inside the verb phrase (PRE-REGISTRATION.md).

    python3 docs/act-phrases/ap-7/draw.py [--population]

With `--population` it first copies the 669 "norms" units (id, excerpt, full text) of the pinned constitution run into
population.json; without it, it draws from that saved file, so the draw needs no file outside the repository. It
prints the drawn ids and writes draw.json. No model call.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random
import re
import sys

HERE = Path(__file__).resolve().parent
RUN = Path("/home/seyran/code/manage-agents/pilots/claude-constitution/run-20261012T1800Z/units.json")
RUN_SHA256 = "353a75284fd4fb9921d4079a55a235bcf8be06061cd1005d1367e956f255ec4c"
SOURCE = RUN.parents[1] / "source/claude-constitution.md"
SOURCE_SHA256 = "fa10ed489e758ab009fe420954a385afbe3b11978afd79c4e9f4ae97e02d50dd"
SEED = "act-phrases-AP7"
COUNT = 30
# A verb phrase opens at a modal or a wish word; *and*, *or* or *nor* after it is inside the verb phrase.
OPENERS = {"should", "shouldn't", "must", "mustn't", "may", "can", "cannot", "can't", "never", "ought", "need",
           "needs", "want", "wants"}
JOINS = {"and", "or", "nor"}


def words(text: str) -> list[str]:
    return re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower().replace("’", "'"))


def eligible(excerpt: str) -> bool:
    ws = words(excerpt)
    first = next((i for i, w in enumerate(ws) if w in OPENERS), None)
    return first is not None and any(w in JOINS for w in ws[first + 1:])


def population() -> list[dict]:
    """The run's "norms" units: id, the (cut-off) excerpt the draw reads, and the full sentence from the span."""
    data, source = RUN.read_bytes(), SOURCE.read_bytes()
    if (hashlib.sha256(data).hexdigest(), hashlib.sha256(source).hexdigest()) != (RUN_SHA256, SOURCE_SHA256):
        raise SystemExit("the pinned constitution run or source changed")
    units = [u for u in json.loads(data) if u.get("missing_feature") == "norms"]
    return [{"id": u["id"], "excerpt": u["source_excerpt"],
             "text": " ".join(source[u["span"][0]:u["span"][1]].decode("utf-8").split())} for u in units]


def draw(units: list[dict]) -> dict:
    pool = sorted(u["id"] for u in units if eligible(u["excerpt"]))
    return {"seed": SEED, "population": len(units), "eligible": len(pool),
            "drawn": random.Random(SEED).sample(pool, COUNT)}


if __name__ == "__main__":
    if sys.argv[1:] == ["--population"]:
        (HERE / "population.json").write_text(
            "[\n" + ",\n".join(json.dumps(u, ensure_ascii=False) for u in population()) + "\n]\n")
    elif sys.argv[1:]:
        raise SystemExit("usage: draw.py [--population]")
    result = draw(json.loads((HERE / "population.json").read_text()))
    (HERE / "draw.json").write_text(json.dumps(result, indent=1) + "\n")
    print(" ".join(result["drawn"]))
