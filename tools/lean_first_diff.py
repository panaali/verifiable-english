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
  through `ve document check` (one process per document, under the default authority). A
  report that is JSON is recorded parsed, so that its members are compared one by one.
* ``readings``: `ve.readings_route.validate` on the 1,000 documents of the readings
  differential (`tests/test_readings_s1_differential.py`, the search's situations recorded)
  and on every environment-null case of `tests/test_readings_s1_lean.py` (batch 3). The
  documents are generated once, by this checkout, into a file both sides read.
* ``discourse``: every `ve-document@2` text of `docs/lean-first/discourse-corpus.json.gz` (the
  documents the discourse tests write, captured at batch 4's base by
  `docs/lean-first/b4/capture_discourse.py`), each written with the sibling files its imports name
  to its own scratch directory, through `check_document` and `render_document` (under the default
  authority, `--workers` processes).
* ``rights``: the rights profile's own generated corpus (`conformance/rights_differential.py`, seeds 0 to
  `RIGHTS_COUNT` - 1, accepted and rejected sources alike), each written as a ve-document (`document_text`),
  and every `RIGHTS_HEADED`-th again under the head profile ``readings@1`` with no reading set (the lower
  rights chain under its head, lean-first batch 7 review B3), through `check_document` and `render_document`.
  The documents are generated once, by this checkout, into a file both sides read. Every differential
  generator of ``conformance/`` is a corpus here or is named in `GENERATORS_NOT_RECORDED` with the reason
  (batch 7 review B2: the batch's own profile corpus was left out).
* ``quantity``: every W6 call of `docs/lean-first/quantity-corpus.json.gz` (the calls the W6 tests make
  to a quantity public operation, captured at batch 9's base by `docs/lean-first/b9/capture_quantity.py`),
  each through its one operation (`QUANTITY_OPS`: `Environment`, `elaborate_quantity`,
  `quantity_meaning_id`, `quantity_countermodel`, `check_quantity_certificate`, `prove_quantity`,
  `admit_document`), under each authority (`--workers` processes).
* ``norm_defaults``: 1,000 generated profile documents and ten malformed variants from
  `conformance/norm_defaults_differential.py`, each through `check_document` and
  `render_document` at both revisions.
* ``document``: every `ve-document@1` seed of `conformance/document_wrapper.py` and the differential fuzzer's
  document mutants, frozen in `docs/lean-first/document-corpus.json.gz` at batch 16b's base
  (`docs/lean-first/b16b/capture_documents.py`), each through `check_document` and `render_document`. The texts
  are written once, by this checkout, into a file both sides read.

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

``compare`` refuses evidence that cannot show preservation (exit 2). Before it uses a record, every
line must be one the recorder writes (`record_problem`, the schema `tools/lean_first_schema/record.json`:
each corpus's fields, authorities and sources, each operation's outcome, a rejection's complete
diagnostic), and the records of one corpus file must name one digest; an empty, partial or retyped
outcome is no acceptance. Then, for every corpus and authority
it checks (``--corpus``, ``--authority``, default all; the pilots and the readings, discourse
and rights corpora have the one authority ``default``), each side must hold a record of every case of
the corpus as this checkout defines it (`expected_cases`: the conformance files' case ids, the probe
matrix's frozen baseline, the pilot documents, the readings corpus's cases, the discourse and quantity
corpora's ids, the rights corpus's cases), through every operation the case requires (a conformance
case: `CONFORMANCE_OPS`, given the outcomes recorded for it; a probe case: its operation; a pilot:
``document_check``; a readings case: ``readings_validate``; a discourse document or a rights document:
`DOCUMENT_OPS`; a quantity call: its one operation),
and nothing else, some of its records must be available, and it must hold both an
acceptance and a rejection (every corpus holds both kinds of input). A record unavailable on
both sides is no evidence either (class ``unavailable``, whatever its texts): it is accepted only
when the delta lists it under ``unavailable`` with a ``reason`` (``{"corpus", "authority", "case",
"op", "reason"}``); one unavailable on one side only is an ``availability`` difference. Outcomes
are compared as JSON, with types: ``true`` is not ``1``.

``--delta`` names the batch's signed list. ``wording`` is a list of text pairs ``{"base", "head"}``
(mig3 2.4's wording map, signed as one block): a wording difference is accepted when every text
that differs is a listed pair. ``order``, ``verdict`` and ``availability`` list records, each
``{"corpus", "authority", "case", "op", "base", "head"}`` with the two outcomes, accepted only when
both outcomes are exactly the listed ones. Exit 0 when every difference is listed, 1 otherwise,
2 on unusable input.

``compare`` also refuses (exit 2) the same file given twice, and a delta that lists one record
twice (a second entry would replace the first) or names a record by a key that is not four strings
(`1` and `true` would name one record). A listed record names both outcomes, and a wording pair is
matched with its JSON types.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import dataclasses
from functools import cache
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CORPORA = ("probe", "conformance", "pilots", "readings", "discourse", "rights", "quantity",
           "norm_defaults", "document")
DISCOURSE = Path("docs/lean-first/discourse-corpus.json.gz")
DOCUMENTS = Path("docs/lean-first/document-corpus.json.gz")
DOCUMENT_OPS = ("document_check", "document_render")
QUANTITY = Path("docs/lean-first/quantity-corpus.json.gz")
QUANTITY_OPS = ("environment", "elaborate", "meaning_id", "countermodel", "certificate", "prove", "admission")
AUTHORITIES = ("python", "lean")
CONFORMANCE = ("evaluation", "parser", "identity", "validation", "closure", "countermodels")
DROPPED = frozenset({"checker_build", "record_id"})
PROBE_METADATA = frozenset({"routed", "backend_rejection"})
CLASSES = ("availability", "verdict", "order", "wording")
TEXTS = ("message", "detail", "stderr")
# A report's statement of who checked what is descriptive text: a change to it is wording.
DESCRIPTIONS = ("checked_by",)
# mig3 2.5: the members whose leaf differences are verdicts, identities and counts.
VERDICT_KEYS = frozenset({"status", "valid", "value", "values", "refutes", "composed", "verdict", "cell"})
IDENTITY_KEYS = frozenset({"environment_id", "source_id", "meaning_id", "model_id", "claim_id", "edge_id",
                           "graph_id", "report_id", "document_hash"})
COUNT_KEYS = frozenset({"evaluations", "steps", "models_checked"})
PILOT_TIMEOUT = 600
READINGS_COUNT = 1000  # the readings differential's documents (composition-s1.md 9.3)
RIGHTS_COUNT = 1000  # the rights differential's generator seeds (rights.md 10)
RIGHTS_HEADED = 4  # every fourth rights source is recorded again under readings@1
# The differential generators of `conformance/` that are a corpus here, and those that are not, with the reason.
GENERATED_CORPORA = {"rights": "conformance/rights_differential.py",
                     "norm_defaults": "conformance/norm_defaults_differential.py"}
GENERATORS_NOT_RECORDED = {}
PROBE_BASELINE = "conformance/baseline-2026-09/python.json"
PROBE_SECTIONS = ("graph_probes", "budget_boundaries", "feature_probes")


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

def probe_case(row: dict) -> str:
    """The case key of a probe matrix cell."""
    return json.dumps([row.get("language", "ve.core@0.2"), list(row["profiles"]), row["operation"],
                       row["input_class"]])


def probe_records(root: Path, authority: str):
    from tests import probe_matrix as probe
    from tools import stage2_parity
    from ve.backends import dispatch
    if stage2_parity._observe not in dispatch.observers:
        dispatch.observers.append(stage2_parity._observe)
        probe.outcome = stage2_parity._outcome
        probe.graph_baselines = stage2_parity._backend_graph_baselines
    yield from probe_rows(stage2_parity._generate(authority), digest(root / "tests/probe_matrix.py"))


def probe_rows(data: dict, source: str):
    """The records of the probe matrix's results `data` (cells and named probes, the form of
    `PROBE_BASELINE`), read from the file of digest `source`."""
    for row in data["cells"]:
        yield {"case": probe_case(row), "op": row["operation"], "source_sha256": source,
               "outcome": {"cell": row["cell"], "status": row["status"],
                           "output": probe_public(row["output"])}}
    for section in PROBE_SECTIONS:
        for name, row in data[section].items():
            yield {"case": f"{section}/{name}", "op": section, "source_sha256": source,
                   "outcome": probe_public(row)}


def probe_public(value):
    """The probe matrix's route observer and backend marker are test instrumentation,
    not fields returned by the public operation. Keep nested budget results public."""
    value = public(value)
    if isinstance(value, dict):
        return {k: probe_public(v) for k, v in value.items() if k not in PROBE_METADATA}
    if isinstance(value, list):
        return [probe_public(v) for v in value]
    return value


def identified(value, identity: str) -> dict:
    """A container's public record with its identity, which `to_dict` leaves out."""
    return {identity: getattr(value, identity), "record": public(value)}


# The public operations a conformance case is recorded through, in order: (operation, whether the
# case holds its input, the operations that must have returned first). The one table of both the
# recorder (`conformance_records`) and the completeness check (`conformance_ops`).
CONFORMANCE_OPS = (
    ("environment", lambda case: True, ()),
    ("model", lambda case: "model" in case, ("environment",)),
    ("parse", lambda case: isinstance(case.get("source"), str), ("environment",)),
    ("canonicalize", lambda case: isinstance(case.get("source"), str), ("environment",)),
    ("source_id", lambda case: isinstance(case.get("source"), str), ("environment",)),
    ("typing", lambda case: "ast" in case, ("environment",)),
    ("meaning_id", lambda case: "ast" in case, ("typing",)),
    ("evaluate", lambda case: "ast" in case, ("typing", "model")),
    ("countermodel_check", lambda case: "conclusion" in case, ("model",)),
)


def conformance_ops(case: dict, outcome_of) -> dict[str, dict | None]:
    """The operations conformance case `case` is recorded through (`CONFORMANCE_OPS`), in order,
    each with its outcome `outcome_of(op)` (None for one a recording lacks): an operation runs when
    the case holds its input and every operation it builds on returned."""
    outcomes: dict[str, dict | None] = {}
    for op, holds, after in CONFORMANCE_OPS:
        if holds(case) and all("returned" in (outcomes.get(p) or {}) for p in after):
            outcomes[op] = outcome_of(op)
    return outcomes


def conformance_calls(case: dict) -> dict:
    """The call of each operation of `CONFORMANCE_OPS` on `case`; the environment, model and
    checked document are built once per case."""
    from functools import cache
    from ve import (Environment, FiniteModel, canonicalize, check_countermodel, check_document,
                    document_from_data, evaluate, formula_from_data, meaning_id, parse, source_id)
    env = cache(lambda: Environment(case["environment"]))
    model = cache(lambda: FiniteModel.from_dict(env(), case["model"]))
    document = cache(lambda: check_document(env(), document_from_data(env(), case["ast"])))

    def countermodel():
        premises = [formula_from_data(env(), p) for p in case["premises"]]
        return check_countermodel(env(), premises, formula_from_data(env(), case["conclusion"]), model())

    return {"environment": lambda: identified(env(), "environment_id"),
            "model": lambda: identified(model(), "model_id"),
            "parse": lambda: parse(env(), case["source"]),
            "canonicalize": lambda: canonicalize(env(), case["source"]),
            "source_id": lambda: source_id(case["source"], env()),
            "typing": document,
            "meaning_id": lambda: meaning_id(env(), document()),
            "evaluate": lambda: evaluate(env(), document(), model()),
            "countermodel_check": countermodel}


def conformance_records(root: Path, authority: str):
    for name in CONFORMANCE:
        path = root / f"conformance/{name}.json"
        source = digest(path)
        for case in json.loads(path.read_text()):
            calls = conformance_calls(case)
            for op, out in conformance_ops(case, lambda op: outcome(calls[op])).items():
                yield {"case": f"{name}/{case['id']}", "source_sha256": source, "op": op, "outcome": out}


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


def pilot_companions(root: Path, name: str, text: bytes) -> dict[str, bytes]:
    """The files of a pilot document's branch that its front matter names beside it: each string of `senses.packs`
    (the only member a loader reads a file by) resolved against the document's directory, where the branch holds a
    file there. A bundled pack's name names none. The checker decides which of them it reads (lf-16f review F2:
    a document written alone lost the pack beside it)."""
    import posixpath
    branch, colon, path = name.partition(":")
    if not colon:
        return {}
    try:
        meta = json.loads(text[4:text.index(b"\n---\n", 4)])
        packs = meta["senses"]["packs"]
    except (ValueError, TypeError, KeyError):
        return {}
    out = {}
    for entry in packs if type(packs) is list else ():
        if type(entry) is not str:
            continue
        target = posixpath.normpath(posixpath.join(posixpath.dirname(path), entry))
        if target.startswith("../") or target == ".." or posixpath.isabs(target):
            continue
        done = subprocess.run(["git", "cat-file", "blob", f"{branch}:{target}"], cwd=root, capture_output=True)
        if done.returncode == 0:
            out[target] = done.stdout
    return out


def write_pilot(root: Path, directory: Path, name: str, blob: str, text: bytes) -> Path:
    """Write a pilot document where a checker reads it: `<blob>.ve.md`, or, when it names files beside it
    (`pilot_companions`), at its branch path under `<blob>/` with those files where the branch holds them, so it is
    checked as it is loaded in place."""
    companions = pilot_companions(root, name, text)
    if not companions:
        path = directory / f"{blob}.ve.md"
        path.write_bytes(text)
        return path
    base = directory / blob
    for target, data in companions.items():
        (base / target).parent.mkdir(parents=True, exist_ok=True)
        (base / target).write_bytes(data)
    path = base / name.split(":", 1)[1]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text)
    return path


def pilot_records(root: Path, scratch: Path, workers: int):
    """`ve document check` of each pilot document, one process each, in the recorded checkout."""
    documents = pilot_documents(ROOT)
    scratch.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONPATH": str(root)}
    # A recorded checkout may be read-only. The English shadow is diagnostic
    # output, so keep it beside the recording instead of writing in that tree.
    env["VE_SHADOW_LOG"] = str(scratch / "english-shadow.jsonl")
    env.pop("VE_AUTHORITY", None)

    def check(item):
        name, blob, text = item
        path = write_pilot(ROOT, scratch, name, blob, text)
        return {"case": name, "op": "document_check", "source_sha256": blob, "authority": "default",
                "outcome": pilot_check(root, path, env)}

    with ThreadPoolExecutor(max_workers=workers) as pool:
        yield from pool.map(check, documents)


def readings_corpus(out: Path) -> None:
    """Write the readings corpus: generated by this checkout's tests, read by both recorded sides."""
    from tests import test_readings_s1_differential as differential
    from tests import test_readings_s1_lean as fixtures
    from ve.errors import VEError
    from ve.readings_s1 import wire
    cases, _ = differential.generated_cases(READINGS_COUNT)
    rows = [{"case": f"differential/{c['id']}", "environment": c["environment"], "document": c["document"]}
            for c in cases]
    for name, path in fixtures.ENVIRONMENT_NULLS:
        make, make_document, unit_kind = fixtures.NULL_ENVIRONMENTS[name]
        nulled = fixtures._nulled(make(), path)
        try:
            document = make_document(wire(nulled))
        except (KeyError, TypeError, ValueError, VEError):
            document = make_document(make())
        for unit in document["units"]:
            unit.setdefault("kind", unit_kind)
        rows.append({"case": _null_case(name, path), "environment": nulled, "document": document})
    assert [row["case"] for row in rows] == readings_cases(), "the corpus names its cases as `readings_cases`"
    out.write_text(json.dumps(rows, ensure_ascii=False))


def _null_case(name: str, path) -> str:
    return f"nulls/{name}/{'.'.join(map(str, path))}"


def readings_cases() -> list[str]:
    """The case names of the readings corpus `readings_corpus` writes, without generating it: the
    differential's documents (ids `c0`, `c1`, ...) and the environment-null cases."""
    from tests import test_readings_s1_lean as fixtures
    return [f"differential/c{n}" for n in range(READINGS_COUNT)] + [
        _null_case(name, path) for name, path in fixtures.ENVIRONMENT_NULLS]


def readings_records(path: Path):
    from ve.errors import VEError  # noqa: F401  (the recorded checkout's classes)
    from ve.readings_route import validate
    source = digest(path)
    for case in json.loads(path.read_text()):
        document = case["document"]
        units = [{"id": u["id"], "kind": u.get("kind"), **({"content": u["content"]} if "content" in u else {})}
                 for u in document["units"]]
        yield {"case": case["case"], "op": "readings_validate", "source_sha256": source,
               "outcome": outcome(lambda: validate(case["environment"], units, document["reading_sets"]))}


def rights_corpus(out: Path) -> None:
    """Write the rights corpus: generated by this checkout's rights differential, read by both recorded sides."""
    from conformance import rights_differential as generator
    rows = []
    for seed in range(RIGHTS_COUNT):
        raw, units = generator.document(seed)
        rows.append({"case": f"s{seed}", "text": generator.document_text(raw, units)})
        if seed % RIGHTS_HEADED == 0:
            headed = {**raw, "profiles": sorted([*raw["profiles"], "readings@1"])}
            rows.append({"case": f"s{seed}/readings@1", "text": generator.document_text(headed, units)})
    assert [row["case"] for row in rows] == rights_cases(), "the corpus names its cases as `rights_cases`"
    out.write_text(json.dumps(rows, ensure_ascii=False))


def rights_cases() -> list[str]:
    """The case names of the rights corpus `rights_corpus` writes, without generating it."""
    return [name for seed in range(RIGHTS_COUNT)
            for name in ([f"s{seed}", f"s{seed}/readings@1"] if seed % RIGHTS_HEADED == 0 else [f"s{seed}"])]


def _rights_case(item):
    """`check_document` and `render_document` of one rights corpus document (in a pool worker)."""
    scratch, source, entry = item
    from ve.document import check_document, render_document
    directory = Path(scratch) / entry["case"].replace("/", "_")
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "document.ve.md"
    path.write_text(entry["text"])
    return [{"case": entry["case"], "op": op, "source_sha256": source, "authority": "default",
             "outcome": outcome(lambda: call(path))}
            for op, call in zip(DOCUMENT_OPS, (check_document, render_document))]


def rights_records(path: Path, scratch: Path, workers: int):
    """The rights corpus file `path` recorded with the child's `ve`."""
    import multiprocessing
    source = digest(path)
    os.environ.pop("VE_AUTHORITY", None)
    entries = [(str(scratch), source, entry) for entry in json.loads(path.read_text())]
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        for rows in pool.imap(_rights_case, entries, chunksize=8):
            yield from rows


def norm_defaults_cases() -> list[str]:
    return [f"s{seed}" for seed in range(1000)] + [f"invalid/{seed}" for seed in range(10)]


def norm_defaults_corpus(out: Path, *, trees: int = 1000, include_invalid: bool = True) -> None:
    """Freeze the profile generator's documents once for both revisions.

    A caller measuring a bounded prefix may request only that prefix; the
    default remains the full conformance corpus and its invalid cases.
    """
    if not 0 <= trees <= 1000:
        raise ValueError("norm-defaults trees must be between 0 and 1000")
    from conformance import norm_defaults_differential as generator
    rows, invalid = [], []
    for seed in range(trees):
        env, rules, _ = generator.case(seed, profiled=True)
        phrases = [f"Rule {index}.\n" for index in range(len(rules))] or ["No rule.\n"]
        cursor, units = 0, []
        for index, phrase in enumerate(phrases):
            end = cursor + len(phrase.encode())
            unit = {"id": f"u{index}", "span": [cursor, end],
                    "kind": "norm" if rules else "exposition", "meaning": "specified", "support": "none"}
            if rules:
                unit["content"] = rules[index].to_dict()
            units.append(unit)
            cursor = end
        front = {"format": "ve-document@1", "environment": env.to_dict(), "units": units}
        def encode(metadata):
            return "---\n" + json.dumps(metadata, ensure_ascii=False) + "\n---\n" + "".join(phrases)
        rows.append({"case": f"s{seed}", "text": encode(front)})
        if include_invalid and rules and len(invalid) < 10:
            damaged = json.loads(json.dumps(front))
            damaged["units"][0]["content"]["norm"]["predicate"] = "not_declared"
            invalid.append({"case": f"invalid/{len(invalid)}", "text": encode(damaged)})
    assert [row["case"] for row in rows + invalid] == (
        [f"s{seed}" for seed in range(trees)] + [f"invalid/{seed}" for seed in range(len(invalid))])
    out.write_text(json.dumps(rows + invalid, ensure_ascii=False))


def norm_defaults_records(path: Path, scratch: Path, workers: int):
    """The public document checks of each generated source in the recorded checkout."""
    import multiprocessing
    source = digest(path)
    os.environ.pop("VE_AUTHORITY", None)
    entries = [(str(scratch), source, entry) for entry in json.loads(path.read_text())]
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        for rows in pool.imap(_rights_case, entries, chunksize=8):
            yield from rows


def document_corpus(out: Path) -> None:
    """Write the document corpus's texts (`capture_documents.texts`), read by both recorded sides."""
    sys.path.insert(0, str(ROOT / "docs/lean-first/b16b"))
    from capture_documents import texts
    rows = [{"case": row["id"], "text": row["text"]} for row in texts(json.loads(gzip.decompress(
        (ROOT / DOCUMENTS).read_bytes())))]
    assert [row["case"] for row in rows] == document_cases(ROOT)
    out.write_text(json.dumps(rows, ensure_ascii=False))


def document_cases(root: Path) -> list[str]:
    """The case names of the document corpus of the checkout `root`, without writing its texts."""
    return [entry["id"] for entry in json.loads(gzip.decompress((root / DOCUMENTS).read_bytes()))["entries"]]


def _discourse_case(item):
    """`check_document` and `render_document` of one corpus document (in a pool worker)."""
    scratch, entry = item
    from ve.document import check_document, render_document
    directory = Path(scratch) / entry["id"]
    directory.mkdir(parents=True, exist_ok=True)
    for name, data in entry["files"].items():
        try:
            (directory / name).write_bytes(base64.b64decode(data))
        except OSError:
            pass  # a name no file can have stays absent, as it was in the test that wrote it
    path = directory / "document.ve.md"
    path.write_bytes(base64.b64decode(entry["document"]))
    source = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
    return [{"case": entry["id"], "op": op, "source_sha256": source, "authority": "default",
             "outcome": outcome(lambda: call(path))}
            for op, call in zip(DOCUMENT_OPS, (check_document, render_document))]


def discourse_corpus(root: Path) -> list[dict]:
    """The entries of the discourse corpus file of the checkout `root`."""
    return json.loads(gzip.decompress((root / DISCOURSE).read_bytes()))


def discourse_records(scratch: Path, workers: int):
    """The discourse corpus, read from this tool's checkout, recorded with the child's `ve`."""
    import multiprocessing
    corpus = discourse_corpus(ROOT)
    os.environ.pop("VE_AUTHORITY", None)
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        for rows in pool.imap(_discourse_case, [(str(scratch), entry) for entry in corpus], chunksize=8):
            yield from rows


def _quantity_call(entry: dict):
    """The one public W6 operation a quantity corpus entry names, on the recorded checkout's `ve`."""
    from ve.admission import admit_document
    from ve.environment import Environment
    from ve.units import (check_quantity_certificate, elaborate_quantity, prove_quantity,
                          quantity_countermodel, quantity_meaning_id)
    op = entry["op"]
    if op == "environment":
        env = Environment(entry["environment"])
        return {"environment_id": env.environment_id, "data": env.to_dict()}
    env = Environment(entry["environment"])
    if op == "elaborate":
        return elaborate_quantity(env, entry["quantity"])
    if op == "meaning_id":
        return quantity_meaning_id(env, entry["quantity"])
    if op == "countermodel":
        return quantity_countermodel(env, entry["premises"], entry["conclusion"], entry["model"])
    if op == "certificate":
        return check_quantity_certificate(env, entry["premises"], entry["conclusion"], entry["certificate"])
    if op == "prove":
        return prove_quantity(env, entry["premises"], entry["conclusion"])
    assert op == "admission", op
    return admit_document(env, entry["document"])


def _quantity_case(item):
    """One quantity corpus entry under one authority (in a pool worker)."""
    authority, entry = item
    os.environ["VE_AUTHORITY"] = authority
    source = hashlib.sha256(json.dumps(entry, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return {"case": entry["id"], "op": entry["op"], "source_sha256": source, "authority": authority,
            "outcome": outcome(lambda: _quantity_call(entry))}


def quantity_corpus(root: Path) -> list[dict]:
    """The entries of the quantity corpus file of the checkout `root`."""
    return json.loads(gzip.decompress((root / QUANTITY).read_bytes()))


def quantity_records(authorities, workers: int):
    """The quantity corpus, read from this tool's checkout, recorded with the child's `ve` under each
    authority."""
    import multiprocessing
    corpus = quantity_corpus(ROOT)
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        items = [(authority, entry) for authority in authorities for entry in corpus]
        yield from pool.imap(_quantity_case, items, chunksize=16)
    os.environ.pop("VE_AUTHORITY", None)


def pilot_check(root: Path, path: Path, env: dict) -> dict:
    """The outcome of `ve document check` of `path` in the checkout `root`."""
    try:
        done = subprocess.run([sys.executable, "-m", "ve", "document", "check", str(path)], cwd=root,
                              env=env, capture_output=True, timeout=PILOT_TIMEOUT)
    except subprocess.TimeoutExpired:
        return {"timeout": PILOT_TIMEOUT}
    stdout = done.stdout.decode("utf-8", "replace")
    try:
        report = json.loads(stdout)
    except ValueError:
        report = None
    # A report that is a JSON object is recorded parsed, so that its members are compared one by one.
    return {"exit": done.returncode, "stdout": report if type(report) is dict else stdout,
            "stderr": done.stderr.decode("utf-8", "replace").strip().splitlines()[-1:]}


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
            if corpus == "readings":
                for record in readings_records(Path(args.out).with_suffix(".readings.json")):
                    write({"corpus": corpus, "authority": "default", **record})
                continue
            if corpus == "pilots":
                for record in pilot_records(root, Path(args.out).with_suffix(".pilots"), args.workers):
                    write({"corpus": corpus, **record})
                continue
            if corpus == "rights":
                for record in rights_records(Path(args.out).with_suffix(".rights.json"),
                                             Path(args.out).with_suffix(".rights"), args.workers):
                    write({"corpus": corpus, **record})
                continue
            if corpus in ("norm_defaults", "document"):
                for record in norm_defaults_records(Path(args.out).with_suffix(f".{corpus}.json"),
                                                    Path(args.out).with_suffix(f".{corpus}"), args.workers):
                    write({"corpus": corpus, **record})
                continue
            if corpus == "discourse":
                for record in discourse_records(Path(args.out).with_suffix(".discourse"), args.workers):
                    write({"corpus": corpus, **record})
                continue
            if corpus == "quantity":
                for record in quantity_records(args.authority, args.workers):
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
    for name in ("readings", "rights", "norm_defaults", "document"):
        if name not in args.corpus:
            continue
        corpus = Path(args.out).resolve().with_suffix(f".{name}.json")
        if not corpus.exists():
            done = subprocess.run([sys.executable, str(Path(__file__).resolve()), f"_{name}_corpus",
                                   "--out", str(corpus)], cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT)})
            if done.returncode != 0:
                return 2
    env = {**os.environ, "PYTHONPATH": str(root)}
    command = [sys.executable, str(Path(__file__).resolve()), "_child", "--root", str(root),
               "--out", str(Path(args.out).resolve()),
               "--workers", str(args.workers), "--corpus", *args.corpus, "--authority", *args.authority]
    return subprocess.run(command, cwd=root, env=env).returncode


# --- comparison ------------------------------------------------------------------------

class Unusable(Exception):
    """Evidence that cannot show preservation: `compare` gives no verdict on it (exit 2)."""


def authorities_of(corpus: str, authorities=AUTHORITIES) -> tuple[str, ...]:
    return (("default",) if corpus in ("pilots", "readings", "discourse", "rights", "norm_defaults", "document")
            else tuple(authorities))


def only(op: str):
    """The operations of a case recorded through `op` alone, whatever its outcome."""
    return lambda held: {op}


def expected_cases(root: Path, corpora=CORPORA, authorities=AUTHORITIES) -> dict[tuple[str, str], dict]:
    """Every case each (corpus, authority) of a complete recording holds, from this checkout's
    corpora, not from a recording: the conformance files' case ids, the cells and named probes of
    the probe matrix's frozen baseline, the pilot documents, the readings corpus's cases and the
    discourse and quantity corpora's entries and the rights corpus's cases. Each case maps to its operations:
    a function of the outcomes a recording holds for the case (`{op: outcome}`) giving the set of
    operations it must hold, since a conformance case's later operations run only on what its
    earlier ones returned (`conformance_ops`)."""
    cases: dict[str, dict] = {}
    for corpus in corpora:
        if corpus == "conformance":
            cases[corpus] = {
                f"{name}/{case['id']}": (lambda held, case=case: set(conformance_ops(case, held.get)))
                for name in CONFORMANCE for case in json.loads((root / f"conformance/{name}.json").read_text())}
        elif corpus == "probe":
            baseline = json.loads((root / PROBE_BASELINE).read_text())
            cases[corpus] = {probe_case(row): only(row["operation"]) for row in baseline["cells"]} | {
                f"{section}/{name}": only(section) for section in PROBE_SECTIONS for name in baseline[section]}
        elif corpus == "readings":
            cases[corpus] = {name: only("readings_validate") for name in readings_cases()}
        elif corpus == "discourse":
            cases[corpus] = {entry["id"]: (lambda held: set(DOCUMENT_OPS)) for entry in discourse_corpus(root)}
        elif corpus == "rights":
            cases[corpus] = {name: (lambda held: set(DOCUMENT_OPS)) for name in rights_cases()}
        elif corpus == "norm_defaults":
            cases[corpus] = {name: (lambda held: set(DOCUMENT_OPS)) for name in norm_defaults_cases()}
        elif corpus == "document":
            cases[corpus] = {name: (lambda held: set(DOCUMENT_OPS)) for name in document_cases(root)}
        elif corpus == "quantity":
            cases[corpus] = {entry["id"]: only(entry["op"]) for entry in quantity_corpus(root)}
        else:
            cases[corpus] = {name: only("document_check") for name, _, _ in pilot_documents(root)}
    return {(corpus, authority): cases[corpus] for corpus in corpora
            for authority in authorities_of(corpus, authorities)}


SCHEMA = ROOT / "tools/lean_first_schema"


@cache
def _record_schema():
    from ve.backends.service_schema import Compiler
    return Compiler(SCHEMA).ref("record.json", "#/record")


def _cells(row: dict):
    """The probe outcomes a record holds (`probe_rows`): a cell, a feature probe, a boundary's pair."""
    outcome = row["outcome"]
    if row["corpus"] != "probe" or row["op"] == "graph_probes":
        return []
    if row["op"] == "budget_boundaries":
        return [outcome[side] for side in ("at", "over", "under") if side in outcome]
    return [outcome]


def record_problem(row) -> str | None:
    """Why `row` is not a record `record` writes, or None: the schema `lean_first_schema/record.json`
    (fields, their types, each corpus's authorities and sources, each operation's outcome, a
    rejection's complete diagnostic), then that a rejection cell's status is its error's code."""
    from ve.backends.service_schema import Context, Invalid
    try:
        _record_schema()[0](row, Context(row), {})
    except Invalid as exc:
        return str(exc)
    except RecursionError:
        return "nesting exceeds the reader's depth"
    for cell in _cells(row):
        if cell["cell"] != "S" and cell["status"] != cell["output"]["code"]:
            return "a rejection cell's status is not its error's code"
    return None


def _source_group(key: tuple) -> tuple:
    """The records that read one corpus file: a conformance file, the probe matrix, a pilot document,
    the readings corpus, a discourse corpus entry, the rights corpus."""
    corpus, _, case, _ = key
    return {"conformance": (corpus, case.split("/")[0]), "probe": (corpus,), "readings": (corpus,),
            "rights": (corpus,), "norm_defaults": (corpus,)}.get(
        corpus, (corpus, case))


def _unique_pairs(pairs):
    seen = {}
    for name, value in pairs:
        if name in seen:
            raise ValueError(f"duplicate field {name!r}")
        seen[name] = value
    return seen


def load(path: str) -> dict[tuple, dict]:
    """The records of the recording at `path`, each checked (`record_problem`) before any is used: a
    line the recorder cannot write, a duplicate record, or two records of one corpus file with
    different digests (mixed identity) is `Unusable`."""
    records, sources = {}, {}
    if not Path(path).is_file():
        raise Unusable(f"{path}: no recording")
    for number, line in enumerate(Path(path).read_text().split("\n"), 1):
        if not line:
            continue
        try:
            row = json.loads(line, object_pairs_hook=_unique_pairs)
        except ValueError as exc:
            raise Unusable(f"{path}: line {number} is not JSON ({exc})") from None
        problem = record_problem(row)
        if problem:
            raise Unusable(f"{path}: line {number} is no record the recorder writes: {problem}")
        key = (row["corpus"], row["authority"], row["case"], row["op"])
        if key in records:
            raise Unusable(f"{path}: duplicate record {key}")
        source = sources.setdefault(_source_group(key), row["source_sha256"])
        if source != row["source_sha256"]:
            raise Unusable(f"{path}: line {number} reads {'/'.join(_source_group(key))} with another digest")
        records[key] = row
    return records


def same(a, b) -> bool:
    """JSON equality with the response validator's types (`service_schema.same_json`): `true` is not `1`,
    `false` is not `0` and `1` is not `1.0`, as Python's `==` would have them. Every comparison of two
    outcomes, or of an outcome and a delta entry, goes through it (lf-1 recheck 3, B)."""
    from ve.backends.service_schema import same_json  # here, not at import: `_child` imports another checkout's `ve`
    return same_json(a, b)


def stable_pilot_outcome(outcome, recording: str):
    """Erase only the recorder's own temporary pilot directory from a result.

    The two checkouts write the same historical source bytes beside different
    recording files. A file-open diagnostic may quote that scratch directory;
    its suffix and every other part of the diagnostic remain compared.
    """
    scratch = str(Path(recording).resolve().with_suffix(".pilots")) + "/"

    def visit(value):
        if isinstance(value, str):
            return value.replace(scratch, "<pilot-scratch>/")
        if isinstance(value, list):
            return [visit(item) for item in value]
        if isinstance(value, dict):
            return {key: visit(item) for key, item in value.items()}
        return value

    return visit(outcome)


def json_text(value) -> str:
    """A leaf's identity in the wording pairs: its JSON text, so the pairs are type-strict too."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def record_key(row: dict, origin: str) -> tuple:
    """`(corpus, authority, case, op)`, each a string: a number or a boolean there would pair records
    that Python's `==` and hashing equate (`1` and `true`)."""
    key = tuple(row.get(name) for name in ("corpus", "authority", "case", "op"))
    if not all(type(part) is str for part in key):
        raise Unusable(f"{origin}: a record's corpus, authority, case and op must be strings: {key!r}")
    return key


def leaf_differences(a, b, path=()):
    """mig3 2.5 case A: (path, kind) for each difference; kind is `shape`, `leaf`, or `text` for a
    report's description (`DESCRIPTIONS`), compared whole."""
    if path and path[-1] in DESCRIPTIONS:
        return [] if same(a, b) else [(path, "text")]
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
    return [] if same(a, b) else [(path, "leaf")]


def _unavailable(outcome) -> bool:
    text = json.dumps(outcome)
    return '"CheckerUnavailable' in text or '"timeout"' in text


def change_class(base: dict | None, head: dict | None) -> str | None:
    """The plan's class of a difference between two outcomes, or None when equal (as JSON, with types)."""
    if same(base, head):
        return None
    if base is None or head is None:
        return "verdict"
    if _unavailable(base) != _unavailable(head):
        return "availability"
    a_raised, b_raised = _raised(base), _raised(head)
    if a_raised is not None and b_raised is not None and a_raised.get("code") != b_raised.get("code"):
        return "order"
    differences = leaf_differences(base, head)
    if differences and all(kind == "text" or kind == "leaf" and path and path[-1] in TEXTS
                           for path, kind in differences):
        return "wording"
    return "verdict"


def _rejected(outcome: dict) -> bool:
    """Whether an outcome is a rejection (or unavailable): an error, a rejection cell, a failing exit."""
    return _raised(outcome) is not None or outcome.get("exit", 0) != 0 or "timeout" in outcome


def _raised(outcome: dict):
    """The error record of an outcome that is a rejection, wherever the corpus keeps it."""
    if "raised" in outcome:
        return outcome["raised"]
    output = outcome.get("output")
    if outcome.get("cell") in ("R", "U", "X") and isinstance(output, dict) and "code" in output:
        return output
    return None


def text_pairs(base, head, path=()):
    """The (base, head) texts of the `message` and `detail` leaves that differ; a description
    (`DESCRIPTIONS`) is one pair of its canonical JSON texts."""
    if path and path[-1] in DESCRIPTIONS:
        return [] if same(base, head) else [(json.dumps(base, sort_keys=True, ensure_ascii=False),
                                         json.dumps(head, sort_keys=True, ensure_ascii=False))]
    if isinstance(base, dict) and isinstance(head, dict):
        return [p for k in base.keys() & head.keys() for p in text_pairs(base[k], head[k], path + (k,))]
    if isinstance(base, list) and isinstance(head, list):
        return [p for x, y in zip(base, head) for p in text_pairs(x, y, path)]
    return [(base, head)] if not same(base, head) and path and path[-1] in TEXTS else []


def completeness(name: str, records: dict, expected: dict) -> None:
    """`Unusable` unless `records` hold every expected case of every expected (corpus, authority),
    each through exactly the operations it requires given its recorded outcomes (`expected_cases`),
    nothing else of those, and some available record of each."""
    for group, cases in sorted(expected.items()):
        if not cases:
            raise Unusable(f"no case of {'/'.join(group)} is defined in this checkout")
        held = [key for key in records if key[:2] == group]
        recorded = {key[2] for key in held}
        if recorded != cases.keys():
            missing, extra = sorted(cases.keys() - recorded), sorted(recorded - cases.keys())
            raise Unusable(f"{name} does not hold the {'/'.join(group)} corpus: {len(missing)} of its "
                           f"{len(cases)} cases missing{f' (first {missing[0]})' if missing else ''}, "
                           f"{len(extra)} other cases{f' (first {extra[0]})' if extra else ''}")
        by_case: dict[str, dict] = {}
        for key in held:
            by_case.setdefault(key[2], {})[key[3]] = records[key]["outcome"]
        missing, extra = [], []
        for case, outcomes in sorted(by_case.items()):
            required = cases[case](outcomes)
            missing += [(case, op) for op in sorted(required - outcomes.keys())]
            extra += [(case, op) for op in sorted(outcomes.keys() - required)]
        if missing or extra:
            raise Unusable(f"{name} does not hold the {'/'.join(group)} operations: {len(missing)} required "
                           f"operations missing{f' (first {missing[0]})' if missing else ''}, {len(extra)} "
                           f"operations no case requires{f' (first {extra[0]})' if extra else ''}")
        if all(_unavailable(records[key]["outcome"]) for key in held):
            raise Unusable(f"{name}: every {'/'.join(group)} record is unavailable")
        # Every corpus holds accepted and rejected inputs: a recording that rejects (or accepts)
        # all of them is a broken checker, and two broken alike would compare equal.
        rejected = {_rejected(records[key]["outcome"]) for key in held}
        if rejected != {True, False}:
            raise Unusable(f"{name}: every {'/'.join(group)} record is "
                           f"{'a rejection' if True in rejected else 'an acceptance'}")


def compare(base_path: str, head_path: str, delta: dict | None, *, expected: dict) -> dict:
    """The classed differences of two recordings, given the `expected` cases (`expected_cases`)."""
    base, head = load(base_path), load(head_path)
    if Path(base_path).resolve() == Path(head_path).resolve():
        raise Unusable(f"BASE and HEAD are the same file {base_path}")
    completeness(base_path, base, expected)
    completeness(head_path, head, expected)
    sources = Counter()
    for key in base.keys() & head.keys():
        if base[key]["source_sha256"] != head[key]["source_sha256"]:
            sources[key[0]] += 1
    if sources:
        raise Unusable(f"the two runs read different corpus files: {dict(sources)}")
    delta = delta or {}
    wording = {(json_text(pair["base"]), json_text(pair["head"])) for pair in delta.get("wording", [])}
    listed = {}
    for klass in ("order", "verdict", "availability", "unavailable"):
        for entry in delta.get(klass, []):
            key = record_key(entry, "the delta")
            if key in listed:
                # One entry per record: a second would silently replace the first (lf-1 recheck B's class).
                raise Unusable(f"the delta lists the record {key} twice")
            listed[key] = (klass, entry)
    rows, totals, unlisted = [], Counter(), []
    for key in sorted(base.keys() | head.keys()):
        old = base.get(key, {}).get("outcome")
        new = head.get(key, {}).get("outcome")
        if key[0] == "pilots":
            old = stable_pilot_outcome(old, base_path)
            new = stable_pilot_outcome(new, head_path)
        klass = change_class(old, new)
        if klass != "availability" and old is not None and new is not None and _unavailable(old):
            klass = "unavailable"   # on both sides: no evidence of preservation
        if klass is None:
            totals["same"] += 1
            continue
        totals[klass] += 1
        entry = listed.get(key)
        if klass == "wording":
            accepted = all((json_text(a), json_text(b)) in wording for a, b in text_pairs(old, new))
        elif klass == "unavailable":
            accepted = entry is not None and entry[0] == klass and type(entry[1].get("reason")) is str \
                and entry[1]["reason"].strip() != ""
        else:
            # Both outcomes named: an entry without `base` would accept a record missing from BASE.
            accepted = (entry is not None and entry[0] == klass and "base" in entry[1] and "head" in entry[1]
                        and same(entry[1]["base"], old) and same(entry[1]["head"], new))
        row = {"corpus": key[0], "authority": key[1], "case": key[2], "op": key[3], "class": klass,
               "base": old, "head": new, "listed": accepted}
        rows.append(row)
        if not accepted:
            unlisted.append(row)
    by_corpus = Counter((key[0], key[1]) for key in base.keys() | head.keys())
    unavailable = Counter()
    for key in base.keys() & head.keys():
        if _unavailable(base[key]["outcome"]) and _unavailable(head[key]["outcome"]):
            unavailable[(key[0], key[1])] += 1
    return {"totals": dict(totals), "records": {f"{c}/{a}": n for (c, a), n in sorted(by_corpus.items())},
            "unavailable_both": {f"{c}/{a}": n for (c, a), n in sorted(unavailable.items())},
            "differences": rows, "unlisted": len(unlisted)}


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
    for name in ("_readings_corpus", "_rights_corpus", "_norm_defaults_corpus", "_document_corpus"):
        p = sub.add_parser(name)
        p.add_argument("--out", required=True)
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
    if args.command == "_readings_corpus":
        readings_corpus(Path(args.out))
        return 0
    if args.command == "_rights_corpus":
        rights_corpus(Path(args.out))
        return 0
    if args.command == "_norm_defaults_corpus":
        norm_defaults_corpus(Path(args.out))
        return 0
    if args.command == "_document_corpus":
        document_corpus(Path(args.out))
        return 0
    delta = json.loads(args.delta.read_text()) if args.delta else None
    try:
        result = compare(args.base, args.head, delta, expected=expected_cases(ROOT, args.corpus, args.authority))
    except Unusable as exc:
        print(f"lean_first_diff: unusable evidence: {exc}", file=sys.stderr)
        return 2
    if args.json:
        args.json.write_text(json.dumps(result, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({"records": result["records"], "totals": result["totals"], "unlisted": result["unlisted"],
                      "unavailable_both": result["unavailable_both"]},
                     indent=1, sort_keys=True))
    for row in result["differences"][:20]:
        if not row["listed"]:
            print(f"UNLISTED {row['class']}: {row['corpus']}/{row['authority']} {row['op']} {row['case']}")
    return 0 if result["unlisted"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
