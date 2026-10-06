# Senses, Lean work item: build report

Branch `senses/lean` (worktree `ve-senses-lean`), on `0599bd1f` (spec draft 2, corrections round 2), against the
merged S2 build. Specification: [senses.md](senses.md) (the statements of 5.3 are the approved text); plan:
[senses-PLAN.md](senses-PLAN.md). Nothing was pushed. No model was called.

## 1. What was built

New files only, in `lean/VE/Senses/` (namespace `VE.Senses`, layer 3 in `tools/layer_policy.py`). No frozen file
changed except the generated records that list new modules (`VE/Audit.lean`, `VE/Route/frozen-sources.sha256`,
`lean/VE.lean`); `Norms`, `SoftNorms`, `Route` and `EnglishGrammar` are untouched.

| Module | Batch | Content |
|---|---|---|
| `Dictionary.lean` | B1 | `Sense`, `PackSort`, `Pack`, `Dictionary`; `reservedWords`, `schemaReserved`, `maxFormChars`, `maxNameChars`; the forms of 2.3 by parts; `Dictionary.failures` (W1 to W7, the details of 4.2), `wf` |
| `Assignment.lean` | B4 | `Assignment`, `wf`, `extend`, `defaultOf`, `lines`, `unneeded` |
| `Preamble.lean` | B4 | `preambleShaped`, `preambleGrammar`, the line faults of 2.4, `readPreamble`; `Divergence` and `SenseFault` |
| `Project.lean` | B3 | `usedWords`, `Projection`, `wordOf`, `maxSorts`, `maxPredicates`, the six steps of `project` (2.5), `clashes`, the projected environment, lexicon and JSON, `docKeys`, `dictKeys` |
| `Read.lean` | B5 | `Candidate`, `SenseUnit`, `SenseOccurrence`, `SensesOutcome`, `readWithSenses` (2.6, on S2's grammar as merged), the switch rule (R7), `quotedSense` (R13), the sense map, `mixedOf`, `SenseFault.code` and `SensesOutcome.statusCode` (4.1), and the proofs |
| `Decode.lean` | B2, Lean half | the `ve.sense-pack@1` decoder over `VE.JsonInput`, the encoder, `dictionaryId` (domain `ve-senses-dictionary-v1`) |
| `Fixtures.lean`, `Examples.lean` | B1 to B5 | the fixtures of section 8 as 185 `#guard` checks |

Deviations from 5.1 and 5.2, none in a statement: `SenseFault` and `Divergence` live in `Preamble.lean` (the
preamble's faults need them); a fixtures module beside `Examples.lean`; helper definitions the spec does not
name (`partsOf`, the per-condition `w1Failures` to `w7Failures`, `clashingForm`, `projectionOf`, `preCheck`,
`pairFault`, `readOne`, `tryChoice`, `candidatesOf`, `openUnit`, `readUnit`, `readBody`, `Stop`, the tree walks);
`EFormula.predNames` counts the relation of `reachNamed` as a predicate name (no accepted formula has a sense
there, by `quotedSense`); `dictionaryId` returns `""` on a digest error that cannot occur (the canonical JSON
has no null, no fraction, depth five).

## 2. The statements of 5.3

Every statement is in Lean with exactly the approved text (`tests/test_senses_lean.py::test_statement_equals_the_approved_text`).

| Statement | Status | Note |
|---|---|---|
| `wf_iff_no_failure` | proved | |
| `preamble_unique` | proved | through `readPreambleGo_lines` |
| `project_valid` | proved | `project` returns `ok` only on an empty `Lexicon.failures` |
| `project_extends` | proved | the fallback "stated only" of 5.4 was not needed |
| `senses_resolved_one_reading` | proved | |
| `senses_unit_sound` | proved | |
| `senses_candidate_sound` | proved | |
| `candidates_complete` | proved | |
| `mixed_exact` | proved | |
| `glossed_negative` | **deferred**, a `def … : Prop` | S2's `negativeTemplate` reads the prefix with `String.startsWith`, which is `Substring` equality over byte positions; Lean 4.24 has no lemma for it, so the "string lemma" of 5.4 needs a byte-level library first. Checked by d25 on seven senses |
| `lines_read` | **deferred**, a `def … : Prop` | its proof reads `lex` on the rendered lines (the lexer's spacing and sentence split); 5.4's fallback (one line first) needs the same lexer facts. Checked by a10 and a11 |
| `project_total` | **deferred**, a `def … : Prop` | proposed (Q13); 5.4 allows the deferral with the DRI's signature; the per-request check of `project` stays the guarantee |
| `senseMap_ids` | **deferred**, a `def … : Prop` | 5.4: "stated only"; its proof needs the action semantics of every lexical row. Checked by s1 (as merged: the m1 row), s9, s15, n4; s23 for the exclusion |

The nine proved statements and their 21 helper lemmas are in `lean/VE/Audit.lean` and `lean/axioms.txt` with the
standard axioms only (`propext`, `Classical.choice`, `Quot.sound`); `tests/test_senses_lean.py` checks both, and that
no deferred name is in the audit record. The four deferrals need the DRI's signature (plan 7.1, G-S1).

## 3. Fixtures (section 8), against the computed and hand-derived rows

Every row of 8.1, 8.3, 8.4, the *as merged* column of 8.5, 8.6, the *as merged* rows of 8.7 and 8.8 holds on the
built definitions (`VE/Senses/Examples.lean`, checked by `lake build`). No difference from the specification was
found, so no row was changed. In particular the rows draft 2 marked *hand-derived* or *computed by a reviewer*
hold as written: d2, d26, d27 (every case one failure), j6, j13, j15 (`collision "predicate" "sense__near_1"
"sense__near_2"`), j16 (32 sorts: `limit "sorts"`; 31: valid), j17, c16 and c17 (0 as merged), s22 (one open unit
over `[odd]`, one candidate), s23 (`quotedSense 2 near`). Added beyond section 8: step 4 of `project` (a fresh sort
named as a document constant), the 256-predicate cap at and past it, m1 *as merged* (both `funny` senses in
resolved formulas), the decoder and identity checks of 8.2's Lean half, the status of every outcome kind (4.1).

The *with R3* column of 8.5 was recomputed outside the repository with the narrowed simulation of R8 (twins only
for rows of `clauseRows`, after the cut): 36 twin rules on the 194 of j1's projection with `odd`, well-formed and
terminator-free; c1 to c17 give exactly the specification's *with R3* column, c16 included (2 derivations). So Q4's
rule drops the comma forms if R3 ships. The rows that need R3 (s1 and s2 *with R3*, s13, m1, m2) are not in the
build: the reader is S2's grammar as merged until the DRI decides R3.

## 4. Not done

| Item | Tag | Owner, reason |
|---|---|---|
| R3 and Q4 | HUMAN | the DRI (spec 6.2, 11): B5 formally waits for this decision; this build is the *as merged* column |
| the four deferred proofs | HUMAN | DRI signature per deferral (G-S1) |
| G-S0's bounded re-review of draft 2 | EXTERNAL | the statement reviewers; this build supplies the recomputed rows (section 3) and the re-elaboration of the three changed statements (they elaborate exactly) |
| `flipModel` | AGENT, later | B5 lists it through `VE.Eval`; not built. The flip valuations of s2 and n7 were not recomputed |
| the texts of 3.2 and 4.2's sentences around `detail`; `noSenseFitsText`; `glossedNaturalRewrite` | AGENT, B6 | the service relays Lean's texts; `CandidatesDiverge`'s text needs `{gloss₁}` and `{gloss₂}`, which the fault of 5.2 does not carry (a finding for the spec, section 6) |
| `sensesVersion`, `ve/senses/LOCK.json`, the service modes, the request decoder | AGENT, B6 | after the merged S2.4 build |
| the trust baseline | HUMAN | `tools/trust_map.py --check` reports the new trusted lines (940 in `VE/Senses`: Dictionary 352, Read 275, Project 155, Preamble 84, Decode 43, Assignment 31); growth needs a signed baseline entry. The check is not part of the gate |

## 5. Seeded bugs

Each mutant was applied to code of this item, the named check was run, and the mutant was reverted (the worktree
was clean afterwards).

| Mutant | Check | Result |
|---|---|---|
| M1: W6 compares two bare forms of one word (`clashingForm`) | `lake build VE.Senses.Examples` | 91 `#guard` failures, first d1 |
| M2: a switched occurrence counts as unswitched (`unswitchedIn`) | `lake build VE.Senses.Examples` | 5 failures, first s22's `unresolvedIn` guard |
| M3: no sense is a default in the projection (`isDefaultIn`) | `lake build VE.Senses.Examples` | 35 failures, first j1 |
| M4: the decoder reads `true` as the index 1 (`natOf`) | `lake build VE.Senses.Examples` | 2 failures, the field-type mutants |
| M5: `reservedWords` loses `document` | `pytest tests/test_senses_lean.py` | `test_reserved_words_are_python_reserved_and_the_three_of_d13` fails |

## 6. Findings for the specification

1. **Letters of the fixture pack across branches.** Section 8 gives `principal` the letter `R` and `resource`
   `Q`; the Python half (`ve/senses/packs/fixtures@1.json` on `senses/py`) gives `A` and `R`. The Lean fixtures
   follow section 8. One of the two must change before B6 sends that file to Lean.
2. **`CandidatesDiverge`'s text** (3.2) names two glosses, but `candidatesDiverge (sentence) (words) (why)` carries
   neither; B6 must recompute them or the fault must carry the two choices.
3. **W2's "not a word of the dictionary"** is read for the whole gloss (`deployed`, d4), not for each of its
   parts; and a gloss equal to its own word gives only the "word itself" failure (d3).
4. **The order within a row** of `failures` is by condition as written, then by sense or sort; a sort that fails two
   conditions of W4 gets two failures.
5. **`quotedSense` for a choice** is checked only when the choice would be a candidate (it reads and types), as
   2.6 says; the B0 stub checked it before the type.

## 7. Build checklist (`manage-agents/prompts/build-checklist.txt`)

| # | Status | Evidence |
|---|---|---|
| 1 | done for this item | codes are one exhaustive Lean match (`SenseFault.code`, `statusCode`); `reservedWords`, `schemaReserved` and the limits are read from compiled Lean and compared with Python's (`test_reserved_words_…`, `test_schema_names_…`, `test_limits_…`); texts are B6 |
| 2 | not applicable | no Python or Rust senses decision exists to compare |
| 3 | done | no-break space, double space, tab, CR, curly quotes, the Kelvin sign, a dotted capital I and a control character through `readWithSenses` (Examples, "Budget zero and the spellings of a text"); the text is normalised only by S2's lexer |
| 4 | not applicable | no Lean or Rust response is consumed |
| 5 | done | the pack decoder with every field removed, replaced by null, 7, `true`, `[]`, `{}`, a string; an unknown field; a fraction, a Boolean and a string index; 10,000-deep nesting; empty and scalar texts (Examples 8.2) |
| 6 | done | budget 0 on the preamble and the body (`preambleBudget 0`, `stopped 0 budget`); budget, ambiguity and rejection stop, never drop a choice; no candidate is `stopped noDerivation`, one candidate stays open |
| 7 | done, with a limit | the budget is S2's per sentence; one sentence costs at most `1 + candidateCap` parses, each bounded, and the cap is checked by `choiceCount`, linear in the words (fix round: the first build compared the length of the built choices, exponential in the words, Astra A1; the thirty-word row of `Examples.lean` guards it); there is no whole-operation deadline in Lean (the service adds it, B6) |
| 8 | done | `SenseFault.code` and `statusCode` are exhaustive matches; every constructor of `SensesOutcome` and of `SenseFault` is produced by a fixture (`limit` through `project`, j16); nesting depth does not apply (flat kinds) |
| 9 | done for this item | `Assignment.lines` read back (a10, a11); S2's `checkRendering` under the projection (s8); the English of the texts is B6 |
| 10 | not applicable | one entry point, `readWithSenses`; the service paths are B6 |
| 11 | done, one precedent kept | values come from the compiled Lean (the probe in `tests/test_senses_lean.py`); the statement comparison reads the theorem header from the source as `tests/test_english_lean_s2.py` does |
| 12 | not applicable | no state machine or ledger |
| 13 | done | section 5; the statement test has its own weakened-statement mutants |
| 14 | done | the test writes only under `tmp_path`, waits `HANG_TIMEOUT`, reads no cache |
| 15 | done | every field of the canonical pack form changes `dictionaryId`; whitespace and key order do not (Examples 8.2) |
| 16 | done | the audit enforces every theorem in `VE/Audit.lean`; the frozen inventory, gate collection, trust table and statement dumps were regenerated by their tools |
| 17 | done | `tests/test_senses_lean.py` diffs each Lean statement against the approved text; no theorem statement changed |
| 18 | done | every fixture is computed by the build; 8.10's two directions are guards |
| 19 | not applicable | no use-case formalisation |
| 20 | done for this report | each number here names its command or test; no gate JSON is quoted |
| 21 | done | section 4 tags every open item |
| 22 | see section 8 | |

## 8. Verification

- `lake build` (all default targets): passes; `python3 lean/audit.py`: PASS, 408 source files, standard axioms only.
- `python3 tools/lean_statements.py --check`: PASS (additions only, recorded in the commits).
- `tools/check_lean_imports.py`: the Lean layer graph is kept.
- The full pytest suite, in three file chunks with prebuilt binaries: 5,361 + 2,942 + 2,605 passed, 7 skipped
  (optional corpora and tokenizers); one failure in the first chunk, `test_committed_trust_table_covers_every_declaration`,
  fixed by commit "senses: trust classes" (that file then passed, 283 tests). The four long tests that the chunks
  deselect passed alone (28 cases). The gate result on HEAD is not recorded here: the integration branch's report
  ([senses-integration-report.md](senses-integration-report.md)) carries the later runs.
