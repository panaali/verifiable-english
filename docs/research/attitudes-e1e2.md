# Attitudes: E1 and E2 (pre-registered experiments, run)

> **Status.** 2026-10-13, branch `research/attitudes-p1`, at plan draft 5 (`46669ccb`). The DRI authorised both
> experiments in decision AT1 (`manage-agents/debates/plan-synthesis/DRI-DECISIONS-PHASE2.md`: "E1 and E2 are
> authorised now (Sonnet 5.5 human proxy, 2,480 calls; third Claude account has room)"). Sections 1 and 2 are written
> and committed **before** the first reader call; the bars are quoted verbatim from
> [docs/spec/attitudes-PLAN.md](../spec/attitudes-PLAN.md) draft 5, section 4, and are not moved after the data.
> No product code (`ve/`, `lean/VE/`, `rust/`, `tools/`) is changed. Scripts: `research/attitudes/`; evidence:
> `docs/research/evidence/attitudes/`. The phase-1 report ([attitudes-phase1.md](attitudes-phase1.md), **P1 n**)
> holds the preparation; G1–G6 are its gaps, as the plan cites them.

## 1. Pre-registered bars (quoted before running)

### 1.1 E1 (PLAN section 4, "E1. Likelihood words: order and lower bounds")

> Pre-registered. Readers: Sonnet 5.5 as human proxy (`claude-sonnet-5-5`), 40 independent sessions with no shared
> context, items in a seeded random order (seed `attitudes-E1`). Words: almost certain, very likely, quite likely,
> likely, more likely than not, as likely as not, unlikely, very unlikely (8 words, 28 pairs), each pair as two
> sentences "Claude thinks it *a* that the file is safe" / "… *b* …", question: "If the first sentence is true, must the
> second be true?" (yes / no / cannot tell). Plus 8 items "If Claude is certain that the file is safe, does Claude
> think it *w* that the file is safe?".
>
> - **A pair enters the scale table** (`table.above`, with its item) iff at least 36 of 40 answer yes and at most 2
>   answer no.
> - **The lower-bound reading of a word** is confirmed iff at least 34 of 40 answer yes to its certainty item; the
>   word then enters `Scale.lowerBound` (with its item). A word that fails is refused by `attitudes@0` (A1), and no
>   pair names it.
> - Nothing else is concluded. This measures agreement among proxy readers, not truth and not human readers. Cost
>   **estimate**: 40 × 36 = 1,440 short calls, under the usage cap rules.

Protocol, quoted (G1, G2, G5, G6):

> - **G1, pair direction.** Each of the 28 pairs is asked once, the earlier word in the list above as the first
>   sentence, so a passing item is the scale pair (earlier, later). Item ids `E1.pair.<a>.<b>` and `E1.cert.<w>`.
> - **G2, independence.** One fresh context per call: no system prompt beyond the preamble, no earlier turn. The 40
>   "sessions" are 40 readers per item; the seeded order (`random.Random("attitudes-E1")`, 40 orders) fixes only the
>   call order.
> - **G5, framing.** Preamble: "Read the text and answer the question as an ordinary reader of English. Answer with
>   exactly one of: yes, no, cannot tell." Pair items label their parts "First sentence:", "Second sentence:",
>   "Question:"; certainty items label only "Question:". These choices can move answers; the DRI fixes them.
> - **G6, answers that are not yes, no or cannot tell.** The first line is read; anything else is invalid. An invalid
>   answer is not a yes (it counts against every yes bar) and, for the bar "at most 2 answer no", **counts as a no**
>   (so 36 yes and 4 "Not necessarily." fails, as the bar intends). The invalid count is reported per item. Reader
>   settings (temperature, output limit, extended thinking) are the reader's defaults, recorded with the answers.

### 1.2 E2 (PLAN section 4, "E2. Factivity and the knowing entailments")

> Same protocol. Items: three factivity items ("Claude knows that the file is safe. Must the file be safe?"); three
> "knows → believes"; one "knows → thinks it *w*" item for each of E1's eight words, scored only for the words that
> enter `lowerBound` (G3; draft 4 asked it per lower-bound word, which made E2 wait for E1); three negated-"know"
> items ("Claude does not know that the file is safe. Must the file be safe?", where the expected answer splits);
> three "unless X knows that P" items (for example, "… unless Claude knows that the user is an adult. The user is not
> an adult. Must Claude not share the file?"); six "P, and X does not know that P" items (A4, G5): three asking "Must
> P?" (expected yes) and three asking "P, and Claude does not know that P. Does Claude know that P?" (expected no).
> […]
>
> - Frame premise 1 ships iff all three factivity items reach 36 of 40. (If not, `knows` is not admitted at all.)
> - Frame premise 2 ships iff its three items reach 36 of 40. Premise 3 ships per word, iff that word's item reaches
>   36 of 40.
> - **Closure review**, then freezing. The frozen table records, for each admitted entry, the item that passed it. A
>   Lean `#guard` (`Table.reviewed`, evaluated through QS-1's closure) checks that the reflexive-transitive closure of
>   the frozen pairs adds no pair, and no premise-3 word, without its own passing item. If a derived entry's item
>   failed, the weaker word of that entry leaves `lowerBound`, with every pair and premise that names it, until the
>   closure is clean, before freezing; of several offending words the weakest goes first, one per round (G4, D-A4;
>   `resolve` in `experiments.py`, its output reviewed by Lean). […]
> - The negated-"know" items are expected to split (that is why D-A7 refuses the form); if instead 36 of 40 agree on
>   one reading, AT-0 records it and keeps the refusal anyway (one reading must not depend on a majority). Invalid
>   answers are left out of that agreement count (G6).
> - "P, and X does not know that P" is admitted only if all six of its items reach 36 of 40 (G5; […]); otherwise it is
>   refused, with its rewrites. The "unless" items are evidence only: the form stays refused whatever they show, and a
>   later admission needs its own statement review (debate round 3).

"Reaches 36 of 40" is read as: at least 36 of 40 readers give the item's expected answer (yes for every item but
the three "Does Claude know that P?" items, whose expected answer is no, as the plan states).

### 1.3 The summary line (defined before running)

The plan's bars are per item; the task asks for one line per experiment. Fixed here, before any answer:

- **E1 MET** iff at least one word's lower-bound reading is confirmed and survives the closure review, so that
  `attitudes@0` admits at least one `thinks w` mode; otherwise **NOT MET** (no `thinks w` mode, no premise 4).
  Which words and pairs pass is reported in full; the line does not summarise them.
- **E2 MET** iff frame premises 1 and 2 both ship (the two bars of E2 that are not per word: factivity, which
  decides whether `knows` is admitted at all, and knows → believes); otherwise **NOT MET**. Premise 3 per word, the
  asserted-not-know admission and the negated-"know" and "unless" evidence are reported in full.

## 2. Protocol as run, and what was added before the first call

**The DRI's confirmation of G1–G6.** Decision AT1 authorises "2,480 calls", which is E1's 1,440 plus E2's 1,040
with G5's three added items, and gives no change to G1–G6. So the protocol run is draft 5's as written (section 1),
with no change.

**Added before the first call, as draft 5 requires** (PLAN section 4 and 9: "before the first call, the scorer
implements G6's no-cap rule with its self-check case"; "the item file gains G5's three items and the scorer G6's
agreement rule, with self-check cases"):

- `experiments.py score-e1`: an invalid answer counts as a no for the pair bar's no cap (G6).
- `e2-items.json`: G5's three items `E2.asserted-not-know-knows.{1,2,3}` ("The file is safe, and Claude does not
  know that the file is safe. Question: Does Claude know that the file is safe?"; also the user/adult and door/locked
  contents), expected answer no. E2 now has 26 items; its 40 orders are regenerated from the same seed
  `attitudes-E2`. The 23 earlier items and the protocol are unchanged (compared), and `e1-items.json` is
  byte-identical.
- `experiments.py score-e2`: an item reaches when 36 of 40 give its expected answer; the asserted-not-know form is
  admitted iff all six items reach (before, the scorer refused it whatever the counts, `8538355c`); the negated-"know"
  agreement count leaves invalid answers out (G6).
- Self-check (`e-selfcheck.json`): 35 checks, all hold (was 24). Added: the pair bar with invalid answers at the cap
  (36 yes, 2 no, 1 invalid out; 36 yes, 4 invalid out; 38 yes, 2 invalid in; 36 yes, 1 no, 1 invalid in); the
  asserted-not-know form in at 36 "no" to a "Does Claude know?" item, out at 35, out when readers answer yes; the
  negated-"know" agreement in at 36 no, out at 35 no with 5 invalid, out with 40 invalid.

**Reader calls** (`research/attitudes/run_readers.py`). One fresh `claude -p --model claude-sonnet-5-5` process
per call (Claude Code 2.1.296), each in an empty working directory of its own, with `--system-prompt ""`,
`--tools ""`, `--setting-sources ""`, `--strict-mcp-config`, `--no-session-persistence`, `--disable-slash-commands`:
no tools, no settings, no project or user instructions, no saved session. The user message is the preamble and the
item, exactly `PROMPT` in `experiments.py`. At most 8 calls run at once; they are dispatched in the seeded order
(session 0's order, then session 1's, …), E1's 1,440 then E2's 1,040. Temperature, output limit and thinking are
the reader's defaults (nothing sets them); each answer is saved with the model, output and thinking tokens and stop
reason the reader reports. A failed call (process error, timeout, API error) gives no answer and is asked again,
at most three times, each failure logged.

**One known departure from G2's letter.** Claude Code adds a short context of its own to every call even with an
empty system prompt (a probe call used 625 input tokens, the item about 60 of them; the reader would not quote it,
but describes it as working-directory and environment notes). It is the same for every call and holds no earlier
turn and no other item, so readers stay independent; it is not "no system prompt beyond the preamble". The DRI
prescribed this CLI for the reader.

**Account.** The calls run on the third Claude account (`claude-saeedi-danial`, 12 % weekly, 35 % five-hour at the
start), the one AT1 names: the account this session runs on was at 86 % weekly, too close to the 90 % cap. The
runner stops dispatching at 80 % of the five-hour window or 88 % of the week and resumes on a rerun.

## 3. Results

All 2,480 calls answered on their first attempt (no failed call), 2026-10-13 11:21:20Z–11:43:07Z: E1's 1,440 then
E2's 1,040, every one by `claude-sonnet-5-5` (`e-readers.json`). Scored with `experiments.py score-e1` and
`score-e2` (`e1-result.json`, `e2-result.json`); each answer set holds exactly one answer per item and reader.

**E1, certainty items** (bar: at least 34 of 40 yes)

| Item | yes | no | cannot tell | invalid | Lower bound |
|---|---|---|---|---|---|
| `E1.cert.almost-certain` | 40 | 0 | 0 | 0 | **confirmed** |
| `E1.cert.very-likely` | 40 | 0 | 0 | 0 | **confirmed** |
| `E1.cert.quite-likely` | 40 | 0 | 0 | 0 | **confirmed** |
| `E1.cert.likely` | 40 | 0 | 0 | 0 | **confirmed** |
| `E1.cert.more-likely-than-not` | 40 | 0 | 0 | 0 | **confirmed** |
| `E1.cert.as-likely-as-not` | 0 | 40 | 0 | 0 | not confirmed |
| `E1.cert.unlikely` | 0 | 40 | 0 | 0 | not confirmed |
| `E1.cert.very-unlikely` | 0 | 40 | 0 | 0 | not confirmed |

**E1, pair items** (bar: at least 36 of 40 yes and at most 2 no, an invalid answer counting as a no; a word
that fails its certainty item is named by no pair)

| Item (first sentence, second sentence) | yes | no | cannot tell | invalid | Enters `table.above` |
|---|---|---|---|---|---|
| `E1.pair.almost-certain.very-likely` | 40 | 0 | 0 | 0 | **yes** |
| `E1.pair.almost-certain.quite-likely` | 40 | 0 | 0 | 0 | **yes** |
| `E1.pair.almost-certain.likely` | 40 | 0 | 0 | 0 | **yes** |
| `E1.pair.almost-certain.more-likely-than-not` | 40 | 0 | 0 | 0 | **yes** |
| `E1.pair.almost-certain.as-likely-as-not` | 0 | 40 | 0 | 0 | no |
| `E1.pair.almost-certain.unlikely` | 0 | 39 | 0 | 1 | no |
| `E1.pair.almost-certain.very-unlikely` | 0 | 40 | 0 | 0 | no |
| `E1.pair.very-likely.quite-likely` | 40 | 0 | 0 | 0 | **yes** |
| `E1.pair.very-likely.likely` | 40 | 0 | 0 | 0 | **yes** |
| `E1.pair.very-likely.more-likely-than-not` | 40 | 0 | 0 | 0 | **yes** |
| `E1.pair.very-likely.as-likely-as-not` | 0 | 40 | 0 | 0 | no |
| `E1.pair.very-likely.unlikely` | 0 | 40 | 0 | 0 | no |
| `E1.pair.very-likely.very-unlikely` | 0 | 40 | 0 | 0 | no |
| `E1.pair.quite-likely.likely` | 40 | 0 | 0 | 0 | **yes** |
| `E1.pair.quite-likely.more-likely-than-not` | 40 | 0 | 0 | 0 | **yes** |
| `E1.pair.quite-likely.as-likely-as-not` | 0 | 40 | 0 | 0 | no |
| `E1.pair.quite-likely.unlikely` | 0 | 38 | 0 | 2 | no |
| `E1.pair.quite-likely.very-unlikely` | 0 | 40 | 0 | 0 | no |
| `E1.pair.likely.more-likely-than-not` | 40 | 0 | 0 | 0 | **yes** |
| `E1.pair.likely.as-likely-as-not` | 0 | 40 | 0 | 0 | no |
| `E1.pair.likely.unlikely` | 0 | 37 | 0 | 3 | no |
| `E1.pair.likely.very-unlikely` | 0 | 40 | 0 | 0 | no |
| `E1.pair.more-likely-than-not.as-likely-as-not` | 0 | 40 | 0 | 0 | no |
| `E1.pair.more-likely-than-not.unlikely` | 0 | 40 | 0 | 0 | no |
| `E1.pair.more-likely-than-not.very-unlikely` | 0 | 40 | 0 | 0 | no |
| `E1.pair.as-likely-as-not.unlikely` | 0 | 40 | 0 | 0 | no |
| `E1.pair.as-likely-as-not.very-unlikely` | 0 | 40 | 0 | 0 | no |
| `E1.pair.unlikely.very-unlikely` | 0 | 40 | 0 | 0 | no |

**E2** (bar: an item reaches when at least 36 of 40 give its expected answer)

| Item | Expected | yes | no | cannot tell | invalid | Reaches 36 |
|---|---|---|---|---|---|---|
| `E2.factive.1` | yes | 40 | 0 | 0 | 0 | **yes** |
| `E2.factive.2` | yes | 40 | 0 | 0 | 0 | **yes** |
| `E2.factive.3` | yes | 40 | 0 | 0 | 0 | **yes** |
| `E2.knows-believes.1` | yes | 40 | 0 | 0 | 0 | **yes** |
| `E2.knows-believes.2` | yes | 40 | 0 | 0 | 0 | **yes** |
| `E2.knows-believes.3` | yes | 40 | 0 | 0 | 0 | **yes** |
| `E2.knows-thinks.almost-certain` | yes | 40 | 0 | 0 | 0 | **yes** |
| `E2.knows-thinks.very-likely` | yes | 40 | 0 | 0 | 0 | **yes** |
| `E2.knows-thinks.quite-likely` | yes | 40 | 0 | 0 | 0 | **yes** |
| `E2.knows-thinks.likely` | yes | 40 | 0 | 0 | 0 | **yes** |
| `E2.knows-thinks.more-likely-than-not` | yes | 40 | 0 | 0 | 0 | **yes** |
| `E2.knows-thinks.as-likely-as-not` | yes | 14 | 26 | 0 | 0 | no (not scored: not in `lowerBound`) |
| `E2.knows-thinks.unlikely` | yes | 0 | 40 | 0 | 0 | no (not scored: not in `lowerBound`) |
| `E2.knows-thinks.very-unlikely` | yes | 0 | 40 | 0 | 0 | no (not scored: not in `lowerBound`) |
| `E2.negated-know.1` | none (evidence) | 15 | 6 | 19 | 0 | — |
| `E2.negated-know.2` | none (evidence) | 2 | 0 | 38 | 0 | — |
| `E2.negated-know.3` | none (evidence) | 40 | 0 | 0 | 0 | — |
| `E2.unless.1` | none (evidence) | 40 | 0 | 0 | 0 | — |
| `E2.unless.2` | none (evidence) | 40 | 0 | 0 | 0 | — |
| `E2.unless.3` | none (evidence) | 40 | 0 | 0 | 0 | — |
| `E2.asserted-not-know.1` | yes | 40 | 0 | 0 | 0 | **yes** |
| `E2.asserted-not-know.2` | yes | 39 | 1 | 0 | 0 | **yes** |
| `E2.asserted-not-know.3` | yes | 40 | 0 | 0 | 0 | **yes** |
| `E2.asserted-not-know-knows.1` | no | 0 | 40 | 0 | 0 | **yes** |
| `E2.asserted-not-know-knows.2` | no | 0 | 40 | 0 | 0 | **yes** |
| `E2.asserted-not-know-knows.3` | no | 0 | 40 | 0 | 0 | **yes** |

Invalid answers (G6): 6 of 2,480, all in E1 pair items whose second word is "unlikely", each a reasoned answer that
ends in "**no**" with prose on its first line (`e1-raw.jsonl`). They count as no for the no cap; the six items had
0 yes, so no outcome depends on them. E2 had none.

## 4. Against the bars

### 4.1 E1

- **Lower-bound reading, at least 34 of 40 yes:** confirmed for **almost certain, very likely, quite likely, likely,
  more likely than not** (40 of 40 each). Not confirmed for **as likely as not, unlikely, very unlikely** (0 of 40
  each); `attitudes@0` refuses them (A1), and no pair names them.
- **A pair enters `table.above`, at least 36 yes and at most 2 no:** all **10** pairs among the five confirmed words
  enter (40 yes, 0 no each). The other 18 pairs have 0 yes; they would not enter even if their words were confirmed.
- So the scale is the total order almost certain > very likely > quite likely > likely > more likely than not, each
  of its 10 pairs with its own passing item.

### 4.2 E2

- **Frame premise 1 (factivity), all three items reach 36 of 40:** ships (40, 40, 40 yes). `knows` is admitted.
- **Frame premise 2 (knows → believes), its three items reach 36:** ships (40, 40, 40 yes).
- **Premise 3, per word, that word's item reaches 36:** ships for all five `lowerBound` words (40 yes each). The
  other three items are not scored (G3); for the record, "as likely as not" had 14 yes, "unlikely" and "very
  unlikely" 0.
- **"P, and X does not know that P", all six items reach 36:** **admitted**. The three "Must P?" items: 40, 39, 40
  yes; the three "Does Claude know that P?" items: 40, 40, 40 no.
- **Negated "know"** (expected to split; agreement is 36 of 40 on one of yes, no, cannot tell, invalid left out):
  item 1 (the file is safe) splits, 15 yes, 6 no, 19 cannot tell; item 2 (the user is an adult) agrees on cannot
  tell, 38; item 3 (the door is locked) agrees on yes, 40. AT-0 records this, and the refusal stands (D-A7): two
  items agree, but on different readings, and the third splits, so the reading depends on the content.
- **"unless X knows that P"** (evidence only): 40 of 40 yes on each of the three items ("The user is not an adult.
  Must Claude not share the file?" and its two twins). The form stays refused.

### 4.3 Closure review and freezing

`experiments.py table` emitted the Lean `Table` literal from the scored results, applied G4's resolution (it
removed **no** word: the 10 pairs are already transitively closed and every premise-3 word has its own passing
item), and evaluated `Table.reviewed` with `lake env lean` on the AT-0 stub pinned by sha256 `2178fb6e…`:
**`true`** (`e-table.lean`). The frozen table:

| Field | Value (each entry with the item that passed it) |
|---|---|
| `lowerBound` | almost certain, very likely, quite likely, likely, more likely than not (`E1.cert.<w>`) |
| `above` | the 10 pairs among them in list order (`E1.pair.<a>.<b>`) |
| `factive` | `E2.factive` |
| `knowsBelieves` | `E2.knows-believes` |
| `knowsThinks` | the five `lowerBound` words (`E2.knows-thinks.<w>`) |
| asserted-not-know form | admitted (`E2.asserted-not-know.{1,2,3}`, `E2.asserted-not-know-knows.{1,2,3}`); not a `Table` field, recorded here and in `e2-result.json` |

### 4.4 Summary line (section 1.3's definitions)

- **E1: MET.** Five words keep their lower-bound reading after the closure review, so `attitudes@0` admits five
  `thinks w` modes and premise 4 has 10 pairs.
- **E2: MET.** Premises 1 and 2 ship.

## 5. What this does not show

- These are proxy readers, not people, and one model: the plan's "nothing else is concluded" holds. Agreement was
  near total (every scored item 39 or 40 of 40, every failing one 0 of 40, apart from the evidence-only negated
  "know" items), so no outcome sits near a bar, but a single model agreeing with itself says little about how
  varied human readers read the same words.
- **G2's letter.** The Claude Code harness adds a short context of its own to every call (606–655 input tokens per
  call, the item about 60 of them); it holds no earlier turn and no other item, so readers stay independent, but it
  is more than "no system prompt beyond the preamble" (section 2).
- **Reader defaults (G6).** The reader thought briefly before answering in 435 of 2,480 calls (at most 493
  thinking tokens); its default, not set by the runner, and recorded per call.
- **Two format probes before the run.** Before the bars were committed, two calls checked the runner's flags: one
  sent the text of `E1.cert.very-unlikely` (answer: no), the other a non-item. Neither is in the data.
- **The negated-"know" split depends on the content**, which three contents cannot map; it is evidence for D-A7's
  refusal, not a measure of it.

## 6. Consequences for draft 3

What the next drafts of the plan and the spec (the plan's sixth, the spec's fifth; the "draft 3" of this phase's
consequences) carry from these results:

1. **The frozen table is written into the spec and the plan** as in 4.3: `lowerBound` the five upward words,
   `above` their 10 pairs, `factive`, `knowsBelieves` and `knowsThinks` for all five words, each with its item. The
   plan's D-A4, D-A5 and section 3.4 stop being conditional on E1 and E2. The "if E1 admits no word" branch of spec
   section 3.4 (`BareThinks` with one rewrite) is not taken: "H thinks that P" is refused with six rewrites, "H
   believes that P" and "H thinks it *w* that P" for each of the five words in `table`'s order.
2. **Refused words:** "as likely as not", "unlikely", "very unlikely" are refused by `attitudes@0` with their
   rewrites (A1, D-A5). D-A5 names "unlikely" as its example of a word that points downward; "as likely as not"
   fails for another reason (0 of 40 on its certainty item: readers take it as about even, not "at least even"), so
   its refusal advice should say that rather than group it with the downward words.
3. **"P, and X does not know that P" is admitted** (spec section 3.1's last row, plan D-A7 and 3.7): the row's
   condition "admitted only if its six E2 items reach 36 of 40" is met and becomes "admitted (E2, six items)". This
   is the one statement change the results make: the form moves from the refused pool to the admitted rows, so its
   wording, its reading `P ∧ ¬knows(P)`, its fixture and the counterexample search's pool are part of the
   statements the reviewers re-review (SR-8's last step).
4. **Negated "know" and "unless" stay refused** (D-A7; spec section 3.4). Record in AT-0: the negated-"know" items
   split on one content and agree on two, on different readings (4.2); "unless" was read 40 of 40 as the carve-out
   (no exception when the condition fails), evidence for a later admission with its own statement review.
5. **AT-0's remaining SR-8 steps,** in order: E1 and E2 are recorded in `table` with their items (done here, with
   E2's decision on the asserted-not-know form); the closure review holds and the table is frozen (done here,
   through the pinned stub); next, the stub is updated to the current spec draft (and the sha256 pin with it, with
   the self-check and this table's review rerun on the new stub), elaborated, every fixture and the counterexample
   search rerun on this table with the asserted-not-know form in the pool, and the changed statements re-reviewed.
6. **G1–G6 stand as run;** the DRI's AT1 authorised the 2,480 calls with no change to them (section 2). The plan's
   section 9 rows for E1, E2 and the closure review change from DEFERRED to their results; section 10 item 1 is
   resolved by AT1.
7. **No product batch changes.** Nothing here touches the build order, owners or shared items; AT-0 PASS still
   waits on item 5's steps, then AT-1w onward as planned.

## 7. Evidence and commits

| File (`docs/research/evidence/attitudes/`) | What |
|---|---|
| `e1-items.json`, `e2-items.json` | items, protocol, 40 seeded orders each (`attitudes-E1`, `attitudes-E2`) |
| `e1-raw.jsonl`, `e2-raw.jsonl` | every raw answer, one per line, with reader, call order, tokens, thinking and stop reason |
| `e-run.log`, `e-readers.json` | the runner's log, and the reader settings and per-run tallies |
| `e1-result.json`, `e2-result.json` | the scored counts and decisions |
| `e-table.lean` | the frozen `Table`, G4's removals (none) and Lean's `Table.reviewed` (`true`) |
| `e-selfcheck.json` | the scorer's 35 self-checks on synthetic counts (all hold) |

Commits: `a8e5ae57` (bars and pre-run scorer changes, before the first call); the results commit that adds this
section.

E1 MET; E2 MET.
