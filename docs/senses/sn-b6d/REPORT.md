# sn-b6d REPORT (senses.read: the re-read of a rendering and Lean's line, for sn-b7b)

Status: (1) the re-read and (2) Lean's line are built (HEAD: the commit with this report's last edit; selected tests
exit 0 at `4063532f3`); (3) `GlossedNatural` is cut whole to sn-b6e at the size line
before it, as the task orders (sn-b7b does not need it). No DRI signature is reserved. Trust V +58, K +0 (R16).
Decisions: reviews/dri-decisions-20261108-sn-b6c.md items 1-3 (in /home/seyran/code/manage-agents),
reviews/dri-decisions-20261102-sn-b6b.md item 1, reviews/dri-decisions-20261101-sn-b7b8-reread.md item 1.

## Deliverables

| Task deliverable | Delivered | Where | Tests |
|---|---|---|---|
| (1) the re-read: optional source-request member `reread` `{sentence, candidate, rendering}`, read by `readOne` under the candidate's `linesProjection`, no policy, quoted senses refused; `same` / `different` / `unknown` (budget) | yes, from `3eae10692`; two changes: the member is decoded before any reading (`decodeReread`), and a rendering that is not one sentence is Lean's `InvalidInput` with the lexer's code when it does not lex (it was `different`) | `lean/VE/Senses/Run.lean` `decodeReread`, `rereadJson`, `readCase`; relay `_reread_problem` | `tests/test_senses_read_members.py::test_each_candidate_rereads_under_its_own_projection` (7), `::test_a_base_projection_rendering_is_refused`, `::test_the_reread_is_unknown_when_its_budget_ends`, `::test_a_golden_request_without_the_members_keeps_its_answer` (9), `::test_the_members_only_add_to_the_answer`, `::test_a_rendering_that_is_not_one_sentence_is_refused_by_lean`, `::test_a_long_rendering_ends_within_its_limits`, `::test_a_refused_reading_has_no_reread`, `::test_lean_refuses_a_malformed_member_before_reading` (16), `::test_reread_rebinding_is_refused` (6), `::test_an_unasked_reread_is_refused`; `#guard`s `lean/VE/Senses/TextsExamples.lean:91-95` |
| (2) Lean's line `In this document, <word> means <gloss>.` for a requested word and gloss | yes, from `3eae10692`: result member `line` `{word, gloss, text}` (`lineOf`, the one owner of the line, `Assignment.lean`), or `{word, gloss, code}` with `UnknownWord` / `UnknownGloss` | `Run.lean` `lineJson`; relay `_line_problem` | `#guard` per slot `TextsExamples.lean:77-81`; `::test_the_line_is_leans` (a refused reading too), `::test_line_rebinding_is_refused` (8), `::test_a_line_is_there_exactly_when_asked` (2), `::test_the_relay_refuses_a_malformed_line_request` (3) |
| (3) `GlossedNatural` (detection, rewrite, re-read, text) | **no: sn-b6e** (size line, below) | | |
| typed, bound, fuzzed | yes, in the relay (Deviation 1) | `ve/backends/senses.py` | `tests/test_senses_route.py::test_genuine_response_field_mutations_are_rejected[reread, line]` (every field dropped and retyped); the rebinding tests above; `tools/relay_mutation_gate.py --route ve_senses_route::senses.read` (two asked fixtures; `tests/test_relay_mutation_gate.py::test_the_senses_read_fixtures_ask_for_the_line_and_the_reread`) |

## Deviations

1. Typing stays on `ve_senses_route`: the members are typed and bound by the relay's validator
   (`_response_problem`, `_reread_problem`, `_line_problem`), not a response shape, as reviews/dri-decisions-20261108-sn-b6c.md
   item 1 rules after the sn-b6b precedent (reviews/dri-decisions-20261102-sn-b6b.md item 1). The theorem-level tie
   is the open design row sn-read-shape.
2. "The rendering is one sentence" is Lean's check, not the relay's: Python has no English reader (relay_lint), so
   `decodeReread` refuses a rendering that is not one sentence (`InvalidInput`; one over S2's lexer limit says
   `TextTooLong`), before any reading. The relay binds the unit and candidate (the request's, and one of the answer's).
5. Evaluated once: the rendering is lexed once, under S2's lexer limits, and read once against the request's budget.
   The candidate's projection is computed once more for the re-read (`linesProjection` over its lines, as
   `admittedIds` computed it for its identities): one candidate's lines, at most one re-read per request, bounded by
   the budget. Reusing `admittedIds`' table would change that function's type for one lookup.
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
| L4 | Lean, `Run.lean` `readCase` | a malformed `reread` ignored instead of refused | `::test_lean_refuses_a_malformed_member_before_reading` (10) |
| P4 | Python, `senses.py` `_line_problem` | the line's code not bound to what the dictionary lacks | `::test_line_rebinding_is_refused[code-word-for-gloss, code-gloss-for-word]` |
| G1 | Python, `tools/relay_mutation_gate.py` `_shape` | the asked members not part of a shape | `tests/test_relay_mutation_gate.py::test_the_senses_read_fixtures_ask_for_the_line_and_the_reread` |

The task's fourth seeded bug (`GlossedNatural` for a rewrite with two derivations) goes with (3) to sn-b6e. No Rust
changed.

## Trust, mutants, size

- `uv run python tools/trust_map.py --check`: "PASS: K, S and untied [V] within 9ba8aeaedfc8 and the allowances
  introduced since", "allowed V +58"; `VE/Senses/Run.lean` +58 (G[V] `rereadJson`, `decodeReread`, `lineJson`, whose
  text `ve senses resolve` writes into a document, and the `readCase` wiring); the examples' `reread` is T.
  FOLLOW-UPS.md "## sn-b6d" asks for the ties pass.
- Trust mutants (`zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/senses/sn-b6d/trust-mutants.json
  --test lean/VE/Senses/RunExamples.lean --test lean/VE/Senses/TextsExamples.lean`, ve-cloud-2): run 1
  (`trust-mutants-run1.json`, at `a07e5fada`): 75 KILLED, 12 SURVIVOR, 2 UNKNOWN, 11 INVALID. The survivors were cuts
  of the member-name list and of `units` (killed by new `#guard`s: both members in one request, a re-read of the
  second of two units), `drop` cuts of a one-sense word's senses (killed by `lineJson F "tells" "purple"`), and
  equivalent cuts (lists of at most one entry, `isEmpty` under `take 1`), allowed in `trust-mutants-allow.json`
  with the two UNKNOWNs, which do not elaborate. Final run (`trust-mutants.json`, `--allow` and `--rescore` of run 1,
  86 verdicts carried over a check-only change): 81 KILLED, 0 SURVIVOR, 0 UNKNOWN, 11 INVALID, 8 ALLOWED, 0 NOT RUN, exit 0.
- Statement gate and audit: `uv run python tools/lean_statements.py --check`: "added: 0, removed: 0, changed: 0 ...
  PASS: 8116 statements"; `python3 lean/audit.py`: "PASS: 789 source files; 8708 named theorem declarations audited
  ... only the declared standard axiom allowlist" (after the full `lake build`, "Build completed successfully (1319
  jobs)"; later only `TextsExamples.lean`'s `#guard`s changed, built with `lake build VE.Senses.TextsExamples`).
- Size (`git diff --numstat 9ba8aeaed`, generated files, the tool's evidence JSONs and the recorded gate cases out):
  710 added, 37 deleted. Of these, product code and side tables 174 (Run.lean 63, senses.py 78, the gate 13, the
  trust classes 11, the manifest pin 9), tests and `#guard`s 335 (pytest 266, guards 69), docs and the seeded-bug
  list 201. Measured after (2), before (3): ~367 of code and tests, ~525 with the docs to come; (3) projected ~120-130
  more (detection over both gloss forms, the rewrite cut from `lexSpans` bytes, a re-read, the hint's wiring and
  relay, a two-derivation fixture pack, tests, docs), past ~600, so the task's seam before (3) applies. The item then
  grew past the line on (1)-(2)'s own fixes: the self-review's two B findings (decode-first, the line's code binding:
  ~55 lines with their tests) and the `#guard`s that kill the trust mutants (~45). Neither could move to sn-b6e: both
  are conditions of (1) and (2).

## Tests run

- Selected tests once, on the committed tree (`MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base 9ba8aeaed
  --run`, at `4063532f3`, ve-cloud-2): exit 0, "recorded 472 units for tree d1d9e360cc; ... 0 failed" (7119 s). No
  test of main-known-red.txt failed, and none was touched.
- `uv run python tools/regen_generated.py --check`: "checked 37 entries"; `uv run python tools/trust_map.py --check`:
  PASS; `uv run python tools/relay_lint.py`: PASS ("4 senses module(s), no English reader");
  `uv run python tools/gate_collection.py --check --prebuilt`: "63 added, 0 removed by a trailer, 0 refused, 0 stale
  and 0 malformed trailers".

- `uv run python tools/relay_mutation_gate.py --route ve_senses_route::senses.read`: 4 fixtures, 2069 mutants, 2059
  refused, 10 allowed, 0 failures.
- Overlap: `feature/sn-b6-f8-trust` changes `docs/trust-baseline.json` and `tools/trust-classes.json` (other
  entries); `feature/ap-4` changes `tools/relay_mutation_gate.py` and `tests/data/relay-gate-cases.jsonl`, and
  `feature/ci-2b` `tools/relay_mutation_gate.py` (other functions). Whichever merges second merges them; a full
  `--record` on either must keep the two asked `senses.read` cases (the shape rule here keeps them).

Pilot bytes: 0 expected (no pilot document asks for the members; no unit's status changes).

## Spec re-read

- The line against docs/spec/senses.md 2.4 (`Assignment.lines`: `In this document, <word> means <gloss>.`) and 3.2
  (the same line in the `CandidatesDiverge` text): `lineOf` is that one owner, `#guard`ed slot by slot.
- The re-read against plan 2.8 / B7 ("re-read under that same projection; the base projection is never used") and
  reviews/dri-decisions-20261101-sn-b7b8-reread.md item 1 (the senses reader, not S2's policy).
- DRI 20261108-sn-b6c item 3's tests: base-projection rendering refused, goldens byte for byte, budget `unknown` and
  the same rendering `different` under an adequate budget.

## Next

FOLLOW-UP: sn-b6e GlossedNatural (detection, rewrite, re-read, text) on senses.read

sn-b6e: `GlossedNatural` whole (detect a glossed adjective before its noun, the rewrite with the gloss behind the
noun as `that is ...` (s10), its re-read under the same projection, the hint only for exactly one derivation, spec
3.2's text with `{i}` and `{rewrite}`; fixtures s10, a two-derivation rewrite, a sentence with no glossed adjective;
seeded bug: the hint for a rewrite with two derivations). Then sn-b7b (the display rest, Python only, on the
members of this item), then sn-b10.

Follow-up (C): a flip model's `constants` may omit a constant of the projection and the relay accepts it
(`_model_problem` checks the constants given); found while fuzzing a two-candidate asked fixture, which this item
does not use (the asked fuzz fixture is one-candidate). sn-b6b's member; not changed here.

FOLLOW-UP: sn-b6b-flipconst the relay accepts a flip model that omits a projected constant

## Self-review against BUILDER-CHECKLIST

SELF-REVIEW: 0 A, 2 B, 11 C; fixed 12 (both B; C: the line on a refused reading, the relay's line request
checks, the gate-fixture test, `lineJson` to G[V], the lexer's reason in the refusal, the overlap note, the FOLLOW-UP
lines, the DELTA claim's evidence, the size figure, "equal canonical JSON" for the goldens; the evaluate-once C is
answered in Deviation 5 and the flip-model C stays a follow-up).

1. PASS: `test_senses_route.py::test_genuine_response_field_mutations_are_rejected[reread, line]`, `::test_lean_refuses_a_malformed_member_before_reading` (16), relay mutation gate 0 failures.
2. PASS: deliverables table; (3) cut at the task's named seam (size above); one owner: the line is `lineOf`'s, the re-read Lean's, the relay only binds.
3. PASS: seeded bugs L1-L4, P1-P4, G1, each with its failing test; trust mutants exit 0 with an allow file.
4. PASS: `::test_a_golden_request_without_the_members_keeps_its_answer` (9 goldens against main's binary); RunExamples pins unchanged.
5. PASS: `::test_reread_rebinding_is_refused` (6), `::test_an_unasked_reread_is_refused`, `::test_line_rebinding_is_refused` (8), `::test_a_line_is_there_exactly_when_asked` (2).
6. PASS: selected tests and evidence on the committed final tree; the chain runs the gate.
7. PASS: DELTA rows cite R3 and R16 with their tests; nothing reserved.
8. PASS: DELTA rows 1-3; the emptied-lines refusal is no delta on a genuine answer (Lean writes a line for every candidate).
9. PASS: the selection ran 472 units, `tests/test_senses_read_members.py` among them.
10. N.A.: no theorem added or changed (statements unchanged).
11. PASS: `::test_the_reread_is_unknown_when_its_budget_ends`, `::test_a_refused_reading_has_no_reread` (budget 1); `#guard`s on budget 4000.
12. PASS: one lex and one budgeted read per request (Deviation 5); `::test_a_long_rendering_ends_within_its_limits`.
13. PASS: no test removed (`gate_collection.py --check --prebuilt`, 0 removed).
14. PASS: both directions (same and different, text and code, asked and unasked); the spec re-read above.
15. PASS: no overclaim (the cut is named; "byte for byte" reworded to equal canonical JSON); the cut point is the task's; every new check has a mutant; limits: the rendering is lexed under S2's limits before any reading.
