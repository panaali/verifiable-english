"""D gate raw arm: Opus 5.5 answers each item from the artefact alone (PREREG-DRAFT.md).

NOT RUN YET. Freeze procedure, then run (no model call before `run --execute`):

    python experiments/D-gate/run_raw.py freeze --account <label>   # writes FREEZE.json
    git add experiments/D-gate/FREEZE.json && git commit -m "D gate: freeze"
    python experiments/D-gate/run_raw.py stamp                      # FREEZE-STAMP.txt + OpenTimestamps .ots
    git add experiments/D-gate/FREEZE-STAMP.txt* && git commit -m "D gate: timestamp the freeze"
    python experiments/D-gate/run_raw.py run --account <label> --arm high --execute

`freeze` needs a clean committed tree. It records the commit and the SHA-256 of every frozen input
(the study files, `ve_experiments/claude_cli.py` and its endpoint dependency `ve/stream_audit.py`),
the SYSTEM prompt, the model, the account label and the SHA-256 of the account's OAuth account UUID
(read from the CLI's account metadata `<config>/.claude.json` oauthAccount.accountUuid; only the hash is
kept or printed, never a credential), the `claude` binary and version, the per-arm controls, and the
endpoint controls every ledger row carries (host, shell, locale, timezone, backend revision).

`stamp` needs FREEZE.json committed and a clean tree. It writes FREEZE-STAMP.txt (the SHA-256 of
FREEZE.json and the commit that froze it) and stamps it with OpenTimestamps (`ots stamp`, as in the
earlier VE preregistrations; a pending calendar receipt suffices). Nothing is pushed.

`run` refuses to call the model unless: --execute is given; FREEZE.json exists; the tree is clean
(outside runs/); the frozen commit is an ancestor of HEAD and nothing under experiments/D-gate, ve or
ve_experiments changed since it (apart from FREEZE.json, the stamp files and runs/); every frozen hash,
SYSTEM, the model id, the `claude` binary, the host controls, --account and the account-UUID hash match;
FREEZE-STAMP.txt and its .ots are committed, name the committed FREEZE.json, and the .ots deserializes,
commits to the stamp file's SHA-256 and carries a pending calendar or completed Bitcoin attestation; and every repository module loaded by the endpoint lies under those paths.

Execution rules (frozen):
* One fresh process per sample through ClaudeCLI; no infrastructure retries; a started sample is
  never replayed (its outcome is final, whatever it is).
* UTC days: the endpoint pins the context date to the current UTC date and refuses to cross midnight.
  Each UTC day therefore writes its own ledger segment runs/<arm>/ledger-<date>.jsonl (controls
  identical apart from context_date), and no call starts within timeout_s + 120 s of UTC midnight:
  the runner waits for the new day and continues in a new segment. Resume reconciles every segment,
  so no sample is started twice.
* Every call's served model must be the frozen model (served_model=None only when reported_models is
  empty or exactly the frozen model and the stream names no other model), and its stream must show
  subscription billing (init apiKeySource "none", no rate-limit record with isUsingOverage true).
  Otherwise: STOP. The whole ledger (every daily segment) is audited against the frozen baseline before
  the first call of every run -- so a crash between a billed call and its stop still stops the arm --
  and again after every call (billing, model identity, controls and input-token drift, see analyze.py).
* A global error (the endpoint refused before starting the call: budget, drift, date, credentials,
  CLI version) aborts the run without writing any per-sample row.
* A usage-limit rejection that produced no model output is excluded: no answers row, not an
  ENDPOINT_ERROR; the run aborts and, after the reset, the same account retries that sample in a new
  segment ledger-<date>-q<n>.jsonl (the endpoint never reuses a key within one ledger file). A usage-limit
  rejection after model output records the sample (ENDPOINT_ERROR or TRUNCATED) and aborts.
* Stop rule: once ENDPOINT_ERROR samples exceed 10% of the arm's scheduled samples, the run writes
  STOP.json and stops; a stopped arm is never resumed and gets no verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
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
STAMP = f"{REL}/FREEZE-STAMP.txt"
OTS = f"{STAMP}.ots"
OTS_CMD = ("uvx", "--from", "opentimestamps-client", "ots", "stamp")
# OpenTimestamps detached-proof header: magic, major version 1, file-hash op sha256 (0x08), then the digest
OTS_MAGIC = b"\x00OpenTimestamps\x00\x00Proof\x00\xbf\x89\xe2\xe8\x84\xe8\x92\x94"


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


def endpoint_controls():
    """The non-arm controls claude_cli adds to every ledger row (claude_cli.py _sample_once, frozen by hash)."""
    return dict(backend_revision=4, host_system=platform.system(), host_release=platform.release(),
                shell="/bin/sh", locale="en_US.UTF-8", timezone="UTC")


def account_uuid_sha256(config_dir):
    """SHA-256 of the OAuth account UUID in the CLI's account metadata (<config>/.claude.json), or None.
    The UUID is an identifier, not a credential; only its hash is returned, stored or printed."""
    try:
        uuid = json.loads((Path(config_dir) / ".claude.json").read_text())["oauthAccount"]["accountUuid"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    return A.sha256_text(f"claude-oauth-account:{uuid}") if isinstance(uuid, str) and uuid else None


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
    uuid_sha = account_uuid_sha256(account_dir_for_label(account))
    if uuid_sha is None:
        sys.exit(f"no OAuth account UUID in the account metadata of {account!r}; log in with that account first")
    _, bsha, version = claude_binary()
    arms = {a: frozen_arm(a) for a in ARMS}
    if any(c["cli_version"] != version for c in arms.values()):
        sys.exit(f"installed claude {version!r} differs from the pinned Controls.cli_version")
    out = dict(frozen_commit=git("rev-parse", "HEAD").stdout.strip(), frozen_at=datetime.now(timezone.utc).isoformat(),
               account_label=account, account_uuid_sha256=uuid_sha, model=MODELS["opus"], k=K, system_sha256=A.sha256_text(SYSTEM),
               claude_binary_sha256=bsha, cli_version=version, arms=arms, endpoint_controls=endpoint_controls(),
               files={f: sha_file(ROOT / f) for f in FROZEN_FILES}, covered_paths=list(COVERED_PATHS),
               context_date_policy="per-UTC-day ledger segments; no call starts within timeout_s + "
                                   f"{MIDNIGHT_MARGIN_S} s of UTC midnight")
    (HERE / "FREEZE.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"FREEZE.json written for commit {out['frozen_commit']}; commit it, then run `stamp` and commit the "
          "stamp files before running")


OTS_PENDING = bytes.fromhex("83dfe30d2ef90c8e")
OTS_BITCOIN = bytes.fromhex("0588960d73d71901")
OTS_UNARY = {0x02, 0x03, 0x08, 0x67, 0xf2, 0xf3}   # sha1 ripemd160 sha256 keccak256 reverse hexlify
OTS_BINARY = {0xf0, 0xf1}                          # append prepend (varbytes argument)


class OtsError(ValueError):
    pass


class _Reader:
    def __init__(self, b):
        self.b, self.i = b, 0

    def bytes(self, n):
        if self.i + n > len(self.b):
            raise OtsError("truncated proof")
        out, self.i = self.b[self.i:self.i + n], self.i + n
        return out

    def varuint(self):
        v, shift = 0, 0
        while True:
            c = self.bytes(1)[0]
            v |= (c & 0x7f) << shift
            if not c & 0x80:
                return v
            shift += 7
            if shift > 63:
                raise OtsError("varuint too long")

    def varbytes(self, max_len):
        n = self.varuint()
        if n > max_len:
            raise OtsError("varbytes too long")
        return self.bytes(n)


def _ots_attestations_manual(r, depth=0):
    """Parse one serialized Timestamp (the OpenTimestamps tree format) and return its attestation kinds."""
    if depth > 256:
        raise OtsError("timestamp tree too deep")
    found = []

    def branch(tag):
        if tag == 0x00:
            atag = r.bytes(8)
            payload = _Reader(r.varbytes(8192))
            if atag == OTS_PENDING:
                uri = payload.varbytes(1000)
                if not uri.startswith(b"https://") or payload.i != len(payload.b):
                    raise OtsError("malformed pending attestation")
                found.append(("pending", uri.decode("ascii")))
            elif atag == OTS_BITCOIN:
                found.append(("bitcoin", payload.varuint()))
            else:
                found.append(("unknown", atag.hex()))
        elif tag in OTS_BINARY:
            r.varbytes(4096)
            found.extend(_ots_attestations_manual(r, depth + 1))
        elif tag in OTS_UNARY:
            found.extend(_ots_attestations_manual(r, depth + 1))
        else:
            raise OtsError(f"unknown op tag 0x{tag:02x}")

    tag = r.bytes(1)[0]
    while tag == 0xff:
        branch(r.bytes(1)[0])
        tag = r.bytes(1)[0]
    branch(tag)
    return found


def ots_attestations(proof, data):
    """Deserialize the detached OpenTimestamps proof `proof` (bytes) for `data` (bytes) and return its attestations
    as (kind, detail) pairs. Raises OtsError unless the proof is well formed and commits to SHA-256(data). Uses the
    opentimestamps library when it is installed and otherwise parses the serialization directly."""
    digest = hashlib.sha256(data).digest()
    try:
        from opentimestamps.core.notary import BitcoinBlockHeaderAttestation, PendingAttestation
        from opentimestamps.core.op import OpSHA256
        from opentimestamps.core.serialize import BytesDeserializationContext
        from opentimestamps.core.timestamp import DetachedTimestampFile
    except ImportError:
        r = _Reader(proof)
        if r.bytes(len(OTS_MAGIC)) != OTS_MAGIC or r.varuint() != 1:
            raise OtsError("not an OpenTimestamps v1 proof")
        if r.bytes(1) != b"\x08" or r.bytes(32) != digest:
            raise OtsError("the proof is not for the SHA-256 of the stamped file")
        found = _ots_attestations_manual(r)
        if r.i != len(proof):
            raise OtsError("trailing bytes after the timestamp")
        return found
    try:
        dtf = DetachedTimestampFile.deserialize(BytesDeserializationContext(proof))
    except Exception as e:  # the library raises several deserialization error types
        raise OtsError(f"malformed proof: {e}") from e
    if not isinstance(dtf.file_hash_op, OpSHA256) or dtf.file_digest != digest:
        raise OtsError("the proof is not for the SHA-256 of the stamped file")
    out = []
    for _, att in dtf.timestamp.all_attestations():
        if isinstance(att, PendingAttestation):
            if not att.uri.startswith("https://"):
                raise OtsError("malformed pending attestation")
            out.append(("pending", att.uri))
        elif isinstance(att, BitcoinBlockHeaderAttestation):
            out.append(("bitcoin", att.height))
        else:
            out.append(("unknown", att.TAG.hex()))
    return out


def ots_binds(proof, data):
    """The detached OpenTimestamps proof `proof` deserializes, commits to SHA-256(`data`), and carries at least
    one pending calendar attestation or a completed (Bitcoin) timestamp. A header alone does not count."""
    try:
        return any(kind in ("pending", "bitcoin") for kind, _ in ots_attestations(proof, data))
    except OtsError:
        return False


def freeze_commit():
    """The commit that last changed FREEZE.json."""
    return git("log", "-n", "1", "--format=%H", "--", f"{REL}/FREEZE.json").stdout.strip()


def stamp_text():
    return f"{sha_file(HERE / 'FREEZE.json')}  {REL}/FREEZE.json\n{freeze_commit()}  freeze-commit\n"


def stamp(run=subprocess.run):
    """Write FREEZE-STAMP.txt and stamp it with OpenTimestamps (network: OTS calendars; no model call)."""
    if dirty_paths():
        sys.exit("stamp needs a clean committed tree:\n" + "\n".join(dirty_paths()))
    if git("ls-files", "--error-unmatch", f"{REL}/FREEZE.json").returncode or not freeze_commit():
        sys.exit("commit FREEZE.json first")
    path = ROOT / STAMP
    path.write_text(stamp_text())
    (ROOT / OTS).unlink(missing_ok=True)
    proc = run([*OTS_CMD, str(path)], capture_output=True, text=True, timeout=300)
    if proc.returncode or not (ROOT / OTS).exists() or not ots_binds((ROOT / OTS).read_bytes(), path.read_bytes()):
        sys.exit(f"ots stamp failed (exit {proc.returncode}): {proc.stderr.strip()[:500]}")
    print(f"{STAMP} and {OTS} written; commit both before running (do not push from here)")


def stamp_problems():
    """The freeze is timestamped: FREEZE-STAMP.txt and its .ots are committed, name the committed FREEZE.json
    and the commit that froze it, and the .ots binds the stamp file."""
    for f in (STAMP, OTS):
        if not (ROOT / f).exists() or git("ls-files", "--error-unmatch", f).returncode:
            return [f"{f} missing or not committed: run `stamp` and commit its output before any call"]
    out = []
    lines = [line.split() for line in (ROOT / STAMP).read_text().splitlines()]
    if len(lines) != 2 or [len(x) for x in lines] != [2, 2] or lines[0][1] != f"{REL}/FREEZE.json" \
            or lines[1][1] != "freeze-commit":
        return [f"{STAMP} is malformed"]
    (h, _), (commit, _) = lines
    if h != sha_file(HERE / "FREEZE.json"):
        out.append(f"{STAMP} does not name the current FREEZE.json")
    shown = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{REL}/FREEZE.json"], capture_output=True)
    if shown.returncode or hashlib.sha256(shown.stdout).hexdigest() != h:
        out.append(f"{STAMP} names a commit that does not contain this FREEZE.json")
    elif git("merge-base", "--is-ancestor", commit, "HEAD").returncode:
        out.append("the stamped freeze commit is not an ancestor of HEAD")
    if not ots_binds((ROOT / OTS).read_bytes(), (ROOT / STAMP).read_bytes()):
        out.append(f"{OTS} does not bind {STAMP}")
    return out


def check_freeze(account, arm):
    """Every freeze condition, or exit. Returns the frozen record."""
    from ve_experiments.claude_cli import MODELS, SYSTEM, account_dir_for_label
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
             f":!{REL}/FREEZE.json", f":!{STAMP}", f":!{OTS}", f":!{RUNS}").returncode:
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
    elif account_uuid_sha256(account_dir_for_label(account)) != frozen.get("account_uuid_sha256"):
        problems.append("the OAuth account UUID of --account differs from the frozen one (hash compared)")
    if endpoint_controls() != frozen.get("endpoint_controls"):
        problems.append("host/endpoint controls differ from the freeze")
    problems.extend(stamp_problems())
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

billing_signals = A.billing_signals      # shared with the analysis (frozen in analyze.py)
quota_rejected = A.quota_rejected


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

    def segment_for(self, day, ledgers):
        """ledger-<day>.jsonl, or ledger-<day>-q<n>.jsonl after n excluded usage-limit rejections that day
        (a retried sample needs a ledger file in which its key is unused)."""
        n = sum(1 for name, rows in ledgers.items() if A.segment_order(name)[0] == day
                for r in rows if r.get("status") in A.FINAL_LEDGER and A.quota_excluded(r))
        return f"ledger-{day}.jsonl" if n == 0 else f"ledger-{day}-q{n}.jsonl"

    def check_ledgers(self, ledgers=None):
        """Audit every ledger segment against the frozen baseline; any problem stops the arm."""
        if ledgers is None:
            ledgers = A.load_arm(self.dir)[1]
        problems = A.audit(ledgers, self.prompts, self.frozen, self.arm)
        if not problems:
            return ledgers
        if any("billing outside the subscription" in p for p in problems):
            reason = "billing outside the subscription"
        elif any("served model differs" in p for p in problems):
            reason = "served model differs from the frozen model"
        elif any("drift" in p for p in problems):
            reason = "drift from the frozen baseline"
        else:
            reason = "ledger check against the freeze failed"
        self.stop(reason, problems=problems[:20])

    # -- main loop
    def run(self, prompt_texts, system):
        self.prompt_texts = prompt_texts
        self.dir.mkdir(parents=True, exist_ok=True)
        if (self.dir / "STOP.json").exists():
            raise Stop("STOP.json exists: this arm stopped under a stop rule and is never resumed")
        answers, ledgers, _ = A.load_arm(self.dir)
        self.check_ledgers(ledgers)  # before any further call: a crash may have hidden a billed or foreign call
        records, orphans = A.reconcile(answers, ledgers, self.prompts, self.frozen, self.arm, allow_incomplete=True)
        idx = A.ledger_index(ledgers, self.prompts, self.frozen, self.arm, [])
        for ident in orphans:  # outcome logged earlier, answers row lost (crash): derive it, never replay
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
        segment = self.segment_for(day, A.load_arm(self.dir)[1])
        client = self.client_for_day(day, self.dir / segment)
        try:
            reply = client.sample(ident[0], system, self.prompt_text(ident[0]), ident[1])
        except EndpointError as exc:
            usage = getattr(exc, "usage", None) or {}
            if usage.get("not_started") or usage.get("rejected_before_start") or not usage.get("call_key"):
                raise Abort(f"global endpoint error before the call started: {exc}") from None
            row = self.ledger_final(segment, usage["call_key"]) or {}
            if row and A.quota_excluded(row):
                self.check_ledgers()
                raise Abort("subscription usage limit reached before any model output: the sample is excluded "
                            "and retried after the reset on the same account") from None
            status = A.classify_ledger_final(row) if row else "ENDPOINT_ERROR"
            rec = self.record(ident, status, usage["call_key"], segment, error=str(exc)[:500],
                              served_model=row.get("served_model"), output_tokens=row.get("output_tokens"))
            signals = billing_signals(row.get("stream_records"))
            if signals:
                self.stop("billing outside the subscription", signals=signals, sample=list(ident))
            bad = A.model_problems(row, self.frozen["model"]) if row else []
            if bad:
                self.stop("served model differs from the frozen model", problems=bad, sample=list(ident))
            self.check_ledgers()
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
        bad = A.model_problems(dict(reply, status="ok"), self.frozen["model"])
        if bad:
            self.stop("served model differs from the frozen model", problems=bad, sample=list(ident))
        self.check_ledgers()
        return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze")
    f.add_argument("--account", required=True)
    sub.add_parser("stamp")
    r = sub.add_parser("run")
    r.add_argument("--account", required=True)
    r.add_argument("--arm", choices=sorted(ARMS), required=True)
    r.add_argument("--execute", action="store_true")
    a = ap.parse_args()
    if a.cmd == "freeze":
        return freeze(a.account)
    if a.cmd == "stamp":
        return stamp()
    if not a.execute:
        sys.exit("dry: pass --execute to call the model (only after the freeze and both reviews)")
    from ve_experiments.claude_cli import ClaudeCLI, SYSTEM, account_dir_for_label
    frozen = check_freeze(a.account, a.arm)
    rows = [json.loads(line) for line in (HERE / "prompts.jsonl").read_text().splitlines()]
    prompts = {r_["id"]: r_["sha256"] for r_ in rows}
    texts = {r_["id"]: r_["prompt"] for r_ in rows}
    assert all(A.sha256_text(texts[i]) == prompts[i] for i in prompts)
    clients = {}

    def client_for_day(day, ledger):  # one client per ledger segment
        if ledger not in clients:
            clients[ledger] = ClaudeCLI(ledger, arm_controls(a.arm, day), max_calls=len(prompts) * frozen["k"],
                                        account_config_dir=account_dir_for_label(a.account))
        return clients[ledger]

    runner = Runner(a.arm, HERE / "runs" / a.arm, prompts, frozen, client_for_day)
    try:
        runner.run(texts, SYSTEM)
    except Stop as exc:
        sys.exit(f"STOP: {exc}")
    except Abort as exc:
        sys.exit(f"ABORT (resumable): {exc}")


if __name__ == "__main__":
    main()
