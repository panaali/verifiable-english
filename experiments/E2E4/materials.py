"""Offline E2/E4 materials; dispatchers preserve the shared harness contract."""
from copy import deepcopy
from pathlib import Path
import gzip
import json
from . import e2, e4
from .common import replay

ROOT = Path(__file__).resolve().parent
SIZES, FAMILIES = e2.SIZES, tuple(e2.VOCABS)
E2_CELLS, E4_CELLS = e2.CELLS, e4.CELLS
construction_support, validate_e2 = e2.construction_support, e2.validate


def build_items(split, experiment=None):
    if split not in {"dev", "scored", "all"}:
        raise ValueError("split must be dev, scored, or all")
    if experiment not in {None, "E2", "E4"}:
        raise ValueError("experiment must be E2, E4, or None")
    rows = (e2.items() if experiment in {None, "E2"} else []) + (e4.items() if experiment in {None, "E4"} else [])
    return deepcopy(rows if split == "all" else [r for r in rows if r["split"] == split])


def render_cell(item, cell):
    p = item.payload if hasattr(item, "payload") else item.get("payload", item)
    return (e2.render if p["experiment"] == "E2" else e4.render)(p, cell)


def as_harness(split, experiment):
    from ve_experiments.runner import Condition, Item
    cells = E2_CELLS if experiment == "E2" else E4_CELLS
    return [Item(**r) for r in build_items(split, experiment)], [Condition(c, lambda p, c=c: render_cell(p, c)) for c in cells]


def load_frozen(split, experiment):
    """Hydrate shared proof artifacts without regeneration or model calls."""
    if split not in {"dev", "scored"} or experiment not in {"E2", "E4"}:
        raise ValueError((split, experiment))
    with gzip.open(ROOT / f"{experiment.lower()}-{split}.jsonl.gz", "rt") as f:
        rows = [json.loads(line) for line in f]
    if experiment == "E2":
        templates = {}
        for row in rows:
            p = row["payload"]
            if "checks" in p:  # legacy full export
                continue
            template = p["template"]
            if template not in templates:
                with gzip.open(ROOT / "certificates" / f"{template}.jsonl.gz", "rt") as f:
                    templates[template] = {entry["ref"]: entry["check"] for line in f if (entry := json.loads(line))}
            p["checks"] = {ref: templates[template][ref] for ref in p.pop("check_refs")}
    return rows
