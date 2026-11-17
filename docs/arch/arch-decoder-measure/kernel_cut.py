#!/usr/bin/env python3
"""arch-decoder-measure, deliverable 3: the kernel total with closure's trace decoder cut out.

Runs tools/kernel_closure.py's own measurement twice on the checkout: as it is, and with
`VE.CertificateWire.decodeClosureTrace` added to every request's `opaque` list (an opaque name is
neither counted nor followed, tools/kernel_closure.lean `closure`). The difference is the kernel
lines that are reached only through that decoder: what removing it takes out of the kernel, before
anything a switch adds. Measurement only; it writes nothing in the tree.

    python3 docs/arch/arch-decoder-measure/kernel_cut.py OUT.json   # needs a built lean/.lake
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

import kernel_closure  # noqa: E402

CUT = "VE.CertificateWire.decodeClosureTrace"


def summary(result: dict) -> dict:
    return {"kernel_lines": result["kernel_lines"],
            "paths": {p["name"]: {"tier": p["tier"], "spec": p["spec_lines"], "wrap": p["wrap_lines"],
                                  "lines": p["lines"]} for p in result["paths"]}}


def main(out: str) -> int:
    registry = json.loads(kernel_closure.REGISTRY.read_text())
    before = summary(kernel_closure.measure(registry))
    plain = kernel_closure.requests

    def cut(reg: dict) -> list[dict]:
        return [{**r, "opaque": list(r["opaque"]) + [CUT]} for r in plain(reg)]

    kernel_closure.requests = cut
    try:
        after = summary(kernel_closure.measure(registry))
    finally:
        kernel_closure.requests = plain
    delta = {name: after["paths"][name]["lines"] - row["lines"] for name, row in before["paths"].items()
             if after["paths"][name]["lines"] != row["lines"]}
    data = {"cut": CUT, "before": before, "after": after,
            "kernel_delta": after["kernel_lines"] - before["kernel_lines"], "path_deltas": delta}
    Path(out).write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"kernel_before": before["kernel_lines"], "kernel_after": after["kernel_lines"],
                      "kernel_delta": data["kernel_delta"], "path_deltas": delta}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
