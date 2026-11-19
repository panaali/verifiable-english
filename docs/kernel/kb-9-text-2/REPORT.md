# kb-9-text-2 REPORT

Status: done, ready for the gate; no DRI signature needed.
HEAD: the commit that adds this report, on top of 60a3157f7d (the edit), base main 20cf38f5422e.
Change: one line of `tools/kernel-paths.json`. runSoftKind's "why" now says that soft_wire_selected_facts states soft-selected's whole answer and soft_wire_selected states only SelectedAnswer (F3 of kb-9-looprecheck1).
Open items: none. No Lean, Python or Rust change; DELTA none; trust +0.
SIZE: 0 product, 0 tests, 1 other hand-written line (tools/kernel-paths.json; plus this report).

## Plan rows (all AGENT)

| Deliverable | Delivered | Evidence |
|---|---|---|
| 1. Failing-first probe | yes | see "Probe" below |
| 2. One-line edit of the "why", naming soft_wire_selected_facts; grep for other "whole answer" claims | yes | commit 60a3157f7d; see "Other whole-answer claims" |
| 3. Regenerate nothing by hand | yes, nothing to regenerate | see "Generated files" |

## Probe

Command: `uv run python -c "import sys; sys.exit(int('soft_wire_selected covers soft-selected (its whole answer' in open('tools/kernel-paths.json').read()))"`

- Before the edit, on this branch at main 20cf38f5422e: `probe exit 1`.
- After the edit (60a3157f7d): `probe exit 0`.

## The two statements (lean/VE/SoftNorms/SelectedSound.lean, namespace VE.SoftNorms.Run)

`soft_wire_selected` (line 182) concludes, after the decoding conjuncts:

```
      SelectedAnswer id src.D M qs answer
```

where (line 45)

```
def SelectedAnswer (id : String) (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity)
    (qs : List SelectedQuery) (answer : Json) : Prop :=
  ∃ sent facts, SelectedAnswerWith id D M qs (factsFields sent facts (coherentAt D M)) answer
```

So it fixes `id`, `status`, `background` and `results`, but leaves open whether `facts` and
`coherent` appear and what `facts` is. Its own docstring (lines 42-44) says this:
"It cannot see the case; `soft_wire_selected_facts` states, from the case, when the two appear and what `facts` is."

`soft_wire_selected_facts` (line 221, kb-9) concludes, besides the same decoding conjuncts and `SelectedAnswer`:

```
      VE.Compose.SlotWire.decodeFacts src j = .ok (P, items) ∧
      (∀ φ ∈ P, φ.WellFormed (envAt (soften src.D) 0) []) ∧
      SelectedAnswerWith id src.D M qs (factsFields (factsSent j) (factsAt P M) (coherentAt src.D M)) answer ∧
      (factsSent j = true ↔ ∃ v, j.getObjVal? "facts" = .ok v) ∧
      (factsSent j = true → ∃ b, answer.getObjVal? "facts" = .ok (.bool b) ∧
        (b = true ↔ ∀ φ ∈ P, φ.denote M.asStructure [])) ∧
      (factsSent j = false → (∃ e, answer.getObjVal? "facts" = .error e) ∧
        ∃ e, answer.getObjVal? "coherent" = .error e)
```

This conclusion fixes the whole answer: `SelectedAnswerWith` is an equation `answer = VE.Route.Wire.ok id (...)` (line 37)
with the facts' fields decided from the case.

New text, in place of `soft_wire_selected covers soft-selected (its whole answer; kb-10a)`:

> soft_wire_selected_facts covers soft-selected (its whole answer: SelectedAnswerWith the facts' fields, `facts` and
> `coherent` present exactly when the case sent `facts`, `facts` true exactly when every decoded fact holds; kb-9), where
> soft_wire_selected states only SelectedAnswer (id, status, background and results; whether `facts` and `coherent`
> appear and the value of `facts` left open; kb-10a)

## Other whole-answer claims

`grep -n 'whole answer' tools/kernel-paths.json` matches one line (346), runSoftKind's "why". That line makes three
other whole-answer claims, and I checked each against its statement in lean/VE/SoftNorms/SlotSound.lean:

- slot_wire_certificate (line 30): concludes `answer = slotCertificateAnswer id r openLabels`. The claim holds.
- slot_wire_conflict (line 66): each disjunct concludes `answer = slotWitnessAnswer id r names` or the
  `slotConflictAnswer` equation. The claim holds ("over the slot replays", as the text says).
- slot_wire_admission (line 128): concludes `answer = slotAdmissionAnswer id r`. The claim holds.

No other "why" names soft_wire_selected. The old clause was in no other file: `grep -rln 'its whole answer; kb-10a' .`
(excluding .git and .lake) listed only tools/kernel-paths.json.

## Generated files

`tools/kernel-paths.json` is hand-written: `uv run python tools/regen_generated.py --owner tools/kernel-paths.json`
prints `-`, and `--list` shows no generator that writes it. The "why" text reaches no generated file:
`regen_generated.py --check` (log /tmp/kb9t2-regen.log, with the edit applied) printed
`PASS: docs/kernel/closure-baseline.json is what --out writes now` for kernel-closure. It ended
`regen_generated: failed: route-cases, checker-pins`, and the tree stayed clean (`git status --short` showed only the
edit). Neither check reads the registry. route-cases rewrites lean/VE/Route/examples/route-cases.json through the Lean
service, and checker-pins compares lean/checkers.lock with the built binaries. I did not run that check on main, so I
do not claim these two failures were already there. The chain's gate on the final HEAD decides.

## Tests

- `uv run pytest -q tests/test_kernel_closure.py` on the edit: `53 passed` (/tmp/kb9t2-kc.log).
- Selected run `mac-pytest.sh --select -- --base 20cf38f5... --run`: 12 units, `0 failed`, exit 0 (ran on the VM,
  MAC_LAST_RESORT; /tmp/kb9t2-select.log).
- Not run: the full gate (the chain runs it), trust_mutants (LIGHT lane: `LIGHT 2 changed lines outside generated
  files <= 150 (1 files), no trusted-core file`; no Lean change).

## Seeded bugs (all in tools/kernel-paths.json, the only changed file; no Lean, Python or Rust product code changed)

| # | Behaviour | Mutant | Fails | Restored |
|---|---|---|---|---|
| S1 | The why no longer overclaims soft_wire_selected | put the old clause back | probe exits 1 | `git checkout`; probe exit 0 |
| S2 | The registry still parses | add a stray `"` inside the new text | `tests/test_kernel_closure.py` collection ERROR (JSONDecodeError), rc=2 | `git checkout`, clean |
| S3 | runSoftKind's uncovered row keeps a real reason | why replaced by `"soft kinds"` (< 20 chars) | `tests/test_kernel_closure.py::test_the_registry_problems_are_found_before_any_lean_runs` FAILED | `git checkout`, clean |

## Trust

`uv run python tools/trust_map.py --check` (/tmp/kb9t2-trust.log): `against 20cf38f5422e: K +0, S +0, D +0, G +0,
tied +0, unclassified +0, trusted +0` and `PASS`. No allowance recorded, and no FOLLOW-UPS row (R16 is not used).

## DELTA

None: the change is registry text only and changes no verdict or answer. No DELTA.md.

## Pilot bytes

0 expected (no verdict or rendering path reads the "why" text).

## Next item

None.

## Notes for the DRI

- The registry's `kinds` map still lists `"soft-selected": {"theorem": "VE.SoftNorms.Run.soft_wire_selected"}`.
  The task puts any tier change out of scope, so I did not point it at soft_wire_selected_facts. The why text now
  says which theorem states the whole answer. Whether the kinds row should name the stronger theorem is a registry
  choice for a later item; no verdict depends on it.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relayed answer or schema changed.
2. Every deliverable built, no rule broken: PASS, the plan-rows table above. The probe goes 1 → 0.
3. Tests and gates can fail: PASS, seeded bugs S1-S3 (probe; tests/test_kernel_closure.py::test_the_registry_problems_are_found_before_any_lean_runs).
4. Py/Lean/Rust agree: N.A., no code in any of the three changed.
5. R8 binding: N.A., no binding changed.
6. Gate evidence matches final HEAD: PASS by construction. The chain runs the gate on the final HEAD; this report holds no gate numbers.
7. No unsigned item: PASS, no DELTA row and no reserved signature.
8. Every user-visible change in DELTA: N.A., no user-visible change (registry text only).
9. Test selection finds affected tests: PASS, the selected run picked tests/test_kernel_closure.py and tests/test_ownership_floor.py, which read the registry (/tmp/kb9t2-select.log).
10. Lean statements say what is claimed: PASS. The new text was checked against the quoted statements of soft_wire_selected, SelectedAnswer and soft_wire_selected_facts, and the other three whole-answer claims against SlotSound.lean (section above).
11. Budgets and limits fail closed: N.A., no evaluator or limit touched.
12. No CPU or memory regression: N.A., text only.
13. Test-removed trailer: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. Both directions of the probe were recorded (1 before, 0 after, 1 with S1). Each claim cites its command or log. I re-read the task text and the decision's wording ("names soft_wire_selected_facts as the theorem that states the whole answer, and what soft_wire_selected covers").
15. Four classes. No overclaim: PASS. Each universal word in this report cites a grep or log above ("only", "every": the SelectedSound.lean quotes). No silent cut: PASS, all three deliverables were done. New check can fail: N.A., no new check added (S1 shows the probe can fail). Limits charged before work: N.A.
