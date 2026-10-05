"""A pytest plugin that records every Lean executable invocation the test session makes.

Loaded with `-p tests.lean_input_recorder` and `VE_LEAN_INPUTS=<folder>`, it wraps `subprocess.Popen`
so that a process whose program is a file in a `lean/.lake/build/bin/` folder is recorded with its
arguments, the contents of every argument that names an existing file at start-up, and every byte
written to its standard input (through `communicate` or the `ve_service` client's writer). At the end
of the session (of each worker, under xdist) the records are written to
`<folder>/lean-inputs-<pid>.jsonl`, one JSON object per invocation: `exe`, `args` (an input file is
`@file:<n>`), `files` (`name` and base64 `data`), `stdin` (base64, or null when nothing was written)
and `test` (the test that started the process). `tools/lean_output_diff.py --recorded <folder>`
replays them against two builds (bundle OUT of docs/CONSOLIDATION-PLAN.md).

The plugin changes no behaviour: every wrapped call runs as before.
"""

import base64
import json
import os
from pathlib import Path
import subprocess

_RECORDS = []
_ORIGINAL_INIT = subprocess.Popen.__init__
_ORIGINAL_COMMUNICATE = subprocess.Popen.communicate


def _lean_executable(args):
    if isinstance(args, (str, bytes, os.PathLike)) or not args:
        return None
    program = Path(os.fsdecode(args[0]))
    return program.name if program.parent.as_posix().endswith("lean/.lake/build/bin") else None


def _start(self, args, *rest, **kwargs):
    _ORIGINAL_INIT(self, args, *rest, **kwargs)
    name = _lean_executable(args)
    if name is None:
        return
    cwd = Path(os.fsdecode(kwargs.get("cwd") or os.getcwd()))
    recorded_args, files = [], []
    for arg in args[1:]:
        text = os.fsdecode(arg)
        path = Path(text) if Path(text).is_absolute() else cwd / text
        if text not in {"-", ""} and path.is_file():
            recorded_args.append(f"@file:{len(files)}")
            files.append({"name": path.name, "data": base64.b64encode(path.read_bytes()).decode()})
        else:
            recorded_args.append(text)
    self._ve_record = {"exe": name, "args": recorded_args, "files": files, "stdin": None,
                       "test": os.environ.get("PYTEST_CURRENT_TEST", "?").rsplit(" ", 1)[0], "_input": bytearray()}
    _RECORDS.append(self._ve_record)


def _feed(record, data):
    if record is not None and data:
        record["_input"] += data.encode() if isinstance(data, str) else bytes(data)


def _communicate(self, input=None, timeout=None):
    _feed(getattr(self, "_ve_record", None), input)
    return _ORIGINAL_COMMUNICATE(self, input, timeout)


def _install():
    subprocess.Popen.__init__ = _start
    subprocess.Popen.communicate = _communicate
    from ve.backends import lean_service

    original_write = lean_service.LeanService._write_all

    def write_all(self, data, deadline):
        _feed(getattr(self._proc, "_ve_record", None), data)
        return original_write(self, data, deadline)

    lean_service.LeanService._write_all = write_all


_install()


def pytest_sessionfinish(session, exitstatus):
    folder = os.environ.get("VE_LEAN_INPUTS")
    if not folder:
        return
    Path(folder).mkdir(parents=True, exist_ok=True)
    with open(Path(folder) / f"lean-inputs-{os.getpid()}.jsonl", "w") as out:
        for record in _RECORDS:
            data = bytes(record.pop("_input"))
            record["stdin"] = base64.b64encode(data).decode() if data else None
            out.write(json.dumps(record) + "\n")
