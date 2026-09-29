"""Reading-set structure and conservative checking plans.

Only same-background assertion readings may use the disjunction shortcut.
Every other kind requires complete choice enumeration or stays UNKNOWN.
"""
from __future__ import annotations

from itertools import product

from .assurance import semantic_entry
from .admission import _check_kind, token
from .ast import formula_from_data
from .errors import UnsupportedProfile, VEError
from .identity import meaning_id


def validate_reading_sets(env, values, unit_ids):
    if type(values) is not list:
        raise VEError("reading_sets must be a list")
    seen = set()
    owners = {}
    units = {}
    for item in values:
        required = {"id", "unit", "version", "status", "readings"}
        if type(item) is not dict or not required <= set(item) or set(item) - required - {"signature", "rejected_history", "models"}:
            raise VEError("invalid reading set")
        key = (item["id"], item["version"])
        if not token(item["id"]) or type(item["version"]) is not int or item["version"] < 1 or key in seen:
            raise VEError("invalid or duplicate reading set version")
        seen.add(key)
        if item["unit"] not in unit_ids or item["status"] not in ("authored", "open"):
            raise VEError("invalid reading set unit or status")
        if (item["id"] in owners and owners[item["id"]] != item["unit"]
                or item["unit"] in units and units[item["unit"]] != item["id"]):
            raise VEError("one reading set per source unit; versions must keep their unit")
        owners[item["id"]] = item["unit"]
        units[item["unit"]] = item["id"]
        readings = item["readings"]
        if type(readings) is not list or not 1 <= len(readings) <= 64:
            raise VEError("reading sets hold 1 to 64 readings")
        if item["status"] == "authored" and (len(readings) != 1 or not token(item.get("signature"))):
            raise VEError("authored reading needs one signed choice")
        if item["status"] == "open" and "signature" in item:
            raise VEError("open reading set cannot have an author signature")
        ids = set()
        model_ids = set()
        for reading in readings:
            if type(reading) is not dict or set(reading) != {"id", "kind", "meaning_id", "content", "admission"}:
                raise VEError("invalid reading")
            if not token(reading["id"]) or reading["id"] in ids:
                raise VEError("duplicate or invalid reading id")
            ids.add(reading["id"])
            _check_kind(reading["kind"])
            if not token(reading["meaning_id"]):
                raise VEError("invalid reading meaning id")
            if reading["content"] is not None:
                if env.unit_schema is not None:
                    from .units import quantity_meaning_id
                    content_id = quantity_meaning_id(env, reading["content"])
                else:
                    content_id = meaning_id(env, formula_from_data(env, reading["content"]))
                if content_id != reading["meaning_id"]:
                    raise VEError("reading meaning id does not match content")
            admission = reading["admission"]
            if (type(admission) is not dict or set(admission) != {"who", "why", "distinguishing_models"}
                    or not token(admission["who"]) or type(admission["why"]) is not str
                    or not admission["why"] or type(admission["distinguishing_models"]) is not dict):
                raise VEError("invalid reading admission")
            if set(admission["distinguishing_models"]) != set(r["id"] for r in readings) - {reading["id"]}:
                raise VEError("each other reading needs a distinguishing model id")
            if not all(token(v) for v in admission["distinguishing_models"].values()):
                raise VEError("invalid distinguishing model id")
            model_ids.update(admission["distinguishing_models"].values())
        models = item.get("models", {})
        if type(models) is not dict or set(models) != model_ids:
            raise VEError("distinguishing models must be supplied by id")
        if model_ids:
            from .evaluate import evaluate
            from .model import FiniteModel
            # Quantity readings are evaluated through their regenerated cores
            # on the erased target; tables are never read with tags dropped first.
            model_env, formula_of = _reading_evaluation(env)
            for name, data in models.items():
                model = FiniteModel.from_dict(model_env, data)
                if name != model.model_id:
                    raise VEError("distinguishing model id does not match model")
            for reading in readings:
                for other_id, model_id in reading["admission"]["distinguishing_models"].items():
                    other = next(r for r in readings if r["id"] == other_id)
                    if reading["content"] is None or other["content"] is None:
                        continue  # other-kind elaboration is pending; the checking route reports UNKNOWN
                    model = FiniteModel.from_dict(model_env, models[model_id])
                    a = evaluate(model_env, formula_of(reading["content"]), model, trace=False)
                    b = evaluate(model_env, formula_of(other["content"]), model, trace=False)
                    if a.value is None or b.value is None or a.value == b.value:
                        raise VEError("distinguishing model does not separate readings")
        if "rejected_history" in item and type(item["rejected_history"]) is not list:
            raise VEError("invalid rejected reading history")
    return seen


def _reading_evaluation(env):
    if env.unit_schema is None:
        return env, lambda content: formula_from_data(env, content)
    from .units import core_formula, erased_environment
    return erased_environment(env), lambda content: core_formula(env, content)[1]


def active_reading_sets(sets):
    """Only the latest version of each source unit contributes premises."""
    latest = {}
    for reading_set in sets:
        unit = reading_set["unit"]
        if unit not in latest or reading_set["version"] > latest[unit]["version"]:
            latest[unit] = reading_set
    return [r for r in sets if latest[r["unit"]] is r]


def validate_narrowings(values, reading_sets, unit_ids):
    if type(values) is not list:
        raise VEError("narrowings must be a list")
    ids = set()
    for item in values:
        if type(item) is not dict or set(item) != {"id", "set", "version", "keeps", "by", "reason_spans"}:
            raise VEError("invalid narrowing")
        if not token(item["id"]) or item["id"] in ids or not token(item["by"]):
            raise VEError("invalid narrowing id or author")
        ids.add(item["id"])
        ref = (item["set"], item["version"])
        if ref not in {(r["id"], r["version"]) for r in reading_sets}:
            raise VEError("narrowing cites unknown reading set version")
        rs = next(r for r in reading_sets if (r["id"], r["version"]) == ref)
        choices = {r["id"] for r in rs["readings"]}
        if (type(item["keeps"]) is not list or not item["keeps"]
                or not all(type(x) is str for x in item["keeps"]) or not set(item["keeps"]) <= choices):
            raise VEError("narrowing must keep named readings")
        if (type(item["reason_spans"]) is not list or not item["reason_spans"]
                or not all(type(x) is str for x in item["reason_spans"])
                or not set(item["reason_spans"]) <= unit_ids):
            raise VEError("narrowing needs cited source units")
    return ids


def plan_choices(sets, *, limit=64):
    """Return a sound checking route; no verdict is inferred by this planner."""
    if not sets:
        return {"route": "single", "choices": [{}]}
    if all(all(r["kind"] == "asserted" and r["content"] is not None for r in s["readings"])
           for s in sets):
        return {"route": "assertion-disjunction", "choices": None,
                "all": "one proof from per-unit disjunctions",
                "none": "one shared finite model satisfying every reading"}
    count = 1
    for s in sets:
        count *= len(s["readings"])
        if count > limit:
            return {"route": "UNKNOWN", "budget": {"max_choices": limit}, "choice_count": count}
    return {"route": "enumerate", "choices": [dict(zip((s["id"] for s in sets), c))
             for c in product(*(range(len(s["readings"])) for s in sets))]}


def _lean_readings_scope(env) -> bool:
    """Whether Lean's `readings` mode checks verdicts over `env`: a ve.core@0.2
    FOL-family environment without statement layers."""
    return (getattr(env, "language", None) == "ve.core@0.2" and not env.closure and not env.order
            and env.unit_schema is None and env.alternatives is None
            and not {"soft-norms@0", "reports@0"} & set(env.profiles))


@semantic_entry("readings")
def check_readings(env, sets, conclusion_ast, *, max_steps=10_000, max_domain_size=2,
                   max_models=10_000, max_evaluations=100_000, fixed=()):
    """Checked ALL/SOME/NONE for assertion sets; otherwise honest UNKNOWN.

    Every positive proof is replayed by the certificate checker, and every
    negative claim has an independently checked finite model. Failure of
    bounded search means UNKNOWN. We never infer NONE from proof failure.
    Under a backend authority the replays and model checks run on the backend
    and Lean's `readings` mode must confirm an ALL, NONE or SOME verdict from
    its evidence (`lean/VE/Service/Readings.lean`).
    """
    from .backends.dispatch import authority_for, execute
    options = {"max_steps": max_steps, "max_domain_size": max_domain_size, "max_models": max_models,
               "max_evaluations": max_evaluations, "fixed": fixed}

    def python():
        return _check_readings_python(env, sets, conclusion_ast, **options)

    if authority_for("readings") in ("python", "rust-experimental") or not _lean_readings_scope(env):
        return python()
    return execute("readings", {"kind": "readings"}, python,
                   lean=lambda: _check_readings_lean(env, sets, conclusion_ast, options))


def _check_readings_lean(env, sets, conclusion_ast, options):
    from .backends.dispatch import pinned
    from .backends.lean_runner import run
    from .errors import CheckerUnavailable
    evidence = {}
    with pinned("lean"):
        result = _check_readings_python(env, sets, conclusion_ast, evidence=evidence, **options)
    verdict = result["verdict"]
    if verdict not in ("ALL", "NONE", "SOME"):
        return result  # UNKNOWN asserts nothing
    case = {"id": "readings", "environment": env.to_dict(), "fixed": list(options["fixed"]),
            "sets": [[r["content"] for r in s["readings"]] for s in sets],
            "conclusion": conclusion_ast, "verdict": verdict, "evidence": evidence}
    try:
        row = run("readings", [case])[0]
    except VEError as exc:
        # Lean refusing evidence whose parts it checked one by one is a
        # disagreement, never an input rejection.
        raise CheckerUnavailable("CheckerUnavailable: Lean does not confirm the readings verdict: "
                                 + exc.message) from None
    if row["verdict"] != verdict:
        raise CheckerUnavailable("CheckerUnavailable: Lean does not confirm the readings verdict")
    return result


def _check_readings_python(env, sets, conclusion_ast, *, max_steps=10_000, max_domain_size=2,
                           max_models=10_000, max_evaluations=100_000, fixed=(), evidence=None):
    """`evidence`, when given, receives the verdict's evidence on the wire."""
    from .ast import Or
    from .entailment import check_entailment_certificate, prove_entailment
    from .search import check_countermodel, find_countermodel
    from .vacuity import premise_status

    plan = plan_choices(sets)
    if plan["route"] == "UNKNOWN":
        return {"verdict": "UNKNOWN", "route": plan["route"], "budget": plan["budget"]}
    if plan["route"] == "enumerate":
        return {"verdict": "UNKNOWN", "route": "enumerate", "choice_count": len(plan["choices"]),
                "reason": "non-assertion elaborator is not yet available"}
    if env.unit_schema is not None:
        raise UnsupportedProfile("reading queries over quantity statements are not certified; "
                                 "admit the claim graph on the quantity document route")
    conclusion = formula_from_data(env, conclusion_ast)
    fixed_formulas = [formula_from_data(env, ast) for ast in fixed]
    formulas = [[formula_from_data(env, r["content"]) for r in s["readings"]] for s in sets]

    def prove(premises):
        result = prove_entailment(env, premises, conclusion, max_steps=max_steps)
        if result.status != "Found":
            return None
        replay = check_entailment_certificate(env, premises, conclusion, result.certificate,
                                               max_steps=max_steps)
        return result.certificate if replay.valid else None

    models = {}

    def witness(premises):
        found = find_countermodel(env, premises, conclusion, max_domain_size=max_domain_size,
                                  max_models=max_models, max_evaluations=max_evaluations)
        if found.status != "Found":
            return None
        checked = check_countermodel(env, premises, conclusion, found.model,
                                     max_evaluations=max_evaluations)
        if not checked.valid:
            return None
        models[found.model.model_id] = found.model.to_dict()
        return found.model.model_id

    evidence = {} if evidence is None else evidence

    disjunctions = []
    for rs in formulas:
        formula = rs[-1]
        for other in reversed(rs[:-1]):
            formula = Or(other, formula)
        disjunctions.append(formula)
    status = premise_status(env, [*fixed_formulas, *disjunctions],
                            max_proof_steps=max_steps, max_domain_size=max_domain_size,
                            max_models=max_models, max_evaluations=max_evaluations)
    vacuous = (True if status["status"] == "INCONSISTENT" else
               False if status["status"] == "model" else None)
    all_proof = prove([*fixed_formulas, *disjunctions])
    if all_proof is not None:
        evidence["certificate"] = all_proof
        return {"verdict": "ALL", "route": "assertion-disjunction", "certificate": all_proof,
                "labels": [f"readings:{s['id']}@{s['version']}:all" for s in sets],
                "vacuous": vacuous, "premises": status}
    shared = witness([*fixed_formulas, *(f for rs in formulas for f in rs)])
    if shared is not None:
        evidence["model"] = models[shared]
        return {"verdict": "NONE", "route": "assertion-shared-model", "model_id": shared,
                "labels": [f"readings:{s['id']}@{s['version']}:all" for s in sets],
                "vacuous": vacuous, "premises": status}
    count = 1
    for rs in formulas:
        count *= len(rs)
    if count > 64:
        return {"verdict": "UNKNOWN", "route": "assertion-choices", "budget": {"max_choices": 64}}
    positive = negative = None
    for choice in product(*(range(len(rs)) for rs in formulas)):
        premises = [*fixed_formulas, *(formulas[i][j] for i, j in enumerate(choice))]
        labels = [f"readings:{s['id']}@{s['version']}:{s['readings'][j].get('original_index', j)}"
                  for s, j in zip(sets, choice)]
        if positive is None:
            cert = prove(premises)
            if cert is not None:
                choice_status = premise_status(
                    env, premises, max_proof_steps=max_steps,
                    max_domain_size=max_domain_size, max_models=max_models,
                    max_evaluations=max_evaluations)
                positive = {"choice": labels, "certificate": cert,
                            "premises": choice_status}
                evidence["proof"] = {"choice": list(choice), "certificate": cert}
        if negative is None:
            model_id = witness(premises)
            if model_id is not None:
                negative = {"choice": labels, "model_id": model_id}
                evidence["countermodel"] = {"choice": list(choice), "model": models[model_id]}
        if positive is not None and negative is not None:
            return {"verdict": "SOME", "route": "assertion-choices", "proof": positive,
                    "countermodel": negative,
                    "vacuous": (True if positive["premises"]["status"] == "INCONSISTENT" else
                                False if positive["premises"]["status"] == "model" else None),
                    "premises": positive["premises"]}
    return {"verdict": "UNKNOWN", "route": "assertion-choices",
            "reason": "no complete checked classification within the search budget"}
