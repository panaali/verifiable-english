"""Lean-first A/B: the base commit and the batch head over the same corpora (docs/LEAN-FIRST-PLAN.md,
section 5.1 item 2).

Usage::

    tools/lean_first_diff.py record --root DIR --out FILE [--corpus NAME ...] [--authority A ...]
    tools/lean_first_diff.py compare BASE HEAD [--delta FILE] [--json OUT]

``record`` imports the `ve` package of the checkout at ``--root`` (its sources and its Lean and
Rust builds) in a child process and writes one record per public result, so a base commit is
recorded from a worktree of it and the head from this checkout. The corpora are read from that
checkout too; each record carries the SHA-256 of the corpus file it came from, and ``compare``
refuses two runs whose corpus files differ: both sides must see the same inputs.

Corpora (``--corpus``, default all):

* ``probe``: the Stage-0 probe matrix (`tests/probe_matrix.py`), every cell and named probe,
  under each ``--authority`` (default ``python`` and ``lean``; the backend side is
  `tools/stage2_parity.py`'s).
* ``conformance``: `conformance/{evaluation,parser,identity,validation,closure,countermodels}.json`,
  every case through the public operations it exercises (environment and model validation,
  parse and canonical text, typing, meaning and source identities, evaluation, the
  countermodel check), under each authority.
* ``pilots``: every `.ve.md` document of every `pilot/*` branch, deduplicated by content,
  through `ve document check` (one process per document, under the default authority).

A record is ``{"corpus", "authority", "case", "op", "source_sha256", "outcome"}``; the outcome is
``{"returned": <public record>}`` or ``{"raised": <error record>}``, as mig3's recorder writes
them (`docs/spec/mig3.md` 2.4, on `mig3/py`): ``to_dict()`` where the value has one, dataclass
fields, containers member by member, and for an exception ``to_dict()`` or ``{code, message}``.
Members named ``checker_build`` or ``record_id`` are dropped (`probe_matrix.baseline_projection`).

``compare`` pairs the records by ``(corpus, authority, case, op)`` and gives every difference
mig3's fine classes (2.5: the path walk), then the plan's change class:

* ``availability``: one side is ``CheckerUnavailable`` and the other is not;
* ``wording``: only diagnostic texts differ (``message`` or ``detail`` leaves);
* ``order``: both sides raised and the codes differ (another fault is reported first);
* ``verdict``: anything else (verdicts, identities, counts, structure, a missing record).

``--delta`` names the batch's signed list. ``wording`` is a list of text pairs ``{"base", "head"}``
(mig3 2.4's wording map, signed as one block): a wording difference is accepted when every text
that differs is a listed pair. ``order``, ``verdict`` and ``availability`` list records, each
``{"corpus", "authority", "case", "op", "base", "head"}`` with the two outcomes, accepted only when
both outcomes are exactly the listed ones. Exit 0 when every difference is listed, 1 otherwise,
2 on unusable input.

``compare`` is evidence only when both runs recorded the gate's corpora: it refuses (exit 2) the
same file given twice, a run without records and runs over different corpus files, and fails
(exit 1, ``problems``) when a corpus of ``--corpus`` (default all; under each ``--authority``, the
pilots under ``default``) has no record on a side, or when every record of a corpus is
unavailable on both sides (two runs that checked nothing agree).
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CORPORA = ("probe", "conformance", "pilots")
AUTHORITIES = ("python", "lean")
CONFORMANCE = ("evaluation", "parser", "identity", "validation", "closure", "countermodels")
DROPPED = frozenset({"checker_build", "record_id"})
CLASSES = ("availability", "verdict", "order", "wording")
# mig3 2.5: the members whose leaf differences are verdicts, identities and counts.
VERDICT_KEYS = frozenset({"status", "valid", "value", "values", "refutes", "composed", "verdict", "cell"})
IDENTITY_KEYS = frozenset({"environment_id", "source_id", "meaning_id", "model_id", "claim_id", "edge_id",
                           "graph_id", "report_id", "document_hash"})
COUNT_KEYS = frozenset({"evaluations", "steps", "models_checked"})
PILOT_TIMEOUT = 600


# --- records ---------------------------------------------------------------------------

def public(value):
    """mig3 2.4 `_record`: the public record of a returned value."""
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return public(value.to_dict())
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {f.name: public(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, dict):
        return {str(k): public(v) for k, v in value.items() if k not in DROPPED}
    if isinstance(value, (list, tuple)):
        return [public(v) for v in value]
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return f"<unserializable {type(value).__name__}>"


def error_record(exc: BaseException) -> dict:
    """mig3 2.4: the error record of a raised exception."""
    if hasattr(exc, "to_dict"):
        return public(exc.to_dict())
    return {"code": getattr(exc, "code", type(exc).__name__), "message": str(exc)}


def outcome(call) -> dict:
    try:
        return {"returned": public(call())}
    except Exception as exc:  # noqa: BLE001  (every outcome is recorded; the comparison judges it)
        return {"raised": error_record(exc)}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- the corpora (run in the child, importing the recorded checkout's `ve`) -------------------

def probe_records(root: Path, authority: str):
    from tests import probe_matrix as probe
    from tools import stage2_parity
    from ve.backends import dispatch
    if stage2_parity._observe not in dispatch.observers:
        dispatch.observers.append(stage2_parity._observe)
        probe.outcome = stage2_parity._outcome
        probe.graph_baselines = stage2_parity._backend_graph_baselines
    data = stage2_parity._generate(authority)
    source = digest(root / "tests/probe_matrix.py")
    for row in data["cells"]:
        key = [row.get("language", "ve.core@0.2"), list(row["profiles"]), row["operation"], row["input_class"]]
        yield {"case": json.dumps(key), "op": row["operation"], "source_sha256": source,
               "outcome": {"cell": row["cell"], "status": row["status"], "output": public(row["output"])}}
    for section in ("graph_probes", "budget_boundaries", "feature_probes"):
        for name, row in data[section].items():
            yield {"case": f"{section}/{name}", "op": section, "source_sha256": source,
                   "outcome": public({k: v for k, v in row.items() if k != "routed"})
                   if isinstance(row, dict) else public(row)}


def identified(value, identity: str) -> dict:
    """A container's public record with its identity, which `to_dict` leaves out."""
    return {identity: getattr(value, identity), "record": public(value)}


def conformance_records(root: Path, authority: str):
    from ve import (Environment, FiniteModel, canonicalize, check_countermodel, check_document,
                    document_from_data, evaluate, formula_from_data, meaning_id, parse, source_id)
    for name in CONFORMANCE:
        path = root / f"conformance/{name}.json"
        source = digest(path)
        for case in json.loads(path.read_text()):
            base = {"case": f"{name}/{case['id']}", "source_sha256": source}
            env_out = outcome(lambda: identified(Environment(case["environment"]), "environment_id"))
            yield {**base, "op": "environment", "outcome": env_out}
            if "returned" not in env_out:
                continue
            env = Environment(case["environment"])
            model = None
            if "model" in case:
                model_out = outcome(lambda: identified(FiniteModel.from_dict(env, case["model"]), "model_id"))
                yield {**base, "op": "model", "outcome": model_out}
                if "returned" in model_out:
                    model = FiniteModel.from_dict(env, case["model"])
            if isinstance(case.get("source"), str):
                yield {**base, "op": "parse", "outcome": outcome(lambda: parse(env, case["source"]))}
                yield {**base, "op": "canonicalize", "outcome": outcome(lambda: canonicalize(env, case["source"]))}
                yield {**base, "op": "source_id", "outcome": outcome(lambda: source_id(case["source"], env))}
            if "ast" in case:
                doc_out = outcome(lambda: check_document(env, document_from_data(env, case["ast"])))
                yield {**base, "op": "typing", "outcome": doc_out}
                if "returned" in doc_out:
                    document = check_document(env, document_from_data(env, case["ast"]))
                    yield {**base, "op": "meaning_id", "outcome": outcome(lambda: meaning_id(env, document))}
                    if model is not None:
                        yield {**base, "op": "evaluate", "outcome": outcome(lambda: evaluate(env, document, model))}
            if "conclusion" in case and model is not None:
                def countermodel():
                    premises = [formula_from_data(env, p) for p in case["premises"]]
                    return check_countermodel(env, premises, formula_from_data(env, case["conclusion"]), model)
                yield {**base, "op": "countermodel_check", "outcome": outcome(countermodel)}


def pilot_documents(root: Path) -> list[tuple[str, str, bytes]]:
    """(name, sha256, text) of every `.ve.md` on every `pilot/*` branch, once per content."""
    def git(*args):
        return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True).stdout
    branches = git("for-each-ref", "--format=%(refname:short)", "refs/heads/pilot/").decode().split()
    seen: dict[str, tuple[str, str, bytes]] = {}
    for branch in sorted(branches):
        listing = git("ls-tree", "-r", "--format=%(objectname) %(path)", branch, "--", "usecases").decode()
        for line in listing.splitlines():
            blob, path = line.split(" ", 1)
            if path.endswith(".ve.md") and blob not in seen:
                seen[blob] = (f"{branch}:{path}", blob, b"")
    out = []
    for blob, (name, _, _) in sorted(seen.items(), key=lambda item: item[1][0]):
        out.append((name, blob, git("cat-file", "blob", blob)))
    return out


def pilot_records(root: Path, scratch: Path, workers: int):
    """`ve document check` of each pilot document, one process each, in the recorded checkout."""
    documents = pilot_documents(ROOT)
    scratch.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONPATH": str(root)}
    env.pop("VE_AUTHORITY", None)

    def check(item):
        name, blob, text = item
        path = scratch / f"{blob}.ve.md"
        path.write_bytes(text)
        try:
            done = subprocess.run([sys.executable, "-m", "ve", "document", "check", str(path)], cwd=root,
                                  env=env, capture_output=True, timeout=PILOT_TIMEOUT)
            result = {"exit": done.returncode, "stdout": done.stdout.decode("utf-8", "replace"),
                      "stderr": done.stderr.decode("utf-8", "replace").strip().splitlines()[-1:]}
        except subprocess.TimeoutExpired:
            result = {"timeout": PILOT_TIMEOUT}
        return {"case": name, "op": "document_check", "source_sha256": blob, "authority": "default",
                "outcome": result}

    with ThreadPoolExecutor(max_workers=workers) as pool:
        yield from pool.map(check, documents)


def child(args) -> int:
    root = Path(args.root).resolve()
    import ve
    if not Path(ve.__file__).resolve().is_relative_to(root):
        print(f"ve imported from {ve.__file__}, not from {root}", file=sys.stderr)
        return 2
    with open(args.out, "w") as out:
        def write(record):
            out.write(json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
            out.flush()
        for corpus in args.corpus:
            if corpus == "pilots":
                for record in pilot_records(root, Path(args.out).with_suffix(".pilots"), args.workers):
                    write({"corpus": corpus, **record})
                continue
            for authority in args.authority:
                os.environ["VE_AUTHORITY"] = authority
                produce = probe_records if corpus == "probe" else conformance_records
                for record in produce(root, authority):
                    write({"corpus": corpus, "authority": authority, **record})
                os.environ.pop("VE_AUTHORITY", None)
    return 0


def record(args) -> int:
    root = Path(args.root).resolve()
    env = {**os.environ, "PYTHONPATH": str(root)}
    command = [sys.executable, str(Path(__file__).resolve()), "_child", "--root", str(root),
               "--out", str(Path(args.out).resolve()),
               "--workers", str(args.workers), "--corpus", *args.corpus, "--authority", *args.authority]
    return subprocess.run(command, cwd=root, env=env).returncode


# --- comparison ------------------------------------------------------------------------

class Unusable(SystemExit):
    """Input that cannot show a difference or its absence (exit 2)."""


def load(path: str) -> dict[tuple, dict]:
    records = {}
    for line in Path(path).read_text().split("\n"):
        if not line:
            continue
        row = json.loads(line)
        key = (row["corpus"], row["authority"], row["case"], row["op"])
        if key in records:
            raise SystemExit(f"{path}: duplicate record {key}")
        records[key] = row
    return records


def leaf_differences(a, b, path=()):
    """mig3 2.5 case A: (path, kind) for each difference; kind is `shape` or `leaf`."""
    if type(a) is not type(b):
        return [(path, "shape")]
    if isinstance(a, dict):
        if a.keys() != b.keys():
            return [(path, "shape")]
        return [d for k in a for d in leaf_differences(a[k], b[k], path + (k,))]
    if isinstance(a, list):
        if len(a) != len(b):
            return [(path, "shape")]
        return [d for x, y in zip(a, b) for d in leaf_differences(x, y, path)]
    return [] if a == b else [(path, "leaf")]


def _unavailable(outcome) -> bool:
    text = json.dumps(outcome)
    return '"CheckerUnavailable' in text or '"timeout"' in text


def change_class(base: dict | None, head: dict | None) -> str | None:
    """The plan's class of a difference between two outcomes, or None when equal."""
    if base == head:
        return None
    if base is None or head is None:
        return "verdict"
    if _unavailable(base) != _unavailable(head):
        return "availability"
    a_raised, b_raised = _raised(base), _raised(head)
    if a_raised is not None and b_raised is not None and a_raised.get("code") != b_raised.get("code"):
        return "order"
    differences = leaf_differences(base, head)
    if differences and all(kind == "leaf" and path and path[-1] in ("message", "detail", "stderr")
                           for path, kind in differences):
        return "wording"
    return "verdict"


def _raised(outcome: dict):
    """The error record of an outcome that is a rejection, wherever the corpus keeps it."""
    if "raised" in outcome:
        return outcome["raised"]
    output = outcome.get("output")
    if outcome.get("cell") in ("R", "U", "X") and isinstance(output, dict) and "code" in output:
        return output
    return None


def text_pairs(base, head, path=()):
    """The (base, head) texts of the `message` and `detail` leaves that differ."""
    if isinstance(base, dict) and isinstance(head, dict):
        return [p for k in base.keys() & head.keys() for p in text_pairs(base[k], head[k], path + (k,))]
    if isinstance(base, list) and isinstance(head, list):
        return [p for x, y in zip(base, head) for p in text_pairs(x, y, path)]
    return [(base, head)] if base != head and path and path[-1] in ("message", "detail", "stderr") else []


def expected_groups(corpora=CORPORA, authorities=AUTHORITIES) -> set[tuple[str, str]]:
    """The (corpus, authority) record groups a run of `record` over these corpora writes."""
    return {(corpus, "default" if corpus == "pilots" else authority) for corpus in corpora for authority in authorities}


def compare(base_path: str, head_path: str, delta: dict | None, expect: set | None = None) -> dict:
    if Path(base_path).resolve() == Path(head_path).resolve():
        raise Unusable(f"BASE and HEAD are the same file {base_path}")
    base, head = load(base_path), load(head_path)
    for path, records in ((base_path, base), (head_path, head)):
        if not records:
            raise Unusable(f"{path} holds no record")
    sources = Counter()
    for key in base.keys() & head.keys():
        if base[key]["source_sha256"] != head[key]["source_sha256"]:
            sources[key[0]] += 1
    if sources:
        raise Unusable(f"the two runs read different corpus files: {dict(sources)}")
    delta = delta or {}
    wording = {(pair["base"], pair["head"]) for pair in delta.get("wording", [])}
    listed = {}
    for klass in ("order", "verdict", "availability"):
        for entry in delta.get(klass, []):
            key = (entry["corpus"], entry["authority"], entry["case"], entry["op"])
            if key in listed:
                # One entry per record: a second would silently replace the first (lf-1 recheck B's class).
                raise Unusable(f"the delta lists the record {key} twice")
            listed[key] = (klass, entry)
    rows, totals, unlisted = [], Counter(), []
    for key in sorted(base.keys() | head.keys()):
        old = base.get(key, {}).get("outcome")
        new = head.get(key, {}).get("outcome")
        klass = change_class(old, new)
        if klass is None:
            totals["same"] += 1
            continue
        totals[klass] += 1
        entry = listed.get(key)
        if klass == "wording":
            accepted = all(pair in wording for pair in text_pairs(old, new))
        else:
            accepted = (entry is not None and entry[0] == klass and "base" in entry[1] and "head" in entry[1]
                        and entry[1]["base"] == old and entry[1]["head"] == new)
        row = {"corpus": key[0], "authority": key[1], "case": key[2], "op": key[3], "class": klass,
               "base": old, "head": new, "listed": accepted}
        rows.append(row)
        if not accepted:
            unlisted.append(row)
    by_corpus = Counter((key[0], key[1]) for key in base.keys() | head.keys())
    problems = []
    for side, records in (("BASE", base), ("HEAD", head)):
        present = {(key[0], key[1]) for key in records}
        problems += [f"{side} has no record of {c}/{a}" for c, a in sorted((expect or set()) - present)]
    unavailable = Counter()
    for key in base.keys() & head.keys():
        if _unavailable(base[key]["outcome"]) and _unavailable(head[key]["outcome"]):
            unavailable[(key[0], key[1])] += 1
    problems += [f"every record of {c}/{a} is unavailable on both sides" for (c, a), n in sorted(unavailable.items())
                 if n == by_corpus[(c, a)]]
    return {"totals": dict(totals), "records": {f"{c}/{a}": n for (c, a), n in sorted(by_corpus.items())},
            "unavailable_both": {f"{c}/{a}": n for (c, a), n in sorted(unavailable.items())},
            "differences": rows, "unlisted": len(unlisted), "problems": problems}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("record", "_child"):
        p = sub.add_parser(name)
        p.add_argument("--root", required=True)
        p.add_argument("--out", required=True)
        p.add_argument("--corpus", nargs="+", default=list(CORPORA), choices=CORPORA)
        p.add_argument("--authority", nargs="+", default=list(AUTHORITIES), choices=AUTHORITIES)
        p.add_argument("--workers", type=int, default=4)
    p = sub.add_parser("compare")
    p.add_argument("base")
    p.add_argument("head")
    p.add_argument("--delta", type=Path)
    p.add_argument("--json", type=Path)
    p.add_argument("--corpus", nargs="+", default=list(CORPORA), choices=CORPORA)
    p.add_argument("--authority", nargs="+", default=list(AUTHORITIES), choices=AUTHORITIES)
    args = parser.parse_args(argv)
    if args.command == "record":
        return record(args)
    if args.command == "_child":
        return child(args)
    delta = json.loads(args.delta.read_text()) if args.delta else None
    try:
        result = compare(args.base, args.head, delta, expected_groups(args.corpus, args.authority))
    except Unusable as exc:
        print(f"lean_first_diff: {exc}", file=sys.stderr)
        return 2
    if args.json:
        args.json.write_text(json.dumps(result, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({"records": result["records"], "totals": result["totals"], "unlisted": result["unlisted"],
                      "unavailable_both": result["unavailable_both"], "problems": result["problems"]},
                     indent=1, sort_keys=True))
    for row in result["differences"][:20]:
        if not row["listed"]:
            print(f"UNLISTED {row['class']}: {row['corpus']}/{row['authority']} {row['op']} {row['case']}")
    return 0 if result["unlisted"] == 0 and not result["problems"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
