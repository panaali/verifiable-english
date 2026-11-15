"""Which functions of the `ve` package a harness run executes (stands in for the architect's py_under.py, which this
worktree cannot read after the restart; same question: the ve/norms.py and ve/evaluate.py functions that run).

usage: py_funcs.py <out.json> <script> [args...]   (run from the worktree root whose `ve` is measured)

sys.monitoring (PEP 669) records each code object of a file under `ve/` once at its first start, and each of its lines
once; every event location is disabled after its first hit, so the run costs about what it costs untraced. Events are
interpreter-wide, so every thread is seen. Output: per file the qualified names of the functions that ran and the
number of lines that ran, and totals.
"""
import json
import os
import runpy
import sys
from pathlib import Path

out, script, args = sys.argv[1], sys.argv[2], sys.argv[3:]
root = Path.cwd().resolve() / "ve"
prefix = str(root) + os.sep
mon = sys.monitoring
TOOL = mon.PROFILER_ID
functions: dict[str, set] = {}
lines: dict[str, set] = {}


def _file(code):
    name = code.co_filename
    return name[len(prefix):] if name.startswith(prefix) else None


def on_start(code, offset):
    rel = _file(code)
    if rel is not None:
        functions.setdefault(rel, set()).add(code.co_qualname)
    return mon.DISABLE


def on_line(code, line):
    rel = _file(code)
    if rel is not None:
        lines.setdefault(rel, set()).add(line)
    return mon.DISABLE


mon.use_tool_id(TOOL, "py_funcs")
mon.register_callback(TOOL, mon.events.PY_START, on_start)
mon.register_callback(TOOL, mon.events.LINE, on_line)
mon.set_events(TOOL, mon.events.PY_START | mon.events.LINE)
sys.argv = [script, *args]
sys.path[0] = str(Path(script).resolve().parent)
code = 0
try:
    runpy.run_path(script, run_name="__main__")
except SystemExit as stop:
    code = stop.code if isinstance(stop.code, int) else (0 if stop.code is None else 1)
finally:
    mon.set_events(TOOL, 0)
    mon.free_tool_id(TOOL)
    files = {f: {"functions": sorted(functions.get(f, ())), "lines": len(lines.get(f, ()))}
             for f in sorted(set(functions) | set(lines))}
    Path(out).write_text(json.dumps({"script": script, "exit": code,
                                     "total_functions": sum(len(v["functions"]) for v in files.values()),
                                     "total_lines": sum(v["lines"] for v in files.values()), "files": files},
                                    indent=1) + "\n")
sys.exit(code)
