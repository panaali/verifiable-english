"""The peak memory of a command's whole process tree (Linux /proc), for speed-vocabpar's stop rule (8 GB).

    python3 docs/infra/speed-vocabpar/rss.py OUT.json -- <command ...>

Runs the command, sums the resident memory of it and every descendant five times a second, and writes
{"command", "exit", "seconds", "peak_tree_rss_bytes", "peak_processes", "peak_lean"} to OUT.json, where
`peak_lean` is the most `lean` processes seen at once. A measurement script, not a test.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time

PAGE = os.sysconf("SC_PAGE_SIZE")


def tree() -> dict[int, tuple[int, str, int]]:
    """pid -> (parent, name, resident bytes) for every process readable now."""
    found = {}
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        try:
            stat = Path(f"/proc/{entry}/stat").read_text()
            pages = int(Path(f"/proc/{entry}/statm").read_text().split()[1])
        except (OSError, IndexError, ValueError):
            continue
        name = stat[stat.index("(") + 1:stat.rindex(")")]
        parent = int(stat[stat.rindex(")") + 2:].split()[1])
        found[int(entry)] = (parent, name, pages * PAGE)
    return found


def descendants(root: int, processes: dict[int, tuple[int, str, int]]) -> list[int]:
    children: dict[int, list[int]] = {}
    for pid, (parent, _, _) in processes.items():
        children.setdefault(parent, []).append(pid)
    out, todo = [], [root]
    while todo:
        pid = todo.pop()
        out.append(pid)
        todo += children.get(pid, [])
    return out


def main() -> int:
    out, command = Path(sys.argv[1]), sys.argv[sys.argv.index("--") + 1:]
    start = time.monotonic()
    process = subprocess.Popen(command)
    peak = peak_count = peak_lean = 0
    while process.poll() is None:
        processes = tree()
        pids = [pid for pid in descendants(process.pid, processes) if pid in processes]
        peak = max(peak, sum(processes[pid][2] for pid in pids))
        peak_count = max(peak_count, len(pids))
        peak_lean = max(peak_lean, sum(1 for pid in pids if processes[pid][1] == "lean"))
        time.sleep(0.2)
    out.write_text(json.dumps({"command": command, "exit": process.returncode,
                               "seconds": round(time.monotonic() - start, 1), "peak_tree_rss_bytes": peak,
                               "peak_processes": peak_count, "peak_lean": peak_lean}, indent=1) + "\n")
    return process.returncode


if __name__ == "__main__":
    sys.exit(main())
