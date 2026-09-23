"""Evaluator-side verification of a ``ve assist`` session ledger.

``AssistSession.from_ledger`` proves only that a ledger is internally consistent:
whoever wrote the file could also have written a different configuration with a
matching digest, or invented model calls. ``verify_session`` closes that gap for
an evaluator that holds its own materials:

* it rebuilds the configuration from the dossier (or takes an expected one) and
  compares environment, source sentences and roles, targets (no pre-set target
  formulas), options and dossier metadata;
* it replays the ledger with result verification;
* it matches every recorded model call -- successful AND failed -- against the
  claude CLI calls ledger by ``call_key`` (reply text, tokens, served model,
  account, requested model, prompt digest), and binds each call to its event:
  the calls-ledger ``item_id`` must name this session and the recording event's
  sequence number, so deleting or reordering events is detected;
* it accounts for every backend attempt: each earlier failed attempt under a call's
  key (infrastructure retries) must be carried in the recorded call's ``attempts``
  with the same token counts; a ``started`` row with no outcome (crash, kill) is an
  unresolved attempt of unknown usage and fails verification; and the session's
  proposer token totals must equal the calls ledger's totals over every attempt;
* it reports calls-ledger rows the session never recorded. With ``dedicated_calls``
  (the default, matching the CLI's per-session ``SESSION.calls.jsonl``, which the
  evaluator must hold) EVERY row in the calls ledger counts. A SHARED calls ledger
  finds a session's rows by session id, and a ledger's own ``session_id`` can be
  forged to disown rows: shared mode therefore requires ``trusted_session_id`` --
  an id the evaluator assigned or recorded independently -- and is refused without it.

Provenance is bound to content inside the session itself: a node or target whose
formula equals a shown candidate or suggestion is marked proposer/suggestion-
derived however it was entered, so regenerating a ledger with a hand-written
insertion in place of an acceptance cannot erase proposer provenance.
"""
from __future__ import annotations

import json
from pathlib import Path

from .. import stream_audit
from ..errors import VEError
from .proposer import _digest
from .session import DEFAULT_OPTIONS, AssistSession
from .sources import source_from_p5

FINAL = ("ok", "error", "infrastructure_error")


def _usage_totals(row):
    """``(input, output)`` the row's stream implies, recomputed from its stored ``stream_records`` with
    the endpoint's own rule (``ve.stream_audit.stream_usage``: field-wise max over every usage-bearing
    record). Legacy rows without stream records fall back to ``usage.sources``; None when neither exists."""
    if type(row.get("stream_records")) is list:
        return stream_audit.usage_totals(stream_audit.stream_usage(row["stream_records"]))
    usage = row.get("usage")
    sources = usage.get("sources") if type(usage) is dict else None
    if type(sources) is not dict:
        return None
    records = [{"type": "result", "usage": sources.get("result")},
               {"type": "assistant", "message": {"usage": sources.get("assistant_messages")}}]
    return stream_audit.usage_totals(stream_audit.stream_usage(records))


def _read_calls(calls):
    if isinstance(calls, (str, Path)):
        text = Path(calls).read_text(encoding="utf-8") if Path(calls).exists() else ""
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return list(calls)


def expected_config_from_p5(item, *, targets="root"):
    built = source_from_p5(item, targets=targets)
    return {"environment": built["environment"], "source": built["source"], "targets": built["targets"],
            "english_vocabulary": None}, built["metadata"]


def verify_session(ledger, *, item=None, expected_config=None, options=None, calls=None, p5_targets="root",
                   dedicated_calls=True, trusted_session_id=None):
    """Return ``{"ok", "problems", "session", "calls"}``; never raises on a bad ledger.

    ``item``: the P5 dossier the session claims to formalise (config is rebuilt from it).
    ``expected_config``: alternatively, the exact expected config fields.
    ``options``: the options the evaluation arm set (compared after defaults).
    ``calls``: the claude CLI calls ledger (path or rows); None skips the call comparison.
    ``dedicated_calls``: the calls ledger belongs to this session alone (every row must be accounted for).
    ``trusted_session_id``: the session id the evaluator assigned or recorded independently of the
    ledger. REQUIRED when ``dedicated_calls`` is False: in a shared calls ledger a session's rows are
    found by session id, and a ledger's own ``session_id`` can be forged to disown rows, so shared mode
    without a trusted id is refused (reported as a problem, never ok).
    """
    problems = []
    try:
        session = AssistSession.from_ledger(ledger)
    except (VEError, KeyError, TypeError) as exc:
        return {"ok": False, "problems": ["replay: " + (exc.message if isinstance(exc, VEError) else repr(exc))],
                "session": None, "calls": None}
    config = ledger["config"]
    expected, metadata = dict(expected_config or {}), {}
    if item is not None:
        rebuilt, metadata = expected_config_from_p5(item, targets=p5_targets)
        expected = {**rebuilt, **expected}
    for key, value in expected.items():
        if config.get(key) != value:
            problems.append(f"config {key} differs from the rebuilt configuration")
    for key, value in metadata.items():
        if (config.get("metadata") or {}).get(key) != value:
            problems.append(f"config metadata {key} differs from the dossier")
    if options is not None and config.get("options") != {**DEFAULT_OPTIONS, **options}:
        problems.append("config options differ from the evaluation arm")
    if any(row.get("formula") for row in config.get("targets", [])):
        problems.append("config pre-sets a target formula")

    recorded = [(event["seq"], call) for event in ledger["events"] for call in event.get("model_calls", [])]
    summary = {"recorded_calls": len(recorded)}
    if calls is not None:
        if not dedicated_calls and trusted_session_id is None:
            problems.append("shared calls ledger refused: a shared ledger is attributable only through an "
                            "independently trusted session id (pass trusted_session_id); the ledger's own "
                            "session_id can be forged")
        if trusted_session_id is not None and session.session_id != trusted_session_id:
            problems.append("session_id differs from the independently trusted session id")
        rows = _read_calls(calls)
        prefix = (trusted_session_id if trusted_session_id is not None else session.session_id) + "/"
        mine = lambda r: dedicated_calls or str(r.get("item_id", "")).startswith(prefix)
        by_key = {}
        for row in rows:
            by_key.setdefault(row.get("key"), []).append(row)
        used = set()
        for seq, call in recorded:
            key = call.get("call_key")
            finals = [r for r in by_key.get(key, []) if r.get("status") in FINAL] if key else []
            if call.get("not_started") is True:
                # Rejected before any backend call: legitimate only when nothing under its key ever ran.
                if not call.get("failed") or finals or any(call.get(f) for f in ("input_tokens", "output_tokens")) \
                        or call.get("attempts"):
                    problems.append(f"event {seq}: call recorded as never started, but the calls ledger or "
                                    "its own counts show spend")
                continue
            if not finals:
                problems.append(f"event {seq}: model call has no matching row in the calls ledger")
                continue
            used.add(key)
            row = finals[-1]
            # Every earlier attempt under the same key (a retried call) spent tokens the session must carry.
            attempts = call.get("attempts", [])
            earlier = finals[:-1]
            if any(r["status"] == "ok" for r in earlier):
                problems.append(f"event {seq}: the calls ledger has more than one reply for this call")
            if len(attempts) != len(earlier):
                problems.append(f"event {seq}: the calls ledger has {len(earlier)} earlier attempt(s) under this "
                                f"key but the session accounts for {len(attempts)}")
            else:
                for index, (mine_row, theirs) in enumerate(zip(attempts, earlier)):
                    for field in ("input_tokens", "output_tokens"):
                        if mine_row.get(field) != theirs.get(field):
                            problems.append(f"event {seq}: attempt {index} {field} differs from the calls ledger")
            if row.get("prompt") is None or _digest([row.get("system"), row["prompt"]]) != call.get("prompt_digest"):
                problems.append(f"event {seq}: prompt differs from the calls ledger")
            item_id = str(row.get("item_id", ""))
            if not item_id.startswith(prefix) or f"/e{seq}/" not in item_id or call.get("item_id") != item_id:
                problems.append(f"event {seq}: model call is bound to a different session or event "
                                "in the calls ledger")
            if call.get("failed"):
                if row["status"] == "ok":
                    problems.append(f"event {seq}: recorded as failed but the calls ledger has a reply")
                    continue
                compared = (("input_tokens", "input_tokens"), ("output_tokens", "output_tokens"),
                            ("model", "served_model"), ("account_label", "account_label"))
            else:
                if row["status"] != "ok":
                    problems.append(f"event {seq}: recorded reply but the calls ledger call failed")
                    continue
                compared = (("text", "text"), ("input_tokens", "input_tokens"),
                            ("output_tokens", "output_tokens"), ("model", "served_model"),
                            ("account_label", "account_label"))
            for mine_field, theirs in compared:
                if call.get(mine_field) != row.get(theirs):
                    problems.append(f"event {seq}: {mine_field} differs from the calls ledger")
            if call.get("requested_model") != (row.get("controls") or {}).get("model"):
                problems.append(f"event {seq}: requested model differs from the calls ledger")
        scoped = [r for r in rows if mine(r)]
        stray = [r for r in scoped if r.get("status") in FINAL and r.get("key") not in used]
        if stray:
            problems.append(f"calls ledger has {len(stray)} call(s) for this session that the session never recorded")
        # An attempt that started but never logged an outcome (crash, kill) may have spent tokens that
        # no one can account for: the session cannot verify.
        started, finished = {}, {}
        for r in scoped:
            if r.get("status") == "started":
                started[r.get("key")] = started.get(r.get("key"), 0) + 1
            elif r.get("status") in FINAL:
                finished[r.get("key")] = finished.get(r.get("key"), 0) + 1
        orphans = sum(max(0, n - finished.get(k, 0)) for k, n in started.items())
        if orphans:
            problems.append(f"calls ledger has {orphans} started call(s) with no recorded outcome "
                            "(usage unknown)")
        final = [r for r in scoped if r.get("status") in FINAL]
        # Each row's counted usage must be what its stored stream records imply (field-wise max over every
        # usage-bearing record), so a row cannot understate what the stream reported. A row that digested a
        # stream must carry its records.
        for r in final:
            if "raw_stream_sha256" in r and type(r.get("stream_records")) is not list:
                problems.append(f"calls ledger row {str(r.get('key'))[:12]} ({r.get('status')}): stream "
                                "records missing")
            implied = _usage_totals(r)
            if implied is not None and implied != (r.get("input_tokens"), r.get("output_tokens")):
                problems.append(f"calls ledger row {str(r.get('key'))[:12]} ({r.get('status')}): counted usage "
                                f"{(r.get('input_tokens'), r.get('output_tokens'))} differs from its reported "
                                f"usage {implied}")
        summary.update(ledger_calls=len(final), ledger_attempts_started=sum(started.values()),
                       unresolved_started=orphans,
                       ledger_input_tokens=sum(r.get("input_tokens") or 0 for r in final),
                       ledger_output_tokens=sum(r.get("output_tokens") or 0 for r in final))
        totals = session.usage()["tokens"].get("proposer", {})
        for field in ("input_tokens", "output_tokens"):
            if (totals.get(field) or 0) != summary["ledger_" + field]:
                problems.append(f"session proposer {field} total ({totals.get(field) or 0}) differs from the "
                                f"calls ledger total ({summary['ledger_' + field]})")
    return {"ok": not problems, "problems": problems, "session": session, "calls": summary}
