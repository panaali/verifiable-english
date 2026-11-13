"""Write the 33 norm-defaults route cases as `tests/lean_input_recorder.py` records, one `ve_service` session each.

usage (from the head checkout, whose `tools/lean_output_diff.route_session` builds the session):
    uv run python <this file> <cases.jsonl> <out dir>

Each record's `test` names the case: `route-case nd-NN id=<id> kind=<kind> sha256=<first 12 hex of its line>`.
The listing printed to stdout is saved in the differential record, so the record names every case it ran.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd()))
from tools.lean_output_diff import route_session  # noqa: E402  (the head checkout's own session builder)


def main(cases_path: Path, out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for number, line in enumerate(cases_path.read_text().splitlines(), 1):
        mode, case = json.loads(line)
        assert mode == "norm-defaults", line
        name = (f"route-case nd-{number:02d} id={case.get('id')} kind={case.get('kind')} "
                f"sha256={hashlib.sha256(line.encode()).hexdigest()[:12]}")
        stdin = route_session(mode, [case])
        records.append({"exe": "ve_service", "args": [], "files": [], "stdin": base64.b64encode(stdin).decode(),
                        "test": name})
        print(name)
    (out / "route-cases.jsonl").write_text("".join(json.dumps(record) + "\n" for record in records))
    print(f"{len(records)} route-case sessions written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
