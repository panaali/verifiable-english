# fsf-repair-f5-lowrisk-1119 REPORT

Status: built, ready for the chain's gate. No DRI signature is reserved, and no DELTA row is needed (DELTA.md).
Changed: the `low_risk` legend now quotes the Glossary sentence on Low-Risk External Deployments verbatim from the
pinned source, so "or organizations" is back. The files that hash the legend are regenerated.
Open: the reads-1119 counter (R16 C5) is not installed, so the prompt-size dry-run could not be run (see "Prompt size").
Base: main c9295c9c94 (the merge base). The VE commit this merges at is the branch's final HEAD on that base (see "Merge commit").

SIZE: 3 product, 20 tests, 30 other hand-written lines (product means the `vocabulary.py` legend; other means
DELTA.md and this REPORT; generated or recorded outputs are not counted).

## Source passage (the source wins)

Pinned source: `~/code/manage-agents/pilots/safety-framework/source/fsf-3.1.txt` (sha256 18e3375b35c6..., 54,373 B,
the text `usecases/safety-framework/source/extract_text.py` writes from the pinned PDF). Glossary, PDF page 19
(text line 19), bytes 51747-51879, inside unit `g-low-risk` [51743, 51880] of `spans.json`. It occurs once:

> Low-Risk External Deployments: represent small scale and private releases restricted to particular external groups or organizations.

I read this with `python3 -I -c` over the pinned file (`b.find`, `b.count` = 1). The text was not taken from any
reader, flag, diagnostic or analyst output.

## Deliverables

| # | Task row | Delivered | Commit | Test |
|---|---|---|---|---|
| 1 | Replace the paraphrase in the `low_risk` legend with the Glossary text verbatim | `vocabulary.py` `BASE["low_risk"]` now reads `{0} is a low-risk external deployment (Glossary: "<the sentence above>")`, and its open term OT8 and its decider are unchanged. `environment.d1.json` is rewritten by its generator (`uv run python usecases/safety-framework/vocabulary.py`). | bd6553d499 | `tests/test_safety_framework.py::test_the_low_risk_legend_quotes_the_glossary_sentence_whole` |
| 1a | "and its source in build_document.py ot8_low_risk_external if the legend is generated from it" | Not changed, because the legend is not generated from it. `build_document.py:61` `ot8_low_risk_external` is the open-term table entry for OT8, and its two strings are anchor phrases for the span accounting. The legend's only source is `vocabulary.py` (`environment()` / `text()`, written by `vocabulary.py`'s `__main__`). | n/a | `test_the_open_predicates_are_the_environment_legend_s_open_terms` (unchanged, passes) |
| 2 | The condition test | The test reads the sentence from the pinned source (`pinned_source("safety-framework")`) with this file's quote normalisation (`_quote_normal`: whitespace collapsed, curly quotes made straight). It asserts that the sentence occurs once and ends with "external groups or organizations.". It then asserts that the quoted sentence is byte for byte in both the `vocabulary.environment()` legend and the committed `environment.d1.json` legend, and that the subject, OT8 and the decider are kept. It fails with main's text (seeded bug S1) and passes on HEAD. | bd6553d499, then the R1-names assertions in the docs commit | same |

Carrier guard: the sentence sits in the vocabulary legend (`description`) of `low_risk`, the predicate that Rule 1
(`rules.d1.ve:4`) and the fact on line 28 of `facts.d1.ve` use. It is not in a header, a citation run or a constant table.

Regenerated outputs (each from its own writer; none was edited by hand). Only hashes move:
- `usecases/safety-framework/results.json`: `uv run python usecases/safety-framework/run.py`. Two `certificate_sha256` values change and no verdict changes (`git diff -U0`: 2 lines).
- `usecases/safety-framework/coverage.json`: `uv run python usecases/safety-framework/build_document.py --source /tmp/f5src/fsf-3.1.txt`. I gave it a `/tmp` copy of the pinned text because the writer puts `fsf.d1.ve.md` beside its source, and that is under manage-agents. Only `document_sha256` changes, and `spans.json` is unchanged.
- `tests/data/route-cases.jsonl`: `uv run python docs/en-e3-norm/en-2b/route_fixtures.py --write` (the `stale` case embeds this environment).
- `conformance/english-lean/lexicon-report.json`: `uv run python conformance/english_lean_lexicon.py` (`{"valid": 43, "invalid": 0}`).
- `uv run python tools/regen_generated.py --check`: rc=0, "checked 41 entries". No regen_generated entry owns these four files.

Not changed: the frozen fidmech copies under `tests/data/fidmech/{wording,fp1}-inputs/safety-framework/`. These are
frozen inputs whose sha256 is pinned in `wording-golden.json`, so they are not mirrors of the live file.

Out of scope and not touched: the `internal` and `high_risk` legends, rows F1-F4 and F6-F9, and every Lean, decision
or relay path.

## Seeded bugs (Python only; it is the only language changed)

Each was planted in a changed file and run against
`tests/test_safety_framework.py::test_the_low_risk_legend_quotes_the_glossary_sentence_whole`. Each made the test
fail (rc=1), and each was then restored with `git checkout -- usecases` (the tree was clean afterwards).

| id | File | Bug | Fails at |
|---|---|---|---|
| S1 | `usecases/safety-framework/vocabulary.py` + `environment.d1.json` | main's text (the pinned commit's legend: the paraphrase without "or organizations") | `assert f'"{sentences[0]}"' in _quote_normal(legend)` (/tmp/f5-s1.log) |
| S2 | `usecases/safety-framework/vocabulary.py` | "groups or organizations." becomes "groups." in the quote only | same assertion (/tmp/f5-s2.log) |
| S3 | `usecases/safety-framework/vocabulary.py` | "Low-Risk" becomes "Low-risk" in the quote, a one-byte case change | same assertion (/tmp/f5-s3.log) |
| S4 | `usecases/safety-framework/environment.d1.json` | the committed environment is stale (main's legend) while vocabulary.py is new | same assertion, on the committed legend (/tmp/f5-s4.log) |
| S5 | `usecases/safety-framework/vocabulary.py` | the decider "no one the text names (unstated)" becomes "the developer" | `assert legend.endswith(". Open term OT8, decided by no one the text names (unstated)")` (/tmp/f5-s5.log) |

There is no Lean or Rust product change, so no seeded bug is needed there. Mutants per new trusted definition: none
(trust +0, see below). Light lane: `light-lane.py check` printed "LIGHT 25 changed lines outside generated files <= 150
(3 files), no trusted-core file, against c9295c9c", so no trust_mutants sweep was run.

## Trust

`uv run python tools/trust_map.py --check`: "against c9295c9c9440: K +0, S +0, D +0, G +0, tied +0, unclassified +0,
trusted +0 / PASS". So there is no R6 or R16 record and no FOLLOW-UPS.md row.

## Tests run

- Selected run 1 (`mac-pytest.sh --select`, run on the VM, 2058 s; `/tmp/f5-select.log`) on bd6553d499 failed 5 ids. Each failure was a recorded output that hashes this environment and was stale: `test_span_accounting_is_complete`, `test_rerun_equals_committed_results` and `test_build_check_writes_nothing_beside_the_source` (all in test_safety_framework.py), `test_english_lean_lexicon.py::test_every_corpus_environment_has_a_valid_selected_lexicon` and `test_english_statement_blocks.py::test_the_route_fixtures_are_recorded`. The run stopped early (--maxfail 5), and 129 units did not run.
- Fix d1bbb7b3ae regenerated those outputs. Rerun of the 5 failed ids plus the new test: `6 passed in 377.84s` (`/tmp/f5-rerun.log`).
- The final selected run on the final code is recorded in "Final selected run" below.

## Prompt size

The counter version reads-1119 (R16 C5) is NOT installed. `tools-local/` holds `uc-audit.py.reads-1116` and
`omission-seq-read.py.reads-1116` only, `grep -c reads-1119 tools-local/uc-audit.py` gives 0, and no file on VE main
names it. So I did not run the dry-run, and the decider re-checks at the counted read. My estimate of the change: the
legend grows from 113 to 184 bytes (+71), or +73 bytes inside `environment.d1.json` with the JSON-escaped quotes.
That is per copy of the environment in a prompt. This is an estimate only; nothing is claimed before the counter's
dry-run.

## Pilot bytes expected to move (estimate)

Unit `g-low-risk` (bytes 51743-51880, 137 B, LABELLED) is the Glossary passage this legend now carries whole. The
expected effect is on the F5 LANGUAGE flag only, and nothing is claimed before a pilot audit.

## Merge commit

The VE commit this merges at is this branch's final HEAD, on base main c9295c9c94. The task names VE main
7cbec4b340b8, which in this clone's bundle remote (`origin/main`) shares no merge base with local main. Local main
c9295c9c94 is VE main, and it is later (2026-11-19 09:52Z against 2026-11-15). `vocabulary.py` and
`environment.d1.json` are identical at 7cbec4b340 and c9295c9c94 (`git diff --stat`: empty), so "fails at the pinned
commit" is shown by S1 (main's text). The R16 C2/C3 pinned lists re-pin at the counted read.

## Notes for the DRI

- `usecases/safety-framework/PLAN.md:125` (OT8 row) still quotes the Glossary without "or organizations". It is
  planning prose, not a carrier, so under the narrower reading of the task I left it unchanged.
- `build_document.py:61` keeps its OT8 anchor phrases. They are span anchors and are still in the source.

## Spec re-read

- "replace the paraphrase in the `low_risk` legend ... with the Glossary text verbatim" against the task text and the
  source passage above: the legend holds the whole sentence, starting with the term and ending with its period.
- "Put each sentence in the legend of the predicate named below" (carrier guard): checked against the predicate
  `low_risk`, which rules.d1.ve:4 and facts.d1.ve:28 use.
- "fails on 7cbec4b340b8, passes after": shown by S1, with the identical text at both commits.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A., no relayed route or schema changed.
2. Every deliverable built: PASS. Deliverables table above; diff grep shows no Python copy of a Lean decision, no permanent report test, and no in-flight branch touching these files (`git diff --name-only main...<b>` over the `lean-first/feature/infra/foundation` branches: none).
3. Tests can fail: PASS, seeded bugs S1-S5 against `test_the_low_risk_legend_quotes_the_glossary_sentence_whole`.
4. Py/Lean/Rust agree, valid inputs pass: PASS for this data change. `test_rerun_equals_committed_results` shows the same verdicts, and `test_every_corpus_environment_has_a_valid_selected_lexicon` gives 43 valid (/tmp/f5-rerun.log).
5. R8 binding: N.A., no relayed answer read.
6. Three-valued verdicts: N.A., no verdict path changed (results.json verdicts unchanged).
7. Deadlines and budgets: N.A., no operation added.
8. Kind and owner folds: N.A., no fold added.
9. English render and parse: PASS for the legend's lexicon, `test_every_corpus_environment_has_a_valid_selected_lexicon`.
10. Entry points: N.A., no entry point added.
11. No regex of a real language: PASS. The test's regex reads English prose from the pinned source, not code or JSON.
12. State machines and ledgers: N.A.
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. The accepting side is HEAD, the refusing side is S1-S5, every claim cites a log or command, and the spec re-read section is above.
15. No overclaim / no silent cut / every check can fail / limits charged: PASS. The universal words above each cite a command or log, nothing is cut, S1-S5 cover the checks, and limits are N.A. (no evaluator).
