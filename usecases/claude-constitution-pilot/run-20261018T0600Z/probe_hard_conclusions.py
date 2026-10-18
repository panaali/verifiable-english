#!/usr/bin/env python3
"""Run 20261015T0600Z (AT-0p guards; u0165.s03 with one pair of attitude terms per candidate; first written in 20261014T1800Z): conclusion queries on the seven hard-constraint rules, superposed route (u0165.s03 is a reading set of two candidates).

For each constraint, over every instance of Claude and every situation, `ve document readings translation.ve.md --conclusion`:
  * knowing:  the case holds and this instance of Claude knowingly and intentionally engages in it (first alternative)  -> not permitted
  * belief:   this instance of Claude thinks it quite likely that the action falls into the category (second alternative) -> not permitted
  * neither:  the guard does not hold: neither alternative (an unclear, uncertain or unknowing case)  -> not permitted  (NOT meant to be entailed)
  c = var 1 (the instance), s = var 0 (the situation). For u0165.s03 the case is "a cyberweapon that could cause significant damage", a case under both readings.
Writes probes/nd/hard/<unit>-<kind>.json (the query) and <unit>-<kind>-result.json (VE's answer), and probes/hard-conclusions-probe.json.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(RUN))
import s03_scope as sc  # noqa: E402
import spec_nd  # noqa: E402

OUT = RUN / "probes/nd/hard"
WORKERS = 3  # independent queries, one `ve document readings` process each


def ask(unit, kind, pred, premise, doc, capped=False):
    """capped: DRI 2026-10-14 15:30Z (3): only under `prlimit --as=6442450944` (6 GB address space) may VE_RUST_TIMEOUT be raised (to at most 600 s);
    the peak resident set of the child is read from /usr/bin/time -v and recorded."""
    query = ["forall", "claude_instance", ["forall", "situation",
             ["implies", premise, ["not", ["binary", pred, ["var", 1], ["var", 0]]]]]]
    qpath = OUT / f"{unit}-{kind}.json"
    qpath.write_text(json.dumps(query) + "\n")
    cmd = [sys.executable, "-m", "ve", "document", "readings", doc, "--conclusion", str(qpath.relative_to(ROOT))]
    env = None
    if capped:
        cmd = ["prlimit", "--as=6442450944", "/usr/bin/time", "-v", *cmd]
        env = {**os.environ, "VE_RUST_TIMEOUT": "600"}
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=env)
    (OUT / f"{unit}-{kind}-result.json").write_text(proc.stdout)
    row = {"unit": unit, "kind": kind, "predicate": pred, "returncode": proc.returncode}
    if capped:
        m = re.search(r"Maximum resident set size \(kbytes\): (\d+)", proc.stderr)
        row.update({"cap": "prlimit --as=6442450944 (6 GB address space), VE_RUST_TIMEOUT=600",
                    "peak_resident_set_kb": int(m.group(1)) if m else None})
    try:
        d = json.loads(proc.stdout)
        row.update({k: d.get(k) for k in ("verdict", "route", "evidence", "english")})
    except ValueError:
        row["stderr"] = proc.stderr[-400:]
    print(unit, kind, row.get("verdict"), row.get("route"), row.get("evidence"), flush=True)
    return row


def rerun():
    """Rerun, one at a time, the rows without a verdict (CheckerUnavailable: the Rust checker's default 5 s limit under load; never a verdict).
    First at the default limit; a row that is still unavailable is rerun under the 6 GB cap with the raised limit."""
    path = RUN / "probes/hard-conclusions-probe.json"
    summary = json.loads(path.read_text())
    doc = summary["document"]
    doc = str((RUN / doc).relative_to(ROOT))
    jobs = {(u, k): (p, prem) for u, k, p, prem in _jobs()}
    for i, row in enumerate(summary["queries"]):
        if row.get("verdict") is not None:
            continue
        pred, prem = jobs[(row["unit"], row["kind"])]
        new = ask(row["unit"], row["kind"], pred, prem, doc)
        note = "first run (3 queries in parallel on a loaded machine) was CheckerUnavailable: the Rust checker's default 5 s limit; this row is a single re-run at the default limit"
        if new.get("verdict") is None:
            new = ask(row["unit"], row["kind"], pred, prem, doc, capped=True)
            note = "the default-limit re-run was also CheckerUnavailable; this row is a single re-run under the cap in `cap`"
        new["rerun_alone"] = note
        summary["queries"][i] = new
        path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")


def _premises(unit, term, n):
    """(predicate-independent) premises of one rule's three queries. c = var 1 (the instance), s = var 0 (the situation).
    u0165.s03 has one pair of attitude terms per candidate (run 20261015T0600Z); its case is "a cyberweapon that could cause significant damage", a case under
    both candidates, and its premises name both candidates' terms, so that each candidate's rule fires."""
    def at(name):
        return ["binary", name, ["var", 1], ["var", 0]]
    if unit == sc.UNIT:
        case = ["and", ["unary", sc.CYBERWEAPON, ["var", 0]], ["unary", sc.DAMAGE, ["var", 0]]]
        knowing = ["and", case, ["and", at(sc.KNOWING["wide"]), at(sc.KNOWING["narrow"])]]
        belief = ["and", at(sc.THINKING["wide"]), at(sc.THINKING["narrow"])]
        guards = [sc.guard(r) for r in sc.READINGS]
        neither = ["and", ["not", guards[0]], ["not", guards[1]]]
    else:
        case = ["unary", term, ["var", 0]]
        x, b = at(f"knowingly_engages_{n}"), at(f"thinks_quite_likely_{n}")
        knowing, belief, neither = ["and", case, x], b, ["not", ["or", ["and", case, x], b]]
    return {"knowing": knowing, "belief": belief, "neither": neither}


def _jobs():
    for n, (unit, _rule, pred, term, _act, _words) in enumerate(spec_nd.HARD, 1):
        for kind, premise in _premises(unit, term, n).items():
            yield unit, kind, pred, premise


def only(units):
    """Ask again, one query at a time, every query of the given units on the document as it is now (default limit first, then the 6 GB cap if that is
    CheckerUnavailable). Used after an edit of a predicate's description text that changes no logic (run 20261014T1800Z, u0165.s03)."""
    path = RUN / "probes/hard-conclusions-probe.json"
    summary = json.loads(path.read_text())
    doc = str((RUN / summary["document"]).relative_to(ROOT))
    jobs = {(u, k): (p, prem) for u, k, p, prem in _jobs()}
    for i, row in enumerate(summary["queries"]):
        if row["unit"] not in units:
            continue
        pred, prem = jobs[(row["unit"], row["kind"])]
        new = ask(row["unit"], row["kind"], pred, prem, doc)
        note = "re-asked alone on the final document after an edit of a predicate description (no logic changed), at the default limit"
        if new.get("verdict") is None:
            new = ask(row["unit"], row["kind"], pred, prem, doc, capped=True)
            note = "re-asked alone on the final document after an edit of a predicate description (no logic changed); the default limit gave CheckerUnavailable, so under the cap in `cap`"
        new["rerun_alone"] = note
        new["asked_on_final_document"] = True
        summary["queries"][i] = new
        path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "only":
        return only(sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] == "rerun":
        return rerun()
    OUT.mkdir(parents=True, exist_ok=True)
    doc = str((RUN / "translation.ve.md").relative_to(ROOT))
    jobs = [(unit, kind, pred, premise) for unit, kind, pred, premise in _jobs()]
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        rows = list(pool.map(lambda j: ask(*j, doc), jobs))  # map keeps the job order
    summary = {"document": "translation.ve.md", "queries": rows}
    (RUN / "probes/hard-conclusions-probe.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
