"""Isolated runs of one document's mutants: a scratch tree per mutant, a long-lived worker, sentinels (plan 6).

- **Scratch tree.** The whole `usecases/` tree is copied in the repo layout (PF loads anthropic-rsp/run.py at
  import; rsp_translation puts the tree's root on sys.path), the mutant's edits are written into the copy, and `ve`
  and `tools` are imported from the worktree (the scratch root has neither).
- **Per mutant.** The worker purges every use-case module (any module whose file is under the worktree's or a
  scratch `usecases/`) from sys.modules, imports the scratch run.py under a fresh module name, calls the document's
  adapter (tools/fidmech/adapters.py), and restores sys.path. It never runs main() and never sets a module global.
- **Sentinels.** The unmutated baseline runs first, after every 20 mutants and last. A sentinel whose projection
  differs from the batch baseline makes every result since the last good sentinel INVALID and re-queues it once;
  a result INVALID twice stays INVALID. A last sentinel that differs from the first makes the whole batch INVALID.
- **Timeout.** 10x the baseline seconds per mutant; a timeout or an exception is `error`. An interrupted Lean
  request leaves the service pool mid-answer, so the worker closes the pool and the next call starts a fresh one.
- **Warm or fresh.** `fresh=True` evaluates each tree in a new process (`python -m tools.fidmech.worker evaluate`).
  The measured choice is DEFAULT_FRESH (docs/infra/fid-mech-b3/REPORT.md, section 4).
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import resource
import shutil
import signal
import subprocess
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from pathlib import Path

from tools.fidmech import adapters

REPO = Path(__file__).resolve().parents[2]
SENTINEL_EVERY = 20
TIMEOUT_FACTOR = 10
# Measured (REPORT section 4): a fresh process costs under 2x a warm worker's run, so fresh is the default.
DEFAULT_FRESH = True
_NAMES = itertools.count()
PARTS = ("answers", "rules", "atoms", "agree")


class MutantTimeout(Exception):
    """A mutant ran past its limit (TIMEOUT_FACTOR x the baseline seconds)."""


@dataclass(frozen=True)
class Mutant:
    """A mutant: its id and its edits, {path relative to usecases/: the file's new text}."""
    id: str
    edits: dict = field(default_factory=dict)


BASELINE = Mutant("baseline")


@dataclass(frozen=True)
class Outcome:
    """One evaluation: status "ok" or "error" (with its reason), the projection of an ok run, and its cost."""
    id: str
    status: str
    projection: object
    seconds: float
    cpu_seconds: float
    worker: str
    error: str | None = None
    sentinel_ok: bool | None = None


def scratch_tree(worktree, dest, edits=None):
    """dest/usecases: a copy of the worktree's usecases/ with `edits` written into it. An edit outside the tree is
    refused."""
    dest = Path(dest)
    target = dest / "usecases"
    shutil.copytree(Path(worktree) / "usecases", target, ignore=shutil.ignore_patterns("__pycache__"))
    for rel, text in (edits or {}).items():
        path = (target / rel).resolve()
        if not path.is_relative_to(target.resolve()) or Path(rel).is_absolute():
            raise ValueError(f"mutant edit outside usecases/: {rel}")
        path.write_text(text, encoding="utf-8")
    return dest


def purge(roots):
    """Remove from sys.modules every module whose file lies under one of `roots`; the names removed."""
    roots = [Path(r).resolve() for r in roots]
    gone = []
    for name, module in list(sys.modules.items()):
        file = getattr(module, "__file__", None)
        if file and any(Path(file).resolve().is_relative_to(r) for r in roots):
            del sys.modules[name]
            gone.append(name)
    return gone


def import_run(tree, document):
    """The scratch tree's run.py of `document`, imported under a fresh module name."""
    name = f"fidmech_{document.replace('-', '_')}_{next(_NAMES)}"
    spec = importlib.util.spec_from_file_location(name, Path(tree) / "usecases" / document / "run.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate_tree(worktree, tree, document):
    """The adapter's projection of `document` in a scratch tree, in this process; sys.path and the use-case modules
    are restored and purged around it."""
    roots = (Path(worktree) / "usecases", Path(tree) / "usecases")
    saved = list(sys.path)
    purge(roots)
    try:
        return adapters.adapt(document, import_run(tree, document))
    finally:
        sys.path[:] = saved
        purge(roots)


def evaluate_fresh(worktree, tree, document, limit):
    """The projection computed by a new process (`python -m tools.fidmech.worker evaluate`)."""
    out = Path(tree) / "projection.json"
    try:
        done = subprocess.run([sys.executable, "-m", "tools.fidmech.worker", "evaluate", "--document", document,
                               "--tree", str(tree), "--worktree", str(worktree), "--out", str(out)], cwd=REPO,
                              capture_output=True, text=True, timeout=limit)
    except subprocess.TimeoutExpired as e:
        raise MutantTimeout(f"the process ran over {limit:.0f} s") from e
    if done.returncode != 0:
        raise RuntimeError(f"the process exited {done.returncode}: {done.stderr.strip()[-500:]}")
    return projection_from_json(out.read_text(encoding="utf-8"))


def projection_json(projection):
    return json.dumps({part: list(getattr(projection, part).items()) for part in PARTS}, ensure_ascii=False)


def projection_from_json(text):
    data = json.loads(text)
    return adapters.Projection(*({k: adapters.freeze(v) for k, v in data[part]} for part in PARTS))


@contextmanager
def alarm(seconds):
    """Raise MutantTimeout in this (main) thread after `seconds`; None arms nothing."""
    if seconds is None:
        yield
        return

    def fire(signum, frame):
        raise MutantTimeout(f"ran over {seconds:.0f} s")
    old = signal.signal(signal.SIGALRM, fire)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def cpu_seconds():
    """CPU seconds of this process and of its reaped children: a fresh run's process and the Lean service it
    stopped. A warm worker's long-lived Lean service is not reaped, so its CPU is not counted."""
    own, children = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + children.ru_utime + children.ru_stime


def close_lean_pool():
    """Close the relay's service pools; the next Lean call starts a fresh service."""
    from ve.backends import relay
    relay._close()


class Worker:
    """One document's evaluator. `evaluate(mutant, limit)` returns a projection; the default copies the tree and runs
    the adapter in this process (warm) or in a new one (fresh). `clock`, `cpu_clock`, `deadline` and `reset` are
    injectable so tests need no Lean, no sleep and no short timeout."""

    def __init__(self, document, worktree, scratch, *, name="w0", fresh=DEFAULT_FRESH, evaluate=None,
                 clock=time.monotonic, cpu_clock=cpu_seconds, deadline=alarm, reset=close_lean_pool):
        if document not in adapters.DOCUMENTS:
            raise ValueError(f"no adapter for document {document!r}")
        self.document, self.worktree, self.scratch, self.name = document, Path(worktree), Path(scratch), name
        self.fresh, self.clock, self.cpu_clock, self.deadline, self.reset = fresh, clock, cpu_clock, deadline, reset
        self.evaluate = evaluate or self._evaluate
        self.runs = 0

    def _evaluate(self, mutant, limit):
        tree = scratch_tree(self.worktree, self.scratch / f"{self.name}-{self.runs}", mutant.edits)
        try:
            if self.fresh:
                return evaluate_fresh(self.worktree, tree, self.document, limit)
            with self.deadline(limit):
                return evaluate_tree(self.worktree, tree, self.document)
        finally:
            shutil.rmtree(tree, ignore_errors=True)

    def run(self, mutant, limit=None):
        """One evaluation of `mutant` with a limit in seconds (None: the baseline, no limit)."""
        self.runs += 1
        started, cpu = self.clock(), self.cpu_clock()
        projection, error = None, None
        try:
            projection = self.evaluate(mutant, limit)
        except MutantTimeout as e:
            error = f"timeout: {e}"
            self.reset()
        except (Exception, SystemExit) as e:  # noqa: BLE001 - any failure of the mutant's run is its error
            error = f"{type(e).__name__}: {e}"
        seconds = self.clock() - started
        if error is None and limit is not None and seconds > limit:
            error = f"timeout: ran {seconds:.1f} s over the limit {limit:.1f} s"
        return Outcome(mutant.id, "error" if error else "ok", None if error else projection, round(seconds, 3),
                       round(self.cpu_clock() - cpu, 3), self.name, error)


@dataclass
class Batch:
    """A batch's outcomes in mutant order, its first and last baselines, and its status ("ok" or "INVALID")."""
    status: str
    baseline: Outcome
    last: Outcome | None
    outcomes: dict
    sentinels: list


def run_batch(worker, mutants, *, sentinel_every=SENTINEL_EVERY, timeout_factor=TIMEOUT_FACTOR):
    """Every mutant through `worker` with the sentinel schedule; each outcome carries sentinel_ok."""
    first = worker.run(BASELINE)
    if first.status != "ok":
        return Batch("INVALID", first, None, {}, [])
    limit = timeout_factor * max(first.seconds, 1.0)
    pending, requeued, since_good, outcomes, sentinels = list(mutants), set(), [], {}, []
    if len({m.id for m in pending}) != len(pending):
        raise ValueError("mutant ids are not unique")
    done = 0
    while True:
        if pending:
            mutant = pending.pop(0)
            outcomes[mutant.id] = worker.run(mutant, limit)
            since_good.append(mutant)
            done += 1
            if done % sentinel_every:
                continue
        sentinel = worker.run(BASELINE, limit)
        good = sentinel.status == "ok" and sentinel.projection == first.projection
        sentinels.append(good)
        for mutant in since_good:
            outcomes[mutant.id] = replace(outcomes[mutant.id], sentinel_ok=good)
            if not good and mutant.id not in requeued:
                requeued.add(mutant.id)
                pending.append(mutant)
        since_good = []
        if not good:
            worker.reset()
        if not pending:
            break
    status = "ok" if good else "INVALID"
    return Batch(status, first, sentinel, {m.id: outcomes[m.id] for m in mutants}, sentinels)


def measure(document, worktree, scratch, runs=2):
    """Seconds per baseline run in one warm worker (`runs` runs) and in `runs` fresh processes, and whether every
    run's projection equals the first (a sentinel on the real document)."""
    result, outcomes = {"document": document}, []
    for mode in ("warm", "fresh"):
        worker = Worker(document, worktree, scratch, name=mode, fresh=mode == "fresh")
        done = [worker.run(BASELINE) for _ in range(runs)]
        outcomes += done
        result[mode] = [o.seconds for o in done]
        result[f"{mode}_errors"] = [o.error for o in done if o.error]
    result["projections_equal"] = all(o.projection == outcomes[0].projection for o in outcomes)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m tools.fidmech.worker")
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("evaluate", help="print the projection of one scratch tree (a fresh worker's run)")
    one.add_argument("--document", required=True, choices=adapters.DOCUMENTS)
    one.add_argument("--tree", required=True)
    one.add_argument("--worktree", default=str(REPO))
    one.add_argument("--out", required=True, help="the projection's JSON file (stdout carries the use case's prints)")
    timing = sub.add_parser("measure", help="seconds per run: warm worker against fresh process")
    timing.add_argument("--document", required=True, choices=adapters.DOCUMENTS)
    timing.add_argument("--scratch", required=True)
    timing.add_argument("--runs", type=int, default=2)
    args = parser.parse_args(argv)
    if args.command == "evaluate":
        projection = evaluate_tree(args.worktree, args.tree, args.document)
        Path(args.out).write_text(projection_json(projection) + "\n", encoding="utf-8")
    else:
        print(json.dumps(measure(args.document, REPO, Path(args.scratch), args.runs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
