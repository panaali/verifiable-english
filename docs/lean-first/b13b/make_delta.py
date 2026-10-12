"""Build `DELTA.json`, the batch's list for `tools/lean_first_diff.py compare --delta`, from a comparison run
without it: every wording text pair (with `lean_first_diff.text_pairs`, so each is matched as the tool matches
it) and every order record with both outcomes. Verdict and availability differences are refused: the 13b A/B
has none, and each would need a DRI signature of its own.

    python docs/lean-first/b13b/make_delta.py COMPARE_JSON
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from tools.lean_first_diff import text_pairs  # noqa: E402


def main(path: str) -> int:
    differences = json.loads(Path(path).read_text())["differences"]
    wording, order = {}, []
    for row in differences:
        if row["class"] == "wording":
            for base, head in text_pairs(row["base"], row["head"]):
                wording[json.dumps([base, head], sort_keys=True)] = {"base": base, "head": head}
        elif row["class"] == "order":
            order.append({key: row[key] for key in ("corpus", "authority", "case", "op", "base", "head")})
        else:
            raise SystemExit(f"{row['class']} difference needs a DRI signature: {row['corpus']} {row['case']}")
    delta = {"wording": [wording[key] for key in sorted(wording)],
             "order": sorted(order, key=lambda r: (r["corpus"], r["authority"], r["case"], r["op"]))}
    (HERE / "DELTA.json").write_text(json.dumps(delta, indent=1, ensure_ascii=False) + "\n")
    print(len(delta["wording"]), "wording pairs,", len(delta["order"]), "order records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
