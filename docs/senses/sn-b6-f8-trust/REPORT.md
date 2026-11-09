# sn-b6-f8-trust REPORT (count three senses definitions in the trust budget)

Item: follow-up sn-b6-f8-trust (reviews/dri-decisions-20261105-cfr2.md, C-finding regrade 11-04 #9: sn-b6-review-ov F8
regraded A, the trusted-base rule broken; queued repair-first by reviews/dri-decisions-20261109-lp0412.md item 2).
Base: `9ba8aeaed` (main). No Lean definition, statement, verdict or wire output changes.

## What changed

| Deliverable | Done | Where |
|---|---|---|
| (1) `projectionIds`, `admittedIds`, `usedOf` from G[I] to G[V] under `VE/Senses/Run.lean` | yes | `tools/trust-classes.json` |
| (2) re-measured on the final HEAD; baseline allowance naming this item; trust check passes | yes: V +38, K +0, S +0 (projectionIds +10, admittedIds +24, usedOf +4) | `docs/trust-baseline.json` (allowance V 38, commit `9ba8aeaed`); `uv run python tools/trust_map.py --check`: PASS |
| (3) R16: DELTA row per file, each definition exercised by a test that can fail, FOLLOW-UPS row | yes, growth 38 is under the 150-line cap | `DELTA.md` row 1 (Ruling R16); `evidence/follow-ups-row.md` (also appended to manage-agents FOLLOW-UPS.md) |
| (4) one seeded bug per definition | yes, 3 | below |

`admittedIds` is already checked in `lean/VE/Senses/RunExamples.lean`: the pinned `runCaseReported` answers of
identified requests (lines 120-136, 171, 173) hash the whole answer, whose `identities`, `used`, `preamble`, `flips`
and candidate ids `admittedIds` builds; seeded bug 3 shows it. So no example was added.

## Not moved: `Projection.written` and `SensesOutcome.written` (a finding for the DRI decider)

They stay G[I] as the task asks. By the trust map's own rule ([I] is "hashes, ids and binding checks", tools/trust_map.py
docstring and the trust map's section 2) they look decision-path too: `Projection.written` rewrites the projection's
environment JSON (its `profiles` member), which `senses.project` returns on the wire as the projection's `environment`
(`lean/VE/Senses/Run.lean:444-447`) for B7 to read, besides feeding `environmentId`; `SensesOutcome.written` lifts it over
the outcome that `readCase` then encodes (`Run.lean:390`, the sense-map entry of line 400 reads that projection). They
are content, not only ids. Size if moved: 8 + 5 lines (declarations 221-227 and 229-232 with their docstrings and the blank line after each).
Reported for a separate DRI decision; not moved here.

## Seeded bugs (Lean; each restored)

| # | Definition | Bug (file `lean/VE/Senses/Run.lean`) | Failing test |
|---|---|---|---|
| 1 | `usedOf` | `.eraseDups` → `.eraseDups.reverse` | `lake build VE.Senses.RunExamples`: `RunExamples.lean:43` (`usedOf P == ["funny", "tells"]`), also 128, 171, 173 |
| 2 | `projectionIds` | lexicon digest tag `ve-english-lexicon-v1\n` → `v2` | `RunExamples.lean:55` (the `idsOf` guard: `lexicon_id` is the digest of the lexicon), also the pins 120-148 |
| 3 | `admittedIds` | `("used", toJson used)` → `toJson (used.drop 1)` | `RunExamples.lean:120` (open unit, its identities), also 122, 128, 132, 134, 136, 171, 173 |

Only Lean product code would count as changed product code here, and none is changed in the commit (the bugs were
planted in the definitions this item reclassifies). No Python or Rust product code changed.

## Checks

- `uv run python tools/trust_map.py --check`: PASS, "VE/Senses/Run.lean: trusted +38", "allowed V +38 over 9ba8aeaedfc8".
- `lake build VE.Senses.RunExamples`: builds on the restored tree.
