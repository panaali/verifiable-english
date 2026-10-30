"""jt-2c review F1's delta, base against head: what every composing mode answers to a `judgments@0` list without
`documents@1`.

    uv run python docs/judgment-terms/jt-2c/delta.py --answers OUT --service <checkout>/lean/.lake/build/bin/ve_service
    uv run python docs/judgment-terms/jt-2c/delta.py --compare BASE.json HEAD.json --out evidence/delta.json

`--answers` sends the same requests (built by this checkout's tests: the environment of
`tests/test_judgments_document.py` without `documents@1`) to the given service, so the base's and the head's records
answer identical bytes. `--compare` checks each pair that differs against standing ruling R1: both sides refuse; the head's text is
the environment mode's `UnsupportedProfile: judgments@0 requires documents@1`; it keeps the base's code and every
profile name the base quoted (R1 (a)); neither side has a path (R1 (b)); and the head names the missing profile, which
the base did not (R1 (c)). Exit 1 when any pair fails, when nothing differs (head against head) or when there are no
records.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import re
import sys

REQUIRES = "UnsupportedProfile: judgments@0 requires documents@1"


def probes():
    """(name, mode, case) for every composing mode over the list without `documents@1`."""
    from tests.test_acts_profile import seek_environment
    from tests.test_judgments_compose import COMPOSING, WITHOUT_DOCUMENTS
    from tests.test_judgments_document import environment
    from ve import english
    from ve.backends import english_lean
    from ve.environment import Environment
    for mode, field, extra in COMPOSING:
        yield (f"{mode}/{field.get('kind', 'case')}", mode,
               {"id": "x", "environment": environment(profiles=sorted(WITHOUT_DOCUMENTS + extra)), **field})
    written = ["acts@0", "documents@1", "judgments@0", "norm-defaults@0", "norms@0", "relational-fol@0"]
    env = Environment(seek_environment(written))
    case = copy.deepcopy(english_lean.request(env, "Alice may seek asylum.", english.EnglishVocabulary(env), {}))
    case["environment"]["profiles"] = [p for p in written if p != "documents@1"]
    yield "english.read/block", "english.read", case


def record(out: Path, executable: Path) -> None:
    sys.path[:0] = [os.getcwd(), os.path.join(os.getcwd(), "tests")]  # this checkout's `ve` and `tests`
    from ve.backends.lean_service import LeanService
    records = {}
    with LeanService(executable, allow_unlisted_build=True) as service:
        build = service.build
        for name, mode, case in probes():
            records[name] = service.run(mode, [case])[0]
    out.write_text(json.dumps({"service": build, "records": records}, indent=1, sort_keys=True) + "\n")


def r1(base: dict, head: dict) -> list[str]:
    """The R1 conditions a pair fails, empty when it keeps them all."""
    faults = []
    if base.get("status") != "error" or head.get("status") != "error":
        faults.append("both sides refuse")
    b, h = str(base.get("error", "")), str(head.get("error", ""))
    if h != REQUIRES:
        faults.append("the head's text is the environment mode's")
    if b.split(":", 1)[0] != h.split(":", 1)[0]:
        faults.append("the base's code is kept")
    if any(q not in h for q in re.findall(r"[a-z][a-z.-]*@\d+", b)):
        faults.append("R1 (a): every profile the base quoted is quoted")
    if any("path" in row for row in (base, head)):
        faults.append("R1 (b): no path on either side")
    if "documents@1" in b or "documents@1" not in h:
        faults.append("R1 (c): the head names the missing profile")
    return faults


def compare(base_path: Path, head_path: Path, out: Path) -> int:
    base, head = (json.loads(p.read_text()) for p in (base_path, head_path))
    names = sorted(base["records"])
    pairs = [{"probe": n, "base": base["records"][n], "head": head["records"].get(n, {})} for n in names]
    for p in pairs:  # an unchanged record is no delta; a changed one keeps R1
        p["faults"] = [] if p["base"] == p["head"] else r1(p["base"], p["head"])
    changed = [p for p in pairs if p["base"] != p["head"]]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"base_service": base["service"], "head_service": head["service"], "ruling": "R1",
                               "pairs": pairs}, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    failed = [p["probe"] for p in pairs if p["faults"]]
    print(f"{len(pairs)} probes, {len(changed)} changed, {len(failed)} failing R1: {failed}")
    return 0 if pairs and changed and not failed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--answers", type=Path)
    parser.add_argument("--service", type=Path, default=Path("lean/.lake/build/bin/ve_service"))
    parser.add_argument("--compare", nargs=2, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.answers:
        record(args.answers, args.service.resolve())
        return 0
    return compare(*args.compare, args.out)


if __name__ == "__main__":
    sys.exit(main())
