"""The response schemas against the Lean service and the Lean decoders.

* Every genuine response of the service over a corpus with every mode and result kind
  (`tests/lean_service_corpus.py`) is accepted by the schemas and by
  `ve_response_decode`, the Lean decoding of responses (`lean/ResponseDecode.lean`).
* Differential fuzz: mutations of those genuine responses (dropped, altered, retyped,
  enum-swapped, truncated and extra fields, at every depth) are accepted by the schemas
  exactly when the Lean decoders accept them. Request-linked values are also mutated
  together with their request, so each value domain is compared on its own.
* The harness has teeth: each of a list of schema weakenings disagrees with Lean on
  some mutation.
* Each finding of the mig1 rechecks is a scripted replacement of a genuine response
  that must fail closed, after one retry, as `CheckerUnavailable`.
* Every result is bound to its case (position and case digest); mutations of the
  bindings are part of the fuzz.
"""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import random
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_service_corpus import corpus
from tests.test_lean_service import fake
from ve.backends.lean_service import CheckerUnavailable, LeanService, case_digest, case_texts
from ve.backends.service_schema import DIRECTORY, MODES, Compiler, Context, Invalid, check_response

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "lean/.lake/build/bin"
COMMON = json.loads((DIRECTORY / "common.json").read_text())["$defs"]


@pytest.fixture(scope="module")
def executables():
    lake = shutil.which("lake")
    if lake is None and not (BIN / "ve_response_decode").exists():
        pytest.skip("lake is not available")
    if lake is not None and not os.environ.get("VE_LEAN_PREBUILT"):
        build = subprocess.run([lake, "build", "ve_service", "ve_response_decode"], cwd=ROOT / "lean",
                               capture_output=True, text=True, timeout=HANG_TIMEOUT)
        assert build.returncode == 0, build.stdout + build.stderr
    return BIN / "ve_service", BIN / "ve_response_decode"


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
    with LeanService(service_executable, timeout=600) as service:
        for mode, cases in corpus().items():
            for start in range(0, len(cases), 16):
                chunk = cases[start:start + 16]
                text = _text(chunk)
                _, response = service.exchange(mode, text, len(chunk), timeout=600)
                request = {"id": response["id"], "mode": mode, "cases": chunk,
                           "digests": [case_digest(t) for t in case_texts(text)], "bytes": len(text.encode())}
                assert rebind(request, response) == (request, response)
                exchanges.append((mode, request, response))
        assert service.stats["retries"] == 0
    return exchanges


def lean_verdicts(decoder, items):
    """ve_response_decode's verdict ("accept" or "reject: ...") for each (mode, request, response)."""
    lines, sizes = [], []
    for mode, request, responses in items:
        lines.append(json.dumps({"mode": mode, "request": request, "responses": responses}))
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
def fuzz(genuine, executables):
    """[(mode, request, [response])]: mutations of every genuine response and of each of its
    results alone, joint request/result mutations, altered requests and the value-domain
    probes below; with Lean's verdicts."""
    rng = random.Random(20260928)
    items = [(mode, request, mutations(response, rng, 0, 1)) for mode, request, response in genuine]
    for mode, request, response in singles(genuine):
        items.append((mode, request, mutations(response, rng, 14, 3)))
        items += [(mode, req, [res]) for req, res in joint_mutations(request, response, rng, 8)]
        items += [(mode, req, [res]) for req, res in request_mutations(request, response, rng, 6)]
    items += (kind_items(genuine) + label_items(genuine) + depth_items(genuine) + report_items(genuine)
              + graph_items(genuine) + count_items(genuine))
    return items, lean_verdicts(executables[1], items)


def test_mutated_genuine_responses_agree_with_lean_decoders(fuzz, executables):
    items, lean = fuzz
    verdicts = assert_agreement(executables[1], items, lean)
    assert 0 < sum(v == "accept" for v in verdicts) < len(verdicts)


@pytest.mark.parametrize("weaken", [
    "digest", "index", "modality", "act", "relation", "token", "kind-fuel", "formula-fuel", "values-nonempty",
    "values-count", "claim-member", "kinds-link", "lemmas-link", "checked-count", "order-link",
    "surface-nonempty", "label", "english-checked", "assumptions-unfold", "valid-false", "background-runs",
    "certificate-count", "norms-layers", "norms-order", "norms-targets", "norms-background",
    "norms-certificate", "conflict-targets", "literal-pairs", "generated-cap"])
def test_fuzz_detects_a_weakened_schema(tmp_path, fuzz, weaken):
    """The differential harness has teeth: each weakening of the schemas disagrees with
    the Lean decoders on some mutation (and so does the decoders' depth cap put back on
    generated formulas)."""
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
     "values-nonempty": lambda: edit(common, lambda d: d["values"].pop("minItems")),
     "values-count": lambda: edit(common, lambda d: d["values"].pop("x-length")),
     "claim-member": lambda: edit(common, lambda d: d["claim"].pop("x-member")),
     "kinds-link": lambda: edit(common, lambda d: d["admission"]["properties"]["kinds"].pop("x-equals")),
     "lemmas-link": lambda: edit("route.json", lambda d: d["bundle"]["properties"]["lemmas"].pop("x-equals")),
     "checked-count": lambda: edit("route.json", lambda d: d["bundle"]["properties"]["checked"].pop("x-count")),
     "order-link": lambda: edit("route.json",
                                lambda d: d["dependency-order"]["properties"]["order"].pop("x-dependency-order")),
     "surface-nonempty": lambda: edit("order.json", lambda d: d["surface"]["properties"]["ast"].pop("minItems")),
     "label": lambda: edit(common, lambda d: d["label"].update(pattern=".*")),
     "english-checked": lambda: edit("english.json", lambda d: d["item"]["allOf"].pop()),
     "assumptions-unfold": lambda: edit(common, lambda d: d["admission"]["properties"]["report"]["properties"][
         "assumptions"].pop("x-unfolds")),
     "valid-false": lambda: edit(common, lambda d: d["error_valid"]["properties"].update(valid={"type": "boolean"})),
     "background-runs": lambda: edit("route.json", lambda d: d["background"]["properties"]["generators"].pop("x-runs")),
     "certificate-count": lambda: edit("route.json",
                                       lambda d: d["certificate"]["properties"]["background"].pop("x-cardinality")),
     "norms-layers": lambda: edit("norms.json",
                                  lambda d: d["norms-elaborate"]["properties"]["premises"].pop("x-cardinality")),
     "norms-order": lambda: edit("norms.json",
                                 lambda d: d["norms-elaborate"]["properties"]["order"].pop("x-cardinality")),
     "norms-targets": lambda: edit("norms.json", lambda d: d["norms-elaborate"]["properties"][
         "conflict_targets"].pop("x-cardinality")),
     "norms-background": lambda: edit("norms.json",
                                      lambda d: d["norms-elaborate"]["properties"]["background"].pop("x-runs")),
     "norms-certificate": lambda: edit("norms.json", lambda d: d["norms-certificate"]["properties"][
         "layers"].pop("x-cardinality")),
     "conflict-targets": lambda: edit("norms.json",
                                      lambda d: d["norms-conflict"]["properties"]["targets"].pop("x-cardinality")),
     "literal-pairs": lambda: _edit_counts(
         tmp_path, lambda c: c["literals"].update(pairs={"sum": [c["literals"]["pairs"], 1]})),
     "generated-cap": lambda: edit(common, lambda d: d["generated_formula"].update(
         {"x-fuel": {"counter": "generated_formula", "limit": 64}})),
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


def _edit_counts(directory, change):
    document = json.loads((directory / "common.json").read_text())
    change(document["counts"])
    (directory / "common.json").write_text(json.dumps(document))


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


def report_items(genuine):
    """Reports: assumptions are exactly the ordered unfolding of the request graph from its
    root; the root is the graph's root."""
    items = []
    for mode in ("route", "norms"):
        for request, response, i in _linked(genuine, mode, "admission"):
            report = result(response, i)["report"]
            root, assumptions = report["root"], report["assumptions"]
            for changed in ({"assumptions": assumptions + [root]}, {"assumptions": assumptions * 2},
                            {"assumptions": assumptions[::-1]}, {"assumptions": []},
                            {"assumptions": assumptions[1:]}, {"assumptions": assumptions[:-1]},
                            {"assumptions": assumptions[1:2] + assumptions[:1] + assumptions[2:]},
                            {"assumptions": assumptions[-1:] + assumptions[1:]},
                            {"root": assumptions[0]} if assumptions else {}):
                res = deepcopy(response)
                result(res, i)["report"].update(changed)
                items.append((mode, request, [res]))
    return items


def graph_items(genuine):
    """The unfolding's conditions on the request graph (`VE.Graph.check`): the genuine
    report against graphs with a later or dangling premise, a duplicate name, a deduction
    without its certificate, a leaf with one, another root, and an extra premise."""
    items = []
    for mode in ("route", "norms"):
        for request, response, i in _linked(genuine, mode, "admission"):
            graph = request["cases"][i]["document"]["graph"]
            nodes = graph["nodes"]
            deductions = [k for k, n in enumerate(nodes) if "premises" in n]
            changes = [{"nodes": nodes[::-1]}, {"nodes": nodes + nodes[:1]}, {"root": "missing"},
                       {"root": nodes[0]["name"]}, {"nodes": [{**nodes[0], "certificate": {}}] + nodes[1:]}]
            for k in deductions[:1]:
                edited = deepcopy(nodes)
                del edited[k]["certificate"]
                changes.append({"nodes": edited})
                for premise in ("missing", nodes[k]["name"], nodes[-1]["name"], nodes[0]["name"]):
                    edited = deepcopy(nodes)
                    edited[k]["premises"] = edited[k]["premises"] + [premise]
                    changes.append({"nodes": edited})
            for change in changes:
                req = deepcopy(request)
                req["cases"][i]["document"]["graph"].update(change)
                req, res = rebind(req, response)
                items.append((mode, req, [res]))
    return items


def test_graph_unfolding_agrees_with_the_lean_graph_conditions(genuine, executables):
    verdicts = assert_agreement(executables[1], graph_items(genuine) + report_items(genuine))
    assert "accept" in verdicts and any(v != "accept" for v in verdicts)


REGENERATED = {  # (mode, kind): the result fields regenerated from the environment
    ("route", "background"): ("background", "premises", "generators"),
    ("route", "certificate"): ("background",),
    ("norms", "background"): ("background", "premises", "generators"),
    ("norms", "certificate"): ("background",),
    ("norms", "norms-elaborate"): ("order", "background", "premises", "conflict_targets"),
    ("norms", "norms-certificate"): ("background", "layers"),
    ("norms", "norms-conflict"): ("targets",),
}


def _count_mutants(row, fields):
    """Each regenerated list emptied, shortened, extended or reordered, and each count moved."""
    for field in fields:
        value = row[field]
        if isinstance(value, list):
            changes = [[], value[:-1], value[1:], value + value[-1:], value[::-1], value[-1:] + value[:-1]]
            if field in ("background", "premises", "generators") and "generators" in row:
                # the route Background: all three arrays together
                yield {**row, **{f: [] for f in ("background", "premises", "generators")}}
                for keep in (slice(None, -1), slice(1, None)):
                    yield {**row, **{f: row[f][keep] for f in ("background", "premises", "generators")}}
            for changed in changes:
                if changed != value:
                    yield {**row, field: changed}
        else:
            for changed in (value - 1, value + 1):
                if changed >= 0:
                    yield {**row, field: changed}
    if "generators" in row:
        for other in ("flags", "definitions", "literals"):
            if row["generators"] and other != row["generators"][0]:
                yield {**row, "generators": [other] + row["generators"][1:]}


def _environment_mutants(case):
    """The environment with one more or one fewer regenerated declaration."""
    vocabulary = case["environment"]["vocabulary"]
    predicates, constants = vocabulary["predicates"], vocabulary["constants"]
    yield {"constants": {**constants, "zeta": {"sort": "$string"}}}
    yield {"constants": {**constants, "zeta": {"sort": "$string"}, "eta": {"sort": "$string"}}}
    yield {"constants": {k: v for k, v in constants.items() if v.get("sort") != "$string"}}
    for name, entry in predicates.items():
        for key in ("defined", "regulated", "functional", "total"):
            if key in entry:
                yield {"predicates": {**predicates, name: {k: v for k, v in entry.items() if k != key}}}
        if isinstance(entry.get("regulated"), dict):
            regulated = entry["regulated"]
            yield {"predicates": {**predicates, name: {**entry, "regulated": {
                **regulated, "role": "plain" if regulated.get("role") == "obligation" else "obligation"}}}}
            yield {"predicates": {**predicates, name: {**entry, "regulated": {**regulated, "permission": None}}}}
        if len(entry.get("arguments", ())) == 2:
            yield {"predicates": {**predicates, name: {**entry, "functional": True, "total": True}}}
    yield {"predicates": [], "constants": []}


def count_items(genuine):
    """Regenerated lists and counts: altered results against their request, and the
    genuine result against environments with more or fewer regenerated declarations."""
    items = []
    for (mode, kind), fields in REGENERATED.items():
        for request, response, i in _linked(genuine, mode, kind)[:6]:
            row, case = result(response, i), request["cases"][i]
            for changed in _count_mutants(row, fields):
                res = deepcopy(response)
                res["results"][i]["result"] = changed
                items.append((mode, request, [res]))
            for change in _environment_mutants(case):
                req = deepcopy(request)
                req["cases"][i]["environment"]["vocabulary"].update(change)
                req, res = rebind(req, response)
                items.append((mode, req, [res]))
    return items


def test_regenerated_counts_agree_with_lean(genuine, executables):
    verdicts = assert_agreement(executables[1], count_items(genuine))
    assert "accept" in verdicts and any(v != "accept" for v in verdicts)


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


# Regression tests for the mig1 recheck findings: scripted replacements of genuine
# responses fail closed after exactly one retry.

def _scripted_rejected(tmp_path, mode, case, good, bad):
    """The scripted service answers `good` (accepted, no retry), then `bad`, which must
    fail closed after exactly one retry."""
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
    ("dependency-order", {"order": []}),
    ("dependency-order-short", None),
    ("admission", {"kinds": []}),
    ("admission-short", None),
])
def test_truncated_request_linked_results_fail_closed(tmp_path, genuine, mode, field, truncated):
    kind = field.removesuffix("-short")
    size = {"bundle": ("lemmas", 3), "dependency-order": ("order", 3), "admission": ("kinds", 4)}[kind]
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
@pytest.mark.parametrize("name,change", [
    ("bridge-background", "empty"), ("shared-leaves", "empty"), ("shared-leaves", "drop-last"),
    ("shared-leaves", "drop-first"), ("shared-leaves", "duplicate"), ("shared-leaves", "reorder"),
    ("shared-leaves", "substitute"), ("shared-leaves", "deduction")])
def test_admission_assumptions_are_the_graph_unfolding(tmp_path, genuine, mode, name, change):
    """mig1c-looprecheck1 A: a report whose assumptions were replaced by [] kept
    `admitted: true` and was accepted. The assumptions are exactly the root's ordered
    unfolding, so every loss, repetition, reordering or substitution of a leaf fails closed
    (each substitute is still a node, and a leaf, of the request)."""
    case, row = _genuine_row(genuine, mode, "admission", lambda c, r: c["id"] == name)
    assumptions = row["report"]["assumptions"]
    nodes = {n["name"]: {k: n[k] for k in ("name", "ast", "label") if k in n}
             for n in case["document"]["graph"]["nodes"]}
    assert assumptions and all(a in nodes.values() for a in assumptions)
    changed = {"empty": lambda: [], "drop-last": lambda: assumptions[:-1],
               "drop-first": lambda: assumptions[1:], "duplicate": lambda: assumptions + assumptions[:1],
               "reorder": lambda: assumptions[1:2] + assumptions[:1] + assumptions[2:],
               "substitute": lambda: [nodes["b"]] + assumptions[1:],
               "deduction": lambda: [nodes["mid"]] + assumptions[3:]}[change]()
    assert changed != assumptions
    bad = deepcopy(row)
    bad["report"]["assumptions"] = changed
    _scripted_rejected(tmp_path, mode, case, row, bad)


@pytest.mark.parametrize("mode", ["route", "norms"])
@pytest.mark.parametrize("change", ["empty", "drop-definition", "drop-literal", "relabel"])
def test_regenerated_background_keeps_every_premise(tmp_path, genuine, mode, change):
    """mig1c-looprecheck1 B: the five-premise defs-background response with all three
    arrays emptied was accepted. Each generator's premise count is fixed by the request."""
    case, row = _genuine_row(genuine, mode, "background", lambda c, r: c["id"] == "defs-background")
    assert row["generators"] == ["definitions"] * 4 + ["literals"]
    keep = {"empty": slice(0, 0), "drop-definition": slice(1, None), "drop-literal": slice(None, -1),
            "relabel": slice(None)}[change]
    bad = {**row, **{f: row[f][keep] for f in ("background", "premises", "generators")}}
    if change == "relabel":
        bad["generators"] = ["definitions"] * 5
    _scripted_rejected(tmp_path, mode, case, row, bad)


@pytest.mark.parametrize("name", ["e2", "e-literals"])
@pytest.mark.parametrize("fields", [("order",), ("premises",), ("conflict_targets",), ("background",),
                                    ("order", "premises", "conflict_targets"),
                                    ("order", "background", "premises", "conflict_targets")])
@pytest.mark.parametrize("truncate", ["empty", "drop-last"])
def test_regenerated_norms_elaboration_keeps_every_layer(tmp_path, genuine, name, fields, truncate):
    """mig1c-looprecheck1 B: emptied order, premises and conflict targets of a nonempty
    elaboration were accepted. Their lengths are fixed by the regulated predicates and
    profile pairs, and Background by its generators."""
    case, row = _genuine_row(genuine, "norms", "norms-elaborate", lambda c, r: c["id"] == name)
    assert all(row[f] for f in fields)
    bad = {**row, **{f: [] if truncate == "empty" else row[f][:-1] for f in fields}}
    _scripted_rejected(tmp_path, "norms", case, row, bad)


@pytest.mark.parametrize("mode,kind,field,name", [
    ("route", "certificate", "background", "data-definition-certificate"),
    ("norms", "certificate", "background", "defs-certificate-uses-definitions"),
    ("norms", "norms-certificate", "layers", "certificate"),
    ("norms", "norms-certificate", "background", "certificate"),
    ("norms", "norms-conflict", "targets", "c2"),
    ("norms", "norms-conflict", "targets", "w0"),
])
def test_regenerated_counts_fail_closed(tmp_path, genuine, mode, kind, field, name):
    """The same class for counts and target lists: each is the request's count."""
    case, row = _genuine_row(genuine, mode, kind, lambda c, r: c["id"] == name)
    value = row[field]
    for bad in ([], value[:-1]) if isinstance(value, list) else (value + 1, max(value - 1, 0) if value else 1):
        if bad != value:
            _scripted_rejected(tmp_path, mode, case, row, {**row, field: bad})


@pytest.mark.parametrize("mode", ["route", "norms"])
def test_empty_evaluation_of_empty_document_fails_closed(tmp_path, genuine, mode):
    case, row = _genuine_row(genuine, "route", "evaluate", lambda c, r: bool(c.get("ast")))
    case["ast"] = case["ast"][:1]
    good = {**row, "values": row["values"][:1]}
    _scripted_rejected(tmp_path, mode, case, good, {**good, "values": []})
    case["ast"] = []
    error = {"id": case["id"], "status": "error", "error": "empty document"}
    _scripted_rejected(tmp_path, mode, case, error, {**good, "values": []})


def test_empty_order_surface_parse_fails_closed(tmp_path, genuine):
    case, row = _genuine_row(genuine, "order", "surface")
    case["source"] = "0 < 1.\n"
    good = {**row, "ast": [["lt", ["num", "0"], ["num", "1"]]]}
    _scripted_rejected(tmp_path, "order", case, good, {**good, "ast": []})


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


def test_generated_formulas_deeper_than_the_decoders_are_accepted(executables):
    """mig1c-looprecheck1 B: a binary definition with a body of depth 62 has a depth-66
    Background premise, and English with 64 negations parses at depth 65; both actual
    service responses failed as CheckerUnavailable after one retry. Formulas the runners
    generate are not bounded by the decoders' 64: these, the largest definition premise
    (68), a 2002-deep English parse and a norms elaboration over 70 rules are accepted with
    no retry. Order surface formulas stay within 64 because the runner re-decodes them."""
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
    assert [max(map(_depth, row["premises"])) for row in backgrounds] == [66, 68]
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
