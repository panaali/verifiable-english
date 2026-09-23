"""D gate raw arm: Opus 5.5 answers each item from the artefact alone (PREREG-DRAFT.md).

NOT RUN YET. Two commands:

    python experiments/D-gate/run_raw.py freeze --account <label>        # writes FREEZE.json; no model call
    python experiments/D-gate/run_raw.py run --account <label> --arm high --execute

`freeze` needs a clean committed tree. It records the commit and the SHA-256 of every frozen input
(the study files, `ve_experiments/claude_cli.py` and its endpoint dependency `ve/stream_audit.py`),
the SYSTEM prompt, the model, the account label (never a credential), the `claude` binary and version,
and the per-arm controls. Commit FREEZE.json afterwards.

`run` refuses to call the model unless: --execute is given; FREEZE.json exists; the tree is clean
(outside runs/); the frozen commit is an ancestor of HEAD and nothing under experiments/D-gate, ve or
ve_experiments changed since it; every frozen hash, SYSTEM, the model id, the `claude` binary and
--account match; and every repository module loaded by the endpoint lies under those paths.

Execution rules (frozen):
* One fresh process per sample through ClaudeCLI; no infrastructure retries; a started sample is
  never replayed (its outcome is final, whatever it is).
* UTC days: the endpoint pins the context date to the current UTC date and refuses to cross midnight.
  Each UTC day therefore writes its own ledger segment runs/<arm>/ledger-<date>.jsonl (controls
  identical apart from context_date), and no call starts within timeout_s + 120 s of UTC midnight:
  the runner waits for the new day and continues in a new segment. Resume reconciles every segment,
  so no sample is started twice.
* Every call's served model must be the frozen model, and its stream must show subscription billing
  (init apiKeySource "none", no rate-limit record with isUsingOverage true). Otherwise: STOP.
* A global error (the endpoint refused before starting the call: budget, drift, date, credentials,
  CLI version) aborts the run without writing any per-sample row.
* A usage-limit rejection records that sample and aborts the run (resume after the reset).
* Stop rule: once ENDPOINT_ERROR samples exceed 10% of the arm's scheduled samples, the run writes
  STOP.json and stops; a stopped arm is never resumed and gets no verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import analyze as A  # noqa: E402  (frozen; shared parsing, classification and reconciliation)

K = A.K
ARMS = {
    # primary: the strongest routine configuration; secondary: the T1c monitor configuration
    "high": dict(effort="high", thinking_tokens=None, output_tokens=32000, timeout_s=900),
    "low": dict(effort="low", thinking_tokens=1024, output_tokens=6000, timeout_s=600),
}
WORKDIR = "/private/tmp/ve-dgate-claude-empty"
MIDNIGHT_MARGIN_S = 120
REL = "experiments/D-gate"
FROZEN_FILES = tuple(f"{REL}/{n}" for n in (
    "items.json", "ground_truth.json", "prompts.jsonl", "analyze.py", "run_raw.py", "PREREG-DRAFT.md",
    "build_items.py", "ground_truth.py", "render_prompts.py", "domain_check.py")) + (
    "ve_experiments/claude_cli.py", "ve/stream_audit.py")
COVERED_PATHS = (REL, "ve", "ve_experiments")
RUNS = f"{REL}/runs/"


class Stop(Exception):
    """A stop rule fired: STOP.json is written and the arm is never resumed."""


class Abort(Exception):
    """A global error: the run ends without a per-sample row; it may be resumed."""


def sha_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)


def dirty_paths():
    out = git("status", "--porcelain", "--untracked-files=all").stdout.splitlines()
    return [line for line in out if not line[3:].startswith(RUNS)]


def arm_controls(arm, context_date):
    from ve_experiments.claude_cli import Controls, MODELS
    return Controls(model=MODELS["opus"], context_date=context_date, working_directory=WORKDIR, **ARMS[arm])


def frozen_arm(arm):
    c = asdict(arm_controls(arm, "2000-01-01"))
    c.pop("context_date")
    return c


def claude_binary():
    import shutil
    exe = shutil.which("claude")
    if not exe:
        sys.exit("claude not found")
    return exe, sha_file(exe), subprocess.check_output([exe, "--version"], text=True).strip()


def freeze(account):
    from ve_experiments.claude_cli import MODELS, SYSTEM, account_dir_for_label
    if dirty_paths():
        sys.exit("freeze needs a clean committed tree:\n" + "\n".join(dirty_paths()))
    if not account_dir_for_label(account).is_dir():
        sys.exit(f"no config directory for account {account!r}")
    _, bsha, version = claude_binary()
    arms = {a: frozen_arm(a) for a in ARMS}
    if any(c["cli_version"] != version for c in arms.values()):
        sys.exit(f"installed claude {version!r} differs from the pinned Controls.cli_version")
    out = dict(frozen_commit=git("rev-parse", "HEAD").stdout.strip(), frozen_at=datetime.now(timezone.utc).isoformat(),
               account_label=account, model=MODELS["opus"], k=K, system_sha256=A.sha256_text(SYSTEM),
               claude_binary_sha256=bsha, cli_version=version, arms=arms,
               files={f: sha_file(ROOT / f) for f in FROZEN_FILES}, covered_paths=list(COVERED_PATHS),
               context_date_policy="per-UTC-day ledger segments; no call starts within timeout_s + "
                                   f"{MIDNIGHT_MARGIN_S} s of UTC midnight")
    (HERE / "FREEZE.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"FREEZE.json written for commit {out['frozen_commit']}; commit it (and timestamp it) before running")


def check_freeze(account, arm):
    """Every freeze condition, or exit. Returns the frozen record."""
    from ve_experiments.claude_cli import MODELS, SYSTEM
    f = HERE / "FREEZE.json"
    if not f.exists():
        sys.exit("FREEZE.json missing: the prereg is not frozen; no model calls")
    frozen = json.loads(f.read_text())
    problems = []
    if dirty_paths():
        problems.append("the tree is not clean (outside runs/)")
    if git("ls-files", "--error-unmatch", f"{REL}/FREEZE.json").returncode:
        problems.append("FREEZE.json is not committed")
    if git("merge-base", "--is-ancestor", frozen["frozen_commit"], "HEAD").returncode:
        problems.append("the frozen commit is not an ancestor of HEAD")
    elif git("diff", "--quiet", frozen["frozen_commit"], "HEAD", "--", *COVERED_PATHS,
             f":!{REL}/FREEZE.json", f":!{RUNS}").returncode:
        problems.append("files under the covered paths changed since the frozen commit")
    for name, h in frozen["files"].items():
        if sha_file(ROOT / name) != h:
            problems.append(f"{name} changed since the freeze")
    if set(frozen["files"]) != set(FROZEN_FILES):
        problems.append("the frozen file list differs")
    if A.sha256_text(SYSTEM) != frozen["system_sha256"]:
        problems.append("claude_cli.SYSTEM changed")
    if MODELS["opus"] != frozen["model"]:
        problems.append("model id changed")
    if account != frozen["account_label"]:
        problems.append(f"--account {account!r} is not the frozen account")
    if frozen_arm(arm) != frozen["arms"].get(arm):
        problems.append(f"controls for arm {arm} differ from the freeze")
    _, bsha, version = claude_binary()
    if bsha != frozen["claude_binary_sha256"] or version != frozen["cli_version"]:
        problems.append("the claude binary differs from the frozen one")
    for m in list(sys.modules.values()):
        p = getattr(m, "__file__", None)
        if p:
            rel = Path(p).resolve()
            if ROOT in rel.parents and not any(str(rel.relative_to(ROOT)).startswith(c + "/") for c in COVERED_PATHS):
                problems.append(f"loaded module outside the covered paths: {rel.relative_to(ROOT)}")
    if problems:
        sys.exit("freeze check failed; no model calls:\n  " + "\n  ".join(problems))
    return frozen


# ------------------------------------------------------------------------------------------------
# Per-call checks
# ------------------------------------------------------------------------------------------------

def billing_signals(stream_records):
    """Evidence of billing outside the subscription in a call's stream (empty list if none)."""
    out = []
    for r in stream_records or []:
        if not isinstance(r, dict):
            continue
        if r.get("type") == "system" and r.get("subtype") == "init" and r.get("apiKeySource") != "none":
            out.append(f"init apiKeySource={r.get('apiKeySource')!r}")
        info = r.get("rate_limit_info") if r.get("type") == "rate_limit_event" else None
        if isinstance(info, dict) and info.get("isUsingOverage"):
            out.append("rate_limit_event isUsingOverage=true")
    return out


def quota_rejected(stream_records, error):
    info = [r.get("rate_limit_info") for r in stream_records or []
            if isinstance(r, dict) and r.get("type") == "rate_limit_event"]
    if any(isinstance(i, dict) and i.get("status") == "rejected" for i in info):
        return True
    e = str(error or "").lower()
    return any(s in e for s in ("usage limit", "hit your limit", "rate limit", "rate_limit"))


def seconds_to_utc_midnight(now):
    nxt = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return (nxt - now).total_seconds()


# ------------------------------------------------------------------------------------------------
# The run loop (clients are injected so the stop rules are testable offline)
# ------------------------------------------------------------------------------------------------

class Runner:
    def __init__(self, arm, arm_dir, prompts, frozen, client_for_day, now=lambda: datetime.now(timezone.utc),
                 sleep=time.sleep, log=print):
        self.arm, self.dir, self.prompts, self.frozen = arm, Path(arm_dir), prompts, frozen
        self.client_for_day, self.now, self.sleep, self.log = client_for_day, now, sleep, log
        self.sched = A.schedule(list(prompts), frozen["k"])
        self.max_errors = A.max_endpoint_errors(len(self.sched))
        self.timeout_s = frozen["arms"][arm]["timeout_s"]

    # -- persistence
    def append(self, rec):
        with open(self.dir / "answers.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
            f.flush()

    def stop(self, reason, **detail):
        (self.dir / "STOP.json").write_text(json.dumps(dict(reason=reason, at=self.now().isoformat(), **detail), indent=1) + "\n")
        raise Stop(reason)

    def ledger_final(self, segment, key):
        rows = A.read_jsonl(self.dir / segment) if (self.dir / segment).exists() else []
        finals = [r for r in rows if r.get("key") == key and r.get("status") in A.FINAL_LEDGER]
        return finals[-1] if finals else None

    def record(self, ident, status, key, segment, **extra):
        rec = dict(id=ident[0], sample=ident[1], arm=self.arm, status=status,
                   answer=status if status in A.VALID else None, key=key, ledger=segment, **extra)
        self.append(rec)
        return rec

    def prompt_text(self, iid):
        return self.prompt_texts[iid]

    # -- main loop
    def run(self, prompt_texts, system):
        self.prompt_texts = prompt_texts
        self.dir.mkdir(parents=True, exist_ok=True)
        if (self.dir / "STOP.json").exists():
            raise Stop("STOP.json exists: this arm stopped under a stop rule and is never resumed")
        answers, ledgers, _ = A.load_arm(self.dir)
        records, orphans = A.reconcile(answers, ledgers, self.prompts, self.frozen, self.arm, allow_incomplete=True)
        idx = A.ledger_index(ledgers, self.prompts, self.frozen, self.arm, [])
        for ident in orphans:  # started earlier, answers row lost (crash): derive it, never replay
            status, key, segment, error = A.ledger_status(idx[ident])
            records[ident] = self.record(ident, status, key, segment, error=error, recovered_from_ledger=True)
            self.log(json.dumps({"event": "recovered", "id": ident[0], "sample": ident[1], "status": status}))
        self.check_error_budget(records)
        for ident in self.sched:
            if ident in records:
                continue
            records[ident] = self.one(ident, system)
            self.check_error_budget(records)
        self.log(json.dumps({"event": "complete", "arm": self.arm, "samples": len(records)}))

    def check_error_budget(self, records):
        n = sum(r["status"] == "ENDPOINT_ERROR" for r in records.values())
        if n > self.max_errors:
            self.stop("endpoint errors exceed 10% of the scheduled samples", endpoint_errors=n,
                      threshold=self.max_errors, scheduled=len(self.sched))

    def one(self, ident, system):
        from ve_experiments.claude_cli import EndpointError
        wait = seconds_to_utc_midnight(self.now())
        if wait < self.timeout_s + MIDNIGHT_MARGIN_S:
            self.log(json.dumps({"event": "waiting_for_utc_midnight", "seconds": round(wait) + 60}))
            self.sleep(wait + 60)
        day = self.now().date().isoformat()
        segment = f"ledger-{day}.jsonl"
        client = self.client_for_day(day, self.dir / segment)
        try:
            reply = client.sample(ident[0], system, self.prompt_text(ident[0]), ident[1])
        except EndpointError as exc:
            usage = getattr(exc, "usage", None) or {}
            if usage.get("not_started") or usage.get("rejected_before_start") or not usage.get("call_key"):
                raise Abort(f"global endpoint error before the call started: {exc}") from None
            row = self.ledger_final(segment, usage["call_key"]) or {}
            status = A.classify_ledger_final(row) if row else "ENDPOINT_ERROR"
            served = row.get("served_model")
            rec = self.record(ident, status, usage["call_key"], segment, error=str(exc)[:500],
                              served_model=served, output_tokens=row.get("output_tokens"))
            signals = billing_signals(row.get("stream_records"))
            if signals:
                self.stop("billing outside the subscription", signals=signals, sample=list(ident))
            if served not in (None, self.frozen["model"]):
                self.stop("served model differs from the frozen model", served_model=served, sample=list(ident))
            if quota_rejected(row.get("stream_records"), row.get("error")):
                raise Abort("subscription usage limit reached; resume after the reset")
            return rec
        served = reply.get("served_model")
        text = reply.get("text")
        status = A.parse(text)
        rec = self.record(ident, status, reply.get("key"), segment, served_model=served,
                          output_tokens=reply.get("output_tokens"), stop_reason=reply.get("stop_reason"),
                          context_date=(reply.get("controls") or {}).get("context_date"))
        signals = billing_signals(reply.get("stream_records"))
        if signals:
            self.stop("billing outside the subscription", signals=signals, sample=list(ident))
        if served != self.frozen["model"]:
            self.stop("served model differs from the frozen model", served_model=served, sample=list(ident))
        return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze")
    f.add_argument("--account", required=True)
    r = sub.add_parser("run")
    r.add_argument("--account", required=True)
    r.add_argument("--arm", choices=sorted(ARMS), required=True)
    r.add_argument("--execute", action="store_true")
    a = ap.parse_args()
    if a.cmd == "freeze":
        return freeze(a.account)
    if not a.execute:
        sys.exit("dry: pass --execute to call the model (only after the freeze and both reviews)")
    from ve_experiments.claude_cli import ClaudeCLI, SYSTEM, account_dir_for_label
    frozen = check_freeze(a.account, a.arm)
    rows = [json.loads(line) for line in (HERE / "prompts.jsonl").read_text().splitlines()]
    prompts = {r_["id"]: r_["sha256"] for r_ in rows}
    texts = {r_["id"]: r_["prompt"] for r_ in rows}
    assert all(A.sha256_text(texts[i]) == prompts[i] for i in prompts)
    clients = {}

    def client_for_day(day, ledger):
        if day not in clients:
            clients[day] = ClaudeCLI(ledger, arm_controls(a.arm, day), max_calls=len(prompts) * frozen["k"],
                                     account_config_dir=account_dir_for_label(a.account))
        return clients[day]

    runner = Runner(a.arm, HERE / "runs" / a.arm, prompts, frozen, client_for_day)
    try:
        runner.run(texts, SYSTEM)
    except Stop as exc:
        sys.exit(f"STOP: {exc}")
    except Abort as exc:
        sys.exit(f"ABORT (resumable): {exc}")


if __name__ == "__main__":
    main()
