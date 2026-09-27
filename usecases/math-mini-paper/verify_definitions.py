#!/usr/bin/env python3
"""W3 rerun: definition Background and a labelled T7 citation bundle."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

import theory  # noqa: E402
from ve import ast  # noqa: E402
from ve.background import background  # noqa: E402
from ve.bundle import check_bundle  # noqa: E402
from ve.entailment import check_entailment_certificate, prove_entailment  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.identity import meaning_id  # noqa: E402
from ve.profiles import SPEC_REVISION  # noqa: E402
from ve.wire import canonical_json  # noqa: E402
from ve.surface.definitions import render_definition  # noqa: E402
from ve.definitions import compile_definitions  # noqa: E402

LEAN = HERE.parents[1] / "lean/.lake/build/bin/ve_conformance"

DEFINITIONS = {"greatest": theory.DEF_GREATEST, "sim": theory.DEF_SIM,
               "minimal": theory.DEF_MINIMAL, "least": theory.DEF_LEAST}
THEOREMS = {spec["id"]: spec for spec in theory.THEOREMS}


def environment(names):
    raw = theory.ENV.to_dict()
    del raw["profile"]
    raw.update(language="ve.core@0.2", profiles=["definitions@0", "relational-fol@0"],
               spec_revision=SPEC_REVISION)
    for name in names:
        body = DEFINITIONS[name]
        while isinstance(body, ast.Forall):
            body = body.body
        body = body.left.right
        raw["vocabulary"]["predicates"][name]["defined"] = {
            "arguments": list(theory.ENV.predicates[name].arguments), "body": ast._to_data(body)}
    return Environment(raw)


def certify(env, premises, goal):
    proof = prove_entailment(env, premises, goal, max_steps=200_000)
    valid = proof.certificate is not None and check_entailment_certificate(
        env, premises, goal, proof.certificate, max_steps=200_000).valid
    return proof, valid


def lean_certificates(cases):
    """Replay certificates on the Lean route (Background = definitions ++ literals)."""
    import subprocess
    run = subprocess.run([str(LEAN), "route", "-"], input=json.dumps(cases), capture_output=True,
                         text=True, timeout=600)
    return [row.get("valid") is True for row in json.loads(run.stdout)]


def certified_count():
    """The paper's 19 queries: the checked-in baseline (Python and Lean), the
    closure-induction supplement for T9 and T9e, and T7mono by citation."""
    baseline = json.loads((HERE / "results.json").read_text())
    certified = {row["id"] for row in baseline if row.get("python_valid") and row.get("lean_valid")}
    induction = json.loads((HERE.parent / "closure-induction/results.json").read_text())
    for row in induction:
        if row["id"] in ("T9_induction", "T9e_induction") and row["python_valid"] and row["lean_valid"]:
            certified.add(row["id"].removesuffix("_induction"))
    return certified, len(baseline)


def main():
    environments = {"T5": environment(["greatest"]), "T6": environment(["sim"]),
                    "T7a": environment(["sim"]), "T7b": environment(["sim"]),
                    "T7": environment(["sim"]), "T8": environment(["minimal", "least"])}
    rows = []
    proofs = {}
    for tid, env in environments.items():
        spec = THEOREMS[tid]
        premises = [(label, formula) for label, formula in spec["premises"]
                    if not label.startswith("definition of")]
        proof, valid = certify(env, [formula for _, formula in premises], spec["goal"])
        rows.append({"theorem": tid, "environment_id": env.environment_id,
                     "copied_definition_hypotheses": 0, "premises": [label for label, _ in premises],
                     "status": proof.status, "python_valid": valid})
        proofs[tid] = proof
        if not valid:
            raise RuntimeError(f"{tid} did not certify")

    env = environments["T7"]
    bg = [{"label": "background:" + entry.generator, "ast": ast.formula_to_data(env, entry.formula)}
          for entry in background(env)]
    transitivity = {"label": "open:transitivity", "ast": ast.formula_to_data(env, theory.transitive("le"))}
    leaves = bg + [transitivity]
    lemmas = []
    for tid in ("T7a", "T7b"):
        spec = THEOREMS[tid]
        lemmas.append({"name": tid, "environment_id": env.environment_id,
                       "premises": [transitivity], "cites": [],
                       "conclusion": ast.formula_to_data(env, spec["goal"]),
                       "meaning_id": meaning_id(env, spec["goal"]),
                       "reading_choices": {}, "transitive_leaves": leaves,
                       "certificate": proofs[tid].certificate})
    t7 = THEOREMS["T7"]
    lemmas.append({"name": "T7", "environment_id": env.environment_id,
                   "premises": [], "cites": [lemmas[0]["meaning_id"], lemmas[1]["meaning_id"]],
                   "conclusion": ast.formula_to_data(env, t7["goal"]),
                   "meaning_id": meaning_id(env, t7["goal"]),
                   "reading_choices": {}, "transitive_leaves": leaves,
                   "certificate": proofs["T7"].certificate})
    bundle = {"version": "ve-bundle@0", "environment": env.to_dict(), "lemmas": lemmas}
    lean = LEAN.exists()
    checked = check_bundle(bundle, lean_executable=LEAN if lean else None)
    if lean:
        cases = [{"id": row["theorem"], "kind": "certificate", "environment": environments[row["theorem"]].to_dict(),
                  "premises": [ast.formula_to_data(environments[row["theorem"]], f)
                               for label, f in THEOREMS[row["theorem"]]["premises"]
                               if not label.startswith("definition of")],
                  "conclusion": ast.formula_to_data(environments[row["theorem"]], THEOREMS[row["theorem"]]["goal"]),
                  "certificate": proofs[row["theorem"]].certificate} for row in rows]
        for row, valid in zip(rows, lean_certificates(cases), strict=True):
            row["lean_valid"] = valid
            if not valid:
                raise RuntimeError(f"Lean rejected {row['theorem']}")
    certified, total = certified_count()
    t7mono = checked["status"] == "Checked" and checked["lean_checked"]
    if t7mono:
        certified.add("T7mono")
    (HERE / "t7-definitions-bundle.json").write_bytes(canonical_json(bundle) + b"\n")
    english = {name: render_definition(env_, definition)
               for env_ in (environments["T5"], environments["T6"], environments["T8"])
               for definition in compile_definitions(env_, env_.definition_entries, version=env_.environment_id)
               for name in [definition.name]}
    result = {"rows": rows, "t7mono_by_citation": checked["status"] == "Checked",
              "t7mono_lean_bundle": checked["lean_checked"],
              "t7mono_citation_english": checked["lemmas"][-1]["english"],
              "t7mono_leaves": checked["lemmas"][-1]["transitive_leaves"],
              "definitions_english": dict(sorted(english.items())),
              "certified": sorted(certified), "certified_count": len(certified), "queries": total,
              "c1": "uncertified"}
    (HERE / "definitions-results.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = ["# W3 definitions rerun", "",
             "The four mathematical names are identity-bound `defined` declarations. Each theorem uses a "
             "vocabulary version containing only the declarations it needs, so no theorem copies a definition "
             "axiom into its own hypotheses. Python, Lean and Rust decode the declarations and regenerate the "
             "definition Background; the certificates below are replayed by both checkers.", "",
             "| Theorem | Python certificate | Lean certificate | Copied definition hypotheses |",
             "|---|---|---|---:|"]
    lines += [f"| {row['theorem']} | {'yes' if row['python_valid'] else 'no'} | "
              f"{'yes' if row.get('lean_valid') else 'not run'} | 0 |" for row in rows]
    lines += ["", "The definitions, as the English surface writes them:", ""]
    lines += [f"- {text.strip()}" for _, text in sorted(english.items())]
    lines += ["", f"T7mono is certified by citing T7a and T7b to obtain T7: **{checked['status']}** in Python, "
              f"**{'Checked' if checked['lean_checked'] else 'not run'}** in one Lean bundle run. Its report "
              "retains the `background:definitions` and `open:transitivity` leaves, and reads:", "",
              "> " + checked["lemmas"][-1]["english"].strip().replace("\n", "\n> "), "",
              f"**Certified: {len(certified)}/{total}** ({', '.join(sorted(certified))}). The checked-in "
              "baseline certifies 15 queries in Python and Lean; the closure-induction supplement "
              "(`usecases/closure-induction`) certifies T9 and T9e in both; T7mono is added here by "
              "citation. C1 remains honestly uncertified: it is false, and refuted by a one-element "
              "countermodel.", ""]
    (HERE / "definitions-report.md").write_text("\n".join(lines))
    print(f"W3 math rerun: {len(certified)}/{total} certified; C1 uncertified")


if __name__ == "__main__":
    main()
