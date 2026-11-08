# sn-b6c REPORT (senses.read members for sn-b7's display)

Status: (1) byte spans, (2) seven of the eight 3.2 texts and (3) glosses are built; GlossedNatural is cut to sn-b6d
(DRI-signed), and so are (4) Lean's preamble line and (5) the re-read (cut at the size line, as the task orders).
HEAD: the commit that adds this report's last edit. Trust V +25, K +0 (R16). Open: sn-b6d. No DRI signature is reserved.
Decisions: reviews/dri-decisions-20261101-sn-b7b8.md item 2, reviews/dri-decisions-20261108-sn-b6c.md items 1-4.

## Deliverables

| Task deliverable | Delivered | Where | Tests |
|---|---|---|---|
| (1) (b) byte spans in the sense map, at `lexSpans` token boundaries | yes: `byte_start`/`byte_stop` (UTF-8, exclusive) on every entry of a source answer | `lean/VE/Senses/Run.lean` `byteSpan`, `senseEntryJson`; relay `_byte_spans_problem` | `tests/test_senses_read_members.py::test_each_span_is_the_bytes_of_its_words` (3 goldens), `::test_a_span_off_by_one_byte_is_refused` (7), `::test_spans_follow_their_tokens`, `::test_a_tampered_entry_through_the_route_is_unavailable`; `lean/VE/Senses/TextsExamples.lean` |
| (2) (c) the 3.2 texts on source requests | Unresolved (every open unit's `text`), CandidatesDiverge (one word), UnknownGloss, TooManyCandidates, NoSenseFits (`hint`, one unresolved word), Mixed and Unneeded (`warnings`). **GlossedNatural: sn-b6d** (DRI 20261108 item 2) | `lean/VE/Senses/Texts.lean`; `Run.lean` `textsJson`, `warningsJson`, `bodyOf` | `TextsExamples.lean` (every text, slot by slot); `tests/test_senses_route.py::test_every_refusal_carries_its_arguments[s4, a1-30-words, s17]`; `::test_the_texts_of_a_source_answer_are_leans`; `::test_text_rebinding_is_refused` (7); `::test_warning_rebinding_is_refused` (7) |
| (3) (e) the gloss of each used sense in the sense map | yes: `gloss` on every entry (source and fence answers) | `senseEntryJson` | the goldens above; `::test_a_tampered_entry_through_the_route_is_unavailable[gloss-*]` |
| (4) (f) Lean's text of `In this document, W means G.` | **no: sn-b6d** (size line) | built and tested in `3eae10692`, removed in `4a9a28083` | |
| (5) the re-read under a given Lean projection | **no: sn-b6d** (size line); DRI 20261108 item 3 already rules its DELTA (R3) and tests | built in `3eae10692` (`rereadJson`: `readOne` under the candidate's `linesProjection`, no policy, quoted senses refused) | |
| typed, bound, fuzzed | yes, in the relay (Deviation 1) | `ve/backends/senses.py` | `tests/test_senses_route.py::test_genuine_response_field_mutations_are_rejected` (GENUINE gains `warnings` and `hint` answers: every field dropped and retyped); the rebinding tests above |

Plan edit 1 (edits-senses.md: senses runs as `ve_senses_route`, no profile) is the one this item builds under.

## Deviations (all DRI-signed in reviews/dri-decisions-20261108-sn-b6c.md)

1. The members are typed and bound by the relay's validator, not a response shape (item 1, as sn-b6b's
   reviews/dri-decisions-20261102-sn-b6b.md item 1): `senses.read` is not a `ve_service` mode. The theorem-level tie
   is the open design row sn-read-shape.
2. NoSenseFits only for a sentence with exactly one unresolved word; Mixed writes "(sentence 3)" for one sentence;
   Unneeded has one line per word of `VE.Senses.unneeded` (item 2), each with a `#guard`.
3. The span binding is the relay's (item 4): in the source's body, on character boundaries, no white space or cut
   word at either edge, in the order of its tokens. A stretch onto a neighbouring punctuation token (`funny` to
   `funny.`) passes it; that form is caught by the golden test against Lean's spans (S2 below).
4. A fault's `text` is given on fence answers too, and the gloss on every answer: one rule for every route answer.
5. `hint` dropped from a genuine answer is accepted (the retype fuzz skips that one deletion): whether a sentence
   has one unresolved word is Lean's, and without the hint the answer is S2's `none`.

## Seeded bugs (docs/senses/sn-b6c/mutants.json)

| Id | Language, file | Bug | Caught by |
|---|---|---|---|
| S1 | Python, `ve/backends/senses.py` | a span off by one byte accepted by the relay | `test_a_span_off_by_one_byte_is_refused[start-1, start+1, stop-1, stop+1]` |
| S2 | Lean, `Run.lean` `byteSpan` | every span one byte long (onto `.`, or a space) | `test_each_span_is_the_bytes_of_its_words`: golden 0 by the relay (CheckerUnavailable), goldens 1, 2 by value |
| S3 | Lean, `Texts.lean` `divergeText` | a 3.2 text with a slot swapped | `test_every_refusal_carries_its_arguments[s17]`; `TextsExamples.lean:14`, `:18` |
| S4 | Python, `senses.py` | Mixed warnings not bound to `mixed` | `test_warning_rebinding_is_refused[mixed-dropped, mixed-word]` |
| S5 | Lean, `Run.lean` `senseEntryJson` | each entry given the first sense's gloss | `test_each_span_is_the_bytes_of_its_words` (3) |
| S6 | Lean, `Run.lean` `textsJson` | NoSenseFits for several unresolved words | `test_the_texts_of_a_source_answer_are_leans` |

The re-read's seeded bug (a base-projection rendering accepted) goes with (5) to sn-b6d. No Rust changed.

## Trust, mutants, size

- `uv run python tools/trust_map.py --check`: "PASS ... allowed V +25 over e9a6ec8d5938"; `VE/Senses/Run.lean`
  +25 (G[V] `byteSpan`, `senseEntryJson`, and the new arguments of `outcomeJson`, `readCase`). The texts are G[R].
  FOLLOW-UPS.md "## sn-b6c" asks for the ties pass and the span encoder theorem.
- Trust mutants: run 1 (`trust-mutants-run1.json`, cloud): 99 KILLED, 23 SURVIVOR, 16 UNKNOWN, 33 INVALID. The
  survivors were cuts of lists of at most one entry (allowed as equivalent, `trust-mutants-allow.json`) and cuts of
  S2's fields under front-matter defaults (a new `#guard` in `TextsExamples.lean`); the UNKNOWNs do not elaborate,
  but for the default `texts := false`, whose flip fails the document-mode pin through `readCase`. Final run
  (`trust-mutants.json`, VM, full: the rescore found its inputs changed), on `ed6fe6b6b`: 104 KILLED, 0 SURVIVOR,
  0 UNKNOWN, 33 INVALID, 34 ALLOWED, 0 NOT RUN.
- Statement gate: `uv run python tools/lean_statements.py --check`: added 0, removed 0, changed 0.
  `python3 lean/audit.py --write`: PASS (782 source files, the standard axioms only).
- Size (hand-written, `git diff --numstat` against the merge base, generated files and the trust-mutant evidence
  out): about 640 lines with these docs; (4) and (5) were cut when the projection with tests and docs was ~800.

## Tests run

- Selected tests once: `zsh mac-pytest.sh --select -- --base e9a6ec8d5 --run` (cloud, 4 shards): 461 of 463 units
  passed (2 units, 3 tests failed): my stale assurance tables and an unclassified JSON file
  (`tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`,
  `::test_spec_tables_are_generated_from_the_manifest`,
  `tests/test_regen_generated.py::test_assurance_doc_check_fails_on_a_stale_table`); fixed in `ed6fe6b6b`; rerun of the 3 ids
  (`zsh mac-pytest.sh -- <ids>`, ve-mac-1): 3 passed.
- `uv run python tools/relay_mutation_gate.py --route ve_senses_route::senses.read`: 649 mutants, 0 failures. Its
  two fixtures (`The riddle is funny.`) carry the glosses, spans and the open unit's text; the warnings, hint and
  fault texts are fuzzed by the pytest tests above (the recorder keeps two cases per answer shape).
- `uv run python tools/relay_lint.py`: PASS ("4 senses module(s), no English reader").
- Overlap: `infra/arch-20261105-2` re-pins the same `#guard` lines of `RunExamples.lean` (another pin function);
  whichever merges second re-pins them.

Pilot bytes: 0 expected (no pilot document uses senses yet). Main's known-red tests: none in this selection.

## Spec re-read

- Each text against docs/spec/senses.md 3.2 (lines 513-528) and senses-PLAN.md 2.8 (26da4c5ab, lines 400-410),
  word by word in `TextsExamples.lean`; `{i}` from 1 counting the preamble, as S2 shows it.
- Byte spans against plan B6 ("the sense map with byte spans from `lexSpans`") and the decision's item 4.
- The binding rules against DRI-RULINGS.md R3 and R8 and the decision's item 1 conditions (a)-(f).

## Next

sn-b6d: GlossedNatural; (f) Lean's line; the re-read (from `3eae10692`, with the base-projection test and the
golden byte-for-byte test of decision item 3). Then sn-b7b.

## Self-review against BUILDER-CHECKLIST

1. PASS: `test_genuine_response_field_mutations_are_rejected` (warnings, hint), `test_text_rebinding_is_refused`, relay mutation gate 0 failures.
2. PASS: deliverables table above; cuts by the task's size line and DRI 20261108 item 2; no Python text (relay_lint).
3. PASS: seeded bugs S1-S6, each with its failing test; trust mutants with allow reasons.
4. N.A.: no CPU-heavy path added (the texts re-read only a diverging prefix once per fault).
5. PASS: `test_spans_follow_their_tokens`, `test_a_span_off_by_one_byte_is_refused` (out of range, emptied).
6. N.A.: no verdict added; budget answers keep S2's texts (`test_text_rebinding_is_refused[hint-on-budget]`).
7. N.A.: no deadline path changed.
8. N.A.: no kind fold added.
9. N.A.: no rendering; the texts are Lean's.
10. N.A.: one entry (`senses.read` route); the document mode's call is unchanged (RunExamples pin, line 120).
11. PASS: no regex of a language; spans are Lean's `lexSpans` (`test_each_span_is_the_bytes_of_its_words`).
12. N.A.: no state machine.
13. PASS: no test removed: `uv run python tools/gate_collection.py --check --prebuilt`: 33 added, 0 removed, 0 refused, 0 stale, 0 malformed.
14. PASS: both directions (accepted goldens and refused shifts; text present and absent); spec re-read above.
15. PASS: no overclaim (deferred parts named as sn-b6d); no silent cut (task's cut order, DRI item 2); every new
    check has a mutant (S1-S6); limits: the texts read the request's own sentences once more, no new list.
