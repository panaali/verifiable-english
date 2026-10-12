# Question answering Q2: builder's progress notes (working file)

Branch `question-answering/q2`, base `main` at `f0547468`. This file records decisions and state so the batch can be
resumed; the final report is `docs/spec/question-answering-q2/REPORT.md`, the deltas `docs/spec/question-answering-q2/DELTA.md`.

## Decisions

1. **Three routes for `ask`, chosen by Lean from the document's profiles** (`VE.Ask.Run.routeOfDocument`).
   - *readings* (`readings@1`): RD-3's `replayVerdictsND` on the request's `case`, the approved `Asked` /
     `ask_wire_sound` of spec 5.2. UDHR part 7.
   - *plain* (no norms, no readings; R13): the approved `PlainAsked` / `plain_ask_wire_sound`. G document.
   - *norm-defaults, no reading set* (the agent-policy documents: `norms@0` + `norm-defaults@0`, no `readings@1`).
     Plan 4.7 says Q2.2 "extends [RD-3's] admission to zero sets". Measured on `a-unspecified.ve.md`: RD-3's admission
     with `readings@1` inserted passes `admitS2` but takes **73 s** of Lean per replay (three runs: 68, 74, 73 s),
     and the document is refused as not enumerated. The norm-defaults route elaborates the same policy in 0.2 s. So
     the zero-set case is a third adapter (`VE.Ask.ZeroWire`, `ZeroAnswer`) on the norm-defaults route's own checkers
     (`acceptanceU`, `modelCheckU`, `conflictFreeCheckU`, `witnessFromU`), one row with choice `[]`, whose claims are
     RD-3's per-choice claims on the document's own `UDoc` (`LeadHolds N ψ r = LeadHoldsU (choiceU N c) …` by `rfl`,
     `leadHolds_eq`). Its statements are new (not in spec 5.2): DRI review needed.
2. **Segment order of sources** (task: "sourcesU_length alone is too weak"): `sourcesU_zip_premisesU` zips the
   sources with `premisesU` into `sourced`, built segment by segment from the very lists `premisesU` reads.
3. **Citation exactness**: `mem_cited`, `cited_nodup`, `checkedCites_spec`, `answerFor_cites` (readings),
   `plainCites_spec` (plain), `zeroCites_spec` (zero-set), and the approved `render_cites_exact`.
4. **`NameReadsBack` uses `=` on `Json`**, which has no decidable equality (`Json.beq` is `partial`; an object's tree
   shape is not observable). The checked relation is `NameReadsBackSame` (canonical JSON text, the relation
   `UnitBound` already uses). `Asked.hnames` uses it. DRI signature needed.
5. **The answer frames' slots** (Q1's `VE.Question.Frames`): a `slot` takes any text, so an R1 line naming two
   sentences had two derivations and was refused. Spec 3.3 says slots are closed classes; a digits-only `num` piece
   now reads C1's, R1's and U1's numbers. A0 is unchanged. LOCK relocked, `question_version` unchanged.
6. **Lines from a route-independent `View`** (`VE.Ask.Lines`); the approved `render`, `renderGroup`, `lineText` are
   the readings answer's view (`Answer.view`), and the approved statements follow from the view-level lemmas.
7. **Unnamed readings**: Python sends `""` for a reading its slot cannot word; Lean refuses an answer that shows it
   (`unworded`, `CheckerUnavailable: VE could not check the wording of a reading of sentence n`).
8. **Splits**: one flip generator (`ve.ask._split_piece`) flips a countermodel at the gaps Lean's row names
   (`gaps`, RD-3's `gapsOf`); a second request asks for the split.
9. **Agent-policy evidence**: the generic prover cannot prove the policy's `permitted` conflict package (ResourceLimit
   at 10,000 and 100,000 steps, 162 s); the use case's focused prover proves it in 5.8 s. `ve ask --evidence FILE`
   takes recorded pieces; the agent fixtures' evidence is recorded by a fixture builder (untrusted).

## State

- Q2.1, Q2.2 (three routes), Q2.3 and Q2.5: done; all approved statements proved (`tools/question_statements.py --q2`).
- Tests, schema, relay binding, seeded bugs, report and DELTA: done (`docs/spec/question-answering-q2/`).
- Not done: Q2.4 (one owner of situation wording), Q2.6's evaluation, latency and W2 agreement (REPORT.md, "Not done").
- 2026-10-11: mutants rerun on the synced code (12, each caught); a gap's elements bound to the request's evidence
  models; relay gate rerun and saved; evidence recaptured. Next: the full gate once on the final HEAD.
- 2026-10-12: definition citations and exact choice-row coverage bound in the relay; two more seeded bugs caught.
  The selected run exposed two inventory omissions and an audit-test timeout; both inventories were fixed, and the
  audit test passed with a doubled `HANG_TIMEOUT`. The wire corpus passed when rerun serially beyond the selector's
  one-hour per-file cutoff. Next: the full gate on the committed HEAD, then save its result in the report.
