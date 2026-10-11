"""Record, or check, the `ask` fixtures (docs/spec/question-answering.md 7.2, 7.4, 7.5; plan Q2.2, Q2.5).

    python tools/ask_fixtures.py --write [ID ...]   # run the generators and Lean, record tests/fixtures/ask/<ID>.json
    python tools/ask_fixtures.py --check            # replay every recorded request through Lean, compare the answers

Each fixture is a question over a fixture document: the G document (the plain adapter), the UDHR pilot's part 7 (RD-3's
readings route) and the agent-policy documents (the zero-set route). `--write` runs `ve.ask.prepare` (the untrusted
generators) and records the request's case and reading names with Lean's answer; the tests replay the recorded
request through Lean with no generator (plan Q2.2: "from recorded evidence files"). For the agent-policy documents
VE's prover cannot prove the `permitted` conflict package within its budget, so this tool adds the agent-policy use
case's focused prover (`usecases/agent-policy/focused.py`, untrusted tooling) for the packages it leaves open; Lean
checks every package as it checks every piece.

This is evidence tooling, not a product path: nothing here decides an answer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "tests/fixtures/ask"
GROUP = "usecases/question-answering/group.ve.md"
UDHR = "usecases/question-answering/udhr-part07.ve.md"
AGENT = "usecases/question-answering/agent-policy/"

FIXTURES = [
    ("G1", GROUP, "Is every member eligible?"),
    ("G2", GROUP, "Is it the case that every member is eligible?"),
    ("G3", GROUP, "Is every member verified?"),
    ("G4", GROUP, "Is it the case that no member is eligible?"),
    ("G10", GROUP, "Is Ann eligible?"),
    ("U2", UDHR, "Must every person be given equal access to higher education on the basis of merit?"),
    ("U3", UDHR, "Must every person be spared exclusion from education?"),
    ("U5", UDHR, "May every person form as well as join trade unions to protect their interests?"),
    ("U6", UDHR, "Must every person receive elementary education?"),
    ("U7", UDHR, "Must every education kind be made generally available?"),
    ("A1", AGENT + "a-unspecified.ve.md", 'May "a27" be performed?'),
    ("A1d", AGENT + "a-deny.ve.md", 'May "a27" be performed?'),
    ("A2", AGENT + "a-unspecified.ve.md", 'May "a25" be performed?'),
    ("A3", AGENT + "a-unspecified.ve.md", 'May "a26" be performed?'),
    ("A4", AGENT + "a-unspecified.ve.md", 'Must "a13" be reported to the user?'),
    ("A5", AGENT + "a-conflict.ve.md", 'May "a10" be performed?'),
    ("A7", AGENT + "a-rules.ve.md", "May every action be performed?"),
    ("A8", AGENT + "a-unspecified.ve.md", "Must every action be reported to the user?"),
]


def _remap(node, index):
    """A trace with every branch index sent through `index`; None when a node expands a premise `index` drops."""
    if type(node) is list:
        out = [_remap(x, index) for x in node]
        return None if any(x is None for x in out) else out
    if type(node) is not dict:
        return node
    out = {}
    for key, value in node.items():
        if key == "at":
            if index(value) is None:
                return None
            out[key] = index(value)
        else:
            mapped = _remap(value, index)
            if mapped is None and value is not None:
                return None
            out[key] = mapped
    return out


def focused_packages(path: str) -> dict:
    """The conflict packages of an agent-policy document: VE's prover's, then the focused prover's for the targets
    it leaves open, bound as `_FilledChoiceDocument._packages` binds a package."""
    from ve.ask import _zero_generator
    from ve.ast import Not, formula_to_data
    from ve.document import load_document
    from ve.entailment import _validate_inputs
    from ve.norms import _bind
    from ve.wire import digest
    sys.path.insert(0, str(ROOT / "usecases/agent-policy"))
    import focused
    gen = _zero_generator(load_document(ROOT / path))
    packages = gen._packages()
    row = gen.elaboration
    literals = gen._base_literals()
    premises = [formula for _, formula in literals] + gen._base_fill()
    lit_data = [json.dumps(ast, sort_keys=True) for ast, _ in literals]

    def meaning(ast):
        return digest(f"ve-meaning-{gen.base.identity_version}\n",
                      {"environment_id": gen.base.environment_id, "ast": ast})
    for target, sorts, formula in gen.targets:
        if target in packages:
            continue
        conclusion = _bind(Not(formula), sorts)
        try:
            certificate, _ = focused.prove(gen.base, premises, conclusion, max_nodes=200_000)
        except focused.Failed:
            continue
        validated = _validate_inputs(gen.base, premises, conclusion)
        background = len(validated) - len(premises)
        # The focused prover lists VE's Background first; Lean's package premises are the literals and `Fill_T`.
        # A Background literal is the same premise as the row's literal; a flag premise has no place in Lean's list.
        own = {}
        for position in range(background):
            data = json.dumps(formula_to_data(gen.base, validated[position], _generated=True), sort_keys=True)
            if data in lit_data:
                own[position] = lit_data.index(data)

        def index(at, own=own, background=background):
            return own.get(at) if at < background else at - background
        trace = _remap(certificate["trace"], index)
        if trace is None:
            continue
        packages[target] = {"environment_id": row["environment_id"], "document_hash": row["document_hash"],
                            "target": target,
                            "certificate": {**{k: v for k, v in certificate.items() if k != "trace"}, "trace": trace,
                                            "environment_id": gen.base.environment_id,
                                            "premise_meaning_ids": [meaning(ast) for ast, _ in literals] +
                                            [meaning(item["ast"]) for item in row["fill"]],
                                            "conclusion_meaning_id": meaning(
                                                formula_to_data(gen.base, conclusion, _generated=True))}}
    return packages


def record_model(case: dict) -> dict:
    """The closed-world base situation of an agent-policy document's records (as the use case's `record_model`):
    each constant its own element, the recorded atoms true and every other atom false, a recorded existential with
    one fresh witness. An action no record names shares the first recorded action's element, so that `tool` stays
    functional and total. Lean checks it like every model."""
    env = case["environment"]
    vocabulary = env["vocabulary"]
    regulated = {p for p, d in vocabulary["predicates"].items() if "regulated" in d}
    domains = {sort: [] for sort in vocabulary.get("sorts", {})}
    domains.setdefault("$string", [])
    relations = {p: [] for p in vocabulary["predicates"] if p not in regulated}
    recorded = []

    def atom(f, witness=None):
        args = f[2:] if f[0] == "binary" else [f[2]]
        values = [witness if a == ["var", 0] else a[1] for a in args]
        if all(type(v) is str for v in values) and f[1] in relations and values not in relations[f[1]]:
            relations[f[1]].append(values)
    for unit in case["document"]["units"]:
        f = unit["content"]
        if unit["kind"] != "asserted" or f is None:
            continue
        if f[0] == "exists" and f[2][0] in ("unary", "binary"):
            witness = f"unnamed_{f[1]}_{len(domains.setdefault(f[1], [])) + 1}"
            domains[f[1]].append(witness)
            atom(f[2], witness)
        elif f[0] in ("unary", "binary"):
            atom(f)
    for row in relations.get("tool", []):
        if row[0] not in recorded:
            recorded.append(row[0])
    constants = {}
    for name, decl in vocabulary.get("constants", {}).items():
        sort = decl["sort"]
        if sort == "action" and recorded and name not in recorded:
            constants[name] = recorded[0]
            continue
        domains.setdefault(sort, []).append(name)
        constants[name] = name
    return {"complete": True, "domains": domains, "constants": constants, "relations": relations}


def agent_evidence(prepared_for, base: dict, packages: dict) -> tuple:
    """The evidence Lean accepts among the closed-world candidates: the base situation as the premises' model, as a
    countermodel with an empty filling, and, for a document with a conflict, as a witness at each recorded action;
    a split is added by `Prepared.ask` from the gaps Lean names. A document with no record (no action has a tool)
    gets one action, every action constant naming it, under each tool literal in turn. Returns the prepared request
    and Lean's answer."""
    bases = [base]
    actions = base["domains"].get("action", [])
    if actions and not base["relations"].get("tool"):
        first = actions[0]
        for literal in base["domains"].get("$string", []):
            alt = json.loads(json.dumps(base))
            alt["domains"]["action"] = [first]
            alt["constants"] = {c: (first if e in actions else e) for c, e in alt["constants"].items()}
            alt["relations"]["tool"] = [[first, literal]]
            bases.append(alt)
    prepared = result = None
    for candidate_base in bases:
        model = {"model": candidate_base, "filling": {}}
        evidence = {"conflict": {"packages": packages}, "model": {"kind": "choice-model", **model},
                    "countermodel": {"kind": "choice-model", **model}}
        prepared = prepared_for(evidence)
        result = prepared.ask()
        if result["rows"][0]["lead"] != "unknown" or result["rows"][0]["reason"] == "X2":
            base = candidate_base
            break
    row = result["rows"][0]
    if row["reason"] == "X2":
        actions = sorted({c for c in base["constants"].values() if c in base["domains"].get("action", [])})
        for target in ("permitted", "report_required"):
            for action in actions:
                # The witness's model is the filled situation: the base with the (empty) unsaid tables.
                tables = {f"unsaid__{p}": [] for p, d in prepared.request["case"]["environment"]["vocabulary"][
                    "predicates"].items() if (d.get("regulated") or {}).get("default") == "unspecified"}
                filled = {**base, "relations": {**base["relations"], **tables}}
                witness = {"witness": {"target": target, "model": filled, "tuple": [action]}}
                candidate = prepared_for({**evidence, "witness": witness})
                answer = candidate.ask()
                if answer["rows"][0]["reason"] == "X1":
                    return candidate, answer
    return prepared, result


def record(ident: str, path: str, question: str, packages: dict | None) -> dict:
    from ve.ask import prepare
    raw = (ROOT / path).read_bytes()
    started = time.monotonic()
    if packages is not None:
        probe = prepare(ROOT / path, raw, question, {"conflict": {"packages": packages}}, generate=False)
        base = record_model(probe.request["case"])
        prepared, result = agent_evidence(
            lambda evidence: prepare(ROOT / path, raw, question, evidence, generate=False), base, packages)
    else:
        prepared = prepare(ROOT / path, raw, question)
        result = prepared.ask()
    return {"id": ident, "path": path, "sha256": hashlib.sha256(raw).hexdigest(), "question": question,
            "case": prepared.request["case"], "names": prepared.request["names"], "result": result,
            "seconds": round(time.monotonic() - started, 1)}


def write(ids: list[str]) -> int:
    from ve.errors import VEError
    OUT.mkdir(parents=True, exist_ok=True)
    cache: dict[str, dict] = {}
    for ident, path, question in FIXTURES:
        if ids and ident not in ids:
            continue
        packages = None
        if path.startswith(AGENT):
            if path not in cache:
                try:
                    cache[path] = focused_packages(path)
                except VEError:
                    cache[path] = {}
            packages = cache[path]
        try:
            entry = record(ident, path, question, packages)
        except VEError as exc:
            # A refusal is recorded as the fixture's outcome (its class and Lean's text).
            raw = (ROOT / path).read_bytes()
            entry = {"id": ident, "path": path, "sha256": hashlib.sha256(raw).hexdigest(), "question": question,
                     "error": {"class": type(exc).__name__, "message": str(exc)}}
            print(f"{ident}: {entry['error']['class']}: {entry['error']['message']}")
        else:
            print(f"{ident}: {entry['result']['lead']} ({entry['seconds']} s)")
            conflict = entry["case"]["evidence"].get("conflict") if path.startswith(AGENT) else None
            if conflict is not None:
                # One document's packages, recorded once beside its fixtures (`load` puts them back).
                name = f"packages-{Path(path).stem.removesuffix('.ve')}.json"
                (OUT / name).write_text(_dump(conflict))
                entry["case"]["evidence"]["conflict"] = {"recorded": name}
        (OUT / f"{ident}.json").write_text(_dump(entry))
    return 0


def _dump(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def load(ident: str) -> dict:
    """A recorded fixture, its document's recorded packages put back in its case."""
    entry = json.loads((OUT / f"{ident}.json").read_text())
    evidence = (entry.get("case") or {}).get("evidence")
    conflict = evidence.get("conflict") if isinstance(evidence, dict) else None
    if conflict is not None and set(conflict) == {"recorded"}:
        entry["case"]["evidence"]["conflict"] = json.loads((OUT / conflict["recorded"]).read_text())
    return entry


def replay(entry: dict) -> dict:
    """Lean's answer to the recorded request, checked against it by the relay (`ve.ask._ask`), no generator run."""
    from ve.ask import Prepared, _context, _identities, read
    from ve.document import load_document
    raw = (ROOT / entry["path"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
        raise SystemExit(f"{entry['id']}: the fixture document changed")
    reading = read(raw, entry["question"])
    doc = load_document(ROOT / entry["path"])
    lexicon, expected = _identities(raw, entry["question"], doc)
    request = {"id": "ask", "document": raw.decode("utf-8"), "question": entry["question"], "lexicon": lexicon,
               "case": entry["case"], "names": entry["names"]}
    route = entry["result"]["route"]

    class _NoSplits:
        def splits(self, case, rows):
            return False
    return Prepared(request, _context(request, doc, raw, reading, route), expected, _NoSplits()).ask()


def check() -> int:
    failures = 0
    for ident, _, _ in FIXTURES:
        entry = load(ident)
        if "error" in entry:
            continue
        if replay(entry) != entry["result"]:
            print(f"{ident}: Lean's answer differs from the recorded one")
            failures += 1
    print(f"{len(FIXTURES) - failures} of {len(FIXTURES)} recorded answers replayed")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("ids", nargs="*")
    args = parser.parse_args()
    if args.write:
        return write(args.ids)
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
