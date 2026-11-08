# ci-5 report: `speech-acts@0` with `acts@0`, simple acts only

Status: all six deliverables built; awaiting review. HEAD: the final commit of feature/ci-5 (`git log -1`).
Changed: AR-10's `actsRefuses` admits `speech-acts@0`, `gate_acts` revised as spec section 9, the speech allowlist gains
`acts@0`, `command_act_simple` proved; the plan's three fixtures read as one simple act each, "Click Check and save." is
refused at declaration. No signature is reserved; every DELTA row cites a DRI decision or R12/R16.
Open: FOLLOW-UP ci-5-for-slot. Size over the ~600 cap, kept whole: SIGNED, reviews/dri-decisions-20261108-ci-5-size.md item 1.

Plan and spec: `9a12df17a` on design/commands-imperatives, PLAN "CI-5" (lines 840-922) and section 9; spec section 9
(lines 1276-1349), S28 (line 71), section 14's row (line 1653), checklist item 8 (line 1696). Statement gate: passed
(reviews/dri-decisions-20261102-ci-0.md item 1). Gate contract: SIGNED, reviews/dri-decisions-20261028-commands-imperatives.md
item 3(b); verdict changes item 2(b); builder points reviews/dri-decisions-20261105-ci-5.md items 1-3.

## Deliverables

| # | Task line | Delivered | Evidence |
|---|---|---|---|
| 1 | `Acts/Lexical.lean`: `joinFree fx act` (the `joinWords` table, *for* included) | `VE.Acts.Lexical.joinFree` exactly as spec section 9; `check_joinFree` (what `check` accepts is `joinFree`). `check` is NOT changed to call it: DRI 20261105 item 2 (task vs spec S27: main already factored `joinCheck`, "CI-5 adds no second join test"). Every AP-1 answer is untouched because `check` is untouched. | 336b0be6d; `#guard`s `lean/VE/Commands/Examples.lean:376-379` (the table: `and`, `or`, `nor`, `for`, comma, a lexing fault) |
| 2 | `SpeechActs/Wire.lean`: `profileGate₀`, `decodeSpeechEnvironmentFull₀` kept; `allowlist` gains `acts@0`; `profileGate_mono`, `decode_without_acts`, `decode_acts_compatible`; re-check `today_speech` | All, statements as spec section 9 (`allowlist` = `["acts@0", "norms@0", "relational-fol@0", "speech-acts@0"]`). Both gates are `profileGateOf` over an allowlist and both decoders `decodeEnvironmentWith` over a gate, so the merged definitions are kept by value. `today_speech`: statement unchanged, proof unfolds the new names. Plus `checkActsBlock` (DRI 20261105 item 3) and `decoded_act_simple`. | 336b0be6d, 3668563e0; full `lake build` (1311 jobs, "Build completed successfully"); `python3 lean/audit.py` "PASS: 780 source files; 8655 named theorem declarations audited" |
| 3 | `Compose/Dispatch.lean`: `actsRefuses` drops `speech-acts@0`; `rowChecks_erase`, `todayGate_base` re-proved unchanged; `gate_acts` revised; the Examples count `#guard` (6) and row; ActsExamples' pin | All. `rowChecks_erase` and `todayGate_base` needed no proof edit (their `simp` takes the shorter list); `gate_acts` gains one `by_cases` on `speech-acts@0`. | 343a7a0ae; `lean/VE/Compose/Examples.lean:272-283`; `lean/VE/Service/ActsExamples.lean:203-205, 231-234, 320-321` |
| 4 | `Commands/`: `command_act_simple` | `VE.Commands.command_act_simple` (`lean/VE/Commands/Read.lean`), statement as spec section 9, from `readCommand_one_iff`, `candidate_reads_back` and `decoded_act_simple`. No `JoinedCommandAct` reader refusal (task). | 343a7a0ae |
| 5 | `docs/spec/act-phrases.md` 4.4 revised | 4.4's gate text only: the `gate_acts` statement and the paragraph on the speech route. | 316b72a91 |
| 6 | Fixtures; `ve/profile_table.json` regenerated | The plan's three (`Examples.lean:363`, `RunExamples.lean` CI-5 section, through the mode); "Click Check and save." refused at declaration (`Examples.lean:385`, `RunExamples.lean`); with `acts@0` off every row unchanged (`Examples.lean:411-422`: the merged and new decoders agree on `E_web`, `webWith none definitesWeb` and the acts-off environment; `decode_without_acts` for every list); the existing act-phrases tests untouched (no file under `tests/test_acts_*` or `lean/VE/Acts/*Examples*` changed: `git diff --stat main...HEAD`). DRI 20261105 conditions 1(a)-(c) at `Examples.lean:393-406`, 3(a)-(b) at `:477-479`. Limits at `:450-458`. `ve/profile_table.json` by `regen_generated.py --write`. | 343a7a0ae, 316b72a91, 80cb1088e, ebe192d58 |

Also: the A/B of DRI item 2(b), `AB.json` (made by `ab.py` on the base and on HEAD, merged with `--merge`): 9 rows, 4 b1,
2 b2, 3 unchanged with `acts@0` off, plus 6 acts-off rows identical. `tests/test_speech_acts_acts0.py` pins each b1 row to
its Lean fixture and to a live answer, and each b2 row to a live refusal (item 2(b)'s condition).

## Deviations (each signed)

- `check` does not call `joinFree`; `joinFree` is its Bool view, linked by `check_joinFree` (DRI 20261105 item 2).
- "Choose declared kinds of things for the new word." reads with the whole of "declared kinds of things for the new word"
  as one fixed phrase and args `[]`: "the new word" is not bound to a slot, unlike the plan's section 9 fixture note. A
  frame for `choose` with the marker `for` does not admit the slot form (`Examples.lean:401`), and "the old word" does not
  read (`:406`). DRI 20261105 item 1; FOLLOW-UP ci-5-for-slot.
- `checkActsBlock` refuses (`InvalidInput: environment acts block`) a hand-built tree whose `vocabulary` lookup differs
  from the value `stripSpeech` rebuilds, instead of a hypothesis on `command_act_simple` (DRI 20261105 item 3). What is
  shown of parsed trees: `E_acts` read back through `Lean.Json.parse` decodes (`:479`); no theorem states it for every
  parsed tree.
- Removed before merge, never on main: `test_the_ab_lists_a_class_for_every_changed_row` re-read only the saved A/B, a
  permanent report test (D4); the b1/b2 pins stay.

## Seeded bugs (Lean; no Python or Rust product code changed)

Each was planted in the file named, the named check failed, and the file was restored (`git checkout`, then
`lake build VE.Commands.Examples VE.Compose.Examples VE.Service.ActsExamples`: "Build completed successfully"). Details in
`mutants.json`.

| id | File | Mutation | Fails |
|---|---|---|---|
| S1 (plan's) | `lean/VE/SpeechActs/Wire.lean` | `allowlist` also admits `soft-norms@0` | the proof of `decode_without_acts` (`Wire.lean:533`, unsolved goal `p = "soft-norms@0" → p ∈ allowlist₀`); with that proof stubbed, the `#guard` `lean/VE/Commands/Examples.lean:424` (SA's fixture φ: `speech-acts@0 with soft-norms@0`) |
| S2 (task's) | `lean/VE/Acts/Lexical.lean` | `joinWords` drops `for` | `#guard`s `Examples.lean:377` (the `joinFree` table: `{0} pay for {1}`), `:393` and `:401` (the `chooseFor` frame fixtures), and 6 more in the CI-5 section |
| S3 (task's) | `lean/VE/Compose/Dispatch.lean` | `actsRefuses` drops `rights@0` besides `speech-acts@0` | the proof of `gate_acts` (`Dispatch.lean:1268`); with that proof stubbed, the count `#guard` `lean/VE/Compose/Examples.lean:272` (`actsRefuses.length == 6`) |
| S4 (DRI 20261105 3(c)) | `lean/VE/SpeechActs/Wire.lean` | `checkActsBlock` never throws | the proof of `decoded_act_simple` (`Wire.lean:592`); with that proof stubbed, the `#guard` `Examples.lean:477` (`twoVocabularies` refused) |

## Trust

`uv run python tools/trust_map.py --check`: "against e9a6ec8d5938: K +0, S +0, D +40, G +1, tied +0, unclassified +0,
trusted +41" (`VE/SpeechActs/Wire.lean` +31, `VE/Acts/Lexical.lean` +9, `VE/Compose/Dispatch.lean` +1), then "PASS: K, S
and untied [V] within e9a6ec8d5938 and the allowances introduced since" with the allowance in `docs/trust-baseline.json`
(SIGNED by standing ruling R16, within 150, no K growth). FOLLOW-UPS.md "## ci-5": the ties pass. The assurance manifest
re-pins `Acts/Lexical.lean` (16-161 -> 16-170, `joinFree` added to its declarations) and `SpeechActs/Wire.lean` (whole
file, 1322 lines); `uv run pytest -q tests/test_assurance_manifest.py`: "139 passed".

R16's mutants: TRUST-MUTANTS (filled below when the run ends).

## Size

`git diff --numstat $(git merge-base HEAD main)`, generated files excluded: 844 lines (813 added, 31 removed):
`SpeechActs/Wire.lean` +326/-15 (about 300 are the statement gate's proofs and their lemmas), `Commands/Examples.lean`
+160, `tests/test_speech_acts_acts0.py` +108, `ab.py` +109 and `AB.json` +11, `Acts/Lexical.lean` +42, the rest +57/-16.
Over the ~600 cap. The six deliverables were built before the size was measured, and the fixtures past the task's seam
(after (3)) carry conditions of item 3(b) (the counterexample) and item 2(b) (the A/B and its pin). Asked the DRI
(inbox/dri/20261108T102318Z-ci-5-2509481.md): SIGNED, keep ci-5 whole, no cut to ci-5b, no further growth beyond review
fixes and this section (reviews/dri-decisions-20261108-ci-5-size.md item 1). With REPORT.md, DELTA.md and mutants.json
the count by the task's rule is FINAL-COUNT.

## Tests

SELECTED (filled below when the run ends).

While iterating: `uv run pytest -q tests/test_speech_acts_acts0.py`: "11 passed"; `tests/test_assurance_manifest.py`:
"139 passed"; `uv run python tools/regen_generated.py --write`: rc 0. Not run here: the full gate (the chain runs it).

## Evaluators and limits

CI-5 adds no mode and no evaluator. The decoder reads the fixed phrases once in W1's decoder and twice more in
`checkActsBlock` (the submitted and the stripped tree); each read is bounded by `Acts.Lexical.maxPhrases` (128) and
charged before the phrases are walked: 129 phrases end with "ResourceLimit: more than 128 fixed phrases"
(`Examples.lean:451`), a 401-byte act with "ResourceLimit: act phrase for click_required is over 400 bytes" (`:453`),
65 regulated predicates with "ResourceLimit: regulated predicates" (`:457`), and the largest accepted request (64 acts
over 128 phrases) decodes and reads (`:456`, `:458`; 125 + 3 phrases and a 400-byte act decode, `:450`, `:452`).

## Pilot bytes

Web fixture: +3 segments, about 125 B (the plan's estimate; nothing is claimed before a pilot audit).

## In-flight overlap

feature/et-4b (unmerged at 2026-11-08) also edits `lean/VE/Compose/Dispatch.lean`, `lean/VE/Compose/Examples.lean` and
`ve/profile_table.json`. This branch changes only `actsRefuses`, `gate_acts` and `today_speech` there; rebase after et-4b
merges (the feed waits for that path). Main has not moved since the merge base `e9a6ec8d5`.

## Next item

PC-6 (profile composition), after pc-revise-20261104 and sn-wire-pc6.

## Spec re-read

- `gate_acts` against commands-imperatives.md:1281-1284 (section 9): identical conclusion, hypotheses and names.
- `decode_acts_compatible` against :1288-1291; `profileGate_mono` against :1294-1295; `decode_without_acts` against
  :1298-1300: identical.
- `joinFree` against :1306-1311: identical body; `check` not changed (:1305 "CI-5 adds no second join test").
- `command_act_simple` against :1315-1318: identical; no reader refusal (:1323-1324).
- `allowlist` against :1321-1322: `["acts@0", "norms@0", "relational-fol@0", "speech-acts@0"]`, code point order.
- `actsRefuses` against :1334-1336: only `speech-acts@0` removed; `closure@0`, `order@0`, `ve.discourse@1` kept.
- Examples count 7 -> 6, the row at Examples:267 removed, ActsExamples pin re-pinned (:1331-1334).

## Self-review against BUILDER-CHECKLIST

SELF-REVIEW (filled below).
