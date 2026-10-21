"""ap-1b's user-visible delta on `acts@0` inputs, base against head (DELTA.md rows 2 to 4), saved as evidence.

    uv run python docs/act-phrases/ap-1b/delta.py --base ../base --out docs/act-phrases/ap-1b/evidence/delta.json

Every input lists `acts@0`, and the merge base refuses each one (by the profile, or by the first check of the
decoder that ran before any profile check). Each goes through the base's `ve_service` and this checkout's in the mode
a client sends it to. A head answer that is a profile refusal must quote `acts@0` and every profile the base's text
quoted (R1 (a)); exit 1 otherwise, or when the base answered an input (it would not be new).
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
import sys

HEAD = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HEAD))
from tests.test_acts_profile import A5, ENV, predicate  # noqa: E402
from ve.backends.lean_service import LeanService  # noqa: E402
from ve.errors import VEError  # noqa: E402

SERVICE = "lean/.lake/build/bin/ve_service"


def env(profiles=None, **predicates):
    data = copy.deepcopy(ENV)
    data["profiles"] = profiles or data["profiles"]
    data["vocabulary"]["predicates"].update(predicates)
    return data


RULE = {"norm": {"name": "m", "predicate": "heard", "sign": True, "guard": ["top"], "unless": [], "over": []}}
LISTS = {"soft-norms": ["acts@0", "norms@0", "relational-fol@0", "soft-norms@0"],
         "alternatives": ["acts@0", "alternatives@0", "norms@0", "relational-fol@0"],
         "speech-acts": ["acts@0", "norms@0", "relational-fol@0", "speech-acts@0"],
         "closure": ["acts@0", "closure@0", "norms@0", "relational-fol@0"],
         "order": ["acts@0", "norms@0", "order@0", "relational-fol@0"],
         "no-norms": ["acts@0", "relational-fol@0"]}
CASES = ([(f"environment/{k}", "environment", {"id": k, "environment": env(ps)}) for k, ps in LISTS.items()] +
         [(f"family-norms/{k}", "family-norms", {"id": k, "kind": "norms-elaborate", "environment": env(LISTS[k]),
                                                 "norms": [RULE]}) for k in ("closure", "order")] +
         [(f"norms-background/{k}", "norms", {"id": k, "kind": "background", "environment": env(LISTS[k])})
          for k in ("closure", "order")] +
         [("environment/A1-A3", "environment", {"id": "a", "environment": env()}),
          ("norms/A1-A3", "norms", {"id": "e", "kind": "norms-elaborate", "environment": env(), "norms": [RULE]}),
          ("norms-background/A1-A3", "norms", {"id": "b", "kind": "background", "environment": env()}),
          ("environment/A5", "environment", {"id": "a5", "environment": env(
              p=predicate(["person"], {"role": "plain", "default": "deny", "act": A5, "form": "has the right"}))})])


def answers(root: Path) -> list[str]:
    service = LeanService(root / SERVICE, allow_unlisted_build=True)
    try:
        out = []
        for _, mode, case in CASES:
            try:
                [row] = service.run(mode, [case])
                out.append(row.get("error") if row.get("status") == "error" else "answered")
            except VEError as refused:
                out.append(refused.message)
        return out
    finally:
        service.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    base, head = answers(args.base.resolve()), answers(HEAD)
    records = []
    for (label, mode, _), b, h in zip(CASES, base, head):
        refusal = h.startswith("UnsupportedProfile:")
        quoted = set(re.findall(r"[a-z.-]+@\d", b)) | {"acts@0"}
        records.append({"input": label, "mode": mode, "base": b, "head": h, "base_refused": b != "answered",
                        "profile_refusal": refusal, "keeps_names": (not refusal) or all(q in h for q in quoted)})
    ok = all(r["base_refused"] and r["keeps_names"] for r in records)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"records": records, "ok": ok}, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(records)} records, ok={ok}")
    raise SystemExit(0 if ok and records else 1)


if __name__ == "__main__":
    main()
