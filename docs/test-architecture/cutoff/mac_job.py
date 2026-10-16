"""The batch's measurement jobs on the Mac test runner (never part of the suite).

`measure.py` copies this file into a scratch worktree as tests/test_zz_cutoff_job.py, with a job
file `cutoff-job.json`, and runs it there through mac-pytest.sh, the only way this batch reaches
the runner. Each step's output comes back on standard output between `CUTOFF-BEGIN <name>` and
`CUTOFF-END` lines, base64 of gzip. The recording stays in the runner's per-worktree directory
(`cutoff-store` beside the checkout), so later jobs of the same worktree replay it.

Steps: `record` (tools/answer_cutoff.py record), `replay` (tools/answer_replay.py replay of that
recording against this checkout's build), `table` (the Lean mode table of this checkout,
tools/lean_mode_deps.lean), `pytest` (named tests, their failures), `emit` (a file of the store).
"""
import base64
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT.parent / "cutoff-store"
PYTHON = ["uv", "run", "--frozen", "--group", "dev", "python"]
JOB = "tests/test_zz_cutoff_job.py"  # this file in the runner's checkout: never recorded


def send(name: str, data: bytes) -> None:
    blob = base64.b64encode(gzip.compress(data)).decode()
    print(f"\nCUTOFF-BEGIN {name} {len(blob)}", flush=True)
    for i in range(0, len(blob), 4000):
        print("CUTOFF:" + blob[i:i + 4000], flush=True)
    print("CUTOFF-END", flush=True)


def run(command: list[str], cwd: Path = ROOT, **options) -> subprocess.CompletedProcess:
    env = {**os.environ, "PATH": str(Path.home() / ".elan/bin") + os.pathsep + os.environ.get("PATH", "")}
    print("+", " ".join(command), flush=True)
    return subprocess.run(command, cwd=cwd, env=env, **options)


def build() -> str:
    return hashlib.sha256((ROOT / "lean/.lake/build/bin/ve_service").read_bytes()).hexdigest()


def test_job():
    job = json.loads((ROOT / "cutoff-job.json").read_text())
    report = {"commit": run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
              "service": build(), "steps": []}
    for step in job["steps"]:
        kind = step["kind"]
        if kind == "record":
            units = step.get("units") or [*(path.relative_to(ROOT).as_posix() for path in
                                            sorted((ROOT / "tests").glob("test_*.py")) if path.name != Path(JOB).name),
                                          "tools/test_layer_policy.py"]
            result = run([*PYTHON, "tools/answer_cutoff.py", "record", "--allow-dirty", "--no-build",
                          "--jobs", str(step.get("jobs", 6)), "--output", str(STORE), "--work",
                          str(ROOT.parent / "cutoff-work"), *units])
            report["steps"].append({"kind": kind, "exit": result.returncode})
        elif kind == "replay":
            output = STORE / f"answers-{build()[:16]}.json.gz"
            result = run([*PYTHON, "tools/answer_replay.py", "replay", str(STORE), "--jobs",
                          str(step.get("jobs", 6)), "--output", str(output)])
            report["steps"].append({"kind": kind, "exit": result.returncode, "output": output.name})
            if result.returncode == 0:
                send(output.name, output.read_bytes())
        elif kind == "table":
            result = run(["lake", "env", "lean", "../tools/lean_mode_deps.lean"], cwd=ROOT / "lean",
                         capture_output=True, text=True)
            report["steps"].append({"kind": kind, "exit": result.returncode, "stderr": result.stderr[-2000:]})
            if result.returncode == 0:
                send("modes.json", result.stdout.encode())
        elif kind == "pytest":
            junit = ROOT.parent / "cutoff-junit.xml"
            result = run([*PYTHON, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rfE",
                          f"--junitxml={junit}", *step["args"]], capture_output=True, text=True)
            print(result.stdout[-20000:], flush=True)
            report["steps"].append({"kind": kind, "exit": result.returncode, "args": step["args"]})
            if junit.exists():
                send(f"junit-{step.get('name', 'run')}.xml", junit.read_bytes())
        elif kind == "emit":
            send(step["file"], (STORE / step["file"]).read_bytes())
            report["steps"].append({"kind": kind, "file": step["file"]})
        else:
            raise ValueError(f"unknown step {kind}")
    send("report.json", json.dumps(report).encode())
    print(json.dumps(report), file=sys.stderr)
