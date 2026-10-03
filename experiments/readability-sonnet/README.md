# VE readability and writability eval (proxy: Claude Sonnet 5.5)

This directory holds a small usability eval for Verifiable English. Claude Sonnet 5.5 stands in for a reader or writer
who has had **no training** in VE. It has 30 reading items and 15 writing tasks. Every reading key and every writing
score comes from VE's own checker, not from a person's judgment.

**Status: sealed before any run.** No model was called to build it. Results must be labelled
"proxy: Claude Sonnet 5.5, upper bound for careful readers". [MANIFEST.sha256](MANIFEST.sha256) lists the SHA-256
of every sealed file; none of them is edited after the seal commit. Run records go under `runs/`, and results go in
`RESULTS.md`; neither is sealed.

## Drops (applied before the seal)

An independent pre-run check (`manage-agents/readability-check.final.md`) reran every key and asked for these drops:

- **W07** (risk, sufficient condition). The scorer compares the condition as text, so a correct paraphrase can never
  score `correct` and a wrong condition can never count as silent-wrong. The legend line "Comparison: <quantity> is
  greater than <quantity>" was written by the builder, not VE. `writing_spec.DROPPED` keeps the definition, and no
  context is built.
- **The VE-C condition of R05, R12 and R14.** Their keys come only from a legend line (the declared default), so
  in VE-C the text decides nothing. R05's VE-C was byte-identical to R04's, which has a different key.
  `build.DROPPED_CONDITIONS` removes the condition, and their VE-L condition is kept.

After the drops there are 30 reading items: 30 in VE-L, 27 in VE-C and 7 in EN. Each is answered by 2 sessions, so
there are 128 reading sessions. There are 14 writing tasks, and 28 writing sessions. Wherever the counts below say 15
tasks or 30 VE-C items, they describe the build before the drops. The rebuild after the drops changed nothing else:
every other context file is byte-identical to commit `2299dcc8`.

The check also listed minor issues that are not drops. They are left unchanged, so the scorer is the one that was
reviewed:

- `score.py` counts two unparsed answers as agreeing.
- `score.py` scores a DNS answer to R07 (key CONFLICT) as critical.

RESULTS.md reports whether either case occurred.

## The rule: only what a human user would get

The rule, as given:

> RULE: the reader/writer gets ONLY what a human user would get: the VE text exactly as VE renders it for readers
> (natural view), the editor legend/explanation lines VE shows for the words used, at most 5 example VE sentences,
> and the question. No grammar, no spec, no hints about intended answers.

How the files apply it:

- **The VE text** is VE's rendering, produced by the function listed for each item under `rendering.renderer` in
  [items.json](items.json):
  - norm rules: `ve.norm_english.render_english`;
  - formulas: the audited natural view, `ve.printer.natural_document`, or `ve.prose@1`'s `render_presentation`;
  - rights: `ve.surface.rights.render_unit`;
  - soft-norm declarations: `ve.surface.softnorms.render_declaration`.

  The build checks that each excerpt is VE's rendering of its own AST and re-parses with one reading. Two
  exceptions, listed under "Construction findings": the risk decision record and the speech-act question line.
- **The legend** holds only lines for words the VE text uses:
  - VE's completion sentences (`ve.norm_defaults_english.legend`: "By default, …", "When nothing else in the text
    decides, …");
  - the risk route's explanation lines, the speech-acts legend, and the soft-norm declarations;
  - one line per sort, predicate and constant, taken from `ve.english.english_legend`: the selected wording with each
    argument shown as `<noun>`, then the declared description.

  The VE-C condition shows no legend.
- **Examples.** Reading contexts have none. Each writing context has at most five, one fixed set per family. Each
  set uses a different vocabulary from its tasks, or no example in it is a correct answer. Every example is VE's
  own wording and parses in VE.
- **The question** gives the situation in plain English. It is identical in every condition. Each question has three
  or four options, and "The text does not say." is always the last one.
- **What sessions never see.** No session sees a grammar, a spec excerpt, a key, a VE verdict or a deciding rule.
  The `world_knowledge` notes and `en_note` fields in items.json are for analysis only.

## Pre-registered design (orchestrator, fixed before any run; recorded verbatim)

> PRE-REGISTERED DESIGN (orchestrator, fixed BEFORE any run; record it verbatim in README.md):
> CONDITIONS (reading): each reading item is answered in three conditions by separate fresh sessions: VE-L (VE natural view + the editor legend lines), VE-C (VE natural view only, no legend), EN (the original plain-English source text of the same excerpt, where the use case has one; mark items without a source as VE-only). Same question and options in all conditions.
> WRITING LOOP: each writing task allows up to 3 attempts; after a failed attempt the session receives exactly VE's own error message / rephrasing suggestion for that attempt (what the editor would show), nothing else. Record first-try and within-3 outcomes.
> REASONS: every answer includes a one-sentence reason; record it (for qualitative analysis of text-based vs world-knowledge answers).
> METRICS:
> - Reading: accuracy per condition; CRITICAL misreadings (opposite verdict, e.g. permitted vs forbidden, or a definite answer where the key is "The text does not say", or "does not say" where the text decides) per condition; abstention correctness; two-session agreement; per-construct breakdown (should/soft norms, unspecified defaults, might/cannot risk, rights, pronouns/discourse, exceptions/unless, precedence, speech acts); per-item rendering type (natural vs explicit-form fallback).
> - Writing: parse rate, one-reading rate, meaning-correct rate, SILENT WRONG MEANING rate (parses with one reading but not equivalent to gold), first-try vs within-3, per construct, and which VE error messages led to a fix.
> - Report counts with Wilson 95% intervals; label results "proxy: Claude Sonnet 5.5, upper bound for careful readers".
> PASS BARS (fixed now): critical misreadings in VE-L <= 2%; VE-L accuracy >= EN accuracy on items that have EN; two-session agreement >= 90% in VE-L; writing silent-wrong-meaning <= 5%; meaning-correct within 3 attempts >= 80%. Report each bar met / not met.

## Operational protocol (worker; fixed with the build, before any run)

These details implement the design above and were fixed before any session ran.

### Sessions

- **Model and setup.** Model `claude-sonnet-5-5`, run by [run.py](run.py):
  - The command is `claude -p --model claude-sonnet-5-5 --tools "" --strict-mcp-config --disable-slash-commands
    --output-format json --verbose`, with `CLAUDE_CONFIG_DIR` from `pick-claude-account.sh`.
  - Each session runs in its own empty temporary directory under `/tmp`, outside the repo.
  - **Correction to the line written at build time.** The session is not free of any system prompt: it has Claude
    Code's default one. What it lacks is any CLAUDE.md (no account config has one, and the directory is empty),
    memory content, tools, MCP servers and skills. The init record of every call is stored as proof.
  - **One item per session.** The orchestrator allowed up to 6 items per session, never two from the same excerpt.
    One item per session meets that, and it keeps each session's input byte-identical to one sealed file.
  - **Order.** All sessions are shuffled with `random.Random(20261003)`. `runs/order.json` records the order.
- **Reading.** For each item and each of its conditions, two separate sessions (`s1`, `s2`) each receive
  `contexts/<item>/<condition>.txt` as their only user message. That means 30 × 2 VE-L, 27 × 2 VE-C and 7 × 2 EN
  sessions, 128 in all (see "Drops"). The reply must contain `ANSWER: <letter>` and `REASON: <one sentence>`. A reply without a
  parseable letter counts as wrong and not critical, and is reported as unparsed.
- **Writing.** Each task gets two sessions (`s1`, `s2`). A session starts with `contexts/<task>/attempt1.txt`.
  - The scorer reads the `SENTENCE:` line and runs `score.py check <task> "<sentence>"`.
    - A reply with no `SENTENCE:` line is scored as the empty sentence.
    - A wrapper around the whole sentence (backticks, quotes or `**`) is removed first, because a person would not
      type it into the editor.
    - Later turns resume the same conversation (`--resume`) with the same account and directory.
  - If the outcome is `correct`, the session stops.
  - Otherwise, up to three attempts in total, the next user message in the same conversation is
    `contexts/<task>/retry.txt` with `{ve_message}` set to the `ve_message` that `check` printed and `{attempt}` set
    to the attempt number.
  - `ve_message` is VE's error message for a parse failure or ambiguity (the parser rejects every sentence that has
    more than one derivation). For a sentence that parses, it is VE's paraphrase of its one reading, which is what the
    editor displays.
  - The re-prompt itself tells the session its attempt was not accepted. This is unavoidable in a loop that stops on
    success, and it is a limitation.
- **Response files.** The formats for `reading.jsonl` and `writing.jsonl` are in the docstring of
  [score.py](score.py). The session's raw reply may be stored instead of the parsed answer.

### Reading metric definitions

`score.py report` computes all of these.

- **Accuracy** is correct answers over all responses in the condition.
- **Critical misreading** is a wrong answer that is either an opposite verdict or involves "The text does not say"
  (the "DNS" label) on one side. The opposite pairs are:
  - PERMITTED/FORBIDDEN;
  - REQUIRED/NOT-REQUIRED;
  - YES/NO;
  - MIGHT/CANNOT;
  - FOLLOWS/GAP.

  The DNS cases are a definite answer where the key is DNS, or DNS where the key is definite. Confusing CONFLICT with
  another label is wrong but not critical.
- **Abstention correctness** is reported two ways:
  - **recall:** DNS answers among items whose key is DNS;
  - **precision:** keys that are DNS among DNS answers.
- **Two-session agreement** is the share of item × condition pairs where `s1` and `s2` gave the same letter.
- **Breakdowns.** Results are broken down by construct, by rendering form (`natural` or `explicit form`), by
  rendering type, by whether the item depends on the legend, and by whether world knowledge points elsewhere.
- **VE-L vs EN.** VE-L accuracy is compared with EN accuracy on the same seven items, the ones that have an EN
  condition.

### Writing metric definitions

- **Unit.** The unit is a task × session (14 × 2 = 28 after the drop of W07). Each attempt is rescored mechanically.
- **Outcomes per attempt.** Each attempt gets one of these outcomes:

  | Outcome | Meaning |
  |---|---|
  | `parse_failure` | VE rejects the sentence |
  | `ambiguous` | VE reports two derivations |
  | `not_one_sentence` | the text parses to more than one sentence |
  | `wrong_meaning` | one reading, not equivalent to the gold |
  | `correct` | one reading, equivalent to the gold |
  | `unknown` | VE's equivalence check returned UNKNOWN |
  | `condition_unverified` | risk only; see below |

- **First-try rates.** All are taken over first attempts:
  - parse rate: not `parse_failure`;
  - one-reading rate: one reading;
  - meaning-correct: `correct`;
  - silent wrong meaning: `wrong_meaning`.
- **Within-3 rates.** These use each session's final attempt:
  - meaning-correct: `correct`;
  - **silent wrong meaning: `wrong_meaning`. This is the number the pass bar uses.**
- **Also reported.** The per-attempt silent-wrong rate, results per construct and per family, and every VE message
  that was followed by a correct attempt.
- **Equivalence rule for each family:**
  - **Formulas:** `ve.equivalence.compare` must return EQUIVALENT, which requires two replayed certificates.
  - **Rules:** the editor numbers an unnumbered rule. The attempt, added after any existing rules of the task, must
    give the regulated predicate a completed outcome equivalent to the gold's. The comparison uses
    `ve.equivalence.compare` at fresh constants under the declared default, over the base vocabulary. The attempt's
    document must also be CONFLICT-FREE under `ve.norms.check_conflict`, because two rules that clash can produce
    the same outcome formula as the gold.
  - **Risk record statements:** the attempt must give the same registered reading under
    `ve.surface.risk.parse_wording`: form, action and harm. There are two caveats:
    - VE's record parser compares labels case-sensitively, and every label begins in lower case. The scorer
      lower-cases a capital first letter, as the build does when it checks the displayed record.
    - The condition of a conditional statement is compared as text after whitespace normalisation, because no Python
      decoder for record condition text exists. If only the condition text differs, the outcome is
      `condition_unverified`. It counts as not correct and is **not** counted as a silent wrong meaning.

### Pass bars

Each bar is judged met or not met on its point estimate, and its Wilson 95% interval is shown beside it. With 60
VE-L responses (VE-L keeps all 30 items), the critical-misreading bar (≤ 2%) allows at most one critical misreading. Even with zero, the upper
bound of the interval is 6.0%. The sample cannot show that the true rate is below 2%.

## Files

| File | What it is |
|---|---|
| [items.json](items.json) | The 30 reading items. Each has its question and options, the key letter and label, the VE text, the legend lines, rendering data, the EN text and source (or why the item is VE-only), its conditions, world-knowledge notes, `ve_command`, and `ve_output` (the literal stdout of `ve_command`, the checker verdict that justifies the key). |
| [writing.json](writing.json) | The 15 writing tasks. Each has its intention, environment, gold, the gold's own VE wording (`gold_surface`, used only to check that the scorer accepts the gold), `gold_check`, the equivalence method, the examples, the legend, and `score_command`. |
| `contexts/R??/{VE-L,VE-C,EN}.txt` | The exact text each reading session sees. |
| `contexts/W??/attempt1.txt`, `retry.txt` | The exact first message of each writing session, and the retry template. |
| [score.py](score.py) | Mechanical scoring: `check` (one writing attempt) and `report` (metrics, Wilson intervals, pass bars). |
| [build.py](build.py), [items_spec.py](items_spec.py), [writing_spec.py](writing_spec.py), [vekit.py](vekit.py) | The builder, the item and task specs (written before any run), and the shared VE calls. |
| [run.py](run.py) | The session runner (the protocol is in its docstring). It writes `runs/` (not sealed): one record per session with the raw reply, the CLI result and init record, and every writing turn's check. It also writes `runs/reading.jsonl` and `runs/writing.jsonl` for `score.py report`. |
| [results.py](results.py) | Writes `RESULTS.md` from `runs/`. It uses score.py's metrics and bars, and adds every answer and attempt, the 3 hardest constructs (ranking rule in its docstring) and the flagged scorer cases. |
| [MANIFEST.sha256](MANIFEST.sha256) | `sha256sum` of every sealed file, paths relative to this directory. Check with `sha256sum -c MANIFEST.sha256` here. |
| [ve_key.py](ve_key.py) | `uv run python experiments/readability-sonnet/ve_key.py R07` recomputes one item's key and prints the VE verdict. |
| `sources/R23–R25/speech.ve.md` | The `ve-document@2` files the speech-act items were checked with (`python -m ve speech-acts`). |

**Reproduce.** Lean must be built first, because the risk items use `lean/.lake/build/bin/ve_risk_route`. Then:

```sh
(cd lean && PATH=~/.elan/bin:$PATH lake build)
uv run python experiments/readability-sonnet/build.py   # about 20 s; rewrites items.json, writing.json, contexts/
```

The build reruns every `ve_command` and requires its output to match the verdict it computed. It also requires every
writing gold to score `correct`. These files were built at commit `a093a14d` (main).

## Counts by feature

### Reading (30 items)

| Use case or feature | Items | Keys | With EN |
|---|---|---|---|
| agent-policy (norms@0 + norm-defaults@0) | 7 | R01 FORBIDDEN, R02 PERMITTED, R03 FORBIDDEN, R04 DNS, R05 FORBIDDEN, R06 REQUIRED, R07 CONFLICT | 0 |
| norm-defaults `unspecified`, fixture u1 (constitution u0165.s07) | 2 | R08 DNS, R09 FORBIDDEN | 2 |
| asimov-laws (rules 1, 2, 3, 8, 11) | 3 | R10 FORBIDDEN, R11 REQUIRED, R12 PERMITTED | 2 |
| safety-framework (FSF v3.1, rules.d1.ve) | 2 | R13 NOT-REQUIRED, R14 FORBIDDEN | 1 |
| soft norms (`should`, ranks) | 2 | R15 REQUIRED, R16 FORBIDDEN | 0 |
| risk@0, Decision 17 (out-of-memory) | 4 | R17 MIGHT, R18 CANNOT, R19 FORBIDDEN, R20 CANNOT | 0 |
| discourse: pronouns in `ve.prose@1` | 2 | R21 YES, R22 DNS | 0 |
| speech-acts@0 | 3 | R23 FOLLOWS, R24 GAP, R25 REQUIRED | 0 |
| US Constitution, 14th Amendment, s1 (entailment) | 3 | R26 YES, R27 DNS, R28 YES | 2 |
| rights@0 (UDHR Art. 3, state-negative reading) | 2 | R29 FORBIDDEN, R30 DNS | 0 |
| **Total** | **30** | 5 DNS keys; 11 items where world knowledge points elsewhere; 3 legend-dependent | **7** |

**By construct.** An item can count under more than one construct:

| Construct | Items |
|---|---|
| precedence | 10 |
| entailment | 7 |
| exceptions/unless | 6 |
| unspecified defaults | 4 |
| might/cannot risk | 4 |
| declared defaults (deny/allow) | 3 |
| speech acts | 3 |
| should/soft norms | 2 |
| pronouns/discourse | 2 |
| rights | 2 |

**By rendering form:** 23 natural and 7 explicit form. R10 to R14 use the `classified as "…"` fallback wording;
R23 and R24 are the audited natural view's explicit form. R26 and R27 are natural by VE's classification but use
"first clause: … end first clause" scaffolding, which is recorded in `rendering.explicit_notation`. The key letters
are A 11, B 14 and C 5. The order of
the non-DNS options is shuffled per item from a hash of the item id.

### Writing (15 tasks)

| Family | Tasks | Constructs |
|---|---|---|
| rules (norms@0) | 5 | permission, prohibition, `unless`, obligation, precedence (exception header), the declared default |
| risk record statements (risk@0) | 2 | `cannot lead to`; a sufficient condition (the out-of-memory example) |
| formulas (relational-fol@0) | 8 | universal, relative clause, conjunction, binary relation, negation, named constant, negated existential, existential scope, disjunction |

## Reading items

DNS means the key is "The text does not say." EN is "yes" when the item has an EN condition. "Legend-dependent"
means VE's answer comes from a completion sentence ("By default, …") that only VE-L shows.

| Item | Use case / feature | Constructs | Key (VE verdict) | EN | Rendering | Legend-dependent | World knowledge differs |
|---|---|---|---|---|---|---|---|
| R01 | agent-policy | exceptions/unless, precedence | A = FORBIDDEN | no | natural (norm rule surface) |  |  |
| R02 | agent-policy | exceptions/unless, precedence | A = PERMITTED | no | natural (norm rule surface) |  |  |
| R03 | agent-policy | precedence | A = FORBIDDEN | no | natural (norm rule surface) |  | yes |
| R04 | agent-policy | unspecified defaults, exceptions/unless | C = DNS | no | natural (norm rule surface) |  | yes |
| R05 | agent-policy | declared defaults (deny/allow), exceptions/unless | A = FORBIDDEN | no | natural (norm rule surface) | yes | yes |
| R06 | agent-policy | precedence | B = REQUIRED | no | natural (norm rule surface) |  | yes |
| R07 | agent-policy | precedence | B = CONFLICT | no | natural (norm rule surface) |  | yes |
| R08 | norm-defaults (constitution u0165.s07) | unspecified defaults | C = DNS | yes | natural (norm rule surface) |  | yes |
| R09 | norm-defaults (constitution u0165.s07) | unspecified defaults | B = FORBIDDEN | yes | natural (norm rule surface) |  |  |
| R10 | asimov-laws | precedence | A = FORBIDDEN | yes | explicit form (norm rule surface) |  |  |
| R11 | asimov-laws | precedence | A = REQUIRED | yes | explicit form (norm rule surface) |  |  |
| R12 | asimov-laws | declared defaults (deny/allow) | B = PERMITTED | no | explicit form (norm rule surface) | yes |  |
| R13 | safety-framework | exceptions/unless, precedence | B = NOT-REQUIRED | yes | explicit form (norm rule surface) |  |  |
| R14 | safety-framework | exceptions/unless, declared defaults (deny/allow) | B = FORBIDDEN | no | explicit form (norm rule surface) | yes | yes |
| R15 | soft-norms | should/soft norms | B = REQUIRED | no | natural (norm rule surface) |  |  |
| R16 | soft-norms | should/soft norms, precedence | A = FORBIDDEN | no | natural (norm rule surface) |  |  |
| R17 | risk (decision 17) | might/cannot risk | B = MIGHT | no | natural (risk rules and decision record) |  |  |
| R18 | risk (decision 17) | might/cannot risk | B = CANNOT | no | natural (risk rules and decision record) |  |  |
| R19 | risk (decision 17) | might/cannot risk, precedence | A = FORBIDDEN | no | natural (risk rules and decision record) |  |  |
| R20 | risk (decision 17) | might/cannot risk | B = CANNOT | no | natural (risk rules and decision record) |  |  |
| R21 | discourse (ve.prose@1) | pronouns/discourse, entailment | A = YES | no | natural (ve.prose@1) |  |  |
| R22 | discourse (ve.prose@1) | pronouns/discourse, entailment | C = DNS | no | natural (ve.prose@1) |  | yes |
| R23 | speech-acts | speech acts, entailment | A = FOLLOWS | no | explicit form |  |  |
| R24 | speech-acts | speech acts, entailment | B = GAP | no | explicit form |  | yes |
| R25 | speech-acts | speech acts | A = REQUIRED | no | natural (speech-act wording) |  |  |
| R26 | us-constitution-14th-s1 | entailment | B = YES | yes | natural (audited natural view, clause scaffolding) |  |  |
| R27 | us-constitution-14th-s1 | entailment | C = DNS | yes | natural (audited natural view, clause scaffolding) |  | yes |
| R28 | us-constitution-14th-s1 | entailment | B = YES | no | natural |  |  |
| R29 | rights (UDHR Art. 3) | rights | B = FORBIDDEN | no | natural (rights unit surface) |  |  |
| R30 | rights (UDHR Art. 3) | rights, unspecified defaults | C = DNS | no | natural (rights unit surface) |  | yes |

### How each key is computed (`ve_key.py ITEM`)

- **Norm items** (agent-policy, norm-defaults, Asimov, safety-framework, soft norms).
  - The excerpt is parsed with `ve.norm_english.parse_english`. It is checked under `norm-defaults@0` with
    `ve.norm_defaults.UnspecifiedDocument` (`UnspecifiedSoftDocument` for soft norms).
  - The answer is the status at the queried point in the situation: SETTLED yes/no or UNDECIDED, with VE's paraphrase
    from `status_sentence` (for example "The text says act must not be performed (rule 3).").
  - `check_conflict` then searches the finite situation for a conflict witness. R07's witness is the seeded defect D1.
  - The `deny` and `allow` completions are the same route with a declared default.
- **Risk.** The Lean risk route (`ve.risk.run_case`, `risk-decision`) runs on the `conformance/risk.py` fixtures for
  `agent-ops`, `log_l17` and `decision_17`. MIGHT means the cell is in the might table. CANNOT means it is not in the
  might table and is not merely assumed ruled out. The permitted or forbidden status comes from `statuses`. R20 uses
  `log_l17(e1=("6", "7"))`.
- **Prose and the 14th Amendment.**
  - The premises are the rendered sentences (the excerpt's claims) plus the question's facts, written in VE and parsed
    by VE.
  - YES means a replayed tableau certificate for the conclusion. NO means one for its negation.
  - DNS means checked countermodels exist both ways (`find_countermodel`).
- **Speech acts.**
  - Follows questions: `SpeechDocument.check_consequence_certificate` on a found proof gives FOLLOWS. A countermodel
    gives GAP.
  - Commands: the policy is completed with `SpeechDocument.complete_model`.
- **Rights.** `ve.norm_defaults.UnspecifiedRightsDocument.status`, with both acts declared `unspecified`.

### EN condition

EN shows the use case's own source sentences for the excerpt, and only where the source supports VE's answer. The EN
key is always VE's key. The seven EN items, with their sources:

| Items | Source |
|---|---|
| R08, R09 | "Claude should never generate child sexual abuse material." (constitution unit u0165.s07) |
| R10, R11 | Asimov's three laws, from "Runaround" (`usecases/asimov-laws/source.md`) |
| R13 | The FSF sentences quoted in the `f2` and `f3` block headers of `rules.d1.ve` |
| R26, R27 | The Citizenship Clause (`usecases/us-constitution-14th-s1/source.md`) |

The other 23 items are VE-only, and each has a reason in `en_note`:

- agent-policy was written directly in VE, so it has no source text.
- R12's permission is the environment's allow default. The Asimov README calls that a modeling choice that the source
  does not make.
- The `f12-u` header quotes no source sentence, and the FSF PDF is not committed.
- The soft, risk, prose and speech-act items come from fixtures written in VE.
- R28's translation turns the Due Process prohibition into a stated fact, so the source would give a different key.
- For rights, the bearer and polarity are this translation's reading of Art. 3.

## Writing tasks

| Task | Family | Constructs | Intention | Gold (VE wording, never shown) |
|---|---|---|---|---|
| W01 | rules | permission, declared defaults (deny/allow) | The agent may delete files only inside the workspace. | Rule 1. Every agent may delete each file, if that file resides in workspace. |
| W02 | rules | prohibition | The agent must not read confidential files. | Rule 1. Every agent must not read each file, if that file is confidential. |
| W03 | rules | prohibition, exceptions/unless | The agent must not contact a host that is not on the allowlist, unless the user has approved that host. | Rule 1. Every agent must not contact each host, if that host is not allowlisted, unless that host is approved. |
| W04 | rules | obligation | Whenever the agent deletes a file, it must report that file to the user. | Rule 1. Every agent must report each file to the user, if that agent deletes that file. |
| W05 | rules | precedence, prohibition | Add a second rule to the existing rule: even inside the workspace, the agent must not read confidential files. The new rule should win over rule 1. | Rule 2 (exception to rule 1). Every agent must not read each file, if that file is confidential. |
| W06 | risk | might/cannot risk | Asking the user can never cause data loss. | asking the user cannot lead to data loss. |
| W07 (dropped) | risk | might/cannot risk, conditions | If the job's peak memory exceeds the free memory of the server, running the job causes a server outage. | If the peak memory of the job is greater than the free memory of the server, running the job leads to a server outage. |
| W08 | formulas | universal, relative clause, conjunction | Anyone who was born in the United States and is subject to its jurisdiction is a citizen of the United States. | Every person who was born in the United States and is subject to the jurisdiction of the United States is a citizen of the United States. |
| W09 | formulas | universal, binary relation, negation | No state denies the equal protection of the laws to a person who is within its jurisdiction. | For every state, for every person who is within the jurisdiction of that state, it is not the case that that state denies the equal protection of the laws to that person. |
| W10 | formulas | universal, relative clause | Everyone who has a noncitizen parent domiciled in the United States is subject to US jurisdiction. | Every person who has a noncitizen parent domiciled in the United States is subject to US jurisdiction. |
| W11 | formulas | universal, named constant, negation | Claude does not undermine any appropriate mechanism. | For every mechanism that is appropriate, it is not the case that claude undermines that mechanism. |
| W12 | formulas | negated existential | There is no deployed service that is not reviewed. | It is not the case that there is a service such that both of the following hold: first clause: that service is deployed; end first clause; second clause: it is not the case that that service is reviewed; end second clause. |
| W13 | formulas | existential, quantifier scope | A single person owns all the deployed services. | There is a person such that for every service that is deployed, that person owns that service. |
| W14 | formulas | universal, disjunction | Every service is deployed or reviewed, or both. | For every service, either that service is deployed or that service is reviewed, or both. |
| W15 | formulas | universal, named constant, relative clause | Claude follows every relevant guideline. | For every guideline that is relevant, claude follows that guideline. |

Any sentence with an equivalent meaning scores `correct`. For example, "Every deployed service is reviewed." is
correct for W12.

**Environments for each family:**

- **Rules** use an agent-tools vocabulary in agent-policy's style (`writing_spec.norm_env`). Each task's legend shows
  its declared defaults, for example "By default, an agent must not delete a file." Examples come from a separate
  hospital vocabulary.
- **Risk** uses the `agent-ops` environment and the Decision 17 labels. The legend shows:
  - the record's action, harm and quantity labels;
  - the comparison wording;
  - the risk route's explanation lines.

  The examples are four Decision 17 record lines.
- **Formulas** use the use cases' own environments, with their reviewed display overlays. Examples are the natural
  view of five formulas over agent-policy's log vocabulary.

## Construction findings, choices and limitations

Several of these are findings about VE itself. They were recorded while building and are not results of the eval.

1. **Eligibility could not supply a reading item.** VE has no reader wording for the Winter Fuel Payment rules.
   `ve.surface.time.render_quantity_sentence` fails on every rule tried, including R9, R13a/b, R14.1/2 and R16a/b,
   with "No controlled W6 wording for this operation". The rules exist only as ASTs and hand-written glosses.
   Eligibility therefore has no reading item, and the build could not satisfy the brief's request to include it.
2. **There is no Python renderer for risk decision records.** The record text is the canonical IDE rendering in
   `docs/spec/risk.md` 2.5, adapted only for R20's E1 bounds and without the environment id and hash. Every C and T
   line is checked: it parses to one registered reading and renders back to itself. The rule text also comes from risk.md
   2.5. The legend lines come from the Lean risk route.
3. **VE's risk record parser rejects VE's own displayed capitalisation.** "Running the job …" fails with "Risk
   wording has no unique registered reading" because the labels begin in lower case. The writing scorer and the build
   check lower-case the first letter (see the risk scoring caveats above).
4. **Risk record conditions are not decoded in Python.** `parse_wording` accepts any condition text, so "exceeds" and
   "is greater than" cannot be compared by VE. Hence the `condition_unverified` outcome.
5. **Vocabulary lint shapes wording.**
   - The speech-act fixture's declared "is a cat" is rejected, so VE renders `tom is classified as "cat"`. R23 and R24
     show that explicit form.
   - Pruning a vocabulary can change which wordings the lint admits. Asimov's `protects_robot` becomes "is
     protective". Each norm excerpt is therefore kept on the smallest vocabulary that renders it byte-for-byte as the
     full use-case environment does.
   - Writing vocabularies were adjusted to lint-admitted wordings: "resides in workspace" rather than "is in the
     workspace", and "is approved" rather than "is approved by the user".
6. **Discourse.** VE renders a bare "It" only when exactly one named constant was mentioned earlier. After a universal
   or existential sentence it rejects "it" as incomplete. The `web` constant's reviewed display name ("the web front
   end") fails presentation with "needs an English repair or a confirmed display name". Both discourse items use the
   assist example's API constant. Real discourse documents (constitution u0214) are UNFORMALISED and have no verdict.
7. **Excerpts.**
   - Rules are renumbered, and exception edges are kept only between excerpted rules. Contents are byte-for-byte from
     the use case.
   - R07 keeps agent-policy's seeded defect D1 (rule 14 is not an exception to rule 3).
   - The soft-norm rules are rules 4 and 21 of soft-norms.md 2.4, simplified. "Is demeaning" stands in for the
     source's long guard, because the lint rejects "complying with {0} is unsafe".
   - The rights text is VE's `render_unit`. It reads "has the right described by its incident lines; the right
     requires or permits nothing by itself", not rights.md 2.4's "has the right to life".
8. **Environment edits.**
   - The 14th Amendment items add constants (Ann, Ben, Carl, Ohio) to a copy of the use-case environment, and re-bind
     the reviewed display overlay to the new environment id.
   - The Asimov and safety-framework excerpts drop the `alternatives`, `risk` and `soft` blocks they do not use, and
     run under `norm-defaults@0` with their declared defaults unchanged.
   - Soft-norm situations state that no exception was taken, because the exception decision is a base fact that the
     verdict needs.
9. **Situations are plain English in the question.** This keeps the question identical across conditions, as the
   design requires, but it means VE readers never read VE facts. Each key is computed on the closed-world situation
   that the question states. Facts the question does not state are false, and every fact the verdict depends on is
   stated.
10. **Legend lines are VE data in a fixed format.** Completion sentences, the risk legend and declarations are VE's
    verbatim strings. Vocabulary lines are formatted from `english_legend` data, one line per word used, as described
    above. A fully generic VE legend (`render --with-legend`) would also print environment ids and grammar notes.
11. **`world_knowledge` and `legend_dependent` are annotations for analysis.** `legend_dependent` is computed
    mechanically: VE's status sentence says "(by default)". VE-C sessions cannot see completion sentences, so
    legend-dependent items measure the legend's necessity, not reading skill.
12. **Power.** 30 items and 2 sessions per condition is small (see "Pass bars"). Results are an upper bound for
    careful readers: a proxy model that reads every word.
