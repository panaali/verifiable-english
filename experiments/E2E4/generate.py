"""Regenerate complete compressed materials, local JSONL and frozen counts."""
from collections import Counter
from copy import deepcopy
import argparse
import gzip
import json
from pathlib import Path
from .materials import build_items

ROOT = Path(__file__).resolve().parent


def main(pack_existing=False):
    groups, summary = {}, {}
    for experiment in ("E2", "E4"):
        rows = ([json.loads(line) for split in ("dev", "scored") for line in (ROOT / f"{experiment.lower()}-{split}.jsonl").read_text().splitlines()]
                if pack_existing else build_items("all", experiment))
        for row in rows:
            groups[row["group"]] = row["split"]
        for split in ("dev", "scored"):
            selected = [r for r in rows if r["split"] == split]
            raw = "".join(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n" for r in selected).encode()
            path = ROOT / f"{experiment.lower()}-{split}.jsonl"
            path.write_bytes(raw)
            if experiment == "E2":
                slim = []
                for row in selected:
                    copy = {**row, "payload": {k: v for k, v in row["payload"].items() if k != "checks"}}
                    copy["payload"]["check_refs"] = sorted(row["payload"]["checks"])
                    slim.append(copy)
                frozen = "".join(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n" for r in slim).encode()
            else:
                frozen = raw
            path.with_suffix(".jsonl.gz").write_bytes(gzip.compress(frozen, mtime=0))
        if experiment == "E2":
            directory = ROOT / "certificates"
            directory.mkdir(exist_ok=True)
            templates = sorted({r["payload"]["template"] for r in rows})
            for template in templates:
                checks = {ref: check for row in rows if row["payload"]["template"] == template for ref, check in row["payload"]["checks"].items()}
                raw = "".join(json.dumps({"ref": ref, "check": check}, sort_keys=True, separators=(",", ":")) + "\n" for ref, check in sorted(checks.items())).encode()
                (directory / f"{template}.jsonl.gz").write_bytes(gzip.compress(raw, mtime=0))
        summary[experiment] = {"items": len(rows), "counts": [dict(zip(("split", "template", "vocabulary", "label", "size", "workload", "error", "n"), (*k, n)))
            for k, n in sorted(Counter((r["split"], r["payload"]["template"], r["payload"]["family"], r["label"],
                r["payload"].get("size", 0), r["payload"].get("workload", "na"), r["payload"]["_audit"].get("error", "na")) for r in rows).items())]}
        print(experiment, len(rows), "items; no model calls", flush=True)
    (ROOT / "splits.json").write_text(json.dumps({"version": 2, "seed": 5204, "groups": groups}, indent=2) + "\n")
    (ROOT / "counts.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-existing", action="store_true", help="Repack existing full JSONL; does not regenerate or validate it")
    main(parser.parse_args().pack_existing)
