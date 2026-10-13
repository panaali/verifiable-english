"""ME-0, P3: units of the pinned constitution and UDHR pilots blocked by this topic (read-only).

Pre-registered: a unit matches when its `missing_feature` or an `other_blockers` entry contains, as a
case-insensitive substring, one of the plan's ME-0 feature tags or research 2.2's words. Also reported (not part of
the bar): UDHR's `residual_missing_features`, which the pre-registration did not name.

    python3 -I research/math-evidence/pilots_zero.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

PILOTS = Path("/home/seyran/code/manage-agents/pilots")
RUNS = {"constitution": PILOTS / "claude-constitution/run-20261012T1800Z/units.json",
        "udhr": PILOTS / "udhr/run-20261012T1800Z/units.json"}
TAGS = ["calc", "calc-data", "calc-derive", "calc-dimension", "calc-stats", "calc-algebra", "arith", "arith-import",
        "approximation", "evidence", "statistic", "mathematic", "calculat", "equation", "empiric", "science",
        "probabilit", "number", "arithmetic"]
OUT = Path(__file__).resolve().parents[2] / "docs/research/evidence/math-evidence/pilots-zero.json"


def tags_of(unit: dict, fields: tuple[str, ...]) -> list[str]:
    out = []
    for f in fields:
        v = unit.get(f)
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, list):
            out.extend(x if isinstance(x, str) else json.dumps(x) for x in v)
    return out


def span_bytes(unit: dict) -> int:
    s = unit.get("span")
    return s[1] - s[0] if isinstance(s, list) and len(s) == 2 else 0


def main() -> None:
    result = {"tags": TAGS, "pilots": {}}
    for name, path in RUNS.items():
        data = path.read_bytes()
        units = json.loads(data)
        units = units["units"] if isinstance(units, dict) else units
        flat = []
        for u in units:
            flat.extend(u.get("parts") or [u])
        hits, extra = [], []
        for u in flat:
            barred = [t for t in tags_of(u, ("missing_feature", "other_blockers"))
                      if any(k in t.lower() for k in TAGS)]
            if barred:
                hits.append({"id": u.get("id"), "bytes": span_bytes(u), "tags": barred})
            residual = [t for t in tags_of(u, ("residual_missing_features",)) if any(k in t.lower() for k in TAGS)]
            if residual:
                extra.append({"id": u.get("id"), "bytes": span_bytes(u), "tags": residual})
        result["pilots"][name] = {"units_json": str(path), "units_json_sha256": hashlib.sha256(data).hexdigest(),
                                  "units": len(units), "flattened_units": len(flat),
                                  "matching_units": len(hits), "matching_bytes": sum(h["bytes"] for h in hits),
                                  "matches": hits, "residual_missing_features_matches": extra}
    result["pass"] = all(p["matching_units"] == 0 for p in result["pilots"].values())
    OUT.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("matches",)}
                      for k, v in result["pilots"].items()}, indent=1), "\npass:", result["pass"])


if __name__ == "__main__":
    main()
