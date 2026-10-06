Status: Draft 2 (converged by DRI ruling); plan and pre-registration text; not frozen, not timestamped, no model call made

# Policy audit: do VE's checks find defects in real agent policies that frontier models miss?

2026-10-05. Branch `design/policy-audit`, from `main` at `95a97a07`. Planner: Fable 5.1 (xhigh).
This file is experiment 1 of `~/code/manage-agents/reviews/oversight-opportunities-2026-10.md`
("spec-defect audit of real agent policies"), written as a pre-registration and as a build plan in batches of
2 to 6 hours. It becomes binding only when batch B5 freezes it: line 1 changes to `Status: FROZEN`, a copy goes to
`experiments/policy-audit/PREREG.md` (the path `ve_experiments/runner.py` checks), and the hash is timestamped.

**Draft 2 (2026-10-06).** This text holds the edits both plan reviewers (Fable 5.1, GPT-6 Astra) agreed in
`~/code/manage-agents/debates/design-policy-audit/` (Astra's findings 1 to 6 and Fable's 1 to 9, merged where they
overlap) and the DRI ruling on the two points they left open: the measured VE arm uses Lean-owned admission of
the English it uses (sections 9, 12, 13), and the gap bar's subset is the CHECKED-anchor subset (sections 8, 9).
Main changes: silence means "two admissible completions differ", not "no rule decides"; obligation-permission
conflicts are explained; universal verdicts need a checked situation that meets the stated facts; every report
is adjudicated and matching is semantic; one judge call per variant; a cluster check after seeding; a protocol
freeze (B5) and a later materials seal; baseline guides carry the raised-case recipe.

**What was and was not done for this draft.**

- Read: the oversight report, `usecases/agent-policy` (plan, key, harness), `usecases/safety-framework`,
  `docs/spec/norm-defaults.md`, `lean/NORMS.md`, `lean/NORMDEFAULTS.md`, the Lean sources named in section 13,
  `docs/LEAN-FIRST-PLAN.md` (branch `design/lean-first`), the english-lean S3 plan, `experiments/T1c`, `ve_experiments`.
- **No model was called, no network request was made, and no Lean was built.** The planner session could not run
  `lake build`, `curl` or `python3`. Three consequences, each repeated where it matters:
  1. Licences in section 2 are the ones the oversight report recorded on 2026-10-05; batch B0 checks them again.
  2. The Lean statements of section 13 and the appendix were written against the sources but **not elaborated**.
     Batch A1 starts by elaborating the stub. A statement that fails or is false is recorded as a finding, as
     `lean/NORMDEFAULTS.md` does, never silently weakened.
  3. The power figures of section 7 are hand-computed approximations. Batch B4 recomputes them by simulation
     before the freeze. The pass bars do not move.

## 0. Summary

- **Question.** A written policy for an AI agent can be silent on a case it raises, contradict itself, or contain
  a rule that never takes effect. Do frontier models find such defects by reading? Does adding VE find more? Does
  VE find more than Z3 or Datalog encodings written by the same model?
- **Materials.** Ten real policies (two τ-bench domains, six MANTRA manuals, the Claude Code permission page, the
  Codex sandbox and approval text), 1 to 17 thousand words. τ² airline is the development policy and is not scored.
- **Items.** 200: 150 with one seeded defect and 50 clean. Seeds are written by models that are not arm models,
  checked by two validators, and the answer key is sealed before any arm runs.
- **Arms.** A frontier model alone; the same model with VE; the same model writing Z3; the same model writing
  Datalog. Equal rounds, equal token and compute caps.
- **Metric.** Share of seeded defects found, at an equal rate of false reports. Every report in every arm must
  carry a concrete situation, and every report is checked by two blind judges against the policy text. A seeded
  defect counts as found only if the judges confirm the report and its situation.
- **Bars fixed here.** The VE claim on gaps passes only if the model alone is under 90%, VE adds at least 15
  points over the model alone, and VE beats both Z3 and Datalog by at least 15 points. It is **falsified** if a
  model alone reaches 90%, or if Z3 or Datalog comes within 5 points of VE on gaps. It is **void** if VE can
  formalise less than 60% of the rule paragraphs, or if fewer than 8 policies carry at least 3 gap items.
- **Build.** Four Lean-first batches give Lean the audit questions that live in a Python harness today (which two
  rules clash, which rule never decides, which condition can never hold, which raised case is left open). Six
  harness batches build materials, runners and the scorer. The measured run waits for Lean-owned admission of
  the English the VE arm uses. Then a gate run, the scored run, blind adjudication and the report. No GPU.

## 1. Claims and hypotheses

Prior results that shape the claims (all from the oversight report, section 0):

- A formal checker beating a bare agent on policy compliance is already shown by others. It is not claimed here.
- A frontier model as verifier is at ceiling on τ² airline refusal tasks (24 of 24). Short policies may be at
  ceiling for defect finding too. That is falsifier F1.
- VE's own evidence so far is small: 4 of 4 seeded defects on one authored policy of 26 rules.

**Definitions used in every hypothesis.** "Recall" is the share of seeded items on which the arm reports the
seeded defect (section 6.2). "At the matched level" means at the confidence cut-off where the arm makes at most
0.20 false reports per item (section 6.3). "Points" are percentage points. The model in the comparison is the
same in every arm of that comparison.

| # | Hypothesis | Kind |
|---|---|---|
| H1 | Headroom: each model alone has recall below 90% on the 120 policy-defect items and on the 60 gap items | primary |
| H2 | On gap items, model with VE exceeds the model alone by at least 15 points | primary |
| H3 | On gap items, model with VE exceeds model with Z3 and model with Datalog by at least 15 points each | primary; the VE-specific claim |
| H4 | On conflict items the four arms are within 10 points of each other | parity prediction; no VE claim |
| H5 | On loophole items (rules that never take effect), model with VE exceeds the model alone by at least 15 points | secondary (30 items) |
| H6 | On clean items, model with VE is not worse than the model alone by more than 10 points in the share with no false report | secondary |
| H7 | Reports that carry a VE-checked situation are judged "not a real defect" less often than the model-alone reports, and the two judges agree on them more often | secondary |
| H8 | Translation track: a reader finds a seeded mistranslation more often in VE English than in SMT-LIB or Datalog | secondary; powered for large effects only |

**Predictions (not results).** The oversight report expects the model alone at 50 to 75% on gaps and on rules
that never take effect in policies over five thousand words, VE at 90% or more where the policy is expressible,
and parity on direct conflicts. No number in this paragraph has been measured.

**What is not claimed, whatever the outcome.** Nothing about agent behaviour, runtime guards or training. Nothing
about human readers (the reader in H8 is a model). Nothing about policies outside the ten. Nothing about defects
other than the seeded families.

## 2. Policies and licences

| # | Policy | Source | Size | Licence as recorded | Role |
|---|---|---|---|---|---|
| D | τ² airline | `sierra-research/tau2-bench` | 1,313 words (report, verified) | MIT (report, GitHub API) | **development only**, never scored |
| 1 | τ² retail | same repository | B0 measures | MIT | scored |
| 2 | τ² telecom | same repository | B0 measures | MIT | scored |
| 3 to 8 | MANTRA manuals 1 to 6 | arXiv 2605.06334 and its data release | 1,158 to 16,644 words, 13 to 148 tools (report, verified from the paper) | CC BY 4.0 (stated in the paper; the data release's own licence file is **not yet checked**) | scored |
| 9 | Claude Code permissions page | `https://code.claude.com/docs/en/permissions` (pinned by hash in `usecases/agent-policy/sources.md`) | B0 measures | **no open licence found; treated as all rights reserved** | scored, by reference (below) |
| 10 | Codex sandbox and approvals text | `openai/codex`, `docs/` at a pinned commit that still holds the full text | B0 measures | repository licence **not checked in this session** (believed Apache-2.0) | scored |
| R | τ³ banking | τ-bench repository | B0 measures | MIT if in the same repository; **not checked** | reserve |

Rules:

1. **Why airline is not scored.** Datalog and SMT encodings of it are published (PCAS, the solver-aided paper),
   and a frontier verifier is at ceiling on it. Scoring it would leak in favour of the Z3 and Datalog arms and
   would test nothing.
2. **B0 checks every licence again** from the licence file at the pinned commit or release, records the file's
   SHA-256, and stops if a licence differs from this table. A policy whose licence does not allow modified copies
   is used **by reference**: its text and every variant made from it stay in an untracked local store, and the
   repository holds only hashes, paragraph numbers and scores. This is how row 9 is handled, as
   `usecases/safety-framework` handled a PDF without a licence.
3. **Attribution.** Committed variants of MIT, Apache-2.0 and CC BY texts carry the source, the licence and a
   statement that the text was changed (CC BY 4.0 requires it).
4. **Replacement.** The reserve replaces a scored policy only for a licence failure or if the source cannot be
   pinned. Low VE coverage is **not** a reason to replace a policy; that would select in VE's favour.
5. **Base text.** Each policy is turned once into its base text: plain text, split into numbered paragraphs by a
   deterministic splitter, with proper names (company, product, plan and tool names) replaced through a fixed
   one-to-one table. Numbers and conditions are not changed. All variants derive from the base text. The table
   lowers the value of a memorised original or a published encoding; it does not remove it (section 10).

## 3. Defect taxonomy

One seeded defect per item. Four classes; the first three are defects of the policy text, the fourth is a defect
of a formal rendering of it.

| Class | Family | What the seeder does to the text | What makes it a defect | Items |
|---|---|---|---|---|
| G gaps | G1 unstated complement | removes or narrows the sentence that covers the other side of a condition the text itself draws (keeps "a confirmed transfer may be made", removes what holds for an unconfirmed one) | a case the text raises gets no answer from any paragraph, the general clauses included | 30 |
| G gaps | G2 unanswered exception | leaves a prohibition with its "unless" and removes the sentence that says what holds when the exception applies | the same, in the exception case | 30 |
| C conflicts | C1 direct conflict | adds or changes a sentence so that two paragraphs give opposite answers for one case | both answers follow from the text | 15 |
| C conflicts | C2 missing precedence | removes the words that made one of two overlapping rules win ("except", "unless", "takes priority") | both answers follow from the text | 15 |
| L loopholes | L1 swallowed prohibition | widens an exception or a permission so that it covers every case of a prohibition | the prohibition can never decide; what it forbade is now allowed throughout | 10 |
| L loopholes | L2 unreachable permission | narrows a permission, or widens a prohibition, so that the permission is always overridden | the text grants something that can never be granted | 10 |
| L loopholes | L3 dead condition | changes a condition, or a stated fact, so that the condition can never hold | the rule can never apply | 10 |
| T unfaithful translation | T1 dropped exception, T2 reversed or implied negation, T3 omitted clause, T4 widened condition | changes a correct formal rendering of a section, the same change in VE, SMT-LIB and Datalog | the rendering gives a different answer from the source in a stated situation | 30 |

Totals: 120 policy-defect items (G 60, C 30, L 30) and 30 translation items. Each of the ten policies carries
12 policy-defect items (3 G1, 3 G2, 3 C, 1 each of L1, L2, L3) and 3 translation items. The C split alternates
2 and 1 by policy number, and T1 to T4 rotate, so that C1 and C2 have 15 each and the T families 7 or 8 each.

The report's five families map onto this table as follows: "missing precedence" is C2, "unstated complement"
is G1, "unreachable permission" is L2, "direct conflict" is C1, "dead guard" is L3. G2, L1 and the T families
are added here: G2 is defect D2 of `usecases/agent-policy` in English form, and L1 is the mirror image of its
defect D4 (there a permission never decides; here a prohibition never does).

**Why T is separate.** T1 to T4 are the failures the solver-aided paper names for LLM translation ("implicit
negation", "omitted clauses"). They are seeded into a rendering, not into the policy, so they are scored in
their own track (section 5.3).

## 4. Seeding protocol and the sealed key

### 4.1 Who seeds

- **Seeders:** Claude Fable 5.1 for the odd-numbered policies and GPT-6 Astra for the even-numbered ones. Neither
  is an arm model for the items it seeds (section 5.1).
- **Validators:** each item is checked by the other seeder model and by Claude Sonnet 5.5, in fresh contexts.
- Astra's steps run inside the Codex plan allowance. They are never handed to GPT-6 Sol, because Sol is an arm
  model. If Astra has no capacity the step waits.

### 4.2 Steps (all before any arm call on scored items)

1. **Site survey.** For each base text the seeder lists, per family, the paragraphs where a seed is possible.
   A policy with a stated general default ("refuse whatever this policy does not allow") has no G site unless a
   case escapes that default; the survey says so.
2. **Allocation.** Targets are those of section 3. A shortfall in one policy moves to the next policy number that
   has a spare site of the same family, then of the same class. The allocation is recorded before step 3.
3. **Variants.** Every policy-track variant carries exactly three edits: one structural edit and two
   paraphrases. In a seeded variant the structural edit is the seed. In a clean variant it is harmless (an
   expository sentence removed, two paragraphs reordered). So neither the number nor the kind of edits reveals
   the label. 50% more variants than needed are produced as a reserve.
4. **Key entry, written by the seeder with the variant:** the family; up to three anchor paragraph numbers in the
   variant; the question the defect concerns; a concrete witness situation in plain English; for G "no paragraph
   answers", for C the two paragraphs and their answers, for L the rule that never takes effect and what always
   wins or what can never hold.
5. **Validation, without VE, Z3 or Datalog.** Both validators must confirm, from the base text and the variant:
   (a) the situation is possible under the text's own facts; (b) the variant has the stated defect in it;
   (c) the base text does not; (d) the two paraphrases preserve meaning; (e) the edit reads as a plausible
   drafting slip. For clean variants: (d), and that the structural edit changes no answer. A variant that either
   validator rejects is discarded and replaced from the reserve in the recorded order.
6. **Sealing.** The key file is written outside every worktree. The protocol freeze (batch B5) comes before
   seeding, so it cannot hold the key. After seeding, a **materials seal** records the SHA-256 of the key, the
   variants, the allocation and the base texts in a second manifest. That manifest is timestamped before any
   scored arm call. Only the frozen scorer reads the key: once in gate mode (section 9, step 3) and once after
   adjudication (step 6), each time after the outputs of the arms it scores are hashed. The key is committed
   after the last arm output is hashed.
7. **Cluster check.** After validation and before the materials seal, count the policies that hold at least 3
   gap items. The gap tests of section 7 run over those policies only. If fewer than 8 policies qualify, the gap
   claim is void (V2, section 8). This is declared in R1 before any arm call.

**Why validation uses no formal tool.** A key checked by VE would favour the VE arm; one checked by Z3 would
favour the Z3 arm. The cost is stated in section 14: the key holds defects a model can confirm when told where
to look.

### 4.3 Clean items and natural defects

A clean variant has no seeded defect. It still has whatever defects the original policy has. Those are handled
by adjudication (section 6.4): a report of a real natural defect is not a false report.

**Natural defects, reported separately.** VE's findings on the ten base texts (from the gate translations,
section 9) are listed with their situations. Each counts only if two blind judges confirm it against the
original text. This list is a deliverable, not a score.

## 5. Arms

### 5.1 Models

| Role | Model | Notes |
|---|---|---|
| Arm model M1 | Claude Opus 5.5 (`claude-opus-5-5`) | all four arms on all 160 policy-track items |
| Arm model M2 | GPT-6 Sol | model alone on all 160; the three formal arms on policies 1 to 5 (80 items) in tier A |
| Strongest-model check | Claude Fable 5.1 on the Astra-seeded policies; GPT-6 Astra on the Fable-seeded ones | model alone only, 80 items each; never on a model's own seeds |
| Seeders, validators, judges | Fable 5.1, GPT-6 Astra, Sonnet 5.5 | section 4.1, section 6.4 |
| Reader proxy (track T) | Claude Sonnet 5.5 (`claude-sonnet-5-5`) | the project's stand-in for a human reader; results labelled "proxy" |

All calls go through `ve_experiments/llm.py` with its isolation flags: no tools, no files, no memory, an empty
working directory, one conversation per item and arm. Served model ids and CLI versions are pinned at the
freeze. A served-model change stops the run.

### 5.2 Policy track: four arms on the same items

Every arm sees only the variant, as numbered paragraphs. No arm sees the base text, the original or another
variant.

| Arm | What the model does | Tool rounds |
|---|---|---|
| **J** model alone | reads the variant and writes its reports | none |
| **J+VE** | writes the policy as a VE document; the VE reader answers in English (accepted, or what to rephrase); VE's findings come back as English sentences with situations; the model writes its reports | up to 2 repair rounds, then 1 findings round |
| **J+Z3** | writes an SMT-LIB encoding and its own defect queries; Z3's output comes back (results, models, errors); the model writes its reports | the same |
| **J+DL** | the same with Datalog (Soufflé) | the same |

Equal treatment of the three formal arms:

- **Guides.** Each formal arm gets a writing guide of at most 5,000 tokens. Each guide names the three defect
  classes and says how to ask for each in that formalism. The Z3 and Datalog guides say outright that
  "permitted" and "forbidden" should be separate relations and that a case where neither holds is a gap. They
  also carry the same per-rule raised-case recipe that VE applies: for each rule, the cases its condition names
  when one of its parts is reversed, and each of its "unless" cases, then the question whether anything in the
  text answers there. The baselines are therefore told VE's main idea and VE's recipe, so H3 does not test a
  withheld recipe. The two baseline guides are drafted by a builder model and reviewed by both plan reviewers
  with one instruction: make this arm as strong as you can.
- **Caps.** The same number of rounds, the same input and output token caps per item, the same tool budget
  (20 minutes of wall time on 4 cores per item for VE's findings, for Z3 and for Soufflé). A tool that runs out
  returns "unknown", which is never a finding.
- **Development.** Guides, prompts and the harness are tuned on τ² airline and on an English paraphrase of
  `usecases/agent-policy` only, then frozen. Builders never see a scored variant.

Arm J gets one call at the highest effort with an output cap equal to the formal arms' total output cap.

**Sub-arms computed from the same outputs, with no extra call:**

- *VE-checked only*: the J+VE reports that cite a VE finding (below).
- *Solver-backed only*: the J+Z3 and J+DL reports that cite a query whose recorded output supports them.
- *Union of J and VE-checked*: descriptive.

**What VE returns to the model in J+VE** (all Lean-decided, shown in English, section 13):

| Finding | Evidence | Shown as |
|---|---|---|
| two rules clash | a checked situation, and the rules that decide in it | "Paragraphs 3 and 14 give opposite answers when …" plus the facts of the situation |
| something required is not permitted | a checked situation, the rules or defaults that make the obligation hold, and those that make the permission fail | "Paragraph 7 requires … when …, and paragraph 11 does not permit it there" plus the facts |
| a raised case is left open | a checked situation at a case the rules themselves name, where two admissible completions of the text give opposite answers | "The text does not say whether … when …" plus the facts |
| a rule never decides | a checked proof, a checked situation that meets the stated facts, and one checked situation where its condition holds and another rule decides | "Paragraph 12 never decides any case. Here its condition holds and paragraph 24 decides." |
| a condition can never hold | a checked proof, and a checked situation that meets the stated facts | "The condition of paragraph 9 can never hold, given paragraphs 2 and 5." |
| no conflict anywhere, or no gap for a question | a checked proof, and a checked situation that meets the stated facts | stated as such |
| the stated facts cannot all hold | a checked proof | "The facts stated in paragraphs 2 and 5 cannot all hold." |
| unknown | the budget that ran out, or no checked situation that meets the stated facts | "not decided within the budget" |

A case where a stated default answers ("by default, refuse"), or where an obligation settles the permission
that goes with it, is not left open. Such a case is shown as "the text's default answers here", for display
only; it is never a finding.

A universal verdict (never decides, can never hold, no conflict, no gap) is true of any set of stated facts
that cannot all hold. So each such verdict is given only with a checked situation that meets the background,
the completion premises and the stated facts. Without one the answer is "unknown", unless a checked proof
shows that the stated facts cannot all hold, which is then the finding.

A rule carries the paragraph numbers it translates, in a side file the model writes with the document. The
mapping from a finding to paragraphs is a lookup. A wrong mapping is the arm's error.

**Unaccepted units.** After the two repair rounds, Lean checks the accepted units only. The rule paragraphs
that no accepted unit translates are listed beside the findings, both in what the model sees and in the record.

**Ambiguous source sentences.** The translator writes the reading it judges most likely and marks the unit as
narrowed, with the other reading in a note. A finding that depends on a narrowed unit is shown as
"depends on a reading". (Keeping both readings inside one checked document needs the readings and
norm-defaults composition, which is not on `main`; section 12.)

**Completions.** The guide repeats `docs/spec/norm-defaults.md` section 5: the translator states "by default …"
only where a paragraph says so and cites it; otherwise the completion is "the text does not say".

### 5.3 Translation track

- **Items.** Four sections per policy (three seeded, one clean), each at most 600 words. For each section a
  builder writes a reference rendering in VE, in SMT-LIB and in Datalog. The three must agree with each other on
  at least 20 generated situations before any seed (VE's answers from Lean, Z3's and Soufflé's from their
  tools). The seeder then makes the same change of meaning in all three. The three changed renderings must agree
  with each other on the same situations and differ from the references in at least one, which is recorded.
- **Arms.** A reader gets the source section and one rendering, and says "faithful" or reports where they
  differ, with a situation. Renderings: VE English exactly as a reader sees it (rules and legend sentences, no
  JSON, no symbols); SMT-LIB; Datalog. Readers: Sonnet 5.5 (proxy for a human reader), Opus 5.5, GPT-6 Sol.
  Each reader sees each section in all three renderings, in separate conversations, in rotated order.
- **Reader prompt.** The source section, the rendering and the task, nothing else: no writing guide and no
  worked example, so the reading stays zero-training. The prompt is frozen in B5.
- **Score.** As section 6, with "the rendering differs from the source here" as the only class.

## 6. Outputs, matching and metrics

### 6.1 Output of every arm

At most 8 reports per item, or none. Each report has: the class (gap, conflict, loophole); one to three paragraph
numbers; the question concerned; a concrete situation as plain English facts; what the text says there (nothing;
two opposite answers and from which paragraphs; which rule never takes effect and why); a confidence between 0
and 1; and for formal arms the id of the tool result it rests on, if any. A reply that cannot be parsed is kept
and scored as no report.

### 6.2 Matching a report to the key (semantic)

A seeded item is **found at cut-off t** if some report with confidence at least t has the key's class, names at
least one anchor paragraph, is judged real by both judges (6.4), and both judges agree that its situation is the
key's kind of situation. The class-and-anchor test alone is **candidate retrieval**: it selects the reports the
judges compare with the key. Reported beside the primary figure: *mechanical* recall (class and anchor only) and
*lenient* recall (anchor paragraph only, class ignored).

**Paragraph-spray control.** A scripted arm (B4) that gives 8 reports per item, each with a random class and
three random paragraphs and no situation, is scored mechanically on the sealed key. Its recall is reported as the
chance level of mechanical matching.

### 6.3 False reports and the matched level

- **Every report**, matched or not, goes to adjudication (6.4) and is **real**, **not real** or
  **unresolved**. "Not real" and "unresolved" count as false in the primary analysis. A report that matches the
  key mechanically but is not judged real is a false report, never a hit. A sensitivity analysis drops
  "unresolved". The cut-offs and H7 are computed over all reports.
- For an arm and a cut-off t, the false-report rate is the number of false reports with confidence at least t,
  divided by the number of items the arm ran, seeded and clean together (160 for a full arm).
- **Matched level:** for each arm, the lowest cut-off whose false-report rate is at most **0.20 per item**. The
  cut-off is chosen on the scored data, for every arm in the same way. This favours no arm; it is optimistic for
  all of them in the same degree.
- Reported beside it: recall at 0.05, 0.10 and 0.50 false reports per item, and with no cut-off.

### 6.4 Adjudication: the situation makes each report checkable

- Reports are rewritten into one neutral template (class, paragraphs, question, situation, claim). Arm, model,
  tool ids and confidence are removed. Identical reports on the same variant are judged once.
- **One judge call per variant and judge.** Two judges, Fable 5.1 and GPT-6 Astra, each in a fresh context, get
  the variant and every distinct report of every arm on it, in shuffled order. For each report they answer three
  narrow questions: Is the situation possible under the text? Which paragraphs apply in it? Does the claim
  follow? They answer against the whole variant, defaults and paragraphs outside the report's anchors included.
  A report with no usable situation is "not real". A gap that exists only because a formal translation left a
  paragraph out is "not real".
- After the three answers for every report are recorded, a second turn of the same conversation shows the key
  entry and asks, for each report that matches it mechanically, whether the report's situation is the key's
  kind of situation (6.2). This turn runs at step 6 of section 9, after the scorer opens the key.
- Agreement of the two gives the label. Disagreement is "unresolved". Cohen's kappa is reported per arm.
- A judge may meet reports from an arm of its own model. The template hides that; section 14 lists what remains.

### 6.5 Metrics

| Metric | Definition |
|---|---|
| **Primary:** recall at the matched level | per arm and model, semantic matching (6.2), on G (60; the gap tests use the qualifying policies of 4.2 step 7), C (30), L (30) and all 120 |
| Mechanical and lenient recall | the same, with candidate retrieval only (6.2); the paragraph-spray chance level beside them |
| Seeded case in VE's findings | descriptive, uncapped: share of seeded gap items whose seeded case is in VE's full finding list for the item, before the 8-report cap |
| Clean accuracy | share of the 40 clean items with no false report at the matched level |
| Certified clean (VE only) | share of clean items for which VE returns "no conflict" and "no gap" proofs for every question; expected to be small on real policies, reported as found |
| False share of checked reports | among VE-checked (and solver-backed) reports that do not match the key, the share judged not real: the size of the translation-error problem |
| Judge agreement | kappa per arm; first-pass agreement on checked against unchecked reports |
| Coverage | share of rule paragraphs with at least one formal VE unit, CHECKED or OPEN, and with at least one CHECKED unit (section 9, step 2); the same count for Z3 and Datalog, from the paragraph side files |
| Recall by subset | J+VE and J recall on gaps in the CHECKED-anchor subset (section 9, step 2) and, descriptively, in the CHECKED-or-OPEN subset |
| Unknown rate | share of tool questions that ended "unknown", per formal arm |
| Cost | input and output tokens, tool CPU seconds, rounds used, per arm and item |
| Translation track | recall and clean accuracy per rendering and reader |

## 7. Analysis, sample size and power

- **Unit and clusters.** The unit is the item. Items of one policy share a base text, so the ten policies are
  the clusters.
- **Registered test.** For a contrast between two arms on a class, compute the recall difference inside each
  policy, then the exact sign-flip test on the mean of the differences (2^k assignments for k policies,
  two-sided). Holm's correction covers the three primary contrasts of M1 on gaps: J+VE against J, against J+Z3,
  against J+DL.
- **Policies in the gap tests.** Only the policies with at least 3 gap items (section 4.2, step 7). The
  smallest two-sided p of the sign-flip test is 2 / 2^k: 0.008 for 8 policies, but 0.031 for 6, which is above
  Holm's strictest level of 0.0167. Hence fewer than 8 qualifying policies make the gap claim void (V2).
- **Intervals.** A 95% interval for each difference from a bootstrap over policies (10,000 resamples), and a
  Wilson interval for each single recall. Ten clusters make the bootstrap interval too narrow; it is descriptive.
- **Failures.** A failed call or an unparseable reply stays in the data as "no report". The failure rate is
  shown beside every metric. No retries beyond transport errors, no replacement samples, no stopping on results.
- **M2** is a replication on five policies: the same tables, no bar of its own except "same sign" in section 8.

**Why 150 and 50, and why 60 gaps.** The VE-specific prediction concerns gaps, so gaps get the most items. The
figures below are planning values, computed by hand with a normal approximation for ten policies; batch B4
replaces them with a simulation under the same assumptions, including fewer qualifying policies.

| Quantity | Value |
|---|---|
| Wilson 95% interval for 54 of 60 (90%) | 80% to 95% |
| Wilson 95% interval for 108 of 120 (90%) | 83% to 94% |
| Wilson 95% interval for 36 of 60 (60%) | 47% to 71% |
| Per-item paired test on 60 gaps, 60% against 90% (few items found by J only) | power about 0.99 |
| The same, 75% against 90% | about 0.77 |
| The same, 80% against 90% | about 0.55 |
| Registered policy-level test, 60% against 90%, policies differing by 15 points (SD) in the effect | about 0.9; about 0.8 at Holm's strictest step |
| The same, 75% against 90% | about 0.45; about 0.2 at Holm's strictest step |

Reading: the design can confirm the predicted effect of about 30 points. It cannot reliably confirm an effect
of 15 points, and it cannot resolve differences under 10 points. That is why an outcome between the pass bar and
the falsifier is called inconclusive and not a pass. With 30 items each, C, L and T are powered for effects of
30 points or more only.

## 8. Pass and fail bars, fixed in advance

All bars use M1 at the matched level with the primary matching, unless stated.

| # | Outcome | Condition |
|---|---|---|
| F1 | **Falsified: no headroom** | any model-alone arm (M1, M2, or a strongest-model check on its half) reaches 90% recall on the policy-defect items it ran, or on its gap items. The scope that reached 90% gets no VE claim |
| F2 | **Falsified: not VE-specific** | on gaps, J+Z3 or J+DL is within 5 points of J+VE, or above it |
| F3 | **Falsified: VE does not help** | on gaps, J+VE is not above J (difference zero or negative) |
| V1 | **Void** | VE formalises less than 60% of the rule paragraphs of the ten base texts, pooled (section 9, step 2). The run stops after the gate and reports the coverage |
| V2 | **Void: too few clusters** | fewer than 8 policies hold at least 3 gap items after validation (section 4.2, step 7). Declared in R1 before any arm call; the gap claim is not tested |
| P1 | Pass, headroom | F1 does not hold |
| P2 | Pass, VE over the model alone | on gaps, J+VE minus J is at least 15 points and the registered test gives p below 0.05 after Holm |
| P3 | Pass, VE-specific | on gaps, J+VE minus J+Z3 and J+VE minus J+DL are each at least 15 points, each with p below 0.05 after Holm |
| P4 | Pass, absolute | J+VE recall on gaps is at least 80% on all gap items, and at least 90% on the gap items in the CHECKED-anchor subset (section 9, step 2) |
| P5 | Replication | every M2 difference that P2 and P3 use has the same sign |

All recall figures in this table use the semantic matching of 6.2.

**Verdict rule.** "VE finds gaps that the alternatives miss" is claimed only if P1 to P5 all hold. If F1, F2,
F3, V1 or V2 holds, the report's first sentence says so. Anything else is **inconclusive**, and is reported with
that word.

Secondary bars, reported and never used to rescue a primary failure:

- Conflicts (H4): parity is expected. If J+VE is 10 points or more below J, that is reported as a VE weakness.
- Loopholes (H5): supported at 15 points or more with p below 0.05; contradicted if J+VE is not above J.
- Clean items (H6): contradicted if J+VE is more than 10 points below J in clean accuracy.
- Checkability (H7): contradicted if more than half of the VE-checked reports that miss the key are judged not
  real. In that case translation errors dominate and the checked situation did not help in practice.
- Translation track (H8): supported if the proxy reader's recall on VE English exceeds both other renderings by
  20 points or more; contradicted if it is 10 points or more below either.

### Plan v2 fields (the headings `ve_experiments/runner.py` requires)

#### Primary contrast

Recall (semantic matching, 6.2) on the gap items of the qualifying policies (section 4.2, step 7) at 0.20 false
reports per item: J+VE minus J, J+VE minus J+Z3, J+VE minus J+DL, for Opus 5.5.

#### Refutation condition

F1, F2 or F3 above.

#### Honest-acceptance constraint

Clean accuracy of J+VE not more than 10 points below J (H6); the false-report rate is equal by construction at
the matched level.

#### Smallest useful effect

15 points of recall on gaps.

#### Capability gate

The gates of section 9: Lean-owned admission of the English the VE arm uses (else no measured run), at least 8
qualifying policies (else void), coverage at least 60% (else void), and the model alone below 90% (else
falsified, and the formal arms are not run).

#### Sample size

200 items in 10 policies: 120 policy-defect items (60 G, 30 C, 30 L), 40 clean policy items, 30 translation
items, 10 clean translation items. The gap tests use the policies with at least 3 gap items. Reasoning in
section 7.

## 9. Gates and order of the run

0. **Checks before the freeze.**
   - *Ownership (gate O).* Lean admits the English subset the VE arm actually uses and decides what it means,
     through english-lean E2/E3 or an equivalent scoped delivery, and Lean checks the findings. Executable guards
     (section 13) show that no scored finding and no admission can reach a legacy Python semantic path. Without
     gate O there is no measured run: development and a VE arm on the Python reader may run only as a pilot
     labelled as such, and the pilot is not the measured VE arm.
   - *Readability.* The A4 situations render with no symbol, bracket or variable letter; the reader prompts of
     5.3 hold source, rendering and task only.
   - *Coverage procedure.* Step 2 below runs end to end on the development policy.
1. **Protocol freeze** (batch B5): prompts, guides, harness, scorer, tool versions, the Lean service and
   reader, this file. Then seeding, validation, the cluster check and the materials seal (section 4). No prompt
   or harness change after the first seed is written; a change after that point is a dated amendment and a
   rerun of everything it touches.
2. **Coverage gate.** M1 translates each of the ten base texts into VE (ten translations).
   - Two annotators (the seeders) mark each base paragraph as rule, definition or other; on disagreement it
     counts as a rule.
   - **Coverage** is the share of rule paragraphs that at least one formal VE unit translates (status CHECKED,
     or OPEN because of an open term). CHECKED alone is reported beside it.
   - Pooled coverage below 60%: outcome V1, stop.
   - A seeded item is **in the CHECKED-anchor subset** if every one of its anchor paragraphs corresponds to a
     base paragraph that at least one CHECKED unit translates (OPEN units do not count). The subset is fixed
     before any arm runs, so P4's second part does not depend on arm outcomes. Recall on the
     CHECKED-or-OPEN subset is reported beside it, descriptively.
   - **CHECKED establishes neither a complete translation nor a faithful one.** A CHECKED unit is accepted and
     checked; it may still leave out a condition, or say something the source does not. The subset is therefore
     not called expressible. Every report is still adjudicated against the whole variant (6.4), so an
     incomplete translation earns no credit by itself.
3. **Headroom gate.** Run every model-alone arm on all its items; hash the outputs. The scorer then runs in
   **gate mode**, which this step authorises: it reads the key once, for the model-alone arms only, and prints
   per arm only recall with no cut-off on all items and on gaps (mechanical matching, since adjudication has
   not run). If every figure is below 90%, continue. Otherwise adjudicate those arms' reports and compute recall
   at the matched level; if F1 holds, stop and report.
4. **Formal arms**, tier A or B (section 11), items in a fixed random order, arms interleaved.
5. **Translation track.**
6. **Adjudication**, then the scorer opens the key and writes the tables.
7. **Report**, with every deviation listed.

## 10. Leakage controls

| Risk | Control |
|---|---|
| An arm model knows the original policy and spots the change | proper names replaced (section 2, rule 5); three edits in every variant, seeded or clean (4.2); a recitation probe before the run: each arm model is asked to continue each original from a 200-word prefix, and the overlap is reported per policy |
| Published encodings help the Z3 and Datalog arms | τ² airline is not scored. MANTRA is published with SMT validation; if its encodings are public, that helps the Z3 arm, which is against VE's claim and is accepted. B0 records what is public |
| A model audits its own seeds | no arm model seeds. The strongest-model checks run only on the other seeder's policies |
| The key leaks into prompts or code | the key lives outside every worktree; arms have no tools or files; builders work on development policies only; protocol freeze before seeding, materials seal before any scored arm call; the scorer opens the key only in gate mode and after adjudication, each time after output hashes are written |
| Tuning on scored outcomes | cut-off rule, matching rule, tiers and bars are fixed here; the gates print only what section 9 allows |
| The key favours a formalism | validation uses no formal tool (4.2) |
| Judges recognise an arm | neutral template; arm and model removed (6.4) |
| Items leak between arms or conversations | one conversation per item and arm; no memory; the item id is never in a prompt (`ve_experiments` rule) |
| The orchestrator steers on partial results | the orchestrator may read only the gate lines until step 6 |

## 11. Cost and model budget (Claude and Codex)

All figures are **estimates**, for a mean base text of 5,000 words (about 6,700 tokens), which B0 measures.
Batch B2 measures real tokens per item and arm on the development policy, and the tier is then chosen by the
rule below, before any scored call. Calls run on the Claude and Codex subscriptions; no paid API is planned.

| Part | Calls | Input tokens | Output tokens |
|---|---|---|---|
| Model alone: Opus and Sol on 160 items, Fable and Astra on 80 each | 480 | 4.1 M | 4.8 M |
| Formal arms, M1: 160 items × 3 formalisms, about 51 k in and 33 k out per item and arm | 480 item-arms | 24.5 M | 15.8 M |
| Formal arms, M2, tier A: 80 items × 3 | 240 item-arms | 12.2 M | 7.9 M |
| Coverage gate: 10 base translations | 10 | 0.5 M | 0.3 M |
| Seeding and validation, with the 50% reserve | about 800 | 7 M | 0.8 M |
| Adjudication: one call per variant and judge, each holding every distinct report of every arm on it (up to about 70, thousands in all) | 160 × 2 = 320 | about 6 M | about 2 M |
| Translation track: references, seeds, 360 readings | about 600 | 2.5 M | 2 M |
| Development on airline and agent-policy | — | 3 M | 1.5 M |
| **Total, tier A** | | **about 60 M** | **about 36 M** |

Split: Claude (Opus, Fable, Sonnet) about 38 M in and 22 M out; Codex (Sol, Astra) about 22 M in and 13 M out.
Half of the adjudication falls on Astra, beside half of the seeding, the validation and a strongest-model check.
For scale, T1c used about 45 M input tokens on a subscription, with little output. How these token counts map
onto the weekly allowances is not known; B2's development runs measure it as a share of each pool.

**Ceilings.** Claude 45 M in and 25 M out; Codex 28 M in and 15 M out. The run stops before a call that would
pass a ceiling, and reports what is missing.

**Tier rule** (applied once, from B2's measurements):

- **Tier A** if the measured cost per item and arm, times the planned counts, plus the measured adjudication
  cost per variant times 160, fits the ceilings, and Astra's share (seeding, validation, judging, its
  strongest-model check) fits Astra's plan allowance over the run's weeks.
- **Tier B** otherwise: M2 runs the model-alone arm on all items and the three formal arms only on the gap and
  clean items of policies 1 to 5 (50 items). M1 is unchanged. The same two conditions apply.
- If tier B does not fit either, nothing scored is run and this file is amended.

**Standing limits.** No Claude account above 90% of a five-hour or weekly pool (`usage-guard.sh`,
`usage-watch.sh`); accounts chosen by `pick-claude-account.sh`; the run takes at most 25 points of any account's
weekly allowance in one week, so it spreads over at least two weeks beside the build work. Codex: Sol on the plan
allowance, then on credits inside the weekly pace of about 4,800; Astra only inside the plan allowance; no
credits are bought.

**Compute.** CPU only, on the 32-core VM. Tool budget 20 minutes × 4 cores per item and formal arm: at most
640 core-hours for M1's 480 item-arms (20 hours of the whole VM) and 320 more for M2 in tier A. In practice far
less is expected if agent-policy's cost (115 s for 26 rules on 6 workers) is a guide; B2 measures it. No GPU.

## 12. What VE needs: now, built by this plan, and next month

| Need | State on `main` at `95a97a07` | In this plan |
|---|---|---|
| Rules with exceptions and "unless", permissions, prohibitions, obligations (`norms@0`) | present; Lean decides conflicts (`lean/NORMS.md`) | used as is |
| "The text does not say" as a third answer (`norm-defaults@0`) | present; Lean replays "no gap" proofs and reachable-gap situations (`normDefaults_wire_gaps_sound`, `normDefaults_wire_reached_sound`); Python still decides at runtime until lean-first batch 10b | used through the Lean service only |
| Which two rules clash; which obligation lacks its permission; a rule that never decides; a condition that can never hold | **Python only**, inside `usecases/agent-policy/check.py` (`policy_findings`) and the safety-framework harness; Lean decides that a conflict exists, not which rules or defaults make it | **A1, A2: moved to Lean** |
| A gap at a case the rules themselves raise | not present (gaps are per question, not per rule); `reachedF` counts a case a stated default answers as reached | **A1, A2**: "left open" means two admissible completions differ |
| Checks relative to the document's own stated facts ("no booking is both basic and business") | Lean checks over the base background only; the safety-framework harness added the facts in Python | **A1, A2**: a premise list in every finding |
| The facts of a situation that matter, for display | not present | **A1** (`Formula.why`), **A4** |
| Reading rule blocks in English with one reading | `ve/norm_english.py` decides acceptance (Python). Lean reads formula-level English (S2 merged, S3 and E2 in flight); rule blocks are track E3 | **Lean-owned admission of the English subset the experiment uses**, through E2/E3 or an equivalent scoped delivery: a prerequisite of the measured run (gate O, section 9); see below |
| Stated facts with attribute flags (`data@0`) on the norm-defaults route | **unverified**; the agent-policy case replays in Lean on a flag-free copy | A0 probes it; the writing guide states uniqueness as ordinary sentences if flags are refused |
| Size limits: 256 rules, 64 regulated predicates, 8 "unless" parts per rule, precedence depth 16 | fixed limits | a policy over a limit is split by the translator; findings across the parts are lost and count as misses |

**The reader's owner (DRI ruling, 2026-10-06).** In `ve/norm_english.py` Python decides the consequence, the
conditions, the exceptions, the precedence and the one reading, then builds the document. Lean checking that
document does not check that Python gave the English its right meaning, and an import restriction cannot show
it either. So a Python reader deciding meaning is not acceptable for the measured VE arm. The measured run uses
Lean-owned admission for the English subset it actually uses: E2/E3 if they cover it, else an equivalent scoped
delivery. A0 sizes the minimum Lean reader work for that subset. Full E3 does not block development or batches
A0, B0 and B1; Lean-owned admission of the subset blocks the measured run (gate O). A VE arm on the Python
reader may run only as a pilot, labelled as such, and is not the measured VE arm.

**Not needed, but each would raise coverage (next month or later):**

| Feature | What the translator must do without it |
|---|---|
| Time and events ("within 24 hours of booking", "before", "after") | treat each as a yes-or-no fact that a tool supplies |
| Counting and sums ("at most three gift cards") | the same |
| Integers under a quantifier (`order@0` forbids it) | the same for "an amount over the limit" |
| One sentence for "every prohibition overrides every permission" | list the exceptions rule by rule; an omitted one shows up as a conflict that the source does not have, and counts against the arm |
| Speech acts ("the user has confirmed") | a flag on the action |
| Both readings of an ambiguous sentence in one checked document (readings with norm-defaults) | pick one reading and mark it (5.2) |
| Graded norms ("should") together with norm-defaults in one route | write "should" as a rule and mark the unit |

## 13. Build plan

Throughput rules of `docs/LEAN-FIRST-PLAN.md` section 5 apply to every batch: 2 to 6 hours of build work, a
build checklist, only the affected tests while iterating, the duplicate deleted in the same batch, the
differential fuzzer's baseline not growing. Review rounds come on top. Lean changes also pass `lean/audit.py`,
the frozen-source list, the assurance manifest and `tools/trust_map.py --since` (the batch states its own trust
budget growth).

**Ownership rule for this experiment.** Lean owns every question about what a VE policy means, every finding,
and, for the measured run, the admission of the English the VE arm uses (section 12). Python reads files, calls
models and tools, relays Lean's answers and shows them. Scoring an experiment (matching reports to a key,
statistics) is not VE logic and stays in `ve_experiments`. No Python in this plan builds a VE formula.

**Python semantic paths that remain on `main`**, each with the lean-first batch that moves it:

| Path | Moved by |
|---|---|
| acceptance and meaning of rule-block English, `ve/norm_english.py` | E3, or for this experiment's subset the scoped delivery of gate O |
| the runtime norm-defaults decision | lean-first 10b |
| per-action verdicts in `usecases/agent-policy/check.py` | lean-first 13b |
| the per-tool gap loop in the same file | lean-first 14 |

These stay for their unmigrated callers. The experiment cannot reach them: a lint fixture pins the modules that
`ve_experiments` may import for scored runs, and an executable guard fails a scored run that reaches a legacy
semantic path (gate O). This plan makes no repository-wide deletion claim.

### A0. Probes (2 h, no code kept)

Recorded in the deviations section before A1:

- the stub of the appendix elaborates against the build, or which statement fails and why;
- whether the `norm-defaults` service mode accepts an environment with `data@0` flags;
- the cost of a "never decides" proof on the agent-policy document through the service (the plan's largest
  performance risk: VE's prover alone exhausted its steps there, and the certificate replay has depth limit 125);
- whether E3 for rule blocks has a date, and the minimum Lean reader work that gives Lean-owned admission of the
  English subset this experiment uses (gate O), with its estimate;
- the semantic counterexamples behind fd9 and fd10 run against the current semantics: a case a stated default
  answers is reached but not open, and an obligation can settle a permission where no permission rule decides.

Effort is re-estimated after A0. Elaboration alone does not show that the proofs are feasible or that the
search cost is acceptable.

### A1. Lean: the audit questions and their meaning (4–6 h)

New file `lean/VE/NormDefaults/Findings.lean` (namespace `VE.NormDefaults`), and `Formula.why` beside
`Formula.eval`. Full text in the appendix. Definitions:

| Name | Meaning |
|---|---|
| `baseOf U N φ` | a formula of rule `N` read on the base vocabulary of `fill U`, as `gapF` reads `pos` and `neg` |
| `decidesF U N`, `appliesF U N` | "rule `N` decides here"; "its condition holds and no stated exception does" |
| `clashF U N₁ N₂` | both rules decide here |
| `Allowed U Γ B` | `B` is an admissible filled situation that satisfies the stated facts `Γ` |
| `NeverDecides U Γ N`, `NeverApplies U Γ N` | in no allowed situation, at no typed point |
| `pairSettledF U p`, `unsettledF U p` | "a declared obligation-permission pair forces `p`'s answer here"; "`p` is a gap here and no pair forces it", so two admissible fillings differ |
| `ConflictFreeUnder U Γ`, `GapFreeUnder U Γ r` | the existing conflict notion over allowed situations; no allowed point unsettled on `r` |
| `nearMisses φ`, `raisedCases N`, `raisedGapF U N k` | the cases a rule's own condition names by reversing one part, plus each "unless" case; "that case occurs and is unsettled" |
| `decidersAt U M p vs` | the author rules that decide at a checked point, by evaluation |
| `Formula.why M ρ φ` | a small set of facts (equalities between objects, and ground atoms) that settles the value of `φ` in `M` |

A case reached by a stated default but not unsettled is a display kind, "the default answers here", never a
finding.

Statements to prove (exact text in the appendix):

1. `conflictFreeUnder_nil`: with no stated facts, `ConflictFreeUnder` is `ConflictFreeU`. (Conservative.)
2. `decidesF_iff_selects`: `decidesF` holds on the base restriction exactly when the direct semantics `SelectsD`
   holds, through `subst_sound` and `selects_denote`.
3. `conflict_iff_clash`: a conflict on `r` at a point holds exactly when two author rules of opposite sign on `r`
   both decide there. So every conflict on one predicate has a named pair of rules.
4. `pairConflict_explained`: an obligation-permission conflict (`pairConflict`, the second half of
   `ConflictFree`) at a point has, on the obligation side, a positive author rule that decides there or the
   obligation's default or filling, and on the permission side a negative author rule that decides there or the
   permission's default or filling. With 3, every conflict that `ConflictFree` excludes has a named explanation.
5. `never_decides_sound`, `never_applies_sound`: an accepted certificate over
   `Background_base(E‴) ++ Fill_T ++ Γ` gives `NeverDecides` or `NeverApplies`.
6. `decides_witness_sound`, `applies_witness_sound`: a valid finite model that passes the background, the fill
   premises and `Γ`, with the formula true at a typed tuple, refutes them.
7. `allowed_witness_sound`: such a model, with no formula required, shows that an allowed situation exists.
   `facts_inconsistent_sound`: an accepted certificate for the negation of the conjunction of `Γ` shows that none
   does. A universal verdict (5, 8, 9) is reported only together with 7's witness; otherwise it is `unknown`, or
   the finding "the stated facts cannot all hold".
8. `conflictFreeUnder_sound`, `conflictUnder_witness_sound`: the two halves of the conflict check, with `Γ`.
9. `unsettled_iff_two_fillings`: `unsettledF` holds at a point of an admissible filling exactly when two
   admissible fillings that differ only in the table of that predicate give it opposite answers there.
   `gapFreeUnder_sound`; `raisedGap_unsettled`: a raised gap is an unsettled point of the same question.
10. `decidersAt_iff`: membership is "an author rule on `p` that decides there".
11. `eval_congr_why`: a model with the same domains and constants that agrees on the `why` atoms gives the
    formula the same value. Equalities are part of `why` for display (A4); they hold in every such model.

Fixtures (`#guard` in `Findings/Examples.lean`, hand-written expectations):

| Id | Input | Expected |
|---|---|---|
| fd1 | agent-policy, `environment.unspecified.lean.json` with `policy.ve`, the record model of action a10 | `decidersAt` gives rules 3 and 14; `clashF 3 14` true |
| fd2 | the same, record model of a06 | rule 12 applies; `decidersAt` gives rule 24 only |
| fd3 | the same, rule 19 and a27's model | the raised case "condition and exception both hold" is unsettled |
| fd4 | the same, rule 11 and a36's model | the near miss "get_secret and not confirmed" is unsettled |
| fd5 | two rules "may if internal", "must not if external", no facts; then with the fact "nothing is both internal and external" | a clash situation without the fact; a model that breaks the fact is refused with it |
| fd6 | a rule "may if gold and basic", fact "no gold member is basic" | an applies situation without the fact; none can pass with it |
| fd7 | `nearMisses` of "there is a file such that both A and B" | the two expected formulas, in order |
| fd8 | `Formula.why` on "there is a file that the action reads and that is in the workspace" at a01's model | the two atoms about that file |
| fd9 | "by default, refuse; permit if confirmed", a model with an unconfirmed action | the default is reached, the case is not unsettled, and its raised case is no gap ("the default answers here") |
| fd10 | a declared pair, an obligation rule that holds at the point, no permission rule deciding | the permission is a gap but pair-settled, so not unsettled |

Certificate-side expectations (rule 12 never decides; no dead condition; pair (3, 14) the only clash) are A2's
fixtures, because they need generated certificates.

Deleted or not duplicated: nothing is deleted in A1. Nothing is copied: `decidesF`, `appliesF`, `unsettledF` and
`raisedGapF` reuse `selects`, `applies`, `subst`, `before`, `gapF`, `outcomeBase` and `pairs`; no new
elaboration of rules is written.

### A2. Lean: service kinds and the public statements (3–5 h)

Additions to the `norm-defaults` service mode (`lean/VE/NormDefaults/Run.lean`, new
`lean/VE/NormDefaults/FindingsWire.lean`):

| Case kind | Extra input | Answer |
|---|---|---|
| `norm-defaults-elaborate` | none | gains `finding_targets`: for each author rule the keys `decides:<rule>`, `applies:<rule>`, `raised:<rule>:<k>` with sorts and formula, so that the untrusted provers and searchers get every target from Lean |
| `norm-defaults-rule` | `rule`, `question` (`decides` or `applies`), `premises`, `allowed_model`, and either `packages` or `model` with `tuple` | `finding`: `never` with an accepted certificate and a checked `allowed_model`, `some` with a checked situation, `facts-inconsistent` with an accepted certificate, else `unknown` |
| `norm-defaults-deciders` | `predicate` or `pair`, `model`, `tuple`, `premises` | for a predicate, `deciders`: the rules that decide there, each with its sign, and `clash`: whether two signs occur; for a pair, the deciders of each member, whether each member's default or filling answers, and `pair_conflict` |
| `norm-defaults-gaps` | gains optional `rule` with `case`, `premises` and `allowed_model` | `raised`: `unsettled` with a checked situation, `default-answers` (display only, never a finding) or `unknown`; a "no gap" verdict needs a checked `allowed_model`; the existing answers unchanged when the new fields are absent |
| `norm-defaults-conflict` | gains optional `premises` and `allowed_model` | the existing verdicts, relative to the stated facts; "conflict-free" needs a checked `allowed_model` |
| `norm-defaults-why` | `target`, `model`, `tuple` | the objects of each sort, then `equalities`, then `atoms`: the list of `Formula.why`, each with its truth value in the model |

`premises` are formulas over the base vocabulary of `fill U`. A premise that uses a regulated or defined word is
refused (`InvalidInput`), and a model that breaks a premise is refused (`InvalidModel: premises`), never turned
into a verdict. `allowed_model` is a finite model that must pass the background, `Fill_T` and the premises
(`allowed_witness_sound`); without one that passes, a universal verdict is `unknown`.

Public statements, one per verdict a caller can receive, each from raw JSON in the pattern of
`normDefaults_wire_reached_sound`: `normDefaults_wire_never_sound` (appendix), `normDefaults_wire_some_sound`,
`normDefaults_wire_inconsistent_sound`, `normDefaults_wire_deciders_sound`, `normDefaults_wire_pair_sound`,
`normDefaults_wire_raised_sound`, `normDefaults_wire_under_sound`.

Fixtures: `conformance/norm_defaults_findings.py` with `tests/test_norm_defaults_findings.py`.

- **The agent-policy answer key, section 7, is the main fixture**: rule 12 never decides (certificate) and every
  other rule decides somewhere; no condition is dead; exactly one of the 144 opposite-sign pairs clashes, (3, 14);
  mutant m1 has no clash and is conflict-free; mutant m5 makes (12, 24) clash at a06.
- The safety-framework answers N1 (a rule that can never apply through two levels, given a closure sentence) and
  N3 (no dead commitment) as stated-fact fixtures.
- Vacuity: a `never` question with stated facts that cannot all hold answers `facts-inconsistent`, and without
  a passing `allowed_model` answers `unknown`, never `never`.
- fd9 and fd10 through the service: `default-answers` and no `unsettled` answer.
- Conservativity: every existing `norm-defaults-*` and `norms-*` case of the conformance corpus gives a
  byte-identical answer (corpus A/B of the lean-first gate).

Deleted or not duplicated: the service gains kinds; no route is copied. The assurance manifest binds the new
decoders.

### A3. Python: relay, generators, command line; delete the harness copy (3–5 h)

- `ve/policy_findings.py`: reads the document and its stated facts, asks Lean for `finding_targets`, asks the
  untrusted generators for evidence (the existing Rust search for situations, the existing prover for
  certificates), sends each piece of evidence to Lean through `ve/backends/relay.py`, and returns Lean's rows.
  A generator that finds nothing yields `unknown`.
- `ve policy findings <document>`: prints the table of section 5.2.
- `usecases/agent-policy/focused.py` moves to `ve/focused.py` unchanged (it has two callers now). It only
  chooses among VE's own tableau rules, and Lean replays what it produces.

**Deleted in this batch:** in `usecases/agent-policy/check.py`, lines 554 to 581 only: the policy-level loops
that build formulas in Python from `NormDocument.selection` (opposite-sign pairs, never-deciding rules, dead
conditions). They become calls to `ve.policy_findings`. The helper `applies_open` stays (it is still used at
line 359), and so does `doc.selection` (it feeds the per-tool gap loop at line 584, which is not touched here).
Both remain until their callers migrate. `results.json` must be
unchanged in its `pairs`, `never_deciding` and `dead_guards` entries, apart from evidence ids;
`tests/test_agent_policy_rerun.py` is the gate. The per-action verdicts and the per-tool gap loop are not
touched here; they belong to lean-first batches 13b and 14. If A0 finds that the route refuses `data@0` flags,
these calls use the flag-free copy the case already ships (`environment.unspecified.lean.json`), as its Lean
replay does today. The key's answers to these three questions rest on precedence edges and on rule 24's
condition, not on the flags; the test confirms that or the batch records the difference.

Not duplicated: after this batch no Python builds the policy-level findings (opposite-sign pairs, never-deciding
rules, dead conditions). Python semantic code remains for its unmigrated callers (the table under the ownership
rule); the experiment cannot reach it, and no repository-wide deletion is claimed. `tools/relay_lint.py` covers
the new module.

### A4. Situations in English (2–4 h)

- Python renders what `norm-defaults-why` returns as fact sentences, with the environment's wordings, in a
  fixed order: first the objects of each sort ("There are two files."), then the equalities ("The file it reads
  is the file it writes."), then the atoms ("The action reads the file." / "The file is not in the workspace.").
  An unsaid atom becomes the existing sentence "Here the text does not say whether …; this situation answers
  yes". `eval_congr_why` holds only with the domains and constants fixed, so the reader is shown what they are.
  An explanation whose objects or equalities cannot be shown is marked "explanation incomplete".
- Every rendered sentence is read back by the English reader and must give the same atom, or the situation is
  shown as "not displayable" and the finding keeps its evidence id. Rendering is display; reading back is Lean's
  where the Lean reader covers the sentence, else the Python reader, stated in the output. In the measured run
  the sentence kinds shown are part of the English subset that gate O puts under Lean.
- Fixtures: the situations of fd1 to fd6 as expected English text, with no symbol, bracket or variable letter.

Not duplicated: no new renderer; `ve/english.py`'s rendering entry and the existing legend sentences are used.

### B0. Sources, licences, base texts (2–3 h; first network use)

- Fetch and pin the eleven sources (commit or release, URL, date, SHA-256). Check each licence file and record it
  in `experiments/policy-audit/SOURCES.md`. Stop on any mismatch with section 2.
- Deterministic paragraph splitter and name table per policy; base texts; word and token counts.
- Record which encodings of these policies are public (PCAS, the solver-aided paper, MANTRA's release).
- Fixtures: splitter round trip (joining the paragraphs gives the text); the name table is one-to-one; hashes.

Not duplicated: file handling only. Texts that may not be redistributed stay untracked.

### B1. Baseline tools (2–3 h)

- Pin Z3 (the `z3-solver` wheel and its hash) and Soufflé (release and hash). If Soufflé cannot be installed
  without root, Z3's Datalog engine replaces it, recorded as a deviation before the freeze.
- One runner for both with the caps of section 5.2 and structured output (result, model, error, time).
- Known-answer fixtures: the agent-policy policy written by hand in SMT-LIB and in Datalog, where the runner
  must reproduce (3, 14) as the only clash and an unconfirmed secret fetch as uncovered. These two encodings
  are fixtures for the runner. They are not shown to any arm.

### B2. Arm protocols, guides and prompts (4–6 h, development calls only)

- The four arm protocols of 5.2 and the reader protocol of 5.3 in `ve_experiments/policy_audit/`, on
  `ve_experiments/llm.py` and `runner.py`. Report parser (strict JSON at the end of the reply).
- The three writing guides, each at most 5,000 tokens, each with the raised-case recipe (5.2); the two baseline
  guides go to both plan reviewers for the "make it as strong as you can" review.
- The reader prompts of 5.3: source, rendering and task only.
- Development runs on τ² airline and the agent-policy paraphrase; measured tokens per item and arm, per
  adjudication call (one variant, all its reports), and as a share of Astra's plan allowance; the tier is chosen
  by the rule of section 11 and written into the freeze manifest. Development VE runs use whatever reader `main`
  has; they are not the measured arm.
- Fixtures: a full offline pass with scripted model replies for each arm.

Not duplicated: `llm.py` stays the only place that calls a model; the runner's pre-registration gate is used
as is.

### B3. Seeding, validation, translation-track materials (4–6 h, development calls only)

- Site survey, allocation, variant writer, key entry format, the two validators, the reserve order, the sealing
  step (key outside the worktrees, hash recorded).
- Translation track: reference renderings in three formalisms for the development sections, the agreement
  check on generated situations, the seed and its check.
- Dry run on τ² airline end to end (its key is not sealed and is committed as a worked example). The dry run
  also counts VE's raised-gap findings on the unseeded development text: how many true gaps the 8-report cap
  competes with on a policy that leaves most near misses open.
- The cluster check (4.2, step 7) and the materials seal (4.2, step 6) as code.
- Fixtures: allocation with shortfalls gives the totals of section 3; a variant always has three edits; a
  rejected variant is replaced in the recorded order.

### B4. Scorer and statistics (3–5 h, no model call)

- Semantic matching with candidate retrieval (6.2), false-report rates over all reports and the matched level
  (6.3), adjudication input and output, one call per variant and judge with shuffled reports (6.4), every table
  of 6.5, the gate mode and gate lines of section 9, the cluster rule, the verdict rule of section 8 as code.
- The paragraph-spray control arm (6.2).
- Statistics: the exact sign-flip test, Holm, the policy bootstrap, Wilson intervals, on `ve_experiments/stats.py`
  (extended, not copied).
- **Known-answer runs with scripted arms and scripted judges**: one that reads the key (recall 100%, no false report); one that
  reports nothing; one random; one that always reports the first paragraph. The scorer must give the values
  these imply, and the verdict rule must give "falsified: no headroom" for the first as a model-alone arm.
- **Power by simulation** under the assumptions of section 7; the table there is replaced by the simulated one.

### B5. Protocol freeze (2 h)

Only after the checks of section 9, step 0 (gate O, readability, coverage procedure) pass. Line 1 becomes
`Status: FROZEN`; the copy at `experiments/policy-audit/PREREG.md`; the protocol manifest of hashes (this file,
guides, prompts, harness, scorer, tool binaries, the Lean service binary and the Lean reader of gate O, model
ids, tier); OpenTimestamps receipt, as for T1c. The key, variants, allocation and base texts are not in it; they
go into the materials seal after seeding (4.2, step 6). Both plan reviewers have accepted the revised text. Only
then does seeding of scored policies start.

### R1 to R4. Runs

| Step | Content | Stops when |
|---|---|---|
| R1 | seeding, validation, cluster check, materials seal; coverage gate; recitation probe; headroom gate | V2, V1 or F1 |
| R2 | formal arms (tier A or B); translation track | a ceiling of section 11 |
| R3 | adjudication; the scorer opens the key | — |
| R4 | report in `experiments/policy-audit/RESULTS.md`: every table of 6.5, the verdict, every deviation, the natural-defect list | — |

### Order and effort

A0, B0 and B1 start at once. A1 (the revised stub) after A0; then A2; then A3 and A4 in parallel. B2 after A3
and B1; B3 after B0. B4's code may start at once; its validation against the semantic matching of 6.2 follows
this revision. Then the checks of section 9, step 0 (ownership, readability, coverage procedure), including the
Lean reader work A0 sizes for gate O; B5 after all of them and after both reviewers accept the revised text; then
R1 (seeding, cluster check, materials seal, gates) and the runs. About 11 batches and 30 to 50 build hours
before R1, reviews and gate O's reader work not counted; re-estimated after A0.

## 14. Honest limits

1. **Seeded defects are not natural defects.** Recall on seeds says how an arm does on the eight families as
   models write them. The natural-defect list is small and unscored.
2. **The key is model-made and model-checked.** It contains defects that a frontier model can confirm when told
   where to look. Defects that only a formal tool would confirm are absent, which works against all formal arms.
3. **Ten policies are ten clusters.** Intervals are wide, and a 15-point effect will most likely come out
   inconclusive.
4. **Judges are models.** No human checks a report unless the lead decides to sample. Judge error adds noise to
   false-report rates in every arm.
5. **The reader in the translation track is a model.** VE's claim that people can read it stays untested with
   people. The earlier readability result (59 of 60) rests on a plain-English baseline of 14 items.
6. **Same-family effects.** Seeders, judges and arm models come from two families. A Claude seeder may write
   defects that a Claude arm finds more easily. This inflates the model-alone arm, against VE's claim.
7. **Memorisation.** The models have very likely seen the τ-bench policies. Renaming and the recitation probe
   reduce and measure this; they do not remove it.
8. **VE is new to the models; Z3 and Datalog are not.** The VE arm depends on a 5,000-token guide and two
   repair rounds. A poor VE result may reflect writing difficulty and not checking power; the unknown rate, the
   rounds used and the reader's rejections are reported so that the two can be told apart.
9. **Translation errors create false findings.** A VE-checked situation is checked against the translation, not
   against the source. H7 measures how often that matters.
10. **Coverage.** Earlier translations of real texts formalised little (the safety framework: 8.5% of bytes
    CHECKED, most commitments OPEN on open terms). Agent policies are more procedural, but V1 may well fire.
    The CHECKED-anchor subset of P4 is not an expressible region: CHECKED establishes neither a complete nor a
    faithful translation.
11. **Expressiveness.** Time, counting and amounts become tool-supplied facts. A defect that lives in such a
    condition (two deadlines that cannot both be met) is invisible to VE and counts as a miss.
12. **Size limits.** A long manual may exceed 256 rules. Findings across its parts are lost.
13. **Proof search.** "Never decides" needs a certificate. If the provers run out, the answer is "unknown" and
    the item is a miss for the checked sub-arm.
14. **The matched level is set on the scored data.** Every arm gets the same advantage from that.
15. **One reading.** The measured run needs Lean-owned admission of the English subset it uses (gate O). Until
    that exists, only a labelled pilot on the Python reader can run, and the measured run waits. Python
    semantic paths remain on `main` for other callers (section 13); the experiment is guarded from them, but they
    are not deleted.
16. **Budget.** Tier B weakens the replication to gaps on five policies.
17. **Clusters.** If seeding leaves fewer than 8 policies with 3 gap items, the gap claim is void (V2), whatever
    the arms would have shown.
18. **This draft's own gaps:** licences re-check pending; Lean statements not elaborated; power figures by hand;
    the size of gate O's reader work unknown until A0.

## 15. Questions for the DRI

1. Arm models: Opus 5.5 and GPT-6 Sol as planned, with Fable and Astra as seeders, judges and cross-checks? The
   alternative (Fable and Astra as arms) would test the strongest models everywhere but leaves no strong seeder
   outside the arms, and Astra's allowance is small.
2. ~~Freeze before or after E3 moves rule-block English to Lean (section 12)?~~ **Resolved by the DRI ruling
   (2026-10-06):** the measured VE arm uses Lean-owned admission for the English subset it uses (E2/E3 or an
   equivalent scoped delivery); full E3 does not block development or A0, B0 and B1; gate O blocks the measured
   run (sections 9 and 12).
3. The Claude Code page has no open licence. Use it by reference as planned, or drop it for the reserve?
4. May Astra's steps use the lead's held Codex reset if the plan allowance runs short?
5. Should the lead or another person check a sample of adjudicated reports (limit 4)?

## Deviations

Empty at plan time. A0's probe results and every later change go here, each with date, section, old text, new
text and reason. (Draft 2 is a pre-freeze revision, described under the title, not a deviation.)

## Appendix: Lean stub (not elaborated; batch A0 elaborates it first)

`lean/audit.py` constraints are respected: no primes or question marks in theorem names, names under 57
characters, none of the audit's forbidden words in comments.

```lean
import VE.NormDefaults.Replay

namespace VE
universe u

/-- One fact shown to a reader: a ground atom, or whether two objects are the same. -/
inductive WhyFact (α : Type u) where
  | atom (p : String) (args : List α)
  | eq (v w : α)

/-- A small set of facts that settles the value of a formula in a finite model: enough to
show a reader, and any model with the same domains and constants that agrees on its atoms
gives the same value. Equalities are kept for the reader; they hold in every such model. -/
def Formula.why {α : Type u} [DecidableEq α] (M : FiniteModel α) (ρ : List α) :
    Formula → List (WhyFact α)
  | .top => []
  | .bottom => []
  | .eq t s => match t.denote M.asStructure ρ, s.denote M.asStructure ρ with
      | some v, some w => [.eq v w]
      | _, _ => []
  | .unary p t => match t.denote M.asStructure ρ with
      | some v => [.atom p [v]]
      | none => []
  | .binary p t s => match t.denote M.asStructure ρ, s.denote M.asStructure ρ with
      | some v, some w => [.atom p [v, w]]
      | _, _ => []
  | .not a => a.why M ρ
  | .and a b =>
      if a.eval M ρ then (if b.eval M ρ then a.why M ρ ++ b.why M ρ else b.why M ρ) else a.why M ρ
  | .or a b =>
      if a.eval M ρ then a.why M ρ else (if b.eval M ρ then b.why M ρ else a.why M ρ ++ b.why M ρ)
  | .implies a b =>
      if a.eval M ρ then (if b.eval M ρ then b.why M ρ else a.why M ρ ++ b.why M ρ) else a.why M ρ
  | .all s a => match (M.domains s).find? (fun v => !(a.eval M (v :: ρ))) with
      | some v => a.why M (v :: ρ)
      | none => (M.domains s).flatMap (fun v => a.why M (v :: ρ))
  | .ex s a => match (M.domains s).find? (fun v => a.eval M (v :: ρ)) with
      | some v => a.why M (v :: ρ)
      | none => (M.domains s).flatMap (fun v => a.why M (v :: ρ))

theorem eval_congr_why {α : Type u} [DecidableEq α] (M N : FiniteModel α) (ρ : List α) (φ : Formula)
    (hd : N.domains = M.domains) (hc : N.constants = M.constants)
    (hr : ∀ p xs, WhyFact.atom p xs ∈ φ.why M ρ → (xs ∈ N.relations p ↔ xs ∈ M.relations p)) :
    φ.eval N ρ = φ.eval M ρ := by
  stub

end VE

namespace VE.NormDefaults
open VE.Norms VE.Route
universe u

/-- A formula of rule `N` read on the base vocabulary of `fill U`: lower layer symbols become
their outcomes, so lower gaps appear as unsaid atoms (as `gapF` reads `pos` and `neg`). -/
def baseOf (U : UDoc) (N : Node) (φ : VE.Formula) : VE.Formula :=
  subst (fill U).T (before (fill U) N.pred) φ

/-- "Rule `N` decides here." -/
def decidesF (U : UDoc) (N : Node) : VE.Formula := baseOf U N (selects U.D.T (fuel U.D.T) N)

/-- "The condition of rule `N` holds here and none of its stated exceptions does." -/
def appliesF (U : UDoc) (N : Node) : VE.Formula := baseOf U N (applies N)

/-- "Rules `N₁` and `N₂` both decide here." -/
def clashF (U : UDoc) (N₁ N₂ : Node) : VE.Formula := .and (decidesF U N₁) (decidesF U N₂)

/-- The situations the document's own stated facts `Γ` leave open. -/
def Allowed (U : UDoc) (Γ : List VE.Formula) (B : VE.Structure.{u}) : Prop :=
  BaseAdmissibleU U B ∧ Sat B Γ

def NeverDecides (U : UDoc) (Γ : List VE.Formula) (N : Node) : Prop :=
  ∀ B : VE.Structure.{u}, Allowed U Γ B → ∀ vs, VE.TupleTyped B (sortsOf U.D N.pred) vs →
    ¬ (decidesF U N).denote B (tupleVal vs)

def NeverApplies (U : UDoc) (Γ : List VE.Formula) (N : Node) : Prop :=
  ∀ B : VE.Structure.{u}, Allowed U Γ B → ∀ vs, VE.TupleTyped B (sortsOf U.D N.pred) vs →
    ¬ (appliesF U N).denote B (tupleVal vs)

def ConflictFreeUnder (U : UDoc) (Γ : List VE.Formula) : Prop :=
  ∀ B : VE.Structure.{u}, Allowed U Γ B → ConflictFree (fill U) B

/-- "A declared pair forces `p`'s answer here": `p` is the permission member of a pair whose
obligation holds, or the obligation member of a pair whose permission fails. -/
def pairSettledF (U : UDoc) (p : String) : VE.Formula :=
  ((pairs U.D.T).filterMap fun pr =>
      if pr.perm = p then some (outcomeBase (fill U) pr.req)
      else if pr.req = p then some (.not (outcomeBase (fill U) pr.perm))
      else none).foldr .or .bottom

/-- "No author rule decides `p` here, no stated default answers, and no pair forces it":
the text leaves the answer open. -/
def unsettledF (U : UDoc) (p : String) : VE.Formula :=
  .and (gapF U p) (.not (pairSettledF U p))

def GapFreeUnder (U : UDoc) (Γ : List VE.Formula) (r : Regulated) : Prop :=
  ∀ B : VE.Structure.{u}, Allowed U Γ B → ∀ vs, VE.TupleTyped B r.sorts vs →
    ¬ (unsettledF U r.name).denote B (tupleVal vs)

/-- The cases a condition names by reversing exactly one of its parts. -/
def nearMisses : VE.Formula → List VE.Formula
  | .and a b => (nearMisses a).map (fun x => .and x b) ++ (nearMisses b).map (fun x => .and a x)
  | .ex s a => (nearMisses a).map (fun x => .ex s x)
  | .not a => [a]
  | φ => [.not φ]

/-- The cases rule `N` itself raises: each near miss of its condition, then each stated exception. -/
def raisedCases (N : Node) : List VE.Formula :=
  nearMisses N.guard ++ N.carveOuts.map (fun c => .and N.guard c)

/-- "The `k`-th case that rule `N` raises occurs here, and the text leaves its question open."
A case a stated default answers is not open (`gapF` is `.bottom` off `U.unspec`). -/
def raisedGapF (U : UDoc) (N : Node) (k : Nat) : VE.Formula :=
  .and (baseOf U N ((raisedCases N).getD k .bottom)) (unsettledF U N.pred)

/-- The author rules on `p` that decide at a checked point. -/
def decidersAt {α : Type u} [DecidableEq α] (U : UDoc) (M : VE.FiniteModel α) (p : String) (vs : List α) :
    List Node :=
  (rulesOn U.D.T p).filter (fun N => (decidesF U N).eval M (tupleVal vs))

theorem conflictFreeUnder_nil (U : UDoc) : ConflictFreeUnder.{u} U [] ↔ ConflictFreeU.{u} U := by
  stub

theorem decidesF_iff_selects (U : UDoc) (h : WellFormedU U = true) (N : Node) (hN : N ∈ U.D.T.nodes)
    (S : VE.Structure.{u}) (hS : S.Admissible (envAt (fill U) (before (fill U) N.pred)))
    (hlow : Sat S (PrefixPremises (fill U) (before (fill U) N.pred)))
    (vs : List S.Carrier) (typed : VE.TupleTyped S (sortsOf U.D N.pred) vs) :
    (decidesF U N).denote (restrictAll (fill U).T S) (tupleVal vs) ↔
      SelectsD U.D.T S (tupleVal vs) (fuel U.D.T) N := by
  stub

theorem conflict_iff_clash (U : UDoc) (h : WellFormedU U = true) (r : Regulated) (hr : r ∈ U.D.T.regulated)
    (B : VE.Structure.{u}) (hB : BaseAdmissibleU U B) (vs : List B.Carrier)
    (typed : VE.TupleTyped B r.sorts vs) :
    (conflict (fill U) r).denote B (tupleVal vs) ↔
      ∃ N₁ ∈ rulesOn U.D.T r.name, ∃ N₂ ∈ rulesOn U.D.T r.name,
        N₁.sign = true ∧ N₂.sign = false ∧ (clashF U N₁ N₂).denote B (tupleVal vs) := by
  stub

/-- An obligation-permission conflict has a named explanation on each side: a deciding
author rule of the right sign, or the member's own default or filling. -/
theorem pairConflict_explained (U : UDoc) (h : WellFormedU U = true) (pr : Pair) (hpr : pr ∈ pairs U.D.T)
    (B : VE.Structure.{u}) (hB : BaseAdmissibleU U B) (vs : List B.Carrier)
    (typed : VE.TupleTyped B pr.sorts vs)
    (hc : (pairConflict (fill U) pr).denote B (tupleVal vs)) :
    ((∃ N ∈ rulesOn U.D.T pr.req, N.sign = true ∧ (decidesF U N).denote B (tupleVal vs)) ∨
        (reachedF U pr.req).denote B (tupleVal vs)) ∧
      ((∃ N ∈ rulesOn U.D.T pr.perm, N.sign = false ∧ (decidesF U N).denote B (tupleVal vs)) ∨
        (reachedF U pr.perm).denote B (tupleVal vs)) := by
  stub

theorem never_decides_sound (U : UDoc) (Γ : List VE.Formula) (N : Node) (c : VE.Tableau.Certificate)
    (ok : VE.Tableau.checkCertificate (envAt (fill U) 0) (Wire.baseBackgroundU U ++ Γ)
      (bindAll (sortsOf U.D N.pred) (.not (decidesF U N))) c = true) :
    NeverDecides.{u} U Γ N := by
  stub

theorem never_applies_sound (U : UDoc) (Γ : List VE.Formula) (N : Node) (c : VE.Tableau.Certificate)
    (ok : VE.Tableau.checkCertificate (envAt (fill U) 0) (Wire.baseBackgroundU U ++ Γ)
      (bindAll (sortsOf U.D N.pred) (.not (appliesF U N))) c = true) :
    NeverApplies.{u} U Γ N := by
  stub

theorem decides_witness_sound {α : Type u} [DecidableEq α] (U : UDoc) (Γ : List VE.Formula) (N : Node)
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (fill U) 0))
    (hb : backgroundValid (fill U) M = true)
    (hf : (fillPremises U).all (fun φ => φ.eval M []) = true)
    (hg : Γ.all (fun φ => φ.eval M []) = true)
    (vs : List α) (typed : VE.TupleTyped M.asStructure (sortsOf U.D N.pred) vs)
    (hw : (decidesF U N).eval M (tupleVal vs) = true) :
    ¬ NeverDecides.{u} U Γ N := by
  stub

theorem applies_witness_sound {α : Type u} [DecidableEq α] (U : UDoc) (Γ : List VE.Formula) (N : Node)
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (fill U) 0))
    (hb : backgroundValid (fill U) M = true)
    (hf : (fillPremises U).all (fun φ => φ.eval M []) = true)
    (hg : Γ.all (fun φ => φ.eval M []) = true)
    (vs : List α) (typed : VE.TupleTyped M.asStructure (sortsOf U.D N.pred) vs)
    (hw : (appliesF U N).eval M (tupleVal vs) = true) :
    ¬ NeverApplies.{u} U Γ N := by
  stub

/-- A checked model of the background, `Fill_T` and the stated facts: the universal
verdicts above are then not empty. -/
theorem allowed_witness_sound {α : Type u} [DecidableEq α] (U : UDoc) (Γ : List VE.Formula)
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (fill U) 0))
    (hb : backgroundValid (fill U) M = true)
    (hf : (fillPremises U).all (fun φ => φ.eval M []) = true)
    (hg : Γ.all (fun φ => φ.eval M []) = true) :
    ∃ B : VE.Structure.{u}, Allowed U Γ B := by
  stub

/-- "The stated facts cannot all hold." -/
theorem facts_inconsistent_sound (U : UDoc) (Γ : List VE.Formula) (c : VE.Tableau.Certificate)
    (ok : VE.Tableau.checkCertificate (envAt (fill U) 0) (Wire.baseBackgroundU U)
      (.not (Γ.foldr .and .top)) c = true) :
    ∀ B : VE.Structure.{u}, ¬ Allowed U Γ B := by
  stub

theorem conflictFreeUnder_sound (U : UDoc) (Γ : List VE.Formula)
    (certs : List (Option VE.Tableau.Certificate))
    (hl : (targets (fill U)).length = certs.length)
    (ok : ((targets (fill U)).zip certs).all (fun tc => match tc.2 with
      | some c => VE.Tableau.checkCertificate (envAt (fill U) 0) (Wire.baseBackgroundU U ++ Γ)
          (targetConclusion tc.1) c
      | none => false) = true) :
    ConflictFreeUnder.{u} U Γ := by
  stub

theorem conflictUnder_witness_sound {α : Type u} [DecidableEq α] (U : UDoc) (Γ : List VE.Formula)
    (t : String × List String × VE.Formula) (ht : t ∈ targets (fill U))
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (fill U) 0))
    (hb : backgroundValid (fill U) M = true)
    (hf : (fillPremises U).all (fun φ => φ.eval M []) = true)
    (hg : Γ.all (fun φ => φ.eval M []) = true)
    (vs : List α) (typed : VE.TupleTyped M.asStructure t.2.1 vs)
    (hw : t.2.2.eval M (tupleVal vs) = true) :
    ¬ ConflictFreeUnder.{u} U Γ := by
  stub

/-- At a point of an admissible filling, "unsettled" is "two admissible fillings that differ
only in `r`'s own table give opposite answers there". -/
theorem unsettled_iff_two_fillings (U : UDoc) (h : WellFormedU U = true) (r : Regulated)
    (hr : r ∈ U.D.T.regulated) (B : VE.Structure.{u}) (hB : BaseAdmissible U.D B) (F : FillTables U B)
    (hF : BaseAdmissibleU U (withFill U B F)) (vs : List B.Carrier) (typed : VE.TupleTyped B r.sorts vs) :
    (unsettledF U r.name).denote (withFill U B F) (tupleVal vs) ↔
      ∃ F₁ F₂ : FillTables U B, (∀ n, n ≠ unsaidName r.name → F₁ n = F n ∧ F₂ n = F n) ∧
        BaseAdmissibleU U (withFill U B F₁) ∧ BaseAdmissibleU U (withFill U B F₂) ∧
        (outcomeBase (fill U) r.name).denote (withFill U B F₁) (tupleVal vs) ∧
        ¬ (outcomeBase (fill U) r.name).denote (withFill U B F₂) (tupleVal vs) := by
  stub

theorem gapFreeUnder_sound (U : UDoc) (Γ : List VE.Formula) (r : Regulated) (c : VE.Tableau.Certificate)
    (ok : VE.Tableau.checkCertificate (envAt (fill U) 0) (Wire.baseBackgroundU U ++ Γ)
      (bindAll r.sorts (.not (unsettledF U r.name))) c = true) :
    GapFreeUnder.{u} U Γ r := by
  stub

theorem raisedGap_unsettled (U : UDoc) (N : Node) (k : Nat) (B : VE.Structure.{u}) (ρ : VE.Valuation B) :
    (raisedGapF U N k).denote B ρ → (unsettledF U N.pred).denote B ρ := by
  stub

theorem decidersAt_iff {α : Type u} [DecidableEq α] (U : UDoc) (M : VE.FiniteModel α) (p : String)
    (vs : List α) (N : Node) :
    N ∈ decidersAt U M p vs ↔
      N ∈ rulesOn U.D.T p ∧ (decidesF U N).denote M.asStructure (tupleVal vs) := by
  stub

end VE.NormDefaults

namespace VE.NormDefaults.Wire
open Lean
open VE.Norms

/-- A replayed "never" question: the decoded source, the stated facts, the rule, which
question (`true` for decides, `false` for applies), the bound certificate, if any, and
whether the decoder checked an `allowed_model` against the background, `Fill_T` and the
stated facts (the checks of `allowed_witness_sound`). -/
structure FindingReplay where
  s : SourceU
  Γ : List VE.Formula
  N : Node
  mem : N ∈ s.U.D.T.nodes
  question : Bool
  cert : Option VE.Tableau.Certificate
  allowed : Bool

def FindingReplay.target (g : FindingReplay) : VE.Formula :=
  if g.question then decidesF g.s.U g.N else appliesF g.s.U g.N

/-- "Never" needs both the certificate and a checked allowed situation; otherwise the
answer is `unknown`. -/
def FindingReplay.never (g : FindingReplay) : Bool := g.allowed && match g.cert with
  | some c => VE.Tableau.checkCertificate (envAt (fill g.s.U) 0) (baseBackgroundU g.s.U ++ g.Γ)
      (bindAll (sortsOf g.s.U.D g.N.pred) (.not g.target)) c
  | none => false

/-- Decoder of a `norm-defaults-rule` case with `packages`; written in A2. -/
def replayFinding (j : Json) : Except String FindingReplay := by
  stub

theorem normDefaults_wire_never_sound (j : Json) (g : FindingReplay) (h : replayFinding j = .ok g)
    (hn : g.never = true) :
    decodeSourceU (j.getObjValD "environment") (j.getObjValD "norms") = .ok g.s ∧
      (∃ B : VE.Structure.{0}, Allowed g.s.U g.Γ B) ∧
      (if g.question then NeverDecides.{0} g.s.U g.Γ g.N else NeverApplies.{0} g.s.U g.Γ g.N) := by
  stub

end VE.NormDefaults.Wire
```

In the stub, `stub` stands for the proof or body that the batch writes; A0 replaces it with Lean's placeholder
term locally to elaborate the statements, and no placeholder is committed.
