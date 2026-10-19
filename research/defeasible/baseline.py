"""DF-0.3, the defeasible plan's baseline (docs/spec/defeasible-PLAN.md, DF-0 item 3; 0.2's DF-0.3 row).

"Baseline: on RD-9 SC-9's probe translation, P-1's and P-2's questions with today's kinds, answers recorded
verbatim." The probe translation is `CE4` (`tests/ce4.py`, the pilot's pinned translation); this script builds its
documents from there, never retyped:

- P-1: each of the three sets' `default` candidate as a standalone soft document in `CE4`'s frame: `CE4`'s
  environment, the set's sentence, one unit whose content is the candidate.
- P-2: the same three questions on `CE4` itself, the document of `tests/test_readings_sd_ce4.py`.

Each question goes through today's public route, `ve document readings <doc> --conclusion <question>`, and its exit
code, stdout and stderr are saved verbatim in `docs/research/evidence/defeasible/baseline/baseline.json` with the
documents, the questions, the main commit, the command, the host load and the binaries' hashes. No model is called
and no whole-constitution document is run (L70).

    uv run python research/defeasible/baseline.py
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from baseline_cases import BINARIES, COMMAND, EXPECTED, QUESTIONS, follows, p1_document  # noqa: E402
from tests.subprocesses import HANG_TIMEOUT  # noqa: E402

OUT = ROOT / "docs/research/evidence/defeasible/baseline"


def p2_document():
    """`CE4` as `tests/test_readings_sd_ce4.py` writes it (its one owner)."""
    from tests.test_readings_sd_ce4 import ce4_document
    with tempfile.TemporaryDirectory() as tmp:
        return ce4_document(Path(tmp)).read_bytes()


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True,
                          timeout=HANG_TIMEOUT).stdout.strip()


def ask(document, question):
    """Today's route, verbatim: `ve document readings <document> --conclusion <question>`."""
    argv = ["ve", "document", "readings", str(document.relative_to(ROOT)), "--conclusion",
            str(question.relative_to(ROOT))]
    done = subprocess.run([sys.executable, "-m", *argv], cwd=ROOT, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)
    try:
        verdict = json.loads(done.stdout)["verdict"]
    except (ValueError, KeyError, TypeError):
        verdict = None
    return {"argv": argv, "exit": done.returncode, "stdout": done.stdout, "stderr": done.stderr, "verdict": verdict}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    head = git("rev-parse", "HEAD")
    main_commit = git("merge-base", "HEAD", "main")
    changed = git("diff", "--name-only", main_commit, "HEAD", "--", "ve", "lean", "rust", "tools", "tests").split()
    lock = json.loads((ROOT / "lean/checkers.lock").read_text())
    binaries = {}
    for name, path in BINARIES.items():
        digest = sha256(ROOT / path)
        binaries[name] = {"path": path, "sha256": digest, "pinned": digest in lock[name]}
    load_before = os.getloadavg()
    files, p1, p2 = {}, [], []
    p2_path = OUT / "p2-ce4.ve.md"
    p2_path.write_bytes(p2_document())
    for set_id, question in QUESTIONS.items():
        q_path = OUT / f"question-{set_id}.json"
        q_path.write_text(json.dumps(question) + "\n")
        p1_path = OUT / f"p1-{set_id}.ve.md"
        p1_path.write_bytes(p1_document(set_id))
        p1.append({"set": set_id, **ask(p1_path, q_path)})
        p2.append({"set": set_id, **ask(p2_path, q_path)})
        files[q_path.name] = sha256(q_path)
        files[p1_path.name] = sha256(p1_path)
    files[p2_path.name] = sha256(p2_path)
    record = {
        "item": "DF-0.3",
        "plan": "docs/spec/defeasible-PLAN.md (00a45ce36), DF-0 item 3",
        "date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "main_commit": main_commit,
        "head": head,
        "product_files_changed_from_main": changed,
        "command": COMMAND,
        "host": {"system": platform.system(), "cpus": os.cpu_count(),
                 "load_before": [round(x, 2) for x in load_before],
                 "load_after": [round(x, 2) for x in os.getloadavg()]},
        "binaries": binaries,
        "files": dict(sorted(files.items())),
        "expected": EXPECTED,
        "p1": p1,
        "p2": p2,
        "measured": {"p1_answered": sum(follows(a) for a in p1),
                     "p1_verdicts": {a["set"]: a["verdict"] for a in p1},
                     "p2_verdicts": {a["set"]: a["verdict"] for a in p2}},
    }
    (OUT / "baseline.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(record["measured"], indent=2))


if __name__ == "__main__":
    main()
