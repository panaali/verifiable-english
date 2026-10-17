#!/usr/bin/env python3
"""Run 20261016T1800Z (rerun in 20261017T0600Z and 20261017T1800Z): can the three 'should' sets be stated natively on the soft chain (rd-9: `soft-norms@0` beside `norm-defaults@0`)?

The defeasible candidate of each set becomes a default rule with an unstated exception (`mode: default`, `exception: {decided_by: unstated}`, `unless: []`), so the three
invented exception_to_* open terms are dropped. Everything else is `readings/nd-all.ve.md`. The situations are searched again (meaning and situation ids depend on the
environment, which now lists soft-norms@0). The probe records what VE does with that document; the translation itself is NOT changed by it (the plan's rule: keep a repair
only if `ve document check` passes). Writes readings/soft-chain.ve.md and evidence/soft-chain-probe.json.

    uv run python usecases/claude-constitution-pilot/run-20261017T1800Z/probe_soft_chain.py
"""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))
_spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pilot)
import nd  # noqa: E402
from ve.document import _environment, load_document  # noqa: E402
from ve.errors import VEError  # noqa: E402
from ve.readings import s1_content_meaning_id  # noqa: E402

DOC = RUN / "readings/soft-chain.ve.md"


def soft_default(content):
    out = copy.deepcopy(content)
    n = out["norm"]
    n["unless"] = []
    n["mode"] = "default"
    n["exception"] = {"decided_by": "unstated", "sufficient": [], "necessary": [], "factors": []}
    return out


def ve(*args):
    proc = subprocess.run([sys.executable, "-m", "ve", *args], cwd=ROOT, capture_output=True, text=True)
    return proc


def main():
    meta, source = pilot.read(RUN / "readings/nd-all.ve.md")
    meta = copy.deepcopy(meta)
    env_data = meta["environment"]
    before_terms = len(meta["open_terms"])
    env_data["profiles"] = sorted({*env_data["profiles"], "soft-norms@0"})
    for name, *_ in nd.EXCEPTIONS.values():
        env_data["vocabulary"]["predicates"].pop(name)
        meta["open_terms"] = [t for t in meta["open_terms"] if t["name"] != name]
        for unit in pilot._flat(meta["units"]):   # run 20261017T0600Z: the units' `meaning` listed the exception term (nd.py); the soft form has none
            if isinstance(unit.get("meaning"), dict) and name in unit["meaning"].get("open", []):
                rest = [x for x in unit["meaning"]["open"] if x != name]
                unit["meaning"] = {"open": rest} if rest else "specified"
    env = _environment(env_data)
    for item in meta["reading_sets"]:
        for r in item["readings"]:
            if item["id"] in nd.FORCE and r["id"] in ("default", "default-in-frame"):   # run 20261017T1800Z: u0156.s03 has two default candidates
                r["content"] = soft_default(r["content"])
            if r.get("content") is not None:
                r["meaning_id"] = s1_content_meaning_id(env, item["id"], r)
        item.pop("situations", None)
        for r in item["readings"]:
            r["admission"]["distinguishing_models"] = {o["id"]: "pending" for o in item["readings"] if o["id"] != r["id"]}
    t = time.monotonic()
    meta, missing, limits = nd.find_situations(meta)
    search = round(time.monotonic() - t, 1)
    pilot.write(DOC, meta, source)
    rel = str(DOC.relative_to(ROOT))
    out = {"document": rel, "profiles": meta["environment"]["profiles"], "open_terms_before": before_terms, "open_terms_after": len(meta["open_terms"]),
           "exception_terms_dropped": [n for n, *_ in nd.EXCEPTIONS.values()], "situation_search_seconds": search, "pairs_without_situation": missing, "search_limits": limits}
    try:
        load_document(DOC)
        out["load"] = "admitted"
    except VEError as exc:
        out["load"] = "refused: " + getattr(exc, "message", str(exc))
    t = time.monotonic()
    proc = ve("document", "check", rel)
    out["check"] = {"returncode": proc.returncode, "seconds": round(time.monotonic() - t, 1), "stdout_head": proc.stdout[:300],
                    "stderr_last_lines": proc.stderr.strip().splitlines()[-12:]}
    cov = ve("document", "coverage", rel)
    out["coverage"] = {"returncode": cov.returncode}
    if cov.returncode == 0:
        d = json.loads(cov.stdout)
        out["coverage"].update({"coverage_percent": d["coverage_percent"], "bytes_by_status": d["bytes_by_status"], "residual": d["residual"]})
    ren = ve("document", "render", rel)
    out["render"] = {"returncode": ren.returncode, "lines": len(ren.stdout.splitlines())}
    out["conclusions"] = {}
    for name, q in (("denial", "probes/nd/conclusion-no-denial.json"), ("claim_human", "probes/nd/conclusion-no-claim-human.json")):
        t = time.monotonic()
        r = ve("document", "readings", rel, "--conclusion", str((RUN / q).relative_to(ROOT)))
        row = {"returncode": r.returncode, "seconds": round(time.monotonic() - t, 1)}
        if r.returncode == 0:
            d = json.loads(r.stdout)
            row.update({k: d.get(k) for k in ("verdict", "route", "evidence")})
            row["choices"] = len(d.get("proofs") or d.get("choices") or [])
        else:
            row["stderr_last_lines"] = r.stderr.strip().splitlines()[-6:]
        out["conclusions"][name] = row
    (RUN / "evidence").mkdir(exist_ok=True)
    (RUN / "evidence/soft-chain-probe.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(out, indent=1, ensure_ascii=False)[:5000])


if __name__ == "__main__":
    main()
