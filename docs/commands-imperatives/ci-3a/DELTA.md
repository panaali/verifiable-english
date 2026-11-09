# ci-3a delta: the step reader, no route caller

No CLI, document, service or conformance verdict or text changes: nothing on main calls `readStep` (ci-3 wires it).
The one row below is a change to approved spec text, which the DRI signed.

| # | Change | Evidence | Ruling |
|---|---|---|---|
| 1 | Changed approved statements. `readStep` charges `maxWordingBytes` first (`if maxWordingBytes < (trimmed s).utf8ByteSize then .limit else` section 7's body). The hypothesis `hb : (trimmed s).utf8ByteSize ≤ maxWordingBytes` is added to `after_eq`, `seq_eq` and `shapes_ambiguous`; no other statement changes. | `lean/VE/Commands/StepsExamples.lean`: the 6 KB "If a, a, …, click Ask." guard is `limit`; the two-step wording over 400 bytes is `limit`, though each step reads alone (`step ("Click Check rule conflict, then" ++ padded ++ ".")`). The mutant "the byte test dropped" in `mutants.json` fails that guard (line 154). | SIGNED by the DRI 2026-11-09 (reviews/dri-decisions-20261109-ci-3a-wording.md item 1) |
