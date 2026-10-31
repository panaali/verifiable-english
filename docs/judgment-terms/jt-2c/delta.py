"""jt-2c review F1's and F5's delta, base against head: what every composing mode answers to a `judgments@0` list
without `documents@1` (F1), and with `judgments@0` duplicated, first or last (F5).

    uv run python docs/judgment-terms/jt-2c/delta.py --answers OUT --service <checkout>/lean/.lake/build/bin/ve_service
    uv run python docs/judgment-terms/jt-2c/delta.py --compare BASE.json HEAD.json --out evidence/delta.json

`--answers` sends the same requests (built by this checkout's tests: the environment of
`tests/test_judgments_document.py` without `documents@1`, or out of order) to the given service, so the base's and the
head's records answer identical bytes, and records the environment mode's answer to each probe's environment beside it
(`authority`). `--compare` checks that every head record refuses with the head's environment mode's text, and each pair
that differs against standing ruling R1: both sides refuse; it keeps the base's code and every
profile name the base quoted (R1 (a)); neither side has a path (R1 (b)); and the head names the missing profile, which
the base did not (R1 (c)). Exit 1 when any pair fails, when nothing differs (head against head) or when there are no
records. The F5 probes answer as at the merge base (`delta.json`: unchanged).
"""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import re
import sys


def probes():
    """(name, mode, case) for every composing mode over the list without `documents@1`."""
    from tests.test_acts_profile import seek_environment
    from tests.test_judgments_compose import COMPOSING, UNORDERED, WITHOUT_DOCUMENTS, written as placed
    from tests.test_judgments_document import environment
    from ve import english
    from ve.backends import english_lean
    from ve.environment import Environment
    for mode, field, extra in COMPOSING:
        yield (f"{mode}/{field.get('kind', 'case')}", mode,
               {"id": "x", "environment": environment(profiles=sorted(WITHOUT_DOCUMENTS + extra)), **field})
    for shape, profiles in UNORDERED.items():  # review F5
        for mode, field, extra in COMPOSING:
            yield (f"{mode}/{field.get('kind', 'case')}/{shape}", mode,
                   {"id": "x", "environment": environment(profiles=placed(profiles, extra)), **field})
    written = ["acts@0", "documents@1", "judgments@0", "norm-defaults@0", "norms@0", "relational-fol@0"]
    others = [p for p in written if p != "judgments@0"]
    env = Environment(seek_environment(written))
    request = english_lean.request(env, "Alice may seek asylum.", english.EnglishVocabulary(env), {})
    for name, profiles in [("block", [p for p in written if p != "documents@1"]),
                           ("block/duplicate", sorted(written + ["judgments@0"])),
                           ("block/leading", ["judgments@0"] + others), ("block/trailing", others + ["judgments@0"])]:
        case = copy.deepcopy(request)
        case["environment"]["profiles"] = profiles
        yield f"english.read/{name}", "english.read", case


def record(out: Path, executable: Path) -> None:
    sys.path[:0] = [os.getcwd(), os.path.join(os.getcwd(), "tests")]  # this checkout's `ve` and `tests`
    from ve.backends.lean_service import LeanService
    records, authority = {}, {}
    with LeanService(executable, allow_unlisted_build=True) as service:
        build = service.build
        for name, mode, case in probes():
            records[name] = service.run(mode, [case])[0]
            authority[name] = service.run("environment", [{"id": "x", "environment": case["environment"]}])[0]
    out.write_text(json.dumps({"service": build, "records": records, "authority": authority}, indent=1,
                              sort_keys=True) + "\n")


def refuses_as_the_environment_mode(row: dict, authority: dict) -> list[str]:
    """Empty when `row` refuses with the text the environment mode refuses the same environment with."""
    if authority.get("status") != "error" or row.get("status") != "error" or row.get("error") != authority["error"]:
        return ["the head refuses with the environment mode's text"]
    return []


def r1(base: dict, head: dict) -> list[str]:
    """The R1 conditions a pair fails, empty when it keeps them all."""
    faults = []
    if base.get("status") != "error" or head.get("status") != "error":
        faults.append("both sides refuse")
    b, h = str(base.get("error", "")), str(head.get("error", ""))
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
    pairs = [{"probe": n, "base": base["records"][n], "head": head["records"].get(n, {}),
              "authority": head["authority"].get(n, {})} for n in names]
    for p in pairs:  # every head record is the environment mode's refusal; a changed one keeps R1 against the base
        p["faults"] = refuses_as_the_environment_mode(p["head"], p["authority"]) + (
            [] if p["base"] == p["head"] else r1(p["base"], p["head"]))
    changed = [p for p in pairs if p["base"] != p["head"]]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"base_service": base["service"], "head_service": head["service"], "ruling": "R1",
                               "pairs": pairs}, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    failed = [p["probe"] for p in pairs if p["faults"]]
    print(f"{len(pairs)} probes, {len(changed)} changed, {len(failed)} failing: {failed}")
    return 0 if pairs and changed and not failed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--answers", type=Path)
    parser.add_argument("--service", type=Path, default=Path("lean/.lake/build/bin/ve_service"))
    parser.add_argument("--compare", nargs=2, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.compare and not args.out:
        parser.error("--compare needs --out")
    if args.answers:
        record(args.answers, args.service.resolve())
        return 0
    return compare(*args.compare, args.out)


if __name__ == "__main__":
    sys.exit(main())
