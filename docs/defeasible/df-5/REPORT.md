# df-5: the zone on the route (report)

**Status**: review loop round (recheck df-5-c050416-looprecheck1.final.md: F1, F5; reviews/df-5-dri-note-20261105.md)
committed; the recheck follows. HEAD: the last commit of feature/df-5. No DRI signature is reserved.
**What changed in the loop round**: fix (a) of the DRI note: the decoders' theorems bind each decoded value to the request's
field, and one value mutant per tied definition breaks its theorem (S10-S22); the records say only what the theorems
prove. T1 stays V +140 under R16. **DELTA**: D1 SIGNED by the DRI (reviews/dri-decisions-20261104-df-5.md item 1); T1
under R16. Bytes 0. Size: SIGNED by the DRI (reviews/dri-decisions-20261104-df-5-size.md item 1).

## Review loop round (F1, F5)

| Finding | Fix (the class) | Regression test | Seeded bug |
| --- | --- | --- | --- |
| F1 (A) the decoders "tied" by theorems that bind membership and type, not the decoded value (a `recordEntry` with its Bool flipped kept `recordEntry_sound`) | fix (a), for every definition T1 lists as tied: `decisionOf_mem` names the request's key, string by string (`decisionOf_key`); `tupleIn_typed` names the tuple (the request's `tuple` is `entityIds` of it, its sorts are `sorts`); `recordEntry_sound` and `obsEntry_sound` name the decision or outcome, the tuple and `a.snd`, the request's `value`; `replayZoneOn_sound` names the situation, the query's outcome and tuple, `early` as `zoneSizes`' answer on the request's sizes, and the record and observations as the request's entries decoded in order; `ZoneReplay.min_early`, `ZoneReplay.min_none`, `zoneSizes_none_iff`, `zoneSizes_observations` pin every branch; `zoneLine_rows_distinct` pins the rows' labels (as main's `outcomes_words`). No definition changed; T1 remeasured V +140 | `tests/test_defaults_zone_ties.py::test_review_f1_each_value_mutant_breaks_its_tied_theorem` (13 mutants, each alone in a `tmp_path` copy: its theorem's proof fails and nothing else; the unmutated copy elaborates); PROBE F1 passes (fails on d0e6c05c4) | S10-S22 |
| F5 (A) records claiming a value binding the theorems did not prove, and that the decoders' mutants break their proofs | each record says what its theorem proves: `ZoneWire.lean`'s module comment names each binding and its theorem; this report (summary, round 1's F1 row, "Trust") and DELTA T1 likewise; the words tables' text is tied for its selection only, as DELTA says. PROBE F5 passes. REPORT S7's stale citation of line 149 is `:164` now | PROBE F5 (no record keeps the sentence) | — |

On d0e6c05c4 (before this round), 10 of the 13 mutants elaborate: the old theorems held of them. Not bound by a
theorem: the words' text in `zoneHeads` and `zoneLineWords` (spec 4's sentences, read by `tests/test_defaults_zone.py`
and S8, S9), and which regulated outcome of a name `outcomeOf` returns when two share it (`find?`'s first). No
trust-mutant sweep this round: no trusted or tied definition changed (only theorems and comments), and
`tools/trust_mutants.py` does not mutate tied definitions; the final-Lean run stays moved to df-5-tm (R9).

## Review fix round 1

| Finding | Fix (the class) | Regression test | Seeded bug |
| --- | --- | --- | --- |
| F1 (A) the wire's request decoders and replay classed C, unproved | every decoder of the request bound to it by a theorem: `decisionOf_mem`, `outcomeOf_mem`, `tupleIn_typed`, `recordEntry_sound`, `obsEntry_sound`, `replayZoneOn_sound` (as first stated: membership and type only, not the decoded value; the loop round binds the values), `ZoneReplay.min_ok`, `zoneSizes_record`; classed D[V]/G[V] tied; `ZoneReplay`, `ZoneReplay.X`, `maxZoneObservations` G[V] untied and counted. Remeasured: V +140 (was +113 with 60 lines uncounted) | `lake build` (the theorems); `tools/trust_map.py --check` (exit 0); trust mutants ("Trust") | S7 |
| F4 (A) observations and record decoded before their bounds | `replayZoneOn` reads the situation and the query, then counts both lists (`zoneSizes`; the record's answer is `zoneCharge`'s, `zoneSizes_record`) before decoding any entry: past a bound, no entry is read | `ZoneWireExamples.lean`: 1,024 observations then one with no outcome, and 1,024 record entries then `null`, answer `unknown` (observations size, record size); one fewer each is refused with the entry's own fault; 1,024 entries answered | S4 |
| F2 (B) a decision recorded false accepted in a completion | `bind_zone` compares the answer with every value the request fixes: each completion names every decision the record sets true and none it sets false (DE11, DE10f and its `forced_all` entry, DE13 for an exception, a switch, a ranking); an observed query allows only `byDefault` with the observed value, never `leftTo` or `notSaid` (two default completions differ there, `defaultZone_leftTo_sound`, `defaultZone_notSaid_sound`) | `tests/test_defaults_zone.py::test_review_f2_probe_a_switch_recorded_false_is_not_shown` (PROBE F2), `::test_each_binding_refuses_a_row_its_request_contradicts` (8 cases), two new `TAMPERED` rows, fixture `observed_twice`; both-sides harness `tests/test_defaults_checks.py` | S5, S6 |
| F3 (B) the new rows' words owned by Python | `zoneHeads`, `zoneLineWords`, `zoneJoins` in `ZoneWire.lean`, keyed by the answer's fields that select each row (`zoneWords_complete`: one row per zone, form and line kind); `ZoneWordsMain.lean` generates `ve/defaults_words.json` (`tools/defaults_words.py`, regen entry `defaults-words`); `defaults_english` fills their slots and has no wording of its own for them (DE11 after DE6′ reads the same row; its text is unchanged) | `::test_review_f3_the_committed_words_are_the_lean_generators_output`, `::test_review_f3_every_zone_sentence_is_lean_s_words_filled`; the spec 4 texts in `CASES` unchanged | S8, S9 |
| F-ready1 (B) the relay mutation gate refused the built `ve_service` (unlisted build) | `lean/checkers.lock` (generated, `checker-pins`) regenerated by `tools/regen_generated.py --write` on the final Lean tree; `--check`: 36 entries up to date | the selected tests start the pinned service | — |
| FOLLOW-UP (C) size | the DRI accepted the size (reviews/dri-decisions-20261104-df-5-size.md item 1); this round adds only its findings' fixes | — | — |

## Plan rows (batch DF-5 at 174fbb62a, plan 2.7 and 2.8, D7, D10, D11; spec 3.8, 4, 5, 8.6, 8.8; task (1) to (5))

| Row | Delivered | Where | Evidence |
| --- | --- | --- | --- |
| (1) the `defaults-zone` row of PK-1's kind table; no new profile, no existing route, answer, identity, certificate or theorem statement changed (D7) | yes | `lean/VE/Defaults/Route.lean` (`defaultsKinds` gains the kind; `defaultsRows` answers by `zoneCase`, then `defaultsCase`); `layeredKindCase_other` keeps its statement | `evidence/conservativity.json` (62/62 identical, main's `ve_service` at the merge base against this branch's); `lean/statements.txt`: 0 removed, 0 changed |
| (1) its encoder and response-shape row | yes | `ResponseShape/Schemas/NormDefaults.lean` (`defaults_zone`, `defaults_zone_line`, digest-pinned); `ResponseShape/Encoders/NormDefaults.lean` (`zoneLine_fits`, `zoneCase_fits`, used by `layeredKindCase_fits`) | `lake build`; `tests/test_route_row_schemas.py` over the corpus with the 12 new cases (32 passed) |
| (2) DE10 in three forms, chosen by `zoneForm` (`zoneFormOf`) | yes | Lean: `zoneFieldsOf` gives `form` (short/long) with `byDefault`/`leftTo`, and `zoneHeads` words each (review F3); Python: `defaults_english.zone` fills DE10, DE10′, DE10″'s slots | DF-μ/ξ/π′ short, DF-δz long (`ZoneWireExamples.lean`; `test_each_zone_is_lean_s_and_reads_as_spec_4_says`) |
| (2) DE10f once per `forcedAll` entry no stated condition forces; never from `unknown` or no completion | yes | `zoneLines` (DE11 first, then DE10f from `forcedOfMin`'s list, else DE13); `zoneFieldsOf` reads `forcedAll` only for `byDefault`/`leftTo` | DF-μ (DE10f g1 at o1), DF-ξ′ (DE11, no DE10f), budget/no completion (no rows); `test_de10f_only_from_forced_all_and_never_from_unknown_or_no_completion` |
| (2) DE11, DE13 (exception, switch, ranking) | yes | `ZoneLine` rows; DE13 names the decision by its key (`decisionKeyJson`) | DF-ξ′, β2 (two DE11, conditions 1 and 0), DF-ε with the switch recorded, DF-δ with the ranking recorded |
| (3) `ve/defaults.py`: relay and bind only (typed schema; every id, tuple and label in the request; no Python copy of a Lean decision) | yes | `bind_zone`, `answer`, `soft_source` (adds each decision's sorts by key, from Lean's soft elaboration) | `test_mutants_never_pass_as_answers` (every one-fault mutant of 7 genuine rows), `test_each_binding_refuses_its_tampered_field_and_keeps_the_genuine_row` (12 refusals, each with the genuine row accepted) |
| (4) route cases: DF-μ, DF-μ′, DF-μ″, DF-δz, DF-ξ, DF-π′ end to end; DF-θ refused; conservativity (8.8) | yes | `tests/data/route-cases.jsonl` (+12, recorded by `tests.route_case_recorder`); `tests/test_defaults_zone.py`; `ZoneWireExamples.lean` | `evidence/delta.json`, `evidence/conservativity.json` (saved; no live git) |
| (5) seeded bugs: DE10f from an `unknown` zone; the "exceptions" form with a ranking open (DF-δ); Python accepting a tampered `forcedAll` entry; one mutant per new trusted definition | yes | `mutants.json` S1-S3; `trust-mutants.json` | "Seeded bugs" below |
| DRI 2026-11-04 item 2: `zoneMin` once; `zoneOfMin`, `forcedOfMin` with `defaultZoneOf_eq`, `forcedAllOf_eq` (rfl); a guard that the one-call answer equals `defaultZoneOf`/`forcedAllOf`; df-5a's Zone mutants rerun | yes | `Zone.lean`; `zoneFields` binds `x.min` once; `oneCall` guard on 8.6's fixtures | statements 0 removed / 0 changed; `evidence/df-5a-mutants-rerun.out` (25: all fail their guards), `evidence/df-5ab-mutants-rerun.out` (12, F4 re-targeted as F4′: all fail) |
| DRI 2026-11-04 item 1, conditions (i)-(iii) | yes | — | (i) `evidence/conservativity.json`; (ii) `ZoneWireExamples.lean`: `weighingText` is row 1's text and `viewRest` gives it on a `defaults-zone` request; (iii) the 8.6 guards through `runCaseReported` |
| Evaluator rule (each value once, size charged) | yes | `zoneMin` once; the record's and the observations' sizes (`zoneSizes`: `maxZoneRecord`, `maxZoneObservations` 1,024) counted before any entry is decoded (review F4), then df-5a's `zoneCharge` on the open atoms | guards: 1,025 observations or record entries `unknown` even with an undecodable last entry, 1,024 answered; DF-λ at 13 operators `budget: 26 open atoms, over 12` |
| Spec text (edit 6, the routes paragraph) | yes | `docs/spec/defeasible.md` (the two hunks, verbatim from 174fbb62a); `docs/spec/defeasible-PLAN.md` (verbatim from 174fbb62a) | `diff` against the pinned files: only df-5a's DRI-signed `valid` lines differ |
| `ve document readings --assume-no-exception` at a situation with observations | **no: df-5b** (not in the task's deliverables; size) | — | — |
| W7's all-derivations gate on the new rows | **no: df-5b** (deferred for every DE row to df-1bbc already) | — | — |

## Recorded choices (no statement changes)

1. **The request.** `model` is the situation (`situationX`), with every decision table empty: a fixed decision goes in
   `record`, named by its key (`{"excepted": r}`, `{"off": r, "party": π}`, `{"outweighs": a, "lower": L, "higher":
   H}`); `observations` and `query` name a regulated outcome and a tuple. A non-empty decision table is refused
   (`InvalidInput: the situation's decision tables are empty; a fixed decision goes in the record`): the zone leaves
   those atoms open, so a table there would be silently ignored.
2. **DE10″'s `<two completions>`.** Rendered as the two completions' rows in their own words without the sentence
   frame, joined by "and" within a completion and ", or" between them: "…, the answer depends on which rule gives way:
   the exception to rule r2 applies to a, or the exception to rule r1 applies to a." The row's fixed words are spec
   4's verbatim; only the slot's joining is this item's.
3. **`<tuple>`** is the entity ids, joined by ", ". **`<result>`** is Lean's `words` clause of the query's outcome
   with the zone's value. For DF-λ's plain `instructs` (no `act`) that clause is "o2 is instructs": the existing
   renderer's text, not this item's.
4. **DF-θ.** On main the layered decoder refuses `weighing@0` (`UnsupportedProfile: Unsupported profile weighing@0`)
   before diagnostic 1, for every `defaults-*` kind (DF-1a). Row 1's text is reached by `viewRest` on a decoded
   document; both are guarded.
5. **`noCompletion`'s labels** are bound to X's labels (the layered `norm-defaults-elaborate` row) or `ZONE_CHECKS`,
   the names of `zoneMin`'s and `zoneRow`'s own checks (record, background, fill, observed, typing).

## Seeded bugs (each planted alone, the named test fails, then restored)

| Id | Language, file | Bug | Fails |
| --- | --- | --- | --- |
| S1 | Lean, `lean/VE/Defaults/ZoneWire.lean` | DE10f from an `unknown` zone (forcedAll read as `[]` from an incomplete enumeration, the zone shown with rows) | `ZoneWireExamples.lean:126` (observations-size guard) |
| S2 | Lean, `lean/VE/Defaults/ZoneWire.lean` | the "exceptions" form with DF-δ's ranking open | `ZoneWireExamples.lean:66` (DF-δz guard) |
| S3 | Python, `ve/defaults.py` | a tampered `forced_all` entry accepted | `tests/test_defaults_zone.py::test_each_binding_refuses_its_tampered_field (its first tamper: an absent rule in forced_all)` |
| S4 | Lean, `ZoneWire.lean` `replayZoneOn` | review F4: the observations decoded before the size answer | `replayZoneOn_sound`'s proof; with it `sorry`, `ZoneWireExamples.lean:134` |
| S5 | Python, `ve/defaults.py` `bind_zone` | review F2: a decision recorded false accepted in a completion | `::test_each_binding_refuses_a_row_its_request_contradicts`, `::test_review_f2_probe_a_switch_recorded_false_is_not_shown`, `::test_each_binding_refuses_its_tampered_field` |
| S6 | Python, `ve/defaults.py` `bind_zone` | review F2: a zone other than the observed query's value accepted | `::test_each_binding_refuses_a_row_its_request_contradicts`, `::test_each_binding_refuses_its_tampered_field` |
| S7 | Lean, `ZoneWire.lean` `outcomeOf` | review F1: the outcome decoded without the request's name | `outcomeOf_mem`'s proof; with it `sorry`, `ZoneWireExamples.lean:74`, `:102`, `:164` |
| S8 | Lean, `ZoneWire.lean` `zoneLineWords` | review F3: DE10f's words changed in Lean, the table not regenerated | `::test_review_f3_the_committed_words_are_the_lean_generators_output` |
| S9 | Python, `ve/defaults_english.py` `zone` | review F3: DE10's words written in Python | `::test_review_f3_every_zone_sentence_is_lean_s_words_filled` |
| S10 | Lean, `ZoneWire.lean` `recordEntry` | review loop F1: a record entry's value flipped (the recheck's mutant) | `tests/test_defaults_zone_ties.py::test_review_f1_each_value_mutant_breaks_its_tied_theorem[recordEntry-value]`: `recordEntry_sound`'s proof fails, and nothing else |
| S11 | Lean, `ZoneWire.lean` `obsEntry` | review loop F1: an observation's value flipped | `tests/test_defaults_zone_ties.py::test_review_f1_each_value_mutant_breaks_its_tied_theorem[obsEntry-value]`: `obsEntry_sound`'s proof fails, and nothing else |
| S12 | Lean, `ZoneWire.lean` `decisionOf` | review loop F1: a ranking's lower and higher read from each other's fields | `tests/test_defaults_zone_ties.py::test_review_f1_each_value_mutant_breaks_its_tied_theorem[decisionOf-key]`: `decisionOf_key`'s proof fails, and nothing else |
| S13 | Lean, `ZoneWire.lean` `decisionOf` | review loop F1: the first keyed decision, whatever the request's key | `tests/test_defaults_zone_ties.py::test_review_f1_each_value_mutant_breaks_its_tied_theorem[decisionOf-lookup]`: `decisionOf_mem`'s proof fails, and nothing else |
| S14 | Lean, `ZoneWire.lean` `outcomeOf` | review loop F1: the first regulated outcome, whatever the request's name (S7's bug, now against the value tie) | `tests/test_defaults_zone_ties.py::test_review_f1_each_value_mutant_breaks_its_tied_theorem[outcomeOf-name]`: `outcomeOf_mem`'s proof fails, and nothing else |
| S15 | Lean, `ZoneWire.lean` `tupleIn` | review loop F1: the tuple decoded in reverse order | `tests/test_defaults_zone_ties.py::test_review_f1_each_value_mutant_breaks_its_tied_theorem[tupleIn-order]`: `tupleIn_typed`'s proof fails, and nothing else |
| S16 | Lean, `ZoneWire.lean` `replayZoneOn` | review loop F1: the observations decoded in reverse order | `tests/test_defaults_zone_ties.py::test_review_f1_each_value_mutant_breaks_its_tied_theorem[replayZoneOn-order]`: `replayZoneOn_sound`'s proof fails, and nothing else |
| S17 | Lean, `ZoneWire.lean` `replayZoneOn` | review loop F1: the record decoded from the observations' list | `tests/test_defaults_zone_ties.py::test_review_f1_each_value_mutant_breaks_its_tied_theorem[replayZoneOn-sibling]`: `replayZoneOn_sound`'s proof fails, and nothing else |
| S18 | Lean, `ZoneWire.lean` `ZoneReplay.min` | review loop F1: the sizes' early answer replaced by another unknown | `tests/test_defaults_zone_ties.py::test_review_f1_each_value_mutant_breaks_its_tied_theorem[min-early]`: `ZoneReplay.min_early`'s proof fails, and nothing else |
| S19 | Lean, `ZoneWire.lean` `zoneSizes` | review loop F1: past the observations' bound, the reason 'size' instead of 'observations size' | `tests/test_defaults_zone_ties.py::test_review_f1_each_value_mutant_breaks_its_tied_theorem[zoneSizes-reason]`: `zoneSizes_observations`'s proof fails, and nothing else |
| S20 | Lean, `ZoneWire.lean` `zoneSizes` | review loop F1: the observations' bound one higher | `tests/test_defaults_zone_ties.py::test_review_f1_each_value_mutant_breaks_its_tied_theorem[zoneSizes-bound]`: `zoneSizes_none_iff` or `zoneSizes_observations`'s proof fails, and nothing else |
| S21 | Lean, `ZoneWire.lean` `ZoneLine.row` | review loop F1: a stated condition's line labelled DE10f | `tests/test_defaults_zone_ties.py::test_review_f1_each_value_mutant_breaks_its_tied_theorem[row-label]`: `zoneLine_rows_distinct`'s proof fails, and nothing else |
| S22 | Lean, `ZoneWire.lean` `ZoneLine.kind` | review loop F1: a switch's DE13 line given the exception's kind | `tests/test_defaults_zone_ties.py::test_review_f1_each_value_mutant_breaks_its_tied_theorem[kind-label]`: `zoneLine_rows_distinct`'s proof fails, and nothing else |
| R16 | Lean, every new trusted definition | `tools/trust_mutants.py` | `trust-mutants-final.json`: 389 killed, 0 survivor, 0 unknown (see "Trust") |

## Trust

`uv run python tools/trust_map.py --check` (exit 0): K +0, S +0, **V +140** (`ZoneWire.lean` +100, the two shapes +36,
`ZoneWordsMain.lean` +2, `Route.lean` +2); the R16 allowance (`docs/trust-baseline.json`) and DELTA T1 itemise it.
Review F1: the 60 lines classed C before are D[V]/G[V] now; the decoders, `ZoneReplay.min`, `zoneSizes` and the words'
selectors are tied by the theorems in "Review fix round 1" (100 tied lines), and `ZoneReplay`, `ZoneReplay.X`,
`maxZoneObservations`, `zoneJoins` and `zoneWordsJson` are counted. The words' text is tied by `zoneWords_complete`
for its selection only; spec 4's sentences are checked by `tests/test_defaults_zone.py`. FOLLOW-UPS.md "## df-5" asks
for the ties pass of the rest.

`tools/trust_mutants.py` (`mac-pytest.sh --trustmut`, `--test lean/VE/Defaults/ZoneWireExamples.lean --test
lean/ResponseShape/DefaultsExamples.lean`, `--allow trust-mutants-allow.json`), the trusted definitions the branch
adds or changes:

- Build round (head 66190bd0c), `trust-mutants-final.json` before this round: 389 killed, 8 invalid, 29 allowed, 0
  survivor, 0 unknown.
- Fix round, first run (head c1d557077, kept out of the evidence): 396 killed, 32 survivors and 11 unknown, all in
  the words generator's JSON builder (`ZoneWordsMain.main`) and `zoneJoins`, which only the Python freshness test
  read. Fixed by `zoneWordsJson` and three guards that read it back (commit 9028ce14a).
- Fix round, final run: the run on the final Lean (d06883292) is moved to follow-up row df-5-tm by the DRI's
  fix-round bound (lp0401 Q3, R9), and the committed records stay `trust-mutants.json` (head 54a4a2067) and
  `trust-mutants-final.json` (head 66190bd0c), both from before the review fixes' Lean changes.
- Every definition has killed mutants except the inductive `ZoneLine`: its three `ctor-drop` mutants do not elaborate,
  because `zoneLines` and `ZoneLine.json` name the dropped constructor (as df-5a's T8 for `DefaultZone`). Each
  constructor is exercised by guards: `stated` by DF-ξ′ and β2, `forced` by DF-μ and two tuples, `assumed` by DF-μ′,
  DF-ε and DF-δ.
- The allowed mutants (`trust-mutants-allow.json`, each with its reason) are type errors in the mutated text, two
  equivalent ones (`value` has at most one element), two drops of `row`'s alternatives that no zone answer reaches
  (checked in Python by `tests/test_route_row_schemas.py`), and `defaultsRows` emptied (it fails RouteExamples'
  guards, which also reach the fits proof the mutant breaks).
- The tied definitions are not mutated by `tools/trust_mutants.py` (R16 counts trusted lines). One value mutant of each
  (S10-S22, loop round) breaks its tied theorem's proof, and only that theorem's
  (`tests/test_defaults_zone_ties.py`); S4 and S7 show the guards catch such a bug with the proof set aside. The words
  tables are tied for their selection only (`zoneWords_complete`, `zoneLine_rows_distinct`): a change of their text
  keeps both theorems and is caught by `tests/test_defaults_zone.py` (S8, S9).

## Tests run (loop round)

- Selected tests (`mac-pytest.sh --select`, base c3d9ea938, the worktree at 69268b56e with this round's records
  uncommitted): 478 of 540 units, 0 failed, exit 0. Actions gave 2 of 5 shards by its deadline (198 passed); the
  selection then ran on the VM (no Mac slot). It includes `tests/test_defaults_zone_ties.py`,
  `tests/test_defaults_zone.py` (PROBE F2's test and the F2 binding tests), `tests/test_defaults_checks.py`,
  `tests/test_assurance_manifest.py` and `tests/test_trust_budget.py`.
- `tests/test_defaults_zone_ties.py` alone: 16 passed (13 mutants, the unmutated copy, two helper tests).
- `cd lean && lake build`: completed (1275 jobs); `python3 lean/audit.py`: PASS (759 files, 8407 theorems);
  `tools/trust_map.py --check`: exit 0, V +140; `tools/regen_generated.py --check`: 36 entries up to date;
  `lean/statements.txt` against the merge base: 0 removed, 0 changed.
- PROBE F1: rc 1 on d0e6c05c4's `lean/statements.txt`, rc 0 now. PROBE F5: passes. The recheck's value-flip mutant
  of `recordEntry` elaborates on d0e6c05c4 and breaks `recordEntry_sound` now (S10).
- S4 and S7 replanted on the final `ZoneWire.lean`: each still breaks its theorem (`replayZoneOn_sound`,
  `outcomeOf_mem`); S5, S6 (Python) are unchanged and their tests passed in the selected run.
- Not run here: the full gate and the trust-mutant sweep (no trusted or tied definition changed; the final-Lean run
  is df-5-tm's, R9).

## Tests run (fix round 1)

- Selected tests (`mac-pytest.sh --select`, HEAD 49cc5d1dd, GitHub Actions, 6 shards): 491 units, 1 failed:
  `tests/test_merge_tooling_evidence.py::test_the_generated_file_table_names_every_entry` (the new `defaults-words`
  entry missing from `docs/merge-tooling.md`; fixed in bda9f6df5, the file rerun: 5 passed). `tests/test_defaults_zone.py`
  and `tests/test_defaults_checks.py` (every `bind_zone` check needed by a both-sides test) passed there.
- The final selected run of round 1 was left unrecorded here (a placeholder line, removed in the loop round).
- `cd lean && lake build`: completed; `python3 lean/audit.py`: PASS (759 files); `tools/lean_statements.py`: 0
  removed, 0 changed; `tools/regen_generated.py --check`: 36 entries up to date; `tools/trust_map.py --check`: exit 0.
- PROBE F2: fails on 8f507c5f4's `ve/defaults.py` (`DID NOT RAISE CheckerUnavailable`), passes now; it is
  `::test_review_f2_probe_a_switch_recorded_false_is_not_shown`. F1, F3 and F4 had no probe.
- F-ready1's probe (`review-ready.py`, HEAD bda9f6df5): `PASS [relay] relay mutation gate passed`; `[gate]` FAILs
  until the chain's full gate runs on the final HEAD (not run here, as the task says).
- Not run here: the full gate.

## Overlap

Hand-written files against every in-flight branch (`git diff --name-only <merge-base> <branch>`): feature/et-4b and
feature/ap-3db also edit `lean/ResponseShape/Schemas/NormDefaults.lean` and `lean/ResponseShape/Encoders/NormDefaults.lean`
(other hunks: `base_environment`, `layered_elaborate`); et-4b also edits `lean/VE/Defaults/Wire.lean`, which this
item does not touch (the wire is a new file). Several branches add imports to `lean/VE.lean`.

## Size

About 1,000 hand-written lines before this round (`git diff --numstat` against the merge base, without generated
files, the verbatim plan and spec, and the saved evidence). **SIGNED by the DRI**: reviews/dri-decisions-20261104-df-5-size.md
item 1 accepts the item as built with the proposed cut (the CLI path and W7's gate are df-5b). Its condition, no growth
beyond the fix round's findings, holds: this round adds the four findings' fixes, their tests and the regenerated files.

## Pilot bytes

0 (plan: none in bytes). The kind is reachable through the service; no pilot document asks a zone question yet.

## Next items

- df-5b: `ve document readings --assume-no-exception` at a situation with observations and a record (the CLI path to
  `ve.defaults.answer`), and W7's all-derivations gate on DE10-DE13.
- df-6, DF-E4 (the plan's next).

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: PASS. `defaults_zone` types every field (`lake build`: the digest pins and
   `zoneCase_fits`); `tests/test_defaults_zone.py::test_mutants_never_pass_as_answers` (drop, retype to 7, 1.5, true,
   null, [], {}, "\ud800", a 10,000-deep list, swaps, duplicates, on 7 genuine rows);
   `::test_each_request_member_retyped_or_dropped_is_refused_by_lean` (12 request paths × 7 values);
   `tools/relay_mutation_gate.py`: 46 routes, 148,161 mutants, 0 failures.
2. Every deliverable built: PASS (the plan rows table; CLI and W7 named as df-5b, not in the task's list). Grep of the
   diff: no Python copy of a Lean decision (`bind_zone` checks shape and binding only; `ZONE_CHECKS` names Lean's
   labels for binding), no Python words of DE10-DE13 (review F3: Lean's `zoneHeads`, `zoneLineWords`, `zoneJoins`;
   `::test_review_f3_every_zone_sentence_is_lean_s_words_filled`), no permanent report test, no def of the six
   weighing names under `lean/VE/Defaults/`.
3. Tests can fail: PASS. S1-S22 (`mutants.json`; S4-S9 round 1, Lean and Python; S10-S22 the loop round, Lean, run by
   `tests/test_defaults_zone_ties.py`), the R16 mutants (`trust-mutants.json`), df-5a's and df-5ab's Zone
   mutants rerun on the refactor (`evidence/*-mutants-rerun.out`: all fail their guards).
4. Python and Lean agree, valid inputs still pass: PASS. `evidence/conservativity.json` (62 of 62 identical);
   `tests/test_route_row_schemas.py` (32 passed: both decoders agree on every mutation of the 12 new cases).
5. R8 binding: PASS. `::test_each_binding_refuses_a_row_its_request_contradicts` (review F2: 8 requests whose record
   or observed query contradicts Lean's genuine row), `::test_each_binding_refuses_its_tampered_field` (25 tampers: an absent or strict rule, a
   tuple outside the situation, of the wrong length or type, a condition out of range, a party the rule lacks, a
   forced exception shown as an assumption, a duplicated or reordered row, an extra, repeated or emptied completion,
   an absent, repeated or empty label, an empty reason, a decision recorded false shown, a value against the observed
   query) and `::test_every_genuine_row_binds` (18 genuine rows);
   `tests/test_defaults_checks.py` reads them as both-sides tests, so each check of `bind_zone` weakened or deleted
   fails one of them (`test_review_f1_every_check_is_needed_by_a_both_sides_test`: passed); inputs:
   `ZoneWireExamples.lean` refusals (an absent decision, a malformed key, an outcome the document does not regulate,
   an entity outside the situation, a non-empty decision table).
6. Gate evidence: N.A. here (the chain runs the gate on the final HEAD); the saved evidence reads no live git.
7. No unsigned item: PASS. D1 SIGNED by the DRI (reviews/dri-decisions-20261104-df-5.md item 1), T1 R16 (V +140),
   size SIGNED by the DRI (reviews/dri-decisions-20261104-df-5-size.md item 1).
8. Every user-visible change in DELTA: PASS. `evidence/delta.json` (the 12 cases, main against this branch),
   `evidence/conservativity.json`.
9. Test selection: PASS. `tools/select_tests.py --base <merge base>` selects `tests/test_defaults_zone.py` (441 test
   files, not every unit).
10. Lean statements: PASS. `lean/statements.txt` against the merge base: 0 removed, 0 changed (20 added: the loop round
    restates df-5's own decoder theorems and adds 8); `defaultZoneOf_eq`, `forcedAllOf_eq` added;
    `python3 lean/audit.py`: PASS. A `BOGUS` row label in `ZoneLine.json` breaks `zoneLine_fits`
    (`Encoders/NormDefaults.lean:145`, restored).
11. Budgets and limits: PASS. `budget: 26 open atoms, over 12` (13 operators); the record's and the observations'
    sizes counted before any entry is decoded (review F4): 1,025 `unknown` even with an undecodable last entry, 1,024
    answered (`ZoneWireExamples.lean`); df-5a's record and typed-atom bounds unchanged.
12. CPU: PASS. `zoneMin` is evaluated once per request (`zoneFields`' one `let m := x.min`, DRI 2026-11-04 item 2;
    the `oneCall` guard: the answer equals `defaultZoneOf`/`forcedAllOf`'s). No step counter exists for this path.
13. Test-removed trailers: N.A. (no test removed; round 1 added five test ids in `tests/test_defaults_zone.py`, the
    loop round adds `tests/test_defaults_zone_ties.py`, 16 test ids).
    `tools/gate_collection.py --check --prebuilt`: 0 removed, 0 refused, 0 stale, 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS. Each guard and binding test has its accepting side; each
    claim here names its command; spec 3.8, 4 (DE10-DE13 words verbatim), 5 row 1 and 8.6 re-read against the
    fixtures (every computed zone matches 8.6).
