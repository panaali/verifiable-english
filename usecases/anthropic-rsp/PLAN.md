# Use case: anthropic-rsp (Anthropic Responsible Scaling Policy, version 3.4)

> Status: **PLAN, draft 1** (2026-10-28, branch `infra/usecase-safetyfw`). The plan and its answer key (section 6)
> are written before any VE run. They get two plan reviews (gpt-6-astra xhigh and Opus xhigh) before the key is
> frozen; the freeze is recorded in [KEY-FREEZE.md](KEY-FREEZE.md) with a timestamp and the SHA-256 of section 6.
> After the freeze no answer-key cell changes; section 12 records every deviation.

This use case follows the method of [safety-framework](../safety-framework/PLAN.md) (Google DeepMind FSF 3.1). It
translates someone else's text, so it runs in **translation mode** ([VISION.md](../../VISION.md) 3,
[document.md](../../docs/spec/document.md)):

- every admissible reading is kept as a reading set, and no translator may collapse one;
- every vague term is a named open term with its decider;
- no default, permission, threshold, ordering or causal link is added that the text does not state;
- every byte of the source is accounted for.

It measures two things: whether VE answers four questions about a published frontier-lab safety policy the same
way as a key derived from the text by hand (section 6), and how much of the text VE can check at all (section 10).

**Conflict of interest.** This is the policy of the company that makes the model writing this plan. Three checks
stand against that: every key cell cites its source sentence; the plan review includes a reviewer from another
company (gpt-6-astra); and the implementation round's `reference.py` recomputes families A, B, C and G from
sections 3 and 4 alone.

## 1. Source (pinned)

| Field | Value |
|---|---|
| Document | Anthropic, *Responsible Scaling Policy*, **Version 3.4**, "Effective July 8, 2026" (21 pages) |
| URL | `https://www-cdn.anthropic.com/files/4zrzovbb/website/0bacdc8440ea96e62a8766d99ebe1d4eea6d5f3a.pdf` (the page's "current version" link, `https://cdn.sanity.io/files/4zrzovbb/website/0bacdc8440ea96e62a8766d99ebe1d4eea6d5f3a.pdf`, serves the same bytes) |
| Retrieved | 2026-10-28, 17:34 UTC, with `curl` |
| PDF SHA-256 | `6247b9e4001fd342827526fabc476c9d4dd6b2041ac00055f0ccda26f4d0b07d` (304,755 bytes). The same file was pinned as a candidate on 2026-10-01 ([safety-framework PLAN](../safety-framework/PLAN.md) 1). |
| Extracted text | [`source/extract_text.py`](source/extract_text.py) with `pypdf==6.19.0`: one line per page, whitespace collapsed. 59,410 bytes, 21 lines, SHA-256 `c7de7fe2f1f44cdd650efb327ecd798f1140034cf6328eb2e494de587c2c3063`. Two runs gave identical bytes. |
| Currency check | `https://www.anthropic.com/responsible-scaling-policy` (fetched 2026-10-28 17:34 UTC) lists "Version 3.4 ... (effective July 8, 2026)" first in its version list, and its "current version of the RSP" link is this PDF. The PDF's own changelog ends at v3.4. |
| Licence | None stated: neither the text nor the PDF metadata names a licence or terms of reuse. |
| Stored copy | `~/code/manage-agents/pilots/anthropic-rsp/source/` (the PDF, the extracted text and the policy page). It is **not** committed here, because no licence is stated. This repository keeps the hashes, the extractor, short quotations and byte spans only. |

Quotations below are from the extracted text after Unicode NFKC normalisation (the PDF sets "fi" as the ligature
"ﬁ"). Each was checked to occur in it. "p. n" is the PDF page.

**Why this text.** It is the lead's request (2026-10-28) and the second frontier-lab framework next to DeepMind's.
Its shape differs from the FSF in ways the four questions probe:

- **Recommendations kept apart from commitments.** Section 1's table pairs four capability thresholds with the
  company's plans (middle column) and "ambitious industry-wide recommendations" (right column), which "we cannot
  unilaterally and unconditionally commit to staying in line with" (p. 4). Footnote 3 says the middle column
  "should be read as an overview, not as indicating any separate or additional plans" (p. 6).
- **Few if-then deployment rules.** Most commitments concern Risk Reports, external review and governance. The
  only rules that make the company delay development or deployment are the competitor-contingent scenarios of
  Appendix A.
- **A quantified threshold.** The Automated R&D threshold is defined by a cost factor ("within a factor of 5") and a
  rate ("double the rate of progress", footnote 8).
- **Dated process steps.** "every 3-6 months", "no more than 30 days prior", "Within 30 days", "within one week",
  "within 30 days of receipt".

## 2. Scope

**In scope.** Every byte of the pinned text is accounted for (section 10, M3). The questions concern:

- the four named thresholds of section 1 and the "no threshold reached" case;
- the company column and the industry-wide recommendation column of each row;
- the Risk Report regime (scope, timing, off-cycle analyses, contents, procedures, redactions, external review);
- the governance measures of section 4 and the competitor commitments of Appendix A;
- the Automated R&D threshold's own definition, the stated harm classes and the dates.

**Out of scope, with reasons.**

- **Whether any model has reached any threshold.** That is an open term (OT1), decided by the company; the cases
  stipulate it.
- **The content of external references:** the ASL-3 protections (named, not specified in v3.4), the Frontier
  Safety Roadmap, the initial Risk Report, the Constitution, the Usage Policy, RAND SL4, California SB 53. Each is a
  pointer, so each unit that names one is OPEN or LABELLED.
- **Earlier versions.** The changelog describes v1.0 to v3.3. Its sentences are history (narrowing N2), not rules
  of v3.4.
- **Event order inside a process** beyond the stated day counts ("promptly", "prior to", "Following approval").
  "Within N days" and "no more than N days prior" are dates (family D).

## 3. Translation rules applied

### 3.1 Reading sets (written before the translation; none is collapsed)

Each set is cited to its source unit. The harness evaluates every complete choice of the sets in a case's cone
(section 9). N1 and N2 are the only narrowings; each cites source units, is listed in the residual, and section 9
reports what changes without it.

| Id | Source unit | Readings | Why the text admits each |
|---|---|---|---|
| RS0 | every "we will …" about the company's own process | **commitment** / **prediction** | "Will" is not a deontic word. |
| N1 | narrowing of RS0 to **commitment** | cites the Introduction "Frontier Safety Roadmaps are a new requirement under our RSP" and "Risk Reports are another new requirement", and section 4 "We commit to the following governance measures" | The text calls its process sentences requirements and commitments. A "will" sentence that also carries "aim", "strive", "intend", "try to", "work toward", "usually", "expect", "may", "as needed" or "as appropriate" is not narrowed; it stays RS0 or becomes an aim unit (O4). Under N1 a commitment is strict (`must`). |
| N2 | narrowing: the Changelog's entries for v1.0 to v3.3 are **history**, with no force in v3.4 | cites "This update is a comprehensive rewrite of our RSP" (v3.0 entry) and the Introduction "Our previous RSP committed to implementing mitigations that would reduce our models' absolute risk levels to acceptable levels, without regard to whether other frontier AI developers would do the same" | The v2.0 entry says the update maintained "our commitment not to train or deploy models unless we have implemented adequate safeguards". Read as standing, it would be a stop rule that v3.4 states nowhere else. Section 9 reports what changes without N2. The v3.4 entry is read as an explanation of this version (LABELLED explanation), not as rules. |
| RS1 | the middle column of the section 1 table ("Mitigations—our plan as a company"), each row | **cond**: the row's plans are commitments conditioned on the row's threshold / **uncond**: the plans hold whatever threshold is reached; the row only says which risk they address / **overview**: the column states no rule of its own (footnote 3) | The table "maps capability thresholds to the mitigations we believe they call for" (Introduction) supports cond. The plans are worded as present undertakings ("We will maintain or improve on our ASL-3 protections"), which supports uncond. Footnote 3: "It should be read as an overview, not as indicating any separate or additional plans." |
| RS2 | the right column ("Mitigations—ambitious industry-wide recommendations"): "A frontier developer should make a strong argument that …" | **F**: a recommendation to the field, no norm on the company / **Dd**: "should" read distributively, so it also binds the company as a frontier developer, as a **default** rule | The addressee is "a frontier developer". The strict force of the soft-norms rule is excluded by p. 4: "we cannot unilaterally and unconditionally commit to staying in line with the industry-wide recommendations in the right column". |
| RS3 | the Automated R&D row: "We will consider this threshold to be met if we determine that either (1) … or (2) …"; "We would consider scenario (2) to have occurred where (a) … and (b) …" | **suff**: sufficient conditions only / **iff**: the stated conditions are also necessary | "If" and "where" state sufficient conditions; a definition is often read as complete. |
| RS4 | Appendix A, "General upleveling": "However, we will not necessarily delay AI development and deployment in this scenario." | **scope**: no rule; A3 itself creates no duty to delay / **rel**: a "need not" rule (no duty to delay in this scenario) | "Not necessarily" can deny a duty (scope) or grant a release. |
| RS5 | Appendix A, "Competitors have strong safety measures": "all competitors who have developed, or will soon develop, a highly capable frontier model are able to make strong arguments …" | **import**: the scenario needs at least one such competitor / **noimport**: the universal holds vacuously when there is none | English "all" does not fix existential import. |
| RS6 | 3.6.1: "a reviewing organization itself may not have a financial interest in Anthropic; and the individuals … may not have a financial interest in Anthropic or close personal relationships …" | **P**: a prohibition / **M**: "may not" in the sense of "might not", no norm | In translation "may" is ambiguous ([norms.md](../../docs/spec/norms.md) 2), as in safety-framework RS7. |
| RS7 | 3.4 step 3: "The CEO and RSO will make the ultimate determination regarding the adequacy of the risk assessment and any downstream deployment or development plans." | **exec**: the executives' determination, a step of the process / **final**: no approval beyond the CEO and RSO is needed (a "need not" rule) | "Ultimate" can mean final or highest within the process. Step 5 is titled "Modified process when marginal risk analysis is important" and says "rather than just the CEO and RSO", so under both readings step 5 is an exception to step 3. |
| RS8 | 3.2: "We should make a strong attempt to ensure that ongoing (as opposed to temporary) changes do not significantly increase the level of risk." | **strict** / **default** | The [soft-norms.md](../../docs/spec/soft-norms.md) 2.2 rule for "should". |
| RS9 | 3.1 Timing: "We will publish a Risk Report every 3-6 months." | **window**: each interval between consecutive reports is at least 3 and at most 6 months / **bound**: each interval is at most 6 months | "every 3-6 months" may state a range or only its upper end. |
| RS10 | Appendix A, "Anthropic in the lead" and "Competitors have strong safety measures": "We will delay AI development and deployment as needed to achieve this" | **as-needed**: the duty to delay holds only when the open term "needed" (OT7) holds / — | One reading only; listed so that OT7's role is explicit. Not a set; no choice is enumerated. |

### 3.2 Open terms (each with its decider; none gets invented criteria)

Each has the W2 schema (`name`, `arguments`, `decided_by`, `necessary`, `sufficient`, `factors`, `precedents`,
`jurisdiction`, `version`). Factors are copied from the text's "such as", "e.g." and "for example" lists and give no
premise. `we` means Anthropic as the text uses the word.

| Id | Term | Decided by (from the text) | Factors or definitions stated |
|---|---|---|---|
| OT1 | the model has crossed threshold Tk | `we` (3.3 "whether we believe we've crossed relevant thresholds"; for T4 "if we determine") | the row's description; T4: section 3.1 conditions (family T) |
| OT2 | "significantly more capable than … all models for which we have publicly analyzed risks" (off-cycle, bullet 1) | `we` ("that we determine") | "e.g., in a prior Risk Report, System Card, or other public artifact" |
| OT3 | "could pose risks related to high-stakes misalignment or automated R&D that … significantly exceed those posed by models covered by a prior Risk Report" (in-scope internal models; off-cycle bullet 2 compares with all publicly analyzed models) | `we` ("we have determined") | at a minimum, "internal models that we are deploying for large-scale, fully autonomous research" (a sufficient condition, not a factor) |
| OT4 | "significantly redacted" | any of `RSO`, `CEO`, `Board`, `LTBT` ("in the judgment of the RSO, CEO, Board, or LTBT") | "the redactions omit information a reasonable external safety researcher would consider important …" |
| OT5 | "highly capable" | `we` ("if we conclude that it crosses the threshold for automated AI R&D") | defined by OT1 for T4 |
| OT6 | a "strong argument" / "strong case" that risk is contained | `unstated` (p. 5 suggests third parties "determine which such arguments are adequate") | the right column's "This will likely require" lists |
| OT7 | delay "as needed" | `we` | none |
| OT8 | "clear evidence" / "strong evidence" about competitors | `we` ("use our best judgment") | none |
| OT9 | "a significant lead" | `we` ("we no longer believe") | none |
| OT10 | a substantiated report "involves a material safety risk" | `we` ("If we determine") | none |
| OT11 | "noteworthy" changes and deviations | `unstated` | none |
| OT12 | "promptly"; "regularly"; "On approximately an annual basis" | `unstated` | none |
| OT13 | "ASL-3 protections" | external reference | "which include classifier guards at least as robust as our initial Constitutional Classifiers; access controls …" (factors) |
| OT14 | T3's "highly relied on", "extensive access to sensitive assets", "moderate capacity for autonomous, goal-directed operation and subterfuge" | `unstated` | none |
| OT15 | T4 (1): "fully substitute for our entire set of Research Scientists and Research Engineers" | `we` | "at competitive costs (i.e., within a factor of 5)": the factor is quantified (family T) |
| OT16 | T4 (2)(a): "double the rate of progress … compared to both the rate we'd expect and the fastest rate of extended progress … we've observed" (the footnote numbers 8 and 9 sit inside the sentence) | `we` ("we observe or expect") | footnote 8 (definition and example), footnote 9 ("Over at least three model generations") |
| OT17 | T4 (2)(b): "plausible that this doubling is substantially attributable to the automation of research and/or engineering" | `we` | "as opposed to other … factors, such as increased headcount, compute, or general productivity" (the table's columns interleave here) |
| OT18 | "the absolute level of risk being imposed industry-wide … is high"; the decision is justified "partly on a marginal risk analysis" | `we` ("If we determine") | footnote 11 defines "marginal risk analysis" |
| OT19 | marginal risk analysis "plays a major role in a decision to move forward" | `unstated` | none |
| OT20 | "appropriate and proportional corrective action" | `unstated` | none |
| OT21 | the industry-wide threshold rows' harm descriptions (T1 "significantly help", T2 "functionally substitute for the scarce human expertise") | `unstated` | footnotes 4 to 7 (examples) |

### 3.3 What the translation must not add

- **No completion default is trusted.** Every query runs under both defaults ("need not" and "must"), and only
  selection-based verdicts are scored (as in [agent-policy](../agent-policy/PLAN.md) 5). A verdict that depends on
  the default is a gap.
- **No stop rule the text does not state.** v3.4 states no rule that forbids training or deployment when a
  threshold is crossed and the company's plans are not met. The only duties to delay are Appendix A's, under their
  scenario conditions. N2 keeps the v2.0 changelog sentence from becoming one.
- **No order between thresholds.** No threshold implies another; reaching T2 is not reaching T1. "Catastrophic" is
  the only harm word for T1 to T3, and T4 states none (family S).
- **No causal link stated as certain.** "could result in", "could cause", "may serve", "will likely require",
  "significantly more likely" become `causal` units (LABELLED) or `might` cells, never `leads to`.
- **No closure of examples.** "such as", "e.g.", "for example", "include but are not limited to" lists are factors;
  none is a premise.

## 4. The text as rules (the inventory the key and the translation both use)

### 4.1 Named thresholds

| Id | Threshold, verbatim name (section 1 table) | Kind | Harm stated (family S) |
|---|---|---|---|
| T1 | "Non-novel chemical/biological weapons production" | capability | "serious potential for catastrophic damages" |
| T2 | "Novel chemical/biological weapons production" | capability | "potential for catastrophic harm"; footnote 4: "comparable to or worse than those of COVID-19" |
| T3 | "Misaligned AI systems in high-stakes settings" | capability or usage | "irreversibly and substantially higher odds of a later global catastrophe" |
| T4 | "Automated R&D in key domains" | capability; defined for AI R&D by (1) or (2) | "threats to international security and/or rapid disruptions to the global balance of power" (no harm class word) |

T0 is "no threshold crossed". The column header is "Capability or usage threshold". **Closure:** the text states
no closure ("at a minimum, include those discussed above", 3.3 item 2), so no case may infer that a risk outside
T1 to T4 has no threshold. **Definition link:** "This capability threshold is intended to reflect our definition of
highly capable models (see Section 3.6)" and 3.6 "A model is 'highly capable' if we conclude that it crosses the
threshold for automated AI R&D described in Section 1."

### 4.2 Commitments

| Id | Source | Content (the reading sets that apply) |
|---|---|---|
| F1 | 1, T1 middle | maintain or improve on the ASL-3 protections; maintain equally or more robust measures over time; publish updates in Risk Reports. (RS1, OT13) |
| F2 | 1, T2 middle | apply protections at least as strong as ASL-3 to an expanded set of use cases; identify the most concerning threat pathways, create policy recommendations, share them with policymakers. (RS1) |
| F3 | 1, T3 middle | detail capabilities, propensities, monitoring practices and overall risk in Risk Reports. (RS1) |
| F4 | 1, T4 middle | five bullets: moonshot R&D for security; "eyes on everything"; systematic alignment assessments; internal red-teaming better than the bug bounty participants; publish Risk Reports "subject to external review by at least one expert, experienced, credible, candid and disinterested external party". (RS1) |
| F5 | 1, right column, rows T1 to T4 | "A frontier developer should make a strong argument that …" (OT6). (RS2) |
| F6 | 2 | maintain a Frontier Safety Roadmap; share it with all full-time employees, the Board and the LTBT; publish it in redacted form; provide updates on whether goals are achieved; set new goals when they are. (RS0/N1) The goals are "not hard commitments" (Introduction). |
| F7 | 3, 3.1 Timing | publish Risk Reports, every 3-6 months. (RS0/N1, RS9) |
| F8 | 3.1 Scope | a Risk Report covers in-scope models: all publicly deployed models as of the coverage date, and internal models determined under OT3, including at a minimum those deployed "for large-scale, fully autonomous research"; the coverage date is "no more than 30 days prior to the publication of the report". Voluntary inclusion "does not expand the commitments below". |
| F9 | 3.1 Off-cycle | an off-cycle analysis (bullet 1) when publicly deploying a model determined under OT2 (no deadline stated); (bullet 2) "Within 30 days of determining" an internal model under OT3 relative to all publicly analyzed models. |
| F10 | 3.2 | keep future practices in line with described mitigations "or track and report noteworthy changes and deviations" (OT11); acknowledge significant absolute risk; "We should make a strong attempt …" (RS8). "We intend" is an aim. |
| F11 | 3.3 | the factual, risk-analysis and review contents, for each in-scope model; the marginal-risk analyses when OT18 holds. |
| F12 | 3.4 | steps 1 to 4: drafting by internal experts; comprehensive internal feedback; approval by the CEO and RSO, who make the "ultimate determination" (RS7); prompt sharing with the Board and LTBT. Step 5: explicit Board and LTBT approval when marginal risk analysis plays a major role (OT19); an exception to step 3. |
| F13 | 3.5 | publish a public version; disclose the existence of each redaction; "aim" to minimise redactions and to justify them (aims). |
| F14 | 3.6 | a full external review with at least one external reviewer whenever a Risk Report covers highly capable models (OT5) and is significantly redacted (OT4); an external review upon the LTBT's request. "We will work toward a practice of seeking comprehensive, public external review" is an aim. |
| F15 | 3.6.1 | select reviewers meeting three criteria (the third with RS6); consult the Board and obtain the LTBT's approval. |
| F16 | 3.6.2 | share the report with reviewers within one week of submitting it to the Board and LTBT; ask for public commentary within 30 days of receipt; every section shared with at least one reviewer; only legally necessary redactions. "We will try to work toward" earlier review is an aim. |
| F17 | 3.6.3 | the contents of the external review, and the public written report (the reviewer's acts; the company commits only to "ask"). |
| F18 | 4.1 | maintain the RSO position, with six duties. |
| F19 | 4.2, 4.3 | brief the LTBT regularly (OT12); share unredacted Risk Reports with at least 200 employees and minimally-redacted ones with all regular-clearance staff. |
| F20 | 4.4 | a noncompliance reporting process with more than one recipient option; promptly investigate; corrective action if substantiated (OT20); document; quarterly Board updates; prompt Board notice if substantiated and a material safety risk (OT10), public notice permitted ("we may"); protection from retaliation; a Board member among the recipients when the report concerns the RSO. |
| F21 | 4.5 | no non-disparagement obligations that impede raising safety concerns; such clauses do not preclude raising concerns or disclosing the clause. |
| F22 | 4.6, 4.7 | regular internal review (OT12); a third-party procedural compliance review "On approximately an annual basis". |
| F23 | 4.8 | changes proposed by the CEO and RSO, approved by the Board in consultation with the LTBT; the updated version published "prior to or on … its effective date"; differences recorded in the Change Log; the current version kept on the website. |
| F24 | App. A, "Anthropic in the lead" | if the company has or will imminently develop a highly capable model (OT5) and has clear evidence no competitor will soon (OT8): require a strong argument that catastrophic risk is contained (OT6); delay development and deployment as needed (OT7), until it no longer believes it has a significant lead (OT9). |
| F25 | App. A, "Competitors have strong safety measures" | if strong evidence (OT8) that all competitors who have or will soon develop a highly capable model can make strong arguments (RS5): meet or exceed their overall risk reduction posture; delay as needed until able. |
| F26 | App. A, "General upleveling" | if strong evidence that a competitor's mitigation (1) is a significant improvement and (2) is implementable at comparable or lower effort or cost: make a significant effort to meet or exceed it; "we will not necessarily delay" (RS4). |
| F27 | 3.6 definitions | "highly capable" (OT5) and "significantly redacted" (OT4). |
| F28 | 1, T4 row | the threshold is met if (1) or (2); (2) occurs where (a) and (b) (RS3, OT15 to OT17). |

Everything else (the Introduction's rationale, beliefs, expectations, hopes, examples, footnotes that explain,
the changelog under N2, page furniture) is accounted for as LABELLED or UNFORMALISED units, with reasons
(section 10, M3).

## 5. Questions and cases (exact list)

The brief's four questions map to the families:

- "What does each threshold require": family A (per threshold), with B (Risk Report scope), K (process triggers)
  and T (when the Automated R&D threshold is met).
- "Do any two commitments conflict": family C.
- "Which thresholds or situations no rule covers": family G, plus the NONE cells of A and K.
- "Which commitments can never apply": family N.
- Families S and D cover severity, causation, quantities and dates.

**Verdicts** are those of [safety-framework PLAN](../safety-framework/PLAN.md) 5: **ALL** (holds under every
complete choice of the reading sets that bear on the item, with N1 and N2 applied), **SOME(c)** (exactly under the
choices satisfying c; c is scored), **NONE**. "R is required" means some rule's obligation selects at the case's
situation under both completion defaults; a default rule counts when it selects with no exception finding, and the
results say which requirements are only soft ("soft"). **REL** is a "need not" rule that selects. **CONFLICT** is
the W1 conflict check on the document of that choice; a strict rule that blocks a default rule on the same act is
not a conflict.

**Case facts.** The model has crossed exactly the thresholds named (T0: none) and no others; every open term not
named by the case is unset; the company is the frontier developer the right column addresses (relevant only
under RS2 = Dd).

| Family | Cases | Scored items |
|---|---|---|
| A: what each threshold requires | A-T0 … A-T4: 5 cases | 8 atoms each (PROT1 … PROT4, ARG1 … ARG4): 40 |
| B: Risk Report scope | B-PUB, B-INT, B-INTD, B-AUT, B-VOL, B-TRN | 2 atoms each (INSCOPE, ASSESS): 12 |
| K: process triggers | K1 … K22 | 27 |
| T: the Automated R&D threshold | T1 … T6 | 8 |
| C: conflicts | C1 … C6, C-doc | 7 |
| G: gaps | G1 … G8 | 8 |
| N: never applies | N1 … N5 | 5 |
| S: severity and causation | S1-T1 … S1-T4, S2 … S5 | 8 |
| D: dates | D1 … D7 | 9 |
| **Total** | | **124** |

## 6. Answer key (written before any VE run)

Notation: cond, uncond, ov: RS1; F, Dd: RS2; suff, iff: RS3; scope, rel: RS4; import, noimport: RS5; P, M: RS6;
exec, final: RS7; window, bound: RS9. PROTk is "the row k plans of the middle column are required"; ARGk is "the
company is required to make the row k strong argument".

### 6.1 Family A (40 items)

| Case | PROTk (own row) | PROTj (other rows) | ARGk (own row) | ARGj (other rows) | Justification |
|---|---|---|---|---|---|
| A-T0 | — | SOME(uncond), each j | — | NONE, each j | Only under uncond do the middle-column plans hold with no threshold crossed. The right column is stated "at each threshold". |
| A-Tk, k = 1 … 4 | SOME(cond ∨ uncond) | SOME(uncond), each j ≠ k | SOME(Dd), soft | NONE, each j ≠ k | Under ov the column states no rule (footnote 3), and no other section of v3.4 restates the row plans as rules (F3's and F4's Risk Report sentences are covered by family B and K, not by PROTk). Under Dd the strong-argument "should" is a default rule; a strict reading is excluded (RS2). No threshold implies another (3.3). |

Totals: SOME 24, NONE 16. Under RS0 "prediction" (without N1) nothing is required anywhere; that is reported, not
scored.

### 6.2 Family B (12 items)

| Case | Situation | INSCOPE (F8) | ASSESS (F11 "with respect to each in-scope model") | Justification |
|---|---|---|---|---|
| B-PUB | publicly deployed as of the coverage date | ALL | ALL | "all publicly deployed models as of the coverage date" |
| B-INT | internally deployed; no OT3 determination; not used for large-scale autonomous research | NONE | NONE | the internal criterion needs the determination |
| B-INTD | internally deployed; OT3 determined by publication | ALL | ALL | F8 |
| B-AUT | internally deployed for large-scale, fully autonomous research; OT3 unset | ALL | ALL | "this will—at a minimum—include any internal models that we are deploying for large-scale, fully autonomous research" |
| B-VOL | not deployed publicly, OT3 unset; voluntarily included | NONE | NONE | "such inclusion does not expand the commitments below" |
| B-TRN | in training, not deployed | NONE | NONE | no criterion names it (gap G2) |

### 6.3 Family K (27 items)

| Case | Situation | Item | Key | Justification |
|---|---|---|---|---|
| K1 | any time | publishing Risk Reports required | ALL | F7 |
| K2 | public deployment of a model determined (OT2) significantly more capable than all publicly analyzed models | off-cycle analysis required | ALL | F9 bullet 1 |
| K3 | the same deployment, OT2 unset | off-cycle analysis required | NONE | the determination is the trigger |
| K4 | internal model determined under OT3 against all publicly analyzed models | off-cycle analysis required | ALL | F9 bullet 2 (deadline: D4) |
| K5 | OT18 holds (risk high, decision partly on marginal risk) | the four marginal-risk analyses required | ALL | F11 |
| K6 | marginal risk analysis plays a major role in a decision to move forward (OT19) | explicit Board and LTBT approval required | ALL | F12 step 5 |
| K7 | a Risk Report is approved | sharing decisions, report and internal feedback with the Board and LTBT required | ALL | F12 step 4 |
| K8 | a report covers a highly capable model and is significantly redacted | full external review required | ALL | F14 |
| K9 | covers a highly capable model; not significantly redacted | full external review required | NONE | F14 needs both; "work toward a practice" is an aim |
| K10 | significantly redacted; no highly capable model | full external review required | NONE | as K9 |
| K11 | the LTBT requests a review | conducting a public or private external review required | ALL | F14 |
| K12a | selecting external reviewers | the LTBT's approval required | ALL | F15 |
| K12b | the same | consulting the Board required | ALL | F15 |
| K13 | a candidate reviewing organisation has a financial interest in Anthropic | selecting it forbidden | SOME(P) | F15 with RS6. Under M only the third criterion "Do not have conflicts of interest" remains, and whether a financial interest is one is not stated. |
| K14 | a Risk Report is submitted to the Board and LTBT under the external review process | sharing it with the reviewers within one week required | ALL | F16 (dates: D5) |
| K15a | a noncompliance report is substantiated and involves a material safety risk (OT10) | prompt Board notification required | ALL | F20 |
| K15b | the same | public notice required | NONE | "we may provide public notice" |
| K16 | a report concerns the RSO's conduct | a Board member among the recipients required | ALL | F20 |
| K17 | the RSP is updated | publishing it on or before its effective date and recording the differences in the Change Log required | ALL | F23 |
| K18 | a Risk Report described a mitigation; later practice deviates from it | tracking and reporting the deviation required | ALL | F10: the disjunction's first branch fails, so the second is required |
| K19a | Appendix A "in the lead" scenario (OT5, OT8 found) | a strong argument required | ALL | F24 |
| K19b | the same, and delay found needed (OT7) | delaying development and deployment required | ALL | F24 |
| K20 | "Competitors have strong safety measures" (OT8 found), with at least one such competitor | meeting or exceeding their posture required | ALL | F25 (under both RS5 readings, since a competitor exists) |
| K21a | "General upleveling" scenario | a significant effort to meet or exceed required | ALL | F26 |
| K21b | the same | delay required | NONE | "we will not necessarily delay" |
| K22a | a Roadmap goal is missed | the next Risk Report addressing it required | ALL | F11, review item 3 ("any cases where we failed to meet our goals") |
| K22b | the same | any other consequence (delay, pause) required | NONE | the goals are "not hard commitments" |

### 6.4 Family T: the Automated R&D threshold (8 items)

| Case | Situation | Item | Key | Justification |
|---|---|---|---|---|
| T1 | determined: the models can fully substitute for all Research Scientists and Research Engineers at 4× their cost | T4 met | ALL | (1), with 4 ≤ 5 |
| T2a | the same at 6× the cost; (2) found not to hold | T4 met | NONE | (1) fails on the factor; (2) fails |
| T2b | the same | T4 not met | SOME(iff) | only a complete definition concludes "not met" |
| T3 | (2)(a) observed and (2)(b) found plausible | T4 met | ALL | (2) |
| T4a | (2)(a) observed; (2)(b) found not plausible; (1) found not to hold | T4 met | NONE | neither (1) nor (2) |
| T4b | the same | T4 not met | SOME(iff) | as T2b |
| T5 | substitution at 4.5× cost | "at competitive costs" | ALL | "(i.e., within a factor of 5)" |
| T6 | the rate of progress equals the fastest rate observed without significant AI contribution; (1) unset | T4 met | NONE | (2)(a) needs double that rate (the v3.4 changelog explains the same outcome; under N2 it is not used as a rule) |

### 6.5 Family C: conflicts (7 items)

| Case | Rules | Key | Witness or reason |
|---|---|---|---|
| C1 | F24 (delay as needed) against F26 (not necessarily delay) | SOME(rel) | A highly capable model in the lead scenario, with delay needed (OT7), and the general-upleveling scenario at once. Under rel, F26's "need not delay" meets F24's "must delay" on the same act. Under scope, F26 states no rule. |
| C2 | F12 step 3 against step 5 | NONE | Under final, step 3 is a "need not" on further approval, but step 5 is its exception ("Modified process", "rather than just the CEO and RSO"). Under exec there is no "need not". Mutant m1 removes the precedence. |
| C3 | F1 ("equally or more robust measures over time") against F10 ("keep … in line … or track and report") | NONE | F10 is a disjunction that F1's compliance satisfies; neither permits weakening. |
| C4 | F13 (public redactions "include but are not limited to" four reasons) against F16 ("the only redactions" for external review are legal) | NONE | different versions of the report |
| C5 | F24 against F25 in the lead scenario | NONE | Under import, F25's scenario fails (no competitor). Under noimport, F25's condition holds vacuously and its posture comparison is over no competitors (N3). |
| C6 | F19 (unredacted to at least 200 employees) against F13 ("aim to minimize redactions" for the regular-clearance version) | NONE | different versions; F13's sentence is an aim |
| C-doc | the whole document, per choice | SOME(rel) | exactly C1; otherwise CONFLICT-FREE |

### 6.6 Family G: gaps (8 items)

"Silent" means no rule selects under the stated readings, so the answer depends on the completion default only.

| Case | Situation | Key | Justification |
|---|---|---|---|
| G1 | T2 crossed; the row's plans not in place; no Appendix A scenario holds | silent on development and deployment: ALL (no rule forbids either) | Under cond and uncond the plans are required, but nothing makes proceeding depend on them (3.3). |
| G2 | a model in training, not deployed | silent on Risk Reports and analyses: ALL | F8 and F9 name deployed models only |
| G3 | a catastrophic risk outside T1 to T4 (e.g., a cyber capability) | silent on thresholds: ALL; covered by F11's threat-model identification only | no closure (4.1) |
| G4 | the off-cycle analysis for a public deployment (K2) | silent on its deadline: ALL | bullet 1 has no "within"; bullet 2 has "Within 30 days" |
| G5 | an external reviewer gives no commentary within 30 days | silent on consequences: ALL | the company commits only to "ask" |
| G6 | a full review is required (K8) and the LTBT approves no candidate reviewer | silent on what follows: ALL | F14 and F15 cannot both be met; no rule says which yields |
| G7 | a substantiated noncompliance report without a material safety risk | prompt Board notice required: NONE; covered by the quarterly update: ALL (one item, keyed "covered by quarterly update only") | F20 |
| G8 | a Roadmap goal revised in a less ambitious direction because it was not achieved | silent: ALL (no rule forbids it) | "we will strive to avoid" is an aim |

### 6.7 Family N: never applies (5 items)

| Case | Question | Key | Justification |
|---|---|---|---|
| N1 | Can F11's assessments be required for a model that is only voluntarily included? | never: ALL | "with respect to each in-scope model"; voluntary inclusion "does not expand the commitments below" |
| N2 | Can F26 ever require a delay? | never: ALL | "we will not necessarily delay" under both RS4 readings |
| N3 | In the lead scenario, does F25 add any requirement? | never: ALL | import: the scenario fails; noimport: the comparison set is empty |
| N4 | Is any commitment F1 to F28 dead (an unsatisfiable guard)? | no: NONE dead; a witness model for each | every guard is satisfiable over the declared vocabulary |
| N5 | Can any changelog sentence for v1.0 to v3.3 select as a rule? | never: ALL (under N2) | N2; section 9 reports what selects without it |

### 6.8 Family S: severity and causation (8 items)

| Case | Question | Key | Justification |
|---|---|---|---|
| S1-T1 … S1-T3 | the harm word stated for the threshold | catastrophic (T1 "catastrophic damages", T2 "catastrophic harm", T3 "global catastrophe") | 4.1 |
| S1-T4 | the same for T4 | none stated (no class; VE must not assign one) | the row names "threats to international security and/or rapid disruptions to the global balance of power" |
| S2 | Is T2's harm ranked above T1's? | NONE (no order; countermodels both ways) | the text states no order (3.3) |
| S3 | Might a T1-capable system without the row's protections make catastrophic harm more likely? | ALL (a stated `might` cell) | "with serious potential for catastrophic damages" |
| S4 | Does it *lead to* catastrophic harm? | NONE | only potential is stated |
| S5 | Is an existential threat a catastrophic risk in the RSP's sense? | NONE (an example in footnote 1's "such as" list gives no premise) | 3.3, no closure of examples; the footnote's term is "in its plain meaning" |

### 6.9 Family D: dates (9 items)

| Case | Question | Key | Justification |
|---|---|---|---|
| D1 | Are the changelog dates increasing in version order: 2023-09-19, 2024-10-15, 2025-03-31, 2025-05-14, 2026-02-24, 2026-04-02, 2026-04-29, 2026-05-26, 2026-07-08? | ALL | Changelog |
| D2 | Was v3.4 effective before the retrieval date 2026-10-28? | ALL | that v3.4 is current is an observation leaf (LABELLED) |
| D3a | coverage date 2026-05-20, publication 2026-07-01: does the coverage date comply? | NONE (42 days > 30) | F8 |
| D3b | coverage date 2026-06-10, publication 2026-07-01 | ALL (21 days) | F8 |
| D4 | an OT3 determination on 2026-08-03: is the off-cycle analysis due no later than 2026-09-02? | ALL | "Within 30 days" |
| D5 | submitted to the Board and LTBT on 2026-09-01: must the reviewers have it by 2026-09-08? | ALL | "within one week" (7 days, a bridge) |
| D6a | Risk Reports published 2026-03-01 and next on 2026-10-01: is the cadence met? | NONE (7 months) | RS9, both readings |
| D6b | published 2026-03-01 and next on 2026-04-15 | SOME(bound) | under window the interval is under 3 months |
| D7 | Is the procedural compliance review due by a fixed date? | NONE (no date certifiable: "approximately") | OT12 |

**Independent check of the key.** In the implementation round, `reference.py` (stdlib only, no `ve` import) is
written from sections 3 and 4 alone and recomputes families A, B, C and G. A disagreement is resolved in a
separate commit that says why, never inside a results commit.

## 7. Planned VE translation

**Documents.** As in safety-framework 7, three `ve-document@1` documents over disjoint byte ranges, unless a probe
shows that main now composes the profiles (record the result either way):

| Doc | Environment profiles | Carries | Questions |
|---|---|---|---|
| D1 | `norms@0`, `soft-norms@0` (base profiles fixed by probe P1; add `judgments@0` only if probe P8 admits it with them) | F1 to F28, the threshold vocabulary, open terms, reading sets | A, B, K, C, G, N |
| D2 | `norms@0`, `alternatives@0`, `risk@0` | the harm words and `might` cells; `causal` units | S |
| D3 | `ve-units@1` (`documents@1`, `order@0`, `relational-fol@0`, `time@0`) | changelog dates, the day counts of F8, F9, F16, the cadence of F7, the cost factor of T5 | D, T5 |

Family T's T1 to T4 and T6 are rules over open-term findings in D1, with the factor check of T1, T2 and T5
routed to D3.

**Shared structure (the CHECKED bar).** As safety-framework 7: rules quantify over `threshold`, `model`,
`report`, `proposal`, `requirement`; thresholds are constants with the source's own labels; one source bullet
gives one rule; no identifier packs a threshold, number or condition into its name (probe P7 lints it).

**Vocabulary sketch.** Sorts `threshold`, `model`, `report`, `reviewer`, `proposal`, `requirement`, `day`.
Facts: `crossed(model, threshold)`, `publicly_deployed(model, day)`, `internally_deployed(model, day)`,
`autonomous_research_use(model)`, `in_scope(model, report)`, `covers(report, model)`, `approved(report)`,
`submitted_to_board(report, day)`. Regulated: `meet(subject, requirement)`, `delay(proposal)`,
`select_reviewer(reviewer)`. Open-term predicates, one per OT.

**Feature map** (the feature families of `reviews/feature-plan-20261018.md` in manage-agents: JT judgments, DF
defaults, SC scope, QT quantities, ET time, AP acts, WG weighing, AT attitudes).

| Part | VE feature | Family |
|---|---|---|
| F6 to F28 rule blocks, exceptions (F12 step 5), "need not" (RS4, RS7) | `norms@0` | merged |
| RS2 Dd, RS8, the aims | `soft-norms@0` | merged; aims are AT |
| OT1 to OT21 | W2 open terms; `judgments@0` (jt-2, jt-2b) if P8 admits it | JT |
| RS0 to RS9, N1, N2 | W2 reading sets, per-choice harness expansion | merged |
| RS5 (existential import), "all", "each in-scope model" | quantifier scope | SC |
| day counts, cadence, "within a factor of 5", footnote 8's "81×" | W6a; `ve-units@1` | QT, ET |
| "promptly", "regularly", "On approximately an annual basis", "prior to or on … its effective date" | event order and deadlines | ET |
| "delay AI development and deployment", "make a significant effort", "share … with policymakers" | act phrases | AP |
| "meet or exceed the overall risk reduction posture of these competitors", "risks … justified by corresponding benefits" | comparison and weighing | WG |
| "We believe", "We expect", "We hope", "We intend", "we aim", "we will strive" | attitudes | AT |
| "ordinarily", "generally", "usually" | defaults | DF |

## 8. What is expected to stay OPEN

- **O1: every open term OT1 to OT21.** Whether a threshold is crossed is never a VE result.
- **O2: norm reading sets.** Per-choice answers come from the harness's expansion and are labelled so; VE's own
  readings query decides only sets whose readings are each one rule (as fsf-r1 found).
- **O3: causal and degree language** ("significantly more likely", "could result in", "dramatically accelerate").
- **O4: beliefs, expectations, hopes, aims, intent.** Most of the Introduction, section 1's framing and 3.2.
- **O5: examples and factor lists.** Footnotes 4 to 9 and the "include" lists.
- **O6: external references:** ASL-3 protections, the Roadmap, the Constitution, the Usage Policy, RAND SL4, SB 53.
- **O7: event order** ("promptly", "Following approval", "prior to Board/LTBT review").
- **O8: feature combination.** D2 cannot share an environment with D1, so no question needs both.
- **O9: "a year" and "a month".** "every 3-6 months" and "On approximately an annual basis" have no calendar unit in W6a; D6
  uses explicit day counts as a bridge (a month as the calendar month of the dates given).
- **O10: who "we" is.** Anthropic is labelled, never identified with the RSO, CEO, Board or LTBT.

Expected CHECKED share: **under 10%**, probably under 5%: the dates, the factor arithmetic, and the few
commitments whose guards have no open term (K1, K7, K12, K16, K17).

## 9. Run protocol (implementation round)

**Stage 0 probes.**

| Probe | Input | Expected |
|---|---|---|
| P1 | D1 environment with `norms@0` + `soft-norms@0`, an obligation with an open-term predicate in its guard | admitted; the rule is OPEN |
| P2 | a norm reading set (RS1) and `ve document readings` | per fsf-r1: a set whose readings are each one rule is decided by VE; a set with a no-rule reading (RS1 ov, RS4 scope) stays pending |
| P3 | D2: a risk environment with assertion units only (`catastrophic`, `might` cells) | admitted, or S3 and S4 move to D1 as plain facts (a deviation) |
| P4 | D3: the changelog dates and the D family day counts | admitted, with certificates |
| P5 | D1 partition over the 59,410-byte text, `MIXED` units | `bytes_by_status` totals 59,410 |
| P6 | routed placeholders against the D2 and D3 spans | equal byte ranges; the master map is total and disjoint |
| P7 | the identifier lint | 0 violations |
| P8 | D1 with `judgments@0` added | record admitted or refused (jt-2c, the composing modes, is not merged) |

**Per case.** As safety-framework 9: build the facts from section 5 without reading the key; for every complete
choice in the case's cone, check the premises are consistent; compute selections, conflicts or entailments under
both completion defaults; combine into ALL, SOME(c) or NONE; a search that runs out of budget is UNKNOWN and a miss.
Report, unscored, what changes without N1 and without N2.

## 10. Metrics to report

| # | Metric | Expected |
|---|---|---|
| M1 | key agreement per family (A 40, B 12, K 27, T 8, C 7, G 8, N 5, S 8, D 9) | 124/124; every miss explained in section 12 |
| M2 | reading sets: count, choices per case, SOME verdicts, VE's own readings verdicts | RS1 to RS9 (RS1 has three readings) plus N1 and N2; at most 3 · 2 = 6 choices per family A case; C-doc enumerates the sets that bear on a conflict candidate (RS1, RS4, RS5, RS7: 24 choices) |
| M3 | span accounting: `bytes_by_status` (CHECKED, OPEN, LABELLED, UNFORMALISED) and `bytes_by_kind`, totalling 59,410; the reason for each unformalised unit; the residual; for each unit that is not CHECKED, the feature family it waits for (section 7) | CHECKED under 10% |
| M4 | structure-conditional answers per family | reported |
| M5 | CHECKED-bar lint (P7) | 0 |
| M6 | invention audit: every default, permission, threshold, order and causal link traced to a span | 0 untraced |
| M7 | default sensitivity | exactly the silent items |
| M8 | evidence: certificates replayed, witnesses validated, UNKNOWNs named | reported |
| M9 | seeded mutants (section 11) detected | 6/6 |
| M10 | cost: units, rules, choices, prover calls, wall time | reported |

## 11. Seeded mutants (each must change exactly the named results)

| Id | Mutation | Expected change |
|---|---|---|
| m1 | remove step 5's precedence over step 3 (keep RS7 = final) | C2 becomes SOME(final); C-doc adds it |
| m2 | add "a model that crosses T1 crosses T4" (an invented implication) | A-T1 PROT4 becomes SOME(cond ∨ uncond), A-T1 ARG4 SOME(Dd); M6 flags it |
| m3 | replace F26's "we will not necessarily delay" with "we will delay as needed" | N2 fails; C1 and C-doc become NONE; K21b becomes ALL given OT7 |
| m4 | add a cyber threshold row T5 with a middle-column plan | G3 changes (a threshold covers cyber); M6 flags it |
| m5 | drop "(i.e., within a factor of 5)" | T5 becomes NONE (an open term without its factor); T1 becomes OPEN on the cost |
| m6 | change "Within 30 days" (F9 bullet 2) to "Within 60 days" | D4 becomes NONE |

## 12. Deviations (after running VE; empty at plan time)

## 13. Files for the implementation round (not this commit)

`environment.d1.json`, `environment.d2.json`, `environment.d3.json`; `rsp.d1.ve.md`, `rsp.d2.ve.md`, `rsp.d3.ve.md`
(generated with the source prose from the pinned PDF, never committed with the full text); `spans.json` (byte
spans, unit ids, statuses and feature families only); `cases.json` and `answer-key.json` (transcribed from section
6 in a separate commit that changes no key); `reference.py`; `run.py`; `coverage.json`; `README.md`.
