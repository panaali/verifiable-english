# fsf-repair-f3-safetycase-1119 REPORT

Status: built and ready for the chain's gate. No DRI signature is reserved, and DELTA.md needs no row.
Changed: the legend of `governance_found_acceptable_with_safety_case_where_ccl_reached` (the GOV / OT3 finding) now
carries the Glossary's Safety Cases sentence, copied verbatim from the pinned source. Recorded outputs that hash the
legend were regenerated.
Open: the reads-1119 counter (R16 C5) is not the installed counter, so I could not run the prompt-size dry-run (see
"Prompt size").
Base: main f5553bc894 (merged in at e9f70b1e95; built on d8758ce968). This item merges at its branch's final HEAD on
that base (see "Merge commit").

SIZE: 3 product, 64 tests, 170 other hand-written lines. Counted with `git diff --numstat` against the merge
base: vocabulary.py +3/-1, the new test file +64, plus DELTA.md and this REPORT. Generated or recorded outputs are not
counted.

## Source passage (taken from the source)

Pinned source: `~/code/manage-agents/pilots/safety-framework/source/fsf-3.1.txt` (sha256 18e3375b35c6..., 54,373 B).
This is the text that `usecases/safety-framework/source/extract_text.py` writes from the pinned PDF. The sentence is
in the Glossary, text line 20 (the last page), bytes 53440-53578. It falls inside unit `g-safety-cases` [53440, 53579]
of `spans.json` and occurs once (`bytes.count` = 1):

> Safety Cases: are an assessable argument showing how severe risks associated with a model's CCLs have been reduced to an acceptable level.

I read it with `python3 -c` (`find`, `count`) over the pinned file. It was not taken from any reader, flag,
diagnostic or analyst output.

**Deviation from the row's draft, toward the source.** The draft append was `a safety case "is an assessable
argument ..."`, which turns the source's "are" into "is". A verbatim carrier cannot make that change. The legend
instead quotes the whole source sentence, with its term, its "are" and its final period:
`; a safety case (Glossary: "Safety Cases: are an assessable argument ... to an acceptable level.")`. This form
matches F5's `low_risk` legend.

## Deliverables

| # | Task row | Delivered | Commit | Test |
|---|---|---|---|---|
| 1 | Append the Glossary Safety Cases sentence, verbatim, to the GOV legend (row F3) | `vocabulary.py` `BASE["governance_found_acceptable_with_safety_case_where_ccl_reached"]`: the description now ends `...; a determination without that safety case at a CCL is not this finding; a safety case (Glossary: "<the sentence above>")`. Its subject, open term OT3 and decider are unchanged. `environment.d1.json` was rewritten by its writer (`uv run python usecases/safety-framework/vocabulary.py`). | 83639ecf2a | `tests/test_fsf_repair_f3_safetycase_1119.py::test_the_governance_legend_quotes_the_glossary_safety_case_sentence_whole` |
| 2 | The condition test, in a new file | When the source is stored (it is on this machine and on the test runner: the selected run passed it), the test reads the sentence from `pinned_source("safety-framework")` after quote normalisation (whitespace collapsed, curly quotes made straight, the same normalisation as the pinned-source tests in test_safety_framework.py). It checks that the source holds exactly this one sentence, then asserts the sentence, in quotes, byte for byte in both the `vocabulary.environment()` legend and the committed `environment.d1.json` legend. It also asserts that f12-p, f12-u, f13-p and f13-u use this predicate and never `safety_case` (the carrier), and that the subject, OT3 and the decider are kept. Where the source is absent, it falls back to the test's copy of the sentence, so the legend check still runs and nothing is skipped. It fails on the pinned commit's text (seeded bug S1) and passes on HEAD. | 83639ecf2a, 33c4a96e5a | itself |

**Carrier guard** (converge-AB.md section 0). The sentence sits in the vocabulary legend (`description`) of the
predicate that the Rule lines of rules.d1.ve blocks f12-p, f12-u, f13-p and f13-u name (lines 52, 54, 56 and 58).
The test checks all four. None of the four uses `safety_case`. The
sentence is not in a header, a citation run or a constant table. Row F3 names no fallback.

**Kind call to check.** None differs on this row: A and B converged on LANGUAGE (B withdrew PROTOCOL-RENDER,
converge-AB.md F3). The reviewer should still confirm one point: that C5's used-legends render shows this legend for
the GOV answers.

Regenerated outputs, each by its own writer; none was edited by hand. Only hashes or the embedded legend move:
- `usecases/safety-framework/results.json`: `uv run python usecases/safety-framework/run.py`. Two `certificate_sha256` values change and no verdict changes (`git diff -U0`: 2 lines). The run printed the DISAGREE lines already recorded on main (e.g. G3 key ALL, VE NONE), unchanged.
- `usecases/safety-framework/coverage.json`: `uv run python usecases/safety-framework/build_document.py --source /tmp/f3src/fsf-3.1.txt`. I used a `/tmp` copy of the pinned text because the writer puts `fsf.d1.ve.md` beside its source. Only `document_sha256` changes. `spans.json` is unchanged.
- `tests/data/route-cases.jsonl`: `uv run python docs/en-e3-norm/en-2b/route_fixtures.py --write`. The `stale` case embeds this environment.
- `conformance/english-lean/lexicon-report.json`: `uv run python conformance/english_lean_lexicon.py` (`{"valid": 43, "invalid": 0}`).
- `uv run python tools/regen_generated.py --check`: rc=0, "checked 41 entries".

Not changed: the frozen fidmech inputs under `tests/data/fidmech/{wording,fp1}-inputs/safety-framework/`. They are
pinned by sha256 in `wording-golden.json` and are not mirrors of the live file. Also not changed: the `safety_case`
legend, which already quotes the definition and is not in F3's scope.

Out of scope and not touched: rows F1, F2 and F4-F9, RSP R1, and every Lean, decision or relay path.

## Seeded bugs (Python only; it is the only language changed)

I planted each bug in a changed file and ran `tests/test_fsf_repair_f3_safetycase_1119.py`. Each made the test fail
(rc=1). After each one I restored the tree with `git checkout HEAD -- usecases`, and `git status` was clean. The
restored tree passes (`/tmp/f3-restored.log`).

| id | File | Bug | Fails at |
|---|---|---|---|
| S1 | `usecases/safety-framework/vocabulary.py` + `environment.d1.json` | main's text, which is identical to the text at 7cbec4b340b8 | `assert f'"{sentence}"' in _quote_normal(legend)`, line 57 (/tmp/f3-s1.log) |
| S2 | `usecases/safety-framework/vocabulary.py` | the draft's "is" for the source's "are", in the quote only | same, line 57 (/tmp/f3-s2.log) |
| S3 | `usecases/safety-framework/environment.d1.json` | the committed environment is stale (main's) while vocabulary.py is new | same, on the committed legend (/tmp/f3-s3.log) |
| S4 | `usecases/safety-framework/vocabulary.py` | the quote's closing period dropped | same, line 57 (/tmp/f3-s4.log) |
| S5 | `usecases/safety-framework/vocabulary.py` | the decider "the appropriate governance function (unnamed)" becomes "the developer" | `assert legend.endswith(...)`, line 59 (/tmp/f3-s5.log) |

A first attempt at S2-S5 was invalid, and I redid it. The restore read main's files back from the index, so those
bugs ran on main's text. The table above is from the second run, which restored from HEAD.

No Lean or Rust code changed, so no seeded bug is needed there. Mutants per new trusted definition: none (trust +0).
Light lane: `light-lane.py check` printed "LIGHT 80 changed lines outside generated files <= 150 (7 files), no
trusted-core file, against d8758ce9", so I ran no trust_mutants sweep.

## Trust

`uv run python tools/trust_map.py --check`: "against d8758ce96837: K +0, S +0, D +0, G +0, tied +0, unclassified +0,
trusted +0 / PASS", and the same against f5553bc894cf after the merge of main. So there is no R6 or R16 record and no FOLLOW-UPS.md row.

## Tests run

- New test while iterating: `1 passed` (/tmp/f3-t1.log, /tmp/f3-t2.log).
- Selected run (`mac-pytest.sh --select -- --base d8758ce968 --run`, on ve-mac-1, 3755 s; `/tmp/f3-select.log`) on
  33c4a96e5a, a clean tree with the final code; only DELTA.md and this REPORT came after it. Result: exit=0, "recorded
  75 units ... 0 failed". It included the new test file (0.4 s), `tests/test_safety_framework.py` (209.6 s),
  `tests/test_english_lean_lexicon.py` and `tests/test_english_statement_blocks.py`, all exit 0.
- I did not run the full gate, as the task says. The chain runs it on the final HEAD.

## Prompt size

The reads-1119 counter (R16 C5) is NOT installed. `tools-local/uc-audit.py` is the Nov 16 counter: it contains
`reads-1119` 0 times and differs from `uc-audit.py.reads-1119`. The reads-1119 counter and its runner
(`omission-seq-read.py.reads-1119`, `--dry-run-all`) are only staged beside the live files. That runner needs a
uc-audit debate dir frozen at a VE commit, which the decider prepares at the counted read. So I did not run the
dry-run; the decider re-checks it at the counted read.

Estimate (not a measurement): the legend grows from 402 to 570 bytes (+168), or +170 bytes inside
`environment.d1.json` with the JSON-escaped quotes. That is per rendered copy of this legend in a prompt. The largest
prompt measured so far is 105,768 bytes (RSP G3, per the runner's ARG_LIMIT note), against a limit of 131,000.

## Pilot bytes expected to move (estimate)

Unit `g-safety-cases` (bytes 53440-53579, 139 B, LABELLED) is the Glossary passage this legend now carries whole.
The expected effect is on the F3 LANGUAGE flag of the GOV answers only: 36 touched and 5 cleared alone, by the
comparer's upper-bound count. B-L0/SC and B-L2/SC belong to F4. Nothing is claimed before a pilot audit.

## Merge commit

This item merges at the branch's final HEAD on base main f5553bc894. I merged main in at e9f70b1e95; main's new
commits since d8758ce968 touch only infra tooling and docs and none of this item's files (`git diff --name-only`), and
after the merge `regen_generated.py --check` gives rc=0 and the new test passes (/tmp/f3-regen3.log, /tmp/f3-t3.log).
The task names VE commit 7cbec4b340b8, which is
not an ancestor of local main. At that commit and at d8758ce968, `vocabulary.py`, `environment.d1.json` and
`rules.d1.ve` are identical (`git diff --stat`: empty). So seeded bug S1 (main's text) shows the test failing on the
pinned commit. The R16 C2/C3 pinned lists are per commit and re-pin at the counted read. A merge after the R16
diagnostic voids the diagnostic for the GOV answers this legend touches.

## Notes for the DRI

- Several sibling rows edit `vocabulary.py` near this predicate and regenerate the same four recorded outputs
  (results.json, coverage.json, route-cases.jsonl and lexicon-report.json). F7 (govadequacy) releases S:10 to this
  same GOV legend (converge-AB.md:48), so the two touch the same lines. Whichever merges second must rebase, keep both
  appends, and regenerate with the writers listed above.
- The `safety_case` legend (vocabulary.py, used by f7-sc) already quotes the same definition without the term and the
  period. I left it as is: it is outside row F3.

## Spec re-read

- "Append the Glossary sentence, verbatim, to the GOV legend": the sentence is in that legend whole, from its term to
  its period. The draft's "is" was not used, because it is not the source's word (see above).
- Carrier guard: checked against rules.d1.ve, where f12-p/u and f13-p/u name the predicate. The test asserts this.
- "fails on 7cbec4b340b8, passes after": shown by S1, since the text is identical at both commits.
- "a NEW file tests/test_fsf_repair_f3_safetycase_1119.py": done. test_safety_framework.py and conftest.py are
  untouched. route-cases.jsonl changed only through its writer, because its `stale` case embeds this environment.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A. No relayed route or schema changed.
2. Every deliverable built, no rule broken: PASS. Both deliverables are in the table above, and no in-flight branch's diff touched these files at the start (sibling FSF repair branches had no commits except F5, which touches `low_risk` only).
3. Tests and gates can fail: PASS. Seeded bugs S1-S5 each fail `test_the_governance_legend_quotes_the_glossary_safety_case_sentence_whole`.
4. Py/Lean/Rust agree, valid inputs pass: PASS for this data change. `test_safety_framework.py` (including `test_rerun_equals_committed_results`) and `test_english_lean_lexicon.py` pass in /tmp/f3-select.log, with verdicts unchanged.
5. R8 binding: N.A. No relayed answer is read.
6. Gate evidence matches final HEAD: PASS for the selected run (33c4a96e5a, code identical to the final HEAD; only docs follow). The chain runs the full gate on the final HEAD.
7. No unsigned item: PASS. No DELTA row and no reserved signature.
8. Every user-visible change in DELTA: PASS. No user-visible VE change; DELTA.md says so.
9. Test selection finds the tests: PASS. The selected run picked the new file and the safety-framework, lexicon and route-fixture tests.
10. Lean statements: N.A. No Lean change.
11. Budgets, limits, deadlines: N.A. No evaluator. The prompt-size limit is reported under "Prompt size".
12. No CPU or memory regression: N.A. A data-only change; the new test runs in 0.4 s.
13. Test-removed trailers: N.A. No test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. HEAD passes; S1-S5 fail with logs; the spec re-read is above.
15. The four classes behind FIX reviews: PASS. Nothing is overclaimed (the prompt size is stated as an estimate), nothing is cut silently, every check can fail (S1-S5), and limits are N.A.
