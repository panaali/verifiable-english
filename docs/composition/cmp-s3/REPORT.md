# cmp-s3: totality premises and the slot of the head (Relation.lean, spec 8.4)

Status: Relation.lean built, five of 8.4's six theorems proved; HEAD is the branch tip; no DRI signature reserved.
Two spec statements were false as written; the DRI signed one added hypothesis each (reviews/dri-decisions-20261104-cmp-s3.md):
`clauseSlot_labelled` (Q3 B1, delivered) and `elaborate_plain` (Q1 A1, cmp-s3b); counterexamples are `#guard`s.
Cut to **cmp-s3b**: `clauseSlot_wellFormed`, 8.5 (Wire.lean), the `clauses-elaborate` mode, the registration (Q2),
`ve/right_clauses.py` and the differential, 9.2, 9.3 and W1's budget. No answer changes (DELTA.md).

Spec: docs/spec/right-clauses.md draft 3 (on main from cmp-s3a). Decisions read:
reviews/dri-decisions-20261031-spec-right-clauses.md items 1-7 and reviews/dri-decisions-20261104-cmp-s3.md (Q1-Q3). cmp-s3a's REPORT and names are used as they are.

## Deliverables (task rows)

| Task row | Delivered | Evidence |
|---|---|---|
| (1) `totalF`, `relPremisesLabelled`, `relPremises`, `clauseSlotLabelled`, `clauseSlot` | yes, word for word | 95b618a8f; statement check below |
| (1) `clauseSlot_eq`, `clauseSlot_no_total`, `clause_fails_not_selected`, `relation_some_bearer` | yes, word for word, proved | `lake build` rc 0 (1280 jobs); `python3 lean/audit.py`: "PASS: 764 source files; 8408 named theorem declarations" |
| (1) `clauseSlot_labelled` | proved with one added hypothesis `hl` (`Lim_D`'s labels distinct), SIGNED by the DRI (Q3 B1) | b5f33f3da; counterexample `cxDoc` `#guard`, Examples.lean |
| (1) `clauseSlot_wellFormed` | **no: cmp-s3b** (see "Cut") | - |
| (2) Wire.lean, `decode_unstructured`, `elaborate_plain`, `clauses-elaborate` | **no: cmp-s3b**; `elaborate_plain` is false as stated; the DRI signed `(hd : PlainOnWire D)` (Q1 A1) | depth `#guard` (`notChain`), Examples.lean |
| (2) `right-clauses@0` in the registered list, ve/profile_table.json | **no: cmp-s3b**, with the head's mode (Q2, plan accepted by the DRI) | QUESTIONS.md Q2 |
| (3) ve/right_clauses.py, the differential | **no: cmp-s3b** | - |
| (4) K3, K13; K2's `Rel_D = []` | yes, `#guard`s | Examples.lean "Relation.lean: `Rel_D` and the slot" |
| (4) K9, K10, K15, F11-F14, 9.3, W1's 10,000-node budget | **no: cmp-s3b** (the wire decoder's and the runner's) | - |
| (5) seeded bugs | 9 planted alone, all killed; trust mutants 32 killed, 0 survivors | mutants.json, trust-mutants.json |
| 8.1 lean/RIGHT-CLAUSES.md | yes (Tree, Plain, Relation) | lean/RIGHT-CLAUSES.md |
| OPEN-6 `interface` value | nothing to set: pc-3 merged first and `right-clauses@0`'s rows already carry `.rewrite 20` | `lean/VE/Compose/Dispatch.lean:815-816`; `ContractExamples.lean:105` |

No import of `VE.Readings`: Relation.lean imports `VE.RightClauses.Plain` only. Frozen `Rights/*`, `SoftNorms/*`,
`Norms/*`, `Route/*` and `Compose/*` are untouched (`git diff --stat main...HEAD -- lean/VE/Rights lean/VE/SoftNorms
lean/VE/Norms lean/VE/Route lean/VE/Compose` is empty). Plain.lean (cmp-s3a's) changes by a refactor only:
`entry_facts` is taken out of `plain_guard`'s proof, and the statements are unchanged.

## Cut: cmp-s3b

- `clauseSlot_wellFormed`. `totalF` must be well formed in `envAt (soften (correlate (plain D))) 0`. `relationOk`
  types the relation and `H_R` over `baseEnv D = envAt D.doc.soft.base 0`. These two vocabularies hide different
  layer names: the base tree's and the correlated tree's, each read off its own dependency order. The proof needs
  every regulated or defined name to be a layer name of the base tree. Only `regName_layer` gives that, and it needs
  `Valid` of the base tree, which nothing derives from `WellFormedRights (plain D)`. The proof also needs the holder
  slot's sort from `checkShape`. Together that is beyond this item. Nothing here depends on it: 4.2 reads it when the
  head runs (cmp-s3b).
- 8.5 whole. `elaborate_plain` takes the DRI's added `(hd : PlainOnWire D)` (Q1 A1); `decodeClauseDoc` reads a W2 document (units with spans and
  `reading_sets`), so `stripElided` and `elaborateJson` must also take its rights source, a reading of the 8.5 notes to
  confirm there. The mode (Registry, Protocol, response shape, encoder theorem, relay, route cases, fuzz tests) and
  W1's budget fixture come with it; the DRI's evaluator rule of 2026-10-27 then applies there.
- The registration (Q2), `ve/right_clauses.py`, the differential, 9.2, 9.3 as saved evidence.

## DRI questions (QUESTIONS.md; answered: reviews/dri-decisions-20261104-cmp-s3.md, 16:05Z)

- Q1, `elaborate_plain` is false: `budgetFormula` refuses depth 65, `WellFormedRights` bounds no depth, and `plain`
  nests a depth-64 clause one level deeper. `#guard` (`notChain`) shows both sides. Ruling: A1 SIGNED (the hypothesis).
- Q2, registration without a runner changes a profile-on text. Ruling: plan accepted; it lands with the mode in cmp-s3b.
- Q3, `clauseSlot_labelled` is false: at `⟨cx, [], []⟩` both hypotheses hold and `Lim_D` repeats a label. `#guard`
  (`cxDoc`) shows it. Ruling: B1 SIGNED, as delivered; the statement change is recorded in DELTA.md.

## Seeded bugs (each planted alone, `lake build VE.RightClauses.Examples`, restored)

All in Lean (no Python or Rust changed). `test` is the first check that fails. For the bugs a proof stops before
Examples builds, mutants.json also lists the Examples `#guard`s that fail on a copy of the definitions with the bug.

| Bug | File, definition | Fails |
|---|---|---|
| totality on a non-holder slot accepted (K8) | Plain.lean `relationOk` | Examples.lean:142 K8 `#guard` |
| `Rel_D` built for total null (K2) | Relation.lean `relPremisesLabelled` | Relation.lean:39 `clauseSlot_no_total`; Examples.lean:289 K2 `#guard` |
| ρ's variables exchanged | `totalF` | Relation.lean:254 `relation_some_bearer`; Examples.lean:292 K3 |
| holder guard dropped from ρ | `totalF` | Relation.lean:251; Examples.lean:301 |
| wrong other slot | `totalF` | Examples.lean:302 (slots (1, 0)) |
| label from the right, not the rule | `relPremisesLabelled` | Relation.lean:117 `clauseSlot_labelled`; Examples.lean:292 |
| `relPremises` empty | `relPremises` | Relation.lean:29 `clauseSlot_eq`; Examples.lean:293 |
| `Rel_D` before `Lim_D` | `clauseSlotLabelled` | Relation.lean:29; Examples.lean:311 K13 |
| slot drops `Rel_D` | `clauseSlot` | Relation.lean:29; Examples.lean:293 |

The profile-off text (K10) and Python's plained bytes (the differential) have no code in this item: cmp-s3b.
Trust mutants (`mac-pytest.sh --trustmut -- --max-mutants 1000`, then `--rescore` with the allow file): first run
28 KILLED, 4 SURVIVOR, 6 UNKNOWN. The survivors were `take 1` on `Rel_D`; the `twoTotal` fixture kills them. The final
run (head 1506199fd) exits 0: 32 KILLED, 0 SURVIVOR, 0 UNKNOWN, 12 INVALID, 6 ALLOWED. The allow file lists only the
mutants that do not elaborate.

## Trust (R16)

`uv run python tools/trust_map.py --check`: K +0, S +13 (lean/VE/RightClauses/Relation.lean), D/G +0, unclassified
+0; "PASS: K, S and untied [V] within 5c6a544446dc and the allowances introduced since". Allowance recorded with
`trust_map.py --allow ... --signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), cmp-s3, 2026-10-18"`.
The FOLLOW-UPS row is under "## cmp-s3".

## Size

`git diff --numstat $(git merge-base HEAD main)`, hand-written: Relation.lean 264, Examples.lean 73, Plain.lean 27,
VE.lean 1, RIGHT-CLAUSES.md 35, tools/trust-classes.json 17, QUESTIONS.md 53, DELTA.md 16, mutants.json 12, allow file
6, this REPORT. That is about 600 with the REPORT. Generated, not counted: Audit.lean, statements.txt, declarations.txt,
axioms.txt, predicates.txt, codemap, trust-baseline.json, trust-mutants.json.

## Overlap with branches in flight

Additive lines only, in shared registries: `lean/VE.lean` (ap-3db, ci-2, df-5, et-4b, pe-1, ps-1, wg-2, me-1) and
`tools/trust-classes.json` (ap-3db, ci-2, df-5, et-4b, pc-1g, ps-1, wg-2, me-1). et-4b edits
`lean/VE/Compose/Dispatch.lean` and ve/profile_table.json, which this item no longer touches. No branch touches
`lean/VE/RightClauses/`.

## Tests

`zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on HEAD 35ecdc5f (clean): "exit=0;
failed/error ids=0", "recorded 418 units ... 0 failed" (/tmp/cmps3/select.log). The selection includes `lake build`
and `python3 lean/audit.py`. After it, two fixtures and their trust classes were added. Then `lake build
VE.RightClauses.Examples` and `trust_map.py --check` were rerun (both pass), plus tests/test_trust_budget.py,
tests/test_trust_ratchet.py and tests/test_lean_statements_parts.py ("117 passed"). `regen_generated.py --write --skip
route-cases` rc 0: route-cases needs a Rust release binary this worktree lacks, and none of its inputs changed. The full
gate is the chain's. No test of main-known-red.txt was touched.

## Pilot bytes

None expected: no route reads these definitions before cmp-s3b. The UDHR rerun's figure (spec 9.3) is cmp-s3b's
estimate.

## Spec re-read

- 8.4 against docs/spec/right-clauses.md:452-506, whitespace-normalised, docstrings included: OK for `totalF`,
  `relPremisesLabelled`, `relPremises`, `clauseSlotLabelled`, `clauseSlot`, `clauseSlot_eq`, `clauseSlot_no_total`,
  `clause_fails_not_selected`, `relation_some_bearer`. `clauseSlot_labelled` differs by `hl` (Q3);
  `clauseSlot_wellFormed` is missing (cut).
- 1.3 (:78-94): ρ_n is `∀x:s_j. H_R(x) → ∃y:s_o. pred(t_a, t_b)`, label `rights:relation:<n>:total`, `Rel_D` in
  document order after `Lim_D` (K3, K13, `twoTotal`).
- 4.3 (:221-226) and 4.4 (:228-234) against `clause_fails_not_selected` and `relation_some_bearer`.

## Next item

cmp-s3b (see "Cut"), with the DRI's rulings on Q1 and Q2; cmp-s3ab (`plain_wellFormed`) stays as cmp-s3a named it.

## Pre-review gate repair (2026-11-05)

The full gate on f330aff00 failed only
`tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`:
`lean/VE/RightClauses/Examples.lean` was absent from the manifest's JSON-handling inventory
(`gate-result.json`, commit_sha f330aff00, counts.failed 1). Its `notChain` fixture builds JSON formulas
for the Q1 depth `#guard`; no runtime decoder or runner imports that file. The file is now classified
under `lean_decoders.other_json` in `ve/assurance-manifest.json` with that reason. This changes no
checker, verdict or profile output, so DELTA.md needs no new row.

`.venv/bin/pytest -q tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`
returned `1 passed`; `.venv/bin/python tools/regen_generated.py --write --only assurance-manifest`
returned `wrote 1 entries` and left the manifest's layout intact. The full gate runs on the committed
final HEAD; `gate-result.json` records its result.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained answers: N.A., no relayed answer (no mode, wire or Python in this item).
2. Deliverables: PASS, the table above; the cuts are named cmp-s3b under the size rule; the statement changes are
   signed by the DRI (Q1, Q3).
3. Tests can fail: PASS, mutants.json (9 killed) and trust-mutants.json (32 killed, 0 survivors) with the allow file.
4. Python/Lean/Rust agree: N.A., Lean only; the differential is cmp-s3b's.
5. R8 binding: N.A., no relay.
6. Gate evidence matches HEAD: PASS, the chain runs the gate on the final HEAD; no evidence reads live git.
7. No unsigned item: PASS, R16 allowance signed by the standing ruling; `clauseSlot_labelled`'s hypothesis signed by
   the DRI (reviews/dri-decisions-20261104-cmp-s3.md Q3), recorded in DELTA.md "Statement changes".
8. DELTA: PASS, DELTA.md: no answer changes (`grep -rn RightClauses lean/VE --include=*.lean` finds only
   `lean/VE/RightClauses/*`, VE.lean and Audit.lean).
9. Test selection: PASS, `tools/select_tests.py --base $(git merge-base HEAD main)` selects `lake build` and
   `python3 lean/audit.py`, which run every `#guard` and proof the seeded bugs break.
10. Statements say what is claimed: PASS, the statement comparison above. Each mutant breaks a proof or `#guard`.
    The added hypothesis has a DRI ruling (Q3) and a mechanised counterexample (`cxDoc`).
11. Budgets fail closed: N.A., no evaluator, runner or budget in this item.
12. CPU/memory: N.A., no route calls the new code.
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. K2 checks `Rel_D = []` and K3 its one premise; K3's slot is
    false on `onlyAnn` and true on `both`. The line selects at (Texas, Bob) on `both` and not on `onlyAnn`.
    `cxDoc` shows the label hypothesis is needed and K13 that it holds there. The spec re-read is above.
