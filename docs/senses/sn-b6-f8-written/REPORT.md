# sn-b6-f8-written REPORT (count `Projection.written` and `SensesOutcome.written` in the trust budget)

Status: deliverables (1)-(4) built. `VE.Senses.Projection.written` and `VE.Senses.SensesOutcome.written` count as G[V];
trust V +13, K +0, S +0 (R16, under its 150-line cap; the DRI's measured +13 holds exactly). Base `223babd3d` (main,
synced at `5b1ed6101`; first measured over `1ddb87dc1`, after sn-b6-f8-trust `6db6ee16d`, also +13). No DRI signature is reserved. No Lean definition, statement, verdict or wire output
changes. Open: the R16 ties pass (FOLLOW-UPS).
Decision: reviews/dri-decisions-20261109-sn-b6-f8-written.md item 1.

## Deliverables

| Task line | Done | Commit / where | Test or command |
|---|---|---|---|
| (1) move the two names from G[I] to G[V] under `VE/Senses/Run.lean`; nothing else moves | yes (the emptied G[I] group is removed; the three new example helpers are added to the file's existing T list, since an unclassified declaration counts as trusted) | `905d787f3`, `d1777f522` (main's order kept after the merge: the diff is +7/-6 lines), `tools/trust-classes.json` | `uv run python tools/trust_map.py --check` |
| (2) re-measure on the final HEAD; baseline allowance naming this item; the trust check passes | yes: V +13 (`Projection.written` +8, `SensesOutcome.written` +5) | `905d787f3`, `docs/trust-baseline.json` (allowance V 13 over `223babd3d`, reason names sn-b6-f8-written, signature R16) | `trust_map.py --check`: "against 223babd3d047: K +0, S +0, ... trusted +13", "VE/Senses/Run.lean: trusted +13", "PASS: K, S and untied [V] within 223babd3d047 and the allowances introduced since" |
| (3) DELTA row per file, Ruling R16 | yes | `DELTA.md` row 1 | `review-ready.py` [delta]: UNVERIFIED here (the chain runs it) |
| (3) each definition exercised by a test that can fail | yes, two `#guard` examples added (no pin depended on the written list) | `b49d72aa8`, `d45977b38`, `lean/VE/Senses/RunExamples.lean:197-220` | seeded bugs 1-3 below |
| (3) FOLLOW-UPS row asking for a ties pass | yes | `evidence/follow-ups-row.md`, appended verbatim to manage-agents FOLLOW-UPS.md | - |
| (4) one seeded bug per definition | yes, 2, plus 1 on the side that keeps the list | below | `lake build VE.Senses.RunExamples` |
| No change to any Lean definition, statement, verdict or wire output | yes | - | `git diff --stat 223babd3d..HEAD -- lean ':!lean/VE/Senses/RunExamples.lean' ':!lean/declarations.txt'` prints nothing; `lean/statements.txt` is not in the diff; `declarations.txt` changes only RunExamples rows (line shifts and the three helpers) |
| Condition tests kept selected | yes | - | `tools/select_tests.py --base 223babd3d`: 103/559 units, including `lake build` (builds `VE.Senses.RunExamples` through `lean/VE.lean`) and `tests/test_trust_budget.py` |
| Size: trust-map records plus at most two examples, under 60 lines | yes | - | `git diff --numstat 223babd3d..HEAD`: `RunExamples.lean` +25, `trust-classes.json` +7/-6, `trust-baseline.json` +7 (39 lines added; docs and the generated `declarations.txt` aside) |

Line counts: `lean/declarations.txt` gives `Projection.written` 221:0-227:17 and `SensesOutcome.written` 229:0-232:10;
with the blank line after each (228, 233) that is 8 + 5 = 13, the `trust_map.py --check` figure.

## Why examples were added

No existing pin depended on the written profile list. With seeded bug 1 planted (`Projection.written` returns `P`
unchanged) before the new examples existed, `lake build VE.Senses.RunExamples` succeeded: every pinned request uses the
fixture's v0 environment (`"profile"`, no `"profiles"` member), so `.written` was the identity on all of them.

The new examples (`RunExamples.lean`, section "The profile list as written") send a `ve.core@0.2` environment listing
`["documents@1", "judgments@0", "relational-fol@0"]`, with its lexicon bound to that environment's id. The reader
decides without the document layer (`VE.Compose.decidingEnvironment` leaves `["documents@1", "relational-fol@0"]`,
checked in the first conjunct of line 214), and these answers must return the list as written:

- line 214: `senses.project` (`projectCaseReported`), `result.projection.environment.profiles` (`Projection.written`);
- line 219: an identified `senses.read` source request (`runCaseReported`), `result.reading.environment.profiles`
  (`SensesOutcome.written`, through `readCase`, Run.lean:390).

The helpers `envL`, `layered` and `profilesOf` are test code, class T in `tools/trust-classes.json`.

## Seeded bugs (Lean; each planted alone in `lean/VE/Senses/Run.lean`, then restored with `git checkout` and rebuilt)

| # | Definition | Bug | Failing test (`lake build VE.Senses.RunExamples`) |
|---|---|---|---|
| 1 | `Projection.written` (Run.lean:226) | `\| .ok ps => { P with envJson := P.envJson.setObjVal! "profiles" ps }` → `\| .ok _ => P` (keeps the projection's own profiles) | `RunExamples.lean:214` (`senses.project` list) and `:219` (the read answer, which lifts it) |
| 2 | `SensesOutcome.written` (Run.lean:231) | `.ok units senses mixed unused (P.written environment)` → `.ok units senses mixed unused P` (outcome unchanged) | `RunExamples.lean:219` only |
| 3 | `Projection.written` keep side (Run.lean:227) | `\| .error _ => P` → `\| .error _ => { P with envJson := P.envJson.setObjVal! "profiles" (toJson ([] : List String)) }` (writes a list when the request has none) | `RunExamples.lean:120`, `:122`, `:128`, `:132`, `:134`, `:136`, `:146` and later pins (the v0 requests, which have no `profiles` member) |

Each run failed the build (`✖ [253/253] Building VE.Senses.RunExamples`), on the synced tree (`d45977b38`); bugs 1 and 2
were first shown on `b49d72aa8` with the guards at lines 216 and 219, before the precondition was folded in. After the restore, `lake build
VE.Senses.RunExamples` succeeds. No Python or Rust product code changed; the bugs were planted in the two definitions
this item reclassifies (this diff changes no Lean product file).

## Trust mutants (checklist 13a)

The light lane printed NOT (the two trust files count as trusted core), so the sweep ran:
`mac-pytest.sh --trustmut -- --test lean/VE/Senses/RunExamples.lean --json docs/senses/sn-b6-f8-written/trust-mutants.json`
on `a386daf02` (ve-cloud-3): "0 definitions, 0 mutants (0 to run) ... 0 KILLED, 0 SURVIVOR, 0 UNKNOWN", exit 0. The
tool selects trusted declarations whose lines the tree changes, and this item changes no Lean product line, so it
judges nothing; seeded bugs 1-3 are the R16 evidence. (`d1777f522` after it only restores main's key order in the
two trust files; their contents are the same.)

## Checks

- Condition test 1, the trust-map check: `uv run python tools/trust_map.py --check` passes (quoted above);
  `uv run pytest -q tests/test_trust_budget.py`: 7 passed.
- Condition test 2, the senses run examples: `lake build VE.Senses.RunExamples` passes on the restored tree.
- Full `lake build` (1327 jobs) and `python3 lean/audit.py` ("PASS: 795 source files; 8805 named theorem
  declarations audited") on the synced tree.
- `uv run python tools/regen_generated.py --write` once after the sync: it rewrote only `docs/codemap/*` with main's
  own lag ("regenerated on every merge to main"), none from this item, so that was reverted;
  `regen_generated.py --check` then passed ("checked 37 entries"). `lean/declarations.txt` is from
  `tools/lean_statements.py`.
- Selected tests: `MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base 223babd3d --run` on committed `cd8bc6332` (clean tree): exit 0; "recorded 103 units for tree bf8cea9e8a; ... 0 failed" (ve-cloud-3, 7484 s).
- Not run: the full gate (the chain runs it).

## Self-review

SELF-REVIEW: 0 A, 2 B, 6 C; fixed 8 (B1 the precondition folded into the line-214 guard; B2 deliverables rows for the
no-change, condition-test and size lines; C1 section comment narrowed to the two answers; C2 DELTA guard count; C3 the
keep side seeded as bug 3; C4 the ties row names `projectCase_fits` / `projectCaseReported_fits`; C5 the [delta] check
marked UNVERIFIED; C6 synced with main and re-measured, +13 holds).

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer or schema changes (trust tables, two Lean examples, docs).
2. PASS: the deliverables table maps each task line to a commit and a check. No Python copy of Lean logic; no new report test.
3. PASS: seeded bugs 1-3 (`RunExamples.lean:214`, `:219`, `:120`); trust mutants ran (0 mutants, above).
4. N.A.: no product output changes (no Lean, Python or Rust product code).
5. N.A.: no field read from a Lean answer is added or changed.
6. PASS: synced with main (`223babd3d`); the final selected run is on the committed final tree; the chain gates the final HEAD.
7. PASS: one DELTA row, Ruling R16, with its conditions (per-file growth on the final HEAD, seeded bugs, FOLLOW-UPS row). No reserved signature.
8. PASS: the one user-visible change, the trust budget, is DELTA row 1; wire outputs do not change (the no-change row above).
9. PASS: `select_tests.py --base 223babd3d` selects 103/559 units, including `lake build` and `tests/test_trust_budget.py`.
10. N.A.: no Lean statement or proof.
11. N.A.: no budget, limit or deadline code.
12. N.A.: no code on a runtime path.
13. N.A.: no test removed or renamed.
14. PASS: both directions seeded (bug 1/2 the rewrite, bug 3 the keep side); each REPORT claim names its command; the task and the DRI decision were re-read for the DELTA and FOLLOW-UPS rows.
15. PASS: overclaims checked (the no-change claim by `git diff --stat`; "no pin depended on it" by bug 1 before the examples); every new `#guard` has a seeded bug; no deliverable cut.
