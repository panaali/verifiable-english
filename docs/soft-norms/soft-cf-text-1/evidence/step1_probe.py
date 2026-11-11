"""Step 1 probe (soft-cf-text-1): the soft route's CONFLICT-FREE line on every recorded fixture, on the logged test
answers, and on one constructed case whose <k> and open WP(T) differ.

For each CONFLICT-FREE soft answer it prints the status line, <k> (`conditional_on`, Run.lean `sufficientCoherence`),
the printed <j> (read off the line), and the size of the open WP(T) list: the `weighing_points` field of a
`soft-pairs` request with the same environment, norms and pair evidence (Run.lean `pairsResult`).

    uv run python docs/soft-norms/soft-cf-text-1/evidence/step1_probe.py [<probe log dir>]

The optional log dir holds the JSON lines `soft_cf_probe_plugin.py` wrote during a pytest run (see soft-cf-probe.txt).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.setrecursionlimit(100000)

from tests import lean_routes  # noqa: E402
from tests import test_soft_norms_lean as S  # noqa: E402
from ve.ast import formula_from_data  # noqa: E402
from ve.entailment import _binding, _validate_inputs, prove_entailment  # noqa: E402
from ve.wire import digest  # noqa: E402

HEAD = "CONFLICT-FREE among rules on the same act, conditional on "
LINE = re.compile(r"conditional on (\d+) coherence premises; (\d+) weighing points open; ")


def found(x):
    if isinstance(x, dict):
        t = x.get("status_text")
        if isinstance(t, str) and t.startswith(HEAD) and "coherent situation exhibited" in t:
            yield x
        for v in x.values():
            yield from found(v)
    elif isinstance(x, list):
        for v in x:
            yield from found(v)


def wp_size(case):
    [row] = lean_routes.rows("soft-norms", [{"id": "wp", "kind": "soft-pairs", "environment": case["environment"],
                                             "norms": case["norms"], "pairs": case.get("pairs", {})}])
    return len(row["weighing_points"])


def report(source, case, row):
    k, j = (int(n) for n in LINE.search(row["status_text"]).groups())
    wp = wp_size(case) if case.get("kind") == "soft-conflict" else "n/a"
    print(f"{source} | {row['status_text']} | k={k} (conditional_on {len(row['conditional_on'])}) | j={j} | "
          f"WP(T)={wp}")


def fixtures():
    for name in ("relay-gate-cases.jsonl", "route-cases.jsonl"):
        for n, line in enumerate((ROOT / "tests/data" / name).read_text().splitlines(), 1):
            if "soft-conflict" not in line:
                continue
            record = json.loads(line)
            mode, case = record[-2], record[-1]
            if case.get("kind") == "soft-conflict" and "witness" in case:
                continue
            for row in found(lean_routes.rows(mode, [case])):
                report(f"tests/data/{name}:{n} ({mode} {case.get('id')})", case, row)


def logged(directory):
    seen = set()
    for path in sorted(Path(directory).glob("log-*.jsonl")):
        for line in path.read_text().splitlines():
            d = json.loads(line)
            key = (d["test"].rsplit(" ", 1)[0], json.dumps(d["case"], sort_keys=True), d["row"]["status_text"])
            if key in seen:
                continue
            seen.add(key)
            report(key[0], d["case"], d["row"])


def constructed():
    """One default guarded by bottom (a,b collide, unranked: one open weighing point) with certificates whose
    traces do not use the coherence premise, so `sufficientCoherence` drops it: <k> 0, WP(T) 1."""
    environment = S.env()
    norms = [S.should("a", "x_required", True), S.should("b", "x_permitted", False)]
    norms[0]["norm"]["guard"] = ["bottom"]
    row = S.elaborate(S.LEAN, environment, norms)
    profiles = environment["profiles"]
    env_id = digest(f"ve-environment-{S.identity(profiles)}\n", environment)
    doc_hash = digest(f"ve-soft-norms-{S.identity(profiles)}\n",
                      {"environment_id": env_id, "document": [S.canonical_norm(n) for n in norms]})
    base = S.base_prime(row)
    soft = [b["ast"] for b in row["background"] if b["generator"] == "soft"]
    packages = {}
    for t in row["conflict_targets"]:
        closed = ["not", t["ast"]]
        for sort in reversed(t["sorts"]):
            closed = ["forall", sort, closed]
        conclusion = formula_from_data(base, closed)
        found_ = prove_entailment(base, [formula_from_data(base, ["top"]) for _ in soft], conclusion)
        assert found_.status == "Found", t["target"]
        real = _validate_inputs(base, [formula_from_data(base, f) for f in soft], conclusion, background=True)
        packages[t["target"]] = {"environment_id": env_id, "document_hash": doc_hash, "target": t["target"],
                                 "certificate": {**_binding(base, real, conclusion),
                                                 "trace": found_.certificate["trace"]}}
    case = {"id": "c", "kind": "soft-conflict", "environment": environment, "norms": norms, "packages": packages}
    [answer] = lean_routes.rows("soft-norms", [case])
    report("constructed (default a guarded by bottom, certificates without Coh)", case, answer)


if __name__ == "__main__":
    fixtures()
    if len(sys.argv) > 1:
        logged(sys.argv[1])
    constructed()
