"""The whole declaration as ONE document, with the reading sets that carry their own vocabulary as components (readings-defaults RD-4a/4b).

rd-4b (merged since the last run) lets a reading carry `companion: {environment, open_terms}`: a set all of whose readings do is a component,
checked by itself, and the document's meaning is the product of its components. The 11 two-reading sets of the declaration no longer
multiply (2,048 choices): the six whose readings are all norms with their own vocabulary (u025, u049, u055, u073, u077, u111) are components of
at most two choices each; the other five (u052, u110, u114 mix a formula and a norm, or are formulas; u105b and u105c are coupled, and a
coupling may not link two components) stay in the main component (16 choices).

    uv run --frozen python usecases/udhr-pilot/run-20261012T1800Z/whole.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import integrate as I  # noqa: E402
import readings_s1_pilot as P  # noqa: E402
from ve.document import load_document  # noqa: E402

PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
COMPONENT_SETS = ["u025", "u055", "u073", "u111"]      # 2026-10-14T1800Z: u049 and u077 are single readings now (audit repair)
OUT = HERE / "experiment-whole" / "translation-whole.ve.md"


def companion_doc(uid, cid):
    raw = (HERE / "readings" / f"{uid}.{cid}.ve.md").read_bytes()
    _, front, _ = raw.split(b"---\n", 2)
    meta = json.loads(front)
    return meta


def merged_environment(metas):
    """The companions' environments united by name (a repeated name only if identical), `readings@1` added (spec 1.9)."""
    out = deepcopy(metas[0]["environment"])
    for meta in metas[1:]:
        voc = meta["environment"]["vocabulary"]
        for field in ("sorts", "predicates", "constants"):
            for name, decl in voc[field].items():
                assert out["vocabulary"][field].setdefault(name, decl) == decl, (field, name)
    out["profiles"] = sorted(set(out["profiles"]) | {"readings@1"})
    return out


def merged_open_terms(metas):
    out = {}
    for meta in metas:
        for term in meta["open_terms"]:
            assert out.setdefault(term["name"], term) == term, term["name"]
    return [out[n] for n in sorted(out)]


def main():
    raw = (HERE.parent / "source" / "udhr.md").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    legacy, _ = P.read(HERE / "translation.ve.md")
    comp_sets = {s["unit"]: s for s in legacy["reading_sets"] if s["unit"] in COMPONENT_SETS}
    base = deepcopy(legacy)
    base["reading_sets"] = [s for s in base["reading_sets"] if s["unit"] not in COMPONENT_SETS]
    part, src, a, b = I.build_part(base, raw, "u001", "u114", "whole")
    regulated = sum(1 for d in part["environment"]["vocabulary"]["predicates"].values() if "regulated" in d)
    print("main: regulated predicates", regulated, "sorts", len(part["environment"]["vocabulary"]["sorts"]), flush=True)
    part = I.finish_sets(part, src, "whole")
    part, row, missing, limits = I.find(part, "whole-main")
    print("main missing", missing, "limits", limits, flush=True)

    sets = {s["unit"]: s for s in part["reading_sets"]}
    for uid in COMPONENT_SETS:
        s = comp_sets[uid]
        metas = {r["id"]: companion_doc(uid, r["id"]) for r in s["readings"]}
        env = merged_environment(list(metas.values()))
        terms = merged_open_terms(list(metas.values()))
        content_of = {cid: m["units"][0]["content"] for cid, m in metas.items()}
        unit = next(u for u in legacy["units"] if u["id"] == uid)
        mini = {"environment": env, "open_terms": terms, "format": "ve-document@1",
                "units": [{"id": uid, "kind": "norm", "meaning": unit["meaning"], "span": [0, 1], "support": "none"}],
                "_sets": [{**deepcopy(s), "_content": content_of, "models": {}}]}
        mini = I.finish_sets(mini, b"x", uid)
        mini, row, miss, lim = I.find(mini, uid)
        print(uid, "component:", row["status"], "missing", miss, "limits", lim, flush=True)
        [item] = mini["reading_sets"]
        for r in item["readings"]:
            r["meaning_id"] = metas[r["id"]]["units"][0].get("meaning_id") or load_document(HERE / "readings" / f"{uid}.{r['id']}.ve.md")["units"][0]["meaning_id"]
            r["companion"] = {"environment": metas[r["id"]]["environment"], "open_terms": metas[r["id"]]["open_terms"]}
        sets[uid] = item
    part["reading_sets"] = [sets[u["id"]] for u in part["units"] if u["id"] in sets]
    P.write(OUT, part, src)
    print("wrote", OUT.name)


if __name__ == "__main__":
    main()
