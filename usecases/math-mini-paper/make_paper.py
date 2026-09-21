#!/usr/bin/env python3
"""Expand `paper.template.md` into `paper.md` using only machine-produced text.

Every VE statement, English rendering, countermodel and table cell in the paper
is copied out of `results.json`, which `verify.py` writes.  Prose is the only
hand-written part.  Run `verify.py` first.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = {r["id"]: r for r in json.loads((HERE / "results.json").read_text())}


def fence(lines, lang="text"):
    body = "\n".join(lines)
    return f"```{lang}\n{body}\n```"


def statement(tid):
    r = RESULTS[tid]
    out = []
    if r["premise_labels"]:
        out.append("*Hypotheses (VE, strict canonical text).*")
        out.append(fence(r["premises_ve"]))
    else:
        out.append("*Hypotheses.* None; this is a logical validity of the VE profile.")
    out.append("*Conclusion (VE, strict canonical text).*")
    out.append(fence([r["conclusion_ve"]]))
    out.append("*English rendering (`python -m ve render --view ve_fluent`).*")
    bullets = []
    for label, text in zip(r["premise_labels"], r["premises_fluent"]):
        bullets.append(f"- **{label}:** {text}")
    bullets.append(f"- **conclusion:** {r['conclusion_fluent']}")
    out.append("\n".join(bullets))
    return "\n\n".join(out)


def verdict(tid):
    r = RESULTS[tid]
    mark = {True: "yes", False: "no", None: "n/a"}
    bits = [f"prover: `{r['prove_status']}` in {r['prove_seconds']} s "
            f"({r['prove_steps']} steps, budget {r['max_steps']})",
            f"certificate: {r['certificate_bytes']} bytes",
            f"Python replay: {mark[r['python_valid']]}",
            f"Lean `check-certificate`: {mark[r['lean_valid']]}"]
    line = " | ".join(bits)
    if r["prove_detail"]:
        line += f"\n\nProver detail: `{r['prove_detail']}`."
    return line


def necessity(tid):
    r = RESULTS[tid]
    if not r["necessity"]:
        return "_No hypotheses; nothing to drop._"
    rows = ["| Hypothesis dropped | Countermodel found | Domain size | Re-checked | File |",
            "|---|---|---|---|---|"]
    for e in r["necessity"]:
        rows.append(f"| {e['dropped']} | {e['status']} | {e.get('domain_size', '-')} | "
                    f"{e.get('recheck_valid')} | `countermodels/{e.get('file', '-')}` |")
    return "\n".join(rows)


def countermodel(spec):
    tid, label = spec.split(":", 1)
    r = RESULTS[tid]
    if label == "refutation":
        model = r.get("refutation_model")
    else:
        model = next((e.get("model") for e in r["necessity"] if e["dropped"] == label), None)
    if model is None:
        return "_(no countermodel recorded)_"
    return fence(json.dumps(model, indent=2).splitlines(), "json")


def table(_arg=""):
    rows = ["| Theorem | Certified (Python) | Certified (Lean) | Hypotheses necessary |"
            " Prove time (s) | Certificate bytes |", "|---|---|---|---|---|---|"]
    mark = {True: "yes", False: "**no**", None: "n/a"}
    for r in RESULTS.values():
        nec = r["necessity"]
        if not nec:
            cell = "n/a" if r["premise_labels"] else "(no hypotheses)"
        else:
            ok = sum(1 for e in nec if e["status"] == "Found" and e.get("recheck_valid"))
            cell = f"{ok}/{len(nec)}"
        rows.append(f"| {r['id']} | {mark[r['python_valid']]} | {mark[r['lean_valid']]} | "
                    f"{cell} | {r['prove_seconds']} | {r['certificate_bytes']} |")
    py = sum(1 for r in RESULTS.values() if r["python_valid"])
    ln = sum(1 for r in RESULTS.values() if r["lean_valid"])
    rows.append("")
    rows.append(f"Totals: **{py}/{len(RESULTS)}** certificates accepted by the Python replay "
                f"checker, **{ln}/{len(RESULTS)}** accepted by the Lean "
                f"`ve_conformance check-certificate` executable.")
    return "\n".join(rows)


def totals(key):
    nec_total = sum(len(r["necessity"]) for r in RESULTS.values())
    nec_ok = sum(1 for r in RESULTS.values() for e in r["necessity"]
                 if e["status"] == "Found" and e.get("recheck_valid"))
    models = nec_ok + sum(1 for r in RESULTS.values() if r.get("refutation_model"))
    values = {"nec": f"{nec_ok} of {nec_total}", "nec_ok": str(nec_ok),
              "models": str(models), "queries": str(len(RESULTS)),
              "python": str(sum(1 for r in RESULTS.values() if r["python_valid"])),
              "lean": str(sum(1 for r in RESULTS.values() if r["lean_valid"]))}
    return values[key]


HANDLERS = {"TOTALS": totals, "STATEMENT": statement, "VERDICT": verdict, "NECESSITY": necessity,
            "COUNTERMODEL": countermodel, "TABLE": table}


def main():
    template = (HERE / "paper.template.md").read_text()

    def expand(match):
        kind, arg = match.group(1), match.group(2) or ""
        return HANDLERS[kind](arg)

    text = re.sub(r"\{\{([A-Z]+)(?::([^}]*))?\}\}", expand, template)
    (HERE / "paper.md").write_text(text)
    print(f"wrote paper.md ({len(text)} bytes)")


if __name__ == "__main__":
    main()
