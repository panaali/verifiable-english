#!/usr/bin/env python3
"""AR-2's tool checks at the batch head (plan 4.1 item 3), written to docs/arch/AR-2/evidence/checks.json.

    uv run python docs/arch/AR-2/checks.py BASE

Runs each check below at HEAD and saves its exit code and output tail, and the changed-files trust report
(`tools/trust_changes.py --since BASE --json`) whole. Batch evidence (D4): not a test of the suite.
"""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = Path(__file__).resolve().parent / "evidence/checks.json"
PY = sys.executable


def checks(base: str) -> list[tuple[str, list[str], Path]]:
    return [
        ("frozen", [PY, "VE/Route/frozen.py"], ROOT / "lean"),
        ("question-lock", [PY, "tools/question_lock.py"], ROOT),
        ("trust-since", [PY, "tools/trust_map.py", "--since", base], ROOT),
        ("trust-check", [PY, "tools/trust_map.py", "--check"], ROOT),
        ("lean-statements", [PY, "tools/lean_statements.py", "--check"], ROOT),
        ("lean-audit", [PY, "lean/audit.py", "--check"], ROOT),
        ("regen-generated", [PY, "tools/regen_generated.py", "--check"], ROOT),
        ("trust-changes", [PY, "tools/trust_changes.py", "--since", base], ROOT),
    ]


def main(base: str) -> int:
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()
    base = subprocess.run(["git", "-C", str(ROOT), "rev-parse", base], capture_output=True, text=True,
                          check=True).stdout.strip()
    out = {"base": base, "head": head, "checks": {}}
    for name, command, cwd in checks(base):
        done = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
        lines = [line for line in (done.stdout + done.stderr).splitlines() if line.strip()]
        out["checks"][name] = {"command": " ".join(Path(c).name if c == PY else c for c in command),
                               "exit": done.returncode, "tail": lines[-12:]}
        print(f"{name}: exit {done.returncode}", flush=True)
    report = subprocess.run([PY, "tools/trust_changes.py", "--since", base, "--json"], cwd=ROOT,
                            capture_output=True, text=True)
    out["trust_changes"] = json.loads(report.stdout) if report.returncode == 0 else None
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out, indent=1) + "\n")
    return 0 if all(c["exit"] == 0 for c in out["checks"].values()) and out["trust_changes"] is not None else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
