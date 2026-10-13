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
