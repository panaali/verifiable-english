#!/usr/bin/env python3
"""SC-9: the checks, queries and measurements of the probe translation, before and after (plan SC-9 items 2, 3, 5).

    uv run python usecases/claude-constitution-pilot/run-20261104T0716Z/measure.py

Three documents: `before`, the translation as committed (run 20261010T1800Z at `76922d6c`, `migrate_soft.pinned`);
`after`, `probe-translation.probe.md` (`migrate_soft.py`); and `strict`, the probe with u0073.s05 as its strict force
twin (the same rule, `mode: strict`, no exception), for C9's separation from the strict reading. Each step is one
Python command, run one at a time in the foreground under `/usr/bin/time -v` with a 16 GB memory limit (L70);
the host load is read before each step. Each answer is saved verbatim (`answers/<document>/<step>.out`
and `.err`); `answers/measurements.json` holds the exit code, wall, CPU, peak RSS and host load of every step. A run
that is killed or ends unavailable is recorded as measured and not rerun.
"""
from __future__ import annotations

import json
import os
import re
import resource
import subprocess
import sys
import tempfile
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(RUN))
import migrate_soft  # noqa: E402
from c9_status import strict_twin  # noqa: E402

pilot = migrate_soft.pilot
ANSWERS = RUN / "answers"
DENIAL, CLARIFY = "force-u0125-s04-p2", "force-u0036-s05"
LOAD = ("import json, sys; from ve.document import load_document; d = load_document(sys.argv[1]); "
        "s2 = d.get('readings_s2') or {}; print(json.dumps({'admitted': True, 'route': s2.get('route'), "
        "'finding': s2.get('finding'), 'choices': len(s2.get('choices', [])), 'soft_premises': s2.get('soft_premises'), "
        "'units': {u['id']: [u['status'], u.get('meaning_id')] for u in d['units'] if u['status'] != 'UNFORMALISED'}}, "
        "indent=1, ensure_ascii=False))")
# Lean's premises answer on the readings route (C8, SC-5's `decided_units`): the status and the units it decides.
DECIDED = ("import json, sys; from ve.document import load_document; from ve.readings_verdicts import context; "
           "a = context(load_document(sys.argv[1])).premises_answer(); print(json.dumps({'status': a['result']"
           "['status'], 'decided_units': a.get('decided_units'), 'per_choice': sorted({e['premises'] for e in "
           "a.get('per_choice', [])})}, indent=1))")
POINT_STATUS = (f"import sys; sys.path.insert(0, {str(RUN)!r}); from c9_status import point_statuses; "
                "point_statuses(sys.argv[1])")


def queries(*names):
    return [(f"readings-{name}{'-under-' + under.replace(':', '-') if under else ''}",
             ["document", "readings", "{doc}", "--conclusion", str(RUN / "queries" / f"{name}.json"),
              *(["--under", under] if under else [])]) for name, under in names]


CHECKS = [("load", ["-c", LOAD, "{doc}"]), ("decided", ["-c", DECIDED, "{doc}"]), ("check", ["document", "check", "{doc}"]),
          ("render", ["document", "render", "{doc}"]), ("coverage", ["document", "coverage", "{doc}"])]
CHECKS = [(name, argv if argv[0] == "-c" else ["-m", "ve", *argv]) for name, argv in CHECKS]
C9 = queries(("c9-unsafe-required", None), ("c9-unsafe-not-required", None), ("c9-none-required", None))
QUERIES = queries(("c6-denial", None), ("c6-denial", f"{DENIAL}:0"), ("c6-denial", f"{DENIAL}:1"),
                  ("c7-clarification", None), ("c7-clarification", f"{CLARIFY}:0"), ("claim-human", None))
STEPS = {"before": CHECKS + [(n, ["-m", "ve", *a]) for n, a in QUERIES],
         "after": CHECKS + [(n, ["-m", "ve", *a]) for n, a in QUERIES + C9]
                  + [("point-status-c9", ["-c", POINT_STATUS, "{doc}"])],
         "strict": [(n, ["-m", "ve", *a]) for n, a in C9]
                   + [("point-status-c9", ["-c", POINT_STATUS, "{doc}"])]}
TIME = {"wall": r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (.+)", "user": r"User time \(seconds\): (.+)",
        "system": r"System time \(seconds\): (.+)", "max_rss_kb": r"Maximum resident set size \(kbytes\): (.+)",
        "exit": r"Exit status: (.+)"}


def host():
    """The host load when a step starts: load averages, processors and available memory."""
    meminfo = dict(line.split(":", 1) for line in Path("/proc/meminfo").read_text().splitlines())
    return {"loadavg": os.getloadavg(), "cpus": os.cpu_count(), "mem_available_kb": int(meminfo["MemAvailable"].split()[0])}


def seconds(wall):
    parts = [float(p) for p in wall.split(":")]
    return round(sum(p * 60 ** i for i, p in enumerate(reversed(parts))), 2)


def step(document, path, name, argv):
    out = ANSWERS / document
    out.mkdir(parents=True, exist_ok=True)
    started = host()
    command = ["systemd-run", "--user", "--scope", "-q", "-p", "MemoryMax=16G", "-p", "MemorySwapMax=0",
               "/usr/bin/time", "-v", sys.executable, *[str(path) if a == "{doc}" else a for a in argv]]
    proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    limit = "systemd MemoryMax=16G"
    if proc.returncode and "Failed to connect to bus" in proc.stderr:
        # Managed workers can have no user bus. This is a setup failure, not a VE answer; keep the same
        # sequential, foreground timing and an explicit 16 GB process limit.
        def cap_memory():
            resource.setrlimit(resource.RLIMIT_AS, (16 << 30, 16 << 30))

        command = ["/usr/bin/time", "-v", sys.executable,
                   *[str(path) if a == "{doc}" else a for a in argv]]
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False,
                              preexec_fn=cap_memory)
        limit = "RLIMIT_AS=16G (user bus unavailable)"
    marker = proc.stderr.rfind("\tCommand being timed:")
    status = proc.stderr.rfind("Command exited with non-zero status", 0, marker if marker >= 0 else None)
    marker = status if status >= 0 else marker
    err, timing = (proc.stderr[:marker], proc.stderr[marker:]) if marker >= 0 else (proc.stderr, "")
    (out / f"{name}.out").write_text(proc.stdout)
    (out / f"{name}.err").write_text(err)
    found = {k: (m[1].strip() if (m := re.search(p, timing)) else None) for k, p in TIME.items()}
    row = {"document": document, "step": name, "returncode": proc.returncode, "host_at_start": started,
           "memory_limit": limit,
           "wall_s": seconds(found["wall"]) if found["wall"] else None,
           "cpu_s": round(float(found["user"]) + float(found["system"]), 2) if found["user"] else None,
           "max_rss_kb": int(found["max_rss_kb"]) if found["max_rss_kb"] else None,
           "stderr_last_line": err.strip().splitlines()[-1] if err.strip() else ""}
    print(json.dumps(row), flush=True)
    return row


def main(only=()):
    """Every step, or the steps named in `only`, whose rows replace those of the same name in the saved record."""
    raw = migrate_soft.pinned()
    _, front, source = raw.split(b"---\n", 2)
    probe = migrate_soft.PROBE
    after, after_source = pilot.read(probe)
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        paths = {"before": Path(tmp) / "translation.ve.md", "after": probe,
                 "strict": Path(tmp) / "probe-strict-twin.ve.md"}
        paths["before"].write_bytes(raw)
        pilot.write(paths["strict"], strict_twin(after), after_source)
        for document, steps in STEPS.items():
            rows += [step(document, paths[document], name, argv) for name, argv in steps if not only or name in only]
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    for row in rows:
        row["commit"] = commit
    record = ANSWERS / "measurements.json"
    kept = [r for r in json.loads(record.read_text())["steps"] if r["step"] not in only] if only else []
    record.write_text(json.dumps({"translation": f"{migrate_soft.PILOT_COMMIT}:{migrate_soft.PILOT_PATH}",
                                  "steps": kept + rows}, indent=1) + "\n")


if __name__ == "__main__":
    main(tuple(sys.argv[2:]) if sys.argv[1:2] == ["--only"] else ())
