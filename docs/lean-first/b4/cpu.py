"""Python CPU against Lean CPU of `check_document` over the discourse corpus (lean-first batch 4).

Usage: PYTHONPATH=ROOT python docs/lean-first/b4/cpu.py CORPUS.json.gz SCRATCH
Runs every document once, sequentially, in this process with the `ve` of ROOT, and prints the
process's own CPU (Python) and its children's CPU (the Lean discourse route and other checkers).
"""
import base64, gzip, json, resource, sys, time
from pathlib import Path

from ve.document import check_document

corpus = json.loads(gzip.decompress(Path(sys.argv[1]).read_bytes()))
scratch = Path(sys.argv[2])
paths = []
for entry in corpus:
    directory = scratch / entry["id"]
    directory.mkdir(parents=True, exist_ok=True)
    for name, data in entry["files"].items():
        try:
            (directory / name).write_bytes(base64.b64decode(data))
        except OSError:
            pass
    path = directory / "document.ve.md"
    path.write_bytes(base64.b64decode(entry["document"]))
    paths.append(path)
start, self0, child0 = time.time(), resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
admitted = 0
for path in paths:
    try:
        check_document(path)
        admitted += 1
    except Exception:  # noqa: BLE001
        pass
self1, child1 = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
cpu = lambda a, b: (b.ru_utime + b.ru_stime) - (a.ru_utime + a.ru_stime)
print(json.dumps({"documents": len(paths), "checked": admitted, "wall_s": round(time.time() - start, 1),
                  "python_cpu_s": round(cpu(self0, self1), 1), "children_cpu_s": round(cpu(child0, child1), 1)}))
