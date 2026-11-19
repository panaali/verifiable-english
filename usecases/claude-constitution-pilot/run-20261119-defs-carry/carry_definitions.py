#!/usr/bin/env python3
"""defs-repair-claude-constitution-pilot-1119: run-20261104T0716Z's probe with the source's definitions in its legends.

    uv run python usecases/claude-constitution-pilot/run-20261119-defs-carry/carry_definitions.py
    uv run python usecases/claude-constitution-pilot/run-20261119-defs-carry/point_status.py

The run of 20261104T0716Z stays as it was recorded (DRI decision 2026-11-19,
reviews/dri-decisions-20261119-defs-repair-claude-constitution-pilot-1119.md item 1). This script imports that run's
`migrate_soft.py` unchanged (`point_status.py` imports its `measure.py`), points its outputs at this directory and
adds one rewrite rule:

7. The legend of each of 15 terms a rule uses carries the source's own definition of the term, word for word,
   appended to the legend's description (`carry_definitions`). Each passage is cut from the pinned body: it starts
   with the words given here and ends with the words given here, and nothing in between is written by this script.

The first command writes `probe-translation.probe.md` the way `migrate_soft.main` does. It runs rules 1 to 7, gives
the candidate identities, runs SC-8's search and writes `answers/search.json`, `answers/meaning-ids.json` and
`changed_units.json`. The second runs only `measure.py`'s `point-status-c9` steps (after, strict) on this
probe. The run's whole-translation steps (check, coverage, readings) are not run here (L70).
"""
from __future__ import annotations

import copy
import re
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
OLD = RUN.parent / "run-20261104T0716Z"
sys.path.insert(0, str(OLD))
import migrate_soft  # noqa: E402

PROBE = RUN / "probe-translation.probe.md"
_REWRITE = migrate_soft.rewrite

# (vocabulary kind, name) -> the passages of the body its legend carries, each given by its first and last words.
# The body is read with its list marks and bold marks dropped and its lines joined by one space (`flat_source`).
ANTHROPIC = ("Anthropic: We are the entity", "than operators or users.")
GUIDELINES = (("Compliant with Anthropic’s guidelines: Acting", "where they’re relevant."),
              ("Beyond the broad principles outlined in this document", "in particular circumstances."), ANTHROPIC)
CLAUDE = (("The name “Claude” is often used", "documents like this one."),)
USERS = (("Users: Those who interact with Claude", "than mistakenly assuming there is."),
         ("Whether someone should be treated as an operator or user", "what kind of entity they are."))
DECEPTION = (("Deception involves attempting", "what was happening."),)
DEFINITIONS = {
    ("sorts", "claude_instance"): CLAUDE,
    ("constants", "claude"): CLAUDE,
    ("sorts", "operator"): (("Operators: Companies and individuals", "within their platforms."), *USERS),
    ("sorts", "user"): USERS,
    ("predicates", "instruction_deceptive_tactics_harming_users"): DECEPTION,
    ("predicates", "system_prompt_deception_permitted"): DECEPTION,
    ("predicates", "judgment_use_required"): (
        ("Conversational inputs: Tool call results", "(e.g., performing a search)."),
        ("And if any outputs of the Claude subagents", "instructions from a principal.")),
    ("predicates", "instruction_dishonest_looking_within_honesty"): (
        ("There are many different components of honesty", "through their own reasoning process."),),
    ("predicates", "instruction_act_against_guidelines"): GUIDELINES,
    ("predicates", "compliance_against_guidelines"): GUIDELINES,
    ("predicates", "compliance_unsafe"): (("Broadly safe: Not undermining", "current phase of development."),),
    ("predicates", "compliance_unethical"): (("Broadly ethical: Having good", "dangerous or harmful."),),
    ("predicates", "clear_and_substantial_undermining_of_oversight"): (
        ("That is, per the hard constraints, we want Claude", "catastrophic forms of power-seeking."),
        ("Supporting human oversight doesn’t mean", "big-picture safety below."), ANTHROPIC),
    ("predicates", "illegitimate_absolute_control"): (
        ("Assessing the legitimacy of a given attempt", "an attempt to escape accountability."),),
    ("predicates", "seemingly_compelling_argument_to_cross_line"): (
        ("The current hard constraints on Claude’s behavior", "sexual abuse material (CSAM)."),
        ("These represent absolute restrictions for Claude", "rarely, if ever, outweigh them."),
        ("Hard constraints are restrictions on the actions", "should otherwise promote."),
        ("Hard constraints are centrally meant to apply", "fall into such a category.")),
}


def flat_source(source):
    """The body as one line: each nonblank line without its list mark (`* `, `- `, `1. `) and bold marks (`**`),
    joined by one space."""
    lines = (re.sub(r"^\s*(?:[*-]|\d+\.)\s+", "", line).replace("**", "").strip()
             for line in source.decode("utf-8").splitlines())
    return " ".join(line for line in lines if line)


def passage(flat, start, end):
    """The passage of `flat` from the one place `start` occurs to the first `end` after it, both included."""
    i = flat.find(start)
    if i < 0 or flat.find(start, i + 1) >= 0:
        raise ValueError(f"the start of a passage must occur exactly once: {start!r}")
    j = flat.find(end, i + len(start))
    if j < 0:
        raise ValueError(f"no end {end!r} after {start!r}")
    return flat[i:j + len(end)]


def carry_definitions(meta, source, definitions=DEFINITIONS):
    """Rule 7: each legend of `definitions` with its passages appended to its description, one space apart. A name
    the vocabulary lacks is refused."""
    meta = copy.deepcopy(meta)
    flat = flat_source(source)
    vocabulary = meta["environment"]["vocabulary"]
    for (kind, name), spans in definitions.items():
        entry = vocabulary[kind].get(name)
        if entry is None:
            raise ValueError(f"no {kind} {name} in the vocabulary")
        entry["description"] = " ".join([entry["description"], *(passage(flat, a, b) for a, b in spans)])
    return meta


def rewrite(meta):
    """run-20261104T0716Z's rules 1 to 4 (its `rewrite`, unchanged), then rule 7 over the pinned body."""
    after, changed = _REWRITE(meta)
    return carry_definitions(after, migrate_soft.pinned().split(b"---\n", 2)[2]), changed


def here():
    """Point the old run's `migrate_soft.py` at this directory and its rewrite at `rewrite`."""
    migrate_soft.RUN, migrate_soft.PROBE, migrate_soft.rewrite = RUN, PROBE, rewrite


if __name__ == "__main__":
    if sys.argv[1:]:
        sys.exit(__doc__)
    here()
    migrate_soft.main()
