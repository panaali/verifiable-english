# Feature review: what `ve-green-rd-3` adds over `ve-green-lf-17`

Source: the pinned 184,893-byte constitution, unchanged (`source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261009T0600Z` (`prev/`). Two first-parent merges since `ve-green-lf-17`.

| Merged | What it is | Changes what a document can say? |
|---|---|---|
| `lean-first/b12` (lf-12) | Lean validates every authored environment and model envelope before Python builds one; the Python profile gate and decoder refusals are deleted | No |
| `readings-defaults/rd3` (rd-3) | the enumerated route's conflict, premise and entailment folds, the three-valued gate, the restrictions and the English plan are Lean's (`readings-verdicts`) | No new form of text |

Result: **no unit changes status because of a feature, and no unit is newly expressible.** The only status change of this run (u0166.s04.p4, OPEN -> UNFORMALISED) is an audit repair.

## What did change the measurement (not a new feature)
* **Same verdicts, faster.** `ve document check` of the unchanged 20261009T0600Z translation at rd-3 (`check-baseline.json`) gives the same verdicts as at lf-17: premises `model` in all 32 choices, enumerated plan, conflict-free, 8 separating situations. It takes 83 seconds, about 5 minutes before (RD-3 moved the folds to Lean). All eight sets, with content, still fit in one document (32 choices of at most 64).
* **The conclusion queries give the same answers**: the denial query ("Claude may not directly deny being Claude") ALL under the strict reading, UNKNOWN under the defeasible one and across all readings; the "claim to be human" query ALL under the narrow scope, UNKNOWN under the wide one (now stated on the instructed behaviour, see AUDIT-REPAIR.md).
* **Lean-decided share stays 0.00%.** RD-3 is merged, but no route and no CLI output reports `decided_units` (the only mentions in the repository are `tools/lean_decided_share.py`, its test and the gate list; Lean's `setDecided` of spec 1.10 is not in `lean/VE`). The folded verdicts are Lean's, the units are not reported as decided.

## A defect the probes found
`probes/rights-reading-probe.json`: one of the four situation-by-candidate checks of the rights probe used to be refused by name ("relations must contain exactly the base predicates; defined tables are computed"). At rd-3 it ends in a Python `KeyError: 'soft__excepted__no_system_prompt_deception'` from `ve/model.py` `_decode`: lf-12 builds the model of a generated soft/rights environment without Python's shape check. The probe's conclusion is unchanged. A refusal turned into a crash is a tool defect, not a translation property. The other six carried probes are byte-identical to the previous run's JSON; the profile-combination probe differs in one refusal sentence (`reports@0` with the strict companion now reads "Unsupported profile norm-defaults@0").

## Costs and limits
* Open terms 36 -> 34: `operator_unlocks`, `user_unlocks` and the wide-scope term (`instruction_given_while_role_playing_persona`) removed, `instruction_is_for_behaviour_while_role_playing_persona` added; three "how likely" factors removed from the factors of other terms.
* A defeasible rule beside norm-defaults@0 is still refused (probe c); the defeasible candidates are the strict rule with an `unless` over an open term.
* `ve document` still refuses a reading with `companion` (RD-4b is not merged).
* `readings/all-default.ve.md` and `readings/s1.ve.md` are not carried; the probes that read them were run on the earlier copies and the copies removed.

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50, counting 31, modality/belief 25 (24 + u0166.s04.p4), attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1.
Next, in order of unlock: reporting decided units from RD-3; RD-4b (companions); typed modals ("cannot", "can", "may": ability, permission or authority) and graded quantities.
