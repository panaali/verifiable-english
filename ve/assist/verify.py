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
* it reports calls-ledger rows the session never recorded. A session's calls are
  found by its ``session_id`` (fixed at creation, unaffected by metadata edits and
  config re-digesting); with ``dedicated_calls`` (the default, matching the CLI's
  per-session ``SESSION.calls.jsonl``) EVERY unused row in the calls ledger counts.

Provenance is bound to content inside the session itself: a node or target whose
formula equals a shown candidate or suggestion is marked proposer/suggestion-
derived however it was entered, so regenerating a ledger with a hand-written
insertion in place of an acceptance cannot erase proposer provenance.
"""
from __future__ import annotations

import json
from pathlib import Path

from ..errors import VEError
from .proposer import _digest
from .session import DEFAULT_OPTIONS, AssistSession
from .sources import source_from_p5

FINAL = ("ok", "error", "infrastructure_error")


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
                   dedicated_calls=True):
    """Return ``{"ok", "problems", "session", "calls"}``; never raises on a bad ledger.

    ``item``: the P5 dossier the session claims to formalise (config is rebuilt from it).
    ``expected_config``: alternatively, the exact expected config fields.
    ``options``: the options the evaluation arm set (compared after defaults).
    ``calls``: the claude CLI calls ledger (path or rows); None skips the call comparison.
    ``dedicated_calls``: the calls ledger belongs to this session alone (every row must be accounted for).
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
        rows = _read_calls(calls)
        by_key = {}
        for row in rows:
            by_key.setdefault(row.get("key"), []).append(row)
        used = set()
        prefix = session.session_id + "/"
        for seq, call in recorded:
            key = call.get("call_key")
            finals = [r for r in by_key.get(key, []) if r.get("status") in FINAL] if key else []
            if not finals:
                problems.append(f"event {seq}: model call has no matching row in the calls ledger")
                continue
            used.add(key)
            row = finals[-1]
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
            for mine, theirs in compared:
                if call.get(mine) != row.get(theirs):
                    problems.append(f"event {seq}: {mine} differs from the calls ledger")
            if call.get("requested_model") != (row.get("controls") or {}).get("model"):
                problems.append(f"event {seq}: requested model differs from the calls ledger")
        stray = [r for r in rows if r.get("status") in FINAL and r.get("key") not in used
                 and (dedicated_calls or str(r.get("item_id", "")).startswith(prefix))]
        if stray:
            problems.append(f"calls ledger has {len(stray)} call(s) for this session that the session never recorded")
        mine = [r for r in rows if r.get("status") in FINAL
                and (dedicated_calls or str(r.get("item_id", "")).startswith(prefix))]
        summary.update(ledger_calls=len(mine),
                       ledger_input_tokens=sum(r.get("input_tokens") or 0 for r in mine),
                       ledger_output_tokens=sum(r.get("output_tokens") or 0 for r in mine))
    return {"ok": not problems, "problems": problems, "session": session, "calls": summary}
