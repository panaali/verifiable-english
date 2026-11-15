"""translim-predicates PART 1b: the cost of each request kind that reads the regulated list, at N regulated predicates.

Run from the checkout root: `uv run python docs/translim/translim-predicates/cost_curve.py --sizes 32 64 [--out f.json]`
(`VE_LEAN_SERVICE=<binary>` picks the service; a binary with a raised limit times N > 64). Each (N, shape, kind) runs
`--runs` times on a fresh service: wall seconds of the request, the service's CPU seconds for it (`/proc`), and the CPU
deadline the client gives that request (`lean_service.deadline`). Nothing here is a test; the numbers go in REPORT.md.

Environments: the RSP frame (usecases/anthropic-rsp/environment.d1.json without its regulated predicates: 3 sorts, 55
predicates) plus N generated regulated predicates over `situation`, obligations paired with their permissions, each
with a legend and one rule. Shape `flat`: each rule's guard is one RSP frame predicate. Shape `cone`: rule i's guard
reads regulated predicate i-1, so the last rule's guard cone holds every regulated predicate (the worst case).
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tests.test_acts_readings_lean import frame  # noqa: E402
from ve.backends import lean_service, relay  # noqa: E402

RSP = ROOT / "usecases/anthropic-rsp/environment.d1.json"
FRAME_GUARDS = ["publicly_deployed", "internally_deployed", "risk_report_approved", "rsp_updated"]
DECIDER = {"decided_by": "assistant", "sufficient": [], "necessary": [], "factors": []}
LETTERS = "abcdefghijklmnopqrstuvwxyz"
# A binary with a test-only raised limit is not in lean/checkers.lock: `--unlisted` admits it for timing only.
UNLISTED = False


def names(n):
    return [f"g{LETTERS[i // 26]}{LETTERS[i % 26]}" for i in range((n + 1) // 2)]


def environment(n, profiles, default="deny", joined=False):
    """The RSP frame plus `n` regulated predicates (n/2 obligation and permission pairs)."""
    env = json.loads(RSP.read_text())
    preds = {k: v for k, v in env["vocabulary"]["predicates"].items() if "regulated" not in v}
    env["vocabulary"]["predicates"] = preds
    env["profiles"] = sorted(profiles)
    if joined:
        env["vocabulary"]["acts"] = {"fixed": ["asylum or refuge"], "adverbs": [],
                                     "frames": [frame(f"seek{n}") for n in names(n)] + [frame("hold")]}
    for i, name in enumerate(names(n)):
        act = f"{{0}} to seek{name} asylum or refuge" if joined else f"{{0}} do {name}"
        if 2 * i + 1 < n:
            preds[f"{name}_required"] = {"arguments": ["situation"], "description": f"{{0}} must do {name}",
                                         "regulated": {"role": "obligation", "default": default, "act": act,
                                                       "permission": f"{name}_permitted"}}
        preds[f"{name}_permitted"] = {"arguments": ["situation"], "description": f"{{0}} may do {name}",
                                      "regulated": {"role": "permission", "default": default, "act": act}}
    regulated = [k for k, v in preds.items() if "regulated" in v]
    assert len(regulated) == n, (len(regulated), n)
    return env, regulated


def rules(regulated, shape, soft=False):
    out = []
    for i, p in enumerate(regulated):
        if shape == "cone" and i > 0:
            guard = ["unary", regulated[i - 1], ["var", 0]]
        else:
            guard = ["unary", FRAME_GUARDS[i % len(FRAME_GUARDS)], ["var", 0]]
        norm = {"name": f"r{i}", "predicate": p, "sign": p.endswith("_required"), "guard": guard, "unless": [],
                "over": []}
        if soft:
            norm |= {"mode": "default", "exception": dict(DECIDER)}
        out.append({"norm": norm})
    return out


NORMS = ["norms@0", "relational-fol@0"]
SOFT = NORMS + ["soft-norms@0"]
DEFAULTS = NORMS + ["norm-defaults@0"]


def cases(n, shape):
    """(label, mode, case) for every request kind timed."""
    env, reg = environment(n, NORMS)
    senv, _ = environment(n, SOFT)
    denv, _ = environment(n, DEFAULTS, default="unspecified")
    jenv, _ = environment(n, NORMS + ["acts@0"], joined=True)
    out = [("norms-elaborate", "norms", {"kind": "norms-elaborate", "environment": env, "norms": rules(reg, shape)}),
           ("norms-conflict", "norms", {"kind": "norms-conflict", "environment": env, "norms": rules(reg, shape),
                                        "packages": {}}),
           ("soft-rules", "soft-norms", {"kind": "soft-rules", "environment": senv,
                                         "norms": rules(reg, shape, soft=True)}),
           ("soft-elaborate", "soft-norms", {"kind": "soft-elaborate", "environment": senv,
                                             "norms": rules(reg, shape, soft=True)}),
           ("norm-defaults-elaborate", "norm-defaults", {"kind": "norm-defaults-elaborate", "environment": denv,
                                                         "norms": rules(reg, shape)}),
           ("acts-parse (joined, acts@0)", "norms", {"kind": "norms-elaborate", "environment": jenv,
                                                    "norms": rules(reg, shape)})]
    return out, senv, reg


def timed(mode, case, executable):
    text = json.dumps([{"id": "c", **case}], separators=(",", ":"))
    with lean_service.LeanService(executable, allow_unlisted_build=UNLISTED) as service:
        service.start()
        cpu0, t0 = service.cpu_seconds(), time.perf_counter()
        try:
            _, response = service.exchange(mode, text, 1)
        except lean_service.CheckerUnavailable as error:  # past the deadline: the client stops the service
            wall = time.perf_counter() - t0
            return wall, None, lean_service.deadline(mode, len(text.encode()), 1), f"DEADLINE: {error}"[:60]
        wall, cpu = time.perf_counter() - t0, service.cpu_seconds() - cpu0
    row = response["results"][0]["result"]
    status = row.get("error") or row.get("status") or row.get("verdict") or "ok"
    return wall, cpu, lean_service.deadline(mode, len(text.encode()), 1), str(status)[:60]


def document_check(senv, reg, shape, executable):
    """The whole `ve check` path on a soft document of one norm unit per regulated predicate (wall, all child CPU)."""
    from tests.test_document import unit, write_doc
    from ve.document import check_document
    with tempfile.TemporaryDirectory() as tmp:
        text, units = b"", []
        for i, r in enumerate(rules(reg, shape, soft=True)):
            line = f"Rule {i} applies.\n".encode()
            units.append(unit(f"u{i}", len(text), len(text) + len(line), "norm", "specified", r))
            text += line
        path = write_doc(Path(tmp), text, units, environment_json=senv)
        pool = lean_service.LeanServicePool(size=1, executable=executable, allow_unlisted_build=UNLISTED)
        relay._pool = pool
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        t0 = time.perf_counter()
        try:
            report = check_document(path)
            status = report.get("premises", {}).get("status", "ok")
        except Exception as error:  # a refusal is a measured answer too
            status = f"{type(error).__name__}: {error}"
        wall = time.perf_counter() - t0
        pool.close()
        relay._pool = None
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)
    return wall, cpu, lean_service.DEADLINES["document"][0], str(status)[:60]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", type=int, nargs="+", default=[32, 64])
    parser.add_argument("--shapes", nargs="+", default=["flat", "cone"])
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--kinds", nargs="+", help="only the kinds whose label starts with one of these")
    parser.add_argument("--unlisted", action="store_true", help="time a binary not in lean/checkers.lock")
    parser.add_argument("--out")
    args = parser.parse_args()
    global UNLISTED
    UNLISTED = args.unlisted
    executable = Path(os.environ.get("VE_LEAN_SERVICE") or lean_service.DEFAULT_EXECUTABLE)
    if UNLISTED:  # the document path starts its own services: a temporary lock that also lists this binary
        lock = json.loads(lean_service.build_lock().read_text())
        lock["ve_service"] = sorted(set(lock["ve_service"]) | {lean_service.executable_sha256(executable)})
        handle = tempfile.NamedTemporaryFile("w", suffix=".lock", delete=False)
        handle.write(json.dumps(lock))
        handle.close()
        lean_service.BUILD_LOCK = Path(handle.name)
    rows = []
    for n in args.sizes:
        for shape in args.shapes:
            kinds, senv, reg = cases(n, shape)
            for label, mode, case in kinds:
                if args.kinds and not any(label.startswith(k) for k in args.kinds):
                    continue
                runs = [timed(mode, case, executable) for _ in range(args.runs)]
                rows.append({"n": n, "shape": shape, "kind": label, "mode": mode, "wall": [r[0] for r in runs],
                             "cpu": [r[1] for r in runs], "deadline_cpu": runs[0][2], "answer": runs[0][3]})
                print(json.dumps(rows[-1]), flush=True)
            if args.kinds and "document" not in args.kinds:
                continue
            runs = [document_check(senv, reg, shape, executable) for _ in range(args.runs)]
            rows.append({"n": n, "shape": shape, "kind": "document check", "mode": "document",
                         "wall": [r[0] for r in runs], "cpu": [r[1] for r in runs], "deadline_cpu": runs[0][2],
                         "answer": runs[0][3]})
            print(json.dumps(rows[-1]), flush=True)
    if args.out:
        Path(args.out).write_text(json.dumps({"executable": str(executable), "rows": rows}, indent=1) + "\n")


if __name__ == "__main__":
    main()
