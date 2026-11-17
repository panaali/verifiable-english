# kb-9: the keyed selection answer in one kernel row

**Summary.** Status: built; no DRI signature reserved (DELTA rows cite R8, R2, R16, R12). HEAD: see `git log -1`
on this branch (the chain gates it). `soft-selected` takes an optional `facts` member and answers `facts` and
`coherent` beside the selected rules, from the same model (`soft_wire_selected_facts`, `selected_model_admissible`).
anthropic-rsp and openai-preparedness assert that flag instead of per-formula `metered` calls (shadow: 0 mismatches
in 1,470 premise evaluations; `results.json` byte-identical). Open: safety-framework's premise check is not switched
(it has no `check_premises`, see Notes 2); one note for the DRI on `SelectedAnswer` (Notes 1).

Review fixes (kb-9-review.final.md, row `kb-9-text-1`): F1 and F2 correct records only; see section 11.

SIZE: 481 product, 369 tests, about 650 other hand-written lines (`git diff --numstat` against the merge base;
generated inventories, schemas, evidence JSON and the code map excluded). No deliverable was cut.

## 1. Theorems (`lean/VE/SoftNorms/SelectedSound.lean`), verbatim

(a)

```lean
theorem soft_wire_selected_facts (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "soft-selected") (hn : usesSoftPath j = true) :
    ∃ (id : String) (environment : Json) (src : SoftSource) (M : VE.FiniteModel VE.Bridge.Entity)
      (hM : M.Valid (envAt (soften src.D) 0)) (raws : Array Json) (qs : List SelectedQuery)
      (P : List VE.Formula) (items : List Json),
      VE.Bridge.stringField j "id" = .ok id ∧
      j.getObjVal? "environment" = .ok environment ∧
      decodeSoftSource environment (j.getObjValD "norms") = .ok src ∧
      decodeModel src j = .ok ⟨M, hM⟩ ∧
      j.getObjValD "queries" = Json.arr raws ∧ raws.toList ≠ [] ∧
      qs.length = raws.size ∧ (∀ x ∈ raws.toList.zip qs, QueryDecoded src.D M x.1 x.2) ∧
      SelectedAnswer id src.D M qs answer ∧
      VE.Compose.SlotWire.decodeFacts src j = .ok (P, items) ∧
      (∀ φ ∈ P, φ.WellFormed (envAt (soften src.D) 0) []) ∧
      SelectedAnswerWith id src.D M qs (factsFields (factsSent j) (factsAt P M) (coherentAt src.D M)) answer ∧
      (factsSent j = true ↔ ∃ v, j.getObjVal? "facts" = .ok v) ∧
      (factsSent j = true → ∃ b, answer.getObjVal? "facts" = .ok (.bool b) ∧
        (b = true ↔ ∀ φ ∈ P, φ.denote M.asStructure [])) ∧
      (factsSent j = false → (∃ e, answer.getObjVal? "facts" = .error e) ∧
        ∃ e, answer.getObjVal? "coherent" = .error e)
```

The first nine conjuncts are `soft_wire_selected`'s conclusion, whose statement is unchanged (`lean/statements.txt`:
`uv run python tools/lean_statements.py` listed it neither as changed nor removed). `SelectedAnswerWith` is the whole
answer, field by field; `selectedAnswer_flags` reads `facts` and `coherent` out of it.

(b)

```lean
theorem selected_model_admissible (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "soft-selected") (hn : usesSoftPath j = true)
    (hb : answer.getObjVal? "background" = .ok (.bool true))
    (hc : answer.getObjVal? "coherent" = .ok (.bool true))
    (hf : answer.getObjVal? "facts" = .ok (.bool true)) :
    ∃ (environment : Json) (src : SoftSource) (M : VE.FiniteModel VE.Bridge.Entity)
      (hM : M.Valid (envAt (soften src.D) 0)) (P : List VE.Formula) (items : List Json),
      j.getObjVal? "environment" = .ok environment ∧
      decodeSoftSource environment (j.getObjValD "norms") = .ok src ∧
      decodeModel src j = .ok ⟨M, hM⟩ ∧
      VE.Compose.SlotWire.decodeFacts src j = .ok (P, items) ∧
      VE.Compose.BaseAdmissibleP src.D P M.asStructure
```

Its step, `model_admissible_of_flags` (the flags as functions: `classificationBackgroundValid`, `coherentAt`,
`factsAt` all true give `BaseAdmissibleP`), is the task's proof route: `background` and `coherent` together are
`backgroundValid'` (`softPremises = excPremises ++ cohPremises`), then `VE.Compose.baseAdmissibleP_of_valid`, the
lemma kb-3a's `factsModel` check uses (no new bridge).

The flag's converse:

```lean
theorem coherentAt_iff (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity) :
    coherentAt D M = true ↔ ∀ a ∈ cohPremises D, a.denote M.asStructure [] := by
```

(c) Non-vacuity, `lean/VE/SoftNorms/SelectedExamples.lean` (kb-9 sections): kb-10a's three-rule document with one
true and one false fact: `facts: false`, the selected rules as without facts; the true fact alone: `facts`,
`background`, `coherent` all true (the hypotheses of (b) are met); two colliding unranked defaults selected at one
tuple: `coherent: false`, both rules reported.

Built: `cd lean && lake build` (1461 jobs, exit 0, /tmp log); `python3 lean/audit.py`: `PASS: 889 source files; 10084
named theorem declarations audited`. Registry: both theorems under `softNorms` in `tools/kernel-paths.json`.

## 2. What changed

- Lean (`Selected.lean`, `SelectedSound.lean`, `Prepared.lean`; `SlotWire.lean` split only): `runSelected` decodes
  `facts` with `decodeFacts` right after the source (the slot kinds' order) and appends `factsFields (factsSent j)
  (factsAt P M) (coherentAt src.D M)`. The prepared runner does the same from the prepared document, which now also
  holds the base vocabulary (`baseEnv`) and the coherence conjuncts (`coherence = cohPremisesIn …`,
  `cohPremisesIn_eq`), so a prepared case recomputes neither `soften` nor the layer order. `decodeFacts src j` is now
  `decodeFactsIn (envAt (soften src.D) 0) src.D j`, the same body: the slot kinds are unchanged (their statements in
  `lean/statements.txt` are unchanged; `tests/test_slot_premises.py`: 35 passed).
- Schema: `soft-norms.json#/$defs/selected` requires `facts` and `coherent` exactly when the request has `facts`
  (`selected_fits`, `runSelected_fits`; `lean/ResponseShape/SoftSelectedExamples.lean` kb-9 section).
- Python: `ve.softnorms.facts_wire` (the one encoder of a case's facts; kb-3a's slot cases use it too),
  `selected_at(..., facts=)`, `bind_selected` (flags present exactly when facts were sent, bools),
  `SoftenedNormDocument.selected_rules/outcome_at(..., facts=)` keyed by document, model and the facts' encoded bytes,
  and `selection_flags(model, facts=)`. `ve.soft_route.selected_at(..., facts=)`.
- Harnesses: `check_premises` of anthropic-rsp and openai-preparedness (section 4).

## 3. Shadow (`usecases/kb9_facts_shadow.py`; docs/usecases/safetyfw/<case>/kb9-shadow.json, at cd8b3018fc)

| Harness | Premise check | Evaluations | Lean facts cases | Mismatches | Both false | Keyed pairs | `coherent: false` | `background: false` | Harness |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| anthropic-rsp | `check_premises` | 330 | 129 | 0 | 0 | 1,326 | 0 | 0 | exit 0 |
| openai-preparedness | `check_premises` | 923 | 495 | 0 | 24 | 11,526 | 0 | 0 | exit 0 |
| safety-framework | `premise_status` | 217 | 217 | 0 | 0 | 672 | 0 | 0 | exit 0 |

The 24 "both false" are Preparedness cases whose premise check fails on purpose (the harness catches it); both sides
say false. The lists of keyed pairs with `coherent: false` or `background: false` are empty in all three harnesses:
every keyed (document, model) pair is a model of the soft background and of every coherence conjunct.

Zero mismatches, so the switch was made (commit 757a97a0ae): `check_premises` asks the flag from the `soft-selected`
case that also answers the checked document's selected rules (the same facts tuple goes to `selected_rules` and
`outcome_at`), keeps today's AssertionError text (`... does not satisfy premise <block>: Violated`; the block is the
first whose own flag is false), and makes no `evaluate` call
(`tests/test_kb9_selected_facts.py::test_a_harness_premise_check_reads_the_flag_of_the_selection_case`). The harness
does not assert `coherent`.

## 4. Calls and wall time (`tools/kernel_trace.py <out> usecases/<h>/run.py --check`; docs/kernel/kb-9/before, after)

Same machine (the VM), the same day: before 15:05-15:37 UTC at load 14-16 (at 950d99ce1b's code, pre-switch),
after 16:18-16:47 UTC at load 6-8 (757a97a0ae). Every run exited 0, so each `results.json` is byte-identical.

| Harness | `metered` before → after | `check` | `soft-selected` | all Lean cases | `--check` wall s |
|---|---|---|---|---|---|
| anthropic-rsp | 4,852 → 2,311 | 13,727 → 13,711 | 458 → 458 | 21,584 → 19,027 | 205.4 → 190.9 |
| openai-preparedness | 16,392 → 36 | 57,879 → 57,825 | 6,376 → 6,433 | 98,453 → 82,092 | 1,521.6 → 1,325.0 |
| safety-framework | 10,209 → 10,209 | 8,764 → 8,764 | 672 → 672 | 22,710 → 22,710 | 123.5 → 159.5 |

safety-framework's code is unchanged and its calls are identical; its wall-time difference is the VM's load, so the
wall times show direction only. Preparedness's 57 more `soft-selected` cases are, by the code, the per-block flags a
failing premise check asks to name its block (24 checks fail in the shadow); I did not count them separately.

Ownership trace (`docs/kernel/kb-9/measure_item.py`, which runs `manage-agents/reviews/lean-ownership-20261112/
trace_item.py`, since kb-10d's `tools/ownership_trace.py` is not on main): items A-T0/PROT1 and B-PUB/INSCOPE (the
first A and B items; the key has no A1 or B1), K1, G1, N1; every one agrees with the key before and after.

| Item | from `check_premises` before | after | `soft-selected` cases on the item, before → after |
|---|---|---|---|
| A-T0/PROT1, B-PUB/INSCOPE, K1, N1 | `metered` 8, `check` 8, `environment` 1 | `soft-selected` 1 (the selection case itself), `environment` 1 (the model's validation) | 6 → 6, 2 → 2, 2 → 2, 2 → 2 |
| G1 | none (G1 does not check premises) | none | 1 → 1 |

So on each item's path the one Lean case kind is `soft-selected`, and `check_premises` sends no `metered` case.

## 5. Kernel

`docs/kernel/closure-baseline.json` (`regen_generated.py --write --only kernel-closure`): kernel 10,083 → 10,108
(+25, inside the signed +60); softNorms spec 4,684 → 4,709 (`SoftNorms.Selected` 15 → 29, `SoftNorms.SelectedSound`
15 → 21, `Compose.SlotWire` 58 → 61, `SoftNorms.Prepared` 8 → 10), theorems 17 → 19; row added to
docs/kernel/ALLOWANCES.md with the signed text. Trusted Lean (tools/trust_map.py --check, PASS): K +0, S +25, V +17
(DELTA row 3, R16). Trust mutants: section 9.

## 6. Values from one Lean answer sent in a later Lean case (remaining)

| Function | file:line | What is carried |
|---|---|---|
| `query` | usecases/anthropic-rsp/run.py:244-260 | the deny document's premise verdict (its `soft-selected` case) stands for the allow document's selections and outcomes (`selected(allow, …)` :253, `completed(allow, …)` :260), asked in a second case on the same model object |
| `lead_without_competitors` | usecases/anthropic-rsp/run.py:660-674 | the same, for N3's allow document (:674) |
| `t_countermodel` | usecases/anthropic-rsp/run.py:462-491 | one model through 1 + n `metered` cases: each premise, then the goal (:490) |
| T family `prove_entailment` then `check_entailment_certificate` | usecases/anthropic-rsp/run.py:454-456; openai-preparedness/run.py:704-707 | the certificate `prove_entailment` already had Lean replay (ve/entailment.py:594) is replayed again in a second `route` case |
| `indicator_silence` (G7) | usecases/openai-preparedness/run.py:532-551 | the premise flag (`soft-selected`) and the goal's value (`metered`, :551) on the same model, in two cases |
| conflict witness after `check_premises` | usecases/openai-preparedness/run.py:619-620 | the premise flag (`soft-selected`) and the `soft-conflict` witness verdict on the same model, in two cases |
| `premise_status` | usecases/safety-framework/run.py:253-262 | per-premise `metered` cases on the plain base model (:259), then a prover certificate replay (:262); the "model" verdict gates cases on other documents' case models (:641 `decide_soft_conflict`, :765 selections, :856 item cases) |
| `_core_problem` / `prove_quantity` | ve/units.py:380-415 | each premise's `core` and meaning id from Lean `check` answers, sent in the `quantity` certificate case |
| `decide_soft_conflict(prove=True)` | ve/soft_route.py:135-173 | certificates searched over the document hydrated from Lean's `soft-elaborate` answer (`soft_document.elaborated`), sent as `soft-conflict` packages (Lean rebinds them to the background it regenerates) |

## 7. Seeded bugs (docs/kernel/kb-9/seeded-bugs.json; each restored)

| Id | Language, file | Bug | Caught by |
|---|---|---|---|
| a | Lean, lean/VE/SoftNorms/Selected.lean | the runner reports `facts: true` unconditionally | build: SelectedSound.lean:128 (`runSelected_answer`, the step of (2a)) |
| b | Lean, lean/VE/SoftNorms/Selected.lean | the facts evaluated in a model decoded again over the source predicates' vocabulary | build: SelectedSound.lean:136 |
| c | Python, ve/softnorms.py | the last fact dropped before sending | `test_the_last_fact_is_sent_and_read` (and 9 more) |
| d | Python, ve/softnorms.py | `bind_selected` accepts an answer without `facts` when facts were sent | `test_a_forged_flag_is_unavailable[facts dropped]` (and 3 more) |
| e | Python, usecases/anthropic-rsp/run.py | the switched check ignores a false flag | `test_a_harness_premise_check_reads_the_flag_of_the_selection_case[anthropic-rsp]` |
| f | Python, ve/softnorms.py | a non-list `facts` reaches the encoder (TypeError) | `test_a_malformed_facts_value_or_item_is_refused_with_a_diagnostic[7]` (and 7 more) |

## 8. Notes for the DRI

1. `soft_wire_selected` keeps its statement text, as the task asks, so its spec `SelectedAnswer` had to admit the
   two new fields: it now reads "exactly `SelectedAnswerWith` `factsFields sent facts (coherentAt D M)` for some
   `sent` and `facts`". So it is weaker for every case: it no longer rules out the two flag fields, even for a case
   that sent no `facts`, and where they appear it does not pin `facts` (only `coherent = coherentAt`). Only
   `soft_wire_selected_facts` pins them: both absent for a case without `facts`, both present with `facts = factsAt`
   for a case with them (review kb-9 F2). The task's two requirements (the statement unchanged; the facts
   fields on the same kind) admit no other reading. `soft_wire_selected_prepared` likewise keeps its text.
2. safety-framework is shadowed, not switched. It has no `check_premises`: `premise_status(atoms, item)` is a
   situation-level gate on the plain base model with no document, whose `failed` list and refutation are part of
   `results.json`. Switching it means making it per document; doing that with one document's flag for all would
   carry the flag from one document's case into another's, which section 8.1 forbids. Conservative choice: shadow
   only (0 mismatches in 217); listed in section 6.
3. The safety-framework shadow first failed `--check`: `case_model` keeps models by `(E′, atoms)`, not by the
   document's rules, so the shadow's own base-document lookup left an entry that a later document with the same E′
   read. The shadow now removes the entries its lookup adds. In the harness itself two documents with one E′ but
   different exception conditions would share that model; I did not find such a pair in the scored run (its
   `--check` passes) and did not test the mutant variants for it.
4. The before and after runs were 70 minutes apart at different loads (section 4); Preparedness `--check` takes
   1,524 s here against the frozen keys' 198.8 s with `--base-only`.

## 9. Tests and checks run

- Lean: `lake build` (full, twice: after the Lean change and after (b) on the wire; the `ve_service` binary is the
  same pinned build, sha256 a4f52ad0dd43f709…), exit 0; `python3 lean/audit.py` PASS; `tools/check_*_statements.py`
  (8 tools) exit 0.
- Trust mutants (`mac-pytest.sh --trustmut -- --max-mutants 1000 --test lean/VE/SoftNorms/SelectedExamples.lean
  --test lean/ResponseShape/SoftSelectedExamples.lean --allow docs/kernel/kb-9/trust-mutants-allow.json`): run 1
  (docs/kernel/kb-9/trust-mutants-run1.json) left 49 survivors; the `factsAt`, `coherentAt`, `cohPremisesIn` and
  `decodeFactsIn` ones are killed by new `#guard`s (a false fact first; two colliding pairs failing first only, last
  only, neither; the prepared runner equal to the runner; a decision predicate at either position and the last
  decision name), the `SelectedAnswer`/`SelectedAnswerWith` ones (Prop definitions over Json, no decidable equality)
  and two that do not elaborate are allowed with a reason each (kb-10a's precedent). Run on 1d2df69240: 81 KILLED,
  0 SURVIVOR, 0 UNKNOWN, 5 INVALID, 32 ALLOWED, exit 0. Final run, full (no --rescore), on 5bab46a913 after the
  review fixes changed `SelectedSound.lean`'s docstrings and added two examples (docs/kernel/kb-9/trust-mutants.json):
  81 KILLED, 0 SURVIVOR, 0 UNKNOWN, 5 INVALID, 32 ALLOWED, exit 0.
- `uv run python tools/regen_generated.py --write`, then `--check`: 41 entries, exit 0. The `lean_decoders` pins of
  `ve/assurance-manifest.json` for Selected.lean, Prepared.lean and SlotWire.lean were reviewed and repinned by hand
  (`decodeFactsIn` added to SlotWire's declarations); `tests/test_assurance_manifest.py` 167 passed.
- `uv run pytest -q tests/test_kb9_selected_facts.py` 53 passed; `tests/test_soft_selected.py tests/test_slot_premises.py`
  205 passed; `tests/test_relay_binding_inventory.py -k "soft-selected or classified"` 21 passed.
- `uv run python tools/gate_collection.py --check --prebuilt`: 53 added, 0 refused, 0 stale, 0 malformed.
- `tools/select_tests.py --base $(git merge-base HEAD main)`: 508 of 628 test files, including every test file above.
- Selected run (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, on
  3e6e411262, ve-cloud-2): 325 units, 1 failed: `tests/test_kb10b_switch.py` (its fakes of `selected_at` and
  `outcome_at` take no `facts`). Fixed at 08dad12cf6 (the relay and RSP pass `facts` only when facts are sent; kb-10b's
  `completed` fake models the document's reading); rerun of that unit and the tests of the touched code
  (`mac-pytest.sh -- tests/test_kb10b_switch.py tests/test_kb9_selected_facts.py tests/test_rsp_fidelity_fix.py
  tests/test_kb10_shadow.py tests/test_safetyfw_usecases.py tests/test_soft_selected.py`): 412 passed.
- On the final code (08dad12cf6): `usecases/anthropic-rsp/run.py --check` exit 0 (193 s) and
  `usecases/openai-preparedness/run.py --check` exit 0 (1,096 s).
- `tests/test_kb10b_switch.py::test_a_harness_loads_its_own_siblings_and_leaves_none_behind` fails when run alone,
  on this branch's code as on its own (Preparedness's `run.py` loads RSP's at import, whose siblings the test
  replaces); in its file it passes after `test_the_harnesses_completed_is_outcome_at` has loaded RSP. Not touched.
- Not run: the agent-policy and eligibility harnesses (their code paths are unchanged; the gate runs their tests).

## 10. Spec re-read

- `facts` decoded by `decodeFacts src j`, closed and well-formed over `envAt (soften src.D) 0`, the slot kinds' limits
  and refusals, absent means `P = []`: against the task's deliverable (1); `runSelected` (Selected.lean) and
  `decodeFacts_ok` (SlotWire.lean:85).
- `"facts": b` with `b = P.all (fun φ => φ.eval M [])` and `"coherent": c` with `c = (cohPremises src.D).all …`,
  present exactly when the member was sent, a false value reported: `factsAt`, `coherentAt`, `factsFields`,
  `factsSent` (Selected.lean); `selectedAnswer_flags`; the schema's `ite` on `facts`.
- (2a) `soft_wire_selected`'s conclusion, `decodeFacts src j = .ok P` (here `.ok (P, items)`: kb-3a's decoder returns
  the pair, as the task notes), well-formedness, `facts` read from the answer with `b = true ↔ ∀ φ ∈ P, φ.denote
  M.asStructure []`: section 1 (a).
- (2b) under (2a)'s hypotheses and the three flags true, `BaseAdmissibleP src.D P M.asStructure`, by the named route;
  the converse for `coherent`: section 1 (b), `coherentAt_iff`.
- (2c) kb-10a's three-rule document, one true and one false fact, `facts` false, rules reported: SelectedExamples.lean.
- (3) both theorems under softNorms; baseline regenerated; +25 within +60; allowance text verbatim in ALLOWANCES.md.
- (4) `selected_at(..., facts=None)` with kb-3a's encoder (`facts_wire`, used by `_slot_case` too); `bind_selected`
  requires both flags exactly when facts were sent, bools; `selected_rules`/`outcome_at` take `facts=`, kept answers
  keyed by document, model and the facts' encoded bytes; the flags exposed (`selection_flags`).
- (5) shadow first, saved per case; zero mismatches, then the switch with the same AssertionError text and no
  per-formula `evaluate`; `coherent` not asserted; pairs with `coherent: false` or `background: false` listed (none).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: PASS. `tests/test_kb9_selected_facts.py::test_a_forged_flag_is_unavailable`
   (each flag dropped, added, set to 7, null, [], {}, 1.5, "\ud800", 10k-deep, 1, 0, "true"),
   `::test_a_malformed_facts_value_or_item_is_refused_with_a_diagnostic` (request side), `SoftSelectedExamples` variants.
2. Every deliverable built: PASS. Section 10 maps each numbered deliverable; FSF's switch is not made for the reason in
   Notes 2 (no `check_premises`); no Python copy of a Lean decision (the harness reads Lean's flag).
3. Tests can fail: PASS. Seeded bugs a-f (section 7); trust mutants 0 SURVIVOR, 0 UNKNOWN.
4. Python, Lean and Rust agree; valid inputs still pass: PASS. Three harnesses' `--check` before and after
   (byte-identical `results.json`), `test_a_case_without_facts_is_answered_as_before`; no Rust change.
5. R8 binding: PASS. Flags present exactly when sent (`test_a_forged_flag_is_unavailable`: added when none sent,
   dropped when sent, also beside empty facts); every fact sent (`test_the_genuine_answer_with_facts_is_bound_and_every_fact_is_sent`).
6. Gate evidence matches the final HEAD: PASS for what I ran (section 9); the chain runs the gate on the final HEAD.
7. No unsigned item: PASS. DELTA rows cite R8, R2, R16, R12; trusted growth under R16 with the FOLLOW-UPS row.
8. Every user-visible change in DELTA: PASS. DELTA rows 1-2 (new fields, new refusals and their order).
9. Test selection finds the tests: PASS. `tools/select_tests.py` selects tests/test_kb9_selected_facts.py,
   test_soft_selected.py, test_slot_premises.py, test_kb10b_switch.py (the unit the selected run caught).
10. Statements say what is claimed: PASS. Seeded bugs a and b break the build of (2a)'s proof; check_*_statements exit 0;
    no hypothesis added to an approved statement (`soft_wire_selected` unchanged; Notes 1 on `SelectedAnswer`).
11. Budgets fail closed: N.A. (the flags are total evaluations of decoded formulas; the facts decoder keeps the slot
    kinds' limits; no budget is added).
12. No CPU regression: PASS. Lean cases fall (section 4); prepared documents keep the coherence conjuncts and base
    vocabulary (no `soften` per case); the facts key is computed once per held tuple.
13. Test-removed trailers: PASS. `tools/gate_collection.py --check --prebuilt`: 53 added, 0 removed, 0 refused, 0 stale, 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS. True and false facts, present and absent flags, accepted and
    refused facts (tests above); section 10.
15. No overclaim, no silent cut, every check can fail, limits before work: PASS. The universal words in this report
    cite their command (sections 3, 4, 9); no cut; every new `#guard` is a trust-mutant killer (run 2/3 counts); the
    facts list is decoded by kb-3a's decoder under its limits.

## 11. Review fixes (text only: row `kb-9-text-1`)

| Finding | Fix | Regression test | Commit |
|---|---|---|---|
| F1 (B): the spec and frozen keys kept 10,083, 16,545 and four stale path rows after the baseline moved | figures from `closure-baseline.json`; the records check lists every stale figure at once and also checks the section 1 keyed total and the measurement table's keyed row | `tests/test_kernel_closure.py::test_the_records_quote_the_saved_measurement` (the probe), `::test_the_records_check_lists_every_stale_figure_at_once` | 5bab46a913 |
| F2 (A): three records said `soft_wire_selected` still rules out the flag fields for a case without `facts` | spec paragraph, note 8.1 and both `SelectedSound.lean` docstrings say the tail is open for every case and only `soft_wire_selected_facts` ties it to the case; two Lean examples check the open tail; `soft-norms.md`'s `soft-selected` row names `facts` and the flags | `tests/test_kb9_selected_facts.py::test_the_records_say_what_soft_wire_selected_states_since_facts`; the examples at the end of `lean/VE/SoftNorms/SelectedExamples.lean` (build) | 5bab46a913 |

No user-visible behaviour changed, so DELTA gains no row. Of the review's unfiled notes, the FOLLOW-UPS row pointer
(now DELTA row 3) and the `soft-norms.md` row are fixed; the others are not addressed here.
