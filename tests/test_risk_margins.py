"""risk.md 8.3: margins against brute force on 200 random records.

For every endpoint of every cited estimate, every grid value in a window on
each side is decided by the route itself on the perturbed record (hashes and
citations recomputed): invalid with its diagnostic, a CONFLICT, or the
statuses. The route's certified scans must agree: the nearest status change
per alternative is the first value that is valid, conflict-free and changes
that alternative's status; `record_invalid` is the first invalid value with
its diagnostic; `record_conflict` the first conflict; and a scan that finds
nothing (or finds a value beyond the window) has no brute-force value in the
window. Review B8.
"""
from __future__ import annotations

import json
import random
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path

import pytest

from conformance.risk import Log, cell_env, condition, estimate, record, statement
from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "lean/.lake/build/bin/ve_risk_route"
pytestmark = pytest.mark.skipif(not BIN.exists(), reason="ve_risk_route is not built")

D = "dimensionless"
RECORDS = 200
SHARDS = 8
WINDOW = 5

RULES = [
    {"norm": {"name": "x1", "predicate": "permitted", "sign": False,
              "guard": ["binary", "risk__might_lead_to", ["var", 0], ["const", "server_outage"]], "unless": [], "over": []}},
    {"norm": {"name": "x2", "predicate": "permitted", "sign": True,
              "guard": ["binary", "risk__might_lead_to", ["var", 0], ["const", "job_failure"]], "unless": [], "over": []}},
    {"norm": {"name": "x3", "predicate": "permitted", "sign": False,
              "guard": ["binary", "leads_to", ["var", 0], ["const", "task_delay"]], "unless": [], "over": ["x2"]}},
]
CELLS = ("server_outage", "job_failure", "task_delay")


def route(cases):
    out = subprocess.run([str(BIN), "-"], input=json.dumps(cases), text=True, capture_output=True, timeout=HANG_TIMEOUT)
    return json.loads(out.stdout)


def comparison(rng, name):
    op = rng.choice(("lt", "le", "eq"))
    tree = [op, ["quantity", name], ["decimal", D, str(rng.randrange(0, 9))]]
    if rng.randrange(2):
        tree = [op, ["decimal", D, str(rng.randrange(0, 9))], ["quantity", name]]
    return ["not", tree] if rng.randrange(4) == 0 else tree


def draw(rng):
    """A random record: estimates of q and r, and one to three conditions on act's cells."""
    estimates = {}
    for name in ("q", "r"):
        lo = rng.randrange(0, 7)
        estimates[name] = (lo, lo + rng.randrange(0, 4))
    conditions = []
    for harm in rng.sample(CELLS, rng.randrange(1, 4)):
        names = rng.sample(("q", "r"), rng.randrange(1, 3))
        tree = comparison(rng, names[0])
        if len(names) == 2:
            tree = [rng.choice(("and", "or")), tree, comparison(rng, names[1])]
        conditions.append((harm, rng.choice(("necessary", "necessary", "sufficient", "exact")), tree))
    return estimates, conditions


def build(policy, estimates, conditions):
    log = Log()
    log.add(1, "Eq", "estimate", estimate("q", *map(str, estimates["q"]), "est", "assumption"))
    log.add(2, "Er", "estimate", estimate("r", *map(str, estimates["r"]), "est", "assumption"))
    for i, (harm, form, tree) in enumerate(conditions, start=3):
        log.add(i, f"C{i}", "condition", condition("act", harm, form, tree))
    # nothing is ruled out of every harm except a job failure, so X1 and X3 never fire on it
    log.add(10, "T", "statement", statement("nothing", "server_outage", "cannot"))
    log.add(11, "T2", "statement", statement("nothing", "task_delay", "cannot"))
    ids = [e["id"] for e in log.entries]
    alternatives = [{"name": "act", "label": "acting"},
                    {"name": "nothing", "label": "doing nothing", "inaction": True}]
    quantities = [{"name": n, "label": n, "tag": D} for n in ("q", "r")]
    dx = log.add(20, "DX", "decision", record("x", "the_agent", "the agent", policy, alternatives, quantities,
                                              log.cite(*ids)))
    return {"id": "d", "kind": "risk-decision", "environment": cell_env(), "document": {"norms": RULES},
            "decision": dx, "entries": log.entries[:-1]}


def outcome(res):
    if res["status"] == "error":
        return ("invalid", re.sub(r", case \(.*\)$", "", res["error"]))
    if res.get("verdict") == "CONFLICT":
        return ("conflict",)
    return ("ok", {s["alternative"]: (s["permitted"], s["required"], s["clear"]) for s in res["statuses"]})


def first(values, test):
    return next((x for x in values if test(x)), None)


@pytest.mark.parametrize("shard", range(SHARDS))
def test_margins_agree_with_brute_force(shard):
    env = cell_env()
    elaborated = route([{"id": "p", "kind": "risk-elaborate", "environment": env, "document": {"norms": RULES}}])[0]
    policy = (elaborated["environment_id"], elaborated["document_hash"])
    rng = random.Random(9000 + shard)
    records = []
    while len(records) < RECORDS // SHARDS:
        estimates, conditions = draw(rng)
        res = route([build(policy, estimates, conditions)])[0]
        if res["status"] == "ok" and res.get("verdict") != "CONFLICT":
            records.append((estimates, conditions, res))
    probes, keys = [], []
    for index, (estimates, conditions, _) in enumerate(records):
        for name, eid in (("q", "Eq"), ("r", "Er")):
            for side in ("lo", "hi"):
                current = estimates[name][0 if side == "lo" else 1]
                for x in range(current - WINDOW, current + WINDOW + 1):
                    if x == current:
                        continue
                    moved = deepcopy(estimates)
                    moved[name] = (x, moved[name][1]) if side == "lo" else (moved[name][0], x)
                    probes.append(build(policy, moved, conditions))
                    keys.append((index, eid, side, x))
    chunks = [probes[i::2] for i in range(2)]
    with ThreadPoolExecutor(2) as pool:
        answers = list(pool.map(route, chunks))
    brute = {}
    for i in range(2):
        for key, res in zip(keys[i::2], answers[i]):
            brute[key] = outcome(res)
    checked = 0
    found = {"invalid": 0, "conflict": 0, "change": 0}
    for index, (estimates, _, res) in enumerate(records):
        base = outcome(res)[1]
        invalid = {(r["estimate"], r["side"], r["direction"]): (r["value"], r["diagnostic"]) for r in res["record_invalid"]}
        conflict = {(r["estimate"], r["side"], r["direction"]): r["value"] for r in res["record_conflict"]}
        nearest = {(m["estimate"], m["side"], m["alternative"], m["direction"]): m.get("nearest") for m in res["margins"]}
        for name, eid in (("q", "Eq"), ("r", "Er")):
            for side in ("lo", "hi"):
                current = estimates[name][0 if side == "lo" else 1]
                for direction, values in (("down", range(current - 1, current - WINDOW - 1, -1)),
                                          ("up", range(current + 1, current + WINDOW + 1))):
                    seen = {x: brute[(index, eid, side, x)] for x in values}
                    window = set(values)

                    def agree(scan, found):
                        # the scan's value is certified nearest over all grid values: inside the window it is
                        # the brute-force first; beyond it (or none) the window has no brute-force value
                        if scan is not None and int(scan) in window:
                            return found is not None and int(scan) == found
                        return found is None

                    x_invalid = first(values, lambda x: seen[x][0] == "invalid")
                    found["invalid"] += x_invalid is not None
                    scan = invalid.get((eid, side, direction))
                    assert agree(scan and scan[0], x_invalid), (estimates, eid, side, direction, scan, seen)
                    if x_invalid is not None and scan is not None:
                        assert scan[1] == seen[x_invalid][1], (scan, seen[x_invalid])
                    x_conflict = first(values, lambda x: seen[x][0] == "conflict")
                    found["conflict"] += x_conflict is not None
                    assert agree(conflict.get((eid, side, direction)), x_conflict), (
                        estimates, eid, side, direction, conflict, seen)
                    for alternative in ("act", "nothing"):
                        x_change = first(values, lambda x: seen[x][0] == "ok"
                                         and seen[x][1][alternative] != base[alternative])
                        found["change"] += x_change is not None
                        assert agree(nearest[(eid, side, alternative, direction)], x_change), (
                            estimates, eid, side, alternative, direction, nearest, seen)
                        checked += 1
    assert checked == len(records) * 16
    # the windows hold every kind: status changes, invalid values and conflicts
    assert all(n > 0 for n in found.values()), found
