"""Evaluator-side verification of a ``ve assist`` session ledger.

``AssistSession.from_ledger`` proves only that a ledger is internally consistent:
whoever wrote the file could also have written a different configuration with a
matching digest, or invented model calls. ``verify_session`` closes that gap for
an evaluator that holds its own materials:

* it rebuilds the configuration from the dossier (or takes an expected one) and
  compares environment, source sentences and roles, targets (no pre-set target
  formulas), options and dossier metadata;
* it replays the ledger with result verification;
* it matches every recorded model call against the claude CLI calls ledger by
  ``call_key`` (reply text, tokens, served model, account, prompt digest), and
  reports calls-ledger rows for this session that the session never recorded.
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


def verify_session(ledger, *, item=None, expected_config=None, options=None, calls=None, p5_targets="root"):
    """Return ``{"ok", "problems", "session", "calls"}``; never raises on a bad ledger.

    ``item``: the P5 dossier the session claims to formalise (config is rebuilt from it).
    ``expected_config``: alternatively, the exact expected config fields.
    ``options``: the options the evaluation arm set (compared after defaults).
    ``calls``: the claude CLI calls ledger (path or rows); None skips the call comparison.
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
            if call.get("failed"):
                if row["status"] == "ok":
                    problems.append(f"event {seq}: recorded as failed but the calls ledger has a reply")
                continue
            if row["status"] != "ok":
                problems.append(f"event {seq}: recorded reply but the calls ledger call failed")
                continue
            for mine, theirs in (("text", "text"), ("input_tokens", "input_tokens"),
                                 ("output_tokens", "output_tokens"), ("model", "served_model"),
                                 ("account_label", "account_label")):
                if call.get(mine) != row.get(theirs):
                    problems.append(f"event {seq}: {mine} differs from the calls ledger")
            if call.get("requested_model") is not None and call["requested_model"] != row.get("controls", {}).get("model"):
                problems.append(f"event {seq}: requested model differs from the calls ledger")
        prefix = str(config.get("config_digest", ""))[:16] + "/"
        stray = [r for r in rows if r.get("status") in FINAL and str(r.get("item_id", "")).startswith(prefix)
                 and r.get("key") not in used]
        if stray:
            problems.append(f"calls ledger has {len(stray)} call(s) for this session that the session never recorded")
        mine = [r for r in rows if r.get("status") in FINAL and str(r.get("item_id", "")).startswith(prefix)]
        summary.update(ledger_calls=len(mine),
                       ledger_input_tokens=sum(r.get("input_tokens") or 0 for r in mine),
                       ledger_output_tokens=sum(r.get("output_tokens") or 0 for r in mine))
    return {"ok": not problems, "problems": problems, "session": session, "calls": summary}
