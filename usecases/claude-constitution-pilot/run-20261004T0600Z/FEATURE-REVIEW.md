# Feature review: what `ve-green-env-profiles` adds over `ve-green-wire-s4`

Source: the pinned 184,893-byte constitution, unchanged (SHA-256 `fa10ed48…50dd`, `../source/SOURCE.md`). Start point: the translation of run `20261003T0600Z` (`prev1003/`): 1,121 of its 1,132 ledger entries are identical in this run, 11 changed (`u0078.s01` and `u0073.s05` in status; the other nine only in notes and, for `u0123.s03`, candidate wording), none added.

## Merged since `ve-green-wire-s4`

`git diff --stat ve-green-wire-s4..ve-green-env-profiles -- ve/` touches 16 files (281 insertions, 121 deletions); nothing under `lean/`.

| Merged | What it is | Changes what can be written? |
|---|---|---|
| `fix/env-field-types` (env-profiles) | every top-level environment field is type-checked before use and read in the order of the Lean route that decodes it; wrong-typed fields give that route's diagnostic on every route (Python, Lean, Rust) | No. It changes which malformed environments are refused and how. |
| `infra/layers2-b1` | Rust module check and output differential, kernel wire tag tables replace registry reads | No. Internal. |

Result: **zero newly expressible features, zero units upgraded by a new feature.** What follows is the repair of the audit's six units, done with the language of the previous tag.

## What the repair shows about the language

* **A defeasible duty can be stated in `norm-defaults@0` as a rule with a named open exception** (`u0073.s05`: "generally" = `general_exception_to_complying`, decided by nobody the source names; the source's own conditions are exceptions). It keeps the completion `unspecified`, so VE says UNDECIDED, not "not required". This is the existing profile used as it was; it does not need `soft-norms@0`. What it cannot do: tell a *strict* reading from a *defeasible* one inside one reading set (that needs `readings@1` content, which cannot join `norm-defaults@0`).
* **F1 (still true). `readings@1` content cannot be beside `norm-defaults@0`** (`probes/s1-probe.json`, byte-identical to the last run). So the six "should" pairs and the four operator "can" sets keep their candidates without content in the main document; the only content-bearing form is a companion on the soft chain, which must complete with `deny`, an invention the audit rejected. Those companions are now demonstrations only (not claimed).
* **F20 (new). A nested "all of the following" guard does not parse back from its English** (`IdentityMetadataMismatch: block count`), even with no exception; the same condition written as repeated "Except when …" lines parses back and is more natural English. The soft-norms version of `u0073.s05` had the same defect (it is the one rule of the demonstration companion that does not round-trip). All 29 strict rules now round-trip.
* **F21 (new). No graded normative force.** "err on the side of following" cannot be a rule: a strict duty is too strong, a defeasible duty keeps an exception but no leaning, and nothing ranks one party's instructions above another's. `u0078.s01` is UNFORMALISED, missing feature `other:graded-force` (tally 1; the other sentences with "prefer" or "weigh" are already counted under norms and quantities).

## Findings still true at this tag

* **F2.** A norm candidate can carry content only on the soft chain, never in a `norm-defaults@0` document. **F4.** Act phrases are at most 80 characters, letters, `'` and `-`, no logical words. **F6.** English for binary base predicates is generic. **F10.** Composition rejections unchanged (`closure@0`, `order@0`, `reports@0`, `alternatives@0`, `risk@0`, `speech-acts@0`, `rights@0` without `soft-norms@0`, `ve.discourse@1`); `time@0`, `definitions@0`, `data@0` accepted; `readings@1` only with `norms@0` and its chain. **F11.** The `defaults` tag is stale (50 units). **F12.** Sorts of parties are bare sorts. **F13.** Modality is folded into predicates. **F14.** A permission's limits live in another sentence; reading choices do not propagate across sets. **F15.** A candidate is one content. **F16.** Outcome probes lean on the completion (in the demonstration companion). **F17.** The source word of a pair is a closed list. **F18.** E24 ("VE cannot yet show in words") is the wording of 8 of the 16 demonstration pairs. **F19.** A binary base predicate whose wording starts with "is …" can break unrelated English.
* **Ten sets became nine**: the demonstration S1 document has 9 sets and 16 pairs (outcome 7, selects 5, holds 4); five findings `SeparatedByDecisionOnly (not certified)`. `decision_only_sound` is still unmerged here.
* **The document verdict stays UNKNOWN** ("superposition pending"); nothing resolves a reading set (per-choice semantics, S2, is not merged).

## Missing features, in order of what they would unlock here (ledger tally `UNFORMALISED`)

norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50 (stale), counting 31, modality/belief 24, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1.

1. **`readings@1` content beside `norm-defaults@0`** (F1): it would restore faithful strict/defeasible pairs and the operator sets with the completion `unspecified`, removing the need for any `deny` companion.
2. **Graded normative force** (F21): "err on the side of", "prefer", "weigh" as a language form, not a duty.
3. **Per-choice semantics (S2)** and a certified `decision_only_sound`.
4. **Cross-sentence scope** (F14), binary relation wording (F6, F19) and nested-list English (F20).

## Carried probes (re-run at this tag)

`probes/risk-probe.json` and `probes/s1-probe.json` are byte-identical to the previous run's. `probes/discourse-probe.json` differs in one word of one message (the first unit with an unrecorded slot is now `u0123.s02.p1`, `u0078.s01` being UNFORMALISED); `probes/rights-reading-probe.json` differs only in model ids and in one predicate name (the finding is the same: no single situation is accepted for both rights candidates). `probes/unspecified-probe.json` has four more points (`u0073.s05`: SETTLED yes, then UNDECIDED three times); 34 points, 21 SETTLED, 13 UNDECIDED, 0 CONFLICT; the whole-document proof still returns CONFLICT-FREE.
