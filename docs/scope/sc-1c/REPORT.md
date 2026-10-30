# sc-1c: the explain route and relay (scope SC-1c). Build report

- **Status:** built; no DRI signature is reserved. DELTA row 1 cites SYNTHESIS 2.2/4.2 as me-2b's row 1 does, row 2 R16 (V +4).
- **What changed:** the service mode `scope` (`VE.Scope.Run.runCaseReported`), its provenance sentences (`VE/Scope/English.lean`),
  the shape `scope.json` with `runCaseReported_fits`, the relay `ve/scope.py` and `python -m ve scope explain FILE [--ids]`.
- **Open:** size (~1,000 hand-written lines against ~600) is asked of the DRI (inbox `20261030T162456Z-sc-1c-2436193.md`);
  cut to **sc-1cb**: the rows of a reading set governed per choice, the generated rules (`explain_generated`), the rule in full.
- HEAD: the last commit of `feature/sc-1c` (base main `5b0163e94`); the gate is the chain's (not run here).

Branch `feature/sc-1c`, worktree `/home/seyran/code/ve-sc-1c`. Read first: plan SC-1c, 1.6, 3, 7; spec 2.3, 3, 5.3, 7.3, 8.1;
SYNTHESIS 2.2, 4.2; `debates/plan-synthesis-2/edits-scope.md` (none of its seven edits or DEC 10/16 is SC-1c's; this item
implements none of them); sc-1b, sc-5r and sc-5rb's REPORTs; me-2b's REPORT (the new-mode pattern).

## Statement gate

PASS: the scope statement review closed (scope-p3ver1/p3ver2 final), sc-5r's addendum ended MERGE. The two statements
proved here are spec 5.3's text after whitespace normalisation: `explain_bound` and `explain_rows_iff`
(`tests/test_scope_answer.py::test_the_proved_statements_are_spec_5_3s_text`, which compares both files). The recipe
theorems have the recipe's fixed forms: `VE.Service.runMode_scope (j : Json) : runMode .scope j = VE.Scope.Run.runCaseReported j`
(`rfl`) and `ResponseShape.Encoders.Scope.runCaseReported_fits (j : Json) : Fits j Skeletons.scope (VE.Scope.Run.runCaseReported j)`.
`explain_generated` is not proved (sc-1cb). No merged statement changed.

## Plan rows and task deliverables

| Row | Delivered | Where, checked by |
|---|---|---|
| (1) mode `scope`, runner `VE.Scope.Run.runCaseReported` in `lean/VE/Scope/Run.lean` | yes | `Mode.scope` (`Registry.lean`, appended), `runMode` line and `runMode_scope` (`Protocol.lean`), in `lean/VE/Audit.lean` (generated); `modes_complete`, `test_handshake` |
| (1) `MODES` entry | yes, generated: `MODES` reads `envelope.json`'s handshake list (ar-10b) | `tests/test_lean_service.py::test_handshake` |
| (2) `ResponseShape.Schemas.Scope`, `ResponseShape.Encoders.Scope.runCaseReported_fits` | yes; registered in `Schemas.lean`, `Skeletons.lean`, `Encoders.lean` (`runMode_fits`' case); listed in `lean/ResponseShapeAudit.lean` (generated; the task's `lean/ResponseShape/Audit.lean` is that file on main) | `lake build`; `python3 lean/audit.py` PASS |
| (2) generated `scope.json` | yes (`regen_generated.py --write`) | `regen_generated.py --check`: 34 entries checked, none stale |
| (3) rows per governed unit: `unit`, `governors` (`id`, `unit`, `effect` word, `reach`), `provenance` | yes. Spec 5.3's `explainRows` (gate `govern`), read by the run path `explainFast` on `governFast`'s tables computed once (`explainFast_eq`). On the wire each sentence sits in its governor's object, so it cannot be paired with another governor (below) | `RunExamples.lean` F-ex and every contributor's sentence; `explain_bound`, `explain_rows_iff`, `explainRows_effect` |
| (3) provenance sentences from `VE/Scope/English.lean` | yes, spec 2.3's rows `frame`, `reguard`, `carve_out`, `precedes`, `yields`; `<text>`, `<where>`, `<cover>` | `RunExamples.lean` (each reach kind, both sides of 12 words); the generated-rule row is sc-1cb |
| (3) binding: every unit and governor id exists in the request | yes, in the relay (the request carries the document as text, so the shape cannot point into it); `explain_bound` proves it on Lean's side | `ve.scope.answer_problem`; `test_a_row_lean_did_not_bind_to_the_case_is_no_answer` |
| (4) relay `ve/scope.py`, schema and binding only (R8) | yes, through `relay.answer` (the one relay entry; it carries the service's code beside a refusal, which `rows` drops, so a `ManifestMismatch` is raised with its class) | `tests/test_scope_answer.py`; `tools/relay_mutation_gate.py --route service:scope` |
| (4) `ve scope explain` in `ve/__main__.py` | yes, appended (dispatch and help line) | `test_the_reader_sees_each_units_text_and_its_sentences_and_the_ids_only_in_the_provenance_view` |
| (5) route cases in `tests/data/route-cases.jsonl` | 12: each effect on the norms chain, a three-governor document, `yields` on soft-norms, `title` (no row), and four refusals | `test_route_cases_answer_their_rows`; `tests/test_route_row_schemas.py` (corpus, shape fuzz, Lean agreement) |
| (5) fuzz tests in `tests/test_scope_answer.py` | yes: every one-fault structural mutant (drop, add, duplicate, retype), reorders, out-of-range and rebound ids, each effect word, and two-fault drops (a governor with its row); every mutant is refused or shows nothing new, on three documents | `test_every_mutant_of_a_genuine_answer_is_refused_or_changes_nothing_shown` |
| seeded bugs in Lean and Python, one mutant per new trusted definition | yes | `mutants.json` (13), `trust-mutants.json` |
| evaluate once, size bounded (DRI 2026-10-27) | yes: the order, each reach and each governor unit's base name are read from tables computed once (`fastReads`, `memo`), proved equal to spec 5.3's reads (`explainFast_eq`); the runner splits the document once (`readSplit`, `readSplit_scope`) and quotes each governor unit once (`quotesOf`); the answer is bounded by `cellBound` (rows × the block's recorded reach units), refused past 524,288 cells as `ResourceLimit` (UNKNOWN) | `RunExamples.lean`: at the bound 112 it answers, at 111 and 0 it is UNKNOWN |
| per-choice GOVERN (sc-5rb) | **sc-1cb**: the gate is spec 5.3's `govern`, so a document with a reading set governed per choice is refused with `ScopeReadings` (the document mode admits it) | FOLLOW-UPS "## sc-1c" |
| generated rules (`generated`, `explain_generated`), the rule written in full (1.6) | **sc-1cb** | FOLLOW-UPS "## sc-1c" |

Deviations, each named: (a) spec 2.3's `<cover>` says "<n> rules"; one rule reads "1 rule". (b) Spec 5.3's `Row` keeps
`provenance` as a list; the wire nests each sentence in its governor's object and adds `governed`, the relay's index of
the rows, which it zips with the request's governors (without it a dropped governor or row could only be found by
re-deriving `contributors` in Python). (c) The source text a sentence quotes is not in `SDoc`: `explainRows` reads it
through the class `Quotes`, which the runner instantiates from the source once, so the statements keep spec 5.3's
text. (d) The relay uses `relay.answer`, not `rows` (above).

## Found while building

- The binding cannot be total in the relay without copying `contributors`: the answer's `governed` index makes every
  single drop visible; a coordinated drop of a governor from its row and its index is covered by `explain_rows_iff`.
- The display sorts each unit's governors by the block's order, so a reordered answer shows the same (the fuzz test).

## Seeded bugs

[mutants.json](mutants.json): 13, each planted alone on the committed tree, the named check run, restored.
- **Lean (9):** `contributorsF` without `yields` (`explainFast_eq`); `whereOf` earlier/later swapped (F-ex guard);
  `explainWithin` refusing at the bound (cell guard); `govJson` renaming `reach` (`runCaseReported_fits`); `effectWord`
  `carve_out` (effect-words guard); `quote` with `≥ 12` (the 12-word guard); `governedJson` inverted (the governed
  guard); `.scope` dropped from `modes` (`modes_complete`); `.scope` dispatched to the document runner (`runMode_scope`).
- **Python (4), `ve/scope.py`:** no reach binding, no `governed` check, the answer's governor order displayed, Lean's
  refusal ignored; each fails its named test in `tests/test_scope_answer.py`.
- **No Rust** product code changed.

## Trust, size, bytes

- `tools/trust_map.py --check` (final HEAD): K +0, S +0, trusted +4 (Registry, Protocol, Skeletons, Schemas +1 each),
  allowance recorded (`docs/trust-baseline.json`, R16). Trust mutants (`mac-pytest.sh --trustmut -- --max-mutants 1000
  --allow docs/scope/sc-1c/trust-mutants-allow.json`): 19 mutants, 11 KILLED, 8 ALLOWED, 0 SURVIVOR, 0 UNKNOWN, exit 0
  ([trust-mutants.json](trust-mutants.json)); the allowed are `modes` drops killed by `modes_complete` and mutants that do
  not elaborate, as me-2b's and qt-a3c's.
- **Size:** `git diff --numstat 5b0163e94` without generated files: about 1,000 lines (Lean 451, tests 212 with fixtures,
  `ve/scope.py` 150, side tables and evidence ~160), plus this report. Over the ~600 guide; asked of the DRI (option (a)
  take, (b) move the relay, CLI and fuzz tests to sc-1cb).
- **Bytes:** 0, as planned (the reader's view). Pilot bytes moved: none claimed.

## Tests run

- `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`: 504 units; 3 failed
  (`test_assurance_manifest::test_every_json_handling_lean_file_is_classified`, `test_shape_binding_mutants[scope]`,
  `tools/test_layer_policy.py`), fixed (the `other_json` reason, `binding_census.py --answers`, the layer row) and rerun:
  `mac-pytest.sh -- <the three>`: 42 passed. Pre-existing main failures: none met.
- `tests/test_scope_answer.py`: 15 passed. `relay_mutation_gate.py --route service:scope`: 1,577 mutants, 0 failures.
- `regen_generated.py --check` (34 entries), `gate_collection.py --check --prebuilt` (19 added, 0 removed),
  `repo_map.py --check` (40 modes), `lean/audit.py` PASS. The full gate is the chain's.

## Spec re-read

- `explain_bound`, `explain_rows_iff` against `docs/spec/scope.md:1221-1226` (the statement test).
- Row members `unit`, `governors` (`id`, `unit`, `effect`, `reach`), `provenance` against `scope.md:1190-1200` and the task.
- Effect words against `effectWord` at `scope.md:1202-1204` (`carve-out` with a hyphen; the effect-words guard).
- Sentences against `scope.md:383-394` (deviation (a)); binding against plan "Binding" (`scope-PLAN.md:745`).

## Next items

AP-4 (protocol queue), SC-2, SC-E2 on this route; and:

FOLLOW-UP: sc-1cb per-choice rows of a governed reading set, generated rules (explain_generated) and the rule in full

## Self-review against BUILDER-CHECKLIST

1. PASS: `test_every_mutant_of_a_genuine_answer_is_refused_or_changes_nothing_shown`; relay gate (1,577 mutants, retypes and 10k-deep).
2. PASS: the rows table above; one owner: no Python copy of a Lean decision (the relay binds, sorts for display only).
3. PASS: `mutants.json` (13 killed), `trust-mutants.json` exit 0.
4. PASS: `tests/test_route_row_schemas.py` (schema and `ve_response_decode` agree on every mutant); three chains in the route cases.
5. PASS: `test_a_row_lean_did_not_bind_to_the_case_is_no_answer`; the fuzz test's `u9999`, rebound ids, extra and duplicated rows.
6. PASS: the gate is the chain's, on the committed final HEAD; base from `git merge-base`.
7. PASS: DELTA rows 1–2 cite SYNTHESIS 2.2/4.2 and R16; trust growth recorded with `--allow`.
8. PASS: DELTA row 1 (a new mode and command; no existing answer changes: `test_route_row_schemas.py`, `test_lean_service.py`).
9. PASS: `select_tests` selected `tests/test_scope_answer.py` among 504 units.
10. PASS: the `govJson` rename breaks `runCaseReported_fits`; the dispatch mutant breaks `runMode_scope`.
11. PASS: cell limit 0 is UNKNOWN (`RunExamples.lean:64`); no sleeps or deadlines in the tests.
12. PASS: no eager re-read: `explainFast` reads `fastReads`' tables (`explainFast_eq`); no timing asserted in the suite.
13. N.A.: no test removed or renamed (`gate_collection.py --check --prebuilt`: 0 removed).
14. PASS: both sides of each check (cell bound 112/111/0, 12 words, each `<where>`, listed and unlisted `scope@0`); claims cite commands above; spec re-read above.
