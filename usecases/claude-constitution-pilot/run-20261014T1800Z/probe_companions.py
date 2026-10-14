#!/usr/bin/env python3
"""Probe (not part of the counted translation): what readings-defaults RD-4b (companion sets, merged at ve-green-arch-AR-6) gives the constitution.

    uv run python usecases/claude-constitution-pilot/run-20261010T1800Z/probe_companions.py

Each of the four "should" reading sets of translation.ve.md is re-written as a companion set: every candidate carries
`companion` = {the main environment without readings@1, the open terms the candidate's content names}. Nothing else changes
(same units, same contents, same situations, same text). The set is then checked by itself as a component and the document's meaning
is the product of its components. Output: probes/companion-probe.json and probes/companion/translation-companions.ve.md.
What it measures: whether `ve document` accepts the companion document, whether its verdicts equal the plain document's, and whether
Lean now reports `decided_units` (the Lean-decided share of tools/lean_decided_share.py).
"""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)
from ve.environment import Environment  # noqa: E402
from ve.norms import NormDocument, norm_meaning_id  # noqa: E402

OUT = RUN / "probes/companion"


def atoms(node, acc):
    if isinstance(node, list):
        if node and node[0] in ("unary", "binary") and isinstance(node[1], str):
            acc.add(node[1])
        for x in node:
            atoms(x, acc)
    return acc


def ve(*args):
    p = subprocess.run([sys.executable, "-m", "ve", *args], cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    meta, source = pilot.read(RUN / "translation.ve.md")
    env = meta["environment"]
    lower = copy.deepcopy(env)
    lower["profiles"] = [p for p in lower["profiles"] if p != "readings@1"]
    terms = {t["name"]: t for t in meta["open_terms"]}
    probe = copy.deepcopy(meta)
    for item in probe["reading_sets"]:
        for r in item["readings"]:
            names = atoms(r["content"]["norm"], set())
            open_terms = [copy.deepcopy(terms[n]) for n in sorted(names) if n in terms]
            r["companion"] = {"environment": lower, "open_terms": open_terms}
            r["meaning_id"] = norm_meaning_id(Environment(lower), NormDocument._decode(r["content"]))
    result = {"sets": [s["id"] for s in probe["reading_sets"]], "attempts": {}}
    # attempt 1: as the plain document is (each set carries `source_word`, the span of its “should”, used by the English of E22/E23)
    # attempt 2: the same without `source_word`
    for name, strip in (("with_source_word", False), ("without_source_word", True)):
        doc = copy.deepcopy(probe)
        if strip:
            for item in doc["reading_sets"]:
                item.pop("source_word", None)
        path = OUT / f"translation-companions-{name}.ve.md"
        pilot.write(path, doc, source)
        rel = str(path.relative_to(ROOT))
        att = {"document": rel}
        for kind in ("check", "coverage"):
            code, out, err = ve("document", kind, rel)
            att[kind] = {"returncode": code}
            if code == 0:
                att[kind]["json"] = json.loads(out)
            else:
                att[kind]["stdout_error"] = (json.loads(out).get("error") if out.strip().startswith("{") else out.strip()[-600:])
                att[kind]["stderr"] = err.strip()[-600:]
        chk = att["check"].get("json")
        if chk:
            rd = chk["readings"]
            att["summary"] = {
                "route": rd["route"], "components": [(c["component"], c["route"], c["units"]) for c in rd["components"]],
                "conflict": rd["status"], "premises": chk["premises"]["status"],
                "premises_components": [(c["component"], c["status"]) for c in chk["premises"].get("components", [])],
                "separations": rd["separations"], "decided_units": rd.get("decided_units"),
                "english": rd["english"]}
            (OUT / "answer.json").write_text(json.dumps({"decided_units": rd.get("decided_units")}) + "\n")
            p = subprocess.run([sys.executable, "tools/lean_decided_share.py", rel, "--answer", str(OUT / "answer.json")],
                               cwd=ROOT, capture_output=True, text=True)
            att["lean_decided_share"] = json.loads(p.stdout) if p.returncode == 0 else {"error": p.stderr.strip()}
        result["attempts"][name] = att
    (RUN / "probes/companion-probe.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    for name, att in result["attempts"].items():
        print(name, {k: (v["returncode"], v.get("stdout_error")) for k, v in att.items() if k in ("check", "coverage")})
        print(json.dumps({k: v for k, v in att.items() if k not in ("check", "coverage")}, indent=1, ensure_ascii=False)[:4000])


if __name__ == "__main__":
    main()
