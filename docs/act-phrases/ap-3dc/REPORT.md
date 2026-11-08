# ap-3dc report: the `acts-elaborate` relay and the norms routes under `acts@0` on Lean's elaborated document

No DRI signature is reserved. Every DELTA row cites a standing ruling or the item-specific DRI ruling of 2026-11-02
(reviews/dri-decisions-20261102-ap-3db.md item 1, applied as the task directs). Cut at the size line in the task's
order: deliverables (1), (2) and the norms-route part of (4) are built; (3), (5), the document route and the Python
display seeded bug are the next item, ap-3dcb (section 3).

Plan: `80f056f9e:docs/spec/act-phrases-PLAN.md`, AP-3 "The `acts-elaborate` relay (mandatory)" and the `ve/norms.py`
line of the hook list. Spec on main: act-phrases.md 6.4, 6.7, 10 (D-15 to D-18, D-24, D-28), 11.3 (A6, A7, A14, E5j).
Edits of plan synthesis round 2 (`debates/plan-synthesis-2/edits-act-phrases.md`): none implemented here (DEC 16,
u0218.s18 kept unsplit, is deliverable (5), cut to ap-3dcb).

## 1. What was built

| Plan row / deliverable | Commit | Evidence |
|---|---|---|
| (1) `acts-elaborate` shape (`lean/ResponseShape/Schemas/Norms.lean` `«acts-elaborate»`, selected by the `norms` and `norm-defaults` rows) | 0d4ef25d6, e817c7017 | render pins in `Schemas/Norms.lean` and `Service/ActsExamples.lean` (NormDefaults row and kinds) |
| (1) encoder theorem `runElaborate_fits` (`lean/ResponseShape/Encoders/Norms.lean:108`), used by both modes' `_fits` | 0d4ef25d6 | `lake build` (1321 jobs) and `python3 lean/audit.py`: PASS, standard axioms only |
| (1) the case kind: `VE.Acts.Run.runElaborate` (decode, `elaborateSource`, `sourceOf`); `REFUSED` with the diagnostic and every list empty; `UnsupportedProfile` without `acts@0` | 0d4ef25d6 | `Service/ActsExamples.lean` section Relay (A6 both routes, E5j `unspecified` parts, A7 kept whole, D-20 refused row, 32 sources and 128 rules at the limits) |
| (1) generated schema `ve/backends/lean_service_schema/norms.json` (`acts-elaborate`; `if` the verdict is `REFUSED`, `diagnostic` is required, `else` it is absent) | 6b0515056, e817c7017 | `regen_generated --write` |
| (1) binding: each `p__i` and `<rule>-a<i>` to its source and index (`SplitMap`), every copied field to the request, `split` rows with D-28's text relayed verbatim (`ve/norms.py` `bound_elaboration`) | 35bc2eac0 | `tests/test_acts_elaborate_relay.py::test_genuine_row_mutants_never_pass_as_answers` (retypes, rebinds, drops, duplicates and adds every field and row), `::test_a_refused_row_with_a_part_or_no_text_is_no_answer` |
| (1) route cases: norms A6, norms D-24, norm-defaults A6 (`tests/data/route-cases.jsonl`) | ac99b8752 | `tests/test_route_row_schemas.py::test_genuine_route_answers_are_accepted_by_schema_and_lean` |
| (2) `_lean_route` true for every `acts@0` document; the retained Python path refuses it (`CheckerUnavailable`); conflict search and prover run on the relayed document; D-28 for a split source | 35bc2eac0 | `::test_the_retained_python_path_refuses_an_acts_document`, `::test_the_conflict_search_and_prover_run_on_the_parts`, `::test_a_split_source_is_refused_with_leans_text` |
| DRI 2026-11-02 ap-3db item 5: `Environment(data)` admits a joined act through the act check, in the change that makes the relay read the elaboration; the composed paths keep D-4 | 0d4ef25d6, 35bc2eac0, e817c7017 | `tests/test_acts_profile.py::test_a_joined_act_the_frames_read_loads`, `::test_a_joined_act_is_refused_with_leans_text` (moved to D-16, id kept); `ActsExamples.lean:709-714` |
| (4) A6, A7, A14 through the route; precedence pairwise; differing act lists refused (D-24) | 35bc2eac0 | `::test_a6_gives_two_prohibitions_named_by_their_parts`, `::test_a7_is_one_obligation_kept_whole`, `::test_a14_gives_five_prohibitions_through_the_route`, `::test_precedence_splits_pairwise`, `::test_differing_act_lists_are_refused_through_the_route` |
| Route case running the relay on a part document (dr-ap-acts-elaborate) | ac99b8752 | the three route cases above (u027's A6 part) |

## 2. Limits and once-only evaluation

Each act is read once, by the decoder; `runElaborate` adds one pass over the elaborated document. The limits are the
decoder's (64 regulated predicates, 256 rules). The fixture at those limits is in `ActsExamples.lean` ("A request at the
limits": 32 joined sources and 128 rules give 64 parts and 256 part rules). Python makes one `acts-elaborate` call per
`NormDocument` and caches it (`NormDocument.relayed`).

## 3. Not built (cut at the size line): ap-3dcb

Hand-written lines changed over the merge base, generated files and tool-written evidence excluded: about 1,000 lines
(`git diff --numstat $(git merge-base HEAD main)`). The cut was made at 739 lines; the trust-mutants fixes added the
rest. Still to do, in the task's order:
- (3) `test_reference_table_complete` (the relay's reference table over `Node`, `Regulated`, `Definition`, `Doc` and the
  Python inputs);
- (4, rest) the document route on the elaborated document (`Service/Document` admitting a joined act), a G6 normal form
  through `ve document check` or `ve render` on a part document (dr-ap-2bb-public, **not closed by this item**), and the
  Python display seeded bug ap-3d deferred;
- (5) u0218.s18's regression document (DEC 16: kept unsplit, blocker "embedded act frame: modality MD-6");
- `UnspecifiedDocument` and `prove_norm_entailment` on the relayed document; D-28 for `data@0` facts and questions.

## 4. Seeded bugs (each planted, the named check failed, restored)

Committed in [mutants.json](mutants.json), with file and test keys:

| id | file | definition | failing check |
|---|---|---|---|
| split-text-parts | lean/VE/Acts/Run.lean | `splitRows` | `lean/VE/Service/ActsExamples.lean:641` |
| part-index | lean/VE/Acts/Run.lean | `predicatesJson` | `ActsExamples.lean:641` |
| refused-lists | lean/VE/Acts/Run.lean | `runElaborate` | `ActsExamples.lean:655` |
| env-row-lexical | lean/VE/Service/Standalone.lean | `environmentCase` | `ActsExamples.lean:709` |
| over-unbound | ve/norms.py | `bound_elaboration` | `tests/test_acts_elaborate_relay.py::test_genuine_row_mutants_never_pass_as_answers` |
| searches-on-source | ve/norms.py | `NormDocument.conflict_targets` | `::test_the_conflict_search_and_prover_run_on_the_parts` |
| split-not-refused | ve/norms.py | `NormDocument.refuse_split` | `::test_a_split_source_is_refused_with_leans_text` |
| retained-decides | ve/norms.py | `_retained` | `::test_the_retained_python_path_refuses_an_acts_document` |

No Rust was changed.

## 5. Trust (R16)

`uv run python tools/trust_map.py --check` on the final HEAD, against main 094254625: K +0, S +0, untied V +116
(trusted +116), within the signed allowances (114 + 4 = 118). Per file: `VE/Acts/Run.lean` +67, `ResponseShape/Schemas/Norms.lean`
+34, `VE/Service/Standalone.lean` +3, `VE/Norms/Run.lean` +3, `VE/NormDefaults/Wire.lean` +3, `VE/NormDefaults/Run.lean` +3,
`ResponseShape/Schemas/NormDefaults.lean` +2, `VE/WireContract/Hooks/Acts.lean` +1. The new check helpers are in
`tools/trust-classes.json` as T. FOLLOW-UPS.md "## ap-3dc" asks for the ties pass.

Trust mutants: [trust-mutants.json](trust-mutants.json), with [trust-mutants-allow.json](trust-mutants-allow.json).
Final run on 9be4cebeb (`zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/act-phrases/ap-3dc/trust-mutants.json
--test lean/VE/Service/ActsExamples.lean --allow docs/act-phrases/ap-3dc/trust-mutants-allow.json --rescore <the previous
evidence>`; the base had moved with the main merge, so every mutant reran: `rescore.rerun` 438, `reused` 0): exit 0, 365 KILLED,
0 SURVIVOR, 0 UNKNOWN, 40 INVALID, 33 ALLOWED, 0 NOT RUN. The allow file lists 17 (definition, operator) pairs. Each is an
equivalence (a one-member `documentLayers`, `isEmpty` of a first or last cut, a split source's two or more parts), a cut
Lean refuses to elaborate, or an UNKNOWN that exists only because the probe cannot re-elaborate the refuting guard (a
default argument inlined at the call, `Readings/ActsExamples.lean:79`). Each of those names the guard that refutes it.
The first run (d7108e943) had 250 survivors, 228 of them in the schema shapes. The render pins in
`Schemas/Norms.lean` and `ActsExamples.lean`, and the guards for carve-outs, two split sources, `data@0` flags,
`acts@0` alone, the composed path's D-4 and the wire contract's decoder, killed them.

## 6. Tests

- Selected tests (`zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, on 5aeccc443 after the main
  merge, 6 shards on the cloud): shards 1-5 passed (81 + 81 + 82 + 82 + 83 units); shard 6 had 2 failures,
  `tests/test_route_row_schemas.py::test_no_answer_object_is_left_open` and `::test_an_open_answer_is_found`. The new
  `anyOf` branches of the `acts-elaborate` shape were open objects. Fixed in 9be4cebeb (`if`/`then`/`else`, as
  `defaults_coherence` writes it). Rerun: those two ids, `::test_genuine_route_answers_are_accepted_by_schema_and_lean`
  and `tests/test_acts_elaborate_relay.py`, 20 passed.
- `lake build` (1321 jobs) and `python3 lean/audit.py` (PASS, 787 files) on 9be4cebeb; `uv run python
  tools/gate_collection.py --check --prebuilt`: 18 added, 0 refused, 0 stale, 0 malformed.
- Tests failing on main (main-known-red.txt): none among the selected failures.
- The full gate is left to the chain.

## 7. Pilot bytes (estimate only; nothing is claimed before a pilot audit)

About 0 B on the constitution pilot from this item alone. The pilot runs the document route, which reads the elaboration
only in ap-3dcb. u079b's 76 B (A7) waits for ap-3dcb.

## 8. Spec re-read

- `acts-elaborate` row fields and D-28's text against act-phrases.md 6.7 and 10 (D-28): source, parts in index order,
  "name one of its parts: p is split into p__1, p__2".
- Binding against the plan's relay row (80f056f9e, about line 880): each `p__i` and `<rule>-a<i>` names its source
  predicate or rule in the request, with its index as `SplitMap` exports it.
- E5j against 11.3: an unspecified source splits into unspecified parts (`ActsExamples.lean`, norm-defaults A6 guard).
- D-24 against 10: a predicate whose rules give different act lists is refused (`::test_differing_act_lists_are_refused_through_the_route`).

## 9. Next item

ap-3dcb (section 3); then ap-4.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS. `tests/test_acts_elaborate_relay.py::test_genuine_row_mutants_never_pass_as_answers` removes each
   key. It retypes each value (7, true, null, [], {}, "x", -1, 999, 1.5), shifts each integer by one, empties each string,
   renames each source, and duplicates, reverses, drops and replaces rows of each list of the genuine row. Each mutant
   goes through the schema check and `bound_elaboration`. Also `::test_a_refused_row_with_a_part_or_no_text_is_no_answer`.
   Bytes, deep lists and lone surrogates are the shared client decoder's, unchanged here.
2. Deliverables: PASS for (1), (2) and (4)'s norms-route part (section 1). (3), (5) and the rest of (4) are cut at the size
   line, as the task's "cutting at the size line" allows; they are named as ap-3dcb (section 3).
3. Tests can fail: PASS. 8 seeded bugs (section 4, mutants.json); trust mutants exit 0 (section 5).
4. Python, Lean and Rust agree: PASS. The 469 existing route cases are unchanged and 3 are added
   (`tests/test_route_row_schemas.py::test_genuine_route_answers_are_accepted_by_schema_and_lean`). A7 relays unchanged
   (`::test_a7_is_one_obligation_kept_whole`). No Rust changed.
5. R8 binding: PASS. `bound_elaboration` checks each source, index, part and copied field against the request, tested by
   `::test_genuine_row_mutants_never_pass_as_answers` (seeded `over-unbound`); an undeclared name is refused by
   `::test_a_split_source_is_refused_with_leans_text`.
6. Gate evidence: PASS for the parts I ran. Main (094254625) was merged in 7e8f74b00; the full gate is left to the chain on the
   final HEAD.
7. No unsigned item: PASS. Every DELTA Ruling cell cites R6, R16 or the DRI ruling of 2026-11-02 item 1 (DELTA.md).
8. Every user-visible change in DELTA: PASS. DELTA rows 1-4 cover the environment row, the refusal texts, the new case kind
   and the retained path; the "no change" line names its tests.
9. Test selection: PASS. `tools/select_tests.py --base $(git merge-base HEAD main)` selects 456/552 units, including
   `tests/test_acts_elaborate_relay.py`, `tests/test_acts_profile.py` and `tests/test_route_row_schemas.py` (the last is the
   one the shape change broke).
10. Lean statements: PASS. `runElaborate_fits` is about the value `runElaborate` returns. The render pins break on any
    change to the shape, and the trust mutants on `«acts-elaborate»` were killed. No statement was added or changed beyond
    AP-3's list.
11. Budgets and limits fail closed: PASS. The decoder's limits come before elaboration, with the at-limit fixture in
    `ActsExamples.lean` (32 sources, 128 rules). No new budget-taking operation.
12. No CPU or memory regression: PASS. One `acts-elaborate` call per document, cached (`ve/norms.py:481-486`). No pilot timing
    was run (the L70 rule forbids whole-document runs).
13. Test-removed trailers: PASS. No test was removed; `gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and
    0 malformed.
14. Both directions, cited evidence, spec re-read: PASS. Accept and refuse sides: the environment row admits A6 and refuses
    D-16 (`ActsExamples.lean:709-714`); the composed path keeps D-4 (`:716-719`); `acts@0` alone is read, and without
    it the case is refused. Spec re-read: section 8.
15. Overclaim, silent cut, checks can fail, limits before work: PASS. Deferred work is written as deferred (section 3,
    dr-ap-2bb-public "not closed"). The cut follows the task's named cut point. Every new guard has a killing mutant
    (trust-mutants.json). Limits: item 11.
