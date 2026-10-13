"""ET-1: run the component through the alternatives route and record every answer (plan 5, ET-1, steps 1-3).

Step 1: `check_document` on a document whose profile list is alternatives@0, documents@1, norms@0,
relational-fol@0 (two units of the component). Steps 2-3: the route's own cases: alt-elaborate, alt-conflict with
conflict packages, alt-followable with a followability package (P3, and its control without the first premise),
alt-certificate for u0171.s03 (P4), alt-validate on P4's scenario. Certificates are searched by `prove_entailment`
(untrusted) and replayed by Lean, as in `tests/test_alternatives_three_way.py`.

Usage: python3 et1_run.py <pilots-dir> <out-dir>
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import et1_component as C  # noqa: E402

from conformance.alternatives import base_environment  # noqa: E402
from ve.alternatives import run_case  # noqa: E402
from ve.ast import Not, _Decoder, formula_from_data  # noqa: E402
from ve.document import check_document  # noqa: E402
from ve.entailment import _binding, prove_entailment  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.norms import _bind  # noqa: E402
from ve.wire import digest  # noqa: E402

MAX_STEPS = 20000


def document_hash(source):
    env = Environment(source["environment"])
    return digest(f"ve-alternatives-{env.identity_version}\n", {
        "environment_id": env.environment_id, "norms": source["norms"], "units": source["units"]})


def conflict_packages(source, elaborated):
    env = Environment(source["environment"])
    base = Environment(base_environment(source["environment"]))
    packages, proofs = {}, {}
    for target in elaborated["conflict_targets"]:
        conclusion = _bind(Not(_Decoder().decode(target["ast"])), target["sorts"])
        proof = prove_entailment(base, (), conclusion, max_steps=MAX_STEPS)
        proofs[target["target"]] = proof.status
        if proof.status == "Found":
            packages[target["target"]] = {"environment_id": env.environment_id,
                                          "document_hash": document_hash(source),
                                          "target": target["target"], "certificate": proof.certificate}
    return packages, proofs


def followable_package(source, elaborated):
    base = Environment(base_environment(source["environment"]))
    premises = [formula_from_data(base, x["ast"]) for x in elaborated["alternatives"] + elaborated["base_premises"]]
    conclusion = formula_from_data(base, elaborated["followable"]["ast"])
    proof = prove_entailment(base, premises, conclusion, max_steps=MAX_STEPS)
    if proof.status != "Found":
        return None, proof.status
    return ({"environment_id": Environment(source["environment"]).environment_id,
             "document_hash": document_hash(source), "target": "followable",
             "certificate": proof.certificate}, proof.status)


def entailment(source, elaborated, conclusion_data):
    """u0171.s03. The certificate binds the regenerated background and layers, as Lean's replay does. Python's
    prover refuses an alternatives@0 environment (no Python producer of alt-certificate exists), so the untrusted
    search runs over the same vocabulary without the alternatives block, and its trace is bound to the component's
    environment with the product's own `_binding`; Lean then binds and replays it (a stale or wrong binding is
    refused there)."""
    raw = source["environment"]
    env = Environment(raw)
    search_raw = {k: v for k, v in raw.items() if k != "alternatives"} | {
        "profiles": [p for p in raw["profiles"] if p != "alternatives@0"]}
    search_env = Environment(search_raw)
    # Lean binds `backgroundAlt A ++ elaborate D.T` (`replayAltEntailment`): the generated background, the slot
    # premises (`altPremises`), then the layer premises.
    bound = ([x["ast"] for x in elaborated["background"]] + [x["ast"] for x in elaborated["alternatives"]] +
             [x["ast"] for x in elaborated["premises"]])
    try:
        proof = prove_entailment(search_env, [formula_from_data(search_env, a) for a in bound],
                                 formula_from_data(search_env, conclusion_data), max_steps=MAX_STEPS,
                                 _background=False)
    except Exception as exc:  # the producer's failure is recorded, Lean is not asked
        return {"producer": f"{type(exc).__name__}: {exc}"[:400]}
    if proof.status != "Found":
        return {"producer": proof.status}
    premises = tuple(formula_from_data(env, a) for a in bound)
    certificate = {**_binding(env, premises, formula_from_data(env, conclusion_data),
                              generated_premises=[False] * len(premises)),
                   "trace": proof.certificate["trace"]}
    row = run_case(source | {"kind": "alt-certificate", "premises": [], "conclusion": conclusion_data,
                             "certificate": certificate})
    # The same certificate against a changed conclusion must not be accepted (binding check).
    changed = ["forall", "response", ["implies", ["unary", "inaction", ["var", 0]],
                                      ["not", ["unary", "permitted", ["var", 0]]]]]
    stale = run_case(source | {"kind": "alt-certificate", "premises": [], "conclusion": changed,
                               "certificate": certificate})
    return {"producer": proof.status, "lean": row, "same_certificate_other_conclusion": stale}


def step1(pilots, out):
    """A two-unit document on the four-profile list: one hard constraint and the first premise."""
    src = (Path(pilots) / "claude-constitution/source/claude-constitution.md").read_bytes()
    ledger = {u["id"]: u for u in json.loads((Path(pilots) / "claude-constitution/run-20261012T1800Z/units.json")
                                             .read_text())}
    pieces = [src[slice(*ledger[i]["span"])] for i in ("u0165.s01", "u0172.s02")]
    body = b"".join(pieces)
    a = len(pieces[0])
    units = [{"id": "u0165.s01", "span": [0, a], "kind": "norm", "support": "assumption",
              "meaning": {"open": ["mass_casualty_weapon_uplift", C.KNOWING]}, "content": C.norms()[0]},
             {"id": "u0172.s02", "span": [a, len(body)], "kind": "asserted", "support": "testimony",
              "meaning": "specified", "content": {"ast": C.AVAILABLE_INACTION["ast"]}}]
    opens = [{"name": n, "arguments": ["response"], "decided_by": "unresolved_decider", "necessary": [],
              "sufficient": [], "factors": [], "precedents": [], "jurisdiction": "claude_constitution",
              "version": 1} for n in ("mass_casualty_weapon_uplift", C.KNOWING)]
    meta = {"format": "ve-document@1", "environment": C.environment(documents=True), "open_terms": opens,
            "units": units}
    path = Path(out) / "step1.ve.md"
    path.write_bytes(b"---\n" + json.dumps(meta).encode() + b"\n---\n" + body)
    try:
        rep = check_document(path)
        return {"accepted": True, "premises": rep.get("premises"), "coverage": rep["coverage"]["bytes_by_status"],
                "admission": (rep.get("admission") or {}).get("admitted")}
    except Exception as exc:
        return {"accepted": False, "error": f"{type(exc).__name__}: {exc}"[:600]}


def main(pilots, out):
    out = Path(out)
    results = {"step1": step1(pilots, out)}
    print("step1", json.dumps(results["step1"])[:400], flush=True)

    source = C.source()
    elaborated = run_case(source | {"kind": "alt-elaborate"})
    results["elaborate"] = {k: elaborated[k] for k in ("status", "fragment", "order", "legend",
                                                       "unmapped_obligations")}
    results["elaborate"]["slot_premises"] = [x["label"] for x in elaborated["alternatives"]]
    results["elaborate"]["conflict_targets"] = [t["target"] for t in elaborated["conflict_targets"]]
    packages, proofs = conflict_packages(source, elaborated)
    results["conflict_proofs"] = proofs
    results["conflict"] = run_case(source | {"kind": "alt-conflict", "packages": packages})
    print("conflict", results["conflict"].get("verdict"), flush=True)

    package, status = followable_package(source, elaborated)
    results["followable_producer"] = status
    results["followable"] = run_case(source | {"kind": "alt-followable", "packages": packages,
                                               **({"package": package} if package else {})})
    print("followable", results["followable"].get("verdict"), results["followable"].get("conditional_on"),
          flush=True)

    # P3's control: without the first premise (refusal available at every decision).
    control = C.source(units=(C.INACTION_COMPATIBLE,))
    c_elab = run_case(control | {"kind": "alt-elaborate"})
    c_packages, _ = conflict_packages(control, c_elab)
    c_package, c_status = followable_package(control, c_elab)
    results["control_without_first_premise"] = {
        "producer": c_status,
        "answer": run_case(control | {"kind": "alt-followable", "packages": c_packages,
                                      **({"package": c_package} if c_package else {})})}
    print("control", c_status, results["control_without_first_premise"]["answer"].get("verdict"), flush=True)

    # A second control (not in the plan's fixtures): without the compatibility premise.
    control2 = C.source(units=(C.AVAILABLE_INACTION,))
    c2_elab = run_case(control2 | {"kind": "alt-elaborate"})
    c2_packages, _ = conflict_packages(control2, c2_elab)
    c2_package, c2_status = followable_package(control2, c2_elab)
    results["control_without_second_premise"] = {
        "producer": c2_status,
        "answer": run_case(control2 | {"kind": "alt-followable", "packages": c2_packages,
                                       **({"package": c2_package} if c2_package else {})})}
    print("control2", c2_status, results["control_without_second_premise"]["answer"].get("verdict"), flush=True)

    results["u0171_s03"] = entailment(source, elaborated, C.U0171_S03)
    print("u0171.s03", json.dumps(results["u0171_s03"])[:300], flush=True)

    results["scenario"] = run_case(source | {"kind": "alt-validate", "scenario": C.scenario(),
                                             "packages": packages})
    print("scenario", json.dumps(results["scenario"])[:600], flush=True)
    (out / "results.json").write_text(json.dumps(results, indent=1) + "\n")
    (out / "component.json").write_text(json.dumps(source | {"scenario": C.scenario()}, indent=1) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:])
