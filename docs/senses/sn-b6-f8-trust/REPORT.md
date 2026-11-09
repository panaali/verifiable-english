# sn-b6-f8-trust REPORT (count three senses definitions in the trust budget)

Status: deliverables (1)-(4) built. `projectionIds`, `admittedIds` and `usedOf` count as G[V]; trust V +38, K +0, S +0
(R16, under its 150-line cap). HEAD: the commit that adds this report's last edit; base `9ba8aeaed` (main).
Open: `Projection.written` / `SensesOutcome.written` sent to the DRI decider (not moved, as the task asks); the R16 ties pass
(FOLLOW-UPS). No DRI signature is reserved. No Lean definition, statement, verdict or wire output changes.
Decisions: reviews/dri-decisions-20261105-cfr2.md (C-finding regrade 11-04 #9, sn-b6-review-ov F8 regraded A),
reviews/dri-decisions-20261109-lp0412.md item 2.

## Deliverables

| Task line | Done | Commit / where | Test or command |
|---|---|---|---|
| (1) move the three names from G[I] to G[V] under `VE/Senses/Run.lean`; leave the two `written` definitions | yes | `0474e627f`, `tools/trust-classes.json` | `uv run python tools/trust_map.py --check` |
| (2) re-measure on the final HEAD; baseline entry naming this item; the trust check passes | yes: V +38 (projectionIds +10, admittedIds +24, usedOf +4) | `977749685`, `docs/trust-baseline.json` (allowance V 38 over `9ba8aeaed`, reason names sn-b6-f8-trust, signature R16) | `trust_map.py --check`: "VE/Senses/Run.lean: trusted +38", "PASS: K, S and untied [V] within 9ba8aeaedfc8 and the allowances introduced since" |
| (3) DELTA row per file, Ruling R16 | yes | `DELTA.md` row 1 | `review-ready.py` [delta] (run by the chain) |
| (3) each definition exercised by a test that can fail; `admittedIds` checked in RunExamples | yes, no example added | `lean/VE/Senses/RunExamples.lean` | seeded bugs 1-3 below |
| (3) FOLLOW-UPS row asking for a ties pass | yes | `evidence/follow-ups-row.md`, appended verbatim to manage-agents FOLLOW-UPS.md | - |
| (4) one seeded bug per definition | yes, 3 | below | `lake build VE.Senses.RunExamples` |

Line counts: `lean/declarations.txt` gives `projectionIds` 234:0-242:75, `usedOf` 258:0-260:79, `admittedIds` 288:0-310:42;
with the blank line before the next docstring each (243, 261, 311) that is 10 + 4 + 24 = 38, the `trust_map.py --check`
figure.

`admittedIds` was already checked in `lean/VE/Senses/RunExamples.lean`: the pinned `runCaseReported` answers of
identified requests hash the whole answer, and `admittedIds` builds its `identities`, `used`, `preamble`, `flips` and
candidate ids. Seeded bug 3 breaks the pins at lines 120, 122, 128, 132, 134, 136, 171 and 173. So no example was added.

## Not moved: `Projection.written` and `SensesOutcome.written` (sent to the DRI decider)

They stay G[I] as the task asks. By trust_map's own rule ("`[I]` identity and provenance", `tools/trust_map.py:7-8`)
they look decision-path too. `Projection.written` rewrites the projection's environment JSON (its `profiles` member).
`senses.project` returns that JSON on the wire as the projection's `environment` (`lean/VE/Senses/Run.lean:444-447`) for
B7 to read, and it also feeds `environmentId`. The newly counted `admittedIds` calls it (`Run.lean:305`).
`SensesOutcome.written` lifts it over the outcome that `readCase` then encodes (`Run.lean:390`; the sense-map entry at
line 400 reads that projection). If moved: +13 trusted lines (declarations 221-227 and 229-232, 8 + 5 with the blank line
after each). Sent with `msg.sh dri`: manage-agents/inbox/dri/20261109T080332Z-sn-b6-f8-trust-2023641.md.

## Seeded bugs (Lean; each planted alone in `lean/VE/Senses/Run.lean`, then restored with `git checkout`)

| # | Definition | Bug | Failing test (`lake build VE.Senses.RunExamples`, the error lines it printed) |
|---|---|---|---|
| 1 | `usedOf` | `.eraseDups` → `.eraseDups.reverse` | `RunExamples.lean:43` (`usedOf P == ["funny", "tells"]`); also 128, 171, 173 |
| 2 | `projectionIds` | lexicon digest tag `ve-english-lexicon-v1\n` → `v2` | `RunExamples.lean:55` (the `idsOf` guard: `lexicon_id` is the digest of the lexicon); also 120, 122, 128, 132, 134, 136, 146, 148, 171, 173 (the first 11 error lines, read with `head`) |
| 3 | `admittedIds` | `("used", toJson used)` → `toJson (used.drop 1)` | `RunExamples.lean:120` (an open unit with its identities); also 122, 128, 132, 134, 136, 171, 173 |

Each run failed the build (`✖ [253/253] Building VE.Senses.RunExamples`). After the restore, `lake build VE.Senses.RunExamples` succeeds. No Python or Rust
product code changed. The diff changes no Lean file, so the bugs were planted in the definitions this item reclassifies.

## Trust mutants (checklist 13a): N.A.

`uv run python tools/trust_mutants.py --plan` on this branch prints `{"base": "9ba8aeaed...", "definitions": 0,
"mutants": 0, "to_run": 0, "not_run": 0}`. The tool selects trusted declarations whose lines the tree changes over the
base, and this item changes no Lean line, so a sweep would judge nothing. The three seeded bugs above are the R16
evidence that each newly counted definition is exercised by a test that can fail.

## Checks

- Condition test 1, the trust-map check: `uv run python tools/trust_map.py --check` passes (quoted above). The selection
  (`tools/select_tests.py --base 9ba8aeaed`, 97/556 units) includes `tests/test_trust_budget.py`; the gate runs it too.
- Condition test 2, the senses run examples: `lean/VE/Senses/RunExamples.lean` runs as `lake build VE.Senses.RunExamples`
  (passes on the restored tree) and in the gate's full `lake build`. `lean/VE.lean` imports it. select_tests has no lake step.
- Selected tests: run once on the committed tree. The result is in the build report.
- Not run: `regen_generated.py` (the only generated set that reads `tools/trust-classes.json` is `trust-tables`, and its
  check is `trust_map.py --check`); the full `lake build` and `lean/audit.py` (no Lean file changed); the full gate (the
  chain runs it).

## Self-review

SELF-REVIEW: 0 A, 3 B, 4 C; fixed 7 (report summary, self-review section and not-run list; trust mutants recorded N.A.
with the plan output; the `written` finding sent to the DRI; the rule quote; the seeded-bug lines; the condition tests;
the unreached `throw` in the follow-up row).

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer or schema changes (the diff is trust tables and docs).
2. PASS: the deliverables table above maps each task line to a commit and a check. No Python copy of Lean logic and no new report test.
3. PASS: seeded bugs 1-3 (`RunExamples.lean:43`, `:55`, `:120`). Trust mutants N.A.: the plan has 0 mutants (above).
4. N.A.: no product output changes (no Lean, Python or Rust product code).
5. N.A.: no field read from a Lean answer is added or changed.
6. PASS: the chain gates the committed final HEAD. Main has not moved past the base `9ba8aeaed`.
7. PASS: one DELTA row, Ruling R16, with the conditions it asks for (per-file growth, seeded bugs, FOLLOW-UPS row). No reserved signature.
8. PASS: the one user-visible change, the trust budget, is DELTA row 1. Wire outputs do not change: no Lean source changed (`git diff --stat 9ba8aeaed` lists only `tools/` and `docs/` files).
9. PASS: `select_tests.py --base 9ba8aeaed` selects 97/556 units, including `tests/test_trust_budget.py`.
10. N.A.: no Lean statement or proof.
11. N.A.: no budget, limit or deadline code.
12. N.A.: no code on a runtime path.
13. N.A.: no test removed or renamed.
14. PASS: the opposite direction is covered by the restored tree building and the trust check passing. Each REPORT claim names its command. The task text was re-read for the DELTA row and the FOLLOW-UPS row.
15. PASS: overclaims checked ("no Lean change": `git diff --stat`; "no example added": seeded bug 3). No deliverable was cut. Every check named can fail (seeded bugs). Limits N.A.
