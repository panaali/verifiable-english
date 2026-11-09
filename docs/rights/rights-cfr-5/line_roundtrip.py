"""rights-cfr-5 evidence: render_line -> parse_line over the rights generator's lines.

Usage: uv run python docs/rights/rights-cfr-5/line_roundtrip.py [SEEDS]  (default 200)
Every claim, liberty and immunity line with a predicate, of every generated document
(conformance/rights_differential.py, seeds 0..SEEDS-1) that correlates; prints one JSON
object: lines, failures, and the failures by cause and by carve-out count."""
import collections
import json
import sys

from conformance.rights_differential import document
from ve.errors import VEError
from ve.rights import RightsEnvironment, correlate
from ve.surface.rights import parse_line, render_line


def main(seeds):
    lines = failures = documents = 0
    causes, by_unless = collections.Counter(), collections.Counter()
    for seed in range(seeds):
        raw, units = document(seed)
        try:
            rights = correlate(raw, units)
        except VEError:
            continue
        documents += 1
        env = RightsEnvironment(raw)
        for unit in units:
            block = unit.get("right") or unit.get("right_lines") or {}
            name = block.get("name") or block.get("right")
            for line in block.get("lines", ()):
                norm = line.get("norm")
                if line["kind"] == "power" or norm["predicate"] is None:
                    continue
                lines += 1
                try:
                    source = render_line(env, name, line["kind"], norm, rights=rights)
                    back = parse_line(env, source, name=norm["name"], rights=rights)
                    cause = None if back == {"right": name, "kind": line["kind"], "norm": norm} else "mismatch"
                except VEError as error:
                    cause = str(error)
                if cause is not None:
                    failures += 1
                    causes[cause] += 1
                    by_unless[f"unless={len(norm['unless'])}"] += 1
    print(json.dumps({"seeds": seeds, "documents": documents, "lines": lines, "failures": failures,
                      "causes": dict(causes), "failures_by_carve_outs": dict(by_unless)}, indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 200)
