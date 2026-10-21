"""Append the `acts@0` environments to the model oracle `tests/data/b15b-model-oracle.json.gz` (ap-1b).

The oracle holds, for every profile an environment lists, fixture environments and the answers of the public
model operations (`tests/b15b_model_cases.py`), recorded at batch 15b's base. `acts@0` has no base, so its
environment (`tests/test_acts_profile.py` `ENV`, and its display variant) is recorded here at the head: both
engines refuse it (`UnsupportedProfile: Unsupported profile acts@0`) until Lean's model path reads the profile.
Running it again changes nothing.

    uv run python -I docs/act-phrases/ap-1b/oracle_acts.py
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
ORACLE = ROOT / "tests/data/b15b-model-oracle.json.gz"


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from tests import b15b_model_cases as cases
    from tests.test_acts_profile import ENV
    data = json.loads(gzip.decompress(ORACLE.read_bytes()))
    name = "ve.core@0.2:acts@0,norms@0,relational-fol@0#1"
    envs = [(name, ENV), (name + "+display", cases.displayed(ENV))]
    data["environments"] = [e for e in data["environments"] if e[0].split("#")[0] != name.split("#")[0]]
    data["environments"] += [list(e) for e in envs]
    data["answers"] = {k: v for k, v in data["answers"].items() if k.split("#")[0] != name.split("#")[0]}
    data["answers"].update(cases.run_all(envs))
    with gzip.open(ORACLE, "wt") as stream:
        json.dump(data, stream, sort_keys=True, indent=0)
    print(len(data["environments"]), len(data["answers"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
