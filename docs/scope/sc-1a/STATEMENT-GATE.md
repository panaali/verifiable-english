# sc-1a statement gate

The plan's gate (scope-PLAN.md 5, around line 414): a confirmation round on the draft-2 diff, not a fresh review,
decides PASS, and a clean confirmation opens SC-1a and SC-3a.

Verdict recorded: **PASS**, in `manage-agents/scope-p3ver2.final.md` (2026-10-13). The first confirmation round
(`manage-agents/scope-p3ver1.final.md`) found one inconsistency, the document mode's call of `govern` instead of the
run path `governFast`. Spec draft 3 and plan draft 4 (commit `581d9c02`) fix it, and the second round confirmed the
fix and found no other substantive change. `manage-agents/scope-design-ready.final.md` records the design as ready to
build.

Later drafts change no statement this item builds:
- Plan draft 5 and spec draft 4 (phase 1, SC-M0) change no definition, theorem statement or fixture value (spec 9.6,
  "Changes in this draft"; plan "Changes in this draft (draft 5)": "no Lean statement changes").
- The phase-2 check (`manage-agents/scope-ph2-check.final.md`, FIX) raised three wording points (SC-M0 tagging,
  F15 and AP-3, C11's claim). They are fixed in `5c5faba50`, which leaves every Lean block byte-identical
  (`manage-agents/scope-ph2-fix.final.md`). None bears on SC-1a.

DRI-DECISIONS-PHASE2, "Scope": SC1 (the AP-3 → SC-4 queue) and SC2 (pilot prompts) do not touch SC-1a. SC3 adds
`research` to the layer policy in its own item and leaves SC-1a's append unchanged. SC-1a needs no layer-policy line:
`tools/layer_policy.py` maps every `VE.*` module that no earlier rule names to layer 2, profiles, which is where the
plan puts `VE.Layout.*` and `VE.Scope.*`.

Since a PASS was recorded, no new confirmation round was run.
