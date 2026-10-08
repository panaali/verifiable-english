"""Save the 16b differential-fuzzer evidence from base and head reports (`tools/difffuzz.py --report`).

    python docs/lean-first/b16b/fuzz_seeds.py DIR --base COMMIT --head COMMIT

DIR holds `head-ci.json` and, for every date seed, `base-<seed>.json` and `head-<seed>.json` (`--deep 1 --seed
<seed>`). Writes `evidence/difffuzz.json`: the CI run's new signatures and baseline replay, and for each date seed
the new-signature counts on both sides, the signatures only one side has, and each side's signature-set digest.
The baseline does not grow when the CI run has no new signature and no seed has a head-only signature.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def signatures(report: dict) -> list[str]:
    return sorted(entry["signature"] for entry in report["new"])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    args = parser.parse_args(argv)
    ci = json.loads((args.directory / "head-ci.json").read_text())
    rows = []
    for path in sorted(args.directory.glob("head-2*.json")):
        seed = path.stem.removeprefix("head-")
        head = json.loads(path.read_text())
        base = json.loads((args.directory / f"base-{seed}.json").read_text())
        h, b = signatures(head), signatures(base)
        rows.append({"seed": seed, "head_new": len(h), "base_new": len(b),
                     "head_only": len(set(h) - set(b)), "base_only": len(set(b) - set(h)),
                     "head_signature_sha256": hashlib.sha256(json.dumps(h).encode()).hexdigest(),
                     "base_signature_sha256": hashlib.sha256(json.dumps(b).encode()).hexdigest(),
                     "head_passed": head["passed"], "base_passed": base["passed"],
                     "head_document_inputs": head["mutants"].get("document"),
                     "base_document_inputs": base["mutants"].get("document")})
    out = {"base": args.base, "head": args.head,
           "ci": {"seed": ci["seed"], "passed": ci["passed"], "new": len(ci["new"]),
                  "baseline_entries": ci["baseline"]["entries"], "unreviewed": len(ci["baseline"]["unreviewed"]),
                  "not_reproduced": len(ci["baseline"]["not_reproduced"]),
                  "document_inputs": ci["mutants"].get("document")},
           "seeds": rows}
    (HERE / "evidence/difffuzz.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"ci_new": out["ci"]["new"], "seeds": len(rows),
                      "head_only": sum(r["head_only"] for r in rows)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
