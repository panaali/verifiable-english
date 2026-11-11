# cmp-s3-cfr-1d: RC1-RC4 rendered by Lean through W7

No DRI signature is reserved in this item. Branch feature/cmp-s3-cfr-1d, base main 19013ac5f7 (cmp-s3-cfr-1b merged).
Plan: docs/spec/right-clauses.md 2 (RC1-RC5, the noun rules, RC1's fixed order, the reader's checklist), 9.3's English
line, 12 item 8; docs/spec/composition.md 2 (W7, W8), G6, G9 (13.20). Deliverables (3) and (5) moved to
cmp-s3-cfr-1db by the DRI (reviews/dri-decisions-20261111-cmp-s3-cfr-1d.md item 1); see "Moved".

## Deliverables

| Task row | Delivered by | Test or #guard |
|---|---|---|
| (1) lean/VE/RightClauses/English.lean: RC1-RC4 as registered frames of stage S3 (`rcFrames`, RC1 once per line kind, RC2 the relation instance, RC4's two forms), `readings`/`gated` in the form of lean/VE/Question/Frames.lean (exactly one derivation over every frame, and it is the frame's) | b6d5cca288 | EnglishExamples.lean #guards (each instance's exact bytes; `readings` length 1 on every rendered row; frames' leads pairwise not prefixes) |
| (1) each sentence built from the line, its relation instance, its guard and clauses in wire order; RC1's order relation, guard, clauses | b6d5cca288 | EnglishExamples.lean:45 (`rc1Line`: relation, then the guard `adult`, then the clause `charged`) |
| (1) noun rules: RC3 introduces the holder first; `the first`/`the second` when s_a = s_b | b6d5cca288 | EnglishExamples.lean:81 (RC3 with s_a = s_b and slot o before the holder slot); :57, :64 (distinct sorts, `that`) |
| (1) RC4's two forms and `bytes [<a>, <b>)` for "may not", a double quote, a G6 substring | b6d5cca288 | EnglishExamples.lean:90-98 (quotes; the three triggers; a split UTF-8 character; a span outside the source refused) |
| (1) the shown lines only through the gate, theorem `english_gated` in the form of `answerFor_gated` (the only new theorem) | b6d5cca288, 42865aea67 | `english_gated` (lean/VE/RightClauses/English.lean); seeded bug "line shown without the gate" breaks its proof |
| (2) EnglishExamples.lean fixtures: RC1-RC4 one instance each, RC3 also s_a = s_b with slot o first, RC4 "nothing" and a quoted span, the byte form for each trigger; G6/G9 #guards over every rendered sentence | b6d5cca288 | EnglishExamples.lean:123-130 (`rendered`: 18 rows, one derivation each, no `ve__`, `rd-`, `soft__`, `rights__`, `may not`) |
| (3) the document route prints Lean's RC lines under right-clauses@0 | not delivered, moved to cmp-s3-cfr-1db (reviews/dri-decisions-20261111-cmp-s3-cfr-1d.md item 1) | none here |
| (4) W8 for RC4: a quoted elided text is the source bytes of its span, byte-equal | 42865aea67 | tests/test_right_clauses.py::test_right_clauses_rc4_w8_quotes_are_source_bytes (fails on the seeded non-source quote) |
| (5) test_right_clauses_rc_product_route | not delivered, moved to cmp-s3-cfr-1db (same decision; it must fail first on main after cmp-s3-cfr-1c) | none here |
| (6) K10's profile-off identity unchanged | no edit to those tests or their evidence | test_right_clauses_k10_profile_off, test_right_clauses_profile_off_evidence, test_right_clauses_environment_texts_kept (pass: `pytest tests/test_right_clauses.py -k "rc4 or k10 or profile_off or environment_texts or differential or binds_every"`, 6 passed) |
| (7) `clauseSlot_wellFormed` | N.A.: cmp-s3-cfr-1b delivered it (its REPORT, row (3)) | — |
| The mode's typed `english` field and its binding (DRI item 1: "the typed and bound `english` result field of clauses-elaborate with its relay binding and fuzz tests") | 16a38fddcc, 42865aea67, 6be15586b6, fbd608fab4 | ResponseShape `elaborateCase_fits` (the schema's `english` rows: frame, rule, text); test_right_clauses_rc_lean_rows; test_right_clauses_rc_rows_retyped_and_rebound (every field retyped to null, 1, [], "": schema refuses; a row dropped, repeated, added, reordered, moved to another rule or frame, shown unasked or missing: `bind` refuses); relay_mutation_gate --route service:clauses-elaborate: "5 fixtures, 1213 mutants, 1213 refused, 0 allowed" |
| Evaluators (10-27 rule): rendering reads each line once and is charged against a stated limit; a large fixture ends within it, one over it is a deterministic ResourceLimit | 42865aea67 | test_right_clauses_rc_many_lines_within_limits (16 structured lines, 48 rows, about 60 KB shown; 16 x 4,000 bytes and one 70,000-byte span: `ResourceLimit: the shown lines exceed 65536 bytes`) |

The relay sends `english: {source, lexicon}` only when the caller passes the pinned source (`elaborate(environment,
document, source)`); the lexicon is the vocabulary export (`ve.backends.english_lean.export`) of the rights lines' soft
environment, the words `ve.surface.rights` renders with, and Lean refuses one that names another environment
(`VE.EnglishGrammar.Run.decodeLexicon`; probe: Lean's id of the stripped environment is Python's,
`c2df98329ca3...`). Python builds no sentence: `_english_bound` checks which (frame, rule) rows appear, in which order,
and relays each text as Lean wrote it (R8).

## Moved

Deliverables (3) and (5) and the task's DELTA row "under right-clauses@0 the route now prints the RC1-RC4 sentences"
moved to cmp-s3-cfr-1db, blocked by cmp-s3-cfr-1c (reviews/dri-decisions-20261111-cmp-s3-cfr-1d.md item 1, under R9).
Reason: on main every right-clauses@0 document is refused before an RC line could print (`ve document render` on a
rights document with the profile: `UnsupportedProfile: Unsupported profile right-clauses@0`, from Lean's rights mode
through ve/document/load.py:214 and ve/rights.py:150); handing the plained document to the next head (spec 4.1 step 6)
is cmp-s3-cfr-1c's deliverable (6). cmp-s3-cfr-1db adds the route display and test_right_clauses_rc_product_route on
top of it, relaying this item's `english` rows.

## Seeded bugs (each planted alone, restored; mutants.json)

Line numbers are those of tree 42865aea67, before EnglishExamples.lean gained its `import VE.RightClauses.Run` line (add one
for HEAD).

| Behaviour | File | Mutant | Fails |
|---|---|---|---|
| RC1's order | lean/VE/RightClauses/English.lean `rc1` | guard before the relation | EnglishExamples.lean:44 |
| RC2's argument order | English.lean `relInstance` | slots swapped | EnglishExamples.lean:44, :50, :56, :63, :80 |
| RC3's nouns for s_a = s_b | English.lean `rc3` | `that person ... that person` | EnglishExamples.lean:80 |
| G9 on quoted text | English.lean `rc4` | a span with "may not" quoted | EnglishExamples.lean:92, :122 |
| W8: quotes are source bytes | English.lean `rc4` | one byte short | test_right_clauses_rc4_w8_quotes_are_source_bytes, test_right_clauses_rc_lean_rows |
| Lines only through the gate | English.lean `english` | gate check replaced by `true` | `english_gated` no longer elaborates |
| No Python wording (R8) | ve/right_clauses.py `_english_bound` | RC4 built by Python from the request's spans | test_right_clauses_rc_lean_rows |
| Binding | ve/right_clauses.py `_english_bound` | a suffix of the rows accepted | test_right_clauses_rc_rows_retyped_and_rebound |

## Trust (R16)

`uv run python tools/trust_map.py --check` on HEAD: "against 19013ac5f725: K +0, S +0, D +0, G +62, tied +0,
unclassified +0, trusted +29" (VE/RightClauses/Run.lean +22: `englishJson`, `englishOf`, `elaborateCase`'s `english`
branch; VE/RightClauses/English.lean +7: `Row`), "PASS: K, S and untied [V] within 19013ac5f725 and the allowances
introduced since". Recorded in docs/trust-baseline.json as V +29, "SIGNED by standing ruling R16 (DRI-RULINGS.md),
cmp-s3-cfr-1d, 2026-11-11". Classes follow the precedent the task names: the renderer and `english` are C (like
`VE.Ask.renderV`, `answerFor`, `linesGated`: their output is checked by the gate), the frames, `readings`, `gated` and
`shown` are G[R] (like `VE.Question.answerFrames`/`gated`), the row type `Row` is G[V] (like `VE.Ask.Line`). FOLLOW-UPS.md
row `## cmp-s3-cfr-1d` asks for the ties pass.

Trust mutants: `zsh mac-pytest.sh --trustmut -- --test lean/VE/RightClauses/EnglishExamples.lean --test
lean/VE/RightClauses/RunExamples.lean --allow docs/composition/cmp-s3-cfr-1d/trust-mutants-allow.json --rescore <prev>
--json docs/composition/cmp-s3-cfr-1d/trust-mutants.json` exited 0: "45 KILLED, 0 SURVIVOR, 0 UNKNOWN, 5 INVALID, 3
ALLOWED, 0 NOT RUN" (`elaborateCase` 30 killed, `englishJson` 10, `englishOf` 5). The first run (EnglishExamples only)
left the result's other fields unguarded in the `english` branch; the #guard comparing the result with and without
`english` now kills them. Allowed: `englishJson` `list-empty` (does not elaborate) and `elaborateCase` 257 ± 1 (main's
canonical-JSON fuel, unchanged; a plained document passed the rights decoder, whose formula depth limit keeps its JSON
depth far below 256, so the three values answer alike).

## Size

SIZE: 347 product (English.lean 236, Run.lean 34, ve/right_clauses.py 61, the schema source 12, the encoder proof 2, VE.lean
2), 312 tests (EnglishExamples.lean 165, tests/test_right_clauses.py 146, one relay-gate case), about 330 other
hand-written lines (these docs, mutants.json, the allow file, trust-classes.json 47, relay_mutation_gate.py 5, the trust
allowance 7). Measured with `git diff --numstat $(git merge-base HEAD main) HEAD`; generated files (inventories, code
map, census, schema JSON, checkers.lock) and trust-mutants.json excluded.

## Overlaps

feature/cmp-s3-cfr-1c (started at the same main commit) edits ve/right_clauses.py, tests/test_right_clauses.py and
lean/VE/RightClauses/Run.lean. This item's lines sit in their own section at the end of the test file, in `bind`'s tail
and in `elaborateCase`'s result; the merge is a union.

## Pilot bytes

None expected: no route shows the RC lines until cmp-s3-cfr-1db. Nothing is claimed before a pilot audit.

## Next items

cmp-s3-cfr-1db (route display and test_right_clauses_rc_product_route, after cmp-s3-cfr-1c); l1-c-regrade-rights-b waits
on it (DRI item 1).

## Notes for the DRI

- Files: the mode's answer is written in lean/VE/RightClauses/Run.lean (`elaborateCase`), not Wire.lean as the task's file
  list says; the `english` field is there, with `englishOf`/`englishJson`. The response shape
  (lean/ResponseShape/Schemas/ClausesElaborate.lean) and its encoder proof gained the field; tools/relay_mutation_gate.py
  reads it (one recorded RC3 case added to tests/data/relay-gate-cases.jsonl).
- Nouns for s_a = s_b in RC1/RC2: the line's own names (`the first person` ... `the second person`), as rights 2.1's guard
  renderer names a repeated sort (`_bindings`, `VE.EnglishGrammar.Norm.bindings`); the spec's parenthetical ("that person"
  ... "the second person", fixture μ) quotes μ's illustrative text. RC3 uses `the first`/`the second` as spec 2 states.
- RC3's holder guard follows the table literally: `For every person that <H> there is ...`, so a guard renders as
  `that that person is adult` (the core renderer has no relative-clause contraction).
- RC3 is shown for every total relation: on the clauses head every result uses the slot `Lim ++ Rel_D`; showing it under
  each result (inside E3) is the route's (cmp-s3-cfr-1db).
- Conditions are rendered by the core renderer (`VE.English.renderTree`, D[V]) in the line's scope; for a compound
  condition its text can differ from Python's rights display, which contracts relative clauses.
- Conservative choices: a rendered line holding a G6 or G9 substring (for example a wording with `third-party`, which holds
  `rd-`) refuses the answer instead of showing it; a span cutting a UTF-8 character takes the byte form; a span past the
  source refuses.
- The gate (`VE.Question.pieceReadings`) reads a line in time quadratic in its length (one 60,000-byte span took 3.1 s on
  a probe), so the shown lines are charged together against `VE.Limits.maxSourceBytes` (65,536) before any is gated. The
  limit is the existing source limit; the text `ResourceLimit: the shown lines exceed 65536 bytes` is new and reachable
  only with the new request field.

## Spec re-read

- RC1 `<line sentence>[, where <relation instance>][, if C[ and <clause>]*][, unless U].` against
  docs/spec/right-clauses.md:130 and the order sentence after the table: `rc1` (relation, guard unless ⊤, clauses with
  ` and `, then the carve-outs as rights 2.1 words them: one as `, unless U`, more as ` Except when U.` sentences).
- RC2 `that <noun a> <phrase> that <noun b>` in pred's argument order against :131 and the slots paragraph: `relInstance`.
- RC3 `For every <holder>[ that H] there is at least one <noun of slot o> such that <relation instance>.` against :132
  and "in RC3, which introduces the holder first ...": `rc3`.
- RC4's two forms and the byte form for "may not", `"` and the G6 substrings against :133: `rc4`.
- Reader's checklist (RC1 every structured line, RC3 for a total relation, RC4 every line) against right-clauses.md's
  "Reader's checklist": `lineRows`.
- W7 (each template registered with its stage, all-derivations gate before shown) against composition.md:204; G6 against
  composition.md:1283; G9 (no exception for quoted text) against :1286 and 13.20.

## Self-review against BUILDER-CHECKLIST

1. PASS: test_right_clauses_rc_rows_retyped_and_rebound (each `english` field retyped: schema refuses); relay_mutation_gate
   --route service:clauses-elaborate (1213 refused, 0 allowed).
2. PASS: Deliverables table; (3) and (5) moved by reviews/dri-decisions-20261111-cmp-s3-cfr-1d.md item 1; no Python
   sentence (seeded bug "relay builds RC4 in Python").
3. PASS: mutants.json (8 seeded bugs, Lean and Python); trust-mutants.json exit 0.
4. PASS: test_right_clauses_differential and the K fixtures unchanged; the profile-off tests pass.
5. PASS: test_right_clauses_rc_rows_retyped_and_rebound (rule `other`, frame `RC2`, row dropped, repeated, reordered,
   added, unasked, missing).
6. PASS: the chain gates the committed final HEAD; the selected run is on committed code (below).
7. PASS: DELTA.md rows cite the DRI's 2026-10-31 item 2 (named for this case by reviews/dri-decisions-20261111-cmp-s3-cfr-1d.md
   item 1) and R16.
8. PASS: DELTA.md (the mode's new field and refusals; profile-off answers unchanged).
9. PASS: `tools/select_tests.py --base $(git merge-base HEAD main)`: 519/597 units, tests/test_right_clauses.py among them.
10. PASS: `english_gated` is about `english`'s returned rows; seeded bug "line shown without the gate" breaks its proof.
11. PASS: test_right_clauses_rc_many_lines_within_limits (over the limit: deterministic ResourceLimit before the gate).
12. PASS: the base path is unchanged without `english` (no extra work); with it, the charge bounds the gate's work.
13. N.A.: no test removed or renamed (`tools/gate_collection.py --check --prebuilt`: "5 added, 0 removed ... 0 refused, 0
    stale and 0 malformed").
14. PASS: opposite directions: quotes accepted and each trigger in byte form; accepted lexicon and refused one; within
    and over the limit; the result with and without `english`. Spec re-read above.
15. PASS: no overclaim (moved items written as moved); no silent cut (DRI ruling before the cut); every new check has a
    seeded bug; the shown bytes are charged before the gate (test_right_clauses_rc_many_lines_within_limits).
