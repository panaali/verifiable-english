"""Frozen JT-E1s display generator: JT-E1r's generator with section 2.4's one revision.

The lint, the control capture and the shared lines are JT-E1r's frozen code, loaded as a private copy bound to
this directory. Only the English arm changes: after JT-E1r's unchanged declaration line it shows section 2.4's
answer row for the named conclusion. That row displays the frozen answer as the checker would state it (WG-7 and
JT-4 compute it in the product), so the run measures whether readers read 2.4's wording, not whether they infer
the class unaided.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PIN = "4d9a0eeb0"  # main when the frame was frozen, before reader calls

_spec = importlib.util.spec_from_file_location("jt_e1s_base_render", HERE.parent / "jt-e1r/render.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
base.HERE, base.CAPTURES, base.PIN = HERE, HERE / "captures", PIN
CAPTURES = base.CAPTURES
rows, lint, control, common_text, displays = base.rows, base.lint, base.control, base.common_text, base.displays
jt_e1r_english = base.english


def declaration(row):
    """Section 2.4's declaration row, unchanged from JT-E1r: the line JT-3 renders ("" for a fallback row)."""
    return jt_e1r_english(row, b"").decode()


def answer(row):
    """Section 2.4's answer row for the conclusion: zone settled, zone left to, or the conflict lines."""
    atom, decider = row["atom"], row["decider"]
    if row["answer"] == "settled":
        return [f"Settled: whatever is judged here, the text requires that {row['conclusion']}."]
    if row["answer"] == "turns":
        return [f"Left to {decider}: these two admissible completions give different answers"
                f" and differ on whether {atom} (a judgment for {decider})."]
    return [f"These rules conflict where {atom}.", f"Conflict-free, given these sentences: {row['criterion']}"]


def english(row, fallback):
    if row["lint"] != "accepted":
        return fallback
    return "".join(line + "\n" for line in [declaration(row).rstrip("\n"), *answer(row)]).encode()


base.english = english  # the private copy's audit and capture write this arm


def audit(*, capture=False):
    rejected = base.audit(capture=capture)
    for row in rows():
        assert row["answer"] != "turns" or row["decider"] != "unstated", row["id"]
        assert bool(row["criterion"]) == (row["answer"] == "conditional"), row["id"]
        assert not row["criterion"] or row["criterion"] in row["source"], row["id"]
    return rejected


if __name__ == "__main__":
    print("fallback rows:", ", ".join(audit(capture="--capture" in sys.argv)))
