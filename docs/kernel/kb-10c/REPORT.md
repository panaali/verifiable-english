# kb-10c: conflicts of soft-norms documents on Lean's soft route

**DRI signature needed: DELTA row 2.** This is the reason the item stops (L52). Lean CPU per conflict check exceeds
R4 on RSP and Preparedness. Requested 2026-11-15 in `manage-agents/inbox/dri/20261115T050510Z-kb-10c-3111473.md`;
recommended: sign on the 2.0x-per-harness rule of the kb-10b-switch decision (1.07x, 0.97x, 1.04x here).
Status: every deliverable (1)-(5) is built. HEAD: the last commit of `feature/kb-10c`; product code last changed in a2905d1c1.
What changed: three Lean theorems on `soft-conflict`'s answer; a three-harness shadow (0 differences in 2,039 calls);
the harnesses' conflicts are now decided on Lean's soft route; no keyed answer changed.
Open: only the row-2 signature. The full gate is the chain's.

## Deliverables

| Task item | Delivered | Commit | Test or evidence |
|---|---|---|---|
| (1) `soft_wire_conflict_free` | `lean/VE/SoftNorms/ConflictSound.lean` | 801eb8bbf | `lake build` (1,452 jobs, passed); `python3 lean/audit.py` PASS; seeded bug S1 |
| (2) `soft_wire_conflict_witness` | same file | 801eb8bbf | same |
| (3) `soft_wire_conflict_exclusive` | same file | 801eb8bbf | same |
| Registry: on `softNorms`; `soft-conflict` out of `runSoftKind`'s `uncovered`; baseline; ALLOWANCES | `tools/kernel-paths.json`, `docs/kernel/closure-baseline.json`, `docs/kernel/ALLOWANCES.md` (+2, total 11,121) | 801eb8bbf | `tests/test_kernel_closure.py` 37 passed; `python tools/kernel_closure.py --out ...`: signed total 11121 >= kernel 11121 |
| (4) Shadow | `usecases/safetyfw_conflict_shadow.py` (test-only) and its self-test | 26358508f | `tests/test_kb10c_conflict_shadow.py` 5 passed; seeded bugs S2 and S3 |
| (4) Shadow evidence | `docs/usecases/safetyfw/<case>/kb10-conflict-shadow.json` ×3 | 5de708126 | below |
| (5) Harnesses on the soft route | `ve.soft_route.decide_soft_conflict`; the three harnesses call it | 7a184c382, cdd31f6b6 | `tests/test_kb10c_soft_conflict.py` 14 passed; seeded bugs S4-S7 |
| (5) Five keys | RSP, Preparedness and FSF `--check`; agent-policy; eligibility | cbcdad48b | `evidence/wall-times.jsonl` (`rc` 0 on each side), `evidence/keys.txt` |
| Acceptance as kb-10b (3), plus who-owns-what | `docs/usecases/keyed-answers.md` and its re-measured `.json` | cbcdad48b | `tests/test_keyed_answers_authority.py` 12 passed; seeded bug S8 |

### The Lean theorems

The module's case lemma, `soft_conflict_verdict`, reads the answer of `runCase` for kind `soft-conflict`.
- With a `witness` field, the `verdict` is `if w.conflict then "CONFLICT" else "UNKNOWN"` of a successful
  `replaySoftWitness`.
- Without one, it is `if res.conflictFree then "CONFLICT-FREE" else "UNKNOWN"` of a successful
  `replaySoftConflict`.
- Each field is read by key. `ok_verdict` shows that no later field binds `verdict` again.

From the lemma:
1. **`soft_wire_conflict_free`.** Hypotheses: `runCase j = .ok answer`, kind `soft-conflict`, `usesSoftPath j`,
   `(j.getObjVal? "witness").toBool = false` and verdict `CONFLICT-FREE`. Conclusion: `∃ res, replaySoftConflict j =
   .ok res ∧ res.conflictFree = true ∧` `soft_wire_conflict_sound`'s conclusion for the decoded source (decodes to
   `res.src`, `WellFormedSoft`, `SoftConflictFree.{0}`).
2. **`soft_wire_conflict_witness`.** Hypotheses: a `witness` field (`toBool = true`) and verdict `CONFLICT`.
   Conclusion: `∃ src w, replaySoftWitness j = .ok ⟨src, w⟩ ∧ w.conflict = true ∧`
   `soft_wire_conflict_witness_sound`'s conclusion.
3. **`soft_wire_conflict_exclusive`.** Two `soft-conflict` cases with the same `environment` and `norms`: if one
   answer reads `CONFLICT-FREE`, the other does not read `CONFLICT`. This holds whichever case carries the witness,
   in the style of `VE.Norms.FlaggedSpec.norms_wire_conflict_exclusive`.

No existing definition was edited. Trusted lines: +0 (`uv run python tools/trust_map.py --check`: "K +0, S +0, D +0,
G +0, tied +0, unclassified +0, trusted +0"). Trust mutants: 0 definitions, 0 mutants, exit 0
(`docs/kernel/kb-10c/trust-mutants.json`). The light lane printed NOT, because of the new Lean files.

Kernel measure: softNorms path spec 5,368 → 5,370. The two lines are in `VE.SoftNorms.Coherence` (26 → 28), which
the witness theorem's collision and pair-conflict conclusion reads. Distinct kernel lines: 11,119 → 11,121. This is
entered in ALLOWANCES as "kb-10c, pre-signed by the architect seat up to +150 lines". The spec's tables and the
frozen-keys figures are updated (`tests/test_kernel_closure.py::test_the_records_quote_the_saved_measurement`).
`runSoftKind` stays an `uncovered` writer, because it still serves `soft-rule`, `soft-rules`, `soft-elaborate`,
`soft-pairs` and `soft-certificate`. `soft-conflict` moved from `untied_kinds` to the path's `kinds` (theorem
`soft_wire_conflict_free`).

### The shadow (4)

For each `check_conflict(doc.elaborated, …)` call, the soft route was asked the same question with the same
generators' output:
- **Python found a witness:** the `witness` case, with that model, target and tuple.
- **Otherwise:** the `packages` case, with the certificates `_prove_targets` made for that call. These are
  re-bound to the soft source's environment id and document hash, with no packages when the prover found none.

Python's certificates replay unchanged because its W1 check already works over the soft base:
`SoftenedNormDocument.base_environment()` is a `SoftBaseEnvironment`, whose Background holds the soft exception and
coherence premises (`ve/background.py:191`, model check `:95`). Run on 26358508f, each harness with `--check`:

| Harness | Calls (distinct questions) | Status pairs (Python / soft) | Differences | Targets disagree | CONFLICT-FREE questions with a non-empty `conditional_on` | Harness |
|---|---:|---|---:|---:|---:|---|
| Anthropic RSP | 104 (35) | CONFLICT/CONFLICT 2, CONFLICT-FREE/CONFLICT-FREE 102 | 0 | 0 | 0 of 34 | exit 0 |
| OpenAI Preparedness | 472 (101) | CONFLICT 8, CONFLICT-FREE 458, UNKNOWN 6 (each pair equal) | 0 | 0 | 0 of 89 | exit 0 |
| DeepMind FSF | 1,463 (1,276) | CONFLICT 2, CONFLICT-FREE 59, UNKNOWN 1,402 (each pair equal) | 0 | 0 | 0 of 46 | exit 0 |

Every call had a soft source (0 unsourced). Every C item is covered: the scored run, each mutant and each removed
narrowing (`items` in each file).

**The known difference, explained, not hidden.** The soft route's CONFLICT-FREE says "among rules on the same act,
conditional on the open coherence premises" (`conditional_on`); the harness's W1 status states no condition.
- The pairs cannot show this, because the claim behind both is the same: Python's W1 proof reads the same soft
  premises through `SoftBaseEnvironment`.
- On these three harnesses, no CONFLICT-FREE answer needed an open coherence premise. `conditional_on` is empty in
  all 169 CONFLICT-FREE questions.
- The self-test's two-rule document shows the case where the condition is not empty (`soft:coherence:a,b`,
  `tests/test_kb10c_conflict_shadow.py::test_python_and_the_soft_route_agree_and_the_condition_is_counted`).
- `decide_soft_conflict` now carries Lean's status text, condition included, in a CONFLICT-FREE report's `detail`.

### The switch (5)

`ve.soft_route.decide_soft_conflict(soft_document, model=, prove=, max_evaluations=, tableau_steps=)` makes
`check_conflict`'s admission checks, then works as follows:
- **Witness.** It proposes a witness with `_find_conflict`. Lean must confirm it: the verdict must be `CONFLICT` and
  the target the one sent, or the call is CheckerUnavailable. The report is then Python's `_conflict_report`, as on
  the W1 Lean route.
- **Certificates.** It proposes certificates with `_prove_targets` and re-binds them to the soft source. Lean's
  CONFLICT-FREE is returned with Lean's status text. Lean's UNKNOWN is kept only if its `detail` names a target the
  request sent (the targets themselves are bound by `bind_conflict`); anything else is CheckerUnavailable.
- **Exhaustion.** An exhausted search or prover is UNKNOWN without a Lean call.
- **Kept answers.** Lean's answers are kept per request: the key is the canonical JSON of environment, norms, and
  witness or packages.

The three harnesses call it. `ve.norms.check_conflict` is unchanged.

Keys:
- **RSP, Preparedness, FSF.** `--check` exits 0 on the head in every paired round (`evidence/wall-times.jsonl`,
  `"mode": "after"`). Each run compares every result with the committed `results.json`. `git status --short` is
  empty afterwards.
- **agent-policy and eligibility.** They do not import `ve.soft_route`. Both commands exit 0 with no disagreements
  (`evidence/keys.txt`).
- **The route strings.** The strings in `results.json` ("W1 check_conflict …") are kept, because they are
  frozen-key bytes (DELTA.md).

Cost (DELTA row 2): every paired round, its rows and R4's figures are in DELTA.md row 2 and
`evidence/wall-times.jsonl`. The `soft-conflict` kind costs about 1.4 s of Lean CPU per RSP check, measured with
`/tmp` probe `split.py` on RSP C3: `soft-elaborate` 0.016 s, then `soft-conflict` 1.42 to 1.49 s wall and 1.40 to
1.42 s CPU in each of 3 calls. Python cannot remove that.

## Seeded bugs (`seeded-bugs.json`)

- **S1 (Lean)**, `lean/VE/SoftNorms/Run.lean`. Bug: line 425 answers CONFLICT-FREE when `res.conflictFree` is
  false. Result: `lake build VE.SoftNorms.ConflictSound` fails in `soft_conflict_verdict`, which
  `soft_wire_conflict_free` is proved from (a deterministic timeout at lines 49, 67, 78, 81).
- **S2 (Python)**, `usecases/safetyfw_conflict_shadow.py`. Bug: the shadow compares Python with Python. Fails:
  `test_a_planted_difference_is_listed_with_python_and_soft_answers` (and
  `test_pythons_witness_is_sent_and_a_refused_model_is_explained`).
- **S3**, same file. Bug: the question key leaves out the document. Fails:
  `test_each_call_is_paired_with_the_soft_answer_to_its_own_question`.
- **S4**, `ve/soft_route.py`. Bug: Lean's UNKNOWN becomes CONFLICT-FREE. Fails:
  `test_lean_s_unknown_is_kept_when_its_detail_names_a_sent_target`.
- **S5**, same file. Bug: the witness verdict is not checked. Fails:
  `test_a_witness_lean_does_not_confirm_is_checker_unavailable`.
- **S6**, same file. Bug: the kept-answer key leaves out the case. Fails:
  `test_a_repeated_request_is_answered_once_and_a_different_one_is_asked`.
- **S7**, same file. Bug: the UNKNOWN detail's target is not bound. Fails:
  `test_an_unbound_packages_answer_is_checker_unavailable[unsent-target]`.
- **S8**, `usecases/keyed_paths.py`. Bug: `soft-conflict` relays are not counted. Fails:
  `tests/test_keyed_answers_authority.py::test_the_harnesses_conflicts_are_leans_soft_conflict`.

Each was restored after its run (`git status --short` empty).

## Tests and checks run

- `lake build VE.SoftNorms.ConflictSound`, then the full `lake build`: 1,452 jobs, successful.
- `python3 lean/audit.py`: "PASS: 882 source files; 10046 named theorem declarations audited".
- `uv run python tools/regen_generated.py --write`, then `--check`: `layer-ledgers` failed once until
  `tools/layer_policy.py` listed the new module; after that, `check_lean_imports.py` printed "Lean layer graph kept".
- `tests/test_kernel_closure.py` 37 passed; `tests/test_kb10c_conflict_shadow.py` 5 passed;
  `tests/test_kb10c_soft_conflict.py` 14 passed; `tests/test_keyed_answers_authority.py` 12 passed.
- Selected tests (`MAC_PYTEST_NO_DEFER=1 zsh manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`):
  - On cbcdad48b it stopped at `--maxfail 5`. `tests/test_safetyfw_usecases.py::test_rsp_unknown_w1_is_neither_false_nor_a_scored_answer[C1-C5]`
    still patched the harness's `check_conflict`; fixed in edd1e86a5, along with `test_pf_unknown_w1_is_undecided_not_false`.
    After the fix, 12 passed (`-k "rsp_unknown_w1 or pf_unknown_w1"`).
  - On edd1e86a5: 348 units, 3 failed test ids. `tests/test_history_tests.py::test_the_tree_passes` and
    `::test_the_command_line_lint_passes_on_the_tree` failed because the shadow self-test was not listed as history-reading.
    `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified` failed because
    `ConflictSound.lean` was not classified. Both were fixed in a2905d1c1.
  - The three ids plus `tests/test_kb10c_conflict_shadow.py`, rerun with `mac-pytest.sh -- <ids>`: 8 passed.
  - No test of `manage-agents/main-known-red.txt` appeared.
- `uv run python tools/gate_collection.py --check --prebuilt`: "19 added, 0 removed by a trailer, 0 refused, 0 stale
  and 0 malformed trailers".
- **Not run:** the full gate (the chain runs it), and a base-worktree pair. The "before" side is the head with the
  one call swapped back; no shared Lean build of the merge base existed.

SIZE: 286 product, 317 tests, 564 other hand-written lines. Product: `ConflictSound.lean` 168, `ve/soft_route.py`
79, harnesses 14, `keyed_paths.py` 13, registry, layer and root 11. Other: the shadow script 256, `pair.py` 90,
docs and evidence about 214. Generated files are not counted.

## Notes for the DRI

- The task's spec path (`manage-agents/fable-team/architect/kb-10/SPEC.md`) does not exist on this machine. I
  worked from the task text, kb-10b's task, and kb-10b's and kb-10b-switch's reports.
- Conservative choices taken without asking:
  - The harnesses' `route` strings stay as they are (frozen bytes).
  - `check_conflict` itself is not switched. Only the harnesses call the soft route, which is the narrower reading
    of (5).
  - A witness Lean does not confirm is CheckerUnavailable, never Python's CONFLICT.
- An idea for later, not filed as work: Lean CPU per check would fall if the service's prepared soft-document
  handles (kb-10e) also accepted `soft-conflict`. Today they accept only `soft-selected`, and widening them is a Lean
  service change.
- The shadow script wraps the harness's `check_conflict`, which the switch removed. It records the evidence made on
  26358508f and cannot be rerun on a later commit (its docstring says so).
- A non-docs commit (a2905d1c1) followed the last full selected run, so the chain gate cannot reuse that run.
- `ve-mac-1` did not resolve, so trust mutants ran on the VM. The paired rounds ran at VM load 45 to 93; the ratios
  are same-hour pairs.

No FOLLOW-UP: every deliverable is built, and no defect makes a verdict, a binding or a keyed answer wrong.

## Spec re-read

- (1), (2) and (3), hypotheses and conclusions, against the task text ("Deliver, Lean first …"): matched word by
  word. Each hypothesis is listed; "no witness field" is `(j.getObjVal? "witness").toBool = false`, the test
  `runSoftKind` makes.
- Registry: on `softNorms`; `runSoftKind`'s `uncovered` entry loses `soft-conflict`; baseline regenerated; the
  ALLOWANCES text is exactly "kb-10c, pre-signed by the architect seat up to +150 lines". Checked against the task's
  "Registry:" sentence.
- (4): targets are `conflict_targets` of the elaboration (bound by `bind_conflict`); packages are bound to
  `Background_base′` (Lean's `decodeSoftPackage`). Checked against the task's (4) and `lean/VE/SoftNorms/Wire.lean:285-308`.

## Self-review against BUILDER-CHECKLIST

1. **PASS.** Every Lean answer is typed and contained. `decide_soft_conflict` reads `check_soft_conflict`'s rows,
   which pass the soft relay's schema check (`tests/test_relay_binding_inventory.py`, kinds `soft-conflict`, `soft-conflict-witness`).
   Its own reads are fuzzed by `test_an_unbound_packages_answer_is_checker_unavailable` (5 variants: an unsent
   target, free text, an int, an absent detail, CONFLICT on packages) and by the two witness tests.
2. **PASS.** Every deliverable is in the table above. There is no Python copy of a Lean decision: UNKNOWN on an
   exhausted generator asserts nothing, as on the W1 Lean route. No new report test (the authority test was edited,
   not added as a report test).
3. **PASS.** Seeded bugs S1 (Lean) and S2-S8 (Python), each with its failing test.
4. **PASS.** Python and Lean agree in the shadow: 2,039 calls, 0 differences (`kb10-conflict-shadow.json` ×3).
5. **PASS.** R8 binding: an unsent target is refused (`[unsent-target]`), and so is a witness confirmed for another
   target (`test_a_witness_confirmed_for_another_target_is_checker_unavailable`). Targets and labels are bound by
   `bind_conflict`.
6. **N.A.** Gate evidence matches the final HEAD: the chain runs the gate on the final HEAD.
7. **PASS.** DELTA row 2 is reserved, and the first line of this report says so. Row 1 cites R12.
8. **PASS.** Every user-visible change is in DELTA: the keyed outputs are identical (`--check` rc 0), the new API is
   described, and the cost is row 2.
9. **PASS.** Test selection: the selected run includes `tests/test_kb10c_*` and `tests/test_keyed_answers_authority.py` (selected-run log).
10. **PASS.** Lean statements say what is claimed: seeded bug S1 breaks the build, and the theorems read
    `answer.getObjValD "verdict"` of `runCase`'s own output.
11. **PASS.** A zero budget gives UNKNOWN (`test_a_zero_budget_is_unknown_never_a_verdict`). No sleeps or deadlines
    in the new tests.
12. **PASS.** CPU and memory: the measured pairs are in DELTA row 2. The step count (Lean calls per repeated request)
    is pinned by `test_a_repeated_request_is_answered_once_and_a_different_one_is_asked`.
13. **N.A.** No test was removed or renamed.
14. **PASS.** Both directions are tested: kept answers (repeated vs different request), the UNKNOWN binding (kept vs
    refused), the shadow (identical vs planted difference). Each claim above cites its command or file.
15. **PASS.** Universal words ("no keyed answer changed", "every call", "0 differences") are backed by `--check`
    rc 0 and the shadow JSONs. No deliverable was cut. Every new check has a mutant (S2-S8). No new limit.
