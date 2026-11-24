"""The frozen bridge (../bridge/bridges.py, unchanged) on the cross-family encoder's records: the same main() loop, with the
case source xfam/cases_xfam.py instead of ../cases.py. usage (repository root):
    python3 -I usecases/hicbc/xfam/bridges_xfam.py usecases/hicbc/xfam/questions-enc.jsonl > usecases/hicbc/xfam/bridge/bridges.jsonl
"""
import importlib.util
import json
import sys
from pathlib import Path

X = Path(__file__).resolve().parent
sys.path.insert(0, str(X.parent / "bridge"))
import bridges as BR  # noqa: E402


def main(argv):
    spec = importlib.util.spec_from_file_location("cases_xfam", X / "cases_xfam.py")
    K = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(K)
    facts = {json.loads(l)["id"]: json.loads(l)["facts"] for l in open(argv[0], encoding="utf-8") if l.strip()}
    bad = 0
    for case in K.CASES:
        miss = BR.check_quotes(case, facts[case["id"]])
        if miss:
            bad += 1
            print(f"{case['id']}: dates not in the facts: {miss}", file=sys.stderr)
        b = BR.case_bridge(case)
        b["charge_table"] = BR.charge_table(b, case["subject"]) if case["subject"] in case["ani"] else []
        print(json.dumps(b, sort_keys=True))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
