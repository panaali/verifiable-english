# fsf-repair-f1-leveldefs-1119 REPORT

Row F1 of reviews/pathf-q3/flag-analysis-1119/compare-report.md (converge-AB.md section 1): each capability level of
the safety-framework case now carries its source definition verbatim, in the vocabulary legend of a predicate that the
level's `levels-*` fact block uses. LANGUAGE only. No Lean, Python or Rust decision path changes. Trust +0, and no
DELTA row is reserved for the DRI.

SIZE: 33 product (vocabulary.py 27 added, facts.d1.ve 6 changed), 139 tests, 212 other hand-written lines (REPORT.md
183 at the count, DELTA.md 11, mutants.json 17, tools/gate-optional.json 1); generated or recorded outputs:
environment.d1.json +7, results.json 3, coverage.json 1, route-cases.jsonl 1, lexicon-report.json 2 (`git diff
--numstat $(git merge-base HEAD main)` after the rebase onto e53db4e8fc).

## Deliverables

| # | Task line | Done | Where | Test |
|---|---|---|---|---|
| 1 | Each capability level's source definition VERBATIM, one sentence per level, with the footnote marks the source has, on a fact line in `levels-*` or the legend of the level's predicate | Yes, for all 7 levels | `vocabulary.py` `BASE["defined"]`: one legend, one entry per level (`<level> is <name> (<table or section>), defined as "<sentence>"`). `facts.d1.ve`: one fact `"<level>" is defined.` per level, added to the level's own `levels-*` block (levels-cbrn holds two). `environment.d1.json` is rewritten by `vocabulary.py`. | `test_every_level_has_its_definition_in_the_legend_of_a_predicate_its_block_uses` |
| 2 | The condition test, reading each sentence from the pinned source, byte for byte after the project's quote normalisation; fails at 7cbec4b340b8, passes after | Yes | `tests/test_fsf_repair_f1_leveldefs_1119.py` (a new file, as PARALLEL SIBLINGS asks) | `test_every_level_legend_quotes_the_pinned_source_definition_verbatim` (seeded bug S1 is the 7cbec4b340b8 text: it fails) |

### The carrier, and why one predicate rather than one per level

The carrier guard (converge-AB.md section 0) counts a legend only if it belongs to a predicate the block uses. The
reads-1119 counter decides "uses" with `used_predicates`: a verbalisation match or `classified as "<name>"`. The
LEVELS constant strings and the `## ` headers are not changed.

- **First attempt (not kept).** I gave each level its own predicate, `defined_as_<level>`. `run.py` then wrote seven
  `identifier_lint` violations into `results.json` ("predicate defined_as_cbrn_uplift_tcl", ...). PLAN P7/M5 requires
  0 violations, because no predicate name may contain a constant name or a digit. I reverted it in the same session,
  and it was never committed.
- **Kept.** There is one predicate, `defined` (arguments `["level"]`, verbalisation `{0} is defined`). Its legend
  names each level by its constant and quotes that level's sentence after it. Each `levels-*` block states
  `"<level>" is defined.`, so the block uses `defined` and the counter shows the legend with that block.
  - `run.identifier_lint()` gives `[]` (the results.json `violations` field is unchanged).
  - "is defined" occurs in no rule block and in no case (`grep -c "is defined"`: rules.d1.ve 0, cases.json 0,
    facts.d1.ve 6). The legend therefore appears only with the `levels-*` blocks and with the FACTS unit.
- **Counter's legend cuts.** The legend does not begin with a section citation, so the counter does not treat it as
  a provenance string. Its parenthesised citations, such as "(table 2.2.1.a)" and "(the 8 is the mark of footnote
  8)", are the parts the counter cuts. The quoted sentences hold no digit in parentheses, so the counter keeps them
  whole.
- **Size.** The whole entry is 26 lines of vocabulary.py, under legend_raw's 40-line read.

## Source passages (verbatim, pinned text fsf-3.1.txt, sha256 18e3375b…3c53946; "p." is the PDF page = text line)

Each sentence was printed by `source_definitions()` of the new test from the stored pinned text. The byte offsets
come from `data.index(sentence)`.

| Level | Location | Bytes | Sentence |
|---|---|---|---|
| cbrn_uplift_tcl | 2.2.1, "The CBRN TCL is defined as follows: CBRN uplift TCL :", p. 11 | 31701-31868 | Provides low to medium resourced actors uplift in reference scenarios, resulting in material risk of CBRN attacks that could result in significant but not severe harm. |
| cbrn_uplift_level_1 | table 2.2.1.a, p. 11 | 31082-31208 | Provides low to medium resourced actors uplift in reference scenarios resulting in additional 8 expected harm at severe scale. |
| cyber_uplift_level_1 | table 2.2.2.a, p. 12 | 32305-32408 | Provides sufficient uplift with high impact cyber attacks for additional expected harm at severe scale. |
| harmful_manipulation_level_1 | table 2.2.3.a ("Harmful manipulation level 1 (exploratory):"), p. 12 | 33330-33602 | Possesses manipulative capabilities sufficient to enable it to systematically and substantially change beliefs and behavior in identified high stakes contexts over the course of interactions with the model, reasonably resulting in additional expected harm at severe scale. |
| stealth_and_situational_awareness_tcl | 3.2.1, "The Stealth and Situational Awareness TCL is defined as follows: Stealth and Situational Awareness TCL :", p. 14 | 39567-39900 | The instrumental reasoning abilities of the model enable enough situational awareness (ability to discover and use relevant details of its deployment setting) and stealth (ability to circumvent basic oversight mechanisms) such that, absent additional mitigations, we cannot rule out the model significantly undermining human control. |
| ml_rd_acceleration_level_1 | table 3.2.2.a, p. 15 | 41134-41252 | Has been used to accelerate AI development, resulting in AI progress substantially accelerating from historical rates. |
| ml_rd_automation_level_1 | table 3.2.2.a, p. 15 | 41973-42126 | Can fully automate the work of any team of researchers at Google focused on improving AI capabilities, with approximately comparable all-inclusive costs. |

**Differences from the task text.**

1. The task says "about 10 levels". The source defines 7, the same 7 as `vocabulary.LEVELS`, and the condition test
   asserts `set(SOURCE_LABELS) == set(vocabulary.LEVELS)`. The levels in the task's list map as follows:
   - "Stealth and instrumental reasoning levels" is the one Stealth and Situational Awareness TCL, whose definition
     begins "The instrumental reasoning abilities".
   - "ML R&D" is two levels: acceleration level 1 and automation level 1.
2. The task's example sentence for CBRN uplift level 1 matches the source. In the extracted text, footnote mark 8
   follows "additional" ("additional 8 expected"), and the legend keeps it there, as the task asks. The legend then
   adds "(the 8 is the mark of footnote 8)", a parenthesis that the counter cuts as a citation.
3. No other definition sentence holds a footnote mark. Marks 12 and 13 in table 3.2.2.a belong to the
   security-level column ("Security level 3 12", "Security level 4 13"), not to a definition, so they are not
   carried.
4. The extracted text has a space before the colon in two labels ("CBRN uplift TCL :" and "Stealth and Situational
   Awareness TCL :"). Only the sentences after the labels are quoted, so the space does not enter any legend.

## Tests

- `tests/test_fsf_repair_f1_leveldefs_1119.py` has 3 tests, all passing locally (`uv run pytest -q
  tests/test_fsf_repair_f1_leveldefs_1119.py`: "3 passed", /tmp/f1-t2.log).
  - `..._in_the_legend_of_a_predicate_its_block_uses` is hermetic and needs no source. It checks:
    - the committed legend equals the vocabulary's own;
    - each level's entry is present, once, in LEVELS order, cites the level's own table or section, and quotes one
      sentence;
    - the fact sits in the level's own block, and nowhere else;
    - the parsed formula is `defined(<level>)`.
  - `..._quotes_the_pinned_source_definition_verbatim` is the condition test. It reads each sentence from the pinned
    text (`tests/pinned_source.py`) and checks `"norm(sentence)"` against `norm(entry)` for both the built and the
    committed legend. `norm` is `tools/fidmech/segment.py` norm, the project's quote normalisation: it folds
    whitespace, quote styles, dashes and ligatures, and keeps digits.
  - `..._reader_takes_the_whole_sentence_and_one_label_only` checks the sentence reader in both directions. A full
    stop ends a sentence, while a digit inside it stays. A missing label, or one that occurs twice, is refused.
- The condition test's pinned-source skip is allowed in `tools/gate-optional.json`, with the same reason as the
  Glossary-definition test (`test_every_glossary_definition_is_the_pinned_source_text`). On Actions,
  `VE_REQUIRE_PINNED_SOURCES=1` turns that skip into a failure (`tests/pinned_source.py`), so R18 gains no skip on
  Actions.
- Selected run: see "Selected run" below.

## Regenerated outputs (each from its own writer; none edited by hand)

- `usecases/safety-framework/environment.d1.json`: written by `uv run python usecases/safety-framework/vocabulary.py`.
- `usecases/safety-framework/results.json`: written by `uv run python usecases/safety-framework/run.py` (rc 0,
  /tmp/f1-run2.log). `premises` goes from 35 to 42, the seven new facts. Two `certificate_sha256` values move. No
  verdict, comparison row or violation moves (`git diff -U1`: those 3 lines only).
- `usecases/safety-framework/coverage.json`: written by `uv run python usecases/safety-framework/build_document.py
  --source /tmp/f1src/fsf-3.1.txt`, run on a /tmp copy so that `fsf.d1.ve.md` is not written under manage-agents.
  Only `document_sha256` changes, and `spans.json` is unchanged.
- `tests/data/route-cases.jsonl`: written by `uv run python docs/en-e3-norm/en-2b/route_fixtures.py --write`. Its
  `stale` case embeds this environment, so the change is required.
- `conformance/english-lean/lexicon-report.json`: written by `uv run python conformance/english_lean_lexicon.py`
  (`{"valid": 43, "invalid": 0}`). The FSF lexicon has one more symbol (85 to 86) and a new `lexicon_id`.
- `uv run python tools/regen_generated.py --check`: rc 0, "checked 41 entries". No regen_generated entry owns these
  files, so `--write` has nothing of this item to write.

## Seeded bugs (docs/usecases/safety-framework/fsf-repair-f1-leveldefs-1119/mutants.json)

Every bug below was planted in the worktree, run against the new test file, and restored with `git checkout HEAD --
usecases/safety-framework`. `git status` was clean afterwards.

| # | File | Bug | Failing test(s) |
|---|---|---|---|
| S1 | usecases/safety-framework/vocabulary.py (+ environment.d1.json, facts.d1.ve) | main's text, which equals 7cbec4b340b8's for these three files (`git diff --stat 7cbec4b340b8 d8758ce968` is empty) | both the hermetic test and the condition test (/tmp/f1-s1.log) |
| S2 | usecases/safety-framework/vocabulary.py | footnote mark 8 dropped from the CBRN uplift level 1 quote | condition test (/tmp/f1-s2.log) |
| S3 | usecases/safety-framework/vocabulary.py | names cbrn_uplift_level_1 and cyber_uplift_level_1 swapped, so each sentence sits under the wrong level | both (/tmp/f1-s3.log) |
| S4 | usecases/safety-framework/facts.d1.ve | the stealth TCL's `is defined.` fact removed, so the block no longer uses the predicate | hermetic test (/tmp/f1-s4.log) |
| S5 | usecases/safety-framework/vocabulary.py | a quote cut in vocabulary.py while environment.d1.json stays stale | both (/tmp/f1-s5.log) |

These cover each changed language: Python (vocabulary.py) and VE text (facts.d1.ve). No Lean or Rust changed.

## Trust

- `uv run python tools/trust_map.py --check` reports "against e53db4e8fc38 (after the rebase): K +0, S +0, D +0, G +0, tied +0,
  unclassified +0, trusted +0" and PASS.
- `uv run python tools/trust_mutants.py --plan` reports `{"definitions": 0, "mutants": 0, "to_run": 0}` (no Lean).
- The light lane reports NOT: "199 changed lines outside generated files > 150", because it counts the test file and
  the recorded outputs. A sweep therefore runs as usual, but its plan has 0 mutants, so it has nothing to run. No R16
  or R6 allowance is recorded, and no FOLLOW-UPS row is needed.

## Prompt size

The counter version reads-1119 (R16 C5) is NOT installed:
- `tools-local/uc-audit.py` is the Nov 16 file, byte-identical to `uc-audit.py.bak-20261119-r16`.
- `uc-audit.py.reads-1119` sits beside it, but it is not the counter that runs, and `grep -c seq_unit_legends
  tools-local/uc-audit.py` gives 0.

So I did not run the dry-run, and the decider re-checks at the counted read. Estimate only (not a measurement):
- The `defined` legend is 1,987 bytes, and its environment.d1.json entry is 2,079 bytes. The six fact blocks grow by
  about 170 bytes of fact text.
- Under C5, `seq_unit_legends` adds one legend line of about 2,000 bytes to each rendered `levels-*` unit and to the
  FACTS unit.
- converge-AB gives the largest prompt now as 105,768 bytes. Against the 131,000-byte limit, that leaves room for
  about 12 such renders in one prompt.

## Pilot bytes expected to move (estimate; nothing is claimed before a pilot audit)

The six fact units anchored on the level definitions are:
- s221-ccl (CBRN uplift level 1 row)
- s222-ccl
- s223-ccl
- s321-tcl
- s322-acceleration
- s322-automation

Each now carries its definition in a legend of a predicate its block uses. The CBRN TCL definition (unit s221-tcl,
routed D2) is carried by the levels-cbrn block, the block that holds the TCL's facts.
- Expected effect: row F1's flags, which touch 136 answers and clear 13 alone (S1-L2, S1-L5, S1-L6, S2, S5, S6).
  These are the analysts' upper bounds.

## Selected run

- `zsh mac-pytest.sh --select -- --base d8758ce968 --run` ran at e0913623, the pre-rebase HEAD. Its log is
  /tmp/fsf-repair-f1-leveldefs-1119-select.log, and its exit code is 0.
  - "recorded 77 units for tree 72a24fafab; 1 others left to the static graph until they run; 0 failed".
  - The summary reads "ran LOCALLY (VM) because: MAC_LAST_RESORT ...; exit=0; 5751s".
  - The selection included tests/test_fsf_repair_f1_leveldefs_1119.py, test_safety_framework.py (exit 0, 886 s),
    test_safetyfw_usecases.py (exit 0), test_pinned_sources.py and the fidmech tests.
  - The run deferred one file to the chain gate as selected only for weak reasons:
    tests/test_relay_binding_inventory.py.
- An earlier attempt was stopped and is not evidence. Another item had written to the same /tmp log name, so I killed
  only my own job's session and restarted under a unique log name.
- **Rebase.** After the run, main gained the merges of fsf-repair-f9-mcca-1119 and others, so I rebased onto
  e53db4e8fc as the task asks.
  - Main changed nothing under lean/ or rust/ (`git diff --stat d8758ce968 main -- lean rust` is empty), and it did
    not touch facts.d1.ve or this item's vocabulary.py lines.
  - The only conflicts were the four recorded outputs. Each was rewritten by its writer on the rebased tree. results.json
    again moves only `premises` 35 to 42 and two `certificate_sha256` (/tmp/f1-run3.log).
  - After the rebase: `regen_generated.py --check` returns rc 0. `uv run pytest -q tests/test_fsf_repair_f1_leveldefs_1119.py
    tests/test_safety_framework.py::test_environment_file_is_generated
    tests/test_safety_framework.py::test_span_accounting_is_complete
    tests/test_pinned_sources.py::test_gate_optional_still_allows_the_unset_skips` gives "6 passed"
    (/tmp/f1-post-rebase.log).
  - The full gate runs on the final HEAD in the chain.

## Merge commit

The VE commit this merges at is this branch's final HEAD, rebased on main e53db4e8fc. The task's pinned commit
7cbec4b340b8 and the first base d8758ce968 have the same vocabulary.py, facts.d1.ve and environment.d1.json, so S1
is the 7cbec4b340b8 text. Main e53db4e8fc adds F5's and F9's legend changes, which this item keeps. The R16 C2/C3 pinned lists are per commit, so the counted read re-pins. A merge after
the R16 diagnostic voids that diagnostic for the touched answers.

## Notes for the DRI

- Main-known-red: the selected run had 0 failures, so it showed no pre-existing failure.
- The `defined` legend holds all seven definitions, so a reader of one `levels-*` block also sees the other six. A
  per-level legend is not possible under P7 without a lint violation.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. This item adds no relay, mode or Lean answer.
2. Every required deliverable built, no rule broken: PASS. Both deliverables are built (table above).
   - The identifier lint stays at 0 violations: results.json `violations` is `[]`, from `run.py`.
   - The carrier rule holds: `test_every_level_has_its_definition_in_the_legend_of_a_predicate_its_block_uses`.
3. Tests can fail: PASS. Seeded bugs S1 to S5 each fail a named test (mutants.json). S1 is the 7cbec4b340b8 text.
4. Python, Lean and Rust agree: N.A. No product decision code changed. `run.py` gives the same verdicts.
5. R8 binding: N.A. There is no relayed answer.
6. Gate evidence matches the final HEAD: PASS for what I ran (selected run at e0913623, plus the post-rebase checks
   above). The chain runs the full gate on the final HEAD.
7. No unsigned item: PASS. DELTA.md has no row and no signature.
8. Every user-visible change in DELTA: PASS. DELTA.md states there is no VE change. The results.json diff is
   premises and two hashes only (`git diff -U0`).
9. Test selection finds the tests: PASS. `tools/select_tests.py --base ...` listed the new test file,
   test_safety_framework.py and test_safetyfw_usecases.py, not every unit (/tmp/f1-sel.log). The changed files are in
   its "changed:" line.
10. Lean statements: N.A. No Lean changed.
11. Budgets and limits: N.A. No evaluator, runner or limit is added.
12. No CPU or memory regression: N.A. Seven more premise facts over a fixed predicate. `run.py` took about 4 min, as
    before (/tmp/f1-run.log, "real 4m5s").
13. Test-removed trailers: N.A. No test is removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS.
    - Both directions: `test_the_source_definitions_reader_takes_the_whole_sentence_and_one_label_only` accepts the
      whole sentence, and refuses a missing label and a duplicated one. S2 and S5 show the verbatim check refusing a
      one-word change.
    - Spec re-read: the carrier against converge-AB.md section 0 ("a Rule or fact line ... or a vocabulary legend
      of a predicate that block uses") and uc-audit.py.reads-1119 `used_predicates` / `_omit_legend_segments`.
      "One sentence per level, with the table's footnote marks" against the task text and compare-report.md row
      F1.
15. Overclaim, silent cut, every check can fail, limits: PASS / N.A.
    - Universal words in this report ("every", "no", "unchanged") each cite a command or test above.
    - Nothing is cut.
    - Each new test has a seeded bug.
    - No limit is involved.
