# Senses integration report

This report covers the local `senses/integrate` merge of `senses/py` and
`senses/lean`, and the new route that admits senses readings through the
compiled Lean reader. The shipped grammar follows the **as merged** column of
[senses.md](senses.md) section 8. R3 has no DRI ruling in this checkout. The fix round of 2026-10-06
(section "Review fix round" below) answers the integration reviews' A and B findings.

## Acceptance and ownership

| Item | Class | State and owner |
|---|---|---|
| Merge and conflict resolution | AGENT | Done. The frozen source inventory, audit declarations, trust classification, layer policy, and gate collection include both branches. |
| Fixture pack and Lean decoder | AGENT | Done. The fixture pack's `principal` and `resource` letters match the spec and Lean. `test_spec_pack_python_file_and_lean_fixture_agree` checks spec JSON, Python bytes, compiled Lean pack and dictionary identity. |
| Senses admission | AGENT | Done for `senses.read`, a `lean-only` operation of `ve/assurance-manifest.json`: `ve/backends/senses.py:read` calls `ve.backends.lean.run` under its binding (`ve_senses_route`, response `result`) and declared call site; `ve_senses_route` transports raw pack text to Lean's restricted decoder, calls `readWithSenses`, and returns the result with dictionary and full-request identities. The relay checks those identities and the response shape, including each unit's sentence and state and every refusal's arguments (spec 4.1 *as built*). A dictionary of own senses alone needs no pack. |
| CLI reading | AGENT | Done for `ve senses check` only: it is admission only, and its answer says so (`operation`, `assurance` from the manifest, `intent`, `proof` and `conclusions`: `not_checked`). `ve check` has no `--senses`, so its record contract (honesty fields, premises, conclusion check) is unchanged (`test_only_senses_check_reads_with_senses`, `test_senses_check_is_admission_only`). Human-readable diagnostic text and rendering are not present. |
| Fixture conformance, spec against Lean | AGENT | Not three-way: Rust has no senses code and Python only relays the Lean reader. Done for the fixture pack and s1, s3, s4, s5, s6, s7, s8, s9, s16, s17, s21, s22, s23, d3, n1, n2 and n3 in the as-merged column: `test_spec_reading_fixtures`, `test_every_refusal_carries_its_arguments` and `test_spec_fixtures_through_the_route_against_lean` compare the route's whole answer (formula, unresolved words, candidates, sentence, arguments) with the spec row that `VE.Senses.Examples` also guards (built once per module). The complete spec matrix is guarded in Lean only. |
| Full B6 service | AGENT | Open, owner senses integration: no `senses.project`, six S2 projection identities, `sensesVersion` lock, flip models, or Lean diagnostic text. The new one-shot executable is separate from `ve_english_route`. |
| B7 display and reading sets | AGENT | Open, owner senses integration: rendering, glossary, resolve, candidate re-read, and propose-readings are not implemented. |
| R3 and Q4 | HUMAN | Deferred to the senses DRI under spec sections 6.2 and 11. Until R3 is decided, the build ships the as-merged column, which is what spec 6.2 prescribes; that column keeps the comma forms (no c fixture is `many` there, so Q4's rule keeps them). |
| Four deferred statements | HUMAN | Deferred to the senses DRI for signatures under G-S1: `glossed_negative`, `lines_read`, `project_total`, `senseMap_ids`. They are `Prop` definitions, not theorems. |
| Draft 2 bounded re-review | EXTERNAL | Deferred to the statement reviewers under G-S0, which is not yet passed. Its evidence is complete: every row G-S0 lists as recomputed (d2, d26, j6, j13, j15, j16, j17, c16, c17, s22, s23, the R3 column where the spec gives it, and the hand-derived rows) is a `#guard` of `VE.Senses.Examples` that the build computes, and the thirteen statements equal the approved text. The pass is the reviewers' and the DRI's to record. |
| Trusted-base growth | HUMAN | The senses branch adds about 966 trusted lines, and this fix round S +45 and V +53 (`python3 tools/trust_map.py --since HEAD` before the fix commits); both need a DRI-signed entry in `docs/trust-baseline.json`. `--check` also fails on growth merged before this branch. |
| Starter packs and measurements | HUMAN / AGENT | Human reviewers own the pack pins; senses integration owns the subsequent use-case measurements. Neither is complete. |

## Review fix round (2026-10-06)

The A and B findings of `manage-agents/senses-review-astra.final.md` (with the DRI's added findings) and
`manage-agents/reviews/senses-review-fable.md`, each fixed as a class, with its regression test.

| Finding | Class removed | Fix | Regression | Commit |
|---|---|---|---|---|
| Astra A1: the cap built 2^n choices | a limit checked after the work it limits | `choiceCount` (capped product, `choiceCount_eq`) | `Examples.lean` A1 rows; `test_every_refusal_carries_its_arguments[a1-30-words]` | `6c40aa1c` |
| Fable B3: words inside a gloss counted as occurrences | two token scans that disagreed on what a gloss covers | one `unglossed`, read by `usedWords` and `unswitchedIn` (spec 2.6) | `Examples.lean` B3 rows (each fails on a mutant); `test_gloss_words_are_not_occurrences` | `6c40aa1c` |
| Astra B1, Fable B2: no unit state, no refusal arguments | an encoder that dropped fields of the Lean value | units with `sentence`, `referents`, `binder_seen`; `details` for every sense fault; S2's fields for S2's outcomes, compared with `ve_english_route` | `test_every_refusal_carries_its_arguments`, `test_s2_outcomes_match_the_english_route`, `test_spec_reading_fixtures[s1]` | `6c40aa1c`, `72971015`, `225a070f` |
| (found by the new tests) `invalidDictionary` was a nested pair, so every such answer was CheckerUnavailable | as above | a flat triple | `test_every_refusal_carries_its_arguments[d3]` | `6c40aa1c` |
| Fable B1: `ve check --senses` broke the check contract; an unregistered subprocess | a sibling entry point that bypasses the contract and the manifest guards | `senses.read` registered `lean-only` with a binding, probe and call site; transport through `ve.backends.lean.run`; `ve check --senses` removed; the widened guard test restored | `test_the_route_goes_through_the_manifest_binding`, `test_only_senses_check_reads_with_senses`, `test_only_the_backend_starts_processes`, `test_every_lean_binding_routes_its_operation` | `72971015` |
| Astra (added) A: `check` succeeded without checking marked conclusions | as above | `ve check --senses` removed; `ve senses check` is admission only and answers `conclusions: not_checked` | `test_senses_check_is_admission_only` | `72971015` |
| Astra (added) B: own senses alone refused by Python | a Python rule Lean does not have | the non-empty pack rule removed | `test_own_senses_need_no_pack` | `72971015` |
| Astra (added) B: impossible status and code pairs accepted | a validator that checked the code's shape, not its status | per-code status for sense faults; S2's validator for S2's codes | `test_impossible_status_code_pairs_are_rejected`, `test_genuine_response_field_mutations_are_rejected` | `72971015` |
| Fable B4: "three-way" overclaimed; Lean rebuilt per case | a claim with no third engine | renamed spec against Lean, Lean guards built once, whole answers compared (s22's candidate) | `test_spec_fixtures_through_the_route_against_lean` | `225a070f` |
| Astra B2: gates not recorded | items the agent cannot close | the as-merged ruling of 6.2, G-S0's evidence, G-S1 and the trusted-base growth recorded above as HUMAN or EXTERNAL | this report | this commit |

## Verification

- `PATH=$HOME/.elan/bin:$PATH lake build` passed after the merge and route commit.
- `PATH=$HOME/.elan/bin:$PATH .venv/bin/python lean/audit.py` passed with only `propext`, `Classical.choice` and `Quot.sound`.
- `VE_NATIVE_PREBUILT=1 PATH=$HOME/.elan/bin:$PATH .venv/bin/python -m pytest -q tests/test_senses_route.py` passed after the fixture extension.
- `tools/lean_statements.py` found no added, removed or changed approved statements.
- The full clean-HEAD gate runs after this report is committed; its generated JSON is the source for final counts.

## Seeded bugs

Each change was made in `ve/backends/senses.py`, its focused test was run, and
the source was restored. All three mutant runs exited 1 with one failed test.

| Seed | Failing test selection |
|---|---|
| Return an empty string instead of the pack bytes | `spec_reading_fixtures and s7` |
| Skip the dictionary identity comparison | `response_identity_and_type_mutations_fail_closed and dictionary_id` |
| Omit `open` from the allowed statuses | `spec_reading_fixtures and s16` |

## Build checklist

The line numbers refer to `manage-agents/prompts/build-checklist.txt`.
"Open" means this integration does not yet satisfy an applicable line.

| Line | State | Evidence or reason |
|---|---|---|
| 1 | Open | Lean owns admission codes, but limits and response JSON are still described in several sources; there is no generated single contract table or diagnostic text in the route. |
| 2 | Not applicable | Rust and Python have no senses decision engine to compare with Lean; Python is a transport and response validator. |
| 3 | Done for this route | Lean's S2 lexer normalizes reading text. `VE.Senses.Examples` covers NBSP, repeated space, tab, CR, curly quotes, U+212A, dotted I and control characters; the Python relay never normalizes. |
| 4 | Done for the route, schema handwritten | `test_genuine_response_field_mutations_are_rejected` walks every field of seven genuine answers (open, one, none, budget, many, a divergence, a dictionary failure) and drops it or gives it every other JSON type; `test_impossible_status_code_pairs_are_rejected` gives each every status and code `statusCode` never pairs. S2's outcome fields are checked by S2's one validator (`english_lean.response_problem`). The schema is still written by hand, not derived from the Lean encoder. |
| 5 | Open | Top-level malformed pack forms and some nested field types raise `VEError`; every JSON node and 10k-deep replacements have not been exercised. |
| 6 | Done for admission | `test_zero_budget_never_admits` and Lean examples require a budget result, never a negative reading. No senses model verdict is exposed. |
| 7 | Done for admission | The relay starts its deadline before pack prep and sends only the remaining time to Lean; `test_deadline_covers_pack_preparation` injects a stalled prep callee. The candidate cap is checked in time linear in the words (A1). Other B6/B7 operations are open. |
| 8 | Not applicable | No kind or owner fold is changed by this integration. |
| 9 | Not applicable | This route does not render English; B7 is open. |
| 10 | Done for current paths | One entry point, `ve senses check`, calls `ve.backends.senses.read`, which is the operation's one declared Lean call site; `ve check` refuses `--senses`. Other planned B7 paths are open. |
| 11 | Done | Lean parses pack JSON and English with its libraries; Python uses its JSON library and no regex parser for source text. |
| 12 | Not applicable | No state machine or ledger was added. |
| 13 | Done | Three seeded route bugs each failed a focused test; the spec-against-Lean tests execute the relay and compile Lean's fixture guards. The fix round's five gloss rows of `VE.Senses.Examples` each fail on a seeded mutant of `unglossed` that keeps every token. |
| 14 | Done for admission | The subprocess has a fixed environment, the executable is built from sources by `lake build`, and tests write under `tmp_path`. The full gate checks source identity on clean HEAD. |
| 15 | Done for request identity | `request_id` covers the complete request JSON and `dictionary_id` covers canonical decoded pack content and own senses. The relay rejects mutated identities; response fields lack individual S2 projection identities. |
| 16 | Done for changed lists | Frozen sources, audit declarations, trust classes, executable list and pytest collection were regenerated or registered. |
| 17 | Partly done | `test_statement_equals_the_approved_text` and the statement diff pass. The R3 ruling, G-S0 re-review and DRI signatures remain HUMAN / EXTERNAL. |
| 18 | Done in Lean slice | `VE.Senses.Examples` compiles the section 8 fixture guards, including boundaries, and the deferred statements remain exact `Prop` definitions. Human approval is open. |
| 19 | Not applicable to route | No new use-case rule is formalized. B8 use-case measurement remains open. |
| 20 | Partly done | The final handoff takes test counts from the gate JSON and cites fixture test IDs. Full B6/B7 and measurements are listed as not run. |
| 21 | Done | Every acceptance row above has AGENT, HUMAN or EXTERNAL ownership and deferred owners. |
| 22 | Pending final gate | This non-empty report is committed before the full gate on clean HEAD; final status and disk space are recorded in the handoff. |
