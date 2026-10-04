# Feature review: what `ve-green-layers2-b2` adds over `ve-green-env-profiles`

Source: the pinned 184,893-byte constitution, unchanged (SHA-256 `fa10ed48…50dd`, `../source/SOURCE.md`). Start point: the translation of run `20261004T0600Z` (`prev1004/`): 1,129 of its 1,132 ledger entries are identical in this run, 3 changed (`u0123.s01.p1` in status; `u0062.s01` and `u0123.s02.p1` in candidate wording), none added.

## Merged since `ve-green-env-profiles`

`git diff --stat ve-green-env-profiles..ve-green-layers2-b2 -- ve/` is empty. Under `lean/`: `VE/Readings/Force.lean` (new), `Readings/Separate.lean`, `Audit.lean`, pins.

| Merged | What it is | Changes what can be written? |
|---|---|---|
| `proof/decision-only-sound` | Lean proves `decision_only_sound`, the statement behind a `SeparatedByDecisionOnly` finding | No. The wire text and English are unchanged by decision (DRI ruling 2 of 2026-10-02): the finding is still `(not certified)` and E25. All five `SeparatedByDecisionOnly` findings of the demonstration document still carry it. Replacing it with the certified form is a wire-contract change, not made at this tag. |
| `infra/layers2-b2` | Rust `ve-core` split into kernel, profile and surface crates behind a facade | No. Internal; output unchanged. |
| `infra/gate-collection` | pins the test-collection list | No. Infrastructure. |

Result: **zero newly expressible features, zero units upgraded by a new feature.** What follows is the repair of the audit's two units, done with the language of the previous tag.

## What the repair shows about the language

* **F22 (new). "can" needs a typed action complement.** The audit separates three readings of an operator "can": *permitted to*, *able to give/instruct* (supply input) and *able to get Claude to do* (induce behaviour). VE has no modal form: a reading set's candidates are texts, and a candidate norm carries no content in a `norm-defaults@0` document, so the three can be told apart only in prose. What VE can do is state the permission reading as a rule and *not* offer a reading the text does not admit: `u0123.s01.p1` ("permitted") has exactly one reading and now carries it as a rule in the main document, so a sentence with an explicit word of permission no longer needs a reading set.
* **F1 (still true). `readings@1` content cannot be beside `norm-defaults@0`** (`probes/s1-probe.json`, byte-identical). Faithful strict/defeasible pairs with content stay impossible; the demonstration companions (soft chain, completion `deny`) remain outside every claim.
* **F20, F21 (still true).** A nested "all of the following" guard does not parse back from English (29 of 29 strict rules, all written as exceptions, do). No graded normative force (`u0078.s01`, `other:graded-force`).

## Findings still true at this tag

**F2.** A norm candidate can carry content only on the soft chain. **F4.** Act phrases are at most 80 characters, letters, `'` and `-`, no logical words. **F6.** English for binary base predicates is generic. **F10.** Composition rejections unchanged (`closure@0`, `order@0`, `reports@0`, `alternatives@0`, `risk@0`, `speech-acts@0`, `rights@0` without `soft-norms@0`, `ve.discourse@1`); `time@0`, `definitions@0`, `data@0` accepted; `readings@1` only with `norms@0` and its chain. **F11.** The `defaults` tag is stale (50 units). **F12.** Sorts of parties are bare sorts. **F13.** Modality is folded into predicates. **F14.** A permission's limits live in another sentence; reading choices do not propagate across sets. **F15.** A candidate is one content. **F16.** Outcome probes lean on the completion (demonstration companion). **F17.** The source word of a pair is a closed list. **F18.** E24 ("VE cannot yet show in words") is the wording of several demonstration pairs. **F19.** A binary base predicate whose wording starts with "is …" can break unrelated English.

* **Nine sets became eight** in the main document (`u0123.s01.p1` is a rule now); the demonstration S1 document has 8 sets (its `u0123.s01.p1` set was dropped, so the rejected ability candidate is in no file). Five findings `SeparatedByDecisionOnly (not certified)`.
* **The document verdict stays UNKNOWN** ("superposition pending"; reading plan UNKNOWN, 96 choices over a budget of 64). Nothing resolves a reading set (per-choice semantics, S2, is not merged).

## Missing features, in order of what they would unlock here (ledger tally `UNFORMALISED`)

norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50 (stale), counting 31, modality/belief 24, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1.

1. **`readings@1` content beside `norm-defaults@0`** (F1).
2. **Typed modals with action complements** (F22) and **graded normative force** (F21).
3. **Per-choice semantics (S2)** and the certified form of the `decision_only_sound` finding (the theorem is proved; the wire text is not yet changed).
4. **Cross-sentence scope** (F14), binary relation wording (F6, F19) and nested-list English (F20).

## Carried probes (re-run at this tag)

`probes/unspecified-probe.json`, `s1-probe.json`, `risk-probe.json`, `discourse-probe.json` and `rights-reading-probe.json` are all byte-identical to the previous run's: 34 points, 21 SETTLED, 13 UNDECIDED, 0 CONFLICT; the whole-document proof still returns CONFLICT-FREE.
