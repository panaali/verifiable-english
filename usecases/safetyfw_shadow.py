"""kb-10b shadow (evidence only): Python's selected rules and completed outcomes against Lean's `soft-selected`.

A test-only script, not a product switch: nothing it installs changes an answer. It runs one of the three
safety-framework harnesses (`HARNESSES`) with two read-only wrappers, `SoftenedNormDocument.selected_rules`
and the harness's own `completed`, which record each call (the soft source, the case model, the predicate, the
tuple and Python's answer) and return Python's answer unchanged. After the run it asks Lean once per document
and model, with every query recorded for that pair (`ve.soft_route.selected_at`), and lists every call where
Python's answer and Lean's differ, with the document choice, the case, Lean's `background` flag and both
answers (docs/usecases/safetyfw/<case>/kb10-shadow.json, saved evidence that no test recomputes).

    uv run python usecases/safetyfw_shadow.py anthropic-rsp docs/usecases/safetyfw/anthropic-rsp/kb10-shadow.json

The harness runs with `--check`, so a shadow run that changed a keyed answer would fail as the harness does.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import time
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ve import soft_route  # noqa: E402
from ve.softnorms import SoftenedNormDocument, SoftNormDocument  # noqa: E402


def _text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(value):
    return hashlib.sha256(_text(value).encode()).hexdigest()[:16]


class Shadow:
    """The recorded calls of one run and their comparison with Lean.

    A recorded call is keyed by its document (the soft source's environment and rules), its model (the
    model's `to_dict`), its predicate and tuple; `compare` sends each (document, model) pair's distinct
    queries to Lean in one `selected_at` call."""

    def __init__(self):
        self.documents = {}      # document digest -> (SoftNormDocument, [choice labels])
        self.models = {}         # model digest -> model dict
        self.calls = []          # (kind, document digest, model digest, predicate, tuple, python answer, context)
        self.unsourced = Counter()  # selected_rules on a SoftenedNormDocument with no soft source, by context
        self.context = []        # the harness's current item labels, outermost first

    # -- recording -----------------------------------------------------------------------------------
    def _document(self, soft_document):
        # Through __dict__: a deferred SoftNormDocument elaborates on a missing attribute (`__getattr__`).
        digest = soft_document.__dict__.get("_shadow_digest")
        if digest is None:
            digest = _digest([soft_document.env.to_dict(), [rule.to_dict() for rule in soft_document.rules]])
            soft_document._shadow_digest = digest
        entry = self.documents.setdefault(digest, (soft_document, []))
        for label in soft_document.__dict__.get("_shadow_choices", ()):
            if label not in entry[1]:
                entry[1].append(label)
        return digest

    def _model(self, model):
        data = model.to_dict() if hasattr(model, "to_dict") else model
        digest = _digest(data)
        self.models.setdefault(digest, data)
        return digest

    def record(self, kind, soft_document, model, predicate, values, answer):
        """One call of `kind` ("selected" or "completed") and Python's answer to it."""
        self.calls.append((kind, self._document(soft_document), self._model(model), predicate,
                           tuple(values), answer, " / ".join(self.context) or "(outside an item)"))

    def record_selected(self, elaborated, model, predicate, values, rules):
        source = elaborated.__dict__.get("_shadow_source")
        if source is None:
            self.unsourced[" / ".join(self.context) or "(outside an item)"] += 1
            return
        self.record("selected", source, model, predicate, values, [rule.name for rule in rules])

    # -- comparison ----------------------------------------------------------------------------------
    def groups(self):
        """{(document digest, model digest): [distinct (predicate, tuple) in first-call order]}."""
        out = {}
        for _, document, model, predicate, values, _, _ in self.calls:
            queries = out.setdefault((document, model), [])
            if (predicate, values) not in queries:
                queries.append((predicate, values))
        return out

    def ask(self, document, model, queries, *, ask=None):
        """Lean's answers {(predicate, tuple): row} and background flag for one document and model; a refused
        call is asked again query by query, so each refusal is listed with the query it names."""
        ask = ask or soft_route.selected_at
        soft_document = self.documents[document][0]
        sent = [{"predicate": p, "tuple": list(v)} for p, v in queries]
        try:
            answer = ask(soft_document, self.models[model], sent)
            return {(r["predicate"], tuple(r["tuple"])): r for r in answer["results"]}, answer["background"], {}
        except Exception as error:  # noqa: BLE001  (a refusal is a finding to list, not to hide)
            whole = f"{type(error).__name__}: {error}"
        rows, refused, background = {}, {}, None
        for query in sent:
            try:
                answer = ask(soft_document, self.models[model], [query])
            except Exception as error:  # noqa: BLE001
                refused[(query["predicate"], tuple(query["tuple"]))] = f"{type(error).__name__}: {error}"
                continue
            row = answer["results"][0]
            rows[(row["predicate"], tuple(row["tuple"]))] = row
            background = answer["background"] if background is None else background and answer["background"]
        if not rows:
            refused = {key: whole for key in refused} or {("*", ()): whole}
        return rows, background, refused

    def compare(self, *, ask=None):
        """The report: counts, every mismatch, every refusal and every call answered with `background: false`."""
        mismatches, refusals, background_false = Counter(), Counter(), Counter()
        lean_calls = 0
        answers = {}
        for (document, model), queries in self.groups().items():
            lean_calls += 1
            answers[(document, model)] = self.ask(document, model, queries, ask=ask)
        counts = Counter()
        for kind, document, model, predicate, values, python, context in self.calls:
            counts[kind] += 1
            rows, background, refused = answers[(document, model)]
            choice = (self.documents[document][1] or ["(built outside the harness's document builder)"])[0]
            cell = (kind, document, choice, context, predicate, values)
            if (predicate, values) in refused or ("*", ()) in refused:
                refusals[(*cell, refused.get((predicate, values)) or refused[("*", ())])] += 1
                continue
            row = rows[(predicate, values)]
            lean = row["selected"] if kind == "selected" else row["outcome"]
            if background is False:
                background_false[cell] += 1
            if (python if kind == "selected" else python is True) != lean or (kind == "completed" and python is None):
                mismatches[(*cell, _text(python), _text(lean), background)] += 1

        def rows_of(counter, fields):
            return [dict(zip(fields, (*key[:5], list(key[5]), *key[6:])), calls=n)
                    for key, n in sorted(counter.items(), key=lambda item: _text(item[0]))]

        cell_fields = ("kind", "document", "choice", "case", "predicate", "tuple")
        return {
            "calls_compared": dict(sorted(counts.items())),
            "calls_without_soft_source": dict(sorted(self.unsourced.items())),
            "documents": len(self.documents),
            "models": len(self.models),
            "lean_calls": lean_calls,
            "distinct_queries": sum(len(q) for q in self.groups().values()),
            "mismatch_calls": sum(mismatches.values()),
            "mismatches": rows_of(mismatches, (*cell_fields, "python", "lean", "background")),
            "refused_calls": sum(refusals.values()),
            "refusals": rows_of(refusals, (*cell_fields, "error")),
            "background_false_calls": sum(background_false.values()),
            "background_false": rows_of(background_false, cell_fields),
            "document_choices": {digest: labels for digest, (_, labels) in sorted(self.documents.items())},
        }


# -- the wrappers --------------------------------------------------------------------------------------

def _label(args, kwargs):
    parts = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in sorted(kwargs.items())]
    return ", ".join(parts)


@contextmanager
def installed(shadow, harness, spec):
    """Install the recording wrappers on the classes and on `harness` (a loaded run.py) for one run."""
    saved_init, saved_selected = SoftNormDocument._init_soft, SoftenedNormDocument.selected_rules
    saved_module = {}

    def init_soft(self, *args, **kwargs):
        saved_init(self, *args, **kwargs)
        self.elaborated._shadow_source = self

    def selected_rules(self, predicate, model, values, *args, **kwargs):
        rules = saved_selected(self, predicate, model, values, *args, **kwargs)
        shadow.record_selected(self, model, predicate, values, rules)
        return rules

    def replace(name, make):
        saved_module[name] = getattr(harness, name)
        wrapper = make(saved_module[name])
        for attribute in ("cache_clear", "cache_info"):
            if hasattr(saved_module[name], attribute):
                setattr(wrapper, attribute, getattr(saved_module[name], attribute))
        setattr(harness, name, wrapper)

    def documented(original):
        def document(*args, **kwargs):
            built = original(*args, **kwargs)
            labels = built.__dict__.setdefault("_shadow_choices", [])
            label = _label(args, kwargs)
            if label not in labels:
                labels.append(label)
            return built
        return document

    def completed_wrapper(original):
        def completed(*args, **kwargs):
            value = original(*args, **kwargs)
            soft_document, model, predicate, values = spec["completed"](harness, *args, **kwargs)
            shadow.record("completed", soft_document, model, predicate, values, value)
            return value
        return completed

    def labelled(label):
        def wrap(original):
            def call(*args, **kwargs):
                shadow.context.append(label(harness, *args, **kwargs))
                try:
                    return original(*args, **kwargs)
                finally:
                    shadow.context.pop()
            return call
        return wrap

    SoftNormDocument._init_soft = init_soft
    SoftenedNormDocument.selected_rules = selected_rules
    try:
        replace(spec.get("document", "document"), documented)
        replace("completed", completed_wrapper)
        for name, label in spec["contexts"].items():
            replace(name, labelled(label))
        yield shadow
    finally:
        SoftNormDocument._init_soft, SoftenedNormDocument.selected_rules = saved_init, saved_selected
        for name, original in saved_module.items():
            setattr(harness, name, original)


def _phase(harness):
    """The harness's mutant or removed narrowing while a call runs ('' for the scored run)."""
    parts = [f"{name}={getattr(harness, name)}" for name in ("MUTANT", "WITHOUT_NARROWING")
             if getattr(harness, name, None) is not None]
    return f" [{', '.join(parts)}]" if parts else ""


HARNESSES = {
    "anthropic-rsp": {
        "path": "usecases/anthropic-rsp/run.py", "args": ["--check"],
        "completed": lambda h, doc, case, predicate, values: (doc, h.model(doc, case), predicate, values),
        "contexts": {"answer": lambda h, item: item["id"] + _phase(h)},
    },
    "openai-preparedness": {
        "path": "usecases/openai-preparedness/run.py", "args": ["--check"],
        "completed": lambda h, doc, found, predicate: (doc, h.model(doc, found), predicate,
                                                       (h.subject(predicate)[1],)),
        "contexts": {"_answer": lambda h, item: item["id"] + _phase(h)},
    },
    "safety-framework": {
        "path": "usecases/safety-framework/run.py", "args": ["--check"],
        "completed": lambda h, doc, model, predicate, values: (doc, model, predicate, values),
        "contexts": {
            "progress": None,  # replaced below: a stage name, not a call around the items
            "item_result": lambda h, kind, case, **kw: " ".join(
                [case["id"], kind] + [f"{k}={v!r}" for k, v in sorted(kw.items()) if v not in (None, ())]),
            "default_sensitive": lambda h, kind, case, level=None: f"default-sensitivity {case['id']} {kind}"
                                                                   + (f" level={level}" if level else ""),
            "conflict_result": lambda h, rule_ids, variant=(): "conflict " + ",".join(rule_ids),
        },
    },
}


def _fsf_stages(shadow):
    """FSF announces each stage through `progress(message)`; the stage is the outermost context."""
    def wrap(original):
        def progress(message):
            if shadow.context and shadow.context[0].startswith("stage "):
                shadow.context[0] = f"stage {message}"
            else:
                shadow.context.insert(0, f"stage {message}")
            return original(message)
        return progress
    return wrap


def load(name):
    spec = HARNESSES[name]
    path = ROOT / spec["path"]
    module_spec = importlib.util.spec_from_file_location(f"kb10_shadow_{name.replace('-', '_')}", path)
    module = importlib.util.module_from_spec(module_spec)
    sys.path.insert(0, str(path.parent))
    module_spec.loader.exec_module(module)
    return module


def shadow_run(name):
    """Run harness `name` with the wrappers; the report, with the harness's own exit and wall time."""
    spec = dict(HARNESSES[name])
    harness = load(name)
    shadow = Shadow()
    contexts = dict(spec["contexts"])
    stages = contexts.pop("progress", "absent") is None
    spec["contexts"] = contexts
    started = time.monotonic()
    with installed(shadow, harness, spec):
        if stages:
            original = harness.progress
            harness.progress = _fsf_stages(shadow)(original)
        try:
            try:
                code = harness.main(spec["args"])
                outcome = "exit 0" if not code else f"exit {code}"
            except SystemExit as stop:
                outcome = f"SystemExit: {stop.code}"
        finally:
            if stages:
                harness.progress = original
    harness_seconds = round(time.monotonic() - started, 1)
    started = time.monotonic()
    report = shadow.compare()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {"harness": spec["path"], "command": f"uv run python usecases/safetyfw_shadow.py {name} OUT",
            "harness_args": spec["args"], "harness_outcome": outcome, "commit": head,
            "seconds": {"harness": harness_seconds, "lean": round(time.monotonic() - started, 1)}, **report}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    name, out = argv
    report = shadow_run(name)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(f"{name}: {report['harness_outcome']}; calls {report['calls_compared']}, "
          f"{report['lean_calls']} Lean calls, {report['mismatch_calls']} mismatched calls "
          f"({len(report['mismatches'])} cells), {report['refused_calls']} refused, "
          f"{report['background_false_calls']} with background false; "
          f"unsourced {sum(report['calls_without_soft_source'].values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
