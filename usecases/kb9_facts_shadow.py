"""kb-9 shadow (evidence only): each harness's premise check against Lean's `facts` flag from `soft-selected`.

A test-only script, not a product switch: nothing it installs changes an answer. It runs one of the three
safety-framework harnesses with read-only wrappers:

* the premise check (`check_premises` in anthropic-rsp and openai-preparedness; `premise_status` in
  safety-framework, which has no `check_premises`): at every evaluation (a cache miss of the harness's own key) it
  records Python's verdict (every premise of the choice true in the case model) and asks Lean's `soft-selected`
  for the same document, model and the same premises as `facts` (`SoftenedNormDocument.selection_flags`);
  safety-framework's check has no document, so it is asked on the base choice's document and its case model of the
  same atoms (the premises name no decision predicate, so the two models agree on them);
* every keyed selection (`SoftenedNormDocument.selected_rules`, `outcome_at`): the (document, model) pair, whose
  `background` and `coherent` flags are asked once after the run (with empty `facts`).

The report (docs/usecases/safetyfw/<case>/kb9-shadow.json, saved evidence that no test recomputes): the number of
premise evaluations and the Lean calls they cost, every mismatch with its document choice, case and the formulas
whose values differ, and the keyed pairs whose `coherent` or `background` flag is false.

    uv run python usecases/kb9_facts_shadow.py anthropic-rsp docs/usecases/safetyfw/anthropic-rsp/kb9-shadow.json

The harness runs with `--check`, so a shadow run that changed a keyed answer fails as the harness does.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import ve.softnorms as softnorms  # noqa: E402
from ve.softnorms import SoftenedNormDocument  # noqa: E402

HARNESSES = {
    "anthropic-rsp": {"path": "usecases/anthropic-rsp/run.py", "check": "check_premises"},
    "openai-preparedness": {"path": "usecases/openai-preparedness/run.py", "check": "check_premises"},
    "safety-framework": {"path": "usecases/safety-framework/run.py", "check": "premise_status"},
}


def _text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _label(value):
    """A document argument as text: a choice (a dict, or its sorted item pairs) as `set=value, ...`."""
    try:
        return _choice(dict(value)) if isinstance(value, (dict, tuple)) else str(value)
    except (TypeError, ValueError):
        return str(value)


def _choice(choice):
    return ", ".join(f"{k}={v}" for k, v in sorted(choice.items())) if isinstance(choice, dict) else str(choice)


class Shadow:
    def __init__(self):
        self.evaluations = []   # one per premise evaluation: {document, case, formulas, python, lean, ...}
        self.pairs = {}         # (id(elaborated), model key) -> (elaborated, model, document label, case label)
        self.lean_cases = 0     # soft-selected cases the premise comparison sent
        self.labels = {}        # id(soft document or elaborated) -> document label
        self.cases = {}         # id(model) -> case label

    # -- the premise comparison -----------------------------------------------------------------------------
    def compare(self, elaborated, model, formulas, python_ok, document, case, evaluate_one):
        """Lean's `facts` flag for `formulas` in `model` beside Python's verdict; on a mismatch, each formula's
        value from both (Lean: one `soft-selected` case per formula)."""
        flags = elaborated.selection_flags(model, facts=list(formulas))
        row = {"document": document, "case": case, "facts": len(formulas), "python": python_ok,
               "lean": flags["facts"], "background": flags["background"], "coherent": flags["coherent"]}
        if flags["facts"] != python_ok:
            row["formulas"] = [
                {"formula": str(f), "python": evaluate_one(f),
                 "lean": elaborated.selection_flags(model, facts=[f])["facts"]} for f in formulas]
            row["formulas"] = [x for x in row["formulas"] if x["python"] != x["lean"]] or row["formulas"]
        self.evaluations.append(row)
        return row

    def keyed(self, elaborated, model):
        data = model.to_dict() if hasattr(model, "to_dict") else model
        key = (id(elaborated), _text(data))
        if key not in self.pairs:
            source = elaborated.__dict__.get("_soft_source")
            self.pairs[key] = (elaborated, model, self.labels.get(id(source), "(unlabelled)"),
                               self.cases.get(id(model), "(unlabelled)"))

    def report(self):
        mismatches = [e for e in self.evaluations if e["python"] != e["lean"]]
        flagged = {"coherent": [], "background": []}
        for elaborated, model, document, case in self.pairs.values():
            flags = elaborated.selection_flags(model, facts=[])
            for name in flagged:
                if flags[name] is False:
                    flagged[name].append({"document": document, "case": case})
        return {"premise_evaluations": len(self.evaluations),
                "facts_false": sum(1 for e in self.evaluations if e["lean"] is False),
                "mismatches": mismatches,
                "keyed_pairs": len(self.pairs),
                "coherent_false": flagged["coherent"], "background_false": flagged["background"]}


def _load(name):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from safetyfw_shadow import HARNESSES as KB10, load  # the kb-10b loader: run.py as a module
    assert KB10[name]["path"] == HARNESSES[name]["path"]
    return load(name)


@contextmanager
def installed(shadow, harness, name):
    """The read-only wrappers for one run of `harness`."""
    from ve.evaluate import evaluate
    saved = {}
    saved_selected, saved_outcome = SoftenedNormDocument.selected_rules, SoftenedNormDocument.outcome_at

    def selected_rules(self, predicate, model, values, *args, **kwargs):
        shadow.keyed(self, model)
        return saved_selected(self, predicate, model, values, *args, **kwargs)

    def outcome_at(self, predicate, model, values, *args, **kwargs):
        shadow.keyed(self, model)
        return saved_outcome(self, predicate, model, values, *args, **kwargs)

    def replace(attribute, make):
        saved[attribute] = getattr(harness, attribute)
        wrapper = make(saved[attribute])
        for name in ("cache_clear", "cache_info"):  # the harness clears its lru caches between phases
            if hasattr(saved[attribute], name):
                setattr(wrapper, name, getattr(saved[attribute], name))
        setattr(harness, attribute, wrapper)

    def documented(original):
        def document(*args, **kwargs):
            built = original(*args, **kwargs)
            label = " / ".join(_label(a) for a in args)
            shadow.labels.setdefault(id(built), label)
            return built
        return document

    def modelled(original, label):
        def model(*args, **kwargs):
            built = original(*args, **kwargs)
            shadow.cases.setdefault(id(built), label(*args))
            return built
        return model

    def python_value(env, model):
        def one(formula):
            return evaluate(env, formula, model, trace=False).value
        return one

    if name in ("anthropic-rsp", "openai-preparedness"):
        rsp = name == "anthropic-rsp"
        checked = harness._PREMISES_CHECKED if rsp else harness._PREMISES

        def check_wrapper(original):
            def check_premises(doc, case, choice):
                key = ((frozenset(harness.atoms(case)), tuple((s, choice[s]) for s in ("RS3o", "RS3i")),
                        harness.WITHOUT_NARROWING == "N1") if rsp else (case, choice.get("RS2")))
                fresh = key not in checked
                try:
                    original(doc, case, choice)
                    python_ok = True
                except AssertionError:
                    python_ok = False
                    raise
                finally:
                    if fresh:
                        model = harness.model(doc, case)
                        formulas = [f for _, fs in harness.selected_facts(choice) for f in fs]
                        shadow.compare(doc.elaborated, model, formulas, python_ok, _choice(choice),
                                       case["id"] if rsp else ", ".join(sorted(map(str, case))),
                                       python_value(doc.elaborated.base_environment(), model))
            return check_premises
        replace("check_premises", check_wrapper)
        replace("document", documented)
        replace("model", lambda original: modelled(
            original, (lambda doc, case: case["id"]) if rsp else (lambda doc, found: ", ".join(sorted(map(str, found))))))
    else:
        seen, base = set(), []

        def status_wrapper(original):
            def premise_status(atoms, item=None):
                status = original(atoms, item)
                if (atoms, item) not in seen:
                    seen.add((atoms, item))
                    if not base:
                        base.append(harness.document(harness.BASE_CHOICE))
                    # `case_model` keeps its models by (E', atoms), not by the document's rules: an entry this
                    # lookup adds is removed, so the harness never reads the base document's model for another.
                    kept = set(harness._MODELS)
                    model = harness.case_model(base[0], atoms)
                    for key in set(harness._MODELS) - kept:
                        del harness._MODELS[key]
                    env = harness.T.base_environment()
                    plain = harness._model(env, frozenset(a for a in harness.fact_atoms() | atoms
                                                          if a[0] in env.predicates))
                    case = ", ".join("(" + " ".join(a) + ")" for a in sorted(atoms)) + (f" [item {item}]" if item else "")
                    shadow.compare(base[0].elaborated, model, harness.PREMISES(item), status[0] == "model",
                                   "base choice", case, python_value(env, plain))
                return status
            return premise_status
        replace("premise_status", status_wrapper)
        replace("document", documented)
        replace("case_model", lambda original: modelled(
            original, lambda doc, atoms: ", ".join("(" + " ".join(a) + ")" for a in sorted(atoms))))

    relay = softnorms._relay_run

    def counted(request):
        if request.get("kind") == "soft-selected" and "facts" in request:
            shadow.lean_cases += 1
        return relay(request)

    SoftenedNormDocument.selected_rules, SoftenedNormDocument.outcome_at = selected_rules, outcome_at
    softnorms._relay_run = counted
    try:
        yield shadow
    finally:
        SoftenedNormDocument.selected_rules, SoftenedNormDocument.outcome_at = saved_selected, saved_outcome
        softnorms._relay_run = relay
        for attribute, original in saved.items():
            setattr(harness, attribute, original)


def run(name):
    harness = _load(name)
    shadow = Shadow()
    started = time.monotonic()
    with installed(shadow, harness, name):
        try:
            code = harness.main(["--check"])
            outcome = "exit 0" if not code else f"exit {code}"
        except SystemExit as stop:
            outcome = "exit 0" if stop.code in (0, None) else f"SystemExit: {stop.code}"
        premise_cases = shadow.lean_cases
        report = shadow.report()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {"harness": name, "commit": head, "command": f"uv run python usecases/kb9_facts_shadow.py {name} OUT",
            "harness_outcome": outcome, "wall_seconds": round(time.monotonic() - started, 1),
            "premise_check": HARNESSES[name]["check"], "lean_facts_cases_for_premises": premise_cases, **report}


def main(argv):
    name, out = argv
    report = run(name)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(report, indent=1, ensure_ascii=False, default=str) + "\n")
    print(f"{name}: {report['premise_evaluations']} premise evaluations, {len(report['mismatches'])} mismatches, "
          f"{report['keyed_pairs']} keyed pairs ({len(report['coherent_false'])} coherent false, "
          f"{len(report['background_false'])} background false); {report['harness_outcome']}")
    return 0 if report["harness_outcome"] == "exit 0" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
