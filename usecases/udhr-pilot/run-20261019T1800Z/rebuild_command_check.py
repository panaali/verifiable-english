"""The committed reading-set rebuild command, tried on the UNCHANGED parts of the previous run (the plan's `--check-noop` precondition).

    uv run --frozen python usecases/udhr-pilot/run-20261019T1800Z/rebuild_command_check.py

Writes evidence/rebuild-command.json: per document, whether `tools/readings_s1_pilot.py --rebuild-reading-ids <doc> --check-noop` reports no_op true, and
whether the document the command writes (--out) still loads.
"""
import json, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from ve.document import load_document
from ve.errors import VEError

prev = HERE  # the carried parts are unchanged from the previous run
docs = {**{f"part0{n}": prev / f"translation-part0{n}.ve.md" for n in range(1, 5)}, "whole": prev / "experiment-whole" / "translation-whole.ve.md"}
out = {}
scratch = Path(tempfile.mkdtemp(prefix="udhr-rebuild-"))
for name, path in docs.items():
    noop = subprocess.run(["uv", "run", "--frozen", "python", "tools/readings_s1_pilot.py", "--rebuild-reading-ids", str(path), "--check-noop"],
                          cwd=ROOT, capture_output=True, text=True)
    row = {"check_noop_exit": noop.returncode, "check_noop_output": (noop.stdout.strip() or noop.stderr.strip().splitlines()[-1])[:200]}
    target = scratch / f"{name}.ve.md"
    made = subprocess.run(["uv", "run", "--frozen", "python", "tools/readings_s1_pilot.py", "--rebuild-reading-ids", str(path), "--out", str(target)],
                          cwd=ROOT, capture_output=True, text=True)
    row["rebuild_exit"] = made.returncode
    if made.returncode == 0:
        try:
            load_document(target); row["rebuilt_document_loads"] = True
        except VEError as e:
            row["rebuilt_document_loads"] = f"no: {getattr(e, 'message', None) or e}"[:200]
    else:
        row["rebuild_error"] = made.stderr.strip().splitlines()[-1][:300]
    out[name] = row
    print(name, row, flush=True)
(HERE / "evidence").mkdir(exist_ok=True)
(HERE / "evidence" / "rebuild-command.json").write_text(json.dumps(out, indent=1) + "\n")
