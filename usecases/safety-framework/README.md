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
| [facts.d1.ve](facts.d1.ve) | 37 VE premises: the level tables, the closure sentences and the Glossary definitions; and N1's own bridge |
| [vocabulary.py](vocabulary.py), [environment.d1.json](environment.d1.json) | the vocabulary; each predicate's description is its legend |
| [cases.json](cases.json), [answer-key.json](answer-key.json) | the 85 cases and the 262 answers of PLAN sections 5 and 6, transcribed before VE ran |
| [run.py](run.py), [translation.py](translation.py), [severity_and_dates.py](severity_and_dates.py) | the harness that runs VE on every case and compares with the key |
| [results.json](results.json) | everything the harness computed |
| [build_document.py](build_document.py), [spans.json](spans.json), [coverage.json](coverage.json) | the byte-by-byte accounting of the source text |
| [reference.py](reference.py) | a second reading of the commitments in plain Python, which shares no code with VE |
| [readings_r1.py](readings_r1.py), [readings/results.json](readings/results.json) | fsf-r1: VE's own answer on every reading set that carries content |
| [measure_r1.py](measure_r1.py) | fsf-r1: each unit's status on Oct 1 and today, and the gaps by feature ([evidence](../../docs/usecases/safety-framework/fsf-r1/)) |
| [../../tests/test_safety_framework.py](../../tests/test_safety_framework.py) | the test: it fails on any mismatch with the key or any change in a result |

Run `python usecases/safety-framework/run.py` to recompute everything (a few minutes). The severity family
needs the Lean risk route, so run `lake build` in `lean/` first. `build_document.py` and `readings_r1.py` also
need the pinned Rust binary (`python3 tools/rust_build.py`).

## Re-measured on 2026-10-18 (fsf-r1)

The translation was re-checked on main at 93131f96 with the same rules. Since Oct 1, soft norms gained the rd-9
soft chain, readings gained rd-1 to rd-9, the Lean-first relocation merged, and so did qa-q2.

- **The same translation gives the same answers.** `run.py --check` and `build_document.py --check` pass
  unchanged on main: 257 of 262 answers agree with the key, and every unit keeps its Oct 1 status.
- **Seven reading sets now carry content, and VE decides each of them itself.** On Oct 1 every reading set had
  pending content, so VE's own readings query was UNKNOWN (PLAN 12, item 13). Content-bearing sets have since
  merged on the soft chain. A set whose readings are each one rule now gives each reading that rule as its
  content: RS2 on two units, RS4holistic, RS4within, RS4elicitation, RS6 and RS9.
  - On its own part document, Lean admits each set and finds a separating situation. It answers CONFLICT-FREE
    under every reading, with a checked model of the premises ([readings/results.json](readings/results.json)).
  - Each unit stays OPEN, because the text has two readings and a translation of someone else's text never picks
    one.
- **Eleven sets still have a pending reading.** Either the reading has no rule (RS3 F, RS4aim intent, RS7 M, RS8
  scope) or it has several (RS1 G, RS5 R). A candidate's content is one rule, so VE's verdict on the whole D1
  document stays UNKNOWN (route `pending`) until those readings can be written.
- **An independent check on a second model** ([fidelity-check.md](../../docs/usecases/safety-framework/fsf-r1/fidelity-check.md))
  found RS2 and RS6 faithful, with notes. It argues that "should" and "must" each have one reading here, against the
  soft-norms rule that every force word keeps both, and that RS9 = same drops "severe". These two questions are for
  the DRI; the translation is unchanged. Under R14 it classifies C1 and C3 as translation artefacts (below).

| Status | Oct 1 bytes | Oct 18 bytes |
|---|---|---|
| CHECKED | 4,595 (8.5%) | 4,595 (8.5%) |
| OPEN | 7,356 (13.5%) | 7,356 (13.5%) |
| LABELLED | 35,557 (65.4%) | 35,557 (65.4%) |
| UNFORMALISED | 6,865 (12.6%) | 6,865 (12.6%) |

### What each byte that is not CHECKED waits for

From [gaps.json](../../docs/usecases/safety-framework/fsf-r1/gaps.json). A unit counts under every blocker it has;
"alone" counts the units with no other blocker, so their bytes move when that one feature lands.

| Feature | Units | Bytes | Alone: units, bytes |
|---|---|---|---|
| judgment terms (16 open terms; "as appropriate", "where appropriate", "adequate") | 36 | 7,976 (OPEN 6,621, UNFORMALISED 1,355) | 23, 5,114 |
| modality ("may", "could": LABELLED hedged) | 18 | 3,276 | 18, 3,276 |
| process and deadline wording ("periodically", "this will inform", "the process will involve", an iterative process) | 11 | 2,212 | 11, 2,212 |
| readings with no rule or with several rules | 11 | 2,161 | 1, 95 |
| external references (RAND security levels, SAIF) | 7 | 1,978 | 7, 1,978 |
| attitudes: beliefs and expectations (LABELLED attributed) | 11 | 1,855 | 11, 1,855 |
| two readings kept, each decided by VE (fsf-r1; not a VE gap) | 7 | 1,436 | 4, 640 |
| causation (LABELLED causal) | 3 | 807 | 3, 807 |
| defeasible: "may be adjusted" | 2 | 551 | 2, 551 |
| attitudes: aims without force ("we strive", "we seek") | 2 | 486 | 2, 486 |
| addressee: a recommendation to the field | 2 | 283 | 2, 283 |
| no claim to check (layout, exposition, definitions, examples) | 165 | 29,619 | 165, 29,619 |

## Result: agreement with the answer key

**How these answers are computed today.** Lean elaborates the soft rules and replays every certificate. Python builds the rule formulas and evaluates them on each case, so a selection, a completed outcome or a CONFLICT is Python's answer. See [who computes the keyed answers](../../docs/usecases/keyed-answers.md) for the answer-by-answer table (work item `kb-10`).

VE agrees with the answer key on **260 of 262** items. The two others are key cells that PLAN section 12 (item 23)
corrects to NONE, and VE agrees with each correction.

| Family | What it asks | Agreement |
|---|---|---|
| A | what each level requires, for each of five activities | 160 / 160 |
| B | what each level requires whatever the activity | 40 / 40 |
| K | what the process triggers require | 18 / 18 |
| R | when the text deems a model's risk acceptable | 11 / 11 |
| C | conflicts | 4 / 6 (6 / 6 with the section-12 entries) |
| G | gaps | 9 / 9 |
| N | commitments that can never apply | 3 / 3 |
| S | severity and causation | 12 / 12 |
| D | dates | 3 / 3 |

### The two disagreements (fsf-fidelity-fix, 2026-11-12)

Before the fidelity fix VE disagreed on five items (A-L5/L6/L7-INT/DM, C1 and C-doc). The uc-audit of 2026-10-29
found 18 of 47 translation units unfaithful; the fix and every answer it moved are in
[REPORT.md](../../docs/usecases/safety-framework/fsf-fidelity-fix/REPORT.md).

1. **C3 and C-doc.** The key says SOME(G & rel & RS9 = same). Footnote 5 excludes RS9 = same: the deployment
   mitigations for the ML R&D CCLs "are different than those for the misuse CCLs". So the key's condition names no
   admissible choice, and the harness counts it as a disagreement rather than as a vacuous NONE. Both auditors
   found the right answer is NONE; PLAN section 12 records it (the key file is unchanged), and VE answers NONE.
2. **C1** now agrees with the key's NONE: F15 releases mitigations against insider misuse, and F16 recommends
   security measures for the weights, two acts (RS6 = same is excluded, R14).

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
| F4 (1.3.2) | A subsequent version is checked for substantial modification and for whether a further assessment is required; a further assessment may be required. | OPEN | two readings of what the "if" attaches to |
| F5 (1.3.2) | Material capability change assessments follow each completed post-training run. | CHECKED | |
| F6 (1.3.3) | Reaching an alert threshold for a CCL triggers a proximity assessment and a risk analysis. | OPEN | reaching a threshold is an open term |
| F7 (1.3.4) | A model at a TCL or CCL gets a residual risk assessment; at a CCL it is informed by a safety case. | OPEN | reaching a level is an open term |
| F8 (1.3.5) | A model at no level is deemed acceptable. | OPEN | reaching a level is an open term |
| F9 to F11 (1.3.5) | A model at a level is deemed acceptable when the stated mitigation and security conditions hold. | OPEN | two reading sets: sufficient or gate; scope or release (RS9 = same excluded) |
| F12, F13 (2.1.2, 3.1.2) | A deployment takes place only after the governance function finds its residual risk acceptable. | OPEN | two readings: within the section's process, or for every model |
| F14 (2.1.2, 3.1.2) | A material update to a safety case goes to the governance function for review. | CHECKED | |
| F15 (2.2) | Mitigations against insider misuse beyond the baseline controls are not required. | OPEN | reaching a level is an open term; one reading: insider misuse is not SL2+'s insider threat to the weights (RS6 = same excluded) |
| F16 (2.2, 3.2.2) | The recommended security level should be applied. | OPEN | two readings: a recommendation to the field only, or a "should" that also binds the developer, strictly or as a default |
| F17 (3.2.1) | At the stealth TCL, periodic misalignment assessments run and account for high-risk internal deployments, and safeguards are added when they are needed. | OPEN | "periodic" and reaching a level are open terms |
| F18 (5.1) | The framework is reviewed at least once a year. | CHECKED | |
| F18 (5.1) | It is reviewed more often when there are reasonable grounds. | OPEN | "reasonable grounds" is an open term |
| F19 (5.2) | Information is shared with government authorities when a CCL poses an unmitigated public-safety risk. | OPEN | two readings of "we aim to" |
| F20 (1.3.5 Note, Glossary, Note on ML R&D) | Mitigations are assessed holistically; residual risk is brought within acceptable levels; risk assessment allows for greater effort by others. | OPEN | each "should" or "must" is strict or a default |

No commitment is LABELLED. Several process sentences are UNFORMALISED, each with a reason: for example "we will
review the Framework periodically" names no deadline, and "the updated version ... will be reviewed by the
appropriate corporate governance bodies" concerns the order of events. [spans.json](spans.json) gives every unit
and its reason.

## Conflicts in the translation

**No conflict.** Until fsf-fidelity-fix the translation produced two conflicts (C1, C3), each only under a reading
that merges two acts the source words differently: RS9 = same (bullet 2's "residual risk of harm" with bullet 3's
"residual risk of *severe* harm") and RS6 = same (mitigations against "insider misuse" with Security Level 2+'s
measures against "insider threats"). An independent source check classified both as translation artefacts under R14
on 2026-10-18, and both uc-auditors found the readings excluded by the text on 2026-10-29. The DRI's decision of
2026-10-29 (uc-audit2 item 1) removed both readings and the rules only they selected; PLAN section 12 lists them
under "Excluded readings". The whole document (C-doc) is now CONFLICT-FREE at every choice.

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
readings, and 70 are silent under every choice. At exactly those choices, the outcome VE completes depends on the
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
- **16 reading sets.** On Oct 1, VE's own readings query returned UNKNOWN for norm readings, as the plan expected.
  Since fsf-r1, sets that carry content are separated and checked by VE itself (see "Re-measured on 2026-10-18").
  fsf-fidelity-fix removed the sets of RS6 and RS9 (one reading each is left), so 16 sets are placed: five carry
  content and eleven are pending. The ALL, SOME and NONE answers still come from the harness, which builds one
  document per choice of readings.
- **Order of events.** VE has no deadlines inside a process, so "prior to", "after" and "upon completion" are read
  as conditions that already hold.
- **External standards.** The RAND security levels, SAIF and the cited papers are pointers, not content.
- **One bridge, N1's own.** That a cyber or manipulation level is neither a CBRN nor an ML R&D level is not stated
  by the text. Since fsf-fidelity-fix it is no premise of the document: N1's certificate alone uses it, as an
  assumption of that item.

## Span accounting

All 54,373 bytes of the source are in exactly one unit of the document (290 units). These are the Oct 1 figures;
on Oct 18 every unit has the same status (the table under "Re-measured on 2026-10-18").

| Status | Bytes | Share |
|---|---|---|
| CHECKED | 4,595 | 8.5% |
| OPEN | 7,356 | 13.5% |
| LABELLED | 35,557 | 65.4% |
| UNFORMALISED | 6,865 | 12.6% |

The CHECKED share includes 1,108 bytes that the severity and date documents check. Within the main document alone,
3,487 bytes are CHECKED. The plan expected less than 10%. After fsf-fidelity-fix: CHECKED 4,043 (2,935 in the main
document), OPEN 7,954, LABELLED 35,511, UNFORMALISED 6,865; four units changed status (s131-four-domains CHECKED
to LABELLED; s321-internal LABELLED to OPEN; g-external and g-high-risk CHECKED to OPEN, as their premises are
about the open terms OT8 and OT7), see [coverage.json](coverage.json). Most of the text is exposition, examples,
definitions and page layout. The commitments are OPEN because their conditions use open terms. A unit's open terms
are derived from the predicates its rule or premise uses (`build_document.derived_meaning`), and the builder refuses
a document in which a CHECKED unit uses an open predicate.

## Metrics

| Metric | Result | Expected |
|---|---|---|
| M1 agreement with the key | 260/262; 262/262 with the PLAN 12 entries for C3 and C-doc | 262/262, every miss explained |
| M2 reading sets | 14 sets (13 in the main document, RS10 in the date document), placed on 18 units; at most 16 choices per item, and 64 for C-doc, the union over every act. Oct 1: VE's own readings query is UNKNOWN on every norm set. Oct 18: 7 of the 18 placed sets carry content, and VE answers CONFLICT-FREE with a model on each part document; the whole document stays UNKNOWN | as found |
| M3 CHECKED share | 7.4% (8.5% before fsf-fidelity-fix) | under 10% |
| M4 how each answer is backed | each per-choice answer rests on a case model that VE validated, a replayed certificate, or the Lean risk route | reported |
| M5 one-off identifiers | 0 | 0 |
| M6 untraced premises or rules | 0; one bridge, an assumption of N1 only | 0 |
| M7 items whose completed outcome depends on the default | 146, exactly at the silent cells (no conflicted cell since fsf-fidelity-fix) | the silent items |
| M8 evidence | every certificate is replayed; conflict witnesses satisfy every premise; the severity answers come from the Lean risk route | reported |
| M9 seeded mutants detected | 6/6 (m4 and m6 differ from the plan's expectation, PLAN section 12) | 6/6 |
| M10 cost | 85 cases, 87 documents, 301 case models, 1,732 prover calls, a few minutes | reported |

## Deviations

PLAN section 12 lists every deviation, with its reason. The main ones:

- Each act has its own regulated predicate, so that rules read as plain English.
- The conflict check runs against the premises, because VE's W1 check also counts impossible situations, such as a
  proposal that is both internal and external.
- Four Glossary sentences and one bridge became premises.
- After the results review: "For CCLs, we define alert thresholds" is no longer a premise, and narrowing N2 is
  withdrawn, so F16 under RS3 = Ds keeps both its strict and its default force.
