# sc-admit-cpu delta: admission's per-reading charge (`sdAdmitWork N ≤ maxSdAdmitWork`)

Base: `git merge-base HEAD main` (5f756e791d). The decision is manage-agents/reviews/dri-decisions-20261111-sc-admit-cpu.md:
- item 1 asks for step 2;
- item 2 signs the move of `sdRuleCharge`, `sdContentCharge` and `sdSizeCharge` to SoftWire.lean;
- item 3 signs the charge and its row.

The change applies only to a document under the soft completion with at most 64 compatible choices whose
`sdAdmitWork N` is over 131,072. Such a document is now refused at admission with
`ResourceLimit: the per-reading checks of <n> readings exceed 131072 units` (status `ResourceLimit`, exit 4). Every
soft-chain readings kind that admits a document refuses it with that text:
- `readings-validate`, `-elaborate`, `-separate`, `-choice`, `-dead`, the superposed kinds;
- `readings-verdicts` (RD-9's and DF-3's).

Unchanged:
- At most 131,072 units, every answer is today's, byte for byte. A failing choice's text is today's
  (SoftWireExamples.lean:49, :56).
- Over 64 choices nothing changes: no per-choice text runs and the charge is not read (:46).
- Documents on any other chain or route are not affected. The three keyed corpora and every soft-default document under data/ and usecases/ answer as on main (cpu.md, the DRI amendment's list).
- The move changes no value: sc-11w's size-charge and W-13 `#guard`s are unchanged and pass.

## User-visible deltas

| # | Where | Before (main) | After | Evidence | Ruling |
|---|---|---|---|---|---|
| 1 | every soft-chain readings kind's admission (`admitSDOf`, 4.1 step 5), documents of at most 64 compatible choices with `sdAdmitWork N` over 131,072. The documents named (the signature covers only these, DRI amendment 2026-11-11): NSDheavy (:35) and heavyIn (:36), and item 3's limit+1 fixture `overLimit` (:42); `atLimit` is refused only under the limit−1 parameter (:40), not at 131,072 | admitted after 64 per-choice texts, 1.30-2.00 s of Lean CPU (docs/rd-9/sc-admit-cpu/cpu.md), then the kind's answer | `ResourceLimit: the per-reading checks of 64 readings exceed 131072 units`, in at most 0.23 s | Regression rows: SoftWireExamples.lean:35 (NSDheavy), :36 (heavyIn), :42 (the next work over the limit); `tests/test_rd9_admit_charge.py::test_over_the_charge_admission_is_refused_with_leans_resource_limit` (validate and elaborate, through the service). Adequate budget: :38 (heavyIn under its own work as the limit: admitted), :40 (at the limit admitted, one unit lower refused); `test_within_the_charge_or_over_64_choices_admission_is_unchanged`. Condition test (DRI amendment 2026-11-11): `tests/test_rd9_admit_charge_corpora.py` (the three keyed corpora run live with their committed answers and no answer refused by the charge; every soft-default document under data/ and usecases/ admitted). Main vs HEAD at 131,072: no answer changes (cpu.md "Keyed corpora and soft-default documents at the final limit", output-corpora.txt) | SIGNED by the DRI 2026-11-11 (reviews/dri-decisions-20261111-sc-admit-cpu.md item 3) |
