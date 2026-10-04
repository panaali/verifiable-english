"""The differential fuzzer's corpus: every fixture of `conformance/` and `usecases/`, read into seeds.

A *fixture* is a JSON file under `conformance/` or `usecases/`. Each one is read by the fuzzer or listed in
`EXCLUDED` with the reason it is not; `tests/test_difffuzz.py` checks that every fixture is one or the other,
and that no file excluded as holding no input holds an environment or a request.

* `environments()`: every distinct environment of every fixture, wherever it sits (a file of its own, the
  `environment` of a case, the environment of a use-case request or bundle), and of the generated corpora
  (`GENERATED`).
* `requests()`: every route request of every fixture, found by its fields (`REQUEST_FIELDS`), and the requests
  built from each use case's documents: each model of a use-case directory against each of its environments,
  with the formulas of the directory's `.ve` documents that parse there (`usecase_requests`).
* `wire_fixtures()`: the wire-contract files the `wire` surface reads (through the wire-contract tests' corpora).
"""
from __future__ import annotations

from copy import deepcopy
import fnmatch
import functools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = ("conformance", "usecases")

# Files that are not fixtures, by pattern: (kind, reason). `artifact` files are outputs of a tool or a run
# (reports, baselines, results); they may quote environments but are not inputs. `no-input` files hold no
# environment and no request (tests/test_difffuzz.py checks that).
EXCLUDED = {
    "conformance/difffuzz-baseline.json": ("artifact", "the fuzzer's own baseline: minimised mutants, not fixtures"),
    "conformance/v0-replay-baseline.json": ("artifact", "the v0 replay's recorded outputs (conformance/replay_baseline.py)"),
    "conformance/baseline-2026-09/*.json": ("artifact", "the 2026-09 import baseline (its README)"),
    "conformance/*-report.json": ("artifact", "a generated report"),
    "conformance/fuzz-summary.json": ("artifact", "the v0 fuzzer's summary"),
    "conformance/english-before-after.json": ("no-input", "English renderings before and after a change"),
    "conformance/wire.json": ("no-input", "raw-text cases of the restricted JSON reader (tests/test_wire.py); "
                                          "the fuzzer's inputs are parsed JSON"),
    "conformance/wire-contract/engine*.json": ("no-input", "the wire-contract engine's own test vectors"),
    "conformance/wire-contract/soft-norms*-delta.json": ("no-input", "a recorded delta between engines"),
    "conformance/wire-contract/soft-norms@0-catalogue.json": ("no-input", "the soft-norms@0 diagnostic catalogue"),
    "conformance/wire-contract/soft-norms@0-gate.json": ("artifact", "the wire-contract gate's report"),
    "conformance/wire-contract/soft-norms@0-golden.json": ("artifact", "golden diagnostics of the gate"),
    "conformance/wire-contract/soft-norms@0-switch.json": ("no-input", "the switch record of soft-norms@0"),
    "usecases/*/results.json": ("artifact", "a use case's recorded results"),
    "usecases/*/*/results.json": ("artifact", "a use case's recorded results"),
    "usecases/*/definitions-results.json": ("artifact", "a use case's recorded results"),
    "usecases/*/answer-key.json": ("no-input", "a use case's hand-written answer key"),
    "usecases/*/coverage.json": ("no-input", "a use case's source-coverage table"),
    "usecases/*/spans.json": ("no-input", "a use case's source spans"),
    "usecases/*/*.manifest.json": ("no-input", "a use case's document manifest (its .ve files are read)"),
    "usecases/*/environment.english.json": ("no-input", "English surface words for an environment"),
    "usecases/*/log.vocabulary.json": ("no-input", "a vocabulary fragment the use case's script merges"),
    "usecases/*/vocabulary-lint.json": ("artifact", "a vocabulary lint report"),
    "usecases/*/theorems/*/verdict.json": ("artifact", "a recorded verdict"),
    "usecases/*/theorems/*/certificate.json": (
        "no-input", "a certificate whose premises are built by the use case's script (math-mini-paper/verify.sh)"),
    "usecases/eligibility/cases.json": ("no-input", "applicant profiles the use case's script turns into documents"),
    "usecases/eligibility/rules.json": ("no-input", "rule records the use case's script turns into documents"),
    "usecases/safety-framework/cases.json": ("no-input", "case facts the use case's script turns into documents"),
    "usecases/gatekeeper-exemption/*.json": ("no-input", "a glob@1 policy request, outside the VE checker"),
}

def _generated(module, name, convert=lambda value: value):
    def make():
        import importlib
        return convert(getattr(importlib.import_module(module), name)())
    return make


# Environments of the generated corpora and of the route tests that build theirs in code: (origin, a
# function returning one environment). These give the alternatives, speech-acts and reports routes seeds.
GENERATED = (
    ("conformance/risk.agent_ops", _generated("conformance.risk", "agent_ops")),
    ("conformance/alternatives.environment", _generated("conformance.alternatives", "environment")),
    ("conformance/alternatives.constitution_environment",
     _generated("conformance.alternatives", "constitution_environment")),
    ("tests/test_speech_acts.environment", _generated("tests.test_speech_acts", "environment",
                                                      lambda env: env.to_dict())),
    ("tests/test_reports_lean.E0", _generated("tests.test_reports_lean", "E0")),
)

# The route request kinds, each with the fields that make it (the case's other fields are dropped). A case
# with a `kind` is read by it; one without is read by every `UNKINDED` entry whose fields it has (a search
# fixture with a model to check is a `countermodel` and a `search` request).
REQUEST_FIELDS = {
    "label": ("environment", "label"),
    "dependency-order": ("environment", "nodes"),
    "admission": ("environment", "document"),
    "background": ("environment",),
    "evaluate": ("environment", "model", "ast"),
    "countermodel": ("environment", "model", "premises", "conclusion"),
    "certificate": ("environment", "premises", "conclusion", "certificate"),
    "search": ("environment", "premises", "conclusion", "max_domain_size"),
}
UNKINDED = ("evaluate", "countermodel", "certificate", "search")
# Kinds of fixture cases no surface reads, with the reason.
NOT_REQUESTS = {
    "vacuity": "its Python adapter asserts its own witness (conformance/three_way.py)",
    "base": "Rust-only norm-defaults evaluation of Python's filled premises (conformance/norm_defaults.py)",
    "layers": "Rust-only norm-defaults evaluation of Python's filled premises (conformance/norm_defaults.py)",
}


def excluded(relative: str):
    """(kind, reason) when a fixture path is excluded, else None."""
    for pattern, verdict in EXCLUDED.items():
        if fnmatch.fnmatchcase(relative, pattern):
            return verdict
    return None


def fixture_files() -> list[str]:
    """Every JSON file under the fixture directories, as a path relative to the repository."""
    out = []
    for directory in DIRECTORIES:
        out += [str(p.relative_to(ROOT)) for p in (ROOT / directory).rglob("*.json")
                if "__pycache__" not in p.parts and ".lake" not in p.parts]
    return sorted(out)


@functools.cache
def read_fixtures() -> tuple[tuple[str, object], ...]:
    """(path, parsed JSON) of every fixture that is not excluded (shared: do not mutate)."""
    return tuple((relative, json.loads((ROOT / relative).read_text())) for relative in fixture_files()
                 if excluded(relative) is None)


def _walk(value, path=()):
    yield path, value
    if type(value) is dict:
        for key, item in value.items():
            yield from _walk(item, path + (key,))
    elif type(value) is list:
        for index, item in enumerate(value):
            yield from _walk(item, path + (index,))


def is_environment(path, node) -> bool:
    """An environment: the value of an `environment` member, or an object with a string `language` and a
    `vocabulary` (an environment file, or one inside a bundle or request)."""
    if type(node) is not dict:
        return False
    if path and path[-1] == "environment":
        return True
    return type(node.get("language")) is str and "vocabulary" in node


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def environments_of(relative, data) -> list[tuple[str, object]]:
    out = []
    for path, node in _walk(data):
        if is_environment(path, node):
            out.append((relative + "".join(f"/{step}" for step in path), node))
    return out


def environments() -> list[tuple[str, object]]:
    """(origin, environment) for every distinct environment of the fixtures and the generated corpora."""
    found = {}
    for relative, data in read_fixtures():
        for origin, env in environments_of(relative, data):
            found.setdefault(canonical(env), (origin, env))
    for origin, make in GENERATED:
        env = make()
        found.setdefault(canonical(env), (origin, env))
    return list(found.values())


def request_kinds(case) -> list[str]:
    """The route request kinds a fixture object is read as."""
    if type(case) is not dict or "environment" not in case:
        return []
    kind = case.get("kind")
    if type(kind) is str:
        return [kind] if kind in REQUEST_FIELDS else []
    return [name for name in UNKINDED if all(f in case for f in REQUEST_FIELDS[name])]


def unread_kind(case) -> str | None:
    """The kind of a fixture case that `NOT_REQUESTS` leaves out, or None."""
    if type(case) is dict and "environment" in case and type(case.get("kind")) is str:
        return case["kind"] if case["kind"] in NOT_REQUESTS else None
    return None


def requests_of(relative, data) -> list[tuple[str, str, dict, object]]:
    """(origin, kind, case, expected) for every route request in one fixture."""
    out = []
    for path, node in _walk(data):
        for kind in request_kinds(node):
            case = {"kind": kind, **{f: deepcopy(node[f]) for f in REQUEST_FIELDS[kind]}}
            origin = relative + "".join(f"/{step}" for step in path)
            expected = node.get("expected") if "kind" in node else None
            out.append((origin, kind, case, expected if type(expected) is dict else None))
    return out


def _is_model(node) -> bool:
    return type(node) is dict and "domains" in node and "relations" in node


def usecase_requests() -> list[tuple[str, str, dict, object]]:
    """Each model of a use case against each environment of its directory that decodes it, as an `evaluate`
    request over the formulas of the directory's `.ve` documents that parse under that environment (the
    formula `top` when none does)."""
    from ve import Environment, FiniteModel, parse
    from ve.ast import document_to_data
    from ve.errors import VEError
    out = []
    for directory in sorted({p.parent for p in (ROOT / "usecases").rglob("*.json")}):
        envs = [(p, json.loads(p.read_text())) for p in sorted(directory.glob("*.json"))
                if excluded(str(p.relative_to(ROOT))) is None]
        envs = [(p, data) for p, data in envs if is_environment((), data)]
        models = [(p, json.loads(p.read_text())) for p in sorted(directory.rglob("*.json"))
                  if excluded(str(p.relative_to(ROOT))) is None]
        models = [(p, data) for p, data in models if _is_model(data)]
        documents = sorted(directory.rglob("*.ve"))
        for env_path, raw in envs:
            try:
                env = Environment(deepcopy(raw))
            except VEError:
                continue
            formulas = []
            for document in documents:
                try:
                    formulas += document_to_data(env, parse(env, document.read_text()))
                except VEError:
                    continue
            for model_path, model in models:
                try:
                    FiniteModel.from_dict(env, deepcopy(model))
                except VEError:
                    continue
                origin = f"{model_path.relative_to(ROOT)}@{env_path.name}"
                out.append((origin, "evaluate", {"kind": "evaluate", "environment": raw, "model": model,
                                                  "ast": formulas[:64] or [["top"]]}, None))
    return out


def requests() -> list[tuple[str, str, dict, object]]:
    """(origin, kind, case, expected) for every distinct route request: the fixtures' and the use cases'."""
    found = {}
    for relative, data in read_fixtures():
        for item in requests_of(relative, data):
            found.setdefault(canonical(item[2]), item)
    for item in usecase_requests():
        found.setdefault(canonical(item[2]), item)
    return list(found.values())


def wire_fixtures() -> list[str]:
    """The fixture files the `wire` surface reads: the wire-contract units' contracts and test inputs."""
    return [f for f in fixture_files() if fnmatch.fnmatchcase(f, "conformance/wire-contract/contracts/*.json")
            or f == "conformance/wire-contract/soft-norms@0-test-inputs.json"]


def readers(relative: str, data, usecase_origins=None) -> set[str]:
    """The surfaces that read a fixture file; `usecase_origins` are the origins of `usecase_requests()`."""
    out = set()
    if environments_of(relative, data):
        out.add("environment")
    if requests_of(relative, data) or any(origin.split("@")[0] == relative for origin in usecase_origins or ()):
        out.add("requests")
    if relative in wire_fixtures():
        out.add("wire")
    return out
