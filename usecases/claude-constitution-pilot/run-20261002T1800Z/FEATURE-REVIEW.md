# Feature review: what `ve-green-wire` adds over `ve-green-unspecified-uc`

Source: the pinned 184,893-byte constitution, unchanged (SHA-256 `fa10ed48…50dd`, `../source/SOURCE.md`). Start point: the translation of run `20261002T0620Z`
(`prev0620/`): 1,128 of its 1,132 ledger entries are identical in this run, 4 are changed (`u0062.s01`, `u0123.s01.p1`, `u0123.s02.p1`, `u0166.s04.p4`), none added.

## Merged since `ve-green-unspecified-uc`

`git diff ve-green-unspecified-uc..ve-green-wire -- ve/` touches 14 files: `ve/errors.py` (an optional `diagnostic` field on errors), `ve/rights.py` (one attribute),
`ve/softnorms.py` (the soft route alone refuses `rights@0`), `ve/softnorms_contract.py`, `ve/wire_contract/*`, `ve/assurance-manifest.json`. Nothing in `ve/document.py`, `ve/norms.py`,
`ve/norm_defaults*.py`, `ve/profiles.py`, `ve/english*.py`. The two merges:

| Merged | What it is | Changes what can be written? |
|---|---|---|
| `compose` (S0) | Lean proofs of a composition dispatcher and the base-premise slot (`VE.Compose`); `docs/INTEGRATION-GAPS.md`: "the dispatcher is not called by an executable in S0" | **No.** No new profile combination is admitted. |
| `wire` | A generated contract for `soft-norms@0` (table, diagnostics, English table), checked in Python and Lean in shadow | **No.** It changes how errors are reported and cross-checked. |
| soft route and `rights@0` | `LAYER_ROUTES`: a soft source that lists `rights@0` is never accepted by the soft route alone | A tightening, not a feature. |

Result: **0 newly expressible features, 0 units upgraded by a feature.** The profile probe (`metrics.json`, `profile_combination_probe`) gives the same accepted and rejected combinations as
last run, including `norm-defaults@0` with `soft-norms@0` (still rejected: "await the Lean route"). The risk and discourse probes (re-run) are byte-identical; the rights probe (re-run on the soft
companion) reaches the same conclusion. So the differences between this run and the last measure the audit repairs, not the language.

## What this run did instead (existing features, applied to a finding)

1. **Scoped permissions** (existing `norms@0` exceptions + `norm-defaults@0`): each operator permission excludes the six kinds of input the next sentence says operators cannot instruct.
   VE's verdicts moved from a checked CONFLICT to SETTLED no on the overlapping inputs, and its whole-document proof went from UNKNOWN to CONFLICT-FREE (`probes/unspecified-probe.json`).
2. **An ability the source denies, written as a statement and not as a norm** (existing FOL fence): "cannot be unlocked by any operator or user". No duty on anyone.
3. **A labelled evaluative inside a reading set** ("legitimately" as the named open term `instruction_is_legitimate`).

## Findings still true at this tag

* **F1. A completion cannot be avoided on the defeasible route.** `norm-defaults@0` cannot share a document with `soft-norms@0`; the defeasible readings live in `readings/all-default.ve.md` with deny completions.
* **F2. A norm reading candidate cannot carry content** (12 reading sets, none content-bearing; main premise status UNKNOWN: "non-assertion reading elaboration pending"). Elaboration happens only in the strict companion.
* **F4. Act phrases** are at most 80 characters, letters, `'` and `-`, no logical words.
* **F6. English for base predicates is generic** for relations: a binary base predicate cannot carry an authored wording (VE prints `has the recorded relation "operator_unlocks" to …`; lint reasons such as `BINARY_AUXILIARY`, `LOGICAL_WORD`, `SYMBOL_COLLISION`). Unary wordings are limited to a fixed shape (`TEMPLATE_SHAPE`).
  The checked `u0166.s04.p4` is therefore readable but not natural.
* **F10. Composition**: unchanged rejections (`soft-norms@0`, `closure@0`, `order@0`, `reports@0`, `alternatives@0`, `rights@0`, `risk@0`, `speech-acts@0`, `ve.discourse@1`); `time@0`, `definitions@0`, `data@0` accepted.
* **F11. The `defaults` tag is stale** (50 units; only four ever needed a completion).
* **F12. Sorts of parties.** `operator`, `operator_input`, `hard_constraint` are bare sorts: "who is an operator" and "the seven hard constraints" are not tied to the rules by name, so "these" in `u0166.s04` stays the seven by a note only.
* **F13 (new). Modality is folded into predicates.** "cannot be unlocked" is a statement about an ability; the language has no possibility operator, so "able to" is part of the predicate and the claim is checked only as a universal negation. A real `modality/belief` feature (24 units tagged) would let the source's "cannot" be told from "does not".
* **F14 (new). A permission's limits live in another sentence.** The scope of `u0062.s01` and `u0123.s02` is fixed by `u0123.s03`, whose own scope (narrow or wide) is a reading set; the language has no way to make the exceptions follow the choice, so the narrow reading is the one wired in and the dependency is recorded in the notes.

## Missing features, in order of what they would unlock here (ledger tally `UNFORMALISED`)

norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50 (stale), counting 31, modality/belief 24, attribution 12, time 9, `other:open-list` 1 (unchanged).

1. **Unspecified together with soft norms** (F1): defeasible "should" statements are the bulk of the 669.
2. **Norm reading candidates that hold their rules** (F2).
3. **A normative layer that can say "whichever reading of that sentence is taken, this follows"** (F14).
4. **Binary relation wording** (F6) so checked relational statements read as English.
