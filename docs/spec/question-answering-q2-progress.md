# Question answering Q2: builder's progress notes (working file)

Branch `question-answering/q2`, base `main` at `f0547468`. This file records decisions and state so the batch can be
resumed; the final report is `docs/spec/question-answering-q2-report.md`.

## Decisions

1. **Three routes for `ask`, chosen by Lean from the document's profiles.**
   - *readings* (`readings@1` with `norm-defaults@0` on the norms chain, a content-bearing set): RD-3's
     `replayVerdictsND` on the request's `case`, the approved `Asked` / `ask_wire_sound` of spec 5.2. UDHR part 7.
   - *plain* (`relational-fol@0` without norms; R13): the approved `PlainAsked` / `plain_ask_wire_sound`. G document.
   - *norm-defaults, no reading set* (the agent-policy documents: `norms@0` + `norm-defaults@0`, no `readings@1`).
     Plan 4.7 says Q2.2 "extends [RD-3's] admission to zero sets". Measured on `a-unspecified.ve.md`: RD-3's admission
     with `readings@1` inserted passes `admitS2` but takes **73 s** of Lean per replay (three runs: 68, 74, 73 s),
     and the document is refused as not enumerated. The norm-defaults route elaborates the same policy in 0.2 s. So
     the zero-set case is a third adapter on the norm-defaults route's own checkers (`acceptanceU`, `modelCheckU`,
     `conflictFreeCheckU`), one row with choice `[]`, whose claims are RD-3's per-choice claims on the document's
     own `UDoc`. Its statements are new and need DRI review (they are not in spec 5.2).
2. **Segment order of sources** (task: "sourcesU_length alone is too weak"): `sourcesU_zip_premisesU` zips the
   sources with `premisesU` into `sourced`, built segment by segment from the very lists `premisesU` reads.
3. **Citation exactness**: `mem_cited` (a source is cited iff a used position has it) and `cited_nodup`, plus the
   approved `render_cites_exact` (Q2.3).

## State

- Q2.1 Lean core: done (`bbbe98a4`): `VE/Ask/{Basic,Sound,Sources,Groups,Plain}.lean`, every 5.2 core statement
  proved as written.
- Q2.2 wire: in progress.
