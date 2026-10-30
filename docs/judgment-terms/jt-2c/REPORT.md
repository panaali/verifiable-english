# jt-2c report: the composing modes under `judgments@0`

Status: built; no DRI signature reserved. DELTA row 1 is the DRI's (reviews/dri-decisions-20261028-jt-2c.md item 2),
row 2 is R16 (+23 untied V, K +0, S +0). `ve document` answers a `judgments@0` document; every composing mode decides
without the layer through `VE.Compose.decidingEnvironment` and names the list as written. Cut to jt-2d: the
norm-defaults replay kinds under the layer (refused by name now). The chain runs the full gate on the final HEAD.

Plan: docs/spec/judgment-terms-PLAN.md JT-2 (row at line 68), spec docs/spec/judgment-terms.md 8.1-8.3, jt-2b's REPORT
(plan row (3), "Composing modes"), the DRI's decision items 1-3. Statement gate: jt-2's REPORT records JT-2's statement
review (draft 4 ACCEPT). No theorem statement changed: `Route.Run`, `Route.Gate` and `AllowedFamily` are untouched
(`git diff 1f28dddfb -- lean/VE/Route` is empty); the one proof edited, `ResponseShape.Encoders.NormDefaults.runGated_fits`,
keeps its statement (one more `split`). Synthesis round 2 (edits-judgment-terms.md items 1-4: D7's token, JT-4,
JT-3's catalogue rows, PC-10) concerns other batches; this item implements none of them. In-flight overlap (checked
during the build, not before it, with `git diff --name-only main...<branch>` for every `lean-first/*`, `feature/*`,
`infra/*`, `foundation/*` branch): only the shared trust ledgers, `tools/trust-classes.json` (feature/me-2nb,
feature/qt-a3d, foundation/me-1) and `docs/trust-baseline.json` (feature/q1-4bb, feature/qt-a3d); no product file.
feature/sc-5rc, the one the task named, is merged on main.

## Plan rows and directives

| Row | Delivered | Where | Checked by |
|---|---|---|---|
| (1) Every composing mode decides without the layers through Lean's one function, in the mode's own decode; Python never filters the list | yes | `VE.Compose.decidingEnvironment` (`withoutDocumentLayers` after the refusal by name), read by `Standalone.checkCase`, `modelEnvironment`, `evaluable` (metered), `Norms.Plain.run` (background, evaluate, countermodel, certificate: definitions), `Norms.Run` norms-elaborate, `NormDefaults.Run` norm-defaults-elaborate, `EnglishGrammar.Run.decodeCase` and `environmentId`. `Norms.Plain.layered` covers the layer, and `lean_runner.route_mode` sends a listed layer to the norms mode (the route mode's gate theorems read the list as written). Python keeps the layer in every case it sends (`profiles.MODEL_REDUCTIONS`: `DOCUMENT_LAYERS`, generated from Lean's `documentLayers` into `ve/profile_table.json`) | `tests/test_judgments_compose.py` (34 tests), seeded P1, P2, S2 |
| (2) Every identity over the list as written, computed by Lean beside the envelope | yes | each mode's ids read its submitted environment: check (meaning id), model (model id; `checkClaimed`), environment mode (already jt-2's), norm-defaults elaboration (environment, filled environment, document and fill hashes), English (environment id). The English `grammar_id` reads only profiles with an English table (`tableSources`), which no document layer has | `test_the_check_mode_types_as_the_twin_and_names_the_written_list`, `test_a_model_is_valid_as_for_the_twin_and_the_twin_s_ids_do_not_bind` (the twin's claimed ids refused both ways), `test_ve_document_loads_as_the_twin_with_identities_of_its_own`, `test_ve_document_check_and_coverage_answer_as_the_twin`; seeded S1 |
| (3) Composed profiles stay refused | yes | `decidingEnvironment` refuses `alternatives@0`, `rights@0`, `risk@0`, `soft-norms@0` beside the layer by name; the document mode now reads the same function (`environmentOf`, one owner of the text, was `judgmentsApart`); senses and `scope@0` stay refused by the document mode as in jt-2 | `test_a_composed_profile_is_refused_by_name` (12: three modes, four profiles, with and without the layer), `test_a_profile_the_layer_composes_with_is_answered` (4), `test_layers_judgments_does_not_compose_with_are_unavailable`, `test_scope_does_not_compose_with_judgments_yet`; Compose/Examples `#guard`s; M1, M3 |
| (4) jt-2b's row (3): the document answer's route cases in the relay gate's fixtures; `_lean_document` refusing what it must | yes | two genuine `judgments@0` requests appended to `tests/data/relay-gate-cases.jsonl` (`two-rows`, J-ξ′ with reading sets) | `uv run python tools/relay_mutation_gate.py --route service:document`: "13 fixtures, 4984 mutants, 4982 refused, 2 allowed", "0 failures" (no genuine answer refused) |
| (5) The decision's condition tests | yes | `tests/test_judgments_document.py::test_without_the_profile_every_answer_is_todays` (kept, passes), `VE.Compose.gate_judgments` (unchanged), the twin tests above | selected run below |
| (6) Seeded bugs and one mutant per new trusted definition | yes | `mutants.json` (S1, S2, P1-P3, R1, M1-M4), `trust-mutants.json` with `trust-mutants-allow.json` | below |

Deviations, each recorded here and nowhere in the plan:

- jt-2b's test `test_the_answer_fits_its_schema_and_models_refuse_the_profile` asserted that Python's model
  projection refuses the layer. It is renamed `..._models_keep_the_profile_as_written` and asserts the opposite: the
  projection keeps the list as written and Lean decides without it (trailer `Test-removed` on this report's commit).
- Rust's accelerator lists `judgments@0` in its allow-list (`rust/ve-kernel/src/environment.rs`): its search reads
  the model environment as written; its answers carry no identity and every witness is checked by Lean's model and
  check modes, which decide without the layer.
- `EnglishGrammar/Run.lean` changed, so the English `actions_version` is 35 (`tools/english_grammar_gen.py --write
  --actions-version 35`) and the ask fixtures were re-recorded (`tools/ask_fixtures.py --write`): 17 files, only
  `actions_version` (17) and the recorded `seconds` (11) change (a field diff of each file against HEAD).

## Not delivered: jt-2d

Under `norm-defaults@0` the route's replay kinds (`norm-defaults-gaps`, `-conflict`, `-status`, `-report`,
`-certificate` and defeasible's four) decode the case's environment inside replay functions whose soundness theorems
(`Wire.replayConflictU`, `replayEntailmentU`, ...) are stated over that environment, and bind their certificates and
models to it. Deciding them without the layer needs those statements (or a wrapper binding to the written list)
reviewed. Until then `pendingDocumentLayer` refuses them by name, so `ve document check` and `coverage` of a
pilot-list document (`norm-defaults@0` with `judgments@0`) end `CheckerUnavailable: judgments@0 with
norm-defaults-gaps needs its composed Lean route`, while load, `render` and `readings` answer
(`test_the_pilot_list_s_replay_kinds_are_refused_by_name_until_jt_2d`, `test_ve_document_loads_..[pilot]`,
`test_ve_document_render_is_the_twin_s[pilot]`). The route mode itself is not needed: a listed layer goes to the norms
mode, which delegates to the route on the environment without it.

## Seeded bugs

[`mutants.json`](mutants.json); each applied to the committed file, its test run, the file restored:

- S1 (Lean, `lean/VE/Service/Standalone.lean`, an identity over the stripped list): the check mode's ids over
  `decidingEnvironment environment`. Fails `test_the_check_mode_types_as_the_twin_and_names_the_written_list` (2).
- S2 (Lean, `lean/VE/Norms/Plain.lean`, a mode deciding over the written list): `let deciding := submitted`. Fails
  `test_definitions_are_elaborated_as_for_the_twin`. S1 and S2 were built into one service (disjoint modes).
- P1 (Python, `ve/profiles.py`, Python filtering the list): the layers' model row drops them. Fails
  `test_the_answer_fits_its_schema_and_models_keep_the_profile_as_written`.
- P2 (Python, `ve/document/lean.py`, Python filtering the list): the environment built without the layer. Fails
  `test_ve_document_loads_as_the_twin_with_identities_of_its_own` (5 of 5).
- P3 (Python, `ve/backends/lean_runner.py`): `route_mode` ignores the layer. Fails `..._loads_..[fol]`.
- R1 (Rust, `rust/ve-kernel/src/environment.rs`): the layer off the allow-list. Fails
  `test_ve_document_check_and_coverage_answer_as_the_twin` (Rust's `UnsupportedProfile`).
- M1-M4, one per new trusted definition (`decidingEnvironment` twice, `documentLayersApart`, `pendingDocumentLayer`):
  each breaks a `#guard` of `lean/VE/Compose/Examples.lean` or `lean/VE/Defaults/RouteExamples.lean` (`lake build`
  of that module: "error: ... Expression" at the guard).
- Mechanical mutants (`zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --test lean/VE/Defaults/RouteExamples.lean
  --allow ... --json docs/judgment-terms/jt-2c/trust-mutants.json`): see `trust-mutants.json` `counts`. Allowed
  survivors are listed with reasons in `trust-mutants-allow.json`: equivalent cuts of the one-element
  `documentLayers`, two cuts that do not elaborate, the `ProfilesMain` IO generator (checked by
  `tests/test_profile_table.py`), `ownedProfiles` (unchanged, selected only by the deleted neighbour) and the
  existing `flags := true` argument on a changed line.

## Trust, size and evidence

- Trust: `uv run python tools/trust_map.py --check` on this branch: "K +0, S +0, D +2, G +32, ..., trusted +23"
  (Dispatch +12, NormDefaults/Run +4, Plain +3, Standalone +3, EnglishGrammar/Run +1); allowance recorded with
  `--allow ... --signed "SIGNED by standing ruling R16 ..."` (`docs/trust-baseline.json`); FOLLOW-UPS.md "## jt-2c"
  asks for the ties pass.
- Lean: `lake build` "Build completed successfully (1161 jobs)"; `python3 lean/audit.py` "PASS: 670 source files".
- Size (`git diff --numstat` against the merge base, added plus deleted, generated files, the re-recorded ask
  fixtures and the two appended fixture lines left out): Lean 126 (of which `#guard`s and their helpers 48), Python 14, Rust 2,
  tests 207, plus these docs.
- Tests while iterating: `uv run pytest -q tests/test_judgments_compose.py tests/test_judgments_document.py
  tests/test_judgments_answer.py tests/test_ask_fixtures.py tests/test_profile_table.py`: "140 passed". The selected
  run on the Mac runner: see the build report (run after this file was committed).
- Not run: whole-document pilots (L70), base/head timing (one extra list filter per case).
- Pilot bytes expected to move: none from this item (no pilot lists `judgments@0`). After JT-5r, JT-5a expects Lean
  statuses on 13 constitution units and JT-5b on 18 UDHR units; the pilots list `norm-defaults@0`, so their
  `check` and `coverage` need jt-2d first. Nothing is claimed before a pilot audit.

Spec re-read: "every composing mode DECIDES over the environment without the document layers ... in the mode's own
decode" and "every IDENTITY ... over the list AS WRITTEN" against reviews/dri-decisions-20261028-jt-2c.md item 1 (a),
(b); "AllowedFamily is NOT widened and decodeEnvelope's refusal theorems keep their statements" against item 1 (c);
"a composition with alternatives@0, rights@0, risk@0, soft-norms@0 or senses stays refused by name" against item 1 (d);
"With the profile off, none of this runs and every answer is byte-identical" against docs/spec/judgment-terms.md:746.

## Next item

jt-2d (the norm-defaults replay kinds under a document layer, with their statement review), then JT-5r's audit and
the JT-5a/5b pilot switch-ons.
