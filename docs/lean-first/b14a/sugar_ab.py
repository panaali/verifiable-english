"""The batch's own corpus: every `definitions@0` sugar fixture of `tests/test_lean_first_b14a.py` (accepted,
rejected, n-ary, perturbed and two-fault sources over every family it names), through the public
`ve.parser.parse` and `canonicalize` at the base and at the head (plan 5.1 item 2, "the batch profile's own
corpora").

    cd ROOT && uv run python HEAD/docs/lean-first/b14a/sugar_ab.py record OUT      # in each checkout
    uv run python docs/lean-first/b14a/sugar_ab.py compare BASE HEAD --json OUT     # here

The fixtures are read from this file's checkout (the head), `ve` from the working directory's checkout, so
both sides see the same sources. `compare` classes each pair: `same`, or `wording` when only the message
differs and standing ruling R1's conditions hold (DRI-RULINGS.md: the same code, the same span, and the
head message is the base message or Lean's `Code: ` prefix followed by it, so every quoted name is kept);
anything else is `unlisted` and fails the comparison.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HEAD = Path(__file__).resolve().parents[3]


def fixtures():
    spec = importlib.util.spec_from_file_location("b14a_fixtures", HEAD / "tests/test_lean_first_b14a.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cases(module):
    from tests import probe_matrix as pm
    from ve.environment import Environment
    out = []
    plain = Environment(pm.raw_environment(("definitions@0",)))
    for family in module.FAMILIES:
        env = Environment(pm.raw_environment(family))
        for source in module.ACCEPTED + module.REJECTED:
            out.append(("/".join(family), env, source))
    for source in module.NARY:
        out.append(("nary", module.nary_environment(), source))
    for name, change in sorted(module.PERTURBATIONS.items()):
        for source in module.ACCEPTED:
            if change(source) != source:
                out.append((f"perturbed:{name}", plain, change(source)))
    lines = [s for s in module.REJECTED if s.endswith(".\n") and s.count("\n") == 1]
    for index, first in enumerate(lines):
        second = lines[(index * 7 + 3) % len(lines)]
        out.append(("two-fault", plain, first + second))
        out.append(("two-fault", plain, module.ACCEPTED[index % len(module.ACCEPTED)] + first + second))
    bare = Environment(pm.raw_environment(()))
    for source in module.ACCEPTED:
        out.append(("no-profile", bare, source))
    return out


def outcome(call):
    from ve.errors import VEError
    try:
        return {"returned": call()}
    except VEError as exc:
        return {"raised": exc.to_dict()}


def record(out: Path) -> None:
    sys.path.insert(0, str(Path.cwd()))
    os.environ.pop("VE_AUTHORITY", None)
    from ve.ast import formula_to_data
    from ve.parser import canonicalize, parse
    rows = []
    for group, env, source in cases(fixtures()):
        key = hashlib.sha256(json.dumps([group, env.environment_id, source]).encode()).hexdigest()
        rows.append({"group": group, "source": source, "key": key,
                     "parse": outcome(lambda: [formula_to_data(env, f) for f in parse(env, source).formulas]),
                     "canonical": outcome(lambda: canonicalize(env, source))})
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=0) + "\n")
    print(f"recorded {len(rows)} sources")


def classify(base: dict, head: dict) -> str:
    if base == head:
        return "same"
    if "raised" in base and "raised" in head:
        b, h = base["raised"], head["raised"]
        if (b["code"] == h["code"] and b.get("span") == h.get("span")
                and h["message"] in (b["message"], f"{b['code']}: {b['message']}")):
            return "wording"
    return "unlisted"


def compare(base_path: Path, head_path: Path, out: Path | None) -> int:
    base, head = json.loads(base_path.read_text()), json.loads(head_path.read_text())
    assert [r["key"] for r in base] == [r["key"] for r in head], "the two sides saw different sources"
    totals, pairs, unlisted = {}, {}, []
    for b, h in zip(base, head):
        for op in ("parse", "canonical"):
            kind = classify(b[op], h[op])
            totals[kind] = totals.get(kind, 0) + 1
            if kind == "wording":
                pairs[b[op]["raised"]["message"]] = h[op]["raised"]["message"]
            if kind == "unlisted":
                unlisted.append({"group": b["group"], "source": b["source"], "op": op, "base": b[op], "head": h[op]})
    result = {"records": len(base) * 2, "totals": totals, "wording_pairs": pairs, "unlisted": unlisted}
    if out:
        out.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({"records": result["records"], "totals": totals, "pairs": len(pairs),
                      "unlisted": len(unlisted)}))
    return 1 if unlisted else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("record")
    r.add_argument("out", type=Path)
    c = sub.add_parser("compare")
    c.add_argument("base", type=Path)
    c.add_argument("head", type=Path)
    c.add_argument("--json", type=Path)
    args = parser.parse_args()
    if args.command == "record":
        record(args.out)
        return 0
    return compare(args.base, args.head, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
