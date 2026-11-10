# ci-3b: the `String.splitOn` lemma library, `preposed_eq` and `readStep_conservative` (commands-imperatives section 7)

No DRI signature is reserved.

Status: built. Both statements are proved, with no `sorry`, and `python3 lean/audit.py` gives PASS:
- `preposed_eq`, with the DRI's `hb`;
- `readStep_conservative`, exactly as section 7 states it.

Nothing is cut. The DRI ruled twice:
- reviews/dri-decisions-20261109-ci-3b.md item 1: the proof stays in ci-3b;
- reviews/dri-decisions-20261109-ci-3b-size.md item 1: the item is accepted at its final size, and the ~800-line
  trigger is waived.

There is no ci-3b follow-up item. No route calls `readStep`, so no verdict, wording or pilot byte changes. There is no
DELTA row: the item adds theorems only. Trust growth is `splitOnL` (V +12), under R16
(reviews/dri-decisions-20261109-ci-3b.md item 2). Next item: ci-4, after ci-3.

## Review fix (ci-3b-review.final.md, review of 5f4760e2c)

One finding, F1 (A, wording-only overclaim), fixed in 0bdf509e8. There is no B finding. C1-C4 are follow-ups for the
DRI and are not changed here, except that the StepsProofs line numbers above and in `mutants.json` now point at the
new lines.

| Finding | Fix | Regression test | Commit |
|---|---|---|---|
| F1: the module comment said ConditionScope "never fires" for `If <c>, <x>.`, but that holds only for the wording's only shape | The module comment, `shapes_preposed` and `hasThen_preposed` now state the one-shape condition (`shapes s = [.preposed c x]`, `preposed_eq`'s `h`). A `#guard` (StepsProofs.lean:676-682) pins the two-shape counterexample: the first `<x>` holds `, then ` and the step is ConditionScope. The REPORT's lemma list states the same condition | `tests/test_commands_ci3b_review.py` (both tests); the `#guard` under `lake build`; seeds S8 and S9 | 0bdf509e8 |

- PROBE F1 exits 1 on 5f4760e2c and 0 after the fix.
- The class: every StepsProofs doc comment that claims `<x>` is one piece of the split, holds no `, then `, or
  escapes ConditionScope must name the hypothesis. The test scans all of them, not only line 7.
- No DELTA row: the change is comments, a `#guard` and evidence. Nothing calls `readStep`.
- Tests on 54cf5f054:
  - Selected tests (`mac-pytest.sh --select -- --base <merge-base> --run`): 129 units in 5 shards, all passed, exit 0.
    They include tests/test_commands_ci3b_review.py.
  - `lake build`: PASS (1330 jobs).
  - `python3 lean/audit.py`: PASS (798 source files, 8859 theorem declarations).
  - `tools/regen_generated.py --check`: 38 entries.
  - `tools/gate_collection.py --check --prebuilt`: 2 added, 0 removed.
  - Not run: the full suite and the gate, which the merge train runs.

## Plan rows delivered (spec 9a12df17a section 7; plan CI-3; task deliverables)

| Deliverable | Commit | Evidence |
|---|---|---|
| (1) SplitOnLemmas.lean: splitOn and intercalate lemmas for a multi-character separator, with `#guard`s | 7116b078a, 469f86398, 93b8395cd | `lake build` PASS; `#guard`s at SplitOnLemmas.lean:295-304 |
| (2) `preposed_eq` (with `hb`) | 7116b078a | StepsProofs.lean `preposed_eq`; `hb` fixture (`let p`) at :670-674 |
| (2) `readStep_conservative` | 469f86398 | StepsProofs.lean `readStep_conservative`; the conservative `#guard` at :664-666 |
| (2) answer "Does W1's act linter make `hs` unnecessary?" | this REPORT | below |
| (3) lean/VE.lean import; tools/layer_policy.py layer 4 | 7116b078a | `python3 tools/check_lean_imports.py` exit 0 (S4 shows that it can fail) |
| (3) generated inventories (R12) | 5976ca50c | `uv run python tools/regen_generated.py --write` rc=0 |

Two table rows outside the task's file list were forced by tests (commit ec76949a9). ci-3a extended the same two
tables:
- `tools/trust-classes.json` classes `splitOnL` as G[V], untied. `tests/test_consolidation_tools.py::
  test_committed_trust_table_covers_every_declaration` requires every definition to be classified. Untied G[V] keeps
  the trusted count R16 allows (+12).
- `ve/assurance-manifest.json` gives StepsProofs.lean an `other_json` reason. `tests/test_assurance_manifest.py::
  test_every_json_handling_lean_file_is_classified` requires one, because `readStep_conservative` names `Lean.Json` as
  section 7 states it.

### SplitOnLemmas.lean

`splitOnL` is a `List Char` spec of `String.splitOn`. Its lemmas, over `List Char` and over `String`:
- `splitOn_data` (the bridge): `s.splitOn t = (splitOnL t.data s.data).map String.mk` for every `t ≠ ""`. It is proved
  by following `String.splitOnAux` byte by byte, including the restart after an unfinished match. The guards at
  :303-304 check it on an unfinished and an overlapping match.
- `splitOn_none` (:295): a separator that does not occur gives the whole string.
- `intercalate_splitOn` (:296): `t.intercalate (s.splitOn t) = s`.
- `splitOn_free` (:297): the pieces hold no occurrence of the separator.
- `splitOn_first` (:299): the first-occurrence decomposition `s = a ++ t ++ b`, with `a` free of `t`.
- `splitOn_two` (:300): there are at least two pieces exactly when the separator occurs, checked both ways.
- `prefix_first` (:301): a prefix without the separator's first character stays inside the first piece.
- The `List Char` twins of each.

`VE.Acts.Lexical.splitOn_space` (one space) and `VE.Readings`' `splitOn_dunder` are special cases of these. They are
left in place because their files are outside this item.

### StepsProofs.lean

- `preposed_eq` uses three lemmas, the first two under its `h` (`If <c>, <x>.` is the wording's only shape,
  `shapes s = [.preposed c x]`):
  - `shapes_preposed`: `<x>` is a piece of the split at `, `;
  - `hasThen_preposed`: `<x>.` holds no `, then `;
  - `trimmed_infix`.
- `readStep_conservative` is `readStep_core` plus `one_begins`:
  - `readStep_core`: `hs` rules out the `seq` shape;
  - `one_begins`: over a decoded environment, a wording that `readCommand` reads as `one` has a body that begins with
    neither `If ` nor `Then `.
- `one_begins` traces the act linter:
  - `body_prefix` and `splitLast_prefix`: the body keeps the prefix through `splitLastIf` and the `Do not ` test.
  - `decoded_actIn`: the act passes `canonicalActIn` (`canonicalAct`, or `Acts.Lexical.check` under `acts@0`).
  - `actIn_shape`: the act is `" ".intercalate W` and begins `{0} `. No word of W without a brace is `if` or `then` in
    any case, by `actReserved` and by `check_no_clause`.
  - `act_rest` and `verb_head`: the second word follows `{0} ` and opens no slot (`actVerb`, through `surfaceWords`).
  - `decode_templates` and `templates_act`: `slotsApart` holds for the act (`checkTemplates`).
  - `filled_word`: `fillHoles` copies the verb unchanged, and `slotsApart` refuses a slot attached to a letter, so the
    filled text begins `if `/`then ` only if the verb is `if`/`then`. The linter refuses that verb.
- Fixtures (:657-682):
  - the rewritten wording "Click Ask, if draft is approved.";
  - `hasThen`;
  - the merged shape;
  - a conservative row over `E_web`;
  - `hb`'s counterexample;
  - `h`'s counterexample (review F1): with two `If` shapes the first `<x>` holds `, then ` and the step is
    `ConditionScope`.
- The module defines no `def`: the `hb` fixture is a `let` inside its `#guard`.

### Statement comparison

Both theorems equal section 7's text after whitespace normalisation, except for `hb`. The check is an inline `python3`
snippet: it cuts `theorem <name> ` up to the first blank line or `:=` in the spec (`git show
9a12df17a:docs/spec/commands-imperatives.md`) and in StepsProofs.lean, and joins whitespace.
- Output for `preposed_eq`: `equal after removing hb: True | hb present: True`.
- Output for `readStep_conservative`: `True`.
- The DRI's size decision re-checked `readStep_conservative` word for word.

The one addition, in `preposed_eq` after `h`: `(hb : (trimmed s).utf8ByteSize ≤ maxWordingBytes)`. SIGNED by the DRI
2026-11-09, reviews/dri-decisions-20261109-ci-3a-wording.md item 1. `readStep_conservative` does not need it.

`hb` is needed. The counterexample is mechanised in the `#guard`s at StepsProofs.lean:670-674:
- "If draft is approved," ++ 390 spaces ++ "click Ask." has the shape `.preposed "draft is approved" (389 spaces ++ "click Ask")`.
- Its trimmed form is over `maxWordingBytes`, so `step` gives `.limit`.
- `web` of the rewritten wording gives `.one ⟨.require, "click_ask_required", [], approvedDraft⟩`, because
  `readCommand` trims the spaces away.

So `preposed_eq` without `hb` is false.

spec re-read:
- `preposed_eq` against spec 9a12df17a docs/spec/commands-imperatives.md:960-962: names `c x r h`, the `↔` order, and
  `capitalise x ++ ", if " ++ c ++ "."`.
- `readStep_conservative` against the same file at 954-958: `j r hd h hs`, `.one r false`.
- The `hs` question against the same file at 1053-1059.

## Does W1's act linter make `hs` unnecessary?

No. `hs` stays, as the spec's computed answer says. What is proved:
- `readStep_core` uses `hs` once, to rule out the `seq` shape (the body has no `, then `).
- `one_begins` rules out the `If ` and `Then ` shapes from the act linter, without `hs`. It covers only the act's first
  word after `{0}`.

What dropping `hs` would need, and what is not proved here:
1. A filled act holds no `, then `: no later act word and no fill does.
2. No condition reading holds `, then `.

The spec computed both: "no act word or fill holds a comma", and english-lean has no such sentence. This item proves
neither.

The proof uses `slotsApart` (S7 shows `templates_act` failing without it). By a hand trace that is not mechanised, the
act `{0} then{1}` passes `canonicalAct`. With a definite whose text begins with a space, it would read "Then draft." as
`one`, so `checkTemplates` is what excludes it.

## Seeded bugs and mutants (`mutants.json`, `trust-mutants.json`)

Each was planted, shown failing, and restored. Lines are on the final HEAD.

1. **S1 (Lean, `preposed_eq` fixture):** `capitalise` lower-cases the first letter in `lean/VE/Commands/Steps.lean:24`.
   - StepsProofs.lean:660 fails. This was shown with `lake env lean` on a copy without the `E_web` fixtures, because
     StepsProofs imports StepsExamples and StepsExamples.lean:40 fails first.
2. **S2 (Lean, splitOn `#guard`):** the separator `", then "` is shortened to `", "` at SplitOnLemmas.lean:298. That
   line fails.
3. **S3 (Lean, the R16 mutant of `splitOnL`):** a cut drops `sep.length - 1` characters (SplitOnLemmas.lean:21).
   The `#guard`s at :303-304 fail, and so do the proofs at :26 and :42.
4. **S4 (Python, `tools/layer_policy.py`):** the two modules are left out of layer 4.
   `python3 tools/check_lean_imports.py` exits 1 with "new outward Lean import: VE.Commands.StepsProofs ->
   VE.Commands.Steps". Restored, it exits 0.
5. **S5 (Lean, conservative):** in Steps.lean:40, `shapes` makes an `after` shape for a body that begins `C`.
   - `readStep_core` fails at StepsProofs.lean:580 and `shapes_preposed` at :64.
   - StepsExamples.lean 43, 45, 50, 57, 58, 77, 163 and 185 fail.
6. **S6 (Lean, act linter):** `actVerb` accepts a slot as its verb (`lean/VE/SpeechActs/Wire.lean:943`).
   - `verb_head` fails at StepsProofs.lean:332 (shown on a copy without fixtures).
   - Examples.lean:288 fails.
7. **S7 (Lean, act linter):** `checkTemplates` without its `slotsApart` test (Wire.lean:225). `templates_act` fails at
   StepsProofs.lean:408 and :412.
8. **S8 (Lean, review F1):** `shapeOutcome` no longer refuses a preposed `<x>` that holds `, then `
   (Steps.lean:86, `if false then conditionScope`). StepsExamples.lean:70 fails; with that guard commented out,
   StepsProofs.lean:678 (the two-shape counterexample) fails.
9. **S9 (comment, review F1):** StepsProofs.lean's comments as at 5f4760e2c. Both tests of
   tests/test_commands_ci3b_review.py fail.

The trust-mutants sweep was run with `mac-pytest.sh --trustmut -- --max-mutants 1000`.
- `trust-mutants-full.json`: 15 KILLED, 11 UNKNOWN, 1 INVALID.
- With `trust-mutants-allow.json`, `--rescore` on the final table gave 15 KILLED, 11 ALLOWED, 1 INVALID,
  0 SURVIVOR, exit 0 (at 17e6b4e3b).
- After the review fix, which is the final Lean change, a full run (no `--rescore`) with
  `--allow trust-mutants-allow.json` on 0bdf509e8 gives `trust-mutants.json`: 15 KILLED, 11 ALLOWED, 1 INVALID,
  0 SURVIVOR, 0 UNKNOWN, 0 NOT RUN, exit 0. It ran in the cloud pool as four merged shards (`shards`).
- Lean refuses the text of every allowed mutant. Nine break `splitOnL`'s own termination proof (`decreasing_by`,
  SplitOnLemmas.lean:26), and the two `<` mutants split the `<+:` token.

## Trust, size, overlap

- Trust: `uv run python tools/trust_map.py --check` exits 0 on the final HEAD, against 1531891aaf6b: "K +0, S +0,
  D +0, G +12, tied +0, unclassified +0, trusted +12". The +12 is `splitOnL`, classed G[V] untied.
  - The allowance in docs/trust-baseline.json: "SIGNED by standing ruling R16 (DRI-RULINGS.md), ci-3b, 2026-11-09;
    reviews/dri-decisions-20261109-ci-3b.md item 2".
  - /home/seyran/code/manage-agents/FOLLOW-UPS.md "## ci-3b" asks the ties pass to class it P.
  - Its mutant is S3.
- Size (`git diff --numstat $(git merge-base HEAD main)`): SplitOnLemmas.lean 306 and StepsProofs.lean 671.
  - Those are 977 whole-file lines: 823 non-blank non-comment, 783 without `#guard`s, imports and opens. The DRI
    accepted this (ci-3b-size decision).
  - Non-proof hand-written lines: lean/VE.lean 1, tools/layer_policy.py 3, tools/trust-classes.json 5,
    ve/assurance-manifest.json 3, this REPORT, and the mutants files.
  - SplitOnLemmas.lean was 287 lines after deliverable (1) (7116b078a).
- Overlap:
  - lean/VE.lean (cmp-s3a-cfr-1, rights-cfr-4, sc-7, me-1) and tools/layer_policy.py (et-5, rights-cfr-4) are edited
    in flight elsewhere. Each change here is a one-line addition in its own place.
  - Semantic overlap: `decode_templates` follows the bind order of `decodeEnvironmentWith`, and `decoded_actIn` follows
    `decodeNormsEnvironment` (lean/VE/SpeechActs/, lean/VE/Norms/). A change there by ci-3, which runs beside this item,
    breaks these proofs at merge. Recheck after each sync with main.
- Pilot bytes moved: 0 (proofs only).

## Tests

- Selected tests: `MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base <merge-base> --run` on 956e5168f selected
  452 units. 450 passed and 2 failed: the two classification tests above, which commit ec76949a9 fixes.
- Rerun of the two failed ids (`mac-pytest.sh -- <ids>`) on ec76949a9: 2 passed, exit 0.
- `python3 lean/audit.py`: PASS (798 source files, 8859 theorem declarations, standard axioms only).
- `uv run python tools/gate_collection.py --check --prebuilt`: 0 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- Not in main-known-red: none of the failures.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relayed route or response field changes; the item is proofs only.
2. Every deliverable built: PASS. The plan-row table above gives a commit per row, and the DRI decisions cover the cut
   question. The rule-break grep found no Python copy, no new report test and no authority switch. Overlap is listed.
3. Tests can fail: PASS. Seeds S1-S9 (mutants.json). The trust-mutants sweep exits 0 (trust-mutants.json); `splitOnL`'s
   mutant S3 is killed by the `#guard`s at SplitOnLemmas.lean:303-304.
4. Python, Lean and Rust agree: N.A. No product behaviour changes; `readStep` has no caller.
5. R8 binding: N.A. No relayed field.
6. Gate evidence: the chain runs the gate on the final HEAD. The selected run and the rerun are listed above with
   their commits.
7. No unsigned item: PASS. The only signatures are `hb` (DRI ci-3a-wording item 1) and R16 for `splitOnL` (DRI ci-3b
   item 2). There are no DELTA rows.
8. Every user-visible change in DELTA: N.A. There is none; no route calls `readStep`.
9. Test selection: PASS. `tools/select_tests.py --base` selects 452 of 560 units, because lean/VE.lean and the
   generated inventories changed. The two classification tests it selected failed as they should, and pass after
   ec76949a9.
10. Lean statements say what is claimed: PASS. The statement comparison is above. `hb` has its mechanised
    counterexample (StepsProofs.lean:670-674). Seeds S5-S7 break the proofs.
11. Budgets fail closed: N.A. No evaluator or limit is added. `preposed_eq` keeps `readStep`'s byte charge (`hb`).
12. No CPU or memory regression: N.A. No runtime code changes.
13. Test-removed trailers: PASS. `gate_collection.py --check --prebuilt` reports 0 removed and 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS. `splitOn_two` is guarded both ways (:300), `hb` is shown
    needed and sufficient, and the spec re-read lines are above.
15. The four classes:
    - no overclaim: PASS. The `hs` answer states what is not proved, and the `{0} then{1}` trace is marked as not
      mechanised.
    - no silent cut: PASS. The DRI was asked before any cut and ruled no cut (ci-3b decisions).
    - every new check can fail: PASS. S1-S3 and S5-S7 each break a named `#guard` or proof.
    - limits charged before work: N.A. No evaluator.

SELF-REVIEW: 1 A, 4 B, 6 C (first pass); 2 A, 2 B, 7 C (second pass); fixed 16. The open C is splitting the `E_web`
fixtures out of the proof module (StepsProofs imports StepsExamples), left for a later item.
