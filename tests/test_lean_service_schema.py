"""Service responses: the client's schemas, the Lean decoders and the Lean invariants.

Threat model (docs/spec/lean-service.md): the service is the semantic authority; the
client checks binding (nonce, mode, each result's position and case digest, the identity
fields the runners echo from the case) and well-formedness, and nothing else.

* Every genuine response of the service over a corpus with every mode and result kind
  (`tests/lean_service_corpus.py`) is accepted by the schemas and by `ve_response_decode`
  (`lean/ResponseDecode.lean`), and satisfies its Lean invariants: the content the runners
  guarantee and the client does not check (regenerated counts, distinct layers and
  conflict targets with their declared sorts, graph unfoldings, dependency orders, ...).
* Differential fuzz: mutations of those genuine responses (dropped, altered, retyped,
  enum-swapped, truncated and extra fields, at every depth, bindings included) are
  accepted by the schemas exactly when the Lean decoders accept them. Request-linked
  values are also mutated together with their request, so each value domain is compared
  on its own. Each of a list of schema weakenings disagrees with Lean on some mutation.
* Findings: each shape or binding finding of the mig1 rechecks is a scripted replacement
  of a genuine response that fails closed, after one retry, as `CheckerUnavailable`; each
  content finding is a corruption that keeps every binding, which the client accepts and
  a Lean invariant rejects. The service's norms content is also compared with Python's
  independent regeneration (`ve/norms.py`).
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import random
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import lean_build
from tests.lean_service_corpus import ERROR_REQUESTS, corpus
from tests.test_lean_service import fake
from ve.backends.lean_service import CheckerUnavailable, LeanService, case_digest, case_texts, request_context
from ve.backends.service_schema import DIRECTORY, MODES, Compiler, Context, Invalid, check_response

ROOT = Path(__file__).resolve().parents[1]
COMMON = json.loads((DIRECTORY / "common.json").read_text())["$defs"]


@pytest.fixture(scope="module")
def executables():
    bin_ = lean_build("ve_service", "ve_response_decode")
    return bin_ / "ve_service", bin_ / "ve_response_decode"


def _text(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def rebind(request, response):
    """The request's digests of its (possibly altered) cases, and the response's results
    bound to them: an altered request/response pair as the client and service would see it."""
    digests = [case_digest(_text(case)) for case in request["cases"]]
    if isinstance(response.get("results"), list):
        response = {**response, "results": [
            {**bound, "digest": digests[i]} if isinstance(bound, dict) and i < len(digests) else bound
            for i, bound in enumerate(response["results"])]}
    return {**request, "digests": digests}, response


def result(response, i):
    return response["results"][i]["result"]


@pytest.fixture(scope="module")
def genuine(executables):
    """[(mode, request, response)] from the real service, in 16-case requests."""
    service_executable, _ = executables
    exchanges = []
    with LeanService(service_executable, timeout=HANG_TIMEOUT) as service:
        for mode, cases in corpus().items():
            for start in range(0, len(cases), 16):
                chunk = cases[start:start + 16]
                text = _text(chunk)
                _, response = service.exchange(mode, text, len(chunk), timeout=HANG_TIMEOUT)
                request = {"id": response["id"], "mode": mode, "cases": chunk,
                           "digests": [case_digest(t) for t in case_texts(text)], "bytes": len(text.encode())}
                assert rebind(request, response) == (request, response)
                exchanges.append((mode, request, response))
        assert service.stats["retries"] == 0
    return exchanges


@pytest.fixture(scope="module")
def genuine_errors(executables):
    """[(mode, request, response)]: the service's request errors, each with the request as
    the client checks it (`request_context`); one cases text does not split into cases."""
    exchanges = []
    with LeanService(executables[0]) as service:
        for mode, text, count, budget in ERROR_REQUESTS:
            _, response = service.exchange(mode, text, count, budget=budget)
            assert response["status"] == "error"
            exchanges.append((mode, request_context(response["id"], mode, text, count), response))
        assert service.stats["retries"] == 0
    return exchanges


def error_items(genuine_errors, rng):
    """Mutations of the request errors, and each error against requests with other digests."""
    items = []
    for mode, request, response in genuine_errors:
        items.append((mode, request, mutations(response, rng, 0, 4)))
        digests = request["digests"]
        others = [None, [], ["0" * 64]] + ([digests[:-1], digests[::-1], digests + digests[-1:]]
                                           if digests else [])
        items += [(mode, {**request, "digests": other}, [response]) for other in others if other != digests]
    return items


def lean_verdicts(decoder, items, check="decode"):
    """ve_response_decode's verdict ("accept" or "reject: ...") for each (mode, request,
    response) under `check`: `decode` (the client's schemas) or `invariants`."""
    lines, sizes = [], []
    for mode, request, responses in items:
        lines.append(json.dumps({"check": check, "mode": mode, "request": request, "responses": responses}))
        sizes.append(len(responses))
    proc = subprocess.run([str(decoder)], input="\n".join(lines) + "\n", capture_output=True,
                          text=True, timeout=HANG_TIMEOUT)
    assert proc.returncode == 0, proc.stderr
    out = [json.loads(line) for line in proc.stdout.splitlines()]
    assert [len(x) if isinstance(x, list) else x for x in out] == sizes
    return [v for verdicts in out for v in verdicts]


def schema_verdict(mode, request, response):
    try:
        check_response(mode, response, request)
        return "accept"
    except Invalid as exc:
        return f"reject: {exc}"


def assert_agreement(decoder, items, lean=None):
    """items: [(mode, request, [response, ...])]; the verdicts must agree on every response."""
    lean = lean_verdicts(decoder, items) if lean is None else lean
    ours = [schema_verdict(mode, request, r) for mode, request, responses in items for r in responses]
    flat = [(mode, r) for mode, _, responses in items for r in responses]
    disagreements = [(mode, json.dumps(r)[:600], a, b) for (mode, r), a, b in zip(flat, ours, lean)
                     if a.startswith("accept") != b.startswith("accept")]
    assert not disagreements, f"{len(disagreements)} of {len(flat)} disagree; first: {disagreements[:5]}"
    return ours


def test_genuine_responses_are_accepted_by_schema_and_lean(genuine, executables):
    kinds = {(mode, case.get("kind", "evaluate") if isinstance(case, dict) else "?")
             for mode, request, _ in genuine for case in request["cases"]}
    for mode, kind in [("route", "admission"), ("route", "bundle"), ("route", "dependency-order"),
                       ("route", "background"), ("route", "label"), ("order", "surface"),
                       ("order", "certificate"), ("norms", "norms-conflict"),
                       ("norms", "norms-certificate"), ("norms", "admission")]:
        assert (mode, kind) in kinds
    statuses = {row.get("status", "ok") if "case_index" not in row else "case" for _, _, response in genuine
                for row in map(lambda bound: bound["result"], response["results"])}
    assert statuses == {"ok", "error", "case"}
    verdicts = assert_agreement(executables[1], [(m, q, [r]) for m, q, r in genuine])
    assert set(verdicts) == {"accept"}


def test_coverage_unit_binding_and_counts_agree_with_lean(executables, tmp_path):
    """The generated schema and Lean decoder both reject the review's invented ID and
    one-cell/zero-count mutants, including the other coverage sections."""
    from tests.test_alternatives_profile import source

    case = {"id": "coverage", "kind": "alt-elaborate", "environment": source(),
            "norms": [], "coverage_units": [{
                "id": "choice", "kind": "asserted", "support": "testimony",
                "content": ["binary", "available", ["const", "pull"], ["const", "r"]]}]}
    cases_text = _text([case])
    with LeanService(executables[0]) as service:
        _, response = service.exchange("alternatives", cases_text, 1)
    request = request_context(response["id"], "alternatives", cases_text, 1)
    good = result(response, 0)["coverage"]
    assert good["alternatives"]["alternatives_declared"][0]["unit"] == "choice"
    mutants = []
    for change in ("unit", "count", "type"):
        bad = deepcopy(response)
        coverage = result(bad, 0)["coverage"]
        if change == "unit":
            coverage["alternatives"]["alternatives_declared"][0]["unit"] = "invented"
        elif change == "count":
            coverage["residual"]["alternatives_declared"] = 0
        else:
            coverage["alternatives"]["alternatives_declared"][0]["unit"] = []
        mutants.append(bad)
    assert assert_agreement(executables[1], [("alternatives", request, [response, *mutants])]) == [
        "accept", *[schema_verdict("alternatives", request, bad) for bad in mutants]]
    assert all(schema_verdict("alternatives", request, bad).startswith("reject") for bad in mutants)
    for index, bad in enumerate(mutants):
        location = tmp_path / str(index)
        location.mkdir()
        _scripted_rejected(location, "alternatives", case,
                           deepcopy(result(response, 0)), deepcopy(result(bad, 0)))


def test_coverage_is_required_for_both_elaborate_modes(executables):
    """A covered request cannot turn into a valid response with no coverage section."""
    from tests.test_alternatives_profile import source
    from tests.test_risk_profile import risk_source

    for mode, kind, environment, document in (
        ("alternatives", "alt-elaborate", source(), None),
        ("risk", "risk-elaborate", risk_source(), {"norms": [], "units": []}),
    ):
        case = {"id": "coverage", "kind": kind, "environment": environment,
                "coverage_units": []}
        if document is None:
            case["norms"] = []
        else:
            case["document"] = document
        cases_text = _text([case])
        with LeanService(executables[0]) as service:
            _, response = service.exchange(mode, cases_text, 1)
        request = request_context(response["id"], mode, cases_text, 1)
        assert "coverage" in result(response, 0)
        assert schema_verdict(mode, request, response) == "accept"
        missing = deepcopy(response)
        del result(missing, 0)["coverage"]
        assert schema_verdict(mode, request, missing).startswith("reject")
        assert assert_agreement(executables[1], [(mode, request, [response, missing])]) == [
            "accept", schema_verdict(mode, request, missing)]


def test_every_coverage_cell_field_has_a_checked_shape(executables):
    """A genuine declared cell reduced to {unit} is invalid; so is every dropped,
    retyped, or unexpected member of each kind of emitted coverage cell."""
    from tests.test_alternatives_profile import source

    environment = source()
    environment["alternatives"]["outcomes"] = {"complete_by": "case annotator"}
    environment["vocabulary"]["constants"] = {
        "pull": {"sort": "action", "description": "pull"},
        "wait": {"sort": "action", "description": "wait"},
        "r": {"sort": "robot", "description": "r"},
        "h": {"sort": "harm", "description": "h"},
    }
    units = [
        {"id": name, "kind": "asserted", "support": "testimony",
         "content": ["binary", predicate, ["const", "pull"], ["const", second]]}
        for name, predicate, second in (
            ("choice", "available", "r"),
            ("outcome", "leads_to", "h"),
            ("cause", "causes", "h"),
        )]
    case = {"id": "coverage", "kind": "alt-elaborate", "environment": environment,
            "norms": [], "coverage_units": units}
    cases_text = _text([case])
    with LeanService(executables[0]) as service:
        _, response = service.exchange("alternatives", cases_text, 1)
    request = request_context(response["id"], "alternatives", cases_text, 1)
    sections = ("alternatives_declared", "counterfactual_leaves", "assumed_harm_free",
                "proximate_judgments")
    detail = result(response, 0)["coverage"]["alternatives"]
    assert all(detail[section] for section in sections)
    assert schema_verdict("alternatives", request, response) == "accept"
    mutants = []
    for section in sections:
        cell = detail[section][0]
        for field in cell:
            for change in ("drop", "retype"):
                bad = deepcopy(response)
                target = result(bad, 0)["coverage"]["alternatives"][section][0]
                if change == "drop":
                    del target[field]
                else:
                    target[field] = []
                mutants.append(bad)
        bad = deepcopy(response)
        result(bad, 0)["coverage"]["alternatives"][section][0]["unexpected"] = True
        mutants.append(bad)
    declared = deepcopy(response)
    result(declared, 0)["coverage"]["alternatives"]["alternatives_declared"] = [{"unit": "choice"}]
    mutants.append(declared)
    assert all(schema_verdict("alternatives", request, bad).startswith("reject") for bad in mutants)
    assert all(verdict.startswith("reject") for verdict in
               assert_agreement(executables[1], [("alternatives", request, mutants)]))


def test_genuine_responses_satisfy_the_lean_invariants(genuine, executables):
    """What the client leaves to the service holds on everything the service emits."""
    verdicts = lean_verdicts(executables[1], [(m, q, [r]) for m, q, r in genuine], "invariants")
    assert set(verdicts) == {"accept"}, [v for v in verdicts if v != "accept"][:5]


def test_genuine_request_errors_are_bound_and_accepted(genuine_errors, executables):
    """mig1d recheck: every request error echoes the request's mode and its case digests
    (`null` for a cases text that does not split), and the schemas and the Lean decoders
    accept each one against its request."""
    assert all(set(response) == {"id", "status", "mode", "digests", "error", "code"} and response["mode"] == mode
               and response["digests"] == request["digests"] for mode, request, response in genuine_errors)
    assert any(request["digests"] is None for _, request, _ in genuine_errors)
    assert any(request["digests"] and request["cases"] is None for _, request, _ in genuine_errors)
    items = [(m, q, [r]) for m, q, r in genuine_errors]
    assert set(assert_agreement(executables[1], items)) == {"accept"}
    assert set(lean_verdicts(executables[1], items, "invariants")) == {"accept"}


def test_request_errors_without_their_binding_are_rejected(genuine_errors, executables):
    """Dropping or altering the mode or the digests of a request error, or checking it
    against another request's digests, is rejected by the schemas and by Lean alike."""
    items = error_items(genuine_errors, random.Random(20260928))
    verdicts = assert_agreement(executables[1], items)
    flat = [(q, r) for _, q, responses in items for r in responses]
    for (request, response), verdict in zip(flat, verdicts):
        if not (isinstance(response, dict) and response.get("mode") == request["mode"]
                and response.get("digests", 0) == request["digests"]):
            assert verdict != "accept", (request, response)


# Mutations of genuine responses

STRINGS = sorted({*COMMON["atomic_kind"]["enum"], *COMMON["act"]["enum"], *COMMON["modality"]["enum"],
                  *COMMON["relation"]["enum"], *COMMON["generator"]["enum"],
                  "attributed", "hedged", "causal", "unformalised", "not-a-modality", "", "a b", "x",
                  "top", "not", "var", "const", "num", "lt", "add", "unary", "forall",
                  "ok", "error", "CONFLICT", "CONFLICT-FREE", "UNKNOWN", "0" * 64, "g" * 64, "A" * 64,
                  "00", "-0", "01", "7", "-7", "1" * 41, "InvalidModel(x)", "InvalidModel(literals",
                  "layer:norms:p", "asserted", "bridge:accepts(a,b)", "readings:s@01:all",
                  "readings:s@1:all", "background:profile", "background:other", "t" * 65})
VALUES = [None, True, False, 0, 1, -1, 2, "", "x", [], {}, [True], ["top"], {"extra": 1}]


def _nodes(value, path=()):
    yield path, value
    if isinstance(value, dict):
        for k, v in value.items():
            yield from _nodes(v, path + (k,))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _nodes(v, path + (i,))


def _replace(root, path, new):
    if not path:
        return new
    copy = deepcopy(root)
    node = copy
    for step in path[:-1]:
        node = node[step]
    node[path[-1]] = new
    return copy


def _mutants(value, rng):
    """Local alterations of one JSON node."""
    out = [rng.choice(VALUES), rng.choice(VALUES)]
    if isinstance(value, dict):
        for k in value:
            out.append({x: y for x, y in value.items() if x != k})
        out.append({**value, "extra": 1})
    elif isinstance(value, list):
        out += [[], value[:-1], value[1:], value + value[-1:], value[::-1], value[:len(value) // 2],
                value + [None]]
        if value and isinstance(value[0], str):
            out += [[s] + value[1:] for s in rng.sample(STRINGS, 6)]
    elif isinstance(value, str):
        out += rng.sample(STRINGS, 8) + [value + "x", value[:-1], value.upper()]
    elif type(value) is bool:
        out += [not value, int(value), None]
    elif type(value) is int:
        out += [value + 1, value - 1, -1, 0, True, str(value), 1.5]
    return [m for m in out if not (type(m) is type(value) and m == value)]


def mutations(response, rng, paths, per_path):
    """Up to `paths` nodes of the response, each altered `per_path` ways; every binding and
    every top-level field of every result is among them."""
    nodes = [p for p, _ in _nodes(response)]
    shallow = [p for p in nodes if len(p) <= 4]
    deep = [p for p in nodes if len(p) > 4]
    rng.shuffle(deep)
    out = []
    for path in shallow + deep[:max(0, paths - len(shallow))]:
        node = response
        for step in path:
            node = node[step]
        mutants = _mutants(node, rng)
        out += [_replace(response, path, m) for m in rng.sample(mutants, min(per_path, len(mutants)))]
    return out


def singles(genuine):
    """Each genuine result as the response to a request with only its case."""
    for mode, request, response in genuine:
        for case, digest, bound in zip(request["cases"], request["digests"], response["results"]):
            size = len(_text([case]).encode())
            yield (mode, {**request, "cases": [case], "digests": [digest], "bytes": size},
                   {**response, "results": [{**bound, "index": 0}], "counts": {
                       "cases": 1, "bytes": size, "errors": int(bound["result"].get("status") == "error")}})


def _key(value):
    return json.dumps(value, sort_keys=True)


def joint_mutations(request, response, rng, limit):
    """Request-linked alterations: a result value equal to values of its case (ids, labels,
    kinds, meaning ids, node names and ASTs, ...) is replaced together with them, and an
    array as long as a case array is truncated together with it."""
    out = []
    for index, (case, bound) in enumerate(zip(request["cases"], response.get("results", []))):
        row = bound.get("result") if isinstance(bound, dict) else None
        if not isinstance(case, dict) or not isinstance(row, dict):
            continue
        by_value, by_length = {}, {}
        for path, value in _nodes(case):
            if path:
                by_value.setdefault(_key(value), []).append(path)
                if isinstance(value, list) and value:
                    by_length.setdefault(len(value), []).append(path)
        candidates = []
        for path, value in _nodes(row):
            if not path or type(value) in (bool, int) or value is None:
                continue
            for case_path in by_value.get(_key(value), []):
                candidates += [("value", path, case_path, m) for m in _mutants(value, rng)]
            if isinstance(value, list) and value:
                for case_path in by_length.get(len(value), []):
                    candidates += [("length", path, case_path, k) for k in (0, len(value) - 1)]
        rng.shuffle(candidates)
        for how, path, case_path, change in candidates[:limit]:
            req, res = deepcopy(request), deepcopy(response)
            row_node, case_node = res["results"][index]["result"], req["cases"][index]
            if how == "value":
                row_node, case_node = _replace(row_node, path, change), _replace(case_node, case_path, change)
            else:
                old_row, old_case = row_node, case_node
                for step in path:
                    old_row = old_row[step]
                for step in case_path:
                    old_case = old_case[step]
                row_node = _replace(row_node, path, old_row[:change])
                case_node = _replace(case_node, case_path, old_case[:change])
            res["results"][index]["result"], req["cases"][index] = row_node, case_node
            out.append(rebind(req, res))
    return out


def request_mutations(request, response, rng, limit):
    """The same results against altered requests (kinds, ids, linked fields), rebound to
    them so that each linked value is compared on its own."""
    out = []
    for index, case in enumerate(request["cases"]):
        nodes = [(p, v) for p, v in _nodes(case) if len(p) <= 3]
        rng.shuffle(nodes)
        for path, value in nodes[:4]:
            for mutant in _mutants(value, rng)[:3]:
                req = deepcopy(request)
                req["cases"][index] = _replace(case, path, mutant)
                out.append(rebind(req, response))
    rng.shuffle(out)
    return out[:limit]


@pytest.fixture(scope="module")
def fuzz(genuine, genuine_errors, executables):
    """[(mode, request, [response])]: mutations of every genuine response and of each of its
    results alone, joint request/result mutations, altered requests and the value-domain
    probes below; with Lean's verdicts."""
    rng = random.Random(20260928)
    items = [(mode, request, mutations(response, rng, 0, 1)) for mode, request, response in genuine]
    for mode, request, response in singles(genuine):
        items.append((mode, request, mutations(response, rng, 14, 3)))
        items += [(mode, req, [res]) for req, res in joint_mutations(request, response, rng, 8)]
        items += [(mode, req, [res]) for req, res in request_mutations(request, response, rng, 6)]
    items += kind_items(genuine) + label_items(genuine) + depth_items(genuine)
    items += error_items(genuine_errors, rng)
    return items, lean_verdicts(executables[1], items)


# Each field dropped, emptied ("" [] {}), nulled and retyped (7, true, a string): build checklist line 4.
_DROP = object()
FIELD_FAULTS = {"drop": _DROP, "empty-text": "", "empty-array": [], "empty-object": {}, "null": None,
                "number": 7, "true": True, "text": "x"}


def field_faults(response):
    """Every field of `response` (a list through its first element, results to depth 4 below the
    bound entry) dropped, emptied, nulled and retyped."""
    def nodes(value, path=()):
        yield path, value
        if len(path) < 7:
            if isinstance(value, dict):
                for key, item in value.items():
                    yield from nodes(item, path + (key,))
            elif isinstance(value, list) and value:
                yield from nodes(value[0], path + (0,))
    out = []
    for path, value in nodes(response):
        if not path:
            continue
        for new in FIELD_FAULTS.values():
            if new is _DROP:
                if isinstance(path[-1], str):
                    copy = deepcopy(response)
                    node = copy
                    for step in path[:-1]:
                        node = node[step]
                    del node[path[-1]]
                    out.append(copy)
            elif not (type(new) is type(value) and new == value):
                out.append(_replace(response, path, new))
    return out


def test_every_field_dropped_emptied_nulled_and_retyped_agrees_with_lean(genuine, genuine_errors, executables):
    """Table-driven over one genuine response of each mode, case kind and outcome (and every request
    error): the schema accepts a mutant exactly when the Lean decoders do, and refuses every drop or
    null of the binding (nonce, mode, index, digest, a rejection's code and text)."""
    shapes = {}
    for mode, request, response in singles(genuine):
        case, row = request["cases"][0], response["results"][0]["result"]
        kind = case.get("kind", "evaluate") if isinstance(case, dict) else "?"
        shapes.setdefault((mode, kind, row.get("status"), "case_index" in row), (mode, request, response))
    items = [(mode, request, field_faults(response)) for mode, request, response in
             [*shapes.values(), *genuine_errors]]
    verdicts = assert_agreement(executables[1], items)
    assert 0 < sum(v == "accept" for v in verdicts) < len(verdicts) // 10
    for mode, request, response in [*shapes.values(), *genuine_errors]:
        bound = response["results"][0] if response.get("status") != "error" else None
        binding = [("id",), ("mode",)] + ([("results", 0, "index"), ("results", 0, "digest")] if bound else [])
        if bound is None or bound["result"].get("status") == "error":
            binding += [("results", 0, "code"), ("results", 0, "result", "error")] if bound else [("code",), ("error",)]
        for path in binding:
            for new in (None, ""):
                assert schema_verdict(mode, request, _replace(response, path, new)) != "accept", (mode, path, new)


def test_mutated_genuine_responses_agree_with_lean_decoders(fuzz, executables):
    items, lean = fuzz
    verdicts = assert_agreement(executables[1], items, lean)
    assert 0 < sum(v == "accept" for v in verdicts) < len(verdicts)


@pytest.mark.parametrize("weaken", [
    "digest", "index", "modality", "act", "relation", "token", "kind-fuel", "formula-fuel",
    "values-count", "kinds-link", "lemmas-link", "checked-count", "label", "valid-false",
    "error-id", "generated-cap", "request-error-mode", "request-error-digests"])
def test_fuzz_detects_a_weakened_schema(tmp_path, fuzz, weaken):
    """The differential harness has teeth: each weakening of the schemas, bindings
    included, disagrees with the Lean decoders on some mutation (and so does the decoders'
    depth cap put back on generated formulas)."""
    for path in DIRECTORY.glob("*.json"):
        shutil.copy(path, tmp_path / path.name)
    def edit(name, change):
        document = json.loads((tmp_path / name).read_text())
        change(document["$defs"])
        (tmp_path / name).write_text(json.dumps(document))
    common = "common.json"
    {"digest": lambda: edit("envelope.json", lambda d: d["bound"]["properties"]["digest"].pop("x-digest")),
     "index": lambda: edit("envelope.json", lambda d: d["bound"]["properties"]["index"].pop("x-index")),
     "modality": lambda: edit(common, lambda d: d["modality"]["enum"].append("not-a-modality")),
     "act": lambda: edit(common, lambda d: d["act"]["enum"].append("shouts")),
     "relation": lambda: edit(common, lambda d: d["relation"]["enum"].append("since")),
     "token": lambda: edit(common, lambda d: d["token"].update(pattern=".*")),
     "kind-fuel": lambda: edit(common, lambda d: d["kind"]["x-fuel"].update(limit=256)),
     "formula-fuel": lambda: edit(common, lambda d: d["fol_formula"]["x-fuel"].update(limit=256)),
     "values-count": lambda: edit(common, lambda d: d["values"].pop("x-length")),
     "kinds-link": lambda: edit(common, lambda d: d["admission"]["properties"]["kinds"].pop("x-equals")),
     "lemmas-link": lambda: edit("route.json", lambda d: d["bundle"]["properties"]["lemmas"].pop("x-equals")),
     "checked-count": lambda: edit("route.json", lambda d: d["bundle"]["properties"]["checked"].pop("x-count")),
     "label": lambda: edit(common, lambda d: d["label"].update(pattern=".*")),
     "valid-false": lambda: edit(common, lambda d: d["error_valid"]["properties"].update(valid={"type": "boolean"})),
     "error-id": lambda: edit(common, lambda d: d["error"]["properties"]["id"].pop("x-echo")),
     "generated-cap": lambda: edit(common, lambda d: d["generated_formula"].update(
         {"x-fuel": {"counter": "generated_formula", "limit": 64}})),
     "request-error-mode": lambda: edit("envelope.json", lambda d: d["error"]["properties"]["mode"].pop("x-equals")),
     "request-error-digests": lambda: edit("envelope.json",
                                           lambda d: d["error"]["properties"]["digests"].pop("x-equals")),
     }[weaken]()
    compiler = Compiler(tmp_path)
    rows = {mode: compiler.ref(f"{mode}.json", "#/row") for mode in MODES}
    response = compiler.ref("envelope.json", "#/response")
    items, lean = fuzz
    def accepts(mode, request, r):
        try:
            response[0](r, Context(request, rows=rows[mode][0]), {})
            return True
        except Invalid:
            return False
    ours = [accepts(mode, request, r) for mode, request, responses in items for r in responses]
    assert any(a != (b == "accept") for a, b in zip(ours, lean))


def _linked(genuine, mode, kind):
    return [(request, response, i) for m, request, response in genuine if m == mode
            for i, case in enumerate(request["cases"])
            if isinstance(case, dict) and case.get("kind") == kind
            and result(response, i).get("status") == "ok"]


KINDS = ["asserted", "meta", "not-a-kind", "", ["hedged", "likely", "asserted"],
         ["hedged", "not-a-modality", "asserted"], ["hedged", "could", ["hedged", "maybe", "norm"]],
         ["attributed", "bob", "says", "asserted"], ["attributed", "bob", "shouts", "asserted"],
         ["attributed", "bob smith", "says", "asserted"], ["attributed", "", "says", "asserted"],
         ["attributed", "b" * 64, "says", "asserted"], ["attributed", "b" * 65, "says", "asserted"],
         ["causal", "because", "asserted", "norm"], ["causal", "since", "asserted", "norm"],
         ["causal", "in order to", "asserted"], ["unformalised", "rhetoric"], ["unformalised", ""],
         ["unformalised", "two words"], ["unformalised", "é"], ["hedged", "likely"], ["norm"], [],
         ["hedged", 1, "asserted"], ["hedged", "likely", "asserted", "extra"], 7, None]

def _nested_kind(depth):
    kind = "asserted"
    for _ in range(depth - 1):
        kind = ["hedged", "likely", kind]
    return kind


def kind_items(genuine):
    """Unit kinds are linked to the request; setting both sides to one value compares
    the kind grammar itself (enumerations, tokens, arity, fuel 16)."""
    items = []
    for mode in ("route", "norms"):
        for request, response, i in _linked(genuine, mode, "admission")[:3]:
            for kind in KINDS + [_nested_kind(16), _nested_kind(17)]:
                req = deepcopy(request)
                req["cases"][i]["document"]["units"][0]["kind"] = kind
                res = deepcopy(response)
                result(res, i)["kinds"][0] = kind
                req, res = rebind(req, res)
                items.append((mode, req, [res]))
    return items


def test_kind_domain_agrees_with_decode_kind(genuine, executables):
    verdicts = assert_agreement(executables[1], kind_items(genuine))
    assert "accept" in verdicts and any(v != "accept" for v in verdicts)


LABELS = ["asserted", "bridge:accepts(a,u1)", "bridge:accepts(a,u1,x)", "bridge:accepts(a b,u)",
          "background:flags", "background:profile", "background:other", "cite:b/l", "cite:b/l/m",
          "open:t", "open:", "readings:s@0:all", "readings:s@1:2", "readings:s@01:2",
          "readings:s@1:02", "readings:s@1", "readings:s@x:1", "narrowing:n", "narrowing:" + "n" * 65,
          "layer:norms:p", "", "cite:" + "b" * 64 + "/l"]


def label_items(genuine):
    items = []
    for request, response, i in _linked(genuine, "route", "label")[:2]:
        for label in LABELS:
            req = deepcopy(request)
            req["cases"][i]["label"] = label
            res = deepcopy(response)
            result(res, i)["label"] = label
            req, res = rebind(req, res)
            items.append(("route", req, [res]))
    return items


def test_label_domain_agrees_with_parse_label(genuine, executables):
    verdicts = assert_agreement(executables[1], label_items(genuine))
    assert "accept" in verdicts and any(v != "accept" for v in verdicts)


def _deep_formula(depth, leaf):
    formula = leaf
    for _ in range(depth - 1):
        formula = ["not", formula]
    return formula


def _deep_term(depth):
    term = ["num", "1"]
    for _ in range(depth - 1):
        term = ["add", term, ["var", 0]]
    return term


GENERATED_DEPTHS = [(depth, ["top"]) for depth in (63, 64, 65, 69, 3000)] + [(3000, ["nope"]), (65, ["top", 1])]


def depth_items(genuine):
    """Formula depth: generated formulas (Background, norms premises and targets, English
    parses) at any depth, malformed deep ones rejected; claims, which the runners decode
    from the request, at most 64; order surface formulas and terms at most 64."""
    items = []
    for request, response, i in [x for x in _linked(genuine, "route", "background")
                                 if result(x[1], x[2])["premises"]][:1]:
        for depth, leaf in GENERATED_DEPTHS:
            res = deepcopy(response)
            for field in ("background", "premises"):
                result(res, i)[field][0] = _deep_formula(depth, leaf)
            items.append(("route", request, [res]))
    for request, response, i in _linked(genuine, "norms", "norms-elaborate")[:1]:
        for field in ("background", "premises", "conflict_targets"):
            if result(response, i)[field]:
                for depth, leaf in GENERATED_DEPTHS:
                    res = deepcopy(response)
                    result(res, i)[field][0]["ast"] = _deep_formula(depth, leaf)
                    items.append(("norms", request, [res]))
    for mode, request, response in genuine:
        rows = [(k, j) for k, bound in enumerate(response["results"])
                if isinstance(bound["result"].get("results"), list)
                for j, item in enumerate(bound["result"]["results"]) if item.get("parsed")]
        for k, j in rows[:1]:
            for depth, leaf in GENERATED_DEPTHS:
                res = deepcopy(response)
                result(res, k)["results"][j]["parsed"][0] = _deep_formula(depth, leaf)
                items.append((mode, request, [res]))
    for request, response, i in [x for x in _linked(genuine, "route", "admission")
                                 if x[0]["cases"][x[2]]["id"] == "shared-leaves"]:
        for depth in (63, 64, 65, 3000):
            formula = _deep_formula(depth, ["top"])
            req, res = deepcopy(request), deepcopy(response)
            for node in req["cases"][i]["document"]["graph"]["nodes"]:
                node["ast"] = formula if node["name"] == "a" else node["ast"]
            report = result(res, i)["report"]
            for claim in report["assumptions"]:
                claim["ast"] = formula if claim["name"] == "a" else claim["ast"]
            req, res = rebind(req, res)
            items.append(("route", req, [res]))
    for request, response, i in _linked(genuine, "order", "surface")[:1]:
        for formula in [_deep_formula(d, ["lt", ["num", "0"], ["num", "1"]]) for d in (64, 65)] + [
                ["lt", _deep_term(d), ["num", "1"]] for d in (63, 64, 65)] + [
                ["lt", ["num", n], ["num", "1"]] for n in ("0", "-1", "00", "-0", "+1", "1_0", "٣",
                                                         "9" * 40, "9" * 41, "-" + "9" * 39, "-" + "9" * 40)]:
            res = deepcopy(response)
            result(res, i)["ast"] = [formula]
            items.append(("order", request, [res]))
    return items


def test_formula_depth_and_numerals_agree_with_lean_decoders(genuine, executables):
    verdicts = assert_agreement(executables[1], depth_items(genuine))
    assert "accept" in verdicts and any(v != "accept" for v in verdicts)


# Shape and binding findings of the mig1 rechecks: scripted replacements of genuine
# responses fail closed after exactly one retry.

def _scripted_rejected(tmp_path, mode, case, good, bad):
    """The scripted service answers `good` (accepted, no retry), then `bad`, which must
    fail closed after exactly one retry. The stand-in binds each row to its case."""
    def answer(row):
        return {"id": "__nonce__", "status": "ok", "mode": mode, "results": [row],
                "counts": {"cases": 1, "bytes": "__bytes__", "errors": int(row.get("status") == "error")}}
    marker = tmp_path / "marker"
    marker.write_text(json.dumps(answer(good)))
    with LeanService(fake(tmp_path, "scripted"), allow_unlisted_build=True) as service:
        assert service.run(mode, [case]) == [good]
        assert service.stats["retries"] == 0
        marker.write_text(json.dumps(answer(bad)))
        with pytest.raises(CheckerUnavailable, match="malformed response"):
            service.run(mode, [case])
        assert service.stats["retries"] == 1


def _genuine_row(genuine, mode, kind, predicate=lambda case, row: True):
    for request, response, i in _linked(genuine, mode, kind):
        case, row = request["cases"][i], result(response, i)
        if predicate(case, row):
            return deepcopy(case), deepcopy(row)
    raise AssertionError(f"no genuine {mode} {kind} result")


@pytest.mark.parametrize("mode", ["route", "norms"])
@pytest.mark.parametrize("kind", [["hedged", "not-a-modality", "asserted"],
                                  ["attributed", "bob", "shouts", "asserted"],
                                  ["causal", "since", "asserted", "asserted"],
                                  ["unformalised", ""],
                                  ["hedged", "not-a-modality", ["attributed", "bob", "says", "asserted"]]])
def test_admission_kinds_outside_lean_decoder_fail_closed(tmp_path, genuine, mode, kind):
    case, row = _genuine_row(genuine, mode, "admission", lambda c, r: len(r["kinds"]) >= 1)
    bad = deepcopy(row)
    bad["kinds"][-1] = kind
    _scripted_rejected(tmp_path, mode, case, row, bad)


@pytest.mark.parametrize("mode", ["route", "norms"])
@pytest.mark.parametrize("field,truncated", [
    ("bundle", {"checked": 0, "lemmas": []}),
    ("bundle-short", None),
    ("admission", {"kinds": []}),
    ("admission-short", None),
])
def test_truncated_request_linked_results_fail_closed(tmp_path, genuine, mode, field, truncated):
    """Results the runners echo from the request (a bundle's lemma ids, an admission's unit
    kinds) are bindings: truncating them fails closed."""
    kind = field.removesuffix("-short")
    size = {"bundle": ("lemmas", 3), "admission": ("kinds", 4)}[kind]
    case, row = _genuine_row(genuine, mode, kind, lambda c, r: len(r[size[0]]) >= size[1])
    bad = deepcopy(row)
    if truncated is None:
        bad[size[0]] = bad[size[0]][:-1]
        if kind == "bundle":
            bad["checked"] = len(bad["lemmas"])
    else:
        bad.update(truncated)
    _scripted_rejected(tmp_path, mode, case, row, bad)


@pytest.mark.parametrize("mode", ["route", "norms"])
def test_evaluation_of_fewer_formulas_fails_closed(tmp_path, genuine, mode):
    """One value per requested formula is a binding."""
    case, row = _genuine_row(genuine, "route", "evaluate", lambda c, r: bool(c.get("ast")))
    case["ast"] = case["ast"][:1]
    good = {**row, "values": row["values"][:1]}
    _scripted_rejected(tmp_path, mode, case, good, {**good, "values": []})


# Content findings: corruptions that keep every binding. Directive 3: the client accepts
# them (it does not re-derive semantics); a Lean invariant rejects each, and every genuine
# response satisfies the invariants (test_genuine_responses_satisfy_the_lean_invariants).

def _dup_first(values):
    """The list with its first element in every position: the length is kept, every other
    element is lost."""
    return [values[0]] * len(values)


def _swap(values):
    return values[1:2] + values[:1] + values[2:]


def _set_sorts(sorts, which=None):
    def change(row, case):
        targets = deepcopy(row["conflict_targets"])
        for k, target in enumerate(targets):
            if which is None or k == which:
                target["sorts"] = sorts
        return {**row, "conflict_targets": targets}, case
    return change


def _row_change(change):
    return lambda row, case: (change(row), case)


def _assumptions(change):
    def edit(row, case):
        nodes = {n["name"]: {k: n[k] for k in ("name", "ast", "label") if k in n}
                 for n in case["document"]["graph"]["nodes"]}
        bad = deepcopy(row)
        bad["report"]["assumptions"] = change(row["report"]["assumptions"], nodes)
        return bad, case
    return edit


def _empty_document(row, case):
    return {**row, "values": []}, {**case, "ast": []}


# name: (mode, request kind, case id or None, change(row, case) -> (row, case))
CONTENT = {
    # mig1c-looprecheck2 B: omitted targets disguised as duplicates.
    "c2-targets-all-permitted": ("norms", "norms-conflict", "c2",
                                 _row_change(lambda r: {**r, "targets": ["permitted"] * 3})),
    "conflict-target-duplicated-in-place": ("norms", "norms-conflict", "c2",
                                            _row_change(lambda r: {**r, "targets": r["targets"][:1] * 2 + r["targets"][2:]})),
    "conflict-targets-reordered": ("norms", "norms-conflict", "c2",
                                   _row_change(lambda r: {**r, "targets": _swap(r["targets"])})),
    "witness-targets-substituted": ("norms", "norms-conflict", "w0",
                                    _row_change(lambda r: {**r, "targets": [r["target"], r["target"]]})),
    "elaboration-order-duplicated": ("norms", "norms-elaborate", "e2",
                                     _row_change(lambda r: {**r, "order": _dup_first(r["order"])})),
    "elaboration-premises-duplicated": ("norms", "norms-elaborate", "e2",
                                        _row_change(lambda r: {**r, "premises": _dup_first(r["premises"])})),
    "elaboration-targets-duplicated": ("norms", "norms-elaborate", "e2",
                                       _row_change(lambda r: {**r, "conflict_targets": _dup_first(r["conflict_targets"])})),
    "elaboration-targets-renamed": ("norms", "norms-elaborate", "e-literals", _row_change(lambda r: {
        **r, "conflict_targets": [{**t, "target": r["conflict_targets"][0]["target"]} for t in r["conflict_targets"]]})),
    # mig1c-looprecheck2 B: target sorts truncated.
    "target-sorts-emptied": ("norms", "norms-elaborate", "e2", _set_sorts([])),
    "first-target-sorts-emptied": ("norms", "norms-elaborate", "e2", _set_sorts([], 0)),
    "pair-target-sorts-emptied": ("norms", "norms-elaborate", "e-literals", _set_sorts([], 2)),
    "target-sorts-substituted": ("norms", "norms-elaborate", "e2", _set_sorts(["other"], 1)),
    "target-sorts-extended": ("norms", "norms-elaborate", "e2", _set_sorts(["act", "act"], 0)),
    # mig1c-looprecheck1 A: admission assumptions erased or altered (route and norms).
    **{f"{mode}-assumptions-{name}": (mode, "admission", case_id, _assumptions(change))
       for mode in ("route", "norms")
       for name, case_id, change in [
           ("emptied", "bridge-background", lambda a, n: []),
           ("emptied-shared", "shared-leaves", lambda a, n: []),
           ("drop-last", "shared-leaves", lambda a, n: a[:-1]),
           ("drop-first", "shared-leaves", lambda a, n: a[1:]),
           ("duplicate", "shared-leaves", lambda a, n: a + a[:1]),
           ("reorder", "shared-leaves", lambda a, n: _swap(a)),
           ("substitute", "shared-leaves", lambda a, n: [n["b"]] + a[1:]),
           ("deduction", "shared-leaves", lambda a, n: [n["mid"]] + a[3:])]},
    # mig1c-looprecheck1 B: regenerated lists truncated.
    **{f"{mode}-background-{name}": (mode, "background", "defs-background", _row_change(change))
       for mode in ("route", "norms")
       for name, change in [
           ("emptied", lambda r: {**r, "background": [], "premises": [], "generators": []}),
           ("drop-definition", lambda r: {k: v[1:] if isinstance(v, list) else v for k, v in r.items()}),
           ("drop-literal", lambda r: {k: v[:-1] if isinstance(v, list) else v for k, v in r.items()}),
           ("relabel", lambda r: {**r, "generators": ["definitions"] * len(r["generators"])}),
           ("premises-differ", lambda r: {**r, "premises": r["premises"][::-1]})]},
    **{f"elaboration-{case_id}-{'-'.join(fields)}-{how}": (
        "norms", "norms-elaborate", case_id,
        _row_change(lambda r, fields=fields, how=how: {**r, **{f: [] if how == "emptied" else r[f][:-1]
                                                              for f in fields}}))
       for case_id in ("e2", "e-literals")
       for fields in [("order",), ("premises",), ("conflict_targets",), ("background",),
                      ("order", "premises", "conflict_targets")]
       for how in ("emptied", "drop-last")},
    **{f"{mode}-{kind}-{field}-{name}": (mode, kind, case_id, _row_change(change))
       for mode, kind, field, case_id in [
           ("route", "certificate", "background", "data-definition-certificate"),
           ("norms", "certificate", "background", "defs-certificate-uses-definitions"),
           ("norms", "norms-certificate", "layers", "certificate"),
           ("norms", "norms-certificate", "background", "certificate")]
       for name, change in [("plus-one", lambda r, f=field: {**r, f: r[f] + 1}),
                            ("minus-one", lambda r, f=field: {**r, f: max(r[f] - 1, 0) if r[f] else 1})]},
    "c2-targets-emptied": ("norms", "norms-conflict", "c2", _row_change(lambda r: {**r, "targets": []})),
    "c2-targets-drop-last": ("norms", "norms-conflict", "c2", _row_change(lambda r: {**r, "targets": r["targets"][:-1]})),
    # Earlier rechecks: dependency orders, empty documents and parses, verdict details.
    **{f"{mode}-dependency-order-{name}": (mode, "dependency-order", None, _row_change(change))
       for mode in ("route", "norms")
       for name, change in [("emptied", lambda r: {**r, "order": []}),
                            ("drop-last", lambda r: {**r, "order": r["order"][:-1]}),
                            ("duplicated", lambda r: {**r, "order": _dup_first(r["order"])})]},
    **{f"{mode}-empty-document-values": (mode, "evaluate", None, _empty_document) for mode in ("route", "norms")},
    "empty-surface-parse": ("order", "surface", None, _row_change(lambda r: {**r, "ast": []})),
    "evaluate-conjunction-flipped": ("evaluate", None, None, _row_change(lambda r: {**r, "value": not r["value"]})),
    "conflict-free-with-detail": ("norms", "norms-conflict", "c2", _row_change(lambda r: {**r, "detail": "stale"})),
    "english-checked-without-rendering": ("english", None, None, _row_change(lambda r: {
        **r, "results": [{**r["results"][0], "checked": True, "rendered": None}] + r["results"][1:]})),
    "route-generator-not-the-messages": ("route", "evaluate", "invalid-model", _row_change(lambda r: {
        **r, "generator": "other"})),
}


def _content_item(genuine, name):
    mode, kind, case_id, change = CONTENT[name]
    for m, request, response in genuine:
        if m != mode:
            continue
        for i, case in enumerate(request["cases"]):
            row = result(response, i)
            if not isinstance(case, dict) or (kind is not None and case.get("kind", "evaluate") != kind):
                continue
            if case_id is not None and case.get("id") != case_id:
                continue
            if case_id is None and (row.get("status", "ok") != "ok" or "case_index" in row
                                    or (mode == "evaluate" and "kind" in case)
                                    or (kind == "dependency-order" and len(row["order"]) < 2)
                                    or (mode == "english" and not row.get("results"))
                                    or (kind == "evaluate" and not row.get("values"))):
                continue
            bad_row, bad_case = change(deepcopy(row), deepcopy(case))
            assert bad_row != row, name
            req, res = deepcopy(request), deepcopy(response)
            req["cases"][i], res["results"][i]["result"] = bad_case, bad_row
            req, res = rebind(req, res)
            return mode, req, res
    raise AssertionError(f"no genuine result for {name}")


@pytest.fixture(scope="module")
def content(genuine, executables):
    """{name: (mode, request, response, decode verdict, invariants verdict)}."""
    items = {name: _content_item(genuine, name) for name in CONTENT}
    batch = [(mode, request, [response]) for mode, request, response in items.values()]
    decoded = lean_verdicts(executables[1], batch)
    checked = lean_verdicts(executables[1], batch, "invariants")
    return {name: (*item, d, c) for (name, item), d, c in zip(items.items(), decoded, checked)}


@pytest.mark.parametrize("name", list(CONTENT))
def test_binding_preserving_content_is_left_to_the_service(content, name):
    """The client (its schemas, and the Lean decoding of them) accepts the corruption, and
    a Lean invariant, which every genuine response satisfies, rejects it."""
    mode, request, response, decoded, checked = content[name]
    assert schema_verdict(mode, request, response) == "accept"
    assert decoded == "accept"
    assert checked.startswith("reject"), checked


@pytest.mark.parametrize("name", ["c2-targets-all-permitted", "target-sorts-emptied"])
def test_client_accepts_the_recheck2_reproducers_with_no_retry(tmp_path, genuine, name):
    """mig1c-looprecheck2: the two content reproducers keep every binding. The client
    accepts them with no retry, as documented; the service never emits them (the Lean
    invariants above, and parity with Python's regeneration below)."""
    mode, kind, case_id, change = CONTENT[name]
    case, row = _genuine_row(genuine, mode, kind, lambda c, r: c["id"] == case_id)
    bad, _ = change(deepcopy(row), case)
    (tmp_path / "marker").write_text(json.dumps({"id": "__nonce__", "status": "ok", "mode": mode, "results": [bad],
                                                 "counts": {"cases": 1, "bytes": "__bytes__", "errors": 0}}))
    with LeanService(fake(tmp_path, "scripted"), allow_unlisted_build=True) as service:
        assert service.run(mode, [case]) == [bad]
        assert service.stats["retries"] == 0


def test_service_norms_content_matches_python_regeneration(executables):
    """Parity for norms content the client does not check: on the three-way corpus, the
    service's layers, premises and conflict targets (names, argument sorts and formulas)
    are Python's independent regeneration (ve/norms.py), and every response satisfies the
    Lean invariants."""
    from ve.ast import _to_data, formula_to_data
    from tests.test_norms_three_way import corpus as norms_corpus, lean_case, pair_corpus
    docs = [*norms_corpus(160), *pair_corpus(60)]
    cases = [lean_case(i, doc) for i, doc in enumerate(docs)]
    text = _text(cases)
    with LeanService(executables[0], timeout=HANG_TIMEOUT) as service:
        _, response = service.exchange("norms", text, len(cases), timeout=HANG_TIMEOUT)
        assert service.stats["retries"] == 0
    for i, (doc, bound) in enumerate(zip(docs, response["results"], strict=True)):
        got = bound["result"]
        assert got["status"] == "ok", (i, got)
        assert got["order"] == list(doc.order), i
        assert got["premises"] == [{"label": label, "ast": formula_to_data(doc.env, ast)}
                                   for label, ast in doc.premises()], i
        assert got["conflict_targets"] == [{"target": target, "sorts": list(sorts), "ast": _to_data(ast)}
                                           for target, sorts, ast in doc.conflict_targets()], i
    assert any(len(bound["result"]["conflict_targets"]) >= 3 for bound in response["results"])
    request = {"id": response["id"], "mode": "norms", "cases": cases,
               "digests": [case_digest(t) for t in case_texts(text)], "bytes": len(text.encode())}
    assert lean_verdicts(executables[1], [("norms", request, [response])], "invariants") == ["accept"]


def test_order_surface_of_zero_less_than_one_is_nonempty(executables):
    env = next(c for c in corpus()["order"] if isinstance(c, dict) and c.get("kind") == "surface")
    with LeanService(executables[0]) as service:
        [row] = service.run("order", [{**env, "id": "z", "source": "0 < 1.\n"}])
        [empty] = service.run("order", [{**env, "id": "e", "source": ""}])
    assert row["status"] == "ok" and row["ast"] == [["lt", ["num", "0"], ["num", "1"]]]
    assert empty["status"] == "error"


def _depth(formula):
    """Formula nesting depth (terms not counted), without recursion."""
    deepest, pending = 0, [(formula, 1)]
    while pending:
        node, depth = pending.pop()
        deepest = max(deepest, depth)
        if node[0] in ("not", "and", "or", "implies"):
            pending += [(sub, depth + 1) for sub in node[1:]]
        elif node[0] in ("forall", "exists"):
            pending.append((node[2], depth + 1))
    return deepest


def test_generated_formulas_follow_each_routes_limits(executables):
    """The W6 route rejects generated definition premises beyond its AST limit.
    English and norms still return their deeper generated formulas; the service
    accepts those responses without a retry. Order re-decodes surface formulas."""
    from tests.lean_service_corpus import (deep_definition_background, deep_norms_elaboration,
                                           english_cases, load, order_cases)
    route = load("lean/VE/Route/examples/route-cases.json")
    order = next(c for c in order_cases() if isinstance(c, dict) and c.get("kind") == "surface")

    def source(depth):
        return "not (" * (depth - 1) + "0 < 1" + ")" * (depth - 1) + ".\n"
    with LeanService(executables[0]) as service:
        backgrounds = service.run("route", [deep_definition_background(route, d) for d in (62, 64)])
        [english] = service.run("english", english_cases(negations=(64, 2000))[:1])
        [norms] = service.run("norms", [deep_norms_elaboration()])
        surfaces = service.run("order", [{**order, "id": str(d), "source": source(d)} for d in (64, 65)])
        assert service.stats["retries"] == 0
    assert all(row["status"] == "error" and "generated biconditional exceeds" in row["error"]
               for row in backgrounds)
    assert [_depth(item["parsed"][0]) for item in english["results"][-4:]] == [66, 2002, 66, 2002]
    assert min(_depth(x["ast"]) for x in norms["premises"] + norms["conflict_targets"]) > 64
    assert surfaces[0]["status"] == "ok" and _depth(surfaces[0]["ast"][0]) == 64
    assert surfaces[1]["status"] == "error"


def test_python_reference_decoders_agree_with_schema_domains():
    """The Python admission decoders (ve/admission.py) have the schema's kind and label
    domains: enumerations, tokens, fuel and canonical labels."""
    from ve import admission
    from ve.errors import VEError
    from ve.backends.service_schema import _compiler
    assert admission.ATOMIC_KINDS == tuple(COMMON["atomic_kind"]["enum"])
    assert admission.ACTS == tuple(COMMON["act"]["enum"])
    assert admission.MODALITIES == tuple(COMMON["modality"]["enum"])
    assert admission.RELATIONS == tuple(COMMON["relation"]["enum"])
    assert set(admission.GENERATORS) == set(COMMON["generator"]["enum"])
    kind = _compiler.ref("common.json", "#/$defs/kind")[0]
    label = _compiler.ref("common.json", "#/$defs/label")[0]

    def accepts(check, value):
        try:
            check(value, Context(None), {})
            return True
        except Invalid:
            return False

    def python_kind(value):
        try:
            admission._check_kind(value)
            return True
        except VEError:
            return False

    for value in KINDS + [_nested_kind(16), _nested_kind(17)]:
        assert python_kind(value) == accepts(kind, value), value
    for value in LABELS + STRINGS:
        assert (admission.parse_label(value) is not None) == accepts(label, value), value
