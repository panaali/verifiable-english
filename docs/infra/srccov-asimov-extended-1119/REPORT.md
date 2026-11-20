# srccov-asimov-extended-1119: source-coverage rows of asimov-extended (no rule line)

- **Status:** row s7-1 (S0005) KEPT and carried. Row s7-2 (S0007) DROPPED: its record file `rules.ve` cannot hold a comment. The S0007 recording is not done (see FOLLOW-UP). Trust +0. No DELTA row. Nothing waits on a DRI signature.
- **VE commit:** rebased onto main `12cb72fa55`, which this merges at. HEAD is the last commit on `infra/srccov-asimov-extended-1119`. The code was last tested at `c2e75afd75`.
- **What changed:** the ten addition legends in `usecases/asimov-extended/environment.json` carry S0005's clause `written by "the Asimov extension author" for this use case` word for word. The derived ids were regenerated with the project's tools. A new condition test: `tests/test_srccov_asimov_extended_1119.py`.
- **Open:** one FOLLOW-UP (S0007 has no record form). The dependency `defs-repair-asimov-extended-1119` is merged (main `24e3ac848a`). It carried S0009 (E3), E1, E2a and E2b. It carried neither S0005 nor S0007.

## 0. Verify table (map at pin `e53db4e8fc`, checked against current main `12cb72fa55`)

Every step below used the in-repo source `usecases/asimov-extended/source.md`, which has no hash pin. The unit ids, offsets and text come from `reviews/source-coverage-1119/units-asimov-extended.tsv`.

| row id | KEPT / DROPPED | units kept | reason |
|---|---|---|---|
| srccov-asimov-extended-s7-1-1119 | KEPT | S0005 | **The text is in the source:** `source.md:26-27` "Rules 14–29 in [rules.ve](rules.ve), after the 13 lines of `base.ve`, are **this project's additions**, written by "the Asimov extension author" for this use case."<br>**Not carried at main:** clause c1 is carried in other words by the existing "as derived by addition rule N … (authored, not Asimov's)" on each addition legend. Clause c2 occurs on no legend: `grep -n "written by\|rank laws" usecases/asimov-extended/*.json *.ve *.py` on the main tree found nothing, and the condition test fails on main's legends (11 failed, below). "decided by the Asimov extension author" on `less_severe_competitor` and `beaten_by_a_candidate` is S0009's attribution of the severity order, not S0005's.<br>**The carrier carries under amendment 4:** each of the 10 legends belongs to a predicate that a rule line of `rules.ve` derives (rules 14-17, 20-23, 25-29). This is checked by `test_the_carrier_is_the_legend_of_a_predicate_the_additions_use`.<br>**Scope:** no rule or fact line, no language feature, no theorem, no trust and no DELTA row. |
| srccov-asimov-extended-s7-2-1119 | DROPPED | none | **The record cannot be written.** The row's carrier is a comment in `rules.ve` above rule 14, and comments in `base.ve`/`rules.ve` are the only record form METHOD section 0 allows for this document. The norm-English reader has no comment line: in `parse_english`, every line that is not a precedence line must be the block `Rule N.` (`ve/norm_english.py:322`, "Expected Rule {index} with its own block"). Two more constraints apply. `tests/test_asimov_extended.py:120` requires that `rules.ve` equal its own rendering (`render_english(doc) == (text, manifest)`). `tests/test_asimov_extended.py:101-105` keeps `base.ve` equal to v2's bytes. A record would therefore need comment syntax, which is a new language feature and out of scope. This is pinned by `test_s0007_has_no_record_form_in_rules_ve`. |
| RECORDING S0007 | DROPPED | none | Same reason as row s7-2: neither allowed record file (`base.ve`, `rules.ve`) can hold a comment (`ve/norm_english.py:322`). Not recorded. See FOLLOW-UP. |

No other row was found. The map's other 11 units are CARRIED-OTHER-WORDS (asimov-extended.md table), and this item does not re-audit them.

## 1. Rows carried

**s7-1, S0005 (legend append, word for word).** The source clause `written by "the Asimov extension author" for this use case` (`source.md:27`) now sits right before the closing tag `(authored, not Asimov's)` on these legends:

- `lawful_action` (`environment.json:199`)
- `candidate_action` (:209)
- `possibly_harmful` (:219)
- `valid_order` (:229)
- `prevails_over` (:240)
- `overridden_order` (:250)
- `own_robot_harm` (:261)
- `competes_with` (:272)
- `less_severe_competitor` (:283)
- `beaten_by_a_candidate` (:293)

These are exactly the 10 keys of the row's `carrier_key`, and the 10 legends that carry the tag (`test_the_carried_clause_is_on_exactly_the_tagged_legends`). Example: "The action breaks neither the First nor the Zeroth Law, as derived by addition rule 14, written by "the Asimov extension author" for this use case (authored, not Asimov's)".

The map's change said "append to each tag". The clause goes before the tag instead, because `tests/test_asimov_extended.py:144` keeps the tag last on every addition legend. That is the use case's own invariant. The first placement, after the tag, failed it in the first selected run (`/tmp/ae-select.log`: "1 failed, 16 passed": `test_the_environment_extends_v2_without_changing_it`). The clause was then moved, and the test was not changed.

## 2. Derived files (regenerated with the project's tools only)

- **`usecases/asimov-extended/rules.manifest.json` and `base.manifest.json`:** `environment_id` and `document_hash` changed. `blocks` and `text_digest` stayed byte-equal (asserted by the regeneration script). They were written with the document's own `asimov_extended_cases.render_manifest()`, in the file's existing format (`json.dumps(indent=2)+"\n"`), as defs-repair did. The script checked that the rendered text equals `rules.ve`/`base.ve`.
  - `environment_id`: `6aad3e37…` → `a5dda6ba…`
  - rules `document_hash`: `3494fff9…` → `a916654f…`
  - base `document_hash`: `2f9b3f05…` → `a6aaa116…`
  - `git grep` finds none of the old values.
- **`conformance/english-lean/lexicon-report.json`:** the asimov-extended `lexicon_id`, written by `uv run python -m conformance.english_lean_lexicon` (43 valid, 0 invalid). This file is not in the row's `derived_files` or in the task's path list. `tests/test_english_lean_lexicon.py` requires it (defs-repair found the same).
- **`conformance/english-lean/corpus-seal.json`:** written by `uv run python -m conformance.english_lean_seal`, which renews the whole seal. `--check` gives "0 difference(s)" at HEAD. The new seal:
  - pins the new `environment.json` sha256;
  - adds `tests/test_srccov_asimov_extended_1119.py` as an "entry-point caller", because the test calls `parse_english`;
  - re-pins `usecases/safety-framework/environment.d1.json` to main's current bytes. That entry was already stale on main: `--check` at main `09bea0972d` gave "changed: usecases/safety-framework/environment.d1.json".
- **`uv run python tools/regen_generated.py --check`:** fails only `route-cases` and `checker-pins`, both because this worktree has no Rust binary ("missing Rust executable …/rust/target/release/ve"; "the Rust release binary is missing or not pinned"). This item touches no route, Lean or Rust file. All other checks pass (`/tmp/srccov-ae-regen.log`).

## 3. Answers touched

None. `usecases/asimov-extended/answer-key.json` and `results.json` are unchanged (`git diff --quiet main...HEAD -- …` → "answers unchanged"). `tests/test_asimov_extended.py` recomputes the key and the results, and it passed in the final selected run. Later reads that pin this document must re-pin:

- `environment_id` `a5dda6ba…`
- rules `document_hash` `a916654f…`
- base `document_hash` `a6aaa116…`
- the content sha256 of `environment.json`, now `8ccd287b…` (it was `b0f4d368…`)

## 4. Condition test

`tests/test_srccov_asimov_extended_1119.py`, 33 tests:

- `test_the_clause_is_the_source_text_of_s0005` reads the S0005 sentence from `source.md` by its first and last words. It must start a paragraph and occur once. After `omit_norm`, the sentence must end with the clause.
- `test_s0005_is_carried_word_for_word_on_the_addition_legend[*]` (10): each legend contains the clause after `omit_norm`, right before the tag.
- `test_the_carrier_is_the_legend_of_a_predicate_the_additions_use[*]` (10): METHOD amendment 4. The predicate is in the head of its addition rules and in none of rules 1-13.
- `test_the_carry_only_inserts_the_clause[*]` (10): this is the opposite direction. With the clause removed, the legend ends with the tag and names exactly its own addition rules.
- `test_the_carried_clause_is_on_exactly_the_tagged_legends`.
- `test_s0007_has_no_record_form_in_rules_ve`: the drop reason. A `#`, `--` or `//` comment line before rule 14 raises "Expected Rule 14 with its own block".

Results:

- **On main's legends** (main's `environment.json` copied in, then restored): "11 failed, 12 passed" (`/tmp/srccov-ae-main2.log`). The 10 carry tests and the exact-set test failed. This was measured before the `test_the_carry_only_inserts_the_clause` tests were added, and those fail on main too, since `base == legend` there.
- **At HEAD:** "33 passed" (`/tmp/ae-t4.log`).
- **Selected:** `uv run python tools/select_tests.py --base $(git merge-base HEAD main)` plans this file and `tests/test_asimov_extended.py`, `test_defs_repair_asimov_extended_1119.py`, `test_english_lean_lexicon.py` and `test_english_lean_seal.py` (`/tmp/ae-plan.log`).

## 5. Seeded bugs (`docs/infra/srccov-asimov-extended-1119/mutants.json`)

The only carry kind is the legend append; no record was written. Every bug is in `usecases/asimov-extended/environment.json`, and each was restored afterwards (git status clean).

| id | bug | failing test |
|---|---|---|
| M1 | remove the carried clause from `lawful_action` | `test_s0005_is_carried_word_for_word_on_the_addition_legend[lawful_action]`, `test_the_carried_clause_is_on_exactly_the_tagged_legends` |
| M2 | unquote the author's name on `prevails_over` | `…[prevails_over]`, exact-set test |
| M3 | move the clause from `lawful_action` to v2's `ordered` legend | `…[lawful_action]`, exact-set test, `tests/test_asimov_extended.py::test_the_environment_extends_v2_without_changing_it` |
| M4 | put the clause after the tag on `competes_with` | `…[competes_with]`, `test_the_environment_extends_v2_without_changing_it` |
| M5 | drop the rule number from "as derived by addition rule 14" on `lawful_action` | `test_the_carry_only_inserts_the_clause[lawful_action]` |

No Lean, Python or Rust product code changed (`git diff --stat main...HEAD`: no file under `ve/`, `lean/` or `rust/`), so no per-language mutant is required.

## 6. Runs

- **First selected run** (`mac-pytest.sh --select`, before the clause moved): exit 1. "1 failed, 16 passed, 7 deselected", the tag-last invariant (section 1). `/tmp/ae-select.log`.
- **Targeted rerun after the fix:** the failed id, `test_every_rule_has_one_reading_in_plain_english`, this file, `test_defs_repair_asimov_extended_1119.py`, `test_english_lean_lexicon.py` and `test_english_lean_seal.py` gave "96 passed" (`/tmp/ae-t3.log`).
- **Final selected run** at `c2e75afd75`, tree `04cf61e374`: GitHub Actions, 3 shards, run `srccov-asimov-extended-1119-c2e75afd-t169019`, "25 passed / 25 passed / 22 passed", 0 failed, exit=0 (`/tmp/ae-select2.log`).
- **trust_mutants:** `light-lane.py check` gave "NOT 200 changed lines outside generated files > 150". The sweep ran through `mac-pytest.sh --trustmut`: "0 definitions, 0 mutants … 0 KILLED, 0 SURVIVOR", exit=0 (`/tmp/ae-trustmut.log`). No Lean changed.
- The full gate is left to the chain, as the task says.

## 7. DELTA

No DELTA row. No verdict, diagnostic (code, text, path), fault order, availability or answer changes:

- answers unchanged (section 3);
- `tests/test_asimov_extended.py` passed in the final selected run.

The only change a reader sees is the legend text this task asks for. The text is appended, and nothing is removed (`test_the_carry_only_inserts_the_clause`). Trust +0 (no Lean).

SIZE: 0 product, 122 tests, 10 other hand-written lines (`environment.json` legends), plus this REPORT and mutants.json. Generated: 4 manifest lines, 1 lexicon-report line, 11 seal lines.

FOLLOW-UP: srccov-asimov-extended-s0007-record-1119 Record S0007 (rationale, "The Three Laws rank laws, not harms, …") for asimov-extended: base.ve/rules.ve, its only record files, take no comment line (ve/norm_english.py:322), so the record needs a record form (a language feature)

## Notes for the DRI

- **S0007 and amendment 12.** S0007 contains the number word "Three", in the name "The Three Laws". Read strictly, amendment 12 ("a number") would make S0007 never out of scope, and so ABSENT and "absent, not recordable". Read as a name, it is rationale, as the map says. Either way it is not recorded here, and the FOLLOW-UP covers both readings.
- **The map's derived_files** named only the two manifests. Regeneration also changed `lexicon-report.json` and `corpus-seal.json`. Both were regenerated with their own tools.
- **The map's change text** ("append … to each tag") was applied as an insertion just before the tag, to keep the use case's tag-last invariant (section 1).

## Spec re-read

- The clause matches `source.md:27` byte for byte (with `omit_norm`), checked by `test_the_clause_is_the_source_text_of_s0005`.
- The row's carrier keys match `rows-asimov-extended.tsv` row s7-1 `carrier_key` (10 names, the same set as `CARRIERS`).
- METHOD amendment 4 (a legend of a used symbol) was re-read against `METHOD.md:61`. Amendment 13 (unit records) was re-read against `METHOD.md:44`. The record forms allowed for asimov-extended were re-read against `METHOD.md:13` ("comments in base.ve, rules.ve").

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relayed route or Lean answer changed.
2. Every deliverable is built: PASS for row s7-1, the condition test, the regeneration and the REPORT (`test_s0005_is_carried_word_for_word_on_the_addition_legend[*]`). Row s7-2 and the S0007 recording were dropped with a cited reason (`test_s0007_has_no_record_form_in_rules_ve`) and a FOLLOW-UP. This is not a silent cut.
3. Tests and gates can fail: PASS. M1-M5 (mutants.json); the test file fails on main's legends (11 failed).
4. Python, Lean and Rust agree: N.A. No product code changed. The final selected run passed (`/tmp/ae-select2.log`).
5. R8 binding: N.A. No relayed answer.
6. Gate evidence matches the final HEAD: PASS. The final selected run was on `c2e75afd75`. Later commits are this REPORT only. The full gate is left to the chain.
7. No unsigned item: PASS. No DELTA row; nothing reserved for the DRI.
8. Every user-visible change is in DELTA: PASS (none). Answers unchanged (`git diff --quiet` on answer-key.json and results.json); `tests/test_asimov_extended.py` passed in the final selected run.
9. Test selection finds the tests: PASS. The `select_tests.py` plan includes this file and `test_asimov_extended.py` (`/tmp/ae-plan.log`). M3 and M4 fail `test_asimov_extended.py::test_the_environment_extends_v2_without_changing_it`, which is selected.
10. Lean statements: N.A. No Lean.
11. Budgets and limits: N.A. No budget or limit code.
12. CPU and memory: N.A. Only a legend text change.
13. Test-removed trailers: N.A. No test was removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. `test_the_carry_only_inserts_the_clause` covers the opposite direction. Every claim above cites its log. See "Spec re-read".
15. No overclaim, no silent cut, new checks can fail, limits charged first: PASS. The universal words ("exactly the 10", "none", "unchanged") cite `test_the_carried_clause_is_on_exactly_the_tagged_legends` and the `git diff --quiet` and `git grep` commands. S0007 was not silently cut (FOLLOW-UP). M1-M5 cover the new checks. Limits: N.A.
