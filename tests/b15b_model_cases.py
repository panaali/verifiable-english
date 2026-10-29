"""Search, premise status and comparison over every fixture environment (lean-first batch 15b, review A1/B1).

Batch 15b moved Python's search to Rust's, and witness non-vacuity to Lean's `ve_metered`; both engines read
the model environment (`profiles.model_environment`), not the environment Python validated. The cases here
run the public operations over every distinct environment of the route fixtures and the norm-defaults wire
examples, each also with English display text on every sort, predicate and constant, so that every
registered profile and every display field reaches both engines. Their answers were recorded at the base,
where Python searched by itself (`record`, run from a base checkout), together with the environments
themselves, and `tests/test_model_environment.py` runs the same cases over those saved environments and
compares the head's answers with that oracle.

    python -I tests/b15b_model_cases.py record tests/data/b15b-model-oracle.json.gz
"""
from __future__ import annotations

from copy import deepcopy
import gzip
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def _found(value, out):
    """Every environment JSON object nested in `value`, in document order."""
    stack = [value]
    while stack:
        item = stack.pop()
        if type(item) is dict:
            if "language" in item and "vocabulary" in item:
                out.append(item)
            stack.extend(reversed(list(item.values())))
        elif type(item) is list:
            stack.extend(reversed(item))


SOURCES = ("tests/data/route-cases.jsonl", "ve/wire_contract/examples/*/*.json", "conformance/*.json",
           "conformance/**/*.json", "usecases/**/environment*.json", "tests/data/**/*.json")
PER_COMBINATION = 4


def build(raw: dict):
    """The Python environment of `raw`: a rights environment (its block validated) under rights@0."""
    from ve.environment import Environment
    if type(raw.get("profiles")) is list and "rights@0" in raw["profiles"]:
        from ve.rights import RightsEnvironment
        return RightsEnvironment(raw)
    return Environment(raw)


def environments() -> list[tuple[str, dict]]:
    """(key, environment JSON): up to PER_COMBINATION distinct valid fixture environments per profile
    combination, each followed by its display-text variant."""
    raws = []
    for pattern in SOURCES:
        for path in sorted(ROOT.glob(pattern)):
            text = path.read_text()
            for line in (text.splitlines() if path.suffix == ".jsonl" else [text]):
                try:
                    _found(json.loads(line), raws)
                except ValueError:
                    continue
    out, seen, per = [], set(), {}
    for raw in raws:
        key = json.dumps(raw, sort_keys=True)
        profiles = (",".join(map(str, raw["profiles"])) if type(raw.get("profiles")) is list
                    else str(raw.get("profile")))
        if key in seen or per.get(profiles, 0) >= PER_COMBINATION:
            continue
        seen.add(key)
        try:
            build(raw)
        except Exception:
            continue
        per[profiles] = per.get(profiles, 0) + 1
        name = f"{raw['language']}:{profiles}#{per[profiles]}"
        out.append((name, raw))
        shown = displayed(raw)
        try:
            build(shown)
        except Exception:
            continue
        if shown != raw:
            out.append((name + "+display", shown))
    return out


def displayed(raw: dict) -> dict:
    """`raw` with an English display on every sort, predicate and constant that has none."""
    shown = deepcopy(raw)
    vocabulary = shown["vocabulary"]
    for name, entry in vocabulary.get("sorts", {}).items():
        entry.setdefault("verbalisation", {"singular": name.replace("_", " "),
                                           "plural": name.replace("_", " ") + "s"})
    for entry in vocabulary.get("predicates", {}).values():
        if "description" in entry and "{" in entry["description"]:
            entry.setdefault("verbalisation", entry["description"])
    for name, entry in vocabulary.get("constants", {}).items():
        if entry.get("sort") != "$string":
            entry.setdefault("verbalisation", name.replace("_", " "))
    return shown


def _atom(env):
    """A closed-formula builder over the first plain predicate, or None."""
    from ve.ast import Binary, Exists, Forall, Unary, Var
    defined = env.definition_entries.keys()
    for name in sorted(env.predicates):
        arguments = env.predicates[name].arguments
        if name in defined or len(arguments) > 2 or any(s.startswith("$") for s in arguments):
            continue
        body = Unary(name, Var(0)) if len(arguments) == 1 else Binary(name, Var(1), Var(0))

        def close(formula, quantifier, arguments=arguments):
            for sort in reversed(arguments):
                formula = quantifier(sort, formula)
            return formula
        return body, lambda f: close(f, Forall), lambda f: close(f, Exists)
    return None


def answer(run) -> dict:
    try:
        return {"ok": run()}
    except Exception as exc:  # the oracle records every outcome, errors included
        return {"error": getattr(exc, "code", type(exc).__name__), "message": str(exc)}


def search_answer(result) -> dict:
    data = result.to_dict()
    return {key: data[key] for key in ("status", "model", "models_checked", "evaluations", "detail")}


def comparison(result) -> dict:
    return {"status": result.status, "relation": result.relation,
            **{name: {"status": direction.status,
                      "model": None if direction.model is None else direction.model.to_dict()}
               for name, direction in (("forward", result.a_implies_b), ("reverse", result.b_implies_a))}}


def cases(envs):
    """(id, thunk) for every query over every (name, environment JSON) of `envs`."""
    from ve.ast import Eq, Exists, Implies, Not, Var
    from ve.equivalence import compare
    from ve.search import find_countermodel, find_distinguishing_model
    from ve.vacuity import premise_status
    out = []
    for name, raw in envs:
        env = build(raw)
        sorts = sorted(s for s in env.sorts if not s.startswith("$"))
        if sorts:
            inhabited = Exists(sorts[0], Eq(Var(0), Var(0)))
            out.append((f"{name}|inhabited", lambda env=env, f=inhabited: search_answer(
                find_countermodel(env, (), f, max_domain_size=2, max_models=2000))))
        built = _atom(env)
        if built is None:
            continue
        atom, every, some = built
        guard = every(Implies(atom, atom))
        for semantic in (False, True):
            out.append((f"{name}|guarded|{semantic}", lambda env=env, g=guard, c=every(Not(atom)), s=semantic:
                        search_answer(find_countermodel(env, (g,), c, max_domain_size=2, max_models=2000,
                                                        nonvacuous_for=g, semantic_nonvacuity=s))))
        out.append((f"{name}|distinguishing", lambda env=env, a=some(atom), b=every(atom): search_answer(
            find_distinguishing_model(env, a, b, max_domain_size=2, max_models=2000, nonvacuous_for=a))))
        out.append((f"{name}|premise_status", lambda env=env, p=some(atom): {
            key: value for key, value in premise_status(env, (p,), max_models=2000).items()
            if key in ("status", "model_id")}))
        out.append((f"{name}|compare", lambda env=env, a=some(atom), b=every(atom): comparison(
            compare(env, a, b, {"max_models": 2000}))))
    return out


def run_all(envs) -> dict:
    return {case_id: answer(thunk) for case_id, thunk in cases(envs)}


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] != "record":
        raise SystemExit(__doc__)
    sys.path.insert(0, str(Path.cwd()))
    envs = environments()
    answers = run_all(envs)
    with gzip.open(sys.argv[2], "wt") as stream:
        json.dump({"environments": envs, "answers": answers}, stream, sort_keys=True, indent=0)
    print(len(envs), len(answers))


if __name__ == "__main__":
    main()
