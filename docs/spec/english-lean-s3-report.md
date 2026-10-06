# English in Lean S3: Python profile report

Status: **integrated fixture slice passed with the two spec dispositions; G3 and GE2 remain open**. This
report joins the Python and Lean branches on `english-lean-s3/integrate`. It does not claim an authority flip.
The committed case records are in `conformance/english-lean/s3-python-report.json` and
`conformance/english-lean/s3-fixture-comparison.json`. Every number below is derived from their rows.

## Completed work

| Item | Result | Evidence |
|---|---|---|
| S3.0, profile tables | The 25 `order@0` and 8 `alternatives@0` rows, staged catalogue, certificate, lock, and generated modules are committed. The base table source is unchanged. | `c88ae554`; `tools/english_grammar_gen.py --check`; `tests/test_english_lean_s3.py` |
| S3.1, Python wording | `risk__more_severe` reads and renders as `{0} is more severe than {1}`. The real fixture environment JSON and malformed profile and unit declarations have Python boundary tests. | `53341bf1`, `cba916cc`; `tests/test_english_lean_s3.py` |
| S3.5, Python fixture outcomes | Python's dispatched reading was run on all 163 spec fixtures. The comparison now also sends the exact text and Python's selected wording to Lean, validates each answer through the existing adapter, and saves each comparison record. | `8b605c26`, `6e149b06`; `tests/test_english_lean_s3_compare.py` |
| Gate bookkeeping | The comparison report is registered as an artifact. The S3.0 change to `Run.lean` is reflected in the reviewed whole-file pin, decoder total, and generated assurance table. | `ca0335ea`, `016ab982`; `tests/test_assurance_manifest.py` |

No Rust implementation is named by the S3 statement spec or plan. The generic Rust suite remains a gate.

## Measured fixture differences

Python agrees with the spec's mapped class, formulas, and marks on 147 of the 163 exact texts. All 16 exact-text
differences agree when written with Python's selected wording. Python selects the quoted fallback for `safe`
under `FA` and `FR`, because its declared `{0} is safe` collides with the fixed role wording; it selects `C`
instead of `A` as the action letter under `FA`. These are findings against the hand-written spec lexicons,
not hidden fixture passes. The two `or38` resource-limit outcomes are the agreed class difference in spec 2.11.

The integrated fixture comparison has 200 cases, including 37 selected-wording variants. It records 198 agreements
and 2 differences, both dispositioned, with zero unexplained differences. The hand parser and Lark
were run independently for each case; their grammatical verdicts are saved beside the dispatched Python and
Lean results in each case record. The two differences are `or38a` and `or38b`, exactly the mixed-fault depth
precedence of spec 2.11/Q11: Python returns `ResourceLimit` and Lean returns `NoDerivation`.

| Environment | Cases | Agree | Differ | Current Lean result |
|---|---:|---:|---:|---|
| `FO` | 57 | 55 | 2 | `or38a`, `or38b` dispositioned |
| `FO+cap` | 3 | 3 | 0 | Same outcomes |
| `FD` | 24 | 24 | 0 | Same outcomes |
| `FA` | 68 | 68 | 0 | Same outcomes |
| `FA2` | 8 | 8 | 0 | Same outcomes |
| `FR` | 35 | 35 | 0 | Same outcomes |
| `FM` | 5 | 5 | 0 | Same outcomes |

The comparison is the fixture slice of G3. It is not the sealed 57,765-text core comparison, the reverse
grammar corpus, the lexicon mutation replay, the use-case and pilot seal, or a latency measurement. G3 and
GE2 remain open. `python -m conformance.english_lean_seal --check` reports 16 source/registry drift findings,
so the old seal is not a valid basis for G3. The `english.admission` authority is still Python and no E2 flip
was attempted.

## Verification and seeded bugs

`lake build` completed. The clean-HEAD gates on `6e149b06` and `ca0335ea` ran the Lean audit, 49 Rust tests,
and the full Python suite; each found two bookkeeping failures, fixed by the subsequent commits above.
After the final report commit, run `python3 tools/gate.py --workers 16` on clean HEAD. Its result belongs in
the handoff, not in a claim made before the run.

Three temporary mutations to `conformance/english_lean_s3_compare.py` each failed a targeted test and were
removed:

1. Accept an empty corpus: `test_comparison_refuses_an_empty_corpus` failed because no `ValueError` was raised.
2. Clear comparison difference classes: `test_comparison_detects_an_accepted_sentence_changed_to_no_reading`
   failed because it counted two agreements instead of one.
3. Ignore the response ID: `test_comparison_rejects_a_response_for_a_different_request` failed because the
   mismatched answer was accepted as `none` instead of unavailable.

The restored comparison tests pass. `test_committed_report_counts_are_derived_from_individual_records`
recomputes every summary count from the committed records.

## Acceptance ownership

| Item | Tag | Status and owner |
|---|---|---|
| S3.0 rows and Python wording | AGENT | Done in this branch; Python implementer |
| S3.5 full G2/G3 corpus, reverse, mutation, and latency gates | AGENT | Open; Python implementer after the Lean S3 reader and service are available |
| S3.1–S3.4 and E2.0–E2.2 Lean reader, proofs, service, and V6 | AGENT | Outside this Python worktree; Lean implementer |
| DRI disposition of any verdict or availability delta | HUMAN | Deferred; DRI |
| Pilot and sealed corpus inputs needed for GE2 | EXTERNAL | Deferred; corpus and pilot owners |

## Build checklist disposition

The numbers refer to `manage-agents/prompts/build-checklist.txt`. “Open” means this partial S3 branch does
not satisfy the line; it is not treated as an exception to the final G3 or GE2 gates.

| Line | Status | Evidence or reason |
|---:|---|---|
| 1 | Open | This comparator reuses the adapter's code/class map, but S3 diagnostic text and phase order await E2.2. |
| 2 | Open | Fixture Python/Lean comparison exists; full one- and two-fault corpus and a three-way S3 route do not. Rust has no S3 route in the spec. |
| 3 | Open | Exhaustive normalization variants across S3 entry points are not complete. |
| 4 | Done | The existing response validator checks fields, identities, counts, trees, and bool-for-int; adapter mutation tests and the new wrong-ID test exercise failure. |
| 5 | Not applicable | This branch adds no input decoder; it uses the existing Environment and route decoders. |
| 6 | Not applicable | The fixture comparator observes readings; it does not decide proof verdicts. |
| 7 | Done | The foreground comparison uses the route transport's configured whole-call timeout. |
| 8 | Not applicable | No kind or owner fold changes. |
| 9 | Open | The full S3 render/read/unique corpus cannot pass before the Lean rules and actions exist. |
| 10 | Open | E2.3's single `admit` relay has not been built. |
| 11 | Done | The comparator parses response JSON through the route library; no language/import syntax is matched by a new regex. |
| 12 | Not applicable | No state machine or ledger change. |
| 13 | Done | The three seeded mutations above each failed a targeted test and were removed. |
| 14 | Done | The gate supplies a hermetic environment; comparison writes a deterministic report, with no sleep or model call. |
| 15 | Done | Requests bind six identities; the existing response validator checks them and the comparator checks row IDs. |
| 16 | Open | Every spec fixture ID is covered and the gate collection and report artifact registry are updated, but the old corpus seal has 16 drift findings. |
| 17 | Not applicable | No theorem statement was changed in this Python worktree. |
| 18 | Not applicable | Lean theorem stubs and proofs are outside this worktree's task. |
| 19 | Not applicable | No use-case formalisation was changed. |
| 20 | Done | The report-count test regenerates numbers from the per-case JSON; no three-way S3 claim is made. |
| 21 | Done | The acceptance items above have AGENT, HUMAN, or EXTERNAL tags and deferred owners. |
| 22 | Open until handoff | All code and this report are committed before the final clean-HEAD gate; the handoff records its result and free disk space. |
