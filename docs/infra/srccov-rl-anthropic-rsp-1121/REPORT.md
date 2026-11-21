# srccov-rl-anthropic-rsp-1121: REPORT

| unit id | row id | KEPT / DROPPED | reason (file:line) |
|---|---|---|---|
| S0189 | srccov-anthropic-rsp-27-1119 | DROPPED | Attitude content: the document records "we will likely analyze ... collectively" as an expectation, `believes("expects")` (usecases/anthropic-rsp/build_document.py:399; spans.json s33-groupings, kind `attributed`). It waits for srccov-design-attributed-1119. A rule line would also have to choose whether "with appropriate justification" sits under "likely". |
| S0190 | srccov-anthropic-rsp-28-1119 | DROPPED | Needs a new regulated act ("have the Risk Report drafted ..."). main's environment already has 64 regulated predicates, Lean's limit: `if T.regulated.length > 64 then throw "ResourceLimit: regulated predicates"` (lean/VE/SoftNorms/Soften.lean:471; README.md:45 says "64 regulated predicates (Lean's limit)"). Tried and refused: adding the act made every RSP parse fail with `ResourceLimit: regulated predicates`. Raising the limit is a Lean change, out of scope. |
| S0192 | srccov-anthropic-rsp-28-1119 | DROPPED | The document reads "We may also use this feedback ..." as hedged "could" exposition: `hedged()` = `label(["hedged", "could", "exposition"])` (build_document.py:402; usecases/safety-framework/build_document.py:150). A permission line picks the deontic reading, or would need a new PLAN 3.1 RS6 reading set. That is a reading decision, not a plain line. Took the conservative option. |
| S0195 | srccov-anthropic-rsp-28-1119 | DROPPED | Already carried at main. The `executive_submitted` legend quotes the whole sentence (usecases/anthropic-rsp/rsp_vocabulary.py:647; srccov-anthropic-rsp-1119 row 17, tests/test_srccov_anthropic_rsp_1119.py CARRIES "row17"). That predicate is used by rule f12-approval (rules.d1.ve:61). Its first clause is also an `omits:` reading (accounting.d1.txt:32). |
| S0219 | srccov-anthropic-rsp-29-1119 | KEPT | Lead-in "We will select external reviewers that:". Each of the three criterion rules keeps its commitment (RS0, "must"). Each legend quotes the lead-in together with its criterion (rsp_vocabulary.py:243-256). Record s361-select → f15-expertise. |
| S0220 | srccov-anthropic-rsp-29-1119 | KEPT | rules.d1.ve:83-84 f15-expertise; legend `candidate_lacks_expertise` (rsp_vocabulary.py:243); spans.json s361-select `rule: f15-expertise`, OT25 still open |
| S0222 | srccov-anthropic-rsp-29-1119 | KEPT | rules.d1.ve:85-86 f15-candid; legend `candidate_lacks_candid_incentives` (rsp_vocabulary.py:247); spans.json s361-candid `rule: f15-candid`, OT25 still open |
| S0224 | srccov-anthropic-rsp-29-1119 | KEPT | rules.d1.ve:87-88 f15-conflicts; legend `candidate_has_conflict_of_interest` (rsp_vocabulary.py:252); spans.json s361-conflicts `rule: f15-conflicts`, OT24 still open |

**Summary.** 4 of the 8 in-scope units are carried and 4 are dropped. No DRI signature is needed and no DELTA row
is reserved (DELTA.md has no rows). Trust is +0: no Lean, Rust or `ve/` file changed, and `trust_mutants`
planned 0 definitions. No keyed answer changes. Base: main e331b45943 (rebased from cebf4fd24f; section 7).
SIZE: 29 product, 136 tests, 50 other hand-written lines (product: rules.d1.ve 6, rsp_vocabulary.py 16,
build_document.py 3, accounting.d1.txt 3, README.md 1; tests: the new file 129, test_english_statement_blocks.py 7;
other: this REPORT and DELTA.md are not counted, mutants.json 34, seeded-bugs.log 13. Source: `git diff --numstat
main...HEAD`).

## 0. Verify first (map pin e53db4e8fc; checked against main cebf4fd24f, rebased onto e331b45943)

- **Scope.** The map lists 8 units tagged `none: translation omission` in the three rows
  (part-anthropic-rsp-s7.tsv rows S0189, S0190, S0192, S0195, S0219, S0220, S0222, S0224). S0195's overlap reading
  in part-anthropic-rsp-s6.tsv tags it `attribution-evaluation`. Its home shard, s7, tags it `none`. It is dropped
  either way, as carried.
- **Source.** Every quote was checked against the pinned rsp-3.4.txt (SHA-256 c7de7fe2..., 59,410 bytes; read
  through tests/pinned_source.py). The byte offsets were found with `bytes.find`, and each run occurs exactly once:
  "We will select external reviewers that:" 36952-36991, S0220 36996-37108, S0222 37262-37437, S0224
  37618-37679, S0190 32221-32313.
- **Not carried at main.** A grep for "subject matter", "draft", "conflicts of interest", "significant experience",
  "candid about", "reputational", "similar models", "redundancy" and "refine the report" over rules.d1.ve, facts.d1.ve,
  environment.d1.json, accounting.d1.txt, rsp_vocabulary.py and stage0.py found only unrelated text: f16-split-p's
  "subject matter expertise" and f19/f23's "draft". So S0189, S0190, S0192 and S0219-S0224 are not carried at main.
  S0195 is carried, as the table above says.
- **Carrier.** These are rules.d1.ve lines (soft-norms@0, one of the profiles the environment declares:
  `PROFILES = ["norms@0", "relational-fol@0", "soft-norms@0"]`, rsp_vocabulary.py:19), plus the legends of what
  the lines use. No new language feature, profile, refuses pair, mode, route or listedStacks entry is needed, and no
  Lean, Python or Rust decision path changes. The rules reuse the existing regulated act `candidate_selected`.

## 1. Units carried

All three rules follow the form main already uses for 3.6.1, as f15-financial-interest does (rules.d1.ve:89-90):
"Every situation must not have the candidate selected as an external reviewer, if that situation is classified as
"<criterion failed>"." The narrowing column is RS0, because "We will select" is a commitment under N1, as for
f15-select-approval. Each condition is a new open-term base predicate decided by the company, and the open term is the
one the record already named (OT25 `ot25_reviewer_criteria`, OT24 `ot24_conflicts_of_interest`). Each legend is the
source's lead-in and criterion, quoted after "in the source's words (3.6.1):", outside any citation parenthesis.

- f15-expertise / `candidate_lacks_expertise`: “We will select external reviewers that: Have significant experience
  and expertise regarding evaluations for dangerous AI capabilities and propensities.”
- f15-candid / `candidate_lacks_candid_incentives`: “We will select external reviewers that: Have reputational and
  other incentives making them likely to be candid about their assessment of risks, rather than focused on writing
  comments that Anthropic will approve of.”
- f15-conflicts / `candidate_has_conflict_of_interest`: “We will select external reviewers that: Do not have conflicts
  of interest with respect to Anthropic.”

The quotes differ from the source only by the project's normalisation: the "ﬁ" and "ﬂ" ligatures are written as
plain letters, and the bullet sign "●" between the lead-in and the criterion becomes one space.

**Reading choice (conservative, not asked).** "We will select external reviewers that: <criterion>" is carried as a
prohibition: a candidate that fails the criterion must not be selected. It is not a duty to select some reviewer
who meets it. This is the narrower reading, and the same form main uses for the 3.6.1 "At a minimum" clause.
The failing predicates are positive atoms that no case stipulates, so no rule fires in any existing case.

Span records (build_document.py:429-433): `condition(...)` becomes `rule("<block>", <same open term>)`. spans.json
gives the three records a `rule` key. Their status stays OPEN, because the open terms are still open (the rows say
"open terms ot24, ot25 stay open").

## 2. Derived files (regenerated only by their writers)

- `uv run python usecases/anthropic-rsp/rsp_vocabulary.py` wrote environment.d1.json (+18 lines).
- `uv run python usecases/anthropic-rsp/build_document.py --source /tmp/rsp-src-1121/rsp-3.4.txt` (a copy of the
  pinned text, so rsp.d1.ve.md is written under /tmp and not in manage-agents) wrote spans.json and coverage.json.
  The printed totals are D1 CHECKED 4,676 / LABELLED 37,534 / OPEN 13,072 / UNFORMALISED 4,128, and master CHECKED
  5,320 / LABELLED 36,890. They are equal to main; only `document_sha256` changed.
- `uv run python usecases/safetyfw_accounting.py anthropic-rsp --source <pinned> --check --report
  docs/usecases/safetyfw/anthropic-rsp/accounting.json` → "88 blocks, 91 unaccounted words in 23 blocks, 2 blocks with
  a loss ..., 0 of 147 quotes unanchored", rc 0. The three new blocks have no unaccounted word.
- `stage0.py` wrote stage0.json (F15's block list); `measure.py --check` rc 0 (units.json and gaps.json unchanged).
- `docs/en-e3-norm/en-2b/route_fixtures.py --write` (route-cases.jsonl), `python -m conformance.english_lean_seal`
  (corpus-seal 8628bed5..., 111 sources), and `python -m conformance.english_lean_lexicon` (43 valid, 0 invalid;
  RSP 127 → 130 symbols).
- `uv run python usecases/anthropic-rsp/run.py` wrote results.json and printed "110 / 126". A structural diff against
  main's results.json shows only `/metrics/M10/rules 76 -> 79` and M5's F15 list.
- tests/data/norm-blocks/rsp.jsonl was recaptured with `capture_blocks.capture("anthropic-rsp", "rsp_translation")`,
  RSP only, as d255cbd9f4 did for FSF. The 3 rows are added, and every other row is unchanged apart from its commit
  (checked by an id/content diff). The count pins in tests/test_english_statement_blocks.py follow (rsp 79; 124
  pinned, 125 with f21, 108 strict).
- README.md:43 "76 VE rules" → "79 VE rules". It is bound by test_readme_figures_are_the_committed_measurements.
- Checks on the final product tree: `build_document.py --check`, `measure.py --check` and `stage0.py --check` rc 0;
  `tools/regen_generated.py --check` "checked 43 entries" rc 0; `python -m tools.fidmech boundaries --doc
  anthropic-rsp --check` rc 0.
- Not pinned here: tools/fidmech/manifests.py has no anthropic-rsp entry (grep). tests/data/fidmech/wording-golden.json
  and wording-inputs are frozen copies from fidmech b4 and are not inputs that this change reaches. fidmech/bindings.json
  is unchanged: no case stipulates OT24 or OT25, and its OT table has neither.

## 3. Answers whose status changes

None. results.json's `items` and `comparison` are byte-equal to main's (structural diff above). Per the conservative
rule, no CHECKED answer changes status or verdict, so no unit is stopped by this. What a later read shows does change,
so these re-pin:
- **K13** (results.json item: candidate_selected, rule f15-financial-interest, cone RS8revenue). Its act now has three
  more rules shown, f15-expertise, f15-candid and f15-conflicts. Their conditions are not stipulated by K13's case,
  so the selected rule, the cone and the verdict are unchanged. Justifying source: 3.6.1 "We will select external
  reviewers that: ● Have significant experience ... ● Have reputational and other incentives ... ● Do not have
  conflicts of interest with respect to Anthropic."
- K12a and K12b (f15-select-approval, the same section) are unchanged: their act is `reviewers_approved`.
- Hashes: environment.d1.json (corpus seal and lexicon_id), coverage.json document_sha256, spans.json (3 `rule` keys).

## 4. Condition test: tests/test_srccov_rl_anthropic_rsp_1121.py (12 tests, selected)

For each kept unit, the test checks that:
- the block and its exact rule line are in rules.d1.ve, with an RS0 header quoting the lead-in;
- its spans.json record names the block, covers the unit's bytes, and keeps its open term at OPEN;
- the legend holds the normalised source run byte for byte. The run is read from the pinned text, or checked by
  SHA-256 and length when the text is absent;
- the run survives the counter's citation cut, and the legend ends with its decider;
- the rule parses to a `candidate_selected` prohibition guarded by its predicate (skipped without the Lean service).

On main's carrier files (`git checkout main -- rules.d1.ve environment.d1.json spans.json rsp_vocabulary.py`, then
restored): "12 failed in 1.94s". On HEAD: "12 passed in 3.83s". `tools/select_tests.py --base $(git merge-base HEAD
main)` selects it: 90/678 units, including this file, test_english_statement_blocks.py, test_safetyfw_usecases.py,
test_safetyfw_accounting.py and test_srccov_anthropic_rsp_1119.py.

## 5. Seeded bugs (mutants.json; log evidence/seeded-bugs.log)

Each was planted by hand, run with `uv run pytest -q tests/test_srccov_rl_anthropic_rsp_1121.py`, and restored with
`git checkout`. Languages changed: Python (rsp_vocabulary.py, build_document.py) and VE text (rules.d1.ve). No
Lean or Rust product code changed.
1. rules.d1.ve: the f15-conflicts line removed (the required "remove one new line" check) →
   `test_each_kept_unit_has_its_rule_line_in_the_carrier[S0224]` and `test_each_rule_parses...[S0224]` FAIL (2 failed).
2. rsp_vocabulary.py (Python): the S0220 legend's "significant" → "substantial", environment regenerated →
   `test_each_legend_quotes_the_source_word_for_word[S0220]` FAIL.
3. build_document.py (Python): s361-candid back to `condition(...)`, spans regenerated →
   `test_each_kept_unit_routes_to_its_rule_and_keeps_its_open_term[S0222]` FAIL.
4. build_document.py (Python): s361-conflicts loses its open term (CHECKED) → `...keeps_its_open_term[S0224]` FAIL.

## 6. Tests run

- Selected run (`mac-pytest.sh --select -- --base cebf4fd24f --run`, on d94f986fde; log evidence/selected-run.log):
  one failure, `tests/test_english_statement_blocks.py::test_every_pinned_block_has_its_python_node[rsp]` (the
  pinned RSP blocks lacked the new rules). Every other selected file exited 0, including the chunked
  test_consolidation_tools.py (304 passed).
- Fix (28ba1e408b after the rebase; 235332eac9 before): the recapture in section 2. Rerun of the failed id plus the two tests whose pins moved
  (`test_lean_reads_each_pinned_block_as_python`, `test_each_pinned_block_through_the_mode`): "4 passed in 912.81s".
- trust_mutants (`mac-pytest.sh --trustmut -- --json /tmp/tm-1121.json`): "0 definitions, 0 mutants ... 0 SURVIVOR ...
  exit=0". The light lane said NOT (284 changed lines), so the sweep was run; `--plan` gave 0 definitions.
- `tools/gate_collection.py --check --prebuilt`: "12 added, 0 removed by a trailer, 0 refused, 0 stale and 0
  malformed". No test was removed.
- The full gate is run by the chain on the final HEAD (not run here, per the task).
- No test in main-known-red.txt failed in the selected run.

## 7. VE commit and freeze

The branch was built on main cebf4fd24f and rebased onto main e331b45943 (srccov-rl-claude-constitution-pilot-1121
merged in between). The only conflict was the shared conformance/english-lean/corpus-seal.json. main's version was
taken and regenerated with `python -m conformance.english_lean_seal` (64185f5b..., 111 sources), and the lexicon
report was regenerated. main's new commits change nothing under ve/, lean/, rust/, usecases/anthropic-rsp,
safetyfw_common.py, safetyfw_accounting.py or tests/data/norm-blocks (`git diff --stat cebf4fd24f main -- ...` is
empty), so results.json and the selected run's RSP results stand. After the rebase: `tools/regen_generated.py
--check` checked 43 entries, rc 0; the three builder `--check`s rc 0; the accounting report was rewritten to /tmp and is
byte-equal (`cmp`); the condition test gave 12 passed. The item merges at its merge-train commit on main after
e331b45943. That commit is not known yet, and the merge train records it. If it lands after Monday's FSF
freeze commit, it waits for a later freeze. Later RSP reads re-pin K13 and the hashes in section 3.

## 8. Notes for the DRI

- **The regulated-predicate cap.** RSP's environment is at Lean's 64-regulated-predicate limit (README.md:45). Every
  future RSP carry that needs a new act, not only S0190, is blocked until the limit or the vocabulary changes. The
  options are a kernel limit change or merging acts; either is a design item and not an omission repair.
- **Out-of-path files.** Two files outside this item's path list changed because a derived fixture had to follow:
  tests/data/norm-blocks/rsp.jsonl (recaptured by its tool) and its count pins in tests/test_english_statement_blocks.py.
  This follows the FSF precedent d255cbd9f4. A sibling (srccov-rl-safety-framework-1121) that adds FSF rules edits
  the same CASES line. On a conflict, take main's version and recount.
- docs/usecases/safetyfw/REPORT.md:27, 751 and 765 still say "76 rules". These are that batch's saved evidence at
  its own commit (line 751 also still says 303 units), so they are left as they are.
- The map's challenger note on S0192 ("a permission line (norms@0 has may) could carry it") is true of the grammar.
  It is not taken here because of the document's hedged reading (table above).

## 9. Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relay, schema or route changed.
2. Deliverables built, no rule broken: PASS. Deliverables 0-4 are in sections 0-4. No Python copy of a Lean
   decision, no report test (D4), and generated files come only from writers (section 2).
3. Tests can fail: PASS. 4 seeded bugs (section 5); the condition test fails on main (12 failed).
4. Python/Lean/Rust agree: PASS for what this reaches. test_lean_reads_each_pinned_block_as_python compares Lean's
   node with Python's for the 3 new blocks ("4 passed"). No Rust change.
5. R8 binding: N.A. No relayed field is read.
6. Gate evidence on final HEAD: PASS by process. Synced with main (unchanged); the chain runs the gate on the final
   HEAD.
7. No unsigned item: PASS. DELTA.md has no rows; trust +0 (trust_mutants 0 definitions).
8. Every user-visible change in DELTA: PASS. There is no VE behaviour change. The use-case changes are listed in
   DELTA.md, with results.json diffed (only M5 and M10).
9. Test selection: PASS. 90/678 units, including every test the seeded bugs broke (section 4).
10. Lean statements: N.A. No Lean changed.
11. Budgets and limits: N.A. No limit changed. S0190 was dropped rather than raising the 64 limit.
12. CPU/memory: N.A. Three rules with never-stipulated guards; run.py's answers are unchanged.
13. Test-removed trailers: PASS. gate_collection: 0 removed, 0 stale, 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS. The test fails on main and passes on HEAD, and seeded bugs
    cover each record field. Spec re-read: the three rules against the row's quotes (rows-anthropic-rsp.tsv:31) and
    METHOD amendment 8 (the lead-in's "will" kept as "must"; polarity kept as a prohibition on a failing candidate).
    The open terms against the row's "(open terms ot24, ot25 stay open)".
15. No overclaim / no silent cut / every check can fail / limits: PASS. Every dropped unit has a cited reason, and no
    deliverable was cut. "No answer changes" is the results.json diff (section 3). Limits: N.A.
