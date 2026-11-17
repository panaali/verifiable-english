"""The parallel batch runner of one document (plan 7): admission, budget, resume, per-mutant K and text verdicts.

  uv run python -m tools.fidmech batch --doc <doc> --jobs auto --out <dir> [--budget S] [--resume FILE]
                                       [--inputs DIR]

- **Refusal.** While the host's 5-min load is REFUSE_LOAD5 or more the runner exits EXIT_REFUSED (75) before it
  generates, writes or runs anything.
- **Admission** (`admission`). Before each dispatch another worker starts only when all hold: workers < MAX_WORKERS
  (and < --jobs N), the 1-min load < MAX_LOAD1, the scope cgroup's memory.max - memory.current >= one worker's
  measured peak RSS (the baseline run's), MemAvailable > MIN_MEM_AVAILABLE. Otherwise the runner waits and adds the
  seconds to `admission_wait_s`.
- **Workers.** Each slot is a tools/fidmech/worker.py Worker in a thread; a run is a fresh process reaped with
  os.wait4, so each run's CPU and peak RSS are its own. The unmutated baseline runs first, alone; then each slot runs
  a sentinel after every SENTINEL_EVERY of its mutants and a last one. A sentinel that differs from the first
  baseline makes the slot's results since its last good sentinel INVALID and re-queues them once; a slot whose last
  sentinel differs makes the batch INVALID (worker.run_batch's rule, per slot).
- **Verdicts.** K by records.kernel_verdict against the batch baseline (a move to or from UNDECIDED is inconclusive).
  L1-L4 and D (`TextChecks`): a mutant kills a check when its tree has a hit of that check the baseline lacks
  (keyed by class, block or predicate, quote), located on the mutated unit, a predicate the mutation edited, a block
  using such a predicate, or a sentence the unit quoted at baseline (L4's location, the missing rule). CR is never
  run here: `not-read`.
- **Budget.** Past --budget seconds no mutant is dispatched; the rest are K `not-run` (their text checks, which need
  no Lean, still run). **Resume** reads a results.jsonl: every line's inputs_sha256 must equal this batch's or the
  runner refuses (EXIT_MISMATCH, nothing run); lines with a K verdict other than not-run are kept, the rest run.
- **Out.** mutants.jsonl (the records), results.jsonl (one line per mutant: {"record", "mutant", "text"}),
  baseline.json, textcheck.json (the baseline text-check report with every lever off) and batch.json (status,
  counts, the measurements of plan 7).
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import os
import resource
import shutil
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from collections import deque
from dataclasses import dataclass, field, replace
from pathlib import Path

from tools.fidmech import mutants as M
from tools.fidmech import records as R
from tools.fidmech import worker as W

EXIT_REFUSED = 75
EXIT_MISMATCH = 65
MAX_WORKERS = 16
MAX_LOAD1 = 24.0
REFUSE_LOAD5 = 44.0
MIN_MEM_AVAILABLE = 4 * 10**9  # bytes ("> 4 GB")
POLL_S = 15.0
DOCUMENTS = {"RSP": "anthropic-rsp", "PF": "openai-preparedness", "FSF": "safety-framework"}
CHECK_OF = {"L1m": "L1", "L1n": "L1", "L1u": "L1", "L1c": "L1", "L1e": "L1", "L1a": "L1", "L2b": "L2", "L2q": "L2",
            "L2a": "L2", "L3w": "L3", "L4u": "L4", "L4l": "L4", "D": "D"}  # L4g is info, never a kill
TEXT = ("L1", "L2", "L3", "L4", "D")


class Refused(Exception):
    """The runner refuses to start: nothing was run. `code` is the exit code."""

    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


# ---- the host --------------------------------------------------------------------------------------------------

class Host:
    """The host's load, memory and the scope cgroup's room, read from /proc and /sys/fs/cgroup."""

    def loadavg(self):
        return os.getloadavg()

    def mem_available(self):
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) * 1024
        return None

    def cgroup_room(self):
        """memory.max - memory.current of this process's cgroup (v2); None when unlimited or unreadable."""
        try:
            rel = next(line.split(":", 2)[2] for line in Path("/proc/self/cgroup").read_text().splitlines()
                       if line.startswith("0::"))
            base = Path("/sys/fs/cgroup") / rel.strip().lstrip("/")
            limit = (base / "memory.max").read_text().strip()
            if limit == "max":
                return None
            return int(limit) - int((base / "memory.current").read_text().strip())
        except (OSError, StopIteration, ValueError):
            return None


def admission(host, running, jobs, peak_rss):
    """The reasons another worker may not start now (empty: admit)."""
    reasons = []
    if running >= min(MAX_WORKERS, jobs):
        reasons.append(f"{running} workers running (cap {min(MAX_WORKERS, jobs)})")
    load1 = host.loadavg()[0]
    if load1 >= MAX_LOAD1:
        reasons.append(f"1-min load {load1:.1f} >= {MAX_LOAD1:.0f}")
    room = host.cgroup_room()
    if room is not None and peak_rss is not None and room < peak_rss:
        reasons.append(f"cgroup room {room / 2**30:.1f} GiB < one worker's peak RSS {peak_rss / 2**30:.1f} GiB")
    avail = host.mem_available()
    if avail is not None and avail <= MIN_MEM_AVAILABLE:
        reasons.append(f"MemAvailable {avail / 1e9:.1f} GB <= 4 GB")
    return reasons


def wait_admitted(host, jobs, peak_rss, *, clock, sleep, log, running=0):
    """Wait (sleep POLL_S at a time) until another worker is admitted; the seconds waited."""
    waited, reasons = 0.0, admission(host, running, jobs, peak_rss)
    if reasons:
        log("admission wait: " + "; ".join(reasons))
    while reasons:
        before = clock()
        sleep(POLL_S)
        waited += clock() - before
        reasons = admission(host, running, jobs, peak_rss)
    if waited:
        log(f"admitted after {waited:.1f} s of admission wait")
    return waited


def refuse_if_loaded(host):
    load5 = host.loadavg()[1]
    if load5 >= REFUSE_LOAD5:
        raise Refused(f"5-min load {load5:.1f} >= {REFUSE_LOAD5:.0f}: refused, nothing run", EXIT_REFUSED)


# ---- text checks per mutant ------------------------------------------------------------------------------------

class TextChecks:
    """The baseline hits of L1-L4 and D on one case, and each mutant's verdicts against them."""

    def __init__(self, case, source_bytes, boundaries_path):
        from tools.fidmech import segment as S
        from tools.fidmech import sentchecks as C
        from tools.fidmech import textchecks as T
        self.S, self.C, self.T = S, C, T
        self.case, self.boundaries_path, self.source_bytes = Path(case), Path(boundaries_path), source_bytes
        self.seg = S.Segmentation(S.Source(source_bytes), S.load_boundaries(boundaries_path))
        self.files = M.case_files(self.case)
        blocks = T.read_blocks(self.case)
        data = C.load_case(self.case, self.seg)
        self.hits, _ = C.run(self.seg, blocks, data, C.CHECKS)
        self.keys = {h.key() for h in self.hits}
        self.predicates = data.vocabulary.get("predicates", {})
        self.users = C.users(blocks, data)
        self.quoted = {}  # block id -> the "stream@start" ids of the sentences it quotes (L4's hit location)
        streams = {st.name: st for st in self.seg.streams}
        for b in blocks:
            locs = T.analyse(self.seg, b)[2]
            self.quoted[b["id"]] = {f"{loc.place.stream}@{streams[loc.place.stream].sentences[i].start}"
                                    for loc in locs if loc.place for i in loc.place.sentences}
        self.units = [b["id"] for b in blocks]
        self.sidecar = data.sidecar is not None

    def _scratch(self, changed):
        tmp = Path(tempfile.mkdtemp(prefix="fidmech-text-"))
        case = tmp / self.case.name
        case.mkdir()
        for f in self.case.iterdir():
            if f.is_file():
                shutil.copy2(f, case / f.name)
        if (self.case / "fidmech").is_dir():
            shutil.copytree(self.case / "fidmech", case / "fidmech")
        for name, text in changed.items():
            (case / name).write_text(text, encoding="utf-8")
        return tmp, case

    def located(self, unit, changed):
        """The locations a hit of this mutant kills on: the unit, each predicate whose entry the mutation changed,
        each block using one, and each sentence the unit quotes at baseline."""
        edited = set()
        if "environment.d1.json" in changed:
            preds = json.loads(changed["environment.d1.json"]).get("vocabulary", {}).get("predicates", {})
            edited = {n for n in set(preds) | set(self.predicates) if preds.get(n) != self.predicates.get(n)}
        return {unit} | edited | {b for n in edited for b in self.users.get(n, ())} | self.quoted.get(unit, set())

    def verdicts(self, rec):
        """({check: killed/survived/error}, the new located hits as dicts, error text or None) of one mutant."""
        changed = M.apply_edits(self.files, rec["edits"])
        tmp, case = self._scratch(changed)
        try:
            data = self.C.load_case(case, self.seg)
            hits, _ = self.C.run(self.seg, self.T.read_blocks(case), data, self.C.CHECKS)
        except Exception as e:  # noqa: BLE001 - a mutant whose text checks raise has no text verdict
            return {c: "error" for c in TEXT}, [], f"{type(e).__name__}: {e}"
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        where = self.located(rec["unit"], changed)
        new = [h for h in hits if h.key() not in self.keys and h.cls in CHECK_OF and h.block in where]
        killed = {CHECK_OF[h.cls] for h in new}
        return {c: "killed" if c in killed else "survived" for c in TEXT}, [h.to_dict() for h in new], None


# ---- the schedule ----------------------------------------------------------------------------------------------

@dataclass
class Slot:
    worker: object
    since_good: list = field(default_factory=list)
    count: int = 0
    last_sentinel: bool | None = None


@dataclass
class Meter:
    """Concurrency over time: peak, and the time-weighted mean while the schedule ran."""
    clock: object
    running: int = 0
    peak: int = 0
    area: float = 0.0
    since: float = 0.0
    started: float = 0.0

    def start(self):
        self.started = self.since = self.clock()

    def move(self, delta):
        now = self.clock()
        self.area += self.running * (now - self.since)
        self.since, self.running = now, self.running + delta
        self.peak = max(self.peak, self.running)

    def mean(self):
        span = self.since - self.started
        return self.area / span if span > 0 else float(self.running)


def schedule(slots, mutants, baseline, *, host, jobs, peak_rss, limit, budget_end, clock, sleep, log,
             sentinel_every=W.SENTINEL_EVERY, after=None):
    """Every mutant through the slots under admission; `after(mutant id)` (the text checks) runs in the mutant's
    thread after its kernel run, beside the other runs. Returns (outcomes {id: Outcome}, not_run ids, status,
    sentinels [bool], admission_wait_s, Meter, {id: after's result})."""
    pending, requeued, outcomes, not_run, sentinels = deque(mutants), set(), {}, [], []
    free, due, running = deque(slots), deque(), {}
    meter, waited, waiting_since = Meter(clock), 0.0, None
    meter.start()
    pool = cf.ThreadPoolExecutor(max_workers=MAX_WORKERS)

    def finish(fut):
        slot, kind, mutant = running.pop(fut)
        meter.move(-1)
        out, extra = fut.result()
        if kind == "mutant":
            outcomes[mutant.id] = out
            extras[mutant.id] = extra
            slot.since_good.append(mutant)
            slot.count += 1
            if slot.count % sentinel_every == 0:
                due.append(slot)
            else:
                free.append(slot)
            return
        good = out.status == "ok" and out.projection == baseline.projection
        sentinels.append(good)
        slot.last_sentinel = good
        for m in slot.since_good:
            outcomes[m.id] = replace(outcomes[m.id], sentinel_ok=good)
            if not good and m.id not in requeued:
                requeued.add(m.id)
                pending.append(m)
        slot.since_good = []
        if not good:
            slot.worker.reset()
        free.append(slot)

    extras = {}

    def task_run(slot, kind, mutant):
        out = slot.worker.run(mutant, limit)
        return out, (after(mutant.id) if after is not None and kind == "mutant" else None)

    try:
        while True:
            for fut in [f for f in running if f.done()]:
                finish(fut)
            if pending and budget_end is not None and clock() >= budget_end:
                not_run += [m.id for m in pending]
                log(f"budget reached: {len(pending)} mutants not run")
                pending.clear()
            task = None
            if due:
                task = ("sentinel", due[0], W.BASELINE)
            elif pending and free:
                task = ("mutant", free[0], pending[0])
            elif not pending and not running:
                last = [s for s in slots if s.since_good]
                if not last:
                    break
                for s in last:
                    free.remove(s)
                due.extend(last)
                continue
            if task is None:
                cf.wait(list(running), return_when=cf.FIRST_COMPLETED)
                continue
            reasons = admission(host, len(running), jobs, peak_rss)
            if reasons:
                if waiting_since is None:
                    waiting_since = clock()
                    log("admission wait: " + "; ".join(reasons))
                before = clock()
                if running:
                    cf.wait(list(running), timeout=POLL_S, return_when=cf.FIRST_COMPLETED)
                else:
                    sleep(POLL_S)
                waited += clock() - before
                continue
            if waiting_since is not None:
                log(f"admitted after {clock() - waiting_since:.1f} s of admission wait")
                waiting_since = None
            kind, slot, mutant = task
            (due if kind == "sentinel" else pending).popleft()
            if kind == "mutant":
                free.popleft()
            meter.move(+1)
            running[pool.submit(task_run, slot, kind, mutant)] = (slot, kind, mutant)
    finally:
        pool.shutdown(wait=True)
    status = "ok" if all(s.last_sentinel is not False for s in slots) else "INVALID"
    return outcomes, not_run, status, sentinels, waited, meter, extras


# ---- the batch -------------------------------------------------------------------------------------------------

def lean_start_cost(document, worktree=W.REPO):
    """Seconds of the first and of a second parse of one rule of the case in a new process: the first pays the
    Lean service's start."""
    code = ("import json,sys,time\nfrom pathlib import Path\nfrom ve.softnorms import SoftEnvironment\n"
            "from ve.norm_english import parse_english\nfrom tools.fidmech import structural as S\n"
            "case=Path(sys.argv[1])\nenv=SoftEnvironment(json.loads((case/S.ENVIRONMENT).read_text()))\n"
            "line=next(l for l in (case/S.RULES).read_text().splitlines() if l.startswith('Rule '))\n"
            "t=[time.monotonic()]\nfor _ in range(2):\n    parse_english(env,line); t.append(time.monotonic())\n"
            "print(json.dumps({'first_s':t[1]-t[0],'second_s':t[2]-t[1]}))\n")
    done = subprocess.run([sys.executable, "-c", code, str(Path(worktree) / "usecases" / document)], cwd=W.REPO,
                          capture_output=True, text=True)
    if done.returncode != 0:
        return {"error": done.stderr.strip()[-300:]}
    data = json.loads(done.stdout.strip().splitlines()[-1])
    return {**data, "start_s": round(data["first_s"] - data["second_s"], 3)}


@dataclass
class Prepared:
    """The batch's mutant records (inputs_sha256 set), the plant and defect rows, and the rule selection counts."""
    records: list
    inputs_sha256: str
    rows: dict = field(default_factory=dict)
    selection: dict = field(default_factory=dict)


def prepare(worktree, document, inputs=None):
    """Every structural and wording mutant (mutants.document_mutants; needs Lean), the plants and real defects of
    `document` from the loaded inputs (manifests.load), and one inputs_sha256 over all of them."""
    from types import SimpleNamespace

    from tools.fidmech import manifests
    from tools.fidmech import structural as S
    case = Path(worktree) / "usecases" / document
    records, report = M.document_mutants(worktree, document)
    rows = {}
    if inputs is not None:
        plants, rows["plants"] = manifests.plant_records(inputs["plants"], document, case)
        defects, rows["defects"] = manifests.defect_records(inputs["defects"], document, case)
        records += plants + defects
        rows["inputs_sha256"] = inputs["sha256"]
    digest = R.inputs_sha256(R.collect_inputs(worktree, document, generator_version=S.GENERATOR,
                                              mutants=[SimpleNamespace(id=r["id"], edits=r["edits"])
                                                       for r in records]))
    selected, _ = M.selection(worktree, document)
    in_items = {r for ids in selected.values() for r in ids}
    blocks = [b.id for b in S.rule_blocks((case / S.RULES).read_text(encoding="utf-8"))]
    selection = {"rule_blocks": len(blocks), "in_items": len(set(blocks) & in_items),
                 "in_no_item": sorted(set(blocks) - in_items)}
    return Prepared([{**r, "inputs_sha256": digest} for r in records], digest, rows, selection)


def read_resume(path, digest):
    """{id: line} of a results.jsonl whose every line carries `digest`; any other refuses (nothing run)."""
    lines = [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]
    wrong = sorted({line["record"]["inputs_sha256"] for line in lines} - {digest})
    if wrong:
        raise Refused(f"--resume {path}: inputs_sha256 {wrong[0][:16]}... is not this batch's {digest[:16]}...: "
                      "refused, nothing run", EXIT_MISMATCH)
    return {line["record"]["id"]: line for line in lines if line["record"]["verdict"]["K"] != "not-run"}


def _fp1(worktree, document):
    """fp-1 of every rule block and of the document at the tree under test (item 44; the adjudication match)."""
    from tools.fidmech import fp1
    return fp1.fingerprints_of(fp1.semantic_files_tree(Path(worktree) / "usecases" / document))


def _meta(rec):
    return {k: rec[k] for k in ("id", "document", "unit", "class", "op", "where", "equivalent", "parse")}


def _jsonl(path, rows):
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


@dataclass
class Deps:
    """What a batch reads from the world; tests replace each part."""
    host: object = field(default_factory=Host)
    prepare: object = None  # (worktree, document, inputs) -> Prepared; None: prepare()
    slot: object = None  # (name, document, scratch) -> a Worker-like object with run(mutant, limit), reset(), usage
    text: object = None  # (document) -> TextChecks or None; None: the case's TextChecks
    lean_start: object = "measure"  # (document) -> dict, None to skip; "measure": lean_start_cost
    clock: object = time.monotonic
    sleep: object = time.sleep
    log: object = print
    worktree: Path = W.REPO


def _default_slot(worktree):
    def make(name, document, scratch):
        return W.Worker(document, worktree, scratch, name=name, fresh=True)
    return make


def _default_text(worktree):
    def make(document):
        from tools.fidmech import segment as S
        case = Path(worktree) / "usecases" / document
        return TextChecks(case, S.doc_source(case).read_bytes(), case / "fidmech" / "boundaries.json")
    return make


def run(document, out, *, jobs="auto", budget=None, resume=None, inputs=None, deps=None):
    """One document's batch; returns batch.json's dict. Raises Refused before anything runs."""
    deps = deps or Deps()
    document = DOCUMENTS.get(document, document)
    refuse_if_loaded(deps.host)
    jobs = MAX_WORKERS if jobs == "auto" else int(jobs)
    if inputs is not None:
        from tools.fidmech import manifests
        try:
            inputs = manifests.load(inputs)
        except manifests.InputsError as e:
            raise Refused(str(e), EXIT_MISMATCH) from e
    out = Path(out)
    started, cpu0 = deps.clock(), resource.getrusage(resource.RUSAGE_CHILDREN)
    prepared = (deps.prepare or prepare)(deps.worktree, document, inputs)
    kept = read_resume(resume, prepared.inputs_sha256) if resume else {}
    if (out / "results.jsonl").exists() and not (resume and Path(resume).resolve() == (out / "results.jsonl").resolve()):
        raise Refused(f"{out}/results.jsonl exists; pass it as --resume or choose another --out", 2)
    out.mkdir(parents=True, exist_ok=True)
    _jsonl(out / "mutants.jsonl", prepared.records)
    by_id = {r["id"]: r for r in prepared.records}
    runnable = [r for r in prepared.records if r["parse"] == "ok" and r["id"] not in kept]
    text = (deps.text or _default_text(deps.worktree))(document)
    if text is not None:
        (out / "textcheck.json").write_text(json.dumps(
            _text_report(text), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    scratch = Path(tempfile.mkdtemp(prefix=f"fidmech-{document}-"))
    make = deps.slot or _default_slot(deps.worktree)
    slots = [Slot(make(f"w{i}", document, scratch)) for i in range(min(MAX_WORKERS, jobs))]
    files = M.case_files(Path(deps.worktree) / "usecases" / document)
    lean_start = (lambda d: lean_start_cost(d, deps.worktree)) if deps.lean_start == "measure" else deps.lean_start
    lean = lean_start(document) if lean_start else None
    t0 = deps.clock()
    waited = wait_admitted(deps.host, jobs, None, clock=deps.clock, sleep=deps.sleep, log=deps.log)
    baseline = slots[0].worker.run(W.BASELINE)
    peak_rss = slots[0].worker.usage[-1][1] if getattr(slots[0].worker, "usage", None) else None
    deps.log(f"{document}: baseline {baseline.status} in {baseline.seconds:.1f} s; {len(runnable)} mutants to run, "
             f"{len(kept)} kept from --resume")
    summary = {"document": document, "inputs_sha256": prepared.inputs_sha256, "baseline": baseline.status,
               "budget_s": budget, "resumed_from": str(resume) if resume else None, "jobs": jobs}
    if baseline.status != "ok":
        summary["status"] = "INVALID"
        (out / "batch.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
        shutil.rmtree(scratch, ignore_errors=True)
        return summary
    (out / "baseline.json").write_text(W.projection_json(baseline.projection) + "\n", encoding="utf-8")
    limit = W.TIMEOUT_FACTOR * max(baseline.seconds, 1.0)
    mutants = [M.to_worker(r, files) for r in runnable]
    budget_end = started + budget if budget is not None else None
    outcomes, not_run, status, sentinels, scheduled_wait, meter, texts = schedule(
        slots, mutants, baseline, host=deps.host, jobs=jobs, peak_rss=peak_rss, limit=limit, budget_end=budget_end,
        clock=deps.clock, sleep=deps.sleep, log=deps.log,
        after=(lambda rid: text.verdicts(by_id[rid])) if text is not None else None)
    lines = []
    for rid, rec in by_id.items():
        if rid in kept:
            lines.append(kept[rid])
            continue
        if rec["parse"] != "ok":
            continue
        if texts.get(rid) is not None:
            verdicts, new, error = texts[rid]
        elif text is not None:  # not run: the text checks need no Lean and still run
            verdicts, new, error = text.verdicts(rec)
        else:
            verdicts, new, error = {c: "survived" for c in TEXT}, [], None
        o = outcomes.get(rid)
        if o is None:
            k, kernel = "not-run", {"changed": [], "inconclusive": [], "toward_key": 0, "away_from_key": 0}
            o = W.Outcome(rid, "not-run", None, 0.0, 0.0, None, sentinel_ok=False)
        elif o.status != "ok":
            k, kernel = "error", {"changed": [], "inconclusive": [], "toward_key": 0, "away_from_key": 0,
                                  "error": o.error}
        else:
            k, kernel = R.kernel_verdict(baseline.projection.answers, o.projection.answers,
                                         baseline.projection.agree, o.projection.agree)
        record = R.result_record(rid, {"K": k, **verdicts, "CR": "not-read"}, kernel, o.seconds, o.cpu_seconds,
                                 o.worker or "", bool(o.sentinel_ok), prepared.inputs_sha256)
        lines.append({"record": record, "mutant": _meta(rec), "text": {"new_hits": new, "error": error}})
    _jsonl(out / "results.jsonl", lines)
    shutil.rmtree(scratch, ignore_errors=True)
    wall = deps.clock() - started
    cpu1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    usage = [u for s in slots for u in getattr(s.worker, "usage", [])]
    seconds = [o.seconds for o in outcomes.values()]
    ran = len(outcomes)
    child_cpu = (cpu1.ru_utime + cpu1.ru_stime) - (cpu0.ru_utime + cpu0.ru_stime)
    summary.update({
        "status": status, "mutants": len(prepared.records), "stillborn": sum(r["parse"] != "ok" for r in by_id.values()),
        "ran": ran, "kept": len(kept), "not_run": len(not_run), "sentinels": {"run": len(sentinels),
                                                                               "failed": sentinels.count(False)},
        "selection": prepared.selection, "rows": prepared.rows, "fp1": _fp1(deps.worktree, document),
        "measurements": {
            "wall_s": round(wall, 1), "schedule_wall_s": round(deps.clock() - t0, 1),
            "child_cpu_s": round(child_cpu, 1), "run_cpu_s": round(sum(u[0] for u in usage), 1),
            "peak_concurrency": meter.peak, "mean_concurrency": round(meter.mean(), 2),
            "admission_wait_s": round(waited + scheduled_wait, 1),
            "per_mutant_s": {"mean": round(statistics.mean(seconds), 1), "median": round(statistics.median(seconds), 1),
                             "max": round(max(seconds), 1)} if seconds else None,
            "baseline_s": baseline.seconds,
            "worker_peak_rss_bytes": peak_rss, "max_peak_rss_bytes": max((u[1] for u in usage), default=None),
            "lean_service_start": lean,
            "cpu_h_per_100": round(child_cpu / 3600 / ran * 100, 2) if ran else None,
            "wall_min_per_100": round(wall / 60 / ran * 100, 1) if ran else None,
        }})
    (out / "batch.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def _text_report(text):
    """The baseline hits, the predicate users, the units and the levers (sentchecks.report with every lever off)."""
    report = text.C.report(text.case, text.source_bytes, text.boundaries_path, text.C.CHECKS)
    return {**report, "users": text.users, "units": text.units, "sidecar": text.sidecar}


def main(args, deps=None) -> int:
    try:
        summary = run(args.doc, args.out, jobs=args.jobs, budget=args.budget, resume=args.resume,
                      inputs=args.inputs, deps=deps)
    except Refused as e:
        print(f"fidmech batch: {e}", file=sys.stderr)
        return e.code
    print(json.dumps({k: summary.get(k) for k in ("document", "status", "mutants", "ran", "kept", "not_run")}))
    if summary.get("not_run"):
        print(f"resume: uv run python -m tools.fidmech batch --doc {summary['document']} --jobs {args.jobs} "
              f"--out <new dir> --resume {Path(args.out) / 'results.jsonl'}"
              + (f" --inputs {args.inputs}" if args.inputs else ""))
    return 0 if summary.get("status") == "ok" else 1
