# UDHR pilot under readings with their own vocabulary (readings-defaults RD-5)

Run 20261006T1800Z's translation (`usecases/udhr-pilot/run-20261006T1800Z at bd6c7ab2`), migrated by `migrate.py` and measured by `measure.py` at commit `ae7fa229` (the tree's `ve`, `lean`, `rust` and `tools` clean: true), on a 32-CPU host. Every number below is rendered from `metrics.json` by `summary.py`; the three marked *recorded* are copied from the run (usecases/udhr-pilot/run-20261006T1800Z/metrics.json and verdict.json at bd6c7ab2).

## What changed

- 22 of 49 reading sets now carry their companions inline: each is a sentence checked by itself, in the terms its readings declare (E31). The other 27 stay on W2 as they were (content null, no companions), listed below with Lean's text; they are not decided.
- Lean admits the migrated document: premises `model`, conflict `CONFLICT-FREE`, over 23 components (the main case and 22 companion sets). Before, the premises were UNKNOWN (*recorded* UNKNOWN) and there was no readings answer.
- **Lean-decided share** (spec 1.10, plan 3.9): 0 bytes (0.00%) before, 2111 of 10916 bytes (19.34%) after, in 23 units Lean lists as decided.
- Claimed covered bytes 4792 (43.90%) and audit-verified 2543 (23.30%) are *recorded* and unchanged: no unit changed status (bytes by status before {"CHECKED": 57, "LABELLED": 535, "OPEN": 4200, "UNFORMALISED": 6124}, after {"CHECKED": 57, "LABELLED": 535, "OPEN": 4200, "UNFORMALISED": 6124}). The next audit decides on the migrated units.

## What the share does and does not say

- Every sentence with readings was checked by itself (E31). The share says nothing about whether two sentences' readings fit together.
- The largest choice document holds 4 rules: 1 written rule and the generated rules of its unspecified predicates (counted from Lean's `norm-defaults-elaborate` of every choice). The share tool's `max_choice_rules` is null, because Lean's answer does not carry that count.
- 1886 of the 2111 decided bytes belong to units whose every reading's companion the run had already checked as a document of its own.
- A rule checked by itself is CONFLICT-FREE by construction: a single rule cannot contradict another. This says nothing of a reading checked with the document's other rules; Lean's answer decides that.
- Most UDHR readings hold one rule, and their companions had already passed their checks as separate documents. So the move from 0 measures those checks routed into Lean inside the document, not new assurance.

## Measurements

| Measure | Before (as committed) | After (migrated) |
|---|---|---|
| Load (`load_document`) | 1.1 s wall, 0.6 s CPU (load 52.9) | 2.0 s wall, 1.9 s CPU (load 52.9) |
| Check (`check_document`) | 0.9 s wall, 0.6 s CPU (load 52.9) | 22.0 s wall, 17.5 s CPU (load 52.2) |
| Render (`render_document`) | 1.0 s wall, 0.7 s CPU (load 52.9) | 3.1 s wall, 2.5 s CPU (load 50.4) |
| Document bytes | 287,435 | 374,535 (limit 4,000,000) |
| Components; regulated predicates per component (max); readings per component (max) | — | 23; 3 (limit 64); 4 (limit 64) |
| Compatible choices per component (max) | — | 4 (limit 64) |
| Premises verdict | UNKNOWN | model |
| Conflict verdict | — | CONFLICT-FREE |
| Lean-decided bytes and share | 0 (0.00%) | 2111 (19.34%) |
| Maximum rules in one choice's document; decided bytes already checked outside | — | 4; 1886 |
| Claimed covered; audit-verified | 4,792; 2,543 (*recorded*) | unchanged |
| Sets admitted with every pair separated; unseparated pairs | — | 22 (30 situations); 0 |
| Sets not migrated ("needs one vocabulary", E1) | — | 27 |

## Checks

- Status witnesses in the components (`readings-choice`, inner `norm-defaults-status`): 152 of 152 equal to the recorded `witnesses.json`.
- The 156 companions re-checked alone: 156 with premises `model`; their witnesses through the norm-defaults route: 459 of 459 equal to the recorded ones.
- Pair sentences of the migrated sets: E19 19, E24 15. A pair separated on a plain regulated predicate (an entitlement reading: "Everyone has the right to …") gets E24, "These two readings differ in a checked situation that VE cannot yet show in words.": E19 words duties and permissions only. Before this batch such a pair made the whole report `CheckerUnavailable` (`ve/readings_route.py`, the batch's one product change).

## Observations (follow-ups, not changed here)

- The English of a shown situation names elements of different sorts alike ("e0 is a person; e0 is a State"), which a reader can take for one entity.
- A plain predicate without a verbalisation in the companion's frame reads as 'is classified as "resources_allow"'; the pilot's companions give some plain predicates no verbalisation.
- E24 says that a separation was checked but not what it is; an E19 sentence for plain predicates needs new wording and the W7 gate.
- 27 sets wait for one vocabulary (E1): most declare the duty over `state` in one reading and over `bearer` in another. Re-translating them onto one sort is a pilot task.

## Queries (spec 8.6), answers verbatim

### "every State must recognise each person everywhere as a person before the law" (sentence `u029`)

Expected SOME; Lean answered **SOME** (43.7 s wall, load 57.4; `answers/u029-recognise.json`).

> Each open sentence below was checked by itself, under each of its readings.
> Sentence 34 was checked by itself, with the terms its readings declare; VE did not check it together with the other sentences.
> Read sentence 34 as *Every State must recognise each person everywhere as a person before the law*: the conclusion follows: *For every State, for every person, that State must recognise that person everywhere as a person before the law.*
> Read sentence 34 as *Every person is classified as "has_the_right_to_recognition_as_a_person"*: the conclusion does not follow. It fails here: e0 is a person; e0 is a State. Here the text does not say whether e0 must recognise e0 everywhere as a person before the law; this situation answers 'no'.

### "every State whose organization and resources allow it must secure each person social security" (sentence `u081`)

Expected SOME; Lean answered **SOME** (74.6 s wall, load 70.2; `answers/u081-secure.json`).

> Each open sentence below was checked by itself, under each of its readings.
> Sentence 90 was checked by itself, with the terms its readings declare; VE did not check it together with the other sentences.
> Read sentence 90 as *Every State must secure each person social security*: the conclusion follows: *For every State that is classified as "resources_allow", for every person, that State must secure that person social security.*
> Read sentence 90 as *Every person is classified as "has_the_right_to_social_security"*: the conclusion does not follow. It fails here: e0 is a person; e0 is a State; e0 is classified as "resources_allow". Here the text does not say whether e0 must secure e0 social security; this situation answers 'no'.

### "every State whose organization and resources allow it must secure each person social security" (sentence `u081`, `--under rs_u081:2`)

Expected ALL; Lean answered **ALL** (52.4 s wall, load 78.7; `answers/u081-secure-under-2.json`).

> Each open sentence below was checked by itself, under each of its readings.
> Sentence 90 was checked by itself, with the terms its readings declare; VE did not check it together with the other sentences.
> Read sentence 90 as *Every State must secure each person social security, if that State is classified as "resources_allow"*: the conclusion follows: *For every State that is classified as "resources_allow", for every person, that State must secure that person social security.*

### "no State must secure any person social security" (sentence `u081`)

Expected NONE; Lean answered **NONE** (67.7 s wall, load 86.5; `answers/u081-none.json`).

> Each open sentence below was checked by itself, under each of its readings.
> Sentence 90 was checked by itself, with the terms its readings declare; VE did not check it together with the other sentences.
> Read sentence 90 as *Every person is classified as "has_the_right_to_social_security"*: the conclusion does not follow. It fails here: e0 is a person; e0 is a State. Here the text does not say whether e0 must secure e0 social security; this situation answers 'yes'.
> Read sentence 90 as *Every State must secure each person social security*: the conclusion does not follow. It fails here: e0 is a person; e0 is a State.
> Read sentence 90 as *Every State must secure each person social security, if that State is classified as "resources_allow"*: the conclusion does not follow. It fails here: e0 is a person; e0 is a State; e0 is classified as "resources_allow".

## Sets not migrated

| Set | Lean's text |
|---|---|
| `rs_u020` | InvalidInput: readings rs_u020@2:0 and rs_u020@2:1 declare avoid_distinction_by_country_status_required differently |
| `rs_u022a` | InvalidInput: readings rs_u022a@3:1 and rs_u022a@3:2 declare avoid_life_required differently |
| `rs_u022b` | InvalidInput: readings rs_u022b@3:1 and rs_u022b@3:2 declare avoid_liberty_required differently |
| `rs_u022c` | InvalidInput: readings rs_u022c@3:1 and rs_u022c@3:2 declare avoid_security_of_person_required differently |
| `rs_u024` | InvalidInput: readings rs_u024@2:0 and rs_u024@2:1 declare avoid_holding_in_slavery_or_servitude_required differently |
| `rs_u027` | InvalidInput: readings rs_u027@2:0 and rs_u027@2:1 declare avoid_torture_or_ill_treatment_required differently |
| `rs_u037` | InvalidInput: readings rs_u037@2:0 and rs_u037@2:1 declare avoid_arbitrary_arrest_detention_exile_required differently |
| `rs_u045a` | InvalidInput: readings rs_u045a@2:0 and rs_u045a@2:1 declare avoid_arbitrary_interference_required differently |
| `rs_u045b` | InvalidInput: readings rs_u045b@2:0 and rs_u045b@2:1 declare avoid_attacks_upon_honour_and_reputation_required differently |
| `rs_u048` | InvalidInput: readings rs_u048@5:1 and rs_u048@5:2 declare avoid_denying_right_u048_required differently |
| `rs_u049` | InvalidInput: readings rs_u049@3:1 and rs_u049@3:3 declare avoid_leave_and_return_required differently |
| `rs_u051` | InvalidInput: readings rs_u051@5:2 and rs_u051@5:3 declare avoid_barring_asylum_required differently |
| `rs_u052` | InvalidInput: readings rs_u052@4:0 and rs_u052@4:1 declare arises_from_acts_contrary_to_un differently |
| `rs_u055` | InvalidInput: readings rs_u055@2:0 and rs_u055@2:1 declare avoid_loss_of_nationality_required differently |
| `rs_u059` | InvalidInput: readings rs_u059@2:0 and rs_u059@2:1 declare avoid_marriage_without_free_and_full_consent_required differently |
| `rs_u063` | InvalidInput: readings rs_u063@5:1 and rs_u063@5:2 declare avoid_denying_right_u063_required differently |
| `rs_u064` | InvalidInput: readings rs_u064@2:0 and rs_u064@2:1 declare avoid_arbitrary_deprivation_of_property_required differently |
| `rs_u066` | InvalidInput: readings rs_u066@5:1 and rs_u066@5:2 declare avoid_thought_conscience_religion_required differently |
| `rs_u070` | InvalidInput: readings rs_u070@3:1 and rs_u070@3:2 declare avoid_opinion_and_expression_required differently |
| `rs_u073` | InvalidInput: readings rs_u073@5:1 and rs_u073@5:2 declare avoid_assembly_and_association_required differently |
| `rs_u084a` | InvalidInput: readings rs_u084a@5:1 and rs_u084a@5:2 declare avoid_work_required differently |
| `rs_u084b` | InvalidInput: readings rs_u084b@3:1 and rs_u084b@3:2 declare avoid_free_choice_of_employment_required differently |
| `rs_u087` | InvalidInput: readings rs_u087@3:0 and rs_u087@3:1 declare avoid_trade_unions_required differently |
| `rs_u096` | InvalidInput: readings rs_u096@3:1 and rs_u096@3:2 declare avoid_education_required differently |
| `rs_u105a` | InvalidInput: readings rs_u105a@5:1 and rs_u105a@5:2 declare avoid_cultural_life_required differently |
| `rs_u105b` | InvalidInput: readings rs_u105b@3:1 and rs_u105b@3:2 declare avoid_enjoyment_of_the_arts_required differently |
| `rs_u112` | InvalidInput: readings rs_u112@5:0 and rs_u112@5:1 declare exercise_contrary_to_un differently |

## Unseparated pairs

None.

## Copied declarations (asserted readings given a companion from the main frame)

- `rs_u052:case_excluded`: sort prosecution, predicate arises_from_acts_contrary_to_un, predicate arises_from_non_political_crime, predicate asylum_right_covers_case
- `rs_u112:exercise_unprotected`: sort exercise, predicate exercise_contrary_to_un, predicate exercise_of_declared_right, predicate right_protects_exercise
- `rs_u114:no_implied_right`: sort bearer, predicate declaration_implies_destructive_right

## Sets on W2 in the main component (Lean's UNKNOWN)

`rs_u020`, `rs_u022a`, `rs_u022b`, `rs_u022c`, `rs_u024`, `rs_u027`, `rs_u037`, `rs_u045a`, `rs_u045b`, `rs_u048`, `rs_u049`, `rs_u051`, `rs_u052`, `rs_u055`, `rs_u059`, `rs_u063`, `rs_u064`, `rs_u066`, `rs_u070`, `rs_u073`, `rs_u084a`, `rs_u084b`, `rs_u087`, `rs_u096`, `rs_u105a`, `rs_u105b`, `rs_u112`
