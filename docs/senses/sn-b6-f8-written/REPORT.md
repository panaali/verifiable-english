# sn-b6-f8-written REPORT (count `Projection.written` and `SensesOutcome.written` in the trust budget)

Status: deliverables (1)-(4) built. `VE.Senses.Projection.written` and `VE.Senses.SensesOutcome.written` count as G[V];
trust V +13, K +0, S +0 (R16, under its 150-line cap; the DRI's measured +13 holds exactly). Base `1ddb87dc1` (main,
after sn-b6-f8-trust `6db6ee16d`). No DRI signature is reserved. No Lean definition, statement, verdict or wire output
changes. Open: the R16 ties pass (FOLLOW-UPS).
Decision: reviews/dri-decisions-20261109-sn-b6-f8-written.md item 1.

## Deliverables

| Task line | Done | Commit / where | Test or command |
|---|---|---|---|
| (1) move the two names from G[I] to G[V] under `VE/Senses/Run.lean`; nothing else moves | yes (the emptied G[I] group is removed; the three new example helpers are added to the file's existing T list, since an unclassified declaration counts as trusted) | `905d787f3`, `tools/trust-classes.json` | `uv run python tools/trust_map.py --check` |
| (2) re-measure on the final HEAD; baseline allowance naming this item; the trust check passes | yes: V +13 (`Projection.written` +8, `SensesOutcome.written` +5) | `905d787f3`, `docs/trust-baseline.json` (allowance V 13 over `1ddb87dc1`, reason names sn-b6-f8-written, signature R16) | `trust_map.py --check`: "VE/Senses/Run.lean: trusted +13", "PASS: K, S and untied [V] within 1ddb87dc12c7 and the allowances introduced since" |
| (3) DELTA row per file, Ruling R16 | yes | `DELTA.md` row 1 | `review-ready.py` [delta] (run by the chain) |
| (3) each definition exercised by a test that can fail | yes, two examples added (no pin depended on the written list) | `b49d72aa8`, `lean/VE/Senses/RunExamples.lean:197-220` | seeded bugs 1-2 below |
| (3) FOLLOW-UPS row asking for a ties pass | yes | `evidence/follow-ups-row.md`, appended verbatim to manage-agents FOLLOW-UPS.md | - |
| (4) one seeded bug per definition | yes, 2 | below | `lake build VE.Senses.RunExamples` |

Line counts: `lean/declarations.txt` gives `Projection.written` 221:0-227:17 and `SensesOutcome.written` 229:0-232:10;
with the blank line after each (228, 233) that is 8 + 5 = 13, the `trust_map.py --check` figure.

## Why examples were added

No existing pin depended on the written profile list. With seeded bug 1 planted (`Projection.written` returns `P`
unchanged) before the new examples existed, `lake build VE.Senses.RunExamples` succeeded: every pinned request uses the
fixture's v0 environment (`"profile"`, no `"profiles"` member), so `.written` was the identity on all of them.

The new examples (`RunExamples.lean`, section "The profile list as written") send a `ve.core@0.2` environment listing
`["documents@1", "judgments@0", "relational-fol@0"]`, with its lexicon bound to that environment's id. The reader
decides without the document layer (`VE.Compose.decidingEnvironment`, checked at line 213: it leaves
`["documents@1", "relational-fol@0"]`), and each answer must return the list as written:

- line 216: `senses.project` (`projectCaseReported`), `result.projection.environment.profiles` (`Projection.written`);
- line 219: an identified `senses.read` source request (`runCaseReported`), `result.reading.environment.profiles`
  (`SensesOutcome.written`, through `readCase`, Run.lean:390).

The helpers `envL`, `layered` and `profilesOf` are test code, class T in `tools/trust-classes.json`.

## Seeded bugs (Lean; each planted alone in `lean/VE/Senses/Run.lean`, then restored with `git checkout` and rebuilt)

| # | Definition | Bug | Failing test (`lake build VE.Senses.RunExamples`) |
|---|---|---|---|
| 1 | `Projection.written` (Run.lean:226) | `\| .ok ps => { P with envJson := P.envJson.setObjVal! "profiles" ps }` → `\| .ok _ => P` (keeps the projection's own profiles) | `RunExamples.lean:216` (`senses.project` list) and `:219` (the read answer, which lifts it) |
| 2 | `SensesOutcome.written` (Run.lean:231) | `.ok units senses mixed unused (P.written environment)` → `.ok units senses mixed unused P` (outcome unchanged) | `RunExamples.lean:219` only |

Each run failed the build (`✖ [253/253] Building VE.Senses.RunExamples`). After the restore, `lake build
VE.Senses.RunExamples` succeeds. No Python or Rust product code changed; the bugs were planted in the two definitions
this item reclassifies (this diff changes no Lean product file).

## Trust mutants (checklist 13a)

PENDING

## Checks

PENDING

## Self-review

PENDING

## Self-review against BUILDER-CHECKLIST

PENDING
