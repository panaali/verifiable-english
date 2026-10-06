"""Capture the quantity corpus of the lean-first gate (docs/LEAN-FIRST-PLAN.md 5.1 item 2, batch 9).

No W6 statement corpus is stored in the repository: the W6 tests and use cases build their
environments, statements, models, certificates and documents in code. This module is a pytest
plugin that records every call the tests make to a W6 public operation, and a writer that merges the
records into one corpus file, deduplicated by content::

    cd BASE; LF9_CAPTURE=/tmp/capture.jsonl PYTHONPATH=BASE:HEAD/docs/lean-first/b9 \\
        HEAD/.venv/bin/python -m pytest -p capture_quantity -n 8 tests/test_units_*w6a.py ...
    python docs/lean-first/b9/capture_quantity.py write /tmp/capture.jsonl docs/lean-first/quantity-corpus.json.gz

Run the plugin in the base checkout, so the corpus holds the inputs the tests passed before the batch.
The operations (`QUANTITY_OPS` of `tools/lean_first_diff.py`) are `Environment` of a W6 envelope,
`elaborate_quantity`, `quantity_meaning_id`, `quantity_countermodel`, `check_quantity_certificate`
(at its default step budget), `prove_quantity` and `admit_document` of a W6 environment. Each process
appends to `$LF9_CAPTURE.<pid>`. `tools/lean_first_diff.py --corpus quantity` replays every entry
through the recorded checkout's `ve`.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import sys
from pathlib import Path

LIMIT = 1 << 20  # an entry over 1 MiB of JSON (the 10,000-node limit probes) is kept once per shape


def _raw(environment):
    from ve.environment import Environment
    return environment.to_dict() if isinstance(environment, Environment) else environment


def _w6(raw) -> bool:
    return type(raw) is dict and ("unit_schema" in raw or "units" in raw)


def _write(entry: dict) -> None:
    try:
        line = json.dumps(entry, sort_keys=True, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError):
        return  # not a wire value (a Python object, a float NaN): no other checkout could replay it
    if len(line) > LIMIT:
        return
    with open(f"{os.environ['LF9_CAPTURE']}.{os.getpid()}", "a") as out:
        out.write(line + "\n")


def _wrap(module, name, build):
    original = getattr(module, name)

    def recording(*args, **kwargs):
        try:
            entry = build(*args, **kwargs)
            if entry is not None:
                _write(entry)
        except Exception as exc:  # noqa: BLE001  (capture never changes a test's outcome)
            print(f"capture failed: {exc}", file=sys.stderr)
        return original(*args, **kwargs)

    setattr(module, name, recording)


def pytest_configure(config):
    import ve.admission as admission
    import ve.environment as environment
    import ve.units as units

    _wrap(units, "elaborate_quantity", lambda env, payload: {
        "op": "elaborate", "environment": _raw(env), "quantity": payload})
    _wrap(units, "quantity_meaning_id", lambda env, payload: {
        "op": "meaning_id", "environment": _raw(env), "quantity": payload})
    _wrap(units, "quantity_countermodel", lambda env, premises, conclusion, model: {
        "op": "countermodel", "environment": _raw(env), "premises": premises, "conclusion": conclusion,
        "model": model})
    _wrap(units, "check_quantity_certificate", lambda env, premises, conclusion, certificate, **more: None
          if more else {"op": "certificate", "environment": _raw(env), "premises": premises,
                        "conclusion": conclusion, "certificate": certificate})
    _wrap(units, "prove_quantity", lambda env, premises, conclusion, **more: None if more else {
        "op": "prove", "environment": _raw(env), "premises": premises, "conclusion": conclusion})

    def admission_entry(env, document):
        raw = _raw(env)
        return {"op": "admission", "environment": raw, "document": document} if _w6(raw) else None
    _wrap(admission, "admit_document", admission_entry)

    original = environment.Environment.__init__

    def init(self, data, *args, **kwargs):
        if _w6(data) and not args and not kwargs:
            try:
                _write({"op": "environment", "environment": data})
            except Exception as exc:  # noqa: BLE001
                print(f"capture failed: {exc}", file=sys.stderr)
        return original(self, data, *args, **kwargs)

    init.__wrapped__ = original
    environment.Environment.__init__ = init


def write(capture: Path, out: Path) -> int:
    seen = {}
    for path in sorted(capture.parent.glob(capture.name + ".*")):
        # split on newline only: str.splitlines also splits at U+001C..U+001E, U+0085 and U+2028,
        # which the W6 display-string probes hold inside strings
        for line in path.read_text().split("\n"):
            if not line:
                continue
            row = json.loads(line)
            key = hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            seen.setdefault(key, row)
    corpus = [{"id": key[:16], **row} for key, row in sorted(seen.items())]
    out.write_bytes(gzip.compress(json.dumps(corpus, sort_keys=True, ensure_ascii=False).encode(), mtime=0))
    counts = {}
    for entry in corpus:
        counts[entry["op"]] = counts.get(entry["op"], 0) + 1
    print(f"{len(corpus)} entries: {dict(sorted(counts.items()))}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] != "write":
        raise SystemExit("usage: capture_quantity.py write CAPTURE.jsonl CORPUS.json.gz")
    raise SystemExit(write(Path(sys.argv[2]), Path(sys.argv[3])))
