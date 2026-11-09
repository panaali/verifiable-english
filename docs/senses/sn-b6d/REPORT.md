# sn-b6d REPORT (senses.read: the re-read of a rendering and Lean's line, for sn-b7b)

Status: (1) the re-read and (2) Lean's line are built; (3) `GlossedNatural` is cut whole to sn-b6e at the size line
before it, as the task orders (sn-b7b does not need it). No DRI signature is reserved. Trust V +41, K +0 (R16).
Decisions: reviews/dri-decisions-20261108-sn-b6c.md items 1-3 (in /home/seyran/code/manage-agents),
reviews/dri-decisions-20261102-sn-b6b.md item 1, reviews/dri-decisions-20261101-sn-b7b8-reread.md item 1.

## Deliverables

| Task deliverable | Delivered | Where | Tests |
|---|---|---|---|
| (1) the re-read: optional source-request member `reread` `{sentence, candidate, rendering}`, read by `readOne` under the candidate's `linesProjection`, no policy, quoted senses refused; `same` / `different` / `unknown` (budget) | yes, from `3eae10692`; one change: a rendering that does not lex to exactly one sentence is Lean's `InvalidInput` (it was `different`) | `lean/VE/Senses/Run.lean` `rereadJson`, `readCase`; relay `_reread_problem` | `tests/test_senses_read_members.py::test_each_candidate_rereads_under_its_own_projection` (7), `::test_a_base_projection_rendering_is_refused`, `::test_the_reread_is_unknown_when_its_budget_ends`, `::test_a_golden_request_without_the_members_keeps_its_answer` (9), `::test_the_members_only_add_to_the_answer`, `::test_a_rendering_that_is_not_one_sentence_is_refused_by_lean`, `::test_a_long_rendering_ends_within_its_limits`, `::test_a_refused_reading_has_no_reread`, `::test_reread_rebinding_is_refused` (6), `::test_an_unasked_reread_is_refused`; `#guard`s `lean/VE/Senses/TextsExamples.lean:91-95` |
| (2) Lean's line `In this document, <word> means <gloss>.` for a requested word and gloss | yes, from `3eae10692`: result member `line` `{word, gloss, text}` (`lineOf`, the one owner of the line, `Assignment.lean`), or `{word, gloss, code}` with `UnknownWord` / `UnknownGloss` | `Run.lean` `lineJson`; relay `_line_problem` | `#guard` per slot `TextsExamples.lean:77-81`; `::test_the_line_is_leans`, `::test_line_rebinding_is_refused` (6), `::test_a_line_is_there_exactly_when_asked` (2) |
| (3) `GlossedNatural` (detection, rewrite, re-read, text) | **no: sn-b6e** (size line, below) | | |
| typed, bound, fuzzed | yes, in the relay (Deviation 1) | `ve/backends/senses.py` | `tests/test_senses_route.py::test_genuine_response_field_mutations_are_rejected[reread, line]` (every field dropped and retyped); the rebinding tests above; `tools/relay_mutation_gate.py --route ve_senses_route::senses.read` (two asked fixtures) |

## Deviations

1. Typing stays on `ve_senses_route`: the members are typed and bound by the relay's validator
   (`_response_problem`, `_reread_problem`, `_line_problem`), not a response shape, as reviews/dri-decisions-20261108-sn-b6c.md
   item 1 rules after the sn-b6b precedent (reviews/dri-decisions-20261102-sn-b6b.md item 1). The theorem-level tie
   is the open design row sn-read-shape.
2. "The rendering is one sentence" is Lean's check, not the relay's: Python has no English reader (relay_lint), so
   `rereadJson` refuses a rendering that does not lex to exactly one sentence (`InvalidInput`), including one over
   S2's lexer length limit. The relay binds the unit and candidate (the request's, and one of the answer's).
3. The relay refuses a candidate whose `lines` is empty (a candidate resolves at least one word, so Lean always writes
   a line). Found by the relay mutation gate on the new asked fixture; a pre-existing gap of the candidate's typing.
4. `tools/relay_mutation_gate.py`: an answer's shape also names the case's asked members (`ASKED_MEMBERS`), so the
   recorder keeps a `line` and a `reread` case of `senses.read`. No recorded case of another route has those keys.
   The two cases were recorded from `tests/test_senses_route.py` alone and added to `tests/data/relay-gate-cases.jsonl`
   (a full `--record` rewrites every route's cases).

## Seeded bugs (docs/senses/sn-b6d/mutants.json)

| Id | Language, file | Bug | Caught by |
|---|---|---|---|
| L1 | Lean, `Run.lean` `rereadJson` | the rendering re-read under the base projection (no candidate lines) | `::test_a_base_projection_rendering_is_refused`; `#guard`s `TextsExamples.lean:91, 92, 95` |
| L2 | Lean, `Run.lean` `readCase` | the re-read member written on unasked answers | `::test_a_golden_request_without_the_members_keeps_its_answer` (9 of 9) |
| L3 | Lean, `Run.lean` `lineJson` | the line with word and gloss swapped | `#guard`s `TextsExamples.lean:77-79`; `::test_the_line_is_leans` |
| P1 | Python, `senses.py` `_reread_problem` | a re-read of another candidate accepted | `::test_reread_rebinding_is_refused[candidate-other]` |
| P2 | Python, `senses.py` `_line_problem` | a line for another word or gloss accepted | `::test_line_rebinding_is_refused[word-swapped, gloss]` |
| P3 | Python, `senses.py` `_response_problem` | a candidate's emptied lines accepted | `::test_a_candidate_with_its_lines_emptied_is_refused` |

The task's fourth seeded bug (`GlossedNatural` for a rewrite with two derivations) goes with (3) to sn-b6e. No Rust
changed.

## Trust, mutants, size

- `uv run python tools/trust_map.py --check`: "PASS ... allowed V +41 over 9ba8aeaedfc8"; `VE/Senses/Run.lean` +41
  (G[V] `rereadJson` and the `readCase` wiring); `lineJson` is G[R], the examples' `reread` T. FOLLOW-UPS.md
  "## sn-b6d" asks for the ties pass.
- Trust mutants: TRUSTMUT
- Statement gate and audit: AUDIT
- Size (hand-written lines added or changed, `git diff --numstat` against the merge base, generated files and the
  tool's evidence JSONs out): after (2), product code and side tables 160, tests and `#guard`s 236, then these docs
  and the seeded-bug list ~130: ~525. (3) projects to ~120-130 more (detection over both gloss forms, the rewrite
  cut from `lexSpans` bytes, a re-read, the hint's wiring and relay, a two-derivation fixture pack, tests, docs):
  past ~600, so the task's seam before (3) applies.

## Tests run

SELECTED

- `uv run python tools/relay_mutation_gate.py --route ve_senses_route::senses.read`: 4 fixtures, 2069 mutants, 2059
  refused, 10 allowed, 0 failures.
- Overlap: `feature/sn-b6-f8-trust` changes `docs/trust-baseline.json` and `tools/trust-classes.json` (other
  entries); whichever merges second merges those side tables.

Pilot bytes: 0 expected (no pilot document asks for the members; no unit's status changes).

## Spec re-read

- The line against docs/spec/senses.md 2.4 (`Assignment.lines`: `In this document, <word> means <gloss>.`) and 3.2
  (the same line in the `CandidatesDiverge` text): `lineOf` is that one owner, `#guard`ed slot by slot.
- The re-read against plan 2.8 / B7 ("re-read under that same projection; the base projection is never used") and
  reviews/dri-decisions-20261101-sn-b7b8-reread.md item 1 (the senses reader, not S2's policy).
- DRI 20261108-sn-b6c item 3's tests: base-projection rendering refused, goldens byte for byte, budget `unknown` and
  the same rendering `different` under an adequate budget.

## Next

sn-b6e: `GlossedNatural` whole (detect a glossed adjective before its noun, the rewrite with the gloss behind the
noun as `that is ...` (s10), its re-read under the same projection, the hint only for exactly one derivation, spec
3.2's text with `{i}` and `{rewrite}`; fixtures s10, a two-derivation rewrite, a sentence with no glossed adjective;
seeded bug: the hint for a rewrite with two derivations). Then sn-b7b (the display rest, Python only, on the
members of this item), then sn-b10.

Follow-up (C): a flip model's `constants` may omit a constant of the projection and the relay accepts it
(`_model_problem` checks the constants given); found while fuzzing a two-candidate asked fixture, which this item
does not use (the asked fuzz fixture is one-candidate). sn-b6b's member; not changed here.

## Self-review against BUILDER-CHECKLIST

SELFREVIEW
