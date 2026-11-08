# PS-E1 preregistration: which carriers do readers take?

Status: frozen before any model call (R-12; plan `docs/spec/presupposition-PLAN.md`, PS-E1; spec
`docs/spec/presupposition.md` 6). The commit that adds this file precedes every record under
`docs/research/presupposition-E1/raw/`; the runner refuses to call unless this file, the items and its own code are
in HEAD byte for byte (`e1_runner.committed`).

Sonnet 5.5 is a proxy. Every result is labelled "proxy, an upper bound for careful readers", and none establishes
what untrained human readers understand. The experiment decides candidates and wording only; it never admits a
sentence (D2-6).

## Machine-readable settings

The scorer and the runner read this block; the bars live here and nowhere else.

<!-- config:begin -->
```json
{
 "model": "claude-sonnet-5-5",
 "trials_per_item": 40,
 "concurrency": 4,
 "call_cap": 4320,
 "cw_cap": 15000000,
 "reader_instruction": "You are a careful reader of English. You will be given a sentence, a situation and a question with lettered options. Read the sentence exactly as written and use only what the sentence and the situation say. Choose the one option that fits best. Reply with only that option's letter in parentheses, and nothing else.",
 "mapping": {
  "singular_definite": "definite",
  "possessive_or_plural": "plural",
  "role_definite_in_rule": "definite",
  "factive": "generic",
  "change_of_state": "generic",
  "iteration": "generic",
  "heading_noun_phrase": "plural"
 },
 "candidate_order": ["assumed", "conditioned", "asserted", "in_place", "unconditional"],
 "bars": {
  "candidate_min": 6,
  "one_reading_min": 36,
  "cannot_tell_max": 10,
  "control_min": 36,
  "controls_passing_min": 11,
  "suspension_c_max": 6,
  "proviso_min": 6
 }
}
```
<!-- config:end -->

## 1. Mapping of the seven trigger classes to the three row names

`mapping` above. Spec 2.1 gives the rows: "the N", "the N of t", "t's N" (singular) are `definite`; "t's Ns", "the Ns of
t" are `plural`; factive complements, earlier states and earlier events are `generic`. A role definite ("the operator
of Line 4") is a singular definite. A heading noun phrase is `plural`: every heading item uses a possessive plural,
the shape of S23 and P1 ("Claude's core values", `plural`). The rows therefore aggregate two (`definite`), two
(`plural`) and three (`generic`) classes.

## 2. Aggregation per cell

A class's cell is its two items in a position class. For a class's cell, the plan's bars apply verbatim:

- a carrier is a **candidate** iff it gets at least 6/40 on each of the two items;
- the cell is **one-reading** iff one carrier gets at least 36/40 on both items;
- the cell admits **no carrier** when (d) exceeds 10/40 on either item.

A row's cell is computed from the cells of the classes mapped to that row:

- if any class's cell admits no carrier, the row's cell is empty (status `no_carrier`);
- otherwise the row's cell is the union of the classes' candidates (status `open`);
- if every class's cell is one-reading with the same carrier, the row's cell lists only that carrier (status
  `one_reading`). In place is the conditioned reading's alias, never a reading of its own (spec 1.4), so where that
  carrier is conditioned and (e) is a candidate, the cell is conditioned then in place: one reading, two wordings.

Answers: (a) counts for `asserted`, (b) for `conditioned`, (c) for `assumed`, (e) for `in_place` (and for `conditioned`
too under rule 6). (d) counts for no carrier. A call error or an answer that is not one of the item's letters counts
as (d) and is listed by id (the jt-e1r F2 rule).

`disjunct` is not measured (spec C1): its cell stays empty. Controls and suspension items never feed a cell. Proviso
items feed only `unconditional`, as follows.

**Proviso.** The six proviso items are three pairs, one per row. A pair is reported as the share of (c) answers,
which mean the unconditional goal `f.close pre`. If (c) gets at least 6/40 on both items of a row's pair,
`unconditional` joins that row's `consequent` cell independently of the target items' status; a target one-reading
or no-carrier classification does not decide the proviso goal. A proviso item's situation is the only one that separates the
unconditional goal from the conditional one: the antecedent is false and `pre` fails, so the projected goal holds and
`f.close pre` fails (table below, `goal` true, `close` false). The plan's "where the projected goal fails" cannot
separate them, since there both goals fail.

**`cellOk`.** Two shape rules bind the output (spec 1.8, 4.7), checked by Lean on the spec's own definition
(`e1_score.table_ok`): a table that fails is an analysis error.
- If assumed and asserted are both above the bar, the cell lists `assumed`, and the note says so (spec C3's proposal:
  the presupposition stays visible, and PS-E2 tests the asserted wording as a paraphrase).
- A cell that lists `in_place` also lists `conditioned`, added if the bars did not give it.

## 3. Classes of one row that disagree

Disagreement never narrows a row. The table can name only rows, not classes, so:
- a reading any class's readers take stays in the row's cell (the union);
- one-reading needs every class to agree;
- one no-carrier class empties the row's cell (the row refuses rather than guesses for the other classes' sentences).

Every disagreement is listed beside the row's cell in the results.

## 4. Ordering

Candidates in a cell are ordered by share of answers over all the cell's items of the row, highest first; ties in the
list order `assumed, conditioned, asserted, in_place, unconditional` (spec 6). `conditioned`'s share includes (e) where
rule 6 merges them; `in_place`'s share is (e) alone. `unconditional`'s share is its (c) answers on the proviso pair.

## 5. Per-item frame and denotation table

The block at the end of this file is written by `docs/presupposition/ps-e1/e1_stub.py --write`, never typed. It reads
`docs/research/presupposition-E1/items.jsonl`, elaborates one generated file against PS-1's merged Lean
(`lean/VE/Presupposition/`: `Frame.plug`, `Frame.goal`, `Frame.close`, `Frame.cls`, `Frame.shallowB`, `assertedAt`,
`conditionedAt`, `inPlaceAt`, the rows, `Examples.model`, `Examples.ev`) and prints each row with Lean's `#eval`. Each
item carries its reading, frame and finite model as Lean source. Its `#guard`s stop the generator when they fail:

- claim cells: `f.cls` is the item's cell; every target and suspension item: the goal is false in its model;
- every negated and antecedent item: `f.shallowB`, and in place and conditioned have the same value (R-D4);
- controls: the goal is true; proviso: the goal is true and `f.close pre` is false.

Columns: `frame` (Lean's rendering, `·` the hole, `…` the other side), `cls` (`Frame.cls`), `shallow`, `goal`, `close`,
`asserted`, `conditioned`, `in_place`, `base` (the sentence as written, `f.plug strong`), `be_one_class` (rule 6).

**Rules.** `lean/VE/Presupposition/Rules.lean` (spec 4.5) is not merged yet, so a rule item is computed on the rule's
formula rendering `∀agent (guard → act)`, with the frame crossing the binder. For a rule act with a silent guard the
goal is spec 4.5's `ruleGoal` without carve-outs. `cls` is then the formula's class, and the item's cell is its
position (`cls` gives no rule class, spec 1.2). A rule act's `asserted` and `in_place` are null: it has neither
carrier (spec 1.8). Its `conditioned` value true is `conditioned_vacuous_off_goal`: the rule contributes no decision.

## 6. The equivalent-option rule for (e) (R-D4)

(b) and (e) count as one class only for an item whose row above has `be_one_class` true: its frame is shallow and the
stub shows in place and conditioned with the same value in the item's failing situation. Otherwise they count apart.
"True here" is never identified with local accommodation at a compound or nested frame. One class means: `conditioned`
gets (b) + (e) for every bar; `in_place` keeps (e) alone, so it is a candidate only when (e) itself clears the bar, and
it then licenses only the conditioned reading's alias wording at shallow frames (plan PS-E1, Output).

## 7. Items

`docs/research/presupposition-E1/items.jsonl`, 108 items, built once by `e1_items.py` from `scenarios.json` and frozen:

- 84 target items: 7 classes × 6 positions × 2. Two scenarios per class, each written at all six positions. The goal
  fails in each situation by existence: no owner, no students, the earlier state never held.
- 12 controls, the filters of R 4.1 (`if` 3, `and` 3, `or` 2, `every` 2, rule guard 2), four per row. The text supplies
  the presupposition and the goal holds. The key is what the proved carrier predicts, the value of the sentence as
  written: `base` false keys (a); `base` true keys (b), where the filter leaves the trigger unreached. No control has
  option (e), by the plan's cell rule, so no control's situation makes the sentence plainly true.
- 6 suspension items, two per row: "We are uncertain whether …; …" with `pre` failing.
- 6 proviso items, three pairs (rule 2).

A heading item shows the noun phrase as a section heading above a sentence that reuses it at the cell's position. It
measures a heading noun phrase's reading in that cell; the heading's own position (spec 1.4a, proved or assumed only)
is not a table cell.

**Options** (spec 2.5, fixed order a to e; not shuffled): (a) "The sentence is false in this situation."; (b) "The
sentence says nothing about this situation."; (c) "The sentence takes for granted that <pre>, so this situation goes
against the text."; (d) "I cannot tell."; (e) "The sentence is true in this situation.". Rule-act items drop (a). (e)
only in negated and antecedent cells. Rule-act and rule-guard items word (b) "This rule decides nothing in this
situation.": the plan reads "(for a rule: this rule decides nothing here)", while spec 2.5 names only rule-act items;
a rule guard is a rule, and the plan is the reviewed protocol.

## 8. Protocol

One fresh, blinded call per trial, 40 trials per item, 4,320 calls, `claude-sonnet-5-5` through the `claude` CLI on the
account `pick-claude-account.sh` picks (subscription only: no API key, no paid credits; a reported paid-credit fallback
stops the run). No tools, no settings, no MCP, an empty working directory, `reader_instruction` as the whole system
prompt, at most four calls at once, default effort. The reader sees the optional heading, the sentence, the situation,
the question and the options; ids, families, keys and this file never reach it.

- **Caps.** At most 4,320 calls, 15M CW. CW is the sum of the four usage counters the CLI reports (the jt-e1r rule).
  One item's 40 trials run first and the projection for 4,320 calls goes in the report; above 15M the run stops there
  and asks the decider. Otherwise all run. Before each dispatch the runner reserves 25k CW plus one output allowance,
  bounds the prompt and CLI output, and stops on reported exhaustion. A CLI that exceeds its allowance is recorded
  with its full reported usage and stops the run; its actual overage cannot be undone.
- **Resumable.** A re-run skips every trial with a final record. Only a call known not to have started is an outage,
  charged 25k CW and retried up to three attempts in all; the third is a call error. Missing usage, zero output,
  timeout and malformed CLI JSON do not prove the model was not reached: they consume a call and are final call
  errors. Three failed calls in a row stop the run. Call errors count as (d) and are listed by id.

## 9. Bars, verbatim from the plan

- A carrier is a **candidate** in a cell iff it gets at least 6/40 on each of the cell's two items.
- A cell is **one-reading** iff one carrier gets at least 36/40 on both items.
- A cell where (d) exceeds 10/40 on either item admits **no** carrier.
- **Controls:** at least 36/40 choose the answer the proved carrier predicts, on at least 11 of 12 items.
- **Suspension:** (c) at most 6/40 on each item.
- **Proviso:** reported as the share of unconditional-assumption answers. If at least 6/40 on both items, the
  unconditional goal becomes an extra candidate in the consequent cells.

The candidate table (`docs/research/presupposition-E1/candidate-table.json`, format of spec 6) is written by
`e1_score.py --write`, which reads this file and the saved answers. `tableOk` must hold on its output.

## Per-item table

<!-- stub-table:begin -->
```json
[
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "·", "goal": false, "id": "T-SD-TOP-a", "in_place": false, "shallow": false},
{"asserted": false, "base": true, "be_one_class": true, "cell": "negated", "close": false, "cls": "negated", "conditioned": true, "frame": "not (·)", "goal": false, "id": "T-SD-NEG-a", "in_place": true, "shallow": true},
{"asserted": false, "base": true, "be_one_class": true, "cell": "antecedent", "close": false, "cls": "antecedent", "conditioned": true, "frame": "if (·) then …", "goal": false, "id": "T-SD-ANT-a", "in_place": true, "shallow": true},
{"asserted": false, "base": false, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": false, "id": "T-SD-CON-a", "in_place": false, "shallow": false},
{"asserted": null, "base": false, "be_one_class": false, "cell": "rule_act", "close": false, "cls": "consequent", "conditioned": true, "frame": "every agent: if … then (·)", "goal": false, "id": "T-SD-ACT-a", "in_place": null, "shallow": false},
{"asserted": false, "base": true, "be_one_class": false, "cell": "rule_guard", "close": false, "cls": "antecedent", "conditioned": true, "frame": "every agent: if (·) then …", "goal": false, "id": "T-SD-GRD-a", "in_place": true, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "·", "goal": false, "id": "T-SD-TOP-b", "in_place": false, "shallow": false},
{"asserted": false, "base": true, "be_one_class": true, "cell": "negated", "close": false, "cls": "negated", "conditioned": true, "frame": "not (·)", "goal": false, "id": "T-SD-NEG-b", "in_place": true, "shallow": true},
{"asserted": false, "base": true, "be_one_class": true, "cell": "antecedent", "close": false, "cls": "antecedent", "conditioned": true, "frame": "if (·) then …", "goal": false, "id": "T-SD-ANT-b", "in_place": true, "shallow": true},
{"asserted": false, "base": false, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": false, "id": "T-SD-CON-b", "in_place": false, "shallow": false},
{"asserted": null, "base": false, "be_one_class": false, "cell": "rule_act", "close": false, "cls": "consequent", "conditioned": true, "frame": "every agent: if … then (·)", "goal": false, "id": "T-SD-ACT-b", "in_place": null, "shallow": false},
{"asserted": false, "base": true, "be_one_class": false, "cell": "rule_guard", "close": false, "cls": "antecedent", "conditioned": true, "frame": "every agent: if (·) then …", "goal": false, "id": "T-SD-GRD-b", "in_place": true, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "·", "goal": false, "id": "T-PP-TOP-a", "in_place": false, "shallow": false},
{"asserted": false, "base": true, "be_one_class": true, "cell": "negated", "close": false, "cls": "negated", "conditioned": true, "frame": "not (·)", "goal": false, "id": "T-PP-NEG-a", "in_place": true, "shallow": true},
{"asserted": false, "base": true, "be_one_class": true, "cell": "antecedent", "close": false, "cls": "antecedent", "conditioned": true, "frame": "if (·) then …", "goal": false, "id": "T-PP-ANT-a", "in_place": true, "shallow": true},
{"asserted": false, "base": false, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": false, "id": "T-PP-CON-a", "in_place": false, "shallow": false},
{"asserted": null, "base": false, "be_one_class": false, "cell": "rule_act", "close": false, "cls": "consequent", "conditioned": true, "frame": "every agent: if … then (·)", "goal": false, "id": "T-PP-ACT-a", "in_place": null, "shallow": false},
{"asserted": false, "base": true, "be_one_class": false, "cell": "rule_guard", "close": false, "cls": "antecedent", "conditioned": true, "frame": "every agent: if (·) then …", "goal": false, "id": "T-PP-GRD-a", "in_place": true, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "·", "goal": false, "id": "T-PP-TOP-b", "in_place": false, "shallow": false},
{"asserted": false, "base": true, "be_one_class": true, "cell": "negated", "close": false, "cls": "negated", "conditioned": true, "frame": "not (·)", "goal": false, "id": "T-PP-NEG-b", "in_place": true, "shallow": true},
{"asserted": false, "base": true, "be_one_class": true, "cell": "antecedent", "close": false, "cls": "antecedent", "conditioned": true, "frame": "if (·) then …", "goal": false, "id": "T-PP-ANT-b", "in_place": true, "shallow": true},
{"asserted": false, "base": false, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": false, "id": "T-PP-CON-b", "in_place": false, "shallow": false},
{"asserted": null, "base": false, "be_one_class": false, "cell": "rule_act", "close": false, "cls": "consequent", "conditioned": true, "frame": "every agent: if … then (·)", "goal": false, "id": "T-PP-ACT-b", "in_place": null, "shallow": false},
{"asserted": false, "base": true, "be_one_class": false, "cell": "rule_guard", "close": false, "cls": "antecedent", "conditioned": true, "frame": "every agent: if (·) then …", "goal": false, "id": "T-PP-GRD-b", "in_place": true, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "·", "goal": false, "id": "T-RD-TOP-a", "in_place": false, "shallow": false},
{"asserted": false, "base": true, "be_one_class": true, "cell": "negated", "close": false, "cls": "negated", "conditioned": true, "frame": "not (·)", "goal": false, "id": "T-RD-NEG-a", "in_place": true, "shallow": true},
{"asserted": false, "base": true, "be_one_class": true, "cell": "antecedent", "close": false, "cls": "antecedent", "conditioned": true, "frame": "if (·) then …", "goal": false, "id": "T-RD-ANT-a", "in_place": true, "shallow": true},
{"asserted": false, "base": false, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": false, "id": "T-RD-CON-a", "in_place": false, "shallow": false},
{"asserted": null, "base": false, "be_one_class": false, "cell": "rule_act", "close": false, "cls": "consequent", "conditioned": true, "frame": "every agent: if … then (·)", "goal": false, "id": "T-RD-ACT-a", "in_place": null, "shallow": false},
{"asserted": false, "base": true, "be_one_class": false, "cell": "rule_guard", "close": false, "cls": "antecedent", "conditioned": true, "frame": "every agent: if (·) then …", "goal": false, "id": "T-RD-GRD-a", "in_place": true, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "·", "goal": false, "id": "T-RD-TOP-b", "in_place": false, "shallow": false},
{"asserted": false, "base": true, "be_one_class": true, "cell": "negated", "close": false, "cls": "negated", "conditioned": true, "frame": "not (·)", "goal": false, "id": "T-RD-NEG-b", "in_place": true, "shallow": true},
{"asserted": false, "base": true, "be_one_class": true, "cell": "antecedent", "close": false, "cls": "antecedent", "conditioned": true, "frame": "if (·) then …", "goal": false, "id": "T-RD-ANT-b", "in_place": true, "shallow": true},
{"asserted": false, "base": false, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": false, "id": "T-RD-CON-b", "in_place": false, "shallow": false},
{"asserted": null, "base": false, "be_one_class": false, "cell": "rule_act", "close": false, "cls": "consequent", "conditioned": true, "frame": "every agent: if … then (·)", "goal": false, "id": "T-RD-ACT-b", "in_place": null, "shallow": false},
{"asserted": false, "base": true, "be_one_class": false, "cell": "rule_guard", "close": false, "cls": "antecedent", "conditioned": true, "frame": "every agent: if (·) then …", "goal": false, "id": "T-RD-GRD-b", "in_place": true, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "·", "goal": false, "id": "T-FA-TOP-a", "in_place": false, "shallow": false},
{"asserted": false, "base": true, "be_one_class": true, "cell": "negated", "close": false, "cls": "negated", "conditioned": true, "frame": "not (·)", "goal": false, "id": "T-FA-NEG-a", "in_place": true, "shallow": true},
{"asserted": false, "base": true, "be_one_class": true, "cell": "antecedent", "close": false, "cls": "antecedent", "conditioned": true, "frame": "if (·) then …", "goal": false, "id": "T-FA-ANT-a", "in_place": true, "shallow": true},
{"asserted": false, "base": false, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": false, "id": "T-FA-CON-a", "in_place": false, "shallow": false},
{"asserted": null, "base": false, "be_one_class": false, "cell": "rule_act", "close": false, "cls": "consequent", "conditioned": true, "frame": "every agent: if … then (·)", "goal": false, "id": "T-FA-ACT-a", "in_place": null, "shallow": false},
{"asserted": false, "base": true, "be_one_class": false, "cell": "rule_guard", "close": false, "cls": "antecedent", "conditioned": true, "frame": "every agent: if (·) then …", "goal": false, "id": "T-FA-GRD-a", "in_place": true, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "·", "goal": false, "id": "T-FA-TOP-b", "in_place": false, "shallow": false},
{"asserted": false, "base": true, "be_one_class": true, "cell": "negated", "close": false, "cls": "negated", "conditioned": true, "frame": "not (·)", "goal": false, "id": "T-FA-NEG-b", "in_place": true, "shallow": true},
{"asserted": false, "base": true, "be_one_class": true, "cell": "antecedent", "close": false, "cls": "antecedent", "conditioned": true, "frame": "if (·) then …", "goal": false, "id": "T-FA-ANT-b", "in_place": true, "shallow": true},
{"asserted": false, "base": false, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": false, "id": "T-FA-CON-b", "in_place": false, "shallow": false},
{"asserted": null, "base": false, "be_one_class": false, "cell": "rule_act", "close": false, "cls": "consequent", "conditioned": true, "frame": "every agent: if … then (·)", "goal": false, "id": "T-FA-ACT-b", "in_place": null, "shallow": false},
{"asserted": false, "base": true, "be_one_class": false, "cell": "rule_guard", "close": false, "cls": "antecedent", "conditioned": true, "frame": "every agent: if (·) then …", "goal": false, "id": "T-FA-GRD-b", "in_place": true, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "·", "goal": false, "id": "T-CS-TOP-a", "in_place": false, "shallow": false},
{"asserted": false, "base": true, "be_one_class": true, "cell": "negated", "close": false, "cls": "negated", "conditioned": true, "frame": "not (·)", "goal": false, "id": "T-CS-NEG-a", "in_place": true, "shallow": true},
{"asserted": false, "base": true, "be_one_class": true, "cell": "antecedent", "close": false, "cls": "antecedent", "conditioned": true, "frame": "if (·) then …", "goal": false, "id": "T-CS-ANT-a", "in_place": true, "shallow": true},
{"asserted": false, "base": false, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": false, "id": "T-CS-CON-a", "in_place": false, "shallow": false},
{"asserted": null, "base": false, "be_one_class": false, "cell": "rule_act", "close": false, "cls": "consequent", "conditioned": true, "frame": "every agent: if … then (·)", "goal": false, "id": "T-CS-ACT-a", "in_place": null, "shallow": false},
{"asserted": false, "base": true, "be_one_class": false, "cell": "rule_guard", "close": false, "cls": "antecedent", "conditioned": true, "frame": "every agent: if (·) then …", "goal": false, "id": "T-CS-GRD-a", "in_place": true, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "·", "goal": false, "id": "T-CS-TOP-b", "in_place": false, "shallow": false},
{"asserted": false, "base": true, "be_one_class": true, "cell": "negated", "close": false, "cls": "negated", "conditioned": true, "frame": "not (·)", "goal": false, "id": "T-CS-NEG-b", "in_place": true, "shallow": true},
{"asserted": false, "base": true, "be_one_class": true, "cell": "antecedent", "close": false, "cls": "antecedent", "conditioned": true, "frame": "if (·) then …", "goal": false, "id": "T-CS-ANT-b", "in_place": true, "shallow": true},
{"asserted": false, "base": false, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": false, "id": "T-CS-CON-b", "in_place": false, "shallow": false},
{"asserted": null, "base": false, "be_one_class": false, "cell": "rule_act", "close": false, "cls": "consequent", "conditioned": true, "frame": "every agent: if … then (·)", "goal": false, "id": "T-CS-ACT-b", "in_place": null, "shallow": false},
{"asserted": false, "base": true, "be_one_class": false, "cell": "rule_guard", "close": false, "cls": "antecedent", "conditioned": true, "frame": "every agent: if (·) then …", "goal": false, "id": "T-CS-GRD-b", "in_place": true, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "·", "goal": false, "id": "T-IT-TOP-a", "in_place": false, "shallow": false},
{"asserted": false, "base": true, "be_one_class": true, "cell": "negated", "close": false, "cls": "negated", "conditioned": true, "frame": "not (·)", "goal": false, "id": "T-IT-NEG-a", "in_place": true, "shallow": true},
{"asserted": false, "base": true, "be_one_class": true, "cell": "antecedent", "close": false, "cls": "antecedent", "conditioned": true, "frame": "if (·) then …", "goal": false, "id": "T-IT-ANT-a", "in_place": true, "shallow": true},
{"asserted": false, "base": false, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": false, "id": "T-IT-CON-a", "in_place": false, "shallow": false},
{"asserted": null, "base": false, "be_one_class": false, "cell": "rule_act", "close": false, "cls": "consequent", "conditioned": true, "frame": "every agent: if … then (·)", "goal": false, "id": "T-IT-ACT-a", "in_place": null, "shallow": false},
{"asserted": false, "base": true, "be_one_class": false, "cell": "rule_guard", "close": false, "cls": "antecedent", "conditioned": true, "frame": "every agent: if (·) then …", "goal": false, "id": "T-IT-GRD-a", "in_place": true, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "·", "goal": false, "id": "T-IT-TOP-b", "in_place": false, "shallow": false},
{"asserted": false, "base": true, "be_one_class": true, "cell": "negated", "close": false, "cls": "negated", "conditioned": true, "frame": "not (·)", "goal": false, "id": "T-IT-NEG-b", "in_place": true, "shallow": true},
{"asserted": false, "base": true, "be_one_class": true, "cell": "antecedent", "close": false, "cls": "antecedent", "conditioned": true, "frame": "if (·) then …", "goal": false, "id": "T-IT-ANT-b", "in_place": true, "shallow": true},
{"asserted": false, "base": false, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": false, "id": "T-IT-CON-b", "in_place": false, "shallow": false},
{"asserted": null, "base": false, "be_one_class": false, "cell": "rule_act", "close": false, "cls": "consequent", "conditioned": true, "frame": "every agent: if … then (·)", "goal": false, "id": "T-IT-ACT-b", "in_place": null, "shallow": false},
{"asserted": false, "base": true, "be_one_class": false, "cell": "rule_guard", "close": false, "cls": "antecedent", "conditioned": true, "frame": "every agent: if (·) then …", "goal": false, "id": "T-IT-GRD-b", "in_place": true, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "·", "goal": false, "id": "T-HN-TOP-a", "in_place": false, "shallow": false},
{"asserted": false, "base": true, "be_one_class": true, "cell": "negated", "close": false, "cls": "negated", "conditioned": true, "frame": "not (·)", "goal": false, "id": "T-HN-NEG-a", "in_place": true, "shallow": true},
{"asserted": false, "base": true, "be_one_class": true, "cell": "antecedent", "close": false, "cls": "antecedent", "conditioned": true, "frame": "if (·) then …", "goal": false, "id": "T-HN-ANT-a", "in_place": true, "shallow": true},
{"asserted": false, "base": false, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": false, "id": "T-HN-CON-a", "in_place": false, "shallow": false},
{"asserted": null, "base": false, "be_one_class": false, "cell": "rule_act", "close": false, "cls": "consequent", "conditioned": true, "frame": "every agent: if … then (·)", "goal": false, "id": "T-HN-ACT-a", "in_place": null, "shallow": false},
{"asserted": false, "base": true, "be_one_class": false, "cell": "rule_guard", "close": false, "cls": "antecedent", "conditioned": true, "frame": "every agent: if (·) then …", "goal": false, "id": "T-HN-GRD-a", "in_place": true, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "·", "goal": false, "id": "T-HN-TOP-b", "in_place": false, "shallow": false},
{"asserted": false, "base": true, "be_one_class": true, "cell": "negated", "close": false, "cls": "negated", "conditioned": true, "frame": "not (·)", "goal": false, "id": "T-HN-NEG-b", "in_place": true, "shallow": true},
{"asserted": false, "base": true, "be_one_class": true, "cell": "antecedent", "close": false, "cls": "antecedent", "conditioned": true, "frame": "if (·) then …", "goal": false, "id": "T-HN-ANT-b", "in_place": true, "shallow": true},
{"asserted": false, "base": false, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": false, "id": "T-HN-CON-b", "in_place": false, "shallow": false},
{"asserted": null, "base": false, "be_one_class": false, "cell": "rule_act", "close": false, "cls": "consequent", "conditioned": true, "frame": "every agent: if … then (·)", "goal": false, "id": "T-HN-ACT-b", "in_place": null, "shallow": false},
{"asserted": false, "base": true, "be_one_class": false, "cell": "rule_guard", "close": false, "cls": "antecedent", "conditioned": true, "frame": "every agent: if (·) then …", "goal": false, "id": "T-HN-GRD-b", "in_place": true, "shallow": false},
{"asserted": true, "base": true, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": true, "id": "C01", "in_place": true, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": false, "frame": "… and (·)", "goal": true, "id": "C02", "in_place": false, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "disjunct", "close": true, "cls": "disjunct", "conditioned": false, "frame": "… or (·)", "goal": true, "id": "C03", "in_place": false, "shallow": false},
{"asserted": null, "base": true, "be_one_class": false, "cell": "rule_act", "close": false, "cls": "consequent", "conditioned": true, "frame": "every agent: if … then (·)", "goal": true, "id": "C04", "in_place": null, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "consequent", "close": true, "cls": "consequent", "conditioned": false, "frame": "if … then (·)", "goal": true, "id": "C05", "in_place": false, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": false, "frame": "… and (·)", "goal": true, "id": "C06", "in_place": false, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": false, "frame": "every entity: if … then (·)", "goal": true, "id": "C07", "in_place": false, "shallow": false},
{"asserted": null, "base": true, "be_one_class": false, "cell": "rule_act", "close": false, "cls": "consequent", "conditioned": true, "frame": "every agent: if … then (·)", "goal": true, "id": "C08", "in_place": null, "shallow": false},
{"asserted": true, "base": true, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": true, "id": "C09", "in_place": true, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": false, "frame": "… and (·)", "goal": true, "id": "C10", "in_place": false, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "disjunct", "close": true, "cls": "disjunct", "conditioned": false, "frame": "… or (·)", "goal": true, "id": "C11", "in_place": false, "shallow": false},
{"asserted": true, "base": true, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "every entity: if … then (·)", "goal": true, "id": "C12", "in_place": true, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "… and (·)", "goal": false, "id": "S01", "in_place": false, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "… and (·)", "goal": false, "id": "S02", "in_place": false, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "… and (·)", "goal": false, "id": "S03", "in_place": false, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "… and (·)", "goal": false, "id": "S04", "in_place": false, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "… and (·)", "goal": false, "id": "S05", "in_place": false, "shallow": false},
{"asserted": false, "base": false, "be_one_class": false, "cell": "top", "close": false, "cls": "top", "conditioned": true, "frame": "… and (·)", "goal": false, "id": "S06", "in_place": false, "shallow": false},
{"asserted": true, "base": true, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": true, "id": "V01", "in_place": true, "shallow": false},
{"asserted": true, "base": true, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": true, "id": "V02", "in_place": true, "shallow": false},
{"asserted": true, "base": true, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": true, "id": "V03", "in_place": true, "shallow": false},
{"asserted": true, "base": true, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": true, "id": "V04", "in_place": true, "shallow": false},
{"asserted": true, "base": true, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": true, "id": "V05", "in_place": true, "shallow": false},
{"asserted": true, "base": true, "be_one_class": false, "cell": "consequent", "close": false, "cls": "consequent", "conditioned": true, "frame": "if … then (·)", "goal": true, "id": "V06", "in_place": true, "shallow": false}
]
```
<!-- stub-table:end -->
