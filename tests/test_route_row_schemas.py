"""The statement-layer route modes' answers are closed (lf-1 review B, finding class 8).

Each route mode's `<mode>.json` lists every field its Lean encoder writes, typed to the leaves, and
selects a route's own answers by the route's dispatch test. Over a corpus of genuine cases recorded from
the suite (`tests/data/route-cases.jsonl`, every answer kind the suite reaches, rejections included):

* every genuine response is accepted by the client's schemas and by `ve_response_decode`
  (`ResponseDecode.Routes`, the Lean side, which dispatches with the runners' own tests);
* every drop, empty and retype of every field of every answer, and every alteration of the request
  the answer is bound to, gets the same verdict from both;
* dropping, retyping or emptying any field of an answer, or all of them, is rejected: the relay raises
  `CheckerUnavailable` before a caller can read the answer (the review's soft-norms reproduction, through
  `relay.decide` and the public elaboration, is a test of its own);
* each weakening of a route schema disagrees with the Lean side on some mutation.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import json
from pathlib import Path
import random
import shutil

import pytest

from tests.subprocesses import HANG_TIMEOUT
from tests.lean_build import lean_build
from tests.test_lean_service import fake
from tests.test_lean_service_schema import (
    _replace, _text, assert_agreement, lean_verdicts, mutations, request_mutations, singles)
from ve.backends import relay
from ve.backends.lean_service import CheckerUnavailable, LeanService, LeanServicePool, case_digest, case_texts
from ve.backends.service_schema import DIRECTORY, MODES, Compiler, Context, Invalid, check_response

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "tests/data/route-cases.jsonl"
ROUTE_MODES = ("soft-norms", "rights", "speech-acts", "reports", "alternatives", "risk", "risk-eval",
               "quantity", "norm-defaults", "discourse", "readings-route", "diagnose")
# Top-level answer fields that are maps keyed by request names (an empty map is an answer).
MAPS = {"worst_cases", "bound", "meaning_ids", "presuppositions", "validity", "statuses", "reading_verdicts",
        "units", "mentions"}
# Top-level fields whose domain is a union across JSON types (field: the types beside the genuine one).
UNIONS = {"joint": {"string", "integer"}, "admitted": {"boolean", "string"}, "finding": {"object", "null"},
          "first_failing": {"string", "null"}}
# Top-level fields whose value the schema leaves to another mode: `readings-choice`'s `inner` is the lower
# route's own row for the inner case, whose kind is not the request's, so no row shape selects it
# (readings-route.json `choice_answer`); the caller reads it as that route's answer. It is still required.
OPAQUE = {"inner"}


@pytest.fixture(scope="module")
def executables():
    bin_ = lean_build("ve_service", "ve_response_decode")
    return bin_ / "ve_service", bin_ / "ve_response_decode"


def corpus() -> dict[str, list]:
    cases = defaultdict(list)
    for line in CASES.read_text().splitlines():
        mode, case = json.loads(line)
        cases[mode].append(case)
    return cases


@pytest.fixture(scope="module")
def genuine(executables):
    """[(mode, request, response)] of the real service over the corpus, in 16-case requests."""
    exchanges = []
    with LeanService(executables[0], timeout=HANG_TIMEOUT) as service:
        for mode, cases in corpus().items():
            for start in range(0, len(cases), 16):
                chunk = cases[start:start + 16]
                text = _text(chunk)
                _, response = service.exchange(mode, text, len(chunk), timeout=HANG_TIMEOUT)
                request = {"id": response["id"], "mode": mode, "cases": chunk,
                           "digests": [case_digest(t) for t in case_texts(text)], "bytes": len(text.encode())}
                exchanges.append((mode, request, response))
    return exchanges


def answers(genuine):
    """(mode, request, response, case, row) for each `ok` answer, as the response to its case alone."""
    for mode, request, response in singles(genuine):
        row = response["results"][0]["result"]
        if row.get("status") == "ok":
            yield mode, request, response, request["cases"][0], row


def _kinds(mode):
    return set(json.loads((DIRECTORY / f"{mode}.json").read_text())["$defs"].get("kind", {}))


def test_corpus_reaches_every_answer_kind_of_every_route(genuine):
    """The corpus list is checked against the schemas: each case kind a route's schema answers has a
    genuine answer (the certificate kinds' cases carry a closing certificate bound to the regenerated
    premises, as tests/test_soft_review_regressions.py builds them)."""
    reached = {(mode, case.get("kind", "admission")) for mode, _, _, case, _ in answers(genuine)}
    assert {m for m, _, _ in genuine} == set(ROUTE_MODES) | {"norms"}
    for mode in ROUTE_MODES:
        for kind in _kinds(mode):
            assert (mode, kind) in reached, (mode, kind)
    statuses = {row.get("status") for _, _, response in genuine for row in (b["result"] for b in response["results"])}
    assert statuses == {"ok", "error"}


def test_genuine_route_answers_are_accepted_by_schema_and_lean(genuine, executables):
    verdicts = assert_agreement(executables[1], [(m, q, [r]) for m, q, r in genuine])
    assert set(verdicts) == {"accept"}
    invariants = lean_verdicts(executables[1], [(m, q, [r]) for m, q, r in genuine], "invariants")
    assert set(invariants) == {"accept"}, [v for v in invariants if v != "accept"][:5]


def _bound(response, row):
    return {**response, "results": [{**response["results"][0], "result": row}]}


def _kind_of(value):
    return ("null" if value is None else "boolean" if type(value) is bool else "integer" if type(value) is int
            else "string" if isinstance(value, str) else "array" if isinstance(value, list) else
            "object" if isinstance(value, dict) else "number")


def must_reject(row):
    """(label, answer) alterations of one answer that leave no well-formed answer: each field dropped,
    retyped or (for an object) emptied, and every payload field removed at once."""
    payload = [k for k in row if k not in ("id", "status")]
    out = [("no payload", {k: row[k] for k in ("id", "status") if k in row})] if payload else []
    for key in row:
        out.append((f"drop {key}", {k: v for k, v in row.items() if k != key}))
        if key in OPAQUE:
            continue
        for other in (7, True, None, "x", [None], {}):
            kind = _kind_of(other)
            if kind == _kind_of(row[key]) or kind in UNIONS.get(key, ()):
                continue
            out.append((f"retype {key} to {json.dumps(other)}", {**row, key: other}))
        if isinstance(row[key], dict) and row[key] and key not in MAPS:
            out.append((f"empty {key}", {**row, key: {}}))
    return out


def test_dropped_retyped_or_emptied_fields_are_rejected(genuine):
    """lf-1 review B: soft-norms output without environment_prime, with it emptied, or with every payload
    field removed passed the relay. Now no such alteration of any route's answer is a valid answer."""
    checked = defaultdict(int)
    accepted = []
    for mode, request, response, _, row in answers(genuine):
        for label, altered in must_reject(row):
            checked[mode] += 1
            try:
                check_response(mode, _bound(response, altered), request)
                accepted.append((mode, request["cases"][0].get("kind"), label))
            except Invalid:
                pass
    assert not accepted, accepted[:10]
    assert set(checked) >= set(ROUTE_MODES) and min(checked.values()) > 0


def _children(value, path=(), depth=4):
    """The nodes of an answer to `depth`: every slot of a tagged array (a kind, a formula), the first two
    elements of any other array."""
    yield path, value
    if depth:
        if isinstance(value, dict):
            for key, child in value.items():
                yield from _children(child, path + (key,), depth - 1)
        elif isinstance(value, list):
            tagged = bool(value) and isinstance(value[0], str)
            for i, child in enumerate(value if tagged else value[:2]):
                yield from _children(child, path + (i,), depth - 1)


def field_mutations(response, row, rng):
    """Every node of the answer dropped (a field), retyped, emptied or extended, and altered in its own
    type (another string, the other Boolean, a neighbouring integer); an extra field at every object."""
    out = [_bound(response, {**row, "extra": 1})]
    for path, value in _children(row):
        if not path:
            continue
        mutants = [rng.choice([m for m in (None, 7, True, "x", [None], {"x": 1}) if _kind_of(m) != _kind_of(value)])]
        if isinstance(value, str):
            mutants.append("x" if value != "x" else "y")
        elif type(value) is bool:
            mutants.append(not value)
        elif type(value) is int:
            mutants += [value + 1, -1]
        elif isinstance(value, dict):
            mutants += [{}, {**value, "extra": 1}]
        elif isinstance(value, list):
            mutants += [[], value + value[-1:] if value else [None]]
        out += [_bound(response, _replace(row, path, mutant)) for mutant in mutants]
        if isinstance(path[-1], str):
            dropped = deepcopy(row)
            node = dropped
            for step in path[:-1]:
                node = node[step]
            del node[path[-1]]
            out.append(_bound(response, dropped))
    return out


@pytest.fixture(scope="module")
def fuzz(genuine, executables):
    """[(mode, request, [response])]: field mutations of every answer, mutations of every response,
    and the same responses bound to altered requests; with the Lean side's verdicts."""
    rng = random.Random(20261005)
    items = [(mode, request, mutations(response, rng, 0, 1)) for mode, request, response in genuine]
    for mode, request, response in singles(genuine):
        row = response["results"][0]["result"]
        items.append((mode, request, field_mutations(response, row, rng) if row.get("status") == "ok"
                      else mutations(response, rng, 8, 3)))
        items += [(mode, req, [res]) for req, res in request_mutations(request, response, rng, 6)]
    items = [(mode, request, responses) for mode, request, responses in items if responses]
    return items, lean_verdicts(executables[1], items)


def test_route_answer_mutations_agree_with_lean(fuzz, executables):
    items, lean = fuzz
    verdicts = assert_agreement(executables[1], items, lean)
    assert 0 < sum(v == "accept" for v in verdicts) < len(verdicts)
    assert {mode for mode, _, _ in items} >= set(ROUTE_MODES)


@pytest.mark.parametrize("weaken", [
    "soft-prime-optional", "environment-open", "soft-path-never", "packages-detail-free", "quantity-model-free",
    "rights-kinds-unbound", "risk-decision-open", "discourse-statuses-free", "reports-kind-acts",
    "readings-pair-open", "diagnose-record-open", "risk-eval-witness-free"])
def test_fuzz_detects_a_weakened_route_schema(tmp_path, fuzz, weaken):
    """Each weakening of a route schema disagrees with the Lean side on some mutation."""
    for path in DIRECTORY.glob("*.json"):
        shutil.copy(path, tmp_path / path.name)

    def edit(name, change):
        document = json.loads((tmp_path / name).read_text())
        change(document)
        (tmp_path / name).write_text(json.dumps(document))

    def defs(name, change):
        edit(name, lambda d: change(d["$defs"]))
    {"soft-prime-optional": lambda: defs("soft-norms.json",
        lambda d: d["elaborate"]["required"].remove("environment_prime")),
     "environment-open": lambda: defs("common.json", lambda d: d.update(environment={"type": "object"})),
     "soft-path-never": lambda: defs("soft-norms.json", lambda d: d.update(soft_path=False)),
     "packages-detail-free": lambda: defs("common.json",
        lambda d: [d["packages_conflict"].pop(k) for k in ("if", "then", "else")]),
     "quantity-model-free": lambda: defs("quantity.json",
        lambda d: [d["admission"].pop(k) for k in ("if", "then", "else")]),
     "rights-kinds-unbound": lambda: defs("rights.json",
        lambda d: d["admission"]["properties"]["kinds"].pop("x-equals")),
     "risk-decision-open": lambda: defs("risk.json",
        lambda d: d["decision"]["anyOf"][1].pop("additionalProperties")),
     "discourse-statuses-free": lambda: defs("discourse.json",
        lambda d: [branch["properties"].update(statuses={"type": "object"}) for branch in d["admission"]["anyOf"]]),
     "reports-kind-acts": lambda: defs("reports.json",
        lambda d: d["report_kind"]["anyOf"][1]["x-tagged"]["attributed"].__setitem__(1, {"type": "string"})),
     "readings-pair-open": lambda: defs("readings-route.json", lambda d: d["pair"].pop("additionalProperties")),
     "diagnose-record-open": lambda: defs("diagnose.json", lambda d: d.update(record={"type": "object"})),
     "risk-eval-witness-free": lambda: defs("risk-eval.json",
        lambda d: [d["result"]["anyOf"][1].pop(k) for k in ("if", "then", "else")]),
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


# The review's reproduction, end to end: a genuine soft-norms elaboration with environment_prime deleted,
# emptied or with every payload field removed, through `relay.decide` and the public elaboration.

def _soft_document():
    from tests.test_rights import claim, right, rights_env
    from ve.rights import correlate
    return correlate(rights_env(), [right([claim()])]).soft_document


def _scripted_pool(tmp_path, mode, row):
    marker = tmp_path / "marker"
    marker.write_text(json.dumps({"id": "__nonce__", "status": "ok", "mode": mode, "results": [row],
                                  "counts": {"cases": 1, "bytes": "__bytes__", "errors": 0}}))
    return LeanServicePool(size=1, executable=fake(tmp_path, "scripted"), allow_unlisted_build=True)


@pytest.mark.parametrize("alteration", ["drop environment_prime", "empty environment_prime", "no payload"])
def test_the_reviewed_soft_mutants_raise_checker_unavailable(tmp_path, monkeypatch, executables, alteration):
    from ve.soft_route import elaborate_soft_document
    document = _soft_document()
    rows = []
    real = relay.decide
    monkeypatch.setattr("ve.soft_route.decide", lambda mode, cases: rows.extend(real(mode, cases)) or rows[-1:])
    genuine = elaborate_soft_document(document)
    assert genuine["environment_prime"] and rows == [genuine]
    altered = {"drop environment_prime": {k: v for k, v in genuine.items() if k != "environment_prime"},
               "empty environment_prime": {**genuine, "environment_prime": {}},
               "no payload": {"id": genuine["id"], "status": "ok"}}[alteration]
    pool = _scripted_pool(tmp_path, "soft-norms", altered)
    monkeypatch.setattr(relay, "_pool", pool)
    monkeypatch.setattr("ve.soft_route.decide", real)
    try:
        case = {"id": "soft-elaborate", "kind": "soft-elaborate", "environment": document.env.to_dict(),
                "norms": [rule.to_dict() for rule in document.rules]}
        with pytest.raises(CheckerUnavailable, match="malformed response"):
            relay.decide("soft-norms", [case])
        with pytest.raises(CheckerUnavailable, match="malformed response"):
            elaborate_soft_document(document)
    finally:
        pool.close()


def test_a_soft_rejection_with_another_checks_code_breaks_a_lean_invariant(genuine, executables):
    """Content the client leaves to the service: a soft rejection's code is its failed check's
    (`SoftNorms.Run.reportedCode`). Another valid code keeps the binding, so the client accepts it,
    and the Lean invariant rejects it."""
    swapped = []
    for mode, request, response in singles(genuine):
        row = response["results"][0]["result"]
        if mode == "soft-norms" and row.get("status") == "error" and "code" in row:
            other = "SOFT_INVALID_INPUT" if row["code"] != "SOFT_INVALID_INPUT" else "SOFT_INVALID_NAME"
            swapped.append((mode, request, [_bound(response, {**row, "code": other})]))
    assert swapped
    assert set(assert_agreement(executables[1], swapped)) == {"accept"}
    assert not any(v == "accept" for v in lean_verdicts(executables[1], swapped, "invariants"))


# Every answer object is closed: the structural guard of the class (an open `route_ok` passed any payload).

# Objects deliberately open, with why: a predicate declaration of E' echoes the request's (and the
# generated ones add theirs); its domain is the environment decoder's and the caller compares E' whole.
# The same holds for the base environment of the norm-defaults soft and rights branches.
OPEN_ALLOWED = {"common.json#/$defs/environment/properties/vocabulary/properties/predicates/additionalProperties",
                "norm-defaults.json#/$defs/base_environment/properties/vocabulary/properties/predicates/additionalProperties"}


def open_objects(directory=DIRECTORY):
    """Answer schemas (reachable from every mode's row and the envelope; request selectors, `if`
    conditions and refinements beside a `$ref`, `then` or `else` excluded) that describe an object
    without closing it: no `additionalProperties`, no `x-equals` binding, no closed alternatives."""
    documents = {p.name: json.loads(p.read_text()) for p in directory.glob("*.json")}
    stack = [(f"{mode}.json", "#/row") for mode in MODES] + [("envelope.json", "#/response")]
    seen, found = set(), set()

    def closed(schema):
        return isinstance(schema, dict) and ("additionalProperties" in schema or "x-equals" in schema or (
            "anyOf" in schema and all(closed(branch) for branch in schema["anyOf"])))

    def walk(schema, file, where, refinement):
        if not isinstance(schema, dict):
            return
        if "$ref" in schema:
            name, _, pointer = schema["$ref"].partition("#")
            stack.append((name or file, "#" + pointer))
        shaped = schema.get("type") == "object" or "properties" in schema
        if shaped and not refinement and "$ref" not in schema and not closed(schema):
            found.add(f"{file}{where}")
        for key, value in schema.items():
            if key == "x-select":
                for i, entry in enumerate(value):
                    walk(entry["then"], file, f"{where}/x-select/{i}/then", False)
            elif key == "properties":
                for name, sub in value.items():
                    walk(sub, file, f"{where}/properties/{name}", refinement or "$ref" in schema)
            elif key == "x-tagged":
                for tag, slots in value.items():
                    for i, sub in enumerate(slots):
                        walk(sub, file, f"{where}/x-tagged/{tag}/{i}", False)
            elif key in ("anyOf", "allOf", "prefixItems"):
                for i, sub in enumerate(value):
                    walk(sub, file, f"{where}/{key}/{i}", refinement or key == "allOf")
            elif key in ("items", "additionalProperties", "x-rows"):
                walk(value, file, f"{where}/{key}", False)
            elif key in ("then", "else"):
                walk(value, file, f"{where}/{key}", True)
            elif key == "x-zip":
                walk(value["items"], file, f"{where}/x-zip/items", False)

    while stack:
        file, pointer = stack.pop()
        if (file, pointer) not in seen:
            seen.add((file, pointer))
            target = documents[file]
            for step in pointer[2:].split("/") if pointer != "#" else []:
                target = target[step.replace("~1", "/").replace("~0", "~")]
            walk(target, file, pointer, False)
    return found


def test_no_answer_object_is_left_open():
    assert open_objects() == OPEN_ALLOWED


def test_an_open_answer_is_found(tmp_path):
    for path in DIRECTORY.glob("*.json"):
        shutil.copy(path, tmp_path / path.name)
    document = json.loads((tmp_path / "risk.json").read_text())
    document["$defs"]["audit"].pop("additionalProperties")
    (tmp_path / "risk.json").write_text(json.dumps(document))
    assert open_objects(tmp_path) == OPEN_ALLOWED | {"risk.json#/$defs/audit"}


def test_the_delta_states_the_corpus_it_ran():
    import re
    delta = (ROOT / "docs/lean-first/b1/DELTA.md").read_text()
    stated = re.search(r"`tests/data/route-cases\.jsonl`, (\d[\d,]*) cases", delta)
    assert stated and int(stated.group(1).replace(",", "")) == len(CASES.read_text().splitlines())
