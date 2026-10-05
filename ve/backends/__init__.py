"""Checker backends (docs/spec/SEMANTICS-MIGRATION-PLAN.md, stages 1 and 2).

The one-shot runner and the stage-1 persistent Lean service live here; `relay.py` is the
one Python entry to the service's decisions (docs/LEAN-FIRST-PLAN.md, rule 2). Both
classify operational failures as `CheckerUnavailable`, never as a verdict.
"""
