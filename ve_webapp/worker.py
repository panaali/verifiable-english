"""Disposable, time-limited process. All semantic decisions belong to ve."""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import ve
from ve.assist import AssistSession, call_tool
from ve.assist.sources import source_from_text
from .examples import BY_ID


def _reader_world(env, world):
    """A plain-language summary; exact model data remains available to experts."""
    names = {entity: name.replace("_", " ") for name, entity in world["constants"].items()}
    def label(entity):
        return names.get(entity, entity.replace("_", " "))
    lines = []
    for sort, entities in world["domains"].items():
        noun = sort.replace("_", " ")
        if entities:
            lines.append(f"This world has {len(entities)} {noun if len(entities) == 1 else noun + 's'}: " +
                         ", ".join(label(e) for e in entities) + ".")
        else:
            lines.append(f"This world has no {noun}.")
    for predicate, rows in world["relations"].items():
        description = env.predicates[predicate].description.rstrip(".")
        if re.search(r'[@()\[\]*<=>+{}|^\\/-]', description):
            description = predicate.replace("_", " ") + " holds"
        for row in rows:
            subject = label(row[0])
            if len(row) == 1:
                lines.append(f"{subject.capitalize()}: {description}.")
            else:
                lines.append(f"{subject.capitalize()} and {label(row[1])}: {description}.")
        if not rows:
            lines.append(f"There are no true cases of {predicate.replace('_', ' ')}.")
    lines.append("Every relationship not listed here is false in this world.")
    return lines


def _comparison_summary(env, comparison):
    for model in comparison.get("distinguishing_models", []):
        sentences = []
        for truth, atoms in ((True, model.get("true", [])), (False, model.get("false", []))):
            for atom in atoms:
                try:
                    strict = atom
                    for name in sorted(env.constants, key=len, reverse=True):
                        strict = re.sub(r'(?<![@\w])' + re.escape(name) + r'(?!\w)',
                                        '@' + name, strict)
                    formula = ve.parse(env, strict + ".\n").formulas[0]
                    reading = ve.natural_formula(env, formula).sentences[0]
                    if reading["form"] == "natural":
                        sentences.append(("It is true that " if truth else "It is false that ") +
                                         reading["text"].lower() + ".")
                except (ValueError, ve.VEError):
                    pass
        model["reader_summary"] = sentences or ["This checked world makes one reading true and the other false."]


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
            from ve_experiments.claude_cli import Controls, MODELS
            date = datetime.now(timezone.utc).date().isoformat()
            controls = Controls(model=MODELS[config["model"]], cli_version=config["cli_version"],
                thinking_tokens=None, output_tokens=1024, effort=None, timeout_s=40,
                working_directory=str(Path(config["state"]) / "claude-empty" / "cwd"),
                context_date=date)
            proposer = ClaudeProposer(Path(config["state"]) / f"calls-{date}.jsonl", model=config["model"],
                controls=controls, account_config_dir=config["account_config_dir"],
                allow_builtin_agents_md=True)
        session.proposer = proposer
        result = call_tool(session, "propose", {"sentence": session.sentence_order[0], "k": 3})
        # Do not expose backend diagnostics or credentials through HTTP.
        if not result.get("ok"):
            raise ve.VEError("Assistant unavailable. Check the private server calls ledger.")
        for candidate in result["candidates"]:
            formula = session.candidates[candidate["id"]]["formula"]
            candidate["natural"] = ve.natural_formula(env, formula).to_dict()
        for comparison in result["comparisons"]:
            _comparison_summary(env, comparison)
        return result
    text = data.get("text", ex["claim"])
    doc = ve.parse(env, text.rstrip() + "\n")
    views = {v: ve.render(doc, env, view=v) for v in ("ve_strict", "ve_natural", "ve_fluent", "fol_symbols")}
    result = {"views": views, "natural": ve.natural_document(env, doc).to_dict(),
              "meaning_id": ve.meaning_id(env, doc), "status": "parsed"}
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
            result["countermodel_summary"] = _reader_world(env, result["countermodel"])
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
