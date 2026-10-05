# Feature review: what `ve-green-difffuzz` adds over `ve-green-layers2-b2`

Source: the pinned 184,893-byte constitution, unchanged (SHA-256 `fa10ed48…50dd`, `../source/SOURCE.md`). Start point: the translation of run `20261004T1800Z` (`prev1004b/`): 1,128 of its 1,132 ledger entries are identical in this run, 4 changed (`u0123.s01.p1` in status and text; `u0062.s01`, `u0123.s02.p1`, `u0123.s03` in candidate wording), none added.

## Merged since `ve-green-layers2-b2` (`git log --merges`, `git diff --stat`: 130 files, 53 under `ve/`)

| Merged | What it is | Changes what can be written? |
|---|---|---|
| `wire-s5` | JSON wire contracts and shadow adapters for `norms@0` and `norm-defaults@0` (`ve/norms_contract.py`, `ve/norm_defaults_contract.py`, `ve/wire_contract/*`) | No. A stricter wire format for documents that already existed. |
| `lean-first/b0`, `b3`, `b4` | Lean answers the readings and discourse routes alone; Python relays its row (`ve/backends/relay.py`, `ve/readings_route.py`, `ve/discourse.py`); Python's regeneration, byte-for-byte comparison and Rust's untrusted replay are deleted; every rejection carries Lean's code | No. Same documents, same verdicts; diagnostic wording changed (three probe files, below). |
| `english-lean` | English parsing and printing proved in Lean (S1a, S1b), Python as reference | No. Same English as before. |
| numerals, `wording_key` | one bounded numeral conversion (40 characters before `int()`), one reading of quoted parts shared with Lean | No. |
| `infra/testperf`, `testspeed`, `testselect`, `testselect2`, `difffuzz` | test speed, test selection, a differential corpus | No. Infrastructure. |

Result: **zero newly expressible features, zero units upgraded by a new feature.** What follows is the repair of the audit's two units with the language of the previous tag.

## Carried probes (re-run at this tag, unchanged outcomes)

* `probes/unspecified-probe.json` (34 points: 21 SETTLED, 13 UNDECIDED, 0 CONFLICT; whole-document proof attempt CONFLICT-FREE) and `rights-reading-probe.json`: byte-identical to the previous run's.
* `probes/s1-probe.json`: `readings@1` content beside `norm-defaults@0` and `unspecified` is still rejected. What changed is who says it: before, `CheckerUnavailable: ReadingsConformance: Python and Lean differ …` (Python said `UnsupportedProfile`, Lean `InvalidInput`); now Lean alone: `InvalidInput: invalid regulated role or default for clarification_required`.
* `probes/risk-probe.json`: the same rejections with Lean's `UnsupportedProfile:` prefix.
* `probes/discourse-probe.json`: the norms-free companion is still admitted; the translation itself is still rejected, with a different first message (`invalid JSON front matter`, where it was `UnrecordedSlot: u0123.s02.p1`). New in this run: the same document with its reading sets removed is rejected for the profile (`Unsupported profile norm-defaults@0`), the limit `docs/spec/discourse.md` 11 states. What in the reading sets the front-matter decoder rejects was not isolated.
* `readings/s1.ve.md`: 8 content-bearing sets, 6 outcome, 5 selects, 4 holds separations, 5 findings `SeparatedByDecisionOnly` (still "not certified" in the wire text), the same as before; its `u0123.s03` ability candidates are assertions over `operator_can_supply` ("able to give Claude the input"), which is the issue-an-instruction reading the repair asks for.

## What the repair shows about the language

* **F14 (sharpened). How far one sentence's limits reach depends on how another sentence is read, and the language cannot link the two.** `u0123.s01.p1` shows it: a rule with exceptions fixes one reading of `u0123.s03`. The only faithful form is to list the three ways the limits can reach by name (narrow prohibition, wide prohibition, inability) in a reading set without content; they are not propagated from `u0123.s03`'s own set. A cross-set choice (S2, per-choice semantics) would let the permission follow.
* **F22 (still true). "can / cannot" needs a typed action complement.** Three different acts hide behind it: being permitted, being able to issue an instruction, being able to get Claude to comply. This audit rejected the third as an invention for "cannot instruct"; the language can state none of the three as content beside `norm-defaults@0`, so only candidate text separates them.
* **F1 (still true).** `readings@1` content cannot sit beside `norm-defaults@0`; demonstration companions (`readings/s1.ve.md`, `readings/all-default.ve.md`) stay outside every claim.
* Others as in `FEATURE-REVIEW-prev-20261004T1800Z.md` (F2, F4, F6, F10–F13, F15–F21): unchanged.

## Missing features, in order of what they would unlock here (ledger tally `UNFORMALISED`)

norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50 (stale), counting 31, modality/belief 24, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1. Unchanged.

1. **`readings@1` content beside `norm-defaults@0`** (F1).
2. **Typed modals with action complements** (F22) and **graded normative force**.
3. **Per-choice semantics (S2)** and **cross-sentence scope** (F14); the certified form of the `decision_only_sound` finding.
4. Binary relation wording (F6, F19), nested-list English (F20).
