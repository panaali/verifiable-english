#!/usr/bin/env python3
"""Run 20261021T1800Z: the document change of this run, applied to the input of `nd.py` (`translation-without-content.ve.md`) and to the strict companions.

The audit of run 20261021T0600Z (AUDIT-20261021T0600Z-received.md: 19 of 20 sampled and 4 of 5 changed verdicts faithful) marked one unit unfaithful:

  * u0156.s03 (“Claude shouldn’t actively deceive the user about the existence of a system prompt or its content”): “The contextual readings still lose the situation.
    asked_to_keep_system_prompt_confidential(Claude,user) cannot distinguish two conversations involving the same pair. The source supplies no one-conversation-per-pair restriction;
    mentioning ‘which conversation’ in the open-term factors cannot supply the missing binding.”
    Repair: the regulated predicate, the exception term and the frame term are binary on (claude_instance, situation) instead of (claude_instance, user). The situation is the sort the
    document already uses for the hard constraints (“A situation in which Claude acts”); the act speaks of “the user in {1}”, which is what the source’s definite “the user” says
    (its presupposition that there is one stays recorded as a trigger). The guard of the in-frame candidates binds the instance (var 1) and the situation (var 0), so a request in
    one situation does not govern another, and another instance in the same situation is not bound. The rules’ content is unchanged: only the sort of the second argument, the act
    phrase, the English of the two open terms and the description change. frame_u0156.py and nd.py own the open terms.

    uv run python .../repair_20261021T1800Z.py          # edits translation-without-content.ve.md and readings/all-strict*.ve.md in place; refuses a second run
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))

_spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pilot)
import repair_20261021T0600Z as prev  # noqa: E402  (frame_companion only)

PRED = "system_prompt_deception_permitted"
ACT = "{0} actively deceive the user in {1} about system prompt existence-or-content"
DESCRIPTION = ("Claude is permitted to actively deceive the user in a situation about the existence of a system prompt or its content. Where no rule applies the text does not say "
               "(completion unspecified); the checker reports UNDECIDED. Nothing is permitted or forbidden for any party by default.")


def edit(meta):
    pred = meta["environment"]["vocabulary"]["predicates"][PRED]
    assert pred["arguments"] == ["claude_instance", "user"], pred["arguments"]
    pred["arguments"] = ["claude_instance", "situation"]
    assert pred["regulated"]["act"] == "{0} actively deceive {1} about system prompt existence-or-content", pred["regulated"]
    pred["regulated"]["act"] = ACT
    pred["description"] = DESCRIPTION
    return meta


def main():
    main_path = RUN / "translation-without-content.ve.md"
    raw = main_path.read_bytes()
    assert b'"arguments": ["claude_instance", "user"], "description": "Claude is permitted to actively deceive a user' in raw, "already repaired"
    _, front, body = raw.split(b"---\n", 2)
    meta = edit(json.loads(front))
    main_path.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False).encode() + b"\n---\n" + body)
    strict, strict_source = pilot.read(RUN / "readings/all-strict.ve.md")
    strict = edit(strict)
    pilot.write(RUN / "readings/all-strict.ve.md", strict, strict_source)
    narrow, narrow_source = pilot.read(RUN / "readings/all-strict-narrow.ve.md")
    pilot.write(RUN / "readings/all-strict-narrow.ve.md", edit(narrow), narrow_source)
    pilot.write(RUN / "readings/all-strict-in-frame.ve.md", prev.frame_companion(strict), strict_source)
    print("ok")


if __name__ == "__main__":
    main()
