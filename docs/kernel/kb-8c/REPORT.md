# kb-8c build report: closed admission statements, `quantity` promoted, shown quantity values from the kernel row

Status: built. Tested HEAD fb612c50b0 (tree b4b047fa7f); this report is one docs-only commit after it. Base: main 4a5d3460d3. No DRI signature needed.
Changed: `quantity_admission_wire_sound` is now two closed theorems, `_plain` and `_valued`. `quantity` is at tier kernel, and `kernel_closure --check` passes with no problem line. The kernel went from 10,023 to 11,119 lines (+1,096, signed up to +1,300). `ve/units.py` `_checked_quantity` now asks the `quantity` mode's admission kind.
Open: the `check` mode's quantity branch is kept because callers remain in tests/ (listed below), so 0 lines were removed. DELTA: none (every answer is unchanged, and the trust map shows +0).

SIZE: 100 product (lean/VE/Time/WireSound.lean 60, tools/kernel-paths.json 33, ve/units.py 5, tools/trust-classes.json 2), 113 tests (tests/test_units_relay_w6a.py 92, tests/test_kernel_closure.py 21), 19 other hand-written lines (docs/spec/kernel-boundary.md 13, frozen-keys 4, ALLOWANCES 2). This report is not counted, and neither are the evidence files: calls.json and seeded-bugs.json were written by scripts from the measurements; recorder.py.txt (114) and open-tail-seed-b.lean.txt (36) are throwaway scripts kept as evidence. Generated files came from one `regen_generated.py --write`.

## Deliverables

| Task line | Commit | Evidence |
|---|---|---|
| (1) two closed statements in WireSound.lean; statements and proofs only | 458bc5a8c0 | `lake build` exit 0 (1,451 jobs); `git diff main...HEAD --stat -- lean/VE/Time/Wire.lean lean/VE/Time/Document.lean` is empty (no executable change); both are proved directly, and the old theorem is deleted, not kept as a lemma (AGENT) |
| (1) registry lists the two; `kinds` table | 458bc5a8c0 | tools/kernel-paths.json; `tests/test_kernel_closure.py::test_every_case_kind_of_a_kernel_runner_has_an_entry_and_every_entry_a_kind` and `::test_each_kind_theorem_fixes_its_kind_and_no_theorem_states_an_untied_kind` pass (AGENT) |
| (2) tier kernel; baseline regenerated; `--check` with no problem line | 458bc5a8c0 | `VE_NATIVE_PREBUILT=1 .venv/bin/python tools/kernel_closure.py --check docs/kernel/closure-baseline.json`: exit 0, "PASS: kernel 11119 <= 11119", "PASS: verdict writers outside the kernel 56 <= 56", 0 lines starting `problem` (AGENT) |
| (2) ALLOWANCES row and "signed total:" | 458bc5a8c0 | docs/kernel/ALLOWANCES.md: +1,096, total 11,119, "signed up to +1,300, decision D11" (AGENT) |
| (2) frozen-keys update as kb-8b's part 1 (b) says | 458bc5a8c0 | docs/kernel/frozen-keys-20261111.md: the quantity row's tier, the kernel total (11,119, "10,023 before kb-8c promoted `quantity`"), and the line "Tier of quantity changed by kb-8c on 2026-11-14"; its date is kept (AGENT) |
| (3) shadow, then switch | 30965b84aa | Shadow: 53,038 calls compared, 0 differences (below; calls.json). Switch: ve/units.py:317-327 (AGENT) |
| (3) delete the `check` branch if no caller remains | not deleted | Callers remain in tests/ (below); the task's "if a caller remains, leave it and list the callers" applies (AGENT) |
| Seeded bugs (a) (b) (c) | 56dd3eb812 | docs/kernel/kb-8c/seeded-bugs.json S1-S3 (and S4-S6) (AGENT) |
| Acceptance: `lake build`, `lean/audit.py` | 458bc5a8c0 | `lake build` exit 0; `python3 lean/audit.py`: "PASS: 881 source files; 10041 named theorem declarations audited ... only the declared standard axiom allowlist". axioms.txt: both new theorems use `[propext, Classical.choice, Quot.sound]`, the same as the old one (AGENT) |
| Acceptance: five keys byte-identical | n/a (a measurement) | below (AGENT) |
| Acceptance: eligibility wall time | n/a | 353.5 s before, 308.2 s after (0.87x; below) (AGENT) |
| Acceptance: selected tests | fb612c50b0 | `MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base 4a5d3460d3 --run` on the clean committed tree: "recorded 181 units for tree b4b047fa7f; ... 0 failed", exit 0, 4,959 s on ve-cloud-2 (AGENT) |

## (1) The two statements, verbatim (lean/VE/Time/WireSound.lean:40-51 and 74-90)

```lean
theorem quantity_admission_wire_sound_plain (j answer : Json) (more : Extension)
    (h : runCase j more = .ok answer)
    (hk : j.getObjVal? "kind" = .ok (.str "admission") ∨ ∃ e, j.getObjVal? "kind" = .error e)
    (hm : ∃ e, j.getObjVal? "model" = .error e) :
    ∃ (id : String) (env : Json) (w : W6Env) (quantity : Json) (a : Admission w),
      stringField j "id" = .ok id ∧
      j.getObjVal? "environment" = .ok env ∧ decodeEnvironment env = .ok w ∧
      j.getObjVal? "quantity" = .ok quantity ∧ decodeQuantity w quantity = .ok a ∧
      answer = ok id [("assurance", .str "lean-admitted"), ("Q", a.Q), ("core", a.core),
        ("meaning_id", .str a.meaningId), ("core_meaning_id", .str a.coreId),
        ("environment_id", .str w.environmentId), ("target_environment_id", .str w.targetId)] ∧
      Admitted w.vocab.env [] a.formula ∧ a.formula.erase.WellFormed w.vocab.env.erase []

theorem quantity_admission_wire_sound_valued (j answer model : Json) (more : Extension)
    (h : runCase j more = .ok answer)
    (hk : j.getObjVal? "kind" = .ok (.str "admission") ∨ ∃ e, j.getObjVal? "kind" = .error e)
    (hm : j.getObjVal? "model" = .ok model) :
    ∃ (id : String) (env : Json) (w : W6Env) (quantity : Json) (a : Admission w)
      (d : VE.Order.ModelData VE.Order.Wire.Entity) (b : Bool) (work : Nat),
      stringField j "id" = .ok id ∧
      j.getObjVal? "environment" = .ok env ∧ decodeEnvironment env = .ok w ∧
      j.getObjVal? "quantity" = .ok quantity ∧ decodeQuantity w quantity = .ok a ∧
      VE.Route.Decode.decodeOrderModel w.vocab.core model = .ok d ∧
      answer = ok id [("assurance", .str "lean-admitted"), ("Q", a.Q), ("core", a.core),
        ("meaning_id", .str a.meaningId), ("core_meaning_id", .str a.coreId),
        ("environment_id", .str w.environmentId), ("target_environment_id", .str w.targetId),
        ("value", .bool b), ("evaluations", toJson work)] ∧
      Admitted w.vocab.env [] a.formula ∧ a.formula.erase.WellFormed w.vocab.env.erase [] ∧
      b = a.formula.erase.eval d.toModel []
```

The existentials are entities (`id`, `env`, `w`, `quantity`, `a`, `d`), a `Bool` and a `Nat`. None ranges over a field list. The Lean half of `kernel_closure` (`hasOpenFields`) reports nothing: the `--check` output has no problem line.

How the two differ from the old statement: the hypotheses about the model (`∃ e, … = .error e`, or `= .ok model`) were disjuncts of the old conclusion and are now hypotheses. Each conclusion is that disjunct's half, with `value` substituted (`[]`, or `[("value", .bool b), ("evaluations", toJson work)]`). Every conjunct of the old statement appears in one of the two, and together they cover the same cases: a JSON object either has a `model` member or does not.

Registry (tools/kernel-paths.json, path quantity):
- tier is `kernel`; the theorems are `_plain`, `_valued` and the four others, unchanged.
- `kinds` follows kb-8b's draft. `admission` maps to `_valued`: the tool takes one theorem per kind, and route's `evaluate` likewise names `route_fol_evaluate` while its other families' theorems are listed on the path. `countermodel`, `certificate` and `document` map to their theorems. `count`, `day`, `civil`, `lower` and `render` are `nonverdict`.

Tests changed to read the promoted path (tests/test_kernel_closure.py):
- `KIND_SOURCES` gains `quantity`. `runCase` dispatches with `match kind with` arms and a `[...].contains kind` list, not `kind == "<k>"`, so a reader for that one runner was added (`KIND_MATCHES`). The test pins the nine kinds.
- `statement_states`, review kb-0 F1's probe, now also accepts `Admitted` as "says what an answer means". `VE.Time.Document.extension`'s theorem (`extension_document_sound`) states its whole answer and its admission relations (`NodeAdmitted`, `LeafAdmitted`), but none of the probe's four words. The Lean half (`stated` in the baseline) already counted it.
- The probe's guard against the case it was written for is unchanged: no statement about `VE.CertificateWire.runCase` matches.

## (2) Kernel figures, before and after

| | before (main 4a5d3460d3, closure-baseline.json) | after (this branch) |
|---|---:|---:|
| kernel lines (distinct, tier kernel) | 10,023 | 11,119 |
| quantity path: tier, theorems, spec, wrap, lines | candidate, 5, 2,267, 75, 2,274 | kernel, 6, 2,267, 75, 2,274 |
| lines under the frozen keys' answers | 16,777 | 16,777 |
| of them in the kernel | 10,023 | 11,119 |
| verdict writers, outside the kernel | 59, 56 in 28 modules | 59, 56 in 28 modules |
| problem lines | 0 | 0 |

Source: `VE_NATIVE_PREBUILT=1 .venv/bin/python tools/kernel_closure.py` (then `--check`) on this branch; docs/kernel/closure-baseline.json at both commits.

- The rise is +1,096. kb-8b measured +1,121 on 9,552. The difference comes from what merged since (kb-3, kb-validators' +68, kb-10e), whose lines the quantity path partly shares.
- The rise is below the signed +1,300.
- `tools/trust_map.py --check`: "against 07a963f74da1: K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0 ... PASS", after the `tied` list of `VE.Time.Wire.runCase` in tools/trust-classes.json was renamed to the two new theorems. Before that rename, the check refused "tying theorem VE.Time.Wire.quantity_admission_wire_sound is not in statements.txt".
- docs/spec/kernel-boundary.md has the new figures and table row: "five paths", 11,119, and the quantity row moved to the kernel group. `tests/test_kernel_closure.py::test_the_records_quote_the_saved_measurement` checks them. Section 8.4 is the architect's verbatim text and is unchanged.

## (3) Shadow, switch, and the `check` branch

**Shadow.** A throwaway `sitecustomize` (docs/kernel/kb-8c/recorder.py.txt) wrapped `ve.units._checked_quantity` on main's Python. Beside every call it asked the `quantity` mode's admission kind (no `kind`, no `model`) for the same environment and payload, and compared `environment_id`, `Q`, `core` and `meaning_id`. The five keys ran once each, in parallel, under `manage-agents/iso.sh … 16G`.

| Key | `_checked_quantity` calls compared | differ | rejected by both, same text |
|---|---:|---:|---:|
| eligibility | 52,828 | 0 | 1 (`VEError: DateRange(1960-06-27)`, probe P1) |
| Anthropic RSP | 145 | 0 | 0 |
| OpenAI Preparedness | 45 | 0 | 0 |
| DeepMind FSF | 20 | 0 | 0 |
| agent policy | 0 | 0 | 0 |

There was no disagreement, so nothing went to the architect seat. Raw figures: docs/kernel/kb-8c/calls.json.

**Switch.** `_checked_quantity` (ve/units.py:317-327) sends `decide("quantity", [{"id": "quantity", "environment": …, "quantity": payload}])`. It keeps the `environment_id` binding, and the rest of the function is unchanged. `elaborate_quantity`, `core_formula`, `quantity_meaning_id` and `_core_problem` read `Q`, `core` and `meaning_id` from that row.

**Call counts by mode, per key** (the same recorder; calls.json; "before" is main's Python, "after" is 30965b84aa):

| Key | `check`, quantity branch: before / after | `check`, typing: before / after | `quantity` admission: before / after | `quantity`, other kinds (unchanged) |
|---|---:|---:|---:|---|
| eligibility | 52,829 / 0 | 9,804 / 9,803 | 6,781 / 59,610 | certificate 2,353; document 269 |
| Anthropic RSP | 145 / 0 | 20,255 / 20,255 | 0 / 145 | certificate 26 |
| OpenAI Preparedness | 45 / 0 | 86,275 / 86,275 | 0 / 45 | certificate 30 |
| DeepMind FSF | 20 / 0 | 10,357 / 10,357 | 0 / 20 | certificate 3; countermodel 1 |
| agent policy | 0 / 0 | 17,715 / 17,715 | 0 / 0 | none |

Notes on the counts:
- The "before" quantity-branch figures are the shadow's call counts (each call sends exactly one `check` case). The before run's recorder did not tag those cases yet, so the typing figure is the `check` total minus that count. The after run tagged them directly.
- The task quoted 24,000 calls under eligibility (part2-measure.json iii). That counted another thing; this run counts every `_checked_quantity` call.
- Eligibility's typing count moved by one (9,804 to 9,803) on a path this item does not touch (ve/ast.py). That path goes through `relay.decide_once`, whose memo the harness's threads share. That would explain it, but it is not proved; UNVERIFIED.

**The `check` branch is kept.** Lines removed: 0. `grep` for `decide("check"`, `rows("check"`, `decide_once("check"` and `answer("check"` found, in ve/, only ve/ast.py:396 and :417. Those are typing cases with `ast` and no `quantity`, and `core_gate` refuses a W6 environment before them (ve/ast.py:263). So no caller remains in ve/. In tests/, callers remain:
- tests/test_units_relay_w6a.py:139, `test_identities_are_lean_s_on_every_spelling`, sends `decide("check", [{"id": "v", "environment": raw, "quantity": payload}])` straight to the service. It now compares the `check` branch with the `quantity` row that `quantity_meaning_id` reads.
- tests/data/relay-gate-cases.jsonl:59 and :60 are `check` cases with a `quantity` member (ids `v` and `quantity`). These are the relay mutation gate's fixtures (tools/relay_mutation_gate.py, tests/test_relay_mutation_gate.py).
- tests/test_relay_wire_check.py:197 sends a `check` case with a `quantity` member, but to a stub pool that never reaches Lean. It tests the relay's sendability check, not the branch.
- The schema entry is the first branch of `lean/ResponseShape/Schemas/Check.lean` (`well_typed`, `meaning_id`, `Q`, `core`, `environment_id`, `target_environment_id`).

Deleting the branch would also change direct service answers for a W6 environment in `check` mode. They are answered today, and the task leaves answer bytes out of scope. So the conservative choice is the one the task names: leave it and list the callers.

## Acceptance: the five keys' answers, and eligibility's wall time

- The five harnesses exited 0 in both runs (before with the shadow, after without): /tmp/kb8c/out/{before,after}/<key>/rc.
- Eligibility's stdout is byte-identical (`cmp`). RSP and FSF differ only in their elapsed-time figure: identical after removing `(<n> s)`. Preparedness and agent policy print JSON, and are identical after removing every float, which are their `seconds` and per-phase timing fields.
- The eight `usecases/*/results.json` files have the same SHA-256 after both runs (`sha256sum -c` printed no mismatch), and `git status` stayed clean.
- Eligibility wall time, one run each, same machine, six minutes apart, without the recorder (`/usr/bin/time` around `iso.sh … .venv/bin/python usecases/eligibility/run.py --no-write`):
  - before: 353.5 s (load 6.3 at start);
  - after: 308.2 s (load 19.9 at start);
  - ratio 0.87x, so below 1.5x. The stdout of the two runs is byte-identical.

## Seeded bugs (docs/kernel/kb-8c/seeded-bugs.json)

| Id | Language, file | Mutation | Fails |
|---|---|---|---|
| S1 (a) | Lean, lean/VE/Time/Wire.lean | valued admission answers `("value", Json.bool true)` | `lake build VE.Time.WireSound`: `_valued` does not build (WireSound.lean:89-107, a heartbeat timeout unifying `true` with the evaluation); `_plain` builds |
| S2 (b) | Lean, lean/VE/Time/Wire.lean | `… ++ ids ++ [("Q", a.core)] ++ value` (a second `Q` after the seven) | both statements: `_plain` at WireSound.lean:67 (application type mismatch, both kind branches), `_valued` at 89-107 |
| S3 (c) | Python, ve/units.py | `environment_id` comparison skipped | `tests/test_units_relay_w6a.py::test_an_admission_row_of_another_environment_is_refused` (3 of 3: `elaborate_quantity`, `quantity_meaning_id`, `core_formula`) |
| S4 | Python, ve/units.py | `_checked_quantity` asks `check` again | `tests/test_units_relay_w6a.py::test_the_shown_values_are_the_quantity_admission_rows` |
| S5 | Lean, lean/VE/Time/WireSound.lean | `target_environment_id` dropped from `_plain`'s list | `lake build VE.Time.WireSound` (WireSound.lean:67) |
| S6 | registry, tools/kernel-paths.json | `count` removed from quantity's `kinds` | `tests/test_kernel_closure.py::test_every_case_kind_of_a_kernel_runner_has_an_entry_and_every_entry_a_kind` |

Seed (b) shows why the open-field rule exists:
- With S2 planted, the old open form, `answer = ok id ([seven] ++ value)` for some `value`, is still proved, with `value := [("Q", a.core)]`. `Json.mkObj` keeps the last entry per key, so that tail overrides `Q`. The proof is docs/kernel/kb-8c/open-tail-seed-b.lean.txt; `lake env lean` on it exits 0 against the seeded runner.
- The closed statements fail.
- A second `("Q", a.Q)` with the same value builds: `Json.mkObj` gives the same object, so nothing is wrong there.

Every file was restored from a saved copy (`git diff --quiet`) and rebuilt (`lake build VE.Time.WireSound` exit 0).

Trust mutants: Light-lane check said NOT (WireSound.lean is unclassified and so counts as trusted). `mac-pytest.sh --trustmut -- --json docs/kernel/kb-8c/trust-mutants.json`: "0 definitions, 0 mutants … 0 KILLED, 0 SURVIVOR", exit 0. The Lean change is theorems only, and the tool never selects theorems.

## Notes for the DRI

- This item changes an approved Lean theorem statement: `quantity_admission_wire_sound` is replaced by two statements.
  - The architect seat ordered it (task kb-8c, decisions D11 and D13). It is a restatement: no hypothesis is added to a false statement, and every conjunct of the old conclusion is in one of the two (section (1)).
  - The same class of change in kb-validators (a new conjunct, ordered by the same seat) merged without a DELTA row.
  - No user-visible output changes, so there is no DELTA row.
- The `check` mode's quantity branch could be deleted by a later item, once `test_identities_are_lean_s_on_every_spelling` and the two relay-gate fixtures ask the `quantity` mode instead. That deletion changes direct-service answers for W6 environments in `check` mode (answered, then refused), so it needs a DELTA row.

## Notes

- `kinds` maps `admission` to `_valued`. The tool's form allows one theorem per kind, so `_plain` is listed on the path but not in the kinds table.
- The selected run was on the committed tree b4b047fa7f. It ran on ve-cloud-2 because the Mac was not available (MAC_LAST_RESORT).
- `gate_collection.py --check --prebuilt`: "8 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed".

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: PASS. `tests/test_units_relay_w6a.py::test_a_retyped_admission_field_fails_the_schema` retypes each of the four read fields: deleted, `null`, `true`, `7`, `1.5`, `"x"`, `"\ud800"`, `[]`, `{}`, a 10k-deep list, and a hex64 where an array is expected. Each goes through the service's decoder and is refused. The admission row's transport is in the relay mutation gate's fixtures: 3 quantity admission cases without a model and 2 with one, in tests/data/relay-gate-cases.jsonl.
2. Deliverables: PASS. See the Deliverables table. The branch deletion did not happen because the task's own condition was not met; callers are listed in (3). `git diff main...HEAD` has no new permanent report test and no Python copy of a Lean decision.
3. Tests can fail: PASS. Seeds S1-S6 above. Trust mutants: 0 selected, exit 0, docs/kernel/kb-8c/trust-mutants.json.
4. Python/Lean/Rust agree: PASS. The shadow compared both Lean modes on 53,038 calls with 0 differences, and the five keys' outputs are identical (above). No Rust changed.
5. R8 binding: PASS. `environment_id` is the only identity Python binds here, and `tests/test_units_relay_w6a.py::test_an_admission_row_of_another_environment_is_refused` refuses another environment's id and an all-zero id at each entry. A row-count change (extra, duplicated or empty) is refused by the transport's request binding (`check_response`), which the relay mutation gate tests.
6. Gate evidence: PASS. The selected run was on committed HEAD fb612c50b0 (tree b4b047fa7f), exit 0, 0 failed. The full gate is the chain's. Commit list: `git log main..HEAD --no-merges` (6 commits plus this report).
7. Unsigned items: PASS. There is no DELTA row. The kernel rise is signed in ALLOWANCES.md (architect seat, D11, up to +1,300), and the trust map is +0.
8. User-visible changes: PASS. The five keys' outputs and the eight results.json files are unchanged (above), and the `check` branch is kept, so no answer byte changes.
9. Test selection: PASS. `select_tests.py` picked 193 units, including tests/test_units_relay_w6a.py and tests/test_kernel_closure.py, which catch S3, S4 and S6.
10. Lean statements: PASS. S1, S2 and S5 break the build. Both theorems are about `runCase j more = .ok answer`, the returned value. No `tools/check_*_statements.py` covers `VE.Time.Wire` (grep). No hypothesis was added to a statement; the model disjunct became the split.
11. Budgets and limits: N.A. No public operation or limit changed. The quantity admission keeps its `budgetExhausted` error exit, which no theorem covers (unchanged).
12. CPU and memory: PASS. Eligibility took 353.5 s before and 308.2 s after (0.87x). The switch only changes which mode answers; the cases are the same.
13. Test-removed trailers: PASS. `gate_collection.py --check --prebuilt`: 0 removed, 0 refused, 0 stale, 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS.
    - Both directions: genuine rows pass (`test_the_shown_values_are_the_quantity_admission_rows`), and rebound or retyped ones are refused. Kinds: the nine literals equal the table (S6 removes one).
    - Spec re-read:
      - `_plain` and `_valued` against the task text and lean/VE/Time/Wire.lean:808-820;
      - the kinds table against Wire.lean:798-847 and Document.lean:610-611;
      - the ALLOWANCES row against kb-8b's task part 1 (b);
      - the frozen-keys edit against the same.
15. Overclaim, silent cut, failing checks, limits charged first: PASS / PASS / PASS / N.A.
    - "Unchanged" is said only of outputs compared by `cmp`, `sha256sum` or the masked diff above, and of the trust map (+0).
    - The one unexplained count (eligibility typing, 9,804 to 9,803) is marked UNVERIFIED.
    - The branch deletion is not a cut: the task's condition decides it.
    - No new limit.

Sibling lesson (kb-validators review, F1: a DELTA row cited R7 although direct service requests saw a refusal): checked. This item changes no direct service answer, because the `check` branch is kept. That is why there is no DELTA row, and the deletion is left for an item that writes one.
