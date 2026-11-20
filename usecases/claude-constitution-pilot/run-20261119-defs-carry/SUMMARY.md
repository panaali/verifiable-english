# Run 20261119 (defs carry): the probe translation with the source's definitions in its legends

Item defs-repair-claude-constitution-pilot-1119. DRI decision 2026-11-19, item 1
(manage-agents reviews/dri-decisions-20261119-defs-repair-claude-constitution-pilot-1119.md).

- **Derived from** run-20261104T0716Z, whose probe was measured at `c4d6e79f4`. That run is left byte-identical. Its
  `migrate_soft.py` and `measure.py` are imported unchanged by `carry_definitions.py`.
- **What changes.** Fifteen legends (3 sorts, 1 constant, 11 predicates) now end with the source's own definition of
  their term. The text is appended word for word, cut from the pinned body; the probe's body is that body,
  unchanged. Formulas, reading candidates' content, open terms and situations are unchanged.
- **Unit records (srccov-claude-constitution-pilot-1119, rule 8).** 26 units whose sentence states no rule are set
  aside for what the sentence is instead of a missing feature: `other.background` (11), `other.rationale` (8),
  `other.example` (5) and `other.navigation` (2). Only those units' kind and meaning change; they stay UNFORMALISED.
  Unit kinds are not part of the environment, so no identity changed; the regenerated search changed only its time.
  Report: `docs/infra/srccov-claude-constitution-pilot-1119/REPORT.md`.
- **Identities.** Descriptions are part of the environment's identity, so the environment id changes from
  `5164a9a5…` to `8c2e30a8…`. The 8 candidate `meaning_id`s and the 4 situation ids change with it.
- **Re-measured here.** The search (`answers/search.json`: 4.4 s on the rule-8 rerun, no pair without a situation,
  no search limit), the candidate ids (`answers/meaning-ids.json`) and C9's point status on every choice and condition
  (`answers/{after,strict}/point-status-c9.out`, `answers/measurements.json`). The point-status records equal the
  old run's byte for byte once the 64-hex identities are masked, with the same 80 statuses for each document.
- **Not re-measured.** The whole-translation steps on the probe and its strict twin (load, decided, check, render,
  coverage and the 12 readings queries: 17 steps) were not run (L70). They remain measured on the old run's probe,
  environment `5164a9a5…`.
- **The next pilot read** uses this directory's `probe-translation.probe.md`.

Commands: `uv run python usecases/claude-constitution-pilot/run-20261119-defs-carry/carry_definitions.py` (the probe,
search, ids and changed units), then `point_status.py` in this directory (C9's point status). Tests:
`tests/test_defs_repair_claude_constitution_pilot_1119.py`, `tests/test_srccov_claude_constitution_pilot_1119.py`.
