# Feature review: what `ve-green-unspecified-uc` adds over `ve-green-risk-c5`

Language at this run: `ve.core@0.2`, profiles `documents@1`, `norms@0`, `norm-defaults@0`, `relational-fol@0` for the main document and the
strict companion; `soft-norms@0` (without `norm-defaults@0`) for the defeasible companion. Source: the pinned 184,893-byte constitution,
unchanged (SHA-256 `fa10ed48…50dd`, `../source/SOURCE.md`). Start point: the translation of run `20261001T1800Z`; 1,105 of its 1,127 ledger
entries are identical, 22 are changed or replaced and 8 sub-units are added (`metrics.json`, `changes_against_previous_run`).

## Merged since `ve-green-risk-c5`

`git diff ve-green-risk-c5..ve-green-unspecified-uc -- ve/` touches 15 files; **only `norm-defaults@0` changes what can be written**
(`ve/norm_defaults.py`, `ve/norm_defaults_english.py`, `ve/norm_defaults_route.py`, plus small hooks in `ve/document.py`, `ve/norms.py`,
`ve/norm_english.py`, `ve/profiles.py`). The rest of the tag range is use cases (agent-policy, asimov-extended, safety-framework, BlueDot)
and Lean/documentation work. `ve/discourse.py`, `ve/risk.py`, `ve/rights.py` are unchanged, so the discourse, risk and rights probes are carried
from the previous run (copied into `probes/`, not re-run).

| Merged | What it is | Used here |
|---|---|---|
| `norm-defaults@0`: the completion `unspecified` for a regulated predicate | Where no rule decides, the text is silent: VE reports UNDECIDED, not "not required"/"not permitted". Direct semantics drops W1's third clause; `fill` adds one synthetic lowest-priority rule per unspecified predicate. Statuses per point: SETTLED yes/no, UNDECIDED, UNKNOWN; conflicts can be latent. | **Yes: 17 regulated predicates, every completion `unspecified`.** |
| English legend for the profile (`legend`, `silence_sentence`) | "When nothing else in the text decides, the text does not say whether a <noun> may <act>." | Printed in `rendered.md` and the ledger. |

## What it let this run do (each measured against the previous run)

1. **The prohibitions are prohibitions again.** Last run the seven hard constraints, `u0156.s03` and `u0125.s04.p2` were duties to avoid
   the act, completed with deny ("not required"), because a permission predicate needed a default that the source never states. Now each is a
   permission predicate with a negative rule, scoped to instances of Claude, completion `unspecified`. VE's own verdicts
   (`probes/unspecified-probe.json`): where the case atom holds, "SETTLED no" (Claude may not); where it does not, "UNDECIDED" (the text does not
   say). Nothing is made permitted or forbidden for another party. Evidence of silence: 10 of the 17 predicates have a reachable gap in the strict companion
   (`gaps: reachable`), 5 have none (a rule with guard `top` decides every case) and 2 are unknown (`operator_input_permitted`, `operator_instruction_following_required`: no search result within the budget).
2. **Operator and user permissions, previously blocked on "defaults".** Four ledger units were `UNFORMALISED[defaults]` because "Operators can /
   cannot instruct Claude to …" is a permission for one named party, which needed an invented completion for every other case. They are now covered as
   reading sets whose permission reading is elaborated as strict rules: `u0062.s01` (3 rules), `u0123.s01` first clause (1 rule), `u0123.s02` (5 rules),
   `u0123.s03` (6 prohibitions). The `u0166.s04` clause "cannot be unlocked by any operator or user" (`UNFORMALISED[norms]` before) is two rules.
   Bytes newly covered: 85 + 180 + 348 + 351 + 45 = **1,009**.
3. **A finding VE made on its own.** In the strict companion VE returns a checked `CONFLICT` (kind: settled) for an operator input that is both a custom-persona
   role-play instruction (permitted by `u0123.s02`) and an instruction to claim to be human when sincerely asked (forbidden by `u0123.s03`). The source
   gives no precedence between the lists, and none was written; a whole-document proof of conflict-freeness is `UNKNOWN` (tableau budget).
4. **No default is invented anywhere in the main document and strict companion** (`metrics.json`, `no_invented_permissions`): 12 permission and 5 obligation
   predicates, all `unspecified`, first arguments are the sorts the source names (instances of Claude, operators, users).

## Findings still true at this tag

* **F1 (changed). A completion no longer has to be chosen, but only on the strict route.** `unspecified` exists, so the audit's first ask is closed
  for strict rules. It cannot reach defeasible ones: a document with both `norm-defaults@0` and `soft-norms@0` is rejected (`UnsupportedProfile: norm-defaults@0
  documents on the soft and rights routes await the Lean route`, `metrics.json`, `profile_combination_probe`). So this run's defeasible companion
  (`readings/all-default.ve.md`) keeps last run's deny completions and duty-to-avoid forms for `u0156.s03` and `u0125.s04.p2`, and the main document dropped
  `soft-norms@0`. Consequence: `u0073.s05` ("should generally comply", a defeasible duty with three open conditions) is no longer a content-bearing unit
  in the main document but a one-candidate reading set.
* **F2. A norm reading candidate cannot carry content** (unchanged). All 13 reading sets have candidates recorded without content; the main premise status is
  still UNKNOWN ("non-assertion reading elaboration pending"); the strict companion gets a model because it resolves every set the strict route can.
* **F4. Act phrases** are at most 80 characters, letters, `'` and `-` only, no `or`, `and`, `is`, `not`, `for`, `if`, `no`, `must`, unique within a role.
  The hard-constraint act phrases remain labels ("do the weapons uplift in a situation"); the source's words are in the case atom.
* **F6. English for base predicates is generic** (the rendered rule says `classified as "<name>"`; the declared wording is printed on a "Classifications
  named above" line of `rendered.md`). 31 of 31 strict rules parse back; 6 of 8 defeasible rules do (`comply-operator-prompt`, `follow-operator-in-conflict` do not).
* **F10. Composition.** Probe on the strict companion (`profile_combination_probe`): `time@0`, `definitions@0`, `data@0` pass the document check; `soft-norms@0`,
  `closure@0`, `order@0` (FOL only), `reports@0` ("with norms@0 layers"), `alternatives@0` ("not implemented with norm-defaults@0"), `rights@0` ("requires
  soft-norms@0"), `risk@0` ("requires alternatives@0"), `speech-acts@0`, `ve.discourse@1` (`UnrecordedSlot`) are rejected.
* **F11 (new). The `defaults` tag is stale.** 54 units carried `missing_feature: defaults` in the ledger; only four needed a completion (above). Most of
  the other 50 use the word "default" for Claude's behaviour absent instruction (u0152, u0062.s02) or mean "generally" / "in most cases" (u0031, u0128), which is
  not a completion. They are left tagged as before (this run only upgrades what `unspecified` can express); the tally of 50 overstates what completions block.
* **F12 (new). Sorts of parties.** `operator`, `operator_input`, `hard_constraint` are bare sorts: "who is an operator" (the source defines operators and users by role, not by a fact the language can test) and "the seven hard constraints" are not tied to the rules by name. A relation from the sort `hard_constraint` to the seven rules would be needed to
  say that `u0166.s04` is about exactly them.

## Missing features, in order of what they would unlock here (ledger tally `UNFORMALISED`)

norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50 (stale, see F11), counting 31, modality/belief 24, attribution 12, time 9,
`other:open-list` 1.

1. **Unspecified together with soft norms** (F1): defeasible "should" statements are the bulk of the 669, and they need the completion the strict route no longer does.
2. **Norm reading candidates that hold their rules** (F2): 13 sets are recorded without content; elaboration happens only in companions.
3. **Norms with attribution, causation, quantities, discourse** (tally above): "should … because …" is the dominant shape in the source.
4. **Roles and entitlements** (F12; `u0046.s03` "things users are entitled to that operators cannot override" is untouched: `rights@0` needs `soft-norms@0`).
