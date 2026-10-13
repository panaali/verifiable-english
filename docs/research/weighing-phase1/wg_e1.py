"""WG-E1: do collisions between different acts need a new construct?

Pre-registered in docs/research/weighing.md section 2.1 and docs/research/weighing-phase1.md
section 2 before any unit was drawn. Reads the constitution pilot of run 20261012T1800Z from git at a
pinned commit (never a checkout), so the inputs stay read-only. No model call.

    python3 docs/research/weighing-phase1/wg_e1.py screen   # the CROSSACT population
    python3 docs/research/weighing-phase1/wg_e1.py draw     # the 40 units, with their source context
    python3 docs/research/weighing-phase1/wg_e1.py tally    # the bar, from the reader's classification
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs" / "research" / "evidence" / "weighing"

# The pilot branch pilot/cc-20261012T1800Z, pinned.
PILOT_COMMIT = "ecfd1ace71eaf87b1518e163aa5041cfbad064e0"
RUN = "usecases/claude-constitution-pilot/run-20261012T1800Z"
SOURCE = "usecases/claude-constitution-pilot/source/claude-constitution.md"
SOURCE_SHA256 = "fa10ed489e758ab009fe420954a385afbe3b11978afd79c4e9f4ae97e02d50dd"

SEED = 20261012
SAMPLE_SIZE = 40
SECOND_READER_SIZE = 10  # the first ten units in draw order
CONTEXT_BYTES = 400

# CROSSACT (research 2.1). A unit is in the class when its text sets courses of action against each
# other (group A) or names both helping and refusing (group B). Case-insensitive, whole words.
CONTRAST = {
    "rather than": r"\brather than\b",
    "instead": r"\binstead\b",
    "versus": r"\b(?:versus|vs\.?)(?=\s|$)",
    "at the expense of": r"\bat the expense of\b",
    "in favour of": r"\bin favou?r of\b",
    "trade-off": r"\btrade-?offs?\b",
    "weigh": r"\b(?:out)?weigh(?:s|ed|ing)?\b",
    "balance": r"\bbalanc(?:e|es|ed|ing)\b",
    "conflict": r"\bconflict(?:s|ed|ing)?\b",
    "tension": r"\btensions?\b",
    "compete": r"\b(?:compete|competes|competing|competition)\b",
    "prioritise": r"\bpriorit(?:y|ies|ise|ises|ised|ising|ize|izes|ized|izing|ization|isation)\b",
    "alternative": r"\balternatives?\b",
    "option": r"\boptions?\b",
    "choose": r"\b(?:choose|chooses|choosing|chose|chosen|choice|choices)\b",
    "either": r"\beither\b",
}
HELP_SIDE = r"\b(?:help\w*|assist\w*|compl(?:y|ies|ied|ying|iance)|fulfil\w*|provid\w*)\b"
REFUSE_SIDE = (r"\b(?:refus\w*|declin\w*|reject\w*|withh(?:o|e)ld\w*|unhelpful\w*|turn(?:s|ed|ing)? down|"
               r"push(?:es|ed|ing)? back|conscientious(?:ly)? object\w*|say(?:s|ing)? no)\b")


def crossact_cues(text: str) -> list[str]:
    cues = [name for name, pattern in CONTRAST.items() if re.search(pattern, text, re.IGNORECASE)]
    if re.search(HELP_SIDE, text, re.IGNORECASE) and re.search(REFUSE_SIDE, text, re.IGNORECASE):
        cues.append("help and refuse")
    return cues


def git_show(path: str) -> bytes:
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{PILOT_COMMIT}:{path}"],
                          check=True, capture_output=True).stdout


def load_inputs() -> tuple[list[dict], bytes]:
    units = json.loads(git_show(f"{RUN}/units.json"))
    source = git_show(SOURCE)
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise SystemExit("the pinned source does not match metrics.json's source_sha256")
    return units, source


def population(units: list[dict]) -> list[dict]:
    """Units whose primary blocker is `norms` and whose text is in CROSSACT, in ledger order."""
    rows = []
    for unit in units:
        if unit.get("missing_feature") != "norms":
            continue
        cues = crossact_cues(unit["source_excerpt"])
        if cues:
            rows.append({"id": unit["id"], "cues": cues})
    return rows


def line_of(source: bytes, offset: int) -> int:
    return source.count(b"\n", 0, offset) + 1


def write_json(name: str, data: object) -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / name).write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def screen() -> list[dict]:
    units, _ = load_inputs()
    norms = sum(1 for u in units if u.get("missing_feature") == "norms")
    rows = population(units)
    cue_counts: dict[str, int] = {}
    for row in rows:
        for cue in row["cues"]:
            cue_counts[cue] = cue_counts.get(cue, 0) + 1
    write_json("wg-e1-population.json", {
        "pilot_commit": PILOT_COMMIT, "run": RUN, "norms_units": norms, "crossact_units": len(rows),
        "cue_counts": dict(sorted(cue_counts.items())), "units": rows})
    print(f"norms units {norms}; CROSSACT units {len(rows)}")
    return rows


def draw() -> None:
    units, source = load_inputs()
    by_id = {u["id"]: u for u in units}
    rows = population(units)
    ids = [row["id"] for row in rows]
    drawn = ids if len(ids) <= SAMPLE_SIZE else random.Random(SEED).sample(ids, SAMPLE_SIZE)
    sample = []
    for order, unit_id in enumerate(drawn, start=1):
        unit = by_id[unit_id]
        start, end = unit["span"]
        sample.append({
            "order": order, "id": unit_id, "span": [start, end],
            "lines": [line_of(source, start), line_of(source, max(start, end - 1))],
            "second_reader": order <= SECOND_READER_SIZE,
            "cues": crossact_cues(unit["source_excerpt"]),
            "excerpt": unit["source_excerpt"],
            "before": source[max(0, start - CONTEXT_BYTES):start].decode("utf-8", "replace"),
            "after": source[end:end + CONTEXT_BYTES].decode("utf-8", "replace"),
        })
    write_json("wg-e1-sample.json", {"seed": SEED, "population": len(ids), "sample": sample})
    print(f"drew {len(sample)} of {len(ids)}")


CATEGORIES = ("i", "ii", "iii", "iv")


def tally() -> None:
    data = json.loads((EVIDENCE / "wg-e1-classification.json").read_text(encoding="utf-8"))
    sample = json.loads((EVIDENCE / "wg-e1-sample.json").read_text(encoding="utf-8"))["sample"]
    rows = data["rows"]
    if [r["id"] for r in rows] != [s["id"] for s in sample]:
        raise SystemExit("the classification must name the drawn units, in draw order")
    for row in rows:
        if row["category"] not in CATEGORIES:
            raise SystemExit(f"{row['id']}: category {row['category']!r}")
        if row["category"] == "ii" and row.get("changes_checked_answer") not in ("yes", "no", "needs WG-0"):
            raise SystemExit(f"{row['id']}: a (ii) unit needs changes_checked_answer")
    counts = {c: sum(1 for r in rows if r["category"] == c) for c in CATEGORIES}
    exclusive = [r for r in rows if r["category"] == "ii"]
    changes = sum(1 for r in exclusive if r["changes_checked_answer"] == "yes")
    pending = sum(1 for r in exclusive if r["changes_checked_answer"] == "needs WG-0")
    clause_1 = counts["ii"] >= 8
    if not clause_1:
        verdict = "FAIL"
    elif changes >= 5:
        verdict = "PASS"
    elif changes + pending >= 5:
        verdict = "PASS pending WG-0"
    else:
        verdict = "FAIL"
    result = {"units": len(rows), "counts": counts, "exclusive_units": [r["id"] for r in exclusive],
              "exclusive_changing_a_checked_answer": changes, "exclusive_needing_WG-0": pending,
              "clause_1_ii_at_least_8": clause_1, "clause_2_at_least_5_change": changes >= 5,
              "verdict": verdict}
    write_json("wg-e1-result.json", result)
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    {"screen": screen, "draw": draw, "tally": tally}[sys.argv[1]]()
