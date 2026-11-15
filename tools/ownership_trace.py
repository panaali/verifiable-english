"""Per-answer Lean ownership trace of the five frozen keys (kb-10d; test: manage-agents
reviews/lean-ownership-baseline-20261112.md section 2; method of reviews/lean-ownership-20261112/RESULT.md).

`trace <key> <unit> <out.json>` runs ONE unit of a key's harness (one key item, or the smallest unit a harness
answers several items in) in THIS process under `sys.setprofile`, and writes one JSON record: the unit's items,
every function of `ve/` that ran (file, qualified name, first and last line, its first caller), every Lean case sent through the
relay (`LeanServicePool.run_bound` / `LeanService.run_bound`, the one way `ve` reaches the service: mode, kind,
the environment's profiles and the harness functions on the stack when it was sent, counted), each item's value and whether it equals the frozen key.
Run it in a FRESH process per unit: the harnesses keep documents in `lru_cache`s, and a shared process would hide
the calls an earlier unit made.

`run <key> --out DIR [--jobs N]` runs `trace` for every unit of a key, one fresh process each, at most 4 at a time.
`units <key>` lists a key's units. `verdict --traces DIR --out docs/kernel` judges every item (three criteria,
`ownership_verdict.py`) and writes docs/kernel/ownership.json and ownership.md.

A measurement aid (R10): it reports what ran; the verdict is `ownership_verdict.py`'s.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VE_DIR = str(ROOT / "ve") + os.sep
KEYS = {
    "anthropic-rsp": "usecases/anthropic-rsp",
    "openai-preparedness": "usecases/openai-preparedness",
    "safety-framework": "usecases/safety-framework",
    "agent-policy": "usecases/agent-policy",
    "eligibility": "usecases/eligibility",
}
MAX_JOBS = 4


def _load(case_dir: Path, name: str):
    """The harness module `name` of `case_dir`, imported as the harness imports its siblings."""
    sys.path.insert(0, str(case_dir))
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location(f"own_{case_dir.name.replace('-', '_')}_{name}",
                                                  case_dir / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _family(item_id: str) -> str:
    """The key family: the leading letters of the item id (A-T0/PROT1 -> A, K12a -> K, S1-T1 -> S)."""
    match = re.match(r"[A-Za-z]+", item_id)
    return match.group(0) if match else item_id


# --- adapters: one per key; each names its units, runs one, and compares an item's value with the key ------------

class Adapter:
    """`units()`: unit id -> the key items it answers; `run_unit(unit)`: item id -> value, run under the profile;
    `judge(item, value)`: the item's verdict, its key and whether they agree (or the PLAN 12 entry that records the
    difference). `VALUE`: where the harness reads an answer's value from Lean: (harness function that sends the
    case, mode, kind, why); every case such a function sends of that mode and kind is a value case (criterion 2).
    It says which Lean answers the harness turns into the value; whether that kind passes is the registry's."""
    name = ""
    module = "run"
    VALUE: tuple = ()

    def __init__(self):
        self.dir = ROOT / KEYS[self.name]
        self.key = json.loads((self.dir / "answer-key.json").read_text())

    def load(self):
        self.mod = _load(self.dir, self.module)
        return self

    def family(self, item):
        return _family(item)

    def run_harness(self) -> list:
        """The whole harness, in this process, checked against its committed results.json (`run.py --check`): the
        fields that differ (none, or the whole file)."""
        try:
            self.mod.main(["--check"])
        except SystemExit as exit_:
            if exit_.code not in (None, 0):
                return ["results.json"]
        return []

    def stored(self):
        """The harness's committed results.json (the run the frozen key was compared with)."""
        return json.loads((self.dir / "results.json").read_text())

    def stored_value(self, item):
        """The item's value as the committed results.json shows it (the `ve` of its comparison row)."""
        return next(row["ve"] for row in self.stored()["comparison"] if row["id"] == item)


class RspLike(Adapter):
    """The RSP and Preparedness harnesses: `answer(item)` per key item (`verdict`, `same_set`)."""

    def entries(self):
        return {entry["id"]: entry for entry in self.key["items"]}

    def units(self):
        return {item: [item] for item in self.entries()}

    def request(self, entry):
        return {name: entry[name] for name in ("id", "case", "item")}

    def run_unit(self, unit):
        return {unit: self.mod.answer(self.request(self.entries()[unit]))}

    def judge(self, item, value):
        entry = self.entries()[item]
        agrees = bool(self.mod.same_set(entry["key"], value))
        return {"key": entry["key"], "value": self.mod.verdict(value), "agrees": agrees,
                "deviation": None if agrees else self.deviation(entry, value)}


class Rsp(RspLike):
    name = "anthropic-rsp"
    VALUE = (
        ("selected", "soft-norms", "soft-selected", "A, B, K, G7, G8, N: a choice row holds when a rule of the act is "
         "selected under both defaults (`selected` reads Lean's soft-selected rows)"),
        ("gap_probe", "soft-norms", "soft-selected", "G1, G3: a row holds when no rule is selected on the probe model"),
        ("_conflict", "soft-norms", "soft-conflict", "C: a row holds on Lean's CONFLICT, fails on CONFLICT-FREE"),
        ("t_proof", "route", "certificate", "T: a row holds on a replayed entailment certificate"),
        ("t_countermodel", "metered", "evaluate-budgeted", "T: a row fails on a countermodel Lean evaluates"),
        ("factor_within_five", "quantity", "certificate", "T5's value (and T1/T2's factor finding): a replayed "
         "quantity certificate"),
        ("d2", "risk", "risk-elaborate", "S: the risk route's harm classes (stage0.d2)"),
        ("d2", "risk", "risk-decision", "S3, S4: the risk route's decision record (stage0.d2)"),
        ("_proved", "quantity", "certificate", "D: stage0's replayed quantity certificates"),
        ("check_premises", "metered", "evaluate-budgeted", "the case model satisfies every selected premise (the "
         "answer is refused otherwise)"),
    )

    def deviation(self, entry, value):
        """PLAN 12's "Key deviation" row for the item, when the value equals the row's answer (`compare`)."""
        row = self.mod.key_deviations().get(entry["id"])
        if row and row["key"] == entry["key"] and self.mod.same_set(row["answer"], value):
            return f"PLAN.md section 12, Key deviation {entry['id']}: {row['answer']} ({row['ruling']})"
        return None


class Preparedness(RspLike):
    """`answer(item)` per item, except N3 (`dead_rules`), which reads every other item's answer: its unit runs
    them all (the harness's `run`), so everything they call is under N3."""
    name = "openai-preparedness"
    VALUE = (
        ("pick", "soft-norms", "soft-selected", "A, B, K, G, N: the rules selected for the act (`pick` reads Lean's "
         "soft-selected rows)"),
        ("w1", "soft-norms", "soft-conflict", "C: Lean's CONFLICT or CONFLICT-FREE"),
        ("certified", "quantity", "certificate", "T, S, D: a replayed quantity certificate"),
        ("entailed", "route", "certificate", "N1: a replayed entailment certificate"),
        ("risk_probe", "risk", "risk-elaborate", "the risk route's answer"),
        ("risk_probe", "risk", "risk-decision", "the risk route's answer"),
        ("indicator_silence", "metered", "evaluate-budgeted", "G7: the claim's value in two models of the premises"),
        ("check_premises", "metered", "evaluate-budgeted", "the case model satisfies every selected premise (the "
         "answer is refused otherwise)"),
    )

    def request(self, entry):
        return ({name: entry[name] for name in ("id", "case", "item")} |
                {name: entry[name] for name in ("quantities", "dates", "years") if name in entry})

    def run_unit(self, unit):
        if unit != "N3":
            return super().run_unit(unit)
        items = {entry["id"]: self.mod.answer(self.request(entry)) for entry in self.key["items"]}
        return {"N3": self.mod.recorded(self.mod.dead_rules, items)}

    def deviation(self, entry, value):
        """The harness's own classification (`classify`): a "key finding" cause citing its PLAN 12 item."""
        status, cause = self.mod.classify(entry, value, False)
        if cause and cause["kind"] == "key finding" and "PLAN 12 item" in cause["reason"]:
            return cause["reason"]
        return None


class SafetyFramework(Adapter):
    """`run` answers each item in a loop (no per-item answer function); the unit of an ordinary item is that
    loop's body for the item. Conflict clusters are `conflict_result`, C-doc `document_conflicts`; N1 to N3
    (`family_n`) read every item's evaluation, so their unit is the whole loop; S is
    `severity_and_dates.family_s(d2())` and D `severity_and_dates.d3()`. Items are judged by the harness's own `compare`."""
    name = "safety-framework"
    VALUE = (
        ("selections", "soft-norms", "soft-selected", "A, B, K, R, G, N3: the rules selected (`selections` reads "
         "Lean's soft-selected rows)"),
        ("cluster_conflict", "soft-norms", "soft-conflict", "C: Lean's CONFLICT or CONFLICT-FREE"),
        ("refute", "route", "certificate", "C, N1, S: a replayed entailment certificate"),
        ("holds", "metered", "evaluate-budgeted", "N2, S4: a formula Lean evaluates in a model"),
        ("risk_run", "risk", "risk-elaborate", "S: the risk route's harm classes"),
        ("risk_run", "risk", "risk-decision", "S: the risk route's decision record"),
        ("d3", "quantity", "certificate", "D: a replayed quantity certificate"),
        ("d3", "quantity", "countermodel", "D: a quantity countermodel Lean checks"),
    )

    def units(self):
        units = {}
        for entry in self.key["items"]:
            if entry["plan"] in ("6.7", "6.8"):
                units.setdefault("S" if entry["plan"] == "6.7" else "D", []).append(entry["id"])
            elif entry["id"] in ("N1", "N2", "N3"):
                units.setdefault("N", []).append(entry["id"])
            else:
                units[entry["id"]] = [entry["id"]]
        return units

    def _loop(self, entry, evaluations):
        """`run`'s loop body for one item with a case: the item's result (and its evaluations)."""
        m = self.mod
        kind, case = entry["item"], m.item_case(entry["id"], m.CASES[entry["case"]])
        status = m.case_premises(case)
        if kind == "SILENT:CCA+GOV":
            parts = {"SILENT:CCA": m.item_result("SILENT:CCA", case), "GOV": m.item_result("GOV", case)}
            evaluations.extend(parts.values())
            return m.with_own_premises(entry["id"], {"parts": parts, "premises": status[0]})
        if kind == "FORBIDS+L0":
            other = m.CASES["G9-L0"]
            parts = {"FORBIDS": m.item_result("FORBIDS", case), "FORBIDS@G9-L0": m.item_result("FORBIDS", other)}
            evaluations.extend(parts.values())
            return m.with_own_premises(entry["id"], {"parts": parts, "premises": status[0]})
        result = (m.item_result(kind, case, level=entry.get("level")) if kind == "PROXIMITY"
                  else m.item_result(kind, case))
        result["premises"] = status[0]
        evaluations.append(result)
        return m.with_own_premises(entry["id"], result)

    def run_unit(self, unit):
        m = self.mod
        entries = {entry["id"]: entry for entry in self.key["items"]}
        if unit in ("S", "D"):
            import severity_and_dates as sd
            self.sd = sd
            part = {"S": sd.family_s(sd.d2())} if unit == "S" else {"d3": sd.d3()}
            return {item: part for item in self.units()[unit]}
        if unit == "N":
            evaluations = []
            for entry in self.key["items"]:
                if entry["case"] is not None:
                    self._loop(entry, evaluations)
            n = m.family_n(evaluations)
            return {item: n[item] for item in ("N1", "N2", "N3")}
        entry = entries[unit]
        clusters = {name: ids for name, ids in m.CONFLICT_CLUSTERS.items()}
        if entry["item"] in clusters:
            return {unit: m.with_own_premises(unit, m.conflict_result(
                clusters[entry["item"]], item=unit if m.own_facts(unit) else None))}
        if unit == "C-doc":
            return {unit: m.union_result(list(m.document_conflicts().values()))}
        return {unit: self._loop(entry, [])}

    def judge(self, item, value):
        if "S" in value or "d3" in value:
            # severity_and_dates.compare reads both halves; the other unit's half is the committed run's (it
            # changes no row of this unit's items).
            rows = self.sd.compare({**self.stored()["d2_d3"], **value})
        else:
            rows = self.mod.compare({"items": {item: value}})
        row = next(r for r in rows if r["id"] == item)
        deviation = row.get("deviation")
        recorded = None
        if not row["agree"] and deviation and deviation["agree"]:
            recorded = f"PLAN.md section 12, item {deviation['plan_12']}: {deviation['answer']} (run.py DEVIATIONS)"
        return {"key": row["key"], "value": row["ve"], "agrees": bool(row["agree"]), "deviation": recorded}


class AgentPolicy(Adapter):
    """`check.run(actions={a}, level=False)` per action (the harness's own per-action selection); judged by the
    harness's `compare` on that action (verdict, rules, outcomes, rule 25)."""
    name = "agent-policy"
    module = "check"
    VALUE = (
        ("prove", "route", "certificate", "whether a rule applies or is selected: a replayed certificate"),
        ("value", "metered", "evaluate-budgeted", "a formula's value in the record model, evaluated by Lean"),
        ("Evidence.focus.<locals>.<lambda>", "norms", "norms-certificate", "a completed outcome: a replayed norms "
         "certificate"),
    )

    def units(self):
        return {action: [action] for action in self.key["actions"]}

    def family(self, item):
        return "action"

    def run_unit(self, unit):
        return {unit: self.mod.run(actions={unit}, level=False)["actions"][unit]}

    def judge(self, item, value):
        report = self.mod.compare({"actions": {item: value}}, {"actions": {item: self.key["actions"][item]}})
        failed = [name for name in ("verdict_disagreements", "rule_disagreements", "outcome_disagreements",
                                    "rule_25_disagreements") if item in report[name]]
        return {"key": self.key["actions"][item]["verdict"], "value": value["verdict"], "agrees": not failed,
                "deviation": None, "disagreements": failed}

    def stored_value(self, item):
        return self.stored()["actions"][item]["verdict"]

    def run_harness(self):
        """`check.py base` in this process (no worker pool), compared with the committed results.json field by field
        as tests/test_agent_policy_rerun.py compares it (M10 holds timings)."""
        m = self.mod
        base = m.run(evidence=m.Evidence(keep=False), pool=None)
        summary = json.loads(json.dumps(m.base_summary(base), ensure_ascii=False, sort_keys=True))
        return [field for field in ("inputs", "actions", "policy", "policy_summary", "comparison", "M8")
                if summary[field] != self.stored()[field]]


class Eligibility(Adapter):
    """No per-item answer function: `main(--profiles P)` answers one profile's scored questions (Q1 to Q4), its
    smallest unit; single shot (a process pool, no answer of its own) and the mutation check are left out."""
    name = "eligibility"
    VALUE = (
        ("lean", "quantity", "document", "an answer counts only when Lean admits its staged quantity document"),
    )

    def __init__(self):
        self.dir = ROOT / KEYS[self.name]
        self.cases = json.loads((self.dir / "cases.json").read_text())["cases"]
        self.key = {"cases": self.cases}

    def units(self):
        out = {}
        for case in self.cases:
            questions = ["Q1"] + (["Q2", "Q3", "Q4"] if case["key"]["entitled"] else [])
            out[case["id"]] = [f"{case['id']}/{q}" for q in questions]
        return out

    def family(self, item):
        return item.split("/")[1]

    def run_unit(self, unit):
        results = self.mod.main(["--profiles", unit, "--no-single-shot", "--no-mutants", "--no-write"])
        [profile] = results["profiles"]
        return {f"{unit}/{q}": {"answer": profile["answers"].get(q), "expected": profile["key"].get(q),
                                "score": profile["score"].get(q)} for q in profile["score"]}

    def judge(self, item, value):
        return {"key": value["expected"], "value": value["answer"], "agrees": value["score"] is True,
                "deviation": None}

    def run_harness(self):
        """`run.py --no-write` in this process (its process pools replaced by a map), compared with the committed
        results.json except `seconds`, a timing."""
        self.mod.pool_map = lambda function, items, workers: list(map(function, items))
        results = json.loads(json.dumps(self.mod.main(["--no-write"]), sort_keys=True))
        stored = self.stored()
        results.pop("seconds", None)
        stored.pop("seconds", None)
        return [k for k in sorted(set(results) | set(stored)) if results.get(k) != stored.get(k)]

    def stored_value(self, item):
        profile, question = item.split("/")
        return next(p for p in self.stored()["profiles"] if p["id"] == profile)["answers"][question]


ADAPTERS = {cls.name: cls for cls in (Rsp, Preparedness, SafetyFramework, AgentPolicy, Eligibility)}


# --- the verdict (baseline section 2: three criteria per item) ---------------------------------------------------

DECISION_FILE = ROOT / "tools/ownership-decision-functions.json"
REGISTRY_FILE = ROOT / "tools/kernel-paths.json"
MODE_FILE = ROOT / "tools/lean-mode-deps.json"
# The files whose change can change an answer's trace (kb-10d step 3): ownership.json records their git blob ids.
TRACED_INPUTS = ("ve/norms.py", "ve/evaluate.py", "ve/softnorms.py", "ve/soft_route.py",
                 "usecases/anthropic-rsp/run.py", "usecases/openai-preparedness/run.py",
                 "usecases/safety-framework/run.py", "usecases/agent-policy/check.py", "usecases/eligibility/run.py")
# A family-qualified `untied_kinds` entry fails a case unless the case is outside that family. The profile each
# family needs: VE.Route.Run.route_gate proves every answered route case has `Gate.AllowedFamily profiles family`,
# and AllowedFamily for closureNary requires "nary@0" (lean/VE/Route/Gate.lean). A family not named here fails.
FAMILY_PROFILE = {"closureNary": "nary@0"}
# The one-shot executables of ve/backends/lean.py reach Lean outside the relay, with no kind recorded.
UNRELAYED = {("backends/lean.py", "run"), ("backends/lean.py", "run_route_cases"),
             ("backends/lean.py", "run_english_cases")}


def blob_id(path: Path) -> str:
    """The file's git blob id (what `git hash-object` prints), computed from its bytes."""
    import hashlib
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def input_ids(root: Path = ROOT) -> dict:
    return {path: blob_id(root / path) for path in TRACED_INPUTS}


def decision_functions(path: Path = DECISION_FILE) -> list:
    return json.loads(path.read_text())["functions"]


def decision_hits(functions: list, listed: list) -> list:
    """The listed decision functions among `functions` (trace rows: file under ve/, qualified name, ...)."""
    hits = set()
    for file, qualname, *_ in functions:
        for entry in listed:
            if f"ve/{file}" != entry["file"]:
                continue
            name = entry["qualname"]
            if (qualname.startswith(name + ".") if entry.get("methods") else
                    qualname == name or qualname.startswith(name + ".<locals>.")):
                hits.add(f"{entry['file']}:{qualname}")
    return sorted(hits)


def mode_names(path: Path = MODE_FILE) -> dict:
    """Wire mode name -> the registry's mode name (the constructor of VE.Service.Mode): the wire names are those
    Lean generates into tools/lean-mode-deps.json, `soft-norms` -> `softNorms`, `english.read` -> `englishRead`."""
    return {mode: re.sub(r"[-.](.)", lambda m: m.group(1).upper(), mode) for mode in json.loads(path.read_text())["modes"]}


def kind_problem(registry: dict, mode: str, kind, profiles) -> str | None:
    """None when a case of `kind` in registry mode `mode` is answered on a kernel path whose listed theorem covers
    the kind; otherwise why not (criterion 2)."""
    paths = [path for path in registry["paths"] if mode in path.get("modes", [])]
    if not paths:
        return f"mode {mode} is on no path of tools/kernel-paths.json"
    if kind is None:
        return f"a {mode} case that names no kind (the registry lists kinds by name)"
    for path in paths:
        entry = (path.get("kinds") or {}).get(kind) or {}
        if "nonverdict" in entry:
            return f"{mode} kind {kind} is listed nonverdict on path {path['name']}"
        for code in path.get("uncovered", []):
            if kind in code.get("kinds", []):
                return f"{mode} kind {kind} is listed uncovered on path {path['name']} ({code['name']})"
    names = {path["name"] for path in paths}
    for entry in registry.get("untied_kinds", []):
        if entry["path"] in names and entry["kind"] == kind:
            family = entry.get("family")
            needed = FAMILY_PROFILE.get(family)
            if family is None or needed is None or profiles is None or needed in profiles:
                return f"{mode} kind {kind} is untied on path {entry['path']}" + (f" (family {family})" if family else "")
    for path in paths:
        theorem = ((path.get("kinds") or {}).get(kind) or {}).get("theorem")
        if path.get("tier") == "kernel" and theorem and theorem in path.get("theorems", []):
            return None
    tiers = ", ".join(f"{path['name']} ({path.get('tier', 'candidate')})" for path in paths)
    return f"no kernel path lists a theorem for {mode} kind {kind} (paths: {tiers})"


def plan12_cites(case_dir: Path, citation: str) -> bool:
    """The citation names an entry that PLAN.md section 12 has: a Key deviation row of the item, or a numbered item."""
    text = (case_dir / "PLAN.md").read_text()
    if "\n## 12." not in text:
        return False
    section = text.split("\n## 12.", 1)[1].split("\n## 13.", 1)[0]
    row = re.search(r"Key deviation (\S+):", citation)
    if row:
        return any(line.strip().startswith(f"| {row.group(1)} |") for line in section.split("\n"))
    number = re.search(r"item (\d+)", citation)
    return bool(number) and re.search(rf"(^|\n)\s*(\*\*)?{number.group(1)}\.\s", section) is not None


def criterion_two(calls: list, unrelayed: list, registry: dict, names: dict) -> dict:
    """Criterion 2 over an item's value calls (the cases its key's value sources sent): every one is of a kind a
    kernel path's listed theorem covers, at least one was sent, and no Lean call went around the relay."""
    problems = []
    if unrelayed:
        problems.append(f"a Lean call outside the relay ran ({unrelayed[0]})")
    if not calls:
        problems.append("no Lean case of the key's value sources was sent (the value is not a Lean answer)")
    for call in calls:
        problem = kind_problem(registry, names.get(call["mode"], call["mode"]), call["kind"], call["profiles"])
        if problem:
            problems.append(f"{problem}, sent by {call['caller']}")
    return {"ok": not problems, "failed_by": sorted(set(problems)), "unrelayed": unrelayed,
            "value_kinds": sorted({f"{call['mode']}/{call['kind']}" for call in calls}),
            "value_calls": sorted(calls, key=_canonical)}


def judge(record: dict, item: str, adapter: Adapter, listed: list, registry: dict, names: dict) -> dict:
    """The three criteria for one item of a trace record, each with the function, kind or value that fails it."""
    info = record["items"][item]
    hits = decision_hits(record["functions"], listed)
    callers = {f"ve/{f}:{q}": rest[-1] for f, q, *rest in record["functions"]}
    c1 = {"ok": not hits, "failed_by": hits, "first_callers": {hit: callers.get(hit) for hit in hits}}
    value_sources = {(caller, mode, kind) for caller, mode, kind, _ in adapter.VALUE}
    calls = [{name: call[name] for name in ("mode", "kind", "caller", "profiles", "count")}
             for call in record["lean_calls"] if (call["caller"], call["mode"], call["kind"]) in value_sources]
    unrelayed = sorted(f"ve/{f}:{q}" for f, q, *_ in record["functions"] if (f, q) in UNRELAYED)
    c2 = criterion_two(calls, unrelayed, registry, names)
    if record["error"]:
        c3 = {"ok": False, "failed_by": f"the unit raised {record['error']}"}
    elif not info.get("reproduces"):
        c3 = {"ok": False, "failed_by": "the trace's value differs from the committed results.json"}
    elif info["agrees"]:
        c3 = {"ok": True, "failed_by": None}
    elif info.get("deviation") and plan12_cites(adapter.dir, info["deviation"]):
        c3 = {"ok": True, "failed_by": None, "recorded": info["deviation"]}
    else:
        c3 = {"ok": False, "failed_by": f"value {json.dumps(info['value'], default=str)} differs from the key "
                                        f"{json.dumps(info['key'], default=str)}, no PLAN.md section 12 entry"}
    first = next((n for n, c in ((1, c1), (2, c2), (3, c3)) if not c["ok"]), None)
    reason = None if first is None else {1: lambda: c1["failed_by"][0], 2: lambda: c2["failed_by"][0],
                                         3: lambda: c3["failed_by"]}[first]()
    return {"family": info["family"], "unit": record["unit"], "pass": first is None, "criterion": first,
            "reason": reason, "value": info["value"], "key": info["key"],
            "criteria": {"1": c1, "2": c2, "3": c3}}


def verdict(traces: Path) -> dict:
    """Every item of the five keys judged from the trace records under `traces/<key>/`."""
    listed, registry, names = decision_functions(), json.loads(REGISTRY_FILE.read_text()), mode_names()
    keys, commits = {}, set()
    for key in KEYS:
        adapter = ADAPTERS[key]()
        units = adapter.units()
        items = {}
        for unit, unit_items in units.items():
            path = traces / key / f"{_safe(unit)}.json"
            if not path.exists():
                for item in unit_items:
                    items[item] = {"family": adapter.family(item), "unit": unit, "pass": False, "criterion": None,
                                   "reason": "not traced"}
                continue
            record = json.loads(path.read_text())
            if record.get("inputs") != input_ids():
                raise SystemExit(f"{path}: traced on other inputs than the tree's ({', '.join(TRACED_INPUTS)}); "
                                 "trace again")
            commits.add(record.get("commit"))
            for item in unit_items:
                items[item] = judge(record, item, adapter, listed, registry, names)
        keys[key] = {"items": items, "totals": _totals(items.values()), "families": _families(items)}
    return {"comment": "Per-answer Lean ownership of the five frozen keys (kb-10d; tools/ownership_trace.py; test: "
                       "manage-agents reviews/lean-ownership-baseline-20261112.md section 2). Generated: never edit.",
            "commits": sorted(c for c in commits if c), "inputs": input_ids(),
            "registry": blob_id(REGISTRY_FILE), "decision_functions": blob_id(DECISION_FILE),
            "totals": {key: data["totals"] for key, data in keys.items()}, "keys": keys}


def _totals(items) -> dict:
    items = list(items)
    out = {"items": len(items), "pass": sum(i["pass"] for i in items)}
    for n in (1, 2, 3):
        out[f"fail_criterion_{n}"] = sum(i["criterion"] == n for i in items)
    out["not_traced"] = sum(i["criterion"] is None and not i["pass"] for i in items)
    return out


def _families(items: dict) -> dict:
    out = {}
    for item in items.values():
        row = out.setdefault(item["family"], {"items": 0, "c1": 0, "c2": 0, "c3": 0, "pass": 0})
        row["items"] += 1
        row["pass"] += item["pass"]
        for n in ("1", "2", "3"):
            row[f"c{n}"] += bool(item.get("criteria", {}).get(n, {}).get("ok"))
    return dict(sorted(out.items()))


# --- the trace -------------------------------------------------------------------------------------------------

class Recorder:
    def __init__(self, harness_dir: Path):
        self.harness = str(harness_dir) + os.sep
        self.functions: dict = {}
        self.calls: dict = {}
        self.lock = threading.Lock()

    def profile(self, frame, event, arg):
        if event != "call":
            return
        code = frame.f_code
        name = code.co_filename
        if name.startswith(VE_DIR) and code not in self.functions:
            last = max((line for _, _, line in code.co_lines() if line is not None), default=code.co_firstlineno)
            back = frame.f_back
            caller = "-" if back is None else (
                f"{os.path.relpath(back.f_code.co_filename, ROOT)}:"
                f"{getattr(back.f_code, 'co_qualname', back.f_code.co_name)}")
            self.functions[code] = (name[len(VE_DIR):], getattr(code, "co_qualname", code.co_name),
                                    code.co_firstlineno, last, caller)

    def stack(self):
        """The harness functions on the calling thread's stack, outermost first."""
        out, frame = [], sys._getframe(2)
        while frame is not None:
            if frame.f_code.co_filename.startswith(self.harness):
                out.append(getattr(frame.f_code, "co_qualname", frame.f_code.co_name))
            frame = frame.f_back
        return out[::-1]

    def note(self, mode, case, stack):
        """One case sent: counted per (mode, kind, innermost harness function, environment profiles)."""
        kind = case.get("kind") if isinstance(case, dict) else None
        environment = case.get("environment") if isinstance(case, dict) else None
        profiles = environment.get("profiles") if isinstance(environment, dict) else None
        profiles = sorted(profiles) if isinstance(profiles, list) and all(type(p) is str for p in profiles) else None
        caller = stack[-1] if stack else None
        entry = self.calls.setdefault((mode, kind, caller, tuple(profiles) if profiles is not None else None),
                                      {"mode": mode, "kind": kind, "caller": caller, "profiles": profiles,
                                       "count": 0, "stack": stack})
        entry["count"] += 1

    def wrap(self, cls):
        original = cls.run_bound
        recorder = self

        def run_bound(self, mode, cases, *, timeout=None):
            stack = recorder.stack()
            with recorder.lock:
                for case in cases:
                    recorder.note(mode, case, stack)
            return original(self, mode, cases, timeout=timeout)
        cls.run_bound = run_bound


def trace(key: str, unit: str, out: Path) -> dict:
    adapter = ADAPTERS[key]()
    from ve.backends import lean_service
    recorder = Recorder(adapter.dir)
    recorder.wrap(lean_service.LeanServicePool)
    recorder.wrap(lean_service.LeanService)
    items = adapter.units()[unit]
    error = None
    # The harness is imported under the profile: what its import runs (documents, vocabularies) is on every answer's
    # path, as py_under.py counts it.
    sys.setprofile(recorder.profile)
    threading.setprofile(recorder.profile)
    try:
        adapter.load()
        values = adapter.run_unit(unit)
    except Exception as exc:  # recorded: the unit's items then fail criterion 3
        values, error = {}, f"{type(exc).__name__}: {exc}"
    finally:
        sys.setprofile(None)
        threading.setprofile(None)
    judged = {}
    for item in items:
        if item in values:
            judged[item] = {"family": adapter.family(item), **adapter.judge(item, values[item])}
            # The trace reproduces the harness's own answer: the value equals the committed results.json's.
            judged[item]["reproduces"] = _canonical(judged[item]["value"]) == _canonical(adapter.stored_value(item))
        else:
            judged[item] = {"family": adapter.family(item), "key": None, "value": None, "agrees": False,
                            "deviation": None, "reproduces": False}
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    record = {"key": key, "unit": unit, "error": error, "items": judged, "commit": head, "inputs": input_ids(),
              "functions": sorted([list(v) for v in recorder.functions.values()]),
              "lean_calls": sorted(recorder.calls.values(), key=lambda c: _canonical(c))}
    out.write_text(json.dumps(record, indent=1, sort_keys=True, default=str) + "\n")
    return record


def _canonical(value) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def under(out: Path, key: str) -> dict:
    """manage-agents fable-team/architect/experiments/py_under.py's measure of a whole harness run (`run_harness`:
    the harness's own check against its committed results.json; the fields that differ are recorded) (functions of ve/
    whose code ran, CO_OPTIMIZED code only, and the lines their bodies span, overlaps counted once), with the names
    kept, so the decision functions among them can be counted (py_under.py keeps only norms.py's and softnorms.py's)."""
    import collections
    seen = {}

    def profile(frame, event, arg):
        if event == "call":
            code = frame.f_code
            name = code.co_filename
            if name.startswith(VE_DIR) and code not in seen and code.co_flags & 1:
                last = max((line for _, _, line in code.co_lines() if line is not None), default=code.co_firstlineno)
                seen[code] = (name[len(VE_DIR):], getattr(code, "co_qualname", code.co_name), code.co_firstlineno, last)
    adapter = ADAPTERS[key]()
    sys.setprofile(profile)
    threading.setprofile(profile)
    try:
        adapter.load()
        differs = adapter.run_harness()
    finally:
        sys.setprofile(None)
        threading.setprofile(None)
    by = collections.defaultdict(list)
    for file, name, first, last in seen.values():
        by[file].append((first, last, name))

    def covered(spans):
        total = high = 0
        for first, last, _ in sorted(spans):
            if last <= high:
                continue
            total += last - max(first, high + 1) + 1
            high = last
        return total
    functions = sorted([list(row) for row in seen.values()])
    data = {"key": key, "differs_from_results_json": differs, "total_functions": len(seen),
            "total_lines": sum(covered(spans) for spans in by.values()),
            "decision_functions": decision_hits(functions, decision_functions()), "functions": functions}
    out.write_text(json.dumps(data, indent=1) + "\n")
    return data


def passing_functions(traces: Path, ownership: dict) -> dict:
    """Every ve/ function that ran while a passing item was answered: per function (file, qualified name, lines)
    the keys and the number of passing items it ran under (the input of the kernel-boundary plan's next step)."""
    rows: dict = {}
    for key, block in ownership["keys"].items():
        units = {}
        for item, verdict in block["items"].items():
            if verdict["pass"]:
                units.setdefault(verdict["unit"], []).append(item)
        for unit, items in units.items():
            record = json.loads((traces / key / f"{_safe(unit)}.json").read_text())
            for file, qualname, first, last, *_ in record["functions"]:
                row = rows.setdefault(f"ve/{file}:{qualname}", {"file": f"ve/{file}", "qualname": qualname,
                                                                "lines": [first, last], "items": {}})
                row["items"][key] = row["items"].get(key, 0) + len(items)
    return {"comment": "ve/ functions that ran under a passing item of ownership.json (tools/ownership_trace.py "
                       "passing-functions); items: key -> passing items it ran under.",
            "functions": dict(sorted(rows.items()))}


def markdown(data: dict) -> str:
    """docs/kernel/ownership.md from ownership.json: a table per key by family, then every failing item."""
    lines = ["# Per-answer Lean ownership of the five frozen keys", "",
             "Generated from docs/kernel/ownership.json by `tools/ownership_trace.py verdict`; never edit by hand.",
             "Test: manage-agents reviews/lean-ownership-baseline-20261112.md section 2. An item passes when (1) no "
             "decision function of tools/ownership-decision-functions.json ran while it was answered, (2) its value is "
             "a Lean answer of a kind whose theorem tools/kernel-paths.json lists on a kernel path (not `uncovered`, "
             "`nonverdict` or untied), and (3) the value equals the frozen key or PLAN.md section 12 records the "
             "difference. The counts are per answer; quote them, never a family tally.", "",
             f"Traced at {', '.join(c[:10] for c in data['commits'])}.", "",
             "| key | items | passes | fails 1 | fails 2 | fails 3 |", "|---|---:|---:|---:|---:|---:|"]
    for key, t in data["totals"].items():
        lines.append(f"| {key} | {t['items']} | **{t['pass']}** | {t['fail_criterion_1']} | {t['fail_criterion_2']} "
                     f"| {t['fail_criterion_3']} |")
    for key, block in data["keys"].items():
        lines += ["", f"## {key}", "", "| family | items | 1 clean | 2 Lean kernel kind | 3 agrees or recorded | passes "
                  "| first failing reason (most items) |", "|---|---:|---:|---:|---:|---:|---|"]
        for family, row in block["families"].items():
            reasons = {}
            for item in block["items"].values():
                if item["family"] == family and not item["pass"]:
                    label = f"({item['criterion']}) {item['reason']}"
                    reasons[label] = reasons.get(label, 0) + 1
            top = max(reasons.items(), key=lambda kv: (kv[1], kv[0]))[0] if reasons else ""
            lines.append(f"| {family} | {row['items']} | {row['c1']} | {row['c2']} | {row['c3']} | **{row['pass']}** "
                         f"| {top.replace('|', '/')} |")
        passing = [item for item, v in block["items"].items() if v["pass"]]
        lines += ["", f"Passing ({len(passing)}): {', '.join(passing) if passing else 'none'}."]
    return "\n".join(lines) + "\n"


def write_verdict(traces: Path, out: Path) -> dict:
    data = verdict(traces)
    (out / "ownership.json").write_text(json.dumps(data, indent=1, sort_keys=True, default=str) + "\n")
    (out / "ownership.md").write_text(markdown(data))
    return data


def _safe(unit: str) -> str:
    return unit.replace("/", "_").replace(" ", "_")


def run_all(key: str, out: Path, jobs: int) -> int:
    if not 1 <= jobs <= MAX_JOBS:
        raise SystemExit(f"--jobs must be 1 to {MAX_JOBS}")
    adapter = ADAPTERS[key]()
    target = out / key
    target.mkdir(parents=True, exist_ok=True)

    def one(unit):
        path = target / f"{_safe(unit)}.json"
        log = target / f"{_safe(unit)}.log"
        with log.open("w") as handle:
            code = subprocess.run([sys.executable, __file__, "trace", key, unit, str(path)], cwd=ROOT,
                                  stdout=handle, stderr=subprocess.STDOUT).returncode
        return unit, code

    failed = 0
    with ThreadPoolExecutor(jobs) as pool:
        for unit, code in pool.map(one, list(adapter.units())):
            print(f"{unit} rc={code}", flush=True)
            failed += code != 0
    return 1 if failed else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("trace")
    one.add_argument("key", choices=sorted(KEYS))
    one.add_argument("unit")
    one.add_argument("out", type=Path)
    every = sub.add_parser("run")
    every.add_argument("key", choices=sorted(KEYS))
    every.add_argument("--out", type=Path, required=True)
    every.add_argument("--jobs", type=int, default=MAX_JOBS)
    listing = sub.add_parser("units")
    listing.add_argument("key", choices=sorted(KEYS))
    measured = sub.add_parser("under")
    measured.add_argument("key", choices=sorted(KEYS))
    measured.add_argument("out", type=Path)
    passing = sub.add_parser("passing-functions")
    passing.add_argument("--traces", type=Path, required=True)
    passing.add_argument("--out", type=Path, required=True)
    judged = sub.add_parser("verdict")
    judged.add_argument("--traces", type=Path, required=True)
    judged.add_argument("--out", type=Path, default=ROOT / "docs/kernel")
    args = parser.parse_args(argv)
    if args.command == "under":
        data = under(args.out, args.key)
        print(data["total_functions"], "functions", data["total_lines"], "lines", len(data["decision_functions"]),
              "decision functions; differs from results.json:", ", ".join(differs := data["differs_from_results_json"])
              or "nothing")
        return 0
    if args.command == "passing-functions":
        data = passing_functions(args.traces, json.loads((ROOT / "docs/kernel/ownership.json").read_text()))
        args.out.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
        print(len(data["functions"]), "functions")
        return 0
    if args.command == "verdict":
        data = write_verdict(args.traces, args.out)
        for key, t in data["totals"].items():
            print(key, f"{t['pass']}/{t['items']}")
        return 0
    if args.command == "trace":
        trace(args.key, args.unit, args.out)
        return 0
    if args.command == "run":
        return run_all(args.key, args.out, args.jobs)
    for unit, items in ADAPTERS[args.key]().units().items():
        print(unit, *items)
    return 0


if __name__ == "__main__":
    sys.exit(main())
