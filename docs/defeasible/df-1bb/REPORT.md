# df-1bb: the English, the label lint, the route cases and the defaults probe (build report)

No DRI signature is reserved. DELTA has one row (the flag's answer gains the field `english`), signed by standing ruling
R3. Trust +0: no Lean file changes. **Cut:** DE5 (it needs Lean's `decidersOf` on the wire), the gap sentences after
DE6, W7's all-derivations gate on the new rows and a typed `reason` go to **df-1bbb** (section 5).

Branch `feature/df-1bb`, base main c86861a2a (the merge base). Plan and spec as on main (`docs/spec/defeasible-PLAN.md`
DF-1b, 2.2, 2.3, 2.8, 4.1, 4.2, 6.2, 6.3; `docs/spec/defeasible.md` 4, 5, 7.2). It continues df-1b
(`docs/defeasible/df-1b/REPORT.md` sections 1, 2 and 5).

**Statement gate.** DF-S passed (`manage-agents/defeasible-p3ver1.final.md`). This item adds no Lean statement.

## 1. Plan rows delivered

| Plan row (DF-1b, df-1b's cut) | Where | Test |
| --- | --- | --- |
| English DE1 (`form` short) and DE1′ (`form` long), Lean's form | `ve/defaults_english.py` `follows` | `tests/test_defaults_english.py::test_de1_and_de2_short_form`, `::test_de1_long_and_de2_conditions`, `::test_form_is_lean_s`; R1, E4 |
| DE2, DE2·u, DE2′, DE2′·u (a rule's exception, with or without stated conditions, named or `unstated` decider) | `_exception` | `::test_de1_and_de2_short_form`, `::test_de2_unstated`, `::test_de1_long_and_de2_conditions`, `::test_de2_conditions_unstated`, `::test_de2_document_decider_stands_for_unstated`; E7 |
| DE3 (a switch) | `_switch` | `::test_de3_switch`; E5 |
| DE4 and DE4·u (a ranking, outranking decider named or `unstated`) | `_ranking` | `::test_de4_ranking`, `::test_de4_unstated`; E6 |
| DE6 (`forced` empty) and DE6′ with one DE11 per `forced` entry, in Lean's order | `fails` | `::test_de6_no_exception_holds`, `::test_de6_long_and_de11_at_beta_one`, `::test_de11_once_per_forced_entry_in_lean_order`; R2, E2 |
| DE7 with DE7a, DE7a·u, DE7b, DE7b·u by Lean's `giveWayDeciders` | `collision` | `::test_de7_and_de7a`, `::test_de7b_two_deciders`, `::test_de7_decider_sentence_is_lean_s_deciders` (5 cases), `::test_no_collision_no_de7`; E3, W1 |
| DE12 (basis `unsettled`) | `follows` | `::test_de12_after_the_assumptions_only_when_unsettled`; E1 |
| non-wordings (spec 4): no label, `soft__`, `unsaid__` or "by default"; no short marker on a long or forced answer | all rows | `::test_no_label_prefix_marker_or_by_default` |
| the plan's two renderer seeded bugs | `mutants.json` R1, R2 | section 4 |
| `tools/relay_lint.py`: `default:` forbidden in `ve/`, `ve/defaults.py` in `RELAYED` | fifth rule `default_labels`, `DEFAULT_LABEL`, `DEFAULTS_GLOB`; `RELAYED` | `tests/test_relay_lint.py::test_seeded_default_labels` (6 refusing, 6 accepting), `::test_the_defaults_relay_is_relayed_and_every_ve_module_is_read`, `::test_every_relayed_module_exists_and_passes`; L1-L4 |
| route cases of the flag, recorded by `tests/route_case_recorder.py`, append-only | `tests/data/route-cases.jsonl` +18 lines (`evidence/select_route_cases.py`) | `tests/test_route_row_schemas.py`, `tests/test_lean_handles.py` (66 passed) |
| `probe_defaults.py`; P-1 and P-3; the pilot's `default_answer_probe` | `probe_defaults.py`, `probe/` (P-3's document and two questions) | output `evidence/probe.json` (section 1.1); `::test_p3_follows_long_listing_the_three_conditions`, `::test_p3_fails_where_a_condition_holds_naming_it`, `tests/test_defaults_lean.py::test_p1_follows_unless_an_exception_applies` (DE1 + DE2·u) |
| DE5 | **df-1bbb** | — |
| a typed `reason` (df-1b section 2, item 4) | **df-1bbb** (the shapes' owner) | — |

Each new check has fixtures on both sides: each label kind with the right and a wrong arity, a known and an unknown
rule, a default and a strict rule, an `alterable` party and another, declared and undeclared ranks, a regulated act and
a plain predicate (`::test_a_label_the_request_gives_is_rendered`, `::test_a_label_the_request_cannot_give_is_refused`);
each decider shape; `default:` followed by a name, by nothing, by a space and by a newline, in a literal, a docstring
and a comment.

### 1.1 P-1 and P-3 through the flag (`evidence/probe.json`, verbatim there)

`uv run python docs/defeasible/df-1bb/probe_defaults.py docs/defeasible/df-1bb/evidence/probe.json`:
`{"questions": 5, "strict_answers": 0, "default_answers": {"FOLLOWS": 4, "DOES-NOT-FOLLOW": 1}, "unknown": []}`.

| Probe | Answer (Lean's) | English |
| --- | --- | --- |
| P-1 u0036.s05, u0156.s03, u0263.s04.p2 | FOLLOWS, `needs`, short, one assumption each | DE1 + DE2·u: "Unless an exception applies, the conclusion follows: …" + "This assumes that the exception to rule clarify-ambiguity does not apply. The text names no case where it applies, and no one who decides." (and the other two rules) |
| P-3 u0073.s05, none of the three holds | FOLLOWS, `needs`, **long**, `[default:exception:comply]` | DE1′ + DE2′·u listing the three conditions in the rule's order |
| P-3 u0073.s05, no condition stated | DOES-NOT-FOLLOW, `forced = [(comply, 2, [e0, e0])]` | DE6′ + DE11 "The text's own exception to rule comply applies here: e0 is classified as \"against_guidelines\"." |

That is plan 4.2's expected shape for P-1 and P-3. Spec 8.7 names condition 1 ("unethical") for P-3's countermodel;
the search found one where condition 2 holds, and Lean's `forced` names that one (the test accepts any of the three,
reads its index from Lean's row, and checks the sentence names it). P-3's document (`probe/p3-force-u0073-s05.ve.md`)
is this item's own miniature of u0073.s05 in CE4's frame (no pilot translation of u0073.s05 exists in the tree).

## 2. Deviations and design points

1. **Rule names, not numbers.** `<n>` and `<m>` are the rule's name, as in Lean's labels, Lean's reason "with no
   exception, rules r1 and r2 conflict" and spec 8.3's DF-ρ English ("Rules no-deception and permit-deception").
2. **Labels are read, never built.** An assumption's sentence is chosen by the kind its Lean label names
   (`Premises.lean` `dfltLabelled`: `exception`, `switch`, `ranking`), split at `:`; every rule, party, rank and act it
   names must be the request's (else `CheckerUnavailable`). The labels were bound to Lean's `default_premises` by
   `ve.defaults.answer` before rendering. The lint holds: no `ve/` literal spells the prefix.
3. **Renderers.** The conclusion is `canonical_sentence(..., statement_layer=True)` (read back to the formula); a
   condition is the soft rules' condition text (`norm_english._guard_text`), over the rule's own variables in DE2′ and
   at the forced tuple's entities in DE11; the situation and DE7's effects are Lean's `words` lines (`words.situation`,
   `words.clause`). The act phrase of DE4 is the declared act without its slots, as the readings route's
   `act_phrase` (`ve/readings_route.py:1241`; feature/ap-1bd edits that file, so the one-line helper is not moved
   there in this item: df-1bbb or ap-1bd's successor makes `act_phrase` call `defaults_english`'s, or the reverse).
4. **The deciders.** `_decider` (df-1b's `ve/defaults.py:60`) gives a rule's decider for DE2 to DE2′·u; DE4 reads the
   source's `outranking.decided_by`; DE7 reads Lean's `deciders` only. The decider phrase is spec 4's "the <party>".
5. **DE5 cut.** DE5's `<deciders>` is Lean's `decidersOf D` (spec 4), which no wire row carries; computing it in
   Python would copy a Lean definition. A strict basis shows no default sentence until df-1bbb adds the field.
6. **Not done in this item, named for df-1bbb:** norm-defaults' gap sentences after DE6 (the situation row names the
   unsaid tables, which Python must not spell); W7's all-derivations gate on DE1-DE12 (the conclusion's sentence is
   read back today; the frames are not).

## 3. Evidence

- No Lean change; `lake build` passes on the merge base's Lean tree (restored by `lean-prep.sh`), and
  `python3 tools/rust_build.py` gives the pinned binary.
- `uv run python tools/regen_generated.py --write` once (the new module's layer: `.importlinter`); `--check`
  otherwise clean. `tools/trust_map.py --check`: K +0, S +0, D +0, G +0, trusted +0. `tools/repo_map.py --check`: PASS.
- `uv run python tools/relay_lint.py`: PASS, 149 `ve/` modules with no label, 17 relayed modules (with
  `ve/defaults_english.py` as `ve/defaults.py`'s helper).
- Route cases: `VE_ROUTE_CASES=<dir> uv run pytest -q -p tests.route_case_recorder tests/test_defaults_lean.py -k
  "p1 or beta_forced or gamma_collision or delta or epsilon"`, then `evidence/select_route_cases.py <dir> --write`:
  18 cases (127,005 bytes): every case of P-1's documents and the smallest other case of each new group.

## 4. Seeded bugs, trust, size, pilot bytes

Seeded bugs (Python only; `mutants.json`, run by `evidence/run_mutants.py`, saved `evidence/mutants.out`): the
controls pass and **all 14 fail their tests**.

| # | File: bug | Fails |
| --- | --- | --- |
| R1 | `ve/defaults_english.py`: DE1 without "Unless an exception applies" (plan) | `tests/test_defaults_english.py::test_de1_and_de2_short_form` |
| R2 | DE6 printed for DF-β (i), Lean's `forced` ignored (plan) | `::test_de6_long_and_de11_at_beta_one` |
| E1-E7 | DE12 dropped; DE11 for the first entry only; DE7a·u never chosen; Python chooses the form; a switch's party unbound; a ranking's ranks unbound; DE2·u never chosen | `::test_de12_…`, `::test_de11_once_per_forced_entry_in_lean_order`, `::test_de7_decider_sentence_is_lean_s_deciders`, `::test_form_is_lean_s`, `::test_a_label_the_request_cannot_give_is_refused` (E5, E6), `::test_de2_unstated` |
| L1-L4 | `tools/relay_lint.py`: a bare `default:` missed; comments not read; `ve/defaults.py` not in `RELAYED`; only the top level of `ve/` read | `tests/test_relay_lint.py::test_seeded_default_labels` (L1, L2), `::test_the_defaults_relay_is_relayed_and_every_ve_module_is_read` (L3, L4) |
| W1 | `ve/defaults.py`: `ask` drops the gate's English | `tests/test_defaults_english.py::test_de7_and_de7a` |

**Trust:** +0 (no Lean file). No R16 row, so no FOLLOW-UPS ties row.

**Size** (`git diff --numstat c86861a2a`, hand-written, before this report): product 233 (`ve/defaults_english.py`
185, `ve/defaults.py` +11/-5, `tools/relay_lint.py` +37/-5), tests 327, route cases 18, probe and P-3 inputs 72,
evidence 223 (`mutants.json`, its runner and output, `probe.json`, the case selector), DELTA 11. About 965 lines, in
the trial's 800-1,500 target.

**Pilot bytes** (estimate; nothing is claimed before a pilot audit): none move in this item. The pilot's "Feature
upgrades" count can move once its run copies `default_answer_probe` into `metrics.json`: 4 of 5 probe questions follow
unless an exception applies (P-1's three, P-3's first), and P-3's second is answered DOES-NOT-FOLLOW with the
exception the text forces.

## 5. Next items

- **df-1bbb**: DE5 (Lean's `decidersOf` as a `deciders` field of a strict `defaults-certificate` row and of the strict
  question's answer: a Lean shape change); the gap sentences after DE6 (Lean's row naming each gap by predicate and
  tuple); W7's all-derivations gate on DE1-DE12; a typed `reason` (an enum of spec 5's statuses, with the collision's
  rules); one `act_phrase` shared with `ve/readings_route.py` once feature/ap-1bd lands.
- Then DF-3 (rank 90, readings with the default fold); then DF-4.

Evidence commit list (`git log --oneline main..HEAD --no-merges`, before this report): ff34057f2, 72db1f1c4,
b0307764a, 0f845f373, 864432dc3, ff225512d.

Overlap: `tests/data/route-cases.jsonl` is also appended to by feature/qt-a3c (both append-only: keep both blocks);
`tools/layer_policy.py` is also edited by feature/jt-2b (this item's line is two lines away from its hunk). No file
under `ve/document/` changed.

## 6. Final selected run

`zsh manage-agents/mac-pytest.sh --select -- --base c86861a2a --run` on ff225512d (ran on the VM: no Mac slot
within 600 s), 290 units: **288 passed, 2 failed**, both registry entries for this item's new files:
`tests/test_regen_generated.py::test_every_script_with_a_writing_mode_is_registered_or_excluded_with_a_reason`
(`evidence/select_route_cases.py` not in `NOT_REGENERATED`) and
`tools/test_layer_policy.py::LayerSelectionTests::test_documented_python_layers_match_policy`
(`defaults_english` not in `docs/ARCHITECTURE-LAYERS.md`). Fixed (both entries added); the two ids rerun on the Mac:
2 passed. `regen_generated.py --check`: 33 entries, clean. No test of `main-known-red.txt` was selected to fail.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS. No new Lean answer or field; the rows rendered are df-1b's typed, bound rows
   (`tests/test_defaults_answer.py::test_mutants_never_pass_as_answers`); a label or `forced` rule the request cannot
   give is `CheckerUnavailable` (`tests/test_defaults_english.py::test_a_label_the_request_cannot_give_is_refused`,
   `::test_a_forced_rule_the_request_lacks_is_refused`).
2. Deliverables: PASS for rows (1)-(5) of the cut except DE5, the DE6 gap sentences, W7's gate and a typed `reason`,
   which are named as df-1bbb (section 1, 2.5-2.6, 5); no Python copy of a Lean decision (`decidersOf` not copied:
   DE5 cut); no permanent report test; overlaps listed (section 5).
3. Tests can fail: PASS, 14 seeded bugs all failing (`evidence/mutants.out`), both plan renderer bugs included.
4. Agreement and valid inputs: PASS. Python-only change; the flag's other fields unchanged
   (`tests/test_defaults_lean.py`, `tests/test_defaults_answer.py`); two-argument predicates and tuples (P-3,
   `::test_p3_fails_where_a_condition_holds_naming_it`); labels split into structured parts, never matched by prefix.
5. R8 binding: PASS. Every rule, party, rank, act the English names is refused when undeclared
   (`::test_a_label_the_request_cannot_give_is_refused`, 11 cases; `::test_a_forced_rule_the_request_lacks_is_refused`);
   the rows' ids, counts and order are bound by df-1b's `bind_*`.
6. Gate evidence: PASS for the selected run (section 6); the chain runs the full gate on the final HEAD.
7. Unsigned items: PASS. DELTA row 1 cites R3, with the goldens and tests R3 asks for.
8. User-visible changes in DELTA: PASS (`DELTA.md` row 1; without the flag nothing changes:
   `tests/test_defaults_lean.py::test_p1_follows_unless_an_exception_applies`).
9. Test selection: PASS. `tools/select_tests.py --base c86861a2a` selects `tests/test_defaults_english.py`,
   `tests/test_relay_lint.py`, `tests/test_defaults_lean.py`, `tests/test_defaults_answer.py`.
10. Lean statements: N.A., no Lean change.
11. Budgets: PASS. Unchanged: `tests/test_defaults_lean.py::test_an_empty_budget_is_unknown`; the renderer has no
    budget and shows no default sentence for UNKNOWN (`::test_an_unknown_answer_shows_no_default_sentence`).
12. CPU: N.A. for the pilots (the flag is opt-in; no pilot path changes). The English adds one `words` request per
    situation or effect and one conclusion rendering per answer.
13. Removed tests: N.A., none removed or renamed.

## FIXMAP

- `ve/defaults_english.py`: the English of the defaults rows (spec 4). `_Text` (renderers per request) :29;
  `_exception` DE2/DE2·u/DE2′/DE2′·u :83; `_switch` DE3 :100; `_ranking` DE4/DE4·u :107; `assumption` (label kind)
  :117; `follows` DE1/DE1′/DE12 :126; `fails` DE6/DE6′/DE11 :140; `collision` DE7 + DE7a/a·u/b/b·u :152;
  `sentences` (entry) :177.
- `ve/defaults.py`: `ask` (:283) adds `english` from `sentences` for the answer and the coherence row.
- `tools/relay_lint.py`: fifth rule: `DEFAULT_LABEL`/`DEFAULTS_GLOB` :100-101, `default_labels` :268,
  `defaults_modules` :282, called in `main`; `RELAYED` gains `ve/defaults.py` :73.
- `tools/layer_policy.py`, `docs/ARCHITECTURE-LAYERS.md`: `defaults_english` in layer 4 (generated `.importlinter`).
- `tools/regen_generated.py`: `NOT_REGENERATED` entry for `evidence/select_route_cases.py`.
- `tests/test_defaults_english.py`: one fixture per form, refusals, non-wordings, P-3.
- `tests/test_relay_lint.py`: `test_seeded_default_labels`, `test_the_defaults_relay_is_relayed_and_every_ve_module_is_read`.
- `tests/test_defaults_lean.py`: `ALPHA_ENGLISH`, P-1's English; `tests/test_defaults_answer.py`: alpha golden.
- `tests/data/route-cases.jsonl`: +18 norm-defaults cases (append-only; `evidence/select_route_cases.py`).
- `docs/defeasible/df-1bb/probe_defaults.py`, `probe/`: P-1 and P-3; output `evidence/probe.json`.
- `docs/defeasible/df-1bb/mutants.json`, `evidence/run_mutants.py`, `evidence/mutants.out`: seeded bugs.
- Regression tests: `uv run pytest -q tests/test_defaults_english.py tests/test_defaults_lean.py
  tests/test_defaults_answer.py tests/test_relay_lint.py`; seeded bugs:
  `uv run python docs/defeasible/df-1bb/evidence/run_mutants.py > docs/defeasible/df-1bb/evidence/mutants.out`.
- Generated: `.importlinter` (from `tools/layer_policy.py`): `uv run python tools/regen_generated.py --write`.
- trust_mutants: not run (no Lean change).

## END FIXMAP
