# sn-b6 REPORT: senses B6, the service and relay (first part)

Status: built, cut at the size line; no DRI signature is needed (DELTA rows R3, R16). HEAD: see `git log -1`.
What changed: `senses.project` is a `ve_service` mode (Lean case, shape, encoder theorem, schema, relay with
fuzz tests); `senses.read` answers carry the identities of their projection and each candidate's (i1, i7).
Open: the senses lock (`ve/senses/LOCK.json`, D17 hook rule), the CLI, i3 to i5, flip models and a typed
projected environment go to sn-b6b. Hand-written lines: 1,066 added (over the ~600 line; see Size).

## Plan rows (docs/spec/senses-PLAN.md 836, 877-881, 1069-1075) and the edits

The DRI's synthesis edit 1 (edits-senses.md, D7: senses runs as `ve_senses_route`, no profile) governs where the
modes live: `senses.read` stays on `ve_senses_route` (the plan row's `ve_english_route` is replaced by the edit).
`senses.project` is a `ve_service` mode, as `docs/ROUTE-RECIPE.md` requires for a shape, an encoder theorem and
a generated schema (`tools/repo_map.py --check` ties schema files to service modes); no profile and no AR-10
row are added.

| Plan item | Delivered | Where | Test |
|---|---|---|---|
| `senses.read` response: S2's six identities of the projection, `dictionary_id`, `senses_version` | yes (overlay_digest absent; `source_sha256` for a source request only: a fence request has no single source, see Deviations) | `lean/VE/Senses/Run.lean` `admittedIds`, `projectionIds` | `tests/test_senses_project.py::test_i1_reading_identities_are_its_projections` |
| each candidate's resolving lines and its projection's identities | yes | `admittedIds` (one projection per distinct lines, `linesProjection`) | `::test_i7_candidate_projection_identities` |
| units, candidates, sense map, mixed, unused, environment, code and text | already on main (B5, RD-8) | | `tests/test_senses_route.py` |
| flip models | no: B5 built none (`grep -n flip lean/VE/Senses` is empty) | sn-b6b | |
| the preamble lines as a member | no (the candidates' `lines` and the source carry them) | sn-b6b | |
| request `mode`, `cap` | no: the cap is Lean's `candidateCap` (8), the budget is the request's | | |
| `senses.project` request (environment, lexicon, packs, own, lines, used) and response (projected environment JSON and identities) | yes, plus the projected lexicon (B7 re-reads under it) | `projectCase`, `lean/ResponseShape/Schemas/SensesProject.lean`, `Encoders/SensesProject.lean` (`projectCaseReported_fits`) | `::test_i7_…`, `::test_a_fault_of_the_lines_is_leans`, `::test_lean_refuses_a_request_with_its_text` |
| null fields omitted | yes (absent members are left out: no `source_sha256` on a fence request, no `identities` on a refusal) | | `::test_projection_answer_mutations_are_rejected` |
| `ve/senses/LOCK.json`, `sensesVersion`, hook rule (D17) | `sensesVersion` only; lock and hook moved to **sn-b6b** (size line) | `lean/VE/Senses/Version.lean` | |
| manifest: `senses.read`, `senses.project`, `authority: lean`, no `python` entry, decoders pinned | yes (`lean-only` is the manifest's name for that authority); `Run.lean` re-pinned whole | `ve/assurance-manifest.json` | `::test_i6_both_operations_are_lean_only`, `tests/test_assurance_manifest.py` |
| `ve/backends/senses.py` relay: Lean's code and text verbatim, `CheckerUnavailable` for operational faults, R8 binding | yes | `project`, `_projection_problem`, `_identities_problem` | the fuzz tests below |
| CLI `ve check --surface english --senses PACK` | no: review Fable B1 (`tests/test_senses_route.py::test_only_senses_check_reads_with_senses`) keeps `ve check` without `--senses`; `ve senses check` is the entry | | |
| CLI `ve senses project` | **sn-b6b** | | |
| i1 | yes | | `::test_i1_…` |
| i2 | yes | | `::test_i2_the_same_request_twice_is_byte_identical` |
| i3 (no packs and no own senses refused) | no: review Astra B on main reads an empty dictionary through Lean (`test_own_senses_need_no_pack`, status `none`); changing it is a verdict change for the DRI. **sn-b6b** asks | | |
| i4 (`review_status` of a pack whose bytes differ) | **sn-b6b** (`ve.senses.review_status` exists on main; no display reads it yet) | | |
| i5 (service killed mid-request) | **sn-b6b** | | |
| i6 | yes | | `::test_i6_…` |
| i7 | yes | | `::test_i7_…` |
| evaluated once, against stated limits, a large well-formed request | yes: each candidate projection once per distinct lines; 120 preamble lines over 120 used words (240 of `maxPredicates` 256) answers, 130 words is `VocabularyLimit` | | `::test_a_large_request_is_read_once_within_the_predicate_limit` |
| no Python decision site, no Python text | yes | | `uv run python tools/relay_lint.py`: "PASS: … 3 senses module(s), no English reader" |
| the request's lexicon from the `english.read` adapter's export | yes (`ve.backends.senses.request`, unchanged) | | |

## Deviations

- `source_sha256` is given for a source request only; a fence request reads a document's fences, whose
  document identity is the document mode's.
- The projected environment is an open object in `senses.project.json`; the relay reads it whole as an
  `Environment` and binds its `environment_id` and the lexicon's to it. Typing it is sn-b6b
  (`tests/test_route_row_schemas.py` OPEN_ALLOWED; `tools/relay-gate-allow.json` F7).
- `readCase` adds identities only when the `senses.read` runner asks (`identified`), so the document mode's call
  in `lean/VE/Service/Document.lean` (in flight elsewhere, not edited) does no extra work and answers as before.

## Seeded bugs (docs/senses/sn-b6/mutants.json)

| Id | File | Bug | Failing test or check |
|---|---|---|---|
| P1 | `ve/backends/senses.py` | reading `environment_id` binding disabled | `tests/test_senses_project.py::test_reading_identity_rebinding_is_refused` |
| P2 | `ve/backends/senses.py` | projection `lexicon_id` binding disabled | `tests/test_senses_project.py::test_projection_answer_mutations_are_rejected` |
| P3 | `ve/backends/senses.py` | used words not bound to the dictionary | `tests/test_senses_project.py::test_reading_identity_rebinding_is_refused` |
| P4 | `ve/backends/lean_service.py` | `senses.project` back on `_CORE` (review F1) | `tests/test_senses_project.py::test_a_projection_is_as_available_as_the_reading_it_serves`, `::test_the_large_request_is_answered_within_half_its_deadline` |
| L1 | `lean/VE/Senses/Run.lean` | candidates given the reading's own identities | `#guard` pins, `lean/VE/Senses/RunExamples.lean` (lake build fails) |
| L2 | `lean/VE/Senses/Run.lean` | a non-preamble line accepted | `#guard`, `lean/VE/Senses/RunExamples.lean` |
| L3 | `lean/VE/Senses/Run.lean` | projection status `BOGUS` | `ResponseShape.Encoders.SensesProject.projectCase_fits` |

Each was planted, the named test or build failed (commands and outputs in mutants.json `result`), and the file
was restored (`git diff --stat` empty after each). P3 first survived; `used = [funny, giggle]` was added.

## Trust (R16)

`uv run python tools/trust_map.py --check`: K +0, S +0, trusted +73 over `0c4ea31d2` (`VE/Senses/Run.lean`
+69, Registry, Protocol, Skeletons, Schemas +1 each); allowance recorded in `docs/trust-baseline.json` with
"SIGNED by standing ruling R16 (DRI-RULINGS.md), sn-b6, 2026-10-31"; FOLLOW-UPS.md "## sn-b6" asks for the
ties pass. Trust mutants (`mac-pytest.sh --trustmut -- --max-mutants 1000 --allow
docs/senses/sn-b6/trust-mutants-allow.json --json docs/senses/sn-b6/trust-mutants.json`, exit 0): 213
killed, 0 survivors, 0 unknown, 28 invalid, 27 allowed (22 that do not type-check; 5 equivalent: `take 1` of an
`Option.toList` or of a one-element list, `(lines.take 1).isEmpty`); per definition in mutants.json. The last
run is a full one on the clean `388f6b4a4` ("ran on ve-mac-1 … HEAD 388f6b4a (clean) … exit=0"); the commits
after it change docs and evidence only.

## Gates run

- `lake build` (full) and `python3 lean/audit.py`: "PASS: 688 source files; 7635 named theorem declarations".
- `uv run python tools/regen_generated.py --write`: exit 0.
- `uv run python tools/relay_mutation_gate.py --route service:senses.project --route ve_senses_route::senses.read`:
  "2 routes, 1641 mutants, 0 failures".
- `uv run python tools/trust_map.py --check`: exit 0 after the allowance.
- `uv run python tools/gate_collection.py --check --prebuilt`: "18 added, 0 removed by a trailer, 0 refused, 0
  stale and 0 malformed trailers".
- `uv run python tools/relay_lint.py`: PASS.
- Selected tests, `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`: run 1 (`1a68858a4`)
  failed on the runner-fixture layer, the identity site, the senses.project seed, census answers and open
  object; fixed in `53cb75dfc`. Run 2 (`53cb75dfc`, 508 units on ve-mac-1): 4 failed, all in
  `tests/test_assurance_manifest.py` (budget class, fixture classification, literal operation, probe); fixed in
  `388f6b4a4`; the 4 ids with `tests/test_senses_project.py`, `test_senses_route.py`, `test_senses_document.py`
  rerun through `mac-pytest.sh -- <ids>`: "181 passed" (ran on the VM: no Mac slot).
- Not run: the full gate (the chain runs it on the final HEAD). No test of main-known-red.txt failed.

## Size

`git diff --numstat $(git merge-base HEAD main) HEAD` without generated files: 1,066 added, 61 deleted. The
senses lock (about 230 lines with its test and hook) was cut to sn-b6b at the first measurement (923). What
grew after the cut is evidence the gates require: the runner `#guard`s that kill the trust mutants
(`RunExamples.lean` 165), the relay and trust-mutant allow lists (155) and trust classes (47).

## Pilot bytes

None expected: no pilot document uses senses yet (B8 measures the use cases).

## Spec re-read

- senses-PLAN.md:836 (B6 row): every request and response member checked against the table above.
- senses-PLAN.md:357-360 (candidate identities `environment_id`, `lexicon_id`, `grammar_id` of
  `project D (A.extend choice) E L used`): `linesProjection` reads the candidate's `lines`
  (`Assignment.lines D (A.extend choice)`) over the reading's used words.
- senses-PLAN.md:371-379 (identities; `overlay_digest` absent; `senses_version`): as delivered, lock moved.
- senses-PLAN.md:877-881 (B6 done-when): i7 and the manifest test pass; `ve check --senses` superseded by review
  Fable B1.
- senses-PLAN.md:1069-1075 (i1 to i7): i1, i2, i6, i7 tested; i3 to i5 sn-b6b.

## Review fix (sn-b6-review.final.md)

F1 (B), the `senses.project` CPU deadline: the mode had the core modes' 5 s per case plus 30 s per MiB (6.4 s for
the 46 KB large request), and its 260-sense pack costs 3.7 s to 6.5 s of CPU in the shared dictionary decode and
checks, roughly the square of the pack's size. The class is a projection less available than the reading it
serves. Fix: one constant, `_SENSES` (120 s plus 120 s per MiB) in `ve/backends/lean_service.py`, is the deadline
of both the document mode, which reads senses, and `senses.project`; it is never below `senses.read`'s 120 s route
timeout. It is not a DELTA row: the mode is new over the base. Regression tests:
`tests/test_senses_project.py::test_a_projection_is_as_available_as_the_reading_it_serves` (equal to the
document mode's and at least the route timeout at sizes 0 to 8 MiB) and
`::test_the_large_request_is_answered_within_half_its_deadline` (the review's probe: the large request under half
the deadline). The probe failed before the fix ("used more than its deadline of 3.18421 s of CPU", load 63) and
passes after it; seeded bug P4. The quadratic cost of the pack decode itself is not changed here (it is shared
with `senses.read` on main). Run on `b5a1c261d`: the selection (`mac-pytest.sh --select`, 508 units on ve-mac-1,
exit 0, 0 failed), `lake build`, `python3 lean/audit.py` (PASS: 688 source files), `regen_generated.py --check`,
`gate_collection.py --check --prebuilt` (20 added, 0 removed) and `repo_map.py --check`. Not run: the full gate.

## Next

sn-b7 (display) can call `ve.backends.senses.project` for a candidate's lines; sn-b6b first.

## Self-review against BUILDER-CHECKLIST

1. PASS: fully typed and contained: `senses.project.json` closed per fault code (the environment listed open, F7,
   sn-b6b); `test_projection_answer_mutations_are_rejected` (drop, retype, 1.5, rebind) and
   `test_the_lean_decoder_refuses_each_retyped_member`; `relay_mutation_gate.py` 0 failures.
2. PASS: every plan row in the table above with its commit, test or the item that takes it (sn-b6b); no Python
   copy of a Lean decision (`relay_lint.py` PASS); in-flight files (`Standalone.lean`, `Document.lean`) untouched.
3. PASS: seeded bugs P1-P3, L1-L3; trust mutants 0 survivors (`docs/senses/sn-b6/trust-mutants.json`).
4. PASS: one implementation (Lean); Python and the Lean guards agree on the same requests
   (`test_i7_candidate_projection_identities`, `RunExamples.lean` pins); legitimately empty lines and used words
   (`test_a_fault_of_the_lines_is_leans`, `idsOf ""` guard).
5. PASS: `test_reading_identity_rebinding_is_refused` (undeclared word, duplicate, empty, extra member),
   `test_lean_refuses_a_request_with_its_text` (undeclared used word, duplicate).
6. PASS: evidence from the committed HEAD's runs above; the chain runs the full gate.
7. PASS: DELTA rows cite R3 and R16; no signature reserved.
8. PASS: DELTA.md (the senses.read members); the document mode's answer pinned unchanged.
9. PASS: the selection ran `tests/test_senses_project.py` and `test_senses_route.py` (run 2 log); seeded P1-P3
   fail in them.
10. PASS: L3 (a `BOGUS` status breaks `projectCase_fits`); no approved statement changed.
11. PASS: `test_budget_zero_never_projects`; `tests/test_senses_route.py::test_zero_budget_never_admits`.
12. PASS: one projection per distinct candidate lines (`admittedIds`); the document mode's call does no
    identity work (`identified`); large request `test_a_large_request_is_read_once_within_the_predicate_limit`.
13. N.A.: no test removed or renamed (`gate_collection.py --check`: 0 removed).
14. PASS: opposite directions (accepted genuine answers and refused mutants in every fuzz test; the large
    request answered and the one past the limit refused); spec re-read list above; each claim cites its command.

FOLLOW-UP: sn-b6b senses lock and hook rule (D17), `ve senses project`, i3 (DRI), i4, i5, flip models, typed projected environment
