# cmp-s4c: the discourse route's entry on the composed path, its relay and the chain decoders (discourse 14.5, 14.6)

- **Status:** done as cut below; no signature reserved. DELTA: four rows, each signed: DRI 2026-11-02 item 2,
  DRI 2026-11-04 item 1 (`dri-decisions-20261104-cmp-s4c.md`), DRI 2026-11-04 item 1
  (`dri-decisions-20261104-cmp-s4c-norm.md`), R2.
- **What changed:** `runCase` (`lean/VE/Discourse/Run.lean`) decides the composed path before `baseVocabulary`
  (14.6, the wire entry; `chainCase`); step 1's family check is the decoder of the route `dispatch` chooses for
  the base list (`chainEnvironment`, `Compose.lean`), read once and handed to step 3 (`chainBaseWith`); the
  composed row has a typed shape (`chain_admission`, `composed`, `lean/ResponseShape/Schemas/Discourse.lean`) and
  `runCaseReported_fits` covers it; `discourse_wire_acceptance` is proved with its right disjunct. The relay
  (`ve/discourse.py`) types and binds the composed answer. Route tests, route cases and the saved byte-identity
  comparison are new. The relay reads Lean's `CheckerUnavailable:` code as `CheckerUnavailable` (`_error_of`), the
  text the composed path's step 4 (the document mode's check) gives for a content it cannot decide.
- **Cut to cmp-s4d (FOLLOW-UP):** S4-1 on the constitution part document (the acceptance: 15 norm units and
  `u0214.s02`), a rights-route fixture on the composed path, and the document report of a composed answer with
  unit statuses (14.7; DRI 2026-11-04 item 3: the source of those statuses is a spec question first). Reason: size
  (below).
- **Depends on cmp-s4ab (not merged):** fenced content stays `NotImplemented: fenced content on the chain`.
- **Trust:** trusted +76, K +0 (R16's cap 150). SIGNED by standing ruling R16.

## Review fixes: F1 and F2

F1: `bind_composed` now compares each report claim with the request graph node's complete copied
identity (`name`, `ast`, and the optional `label`), using the schema comparator's JSON equality.
Both the root and every assumption are checked. The F1 probe failed before the fix and passed
after it. `test_f1_copied_claim_is_bound_to_its_complete_graph_node` covers all four fields on
the norms, norm-defaults and soft composed routes; `test_f1_default_label_is_omitted_from_both_copies`
covers the canonical default. A seeded name-only binder made the root-label case fail, then was restored.

F2: the kinds check reads the shared document `_parts` traversal, whose MIXED parent is provenance
and whose children are the units sent to the chain route. The F2 probe failed before the fix and
passed after it. `test_f2_mixed_parent_passes_binding_on_each_available_chain` covers norms,
norm-defaults and soft. A seeded parent-plus-parts traversal made its norms case fail, then was
restored. No Lean or Rust product code changed; these findings are in Python's response binding.

The three failures listed in `/home/seyran/code/manage-agents/main-known-red.txt` are pre-existing
on main and were not edited in this branch. The full gate belongs to the merge train for this item.

## Deliverables (task cmp-s4c)

| Task row | Delivered | Evidence |
|---|---|---|
| (1) route entry: the composed path only on `norms@0` + `ve.discourse@1` + a chain construct; every other input as today, byte for byte; the three `NotImplemented: <kind> on the chain` kinds | yes | `Run.lean` `chainCase`, `runCase`; `discourse_wire_acceptance` (both disjuncts); `ComposeExamples.lean` route checks; `test_answers_are_byte_identical_to_mains` (18 saved cases); `test_s4_27_other_kinds_on_the_chain_are_abstentions` |
| (2) relay and schema, binding only (R8), fuzz tests | yes | `ve/discourse.py` `_composed_answer` (typing), `bind_composed` (references, flattened kinds, complete copied report claims); `discourse.json` `composed`, `chain_admission`; `test_every_mutant_is_refused` (each member dropped and retyped, `inner`'s members dropped and retyped, the bound arrays duplicated and reordered, a foreign root, claim and reference); `test_f1_copied_claim_is_bound_to_its_complete_graph_node`, `test_f2_mixed_parent_passes_binding_on_each_available_chain`; `test_the_relay_returns_leans_answer_unchanged` |
| (3) chain decoders of 14.5 step 1 (soft, rights, norm-defaults) | yes | `chainEnvironment`: norms, norm-defaults (`decodeEnvironmentU`), soft (`Phases.checkSource` without rules), rights (`decodeRightsEnvironment`); a list no chain route reads is `dispatchAdmission`'s refusal (S4-16, S4-17) |
| (3) 14.6 three-way agreement | yes | `test_three_way_ve_discourse_beside_the_chain` (the profile table `ve/profiles.py` reads admits `ve.discourse@1` beside norms, norm-defaults and soft; Lean's route answers a composed row; the row fits `discourse.json`), `test_three_way_ve_discourse_refusals_agree` (the table's refusal texts are Lean's answers). `ve/profiles.py` is unchanged: its table is Lean's (`tools/profile_table.py`) and already agrees |
| (4) route fixtures S4-14, S4-16, S4-17, S4-18, S4-27, S4-28 | yes | `tests/test_discourse_composed_route.py`; 18 route cases appended to `tests/data/route-cases.jsonl` (recorded with `tests/route_case_recorder.py`) |
| (4) S4-1 on a part document of the constitution | **cut to cmp-s4d** | the synthetic S4-1 (norms route) is cmp-s4's guard and `test_norm_content_is_answered_on_the_composed_path` |
| (4) saved byte-identity comparison S4-2 (share), S4-3, S4-25, S4-28 | yes | `byte-identity.json`: each case's answer by main's `ve_service` (merge base `5c6a54444`, pinned in `lean/checkers.lock`), recorded by `record_byte_identity.py`; S4-2's share is every discourse case recorded from the suite before this item (15) |
| every value read once, charged against a stated limit, cmp-s4's `large` through the route | yes | below |

## The route entry (14.6)

`runCase` reads the case's id and kind, loads it (`loadCase`) and reads the profiles once; then
`"norms@0" ∈ profiles ∧ "ve.discourse@1" ∈ profiles ∧ chainConstructs environment document` (evaluated once) decides
the path. On it, `chainCase`: `admission` is `encodeComposed id` of `admitChain` (the body `admitComposed` runs on
that path, so `ComposedAdmissionAnswer` holds by `admitComposed`'s definition); `discourse-validity`,
`discourse-resolve` and `discourse-joint` are `NotImplemented: <kind> on the chain`; any other kind is today's
`UnsupportedProfile: case kind <kind> is not available on the discourse route`. Off it, the code is today's,
unchanged. `encodeComposed` is now `Route.Wire.ok id (composedFields c)` (`composedJson` is `Json.mkObj
(composedFields c)`): the same members, so the fits tactic reads it.

Readings:
- **Step 1's family check** is the chain route's own environment decoder (each checks the FOL family); the
  envelope checks of 3.5 (1) (`envelopeChecks`, split out of `wrapperOk`, which now appends today's frozen-gate
  check to them) run first with today's texts. A list `dispatch` sends to no chain route is
  `dispatchAdmission`'s refusal, read through `dispatchAdmission` itself (no copy of its texts).
- **The composed row's `inner`** is typed by a shape of its own (`chain_admission`), not the chain routes'
  `admission` shapes: those check against their own request (`/id`, `/document/graph/root`, the request's unit
  kinds), which a discourse case does not carry. Its `kinds` are `copied` (chainDocument copies each unit's kind);
  the relay binds them to the document.
- **The document report** (`ve document check`) of a composed answer is `CheckerUnavailable` (exit 5): 14.7 says
  unit statuses are the chain route's, and the chain routes' admission answers carry none; Python shows none of its
  own (DRI 2026-11-04 item 1).

## Evaluation cost (feature feed, evaluators and runners)

On the route each value is read once: the profiles and `chainConstructs` in `runCase`; on the path, the base
environment decoded once by `chainEnvironment` and handed to `chainBaseWith` (step 3), then cmp-s4's single reads
(`tests/test_cmp_s4_evaluate_once.py`, extended: `chainEnvironment` once on the path, `chainBase` no longer called by
`admitChain`). The limit is cmp-s4's: the chain document is charged against `Loader.maxDocumentBytes` (4,000,000
bytes) before the chain route reads it (`ResourceLimit: chain document bytes`). `fuelBudget` (5) bounds the nesting
of imported documents, which today's admission reads only for validity claims; the composed path refuses validity
claims by name (step 1), so it reads no other document and spends no fuel. Fixture: cmp-s4's `large` (200 norm units)
through the route ends within the limit (`test_large_document_ends_within_the_chain_document_limit`).

## Size

`git diff --numstat $(git merge-base HEAD main)`, hand-written (generated tables, `discourse.json` and the saved
`byte-identity.json` excluded): +941/-63 lines (the route tests 322, `mutants.json` 104, the allow file 63, the route
cases 18, the recorder 30; Lean +297/-52; `ve/discourse.py` +40; `tools/trust-classes.json` +15), and this report and
DELTA.md. Over the ~600 guide by about 400, in the evidence the task and the DRI's
conditions require (the route tests, the relay mutants, the saved comparison's recorder, the mutant checks, this
report). Cut: S4-1 on the constitution part, a rights fixture and the composed document report (cmp-s4d).

## Seeded bugs (each alone, then restored)

Each planted alone, the check named failing, then restored (`mutants.json`). Lean:

| Bug (file) | Fails |
|---|---|
| the `ve.discourse@1` check dropped from the route entry, S4-28 changes (`lean/VE/Discourse/Run.lean`) | the proof `discourse_wire_acceptance` (`Run.lean:223`); with it cut to `sorry`, the route check's S4-28 conjunct (`ComposeExamples.lean:245`) |
| `readings@1` beside `norms@0` accepted, S4-16 (`lean/VE/Discourse/Compose.lean` `dispatchAdmission`) | `ComposeExamples.lean:245` (its S4-16 conjunct) |
| a soft coherence premise dropped from `conditional_on` on the route, S4-18 (`Run.lean` `encodeComposed`) | `ComposeExamples.lean:178` (`encodeComposed` keeps `inner`'s `conditional_on`); the proof `composed_fits` (`ResponseShape/Encoders/Discourse.lean:264`) |
| step 1's soft, norm-defaults and rights lists each read by another decoder (`Compose.lean` `chainEnvironment`, three bugs) | `ComposeExamples.lean:245` (its soft, norm-defaults and rights conjuncts) |
| the chain route's environment id over the wrong profile list (`Compose.lean` `chainBaseWith`) | `ComposeExamples.lean:280` |

Python (`ve/discourse.py`):

| Bug | Fails |
|---|---|
| the relay rewrites a Lean answer field (`report_id := inner_report_id`, `lean_admission`) | `test_the_relay_returns_leans_answer_unchanged` |
| the chain route's kinds not bound (`bind_composed`) | `test_every_mutant_is_refused[drop inner.kinds]`, `[retype inner.kinds 0..8]`, `[duplicate kinds]`, `[reorder kinds]` (12 failed) |
| Lean's `CheckerUnavailable` code read as a plain error (`_error_of`) | `tests/test_discourse_constitution.py::test_norm_content_is_read_on_the_composed_path` |

No Rust code changed.

Trust mutants (one or more per new trusted definition): `zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --allow
docs/composition/cmp-s4c/trust-mutants-allow.json --rescore docs/composition/cmp-s4c/trust-mutants.json --json
docs/composition/cmp-s4c/trust-mutants.json` on `7a87e0ac1` (the final Lean tree; cloud pool, 630 s): exit 0, "KILLED 134,
SURVIVOR 0, UNKNOWN 0, INVALID 29, ALLOWED 16" over the 11 definitions it selects (`chainAdmission` 40 killed,
`chain_admission` 9, `composed` 31, `file` 8, `row` 21, `chainCase` 7, `runCase` 5, `composedFields` 8,
`envelopeChecks` 1, `wrapperOk` 4; `chainEnvironment`'s 10 mechanical mutants do not compile or are allowed, so its
three branch bugs above are planted by hand, as is `chainBaseWith`'s, which the tool does not select: its body is
cmp-s4's `chainBase` lines). Each allowed mutant has its reason in the allow file (type errors the tool reads as
UNKNOWN, a stuck universe constraint, an unreachable branch, and `Option.toList` cuts that are the list itself).
Two lessons for the probe: a check that runs the route reaches every route (1 m 45 s to probe one), so the route
checks are two combined `#guard`s; and a check that reads `postOk` (today's admission) cannot kill an
`envelopeChecks` mutant, so step 1's order is checked through `admitChain`.

## Trust

`uv run python tools/trust_map.py --check` on the final tree: "PASS: K, S and untied [V] within 5c6a544446dc and the
allowances introduced since"; against the merge base: K +0, S +0, trusted +76 (`ResponseShape/Schemas/Discourse.lean`
+36, `VE/Discourse/Compose.lean` +24, `VE/Discourse/Run.lean` +12, `VE/Discourse/Admission.lean` +4). Recorded with
`trust_map.py --allow --reason "cmp-s4c: ..." --signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), cmp-s4c,
2026-10-18"`; the FOLLOW-UPS row is under "## cmp-s4c" in `manage-agents/FOLLOW-UPS.md` (ties pass). New
declarations are classified in `tools/trust-classes.json` (no unclassified line).

## Tests

- `cd lean && lake build`: "Build completed successfully (1279 jobs)"; `python3 lean/audit.py`: "PASS: 763 source
  files; 8399 named theorem declarations audited ... only the declared standard axiom allowlist".
- `uv run python tools/regen_generated.py --write`, then `--check` on `8223762d8`: "checked 35 entries".
- `uv run pytest -q tests/test_discourse_composed_route.py`: "147 passed".
- Selected tests (`zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`): the first run (fast stage,
  312 of 446 units) failed `tests/test_discourse_constitution.py::test_norm_content_abstains`, which pinned the old
  `NotImplemented: norm content` abstention; renamed `test_norm_content_is_read_on_the_composed_path` (trailer
  `Test-removed`, DRI 2026-11-04 cmp-s4c-norm item 1), with the relay's `CheckerUnavailable` mapping. The second run,
  on the fix (461 units, 6 shards): 459 passed, 2 failed: `test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`
  (the schema module's new JSON-reading `#guard`s; classified in `ve/assurance-manifest.json`) and
  `test_consolidation_tools.py::test_committed_ledger_names_real_declarations` (step 7's measure of `runCase`, 729 to
  732; the ledger row of `docs/CONSOLIDATION-PLAN.md` updated, as at-1w did). Rerun of those ids and the renamed test
  (`zsh mac-pytest.sh -- <3 ids>`): "3 passed".
- `uv run python tools/gate_collection.py --check --prebuilt`: "148 added, 1 removed by a trailer, 0 refused, 0 stale
  and 0 malformed trailers".
- None of the failures is in `main-known-red.txt`.

## Next items

- FOLLOW-UP: cmp-s4d, S4-1 on the constitution part through the route, a rights fixture on the composed path, and
  the composed path's document report with unit statuses (14.7; DRI 2026-11-04 item 3).
- cmp-s4ab (14.3 fences; then fenced content's route fixtures), cmp-s4b (OPEN 4), pc-s4-positions, then pc-7b.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: PASS, the composed row's shape (`composed`, `chain_admission`, `runCaseReported_fits`); the relay's fuzz `test_every_mutant_is_refused` (each member and `inner`'s dropped and retyped to 7, 1, true, null, [], {}, 1.5, a lone surrogate and a 10,000-deep list; arrays duplicated and reordered; a foreign root, claim and reference): all `CheckerUnavailable`.
2. Every deliverable built or ruled: PASS, the deliverables table; the cut (S4-1 on the constitution part, a rights fixture, the composed report) is cmp-s4d by the size rule (DRI 2026-11-04 item 3 files it); no Python copy of a Lean decision (`ve/profiles.py` unchanged: its table is Lean's), no report test, no in-flight overlap but `tests/data/route-cases.jsonl` (feature/df-5, append-only).
3. Tests can fail: PASS, `mutants.json` (12 planted bugs, each killed) and `trust-mutants.json` (exit 0, allow file with one reason per entry).
4. Python, Lean and Rust agree: PASS, `test_answers_are_byte_identical_to_mains` (main's service against this branch's on 18 cases); `test_three_way_ve_discourse_beside_the_chain`, `test_three_way_ve_discourse_refusals_agree`; no Rust change.
5. R8 binding: PASS, `bind_composed` (references to the mentions, kinds to the units and parts, report claims to the graph); `test_every_mutant_is_refused` ("extra reference", "foreign root", "foreign claim", duplicated and reordered kinds).
6. Gate evidence on the final HEAD: PASS, the chain runs the gate on the final HEAD; the trust mutants ran on `7a87e0ac1`, whose Lean tree is the final one.
7. No unsigned item: PASS, every DELTA row cites a DRI decision file or R2; trust growth signed under R16.
8. Every user-visible change in DELTA: PASS, the route (row 1), the CLI's CheckerUnavailable for an admitted composed document (row 2) and for an undecidable norm object (row 3), the fault order (row 4); off the path no change (the saved comparison).
9. Test selection: PASS, the selection chose 461 units, not every unit, and contained both tests that failed.
10. Statements say what is claimed: PASS, `discourse_wire_acceptance` and `composed_fits` broke on the seeded route-entry and `conditional_on` bugs; cmp-s4's 14.4 to 14.6 statements unchanged (`lean/statements.txt`).
11. Budgets fail closed: PASS, the chain document's byte limit before the chain route (`ResourceLimit: chain document bytes`, cmp-s4); `test_large_document_ends_within_the_chain_document_limit`; no fuel spent on the path (no imported document is read).
12. No CPU or memory regression: N.A., off the composed path `runCase` adds one profile test (and `chainConstructs`, a front-matter scan, only on lists with both profiles); the composed path is new.
13. `Test-removed` trailers: PASS, `gate_collection.py --check --prebuilt` (1 removed by a trailer, 0 refused, stale or malformed).
14. Both directions, cited evidence, spec re-read: PASS, accepting and refusing norm content (`test_norm_content_is_answered_on_the_composed_path`, `test_norm_content_the_chain_route_rejects_is_refused`), lists beside the chain admitted and refused (the two three-way tests), the genuine answer bound and its mutants refused; spec re-read: 14.1 (scope, `docs/spec/discourse.md:2053`), 14.5 steps 1 to 7 (:2399-2412), 14.6's wire entry (:2486-2497) and three-way agreement (:2507-2510), 14.7 (:2514), 14.8 rows S4-14 to S4-28 (:2544-2558).
