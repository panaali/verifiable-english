# `ve ask` zero-training reading and writing eval (proxy: Claude Sonnet 5.5)

This directory holds the reading and writing evaluation of plan Q2.6 (docs/spec/question-answering-PLAN.md,
"Q2.6. Evidence and measurement", the zero-training readability row). Claude Sonnet 5.5 stands in for a reader or
writer who has had **no training** in VE. It has 19 reading items and 16 writing tasks. Every reading key and every
writing gold comes from VE's saved Lean answers (`tests/fixtures/ask/*.json`), not from a person's judgment.

**Status: sealed before any run.** No model was called to build it (q2-6); the run, its scorer and its results are
item q2-6b. Results must be labelled "proxy: Claude Sonnet 5.5, upper bound for careful readers".
[MANIFEST.sha256](MANIFEST.sha256) lists the SHA-256 of every sealed file, this README included; none of them is
edited after the seal commit. Run records go under `runs/` and results in `RESULTS.md`; neither is sealed.

The protocol is the frozen readability protocol of 2026-10-03 (`git show
ac91e1e4:experiments/readability-sonnet/README.md`), applied to `ve ask`. Text copied from it is marked *(frozen)*;
what this evaluation changes is marked *(Q2.6)*.

## The rule: only what a human user would get

> RULE: the reader/writer gets ONLY what a human user would get: the VE text exactly as VE renders it for readers
> (natural view), the editor legend/explanation lines VE shows for the words used, at most 5 example VE sentences,
> and the question. No grammar, no spec, no hints about intended answers. *(frozen)*

How the files apply it *(Q2.6)*:

- **The text** is the document as `ve document render <path>` prints it, saved by
  `conformance/question_answering_readability.py capture` in `../evidence/render/`.
- **Reading** (`contexts/R-*.txt`): the text, the question someone asked VE, and VE's answer lines exactly as `ve ask
  <path> <question>` prints them (the saved `result.text`), then the fixed question "What does VE's answer tell you?"
  with five options. Nothing else: no legend, no example, no key, no lead name, no spec excerpt, no DELTA text.
- **Options.** Yes (`YES`); rules it out (`RULES-OUT`); allows it to fail (`ALLOWS-FAIL`); depends on how a sentence
  is read (`BY-READING`); the text does not settle it or VE could not decide (`OPEN`), always last. The first four
  are in an order fixed per fixture by a hash of its id.
- **Keys.** The label of Lean's saved lead: yes → YES, no → RULES-OUT, notNecessarily → ALLOWS-FAIL, by_reading →
  BY-READING, notSettled and unknown → OPEN. A1d is a refusal and has no item: 17 items.
- **The "No." variants** (D4, open question 1). For each "Not necessarily." answer (G3, A3) a second item
  (`R-G3-no`, `R-A3-no`) differs from its source only in the lead line, which reads "No.". Its key is the source's.
- **Writing** (`contexts/W-*.txt`): the text, the intended meaning in plain English, and at most five example
  questions, saved fixture questions of another family's document (`writing.json` `examples`). One task per distinct
  reading of a fixture question: G1 and G2 read the same formula and are one task (`W-G1`): 16 tasks.
- **Gold.** The saved `english.question` reading of the fixture question (`result.ast`, with `result.sentence`).

## Sessions *(frozen, with the Q2.6 files)*

- **Model and setup.** Model `claude-sonnet-5-5`. The command is `claude -p --model claude-sonnet-5-5 --tools ""
  --strict-mcp-config --disable-slash-commands --output-format json --verbose`. Each session runs in its own empty
  temporary directory outside the repo, with no CLAUDE.md, memory content, tools, MCP servers or skills; the init
  record of every call is stored as proof.
- **One item per session.** Each session's input is byte-identical to one sealed file.
- **Order.** All sessions are shuffled with `random.Random(20261003)`; `runs/order.json` records the order.
- **Reading.** Each item is answered by two separate fresh sessions (`s1`, `s2`), each receiving its context file as
  its only user message: 19 × 2 = 38 sessions. The reply must contain `ANSWER: <letter>` and `REASON: <one sentence>`.
  A reply without a parseable letter counts as wrong and not critical, and is reported as unparsed.
- **Writing.** Each task gets two sessions (`s1`, `s2`), starting with its context file. The scorer reads the
  `QUESTION:` line *(Q2.6; the frozen line was `SENTENCE:`)*. A reply with no such line is scored as the empty
  question; a wrapper around the whole question (backticks, quotes or `**`) is removed first. If the outcome is
  `correct` the session stops. Otherwise, up to three attempts in total, the next user message in the same
  conversation (`--resume`) is `contexts/retry.txt` with `{attempt}` set to the attempt number and `{ve_message}` set
  to exactly what `ve ask --reading <path> <question>` prints for that attempt: Lean's refusal text, its advice and
  its rephrasings when VE does not read the question, or the sentence the question is read as when it does (what the
  editor would show). The re-prompt itself tells the session its attempt was not accepted; this is a limitation.

## Metrics *(frozen definitions, Q2.6 labels)*

- **Reading accuracy:** responses that take the key's option, over all responses.
- **Critical misreading:** "allows it to fail" answered as "rules it out", or the reverse (`items.json` `critical`).
  Other wrong answers are wrong but not critical.
- **Two-session agreement:** the share of items where `s1` and `s2` gave the same letter.
- **Writing outcomes per attempt:** `refused` (VE does not read the question: any refusal Lean names),
  `wrong_meaning` (one reading, not equivalent to the gold), `correct` (one reading, equivalent to the gold),
  `unknown` (the equivalence check returned UNKNOWN; not correct and not silent-wrong). Equivalence: the formulas
  rule of the frozen protocol, `ve.equivalence.compare` returns EQUIVALENT, in the document's environment.
- **First try** uses each session's first attempt; **within three** uses its final attempt. **Silent wrong
  meaning** is `wrong_meaning` on the final attempt.
- Counts are reported with Wilson 95% intervals. Each bar is judged met or not met on its point estimate, its
  interval shown beside it, with no rounding up *(frozen; plan Q2.6 "Done when")*.

## Pass bars (registered before any run)

The reading bars R1 to R3 count the 34 responses of the 17 source items (17 × 2 sessions); the "No." variants are
not in them. The variants' own critical misreadings and agreement are reported apart, with no bar.

| Bar | Value | Set by |
|---|---|---|
| R1 critical misreadings | at most 2% (on 34 responses: none) | frozen protocol (ac91e1e4, PASS BARS) |
| R2 two-session agreement | at least 90% | frozen protocol (ac91e1e4, PASS BARS) |
| R3 leads read correctly (B1) | at least 85% (at most 5 of 34 wrong) | proposed by the q2-6 builder, set by the acting DRI (dri-decider), reviews/dri-decisions-20261031-q2-6.md |
| W1 writing silent wrong meaning | at most 5% | frozen protocol (ac91e1e4, PASS BARS) |
| W2 meaning correct within three attempts | at least 80% | frozen protocol (ac91e1e4, PASS BARS) |
| W3 meaning correct on the first try (B2) | at least 50% of the 32 writing sessions | proposed by the q2-6 builder, set by the acting DRI, reviews/dri-decisions-20261031-q2-6.md |
| N1 "No." against "Not necessarily." (B3) | see below | proposed by the q2-6 builder, set by the acting DRI with the tightening of its item 3, reviews/dri-decisions-20261031-q2-6.md |

**N1.** Every "No." variant response (G3 and A3, 2 sessions each: 4 responses) is read as "allows it to fail", none
as "rules it out", and the "No." variants' correct share is at least that of their "Not necessarily." sources.
B3 not met: D4 stays, with no further review. B3 met: open question 1 is reopened as a design question for the DRI
(q2-6b files a design backlog row citing reviews/dri-decisions-20261031-q2-6.md), and D4 stays until that decision.

## Files

| File | What it is |
|---|---|
| [items.json](items.json) | The 19 reading items: fixture, variant, document, question, Lean's lead, the lead lines, options, key letter and label, context path; the critical pairs. |
| [writing.json](writing.json) | The 16 writing tasks: fixtures, document, intention, gold formula and sentence, example fixtures, context path. |
| `contexts/R-*.txt`, `contexts/W-*.txt`, `contexts/retry.txt` | The exact text each session sees, and the retry template. |
| [MANIFEST.sha256](MANIFEST.sha256) | `sha256sum` of every sealed file, paths relative to this directory: `sha256sum -c MANIFEST.sha256`. |

**Reproduce.** `uv run python conformance/question_answering_readability.py build` rewrites every file but this
README from saved files only; `... check` fails when a file differs from the build or the manifest does not verify.
