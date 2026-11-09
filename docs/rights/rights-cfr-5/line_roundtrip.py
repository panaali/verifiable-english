"""rights-cfr-5 evidence: render_line -> parse_line over the rights generator's lines.

Usage: uv run python docs/rights/rights-cfr-5/line_roundtrip.py [SEEDS] [--carveout-probe]
Every claim, liberty and immunity line with a predicate, of every generated document
(conformance/rights_differential.py, seeds 0..SEEDS-1, default 200) that correlates; prints
one JSON object: lines, failures, the failures by cause and by carve-out count, and each
failing line (seed, right, line name, cause). `--carveout-probe` first applies, in memory
only, the one-character fix of rights-cfr-5b (ve/norm_english.py:540 drops the second space
before a carve-out sentence), to show that it is the cause of every remaining failure."""
import collections
import json
import pathlib
import sys

from conformance.rights_differential import document
from ve.errors import VEError
from ve.rights import RightsEnvironment, correlate
from ve.surface.rights import parse_line, render_line


def carveout_probe():
    import ve.norm_english as module
    path = pathlib.Path(module.__file__)
    old = '(" " + carveouts if carveouts else "")'
    text = path.read_text()
    assert text.count(old) == 1
    exec(compile(text.replace(old, '(" " + carveouts.lstrip() if carveouts else "")'), str(path), "exec"),
         module.__dict__)


def main(seeds):
    lines = failures = documents = 0
    failing = []
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
                    failing.append([seed, name, norm["name"], cause])
    print(json.dumps({"seeds": seeds, "documents": documents, "lines": lines, "failures": failures,
                      "causes": dict(causes), "failures_by_carve_outs": dict(by_unless), "failing": failing},
                     indent=1))


if __name__ == "__main__":
    arguments = [a for a in sys.argv[1:] if a != "--carveout-probe"]
    if "--carveout-probe" in sys.argv:
        carveout_probe()
    main(int(arguments[0]) if arguments else 200)
