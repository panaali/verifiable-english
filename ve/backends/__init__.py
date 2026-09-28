"""Checker backends (docs/spec/SEMANTICS-MIGRATION-PLAN.md, stages 1 and 2).

The one-shot runner and the stage-1 persistent Lean service live here. The
service is additive; no semantic function uses it yet. Both classify operational
failures as `CheckerUnavailable`, never as a verdict.
"""
