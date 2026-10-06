# Senses integration report

This report covers the local `senses/integrate` merge of `senses/py` and
`senses/lean`, and the new route that admits senses readings through the
compiled Lean reader. The shipped grammar follows the **as merged** column of
[senses.md](senses.md) section 8. R3 has no DRI ruling in this checkout.

## Acceptance and ownership

| Item | Class | State and owner |
|---|---|---|
| Merge and conflict resolution | AGENT | Done. The frozen source inventory, audit declarations, trust classification, layer policy, and gate collection include both branches. |
| Fixture pack and Lean decoder | AGENT | Done. The fixture pack's `principal` and `resource` letters match the spec and Lean. `test_spec_pack_python_file_and_lean_fixture_agree` checks spec JSON, Python bytes, compiled Lean pack and dictionary identity. |
| Senses admission | AGENT | Done for `senses.read`: `ve_senses_route` transports raw pack text to Lean's restricted decoder, calls `readWithSenses`, and returns the result with dictionary and full-request identities. `ve/backends/senses.py` checks those identities and the response shape. |
| CLI reading | AGENT | Done for `ve senses check` and `ve check --surface english --senses`. `test_two_cli_admission_paths_agree` runs both on s7 and checks the formula. These paths emit JSON admission; human-readable diagnostic text and rendering are not present. |
| Three-way fixture conformance | AGENT | Done for the fixture pack and s1, s4, s7, s8, s9, s16, s21, s22, n1, n2 and n3 in the as-merged column. `test_spec_reading_fixtures` and `test_three_way_spec_fixture_admission` compare spec values with Python relay results while `VE.Senses.Examples` compiles its independent Lean guards. The complete spec matrix remains guarded in Lean, but has no complete Python route matrix. |
| Full B6 service | AGENT | Open, owner senses integration: no `senses.project`, six S2 projection identities, `sensesVersion` lock, flip models, or Lean diagnostic text. The new one-shot executable is separate from `ve_english_route`. |
| B7 display and reading sets | AGENT | Open, owner senses integration: rendering, glossary, resolve, candidate re-read, and propose-readings are not implemented. |
| R3 and Q4 | HUMAN | Deferred to the senses DRI under spec sections 6.2 and 11. The current as-merged column keeps the comma forms. |
| Four deferred statements | HUMAN | Deferred to the senses DRI for signatures under G-S1: `glossed_negative`, `lines_read`, `project_total`, `senseMap_ids`. They are `Prop` definitions, not theorems. |
| Draft 2 bounded re-review | EXTERNAL | Deferred to the statement reviewers under G-S0. The merged Lean examples and approved statement comparison supply evidence for review. |
| Starter packs and measurements | HUMAN / AGENT | Human reviewers own the pack pins; senses integration owns the subsequent use-case measurements. Neither is complete. |

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
| 4 | Open | The relay checks genuine response field mutations and bool-for-int, but its schema is handwritten rather than derived from the producer; mutation coverage is incomplete. |
| 5 | Open | Top-level malformed pack forms and some nested field types raise `VEError`; every JSON node and 10k-deep replacements have not been exercised. |
| 6 | Done for admission | `test_zero_budget_never_admits` and Lean examples require a budget result, never a negative reading. No senses model verdict is exposed. |
| 7 | Done for admission | The relay starts its deadline before pack prep and sends only the remaining time to Lean; `test_deadline_covers_pack_preparation` injects a stalled prep callee. Other B6/B7 operations are open. |
| 8 | Not applicable | No kind or owner fold is changed by this integration. |
| 9 | Not applicable | This route does not render English; B7 is open. |
| 10 | Done for current paths | Both CLI admission paths call `ve.backends.senses.read`; `test_two_cli_admission_paths_agree` runs the same s7 source through both. Other planned B7 paths are open. |
| 11 | Done | Lean parses pack JSON and English with its libraries; Python uses its JSON library and no regex parser for source text. |
| 12 | Not applicable | No state machine or ledger was added. |
| 13 | Done | Three seeded route bugs each failed a focused test; the three-way tests execute the relay and compile Lean's fixture guards. |
| 14 | Done for admission | The subprocess has a fixed environment, the executable is built from sources by `lake build`, and tests write under `tmp_path`. The full gate checks source identity on clean HEAD. |
| 15 | Done for request identity | `request_id` covers the complete request JSON and `dictionary_id` covers canonical decoded pack content and own senses. The relay rejects mutated identities; response fields lack individual S2 projection identities. |
| 16 | Done for changed lists | Frozen sources, audit declarations, trust classes, executable list and pytest collection were regenerated or registered. |
| 17 | Partly done | `test_statement_equals_the_approved_text` and the statement diff pass. The R3 ruling, G-S0 re-review and DRI signatures remain HUMAN / EXTERNAL. |
| 18 | Done in Lean slice | `VE.Senses.Examples` compiles the section 8 fixture guards, including boundaries, and the deferred statements remain exact `Prop` definitions. Human approval is open. |
| 19 | Not applicable to route | No new use-case rule is formalized. B8 use-case measurement remains open. |
| 20 | Partly done | The final handoff takes test counts from the gate JSON and cites fixture test IDs. Full B6/B7 and measurements are listed as not run. |
| 21 | Done | Every acceptance row above has AGENT, HUMAN or EXTERNAL ownership and deferred owners. |
| 22 | Pending final gate | This non-empty report is committed before the full gate on clean HEAD; final status and disk space are recorded in the handoff. |
