# REPORT: defs-repair-claude-constitution-excerpt-1119

**Summary.**
- Status: all 7 P1 rows are KEPT and CARRIED word for word in the environment.json legends of the terms their rules use. Every derived file is regenerated with the project's tools except `conformance/english-lean/s0-report.json` (see Deliverable 2). No DRI signature is outstanding.
- Merges at VE main `f03cafb9d2` (merged into the branch; corpus seal: main's taken and regenerated). Answers touched: 1 of 2 keyed (model-false.json, through C3 / row 5; rows 1-4, 8, 9: 0 of 2).
- DRI decision used: reviews/dri-decisions-20261119-defs-repair-claude-constitution-excerpt-1119.md item 1, with item 1(a) superseded by reviews/defs-repair-claude-constitution-excerpt-1119-dri-note-20261119.md: the 2026-09-21 Astra review is NOT carried across the environment_id rebind (Astra never read the appended descriptions). The new pinned record is the 2026-11-19 read by Claude Opus 5.5 (claude-opus-5-5), seat dri-decider, of the nine predicates' and sorts' overlay wording against the appended descriptions (reviews/defs-repair-claude-constitution-excerpt-1119-overlay-read.md, manage-agents repo; all nine consistent). The builder is not that reviewer.
- Trust +0 (`uv run python tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0 ... PASS"). No Lean, Python or Rust code changed.
- The full gate has not been run here; the chain runs it on the final HEAD.

## 0. Verify first

Each row was checked against source.md and the legends at main (the in-repo source; METHOD.md amendment 8: no hash-pinned source). `usecases/claude-constitution-excerpt/` has no change between the audit pin 3d6b459df4 and main (`git diff --stat 3d6b459df4 main -- usecases/claude-constitution-excerpt/` is empty). The check script (/tmp/ccx/verify.py, run before any edit) printed `span==quote` and `not-carried` in environment.json, definitions-environment.json, environment.english.json and claims.ve for all seven rows.

| row id | verdict | reason (file:line) |
|---|---|---|
| defs-claude-constitution-excerpt-1-1119 | KEPT | the quote is source.md:16-19 (sentences 4-7) exactly; sort `property` (environment.json:25) is used by claims.ve:7-8 and is the sort of `@safety`..`@helpfulness` in claims.ve:6; not carried (its legend names the four properties only) |
| defs-claude-constitution-excerpt-2-1119 | KEPT | source.md:16-19; predicate `ought_have_core_values` (environment.json:37) is used by claims.ve:1; not carried |
| defs-claude-constitution-excerpt-3-1119 | KEPT | source.md:16 (sentence 4); `appropriate` (environment.json:41) is used by claims.ve:2, 9; not carried ("during the current phase of development" absent) |
| defs-claude-constitution-excerpt-4-1119 | KEPT | source.md:30 (sentence 18); `undermines` (environment.json:45) is used by claims.ve:2, 9; not carried |
| defs-claude-constitution-excerpt-5-1119 | KEPT | source.md:17 (sentence 5); `honest` (environment.json:49) is used by claims.ve:3; not carried (legend quotes a lower-case fragment only) |
| defs-claude-constitution-excerpt-8-1119 | KEPT | source.md:21 (sentence 9); `outranks` (environment.json:77) is used by claims.ve:6, 7, 8 (`tc[outranks]`); not carried |
| defs-claude-constitution-excerpt-9-1119 | KEPT | source.md:32-33 (sentences 20-21, one span); sort `overseer` (environment.json:22) is used by claims.ve:11 and is the sort of `@anthropic` in claims.ve:10; not carried |

P2 rows 6 and 7 (optional, FORMALISED) were not taken, as the task says. I found no candidates of my own.

## 1. Carried definitions

`usecases/claude-constitution-excerpt/environment.json`: each of the seven descriptions keeps its text and gains one space plus the source span. The span is read by script from source.md's numbered list (the "N. " list marker is dropped), so its text is the source's own. The test's `source_span` builds each span from the source file. Carrier = the description legend of the sort or predicate the rule uses (METHOD section 3: "a vocabulary legend ... of a predicate, constant or sort that rule uses"). It is never a header, a comment or a constant table.

- environment.json owns the text. `definitions-environment.json` is not hand-edited: verify_definitions.py:56-86 generates it from environment.json.
- No sealed or frozen run directory is involved (the case has no frozen-run.json).
- No rule formula and no theorem statement changes. claims.ve is untouched.

## 2. Derived files (regenerated with the project's tools)

| file | tool | change |
|---|---|---|
| usecases/.../definitions-environment.json, definitions-report.md | `uv run python usecases/claude-constitution-excerpt/verify_definitions.py` | 7 descriptions. In the report, "Python, Lean and Rust" becomes "Python, Lean" because the current Rust runner answers `unknown case: Rust checks search cases only` to this evaluate case. That comes from main, not from this item. |
| usecases/.../rendered.md | the `ve render ... --view ve_fluent --with-legend --legend-style compact` command the file records (the output block from the old environment reproduced the committed block byte for byte first) | environment id + 7 legend lines |
| usecases/.../environment.english.json | rebind of `environment_id` to the new `Environment.environment_id` (no rebind tool exists; one-line mechanical change, proved by the rebind test) | 98dbed69... -> 467d3440... |
| ve/reviewed-overlays.json | new record per the DRI note (reviewer "Claude Opus 5.5 (claude-opus-5-5), seat dri-decider", date 2026-11-19, no `carried_from`, scope citing the overlay-read file); the 2026-09-21 record is unchanged byte for byte | +7 lines |
| usecases/.../rendered-english.md | `uv run python -m conformance.english_artifacts` (the three other use cases and docs/english-surface.md came out unchanged) | environment id, overlay digest (review status stays `reviewed`), 7 legend lines |
| conformance/english-surface-report.json | `uv run python -m conformance.english_surface` (all 17 vocabularies, about 4 h on the loaded VM) | excerpt environment_id and overlay_digest. `grammar_sha256` moves in all 17 rows because main's report predates later grammar changes. Every count and corpus hash is unchanged and `ambiguous_texts` stays 0. |
| conformance/english-lean/lexicon-report.json | `uv run python -m conformance.english_lean_lexicon` (valid 43, invalid 0) | the excerpt's 2 x 2 lexicon_id lines. The audit's derived_files did not list this file; the selected run found it. |
| conformance/english-lean/corpus-seal.json | `uv run python -m conformance.english_lean_seal` after the merge of main; `--check`: "0 difference(s)" | 110 sources |
| conformance/english-lean/s0-report.json | NOT regenerated | `python -m conformance.english_lean_s0` on this tree rewrites unrelated measurements from 2026-10-03. It drops all `spacing_mutant_examples` (112 lines), sets `same_tokens` true -> false in 2 rows and changes every timing. Writing that in this item would be a loss of recorded information. The file keeps the old excerpt environment_id as the label of that dated measurement. No test binds it (tests/test_english_lean_s0.py reads no environment_id). |

## 3. Condition test

`tests/test_defs_repair_claude_constitution_excerpt_1119.py` (new, 24 cases):
- `test_the_source_definition_is_carried_word_for_word`: 7 rows x {environment.json, definitions-environment.json}. Each case checks a raw substring, then a substring after `omit_norm`.
- `test_the_carrier_is_a_term_the_rule_uses`
- `test_the_only_environment_change_is_the_appended_source_spans`: removing the 7 spans gives environment id 98dbed69..., the id the review was bound to.
- `test_the_overlay_review_is_carried_only_by_the_environment_id_rebind`: the DRI's two proofs, digest with the old id == 8411f393... and a key-by-key comparison with the saved reviewed overlay `evidence/reviewed-overlay-20260921.json`; then the records: the 2026-09-21 Astra record equals its pinned fields exactly, and the new record has exactly the keys overlay_digest, reviewer, date, overlay, scope (no `carried_from`), no "Astra" and no 8411f393... in it, reviewer Claude Opus 5.5 / dri-decider, date 2026-11-19, and a scope that names the nine terms and the overlay-read file. On the earlier Astra-carrying record it fails (`Extra items in the left set: 'carried_from'`).
- `test_the_generated_environment_keeps_every_owner_description`

It fails on pre-change main (14 failed, 8 passed: `evidence/condition-test-on-main.log`; the two rebind tests were added later and fail there too, because the evidence file does not exist on main). On the final tree: 24 passed (`uv run pytest -q tests/test_defs_repair_claude_constitution_excerpt_1119.py`).

## Tests run

- Selected run: `mac-pytest.sh --select -- --base f03cafb9d2 --run` on HEAD 7eefe1ef. It recorded 615 units with 1 failure, `tests/test_english_lean_lexicon.py::test_every_corpus_environment_has_a_valid_selected_lexicon` (the lexicon report above). After the regeneration, that test and tests/test_english_lean_seal.py ran: 2 passed (`evidence/selected-run-summary.txt`).
- `tests/test_english.py::test_reviewed_overlays_preserve_all_historical_views_and_identities` (unchanged) passes; it is in the seeded-bug runs below.
- trust_mutants: light lane printed NOT (802 lines; most are regenerated reports and evidence), so the sweep ran through `mac-pytest.sh --trustmut`. Result: 0 definitions, 0 mutants, exit 0 (`trust-mutants.json`).
- No main-known-red test was involved.

## Seeded bugs

All of these are in data files; no Lean, Python or Rust product code changed. Listed in `mutants.json`, log in `evidence/seeded-bugs.log`. Each was planted, run against the new file plus the overlay test, then restored with `git checkout`.

| id | file | bug | failing tests |
|---|---|---|---|
| M1 | usecases/claude-constitution-excerpt/environment.json | drop "in forming an overall judgment, " from the outranks span | 5, incl. `...carried_word_for_word[...-8-1119-environment.json]` |
| M2 | usecases/claude-constitution-excerpt/definitions-environment.json | generated copy desynchronised (property span shortened) | `..._keeps_every_owner_description`, `...[...-1-1119-definitions-environment.json]` |
| M3 | usecases/claude-constitution-excerpt/environment.english.json | an overlay byte other than environment_id | `..._carried_only_by_the_environment_id_rebind`, `test_reviewed_overlays_preserve_all_historical_views_and_identities` |
| M4 | ve/reviewed-overlays.json | the new record's digest changed | the same two |
| M5 | usecases/claude-constitution-excerpt/environment.json | curly quotes around "tie-breakers" (equal after normalisation, not byte for byte) | 5, incl. `...[...-8-1119-environment.json]` |

## Spec re-read

- The rows' quote column against source.md:16-19, 21, 30, 32-33 (script `span==quote` for all 7).
- The carrier rule against METHOD.md section 3 and amendment 3 (complete span, defined term included).
- The overlay record and test against the DRI note 2026-11-19 (superseding decision item 1(a)) and decision item 1(b): reviewer text, date, no `carried_from`, scope citing the overlay-read file, both proofs.
- The DELTA cells against DRI-RULINGS.md R3 and the decision's DELTA line.

## Pilot bytes expected to move (estimate, not claimed)

The audit's 16 PARTIAL pairs (excerpt.md "Counts") lose 14 P1 pairs to CARRIED on the next read: C1 x D1-D4, C2/C9 x D1, D6, C3 x D2, C6/C7/C8 x D1-D5, C10/C11 x D7. The 2 P2 FORMALISED pairs (C4, C5) stay.

SIZE: 16 product (data: environment.json 7, ve/reviewed-overlays.json 8, environment.english.json 1), 138 tests, 123 other hand-written lines (REPORT 115, DELTA 8). Generated and saved evidence are not counted.

## Notes for the DRI

- source.md:39 says sentences 1-3 and 10-21 of its numbered list are "paraphrases (close to the source wording ...)" while also saying they are "reproduced faithfully". Rows 4 and 9 (sentences 18, 20-21) are therefore carried as the in-repo source.md has them, per amendment 8. Whether they match the published constitution byte for byte cannot be checked inside the repo.
- definitions-report.md now says "Python, Lean" (Rust's runner no longer evaluates this case on main). The agreement claim of verify_definitions.py is no longer three-way. That is pre-existing on main, not a defect this item introduces.
- The excerpt environment_id in s0-report.json is left at the dated value; see the FOLLOW-UP below.

FOLLOW-UP: english-lean-s0-remeasure Re-measure conformance/english-lean/s0-report.json on current main (regeneration changes unrelated recorded measurements) and update the excerpt's environment_id there

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relayed answer or schema touched).
2. Deliverables built, no rule broken: PASS. Deliverables 0-3 above; s0-report is the one derived file left, with its reason and a FOLLOW-UP. The diff adds no Python copy of a Lean decision and no permanent report test.
3. Tests can fail: PASS (M1-M5, mutants.json; the condition test fails on main, evidence/condition-test-on-main.log).
4. Py/Lean/Rust agree: N.A. (no checker code changed; verify_definitions.py ran Python and Lean, which agree on all eight values).
5. R8 binding: N.A. (no relayed field).
6. Gate evidence matches final HEAD: PASS for what this item controls (main merged at f03cafb9d2; the gate is the chain's, on the final HEAD).
7. No unsigned item: PASS (DELTA rows cite R3, per the DRI decision; no SIGNED cell).
8. Every user-visible change in DELTA: PASS (legend text and the derived id/digest; the review status is unchanged: test_reviewed_overlays_preserve_all_historical_views_and_identities).
9. Test selection finds the tests: PASS (the selected run picked the new file first and found the lexicon report test).
10. Lean statements: N.A.
11. Budgets and deadlines: N.A.
12. CPU/memory: N.A. (legend text only).
13. Test-removed trailers: N.A. (no test removed or renamed).
14. Both directions, cited evidence, spec re-read: PASS. The carry test refuses on main and accepts after. The rebind test accepts the rebind and refuses other bytes (M3) and a wrong record (M4). Claims cite commands above.
15. No overclaim, no silent cut, checks can fail, limits: PASS / PASS (s0 named) / PASS (M1-M5) / N.A.
