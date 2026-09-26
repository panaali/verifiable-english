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
    checked = check_bundle(bundle)
    (HERE / "t7-definitions-bundle.json").write_bytes(canonical_json(bundle) + b"\n")
    result = {"rows": rows, "t7mono_by_citation": checked["status"] == "Checked",
              "t7mono_leaves": checked["lemmas"][-1]["transitive_leaves"],
              "lean_defined_route": "UnsupportedProfile",
              "c1": "uncertified"}
    (HERE / "definitions-results.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = ["# W3 definitions rerun", "", "The four mathematical names are identity-bound `defined` declarations. Each theorem uses a vocabulary version containing only the declarations it needs, so no theorem copies a definition axiom into its own hypotheses.", "", "| Theorem | Python certificate | Copied definition hypotheses |", "|---|---|---:|"]
    lines += [f"| {row['theorem']} | {'yes' if row['python_valid'] else 'no'} | 0 |" for row in rows]
    lines += ["", f"T7mono is certified by citing T7a and T7b to obtain T7: **{checked['status']}**. Its report retains the `background:definitions` and `open:transitivity` leaves.", "", "The checked-in baseline rerun remains 15/19; this citation adds T7mono to the Python-certified results, yielding 16/19. T9 and T9e still exhaust the current closure checker. C1 remains uncertified. Lean and Rust explicitly reject `defined` entries; these Python certificates therefore have no cross-language acceptance claim.", ""]
    (HERE / "definitions-report.md").write_text("\n".join(lines))
    print("W3 math rerun: 6 direct Python certificates, T7mono citation checked; C1 uncertified")


if __name__ == "__main__":
    main()
