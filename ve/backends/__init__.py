"""Checker backends. Every external checker invocation in `ve` goes through here.

SEMANTICS-MIGRATION-PLAN.md stage 1 adds the persistent Lean service next to
the one-shot runner in `lean.py`; both classify operational failures as
`CheckerUnavailable`, never as a verdict.
"""
