# Risk wording probe: items (draft, not sealed)

The reader-comprehension items for the wording probe of `docs/spec/risk-PLAN.md` section 2.6. The item writer wrote
them from 2.1, 2.5 and the legend sentences of 9.1 only. **Status: not checked by the second reviewer, not run, not
sealed.** There is no manifest yet, and until sealing any item may be dropped.

## Contents

`items.json` holds 62 items: 4 for each of the 15 scored constructs (c1, c2, c3a, c3b, c4 to c14) and 2 unscored
`prevents` controls. Each item object has:

| Field | Meaning |
|---|---|
| `id`, `construct` | `c3b-2`, `ctl-1`, … ; controls have construct `control-prevents` |
| `domain`, `setting` | `agent-operations` or `non-computer`; the setting is agent operations, delivery robot or clinic |
| `scored` | `false` for the two controls |
| `conditions` | `["L","C"]`, except c13, which is `["L"]` (2.6 Conditions) |
| `separates_rival` | whether the rival reading gives a different answer from the key |
| `counter_world_knowledge` | whether the declarations contradict what world knowledge suggests |
| `legend_text` | the L-condition legend, one line per `\n` |
| `situation_text` | what every reader sees: chooser, actions, declarations and target sentence (rules on their own lines) |
| `target_sentence` | the sentence under test (for c13, the fulfilment legend line) |
| `question`, `options` | the question and its 3 or 4 labelled options; exactly one option is "The text does not say." |
| `key`, `critical` | the correct label, and the labels the rival reading selects (empty only for c8-4) |
| `one_reading`, `rival_reading` | the construct's one reading and the rival reading, from the 2.6 table |
| `rationale` | why the key follows from the one reading, and why each critical option follows from the rival |
| `same_situation_as`, `parallel_to`, `fulfilment_body` | c3b items reuse the c3a situations; controls mirror c12-1 and c12-2; c13 items name `avoids` or `excludes` |

Option labels are identifiers only. The runner shuffles the displayed order with the recorded seed. The fixed
instruction (2.6 Readers) asks for one option and a one-sentence reason.

## Counts

| Construct | Items | Separating | Agent-ops / non-computer | Against world knowledge |
|---|---|---|---|---|
| c1, c4 to c7, c9 to c14 (each) | 4 | 4 | 2 / 2 | 1 |
| c2, c3a, c3b (each) | 4 | 4 | 2 / 2 | 2 |
| c8 | 4 | 3 | 2 / 2 | 2 |
| `prevents` controls | 2 | 2 | 1 / 1 | 0 |
| **Total** | **62** | **61** | **31 / 31** | |

c8-4 is the only item that does not separate. It tests the bare form `<h> is <class>`, where the rival
("exactly `<class>`" for "or worse") does not apply, so it has no critical option. Answers per 2.6: 60 scored items
give 240 in L and 224 in C (c13 is L only), and the controls add 16, for 480 in all.

## How the legends were built

- Lines that 9.1 contains are copied verbatim: the choice line, `might lead to`, `cannot lead to`, `leads to`, the
  worst-case line and the default permission.
- Lines for words that 9.1 does not use are written in 9.1's style from the 2.1 and 2.5 paraphrases: `might not lead to`,
  `if`, `unless`, `exactly when`, `certainly leads to`, `or worse`, `avoidable`, `allows`, `might prevent`, and the
  `avoids` and `excludes` bodies (the 2.5 template "A `<chooser>` `<act>` by taking an action that …", with `<act>` =
  "prevents a harm").
- The first risk line in a legend spells out "the declared estimates, conditions and statements"; later lines say
  "they", as 9.1 does.
- A legend covers only the words in the situation text, plus the words its own paraphrases use (for example, `avoidable`
  brings in `might not lead to`). The choice line is always included, and the default-permission line appears only where
  rules appear (c13, c14).
- Severity orders and class assignments are declarations, so they are in the situation text and C readers see them
  too. Only the meaning lines differ between L and C.
- Bare `prevents` gets no legend line, because risk environments reject it.
- 9.1's `unexamined` line is left out. It is block configuration, not the meaning of a word.

## Notes for the checking reviewer

1. **Undeclared cells.** No key rests on whether an undeclared action–harm cell counts as possible. Where a question
   needs a cell settled, the item declares it.
2. **"The text does not say" as a critical option** (c5-2, c6-2, c6-3, c6-4, c7-1, c7-2, c7-3, c9-3, c9-4). It is
   marked critical wherever it is the rival reading's own answer.
3. **c12-2, c12-4 and ctl-2** declare a condition under which the action leads to the harm. That condition contradicts
   the guarantee rival, so a rival reader may notice the conflict. The items are kept because this is the realistic IDE
   case, and c12-1 and c12-3 test the construct without it.
4. **Rule sentences** in c13 and c14 follow the shape of the 9.1 rules. This goes slightly beyond the three permitted
   sources, but the constructs need "must prevent", "must not" and "may" rules.
5. **c9-3 and c9-4** need one inference: the harm named is `severe`, the top class, so no worst case can be more severe
   than it.
6. **Controls.** The key is the risk@0 meaning of `prevents(a, h)` (2.5: its canonical form is `might prevent`). The
   critical option is the ordinary-English reading that 2.1 gives as the reason for rejecting it.

## Next steps (2.6 Sealing)

The second plan reviewer checks each key against the one reading and each critical option against the rival reading,
and drops any item the two reviewers disagree on. Then prompts, seeds, the reader list and a SHA-256 manifest are
committed here, before any run. Nothing is edited after sealing. Results go to `RESULTS.md`, labelled "proxy; human
readability unmeasured".
