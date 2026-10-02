"""Reading-set structure and conservative checking plans.

Only same-background assertion readings may use the disjunction shortcut.
Every other kind requires complete choice enumeration or stays UNKNOWN.
"""
from __future__ import annotations

from collections import Counter
from itertools import product

from .assurance import semantic_entry
from .admission import _check_kind, token
from .ast import formula_from_data
from .errors import UnsupportedProfile, VEError
from .identity import meaning_id
from .readings_english import SOURCE_WORDS


def source_word_text(source: bytes, span, unit_span):
    """Read a source-word byte span; unknown words omit E14, invalid spans fail."""
    if (type(source) is not bytes or type(span) is not list or len(span) != 2
            or any(type(n) is not int for n in span)
            or type(unit_span) is not list or len(unit_span) != 2
            or not unit_span[0] <= span[0] < span[1] <= unit_span[1]):
        raise VEError("InvalidInput: invalid source word span")
    try:
        word = source[span[0]:span[1]].decode("utf-8")
    except UnicodeDecodeError:
        raise VEError("InvalidInput: invalid source word span") from None
    word = word.translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"))
    word = word.replace("\u2019", "'")
    return word if word in SOURCE_WORDS else None


def rights_meaning_id(env, content):
    """Bind one rights candidate to its source environment and exact AST."""
    from .softnorms import soft_digest
    return soft_digest(f"ve-meaning-{env.identity_version}\n",
                       {"environment_id": env.environment_id, "ast": content})


def _right_situation(env, content, wire, unit_ids=()):
    """Evaluate a complete right reading on one checked finite base situation."""
    from itertools import product as tuples
    from .evaluate import _Evaluator
    from .model import FiniteModel
    from .rights import RightsDocument

    rights = RightsDocument(env, [{"source_units": sorted(unit_ids)}, content])
    tree = rights.soft_document.elaborated
    base = tree.base_environment()
    model = FiniteModel.from_dict(base, wire)
    evaluator = _Evaluator(base, model, 1_000_000, trace=False)
    for _label, premise in (*rights.soft_document.extended_env.soft_premises,
                            *rights.limitation_premises):
        if not evaluator.formula(premise, ())[0]:
            raise VEError("distinguishing model violates a generated premise")
    outcomes = []
    for predicate, decl in sorted(tree.env.predicates.items()):
        if decl.regulated is None:
            continue
        for values in tuples(*(model.domains[s] for s in decl.arguments)):
            bindings = tuple(zip(reversed(decl.arguments), reversed(values)))
            value, _ = evaluator.formula(tree.outcome(predicate, base=True), bindings)
            outcomes.append((predicate, values, value))
    selected = []
    for instance in rights.instances:
        rule = instance["rule"].core
        decl = tree.env.predicates[rule.predicate]
        formula = tree.selection(rule.predicate)[2][rule.name]
        expanded = tree._expand(formula, rule.predicate)
        for values in tuples(*(model.domains[s] for s in decl.arguments)):
            bindings = tuple(zip(reversed(decl.arguments), reversed(values)))
            value, _ = evaluator.formula(expanded, bindings)
            if value:
                selected.append((instance["kind"], rule.predicate, values))
    return model.model_id, (tuple(outcomes), tuple(sorted(selected)))


def validate_reading_sets(env, values, unit_ids, *, source=None, unit_spans=None):
    if type(values) is not list:
        raise VEError("reading_sets must be a list")
    seen = set()
    owners = {}
    units = {}
    for item in values:
        required = {"id", "unit", "version", "status", "readings"}
        optional = {"signature", "rejected_history", "models"}
        if "readings@1" in env.profiles:
            optional.add("source_word")
        if type(item) is not dict or not required <= set(item) or set(item) - required - optional:
            raise VEError("invalid reading set")
        if not token(item["id"]) or type(item["version"]) is not int or item["version"] < 1:
            raise VEError("invalid or duplicate reading set version")
        key = (item["id"], item["version"])
        if key in seen:
            raise VEError("invalid or duplicate reading set version")
        seen.add(key)
        if type(item["unit"]) is not str or item["unit"] not in unit_ids or item["status"] not in ("authored", "open"):
            raise VEError("invalid reading set unit or status")
        if (item["id"] in owners and owners[item["id"]] != item["unit"]
                or item["unit"] in units and units[item["unit"]] != item["id"]):
            raise VEError("one reading set per source unit; versions must keep their unit")
        owners[item["id"]] = item["unit"]
        units[item["unit"]] = item["id"]
        if "source_word" in item:
            source_word_text(source, item["source_word"],
                             None if unit_spans is None else unit_spans.get(item["unit"]))
        readings = item["readings"]
        if type(readings) is not list or not 1 <= len(readings) <= 64:
            raise VEError("reading sets hold 1 to 64 readings")
        if item["status"] == "authored" and (len(readings) != 1 or not token(item.get("signature"))):
            raise VEError("authored reading needs one signed choice")
        if item["status"] == "open" and "signature" in item:
            raise VEError("open reading set cannot have an author signature")
        ids = set()
        model_ids = set()
        rights_enabled = "rights@0" in env.profiles
        labels_enabled = rights_enabled or "readings@1" in env.profiles
        for reading in readings:
            required_reading = {"id", "kind", "meaning_id", "content", "admission"}
            if (type(reading) is not dict or not required_reading <= set(reading) or
                    set(reading) - required_reading - ({"labels"} if labels_enabled else set())):
                raise VEError("invalid reading")
            if "labels" in reading:
                labels = reading["labels"]
                if (type(labels) is not dict or any(not token(axis) or not token(value)
                                                    for axis, value in labels.items())):
                    raise VEError("invalid rights candidate labels")
            if not token(reading["id"]) or reading["id"] in ids:
                raise VEError("duplicate or invalid reading id")
            ids.add(reading["id"])
            if not (rights_enabled and reading["kind"] in
                    ("right", "right_lines", "limitation", "bar")):
                _check_kind(reading["kind"])
            if not token(reading["meaning_id"]):
                raise VEError("invalid reading meaning id")
            if reading["content"] is not None:
                content = reading["content"]
                if rights_enabled and type(content) is dict and set(content) == {"right"}:
                    from .rights import RightsDocument
                    RightsDocument(env, [{"source_units": sorted(unit_ids)}, content])
                    content_id = rights_meaning_id(env, content)
                elif env.unit_schema is not None:
                    from .units import quantity_meaning_id
                    content_id = quantity_meaning_id(env, content)
                else:
                    content_id = meaning_id(env, formula_from_data(env, content))
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
            right_contents = [r["content"] for r in readings
                              if type(r["content"]) is dict and set(r["content"]) == {"right"}]
            right_set = rights_enabled and len(right_contents) == len(readings)
            # Quantity readings are evaluated through their regenerated cores
            # on the erased target; tables are never read with tags dropped first.
            if not right_set and right_contents:
                raise VEError("UnsupportedProfile: mixed rights distinguishing situations")
            if not right_set:
                model_env, formula_of = _reading_evaluation(env)
            for name, data in models.items():
                model_id = (_right_situation(env, right_contents[0], data, unit_ids)[0] if right_set else
                            FiniteModel.from_dict(model_env, data).model_id)
                if name != model_id:
                    raise VEError("distinguishing model id does not match model")
            for reading in readings:
                for other_id, model_id in reading["admission"]["distinguishing_models"].items():
                    other = next(r for r in readings if r["id"] == other_id)
                    if reading["content"] is None or other["content"] is None:
                        continue  # other-kind elaboration is pending; the checking route reports UNKNOWN
                    if right_set:
                        first_id, a = _right_situation(env, reading["content"], models[model_id], unit_ids)
                        second_id, b = _right_situation(env, other["content"], models[model_id], unit_ids)
                        if first_id != model_id or second_id != model_id or a == b:
                            raise VEError("distinguishing model does not separate readings")
                    else:
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


def validate_couplings(env, couplings, sets, unit_ids):
    if type(couplings) is not list:
        raise VEError("invalid couplings")
    if couplings and not {"rights@0", "readings@1"}.intersection(env.profiles):
        raise VEError("UnsupportedProfile: rights@0 is required for couplings")
    if len(couplings) > 8:
        # 11: at most eight couplings, as on the Lean rights route.
        raise VEError("ResourceLimit: couplings")
    active = {(s["id"], s["version"]): s for s in active_reading_sets(sets)}
    ids = set()
    for item in couplings:
        if (type(item) is not dict or set(item) !=
                {"id", "axis", "sets", "by", "reason_spans"} or
                not token(item["id"]) or item["id"] in ids or
                not token(item["axis"]) or not token(item["by"]) or
                type(item["reason_spans"]) is not list or not item["reason_spans"] or
                not set(item["reason_spans"]) <= unit_ids or
                type(item["sets"]) is not list or len(item["sets"]) < 2):
            raise VEError("invalid coupling")
        ids.add(item["id"])
        seen = set()
        for reference in item["sets"]:
            if (type(reference) is not dict or set(reference) != {"set", "version"} or
                    (reference["set"], reference["version"]) not in active or
                    reference["set"] in seen):
                raise VEError("invalid coupling set")
            seen.add(reference["set"])
            target = active[(reference["set"], reference["version"])]
            if any(item["axis"] not in reading.get("labels", {}) for reading in target["readings"]):
                raise VEError(f"CouplingLabelMissing: {item['id']}, {reference['set']}")
        values = [set(reading["labels"][item["axis"]] for reading in
                      active[(ref["set"], ref["version"])]["readings"])
                  for ref in item["sets"]]
        if not set.intersection(*values):
            raise VEError(f"CouplingLabelMissing: {item['id']}, {item['sets'][0]['set']}")
    if couplings and not coupled_choices(active_reading_sets(sets), couplings, limit=1)[0]:
        raise VEError("CouplingUnsatisfiable: " + ", ".join(sorted(ids)))
    return ids


def coupled_choices(sets, couplings, *, limit=64):
    """Enumerate only compatible complete choices, stopping past the budget."""
    constraints = []
    for item in couplings:
        constraints.append((item["axis"], tuple(ref["set"] for ref in item["sets"])))
    choices = []
    selected = {}
    def visit(index):
        if len(choices) > limit:
            return
        if index == len(sets):
            choices.append(dict(selected))
            return
        current = sets[index]
        for number, reading in enumerate(current["readings"]):
            label_map = reading.get("labels", {})
            if any(current["id"] in members and any(
                    selected[other][1].get("labels", {}).get(axis) != label_map.get(axis)
                    for other in members if other in selected)
                   for axis, members in constraints):
                continue
            selected[current["id"]] = (number, reading)
            visit(index + 1)
            selected.pop(current["id"])
            if len(choices) > limit:
                return
    visit(0)
    return ([{name: pair[0] for name, pair in choice.items()} for choice in choices],
            len(choices) > limit)


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
        # The cited version is a set id and a version number (not a Boolean) before it is looked up.
        if not token(item["set"]) or type(item["version"]) is not int or item["version"] < 1:
            raise VEError("invalid narrowing")
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


def undetermined_units(sets, couplings=()):
    """The units whose sets still hold more than one candidate consistent with
    one value per coupled component (6.2): candidates agreeing on every coupled
    axis of their set are chosen independently, so they stay open."""
    axes = {}
    for item in couplings:
        for reference in item["sets"]:
            axes.setdefault(reference["set"], set()).add(item["axis"])
    units = []
    for reading_set in sets:
        keys = sorted(axes.get(reading_set["id"], ()))
        groups = Counter(tuple(reading.get("labels", {}).get(axis) for axis in keys)
                         for reading in reading_set["readings"])
        if max(groups.values(), default=0) > 1:
            units.append(reading_set.get("unit", reading_set["id"]))
    return units


def plan_choices(sets, *, limit=64, couplings=()):
    """Return a sound checking route; no verdict is inferred by this planner."""
    if not sets:
        return {"route": "single", "choices": [{}]}
    if couplings:
        choices, over = coupled_choices(sets, couplings, limit=limit)
        if not choices:
            # 6.2: a family of couplings (after any narrowing) that admits no
            # complete choice is an error, never a vacuous verdict over zero choices.
            raise VEError("CouplingUnsatisfiable: " + ", ".join(sorted(item["id"] for item in couplings)))
        return ({"route": "UNKNOWN", "budget": {"max_choices": limit},
                 "choice_count": len(choices), "units": undetermined_units(sets, couplings)} if over else
                {"route": "enumerate", "choices": choices,
                 "conditional_on": [f"coupling:{item['id']}" for item in couplings]})
    if all(all(r["kind"] == "asserted" and r["content"] is not None for r in s["readings"])
           for s in sets):
        return {"route": "assertion-disjunction", "choices": None,
                "all": "one proof from per-unit disjunctions",
                "none": "one shared finite model satisfying every reading"}
    count = 1
    for s in sets:
        count *= len(s["readings"])
        if count > limit:
            return {"route": "UNKNOWN", "budget": {"max_choices": limit}, "choice_count": count,
                    "units": undetermined_units(sets)}
    return {"route": "enumerate", "choices": [dict(zip((s["id"] for s in sets), c))
             for c in product(*(range(len(s["readings"])) for s in sets))]}


def _lean_readings_scope(env) -> bool:
    """Whether Lean's `readings` mode checks verdicts over `env`: the frozen v0
    and v0.1 envelopes, or a ve.core@0.2 environment of any family
    (`validation.family_in_scope`)."""
    from .backends.validation import LEGACY_LANGUAGES, family_in_scope
    if getattr(env, "language", None) in LEGACY_LANGUAGES:
        return True
    return getattr(env, "language", None) == "ve.core@0.2" and family_in_scope(env)


@semantic_entry("readings")
def check_readings(env, sets, conclusion_ast, *, max_steps=10_000, max_domain_size=2,
                   max_models=10_000, max_evaluations=100_000, fixed=(), joint_choices=None,
                   couplings=()):
    """Checked ALL/SOME/NONE for assertion sets; otherwise honest UNKNOWN.

    Every positive proof is replayed by the certificate checker, and every
    negative claim has an independently checked finite model. Failure of
    bounded search means UNKNOWN. We never infer NONE from proof failure.
    Under a backend authority the replays and model checks run on the backend
    and Lean's `readings` mode must confirm an ALL, NONE or SOME verdict from
    its evidence (`lean/VE/Service/Readings.lean`).
    """
    from .backends.dispatch import authority_for, composed, execute
    options = {"max_steps": max_steps, "max_domain_size": max_domain_size, "max_models": max_models,
               "max_evaluations": max_evaluations, "fixed": fixed, "joint_choices": joint_choices,
               "couplings": couplings}

    def python():
        return _check_readings_python(env, sets, conclusion_ast, **options)

    if authority_for("readings") in ("python", "rust-experimental") or not _lean_readings_scope(env):
        return python()
    if couplings:
        # Coupled choices (docs/spec/rights-PLAN.md) have no Lean interface yet:
        # every per-choice certificate and model is checked on the backend, and
        # the coupled enumeration and its verdict stay Python's (trusted,
        # narrowed; a recorded gap).
        return execute("readings", {"kind": "readings"}, python, lean=composed("lean", python))
    if joint_choices is not None:
        # Discourse joint choices (docs/spec/discourse.md) have no Lean
        # interface yet either: each choice's certificate and model is checked
        # on the backend, and the joint enumeration and its verdict stay
        # Python's (a recorded gap, as for couplings).
        return execute("readings", {"kind": "readings"}, python, lean=composed("lean", python))
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
                           max_models=10_000, max_evaluations=100_000, fixed=(), joint_choices=None,
                           couplings=(), evidence=None):
    """`evidence`, when given, receives the verdict's evidence on the wire."""
    from .ast import Or
    from .entailment import check_entailment_certificate, prove_entailment
    from .search import check_countermodel, find_countermodel
    from .vacuity import premise_status

    if joint_choices is not None:
        if joint_choices.get("status") == "UNKNOWN":
            return {"verdict": "UNKNOWN", "route": "joint-choices",
                    "budget": {"max_choices": joint_choices["budget"]}}
        if not all(all(r["kind"] == "asserted" and r["content"] is not None
                       for r in s["readings"]) for s in sets):
            return {"verdict": "UNKNOWN", "route": "joint-choices",
                    "reason": "non-assertion elaborator is not yet available"}
        conclusion = formula_from_data(env, conclusion_ast)
        fixed_formulas = [formula_from_data(env, ast) for ast in fixed]
        formulas = {f"{s['id']}@{s['version']}": [formula_from_data(env, r["content"])
                                                   for r in s["readings"]] for s in sets}
        positive, negative = [], []
        unknown = False
        for choice in joint_choices["choices"]:
            premises = [*fixed_formulas, *(formulas[key][index] for key, index in choice.items())]
            proof = prove_entailment(env, premises, conclusion, max_steps=max_steps)
            if proof.status == "Found" and check_entailment_certificate(
                    env, premises, conclusion, proof.certificate, max_steps=max_steps).valid:
                positive.append({"choice": choice, "certificate": proof.certificate,
                                 "premises": premise_status(
                                     env, premises, max_proof_steps=max_steps,
                                     max_domain_size=max_domain_size, max_models=max_models,
                                     max_evaluations=max_evaluations)})
                continue
            model = find_countermodel(env, premises, conclusion,
                                      max_domain_size=max_domain_size, max_models=max_models,
                                      max_evaluations=max_evaluations)
            if model.status == "Found" and check_countermodel(
                    env, premises, conclusion, model.model,
                    max_evaluations=max_evaluations).valid:
                negative.append({"choice": choice, "model_id": model.model.model_id})
            else:
                unknown = True
        if unknown:
            return {"verdict": "UNKNOWN", "route": "joint-choices",
                    "reason": "a compatible choice could not be classified"}
        if positive and negative:
            return {"verdict": "SOME", "route": "joint-choices", "proof": positive[0],
                    "countermodel": negative[0]}
        if positive:
            return {"verdict": "ALL", "route": "joint-choices", "proofs": positive}
        return {"verdict": "NONE", "route": "joint-choices", "countermodels": negative}

    plan = plan_choices(sets)
    plan = plan_choices(sets, couplings=couplings)
    if plan["route"] == "UNKNOWN":
        return {"verdict": "UNKNOWN", "route": plan["route"], "budget": plan["budget"],
                "units": plan["units"]}
    if plan["route"] == "enumerate" and any(
            r["kind"] != "asserted" or r["content"] is None
            for s in sets for r in s["readings"]):
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

    if couplings:
        outcomes = []
        for choice in plan["choices"]:
            premises = [*fixed_formulas, *(formulas[i][choice[s["id"]]]
                                            for i, s in enumerate(sets))]
            labels = [f"readings:{s['id']}@{s['version']}:{s['readings'][choice[s['id']]].get('original_index', choice[s['id']])}"
                      for s in sets]
            certificate = prove(premises)
            model_id = None if certificate is not None else witness(premises)
            row = {"choice": labels,
                   **({"certificate": certificate} if certificate is not None else
                      {"model_id": model_id} if model_id is not None else
                      {"status": "UNKNOWN"})}
            if certificate is not None:
                # 5.3: every positive choice carries its premise-set line, so an
                # inconsistent choice is reported vacuous rather than as support.
                row["premises"] = premise_status(
                    env, premises, max_proof_steps=max_steps, max_domain_size=max_domain_size,
                    max_models=max_models, max_evaluations=max_evaluations)
                row["vacuous"] = (True if row["premises"]["status"] == "INCONSISTENT" else
                                  False if row["premises"]["status"] == "model" else None)
            outcomes.append(row)
        positive = [row for row in outcomes if "certificate" in row]
        negative = [row for row in outcomes if "model_id" in row]
        if not outcomes:
            raise VEError("CouplingUnsatisfiable: " + ", ".join(sorted(item["id"] for item in couplings)))
        verdict = ("SOME" if positive and negative else
                   "ALL" if len(positive) == len(outcomes) else
                   "NONE" if len(negative) == len(outcomes) else "UNKNOWN")
        vacuous = [row["vacuous"] for row in positive]
        return {"verdict": verdict, "route": "coupled-choices", "choices": outcomes,
                "conditional_on": plan["conditional_on"],
                **({"vacuous": (True if True in vacuous else
                                False if all(v is False for v in vacuous) else None)}
                   if positive else {})}

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
        return {"verdict": "UNKNOWN", "route": "assertion-choices", "budget": {"max_choices": 64},
                "units": undetermined_units(sets)}
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
