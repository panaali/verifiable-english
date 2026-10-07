"""Same-host W2 caller timing against the frozen pre-switch Python path."""
from __future__ import annotations

import json
from pathlib import Path
import resource
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))

from test_speech_source_lean import templates  # noqa: E402
from tests.frozen_speech.speech_document import SpeechSource as Frozen  # noqa: E402
from ve.speech_document import SpeechSource  # noqa: E402


def main():
    rows = []
    for name, metadata, source in templates():
        for label, ctor in (("base", Frozen), ("head", SpeechSource)):
            samples = []
            child_cpu = []
            for _ in range(20):
                started = time.perf_counter()
                before = resource.getrusage(resource.RUSAGE_CHILDREN)
                ctor(metadata, source.encode(), {})
                after = resource.getrusage(resource.RUSAGE_CHILDREN)
                samples.append((time.perf_counter() - started) * 1000)
                child_cpu.append(((after.ru_utime + after.ru_stime) -
                                  (before.ru_utime + before.ru_stime)) * 1000)
            samples.sort()
            child_cpu.sort()
            rows.append({"case": name, "side": label, "calls": len(samples),
                         "median_wall_ms": round(statistics.median(samples), 3),
                         "p95_wall_ms": round(samples[18], 3), "max_wall_ms": round(samples[-1], 3),
                         "median_child_cpu_ms": round(statistics.median(child_cpu), 3),
                         "p95_child_cpu_ms": round(child_cpu[18], 3)})
    out = ROOT / "docs/lean-first/b11b/evidence/latency.json"
    out.write_text(json.dumps(rows, indent=2) + "\n")
    print(f"wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
