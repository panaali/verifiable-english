# Use case: safety-framework (Google DeepMind Frontier Safety Framework, version 3.1)

> Status: **BUILT**, 2026-10-01, branch `usecase/safety-framework` (backlog item 2). Results are in
> [README.md](README.md), and every deviation from this plan is in section 12. The plan and its answer key (section 6)
> were committed before any VE run. The plan review's findings A to C
> (`manage-agents/safety-framework-planreview.final.md`) were applied in a separate commit, also before any VE run:
> RS3 and N2, B DISC and K9, and family R. No answer-key cell was changed after VE ran. No model calls were made.

This use case translates someone else's text, so it runs in **translation mode** ([VISION.md](../../VISION.md) 3,
[document.md](../../docs/spec/document.md)):

- every admissible reading is kept as a reading set, and no translator may collapse one;
- every vague term is a named open term with its decider;
- no default, permission, threshold, ordering or causal link is added that the text does not state;
- every byte of the source is accounted for.

It measures two things: whether VE answers four questions about a published frontier-lab safety framework the
same way as a key derived from the text by hand (section 6), and how much of the text VE can check at all
(section 10). A low CHECKED share is the expected and honest outcome.

## 1. Source (pinned)

| Field | Value |
|---|---|
| Document | Google DeepMind, *Frontier Safety Framework*, **Version 3.1**, "Published: April 17, 2026" (20 pages) |
| URL | `https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/strengthening-our-frontier-safety-framework/frontier-safety-framework_3-1.pdf` |
| Retrieved | 2026-10-01, about 10:50 UTC, with `curl` |
| PDF SHA-256 | `ad10d2d240e0d557ecad406dbccedcbb4a70295f8ba8eec46bfe01803cb9c301` (447,155 bytes) |
| Extracted text | [`source/extract_text.py`](source/extract_text.py) with `pypdf==6.19.0`: one line per page, whitespace collapsed. 54,373 bytes, 20 lines, SHA-256 `18e3375b35c6699a8bf864606e48a20fae0152f1073c37c51e27a0c0f0c53946`. Two runs gave identical bytes. |
| Currency check | The announcement page `https://deepmind.google/discover/blog/strengthening-our-frontier-safety-framework/` linked only this PDF at retrieval. The PDF's own version list (section 5.3) ends at 3.1. |
| Stored copy | `~/code/manage-agents/pilots/safety-framework/source/` (the PDF, the extracted text and the announcement page). It is **not** committed here: the PDF states no licence. This repository keeps the hashes, the extractor, short quotations and byte spans only. The span-accounting document is regenerated locally from the pinned PDF and checked against the text hash before any run. |

Quotations below are from the extracted text and each was checked to occur in it verbatim. "p. n" is the PDF page.

**Why this text.**

- **Current and versioned.** Version 3.1 is the latest the publisher lists, from 2026-04-17. The text dates every
  earlier version.
- **Named capability levels with if-then commitments.** It names seven levels (section 4.1), and for each it says
  what is assessed, which conditions make the risk acceptable for development or deployment, and when a
  deployment may take place. This is the shape the backlog item asks for: "if a model reaches level X, then Y is
  required before deployment".
- **Severity stated in its own words.** A Tracked Capability Level (TCL) concerns "significant but not severe"
  harm and a Critical Capability Level (CCL) concerns "severe" harm (Glossary, p. 18). That is an explicit
  two-class order for `risk@0`.
- **Real ambiguity and real gaps.** "If" may be sufficient only or a gate. Scope sentences may or may not reach
  every model. One recommended level is addressed "to the field". Some cases have no rule. These are the things
  the questions probe.
- **Short.** About 8,000 words, so full byte accounting is feasible.

**Candidates retrieved on the same day and not chosen.**

| Candidate | Pinned bytes | Why not |
|---|---|---|
| Anthropic, *Responsible Scaling Policy* v3.4 (effective 2026-07-08), `https://www-cdn.anthropic.com/files/4zrzovbb/website/0bacdc8440ea96e62a8766d99ebe1d4eea6d5f3a.pdf` | SHA-256 `6247b9e4001fd342827526fabc476c9d4dd6b2041ac00055f0ccda26f4d0b07d` | Current, but its threshold table is a list of industry-wide recommendations that the text says "we cannot commit to following unilaterally". The company column is "an overview, not ... separate or additional plans". Few if-then deployment commitments remain; most commitments concern Risk Reports. It is also the project lead lab's own text, so a third-party text avoids that conflict. |
| OpenAI, *Preparedness Framework* v2 (2025-04-15), `https://cdn.openai.com/pdf/18a02b5d-6b67-4cec-ab64-68cdfbddebcd/preparedness-framework-v2.pdf` | SHA-256 `fae6e4cc6f7212a010bb9348fc0cde1fe711b9cad426c6a99db97740ee52729b` | It has a good if-then shape, but its currency could not be checked: `openai.com` answered `curl` with HTTP 403, and the PDF is 18 months old. |

## 2. Scope

**In scope.** Every sentence of the pinned text is accounted for (section 10, M3). The questions concern:

- the seven named levels and the "no level reached" case;
- the five activities the text distinguishes: further development, internal deployment, high-risk internal
  deployment, low-risk external deployment and other external deployment (Glossary, p. 19);
- the process triggers: alert thresholds, subsequent versions, post-training runs, safety-case updates, the yearly
  review and disclosure;
- the stated severity classes and the version dates.

**Out of scope, with reasons.**

- **Whether any model has reached any level.** That is an open term decided by the developer (OT1); the cases
  stipulate it.
- **The content of external references.** This covers the RAND security levels, Google's Secure AI Framework
  (SAIF), the cited arXiv papers and the AI Principles. The text points to them but does not state them; each
  pointer is an open or labelled unit.
- **Event order inside a process** ("prior to", "upon the completion of", "periodic", "throughout the
  lifecycle"). `norms@0` has no deadlines ([norms.md](../../docs/spec/norms.md) 0). "Only after X" is translated
  as a precondition that X already holds when the activity is proposed (O7).
- **Earlier versions of the framework** and how they differ from 3.1.

## 3. Translation rules applied

### 3.1 Reading sets (written before the translation; none is collapsed)

Each set is cited to its source unit. The translation keeps every reading, and the harness evaluates every
complete choice of readings (section 9). "N1" and "N2" are the only narrowings; each cites source units and is
listed in the residual, and section 9 also reports what changes without each.

| Id | Source unit | Readings | Why the text admits each |
|---|---|---|---|
| RS0 | every "we will …" about the developer's own process | **commitment** (an obligation on the developer) / **prediction** (an assertion about the future) | "Will" is not a deontic word. |
| N1 | narrowing of RS0 to **commitment** | cites 4.1 "designed to ensure the robust implementation of the processes outlined in this Frontier Safety Framework" and 5.1 "an assessment of our adherence to the Framework" | The text treats its own process sentences as things one adheres to. A "will" sentence that also carries "may", "where appropriate", "as appropriate" or "as needed" is not narrowed; it stays RS4. Under N1 a commitment is strict (`must`). |
| RS1 | 1.3.5 bullets 2 to 4: "will be deemed to pose an acceptable level of residual risk for further development or deployment, if: …" | **S**: the listed conditions are sufficient for the classification "deemed acceptable", which gates nothing by itself / **G**: the listed conditions are sufficient for the classification, as worded, and are also necessary before the named activity proceeds (a gate). Under both readings the classification follows when the conditions hold; G adds the gate. | The words say "if". The heading "Risk Acceptance Determination", 1.3.3 "mitigations that will be required to bring a model to an acceptable level of risk" and the bullets' own "This is required only for …" all point to a gate. The text never says that development or deployment stops when the conditions fail. |
| RS2 | 2.1.2 step 2 "external deployments of a model take place only after the appropriate governance function determines the residual risk to be acceptable"; 3.1.2 step 2, the same for "external deployments and high-risk internal deployments" | **P**: within its section's process, which "will be applied to models reaching a misuse T/CCL" (2.1.2) or "for deployments of a model reaching a ML R&D and Misalignment T/CCL" (3.1.2) / **U**: about every model | Inside the process the sentence's subject is "a model", with no qualifier. |
| RS3 | the recommended security levels (2.2 and 3.2.2 tables): "the minimum appropriate level of security the field of frontier AI should apply"; for ML R&D automation level 1 "this must be taken on by the frontier AI field as a whole" | **F**: a recommendation to the field, not a norm on the developer / **Ds**: the field's "should" read distributively, so it also binds the developer as a member of the field. Under Ds the force follows the RS4 rule for "should" ({strict, default}), narrowed by N2. | The addressee is "the field", with "should". 1.3.5 nonetheless uses "the recommended security level" as one of three ways the developer's own security condition can hold. |
| N2 | narrowing of RS3 = Ds to **default** force | cites 2.2 "may be adjusted if … a model does not possess capabilities meaningfully different from other publicly available models that have weaker security applied … or if we assess that the benefits of the open release of model weights outweigh the risks", footnote 11 "The same caveats regarding security levels for misuse CCLs apply", and 1.3.5 bullets 2 and 3 "or we otherwise assess that the level of security applied is adequate … or we assess that the benefits of the open release of model weights outweigh the risks" | The text itself states when the recommended level need not be applied. A strict reading would contradict those stated cases, so they become the default rule's excepted cases (soft-norms.md 1.1: OT16, OT4 and OT5 as sufficient conditions). The developer's only strict security commitment is the SEC condition of F9 and F10 (under RS1 = G). Section 9 reports what changes without N2. |
| RS4 | hedged force: 5.2 "we aim to share"; 1.3.5 Note "should also be assessed holistically"; Glossary "The residual risk should be brought within the acceptable levels"; Note on ML R&D CCLs "Risk assessment must take into account …" | for "aim to": **default norm** (a soft norm, decider unstated) / **intent** (no norm). For "should" and "must": **strict** / **default**, the [soft-norms.md](../../docs/spec/soft-norms.md) 2.2 translation rule | "Aim" states a goal. The force words follow the general rule. |
| RS5 | 1.3.2 "we determine whether a substantial modification has been made and whether a further critical capability assessment is required if (1) … and (2) …" | **D**: (1) and (2) trigger the determination / **R**: (1) and (2) make a further assessment required | The "if" clause can attach to "we determine" or to "is required". |
| RS6 | 2.2 "the risks of insider misuse … are effectively addressed by our baseline controls … additional mitigations beyond these established safeguards are not required" against 2.1.1 Security Level 2+ "with additional security measures designed to address risks from insider threats" | **same**: both concern one act, adding insider-risk mitigations to a model at a misuse CCL / **different**: insider *misuse* of capabilities is not insider *threat* to weights | Both name insiders and "additional" measures. Background checks appear on both lists. |
| RS7 | footnote 4: "A critical capability assessment may not be conducted for low-risk external deployments … if the appropriate governance function determines the residual risk of such deployments to be acceptable" | **E**: a permission not to conduct it, an exception to F2 (the footnote is attached to F2's sentence) / **M**: "may" in the sense of "might", no norm | In translation "may" is ambiguous; norm English never reads "may" as "might" ([norms.md](../../docs/spec/norms.md) 2). |
| RS8 | 1.3.5 "This is required only for external deployment, not internal deployment or further development" (bullet 2), and "only for external deployment and high-risk internal deployment, not further development" (bullets 3 and 4) | **scope**: limits where the bullet's condition applies; no rule of its own / **release**: an explicit "need not" for the activities left out | "Only … not …" can be a scope note or a rule. |
| RS9 | the three deployment-mitigation conditions: "residual risk of harm" (bullet 2), "residual risk of severe harm" (bullet 3), "residual risk of significant harm … or … very unlikely to possess the propensities" (bullet 4) | **same**: bullets 2 and 3 name one act, bringing the residual risk to an acceptable level / **different**: three acts, as worded | The wording differs; whether the difference matters is not stated. |
| RS10 | 5.1 "will be reviewed at least once a year" | **publication**: counted from the publication of the current version / **unstated**: counted from an unstated last review | No start point is given. |

### 3.2 Open terms (each with its decider; none gets invented criteria)

Each has the W2 schema (`name`, `arguments`, `decided_by`, `necessary`, `sufficient`, `factors`, `precedents`,
`jurisdiction`, `version`). Factors are copied from the text's "such as" and "e.g." lists and give no premise.
`we` means the framework's authors as the text uses the word; the text never names a person or body as decider.

| Id | Term | Decided by (from the text) | Factors or definitions stated |
|---|---|---|---|
| OT1 | the model has reached level L (also: has reached an alert threshold) | `we` (critical capability assessment, 1.3.2) | early warning evaluations, expert assessments, "other sources of information" |
| OT2 | the deployment mitigations have brought the residual risk (of harm / severe harm / significant harm) to an acceptable level | `we` ("We assess", 1.3.5) | effectiveness, scope of deployment, other public models, historical incidence and severity |
| OT3 | the appropriate governance function determines the residual risk to be acceptable | `appropriate governance function` (unnamed) | "including a safety case where a CCL has been reached" |
| OT4 | the level of security applied is adequate | `we` | "match or exceed the level of security applied to other models with similar capabilities or risk profiles" |
| OT5 | the benefits of the open release of model weights outweigh the risks | `we` | none |
| OT6 | the model is very unlikely to possess the propensities required for material risk of significant harm through misalignment | `we` | none |
| OT7 | high-risk internal deployment | `unstated` | Glossary: "use cases with the potential to enable severe threat scenarios (e.g. …)" |
| OT8 | low-risk external deployment | `unstated` (footnote 4 lets the governance function decide acceptability, not the class) | Glossary: "small scale and private releases restricted to particular external groups" |
| OT9 | frontier AI model | `unstated` | Glossary definition (generality, near or above other Google models) |
| OT10 | meaningful new capabilities or material increases; could materially undermine the justification | `we` ("we believe") | provenance, size, modality, benchmarks |
| OT11 | the CCL "poses an unmitigated and material risk to overall public safety"; sharing "will facilitate safety" | `we` | none |
| OT12 | "periodic" (3.2.1) | `unstated` | none |
| OT13 | "reasonable grounds to believe the adequacy of the Framework or our adherence to it has been materially undermined" (5.1) | `we` | none |
| OT14 | security level N (RAND SL N goals and principles) | external reference, `unstated` | "security goals and principles … rather than the benchmarks" |
| OT15 | uplift / "additional expected harm" relative to "a baseline without generative AI" | `unstated` | reference scenarios |
| OT16 | the 2.2 adjustment cases: "does not possess capabilities meaningfully different from other publicly available models that have weaker security applied" | `we` | none |

### 3.3 What the translation must not add

- **No completion default is trusted.** W1 forces one per regulated predicate. Every query is run under both
  defaults ("need not" and "must"), and only selection-based verdicts are scored (as in
  [agent-policy](../agent-policy/PLAN.md) 5). A verdict that depends on the default is a gap.
- **No permission the text does not grant.** "Deemed acceptable for further development and deployment" (1.3.5)
  is a classification, never a permission to proceed. Adding that permission would create the conflict case C5,
  so C5 is keyed NONE.
- **No threshold or ordering.** In particular there is no order between SL2+, SL3 and SL4: their footnotes say
  only "may include". "Catastrophic" is not ranked against "severe". No level implies another; the text never
  says that reaching a CCL means the TCL of the same domain was reached.
- **No causal link stated as certain.** The text says "may", "could", "resulting in additional expected harm",
  "may enable" and "increases the likelihood". These become `causal` units (LABELLED) or `might lead to` cells.
  They never become `leads to`, and "uplift" is an open degree term (OT15; `alternatives@0` rejects "provides
  uplift to").

## 4. The text as rules (the inventory the key and the translation both use)

### 4.1 Named levels (F1)

| Id | Level, verbatim name | Domain | Kind | Harm class stated | Recommended security level |
|---|---|---|---|---|---|
| L1 | CBRN uplift TCL | CBRN (misuse) | TCL | significant ("significant but not severe harm", p. 11) | none stated |
| L2 | CBRN uplift level 1 | CBRN (misuse) | CCL | severe ("additional expected harm at severe scale", p. 11) | Security level 2+ |
| L3 | Cyber uplift level 1 | Cyber (misuse) | CCL | severe (p. 12) | Security level 2+ |
| L4 | Harmful manipulation level 1 (exploratory) | Harmful manipulation (misuse) | CCL | severe (p. 12) | Security level 2+ |
| L5 | Stealth and Situational Awareness TCL | ML R&D and misalignment | TCL | significant (Glossary TCL definition) | none stated |
| L6 | ML R&D acceleration level 1 | ML R&D and misalignment | CCL | severe ("may reach a severe scale", 3.2.2) | Security level 3 |
| L7 | ML R&D automation level 1 | ML R&D and misalignment | CCL | severe (3.2.2) | Security level 4 ("must be taken on by the frontier AI field as a whole") |

L0 is "no T/CCL reached". **Closure sentences stated by the text:** misuse CCLs are in exactly CBRN, cyber and
harmful manipulation (1.2); "We identify TCLs for CBRN risk, as well as ML R&D and misalignment risks" (1.2); "For
CCLs, we define 'alert thresholds'" (1.3.2). The text states no closure for recommended security levels: it says
"We recommend a security level for each CCL" and lists levels only in the CCL tables.

### 4.2 Commitments

| Id | Source | Content (the reading sets that apply) |
|---|---|---|
| F2 | 1.3.2 | A critical capability assessment (CCA) takes place before the first external deployment of a new frontier AI model. (RS0/N1) |
| F3 | footnote 4 | Exception to F2 for a low-risk external deployment when the governance function determines its residual risk acceptable, "even if the model has reached a T/CCL". (RS7) |
| F4 | 1.3.2 | A subsequent version with (1) meaningful new capabilities and (2) a possible material undermining of the justification. (RS5) |
| F5 | 1.3.2 | "we conduct material capability change assessments on various checkpoints upon the completion of a post-training run". The object is existential ("various checkpoints"), so it stays inside the act phrase. |
| F6 | 1.3.3 | "When a model reaches an alert threshold for a CCL, we will assess the proximity of the model to the CCL and analyze the risk posed". |
| F7 | 1.3.4; 2.1.2/3.1.2 step 1c | "Models reaching TCLs or CCLs will be subject to residual risk assessments" (RRA). For CCLs the RRA is informed by a supplemental safety case (SC). |
| F8 | 1.3.5 bullet 1 | No T/CCL reached → "deemed to pose an acceptable level of risk for further development and deployment". A classification only (3.3). |
| F9 | 1.3.5 bullet 2 | Misuse T/CCL reached → deemed acceptable for further development or deployment if (a) DM-h, the deployment mitigations brought the residual risk of harm to an acceptable level (OT2), required only for external deployment; and (b) SEC, the recommended security level applied, or the level otherwise assessed adequate (OT4), or open release judged beneficial (OT5). (RS1, RS8, RS9) |
| F10 | 1.3.5 bullet 3 | ML R&D CCL reached → as F9, with DM-s (residual risk of *severe* harm), required only for external and high-risk internal deployment; and SEC. (RS1, RS8, RS9) |
| F11 | 1.3.5 bullet 4 | ML R&D TCL reached → as F10, with DM-g (DM for *significant* harm, or very unlikely propensities, OT6) and SEC-t (adequate, OT4, or open release, OT5; no recommended-level disjunct). (RS1, RS8) |
| F12 | 2.1.2 step 2 | External deployments take place only after GOV, the governance function's determination (OT3), which includes an SC where a CCL is reached. (RS2) |
| F13 | 3.1.2 step 2 | External and high-risk internal deployments take place only after GOV. (RS2) |
| F14 | 2.1.2/3.1.2 step 3 | "Material updates to a safety case will be submitted to the appropriate governance function for review." |
| F15 | 2.2 intro | Insider misuse at misuse T/CCLs: "additional mitigations beyond these established safeguards are not required". (RS6) |
| F16 | 2.1.1, 2.2, 3.2.2 | Recommended security levels (table in 4.1), with the 2.2 adjustment cases (OT16, OT5). Footnote 11 applies the same caveats to ML R&D. Under RS3 = Ds (with N2) a default rule on the developer, whose excepted cases are OT16, OT4 and OT5; under F no rule on the developer. (RS3, N2) |
| F17 | 3.2.1 | At L5: "periodic residual risk assessments of the misalignment risk" (PRA, OT12), which account for high-risk internal deployments. If the internal-deployment residual risk is unacceptable without additional safeguards, "these will be applied" (ADD). |
| F18 | 5.1 | Review "at least once a year", more often given reasonable grounds (OT13). The updated version is reviewed by governance bodies. (RS10) |
| F19 | 5.2 | At a CCL posing an unmitigated, material risk to public safety (OT11), "we aim to share relevant information with appropriate government authorities" (DISC). (RS4) |
| F20 | 1.3.5 Note; Glossary; Note on ML R&D CCLs | Soft or strict: "should also be assessed holistically", "should be brought within the acceptable levels", "Risk assessment must take into account …". (RS4) |

Everything else (the overview, scope statements, beliefs, expectations, examples, the SAIF description, rationales,
URLs, page furniture) is accounted for as LABELLED or UNFORMALISED units, with reasons (section 10, M3).

## 5. Questions and cases (exact list)

The brief's four questions map to the families:

- "What is required at each named level": families A, B and K, and family R for the risk acceptance determination
  itself (when the text deems a model's risk acceptable, kept apart from any permission to deploy).
- "Do any two commitments conflict": family C.
- "Which levels or situations no rule covers": family G, plus the NONE cells of A and B.
- "Which commitments can never apply": family N.
- Families S and D cover the severity, causation and date features.

**Verdicts.**

- **ALL**: the item holds under every complete choice of the reading sets that bear on it, with N1 applied.
- **SOME(c)**: it holds exactly under the choices that satisfy condition c. The condition is part of the key and
  is scored.
- **NONE**: it holds under no choice.
- **Requirements.** "R is required" means some rule's obligation `meet(p, R)` selects at the case's proposal `p`
  (selection as in [agent-policy](../agent-policy/PLAN.md) 5), under both completion defaults. A default rule
  (a soft norm) counts when it selects with no exception finding, which the case leaves unset; the results say
  which requirements are only soft.
- **REL**: a "need not" rule selects. It counts as covered, but it is not a requirement.
- **Deemed acceptable** (family R): a rule of F8 to F11 concludes the classification at `p`. It is a classification,
  never a permission to proceed (3.3).
- **Conflicts.** CONFLICT is the W1 conflict check on the document of that choice. A strict rule that blocks a
  default rule on the same act is not a conflict (soft-norms.md 1.4 and 4.2).

**Case facts.**

- The model has reached exactly the levels named (L0: none) and no others.
- The proposal is of the named activity.
- For low-risk external (LRX) and other external (EXT) deployments, the proposal is the first external deployment
  of a new frontier AI model.
- For LRX, the governance function has determined this deployment's residual risk acceptable, which exercises F3.
- Every other open term is unset unless the case says so.

| Family | Cases | Scored items |
|---|---|---|
| A: required conditions per level and activity | A-L*k*-*X* for *k* = 0…7 and *X* ∈ {DEV, INT, HRI, LRX, EXT}: 40 cases | 4 atoms each (DM, SEC, GOV, CCA): 160 |
| B: per-level requirements independent of the activity | B-L0 … B-L7: 8 cases | 5 atoms each (RRA, SC, PRA, RECSEC, DISC): 40 |
| K: process triggers | K1 (5 cases), K2 (2), K3 to K8, K9 (5) | 18 |
| R: risk acceptance determination | R1 to R9 | 11 |
| C: conflicts | C1 to C5, C-doc | 6 |
| G: gaps | G1 to G9 | 9 |
| N: never applies | N1 to N3 | 3 |
| S: severity and causation | S1 (7 levels), S2 to S6 | 12 |
| D: dates | D1 to D3 | 3 |
| **Total** | | **262** |

## 6. Answer key (written before any VE run)

Notation:

- G, S: RS1; U, P: RS2; Ds, F: RS3; M, E: RS7; rel: RS8 release; same: RS9 or RS6 "same".
- DM is DM-h at L1 to L4, DM-g at L5 and DM-s at L6 and L7. SEC is SEC-t at L5.

### 6.1 Family A (160 items)

| Cases | DM | SEC | GOV | CCA | Justification |
|---|---|---|---|---|---|
| A-L0-DEV, A-L0-INT | NONE | NONE | NONE | NONE | F8 states no condition. F12 and F13 concern external and high-risk internal deployment. F2 concerns external deployment. |
| A-L0-HRI | NONE | NONE | SOME(U) | NONE | F13 reaches a model with no T/CCL only under U. |
| A-L0-LRX | NONE | NONE | SOME(U) | SOME(M) | F12 under U. Under E, F3 releases the CCA, because the governance function found the deployment acceptable. Under M, F2 stands. |
| A-L0-EXT | NONE | NONE | SOME(U) | ALL | F2: the first external deployment of a new frontier model. |
| A-L*k*-DEV, A-L*k*-INT, *k* = 1…4 | NONE (REL under G∧rel) | SOME(G) | NONE | NONE | F9: SEC holds "for further development or deployment"; DM is "required only for external deployment, not internal deployment or further development". |
| A-L*k*-HRI, *k* = 1…4 | NONE (REL under G∧rel) | SOME(G) | SOME(U) | NONE | High-risk internal deployment is internal deployment (Glossary), so F9 as above. F13 reaches misuse models only under U. |
| A-L*k*-LRX, *k* = 1…4 | SOME(G) | SOME(G) | ALL | SOME(M) | F9 (external). F12 covers misuse T/CCL models under P and under U. F2 and F3 as for L0. |
| A-L*k*-EXT, *k* = 1…4 | SOME(G) | SOME(G) | ALL | ALL | F9, F12, F2. |
| A-L5-DEV | NONE (REL under G∧rel) | SOME(G) | NONE | NONE | F11: "not further development". |
| A-L5-INT | NONE (REL under G∧rel) | SOME(G) | NONE | NONE | F11 "only for external deployment and high-risk internal deployment". F13 covers high-risk internal deployment only. F17's ADD needs an unset finding (see K7). |
| A-L5-HRI | SOME(G) | SOME(G) | ALL | NONE | F11, and F13 under P and U. |
| A-L5-LRX | SOME(G) | SOME(G) | ALL | SOME(M) | F11, F12/F13, F2/F3. |
| A-L5-EXT | SOME(G) | SOME(G) | ALL | ALL | F11, F12/F13, F2. |
| A-L*k*-DEV, A-L*k*-INT, *k* = 6, 7 | NONE (REL under G∧rel) | SOME(G) | NONE | NONE | F10, as A-L5. |
| A-L*k*-HRI, *k* = 6, 7 | SOME(G) | SOME(G) | ALL | NONE | F10, F13. |
| A-L*k*-LRX, *k* = 6, 7 | SOME(G) | SOME(G) | ALL | SOME(M) | F10, F12/F13, F2/F3. |
| A-L*k*-EXT, *k* = 6, 7 | SOME(G) | SOME(G) | ALL | ALL | F10, F12/F13, F2. |

Totals: ALL 25, SOME 67, NONE 68. Under the RS0 "prediction" reading (without N1), every ALL and SOME above
becomes NONE: nothing is required. That is reported, not scored.

### 6.2 Family B (40 items)

| Case | RRA (F7) | SC (F7) | PRA (F17) | RECSEC (F16) | DISC (F19) |
|---|---|---|---|---|---|
| B-L0 | NONE | NONE | NONE | NONE | NONE |
| B-L1 | ALL | NONE | NONE | NONE (no level stated) | NONE (not a CCL) |
| B-L2, B-L3, B-L4 | ALL | ALL | NONE | SOME(Ds): SL2+, soft | NONE (OT11 unset; see K9) |
| B-L5 | ALL | NONE | ALL | NONE (no level stated) | NONE |
| B-L6 | ALL | ALL | NONE | SOME(Ds): SL3, soft | NONE (OT11 unset; see K9) |
| B-L7 | ALL | ALL | NONE | SOME(Ds): SL4, soft | NONE (OT11 unset; see K9) |

Totals: ALL 13, SOME 5, NONE 22. Under Ds (with N2), RECSEC is a default rule: it selects unless an exception
finding (OT16, OT4 or OT5) holds, and the B cases leave those unset (F16, footnote 11). Under F nothing on the
developer selects. The case facts leave OT11 unset, so F19's guard fails and DISC is NONE in every B case; family K9
stipulates the OT11 findings.

### 6.3 Family K (13 items)

| Case | Situation | Item | Key | Justification |
|---|---|---|---|---|
| K1-L2, K1-L3, K1-L4, K1-L6, K1-L7 | the model reaches an alert threshold for the CCL | proximity assessment and risk analysis required | ALL | F6 |
| K2-L1, K2-L5 | an "alert threshold" for a TCL | any requirement | NONE | alert thresholds are defined "For CCLs" only (gap G3) |
| K3 | a subsequent version with (1) and (2), before external deployment | a further CCA required | SOME(R) | F4, RS5 |
| K4 | a post-training run completes on checkpoint c | an MCCA of **c** required | NONE | F5 commits to "various checkpoints", not to each one; the existential object stays in the act phrase |
| K5 | a material update to a safety case | submission to the governance function required | ALL | F14 |
| K6 | the framework at any time | a review at least yearly required | ALL | F18 (the deadline is family D) |
| K7 | L5, internal deployment, and the finding that the residual risk is unacceptable without additional safeguards | ADD required | ALL | F17 "these will be applied" |
| K8 | reasonable grounds (OT13) found | a more frequent review required | ALL, conditional on OT13 | F18 |
| K9-L2, K9-L3, K9-L4, K9-L6, K9-L7 | the model has reached the CCL, and both OT11 findings hold: the CCL poses an unmitigated and material risk to overall public safety, and sharing will facilitate safety | sharing information with government authorities required (DISC) | SOME(RS4 "aim to" = default norm), soft | F19. Under "intent" no norm selects. |

### 6.3a Family R: risk acceptance determination (11 items)

"Deemed acceptable" is the classification of 1.3.5. It is never a permission to proceed (3.3), so R9 also asks
whether any rule permits or forbids proceeding. Under RS1 the classification follows from the stated conditions in
both readings; RS8 limits the deployment-mitigation condition to the activities the bullet names. Every open term
not named is unset.

| Case | Situation | Item | Key | Justification |
|---|---|---|---|---|
| R1 | L0, EXT | deemed acceptable | ALL | F8 |
| R2 | L2, EXT; DM-h found (OT2); Security level 2+ applied | deemed acceptable | ALL | F9: both conditions hold |
| R3 | L2, EXT; Security level 2+ applied; DM-h found **not** to hold | deemed acceptable | NONE | F9's DM condition fails, and no other rule concludes the classification. The text never says the opposite either (silent) |
| R4 | L2, DEV; Security level 2+ applied; DM-h unset | deemed acceptable | ALL | F9: DM is "required only for external deployment", so SEC alone is the condition for further development |
| R5 | L6, HRI; DM-s found (OT2); security assessed adequate (OT4), no recommended level applied | deemed acceptable | ALL | F10: SEC's second disjunct |
| R6 | L5, EXT; very unlikely propensities found (OT6); open release judged beneficial (OT5) | deemed acceptable | ALL | F11: DM-g's second disjunct and SEC-t's second disjunct |
| R7 | L5, EXT; DM-g found (OT2); OT4 and OT5 found **not** to hold | deemed acceptable | NONE | F11's SEC-t fails |
| R8 | L1, EXT; DM-h found (OT2); Security level 2+ applied; OT4 and OT5 unset | deemed acceptable | NONE | No unit states a recommended level for L1, so SEC's first disjunct cannot hold (N2 of family N); nothing is invented |
| R9a | L2, EXT; DM-h found; Security level 2+ applied; GOV not determined | deemed acceptable | ALL | F9 |
| R9b | the same case | some rule permits proceeding | NONE | "Deemed acceptable" is a classification only (3.3) |
| R9c | the same case | some rule forbids proceeding | ALL | F12 covers misuse T/CCL models under P and U, and GOV is absent |

### 6.4 Family C: conflicts (6 items)

| Case | Rules | Key | Witness or reason |
|---|---|---|---|
| C1 | F15 against F16 | NONE | A model at L2 (or L3, L4). Under F the recommendation puts no norm on the developer. Under Ds (with N2) the SL2+ insider-threat measures are a default rule; under RS6 "same", F15's strict "need not" regulates the same act and blocks the default rule instead of conflicting with it (soft-norms.md 4.2). Without N2 (Ds strict), C1 would be SOME(RS6 same ∧ Ds strict); section 9 reports this. |
| C2 | F2 against F3 | NONE | Under E, F3 is an exception to F2 (precedence from the footnote's attachment). Under M, F3 is no norm. Mutant m1 removes the precedence and must give CONFLICT. |
| C3 | F9 against F10 | SOME(G ∧ rel ∧ RS9 same) | A model at a misuse T/CCL and an ML R&D CCL, proposed for high-risk internal deployment. F9 releases DM for internal deployment and F10 requires it. |
| C4 | F16 against F9/F10's SEC and the 2.2 adjustment cases | NONE | SEC is a disjunction that contains the recommended level. The adjustments are the default rule's excepted cases under Ds, and under F there is no norm on the developer. |
| C5 | F8 against F12/F13 (U) at L0 | NONE | F8 is a classification, not a permission (3.3), so "deemed acceptable" and "only after GOV" never collide. |
| C-doc | the whole document, per choice | SOME(G ∧ rel ∧ RS9 same) | Exactly C3. Otherwise CONFLICT-FREE. |

### 6.5 Family G: gaps (9 items)

"Silent" means no rule selects under the stated readings, so the answer depends on the completion default only.

| Case | Situation | Key | Justification |
|---|---|---|---|
| G1 | further development of a CCL model whose SEC fails | silent: SOME(S) | Under G, SEC is necessary before further development (F9/F10); under S no rule says anything. The text never says development pauses. |
| G2 | internal (not high-risk) deployment of an ML R&D CCL model, with no GOV | silent on GOV: ALL | F13 covers high-risk internal deployment only. Under G, SEC still applies. |
| G3 | approaching or reaching a TCL (alert) | silent: ALL | No alert thresholds for TCLs (K2). |
| G4 | significant but not severe cyber or manipulation risk | covered by F8's catch-all classification: ALL; no safeguard required | There is no cyber or manipulation TCL, so F8 applies. Reported as COVERED-BY-CATCH-ALL. |
| G5 | a capability in a domain outside the four | as G4 | F8. 1.3.1's "continue to assess" is no commitment. |
| G6 | the first external deployment of a non-frontier model | silent on CCA: ALL; GOV SOME(U) | F2 is for frontier models; 1.3.2 says MCCAs "may" also apply to them. |
| G7 | disclosure for a TCL or for a mitigated CCL risk | silent: ALL | F19 needs a CCL with an unmitigated, material risk. |
| G8 | post-deployment evidence that the safeguards are circumvented | silent: ALL (except K5 when a material safety-case update is made) | Step 3 says the assessments "may be updated". |
| G9 | the governance function does not find an external deployment acceptable | covered (must not deploy) for T/CCL models: ALL; for L0: SOME(U) | F12/F13 under P and U, or U only for L0. |

### 6.6 Family N: never applies (3 items)

| Case | Question | Key | Justification |
|---|---|---|---|
| N1 | Can F9 apply through a cyber or harmful-manipulation TCL? | never: ALL (a certificate from the closure in 4.1) | "We identify TCLs for CBRN risk, as well as ML R&D and misalignment risks." |
| N2 | Can SEC's first disjunct (the recommended level) ever hold for L1? | **not certifiable**: no unit states a recommendation for L1, and none states that recommendations exist only for CCLs. VE must answer UNKNOWN or give a countermodel in both directions, and report the disjunct as unsupported by any unit. | Never inventing a closure is the point. |
| N3 | Is any commitment F2 to F20 dead (an unsatisfiable guard)? | no: NONE dead; a witness model for each | Every guard is satisfiable over the declared vocabulary. |

### 6.7 Family S: severity and causation (12 items)

| Case | Question | Key | Justification |
|---|---|---|---|
| S1-L1 … S1-L7 | the severity class of the level's stated harm | L1 significant; L2, L3, L4 severe; L5 significant; L6, L7 severe | Table 4.1. The Glossary orders "significant but not severe" below severe. |
| S2 | Is every CCL harm more severe than every TCL harm? | ALL (yes) | severe is more severe than significant (Glossary). |
| S3 | Is "catastrophic" (3.2.2, L7 rationale) ordered against "severe"? | NONE (no edge; countermodels both ways) | The text states no order (3.3). |
| S4 | Is SL4 at least as strong as SL3? | NONE (not entailed; countermodel) | The footnotes say only "may include" (3.3). |
| S5 | Might deploying an unmitigated L2 model lead to a severe harm? | ALL (a stated `might` cell) | CCL definition: "absent mitigation measures … may pose heightened risk of severe harm". |
| S6 | Does deploying an unmitigated L2 model *lead to* a severe harm? | NONE (no sufficient source; VE must not derive it) | Only "may" is stated. |

### 6.8 Family D: dates (3 items)

| Case | Question | Key | Justification |
|---|---|---|---|
| D1 | Are the version dates increasing in version order: 1.0 (2024-05-17), 2.0 (2025-02-04), 3.0 (2025-09-22), 3.1 (2026-04-17)? | ALL (yes) | 5.3 |
| D2 | Is a review due no later than 2027-04-17? | SOME(RS10 publication) | Bridge: "a year" from 2026-04-17 is 365 days, with no 29 February between, so 2027-04-17. Under "unstated" the start point is OPEN. |
| D3 | Was v3.1 published before the retrieval date 2026-10-01? | ALL (yes) | That v3.1 is the latest version is an observation leaf (LABELLED), not a VE result. |

**Independent check of the key.** In the implementation round, `reference.py` (stdlib only, no `ve` import) is
written from sections 3 and 4 alone. It enumerates the reading choices and recomputes families A, B, C and G. A
disagreement with this section is resolved by a separate commit that says why, never inside a results commit. The
same author wrote this key and will write the translation. The checks on that are the cited justification on
every key row and the plan review.

## 7. Planned VE translation

**Documents.** `risk@0` requires `alternatives@0`, which rejects `soft-norms@0` ([risk.md](../../docs/spec/risk.md)
1.1). W6a quantities need a `ve-units@1` environment, which admits no norms. So three `ve-document@1` documents
are needed, each over disjoint byte ranges of the pinned text.

| Doc | Environment profiles | Carries | Questions |
|---|---|---|---|
| D1 | `norms@0`, `soft-norms@0` (base profiles fixed by probe P1) | F2 to F20, the level vocabulary and closure sentences, open terms, reading sets | A, B, K, C, G, N |
| D2 | `norms@0`, `alternatives@0`, `risk@0` | severity block (`significant`, `severe`; `severe` more severe than `significant`, from the Glossary), one harm constant per level, stated `might` cells for unmitigated deployment, `causal` units | S |
| D3 | `ve-units@1` (`documents@1`, `order@0`, `relational-fol@0`, `time@0`) | version dates, publication date, the review bound under RS10 publication | D |

The master coverage map assigns every byte to exactly one unit of exactly one document. D1 carries the whole
text. Its units for byte ranges checked in D2 or D3 are `routed` placeholders, and the harness replaces them with
the D2 or D3 unit's status, after checking that the byte ranges are equal (probe P6).

**Shared structure (the CHECKED bar).**

- Rules quantify over `level`, `domain`, `proposal` and `requirement`. Levels, domains, requirement atoms and
  security levels are constants, and their properties are facts: `is a critical level`, `is a tracked level`,
  `belongs to <domain>`, `is a misuse domain`, `has <security level> as its recommended level`.
- One source bullet gives one rule. F9, for example, is a single rule over every level of a misuse domain.
- **Forbidden:** a predicate or constant that packs a level, number or condition into its name, such as
  `cbrn_ccl_requires_sl2plus` or `external_deploy_after_governance`.
- **Allowed:** constants whose names are the source's own labels (`cbrn_uplift_level_1`, `security_level_2_plus`).
  Probe P7 lints this mechanically.

**Vocabulary sketch.**

- **Sorts:** `level`, `domain`, `proposal`, `requirement`, `security_level`.
- **Base predicates:**
  - level facts: `reached(proposal, level)`, `critical(level)`, `tracked(level)`, `in_domain(level, domain)`,
    `misuse(domain)`, `recommended(level, security_level)`;
  - activity facts: `further_development(proposal)`, `internal(proposal)`, `high_risk_internal(proposal)`,
    `external(proposal)`, `low_risk_external(proposal)`, `first_external_of_new_frontier_model(proposal)`;
  - open-term predicates, one per OT.
- **Regulated obligation `meet(proposal, requirement)`**, act phrase `{0} meet {1}`. Under RS1 = G each F9 to F11
  condition is a `must` rule. Under RS8 = rel the "not …" clauses are `need not` rules. Under both RS1 readings,
  F8 to F11 conclude the plain predicate `deemed_acceptable(proposal)` when their conditions hold (family R).
- **Regulated permission `proceed(proposal)`.** Only F12/F13 forbid it ("must not proceed, unless …").
  Selection-based verdicts make the default irrelevant (3.3).
- **Reading sets.** Each RS is a W2 reading set on its source unit, with one candidate per reading. The harness
  builds one document per complete choice for each case, at most 2⁵ = 32 per case, under the W2 cap of 64.

**Feature map.**

| Part | VE feature | Status at plan time |
|---|---|---|
| F2 to F15, F17 to F18 | `norms@0` rule blocks, exceptions (F3 as `Rule n (exception to rule m)`), `need not` (RS8, F15), stratified `proceed` | merged |
| F16 (RS3 F/D), F19, F20 (RS4) | `soft-norms@0`: `should` / default rules, `excepted_N` with deciders, READINGS {strict, default} | merged |
| Conditions (levels, activities, closures) | base formulas in guards; closure sentences as premises | merged |
| Open terms OT1 to OT16 | W2 open-term declarations, residual | merged (strict only; no English authoring yet) |
| Reading sets RS0 to RS10, N1 | W2 reading sets and narrowing; `ve document readings` | merged. Norm reading sets return UNKNOWN natively (document.md); per-choice expansion is a harness step and is labelled so. |
| Severity, `might lead to` | `risk@0` severity block, `harm_classes`, stated `might` cells, `is <class> or worse` | merged; fit for an assertion-only policy is probe P3 |
| Causal sentences | W2 `causal` kind (LABELLED); `alternatives@0` rejects "provides uplift to" | merged |
| Dates | W6a `day` literals, `date_no_later`, `elapsed_days` | merged |
| Span accounting | `ve-document@1` partition, `MIXED` parts, `bytes_by_status` | merged |
| Conflicts, never-applies | W1 conflict check, selection, dead-guard witnesses | merged |

## 8. What is expected to stay OPEN

- **O1: every open term OT1 to OT16.** In particular, whether a model has reached a level is never a VE result.
  Every family A answer is "required given the stipulated level".
- **O2: norm reading sets.** The native readings query returns UNKNOWN for norm kinds until the W1 elaborator
  supports choices. ALL, SOME and NONE come from the harness's per-choice expansion and are labelled harness
  results.
- **O3: causal and degree language** ("resulting in", "may enable", "increases the likelihood", "uplift",
  "expected harm"). These units are LABELLED `causal` or OPEN, and none is CHECKED.
- **O4: beliefs, expectations, aims and intent** ("we believe", "we expect", "we may", "we strive", "we aim").
  These are unformalised or soft, with reasons.
- **O5: examples and factor lists.** They are factors of open terms and give no premise.
- **O6: external standards** (RAND SL, SAIF, the arXiv papers): their content and their order.
- **O7: event order and frequency** ("prior to", "after", "upon completion", "periodic", "throughout the
  lifecycle"). Preconditions are read as states, and deadlines are not represented.
- **O8: feature combination.** Severity (D2) cannot be combined with soft norms (D1) in one environment, so no
  question may need both. None of section 5 does.
- **O9: the review anchor and "a year".** The day count is a bridge (W6a has no year unit).
- **O10: who "we" is.** Google, Google DeepMind and the framework's authors are labelled, never identified.

## 9. Run protocol (implementation round)

**Stage 0 probes.** The expected results are recorded here.

| Probe | Input | Expected |
|---|---|---|
| P1 | D1 environment with `norms@0` + `soft-norms@0`, an obligation rule with an open-term predicate in its guard, the open-term declarations | admitted; the rule is OPEN |
| P2 | a norm reading set (RS1) and `ve document readings` | UNKNOWN; each authored singleton choice admits and runs |
| P3 | D2: a risk environment whose policy has only assertion units (severity facts, `might` cells) and one decision record per CCL | admitted. If a decision record cannot carry only `might` cells, S5 and S6 move to D1 as plain facts, recorded as a deviation. |
| P4 | D3: the dates 2024-05-17 to 2027-04-17, `elapsed_days` | admitted, with certificates |
| P5 | D1 partition over the 54,373-byte text, `MIXED` units | `bytes_by_status` totals 54,373 |
| P6 | routed placeholders against the D2 and D3 spans | equal byte ranges; the master map is total and disjoint |
| P7 | the identifier lint on the environments | 0 violations |

**Per case.**

1. Build the facts from section 5. Never read the key.
2. For every complete choice of the reading sets in the case's cone, build the document and check that the
   premises are consistent (a model or an inconsistency certificate). Inconsistency is reported, never scored as
   an answer.
3. Compute the selections, the conflict status or the entailment under both completion defaults.
4. Combine the choices into ALL, SOME(c) or NONE.
5. A search that runs out of budget is UNKNOWN and counts as a miss, never as an answer.

## 10. Metrics to report

| # | Metric | Expected |
|---|---|---|
| M1 | key agreement per family (A 160, B 40, K 18, R 11, C 6, G 9, N 3, S 12, D 3), with SOME conditions matched exactly | 262/262; every miss is explained in section 12 |
| M2 | reading sets: count, the choices enumerated per case, cases whose verdict is SOME, native `readings` verdicts | 11 sets plus N1 and N2; at most 32 choices per case; native UNKNOWN on every norm set |
| M3 | span accounting: `bytes_by_status` (CHECKED, OPEN, LABELLED, UNFORMALISED) and `bytes_by_kind`, both totalling 54,373 (100%); reasons for unformalised bytes; the residual (open terms with deciders, assumptions, bridges, narrowings, unresolved reading sets) | **CHECKED under 10% of bytes, probably under 5%**: closure sentences, severity classes and dates. Commitments are OPEN, because their guards carry OT1. A lower number is the honest outcome. |
| M4 | structure-conditional answers: items answered with a certificate or a validated witness per choice, although their units are OPEN | reported per family |
| M5 | CHECKED-bar lint (P7): one-off identifiers; rules per source bullet | 0; each of F9, F10 and F11 is one rule |
| M6 | invention audit: every default, permission, threshold, order and causal link in the translation is traced to a source span or listed as a forced choice | 0 untraced |
| M7 | default sensitivity: items whose completed outcome differs between the "need not" and "must" defaults | exactly the silent items of A, B, K and G |
| M8 | evidence: certificates replayed in Python and Lean, witnesses validated, UNKNOWNs named | reported |
| M9 | seeded mutants (section 11) detected | 6/6 |
| M10 | cost: units, rules, choices, prover calls, wall time | reported |

## 11. Seeded mutants (each must change exactly the named results)

| Id | Mutation | Expected change |
|---|---|---|
| m1 | remove F3's precedence over F2 (keep RS7 = E) | C2 becomes SOME(E): CONFLICT under E. The CCA item of every LRX case stays SOME(M) as a requirement, but under E it is now CONFLICT instead of REL |
| m2 | add "the recommended security level for the CBRN uplift TCL is Security level 2+" (an invented threshold) | N2 becomes satisfiable at L1; B-L1 RECSEC becomes SOME(Ds); M6 flags the untraced fact |
| m3 | add an order SL2+ < SL3 < SL4 | S4 becomes ALL; M6 flags it |
| m4 | add a cyber TCL constant | N1 becomes satisfiable; M6 flags it |
| m5 | turn F8 into a permission ("may proceed") | C5 becomes CONFLICT under U; M6 flags the invented permission |
| m6 | delete "This is required only for external deployment, not internal deployment or further development" from F9 | A-L*k*-DEV, -INT and -HRI for *k* = 1…4: DM becomes SOME(G) (was NONE with REL). C3 and its share of C-doc disappear |

## 12. Deviations (after running VE; empty at plan time)

Each entry gives the section and cell, the old value, the new value and the reason. No answer-key cell was changed;
the six disagreements with the key are findings and are listed in [README.md](README.md).

1. **Section 7, vocabulary.** Old: one obligation `meet(proposal, requirement)` with requirement constants. New: one
   obligation per act, such as `residual_assessed` with the act phrase "be subject to a residual risk assessment",
   and `applied(proposal, measure)` for security levels. Reason: VE writes a constant in a rule as a quoted
   identifier, while an act phrase reads as plain English. Rules still quantify over proposals, levels and measures.
2. **Section 7, level facts.** Old: `misuse(domain)`. New: `misuse(level)` and `ml_rd_and_misalignment(level)`;
   `concerns(level, domain)` stays for the closure sentences. Reason: VE's English guards nest at most three
   lists deep, and the domain detour cost one level in the classification rules.
3. **M5, rules per bullet.** Old: one rule each for F9, F10 and F11. New: one classification rule per bullet, plus
   one rule per gated condition (DM, SEC) and one per release. Reason: each sub-bullet has its own scope sentence.
   No rule is per level.
4. **Section 4.1, premises.** Added, each cited to its sentence: no TCL is a CCL (Glossary), the activity
   definitions (Glossary; "further development or deployment", 1.3.5), and the bridge that no level belongs to two
   of the four domains (1.3.1, support `assumption`). The bridge is stated as six exclusions, because VE's prover
   found no certificate from the equality form.
5. **Section 5, conflicts.** Old: the W1 conflict check. New: the W1 check against the premises. A CONFLICT needs a
   witness situation that satisfies every premise; CONFLICT-FREE needs certificates from the premises. Reason: W1
   checks all base structures, including a proposal that is both internal and external. The plain W1 status is
   recorded too; it is UNKNOWN for F9 against F10 under G, rel and RS9 different.
6. **Section 5, GOV.** The plan did not say how "GOV required" is decided. New: with the governance determination
   removed from the case, some rule forbids proceeding.
7. **Section 5, unset open terms.** An unset finding is false in the case model: the decider has made no such
   finding. A soft exception is found exactly where a sufficient condition that the text states holds.
8. **K4.** No regulated act has a checkpoint slot, so VE answers K4 from the vocabulary; F5 itself selects.
9. **S4.** Asked in D1, not D2: it is about security levels. D1 has the word `at_least_as_strong` and no premise
   uses it. **S1** is a transcription check: the classes are inputs read from the text, which the risk route admits.
10. **D2 and D3.** D2 counts unexamined cells as possible. RS10 is a reading set of D3 only. The countermodel for
    the "unstated" reading dates a last review on 2026-06-01, which the text does not state.
11. **Section 7, routed units.** A unit checked in D2 or D3 is LABELLED in D1 and CHECKED in the master map.
12. **Section 3.1, placement.** RS1 and RS8 sit on three bullets, and RS2 and RS3 on two sections. Each has one
    reading set per unit in the document, and the harness makes one choice for all of them.
13. **O2.** Every norm reading set in the document has pending content, so VE's native `readings` query is UNKNOWN,
    as expected. The ALL, SOME and NONE results come from the harness's expansion of choices.
14. **Restated rules.** F7's safety case appears four times and F14 twice. Each rule is carried once; a
    restatement is OPEN or LABELLED with a note.
15. **Mutants.** m4 adds a level that is tracked and concerns cyber: the premises become inconsistent, with a
    certificate, rather than N1 becoming satisfiable. m6 deletes the whole sentence, so DM is no longer limited to
    external deployment. The twelve DM items change as expected. C3 does not disappear: the conflict moves to
    further development of a model at both a misuse level and an ML R&D CCL (F10's release against the unscoped DM).
16. **Without N1.** The prediction reading is computed on eight representative items, not on all items.
17. **Probes P1 to P7.** P1 to P6 passed. P2: the norm reading sets load, and every choice is admitted by
    `SoftNormDocument`. P3: the risk route admits a record with only `might` statements. P7 found no violation.
18. **Build.** The first `lake build` logged a failure at `VE.English.Run:c.o`; a second run built it and finished.
19. **Section 13, files.** The D2 and D3 environments are built by `severity_and_dates.py` instead of committed
    `environment.d2.json` and `environment.d3.json` files. The rules and premises of D1 are `rules.d1.ve` and
    `facts.d1.ve`; `fsf.d1.ve.md` is built locally by `build_document.py`. The results are in `README.md` and
    `results.json`, so there is no `RESULTS.md`. `cases.json` and `answer-key.json` were transcribed in their own commit.

## 13. Files for the implementation round (not this commit)

`environment.d1.json`, `environment.d2.json`, `environment.d3.json`; `fsf.d1.ve.md`, `fsf.d2.ve.md`,
`fsf.d3.ve.md` (generated with the source prose from the pinned PDF, never committed with the full text);
`spans.json` (byte spans, unit ids and statuses only); `cases.json` and `answer-key.json` (transcribed from
section 6 in a separate commit that changes no key); `reference.py`; `run.py`; `coverage.json`; `README.md` and
`RESULTS.md`.
