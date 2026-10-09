# Feature review: what `ve-green-lf-17` adds over `ve-green-lf-15b`

Source: the pinned 184,893-byte constitution, unchanged (`source/SOURCE.md`). Start: the translation of run `20261008T1800Z` (`prev/`). 5 first-parent merges since `ve-green-lf-15b`.

| Merged | What it is | Changes what a document can say? |
|---|---|---|
| `fix/bundle-test` | test infrastructure | No |
| `english-lean/e2-flip` | Lean's English reader and diagnostics are the authority | No (two probe diagnostics read differently) |
| `readings-defaults/rd4a` | Lean wire: reading sets with their own vocabulary (companions) merge and split per component | **Not reachable**: `ve document` still refuses a reading with `companion` (RD-4b is not merged) |
| `lean-first/b16b` | `ve-document@1` is checked by Lean's document mode; decoder diagnostics kept | No |
| `lean-first/b17` | assist and Cedar decisions move to Lean | No |

Result: **no unit changes status and no unit is newly expressible by a merged feature.**

## What did change the measurement (not a new feature)
* **Couplings.** The previous run recorded the four operator sets as "not linked in the language (F14)" and, with 1,152 choices, could check them only in three slices. A coupling on a label axis ties them; it validates and enumerates beside `norm-defaults@0` with content at this tag (I did not test it at the previous tag, so I cannot say whether it was already possible). With the inadmissible candidates removed (AUDIT-REPAIR.md) the eight sets have 2 x 2 x 2 x 2 x 2 x 2 x 2 x 2 = 256 combinations, of which the coupling allows 32 (16 for the force sets x 2 for the operator sets).
* **All eight sets in one document, which is the translation.** `ve document check` of `translation.ve.md`: premises `model` in all 32 choices (was UNKNOWN), reading plan `enumerate` (was UNKNOWN, 144 choices), conflict-free in all 32, 8 separating situations checked by Lean, no "separated only by decision" finding. Check time about 5 minutes.
* **A conclusion that depends on the ambiguity.** "No operator is permitted to give Claude an instruction to claim to be human when directly and sincerely asked": ALL under the narrow scope, UNKNOWN under the wide scope (`probes/nd/claim-human-*.json`). The denial query on the four force sets gives the same answers as before (UNKNOWN across readings, ALL under the strict reading, UNKNOWN under the defeasible one) and, in the whole translation, UNKNOWN across readings.

## Costs and limits
* Open terms 32 -> 36: `instruction_is_legitimate` removed; `instruction_given_while_role_playing_persona` and four `exception_to_*` terms (the exception a defeasible reading of "should" allows but the text does not name) added now that candidates have content.
* A defeasible rule beside `norm-defaults@0` is still refused (probe c), so the defeasible candidates are the strict rule with an `unless` over an open term.
* `lean_decided_share` stays 0.00% (RD-3 not built).
* `readings/all-default.ve.md` and `readings/s1.ve.md` (soft-chain demonstrations that held the removed candidates and the `deny` completion) are no longer carried: neither checks at this tag.
* Probes: the seven carried probes re-run; five byte-identical in their JSON; senses and discourse differ only in diagnostic wording.

## Missing features, ledger tally (`UNFORMALISED`), unchanged
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50, counting 31, modality/belief 24, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1.
Next, in order of unlock: RD-4b and RD-3; typed modals and graded quantities; statements about what a word does not mean.
