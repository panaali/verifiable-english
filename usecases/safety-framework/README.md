# A frontier-lab safety framework, translated into VE

This case translates a published safety framework into VE: Google DeepMind's *Frontier Safety Framework*,
version 3.1, published on 17 April 2026. VE then answers four questions about it:

- What does the framework require at each named capability level?
- Do any two of its commitments conflict?
- Which levels or situations does no rule cover?
- Which commitments can never apply?

The text is someone else's, so the translation keeps every reading the text allows. It names every vague term as
an open term with the person or body who decides it. It adds no default, permission, threshold or causal link
that the text does not state.

The plan, with the answer key written before VE was run, is [PLAN.md](PLAN.md). Section 12 of the plan lists every
deviation from it. The answer key was never changed to match VE.

## The source

| Field | Value |
|---|---|
| Document | Google DeepMind, *Frontier Safety Framework*, version 3.1, 20 pages |
| URL | `https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/strengthening-our-frontier-safety-framework/frontier-safety-framework_3-1.pdf` |
| Retrieved | 2026-10-01 |
| PDF SHA-256 | `ad10d2d240e0d557ecad406dbccedcbb4a70295f8ba8eec46bfe01803cb9c301` |
| Text SHA-256 | `18e3375b35c6699a8bf864606e48a20fae0152f1073c37c51e27a0c0f0c53946` (54,373 bytes, from [source/extract_text.py](source/extract_text.py)) |

It was chosen because it is current and versioned, it names seven capability levels with if-then commitments for
each, and it states the severity of each level in its own words. PLAN section 1 gives the full reasons and the two
texts not chosen. The PDF states no licence, so it is not committed here.

## Files

| File | Contents |
|---|---|
| [rules.d1.ve](rules.d1.ve) | 44 VE rules: one per commitment and per reading of it, each with the sentence it translates |
| [facts.d1.ve](facts.d1.ve) | 43 VE premises: the level tables, the closure sentences, the Glossary definitions and one bridge |
| [vocabulary.py](vocabulary.py), [environment.d1.json](environment.d1.json) | the vocabulary; each predicate's description is its legend |
| [cases.json](cases.json), [answer-key.json](answer-key.json) | the 85 cases and the 262 answers of PLAN sections 5 and 6, transcribed before VE ran |
| [run.py](run.py), [translation.py](translation.py), [severity_and_dates.py](severity_and_dates.py) | the harness that runs VE on every case and compares with the key |
| [results.json](results.json) | everything the harness computed |
| [build_document.py](build_document.py), [spans.json](spans.json), [coverage.json](coverage.json) | the byte-by-byte accounting of the source text |
| [reference.py](reference.py) | a second reading of the commitments in plain Python, which shares no code with VE |
| [../../tests/test_safety_framework.py](../../tests/test_safety_framework.py) | the test: it fails on any mismatch with the key or any change in a result |

Run `python usecases/safety-framework/run.py` to recompute everything (a few minutes). The severity family
needs the Lean risk route, so run `lake build` in `lean/` first.

## Result: agreement with the answer key

VE agrees with the answer key on **257 of 262** items.

| Family | What it asks | Agreement |
|---|---|---|
| A | what each level requires, for each of five activities | 157 / 160 |
| B | what each level requires whatever the activity | 40 / 40 |
| K | what the process triggers require | 18 / 18 |
| R | when the text deems a model's risk acceptable | 11 / 11 |
| C | conflicts | 4 / 6 |
| G | gaps | 9 / 9 |
| N | commitments that can never apply | 3 / 3 |
| S | severity and causation | 12 / 12 |
| D | dates | 3 / 3 |

### The five disagreements

Each disagreement is a finding. Three show an error in a note of the answer key. The other two show that the key's
conflict answers rest on a narrowing that the results review withdrew.

1. **A-L5-INT, A-L6-INT and A-L7-INT (DM).** Both VE and the key say that deployment mitigations are not required
   for an ordinary internal deployment at these levels. The key adds that, under one reading, a rule releases them
   ("need not"). That note is wrong. Bullets 3 and 4 of section 1.3.5 say "not further development"; they do not
   mention internal deployment. So no rule speaks about mitigations for an ordinary internal deployment at the ML
   R&D levels: the text is silent there. The independent Python reading ([reference.py](reference.py)) finds the
   same.
2. **C1 and C-doc.** The key says that the recommended security level (F16) never conflicts with the
   insider-misuse sentence (F15). It was written under narrowing N2, which read the field's "should" as a default
   rule only. The adjustment cases of 2.2 fit a strict rule with stated exceptions just as well, so the results
   review withdrew N2 and the translation now keeps both forces (reading set RS3force). Under the strict force,
   when both sentences name one act (RS6 = same), they conflict: Security level 2+ includes the insider-threat
   measures that F15 says need not be added. VE finds a witness that satisfies every premise: CBRN uplift level 1,
   further development. So C1 is SOME(RS3 = Ds, RS3force = strict, RS6 = same), and C-doc adds this choice to C3's.
   With N2 restored, C1 is conflict-free at every choice (`variants.with_N2` in [results.json](results.json)). The
   independent Python reading finds the same.

The first run also missed K2-L1, K2-L5 and G3, which ask about an alert threshold for a Tracked Capability Level.
The translation had read "For CCLs, we define alert thresholds" (1.3.2) as a closure, so that only a CCL could have
an alert threshold. The sentence does not say that, and the results review removed the premise. These cases now
agree with the key: no rule speaks about an alert threshold for a TCL. Section 1.2 does say that "early warning
evaluations will be used to assess the proximity of a model to a TCL", but it names no trigger, so it stays
unformalised.

## The rules and their check status

VE checks a unit only when its whole meaning is formal. A rule is **OPEN** when its condition uses an open term,
such as "the model has reached this level", which only the developer decides. A rule is also OPEN when the text
has more than one reading of it. The table gives each commitment in plain English.

| Commitment | In plain English | Status | Why |
|---|---|---|---|
| F2 (1.3.2) | A critical capability assessment comes before the first external deployment of a new frontier model. | OPEN | "frontier model" is an open term |
| F3 (footnote 4) | That assessment is not needed for a low-risk external deployment that the governance function has found acceptable. | OPEN | two readings: an exception, or "may" in the sense of "might" |
| F4 (1.3.2) | A subsequent version is checked for substantial modification; a further assessment may be required. | OPEN | two readings of what the "if" attaches to |
| F5 (1.3.2) | Material capability change assessments follow each completed post-training run. | CHECKED | |
| F6 (1.3.3) | Reaching an alert threshold for a CCL triggers a proximity assessment and a risk analysis. | OPEN | reaching a threshold is an open term |
| F7 (1.3.4) | A model at a TCL or CCL gets a residual risk assessment; at a CCL it is informed by a safety case. | OPEN | reaching a level is an open term |
| F8 (1.3.5) | A model at no level is deemed acceptable. | OPEN | reaching a level is an open term |
| F9 to F11 (1.3.5) | A model at a level is deemed acceptable when the stated mitigation and security conditions hold. | OPEN | three reading sets: sufficient or gate; scope or release; one act or two |
| F12, F13 (2.1.2, 3.1.2) | A deployment takes place only after the governance function finds its residual risk acceptable. | OPEN | two readings: within the section's process, or for every model |
| F14 (2.1.2, 3.1.2) | A material update to a safety case goes to the governance function for review. | CHECKED | |
| F15 (2.2) | Mitigations against insider misuse beyond the baseline controls are not required. | OPEN | two readings: the same act as Security Level 2+'s insider measures, or a different one |
| F16 (2.2, 3.2.2) | The recommended security level should be applied. | OPEN | two readings: a recommendation to the field only, or a "should" that also binds the developer, strictly or as a default |
| F17 (3.2.1) | At the stealth TCL, periodic misalignment assessments run, and safeguards are added when they are needed. | OPEN | "periodic" and reaching a level are open terms |
| F18 (5.1) | The framework is reviewed at least once a year. | CHECKED | |
| F18 (5.1) | It is reviewed more often when there are reasonable grounds. | OPEN | "reasonable grounds" is an open term |
| F19 (5.2) | Information is shared with government authorities when a CCL poses an unmitigated public-safety risk. | OPEN | two readings of "we aim to" |
| F20 (1.3.5 Note, Glossary, Note on ML R&D) | Mitigations are assessed holistically; residual risk is brought within acceptable levels; risk assessment allows for greater effort by others. | OPEN | each "should" or "must" is strict or a default |

No commitment is LABELLED. Several process sentences are UNFORMALISED, each with a reason: for example "we will
review the Framework periodically" names no deadline, and "the updated version ... will be reviewed by the
appropriate corporate governance bodies" concerns the order of events. [spans.json](spans.json) gives every unit
and its reason.

## Conflicts found

**Two conflicts.** Each needs its own choice of readings.

- **C3.** Rule F9 says that deployment mitigations need not be in place for an internal deployment of a misuse
  model. Rule F10 says that they must be in place for a high-risk internal deployment of an ML R&D model. A model
  that has reached both a misuse level and an ML R&D level, proposed for high-risk internal deployment, falls under
  both. This happens only when three readings hold together: the conditions are a gate (RS1 = G), "not internal
  deployment" is a release (RS8 = rel), and the two bullets name one act (RS9 = same).
- **C1.** The recommended security level (F16) against the insider-misuse sentence (F15). Security level 2+ includes
  measures against insider threats, and F15 says that mitigations against insiders beyond the baseline are not
  required. This happens only when the recommendation binds the developer (RS3 = Ds) with strict force (RS3force =
  strict), and both sentences name one act (RS6 = same). Under the default force, the strict "not required"
  overrides the default rule without a conflict.

VE finds a witness situation that satisfies every premise for each. These are the only conflicts in the whole
document (C-doc).

**No conflict in the other three pairs.**

- C2: footnote 4 is an exception to F2.
- C4 and C5: the rules regulate different acts. "Deemed acceptable" is a classification, not a permission to
  deploy.

## Gaps found

"Silent" means that no rule says anything, so the answer depends only on a default that the text never states.

| Gap | Situation | VE's answer |
|---|---|---|
| G1 | further development of a CCL model whose security condition fails | silent unless the conditions are read as a gate |
| G2 | an ordinary internal deployment of an ML R&D CCL model | no governance review is required |
| G3 | an alert threshold for a TCL | silent: no rule mentions it |
| G4, G5 | significant cyber or manipulation risk, or a risk outside the four domains | only the catch-all "deemed acceptable" applies; no safeguard is required |
| G6 | the first external deployment of a model that is not a frontier model | no capability assessment is required; governance review only if F12 covers every model |
| G7 | disclosure for a TCL | silent: disclosure needs a CCL |
| G8 | evidence after deployment that safeguards are circumvented | silent: no rule mentions it |
| G9 | the governance function does not find a deployment acceptable | covered for a model at a level; for a model at no level, only if F12 covers every model |

Family A adds more gaps. Of the 192 items whose answer is a selection, 146 are silent under at least one choice of
readings, and 73 are silent under every choice. At exactly those choices, the outcome VE completes depends on the
default (metric M7). The text never says what happens when a stated condition fails: R3 and R7 show that a failed
condition makes no rule conclude "acceptable", but no rule says "not acceptable" either.

## Commitments that can never apply

- **N1.** Rule F9 can never apply through a cyber or harmful-manipulation TCL. VE proves this from the closure
  sentence "We identify TCLs for CBRN risk, as well as ML R&D and misalignment risks", with checked certificates.
- **N2.** Whether the CBRN TCL has a recommended security level is undetermined. VE finds two checked models of the
  premises, one with and one without such a level. VE does not invent one.
- **N3.** No commitment is dead. Each of the 44 rules is selected in some situation that satisfies every premise.

## Severity, causation and dates

- **Severity.** The risk route admits the classes as the text states them: severe for the five CCLs and significant
  for the two TCLs. Severe ranks above significant (Glossary). "Catastrophic" (3.2.2) is not ranked against either,
  and VE reports the pair as unranked.
- **Causation.** Deploying an unmitigated model at CBRN uplift level 1 *might* lead to severe harm, because the text
  says "may pose". It is not entailed that it *leads to* severe harm. Every causal sentence of the text is LABELLED.
- **Dates.** The version dates increase. Version 3.1 was published before the retrieval date. A review is due by
  17 April 2027 only if "at least once a year" counts from the publication of version 3.1. If it counts from an
  undated last review, VE gives a countermodel.

## What stayed OPEN, and why

- **16 open terms.** Examples: whether a model has reached a level; whether residual risk is acceptable; whether a
  deployment is high-risk or low-risk; "frontier model"; "periodic"; "reasonable grounds". The text names a
  decider for most of them ("we" or the governance function) and gives no criteria, so VE never decides them. Every
  answer in families A, B, K and R is "required, given the stated level and findings".
- **18 reading sets.** VE's own readings query returns UNKNOWN for norm readings, as the plan expected. The ALL,
  SOME and NONE answers come from the harness, which builds one document per choice of readings.
- **Order of events.** VE has no deadlines inside a process, so "prior to", "after" and "upon completion" are read
  as conditions that already hold.
- **External standards.** The RAND security levels, SAIF and the cited papers are pointers, not content.
- **One bridge.** No level belongs to two of the four domains. The text implies this by its structure but does not
  state it, so the premise is marked as an assumption.

## Span accounting

All 54,373 bytes of the source are in exactly one unit of the document (290 units).

| Status | Bytes | Share |
|---|---|---|
| CHECKED | 4,595 | 8.5% |
| OPEN | 7,356 | 13.5% |
| LABELLED | 35,557 | 65.4% |
| UNFORMALISED | 6,865 | 12.6% |

The CHECKED share includes 1,108 bytes that the severity and date documents check. Within the main document alone,
3,487 bytes are CHECKED. The plan expected less than 10%. Most of the text is exposition, examples, definitions and
page layout. The commitments are OPEN because their conditions use open terms.

## Metrics

| Metric | Result | Expected |
|---|---|---|
| M1 agreement with the key | 257/262 | 262/262, every miss explained |
| M2 reading sets | 14 sets (13 in the main document, RS10 in the date document), placed on 18 units; at most 16 choices per item, and 64 for C-doc, the union over every act; VE's own readings query is UNKNOWN on every norm set | as found |
| M3 CHECKED share | 8.5% | under 10% |
| M4 how each answer is backed | each per-choice answer rests on a case model that VE validated, a replayed certificate, or the Lean risk route | reported |
| M5 one-off identifiers | 0 | 0 |
| M6 untraced premises or rules | 0; one bridge marked as an assumption | 0 |
| M7 items whose completed outcome depends on the default | 146, exactly at the silent cells and at the C1 conflict cell (B-L2 to B-L4, RECSEC) | the silent items |
| M8 evidence | every certificate is replayed; conflict witnesses satisfy every premise; the severity answers come from the Lean risk route | reported |
| M9 seeded mutants detected | 6/6 (m4 and m6 differ from the plan's expectation, PLAN section 12) | 6/6 |
| M10 cost | 85 cases, 108 documents, 658 case models, 2,054 prover calls, a few minutes | reported |

## Deviations

PLAN section 12 lists every deviation, with its reason. The main ones:

- Each act has its own regulated predicate, so that rules read as plain English.
- The conflict check runs against the premises, because VE's W1 check also counts impossible situations, such as a
  proposal that is both internal and external.
- Four Glossary sentences and one bridge became premises.
- After the results review: "For CCLs, we define alert thresholds" is no longer a premise, and narrowing N2 is
  withdrawn, so F16 under RS3 = Ds keeps both its strict and its default force.
