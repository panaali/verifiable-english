"""Step 0 of the answer-store batch: the hit rate of exact request lines between two runs.

Measurement only; it serves nothing and changes no request. Registered for a measurement run by a temporary,
uncommitted line in tests/conftest.py (`pytest_configure`: `config.pluginmanager.register(<this module>)`).

Every request a `LeanService` writes is logged at `_roundtrip`, after `_ensure`, with two keys:

* `k`, the line the client really wrote: SHA-256 of the service binary's actual digest, its start-up limits
  and the request bytes, the nonce masked (a store derives it from the rest of the line);
* `kf`, the same request written self-contained: every environment its cases name registered in the line
  itself (`_request_line(..., environments)` with all of them), so that its answer does not depend on the
  handle table the process happens to hold.

and the SHA-256 of the response line, its nonce masked (for the byte identity of the two runs' answers).
The run's records go to ~/tarch-store-measure/<label>/<worker>.jsonl, label = the marker expression and
worker count; at the end the controller compares them with the last earlier run of the same label and
prints the hit rates.
"""
from __future__ import annotations

import functools
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import time

ROOT_DIR = Path.home() / "tarch-store-measure"
_local = threading.local()
_out = None
_lock = threading.Lock()


def _label(config) -> str:
    marks = config.getoption("markexpr", "") or ""
    workers = config.getoption("numprocesses", None)
    return hashlib.sha1(f"{marks}|{workers}".encode()).hexdigest()[:10]


def pytest_configure(config):
    global _out
    from ve.backends import lean_service as ls
    worker = getattr(config, "workerinput", {}).get("workerid")
    if worker is None:  # the controller makes the run's directory; workers inherit it
        stamp = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
        run = ROOT_DIR / _label(config) / f"{stamp}-{os.getpid()}"
        run.mkdir(parents=True, exist_ok=True)
        (run / "args.json").write_text(json.dumps({"argv": sys.argv, "marks": config.getoption("markexpr", "")}))
        os.environ["VE_STORE_MEASURE_DIR"] = str(run)
        worker = "controller"
    run = Path(os.environ["VE_STORE_MEASURE_DIR"])
    listing = Path(__file__).with_name("dump.txt")
    DUMP = set(listing.read_text().split()) if listing.exists() else set()
    _out = open(run / f"{worker}.jsonl", "a", buffering=1 << 20)
    default = Path(ls.DEFAULT_EXECUTABLE).resolve()
    exchange, roundtrip = ls.LeanService.exchange, ls.LeanService._roundtrip
    ORIGINAL = {name: getattr(ls.LeanService, name) for name in ("_read_line", "_write_all", "_spawn",
                                                                  "_deadline", "_ensure")}
    ORIGINAL["check_response"] = ls.check_response

    @functools.wraps(exchange)
    def exchange_(self, mode, cases_text, count, *, timeout=None, budget=None, texts=None,
                  environments=None, expanded=None):
        _local.call = {"timeout": self.timeout if timeout is None else timeout, "environments": environments,
                       "budget": budget if budget is not None else
                       {"cases": max(count, 1), "bytes": len(cases_text.encode())}}
        return exchange(self, mode, cases_text, count, timeout=timeout, budget=budget, texts=texts,
                        environments=environments, expanded=expanded)

    @functools.wraps(roundtrip)
    def roundtrip_(self, mode, cases_text, count, timeout, nonce, line, texts, expanded=None):
        call = getattr(_local, "call", None) or {}
        environments = call.get("environments") or {}
        needed = [d for d in environments if d not in self._registered]
        new_bytes = sum(len(environments[d].encode()) for d in needed)
        no_reset = (len(self._registered) + len(needed) <= ls.MAX_HANDLES
                    and self._handle_bytes + new_bytes <= ls.MAX_HANDLE_BYTES)
        reasons = []
        if call.get("timeout") is not None:
            reasons.append("timeout")
        if self.executable.resolve() != default:
            reasons.append("executable")
        if self.expected_sha256 is not None:
            reasons.append("expected-hash")
        if self.allow_unlisted_build:
            reasons.append("unlisted")
        try:
            build = self.build
        except OSError:
            build = "?"
        limits = json.dumps([self.address_space, self.max_rss, self.max_requests, self.batch_cases,
                             self.batch_bytes, self.handles])
        prefix = f"{build}\0{limits}\0".encode()
        mask = json.dumps(nonce).encode()
        live_line = line.replace(mask, b'"-"', 1)
        full_line = ls.LeanService._request_line("-", mode, cases_text, call.get("budget") or {}, environments)
        t0 = time.monotonic()
        failed = None
        try:
            raw, response = roundtrip(self, mode, cases_text, count, timeout, nonce, line, texts, expanded)
        except BaseException as exc:
            failed = type(exc).__name__
            raise
        finally:
            seconds = time.monotonic() - t0
            record = {"t": os.environ.get("PYTEST_CURRENT_TEST", "").rsplit(" ", 1)[0], "m": mode,
                      "k": hashlib.sha256(prefix + live_line).hexdigest()[:32],
                      "kf": hashlib.sha256(prefix + full_line).hexdigest()[:32],
                      "s": round(seconds, 6), "n": count, "b": len(line), "sc": len(needed) == len(environments),
                      "nr": no_reset, "h": bool(environments), "el": ",".join(reasons), "pid": self.pid, "reg": len(self._registered)}
            if failed is None:
                record["r"] = hashlib.sha256(raw.replace(nonce.encode(), b"-")).hexdigest()[:32]
                record["err"] = response.get("status") == "error"
                if record["err"]:
                    record["e"] = str(response.get("error"))[:240]
                patched = [name for name in ("_read_line", "_write_all", "_spawn", "_deadline", "_ensure")
                           if getattr(ls.LeanService, name) is not ORIGINAL[name]]
                if patched or ls.check_response is not ORIGINAL["check_response"]:
                    record["p"] = ",".join(patched) or "check_response"
            else:
                record["fail"] = failed
            with _lock:
                _out.write(json.dumps(record, separators=(",", ":")) + "\n")
                if failed is None and DUMP and record["t"].split("::")[0] in DUMP:
                    with open(run / f"dump-{worker}.jsonl", "a") as dump:
                        dump.write(json.dumps({"t": record["t"], "k": record["k"], "line": live_line.decode(),
                                               "raw": raw.replace(nonce.encode(), b"-").decode()}) + "\n")
        return raw, response

    ls.LeanService.exchange = exchange_
    ls.LeanService._roundtrip = roundtrip_


def pytest_unconfigure(config):
    if _out is not None:
        _out.flush()
    if hasattr(config, "workerinput"):
        return
    run = Path(os.environ["VE_STORE_MEASURE_DIR"])
    summary = summarise(run)
    (run / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print("\nstore-measure: " + json.dumps(summary["headline"]) + f" ({run})", file=sys.stderr)


def _records(run: Path):
    for path in sorted(run.glob("*.jsonl")):
        with path.open() as stream:
            for line in stream:
                if line.strip():
                    yield json.loads(line)


def summarise(run: Path, previous: Path | None = None) -> dict:
    """This run's records, and their hit rates against `previous` (default: the latest earlier run of the
    same label that has a summary)."""
    if previous is None:
        earlier = sorted(p for p in run.parent.iterdir() if p.is_dir() and p.name < run.name
                         and (p / "summary.json").exists())
        previous = earlier[-1] if earlier else None
    before_live, before_full = {}, {}
    if previous is not None:
        for r in _records(previous):
            if "r" in r:
                before_live.setdefault(r["k"], r["r"])
                before_full.setdefault(r["kf"], r["r"])
    rows = [r for r in _records(run) if "r" in r]
    eligible = [r for r in rows if not r["el"]]

    def rate(selected, key, before):
        hits = [r for r in selected if r[key] in before]
        seconds = sum(r["s"] for r in selected)
        return {"requests": len(selected), "hits": len(hits),
                "hit_rate": round(len(hits) / len(selected), 4) if selected else None,
                "seconds": round(seconds, 1), "hit_seconds": round(sum(r["s"] for r in hits), 1),
                "hit_seconds_share": round(sum(r["s"] for r in hits) / seconds, 4) if seconds else None,
                "same_response": sum(before[r[key]] == r["r"] for r in hits)}

    headline = {"previous": previous.name if previous else None, "records": len(rows),
                "failed_roundtrips": sum(1 for r in _records(run) if "fail" in r),
                "eligible": len(eligible),
                "exact_line": rate(eligible, "k", before_live) if previous else None,
                "self_contained_line": rate(eligible, "kf", before_full) if previous else None,
                "lines_self_contained": sum(r["sc"] for r in eligible),
                "lines_with_handles": sum(r["h"] for r in eligible),
                "lines_without_reset": sum(r["nr"] for r in eligible)}
    by_file: dict[str, dict] = {}
    for r in eligible:
        f = by_file.setdefault(r["t"].split("::")[0], {"requests": 0, "seconds": 0.0, "hits": 0, "hit_s": 0.0,
                                                       "hits_full": 0, "hit_full_s": 0.0})
        f["requests"] += 1
        f["seconds"] += r["s"]
        if r["k"] in before_live:
            f["hits"] += 1
            f["hit_s"] += r["s"]
        if r["kf"] in before_full:
            f["hits_full"] += 1
            f["hit_full_s"] += r["s"]
    return {"headline": headline, "by_file": dict(sorted(by_file.items(), key=lambda kv: -kv[1]["seconds"]))}
