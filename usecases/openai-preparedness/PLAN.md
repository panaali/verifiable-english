# Use case: openai-preparedness (OpenAI Preparedness Framework, version 2)

> Status: **PLAN, draft 3, key FROZEN** (see KEY-FREEZE.md) (2026-10-28, branch `infra/usecase-safetyfw`; draft 1 reviewed by gpt-6-astra and Opus,
> `manage-agents/safetyfw-planreview-{astra,opus}.final.md`; dispositions in `manage-agents/reviews/safetyfw-plan-convergence-20261028.md`). The plan and its answer key (section 6)
> are written before any VE run. They get two plan reviews (gpt-6-astra xhigh and Opus xhigh) before the key is
> frozen; the freeze is recorded in [KEY-FREEZE.md](KEY-FREEZE.md) with a timestamp and the SHA-256 of section 6.
> After the freeze no answer-key cell changes; section 12 records every deviation.

This use case follows the method of [safety-framework](../safety-framework/PLAN.md) (Google DeepMind FSF 3.1) and
runs in **translation mode** ([VISION.md](../../VISION.md) 3, [document.md](../../docs/spec/document.md)): every
admissible reading is kept as a reading set; every vague term is a named open term with its decider; no default,
permission, threshold, ordering or causal link is added that the text does not state; every byte is accounted for.

It measures whether VE answers four questions about a published frontier-lab framework the same way as a key
derived from the text by hand (section 6), and how much of the text VE can check at all (section 10).

**Conflict of interest.** One plan reviewer (gpt-6-astra) is a model of the publisher. The other reviewer and the
author are not. Every key cell cites its source sentence, and `reference.py` recomputes families A, B, C and G
from sections 3 and 4 alone.

## 1. Source (pinned)

| Field | Value |
|---|---|
| Document | OpenAI, *Preparedness Framework*, **Version 2**, "Last updated: 15th April, 2025" (22 pages) |
| URL | `https://cdn.openai.com/pdf/18a02b5d-6b67-4cec-ab64-68cdfbddebcd/preparedness-framework-v2.pdf` |
| Retrieved | 2026-10-28, about 17:36 UTC, with `curl` |
| PDF SHA-256 | `fae6e4cc6f7212a010bb9348fc0cde1fe711b9cad426c6a99db97740ee52729b` (170,399 bytes). The same file was pinned as a candidate on 2026-10-01 ([safety-framework PLAN](../safety-framework/PLAN.md) 1). |
| Extracted text | [`source/extract_text.py`](source/extract_text.py) with `pypdf==6.19.0`: one line per page, whitespace collapsed. 67,418 bytes, 22 lines, SHA-256 `d2e3dd5b80e5bb86079911230358e0c2bb78f12435757959e14dae50e4d48d0f`. Two runs gave identical bytes. |
| Currency check | `openai.com` answers `curl` with HTTP 403 (as on 2026-10-01). The publisher's announcement page, "Our updated Preparedness Framework" (`https://openai.com/index/updating-our-preparedness-framework/`, publication date "April 15, 2025"), was read through its Internet Archive capture of 2026-10-23 11:54 UTC (`web.archive.org/web/20261023115435id_/…`), five days before retrieval: it links only this Preparedness Framework PDF (its other PDF link is a threat-intelligence report). A query of the Archive's index of `cdn.openai.com/pdf/` on 2026-10-28 found no other Preparedness Framework file. Neither check can prove that no later version exists. The PDF's own change log describes version 2. So version 2 is taken as current; that it is current is an observation leaf (LABELLED), not a VE result. |
| Licence | None stated: neither the text nor the PDF metadata names a licence or terms of reuse. |
| Stored copy | `~/code/manage-agents/pilots/openai-preparedness/source/` (the PDF, the extracted text and the archived announcement page). It is **not** committed here, because no licence is stated. This repository keeps the hashes, the extractor, short quotations and byte spans only. |

Quotations below are from the extracted text and each was checked to occur in it (curly quotes and apostrophes
normalised; pypdf keeps the PDF's hyphenation, e.g. "pro- vide"). "p. n" is the PDF page.

**Why this text.** It is the lead's request (2026-10-28), the third frontier-lab framework next to DeepMind's and
Anthropic's. It has the clearest if-then shape of the three: three Tracked Categories, each with a High and a
Critical capability threshold, and a "Risk-specific safeguard guidelines" column that names what each threshold
requires and for which activity ("before external deployment", "for large-scale internal deployment", "halt
further development"). It also defines "severe harm" with numbers, separates the Safety Advisory Group's
recommendations from OpenAI Leadership's decisions, and allows safeguards to be adjusted when another developer
releases a comparable system.

## 2. Scope

**In scope.** Every byte of the pinned text (section 10, M3). The questions concern:

- the six capability thresholds (three Tracked Categories × High, Critical) and the "no threshold reached" case;
- the four activities the text distinguishes: further development, internal deployment, large-scale internal
  deployment, external deployment;
- the Research Categories and their "Potential response" column;
- the process: covered deployments, Capabilities and Safeguards Reports, SAG decisions, marginal risk, disclosure,
  governance (Appendix B);
- the definition of severe harm, the quantified Critical self-improvement indicator, and the dates.

**Out of scope, with reasons.**

- **Whether any model has reached any threshold** (OT1, decided by the SAG); the cases stipulate it.
- **The content of Appendix C's illustrative safeguards** beyond C.3's required practices. C.1 and C.2 are
  "illustrative examples" that "should not be construed as a definitive checklist"; they are factors of open terms.
- **External references:** ISO 27001, SOC2, NIST SP 800-53, FedRAMP, the Model Spec, the Raising Concerns Policy,
  system cards, Meta's and Anthropic's frameworks.
- **Version 1 and the removed "low" and "medium" levels**, except as the change log states them.

## 3. Translation rules applied

### 3.1 Reading sets (written before the translation; none is collapsed)

| Id | Source unit | Readings | Why the text admits each |
|---|---|---|---|
| RS0 | every process statement about OpenAI's own conduct, in the future or present tense ("we will …", "Prior to deployment, every covered model undergoes", "We do not deploy models", "SAG will receive", "SAG members serve") | **commitment** / **prediction** | "Will" and the present tense are not deontic words. |
| N1 | narrowing of RS0 to **commitment**, clause by clause | cites 5 "so that the public, governments, and our industry peers can trust in our adherence to this policy" and 1 "to build confidence that we are meeting our commitments" | A clause that carries "expect", "aim", "strive", "may", "could", "where feasible" or "as needed" is not narrowed. Under N1 a commitment is strict. |
| RS1 | Table 1, column "Risk-specific safeguard guidelines": "Require security controls …", "Require safeguards against misuse …", "Until we have specified … halt further development", "Contribute towards …" | **strict** / **default** | Imperatives under a header that calls them guidelines. The default reading is the guideline reading; a third, no-norm reading is not admitted, because each cell is an imperative ("Require", "halt"); 2.2 restates one of them, the security controls, in force words ("appropriate security controls as they are developed"). |
| RS2 | whether reaching a Critical threshold in a category is reaching its High threshold | **nest** / **sep** | 4.2 "Systems that reach Critical capability also require safeguards …" ("also" presupposes the High rule applies); no sentence states the implication. |
| RS3 | the High deployment rule: 2.2 "required to have robust and effective safeguards that sufficiently minimize the associated risk of severe harm before they are deployed"; 4.2 "must have safeguards that sufficiently minimize … before they are deployed"; 1 "We do not deploy models that reach a High capability threshold until …" | **ext**: "deployed" is external deployment / **any**: every deployment, internal included | 4.4's heading "Increasing safeguards before internal use and further development" names internal use for Critical (RS18), which suggests the High rule did not cover it, and so supports ext. The word is unqualified, and Table 1 sets a High-level safeguard "for large-scale internal deployment", which supports any. |
| RS4 | Table 2, column "Potential response" | **N**: each response is a norm / **P**: a potential response, no norm | The header says "Potential"; 2.3 commits only to threat modelling, measurement and sharing in these areas. |
| RS4s | the guard of each Table 2 response | **scoped**: the response applies to a model with the row's research capability (plus any stated condition) / **unscoped**: only the stated condition, if any | Table 2 pairs each capability with its response; some responses state their own condition ("If a model has High or Critical capabilities in any of the Tracked Categories"). |
| RS5 | 4.3: "we could adjust accordingly the level of safeguards that we require in that capability area, but only if: …" | **within**: an adjusted level must still sufficiently minimize the risk (4.2 lists "The baseline risk from other deployments" among the SAG's factors) / **exception**: an exception to the High deployment rule, under the three stated conditions | "Could adjust" may change what counts as sufficient or override the requirement. |
| RS6 | Appendix B: OpenAI Leadership makes "deployment go/no-go decisions, informed by SAG's recommendations" | **req**: being informed by the SAG's recommendations is a requirement on the decision / **desc**: a description of the role, no norm | It sits in a list of responsibilities. |
| RS7 | Appendix B: "OpenAI Leadership can also make decisions without the SAG's participation" | **noinput**: without any SAG recommendation / **nodelib**: without the SAG taking part in the decision itself; its prior recommendation may still inform it | "Participation" and the explanation "does not have the ability to 'filibuster'" fit both. |
| N2 | the RS7 clause takes precedence over RS6 = req | cites "For the avoidance of doubt", which marks the clause as the one that decides the question it answers | Section 9 reports C2 without N2. |
| RS8 | footnote 6: "will ordinarily not require additional safety measures barring reason to believe a significant increase in capability has occurred" | **rel**: a default "need not" rule with the stated exception / **pred**: a prediction | "Ordinarily" marks a default; "will … not require" may report an expectation. |
| RS9 | every "should" and every "must" not restated by a strict "required" (e.g. 4.2 "The Safeguards Report should include …", Appendix B "The SAG Chair should also coordinate …", C.3 "access must be strictly limited", "Employees must authenticate") | **strict** / **default** | the [soft-norms.md](../../docs/spec/soft-norms.md) 2.2 rule. F2's "must have safeguards" (4.2, Appendix C) restates 2.2's strict "are required to have", so F2 is strict. |
| RS10 | Appendix B: "at least once a year" | **publication**: counted from 2025-04-15 / **unstated** | No start point is given. |
| RS11 | Appendix B: OpenAI Leadership is responsible for "Making all final decisions" | **final**: no other body may change them / **process**: final within the operational process the appendix sets up | The same appendix says "Where necessary, the Board may reverse a decision and/or mandate a revised course of action." |
| RS12 | 2.1 "We treat a frontier capability as a Tracked Category if the capability creates a risk that meets five criteria" | **suff** / **iff** | "If" states a sufficient condition; 2.3 "Research Categories are capabilities that, while they do not meet the above criteria …" suggests a complete one. |
| RS13 | 5.1: "Employees may also request and receive a summary of the testing results and SAG recommendation" | **permission** / **might** | [norms.md](../../docs/spec/norms.md) 2 |
| RS14 | Appendix B: "SAG members serve for one year terms" | **appointment**: counted from the appointment / **unstated** | No start point is given (as RS10). |
| RS15 | the change log's own undertakings (item 4 "Going forward we will handle risks related to persuasion outside the Preparedness Framework, including via our Model Spec and policy prohibitions"; item 5 "we commit to further developing the associated threat models") | **explanation**: they describe the version / **rule**: commitments of version 2 | They are written as commitments inside a change log. |
| RS16 | 3.3: "Determine that the capability threshold has been crossed, and therefore recommend implementing and assessing corresponding safeguards, if they have not already been implemented and assessed" | **coupled**: a determination that a threshold is crossed brings the recommendation with it / **option**: one of the next steps the SAG's decision "can include" | "These can include" introduces the list; "and therefore" couples the two acts inside the item. |
| RS17 | Appendix B: "Where necessary, the Board may reverse a decision and/or mandate a revised course of action." | **bperm**: a permission / **bmight**: "may" in the sense of "might" | [norms.md](../../docs/spec/norms.md) 2 |
| RS18 | the scope of 4.4 (Critical): heading "4.4 Increasing safeguards before internal use and further development"; body "Such models require additional safeguards (safety and security controls) during development, regardless of whether or when they are externally deployed" | **inuse**: the Critical rule also covers internal use (the heading) / **devonly**: development only (the body) | The heading and the body differ. |

### 3.2 Open terms (each with its decider; none gets invented criteria)

`we` means OpenAI as the text uses the word. Factors come from "e.g.", "such as", "including", "for example" and the
illustrative Appendix C, and give no premise.

| Id | Term | Decided by | Factors or definitions stated |
|---|---|---|---|
| OT1 | the model has reached threshold L (category, High or Critical) | `SAG` (3.3 "The SAG reviews the Capabilities Report and decides on next steps"); OpenAI Leadership makes the final decisions on deployment, not on the threshold | indicative thresholds of Scalable Evaluations, deep dives, "holistic judgment based on the totality of available evidence" |
| OT2 | the safeguards "sufficiently minimize the associated risk of severe harm" | `SAG` (4.2 "SAG is responsible for assessing whether the safeguards … sufficiently minimize the risk of severe harm"). OpenAI Leadership's "accepting any residual risks" is a separate act and does not decide OT2. | 4.2's four factors |
| OT3 | security controls "meeting High standard (Appendix C.3)" | `unstated` | C.3's practices, which "We will require … for High capability models" (each itself vague: "regularly", "Comprehensive") |
| OT4 | safeguards against misuse "meeting High standard (Appendix C.1)" | `unstated` (4.2 gives the SAG OT2 only) | C.1, illustrative |
| OT5 | safeguards "meeting High standard against misalignment (Appendix C.2)" | `unstated` | C.2, illustrative |
| OT6 | "a Critical standard" for safeguards and security controls; whether it is "specified" | `unstated` | none (4.4: "we expect to further update this Preparedness Framework before reaching such a level") |
| OT7 | a covered deployment ("a plausible chance of reaching a capability threshold whose corresponding risks are not addressed by an existing Safeguards Report") | `SAG` "In cases of ambiguity" | 3.2's four examples |
| OT8 | "large-scale internal deployment" | `unstated` | none |
| OT9 | a covered system "appears likely to cross a capability threshold" | `we` | none |
| OT10 | a model "forecasted to reach Critical capability" | `we` | "our forecasts and threat models" |
| OT11 | "reasonable evidence that our safeguards are not working as expected" | `we` | none |
| OT12 | 4.3: "rigorously confirm"; "does not meaningfully increase the overall risk"; "comparable safeguards"; "more protective" | `we` | none |
| OT13 | "major deployments" (5.2) | `unstated` | none |
| OT14 | a deployment "warrants deeper testing"; third-party testing "available and feasible", "high quality" | `we` ("If we deem") | "based on results of Capabilities Report" |
| OT15 | "severe harm" | definition (footnote 1) | "the death or grave injury of thousands of people or hundreds of billions of dollars of economic damage" (quantified, family S) |
| OT16 | the threshold descriptions ("meaningful counterfactual assistance", "novice", "reasonably hardened targets", "highly performant mid-career research engineer assistant", "superhuman research-scientist agent") | `SAG` | Table 1's examples |
| OT17 | "sustainably for several months" (AIS-C lagging indicator) | `unstated` | none |
| OT18 | "a risk of severe harm rapidly develops" | `unstated` | "e.g., there is a change in our understanding of model safety that requires urgent response" |
| OT19 | "appropriate and proportional corrective action" | `unstated` | none |
| OT20 | "reason to believe a significant increase in capability has occurred" (footnote 6) | `we` | none |
| OT21 | the fast track's "immediate reaction as needed" | `unstated` | none |

### 3.3 What the translation must not add

- **No completion default is trusted.** Every query runs under both defaults; only selection-based verdicts are
  scored. A verdict that depends on the default is a gap.
- **No permission the text does not grant.** 4.3's "could adjust" is limited by its three conditions; "SAG can find
  …" and "These can include" list options and give no permission beyond them.
- **No order between High and Critical by severity.** The text distinguishes them by kind ("significantly increase
  existing risk vectors" against "a qualitatively new threat vector … with no ready precedent"), not by a stated
  severity order. RS2 is the only link between them.
- **No closure of examples; stated instances are premises.** "e.g.", "such as", "for example", "Examples of such …
  are" never close a class. A listed instance of a stated class is a premise (3.2's examples are covered deployments).
  Factors of an open term (what is considered in deciding it) give no premise. C.1 and C.2 are "illustrative
  examples" of safeguards that "could" be used: factors, not instances of a required standard. Only C.3's "We will
  require the following practices" states requirements. The same rule is used in the anthropic-rsp plan.
- **No causal link stated as certain.** "could lead to", "could cause", "may upset", "could compromise" become
  `causal` units or `might` cells.

## 4. The text as rules (the inventory the key and the translation both use)

### 4.1 Named levels (Table 1)

| Id | Level | Category | Associated risk, short | Safeguard guidelines (RS1) |
|---|---|---|---|---|
| BIO-H | [High] | Biological and Chemical | "Significantly increased likelihood and frequency of biological or chemical terror events by non-state actors" | SEC (C.3); MIS (C.1) "before external deployment" |
| BIO-C | [Critical] | Biological and Chemical | "could cause millions of deaths" | HALT "Until we have specified safeguards and security controls that would meet a Critical standard, halt further development"; CONTRIB "Contribute towards improved public policy and pandemic preparedness" |
| CYB-H | [High] | Cybersecurity | "significantly automating and scaling the volume of existing cyberattacks" | SEC; MIS "for external deployment"; ALN (C.2) "for large-scale internal deployment"; CONTRIB "Contribute towards improved cyberdefense policies and tools for cyberdefense" |
| CYB-C | [Critical] | Cybersecurity | "could lead to catastrophe" | HALT |
| AIS-H | [High] | AI Self-improvement | "AI self-improvement may be beginning to accelerate" | SEC |
| AIS-C | [Critical] | AI Self-improvement | "risks to maintaining human control of the AI system itself" | HALT |

L0 is "no threshold reached". **Closure stated by the text:** "We currently focus this work on three areas of
frontier capability, which we call Tracked Categories" (p. 2) lists exactly three; Persuasion is outside the
Framework ("Persuasion category risks do not fit the criteria for inclusion"). Footnote 5: biological evaluations
"will be used as indicators for High and Critical capabilities for the category".

### 4.2 Commitments

| Id | Source | Content (reading sets) |
|---|---|---|
| F1 | Table 1 | the guideline bullets of 4.1, per level and activity (RS1, RS2) |
| F2 | 1, 2.2, 4.2, App. C | **High deployment rule**: a covered system that reaches High must have safeguards that sufficiently minimize the associated risk (OT2) before it is deployed (RS3; OT2 is the SAG's) |
| F3 | 1, 2.2, 4.2, 4.4 | **Critical development rule**: a system that reaches Critical requires such safeguards during development, irrespective of deployment plans; also for models "forecasted to reach" Critical (4.4); its scope beyond development is RS18 |
| F4 | C.3 | "We will require the following practices for High capability models" (the security practices; OT3) |
| F5 | 3.2 | the covered deployments (OT7); the SAG decides ambiguity; a development checkpoint "If justified by our forecasts" |
| F6 | footnote 6 | distilled, fine-tuned or quantized from a model determined not High: "ordinarily not require additional safety measures barring reason to believe a significant increase" (RS8, OT20) |
| F7 | 3.3 | every covered model undergoes Scalable Evaluations before deployment; a Capabilities Report goes to the SAG; the SAG "decides on next steps", which "can include" three options |
| F8 | 4 | if a covered system appears likely to cross a threshold (OT9), start work on safeguards before a formal determination |
| F9 | 4.1, 4.2 | safeguard selection (three steps); a Safeguards Report that "should include" four items (RS9); the SAG assesses sufficiency on four factors; three decision points; recommendations go to OpenAI Leadership |
| F10 | 4.2 | on reasonable evidence that safeguards are not working (OT11): validate the information and review sufficiency |
| F11 | 4.3 | the marginal-risk adjustment, only if three conditions hold (RS5, OT12) |
| F12 | Table 2 | Research Category responses (RS4): LRA "require a 'misalignment' safeguards report" if High or Critical in a Tracked Category; Sandbagging; ARA "Convert … to a Tracked Category"; Undermining Safeguards "require the Safeguards case to be robust"; Nuclear and Radiological "Heighten safeguards … in consultation with appropriate US government actors" |
| F13 | 2.3 | periodic review of each Research Category; "SAG will receive the results" |
| F14 | 5.1 | documentation of SAG reports and decisions; employees "may also request and receive a summary"; noncompliance tracked and investigated, corrective action if substantiated (OT19) |
| F15 | 5.2 | public disclosure for major deployments (OT13): scope of testing, evaluations, reasoning; safeguards information "if the model is beyond a High threshold"; third-party evaluation and stress testing when deemed warranted and available (OT14); independent expert opinion at the SAG's option |
| F16 | App. B | SAG duties; Leadership's final decisions "informed by SAG's recommendations" (RS6); Leadership "can also make decisions without the SAG's participation" (RS7); SSC visibility; the Board "may reverse a decision" (RS17); one-year SAG terms; review "at least once a year" (RS10); fast-track, and the Chair "should also coordinate" (RS9) |
| F17 | 2.1 | Tracked Category criteria (RS12) |

Everything else (the motivation of 1.1, beliefs, expectations, the change log's explanations, the persuasion and
nuclear rationale, examples, Appendix C's tables, page furniture) is accounted for as LABELLED or UNFORMALISED
units, with reasons.

## 5. Questions and cases (exact list)

- "What does each level require": families A (per level and activity) and B (per level), with K (process
  triggers) and T (the quantified Critical self-improvement indicator).
- "Do any two commitments conflict": family C.
- "Which levels or situations no rule covers": family G, plus the NONE cells of A and B.
- "Which commitments can never apply": family N.
- Families S and D cover severity, causation and dates.

**Verdicts, requirements, REL and CONFLICT** are as in [safety-framework PLAN](../safety-framework/PLAN.md) 5. A
requirement that holds only as a default rule is marked "soft".

**Case facts.** The model has reached the levels named (L0: none), and under RS2 = nest also the High level of the
same category as each Critical level named; no others; the proposal is of the
named activity; the deployment is a covered deployment (OT7) and, for family B, a major deployment (OT13); no
Critical standard has been specified (OT6 false); every other open term is unset unless the case says so.

| Family | Cases | Scored items |
|---|---|---|
| A: per level and activity | A-*L*-*X* for *L* ∈ {L0, BIO-H, BIO-C, CYB-H, CYB-C, AIS-H, AIS-C}, *X* ∈ {DEV, INT, LINT, EXT}: 28 cases | 5 atoms each (SEC, MIS, ALN, SUF, HALT): 140 |
| B: per level | B-*L*: 7 cases | 6 atoms each (CAPREP, SAFEREP, MREP, DISC, PUBRES, CONTRIB): 42 |
| K: process triggers | K1 … K20 | 22 |
| T: the AIS-C lagging indicator | T1, T2 | 2 |
| C: conflicts | C1 … C6, C-doc | 7 |
| G: gaps | G1 … G10 | 10 |
| N: never applies | N1 … N4 | 4 |
| S: severity and causation | S1 … S8 | 8 |
| D: dates | D1 … D4 | 4 |
| **Total** | | **239** |

## 6. Answer key (written before any VE run)

Notation: strict, default: RS1; nest, sep: RS2; ext, any: RS3; N, P: RS4; within, exception: RS5; req, desc: RS6;
noinput, nodelib: RS7; rel, pred: RS8; publication, unstated: RS10; final, process: RS11; suff, iff: RS12; bperm, bmight: RS17; inuse, devonly: RS18;
permission, might: RS13; appointment: RS14; explanation, rule: RS15; coupled, option: RS16; scoped, unscoped: RS4s. "soft" marks
an item that holds only as a default rule under RS1 = default (or RS9 = default).

Atoms: **SEC** security controls meeting the High standard (F1, F4); **MIS** misuse safeguards meeting the High
standard (F1); **ALN** misalignment safeguards meeting the High standard (F1); **SUF** safeguards that sufficiently
minimize the associated risk (F2, F3); **HALT** further development forbidden (F1, until a Critical standard is
specified).

### 6.1 Family A (140 items)

| Level | SEC (DEV, INT, LINT, EXT) | MIS | ALN | SUF | HALT | Justification |
|---|---|---|---|---|---|---|
| L0 | NONE ×4 | NONE ×4 | NONE ×4 | NONE ×4 | NONE ×4 | no family A atom names a model at no threshold (C.3's "For all models … access must be strictly limited" is not the High-standard bundle; see G9) |
| BIO-H | ALL ×4 | EXT: ALL, soft; else NONE | NONE ×4 | EXT: ALL; INT, LINT: SOME(any); DEV: NONE | NONE ×4 | F1 SEC is also F4's strict C.3 commitment, for the model whatever the activity (2.2 "appropriate security controls as they are developed"). MIS "before external deployment". F2 under RS3. |
| BIO-C | SOME(nest) ×4 | EXT: SOME(nest), soft; else NONE | NONE ×4 | DEV: ALL; EXT: SOME(nest); INT, LINT: SOME(inuse ∨ (nest ∧ any)) | DEV: ALL, soft; else NONE | F3's body is limited to development ("during development"; "irrespective of deployment plans" qualifies it); under RS18 = inuse its heading adds internal use. External deployment reaches SUF only through F2, which needs High (nest); internal deployment through F2 also needs RS3 = any. HALT names further development only. |
| CYB-H | ALL ×4 | EXT: ALL, soft; else NONE | LINT: ALL, soft; else NONE | as BIO-H | NONE ×4 | MIS "for external deployment"; ALN "for large-scale internal deployment". |
| CYB-C | SOME(nest) ×4 | EXT: SOME(nest), soft; else NONE | LINT: SOME(nest), soft; else NONE | as BIO-C | DEV: ALL, soft; else NONE | as BIO-C |
| AIS-H | ALL ×4 | NONE ×4 | NONE ×4 | as BIO-H | NONE ×4 | the row lists security controls only |
| AIS-C | SOME(nest) ×4 | NONE ×4 | NONE ×4 | as BIO-C | DEV: ALL, soft; else NONE | as BIO-C |

Totals: ALL 24, SOME 30, NONE 86. Under RS0 "prediction" (without N1), F4 and the "we will" sentences give nothing;
F1, F2 and F3 ("require", "must", "are required to") still hold. Reported, not scored.

### 6.2 Family B (42 items)

| Level | CAPREP (F7) | SAFEREP (F9) | MREP (F12, LRA) | DISC (F15 safeguards) | PUBRES (F15 results) | CONTRIB (F1) |
|---|---|---|---|---|---|---|
| L0 | ALL | NONE | NONE | NONE | ALL | NONE |
| BIO-H | ALL | ALL | SOME(N ∧ unscoped) | ALL | ALL | NONE |
| BIO-C | ALL | ALL | SOME(N ∧ unscoped) | SOME(nest) | ALL | ALL, soft |
| CYB-H | ALL | ALL | SOME(N ∧ unscoped) | ALL | ALL | ALL, soft |
| CYB-C | ALL | ALL | SOME(N ∧ unscoped) | SOME(nest) | ALL | SOME(nest), soft |
| AIS-H | ALL | ALL | SOME(N ∧ unscoped) | ALL | ALL | NONE |
| AIS-C | ALL | ALL | SOME(N ∧ unscoped) | SOME(nest) | ALL | NONE |

Justification. CAPREP: "Prior to deployment, every covered model undergoes the suite of Scalable Evaluations" and
the results go into a Capabilities Report submitted to the SAG. SAFEREP: section 4 concerns "covered systems that
reach a capability threshold"; Critical is a capability threshold, so no RS2 choice is needed. MREP: the LRA row
reaches a model with "High or Critical capabilities in any of the Tracked Categories", under N; under scoped it
also needs the Long-range Autonomy capability, which family B leaves unset. DISC: "if the
model is beyond a High threshold". PUBRES: for major deployments, whatever the level. CONTRIB: BIO-C's and CYB-H's
rows; CYB-C through CYB-H under nest. Totals: ALL 25, SOME 10, NONE 7.

### 6.3 Family K (22 items)

| Case | Situation | Item | Key | Justification |
|---|---|---|---|---|
| K1 | a covered system appears likely to cross a threshold (OT9); no formal determination | starting work on safeguards required | ALL | F8 |
| K2 | the SAG determines that a threshold has been crossed; corresponding safeguards have not already been implemented and assessed | the SAG required to recommend implementing and assessing them | SOME(coupled) | F7, RS16 |
| K3 | a model distilled from one determined not High; OT20 false | additional safety measures required | NONE | F6: under rel a "need not" selects (REL); under pred no rule |
| K4 | the same model with an unexpectedly significant increase in capability (OT20 true) | a Capabilities Report required | ALL | 3.2 lists "distilled models with unexpectedly significant increases in capability" as a covered deployment (a stated instance, 3.3); F7 |
| K5 | reasonable evidence that safeguards are not working (OT11) | validating the information and reviewing sufficiency required | ALL | F10 |
| K6a | another developer released a High system without comparable safeguards (OT12 confirmed); OpenAI adjusts its safeguards | keeping its safeguards more protective than the other developer's required | ALL | F11 "but only if … we keep our safeguards at a level more protective" |
| K6b | the same | publicly acknowledging the adjustment required | ALL | F11 |
| K6c | the same | sharing information to validate the claim required | ALL | F11 |
| K7 | a model forecasted to reach Critical (OT10); not reached | safeguards during development required | ALL | F3 (4.4) |
| K8 | the same | halting further development required | NONE | HALT is stated for the Critical level, not for a forecast |
| K9 | a model with High capability in a Tracked Category and a discovered capability to undermine safeguards | a safeguards case robust to it required | SOME(N) | F12 |
| K10 | a model shows a sandbagging ability or propensity | an elicitation approach that overcomes it, or a conservative upper bound, required | SOME(N) | F12 |
| K11 | it is ambiguous whether a model is covered | the SAG's final determination required | ALL | F5 |
| K12 | any time | reviewing the Framework at least once a year required | ALL | F16 (deadline: D2) |
| K13 | a risk of severe harm rapidly develops (OT18), a fast track is requested, and immediate reaction is needed (OT21) | the SAG Chair coordinating with OpenAI Leadership required | ALL, soft under RS9 = default | F16 "should also coordinate … as needed" |
| K14 | a deployment warrants deeper testing (OT14), third parties available and feasible | working with third parties to evaluate the model required | ALL | F15 |
| K15 | a Research Category review is completed | the SAG receiving its results required | ALL | F13 |
| K16 | an employee requests a summary of testing results; no highly sensitive information is involved | the employee permitted to request and receive it | SOME(permission) | F14, RS13; a duty on OpenAI to provide it is not stated |
| K17 | a noncompliance report is substantiated | corrective action required | ALL | F14 |
| K18 | a model is found to have the Nuclear and Radiological capability | heightening safeguards in consultation with US government actors required | SOME(N) | F12 |
| K19 | a model is found to have the Autonomous Replication and Adaptation capability | converting the category to a Tracked Category required | SOME(N) | F12 |
| K20 | a Safeguards Report is compiled | including a residual-risk assessment required | ALL, soft under RS9 = default | F9 "should include" |

### 6.4 Family T: the AIS-C lagging indicator (2 items)

| Case | Situation | Item | Key | Justification |
|---|---|---|---|---|
| T1 | a generational improvement in 4 weeks; the equivalent 2024 progress took 20 weeks | "in 1/5th the wall-clock time of equivalent progress in 2024" holds | ALL | 4 ≤ 20/5 ("in 1/5th the time" read as at most a fifth, the plain reading of a speed-up bound) |
| T2 | 5 weeks against 20 | the same | NONE | 5 > 4 |

Whether the threshold is reached remains OT1 (the SAG's holistic judgment) and OT17 ("sustainably for several
months"); T1 and T2 score only the quantity.

### 6.5 Family C: conflicts (7 items)

| Case | Rules | Key | Witness or reason |
|---|---|---|---|
| C1 | F11 (adjustment) against F2 (High deployment rule) | NONE | Under within, an adjusted level must still sufficiently minimize the risk. Under exception, F11 is F2's exception under its three conditions. Mutant m1 removes the precedence. |
| C2 | F16 "informed by SAG's recommendations" against F16 "without the SAG's participation" | NONE | Under N2 the "avoidance of doubt" clause takes precedence, so a decision made with no SAG recommendation is its stated case, not a conflict. Without N2, SOME(req ∧ noinput) (section 9). Mutant m6 removes the precedence. |
| C3 | F1 HALT against F3 (safeguards during development) | NONE | both restrict development |
| C4 | F6 against F5 bullet 4 | NONE | F6's own exception ("barring reason to believe …") is F5's case |
| C5 | AIS-H's guideline (security controls only) against F2 | NONE | the rules add up; none releases what another requires |
| C6 | Appendix B, Leadership's "all final decisions" against "the Board may reverse a decision" | SOME(final ∧ bperm) | A deployment decision by Leadership that the Board reverses: under final, no body may change it; under bperm the Board sentence permits the change. Under process, Leadership's decisions are final only within the operational process; under bmight the Board sentence is no norm. |
| C-doc | the whole document, per choice | SOME(final ∧ bperm) | exactly C6 |

### 6.6 Family G: gaps (10 items)

| Case | Situation | Key | Justification |
|---|---|---|---|
| G1 | BIO-C; a Critical standard specified but not implemented; further development proposed | silent on proceeding: ALL (F3 requires safeguards; no rule forbids development) | HALT ends when a standard is "specified" |
| G2 | external deployment of a Critical model with no Critical standard | a Critical-specific deployment rule: silent: ALL (F2 reaches it only under nest) | HALT names further development only; F3 reaches development and, under RS18 = inuse, internal use, never external deployment |
| G3 | CYB-H, external deployment | misalignment safeguards: silent: ALL (F2 still applies) | ALN is "for large-scale internal deployment" |
| G4 | AIS-H, external deployment | misuse and misalignment safeguards: silent: ALL (F2 still applies) | the row lists security controls only |
| G5 | a nuclear or radiological capability comparable to High | no threshold rule: ALL; only K18 under N | Research Category |
| G6 | a persuasion capability | no rule: SOME(explanation) | "Persuasion category risks do not fit the criteria for inclusion"; under RS15 = rule the change log's item 4 commits to handling them outside the Framework |
| G7 | a chemical-only capability, no biological capability | an evaluation indicator of High or Critical: silent: ALL | footnote 5: biological evaluations "will be used as indicators"; the footnote's "We will build safeguards against both biological and chemical threats" states safeguards, not an indicator |
| G8 | BIO-H reached during development, before any deployment | SUF required during development: NONE (only SEC) | F2 is a deployment rule; F3 is Critical's |
| G9 | a model at no threshold in a deployment that is not covered (OT7 false) | covered only by C.3's all-model access requirement: ALL | "For all models, especially those presenting High capabilities, access must be strictly limited" (RS9) |
| G10 | the SAG finds the safeguards insufficient and Leadership deploys anyway (BIO-H, EXT) | deployment forbidden: ALL | F2 with OT2 decided by the SAG (OT2); Leadership's acceptance of residual risk does not make the safeguards sufficient |

### 6.7 Family N: never applies (4 items)

| Case | Question | Key | Justification |
|---|---|---|---|
| N1 | As of publication, can HALT or F3's "reached" branch apply to an existing model? | never: ALL | "We do not currently possess any models that have Critical levels of capability" (a dated fact); F3's "forecasted to reach" branch is not covered by it |
| N2 | Can any Framework threshold rule require a persuasion-specific safeguard? | never: ALL | 4.1 closure; persuasion is outside the Framework (RS15 = rule commits only to handling it outside) |
| N3 | Is any commitment F1 to F17 dead? | no: NONE dead; a witness model for each | every guard is satisfiable |
| N4 | Can a "low" or "medium" level trigger any rule? | never: ALL | "we are removing terms 'low' and 'medium' from the Framework" |

### 6.8 Family S: severity and causation (8 items)

| Case | Question | Key | Justification |
|---|---|---|---|
| S1 | 5,000 deaths: severe harm? | ALL | "thousands of people" |
| S2 | 500 deaths and no economic damage: severe harm? | NONE | footnote 1 is a definition ("we mean"); 500 is not thousands |
| S3 | $300 billion of economic damage: severe harm? | ALL | "hundreds of billions of dollars" |
| S4 | $50 billion: severe harm? | NONE | below hundreds of billions |
| S5 | BIO-C's associated risk ("could cause millions of deaths"): of severe harm? | ALL | millions exceed thousands |
| S6 | Is Critical ranked more severe than High? | NONE (no stated order) | 3.3 |
| S7 | Might deploying a BIO-H model without safeguards make biological terror events more likely? | ALL (a stated `might` cell) | Table 1 associated risk |
| S8 | Does it *lead to* such events? | NONE | only increased likelihood is stated |

### 6.9 Family D: dates (4 items)

| Case | Question | Key | Justification |
|---|---|---|---|
| D1 | Was version 2 (2025-04-15) last updated before the retrieval date 2026-10-28? | ALL | p. 1 |
| D2 | Was a review due no later than 2026-04-15? | SOME(publication) | RS10; "a year" from 2025-04-15 is 365 days with no 29 February between, so 2026-04-15. A review need not produce a new version ("review and potentially update"), so the absence of version 3 is not a violation. |
| D3 | A SAG member appointed on 2026-01-05: does the term end no later than 2027-01-05? | SOME(appointment) | RS14; "one year terms" (365 days, a bridge) |
| D4 | Is BIO-H's baseline year (2021) earlier than AIS-H's (2024)? | ALL | Table 1 |

**Independent check of the key.** `reference.py` (stdlib only, no `ve` import) is written from sections 3 and 4
alone and recomputes families A, B, C and G; a disagreement is resolved in a separate commit that says why.

## 7. Planned VE translation

**Documents.** As safety-framework 7 (unless a probe shows main composes the profiles; record either way):

| Doc | Environment profiles | Carries | Questions |
|---|---|---|---|
| D1 | `norms@0`, `soft-norms@0` (probe P1; `judgments@0` only if probe P8 admits it) | F1 to F17, level and activity vocabulary, open terms, reading sets | A, B, K, C, G, N |
| D2 | `norms@0`, `alternatives@0`, `risk@0` | severe harm, the stated `might` cells, `causal` units | S5 to S8 |
| D3 | `ve-units@1` (`documents@1`, `order@0`, `relational-fol@0`, `time@0`) | the severe-harm quantities (S1 to S4), the 1/5 ratio (T), the dates (D) | S1 to S4, T, D |

**Shared structure (the CHECKED bar).** Rules quantify over `level`, `category`, `proposal`, `requirement`; levels
are constants with the source's own labels (`biological_and_chemical_high`); a level's category and grade are
facts (`in_category`, `high`, `critical`); one Table 1 bullet gives one rule; no identifier packs a level, number or
condition into its name (probe P7).

**Feature map** (feature families of `reviews/feature-plan-20261018.md` in manage-agents: JT judgments, DF
defaults, SC scope, QT quantities, ET time, AP acts, WG weighing, AT attitudes).

| Part | VE feature | Family |
|---|---|---|
| F1 to F17 rule blocks; exceptions (F11 under RS5 = exception, F6's own exception) | `norms@0` | merged |
| RS1 default, RS9, RS8 (footnote 6, "ordinarily") | `soft-norms@0`, defaults | DF |
| OT1 to OT21 | W2 open terms; `judgments@0` if P8 admits it | JT |
| RS2 nesting, "any of the Tracked Categories", "every covered model" | quantifier scope | SC |
| footnote 1's thousands and hundreds of billions, "1/5th", "4 weeks", "several months" | W6a; `ve-units@1` | QT |
| "before external deployment", "during development", "Until we have specified", "at least once a year", "Prior to deployment" | event order and deadlines | ET |
| "halt further development", "Contribute towards improved public policy", "share information to validate this claim" | act phrases | AP |
| 4.3 "more protective than the other AI developer"; 4.2's four factors; "benefits … while addressing their risks" | comparison and weighing | WG |
| "We believe", "we expect", "we aim", "our analysis suggests" | attitudes | AT |

## 8. What is expected to stay OPEN

- **O1: every open term OT1 to OT21.** In particular whether a level is reached, and whether safeguards
  sufficiently minimize the risk.
- **O2: norm reading sets**, answered per choice by the harness; VE decides only sets whose readings are each one
  rule.
- **O3: causal and degree language** ("meaningful counterfactual assistance", "significantly increase", "could
  lead to").
- **O4: beliefs, expectations and rationale** (1.1, 2.3's change notes, the nuclear and persuasion paragraphs).
- **O5: Appendix C's illustrative tables**, as factors.
- **O6: external standards** (ISO 27001, SOC2, NIST, FedRAMP, the Model Spec).
- **O7: event order** ("before", "during development", "Until … specified").
- **O8: feature combination**: D2 and D3 do not share an environment with D1.
- **O9: "a year"** is a 365-day bridge.
- **O10: who "we" is**: OpenAI, the SAG, OpenAI Leadership and the SSC are kept apart; "we" is never identified with
  one of them.

Expected CHECKED share: **under 10%**, probably under 5%: the definitions' quantities, the dates, the ratio and
the few rules whose guards carry no open term.

## 9. Run protocol (implementation round)

**Stage 0 probes.** P1 to P7 as [anthropic-rsp PLAN](../anthropic-rsp/PLAN.md) 9, over this document (P5: the
partition totals 67,418 bytes); P8: D1 with `judgments@0` added (record admitted or refused). **Per case** as
safety-framework 9. Report, unscored, what changes without N1 and without N2.

## 10. Metrics to report

| # | Metric | Expected |
|---|---|---|
| M1 | key agreement per family (A 140, B 42, K 22, T 2, C 7, G 10, N 4, S 8, D 4) | 239/239; every miss explained in section 12 |
| M2 | reading sets: count, choices per case, SOME verdicts, VE's own readings verdicts | RS1 to RS18 and RS4s plus N1, N2; at most 2⁴ = 16 choices per family A case (RS1, RS2, RS3, RS18) |
| M3 | span accounting: `bytes_by_status` (CHECKED, OPEN, LABELLED, UNFORMALISED) and `bytes_by_kind`, totalling 67,418; reasons; residual; for each unit that is not CHECKED, the feature family it waits for (section 7) | CHECKED under 10% |
| M4 | structure-conditional answers per family | reported |
| M5 | CHECKED-bar lint (P7) | 0 |
| M6 | invention audit | 0 untraced |
| M7 | default sensitivity | exactly the silent items |
| M8 | evidence: certificates replayed, witnesses validated, UNKNOWNs named | reported |
| M9 | seeded mutants (section 11) detected | 6/6 |
| M10 | cost | reported |

## 11. Seeded mutants (each must change exactly the named results)

| Id | Mutation | Expected change |
|---|---|---|
| m1 | remove F11's precedence over F2 (keep RS5 = exception) | C1 becomes SOME(exception); C-doc adds it |
| m2 | add "a model at a High level may be deployed externally once its misuse safeguards meet the High standard" (an invented permission, 3.3) | C-doc becomes ALL: a witness (external deployment at BIO-H, CYB-H or AIS-H, and at a Critical level under nest, with OT4 true, OT2 false and OT12 false) conflicts with the strict F2 under every choice; M6 flags it |
| m3 | delete "for large-scale internal deployment" from CYB-H's ALN bullet | A-CYB-H ALN becomes ALL, soft, ×4; A-CYB-C ALN at DEV, INT and EXT becomes SOME(nest), soft; G3 changes |
| m4 | change "1/5th" to "1/4th" | T2 becomes ALL |
| m5 | change "thousands of people" to "millions of people" | S1 becomes NONE; S5 stays ALL |
| m6 | remove the precedence N2 gives the "avoidance of doubt" clause | C2 becomes SOME(req ∧ noinput); C-doc adds it |

## 12. Deviations (after running VE; empty at plan time)

1. **D1 is a sparse baseline, not the full F1–F17 translation planned in section 7.** The 32 authored rule blocks
   include F1 guideline alternatives; 20 direct blocks sit in D1 units and the reading alternatives remain
   pending. F5, F6, F11, F12 and F17 have OPEN source units, but their per-choice rules are still to be written.
   F13's “periodically review” is UNFORMALISED (ET). The other untranslated clauses are explicit
   `not_translated` units, not CHECKED. The follow-up must finish those rules before key answering.
2. **Only six Table 1 level markers carry D1 facts.** They are separate 6- or 10-byte units. Their capability
   descriptions, risk claims and safeguard bullets are separate OPEN or UNFORMALISED units. This prevents the whole
   row from becoming CHECKED when the two stated facts are all D1 encoded.
3. **D2 is admitted as a separate risk probe.** Its severe-harm class has the two disjuncts in footnote 1; the
   BIO-C “could cause millions of deaths” is one `might` cell and does not become a `leads` cell. The other Table 1
   causal units have no D2 decision record yet. No source byte is promoted by this probe.
4. **D3 certifies only the version date before retrieval.** The 1/5th self-improvement ratio and the severe-harm
   quantities remain `quantity` units (QT), and “several months” also waits for ET. P4 records this explicitly;
   those source bytes are not CHECKED.
5. **P8 refuses the planned combination.** On F2 with `judgments@0`, `documents@1` and D1's soft norms, Lean says
   `CheckerUnavailable: judgments@0 with soft-norms@0 needs its composed Lean route`. D1 therefore uses W2 open
   names and pending readings, as the plan allowed.
6. **The 186 `not_translated` units are mapped to “readings” as a translation backlog.** This is not a claim that
   landing a VE readings feature alone would make their 31,643 sole bytes CHECKED. The stage 0 and coverage files
   disclose the gap; `usecase-pf-run` must complete and check the source reading of each before answering keys.
7. **No key cell changed and no key item was answered in this baseline.** The only original-key comparison remains
   the freeze and transcription tests. No conflict is presented as a source finding.

## 13. Files for the implementation round (not this commit)

`environment.d1.json`, `environment.d2.json`, `environment.d3.json`; `pf.d1.ve.md`, `pf.d2.ve.md`, `pf.d3.ve.md`
(generated with the source prose from the pinned PDF, never committed with the full text); `spans.json`;
`cases.json` and `answer-key.json` (transcribed from section 6 in a separate commit that changes no key);
`reference.py`; `run.py`; `coverage.json`; `README.md`.
