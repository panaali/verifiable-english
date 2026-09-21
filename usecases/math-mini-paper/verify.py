#!/usr/bin/env python3
"""Re-run every check in the mini-paper from scratch and print the results table.

    UV_CACHE_DIR=/private/tmp/ve-uv-cache-uc uv run python \
        usecases/math-mini-paper/verify.py

Writes, for every theorem, `theorems/<id>/{premises.ve,conclusion.ve,
certificate.json,verdict.json}`; for every hypothesis, a countermodel under
`countermodels/`; and `report.md` + `results.json` beside this script.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from ve import (Document, FiniteModel, check_entailment_certificate,  # noqa: E402
                check_countermodel, find_countermodel, formula_to_data,
                print_document, prove_entailment, render)
from ve.printer import lint_vocabulary  # noqa: E402
from ve.wire import canonical_json  # noqa: E402

from theory import NECESSITY_HINTS, THEOREMS  # noqa: E402

LEAN_EXE = ROOT / "lean/.lake/build/bin/ve_conformance"
MAX_STEPS = 200_000


def ve_text(env, formulas):
    if not formulas:
        return ""
    return print_document(env, Document(tuple(formulas)))


def fluent(env, formulas):
    return [render(f, env, "ve_fluent") for f in formulas]


def staged_countermodel(env, premises, goal, sizes=(0, 1, 2, 3)):
    """Search domain sizes separately so the 10^6-node evaluation cap is per size."""
    last = None
    for size in sizes:
        result = find_countermodel(env, premises, goal, min_domain_size=size,
                                   max_domain_size=size, max_models=400_000,
                                   max_evaluations=1_000_000)
        last = result
        if result.model is not None:
            return result, size
    return last, None


def lean_check(queries):
    """Batch `check-certificate`; returns {id: (valid, note)}."""
    if not queries:
        return {}
    if not LEAN_EXE.exists():
        return {q["id"]: (None, "lean executable not built (run `cd lean && lake build`)")
                for q in queries}
    out = {}
    for start in range(0, len(queries), 20):
        chunk = queries[start:start + 20]
        proc = subprocess.run([str(LEAN_EXE), "check-certificate"],
                              input=json.dumps(chunk), text=True,
                              capture_output=True, timeout=600)
        if proc.returncode not in (0, 1):
            for q in chunk:
                out[q["id"]] = (None, f"lean exit {proc.returncode}: {proc.stderr.strip()[:200]}")
            continue
        try:
            rows = json.loads(proc.stdout)
        except json.JSONDecodeError:
            for q in chunk:
                out[q["id"]] = (None, f"unparsable lean output: {proc.stdout[:200]}")
            continue
        for row in rows:
            out[row["id"]] = (bool(row.get("valid")),
                              row.get("error", "") if row.get("status") != "ok" else "")
    return out


def main():
    results = []
    lean_queries = []

    # The fluent English view is only trustworthy when the vocabulary metadata
    # passes the renderer's own lint; otherwise it silently falls back to the
    # strict symbol names.
    from theory import ENV, ENV_TC
    lint = {name: sorted((i.path, i.code) for i in lint_vocabulary(e))
            for name, e in (("environment.json", ENV), ("environment-closure.json", ENV_TC))}
    (HERE / "vocabulary-lint.json").write_text(json.dumps(lint, indent=2) + "\n")
    print("vocabulary lint:", {k: len(v) for k, v in lint.items()}, flush=True)

    for spec in THEOREMS:
        tid, env = spec["id"], spec["env"]
        labels = [label for label, _ in spec["premises"]]
        premises = [f for _, f in spec["premises"]]
        goal = spec["goal"]
        expect = spec.get("expect", "prove")
        max_steps = spec.get("max_steps", MAX_STEPS)

        out = HERE / "theorems" / tid
        out.mkdir(parents=True, exist_ok=True)
        (out / "premises.ve").write_text(ve_text(env, premises))
        (out / "conclusion.ve").write_text(ve_text(env, [goal]))

        record = {
            "id": tid, "title": spec["title"], "expect": expect,
            "environment": "environment-closure.json" if env.closure else "environment.json",
            "premise_labels": labels,
            "premises_ve": ve_text(env, premises).splitlines(),
            "premises_fluent": fluent(env, premises),
            "conclusion_ve": ve_text(env, [goal]).strip(),
            "conclusion_fluent": render(goal, env, "ve_fluent"),
        }

        # --- prove ----------------------------------------------------------
        t0 = time.perf_counter()
        proof = prove_entailment(env, premises, goal, max_steps=max_steps)
        record["prove_seconds"] = round(time.perf_counter() - t0, 3)
        record["prove_status"] = proof.status
        record["max_steps"] = max_steps
        record["prove_steps"] = proof.steps
        record["prove_detail"] = proof.detail

        if proof.certificate is not None:
            blob = canonical_json(proof.certificate)
            (out / "certificate.json").write_bytes(blob)
            record["certificate_bytes"] = len(blob)
            replay = check_entailment_certificate(env, premises, goal, proof.certificate,
                                                  max_steps=max_steps)
            record["python_valid"] = replay.valid
            record["python_status"] = replay.status
            record["python_detail"] = replay.detail
            lean_queries.append({
                "id": tid, "environment": env.to_dict(),
                "premises": [formula_to_data(env, f) for f in premises],
                "conclusion": formula_to_data(env, goal),
                "certificate": proof.certificate,
            })
        else:
            (out / "certificate.json").write_text("")
            record["certificate_bytes"] = 0
            record["python_valid"] = False
            record["python_status"] = proof.status
            record["python_detail"] = proof.detail

        # --- refutation (for the conjecture, and as a sanity check on failures)
        if expect in ("refuted", "fail"):
            t0 = time.perf_counter()
            cm, size = staged_countermodel(env, premises, goal)
            record["refutation_status"] = cm.status
            record["refutation_domain_size"] = size
            record["refutation_seconds"] = round(time.perf_counter() - t0, 3)
            if cm.model is not None:
                path = HERE / "countermodels" / f"{tid}-refutation.json"
                path.write_text(json.dumps(cm.model.to_dict(), indent=2) + "\n")
                record["refutation_model"] = cm.model.to_dict()
                record["refutation_file"] = path.name
                verified = check_countermodel(env, premises, goal, cm.model)
                record["refutation_recheck_valid"] = verified.valid
            else:
                record["refutation_detail"] = cm.detail

        # --- hypothesis necessity -------------------------------------------
        necessity = []
        for i, label in enumerate(labels if not spec.get("skip_necessity") else []):
            kept = premises[:i] + premises[i + 1:]
            t0 = time.perf_counter()
            hint = NECESSITY_HINTS.get((tid, label))
            if hint is not None:
                model = FiniteModel.from_dict(env, hint)
                check = check_countermodel(env, kept, goal, model)
                entry = {"dropped": label,
                         "status": "Found" if check.valid else "HintRejected",
                         "source": "hand-supplied candidate, re-checked by ve.check_countermodel",
                         "domain_size": len(hint["domains"]["point"]),
                         "seconds": round(time.perf_counter() - t0, 3)}
                cm_model = model if check.valid else None
            else:
                cm, size = staged_countermodel(env, kept, goal)
                entry = {"dropped": label, "status": cm.status, "domain_size": size,
                         "source": "exhaustive search over domains of size 0-3",
                         "seconds": round(time.perf_counter() - t0, 3)}
                cm_model = cm.model
                if cm_model is None:
                    entry["detail"] = cm.detail
            if cm_model is not None:
                name = f"{tid}-without-{label.replace(' ', '-')}.json"
                (HERE / "countermodels" / name).write_text(
                    json.dumps(cm_model.to_dict(), indent=2) + "\n")
                entry["file"] = name
                entry["model"] = cm_model.to_dict()
                entry["recheck_valid"] = check_countermodel(env, kept, goal, cm_model).valid
            necessity.append(entry)
        record["necessity"] = necessity
        results.append(record)
        print(f"  {tid}: prove={record['prove_status']} "
              f"python={record['python_valid']} ({record['prove_seconds']}s)", flush=True)

    # --- Lean ---------------------------------------------------------------
    print("running Lean check-certificate ...", flush=True)
    lean = lean_check(lean_queries)
    for record in results:
        valid, note = lean.get(record["id"], (None, "no certificate to check"))
        record["lean_valid"] = valid
        record["lean_note"] = note

    (HERE / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    for record in results:
        out = HERE / "theorems" / record["id"] / "verdict.json"
        out.write_text(json.dumps({k: v for k, v in record.items()
                                   if k not in ("premises_ve", "premises_fluent")},
                                  indent=2) + "\n")

    table = render_table(results)
    (HERE / "report.md").write_text(table)
    print()
    print(table)
    return 0


def render_table(results):
    def mark(v):
        return {True: "yes", False: "no", None: "n/a"}[v]

    lines = ["# verify.py output", "",
             "| Theorem | Certified (Python) | Certified (Lean) | Hypotheses necessary |"
             " Prove time (s) | Certificate bytes |",
             "|---|---|---|---|---|---|"]
    for r in results:
        nec = r["necessity"]
        if not nec:
            necessary = "n/a" if r.get("premise_labels") else "(none)"
        else:
            ok = sum(1 for e in nec if e["status"] == "Found" and e.get("recheck_valid"))
            necessary = f"{ok}/{len(nec)}"
        lines.append(f"| {r['id']} | {mark(r['python_valid'])} | {mark(r['lean_valid'])} | "
                     f"{necessary} | {r['prove_seconds']} | {r['certificate_bytes']} |")
    py = sum(1 for r in results if r["python_valid"])
    ln = sum(1 for r in results if r["lean_valid"])
    lines += ["", f"Certified by the Python replay checker: {py}/{len(results)}.",
              f"Certified by the Lean `check-certificate` executable: {ln}/{len(results)}.", ""]
    for r in results:
        if not r["python_valid"]:
            lines.append(f"- **{r['id']} not certified**: {r['prove_status']} — {r['prove_detail']}"
                         + (f" Refutation search: {r.get('refutation_status', 'not attempted')}."
                            if r.get("refutation_status") else ""))
    lines.append("")
    for r in results:
        for e in r["necessity"]:
            if not (e["status"] == "Found" and e.get("recheck_valid")):
                lines.append(f"- **{r['id']}** dropping *{e['dropped']}*: no countermodel "
                             f"within the search bound ({e['status']}).")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
