# ci-3a: the step reader (commands-imperatives section 7, CI-3's first part)

Status: built; 6 of section 7's 8 statements proved. `preposed_eq` and `readStep_conservative` move whole to ci-3
(reviews/dri-decisions-20261109-ci-3a.md item 2). No route calls `readStep`, so no verdict, wording or pilot byte
changes. DELTA row 1 is signed. Next item: ci-3.

## Delivered (spec 9a12df17a section 7)

- Steps.lean has `Shape` through `reads` as section 7 writes them: a probe of the 14 definitions and the 6
  statements found 20 of 20 equal. Exceptions:
  - `Form` comes from section 10 (reviews/dri-decisions-20261109-ci-3a-form.md);
  - `readStep`'s byte charge and the `hb` hypothesis (wording ruling item 1, DELTA row 1).
- The product is charged: `shapeOutcomeCharged` counts `productSize` before it builds the product. The kernel-checked
  `@[csimp] shapeOutcome_charged` sits before `readStep`, so compiled code calls the charged form (ruling item 1).
- Proved with no `sorry`, standard axioms only (`python3 lean/audit.py` PASS): `after_eq`, `seq_eq`,
  `shapes_ambiguous`, `seq_ambiguous`, `shapes_limit` and `shapes_complete`.
- StepsExamples.lean has:
  - every `E_web` row and the constructed aggregation rows;
  - finding (d), with the code only (O8);
  - the charges: the gate (line 144), 8×64 readings (148), 6 KB, and 400 and 401 bytes (164-165).
- Other files: lean/VE.lean (import), tools/layer_policy.py (layer 4) and tools/trust-classes.json (G[V]; two ties).

**Does W1's act linter make `hs` unnecessary?** ci-3a proved nothing about `readStep_conservative`, so the spec's
computed answer stands: `hs` stays. ci-3 proves it. `preposed_eq` needs `String.splitOn` lemmas that core Lean 4.24
lacks.

## Seeded bugs and mutants

`mutants.json` has 21 Lean hand mutants, each with its `old` and `new` text, and each fails a fixture (StepsExamples
lines), plus one Python seeded bug:
- `tools/layer_policy.py`: `lean_layer` with `VE.Commands.Steps` and `VE.Commands.StepsExamples` left out of
  layer 4 (back to `module == "VE.Commands.Read"`). `python3 tools/check_lean_imports.py` fails with exit 1 and
  reports two new outward Lean imports, Steps -> Read and StepsExamples -> Examples. Restored, it exits 0.

The four Lean seeded bugs the task names:
- `shapes` without `preposed`'s condition: 60-61;
- the generic refusal for one shape: 64;
- `many` beside a `limit`: 88;
- first-step-only tuples: 107-109.

The trust-mutants sweep (`mac-pytest.sh --trustmut`): `trust-mutants-full.json` has 175 KILLED, 20 SURVIVOR,
107 UNKNOWN and 36 INVALID. With `trust-mutants-allow.json`, `--rescore` gives `trust-mutants.json`: 175 KILLED,
127 ALLOWED and 36 INVALID, exit 0.

The allowed mutants:
- are equivalent;
- are text Lean refuses;
- break the `@[csimp]` lemma, which every check computes through (the hand mutants with the lemma blanked show the
  fixtures kill them);
- or come from `shapeAlts` being inlined.

## Trust (R16), size

`tools/trust_map.py --check` against d55d24faab75 gives K +0, S +0 and trusted +136 (Steps.lean). The allowance in
docs/trust-baseline.json is SIGNED by standing ruling R16; FOLLOW-UPS.md "## ci-3a" asks for the ties pass.
Hand-written lines: 898 (`git diff --numstat` against the merge base, without generated files or tool
output; 890 accepted by reviews/dri-decisions-20261109-ci-3a-size.md item 1, plus the assurance manifest line, plus
7 lines of pre-review evidence: the Python seeded bug in this REPORT and in mutants.json). Pilot bytes moved: 0.

## Re-run after ci-3 fix F1 (ci-3a-record-rerun, 2026-11-20)

Why: since ci-3 fix F1 (dc360e738b, merge 020623f8d7) `shapeOutcomeCharged` writes the non-sequence arms itself, so a
`shapeOutcome` bool-flip breaks `@[csimp] shapeOutcome_charged`; the tool cuts the lemma and READS reaches its
`sorry`, and the nightly saw M021/M050/M066 as UNKNOWN (its M465/M1082/M1423, test-skip/nightly/20261119T0727Z.json).

Head 5f6979256074 (main, contains dc360e738b), tree fd87a73962c9, base d55d24faab75 as before, `--classes trusted`
(default), `--max-mutants 1000`, `--jobs 8`, both runs through `mac-pytest.sh --trustmut` (they ran on VM1). At this
head the same base plans 7539 mutants in 405 definitions (main moved), so both runs add
`--only @docs/commands-imperatives/ci-3a/trust-mutants-only.txt`: the plan's 338 mutants of the 13 definitions this
record lists, all in Steps.lean. They are the old record's 338 one for one (same definition, operator, before and
after; lines equal or 6 lower); the ids are the new plan's.
- `trust-mutants-full.json`: 172 KILLED, 20 SURVIVOR, 90 UNKNOWN, 56 INVALID (5206 s).
- `--allow trust-mutants-allow.json --rescore trust-mutants-full.json` gives `trust-mutants.json`: 172 KILLED,
  110 ALLOWED, 56 INVALID, 0 SURVIVOR, 0 UNKNOWN, exit 0 (248 reused, 90 rerun, 3014 s; `--jobs 5`, the runner's cap).
  The allow list is unchanged.

The three rows (old id, new id, line; old verdict in trust-mutants.json, new):
- M021 / M520, Steps.lean:85, `shapeOutcome` bool-flip `false` -> `true`: KILLED -> ALLOWED (shapeOutcome, bool-flip).
- M050 / M1200, Steps.lean:88, `shapeOutcome` bool-flip `false` -> `true`: KILLED -> ALLOWED (shapeOutcome, bool-flip).
- M066 / M1571, Steps.lean:89, `shapeOutcome` bool-flip `true` -> `false`: KILLED -> ALLOWED (shapeOutcome, bool-flip).
In the full record the three are UNKNOWN, "it computes through a proof the mutant broke".

Every other mutant keeps its verdict (172 KILLED, 107 ALLOWED, 36 INVALID) except 20 that were ALLOWED under a
"Lean refuses the text" reason and are now INVALID. The tool at this head marks Lean's refusal itself; the old full
record had them UNKNOWN. One line each (old / new, line, definition, operator: Lean's error):
- M029 / M724, 27, hasThen, list-empty: implicit `α` not synthesized.
- M037 / M732, 218, reads, list-empty: implicit `α` not synthesized.
- M055 / M1298, 71, lift, list-empty: Function expected.
- M059 / M1302, 191, combineShapes, list-empty: Function expected.
- M060 / M1303, 211, readStep, list-empty: Function expected.
- M072 / M1632, 82, readingTuples, list-empty: Function expected.
- M075 / M1635, 192, combineShapes, list-empty: implicit `α` not synthesized.
- M087 / M1859, 193, combineShapes, list-empty: implicit `α` not synthesized.
- M100 / M2107, 37, shapes, list-empty: Function expected.
- M106 / M2181, 37, shapes, list-empty: implicit `α` not synthesized.
- M107 / M2182, 102, shapeOutcome, list-empty: Function expected.
- M114 / M2290, 107, shapeOutcome, list-empty: implicit `α` not synthesized.
- M118 / M2357, 111, shapeOutcome, list-empty: implicit `α` not synthesized.
- M122 / M2406, 112, shapeOutcome, list-empty: Function expected.
- M124 / M2437, 42, shapes, list-empty: implicit `α` not synthesized.
- M125 / M2451, 42, shapes, list-empty: implicit `α` not synthesized.
- M136 / M2569, 183, shapeAlts, list-first: `.shape`'s expected type not determined (the operator wraps the `match`).
- M145 / M2861, 183, shapeAlts, list-drop-last: as M136.
- M240 / M4872, 183, shapeAlts, list-last: as M136.
- M249 / M5164, 183, shapeAlts, list-drop-first: as M136.
No mutant is newly SURVIVOR; the full record's 20 SURVIVOR are the old record's 20, all ALLOWED as before.

Condition test: `python3 -I tools-local/test_tm_nightly_unknown_disposition_3.py` (manage-agents) passes, 3 tests.
Product code: none changed (record files only), so no seeded bugs; trust +0; no DELTA row.
SIZE: 0 product, 0 tests, about 50 other hand-written lines (this section); the records and the id list are tool output.

Notes for the DRI: the original invocation cannot be repeated as it was at this head (same base, 7539 mutants), so
the re-run adds `--only` (the narrower reading: exactly the record's 13 definitions). The id list is committed beside
the records.
