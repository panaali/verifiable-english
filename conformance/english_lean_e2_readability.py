"""E2.6: replay the frozen readability evaluation at this checkout, with no model calls.

    .venv/bin/python -m conformance.english_lean_e2_readability --out docs/lean-first/e2/evidence/e2.6

The frozen evaluation `experiments/readability-sonnet` is read from its commit (`FROZEN`) with `git archive` into a
temporary directory; nothing in it is edited. Every recorded writing attempt (`runs/writing.jsonl`, 36 attempts) is
scored by the frozen scorer (`writing_spec.score`) against this checkout's `ve`, and each of the 30 reading items is
computed by the frozen builder (`build.compute`). Execution-only adjustments, as in E2.5: the frozen modules read the
checkout (`REPO`), the risk calls drop the obsolete `binary=` argument, and `tests/` is importable for its helpers.

Five reading items have no product path at this checkout, so the harness asks Lean directly:

* R23, R24 (`speech-follows`): the frozen source `sources/R2x/speech.ve.md` with one judgment record. The frozen
  speech oracle (`tests/frozen_speech`) gives only the query's premises; the entailment search finds a certificate or
  a countermodel, and Lean's speech-source route checks it and states the judgment (`follows` or `gap`).
* R25 (`speech-command`): Lean's speech-source route elaborates the instruction into its W1 rules; Lean's norms route
  checks a certificate that those rules require the addressee to click the control (`_norm_certificate_lean`).
* R29, R30 (`rights`): the frozen norm-defaults oracle gives the point's evidence; Lean's `norm-defaults-status`
  decides it, and `status_sentence` renders Lean's row.

The norm items R01 to R16 are on the norm-defaults route, which Lean owns since lean-first batch 10b: the frozen
`vekit.NormItem.verdict` calls the Python status API that batch deleted. Its replacement here does what the product
does (`ve.norm_defaults._point_statuses`): the frozen oracle (`conformance.frozen_norm_defaults`) proposes the point's
evidence, Lean's `norm-defaults-status` decides it, and `status_sentence` renders Lean's row. A situation conflict is
CONFLICT only when Lean replays the oracle's witness (`norm-defaults-conflict`); the soft items R15 and R16 are on
Lean's layered route, as in the frozen builder they have no conflict check.

Each writing record also carries the span of the displayed error and, for an English sentence that was refused, the
message and span of Python's hand parser (`_python_reading`, kept for the comparator), against which the saved base
messages are compared. `conformance/english_lean_e2_readability_report.py` reads only the saved files.
"""
from __future__ import annotations

import argparse
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FROZEN = "ac91e1e4"
EVAL = "experiments/readability-sonnet"
LEAN_ITEMS = ("R23", "R24", "R25", "R29", "R30")


def frozen_tree(into: Path) -> Path:
    """The frozen evaluation, extracted from its commit."""
    archive = subprocess.run(["git", "-C", str(ROOT), "archive", FROZEN, EVAL], check=True,
                             capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(into, filter="data")
    return into / EVAL


def _span(exc):
    span = getattr(exc, "span", None)
    return None if span is None else [span.start, span.end]


def lean_norm_item(vekit):
    """`vekit.NormItem` on Lean's norm-defaults route (see the module text)."""
    from conformance import frozen_norm_defaults as oracle
    from conformance import norm_defaults_layered as layered
    from ve import norm_defaults_route as route
    from ve.environment import Environment
    from ve.model import FiniteModel
    from ve.norm_defaults_english import status_sentence

    def __init__(self, env_raw, rules_text, *, soft=False):
        from ve.norm_english import parse_english
        self.env_raw, self.soft = env_raw, soft
        if soft:
            from ve.softnorms import SoftEnvironment
            self.env = SoftEnvironment(env_raw)
            self.parsed = parse_english(SoftEnvironment(vekit.without_norm_defaults(env_raw)), rules_text)
            self.doc = self.oracle = oracle.UnspecifiedSoftDocument(self.env, [r.to_dict() for r in self.parsed.rules])
        else:
            from ve import norm_defaults
            self.env = Environment(env_raw)
            self.parsed = parse_english(self.env, rules_text)
            self.doc = norm_defaults.UnspecifiedDocument(self.env, self.parsed.rules)
            self.oracle = oracle.UnspecifiedDocument(self.env, self.parsed.rules)

    def verdict(self, situation, predicate, values):
        situation = vekit.complete_situation(self.doc.situation_environment(), situation)
        kind = "soft" if self.soft else "norms"
        norms = [r.to_dict() for r in self.parsed.rules]
        [case] = [c for c, _ in layered.status_cases(kind, self.env_raw, norms, self.oracle, situation)
                  if c["predicate"] == predicate and c["tuple"] == list(values)]
        [row] = route.run_cases([case])
        if row.get("status") != "ok":
            raise RuntimeError(f"Lean refused the status case: {row}")
        state = row["point_status"]
        status, value = (("SETTLED", state == "SETTLED yes") if state.startswith("SETTLED ") else (state, None))
        shown = (self.oracle.situation(situation) if self.soft else
                 FiniteModel.from_dict(self.doc.situation_environment(), situation))
        out = {"point": [predicate, list(values)], "status": status, "value": value, "evidence": row,
               "sentence": status_sentence(self.doc, shown, row)}
        if not self.soft:
            conflict = oracle.check_conflict(self.oracle, model=situation)
            if conflict.status == "CONFLICT":
                filling = {k: frozenset(tuple(r) for r in v) for k, v in conflict.filling.items()}
                model = self.oracle.with_filling(self.oracle.situation(situation), filling)
                [replayed] = route.run_cases([route.source_case(self.doc, "norm-defaults-conflict", witness={
                    "target": conflict.target, "model": model.to_dict(), "tuple": list(conflict.tuple)})])
                out["situation_conflict"] = "CONFLICT" if replayed.get("verdict") == "CONFLICT" else "UNKNOWN"
                out["conflict"] = {"target": conflict.target, "values": list(conflict.tuple), "lean": replayed}
            else:
                out["situation_conflict"] = "UNKNOWN" if conflict.detail == "MAX_EVALUATIONS" else "NONE"
        out["situation"] = situation
        return out

    vekit.NormItem.__init__ = __init__
    vekit.NormItem.verdict = verdict


def load_frozen(here: Path):
    """The frozen modules, reading this checkout."""
    import ve.risk  # noqa: F401  (the checkout's `ve` first)
    for path in (str(ROOT), str(ROOT / "tests"), str(here)):
        if path not in sys.path:
            sys.path.insert(0, path)
    import vekit
    vekit.REPO = ROOT
    import writing_spec
    import build
    writing_spec.REPO = build.REPO = ROOT
    original = ve.risk.run_case
    ve.risk.run_case = lambda case, *, binary=None, **kw: original(case, **kw)
    error = vekit._error

    def located(exc):
        return {**error(exc), "span": _span(exc)}
    vekit._error = located
    lean_norm_item(vekit)
    return vekit, writing_spec, build


# ------------------------------------------------------------------ writing

def python_reading(task, sentence, writing_spec):
    """Python's hand parser on a refused English sentence: the base message and its span."""
    from ve.english import EnglishVocabulary, _python_reading
    from ve.environment import Environment
    raw, voc = writing_spec.task_env(task)
    env = Environment(raw)
    options = {"vocabulary": voc} if voc is not None else {}
    try:
        _python_reading(env, sentence, EnglishVocabulary(env, **options), options)
    except Exception as exc:  # the comparator's record: any outcome is data
        return {"message": str(exc), "span": _span(exc), "class": type(exc).__name__}
    return {"message": None, "span": None, "class": "accepted"}


def writing(here: Path, writing_spec) -> list[dict]:
    rows = []
    for line in (here / "runs/writing.jsonl").read_text().splitlines():
        session = json.loads(line)
        task = writing_spec.task_by_id(session["task"])
        for number, attempt in enumerate(session["attempts"], 1):
            sentence = attempt["sentence"]
            try:
                scored = writing_spec.score(task, sentence)
                exception = None
            except Exception as exc:
                scored, exception = {"outcome": "unavailable", "ve_message": str(exc)}, type(exc).__name__
            row = {"task": session["task"], "session": session["session"], "attempt": number, "sentence": sentence,
                   "family": task["family"], "outcome": scored["outcome"], "ve_message": scored.get("ve_message"),
                   "span": scored.get("span"), "exception": exception}
            if task["family"] == "formulas" and scored["outcome"] in ("parse_failure", "ambiguous"):
                row["python"] = python_reading(task, sentence, writing_spec)
            rows.append(row)
    return rows


# ------------------------------------------------------------------ reading

def _speech_source(here, item_id):
    from ve.document import _body
    raw = (here / "sources" / item_id / "speech.ve.md").read_bytes()
    boundary = raw.find(b"\n---\n", 4)
    source, fences = _body(raw[boundary + 5:])
    return json.loads(raw[4:boundary]), source, fences


def lean_follows(here, item):
    """R23, R24: a judgment record that Lean's speech-source route checks."""
    from tests.frozen_speech.speech_acts import SpeechDocument as Oracle
    from ve.entailment import prove_entailment
    from ve.environment import Environment
    from ve.search import find_countermodel
    from ve.speech_document import SpeechSource
    meta, source, fences = _speech_source(here, item["id"])
    oracle = Oracle(Environment(meta["environment"]), meta["units"], meta["queries"])
    query = meta["queries"][0]["id"]
    premises, target = oracle._caller_premises(query), oracle.queries[query].target
    question = next(u["id"] for u in meta["units"] if u["kind"] == "question")
    proof = prove_entailment(oracle.env, premises, target, max_steps=20_000)
    if proof.status == "Found":
        record = {"question": question, "by": "checker", "support": "certificate", "judgment": "follows",
                  "evidence": {"certificate": proof.certificate}}
    else:
        found = find_countermodel(oracle.env, list(premises), target, max_domain_size=2)
        if found.status != "Found":
            raise RuntimeError(f"{item['id']}: neither a certificate nor a countermodel")
        model = found.model.to_dict()
        regulated = {p for p, d in meta["environment"]["vocabulary"]["predicates"].items() if "regulated" in d}
        model["relations"] = {p: rows for p, rows in model["relations"].items() if p not in regulated}
        record = {"question": question, "by": "checker", "support": "model", "judgment": "gap",
                  "evidence": {"model": model}}
    [answer] = SpeechSource({**meta, "answers": [record]}, source, fences).report["answers"]
    label = {"follows": "FOLLOWS", "gap": "GAP"}[answer["status"]]
    return {"label": label, "verdict": {"lean": "speech-source", "answer": answer}}


def lean_command(here, item):
    """R25: Lean's rules for the instruction, and a certificate that they require the click, checked by Lean."""
    from ve import norms
    from ve.ast import Binary, Const, Not
    from ve.environment import Environment
    from ve.speech_document import SpeechSource
    meta, source, fences = _speech_source(here, item["id"])
    report = SpeechSource(meta, source, fences).report
    plain = copy.deepcopy(meta["environment"])
    plain.pop("speech_acts", None)
    plain["profiles"] = [p for p in plain["profiles"] if p != "speech-acts@0"]
    document = norms.NormDocument(Environment(plain), [{"norm": rule} for rule in report["rules"]])
    if not norms._lean_route(document):
        raise RuntimeError("R25: the plain norms environment is not on Lean's norms route")
    goal = Binary("click_required", Const("alice"), Const("check"))
    for formula, label in ((goal, "REQUIRED"), (Not(goal), "NOT-REQUIRED")):
        proof = norms.prove_norm_entailment(document, (), formula)
        if proof.status == "Found":
            check = norms._norm_certificate_lean(document, (), formula, proof.certificate)
            if check.valid:
                return {"label": label, "verdict": {"lean": "norms-certificate", "rules": report["rules"],
                                                    "steps": check.steps}}
    raise RuntimeError("R25: no certificate either way")


def lean_rights(item, build, vekit):
    """R29, R30: Lean's `norm-defaults-status` row for the point, rendered by `status_sentence`."""
    from conformance import frozen_norm_defaults as oracle
    from conformance import norm_defaults_layered as layered
    from ve import norm_defaults_route as route
    from ve.norm_defaults_english import status_sentence
    from ve.rights import RightsEnvironment
    env = RightsEnvironment(copy.deepcopy(build.RIGHTS_ENV))
    units = [{"source_units": ["u1"]}, build.RIGHT_CONTENT]
    document = oracle.UnspecifiedRightsDocument(env, units)
    situation = vekit.complete_situation(document.situation_environment(), {
        "complete": True, "domains": {"state": ["texas"], "person": ["ann"]},
        "constants": {"texas": "texas", "ann": "ann"}, "relations": {}})
    [(case, _)] = [(c, e) for c, e in layered.status_cases("rights", build.RIGHTS_ENV, units, document, situation)
                   if c["predicate"] == item["predicate"] and c["tuple"] == ["texas", "ann"]]
    [row] = route.run_cases([case])
    if row.get("status") != "ok":
        raise RuntimeError(f"{item['id']}: {row}")
    role = env.predicates[item["predicate"]].regulated.role
    state = row["point_status"]
    if state == "UNDECIDED":
        label = "DNS"
    elif state.startswith("SETTLED "):
        value = state == "SETTLED yes"
        label = ("PERMITTED" if value else "FORBIDDEN") if role == "permission" else \
            ("REQUIRED" if value else "NOT-REQUIRED")
    else:
        label = "UNKNOWN"
    return {"label": label, "verdict": {"lean": "norm-defaults-status", "row": row,
                                        "sentence": status_sentence(document, document.situation(situation), row)}}


def reading(here: Path, build, vekit) -> list[dict]:
    rows = []
    for item in build.ITEMS:
        try:
            if item["id"] in ("R23", "R24"):
                result = lean_follows(here, item)
            elif item["id"] == "R25":
                result = lean_command(here, item)
            elif item["id"] in ("R29", "R30"):
                result = lean_rights(item, build, vekit)
            else:
                result = build.compute(item)
            verdict = result["verdict"] if isinstance(result["verdict"], dict) else {}
            rows.append({"item": item["id"], "verdict": result["label"],
                         "message": verdict.get("sentence") or verdict.get("text") or "",
                         "route": "lean" if item["id"] in LEAN_ITEMS else "frozen builder"})
        except Exception as exc:  # an item that cannot be computed is recorded, never dropped
            rows.append({"item": item["id"], "verdict": "unavailable", "message": str(exc),
                         "route": "lean" if item["id"] in LEAN_ITEMS else "frozen builder",
                         "exception": type(exc).__name__})
    return rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    with tempfile.TemporaryDirectory() as tmp:
        here = frozen_tree(Path(tmp))
        vekit, writing_spec, build = load_frozen(here)
        write_rows = writing(here, writing_spec)
        read_rows = reading(here, build, vekit)
    args.out.mkdir(parents=True, exist_ok=True)
    for name, rows in (("readability-writing.jsonl", write_rows), ("readability-reading.jsonl", read_rows)):
        (args.out / name).write_text("".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in rows))
    print(json.dumps({"writing": len(write_rows), "reading": len(read_rows),
                      "unavailable": [r["item"] for r in read_rows if r["verdict"] == "unavailable"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
