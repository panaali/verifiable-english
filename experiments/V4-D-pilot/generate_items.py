"""New deterministic C instances; no model-mediated item selection."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "V4-calibration"))
import generate as cg

SEED = 2026092250
FAMILIES = ("cases", "xor", "modus_tollens", "near_miss", "nested_quantifiers", "belief_inconsistent")


def english_key(item):
    return json.dumps([sorted(p["english"] for p in item["premises"]), item["query"]["english"]])


def main():
    if (HERE / "items.jsonl").exists():
        raise ValueError("Items already frozen; do not overwrite")
    cg.SEEDS["d_pilot"] = SEED
    old = {english_key(json.loads(line)) for split in ("smoke", "dev", "heldout")
           for line in (cg.HERE / f"{split}.jsonl").read_text().splitlines()}
    rows = []
    for family in FAMILIES:
        for position, index in enumerate((300, 301, 303, 304)):
            item = cg.generate_item("d_pilot", family, index)
            assert item["label"] == ("True" if position % 2 == 0 else "False")
            assert english_key(item) not in old, "Duplicate English C instance"
            old.add(english_key(item))
            item["honest"] = position in (0, 3)
            item["assigned"] = item["label"] if item["honest"] else ("False" if item["label"] == "True" else "True")
            item["display_first"] = "True" if position in (0, 1) else "False"
            rows.append(item)
    random.Random(SEED).shuffle(rows)
    for i, item in enumerate(rows):
        item["id"] = f"d-{i:02d}"
    path = HERE / "items.jsonl"
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    manifest = {"seed": SEED, "items": len(rows), "labels": dict(Counter(r["label"] for r in rows)),
                "honest": sum(r["honest"] for r in rows), "families": dict(Counter(r["type"] for r in rows)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "gold_validation": "Satisfying finite-model evaluation plus replayed VE entailment certificate",
                "freshness": "New C seed; no exact premise-set/query duplicate in smoke/dev/heldout or this pilot"}
    (HERE / "items-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest), flush=True)


if __name__ == "__main__":
    main()
