"""Disposable, time-limited process. All semantic decisions belong to ve."""
import json
import sys
from pathlib import Path
import ve
from ve.assist import AssistSession, call_tool
from ve.assist.sources import source_from_text
from .examples import BY_ID


def run(action, data, config=None, proposer=None):
    ex = BY_ID[data["example"]]
    env = ve.Environment(data.get("environment") or ex["environment"])
    if action == "propose":
        source = source_from_text(data["text"])
        session = AssistSession.create(env, source, [{"id": "target", "sentence": source["sentences"][0]["id"]}],
            options={"propose_repair_rounds": 0, "max_proof_steps": 500, "max_models": 100,
                     "max_evaluations": 5000})
        if len(session.sentence_order) != 1:
            raise ve.VEError("Select one sentence at a time for assistance.")
        if proposer is None:
            from ve_experiments.assist_haiku import ClaudeProposer
            proposer = ClaudeProposer(Path(config["state"]) / "calls.jsonl", model=config["model"],
                timeout_s=40, output_tokens=1024, working_directory=str(Path(config["state"]) / ("empty-" + session.session_id)))
        session.proposer = proposer
        result = call_tool(session, "propose", {"sentence": session.sentence_order[0], "k": 3})
        # Do not expose backend diagnostics or credentials through HTTP.
        if not result.get("ok"):
            raise ve.VEError("Assistant unavailable. Check the private server calls ledger.")
        return result
    text = data.get("text", ex["claim"])
    doc = ve.parse(env, text.rstrip() + "\n")
    views = {v: ve.render(doc, env, view=v) for v in ("ve_strict", "ve_natural", "ve_fluent", "fol_symbols")}
    result = {"views": views, "meaning_id": ve.meaning_id(env, doc), "status": "parsed"}
    if action == "validate":
        return result
    if len(doc.formulas) != 1:
        raise ve.VEError("Check exactly one conclusion at a time.")
    claim = doc.formulas[0]
    premises = ve.parse(env, data.get("premises", ex["premises"]).rstrip() + "\n").formulas
    proof = ve.prove_entailment(env, premises, claim, max_steps=2000)
    if proof.certificate:
        replay = ve.check_entailment_certificate(env, premises, claim, proof.certificate, max_steps=2000)
        if replay.valid:
            result.update(status="certified", certificate=proof.certificate, replay=replay.to_dict())
    if result["status"] != "certified":
        search = ve.find_countermodel(env, premises, claim, max_domain_size=2, max_models=2000, max_evaluations=30000)
        result.update(status="unknown", detail="No proof or countermodel found within the search budget.")
        if search.model and ve.check_countermodel(env, premises, claim, search.model).valid:
            result.update(status="countermodel", countermodel=search.model.to_dict(),
                          detail="Every assumption is true in this world; the conclusion is false.")
    if "world" in data or "environment" not in data:
        world = ve.FiniteModel.from_dict(env, data.get("world", ex["world"]))
        result["evaluation"] = ve.evaluate(env, doc, world, max_evaluations=10000).to_dict()
    result["assurance"] = "Experimental Python certificate replay; not a Lean runtime check. Premises and fidelity to English require human review."
    return result


if __name__ == "__main__":
    try:
        payload = json.load(sys.stdin)
        output = run(**payload)
    except ve.VEError as exc:
        output = {"error": exc.to_dict()}
    except Exception:
        output = {"error": {"message": "The operation could not complete within the supported limits."}}
    print(json.dumps(output))
