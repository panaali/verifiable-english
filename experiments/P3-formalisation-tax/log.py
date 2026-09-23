"""Append an authoring-log event: python log.py <item> <event> [note...]

Events: start, checker_fix (repair after parse/type/eval feedback), diff_fix
(repair after a differential mismatch), end. Timestamps are wall-clock.
"""
import json, sys, time
from pathlib import Path
item, event, *note = sys.argv[1:]
with open(Path(__file__).parent / "authoring_log.jsonl", "a") as f:
    f.write(json.dumps({"item": item, "event": event, "t": round(time.time(), 1),
                        "iso": time.strftime("%Y-%m-%dT%H:%M:%S"), "note": " ".join(note)}) + "\n")
