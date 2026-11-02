"""Records Python's node for each of the 120 pinned rule blocks (en-e3-norm EN-0, spec english-lean-s6 OPEN-3).

`uv run python docs/english-lean/en-s6/capture_blocks.py` writes `tests/data/norm-blocks/rsp.jsonl` (76 blocks) and
`fsf.jsonl` (44 blocks): one line per block of `usecases/<case>/rules.d1.ve`, in file order, with the block's id and
text, the commit it was read at, and the `norm` object of `ve.norm_english.parse_english` on the case's environment
(each use case's own loader), or Python's refusal. It is run once; the files are captured data, never regenerated
by the gate.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CASES = (("rsp", "anthropic-rsp", "rsp_translation", 76), ("fsf", "safety-framework", "translation", 44))


def capture(case: str, module: str) -> list[dict]:
    sys.path.insert(0, str(ROOT / "usecases" / case))
    loader = __import__(module)
    from ve.norm_english import parse_english
    env = loader.environment()
    rows = []
    for block in loader.read_blocks("rules.d1.ve"):
        row = {"id": block.id, "text": block.text}
        try:
            row["node"] = [r.to_dict()["norm"] for r in parse_english(env, block.text).rules]
        except Exception as exc:  # the refusal is the recorded value
            row["error"] = f"{type(exc).__name__}: {exc}"
        rows.append(row)
    sys.path.pop(0)
    return rows


def main() -> None:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True,
                            text=True).stdout.strip()
    out = ROOT / "tests" / "data" / "norm-blocks"
    out.mkdir(parents=True, exist_ok=True)
    for name, case, module, count in CASES:
        rows = capture(case, module)
        if len(rows) != count:
            raise SystemExit(f"{case}: {len(rows)} blocks, expected {count}")
        lines = [json.dumps({"commit": commit, **row}, sort_keys=True) for row in rows]
        (out / f"{name}.jsonl").write_text("\n".join(lines) + "\n")
        print(f"wrote {name}.jsonl: {count} blocks, {sum('error' in r for r in rows)} refused")


if __name__ == "__main__":
    main()
