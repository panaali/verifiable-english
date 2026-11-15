"""kb-10c shadow (evidence only): Python's `check_conflict` on a soft document against Lean's soft route.

A test-only script, not a product switch: nothing it installs changes an answer. It runs one of the three
safety-framework harnesses (`HARNESSES`) with a read-only wrapper around the harness's `check_conflict`
(every call is `check_conflict(doc.elaborated, ...)` on a soft document's W1 elaboration) and one around
`ve.norms._prove_targets` (Python's untrusted prover). For each call it records Python's status, then asks
`ve.soft_route.check_soft_conflict` the same question on the document's soft source, with the output of the
same generators:

* Python found a witness in the case model (CONFLICT): the soft route's `witness` case with that model, target
  and tuple.
* Otherwise: the soft route's `packages` case with the certificates Python's prover made for that call (one
  per conflict target), re-bound to the soft source's environment id and document hash; no packages when the
  prover found none (Python's UNKNOWN), so Lean answers UNKNOWN for the first target without one.

Python's W1 check of a soft document already works over the soft base (`SoftenedNormDocument.base_environment`
is a `SoftBaseEnvironment`: its Background holds the soft exception and coherence premises, which both the
prover and the model check read), so its certificates are proofs of the soft route's conclusions from
`Background_base′` and replay there unchanged. The one difference the pairs cannot show is in the claim:
the soft route's CONFLICT-FREE says it holds among rules on the same act, conditional on the open coherence
premises it names (`conditional_on`); the harness's W1 status says CONFLICT-FREE with no condition. The report
counts those answers and lists every label.

Each distinct (document, model, prove) question is asked once; every call is listed with its harness item.
The report (docs/usecases/safetyfw/<case>/kb10-conflict-shadow.json) is saved evidence that no test recomputes.

    uv run python usecases/safetyfw_conflict_shadow.py anthropic-rsp docs/usecases/safetyfw/anthropic-rsp/kb10-conflict-shadow.json

Since kb-10c step (5) the harnesses call `ve.soft_route.decide_soft_conflict` and no longer `check_conflict`, so
a run on a later commit has nothing to wrap; the script is kept as the record of how the saved evidence was made
(on 26358508f, before the switch).
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for entry in (ROOT, ROOT / "usecases"):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import safetyfw_shadow as selected_shadow  # noqa: E402
from ve import norms as ve_norms, soft_route  # noqa: E402
from ve.errors import CheckerUnavailable, VEError  # noqa: E402

_digest = selected_shadow._digest


def _model_json(model):
    return model.to_dict() if hasattr(model, "to_dict") else model


def classify(python, soft):
    """A status pair's class: `identical`, an explained difference, or `unexplained`."""
    if soft["status"] == python["status"]:
        return "identical"
    if (python["status"] == "CONFLICT" and soft["status"] == "refused"
            and "soft background" in soft.get("error", "")):
        return "explained: the witness model is outside the soft premises (Lean's soft background check)"
    return "unexplained"


class ConflictShadow:
    """The recorded `check_conflict` calls of one run and the soft route's answer to each.

    `soft` asks the soft route (default `ve.soft_route.check_soft_conflict`); a self-test passes its own."""

    def __init__(self, soft=None):
        self.soft = soft_route.check_soft_conflict if soft is None else soft
        self.questions = {}        # question digest -> {"python": ..., "soft": ..., "class": ...}
        self.calls = []            # {"context", "question", "python"}
        self.unsourced = Counter()  # calls on a document without a soft source, by context
        self.context = []
        self._proofs = []          # (document, _prove_targets result) of the call in progress

    # -- the soft route's answer to one question ---------------------------------------------------------------
    def ask(self, source, **case):
        try:
            row = self.soft(source, **case)
        except (VEError, CheckerUnavailable) as error:
            return {"status": "refused", "class": type(error).__name__, "error": str(error)[:400]}
        answer = {"status": row["verdict"], "status_text": row["status_text"], "targets": list(row["targets"])}
        for field in ("conditional_on", "detail", "target", "witness_kind"):
            if field in row:
                answer[field] = row[field]
        return answer

    def soft_answer(self, source, model, report, proofs, certificates):
        """The soft route asked what Python was asked, with Python's generators' output."""
        if report.status == "CONFLICT":
            witness = {"target": report.target, "model": _model_json(model), "tuple": list(report.tuple)}
            return {"case": "witness", **self.ask(source, witness=witness)}
        made = proofs if isinstance(proofs, dict) else certificates if isinstance(certificates, dict) else {}
        packages = {target: {"environment_id": source.env.environment_id, "document_hash": source.document_hash,
                             "target": target, "certificate": package.get("certificate")}
                    for target, package in made.items() if isinstance(package, dict)}
        return {"case": "packages", "packages": len(packages), **self.ask(source, packages=packages)}

    # -- recording ---------------------------------------------------------------------------------------------
    def record(self, document, options, report):
        context = " / ".join(self.context) or "(outside an item)"
        source = document.__dict__.get("_soft_source")
        proofs = next((result for made, result in reversed(self._proofs) if made is document), None)
        if source is None:
            self.unsourced[context] += 1
            return
        model = options.get("model")
        python = {"status": report.status}
        for field in ("target", "detail"):
            if getattr(report, field):
                python[field] = getattr(report, field)
        if report.tuple:
            python["tuple"] = list(report.tuple)
        python["targets"] = [name for name, *_ in document.conflict_targets()]
        question = _digest([source.env.to_dict(), [rule.to_dict() for rule in source.rules], _model_json(model),
                            bool(options.get("prove")), options.get("certificates") is not None])
        if question not in self.questions:
            soft = self.soft_answer(source, model, report, proofs, options.get("certificates"))
            self.questions[question] = {"python": python, "soft": soft, "class": classify(python, soft),
                                        "targets_agree": soft.get("targets", python["targets"]) == python["targets"]}
        elif self.questions[question]["python"]["status"] != python["status"]:
            self.questions[question]["class"] = "unexplained"  # one question, two Python answers
        self.calls.append({"context": context, "question": question, "python": python["status"]})

    # -- the report ----------------------------------------------------------------------------------------------
    def report(self):
        by_class = Counter(self.questions[call["question"]]["class"] for call in self.calls)
        pairs = Counter((self.questions[call["question"]]["python"]["status"],
                         self.questions[call["question"]]["soft"]["status"]) for call in self.calls)
        items = {}
        for call in self.calls:
            entry = self.questions[call["question"]]
            item = items.setdefault(call["context"], {"calls": 0, "pairs": Counter(), "differ": []})
            item["calls"] += 1
            item["pairs"][f"{entry['python']['status']} / {entry['soft']['status']}"] += 1
            if entry["class"] != "identical" and call["question"] not in item["differ"]:
                item["differ"].append(call["question"])
        free = [q for q in self.questions.values() if q["soft"]["status"] == "CONFLICT-FREE"]
        conditional = [q for q in free if q["soft"].get("conditional_on")]
        differences = [{"question": key, **entry} for key, entry in self.questions.items()
                       if entry["class"] != "identical" or not entry["targets_agree"]]
        return {
            "calls_compared": len(self.calls),
            "questions": len(self.questions),
            "status_pairs": {f"{p} / {s}": n for (p, s), n in sorted(pairs.items())},
            "classes": dict(sorted(by_class.items())),
            "unexplained_calls": by_class.get("unexplained", 0),
            "targets_disagree": sum(1 for q in self.questions.values() if not q["targets_agree"]),
            "conflict_free_questions": len(free),
            "conflict_free_conditional": {
                "questions": len(conditional),
                "labels": sorted({label for q in conditional for label in q["soft"]["conditional_on"]}),
                "note": "the soft route's CONFLICT-FREE holds among rules on the same act, conditional on these "
                        "open coherence premises; the harness's W1 CONFLICT-FREE reads the same soft premises "
                        "(SoftBaseEnvironment's Background) but states no condition"},
            "calls_without_soft_source": dict(self.unsourced),
            "items": {name: {"calls": item["calls"], "pairs": dict(item["pairs"]), "differ": item["differ"]}
                      for name, item in sorted(items.items())},
            "differences": differences,
        }


@contextmanager
def installed(shadow, harness, contexts):
    """Install the recording wrappers on `harness` (a loaded run.py) and on `ve.norms._prove_targets`."""
    saved_check, saved_prove = harness.check_conflict, ve_norms._prove_targets
    saved_module = {}

    def prove_targets(document, *args, **kwargs):
        result = saved_prove(document, *args, **kwargs)
        shadow._proofs.append((document, result))
        return result

    def check_conflict(document, **options):
        shadow._proofs.clear()
        report = saved_check(document, **options)
        try:
            shadow.record(document, options, report)
        finally:
            shadow._proofs.clear()
        return report

    def labelled(name, label):
        original = saved_module[name] = getattr(harness, name)

        def call(*args, **kwargs):
            shadow.context.append(label(harness, *args, **kwargs))
            try:
                return original(*args, **kwargs)
            finally:
                shadow.context.pop()
        for attribute in ("cache_clear", "cache_info"):
            if hasattr(original, attribute):
                setattr(call, attribute, getattr(original, attribute))
        setattr(harness, name, call)

    harness.check_conflict, ve_norms._prove_targets = check_conflict, prove_targets
    try:
        for name, label in contexts.items():
            labelled(name, label)
        yield shadow
    finally:
        harness.check_conflict, ve_norms._prove_targets = saved_check, saved_prove
        for name, original in saved_module.items():
            setattr(harness, name, original)


HARNESSES = {name: {"path": spec["path"], "args": spec["args"], "contexts": spec["contexts"]}
             for name, spec in selected_shadow.HARNESSES.items()}


def shadow_run(name):
    """Run harness `name` with the wrappers; the report, with the harness's own exit and wall time."""
    spec = HARNESSES[name]
    harness = selected_shadow.load(name)
    shadow = ConflictShadow()
    contexts = dict(spec["contexts"])
    stages = contexts.pop("progress", "absent") is None
    started = time.monotonic()
    with installed(shadow, harness, contexts):
        if stages:
            original = harness.progress
            harness.progress = selected_shadow._fsf_stages(shadow)(original)
        try:
            try:
                code = harness.main(spec["args"])
                outcome = "exit 0" if not code else f"exit {code}"
            except SystemExit as stop:
                outcome = f"SystemExit: {stop.code}"
        finally:
            if stages:
                harness.progress = original
    seconds = round(time.monotonic() - started, 1)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {"harness": spec["path"], "command": f"uv run python usecases/safetyfw_conflict_shadow.py {name} OUT",
            "harness_args": spec["args"], "harness_outcome": outcome, "commit": head,
            "seconds": seconds, **shadow.report()}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    name, out = argv
    report = shadow_run(name)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(f"{name}: {report['harness_outcome']}; calls {report['calls_compared']} "
          f"({report['questions']} questions); pairs {report['status_pairs']}; classes {report['classes']}; "
          f"targets disagree {report['targets_disagree']}; conditional CONFLICT-FREE "
          f"{report['conflict_free_conditional']['questions']}; unsourced {sum(report['calls_without_soft_source'].values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
