"""Record which checker path, Lean's or Python's, computes the keyed answers of a use case.

`docs/usecases/keyed-answers.md` says which answers of a norm document with soft rules Lean decides and
which Python decides. Its table is checked against this recorder in two ways: on a small soft document by
`tests/test_keyed_answers_authority.py`, and on the three keyed harnesses by the saved evidence
`docs/usecases/keyed-answers.json`, which `uv run python usecases/measure_keyed_paths.py --write` regenerates
(the harness runner is kept apart so that loading this recorder runs no harness).
A path is named by its owner and its function: `python _find_conflict` means Python's evaluator was built
by `_find_conflict`.
"""
from __future__ import annotations

import collections
import contextlib
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT.parent / "docs" / "usecases" / "keyed-answers.json"
HARNESSES = {"anthropic-rsp": ROOT / "anthropic-rsp" / "run.py",
             "openai-preparedness": ROOT / "openai-preparedness" / "run.py",
             "safety-framework": ROOT / "safety-framework" / "run.py"}

# (module, function, owner): calls of these functions are counted under their own name.
_CALLS = (("entailment", "_check_certificate_lean", "lean"),
          ("evaluate", "_evaluate_lean", "lean"),
          ("norms", "_check_conflict_lean", "lean"),
          ("norms", "_check_conflict_python", "python"),
          ("norms", "_norm_certificate_lean", "lean"),
          ("norms", "_norm_certificate_python", "python"))


@contextlib.contextmanager
def recording():
    """Count the checker paths taken inside the block; yields a Counter of `"<owner> <function>"`.

    Python's evaluator (`ve.evaluate._Evaluator`) is counted under the function that builds it. A
    Python certificate replay is the prover's check of its own trace (`_background=False`, untrusted and
    never reported) or a public replay. Lean's soft elaboration is counted per relayed `soft-elaborate`, and
    Lean's selected rules and completed outcomes per `soft-selected` call of a soft document
    (`ve.softnorms.selected_at`, kb-10b).
    """
    # `ve.evaluate` is also the name of a function `ve` re-exports, so the modules are looked up by name.
    modules = {"evaluate": importlib.import_module("ve.evaluate"),
               "entailment": importlib.import_module("ve.entailment"),
               "norms": importlib.import_module("ve.norms")}
    evaluate, entailment = modules["evaluate"], modules["entailment"]
    soft_relay = importlib.import_module("ve.backends.soft_relay")
    counts: collections.Counter = collections.Counter()
    saved = []

    def patch(module, name, value):
        saved.append((module, name, getattr(module, name)))
        setattr(module, name, value)

    def counted(name, owner, original):
        def call(*args, **kwargs):
            counts[f"{owner} {name}"] += 1
            return original(*args, **kwargs)
        return call

    init = evaluate._Evaluator.__init__

    def evaluator_init(self, *args, **kwargs):
        counts[f"python {sys._getframe(1).f_code.co_name}"] += 1
        return init(self, *args, **kwargs)

    python_replay = entailment._check_certificate_python

    def replay(*args, **kwargs):
        counts["python prover-self-replay" if kwargs.get("_background") is False
               else "python _check_certificate_python"] += 1
        return python_replay(*args, **kwargs)

    softnorms = importlib.import_module("ve.softnorms")
    selected_at = softnorms.selected_at

    def soft_selected(*args, **kwargs):
        counts["lean soft-selected"] += 1
        return selected_at(*args, **kwargs)

    relay_run = soft_relay.run

    def soft(request, *args, **kwargs):
        if type(request) is dict and request.get("kind") == "soft-elaborate":
            counts["lean soft-elaborate"] += 1
        return relay_run(request, *args, **kwargs)

    try:
        patch(evaluate._Evaluator, "__init__", evaluator_init)
        patch(entailment, "_check_certificate_python", replay)
        patch(soft_relay, "run", soft)
        patch(softnorms, "selected_at", soft_selected)
        for module_name, name, owner in _CALLS:
            patch(modules[module_name], name, counted(name, owner, getattr(modules[module_name], name)))
        yield counts
    finally:
        for module, name, value in reversed(saved):
            setattr(module, name, value)
