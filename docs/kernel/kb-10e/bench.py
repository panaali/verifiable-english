"""Stage timings of one `soft-selected` case in the persistent Lean service (kb-10e, deliverable 1).

usage: python docs/kernel/kb-10e/bench.py <case.json> [--reps 5] [--handle] [--exe PATH]

Talks to `lean/.lake/build/bin/ve_service` through stdin and stdout with the request lines
`ve/backends/lean_service.py` writes (`LeanService._request_line`), one process for the whole run,
and prints the median wall time of each variant in milliseconds. The written-out variants cut the
runner after one stage each (a bad kind, no model, a model that fails to decode, an empty query
list, one query, the captured queries, 200 queries), so the difference of two medians is one stage.
`--handle` adds the soft-document handle variants of kb-10e: the first call (the request that
registers the document) on a fresh process and on a process that already holds other documents,
and the repeat call naming a registered document. Run under `iso.sh <name> 8G --`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def text(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


class Service:
    def __init__(self, exe: Path):
        self.proc = subprocess.Popen([str(exe)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)
        self.proc.stdout.readline()
        self.n = 0

    def send(self, cases: list, environments: dict[str, str] | None = None) -> tuple[float, dict]:
        self.n += 1
        registered = ("" if not environments else ',"environments":{' + ",".join(
            json.dumps(d) + ":" + t for d, t in environments.items()) + "}")
        line = ('{"id":"r%d","mode":"soft-norms","budget":{"cases":256,"bytes":4194304}' % self.n
                + registered + ',"cases":' + text(cases) + "}\n").encode()
        cpu = self.cpu()
        start = time.perf_counter()
        self.proc.stdin.write(line)
        out = self.proc.stdout.readline()
        wall = time.perf_counter() - start
        self.last_cpu = self.cpu() - cpu
        return wall, json.loads(out)

    def cpu(self) -> float:
        """User plus system CPU seconds of the service process (`/proc/<pid>/stat`)."""
        fields = Path(f"/proc/{self.proc.pid}/stat").read_text().rsplit(")", 1)[1].split()
        return (int(fields[11]) + int(fields[12])) / 100.0

    def close(self) -> None:
        self.proc.stdin.close()
        self.proc.wait()


def median_ms(xs: list[float]) -> float:
    return round(statistics.median(xs) * 1000, 1)


def status(response: dict) -> str:
    if response.get("status") != "ok":
        return "request error: " + str(response.get("error"))[:80]
    result = response["results"][0]["result"]
    return result.get("status", "?") + ("" if result.get("status") == "ok" else ": " + str(result.get("error"))[:80])


def written_out(svc: Service, case: dict, reps: int) -> dict:
    base = {k: case[k] for k in ("id", "kind", "environment", "norms", "model")}
    q = case["queries"]
    variants = {
        "parse (bad kind)": dict(base, kind="no-such-kind", queries=q),
        "source (no model)": {k: v for k, v in dict(base, queries=q).items() if k != "model"},
        "vocabulary (model 7)": dict(base, model=7, queries=q),
        "model (no query)": dict(base, queries=[]),
        "1 query": dict(base, queries=q[:1]),
        f"captured ({len(q)} queries)": dict(base, queries=q),
        "200 queries": dict(base, queries=(q * 200)[:200]),
    }
    out = {}
    for name, c in variants.items():
        times, cpus, last = [], [], None
        for _ in range(reps):
            dt, last = svc.send([c])
            times.append(dt)
            cpus.append(svc.last_cpu)
        out[name] = (median_ms(times), median_ms(cpus), status(last))
    return out


def soft_document(case: dict) -> tuple[str, str]:
    doc = text({"environment": case["environment"], "norms": case["norms"]})
    return hashlib.sha256(doc.encode()).hexdigest(), doc


def handle_variants(exe: Path, case: dict, reps: int) -> dict:
    digest, doc = soft_document(case)
    named = {"id": case["id"], "kind": "soft-selected", "soft_document_handle": digest,
             "model": case["model"], "queries": case["queries"]}
    out = {}
    firsts, repeats, fc, rc, last = [], [], [], [], None
    for _ in range(reps):
        svc = Service(exe)
        dt, last = svc.send([named], {digest: doc})
        firsts.append(dt)
        fc.append(svc.last_cpu)
        for _ in range(reps):
            dt, last = svc.send([named])
            repeats.append(dt)
            rc.append(svc.last_cpu)
        svc.close()
    out["handle: first call (registers, fresh process)"] = (median_ms(firsts), median_ms(fc), status(last))
    out["handle: repeat call"] = (median_ms(repeats), median_ms(rc), status(last))
    # A first call on a process that already holds another document (the harness's steady state).
    svc = Service(exe)
    other = dict(case, norms=case["norms"][:-1])
    od, otext = soft_document(other)
    svc.send([dict(named, soft_document_handle=od)], {od: otext})
    dt, last = svc.send([named], {digest: doc})
    out["handle: first call (process holds another document), once"] = (
        round(dt * 1000, 1), round(svc.last_cpu * 1000, 1), status(last))
    one = dict(named, queries=case["queries"][:1])
    times, cpus = [], []
    for _ in range(reps):
        times.append(svc.send([one])[0])
        cpus.append(svc.last_cpu)
    out["handle: repeat call, 1 query"] = (median_ms(times), median_ms(cpus), status(last))
    svc.close()
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--handle", action="store_true")
    ap.add_argument("--exe", default=str(ROOT / "lean/.lake/build/bin/ve_service"))
    args = ap.parse_args()
    case = json.loads(Path(args.case).read_text())
    exe = Path(args.exe)
    svc = Service(exe)
    rows = written_out(svc, case, args.reps)
    svc.close()
    if args.handle:
        rows.update(handle_variants(exe, case, args.reps))
    print(f"| {Path(args.case).name}, median of {args.reps} | wall ms | CPU ms | answer |")
    print("|---|---:|---:|---|")
    for name, (ms, cpu, st) in rows.items():
        print(f"| {name} | {ms} | {cpu} | {st} |")


if __name__ == "__main__":
    main()
