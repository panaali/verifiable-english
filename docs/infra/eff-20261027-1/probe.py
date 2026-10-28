"""eff-20261027-1 measurement probe: one cold statement dump of a Lean tree, timed per Lean run.

    python3 probe.py dump TREE serial|split PARTS OUT.json [OUTDIR]
    python3 probe.py audit TREE OUT.json

`dump` loads TREE's own tools/lean_statements.py and runs its `dump_all` (VE_RUN_CACHE=off, no cache) with
`run_lean` replaced by a copy that runs each `lake env lean` under /usr/bin/time (wall seconds, peak RSS). With
`split`, the Statements run is the prototype: the audited names (sorted) cut into PARTS contiguous parts, each one
`lake env lean` of the same SCRIPT over its own VE_STATEMENT_NAMES file, run at once, the outputs joined in part
order. The three outputs go to OUTDIR (statements.txt, predicates.txt, declarations.txt) when given.
`audit` runs TREE's own `python3 lean/audit.py --check` (no cache) with each part's `lake env lean` under
/usr/bin/time: the parts' peak RSS, the bound the split must stay within.
The load average is read before and after. Read-only on TREE (Lean writes its temporary files under /tmp).
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

TIME = ["/usr/bin/time", "-f", "%e %M"]


def timed(command, rss_dir, label, **kwargs):
    out = Path(rss_dir) / f"{label}.time"
    done = subprocess.run([*TIME, "-o", str(out), *command], **kwargs)
    seconds, kilobytes = out.read_text().split()[-2:]
    return done, float(seconds), int(kilobytes)


def dump(tree: Path, mode: str, parts: int, out: Path, outdir: Path | None) -> None:
    os.environ["VE_RUN_CACHE"] = "off"
    sys.path[:0] = [str(tree / "tools"), str(tree)]
    L = importlib.import_module("lean_statements")
    assert Path(L.__file__).resolve().is_relative_to(tree.resolve()), L.__file__
    runs: list[dict] = []
    rss_dir = tempfile.mkdtemp(prefix="ve-probe-time-")

    def one(root, folder, script, label, env):
        path = folder / f"{label}.lean"
        path.write_text(script)
        done, seconds, kb = timed(["lake", "env", "lean", str(path)], rss_dir, label, cwd=root / "lean", text=True,
                                  capture_output=True, check=False, env={**os.environ, **env})
        if done.returncode:
            raise SystemExit(f"lake env lean failed on {label} ({done.returncode}):\n{done.stderr}{done.stdout[-2000:]}")
        runs.append({"label": label, "seconds": seconds, "peak_rss_kb": kb, "lines": len(done.stdout.splitlines())})
        return done.stdout

    def run_lean(root, folder, script, label, env):
        if label != "Statements" or mode == "serial":
            return one(root, folder, script, label, env)
        names = [n for n in Path(env["VE_STATEMENT_NAMES"]).read_text().splitlines() if n]
        size = -(-len(names) // parts)
        chunks = [names[i:i + size] for i in range(0, len(names), size)]
        assert [n for c in chunks for n in c] == names
        for index, chunk in enumerate(chunks):
            (folder / f"names{index}.txt").write_text("\n".join(chunk) + "\n")
        start = time.monotonic()
        with ThreadPoolExecutor(len(chunks)) as pool:
            outs = list(pool.map(lambda i: one(root, folder, script, f"Statements{i}",
                                               {"VE_STATEMENT_NAMES": str(folder / f"names{i}.txt")}),
                                 range(len(chunks))))
        runs.append({"label": "Statements(all parts)", "seconds": round(time.monotonic() - start, 1),
                     "parts": len(chunks), "part_size": size})
        return "".join(outs)

    L.run_lean = run_lean
    load0 = os.getloadavg()
    start = time.monotonic()
    texts = L.dump_all(tree)
    total = time.monotonic() - start
    committed = [(tree / "lean" / name).read_text() for name in ("statements.txt", "predicates.txt",
                                                                 "declarations.txt")]
    if outdir:
        outdir.mkdir(parents=True, exist_ok=True)
        for name, text in zip(("statements.txt", "predicates.txt", "declarations.txt"), texts):
            (outdir / name).write_text(text)
    statements = [r for r in runs if r["label"].startswith("Statements") and "peak_rss_kb" in r]
    row = {"tree": str(tree), "head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=tree, text=True,
                                                     capture_output=True).stdout.strip(),
           "mode": mode, "parts": parts if mode == "split" else 1, "total_seconds": round(total, 1),
           "load_before": load0, "load_after": os.getloadavg(),
           "statements_seconds": next(r["seconds"] for r in runs if r["label"] in ("Statements",
                                                                                   "Statements(all parts)")),
           "statements_peak_rss_kb_sum": sum(r["peak_rss_kb"] for r in statements),
           "statements_peak_rss_kb_max": max(r["peak_rss_kb"] for r in statements),
           "tree_seconds": next(r["seconds"] for r in runs if r["label"] == "Tree"),
           "alone_runs": sum(r["label"].startswith("Alone") for r in runs),
           "theorems": texts[0].count("\ntheorem "),
           "matches_committed": [a == b for a, b in zip(texts, committed)],
           "runs": runs}
    out.write_text(json.dumps(row, indent=1) + "\n")
    print(json.dumps({k: v for k, v in row.items() if k != "runs"}))


def audit(tree: Path, out: Path) -> None:
    os.environ["VE_RUN_CACHE"] = "off"
    sys.path[:0] = [str(tree / "lean"), str(tree / "tools"), str(tree)]
    A = importlib.import_module("audit")
    assert Path(A.__file__).resolve().is_relative_to(tree.resolve()), A.__file__
    rss_dir = tempfile.mkdtemp(prefix="ve-probe-time-")
    runs: list[dict] = []
    real = subprocess.run

    class Shim:
        def __getattr__(self, name):
            return getattr(subprocess, name)

        @staticmethod
        def run(command, *args, **kwargs):
            if list(command[:3]) == ["lake", "env", "lean"]:
                label = Path(command[3]).stem
                done, seconds, kb = timed(command, rss_dir, label, *args, **kwargs)
                runs.append({"label": label, "seconds": seconds, "peak_rss_kb": kb})
                return done
            return real(command, *args, **kwargs)

    A.subprocess = Shim()
    load0 = os.getloadavg()
    start = time.monotonic()
    A.main(["--check"])
    total = time.monotonic() - start
    row = {"tree": str(tree), "what": "lean/audit.py --check (no cache)", "total_seconds": round(total, 1),
           "load_before": load0, "load_after": os.getloadavg(), "parts": len(runs),
           "parts_peak_rss_kb_sum": sum(r["peak_rss_kb"] for r in runs),
           "parts_peak_rss_kb_max": max(r["peak_rss_kb"] for r in runs), "runs": runs}
    out.write_text(json.dumps(row, indent=1) + "\n")
    print(json.dumps({k: v for k, v in row.items() if k != "runs"}))


if __name__ == "__main__":
    if sys.argv[1] == "dump":
        dump(Path(sys.argv[2]), sys.argv[3], int(sys.argv[4]), Path(sys.argv[5]),
             Path(sys.argv[6]) if len(sys.argv) > 6 else None)
    else:
        audit(Path(sys.argv[2]), Path(sys.argv[3]))
