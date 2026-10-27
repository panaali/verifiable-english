"""ap-1bc's delta, base against head: the words route's lines of `acts@0` clauses (DELTA row 1), and a control.

    VE_LEAN_SERVICE=<the base's ve_service> uv run python docs/act-phrases/ap-1bc/delta.py --answers BASE.json
    uv run python docs/act-phrases/ap-1bc/delta.py --answers HEAD.json
    uv run python docs/act-phrases/ap-1bc/delta.py --compare BASE.json HEAD.json --out docs/act-phrases/ap-1bc/evidence/delta.json

ap-1bc changes no Python, so this checkout records both sides with its own client, each against its own pinned
service. `--answers` asks the words route each item of `tests/test_acts_profile.py`'s words tests alone (an `acts@0`
environment) and each item of `tests/test_words.py`'s genuine case (a `norm-defaults@0` environment without
`acts@0`: the control). `--compare` classifies each difference: `worded` (an `acts@0` item that was refused as not
regulated, or as no obligation with a declared permission, and now has a line). Exit 1 on any other difference, when
nothing differs (head against head) or when there are no records.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
REFUSED = ("is not regulated", "is no obligation with a declared permission")


def answers() -> dict:
    sys.path.insert(0, str(ROOT))
    from tests.test_acts_profile import DUAL, environment
    from tests.test_words import _case, _norm_env
    from ve import words
    from ve.environment import Environment
    acts = Environment(environment(**DUAL))
    items = {f"point/{p}/{v}": words.point_item({}, p, ids, v) for p, ids in
             [("heard", ["e0", "e1"]), ("paid", ["e0"]), ("protected", ["e0", "e1"]), ("long", ["e0"]),
              ("late", ["e0"])] for v in (True, False)}
    items.update({f"filling/{p}": words.point_item({}, p, ids, False, kind="filling")
                  for p, ids in [("heard", ["e0", "e1"]), ("paid", ["e0"]), ("protected", ["e0", "e1"])]})
    items.update({f"pair/{p}": words.pair_item(p) for p in ("must_hear", "heard", "protected")})
    control = _norm_env()
    asked = [("acts", acts, label, item) for label, item in items.items()]
    asked += [("control", control, f"item/{i}", item) for i, item in enumerate(_case(control)["items"])]
    found = {}
    for side, env, label, item in asked:
        try:
            found[f"{side}/{label}"] = {"line": words.lines(env, [item])[0]}
        except Exception as exc:  # the record is what a caller sees
            found[f"{side}/{label}"] = {"refused": f"{type(exc).__name__}: {exc}"}
    return found


def compare(base: dict, head: dict) -> tuple[dict, bool]:
    changed, ok = {}, bool(base) and set(base) == set(head)
    for key in sorted(set(base) | set(head)):
        b, h = base.get(key), head.get(key)
        if b == h:
            continue
        worded = (key.startswith("acts/") and b is not None and h is not None and "line" in h and
                  any(text in b.get("refused", "") for text in REFUSED))
        changed[key] = {"base": b, "head": h, "class": "worded" if worded else "other"}
        ok = ok and worded
    return {"records": len(head), "identical": len(head) - len(changed), "changed": changed}, ok and bool(changed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--answers")
    parser.add_argument("--compare", nargs=2)
    parser.add_argument("--out")
    args = parser.parse_args()
    if args.answers:
        Path(args.answers).write_text(json.dumps(answers(), indent=1, ensure_ascii=False) + "\n")
        return 0
    base, head = (json.loads(Path(p).read_text()) for p in args.compare)
    result, ok = compare(base, head)
    text = json.dumps(result, indent=1, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text)
    print(f"{result['records']} records, {result['identical']} identical, {len(result['changed'])} changed:",
          "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
