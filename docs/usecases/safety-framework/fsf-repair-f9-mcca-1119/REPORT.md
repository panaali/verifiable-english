# fsf-repair-f9-mcca-1119 REPORT (row F9: the 1.3.2 non-frontier sentence and the MCCA content)

No DRI signature is reserved; no DELTA row (DELTA.md: no user-visible change of VE). Fallback not used. Counter
reads-1119 is NOT installed on main's counter seat at finish (see Prompt size).

## Plan row delivered

ROW F9 (fully converged, reviews/pathf-q3/flag-analysis-1119/converge-AB.md): "the 1.3.2 sentence 'We may also apply
material capability change assessments to models not on the frontier, to understand whether a critical capability
assessment is required.' and the MCCA content, verbatim, in the assessed / MCCA legend. Targets G6 and
K4/CHECKPOINT_MCCA (both TEXT). PRA ... is NOT part of this row."

| Deliverable | Where | Test |
|---|---|---|
| 1.3.2 non-frontier sentence, verbatim, in the `assessed` legend (the CCA legend) | `usecases/safety-framework/vocabulary.py` REGULATED `assessed`; `environment.d1.json` | `tests/test_fsf_repair_f9_mcca_1119.py::test_the_legend_quotes_the_pinned_1_3_2_sentence_byte_for_byte[assessed]` |
| MCCA content (1.3.2), verbatim, in the `change_assessed` legend (the MCCA legend) | same files, `change_assessed` | `...byte_for_byte[change_assessed]` |
| Carrier guard: each legend is that of a predicate the target block USES (the counter's `used_predicates` match of the act template in the rule body) | `assessed` used by f3 (G6 exposure E7); `change_assessed` used by f5 (K4 exposure E3) | `...::test_the_legend_is_a_counted_carrier_of_the_target_block[assessed]`, `[change_assessed]` |
| Condition test in a NEW file | `tests/test_fsf_repair_f9_mcca_1119.py` | selected (mac-pytest --select ran it: exit 0) |

Both legends keep their act, role and arguments; the sentence is appended after the existing text, in the predicate's
own entry (not at the end of a shared file).

### Source passages (pinned FSF 3.1 text, `fsf-3.1.txt`, SHA-256 18e3375b...0c53946, read via tests/pinned_source.py)

- Section 1.3.2, page 5, bytes 10706-10861: "We may also apply material capability change assessments to models not on the
  frontier, to understand whether a critical capability assessment is required."
- Section 1.3.2, page 5, bytes 10206-10344: "These assessments draw on model characteristics, such as its provenance,
  size, modality, and performance on general capability benchmarks." (the sentence after "we conduct material capability
  change assessments on various checkpoints upon the completion of a post-training run", which f5 already translates)

Neither sentence holds a quote mark or a footnote mark, so the project's quote normalisation (whitespace runs to one
space, curly quotes to straight) leaves them byte-identical. Text was taken from the source, not from any flag.

### Kind calls

ROW F9 names no KIND CALLS STILL DIFFER (converge-AB: G6 and K4 both TEXT, converged). Nothing for the reviewer to
check there. One reading call of mine for the reviewer: "the MCCA content" is read as the 1.3.2 content sentence that
K4's 4/4 flags quote (b-report K4 row); the Glossary entry "Material Capability Change Assessments: indicate whether
..." (page 18) is not carried: it is not named by the row, and the Glossary rows belong to F2 (whose list is CCA,
Security Mitigations, RRA, Frontier AI Models). The 1.3.2 non-frontier sentence goes in `assessed` (not in
`change_assessed`) because G6's blocks (f3, f12-p/u, f13-p/u, FACTS) use `assessed` (f3) and never `change_assessed`.

## Carrier check and prompt size

- Counter: `tools-local/uc-audit.py` (live) is NOT `uc-audit.py.reads-1119` (they differ from line 301: the live one is
  the 11-16 version, with no `seq_unit_legends`). So the R16 C5 `--dry-run-all` was not run; the decider re-checks at the
  counted read.
- Local render check (not a dry-run): `seq_frozen_unit` of the frozen `uc-audit.py.reads-1119`, loaded read-only with
  `VE_REPO` set to this worktree, rendered units at main d8758ce968 and at the legend commit:
  - f3: 1,634 -> 1,830 bytes; legend part lists low_risk, governance_found_..., assessed; holds the G6 sentence.
  - f5: 733 -> 896 bytes; legend part lists post_training_run_completed, change_assessed; holds the K4 sentence.
  - f12-p, f12-u, f13-p, f13-u, FACTS: unchanged bytes.
- Size estimate (not measured): a prompt grows by +196 bytes per unit it holds that uses `assessed` (f2, f3) and +163
  per unit using `change_assessed` (f5); at most ~560 bytes for one answer. The largest measured prompt (2026-11-15) is
  105,768 bytes, so the limit of 131,000 bytes has room; only the C5 dry-run on reads-1119 measures it.

## Regenerated files (generators only)

`environment.d1.json` (`python usecases/safety-framework/vocabulary.py`), `coverage.json` (`build_document.py --source`
on a /tmp copy of the pinned text: `document_sha256` only), `tests/data/route-cases.jsonl`
(`docs/en-e3-norm/en-2b/route_fixtures.py --write`), `conformance/english-lean/lexicon-report.json`
(`python -m conformance.english_lean_lexicon`): hashes only. `results.json`: `run.py` rewrote it unchanged (257/262, the
same five recorded disagreements as main). `tools/regen_generated.py --check`: exit 0 after the rebase on f5553bc894.

## Seeded bugs (Python: `usecases/safety-framework/vocabulary.py`, and its generated `environment.d1.json`)

Each planted, run on `tests/test_fsf_repair_f9_mcca_1119.py`, then restored with `git checkout`.

| # | Bug | File | Failing test |
|---|---|---|---|
| 0 | the legends of 7cbec4b340b8 (vocabulary.py and environment.d1.json from that commit) | vocabulary.py, environment.d1.json | `...byte_for_byte[assessed]`, `...byte_for_byte[change_assessed]` (2 failed) |
| 1 | paraphrase: "models not on the frontier" -> "non-frontier models" in `assessed` | vocabulary.py | `...byte_for_byte[assessed]` |
| 2 | MCCA sentence drops "modality, " in `change_assessed` | vocabulary.py | `...byte_for_byte[change_assessed]` |
| 3 | stale committed environment: `change_assessed` description without the sentence | environment.d1.json | `...byte_for_byte[change_assessed]` |
| 4 | carrier broken: `change_assessed` act "{0} be followed by checkpoint capability reviews" (no longer in f5's body) | vocabulary.py | `...::test_the_legend_is_a_counted_carrier_of_the_target_block[change_assessed]` |

A first carrier mutant ("... assessments" without "on various checkpoints") survived: it is still a prefix of f5's
rule wording, so the counter's own match still counts it; it is not a carrier break and was replaced by #4.

No Lean or Rust product code changed (the Rust binary was only built locally for the regen; `lean/checkers.lock`
unchanged).

## Tests

- New file alone: 4 passed locally (the pinned source is present here). Where the pinned text is absent the two
  byte-for-byte cases skip as every pinned-source test does (tools/gate-optional.json); the carrier cases need no source.
- Selected run (`mac-pytest.sh --select`, ve-mac-1, HEAD 52d091bd, i.e. the legend commit before the rebase): exit 0,
  0 failed ids; it ran test_safety_framework.py, test_fsf_case_alternatives.py, test_english_lean_lexicon.py,
  test_ownership_floor.py and this file among 66 units. The rebase onto f5553bc894 brought no change to any file of
  this item (main's new commits touch only docs/infra and tm/gate tooling).
- main-known-red.txt: none of its four ids failed or was touched.

## Trust

`tools/trust_map.py --check` on the rebased HEAD: K +0, S +0, D +0, G +0, tied +0, trusted +0; PASS. No allowance
recorded, no FOLLOW-UPS row. Light lane: LIGHT (108 changed lines outside generated files, no trusted-core file), so no
trust_mutants sweep (the task file asks for no trust_mutants record).

SIZE: 0 product, 89 tests, 7 other hand-written lines (the two legends in vocabulary.py), plus this REPORT and DELTA.

## Commit this merges at

The legend change is commit 3d208f9253 (on main f5553bc894); the branch head is the docs commit that adds this file.
The R16 C2/C3 pinned lists are per commit: the counted read re-pins at the merge commit the train makes, and a merge
after the R16 diagnostic voids the diagnostic for G6 and K4/CHECKPOINT_MCCA (and for any answer reading f2, f3 or f5,
whose rendered units change).

## Pilot bytes expected to move (estimate)

Two TEXT answers targeted: G6 (SILENT:CCA, 8/8 rows flagged the non-frontier sentence) and K4/CHECKPOINT_MCCA (4/4 rows
flagged the MCCA content). converge-AB counts F9 at 13 touched / 3 alone with PRA included; without PRA, at most G6 and
K4 clear on this row. Nothing is claimed before the counted read.

## Notes for the DRI

- Sibling F2 (fsf-repair-f2-glossary-1119) is to append the CCA Glossary sentence to the same `assessed` legend; the
  second of the two to merge will have a textual conflict in that one entry (both appends are kept; then regenerate).
- The Glossary MCCA entry ("Material Capability Change Assessments: indicate whether ...; May also be used to assess
  whether a critical capability assessment is required of non-frontier AI models.") is carried by no row.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relay, no Lean answer read).
2. Every deliverable built, no rule broken: PASS (table above; test_fsf_repair_f9_mcca_1119.py; no Python copy of a
   Lean decision, no report test, no shared-file tail append).
3. Tests can fail: PASS (seeded bugs 0-4; test_the_legend_quotes_..., test_the_legend_is_a_counted_carrier_...).
4. Python/Lean/Rust agree: N.A. (no product code; results.json unchanged by run.py).
5. R8 binding: N.A. (no relayed field).
6. Gate evidence matches final HEAD: PASS (rebased on main f5553bc894, regen --check exit 0; the chain runs the gate).
7. No unsigned item: PASS (DELTA.md: no row; trust +0).
8. Every user-visible change in DELTA: PASS (none; legend text of a use case only).
9. Selection finds the tests: PASS (the selected run picked tests/test_fsf_repair_f9_mcca_1119.py and
   tests/test_safety_framework.py).
10. Lean statements: N.A.
11. Budgets fail closed: N.A. (no evaluator or limit; prompt-size estimate above, measured only by C5).
12. No CPU/memory regression: N.A. (legend text only).
13. Test-removed trailers: N.A. (no test removed).
14. Both directions, cited evidence, spec re-read: PASS (fails on 7cbec4b340b8 legends, passes after; the carrier test
    checks both the computed and the committed legend).
15. The four FIX classes:
    - No overclaim: PASS ("unchanged" results.json: run.py output 257/262 and `git status` showing it unmodified;
      "trust +0": trust_map.py --check; the prompt size is stated as an estimate, not a measurement).
    - No silent cut: PASS (both deliverables built; the C5 dry-run is not run because the counter is not installed,
      as the task allows, and is said in the first lines).
    - Every new check can fail: PASS (seeded bugs 1-4, each with its failing test id).
    - Limits charged before work: N.A. (no evaluator, runner or limit added).
