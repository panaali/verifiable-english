"""Compare the n-ary shape absent from the large corpus on base and head.

Usage: uv run python docs/lean-first/b14c/targeted_ab.py BASE_ROOT HEAD_ROOT OUT
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys

from tests.test_b14c import case


CHECK = """import json,sys
from ve import Environment,FiniteModel
from ve.errors import VEError
env,model=json.load(sys.stdin)
try:
    e=Environment(env)
    m=FiniteModel.from_dict(e,model)
    answer={'status':'ok','environment_id':e.environment_id,
            'model_id':m.model_id,'defined_rows':sorted(m.relations['derived'])}
except VEError as error:
    answer={'status':'error','code':type(error).__name__,'text':str(error),
            'path':getattr(error,'path','')}
print(json.dumps(answer,sort_keys=True))
"""


def run(root: Path, pair: tuple) -> dict:
    env = {**os.environ, "PYTHONPATH": str(root)}
    result = subprocess.run([sys.executable, "-c", CHECK], cwd=root,
                            input=json.dumps(pair), text=True, capture_output=True,
                            env=env, timeout=30, check=True)
    return json.loads(result.stdout)


def preserves_r1(old: dict, new: dict) -> bool:
    quotes = lambda text: set(re.findall(r"['\"]([^'\"]+)['\"]", text))
    return (old["code"] == new["code"] and old["path"] == new["path"] and
            quotes(old["text"]) <= quotes(new["text"]) and
            all(phrase in new["text"] for phrase in ("supplied table", "defined predicate")))


def main() -> int:
    base, head, out = map(Path, sys.argv[1:])
    valid = case()
    supplied = case()
    supplied[1]["relations"]["derived"] = []
    cases = {"valid": valid, "supplied_table": supplied}
    rows = {name: {"base": run(base, pair), "head": run(head, pair)}
            for name, pair in cases.items()}
    old, new = rows["supplied_table"]["base"], rows["supplied_table"]["head"]
    r1 = preserves_r1(old, new)
    passed = rows["valid"]["base"] == rows["valid"]["head"] and r1
    out.write_text(json.dumps({"pass": passed, "cases": rows, "supplied_table_r1": r1},
                              indent=2, sort_keys=True) + "\n")
    saved = json.loads(out.read_text())
    assert saved["supplied_table_r1"] == preserves_r1(
        saved["cases"]["supplied_table"]["base"], saved["cases"]["supplied_table"]["head"])
    print(f"valid answer identical; supplied-table wording R1 check: {r1}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
