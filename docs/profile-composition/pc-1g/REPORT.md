# pc-1g report: the rights@0 reader, G3's definitions, and the statement stop

Status: STOPPED on statements and resolved by the DRI. Under reviews/dri-decisions-20261103-pc-1g-stop.md, pc-1g merges its unblocked parts, and the statements that could not be proved leave its deliverables. No DRI signature is reserved.
HEAD: the last commit on feature/pc-1g. Changed: the rights chain's reader (`correlate_judged` proved), `judgments@0` beside `rights@0` admitted (spec section 4 row 2 deleted), F1.4, G3's definitions, fixtures F1.1/F1.6, F1.3b/c/i/j/k, the compress/parse round trip checked, and review F1's conditioned rights gate.
Open (DRI ruling items 2 to 6): G3 and its 2a/2c proofs, F5 and F1.3e to F1.3h go to pc-1h. The restated round-trip lemma, `swap_correct` and `verdictFields` go through a statement review, then a follow-up proves them.
DELTA: row 2's deletion is SIGNED by the DRI (20261101 item 1); the compress/parse boundary is SIGNED by the DRI (20261103 stop item 2); trust is R16.

Plan: docs/spec/profile-composition-PLAN.md "PC-1" and spec 1.7, 3.1 and 5.1, at 3dfadd302. Main's copies are byte-identical: `git -C ../verifiable-english show 3dfadd302:<file> | diff -q - <file>` printed nothing for both files. Synthesis round 2: this item was to prove edit 2 of debates/plan-synthesis-2/edits-profile-composition.md, the G3 amendment (the exchange applies only when it is one-to-one, decided in Lean first). It does not prove it. The amendment's statements rest on the round trip and on `swap_correct`, both stopped below. Its runtime check (pc-1's row 16) is unchanged.

## The stop, and the DRI's ruling

Asked through msg.sh on 2026-11-03 (inbox/dri/20261103T143453Z-pc-1g-2914307.md, addendum 164838Z). Ruled 17:15Z in reviews/dri-decisions-20261103-pc-1g-stop.md.

1. **The round-trip lemma (deliverable 2) is not provable without an axiom in Lean v4.24.0.** `withoutJudgments` writes the twin's front matter with `Lean.Json.compress`, and `frontJson` (Document.lean:330) reads it back with `Lean.Json.parse`. Both are `partial def`s in the toolchain: `Lean/Data/Json/Printer.lean:164`, and `Parser.lean:75,94,204-233`. The kernel cannot unfold them. In a scratch file, `Json.parse "1" = .ok 1` and `Json.compress (.num 1) = "1"` both fail by `rfl`, and `decide` has no instance. Every theorem about the twin reads the parse: `swapInjective_twin`, `withoutJudgments_ids`, `checkDocSets_swapClash` (its first two conjuncts), `checkDocSets_judgments_transparent` and `checkDocSets_withoutStatuses`. **Ruling item 2:** restate the lemma over the structured value, and record compress/parse as one named trusted boundary in DELTA with a differential round-trip test. Built here: DELTA row 2, and the ChainExamples `#guard`s `twinFront` (every fixture's twin reads back the front matter built) and `drawn` (300 generated values: escapes, astral characters, naturals up to 2^53-1, `null`, nesting; 160 distinct, up to 315 characters, measured with a scratch `#eval`).
2. **`swap_correct` is false.** Take one key `K` stated in two reading sets for contents A and B, with `K = v₁(B)`. Then `swapInjective` holds, `(K, v₁(B), v₂(B))` is a pair, and `exchange K = K`, because it uses the first pair. No digest collision is needed. The witness is the `#guard` after `twoSets` in ChainExamples. **Ruling item 3:** restate it (each stated key maps to one content), or reject such documents. This is triage row syn2-pc1-exchange.
3. **`verdictFields` as specified made G3 false** through jt-3a's `undeclared_evaluative` (pc-1 DELTA row 10). **Ruling item 4:** the spec drops it. Done here: `verdictFields` drops it and names the ruling, and the F1.1/F1.6 and F1.4 `#guard`s check equal verdict fields. This closes pc-1 DELTA row 10.
4. **G3 (whole-chain relational proof):** **ruling item 5** moves it to pc-1h, with its own size budget.
5. **F5 and the unit/reading `meaning_id` exchange (F1.3e to F1.3h)** cannot be built without moving pc-1's whole clash section (Document.lean:391-750). Lean has no forward references, and E″ and a unit's identity need `environmentOf`, `softSource`, `softLayer` and `contentOf`, which come later. The move alone is about 720 numstat lines. The addendum proposed moving them to pc-1h with G3. The ruling (which cites the addendum) lists the parts that merge here, and F5 is not among them. So they are pc-1h's, and row 16's answers are unchanged here.

Nothing false or unproved is stated: no `sorry`, no axiom (`python3 lean/audit.py`: "PASS: 752 source files; 8327 named theorem declarations audited ... only the declared standard axiom allowlist").

## Plan rows

| Row | Delivered | Where | Checked by |
|---|---|---|---|
| (1) `verdictFields`, `unitStatuses`, `judgmentCodes`, `judgmentGateTexts`, `layerRefusal`, `layerRelaxes` | yes (definitions; `verdictFields` per ruling item 4) | Document.lean, "G3: success-only transparency" | ChainExamples 2d and 2e `#guard`s; mutants 10 to 17 |
| (1) `swap_correct`, `withoutJudgments_ids`, `checkDocSets_judgments_transparent`, `checkDocSets_swapClash`, `checkDocSets_withoutStatuses`, `swapInjective_twin` | **no**: the stop. Ruling items 1, 3 and 5 (G3 to pc-1h; the rest restated after statement review) | | `twoSets` witness; pc-1's F1.3l/m/o `swapInjective_twin` guards stay selected (ChainExamples:91-116) |
| (1) `noUnitStatus`, `withoutStatuses` (2b, 2c) | yes (definitions) | Document.lean | F1.3i `#guard`; mutants 18, 19 |
| (2) the round-trip lemma | **no**: unprovable (Lean's parser is opaque to the kernel). Ruling item 2: restated later; the boundary is in DELTA with its round-trip checks | ChainExamples `twinFront`, `drawn` | DELTA row 2 |
| (3) F5 | **no**: pc-1h (ruling item 5, addendum) | | |
| (4) `rightsAuthorFormulas`, `correlate_judged` (proved), `blockFormulas`, `andAll`, `preds_andAll` (proved), through `judgedIn` | yes; the block readers are stated about by `blockFormula_null`, `ruleFormulas_ok`, `linesFormulas_none`, `blockFormulas_bar` and `blockFormulas_limitation` (test_judgments_exercised); Chain.lean is classified in ve/assurance-manifest.json `other_json`, and Document.lean's pin is updated (whole file) | Chain.lean "The rights chain's reader"; Document.lean `UnitContent.judgedIn` | mutants 1 to 8 |
| (4) spec section 4 row 2 deleted (`judgmentsApart` drops `rights@0`) | yes | Document.lean `judgmentsApart` | `test_f1_4_...`; mutant 9 |
| (4) F1.4 (UDHR u111, part document; `Lim_D` the same) | yes | tests/data/composition/pc1g/udhr-u111.json; ChainExamples `udhr`, `udhrLim` | `test_f1_4_udhr_u111_as_a_rights_limitation_is_admitted_and_open`; ChainExamples F1.4 `#guard`s |
| (4) rights twin test (same verdict fields, different ids) | yes | | `test_a_rights_document_and_its_twin_have_the_same_verdict_fields_and_other_identities[2,5]`; ChainExamples F1.1/F1.4 twin `#guard` |
| (5) F1.1 and F1.6 equal verdict fields | yes (`#guard`; Python's `verdict` already dropped the field) | ChainExamples | mutant 20 |
| (5) F1.3b, F1.3c, F1.3i, F1.3j, F1.3k | yes (`#guard`s) | ChainExamples | |
| (5) F1.3e, F1.3f, F1.3g, F1.3h | **no**: pc-1h, with the `meaning_id` exchange (item 5 above) | | |
| (5) F1.8 | **no**: cut to pc-1h at the size line (task: "cut fixtures of (5) to pc-1h") | | |
| Seeded bug "`withoutJudgments` keeps stated identities as written, so F1.3e fails" | **no**: F1.3e is pc-1h's. The nearest: mutant 21 (the twin keeps `judgments@0`) fails F1.3m and F1.3c | | |

Deviations, each recorded only here:
- **The rights reader's reading of "limitation conditions, aims".** A limitation's condition has no formula in `RightsDoc` (`Rights/Tree.lean:34`), only a name. So `rightsAuthorFormulas` and `blockFormulas` read it as an atom of its name: the scan reads names only (spec 3.1, `andAll`). An aim states no author formula: a bar's name is an identifier (`b30`), and its `aimed` atom is generated (`rights__bar__k`, reserved). The norm units outside rights are read as written, guard and author carve-outs, as `correlate` reads them; `correlate_judged` needs them. The comment above `rightsAuthorFormulas` says this.
- **`blockFormulas` decodes a right's lines from the block as written** (`VE.Bridge.decodeFormula`), so that it reads "by its unit": `R.rs` merges `right_lines` units into their right. It reads a limitation's conditions from `R.limits` by name. `R` is otherwise unused.
- **`judgedIn` on a rights document's norm unit:** the unit keeps its `cites` beside the rule (`{"norm", "cites"}`), which the soft decoder refuses. So when the rule as written does not decode, `judgedIn` decodes the rule alone. `judgedIn_soft` keeps its statement and proof.
- **`withoutStatuses`' docstring** says "every other value as written; the front matter is written again compactly". The spec says "every other byte", which no rendering of the front matter can keep.
- **`verdictFields`' docstring** names `undeclared_evaluative`, by ruling item 4, ahead of the spec's amendment of 2e (ruling item 6).
- **`preds_bindAll_eq`:** `lean/audit.py` reads no primed theorem name.

Spec re-read (BUILDER-CHECKLIST 14): a scratch Python comparison, whitespace-normalised, of each statement and given body against spec 3.1 (lines 1458-1484) and 1.7 (lines 980-1011): `rightsAuthorFormulas` (signature and docstring), `correlate_judged`, `blockFormulas`, `andAll` and `preds_andAll`, `judgedIn`'s docstring, `judgmentCodes`, `judgmentGateTexts`, `layerRefusal`, `layerRelaxes`, `noUnitStatus` and `unitStatuses`. All 11 equal ("spec src" on each line). `verdictFields` and `withoutStatuses` deviate as above.

## Seeded bugs and mutants (`mutants.json`, 21 of 21 caught)

Lean is the only product language changed; the Python and Rust product code is unchanged, and the tests are Python. Each mutant was applied to the committed file and rebuilt (`lake build`, and the service for pytest checks). Its named check was run (`VE_NATIVE_PREBUILT=1`, runner /tmp/pc1g-mut/run.py), and the file restored. One per new trusted definition, plus two for the ruling's edits:
1. `rightsAuthorFormulas` without its lines: the proof of `correlate_judged` no longer checks (`mem_author_holder`, Chain.lean:89).
2. `blockFormulas`, a limitation reading no condition: ChainExamples F1.4 `#guard` (:279).
3. `linesFormulas` reading no line: `test_a_judgment_in_a_right_s_line_is_read_by_the_right_s_unit[guard]` (`JudgmentListedUnused: u029 morality`).
4. `ruleFormulas` without carve-outs: the same test's `[unless]` case.
5. `blockFormula` always `⊤` (`| _ => pure .top`): the same test's `[guard]` case.
6. `andAll` over no formula: `preds_andAll` no longer proves.
7. `judgedIn`'s rights block reading nothing: ChainExamples F1.4 `#guard`.
8. `judgedIn` without the `cites` fallback: `test_a_rights_document_and_its_twin_...[2]` (`a soft rule the soft route accepted does not decode again`).
9. `judgmentsApart` with `rights@0`: ChainExamples F1.4 `#guard`.
10. to 12. `dropKey`, `setVerdictFields`, `verdictFields` (keeping each unit's status): ChainExamples 2e `#guard`.
13. `unitStatuses` reading `kind`: ChainExamples F1.3i and F1.4 `#guard`s.
14. to 16. `judgmentCodes` without `JudgmentListedUnused`, `judgmentGateTexts` empty, `layerRefusal` without its `CheckerUnavailable` clause: the 2d `#guard`.
17. `layerRelaxes` reworded: the F1.3c `#guard`.
18., 19. `noUnitStatus` always true, `withoutStatuses` keeping statuses: the F1.3i `#guard`.
20. `verdictFields` keeping `undeclared_evaluative`: the F1.1/F1.4 twin `#guard` (:364).
21. `withoutJudgmentsIn` (pc-1's) keeping `judgments@0` in the twin: the F1.3m (:107) and F1.3c `#guard`s.

Review F1 added a gate before judgment usage for conditioned rights rules. The Lean reader scans the exception on each `norm`, `liberty` and `recognition` line of a `right` or `right_lines` unit, including MIXED parts. The 14 parameterized Python cases in `test_judgments_chain.py::test_a_rights_rule_with_an_exception_condition_keeps_the_layer_apart` cover both condition fields and all rights forms; the Lean `ChainExamples` guards cover each block, line, condition field, and unit/part placement, with empty and factor-only controls. The exact review probe returned an admitted document before the fix and the base rights refusal afterward. A seeded `rightsBlockRules := []` mutant made the Lean guard fail; a seeded `environmentOf` list-empty mutant failed guards at lines 176 and 203, while `listed.dropLast` and `listed.drop 1` failed the minimal-pair guard at line 214. No Python or Rust product code changed.

**Trust-mutation evidence** (`tools/trust_mutants.py` through `mac-pytest.sh --trustmut`, `--test lean/VE/Judgments/ChainExamples.lean`, `--allow trust-mutants-allow.json`):
- On d4aa6e60 (a full run): 108 KILLED, 94 SURVIVOR, 58 UNKNOWN, 63 INVALID. The tool judges with Lean checks only (no pytest), and most survivors were list mutants of lists my fixtures held one element of. Fix (commits d4aa6e60..3e66f10e): `#guard`s with two or more of each (every code, two units, two limitations, a bar, 2e on two sets of two readings with two references), and the allow file.
- On 3e66f10e (a rescore of that record, sharded in 7 parts; cloud parts 2, 4, 7 and local parts 1, 3, 5, 6): **67 KILLED, 0 SURVIVOR, 43 UNKNOWN, 63 INVALID, 150 ALLOWED, 0 NOT RUN**. This was the review F2 record: it exited 1 despite the allow file. The tool's own merge refused the parts because they "disagree on rescore.file": the cloud parts record the `--rescore` path absolute and the local parts relative. I set the field to the relative path in copies of parts 2, 4 and 7, which changes no verdict, and merged them with `trust_mutants.py --merge`. This is the same disclosed path edit as an earlier item's merge (FOLLOW-UPS.md, DEFERRED).
- The 43 UNKNOWNs (32 definition-operator pairs) each make a ChainExamples `#guard` fail ("did not evaluate to `true`"), and the tool's probe could not re-elaborate that guard. They are not survivors. I checked two by hand: the `noUnitStatus` bool-flip makes ChainExamples:406 fail, and `andAll` over `fs.take 1` breaks `preds_andAll` (Chain.lean:212). The allow file names each pair with its guard line. The old record was incomplete evidence, regardless of these explanations.
- Review F2 reran the plan after F1's Lean change. A full Mac run on 8fafa869 timed out after 3 hours and exposed `listed.dropLast`; a 10,000-second budgeted Mac run on 85660f91 recorded 125 KILLED, 1 SURVIVOR (`listed.drop 1`), 0 UNKNOWN, 51 INVALID, 94 ALLOWED and 60 NOT RUN. Both truncations are now caught by the two-order minimal-pair Lean guard; seeded builds fail at ChainExamples:215. The SURVIVOR is M250 (Document.lean:1162, `environmentOf`, list-drop-first, the `listed` of `listed.contains "rights@0"` made `(listed.drop 1)`). The record predates that guard (added in 2dd6702d6 and e572d7890). On e19be795b I applied exactly M250's edit in a scratch copy of `lean/` and ran `lake build VE.Judgments.ChainExamples`. The build fails with the guard's own refutation, its only Lean error: `ChainExamples.lean:215:0: Expression ... did not evaluate to true`. In the `["rights@0", "judgments@0"]` order the mutant takes the soft-norms branch and gives another fault. So nothing changed in `lean/` and there is no allow entry. The record's other six cuts at that line (M021, M041, M090, M105, M128, M209) and the other list-drop-first one (M224) were already KILLED. The unbudgeted full run and identical-input rescore on the final Lean tree were stopped with fix round 1 at e572d7890 and left no result. The passing record on the final Lean (review F2) is moved to pc-1gtm by the DRI's fix-round bound (reviews/dri-decisions-20261105-lp0401.md Q3, applied by reviews/dri-decisions-20261105-lp0401-apply.md item 1; R9), and the committed `trust-mutants.json` is the run on 85660f915 with the counts above (125 KILLED, 1 SURVIVOR `listed.drop 1`, 51 INVALID, 94 ALLOWED, 60 NOT RUN; exit 1).
- The allow file (`trust-mutants-allow.json`, 70 entries) covers equivalent mutants, mutants that break only `correlate_judged`'s proof, the `judgedIn` retry that only `test_a_rights_document_and_its_twin_...[2]` reaches, mutants that do not elaborate, and the probe UNKNOWNs above. Each entry gives its reason.

## Trust

`uv run python tools/trust_map.py --check` on the final Lean: "against fd9f25f9bfaa: K +0, S +85, D +38, G +29, tied +0, unclassified +0, trusted +132", then "PASS: K, S and untied [V] within fd9f25f9bfaa and the allowances introduced since". Per file: Document.lean S +76, G[V] +9 and D[V] +1; Chain.lean S +9 and D[V] +37. The class-total G growth also includes the F1 routing helpers classified G[R]. The classes are in `tools/trust-classes.json`, and the allowances (S +84, S +1, V +45, V +1, V +1) in `docs/trust-baseline.json`, SIGNED by standing ruling R16. FOLLOW-UPS.md row "## pc-1g" asks for the ties pass. 132 is within R16's 150, with no K growth. Proofs (P) and ChainExamples (T) are not trusted.

## Size

`git diff --numstat $(git merge-base HEAD main)...HEAD`, hand-written files only (no generated inventories, pins or codemaps; the mutant JSON evidence excluded): about +905 / -30. Chain.lean +247, ChainExamples +283, Document.lean +111, the tests +87, the F1.4 data +28, `tools/trust-classes.json` +40, the manifest pin +11 and the docs about +105. That is over the ~600 size line. The proofs of `correlate_judged` and of the block readers are about 150 lines of Chain.lean. About 270 lines of ChainExamples are fixtures and `#guard`s, about 130 of them added so that the trust-mutant tool, which runs only Lean checks, kills what pytest already caught. The DRI's stop ruling (item 1) names these parts for this item, so nothing more was cut. F1.8 and F1.3e to F1.3h were cut to pc-1h.

## Tests

- Iterating: `tests/test_judgments_chain.py` and `tests/test_judgments_document.py`, the cases touched (`VE_NATIVE_PREBUILT=1 uv run pytest -q ... -k ...`: "5 passed", "2 passed", "2 passed", "1 passed"); `lake build VE.Judgments.ChainExamples` after each Lean edit.
- On the finished code: `regen_generated.py --write` ("wrote 35 entries"), `python3 lean/audit.py` (PASS, above) and `trust_map.py --check` (PASS). Each later Lean edit (the stop ruling's, then the fixes below) was followed by the same regen and check.
- Selected tests: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`. The first run (04d62d20) had 2 failing files, test_judgments_exercised.py (the block readers were stated about by no theorem) and test_assurance_manifest.py (Document.lean's pin; Chain.lean now reads JSON); it stopped at its 5-failure limit. Fixed in 8232b41f2: five theorems about the block readers, Chain.lean classified under `other_json`, and Document.lean re-pinned whole. Those two files then passed (`uv run pytest -q tests/test_assurance_manifest.py tests/test_judgments_exercised.py`: "143 passed"), and the full selection on 8232b41f passed: "selected tests ran on GitHub Actions (6 shards, run pc-1g-8232b41f-t741741); exit=0". The later commits change only ChainExamples `#guard`s, the class table, the allow file and docs.
- Pre-existing failures on main (main-known-red.txt) are not touched here.

## Pilot bytes

0 B directly. Neither the pinned constitution translation nor the pinned UDHR translation lists `rights@0` beside `judgments@0`; the UDHR pilot's environment lists neither `rights@0` nor `judgments@0`. PC-2a and PC-5 build on the rights reader. This is an estimate: no pilot audit was run (L70: no whole-document runs).

## Next

pc-2a (after PC-1) and pc-5 (after sc-1ae, sc-5rc and PC-1), then pc-2b. The DRI's stop ruling adds pc-1h (G3, F5, F1.3e to F1.3h, F1.8) and a follow-up item for the restated round-trip lemma, `swap_correct` and `verdictFields`, after their statement review.

## Base

The branch is based on fd9f25f9b; main has since moved 165 commits. Of those, pc-2a's change Document.lean in other functions (`decodedEnvironment`, `softSourceNorms`, `environmentOf`, `layeredIds`, `admitGraph`, `check`), so the file merges without overlap. The generated files (pins, inventories, the assurance manifest's pin and the class table) need the merge train's regen (R12). I did not sync: a sync invalidates the trust-mutant record, whose last run took 17,839 s of mutant time.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no new relayed field or response member. The document answer's schema is unchanged; rights@0 documents with the layer answer through the existing `judgments` member (jt-2b's fuzz, tests/test_judgments_answer.py).
2. PASS: every plan row and deliverable is in "Plan rows", with its commit and check, or with the DRI ruling that moved it (reviews/dri-decisions-20261103-pc-1g-stop.md items 1 to 6). No Python copy of a Lean decision (Python product code is unchanged), and no permanent report test. The files in-flight branches also edit are in "Base".
3. PASS: 21 hand mutants, one per new trusted definition plus the ruling's edits (`mutants.json`, 21 of 21 caught by a named `#guard`, proof or test). The committed trust-mutant record `trust-mutants.json` is the budgeted run on 85660f915 (1 SURVIVOR `listed.drop 1`, M250, now caught by the two-order guard at ChainExamples:215, checked by hand on e19be795b, and 60 NOT RUN; exit 1); the passing record on the final Lean is FOLLOW-UP pc-1gtm (lp0401 Q3).
4. PASS: base and head side by side. The twin tests compare each layered case with its plain twin (`test_a_rights_document_and_its_twin_...`, ChainExamples F1.1/F1.4 `#guard`s). Plain documents are unchanged: `judgmentsApart` only changes what lists `judgments@0`. The selected run passed (6 shards, exit 0).
5. N.A.: Python reads no new field from a Lean answer.
6. PASS: the chain runs the gate on the final HEAD. Not synced with main (see "Base"); the merge train syncs.
7. PASS: the DELTA cells read "SIGNED by the DRI 2026-11-01 (reviews/dri-decisions-20261101-pc-1.md item 1)", "SIGNED by the DRI 2026-11-03 (reviews/dri-decisions-20261103-pc-1g-stop.md item 2)" and "SIGNED by standing ruling R16 (DRI-RULINGS.md), pc-1g, 2026-10-18"; no signature is reserved.
8. PASS: the user-visible change (rights@0 beside `judgments@0` answered, and the refusal text for a document without a rights block) is DELTA row 1, with its tests; the trusted boundary is row 2.
9. PASS: the selected run included tests/test_judgments_chain.py, test_judgments_document.py, test_judgments_exercised.py and test_assurance_manifest.py. The first run's two failures came from this change and were found by the selection.
10. PASS: the proved statements (`correlate_judged`, `preds_andAll`, the block-reader theorems) equal the spec or pin the definitions' values. Mutants 1 and 6 break proofs. No hypothesis was added to an approved statement; the false statement (`swap_correct`) has a mechanised counterexample (`twoSets`) and a DRI ruling.
11. N.A.: no budget, limit or deadline added. The readers run once per rights block, on blocks the rights route already decoded.
12. N.A.: no new pass over a document beyond one read per rights unit; no pilot timing (L70).
13. PASS: `uv run python tools/gate_collection.py --check --prebuilt`: "1 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers" (the renamed rights parametrisation).
14. PASS: both directions. The rights reader admits F1.4 and refuses a judgment it does not find (mutants 3 to 5: `JudgmentListedUnused`). `layerRefusal` accepts the layer's codes and gate texts and rejects validation texts (2d `#guard`). `noUnitStatus` covers stated and not stated. Every count in this report quotes its command. Spec re-read: "Plan rows", Spec re-read (11 statements, whitespace-normalised).
