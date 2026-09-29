# Risk wording probe: items (sealed)

The reader-comprehension items for the wording probe of `docs/spec/risk-PLAN.md` section 2.6. The item writer wrote
them from 2.1, 2.5 and the legend sentences of 9.1 only. The second plan reviewer checked every key and critical option
(`manage-agents/risk-probe-check.final.md`), and the items it rejected were dropped before sealing. **Status: sealed.**
`MANIFEST.sha256` lists every sealed file with its SHA-256; nothing it lists is edited after sealing. An item found
defective afterwards is reported in `RESULTS.md` with its reason, and its construct is scored with and without it.

## Dropped before sealing

| Item | Reason (checking reviewer) |
|---|---|
| c3a-4 | Critical (b) infers "probably" at a specific five-minute duration from "usually" overall; the rival gives no likelihood conditional on that duration. |
| c3b-4 | The same conditional-likelihood error as c3a-4. |
| c6-2 | Critical (b) adds a world-knowledge explanation that does not follow from the sufficient-condition rival; critical (d) is supported. |
| c9-3 | Critical (b) infers a lower probability of data loss from a lower probability of any harm; neither rival establishes that comparison. |
| c9-4 | Critical (b) infers a lower seizure probability from a lower probability of any harm. |
| c12-2 | At 28 kilograms the sufficient condition requires a fall and the guarantee rival excludes it; the options give no conflict answer. |
| c12-4 | At 11 gigabytes the sufficient condition requires an outage and the guarantee rival excludes it. |
| c14-3 | The permission rival conflicts with Rule 1's prohibition; nothing gives it precedence, so critical (b)'s "Yes" is unsupported. |
| ctl-2 | Unscored control with the same contradiction as c12-2. |

## Contents

| File | What it is |
|---|---|
| `items.json` | 53 items: 52 scored over the 15 constructs (c1, c2, c3a, c3b, c4 to c14) and the control `ctl-1` |
| `prompt.txt` | the fixed reader instruction (2.6 Readers), and nothing else |
| `readers.json` | the reader list: family, model and the exact invocation |
| `sessions.json` | the seed, the dropped ids, and for every session its family, replicate, condition and items in order, with the shown-letter to sealed-label map of each item's shuffled options |
| `sessions/<session>.txt` | the exact text each reader session receives |
| `seal.py` | the script that dropped the items and wrote the files above (run once) |
| `score.py` | the mechanical scorer; it writes `scored.json` and `RESULTS.md` |

Each item object in `items.json` has:

| Field | Meaning |
|---|---|
| `id`, `construct` | `c3b-2`, `ctl-1`, … ; the control has construct `control-prevents` |
| `domain`, `setting` | `agent-operations` or `non-computer`; the setting is agent operations, delivery robot or clinic |
| `scored` | `false` for the control |
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
| `same_situation_as`, `parallel_to`, `fulfilment_body` | c3b items reuse the c3a situations; the control mirrors c12-1; c13 items name `avoids` or `excludes` |

## Counts after the drops

| Construct | Items | L answers | C answers |
|---|---|---|---|
| c1, c2, c4, c5, c7, c8, c10, c11 (each) | 4 | 16 | 16 |
| c3a, c3b, c6, c14 (each) | 3 | 12 | 12 |
| c9, c12 (each) | 2 | 8 | 8 |
| c13 | 4 | 16 | (L only) |
| `prevents` control | 1 | 4 | 4 |
| **Total** | **53** | **212** | **196** |

408 answers in all, from 56 sessions. Every remaining scored construct keeps at least two separating items; c6 no
longer has an item against world knowledge (c6-2 was its only one).

## Sessions

Two readers (Claude Haiku 4.5, GPT-6 Sol), two replicates each, two conditions: for each (family, replicate,
condition) the items of that condition are split into 7 sessions of at most 8 items with a seeded random greedy
assignment. A session holds at most one item per construct, never both c3a and c3b, never c12 with the control, and
one condition only. Item order and each item's option order are shuffled with the same seed; options are shown as
(a) to (d) in shuffled order and mapped back to the sealed labels by `sessions.json`. So every item is answered in
each of its conditions by two independent sessions per family. Session ids are `<family>-r<replicate>-<L|C>-<nn>`;
readers never see ids, constructs or keys.

In L each text starts with a `Legend:` block of the item's legend lines, as the IDE shows it; in C the block is
absent and the text is otherwise identical.

## Scoring (fixed before any run)

- `score.py` splits a response into one block per text (at `Text n`, `Item n`, `Question n` or a line starting
  `n.`), takes the earliest option letter in the block (`(b)`, `b)`, `**b**`, `Answer: b`, `Text 2: b`), and
  otherwise a unique verbatim option text. Anything else is **unparseable**: wrong, not critical.
  `python3 score.py --selftest` checks the parser on hand-written shapes.
- Rule 1 of 2.6 ("at least 15 of its 16 answers are correct and none is critical") is applied as the same
  allowance to the answers that remain after the drops: **a construct passes when, in L, at most one of its answers
  is not correct and none is critical.** RESULTS.md also shows, without deciding anything, the proportional reading
  (at least 15/16 of the answers correct), which for 8 or 12 answers requires every answer correct.
- A construct that passes L with a critical answer in C is **legend-dependent**. Rules 2 to 5 of 2.6 are applied as
  written; the control is reported, not scored.

## After sealing (not in the manifest)

`run.py` sends each session to its reader in a fresh empty temporary directory outside the repository and saves the
raw output under `runs/<session>/`; `scored.json` and `RESULTS.md` are generated by `score.py`. Every result is
labelled "proxy; human readability unmeasured".
